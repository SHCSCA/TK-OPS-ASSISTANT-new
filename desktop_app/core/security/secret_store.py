from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportMissingTypeStubs=false

"""Secure credential storage abstractions and platform adapters."""

import base64
import hashlib
import json
import os
import platform
import threading
import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List, Mapping, Optional, Protocol, Tuple, cast, runtime_checkable

_keyring: Any = None
_keyring_errors: Any = None
_fernet_cls: Any = None
_invalid_token_cls: Any = Exception
_hashes_module: Any = None
_pbkdf2hmac_cls: Any = None

try:
    import keyring as _keyring
    import keyring.errors as _keyring_errors
except ImportError:  # pragma: no cover - optional dependency
    pass

try:
    from cryptography.fernet import Fernet as _fernet_cls
    from cryptography.fernet import InvalidToken as _invalid_token_cls
    from cryptography.hazmat.primitives import hashes as _hashes_module
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as _pbkdf2hmac_cls
except ImportError:  # pragma: no cover - optional dependency
    pass


_CryptoTuple = Tuple[Any, Any, Any]

class SecretStoreError(RuntimeError):
    """Base error raised for secret store failures."""


class SecretStoreCorruptedError(SecretStoreError):
    """Raised when persisted secret data is corrupted or undecryptable."""


@runtime_checkable
class SecretStore(Protocol):
    """Protocol for secure credential storage."""

    def get(self, service: str, key: str) -> Optional[str]:
        ...

    def set(self, service: str, key: str, value: str) -> None:
        ...

    def delete(self, service: str, key: str) -> bool:
        ...

    def has(self, service: str, key: str) -> bool:
        ...

    def list_keys(self, service: str) -> List[str]:
        ...


def _default_state_dir() -> Path:
    """Return the application data directory used by secret stores."""

    if os.name == "nt":
        base_dir = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    else:
        base_dir = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base_dir / "tk-ops"


def _machine_seed() -> bytes:
    """Build a deterministic machine-local seed for key derivation."""

    parts = [
        os.environ.get("COMPUTERNAME", ""),
        platform.node(),
        platform.system(),
        platform.machine(),
        str(uuid.getnode()),
        str(Path.home()),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).digest()


def _write_json_atomic(path: Path, payload: Mapping[str, object]) -> None:
    """Write JSON atomically to avoid torn writes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Optional[Path] = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as handle:
            temp_path = Path(handle.name)
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temp_path), str(path))
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def _backup_corrupted_file(path: Path) -> None:
    """Move a corrupted file out of the way if possible."""

    if not path.exists():
        return
    backup_path = path.with_suffix(path.suffix + ".corrupt")
    try:
        os.replace(str(path), str(backup_path))
    except OSError:
        pass


def _require_keyring() -> Any:
    if _keyring is None:
        raise RuntimeError("keyring is not installed")
    return _keyring


def _keyring_error_types() -> Tuple[type, ...]:
    if _keyring_errors is None:
        return (Exception,)

    keyring_error = getattr(_keyring_errors, "KeyringError", Exception)
    delete_error = getattr(_keyring_errors, "PasswordDeleteError", keyring_error)
    return cast(Tuple[type, ...], (delete_error, keyring_error))


def _is_keyring_error(exc: Exception) -> bool:
    return isinstance(exc, _keyring_error_types())


def _require_crypto() -> _CryptoTuple:
    if _fernet_cls is None or _pbkdf2hmac_cls is None or _hashes_module is None:
        raise RuntimeError("cryptography is required for encrypted file secret storage")
    return _fernet_cls, _pbkdf2hmac_cls, _hashes_module


class _MetadataIndex:
    """Thread-safe metadata sidecar for secret key discovery."""

    def __init__(self, path: Path, lock: threading.RLock) -> None:
        self._path = path
        self._lock = lock

    def list_keys(self, service: str) -> List[str]:
        with self._lock:
            metadata = self._load_metadata()
            return list(metadata.get(service, []))

    def add(self, service: str, key: str) -> None:
        with self._lock:
            metadata = self._load_metadata()
            keys = set(metadata.get(service, []))
            keys.add(key)
            metadata[service] = sorted(keys)
            self._save_metadata(metadata)

    def remove(self, service: str, key: str) -> None:
        with self._lock:
            metadata = self._load_metadata()
            keys = set(metadata.get(service, []))
            if key not in keys:
                return
            keys.remove(key)
            if keys:
                metadata[service] = sorted(keys)
            else:
                metadata.pop(service, None)
            self._save_metadata(metadata)

    def replace(self, metadata: Dict[str, List[str]]) -> None:
        with self._lock:
            sanitized: Dict[str, List[str]] = {}
            for service, keys in metadata.items():
                if not service:
                    continue
                unique_keys = sorted({key for key in keys if key})
                if unique_keys:
                    sanitized[service] = unique_keys
            self._save_metadata(sanitized)

    def _load_metadata(self) -> Dict[str, List[str]]:
        if not self._path.exists():
            return {}
        try:
            raw_data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _backup_corrupted_file(self._path)
            return {}
        if not isinstance(raw_data, dict):
            _backup_corrupted_file(self._path)
            return {}

        metadata: Dict[str, List[str]] = {}
        for service, keys in raw_data.items():
            if not isinstance(service, str) or not isinstance(keys, list):
                continue
            metadata[service] = sorted(
                [key for key in keys if isinstance(key, str) and key]
            )
        return metadata

    def _save_metadata(self, metadata: Dict[str, List[str]]) -> None:
        payload = cast(Mapping[str, object], metadata)
        _write_json_atomic(self._path, payload)


class KeyringSecretStore:
    """OS keychain adapter using the keyring library."""

    SERVICE_PREFIX = "tk-ops"

    def __init__(self, metadata_path: Optional[Path] = None) -> None:
        keyring_module = _require_keyring()
        if not _is_keyring_available(keyring_module):
            raise RuntimeError("No usable keyring backend is available")

        self._keyring = keyring_module
        self._lock = threading.RLock()
        self._index = _MetadataIndex(
            metadata_path or (_default_state_dir() / "keyring-index.json"),
            self._lock,
        )

    def get(self, service: str, key: str) -> Optional[str]:
        """Return the stored secret for a service/key pair."""

        with self._lock:
            try:
                return self._keyring.get_password(self._service_name(service), key)
            except Exception as exc:
                if not _is_keyring_error(exc):
                    raise
                raise SecretStoreError(
                    "Failed to read secret from keyring for %r/%r" % (service, key)
                ) from exc

    def set(self, service: str, key: str, value: str) -> None:
        """Store a secret in the keyring backend."""

        with self._lock:
            try:
                self._keyring.set_password(self._service_name(service), key, value)
            except Exception as exc:
                if not _is_keyring_error(exc):
                    raise
                raise SecretStoreError(
                    "Failed to store secret in keyring for %r/%r" % (service, key)
                ) from exc
            self._index.add(service, key)

    def delete(self, service: str, key: str) -> bool:
        """Delete a secret from the keyring backend."""

        with self._lock:
            if self.get(service, key) is None:
                self._index.remove(service, key)
                return False
            try:
                self._keyring.delete_password(self._service_name(service), key)
            except Exception as exc:
                if not _is_keyring_error(exc):
                    raise
                raise SecretStoreError(
                    "Failed to delete secret from keyring for %r/%r" % (service, key)
                ) from exc
            self._index.remove(service, key)
            return True

    def has(self, service: str, key: str) -> bool:
        """Return whether a secret exists."""

        return self.get(service, key) is not None

    def list_keys(self, service: str) -> List[str]:
        """Return tracked keys for a service."""

        return self._index.list_keys(service)

    def get_secret(self, namespace: str, key: str) -> Optional[str]:
        """Backward-compatible alias for legacy callers."""

        return self.get(namespace, key)

    def set_secret(self, namespace: str, key: str, value: str) -> None:
        """Backward-compatible alias for legacy callers."""

        self.set(namespace, key, value)

    def delete_secret(self, namespace: str, key: str) -> None:
        """Backward-compatible alias for legacy callers."""

        self.delete(namespace, key)

    @classmethod
    def _service_name(cls, service: str) -> str:
        return "%s.%s" % (cls.SERVICE_PREFIX, service)


class EncryptedFileSecretStore:
    """Fallback encrypted JSON file store using Fernet."""

    def __init__(self, path: Path, master_key: Optional[bytes] = None) -> None:
        _require_crypto()
        self._path = path
        self._master_key = master_key
        self._lock = threading.RLock()
        self._index = _MetadataIndex(path.with_suffix(path.suffix + ".meta.json"), self._lock)

    def get(self, service: str, key: str) -> Optional[str]:
        """Return the stored secret for a service/key pair."""

        with self._lock:
            secrets = self._load_secrets()
            return secrets.get(service, {}).get(key)

    def set(self, service: str, key: str, value: str) -> None:
        """Store a secret in the encrypted file backend."""

        with self._lock:
            secrets = self._load_secrets()
            secrets.setdefault(service, {})[key] = value
            self._write_secrets(secrets)

    def delete(self, service: str, key: str) -> bool:
        """Delete a secret from the encrypted file backend."""

        with self._lock:
            secrets = self._load_secrets()
            service_secrets = secrets.get(service)
            if service_secrets is None or key not in service_secrets:
                self._index.remove(service, key)
                return False

            del service_secrets[key]
            if not service_secrets:
                secrets.pop(service, None)
            self._write_secrets(secrets)
            return True

    def has(self, service: str, key: str) -> bool:
        """Return whether a secret exists."""

        return self.get(service, key) is not None

    def list_keys(self, service: str) -> List[str]:
        """Return tracked keys for a service."""

        return self._index.list_keys(service)

    def get_secret(self, namespace: str, key: str) -> Optional[str]:
        """Backward-compatible alias for legacy callers."""

        return self.get(namespace, key)

    def set_secret(self, namespace: str, key: str, value: str) -> None:
        """Backward-compatible alias for legacy callers."""

        self.set(namespace, key, value)

    def delete_secret(self, namespace: str, key: str) -> None:
        """Backward-compatible alias for legacy callers."""

        self.delete(namespace, key)

    def _load_secrets(self) -> Dict[str, Dict[str, str]]:
        if not self._path.exists():
            return {}

        try:
            envelope = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SecretStoreCorruptedError(
                "Encrypted secret store is unreadable: %s" % self._path
            ) from exc
        if not isinstance(envelope, dict):
            raise SecretStoreCorruptedError("Encrypted secret store has invalid format")

        salt_value = envelope.get("salt")
        token_value = envelope.get("token")
        if not isinstance(salt_value, str):
            raise SecretStoreCorruptedError("Encrypted secret store is missing a valid salt")
        if token_value in (None, ""):
            return {}
        if not isinstance(token_value, str):
            raise SecretStoreCorruptedError("Encrypted secret store token is invalid")

        try:
            salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        except (ValueError, OSError) as exc:
            raise SecretStoreCorruptedError("Encrypted secret store salt cannot be decoded") from exc

        fernet = self._build_fernet(salt)
        try:
            payload = fernet.decrypt(token_value.encode("ascii"))
        except Exception as exc:
            if not isinstance(exc, _invalid_token_cls):
                raise
            raise SecretStoreCorruptedError(
                "Encrypted secret store could not be decrypted on this machine"
            ) from exc

        try:
            raw_data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SecretStoreCorruptedError("Encrypted secret store payload is corrupted") from exc

        return self._validate_secret_data(raw_data)

    def _write_secrets(self, secrets: Dict[str, Dict[str, str]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        salt = self._read_existing_salt() or os.urandom(16)
        fernet = self._build_fernet(salt)
        token = fernet.encrypt(
            json.dumps(secrets, ensure_ascii=False, sort_keys=True).encode("utf-8")
        )

        envelope = {
            "version": 1,
            "salt": base64.urlsafe_b64encode(salt).decode("ascii"),
            "token": token.decode("ascii"),
        }
        _write_json_atomic(self._path, cast(Mapping[str, object], envelope))

        metadata: Dict[str, List[str]] = {}
        for service, service_secrets in secrets.items():
            metadata[service] = sorted(service_secrets.keys())
        self._index.replace(metadata)

    def _read_existing_salt(self) -> Optional[bytes]:
        if not self._path.exists():
            return None
        try:
            envelope = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(envelope, dict):
            return None

        salt_value = envelope.get("salt")
        if not isinstance(salt_value, str):
            return None
        try:
            return base64.urlsafe_b64decode(salt_value.encode("ascii"))
        except (ValueError, OSError):
            return None

    def _build_fernet(self, salt: bytes):
        fernet_cls, pbkdf2_cls, hashes_module = _require_crypto()

        if self._master_key is not None:
            derived_key = self._normalize_master_key(self._master_key)
        else:
            kdf = cast(Any, pbkdf2_cls)(
                algorithm=cast(Any, hashes_module).SHA256(),
                length=32,
                salt=salt,
                iterations=390000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(_machine_seed()))
        return cast(Any, fernet_cls)(derived_key)

    @staticmethod
    def _normalize_master_key(master_key: bytes) -> bytes:
        try:
            decoded = base64.urlsafe_b64decode(master_key)
        except (ValueError, OSError):
            decoded = b""
        if len(decoded) == 32:
            return master_key
        return base64.urlsafe_b64encode(hashlib.sha256(master_key).digest())

    @staticmethod
    def _validate_secret_data(raw_data: object) -> Dict[str, Dict[str, str]]:
        if not isinstance(raw_data, dict):
            raise SecretStoreCorruptedError("Encrypted secret store payload is not a mapping")

        secrets: Dict[str, Dict[str, str]] = {}
        for service, service_values in raw_data.items():
            if not isinstance(service, str) or not isinstance(service_values, dict):
                raise SecretStoreCorruptedError(
                    "Encrypted secret store contains invalid service entries"
                )

            normalized_values: Dict[str, str] = {}
            for key, value in service_values.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise SecretStoreCorruptedError(
                        "Encrypted secret store contains non-string secrets"
                    )
                normalized_values[key] = value
            secrets[service] = normalized_values
        return secrets


class PlainFileSecretStore:
    """Last-resort JSON file store for environments without crypto support."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.RLock()

    def get(self, service: str, key: str) -> Optional[str]:
        with self._lock:
            secrets = self._load_secrets()
            return secrets.get(service, {}).get(key)

    def set(self, service: str, key: str, value: str) -> None:
        with self._lock:
            secrets = self._load_secrets()
            secrets.setdefault(service, {})[key] = value
            self._write_secrets(secrets)

    def delete(self, service: str, key: str) -> bool:
        with self._lock:
            secrets = self._load_secrets()
            service_secrets = secrets.get(service)
            if service_secrets is None or key not in service_secrets:
                return False
            del service_secrets[key]
            if not service_secrets:
                secrets.pop(service, None)
            self._write_secrets(secrets)
            return True

    def has(self, service: str, key: str) -> bool:
        return self.get(service, key) is not None

    def list_keys(self, service: str) -> List[str]:
        with self._lock:
            secrets = self._load_secrets()
            return sorted(secrets.get(service, {}).keys())

    def _load_secrets(self) -> Dict[str, Dict[str, str]]:
        if not self._path.exists():
            return {}
        try:
            raw_data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SecretStoreCorruptedError(
                "Plain secret store is unreadable: %s" % self._path
            ) from exc
        if not isinstance(raw_data, dict):
            raise SecretStoreCorruptedError("Plain secret store has invalid format")

        secrets: Dict[str, Dict[str, str]] = {}
        for service, service_values in raw_data.items():
            if not isinstance(service, str) or not isinstance(service_values, dict):
                raise SecretStoreCorruptedError("Plain secret store contains invalid entries")
            normalized_values: Dict[str, str] = {}
            for key, value in service_values.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise SecretStoreCorruptedError("Plain secret store contains non-string secrets")
                normalized_values[key] = value
            secrets[service] = normalized_values
        return secrets

    def _write_secrets(self, secrets: Dict[str, Dict[str, str]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(self._path, cast(Mapping[str, object], secrets))


def create_secret_store(prefer_keyring: bool = True) -> SecretStore:
    """Return a keyring-backed store when available, else encrypted file storage."""

    if prefer_keyring and _keyring is not None:
        try:
            return KeyringSecretStore()
        except RuntimeError:
            pass
    if _fernet_cls is not None and _pbkdf2hmac_cls is not None and _hashes_module is not None:
        return EncryptedFileSecretStore(_default_state_dir() / "secrets.json")
    return PlainFileSecretStore(_default_state_dir() / "secrets.json")


def _is_keyring_available(keyring_module: Any) -> bool:
    """Return whether the keyring backend appears usable."""

    try:
        backend = cast(Any, keyring_module).get_keyring()
    except Exception:
        return False

    priority = getattr(backend, "priority", 1)
    if priority is None:
        priority_ok = True
    elif isinstance(priority, (int, float)):
        priority_ok = priority > 0
    else:
        priority_ok = False

    backend_name = "%s.%s" % (backend.__class__.__module__, backend.__class__.__name__)
    return priority_ok and "fail" not in backend_name.lower()


__all__ = [
    "EncryptedFileSecretStore",
    "KeyringSecretStore",
    "PlainFileSecretStore",
    "SecretStore",
    "SecretStoreCorruptedError",
    "SecretStoreError",
    "create_secret_store",
]

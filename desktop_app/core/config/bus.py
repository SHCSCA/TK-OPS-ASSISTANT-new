from __future__ import annotations

# pyright: basic

"""Typed runtime configuration bus with persistence and change notifications."""

import importlib
import json
import threading
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Iterator, Mapping, TypeVar

from .. import signals as _signals_module
from ..signals import CoreSignalHub
from ..types import ConfigKey
from .migration import CURRENT_SCHEMA_VERSION, apply_migrations
from .schema import AppConfigSchema

T = TypeVar("T")
Signal = getattr(_signals_module, "Signal")


def _freeze_value(value: object) -> object:
    """Recursively freeze a value so snapshot consumers cannot mutate it."""

    if isinstance(value, dict):
        frozen_items = {str(key): _freeze_value(item) for key, item in value.items()}
        return MappingProxyType(frozen_items)
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze_value(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    return deepcopy(value)


def _default_config_path() -> Path:
    """Resolve the default config file path for the current platform."""

    try:
        platformdirs = importlib.import_module("platformdirs")
        user_config_dir = getattr(platformdirs, "user_config_dir", None)
        if callable(user_config_dir):
            return Path(str(user_config_dir(appname="TK-OPS", appauthor="TK-OPS"))) / "config.json"
    except Exception:
        pass

    try:
        qt_core = importlib.import_module("PySide6.QtCore")
        standard_paths = getattr(qt_core, "QStandardPaths", None)
        if standard_paths is not None:
            app_dir = standard_paths.writableLocation(standard_paths.AppConfigLocation)
            if isinstance(app_dir, str) and app_dir:
                return Path(app_dir) / "config.json"
    except Exception:
        pass

    return Path(__file__).resolve().parents[2] / "config.json"


def _signal_emit(signal_owner: object, signal_name: str, *args: object) -> None:
    """Safely emit a Qt signal when a runtime implementation is available."""

    signal = getattr(signal_owner, signal_name, None)
    emit = getattr(signal, "emit", None)
    if callable(emit):
        emit(*args)


def _invoke_callback(
    callback: Callable[..., object],
    key: str,
    old_value: object,
    new_value: object,
) -> None:
    """Invoke a key subscriber using a compatible positional signature."""

    try:
        from inspect import Parameter, signature

        params = list(signature(callback).parameters.values())
        if any(param.kind is Parameter.VAR_POSITIONAL for param in params):
            callback(key, old_value, new_value)
            return
        positional = [
            param
            for param in params
            if param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        ]
        argc = len(positional)
    except Exception:
        argc = 3

    if argc >= 3:
        callback(key, old_value, new_value)
    elif argc == 2:
        callback(old_value, new_value)
    elif argc == 1:
        callback(new_value)
    else:
        callback()


@dataclass(frozen=True)
class ConfigSnapshot:
    """Immutable snapshot of configuration values at a point in time."""

    schema_version: int
    values: Mapping[str, object]

    def get(self, key: ConfigKey, default: T | None = None) -> object | T | None:
        """Return a value from the frozen snapshot."""

        return self.values.get(str(key), default)

    def __getitem__(self, key: ConfigKey | str) -> object:
        """Access a snapshot value by typed or raw key."""

        return self.values[str(key)]

    def __iter__(self) -> Iterator[str]:
        """Iterate over snapshot keys."""

        return iter(self.values)


class ConfigBus(CoreSignalHub):
    """Thread-safe typed configuration bus with Qt notifications and JSON persistence."""

    value_changed: object = Signal(str, object, object)

    def __init__(
        self,
        schema: AppConfigSchema | None = None,
        path: Path | None = None,
        parent: object | None = None,
    ) -> None:
        """Create a config bus bound to a schema and optional persistence path."""

        super().__init__()
        self.schema: AppConfigSchema = schema or AppConfigSchema()
        self._path: Path = Path(path) if path is not None else _default_config_path()
        self._lock = threading.RLock()
        self._values: dict[str, object] = self.schema.defaults()
        self._subscribers: dict[str, set[Callable[..., object]]] = {}
        self.load()

    def get(self, key: ConfigKey, default: T | None = None) -> object | T | None:
        """Return the current config value for ``key`` or a suitable default."""

        with self._lock:
            if str(key) in self._values:
                return deepcopy(self._values[str(key)])

        field = self.schema.get_field(key)
        if field is not None:
            return field.copy_default()
        return deepcopy(default)

    def set(self, key: ConfigKey, value: object) -> None:
        """Store a config value, normalize it, and notify listeners if it changed."""

        normalized = self.schema.normalize_value(key, value)
        callbacks: tuple[Callable[..., object], ...] = ()
        with self._lock:
            raw_key = str(key)
            old_value = self._values.get(raw_key)
            if old_value == normalized:
                return
            self._values[raw_key] = normalized
            callbacks = tuple(self._subscribers.get(raw_key, ()))
        self._publish_change(raw_key, old_value, normalized, callbacks)

    def snapshot(self) -> ConfigSnapshot:
        """Return an immutable snapshot of the current config state."""

        with self._lock:
            frozen_values = MappingProxyType({key: _freeze_value(value) for key, value in self._values.items()})
        return ConfigSnapshot(CURRENT_SCHEMA_VERSION, frozen_values)

    def load(self, path: Path | None = None) -> None:
        """Load configuration from disk, applying migrations and schema normalization."""

        target_path = Path(path) if path is not None else self._path
        if not target_path.exists():
            self._replace_values(self.schema.defaults(), emit_changes=False)
            return

        try:
            payload_obj = json.loads(target_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._replace_values(self.schema.defaults(), emit_changes=False)
            return

        if not isinstance(payload_obj, dict):
            self._replace_values(self.schema.defaults(), emit_changes=False)
            return

        payload = {str(key): value for key, value in payload_obj.items()}
        raw_version = payload.get("schema_version", CURRENT_SCHEMA_VERSION)
        stored_version = int(raw_version) if isinstance(raw_version, (int, float, str)) else CURRENT_SCHEMA_VERSION

        raw_values_obj = payload.get("values")
        if isinstance(raw_values_obj, dict):
            raw_values = {str(key): value for key, value in raw_values_obj.items()}
        else:
            raw_values = {key: value for key, value in payload.items() if key != "schema_version"}

        try:
            migrated_values = apply_migrations(raw_values, stored_version)
            normalized_values = self.schema.normalize_payload(migrated_values)
        except Exception:
            normalized_values = self.schema.defaults()

        self._replace_values(normalized_values, emit_changes=True)

    def save(self, path: Path | None = None) -> None:
        """Persist the current configuration to a JSON file on disk."""

        target_path = Path(path) if path is not None else self._path
        with self._lock:
            serialized_values = self.schema.serialize_payload(self._values)

        payload = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "values": serialized_values,
        }
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def reset_to_defaults(self) -> None:
        """Restore all config values to their schema defaults."""

        self._replace_values(self.schema.defaults(), emit_changes=True)

    def subscribe(self, key: ConfigKey, callback: Callable[..., object]) -> None:
        """Register a key-specific listener invoked only when ``key`` changes."""

        with self._lock:
            self._subscribers.setdefault(str(key), set()).add(callback)

    def unsubscribe(self, key: ConfigKey, callback: Callable[..., object]) -> None:
        """Remove a previously registered key-specific listener."""

        with self._lock:
            listeners = self._subscribers.get(str(key))
            if listeners is None:
                return
            listeners.discard(callback)
            if not listeners:
                self._subscribers.pop(str(key), None)

    def _replace_values(self, new_values: dict[str, object], emit_changes: bool) -> None:
        """Swap the in-memory config state and optionally publish diffs."""

        changes: list[tuple[str, object | None, object | None, tuple[Callable[..., object], ...]]] = []
        with self._lock:
            old_values = self._values
            merged_values = dict(new_values)
            if emit_changes:
                for key in sorted(set(old_values) | set(merged_values)):
                    old_value = old_values.get(key)
                    new_value = merged_values.get(key)
                    if old_value != new_value:
                        callbacks = tuple(self._subscribers.get(key, ()))
                        changes.append((key, old_value, new_value, callbacks))
            self._values = merged_values

        if emit_changes:
            for key, old_value, new_value, callbacks in changes:
                self._publish_change(key, old_value, new_value, callbacks)

    def _publish_change(
        self,
        key: str,
        old_value: object | None,
        new_value: object | None,
        callbacks: tuple[Callable[..., object], ...],
    ) -> None:
        """Emit shared signals and invoke key-specific callbacks for one change."""

        _signal_emit(self, "value_changed", key, old_value, new_value)
        _signal_emit(self, "config_value_changed", key, new_value)
        if key == "theme.mode" and new_value is not None:
            theme_value = getattr(new_value, "value", new_value)
            _signal_emit(self, "theme_mode_changed", str(theme_value))

        for callback in callbacks:
            _invoke_callback(callback, key, old_value, new_value)


__all__ = ["ConfigBus", "ConfigSnapshot"]

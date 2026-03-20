"""License codec — issue and verify HMAC-SHA256-signed license keys.

License payload (before signing)::

    {machine_id_hex}|{expiry_iso}|{tier}

The signed key is base64url-encoded and formatted as groups of 5 chars
separated by dashes for readability, e.g.::

    A3bCd-E5fGh-J8kLm-N0pQr-S2tUv-W4xYz-...

Verification steps:
  1. Decode the key → extract payload + signature
  2. Recompute HMAC over the payload with the embedded secret
  3. Compare signatures (constant-time)
  4. Check machine_id matches local fingerprint
  5. Check expiry has not passed
"""
from __future__ import annotations

import base64
import datetime as _dt
import hmac
import hashlib
import json
import logging
import re

log = logging.getLogger(__name__)

_GROUP_SEPARATOR = ":"

# ── IMPORTANT ──
# Ship this secret inside a compiled .pyd / Cython module for production.
_SECRET = bytes.fromhex(
    "2367ce93ef1bdb87110c2c05c8b0a496"
    "836eddb26cf9ec63318655cf29d5c074"
)

# License tiers: free, pro, enterprise
VALID_TIERS = ("free", "pro", "enterprise")

# Minimum component matches for drift tolerance (compound IDs only)
_DRIFT_THRESHOLD = 3


# ---------------------------------------------------------------------------
# Compound-ID helpers (drift tolerance)
# ---------------------------------------------------------------------------

def _is_compound_id(mid: str) -> bool:
    """Return True if *mid* is a compound ID (4 × 16-hex parts joined by ':')."""
    parts = mid.split(":")
    return len(parts) == 4 and all(len(p) == 16 and all(c in "0123456789abcdef" for c in p) for p in parts)


def _match_machine_id(license_mid: str, local_mid: str) -> bool:
    """Match machine IDs.  Compound IDs allow 3-of-4 component drift."""
    if license_mid == local_mid:
        return True
    if _is_compound_id(license_mid) and _is_compound_id(local_mid):
        lic_parts = license_mid.split(":")
        loc_parts = local_mid.split(":")
        matches = sum(1 for a, b in zip(lic_parts, loc_parts) if a == b)
        return matches >= _DRIFT_THRESHOLD
    return False


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    padded = s + "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(padded)


def _format_key(raw: str) -> str:
    """Chunk into groups of 5 using a separator outside base64url alphabet."""
    clean = raw.replace(_GROUP_SEPARATOR, "").replace(" ", "")
    return _GROUP_SEPARATOR.join(re.findall(r".{1,5}", clean))


def _unformat_key(key: str) -> str:
    return key.replace(_GROUP_SEPARATOR, "").replace(" ", "")


def _unformat_key_legacy(key: str) -> str:
    return key.replace("-", "").replace(" ", "")


# ---------------------------------------------------------------------------
# Issuing
# ---------------------------------------------------------------------------

def issue_license(
    machine_id: str,
    expiry: _dt.date | None = None,
    tier: str = "pro",
) -> str:
    """Create a signed license key for the given machine and expiry.

    Parameters
    ----------
    machine_id : str
        Full 64-char hex machine fingerprint.
    expiry : date, optional
        Expiration date.  ``None`` means permanent.
    tier : str
        One of ``VALID_TIERS``.

    Returns
    -------
    str
        Formatted license key string.
    """
    if tier not in VALID_TIERS:
        raise ValueError(f"Invalid tier: {tier!r}")

    expiry_str = expiry.isoformat() if expiry else "permanent"
    payload = f"{machine_id}|{expiry_str}|{tier}"
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).digest()

    token = _b64url_encode(payload.encode()) + "." + _b64url_encode(sig)
    return _format_key(token)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

class LicenseError(Exception):
    """Raised when license verification fails."""


class LicenseInfo:
    """Parsed & verified license metadata."""

    __slots__ = ("machine_id", "expiry", "tier")

    def __init__(self, machine_id: str, expiry: _dt.date | None, tier: str):
        self.machine_id = machine_id
        self.expiry = expiry
        self.tier = tier

    @property
    def is_permanent(self) -> bool:
        return self.expiry is None

    @property
    def is_expired(self) -> bool:
        if self.expiry is None:
            return False
        return _dt.date.today() > self.expiry

    @property
    def days_remaining(self) -> int | None:
        if self.expiry is None:
            return None
        return (self.expiry - _dt.date.today()).days

    def to_dict(self) -> dict:
        return {
            "machine_id": self.machine_id,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "tier": self.tier,
            "is_permanent": self.is_permanent,
            "is_expired": self.is_expired,
            "days_remaining": self.days_remaining,
        }


def verify_license(key: str, local_machine_id: str) -> LicenseInfo:
    """Verify a license key against the local machine fingerprint.

    Returns
    -------
    LicenseInfo
        Parsed license details on success.

    Raises
    ------
    LicenseError
        On any verification failure.
    """
    raw = _unformat_key(key)
    try:
        return _verify_license_raw(raw, local_machine_id)
    except LicenseError as exc:
        # Legacy keys used '-' as formatting separator, which collides with
        # the base64url alphabet. Keep a best-effort fallback for older keys.
        if _GROUP_SEPARATOR in key or "-" not in key:
            raise
        legacy_raw = _unformat_key_legacy(key)
        return _verify_license_raw(legacy_raw, local_machine_id)


def _verify_license_raw(raw: str, local_machine_id: str) -> LicenseInfo:
    """Verify an unformatted license token against the local machine."""

    # Split payload.signature
    if "." not in raw:
        raise LicenseError("格式无效")

    payload_b64, sig_b64 = raw.rsplit(".", 1)
    try:
        payload_bytes = _b64url_decode(payload_b64)
        sig_bytes = _b64url_decode(sig_b64)
    except Exception:
        raise LicenseError("解码失败")

    # Verify HMAC
    expected_sig = hmac.new(_SECRET, payload_bytes, hashlib.sha256).digest()
    if not hmac.compare_digest(sig_bytes, expected_sig):
        raise LicenseError("签名无效")

    # Parse payload
    payload = payload_bytes.decode("utf-8")
    parts = payload.split("|")
    if len(parts) != 3:
        raise LicenseError("载荷格式错误")

    machine_id, expiry_str, tier = parts

    # Machine match (with drift tolerance for compound IDs)
    if not _match_machine_id(machine_id, local_machine_id):
        raise LicenseError("机器码不匹配")

    # Expiry
    if expiry_str == "permanent":
        expiry = None
    else:
        try:
            expiry = _dt.date.fromisoformat(expiry_str)
        except ValueError:
            raise LicenseError("有效期格式错误")

    # Tier
    if tier not in VALID_TIERS:
        raise LicenseError(f"无效等级: {tier}")

    info = LicenseInfo(machine_id, expiry, tier)
    if info.is_expired:
        raise LicenseError("许可证已过期")

    return info

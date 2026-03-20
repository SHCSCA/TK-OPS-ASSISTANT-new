"""LicenseService — high-level API for activation / verification.

Wraps fingerprint collection, license_codec, and AppSetting persistence.
"""
from __future__ import annotations

import datetime as dt
import logging
import re
from typing import Optional

from desktop_app.database import get_session
from desktop_app.database.repository import Repository
from desktop_app.services.fingerprint import get_machine_id, get_machine_id_short, get_compound_id
from desktop_app.services.license_codec import (
    LicenseError,
    LicenseInfo,
    issue_license,
    verify_license,
    _is_compound_id,
)

log = logging.getLogger(__name__)

_SETTING_KEY = "license_key"
_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")

# Tier feature access: routes gated by tier
_FREE_ROUTES = frozenset([
    "dashboard", "account", "setup-wizard", "system-settings",
    "log-center", "version-upgrade", "network-diagnostics",
])
_ENTERPRISE_ONLY_ROUTES = frozenset([
    "license-issuer", "permission-management",
])


class LicenseService:
    """Stateless facade; reads/writes license from ``app_settings`` table."""

    # ── query ──

    def get_machine_id(self) -> str:
        """Full 64-char hex fingerprint."""
        return get_machine_id()

    def get_machine_id_display(self) -> str:
        """User-friendly ``XXXX-XXXX-XXXX-XXXX``."""
        return get_machine_id_short()

    def get_compound_id(self) -> str:
        """Compound machine ID for drift-tolerant licensing."""
        return get_compound_id()

    def get_stored_key(self) -> str:
        """Return the license key saved in DB, or empty string."""
        session = get_session()
        try:
            repo = Repository(session)
            return repo.get_setting(_SETTING_KEY)
        finally:
            session.close()

    def get_status(self) -> dict:
        """Return current license status as a JSON-serialisable dict.

        Keys: ``activated``, ``machine_id``, ``machine_id_short``,
              ``tier``, ``expiry``, ``days_remaining``, ``error``.
        """
        # Capture machine fingerprint early and log both full and short forms.
        try:
            mid = get_machine_id()
        except Exception as exc:  # Defensive: fingerprint collectors may fail on exotic systems
            log.exception("Failed to obtain full machine id")
            mid = ""

        try:
            short = get_machine_id_short()
        except Exception as exc:
            log.exception("Failed to obtain short machine id")
            short = ""

        log.debug("LicenseService.get_status: machine_id(full)=%s machine_id_short=%s", mid or '<empty>', short or '<empty>')

        result: dict = {
            "activated": False,
            "machine_id": mid,
            "machine_id_short": short,
            "compound_id": "",
            "tier": None,
            "expiry": None,
            "days_remaining": None,
            "is_permanent": False,
            "error": None,
        }

        try:
            result["compound_id"] = get_compound_id()
        except Exception:
            log.exception("Failed to get compound id")

        key = self.get_stored_key()
        if not key:
            result["error"] = "未激活"
            log.info("License status: no stored key; returning not-activated (machine_short=%s)", result.get("machine_id_short"))
            return result

        # Try compound_id first (drift-tolerant), fall back to legacy full hash
        cid = result.get("compound_id", "")
        try:
            info = verify_license(key, cid) if cid else None
        except LicenseError:
            info = None
        if info is None:
            try:
                info = verify_license(key, mid)
            except LicenseError as exc:
                log.warning("License verification failed: %s (machine_short=%s)", exc, result.get("machine_id_short"))
                result["error"] = str(exc)
                return result
        result["activated"] = True
        result["tier"] = info.tier
        result["expiry"] = info.expiry.isoformat() if info.expiry else None
        result["days_remaining"] = info.days_remaining
        result["is_permanent"] = info.is_permanent
        log.info("License verified: tier=%s expiry=%s machine_short=%s", info.tier, info.expiry, result.get("machine_id_short"))

        return result

    def issue(self, machine_id: str, days: int = 0, tier: str = "pro") -> dict:
        """Issue a license key for *machine_id* using the local signing secret."""
        normalized_machine_id = self._normalize_machine_id(machine_id)
        expiry = dt.date.today() + dt.timedelta(days=days) if days > 0 else None
        key = issue_license(normalized_machine_id, expiry=expiry, tier=tier)
        info = verify_license(key, normalized_machine_id)
        return {
            "ok": True,
            "license_key": key,
            "machine_id": normalized_machine_id,
            "tier": info.tier,
            "expiry": info.expiry.isoformat() if info.expiry else None,
            "days": days,
            "is_permanent": info.is_permanent,
        }

    def issue_compound(self, compound_id: str, days: int = 0, tier: str = "pro") -> dict:
        """Issue a license key for a compound machine ID (drift-tolerant)."""
        if not _is_compound_id(compound_id):
            raise LicenseError("无效的复合机器码格式")
        expiry = dt.date.today() + dt.timedelta(days=days) if days > 0 else None
        key = issue_license(compound_id, expiry=expiry, tier=tier)
        info = verify_license(key, compound_id)
        return {
            "ok": True,
            "license_key": key,
            "machine_id": compound_id,
            "tier": info.tier,
            "expiry": info.expiry.isoformat() if info.expiry else None,
            "days": days,
            "is_permanent": info.is_permanent,
        }

    def verify(self, key: str, machine_id: str) -> dict:
        """Verify a license key against an explicit machine id."""
        normalized_machine_id = self._normalize_machine_id(machine_id)
        info = verify_license(key, normalized_machine_id)
        return {"ok": True, "info": info.to_dict()}

    # ── mutation ──

    def activate(self, key: str) -> dict:
        """Verify *key* and persist it.  Returns the status dict."""
        mid = get_machine_id()
        cid = get_compound_id()
        # Try compound first for drift tolerance, fall back to legacy
        info = None
        for candidate in (cid, mid):
            try:
                info = verify_license(key, candidate)
                break
            except LicenseError:
                continue
        if info is None:
            return {"ok": False, "error": "激活失败：许可证无效或机器码不匹配"}

        session = get_session()
        try:
            repo = Repository(session)
            repo.set_setting(_SETTING_KEY, key)
        finally:
            session.close()

        log.info("License activated: tier=%s, expiry=%s", info.tier, info.expiry)
        return {"ok": True, "info": info.to_dict()}

    def deactivate(self) -> dict:
        """Remove the stored license key."""
        session = get_session()
        try:
            repo = Repository(session)
            repo.set_setting(_SETTING_KEY, "")
        finally:
            session.close()
        log.info("License deactivated")
        return {"ok": True}

    def _normalize_machine_id(self, machine_id: str) -> str:
        normalized = (machine_id or "").strip()
        # Allow compound IDs (4 parts of 16 hex separated by ':')
        if _is_compound_id(normalized):
            return normalized
        normalized = normalized.replace("-", "").replace(" ", "").lower()
        if not _HEX_64_RE.fullmatch(normalized):
            raise LicenseError("机器码必须是 64 位十六进制完整指纹或复合格式")
        return normalized

    # ── Tier access check ──

    def check_route_access(self, route: str) -> dict:
        """Check if the current license tier allows access to *route*."""
        if route in _FREE_ROUTES:
            return {"allowed": True, "required_tier": "free"}

        status = self.get_status()
        tier = status.get("tier") or "free"

        if route in _ENTERPRISE_ONLY_ROUTES:
            allowed = tier == "enterprise"
            return {"allowed": allowed, "required_tier": "enterprise", "current_tier": tier}

        # Everything else requires pro or higher
        allowed = tier in ("pro", "enterprise")
        return {"allowed": allowed, "required_tier": "pro", "current_tier": tier}

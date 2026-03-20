"""Machine fingerprint — stable hardware identifier for license binding.

Collects:
  1. CPU ID (via WMI on Windows, /proc/cpuinfo on Linux)
  2. Motherboard serial (WMI / dmidecode)
  3. Primary disk serial (WMI / lsblk)
  4. First non-loopback MAC address

All values are joined and hashed with SHA-256.
The full hash is 64 hex chars; we expose a short form (first 16 uppercase)
for user-friendly display: ``XXXX-XXXX-XXXX-XXXX``.
"""
from __future__ import annotations

import hashlib
import logging
import platform
import re
import subprocess
import uuid

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------

def _wmi_query(wmic_class: str, field: str) -> str:
    """Run a WMI query on Windows and return the first non-empty value."""
    try:
        out = subprocess.check_output(
            ["wmic", wmic_class, "get", field, "/value"],
            text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        for line in out.splitlines():
            if "=" in line:
                val = line.split("=", 1)[1].strip()
                if val:
                    return val
    except Exception as exc:
        log.debug("WMI query %s.%s failed: %s", wmic_class, field, exc)
    return ""


def _get_cpu_id() -> str:
    if platform.system() == "Windows":
        return _wmi_query("cpu", "ProcessorId")
    # Linux fallback
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Serial") or line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "unknown-cpu"


def _get_board_serial() -> str:
    if platform.system() == "Windows":
        return _wmi_query("baseboard", "SerialNumber")
    try:
        return subprocess.check_output(
            ["cat", "/sys/class/dmi/id/board_serial"],
            text=True, timeout=5,
        ).strip()
    except Exception:
        return ""


def _get_disk_serial() -> str:
    if platform.system() == "Windows":
        return _wmi_query("diskdrive", "SerialNumber")
    try:
        out = subprocess.check_output(
            ["lsblk", "-ndo", "SERIAL"],
            text=True, timeout=5,
        )
        for line in out.splitlines():
            s = line.strip()
            if s:
                return s
    except Exception:
        pass
    return ""


def _get_mac() -> str:
    """First non-loopback MAC address."""
    mac_int = uuid.getnode()
    # uuid.getnode may return a random MAC; detect that
    if (mac_int >> 40) % 2:
        return ""
    return ":".join(f"{(mac_int >> (8 * i)) & 0xFF:02x}" for i in range(5, -1, -1))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_SALT = "tk-ops-fingerprint-v1"

_COMPONENT_NAMES = ("cpu", "board", "disk", "mac")
_COLLECTORS = (_get_cpu_id, _get_board_serial, _get_disk_serial, _get_mac)


def get_component_fingerprints() -> dict[str, str]:
    """Return per-component 16-char hex fingerprints for drift-tolerant matching."""
    result: dict[str, str] = {}
    for name, fn in zip(_COMPONENT_NAMES, _COLLECTORS):
        val = fn()
        h = hashlib.sha256((_SALT + "|" + name + "|" + val).encode()).hexdigest()[:16]
        result[name] = h
    return result


def get_compound_id() -> str:
    """Return compound machine ID ``cpu16:board16:disk16:mac16`` for drift-tolerant licensing."""
    fps = get_component_fingerprints()
    return ":".join(fps[c] for c in _COMPONENT_NAMES)


def get_machine_id() -> str:
    """Return the full 64-char hex SHA-256 machine fingerprint."""
    parts = [
        _get_cpu_id(),
        _get_board_serial(),
        _get_disk_serial(),
        _get_mac(),
    ]
    raw = "|".join(parts)
    log.debug("Fingerprint raw components: %s", raw)
    digest = hashlib.sha256((_SALT + "|" + raw).encode()).hexdigest()
    return digest


def get_machine_id_short() -> str:
    """Return a user-friendly 16-char form: ``XXXX-XXXX-XXXX-XXXX``."""
    h = get_machine_id()[:16].upper()
    return "-".join(re.findall(r".{4}", h))

from __future__ import annotations

from pathlib import Path


_VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


def _read_app_version() -> str:
    version = _VERSION_FILE.read_text(encoding="utf-8").strip()
    if not version:
        raise RuntimeError("VERSION 文件为空")
    return version


APP_VERSION = _read_app_version()
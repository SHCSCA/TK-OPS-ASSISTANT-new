from __future__ import annotations

import re
from pathlib import Path

from desktop_app.version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_version_file_matches_runtime_and_release_artifacts() -> None:
    version = _read(ROOT / "VERSION").strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert APP_VERSION == version

    readme_text = _read(ROOT / "README.md")
    assert f"当前发布版本：`{version}`" in readme_text

    installer_text = _read(ROOT / "installer.iss")
    assert f'#define MyAppVersion   "{version}"' in installer_text

    bridge_text = _read(ROOT / "desktop_app" / "assets" / "js" / "bridge.js")
    assert f"getAppVersion: () => ok({{ version: '{version}' }})," in bridge_text
    assert f"checkForUpdate: () => ok({{ hasUpdate: false, current: '{version}' }})," in bridge_text


def test_file_version_info_matches_version_file() -> None:
    version = _read(ROOT / "VERSION").strip()
    major, minor, patch = version.split(".")
    version_info = _read(ROOT / "file_version_info.txt")

    assert f"filevers=({major}, {minor}, {patch}, 0)" in version_info
    assert f"prodvers=({major}, {minor}, {patch}, 0)" in version_info
    assert f'StringStruct("FileVersion",      "{version}")' in version_info
    assert f'StringStruct("ProductVersion",   "{version}")' in version_info
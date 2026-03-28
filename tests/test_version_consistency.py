from __future__ import annotations

import re
from pathlib import Path

from build import collect_version_metadata_updates
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


def test_collect_version_metadata_updates_detects_drift_without_writing_files(
    tmp_path: Path,
) -> None:
    version = _read(ROOT / "VERSION").strip()

    for relative_path in (
        "README.md",
        "installer.iss",
        "file_version_info.txt",
        Path("desktop_app") / "assets" / "js" / "bridge.js",
    ):
        source_path = ROOT / relative_path
        target_path = tmp_path / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(_read(source_path), encoding="utf-8")

    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        _read(readme_path).replace(
            f"当前发布版本：`{version}`",
            "当前发布版本：`0.0.0`",
            1,
        ),
        encoding="utf-8",
    )

    updates = collect_version_metadata_updates(version, root=tmp_path)

    assert set(updates) == {readme_path}
    assert f"当前发布版本：`{version}`" in updates[readme_path]
    assert "当前发布版本：`0.0.0`" in _read(readme_path)

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
INSTALLER = ROOT / "installer.iss"
RELEASE_SCRIPT = ROOT / "scripts" / "release.ps1"
PREFLIGHT_SCRIPT = ROOT / "scripts" / "preflight-gate.ps1"
DEV_SCRIPT = ROOT / "scripts" / "dev.ps1"
PACKAGE_JSON = ROOT / "apps" / "desktop" / "package.json"
RUNTIME_MAIN = ROOT / "apps" / "py-runtime" / "src" / "main.py"


def test_readme_uses_new_single_shell_commands() -> None:
    text = README.read_text(encoding="utf-8")

    assert "scripts\\dev.ps1" in text
    assert "scripts\\build-desktop.ps1 -SmokeRuntime" in text
    assert "scripts\\build-runtime.ps1" in text
    assert "scripts\\release.ps1" in text
    assert "scripts\\preflight-gate.ps1 -Quick" in text
    assert "scripts\\preflight-gate.ps1 -Full" in text
    assert "desktop_app\\main.py" not in text
    assert "build_exe.bat" not in text


def test_preflight_gate_script_exists_and_defines_modes() -> None:
    text = PREFLIGHT_SCRIPT.read_text(encoding="utf-8")

    assert "param(" in text
    assert "[switch]$Quick" in text
    assert "[switch]$Full" in text
    assert "MODE=Full" in text or "MODE={0}" in text
    assert "MODE=Quick" in text or "MODE={0}" in text


def test_dev_script_defaults_to_managed_runtime_for_desktop_host() -> None:
    text = DEV_SCRIPT.read_text(encoding="utf-8")

    assert "Starting Tauri desktop host..." in text
    assert 'TKOPS_RUNTIME_MANAGED = if ($runBrowserOnly) { "0" } else { "1" }' in text
    assert "Start-Process -FilePath $python" in text


def test_installer_targets_alpha_staging_instead_of_legacy_pyinstaller_output() -> None:
    text = INSTALLER.read_text(encoding="utf-8")

    assert r'Source: "dist-alpha\TK-OPS-Alpha\*"' in text
    assert r'Source: "dist\TK-OPS\*"' not in text
    assert 'TK-OPS.exe' in text


def test_release_script_builds_single_shell_alpha_payload() -> None:
    text = RELEASE_SCRIPT.read_text(encoding="utf-8")

    assert "dist-alpha" in text
    assert "TK-OPS-Alpha" in text
    assert "TK-OPS.exe" in text
    assert "runtime\\src" in text
    assert "desktop_app" in text
    assert "smoke-tauri-runtime.ps1" in text
    assert "preflight-gate.ps1" in text
    assert "SkipPreflight" in text
    assert "cargo" in text.lower()


def test_desktop_package_json_exposes_alpha_release_scripts() -> None:
    package_json = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    scripts = package_json["scripts"]

    assert "tauri:smoke" in scripts
    assert "alpha:release" in scripts
    assert "gate:quick" in scripts
    assert "gate:full" in scripts


def test_runtime_main_supports_alpha_bundle_root_detection() -> None:
    text = RUNTIME_MAIN.read_text(encoding="utf-8")

    assert "desktop_app" in text
    assert "parents[3]" not in text
    assert "parents" in text

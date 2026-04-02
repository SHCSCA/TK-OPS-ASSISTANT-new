from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PAGE = ROOT / "apps" / "desktop" / "src" / "pages" / "settings" / "SettingsPage.vue"
SETUP_PAGE = ROOT / "apps" / "desktop" / "src" / "pages" / "setup" / "SetupWizardPage.vue"
SETTINGS_MODULE = ROOT / "apps" / "desktop" / "src" / "modules" / "settings" / "useSettingsData.ts"
SETUP_MODULE = ROOT / "apps" / "desktop" / "src" / "modules" / "setup" / "useSetupWizardData.ts"


def test_settings_page_exposes_explicit_save_action() -> None:
    text = SETTINGS_PAGE.read_text(encoding="utf-8")

    assert "保存设置" in text
    assert "saveSettings" in text
    assert "theme" in text
    assert "language" in text
    assert "proxy" in text
    assert "timeout" in text
    assert "concurrency" in text


def test_setup_wizard_page_exposes_explicit_completion_action() -> None:
    text = SETUP_PAGE.read_text(encoding="utf-8")

    assert "保存并标记已完成" in text
    assert "saveSetup" in text
    assert "defaultMarket" in text
    assert "workflow" in text
    assert "model" in text
    assert "completed" in text


def test_settings_and_setup_modules_expose_save_handlers() -> None:
    settings_text = SETTINGS_MODULE.read_text(encoding="utf-8")
    setup_text = SETUP_MODULE.read_text(encoding="utf-8")

    assert "saveSettings" in settings_text
    assert "runtimeApi.saveSettings" in settings_text
    assert "saveSetup" in setup_text
    assert "runtimeApi.saveSetup" in setup_text

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PRESENTATION_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "runtimePresentation.ts"
SPLASH_HTML = ROOT / "apps" / "desktop" / "public" / "splash.html"
MAIN_CSS = ROOT / "apps" / "desktop" / "src" / "styles" / "main.css"


def test_runtime_presentation_module_covers_managed_external_browser_statuses() -> None:
    text = RUNTIME_PRESENTATION_TS.read_text(encoding="utf-8")

    for snippet in [
        "managed-running",
        "managed-runtime-detected",
        "external-reachable",
        "external-unreachable",
        "browser-fallback",
        "mapRuntimeStatus",
        "mapRuntimeLaunchMode",
        "mapThemeMode",
    ]:
        assert snippet in text, snippet


def test_splash_uses_tkops_icon_instead_of_tk_letter_block() -> None:
    text = SPLASH_HTML.read_text(encoding="utf-8")

    assert "src=\"/tkops.ico\"" in text
    assert "<div class=\"logo\">TK</div>" not in text


def test_notification_and_status_panels_have_viewport_bounded_scroll_styles() -> None:
    text = MAIN_CSS.read_text(encoding="utf-8")

    assert "max-height: min(460px, calc(100vh" in text
    assert "overflow-y: auto;" in text
    assert ".notification-panel" in text
    assert ".status-summary-panel" in text

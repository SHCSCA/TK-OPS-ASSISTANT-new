from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "main.js"


def test_startup_renders_boot_route_before_runtime_snapshot() -> None:
    text = MAIN_JS.read_text(encoding="utf-8")

    assert "const bootRoute = currentRoute;" in text
    assert "renderRoute(bootRoute);" in text
    assert "_loadShellRuntimeSnapshot().then(function (snapshot) {" in text
    assert "if (!onboardingCompleted && currentRoute !== 'setup-wizard')" in text
    assert text.index("renderRoute(bootRoute);") < text.index("_loadShellRuntimeSnapshot().then(function (snapshot) {")

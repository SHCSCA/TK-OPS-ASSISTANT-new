from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES_TS = ROOT / "apps" / "desktop" / "src" / "app" / "router" / "routes.ts"
SIDEBAR_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "Sidebar.vue"


def test_new_desktop_routes_cover_current_p0_runtime_pages() -> None:
    text = ROUTES_TS.read_text(encoding="utf-8")

    assert "path: '/accounts'" in text
    assert "name: 'account-management'" in text
    assert "path: '/ai-copywriter'" in text
    assert "name: 'ai-copywriter'" in text
    assert "path: '/providers'" in text
    assert "name: 'ai-provider'" in text
    assert "path: '/tasks'" in text
    assert "name: 'task-queue'" in text
    assert "path: '/setup-wizard'" in text
    assert "name: 'setup-wizard'" in text
    assert "path: '/settings'" in text
    assert "name: 'settings'" in text


def test_sidebar_exposes_p0_navigation_entries() -> None:
    text = SIDEBAR_VUE.read_text(encoding="utf-8")

    assert "'/accounts'" in text
    assert "'/ai-copywriter'" in text
    assert "'/providers'" in text
    assert "'/tasks'" in text
    assert "'/setup-wizard'" in text
    assert "'/settings'" in text
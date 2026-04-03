from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE_MANIFEST_TS = ROOT / "apps" / "desktop" / "src" / "app" / "router" / "routeManifest.ts"
ROUTES_TS = ROOT / "apps" / "desktop" / "src" / "app" / "router" / "routes.ts"
SIDEBAR_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "Sidebar.vue"
TITLE_BAR_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "TitleBar.vue"
APP_SHELL_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "AppShell.vue"
SHELL_STORE_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "shell" / "useShellStore.ts"
DASHBOARD_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "dashboard" / "DashboardPage.vue"


def test_route_manifest_covers_full_legacy_menu_matrix() -> None:
    text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    route_count = len(re.findall(r"legacyRouteKey:\s*'[^']+'", text))

    assert route_count == 44
    for snippet in [
        "path: '/'",
        "path: '/accounts'",
        "path: '/providers'",
        "path: '/tasks'",
        "path: '/task-scheduler'",
        "path: '/settings'",
        "path: '/network-diagnostics'",
        "name: 'dashboard'",
        "name: 'account'",
        "name: 'ai-provider'",
        "name: 'task-queue'",
        "name: 'system-settings'",
    ]:
        assert snippet in text, snippet


def test_routes_file_builds_from_manifest_with_conditional_alias() -> None:
    text = ROUTES_TS.read_text(encoding="utf-8")

    assert "shellRouteManifest" in text
    assert "MigrationPlaceholderPage" in text
    assert "pageComponents[item.pageKind]" in text
    assert "alias: item.aliases" not in text
    assert "if (item.aliases?.length)" in text


def test_sidebar_reads_navigation_from_route_manifest() -> None:
    text = SIDEBAR_VUE.read_text(encoding="utf-8")

    assert "shellNavGroups" in text
    assert "shellRouteManifest" in text
    assert "nav-link__glyph" in text


def test_titlebar_declares_full_shell_controls() -> None:
    text = TITLE_BAR_VUE.read_text(encoding="utf-8")

    for snippet in [
        "id=\"menuToggle\"",
        "id=\"globalSearch\"",
        "id=\"aiChatToggle\"",
        "id=\"detailToggle\"",
        "id=\"themeToggle\"",
        "id=\"notificationToggle\"",
        "id=\"statusSummaryToggle\"",
        "id=\"topbarMoreToggle\"",
        "id=\"topbarOverflowPanel\"",
    ]:
        assert snippet in text, snippet


def test_app_shell_contains_assistant_overlay_and_shell_classes() -> None:
    text = APP_SHELL_VUE.read_text(encoding="utf-8")

    assert "shell-viewport" in text
    assert "shell-canvas" in text
    assert "ai-chat-overlay" in text
    assert "sidebar-collapsed" in text
    assert "detail-hidden" in text
    assert "layout-${shell.layoutMode}" in text
    assert "shell.initializeShell" in text
    assert "shell.markCurrentRouteVisited" in text


def test_dashboard_page_restores_legacy_overview_structure_with_runtime_sections() -> None:
    text = DASHBOARD_PAGE_VUE.read_text(encoding="utf-8")

    for snippet in [
        "rangeOptions",
        "trendItems",
        "activityItems",
        "systemItems",
        "openTaskQueue",
        "openHistory",
        "新建任务",
    ]:
        assert snippet in text, snippet

    assert "刷新数据" not in text
    assert "异常聚焦" not in text
    assert "今日待办" not in text


def test_shell_store_centralizes_global_shell_state() -> None:
    text = SHELL_STORE_TS.read_text(encoding="utf-8")

    for snippet in [
        "themePreference",
        "layoutMode",
        "shellScale",
        "layoutViewportWidth",
        "layoutOverflowXEnabled",
        "sidebarCollapsed",
        "detailPanelVisible",
        "topbarOverflowActions",
        "statusBarCompactChips",
        "searchResults",
        "notifications",
        "runtimeHealth",
        "versionCurrent",
        "versionCheck",
        "assistantSuggestions",
        "dashboardRange",
        "selectedActivity",
        "selectedSystem",
        "setDashboardRange",
        "setSelectedActivity",
        "setSelectedSystem",
        "notifyAppShellReady",
        "runtimeApi.askShellAssistant",
    ]:
        assert snippet in text, snippet

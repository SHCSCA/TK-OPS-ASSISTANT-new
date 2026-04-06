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
ACCOUNTS_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "accounts" / "AccountsPage.vue"
DETAIL_PANEL_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "DetailPanel.vue"
MIGRATION_PLACEHOLDER_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "shared" / "MigrationPlaceholderPage.vue"


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
        "data-dashboard-range",
        "trendItems",
        "activityItems",
        "data-dashboard-activity",
        "systemItems",
        "data-dashboard-systems",
        "selectQuickAction",
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
        "dashboardDetailState",
        "setDashboardRange",
        "setSelectedActivity",
        "setSelectedSystem",
        "setDashboardDetailState",
        "resetDashboardDetailState",
        "notifyAppShellReady",
        "runtimeApi.askShellAssistant",
    ]:
        assert snippet in text, snippet


def test_titlebar_logo_uses_tkops_icon_instead_of_tk_text_block() -> None:
    text = TITLE_BAR_VUE.read_text(encoding="utf-8")

    assert "shell-icon shell-icon--strong\">TK" not in text
    assert "src=\"/tkops.ico\"" in text


def test_runtime_labels_use_chinese_surface_copy() -> None:
    title_bar_text = TITLE_BAR_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")
    detail_panel_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")

    assert "Runtime:" not in shell_store_text
    assert "运行时" in title_bar_text
    assert "runtimePresentation" in shell_store_text
    assert "runtimePresentation" in detail_panel_text
    assert "isDashboardRoute" in detail_panel_text
    assert "dashboardDetailState" in detail_panel_text


def test_stage_cards_source_dynamic_progress_instead_of_static_copy() -> None:
    sidebar_text = SIDEBAR_VUE.read_text(encoding="utf-8")
    placeholder_text = MIGRATION_PLACEHOLDER_PAGE_VUE.read_text(encoding="utf-8")

    assert "useMigrationProgress" in sidebar_text
    assert "useMigrationProgress" in placeholder_text
    assert "新桌面壳全局能力补齐" not in sidebar_text
    assert "菜单先行" not in placeholder_text


def test_dashboard_quick_actions_trigger_detail_not_direct_navigation() -> None:
    text = DASHBOARD_PAGE_VUE.read_text(encoding="utf-8")

    assert "@click=\"selectQuickAction('dashboard-quick-1')\"" in text
    assert "@click=\"selectQuickAction('dashboard-quick-2')\"" in text
    assert "@click=\"selectQuickAction('dashboard-quick-3')\"" in text
    assert "@click=\"selectQuickAction('dashboard-quick-4')\"" in text
    assert "@click=\"openRoute('ai-copywriter')\"" not in text


def test_account_page_restores_legacy_main_structure_and_entry_actions() -> None:
    text = ACCOUNTS_PAGE_VUE.read_text(encoding="utf-8")

    for snippet in [
        "js-account-isolation-banner",
        "js-account-status-tab",
        "js-account-view",
        "js-account-tag-batch",
        "js-account-batch-cancel",
        "account-grid",
        "js-account-open-environment",
        "js-account-manage-cookies",
        "js-account-rebind-validate",
        "导出账号清单",
        "批量检测环境",
        "新建账号",
    ]:
        assert snippet in text, snippet

    for frozen_value in [
        "992834012",
        "992834127",
        "992834305",
        "992834482",
        "TK_User_US_01",
    ]:
        assert frozen_value not in text, frozen_value


def test_account_detail_panel_branch_and_store_state_exist() -> None:
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")

    assert "isAccountRoute" in detail_text
    assert "data-points" in detail_text
    assert "detail-list" in detail_text
    assert "audit-list" in detail_text
    for snippet in [
        "进入环境",
        "Cookie 状态",
        "重绑并校验",
        "校验登录态",
        "检测代理",
        "编辑账号",
        "删除账号",
    ]:
        assert snippet in detail_text, snippet
    assert "dispatchAccountAction('validate-login')" in detail_text
    assert "dispatchAccountAction('edit-account')" in detail_text
    assert "dispatchAccountAction('delete-account')" in detail_text
    assert "tkops:account-detail-action" in detail_text
    assert "createDefaultAccountDetailState" in shell_store_text
    assert "dataPoints" in shell_store_text
    assert "detailItems" in shell_store_text
    assert "dutySummary" in shell_store_text
    assert "setAccountDetailState" in shell_store_text
    assert "resetAccountDetailState" in shell_store_text

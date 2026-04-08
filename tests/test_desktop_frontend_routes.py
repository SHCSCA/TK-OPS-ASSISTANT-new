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
MAIN_CSS = ROOT / "apps" / "desktop" / "src" / "styles" / "main.css"
DASHBOARD_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "dashboard" / "DashboardPage.vue"
ACCOUNTS_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "accounts" / "AccountsPage.vue"
DETAIL_PANEL_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "DetailPanel.vue"
MIGRATION_PLACEHOLDER_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "shared" / "MigrationPlaceholderPage.vue"
SCHEDULED_PUBLISH_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "publish" / "ScheduledPublishPage.vue"
DATA_COLLECTOR_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "collector" / "DataCollectorPage.vue"
CREATIVE_WORKSHOP_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "content" / "CreativeWorkshopPage.vue"
AI_CONTENT_FACTORY_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "content" / "AiContentFactoryPage.vue"
VIDEO_EDITOR_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "content" / "VideoEditorPage.vue"


def test_route_manifest_covers_full_legacy_menu_matrix() -> None:
    text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    route_count = len(re.findall(r"legacyRouteKey:\s*'[^']+'", text))

    assert route_count == 34
    for snippet in [
        "path: '/'",
        "path: '/accounts'",
        "path: '/providers'",
        "path: '/tasks'",
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


def test_device_page_and_detail_panel_branch_exist() -> None:
    device_page = (ROOT / "apps" / "desktop" / "src" / "pages" / "devices" / "DeviceManagementPage.vue").read_text(encoding="utf-8")
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")

    for snippet in [
        "data-page-audit=\"device-management\"",
        "data-device-banner",
        "data-filter-group=\"device-status\"",
        "device-env-grid",
        "data-device-binding-body",
        "data-device-coverage-panel",
        "binding-account-grid",
        "保存绑定关系",
        "导出设备报告",
        "新增设备环境",
    ]:
        assert snippet in device_page, snippet

    assert "isDeviceRoute" in detail_text
    assert "data-device-detail-kind" in detail_text
    assert "dispatchDeviceAction('open-environment')" in detail_text
    assert "dispatchDeviceAction('adjust-binding')" in detail_text
    assert "dispatchDeviceAction('open-logs')" in detail_text
    assert "dispatchDeviceAction('inspect-device')" in detail_text
    assert "dispatchDeviceAction('delete-device')" in detail_text
    assert "deviceDetailState" in shell_store_text
    assert "setDeviceDetailState" in shell_store_text
    assert "resetDeviceDetailState" in shell_store_text


def test_scheduled_publish_page_and_detail_panel_branch_exist() -> None:
    page_text = SCHEDULED_PUBLISH_PAGE_VUE.read_text(encoding="utf-8")
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")
    route_manifest_text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    routes_text = ROUTES_TS.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="scheduled-publish"',
        '新建发布计划',
        '查看发布日历',
        '发布计划列表',
        '发布日历',
        '计划明细表',
        'startPublishPlan(item.id)',
        'deletePublishPlan(item.id)',
    ]:
        assert snippet in page_text, snippet

    assert "isScheduledPublishRoute" in detail_text
    assert "data-scheduled-publish-detail-kind" in detail_text
    assert "dispatchPublishAction('start-plan')" in detail_text
    assert "dispatchPublishAction('delete-plan')" in detail_text
    assert "tkops:scheduled-publish-detail-action" in detail_text

    for snippet in [
        "createDefaultPublishDetailState",
        "publishDetailState",
        "setPublishDetailState",
        "resetPublishDetailState",
        "planId",
    ]:
        assert snippet in shell_store_text, snippet

    assert "pageKind: 'scheduledPublish'" in route_manifest_text
    assert "migrationStatus: 'implemented'" in route_manifest_text
    assert "ScheduledPublishPage" in routes_text
    assert "scheduledPublish: ScheduledPublishPage" in routes_text


def test_data_collector_page_and_detail_panel_branch_exist() -> None:
    page_text = DATA_COLLECTOR_PAGE_VUE.read_text(encoding="utf-8")
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")
    route_manifest_text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    routes_text = ROUTES_TS.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="data-collector"',
        'task-ops-shell',
        'task-filter-bar',
        'task-view-toggles',
        '采集任务表',
        '查看代理池',
        '新建采集方案',
        'startCollectorTask(item.id)',
        'deleteCollectorTask(item.id)',
    ]:
        assert snippet in page_text, snippet

    assert "isDataCollectorRoute" in detail_text
    assert "data-data-collector-detail-kind" in detail_text
    assert "dispatchCollectorAction('start-task')" in detail_text
    assert "dispatchCollectorAction('view-proxy-pool')" in detail_text
    assert "dispatchCollectorAction('delete-task')" in detail_text
    assert "tkops:data-collector-detail-action" in detail_text

    for snippet in [
        "createDefaultCollectorDetailState",
        "collectorDetailState",
        "setCollectorDetailState",
        "resetCollectorDetailState",
        "taskId",
    ]:
        assert snippet in shell_store_text, snippet

    assert "pageKind: 'dataCollector'" in route_manifest_text
    assert "name: 'data-collector'" in route_manifest_text
    assert "migrationStatus: 'implemented'" in route_manifest_text
    assert "DataCollectorPage" in routes_text
    assert "dataCollector: DataCollectorPage" in routes_text


def test_creative_workshop_page_and_detail_panel_branch_exist() -> None:
    page_text = CREATIVE_WORKSHOP_PAGE_VUE.read_text(encoding="utf-8")
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")
    route_manifest_text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    routes_text = ROUTES_TS.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="creative-workshop"',
        '创意组合画板',
        '对比创意版本',
        '保存创意方案',
        '创意版本对比',
        '实验项目',
        '进入视频编辑',
    ]:
        assert snippet in page_text, snippet

    assert "isCreativeWorkshopRoute" in detail_text
    assert "data-creative-workshop-detail-kind" in detail_text
    assert "dispatchCreativeAction('save-plan')" in detail_text
    assert "dispatchCreativeAction('compare-views')" in detail_text
    assert "dispatchCreativeAction('goto-video-editor')" in detail_text
    assert "tkops:creative-workshop-detail-action" in detail_text

    for snippet in [
        "createDefaultCreativeDetailState",
        "creativeDetailState",
        "setCreativeDetailState",
        "resetCreativeDetailState",
        "projectId",
    ]:
        assert snippet in shell_store_text, snippet

    assert "pageKind: 'creativeWorkshop'" in route_manifest_text
    assert "name: 'creative-workshop'" in route_manifest_text
    assert "migrationStatus: 'implemented'" in route_manifest_text
    assert "CreativeWorkshopPage" in routes_text
    assert "creativeWorkshop: CreativeWorkshopPage" in routes_text


def test_ai_content_factory_page_and_detail_panel_branch_exist() -> None:
    page_text = AI_CONTENT_FACTORY_PAGE_VUE.read_text(encoding="utf-8")
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")
    route_manifest_text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    routes_text = ROUTES_TS.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="ai-content-factory"',
        'AI 内容工厂',
        '组件库',
        '工作流设计',
        '批次运行状态',
        '保存工作流',
        '运行工作流',
        '启动批量生产',
        'aicf-shell',
    ]:
        assert snippet in page_text, snippet

    assert "isAiContentFactoryRoute" in detail_text
    assert "data-ai-content-factory-detail-kind" in detail_text
    assert "dispatchAiContentFactoryAction('save-workflow')" in detail_text
    assert "dispatchAiContentFactoryAction('run-batch')" in detail_text
    assert "dispatchAiContentFactoryAction('run-workflow')" in detail_text
    assert "tkops:ai-content-factory-detail-action" in detail_text

    for snippet in [
        "createDefaultAiContentFactoryDetailState",
        "aiContentFactoryDetailState",
        "setAiContentFactoryDetailState",
        "resetAiContentFactoryDetailState",
        "definitionId",
    ]:
        assert snippet in shell_store_text, snippet

    assert "pageKind: 'aiContentFactory'" in route_manifest_text
    assert "name: 'ai-content-factory'" in route_manifest_text
    assert "migrationStatus: 'implemented'" in route_manifest_text
    assert "AiContentFactoryPage" in routes_text
    assert "aiContentFactory: AiContentFactoryPage" in routes_text


def test_video_editor_page_and_detail_panel_branch_exist() -> None:
    page_text = VIDEO_EDITOR_PAGE_VUE.read_text(encoding="utf-8")
    detail_text = DETAIL_PANEL_VUE.read_text(encoding="utf-8")
    shell_store_text = SHELL_STORE_TS.read_text(encoding="utf-8")
    route_manifest_text = ROUTE_MANIFEST_TS.read_text(encoding="utf-8")
    routes_text = ROUTES_TS.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="video-editor"',
        '发起终版导出',
        '切换剪辑序列',
        '新增字幕',
        '保存快照',
        'video-editor-shell',
    ]:
        assert snippet in page_text, snippet

    assert "isVideoEditorRoute" in detail_text
    assert "data-video-editor-detail-kind" in detail_text
    assert "dispatchVideoEditorAction('export-final')" in detail_text
    assert "tkops:video-editor-detail-action" in detail_text

    for snippet in [
        "createDefaultVideoEditorDetailState",
        "videoEditorDetailState",
        "setVideoEditorDetailState",
        "resetVideoEditorDetailState",
        "sequenceId",
    ]:
        assert snippet in shell_store_text, snippet

    assert "pageKind: 'videoEditor'" in route_manifest_text
    assert "name: 'video-editor'" in route_manifest_text
    assert "migrationStatus: 'implemented'" in route_manifest_text
    assert "VideoEditorPage" in routes_text
    assert "videoEditor: VideoEditorPage" in routes_text


def test_detail_panel_styles_prevent_account_and_device_overflow() -> None:
    text = MAIN_CSS.read_text(encoding="utf-8")

    for snippet in [
        "[data-account-detail-kind] .account-detail__actions",
        "[data-device-detail-kind] .account-detail__actions",
        "[data-account-detail-kind] .detail-item--stacked strong",
        "[data-device-detail-kind] .detail-item--stacked strong",
        ".binding-account-grid",
        ".binding-account-card",
    ]:
        assert snippet in text, snippet

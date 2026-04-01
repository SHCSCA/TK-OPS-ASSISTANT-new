from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES_JS = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
VIDEO_EDITOR_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "video-editor-main.js"
TASK_QUEUE_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "task-queue-main.js"
TASK_OPS_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "task-ops-main.js"
ASSET_CENTER_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "asset-center-main.js"
DEVICE_ENV_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "device-environment.js"
DEVICE_MANAGEMENT_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "device-management-main.js"
OPERATIONS_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "operations.js"
GENERATION_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "generation.js"
MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "main.js"
STATE_JS = ROOT / "desktop_app" / "assets" / "js" / "state.js"


PRIMARY_RUNTIME_PAGES = [
    "dashboard",
    "account",
    "device-management",
    "ai-provider",
    "task-queue",
    "asset-center",
    "video-editor",
]


def test_page_loaders_register_runtime_summary_handlers_for_primary_pages() -> None:
    text = aggregate_page_loader_text()
    assert "runtimeSummaryHandlers" in text
    for route_key in PRIMARY_RUNTIME_PAGES:
        assert (
            f"'{route_key}':" in text
            or f'"{route_key}":' in text
            or f"runtimeSummaryHandlers['{route_key}']" in text
        ), route_key


def test_primary_page_route_summaries_no_longer_freeze_numeric_business_copy() -> None:
    routes_text = ROUTES_JS.read_text(encoding="utf-8")
    operations_text = OPERATIONS_JS.read_text(encoding="utf-8")
    generation_text = GENERATION_JS.read_text(encoding="utf-8")

    frozen_copy = {
        ROUTES_JS.name: [
            "AI 任务 452 条正在运行",
            "在线 12",
            "启用 Provider 3",
            "运行中 37 条，排队 28 条",
            "5 个高风险分组待复核",
        ],
        OPERATIONS_JS.name: [
            "3 台异常设备待处理",
            "设备可用率 95.3%",
        ],
        GENERATION_JS.name: [
            "12 个素材待审核",
            "素材 2148",
        ],
    }

    texts = {
        ROUTES_JS.name: routes_text,
        OPERATIONS_JS.name: operations_text,
        GENERATION_JS.name: generation_text,
    }

    for file_name, snippets in frozen_copy.items():
        for snippet in snippets:
            assert snippet not in texts[file_name], f"{file_name} still freezes runtime copy: {snippet}"


def test_runtime_summary_handlers_reference_real_data_sources() -> None:
    text = (
        PAGE_LOADERS_JS.read_text(encoding="utf-8")
        + "\n"
        + DEVICE_ENV_JS.read_text(encoding="utf-8")
        + "\n"
        + DEVICE_MANAGEMENT_MAIN_JS.read_text(encoding="utf-8")
        + "\n"
        + TASK_QUEUE_MAIN_JS.read_text(encoding="utf-8")
        + "\n"
        + ASSET_CENTER_MAIN_JS.read_text(encoding="utf-8")
        + "\n"
        + VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8")
    )
    required_sources = [
        "api.dashboard.overview(",
        "api.accounts.list()",
        "api.groups.list()",
        "api.devices.list()",
        "api.providers.list()",
        "api.tasks.list()",
        "api.assets.list()",
        "api.assets.stats()",
        "api.videoProjects.listVideoProjects()",
    ]
    for source in required_sources:
        assert source in text, source


def aggregate_page_loader_text() -> str:
    parts = [PAGE_LOADERS_JS.read_text(encoding="utf-8")]
    if VIDEO_EDITOR_MAIN_JS.exists():
        parts.append(VIDEO_EDITOR_MAIN_JS.read_text(encoding="utf-8"))
    return "\n".join(parts)


def test_video_editor_runtime_uses_project_sequence_clip_language() -> None:
    text = aggregate_page_loader_text()
    assert "listVideoProjects" in text
    assert "appendAssetsToSequence" in text
    assert "createVideoExport" in text


def test_task_queue_loader_split_remains_registered_in_shell_chain() -> None:
    shell_text = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")
    task_text = TASK_QUEUE_MAIN_JS.read_text(encoding="utf-8")

    assert './js/page-loaders/task-queue-main.js' in shell_text
    assert "loaders['task-queue'] = function ()" in task_text
    assert 'window.__taskQueuePageMain' in task_text


def test_task_ops_loader_split_remains_registered_in_shell_chain() -> None:
    shell_text = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")
    task_ops_text = TASK_OPS_MAIN_JS.read_text(encoding="utf-8")

    assert './js/page-loaders/task-ops-main.js' in shell_text
    assert "loaders['auto-reply'] = function ()" in task_ops_text
    assert "loaders['task-scheduler'] = function ()" in task_ops_text
    assert 'function _loadTaskOpsPage(config)' in task_ops_text


def test_asset_center_loader_split_remains_registered_in_shell_chain() -> None:
    shell_text = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")
    asset_text = ASSET_CENTER_MAIN_JS.read_text(encoding="utf-8")

    assert './js/page-loaders/asset-center-main.js' in shell_text
    assert "loaders['asset-center'] = function ()" in asset_text
    assert 'window.__assetCenterPageMain' in asset_text


def test_device_management_loader_split_remains_registered_in_shell_chain() -> None:
    shell_text = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")
    env_text = DEVICE_ENV_JS.read_text(encoding="utf-8")
    device_text = DEVICE_MANAGEMENT_MAIN_JS.read_text(encoding="utf-8")

    assert './js/page-loaders/device-environment.js' in shell_text
    assert './js/page-loaders/device-management-main.js' in shell_text
    assert 'window.__deviceEnvironmentHelpers' in env_text
    assert "loaders['device-management'] = function ()" in device_text
    assert 'window.__deviceManagementPageMain' in device_text


def test_remaining_realized_analytics_and_content_routes_reference_runtime_data_sources() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    required_sources = [
        "api.experiments.projects()",
        "api.experiments.views()",
        "api.analytics.summary()",
        "api.analytics.conversion()",
        "api.reports.list()",
        "api.activity.list()",
    ]
    for source in required_sources:
        assert source in text, source


def test_shell_runtime_state_exists_for_global_summary_management() -> None:
    text = STATE_JS.read_text(encoding="utf-8")
    required_snippets = [
        "shellRuntime:",
        "defaultSummary",
        "routeSummary",
        "license:",
        "notifications:",
        "update:",
        "onboarding:",
        "boot:",
    ]
    for snippet in required_snippets:
        assert snippet in text, snippet


def test_main_js_builds_shell_runtime_summary_from_real_sources() -> None:
    text = MAIN_JS.read_text(encoding="utf-8")
    required_snippets = [
        "api.dashboard.stats()",
        "api.notifications.list()",
        "api.license.status()",
        "api.version.current()",
        "api.version.check()",
        "api.settings.get('onboarding.completed')",
        "renderShellRuntimeSummary",
        "setShellRouteSummary",
        "setShellSystemStatus",
    ]
    for snippet in required_snippets:
        assert snippet in text, snippet

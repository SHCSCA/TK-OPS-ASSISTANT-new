from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES_JS = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
OPERATIONS_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "operations.js"
GENERATION_JS = ROOT / "desktop_app" / "assets" / "js" / "factories" / "generation.js"


PRIMARY_RUNTIME_PAGES = [
    "dashboard",
    "account",
    "group-management",
    "device-management",
    "ai-provider",
    "task-queue",
    "asset-center",
]


def test_page_loaders_register_runtime_summary_handlers_for_primary_pages() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    assert "runtimeSummaryHandlers" in text
    for route_key in PRIMARY_RUNTIME_PAGES:
        assert f"'{route_key}':" in text or f'"{route_key}":' in text, route_key


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
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    required_sources = [
        "api.dashboard.stats()",
        "api.accounts.list()",
        "api.groups.list()",
        "api.devices.list()",
        "api.providers.list()",
        "api.tasks.list()",
        "api.assets.list()",
        "api.assets.stats()",
    ]
    for source in required_sources:
        assert source in text, source


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

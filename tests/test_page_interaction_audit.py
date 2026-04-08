from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
ROUTES_JS = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
DATA_COLLECTOR_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "collector" / "DataCollectorPage.vue"
CREATIVE_WORKSHOP_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "content" / "CreativeWorkshopPage.vue"
AI_CONTENT_FACTORY_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "content" / "AiContentFactoryPage.vue"
VIDEO_EDITOR_PAGE_VUE = ROOT / "apps" / "desktop" / "src" / "pages" / "content" / "VideoEditorPage.vue"


PRIMARY_TEMPLATE_IDS = {
    "route-dashboard-main",
    "route-account-main",
    "route-ai-provider-main",
    "route-task-queue-main",
}


def test_primary_templates_define_interaction_audit_scope():
    html = APP_SHELL_HTML.read_text(encoding="utf-8")
    for template_id in PRIMARY_TEMPLATE_IDS:
        needle = f'<template id="{template_id}" data-page-audit='
        assert needle in html, f"Missing audit marker on {template_id}"


def test_primary_routes_define_audit_metadata():
    text = ROUTES_JS.read_text(encoding="utf-8")
    for route_key in ["dashboard", "account", "ai-provider", "task-queue"]:
        pattern = re.compile(
            rf"(?:'{re.escape(route_key)}'|{re.escape(route_key)})\s*:\s*\{{.*?audit:\s*\{{",
            re.DOTALL,
        )
        assert pattern.search(text), f"Route missing audit metadata: {route_key}"


def test_page_loader_audit_registry_covers_primary_routes():
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    for route_key in ["dashboard", "account", "ai-provider", "task-queue"]:
        assert f"'{route_key}':" in text or f'"{route_key}":' in text, route_key
    assert "window.__pageAudits" in text


def test_page_loader_audit_registry_covers_remaining_realized_analytics_and_content_routes():
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    for route_key in ["visual-lab", "profit-analysis", "report-center", "creative-workshop", "ai-content-factory"]:
        assert f"'{route_key}':" in text or f'"{route_key}":' in text, route_key


def test_data_collector_page_declares_audit_marker_and_real_actions():
    text = DATA_COLLECTOR_PAGE_VUE.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="data-collector"',
        '新建采集方案',
        '查看代理池',
        'task-filter-bar',
        'task-view-toggles',
        'collector-table',
    ]:
        assert snippet in text, snippet


def test_creative_workshop_page_declares_audit_marker_and_real_actions():
    text = CREATIVE_WORKSHOP_PAGE_VUE.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="creative-workshop"',
        '保存创意方案',
        '对比创意版本',
        '创意版本对比',
        '进入视频编辑',
        'workbench-summary-strip',
    ]:
        assert snippet in text, snippet


def test_ai_content_factory_page_declares_audit_marker_and_real_actions():
    text = AI_CONTENT_FACTORY_PAGE_VUE.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="ai-content-factory"',
        '保存工作流',
        '运行批次',
        '运行工作流',
        '启动批量生产',
        'aicf-shell',
    ]:
        assert snippet in text, snippet


def test_video_editor_page_declares_audit_marker_and_real_actions():
    text = VIDEO_EDITOR_PAGE_VUE.read_text(encoding="utf-8")

    for snippet in [
        'data-page-audit="video-editor"',
        '发起终版导出',
        '切换剪辑序列',
        '新增字幕',
        '保存快照',
        'video-editor-shell',
    ]:
        assert snippet in text, snippet

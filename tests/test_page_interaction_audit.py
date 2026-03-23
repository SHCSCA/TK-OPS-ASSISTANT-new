from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
ROUTES_JS = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"


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
    for route_key in ["visual-lab", "profit-analysis", "report-center", "creative-workshop"]:
        assert f"'{route_key}':" in text or f'"{route_key}":' in text, route_key

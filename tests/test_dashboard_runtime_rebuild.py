from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"
REPOSITORY_PY = ROOT / "desktop_app" / "database" / "repository.py"


def test_dashboard_header_primary_is_wired_to_task_form() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    assert "loaders['dashboard'] = function () {" in text
    assert "_wireHeaderPrimary(function () { openTaskForm(); }" in text


def test_dashboard_has_runtime_range_reload_logic() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    required = [
        "dashboardRange",
        "data-dashboard-range",
        "window.__loadDashboardOverview",
        "_syncDashboardRangeButtons",
        "api.dashboard.overview(",
    ]
    for snippet in required:
        assert snippet in text, snippet


def test_dashboard_uses_dedicated_backend_overview_surface() -> None:
    bridge_text = BRIDGE_PY.read_text(encoding="utf-8")
    data_text = (ROOT / "desktop_app" / "assets" / "js" / "data.js").read_text(encoding="utf-8")
    assert "def getDashboardOverview(" in bridge_text
    assert "callBackend('getDashboardOverview'" in data_text


def test_dashboard_template_no_longer_contains_static_svg_and_fake_engine_names() -> None:
    text = APP_SHELL_HTML.read_text(encoding="utf-8")
    forbidden = [
        "<svg viewBox=\"0 0 800 280\"",
        "Video Engine v4.2",
        "AI Script Gen",
        "Account Sync Hub",
        "Download Gateway",
    ]
    for snippet in forbidden:
        assert snippet not in text, snippet


def test_dashboard_template_declares_axis_labels_and_runtime_mount_points() -> None:
    text = APP_SHELL_HTML.read_text(encoding="utf-8")
    required = [
        "X 轴",
        "Y 轴",
        "data-dashboard-chart",
        "data-dashboard-activity",
        "data-dashboard-systems",
    ]
    for snippet in required:
        assert snippet in text, snippet


def test_dashboard_repository_supports_overview_queries() -> None:
    text = REPOSITORY_PY.read_text(encoding="utf-8")
    required = [
        "def list_recent_tasks(",
        "def list_recent_activity_logs(",
        "def count_tasks_created_between(",
        "def count_tasks_completed_between(",
        "def count_tasks_failed_between(",
    ]
    for snippet in required:
        assert snippet in text, snippet


def test_dashboard_bindings_define_route_specific_range_actions() -> None:
    text = BINDINGS_JS.read_text(encoding="utf-8")
    required = [
        "dashboard:",
        "'查看历史'",
        "'新建任务'",
        "'今日'",
        "'近 7 天'",
        "'近 30 天'",
    ]
    for snippet in required:
        assert snippet in text, snippet

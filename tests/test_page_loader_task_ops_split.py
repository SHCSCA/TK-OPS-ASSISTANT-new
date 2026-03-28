from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
TASK_OPS_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "task-ops-main.js"


def test_task_ops_loader_script_is_registered() -> None:
    html = APP_SHELL_HTML.read_text(encoding="utf-8")

    assert './js/page-loaders.js' in html
    assert './js/page-loaders/task-queue-main.js' in html
    assert './js/page-loaders/task-ops-main.js' in html


def test_task_ops_logic_is_split_from_page_loaders() -> None:
    page_loaders = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    task_ops = TASK_OPS_MAIN_JS.read_text(encoding="utf-8")

    assert 'window.__pageLoaderShared' in page_loaders
    assert 'normalizeTaskStatus: _normalizeTaskStatus' in page_loaders
    assert 'taskStatusLabel: _taskStatusLabel' in page_loaders
    assert 'taskStatusTone: _taskStatusTone' in page_loaders
    assert 'taskTypeLabel: _taskTypeLabel' in page_loaders
    assert 'taskTime: _taskTime' in page_loaders
    assert '// Task ops route loaders moved to page-loaders/task-ops-main.js.' in page_loaders
    assert '// Task ops route-specific helpers moved to page-loaders/task-ops-main.js.' in page_loaders

    moved_loaders = [
        "loaders['auto-reply'] = function ()",
        "loaders['scheduled-publish'] = function ()",
        "loaders['task-hall'] = function ()",
        "loaders['data-collector'] = function ()",
        "loaders['auto-like'] = function ()",
        "loaders['auto-comment'] = function ()",
        "loaders['auto-message'] = function ()",
        "loaders['task-scheduler'] = function ()",
    ]
    for marker in moved_loaders:
        assert marker not in page_loaders, marker
        assert marker in task_ops, marker

    moved_helpers = [
        'function _loadTaskOpsPage(config)',
        'function _updateTaskOpsMetrics(tasks, accounts, assets, config)',
        'function _bindTaskOpsHeaderActions(config, accounts)',
        'function _runInteractionQuickAction(config)',
        'function _renderTaskOpsBody(tasks, accounts, assets, config)',
        'function _bindTaskOpsTaskActions(tasks, config)',
        'function _renderTaskOpsDetail(tasks, accounts, assets, config)',
        'function _filterTasksByKey(tasks, key)',
        'function _filterTasksForOpsMode(tasks, tableMode)',
        'function _taskDraftForOpsRoute(config, accounts)',
        'function _taskTabKey(text)',
        'function _taskTabLabel(key)',
        'function _kanbanStatusByTitle(title, index, config)',
        'function _taskTicketHtml(task)',
        'function _rewireElements(selector, binder)',
    ]
    for marker in moved_helpers:
        assert marker not in page_loaders, marker
        assert marker in task_ops, marker

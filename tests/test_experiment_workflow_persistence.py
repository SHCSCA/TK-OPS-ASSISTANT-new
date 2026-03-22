from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"


def test_frontend_exposes_report_workflow_and_experiment_data_apis() -> None:
    text = DATA_JS.read_text(encoding='utf-8')
    required = [
        'reports:',
        "callBackend('listReportRuns')",
        "callBackend('createReportRun'",
        'workflows:',
        "callBackend('listWorkflowDefinitions')",
        "callBackend('createWorkflowDefinition'",
        "callBackend('listWorkflowRuns')",
        "callBackend('startWorkflowRun'",
        'experiments:',
        "callBackend('listExperimentProjects')",
        "callBackend('createExperimentProject'",
        "callBackend('listExperimentViews')",
        "callBackend('createExperimentView'",
        'activity:',
        "callBackend('listActivityLogs')",
    ]
    for marker in required:
        assert marker in text, marker


def test_persistence_backed_buttons_replace_placeholder_task_only_flows() -> None:
    text = BINDINGS_JS.read_text(encoding='utf-8')
    required = [
        "'保存实验视图': () => _createExperimentProjectFromRoute('visual-lab')",
        "'生成新报表': () => _createReportRunFromRoute()",
        "'保存创意方案': () => _createExperimentProjectFromRoute('creative-workshop')",
        "'保存工作流': () => _createWorkflowDefinitionFromRoute()",
        "'运行工作流': () => _createWorkflowRunFromRoute()",
    ]
    for marker in required:
        assert marker in text, marker

    placeholders = [
        "'保存创意方案': () => _createQuickTask('创意方案保存'",
        "'保存工作流': () => _createQuickTask('工作流保存'",
        "'运行工作流': () => _createQuickTask('运行工作流'",
    ]
    for marker in placeholders:
        assert marker not in text, marker


def test_runtime_loaders_read_persistent_records_for_visual_report_and_workflow_pages() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding='utf-8')
    required = [
        "loaders['visual-lab']",
        'api.experiments.projects()',
        'api.experiments.views()',
        "loaders['report-center']",
        'api.reports.list()',
        "loaders['creative-workshop']",
        "loaders['ai-content-factory']",
        'api.workflows.definitions()',
        'api.workflows.runs()',
    ]
    for marker in required:
        assert marker in text, marker

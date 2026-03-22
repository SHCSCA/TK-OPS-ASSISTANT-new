from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run_isolated_script(script: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env=env,
            text=True,
        )
    return json.loads(output.strip().splitlines()[-1])


def test_can_store_analysis_snapshot() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.analytics_service import AnalyticsService

repo = Repository()
service = AnalyticsService(repo)
snapshot = service.create_analysis_snapshot(
    'profit-analysis',
    '首轮聚合快照',
    summary='已聚合账号、任务、素材指标',
    payload_json='{"widgets": 3}',
)
snapshots = service.list_analysis_snapshots('profit-analysis')
print(json.dumps({
    'title': snapshot.title,
    'page_key': snapshot.page_key,
    'count': len(snapshots),
}, ensure_ascii=False))
"""
    )
    assert result["title"] == "首轮聚合快照"
    assert result["page_key"] == "profit-analysis"
    assert result["count"] == 1


def test_can_create_experiment_project_and_view() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.analytics_service import AnalyticsService

repo = Repository()
service = AnalyticsService(repo)
project = service.create_experiment_project(
    '视觉实验室改版',
    goal='验证新版实验页布局',
    config_json='{"variant": "b"}',
)
view = service.create_experiment_view(
    project.id,
    '趋势视图',
    layout_json='{"chart": "trend"}',
)
projects = service.list_experiment_projects()
views = service.list_experiment_views(project.id)
print(json.dumps({
    'project_name': project.name,
    'project_status': project.status,
    'view_name': view.name,
    'project_count': len(projects),
    'view_count': len(views),
}, ensure_ascii=False))
"""
    )
    assert result["project_name"] == "视觉实验室改版"
    assert result["project_status"] == "draft"
    assert result["view_name"] == "趋势视图"
    assert result["project_count"] == 1
    assert result["view_count"] == 1


def test_can_store_workflow_definition_and_run() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.workflow_service import WorkflowService

repo = Repository()
service = WorkflowService(repo)
definition = service.create_workflow_definition(
    '日常巡检工作流',
    config_json='{"steps": ["sync", "scan"]}',
)
run = service.create_workflow_run(
    definition.id,
    input_json='{"scope": "accounts"}',
)
definitions = service.list_workflow_definitions()
runs = service.list_workflow_runs(definition.id)
print(json.dumps({
    'definition_name': definition.name,
    'definition_status': definition.status,
    'run_status': run.status,
    'definition_count': len(definitions),
    'run_count': len(runs),
}, ensure_ascii=False))
"""
    )
    assert result["definition_name"] == "日常巡检工作流"
    assert result["definition_status"] == "draft"
    assert result["run_status"] == "pending"
    assert result["definition_count"] == 1
    assert result["run_count"] == 1


def test_can_store_report_run_and_activity_log() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.activity_service import ActivityService
from desktop_app.services.report_service import ReportService
from desktop_app.services.task_service import TaskService

repo = Repository()
task_service = TaskService(repo)
report_service = ReportService(repo)
activity_service = ActivityService(repo)
task = task_service.create_task('生成周报', task_type='report')
report = report_service.create_report_run(
    '周度经营报告',
    report_type='weekly',
    task_id=task.id,
    filters_json='{"window": "7d"}',
)
activity = activity_service.create_activity_log(
    'report',
    '已发起周度经营报告',
    payload_json='{"report": "weekly"}',
    related_entity_type='report_run',
    related_entity_id=report.id,
)
reports = report_service.list_report_runs()
activities = activity_service.list_activity_logs()
print(json.dumps({
    'report_title': report.title,
    'report_status': report.status,
    'activity_title': activity.title,
    'report_count': len(reports),
    'activity_count': len(activities),
}, ensure_ascii=False))
"""
    )
    assert result["report_title"] == "周度经营报告"
    assert result["report_status"] == "pending"
    assert result["activity_title"] == "已发起周度经营报告"
    assert result["report_count"] == 1
    assert result["activity_count"] == 1


def test_database_import_can_skip_auto_init_for_alembic_env() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        env["TK_OPS_DATA_DIR"] = temp_dir
        env["TKOPS_SKIP_DB_AUTO_INIT"] = "1"
        output = subprocess.check_output(
            [
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "import desktop_app.database as db; "
                    "print(Path(db.DB_PATH).exists())"
                ),
            ],
            cwd=str(ROOT),
            env=env,
            text=True,
        )
    assert output.strip().splitlines()[-1] == "False"

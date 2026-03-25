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


def test_can_store_account_cookie_content_and_timestamp() -> None:
    result = _run_isolated_script(
        """
import json
from datetime import datetime
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
account = service.create_account(
    'cookie_owner',
    cookie_status='valid',
    cookie_content='[{"name":"sessionid","value":"cookie-owner"}]',
)
updated = service.update_account(
    account.id,
    cookie_updated_at=datetime(2026, 3, 25, 10, 0, 0),
)
print(json.dumps({
    'status': updated.cookie_status,
    'cookie_len': len(updated.cookie_content or ''),
    'cookie_updated_at': str(updated.cookie_updated_at),
}, ensure_ascii=False))
"""
    )
    assert result['status'] == 'valid'
    assert int(result['cookie_len']) > 10
    assert '2026-03-25 10:00:00' in result['cookie_updated_at']


def test_account_login_validation_updates_runtime_fields() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
account = service.create_account(
    'login_owner',
    platform='tiktok',
    cookie_status='unknown',
    cookie_content='[{"name":"sessionid","value":"cookie-owner"}]',
)
service._run_login_validation = lambda account, cookie_entries, *, proxy_url, timeout: {
    'status': 'valid',
    'label': '已登录',
    'message': '已通过接口确认登录态',
    'target': 'https://www.tiktok.com/passport/web/account/info/',
    'http_status': 200,
}
checked = service.validate_account_login(account.id)
updated = service.get_account(account.id)
print(json.dumps({
    'result_status': checked['status'],
    'cookie_status': updated.cookie_status,
    'login_check_status': updated.last_login_check_status,
    'login_check_message': updated.last_login_check_message,
    'last_login_at': str(updated.last_login_at),
}, ensure_ascii=False))
"""
    )
    assert result['result_status'] == 'valid'
    assert result['cookie_status'] == 'valid'
    assert result['login_check_status'] == 'valid'
    assert '已通过接口确认登录态' in result['login_check_message']
    assert 'None' not in result['last_login_at']


def test_account_login_validation_marks_proxy_mismatch_when_direct_passes() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
account = service.create_account(
    'proxy_conflict_owner',
    platform='tiktok',
    cookie_status='unknown',
    cookie_content='[{"name":"sessionid","value":"cookie-owner"}]',
)
device = service.create_device('DEV-PROXY-01', 'Proxy Device', proxy_ip='http://127.0.0.1:8899')
service.bind_device(account.id, device.id)

def fake_attempt(account, validator, cookies, *, proxy_url, timeout):
    if proxy_url:
        return {
            'status': 'unknown',
            'label': '无法确认',
            'message': 'TikTok 已响应，但代理路径返回 400/application/json',
            'target': 'https://www.tiktok.com/passport/web/account/info/',
            'http_status': 400,
        }
    return {
        'status': 'valid',
        'label': '已登录',
        'message': '已通过页面态确认登录，可识别账号 shucengefsc',
        'target': 'https://www.tiktok.com/',
        'http_status': 200,
    }

service._execute_login_validation_attempt = fake_attempt
checked = service.validate_account_login(account.id)
updated = service.get_account(account.id)
print(json.dumps({
    'result_status': checked['status'],
    'cookie_status': updated.cookie_status,
    'login_check_status': updated.last_login_check_status,
    'login_check_message': updated.last_login_check_message,
}, ensure_ascii=False))
"""
    )
    assert result['result_status'] == 'proxy_mismatch'
    assert result['cookie_status'] == 'valid'
    assert result['login_check_status'] == 'proxy_mismatch'
    assert '绑定代理校验失败' in result['login_check_message']


def test_delete_account_clears_task_and_asset_references() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.models import Asset, Task
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
account = service.create_account('delete_owner', platform='tiktok')
task = repo.add(Task(title='账号收尾任务', account_id=account.id))
asset = repo.add(Asset(filename='封面图.png', file_path='C:/tmp/cover.png', account_id=account.id))
deleted = service.delete_account(account.id)
task_after = repo.get_by_id(Task, task.id)
asset_after = repo.get_by_id(Asset, asset.id)
account_after = service.get_account(account.id)
print(json.dumps({
    'deleted': deleted,
    'task_account_id': task_after.account_id if task_after else 'missing',
    'asset_account_id': asset_after.account_id if asset_after else 'missing',
    'account_exists': account_after is not None,
}, ensure_ascii=False))
"""
    )
    assert result['deleted'] is True
    assert result['task_account_id'] is None
    assert result['asset_account_id'] is None
    assert result['account_exists'] is False


def test_device_runtime_status_auto_updates_with_proxy_fields() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
device = service.create_device('DEV-AUTO-01', '自动状态设备', proxy_ip='23.88.14.10')
initial_status = device.status
initial_proxy_status = device.proxy_status
after_clear = service.update_device(device.id, proxy_ip='')
clear_status = after_clear.status
clear_proxy_status = after_clear.proxy_status
after_warning = service.update_device(device.id, proxy_ip='23.88.14.11', fingerprint_status='drifted')
warning_status = after_warning.status
warning_proxy_status = after_warning.proxy_status
after_error = service.update_device(device.id, proxy_ip='23.88.14.12', fingerprint_status='missing')
error_status = after_error.status
error_proxy_status = after_error.proxy_status
print(json.dumps({
    'initial_status': initial_status,
    'initial_proxy_status': initial_proxy_status,
    'clear_status': clear_status,
    'clear_proxy_status': clear_proxy_status,
    'warning_status': warning_status,
    'warning_proxy_status': warning_proxy_status,
    'error_status': error_status,
    'error_proxy_status': error_proxy_status,
}, ensure_ascii=False))
"""
    )
    assert result['initial_status'] == 'healthy'
    assert result['initial_proxy_status'] == 'online'
    assert result['clear_status'] == 'idle'
    assert result['clear_proxy_status'] == 'offline'
    assert result['warning_status'] == 'warning'
    assert result['warning_proxy_status'] == 'online'
    assert result['error_status'] == 'error'
    assert result['error_proxy_status'] == 'online'


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

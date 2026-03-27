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

def test_device_inspection_updates_runtime_fields_from_proxy_probe() -> None:
    result = _run_isolated_script(
        """
import json
import socket
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
device = service.create_device('DEV-INSP-01', 'Inspection Device', proxy_ip='http://127.0.0.1:8899')

class DummyConnection:
    def close(self):
        pass

original_create_connection = socket.create_connection
socket.create_connection = lambda *args, **kwargs: DummyConnection()
try:
    inspected = service.inspect_device(device.id)
finally:
    socket.create_connection = original_create_connection

updated = service.get_device(device.id)
print(json.dumps({
    'ok': inspected['ok'],
    'status': inspected['status'],
    'proxy_status': inspected['proxy_status'],
    'target': inspected['target'],
    'stored_status': updated.status,
    'stored_proxy_status': updated.proxy_status,
}, ensure_ascii=False))
"""
    )
    assert result['ok'] is True
    assert result['status'] == 'idle'
    assert result['proxy_status'] == 'online'
    assert result['target'] == '127.0.0.1:8899'
    assert result['stored_status'] == 'idle'
    assert result['stored_proxy_status'] == 'online'


def test_open_device_environment_prepares_profile_and_launch_command() -> None:
    result = _run_isolated_script(
        """
import json
import subprocess
from pathlib import Path
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
device = service.create_device('DEV-OPEN-01', 'Browser Device', proxy_ip='https://user:pass@123.1.2.2:9000')

service._resolve_browser_executable = lambda: r'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
captured = {}

class DummyProcess:
    pid = 43210

class DummyRelay:
    local_endpoint = '127.0.0.1:47211'
    def close(self):
        pass

service._start_device_proxy_relay = lambda device_id, endpoint: DummyRelay()
service._validate_proxy_endpoint = lambda endpoint: {
    'ok': True,
    'message': '代理连通性验证通过',
    'status_code': 200,
    'egress_ip': '91.204.17.22',
    'detail': '出口 IP 91.204.17.22',
}

def fake_popen(command, creationflags=0, close_fds=False):
    captured['command'] = command
    captured['creationflags'] = creationflags
    captured['close_fds'] = close_fds
    return DummyProcess()

original_popen = subprocess.Popen
subprocess.Popen = fake_popen
try:
    opened = service.open_device_environment(device.id)
finally:
    subprocess.Popen = original_popen

profile_dir = Path(opened['profile_dir'])
manifest = profile_dir / 'tkops-profile.json'
launcher = profile_dir / 'tkops-proxy-launcher.html'
print(json.dumps({
    'pid': opened['pid'],
    'browser_path': opened['browser_path'],
    'proxy_server': opened['proxy_server'],
    'configured_proxy': opened['configured_proxy'],
    'configured_proxy_display': opened['configured_proxy_display'],
    'browser_proxy': opened['browser_proxy'],
    'validation_ok': opened['validation']['ok'],
    'proxy_probe_url': opened['proxy_probe_url'],
    'profile_exists': profile_dir.exists(),
    'manifest_exists': manifest.exists(),
    'launcher_exists': launcher.exists(),
    'launcher_mentions_probe_url': opened['proxy_probe_url'] in launcher.read_text(encoding='utf-8'),
    'launcher_url': opened['launcher_url'],
    'command_has_proxy': any('--proxy-server=127.0.0.1:47211' == part for part in captured['command']),
    'command_has_profile': any(str(part).startswith('--user-data-dir=') for part in captured['command']),
    'command_uses_launcher': any('tkops-proxy-launcher.html' in str(part) for part in captured['command']),
}, ensure_ascii=False))
"""
    )
    assert result['pid'] == 43210
    assert result['browser_path'].lower().endswith('msedge.exe')
    assert result['proxy_server'] == '127.0.0.1:47211'
    assert result['configured_proxy'] == 'https://user:pass@123.1.2.2:9000'
    assert result['configured_proxy_display'] == 'https://user:***@123.1.2.2:9000'
    assert result['browser_proxy'] == '127.0.0.1:47211'
    assert result['validation_ok'] is True
    assert result['proxy_probe_url'].startswith('http://127.0.0.1:')
    assert result['profile_exists'] is True
    assert result['manifest_exists'] is True
    assert result['launcher_exists'] is True
    assert result['launcher_mentions_probe_url'] is True
    assert 'tkops-proxy-launcher.html' in result['launcher_url']
    assert result['command_has_proxy'] is True
    assert result['command_has_profile'] is True
    assert result['command_uses_launcher'] is True


def test_open_device_environment_requires_proxy_port() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
device = service.create_device('DEV-BAD-PROXY', 'Broken Proxy Device', proxy_ip='user:pass@91.204.17.22')
service._resolve_browser_executable = lambda: r'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'

try:
    service.open_device_environment(device.id)
except Exception as exc:
    print(json.dumps({
        'error': str(exc),
    }, ensure_ascii=False))
"""
    )
    assert 'host:port' in result['error']


def test_open_account_environment_prepares_cookie_extension_and_marks_account_runtime() -> None:
    result = _run_isolated_script(
        """
import json
import subprocess
from pathlib import Path
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
device = service.create_device('DEV-ACCOUNT-01', 'Account Device', proxy_ip='https://user:pass@123.1.2.2:9000')
account = service.create_account(
    'account_owner',
    platform='tiktok',
    device_id=device.id,
    isolation_enabled=False,
    cookie_content='[{"name":"sessionid","value":"cookie-owner","domain":".tiktok.com","path":"/","secure":true,"httpOnly":true}]',
)

service._resolve_browser_executable = lambda: r'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
captured = {}

class DummyProcess:
    pid = 54321

class DummyRelay:
    local_endpoint = '127.0.0.1:48888'
    def close(self):
        pass

service._start_device_proxy_relay = lambda device_id, endpoint: DummyRelay()
service._validate_proxy_endpoint = lambda endpoint: {
    'ok': True,
    'message': '代理连通性验证通过',
    'status_code': 200,
    'egress_ip': '91.204.17.22',
    'detail': '出口 IP 91.204.17.22',
}

def fake_popen(command, creationflags=0, close_fds=False):
    captured['command'] = command
    return DummyProcess()

original_popen = subprocess.Popen
subprocess.Popen = fake_popen
try:
    opened = service.open_account_environment(account.id)
finally:
    subprocess.Popen = original_popen

updated = service.get_account(account.id)
profile_dir = Path(opened['profile_dir'])
extension_dir = Path(opened['extension_dir'])
background = (extension_dir / 'background.js').read_text(encoding='utf-8')
manifest = json.loads((extension_dir / 'manifest.json').read_text(encoding='utf-8'))
print(json.dumps({
    'pid': opened['pid'],
    'launch_mode': opened['launch_mode'],
    'cookie_count': opened['cookie_count'],
    'account_id': opened['account_id'],
    'account_username': opened['account_username'],
    'extension_name': opened['extension_name'],
    'extension_ready': opened['extension_ready'],
    'extension_install_required': opened['extension_install_required'],
    'extension_install_hint': opened['extension_install_hint'],
    'extension_exists': extension_dir.exists(),
    'manifest_name': manifest['name'],
    'has_cookie_permission': 'cookies' in manifest['permissions'],
    'has_target_permission': 'https://www.tiktok.com/*' in manifest['host_permissions'],
    'background_mentions_cookie': 'sessionid' in background,
    'background_mentions_report_url': 'reportUrl' in background,
    'background_mentions_validation_endpoint': 'passport/web/account/info/' in background,
    'command_has_load_extension': any(str(part).startswith('--load-extension=') for part in captured['command']),
    'command_has_disable_except': any(str(part).startswith('--disable-extensions-except=') for part in captured['command']),
    'account_isolation_enabled': bool(updated.isolation_enabled),
    'account_last_login_at': str(updated.last_login_at),
    'profile_exists': profile_dir.exists(),
}, ensure_ascii=False))
"""
    )
    assert result['pid'] == 54321
    assert result['launch_mode'] == 'loopback_relay_account_session'
    assert result['cookie_count'] == 1
    assert result['account_username'] == 'account_owner'
    assert result['extension_name'] == 'TKOPS Account Session'
    assert result['extension_ready'] is True
    assert result['extension_install_required'] is False
    assert '无需手动安装' in result['extension_install_hint']
    assert result['extension_exists'] is True
    assert 'TKOPS Account Session' in result['manifest_name']
    assert result['has_cookie_permission'] is True
    assert result['has_target_permission'] is True
    assert result['background_mentions_cookie'] is True
    assert result['background_mentions_report_url'] is True
    assert result['background_mentions_validation_endpoint'] is True
    assert result['command_has_load_extension'] is True
    assert result['command_has_disable_except'] is True
    assert result['account_isolation_enabled'] is True
    assert result['account_last_login_at'] not in {'', 'None'}
    assert result['profile_exists'] is True


def test_open_account_environment_failure_is_logged_with_error_code() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.activity_service import ActivityService
from desktop_app.ui.bridge import Bridge

bridge = Bridge()
account = bridge._accounts.create_account('broken_cookie_owner', platform='tiktok', cookie_content='[]')
response = json.loads(bridge.openAccountEnvironment(account.id))
logs = bridge._activity.list_activity_logs(category='account_environment_failed')
latest = logs[0] if logs else None
payload = ActivityService._load_payload(latest.payload_json if latest else None)
print(json.dumps({
    'ok': response.get('ok'),
    'error': response.get('error', ''),
    'logged': latest is not None,
    'category': latest.category if latest else '',
    'title': latest.title if latest else '',
    'error_code': payload.get('error_code', ''),
    'message': payload.get('message', ''),
}, ensure_ascii=False))
"""
    )
    assert result['ok'] is False
    assert '当前账号未绑定设备' in result['error']
    assert result['logged'] is True
    assert result['category'] == 'account_environment_failed'
    assert result['error_code'] == 'device_unbound'
    assert '当前账号未绑定设备' in result['message']


def test_parse_proxy_endpoint_supports_authenticated_proxy_formats() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService

repo = Repository()
service = AccountService(repo)
http_endpoint = service._parse_proxy_endpoint('user:pass@127.0.0.1:8899')
https_endpoint = service._parse_proxy_endpoint('https://user:pa%23ss@127.0.0.1:9443')
print(json.dumps({
    'http_display': http_endpoint.display,
    'http_upstream': http_endpoint.upstream_url,
    'http_host_port': http_endpoint.host_port,
    'https_display': https_endpoint.display,
    'https_upstream': https_endpoint.upstream_url,
    'https_host_port': https_endpoint.host_port,
}, ensure_ascii=False))
"""
    )
    assert result['http_display'] == 'http://user:***@127.0.0.1:8899'
    assert result['http_upstream'] == 'http://user:pass@127.0.0.1:8899'
    assert result['http_host_port'] == '127.0.0.1:8899'
    assert result['https_display'] == 'https://user:***@127.0.0.1:9443'
    assert result['https_upstream'] == 'https://user:pa%23ss@127.0.0.1:9443'
    assert result['https_host_port'] == '127.0.0.1:9443'

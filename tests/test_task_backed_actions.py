from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
BRIDGE_JS = ROOT / "desktop_app" / "assets" / "js" / "bridge.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"
TASK_SERVICE_PY = ROOT / "desktop_app" / "services" / "task_service.py"
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"


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


def test_task_service_can_create_named_action_tasks_with_metadata() -> None:
    result = _run_isolated_script(
        """
import json
from desktop_app.database.repository import Repository
from desktop_app.services.task_service import TaskService

repo = Repository()
service = TaskService(repo)
task = service.create_action_task(
    'batch_environment_check',
    title='批量环境检测',
    summary='来源页面：账号管理 / 批量检测环境',
    metadata={'route': 'account', 'selected_ids': [1, 2, 3]},
)
tasks = service.list_tasks()
print(json.dumps({
    'title': task.title,
    'task_type': task.task_type,
    'status': task.status,
    'summary': task.result_summary,
    'count': len(tasks),
}, ensure_ascii=False))
"""
    )
    assert result['title'] == '批量环境检测'
    assert result['task_type'] == 'maintenance'
    assert result['status'] == 'pending'
    assert 'batch_environment_check' in str(result['summary'])
    assert result['count'] == 1


def test_bridge_exposes_task_backed_action_creation_slot() -> None:
    text = BRIDGE_PY.read_text(encoding='utf-8')
    assert 'def createTaskAction(' in text
    assert 'self._tasks.create_action_task(' in text

    bridge_stub_text = BRIDGE_JS.read_text(encoding='utf-8')
    assert 'createTaskAction:' in bridge_stub_text

    data_text = DATA_JS.read_text(encoding='utf-8')
    assert 'taskActions:' in data_text
    assert "callBackend('createTaskAction'" in data_text


def test_device_page_routes_environment_actions_to_runtime_hooks() -> None:
    text = BINDINGS_JS.read_text(encoding='utf-8')
    expected = [
        "window.__openDeviceEnvironment",
        "window.__repairDevices",
        "window.__exportDeviceLog",
    ]
    for marker in expected:
        assert marker in text, marker

    stale_markers = [
        "_createNamedTaskAction('device_open_environment'",
        "showToast('设备环境启动命令已下发', 'success')",
    ]
    for marker in stale_markers:
        assert marker not in text, marker

    data_text = DATA_JS.read_text(encoding='utf-8')
    assert 'openEnvironment: function (id)' in data_text
    assert 'logs: function (id)' in data_text


def test_account_page_exposes_direct_connection_detection_hooks() -> None:
    bridge_text = BRIDGE_PY.read_text(encoding='utf-8')
    assert 'def testAccountConnection(' in bridge_text
    assert 'self._accounts.test_account_connection(' in bridge_text

    data_text = DATA_JS.read_text(encoding='utf-8')
    assert 'testConnection: function (id)' in data_text
    assert "callBackend('testAccountConnection'" in data_text

    bindings_text = BINDINGS_JS.read_text(encoding='utf-8')
    assert "'测试连接': () => _createNamedTaskAction('account_connection_test'" not in bindings_text
    assert "'管理 Cookies': () => _createNamedTaskAction('account_cookie_maintenance'" not in bindings_text

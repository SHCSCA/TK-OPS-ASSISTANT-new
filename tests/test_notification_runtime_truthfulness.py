from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_NOTIFICATIONS_JS = ROOT / "desktop_app" / "assets" / "js" / "ui-notifications.js"
BRIDGE_PY = ROOT / "desktop_app" / "ui" / "bridge.py"
BRIDGE_JS = ROOT / "desktop_app" / "assets" / "js" / "bridge.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"


def test_notification_ui_no_longer_injects_simulated_timeout_messages() -> None:
    text = UI_NOTIFICATIONS_JS.read_text(encoding="utf-8")
    forbidden = [
        "setTimeout(() => addNotification('系统提醒'",
        "setTimeout(() => addNotification('任务完成'",
        "setTimeout(() => addNotification('AI 模型更新'",
        "setTimeout(() => addNotification('性能告警'",
    ]
    for marker in forbidden:
        assert marker not in text, marker


def test_bridge_and_data_layer_expose_notification_loading_surface() -> None:
    bridge_py_text = BRIDGE_PY.read_text(encoding="utf-8")
    bridge_js_text = BRIDGE_JS.read_text(encoding="utf-8")
    data_js_text = DATA_JS.read_text(encoding="utf-8")

    assert "def listNotifications(" in bridge_py_text
    assert "listNotifications:" in bridge_js_text
    assert "notifications:" in data_js_text
    assert "callBackend('listNotifications')" in data_js_text

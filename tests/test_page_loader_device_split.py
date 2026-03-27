from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
DEVICE_ENV_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "device-environment.js"
DEVICE_MANAGEMENT_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "device-management-main.js"


def test_device_management_loader_script_is_registered() -> None:
    html = APP_SHELL_HTML.read_text(encoding="utf-8")

    assert './js/page-loaders.js' in html
    assert './js/page-loaders/device-environment.js' in html
    assert './js/page-loaders/device-management-main.js' in html


def test_device_management_logic_is_split_from_page_loaders() -> None:
    page_loaders = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    device_env = DEVICE_ENV_JS.read_text(encoding="utf-8")
    device_main = DEVICE_MANAGEMENT_MAIN_JS.read_text(encoding="utf-8")

    assert "'device-management': function (payload)" in page_loaders
    assert 'window.__pageLoaderShared' in page_loaders
    assert 'buildDeviceViewModel: _buildDeviceViewModel' in page_loaders
    assert 'function _getDeviceEnvironmentHelpers()' in page_loaders
    assert 'window.__deviceEnvironmentHelpers' in device_env
    assert 'runDeviceRepair: _runDeviceRepair' in device_env
    assert 'openDeviceEnvironment: _openDeviceEnvironment' in device_env
    assert 'exportDeviceLog: _exportDeviceLog' in device_env
    assert "loaders['device-management'] = function ()" in device_main
    assert 'var deviceEnvironment = window.__deviceEnvironmentHelpers' in device_main
    assert '_renderDeviceDetail' in device_main
    assert '_renderDeviceGrid' in device_main
    assert '_bindDeviceDetailActions' in device_main
    assert 'window.__deviceManagementPageMain' in device_main
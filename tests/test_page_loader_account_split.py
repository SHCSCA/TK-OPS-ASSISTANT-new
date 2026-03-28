from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_HTML = ROOT / "desktop_app" / "assets" / "app_shell.html"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
ACCOUNT_ENV_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "account-environment.js"
ACCOUNT_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "account-main.js"


def test_account_environment_loader_script_is_registered() -> None:
    html = APP_SHELL_HTML.read_text(encoding="utf-8")
    assert './js/page-loaders.js' in html
    assert './js/page-loaders/account-environment.js' in html
    assert './js/page-loaders/account-main.js' in html


def test_account_environment_logic_is_split_from_page_loaders() -> None:
    page_loaders = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    account_env = ACCOUNT_ENV_JS.read_text(encoding="utf-8")
    account_main = ACCOUNT_MAIN_JS.read_text(encoding="utf-8")

    assert 'window.__accountEnvironmentHelpers' in account_env
    assert 'function _getAccountEnvironmentHelpers()' in page_loaders
    assert 'window.__pageLoaderShared' in page_loaders
    assert 'openAccountProxyConfig(account, options)' in account_env
    assert 'openAccountCookieModal(account)' in account_env
    assert 'runAccountLoginValidation(accountId, button, options)' in account_env
    assert "loaders['account'] = function ()" in account_main
    assert 'window.__accountPageMain' in account_main


def test_account_main_prefers_newest_accounts_and_moves_rebind_validate_into_the_loader() -> None:
    account_main = ACCOUNT_MAIN_JS.read_text(encoding="utf-8")

    assert '_sortAccountsNewestFirst' in account_main
    assert 'js-account-configure-proxy' not in account_main
    assert 'js-account-rebind-validate' in account_main
    assert 'validateAfterSave: true' in account_main
    assert '重绑并校验' in account_main


def test_account_environment_proxy_binding_modal_uses_read_only_device_fields() -> None:
    account_env = ACCOUNT_ENV_JS.read_text(encoding="utf-8")

    required_markers = [
        '_buildAccountProxyDeviceSnapshot',
        "key: 'device_id'",
        "key: 'proxy_ip'",
        "key: 'region'",
        "key: 'status_preview'",
        'disabled: true',
        '选择设备（可选）',
        '重绑并校验',
        '代理 IP',
        '地区',
        '设备状态',
        '只读',
    ]

    for marker in required_markers:
        assert marker in account_env, marker
    assert 'quickValidate' not in account_env

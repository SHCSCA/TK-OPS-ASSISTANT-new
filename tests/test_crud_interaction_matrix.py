from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES_JS = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
ACCOUNT_ENV_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "account-environment.js"
ACCOUNT_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "account-main.js"
TASK_QUEUE_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "task-queue-main.js"
ASSET_CENTER_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "asset-center-main.js"
DEVICE_ENV_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "device-environment.js"
DEVICE_MANAGEMENT_MAIN_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders" / "device-management-main.js"
UI_CRUD_FORMS_JS = ROOT / "desktop_app" / "assets" / "js" / "ui-crud-forms.js"
SEARCH_JS = ROOT / "desktop_app" / "assets" / "js" / "search.js"
STATE_JS = ROOT / "desktop_app" / "assets" / "js" / "state.js"
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
VIDEO_EDITOR_BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings" / "video-editor-bindings.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"
COMPONENTS_CSS = ROOT / "desktop_app" / "assets" / "css" / "components.css"


def _account_loader_runtime_text() -> str:
    return (
        PAGE_LOADERS_JS.read_text(encoding="utf-8")
        + "\n"
        + ACCOUNT_ENV_JS.read_text(encoding="utf-8")
        + "\n"
        + ACCOUNT_MAIN_JS.read_text(encoding="utf-8")
    )


def _task_queue_loader_runtime_text() -> str:
    return PAGE_LOADERS_JS.read_text(encoding="utf-8") + "\n" + TASK_QUEUE_MAIN_JS.read_text(encoding="utf-8")


def _asset_center_loader_runtime_text() -> str:
    return PAGE_LOADERS_JS.read_text(encoding="utf-8") + "\n" + ASSET_CENTER_MAIN_JS.read_text(encoding="utf-8")


def _device_management_loader_runtime_text() -> str:
    return (
        PAGE_LOADERS_JS.read_text(encoding="utf-8")
        + "\n"
        + DEVICE_ENV_JS.read_text(encoding="utf-8")
        + "\n"
        + DEVICE_MANAGEMENT_MAIN_JS.read_text(encoding="utf-8")
    )


def aggregate_binding_text() -> str:
    parts = [BINDINGS_JS.read_text(encoding="utf-8")]
    if VIDEO_EDITOR_BINDINGS_JS.exists():
        parts.append(VIDEO_EDITOR_BINDINGS_JS.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _video_editor_binding_text() -> str:
    if VIDEO_EDITOR_BINDINGS_JS.exists():
        return VIDEO_EDITOR_BINDINGS_JS.read_text(encoding="utf-8")
    text = BINDINGS_JS.read_text(encoding="utf-8")
    start = text.index("            '发起终版导出': () =>")
    end = text.index("            '运行批次': () =>", start)
    return text[start:end]


CRUD_ROUTE_EXPECTATIONS = {
    "account": ["create", "edit", "delete", "filter", "detail", "batch", "task"],
    "device-management": ["create", "edit", "delete", "filter", "detail", "batch"],
    "ai-provider": ["create", "edit", "activate", "delete", "detail"],
    "task-queue": ["create", "edit", "start", "complete", "delete", "filter", "detail", "batch"],
    "asset-center": ["create", "edit", "delete", "filter", "detail"],
}


LOADER_MARKERS = {
    "account": [
        "loaders['account']",
        "openAccountForm(",
        ".js-edit-account",
        ".js-delete-account",
        ".js-view-account",
        ".js-account-rebind-validate",
        ".js-batch-account",
        "_renderAccountDetail(",
    ],
    "device-management": [
        "loaders['device-management']",
        "openDeviceForm(",
        ".js-edit-device",
        ".js-delete-device",
        "_renderDeviceDetail(",
        "_renderDeviceFilterTabs(",
        "_bindDeviceDetailActions(",
    ],
    "ai-provider": [
        "loaders['ai-provider']",
        "openProviderForm(",
        ".js-edit-provider",
        ".js-activate-provider",
        ".js-delete-provider",
        "_renderProviderDetail(",
    ],
    "task-queue": [
        "loaders['task-queue']",
        "openTaskForm(",
        ".js-edit-task",
        ".js-start-task",
        ".js-complete-task",
        ".js-delete-task",
        ".js-batch-task",
        "_renderTaskDetail(",
    ],
    "asset-center": [
        "loaders['asset-center']",
        "openAssetForm(",
        ".js-edit-asset",
        ".js-delete-asset",
        "_renderAssetDetail(",
    ],
}


FILTER_ROUTE_EXPECTATIONS = {
    "account": ["account: { statusFilter:", "applyAccountState("],
    "device-management": ["uiState['device-management']", "applyDeviceManagementState("],
    "task-queue": ["uiState['task-queue']", "applyTaskState("],
    "asset-center": ["uiState['asset-center']", "applyAssetCenterState("],
}


FORM_MARKERS = {
    "account": "function openAccountForm(existing)",
    "device-management": "function openDeviceForm(existing)",
    "ai-provider": "function openProviderForm(existing)",
    "task-queue": "function openTaskForm(existing)",
    "asset-center": "function openAssetForm(existing)",
}


def _window(text: str, anchors: str | list[str], span: int = 1400) -> str:
    if isinstance(anchors, str):
        anchors = [anchors]
    start = -1
    for anchor in anchors:
        start = text.find(anchor)
        if start >= 0:
            break
    assert start >= 0, f"Missing anchor: {anchors[0]}"
    return text[start:start + span]


def test_crud_routes_declare_full_audit_interaction_sets() -> None:
    text = ROUTES_JS.read_text(encoding="utf-8")
    for route_key, interactions in CRUD_ROUTE_EXPECTATIONS.items():
        window = _window(text, [f"'{route_key}':", f'"{route_key}":', f"{route_key}:"])
        assert "audit:" in window, f"Route missing audit metadata: {route_key}"
        for interaction in interactions:
            assert f"'{interaction}'" in window, f"Route audit missing {interaction}: {route_key}"


def test_page_loader_registry_covers_all_crud_routes_and_interactions() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    assert "pageAudits" in text
    page_audits_text = text[text.find("var pageAudits = {"):]
    for route_key, interactions in CRUD_ROUTE_EXPECTATIONS.items():
        window = _window(page_audits_text, [f"'{route_key}':", f'"{route_key}":'])
        for interaction in interactions:
            assert f"'{interaction}'" in window, f"Page audit missing {interaction}: {route_key}"


def test_crud_forms_exist_for_each_mutating_page() -> None:
    text = UI_CRUD_FORMS_JS.read_text(encoding="utf-8")
    for route_key, marker in FORM_MARKERS.items():
        assert marker in text, f"Missing CRUD form entrypoint for {route_key}"


def test_page_loaders_expose_real_loader_hooks_for_promised_crud_interactions() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    account_text = _account_loader_runtime_text()
    task_queue_text = _task_queue_loader_runtime_text()
    asset_center_text = _asset_center_loader_runtime_text()
    device_management_text = _device_management_loader_runtime_text()
    for route_key, markers in LOADER_MARKERS.items():
        if route_key == "account":
            source_text = account_text
        elif route_key == "device-management":
            source_text = device_management_text
        elif route_key == "task-queue":
            source_text = task_queue_text
        elif route_key == "asset-center":
            source_text = asset_center_text
        else:
            source_text = text
        for marker in markers:
            assert marker in source_text, f"Loader hook missing for {route_key}: {marker}"


def test_filterable_crud_pages_have_route_state_and_apply_handlers() -> None:
    state_text = STATE_JS.read_text(encoding="utf-8")
    search_text = SEARCH_JS.read_text(encoding="utf-8")
    for route_key, markers in FILTER_ROUTE_EXPECTATIONS.items():
        assert markers[0] in state_text, f"Missing uiState bucket for {route_key}"
        assert markers[1] in search_text, f"Missing filter apply handler for {route_key}"


def test_remaining_crud_buttons_no_longer_route_to_placeholder_flows() -> None:
    text = aggregate_binding_text()

    required_handlers = [
        "'批量开始': () => _batchStartSelectedTasks()",
        "'恢复默认': () => _resetSelectedProviderDefaults()",
        "'保存变更': () => _openSelectedProviderEditModal()",
        "'Save Changes': () => _openSelectedProviderEditModal()",
        "'调整绑定': (btn) => _openDeviceBindingModal(btn)",
        "'修改绑定': (btn) => _openDeviceBindingModal(btn)",
        "'批量打标签': () => _openAssetTagBatchModal()",
    ]
    for marker in required_handlers:
        assert marker in text, marker

    placeholder_flows = [
        "'批量开始': () => showToast('批量启动任务已加入队列', 'info')",
        "'调整绑定': () => showToast('绑定调整面板正在接入', 'info')",
        "'修改绑定': () => showToast('绑定修改面板正在接入', 'info')",
        "'保存变更': () => showToast('供应商配置已记录，建议先执行连接测试', 'success')",
        "'Save Changes': () => showToast('供应商配置已记录，建议先执行连接测试', 'success')",
    ]
    for marker in placeholder_flows:
        assert marker not in text, marker


def test_video_editor_actions_are_not_plain_toasts() -> None:
    text = _video_editor_binding_text()
    assert "发起终版导出" in text
    assert "_createQuickTask('终版导出'" not in text
    assert "showToast('已切换到剪辑序列选择模式'" not in text


def test_asset_mutations_invalidate_asset_runtime_caches() -> None:
    text = DATA_JS.read_text(encoding="utf-8")
    assert "else if (entity === 'asset')" in text
    assert "_cacheInvalidate('assets:');" in text


def test_runtime_renderers_preserve_filter_metadata_for_account_and_task_pages() -> None:
    account_text = _account_loader_runtime_text()
    task_queue_text = _task_queue_loader_runtime_text()
    page_text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    account_markers = [
        "<article class=\"account-card",
        "data-detail-target=\"' + _esc(a.detailTarget) + '\"",
        "data-status=\"' + _esc(_accountFilterStatus(a.status)) + '\"",
        "data-search=\"' + _esc(_buildAccountSearchText(a.raw, a.device, a.tags",
        "data-order=\"' + _esc(_accountSortOrder(a.status)) + '\"",
    ]
    task_markers = [
        "<tr class=\"route-row\" data-id=\"' + (task.id || '') + '\" data-status=\"' + _esc((task.status || '').toLowerCase()) + '\"",
    ]
    for marker in account_markers:
        assert marker in account_text, marker
    for marker in task_markers:
        assert marker in task_queue_text, marker


def test_account_cookie_runtime_exposes_import_and_login_validation_actions() -> None:
    page_text = _account_loader_runtime_text()
    data_text = DATA_JS.read_text(encoding="utf-8")
    form_text = UI_CRUD_FORMS_JS.read_text(encoding="utf-8")

    required_page_markers = [
        'js-validate-account-login',
        'js-account-rebind-validate',
        'validateAfterSave: true',
        '_saveAccountProxyBinding(',
        '_unbindAccountProxyBinding(',
        '_buildProxyMismatchGuidance(',
        '_predictDeviceRuntimeState(',
        '_runAccountLoginValidation(',
        '_importCookieFileIntoModal(',
    ]
    for marker in required_page_markers:
        assert marker in page_text, marker

    required_data_markers = [
        "validateLogin: function (id) { return callBackend('validateAccountLogin', id); }",
        "importTextFile: function () { return callBackend('importTextFile'); }",
    ]
    for marker in required_data_markers:
        assert marker in data_text, marker

    required_form_markers = [
        "key: 'device_id'",
        "key: 'proxy_ip'",
        "key: 'region'",
        'disabled: true',
    ]
    for marker in required_form_markers:
        assert marker in form_text, marker

def test_account_toolbar_uses_real_environment_flow_and_log_toggle() -> None:
    page_text = _account_loader_runtime_text()
    device_text = _device_management_loader_runtime_text()
    shell_text = (ROOT / "desktop_app" / "assets" / "app_shell.html").read_text(encoding="utf-8")

    assert "js-account-filter-exception" not in shell_text
    assert "js-account-sort" not in shell_text
    assert "api.accounts.openEnvironment(account.id)" in page_text
    assert "已为账号 " in page_text
    assert "已注入 " in page_text
    assert "js-device-toggle-logs" in device_text


def test_account_loader_keeps_newest_accounts_first_sort_contract() -> None:
    account_text = ACCOUNT_MAIN_JS.read_text(encoding="utf-8")

    assert '_sortAccountsNewestFirst(accounts.map(function (account) {' in account_text
    assert 'return rightCreated - leftCreated;' in account_text


def test_account_status_cards_keep_offline_and_exception_tints_in_css() -> None:
    css_text = COMPONENTS_CSS.read_text(encoding="utf-8")

    assert '.account-card[data-status="offline"] {' in css_text
    assert '.account-card[data-status="exception"] {' in css_text
    assert 'background: color-mix(in srgb, var(--status-info) 6%, var(--surface-secondary));' in css_text
    assert 'background: color-mix(in srgb, var(--status-error) 6%, var(--surface-secondary));' in css_text

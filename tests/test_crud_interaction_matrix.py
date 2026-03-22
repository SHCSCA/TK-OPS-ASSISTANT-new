from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES_JS = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS_JS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"
UI_CRUD_FORMS_JS = ROOT / "desktop_app" / "assets" / "js" / "ui-crud-forms.js"
SEARCH_JS = ROOT / "desktop_app" / "assets" / "js" / "search.js"
STATE_JS = ROOT / "desktop_app" / "assets" / "js" / "state.js"
BINDINGS_JS = ROOT / "desktop_app" / "assets" / "js" / "bindings.js"
DATA_JS = ROOT / "desktop_app" / "assets" / "js" / "data.js"


CRUD_ROUTE_EXPECTATIONS = {
    "account": ["create", "edit", "delete", "filter", "detail", "batch", "task"],
    "group-management": ["create", "edit", "delete", "filter", "detail"],
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
        ".js-batch-account",
        "_renderAccountDetail(",
    ],
    "group-management": [
        "loaders['group-management']",
        "openGroupForm(",
        ".js-edit-group",
        ".js-delete-group",
        "_renderGroupDetail(",
    ],
    "device-management": [
        "loaders['device-management']",
        "openDeviceForm(",
        ".js-edit-device",
        ".js-delete-device",
        "_renderDeviceDetail(",
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
    "group-management": ["uiState['group-management']", "applyGroupManagementState("],
    "device-management": ["uiState['device-management']", "applyDeviceManagementState("],
    "task-queue": ["uiState['task-queue']", "applyTaskState("],
    "asset-center": ["uiState['asset-center']", "applyAssetCenterState("],
}


FORM_MARKERS = {
    "account": "function openAccountForm(existing)",
    "group-management": "function openGroupForm(existing)",
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
    for route_key, markers in LOADER_MARKERS.items():
        for marker in markers:
            assert marker in text, f"Loader hook missing for {route_key}: {marker}"


def test_filterable_crud_pages_have_route_state_and_apply_handlers() -> None:
    state_text = STATE_JS.read_text(encoding="utf-8")
    search_text = SEARCH_JS.read_text(encoding="utf-8")
    for route_key, markers in FILTER_ROUTE_EXPECTATIONS.items():
        assert markers[0] in state_text, f"Missing uiState bucket for {route_key}"
        assert markers[1] in search_text, f"Missing filter apply handler for {route_key}"


def test_remaining_crud_buttons_no_longer_route_to_placeholder_flows() -> None:
    text = BINDINGS_JS.read_text(encoding="utf-8")

    required_handlers = [
        "'批量归组': () => _openBatchGroupAssignmentModal()",
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
        "'批量归组': () => typeof renderRoute === 'function' ? renderRoute('group-management') : null",
        "'批量开始': () => showToast('批量启动任务已加入队列', 'info')",
        "'调整绑定': () => showToast('绑定调整面板正在接入', 'info')",
        "'修改绑定': () => showToast('绑定修改面板正在接入', 'info')",
        "'保存变更': () => showToast('供应商配置已记录，建议先执行连接测试', 'success')",
        "'Save Changes': () => showToast('供应商配置已记录，建议先执行连接测试', 'success')",
    ]
    for marker in placeholder_flows:
        assert marker not in text, marker


def test_asset_mutations_invalidate_asset_runtime_caches() -> None:
    text = DATA_JS.read_text(encoding="utf-8")
    assert "else if (entity === 'asset')" in text
    assert "_cacheInvalidate('assets:');" in text


def test_runtime_renderers_preserve_filter_metadata_for_account_and_task_pages() -> None:
    text = PAGE_LOADERS_JS.read_text(encoding="utf-8")
    required_markers = [
        "<article class=\"account-card",
        "data-status=\"' + _esc((a.status || '').toLowerCase()) + '\"",
        "data-search=\"' + _esc((a.username || '') + ' ' + (a.platform || '') + ' ' + (a.region || '') + ' ' + (a.status || '') + ' ' + (a.notes || '')) + '\"",
        "data-order=\"' + _esc(_accountSortOrder(a.status)) + '\"",
        "<tr class=\"route-row\" data-id=\"' + (t.id || '') + '\" data-status=\"' + _esc((t.status || '').toLowerCase()) + '\"",
    ]
    for marker in required_markers:
        assert marker in text, marker

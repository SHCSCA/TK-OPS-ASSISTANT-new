from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACCOUNTS_PAGE = ROOT / "apps" / "desktop" / "src" / "pages" / "accounts" / "AccountsPage.vue"
ACCOUNTS_DATA = ROOT / "apps" / "desktop" / "src" / "modules" / "accounts" / "useAccountsData.ts"
ACCOUNTS_TYPES = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "types.ts"
ACCOUNTS_API = ROOT / "apps" / "desktop" / "src" / "modules" / "runtime" / "runtimeApi.ts"


def test_accounts_page_exposes_filters_batch_actions_detail_and_archive_first_copy() -> None:
    text = ACCOUNTS_PAGE.read_text(encoding="utf-8") + "\n" + ACCOUNTS_DATA.read_text(encoding="utf-8")
    for snippet in [
        "账号管理",
        "人工状态筛选",
        "系统状态筛选",
        "风险状态筛选",
        "显示归档",
        "批量改人工状态",
        "批量改风险状态",
        "批量分组",
        "批量检测",
        "批量归档",
        "批量仅取消归档",
        "批量停用",
        "批量恢复启用",
        "账号审计中心",
        "绑定环境",
        "最近错误",
        "最近活动摘要",
        "最近活动记录",
        "刷新活动记录",
        "按活动关键词过滤",
        "全部分类",
        "全部级别",
        "生命周期动作",
        "停用账号",
        "恢复账号",
        "彻底删除",
        "账号导入向导（CSV 文本）",
        "预检查导入内容",
        "执行导入",
        "覆盖已存在账号",
        "归档优先",
        "新建账号",
        "编辑账号",
        "测试连接",
    ]:
        assert snippet in text, snippet


def test_accounts_data_layer_defines_filters_selection_detail_and_bulk_actions() -> None:
    text = ACCOUNTS_DATA.read_text(encoding="utf-8")
    for snippet in [
        "filters",
        "selectedAccountIds",
        "selectedAccountId",
        "accountDetail",
        "detailError",
        "loadAccountDetail",
        "loadAccountActivity",
        "recentActivityItems",
        "previewAccountImport",
        "applyAccountImport",
        "importPreview",
        "importApplyResult",
        "importDraft",
        "bulkChangeManualStatus",
        "bulkChangeRiskStatus",
        "bulkChangeGroup",
        "bulkTestAccounts",
        "bulkArchiveAccounts",
        "bulkSuspendAccounts",
        "bulkRestoreAccounts",
        "bulkUnarchiveAccounts",
        "suspendAccount",
        "restoreAccount",
        "deleteAccount",
        "lifecycleReason",
        "activityCategory",
        "activitySeverity",
        "runtimeApi.listAccounts",
        "runtimeApi.getAccountDetail",
        "runtimeApi.getAccountActivity",
        "runtimeApi.applyAccountLifecycle",
        "runtimeApi.previewAccountImport",
        "runtimeApi.applyAccountImport",
        "runtimeApi.bulkUpdateAccounts",
    ]:
        assert snippet in text, snippet


def test_accounts_runtime_contract_defines_new_query_and_detail_fields() -> None:
    text = ACCOUNTS_TYPES.read_text(encoding="utf-8") + "\n" + ACCOUNTS_API.read_text(encoding="utf-8")
    for snippet in [
        "export interface AccountListQuery",
        "manualStatus",
        "systemStatus",
        "riskStatus",
        "includeArchived",
        "export interface AccountDetail",
        "export interface AccountActivityListResponse",
        "filters?:",
        "export interface AccountImportPayload",
        "export interface AccountImportPreviewResult",
        "export interface AccountImportApplyResult",
        "export type AccountLifecycleActionType",
        "export interface AccountLifecyclePayload",
        "export interface AccountLifecycleResult",
        "activitySummary",
        "boundEnvironment",
        "recentError",
        "export interface AccountBulkActionPayload",
        "export type AccountBulkActionType",
        "listAccounts(params?: AccountListQuery)",
        "getAccountDetail(accountId: number)",
        "getAccountActivity(",
        "previewAccountImport(payload: AccountImportPayload)",
        "applyAccountImport(payload: AccountImportPayload)",
        "applyAccountLifecycle(payload:",
        "bulkUpdateAccounts(payload: AccountBulkActionPayload)",
        "archiveAccount(accountId: number)",
        "category",
        "severity",
        "archiveReason",
        "manual_status",
        "system_status",
        "risk_status",
        "include_archived",
    ]:
        assert snippet in text, snippet

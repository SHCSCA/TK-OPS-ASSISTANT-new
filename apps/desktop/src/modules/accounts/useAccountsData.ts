import { computed, reactive, ref, watch } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';
import type {
  AccountActivitySummaryItem,
  AccountBulkActionPayload,
  AccountBulkActionType,
  AccountDetail,
  AccountImportApplyResult,
  AccountImportPayload,
  AccountImportPreviewResult,
  AccountItem,
  AccountListQuery,
  AccountUpsertPayload,
} from '../runtime/types';

interface AccountDraftState {
  username: string;
  platform: string;
  region: string;
  manualStatus: string;
  riskStatus: string;
  followers: number;
  groupId: string;
  deviceId: string;
  cookieStatus: string;
  notes: string;
  tags: string;
}

interface AccountFilterState {
  query: string;
  manualStatus: string;
  systemStatus: string;
  riskStatus: string;
  includeArchived: boolean;
}

interface AccountBulkDraftState {
  manualStatus: string;
  riskStatus: string;
  groupId: string;
  groupName: string;
}

interface AccountImportDraftState {
  content: string;
  delimiter: string;
  hasHeader: boolean;
  updateExisting: boolean;
}

interface StatusOption {
  value: string;
  label: string;
}

type AccountLifecycleTarget = Pick<AccountItem, 'id' | 'username'>;

const MANUAL_STATUS_OPTIONS: StatusOption[] = [
  { value: '', label: '全部人工状态' },
  { value: 'active', label: '启用' },
  { value: 'warming', label: '预热' },
  { value: 'idle', label: '闲置' },
  { value: 'suspended', label: '停用' },
  { value: 'review', label: '待审核' },
];

const SYSTEM_STATUS_OPTIONS: StatusOption[] = [
  { value: '', label: '全部系统状态' },
  { value: 'online', label: '在线' },
  { value: 'syncing', label: '同步中' },
  { value: 'degraded', label: '降级' },
  { value: 'offline', label: '离线' },
  { value: 'unknown', label: '未知' },
];

const RISK_STATUS_OPTIONS: StatusOption[] = [
  { value: '', label: '全部风险状态' },
  { value: 'safe', label: '安全' },
  { value: 'watch', label: '观察' },
  { value: 'warning', label: '预警' },
  { value: 'high_risk', label: '高风险' },
  { value: 'blocked', label: '阻断' },
  { value: 'unknown', label: '未知' },
];

const ACTIVITY_CATEGORY_OPTIONS: StatusOption[] = [
  { value: '', label: '全部分类' },
  { value: 'account_created', label: '创建' },
  { value: 'account_updated', label: '更新' },
  { value: 'account_suspended', label: '停用' },
  { value: 'account_archived', label: '归档' },
  { value: 'account_restored', label: '恢复' },
  { value: 'account_deleted', label: '删除' },
];

const ACTIVITY_SEVERITY_OPTIONS: StatusOption[] = [
  { value: '', label: '全部级别' },
  { value: 'info', label: '信息' },
  { value: 'success', label: '成功' },
  { value: 'warning', label: '警告' },
  { value: 'error', label: '错误' },
];

const DEFAULT_DRAFT: AccountDraftState = {
  username: '',
  platform: 'tiktok',
  region: 'US',
  manualStatus: 'active',
  riskStatus: 'unknown',
  followers: 0,
  groupId: '',
  deviceId: '',
  cookieStatus: 'unknown',
  notes: '',
  tags: '',
};

const DEFAULT_FILTERS: AccountFilterState = {
  query: '',
  manualStatus: '',
  systemStatus: '',
  riskStatus: '',
  includeArchived: false,
};

const DEFAULT_BULK_DRAFT: AccountBulkDraftState = {
  manualStatus: 'active',
  riskStatus: 'unknown',
  groupId: '',
  groupName: '',
};

const DEFAULT_IMPORT_DRAFT: AccountImportDraftState = {
  content: '',
  delimiter: ',',
  hasHeader: true,
  updateExisting: false,
};

function createDefaultDraft(): AccountDraftState {
  return { ...DEFAULT_DRAFT };
}

function createDefaultFilters(): AccountFilterState {
  return { ...DEFAULT_FILTERS };
}

function createDefaultBulkDraft(): AccountBulkDraftState {
  return { ...DEFAULT_BULK_DRAFT };
}

function createDefaultImportDraft(): AccountImportDraftState {
  return { ...DEFAULT_IMPORT_DRAFT };
}

function toDraft(account: AccountItem): AccountDraftState {
  return {
    username: account.username,
    platform: account.platform,
    region: account.region,
    manualStatus: account.manualStatus || account.status || 'active',
    riskStatus: account.riskStatus || 'unknown',
    followers: Number(account.followers || 0),
    groupId: account.groupId === null ? '' : String(account.groupId),
    deviceId: account.deviceId === null ? '' : String(account.deviceId),
    cookieStatus: account.cookieStatus || 'unknown',
    notes: '',
    tags: '',
  };
}

function parseOptionalNumber(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? Math.trunc(parsed) : null;
}

function normalizeStatus(value: string, fallback: string): string {
  const trimmed = value.trim();
  return trimmed || fallback;
}

function buildListQuery(filters: AccountFilterState): AccountListQuery {
  return {
    query: filters.query.trim() || undefined,
    manualStatus: filters.manualStatus.trim() || undefined,
    systemStatus: filters.systemStatus.trim() || undefined,
    riskStatus: filters.riskStatus.trim() || undefined,
    includeArchived: filters.includeArchived,
  };
}

export function useAccountsData() {
  const filters = reactive<AccountFilterState>(createDefaultFilters());
  const bulkDraft = reactive<AccountBulkDraftState>(createDefaultBulkDraft());
  const importDraft = reactive<AccountImportDraftState>(createDefaultImportDraft());
  const draft = ref<AccountDraftState>(createDefaultDraft());
  const actionError = ref('');
  const actionMessage = ref('');
  const saving = ref(false);
  const testingAccountId = ref<number | null>(null);
  const archivingAccountId = ref<number | null>(null);
  const editingAccountId = ref<number | null>(null);
  const selectedAccountId = ref<number | null>(null);
  const selectedAccountIds = ref<number[]>([]);
  const accountDetail = ref<AccountDetail | null>(null);
  const recentActivityItems = ref<AccountActivitySummaryItem[]>([]);
  const activityQuery = ref('');
  const activityLimit = ref(50);
  const activityCategory = ref('');
  const activitySeverity = ref('');
  const detailError = ref('');
  const detailLoading = ref(false);
  const activityError = ref('');
  const activityLoading = ref(false);
  const bulkWorkingAction = ref<AccountBulkActionType | ''>('');
  const lifecycleReason = ref('');
  const suspendingAccountId = ref<number | null>(null);
  const restoringAccountId = ref<number | null>(null);
  const deletingAccountId = ref<number | null>(null);
  const importPreview = ref<AccountImportPreviewResult | null>(null);
  const importApplyResult = ref<AccountImportApplyResult | null>(null);
  const importLoading = ref(false);
  const importApplying = ref(false);
  const importError = ref('');
  const importMessage = ref('');
  let detailRequestToken = 0;
  let activityRequestToken = 0;

  const resource = useAsyncResource(() => runtimeApi.listAccounts(buildListQuery(filters)));

  function clearActionFeedback() {
    actionError.value = '';
    actionMessage.value = '';
  }

  function createDefaultFiltersState() {
    Object.assign(filters, createDefaultFilters());
  }

  function createDefaultBulkDraftState() {
    Object.assign(bulkDraft, createDefaultBulkDraft());
  }

  function createDefaultImportDraftState() {
    Object.assign(importDraft, createDefaultImportDraft());
    importPreview.value = null;
    importApplyResult.value = null;
    importError.value = '';
    importMessage.value = '';
  }

  function clearSelectedAccounts() {
    selectedAccountIds.value = [];
  }

  function prepareCreate() {
    editingAccountId.value = null;
    draft.value = createDefaultDraft();
    clearActionFeedback();
  }

  function beginEdit(account: AccountItem) {
    editingAccountId.value = account.id;
    draft.value = toDraft(account);
    clearActionFeedback();
  }

  function buildPayload(): AccountUpsertPayload {
    const manualStatus = normalizeStatus(draft.value.manualStatus, 'active');
    const riskStatus = normalizeStatus(draft.value.riskStatus, 'unknown');

    return {
      username: draft.value.username.trim(),
      platform: draft.value.platform.trim(),
      region: draft.value.region.trim() || 'US',
      status: manualStatus,
      manualStatus,
      riskStatus,
      followers: Number.isFinite(draft.value.followers) ? Math.max(0, Math.trunc(draft.value.followers)) : 0,
      groupId: parseOptionalNumber(draft.value.groupId),
      deviceId: parseOptionalNumber(draft.value.deviceId),
      cookieStatus: draft.value.cookieStatus.trim() || 'unknown',
      notes: draft.value.notes.trim() || null,
      tags: draft.value.tags.trim() || null,
    };
  }

  async function refreshAccounts() {
    await resource.load();
  }

  async function loadAccountDetail(accountId: number) {
    selectedAccountId.value = accountId;
    detailLoading.value = true;
    detailError.value = '';
    const requestToken = ++detailRequestToken;

    try {
      const detail = await runtimeApi.getAccountDetail(accountId);
      if (requestToken === detailRequestToken) {
        accountDetail.value = detail;
        void loadAccountActivity(accountId);
      }
    } catch (cause) {
      if (requestToken === detailRequestToken) {
        accountDetail.value = null;
        recentActivityItems.value = [];
        detailError.value = cause instanceof Error ? cause.message : '加载账号详情失败';
      }
    } finally {
      if (requestToken === detailRequestToken) {
        detailLoading.value = false;
      }
    }
  }

  async function loadAccountActivity(
    accountId: number,
    options: {
      limit?: number;
      query?: string;
      category?: string;
      severity?: string;
    } = {},
  ) {
    activityLoading.value = true;
    activityError.value = '';
    const requestToken = ++activityRequestToken;

    try {
      const response = await runtimeApi.getAccountActivity(accountId, {
        limit: options.limit ?? activityLimit.value,
        query: options.query ?? activityQuery.value,
        category: options.category ?? activityCategory.value,
        severity: options.severity ?? activitySeverity.value,
      });
      if (requestToken === activityRequestToken) {
        recentActivityItems.value = response.items || [];
      }
    } catch (cause) {
      if (requestToken === activityRequestToken) {
        recentActivityItems.value = [];
        activityError.value = cause instanceof Error ? cause.message : '加载账号活动失败';
      }
    } finally {
      if (requestToken === activityRequestToken) {
        activityLoading.value = false;
      }
    }
  }

  function focusAccount(account: AccountItem) {
    void loadAccountDetail(account.id);
  }

  function setAccountSelection(accountId: number, selected: boolean) {
    const next = new Set(selectedAccountIds.value);
    if (selected) {
      next.add(accountId);
    } else {
      next.delete(accountId);
    }
    selectedAccountIds.value = Array.from(next);
  }

  function toggleAccountSelection(accountId: number) {
    setAccountSelection(accountId, !selectedAccountIds.value.includes(accountId));
  }

  function selectVisibleAccounts() {
    selectedAccountIds.value = accounts.value.map((account) => account.id);
  }

  async function saveAccount() {
    if (saving.value) {
      return;
    }

    const payload = buildPayload();
    if (!payload.username) {
      actionError.value = '用户名不能为空';
      return;
    }

    saving.value = true;
    clearActionFeedback();
    const isEditing = editingAccountId.value !== null;

    try {
      const saved = isEditing
        ? await runtimeApi.updateAccount(editingAccountId.value as number, payload)
        : await runtimeApi.createAccount(payload);
      await refreshAccounts();
      const refreshed = accounts.value.find((account) => account.id === saved.id) || saved;
      beginEdit(refreshed);
      await loadAccountDetail(refreshed.id);
      actionMessage.value = isEditing ? `已更新账号：${saved.username}` : `已创建账号：${saved.username}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '保存账号失败';
    } finally {
      saving.value = false;
    }
  }

  async function testAccountConnection(account: AccountItem) {
    testingAccountId.value = account.id;
    clearActionFeedback();

    try {
      const result = await runtimeApi.testAccountConnection(account.id);
      const statusText = result.status || (result.ok ? 'reachable' : 'unknown');
      const latencyText = result.latencyMs ? `，延迟 ${result.latencyMs}ms` : '';
      const messageText = result.message ? `，${result.message}` : '';
      actionMessage.value = `账号 ${account.username} 测试连接完成：${statusText}${latencyText}${messageText}`;
      if (selectedAccountId.value === account.id) {
        await loadAccountDetail(account.id);
      }
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '测试连接失败';
    } finally {
      testingAccountId.value = null;
    }
  }

  async function archiveAccount(account: AccountLifecycleTarget) {
    archivingAccountId.value = account.id;
    clearActionFeedback();

    try {
      await runtimeApi.applyAccountLifecycle({
        accountId: account.id,
        action: 'archive',
        reason: lifecycleReason.value.trim() || undefined,
      });
      await refreshAccounts();
      if (selectedAccountId.value === account.id) {
        await loadAccountDetail(account.id);
      }
      actionMessage.value = `已归档账号：${account.username}${lifecycleReason.value.trim() ? `（原因：${lifecycleReason.value.trim()}）` : ''}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '归档账号失败';
    } finally {
      archivingAccountId.value = null;
    }
  }

  async function restoreAccount(account: AccountLifecycleTarget) {
    restoringAccountId.value = account.id;
    clearActionFeedback();

    try {
      await runtimeApi.applyAccountLifecycle({
        accountId: account.id,
        action: 'restore',
        reason: lifecycleReason.value.trim() || undefined,
      });
      await refreshAccounts();
      if (selectedAccountId.value === account.id) {
        await loadAccountDetail(account.id);
      }
      actionMessage.value = `已恢复账号：${account.username}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '恢复账号失败';
    } finally {
      restoringAccountId.value = null;
    }
  }

  async function suspendAccount(account: AccountLifecycleTarget) {
    suspendingAccountId.value = account.id;
    clearActionFeedback();

    try {
      await runtimeApi.applyAccountLifecycle({
        accountId: account.id,
        action: 'suspend',
        reason: lifecycleReason.value.trim() || undefined,
      });
      await refreshAccounts();
      if (selectedAccountId.value === account.id) {
        await loadAccountDetail(account.id);
      }
      actionMessage.value = `已停用账号：${account.username}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '停用账号失败';
    } finally {
      suspendingAccountId.value = null;
    }
  }

  async function deleteAccount(account: AccountLifecycleTarget) {
    deletingAccountId.value = account.id;
    clearActionFeedback();

    try {
      await runtimeApi.applyAccountLifecycle({
        accountId: account.id,
        action: 'delete',
        reason: lifecycleReason.value.trim() || undefined,
      });
      await refreshAccounts();
      if (selectedAccountId.value === account.id) {
        selectedAccountId.value = null;
        accountDetail.value = null;
        recentActivityItems.value = [];
      }
      selectedAccountIds.value = selectedAccountIds.value.filter((id) => id !== account.id);
      actionMessage.value = `已删除账号：${account.username}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '删除账号失败';
    } finally {
      deletingAccountId.value = null;
    }
  }

  async function runBulkAction(
    action: AccountBulkActionType,
    payload: Omit<AccountBulkActionPayload, 'accountIds' | 'action'>,
    successMessage: string,
  ) {
    const targetIds = [...selectedAccountIds.value];
    if (!targetIds.length) {
      actionError.value = '请先勾选至少一个账号';
      return;
    }

    bulkWorkingAction.value = action;
    clearActionFeedback();
    const detailTargetId = selectedAccountId.value;

    try {
      await runtimeApi.bulkUpdateAccounts({
        accountIds: targetIds,
        action,
        ...payload,
      });
      await refreshAccounts();
      clearSelectedAccounts();
      if (detailTargetId !== null && targetIds.includes(detailTargetId)) {
        await loadAccountDetail(detailTargetId);
      }
      actionMessage.value = successMessage;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '批量操作失败';
    } finally {
      bulkWorkingAction.value = '';
    }
  }

  async function bulkChangeManualStatus() {
    const manualStatus = normalizeStatus(bulkDraft.manualStatus, 'active');
    await runBulkAction('manual_status', { manualStatus }, `已批量更新 ${selectedAccountIds.value.length} 个账号的人工状态`);
  }

  async function bulkChangeRiskStatus() {
    const riskStatus = normalizeStatus(bulkDraft.riskStatus, 'unknown');
    await runBulkAction('risk_status', { riskStatus }, `已批量更新 ${selectedAccountIds.value.length} 个账号的风险状态`);
  }

  async function bulkChangeGroup() {
    const groupId = parseOptionalNumber(bulkDraft.groupId);
    const groupName = bulkDraft.groupName.trim() || null;
    if (groupId === null && !groupName) {
      actionError.value = '请填写分组 ID 或分组名称';
      return;
    }
    await runBulkAction('group', { groupId, groupName }, `已批量分组 ${selectedAccountIds.value.length} 个账号`);
  }

  async function bulkTestAccounts() {
    await runBulkAction('test', {}, `已批量检测 ${selectedAccountIds.value.length} 个账号`);
  }

  async function bulkArchiveAccounts() {
    await runBulkAction('archive', {}, `已批量归档 ${selectedAccountIds.value.length} 个账号`);
  }

  async function bulkUnarchiveAccounts() {
    await runBulkAction('unarchive', {}, `已批量取消归档 ${selectedAccountIds.value.length} 个账号`);
  }

  async function bulkSuspendAccounts() {
    await runBulkAction('suspend', { archiveReason: lifecycleReason.value.trim() || undefined }, `已批量停用 ${selectedAccountIds.value.length} 个账号`);
  }

  async function bulkRestoreAccounts() {
    await runBulkAction('restore', { archiveReason: lifecycleReason.value.trim() || undefined }, `已批量恢复 ${selectedAccountIds.value.length} 个账号`);
  }

  async function applyFilters() {
    await refreshAccounts();
  }

  async function clearFilters() {
    createDefaultFiltersState();
    await refreshAccounts();
  }

  function buildImportPayload(updateExisting: boolean): AccountImportPayload {
    return {
      content: importDraft.content,
      delimiter: importDraft.delimiter.trim() || ',',
      hasHeader: importDraft.hasHeader,
      updateExisting,
    };
  }

  async function previewAccountImport() {
    if (importLoading.value) {
      return;
    }

    importLoading.value = true;
    importError.value = '';
    importMessage.value = '';
    importApplyResult.value = null;

    try {
      importPreview.value = await runtimeApi.previewAccountImport(buildImportPayload(false));
      importMessage.value = '导入预检查完成';
    } catch (cause) {
      importPreview.value = null;
      importError.value = cause instanceof Error ? cause.message : '导入预检查失败';
    } finally {
      importLoading.value = false;
    }
  }

  async function applyAccountImport() {
    if (importApplying.value) {
      return;
    }
    importApplying.value = true;
    importError.value = '';
    importMessage.value = '';

    try {
      const result = await runtimeApi.applyAccountImport(buildImportPayload(importDraft.updateExisting));
      importApplyResult.value = result;
      importMessage.value = `导入完成：创建 ${result.created}，更新 ${result.updated}，跳过 ${result.skipped}，无效 ${result.invalid}`;
      await refreshAccounts();
      if (selectedAccountId.value !== null) {
        await loadAccountDetail(selectedAccountId.value);
      }
    } catch (cause) {
      importApplyResult.value = null;
      importError.value = cause instanceof Error ? cause.message : '执行导入失败';
    } finally {
      importApplying.value = false;
    }
  }

  const accounts = computed(() => resource.data.value?.items || []);
  const total = computed(() => resource.data.value?.total || 0);
  const visibleAccountCount = computed(() => accounts.value.length);
  const archivedCount = computed(() => accounts.value.filter((account) => account.isArchived).length);
  const selectedAccountCount = computed(() => selectedAccountIds.value.length);
  const allVisibleSelected = computed(() => accounts.value.length > 0 && accounts.value.every((account) => selectedAccountIds.value.includes(account.id)));
  const isEditing = computed(() => editingAccountId.value !== null);

  watch(accounts, (currentAccounts) => {
    const visibleIds = new Set(currentAccounts.map((account) => account.id));
    selectedAccountIds.value = selectedAccountIds.value.filter((accountId) => visibleIds.has(accountId));
  }, { immediate: true });

  return {
    ...resource,
    accounts,
    accountDetail,
    activityCategory,
    activityCategoryOptions: ACTIVITY_CATEGORY_OPTIONS,
    activityError,
    activityLimit,
    activityLoading,
    activityQuery,
    activitySeverity,
    activitySeverityOptions: ACTIVITY_SEVERITY_OPTIONS,
    actionError,
    actionMessage,
    allVisibleSelected,
    applyFilters,
    archiveAccount,
    archivedCount,
    archivingAccountId,
    beginEdit,
    bulkChangeGroup,
    bulkChangeManualStatus,
    bulkChangeRiskStatus,
    bulkDraft,
    bulkArchiveAccounts,
    bulkRestoreAccounts,
    bulkSuspendAccounts,
    bulkTestAccounts,
    bulkUnarchiveAccounts,
    bulkWorkingAction,
    importApplying,
    importApplyResult,
    importDraft,
    importError,
    importLoading,
    importMessage,
    importPreview,
    clearFilters,
    createDefaultImportDraftState,
    clearSelectedAccounts,
    detailError,
    detailLoading,
    draft,
    editingAccountId,
    filters,
    focusAccount,
    isEditing,
    lifecycleReason,
    loadAccountDetail,
    previewAccountImport,
    loadAccountActivity,
    manualStatusOptions: MANUAL_STATUS_OPTIONS,
    prepareCreate,
    refreshAccounts,
    riskStatusOptions: RISK_STATUS_OPTIONS,
    recentActivityItems,
    saveAccount,
    saving,
    selectVisibleAccounts,
    selectedAccountCount,
    selectedAccountId,
    selectedAccountIds,
    setAccountSelection,
    suspendingAccountId,
    suspendAccount,
    systemStatusOptions: SYSTEM_STATUS_OPTIONS,
    deletingAccountId,
    deleteAccount,
    testingAccountId,
    testAccountConnection,
    toggleAccountSelection,
    total,
    restoreAccount,
    restoringAccountId,
    visibleAccountCount,
    applyAccountImport,
  };
}

import { httpClient } from './httpClient';
import type {
  AccountLifecyclePayload,
  AccountLifecycleResult,
  AccountActivityListResponse,
  AccountBulkActionPayload,
  AccountBulkActionResult,
  AccountConnectionTestResult,
  AccountDetail,
  AccountImportApplyResult,
  AccountImportPayload,
  AccountImportPreviewResult,
  AccountItem,
  AccountListQuery,
  AccountUpsertPayload,
  CopywriterBootstrap,
  CreateSchedulePayload,
  CreateTaskPayload,
  DashboardOverview,
  LicenseStatus,
  MutationResult,
  ProviderItem,
  ProviderTestResult,
  ProviderUpsertPayload,
  RuntimeHealth,
  RuntimeNotificationItem,
  RuntimeListResponse,
  RuntimeSettingsPayload,
  RuntimeVersionCheck,
  RuntimeVersionCurrent,
  SchedulerOverview,
  ShellAssistantResponse,
  TaskItem,
} from './types';

function buildAccountQueryString(params: AccountListQuery = {}): string {
  const searchParams = new URLSearchParams();

  if (params.query?.trim()) {
    searchParams.set('query', params.query.trim());
  }
  if (params.manualStatus?.trim()) {
    searchParams.set('manual_status', params.manualStatus.trim());
  }
  if (params.systemStatus?.trim()) {
    searchParams.set('system_status', params.systemStatus.trim());
  }
  if (params.riskStatus?.trim()) {
    searchParams.set('risk_status', params.riskStatus.trim());
  }
  searchParams.set('include_archived', params.includeArchived ? 'true' : 'false');

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export const runtimeApi = {
  getCopywriterBootstrap(): Promise<CopywriterBootstrap> {
    return httpClient.get('/copywriter/bootstrap');
  },
  getHealth(): Promise<RuntimeHealth> {
    return httpClient.get('/health');
  },
  getLicenseStatus(): Promise<LicenseStatus> {
    return httpClient.get('/license/status');
  },
  getDashboardOverview(range: 'today' | '7d' | '30d' = 'today'): Promise<DashboardOverview> {
    return httpClient.get(`/dashboard/overview?range=${encodeURIComponent(range)}`);
  },
  listNotifications(limit = 20): Promise<RuntimeNotificationItem[]> {
    return httpClient.get(`/notifications?limit=${encodeURIComponent(String(limit))}`);
  },
  getVersionCurrent(): Promise<RuntimeVersionCurrent> {
    return httpClient.get('/version/current');
  },
  checkVersion(): Promise<RuntimeVersionCheck> {
    return httpClient.get('/version/check');
  },
  askShellAssistant(payload: {
    message: string;
    context: Record<string, unknown>;
    history: Array<{ role: 'user' | 'assistant'; content: string }>;
  }): Promise<ShellAssistantResponse> {
    return httpClient.post('/assistant/chat', payload);
  },
  listAccounts(params?: AccountListQuery): Promise<RuntimeListResponse<AccountItem>> {
    return httpClient.get(`/accounts${buildAccountQueryString(params)}`);
  },
  getAccountDetail(accountId: number): Promise<AccountDetail> {
    return httpClient.get(`/accounts/${accountId}`);
  },
  getAccountActivity(
    accountId: number,
    params: {
      limit?: number;
      query?: string;
      category?: string;
      severity?: string;
    } = {},
  ): Promise<AccountActivityListResponse> {
    const limit = params.limit ?? 50;
    const normalizedLimit = Math.max(1, Math.min(Math.trunc(limit), 100));
    const searchParams = new URLSearchParams();
    searchParams.set('limit', String(normalizedLimit));
    if (params.query?.trim()) {
      searchParams.set('query', params.query.trim());
    }
    if (params.category?.trim()) {
      searchParams.set('category', params.category.trim());
    }
    if (params.severity?.trim()) {
      searchParams.set('severity', params.severity.trim());
    }
    return httpClient.get(`/accounts/${accountId}/activity?${searchParams.toString()}`);
  },
  previewAccountImport(payload: AccountImportPayload): Promise<AccountImportPreviewResult> {
    return httpClient.post('/accounts/import/preview', payload);
  },
  applyAccountImport(payload: AccountImportPayload): Promise<AccountImportApplyResult> {
    return httpClient.post('/accounts/import/apply', payload);
  },
  createAccount(payload: AccountUpsertPayload): Promise<AccountItem> {
    return httpClient.post('/accounts', payload);
  },
  updateAccount(accountId: number, payload: AccountUpsertPayload): Promise<AccountItem> {
    return httpClient.put(`/accounts/${accountId}`, payload);
  },
  bulkUpdateAccounts(payload: AccountBulkActionPayload): Promise<AccountBulkActionResult> {
    return httpClient.post('/accounts/bulk', payload);
  },
  archiveAccount(accountId: number, reason?: string | null): Promise<MutationResult> {
    return httpClient.post(`/accounts/${accountId}/archive`, reason ? { reason } : {});
  },
  unarchiveAccount(accountId: number): Promise<MutationResult> {
    return httpClient.post(`/accounts/${accountId}/unarchive`);
  },
  applyAccountLifecycle(payload: { accountId: number; action: AccountLifecyclePayload['action']; reason?: string | null }): Promise<AccountLifecycleResult> {
    return httpClient.post(`/accounts/${payload.accountId}/lifecycle`, {
      action: payload.action,
      reason: payload.reason ?? null,
    });
  },
  deleteAccount(accountId: number): Promise<MutationResult> {
    return httpClient.delete(`/accounts/${accountId}`);
  },
  testAccountConnection(accountId: number): Promise<AccountConnectionTestResult> {
    return httpClient.post(`/accounts/${accountId}/test`);
  },
  listTasks(status?: string): Promise<RuntimeListResponse<TaskItem>> {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return httpClient.get(`/tasks${query}`);
  },
  createTask(payload: CreateTaskPayload): Promise<TaskItem> {
    return httpClient.post('/tasks', payload);
  },
  startTask(taskId: number): Promise<TaskItem> {
    return httpClient.post(`/tasks/${taskId}/start`);
  },
  deleteTask(taskId: number): Promise<MutationResult> {
    return httpClient.delete(`/tasks/${taskId}`);
  },
  getSchedulerOverview(): Promise<SchedulerOverview> {
    return httpClient.get('/scheduler');
  },
  createSchedule(payload: CreateSchedulePayload): Promise<TaskItem> {
    return httpClient.post('/scheduler', payload);
  },
  toggleSchedule(taskId: number): Promise<TaskItem> {
    return httpClient.post(`/scheduler/${taskId}/toggle`);
  },
  deleteSchedule(taskId: number): Promise<MutationResult> {
    return httpClient.delete(`/scheduler/${taskId}`);
  },
  listProviders(): Promise<RuntimeListResponse<ProviderItem>> {
    return httpClient.get('/providers');
  },
  createProvider(payload: ProviderUpsertPayload): Promise<ProviderItem> {
    return httpClient.post('/providers', payload);
  },
  updateProvider(providerId: number, payload: ProviderUpsertPayload): Promise<ProviderItem> {
    return httpClient.put(`/providers/${providerId}`, payload);
  },
  activateProvider(providerId: number): Promise<ProviderItem> {
    return httpClient.post(`/providers/${providerId}/activate`);
  },
  testProvider(providerId: number): Promise<ProviderTestResult> {
    return httpClient.post(`/providers/${providerId}/test`);
  },
  deleteProvider(providerId: number): Promise<MutationResult> {
    return httpClient.delete(`/providers/${providerId}`);
  },
  getSettings(): Promise<RuntimeSettingsPayload> {
    return httpClient.get('/settings');
  },
  saveSettings(payload: {
    theme: string;
    language: string;
    proxyUrl: string;
    timeoutSeconds: number;
    concurrency: number;
  }): Promise<RuntimeSettingsPayload> {
    return httpClient.post('/settings', payload);
  },
  saveSetup(payload: {
    defaultMarket: string;
    workflow: string;
    model: string;
    completed: boolean;
  }): Promise<RuntimeSettingsPayload> {
    return httpClient.post('/settings/setup', payload);
  },
};

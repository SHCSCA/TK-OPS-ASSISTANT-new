import { httpClient } from './httpClient';
import type {
  AccountBulkActionPayload,
  AccountBulkActionResult,
  AccountConnectionTestResult,
  AccountDetail,
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
  RuntimeListResponse,
  RuntimeSettingsPayload,
  SchedulerOverview,
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
  getDashboardOverview(): Promise<DashboardOverview> {
    return httpClient.get('/dashboard/overview');
  },
  listAccounts(params?: AccountListQuery): Promise<RuntimeListResponse<AccountItem>> {
    return httpClient.get(`/accounts${buildAccountQueryString(params)}`);
  },
  getAccountDetail(accountId: number): Promise<AccountDetail> {
    return httpClient.get(`/accounts/${accountId}`);
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
  archiveAccount(accountId: number): Promise<MutationResult> {
    return httpClient.post(`/accounts/${accountId}/archive`);
  },
  unarchiveAccount(accountId: number): Promise<MutationResult> {
    return httpClient.post(`/accounts/${accountId}/unarchive`);
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

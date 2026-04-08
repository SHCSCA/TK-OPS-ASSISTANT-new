import { httpClient } from './httpClient';
import type {
  AccountLifecyclePayload,
  AccountLifecycleResult,
  AccountActivityListResponse,
  AccountBulkActionPayload,
  AccountBulkActionResult,
  AccountConnectionTestResult,
  AccountEnvironmentOpenResult,
  AccountLoginValidationResult,
  AccountDetail,
  AccountImportApplyResult,
  AccountImportPayload,
  AccountImportPreviewResult,
  AccountItem,
  AccountListQuery,
  AccountProxyBindingSnapshot,
  AccountProxyBindingUpdateResult,
  AccountUpsertPayload,
  ActivityLogCreatePayload,
  ActivityLogItem,
  CopywriterBootstrap,
  CreateSchedulePayload,
  CreateTaskPayload,
  DashboardOverview,
  DeviceEnvironmentOpenResult,
  DeviceInspectionResult,
  DeviceItem,
  DeviceLogsResponse,
  DeviceRepairResult,
  DeviceUpsertPayload,
  ExperimentProjectCreatePayload,
  ExperimentProjectItem,
  ExperimentViewCreatePayload,
  ExperimentViewItem,
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
  WorkflowDefinitionCreatePayload,
  WorkflowDefinitionItem,
  WorkflowRunCreatePayload,
  WorkflowRunItem,
  VideoClipAppendPayload,
  VideoClipItem,
  VideoClipPatchPayload,
  VideoClipReorderPayload,
  VideoClipTrimPayload,
  VideoExportCreatePayload,
  VideoExportItem,
  VideoProjectCreatePayload,
  VideoProjectItem,
  VideoSequenceCreatePayload,
  VideoSequenceItem,
  VideoSnapshotCreatePayload,
  VideoSnapshotItem,
  VideoSubtitleCreatePayload,
  VideoSubtitleItem,
  VideoSubtitlePatchPayload,
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
  openAccountEnvironment(accountId: number): Promise<AccountEnvironmentOpenResult> {
    return httpClient.post(`/accounts/${accountId}/environment/open`);
  },
  validateAccountLogin(accountId: number): Promise<AccountLoginValidationResult> {
    return httpClient.post(`/accounts/${accountId}/login/validate`);
  },
  getAccountProxyBinding(accountId: number): Promise<AccountProxyBindingSnapshot> {
    return httpClient.get(`/accounts/${accountId}/proxy-binding`);
  },
  updateAccountProxyBinding(
    accountId: number,
    payload: {
      deviceId?: number | null;
      proxyIp?: string | null;
      region?: string | null;
      validateAfterSave?: boolean;
    },
  ): Promise<AccountProxyBindingUpdateResult> {
    return httpClient.post(`/accounts/${accountId}/proxy-binding`, payload);
  },
  listDevices(status?: string): Promise<RuntimeListResponse<DeviceItem>> {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return httpClient.get(`/devices${query}`);
  },
  createDevice(payload: DeviceUpsertPayload): Promise<DeviceItem> {
    return httpClient.post('/devices', payload);
  },
  updateDevice(deviceId: number, payload: DeviceUpsertPayload): Promise<DeviceItem> {
    return httpClient.put(`/devices/${deviceId}`, payload);
  },
  deleteDevice(deviceId: number): Promise<MutationResult> {
    return httpClient.delete(`/devices/${deviceId}`);
  },
  inspectDevice(deviceId: number): Promise<DeviceInspectionResult> {
    return httpClient.post(`/devices/${deviceId}/inspect`);
  },
  repairDevice(deviceId: number): Promise<DeviceRepairResult> {
    return httpClient.post(`/devices/${deviceId}/repair`);
  },
  openDeviceEnvironment(deviceId: number): Promise<DeviceEnvironmentOpenResult> {
    return httpClient.post(`/devices/${deviceId}/environment/open`);
  },
  getDeviceLogs(deviceId: number, limit = 20): Promise<DeviceLogsResponse> {
    return httpClient.get(`/devices/${deviceId}/logs?limit=${encodeURIComponent(String(limit))}`);
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
  listExperimentProjects(): Promise<RuntimeListResponse<ExperimentProjectItem>> {
    return httpClient.get('/experiments/projects');
  },
  createExperimentProject(payload: ExperimentProjectCreatePayload): Promise<ExperimentProjectItem> {
    return httpClient.post('/experiments/projects', payload);
  },
  listExperimentViews(projectId?: number): Promise<RuntimeListResponse<ExperimentViewItem>> {
    const query = typeof projectId === 'number' ? `?projectId=${encodeURIComponent(String(projectId))}` : '';
    return httpClient.get(`/experiments/views${query}`);
  },
  createExperimentView(payload: ExperimentViewCreatePayload): Promise<ExperimentViewItem> {
    return httpClient.post('/experiments/views', payload);
  },
  listActivityLogs(limit = 20, category?: string): Promise<RuntimeListResponse<ActivityLogItem>> {
    const searchParams = new URLSearchParams();
    searchParams.set('limit', String(limit));
    if (category?.trim()) {
      searchParams.set('category', category.trim());
    }
    return httpClient.get(`/activity/logs?${searchParams.toString()}`);
  },
  createActivityLog(payload: ActivityLogCreatePayload): Promise<ActivityLogItem> {
    return httpClient.post('/activity/logs', payload);
  },
  listWorkflowDefinitions(): Promise<RuntimeListResponse<WorkflowDefinitionItem>> {
    return httpClient.get('/workflows/definitions');
  },
  createWorkflowDefinition(payload: WorkflowDefinitionCreatePayload): Promise<WorkflowDefinitionItem> {
    return httpClient.post('/workflows/definitions', payload);
  },
  listWorkflowRuns(definitionId?: number): Promise<RuntimeListResponse<WorkflowRunItem>> {
    const query = typeof definitionId === 'number' ? `?definitionId=${encodeURIComponent(String(definitionId))}` : '';
    return httpClient.get(`/workflows/runs${query}`);
  },
  startWorkflowRun(payload: WorkflowRunCreatePayload): Promise<WorkflowRunItem> {
    return httpClient.post('/workflows/runs', payload);
  },
  listVideoProjects(): Promise<RuntimeListResponse<VideoProjectItem>> {
    return httpClient.get('/video-editor/projects');
  },
  createVideoProject(payload: VideoProjectCreatePayload): Promise<VideoProjectItem> {
    return httpClient.post('/video-editor/projects', payload);
  },
  listVideoSequences(projectId: number): Promise<RuntimeListResponse<VideoSequenceItem>> {
    return httpClient.get(`/video-editor/projects/${projectId}/sequences`);
  },
  createVideoSequence(payload: VideoSequenceCreatePayload): Promise<VideoSequenceItem> {
    return httpClient.post('/video-editor/sequences', payload);
  },
  setActiveVideoSequence(projectId: number, sequenceId: number): Promise<VideoSequenceItem> {
    return httpClient.post('/video-editor/sequences/activate', { projectId, sequenceId });
  },
  listVideoClips(sequenceId: number): Promise<RuntimeListResponse<VideoClipItem>> {
    return httpClient.get(`/video-editor/sequences/${sequenceId}/clips`);
  },
  appendAssetsToSequence(sequenceId: number, payload: VideoClipAppendPayload): Promise<RuntimeListResponse<VideoClipItem>> {
    return httpClient.post(`/video-editor/sequences/${sequenceId}/assets`, payload);
  },
  reorderVideoClips(payload: VideoClipReorderPayload): Promise<RuntimeListResponse<VideoClipItem>> {
    return httpClient.post('/video-editor/clips/reorder', payload);
  },
  updateVideoClip(clipId: number, payload: VideoClipPatchPayload): Promise<VideoClipItem> {
    return httpClient.put(`/video-editor/clips/${clipId}`, payload);
  },
  trimVideoClip(payload: VideoClipTrimPayload): Promise<VideoClipItem> {
    return httpClient.post('/video-editor/clips/trim', payload);
  },
  deleteVideoClip(clipId: number): Promise<MutationResult> {
    return httpClient.delete(`/video-editor/clips/${clipId}`);
  },
  listVideoSubtitles(sequenceId: number): Promise<RuntimeListResponse<VideoSubtitleItem>> {
    return httpClient.get(`/video-editor/sequences/${sequenceId}/subtitles`);
  },
  createVideoSubtitle(payload: VideoSubtitleCreatePayload): Promise<VideoSubtitleItem> {
    return httpClient.post('/video-editor/subtitles', payload);
  },
  updateVideoSubtitle(subtitleId: number, payload: VideoSubtitlePatchPayload): Promise<VideoSubtitleItem> {
    return httpClient.put(`/video-editor/subtitles/${subtitleId}`, payload);
  },
  deleteVideoSubtitle(subtitleId: number): Promise<MutationResult> {
    return httpClient.delete(`/video-editor/subtitles/${subtitleId}`);
  },
  listVideoExports(projectId: number): Promise<RuntimeListResponse<VideoExportItem>> {
    return httpClient.get(`/video-editor/projects/${projectId}/exports`);
  },
  createVideoExport(payload: VideoExportCreatePayload): Promise<VideoExportItem> {
    return httpClient.post('/video-editor/exports', payload);
  },
  runVideoExport(exportId: number): Promise<VideoExportItem> {
    return httpClient.post(`/video-editor/exports/${exportId}/run`);
  },
  listVideoSnapshots(projectId: number): Promise<RuntimeListResponse<VideoSnapshotItem>> {
    return httpClient.get(`/video-editor/projects/${projectId}/snapshots`);
  },
  createVideoSnapshot(payload: VideoSnapshotCreatePayload): Promise<VideoSnapshotItem> {
    return httpClient.post('/video-editor/snapshots', payload);
  },
  restoreVideoSnapshot(snapshotId: number): Promise<VideoProjectItem> {
    return httpClient.post(`/video-editor/snapshots/${snapshotId}/restore`);
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
  // 素材管理
  listAssets(params?: { asset_type?: string; query?: string }): Promise<{ items: any[]; total: number }> {
    const searchParams = new URLSearchParams();
    if (params?.asset_type) searchParams.set('asset_type', params.asset_type);
    if (params?.query) searchParams.set('query', params.query);
    const query = searchParams.toString();
    return httpClient.get(`/assets${query ? `?${query}` : ''}`);
  },
  getAssetStats(): Promise<{ total: number; byType: Record<string, number> }> {
    return httpClient.get('/assets/stats');
  },
  getAsset(id: number): Promise<any> {
    return httpClient.get(`/assets/${id}`);
  },
  createAsset(payload: {
    filename: string;
    asset_type: string;
    file_path: string;
    tags?: string | null;
    account_id?: number | null;
  }): Promise<any> {
    return httpClient.post('/assets', payload);
  },
  updateAsset(id: number, payload: {
    filename?: string | null;
    asset_type?: string | null;
    file_path?: string | null;
    tags?: string | null;
    account_id?: number | null;
  }): Promise<any> {
    return httpClient.put(`/assets/${id}`, payload);
  },
  deleteAsset(id: number): Promise<{ deleted: boolean }> {
    return httpClient.delete(`/assets/${id}`);
  },
};

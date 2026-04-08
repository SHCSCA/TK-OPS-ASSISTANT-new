export interface RuntimeEnvelope<T> {
  ok: boolean;
  data: T;
  error?: string | {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
    retryable?: boolean;
  };
}

export interface RuntimeHealth {
  status: string;
  version: string;
  dbPath: string;
  dataDir: string;
  host: string;
  port: number;
  environment: string;
  logLevel: string;
  logFile: string;
}

export interface UsageSnapshot {
  prompt: number;
  completion: number;
  requests: number;
}

export interface UsageStats {
  total: UsageSnapshot;
  daily?: Record<string, UsageSnapshot>;
  by_provider?: Record<string, UsageSnapshot>;
  by_model?: Record<string, UsageSnapshot>;
}

export interface CopywriterPreset {
  key: string;
  name: string;
  icon: string;
  system: string;
}

export interface CopywriterBootstrap {
  presets: CopywriterPreset[];
  defaultPreset: string;
  activePreset: CopywriterPreset | null;
  providers: ProviderItem[];
  activeProvider: ProviderItem | null;
  usageToday: UsageSnapshot;
  usageStats: UsageStats;
}

export interface CopywriterStreamRequest {
  prompt: string;
  preset: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface AiStreamDeltaEvent {
  type: 'ai.stream.delta';
  payload: {
    delta: string;
  };
}

export interface AiStreamDoneEvent {
  type: 'ai.stream.done';
  payload: {
    delta: string;
    content: string;
    model: string;
    provider: string;
    tokens: {
      prompt: number;
      completion: number;
      total: number;
    };
    elapsedMs: number;
  };
}

export interface AiStreamErrorEvent {
  type: 'ai.stream.error';
  payload: {
    message: string;
  };
}

export type CopywriterStreamEvent = AiStreamDeltaEvent | AiStreamDoneEvent | AiStreamErrorEvent;

export interface LicenseStatus {
  activated: boolean;
  machineId: string;
  machineIdShort: string;
  compoundId: string;
  tier: string | null;
  expiry: string | null;
  daysRemaining: number | null;
  isPermanent: boolean;
  error: string | null;
}

export interface AccountActivitySummaryItem {
  id?: number;
  category?: string;
  severity?: 'info' | 'success' | 'warning' | 'error';
  title: string;
  summary: string;
  reason?: string | null;
  entityType?: string | null;
  entityId?: number | null;
  occurredAt: string | null;
}

export interface AccountListQuery {
  query?: string;
  manualStatus?: string;
  systemStatus?: string;
  riskStatus?: string;
  includeArchived?: boolean;
}

export interface AccountItem {
  id: number;
  username: string;
  platform: string;
  region: string;
  status: string;
  manualStatus: string | null;
  systemStatus: string | null;
  riskStatus: string | null;
  followers: number;
  groupId: number | null;
  groupName: string | null;
  deviceId: number | null;
  deviceName: string | null;
  proxyIp?: string | null;
  cookieStatus: string;
  boundEnvironment: string | null;
  recentError: string | null;
  activitySummary?: AccountActivitySummaryItem[];
  isArchived: boolean;
  archivedAt: string | null;
  lastConnectionStatus: string;
  lastConnectionMessage: string | null;
  lastConnectionCheckedAt?: string | null;
  lastLoginAt?: string | null;
  lastLoginCheckStatus?: string | null;
  lastLoginCheckAt?: string | null;
  lastLoginCheckMessage?: string | null;
  cookieContent?: string | null;
  cookieUpdatedAt?: string | null;
  isolationEnabled?: boolean;
  archivedReason?: string | null;
  notes?: string | null;
  tags?: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface AccountDetail extends AccountItem {
  activitySummary: AccountActivitySummaryItem[];
}

export interface AccountActivityListResponse {
  accountId: number;
  items: AccountActivitySummaryItem[];
  total: number;
  limit: number;
  filters?: {
    query: string;
    category: string;
    severity: string;
  };
}

export interface AccountImportPayload {
  content: string;
  delimiter?: string;
  hasHeader?: boolean;
  updateExisting?: boolean;
}

export interface AccountImportPreviewItem {
  line: number;
  username: string;
  action: 'create' | 'update' | 'invalid';
  valid: boolean;
  reason: string;
  existingAccountId: number | null;
}

export interface AccountImportPreviewResult {
  total: number;
  valid: number;
  invalid: number;
  create: number;
  update: number;
  items: AccountImportPreviewItem[];
}

export interface AccountImportApplyItem {
  line: number;
  username: string;
  status: 'created' | 'updated' | 'skipped' | 'invalid';
  message: string;
}

export interface AccountImportApplyResult {
  total: number;
  created: number;
  updated: number;
  skipped: number;
  invalid: number;
  updateExisting: boolean;
  items: AccountImportApplyItem[];
}

export type AccountLifecycleActionType = 'suspend' | 'archive' | 'restore' | 'delete';

export interface AccountLifecyclePayload {
  action: AccountLifecycleActionType;
  reason?: string | null;
}

export interface AccountLifecycleResult {
  deleted?: boolean;
  accountId: number;
  manualStatus?: string;
  archived?: boolean;
  archiveReason?: string | null;
}

export interface AccountUpsertPayload {
  username: string;
  platform: string;
  region: string;
  status: string;
  manualStatus?: string;
  riskStatus?: string;
  followers: number;
  groupId?: number | null;
  groupName?: string | null;
  deviceId?: number | null;
  cookieStatus?: string;
  cookieContent?: string | null;
  isolationEnabled?: boolean;
  lastConnectionStatus?: string;
  lastConnectionMessage?: string | null;
  notes?: string | null;
  tags?: string | null;
}

export type AccountBulkActionType =
  | 'manual_status'
  | 'risk_status'
  | 'group'
  | 'test'
  | 'archive'
  | 'unarchive'
  | 'suspend'
  | 'restore';

export interface AccountBulkActionPayload {
  accountIds: number[];
  action: AccountBulkActionType;
  manualStatus?: string;
  riskStatus?: string;
  groupId?: number | null;
  groupName?: string | null;
  archiveReason?: string | null;
}

export interface AccountBulkActionResult {
  message?: string;
  updatedCount?: number;
  affectedAccountIds?: number[];
  action?: AccountBulkActionType;
}

export interface AccountConnectionTestResult {
  ok: boolean;
  accountId?: number;
  username?: string;
  target?: string;
  latencyMs?: number | null;
  checkedAt?: string | null;
  message?: string;
  scope?: string;
  scopeLabel?: string;
  cookieStatus?: string;
  isolationEnabled?: boolean;
  deviceStatus?: string;
  proxyStatus?: string;
  status?: string;
}

export interface AccountEnvironmentOpenResult {
  accountId: number;
  accountUsername: string;
  deviceId: number;
  deviceCode: string;
  deviceName: string;
  browserPath: string;
  profileDir: string;
  extensionDir: string;
  extensionName: string;
  extensionReady: boolean;
  extensionInstallRequired: boolean;
  extensionInstallHint: string;
  proxyServer: string;
  browserProxy: string;
  upstreamProxy: string;
  pid: number;
  url: string;
  cookieCount: number;
  validation: {
    ok: boolean;
    message: string;
    detail: string;
  };
}

export interface AccountLoginValidationResult {
  accountId: number;
  username: string;
  status: string;
  label: string;
  message: string;
  checkedAt: string | null;
  platform: string;
  target: string;
  httpStatus: number | null;
  viaProxy: boolean;
  cookieStatus: string;
}

export interface AccountProxyBindingDeviceSnapshot {
  id: number;
  deviceCode: string;
  name: string;
  region: string;
  proxyIp: string | null;
  status: string;
  proxyStatus: string;
  fingerprintStatus: string;
}

export interface AccountProxyBindingSnapshot {
  accountId: number;
  accountUsername: string;
  boundDeviceId: number | null;
  boundDeviceName: string | null;
  proxyIp: string | null;
  region: string | null;
  status: string | null;
  availableDevices: AccountProxyBindingDeviceSnapshot[];
}

export interface AccountProxyBindingUpdateResult extends AccountProxyBindingSnapshot {
  validation: AccountLoginValidationResult | null;
}

export interface DeviceItem {
  id: number;
  deviceCode: string;
  name: string;
  proxyIp: string | null;
  region: string;
  status: string;
  proxyStatus: string;
  fingerprintStatus: string;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface DeviceUpsertPayload {
  deviceCode?: string;
  name?: string;
  proxyIp?: string | null;
  region?: string;
  status?: string;
  proxyStatus?: string | null;
  fingerprintStatus?: string | null;
}

export interface DeviceInspectionResult {
  deviceId: number;
  deviceCode: string;
  name: string;
  ok: boolean;
  target: string | null;
  latencyMs: number | null;
  checkedAt: string | null;
  message: string;
  scope: string | null;
  scopeLabel: string | null;
  status: string;
  proxyStatus: string;
  fingerprintStatus: string;
  boundAccounts: number;
}

export interface DeviceRepairResult {
  deviceId: number;
  deviceCode: string;
  status: string;
  proxyStatus: string;
  profileDir: string;
  actions: string[];
  inspection: DeviceInspectionResult;
}

export interface DeviceEnvironmentOpenResult {
  deviceId: number;
  deviceCode: string;
  name: string;
  browserPath: string;
  profileDir: string;
  launcherPath: string;
  launcherUrl: string;
  configuredProxy: string;
  configuredProxyDisplay: string;
  upstreamProxy: string;
  upstreamTransport: string;
  browserProxy: string;
  proxyServer: string;
  proxyAuthPresent: boolean;
  validation: {
    ok: boolean;
    message: string;
    detail: string;
  };
  launchMode: string;
  pid: number;
  url: string;
  autoOpenDelayMs: number;
  monitorIntervalMs: number;
  proxyProbeUrl: string;
  extensionName: string;
  extensionReady: boolean;
  extensionInstallRequired: boolean;
  extensionInstallHint: string;
}

export interface DeviceLogItem {
  id: number;
  category: string;
  title: string;
  message: string;
  payload: Record<string, unknown>;
  createdAt: string | null;
}

export interface DeviceLogsResponse {
  items: DeviceLogItem[];
  total: number;
  limit: number;
}

export interface RuntimeListResponse<T> {
  items: T[];
  total: number;
}

export interface MutationResult {
  deleted?: boolean;
  accountId?: number;
  deviceId?: number;
  taskId?: number;
  providerId?: number;
}

export interface DashboardMetric {
  key: string;
  label: string;
  value: number;
  meta: string;
}

export interface DashboardBucket {
  key: string;
  count: number;
}

export interface DashboardTrendItem {
  label: string;
  created: number;
  completed: number;
  failed: number;
}

export interface DashboardActivityItem {
  title: string;
  entity: string;
  category: string;
  status: string;
  time: string;
}

export type DashboardSystemTone = 'success' | 'warning' | 'error' | 'info';

export interface DashboardSystemItem {
  key: string;
  title: string;
  status: string;
  tone: DashboardSystemTone;
  summary: string;
}

export interface TaskItem {
  id: number;
  title: string;
  taskType: string;
  priority: string;
  status: string;
  accountId: number | null;
  accountUsername: string | null;
  scheduledAt: string | null;
  startedAt: string | null;
  finishedAt: string | null;
  resultSummary: string | null;
  createdAt: string | null;
}

export interface ExperimentProjectItem {
  id: number;
  name: string;
  goal: string | null;
  status: string;
  configJson: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface ExperimentViewItem {
  id: number;
  experimentProjectId: number;
  name: string;
  layoutJson: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface ActivityLogItem {
  id: number;
  category: string;
  title: string;
  payloadJson: string | null;
  relatedEntityType: string | null;
  relatedEntityId: number | null;
  createdAt: string | null;
}

export interface CreateTaskPayload {
  title: string;
  taskType: string;
  priority: string;
  accountId?: number | null;
  scheduledAt?: string | null;
  resultSummary?: string | null;
}

export interface ExperimentProjectCreatePayload {
  name: string;
  goal?: string | null;
  status?: string;
  configJson?: string | null;
}

export interface ExperimentViewCreatePayload {
  experimentProjectId: number;
  name: string;
  layoutJson?: string | null;
}

export interface ActivityLogCreatePayload {
  category: string;
  title: string;
  payloadJson?: string | null;
  relatedEntityType?: string | null;
  relatedEntityId?: number | null;
}

export interface WorkflowDefinitionItem {
  id: number;
  name: string;
  status: string;
  description: string | null;
  configJson: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface WorkflowRunItem {
  id: number;
  workflowDefinitionId: number;
  status: string;
  inputJson: string | null;
  resultJson: string | null;
  startedAt: string | null;
  finishedAt: string | null;
  createdAt: string | null;
}

export interface WorkflowDefinitionCreatePayload {
  name: string;
  status?: string;
  description?: string | null;
  configJson?: string | null;
}

export interface WorkflowRunCreatePayload {
  workflowDefinitionId: number;
  status?: string;
  inputJson?: string | null;
  resultJson?: string | null;
}

export interface VideoProjectItem {
  id: number;
  name: string;
  description: string | null;
  activeSequenceId: number | null;
  metaJson: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface VideoSequenceItem {
  id: number;
  projectId: number;
  name: string;
  durationMs: number;
  fps: number;
  width: number;
  height: number;
  metaJson: string | null;
  isActive: boolean;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface VideoClipItem {
  id: number;
  sequenceId: number;
  assetId: number | null;
  trackType: string;
  trackIndex: number;
  sortOrder: number;
  startMs: number;
  sourceInMs: number;
  sourceOutMs: number;
  durationMs: number;
  speed: number;
  volume: number;
  metaJson: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface VideoSubtitleItem {
  id: number;
  sequenceId: number;
  startMs: number;
  endMs: number;
  text: string;
  styleJson: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface VideoExportItem {
  id: number;
  projectId: number;
  sequenceId: number | null;
  preset: string;
  status: string;
  outputPath: string | null;
  ffmpegCommand: string | null;
  errorMessage: string | null;
  progress: number;
  startedAt: string | null;
  finishedAt: string | null;
  createdAt: string | null;
}

export interface VideoSnapshotItem {
  id: number;
  projectId: number;
  title: string;
  createdAt: string | null;
}

export interface VideoProjectCreatePayload {
  name: string;
  description?: string | null;
  metaJson?: string | null;
}

export interface VideoSequenceCreatePayload {
  projectId: number;
  name: string;
  fps?: number;
  width?: number;
  height?: number;
  metaJson?: string | null;
}

export interface VideoClipAppendPayload {
  assetIds?: number[];
  assetId?: number | null;
}

export interface VideoClipReorderPayload {
  sequenceId: number;
  clipIds: number[];
}

export interface VideoClipPatchPayload {
  sourceInMs?: number;
  sourceOutMs?: number;
  volume?: number;
  speed?: number;
}

export interface VideoClipTrimPayload {
  clipId: number;
  sourceInMs: number;
  sourceOutMs: number;
}

export interface VideoSubtitleCreatePayload {
  sequenceId: number;
  startMs: number;
  endMs: number;
  text: string;
  styleJson?: string | null;
}

export interface VideoSubtitlePatchPayload {
  startMs?: number;
  endMs?: number;
  text?: string;
  styleJson?: string | null;
}

export interface VideoExportCreatePayload {
  projectId: number;
  sequenceId: number;
  preset?: string;
}

export interface VideoSnapshotCreatePayload {
  projectId: number;
  title: string;
}

export interface ProviderItem {
  id: number;
  name: string;
  providerType: string;
  apiBase: string;
  defaultModel: string;
  temperature: number;
  maxTokens: number;
  isActive: boolean;
  createdAt: string | null;
}

export interface ProviderUpsertPayload {
  name: string;
  providerType: string;
  apiBase: string;
  defaultModel: string;
  temperature: number;
  maxTokens: number;
  isActive: boolean;
}

export interface ProviderTestResult {
  ok: boolean;
  provider: string;
  model: string;
  latencyMs: number;
}

export interface SettingItem {
  key: string;
  value: string;
}

export interface SettingsPreferences {
  theme: string;
  language: string;
  proxyUrl: string;
  timeoutSeconds: number;
  concurrency: number;
}

export interface SettingsSetupState {
  defaultMarket: string;
  defaultWorkflow: string;
  defaultModel: string;
  completed: boolean;
}

export interface RuntimeSettingsPayload {
  values: Record<string, string>;
  items: SettingItem[];
  theme: string;
  total: number;
  preferences: SettingsPreferences;
  setup: SettingsSetupState;
  savedKeys?: string[];
  message?: string;
}

export interface RuntimeNotificationItem {
  id: string;
  title: string;
  body: string;
  tone: 'info' | 'success' | 'warning' | 'error';
  createdAt: string;
  source: string;
  read?: boolean;
}

export interface RuntimeVersionCurrent {
  version: string;
}

export interface RuntimeVersionCheck {
  hasUpdate: boolean;
  state?: 'latest' | 'available' | 'error';
  current: string;
  latest?: string;
  tag?: string;
  downloadUrl?: string;
  htmlUrl?: string;
  releaseNotes?: string;
  assetName?: string;
  assetSize?: number;
}

export interface ShellAssistantAction {
  id: string;
  label: string;
  action: string;
  payload?: Record<string, unknown>;
}

export interface ShellAssistantResponse {
  answer: string;
  source: 'model' | 'fallback';
  suggestions: ShellAssistantAction[];
  model?: string;
  provider?: string;
  elapsedMs?: number;
  error?: string;
  contextEcho?: Record<string, unknown>;
}

export interface SchedulerTaskItem {
  id: number;
  title: string;
  taskType: string;
  status: string;
  priority: string;
  scheduledAt: string | null;
  accountUsername: string | null;
  resultSummary: string | null;
}

export interface SchedulerOverview {
  generatedAt: string;
  summary: {
    total: number;
    scheduled: number;
    running: number;
    failed: number;
  };
  windows: {
    quietHours: string;
    timezone: string;
    defaultWorkflow: string;
  };
  items: SchedulerTaskItem[];
}

export interface CreateSchedulePayload {
  title: string;
  taskType: string;
  priority: string;
  scheduledAt: string;
  accountId?: number | null;
  resultSummary?: string | null;
}

export interface DashboardOverview {
  generatedAt: string;
  range?: 'today' | '7d' | '30d';
  metrics: DashboardMetric[];
  accountStatus: DashboardBucket[];
  taskStatus: DashboardBucket[];
  regions: DashboardBucket[];
  recentTasks: TaskItem[];
  trend?: DashboardTrendItem[];
  activity?: DashboardActivityItem[];
  systems?: DashboardSystemItem[];
  activeProvider: ProviderItem | null;
  settingsSummary: {
    theme: string;
    total: number;
  };
}

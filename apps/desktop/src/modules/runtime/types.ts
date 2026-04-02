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
  title: string;
  summary: string;
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
  cookieStatus: string;
  boundEnvironment: string | null;
  recentError: string | null;
  activitySummary?: AccountActivitySummaryItem[];
  isArchived: boolean;
  archivedAt: string | null;
  lastConnectionStatus: string;
  lastConnectionMessage: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface AccountDetail extends AccountItem {
  activitySummary: AccountActivitySummaryItem[];
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

export type AccountBulkActionType = 'manual_status' | 'risk_status' | 'group' | 'test' | 'archive' | 'unarchive';

export interface AccountBulkActionPayload {
  accountIds: number[];
  action: AccountBulkActionType;
  manualStatus?: string;
  riskStatus?: string;
  groupId?: number | null;
  groupName?: string | null;
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

export interface RuntimeListResponse<T> {
  items: T[];
  total: number;
}

export interface MutationResult {
  deleted?: boolean;
  accountId?: number;
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

export interface CreateTaskPayload {
  title: string;
  taskType: string;
  priority: string;
  accountId?: number | null;
  scheduledAt?: string | null;
  resultSummary?: string | null;
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
  metrics: DashboardMetric[];
  accountStatus: DashboardBucket[];
  taskStatus: DashboardBucket[];
  regions: DashboardBucket[];
  recentTasks: TaskItem[];
  activeProvider: ProviderItem | null;
  settingsSummary: {
    theme: string;
    total: number;
  };
}

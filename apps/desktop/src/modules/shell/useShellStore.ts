import { computed, ref } from 'vue';
import { defineStore } from 'pinia';

import { router } from '../../app/router';
import { shellRouteManifest } from '../../app/router/routeManifest';
import { loadHostShellInfo, notifyAppShellReady, type HostShellInfo } from '../host/hostCommands';
import { runtimeApi } from '../runtime/runtimeApi';
import type {
  DashboardActivityItem,
  DashboardOverview,
  DashboardSystemItem,
  LicenseStatus,
  RuntimeHealth,
  RuntimeNotificationItem,
  RuntimeSettingsPayload,
  RuntimeVersionCheck,
  RuntimeVersionCurrent,
  ShellAssistantAction,
} from '../runtime/types';

type ThemePreference = 'light' | 'dark' | 'system';
type LayoutMode = 'full' | 'compact' | 'narrow' | 'minimum';
type AssistantMessageRole = 'user' | 'assistant';

interface SearchResultItem {
  id: string;
  title: string;
  description: string;
  routeName: string;
}

interface AssistantMessage {
  id: string;
  role: AssistantMessageRole;
  content: string;
}

interface StatusChipItem {
  text: string;
  tone: 'info' | 'success' | 'warning' | 'error';
}

interface RuntimeChip {
  label: string;
  tone: 'info' | 'success' | 'warning' | 'error';
}

interface TopbarOverflowAction {
  id: 'ai' | 'detail' | 'status';
  label: string;
  icon: string;
}

interface WorkspaceIdentity {
  name: string;
  subtitle: string;
  initials: string;
}

const THEME_STORAGE_KEY = 'tkops.shell.theme';
const SIDEBAR_STORAGE_KEY = 'tkops.shell.sidebar-collapsed';
const DETAIL_STORAGE_KEY = 'tkops.shell.detail-visible';
const RECENT_ROUTE_STORAGE_KEY = 'tkops.shell.recent-routes';

const MAX_RECENT_ROUTES = 6;
const MAX_SEARCH_RESULTS = 10;

const WIDTH_FULL = 1180;
const WIDTH_MIN_LAYOUT = 960;
const SHELL_SCALE_BASE_WIDTH = 1440;
const SHELL_SCALE_MIN = 0.82;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function readBooleanStorage(key: string, fallback: boolean): boolean {
  try {
    const raw = window.localStorage.getItem(key);
    if (raw === 'true') {
      return true;
    }
    if (raw === 'false') {
      return false;
    }
  } catch {
    return fallback;
  }
  return fallback;
}

function writeBooleanStorage(key: string, value: boolean): void {
  try {
    window.localStorage.setItem(key, value ? 'true' : 'false');
  } catch {
    // ignore storage failures
  }
}

function readThemeStorage(): { hasStoredTheme: boolean; value: ThemePreference } {
  try {
    const raw = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (raw === 'light' || raw === 'dark' || raw === 'system') {
      return { hasStoredTheme: true, value: raw };
    }
  } catch {
    return { hasStoredTheme: false, value: 'system' };
  }
  return { hasStoredTheme: false, value: 'system' };
}

function writeThemeStorage(value: ThemePreference): void {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, value);
  } catch {
    // ignore storage failures
  }
}

function readRecentRoutesStorage(): string[] {
  try {
    const raw = window.localStorage.getItem(RECENT_ROUTE_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter((item): item is string => typeof item === 'string').slice(0, MAX_RECENT_ROUTES);
  } catch {
    return [];
  }
}

function writeRecentRoutesStorage(value: string[]): void {
  try {
    window.localStorage.setItem(RECENT_ROUTE_STORAGE_KEY, JSON.stringify(value.slice(0, MAX_RECENT_ROUTES)));
  } catch {
    // ignore storage failures
  }
}

function resolveThemeForDom(themePreference: ThemePreference): 'light' | 'dark' {
  if (themePreference === 'light') {
    return 'light';
  }
  if (themePreference === 'dark') {
    return 'dark';
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function resolveLayoutMode(width: number): LayoutMode {
  if (width <= WIDTH_FULL) {
    return 'compact';
  }
  return 'full';
}

function resolveLayoutViewportWidth(width: number): number {
  return Math.max(Math.floor(width), WIDTH_MIN_LAYOUT);
}

function resolveShellScale(layoutViewportWidth: number): number {
  return clamp(layoutViewportWidth / SHELL_SCALE_BASE_WIDTH, SHELL_SCALE_MIN, 1);
}

function inferRuntimeTone(status: string): RuntimeChip['tone'] {
  const normalized = status.trim().toLowerCase();
  if (!normalized) {
    return 'info';
  }
  if (normalized.includes('error') || normalized.includes('failed') || normalized.includes('异常')) {
    return 'error';
  }
  if (normalized.includes('warn') || normalized.includes('degraded') || normalized.includes('fallback')) {
    return 'warning';
  }
  if (normalized.includes('ok') || normalized.includes('ready') || normalized.includes('healthy')) {
    return 'success';
  }
  return 'info';
}

export const useShellStore = defineStore('shell', () => {
  const themeStorageSnapshot = readThemeStorage();
  const themePreference = ref<ThemePreference>(themeStorageSnapshot.value);
  const hasThemeStorage = ref(themeStorageSnapshot.hasStoredTheme);

  const initialViewportWidth = window.innerWidth || 1280;
  const layoutViewportWidth = ref<number>(resolveLayoutViewportWidth(initialViewportWidth));
  const layoutOverflowXEnabled = ref<boolean>(initialViewportWidth < WIDTH_MIN_LAYOUT);
  const shellScale = ref<number>(resolveShellScale(layoutViewportWidth.value));
  const layoutMode = ref<LayoutMode>(resolveLayoutMode(layoutViewportWidth.value));

  const sidebarPreference = ref<boolean>(readBooleanStorage(SIDEBAR_STORAGE_KEY, false));
  const sidebarCollapsed = ref<boolean>(sidebarPreference.value);

  const detailPreference = ref<boolean>(readBooleanStorage(DETAIL_STORAGE_KEY, true));
  const detailPanelVisible = ref<boolean>(detailPreference.value);

  const topbarOverflowOpen = ref(false);
  const notificationsOpen = ref(false);
  const statusOpen = ref(false);
  const assistantOpen = ref(false);
  const assistantBusy = ref(false);
  const bootError = ref('');

  const hostInfo = ref<HostShellInfo | null>(null);
  const runtimeHealth = ref<RuntimeHealth | null>(null);
  const licenseStatus = ref<LicenseStatus | null>(null);
  const dashboardOverview = ref<DashboardOverview | null>(null);
  const versionCurrent = ref<RuntimeVersionCurrent | null>(null);
  const versionCheck = ref<RuntimeVersionCheck | null>(null);
  const settingsSnapshot = ref<RuntimeSettingsPayload | null>(null);

  const notifications = ref<RuntimeNotificationItem[]>([]);
  const recentRouteNames = ref<string[]>(readRecentRoutesStorage());

  const searchQuery = ref('');
  const searchPanelVisible = ref(false);
  const searchResults = ref<SearchResultItem[]>([]);
  const searchActiveIndex = ref(0);

  const routeSummaryOverride = ref<string | null>(null);
  const dashboardRange = ref<'today' | '7d' | '30d'>('today');
  const selectedActivity = ref<DashboardActivityItem | null>(null);
  const selectedSystem = ref<DashboardSystemItem | null>(null);

  const assistantInput = ref('');
  const assistantMessages = ref<AssistantMessage[]>([]);
  const assistantSuggestions = ref<ShellAssistantAction[]>([]);

  const listenersBound = ref(false);
  const initializing = ref(false);

  const workspaceIdentity = ref<WorkspaceIdentity>({
    name: '我的工作台',
    subtitle: '个人版',
    initials: 'AD',
  });

  const routeMeta = computed(() => router.currentRoute.value.meta || {});
  const currentRouteName = computed(() => String(router.currentRoute.value.name || 'dashboard'));

  const currentRouteManifestItem = computed(() => shellRouteManifest.find((item) => item.name === currentRouteName.value) || null);

  const currentRouteTitle = computed(() => {
    const metaTitle = routeMeta.value.title;
    if (typeof metaTitle === 'string' && metaTitle.trim()) {
      return metaTitle;
    }
    return currentRouteManifestItem.value?.title || '概览看板';
  });

  const currentEyebrow = computed(() => {
    const metaEyebrow = routeMeta.value.eyebrow;
    if (typeof metaEyebrow === 'string' && metaEyebrow.trim()) {
      return metaEyebrow;
    }
    return currentRouteManifestItem.value?.eyebrow || '总览工作台';
  });

  const currentRouteSummary = computed(() => {
    if (routeSummaryOverride.value && routeSummaryOverride.value.trim()) {
      return routeSummaryOverride.value.trim();
    }
    const metaSummary = routeMeta.value.summary;
    if (typeof metaSummary === 'string' && metaSummary.trim()) {
      return metaSummary;
    }
    return currentRouteManifestItem.value?.summary || '页面摘要暂无可展示内容。';
  });

  const resolvedTheme = computed(() => resolveThemeForDom(themePreference.value));

  const isFullMode = computed(() => layoutMode.value === 'full');
  const isCompactMode = computed(() => layoutMode.value === 'compact');
  const isNarrowMode = computed(() => layoutMode.value === 'narrow');
  const isMinimumMode = computed(() => layoutMode.value === 'minimum');

  const showResponsiveNote = computed(() => isFullMode.value || isCompactMode.value);
  const showInlineAiAction = computed(() => isFullMode.value || isCompactMode.value);
  const showInlineDetailAction = computed(() => isFullMode.value || isCompactMode.value);
  const showInlineStatusAction = computed(() => isFullMode.value || isCompactMode.value);
  const showTopbarMore = computed(() => false);

  const topbarOverflowActions = computed<TopbarOverflowAction[]>(() => {
    const actions: TopbarOverflowAction[] = [];
    if (!showInlineAiAction.value) {
      actions.push({ id: 'ai', label: 'AI 助手', icon: '智' });
    }
    if (!showInlineDetailAction.value) {
      actions.push({ id: 'detail', label: detailPanelVisible.value ? '收起右栏' : '展开右栏', icon: '侧' });
    }
    if (!showInlineStatusAction.value) {
      actions.push({ id: 'status', label: '运行状态', icon: '况' });
    }
    return actions;
  });

  const unreadNotificationCount = computed(() => notifications.value.filter((item) => item.read !== true).length);

  const runtimeChip = computed<RuntimeChip>(() => {
    const runtimeStatus = hostInfo.value?.runtimeStatus || runtimeHealth.value?.status || 'unknown';
    return {
      label: runtimeStatus,
      tone: inferRuntimeTone(runtimeStatus),
    };
  });

  const versionChip = computed<StatusChipItem>(() => {
    if (versionCheck.value?.hasUpdate && (versionCheck.value.latest || versionCheck.value.tag)) {
      return {
        text: `可更新 ${versionCheck.value.latest || versionCheck.value.tag || ''}`.trim(),
        tone: 'warning',
      };
    }
    return {
      text: '已是最新版本',
      tone: 'success',
    };
  });

  const notificationChip = computed<StatusChipItem>(() => ({
    text: unreadNotificationCount.value > 0 ? `通知未读 ${unreadNotificationCount.value}` : '通知已读',
    tone: unreadNotificationCount.value > 0 ? 'warning' : 'success',
  }));

  const licenseChip = computed<StatusChipItem>(() => {
    if (!licenseStatus.value?.activated) {
      return { text: '许可未激活', tone: 'warning' };
    }
    const tier = licenseStatus.value.tier || 'ENTERPRISE';
    return { text: `许可 ${tier}`, tone: 'success' };
  });

  const setupChip = computed<StatusChipItem>(() => ({
    text: settingsSnapshot.value?.setup.completed ? '初始化完成' : '初始化未完成',
    tone: settingsSnapshot.value?.setup.completed ? 'success' : 'warning',
  }));

  const runtimeStatusChip = computed<StatusChipItem>(() => ({
    text: `Runtime ${runtimeChip.value.label}`,
    tone: runtimeChip.value.tone,
  }));

  const statusBarCompactChips = computed<StatusChipItem[]>(() => [runtimeStatusChip.value, versionChip.value, notificationChip.value]);

  const statusLeftChips = computed<string[]>(() => {
    const routeLabel = `页面: ${currentRouteTitle.value}`;
    if (isMinimumMode.value) {
      return [routeLabel];
    }
    const chips = [routeLabel, `Runtime: ${runtimeChip.value.label}`];
    if (currentRouteName.value === 'dashboard') {
      if (selectedSystem.value?.title) {
        chips.push(`系统: ${selectedSystem.value.title}`);
      } else if (selectedActivity.value?.title) {
        chips.push(`活动: ${selectedActivity.value.title}`);
      }
    }
    return chips;
  });

  const statusRightChips = computed<StatusChipItem[]>(() => [licenseChip.value, versionChip.value, notificationChip.value, setupChip.value]);

  const quickThemeLabel = computed(() => {
    const nextTheme = resolvedTheme.value === 'dark' ? 'light' : 'dark';
    return nextTheme === 'dark' ? '\u5207\u6362\u5230\u6df1\u8272' : '\u5207\u6362\u5230\u6d45\u8272';
  });

  function applyTheme(theme: ThemePreference, persistToLocalStorage = true): void {
    themePreference.value = theme;
    document.body.setAttribute('data-theme', resolveThemeForDom(theme));
    if (persistToLocalStorage) {
      writeThemeStorage(theme);
      hasThemeStorage.value = true;
    }
  }

  function syncThemeFromRuntime(runtimeTheme: string | undefined): void {
    if (!runtimeTheme || hasThemeStorage.value) {
      return;
    }
    if (runtimeTheme === 'light' || runtimeTheme === 'dark' || runtimeTheme === 'system') {
      applyTheme(runtimeTheme, true);
    }
  }

  async function persistThemeToRuntime(theme: ThemePreference): Promise<void> {
    if (!settingsSnapshot.value?.preferences) {
      return;
    }
    const preferences = settingsSnapshot.value.preferences;
    try {
      const saved = await runtimeApi.saveSettings({
        theme,
        language: preferences.language || 'zh-CN',
        proxyUrl: preferences.proxyUrl || '',
        timeoutSeconds: preferences.timeoutSeconds || 30,
        concurrency: preferences.concurrency || 3,
      });
      settingsSnapshot.value = saved;
      window.dispatchEvent(new CustomEvent('tkops:theme-preference-changed', { detail: { theme } }));
    } catch {
      // keep local switch responsive even if runtime persistence fails
    }
  }

  function updateLayout(width: number): void {
    const rawWidth = Math.max(1, Math.floor(width));
    layoutOverflowXEnabled.value = rawWidth < WIDTH_MIN_LAYOUT;
    layoutViewportWidth.value = resolveLayoutViewportWidth(rawWidth);
    shellScale.value = resolveShellScale(layoutViewportWidth.value);

    const nextMode = resolveLayoutMode(layoutViewportWidth.value);
    const previousMode = layoutMode.value;
    layoutMode.value = nextMode;

    sidebarCollapsed.value = sidebarPreference.value;
    detailPanelVisible.value = detailPreference.value;

    if (nextMode !== previousMode) {
      topbarOverflowOpen.value = false;
      notificationsOpen.value = false;
      statusOpen.value = false;
    }
  }

  function bindGlobalListeners(): void {
    if (listenersBound.value) {
      return;
    }
    listenersBound.value = true;

    window.addEventListener('resize', () => {
      updateLayout(window.innerWidth || 1280);
    });

    window.addEventListener('tkops:theme-preference-changed', (event: Event) => {
      const customEvent = event as CustomEvent<{ theme?: string }>;
      const nextTheme = customEvent.detail?.theme;
      if (nextTheme === 'light' || nextTheme === 'dark' || nextTheme === 'system') {
        applyTheme(nextTheme, true);
      }
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (themePreference.value === 'system') {
        applyTheme('system', false);
      }
    });
  }

  function toggleSidebar(): void {
    sidebarPreference.value = !sidebarCollapsed.value;
    sidebarCollapsed.value = sidebarPreference.value;
    writeBooleanStorage(SIDEBAR_STORAGE_KEY, sidebarPreference.value);
  }

  function toggleDetailPanel(): void {
    detailPanelVisible.value = !detailPanelVisible.value;
    detailPreference.value = detailPanelVisible.value;
    writeBooleanStorage(DETAIL_STORAGE_KEY, detailPreference.value);
  }

  function toggleThemeQuickly(): void {
    const nextTheme: ThemePreference = resolvedTheme.value === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme, true);
    void persistThemeToRuntime(nextTheme);
  }

  function toggleAssistant(): void {
    assistantOpen.value = !assistantOpen.value;
    if (assistantOpen.value) {
      notificationsOpen.value = false;
      statusOpen.value = false;
      topbarOverflowOpen.value = false;
    }
  }

  function closeAssistant(): void {
    assistantOpen.value = false;
  }

  function toggleNotifications(): void {
    notificationsOpen.value = !notificationsOpen.value;
    if (notificationsOpen.value) {
      statusOpen.value = false;
      topbarOverflowOpen.value = false;
    }
  }

  function toggleStatusPanel(): void {
    statusOpen.value = !statusOpen.value;
    if (statusOpen.value) {
      notificationsOpen.value = false;
      topbarOverflowOpen.value = false;
    }
  }

  function toggleTopbarOverflow(): void {
    if (!showTopbarMore.value) {
      topbarOverflowOpen.value = false;
      return;
    }
    topbarOverflowOpen.value = !topbarOverflowOpen.value;
    if (topbarOverflowOpen.value) {
      notificationsOpen.value = false;
      statusOpen.value = false;
    }
  }

  function runTopbarOverflowAction(actionId: TopbarOverflowAction['id']): void {
    if (actionId === 'ai') {
      toggleAssistant();
    } else if (actionId === 'detail') {
      toggleDetailPanel();
    } else if (actionId === 'status') {
      toggleStatusPanel();
    }
    topbarOverflowOpen.value = false;
  }

  function buildSearchResults(query: string): SearchResultItem[] {
    const normalized = query.trim().toLowerCase();
    const routeItems = shellRouteManifest.map((item) => ({
      id: `route:${item.name}`,
      title: item.title,
      description: `${item.eyebrow} · ${item.summary}`,
      routeName: item.name,
      isMatch:
        !normalized ||
        item.title.toLowerCase().includes(normalized) ||
        item.eyebrow.toLowerCase().includes(normalized) ||
        item.summary.toLowerCase().includes(normalized),
    }));

    const recentItems = recentRouteNames.value
      .map((name) => shellRouteManifest.find((item) => item.name === name))
      .filter((item): item is NonNullable<typeof item> => Boolean(item))
      .map((item) => ({
        id: `recent:${item.name}`,
        title: item.title,
        description: `最近访问 · ${item.eyebrow}`,
        routeName: item.name,
        isMatch: !normalized || item.title.toLowerCase().includes(normalized) || item.eyebrow.toLowerCase().includes(normalized),
      }));

    const merged = [...recentItems.filter((item) => item.isMatch), ...routeItems.filter((item) => item.isMatch)];

    const unique = new Map<string, SearchResultItem>();
    merged.forEach((item) => {
      if (!unique.has(item.routeName)) {
        unique.set(item.routeName, {
          id: item.id,
          title: item.title,
          description: item.description,
          routeName: item.routeName,
        });
      }
    });

    return Array.from(unique.values()).slice(0, MAX_SEARCH_RESULTS);
  }

  function updateSearchResults(): void {
    searchResults.value = buildSearchResults(searchQuery.value);
    searchActiveIndex.value = searchResults.value.length > 0 ? 0 : -1;
  }

  function openSearchPanel(): void {
    searchPanelVisible.value = true;
    updateSearchResults();
    notificationsOpen.value = false;
    statusOpen.value = false;
  }

  function closeSearchPanel(): void {
    searchPanelVisible.value = false;
    searchActiveIndex.value = -1;
  }

  function moveSearchSelection(step: number): void {
    if (!searchResults.value.length) {
      searchActiveIndex.value = -1;
      return;
    }
    if (searchActiveIndex.value < 0) {
      searchActiveIndex.value = 0;
      return;
    }
    const maxIndex = searchResults.value.length - 1;
    const next = searchActiveIndex.value + step;
    if (next < 0) {
      searchActiveIndex.value = maxIndex;
      return;
    }
    if (next > maxIndex) {
      searchActiveIndex.value = 0;
      return;
    }
    searchActiveIndex.value = next;
  }

  async function navigateFromSearch(item: SearchResultItem): Promise<void> {
    await router.push({ name: item.routeName });
    closeSearchPanel();
    topbarOverflowOpen.value = false;
  }

  function selectActiveSearchResult(): void {
    if (!searchResults.value.length) {
      return;
    }
    const index = searchActiveIndex.value < 0 ? 0 : searchActiveIndex.value;
    const target = searchResults.value[index];
    if (!target) {
      return;
    }
    void navigateFromSearch(target);
  }

  function markCurrentRouteVisited(): void {
    const routeName = currentRouteName.value;
    if (!routeName) {
      return;
    }

    const next = [routeName, ...recentRouteNames.value.filter((item) => item !== routeName)].slice(0, MAX_RECENT_ROUTES);
    recentRouteNames.value = next;
    writeRecentRoutesStorage(next);
  }

  function setRouteSummary(summary: string | null): void {
    routeSummaryOverride.value = summary;
  }

  function setDashboardRange(value: 'today' | '7d' | '30d'): void {
    dashboardRange.value = value;
  }

  function setSelectedActivity(item: DashboardActivityItem | null): void {
    selectedActivity.value = item;
  }

  function setSelectedSystem(item: DashboardSystemItem | null): void {
    selectedSystem.value = item;
  }

  function defaultAssistantSuggestions(): ShellAssistantAction[] {
    return [
      { id: 'goto-settings', label: '打开系统设置', action: 'navigate', payload: { routeName: 'system-settings' } },
      { id: 'open-notifications', label: '打开通知中心', action: 'toggle-notifications' },
      { id: 'toggle-theme', label: '切换主题', action: 'toggle-theme' },
      { id: 'toggle-detail', label: '切换右栏', action: 'toggle-detail' },
    ];
  }

  async function runShellAction(action: ShellAssistantAction): Promise<void> {
    if (action.action === 'navigate') {
      const routeName = action.payload?.routeName;
      if (typeof routeName === 'string' && routeName.trim()) {
        await router.push({ name: routeName });
      }
      return;
    }
    if (action.action === 'toggle-notifications') {
      toggleNotifications();
      return;
    }
    if (action.action === 'toggle-theme') {
      toggleThemeQuickly();
      return;
    }
    if (action.action === 'toggle-detail') {
      toggleDetailPanel();
      return;
    }
    if (action.action === 'toggle-status') {
      toggleStatusPanel();
      return;
    }
    if (action.action === 'refresh-page') {
      window.location.reload();
    }
  }

  async function sendAssistantMessage(): Promise<void> {
    const message = assistantInput.value.trim();
    if (!message || assistantBusy.value) {
      return;
    }

    const userMessage: AssistantMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
    };
    assistantMessages.value.push(userMessage);
    assistantInput.value = '';
    assistantBusy.value = true;

    const history = assistantMessages.value.slice(-10).map((item) => ({ role: item.role, content: item.content }));

    try {
      const response = await runtimeApi.askShellAssistant({
        message,
        context: {
          route: {
            name: currentRouteName.value,
            title: currentRouteTitle.value,
            summary: currentRouteSummary.value,
          },
          runtime: {
            status: runtimeChip.value.label,
            endpoint: hostInfo.value?.runtimeEndpoint || runtimeHealth.value?.host || '',
          },
          notifications: {
            unread: unreadNotificationCount.value,
            total: notifications.value.length,
          },
        },
        history,
      });

      assistantMessages.value.push({
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer || '已收到。',
      });
      assistantSuggestions.value = response.suggestions?.length ? response.suggestions : defaultAssistantSuggestions();
    } catch (cause) {
      const messageText = cause instanceof Error ? cause.message : '助手暂时不可用，请稍后重试。';
      assistantMessages.value.push({
        id: `assistant-error-${Date.now()}`,
        role: 'assistant',
        content: messageText,
      });
      assistantSuggestions.value = defaultAssistantSuggestions();
    } finally {
      assistantBusy.value = false;
    }
  }

  async function initializeShell(): Promise<void> {
    if (initializing.value) {
      return;
    }
    initializing.value = true;
    bootError.value = '';

    bindGlobalListeners();
    applyTheme(themePreference.value, false);
    updateLayout(window.innerWidth || 1280);

    try {
      const [hostResult, healthResult, licenseResult, dashboardResult, notificationsResult, currentVersionResult, checkVersionResult, settingsResult] =
        await Promise.allSettled([
          loadHostShellInfo(),
          runtimeApi.getHealth(),
          runtimeApi.getLicenseStatus(),
          runtimeApi.getDashboardOverview(),
          runtimeApi.listNotifications(),
          runtimeApi.getVersionCurrent(),
          runtimeApi.checkVersion(),
          runtimeApi.getSettings(),
        ]);

      if (hostResult.status === 'fulfilled') {
        hostInfo.value = hostResult.value;
      }
      if (healthResult.status === 'fulfilled') {
        runtimeHealth.value = healthResult.value;
      }
      if (licenseResult.status === 'fulfilled') {
        licenseStatus.value = licenseResult.value;
      }
      if (dashboardResult.status === 'fulfilled') {
        dashboardOverview.value = dashboardResult.value;
        const nextRange = dashboardResult.value?.range;
        if (nextRange === 'today' || nextRange === '7d' || nextRange === '30d') {
          dashboardRange.value = nextRange;
        }
      }
      if (notificationsResult.status === 'fulfilled') {
        notifications.value = notificationsResult.value;
      }
      if (currentVersionResult.status === 'fulfilled') {
        versionCurrent.value = currentVersionResult.value;
      }
      if (checkVersionResult.status === 'fulfilled') {
        versionCheck.value = checkVersionResult.value;
      }
      if (settingsResult.status === 'fulfilled') {
        settingsSnapshot.value = settingsResult.value;
        syncThemeFromRuntime(settingsResult.value.preferences?.theme || settingsResult.value.theme);
      }

      const failedCritical = [hostResult, healthResult].filter((result) => result.status === 'rejected');
      if (failedCritical.length > 0) {
        const firstError = failedCritical[0] as PromiseRejectedResult;
        const errorMessage = firstError.reason instanceof Error ? firstError.reason.message : String(firstError.reason || '未知错误');
        bootError.value = `壳层初始化存在异常：${errorMessage}`;
      }
    } catch (cause) {
      bootError.value = cause instanceof Error ? cause.message : '初始化失败';
    } finally {
      markCurrentRouteVisited();
      updateSearchResults();
      await notifyAppShellReady().catch(() => undefined);
      initializing.value = false;
    }
  }

  return {
    themePreference,
    resolvedTheme,
    layoutMode,
    shellScale,
    layoutViewportWidth,
    layoutOverflowXEnabled,
    isFullMode,
    isCompactMode,
    isNarrowMode,
    isMinimumMode,
    sidebarCollapsed,
    detailPanelVisible,
    showResponsiveNote,
    showInlineAiAction,
    showInlineDetailAction,
    showInlineStatusAction,
    showTopbarMore,
    topbarOverflowOpen,
    topbarOverflowActions,
    notificationsOpen,
    statusOpen,
    assistantOpen,
    assistantBusy,
    bootError,
    hostInfo,
    runtimeHealth,
    licenseStatus,
    dashboardOverview,
    dashboardRange,
    selectedActivity,
    selectedSystem,
    versionCurrent,
    versionCheck,
    notifications,
    unreadNotificationCount,
    runtimeChip,
    statusLeftChips,
    statusRightChips,
    statusBarCompactChips,
    workspaceIdentity,
    currentRouteName,
    currentRouteTitle,
    currentRouteSummary,
    currentEyebrow,
    quickThemeLabel,
    searchQuery,
    searchPanelVisible,
    searchResults,
    searchActiveIndex,
    assistantInput,
    assistantMessages,
    assistantSuggestions,
    initializeShell,
    toggleSidebar,
    toggleDetailPanel,
    toggleThemeQuickly,
    toggleAssistant,
    closeAssistant,
    toggleNotifications,
    toggleStatusPanel,
    toggleTopbarOverflow,
    runTopbarOverflowAction,
    openSearchPanel,
    closeSearchPanel,
    updateSearchResults,
    moveSearchSelection,
    navigateFromSearch,
    selectActiveSearchResult,
    markCurrentRouteVisited,
    setRouteSummary,
    setDashboardRange,
    setSelectedActivity,
    setSelectedSystem,
    sendAssistantMessage,
    runShellAction,
  };
});

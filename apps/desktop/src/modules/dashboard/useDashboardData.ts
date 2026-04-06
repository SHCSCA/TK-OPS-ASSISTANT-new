import { computed, onMounted, ref } from 'vue';

import { useShellStore } from '../shell/useShellStore';
import { mapRuntimeStatus } from '../runtime/runtimePresentation';
import { runtimeApi } from '../runtime/runtimeApi';
import type {
  DashboardActivityItem,
  DashboardOverview,
  DashboardSystemItem,
  RuntimeHealth,
  SchedulerOverview,
} from '../runtime/types';

export type DashboardRange = 'today' | '7d' | '30d';

export interface DashboardRangeOption {
  key: DashboardRange;
  label: string;
}

type DashboardQuickActionKey = 'dashboard-quick-1' | 'dashboard-quick-2' | 'dashboard-quick-3' | 'dashboard-quick-4';

const RANGE_OPTIONS: DashboardRangeOption[] = [
  { key: 'today', label: '今日' },
  { key: '7d', label: '近 7 天' },
  { key: '30d', label: '近 30 天' },
];

function isDashboardRange(value: unknown): value is DashboardRange {
  return value === 'today' || value === '7d' || value === '30d';
}

function buildSystemSummary(item: DashboardSystemItem): string {
  return `${item.title}：${item.summary}`;
}

function buildActivitySummary(item: DashboardActivityItem): string {
  return `${item.title}：${item.entity} / ${item.category} / ${item.status}`;
}

function formatTime(value: string | null | undefined): string {
  if (!value) {
    return '--';
  }
  if (value.includes('T')) {
    return value.replace('T', ' ').slice(5, 16);
  }
  return value;
}

function isAbnormalStatus(status: string | null | undefined): boolean {
  const normalized = String(status || '').trim().toLowerCase();
  return normalized.includes('error') || normalized.includes('fail') || normalized.includes('warn') || normalized.includes('异常');
}

function formatTaskBucketValue(
  buckets: DashboardOverview['taskStatus'] | null | undefined,
  bucketKey: string,
): string {
  const bucket = (buckets || []).find((item) => String(item.key || '').toLowerCase() === bucketKey);
  return bucket ? String(bucket.count) : '--';
}

export function useDashboardData() {
  const shell = useShellStore();
  type DashboardDetailStateInput = Parameters<typeof shell.setDashboardDetailState>[0];

  const health = ref<RuntimeHealth | null>(null);
  const overview = ref<DashboardOverview | null>(null);
  const schedulerOverview = ref<SchedulerOverview | null>(null);
  const loading = ref(true);
  const error = ref('');

  const range = ref<DashboardRange>(shell.dashboardRange);
  const selectedActivity = ref<DashboardActivityItem | null>(null);
  const selectedSystem = ref<DashboardSystemItem | null>(null);

  const trendItems = computed(() => overview.value?.trend ?? []);
  const activityItems = computed(() => overview.value?.activity ?? []);
  const systemItems = computed(() => overview.value?.systems ?? []);
  const hasDashboardData = computed(
    () =>
      (overview.value?.metrics?.length ?? 0) > 0 ||
      trendItems.value.length > 0 ||
      activityItems.value.length > 0 ||
      systemItems.value.length > 0,
  );

  function applyDefaultDashboardDetail(): void {
    shell.setDashboardDetailState({
      kind: 'default',
      title: '概览页说明',
      subtitle: '选中右侧状态项或活动流后，这里会显示对应运行时详情。',
      statusLabel: '概览详情',
      statusTone: 'info',
      items: [
        { label: '当前模式', value: 'dashboard 运行时聚合' },
        { label: '趋势图', value: 'X 轴为时间，Y 轴为任务数量' },
        { label: '活动流', value: '来自任务与活动日志' },
      ],
    });
  }

  function buildActivityDetail(item: DashboardActivityItem) {
    return {
      kind: 'activity' as const,
      title: item.title || '活动详情',
      subtitle: '来自活动流选中项',
      statusLabel: item.status || '--',
      statusTone: isAbnormalStatus(item.status) ? 'warning' as const : 'info' as const,
      items: [
        { label: '关联对象', value: item.entity || '--' },
        { label: '分类', value: item.category || '--' },
        { label: '时间', value: formatTime(item.time) },
      ],
    };
  }

  function buildSystemDetail(item: DashboardSystemItem) {
    return {
      kind: 'system' as const,
      title: item.title || '系统状态',
      subtitle: '实时状态摘要',
      statusLabel: item.status || '--',
      statusTone: (item.tone || 'info') as 'info' | 'success' | 'warning' | 'error',
      items: [
        { label: '摘要', value: item.summary || '--' },
        { label: '来源', value: 'dashboard 运行时聚合' },
      ],
    };
  }

  function buildQuickActionDetail(actionKey: DashboardQuickActionKey): DashboardDetailStateInput {
    if (actionKey === 'dashboard-quick-1') {
      const riskySystems = systemItems.value.filter((item) => item.tone === 'error' || item.tone === 'warning');
      const recentAbnormalActivity = activityItems.value.find((item) => isAbnormalStatus(item.status));
      const statusTone: 'warning' | 'success' = riskySystems.length > 0 ? 'warning' : 'success';

      return {
        kind: 'quick-action' as const,
        title: '处理账号异常',
        subtitle: '优先聚焦高风险系统项与异常活动。',
        statusLabel: riskySystems.length > 0 ? '优先处理' : '状态稳定',
        statusTone,
        items: [
          {
            label: '异常/关注系统项',
            value: riskySystems.length > 0 ? `${riskySystems.length} 项` : '暂无异常项',
          },
          {
            label: '最近异常活动',
            value: recentAbnormalActivity ? `${recentAbnormalActivity.title} / ${formatTime(recentAbnormalActivity.time)}` : '--',
          },
          {
            label: '建议动作',
            value: riskySystems.length > 0 ? '优先处理异常账号与代理链路' : '保持巡检并持续观测',
          },
        ],
      };
    }

    if (actionKey === 'dashboard-quick-2') {
      const provider = overview.value?.activeProvider;
      const running = formatTaskBucketValue(overview.value?.taskStatus, 'running');
      const pending = formatTaskBucketValue(overview.value?.taskStatus, 'pending');
      const queueState = running === '--' && pending === '--' ? '--' : `运行中 ${running} / 排队 ${pending}`;

      return {
        kind: 'quick-action' as const,
        title: '启动内容批量生成',
        subtitle: '建议先确认默认模型和队列容量。',
        statusLabel: provider ? '可执行' : '待配置',
        statusTone: provider ? 'success' : 'warning',
        items: [
          {
            label: '推荐模型',
            value: provider ? `${provider.name} / ${provider.defaultModel || '--'}` : '--',
          },
          {
            label: '队列状态',
            value: queueState,
          },
          {
            label: '当前可用槽位',
            value: '--',
          },
        ],
      };
    }

    if (actionKey === 'dashboard-quick-3') {
      const runtimeStatus = mapRuntimeStatus(health.value?.status || shell.runtimeRawStatus).label;
      const runtimeReachable = shell.hostInfo?.runtimeReachable;
      const endpoint = shell.hostInfo?.runtimeEndpoint || (health.value?.host ? `${health.value.host}:${health.value.port}` : '--');

      return {
        kind: 'quick-action' as const,
        title: '网络诊断',
        subtitle: '聚焦运行时连通性与宿主可达状态。',
        statusLabel: runtimeReachable ? '可连接' : '待确认',
        statusTone: runtimeReachable ? 'success' : 'warning',
        items: [
          { label: '运行时健康', value: runtimeStatus || '--' },
          { label: '连通状态', value: runtimeReachable == null ? '--' : runtimeReachable ? '可连接' : '不可连接' },
          { label: '访问端点', value: endpoint || '--' },
        ],
      };
    }

    const scheduledCount = schedulerOverview.value?.summary?.scheduled;
    const failedCount = schedulerOverview.value?.summary?.failed;
    const quietHours = schedulerOverview.value?.windows?.quietHours || '--';
    const hasFailed = typeof failedCount === 'number' && failedCount > 0;

    return {
      kind: 'quick-action' as const,
      title: '审核定时发布',
      subtitle: '避免在异常链路上继续推送任务。',
      statusLabel: hasFailed ? '存在异常计划' : '等待触发',
      statusTone: hasFailed ? 'warning' : 'info',
      items: [
        { label: '待触发计划', value: typeof scheduledCount === 'number' ? `${scheduledCount} 条` : '--' },
        { label: '异常计划', value: typeof failedCount === 'number' ? `${failedCount} 条` : '--' },
        { label: '静默时段', value: quietHours || '--' },
      ],
    };
  }

  function syncShellSelectionState(): void {
    shell.setSelectedActivity(selectedActivity.value);
    shell.setSelectedSystem(selectedSystem.value);

    if (selectedSystem.value) {
      shell.setRouteSummary(buildSystemSummary(selectedSystem.value));
      shell.setDashboardDetailState(buildSystemDetail(selectedSystem.value));
      return;
    }
    if (selectedActivity.value) {
      shell.setRouteSummary(buildActivitySummary(selectedActivity.value));
      shell.setDashboardDetailState(buildActivityDetail(selectedActivity.value));
      return;
    }
    shell.setRouteSummary(null);
    applyDefaultDashboardDetail();
  }

  function selectActivity(item: DashboardActivityItem | null): void {
    selectedActivity.value = item;
    selectedSystem.value = null;
    syncShellSelectionState();
  }

  function selectSystem(item: DashboardSystemItem | null): void {
    selectedSystem.value = item;
    selectedActivity.value = null;
    syncShellSelectionState();
  }

  function selectQuickAction(actionKey: DashboardQuickActionKey): void {
    selectedActivity.value = null;
    selectedSystem.value = null;
    shell.setSelectedActivity(null);
    shell.setSelectedSystem(null);

    const next = buildQuickActionDetail(actionKey);
    shell.setDashboardDetailState(next);
    shell.setRouteSummary(`${next.title}：${next.subtitle}`);
  }

  function restoreOrInitSelection(nextOverview: DashboardOverview | null): void {
    const nextActivities = nextOverview?.activity ?? [];
    const nextSystems = nextOverview?.systems ?? [];

    if (selectedSystem.value?.key) {
      const matchedSystem = nextSystems.find((item) => item.key === selectedSystem.value?.key) ?? null;
      if (matchedSystem) {
        selectedSystem.value = matchedSystem;
        selectedActivity.value = null;
        syncShellSelectionState();
        return;
      }
    }

    if (selectedActivity.value?.title) {
      const matchedActivity =
        nextActivities.find(
          (item) =>
            item.title === selectedActivity.value?.title &&
            item.time === selectedActivity.value?.time &&
            item.category === selectedActivity.value?.category,
        ) ?? null;
      if (matchedActivity) {
        selectedActivity.value = matchedActivity;
        selectedSystem.value = null;
        syncShellSelectionState();
        return;
      }
    }

    selectedSystem.value = null;
    selectedActivity.value = null;
    syncShellSelectionState();
  }

  async function load(nextRange: DashboardRange = range.value) {
    loading.value = true;
    error.value = '';
    range.value = nextRange;
    shell.setDashboardRange(nextRange);
    try {
      const [healthResult, overviewResult, schedulerResult] = await Promise.allSettled([
        runtimeApi.getHealth(),
        runtimeApi.getDashboardOverview(nextRange),
        runtimeApi.getSchedulerOverview(),
      ]);

      if (healthResult.status !== 'fulfilled') {
        throw healthResult.reason;
      }
      if (overviewResult.status !== 'fulfilled') {
        throw overviewResult.reason;
      }

      health.value = healthResult.value;
      overview.value = overviewResult.value;
      schedulerOverview.value = schedulerResult.status === 'fulfilled' ? schedulerResult.value : null;

      if (isDashboardRange(overviewResult.value.range) && overviewResult.value.range != range.value) {
        range.value = overviewResult.value.range;
        shell.setDashboardRange(overviewResult.value.range);
      }
      restoreOrInitSelection(overviewResult.value);
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Runtime 请求失败';
      overview.value = null;
      schedulerOverview.value = null;
      selectedActivity.value = null;
      selectedSystem.value = null;
      syncShellSelectionState();
    } finally {
      loading.value = false;
    }
  }

  onMounted(() => {
    void load(range.value);
  });

  return {
    activityItems,
    error,
    hasDashboardData,
    health,
    loading,
    overview,
    range,
    rangeOptions: RANGE_OPTIONS,
    reload: () => load(range.value),
    selectActivity,
    selectSystem,
    selectQuickAction,
    selectedActivity,
    selectedSystem,
    setRange: (nextRange: DashboardRange) => load(nextRange),
    systemItems,
    trendItems,
  };
}

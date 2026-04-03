import { computed, onMounted, ref } from 'vue';

import { useShellStore } from '../shell/useShellStore';
import { runtimeApi } from '../runtime/runtimeApi';
import type {
  DashboardActivityItem,
  DashboardOverview,
  DashboardSystemItem,
  RuntimeHealth,
} from '../runtime/types';

export type DashboardRange = 'today' | '7d' | '30d';

export interface DashboardRangeOption {
  key: DashboardRange;
  label: string;
}

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

export function useDashboardData() {
  const shell = useShellStore();

  const health = ref<RuntimeHealth | null>(null);
  const overview = ref<DashboardOverview | null>(null);
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

  function syncShellSelectionState(): void {
    shell.setSelectedActivity(selectedActivity.value);
    shell.setSelectedSystem(selectedSystem.value);

    if (selectedSystem.value) {
      shell.setRouteSummary(buildSystemSummary(selectedSystem.value));
      return;
    }
    if (selectedActivity.value) {
      shell.setRouteSummary(buildActivitySummary(selectedActivity.value));
      return;
    }
    shell.setRouteSummary(null);
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

    if (nextSystems.length > 0) {
      selectSystem(nextSystems[0]);
      return;
    }
    if (nextActivities.length > 0) {
      selectActivity(nextActivities[0]);
      return;
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
      const [healthPayload, overviewPayload] = await Promise.all([
        runtimeApi.getHealth(),
        runtimeApi.getDashboardOverview(nextRange),
      ]);
      health.value = healthPayload;
      overview.value = overviewPayload;
      if (isDashboardRange(overviewPayload.range) && overviewPayload.range !== range.value) {
        range.value = overviewPayload.range;
        shell.setDashboardRange(overviewPayload.range);
      }
      restoreOrInitSelection(overviewPayload);
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Runtime 请求失败';
      overview.value = null;
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
    selectedActivity,
    selectedSystem,
    setRange: (nextRange: DashboardRange) => load(nextRange),
    systemItems,
    trendItems,
  };
}

import { computed, onBeforeUnmount, ref, watch, type Ref } from 'vue';

import { router } from '../../app/router';
import type { AssetItem } from '../assets/assetCenter.types';
import { runtimeApi } from '../runtime/runtimeApi';
import type {
  AccountItem,
  ActivityLogItem,
  ExperimentProjectItem,
  ExperimentViewItem,
  TaskItem,
} from '../runtime/types';
import { useAsyncResource } from '../runtime/useAsyncResource';
import { useShellStore } from '../shell/useShellStore';
import {
  buildCreativeCompareRows,
  buildCreativeDetail,
  buildCreativeFocusCards,
  buildCreativeRailTools,
  buildCreativeSideCards,
  buildCreativeStripCards,
  buildCreativeSummaryChips,
} from './creativeWorkshop.helpers';
import type { CreativeRailKey } from './creativeWorkshop.types';

const DEFAULT_PLAN_NAME = '创意工坊方案';
const DEFAULT_PLAN_GOAL = '围绕主题、镜头、口播和素材组合做新一轮创意试验。';

type DetailAction = 'save-plan' | 'compare-views' | 'goto-video-editor';

function sortByLatest<T extends { updatedAt?: string | null; createdAt?: string | null }>(items: T[]): T[] {
  return [...items].sort((left, right) => {
    const leftTime = new Date(left.updatedAt || left.createdAt || 0).getTime();
    const rightTime = new Date(right.updatedAt || right.createdAt || 0).getTime();
    return rightTime - leftTime;
  });
}

export function useCreativeWorkshopData() {
  const shell = useShellStore();
  const resource = useAsyncResource(async () => {
    const [accounts, assetsResponse, tasksResponse, projectsResponse, viewsResponse, activitiesResponse] = await Promise.all([
      runtimeApi.listAccounts({ includeArchived: false }),
      runtimeApi.listAssets(),
      runtimeApi.listTasks(),
      runtimeApi.listExperimentProjects(),
      runtimeApi.listExperimentViews(),
      runtimeApi.listActivityLogs(24),
    ]);

    return {
      accounts: accounts.items,
      assets: (assetsResponse.items || []) as AssetItem[],
      tasks: tasksResponse.items,
      projects: projectsResponse.items,
      views: viewsResponse.items,
      activities: activitiesResponse.items,
    };
  });

  const actionError = ref('');
  const actionMessage = ref('');
  const saving = ref(false);
  const compareMode = ref(false);
  const activeRail = ref<CreativeRailKey>('theme');
  const selectedProjectId = ref<number | null>(null);
  const draftName = ref(DEFAULT_PLAN_NAME);
  const draftGoal = ref(DEFAULT_PLAN_GOAL);
  const compareBoardRef: Ref<HTMLElement | null> = ref(null);

  const accounts = computed(() => resource.data.value?.accounts || []);
  const assets = computed(() => resource.data.value?.assets || []);
  const tasks = computed(() => resource.data.value?.tasks || []);
  const projects = computed(() => sortByLatest(resource.data.value?.projects || []));
  const views = computed(() => sortByLatest(resource.data.value?.views || []));
  const activities = computed(() => sortByLatest(resource.data.value?.activities || []));
  const railTools = computed(() => buildCreativeRailTools());
  const selectedProject = computed(() => projects.value.find((item) => item.id === selectedProjectId.value) || projects.value[0] || null);
  const summaryChips = computed(() => buildCreativeSummaryChips(projects.value, tasks.value, assets.value, accounts.value));
  const focusCards = computed(() => buildCreativeFocusCards(accounts.value, assets.value, tasks.value, activeRail.value));
  const sideCards = computed(() => buildCreativeSideCards(selectedProject.value, tasks.value, activities.value));
  const stripCards = computed(() => buildCreativeStripCards(projects.value, views.value, tasks.value, activities.value));
  const compareRows = computed(() => buildCreativeCompareRows(projects.value, views.value, assets.value, tasks.value));
  const detail = computed(() => buildCreativeDetail(selectedProject.value, tasks.value, assets.value, activities.value, views.value));

  function syncDetailState(): void {
    shell.setCreativeDetailState({
      kind: selectedProject.value ? 'selected' : 'default',
      projectId: selectedProject.value?.id ?? null,
      title: detail.value.title,
      subtitle: detail.value.subtitle,
      statusLabel: detail.value.statusLabel,
      statusTone: detail.value.statusTone,
      detailItems: detail.value.detailItems,
      adviceItems: detail.value.adviceItems,
    });
  }

  watch(projects, (next) => {
    if (!next.length) {
      selectedProjectId.value = null;
      syncDetailState();
      return;
    }
    if (typeof selectedProjectId.value === 'number' && next.some((item) => item.id === selectedProjectId.value)) {
      syncDetailState();
      return;
    }
    selectedProjectId.value = next[0].id;
    draftName.value = next[0].name || DEFAULT_PLAN_NAME;
    draftGoal.value = next[0].goal || DEFAULT_PLAN_GOAL;
    syncDetailState();
  }, { immediate: true });

  watch([selectedProject, tasks, assets, activities, views], () => {
    syncDetailState();
  });

  function selectProject(project: ExperimentProjectItem): void {
    selectedProjectId.value = project.id;
    draftName.value = project.name || DEFAULT_PLAN_NAME;
    draftGoal.value = project.goal || DEFAULT_PLAN_GOAL;
    syncDetailState();
  }

  function setActiveRail(value: CreativeRailKey): void {
    activeRail.value = value;
  }

  async function reload(): Promise<void> {
    await resource.load();
    syncDetailState();
  }

  async function saveCreativePlan(): Promise<void> {
    if (saving.value || !draftName.value.trim()) {
      return;
    }

    saving.value = true;
    actionError.value = '';
    actionMessage.value = '';

    try {
      const project = await runtimeApi.createExperimentProject({
        name: draftName.value.trim(),
        goal: draftGoal.value.trim() || DEFAULT_PLAN_GOAL,
        status: 'active',
        configJson: JSON.stringify({
          route: 'creative-workshop',
          rail: activeRail.value,
          compareMode: compareMode.value,
          assetCount: assets.value.length,
          taskCount: tasks.value.length,
        }),
      });

      await runtimeApi.createExperimentView({
        experimentProjectId: project.id,
        name: `${project.name} / 默认视图`,
        layoutJson: JSON.stringify({
          route: 'creative-workshop',
          compareMode: compareMode.value,
          activeRail: activeRail.value,
        }),
      });

      await runtimeApi.createActivityLog({
        category: 'creative-workshop',
        title: `保存创意方案：${project.name}`,
        relatedEntityType: 'experiment_project',
        relatedEntityId: project.id,
        payloadJson: JSON.stringify({
          goal: draftGoal.value.trim() || DEFAULT_PLAN_GOAL,
          activeRail: activeRail.value,
        }),
      });

      selectedProjectId.value = project.id;
      actionMessage.value = '创意方案已保存，并同步生成默认实验视图。';
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '保存创意方案失败';
    } finally {
      saving.value = false;
    }
  }

  function toggleCompareMode(): void {
    compareMode.value = !compareMode.value;
    actionError.value = '';
    actionMessage.value = compareMode.value ? '已切换到创意版本对比视图。' : '已返回实验主视角。';
  }

  async function openVideoEditor(): Promise<void> {
    await router.push({ name: 'video-editor' });
  }

  function onDetailAction(event: Event): void {
    const customEvent = event as CustomEvent<{ action?: DetailAction }>;
    const action = customEvent.detail?.action;

    if (action === 'save-plan') {
      void saveCreativePlan();
      return;
    }
    if (action === 'compare-views') {
      toggleCompareMode();
      return;
    }
    if (action === 'goto-video-editor') {
      void openVideoEditor();
    }
  }

  window.addEventListener('tkops:creative-workshop-detail-action', onDetailAction as EventListener);

  onBeforeUnmount(() => {
    window.removeEventListener('tkops:creative-workshop-detail-action', onDetailAction as EventListener);
    shell.resetCreativeDetailState();
  });

  return {
    actionError,
    actionMessage,
    activeRail,
    compareBoardRef,
    compareMode,
    compareRows,
    detail,
    draftGoal,
    draftName,
    error: resource.error,
    focusCards,
    loading: resource.loading,
    openVideoEditor,
    railTools,
    reload,
    saveCreativePlan,
    saving,
    selectProject,
    selectedProject,
    selectedProjectId,
    setActiveRail,
    sideCards,
    stripCards,
    summaryChips,
    toggleCompareMode,
    views,
    projects,
  };
}
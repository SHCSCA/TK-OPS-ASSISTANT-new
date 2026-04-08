import { computed, onBeforeUnmount, ref, watch } from 'vue';

import type { AssetItem } from '../assets/assetCenter.types';
import { runtimeApi } from '../runtime/runtimeApi';
import type { AccountItem, TaskItem } from '../runtime/types';
import { useAsyncResource } from '../runtime/useAsyncResource';
import { useShellStore } from '../shell/useShellStore';
import {
  buildPublishCalendarDays,
  buildPublishDetail,
  buildPublishMetrics,
  buildPublishRecords,
} from './scheduledPublish.helpers';
import type { PublishViewMode } from './scheduledPublish.types';

const DEFAULT_FORM = {
  title: '定时发布计划',
  priority: 'high',
  resultSummary: '来源页面：定时发布',
};

type DetailAction = 'start-plan' | 'delete-plan' | 'toggle-calendar';

export function useScheduledPublishData() {
  const shell = useShellStore();
  const resource = useAsyncResource(async () => {
    const [tasks, accounts, assetsResponse] = await Promise.all([
      runtimeApi.listTasks(),
      runtimeApi.listAccounts({ includeArchived: false }),
      runtimeApi.listAssets(),
    ]);
    return {
      tasks: tasks.items,
      accounts: accounts.items,
      assets: (assetsResponse.items || []) as AssetItem[],
    };
  });

  const actionError = ref('');
  const actionMessage = ref('');
  const creating = ref(false);
  const query = ref('');
  const statusFilter = ref('');
  const selectedRecordId = ref<number | null>(null);
  const viewMode = ref<PublishViewMode>('list');
  const draftTitle = ref(DEFAULT_FORM.title);
  const draftPriority = ref(DEFAULT_FORM.priority);
  const draftResultSummary = ref(DEFAULT_FORM.resultSummary);
  const draftScheduledAt = ref('');
  const draftAccountId = ref<number | null>(null);

  const tasks = computed(() => (resource.data.value?.tasks || []).filter((item: TaskItem) => item.taskType === 'publish'));
  const accounts = computed(() => resource.data.value?.accounts || []);
  const assets = computed(() => resource.data.value?.assets || []);
  const accountOptions = computed(() => accounts.value.map((item: AccountItem) => ({ id: item.id, label: `${item.username} / ${item.platform}` })));
  const filteredTasks = computed(() => tasks.value.filter((item) => {
    const normalizedQuery = query.value.trim().toLowerCase();
    const matchesQuery = !normalizedQuery
      || item.title.toLowerCase().includes(normalizedQuery)
      || String(item.accountUsername || '').toLowerCase().includes(normalizedQuery)
      || String(item.resultSummary || '').toLowerCase().includes(normalizedQuery);
    const matchesStatus = !statusFilter.value || item.status === statusFilter.value;
    return matchesQuery && matchesStatus;
  }));
  const metrics = computed(() => buildPublishMetrics(filteredTasks.value));
  const records = computed(() => buildPublishRecords(filteredTasks.value, accounts.value));
  const selectedRecord = computed(() => records.value.find((item) => item.id === selectedRecordId.value) || records.value[0] || null);
  const detail = computed(() => buildPublishDetail(selectedRecord.value, filteredTasks.value, accounts.value, assets.value));
  const calendarDays = computed(() => buildPublishCalendarDays(filteredTasks.value));
  const total = computed(() => filteredTasks.value.length);
  const statusCounts = computed(() => ({
    all: tasks.value.length,
    pending: tasks.value.filter((item) => item.status === 'pending').length,
    running: tasks.value.filter((item) => item.status === 'running').length,
    completed: tasks.value.filter((item) => item.status === 'completed').length,
    failed: tasks.value.filter((item) => item.status === 'failed').length,
    paused: tasks.value.filter((item) => item.status === 'paused').length,
  }));

  function syncDetailState(): void {
    shell.setPublishDetailState({
      kind: selectedRecord.value ? 'selected' : 'default',
      planId: selectedRecord.value?.id ?? null,
      title: detail.value.title,
      subtitle: detail.value.subtitle,
      statusLabel: detail.value.statusLabel,
      statusTone: detail.value.statusTone,
      detailItems: detail.value.detailItems,
      adviceItems: detail.value.adviceItems,
    });
  }

  watch(records, (next) => {
    if (!next.length) {
      selectedRecordId.value = null;
      syncDetailState();
      return;
    }
    if (typeof selectedRecordId.value === 'number' && next.some((item) => item.id === selectedRecordId.value)) {
      syncDetailState();
      return;
    }
    selectedRecordId.value = next[0].id;
    syncDetailState();
  }, { immediate: true });

  watch([selectedRecord, filteredTasks, accounts, assets], () => {
    syncDetailState();
  });

  function resetDraft(): void {
    draftTitle.value = DEFAULT_FORM.title;
    draftPriority.value = DEFAULT_FORM.priority;
    draftResultSummary.value = DEFAULT_FORM.resultSummary;
    draftScheduledAt.value = '';
    draftAccountId.value = accountOptions.value[0]?.id ?? null;
  }

  watch(accountOptions, (next) => {
    if (typeof draftAccountId.value === 'number') {
      return;
    }
    draftAccountId.value = next[0]?.id ?? null;
  }, { immediate: true });

  async function reload(): Promise<void> {
    await resource.load();
    syncDetailState();
  }

  function selectRecord(recordId: number): void {
    selectedRecordId.value = recordId;
    syncDetailState();
  }

  function setStatus(value: string): void {
    statusFilter.value = value;
  }

  function setViewMode(mode: PublishViewMode): void {
    viewMode.value = mode;
  }

  function toggleCalendar(): void {
    viewMode.value = viewMode.value === 'calendar' ? 'list' : 'calendar';
  }

  async function createPublishPlan(): Promise<void> {
    if (creating.value || !draftTitle.value.trim() || !draftScheduledAt.value) {
      return;
    }
    creating.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.createTask({
        title: draftTitle.value.trim(),
        taskType: 'publish',
        priority: draftPriority.value,
        accountId: draftAccountId.value,
        scheduledAt: new Date(draftScheduledAt.value).toISOString(),
        resultSummary: draftResultSummary.value.trim() || DEFAULT_FORM.resultSummary,
      });
      actionMessage.value = '发布计划已创建。';
      resetDraft();
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '创建发布计划失败';
    } finally {
      creating.value = false;
    }
  }

  async function startPublishPlan(taskId: number): Promise<void> {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.startTask(taskId);
      actionMessage.value = `发布计划 #${taskId} 已开始执行。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '启动发布计划失败';
    }
  }

  async function deletePublishPlan(taskId: number): Promise<void> {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.deleteTask(taskId);
      actionMessage.value = `发布计划 #${taskId} 已删除。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '删除发布计划失败';
    }
  }

  function onDetailAction(event: Event): void {
    const customEvent = event as CustomEvent<{ action?: DetailAction; planId?: number }>;
    const action = customEvent.detail?.action;
    const planId = customEvent.detail?.planId;
    if (action === 'toggle-calendar') {
      toggleCalendar();
      return;
    }
    if (typeof planId !== 'number') {
      return;
    }
    if (action === 'start-plan') {
      void startPublishPlan(planId);
      return;
    }
    if (action === 'delete-plan') {
      void deletePublishPlan(planId);
    }
  }

  window.addEventListener('tkops:scheduled-publish-detail-action', onDetailAction as EventListener);

  onBeforeUnmount(() => {
    window.removeEventListener('tkops:scheduled-publish-detail-action', onDetailAction as EventListener);
    shell.resetPublishDetailState();
  });

  return {
    actionError,
    actionMessage,
    accountOptions,
    calendarDays,
    createPublishPlan,
    creating,
    deletePublishPlan,
    detail,
    draftAccountId,
    draftPriority,
    draftResultSummary,
    draftScheduledAt,
    draftTitle,
    error: resource.error,
    loading: resource.loading,
    metrics,
    query,
    records,
    reload,
    selectRecord,
    selectedRecord,
    selectedRecordId,
    setStatus,
    setViewMode,
    startPublishPlan,
    statusCounts,
    statusFilter,
    toggleCalendar,
    total,
    viewMode,
  };
}
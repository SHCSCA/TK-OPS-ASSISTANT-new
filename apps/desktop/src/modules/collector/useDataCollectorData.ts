import { computed, nextTick, onBeforeUnmount, ref, watch, type Ref } from 'vue';

import type { AssetItem } from '../assets/assetCenter.types';
import { runtimeApi } from '../runtime/runtimeApi';
import type { AccountItem, DeviceItem, TaskItem } from '../runtime/types';
import { useAsyncResource } from '../runtime/useAsyncResource';
import { useShellStore } from '../shell/useShellStore';
import {
  buildCollectorDetail,
  buildCollectorKanbanColumns,
  buildCollectorMetrics,
  buildCollectorProxySummary,
  buildCollectorRecords,
} from './dataCollector.helpers';
import type { CollectorViewMode } from './dataCollector.types';

const DEFAULT_FORM = {
  title: '数据采集任务',
  priority: 'high',
  resultSummary: '来源页面：数据采集助手',
};

type DetailAction = 'start-task' | 'delete-task' | 'view-proxy-pool';

export function useDataCollectorData() {
  const shell = useShellStore();
  const resource = useAsyncResource(async () => {
    const [tasks, accounts, assetsResponse, devices] = await Promise.all([
      runtimeApi.listTasks(),
      runtimeApi.listAccounts({ includeArchived: false }),
      runtimeApi.listAssets(),
      runtimeApi.listDevices(),
    ]);

    return {
      tasks: tasks.items,
      accounts: accounts.items,
      assets: (assetsResponse.items || []) as AssetItem[],
      devices: devices.items,
    };
  });

  const actionError = ref('');
  const actionMessage = ref('');
  const creating = ref(false);
  const query = ref('');
  const statusFilter = ref('');
  const viewMode = ref<CollectorViewMode>('table');
  const selectedRecordId = ref<number | null>(null);
  const draftTitle = ref(DEFAULT_FORM.title);
  const draftPriority = ref(DEFAULT_FORM.priority);
  const draftResultSummary = ref(DEFAULT_FORM.resultSummary);
  const draftAccountId = ref<number | null>(null);
  const proxyPoolHighlighted = ref(false);
  const proxyPoolPanelRef: Ref<HTMLElement | null> = ref(null);

  const tasks = computed(() => (resource.data.value?.tasks || []).filter((item: TaskItem) => item.taskType === 'scrape'));
  const accounts = computed(() => resource.data.value?.accounts || []);
  const assets = computed(() => resource.data.value?.assets || []);
  const devices = computed(() => resource.data.value?.devices || []);
  const accountOptions = computed(() => accounts.value.map((item: AccountItem) => ({ id: item.id, label: `${item.username} / ${item.region}` })));
  const allRecords = computed(() => buildCollectorRecords(tasks.value, accounts.value));
  const records = computed(() => {
    const normalizedQuery = query.value.trim().toLowerCase();
    return allRecords.value.filter((item) => {
      const matchesQuery = !normalizedQuery
        || item.title.toLowerCase().includes(normalizedQuery)
        || item.accountLabel.toLowerCase().includes(normalizedQuery)
        || item.regionLabel.toLowerCase().includes(normalizedQuery)
        || item.summary.toLowerCase().includes(normalizedQuery);
      const matchesStatus = !statusFilter.value || item.status === statusFilter.value;
      return matchesQuery && matchesStatus;
    });
  });
  const metrics = computed(() => buildCollectorMetrics(tasks.value, devices.value));
  const selectedRecord = computed(() => records.value.find((item) => item.id === selectedRecordId.value) || records.value[0] || null);
  const detail = computed(() => buildCollectorDetail(selectedRecord.value, tasks.value, accounts.value, assets.value, devices.value));
  const proxySummary = computed(() => buildCollectorProxySummary(devices.value));
  const kanbanColumns = computed(() => buildCollectorKanbanColumns(records.value));
  const statusCounts = computed(() => ({
    all: tasks.value.length,
    running: tasks.value.filter((item) => item.status === 'running').length,
    paused: tasks.value.filter((item) => item.status === 'paused').length,
    failed: tasks.value.filter((item) => item.status === 'failed').length,
    completed: tasks.value.filter((item) => item.status === 'completed').length,
  }));

  function syncDetailState(): void {
    shell.setCollectorDetailState({
      kind: selectedRecord.value ? 'selected' : 'default',
      taskId: selectedRecord.value?.id ?? null,
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

  watch([selectedRecord, tasks, accounts, assets, devices], () => {
    syncDetailState();
  });

  watch(accountOptions, (next) => {
    if (typeof draftAccountId.value === 'number') {
      return;
    }
    draftAccountId.value = next[0]?.id ?? null;
  }, { immediate: true });

  function resetDraft(): void {
    draftTitle.value = DEFAULT_FORM.title;
    draftPriority.value = DEFAULT_FORM.priority;
    draftResultSummary.value = DEFAULT_FORM.resultSummary;
    draftAccountId.value = accountOptions.value[0]?.id ?? null;
  }

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

  function setViewMode(mode: CollectorViewMode): void {
    viewMode.value = mode;
  }

  async function createCollectorTask(): Promise<void> {
    if (creating.value || !draftTitle.value.trim()) {
      return;
    }
    creating.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.createTask({
        title: draftTitle.value.trim(),
        taskType: 'scrape',
        priority: draftPriority.value,
        accountId: draftAccountId.value,
        resultSummary: draftResultSummary.value.trim() || DEFAULT_FORM.resultSummary,
      });
      actionMessage.value = '采集方案已创建。';
      resetDraft();
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '创建采集方案失败';
    } finally {
      creating.value = false;
    }
  }

  async function startCollectorTask(taskId: number): Promise<void> {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.startTask(taskId);
      actionMessage.value = `采集任务 #${taskId} 已开始执行。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '启动采集任务失败';
    }
  }

  async function deleteCollectorTask(taskId: number): Promise<void> {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.deleteTask(taskId);
      actionMessage.value = `采集任务 #${taskId} 已删除。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '删除采集任务失败';
    }
  }

  async function focusProxyPool(): Promise<void> {
    proxyPoolHighlighted.value = true;
    actionMessage.value = '已定位到代理池摘要。';
    await nextTick();
    proxyPoolPanelRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    window.setTimeout(() => {
      proxyPoolHighlighted.value = false;
    }, 1600);
  }

  function onDetailAction(event: Event): void {
    const customEvent = event as CustomEvent<{ action?: DetailAction; taskId?: number }>;
    const action = customEvent.detail?.action;
    const taskId = customEvent.detail?.taskId;

    if (action === 'view-proxy-pool') {
      void focusProxyPool();
      return;
    }
    if (typeof taskId !== 'number') {
      return;
    }
    if (action === 'start-task') {
      void startCollectorTask(taskId);
      return;
    }
    if (action === 'delete-task') {
      void deleteCollectorTask(taskId);
    }
  }

  window.addEventListener('tkops:data-collector-detail-action', onDetailAction as EventListener);

  onBeforeUnmount(() => {
    window.removeEventListener('tkops:data-collector-detail-action', onDetailAction as EventListener);
    shell.resetCollectorDetailState();
  });

  return {
    actionError,
    actionMessage,
    accountOptions,
    createCollectorTask,
    creating,
    deleteCollectorTask,
    detail,
    draftAccountId,
    draftPriority,
    draftResultSummary,
    draftTitle,
    error: resource.error,
    focusProxyPool,
    kanbanColumns,
    loading: resource.loading,
    metrics,
    proxyPoolHighlighted,
    proxyPoolPanelRef,
    proxySummary,
    query,
    records,
    reload,
    selectRecord,
    selectedRecordId,
    setStatus,
    setViewMode,
    startCollectorTask,
    statusCounts,
    statusFilter,
    viewMode,
  };
}
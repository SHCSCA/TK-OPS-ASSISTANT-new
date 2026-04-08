import { computed, onBeforeUnmount, ref, watch, type Ref } from 'vue';

import type { AssetItem } from '../assets/assetCenter.types';
import { runtimeApi } from '../runtime/runtimeApi';
import type {
  ProviderItem,
  TaskItem,
  WorkflowDefinitionItem,
  WorkflowRunItem,
} from '../runtime/types';
import { useAsyncResource } from '../runtime/useAsyncResource';
import { useShellStore } from '../shell/useShellStore';
import {
  buildAiContentFactoryBatchCards,
  buildAiContentFactoryConfigItems,
  buildAiContentFactoryDetail,
  buildAiContentFactoryNodePalette,
  buildAiContentFactorySummaryChips,
  buildAiContentFactoryWorkflowStages,
} from './aiContentFactory.helpers';
import type { AiContentFactoryNodeKey } from './aiContentFactory.types';

const DEFAULT_WORKFLOW_NAME = 'AI 内容工厂工作流';
const DEFAULT_WORKFLOW_DESCRIPTION = '围绕素材输入、脚本生成、语音字幕和批量剪辑构建稳定生产线。';

type DetailAction = 'save-workflow' | 'run-batch' | 'run-workflow';

function sortByLatest<T extends { updatedAt?: string | null; createdAt?: string | null }>(items: T[]): T[] {
  return [...items].sort((left, right) => {
    const leftTime = new Date(left.updatedAt || left.createdAt || 0).getTime();
    const rightTime = new Date(right.updatedAt || right.createdAt || 0).getTime();
    return rightTime - leftTime;
  });
}

export function useAiContentFactoryData() {
  const shell = useShellStore();
  const resource = useAsyncResource(async () => {
    const [assetsResponse, tasksResponse, providersResponse, definitionsResponse, runsResponse] = await Promise.all([
      runtimeApi.listAssets(),
      runtimeApi.listTasks(),
      runtimeApi.listProviders(),
      runtimeApi.listWorkflowDefinitions(),
      runtimeApi.listWorkflowRuns(),
    ]);

    return {
      assets: (assetsResponse.items || []) as AssetItem[],
      tasks: tasksResponse.items,
      providers: providersResponse.items,
      definitions: definitionsResponse.items,
      runs: runsResponse.items,
    };
  });

  const actionError = ref('');
  const actionMessage = ref('');
  const saving = ref(false);
  const runningWorkflow = ref(false);
  const runningBatch = ref(false);
  const activeNode = ref<AiContentFactoryNodeKey>('input');
  const selectedDefinitionId = ref<number | null>(null);
  const draftName = ref(DEFAULT_WORKFLOW_NAME);
  const draftDescription = ref(DEFAULT_WORKFLOW_DESCRIPTION);
  const workflowBoardRef: Ref<HTMLElement | null> = ref(null);

  const assets = computed(() => resource.data.value?.assets || []);
  const tasks = computed(() => resource.data.value?.tasks || [] as TaskItem[]);
  const providers = computed(() => resource.data.value?.providers || [] as ProviderItem[]);
  const definitions = computed(() => sortByLatest(resource.data.value?.definitions || [] as WorkflowDefinitionItem[]));
  const runs = computed(() => sortByLatest(resource.data.value?.runs || [] as WorkflowRunItem[]));
  const nodePalette = computed(() => buildAiContentFactoryNodePalette());
  const selectedDefinition = computed(() => definitions.value.find((item) => item.id === selectedDefinitionId.value) || definitions.value[0] || null);
  const filteredRuns = computed(() => {
    if (!selectedDefinition.value) {
      return runs.value;
    }
    return runs.value.filter((item) => item.workflowDefinitionId === selectedDefinition.value.id);
  });
  const latestRun = computed(() => filteredRuns.value[0] || null);
  const summaryChips = computed(() => buildAiContentFactorySummaryChips(definitions.value, filteredRuns.value, providers.value, assets.value));
  const workflowStages = computed(() => buildAiContentFactoryWorkflowStages(assets.value, tasks.value, providers.value, selectedDefinition.value, latestRun.value, activeNode.value));
  const batchCards = computed(() => buildAiContentFactoryBatchCards(filteredRuns.value, tasks.value));
  const configItems = computed(() => buildAiContentFactoryConfigItems(activeNode.value, providers.value, assets.value, selectedDefinition.value, latestRun.value));
  const detail = computed(() => buildAiContentFactoryDetail(selectedDefinition.value, filteredRuns.value, tasks.value, providers.value, assets.value));

  function syncDetailState(): void {
    shell.setAiContentFactoryDetailState({
      kind: selectedDefinition.value ? 'selected' : 'default',
      definitionId: selectedDefinition.value?.id ?? null,
      title: detail.value.title,
      subtitle: detail.value.subtitle,
      statusLabel: detail.value.statusLabel,
      statusTone: detail.value.statusTone,
      detailItems: detail.value.detailItems,
      adviceItems: detail.value.adviceItems,
    });
  }

  watch(definitions, (next) => {
    if (!next.length) {
      selectedDefinitionId.value = null;
      syncDetailState();
      return;
    }
    if (typeof selectedDefinitionId.value === 'number' && next.some((item) => item.id === selectedDefinitionId.value)) {
      syncDetailState();
      return;
    }
    selectedDefinitionId.value = next[0].id;
    draftName.value = next[0].name || DEFAULT_WORKFLOW_NAME;
    draftDescription.value = next[0].description || DEFAULT_WORKFLOW_DESCRIPTION;
    syncDetailState();
  }, { immediate: true });

  watch([selectedDefinition, filteredRuns, tasks, providers, assets], () => {
    syncDetailState();
  });

  function selectDefinition(definition: WorkflowDefinitionItem): void {
    selectedDefinitionId.value = definition.id;
    draftName.value = definition.name || DEFAULT_WORKFLOW_NAME;
    draftDescription.value = definition.description || DEFAULT_WORKFLOW_DESCRIPTION;
    syncDetailState();
  }

  function setActiveNode(node: AiContentFactoryNodeKey): void {
    activeNode.value = node;
  }

  async function reload(): Promise<void> {
    await resource.load();
    syncDetailState();
  }

  async function saveWorkflowDefinition(): Promise<void> {
    if (saving.value || !draftName.value.trim()) {
      return;
    }

    saving.value = true;
    actionError.value = '';
    actionMessage.value = '';

    try {
      const definition = await runtimeApi.createWorkflowDefinition({
        name: draftName.value.trim(),
        status: 'active',
        description: draftDescription.value.trim() || DEFAULT_WORKFLOW_DESCRIPTION,
        configJson: JSON.stringify({
          route: 'ai-content-factory',
          activeNode: activeNode.value,
          providerCount: providers.value.length,
          assetCount: assets.value.length,
        }),
      });

      selectedDefinitionId.value = definition.id;
      actionMessage.value = '工作流已保存，并同步接入内容工厂右栏与批次视图。';
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '保存工作流失败';
    } finally {
      saving.value = false;
    }
  }

  async function runWorkflowDefinition(): Promise<void> {
    if (runningWorkflow.value || !selectedDefinition.value) {
      if (!selectedDefinition.value) {
        actionError.value = '请先保存或选择一个工作流，再运行工作流。';
      }
      return;
    }

    runningWorkflow.value = true;
    actionError.value = '';
    actionMessage.value = '';

    try {
      const run = await runtimeApi.startWorkflowRun({
        workflowDefinitionId: selectedDefinition.value.id,
        status: 'pending',
        inputJson: JSON.stringify({
          route: 'ai-content-factory',
          activeNode: activeNode.value,
          taskCount: tasks.value.length,
        }),
        resultJson: null,
      });

      actionMessage.value = `工作流批次 #${run.id} 已创建。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '运行工作流失败';
    } finally {
      runningWorkflow.value = false;
    }
  }

  async function runBatch(): Promise<void> {
    if (runningBatch.value) {
      return;
    }

    runningBatch.value = true;
    actionError.value = '';
    actionMessage.value = '';

    try {
      const task = await runtimeApi.createTask({
        title: `${selectedDefinition.value?.name || draftName.value.trim() || DEFAULT_WORKFLOW_NAME} / 批量生产`,
        taskType: 'publish',
        priority: 'high',
        resultSummary: '来源页面：AI 内容工厂',
      });

      actionMessage.value = `内容批量生产任务已加入队列：${task.title}`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '启动批量生产失败';
    } finally {
      runningBatch.value = false;
    }
  }

  function chooseTemplateSet(): void {
    actionError.value = '';
    actionMessage.value = '已切换到模板集选择态，可继续调整当前节点配置。';
    activeNode.value = 'input';
  }

  function onDetailAction(event: Event): void {
    const customEvent = event as CustomEvent<{ action?: DetailAction }>;
    const action = customEvent.detail?.action;

    if (action === 'save-workflow') {
      void saveWorkflowDefinition();
      return;
    }
    if (action === 'run-batch') {
      void runBatch();
      return;
    }
    if (action === 'run-workflow') {
      void runWorkflowDefinition();
    }
  }

  window.addEventListener('tkops:ai-content-factory-detail-action', onDetailAction as EventListener);

  onBeforeUnmount(() => {
    window.removeEventListener('tkops:ai-content-factory-detail-action', onDetailAction as EventListener);
    shell.resetAiContentFactoryDetailState();
  });

  return {
    actionError,
    actionMessage,
    activeNode,
    batchCards,
    chooseTemplateSet,
    configItems,
    definitions,
    detail,
    draftDescription,
    draftName,
    error: resource.error,
    loading: resource.loading,
    nodePalette,
    reload,
    runBatch,
    runWorkflowDefinition,
    runningBatch,
    runningWorkflow,
    saveWorkflowDefinition,
    saving,
    selectDefinition,
    selectedDefinition,
    selectedDefinitionId,
    setActiveNode,
    summaryChips,
    workflowBoardRef,
    workflowStages,
  };
}
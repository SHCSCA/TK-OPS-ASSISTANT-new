import { computed, ref } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';

const DEFAULT_FORM = {
  title: '',
  taskType: 'maintenance',
  priority: 'medium',
  resultSummary: '',
};

export function useTasksData() {
  const statusFilter = ref('');
  const draftTitle = ref(DEFAULT_FORM.title);
  const draftTaskType = ref(DEFAULT_FORM.taskType);
  const draftPriority = ref(DEFAULT_FORM.priority);
  const draftResultSummary = ref(DEFAULT_FORM.resultSummary);
  const actionError = ref('');
  const actionMessage = ref('');
  const submitting = ref(false);

  const resource = useAsyncResource(() => runtimeApi.listTasks(statusFilter.value || undefined));

  async function reload() {
    await resource.load();
  }

  function resetDraft() {
    draftTitle.value = DEFAULT_FORM.title;
    draftTaskType.value = DEFAULT_FORM.taskType;
    draftPriority.value = DEFAULT_FORM.priority;
    draftResultSummary.value = DEFAULT_FORM.resultSummary;
  }

  async function createTask() {
    if (!draftTitle.value.trim() || submitting.value) {
      return;
    }

    submitting.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.createTask({
        title: draftTitle.value.trim(),
        taskType: draftTaskType.value,
        priority: draftPriority.value,
        resultSummary: draftResultSummary.value.trim() || null,
      });
      actionMessage.value = '任务已创建并加入队列。';
      resetDraft();
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '创建任务失败';
    } finally {
      submitting.value = false;
    }
  }

  async function startTask(taskId: number) {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.startTask(taskId);
      actionMessage.value = `任务 #${taskId} 已开始执行。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '启动任务失败';
    }
  }

  async function deleteTask(taskId: number) {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.deleteTask(taskId);
      actionMessage.value = `任务 #${taskId} 已删除。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '删除任务失败';
    }
  }

  return {
    ...resource,
    actionError,
    actionMessage,
    createTask,
    deleteTask,
    draftPriority,
    draftResultSummary,
    draftTaskType,
    draftTitle,
    reload,
    startTask,
    statusFilter,
    submitting,
    tasks: computed(() => resource.data.value?.items || []),
    total: computed(() => resource.data.value?.total || 0),
  };
}

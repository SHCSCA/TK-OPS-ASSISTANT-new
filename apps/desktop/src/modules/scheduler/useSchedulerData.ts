import { computed, ref } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';

export function useSchedulerData() {
  const draftTitle = ref('');
  const draftTaskType = ref('maintenance');
  const draftPriority = ref('medium');
  const draftScheduledAt = ref('');
  const draftResultSummary = ref('');
  const actionError = ref('');
  const actionMessage = ref('');
  const submitting = ref(false);

  const resource = useAsyncResource(() => runtimeApi.getSchedulerOverview());

  async function reload() {
    await resource.load();
  }

  async function createSchedule() {
    if (!draftTitle.value.trim() || !draftScheduledAt.value || submitting.value) {
      return;
    }

    submitting.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.createSchedule({
        title: draftTitle.value.trim(),
        taskType: draftTaskType.value,
        priority: draftPriority.value,
        scheduledAt: new Date(draftScheduledAt.value).toISOString(),
        resultSummary: draftResultSummary.value.trim() || null,
      });
      actionMessage.value = '调度任务已创建。';
      draftTitle.value = '';
      draftResultSummary.value = '';
      draftScheduledAt.value = '';
      draftTaskType.value = 'maintenance';
      draftPriority.value = 'medium';
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '创建调度失败';
    } finally {
      submitting.value = false;
    }
  }

  async function toggleSchedule(taskId: number) {
    actionError.value = '';
    actionMessage.value = '';
    try {
      const task = await runtimeApi.toggleSchedule(taskId);
      actionMessage.value = `调度任务 #${taskId} 已切换为 ${task.status}。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '切换调度失败';
    }
  }

  async function deleteSchedule(taskId: number) {
    actionError.value = '';
    actionMessage.value = '';
    try {
      await runtimeApi.deleteSchedule(taskId);
      actionMessage.value = `调度任务 #${taskId} 已删除。`;
      await reload();
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '删除调度失败';
    }
  }

  return {
    ...resource,
    actionError,
    actionMessage,
    createSchedule,
    deleteSchedule,
    draftPriority,
    draftResultSummary,
    draftScheduledAt,
    draftTaskType,
    draftTitle,
    generatedAt: computed(() => resource.data.value?.generatedAt || ''),
    items: computed(() => resource.data.value?.items || []),
    reload,
    submitting,
    summary: computed(() => resource.data.value?.summary || {
      total: 0,
      scheduled: 0,
      running: 0,
      failed: 0,
    }),
    toggleSchedule,
    windows: computed(() => resource.data.value?.windows || {
      quietHours: '23:00-07:00',
      timezone: 'Asia/Shanghai',
      defaultWorkflow: '内容创作',
    }),
  };
}

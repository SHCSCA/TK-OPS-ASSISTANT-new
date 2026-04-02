import { onMounted, ref } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import type { DashboardOverview, RuntimeHealth } from '../runtime/types';

export function useDashboardData() {
  const health = ref<RuntimeHealth | null>(null);
  const overview = ref<DashboardOverview | null>(null);
  const loading = ref(true);
  const error = ref('');

  async function load() {
    loading.value = true;
    error.value = '';
    try {
      const [healthPayload, overviewPayload] = await Promise.all([
        runtimeApi.getHealth(),
        runtimeApi.getDashboardOverview(),
      ]);
      health.value = healthPayload;
      overview.value = overviewPayload;
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Runtime 请求失败';
    } finally {
      loading.value = false;
    }
  }

  onMounted(load);

  return {
    error,
    health,
    loading,
    overview,
    reload: load,
  };
}
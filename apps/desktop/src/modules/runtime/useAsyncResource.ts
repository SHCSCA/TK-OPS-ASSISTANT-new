import { onMounted, ref } from 'vue';

export function useAsyncResource<T>(loader: () => Promise<T>) {
  const data = ref<T | null>(null);
  const loading = ref(true);
  const error = ref('');

  async function load() {
    loading.value = true;
    error.value = '';
    try {
      data.value = await loader();
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Runtime 请求失败';
    } finally {
      loading.value = false;
    }
  }

  onMounted(load);

  return {
    data,
    error,
    load,
    loading,
  };
}
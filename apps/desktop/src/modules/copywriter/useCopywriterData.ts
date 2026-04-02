import { computed, ref } from 'vue';

import { streamCopywriter } from './copywriterStream';
import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';

export function useCopywriterData() {
  const resource = useAsyncResource(() => runtimeApi.getCopywriterBootstrap());
  const prompt = ref('');
  const selectedPreset = ref('copywriter');
  const selectedModel = ref('');
  const generating = ref(false);
  const streamError = ref('');
  const generatedContent = ref('');
  const streamMeta = ref<{
    provider: string;
    model: string;
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    elapsedMs: number;
  } | null>(null);

  async function generate() {
    if (!prompt.value.trim() || generating.value) {
      return;
    }

    generating.value = true;
    streamError.value = '';
    generatedContent.value = '';
    streamMeta.value = null;

    try {
      await streamCopywriter(
        {
          prompt: prompt.value.trim(),
          preset: selectedPreset.value,
          model: selectedModel.value || undefined,
        },
        (event) => {
          if (event.type === 'ai.stream.delta') {
            generatedContent.value += event.payload.delta;
            return;
          }
          if (event.type === 'ai.stream.done') {
            generatedContent.value = event.payload.content || generatedContent.value + event.payload.delta;
            streamMeta.value = {
              provider: event.payload.provider,
              model: event.payload.model,
              promptTokens: event.payload.tokens.prompt,
              completionTokens: event.payload.tokens.completion,
              totalTokens: event.payload.tokens.total,
              elapsedMs: event.payload.elapsedMs,
            };
            return;
          }
          streamError.value = event.payload.message;
        },
      );
      await resource.load();
    } catch (cause) {
      streamError.value = cause instanceof Error ? cause.message : 'AI 文案生成失败';
    } finally {
      generating.value = false;
    }
  }

  const presets = computed(() => resource.data.value?.presets || []);
  const providers = computed(() => resource.data.value?.providers || []);
  const activeProvider = computed(() => resource.data.value?.activeProvider || null);
  const usageToday = computed(() => resource.data.value?.usageToday || { prompt: 0, completion: 0, requests: 0 });
  const recommendedModels = computed(() => {
    const values = providers.value.map((provider) => provider.defaultModel).filter(Boolean);
    return [...new Set(values)];
  });

  function syncDefaults() {
    if (!selectedPreset.value) {
      selectedPreset.value = resource.data.value?.defaultPreset || 'copywriter';
    }
    if (!selectedModel.value) {
      selectedModel.value = activeProvider.value?.defaultModel || recommendedModels.value[0] || '';
    }
  }

  return {
    ...resource,
    activeProvider,
    generate,
    generatedContent,
    generating,
    presets,
    prompt,
    providers,
    recommendedModels,
    selectedModel,
    selectedPreset,
    streamError,
    streamMeta,
    syncDefaults,
    usageToday,
  };
}
import { computed, ref, watch } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';
import type { RuntimeSettingsPayload } from '../runtime/types';

function coerceNumber(value: unknown, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function resolveThemeForDom(theme: string): 'light' | 'dark' {
  if (theme === 'dark') {
    return 'dark';
  }
  if (theme === 'light') {
    return 'light';
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function syncSettingsForm(
  snapshot: RuntimeSettingsPayload | null,
  form: {
    theme: { value: string };
    language: { value: string };
    proxyUrl: { value: string };
    timeoutSeconds: { value: number };
    concurrency: { value: number };
  },
): void {
  const preferences = snapshot?.preferences;
  form.theme.value = preferences?.theme || snapshot?.theme || 'system';
  form.language.value = preferences?.language || 'zh-CN';
  form.proxyUrl.value = preferences?.proxyUrl || '';
  form.timeoutSeconds.value = coerceNumber(preferences?.timeoutSeconds, 30);
  form.concurrency.value = coerceNumber(preferences?.concurrency, 3);
}

export function useSettingsData() {
  const resource = useAsyncResource(() => runtimeApi.getSettings());
  const theme = ref('system');
  const language = ref('zh-CN');
  const proxyUrl = ref('');
  const timeoutSeconds = ref(30);
  const concurrency = ref(3);
  const saving = ref(false);
  const saveError = ref('');
  const saveMessage = ref('');

  watch(
    () => resource.data.value,
    (snapshot) => {
      syncSettingsForm(snapshot, { theme, language, proxyUrl, timeoutSeconds, concurrency });
    },
    { immediate: true },
  );

  async function saveSettings() {
    saving.value = true;
    saveError.value = '';
    saveMessage.value = '';
    try {
      const data = await runtimeApi.saveSettings({
        theme: theme.value,
        language: language.value,
        proxyUrl: proxyUrl.value,
        timeoutSeconds: timeoutSeconds.value,
        concurrency: concurrency.value,
      });
      resource.data.value = data;
      syncSettingsForm(data, { theme, language, proxyUrl, timeoutSeconds, concurrency });
      document.body.setAttribute('data-theme', resolveThemeForDom(theme.value));
      window.dispatchEvent(
        new CustomEvent('tkops:theme-preference-changed', {
          detail: { theme: theme.value },
        }),
      );
      saveMessage.value = data.message || '设置已保存';
      return data;
    } catch (cause) {
      saveError.value = cause instanceof Error ? cause.message : '设置保存失败';
      throw cause;
    } finally {
      saving.value = false;
    }
  }

  return {
    ...resource,
    settings: computed(() => resource.data.value?.items || []),
    preferences: computed(() => resource.data.value?.preferences || null),
    theme,
    language,
    proxyUrl,
    timeoutSeconds,
    concurrency,
    total: computed(() => resource.data.value?.total || 0),
    saveSettings,
    saving,
    saveError,
    saveMessage,
  };
}


import { computed, ref, watch } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';
import type { LicenseStatus, ProviderItem, RuntimeSettingsPayload } from '../runtime/types';

interface SetupResource {
  license: LicenseStatus;
  providers: ProviderItem[];
  settings: RuntimeSettingsPayload;
}

function syncSetupForm(
  snapshot: RuntimeSettingsPayload | null,
  form: {
    defaultMarket: { value: string };
    defaultWorkflow: { value: string };
    defaultModel: { value: string };
    completed: { value: boolean };
  },
) {
  const setup = snapshot?.setup;
  form.defaultMarket.value = setup?.defaultMarket || '';
  form.defaultWorkflow.value = setup?.defaultWorkflow || '';
  form.defaultModel.value = setup?.defaultModel || '';
  form.completed.value = setup?.completed ?? false;
}

export function useSetupWizardData() {
  const resource = useAsyncResource(async (): Promise<SetupResource> => {
    const [license, providers, settings] = await Promise.all([
      runtimeApi.getLicenseStatus(),
      runtimeApi.listProviders(),
      runtimeApi.getSettings(),
    ]);

    return {
      license,
      providers: providers.items,
      settings,
    };
  });
  const defaultMarket = ref('');
  const defaultWorkflow = ref('');
  const defaultModel = ref('');
  const completed = ref(false);
  const saving = ref(false);
  const saveError = ref('');
  const saveMessage = ref('');

  watch(
    () => resource.data.value?.settings || null,
    (snapshot) => {
      syncSetupForm(snapshot, { defaultMarket, defaultWorkflow, defaultModel, completed });
    },
    { immediate: true },
  );

  async function saveSetup() {
    saving.value = true;
    saveError.value = '';
    saveMessage.value = '';
    try {
      const data = await runtimeApi.saveSetup({
        defaultMarket: defaultMarket.value,
        workflow: defaultWorkflow.value,
        model: defaultModel.value,
        completed: true,
      });
      if (resource.data.value) {
        resource.data.value = {
          ...resource.data.value,
          settings: data,
        };
      }
      syncSetupForm(data, { defaultMarket, defaultWorkflow, defaultModel, completed });
      saveMessage.value = data.message || '初始化向导已保存';
      return data;
    } catch (cause) {
      saveError.value = cause instanceof Error ? cause.message : '初始化向导保存失败';
      throw cause;
    } finally {
      saving.value = false;
    }
  }

  return {
    ...resource,
    license: computed(() => resource.data.value?.license ?? null),
    providers: computed(() => resource.data.value?.providers ?? []),
    settings: computed(() => resource.data.value?.settings ?? null),
    defaultMarket,
    defaultWorkflow,
    defaultModel,
    completed,
    saveSetup,
    saving,
    saveError,
    saveMessage,
  };
}

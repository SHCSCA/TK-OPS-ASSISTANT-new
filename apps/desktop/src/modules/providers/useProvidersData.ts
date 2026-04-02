import { computed, ref } from 'vue';

import { runtimeApi } from '../runtime/runtimeApi';
import { useAsyncResource } from '../runtime/useAsyncResource';
import type { ProviderItem, ProviderUpsertPayload } from '../runtime/types';

interface ProviderFormState {
  name: string;
  providerType: string;
  apiBase: string;
  defaultModel: string;
  temperature: number;
  maxTokens: number;
  isActive: boolean;
}

const DEFAULT_FORM: ProviderFormState = {
  name: '',
  providerType: 'openai',
  apiBase: 'https://api.openai.com/v1',
  defaultModel: 'gpt-4o-mini',
  temperature: 0.7,
  maxTokens: 2048,
  isActive: true,
};

function createDefaultForm(): ProviderFormState {
  return { ...DEFAULT_FORM };
}

function toDraft(provider: ProviderItem): ProviderFormState {
  return {
    name: provider.name,
    providerType: provider.providerType,
    apiBase: provider.apiBase,
    defaultModel: provider.defaultModel,
    temperature: provider.temperature,
    maxTokens: provider.maxTokens,
    isActive: provider.isActive,
  };
}

export function useProvidersData() {
  const resource = useAsyncResource(() => runtimeApi.listProviders());
  const draft = ref<ProviderFormState>(createDefaultForm());
  const actionError = ref('');
  const actionMessage = ref('');
  const saving = ref(false);
  const testingProviderId = ref<number | null>(null);
  const deletingProviderId = ref<number | null>(null);
  const editingProviderId = ref<number | null>(null);

  function clearActionFeedback() {
    actionError.value = '';
    actionMessage.value = '';
  }

  function prepareCreate() {
    editingProviderId.value = null;
    draft.value = createDefaultForm();
    clearActionFeedback();
  }

  function beginEdit(provider: ProviderItem) {
    editingProviderId.value = provider.id;
    draft.value = toDraft(provider);
    clearActionFeedback();
  }

  function buildPayload(): ProviderUpsertPayload {
    return {
      name: draft.value.name.trim(),
      providerType: draft.value.providerType,
      apiBase: draft.value.apiBase.trim(),
      defaultModel: draft.value.defaultModel.trim(),
      temperature: Number.isFinite(draft.value.temperature) ? Number(draft.value.temperature) : 0,
      maxTokens: Number.isFinite(draft.value.maxTokens) ? Math.trunc(Number(draft.value.maxTokens)) : 0,
      isActive: Boolean(draft.value.isActive),
    };
  }

  async function refreshProviders() {
    await resource.load();
  }

  async function saveProvider() {
    if (saving.value) {
      return;
    }

    const payload = buildPayload();
    if (!payload.name) {
      actionError.value = 'Provider 名称不能为空';
      return;
    }
    if (!payload.providerType) {
      actionError.value = '请选择 Provider 类型';
      return;
    }
    if (!payload.apiBase) {
      actionError.value = 'Provider API Base 不能为空';
      return;
    }
    if (!payload.defaultModel) {
      actionError.value = 'Provider 默认模型不能为空';
      return;
    }

    saving.value = true;
    clearActionFeedback();
    const isEditing = editingProviderId.value !== null;

    try {
      const saved = isEditing
        ? await runtimeApi.updateProvider(editingProviderId.value as number, payload)
        : await runtimeApi.createProvider(payload);
      await refreshProviders();
      const refreshed = providers.value.find((provider) => provider.id === saved.id) || saved;
      beginEdit(refreshed);
      actionMessage.value = isEditing ? `已更新 Provider：${saved.name}` : `已新建 Provider：${saved.name}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : 'Provider 保存失败';
    } finally {
      saving.value = false;
    }
  }

  async function setActiveProvider(provider: ProviderItem) {
    clearActionFeedback();
    try {
      await runtimeApi.activateProvider(provider.id);
      await refreshProviders();
      actionMessage.value = `已启用 Provider：${provider.name}`;
      if (editingProviderId.value === provider.id) {
        const refreshed = providers.value.find((item) => item.id === provider.id);
        if (refreshed) {
          draft.value = toDraft(refreshed);
        }
      }
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '启用 Provider 失败';
    }
  }

  async function deleteProvider(provider: ProviderItem) {
    const confirmed = typeof window === 'undefined'
      ? true
      : window.confirm(`确定删除 Provider“${provider.name}”吗？此操作不可恢复。`);
    if (!confirmed) {
      return;
    }

    deletingProviderId.value = provider.id;
    clearActionFeedback();

    try {
      await runtimeApi.deleteProvider(provider.id);
      await refreshProviders();
      if (editingProviderId.value === provider.id) {
        prepareCreate();
      }
      actionMessage.value = `已删除 Provider：${provider.name}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '删除 Provider 失败';
    } finally {
      deletingProviderId.value = null;
    }
  }

  async function testProviderConnection(provider: ProviderItem) {
    testingProviderId.value = provider.id;
    clearActionFeedback();

    try {
      const result = await runtimeApi.testProvider(provider.id);
      actionMessage.value = `连接测试成功：${result.provider || provider.name} / ${result.model || provider.defaultModel}`;
    } catch (cause) {
      actionError.value = cause instanceof Error ? cause.message : '测试连接失败';
    } finally {
      testingProviderId.value = null;
    }
  }

  const providers = computed(() => resource.data.value?.items || []);
  const total = computed(() => resource.data.value?.total || 0);
  const activeCount = computed(() => providers.value.filter((provider) => provider.isActive).length);
  const isEditing = computed(() => editingProviderId.value !== null);

  return {
    ...resource,
    actionError,
    actionMessage,
    activeCount,
    beginEdit,
    deleteProvider,
    deletingProviderId,
    draft,
    editingProviderId,
    isEditing,
    prepareCreate,
    providers,
    refreshProviders,
    saveProvider,
    saving,
    setActiveProvider,
    testProviderConnection,
    testingProviderId,
    total,
  };
}

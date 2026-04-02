<template>
  <section class="setup-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>初始化向导</h2>
        <p class="resource-subtitle">显式保存默认市场、工作流和模型，并把完成状态写回本地设置存储。</p>
      </div>
      <button class="dashboard-refresh" type="button" @click="load">刷新</button>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载初始化状态...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <template v-else-if="license && settings">
      <p v-if="saveError" class="dashboard-banner dashboard-banner-error">{{ saveError }}</p>
      <p v-if="saveMessage" class="dashboard-banner">{{ saveMessage }}</p>

      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">许可证</p>
          <strong>{{ license.activated ? '已激活' : '待激活' }}</strong>
          <span>{{ license.tier || license.error || 'free' }}</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">AI Provider</p>
          <strong>{{ providers.length }}</strong>
          <span>{{ activeProviderName }}</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">完成状态</p>
          <strong>{{ completed ? '已完成' : '待完成' }}</strong>
          <span>{{ workflowLabel }}</span>
        </article>
      </div>

      <div class="setup-layout">
        <section class="dashboard-section">
          <div class="dashboard-section-title">
            <h3>初始化配置</h3>
            <span>显式提交，不自动保存</span>
          </div>
          <div class="setup-kv-grid">
            <div class="setup-kv-item">
              <span>默认市场</span>
              <input v-model="defaultMarket" type="text" placeholder="CN / US / SEA" />
            </div>
            <div class="setup-kv-item">
              <span>默认工作流</span>
              <input v-model="defaultWorkflow" type="text" placeholder="内容创作" />
            </div>
            <div class="setup-kv-item">
              <span>默认模型</span>
              <input v-model="defaultModel" type="text" placeholder="gpt-4o-mini" />
            </div>
            <div class="setup-kv-item">
              <span>完成状态</span>
              <strong>{{ completed ? '已完成' : '未完成' }}</strong>
            </div>
          </div>
          <div class="setup-step-meta">
            <button class="dashboard-refresh" type="button" :disabled="saving" @click="handleSaveSetup">
              {{ saving ? '保存中...' : '保存并标记已完成' }}
            </button>
            <span>提交后会写入默认市场、工作流、模型与完成状态。</span>
          </div>
        </section>

        <section class="dashboard-section">
          <div class="dashboard-section-title">
            <h3>当前配置摘要</h3>
            <span>/license/status + /providers + /settings</span>
          </div>
          <div class="setup-kv-grid">
            <div class="setup-kv-item">
              <span>机器码</span>
              <strong>{{ license.machineIdShort || '未生成' }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>复合机器码</span>
              <strong>{{ compoundShort }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>默认模型</span>
              <strong>{{ defaultModelLabel }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>默认市场</span>
              <strong>{{ marketLabel }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>默认工作流</span>
              <strong>{{ workflowLabel }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>许可证有效期</span>
              <strong>{{ expiryLabel }}</strong>
            </div>
          </div>
          <p class="setup-note">下一步优先级由当前未完成项决定，提交保存后会立即回显到这里。</p>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { formatDateTime } from '../../modules/runtime/format';
import { useSetupWizardData } from '../../modules/setup/useSetupWizardData';

const {
  error,
  license,
  load,
  loading,
  providers,
  saveError,
  saveMessage,
  saveSetup,
  saving,
  settings,
  completed,
  defaultMarket,
  defaultWorkflow,
  defaultModel,
} = useSetupWizardData();

const activeProvider = computed(() => providers.value.find((provider) => provider.isActive) ?? providers.value[0] ?? null);
const activeProviderName = computed(() => activeProvider.value?.name || '未配置');
const defaultModelLabel = computed(() => defaultModel.value || activeProvider.value?.defaultModel || '未选择');
const marketLabel = computed(() => defaultMarket.value || settings.value?.setup?.defaultMarket || '未设置');
const workflowLabel = computed(() => defaultWorkflow.value || settings.value?.setup?.defaultWorkflow || '待选择');
const expiryLabel = computed(() => {
  if (!license.value) {
    return '未激活';
  }
  if (license.value.isPermanent) {
    return '永久有效';
  }
  return formatDateTime(license.value.expiry);
});
const compoundShort = computed(() => {
  const value = license.value?.compoundId || '';
  return value ? `${value.slice(0, 19)}...` : '未生成';
});

async function handleSaveSetup() {
  try {
    await saveSetup();
  } catch {
    // 错误已经由 saveError 接管，这里不重复抛出。
  }
}
</script>

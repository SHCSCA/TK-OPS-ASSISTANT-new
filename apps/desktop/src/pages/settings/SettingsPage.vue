<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>系统设置</h2>
        <p class="resource-subtitle">显式保存常用设置，支持主题、语言、代理、超时与并发的真实回写。</p>
      </div>
      <button class="dashboard-refresh" type="button" @click="load">刷新</button>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载系统设置...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>
    <template v-else>
      <p v-if="saveError" class="dashboard-banner dashboard-banner-error">{{ saveError }}</p>
      <p v-if="saveMessage" class="dashboard-banner">{{ saveMessage }}</p>

      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">主题</p>
          <strong>{{ preferences?.theme || theme }}</strong>
          <span>当前保存值</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">语言</p>
          <strong>{{ preferences?.language || language }}</strong>
          <span>当前保存值</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">网络</p>
          <strong>{{ networkSummary }}</strong>
          <span>代理 / 超时 / 并发</span>
        </article>
      </div>

      <form class="setup-layout" @submit.prevent="handleSaveSettings">
        <section class="dashboard-section">
          <div class="dashboard-section-title">
            <h3>常用设置</h3>
            <span>显式提交，不自动保存</span>
          </div>
          <div class="settings-grid">
            <article class="resource-card">
              <p class="eyebrow">主题</p>
              <label>
                <select v-model="theme">
                  <option value="system">跟随系统</option>
                  <option value="light">浅色</option>
                  <option value="dark">深色</option>
                </select>
              </label>
            </article>
            <article class="resource-card">
              <p class="eyebrow">语言</p>
              <label>
                <select v-model="language">
                  <option value="zh-CN">简体中文</option>
                  <option value="en-US">English</option>
                </select>
              </label>
            </article>
            <article class="resource-card">
              <p class="eyebrow">代理地址</p>
              <label>
                <input v-model="proxyUrl" type="text" placeholder="http://127.0.0.1:7890" />
              </label>
            </article>
            <article class="resource-card">
              <p class="eyebrow">超时（秒）</p>
              <label>
                <input v-model.number="timeoutSeconds" type="number" min="1" step="1" />
              </label>
            </article>
            <article class="resource-card">
              <p class="eyebrow">并发数</p>
              <label>
                <input v-model.number="concurrency" type="number" min="1" step="1" />
              </label>
            </article>
          </div>
          <div class="setup-step-meta">
            <button class="dashboard-refresh" type="submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存设置' }}
            </button>
            <span>保存后会立即回显到上方摘要和设置列表。</span>
          </div>
        </section>

        <section class="dashboard-section">
          <div class="dashboard-section-title">
            <h3>原始设置</h3>
            <span>来自 /settings 的 key-value 快照</span>
          </div>
          <div v-if="settings.length" class="settings-grid">
            <article v-for="item in settings" :key="item.key" class="resource-card">
              <p class="eyebrow">{{ item.key }}</p>
              <strong class="setting-value">{{ item.value || '空值' }}</strong>
            </article>
          </div>
          <p v-else class="dashboard-empty">当前没有设置数据。</p>
        </section>
      </form>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { useSettingsData } from '../../modules/settings/useSettingsData';

const {
  error,
  language,
  load,
  loading,
  preferences,
  proxyUrl,
  concurrency,
  saveError,
  saveMessage,
  saveSettings,
  saving,
  settings,
  theme,
  timeoutSeconds,
} = useSettingsData();

const networkSummary = computed(() => {
  const proxy = preferences.value?.proxyUrl || proxyUrl.value || '未配置';
  const timeout = preferences.value?.timeoutSeconds || timeoutSeconds.value;
  const workers = preferences.value?.concurrency || concurrency.value;
  return `${proxy} / ${timeout}s / ${workers}`;
});

async function handleSaveSettings() {
  try {
    await saveSettings();
  } catch {
    // 错误已经由 saveError 接管，这里不重复抛出。
  }
}
</script>

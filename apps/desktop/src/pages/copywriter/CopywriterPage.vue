<template>
  <section class="copywriter-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>AI 文案生成</h2>
        <p class="resource-subtitle">页面直接接入 runtime 的 preset、provider 和流式生成链路，不再依赖旧桥接轮询。</p>
      </div>
      <button class="dashboard-refresh" type="button" @click="reloadBootstrap">刷新</button>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载 AI 文案配置...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <template v-else>
      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">默认预设</p>
          <strong>{{ selectedPresetLabel }}</strong>
          <span>{{ presets.length }} 个可选预设</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">当前供应商</p>
          <strong>{{ activeProvider?.name || '未配置' }}</strong>
          <span>{{ activeProvider?.defaultModel || '无默认模型' }}</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">今日用量</p>
          <strong>{{ usageToday.requests }}</strong>
          <span>Prompt {{ usageToday.prompt }} / Completion {{ usageToday.completion }}</span>
        </article>
      </div>

      <div class="copywriter-layout">
        <section class="dashboard-section copywriter-form-section">
          <div class="dashboard-section-title">
            <h3>生成参数</h3>
            <span>HTTP /copywriter/bootstrap</span>
          </div>
          <label class="copywriter-field">
            <span>写作预设</span>
            <select v-model="selectedPreset">
              <option v-for="preset in presets" :key="preset.key" :value="preset.key">
                {{ preset.icon }} {{ preset.name }}
              </option>
            </select>
          </label>
          <label class="copywriter-field">
            <span>模型</span>
            <select v-model="selectedModel">
              <option value="">跟随供应商默认模型</option>
              <option v-for="model in recommendedModels" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </label>
          <label class="copywriter-field">
            <span>产品信息 / 写作需求</span>
            <textarea
              v-model="prompt"
              rows="10"
              placeholder="输入产品卖点、目标渠道、受众人群和风格要求，例如：生成一段适合 TikTok 护肤短视频的 30 秒口播文案。"
            />
          </label>
          <div class="copywriter-actions">
            <button class="dashboard-refresh" type="button" :disabled="generating || !prompt.trim()" @click="generate">
              {{ generating ? '正在生成...' : '立即生成文案' }}
            </button>
            <span class="copywriter-hint">流式通道：WS /ws/copywriter-stream</span>
          </div>
        </section>

        <section class="dashboard-section copywriter-output-section">
          <div class="dashboard-section-title">
            <h3>输出版本</h3>
            <span>{{ streamMeta ? `${streamMeta.provider} / ${streamMeta.model}` : '等待生成' }}</span>
          </div>
          <p v-if="streamError" class="dashboard-banner dashboard-banner-error">{{ streamError }}</p>
          <div v-if="generatedContent" class="copywriter-output-body">
            <pre>{{ generatedContent }}</pre>
          </div>
          <p v-else class="dashboard-empty">填写需求后点击「立即生成文案」，流式结果会实时写入这里。</p>
          <div v-if="streamMeta" class="copywriter-meta-grid">
            <div class="setup-kv-item">
              <span>耗时</span>
              <strong>{{ streamMeta.elapsedMs }} ms</strong>
            </div>
            <div class="setup-kv-item">
              <span>Token 总量</span>
              <strong>{{ streamMeta.totalTokens }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>Prompt</span>
              <strong>{{ streamMeta.promptTokens }}</strong>
            </div>
            <div class="setup-kv-item">
              <span>Completion</span>
              <strong>{{ streamMeta.completionTokens }}</strong>
            </div>
          </div>
        </section>

        <section class="dashboard-section copywriter-side-section">
          <div class="dashboard-section-title">
            <h3>当前策略</h3>
            <span>preset / provider</span>
          </div>
          <article class="resource-card">
            <p class="eyebrow">选中预设</p>
            <strong>{{ selectedPresetLabel }}</strong>
            <p class="resource-card-meta">{{ selectedPresetSystem }}</p>
          </article>
          <article class="resource-card">
            <p class="eyebrow">可用供应商</p>
            <strong>{{ providers.length }}</strong>
            <p class="resource-card-meta">优先使用激活供应商，失败后由 ChatService 承担 fallback。</p>
          </article>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, watchEffect } from 'vue';

import { useCopywriterData } from '../../modules/copywriter/useCopywriterData';

const {
  activeProvider,
  data,
  error,
  generate,
  generatedContent,
  generating,
  load,
  loading,
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
} = useCopywriterData();

watchEffect(() => {
  if (data.value) {
    syncDefaults();
  }
});

const selectedPresetRecord = computed(() => presets.value.find((preset) => preset.key === selectedPreset.value) || null);
const selectedPresetLabel = computed(() => selectedPresetRecord.value?.name || '未选择');
const selectedPresetSystem = computed(() => selectedPresetRecord.value?.system || '当前没有系统提示词。');

function reloadBootstrap() {
  void load();
}
</script>
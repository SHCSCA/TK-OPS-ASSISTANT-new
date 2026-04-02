<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>AI Provider</h2>
        <p class="resource-subtitle">现在可以直接新建、编辑、启用、删除和测试连接，所有动作都走真实 runtime 数据。</p>
      </div>
      <button class="dashboard-refresh" type="button" @click="prepareCreate">新建 Provider</button>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载 provider 列表...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <template v-else>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>

      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">总 Provider</p>
          <strong>{{ total }}</strong>
          <span>来自 /providers</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">已激活</p>
          <strong>{{ activeCount }}</strong>
          <span>isActive = true</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">当前模式</p>
          <strong>{{ isEditing ? '编辑 Provider' : '新建 Provider' }}</strong>
          <span>{{ isEditing ? `正在编辑 #${editingProviderId}` : '准备创建新配置' }}</span>
        </article>
      </div>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>{{ isEditing ? '编辑 Provider' : '新建 Provider' }}</h3>
          <span>提交后会直接写入 runtime 数据</span>
        </div>
        <form class="copywriter-form" @submit.prevent="saveProvider">
          <label class="copywriter-field">
            <span>Provider 名称</span>
            <input v-model="draft.name" type="text" maxlength="80" placeholder="例如 OpenAI 主账号" />
          </label>
          <label class="copywriter-field">
            <span>Provider 类型</span>
            <select v-model="draft.providerType">
              <option value="openai">openai</option>
              <option value="anthropic">anthropic</option>
              <option value="local">local</option>
              <option value="custom">custom</option>
            </select>
          </label>
          <label class="copywriter-field">
            <span>API Base</span>
            <input v-model="draft.apiBase" type="text" maxlength="255" placeholder="https://api.openai.com/v1" />
          </label>
          <label class="copywriter-field">
            <span>默认模型</span>
            <input v-model="draft.defaultModel" type="text" maxlength="80" placeholder="gpt-4o-mini" />
          </label>
          <div class="resource-summary-grid">
            <label class="copywriter-field">
              <span>温度</span>
              <input v-model.number="draft.temperature" type="number" min="0" max="2" step="0.1" />
            </label>
            <label class="copywriter-field">
              <span>最大 Tokens</span>
              <input v-model.number="draft.maxTokens" type="number" min="1" step="1" />
            </label>
          </div>
          <label class="copywriter-field">
            <span>启用状态</span>
            <select v-model="draft.isActive">
              <option :value="true">启用</option>
              <option :value="false">停用</option>
            </select>
          </label>
          <div class="copywriter-actions">
            <button class="dashboard-refresh" type="submit" :disabled="saving">
              {{ saving ? '保存中...' : isEditing ? '保存修改' : '创建 Provider' }}
            </button>
            <button class="dashboard-refresh" type="button" @click="prepareCreate">重置为新建</button>
          </div>
        </form>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>Provider 列表</h3>
          <span>支持编辑、启用、删除与测试连接</span>
        </div>

        <div v-if="providers.length" class="resource-list">
          <article v-for="provider in providers" :key="provider.id" class="resource-card">
            <div class="resource-card-head">
              <div>
                <strong>{{ provider.name }}</strong>
                <p>{{ provider.providerType }} / {{ provider.defaultModel }}</p>
              </div>
              <span class="status-chip">{{ provider.isActive ? 'active' : 'inactive' }}</span>
            </div>
            <div class="resource-card-grid">
              <span>温度 {{ provider.temperature }}</span>
              <span>最大 Tokens {{ provider.maxTokens }}</span>
              <span>API Base {{ provider.apiBase }}</span>
              <span>创建时间 {{ formatDateTime(provider.createdAt) }}</span>
            </div>
            <div class="copywriter-actions">
              <button class="dashboard-refresh" type="button" @click="beginEdit(provider)">编辑 Provider</button>
              <button class="dashboard-refresh" type="button" :disabled="testingProviderId === provider.id" @click="testProviderConnection(provider)">
                {{ testingProviderId === provider.id ? '测试中...' : '测试连接' }}
              </button>
              <button
                class="dashboard-refresh"
                type="button"
                :disabled="provider.isActive"
                @click="setActiveProvider(provider)"
              >
                {{ provider.isActive ? '已启用' : '启用' }}
              </button>
              <button
                class="dashboard-refresh"
                type="button"
                :disabled="deletingProviderId === provider.id"
                @click="deleteProvider(provider)"
              >
                {{ deletingProviderId === provider.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </article>
        </div>

        <p v-else class="dashboard-empty">当前没有 provider 数据。</p>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { formatDateTime } from '../../modules/runtime/format';
import { useProvidersData } from '../../modules/providers/useProvidersData';

const {
  actionError,
  actionMessage,
  activeCount,
  beginEdit,
  deleteProvider,
  deletingProviderId,
  draft,
  editingProviderId,
  error,
  isEditing,
  loading,
  prepareCreate,
  providers,
  saveProvider,
  saving,
  setActiveProvider,
  testProviderConnection,
  testingProviderId,
  total,
} = useProvidersData();
</script>

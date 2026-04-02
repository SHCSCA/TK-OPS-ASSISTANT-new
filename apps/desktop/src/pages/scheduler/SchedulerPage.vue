<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>任务调度</h2>
        <p class="resource-subtitle">先把最小调度闭环接上：创建计划、启停切换、删除，并继续消费 runtime 的调度概览。</p>
      </div>
      <button class="dashboard-refresh" type="button" @click="reload">刷新</button>
    </div>

    <div class="dashboard-section task-form-section">
      <div class="dashboard-section-title">
        <h3>新建调度</h3>
        <span>POST /scheduler</span>
      </div>
      <div class="task-form-grid">
        <label class="copywriter-field">
          <span>调度标题</span>
          <input v-model="draftTitle" type="text" placeholder="例如：每日晚高峰评论分流" />
        </label>
        <label class="copywriter-field">
          <span>任务类型</span>
          <select v-model="draftTaskType">
            <option value="maintenance">maintenance</option>
            <option value="report">report</option>
            <option value="publish">publish</option>
            <option value="interact">interact</option>
            <option value="scrape">scrape</option>
          </select>
        </label>
        <label class="copywriter-field">
          <span>优先级</span>
          <select v-model="draftPriority">
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>
        <label class="copywriter-field">
          <span>计划执行时间</span>
          <input v-model="draftScheduledAt" type="datetime-local" />
        </label>
        <label class="copywriter-field task-form-grid-wide">
          <span>调度摘要</span>
          <input v-model="draftResultSummary" type="text" placeholder="例如：等待晚间窗口触发" />
        </label>
      </div>
      <div class="copywriter-actions">
        <button
          class="dashboard-refresh"
          type="button"
          :disabled="submitting || !draftTitle.trim() || !draftScheduledAt"
          @click="handleCreateSchedule"
        >
          {{ submitting ? '正在创建...' : '创建调度' }}
        </button>
      </div>
      <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载任务调度...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <template v-else>
      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">调度总量</p>
          <strong>{{ summary.total }}</strong>
          <span>来自 /scheduler</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">已排期</p>
          <strong>{{ summary.scheduled }}</strong>
          <span>scheduledAt 已写入</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">运行中</p>
          <strong>{{ summary.running }}</strong>
          <span>失败 {{ summary.failed }}</span>
        </article>
      </div>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>时间窗</h3>
          <span>{{ generatedAt || '等待生成' }}</span>
        </div>
        <div class="setup-kv-grid">
          <div class="setup-kv-item">
            <span>静默时段</span>
            <strong>{{ windows.quietHours }}</strong>
          </div>
          <div class="setup-kv-item">
            <span>时区</span>
            <strong>{{ windows.timezone }}</strong>
          </div>
          <div class="setup-kv-item">
            <span>默认工作流</span>
            <strong>{{ windows.defaultWorkflow }}</strong>
          </div>
          <div class="setup-kv-item">
            <span>调度状态</span>
            <strong>{{ summary.running > 0 ? '正在执行' : '等待触发' }}</strong>
          </div>
        </div>
      </section>

      <div v-if="items.length" class="resource-list">
        <article v-for="item in items" :key="item.id" class="resource-card">
          <div class="resource-card-head">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.taskType }} / {{ item.priority }}</p>
            </div>
            <span class="status-chip">{{ item.status }}</span>
          </div>
          <div class="resource-card-grid">
            <span>排期 {{ formatDateTime(item.scheduledAt) }}</span>
            <span>账号 {{ item.accountUsername || '未绑定账号' }}</span>
          </div>
          <p class="resource-card-meta">{{ item.resultSummary || '当前没有调度摘要' }}</p>
          <div class="task-actions">
            <button class="dashboard-refresh" type="button" @click="handleToggleSchedule(item.id)">
              {{ item.status === 'paused' ? '恢复' : '暂停' }}
            </button>
            <button class="dashboard-refresh task-delete-button" type="button" @click="handleDeleteSchedule(item.id)">
              删除
            </button>
          </div>
        </article>
      </div>
      <p v-else class="dashboard-empty">当前没有可展示的调度任务。</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { formatDateTime } from '../../modules/runtime/format';
import { useSchedulerData } from '../../modules/scheduler/useSchedulerData';

const {
  actionError,
  actionMessage,
  createSchedule,
  deleteSchedule,
  draftPriority,
  draftResultSummary,
  draftScheduledAt,
  draftTaskType,
  draftTitle,
  error,
  generatedAt,
  items,
  loading,
  reload,
  submitting,
  summary,
  toggleSchedule,
  windows,
} = useSchedulerData();

function handleCreateSchedule() {
  void createSchedule();
}

function handleToggleSchedule(taskId: number) {
  void toggleSchedule(taskId);
}

function handleDeleteSchedule(taskId: number) {
  void deleteSchedule(taskId);
}
</script>

<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>任务队列</h2>
        <p class="resource-subtitle">在新桌面壳里直接创建、启动和删除任务，验证任务主链路已经脱离旧桥接。</p>
      </div>
      <button class="dashboard-refresh" type="button" @click="reload">刷新</button>
    </div>

    <div class="dashboard-section task-form-section">
      <div class="dashboard-section-title">
        <h3>新建任务</h3>
        <span>POST /tasks</span>
      </div>
      <div class="task-form-grid">
        <label class="copywriter-field">
          <span>任务标题</span>
          <input v-model="draftTitle" type="text" placeholder="例如：生成晚间运营日报" />
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
          <span>结果摘要</span>
          <input v-model="draftResultSummary" type="text" placeholder="可选，帮助定位任务用途" />
        </label>
      </div>
      <div class="copywriter-actions">
        <button
          class="dashboard-refresh"
          type="button"
          :disabled="submitting || !draftTitle.trim()"
          @click="handleCreateTask"
        >
          {{ submitting ? '正在创建...' : '创建任务' }}
        </button>
        <label class="copywriter-field task-filter-field">
          <span>状态筛选</span>
          <select v-model="statusFilter" @change="reload">
            <option value="">全部</option>
            <option value="pending">pending</option>
            <option value="running">running</option>
            <option value="paused">paused</option>
            <option value="completed">completed</option>
            <option value="failed">failed</option>
          </select>
        </label>
      </div>
      <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载任务队列...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <template v-else>
      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">总任务数</p>
          <strong>{{ total }}</strong>
          <span>来自 /tasks</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">运行中</p>
          <strong>{{ runningCount }}</strong>
          <span>status = running</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">失败任务</p>
          <strong>{{ failedCount }}</strong>
          <span>status = failed</span>
        </article>
      </div>

      <div v-if="tasks.length" class="resource-list">
        <article v-for="task in tasks" :key="task.id" class="resource-card">
          <div class="resource-card-head">
            <div>
              <strong>{{ task.title }}</strong>
              <p>{{ task.taskType }} / {{ task.priority }}</p>
            </div>
            <span class="status-chip">{{ task.status }}</span>
          </div>
          <div class="resource-card-grid">
            <span>账号 {{ task.accountUsername || '未绑定' }}</span>
            <span>创建 {{ formatDateTime(task.createdAt) }}</span>
            <span>开始 {{ formatDateTime(task.startedAt) }}</span>
            <span>结束 {{ formatDateTime(task.finishedAt) }}</span>
          </div>
          <p class="resource-card-meta">结果摘要：{{ task.resultSummary || '暂无结果摘要' }}</p>
          <div class="task-actions">
            <button
              class="dashboard-refresh"
              type="button"
              :disabled="task.status === 'running' || task.status === 'completed'"
              @click="handleStartTask(task.id)"
            >
              启动
            </button>
            <button class="dashboard-refresh task-delete-button" type="button" @click="handleDeleteTask(task.id)">
              删除
            </button>
          </div>
        </article>
      </div>
      <p v-else class="dashboard-empty">当前没有任务数据。</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { formatDateTime } from '../../modules/runtime/format';
import { useTasksData } from '../../modules/tasks/useTasksData';

const {
  actionError,
  actionMessage,
  createTask,
  deleteTask,
  draftPriority,
  draftResultSummary,
  draftTaskType,
  draftTitle,
  error,
  loading,
  reload,
  startTask,
  statusFilter,
  submitting,
  tasks,
  total,
} = useTasksData();

const runningCount = computed(() => tasks.value.filter((task) => task.status === 'running').length);
const failedCount = computed(() => tasks.value.filter((task) => task.status === 'failed').length);

function handleCreateTask() {
  void createTask();
}

function handleStartTask(taskId: number) {
  void startTask(taskId);
}

function handleDeleteTask(taskId: number) {
  void deleteTask(taskId);
}
</script>

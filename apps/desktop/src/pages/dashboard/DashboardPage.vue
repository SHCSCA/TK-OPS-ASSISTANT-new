<template>
  <section class="page-shell dashboard-workbench">
    <div class="breadcrumbs">
      <span>dashboard</span>
      <span>/</span>
      <span>概览数据看板</span>
    </div>

    <div class="page-header">
      <div>
        <div class="eyebrow">全局总览入口</div>
        <h1>概览数据看板</h1>
        <p>把 KPI、AI 任务、系统健康度、活动流和快捷操作收拢到同一屏，支持管理者先判断风险，再继续调度和下钻。</p>
      </div>
      <div class="header-actions">
        <div class="segmented">
          <button
            v-for="item in rangeOptions"
            :key="item.key"
            type="button"
            :class="{ 'is-active': range === item.key }"
            @click="setRange(item.key)"
          >
            {{ item.label }}
          </button>
        </div>
        <button class="secondary-button" type="button" @click="openHistory">查看历史</button>
        <button class="primary-button" type="button" @click="openTaskQueue">新建任务</button>
      </div>
    </div>

    <div v-if="loading" class="notice-banner">
      <strong>正在加载概览数据</strong>
      <p class="subtle">正在读取 runtime 健康、任务趋势与活动摘要。</p>
    </div>
    <div v-else-if="error" class="notice-banner notice-banner--error">
      <strong>概览加载失败</strong>
      <p class="subtle">{{ error }}</p>
    </div>

    <section v-else class="section-stack">
      <div class="stat-grid">
        <article
          v-for="metric in displayMetrics"
          :key="metric.key"
          class="stat-card dashboard-stat-link"
          role="button"
          tabindex="0"
          @click="openMetric(metric.key)"
          @keydown.enter.prevent="openMetric(metric.key)"
        >
          <div>
            <div class="subtle">{{ metric.label }}</div>
            <div class="stat-card__value metric-value">{{ metric.value }}</div>
          </div>
          <div class="stat-card__delta">
            <span>·</span>
            <span class="subtle metric-meta">{{ metric.meta }}</span>
          </div>
        </article>
      </div>

      <div class="content-grid shell-content-grid">
        <div class="section-stack">
          <section class="chart-card">
            <div class="chart-card__header">
              <div>
                <strong>AI 任务趋势图</strong>
                <div class="subtle">X 轴为时间，Y 轴为任务数量，用于查看新增、完成、异常三类任务变化。</div>
              </div>
              <div class="chart-legend">
                <span><span class="legend-dot legend-dot--created"></span>新增任务</span>
                <span><span class="legend-dot legend-dot--completed"></span>已完成任务</span>
                <span><span class="legend-dot legend-dot--failed"></span>异常任务</span>
              </div>
            </div>

            <div v-if="trendItems.length" class="dashboard-trend-chart dashboard-trend-chart--summary">
              <div class="dashboard-trend-group dashboard-trend-group--summary">
                <div class="dashboard-trend-group__label">{{ trendItems[0].label }}</div>
                <div class="dashboard-trend-group__metrics">
                  <div class="dashboard-trend-metric">
                    <span class="dashboard-trend-metric__name">新增</span>
                    <span class="dashboard-trend-track">
                      <span class="dashboard-trend-fill is-created" :style="{ width: trendRatio(trendItems[0].created) }"></span>
                    </span>
                    <strong class="dashboard-trend-metric__value">{{ trendItems[0].created }}</strong>
                  </div>
                  <div class="dashboard-trend-metric">
                    <span class="dashboard-trend-metric__name">完成</span>
                    <span class="dashboard-trend-track">
                      <span class="dashboard-trend-fill is-completed" :style="{ width: trendRatio(trendItems[0].completed) }"></span>
                    </span>
                    <strong class="dashboard-trend-metric__value">{{ trendItems[0].completed }}</strong>
                  </div>
                  <div class="dashboard-trend-metric">
                    <span class="dashboard-trend-metric__name">异常</span>
                    <span class="dashboard-trend-track">
                      <span class="dashboard-trend-fill is-failed" :style="{ width: trendRatio(trendItems[0].failed) }"></span>
                    </span>
                    <strong class="dashboard-trend-metric__value">{{ trendItems[0].failed }}</strong>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">当前时间范围暂无趋势数据。</div>
          </section>

          <section class="table-card">
            <div class="table-card__header">
              <div>
                <strong>近期活动流</strong>
                <div class="subtle">基于真实任务与活动日志，帮助回看高影响动作与异常处理。</div>
              </div>
              <button class="ghost-button" type="button" @click="openHistory">查看全部</button>
            </div>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>动作名称</th>
                    <th>关联对象</th>
                    <th>分类</th>
                    <th>状态</th>
                    <th>时间</th>
                  </tr>
                </thead>
                <tbody v-if="activityItems.length">
                  <tr
                    v-for="item in activityItems"
                    :key="`${item.title}-${item.time}-${item.category}`"
                    class="route-row"
                    :class="{ 'is-selected': selectedActivity?.title === item.title && selectedActivity?.time === item.time }"
                    @click="selectActivity(item)"
                  >
                    <td><strong>{{ item.title }}</strong></td>
                    <td>{{ item.entity }}</td>
                    <td>{{ item.category }}</td>
                    <td><span class="status-chip" :class="activityTone(item.status)">{{ item.status }}</span></td>
                    <td class="subtle metric-nowrap">{{ formatTime(item.time) }}</td>
                  </tr>
                </tbody>
                <tbody v-else>
                  <tr>
                    <td colspan="5" class="subtle">暂无活动数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <div class="section-stack">
          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>AI / 系统状态</strong>
                <div class="subtle">聚焦真实运行摘要，不再显示伪服务名。</div>
              </div>
              <span class="status-chip" :class="systemSummaryTone">{{ systemSummaryText }}</span>
            </div>
            <div v-if="systemItems.length" class="metric-list dashboard-systems-grid">
              <button
                v-for="item in systemItems"
                :key="item.key"
                type="button"
                class="dashboard-system-card"
                :class="{ 'is-selected': selectedSystem?.key === item.key }"
                @click="selectSystem(item)"
              >
                <div class="dashboard-system-card__head">
                  <strong>{{ item.title }}</strong>
                  <span class="pill" :class="item.tone">{{ item.status }}</span>
                </div>
                <div class="dashboard-system-card__summary">{{ item.summary }}</div>
              </button>
            </div>
            <div v-else class="empty-state">系统状态暂不可用。</div>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>快捷入口 / 待办</strong>
                <div class="subtle">保留最常用动作，避免用户在多域导航中迷路。</div>
              </div>
            </div>
            <div class="action-grid shell-action-grid">
              <button class="secondary-button" type="button" @click="openTaskQueue('failed')">处理账号异常</button>
              <button class="secondary-button" type="button" @click="openRoute('ai-copywriter')">启动内容批量生成</button>
              <button class="secondary-button" type="button" @click="openRoute('network-diagnostics')">网络诊断</button>
              <button class="secondary-button" type="button" @click="openRoute('scheduled-publish')">审核定时发布</button>
            </div>
          </section>
        </div>
      </div>
    </section>

    <div v-if="!loading && !error && !hasDashboardData" class="empty-state">暂无可展示数据，请稍后刷新重试。</div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';

import { useDashboardData } from '../../modules/dashboard/useDashboardData';
import type { DashboardMetric } from '../../modules/runtime/types';

const router = useRouter();
const {
  activityItems,
  error,
  hasDashboardData,
  loading,
  overview,
  range,
  rangeOptions,
  selectActivity,
  selectSystem,
  selectedActivity,
  selectedSystem,
  setRange,
  systemItems,
  trendItems,
} = useDashboardData();

function metricByKeyFragment(fragment: string): DashboardMetric | undefined {
  const metrics = overview.value?.metrics ?? [];
  return metrics.find((item) => item.key.toLowerCase().includes(fragment));
}

const displayMetrics = computed(() => {
  const accountMetric = metricByKeyFragment('account');
  const followerMetric = metricByKeyFragment('follower');
  const taskMetric = metricByKeyFragment('task');
  const assetMetric = metricByKeyFragment('asset');

  return [
    {
      key: 'accounts-total',
      label: accountMetric?.label || '账号总数',
      value: Number(accountMetric?.value || 0),
      meta: accountMetric?.meta || '--',
    },
    {
      key: 'followers-total',
      label: followerMetric?.label || '粉丝样本',
      value: Number(followerMetric?.value || 0),
      meta: followerMetric?.meta || '--',
    },
    {
      key: 'tasks-total',
      label: taskMetric?.label || '任务总数',
      value: Number(taskMetric?.value || 0),
      meta: taskMetric?.meta || '--',
    },
    {
      key: 'assets-total',
      label: assetMetric?.label || '素材总数',
      value: Number(assetMetric?.value || 0),
      meta: assetMetric?.meta || '--',
    },
  ];
});

const systemSummaryTone = computed(() => {
  if (!systemItems.value.length) {
    return 'warning';
  }
  if (systemItems.value.some((item) => item.tone === 'error')) {
    return 'error';
  }
  if (systemItems.value.some((item) => item.tone === 'warning')) {
    return 'warning';
  }
  return 'success';
});

const systemSummaryText = computed(() => {
  if (!systemItems.value.length) {
    return '暂无数据';
  }
  if (systemSummaryTone.value === 'error') {
    return '存在异常';
  }
  if (systemSummaryTone.value === 'warning') {
    return '需要关注';
  }
  return '运行稳定';
});

const trendMax = computed(() => {
  const current = trendItems.value[0];
  if (!current) {
    return 1;
  }
  return Math.max(1, current.created, current.completed, current.failed);
});

function trendRatio(value: number): string {
  const percent = Math.max(10, Math.round((Math.max(0, Number(value || 0)) / trendMax.value) * 100));
  return `${Math.min(percent, 100)}%`;
}

function formatTime(value: string): string {
  if (!value) {
    return '--';
  }
  if (value.includes('T')) {
    return value.replace('T', ' ').slice(5, 16);
  }
  return value;
}

function activityTone(status: string): 'success' | 'warning' | 'error' | 'info' {
  const normalized = String(status || '').trim().toLowerCase();
  if (normalized.includes('error') || normalized.includes('failed') || normalized.includes('异常')) {
    return 'error';
  }
  if (normalized.includes('warn') || normalized.includes('pending') || normalized.includes('关注')) {
    return 'warning';
  }
  if (normalized.includes('ok') || normalized.includes('success') || normalized.includes('正常')) {
    return 'success';
  }
  return 'info';
}

function openRoute(routeName: string): void {
  void router.push({ name: routeName });
}

function openTaskQueue(status: string | Event = 'pending'): void {
  const resolvedStatus = typeof status === 'string' ? status : 'pending';
  void router.push({ name: 'task-queue', query: { status: resolvedStatus } });
}

function openHistory(): void {
  void router.push({ name: 'report-center' });
}

function openMetric(key: string): void {
  const normalized = key.toLowerCase();
  if (normalized.includes('task') || normalized.includes('failed')) {
    openTaskQueue(normalized.includes('failed') ? 'failed' : 'pending');
    return;
  }
  if (normalized.includes('account')) {
    openRoute('account');
    return;
  }
  if (normalized.includes('provider') || normalized.includes('asset')) {
    openRoute('ai-provider');
    return;
  }
  openRoute('dashboard');
}
</script>

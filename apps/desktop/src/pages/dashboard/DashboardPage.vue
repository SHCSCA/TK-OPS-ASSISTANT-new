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
        <div class="segmented" data-segmented data-dashboard-range>
          <button
            v-for="item in rangeOptions"
            :key="item.key"
            type="button"
            :data-range="item.key"
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

    <section class="section-stack">
      <div class="stat-grid">
        <article
          v-for="metric in displayMetrics"
          :key="metric.key"
          class="stat-card dashboard-stat-link"
          role="button"
          tabindex="0"
          :data-dashboard-stat="metric.dataKey"
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
                <div class="subtle">X 轴：时间桶；Y 轴：任务数量。用于查看新增、完成、异常三类任务变化。</div>
              </div>
              <div class="chart-legend">
                <span><span class="legend-dot legend-dot--created"></span>新增任务</span>
                <span><span class="legend-dot legend-dot--completed"></span>已完成任务</span>
                <span><span class="legend-dot legend-dot--failed"></span>异常任务</span>
              </div>
            </div>

            <div class="chart-placeholder" data-dashboard-chart>
              <div v-if="loading" class="subtle">等待加载趋势数据</div>
              <div v-else-if="error" class="subtle">{{ error }}</div>
              <div v-else-if="trendItems.length" class="dashboard-trend-chart dashboard-trend-chart--summary">
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
              <div v-else class="subtle">暂无趋势数据</div>
            </div>
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
                <tbody data-dashboard-activity>
                  <tr v-if="loading">
                    <td colspan="5" class="subtle">等待加载活动数据</td>
                  </tr>
                  <tr v-else-if="error">
                    <td colspan="5" class="subtle">{{ error }}</td>
                  </tr>
                  <template v-else-if="activityItems.length">
                    <tr
                      v-for="item in activityItems"
                      :key="`${item.title}-${item.time}-${item.category}`"
                      class="route-row"
                      data-dashboard-activity-row="1"
                      :class="{ 'is-selected': selectedActivity?.title === item.title && selectedActivity?.time === item.time }"
                      @click="selectActivity(item)"
                    >
                      <td><strong>{{ item.title }}</strong></td>
                      <td>{{ item.entity }}</td>
                      <td>{{ item.category }}</td>
                      <td><span class="status-chip" :class="activityTone(item.status)">{{ item.status }}</span></td>
                      <td class="subtle metric-nowrap">{{ formatTime(item.time) }}</td>
                    </tr>
                  </template>
                  <tr v-else>
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
              <span class="status-chip" :class="systemSummaryTone" data-dashboard-systems-status>{{ systemSummaryText }}</span>
            </div>
            <div class="metric-list dashboard-systems-grid" data-dashboard-systems>
              <template v-if="loading">
                <div class="task-item"><div><strong>等待加载</strong><div class="subtle">系统状态数据即将显示</div></div><span class="pill info">--</span></div>
              </template>
              <template v-else-if="!systemItems.length">
                <div class="task-item"><div><strong>暂无系统状态</strong><div class="subtle">等待后端返回摘要</div></div><span class="pill warning">空</span></div>
              </template>
              <template v-else>
                <button
                  v-for="item in systemItems"
                  :key="item.key"
                  type="button"
                  :data-dashboard-system-key="item.key"
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
              </template>
            </div>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>快捷入口 / 待办</strong>
                <div class="subtle">保留最常用动作，避免用户在多域导航中迷路</div>
              </div>
            </div>
            <div class="action-grid shell-action-grid">
              <button class="secondary-button detail-trigger" data-detail-target="dashboard-quick-1" type="button" @click="selectQuickAction('dashboard-quick-1')">处理账号异常</button>
              <button class="secondary-button detail-trigger" data-detail-target="dashboard-quick-2" type="button" @click="selectQuickAction('dashboard-quick-2')">启动内容批量生成</button>
              <button class="secondary-button detail-trigger" data-detail-target="dashboard-quick-3" type="button" @click="selectQuickAction('dashboard-quick-3')">网络诊断</button>
              <button class="secondary-button detail-trigger" data-detail-target="dashboard-quick-4" type="button" @click="selectQuickAction('dashboard-quick-4')">审核定时发布</button>
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
  selectQuickAction,
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
  const taskMetric = metricByKeyFragment('task');
  const failedMetric = metricByKeyFragment('failed') || metricByKeyFragment('error');
  const providerMetric = metricByKeyFragment('provider');

  return [
    {
      key: 'accounts-total',
      dataKey: 'accounts',
      label: accountMetric?.label || '账号总量',
      value: Number(accountMetric?.value || 0),
      meta: accountMetric?.meta || '来自账号主表',
    },
    {
      key: 'tasks-total',
      dataKey: 'tasks',
      label: taskMetric?.label || '任务总量',
      value: Number(taskMetric?.value || 0),
      meta: taskMetric?.meta || '来自任务主表',
    },
    {
      key: 'failed-total',
      dataKey: 'failed',
      label: failedMetric?.label || '异常任务',
      value: Number(failedMetric?.value || 0),
      meta: failedMetric?.meta || '按任务状态聚合',
    },
    {
      key: 'providers-total',
      dataKey: 'providers',
      label: providerMetric?.label || 'AI 供应商接入',
      value: Number(providerMetric?.value || (overview.value?.activeProvider ? 1 : 0)),
      meta: providerMetric?.meta || '用于判断生成能力是否可用',
    },
  ];
});

const systemSummaryTone = computed(() => {
  if (loading.value) {
    return 'success';
  }
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
  if (loading.value) {
    return '等待加载';
  }
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

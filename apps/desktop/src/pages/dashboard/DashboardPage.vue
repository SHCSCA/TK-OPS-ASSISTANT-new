<template>
  <section class="page-shell dashboard-workbench">
    <div class="breadcrumbs">
      <span>首页</span>
      <span>/</span>
      <span>概览看板</span>
    </div>

    <div class="page-header">
      <div>
        <div class="eyebrow">总览工作台</div>
        <h1>概览看板</h1>
        <p>
          把系统健康、核心指标、任务状态和最近动态放在同一屏内，保持桌面工作台的阅读节奏，同时继续使用新
          runtime 的真实数据。
        </p>
      </div>
      <div class="header-actions">
        <button class="secondary-button" type="button">查看历史</button>
        <button class="primary-button" type="button" @click="reload">刷新数据</button>
      </div>
    </div>

    <div v-if="loading" class="notice-banner">
      <div>
        <strong>正在加载概览数据</strong>
        <div class="subtle">当前正在读取 runtime 健康状态与 dashboard 聚合结果。</div>
      </div>
    </div>

    <div v-else-if="error" class="notice-banner">
      <div>
        <strong>概览加载失败</strong>
        <div class="subtle">{{ error }}</div>
      </div>
    </div>

    <template v-else-if="health && overview">
      <div class="stat-grid">
        <article class="stat-card">
          <div>
            <div class="eyebrow">Runtime Health</div>
            <div class="stat-card__value">{{ health.status }}</div>
          </div>
          <div class="stat-card__delta">
            <span class="subtle">Host</span>
            <strong>{{ health.host }}:{{ health.port }}</strong>
          </div>
        </article>
        <article class="stat-card">
          <div>
            <div class="eyebrow">版本</div>
            <div class="stat-card__value">{{ health.version }}</div>
          </div>
          <div class="stat-card__delta">
            <span class="subtle">环境</span>
            <strong>{{ health.environment }}</strong>
          </div>
        </article>
        <article v-for="metric in overview.metrics.slice(0, 2)" :key="metric.key" class="stat-card">
          <div>
            <div class="eyebrow">{{ metric.label }}</div>
            <div class="stat-card__value">{{ metric.value }}</div>
          </div>
          <div class="stat-card__delta">
            <span class="subtle">{{ metric.meta }}</span>
          </div>
        </article>
      </div>

      <div class="content-grid">
        <section class="section-stack">
          <section class="table-card">
            <div class="table-card__header">
              <div>
                <strong>任务状态</strong>
                <div class="subtle">按状态聚合当前任务队列，帮助先判断风险再继续调度。</div>
              </div>
              <span class="pill info">{{ overview.generatedAt }}</span>
            </div>
            <div class="dashboard-list">
              <div v-for="bucket in overview.taskStatus" :key="bucket.key" class="dashboard-list-item">
                <div>
                  <strong>{{ bucket.key }}</strong>
                  <div class="subtle">当前状态任务数</div>
                </div>
                <span class="status-chip info">{{ bucket.count }}</span>
              </div>
            </div>
          </section>

          <section class="table-card">
            <div class="table-card__header">
              <div>
                <strong>最近任务</strong>
                <div class="subtle">保留真实 runtime 返回的最近任务列表。</div>
              </div>
              <span class="pill">{{ overview.recentTasks.length }} 条</span>
            </div>
            <div v-if="overview.recentTasks.length" class="dashboard-list">
              <div v-for="task in overview.recentTasks" :key="task.id" class="dashboard-list-item">
                <div>
                  <strong>{{ task.title }}</strong>
                  <div class="subtle">
                    {{ task.taskType }} / {{ task.priority }} / {{ task.accountUsername || '未绑定账号' }}
                  </div>
                </div>
                <span class="status-chip">{{ task.status }}</span>
              </div>
            </div>
            <div v-else class="empty-state">当前没有最近任务数据。</div>
          </section>
        </section>

        <section class="section-stack">
          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>系统摘要</strong>
                <div class="subtle">把账号分布、区域分布和当前 AI 提供商收敛在一个摘要区。</div>
              </div>
              <span class="status-chip success" v-if="overview.activeProvider">已连通</span>
            </div>
            <div class="panel__body">
              <div class="dashboard-inline-metrics">
                <span v-for="bucket in overview.accountStatus" :key="bucket.key" class="pill">
                  {{ bucket.key }} · {{ bucket.count }}
                </span>
              </div>
              <div class="dashboard-inline-metrics">
                <span v-for="region in overview.regions" :key="region.key" class="pill info">
                  {{ region.key }} · {{ region.count }}
                </span>
              </div>
              <div v-if="overview.activeProvider" class="dashboard-kv-grid">
                <div class="dashboard-kv-item">
                  <span>当前 AI 提供商</span>
                  <strong>{{ overview.activeProvider.name }}</strong>
                </div>
                <div class="dashboard-kv-item">
                  <span>默认模型</span>
                  <strong>{{ overview.activeProvider.defaultModel }}</strong>
                </div>
              </div>
              <div v-else class="empty-state">当前没有已激活的 AI 提供商。</div>
            </div>
          </section>

          <section class="panel panel--subtle">
            <div class="panel__header">
              <div>
                <strong>设置摘要</strong>
                <div class="subtle">保留当前主题和系统设置摘要，方便核对桌面状态。</div>
              </div>
            </div>
            <div class="dashboard-kv-grid">
              <div class="dashboard-kv-item">
                <span>主题</span>
                <strong>{{ overview.settingsSummary.theme }}</strong>
              </div>
              <div class="dashboard-kv-item">
                <span>设置项数量</span>
                <strong>{{ overview.settingsSummary.total }}</strong>
              </div>
            </div>
          </section>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { useDashboardData } from '../../modules/dashboard/useDashboardData';

const { error, health, loading, overview, reload } = useDashboardData();
</script>

<template>
  <section class="route-page data-collector-page" data-page-audit="data-collector">
    <div class="breadcrumbs"><span>automation</span><span>/</span><span>数据采集助手</span></div>
    <div class="page-header">
      <div>
        <div class="eyebrow">采集源与节点编排</div>
        <h1>数据采集助手</h1>
        <p>复用旧壳 task-ops 的 collector 子模式，统一管理 scrape 任务、区域、代理池与补偿链路。</p>
      </div>
      <div class="header-actions">
        <button class="secondary-button" type="button" @click="focusProxyPool">查看代理池</button>
        <button class="secondary-button" type="button" @click="reload">刷新</button>
        <button class="primary-button" type="button" :disabled="creating || !draftTitle.trim()" @click="createCollectorTask">
          {{ creating ? '创建中...' : '新建采集方案' }}
        </button>
      </div>
    </div>

    <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
    <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
    <p v-if="loading" class="dashboard-banner">正在加载数据采集任务...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <section v-else class="section-stack">
      <section class="panel collector-draft-panel">
        <div class="panel__header">
          <div>
            <strong>新建采集方案</strong>
            <div class="subtle">POST /tasks (scrape)</div>
          </div>
          <span class="status-chip info">草稿</span>
        </div>
        <div class="collector-form-grid">
          <label class="copywriter-field">
            <span>任务名称</span>
            <input v-model="draftTitle" type="text" placeholder="例如：美区达人素材采集" />
          </label>
          <label class="copywriter-field">
            <span>采集账号</span>
            <select v-model="draftAccountId">
              <option :value="null">未绑定账号</option>
              <option v-for="item in accountOptions" :key="item.id" :value="item.id">{{ item.label }}</option>
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
          <label class="copywriter-field collector-form-grid__full">
            <span>结果摘要</span>
            <input v-model="draftResultSummary" type="text" placeholder="默认写入来源页面和采集链路说明" />
          </label>
        </div>
      </section>

      <div class="stat-grid">
        <article v-for="item in metrics" :key="item.label" class="stat-card">
          <div>
            <div class="subtle">{{ item.label }}</div>
            <div class="stat-card__value">{{ item.value }}</div>
          </div>
          <div class="stat-card__delta" :class="`stat-card__delta--${item.tone}`">
            <span>{{ item.delta }}</span>
            <span class="subtle">{{ item.note }}</span>
          </div>
        </article>
      </div>

      <section class="task-ops-shell">
        <div class="task-filter-bar">
          <div class="collector-search-wrap">
            <input v-model="query" type="text" placeholder="搜索采集任务、账号、区域或备注…" class="list-search-input" />
          </div>
          <button class="task-filter-tab" :class="{ 'is-active': statusFilter === '' }" type="button" @click="setStatus('')">全部 {{ statusCounts.all }}</button>
          <button class="task-filter-tab" :class="{ 'is-active': statusFilter === 'running' }" type="button" @click="setStatus('running')">运行中 {{ statusCounts.running }}</button>
          <button class="task-filter-tab" :class="{ 'is-active': statusFilter === 'paused' }" type="button" @click="setStatus('paused')">暂停 {{ statusCounts.paused }}</button>
          <button class="task-filter-tab" :class="{ 'is-active': statusFilter === 'failed' }" type="button" @click="setStatus('failed')">失败 {{ statusCounts.failed }}</button>
          <button class="task-filter-tab" :class="{ 'is-active': statusFilter === 'completed' }" type="button" @click="setStatus('completed')">已完成 {{ statusCounts.completed }}</button>
          <div class="task-view-toggles">
            <button class="task-view-btn" :class="{ 'is-active': viewMode === 'table' }" type="button" @click="setViewMode('table')">表格</button>
            <button class="task-view-btn" :class="{ 'is-active': viewMode === 'kanban' }" type="button" @click="setViewMode('kanban')">看板</button>
          </div>
        </div>

        <div class="task-ops-body data-collector-layout">
          <div class="task-ops-main">
            <section class="panel task-ops-canvas">
              <div class="panel__header">
                <div>
                  <strong>采集任务表</strong>
                  <div class="subtle">collector 模式仅展示 scrape 任务，并保留区域与动作聚合列。</div>
                </div>
                <span class="status-chip info">{{ records.length }} 条</span>
              </div>

              <div v-if="viewMode === 'table'" class="table-wrapper">
                <table class="collector-table">
                  <thead>
                    <tr>
                      <th>任务名</th>
                      <th>类型</th>
                      <th>状态</th>
                      <th>区域与动作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in records" :key="item.id" :class="{ 'is-selected': selectedRecordId === item.id }" @click="selectRecord(item.id)">
                      <td>
                        <strong>{{ item.title }}</strong>
                        <div class="subtle">{{ item.accountLabel }}</div>
                        <div class="subtle">{{ item.timeLabel }}</div>
                      </td>
                      <td>
                        <strong>{{ item.taskTypeLabel }}</strong>
                        <div class="subtle">优先级 {{ item.priorityLabel }}</div>
                      </td>
                      <td><span class="pill" :class="item.statusTone">{{ item.statusLabel }}</span></td>
                      <td>
                        <div class="collector-table__region">{{ item.regionLabel }}</div>
                        <div class="collector-table__actions">
                          <button class="secondary-button" type="button" :disabled="item.status === 'running' || item.status === 'completed'" @click.stop="startCollectorTask(item.id)">启动</button>
                          <button class="ghost-button" type="button" @click.stop="focusProxyPool">代理池</button>
                          <button class="danger-button" type="button" @click.stop="deleteCollectorTask(item.id)">删除</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-else class="kanban-grid collector-kanban-grid">
                <article v-for="column in kanbanColumns" :key="column.key" class="kanban-column">
                  <div class="kanban-column__header">
                    <strong>{{ column.title }}</strong>
                    <span class="pill" :class="column.tone">{{ column.records.length }}</span>
                  </div>
                  <div v-if="column.records.length" class="kanban-column__body">
                    <button
                      v-for="item in column.records"
                      :key="item.id"
                      class="kanban-card"
                      :class="{ 'is-selected': selectedRecordId === item.id }"
                      type="button"
                      @click="selectRecord(item.id)"
                    >
                      <strong>{{ item.title }}</strong>
                      <div class="subtle">{{ item.accountLabel }}</div>
                      <div class="subtle">{{ item.regionLabel }} / {{ item.timeLabel }}</div>
                    </button>
                  </div>
                  <div v-else class="subtle kanban-column__empty">当前列暂无任务</div>
                </article>
              </div>

              <div v-if="!records.length" class="empty-state">
                <p>当前没有匹配的采集任务。</p>
                <p class="subtle">可调整筛选条件，或先创建新的 scrape 草稿。</p>
              </div>
            </section>
          </div>

          <aside ref="proxyPoolPanelRef" class="task-ops-sidebar collector-sidebar" :class="{ 'is-highlighted': proxyPoolHighlighted }">
            <section class="panel">
              <div class="panel__header">
                <div>
                  <strong>{{ proxySummary.title }}</strong>
                  <div class="subtle">{{ proxySummary.subtitle }}</div>
                </div>
                <span class="status-chip info">查看代理池</span>
              </div>
              <div class="collector-proxy-metrics">
                <article v-for="item in proxySummary.metrics" :key="item.label" class="collector-proxy-metric">
                  <span class="subtle">{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                  <span class="pill" :class="item.tone">{{ item.label }}</span>
                </article>
              </div>
              <div class="collector-device-list">
                <article v-for="item in proxySummary.deviceRows" :key="item.id" class="collector-device-row">
                  <div>
                    <strong>{{ item.name }}</strong>
                    <div class="subtle">{{ item.region }}</div>
                    <div class="subtle">{{ item.proxyLabel }}</div>
                  </div>
                  <span class="pill" :class="item.statusTone">{{ item.statusLabel }}</span>
                </article>
              </div>
            </section>

            <section class="panel">
              <div class="panel__header">
                <div>
                  <strong>补偿与重试建议</strong>
                  <div class="subtle">当前选中任务的采集补偿建议同步自右栏详情。</div>
                </div>
                <span class="status-chip" :class="detail.statusTone">{{ detail.statusLabel }}</span>
              </div>
              <div class="board-list">
                <article v-if="!detail.adviceItems.length" class="board-card">
                  <strong>等待选择采集任务</strong>
                  <div class="subtle">左侧任务选中后，这里会显示补偿链路、代理池和落库建议。</div>
                  <div class="status-strip"><span class="pill info">待选择</span></div>
                </article>
                <article v-for="item in detail.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
                  <strong>{{ item.title }}</strong>
                  <div class="subtle">{{ item.copy }}</div>
                  <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
                </article>
              </div>
            </section>
          </aside>
        </div>
      </section>
    </section>
  </section>
</template>

<script setup lang="ts">
import { useDataCollectorData } from '../../modules/collector/useDataCollectorData';

const {
  actionError,
  actionMessage,
  accountOptions,
  createCollectorTask,
  creating,
  deleteCollectorTask,
  detail,
  draftAccountId,
  draftPriority,
  draftResultSummary,
  draftTitle,
  error,
  focusProxyPool,
  kanbanColumns,
  loading,
  metrics,
  proxyPoolHighlighted,
  proxyPoolPanelRef,
  proxySummary,
  query,
  records,
  reload,
  selectRecord,
  selectedRecordId,
  setStatus,
  setViewMode,
  startCollectorTask,
  statusCounts,
  statusFilter,
  viewMode,
} = useDataCollectorData();
</script>
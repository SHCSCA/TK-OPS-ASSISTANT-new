<template>
  <section class="route-page scheduled-publish-page" data-page-audit="scheduled-publish">
    <div class="breadcrumbs"><span>automation</span><span>/</span><span>定时发布</span></div>
    <div class="page-header">
      <div>
        <div class="eyebrow">发布编排中心</div>
        <h1>定时发布</h1>
        <p>复用旧壳 publish 子模式，围绕真实发布任务、账号和素材库存统一管理发布计划。</p>
      </div>
      <div class="header-actions">
        <button class="secondary-button" type="button" @click="toggleCalendar">
          {{ viewMode === 'calendar' ? '返回计划列表' : '查看发布日历' }}
        </button>
        <button class="secondary-button" type="button" @click="reload">刷新</button>
      </div>
    </div>

    <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
    <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
    <p v-if="loading" class="dashboard-banner">正在加载定时发布数据...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <section v-else class="section-stack">
      <section class="panel publish-creator-panel">
        <div class="panel__header">
          <div>
            <strong>新建发布计划</strong>
            <div class="subtle">POST /tasks (publish)</div>
          </div>
          <span class="status-chip info">草稿</span>
        </div>
        <div class="publish-form-grid">
          <label class="copywriter-field">
            <span>计划名称</span>
            <input v-model="draftTitle" type="text" placeholder="例如：晚高峰短视频发布" />
          </label>
          <label class="copywriter-field">
            <span>发布时间</span>
            <input v-model="draftScheduledAt" type="datetime-local" />
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
            <span>发布账号</span>
            <select v-model="draftAccountId">
              <option :value="null">未绑定账号</option>
              <option v-for="item in accountOptions" :key="item.id" :value="item.id">{{ item.label }}</option>
            </select>
          </label>
          <label class="copywriter-field publish-form-grid__full">
            <span>结果摘要</span>
            <input v-model="draftResultSummary" type="text" placeholder="可选，用于备注来源或发布目标" />
          </label>
        </div>
        <div class="copywriter-actions scheduled-publish-actions">
          <button class="primary-button" type="button" :disabled="creating || !draftTitle.trim() || !draftScheduledAt" @click="createPublishPlan">
            {{ creating ? '创建中...' : '新建发布计划' }}
          </button>
          <div class="subtle">默认按 publish 任务写入任务队列，可在右侧详情区继续启动或删除。</div>
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

      <div class="list-management-shell">
        <div class="list-toolbar">
          <div class="list-toolbar__search">
            <input v-model="query" type="text" placeholder="搜索发布计划、账号或备注…" class="list-search-input" />
          </div>
          <div class="list-toolbar__filters scheduled-publish-tabs">
            <button class="filter-pill" :class="{ 'is-active': statusFilter === '' }" type="button" @click="setStatus('')">全部 {{ statusCounts.all }}</button>
            <button class="filter-pill" :class="{ 'is-active': statusFilter === 'pending' }" type="button" @click="setStatus('pending')">待审核 {{ statusCounts.pending }}</button>
            <button class="filter-pill" :class="{ 'is-active': statusFilter === 'running' }" type="button" @click="setStatus('running')">发布中 {{ statusCounts.running }}</button>
            <button class="filter-pill" :class="{ 'is-active': statusFilter === 'completed' }" type="button" @click="setStatus('completed')">已发布 {{ statusCounts.completed }}</button>
            <button class="filter-pill" :class="{ 'is-active': statusFilter === 'failed' }" type="button" @click="setStatus('failed')">已中断 {{ statusCounts.failed }}</button>
          </div>
        </div>

        <div class="list-body scheduled-publish-layout">
          <div class="list-main-area">
            <section class="panel">
              <div class="panel__header">
                <div>
                  <strong>发布计划列表</strong>
                  <div class="subtle">按计划时间排序，点击任意计划同步右栏详情。</div>
                </div>
                <span class="status-chip info">{{ total }} 条</span>
              </div>
              <div v-if="records.length" class="workbench-list">
                <div
                  v-for="item in records"
                  :key="item.id"
                  class="task-item publish-task-item"
                  :class="{ 'is-selected': selectedRecordId === item.id }"
                  @click="selectRecord(item.id)"
                >
                  <div>
                    <strong>{{ item.title }}</strong>
                    <div class="subtle">{{ item.accountLabel }} / {{ item.platformLabel }}</div>
                    <div class="subtle">{{ item.timeLabel }}</div>
                  </div>
                  <span class="pill" :class="item.statusTone">{{ item.statusLabel }}</span>
                </div>
              </div>
              <div v-else class="empty-state">
                <p>当前没有匹配的发布计划。</p>
                <p class="subtle">可调整筛选条件，或先创建新的发布草稿。</p>
              </div>
            </section>
          </div>

          <div class="scheduled-publish-side">
            <section class="panel">
              <div class="panel__header">
                <div>
                  <strong>{{ viewMode === 'calendar' ? '发布日历' : '计划明细表' }}</strong>
                  <div class="subtle">{{ viewMode === 'calendar' ? '展示未来 7 天内的发布槽位。' : '直接管理 publish 任务的执行与删除。' }}</div>
                </div>
                <div class="publish-view-switch">
                  <button class="ghost-button" type="button" :disabled="viewMode === 'list'" @click="setViewMode('list')">列表</button>
                  <button class="ghost-button" type="button" :disabled="viewMode === 'calendar'" @click="setViewMode('calendar')">日历</button>
                </div>
              </div>

              <div v-if="viewMode === 'calendar'" class="calendar-grid">
                <article v-for="day in calendarDays" :key="day.key" class="calendar-day" :class="{ 'is-today': day.isToday }">
                  <div class="calendar-day__header">
                    <strong>{{ day.label }}</strong>
                    <span class="subtle">{{ day.slots.length }} 条</span>
                  </div>
                  <div v-if="day.slots.length" class="calendar-slot-list">
                    <button
                      v-for="slot in day.slots"
                      :key="slot.id"
                      class="calendar-slot"
                      :class="`calendar-slot--${slot.tone}`"
                      type="button"
                      @click="selectRecord(slot.id)"
                    >
                      <strong>{{ slot.title }}</strong>
                      <span>{{ slot.timeLabel }}</span>
                    </button>
                  </div>
                  <div v-else class="subtle calendar-day__empty">当日无发布计划</div>
                </article>
              </div>

              <div v-else class="table-wrapper">
                <table class="publish-table">
                  <thead>
                    <tr>
                      <th>计划名</th>
                      <th>时间</th>
                      <th>平台</th>
                      <th>状态</th>
                      <th>动作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in records" :key="`row-${item.id}`" :class="{ 'is-selected': selectedRecordId === item.id }" @click="selectRecord(item.id)">
                      <td>
                        <strong>{{ item.title }}</strong>
                        <div class="subtle">{{ item.accountLabel }}</div>
                      </td>
                      <td>{{ item.timeLabel }}</td>
                      <td>{{ item.platformLabel }}</td>
                      <td><span class="pill" :class="item.statusTone">{{ item.statusLabel }}</span></td>
                      <td>
                        <div class="publish-table__actions">
                          <button class="secondary-button" type="button" :disabled="item.status === 'running' || item.status === 'completed'" @click.stop="startPublishPlan(item.id)">启动</button>
                          <button class="danger-button" type="button" @click.stop="deletePublishPlan(item.id)">删除</button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section class="panel publish-summary-panel">
              <div class="panel__header">
                <div>
                  <strong>计划摘要</strong>
                  <div class="subtle">当前选中计划与资源准备度概览。</div>
                </div>
                <span class="status-chip" :class="detail.statusTone">{{ detail.statusLabel }}</span>
              </div>
              <div class="detail-list">
                <div v-for="item in detail.detailItems" :key="`publish-detail-${item.label}`" class="detail-item" :class="{ 'detail-item--stacked': item.stacked }">
                  <span class="subtle">{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { useScheduledPublishData } from '../../modules/publish/useScheduledPublishData';

const {
  actionError,
  actionMessage,
  accountOptions,
  calendarDays,
  createPublishPlan,
  creating,
  deletePublishPlan,
  detail,
  draftAccountId,
  draftPriority,
  draftResultSummary,
  draftScheduledAt,
  draftTitle,
  error,
  loading,
  metrics,
  query,
  records,
  reload,
  selectRecord,
  selectedRecordId,
  setStatus,
  setViewMode,
  startPublishPlan,
  statusCounts,
  statusFilter,
  toggleCalendar,
  total,
  viewMode,
} = useScheduledPublishData();
</script>
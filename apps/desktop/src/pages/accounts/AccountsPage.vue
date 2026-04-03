<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>账号管理</h2>
        <p class="resource-subtitle">
          支持搜索、人工状态筛选、系统状态筛选、风险状态筛选、显示归档和批量动作；继续保持归档优先策略，并新增审计中心筛选与生命周期动作，列表与详情全部读取真实 runtime 数据。
        </p>
      </div>
      <div class="copywriter-actions">
        <button class="dashboard-refresh" type="button" @click="prepareCreate">新建账号</button>
        <button class="dashboard-refresh" type="button" @click="refreshAccounts">刷新</button>
      </div>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载账号列表...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <template v-else>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>

      <div class="resource-summary-grid resource-summary-grid-triple">
        <article class="metric-card">
          <p class="eyebrow">账号总数</p>
          <strong>{{ total }}</strong>
          <span>来源于 /accounts</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">当前可见</p>
          <strong>{{ visibleAccountCount }}</strong>
          <span>受当前筛选条件影响</span>
        </article>
        <article class="metric-card">
          <p class="eyebrow">当前选中</p>
          <strong>{{ selectedAccountCount }}</strong>
          <span>支持批量状态、分组、检测和归档</span>
        </article>
      </div>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>筛选条件</h3>
          <span>支持搜索、人工状态筛选、系统状态筛选、风险状态筛选和显示归档</span>
        </div>

        <form class="copywriter-form" @submit.prevent="applyFilters">
          <div class="resource-summary-grid resource-summary-grid-triple">
            <label class="copywriter-field">
              <span>搜索</span>
              <input v-model="filters.query" type="search" maxlength="120" placeholder="输入用户名、平台、分组、环境或备注关键词" />
            </label>
            <label class="copywriter-field">
              <span>人工状态筛选</span>
              <select v-model="filters.manualStatus">
                <option v-for="option in manualStatusOptions" :key="`manual-${option.value || 'all'}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>系统状态筛选</span>
              <select v-model="filters.systemStatus">
                <option v-for="option in systemStatusOptions" :key="`system-${option.value || 'all'}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
          </div>

          <div class="resource-summary-grid resource-summary-grid-triple">
            <label class="copywriter-field">
              <span>风险状态筛选</span>
              <select v-model="filters.riskStatus">
                <option v-for="option in riskStatusOptions" :key="`risk-${option.value || 'all'}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>显示归档</span>
              <div class="copywriter-actions">
                <label class="copywriter-field">
                  <span>包含已归档账号</span>
                  <input v-model="filters.includeArchived" type="checkbox" />
                </label>
              </div>
            </label>
            <div class="copywriter-actions">
              <button class="dashboard-refresh" type="submit">应用筛选</button>
              <button class="dashboard-refresh" type="button" @click="clearFilters">重置筛选</button>
            </div>
          </div>
        </form>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>批量动作</h3>
          <span>先勾选账号，再统一处理人工状态、风险状态、分组、检测和生命周期动作</span>
        </div>

        <div class="resource-summary-grid resource-summary-grid-triple">
          <article class="metric-card">
            <p class="eyebrow">已勾选</p>
            <strong>{{ selectedAccountCount }}</strong>
            <span>支持多选后批量处理</span>
          </article>
          <article class="metric-card">
            <p class="eyebrow">可见列表</p>
            <strong>{{ visibleAccountCount }}</strong>
            <span>当前筛选条件下的账号数量</span>
          </article>
          <article class="metric-card">
            <p class="eyebrow">已归档</p>
            <strong>{{ archivedCount }}</strong>
            <span>当前列表中的归档账号</span>
          </article>
        </div>

        <div class="copywriter-actions">
          <button class="dashboard-refresh" type="button" :disabled="!visibleAccountCount" @click="selectVisibleAccounts">全选当前列表</button>
          <button class="dashboard-refresh" type="button" :disabled="!selectedAccountCount" @click="clearSelectedAccounts">清空选择</button>
        </div>

        <div class="resource-summary-grid resource-summary-grid-triple">
          <label class="copywriter-field">
            <span>批量改人工状态</span>
            <select v-model="bulkDraft.manualStatus">
              <option v-for="option in manualStatusOptions" :key="`bulk-manual-${option.value || 'all'}`" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
          <label class="copywriter-field">
            <span>批量改风险状态</span>
            <select v-model="bulkDraft.riskStatus">
              <option v-for="option in riskStatusOptions" :key="`bulk-risk-${option.value || 'all'}`" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
          <label class="copywriter-field">
            <span>批量分组</span>
            <input v-model="bulkDraft.groupId" type="text" placeholder="分组 ID，可留空后补分组名称" />
          </label>
        </div>

        <div class="resource-summary-grid resource-summary-grid-triple">
          <label class="copywriter-field">
            <span>批量分组名称</span>
            <input v-model="bulkDraft.groupName" type="text" placeholder="分组名称，可选" />
          </label>
          <label class="copywriter-field">
            <span>生命周期原因</span>
            <input v-model="lifecycleReason" type="text" maxlength="120" placeholder="用于归档/停用/恢复/删除的审计备注（可选）" />
          </label>
          <div class="copywriter-actions">
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'manual_status' || !selectedAccountCount" @click="bulkChangeManualStatus">
              批量改人工状态
            </button>
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'risk_status' || !selectedAccountCount" @click="bulkChangeRiskStatus">
              批量改风险状态
            </button>
          </div>
          <div class="copywriter-actions">
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'group' || !selectedAccountCount" @click="bulkChangeGroup">
              批量分组
            </button>
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'test' || !selectedAccountCount" @click="bulkTestAccounts">
              批量检测
            </button>
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'archive' || !selectedAccountCount" @click="bulkArchiveAccounts">
              批量归档
            </button>
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'unarchive' || !selectedAccountCount" @click="bulkUnarchiveAccounts">
              批量仅取消归档
            </button>
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'suspend' || !selectedAccountCount" @click="bulkSuspendAccounts">
              批量停用
            </button>
            <button class="dashboard-refresh" type="button" :disabled="bulkWorkingAction === 'restore' || !selectedAccountCount" @click="bulkRestoreAccounts">
              批量恢复启用
            </button>
          </div>
        </div>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>账号列表</h3>
          <span>每张卡片同时展示人工状态、系统状态、风险状态和归档状态</span>
        </div>

        <div v-if="accounts.length" class="resource-list">
          <article v-for="account in accounts" :key="account.id" class="resource-card">
            <div class="resource-card-head">
              <div class="copywriter-actions">
                <label class="copywriter-field">
                  <span>选择</span>
                  <input
                    :checked="selectedAccountIds.includes(account.id)"
                    type="checkbox"
                    @change="handleSelectionChange(account.id, $event)"
                  />
                </label>
                <div>
                  <strong>{{ account.username }}</strong>
                  <p>{{ account.platform }} / {{ account.region }}</p>
                </div>
              </div>
              <div class="copywriter-actions">
                <span class="status-chip">人工：{{ formatManualStatus(account.manualStatus || account.status) }}</span>
                <span class="status-chip">系统：{{ formatSystemStatus(account.systemStatus) }}</span>
                <span class="status-chip">风险：{{ formatRiskStatus(account.riskStatus) }}</span>
                <span v-if="account.isArchived" class="status-chip">已归档</span>
              </div>
            </div>

            <div class="resource-card-grid">
              <span>分组 {{ account.groupName || '未分组' }}</span>
              <span>绑定环境 {{ account.boundEnvironment || '未绑定' }}</span>
              <span>设备 {{ account.deviceName || '未绑定设备' }}</span>
              <span>连接 {{ account.lastConnectionStatus || '未知' }}</span>
            </div>

            <p class="resource-card-meta">最近错误：{{ account.recentError || '暂无最近错误' }}</p>
            <p class="resource-card-meta">更新时间：{{ formatDateTime(account.updatedAt) }}</p>

            <div class="task-actions">
              <button class="dashboard-refresh" type="button" @click="beginEdit(account)">编辑账号</button>
              <button class="dashboard-refresh" type="button" @click="focusAccount(account)">查看摘要</button>
              <button
                class="dashboard-refresh"
                type="button"
                :disabled="testingAccountId === account.id"
                @click="testAccountConnection(account)"
              >
                {{ testingAccountId === account.id ? '测试中...' : '测试连接' }}
              </button>
              <button
                v-if="account.isArchived"
                class="dashboard-refresh"
                type="button"
                :disabled="restoringAccountId === account.id"
                @click="handleRestoreAccount(account)"
              >
                {{ restoringAccountId === account.id ? '恢复中...' : '恢复账号' }}
              </button>
              <button
                v-else
                class="dashboard-refresh"
                type="button"
                :disabled="archivingAccountId === account.id"
                @click="handleArchiveAccount(account)"
              >
                {{ archivingAccountId === account.id ? '归档中...' : '归档' }}
              </button>
              <button
                class="dashboard-refresh"
                type="button"
                :disabled="suspendingAccountId === account.id"
                @click="handleSuspendAccount(account)"
              >
                {{ suspendingAccountId === account.id ? '停用中...' : '停用' }}
              </button>
            </div>
          </article>
        </div>

        <p v-else class="dashboard-empty">当前没有账号数据。</p>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>账号审计中心</h3>
          <span>绑定环境、最近错误、活动摘要与可筛选审计日志均从 GET /accounts/{id} 与 /accounts/{id}/activity 读取</span>
        </div>

        <article v-if="detailLoading" class="resource-card">
          <p class="resource-card-meta">正在加载账号详情摘要...</p>
        </article>
        <article v-else-if="detailError" class="resource-card">
          <p class="resource-card-meta">{{ detailError }}</p>
        </article>
        <article v-else-if="accountDetail" class="resource-card">
          <div class="resource-card-head">
            <div>
              <strong>{{ accountDetail.username }}</strong>
              <p>{{ accountDetail.platform }} / {{ accountDetail.region }}</p>
            </div>
            <span class="status-chip">{{ accountDetail.isArchived ? '已归档' : '当前查看' }}</span>
          </div>

          <div class="resource-card-grid">
            <span>绑定环境 {{ accountDetail.boundEnvironment || '未绑定' }}</span>
            <span>人工状态 {{ formatManualStatus(accountDetail.manualStatus || accountDetail.status) }}</span>
            <span>系统状态 {{ formatSystemStatus(accountDetail.systemStatus) }}</span>
            <span>风险状态 {{ formatRiskStatus(accountDetail.riskStatus) }}</span>
          </div>

          <p class="resource-card-meta">最近错误：{{ accountDetail.recentError || '暂无最近错误' }}</p>
          <p class="resource-card-meta">最近活动摘要</p>
          <p v-if="!accountDetail.activitySummary.length" class="resource-card-meta">暂无最近活动摘要</p>
          <template v-else>
            <p
              v-for="(item, index) in accountDetail.activitySummary"
              :key="`${item.title}-${index}`"
              class="resource-card-meta"
            >
              {{ item.title }}：{{ item.summary }}{{ item.occurredAt ? `（${formatDateTime(item.occurredAt)}）` : '' }}
            </p>
          </template>

          <div class="dashboard-actions">
            <input v-model="activityQuery" type="text" placeholder="按活动关键词过滤" />
            <select v-model.number="activityLimit">
              <option :value="20">20 条</option>
              <option :value="50">50 条</option>
              <option :value="100">100 条</option>
            </select>
            <select v-model="activityCategory">
              <option v-for="option in activityCategoryOptions" :key="`activity-category-${option.value || 'all'}`" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <select v-model="activitySeverity">
              <option v-for="option in activitySeverityOptions" :key="`activity-severity-${option.value || 'all'}`" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <button
              class="dashboard-refresh"
              type="button"
              :disabled="activityLoading || selectedAccountId !== accountDetail.id"
              @click="loadAccountActivity(accountDetail.id)"
            >
              {{ activityLoading ? '活动刷新中...' : '刷新活动记录' }}
            </button>
          </div>

          <p class="resource-card-meta">最近活动记录</p>
          <p v-if="activityLoading" class="resource-card-meta">正在加载活动记录...</p>
          <p v-else-if="activityError" class="resource-card-meta">{{ activityError }}</p>
          <p v-else-if="!recentActivityItems.length" class="resource-card-meta">暂无活动记录</p>
          <template v-else>
            <p
              v-for="(item, index) in recentActivityItems"
              :key="`activity-${item.id || item.title}-${index}`"
              class="resource-card-meta"
            >
              [{{ formatActivitySeverity(item.severity) }} / {{ item.category || 'uncategorized' }}]
              {{ item.title }}：{{ item.summary }}{{ item.reason ? `（原因：${item.reason}）` : '' }}{{ item.occurredAt ? `（${formatDateTime(item.occurredAt)}）` : '' }}
            </p>
          </template>
        </article>
        <article v-else class="resource-card">
          <p class="resource-card-meta">请选择左侧一个账号查看详情摘要。</p>
        </article>
      </section>

      <section v-if="accountDetail" class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>生命周期动作</h3>
          <span>统一执行停用、归档、恢复和删除，执行前有二次确认并写入审计原因。</span>
        </div>

        <article class="resource-card">
          <label class="copywriter-field">
            <span>动作原因（可选）</span>
            <input v-model="lifecycleReason" type="text" maxlength="120" placeholder="例如：阶段收口、风险隔离、误归档恢复" />
          </label>

          <div class="task-actions">
            <button class="dashboard-refresh" type="button" :disabled="suspendingAccountId === accountDetail.id" @click="handleSuspendAccount(accountDetail)">
              {{ suspendingAccountId === accountDetail.id ? '停用中...' : '停用账号' }}
            </button>
            <button class="dashboard-refresh" type="button" :disabled="archivingAccountId === accountDetail.id" @click="handleArchiveAccount(accountDetail)">
              {{ archivingAccountId === accountDetail.id ? '归档中...' : '归档账号' }}
            </button>
            <button class="dashboard-refresh" type="button" :disabled="restoringAccountId === accountDetail.id" @click="handleRestoreAccount(accountDetail)">
              {{ restoringAccountId === accountDetail.id ? '恢复中...' : '恢复账号' }}
            </button>
            <button class="dashboard-refresh" type="button" :disabled="deletingAccountId === accountDetail.id" @click="handleDeleteAccount(accountDetail)">
              {{ deletingAccountId === accountDetail.id ? '删除中...' : '彻底删除' }}
            </button>
          </div>
        </article>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>{{ isEditing ? '编辑账号' : '新建账号' }}</h3>
          <span>保存后会同步刷新列表，并自动拉取最新详情摘要</span>
        </div>

        <form class="copywriter-form" @submit.prevent="saveAccount">
          <div class="resource-summary-grid resource-summary-grid-triple">
            <label class="copywriter-field">
              <span>账号名称</span>
              <input v-model="draft.username" type="text" maxlength="120" placeholder="例如：demo_tiktok_cn" />
            </label>
            <label class="copywriter-field">
              <span>平台</span>
              <select v-model="draft.platform">
                <option value="tiktok">tiktok</option>
                <option value="tiktok_shop">tiktok_shop</option>
                <option value="instagram">instagram</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>地区</span>
              <input v-model="draft.region" type="text" maxlength="10" placeholder="US / DE / JP" />
            </label>
          </div>

          <div class="resource-summary-grid resource-summary-grid-triple">
            <label class="copywriter-field">
              <span>人工状态</span>
              <select v-model="draft.manualStatus">
                <option v-for="option in manualStatusOptions" :key="`draft-manual-${option.value || 'all'}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>风险状态</span>
              <select v-model="draft.riskStatus">
                <option v-for="option in riskStatusOptions" :key="`draft-risk-${option.value || 'all'}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>Cookie 状态</span>
              <select v-model="draft.cookieStatus">
                <option value="unknown">unknown</option>
                <option value="valid">valid</option>
                <option value="invalid">invalid</option>
                <option value="missing">missing</option>
                <option value="expiring">expiring</option>
              </select>
            </label>
          </div>

          <div class="resource-summary-grid resource-summary-grid-triple">
            <label class="copywriter-field">
              <span>粉丝数</span>
              <input v-model.number="draft.followers" type="number" min="0" step="1" />
            </label>
            <label class="copywriter-field">
              <span>分组 ID</span>
              <input v-model="draft.groupId" type="text" placeholder="可留空" />
            </label>
            <label class="copywriter-field">
              <span>设备 ID</span>
              <input v-model="draft.deviceId" type="text" placeholder="可留空" />
            </label>
          </div>

          <label class="copywriter-field">
            <span>备注</span>
            <input v-model="draft.notes" type="text" placeholder="可留空" />
          </label>
          <label class="copywriter-field">
            <span>标签</span>
            <input v-model="draft.tags" type="text" placeholder="用逗号分隔，可留空" />
          </label>

          <div class="copywriter-actions">
            <button class="dashboard-refresh" type="submit" :disabled="saving">
              {{ saving ? '保存中...' : isEditing ? '保存修改' : '新建账号' }}
            </button>
            <button class="dashboard-refresh" type="button" @click="prepareCreate">重置为新建</button>
          </div>
        </form>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>账号导入向导（CSV 文本）</h3>
          <span>先预检查，再执行导入。支持新建账号，或勾选“覆盖已存在账号”执行更新。</span>
        </div>

        <form class="copywriter-form" @submit.prevent="previewAccountImport">
          <label class="copywriter-field">
            <span>CSV 内容</span>
            <textarea
              v-model="importDraft.content"
              rows="8"
              placeholder="username,platform,region,status,risk_status,followers&#10;demo_a,tiktok,US,active,normal,1000"
            />
          </label>

          <div class="resource-summary-grid resource-summary-grid-triple">
            <label class="copywriter-field">
              <span>分隔符</span>
              <input v-model="importDraft.delimiter" type="text" maxlength="1" />
            </label>
            <label class="copywriter-field checkbox-field">
              <span>首行为表头</span>
              <input v-model="importDraft.hasHeader" type="checkbox" />
            </label>
            <label class="copywriter-field checkbox-field">
              <span>覆盖已存在账号</span>
              <input v-model="importDraft.updateExisting" type="checkbox" />
            </label>
          </div>

          <div class="copywriter-actions">
            <button class="dashboard-refresh" type="submit" :disabled="importLoading || importApplying">
              {{ importLoading ? '预检查中...' : '预检查导入内容' }}
            </button>
            <button class="dashboard-refresh" type="button" :disabled="importApplying" @click="applyAccountImport">
              {{ importApplying ? '导入执行中...' : '执行导入' }}
            </button>
            <button class="dashboard-refresh" type="button" @click="createDefaultImportDraftState">清空导入面板</button>
          </div>
        </form>

        <article class="resource-card">
          <p v-if="importError" class="resource-card-meta">{{ importError }}</p>
          <p v-else-if="importMessage" class="resource-card-meta">{{ importMessage }}</p>
          <p v-else class="resource-card-meta">请先执行预检查，再决定是否导入。</p>

          <template v-if="importPreview">
            <p class="resource-card-meta">
              预检查结果：总计 {{ importPreview.total }}，可导入 {{ importPreview.valid }}，无效 {{ importPreview.invalid }}，
              将新建 {{ importPreview.create }}，可更新 {{ importPreview.update }}
            </p>
            <p
              v-for="item in importPreview.items.slice(0, 20)"
              :key="`import-preview-${item.line}-${item.username}`"
              class="resource-card-meta"
            >
              第 {{ item.line }} 行 / {{ item.username || '（空用户名）' }}：{{ item.reason }}
            </p>
          </template>

          <template v-if="importApplyResult">
            <p class="resource-card-meta">
              导入执行结果：创建 {{ importApplyResult.created }}，更新 {{ importApplyResult.updated }}，
              跳过 {{ importApplyResult.skipped }}，无效 {{ importApplyResult.invalid }}
            </p>
            <p
              v-for="item in importApplyResult.items.slice(0, 20)"
              :key="`import-apply-${item.line}-${item.username}`"
              class="resource-card-meta"
            >
              第 {{ item.line }} 行 / {{ item.username || '（空用户名）' }}：{{ item.message }}
            </p>
          </template>
        </article>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { formatDateTime } from '../../modules/runtime/format';
import { useAccountsData } from '../../modules/accounts/useAccountsData';

const MANUAL_STATUS_LABELS: Record<string, string> = {
  active: '启用',
  warming: '预热',
  idle: '闲置',
  suspended: '停用',
  review: '待审核',
};

const SYSTEM_STATUS_LABELS: Record<string, string> = {
  online: '在线',
  syncing: '同步中',
  degraded: '降级',
  offline: '离线',
  unknown: '未知',
};

const RISK_STATUS_LABELS: Record<string, string> = {
  safe: '安全',
  watch: '观察',
  warning: '预警',
  high_risk: '高风险',
  blocked: '阻断',
  unknown: '未知',
};

const {
  accountDetail,
  activityCategory,
  activityCategoryOptions,
  activityError,
  activityLimit,
  activityLoading,
  activityQuery,
  activitySeverity,
  activitySeverityOptions,
  applyAccountImport,
  accounts,
  actionError,
  actionMessage,
  applyFilters,
  archiveAccount,
  archivedCount,
  archivingAccountId,
  beginEdit,
  bulkArchiveAccounts,
  bulkChangeGroup,
  bulkChangeManualStatus,
  bulkChangeRiskStatus,
  bulkDraft,
  bulkRestoreAccounts,
  bulkSuspendAccounts,
  bulkTestAccounts,
  bulkUnarchiveAccounts,
  bulkWorkingAction,
  createDefaultImportDraftState,
  clearFilters,
  clearSelectedAccounts,
  detailError,
  detailLoading,
  draft,
  error,
  filters,
  focusAccount,
  importApplyResult,
  importApplying,
  importDraft,
  importError,
  importLoading,
  importMessage,
  importPreview,
  isEditing,
  lifecycleReason,
  loadAccountActivity,
  loading,
  manualStatusOptions,
  previewAccountImport,
  prepareCreate,
  refreshAccounts,
  recentActivityItems,
  riskStatusOptions,
  saveAccount,
  saving,
  selectVisibleAccounts,
  selectedAccountCount,
  selectedAccountId,
  selectedAccountIds,
  setAccountSelection,
  suspendingAccountId,
  suspendAccount,
  systemStatusOptions,
  deletingAccountId,
  deleteAccount,
  testingAccountId,
  testAccountConnection,
  total,
  restoreAccount,
  restoringAccountId,
  visibleAccountCount,
} = useAccountsData();

function formatStatusLabel(value: string | null | undefined, labels: Record<string, string>): string {
  const normalized = (value || '').trim();
  if (!normalized) {
    return '未知';
  }
  return labels[normalized] || normalized;
}

function formatManualStatus(value: string | null | undefined): string {
  return formatStatusLabel(value, MANUAL_STATUS_LABELS);
}

function formatSystemStatus(value: string | null | undefined): string {
  return formatStatusLabel(value, SYSTEM_STATUS_LABELS);
}

function formatRiskStatus(value: string | null | undefined): string {
  return formatStatusLabel(value, RISK_STATUS_LABELS);
}

function formatActivitySeverity(value: string | null | undefined): string {
  const normalized = (value || '').trim().toLowerCase();
  if (!normalized) {
    return '信息';
  }
  if (normalized === 'success') {
    return '成功';
  }
  if (normalized === 'warning') {
    return '警告';
  }
  if (normalized === 'error') {
    return '错误';
  }
  return '信息';
}

function lifecycleConfirm(message: string): boolean {
  if (typeof window === 'undefined' || typeof window.confirm !== 'function') {
    return true;
  }
  return window.confirm(message);
}

function handleArchiveAccount(account: { id: number; username: string }) {
  if (!lifecycleConfirm(`确定归档账号「${account.username}」吗？归档后不会出现在默认列表中。`)) {
    return;
  }
  void archiveAccount(account);
}

function handleRestoreAccount(account: { id: number; username: string }) {
  if (!lifecycleConfirm(`确定恢复账号「${account.username}」吗？恢复后会自动回到启用状态。`)) {
    return;
  }
  void restoreAccount(account);
}

function handleSuspendAccount(account: { id: number; username: string }) {
  if (!lifecycleConfirm(`确定停用账号「${account.username}」吗？停用后该账号将不会参与任务执行。`)) {
    return;
  }
  void suspendAccount(account);
}

function handleDeleteAccount(account: { id: number; username: string }) {
  const expected = `DELETE ${account.username}`;
  let confirmed = false;
  if (typeof window !== 'undefined' && typeof window.prompt === 'function') {
    const input = window.prompt(`彻底删除账号「${account.username}」不可恢复。\n请输入 "${expected}" 以确认。`, '');
    confirmed = input === expected;
  } else {
    confirmed = lifecycleConfirm(`确定彻底删除账号「${account.username}」吗？此操作不可恢复。`);
  }
  if (!confirmed) {
    return;
  }
  void deleteAccount(account);
}

function handleSelectionChange(accountId: number, event: Event) {
  const target = event.target as HTMLInputElement | null;
  if (!target) {
    return;
  }
  setAccountSelection(accountId, target.checked);
}
</script>

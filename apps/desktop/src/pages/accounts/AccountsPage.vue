<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>账号管理</h2>
        <p class="resource-subtitle">
          支持搜索、人工状态筛选、系统状态筛选、风险状态筛选、显示归档和批量动作，主退出动作改为归档优先，列表与摘要都直接读取真实 runtime 数据。
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
          <span>先勾选账号，再统一处理人工状态、风险状态、分组、检测和归档</span>
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
              批量取消归档
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
                :disabled="unarchivingAccountId === account.id"
                @click="unarchiveAccount(account)"
              >
                {{ unarchivingAccountId === account.id ? '取消归档中...' : '取消归档' }}
              </button>
              <button
                v-else
                class="dashboard-refresh"
                type="button"
                :disabled="archivingAccountId === account.id"
                @click="archiveAccount(account)"
              >
                {{ archivingAccountId === account.id ? '归档中...' : '归档' }}
              </button>
            </div>
          </article>
        </div>

        <p v-else class="dashboard-empty">当前没有账号数据。</p>
      </section>

      <section class="dashboard-section">
        <div class="dashboard-section-title">
          <h3>账号详情摘要</h3>
          <span>绑定环境、最近错误和最近活动摘要会从 GET /accounts/{id} 直接读取</span>
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
        </article>
        <article v-else class="resource-card">
          <p class="resource-card-meta">请选择左侧一个账号查看详情摘要。</p>
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
  bulkTestAccounts,
  bulkUnarchiveAccounts,
  bulkWorkingAction,
  clearFilters,
  clearSelectedAccounts,
  detailError,
  detailLoading,
  draft,
  error,
  filters,
  focusAccount,
  isEditing,
  loading,
  manualStatusOptions,
  prepareCreate,
  refreshAccounts,
  riskStatusOptions,
  saveAccount,
  saving,
  selectVisibleAccounts,
  selectedAccountCount,
  selectedAccountIds,
  setAccountSelection,
  systemStatusOptions,
  testingAccountId,
  testAccountConnection,
  total,
  unarchiveAccount,
  unarchivingAccountId,
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

function handleSelectionChange(accountId: number, event: Event) {
  const target = event.target as HTMLInputElement | null;
  if (!target) {
    return;
  }
  setAccountSelection(accountId, target.checked);
}
</script>

<template>
  <section class="route-page" data-page-audit="account">
    <div class="breadcrumbs"><span>account</span><span>/</span><span>账号管理</span></div>
    <div class="page-header">
      <div>
        <div class="eyebrow">账号主列表</div>
        <h1>账号管理</h1>
        <p>把账号筛选、标签、环境操作和右侧详情收拢到同一页，避免再依赖空转弹框和占位任务。</p>
      </div>
      <div class="header-actions">
        <button class="secondary-button" type="button" @click="exportAccountList">导出账号清单</button>
        <button class="primary-button" type="button" :disabled="!accounts.length || workingAction === 'bulk-detect'" @click="runBulkDetectEnvironment">
          {{ workingAction === 'bulk-detect' ? '检测中...' : '批量检测环境' }}
        </button>
        <button class="secondary-button" type="button" :disabled="workingAction === 'create'" @click="createAccount">
          {{ workingAction === 'create' ? '创建中...' : '新建账号' }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载账号列表...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <section v-else class="section-stack">
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
      <p v-if="detailError" class="dashboard-banner dashboard-banner-error">{{ detailError }}</p>

      <div v-if="isolationBannerVisible" class="notice-banner js-account-isolation-banner">
        <div class="account-cell" style="align-items: flex-start;">
          <div>
            <strong>多账号隔离未全量启用</strong>
            <div class="js-account-isolation-copy">{{ isolationBannerCopy }}</div>
          </div>
        </div>
        <div class="toolbar__group">
          <button class="primary-button js-account-open-isolation" type="button" @click="openIsolationSettings">立即开启隔离</button>
          <button class="ghost-button js-account-dismiss-reminder" type="button" @click="dismissIsolationReminder">稍后提醒我</button>
        </div>
      </div>

      <div class="local-tabs" data-filter-group="accounts-status">
        <button class="local-tab js-account-status-tab" :class="{ 'is-active': statusFilter === 'all' }" data-filter-value="all" type="button" @click="setStatusFilter('all')">
          全部账号 ({{ accountStatusCounts.all }})
        </button>
        <button class="local-tab js-account-status-tab" :class="{ 'is-active': statusFilter === 'online' }" data-filter-value="online" type="button" @click="setStatusFilter('online')">
          在线 ({{ accountStatusCounts.online }})
        </button>
        <button class="local-tab js-account-status-tab" :class="{ 'is-active': statusFilter === 'offline' }" data-filter-value="offline" type="button" @click="setStatusFilter('offline')">
          离线 ({{ accountStatusCounts.offline }})
        </button>
        <button class="local-tab js-account-status-tab" :class="{ 'is-active': statusFilter === 'exception' }" data-filter-value="exception" type="button" @click="setStatusFilter('exception')">
          异常 ({{ accountStatusCounts.exception }})
        </button>
      </div>

      <div class="toolbar" style="justify-content: space-between;">
        <div class="filter-row">
          <div class="segmented" data-segmented data-view-toggle="accounts">
            <button class="js-account-view" :class="{ 'is-active': viewMode === 'card' }" data-view="card" type="button" @click="setViewMode('card')">卡片视图</button>
            <button class="js-account-view" :class="{ 'is-active': viewMode === 'list' }" data-view="list" type="button" @click="setViewMode('list')">列表视图</button>
          </div>
        </div>
        <div class="table-actions">
          <button class="secondary-button js-account-tag-batch" type="button" :disabled="workingAction === 'batch-tag'" @click="runBatchTagAction">
            {{ workingAction === 'batch-tag' ? '处理中...' : batchTagButtonText }}
          </button>
          <button class="ghost-button js-account-batch-cancel" :class="{ 'shell-hidden': !batchMode }" type="button" @click="cancelBatchMode">取消多选</button>
        </div>
      </div>

      <div class="account-grid" :class="{ 'list-mode': viewMode === 'list', 'is-batch-mode': batchMode }" data-collection="accounts">
        <div v-if="!accounts.length" class="empty-state" style="padding:48px;text-align:center;">
          <p>暂无账号数据</p>
          <p class="subtle">点击右上角「新建账号」添加第一个账号</p>
        </div>

        <article
          v-for="account in accounts"
          :key="account.id"
          class="account-card detail-trigger"
          :class="{ 'is-selected': selectedAccountId === account.id }"
          :data-id="account.id"
          :data-status="account.filterStatus"
          @click="handleCardClick(account.id, $event)"
        >
          <input
            type="checkbox"
            class="batch-check js-batch-account"
            :data-id="account.id"
            :checked="isAccountChecked(account.id)"
            :aria-label="`选择账号 ${account.username}`"
            @click.stop
            @change="handleBatchCheck(account.id, $event)"
          />

          <div class="account-card__head">
            <div>
              <strong>{{ account.username }}</strong>
              <div class="subtle">{{ account.subtitle }}</div>
            </div>
            <span class="status-chip" :class="account.statusTone">{{ account.statusLabel }}</span>
          </div>

          <div class="account-card__meta">
            <div class="list-row"><span class="subtle">账号 ID</span><strong class="mono">{{ account.id }}</strong></div>
            <div class="list-row"><span class="subtle">代理 IP</span><strong class="mono">{{ account.proxyLabel }}</strong></div>
            <div class="list-row"><span class="subtle">上次登录</span><strong>{{ account.lastLoginLabel }}</strong></div>
            <div class="list-row"><span class="subtle">Cookie 状态</span><span class="tag" :class="account.cookieTone">{{ account.cookieLabel }}</span></div>
            <div class="list-row"><span class="subtle">登录态校验</span><span class="tag" :class="account.loginCheckTone">{{ account.loginCheckLabel }}</span></div>
            <div class="list-row">
              <span class="subtle">标签</span>
              <div class="account-card__tags">
                <template v-if="account.tags.length">
                  <span v-for="tag in account.tags.slice(0, 3)" :key="`${account.id}-${tag}`" class="pill info">{{ tag }}</span>
                </template>
                <span v-else class="subtle">未打标签</span>
              </div>
            </div>
          </div>

          <div class="detail-actions account-card__actions">
            <button class="primary-button js-account-open-environment" type="button" :disabled="workingAction === 'open-environment'" @click.stop="openAccountEnvironment(account.id)">
              进入环境
            </button>
            <button class="secondary-button js-account-manage-cookies" type="button" :disabled="workingAction === 'manage-cookies'" @click.stop="manageAccountCookies(account.id)">
              Cookie 状态
            </button>
            <button class="secondary-button js-account-rebind-validate" type="button" :disabled="workingAction === 'rebind-validate'" @click.stop="rebindAndValidateAccount(account.id)">
              重绑并校验
            </button>
            <button class="ghost-button js-view-account" type="button" @click.stop="selectAccount(account.id)">查看详情与更多操作</button>
          </div>
        </article>
      </div>
    </section>

    <div v-if="editDialogVisible" class="modal-overlay" @click.self="closeEditDialog">
      <section class="modal-panel" style="width: min(560px, 92vw);">
        <header class="modal-header">
          <strong>编辑账号</strong>
          <button class="icon-button modal-close-btn" type="button" @click="closeEditDialog">×</button>
        </header>
        <div class="modal-body">
          <p v-if="editDialogError" class="dashboard-banner dashboard-banner-error">{{ editDialogError }}</p>
          <form v-if="editDialogDraft" class="modal-form" @submit.prevent="submitEditDialog">
            <label class="copywriter-field">
              <span>用户名</span>
              <input v-model="editDialogDraft.username" type="text" maxlength="120" />
            </label>
            <label class="copywriter-field">
              <span>平台</span>
              <select v-model="editDialogDraft.platform">
                <option value="tiktok">tiktok</option>
                <option value="tiktok_shop">tiktok_shop</option>
                <option value="instagram">instagram</option>
                <option value="youtube">youtube</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>地区</span>
              <select v-model="editDialogDraft.region">
                <option value="US">US</option>
                <option value="UK">UK</option>
                <option value="DE">DE</option>
                <option value="JP">JP</option>
                <option value="MY">MY</option>
                <option value="SG">SG</option>
                <option value="ID">ID</option>
                <option value="TH">TH</option>
                <option value="VN">VN</option>
                <option value="PH">PH</option>
                <option value="BR">BR</option>
                <option value="MX">MX</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>状态</span>
              <select v-model="editDialogDraft.status">
                <option value="active">在线</option>
                <option value="warming">预热中</option>
                <option value="idle">离线</option>
                <option value="suspended">异常</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>绑定设备</span>
              <select v-model="editDialogDraft.deviceId">
                <option value="">-- 不绑定设备 --</option>
                <option v-for="item in editDialogDeviceOptions" :key="`device-option-${item.id}`" :value="String(item.id)">
                  {{ item.label }}
                </option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>标签</span>
              <input v-model="editDialogDraft.tags" type="text" placeholder="例如 北美, 直播, 重点" />
            </label>
            <label class="copywriter-field">
              <span>Cookie 状态</span>
              <select v-model="editDialogDraft.cookieStatus">
                <option value="valid">有效</option>
                <option value="expiring">即将过期</option>
                <option value="invalid">已失效</option>
                <option value="missing">缺失</option>
                <option value="unknown">待确认</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>Cookie 内容</span>
              <textarea v-model="editDialogDraft.cookieContent" rows="5" class="mono" spellcheck="false"></textarea>
            </label>
            <label class="copywriter-field">
              <span>粉丝数</span>
              <input v-model.number="editDialogDraft.followers" type="number" min="0" />
            </label>
            <label class="copywriter-field">
              <span>备注</span>
              <textarea v-model="editDialogDraft.notes" rows="3"></textarea>
            </label>
            <div class="modal-footer">
              <button class="secondary-button" type="button" @click="closeEditDialog">取消</button>
              <button class="primary-button" type="submit" :disabled="editDialogSaving">
                {{ editDialogSaving ? '保存中...' : '保存修改' }}
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>

    <div v-if="deleteDialogVisible" class="modal-overlay" @click.self="closeDeleteDialog">
      <section class="modal-panel modal-panel--confirm" style="width: min(440px, 92vw);">
        <header class="modal-header">
          <strong>删除账号</strong>
          <button class="icon-button modal-close-btn" type="button" @click="closeDeleteDialog">×</button>
        </header>
        <div class="modal-body">
          <p class="resource-card-meta">确定删除账号「{{ deleteDialogTarget?.username || '--' }}」吗？系统会自动解绑相关任务和素材引用，此操作不可恢复。</p>
          <p v-if="deleteDialogError" class="dashboard-banner dashboard-banner-error">{{ deleteDialogError }}</p>
        </div>
        <div class="modal-footer">
          <button class="secondary-button" type="button" @click="closeDeleteDialog">取消</button>
          <button class="danger-button" type="button" :disabled="deleteDialogWorking" @click="confirmDeleteDialog">
            {{ deleteDialogWorking ? '删除中...' : '删除账号' }}
          </button>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useAccountsData } from '../../modules/accounts/useAccountsData';

const {
  accounts,
  loading,
  error,
  actionError,
  actionMessage,
  detailError,
  workingAction,
  editDialogVisible,
  editDialogSaving,
  editDialogError,
  editDialogDraft,
  editDialogDeviceOptions,
  deleteDialogVisible,
  deleteDialogWorking,
  deleteDialogError,
  deleteDialogTarget,
  statusFilter,
  viewMode,
  batchMode,
  selectedAccountId,
  batchTagButtonText,
  accountStatusCounts,
  isolationBannerVisible,
  isolationBannerCopy,
  setStatusFilter,
  setViewMode,
  selectAccount,
  toggleAccountSelection,
  runBatchTagAction,
  cancelBatchMode,
  isAccountChecked,
  dismissIsolationReminder,
  openIsolationSettings,
  openAccountEnvironment,
  manageAccountCookies,
  rebindAndValidateAccount,
  openEditDialog,
  closeEditDialog,
  submitEditDialog,
  openDeleteDialog,
  closeDeleteDialog,
  confirmDeleteDialog,
  runBulkDetectEnvironment,
  createAccount,
  exportAccountList,
} = useAccountsData();

function handleBatchCheck(accountId: number, event: Event): void {
  const target = event.target as HTMLInputElement | null;
  if (!target) {
    return;
  }
  toggleAccountSelection(accountId, target.checked);
}

function handleCardClick(accountId: number, event: MouseEvent): void {
  const target = event.target as HTMLElement | null;
  if (target?.closest('button, input, textarea, select, label, a')) {
    return;
  }
  void selectAccount(accountId);
}
</script>

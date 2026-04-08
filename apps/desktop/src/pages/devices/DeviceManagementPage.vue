<template>
  <section class="route-page device-management-shell" data-page-audit="device-management">
    <div class="breadcrumbs"><span>device-management</span><span>/</span><span>设备管理</span></div>
    <div class="page-header">
      <div>
        <div class="eyebrow">环境治理</div>
        <h1>设备管理</h1>
        <p>统一查看浏览器隔离环境、代理、指纹和设备账号绑定关系，把设备动作与右侧详情收拢到同一页。</p>
      </div>
      <div class="header-actions">
        <button class="secondary-button" type="button" @click="exportDeviceReport">导出设备报告</button>
        <button class="secondary-button" type="button" :disabled="workingAction === 'batch-inspect'" @click="runBatchInspect">
          {{ workingAction === 'batch-inspect' ? '巡检中...' : batchInspectButtonText }}
        </button>
        <button class="secondary-button" type="button" :disabled="workingAction === 'repair-device' || !selectedDeviceId" @click="selectedDeviceId && repairDevice(selectedDeviceId)">
          {{ workingAction === 'repair-device' ? '修复中...' : '修复环境' }}
        </button>
        <button class="primary-button" type="button" :disabled="workingAction === 'create'" @click="openCreateDialog">新增设备环境</button>
      </div>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载设备列表...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>

    <section v-else class="section-stack">
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>
      <p v-if="detailError" class="dashboard-banner dashboard-banner-error">{{ detailError }}</p>

      <div v-if="!bannerDismissed" class="notice-banner" data-device-banner>
        <div>
          <strong>{{ bannerSummary }}</strong>
          <div>{{ bannerDetail }}</div>
        </div>
        <div class="toolbar__group">
          <button class="ghost-button js-device-banner-dismiss" type="button" @click="dismissBanner">关闭</button>
        </div>
      </div>

      <div class="stat-grid">
        <article class="stat-card">
          <div class="stat-card__label">设备总数</div>
          <div class="stat-card__value">{{ deviceStatusCounts.all }}</div>
          <div class="stat-card__meta">已纳入统一环境治理的设备数量</div>
        </article>
        <article class="stat-card">
          <div class="stat-card__label">隔离覆盖率</div>
          <div class="stat-card__value">{{ isolationCoveragePercent }}%</div>
          <div class="stat-card__meta">已绑定且启用隔离环境的账号占比</div>
        </article>
        <article class="stat-card">
          <div class="stat-card__label">待处理设备</div>
          <div class="stat-card__value">{{ abnormalCount }}</div>
          <div class="stat-card__meta">当前存在告警或异常的设备数量</div>
        </article>
        <article class="stat-card">
          <div class="stat-card__label">空闲设备</div>
          <div class="stat-card__value">{{ idleCount }}</div>
          <div class="stat-card__meta">可继续分配给账号的空闲设备池</div>
        </article>
      </div>

      <div class="local-tabs" data-filter-group="device-status">
        <button class="local-tab" :class="{ 'is-active': statusFilter === 'all' }" data-filter-value="all" type="button" @click="setStatusFilter('all')">全部 ({{ deviceStatusCounts.all }})</button>
        <button class="local-tab" :class="{ 'is-active': statusFilter === 'healthy' }" data-filter-value="healthy" type="button" @click="setStatusFilter('healthy')">正常 ({{ deviceStatusCounts.healthy }})</button>
        <button class="local-tab" :class="{ 'is-active': statusFilter === 'warning' }" data-filter-value="warning" type="button" @click="setStatusFilter('warning')">告警 ({{ deviceStatusCounts.warning }})</button>
        <button class="local-tab" :class="{ 'is-active': statusFilter === 'error' }" data-filter-value="error" type="button" @click="setStatusFilter('error')">异常 ({{ deviceStatusCounts.error }})</button>
        <button class="local-tab" :class="{ 'is-active': statusFilter === 'idle' }" data-filter-value="idle" type="button" @click="setStatusFilter('idle')">空闲 ({{ deviceStatusCounts.idle }})</button>
      </div>

      <div class="toolbar" style="justify-content: space-between;">
        <div class="segmented" data-view-toggle="devices">
          <button class="js-device-view" :class="{ 'is-active': viewMode === 'card' }" data-view="card" type="button" @click="setViewMode('card')">卡片视图</button>
          <button class="js-device-view" :class="{ 'is-active': viewMode === 'list' }" data-view="list" type="button" @click="setViewMode('list')">列表视图</button>
        </div>
        <div class="table-actions">
          <button class="secondary-button" type="button" :disabled="workingAction === 'batch-inspect'" @click="runBatchInspect">
            {{ workingAction === 'batch-inspect' ? '巡检中...' : batchInspectButtonText }}
          </button>
          <button class="secondary-button" type="button" :disabled="workingAction === 'batch-delete'" @click="runBatchDelete">{{ workingAction === 'batch-delete' ? '删除中...' : batchButtonText }}</button>
          <button class="ghost-button" type="button" :class="{ 'shell-hidden': !batchMode }" @click="cancelBatchMode">取消多选</button>
        </div>
      </div>

      <div class="device-env-grid" :class="{ 'list-mode': viewMode === 'list', 'is-batch-mode': batchMode }">
        <div v-if="!devices.length" class="empty-state device-empty-state">
          <p>暂无设备数据</p>
          <p class="subtle">点击右上角「新增设备环境」添加第一台设备</p>
        </div>

        <article
          v-for="device in devices"
          :key="device.id"
          class="device-env-card detail-trigger"
          :class="[{ 'is-selected': selectedDeviceId === device.id }, `device-env-card--${device.status}`]"
          :data-id="device.id"
          :data-status="device.status"
          @click="selectDevice(device.id)"
        >
          <div class="device-env-card__head">
            <label class="batch-check-wrap">
              <input
                type="checkbox"
                class="batch-check js-batch-device"
                :data-id="device.id"
                :checked="isDeviceChecked(device.id)"
                :aria-label="`选择设备 ${device.name}`"
                @click.stop
                @change="toggleDeviceSelection(device.id, ($event.target as HTMLInputElement).checked)"
              />
              <span></span>
            </label>
            <strong>{{ device.name }}</strong>
            <span class="status-chip" :class="device.statusTone">{{ device.statusLabel }}</span>
          </div>

          <div class="device-env-card__meta">
            <div class="list-row"><span class="subtle">设备编码</span><strong class="mono">{{ device.deviceCode }}</strong></div>
            <div class="list-row"><span class="subtle">代理 IP</span><strong class="mono">{{ device.proxyLabel }}</strong></div>
            <div class="list-row"><span class="subtle">地区</span><strong>{{ device.regionLabel }}</strong></div>
            <div class="list-row"><span class="subtle">绑定账号</span><strong>{{ device.boundCount }} 个</strong></div>
            <div class="list-row"><span class="subtle">隔离覆盖</span><strong>{{ device.coveragePercent }}%</strong></div>
            <div class="list-row"><span class="subtle">最近巡检</span><strong>{{ device.lastInspectionLabel }}</strong></div>
          </div>

          <div class="detail-actions device-card__actions">
            <button class="secondary-button js-view-device" type="button" @click.stop="selectDevice(device.id)">查看详情</button>
            <button class="ghost-button js-edit-device" type="button" @click.stop="openEditDialog(device.id)">编辑</button>
          </div>
        </article>
      </div>

      <div class="analytics-two-column">
        <section class="panel">
          <div class="panel__header">
            <div>
              <strong>设备绑定表</strong>
              <div class="subtle">按设备查看账号绑定关系与隔离覆盖情况。</div>
            </div>
            <span class="status-chip info">绑定</span>
          </div>
          <div class="table-shell">
            <table class="route-table">
              <thead>
                <tr>
                  <th>设备编码</th>
                  <th>绑定账号</th>
                  <th>隔离覆盖</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody data-device-binding-body>
                <tr v-if="!devices.length">
                  <td colspan="5" class="device-table-empty">暂无绑定数据</td>
                </tr>
                <tr v-for="device in devices" :key="`binding-${device.id}`" class="route-row js-device-binding-row" :data-id="device.id" @click="selectDevice(device.id)">
                  <td class="mono"><strong>{{ device.deviceCode }}</strong></td>
                  <td>
                    <div class="device-binding-tags">
                      <span v-if="!device.boundAccounts.length" class="subtle">暂无绑定账号</span>
                      <span v-for="account in device.boundAccounts" :key="`bind-${device.id}-${account.id}`" class="tag" :class="account.isolationEnabled ? 'success' : 'warning'">
                        {{ account.username }}
                      </span>
                    </div>
                  </td>
                  <td>{{ device.coverageLabel }}</td>
                  <td><span class="status-chip" :class="device.statusTone">{{ device.statusLabel }}</span></td>
                  <td>
                    <button class="ghost-button js-adjust-device-binding" type="button" @click.stop="openBindingDialog(device.id)">调整绑定</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel" data-device-coverage-panel>
          <div class="panel__header">
            <div>
              <strong>覆盖率面板</strong>
              <div class="subtle">用于识别未覆盖账号和空闲设备池。</div>
            </div>
            <span class="status-chip info">覆盖</span>
          </div>
          <div class="device-coverage-bar">
            <div class="coverage-track">
              <div class="coverage-fill" :style="{ width: `${isolationCoveragePercent}%` }"></div>
            </div>
            <div class="coverage-labels">
              <span>已隔离 {{ totalAccountCount - uncoveredAccounts.length }} 个账号</span>
              <span>未覆盖 {{ uncoveredAccounts.length }} 个账号</span>
            </div>
          </div>
          <div class="device-pool-summary">
            <div class="task-item is-selected">
              <div>
                <strong>未覆盖账号</strong>
                <div class="subtle">{{ uncoveredAccounts.slice(0, 3).map((item) => item.username || `账号#${item.id}`).join('、') || '暂无' }}</div>
              </div>
              <span class="pill warning">{{ isolationCoveragePercent }}%</span>
            </div>
            <div class="task-item">
              <div>
                <strong>空闲设备池</strong>
                <div class="subtle">当前有 {{ idleCount }} 台空闲设备可继续分配</div>
              </div>
              <span class="pill info">调度</span>
            </div>
          </div>
        </section>
      </div>
    </section>

    <div v-if="dialogVisible" class="modal-overlay" @click.self="closeDialog">
      <section class="modal-panel" style="width: min(560px, 92vw);">
        <header class="modal-header">
          <strong>{{ dialogDraft?.deviceId ? '编辑设备' : '新增设备环境' }}</strong>
          <button class="icon-button modal-close-btn" type="button" @click="closeDialog">×</button>
        </header>
        <div class="modal-body">
          <p v-if="dialogError" class="dashboard-banner dashboard-banner-error">{{ dialogError }}</p>
          <form v-if="dialogDraft" class="modal-form" @submit.prevent="submitDialog">
            <label class="copywriter-field">
              <span>设备编码</span>
              <input v-model="dialogDraft.deviceCode" type="text" maxlength="80" />
            </label>
            <label class="copywriter-field">
              <span>设备名称</span>
              <input v-model="dialogDraft.name" type="text" maxlength="120" />
            </label>
            <label class="copywriter-field">
              <span>代理 IP</span>
              <input v-model="dialogDraft.proxyIp" type="text" placeholder="例如 10.10.10.11:18080" />
            </label>
            <label class="copywriter-field">
              <span>地区</span>
              <select v-model="dialogDraft.region">
                <option value="US">US</option>
                <option value="UK">UK</option>
                <option value="DE">DE</option>
                <option value="JP">JP</option>
                <option value="SG">SG</option>
                <option value="MY">MY</option>
                <option value="ID">ID</option>
                <option value="TH">TH</option>
                <option value="VN">VN</option>
                <option value="PH">PH</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>设备状态</span>
              <select v-model="dialogDraft.status">
                <option value="healthy">healthy</option>
                <option value="warning">warning</option>
                <option value="error">error</option>
                <option value="idle">idle</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>代理状态</span>
              <select v-model="dialogDraft.proxyStatus">
                <option value="healthy">healthy</option>
                <option value="warning">warning</option>
                <option value="error">error</option>
                <option value="unknown">unknown</option>
              </select>
            </label>
            <label class="copywriter-field">
              <span>指纹状态</span>
              <select v-model="dialogDraft.fingerprintStatus">
                <option value="ready">ready</option>
                <option value="warning">warning</option>
                <option value="error">error</option>
                <option value="unknown">unknown</option>
              </select>
            </label>
            <div class="modal-footer">
              <button class="secondary-button" type="button" @click="closeDialog">取消</button>
              <button class="primary-button" type="submit" :disabled="dialogSaving">{{ dialogSaving ? '保存中...' : '保存设备' }}</button>
            </div>
          </form>
        </div>
      </section>
    </div>

    <div v-if="bindingDialogVisible" class="modal-overlay" @click.self="closeBindingDialog">
      <section class="modal-panel" style="width: min(720px, 94vw);">
        <header class="modal-header">
          <strong>绑定账号</strong>
          <button class="icon-button modal-close-btn" type="button" @click="closeBindingDialog">×</button>
        </header>
        <div class="modal-body">
          <p class="resource-card-meta">当前设备：{{ bindingDialogTarget?.name || '--' }}。可直接勾选需要绑定的账号，取消勾选即解除绑定。</p>
          <p v-if="bindingDialogError" class="dashboard-banner dashboard-banner-error">{{ bindingDialogError }}</p>
          <div class="toolbar" style="justify-content: space-between; margin-bottom: 12px;">
            <div class="subtle">已选择 {{ bindingDialogSelectedCount }} 个账号</div>
            <div class="table-actions">
              <button class="ghost-button" type="button" @click="setAllBindingAccounts(true)">全选</button>
              <button class="ghost-button" type="button" @click="setAllBindingAccounts(false)">清空</button>
            </div>
          </div>
          <div class="binding-account-grid">
            <label v-for="item in bindingDialogOptions" :key="`binding-option-${item.accountId}`" class="binding-account-card">
              <input type="checkbox" :checked="item.selected" @change="toggleBindingAccount(item.accountId, ($event.target as HTMLInputElement).checked)" />
              <div>
                <strong>{{ item.username }}</strong>
                <div class="subtle">{{ item.regionLabel }} / {{ item.tagsLabel }}</div>
                <div class="subtle">{{ item.isolationLabel }}</div>
              </div>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="secondary-button" type="button" @click="closeBindingDialog">取消</button>
          <button class="primary-button" type="button" :disabled="bindingDialogSaving" @click="submitBindingDialog">
            {{ bindingDialogSaving ? '保存中...' : '保存绑定关系' }}
          </button>
        </div>
      </section>
    </div>

    <div v-if="deleteDialogVisible" class="modal-overlay" @click.self="closeDeleteDialog">
      <section class="modal-panel modal-panel--confirm" style="width: min(440px, 92vw);">
        <header class="modal-header">
          <strong>删除设备</strong>
          <button class="icon-button modal-close-btn" type="button" @click="closeDeleteDialog">×</button>
        </header>
        <div class="modal-body">
          <p class="resource-card-meta">确定删除设备「{{ deleteDialogTarget?.name || '--' }}」吗？绑定的账号关系将同时解除，此操作不可恢复。</p>
          <p v-if="deleteDialogError" class="dashboard-banner dashboard-banner-error">{{ deleteDialogError }}</p>
        </div>
        <div class="modal-footer">
          <button class="secondary-button" type="button" @click="closeDeleteDialog">取消</button>
          <button class="danger-button" type="button" :disabled="deleteDialogWorking" @click="confirmDeleteDialog">{{ deleteDialogWorking ? '删除中...' : '删除设备' }}</button>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useDevicesData } from '../../modules/devices/useDevicesData';

const {
  devices,
  loading,
  error,
  actionError,
  actionMessage,
  detailError,
  workingAction,
  statusFilter,
  viewMode,
  selectedDeviceId,
  batchMode,
  bannerDismissed,
  bannerSummary,
  bannerDetail,
  deviceStatusCounts,
  abnormalCount,
  idleCount,
  totalAccountCount,
  isolationCoveragePercent,
  uncoveredAccounts,
  batchButtonText,
  batchInspectButtonText,
  dialogVisible,
  dialogSaving,
  dialogError,
  dialogDraft,
  bindingDialogVisible,
  bindingDialogSaving,
  bindingDialogError,
  bindingDialogTarget,
  bindingDialogOptions,
  bindingDialogSelectedCount,
  deleteDialogVisible,
  deleteDialogWorking,
  deleteDialogError,
  deleteDialogTarget,
  setStatusFilter,
  setViewMode,
  selectDevice,
  isDeviceChecked,
  toggleDeviceSelection,
  dismissBanner,
  repairDevice,
  adjustBinding,
  openBindingDialog,
  closeBindingDialog,
  toggleBindingAccount,
  setAllBindingAccounts,
  submitBindingDialog,
  openCreateDialog,
  openEditDialog,
  closeDialog,
  submitDialog,
  closeDeleteDialog,
  confirmDeleteDialog,
  runBatchDelete,
  runBatchInspect,
  cancelBatchMode,
  exportDeviceReport,
} = useDevicesData();
</script>
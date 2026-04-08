<template>
  <aside class="detail-panel" :class="{ 'shell-hidden': !shell.detailPanelVisible }">
    <div
      class="detail-root"
      v-if="isDashboardRoute"
      :data-dashboard-detail-kind="dashboardDetailKind"
      :class="{ 'is-activity': isActivityDetail, 'is-system': isSystemDetail, 'is-quick-action': isQuickActionDetail }"
    >
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.dashboardDetailState.title }}</strong>
            <div class="subtle">{{ shell.dashboardDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.dashboardDetailState.statusTone">{{ shell.dashboardDetailState.statusLabel }}</span>
        </div>
        <div class="detail-list">
          <div v-for="item in shell.dashboardDetailState.items" :key="item.label" class="detail-item">
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isAccountRoute" :data-account-detail-kind="accountDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.accountDetailState.title }}</strong>
            <div class="subtle">{{ shell.accountDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.accountDetailState.statusTone">{{ shell.accountDetailState.statusLabel }}</span>
        </div>
        <div class="data-points">
          <div v-for="item in shell.accountDetailState.dataPoints" :key="`point-${item.label}`" class="data-point">
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-list">
          <div
            v-for="item in shell.accountDetailState.detailItems"
            :key="`detail-${item.label}`"
            class="detail-item"
            :class="{ 'detail-item--stacked': item.stacked }"
          >
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('open-environment')">进入环境</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('manage-cookies')">Cookie 状态</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('rebind-validate')">重绑并校验</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('validate-login')">校验登录态</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('test-connection')">检测代理</button>
          <button class="ghost-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('edit-account')">编辑账号</button>
          <button class="danger-button" type="button" :disabled="!hasSelectedAccount" @click="dispatchAccountAction('delete-account')">删除账号</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.accountDetailState.dutySummary.title }}</strong>
            <div class="subtle">{{ shell.accountDetailState.dutySummary.copy }}</div>
          </div>
          <span class="status-chip" :class="shell.accountDetailState.dutySummary.tone">{{ shell.accountDetailState.dutySummary.badge }}</span>
        </div>
        <div class="audit-list">
          <div v-for="item in shell.accountDetailState.adviceItems" :key="`${item.title}-${item.badge}`" class="audit-item">
            <div>
              <strong>{{ item.title }}</strong>
              <div class="subtle audit-item__copy">{{ item.copy }}</div>
            </div>
            <span class="pill" :class="item.tone">{{ item.badge }}</span>
          </div>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isDeviceRoute" :data-device-detail-kind="deviceDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.deviceDetailState.title }}</strong>
            <div class="subtle">{{ shell.deviceDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.deviceDetailState.statusTone">{{ shell.deviceDetailState.statusLabel }}</span>
        </div>
        <div class="data-points">
          <div v-for="item in shell.deviceDetailState.dataPoints" :key="`device-point-${item.label}`" class="data-point">
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" :disabled="!hasSelectedDevice" @click="dispatchDeviceAction('open-environment')">打开环境</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedDevice" @click="dispatchDeviceAction('adjust-binding')">修改绑定</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedDevice" @click="dispatchDeviceAction('open-logs')">环境日志</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedDevice" @click="dispatchDeviceAction('inspect-device')">巡检设备</button>
          <button class="ghost-button" type="button" :disabled="!hasSelectedDevice" @click="dispatchDeviceAction('edit-device')">编辑设备</button>
          <button class="danger-button" type="button" :disabled="!hasSelectedDevice" @click="dispatchDeviceAction('delete-device')">删除设备</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>巡检结果</strong>
            <div class="subtle">根据真实代理、指纹与绑定账号覆盖率生成。</div>
          </div>
          <span class="status-chip info">设备巡检</span>
        </div>
        <div class="audit-list">
          <div v-if="!shell.deviceDetailState.issues.length" class="audit-item">
            <div>
              <strong>当前设备状态正常</strong>
              <div class="subtle audit-item__copy">代理、指纹和绑定账号状态均未发现明显阻塞。</div>
            </div>
            <span class="pill success">正常</span>
          </div>
          <div v-for="item in shell.deviceDetailState.issues" :key="`${item.title}-${item.copy}`" class="audit-item">
            <div>
              <strong>{{ item.title }}</strong>
              <div class="subtle audit-item__copy">{{ item.copy }}</div>
            </div>
            <span class="pill" :class="item.tone">{{ deviceIssueLabel(item.tone) }}</span>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>环境日志</strong>
            <div class="subtle">展示当前设备最近的环境动作与修复记录。</div>
          </div>
          <button
            v-if="shell.deviceDetailState.logs.length > 6"
            class="ghost-button"
            type="button"
            :disabled="!hasSelectedDevice"
            @click="dispatchDeviceAction('toggle-logs')"
          >
            {{ shell.deviceDetailState.logsCollapsed ? '展开全部日志' : '收起较早日志' }}
          </button>
        </div>
        <div class="audit-list">
          <div v-if="!visibleDeviceLogs.length" class="audit-item">
            <div>
              <strong>暂无日志</strong>
              <div class="subtle audit-item__copy">执行打开环境、巡检或修复后，会在这里展示设备级日志详情。</div>
            </div>
            <span class="pill info">空</span>
          </div>
          <div v-for="item in visibleDeviceLogs" :key="`device-log-${item.id}`" class="audit-item device-log-item">
            <div>
              <strong>{{ item.title }}</strong>
              <div class="subtle audit-item__copy">{{ item.message }}</div>
              <div class="subtle">{{ item.createdAt }}</div>
            </div>
            <span class="pill" :class="deviceLogTone(item.category)">{{ item.category }}</span>
          </div>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isScheduledPublishRoute" :data-scheduled-publish-detail-kind="publishDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.publishDetailState.title }}</strong>
            <div class="subtle">{{ shell.publishDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.publishDetailState.statusTone">{{ shell.publishDetailState.statusLabel }}</span>
        </div>
        <div class="detail-list">
          <div
            v-for="item in shell.publishDetailState.detailItems"
            :key="`publish-detail-${item.label}`"
            class="detail-item"
            :class="{ 'detail-item--stacked': item.stacked }"
          >
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" :disabled="!hasSelectedPublishPlan" @click="dispatchPublishAction('start-plan')">启动计划</button>
          <button class="secondary-button" type="button" @click="dispatchPublishAction('toggle-calendar')">切换日历</button>
          <button class="danger-button" type="button" :disabled="!hasSelectedPublishPlan" @click="dispatchPublishAction('delete-plan')">删除计划</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>排程建议</strong>
            <div class="subtle">根据当前发布计划状态、账号排班和素材库存生成。</div>
          </div>
          <span class="status-chip info">建议</span>
        </div>
        <div class="board-list">
          <article v-if="!shell.publishDetailState.adviceItems.length" class="board-card">
            <strong>等待选择发布计划</strong>
            <div class="subtle">左侧列表选中后，这里会显示旧壳同源的排程建议卡片。</div>
            <div class="status-strip"><span class="pill info">待选择</span></div>
          </article>
          <article v-for="item in shell.publishDetailState.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
            <strong>{{ item.title }}</strong>
            <div class="subtle">{{ item.copy }}</div>
            <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
          </article>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isDataCollectorRoute" :data-data-collector-detail-kind="collectorDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.collectorDetailState.title }}</strong>
            <div class="subtle">{{ shell.collectorDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.collectorDetailState.statusTone">{{ shell.collectorDetailState.statusLabel }}</span>
        </div>
        <div class="detail-list">
          <div
            v-for="item in shell.collectorDetailState.detailItems"
            :key="`collector-detail-${item.label}`"
            class="detail-item"
            :class="{ 'detail-item--stacked': item.stacked }"
          >
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" :disabled="!hasSelectedCollectorTask" @click="dispatchCollectorAction('start-task')">启动任务</button>
          <button class="secondary-button" type="button" @click="dispatchCollectorAction('view-proxy-pool')">查看代理池</button>
          <button class="danger-button" type="button" :disabled="!hasSelectedCollectorTask" @click="dispatchCollectorAction('delete-task')">删除任务</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>补偿建议</strong>
            <div class="subtle">针对当前采集任务给出代理池、资源和重试建议。</div>
          </div>
          <span class="status-chip info">建议</span>
        </div>
        <div class="board-list">
          <article v-if="!shell.collectorDetailState.adviceItems.length" class="board-card">
            <strong>等待选择采集任务</strong>
            <div class="subtle">左侧表格或看板选中后，这里会显示采集补偿建议卡片。</div>
            <div class="status-strip"><span class="pill info">待选择</span></div>
          </article>
          <article v-for="item in shell.collectorDetailState.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
            <strong>{{ item.title }}</strong>
            <div class="subtle">{{ item.copy }}</div>
            <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
          </article>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isCreativeWorkshopRoute" :data-creative-workshop-detail-kind="creativeDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.creativeDetailState.title }}</strong>
            <div class="subtle">{{ shell.creativeDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.creativeDetailState.statusTone">{{ shell.creativeDetailState.statusLabel }}</span>
        </div>
        <div class="detail-list">
          <div
            v-for="item in shell.creativeDetailState.detailItems"
            :key="`creative-detail-${item.label}`"
            class="detail-item"
            :class="{ 'detail-item--stacked': item.stacked }"
          >
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" @click="dispatchCreativeAction('save-plan')">保存创意方案</button>
          <button class="secondary-button" type="button" @click="dispatchCreativeAction('compare-views')">对比创意版本</button>
          <button class="ghost-button" type="button" @click="dispatchCreativeAction('goto-video-editor')">进入视频编辑</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>创意建议</strong>
            <div class="subtle">优先确认当前保留方案、主要冲突点和下一轮对比目标。</div>
          </div>
          <span class="status-chip info">建议</span>
        </div>
        <div class="board-list">
          <article v-if="!shell.creativeDetailState.adviceItems.length" class="board-card">
            <strong>等待选择实验项目</strong>
            <div class="subtle">左侧项目列表选中后，这里会显示创意实验建议卡片。</div>
            <div class="status-strip"><span class="pill info">待选择</span></div>
          </article>
          <article v-for="item in shell.creativeDetailState.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
            <strong>{{ item.title }}</strong>
            <div class="subtle">{{ item.copy }}</div>
            <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
          </article>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isAiContentFactoryRoute" :data-ai-content-factory-detail-kind="aiContentFactoryDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.aiContentFactoryDetailState.title }}</strong>
            <div class="subtle">{{ shell.aiContentFactoryDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.aiContentFactoryDetailState.statusTone">{{ shell.aiContentFactoryDetailState.statusLabel }}</span>
        </div>
        <div class="detail-list">
          <div
            v-for="item in shell.aiContentFactoryDetailState.detailItems"
            :key="`aicf-detail-${item.label}`"
            class="detail-item"
            :class="{ 'detail-item--stacked': item.stacked }"
          >
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" @click="dispatchAiContentFactoryAction('save-workflow')">保存工作流</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedWorkflowDefinition" @click="dispatchAiContentFactoryAction('run-batch')">运行批次</button>
          <button class="ghost-button" type="button" :disabled="!hasSelectedWorkflowDefinition" @click="dispatchAiContentFactoryAction('run-workflow')">运行工作流</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>工作流建议</strong>
            <div class="subtle">优先确认当前批次、失败节点和下发路径，避免把内容工厂退化成静态 AI 卡片页。</div>
          </div>
          <span class="status-chip info">建议</span>
        </div>
        <div class="board-list">
          <article v-if="!shell.aiContentFactoryDetailState.adviceItems.length" class="board-card">
            <strong>等待选择工作流</strong>
            <div class="subtle">左侧工作流列表选中后，这里会显示内容工厂的运行建议卡片。</div>
            <div class="status-strip"><span class="pill info">待选择</span></div>
          </article>
          <article v-for="item in shell.aiContentFactoryDetailState.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
            <strong>{{ item.title }}</strong>
            <div class="subtle">{{ item.copy }}</div>
            <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
          </article>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else-if="isVideoEditorRoute" :data-video-editor-detail-kind="videoEditorDetailKind">
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>{{ shell.videoEditorDetailState.title }}</strong>
            <div class="subtle">{{ shell.videoEditorDetailState.subtitle }}</div>
          </div>
          <span class="status-chip" :class="shell.videoEditorDetailState.statusTone">{{ shell.videoEditorDetailState.statusLabel }}</span>
        </div>
        <div class="detail-list">
          <div
            v-for="item in shell.videoEditorDetailState.detailItems"
            :key="`video-editor-detail-${item.label}`"
            class="detail-item"
            :class="{ 'detail-item--stacked': item.stacked }"
          >
            <span class="subtle">{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
        <div class="detail-actions account-detail__actions">
          <button class="primary-button" type="button" :disabled="!shell.videoEditorDetailState.canExportFinal" @click="dispatchVideoEditorAction('export-final')">发起终版导出</button>
          <button class="secondary-button" type="button" :disabled="!shell.videoEditorDetailState.canPreviewExport" @click="dispatchVideoEditorAction('export-preview')">试看导出</button>
          <button class="secondary-button" type="button" :disabled="!hasSelectedVideoProject" @click="dispatchVideoEditorAction('switch-sequence')">切换剪辑序列</button>
          <button class="ghost-button" type="button" :disabled="!shell.videoEditorDetailState.canCreateSubtitle" @click="dispatchVideoEditorAction('create-subtitle')">新增字幕</button>
          <button class="ghost-button" type="button" :disabled="!shell.videoEditorDetailState.canSaveSnapshot" @click="dispatchVideoEditorAction('save-snapshot')">保存快照</button>
          <button class="ghost-button" type="button" :disabled="!shell.videoEditorDetailState.canRestoreSnapshot" @click="dispatchVideoEditorAction('restore-snapshot')">恢复快照</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>剪辑建议</strong>
            <div class="subtle">优先确认当前序列、失败导出和快照恢复路径，避免把视频编辑页退化成静态时间线。</div>
          </div>
          <span class="status-chip info">建议</span>
        </div>
        <div class="board-list">
          <article v-if="!shell.videoEditorDetailState.adviceItems.length" class="board-card">
            <strong>等待选择工程</strong>
            <div class="subtle">进入视频工程后，这里会显示当前导出、快照和字幕相关建议。</div>
            <div class="status-strip"><span class="pill info">待选择</span></div>
          </article>
          <article v-for="item in shell.videoEditorDetailState.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
            <strong>{{ item.title }}</strong>
            <div class="subtle">{{ item.copy }}</div>
            <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
          </article>
        </div>
      </section>
    </div>

    <div class="detail-root" v-else>
      <section class="panel">
        <div class="panel__header">
          <div>
            <strong>当前页面摘要</strong>
            <div class="subtle">用于承接页面说明、宿主状态和页面级上下文。</div>
          </div>
          <span class="status-chip info">详情区</span>
        </div>
        <div class="detail-list">
          <div class="detail-item">
            <span class="subtle">页面</span>
            <strong>{{ shell.currentRouteTitle }}</strong>
          </div>
          <div class="detail-item detail-item--stacked">
            <span class="subtle">说明</span>
            <strong>{{ shell.currentRouteSummary }}</strong>
          </div>
          <div class="detail-item">
            <span class="subtle">宿主</span>
            <strong>{{ hostMode }}</strong>
          </div>
          <div class="detail-item detail-item--stacked">
            <span class="subtle">运行时端点</span>
            <strong>{{ runtimeEndpoint }}</strong>
          </div>
        </div>
      </section>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import { useShellStore } from '../modules/shell/useShellStore';
import { mapRuntimeLaunchMode, mapRuntimeStatus } from '../modules/runtime/runtimePresentation';

const shell = useShellStore();

const isDashboardRoute = computed(() => shell.currentRouteName === 'dashboard');
const isScheduledPublishRoute = computed(() => shell.currentRouteName === 'scheduled-publish');
const isDataCollectorRoute = computed(() => shell.currentRouteName === 'data-collector');
const isCreativeWorkshopRoute = computed(() => shell.currentRouteName === 'creative-workshop');
const isAiContentFactoryRoute = computed(() => shell.currentRouteName === 'ai-content-factory');
const isVideoEditorRoute = computed(() => shell.currentRouteName === 'video-editor');
const isAccountRoute = computed(() => shell.currentRouteName === 'account');
const isDeviceRoute = computed(() => shell.currentRouteName === 'device-management');
const dashboardDetailKind = computed(() => shell.dashboardDetailState.kind);
const publishDetailKind = computed(() => shell.publishDetailState.kind);
const collectorDetailKind = computed(() => shell.collectorDetailState.kind);
const creativeDetailKind = computed(() => shell.creativeDetailState.kind);
const aiContentFactoryDetailKind = computed(() => shell.aiContentFactoryDetailState.kind);
const videoEditorDetailKind = computed(() => shell.videoEditorDetailState.kind);
const accountDetailKind = computed(() => shell.accountDetailState.kind);
const deviceDetailKind = computed(() => shell.deviceDetailState.kind);
const isActivityDetail = computed(() => shell.dashboardDetailState.kind === 'activity');
const isSystemDetail = computed(() => shell.dashboardDetailState.kind === 'system');
const isQuickActionDetail = computed(() => shell.dashboardDetailState.kind === 'quick-action');
const hasSelectedAccount = computed(() => typeof shell.accountDetailState.accountId === 'number');
const hasSelectedDevice = computed(() => typeof shell.deviceDetailState.deviceId === 'number');
const hasSelectedPublishPlan = computed(() => typeof shell.publishDetailState.planId === 'number');
const hasSelectedCollectorTask = computed(() => typeof shell.collectorDetailState.taskId === 'number');
const hasSelectedWorkflowDefinition = computed(() => typeof shell.aiContentFactoryDetailState.definitionId === 'number');
const hasSelectedVideoProject = computed(() => typeof shell.videoEditorDetailState.projectId === 'number');
const visibleDeviceLogs = computed(() => shell.deviceDetailState.logsCollapsed ? shell.deviceDetailState.logs.slice(0, 6) : shell.deviceDetailState.logs);

const hostMode = computed(() => {
  const host = shell.hostInfo;
  if (!host) {
    return '等待宿主信息';
  }
  const launchMode = mapRuntimeLaunchMode(host.runtimeLaunchMode);
  const runtimeStatus = mapRuntimeStatus(host.runtimeStatus).label;
  return `${launchMode} / ${runtimeStatus}`;
});

const runtimeEndpoint = computed(() => shell.hostInfo?.runtimeEndpoint || '等待连接');

function dispatchAccountAction(
  action: 'open-environment' | 'manage-cookies' | 'rebind-validate' | 'validate-login' | 'test-connection' | 'edit-account' | 'delete-account',
): void {
  const accountId = shell.accountDetailState.accountId;
  if (typeof accountId !== 'number') {
    return;
  }
  window.dispatchEvent(new CustomEvent('tkops:account-detail-action', { detail: { action, accountId } }));
}

function dispatchDeviceAction(
  action: 'open-environment' | 'adjust-binding' | 'open-logs' | 'inspect-device' | 'edit-device' | 'delete-device' | 'toggle-logs',
): void {
  const deviceId = shell.deviceDetailState.deviceId;
  if (typeof deviceId !== 'number') {
    return;
  }
  window.dispatchEvent(new CustomEvent('tkops:device-detail-action', { detail: { action, deviceId } }));
}

function dispatchPublishAction(action: 'start-plan' | 'delete-plan' | 'toggle-calendar'): void {
  const planId = shell.publishDetailState.planId;
  if (action !== 'toggle-calendar' && typeof planId !== 'number') {
    return;
  }
  window.dispatchEvent(new CustomEvent('tkops:scheduled-publish-detail-action', { detail: { action, planId } }));
}

function dispatchCollectorAction(action: 'start-task' | 'delete-task' | 'view-proxy-pool'): void {
  const taskId = shell.collectorDetailState.taskId;
  if (action !== 'view-proxy-pool' && typeof taskId !== 'number') {
    return;
  }
  window.dispatchEvent(new CustomEvent('tkops:data-collector-detail-action', { detail: { action, taskId } }));
}

function dispatchCreativeAction(action: 'save-plan' | 'compare-views' | 'goto-video-editor'): void {
  const projectId = shell.creativeDetailState.projectId;
  window.dispatchEvent(new CustomEvent('tkops:creative-workshop-detail-action', { detail: { action, projectId } }));
}

function dispatchAiContentFactoryAction(action: 'save-workflow' | 'run-batch' | 'run-workflow'): void {
  const definitionId = shell.aiContentFactoryDetailState.definitionId;
  window.dispatchEvent(new CustomEvent('tkops:ai-content-factory-detail-action', { detail: { action, definitionId } }));
}

function dispatchVideoEditorAction(
  action: 'export-final' | 'export-preview' | 'save-snapshot' | 'restore-snapshot' | 'create-subtitle' | 'switch-sequence',
): void {
  const projectId = shell.videoEditorDetailState.projectId;
  const sequenceId = shell.videoEditorDetailState.sequenceId;
  window.dispatchEvent(new CustomEvent('tkops:video-editor-detail-action', { detail: { action, projectId, sequenceId } }));
}

function deviceIssueLabel(tone: 'info' | 'success' | 'warning' | 'error'): string {
  if (tone === 'error') return '阻塞';
  if (tone === 'warning') return '待处理';
  if (tone === 'success') return '通过';
  return '提示';
}

function deviceLogTone(category: string): 'info' | 'success' | 'warning' | 'error' {
  const value = String(category || '').toLowerCase();
  if (value.includes('repair')) return 'success';
  if (value.includes('inspect')) return 'warning';
  if (value.includes('error') || value.includes('fail')) return 'error';
  return 'info';
}
</script>

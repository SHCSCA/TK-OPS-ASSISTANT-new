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
const isAccountRoute = computed(() => shell.currentRouteName === 'account');
const dashboardDetailKind = computed(() => shell.dashboardDetailState.kind);
const accountDetailKind = computed(() => shell.accountDetailState.kind);
const isActivityDetail = computed(() => shell.dashboardDetailState.kind === 'activity');
const isSystemDetail = computed(() => shell.dashboardDetailState.kind === 'system');
const isQuickActionDetail = computed(() => shell.dashboardDetailState.kind === 'quick-action');
const hasSelectedAccount = computed(() => typeof shell.accountDetailState.accountId === 'number');

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
</script>

<template>
  <aside class="detail-panel" :class="{ 'shell-hidden': !shell.detailPanelVisible }">
    <div class="detail-root">
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
          <div class="detail-item">
            <span class="subtle">Runtime</span>
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

const shell = useShellStore();

const hostMode = computed(() => {
  const host = shell.hostInfo;
  if (!host) {
    return '等待宿主信息';
  }
  return `${host.runtimeLaunchMode} / ${host.runtimeStatus}`;
});

const runtimeEndpoint = computed(() => shell.hostInfo?.runtimeEndpoint || '等待连接');
</script>


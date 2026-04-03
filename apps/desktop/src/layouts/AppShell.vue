<template>
  <div class="shell-viewport" :class="{ 'shell-viewport--overflow-x': shell.layoutOverflowXEnabled }">
    <div class="shell-canvas" :style="shellScaleVars">
      <div class="app-shell" :class="shellClasses">
        <TitleBar />
        <Sidebar />
        <PageHost />
        <DetailPanel />
        <StatusBar />

        <div class="ai-chat-overlay" :class="{ 'shell-hidden': !shell.assistantOpen }">
          <div class="ai-chat-panel">
            <div class="ai-chat-panel__header">
              <strong>AI 助手</strong>
              <div class="ai-chat-panel__header-actions">
                <button class="icon-button" type="button" @click="shell.closeAssistant">
                  <span class="shell-icon">关</span>
                </button>
              </div>
            </div>
            <div class="ai-chat-messages">
              <div
                v-for="item in shell.assistantMessages"
                :key="item.id"
                class="ai-chat-bubble"
                :class="item.role === 'user' ? 'ai-chat-bubble--user' : 'ai-chat-bubble--assistant'"
              >
                <div class="ai-chat-bubble__role">{{ item.role === 'user' ? '你' : '助手' }}</div>
                <div class="ai-chat-bubble__content">{{ item.content }}</div>
              </div>
              <div v-if="!shell.assistantMessages.length" class="notification-empty">
                你好，我可以结合当前页面给你建议，并触发壳层快捷动作。
              </div>
            </div>
            <div v-if="shell.assistantSuggestions.length" class="shell-assistant-actions">
              <button
                v-for="action in shell.assistantSuggestions"
                :key="action.id"
                type="button"
                class="secondary-button"
                @click="shell.runShellAction(action)"
              >
                {{ action.label }}
              </button>
            </div>
            <div class="ai-chat-input-row">
              <textarea
                v-model="shell.assistantInput"
                rows="2"
                placeholder="输入你的问题（Enter 发送，Shift+Enter 换行）"
                @keydown.enter.exact.prevent="shell.sendAssistantMessage"
              ></textarea>
              <button class="primary-button" type="button" :disabled="shell.assistantBusy" @click="shell.sendAssistantMessage">
                {{ shell.assistantBusy ? '处理中...' : '发送' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="shell.bootError" class="shell-boot-error">
          <strong>启动初始化异常</strong>
          <p>{{ shell.bootError }}</p>
          <button type="button" class="secondary-button" @click="shell.initializeShell">重试初始化</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';

import { router } from '../app/router';
import { useShellStore } from '../modules/shell/useShellStore';
import DetailPanel from './DetailPanel.vue';
import PageHost from './PageHost.vue';
import Sidebar from './Sidebar.vue';
import StatusBar from './StatusBar.vue';
import TitleBar from './TitleBar.vue';

const shell = useShellStore();

const shellClasses = computed(() => ({
  'sidebar-collapsed': shell.sidebarCollapsed,
  'detail-hidden': !shell.detailPanelVisible,
  [`layout-${shell.layoutMode}`]: true,
}));

const shellScaleVars = computed<Record<string, string>>(() => ({
  '--shell-scale': shell.shellScale.toFixed(4),
  '--shell-layout-width': `${shell.layoutViewportWidth}px`,
  '--shell-min-width': '960px',
}));

watch(
  () => router.currentRoute.value.fullPath,
  () => {
    shell.setRouteSummary(null);
    shell.markCurrentRouteVisited();
  },
);

onMounted(async () => {
  await shell.initializeShell();
});
</script>

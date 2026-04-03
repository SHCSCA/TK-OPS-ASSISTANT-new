<template>
  <header class="title-bar">
    <div class="title-bar__cluster">
      <button id="menuToggle" type="button" class="icon-button" aria-label="折叠菜单" @click="shell.toggleSidebar">
        <span class="shell-icon">三</span>
      </button>

      <div class="logo-mark">
        <span class="shell-icon shell-icon--strong">TK</span>
      </div>

      <div class="brand-stack">
        <strong>TK-OPS</strong>
        <p class="eyebrow">{{ shell.currentEyebrow }}</p>
      </div>

      <div class="search-bar shell-search-bar">
        <span class="shell-icon">搜</span>
        <input
          id="globalSearch"
          v-model="shell.searchQuery"
          type="text"
          placeholder="搜索页面、任务、账号、异常约束"
          @focus="shell.openSearchPanel"
          @input="shell.updateSearchResults"
          @keydown.down.prevent="shell.moveSearchSelection(1)"
          @keydown.up.prevent="shell.moveSearchSelection(-1)"
          @keydown.enter.prevent="shell.selectActiveSearchResult"
          @keydown.esc.prevent="shell.closeSearchPanel"
        />

        <div id="searchPanel" class="search-panel" :class="{ 'shell-hidden': !shell.searchPanelVisible }">
          <div class="search-panel__section">
            <div class="search-panel__title">搜索结果</div>
            <div class="search-panel__list">
              <button
                v-for="(item, index) in shell.searchResults"
                :key="item.id"
                type="button"
                class="search-result-item"
                :class="{ 'is-active': index === shell.searchActiveIndex }"
                @click="shell.navigateFromSearch(item)"
              >
                <strong>{{ item.title }}</strong>
                <span class="subtle">{{ item.description }}</span>
              </button>
              <div v-if="!shell.searchResults.length" class="notification-empty">没有匹配结果</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="title-bar__actions">
      <span v-if="shell.showResponsiveNote" class="responsive-note subtle">窗口过窄时会自动折叠更多功能，避免主内容被挤压。</span>

      <button v-if="shell.showInlineAiAction" id="aiChatToggle" type="button" class="icon-button" aria-label="AI 助手" @click="shell.toggleAssistant">
        <span class="shell-icon">智</span>
      </button>

      <button
        v-if="shell.showInlineDetailAction"
        id="detailToggle"
        type="button"
        class="icon-button"
        :class="{ 'is-active': shell.detailPanelVisible }"
        aria-label="切换右栏"
        @click="shell.toggleDetailPanel"
      >
        <span class="shell-icon">侧</span>
      </button>

      <button id="themeToggle" type="button" class="secondary-button" @click="shell.toggleThemeQuickly">
        {{ shell.quickThemeLabel }}
      </button>

      <button id="notificationToggle" type="button" class="icon-button" aria-label="通知" @click="shell.toggleNotifications">
        <span class="shell-icon">铃</span>
        <span v-if="shell.unreadNotificationCount > 0" class="notif-badge">{{ shell.unreadNotificationCount }}</span>
      </button>

      <div id="notificationPanel" class="notification-panel" :class="{ 'is-open': shell.notificationsOpen, 'shell-hidden': !shell.notificationsOpen }">
        <div class="notification-panel__header">
          <strong>通知中心</strong>
          <span class="subtle">{{ shell.notifications.length }} 条</span>
        </div>
        <div class="notification-panel__list">
          <div v-if="!shell.notifications.length" class="notification-empty">暂无通知</div>
          <template v-else>
            <button
              v-for="item in shell.notifications"
              :key="item.id"
              type="button"
              class="notification-item"
              :class="{ 'is-unread': item.read !== true }"
            >
              <span class="notification-item__dot" :class="item.tone"></span>
              <span class="notification-item__body">
                <strong>{{ item.title }}</strong>
                <span class="subtle">{{ item.body }}</span>
              </span>
            </button>
          </template>
        </div>
      </div>

      <button
        v-if="shell.showInlineStatusAction"
        id="statusSummaryToggle"
        type="button"
        class="icon-button"
        aria-label="运行状态"
        @click="shell.toggleStatusPanel"
      >
        <span class="shell-icon">况</span>
      </button>

      <button v-if="shell.showTopbarMore" id="topbarMoreToggle" type="button" class="icon-button" aria-label="更多操作" @click="shell.toggleTopbarOverflow">
        <span class="shell-icon">更</span>
      </button>

      <div id="topbarOverflowPanel" class="topbar-overflow-panel" :class="{ 'shell-hidden': !shell.topbarOverflowOpen }">
        <button
          v-for="item in shell.topbarOverflowActions"
          :key="item.id"
          type="button"
          class="topbar-overflow-panel__item"
          @click="shell.runTopbarOverflowAction(item.id)"
        >
          <span class="shell-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </button>
      </div>

      <div id="statusSummaryPanel" class="status-summary-panel" :class="{ 'shell-hidden': !shell.statusOpen }">
        <div class="notification-panel__header">
          <strong>运行状态</strong>
        </div>
        <div class="detail-list">
          <div class="detail-item">
            <span class="subtle">Runtime</span>
            <strong>{{ shell.runtimeChip.label }}</strong>
          </div>
          <div class="detail-item">
            <span class="subtle">主题</span>
            <strong>{{ shell.resolvedTheme }}</strong>
          </div>
          <div class="detail-item">
            <span class="subtle">通知</span>
            <strong>{{ shell.unreadNotificationCount }} 未读</strong>
          </div>
        </div>
      </div>

      <div class="account-cell">
        <div class="avatar">{{ shell.workspaceIdentity.initials }}</div>
        <div class="account-cell__text">
          <strong>{{ shell.workspaceIdentity.name }}</strong>
          <div class="subtle">{{ shell.workspaceIdentity.subtitle }}</div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue';

import { useShellStore } from '../modules/shell/useShellStore';

const shell = useShellStore();

function handleDocumentClick(event: MouseEvent): void {
  const target = event.target as HTMLElement | null;
  if (!target) {
    return;
  }
  if (!target.closest('.shell-search-bar')) {
    shell.closeSearchPanel();
  }
  if (!target.closest('#notificationToggle') && !target.closest('#notificationPanel')) {
    shell.notificationsOpen = false;
  }
  if (!target.closest('#statusSummaryToggle') && !target.closest('#statusSummaryPanel') && !target.closest('#topbarOverflowPanel')) {
    shell.statusOpen = false;
  }
  if (!target.closest('#topbarMoreToggle') && !target.closest('#topbarOverflowPanel')) {
    shell.topbarOverflowOpen = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick);
});
</script>

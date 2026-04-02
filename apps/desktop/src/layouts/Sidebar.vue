<template>
  <aside class="sidebar">
    <div class="sidebar__content">
      <section v-for="group in navGroups" :key="group.title" class="sidebar__section">
        <div class="sidebar__title">{{ group.title }}</div>
        <RouterLink
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          :class="['nav-link', currentPath === item.to ? 'is-active' : '']"
        >
          <span class="nav-link__label">{{ item.label }}</span>
        </RouterLink>
      </section>
    </div>
    <div class="sidebar__footer">
      <div class="eyebrow">当前阶段</div>
      <strong>新架构桌面宿主</strong>
      <p class="sidebar__footer-copy">
        默认入口已回到桌面壳，浏览器模式只保留为调试辅助。
      </p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

const route = useRoute();
const currentPath = computed(() => route.path);

const navGroups = [
  {
    title: '主要工作台',
    items: [
      { to: '/', label: '概览看板' },
      { to: '/accounts', label: '账号管理' },
      { to: '/tasks', label: '任务队列' },
      { to: '/scheduler', label: '任务调度' },
    ],
  },
  {
    title: '内容与 AI',
    items: [
      { to: '/ai-copywriter', label: 'AI 文案生成' },
      { to: '/providers', label: 'AI 提供商' },
    ],
  },
  {
    title: '系统与工具',
    items: [
      { to: '/setup-wizard', label: '初始化向导' },
      { to: '/settings', label: '系统设置' },
    ],
  },
];
</script>

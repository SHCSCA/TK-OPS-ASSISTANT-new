<template>
  <aside class="sidebar">
    <div class="sidebar__content">
      <section v-for="group in navGroups" :key="group.title" class="sidebar__section">
        <div class="sidebar__title">{{ group.title }}</div>
        <RouterLink
          v-for="item in group.items"
          :key="item.name"
          :to="{ name: item.name }"
          :class="['nav-link', currentRouteName === item.name ? 'is-active' : '']"
        >
          <span class="nav-link__glyph">{{ item.label.slice(0, 1) }}</span>
          <span class="nav-link__label">{{ item.label }}</span>
          <span v-if="item.migrationStatus === 'placeholder'" class="nav-link__badge">待迁移</span>
        </RouterLink>
      </section>
    </div>
    <div class="sidebar__footer">
      <div class="eyebrow">当前阶段</div>
      <strong>新桌面壳全局能力补齐</strong>
      <p class="sidebar__footer-copy">
        完成壳层能力后继续按菜单顺序逐页迁移功能，保证结构稳定、进度可追踪。
      </p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';

import { shellNavGroups, shellRouteManifest } from '../app/router/routeManifest';
import { useShellStore } from '../modules/shell/useShellStore';

const shell = useShellStore();

const currentRouteName = computed(() => shell.currentRouteName);

const navGroups = computed(() =>
  shellNavGroups
    .slice()
    .sort((left, right) => left.order - right.order)
    .map((group) => ({
      title: group.title,
      items: shellRouteManifest
        .filter((item) => item.navGroup === group.key)
        .slice()
        .sort((left, right) => left.navOrder - right.navOrder)
        .map((item) => ({
          name: item.name,
          label: item.title,
          migrationStatus: item.migrationStatus,
        })),
    }))
    .filter((group) => group.items.length > 0),
);
</script>

<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
        <p class="resource-subtitle">
          该页面已进入新桌面壳菜单和路由骨架，接下来会按“页面结构、真实数据、交互、样式、测试”顺序逐步迁移。
        </p>
      </div>
    </div>

    <div class="resource-summary-grid resource-summary-grid-triple">
      <article class="metric-card">
        <p class="eyebrow">迁移状态</p>
        <strong>待迁移</strong>
        <span>已完成菜单注册与路由占位</span>
      </article>
      <article class="metric-card">
        <p class="eyebrow">旧页面键</p>
        <strong>{{ legacyRouteKey }}</strong>
        <span>用于和旧壳功能逐项对照</span>
      </article>
      <article class="metric-card">
        <p class="eyebrow">当前阶段</p>
        <strong>菜单先行</strong>
        <span>下一步进入该页真实迁移</span>
      </article>
    </div>

    <section class="dashboard-section">
      <div class="dashboard-section-title">
        <h3>页面摘要</h3>
        <span>{{ summary }}</span>
      </div>

      <article class="resource-card">
        <p class="resource-card-meta">
          当前占位的目标不是做假界面，而是先把菜单、路由、标题和页面说明稳定下来，保证后续逐页迁移时不会再丢页面。
        </p>
        <p class="resource-card-meta">
          迁移到本页时，会补齐真实数据接口、主交互、异常提示、空态和回归测试。
        </p>
      </article>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const title = computed(() => String(route.meta.title || '迁移占位页'));
const eyebrow = computed(() => String(route.meta.eyebrow || '迁移中'));
const summary = computed(() => String(route.meta.summary || '当前页面正在迁移。'));
const legacyRouteKey = computed(() => String(route.meta.legacyRouteKey || 'unknown'));
</script>

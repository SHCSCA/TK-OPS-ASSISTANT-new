<template>
  <div class="stat-grid">
    <article class="stat-card">
      <div>
        <div class="subtle">素材库存</div>
        <div class="stat-card__value">{{ stats.total }}</div>
        <div class="stat-card__delta" style="color: var(--status-success)">
          <span>最近上传 {{ recentCount }}</span>
          <span class="subtle">真实素材库存总量</span>
        </div>
      </div>
    </article>
    <article class="stat-card">
      <div>
        <div class="subtle">未绑定账号</div>
        <div class="stat-card__value">{{ unboundCount }}</div>
        <div class="stat-card__delta" style="color: var(--status-warning)">
          <span>需要补充归属</span>
          <span class="subtle">未关联账号素材</span>
        </div>
      </div>
    </article>
    <article class="stat-card">
      <div>
        <div class="subtle">标签完善率</div>
        <div class="stat-card__value">{{ taggedRate }}%</div>
        <div class="stat-card__delta" style="color: var(--brand-primary)">
          <span>已打标签 {{ taggedCount }}</span>
          <span class="subtle">标签可检索覆盖率</span>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AssetItem, AssetStats } from '../assetCenter.types';
import { RECENT_UPLOAD_MS } from '../assetCenter.constants';

const props = defineProps<{
  assets: AssetItem[];
  stats: AssetStats;
}>();

const total = computed(() => props.stats.total || props.assets.length);

const unboundCount = computed(() =>
  props.assets.filter(a => !a.accountId).length
);

const taggedCount = computed(() =>
  props.assets.filter(a => a.tags && a.tags.trim().length > 0).length
);

const taggedRate = computed(() =>
  total.value ? Math.round(taggedCount.value / total.value * 100) : 0
);

const recentCount = computed(() => {
  const now = Date.now();
  return props.assets.filter(a => {
    if (!a.createdAt) return false;
    return now - new Date(a.createdAt).getTime() <= RECENT_UPLOAD_MS;
  }).length;
});
</script>

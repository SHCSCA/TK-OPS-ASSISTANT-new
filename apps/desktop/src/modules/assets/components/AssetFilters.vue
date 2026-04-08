<template>
  <div class="asset-filter-row">
    <span
      v-for="filter in filters"
      :key="filter.key"
      class="asset-filter-item"
      :class="{ 'is-active': activeCategory === filter.key }"
      @click="$emit('select', filter.key)"
    >
      {{ filter.label }} {{ filter.count }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AssetCategory } from '../assetCenter.types';

const props = defineProps<{
  activeCategory: AssetCategory;
  typeCounts: Record<string, number>;
  total: number;
}>();

defineEmits<{
  select: [category: AssetCategory];
}>();

const FILTERS = [
  { key: 'all', label: '全部' },
  { key: 'video', label: '视频' },
  { key: 'image', label: '图片' },
  { key: 'text', label: '字幕' },
  { key: 'audio', label: '音频' },
  { key: 'template', label: '模板' },
] as const;

const filters = computed(() =>
  FILTERS.map(f => ({
    ...f,
    count: f.key === 'all' ? props.total : (props.typeCounts[f.key] || 0),
  }))
);
</script>

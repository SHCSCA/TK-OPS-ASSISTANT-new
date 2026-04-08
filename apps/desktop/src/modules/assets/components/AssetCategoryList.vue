<template>
  <div class="asset-category-list">
    <button
      v-for="cat in categories"
      :key="cat.key"
      class="asset-category-item"
      :class="{ 'is-active': activeCategory === cat.key }"
      @click="$emit('select', cat.key)"
    >
      <strong>{{ cat.label }}</strong>
      <span>{{ cat.count }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AssetCategory } from '../assetCenter.types';
import { CATEGORY_LABELS, CATEGORY_ORDER } from '../assetCenter.constants';

const props = defineProps<{
  activeCategory: AssetCategory;
  typeCounts: Record<string, number>;
  total: number;
}>();

defineEmits<{
  select: [category: AssetCategory];
}>();

const categories = computed(() =>
  CATEGORY_ORDER.map(key => ({
    key,
    label: CATEGORY_LABELS[key] || key,
    count: key === 'all' ? props.total : (props.typeCounts[key] || 0),
  }))
);
</script>

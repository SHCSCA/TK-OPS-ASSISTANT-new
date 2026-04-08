<template>
  <section class="panel">
    <div class="panel__header">
      <div>
        <strong>{{ asset?.filename || '暂无素材' }}</strong>
        <div class="subtle">{{ asset?.filePath || '当前筛选条件下没有可展示素材。' }}</div>
      </div>
      <span v-if="asset" class="status-chip info">
        {{ typeLabel(asset?.assetType) }} / {{ humanFileSize(asset?.fileSize || 0) }}
      </span>
    </div>
    <div class="detail-list">
      <div class="detail-item">
        <span class="subtle">素材类型</span>
        <strong>{{ asset ? typeLabel(asset.assetType) : '-' }}</strong>
      </div>
      <div class="detail-item">
        <span class="subtle">素材标签</span>
        <strong>{{ asset?.tags ? tagList(asset.tags).join(' / ') : '-' }}</strong>
      </div>
      <div class="detail-item">
        <span class="subtle">入库时间</span>
        <strong>{{ formatDate(asset?.createdAt) }}</strong>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { AssetItem } from '../assetCenter.types';
import { TYPE_LABELS } from '../assetCenter.constants';

const props = defineProps<{
  asset: AssetItem | null;
}>();

function typeLabel(type: string): string {
  return TYPE_LABELS[type] || type;
}

function tagList(tags: string): string[] {
  return tags.split(/[，,、/\s]+/).filter(Boolean);
}

function humanFileSize(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string | null | undefined): string {
  if (!value) return '-';
  const date = new Date(value);
  if (isNaN(date.getTime())) return '-';
  const yyyy = String(date.getFullYear());
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}
</script>

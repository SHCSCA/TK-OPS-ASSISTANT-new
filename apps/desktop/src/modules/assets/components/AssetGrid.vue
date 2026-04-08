<template>
  <div class="asset-source-grid">
    <template v-if="assets.length">
      <article
        v-for="asset in displayedAssets"
        :key="asset.id"
        class="source-thumb"
        :class="{ 'is-selected': selectedId === asset.id }"
        @click="$emit('select', asset.id)"
      >
        <div class="source-thumb__preview" :class="previewClass(asset.assetType)">
          <img
            v-if="asset.assetType === 'image'"
            class="source-thumb__media"
            :src="fileUrl(asset.filePath)"
            :alt="asset.filename"
            loading="lazy"
          />
          <div v-else-if="asset.assetType === 'video'" class="source-thumb__media source-thumb__media--video-placeholder">
            <span>视频</span>
          </div>
          <span class="source-thumb__preview-label">{{ previewLabel(asset.assetType) }}</span>
          <span v-if="asset.assetType === 'video'" class="source-thumb__dur">
            {{ humanFileSize(asset.fileSize) }}
          </span>
        </div>
        <div class="source-thumb__name">{{ asset.filename }}</div>
        <div class="subtle">{{ asset.filePath || '未记录路径' }}</div>
        <div class="source-thumb__tag">
          <span class="pill" :class="asset.assetType === 'video' ? 'success' : 'info'">
            {{ typeLabel(asset.assetType) }}
          </span>
          <span v-if="asset.tags" class="pill info">{{ firstTag(asset.tags) }}</span>
          <span v-else class="pill warning">未打标签</span>
        </div>
      </article>
    </template>
    <div v-else class="empty-state">
      <p>没有匹配素材</p>
      <p class="subtle">请调整分类、标签页或搜索关键词。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { AssetItem, AssetType } from '../assetCenter.types';
import { TYPE_LABELS } from '../assetCenter.constants';

const props = defineProps<{
  assets: AssetItem[];
  selectedId: number | null;
}>();

defineEmits<{
  select: [id: number];
}>();

const MAX_DISPLAY = 24;

const displayedAssets = computed(() => props.assets.slice(0, MAX_DISPLAY));

function typeLabel(type: string): string {
  return TYPE_LABELS[type] || type;
}

function previewClass(type: string): string {
  if (type === 'video') return 'source-thumb__preview--video';
  if (type === 'audio') return 'source-thumb__preview--audio';
  if (type === 'text') return 'source-thumb__preview--subtitle';
  return 'source-thumb__preview--image';
}

function previewLabel(type: string): string {
  if (type === 'audio') return '♫';
  if (type === 'video') return '视频';
  if (type === 'text') return '文稿';
  if (type === 'template') return '模板';
  return '图片';
}

function fileUrl(filePath: string): string {
  if (!filePath) return '';
  if (/^https?:\/\//i.test(filePath) || /^file:\/\//i.test(filePath)) return filePath;
  return `file:///${filePath.replace(/\\/g, '/')}`;
}

function humanFileSize(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function firstTag(tags: string): string {
  if (!tags) return '';
  const list = tags.split(/[，,、/\s]+/);
  return list[0] || '';
}
</script>

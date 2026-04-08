<template>
  <section class="resource-page">
    <div class="resource-header">
      <div>
        <p class="eyebrow">素材资产库</p>
        <h2>素材中心</h2>
        <p class="resource-subtitle">
          统一查看素材库存、素材分类、授权状态和复用建议，主区直接展示素材。
        </p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <AssetStats :assets="assets" :stats="stats" />

    <div class="asset-center-shell">
      <!-- 左侧分类列表 -->
      <aside class="asset-category-column">
        <section class="panel">
          <div class="panel__header">
            <div>
              <strong>素材分类</strong>
              <div class="subtle">先按类型和场景找素材</div>
            </div>
          </div>
          <AssetCategoryList
            :active-category="filterState.category"
            :type-counts="typeCounts"
            :total="stats.total || assets.length"
            @select="setCategory"
          />
        </section>
      </aside>

      <!-- 主内容区 -->
      <main class="asset-main-content">
        <!-- 筛选栏 -->
        <div class="asset-filter-row-wrapper">
          <AssetFilters
            :active-category="filterState.category"
            :type-counts="typeCounts"
            :total="stats.total || assets.length"
            @select="setCategory"
          />
        </div>

        <!-- 搜索框 -->
        <div class="asset-search-field">
          <input
            type="text"
            :placeholder="SEARCH_PLACEHOLDER"
            :value="filterState.keyword"
            @input="onKeywordInput"
          />
        </div>

        <!-- 素材网格 -->
        <AssetGrid
          :assets="filteredAssets"
          :selected-id="filterState.selectedId"
          @select="onSelectAsset"
        />
      </main>

      <!-- 右侧详情面板 -->
      <aside class="asset-detail-column">
        <AssetDetail :asset="selectedAsset" />
      </aside>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <span>加载中...</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-toast">
      {{ errorMessage }}
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useAssetCenterViewModel } from '../../modules/assets/useAssetCenterViewModel';
import AssetStats from '../../modules/assets/components/AssetStats.vue';
import AssetCategoryList from '../../modules/assets/components/AssetCategoryList.vue';
import AssetFilters from '../../modules/assets/components/AssetFilters.vue';
import AssetGrid from '../../modules/assets/components/AssetGrid.vue';
import AssetDetail from '../../modules/assets/components/AssetDetail.vue';
import { SEARCH_PLACEHOLDER } from '../../modules/assets/assetCenter.constants';

const {
  assets,
  stats,
  filterState,
  isLoading,
  errorMessage,
  filteredAssets,
  typeCounts,
  selectedAsset,
  loadAssets,
  setCategory,
  setKeyword,
  selectAsset,
} = useAssetCenterViewModel();

onMounted(() => {
  loadAssets();
});

function onKeywordInput(event: Event) {
  const target = event.target as HTMLInputElement;
  setKeyword(target.value);
}

function onSelectAsset(id: number) {
  selectAsset(id);
}
</script>

<style scoped>
.asset-center-shell {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  gap: 16px;
  margin-top: 16px;
}

.asset-main-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.asset-filter-row-wrapper {
  overflow-x: auto;
}

.asset-search-field input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--surface-primary);
  color: var(--text-primary);
}

.asset-search-field input::placeholder {
  color: var(--text-tertiary);
}

.loading-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: white;
}

.error-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  background: var(--status-error);
  color: white;
  border-radius: var(--radius-md);
}
</style>

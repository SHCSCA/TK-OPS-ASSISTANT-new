/**
 * 素材中心状态管理
 * @description 素材筛选状态、选中状态等的持久化管理
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  AssetCategory,
  AssetTab,
  PackKey,
  AssetItem,
  AssetStats,
} from './assetCenter.types';

// 默认筛选状态
const DEFAULT_FILTER_STATE = {
  category: 'all' as AssetCategory,
  tab: 'all' as AssetTab,
  keyword: '',
  groupTag: '',
  packKey: '' as PackKey,
  selectedId: null as number | null,
};

/**
 * 素材中心 Store
 */
export const useAssetCenterStore = defineStore('assetCenter', () => {
  // 素材列表
  const assets = ref<AssetItem[]>([]);

  // 统计数据
  const stats = ref<AssetStats>({
    total: 0,
    byType: {
      image: 0,
      video: 0,
      audio: 0,
      text: 0,
      template: 0,
    },
  });

  // 筛选状态
  const filterState = ref({ ...DEFAULT_FILTER_STATE });

  // 加载状态
  const isLoading = ref(false);

  // 错误信息
  const errorMessage = ref<string | null>(null);

  // 计算属性：当前选中的素材
  const selectedAsset = computed(() => {
    if (!filterState.value.selectedId) return null;
    return assets.value.find(a => a.id === filterState.value.selectedId) || null;
  });

  // 计算属性：是否加载完成
  const isLoaded = computed(() => !isLoading.value && assets.value.length >= 0);

  /**
   * 设置素材列表
   */
  function setAssets(newAssets: AssetItem[]) {
    assets.value = newAssets;
  }

  /**
   * 设置统计数据
   */
  function setStats(newStats: AssetStats) {
    stats.value = newStats;
  }

  /**
   * 设置分类筛选
   */
  function setCategory(category: AssetCategory) {
    filterState.value.category = category;
    // 切换分类时清空推荐包筛选
    filterState.value.packKey = '';
  }

  /**
   * 设置Tab筛选
   */
  function setTab(tab: AssetTab) {
    filterState.value.tab = tab;
  }

  /**
   * 设置搜索关键词
   */
  function setKeyword(keyword: string) {
    filterState.value.keyword = keyword;
  }

  /**
   * 设置标签分组
   */
  function setGroupTag(groupTag: string) {
    filterState.value.groupTag = groupTag;
  }

  /**
   * 设置推荐包筛选
   */
  function setPackKey(packKey: PackKey) {
    filterState.value.packKey = packKey;
  }

  /**
   * 设置选中项
   */
  function setSelectedId(id: number | null) {
    filterState.value.selectedId = id;
  }

  /**
   * 设置加载状态
   */
  function setLoading(loading: boolean) {
    isLoading.value = loading;
  }

  /**
   * 设置错误信息
   */
  function setError(error: string | null) {
    errorMessage.value = error;
  }

  /**
   * 重置筛选状态
   */
  function resetFilters() {
    filterState.value = { ...DEFAULT_FILTER_STATE };
  }

  /**
   * 从持久化状态恢复
   */
  function restoreState(savedState: Partial<typeof DEFAULT_FILTER_STATE>) {
    filterState.value = {
      ...DEFAULT_FILTER_STATE,
      ...savedState,
    };
  }

  /**
   * 获取持久化状态（用于保存到路由状态）
   */
  function getPersistState() {
    return {
      category: filterState.value.category,
      tab: filterState.value.tab,
      keyword: filterState.value.keyword,
      groupTag: filterState.value.groupTag,
      packKey: filterState.value.packKey,
      selectedId: filterState.value.selectedId,
    };
  }

  return {
    // 状态
    assets,
    stats,
    filterState,
    isLoading,
    errorMessage,

    // 计算属性
    selectedAsset,
    isLoaded,

    // 方法
    setAssets,
    setStats,
    setCategory,
    setTab,
    setKeyword,
    setGroupTag,
    setPackKey,
    setSelectedId,
    setLoading,
    setError,
    resetFilters,
    restoreState,
    getPersistState,
  };
});

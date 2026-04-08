/**
 * 素材中心 ViewModel
 * @description 素材中心页面的交互逻辑编排
 */

import { computed } from 'vue';
import { runtimeApi } from '../runtime/runtimeApi';
import { useAssetCenterStore } from './assetCenter.store';
import type {
  AssetItem,
  AssetCategory,
  AssetTab,
  PackKey,
  AssetType,
} from './assetCenter.types';
import {
  LARGE_FILE_THRESHOLD,
  RECENT_UPLOAD_MS,
  TYPE_LABELS,
} from './assetCenter.constants';

/**
 * 素材中心 ViewModel Composable
 */
export function useAssetCenterViewModel() {
  const store = useAssetCenterStore();

  // ========== 数据加载 ==========

  /**
   * 加载素材数据
   */
  async function loadAssets() {
    store.setLoading(true);
    store.setError(null);

    try {
      const [assetsResponse, statsResponse] = await Promise.all([
        runtimeApi.listAssets().catch(() => ({ items: [], total: 0 })),
        runtimeApi.getAssetStats().catch(() => ({
          total: 0,
          byType: { image: 0, video: 0, audio: 0, text: 0, template: 0 },
        })),
      ]);

      store.setAssets(assetsResponse.items || []);
      store.setStats(statsResponse);
    } catch (error) {
      store.setError(error instanceof Error ? error.message : '加载失败');
    } finally {
      store.setLoading(false);
    }
  }

  /**
   * 刷新数据
   */
  async function refresh() {
    await loadAssets();
  }

  // ========== 筛选逻辑 ==========

  /**
   * 判断素材是否匹配Tab筛选
   */
  function matchTab(asset: AssetItem, tab: AssetTab): boolean {
    if (tab === 'all') return true;
    if (tab === 'recent') return isRecentUpload(asset);
    if (tab === 'review') return isNeedsReview(asset);
    if (tab === 'tagged') return hasTags(asset);
    return true;
  }

  /**
   * 判断素材是否最近上传（7天内）
   */
  function isRecentUpload(asset: AssetItem): boolean {
    if (!asset.createdAt) return false;
    const createdDate = new Date(asset.createdAt).getTime();
    return Date.now() - createdDate <= RECENT_UPLOAD_MS;
  }

  /**
   * 判断素材是否需要整理
   */
  function isNeedsReview(asset: AssetItem): boolean {
    if (asset.assetType === 'text' || asset.assetType === 'template') return true;
    const tags = parseTags(asset.tags);
    return tags.some(tag => /待审|待审核|需授权|未授权|review|pending/i.test(tag));
  }

  /**
   * 判断素材是否有标签
   */
  function hasTags(asset: AssetItem): boolean {
    return parseTags(asset.tags).length > 0;
  }

  /**
   * 解析标签列表
   */
  function parseTags(tags: string | null): string[] {
    if (!tags) return [];
    return tags.split(/[，,、/\s]+/).map(t => t.trim()).filter(Boolean);
  }

  /**
   * 判断素材是否匹配关键词
   */
  function matchKeyword(asset: AssetItem, keyword: string): boolean {
    if (!keyword) return true;
    const lowerKeyword = keyword.toLowerCase();
    const searchText = [
      asset.filename,
      asset.filePath,
      TYPE_LABELS[asset.assetType] || asset.assetType,
      asset.tags || '',
    ].join(' ').toLowerCase();
    return searchText.includes(lowerKeyword);
  }

  /**
   * 判断素材是否匹配分类
   */
  function matchCategory(asset: AssetItem, category: AssetCategory): boolean {
    if (category === 'all') return true;
    return asset.assetType === category;
  }

  /**
   * 判断素材是否匹配标签分组
   */
  function matchGroupTag(asset: AssetItem, groupTag: string): boolean {
    if (!groupTag) return true;
    const tags = parseTags(asset.tags);
    return tags.includes(groupTag);
  }

  /**
   * 判断素材是否匹配推荐包
   */
  function matchPack(asset: AssetItem, packKey: PackKey): boolean {
    if (!packKey) return true;
    if (packKey === 'recent') return isRecentUpload(asset);
    if (packKey === 'large') return asset.fileSize >= LARGE_FILE_THRESHOLD;
    if (packKey === 'unbound') return !asset.accountId;
    if (packKey === 'tagged') return hasTags(asset);
    return true;
  }

  /**
   * 获取过滤后的素材列表
   */
  const filteredAssets = computed(() => {
    const { category, tab, keyword, groupTag, packKey } = store.filterState;
    return store.assets.filter(asset =>
      matchCategory(asset, category) &&
      matchTab(asset, tab) &&
      matchKeyword(asset, keyword) &&
      matchGroupTag(asset, groupTag) &&
      matchPack(asset, packKey)
    );
  });

  /**
   * 按类型统计素材数量
   */
  const typeCounts = computed(() => {
    const counts: Record<string, number> = {
      image: 0,
      video: 0,
      audio: 0,
      text: 0,
      template: 0,
    };
    store.assets.forEach(asset => {
      counts[asset.assetType] = (counts[asset.assetType] || 0) + 1;
    });
    // 优先使用后端统计
    Object.keys(counts).forEach(key => {
      const byType = store.stats.byType as Record<string, number>;
      if (byType?.[key] > 0) {
        counts[key] = byType[key];
      }
    });
    return counts;
  });

  // ========== 操作 ==========

  /**
   * 选中素材
   */
  function selectAsset(id: number | null) {
    store.setSelectedId(id);
  }

  /**
   * 删除素材
   */
  async function deleteAsset(id: number): Promise<boolean> {
    try {
      await runtimeApi.deleteAsset(id);
      await refresh();
      return true;
    } catch (error) {
      store.setError(error instanceof Error ? error.message : '删除失败');
      return false;
    }
  }

  /**
   * 更新素材
   */
  async function updateAsset(id: number, payload: any): Promise<boolean> {
    try {
      await runtimeApi.updateAsset(id, payload);
      await refresh();
      return true;
    } catch (error) {
      store.setError(error instanceof Error ? error.message : '更新失败');
      return false;
    }
  }

  /**
   * 创建素材
   */
  async function createAsset(payload: any): Promise<boolean> {
    try {
      await runtimeApi.createAsset(payload);
      await refresh();
      return true;
    } catch (error) {
      store.setError(error instanceof Error ? error.message : '创建失败');
      return false;
    }
  }

  // ========== 导出 ==========

  return {
    // 状态
    assets: computed(() => store.assets),
    stats: computed(() => store.stats),
    filterState: computed(() => store.filterState),
    isLoading: computed(() => store.isLoading),
    errorMessage: computed(() => store.errorMessage),
    selectedAsset: computed(() => store.selectedAsset),
    filteredAssets,
    typeCounts,

    // 方法
    loadAssets,
    refresh,
    setCategory: (c: AssetCategory) => store.setCategory(c),
    setTab: (t: AssetTab) => store.setTab(t),
    setKeyword: (k: string) => store.setKeyword(k),
    setGroupTag: (g: string) => store.setGroupTag(g),
    setPackKey: (p: PackKey) => store.setPackKey(p),
    selectAsset,
    deleteAsset,
    updateAsset,
    createAsset,
    parseTags,
  };
}

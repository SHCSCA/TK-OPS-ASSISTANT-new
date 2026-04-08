/**
 * 素材中心类型定义
 * @description 素材管理相关的数据类型和接口定义
 */

// 素材类型枚举
export const ASSET_TYPE_LABELS: Record<string, string> = {
  image: '图片',
  video: '视频',
  audio: '音频',
  text: '字幕',
  template: '模板',
};

// 素材分类标签
export const CATEGORY_LABELS: Record<string, string> = {
  all: '全部素材',
  video: '短视频口播',
  image: '封面图片',
  audio: '音频 / 配乐',
  text: '字幕 / 文案',
  template: '模板 / 工程',
};

/**
 * 素材项
 */
export interface AssetItem {
  id: number;
  filename: string;
  assetType: AssetType;
  filePath: string;
  fileSize: number;
  tags: string | null;
  accountId: number | null;
  createdAt: string | null;
  updatedAt: string | null;
}

/** 素材类型 */
export type AssetType = 'image' | 'video' | 'audio' | 'text' | 'template';

/**
 * 素材列表查询参数
 */
export interface AssetListQuery {
  assetType?: AssetType | null;
  query?: string | null;
}

/**
 * 素材列表响应
 */
export interface AssetListResponse {
  items: AssetItem[];
  total: number;
}

/**
 * 素材统计数据
 */
export interface AssetStats {
  total: number;
  byType: Record<AssetType, number>;
}

/**
 * 创建素材请求
 */
export interface AssetCreatePayload {
  filename: string;
  assetType: AssetType;
  filePath: string;
  tags?: string | null;
  accountId?: number | null;
}

/**
 * 更新素材请求
 */
export interface AssetUpdatePayload {
  filename?: string | null;
  assetType?: AssetType | null;
  filePath?: string | null;
  tags?: string | null;
  accountId?: number | null;
}

/**
 * 素材筛选状态
 */
export interface AssetFilterState {
  category: AssetCategory;     // 分类筛选
  tab: AssetTab;              // Tab筛选
  keyword: string;           // 搜索关键词
  groupTag: string;           // 标签分组
  packKey: PackKey;          // 推荐包
  selectedId: number | null; // 选中项
}

/** 分类类型 */
export type AssetCategory = 'all' | AssetType;

/** Tab类型 */
export type AssetTab = 'all' | 'recent' | 'review' | 'tagged';

/** 推荐包类型 */
export type PackKey = '' | 'recent' | 'large' | 'unbound' | 'tagged';

/**
 * 素材视图模型（前端使用）
 */
export interface AssetViewModel {
  id: string;
  filename: string;
  assetType: AssetType;
  filePath: string;
  posterPath: string;
  fileSize: number;
  tags: string;
  tagList: string[];
  createdAt: string;
  accountId: string;
}

/**
 * 素材卡片标签
 */
export interface AssetTag {
  text: string;
  tone: 'success' | 'warning' | 'info' | 'error';
}

/**
 * 素材预览类型
 */
export type AssetPreviewType = 'image' | 'video' | 'audio' | 'text' | 'template';

/**
 * 素材统计卡片数据
 */
export interface AssetStatCard {
  label: string;
  value: string | number;
  delta?: string;
  note?: string;
  color?: string;
}

/**
 * 分类文件夹卡片
 */
export interface CategoryFolderCard {
  key: string;
  title: string;
  desc: string;
  tone: 'success' | 'warning' | 'info' | 'error';
}

/**
 * 推荐包卡片
 */
export interface PackRecommendationCard {
  key: PackKey;
  title: string;
  desc: string;
  count: number;
  tone: 'success' | 'warning' | 'info' | 'error';
}

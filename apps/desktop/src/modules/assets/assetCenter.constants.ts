/**
 * 素材中心常量定义
 * @description 素材类型、分类、Tab等常量映射
 */

/** 素材类型标签映射 */
export const TYPE_LABELS: Record<string, string> = {
  image: '图片',
  video: '视频',
  audio: '音频',
  text: '字幕',
  template: '模板',
};

/** 分类标签映射 */
export const CATEGORY_LABELS: Record<string, string> = {
  all: '全部素材',
  video: '短视频口播',
  image: '封面图片',
  audio: '音频 / 配乐',
  text: '字幕 / 文案',
  template: '模板 / 工程',
};

/** 分类顺序 */
export const CATEGORY_ORDER = ['all', 'video', 'image', 'audio', 'text', 'template'] as const;

/** Tab筛选配置 */
export const TAB_CONFIG = [
  { key: 'all', label: '全部素材' },
  { key: 'recent', label: '最近上传' },
  { key: 'review', label: '待整理' },
  { key: 'tagged', label: '已打标签' },
] as const;

/** 推荐包配置 */
export const PACK_CONFIG = [
  { key: 'recent', title: '最近上传素材包', desc: '近 7 天上传素材，便于快速回看新资源。', tone: 'info' as const },
  { key: 'large', title: '大文件素材包', desc: '文件 >= 5MB，建议优先做压缩与转码。', tone: 'warning' as const },
  { key: 'unbound', title: '待关联账号素材', desc: '未绑定账号素材，避免后续链路无法追溯。', tone: 'error' as const },
  { key: 'tagged', title: '已打标签素材', desc: '标签齐全的素材更适合批量检索复用。', tone: 'success' as const },
];

/** 文件大小阈值（字节） */
export const LARGE_FILE_THRESHOLD = 5 * 1024 * 1024; // 5MB

/** 最近上传时间阈值（毫秒） */
export const RECENT_UPLOAD_DAYS = 7;
export const RECENT_UPLOAD_MS = RECENT_UPLOAD_DAYS * 24 * 60 * 60 * 1000;

/** 搜索占位符 */
export const SEARCH_PLACEHOLDER = '输入文件名 / 标签 / 路径关键词';

/** 空状态提示 */
export const EMPTY_STATE = {
  title: '没有匹配素材',
  subtitle: '请调整分类、标签页或搜索关键词。',
  loadingFailed: '素材加载失败，请稍后重试，或检查后端连接状态。',
  noSelection: '请先在左侧选择一个素材。',
};

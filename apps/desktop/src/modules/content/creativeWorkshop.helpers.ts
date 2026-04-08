import type { AssetItem } from '../assets/assetCenter.types';
import { formatDateTime } from '../runtime/format';
import type {
  AccountItem,
  ActivityLogItem,
  ExperimentProjectItem,
  ExperimentViewItem,
  TaskItem,
} from '../runtime/types';
import type {
  CreativeAdviceItem,
  CreativeCompareRow,
  CreativeDetailViewModel,
  CreativeFocusCard,
  CreativeRailKey,
  CreativeRailTool,
  CreativeSideCard,
  CreativeStatusTone,
  CreativeStripCard,
  CreativeSummaryChip,
} from './creativeWorkshop.types';

const RAIL_TOOL_MAP: Record<CreativeRailKey, CreativeRailTool> = {
  theme: { key: 'theme', icon: '主题', label: '主题' },
  shot: { key: 'shot', icon: '镜头', label: '镜头' },
  voice: { key: 'voice', icon: '口播', label: '口播' },
  export: { key: 'export', icon: '导出', label: '导出' },
};

function normalizeStatus(value: string | null | undefined): string {
  return String(value || '').trim().toLowerCase();
}

function taskStatusTone(status: string | null | undefined): CreativeStatusTone {
  const value = normalizeStatus(status);
  if (value === 'completed') return 'success';
  if (value === 'failed') return 'error';
  if (value === 'running') return 'info';
  return 'warning';
}

function taskStatusLabel(status: string | null | undefined): string {
  const value = normalizeStatus(status);
  if (value === 'completed') return '已完成';
  if (value === 'failed') return '失败';
  if (value === 'running') return '运行中';
  if (value === 'paused') return '已暂停';
  return '待执行';
}

export function projectStatusTone(status: string | null | undefined): CreativeStatusTone {
  const value = normalizeStatus(status);
  if (['done', 'completed', 'published', 'success'].includes(value)) return 'success';
  if (['failed', 'blocked', 'archived'].includes(value)) return 'error';
  if (['running', 'active', 'testing'].includes(value)) return 'info';
  return 'warning';
}

export function projectStatusLabel(status: string | null | undefined): string {
  const value = normalizeStatus(status);
  if (['done', 'completed', 'published', 'success'].includes(value)) return '已收口';
  if (['failed', 'blocked', 'archived'].includes(value)) return '已阻塞';
  if (['running', 'active', 'testing'].includes(value)) return '实验中';
  return '待评估';
}

export function buildCreativeRailTools(): CreativeRailTool[] {
  return Object.values(RAIL_TOOL_MAP);
}

export function buildCreativeSummaryChips(
  projects: ExperimentProjectItem[],
  tasks: TaskItem[],
  assets: AssetItem[],
  accounts: AccountItem[],
): CreativeSummaryChip[] {
  const currentProject = projects[0] || null;
  const pendingCount = tasks.filter((item) => ['pending', 'running', 'failed', 'paused'].includes(normalizeStatus(item.status))).length;
  const regionHint = accounts[0]?.region || '多地区实验';

  return [
    {
      label: '当前实验',
      value: currentProject?.name || regionHint,
      note: currentProject ? '已根据真实实验项目回填当前主方案。' : '等待首个实验项目落库后自动回填。',
    },
    {
      label: '待决策',
      value: `${Math.max(1, pendingCount)} 组`,
      note: '来自真实任务池和活动日志的反馈会持续更新这里。',
    },
    {
      label: '保留倾向',
      value: assets.length > 3 ? '素材充分' : '素材偏少',
      note: '优先保留素材覆盖度更高、失败反馈更少的方向。',
    },
  ];
}

export function buildCreativeFocusCards(
  accounts: AccountItem[],
  assets: AssetItem[],
  tasks: TaskItem[],
  activeRail: CreativeRailKey,
): CreativeFocusCard[] {
  const region = accounts[0]?.region || '核心地区';
  const failedCount = tasks.filter((item) => normalizeStatus(item.status) === 'failed').length;
  const videoCount = assets.filter((item) => item.assetType === 'video').length;
  const textCount = assets.filter((item) => item.assetType === 'text').length;
  const toolLabel = RAIL_TOOL_MAP[activeRail].label;
  const strategyCopy = activeRail === 'theme'
    ? '优先保留高体量地区可复用的主题方向。'
    : activeRail === 'shot'
      ? '优先比较镜头节奏和失败任务对应的素材缺口。'
      : activeRail === 'voice'
        ? '优先确认口播长度、字幕素材和账号地区是否匹配。'
        : '优先锁定可直接交付到视频编辑页的版本。';

  return [
    {
      title: '实验主视角',
      badge: '实验',
      tone: 'success',
      desc: `${region} 的创意组合更适合作为当前保留主视角。`,
      meta: '优先保留高体量地区内容验证，不再固定示例方案名。',
      wide: true,
    },
    {
      title: '素材覆盖',
      badge: '素材',
      tone: assets.length > 3 ? 'warning' : 'error',
      desc: `当前已接入 ${assets.length} 条素材，其中视频 ${videoCount} 条、文本 ${textCount} 条。`,
      meta: assets.length > 3 ? '素材覆盖可支撑多版本对比。' : '建议先补充素材后再继续对比。',
    },
    {
      title: '任务反馈',
      badge: '任务',
      tone: failedCount > 0 ? 'warning' : 'info',
      desc: `任务池已有 ${tasks.length} 条反馈，失败 ${failedCount} 条。`,
      meta: failedCount > 0 ? '优先排查失败任务对应的阻塞点。' : '当前没有失败任务阻塞，可继续试验。',
    },
    {
      title: '执行建议',
      badge: toolLabel,
      tone: 'success',
      desc: strategyCopy,
      meta: '建议动作由运行时数据和当前选中的工作台工具共同决定。',
    },
  ];
}

export function buildCreativeSideCards(
  project: ExperimentProjectItem | null,
  tasks: TaskItem[],
  activities: ActivityLogItem[],
): CreativeSideCard[] {
  const failedCount = tasks.filter((item) => normalizeStatus(item.status) === 'failed').length;
  const latestActivity = activities[0] || null;

  return [
    {
      title: '实验判定',
      badge: project ? projectStatusLabel(project.status) : '等待回填',
      tone: project ? projectStatusTone(project.status) : 'warning',
      desc: project?.goal || '加载后根据真实项目目标、状态和反馈回填当前实验判定。',
    },
    {
      title: '风险检查',
      badge: failedCount > 0 ? '待排查' : '已通过',
      tone: failedCount > 0 ? 'warning' : 'success',
      desc: failedCount > 0
        ? `当前仍有 ${failedCount} 条失败任务需要排查，避免带着阻塞继续对比。`
        : '当前无失败任务阻塞，可继续锁定保留方向。',
    },
    {
      title: '下一步 →',
      badge: '移交生产',
      tone: 'info',
      desc: latestActivity?.title || '锁定胜出方向后，再交给视频编辑页继续加工和导出。',
      routeName: 'video-editor',
    },
  ];
}

export function buildCreativeStripCards(
  projects: ExperimentProjectItem[],
  views: ExperimentViewItem[],
  tasks: TaskItem[],
  activities: ActivityLogItem[],
): CreativeStripCard[] {
  const latestProject = projects[0] || null;
  const latestView = views[0] || null;
  const failedTask = tasks.find((item) => normalizeStatus(item.status) === 'failed') || null;
  const latestActivity = activities[0] || null;

  return [
    {
      title: '已保存实验',
      badge: latestProject ? '实验' : '待保存',
      tone: latestProject ? 'success' : 'warning',
      desc: latestProject ? `${latestProject.name} / ${projectStatusLabel(latestProject.status)}` : '保存创意方案后，这里会显示真实实验项目记录。',
    },
    {
      title: '待验证项',
      badge: failedTask ? '待试' : '平稳',
      tone: failedTask ? 'warning' : 'info',
      desc: failedTask?.title || latestView?.name || '加载后显示真实待处理任务、实验视图或素材缺口。',
    },
    {
      title: '复盘记录',
      badge: latestActivity ? '复盘' : '待回写',
      tone: latestActivity ? 'info' : 'warning',
      desc: latestActivity?.title || '保存方案和切换对比后，会在这里显示活动日志中的复盘记录。',
    },
  ];
}

export function buildCreativeCompareRows(
  projects: ExperimentProjectItem[],
  views: ExperimentViewItem[],
  assets: AssetItem[],
  tasks: TaskItem[],
): CreativeCompareRow[] {
  return projects.slice(0, 6).map((project) => {
    const projectViews = views.filter((item) => item.experimentProjectId === project.id);
    const tone = projectStatusTone(project.status);
    const failedCount = tasks.filter((item) => normalizeStatus(item.status) === 'failed').length;
    const recommendation = failedCount > 0
      ? '先看失败任务再决定是否保留。'
      : assets.length > 3
        ? '素材充足，可继续推进双版本对比。'
        : '先补素材，再进入下轮实验。';

    return {
      projectId: project.id,
      title: project.name,
      viewLabel: projectViews.length ? `视图 ${projectViews.length} 个` : '默认视图待补齐',
      statusLabel: projectStatusLabel(project.status),
      statusTone: tone,
      assetLabel: `素材 ${assets.length} 条`,
      feedbackLabel: failedCount > 0 ? `失败反馈 ${failedCount} 条` : `任务反馈 ${tasks.length} 条`,
      recommendation,
    };
  });
}

function buildCreativeAdviceItems(
  project: ExperimentProjectItem,
  tasks: TaskItem[],
  assets: AssetItem[],
  activities: ActivityLogItem[],
): CreativeAdviceItem[] {
  const failedTask = tasks.find((item) => normalizeStatus(item.status) === 'failed') || null;
  const latestActivity = activities[0] || null;
  const items: CreativeAdviceItem[] = [];

  if (failedTask) {
    items.push({
      title: '先看失败任务',
      copy: `${failedTask.title} 当前为失败状态，建议先处理阻塞后再继续对比。`,
      badge: '优先',
      tone: 'warning',
    });
  }

  items.push({
    title: '核对素材缺口',
    copy: assets.length > 3
      ? `当前已有 ${assets.length} 条素材，可支撑下一轮实验视图对比。`
      : '素材数量偏少，建议先补充视频或文案素材后再继续实验。',
    badge: assets.length > 3 ? '可推进' : '风险',
    tone: assets.length > 3 ? 'success' : 'error',
  });

  items.push({
    title: '输出下一步',
    copy: latestActivity?.title || `${project.name} 锁定后，可下发到视频编辑页继续加工与导出。`,
    badge: '动作',
    tone: 'info',
  });

  return items;
}

export function buildCreativeDetail(
  project: ExperimentProjectItem | null,
  tasks: TaskItem[],
  assets: AssetItem[],
  activities: ActivityLogItem[],
  views: ExperimentViewItem[],
): CreativeDetailViewModel {
  if (!project) {
    return {
      title: '创意工坊详情',
      subtitle: '选中实验项目后，这里会固定显示实验状态、风险提醒和下一步建议。',
      statusLabel: '待选择',
      statusTone: 'info',
      detailItems: [
        { label: '当前实验状态', value: '请先选择实验项目' },
        { label: '重点风险', value: '失败任务与素材缺口会在这里自动汇总' },
        { label: '建议动作', value: '锁定方向后再进入视频编辑页继续加工' },
      ],
      adviceItems: [],
    };
  }

  const projectViews = views.filter((item) => item.experimentProjectId === project.id);
  const failedCount = tasks.filter((item) => normalizeStatus(item.status) === 'failed').length;
  const latestActivity = activities[0] || null;

  return {
    title: project.name,
    subtitle: project.goal || '当前项目未填写明确目标，将根据真实任务与素材反馈补齐。',
    statusLabel: projectStatusLabel(project.status),
    statusTone: projectStatusTone(project.status),
    detailItems: [
      { label: '当前实验状态', value: projectStatusLabel(project.status) },
      { label: '实验视图', value: projectViews.length ? `${projectViews.length} 个已保存` : '默认视图待补齐' },
      { label: '重点风险', value: failedCount > 0 ? `存在 ${failedCount} 条失败任务待排查` : '当前无失败任务阻塞' },
      { label: '素材覆盖', value: assets.length ? `已接入 ${assets.length} 条素材` : '暂无可复用素材' },
      { label: '最近复盘', value: latestActivity?.title || '暂无活动日志' },
      { label: '更新时间', value: formatDateTime(project.updatedAt || project.createdAt) },
    ],
    adviceItems: buildCreativeAdviceItems(project, tasks, assets, activities),
  };
}
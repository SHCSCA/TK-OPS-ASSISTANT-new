import type { AssetItem } from '../assets/assetCenter.types';
import { formatDateTime } from '../runtime/format';
import type {
  ProviderItem,
  TaskItem,
  WorkflowDefinitionItem,
  WorkflowRunItem,
} from '../runtime/types';
import type {
  AiContentFactoryAdviceItem,
  AiContentFactoryBatchCard,
  AiContentFactoryConfigItem,
  AiContentFactoryDetailViewModel,
  AiContentFactoryNodeKey,
  AiContentFactoryNodePaletteItem,
  AiContentFactoryStatusTone,
  AiContentFactorySummaryChip,
  AiContentFactoryWorkflowStage,
} from './aiContentFactory.types';

const NODE_PALETTE: AiContentFactoryNodePaletteItem[] = [
  { key: 'input', label: '输入源' },
  { key: 'script', label: 'AI 脚本' },
  { key: 'voice', label: '语音合成' },
  { key: 'edit', label: '批量剪辑' },
  { key: 'export', label: '成品导出' },
];

function normalizeStatus(value: string | null | undefined): string {
  return String(value || '').trim().toLowerCase();
}

export function workflowStatusTone(status: string | null | undefined): AiContentFactoryStatusTone {
  const value = normalizeStatus(status);
  if (['completed', 'done', 'success', 'active'].includes(value)) return 'success';
  if (['running', 'processing'].includes(value)) return 'info';
  if (['failed', 'blocked'].includes(value)) return 'error';
  return 'warning';
}

export function workflowStatusLabel(status: string | null | undefined): string {
  const value = normalizeStatus(status);
  if (['completed', 'done', 'success'].includes(value)) return '已完成';
  if (value === 'active') return '已启用';
  if (['running', 'processing'].includes(value)) return '运行中';
  if (['failed', 'blocked'].includes(value)) return '已阻塞';
  return '待执行';
}

export function buildAiContentFactoryNodePalette(): AiContentFactoryNodePaletteItem[] {
  return NODE_PALETTE;
}

export function buildAiContentFactorySummaryChips(
  definitions: WorkflowDefinitionItem[],
  runs: WorkflowRunItem[],
  providers: ProviderItem[],
  assets: AssetItem[],
): AiContentFactorySummaryChip[] {
  const currentDefinition = definitions[0] || null;
  const currentRun = runs[0] || null;
  const activeProviders = providers.filter((item) => item.isActive).length;

  return [
    {
      label: '当前工作流',
      value: currentDefinition?.name || '等待创建',
      note: currentDefinition ? '工作流定义来自真实持久化记录。' : '保存工作流后，这里会显示真实工作流定义。',
    },
    {
      label: '当前批次',
      value: currentRun ? workflowStatusLabel(currentRun.status) : '待启动',
      note: currentRun ? '最近批次运行状态来自 workflow runs。' : '运行工作流或启动批量生产后，这里会自动回填。',
    },
    {
      label: '提供商状态',
      value: activeProviders > 0 ? `${activeProviders} 个可用` : '待接入',
      note: `素材 ${assets.length} 条，优先选择可用 Provider 驱动当前节点。`,
    },
  ];
}

export function buildAiContentFactoryWorkflowStages(
  assets: AssetItem[],
  tasks: TaskItem[],
  providers: ProviderItem[],
  definition: WorkflowDefinitionItem | null,
  run: WorkflowRunItem | null,
  activeNode: AiContentFactoryNodeKey,
): AiContentFactoryWorkflowStage[] {
  const activeProviders = providers.filter((item) => item.isActive).length;
  const failedTasks = tasks.filter((item) => normalizeStatus(item.status) === 'failed').length;
  const videoAssets = assets.filter((item) => item.assetType === 'video').length;
  const textAssets = assets.filter((item) => item.assetType === 'text').length;

  return [
    {
      key: 'input',
      title: '输入素材',
      badge: `${assets.length} 条`,
      tone: assets.length > 0 ? 'success' : 'warning',
      desc: `当前已接入视频 ${videoAssets} 条、文本 ${textAssets} 条，作为生产线输入源。`,
      meta: definition?.name || '保存首个工作流后会固定当前输入策略。',
      active: activeNode === 'input',
    },
    {
      key: 'script',
      title: 'AI 脚本',
      badge: activeProviders > 0 ? 'Provider 就绪' : '待接入',
      tone: activeProviders > 0 ? 'info' : 'warning',
      desc: activeProviders > 0 ? `当前有 ${activeProviders} 个可用 Provider 支撑脚本节点。` : '尚无可用 Provider，脚本节点暂时不可放量。',
      meta: run ? `最近批次状态：${workflowStatusLabel(run.status)}` : '运行工作流后会在这里显示脚本节点反馈。',
      active: activeNode === 'script',
    },
    {
      key: 'voice',
      title: '语音与字幕',
      badge: failedTasks > 0 ? '待排查' : '已接通',
      tone: failedTasks > 0 ? 'warning' : 'success',
      desc: failedTasks > 0 ? `当前有 ${failedTasks} 条任务失败，优先确认语音节点配额和字幕清洗。` : '当前任务池没有失败阻塞，可继续推进语音与字幕节点。',
      meta: '语音节点状态由任务反馈和 Provider 可用性共同决定。',
      active: activeNode === 'voice',
    },
    {
      key: 'edit',
      title: '批量剪辑',
      badge: tasks.length ? `${tasks.length} 条任务` : '等待任务',
      tone: tasks.length ? 'info' : 'warning',
      desc: tasks.length ? '批量剪辑状态优先参考任务队列和最近工作流批次。' : '启动批量生产后，这里会显示真实剪辑任务反馈。',
      meta: '这一段不能退化成静态示意图。',
      active: activeNode === 'edit',
    },
    {
      key: 'export',
      title: '导出成品',
      badge: run ? workflowStatusLabel(run.status) : '待导出',
      tone: run ? workflowStatusTone(run.status) : 'warning',
      desc: run ? '最近工作流批次的结果会在导出节点回填。' : '工作流运行完成后，这里会显示导出结果和可回放批次。',
      meta: '导出态优先读取 workflow run，而不是硬编码成功率。',
      active: activeNode === 'export',
    },
  ];
}

export function buildAiContentFactoryBatchCards(
  runs: WorkflowRunItem[],
  tasks: TaskItem[],
): AiContentFactoryBatchCard[] {
  const latestRun = runs[0] || null;
  const failedRun = runs.find((item) => normalizeStatus(item.status) === 'failed') || null;
  const queuedTask = tasks.find((item) => ['pending', 'running'].includes(normalizeStatus(item.status))) || null;

  return [
    {
      title: '最近批次',
      badge: latestRun ? workflowStatusLabel(latestRun.status) : '待启动',
      tone: latestRun ? workflowStatusTone(latestRun.status) : 'warning',
      desc: latestRun
        ? `批次 #${latestRun.id} 已创建，创建时间 ${formatDateTime(latestRun.createdAt)}。`
        : '运行工作流后，这里会显示真实批次记录。',
    },
    {
      title: '失败节点',
      badge: failedRun ? '待重试' : '平稳',
      tone: failedRun ? 'error' : 'success',
      desc: failedRun
        ? `批次 #${failedRun.id} 当前失败，优先处理阻塞节点后再继续放量。`
        : '当前没有失败批次阻塞。',
    },
    {
      title: '待处理任务',
      badge: queuedTask ? '队列中' : '空闲',
      tone: queuedTask ? 'info' : 'warning',
      desc: queuedTask ? `${queuedTask.title} 正在任务队列中等待或执行。` : '启动批量生产后，这里会显示当前任务排队情况。',
    },
  ];
}

export function buildAiContentFactoryConfigItems(
  activeNode: AiContentFactoryNodeKey,
  providers: ProviderItem[],
  assets: AssetItem[],
  definition: WorkflowDefinitionItem | null,
  run: WorkflowRunItem | null,
): AiContentFactoryConfigItem[] {
  const activeProvider = providers.find((item) => item.isActive) || providers[0] || null;
  const audioAssets = assets.filter((item) => item.assetType === 'audio').length;

  if (activeNode === 'input') {
    return [
      { label: '当前节点', value: '输入素材' },
      { label: '素材总量', value: `${assets.length} 条` },
      { label: '模板工程', value: `${assets.filter((item) => item.assetType === 'template').length} 个` },
      { label: '当前工作流', value: definition?.name || '待保存' },
    ];
  }
  if (activeNode === 'script') {
    return [
      { label: '当前节点', value: 'AI 脚本' },
      { label: '当前供应商', value: activeProvider?.name || '待接入' },
      { label: '默认模型', value: activeProvider?.defaultModel || '待配置' },
      { label: '运行状态', value: run ? workflowStatusLabel(run.status) : '待启动' },
    ];
  }
  if (activeNode === 'voice') {
    return [
      { label: '当前节点', value: '语音与字幕' },
      { label: '可用音频', value: `${audioAssets} 条` },
      { label: '字幕策略', value: '按真实任务反馈动态回填' },
      { label: '最近批次', value: run ? `#${run.id}` : '待创建' },
    ];
  }
  if (activeNode === 'edit') {
    return [
      { label: '当前节点', value: '批量剪辑' },
      { label: '比例', value: '9:16' },
      { label: '转场策略', value: '基于当前工作流配置自动派生' },
      { label: '素材覆盖', value: `${assets.length} 条` },
    ];
  }
  return [
    { label: '当前节点', value: '导出成品' },
    { label: '导出状态', value: run ? workflowStatusLabel(run.status) : '待导出' },
    { label: '最近结果', value: run?.resultJson ? '已有结果' : '暂无结果' },
    { label: '工作流', value: definition?.name || '待选择' },
  ];
}

function buildAdviceItems(
  definition: WorkflowDefinitionItem,
  runs: WorkflowRunItem[],
  tasks: TaskItem[],
  providers: ProviderItem[],
): AiContentFactoryAdviceItem[] {
  const failedRun = runs.find((item) => normalizeStatus(item.status) === 'failed') || null;
  const activeProviders = providers.filter((item) => item.isActive).length;
  const items: AiContentFactoryAdviceItem[] = [];

  if (failedRun) {
    items.push({
      title: '先排查失败批次',
      copy: `批次 #${failedRun.id} 当前失败，优先确认脚本或语音节点阻塞。`,
      badge: '优先',
      tone: 'warning',
    });
  }

  items.push({
    title: '核对 Provider 配额',
    copy: activeProviders > 0 ? `当前有 ${activeProviders} 个可用 Provider，可继续支撑内容工厂运行。` : '当前没有可用 Provider，运行工作流前应先完成供应商接入。',
    badge: activeProviders > 0 ? '可用' : '阻塞',
    tone: activeProviders > 0 ? 'success' : 'error',
  });

  items.push({
    title: '下发批量生产',
    copy: tasks.length ? `${definition.name} 已具备任务反馈，可按当前工作流继续启动批次。` : '保存工作流后，可继续启动内容批量生产。',
    badge: '动作',
    tone: 'info',
  });

  return items;
}

export function buildAiContentFactoryDetail(
  definition: WorkflowDefinitionItem | null,
  runs: WorkflowRunItem[],
  tasks: TaskItem[],
  providers: ProviderItem[],
  assets: AssetItem[],
): AiContentFactoryDetailViewModel {
  if (!definition) {
    return {
      title: 'AI 内容工厂详情',
      subtitle: '选中工作流后，这里会固定显示当前批次、失败节点和下发建议。',
      statusLabel: '待选择',
      statusTone: 'info',
      detailItems: [
        { label: '当前工作流', value: '请先选择或保存工作流' },
        { label: '当前批次', value: '运行工作流后自动回填' },
        { label: '失败节点', value: '失败批次与阻塞任务会在这里汇总' },
      ],
      adviceItems: [],
    };
  }

  const latestRun = runs[0] || null;
  const failedCount = runs.filter((item) => normalizeStatus(item.status) === 'failed').length;
  const activeProviders = providers.filter((item) => item.isActive).length;

  return {
    title: definition.name,
    subtitle: definition.description || '当前工作流未填写说明，将根据真实运行状态持续补齐。',
    statusLabel: workflowStatusLabel(definition.status),
    statusTone: workflowStatusTone(definition.status),
    detailItems: [
      { label: '当前工作流', value: workflowStatusLabel(definition.status) },
      { label: '当前批次', value: latestRun ? `#${latestRun.id} / ${workflowStatusLabel(latestRun.status)}` : '暂无批次' },
      { label: '失败节点', value: failedCount > 0 ? `${failedCount} 个批次待排查` : '当前无失败批次' },
      { label: '素材输入', value: assets.length ? `${assets.length} 条已接入` : '暂无素材' },
      { label: 'Provider', value: activeProviders > 0 ? `${activeProviders} 个可用` : '待接入' },
      { label: '更新时间', value: formatDateTime(definition.updatedAt || definition.createdAt) },
    ],
    adviceItems: buildAdviceItems(definition, runs, tasks, providers),
  };
}
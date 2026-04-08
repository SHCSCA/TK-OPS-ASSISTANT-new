import type { AssetItem } from '../assets/assetCenter.types';
import type {
  TaskItem,
  VideoClipItem,
  VideoExportItem,
  VideoProjectItem,
  VideoSequenceItem,
  VideoSnapshotItem,
  VideoSubtitleItem,
} from '../runtime/types';
import type {
  VideoEditorAssetCard,
  VideoEditorDetailViewModel,
  VideoEditorQueueCard,
  VideoEditorSummaryChip,
  VideoEditorTimelineLane,
  VideoEditorTone,
  VideoInspectorTab,
} from './videoEditor.types';

function formatDuration(ms: number | null | undefined): string {
  const totalSeconds = Math.max(0, Math.floor((ms || 0) / 1000));
  const seconds = totalSeconds % 60;
  const minutes = Math.floor(totalSeconds / 60) % 60;
  const hours = Math.floor(totalSeconds / 3600);
  if (hours > 0) {
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return '--';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString('zh-CN', { hour12: false });
}

function fileSizeText(bytes: number | null | undefined): string {
  const size = Math.max(0, Number(bytes || 0));
  if (size >= 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }
  if (size >= 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }
  if (size >= 1024) {
    return `${Math.round(size / 1024)} KB`;
  }
  return `${size} B`;
}

function findAsset(assets: AssetItem[], assetId: number | null | undefined): AssetItem | null {
  if (typeof assetId !== 'number') {
    return null;
  }
  return assets.find((item) => item.id === assetId) || null;
}

export function videoStatusTone(status: string | null | undefined): VideoEditorTone {
  const normalized = String(status || '').toLowerCase();
  if (normalized === 'completed' || normalized === 'active') {
    return 'success';
  }
  if (normalized === 'failed' || normalized === 'error') {
    return 'error';
  }
  if (normalized === 'running') {
    return 'info';
  }
  return 'warning';
}

export function videoStatusLabel(status: string | null | undefined): string {
  const normalized = String(status || '').toLowerCase();
  if (normalized === 'completed') return '已完成';
  if (normalized === 'failed') return '失败';
  if (normalized === 'running') return '运行中';
  if (normalized === 'active') return '当前序列';
  if (normalized === 'pending') return '待执行';
  return status || '待处理';
}

export function buildVideoEditorSummaryChips(
  project: VideoProjectItem | null,
  sequence: VideoSequenceItem | null,
  clips: VideoClipItem[],
  exports: VideoExportItem[],
): VideoEditorSummaryChip[] {
  const failedExports = exports.filter((item) => item.status === 'failed').length;
  return [
    {
      label: '当前工程',
      value: project?.name || '尚未创建工程',
      note: project ? `最近更新时间 ${formatDate(project.updatedAt)}` : '首次导入素材后会自动建立工程。',
    },
    {
      label: '当前序列',
      value: sequence?.name || '尚未创建序列',
      note: sequence ? `时长 ${formatDuration(sequence.durationMs)}，片段 ${clips.length}` : '切换剪辑序列后会加载片段与字幕轨。',
    },
    {
      label: '导出状态',
      value: exports.length ? `${exports.length} 条记录` : '暂无导出',
      note: failedExports > 0 ? `失败 ${failedExports} 条，右栏会显示原因。` : '终版与试看导出都会写入这里。',
    },
  ];
}

export function buildVideoEditorAssetCards(assets: AssetItem[], selectedAssetId: number | null): VideoEditorAssetCard[] {
  return assets.slice(0, 12).map((asset) => ({
    id: asset.id,
    title: asset.filename,
    meta: `${asset.assetType} · ${fileSizeText(asset.fileSize)}`,
    badge: asset.assetType === 'audio' ? '音频' : asset.assetType === 'text' ? '字幕' : '素材',
    tone: asset.assetType === 'audio' ? 'warning' : asset.assetType === 'text' ? 'info' : 'success',
    selected: asset.id === selectedAssetId,
  }));
}

export function buildVideoEditorTimelineLanes(
  clips: VideoClipItem[],
  subtitles: VideoSubtitleItem[],
  assets: AssetItem[],
  selectedClipId: number | null,
  selectedSubtitleId: number | null,
): VideoEditorTimelineLane[] {
  const videoItems: VideoEditorTimelineLane['items'] = clips
    .filter((item) => item.trackType !== 'audio')
    .map((item) => {
      const asset = findAsset(assets, item.assetId);
      return {
        id: item.id,
        label: asset?.filename || `片段 #${item.id}`,
        meta: `${formatDuration(item.startMs)} - ${formatDuration(item.startMs + item.durationMs)}`,
        tone: item.id === selectedClipId ? 'success' : 'info',
        selected: item.id === selectedClipId,
      };
    });
  const subtitleItems: VideoEditorTimelineLane['items'] = subtitles.map((item) => ({
    id: item.id,
    label: item.text || `字幕 #${item.id}`,
    meta: `${formatDuration(item.startMs)} - ${formatDuration(item.endMs)}`,
    tone: item.id === selectedSubtitleId ? 'warning' : 'info',
    selected: item.id === selectedSubtitleId,
  }));
  const audioItems: VideoEditorTimelineLane['items'] = clips
    .filter((item) => item.trackType === 'audio')
    .map((item) => {
      const asset = findAsset(assets, item.assetId);
      return {
        id: item.id,
        label: asset?.filename || `音频 #${item.id}`,
        meta: `${formatDuration(item.startMs)} - ${formatDuration(item.startMs + item.durationMs)}`,
        tone: item.id === selectedClipId ? 'success' : 'warning',
        selected: item.id === selectedClipId,
      };
    });

  return [
    { key: 'video', title: 'V1 视频', emptyText: '双击左侧素材即可把片段挂入当前序列。', items: videoItems },
    { key: 'subtitle', title: 'T1 字幕', emptyText: '当前没有字幕段，右栏可直接新增字幕。', items: subtitleItems },
    { key: 'audio', title: 'A1 音频', emptyText: '导入音频素材后会自动出现在这里。', items: audioItems },
  ];
}

export function buildVideoEditorQueueCards(
  tasks: TaskItem[],
  exports: VideoExportItem[],
  snapshots: VideoSnapshotItem[],
): VideoEditorQueueCard[] {
  const latestExport = exports[0] || null;
  const latestTask = tasks[0] || null;
  const latestSnapshot = snapshots[0] || null;
  return [
    {
      title: latestExport ? `导出 ${latestExport.id}` : '导出队列',
      desc: latestExport ? `${videoStatusLabel(latestExport.status)}，输出 ${latestExport.outputPath || '等待生成路径'}` : '发起终版导出后，这里会展示最新记录。',
      badge: latestExport ? videoStatusLabel(latestExport.status) : '待触发',
      tone: latestExport ? videoStatusTone(latestExport.status) : 'info',
    },
    {
      title: latestTask ? latestTask.title : '任务反馈',
      desc: latestTask ? `当前任务状态 ${latestTask.status}，用于承接上游内容生产和导出后的回写。` : '暂无相关任务，等待内容工厂或导出回写。',
      badge: latestTask ? latestTask.status : '空',
      tone: latestTask ? videoStatusTone(latestTask.status) : 'warning',
    },
    {
      title: latestSnapshot ? latestSnapshot.title : '快照恢复',
      desc: latestSnapshot ? `最近快照保存于 ${formatDate(latestSnapshot.createdAt)}` : '点击“保存快照”后，这里会保留最近可恢复版本。',
      badge: latestSnapshot ? '可恢复' : '未创建',
      tone: latestSnapshot ? 'success' : 'info',
    },
  ];
}

export function buildVideoEditorInspectorItems(
  tab: VideoInspectorTab,
  project: VideoProjectItem | null,
  sequence: VideoSequenceItem | null,
  asset: AssetItem | null,
  clip: VideoClipItem | null,
  subtitle: VideoSubtitleItem | null,
  exports: VideoExportItem[],
  snapshots: VideoSnapshotItem[],
): Array<{ label: string; value: string; stacked?: boolean }> {
  if (tab === 'subtitles') {
    return [
      { label: '当前字幕', value: subtitle?.text || '尚未选择字幕', stacked: true },
      { label: '时间区间', value: subtitle ? `${formatDuration(subtitle.startMs)} - ${formatDuration(subtitle.endMs)}` : '--' },
      { label: '所属序列', value: sequence?.name || '--' },
    ];
  }
  if (tab === 'exports') {
    const latestExport = exports[0] || null;
    const latestSnapshot = snapshots[0] || null;
    return [
      { label: '最近导出', value: latestExport ? `#${latestExport.id} / ${videoStatusLabel(latestExport.status)}` : '暂无导出' },
      { label: '输出路径', value: latestExport?.outputPath || '等待创建', stacked: true },
      { label: '最近快照', value: latestSnapshot ? `${latestSnapshot.title} / ${formatDate(latestSnapshot.createdAt)}` : '暂无快照', stacked: true },
    ];
  }
  return [
    { label: '当前工程', value: project?.name || '尚未创建工程' },
    { label: '当前序列', value: sequence?.name || '尚未创建序列' },
    { label: '选中素材', value: asset?.filename || '尚未选择素材', stacked: true },
    { label: '选中片段', value: clip ? `${clip.id} / ${formatDuration(clip.durationMs)}` : '尚未选择片段' },
  ];
}

export function buildVideoEditorDetail(
  project: VideoProjectItem | null,
  sequence: VideoSequenceItem | null,
  asset: AssetItem | null,
  clip: VideoClipItem | null,
  subtitle: VideoSubtitleItem | null,
  exports: VideoExportItem[],
  snapshots: VideoSnapshotItem[],
  tasks: TaskItem[],
): VideoEditorDetailViewModel {
  const latestExport = exports[0] || null;
  const latestTask = tasks[0] || null;
  const hasFailedExport = exports.some((item) => item.status === 'failed');
  const hasSelection = Boolean(asset || clip || subtitle);

  return {
    title: project?.name || '视频编辑详情',
    subtitle: sequence ? `当前序列：${sequence.name}` : '尚未创建序列，导入素材后可以开始剪辑。',
    statusLabel: latestExport ? videoStatusLabel(latestExport.status) : '待剪辑',
    statusTone: latestExport ? videoStatusTone(latestExport.status) : 'info',
    detailItems: [
      { label: '当前工程', value: project?.name || '未创建' },
      { label: '当前序列', value: sequence?.name || '未创建' },
      { label: '当前焦点', value: subtitle?.text || asset?.filename || (clip ? `片段 #${clip.id}` : '尚未选择对象'), stacked: Boolean(subtitle || asset) },
      { label: '最近快照', value: snapshots[0] ? `${snapshots[0].title} / ${formatDate(snapshots[0].createdAt)}` : '暂无快照', stacked: true },
    ],
    adviceItems: [
      {
        title: hasFailedExport ? '先处理失败导出' : '保持序列与导出同步',
        copy: hasFailedExport
          ? `最近失败导出需要先查看原因：${latestExport?.errorMessage || '请检查素材源文件和导出路径。'}`
          : '终版导出前先确认当前片段、字幕与快照都已经更新到最新版本。',
        badge: hasFailedExport ? '阻塞' : '建议',
        tone: hasFailedExport ? 'error' : 'info',
      },
      {
        title: latestTask ? '关注上游任务回写' : '准备本轮剪辑动作',
        copy: latestTask ? `最近任务 ${latestTask.title} 状态为 ${latestTask.status}，必要时在导出前确认其输出是否已回写到当前工程。` : '可以先切换剪辑序列、导入素材，再新增字幕或保存快照。',
        badge: latestTask ? videoStatusLabel(latestTask.status) : '待开始',
        tone: latestTask ? videoStatusTone(latestTask.status) : 'warning',
      },
    ],
    canExportFinal: Boolean(project && sequence),
    canPreviewExport: Boolean(project && sequence),
    canSaveSnapshot: Boolean(project),
    canRestoreSnapshot: snapshots.length > 0,
    canCreateSubtitle: Boolean(sequence && (hasSelection || clip)),
  };
}
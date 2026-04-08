import type { AssetItem } from '../assets/assetCenter.types';
import { formatDateTime } from '../runtime/format';
import type { AccountItem, TaskItem } from '../runtime/types';
import type {
  PublishAdviceItem,
  PublishCalendarDay,
  PublishDetailViewModel,
  PublishMetricCard,
  PublishRecord,
  PublishStatusTone,
} from './scheduledPublish.types';

function normalizeDateKey(value: string | null): string {
  if (!value) {
    return '';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return '';
  }
  const year = parsed.getFullYear();
  const month = String(parsed.getMonth() + 1).padStart(2, '0');
  const day = String(parsed.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatDayLabel(value: Date): string {
  return value.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    weekday: 'short',
  });
}

export function mapPublishStatusLabel(status: string): string {
  const value = String(status || '').toLowerCase();
  if (value === 'running') return '发布中';
  if (value === 'completed') return '已发布';
  if (value === 'failed') return '已中断';
  if (value === 'paused') return '已暂停';
  return '待审核';
}

export function mapPublishStatusTone(status: string): PublishStatusTone {
  const value = String(status || '').toLowerCase();
  if (value === 'completed') return 'success';
  if (value === 'failed') return 'error';
  if (value === 'running') return 'info';
  return 'warning';
}

export function buildPublishMetrics(tasks: TaskItem[]): PublishMetricCard[] {
  const todayKey = normalizeDateKey(new Date().toISOString());
  const todayPlans = tasks.filter((item) => normalizeDateKey(item.scheduledAt || item.createdAt) === todayKey).length;
  const pendingReview = tasks.filter((item) => ['pending', 'paused'].includes(String(item.status || '').toLowerCase())).length;
  const interrupted = tasks.filter((item) => String(item.status || '').toLowerCase() === 'failed').length;

  return [
    {
      label: '今日计划',
      value: String(todayPlans),
      delta: `${tasks.length} 条发布任务`,
      note: '按当天计划时间统计',
      tone: 'info',
    },
    {
      label: '待审核',
      value: String(pendingReview),
      delta: '待确认或已暂停',
      note: '建议优先检查账号与发布时间',
      tone: 'warning',
    },
    {
      label: '中断计划',
      value: String(interrupted),
      delta: interrupted > 0 ? '需要补偿重试' : '当前无中断',
      note: '来源于失败任务状态',
      tone: interrupted > 0 ? 'error' : 'success',
    },
  ];
}

export function buildPublishRecords(tasks: TaskItem[], accounts: AccountItem[]): PublishRecord[] {
  const accountMap = new Map(accounts.map((item) => [item.id, item]));

  return [...tasks]
    .sort((left, right) => {
      const leftTime = new Date(left.scheduledAt || left.createdAt || 0).getTime();
      const rightTime = new Date(right.scheduledAt || right.createdAt || 0).getTime();
      return leftTime - rightTime;
    })
    .map((task) => {
      const account = typeof task.accountId === 'number' ? accountMap.get(task.accountId) : null;
      const scheduleValue = task.scheduledAt || task.createdAt;
      return {
        id: task.id,
        title: task.title || '未命名发布计划',
        status: task.status,
        statusLabel: mapPublishStatusLabel(task.status),
        statusTone: mapPublishStatusTone(task.status),
        priority: task.priority || 'medium',
        timeLabel: formatDateTime(scheduleValue),
        scheduledAt: task.scheduledAt,
        platformLabel: account?.platform || 'TikTok',
        accountLabel: task.accountUsername || account?.username || '未绑定账号',
        summary: task.resultSummary || '来源页面：定时发布',
        calendarDateKey: normalizeDateKey(scheduleValue),
      };
    });
}

function buildAdviceItems(record: PublishRecord | null, assets: AssetItem[], tasks: TaskItem[]): PublishAdviceItem[] {
  if (!record) {
    return [];
  }

  const availableAssets = assets.filter((item) => item.assetType === 'video' || item.assetType === 'image').length;
  const sameAccountTasks = tasks.filter((item) => item.accountUsername === record.accountLabel).length;
  const items: PublishAdviceItem[] = [
    {
      title: '素材准备',
      copy: `当前可直接复用的视频/图片素材 ${availableAssets} 份。`,
      badge: availableAssets > 0 ? '已就绪' : '待补齐',
      tone: availableAssets > 0 ? 'success' : 'warning',
    },
    {
      title: '账号排班',
      copy: `${record.accountLabel} 当前关联 ${sameAccountTasks} 条发布任务，建议错峰排期。`,
      badge: sameAccountTasks > 3 ? '偏拥挤' : '正常',
      tone: sameAccountTasks > 3 ? 'warning' : 'info',
    },
  ];

  if (record.status === 'failed') {
    items.unshift({
      title: '中断补偿',
      copy: '建议先检查账号环境、网络状态和发布时间配置，再执行重试。',
      badge: '需处理',
      tone: 'error',
    });
  } else if (record.status === 'pending' || record.status === 'paused') {
    items.unshift({
      title: '审核提醒',
      copy: '计划尚未进入执行，建议先确认素材版本与发布时间窗口。',
      badge: '待确认',
      tone: 'warning',
    });
  } else if (record.status === 'completed') {
    items.unshift({
      title: '复盘建议',
      copy: '计划已完成，可在任务队列中继续跟踪发布效果与后续互动任务。',
      badge: '可复盘',
      tone: 'success',
    });
  }

  return items;
}

export function buildPublishDetail(
  record: PublishRecord | null,
  tasks: TaskItem[],
  accounts: AccountItem[],
  assets: AssetItem[],
): PublishDetailViewModel {
  if (!record) {
    return {
      title: '定时发布详情',
      subtitle: '选中左侧发布计划后，这里会固定展示排程、账号和素材建议。',
      statusLabel: '待选择',
      statusTone: 'info',
      detailItems: [
        { label: '当前状态', value: '请先选择发布计划' },
        { label: '发布时间', value: '--' },
        { label: '资源概览', value: '账号 -- / 素材 --' },
      ],
      adviceItems: [],
    };
  }

  const linkedAccount = accounts.find((item) => item.username === record.accountLabel || item.id === tasks.find((task) => task.id === record.id)?.accountId);
  const assetCount = assets.filter((item) => item.accountId === linkedAccount?.id || item.accountId == null).length;

  return {
    title: record.title,
    subtitle: record.summary,
    statusLabel: record.statusLabel,
    statusTone: record.statusTone,
    detailItems: [
      { label: '当前状态', value: record.statusLabel },
      { label: '发布时间', value: record.timeLabel },
      { label: '发布账号', value: record.accountLabel },
      { label: '平台', value: record.platformLabel },
      { label: '优先级', value: record.priority },
      { label: '素材库存', value: `${assetCount} 份可用素材` },
    ],
    adviceItems: buildAdviceItems(record, assets, tasks),
  };
}

export function buildPublishCalendarDays(tasks: TaskItem[]): PublishCalendarDay[] {
  const base = new Date();
  const records = buildPublishRecords(tasks, []);

  return Array.from({ length: 7 }, (_, index) => {
    const day = new Date(base);
    day.setDate(base.getDate() + index);
    const dayKey = normalizeDateKey(day.toISOString());
    return {
      key: dayKey,
      label: formatDayLabel(day),
      isToday: index === 0,
      slots: records
        .filter((item) => item.calendarDateKey === dayKey)
        .map((item) => ({
          id: item.id,
          title: item.title,
          timeLabel: item.timeLabel,
          tone: item.statusTone,
        })),
    };
  });
}
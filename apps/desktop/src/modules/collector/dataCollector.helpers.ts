import type { AssetItem } from '../assets/assetCenter.types';
import { formatDateTime } from '../runtime/format';
import type { AccountItem, DeviceItem, TaskItem } from '../runtime/types';
import type {
  CollectorAdviceItem,
  CollectorDetailViewModel,
  CollectorKanbanColumn,
  CollectorMetricCard,
  CollectorProxySummary,
  CollectorRecord,
  CollectorStatusTone,
} from './dataCollector.types';

const KANBAN_ORDER = ['running', 'pending', 'failed', 'completed'];

function normalizeStatus(value: string): string {
  return String(value || '').toLowerCase();
}

function normalizeDeviceHealth(device: DeviceItem): CollectorStatusTone {
  const status = String(device.status || '').toLowerCase();
  const proxyStatus = String(device.proxyStatus || '').toLowerCase();
  const fingerprintStatus = String(device.fingerprintStatus || '').toLowerCase();

  if (
    ['failed', 'error', 'offline', 'disabled'].some((item) => status.includes(item))
    || ['failed', 'error', 'offline', 'blocked'].some((item) => proxyStatus.includes(item))
    || ['failed', 'error', 'offline', 'missing'].some((item) => fingerprintStatus.includes(item))
  ) {
    return 'error';
  }
  if (
    ['warning', 'pending', 'checking'].some((item) => status.includes(item))
    || ['warning', 'pending', 'checking'].some((item) => proxyStatus.includes(item))
    || ['warning', 'pending', 'checking'].some((item) => fingerprintStatus.includes(item))
  ) {
    return 'warning';
  }
  if (status || proxyStatus || fingerprintStatus) {
    return 'success';
  }
  return 'info';
}

function mapDeviceStatusLabel(device: DeviceItem): string {
  const tone = normalizeDeviceHealth(device);
  if (tone === 'error') return '异常环境';
  if (tone === 'warning') return '待巡检';
  if (tone === 'success') return '可用';
  return '待确认';
}

export function mapCollectorStatusLabel(status: string): string {
  const value = normalizeStatus(status);
  if (value === 'running') return '运行中';
  if (value === 'paused') return '已暂停';
  if (value === 'failed') return '失败';
  if (value === 'completed') return '已完成';
  return '待执行';
}

export function mapCollectorStatusTone(status: string): CollectorStatusTone {
  const value = normalizeStatus(status);
  if (value === 'completed') return 'success';
  if (value === 'failed') return 'error';
  if (value === 'running') return 'info';
  return 'warning';
}

export function mapCollectorTaskTypeLabel(taskType: string): string {
  const value = String(taskType || '').toLowerCase();
  if (value === 'scrape') return '数据采集';
  return value || '未知类型';
}

export function mapCollectorPriorityLabel(priority: string): string {
  const value = String(priority || '').toLowerCase();
  if (value === 'high') return '高';
  if (value === 'low') return '低';
  return '中';
}

export function buildCollectorMetrics(tasks: TaskItem[], devices: DeviceItem[]): CollectorMetricCard[] {
  const abnormalTasks = tasks.filter((item) => ['failed', 'paused'].includes(normalizeStatus(item.status))).length;
  const completedTasks = tasks.filter((item) => normalizeStatus(item.status) === 'completed').length;
  const executionRate = tasks.length ? `${Math.round((completedTasks / tasks.length) * 100)}%` : '0%';
  const healthyDevices = devices.filter((item) => normalizeDeviceHealth(item) === 'success').length;

  return [
    {
      label: '采集任务总数',
      value: String(tasks.length),
      delta: `${tasks.length} 条 scrape 任务`,
      note: '仅统计数据采集助手范围内的任务',
      tone: 'info',
    },
    {
      label: '异常 / 暂停项',
      value: String(abnormalTasks),
      delta: abnormalTasks > 0 ? '需要补偿重试' : '当前无阻塞项',
      note: '失败任务与暂停任务合并统计',
      tone: abnormalTasks > 0 ? 'error' : 'success',
    },
    {
      label: '执行率',
      value: executionRate,
      delta: `${completedTasks} 条已完成`,
      note: `代理池可用设备 ${healthyDevices} 台`,
      tone: completedTasks > 0 ? 'success' : 'warning',
    },
  ];
}

export function buildCollectorRecords(tasks: TaskItem[], accounts: AccountItem[]): CollectorRecord[] {
  const accountMap = new Map(accounts.map((item) => [item.id, item]));

  return [...tasks]
    .sort((left, right) => {
      const leftTime = new Date(left.scheduledAt || left.startedAt || left.createdAt || 0).getTime();
      const rightTime = new Date(right.scheduledAt || right.startedAt || right.createdAt || 0).getTime();
      return rightTime - leftTime;
    })
    .map((task) => {
      const account = typeof task.accountId === 'number' ? accountMap.get(task.accountId) : null;
      return {
        id: task.id,
        title: task.title || '数据采集任务',
        taskType: task.taskType,
        taskTypeLabel: mapCollectorTaskTypeLabel(task.taskType),
        status: task.status,
        statusLabel: mapCollectorStatusLabel(task.status),
        statusTone: mapCollectorStatusTone(task.status),
        priority: task.priority || 'medium',
        priorityLabel: mapCollectorPriorityLabel(task.priority),
        accountLabel: task.accountUsername || account?.username || '未绑定账号',
        regionLabel: account?.region || '未分配区域',
        timeLabel: formatDateTime(task.scheduledAt || task.startedAt || task.createdAt),
        summary: task.resultSummary || '来源页面：数据采集助手',
      };
    });
}

function buildAdviceItems(
  record: CollectorRecord | null,
  tasks: TaskItem[],
  assets: AssetItem[],
  devices: DeviceItem[],
): CollectorAdviceItem[] {
  if (!record) {
    return [];
  }

  const failedCount = tasks.filter((item) => normalizeStatus(item.status) === 'failed').length;
  const proxyReadyDevices = devices.filter((item) => Boolean(String(item.proxyIp || '').trim())).length;
  const assetCount = assets.filter((item) => item.accountId == null || item.assetType === 'text' || item.assetType === 'template').length;

  const items: CollectorAdviceItem[] = [
    {
      title: '代理池覆盖',
      copy: `当前共有 ${proxyReadyDevices} 台设备已配置代理，可覆盖采集任务执行。`,
      badge: proxyReadyDevices > 0 ? '可执行' : '待补齐',
      tone: proxyReadyDevices > 0 ? 'success' : 'warning',
    },
    {
      title: '结果落库摘要',
      copy: `可用于采集结果归档的模板 / 文本文档 ${assetCount} 份。`,
      badge: assetCount > 0 ? '已准备' : '偏少',
      tone: assetCount > 0 ? 'info' : 'warning',
    },
  ];

  if (record.status === 'failed') {
    items.unshift({
      title: '失败补偿',
      copy: '建议先检查设备代理、账号区域和抓取来源配置，再执行重试。',
      badge: '需处理',
      tone: 'error',
    });
  } else if (record.status === 'paused') {
    items.unshift({
      title: '暂停恢复',
      copy: '当前任务处于暂停状态，建议确认代理池可用性后再继续执行。',
      badge: '待恢复',
      tone: 'warning',
    });
  } else if (record.status === 'running') {
    items.unshift({
      title: '执行监控',
      copy: '任务正在运行中，建议持续关注设备代理状态和区域分布。',
      badge: '执行中',
      tone: 'info',
    });
  } else if (failedCount > 0) {
    items.unshift({
      title: '历史异常',
      copy: `当前采集域仍有 ${failedCount} 条失败任务，建议优先补偿高优先级任务。`,
      badge: '有积压',
      tone: 'warning',
    });
  }

  return items;
}

export function buildCollectorDetail(
  record: CollectorRecord | null,
  tasks: TaskItem[],
  accounts: AccountItem[],
  assets: AssetItem[],
  devices: DeviceItem[],
): CollectorDetailViewModel {
  if (!record) {
    return {
      title: '采集任务详情',
      subtitle: '选中采集任务后，这里会固定展示任务状态、区域、资源和补偿建议。',
      statusLabel: '待选择',
      statusTone: 'info',
      detailItems: [
        { label: '当前状态', value: '请先选择采集任务' },
        { label: '任务类型', value: '数据采集' },
        { label: '区域与资源', value: '账号 -- / 素材 -- / 代理 --' },
      ],
      adviceItems: [],
    };
  }

  const linkedAccount = accounts.find((item) => item.username === record.accountLabel);
  const regionAssets = assets.filter((item) => item.accountId === linkedAccount?.id || item.accountId == null).length;
  const healthyDevices = devices.filter((item) => normalizeDeviceHealth(item) === 'success').length;

  return {
    title: record.title,
    subtitle: record.summary,
    statusLabel: record.statusLabel,
    statusTone: record.statusTone,
    detailItems: [
      { label: '当前状态', value: record.statusLabel },
      { label: '任务类型', value: record.taskTypeLabel },
      { label: '区域', value: record.regionLabel },
      { label: '绑定账号', value: record.accountLabel },
      { label: '优先级', value: record.priorityLabel },
      { label: '最近时间', value: record.timeLabel },
      { label: '资源摘要', value: `素材 ${regionAssets} / 可用代理设备 ${healthyDevices}` },
    ],
    adviceItems: buildAdviceItems(record, tasks, assets, devices),
  };
}

export function buildCollectorProxySummary(devices: DeviceItem[]): CollectorProxySummary {
  const abnormalDevices = devices.filter((item) => normalizeDeviceHealth(item) === 'error').length;
  const proxyReadyDevices = devices.filter((item) => Boolean(String(item.proxyIp || '').trim())).length;
  const regionCount = new Set(devices.map((item) => item.region).filter(Boolean)).size;

  return {
    title: '代理池摘要',
    subtitle: '基于真实设备、代理和区域状态聚合生成。',
    metrics: [
      { label: '设备总数', value: String(devices.length), tone: 'info' },
      { label: '异常设备', value: String(abnormalDevices), tone: abnormalDevices > 0 ? 'error' : 'success' },
      { label: '代理设备', value: String(proxyReadyDevices), tone: proxyReadyDevices > 0 ? 'success' : 'warning' },
      { label: '区域覆盖', value: `${regionCount} 个`, tone: regionCount > 0 ? 'info' : 'warning' },
    ],
    deviceRows: devices.slice(0, 6).map((item) => ({
      id: item.id,
      name: item.name || item.deviceCode,
      region: item.region || '未分配区域',
      statusLabel: mapDeviceStatusLabel(item),
      statusTone: normalizeDeviceHealth(item),
      proxyLabel: item.proxyIp || '未配置代理',
    })),
  };
}

export function buildCollectorKanbanColumns(records: CollectorRecord[]): CollectorKanbanColumn[] {
  return KANBAN_ORDER.map((status) => ({
    key: status,
    title: mapCollectorStatusLabel(status),
    tone: mapCollectorStatusTone(status),
    records: records.filter((item) => normalizeStatus(item.status) === status),
  }));
}
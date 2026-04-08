export type CollectorStatusTone = 'info' | 'success' | 'warning' | 'error';

export type CollectorViewMode = 'table' | 'kanban';

export interface CollectorMetricCard {
  label: string;
  value: string;
  delta: string;
  note: string;
  tone: CollectorStatusTone;
}

export interface CollectorRecord {
  id: number;
  title: string;
  taskType: string;
  taskTypeLabel: string;
  status: string;
  statusLabel: string;
  statusTone: CollectorStatusTone;
  priority: string;
  priorityLabel: string;
  accountLabel: string;
  regionLabel: string;
  timeLabel: string;
  summary: string;
}

export interface CollectorDetailItem {
  label: string;
  value: string;
  stacked?: boolean;
}

export interface CollectorAdviceItem {
  title: string;
  copy: string;
  badge: string;
  tone: CollectorStatusTone;
}

export interface CollectorDetailViewModel {
  title: string;
  subtitle: string;
  statusLabel: string;
  statusTone: CollectorStatusTone;
  detailItems: CollectorDetailItem[];
  adviceItems: CollectorAdviceItem[];
}

export interface CollectorProxyMetric {
  label: string;
  value: string;
  tone: CollectorStatusTone;
}

export interface CollectorProxyDeviceRow {
  id: number;
  name: string;
  region: string;
  statusLabel: string;
  statusTone: CollectorStatusTone;
  proxyLabel: string;
}

export interface CollectorProxySummary {
  title: string;
  subtitle: string;
  metrics: CollectorProxyMetric[];
  deviceRows: CollectorProxyDeviceRow[];
}

export interface CollectorKanbanColumn {
  key: string;
  title: string;
  tone: CollectorStatusTone;
  records: CollectorRecord[];
}
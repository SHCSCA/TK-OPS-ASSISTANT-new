export type PublishStatusTone = 'info' | 'success' | 'warning' | 'error';

export type PublishViewMode = 'list' | 'calendar';

export interface PublishMetricCard {
  label: string;
  value: string;
  delta: string;
  note: string;
  tone: PublishStatusTone;
}

export interface PublishRecord {
  id: number;
  title: string;
  status: string;
  statusLabel: string;
  statusTone: PublishStatusTone;
  priority: string;
  timeLabel: string;
  scheduledAt: string | null;
  platformLabel: string;
  accountLabel: string;
  summary: string;
  calendarDateKey: string;
}

export interface PublishDetailItem {
  label: string;
  value: string;
  stacked?: boolean;
}

export interface PublishAdviceItem {
  title: string;
  copy: string;
  badge: string;
  tone: PublishStatusTone;
}

export interface PublishDetailViewModel {
  title: string;
  subtitle: string;
  statusLabel: string;
  statusTone: PublishStatusTone;
  detailItems: PublishDetailItem[];
  adviceItems: PublishAdviceItem[];
}

export interface PublishCalendarSlot {
  id: number;
  title: string;
  timeLabel: string;
  tone: PublishStatusTone;
}

export interface PublishCalendarDay {
  key: string;
  label: string;
  isToday: boolean;
  slots: PublishCalendarSlot[];
}
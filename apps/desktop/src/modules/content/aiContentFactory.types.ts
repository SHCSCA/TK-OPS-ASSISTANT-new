export type AiContentFactoryStatusTone = 'info' | 'success' | 'warning' | 'error';

export type AiContentFactoryNodeKey = 'input' | 'script' | 'voice' | 'edit' | 'export';

export interface AiContentFactorySummaryChip {
  label: string;
  value: string;
  note: string;
}

export interface AiContentFactoryNodePaletteItem {
  key: AiContentFactoryNodeKey;
  label: string;
}

export interface AiContentFactoryWorkflowStage {
  key: AiContentFactoryNodeKey;
  title: string;
  badge: string;
  tone: AiContentFactoryStatusTone;
  desc: string;
  meta: string;
  active?: boolean;
}

export interface AiContentFactoryBatchCard {
  title: string;
  badge: string;
  tone: AiContentFactoryStatusTone;
  desc: string;
}

export interface AiContentFactoryConfigItem {
  label: string;
  value: string;
}

export interface AiContentFactoryDetailItem {
  label: string;
  value: string;
  stacked?: boolean;
}

export interface AiContentFactoryAdviceItem {
  title: string;
  copy: string;
  badge: string;
  tone: AiContentFactoryStatusTone;
}

export interface AiContentFactoryDetailViewModel {
  title: string;
  subtitle: string;
  statusLabel: string;
  statusTone: AiContentFactoryStatusTone;
  detailItems: AiContentFactoryDetailItem[];
  adviceItems: AiContentFactoryAdviceItem[];
}
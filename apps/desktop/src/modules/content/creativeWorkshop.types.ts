export type CreativeStatusTone = 'info' | 'success' | 'warning' | 'error';

export type CreativeRailKey = 'theme' | 'shot' | 'voice' | 'export';

export interface CreativeSummaryChip {
  label: string;
  value: string;
  note: string;
}

export interface CreativeRailTool {
  key: CreativeRailKey;
  icon: string;
  label: string;
}

export interface CreativeFocusCard {
  title: string;
  badge: string;
  tone: CreativeStatusTone;
  desc: string;
  meta: string;
  wide?: boolean;
}

export interface CreativeSideCard {
  title: string;
  badge: string;
  tone: CreativeStatusTone;
  desc: string;
  routeName?: string;
}

export interface CreativeStripCard {
  title: string;
  badge: string;
  tone: CreativeStatusTone;
  desc: string;
}

export interface CreativeCompareRow {
  projectId: number;
  title: string;
  viewLabel: string;
  statusLabel: string;
  statusTone: CreativeStatusTone;
  assetLabel: string;
  feedbackLabel: string;
  recommendation: string;
}

export interface CreativeDetailItem {
  label: string;
  value: string;
  stacked?: boolean;
}

export interface CreativeAdviceItem {
  title: string;
  copy: string;
  badge: string;
  tone: CreativeStatusTone;
}

export interface CreativeDetailViewModel {
  title: string;
  subtitle: string;
  statusLabel: string;
  statusTone: CreativeStatusTone;
  detailItems: CreativeDetailItem[];
  adviceItems: CreativeAdviceItem[];
}
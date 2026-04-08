export type VideoEditorTone = 'info' | 'success' | 'warning' | 'error';
export type VideoInspectorTab = 'properties' | 'subtitles' | 'exports';

export interface VideoEditorSummaryChip {
  label: string;
  value: string;
  note: string;
}

export interface VideoEditorAssetCard {
  id: number;
  title: string;
  meta: string;
  badge: string;
  tone: VideoEditorTone;
  selected: boolean;
}

export interface VideoEditorTimelineItem {
  id: number;
  label: string;
  meta: string;
  tone: VideoEditorTone;
  selected: boolean;
}

export interface VideoEditorTimelineLane {
  key: string;
  title: string;
  emptyText: string;
  items: VideoEditorTimelineItem[];
}

export interface VideoEditorQueueCard {
  title: string;
  desc: string;
  badge: string;
  tone: VideoEditorTone;
}

export interface VideoEditorDetailItem {
  label: string;
  value: string;
  stacked?: boolean;
}

export interface VideoEditorAdviceItem {
  title: string;
  copy: string;
  badge: string;
  tone: VideoEditorTone;
}

export interface VideoEditorDetailViewModel {
  title: string;
  subtitle: string;
  statusLabel: string;
  statusTone: VideoEditorTone;
  detailItems: VideoEditorDetailItem[];
  adviceItems: VideoEditorAdviceItem[];
  canExportFinal: boolean;
  canPreviewExport: boolean;
  canSaveSnapshot: boolean;
  canRestoreSnapshot: boolean;
  canCreateSubtitle: boolean;
}
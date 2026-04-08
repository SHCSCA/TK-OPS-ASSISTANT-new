import { computed, onBeforeUnmount, ref } from 'vue';

import type { AssetItem } from '../assets/assetCenter.types';
import { runtimeApi } from '../runtime/runtimeApi';
import type {
  TaskItem,
  VideoClipItem,
  VideoExportItem,
  VideoProjectItem,
  VideoSequenceItem,
  VideoSnapshotItem,
  VideoSubtitleItem,
} from '../runtime/types';
import { useShellStore } from '../shell/useShellStore';
import {
  buildVideoEditorAssetCards,
  buildVideoEditorDetail,
  buildVideoEditorInspectorItems,
  buildVideoEditorQueueCards,
  buildVideoEditorSummaryChips,
  buildVideoEditorTimelineLanes,
  videoStatusLabel,
} from './videoEditor.helpers';
import type { VideoInspectorTab } from './videoEditor.types';

type DetailAction = 'export-final' | 'export-preview' | 'save-snapshot' | 'restore-snapshot' | 'create-subtitle' | 'switch-sequence';

const DEFAULT_PROJECT_NAME = '新建视频工程';

function errorMessageOf(cause: unknown, fallback: string): string {
  return cause instanceof Error ? cause.message : fallback;
}

export function useVideoEditorData() {
  const shell = useShellStore();

  const loading = ref(true);
  const error = ref('');
  const actionError = ref('');
  const actionMessage = ref('');
  const exporting = ref(false);
  const switchingSequence = ref(false);
  const savingSnapshot = ref(false);
  const selectedProjectId = ref<number | null>(null);
  const selectedSequenceId = ref<number | null>(null);
  const selectedAssetId = ref<number | null>(null);
  const selectedClipId = ref<number | null>(null);
  const selectedSubtitleId = ref<number | null>(null);
  const selectedSnapshotId = ref<number | null>(null);
  const inspectorTab = ref<VideoInspectorTab>('properties');
  const playheadMs = ref(0);

  const assets = ref<AssetItem[]>([]);
  const tasks = ref<TaskItem[]>([]);
  const projects = ref<VideoProjectItem[]>([]);
  const sequences = ref<VideoSequenceItem[]>([]);
  const clips = ref<VideoClipItem[]>([]);
  const subtitles = ref<VideoSubtitleItem[]>([]);
  const exports = ref<VideoExportItem[]>([]);
  const snapshots = ref<VideoSnapshotItem[]>([]);

  const selectedProject = computed(() => projects.value.find((item) => item.id === selectedProjectId.value) || null);
  const selectedSequence = computed(() => sequences.value.find((item) => item.id === selectedSequenceId.value) || null);
  const selectedAsset = computed(() => assets.value.find((item) => item.id === selectedAssetId.value) || null);
  const selectedClip = computed(() => clips.value.find((item) => item.id === selectedClipId.value) || null);
  const selectedSubtitle = computed(() => subtitles.value.find((item) => item.id === selectedSubtitleId.value) || null);
  const selectedSnapshot = computed(() => snapshots.value.find((item) => item.id === selectedSnapshotId.value) || snapshots.value[0] || null);

  const summaryChips = computed(() => buildVideoEditorSummaryChips(selectedProject.value, selectedSequence.value, clips.value, exports.value));
  const assetCards = computed(() => buildVideoEditorAssetCards(assets.value, selectedAssetId.value));
  const timelineLanes = computed(() => buildVideoEditorTimelineLanes(clips.value, subtitles.value, assets.value, selectedClipId.value, selectedSubtitleId.value));
  const queueCards = computed(() => buildVideoEditorQueueCards(tasks.value, exports.value, snapshots.value));
  const inspectorItems = computed(() => buildVideoEditorInspectorItems(
    inspectorTab.value,
    selectedProject.value,
    selectedSequence.value,
    selectedAsset.value,
    selectedClip.value,
    selectedSubtitle.value,
    exports.value,
    snapshots.value,
  ));
  const detail = computed(() => buildVideoEditorDetail(
    selectedProject.value,
    selectedSequence.value,
    selectedAsset.value,
    selectedClip.value,
    selectedSubtitle.value,
    exports.value,
    snapshots.value,
    tasks.value,
  ));

  function syncDetailState(): void {
    shell.setVideoEditorDetailState({
      kind: selectedProject.value ? 'selected' : 'default',
      projectId: selectedProject.value?.id ?? null,
      sequenceId: selectedSequence.value?.id ?? null,
      title: detail.value.title,
      subtitle: detail.value.subtitle,
      statusLabel: detail.value.statusLabel,
      statusTone: detail.value.statusTone,
      detailItems: detail.value.detailItems,
      adviceItems: detail.value.adviceItems,
      canExportFinal: detail.value.canExportFinal,
      canPreviewExport: detail.value.canPreviewExport,
      canSaveSnapshot: detail.value.canSaveSnapshot,
      canRestoreSnapshot: detail.value.canRestoreSnapshot,
      canCreateSubtitle: detail.value.canCreateSubtitle,
    });
  }

  function normalizeProjectSelection(): void {
    if (typeof selectedProjectId.value === 'number' && projects.value.some((item) => item.id === selectedProjectId.value)) {
      return;
    }
    selectedProjectId.value = projects.value[0]?.id ?? null;
  }

  function normalizeSequenceSelection(): void {
    if (typeof selectedSequenceId.value === 'number' && sequences.value.some((item) => item.id === selectedSequenceId.value)) {
      return;
    }
    selectedSequenceId.value = sequences.value.find((item) => item.isActive)?.id ?? sequences.value[0]?.id ?? null;
  }

  function normalizeClipSelection(): void {
    if (typeof selectedClipId.value === 'number' && clips.value.some((item) => item.id === selectedClipId.value)) {
      return;
    }
    selectedClipId.value = clips.value[0]?.id ?? null;
  }

  function normalizeSubtitleSelection(): void {
    if (typeof selectedSubtitleId.value === 'number' && subtitles.value.some((item) => item.id === selectedSubtitleId.value)) {
      return;
    }
    selectedSubtitleId.value = subtitles.value[0]?.id ?? null;
  }

  async function loadSequenceContext(sequenceId: number | null): Promise<void> {
    if (typeof sequenceId !== 'number') {
      clips.value = [];
      subtitles.value = [];
      selectedClipId.value = null;
      selectedSubtitleId.value = null;
      syncDetailState();
      return;
    }

    const [clipsResponse, subtitlesResponse] = await Promise.all([
      runtimeApi.listVideoClips(sequenceId),
      runtimeApi.listVideoSubtitles(sequenceId),
    ]);

    clips.value = clipsResponse.items;
    subtitles.value = subtitlesResponse.items;
    normalizeClipSelection();
    normalizeSubtitleSelection();
    if (selectedClip.value) {
      playheadMs.value = selectedClip.value.startMs;
    }
    syncDetailState();
  }

  async function loadProjectContext(projectId: number | null): Promise<void> {
    if (typeof projectId !== 'number') {
      sequences.value = [];
      clips.value = [];
      subtitles.value = [];
      exports.value = [];
      snapshots.value = [];
      selectedSequenceId.value = null;
      selectedClipId.value = null;
      selectedSubtitleId.value = null;
      selectedSnapshotId.value = null;
      syncDetailState();
      return;
    }

    const [sequencesResponse, exportsResponse, snapshotsResponse] = await Promise.all([
      runtimeApi.listVideoSequences(projectId),
      runtimeApi.listVideoExports(projectId),
      runtimeApi.listVideoSnapshots(projectId),
    ]);

    sequences.value = sequencesResponse.items;
    exports.value = exportsResponse.items;
    snapshots.value = snapshotsResponse.items;
    normalizeSequenceSelection();
    selectedSnapshotId.value = selectedSnapshot.value?.id ?? null;
    await loadSequenceContext(selectedSequenceId.value);
  }

  async function reload(): Promise<void> {
    loading.value = true;
    error.value = '';
    actionError.value = '';

    try {
      const [projectsResponse, assetsResponse, tasksResponse] = await Promise.all([
        runtimeApi.listVideoProjects(),
        runtimeApi.listAssets(),
        runtimeApi.listTasks(),
      ]);

      projects.value = projectsResponse.items;
      assets.value = (assetsResponse.items || []) as AssetItem[];
      tasks.value = tasksResponse.items;
      normalizeProjectSelection();
      if (!selectedAssetId.value && assets.value.length) {
        selectedAssetId.value = assets.value[0].id;
      }
      await loadProjectContext(selectedProjectId.value);
    } catch (cause) {
      error.value = errorMessageOf(cause, '加载视频编辑页面失败');
    } finally {
      loading.value = false;
    }
  }

  async function ensureProjectSequence(): Promise<{ project: VideoProjectItem; sequence: VideoSequenceItem }> {
    let project = selectedProject.value;
    if (!project) {
      const createdProject = await runtimeApi.createVideoProject({ name: `${DEFAULT_PROJECT_NAME} ${projects.value.length + 1}` });
      selectedProjectId.value = createdProject.id;
      project = createdProject;
    }

    let sequence = selectedSequence.value;
    if (!sequence || sequence.projectId !== project.id) {
      const createdSequence = await runtimeApi.createVideoSequence({ projectId: project.id, name: sequences.value.length ? `序列 ${sequences.value.length + 1}` : '主序列' });
      await runtimeApi.setActiveVideoSequence(project.id, createdSequence.id);
      selectedSequenceId.value = createdSequence.id;
      sequence = createdSequence;
    }

    await reload();
    return {
      project: projects.value.find((item) => item.id === project?.id) || project,
      sequence: sequences.value.find((item) => item.id === sequence?.id) || sequence,
    };
  }

  function selectProject(project: VideoProjectItem): void {
    selectedProjectId.value = project.id;
    void loadProjectContext(project.id);
  }

  function selectSequence(sequence: VideoSequenceItem): void {
    selectedSequenceId.value = sequence.id;
    playheadMs.value = 0;
    void loadSequenceContext(sequence.id);
  }

  function selectAsset(assetId: number): void {
    selectedAssetId.value = assetId;
    selectedSubtitleId.value = null;
  }

  function selectClip(clipId: number): void {
    selectedClipId.value = clipId;
    selectedSubtitleId.value = null;
    const clip = clips.value.find((item) => item.id === clipId);
    if (clip) {
      playheadMs.value = clip.startMs;
    }
    syncDetailState();
  }

  function selectSubtitle(subtitleId: number): void {
    selectedSubtitleId.value = subtitleId;
    selectedClipId.value = null;
    const subtitle = subtitles.value.find((item) => item.id === subtitleId);
    if (subtitle) {
      playheadMs.value = subtitle.startMs;
    }
    syncDetailState();
  }

  function selectSnapshot(snapshotId: number): void {
    selectedSnapshotId.value = snapshotId;
    syncDetailState();
  }

  function setInspectorTab(tab: VideoInspectorTab): void {
    inspectorTab.value = tab;
  }

  function resetPlayhead(): void {
    playheadMs.value = 0;
  }

  function stepPlayhead(deltaMs = 40): void {
    playheadMs.value = Math.max(0, playheadMs.value + deltaMs);
  }

  async function appendAssetToSequence(assetId: number): Promise<void> {
    actionError.value = '';
    actionMessage.value = '';
    try {
      const { sequence } = await ensureProjectSequence();
      await runtimeApi.appendAssetsToSequence(sequence.id, { assetIds: [assetId] });
      selectedAssetId.value = assetId;
      actionMessage.value = '素材已加入当前剪辑序列。';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '导入素材失败');
    }
  }

  async function switchSequence(): Promise<void> {
    if (switchingSequence.value) {
      return;
    }
    switchingSequence.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      const { project, sequence } = await ensureProjectSequence();
      if (sequences.value.length <= 1) {
        const created = await runtimeApi.createVideoSequence({ projectId: project.id, name: `序列 ${sequences.value.length + 1}` });
        await runtimeApi.setActiveVideoSequence(project.id, created.id);
        selectedSequenceId.value = created.id;
        actionMessage.value = `已创建并切换到 ${created.name}。`;
      } else {
        const currentIndex = sequences.value.findIndex((item) => item.id === sequence.id);
        const next = sequences.value[(currentIndex + 1 + sequences.value.length) % sequences.value.length];
        await runtimeApi.setActiveVideoSequence(project.id, next.id);
        selectedSequenceId.value = next.id;
        actionMessage.value = `已切换到 ${next.name}。`;
      }
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '切换剪辑序列失败');
    } finally {
      switchingSequence.value = false;
    }
  }

  async function trimSelectedClip(edge: 'in' | 'out'): Promise<void> {
    if (!selectedClip.value) {
      actionError.value = '请先选中一个时间轴片段。';
      return;
    }
    const clip = selectedClip.value;
    const clipStart = clip.startMs;
    const offset = Math.max(0, playheadMs.value - clipStart);
    const maxDuration = Math.max(clip.sourceOutMs || 0, clip.durationMs || 0);
    const nextIn = edge === 'in'
      ? Math.min(Math.max(0, clip.sourceInMs + offset), Math.max(0, clip.sourceOutMs - 40))
      : clip.sourceInMs;
    const nextOut = edge === 'out'
      ? Math.max(clip.sourceInMs + 40, Math.min(maxDuration, clip.sourceInMs + offset))
      : clip.sourceOutMs;

    try {
      await runtimeApi.trimVideoClip({ clipId: clip.id, sourceInMs: nextIn, sourceOutMs: nextOut });
      actionMessage.value = edge === 'in' ? '片段入点已更新。' : '片段出点已更新。';
      actionError.value = '';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '裁切片段失败');
    }
  }

  async function moveSelectedClip(direction: 'left' | 'right'): Promise<void> {
    if (!selectedClip.value || !selectedSequence.value) {
      actionError.value = '请先选中一个时间轴片段。';
      return;
    }
    const ids = clips.value.map((item) => item.id);
    const currentIndex = ids.indexOf(selectedClip.value.id);
    if (currentIndex < 0) {
      return;
    }
    const swapIndex = direction === 'left' ? currentIndex - 1 : currentIndex + 1;
    if (swapIndex < 0 || swapIndex >= ids.length) {
      return;
    }
    [ids[currentIndex], ids[swapIndex]] = [ids[swapIndex], ids[currentIndex]];
    try {
      await runtimeApi.reorderVideoClips({ sequenceId: selectedSequence.value.id, clipIds: ids });
      actionMessage.value = direction === 'left' ? '片段已左移。' : '片段已右移。';
      actionError.value = '';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '调整片段顺序失败');
    }
  }

  async function deleteSelectedClip(): Promise<void> {
    if (!selectedClip.value) {
      actionError.value = '请先选中一个时间轴片段。';
      return;
    }
    if (!window.confirm('确定删除当前片段吗？')) {
      return;
    }
    try {
      await runtimeApi.deleteVideoClip(selectedClip.value.id);
      actionMessage.value = '片段已删除。';
      actionError.value = '';
      selectedClipId.value = null;
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '删除片段失败');
    }
  }

  async function createSubtitle(): Promise<void> {
    actionError.value = '';
    actionMessage.value = '';
    try {
      const { sequence } = await ensureProjectSequence();
      const text = window.prompt('请输入字幕内容', selectedSubtitle.value?.text || '新字幕');
      if (!text || !text.trim()) {
        return;
      }
      const baseStart = selectedClip.value?.startMs ?? playheadMs.value;
      const baseEnd = selectedClip.value ? selectedClip.value.startMs + Math.min(selectedClip.value.durationMs, 3000) : baseStart + 2000;
      const item = await runtimeApi.createVideoSubtitle({
        sequenceId: sequence.id,
        startMs: baseStart,
        endMs: baseEnd,
        text: text.trim(),
      });
      selectedSubtitleId.value = item.id;
      inspectorTab.value = 'subtitles';
      actionMessage.value = '字幕已创建。';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '创建字幕失败');
    }
  }

  async function editSubtitle(): Promise<void> {
    if (!selectedSubtitle.value) {
      actionError.value = '请先选中一条字幕。';
      return;
    }
    const text = window.prompt('编辑字幕内容', selectedSubtitle.value.text || '');
    if (!text || !text.trim()) {
      return;
    }
    try {
      await runtimeApi.updateVideoSubtitle(selectedSubtitle.value.id, { text: text.trim() });
      actionMessage.value = '字幕已更新。';
      actionError.value = '';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '更新字幕失败');
    }
  }

  async function deleteSubtitle(): Promise<void> {
    if (!selectedSubtitle.value) {
      actionError.value = '请先选中一条字幕。';
      return;
    }
    if (!window.confirm('确定删除当前字幕吗？')) {
      return;
    }
    try {
      await runtimeApi.deleteVideoSubtitle(selectedSubtitle.value.id);
      actionMessage.value = '字幕已删除。';
      actionError.value = '';
      selectedSubtitleId.value = null;
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '删除字幕失败');
    }
  }

  async function saveSnapshot(): Promise<void> {
    if (savingSnapshot.value) {
      return;
    }
    savingSnapshot.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      const { project } = await ensureProjectSequence();
      const title = window.prompt('请输入快照标题', selectedSnapshot.value?.title || '编辑快照');
      if (!title || !title.trim()) {
        return;
      }
      const snapshot = await runtimeApi.createVideoSnapshot({ projectId: project.id, title: title.trim() });
      selectedSnapshotId.value = snapshot.id;
      actionMessage.value = '快照已保存。';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '保存快照失败');
    } finally {
      savingSnapshot.value = false;
    }
  }

  async function restoreSnapshot(): Promise<void> {
    if (!selectedSnapshot.value) {
      actionError.value = '当前没有可恢复的快照。';
      return;
    }
    try {
      await runtimeApi.restoreVideoSnapshot(selectedSnapshot.value.id);
      actionMessage.value = '快照已恢复。';
      actionError.value = '';
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, '恢复快照失败');
    }
  }

  async function runExport(preset: 'final' | 'preview'): Promise<void> {
    if (exporting.value) {
      return;
    }
    exporting.value = true;
    actionError.value = '';
    actionMessage.value = '';
    try {
      const { project, sequence } = await ensureProjectSequence();
      const exportRow = await runtimeApi.createVideoExport({ projectId: project.id, sequenceId: sequence.id, preset });
      const result = await runtimeApi.runVideoExport(exportRow.id);
      actionMessage.value = `${preset === 'final' ? '发起终版导出' : '试看导出'}已完成：${videoStatusLabel(result.status)}`;
      await reload();
    } catch (cause) {
      actionError.value = errorMessageOf(cause, preset === 'final' ? '发起终版导出失败' : '试看导出失败');
    } finally {
      exporting.value = false;
    }
  }

  function onDetailAction(event: Event): void {
    const customEvent = event as CustomEvent<{ action?: DetailAction }>;
    const action = customEvent.detail?.action;
    if (action === 'export-final') {
      void runExport('final');
      return;
    }
    if (action === 'export-preview') {
      void runExport('preview');
      return;
    }
    if (action === 'save-snapshot') {
      void saveSnapshot();
      return;
    }
    if (action === 'restore-snapshot') {
      void restoreSnapshot();
      return;
    }
    if (action === 'create-subtitle') {
      void createSubtitle();
      return;
    }
    if (action === 'switch-sequence') {
      void switchSequence();
    }
  }

  window.addEventListener('tkops:video-editor-detail-action', onDetailAction as EventListener);
  void reload();

  onBeforeUnmount(() => {
    window.removeEventListener('tkops:video-editor-detail-action', onDetailAction as EventListener);
    shell.resetVideoEditorDetailState();
  });

  return {
    actionError,
    actionMessage,
    assetCards,
    clips,
    createSubtitle,
    deleteSelectedClip,
    deleteSubtitle,
    detail,
    editSubtitle,
    error,
    exports,
    exporting,
    inspectorItems,
    inspectorTab,
    loading,
    playheadMs,
    projects,
    queueCards,
    reload,
    resetPlayhead,
    runExport,
    saveSnapshot,
    savingSnapshot,
    selectAsset,
    selectClip,
    selectProject,
    selectSequence,
    selectSnapshot,
    selectSubtitle,
    selectedAsset,
    selectedClip,
    selectedProject,
    selectedProjectId,
    selectedSequence,
    selectedSequenceId,
    selectedSnapshot,
    selectedSubtitle,
    sequences,
    setInspectorTab,
    snapshots,
    stepPlayhead,
    summaryChips,
    switchSequence,
    switchingSequence,
    timelineLanes,
    trimSelectedClip,
    moveSelectedClip,
    appendAssetToSequence,
    restoreSnapshot,
  };
}
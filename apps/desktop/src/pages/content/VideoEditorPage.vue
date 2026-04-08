<template>
  <section class="video-editor-page" data-page-audit="video-editor">
    <div class="resource-header video-editor-header">
      <div>
        <p class="eyebrow">P0</p>
        <h2>视频编辑</h2>
        <p class="resource-subtitle">围绕工程、序列、片段、字幕、快照和导出重建真实视频编辑页，不再保留占位时间线和冻结批次文案。</p>
      </div>
      <div class="video-editor-header__actions">
        <button class="dashboard-refresh" type="button" @click="reload">刷新</button>
        <button class="secondary-button" type="button" :disabled="switchingSequence" @click="switchSequence">{{ switchingSequence ? '正在切换...' : '切换剪辑序列' }}</button>
        <button class="secondary-button" type="button" :disabled="exporting" @click="runExport('preview')">{{ exporting ? '正在导出...' : '试看导出' }}</button>
        <button class="primary-button" type="button" :disabled="exporting" @click="runExport('final')">{{ exporting ? '正在导出...' : '发起终版导出' }}</button>
      </div>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载视频工程、序列、素材、时间线、字幕和导出记录...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>
    <template v-else>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-else-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>

      <div class="workbench-summary-strip video-editor-summary-strip">
        <article v-for="chip in summaryChips" :key="chip.label" class="workbench-summary-chip">
          <span class="subtle">{{ chip.label }}</span>
          <strong>{{ chip.value }}</strong>
          <small>{{ chip.note }}</small>
        </article>
      </div>

      <section class="video-editor-shell">
        <aside class="video-editor-library-column">
          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>视频工程</strong>
                <div class="subtle">左列用于切换工程和序列，不把工程态藏到弹窗里。</div>
              </div>
            </div>
            <div v-if="projects.length" class="video-project-list">
              <button
                v-for="project in projects"
                :key="project.id"
                type="button"
                class="video-project-item"
                :class="{ 'is-selected': project.id === selectedProjectId }"
                @click="selectProject(project)"
              >
                <div>
                  <strong>{{ project.name }}</strong>
                  <div class="subtle">{{ project.description || '当前工程暂无补充说明。' }}</div>
                </div>
                <span class="pill" :class="project.id === selectedProjectId ? 'success' : 'info'">{{ project.id === selectedProjectId ? '当前工程' : '切换' }}</span>
              </button>
            </div>
            <p v-else class="dashboard-empty">暂无视频工程，导入素材或发起导出前会自动创建第一个工程。</p>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>素材库</strong>
                <div class="subtle">单击只切换预览，双击才把素材挂入当前序列。</div>
              </div>
            </div>
            <div class="video-asset-grid">
              <button
                v-for="asset in assetCards"
                :key="asset.id"
                type="button"
                class="video-asset-card"
                :class="{ 'is-selected': asset.selected }"
                @click="selectAsset(asset.id)"
                @dblclick="appendAssetToSequence(asset.id)"
              >
                <strong>{{ asset.title }}</strong>
                <div class="subtle">{{ asset.meta }}</div>
                <span class="pill" :class="asset.tone">{{ asset.badge }}</span>
              </button>
            </div>
          </section>
        </aside>

        <div class="video-editor-canvas-column">
          <section class="panel video-preview-panel">
            <div class="panel__header">
              <div>
                <strong>节目监视器</strong>
                <div class="subtle">当前聚焦对象会同步更新到中区预览与右栏详情。</div>
              </div>
              <div class="video-preview-panel__meta">
                <span class="pill info">播放头 {{ playheadMs }} ms</span>
                <span class="pill success">{{ selectedSequence?.name || '未选择序列' }}</span>
              </div>
            </div>
            <div class="video-preview-stage">
              <div class="video-preview-stage__surface">
                <strong>{{ selectedSubtitle?.text || selectedAsset?.filename || (selectedClip ? `片段 #${selectedClip.id}` : '等待选择素材或片段') }}</strong>
                <div class="subtle">{{ detail.subtitle }}</div>
              </div>
              <div class="video-transport-bar">
                <button class="secondary-button" type="button" @click="resetPlayhead">回到开头</button>
                <button class="secondary-button" type="button" @click="stepPlayhead(40)">逐帧</button>
                <button class="secondary-button" type="button" :disabled="!selectedClip" @click="trimSelectedClip('in')">设入点</button>
                <button class="secondary-button" type="button" :disabled="!selectedClip" @click="trimSelectedClip('out')">设出点</button>
                <button class="secondary-button" type="button" :disabled="!selectedClip" @click="moveSelectedClip('left')">左移片段</button>
                <button class="secondary-button" type="button" :disabled="!selectedClip" @click="moveSelectedClip('right')">右移片段</button>
                <button class="danger-button" type="button" :disabled="!selectedClip" @click="deleteSelectedClip">删除片段</button>
              </div>
            </div>
          </section>

          <section class="panel video-timeline-panel">
            <div class="panel__header">
              <div>
                <strong>时间线</strong>
                <div class="subtle">按视频、字幕、音频三条轨道展示真实片段，不再使用占位时间轴。</div>
              </div>
            </div>
            <div class="video-timeline-board">
              <article v-for="lane in timelineLanes" :key="lane.key" class="video-timeline-lane">
                <header>
                  <strong>{{ lane.title }}</strong>
                </header>
                <div v-if="lane.items.length" class="video-timeline-lane__items">
                  <button
                    v-for="item in lane.items"
                    :key="item.id"
                    type="button"
                    class="video-timeline-item"
                    :class="[{ 'is-selected': item.selected }, `tone-${item.tone}`]"
                    @click="lane.key === 'subtitle' ? selectSubtitle(item.id) : selectClip(item.id)"
                  >
                    <strong>{{ item.label }}</strong>
                    <small>{{ item.meta }}</small>
                  </button>
                </div>
                <p v-else class="dashboard-empty">{{ lane.emptyText }}</p>
              </article>
            </div>
          </section>

          <section class="panel video-output-panel">
            <div class="panel__header">
              <div>
                <strong>导出与快照</strong>
                <div class="subtle">中区底部集中展示最近导出和可恢复快照。</div>
              </div>
              <div class="gen-output-actions">
                <button class="secondary-button" type="button" @click="saveSnapshot">保存快照</button>
                <button class="ghost-button" type="button" :disabled="!selectedSnapshot" @click="restoreSnapshot">恢复快照</button>
              </div>
            </div>
            <div class="video-output-grid">
              <article v-for="card in queueCards" :key="card.title" class="strip-card">
                <strong>{{ card.title }}</strong>
                <div class="subtle">{{ card.desc }}</div>
                <span class="pill" :class="card.tone">{{ card.badge }}</span>
              </article>
            </div>
            <div v-if="snapshots.length" class="video-snapshot-list">
              <button
                v-for="snapshot in snapshots"
                :key="snapshot.id"
                type="button"
                class="video-snapshot-item"
                :class="{ 'is-selected': snapshot.id === selectedSnapshot?.id }"
                @click="selectSnapshot(snapshot.id)"
              >
                <strong>{{ snapshot.title }}</strong>
                <small>{{ snapshot.createdAt || '--' }}</small>
              </button>
            </div>
          </section>
        </div>

        <aside class="video-editor-inspector-column">
          <section class="panel video-inspector-panel">
            <div class="panel__header">
              <div>
                <strong>检查器</strong>
                <div class="subtle">根据当前选中对象切换属性、字幕和导出视图。</div>
              </div>
            </div>
            <div class="video-inspector-tabs">
              <button type="button" :class="{ 'is-selected': inspectorTab === 'properties' }" @click="setInspectorTab('properties')">属性</button>
              <button type="button" :class="{ 'is-selected': inspectorTab === 'subtitles' }" @click="setInspectorTab('subtitles')">字幕</button>
              <button type="button" :class="{ 'is-selected': inspectorTab === 'exports' }" @click="setInspectorTab('exports')">导出</button>
            </div>
            <div class="detail-list">
              <div v-for="item in inspectorItems" :key="item.label" class="detail-item" :class="{ 'detail-item--stacked': item.stacked }">
                <span class="subtle">{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <div class="detail-actions account-detail__actions">
              <button class="secondary-button" type="button" @click="createSubtitle">新增字幕</button>
              <button class="secondary-button" type="button" :disabled="!selectedSubtitle" @click="editSubtitle">编辑字幕</button>
              <button class="danger-button" type="button" :disabled="!selectedSubtitle" @click="deleteSubtitle">删除字幕</button>
              <button class="ghost-button" type="button" @click="saveSnapshot">保存快照</button>
            </div>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>右栏摘要</strong>
                <div class="subtle">保持旧壳语义，显示当前序列、焦点对象和风险提醒。</div>
              </div>
            </div>
            <div class="detail-list">
              <div v-for="item in detail.detailItems" :key="item.label" class="detail-item" :class="{ 'detail-item--stacked': item.stacked }">
                <span class="subtle">{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <div class="board-list">
              <article v-for="item in detail.adviceItems" :key="`${item.title}-${item.badge}`" class="board-card">
                <strong>{{ item.title }}</strong>
                <div class="subtle">{{ item.copy }}</div>
                <div class="status-strip"><span class="pill" :class="item.tone">{{ item.badge }}</span></div>
              </article>
            </div>
          </section>
        </aside>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { useVideoEditorData } from '../../modules/content/useVideoEditorData';

const {
  actionError,
  actionMessage,
  assetCards,
  appendAssetToSequence,
  createSubtitle,
  deleteSelectedClip,
  deleteSubtitle,
  detail,
  editSubtitle,
  error,
  exporting,
  inspectorItems,
  inspectorTab,
  loading,
  playheadMs,
  projects,
  queueCards,
  reload,
  resetPlayhead,
  restoreSnapshot,
  runExport,
  saveSnapshot,
  selectedAsset,
  selectedClip,
  selectedProjectId,
  selectedSequence,
  selectedSnapshot,
  selectedSubtitle,
  setInspectorTab,
  selectAsset,
  selectClip,
  selectProject,
  selectSnapshot,
  selectSubtitle,
  stepPlayhead,
  summaryChips,
  switchSequence,
  switchingSequence,
  timelineLanes,
  trimSelectedClip,
  moveSelectedClip,
  snapshots,
} = useVideoEditorData();
</script>
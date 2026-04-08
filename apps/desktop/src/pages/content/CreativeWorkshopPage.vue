<template>
  <section class="creative-workshop-page" data-page-audit="creative-workshop">
    <div class="resource-header creative-workshop-header">
      <div>
        <p class="eyebrow">P1</p>
        <h2>创意工坊</h2>
        <p class="resource-subtitle">围绕主题、镜头、口播和素材组合做创意试验，页面直接接入 experiments / activity / tasks / assets 的真实链路。</p>
      </div>
      <div class="creative-workshop-header__actions">
        <button class="dashboard-refresh" type="button" @click="reload">刷新</button>
        <button class="secondary-button" type="button" @click="toggleCompareMode">{{ compareMode ? '返回实验主视角' : '对比创意版本' }}</button>
        <button class="primary-button" type="button" :disabled="saving || !draftName.trim()" @click="saveCreativePlan">
          {{ saving ? '正在保存...' : '保存创意方案' }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载创意实验、任务反馈和活动日志...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>
    <template v-else>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-else-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>

      <div class="workbench-summary-strip">
        <article v-for="chip in summaryChips" :key="chip.label" class="workbench-summary-chip">
          <span class="subtle">{{ chip.label }}</span>
          <strong>{{ chip.value }}</strong>
          <small>{{ chip.note }}</small>
        </article>
      </div>

      <div class="content-workbench-shell creative-workbench-shell">
        <aside class="workbench-rail creative-workbench-rail">
          <button
            v-for="tool in railTools"
            :key="tool.key"
            class="workbench-tool"
            :class="{ 'is-selected': tool.key === activeRail }"
            type="button"
            @click="setActiveRail(tool.key)"
          >
            <span>{{ tool.icon }}</span>
            <small>{{ tool.label }}</small>
          </button>
        </aside>

        <div class="section-stack creative-workbench-main">
          <section class="dashboard-section creative-toolbar-card">
            <div class="dashboard-section-title">
              <div>
                <h3>创意组合画板</h3>
                <span>{{ compareMode ? '当前处于创意版本对比视图' : '当前处于实验主视角' }}</span>
              </div>
              <button class="ghost-button" type="button" @click="openVideoEditor">进入视频编辑</button>
            </div>
            <div class="creative-draft-grid">
              <label class="copywriter-field">
                <span>方案名称</span>
                <input v-model="draftName" type="text" placeholder="输入创意方案名称" />
              </label>
              <label class="copywriter-field creative-draft-grid__wide">
                <span>创意目标</span>
                <textarea
                  v-model="draftGoal"
                  rows="3"
                  placeholder="输入当前实验目标，例如：验证美区护肤口播 + 近景镜头的保留倾向。"
                />
              </label>
            </div>
          </section>

          <section class="workbench-canvas workbench-canvas--creative">
            <div class="toolbar-strip">
              <div class="toolbar-strip__group">
                <strong>创意组合画板</strong>
                <span class="subtle">主题、镜头、口播和卖点在同一块板上快速组合，对齐旧壳 content workbench 结构。</span>
              </div>
              <div class="toolbar-strip__group">
                <button class="secondary-button" type="button" @click="saveCreativePlan">锁定版本</button>
                <button class="secondary-button" type="button" @click="toggleCompareMode">生成对比</button>
              </div>
            </div>
            <div class="focus-grid" data-creative-workbench-focus>
              <article
                v-for="card in focusCards"
                :key="card.title"
                class="focus-card"
                :class="{ 'focus-card--wide': card.wide }"
              >
                <div class="focus-card__head">
                  <strong>{{ card.title }}</strong>
                  <span class="pill" :class="card.tone">{{ card.badge }}</span>
                </div>
                <div class="subtle">{{ card.desc }}</div>
                <div class="focus-card__meta">{{ card.meta }}</div>
              </article>
            </div>
          </section>

          <section v-if="compareMode" ref="compareBoardRef" class="dashboard-section creative-compare-board">
            <div class="dashboard-section-title">
              <div>
                <h3>创意版本对比</h3>
                <span>这里不再是 toast，而是实际的项目 / 视图对比表。</span>
              </div>
              <span>{{ compareRows.length }} 个实验项目</span>
            </div>
            <div v-if="compareRows.length" class="creative-compare-table">
              <div class="creative-compare-table__head">
                <span>方案</span>
                <span>视图</span>
                <span>状态</span>
                <span>素材</span>
                <span>反馈</span>
                <span>建议</span>
              </div>
              <button
                v-for="row in compareRows"
                :key="row.projectId"
                class="creative-compare-table__row"
                :class="{ 'is-selected': row.projectId === selectedProjectId }"
                type="button"
                @click="selectedProject && row.projectId !== selectedProjectId ? selectProject(projects.find((item) => item.id === row.projectId)!) : undefined"
              >
                <strong>{{ row.title }}</strong>
                <span>{{ row.viewLabel }}</span>
                <span class="pill" :class="row.statusTone">{{ row.statusLabel }}</span>
                <span>{{ row.assetLabel }}</span>
                <span>{{ row.feedbackLabel }}</span>
                <span>{{ row.recommendation }}</span>
              </button>
            </div>
            <p v-else class="dashboard-empty">暂无可对比的实验项目，先保存一条创意方案再进入对比视图。</p>
          </section>

          <section class="dashboard-section">
            <div class="dashboard-section-title">
              <div>
                <h3>实验轨迹</h3>
                <span>已保存实验、待验证项和复盘记录都来自真实项目、视图和活动日志。</span>
              </div>
              <span>{{ selectedProject?.name || '等待项目' }}</span>
            </div>
            <div class="workbench-strip-grid creative-strip-grid">
              <article v-for="card in stripCards" :key="card.title" class="strip-card">
                <strong>{{ card.title }}</strong>
                <div class="subtle">{{ card.desc }}</div>
                <span class="pill" :class="card.tone">{{ card.badge }}</span>
              </article>
            </div>
          </section>
        </div>

        <aside class="workbench-sidebar creative-workbench-side">
          <section class="dashboard-section">
            <div class="dashboard-section-title">
              <div>
                <h3>方案评分</h3>
                <span>右侧不再是通用摘要，而是创意判定、风险检查和移交建议。</span>
              </div>
              <span>{{ selectedProject?.name || '等待项目' }}</span>
            </div>
            <div class="workbench-side-list">
              <button
                v-for="card in sideCards"
                :key="card.title"
                class="workbench-sidecard creative-sidecard"
                type="button"
                @click="card.routeName ? openVideoEditor() : undefined"
              >
                <div class="workbench-sidecard__head">
                  <strong>{{ card.title }}</strong>
                  <span class="pill" :class="card.tone">{{ card.badge }}</span>
                </div>
                <div class="subtle">{{ card.desc }}</div>
              </button>
            </div>
          </section>

          <section class="dashboard-section creative-project-panel">
            <div class="dashboard-section-title">
              <div>
                <h3>实验项目</h3>
                <span>选中某个项目后，右栏详情和主视角会同步切换。</span>
              </div>
              <span>{{ views.length }} 个视图</span>
            </div>
            <div v-if="projects.length" class="creative-project-list">
              <button
                v-for="project in projects"
                :key="project.id"
                class="creative-project-item"
                :class="{ 'is-selected': project.id === selectedProjectId }"
                type="button"
                @click="selectProject(project)"
              >
                <div>
                  <strong>{{ project.name }}</strong>
                  <div class="subtle">{{ project.goal || '当前项目未填写明确目标。' }}</div>
                </div>
                <span class="pill" :class="project.id === selectedProjectId ? 'success' : 'info'">{{ project.id === selectedProjectId ? '当前实验' : '切换' }}</span>
              </button>
            </div>
            <p v-else class="dashboard-empty">暂无实验项目，点击“保存创意方案”后会在这里显示真实项目。</p>
          </section>
        </aside>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { useCreativeWorkshopData } from '../../modules/content/useCreativeWorkshopData';

const {
  actionError,
  actionMessage,
  activeRail,
  compareBoardRef,
  compareMode,
  compareRows,
  draftGoal,
  draftName,
  error,
  focusCards,
  loading,
  openVideoEditor,
  projects,
  railTools,
  reload,
  saveCreativePlan,
  saving,
  selectProject,
  selectedProject,
  selectedProjectId,
  setActiveRail,
  sideCards,
  stripCards,
  summaryChips,
  toggleCompareMode,
  views,
} = useCreativeWorkshopData();
</script>
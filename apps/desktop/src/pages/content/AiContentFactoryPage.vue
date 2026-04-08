<template>
  <section class="ai-content-factory-page" data-page-audit="ai-content-factory">
    <div class="resource-header ai-content-factory-header">
      <div>
        <p class="eyebrow">P1</p>
        <h2>AI 内容工厂</h2>
        <p class="resource-subtitle">按照左组件库、中工作流画布、右节点配置、底部批次状态的旧壳结构重建，并直接接入 workflows / tasks / providers / assets 的真实链路。</p>
      </div>
      <div class="ai-content-factory-header__actions">
        <button class="dashboard-refresh" type="button" @click="reload">刷新</button>
        <button class="secondary-button" type="button" @click="chooseTemplateSet">选择模板集</button>
        <button class="secondary-button" type="button" :disabled="runningWorkflow || !selectedDefinition" @click="runWorkflowDefinition">
          {{ runningWorkflow ? '正在运行工作流...' : '运行工作流' }}
        </button>
        <button class="primary-button" type="button" :disabled="runningBatch" @click="runBatch">
          {{ runningBatch ? '正在启动...' : '启动批量生产' }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="dashboard-banner">正在加载工作流定义、批次状态、任务反馈和 Provider 列表...</p>
    <p v-else-if="error" class="dashboard-banner dashboard-banner-error">{{ error }}</p>
    <template v-else>
      <p v-if="actionError" class="dashboard-banner dashboard-banner-error">{{ actionError }}</p>
      <p v-else-if="actionMessage" class="dashboard-banner">{{ actionMessage }}</p>

      <div class="workbench-summary-strip aicf-summary-strip">
        <article v-for="chip in summaryChips" :key="chip.label" class="workbench-summary-chip">
          <span class="subtle">{{ chip.label }}</span>
          <strong>{{ chip.value }}</strong>
          <small>{{ chip.note }}</small>
        </article>
      </div>

      <section class="aicf-shell">
        <aside class="aicf-library-column">
          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>组件库</strong>
                <div class="subtle">节点只放在左列，不再占据主画布上方。</div>
              </div>
            </div>
            <div class="aicf-node-palette">
              <button
                v-for="node in nodePalette"
                :key="node.key"
                type="button"
                class="aicf-node-palette__button"
                :class="{ 'is-selected': node.key === activeNode }"
                @click="setActiveNode(node.key)"
              >
                {{ node.label }}
              </button>
            </div>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>我的项目</strong>
                <div class="subtle">最近工作流快速切换，右栏详情与画布会一起更新。</div>
              </div>
            </div>
            <div v-if="definitions.length" class="aicf-project-list">
              <button
                v-for="definition in definitions"
                :key="definition.id"
                type="button"
                class="aicf-project-item"
                :class="{ 'is-selected': definition.id === selectedDefinitionId }"
                @click="selectDefinition(definition)"
              >
                <div>
                  <strong>{{ definition.name }}</strong>
                  <div class="subtle">{{ definition.description || '当前工作流未填写说明。' }}</div>
                </div>
                <span class="pill" :class="definition.id === selectedDefinitionId ? 'success' : 'info'">{{ definition.id === selectedDefinitionId ? '当前工作流' : '切换' }}</span>
              </button>
            </div>
            <p v-else class="dashboard-empty">暂无工作流定义，点击“保存工作流”后会在这里显示真实记录。</p>
          </section>
        </aside>

        <div class="aicf-canvas-column">
          <section class="panel aicf-toolbar-panel">
            <div class="panel__header">
              <div>
                <strong>工作流设计</strong>
                <div class="subtle">中区只保留工具栏与节点画布，避免退化成普通 AI 卡片页。</div>
              </div>
              <div class="gen-output-actions ai-content-factory-toolbar__actions">
                <button class="secondary-button" type="button" :disabled="saving || !draftName.trim()" @click="saveWorkflowDefinition">
                  {{ saving ? '正在保存...' : '保存工作流' }}
                </button>
                <button class="primary-button" type="button" :disabled="runningWorkflow || !selectedDefinition" @click="runWorkflowDefinition">
                  {{ runningWorkflow ? '正在运行...' : '运行工作流' }}
                </button>
              </div>
            </div>
            <div class="ai-content-factory-draft-grid">
              <label class="copywriter-field">
                <span>工作流名称</span>
                <input v-model="draftName" type="text" placeholder="输入当前工作流名称" />
              </label>
              <label class="copywriter-field ai-content-factory-draft-grid__wide">
                <span>工作流说明</span>
                <textarea v-model="draftDescription" rows="3" placeholder="输入当前工作流目标，例如：用于内容工厂脚本生成与剪辑批次编排。" />
              </label>
            </div>
          </section>

          <section ref="workflowBoardRef" class="panel aicf-workflow-canvas">
            <div class="aicf-workflow-row">
              <template v-for="(stage, index) in workflowStages" :key="stage.key">
                <article class="workflow-stage-card" :class="[{ 'is-active': stage.active }, `tone-${stage.tone}`]">
                  <div class="workflow-stage-card__head">
                    <strong>{{ stage.title }}</strong>
                    <span class="pill" :class="stage.tone">{{ stage.badge }}</span>
                  </div>
                  <small>{{ stage.desc }}</small>
                  <span class="subtle">{{ stage.meta }}</span>
                </article>
                <span v-if="index < workflowStages.length - 1" class="workflow-arrow">→</span>
              </template>
            </div>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>批次运行状态</strong>
                <div class="subtle">底部集中查看通过率、失败节点和可复用批次，不再写死示例批次号。</div>
              </div>
              <button class="ghost-button" type="button" :disabled="runningBatch" @click="runBatch">运行批次</button>
            </div>
            <div class="aicf-batch-grid">
              <article v-for="card in batchCards" :key="card.title" class="strip-card">
                <strong>{{ card.title }}</strong>
                <div class="subtle">{{ card.desc }}</div>
                <span class="pill" :class="card.tone">{{ card.badge }}</span>
              </article>
            </div>
          </section>
        </div>

        <aside class="aicf-config-column">
          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>节点配置</strong>
                <div class="subtle">右列只给当前选中节点的真实配置摘要。</div>
              </div>
            </div>
            <div class="aicf-config-list">
              <div v-for="item in configItems" :key="item.label" class="aicf-config-item">
                <span class="subtle">{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </section>

          <section class="panel">
            <div class="panel__header">
              <div>
                <strong>当前工作流摘要</strong>
                <div class="subtle">右列保持旧壳语义，只显示当前工作流与最新批次关系。</div>
              </div>
            </div>
            <div class="detail-list">
              <div v-for="item in detail.detailItems" :key="item.label" class="detail-item" :class="{ 'detail-item--stacked': item.stacked }">
                <span class="subtle">{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { useAiContentFactoryData } from '../../modules/content/useAiContentFactoryData';

const {
  actionError,
  actionMessage,
  activeNode,
  batchCards,
  chooseTemplateSet,
  configItems,
  definitions,
  detail,
  draftDescription,
  draftName,
  error,
  loading,
  nodePalette,
  reload,
  runBatch,
  runWorkflowDefinition,
  runningBatch,
  runningWorkflow,
  saveWorkflowDefinition,
  saving,
  selectDefinition,
  selectedDefinition,
  selectedDefinitionId,
  setActiveNode,
  summaryChips,
  workflowBoardRef,
  workflowStages,
} = useAiContentFactoryData();
</script>
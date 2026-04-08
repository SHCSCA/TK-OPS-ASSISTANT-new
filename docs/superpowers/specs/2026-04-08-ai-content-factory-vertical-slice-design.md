# AI 内容工厂垂直切片设计

## 1. 目标

- 将 `ai-content-factory` 从占位路由升级为真实新壳页面。
- 严格复用旧壳 `makeAIContentFactoryRoute()` 与 `workbenchType = 'ai-content-factory'` 的 content workbench / workflow board 语义，不把它降级成普通 AI 生成页。
- 同步补齐新壳 runtime 对 workflow definitions / workflow runs 的 HTTP 契约，让“保存工作流”“运行工作流”走真实持久化链路。
- 页面、右栏详情、runtime API、测试、迁移文档同时落地，避免出现“页面已切换但工作流动作仍是空壳”的半迁移状态。

## 2. 旧壳基线映射

### 2.1 Route 基线

- 旧壳入口：`desktop_app/assets/js/routes.js`
- 页面配置：`ai-content-factory: makeAIContentFactoryRoute()`
- 语义归属：内容与 AI 域中的批量生产工作台，而不是单次标题/文案生成器。
- 核心动作语义：
  - `primaryAction = 保存工作流`
  - `secondaryAction = 运行批次`
  - 额外动作：`运行工作流`
- 业务目标：围绕素材输入、脚本生成、TTS/字幕、批量剪辑和导出构建一条可复用的生产工作流。

### 2.2 Factory 基线

- 旧壳入口：`desktop_app/assets/js/factories/content.js`
- ai-content-factory 不是普通生成页，而是 content workbench 工厂的 workflow 子模式。
- 关键结构：
  - `workbench-summary-strip`
  - `content-workbench-shell`
  - `workbench-rail`
  - `workbench-canvas workbench-canvas--factory`
  - `toolbar-strip`
  - `workflow-board`
  - `workflow-node`
  - `workbench-sidebar`
  - `workbench-side-list`
  - `workbench-strip-grid`
  - `detailHtml`
- 关键块：
  - 顶部摘要条：输入素材、工作流定义、运行批次等状态摘要
  - 中央 workflow board：输入素材 / AI 脚本 / 语音与字幕 / 批量剪辑 等节点
  - 右侧 side cards：节点库、项目区、当前批次状态
  - 底部 strip cards：批次运行状态、失败节点、可回放批次
  - detail cards / detail groups：当前工作流、风险节点、建议动作

### 2.3 Loader 基线

- 旧壳入口：`desktop_app/assets/js/page-loaders.js`
- loader：`loaders['ai-content-factory']`
- 真实数据来源：
  - `api.assets.list()`
  - `api.tasks.list()`
  - `api.providers.list()`
  - `api.workflows.definitions()`
  - `api.workflows.runs()`
- 关键行为：
  - `_renderWorkflowNodes(assets, tasks, providers, definitions, runs)`
  - `_renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list')`
  - `_renderStripCards(runs.length ? runs : tasks, '#mainHost .workbench-strip-grid')`
  - `_applyAiHandoffHint('ai-content-factory', '#mainHost .workbench-strip-grid')`
  - `bindRouteInteractions()`

### 2.4 交互与持久化基线

- 旧壳入口：`desktop_app/assets/js/bindings.js`
- `ai-content-factory` 属于 `generationRoutes`，但它与 `viral-title`、`product-title`、`script-extractor`、`ai-copywriter` 的差异在于拥有 workflow 持久化主链。
- 关键动作：
  - `保存工作流` -> `_createWorkflowDefinitionFromRoute()`
  - `运行工作流` -> `_createWorkflowRunFromRoute()`
  - `运行批次` -> quick task，语义是批次启动
  - `启动批量生产` -> quick task，语义是生产任务入队
  - `保存` 在该页不是通用 toast，而是显式回落到 `_createWorkflowDefinitionFromRoute()`
- 结论：新壳不能只保留“生成内容”按钮，必须保留 workflow definition / workflow run 这条持久化主链。

### 2.5 样式基线

- 旧壳入口：
  - `desktop_app/assets/css/pages-content.css`
  - `desktop_app/assets/css/interactions.css`
- 关键样式族：
  - `content-workbench-*`
  - `workbench-summary-*`
  - `workbench-tool`
  - `workflow-board`
  - `workflow-node`
  - `workbench-sidecard*`
  - `strip-card`
- 结论：新壳必须沿用 content workbench + workflow board 的布局关系，不得改造成单栏生成页或聊天页。

## 3. Runtime 方案

### 3.1 当前状态判断

- 已存在的新壳 HTTP 能力：
  - `accounts`
  - `assets`
  - `tasks`
  - `providers`
  - `experiments`
  - `activity`
- 当前缺口：
  - `runtimeApi.ts` 尚未暴露 `listWorkflowDefinitions`
  - `runtimeApi.ts` 尚未暴露 `createWorkflowDefinition`
  - `runtimeApi.ts` 尚未暴露 `listWorkflowRuns`
  - `runtimeApi.ts` 尚未暴露 `startWorkflowRun`
- `app_factory.py` 当前也未注册 workflow HTTP router。

### 3.2 新增 HTTP Router

- 新增：`apps/py-runtime/src/api/http/workflows/routes.py`
- 路由前缀：`/workflows`
- 首轮 endpoint：
  - `GET /workflows/definitions`
  - `POST /workflows/definitions`
  - `GET /workflows/runs`
  - `POST /workflows/runs`
- 数据来源：
  - `desktop_app.services.workflow_service.WorkflowService`
  - `desktop_app.database.repository.Repository`
- 返回统一 JSON 信封：`{ ok: true, data: ... }`
- 异常处理：
  - 使用统一中文错误信息
  - 服务异常写 `log.exception(...)`
  - 不向前端直接泄露 traceback

### 3.3 Router 注册

- 修改：`apps/py-runtime/src/bootstrap/app_factory.py`
- 接入 workflow router，保持与 experiments / activity 并列

### 3.4 新壳 runtimeApi/types 扩展

- 修改：
  - `apps/desktop/src/modules/runtime/runtimeApi.ts`
  - `apps/desktop/src/modules/runtime/types.ts`
- 新增最小类型：
  - `WorkflowDefinitionItem`
  - `WorkflowRunItem`
  - `WorkflowDefinitionCreatePayload`
  - `WorkflowRunCreatePayload`
- 新增方法：
  - `listWorkflowDefinitions()`
  - `createWorkflowDefinition(payload)`
  - `listWorkflowRuns(definitionId?)`
  - `startWorkflowRun(payload)`

## 4. 新壳页面方案

### 4.1 文件布局

- 页面：`apps/desktop/src/pages/content/AiContentFactoryPage.vue`
- 数据模块：
  - `apps/desktop/src/modules/content/aiContentFactory.types.ts`
  - `apps/desktop/src/modules/content/aiContentFactory.helpers.ts`
  - `apps/desktop/src/modules/content/useAiContentFactoryData.ts`
- 样式：`apps/desktop/src/styles/ai-content-factory.css`

### 4.2 页面结构

页面按旧壳区块拆成 5 段：

1. 头部操作区
   - 保存工作流
   - 运行批次
   - 运行工作流
   - 刷新
2. summary strip
   - 当前工作流
   - 当前批次
   - 提供商状态
3. content workbench shell
   - rail tools
   - workflow board
   - workbench sidebar
4. strip grid
   - 最近批次
   - 失败节点
   - 待处理任务
5. 页面内运行视图区
   - 首轮用真实 workflow definitions / runs + tasks 派生运行态和回放态

### 4.3 数据来源

- `runtimeApi.listAssets()`
- `runtimeApi.listTasks()`
- `runtimeApi.listProviders()`
- `runtimeApi.listWorkflowDefinitions()`
- `runtimeApi.listWorkflowRuns(definitionId?)`
- `runtimeApi.createWorkflowDefinition(...)`
- `runtimeApi.startWorkflowRun(...)`

### 4.4 派生规则

- summary chips：
  - 当前工作流：优先最近 workflow definition 名称，否则回退默认工作流名称
  - 当前批次：基于最近 workflow run 状态
  - 提供商状态：基于 providers 启用数量与任务失败率
- workflow nodes：
  - 输入素材：assets 总量、可复用素材、最近导入时间
  - AI 脚本：最近 definition 模板或任务反馈
  - 语音与字幕：从任务类型与 providers 可用性派生
  - 批量剪辑：从 run/task 状态派生生产能力
- side cards：
  - 节点库：可用 provider / workflow 数量
  - 项目区：当前 definition 及最近 run 摘要
  - 当前批次状态：running / failed / completed 聚合
- strip cards：
  - 最近批次：workflow runs
  - 失败节点：failed tasks / failed runs
  - 待处理任务：pending tasks / queued runs

### 4.5 主动作“保存工作流”

- 打开页面内轻量表单，采集：
  - 工作流名称
  - 场景说明
  - 默认节点配置摘要
- 提交后执行：
  1. `createWorkflowDefinition`
  2. 重新加载 definitions / runs / tasks
- 成功后：
  - 页面 banner 显示中文成功反馈
  - summary / workflow board / detail 同步刷新

### 4.6 次动作“运行批次”

- 首轮保留任务入队语义，但不能只是按钮摆设。
- 触发后：
  - 调用现有任务创建链路或 workflow run 创建链路之一
  - 立即刷新 strip grid 与 detail
  - 在页面上显示“批次已启动”的真实反馈

### 4.7 动作“运行工作流”

- 直接落到 `startWorkflowRun(...)`
- 首轮入参：
  - `definitionId`
  - `runLabel`
  - `notes`
- 成功后：
  - 页面切换到最近 run 详情态
  - 底部 strip 将最新 run 置顶

## 5. 壳层详情区

### 5.1 新增状态分支

- 修改：`apps/desktop/src/modules/shell/useShellStore.ts`
- 新增：
  - `aiContentFactoryDetailState`
  - `setAiContentFactoryDetailState`
  - `resetAiContentFactoryDetailState`

### 5.2 DetailPanel 分支

- 修改：`apps/desktop/src/layouts/DetailPanel.vue`
- 当 `currentRouteName === 'ai-content-factory'` 时显示专属分支
- 内容包含：
  - 当前工作流状态
  - 失败节点
  - 建议动作
  - 操作按钮：保存工作流 / 运行批次 / 运行工作流
- 事件通道：
  - `tkops:ai-content-factory-detail-action`

## 6. 路由与样式接入

- `routeManifest.ts`
  - 新增 `pageKind: 'aiContentFactory'`
  - `ai-content-factory` 改为 `migrationStatus: 'implemented'`
- `routes.ts`
  - 接入 `AiContentFactoryPage.vue`
- `main.ts`
  - 引入 `ai-content-factory.css`

## 7. 测试与文档

### 7.1 Runtime 测试

- `tests/test_runtime_api.py`
  - 新增 workflow HTTP endpoint 测试
- `tests/test_experiment_workflow_persistence.py`
  - 新壳 runtime HTTP / workflow API 契约断言

### 7.2 Frontend 测试

- `tests/test_desktop_frontend_routes.py`
  - ai-content-factory 页面与 detail panel 分支存在
- `tests/test_page_runtime_data.py`
  - ai-content-factory 模块使用真实 runtime 数据源
  - 断言包含 workflow definitions / runs API
- `tests/test_page_interaction_audit.py`
  - 锁定 summary strip、workflow board、保存/运行动作

### 7.3 迁移文档

- `docs/migration/page-matrix.md`
  - 已迁移数量 `13 -> 14`
  - ai-content-factory 改为已迁移
- `docs/migration/current-status-and-roadmap.md`
  - 同步加入 AI 内容工厂

## 8. 验证

- `pytest tests/test_runtime_api.py -k "workflow" -v`
- `pytest tests/test_experiment_workflow_persistence.py -v`
- `pytest tests/test_desktop_frontend_routes.py -v`
- `pytest tests/test_page_runtime_data.py -v`
- `pytest tests/test_page_interaction_audit.py -v`
- `npm run typecheck`
- `npm run build`

## 9. 回退点

- 若 workflow HTTP route 暂时不可稳定，可先保留 route 文件与 runtimeApi/types，但不把 `ai-content-factory` 标成 implemented。
- 若 workflow board 首轮节点细节不足，可先保留真实节点状态和批次摘要，不回退成普通卡片生成器。
- 若 DetailPanel 分支出现冲突，可先回退为默认 detail，但不得影响保存工作流与运行工作流的真实持久化链路。
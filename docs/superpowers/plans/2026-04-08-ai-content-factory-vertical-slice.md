# AI 内容工厂垂直切片迁移计划

## Summary
- 目标：将 `ai-content-factory` 从占位路由升级为真实新壳页面，并严格按旧壳 `makeAIContentFactoryRoute()` 与 `workbenchType = 'ai-content-factory'` 做 1:1 深度迁移与代码转换。
- 原则：不能把 AI 内容工厂降级成普通生成卡片页，也不能只迁页面标题和按钮；必须同步迁移工作流节点、批次运行状态、工作流定义持久化、运行批次触发、右栏关系和运行时数据装配。
- 范围：本计划覆盖旧壳 route / factory / loader / bindings / CSS / page-audit 基线，以及新壳前端、runtime 契约、DetailPanel 和测试闭环。

## Legacy Baseline

### 1. Route 基线
- 旧壳入口：`desktop_app/assets/js/routes.js`
- 路由工厂：`makeAIContentFactoryRoute()`，其底层走 content workbench 工厂，并指定 `workbenchType = 'ai-content-factory'`。
- 固定语义：
	- 页面名称：`AI 内容工厂`
	- 角色定位：生成类页面集合中的“批量生产工作流页”，不是单次生成器
	- 主动作语义：`保存工作流`
	- 次动作语义：`运行批次`
	- 页面目标：围绕标题、脚本、文案、素材和批量生产链组织内容产线

### 2. Factory 基线
- 旧壳入口：`desktop_app/assets/js/factories/content.js`
- `ai-content-factory` 不是普通生成页，而是 content workbench 的工厂子模式。
- 关键结构：
	- `workbench-summary-strip` 或等价顶部摘要区
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
- 关键内容区块：
	- 批量生产工作流主看板
	- 输入素材 / AI 脚本 / 语音与字幕 / 批量剪辑 等节点
	- side cards：节点库、项目区、当前批次状态
	- bottom cards：批次运行状态、失败节点、可回放批次
	- detail groups + detail cards：当前工作流、风险节点、建议动作

### 3. Loader 基线
- 旧壳入口：`desktop_app/assets/js/page-loaders.js`
- loader：`loaders['ai-content-factory']`
- 真实数据来源：
	- `api.assets.list()`
	- `api.tasks.list()`
	- `api.providers.list()`
	- `api.workflows.definitions()`
	- `api.workflows.runs()`
- 关键运行逻辑：
	- `_renderWorkflowNodes(assets, tasks, providers, definitions, runs)`
	- `_renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list')`
	- `_renderStripCards(runs.length ? runs : tasks, '#mainHost .workbench-strip-grid')`
	- `_applyAiHandoffHint('ai-content-factory', '#mainHost .workbench-strip-grid')`
	- `bindRouteInteractions()`

### 4. 交互与持久化基线
- 旧壳入口：`desktop_app/assets/js/bindings.js`
- `ai-content-factory` 属于 `generationRoutes`，但它是其中唯一带 workflow 持久化语义的页面。
- 关键动作：
	- `保存工作流` -> `_createWorkflowDefinitionFromRoute()`
	- `运行工作流` -> `_createWorkflowRunFromRoute()`
	- `运行批次` -> quick task，语义是批次启动
	- `启动批量生产` -> quick task，语义是生产任务入队
	- `保存` 在该页不是通用 toast，而是显式回落到 `_createWorkflowDefinitionFromRoute()`
- 结论：新壳不能只保留“生成内容”按钮，必须保留 workflow definition / workflow run 这条持久化主链。

### 5. 样式基线
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
- 新壳必须延续 content workbench / workflow board 语义，不得改造成普通表单页或单栏 AI 聊天页。

## Runtime Gap Assessment
- 旧桥接与测试已经证明工作流持久化能力存在：
	- `listWorkflowDefinitions`
	- `createWorkflowDefinition`
	- `listWorkflowRuns`
	- `startWorkflowRun`
- 当前新壳 `apps/desktop/src/modules/runtime/runtimeApi.ts` 尚未暴露 workflow definitions / runs 的完整 HTTP API 封装。
- 当前新壳 runtime HTTP 是否已经具备这些 endpoint，需要在 spec 阶段明确核对；如果没有，则本页迁移范围必须下沉到 `apps/py-runtime/src/` 补最小闭环。
- 结论：ai-content-factory 的迁移必须同时覆盖 workflow runtime API/types；仅实现前端页面会再次形成“能看不能跑”的半迁移状态。

## New-Shell Scope

### 前端页面与模块
- 新增或修改目标：
	- `apps/desktop/src/pages/content/AiContentFactoryPage.vue` 或等价拆分路径
	- `apps/desktop/src/modules/content/aiContentFactory.types.ts`
	- `apps/desktop/src/modules/content/aiContentFactory.helpers.ts`
	- `apps/desktop/src/modules/content/useAiContentFactoryData.ts`
	- `apps/desktop/src/styles/ai-content-factory.css`

### 壳层接入
- 修改：
	- `apps/desktop/src/app/router/routeManifest.ts`
	- `apps/desktop/src/app/router/routes.ts`
	- `apps/desktop/src/main.ts`
	- `apps/desktop/src/layouts/DetailPanel.vue`
	- `apps/desktop/src/modules/shell/useShellStore.ts`
- 需要新增 ai-content-factory 专属 detail state，承接工作流定义、当前批次、失败节点和下游移交建议。

### Runtime 契约补齐
- 修改：
	- `apps/desktop/src/modules/runtime/runtimeApi.ts`
	- `apps/desktop/src/modules/runtime/types.ts`
- 至少补齐：
	- `listWorkflowDefinitions`
	- `createWorkflowDefinition`
	- `listWorkflowRuns`
	- `startWorkflowRun`
- 如新壳 runtime HTTP 未提供以上接口，则还需补：
	- `apps/py-runtime/src/api/http/...` 下 workflow route
	- workflow service / adapter 的最小胶水

## Phase Plan

### Phase 1: 冻结旧壳结构与数据映射
- 明确 route、factory、loader、bindings、CSS 的逐文件映射表。
- 把 summary、rail、workflow 节点、side cards、strip cards、detail groups 映射为新壳 view model。
- 验证哪些文案来自真实 workflow/task/provider 数据，哪些是纯派生状态文案。

### Phase 2: 补齐 workflow runtime 契约
- 优先确认新壳 runtime HTTP 是否已有 workflow definitions / runs 的封装。
- 若无，则先补最小 endpoint 集，确保前端可以读取定义、读取批次、保存工作流、启动运行。
- 该阶段必须明确错误信封、日志记录和 UI 可见反馈。

### Phase 3: 实现 ai-content-factory 页面
- 按 content workbench + workflow board 结构实现页面，不压平成普通生成器。
- 实现工作流节点视图、提供商与任务反馈、批次运行条带、失败节点回看。
- 主动作 `保存工作流` 必须落真实持久化；次动作 `运行批次` / `运行工作流` 必须落真实运行触发或明确任务入队链路。

### Phase 4: 接 DetailPanel、测试与迁移文档
- route 从 placeholder 升级为 implemented。
- 增加 ai-content-factory detail 分支与状态总线。
- 同步更新前端路由测试、runtime 数据测试、交互审计测试和迁移矩阵文档。

## 文件地图
- 旧壳输入：
	- `desktop_app/assets/js/routes.js`
	- `desktop_app/assets/js/factories/content.js`
	- `desktop_app/assets/js/page-loaders.js`
	- `desktop_app/assets/js/bindings.js`
	- `desktop_app/assets/css/pages-content.css`
	- `desktop_app/assets/css/interactions.css`
- 新壳输出：
	- `apps/desktop/src/pages/content/*`
	- `apps/desktop/src/modules/content/*`
	- `apps/desktop/src/modules/runtime/*`
	- `apps/desktop/src/modules/shell/useShellStore.ts`
	- `apps/desktop/src/layouts/DetailPanel.vue`
	- `apps/desktop/src/app/router/*`
	- `apps/desktop/src/styles/*`
	- `tests/test_desktop_frontend_routes.py`
	- `tests/test_page_runtime_data.py`
	- `tests/test_page_interaction_audit.py`
	- workflow 相关 runtime 测试

## Validation Baseline
- `venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "workflow" -v`
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py tests/test_page_runtime_data.py tests/test_page_interaction_audit.py -v`
- 如补了 workflow HTTP route，再加对应 runtime 契约测试
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## Boundaries
- 不在本轮同时迁移 `visual-lab`、`video-editor` 或其他生成类页面。
- 不对 workflow 数据模型做无关扩容，只补 ai-content-factory 运行闭环所需的最小字段。
- 不引入第二套页面骨架，继续复用现有 content workbench 宿主模式。

## Rollback Points
1. 若 workflow HTTP route 不可在本轮稳定补齐，则只保留 plan，不进入 spec 之后的实现。
2. 若旧壳实际页面语义与当前 content workbench 宿主差异过大，则先在 spec 中补结构映射，不直接编码。
3. 若 detail panel 无法承载 workflow 右栏语义，则优先扩展壳层状态，不在页面内偷偷复制第二套右栏。

## Risks
1. ai-content-factory 与普通生成页共享 generationRoutes，容易被错误迁成“AI 生成器合集页”。
	- 应对：spec 必须明确它的 workflow definition / run 主链与普通生成页的差异。
2. workflow definitions / runs 在旧桥接存在，但新壳 runtime HTTP 可能尚未公开。
	- 应对：spec 必须先确认 endpoint 状态，再决定前后端改动范围。
3. 如果只接 `保存工作流`，不接 `运行工作流` 与批次状态，页面仍然不闭环。
	- 应对：实现验收必须包含定义保存、运行触发、运行状态回读三个环节。

## Exit Criteria
- ai-content-factory 拥有独立 plan，不再只是总计划中的一个标题。
- 已明确该页迁移必须同时覆盖 workflow 持久化、批次运行状态、content workbench 布局和 detail panel 关系。
- plan 获批后，下一步直接进入 ai-content-factory spec 编写。
# 创意工坊垂直切片迁移计划

## Summary
- 目标：将 `creative-workshop` 从占位路由升级为真实新壳页面，并严格按旧壳 `makeContentWorkbenchRoute({ workbenchType: 'creative-workshop' })` 做 1:1 深度迁移与代码转换。
- 原则：不能把创意工坊降级成普通卡片页，也不能只迁 UI 外观；必须同步迁移实验项目、任务反馈、素材覆盖、版本对比、持久化动作与详情关系。
- 范围：本计划覆盖旧壳 route / factory / loader / bindings / CSS / runtime summary / page-audit 基线，以及新壳前端与 runtime 契约补齐。

## Legacy Baseline

### 1. Route 基线
- 旧壳入口：`desktop_app/assets/js/routes.js`
- 路由工厂：`makeContentWorkbenchRoute({...})`
- 固定语义：
	- `breadcrumb = creator`
	- `eyebrow = 创意组合实验区`
	- `headerEyebrow = 话题、镜头、文案联动`
	- `title = 创意工坊`
	- `primaryAction = 保存创意方案`
	- `secondaryAction = 对比创意版本`
	- `workbenchType = creative-workshop`

### 2. Factory 基线
- 旧壳入口：`desktop_app/assets/js/factories/content.js`
- creative-workshop 不是独立模板，而是 content workbench 工厂的一个子模式。
- 关键结构：
	- `workbench-summary-strip`
	- `content-workbench-shell`
	- `workbench-rail`
	- `workbench-canvas workbench-canvas--creative`
	- `toolbar-strip`
	- `focus-grid`
	- `workbench-sidebar`
	- `workbench-side-list`
	- `workbench-strip-grid`
	- `detailHtml`
- 关键内容区块：
	- summary chips
	- 主题/镜头/口播/导出 rail tools
	- 4 张 focus cards
	- side cards（实验判定 / 风险检查 / 下一步）
	- bottom cards（已保存实验 / 待验证项 / 复盘记录）
	- detail groups + detail cards

### 3. Loader 基线
- 旧壳入口：`desktop_app/assets/js/page-loaders.js`
- loader：`loaders['creative-workshop']`
- 真实数据来源：
	- `api.accounts.list()`
	- `api.assets.list()`
	- `api.tasks.list()`
	- `api.experiments.projects()`
- 关键运行逻辑：
	- `_renderWorkbenchSummary(...)`
	- `_renderCreativeFocusCards(accounts, assets, tasks)`
	- `_renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list')`
	- `_renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset')`
	- `_renderCreativeWorkshopDetail(projects, tasks, assets)`
	- `runtimeSummaryHandlers['creative-workshop'](...)`
	- `_applyAiHandoffHint('creative-workshop', '#mainHost .workbench-strip-grid')`

### 4. 交互与持久化基线
- 旧壳入口：`desktop_app/assets/js/bindings.js`
- `creative-workshop` 属于 `contentRoutes`
- 主动作 `保存创意方案` 不是 quick task，而是 `_createExperimentProjectFromRoute('creative-workshop')`
- 该动作会串联：
	- `api.experiments.createProject(...)`
	- `api.experiments.createView(...)`
	- `api.activity.create(...)`
	- `_refreshCurrentRoute()`
- 次动作 `对比创意版本` 当前为信息动作，但不能丢失其“版本对比”语义。

### 5. 样式基线
- 旧壳入口：
	- `desktop_app/assets/css/pages-content.css`
	- `desktop_app/assets/css/pages-config.css`
	- `desktop_app/assets/css/interactions.css`
- 关键样式族：
	- `content-workbench-*`
	- `workbench-summary-*`
	- `workbench-tool`
	- `focus-card*`
	- `workbench-sidecard*`
	- `strip-card`
- 新壳必须延续 content workbench 家族布局，不得改成新的页面骨架。

## Runtime Gap Assessment
- 当前新壳 `apps/desktop/src/modules/runtime/runtimeApi.ts` 还没有 `experiments / reports / workflows / activity` 封装。
- 旧桥接与测试已明确后端能力存在：
	- `listExperimentProjects`
	- `createExperimentProject`
	- `listExperimentViews`
	- `createExperimentView`
	- `listActivityLogs`
	- `createActivityLog`
- 结论：creative-workshop 的迁移必须包含 runtime API/types 扩展；仅做页面前端无法形成 1:1 闭环。

## New-Shell Scope

### 前端页面与模块
- 新增或修改目标：
	- `apps/desktop/src/pages/content/CreativeWorkshopPage.vue` 或等价拆分路径
	- `apps/desktop/src/modules/content/creativeWorkshop.types.ts`
	- `apps/desktop/src/modules/content/creativeWorkshop.helpers.ts`
	- `apps/desktop/src/modules/content/useCreativeWorkshopData.ts`
	- `apps/desktop/src/styles/creative-workshop.css`

### 壳层接入
- 修改：
	- `apps/desktop/src/app/router/routeManifest.ts`
	- `apps/desktop/src/app/router/routes.ts`
	- `apps/desktop/src/main.ts`
	- `apps/desktop/src/layouts/DetailPanel.vue`
	- `apps/desktop/src/modules/shell/useShellStore.ts`
- 需要新增 creative-workshop 专属 detail state，承接实验状态、任务反馈、素材缺口与下发建议。

### Runtime 契约补齐
- 修改：
	- `apps/desktop/src/modules/runtime/runtimeApi.ts`
	- `apps/desktop/src/modules/runtime/types.ts`
- 至少补齐：
	- listExperimentProjects
	- createExperimentProject
	- listExperimentViews
	- createExperimentView
	- listActivityLogs
	- createActivityLog
- 若新壳 runtime HTTP 尚无对应 endpoint，则本页实现范围还需下沉到 `apps/py-runtime/src/` 补最小闭环。

## Implementation Phases

### Phase 1: 冻结结构与数据映射
- 把旧壳 summary chips、rail tools、focus cards、side cards、bottom cards、detail groups 映射到新壳 view model。
- 明确哪些内容来自 experiments、tasks、assets、activity，哪些是纯派生文案。

### Phase 2: 补齐 runtime API
- 先让新壳前端可直接读取 experiments / activity 持久化数据。
- 若需新增 py-runtime endpoint，先做最小绝对必要集，不扩散到无关页面。

### Phase 3: 实现 creative-workshop 页面
- 保持 content workbench 布局与块级关系。
- 实现 `保存创意方案` 的真实持久化动作。
- 实现 `对比创意版本` 的页面内真实版本视图切换或对比态，不保留空 toast。

### Phase 4: 接详情区、测试与文档
- 壳层 detail 分支
- 路由从 placeholder 升级为 implemented
- 同步测试与迁移文档

## Test Baseline
- `tests/test_desktop_frontend_routes.py`
- `tests/test_page_runtime_data.py`
- `tests/test_page_interaction_audit.py`
- 建议新增或更新：
	- 与 experiment/workflow 持久化相关的 runtime/front-end 契约测试
	- creative-workshop 页面专属静态结构断言
- 编译验证：
	- `npm run typecheck`
	- `npm run build`

## Risks
1. creative-workshop 依赖 experiments/activity 持久化，而新壳 runtime API 还未封装。
	 - 应对：spec 必须明确 runtime 扩展范围和最小 endpoint 集。
2. content workbench 工厂结构块较多，容易在新壳中被压平为普通卡片页。
	 - 应对：spec 必须列出旧壳区块到新壳组件的逐块映射表。
3. 次动作“对比创意版本”如果只保留 toast，会再次退化成半迁移。
	 - 应对：实现时必须提供真实视图切换或版本对比区域。

## Exit Criteria
- creative-workshop 拥有独立 spec，不再停留在总计划级别。
- 已明确：该页迁移必须同时覆盖 content workbench 结构、experiment 持久化动作、runtime API 补齐与 detail panel 关系。
- plan 获批后，下一步直接进入 creative-workshop spec 编写。

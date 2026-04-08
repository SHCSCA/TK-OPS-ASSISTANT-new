# 创意工坊垂直切片设计

## 1. 目标

- 将 `creative-workshop` 从占位路由升级为真实新壳页面。
- 严格复用旧壳 `makeContentWorkbenchRoute({ workbenchType: 'creative-workshop' })` 的 content workbench 语义，不把它降级成普通内容卡片页。
- 同步补齐新壳 runtime 对 experiments / activity 的 HTTP 契约，让“保存创意方案”走真实持久化链路。
- 页面、右栏详情、runtime API、测试、迁移文档同时落地，避免出现“页面已切换但实验动作仍是空壳”的半迁移状态。

## 2. 旧壳基线映射

### 2.1 Route 基线

- 旧壳入口：`desktop_app/assets/js/routes.js`
- 页面配置：`creative-workshop: makeContentWorkbenchRoute(...)`
- 核心文案：
  - `breadcrumb = creator`
  - `eyebrow = 创意组合实验区`
  - `headerEyebrow = 话题、镜头、文案联动`
  - `title = 创意工坊`
  - `description = 围绕主题、镜头、口播和素材组合做创意试验...`
  - `primaryAction = 保存创意方案`
  - `secondaryAction = 对比创意版本`
- 语义归属：内容与 AI 域中的创意试验工作台，而不是普通文案页或单一创意列表页。

### 2.2 Factory 基线

- 旧壳入口：`desktop_app/assets/js/factories/content.js`
- creative-workshop 不是独立模板，而是 content workbench 工厂的子模式。
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
- 关键块：
  - summary chips：当前实验 / 待决策 / 保留倾向
  - rail tools：主题 / 镜头 / 口播 / 导出
  - focus cards：实验主视角 / 素材覆盖 / 任务反馈 / 执行建议
  - side cards：实验判定 / 风险检查 / 下一步
  - bottom cards：已保存实验 / 待验证项 / 复盘记录
  - detail cards / detail groups

### 2.3 Loader 基线

- 旧壳入口：`desktop_app/assets/js/page-loaders.js`
- loader：`loaders['creative-workshop']`
- 真实数据来源：
  - `api.accounts.list()`
  - `api.assets.list()`
  - `api.tasks.list()`
  - `api.experiments.projects()`
- 关键行为：
  - `_renderWorkbenchSummary(...)`
  - `_renderCreativeFocusCards(accounts, assets, tasks)`
  - `_renderWorkbenchSideCards(tasks, '#mainHost .workbench-side-list')`
  - `_renderStripCards(assets, '#mainHost .workbench-strip-grid', 'asset')`
  - `_renderCreativeWorkshopDetail(projects, tasks, assets)`
  - `runtimeSummaryHandlers['creative-workshop'](...)`
  - `_applyAiHandoffHint('creative-workshop', '#mainHost .workbench-strip-grid')`

### 2.4 交互与持久化基线

- 旧壳入口：`desktop_app/assets/js/bindings.js`
- `creative-workshop` 属于 `contentRoutes`
- 主动作 `保存创意方案` 走 `_createExperimentProjectFromRoute('creative-workshop')`
- 真实链路：
  - `api.experiments.createProject(...)`
  - `api.experiments.createView(...)`
  - `api.activity.create(...)`
  - `_refreshCurrentRoute()`
- 次动作 `对比创意版本` 目前是信息动作，但新壳必须落到真实版本对比态，不能只保留 toast。

### 2.5 样式基线

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
- 结论：新壳必须沿用 content workbench 布局和卡片语义，避免引入第二套视觉框架。

## 3. Runtime 方案

### 3.1 新增 HTTP Router

- 新增：`apps/py-runtime/src/api/http/experiments/routes.py`
- 路由前缀：`/experiments`
- 首轮 endpoint：
  - `GET /experiments/projects`
  - `POST /experiments/projects`
  - `GET /experiments/views`
  - `POST /experiments/views`
- 数据来源：
  - `desktop_app.services.analytics_service.AnalyticsService`
  - `desktop_app.database.repository.Repository`
- 返回统一 JSON 信封：`{ ok: true, data: ... }`

### 3.2 新增 Activity Router

- 新增：`apps/py-runtime/src/api/http/activity/routes.py`
- 路由前缀：`/activity`
- 首轮 endpoint：
  - `GET /activity/logs`
  - `POST /activity/logs`
- 数据来源：
  - `desktop_app.services.activity_service.ActivityService`
  - `desktop_app.database.repository.Repository`

### 3.3 Router 注册

- 修改：`apps/py-runtime/src/bootstrap/app_factory.py`
- 接入 experiments 与 activity router

### 3.4 新壳 runtimeApi/types 扩展

- 修改：
  - `apps/desktop/src/modules/runtime/runtimeApi.ts`
  - `apps/desktop/src/modules/runtime/types.ts`
- 新增最小类型：
  - `ExperimentProjectItem`
  - `ExperimentViewItem`
  - `ActivityLogItem`
  - `ExperimentProjectCreatePayload`
  - `ExperimentViewCreatePayload`
  - `ActivityLogCreatePayload`
- 新增方法：
  - `listExperimentProjects()`
  - `createExperimentProject(payload)`
  - `listExperimentViews(projectId?)`
  - `createExperimentView(payload)`
  - `listActivityLogs(limit?, category?)`
  - `createActivityLog(payload)`

## 4. 新壳页面方案

### 4.1 文件布局

- 页面：`apps/desktop/src/pages/content/CreativeWorkshopPage.vue`
- 数据模块：
  - `apps/desktop/src/modules/content/creativeWorkshop.types.ts`
  - `apps/desktop/src/modules/content/creativeWorkshop.helpers.ts`
  - `apps/desktop/src/modules/content/useCreativeWorkshopData.ts`
- 样式：`apps/desktop/src/styles/creative-workshop.css`

### 4.2 页面结构

页面按旧壳区块拆成 5 段：

1. 头部操作区
   - 保存创意方案
   - 对比创意版本
   - 刷新
2. summary strip
   - 当前实验
   - 待决策
   - 保留倾向
3. content workbench shell
   - rail tools
   - creative canvas + toolbar strip + focus cards
   - workbench sidebar
4. strip grid
   - 已保存实验
   - 待验证项
   - 复盘记录
5. 页面内版本对比区
   - 首轮用真实 experiment projects / views + tasks 派生对比态

### 4.3 数据来源

- `runtimeApi.listAccounts({ includeArchived: false })`
- `runtimeApi.listAssets()`
- `runtimeApi.listTasks()`
- `runtimeApi.listExperimentProjects()`
- `runtimeApi.listExperimentViews(projectId?)`
- `runtimeApi.listActivityLogs(limit, category)`
- `runtimeApi.createExperimentProject(...)`
- `runtimeApi.createExperimentView(...)`
- `runtimeApi.createActivityLog(...)`

### 4.4 派生规则

- summary chips：
  - 当前实验：优先使用最近 experiment project 名称，其次回退账号区域聚合
  - 待决策：基于非 completed 任务数
  - 保留倾向：基于素材数量与失败任务比例
- focus cards：
  - 实验主视角：最近 project + 绑定地区/任务状态
  - 素材覆盖：assets 总量与可复用比率
  - 任务反馈：running / failed / pending 聚合
  - 执行建议：基于失败任务和素材缺口生成
- side cards：
  - 实验判定：project status + views 数量
  - 风险检查：failed tasks + 素材缺口
  - 下一步：视频编辑移交建议
- bottom cards：
  - 已保存实验：experiment projects / views
  - 待验证项：非完成任务与待补素材
  - 复盘记录：`category = experiment` 的 activity logs

### 4.5 主动作“保存创意方案”

- 打开页面内表单或轻量 modal，采集：
  - 项目名称
  - 目标说明
- 提交后顺序执行：
  1. `createExperimentProject`
  2. `createExperimentView`
  3. `createActivityLog`
  4. 重新加载页面数据
- 成功后：
  - 页面 banner 显示中文成功反馈
  - summary / strip / detail 同步刷新

### 4.6 次动作“对比创意版本”

- 不使用空 toast
- 首轮实现为页面内切换 `compareMode`：
  - 默认态：主工作台
  - 对比态：展示最近两个 project/view 或最近 project + 当前草稿的对比卡
- 对比维度：
  - 项目名称
  - 目标说明
  - 关联任务反馈
  - 素材覆盖
  - 活动复盘摘要

## 5. 壳层详情区

### 5.1 新增状态分支

- 修改：`apps/desktop/src/modules/shell/useShellStore.ts`
- 新增：
  - `creativeWorkshopDetailState`
  - `setCreativeWorkshopDetailState`
  - `resetCreativeWorkshopDetailState`

### 5.2 DetailPanel 分支

- 修改：`apps/desktop/src/layouts/DetailPanel.vue`
- 当 `currentRouteName === 'creative-workshop'` 时显示专属分支
- 内容包含：
  - 当前实验状态
  - 重点风险
  - 建议动作
  - 操作按钮：保存创意方案 / 对比创意版本 / 刷新
- 事件通道：
  - `tkops:creative-workshop-detail-action`

## 6. 路由与样式接入

- `routeManifest.ts`
  - 新增 `pageKind: 'creativeWorkshop'`
  - `creative-workshop` 改为 `migrationStatus: 'implemented'`
- `routes.ts`
  - 接入 `CreativeWorkshopPage.vue`
- `main.ts`
  - 引入 `creative-workshop.css`

## 7. 测试与文档

### 7.1 Runtime 测试

- `tests/test_runtime_api.py`
  - 新增 experiments / activity HTTP endpoint 测试
- 若需桥接兼容说明，不修改现有 bridge 测试语义，只补新壳 HTTP 层验证

### 7.2 Frontend 测试

- `tests/test_desktop_frontend_routes.py`
  - creative-workshop 页面与 detail panel 分支存在
- `tests/test_page_runtime_data.py`
  - creative-workshop 模块使用真实 runtime 数据源
  - 断言包含 experiments / activity API
- `tests/test_page_interaction_audit.py`
  - 锁定 summary strip、rail、focus cards、保存/对比动作

### 7.3 迁移文档

- `docs/migration/page-matrix.md`
  - 已迁移数量 `12 -> 13`
  - creative-workshop 改为已迁移
- `docs/migration/current-status-and-roadmap.md`
  - 同步加入创意工坊

## 8. 验证

- `pytest tests/test_runtime_api.py -k "experiment or activity" -v`
- `pytest tests/test_desktop_frontend_routes.py -v`
- `pytest tests/test_page_runtime_data.py -v`
- `pytest tests/test_page_interaction_audit.py -v`
- `npm run typecheck`
- `npm run build`

## 9. 回退点

- 若 experiments/activity HTTP route 暂时不可稳定，可先保留 route 文件与 runtimeApi/types，但不把 creative-workshop 标成 implemented。
- 若页面内版本对比态引发较大回归，可先保留 compareMode 骨架和真实数据列表，不回退成纯 toast。
- 若壳层 detail 分支出现冲突，可先回退为默认 detail，但不得影响保存方案的真实持久化链路。

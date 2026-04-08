# 定时发布旧壳 1:1 迁移计划

## Summary
- 目标：将 `scheduled-publish` 从 placeholder 升级为真实页面，按旧壳 `makeTaskOpsRoute + _loadTaskOpsPage({ tableMode: 'publish' })` 的 publish 模式做 1:1 迁移。
- 核心策略：不重新发明发布页，而是复用现有任务域 runtime 能力和 task-ops 旧壳语义，把“发布计划、审核状态、异常中断、日历/列表联动”映射到新壳页面。
- 流程：本计划经你审批后，补 `docs/superpowers/specs/2026-04-08-scheduled-publish-vertical-slice-design.md`，再进入实现。

## Goals
1. 把 `scheduled-publish` 从占位页切为真实 `implemented` 页面，并进入迁移进度统计。
2. 1:1 复刻旧壳发布编排页的结构、文案语义、主次动作和任务筛选逻辑。
3. 复用现有 `/tasks`、`/accounts`、`/assets` runtime 数据，形成 publish 模式下的专页视图，而不是简单复刻任务队列。
4. 在新壳里补齐发布计划的主区、详情区、状态摘要和最小可执行动作链。
5. 保持文件拆分，避免把 publish 逻辑重新堆进一个大文件。

## Scope
### In Scope
- `apps/desktop/src/app/router/routeManifest.ts`
  - 把 `scheduled-publish` 切成真实 `pageKind` 与 `implemented`。
- `apps/desktop/src/app/router/routes.ts`
  - 注册新的 `ScheduledPublishPage.vue`。
- `apps/desktop/src/pages/publish/ScheduledPublishPage.vue`（新）
- `apps/desktop/src/modules/publish/useScheduledPublishData.ts`（新）
- `apps/desktop/src/modules/publish/scheduledPublish.helpers.ts`（新）
- `apps/desktop/src/modules/publish/scheduledPublish.types.ts`（新）
- `apps/desktop/src/styles/scheduled-publish.css`（新）
- 如需统一右栏：`apps/desktop/src/modules/shell/useShellStore.ts` 与 `apps/desktop/src/layouts/DetailPanel.vue`
- 路由契约、页面运行时数据和样式/结构锁定测试

### Out of Scope
- 不在本轮同时迁移 `data-collector`。
- 不新增发布专用后端 endpoint，除非旧壳行为无法通过现有任务接口等价表达。
- 不把定时发布改造成全新日历产品；优先复刻旧壳 publish 模式。
- 不顺带重写任务队列页。

## Baseline
- 旧壳路由基线：`desktop_app/assets/js/routes.js`
  - `scheduled-publish: makeTaskOpsRoute(...)`
- 旧壳数据/交互基线：`desktop_app/assets/js/page-loaders/task-ops-main.js`
  - `loaders['scheduled-publish'] = function () { _loadTaskOpsPage({ routeKey: 'scheduled-publish', title: '定时发布', tableMode: 'publish' }); };`
  - `_loadTaskOpsPage`
  - `_updateTaskOpsMetrics`
  - `_renderTaskOpsBody`
  - `_renderTaskOpsDetail`
  - `_bindTaskOpsHeaderActions`
  - `_taskDraftForOpsRoute`
- 新壳参考实现：
  - `apps/desktop/src/pages/tasks/TasksPage.vue`
  - `apps/desktop/src/modules/tasks/useTasksData.ts`
  - 已完成的 `device-management` 页面拆分方式
- 菜单顺序基线：`docs/migration/page-matrix.md` 中 `scheduled-publish` 为当前第一优先页

## File Map
### 新增文件
- `apps/desktop/src/pages/publish/ScheduledPublishPage.vue`
- `apps/desktop/src/modules/publish/useScheduledPublishData.ts`
- `apps/desktop/src/modules/publish/scheduledPublish.helpers.ts`
- `apps/desktop/src/modules/publish/scheduledPublish.types.ts`
- `apps/desktop/src/styles/scheduled-publish.css`
- `docs/superpowers/specs/2026-04-08-scheduled-publish-vertical-slice-design.md`

### 预期修改文件
- `apps/desktop/src/app/router/routeManifest.ts`
- `apps/desktop/src/app/router/routes.ts`
- `apps/desktop/src/main.ts`
- `apps/desktop/src/layouts/DetailPanel.vue`
- `apps/desktop/src/modules/shell/useShellStore.ts`
- `tests/test_desktop_frontend_routes.py`
- `tests/test_page_runtime_data.py`
- `docs/migration/page-matrix.md`

## Functional Target
### 页面定位
- 发布编排中心
- 统一查看：
  - 待发布计划
  - 待审核项
  - 中断计划
  - 账号/素材是否具备发布条件

### 主动作
- 主按钮：`新建发布计划`
  - 首版最小闭环：创建 `taskType = publish` 的真实任务草稿
- 次按钮：`查看发布日历`
  - 首版允许在本页切换列表/日历视图，或聚焦本周发布窗口

### 数据视图
- 指标卡沿旧壳 publish 语义：
  - 今日计划
  - 待审核
  - 中断计划
- 列表区优先显示 `publish` 相关任务
- 详情区显示当前计划的审核、环境、素材、账号就绪情况

## Implementation Phases
### Phase 1: 冻结旧壳 publish 模式契约
- 抽取旧壳 `scheduled-publish` 的文案、指标、动作、筛选、详情区语义。
- 明确 task-ops 中哪些逻辑可直接复用，哪些需要新壳适配。

### Phase 2: 新壳页面骨架与路由切换
- 新增 `ScheduledPublishPage.vue` 与 publish 模块小文件。
- `routeManifest` 将 `scheduled-publish` 改为 `implemented`。
- `routes.ts` 注册页面组件。

### Phase 3: 数据派生与动作链
- 基于 `runtimeApi.listTasks/listAccounts/listAssets` 构造 publish 模式数据。
- 复刻旧壳 publish 指标和记录生成逻辑。
- 实现主按钮创建 publish 草稿，补最小刷新/切换视图动作。

### Phase 4: 详情区与样式
- 如旧壳语义需要，增加 publish 专属 detail state。
- 样式单独落在 `scheduled-publish.css`，不污染 `main.css`。
- 保持旧壳 task-ops / list-management 类名语义，减少结构漂移。

### Phase 5: 测试与验证
- 补路由、页面存在性、运行时数据来源测试。
- 跑 typecheck、build 与定向 pytest。

## Validation
### 自动化
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工验收
- 左侧菜单中 `定时发布` 不再显示 placeholder 内容。
- 页面能展示 publish 语义下的真实任务、账号、素材关联信息。
- 主按钮可以创建真实 publish 任务草稿。
- 页面结构、文案、指标和详情区与旧壳 publish 模式保持一致口径。

## Risks
1. 旧壳 `scheduled-publish` 不是独立实现，而是 task-ops 的一个 tableMode。
   - 应对：spec 里明确“复用与拆分边界”，避免直接复制一整套 task-ops 大文件。
2. 现有 runtime 只有通用 tasks，没有发布专属聚合。
   - 应对：先以前端派生复刻旧壳语义，仅在确实缺口时补最小协议。
3. 若直接复用任务队列页面，容易退化成“换个标题的 TasksPage”。
   - 应对：必须锁定 publish 专属指标、详情区和视图切换，保证不是壳层换皮。

## Rollback
- 若实现中发现 publish 语义无法稳定落地，可先保留新建模块代码但不切路由，让 `scheduled-publish` 继续回退到 placeholder。

## Exit Criteria
- `scheduled-publish` 进入 implemented 列表。
- 页面具备旧壳 publish 模式的主区、指标、动作、详情语义。
- 自动化验证通过，且不引入新的大文件或构建告警。
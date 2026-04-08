# 数据采集助手旧壳 1:1 深度迁移计划

## Summary
- 目标：将 `data-collector` 从 placeholder 升级为真实页面，按旧壳 `makeTaskOpsRoute + _loadTaskOpsPage({ tableMode: 'collector' })` 的 collector 模式做 1:1 深度迁移与代码转换。
- 核心策略：不把它实现成“换标题的任务页”，而是完整复刻旧壳的采集工作流中心语义，把采集任务、数据源、代理池、补偿链路和详情建议映射到新壳。
- 流程：本计划经你审批后，补 `docs/superpowers/specs/2026-04-08-data-collector-vertical-slice-design.md`，再进入实现。

## Goals
1. 把 `data-collector` 从占位页切为真实 `implemented` 页面，并进入迁移进度统计。
2. 1:1 复刻旧壳采集页的页面结构、文案语义、主次动作、筛选逻辑和详情区关系。
3. 复用现有 runtime 的真实数据能力，构建 collector 模式下的采集专页视图，而不是退化成普通任务列表。
4. 在新壳中补齐采集任务主区、代理池/设备摘要、补偿与重试建议、右栏详情和最小动作链。
5. 保持文件拆分，避免把 collector 逻辑重新堆成单文件。

## Scope
### In Scope
- `apps/desktop/src/app/router/routeManifest.ts`
  - 把 `data-collector` 切成真实 `pageKind` 与 `implemented`。
- `apps/desktop/src/app/router/routes.ts`
  - 注册新的 `DataCollectorPage.vue`。
- `apps/desktop/src/pages/collector/DataCollectorPage.vue`（新）
- `apps/desktop/src/modules/collector/useDataCollectorData.ts`（新）
- `apps/desktop/src/modules/collector/dataCollector.helpers.ts`（新）
- `apps/desktop/src/modules/collector/dataCollector.types.ts`（新）
- `apps/desktop/src/styles/data-collector.css`（新）
- 如需统一右栏：`apps/desktop/src/modules/shell/useShellStore.ts` 与 `apps/desktop/src/layouts/DetailPanel.vue`
- 路由契约、页面运行时数据和结构/样式锁定测试

### Out of Scope
- 不在本轮同时迁移 `creative-workshop`。
- 不把数据采集助手改造成全新采集平台；优先复刻旧壳 collector 模式。
- 不顺带重写任务队列、设备管理或账号代理绑定页。
- 不新增与旧壳无关的业务指标、图表或仪表板。

## Baseline
- 旧壳路由基线：`desktop_app/assets/js/routes.js`
  - `data-collector: makeTaskOpsRoute({ ... primaryAction: '新建采集方案', secondaryAction: '查看代理池' })`
- 旧壳页面工厂基线：`desktop_app/assets/js/factories/operations.js`
  - `makeTaskOpsRoute(config)` 负责生成 task filter bar、view toggles、task-ops shell、table wrapper 与 detailHtml 骨架
- 旧壳数据/交互基线：`desktop_app/assets/js/page-loaders/task-ops-main.js`
  - `loaders['data-collector'] = function () { _loadTaskOpsPage({ routeKey: 'data-collector', title: '数据采集助手', tableMode: 'collector' }); };`
  - `_filterTasksForOpsMode(..., 'collector')` 仅保留 `task_type = scrape`
  - `_taskDraftForOpsRoute(..., collector)` 默认草稿为：`title = '数据采集任务'`、`task_type = 'scrape'`、`priority = 'high'`、`result_summary = '来源页面：数据采集助手'`
  - `_renderTaskOpsTable(..., config.tableMode === 'collector')` 的表格列语义为：任务名 / 类型 / 状态 / 区域与动作
  - `_renderTaskOpsDetail(...)` 详情区使用任务数、失败数、账号数量和素材数量的共享聚合结果
- 旧壳样式基线：`desktop_app/assets/css/pages-ops.css`
  - `task-ops-shell`
  - `task-filter-bar`
  - `task-filter-tab`
  - `task-view-toggles`
  - `task-ops-body`
  - `task-ops-main`
  - `task-ops-canvas`
  - `task-ops-sidebar`
- 新壳可复用 runtime 能力：
  - `runtimeApi.listTasks()`
  - `runtimeApi.createTask(payload)`
  - `runtimeApi.startTask(taskId)`
  - `runtimeApi.deleteTask(taskId)`
  - `runtimeApi.listAccounts({ includeArchived: false })`
  - `runtimeApi.listAssets()`
  - `runtimeApi.listDevices(status?)`
  - `runtimeApi.getAccountProxyBinding(accountId)` / `updateAccountProxyBinding(...)`（如 spec 需要代理池和设备绑定更细粒度视图）

## Functional Target
### 页面定位
- 采集工作流中心
- 统一查看：
  - scrape 任务列表
  - 数据源 / 区域分布
  - 代理池与设备可用性摘要
  - 补偿、失败重试与阻塞建议

### 主动作
- 主按钮：`新建采集方案`
  - 首版最小闭环：创建 `taskType = scrape` 的真实任务草稿
- 次按钮：`查看代理池`
  - 首版允许在本页切换到设备/代理摘要视图，或聚焦当前可用设备和代理状态

### 数据视图
- 指标卡沿旧壳 collector 语义：
  - 采集任务总数
  - 异常 / 暂停项
  - 执行率
- 列表区优先显示 `scrape` 相关任务
- 详情区显示当前任务状态、失败/补偿建议、账号/素材/设备聚合信息
- 如旧壳“查看代理池”在新壳需要更明确承载，则在页面内或统一右栏中展示设备/代理摘要，但不得改变 collector 主体信息架构

## File Map
### 新增文件
- `apps/desktop/src/pages/collector/DataCollectorPage.vue`
- `apps/desktop/src/modules/collector/useDataCollectorData.ts`
- `apps/desktop/src/modules/collector/dataCollector.helpers.ts`
- `apps/desktop/src/modules/collector/dataCollector.types.ts`
- `apps/desktop/src/styles/data-collector.css`
- `docs/superpowers/specs/2026-04-08-data-collector-vertical-slice-design.md`

### 预期修改文件
- `apps/desktop/src/app/router/routeManifest.ts`
- `apps/desktop/src/app/router/routes.ts`
- `apps/desktop/src/main.ts`
- `apps/desktop/src/layouts/DetailPanel.vue`
- `apps/desktop/src/modules/shell/useShellStore.ts`
- `tests/test_desktop_frontend_routes.py`
- `tests/test_page_runtime_data.py`
- `tests/test_page_interaction_audit.py`
- `docs/migration/page-matrix.md`
- `docs/migration/current-status-and-roadmap.md`

## Implementation Phases
### Phase 1: 冻结旧壳 collector 模式契约
- 抽取旧壳 `data-collector` 的 route 文案、task-ops 共享骨架、筛选规则、默认草稿和详情区语义。
- 明确 collector 模式相对 publish / interaction / calendar 的差异，避免新壳误做成通用任务页。

### Phase 2: 新壳页面骨架与路由切换
- 新增 `DataCollectorPage.vue` 与 collector 模块小文件。
- `routeManifest` 将 `data-collector` 改为 `implemented`。
- `routes.ts` 注册页面组件。
- 1:1 对齐旧壳的 `task-ops-shell`、filter tabs、view toggles、table wrapper 和详情区层次。

### Phase 3: 数据派生与动作链
- 基于 `runtimeApi.listTasks/listAccounts/listAssets/listDevices` 构造 collector 模式数据。
- 复刻旧壳 `scrape` 任务过滤、状态筛选、默认草稿和详情聚合逻辑。
- 实现主按钮创建 scrape 草稿，补最小刷新、启动、删除、查看代理池动作。

### Phase 4: 代理池/设备与右栏语义收口
- 若旧壳“查看代理池”需要在新壳中保持真实承载，则结合 `listDevices` 与代理绑定数据补充采集链路的环境摘要。
- 若 collector 需要专属 detail state，则在统一右栏中新增 collector 分支，确保不破坏壳层全局一致性。

### Phase 5: 样式、测试与验证
- 样式单独落在 `data-collector.css`，保留旧壳 task-ops 选择器和视觉关系，减少结构漂移。
- 补路由、页面存在性、runtime 数据来源、交互审计测试。
- 跑 typecheck、build 与定向 pytest。

## Validation
### 自动化
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_interaction_audit.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工验收
- 左侧菜单中 `数据采集助手` 不再显示 placeholder 内容。
- 页面能展示 scrape 语义下的真实任务、账号、素材与设备/代理关联信息。
- 主按钮可以创建真实 scrape 任务草稿。
- 页面结构、文案、筛选区、表格列和详情区与旧壳 collector 模式保持一致口径。
- `查看代理池` 至少能展示或切换到真实设备/代理摘要，而不是空按钮。

## Risks
1. 旧壳 `data-collector` 不是独立实现，而是 task-ops 的 collector 模式。
   - 应对：spec 里明确共享 task-ops 与 collector 特化边界，避免把共享逻辑复制成大文件。
2. 旧壳 route 文案强调“数据源、代理池、补偿链路”，但共享 loader 默认只聚合 tasks/accounts/assets。
   - 应对：spec 中明确哪些内容必须继续由 `listDevices` 与代理绑定接口补充，哪些保持旧壳共享详情语义。
3. 若直接复用任务队列页面，容易退化成“换个标题的 TasksPage”。
   - 应对：必须锁定 collector 专属筛选、草稿、表格列、次按钮和代理池摘要，保证不是换皮。

## Rollback
- 若实现中发现 collector 语义无法稳定落地，可先保留新建模块代码但不切路由，让 `data-collector` 继续回退到 placeholder。
- 采集环境摘要若阶段一无法稳定落地，可先保留 collector 主体页和真实 scrape 任务链，设备/代理摘要作为同一 spec 内的可分阶段交付项，但不得改写旧壳主语义。

## Exit Criteria
- `data-collector` 进入 implemented 列表。
- 页面具备旧壳 collector 模式的主区、筛选区、动作链、表格列与详情语义。
- scrape 任务、账号、素材和至少一层真实设备/代理摘要已打通，不存在空动作或假数据。
- 自动化验证通过，且不引入新的大文件或构建告警。
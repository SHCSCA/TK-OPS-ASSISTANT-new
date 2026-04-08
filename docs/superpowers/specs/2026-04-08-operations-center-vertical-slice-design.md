# 运营中心旧壳 1:1 全量复刻设计

> 已废弃：2026-04-08 起该模块不再保留在新壳产品范围内，后续实施以 `2026-04-08-remove-operations-center-design.md` 为准。

## Summary
本设计将 `operations-center` 从新壳 placeholder 页面迁移为真实运行页，并以旧壳 `makeListManagementRoute({ mode: 'operations' })` 为唯一主基线，完整转移页面结构、样式约束、数据派生、事件链和接口调用语义。实现过程中遵守“小文件拆分”原则：页面、数据、样式、壳层详情状态、测试分别落在独立文件，避免出现单文件继续膨胀。

## Source Mapping
### 旧壳来源
- 路由元数据：`desktop_app/assets/js/routes.js` 中 `operations-center`
- 页面模板：`desktop_app/assets/js/factories/operations.js` 中 `makeListManagementRoute`
- 数据装配与交互：`desktop_app/assets/js/page-loaders.js`
  - `_loadListManagementPage`
  - `_bindListManagementActions`
  - `_listManagementDraft`
  - `_listManagementRecords`
  - `_renderListManagementMetrics`
  - `_renderListManagementItems`
  - `_renderListManagementDetail`
- 样式：
  - `desktop_app/assets/css/components.css`
  - `desktop_app/assets/css/pages-ops.css`

### 新壳目标映射
- 路由切换：`apps/desktop/src/app/router/routeManifest.ts`、`apps/desktop/src/app/router/routes.ts`
- 页面骨架：`apps/desktop/src/pages/operations/OperationsCenterPage.vue`
- 数据编排：`apps/desktop/src/modules/operations/useOperationsCenterData.ts`
- 本地类型与派生：
  - `apps/desktop/src/modules/operations/operationsCenter.types.ts`
  - `apps/desktop/src/modules/operations/operationsCenter.helpers.ts`
- 右栏状态：`apps/desktop/src/modules/shell/useShellStore.ts`
- 右栏渲染：`apps/desktop/src/layouts/DetailPanel.vue`
- 页面样式：`apps/desktop/src/styles/operations-center.css`
- 样式注册：`apps/desktop/src/main.ts`
- 测试：
  - `tests/test_desktop_frontend_routes.py`
  - `tests/test_page_runtime_data.py`

## File Split Strategy
1. `OperationsCenterPage.vue`
- 仅保留模板绑定和极薄的 script setup 解构。
- 不承载复杂派生和事件分发。

2. `useOperationsCenterData.ts`
- 负责加载 runtime 数据、动作回调、右栏联动。
- 不直接存放大量静态 label 映射和格式化工具。

3. `operationsCenter.helpers.ts`
- 放旧壳派生逻辑的 Vue 适配版本：
  - 指标派生
  - 列表记录生成
  - 详情区数据生成
  - 状态 tone / badge 文案

4. `operationsCenter.types.ts`
- 放本页专属 VM 类型，避免堆到 `runtime/types.ts`。

5. `operations-center.css`
- 仅承接运营中心 1:1 样式，不把新样式继续堆进 `main.css`。

## Route & Shell Changes
### routeManifest
- 新增 `pageKind: 'operationsCenter'`
- `operations-center` 的 `migrationStatus` 从 `placeholder` 改为 `implemented`

### routes.ts
- 注册 `OperationsCenterPage.vue`

### useShellStore / DetailPanel
- 新增 `OperationsDetailState`
- 结构尽量对齐旧壳 detailHtml：
  - `title`
  - `subtitle`
  - `detailItems[]`
  - `adviceCards[]`
  - `statusLabel/statusTone`
- `DetailPanel.vue` 新增 `isOperationsRoute` 分支
- 页面主列表选中项变化时同步写入 `shell.setOperationsDetailState(...)`

## Data Flow
### Inputs
- `runtimeApi.listTasks()`
- `runtimeApi.listAccounts({ includeArchived: false })`
- `runtimeApi.listAssets()`
- `runtimeApi.listProviders()`

### Aggregation Rules
旧壳真实派生规则直接迁移，不做重新设计：

1. 指标卡
- 指标 1：`tasks.length`
- 指标 2：失败任务数 `failed`
- 指标 3：完成率 `completedRate`
- 其中完成率沿用旧壳钳制逻辑：最小 48%，最大 96%

2. 列表记录
- 以 `accounts.slice(0, 4)` 为主轴生成运营排期项
- 每条记录从同索引 `tasks[index]` 和 `assets[index]` 派生描述
- title 规则：`${region} 运营排期`
- desc 规则：`${username} / 素材 ${filename} / ${taskTypeLabel}`
- badge/tone 优先来自任务状态，否则回退为 `待协调` / `warning`

3. 详情区
- `detailItems[0] = ${tasks.length} 项排期运行中`
- `detailItems[1] = ${failed} 项需关注`
- `detailItems[2] = 账号 ${accounts.length} / 素材 ${assets.length} / 供应商 ${providers.length}`
- advice cards 使用列表记录前 3 条生成，label 固定为 `协调建议 1/2/3`

4. 主按钮草稿
- 复刻 `_listManagementDraft(...operations)`
- 创建任务草稿字段：
  - `title = 运营排期协调`
  - `taskType = maintenance`
  - `priority = high`
  - `resultSummary = 来源页面：运营中心 / 协调账号、素材与排期冲突`
  - `accountId = accounts[0]?.id ?? null`

## Interaction Design
### 页面动作
- 主按钮：`新建排期`
  - 行为：复用 `runtimeApi.createTask(...)` 直接创建任务，而不是仅弹 toast
- 次按钮：`导出周报`
  - 首版行为：导出当前页面摘要文本为本地 txt/csv，避免空动作
- 刷新：页面内独立刷新按钮可选；至少保留次动作或局部刷新入口

### 列表与右栏联动
- 默认选中首项
- 点击列表项：更新选中态 + 刷新右栏 detail state
- 所有选中态 class 与旧壳保持同名：`task-item is-selected`

### 跳转区
- 提供到以下页面的明确入口：
  - `account`
  - `asset-center`
  - `task-queue`
- 已实现页直接跳转，未实现页仍可跳到当前保留的 placeholder 页面，但不能死链

## Template Structure
页面结构必须保留以下旧壳核心区块命名：
- `breadcrumbs`
- `page-header`
- `section-stack`
- `stat-grid`
- `list-management-shell`
- `list-toolbar`
- `list-toolbar__search`
- `list-toolbar__filters`
- `list-main-area`
- `workbench-list`

运营中心新增但不违背 1:1 的最小区块：
- `operations-center-links`
  - 仅承接 PRD 要求的跳转区
  - 样式上复用旧壳 `operations-grid` / `board-card`

## Styling Strategy
### 原则
- 优先复用旧壳 class 名和已有桌面壳设计令牌
- 不做新的视觉重设计
- 不把运营中心样式继续堆到 `main.css`

### operations-center.css 内容
- 从旧壳迁移：
  - `list-management-shell`
  - `list-toolbar`
  - `list-search-input`
  - `list-toolbar__filters`
  - `list-filter-select`
  - `list-body`
  - `list-main-area`
  - `operations-grid`
  - `workbench-list`
- 对新壳只做最小适配：
  - 保证主区不因 `DetailPanel` 存在而塌陷
  - 1180px 以下时和旧壳一致地纵向堆叠

## Testing
### test_desktop_frontend_routes.py
新增断言：
- `operations-center` 已不是 placeholder
- `routes.ts` 注册 `OperationsCenterPage`
- 页面包含：
  - `data-page-audit="operations-center"`
  - `list-management-shell`
  - `workbench-list`
  - `新建排期`
  - `导出周报`
  - `account`
  - `asset-center`

### test_page_runtime_data.py
新增断言：
- 页面不包含旧壳硬编码示例值如 `24` / `82%` / `3 项资源冲突` 这类静态演示数
- 页面依赖 runtime 聚合结果

## Verification Commands
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## Non-Goals
- 不把 order/service/refund 一起做成真实页
- 不新增运营专用后端 endpoint
- 不重写成 dashboard 风格的指标页
- 不引入新的全局大文件
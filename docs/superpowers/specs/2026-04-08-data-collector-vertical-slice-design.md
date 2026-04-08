# 数据采集助手垂直切片设计

## 1. 目标

- 将 `data-collector` 从占位路由升级为真实新壳页面。
- 严格复用旧壳 `task-ops` 的 `collector` 子模式语义，不新造第二套采集后台。
- 首轮基于现有 runtime 能力完成闭环：`listTasks`、`createTask`、`startTask`、`deleteTask`、`listAccounts`、`listAssets`、`listDevices`。
- 页面、右栏详情、测试、迁移文档同时落地，避免出现“路由可进但页面仍是 placeholder 或换皮任务页”的半成品。

## 2. 旧壳基线映射

### 2.1 Route 基线

- 旧壳入口：`desktop_app/assets/js/routes.js`
- 页面配置：`data-collector: makeTaskOpsRoute(...)`
- 核心文案：
  - `eyebrow = 采集工作流中心`
  - `headerEyebrow = 采集源与节点编排`
  - `title = 数据采集助手`
  - `primaryAction = 新建采集方案`
  - `secondaryAction = 查看代理池`
- 语义归属：自动化任务域中的采集专页，而不是独立采集平台或普通任务列表页。

### 2.2 Factory 基线

- 旧壳入口：`desktop_app/assets/js/factories/operations.js`
- 关键工厂：`makeTaskOpsRoute(config)`
- 关键结构：
  - `task-ops-shell`
  - `task-filter-bar`
  - `task-filter-tab`
  - `task-view-toggles`
  - `task-ops-body`
  - `task-ops-main`
  - `task-ops-canvas`
  - `table-wrapper`
  - `detailHtml`

新壳必须保留这套结构层级和信息组织关系，不允许直接改成当前任务队列页的资源卡片布局。

### 2.3 Loader 基线

- 旧壳入口：`desktop_app/assets/js/page-loaders/task-ops-main.js`
- 关键调用：`_loadTaskOpsPage({ routeKey: 'data-collector', title: '数据采集助手', tableMode: 'collector' })`
- 关键行为：
  - `tableMode = 'collector'`
  - `_filterTasksForOpsMode(..., 'collector')` 仅保留 `task_type = scrape`
  - `_taskDraftForOpsRoute(..., collector)` 默认草稿：
    - `title = 数据采集任务`
    - `task_type = scrape`
    - `priority = high`
    - `result_summary = 来源页面：数据采集助手`
  - `_renderTaskOpsTable(..., collector)` 表格列语义：
    - 任务名
    - 类型
    - 状态
    - 区域与动作
  - `_renderTaskOpsDetail(...)` 沿用 task-ops 共享详情：
    - 已接入任务数
    - 失败任务数
    - 账号/素材聚合摘要

### 2.4 样式基线

- 旧壳入口：`desktop_app/assets/css/pages-ops.css`
- 关键样式族：
  - `task-ops-*`
  - `table-wrapper`
  - `calendar-grid` / `kanban-grid` 的共享切换容器
- 结论：collector 页面应沿用 task-ops 家族样式语义，必要时在新壳独立 CSS 中做宿主适配，不得重设计为新的视觉框架。

## 3. 新壳方案

### 3.1 页面结构

- 页面文件：`apps/desktop/src/pages/collector/DataCollectorPage.vue`
- 数据模块：
  - `apps/desktop/src/modules/collector/dataCollector.types.ts`
  - `apps/desktop/src/modules/collector/dataCollector.helpers.ts`
  - `apps/desktop/src/modules/collector/useDataCollectorData.ts`
- 样式文件：`apps/desktop/src/styles/data-collector.css`

页面结构分为四块：

1. 头部操作区
   - 刷新
   - 新建采集方案
   - 查看代理池
2. 指标卡片
   - 采集任务总数
   - 异常 / 暂停项
   - 执行率
3. task-ops 主工作区
   - task filter tabs
   - 视图切换按钮
   - 采集任务表格
4. 环境摘要区
   - 设备/代理池摘要
   - 失败重试与补偿建议

页面不能退化成当前 `TasksPage` 的“卡片列表 + 操作按钮”样式，而必须保留 collector/task-ops 的筛选条、表格和详情关系。

### 3.2 数据来源

- `runtimeApi.listTasks()`：主数据源，仅保留 `taskType === 'scrape'`
- `runtimeApi.listAccounts({ includeArchived: false })`：区域、账号名称与采集账户映射
- `runtimeApi.listAssets()`：素材库存与采集结果落库摘要
- `runtimeApi.listDevices()`：设备与代理池摘要来源
- `runtimeApi.createTask(...)`：新建 scrape 任务
- `runtimeApi.startTask(taskId)`：立即启动采集任务
- `runtimeApi.deleteTask(taskId)`：删除采集任务

首轮不新增 runtime endpoint。若需要更细粒度代理绑定视图，优先复用已有设备与账号代理绑定接口，而不是先扩新协议。

### 3.3 派生规则

- 任务过滤：仅展示 `taskType === 'scrape'`
- 状态筛选：复用 task-ops 共享 tab 语义
  - 全部
  - 运行中
  - 暂停
  - 失败
  - 已完成
- 指标：
  - 采集任务总数：当前 collector scope 任务数
  - 异常 / 暂停项：`failed + paused`
  - 执行率：`completed / total`
- 代理池摘要：
  - 设备总数
  - 异常设备数
  - 具备代理的设备数
  - 可用区域覆盖
- 默认创建草稿：
  - `taskType = 'scrape'`
  - `priority = 'high'`
  - `resultSummary = '来源页面：数据采集助手'`

### 3.4 次按钮“查看代理池”语义

旧壳 route 文案明确存在该动作，因此新壳不能留空。

首轮实现要求：

- 在当前页切换或聚焦设备/代理摘要区域
- 使用真实 `listDevices()` 数据显示：
  - 代理状态
  - 可用设备数
  - 覆盖区域
  - 异常环境数

禁止做法：

- 只弹一个 toast
- 只跳到无关页面
- 显示静态“代理池待接入”文案

## 4. 壳层详情区

### 4.1 新增状态分支

- 修改 `apps/desktop/src/modules/shell/useShellStore.ts`
- 新增 `collectorDetailState`
- 新增 `setCollectorDetailState` / `resetCollectorDetailState`

### 4.2 DetailPanel 分支

- 修改 `apps/desktop/src/layouts/DetailPanel.vue`
- 当 `currentRouteName === 'data-collector'` 时，展示采集详情分支
- 内容包含：
  - 当前状态
  - 任务类型 / 区域
  - 账号与素材摘要
  - 设备/代理池摘要
  - 补偿/重试建议
  - 操作按钮：启动任务、查看代理池、删除任务

右栏动作通过 `window.dispatchEvent(new CustomEvent('tkops:data-collector-detail-action', ...))` 与页面通信。

## 5. 路由接入

- `routeManifest.ts`
  - 新增 `pageKind: 'dataCollector'`
  - `data-collector` 改为 `migrationStatus: 'implemented'`
- `routes.ts`
  - 接入 `DataCollectorPage.vue`
- `main.ts`
  - 注入 `data-collector.css`

## 6. 测试与文档

### 6.1 测试

- `tests/test_desktop_frontend_routes.py`
  - 校验 `data-collector` 为 implemented 页面
  - 校验新页面、右栏和 shell store 分支存在
- `tests/test_page_runtime_data.py`
  - 新增 data-collector 模块使用真实 runtime 数据的断言
  - 断言包含 `listTasks/listAccounts/listAssets/listDevices`
- `tests/test_page_interaction_audit.py`
  - 锁定采集页关键区块、主次动作与 placeholder 清理

### 6.2 迁移文档

- `docs/migration/page-matrix.md`
  - 已迁移页面数量从 `11` 更新为 `12`
  - `data-collector` 更新为“已迁移”
- `docs/migration/current-status-and-roadmap.md`
  - 同步新增“数据采集助手”到新链路页面列表

## 7. 验证

- `pytest tests/test_desktop_frontend_routes.py -v`
- `pytest tests/test_page_runtime_data.py -v`
- `pytest tests/test_page_interaction_audit.py -v`
- `npm run typecheck`
- `npm run build`

## 8. 回退点

- 若页面实现出现阻塞，可仅保留路由占位，不提交 routeManifest 的 implemented 标记。
- 若代理池摘要实现引入较大回归，可先保留 collector 主体页和真实 scrape 链路，再把设备摘要限制为页面内受控区域，不回退成空动作。
- 若 collector 专属右栏状态引入壳层冲突，可先保留页面主体，右栏回退为默认摘要分支，但不得影响任务过滤、草稿和表格列语义。
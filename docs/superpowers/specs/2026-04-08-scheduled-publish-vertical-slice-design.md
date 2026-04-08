# 定时发布垂直切片设计

## 1. 目标

- 将 `scheduled-publish` 从占位路由升级为真实新壳页面。
- 严格复用旧壳 `task-ops` 的 `publish` 子模式语义，不新造第二套“发布系统”。
- 首轮只基于现有 runtime 能力完成闭环：`listTasks`、`createTask`、`startTask`、`deleteTask`、`listAccounts`、`listAssets`。
- 页面、右栏详情、测试、迁移文档同时落地，避免出现“路由可进但页面不完整”的半成品。

## 2. 旧壳基线映射

### 2.1 Route 基线

- 旧壳入口：`desktop_app/assets/js/routes.js`
- 页面配置：`scheduled-publish: makeTaskOpsRoute(...)`
- 语义归属：发布编排中心，而非独立任务系统

### 2.2 Loader 基线

- 旧壳入口：`desktop_app/assets/js/page-loaders/task-ops-main.js`
- 关键调用：`_loadTaskOpsPage({ routeKey: 'scheduled-publish', title: '定时发布', tableMode: 'publish' })`
- 关键行为：
  - 只保留 `task_type = publish` 的任务
  - 默认草稿固定为“定时发布计划”
  - 表格列以计划名、时间、平台、状态为核心
  - 详情区显示状态、风险与资源摘要

## 3. 新壳方案

### 3.1 页面结构

- 页面文件：`apps/desktop/src/pages/publish/ScheduledPublishPage.vue`
- 数据模块：
  - `apps/desktop/src/modules/publish/scheduledPublish.types.ts`
  - `apps/desktop/src/modules/publish/scheduledPublish.helpers.ts`
  - `apps/desktop/src/modules/publish/useScheduledPublishData.ts`
- 样式文件：`apps/desktop/src/styles/scheduled-publish.css`

页面结构分为四块：

1. 头部操作区
   - 刷新
   - 列表/日历切换
2. 新建发布计划表单
   - 标题
   - 发布时间
   - 优先级
   - 账号
   - 结果摘要
3. 指标卡片
   - 今日计划
   - 待审核
   - 中断计划
4. 主工作区
   - 左侧：发布计划列表
   - 右侧：发布日历或计划表格

### 3.2 数据来源

- `runtimeApi.listTasks()`：主数据源，仅保留 `taskType === 'publish'`
- `runtimeApi.listAccounts({ includeArchived: false })`：账号映射、平台与账号名称
- `runtimeApi.listAssets()`：素材库存摘要与详情建议
- `runtimeApi.createTask(...)`：新建发布计划
- `runtimeApi.startTask(taskId)`：立即启动计划
- `runtimeApi.deleteTask(taskId)`：删除计划

不新增 runtime endpoint，不做伪造统计。

### 3.3 派生规则

- 状态映射：
  - `pending` -> `待审核`
  - `running` -> `发布中`
  - `completed` -> `已发布`
  - `failed` -> `已中断`
  - `paused` -> `已暂停`
- 指标：
  - 今日计划：计划时间落在当天的 `publish` 任务数
  - 待审核：`pending` 或 `paused`
  - 中断计划：`failed`
- 发布日历：展示未来 7 天内的发布槽位
- 默认创建草稿：
  - `taskType = 'publish'`
  - `priority = 'high'`
  - `resultSummary` 默认值为 `来源页面：定时发布`

## 4. 壳层详情区

### 4.1 新增状态分支

- 修改 `apps/desktop/src/modules/shell/useShellStore.ts`
- 新增 `publishDetailState`
- 新增 `setPublishDetailState` / `resetPublishDetailState`

### 4.2 DetailPanel 分支

- 修改 `apps/desktop/src/layouts/DetailPanel.vue`
- 当 `currentRouteName === 'scheduled-publish'` 时，展示发布详情分支
- 内容包含：
  - 当前状态
  - 发布时间
  - 发布账号
  - 素材库存
  - 风险/建议卡片
  - 操作按钮：启动计划、切换日历、删除计划

右栏按钮通过 `window.dispatchEvent(new CustomEvent('tkops:scheduled-publish-detail-action', ...))` 与页面通信。

## 5. 路由接入

- `routeManifest.ts`
  - 新增 `pageKind: 'scheduledPublish'`
  - `scheduled-publish` 改为 `migrationStatus: 'implemented'`
- `routes.ts`
  - 接入 `ScheduledPublishPage.vue`
- `main.ts`
  - 注入 `scheduled-publish.css`

## 6. 测试与文档

### 6.1 测试

- `tests/test_desktop_frontend_routes.py`
  - 校验 `scheduled-publish` 为 implemented 页面
  - 校验新页面、右栏和 shell store 分支存在
- `tests/test_page_runtime_data.py`
  - 移除已删除的 scheduler 模块引用
  - 新增 scheduled-publish 模块使用真实 runtime 数据的断言

### 6.2 迁移文档

- `docs/migration/page-matrix.md`
  - 已迁移页面数量从 `10` 更新为 `11`
  - `scheduled-publish` 更新为“已迁移”
- `docs/migration/current-status-and-roadmap.md`
  - 同步新增“定时发布”到新链路页面列表

## 7. 验证

- `pytest tests/test_desktop_frontend_routes.py -v`
- `pytest tests/test_page_runtime_data.py -v`
- `npm run typecheck`
- `npm run build`

## 8. 回退点

- 若页面实现出现阻塞，可仅保留路由占位，不提交 routeManifest 的 implemented 标记。
- 若右栏分支实现引入全局回归，可先保留页面主体，右栏回退为默认摘要分支。
- 若 runtime 字段不稳定，不扩 runtime，优先在前端用中性空态兜底。
# 外壳层真实状态修复设计

## 背景

当前桌面壳层已经具备基本的布局、主题、通知、License、版本检查和页面摘要能力，但状态来源分散：

- `routes.js` 中存在静态 `sidebarSummary` / `statusLeft` / `statusRight`
- `page-loaders.js` 中存在按页面加载后回填的 `runtimeSummaryHandlers`
- `ui-license.js`、`ui-notifications.js`、`main.js` 分别管理启动状态、通知、更新检查

结果是：

1. 外壳层启动时缺少统一真实状态
2. 状态栏和侧边栏摘要会依赖当前页面是否完成加载
3. License / onboarding / 更新状态不能稳定地映射到壳层
4. 页面切换时容易残留上一页状态，造成“壳在跳、页面未同步”的观感

## 目标

建立一个统一的前端壳层状态中心，让外壳层始终展示真实、可解释、可恢复的状态。

本轮修复后应满足：

- 启动后 `sidebarSummary`、`statusLeft`、`statusRight` 均可显示真实数据或真实系统状态
- License、首次引导、版本更新、通知状态均可投射到壳层
- 页面级 loader 只负责“当前页面摘要”，不再直接承担全局壳状态职责
- 页面未加载完成前，壳层也能显示默认真实摘要，而不是空白或脏数据

## 方案对比

### 方案 A：继续沿用页面 loader 局部更新

直接扩展 `page-loaders.js`，让每个页面 loader 在加载后顺手更新壳层全部状态。

优点：改动最小。

缺点：

- 壳状态继续散落在页面逻辑里
- 后续每修一个页面都可能改坏壳层
- 启动期状态仍不清晰

### 方案 B：新增前端壳层状态聚合层（推荐）

新增统一 shell runtime 状态管理：

- 壳默认摘要
- 当前页运行时摘要
- License 状态
- onboarding 状态
- 更新状态
- 通知状态

页面 loader 只提交“页面摘要”，壳层统一负责渲染。

优点：

- 状态职责清晰
- 不破坏现有 Bridge / Service 结构
- 最适合当前逐模块收口方式

缺点：

- 需要整理初始化顺序和几个现有脚本之间的边界

### 方案 C：后端新增 `getShellSummary`

通过 Bridge 一次性返回所有壳层状态。

优点：前端逻辑简单。

缺点：

- Bridge 变成 UI 聚合层
- 后端会承担过多前端展示职责
- 灵活性较差

## 采用方案

采用方案 B：新增前端壳层状态聚合层。

## 设计

### 1. 新增 shell runtime 状态对象

在前端增加独立壳层状态，至少包含：

- `defaultSummary`：未进入具体页面前的壳默认摘要
- `routeSummary`：当前页面提交的运行时摘要
- `license`：激活状态、tier、剩余天数、错误信息
- `onboarding`：是否完成初始化
- `update`：最新版本检测状态
- `notifications`：通知总数/未读数
- `boot`：当前启动阶段

说明：

- `routeSummary` 优先级高于 `defaultSummary`
- 若页面 loader 尚未完成，壳显示 `defaultSummary`
- 若页面切换或加载失败，壳回落到默认摘要，不保留旧页脏状态

### 2. 壳层渲染职责统一

把下面三类展示统一收口到壳状态渲染函数：

- 侧边栏底部：`sidebarSummary`
- 底部左侧：`statusLeft`
- 底部右侧：`statusRight`

渲染规则：

1. 启动时先渲染默认壳摘要
2. 页面加载成功后用 `routeSummary` 覆盖
3. License / 更新 / onboarding / 通知等全局状态可对 `statusRight` 做补强
4. 页面没有专属摘要时，继续显示默认壳摘要

### 3. 启动时的真实数据初始化顺序

启动阶段统一收口为以下顺序：

1. 加载最近路由
2. 绑定基础交互
3. 初始化通知系统
4. 初始化 AI Chat / Agent 面板
5. 拉取主题
6. 拉取通知列表
7. 拉取 License 状态
8. 拉取 onboarding 完成状态
9. 拉取当前版本与更新状态
10. 渲染默认壳摘要
11. 再决定进入 `setup-wizard` 还是目标页面

要求：

- 任意一个环节失败都不能阻断应用启动
- 失败时要有可见的回退状态，例如“更新检测失败”“未激活”“未完成初始化”

### 4. 默认壳摘要的数据来源

默认壳摘要使用已有真实接口聚合：

- `api.dashboard.stats()`
- `api.notifications.list()`
- `api.license.status()`
- `api.version.current()` / `api.version.check()`
- `api.settings.get('onboarding.completed')`

默认壳摘要建议表达：

- 侧边栏：系统整体运行情况
- 左侧状态栏：账号/任务/设备真实计数
- 右侧状态栏：License、更新、通知、初始化状态

### 5. 页面摘要与壳状态的边界

`runtimeSummaryHandlers` 继续保留，但职责收缩为：

- 只负责生成当前路由的业务摘要
- 不关心 License / 更新 / onboarding / 通知
- 不直接决定全局壳状态优先级

壳状态层负责：

- 接收页面摘要
- 与全局系统状态合成最终显示

### 6. License 状态接入壳层

当前 `ui-license.js` 已具备：

- 未激活时显示激活遮罩
- 已激活时缓存 tier

本轮补充：

- 把 License 状态同步到壳层状态中心
- 状态栏显示：未激活 / 免费版 / 专业版 / 企业版 / 剩余天数
- 当未激活时，除了遮罩，壳层右侧状态也要明确显示“未激活”

### 7. onboarding 状态接入壳层

首次运行逻辑继续使用 `onboarding.completed` 设置项。

本轮补充：

- 壳层右侧状态明确显示“待完成初始化”或“初始化完成”
- 若未完成初始化，启动后默认进入 `setup-wizard`
- 即使进入其他页面失败，也不能让用户失去引导入口

### 8. 更新状态接入壳层

当前更新检查仅在启动后静默 Toast。

本轮补充：

- 记录更新状态到壳状态中心
- 在状态栏右侧显示：
  - 已是最新版本
  - 发现新版本
  - 更新检查失败

说明：

- 仍保持“静默检查，不打断主流程”原则
- 但不再是用户完全不可见的隐性状态

### 9. 通知状态接入壳层

通知数据继续来自 `listNotifications()`。

本轮补充：

- 启动时主动拉取通知
- 把未读数映射到壳层状态
- 状态栏显示“通知 n 条 / 未读 n 条”一类摘要

本轮暂不做通知已读持久化后端回写，只做壳层真实感知统一。

## 影响文件

主要修改：

- `desktop_app/assets/js/state.js`
- `desktop_app/assets/js/main.js`
- `desktop_app/assets/js/page-loaders.js`
- `desktop_app/assets/js/routes.js`
- `desktop_app/assets/js/ui-license.js`
- `desktop_app/assets/js/ui-notifications.js`

如需补充空态或视觉提示，可能少量调整：

- `desktop_app/assets/app_shell.html`
- `desktop_app/assets/css/shell.css`

## 验收标准

1. 应用启动后，底部状态栏不为空，显示真实系统状态
2. 左侧侧边栏底部摘要在任意页面均有合理内容
3. 未激活时既有全屏激活遮罩，也有壳层状态提示
4. 未完成初始化时壳层明确显示“待完成初始化”，并自动进入向导
5. 发现新版本时，状态栏和 Toast 至少有一处可见提示
6. 切换页面时不会残留上一页状态摘要
7. 页面 loader 失败时，壳层回落到默认摘要而不是空白或脏数据

# Page Loaders Recovery And Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 恢复 `page-loaders.js` 到可解析、可启动的状态，并将其拆分为多个职责清晰且单文件不超过 3000 行的模块。

**Architecture:** 以当前稳定基线为起点恢复 `page-loaders.js`，保留现有全局 API 和运行时 hook，不改变页面对 `window.loadRouteData`、`window.__pageAudits`、`window.__runtimeSummaryHandlers` 的消费方式。随后把账号、设备、仪表盘、任务运营、工具台等逻辑拆到独立模块，由一个轻量聚合入口统一注册和导出。

**Tech Stack:** 原生 JavaScript、QWebChannel 桥接、Node `--check`、Pytest

---

### Task 1: 确认恢复基线

**Files:**
- Modify: `desktop_app/assets/js/page-loaders.js`
- Test: `tests/test_task_backed_actions.py`
- Test: `tests/test_crud_interaction_matrix.py`

- [ ] **Step 1: 比较当前文件与 `HEAD` 基线**

Run: `git diff -- desktop_app/assets/js/page-loaders.js`
Expected: 能看到当前文件存在大量异常差异，且需要以稳定基线为恢复起点。

- [ ] **Step 2: 验证 `HEAD` 版本是否可作为恢复基线**

Run: `git show HEAD:desktop_app/assets/js/page-loaders.js > %TEMP%\\tkops-page-loaders-head.js`
Run: `node --check %TEMP%\\tkops-page-loaders-head.js`
Expected: `HEAD` 版本必须至少通过语法检查；若不通过，则改为最近可用提交作为恢复基线。

- [ ] **Step 3: 恢复聚合入口文件到稳定版本**

把 `desktop_app/assets/js/page-loaders.js` 恢复到已通过语法检查的稳定版本，确保以下对外入口仍然存在：

```js
window.loadRouteData = loadRouteData;
window._pageLoaders = loaders;
window.__pageAudits = pageAudits;
window.__runtimeSummaryHandlers = runtimeSummaryHandlers;
window.__openDeviceEnvironment = _openDeviceEnvironment;
window.__inspectDevices = _runDeviceInspection;
window.__repairDevices = _runDeviceRepair;
```

- [ ] **Step 4: 回补当前测试要求的账号/设备页关键标记**

确认恢复后仍保留这些关键标记：

```js
'js-validate-account-login'
'js-account-configure-proxy'
'js-account-rebind-validate'
'_runAccountLoginValidation('
'_saveAccountProxyBinding('
'_unbindAccountProxyBinding('
'window.__openDeviceEnvironment'
```

- [ ] **Step 5: 运行最小回归**

Run: `venv\Scripts\python.exe -m pytest tests/test_task_backed_actions.py tests/test_crud_interaction_matrix.py -v`
Expected: 相关前端契约测试通过。

### Task 2: 拆分 page loader 模块

**Files:**
- Create: `desktop_app/assets/js/page-loaders/core.js`
- Create: `desktop_app/assets/js/page-loaders/dashboard.js`
- Create: `desktop_app/assets/js/page-loaders/accounts.js`
- Create: `desktop_app/assets/js/page-loaders/devices.js`
- Create: `desktop_app/assets/js/page-loaders/tasks.js`
- Create: `desktop_app/assets/js/page-loaders/tools.js`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/app_shell.html`

- [ ] **Step 1: 建立模块目录与聚合入口**

在 `desktop_app/assets/js/page-loaders/` 下创建子模块目录。聚合入口 `page-loaders.js` 只负责：

```js
(function () {
    'use strict';

    var loaders = {};
    var pageAudits = {};
    var runtimeSummaryHandlers = {};

    window.__pageLoaderRegistry = {
        loaders: loaders,
        pageAudits: pageAudits,
        runtimeSummaryHandlers: runtimeSummaryHandlers,
    };
})();
```

- [ ] **Step 2: 抽取基础设施到 `core.js`**

把以下通用能力搬到 `core.js`：

```js
function loadRouteData(routeKey) { ... }
function _applyRuntimeSummary(summary) { ... }
function _wireHeaderPrimary(handler, text) { ... }
function _wireHeaderSecondary(handler, text) { ... }
function _rewireElements(selector, binder) { ... }
```

并在文件尾部统一导出到全局：

```js
window.loadRouteData = loadRouteData;
window._pageLoaders = loaders;
window.__pageAudits = pageAudits;
window.__runtimeSummaryHandlers = runtimeSummaryHandlers;
```

- [ ] **Step 3: 抽取账号页到 `accounts.js`**

把账号页相关函数迁移到 `accounts.js`，至少包含：

```js
_bindAccountActions
_renderAccountDetail
_bindAccountDetailActions
_renderAccountGrid
_bindAccountToolbar
_renderEmptyAccountDetail
_saveAccountProxyBinding
_unbindAccountProxyBinding
_runAccountLoginValidation
_importCookieFileIntoModal
```

模块末尾只做注册，不直接改其他模块内部状态：

```js
loaders.account = function () { ... };
pageAudits.account = { ... };
```

- [ ] **Step 4: 抽取设备页到 `devices.js`**

把设备页相关函数迁移到 `devices.js`，至少包含：

```js
_renderDeviceFilterTabs
_renderDeviceMetrics
_renderDeviceBanner
_renderDeviceGrid
_renderDeviceBindingTable
_renderDeviceCoverage
_renderDeviceLogPanel
_renderDeviceDetail
_bindDeviceFilterControls
_bindDeviceBannerActions
_bindDeviceDetailActions
_bindDeviceActions
_openDeviceEnvironment
_runDeviceInspection
_runDeviceRepair
```

并保留这些导出：

```js
window.__inspectDevices = _runDeviceInspection;
window.__repairDevices = _runDeviceRepair;
window.__openDeviceEnvironment = _openDeviceEnvironment;
window.__exportDeviceLog = _exportDeviceLog;
```

- [ ] **Step 5: 抽取剩余大块职责到独立模块**

按职责拆分并控制单文件行数：

```text
dashboard.js   -> 仪表盘与首页 runtime summary
tasks.js       -> task-queue / task-ops / analytics header actions
tools.js       -> tool console / diagnostics / list management / setup wizard / permissions
```

每个模块只注册属于自己的 `loaders[routeKey]`、`pageAudits[routeKey]`、`runtimeSummaryHandlers[routeKey]`。

- [ ] **Step 6: 在 `app_shell.html` 中按顺序加载模块**

确保脚本顺序为：

```html
<script src="assets/js/page-loaders.js"></script>
<script src="assets/js/page-loaders/core.js"></script>
<script src="assets/js/page-loaders/dashboard.js"></script>
<script src="assets/js/page-loaders/accounts.js"></script>
<script src="assets/js/page-loaders/devices.js"></script>
<script src="assets/js/page-loaders/tasks.js"></script>
<script src="assets/js/page-loaders/tools.js"></script>
```

- [ ] **Step 7: 确认每个文件不超过 3000 行**

Run: `Get-ChildItem desktop_app\\assets\\js\\page-loaders\\*.js | ForEach-Object { $_.Name + ' ' + ((Get-Content $_.FullName | Measure-Object -Line).Lines) }`
Expected: 所有新模块以及聚合入口都小于等于 3000 行。

### Task 3: 回归验证

**Files:**
- Test: `tests/test_backend_entities.py`
- Test: `tests/test_bridge_runtime_contract.py`
- Test: `tests/test_crud_interaction_matrix.py`
- Test: `tests/test_page_runtime_data.py`
- Test: `tests/test_task_backed_actions.py`

- [ ] **Step 1: 运行 JS 语法检查**

Run: `node --check desktop_app/assets/js/page-loaders.js`
Run: `Get-ChildItem desktop_app\\assets\\js\\page-loaders\\*.js | ForEach-Object { node --check $_.FullName }`
Expected: 所有模块都通过语法检查。

- [ ] **Step 2: 运行前端契约回归**

Run: `venv\Scripts\python.exe -m pytest tests/test_task_backed_actions.py tests/test_bridge_runtime_contract.py tests/test_crud_interaction_matrix.py tests/test_page_runtime_data.py -v`
Expected: 全部通过。

- [ ] **Step 3: 运行服务层相关回归**

Run: `venv\Scripts\python.exe -m pytest tests/test_backend_entities.py -v`
Expected: 代理环境、设备巡检、账号登录态相关测试全部通过。

- [ ] **Step 4: 做一次桌面应用启动验证**

Run: `venv\Scripts\python.exe desktop_app\main.py`
Expected: 应用能够拉起，不再出现 `js: Uncaught SyntaxError: Invalid or unexpected token`。

- [ ] **Step 5: 记录结果**

把最终结果整理为：

```text
1. 恢复基线来源
2. 新模块划分
3. 每个模块行数
4. 测试命令与结果
5. 启动验证结果
```

# Version And Loader Split Next Steps

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:subagent-driven-development or superpowers:executing-plans. Keep commits small, run focused pytest after each page split, and preserve root-file contracts in `page-loaders.js`.

**Goal:** 在已经完成版本单一来源、账号页拆分、任务队列拆分的基础上，继续降低 `page-loaders.js` 复杂度，同时保持运行时 hook、静态测试契约和桌面壳脚本加载链稳定。

**Current Baseline:**

- 版本号统一到根级 `VERSION`，运行时通过 `desktop_app/version.py` 读取。
- 账号页已拆成 `page-loaders.js` + `account-environment.js` + `account-main.js`。
- 任务队列已拆成 `page-loaders.js` + `task-queue-main.js`。
- 当前拆分相关 focused pytest 已通过。

**Architecture Constraint:** `page-loaders.js` 继续承担根聚合职责，保留 `window._pageLoaders`、`window.__pageAudits`、`window.__runtimeSummaryHandlers` 以及共享 helper 出口。子模块只接管页面级实现，不改动全局消费方式。

**Tech Stack:** 原生 JavaScript、PySide6/QWebChannel、Pytest、PowerShell、Git

---

## Task 1: 拆分 Asset Center

**Files:**

- Create: `desktop_app/assets/js/page-loaders/asset-center-main.js`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/app_shell.html`
- Modify: `tests/test_crud_interaction_matrix.py`
- Modify: `tests/test_page_runtime_data.py`

- [ ] **Step 1: 迁移 asset-center 主 loader 与素材详情渲染**

把以下逻辑移动到 `asset-center-main.js`：

```js
loaders['asset-center']
_updateAssetStats
_renderAssetCategories
_buildAssetThumb
_bindAssetThumbs
_renderAssetDetail
```

要求：根文件仅保留共享函数和拆分标记注释。

- [ ] **Step 2: 更新壳层脚本加载顺序**

在 `app_shell.html` 中确保顺序如下：

```html
<script src="./js/page-loaders.js"></script>
<script src="./js/page-loaders/account-environment.js"></script>
<script src="./js/page-loaders/account-main.js"></script>
<script src="./js/page-loaders/task-queue-main.js"></script>
<script src="./js/page-loaders/asset-center-main.js"></script>
<script src="./js/main.js"></script>
```

- [ ] **Step 3: 调整静态断言为 root + asset 子模块聚合文本**

重点修改：

```python
tests/test_crud_interaction_matrix.py
tests/test_page_runtime_data.py
```

要求：仅对 `asset-center` 路由使用聚合读取，其它未拆分路由继续保留当前断言方式。

- [ ] **Step 4: 运行 focused 回归**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_crud_interaction_matrix.py tests/test_page_runtime_data.py tests/test_page_interaction_audit.py tests/test_bridge_runtime_contract.py -v
```

Expected: 与资产页拆分相关的静态契约和运行时测试通过。

---

## Task 2: 预拆 Device Management

**Files:**

- Modify: `desktop_app/assets/js/page-loaders.js`
- Create: `desktop_app/assets/js/page-loaders/device-management-main.js`
- Modify: `tests/test_crud_interaction_matrix.py`
- Modify: `tests/test_page_runtime_data.py`

- [ ] **Step 1: 识别必须留在根文件的共享 helper**

先确认以下函数是否仍被其他页面引用，再决定是否共享导出：

```js
_formatRelativeDate
_isTruthy
_accountRegionLabel
_accountPlatformLabel
_formatNum
_esc
```

- [ ] **Step 2: 先抽设备页主 loader、详情渲染与绑定，不先抽环境工具函数**

优先迁移：

```js
loaders['device-management']
_renderDeviceDetail
_bindDeviceDetailActions
_renderDeviceGrid
_renderDeviceFilterTabs
```

暂缓迁移：

```js
_openDeviceEnvironment
_runDeviceInspection
_runDeviceRepair
```

原因：先减主文件体积，再处理更高风险的设备环境动作链。

- [ ] **Step 3: 为设备页建立单独拆分测试文件**

新增类似账号页的拆分契约测试，验证：

```python
device-management-main.js 已在 app_shell.html 注册
loaders['device-management'] 在子模块中定义
根文件仍保留 __pageAudits / __runtimeSummaryHandlers / shared helpers
```

---

## Task 3: 清理共享层和命名契约

**Files:**

- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `docs/superpowers/plans/*.md`（按需）
- Modify: `tests/test_page_loader_account_split.py`

- [ ] **Step 1: 为共享层建立明确分组**

将 `window.__pageLoaderShared` 内导出按类别整理：

```js
render helpers
batch helpers
account helpers
common formatting helpers
```

要求：不改对外 key，先只整理声明顺序和注释，避免破坏已有子模块。

- [ ] **Step 2: 评估是否需要拆出 page-loader-shared.js**

只有在满足以下条件时才执行：

- `page-loaders.js` 仍明显大于 3000 行
- 至少 3 个子模块依赖共享层
- 测试可接受 root + shared + page 子模块的组合断言

- [ ] **Step 3: 更新仓库计划与记忆**

每完成一次页面拆分后，补充：

- `docs/superpowers/plans` 中对应执行文档
- `/memories/repo/page-loaders-contracts.md` 中的拆分契约记录

---

## Task 4: 版本治理后续收口

**Files:**

- Modify: `README.md`（按需）
- Modify: `build.py`（按需）
- Test: `tests/test_version_consistency.py`

- [ ] **Step 1: 每次版本号更新前先修改 `VERSION`**

要求：不要再直接改 `installer.iss`、`bridge.js`、`file_version_info.txt` 里的版本字符串。

- [ ] **Step 2: 确认构建链会在打包前自动同步元数据**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_version_consistency.py -v
```

Expected: 运行时版本、README、安装器、Windows 文件版本信息、桥接 stub 全部一致。

---

## Task 5: 提交与回归纪律

- [ ] **Step 1: 每轮拆分只处理一个页面块**

禁止在同一轮同时拆 `asset-center` 和 `device-management`。

- [ ] **Step 2: 每轮提交前最少跑一组 focused pytest**

推荐最小集合：

```powershell
venv\Scripts\python.exe -m pytest tests/test_crud_interaction_matrix.py tests/test_page_runtime_data.py tests/test_bridge_runtime_contract.py -v
```

- [ ] **Step 3: 每个提交消息包含拆分页名与契约说明**

示例：

```text
Split asset-center loader and update runtime contracts
```

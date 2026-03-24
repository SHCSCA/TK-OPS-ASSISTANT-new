# Shell Runtime Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 TK-OPS 桌面壳层建立统一真实状态中心，让启动期、页面期和系统级状态都能稳定映射到侧边栏摘要与底部状态栏。

**Architecture:** 继续沿用现有 `routes.js + page-loaders.js + data.js` 架构，在前端新增壳层状态聚合逻辑而不是把 UI 聚合塞进 Bridge。页面 loader 只负责提交当前页摘要，壳层负责合成全局默认摘要、License、通知、更新、初始化状态并统一渲染。

**Tech Stack:** 原生 JavaScript、PySide6 QWebChannel、现有 `window.api` 数据层、pytest。

---

### Task 1: 扩展前端状态结构

**Files:**
- Modify: `desktop_app/assets/js/state.js`
- Test: `tests/test_page_runtime_data.py`

- [ ] **Step 1: 为 shell runtime 增加状态结构**
- [ ] **Step 2: 保存默认摘要、页面摘要、license、通知、更新、onboarding、boot 状态字段**
- [ ] **Step 3: 保持现有页面状态对象兼容**
- [ ] **Step 4: 运行相关测试确保基础结构不破坏现有页面逻辑**

### Task 2: 新增壳层统一渲染入口

**Files:**
- Modify: `desktop_app/assets/js/routes.js`
- Modify: `desktop_app/assets/js/main.js`
- Test: `tests/test_page_runtime_data.py`

- [ ] **Step 1: 在 `routes.js` 保留现有 `renderSidebarSummary` / `renderStatus`，但允许被壳层统一调用**
- [ ] **Step 2: 在 `main.js` 新增默认摘要、系统状态摘要、页面摘要合成函数**
- [ ] **Step 3: 实现“默认摘要 + 页面摘要 + 系统状态”统一渲染到 `sidebarSummary` / `statusLeft` / `statusRight`**
- [ ] **Step 4: 页面切换前清理旧摘要，避免上一页残留**

### Task 3: 接入启动期真实数据

**Files:**
- Modify: `desktop_app/assets/js/main.js`
- Modify: `desktop_app/assets/js/data.js`
- Test: `tests/test_bridge_runtime_contract.py`

- [ ] **Step 1: 启动时并行拉取 dashboard、notifications、license、version、onboarding 状态**
- [ ] **Step 2: 构建壳默认真实摘要**
- [ ] **Step 3: 失败时提供回退状态，不阻断启动**
- [ ] **Step 4: 保持现有 `window.api` 调用契约不变**

### Task 4: 收口页面摘要提交流程

**Files:**
- Modify: `desktop_app/assets/js/page-loaders.js`
- Modify: `desktop_app/assets/js/main.js`
- Test: `tests/test_generation_routes_cleanup.py`
- Test: `tests/test_page_runtime_data.py`

- [ ] **Step 1: 保留 `runtimeSummaryHandlers`，但改为统一通过壳层入口提交摘要**
- [ ] **Step 2: `_applyRuntimeSummary` 从直接写 DOM 改为更新壳状态并重新渲染**
- [ ] **Step 3: 确保 account / dashboard / task-queue / ai-provider 等已接入页面继续正常更新摘要**
- [ ] **Step 4: 页面加载失败时回退默认摘要**

### Task 5: 接入 License、初始化向导、更新、通知状态

**Files:**
- Modify: `desktop_app/assets/js/ui-license.js`
- Modify: `desktop_app/assets/js/ui-notifications.js`
- Modify: `desktop_app/assets/js/main.js`
- Test: `tests/test_notification_runtime_truthfulness.py`

- [ ] **Step 1: License 检查结果同步进壳状态中心**
- [ ] **Step 2: onboarding 状态同步进壳状态中心，并保证未完成时进入 `setup-wizard`**
- [ ] **Step 3: 更新检查结果同步进壳状态中心，支持“最新 / 有更新 / 检查失败”**
- [ ] **Step 4: 通知列表和未读状态同步进壳状态中心**

### Task 6: 调整外壳文案与可视反馈

**Files:**
- Modify: `desktop_app/assets/js/main.js`
- Modify: `desktop_app/assets/css/shell.css`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: 确保状态栏文案使用中文且和壳状态一致**
- [ ] **Step 2: 如果需要，补充轻量样式让更多状态 chip 在底栏可读**
- [ ] **Step 3: 不引入破坏性壳布局变化**

### Task 7: 验证与回归

**Files:**
- Test: `tests/test_page_runtime_data.py`
- Test: `tests/test_generation_routes_cleanup.py`
- Test: `tests/test_notification_runtime_truthfulness.py`
- Test: `tests/test_bridge_runtime_contract.py`
- Test: `tests/test_frontend_style_baseline.py`

- [ ] **Step 1: 运行外壳层相关 pytest**
- [ ] **Step 2: 修复测试失败**
- [ ] **Step 3: 运行应用做启动级人工验证**
- [ ] **Step 4: 记录最终受影响文件和验证结果**

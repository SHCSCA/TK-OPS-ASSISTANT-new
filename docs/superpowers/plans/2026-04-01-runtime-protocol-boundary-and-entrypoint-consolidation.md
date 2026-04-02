# Runtime Protocol Boundary and Entrypoint Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `apps/py-runtime` 补上一层最小可用的鉴权/握手骨架，收口 `/health` 与现有 HTTP/WS 协议边界，并把 README 默认运行入口明确切到 `apps/desktop + apps/py-runtime`，让旧 `desktop_app` 只保留参考定位。

**Architecture:** 以现有 `session_token` 为唯一优先凭据，在 runtime 内部抽出轻量协议辅助层，统一处理 HTTP 与 WS 的入口校验、握手载荷与健康检查元信息。`/health` 继续保持低成本可探活，但补充协议边界所需的最小字段；WS 连接在接受后先完成一次标准握手，再进入具体事件流，避免不同通道各说各话。文档侧同步更新 `packages/protocol/**` 与 `README.md`，把默认入口和旧目录角色讲清楚。

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, existing runtime container/settings, Markdown docs.

---

### Task 1: 补齐 runtime 协议最小骨架

**Files:**
- Create: `apps/py-runtime/src/api/common/session.py`
- Modify: `apps/py-runtime/src/api/http/health/routes.py`
- Modify: `apps/py-runtime/src/api/ws/runtime_status.py`
- Modify: `apps/py-runtime/src/api/ws/copywriter.py`
- Modify: `apps/py-runtime/src/bootstrap/app_factory.py`

- [ ] **Step 1: 在 `api/common/session.py` 里收口 token 提取和最小握手判断**

- [ ] **Step 2: 让 HTTP health 返回协议边界所需的最小元信息**

- [ ] **Step 3: 让 WS 连接先完成统一握手，再发送现有事件**

- [ ] **Step 4: 把 app factory 里的边界跳过/日志规则统一到同一套判断**

### Task 2: 收口协议文档

**Files:**
- Modify: `packages/protocol/http.md`
- Modify: `packages/protocol/events.md`
- Create: `docs/migration/runtime-protocol-boundary.md`

- [ ] **Step 1: 记录 HTTP 侧的默认入口、health 语义和鉴权头约定**
- [ ] **Step 2: 记录 WS 侧的握手顺序、事件边界和 token 透传约定**
- [ ] **Step 3: 增加一份迁移说明，说明旧 `desktop_app` 仅作参考**

### Task 3: 收口 README 默认运行入口

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 把默认运行入口描述改为 `apps/desktop` + `apps/py-runtime`**
- [ ] **Step 2: 明确 `desktop_app/` 仅是迁移参考，不再作为默认执行入口**
- [ ] **Step 3: 清理 README 中仍把旧入口写成主路径的表述**

### Task 4: 轻量自检

**Files:**
- Modify: `apps/py-runtime/src/api/common/session.py`
- Modify: `apps/py-runtime/src/api/http/health/routes.py`
- Modify: `apps/py-runtime/src/api/ws/runtime_status.py`
- Modify: `apps/py-runtime/src/api/ws/copywriter.py`
- Modify: `packages/protocol/http.md`
- Modify: `packages/protocol/events.md`
- Modify: `README.md`
- Create: `docs/migration/runtime-protocol-boundary.md`

- [ ] **Step 1: 人工复核所有新增字段、路径和文案是否与现有 runtime 设置一致**
- [ ] **Step 2: 检查是否仍保留 `desktop_app` 作为默认入口的措辞**
- [ ] **Step 3: 只在需要时补充文档，不扩展到额外 runtime 重构**

**Coverage check:**
- `session_token` 作为优先鉴权来源
- `/health` 与 HTTP/WS 协议边界对齐
- README 默认入口收口到 `apps/desktop` 与 `apps/py-runtime`
- 旧 `desktop_app` 保留 reference 定位

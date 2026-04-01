# AGENTS.md - TK-OPS 代理协作手册

面向本仓库的 AI 编码代理与新加入开发者。
目标：在保持全局一致性的前提下，交付可验证、可维护、前后端打通的功能。

## 1) 基本定位与语言要求

- 项目全局文案、注释、交互提示优先使用中文（必要技术名词可保留英文）。
- 你在本仓库的默认目标：健壮性、全局一致性、真实交互、真实数据、样式一致。
- 禁止把“可点击原型”当最终结果：页面必须尽量由后端真实数据驱动。

## 2) 项目架构速览

- 后端：Python + SQLAlchemy + Alembic + Service 层。
- 桌面壳：PySide6 + QWebEngineView + QWebChannel。
- 前端：原生 HTML/CSS/JS（无 React/Vue，无打包器）。
- 数据库：SQLite（默认 `%APPDATA%/TK-OPS-ASSISTANT/tk_ops.db`）。
- 桥接：Python `Bridge(QObject)` <-> JS `window.backend`/`window.api`。

关键路径：

- 启动：`desktop_app/main.py` -> `desktop_app/app.py` -> `desktop_app/ui/web_shell.py`
- 桥：`desktop_app/ui/bridge.py` + `desktop_app/assets/js/bridge.js`
- 前端数据层：`desktop_app/assets/js/data.js`（统一调用、缓存与失效）
- 页面路由与加载：`desktop_app/assets/js/routes.js` + `desktop_app/assets/js/page-loaders.js`

## 3) 常用命令（Windows）

### 3.1 环境与依赖

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3.2 运行应用

```powershell
venv\Scripts\python.exe desktop_app\main.py
```

### 3.3 测试（重点：单测）

```powershell
# 全量
venv\Scripts\python.exe -m pytest tests/ -v

# 单文件
venv\Scripts\python.exe -m pytest tests/test_dev_seed_service.py -v

# 单用例（最常用）
venv\Scripts\python.exe -m pytest tests/test_dev_seed_service.py::test_seed_development_data_is_idempotent -v

# 关键字过滤
venv\Scripts\python.exe -m pytest tests/ -k "bridge and runtime" -v
```

### 3.4 迁移与数据库

```powershell
# 推荐：程序化初始化/升级（更贴合项目现状）
venv\Scripts\python.exe -c "from desktop_app.database import init_db; init_db(); print('db ok')"

# Alembic 命令（按需）
venv\Scripts\python.exe -m alembic revision --autogenerate -m "your message"
venv\Scripts\python.exe -m alembic upgrade head
```

### 3.5 构建

```powershell
python build.py --clean
python build.py --ico-only
```

说明：仓库目前没有稳定启用的代码检查/格式化命令；提交前至少运行相关 pytest。

## 4) 前后端连通性硬约束

- QWebChannel 注册对象名是 `backend`，不是 `bridge`。
- JS 侧优先通过 `window.api`（`data.js`）调用，不要在业务代码里散落直接 `window.backend.xxx`。
- Bridge 返回统一 JSON 信封：
  - 成功：`{ "ok": true, "data": ... }`
  - 失败：`{ "ok": false, "error": "..." }`
- 新增 Bridge 方法时，遵循既有模式：
  - `@Slot(..., result=str)`
  - `@_safe`
  - 返回 `_ok(...)` / `_err(...)`
- 数据变更后要触发 `dataChanged`，让前端缓存失效并刷新。

## 5) 新增/改造页面检查清单

新增页面通常至少涉及以下点（缺一容易“看得见点不动”）：

1. `routes.js`：新增路由元数据（`mainTemplate/detailTemplate/audit/sidebarSummary` 等）。
2. `app_shell.html`：补充对应模板（命名遵循 `route-<name>-main` / `route-<name>-detail-*`）。
3. `page-loaders.js`：新增加载器，接入真实 API 与运行时摘要。
4. `bindings.js`：绑定关键按钮与交互动作（创建/编辑/删除/筛选/详情）。
5. `data.js`：若需新后端能力，补充 `window.api` 分组方法。
6. `bridge.py` + service/repository：补齐后端槽函数与业务逻辑。
7. `tests/`：新增或更新页面审计、桥接契约、行为真值测试。

## 6) Python 代码规范

- 文件头：`from __future__ import annotations`。
- 导入顺序：标准库 -> 第三方库 -> 本地模块（`desktop_app.*` 绝对导入）。
- 类型：优先完整类型标注，使用 `|` 联合类型与 `Mapped[...]`（ORM）。
- 命名：`snake_case`（函数/变量），`PascalCase`（类），`UPPER_SNAKE_CASE`（常量）。
- 日志：模块级 `log = logging.getLogger(__name__)`，异常记录用 `log.exception(...)`。
- 事务：优先 `session_scope()`；异常时要可回滚，不吞关键错误。
- 错误处理：
  - UI 可感知错误必须转为明确中文错误信息。
  - Bridge 层不得把 traceback 直接暴露给用户。
- 改动原则：小步提交、最小必要修改，避免无关重构。

## 7) JavaScript/CSS 规范

- JS 采用仓库现有模式（IIFE + 模块化全局对象）。
- 统一通过 `api.*` 获取数据，避免重复封装后端调用。
- 交互异常必须有 UI 反馈（toast/提示/状态位），不可静默失败。
- CSS 必须使用 `variables.css` 中设计令牌：颜色、间距、圆角、阴影、层级。
- 禁止随意硬编码颜色/尺寸，优先变量（例如 `--brand-primary`、`--space-*`）。
- 样式调整要同时考虑明暗主题，避免只修 light 或只修 dark。

## 8) 数据真实性与健壮性

- 禁止新增“看起来真实”的硬编码业务数字（ROI、利润、转化等）。
- 无真实后端数据时，使用中性空态/占位态，并明确可恢复路径。
- 外部依赖（AI、网络、文件、更新）必须有超时、失败兜底、可重试提示。
- 对关键动作（删除、覆盖、批量）提供二次确认与结果反馈。
- 任何可能影响全局状态的改动，必须检查 `dataChanged` 与缓存失效链路。

## 9) 测试策略

- 功能改动最少跑“改动相关测试 + 1 条主链路回归”。
- Bridge 改动：至少补/跑桥接契约类测试。
- 页面交互改动：至少补/跑页面审计与运行时数据相关测试。
- 数据层改动：至少补/跑持久化、实体、服务层测试。
- 提交前建议：`venv\Scripts\python.exe -m pytest tests/ -v`。

## 10) 环境变量与运行时约定

- `TK_OPS_DATA_DIR`：覆盖数据目录。
- `TKOPS_DB_PATH`：覆盖数据库文件路径。
- `TKOPS_SKIP_DB_AUTO_INIT=1`：跳过导入时自动初始化（用于特定脚本/测试）。
- `APPDATA`：Windows 默认数据库落盘位置依赖此变量。

## 11) 与 AI 代理相关的仓库规则文件

- 未发现 `.cursor/rules/` 或 `.cursorrules`。
- 未发现 `.github/copilot-instructions.md`。
- 存在 `.github/agents/worst-user-ui.agent.md`：
  - UI/UX 任务要求低认知负担、强容错、明确反馈、温和文案。
  - 适用于表单、引导、错误处理、关键流程体验优化。

注意：`胶水开发` Agent 的工作流程已调整——已移除“验证集成 / 本地验证”步骤，当前工作流程为 1-4 步（分析需求、查找依赖、验证可用性、编写胶水）。详细内容见 `.github/agents/胶水开发.agent.md`。

## 12) 常见陷阱

- 不要把 `window.bridge` 当调用入口；当前真实入口是 `window.backend`，业务封装入口是 `window.api`。
- 不要只改前端模板不改 loader/bindings/bridge；否则“页面能看不能用”。
- 不要绕过 service 直接在 UI 层拼业务规则。
- 不要在样式上引入破坏性全局覆盖，优先局部、可回归的修改。
- 不要跳过测试就宣称完成。

## 13) 交付标准

- 代码遵循上述风格与命名规范。
- 页面有真实数据路径，前后端已打通。
- 异常路径可见、可恢复、可追踪（日志 + UI 反馈）。
- 相关测试通过，至少含 1 条单测级验证。
- 文案、交互、样式与全局视觉语言一致。

## 14) Superpowers 工作流规则

- 当前仓库内，所有非简单工程任务强制先走 superpowers 工作流。
- 固定顺序：先生成 `docs/superpowers/plans/YYYY-MM-DD-topic.md`，经你审批通过后，再生成 `docs/superpowers/specs/YYYY-MM-DD-topic-design.md`，最后才进入实现。
- 非简单工程任务默认包括：多文件改动、架构调整、前后端契约变更、模块拆分、主链路功能改造、测试体系重构。
- 可不强制走完整流程的范围仅限：纯问答、只读分析、单文件低风险小修、纯文案微调。
- 所有大改必须分阶段推进。plan 中必须明确阶段目标、文件地图、验证方式、边界与回退点；未经批准不得跳过 plan 直接写 spec 或直接编码。
- 当实现范围明显超出已批准的 plan / spec 时，必须先回到文档更新，再继续开发，禁止边做边漂移。
- 若本仓库已有可复用的 superpowers 样板，优先沿用既有结构与命名，不额外发明第二套模板。

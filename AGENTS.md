# AGENTS.md - TK-OPS 代理协作手册

面向本仓库的 AI 编码代理与新加入开发者。
目标：在保持全局一致性的前提下，交付可验证、可维护、前后端打通的功能。

## 1) 基本定位与语言要求

- 项目全局文案、注释、交互提示优先使用中文（必要技术名词可保留英文）。
- 你在本仓库的默认目标：健壮性、全局一致性、真实交互、真实数据、样式一致。
- 禁止把“可点击原型”当最终结果：页面必须尽量由后端真实数据驱动。

## 1.1) 不可妥协的硬约束

- 禁止大文件：不允许再出现单文件数千行实现，所有模块必须按职责边界合理拆分。
- 禁止双壳并存运行：旧 PySide6 壳只允许作为迁移参考，不再进入运行、联调、打包、灰度和发布路径。
- 保证全局性：所有新开发必须遵循统一架构、统一规范、统一目录边界，避免局部特例破坏整体一致性。
- 全局采用中文注释：新增注释必须使用中文，并保持简洁，只解释代码意图、边界和复杂逻辑。
- 全局异常处理以及日志记录：所有异常必须被捕获、记录并转换为可见反馈；日志格式和错误处理方式必须统一。
- 全局配置总线：所有配置必须通过统一配置入口或配置总线管理，禁止页面、脚本、服务各自保存一套配置。

## 2) 项目架构速览

- 桌面壳：Tauri 2 + Vue 3 + TypeScript + Vite。
- 业务运行时：Python + FastAPI + SQLAlchemy + Alembic + Service 层。
- 前端状态与路由：Pinia + Vue Router。
- 数据库：SQLite（默认 `%APPDATA%/TK-OPS-ASSISTANT/tk_ops.db`）。
- 旧壳 `desktop_app/`：仅保留为迁移参考与运行时复用来源，不再作为默认入口。

关键路径：

- 启动：`scripts/dev.ps1` -> `apps/desktop` + `apps/py-runtime`
- 桌面宿主：`apps/desktop/src/main.ts` -> `apps/desktop/src/layouts/AppShell.vue`
- 运行时入口：`apps/py-runtime/src/`
- 前端数据层：`apps/desktop/src/modules/runtime/runtimeApi.ts`
- 路由真源：`apps/desktop/src/app/router/routeManifest.ts` + `apps/desktop/src/app/router/routes.ts`

## 3) 常用命令（Windows）

### 3.1 环境与依赖

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3.2 运行应用

```powershell
scripts\dev.ps1

# 仅运行 runtime
scripts\dev.ps1 -RuntimeOnly

# 仅运行桌面端
scripts\dev.ps1 -DesktopOnly
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
scripts\build-runtime.ps1
scripts\build-desktop.ps1 -SmokeRuntime
scripts\release.ps1
```

说明：仓库目前没有稳定启用的代码检查/格式化命令；提交前至少运行相关 pytest。

## 4) 单壳与运行边界硬约束

- 不允许旧 PySide6 壳与新 Tauri 壳在任何环境下并行运行。
- `desktop_app/` 只允许作为迁移参考、数据模型与部分服务复用来源，不再作为默认桌面入口。
- 新功能默认只允许落在 `apps/desktop` 与 `apps/py-runtime`。
- 前后端统一通过 runtime HTTP / WebSocket 通信，默认前端入口是 `runtimeApi.ts`，不得回退到旧桥接调用模式。
- Runtime 返回统一 JSON 信封：
  - 成功：`{ "ok": true, "data": ... }`
  - 失败：`{ "ok": false, "error": "..." }`
- 数据变更后必须同步处理前端缓存失效、任务刷新与状态广播，不允许静默漂移。

## 5) 新增/改造页面检查清单

新增页面通常至少涉及以下点（缺一容易“看得见点不动”）：

1. `apps/desktop/src/app/router/routeManifest.ts`：新增路由元数据与迁移状态。
2. `apps/desktop/src/app/router/routes.ts`：注册真实页面组件，而不是继续占位。
3. `apps/desktop/src/pages/`：落页面骨架，并与旧壳结构做 1:1 映射。
4. `apps/desktop/src/modules/`：拆出数据层、helpers、types，不把页面和逻辑堆成大文件。
5. `apps/desktop/src/styles/`：补局部样式文件，保持样式职责清晰。
6. `apps/py-runtime/src/`：若需新增后端能力，补 service / routes / repository 的最小闭环。
7. `tests/`：新增或更新页面审计、runtime 契约、行为真值测试。

## 6) Python 代码规范

- 文件头：`from __future__ import annotations`。
- 导入顺序：标准库 -> 第三方库 -> 本地模块（优先 `apps.py-runtime.*` 或共享模块绝对导入）。
- 类型：优先完整类型标注，使用 `|` 联合类型与 `Mapped[...]`（ORM）。
- 命名：`snake_case`（函数/变量），`PascalCase`（类），`UPPER_SNAKE_CASE`（常量）。
- 日志：模块级 `log = logging.getLogger(__name__)`，异常记录用 `log.exception(...)`。
- 事务：优先 `session_scope()`；异常时要可回滚，不吞关键错误。
- 错误处理：
  - UI 可感知错误必须转为明确中文错误信息。
  - FastAPI / service 层不得把 traceback 直接暴露给用户。
- 注释规范：新增注释必须使用中文，且只在复杂逻辑、边界条件、外部依赖编排处添加必要注释。
- 配置规范：配置读取与写入必须经过统一配置入口，不允许散落在模块内部自行管理。
- 改动原则：小步提交、最小必要修改，避免无关重构。

## 7) JavaScript/CSS 规范

- TS / Vue 代码优先采用页面、composable、helpers、types 分层拆分，禁止继续堆出超大页面文件。
- 统一通过 `runtimeApi.*` 获取数据，避免重复封装后端调用。
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
- 所有新配置项都必须接入统一配置总线或统一 settings 入口，禁止新增游离环境变量作为默认主路径配置。

## 11) 与 AI 代理相关的仓库规则文件

- 未发现 `.cursor/rules/` 或 `.cursorrules`。
- 未发现 `.github/copilot-instructions.md`。
- 存在 `.github/agents/worst-user-ui.agent.md`：
  - UI/UX 任务要求低认知负担、强容错、明确反馈、温和文案。
  - 适用于表单、引导、错误处理、关键流程体验优化。

注意：`胶水开发` Agent 的工作流程已调整——已移除“验证集成 / 本地验证”步骤，当前工作流程为 1-4 步（分析需求、查找依赖、验证可用性、编写胶水）。详细内容见 `.github/agents/胶水开发.agent.md`。

## 12) 常见陷阱

- 不要把旧 PySide6 壳重新拉回运行链路、联调链路或打包链路。
- 不要只改前端页面不改数据层、详情联动、测试和迁移文档；否则“页面能看不能用”。
- 不要绕过 service 直接在 UI 层拼业务规则。
- 不要把配置写死在页面、脚本、服务内部；统一走配置总线。
- 不要在样式上引入破坏性全局覆盖，优先局部、可回归的修改。
- 不要跳过测试就宣称完成。

## 13) 交付标准

- 代码遵循上述风格与命名规范。
- 无单文件数千行实现，模块拆分符合职责边界。
- 新链路中不存在双壳并行运行或旧壳回流。
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

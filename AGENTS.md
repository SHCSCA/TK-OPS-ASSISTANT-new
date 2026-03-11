# AGENTS.md

本文件为 `TK-OPS-ASSISTANT-new` 仓库中的编码代理提供仓库级工作说明。
在本仓库内工作时，优先遵循这里的规则，而不是通用 Python 建议。

## 1. 仓库概览

- 项目类型：基于 Python 3.11+ 与 PySide6 的桌面应用。
- 主包目录：`desktop_app/`。
- GUI 主入口：`desktop_app/main.py`。
- 新架构组装根：`desktop_app/app.py`。
- CLI MVP 入口：`desktop_app/cli_mvp.py`。
- 数据层：SQLite + SQLAlchemy。
- 架构风格：Clean Architecture / MVVM / 路由驱动 Shell。
- 测试目录：`desktop_app/tests/`。

## 2. 仓库中的规则文件

- 未发现 Cursor 规则目录：`.cursor/rules/`。
- 未发现 `.cursorrules`。
- 未发现 Copilot 指令文件：`.github/copilot-instructions.md`。
- 如果后续新增这些文件，应将其视为比本文件更高优先级的规则来源。

## 3. 环境准备

- 使用 Python 3.11+。
- 如需虚拟环境：
  - PowerShell：`py -3.11 -m venv .venv`
  - 激活：`.\.venv\Scripts\Activate.ps1`
- 安装运行依赖：
  - `pip install -r .\desktop_app\requirements.txt`
- 测试依赖需要单独安装：
  - `pip install pytest pytest-qt`
- Widget 与 smoke 测试依赖 `pytest-qt` 提供 Qt 支持。

## 4. 构建 / 运行命令

- 仓库中没有正式的打包流水线。
- 除非任务涉及发布或打包，否则可将“build”理解为“运行应用或运行测试”。
- 运行桌面应用：
  - `python .\desktop_app\main.py`
- 运行 CLI MVP：
  - `python .\desktop_app\cli_mvp.py`
- 在代码审查或调试时，可从 `desktop_app.app` 作为组装根开始阅读。

## 5. 测试命令

- `pyproject.toml` 已配置 pytest。
- 默认测试根目录：`desktop_app/tests`。
- 已定义 marker：
  - `slow`
  - `widget`
  - `smoke`
- 运行全部测试：
  - `python -m pytest -q`
- 运行单个测试文件：
  - `python -m pytest desktop_app/tests/unit/core/test_theme_engine.py -q`
- 运行单个测试函数：
  - `python -m pytest desktop_app/tests/unit/core/test_theme_engine.py::test_toggle_switches_between_modes -q`
- 运行指定关键字测试：
  - `python -m pytest -k theme -q`
- 只运行 smoke 测试：
  - `python -m pytest -m smoke -q`
- 只运行 widget 测试：
  - `python -m pytest -m widget -q`
- smoke 单测示例：
  - `python -m pytest desktop_app/tests/smoke/test_page_loading.py::test_dashboard_page_instantiates -q`
- widget 单测示例：
  - `python -m pytest desktop_app/tests/widgets/components/test_theme_switching.py::test_toggle_changes_stylesheet -q`

## 6. 静态检查 / 类型检查

- 仓库里没有固定的 Ruff / Black / isort / Flake8 配置文件。
- 未经用户要求，不要假设仓库强制使用某个格式化工具。
- 当前代码大量使用内联 Pyright 指令。
- 如果本地可用，优先使用：
  - `basedpyright desktop_app`
- 也可使用：
  - `pyright desktop_app`
- 如果你引入新的 lint 工具，必须在变更中说明。
- 即使未运行格式化工具，也要保证改动与周围代码风格一致。

## 7. 测试说明

- 仓库已有 unit、integration、widget、smoke 四类测试。
- 共享 fixture 位于：`desktop_app/tests/conftest.py`。
- 常用 fixture 包括：
  - `qapp`
  - `fake_config`
  - `fake_db`
  - `fake_services`
- 纯逻辑优先写 unit test。
- 涉及 SQLAlchemy / 持久化行为优先写 integration test。
- 涉及 PySide6 交互优先写 widget test。
- 涉及页面是否能安全加载优先写 smoke test。

## 8. 导入约定

- 优先遵循当前文件附近已有的导入风格，不要全局重写导入方式。
- `desktop_app` 内部大多数模块使用显式相对导入。
- 入口脚本可能会保留绝对导入回退，以支持脚本模式运行。
- 导入分组顺序：
  - 标准库
  - 第三方库
  - 本地包导入
- 不要使用通配符导入。
- 不要保留未使用导入。
- 如果周围代码通过 `desktop_app.core.qt` 导入 Qt 类型，就继续沿用，不要直接改成 `PySide6`。

## 9. 模块结构约定

- 大多数新 Python 模块应以 `from __future__ import annotations` 开头。
- 保留现有模块级 Pyright 注释，例如 `# pyright: basic`。
- 使用简洁的三引号模块文档字符串。
- 辅助函数优先放在调用点附近；只有在可复用时再抽离。
- 优先使用小而专注的类，避免大而混杂的职责集合。

## 10. 格式约定

- 与被修改文件的现有格式保持一致。
- 使用 4 个空格缩进。
- 行宽保持可读，不要为了压缩长度牺牲可维护性。
- 多行字面量和多行调用中，若能改善 diff，可保留尾随逗号。
- 默认使用双引号，除非当前文件明显采用其他风格。
- 空行数量遵循 PEP 8 与周边文件风格。

## 11. 类型约定

- 新增的公共函数、方法、类属性应补充类型标注。
- 使用现代 Python 类型语法，例如 `X | None`、`dict[str, object]`。
- 如适用，复用 `desktop_app/core/types.py` 中已有类型。
- 当契约更清晰时，优先考虑 `NewType`、`Enum`、`NamedTuple`、类型别名。
- 只有在运行时行为正确、但静态分析需要协助时，才使用 `cast(...)`。
- 不要随意删除现有有价值的 Pyright 抑制；只有真正修复问题后再移除。

## 12. 命名约定

- 模块、函数、变量：`snake_case`。
- 类：`PascalCase`。
- 常量：`UPPER_SNAKE_CASE`。
- Qt 信号名、状态字段名要明确、可读。
- 一旦被测试或 UI 绑定依赖，`route_id`、配置键名、服务名应保持稳定。

## 13. 错误处理

- 能精确捕获时就捕获具体异常。
- 持久化代码在事务失败时应先 rollback，再继续抛出异常。
- 配置或文件解析失败时，优先安全回退到默认值，而不是直接让应用崩溃。
- 包装异常时使用 `raise ... from exc` 保留上下文。
- 除非当前代码明确设计为降级运行，否则不要静默吞错。
- 不要在常规业务流程里随意引入没有边界说明的 `except Exception`。

## 14. 日志与副作用

- 优先使用结构化运行逻辑，而不是临时 `print`。
- 修改核心服务时，尽量复用现有日志与运行时基础设施。
- UI 代码不要混入过多业务逻辑和重 I/O。
- 不要阻塞 Qt 事件循环。
- 涉及异步或流式流程时，保留取消、状态更新和信号语义。

## 15. Qt / UI 约定

- 路由注册应放在组装根或 Shell 注册层。
- 页面与组件聚焦展示和交互，不要承担核心业务决策。
- 可复用 UI 组件优先放在 `desktop_app/ui/components/`。
- 新增可交互部件时，如测试需要，优先提供稳定的 `objectName`。
- 保持与 `desktop_app/ui/shell/` 中现有主题和壳层风格一致。

## 16. 数据层与服务层约定

- Repository 负责 CRUD 与事务边界，不要把这些逻辑放进 UI。
- Service 表达业务行为，并负责编排 repository / adapter。
- 如果测试里已经使用 fake 或 stub，新增代码时优先延续依赖注入方式。
- SQLite / SQLAlchemy 相关行为尽量通过 integration test 验证，而不是深度 mock。

## 17. 代理工作流要求

- 修改前先查看相邻文件，并匹配其风格。
- 用最小改动解决完整问题。
- 不要只为了“统一风格”而重写大文件。
- 行为变化时，应增加或更新测试。
- 修改测试时，优先运行最小范围的 pytest 命令验证。
- 如果因缺少依赖导致测试不能运行，要明确说明原因。

## 18. 仓库特定观察

- `pyproject.toml` 中定义了 pytest 的发现规则与 markers。
- 运行时依赖中未包含 `pytest` 与 `pytest-qt`。
- 如果没有安装 `pytest-qt`，本地运行 pytest 时可能出现 `qt_api` 配置警告。
- 代码库同时包含英文基础设施代码与中文 UI / 业务文本；修改时应保留既有面向用户的语言风格。

## 19. 默认验证顺序

- 纯 Python 逻辑：运行最小相关 unit test。
- Repository / 数据库改动：运行相关 integration test。
- Qt 改动：先运行最小 widget test；若影响路由或页面加载，再补充 smoke test。
- 大范围重构：如条件允许，运行 `python -m pytest -q`。

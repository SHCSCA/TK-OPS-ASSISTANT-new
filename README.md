[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.x-41CD52.svg)](https://doc.qt.io/qtforpython-6/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#许可证-license)

# TK-OPS Desktop Application

TK-OPS 是一个面向 TikTok Shop 运营团队的 Windows 桌面应用，聚焦账号管理、内容生产、数据分析、自动化运营与 AI 工作流，目标是把高频运营动作收敛到统一桌面工作台中。

## 项目简介 (Project Overview)

当前仓库包含两条并行演进路线：

- `desktop_app/main.py`，高保真 GUI 原型入口
- `desktop_app/cli_mvp.py`，CLI MVP 入口
- `desktop_app/app.py`，新一代 Route 驱动桌面 Shell 的组装根

项目已经具备以下基础能力：

- 基于 **Python 3.11+** 与 **PySide6 6.x** 的 Windows 桌面应用骨架
- 基于 **SQLite + SQLAlchemy 2.x** 的本地数据层
- 基于 **Clean Architecture + MVVM** 的模块组织方式
- 基于 **Plugin Shell** 的统一导航与页面宿主机制
- 基于 **ConfigBus** 的配置总线与持久化能力
- 基于 **ThemeEngine** 的主题令牌与 QSS 引擎
- 基于 **RouteRegistry** 的路由注册与页面挂载能力
- 基于 **LiteLLM Adapter** 的多 Provider AI 适配预留
- 覆盖 **9 个业务域、26 个页面** 的 PySide6 交互式原型

仓库同时保留设计稿、规划文档、测试结构与服务层骨架，适合继续做原型完善，也适合逐步工程化。

## 功能特性 (Features)

### 产品能力

- 统一桌面工作台，按业务域组织导航
- 已实现 26 个页面的高保真交互原型
- 支持账号、分组、设备、素材、脚本、分析、调度、CRM 等场景
- 支持 AI Provider 配置、模型目录、连接测试与适配器扩展
- 支持亮色 / 暗色主题
- 支持右侧详情区、状态栏、QStackedWidget 页面切换等桌面交互模式

### 工程能力

- Plugin Shell
- Route 驱动页面注册
- 配置快照、订阅、持久化
- 主题 Token 解析与 QSS 生成
- 数据模型与 Repository 分层
- `unit / integration / widgets / smoke` 测试目录结构

## 技术栈 (Tech Stack)

| 分类 | 技术 | 说明 |
|---|---|---|
| 语言 | Python 3.11+ | 推荐运行版本 |
| 桌面框架 | PySide6 6.x | GUI、信号槽、QWidget 体系 |
| 数据库 | SQLite | 默认本地数据库 |
| ORM | SQLAlchemy 2.x | 模型、会话、仓储层 |
| AI 接入 | OpenAI API | 旧版 MVP 与 CLI 已接入 |
| AI 适配层 | LiteLLM | 多 Provider 统一适配入口 |
| 网络 | httpx | 网络请求依赖 |
| 异步 SQLite | aiosqlite | 异步数据库能力预留 |
| 配置 / DTO | Pydantic | 依赖中已声明 |
| 测试 | pytest、pytest-qt | `pyproject.toml` 已配置 pytest |

### 已落地的架构关键词

- Clean Architecture
- MVVM
- plugin shell
- ConfigBus
- ThemeEngine
- RouteRegistry

## 系统架构 (Architecture)

新架构入口位于 `desktop_app/app.py`。核心流程是创建应用对象、配置总线、主题引擎、数据库、服务注册表、路由注册表，再创建统一 Shell 主窗口。

### 分层说明

| 层 | 目录 | 职责 |
|---|---|---|
| App Composition | `desktop_app/app.py` | 组装 QApplication、Database、Services、Routes |
| Core | `desktop_app/core/` | 配置、主题、Shell、运行时、安全、类型 |
| Services | `desktop_app/services/` | 账号、AI、分析、自动化、内容、运营服务 |
| Data | `desktop_app/data/` | SQLAlchemy 模型、数据库、仓储 |
| UI | `desktop_app/ui/` | Shell、页面、可复用组件 |
| Docs | `docs/planning/` | 页面盘点、IA、测试策略、设计令牌 |
| Mockups | `stitch_text_document/` | 设计稿来源 |

### ASCII 架构图

```text
┌──────────────────────────────────────────────────────────────────┐
│                         TK-OPS Desktop                          │
├──────────────────────────────────────────────────────────────────┤
│ GUI: desktop_app/main.py                                        │
│ CLI: desktop_app/cli_mvp.py                                     │
│ New App Root: desktop_app/app.py                                │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                v
┌──────────────────────────────────────────────────────────────────┐
│ Application Composition Root                                     │
│ TKOpsApp                                                         │
│ - QApplication                                                   │
│ - ConfigBus                                                      │
│ - ThemeEngine                                                    │
│ - Database                                                       │
│ - ServiceRegistry                                                │
│ - RouteRegistry                                                  │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                v
┌──────────────────────────────────────────────────────────────────┐
│ Plugin Shell                                                     │
│ TitleBar + Sidebar + PageHost + StatusBar                        │
│ MainWindow(route_registry, navigation_model, theme_engine, ...)  │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                v
┌──────────────────────────────────────────────────────────────────┐
│ UI Pages                                                         │
│ dashboard / account / content / analytics / automation / ai      │
│ system / crm / operations                                        │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                v
┌──────────────────────────────────────────────────────────────────┐
│ Services                                                         │
│ account / ai / analytics / automation / content / operations     │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                v
┌──────────────────────────────────────────────────────────────────┐
│ Data                                                             │
│ SQLite + SQLAlchemy Models + Repositories                        │
└──────────────────────────────────────────────────────────────────┘
```

### Shell 结构

```text
+--------------------------------------------------------------------------------+
| TitleBar, 页面标题, 搜索, 全局状态                                              |
+----------------------+---------------------------------------------------------+
| Sidebar              | PageHost / QStackedWidget                               |
| - Main               | - Dashboard                                             |
| - 运营经理专区       | - Account                                               |
| - 内容创作者专区     | - Content / AI                                          |
| - 数据分析师专区     | - Analytics                                             |
| - 自动化运营专区     | - Automation                                            |
| - System             | - System / CRM                                          |
+----------------------+---------------------------------------------------------+
| StatusBar, 页面提示, 运行状态, 连接状态                                         |
+--------------------------------------------------------------------------------+
```

## 项目结构 (Project Structure)

以下目录树根据仓库当前实际目录整理，已先通过扫描确认。

```text
TK-OPS-ASSISTANT-new/
├── AGENTS.md
├── pyproject.toml
├── desktop_app/
│   ├── __init__.py
│   ├── app.py
│   ├── cli_mvp.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── ai/
│   │   ├── __init__.py
│   │   └── openai_client.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── qt.py
│   │   ├── signals.py
│   │   ├── types.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── bus.py
│   │   │   ├── migration.py
│   │   │   └── schema.py
│   │   ├── runtime/
│   │   │   ├── __init__.py
│   │   │   ├── cancellation.py
│   │   │   ├── command.py
│   │   │   ├── event_bus.py
│   │   │   └── worker.py
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   └── secret_store.py
│   │   ├── shell/
│   │   │   ├── __init__.py
│   │   │   ├── lifecycle.py
│   │   │   ├── navigation.py
│   │   │   └── registry.py
│   │   └── theme/
│   │       ├── __init__.py
│   │       ├── engine.py
│   │       ├── qss.py
│   │       └── tokens.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models/
│   │   └── repositories/
│   ├── pipeline/
│   │   └── pipeline.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── account/
│   │   ├── ai/
│   │   ├── analytics/
│   │   ├── automation/
│   │   ├── content/
│   │   └── operations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── _pytest_stub.py
│   │   ├── conftest.py
│   │   ├── fakes/
│   │   ├── integration/
│   │   ├── smoke/
│   │   ├── unit/
│   │   └── widgets/
│   ├── tiktok/
│   │   ├── __init__.py
│   │   └── api_client.py
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py
│       ├── components/
│       ├── pages/
│       │   ├── account/
│       │   ├── ai/
│       │   ├── analytics/
│       │   ├── automation/
│       │   ├── content/
│       │   ├── crm/
│       │   ├── dashboard/
│       │   ├── operations/
│       │   └── system/
│       └── shell/
│           ├── main_window.py
│           ├── sidebar.py
│           ├── status_bar.py
│           └── title_bar.py
├── docs/
│   └── planning/
│       ├── PLN-01-page-inventory.md
│       ├── PLN-02-information-architecture.md
│       ├── PLN-03-tdd-strategy.md
│       └── PLN-04-design-tokens.md
├── stitch_text_document/
│   ├── ANALYSIS.md
│   ├── tk_ops/
│   ├── crm/
│   ├── ai_1/
│   ├── ai_2/
│   └── _1 ... _24/
└── venv/
```

### 目录补充说明

- `desktop_app/core/` 是架构底座
- `desktop_app/services/` 是业务服务层
- `desktop_app/data/` 是数据库与仓储层
- `desktop_app/ui/pages/` 是页面实现层
- `docs/planning/` 是项目规划文档来源
- `stitch_text_document/` 是 26 个页面设计稿来源

## 快速开始 (Quick Start)

### 环境要求 (Prerequisites)

- Windows 10/11
- Python 3.11+
- pip
- 建议使用虚拟环境

### 1. 克隆仓库

```powershell
git clone <your-repo-url>
cd TK-OPS-ASSISTANT-new
```

### 2. 创建虚拟环境

```powershell
py -3.11 -m venv .venv
```

### 3. 激活虚拟环境

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

CMD:

```bat
.\.venv\Scripts\activate.bat
```

### 4. 安装依赖

```powershell
pip install -r .\desktop_app\requirements.txt
```

### 5. 配置环境变量

如果需要启用 OpenAI，先设置 `OPENAI_API_KEY`。

PowerShell:

```powershell
$env:OPENAI_API_KEY="sk-xxxx"
```

CMD:

```bat
set OPENAI_API_KEY=sk-xxxx
```

### 6. 运行 GUI 原型

```powershell
python .\desktop_app\main.py
```

### 7. 运行 CLI MVP

```powershell
python .\desktop_app\cli_mvp.py
```

### 8. 新架构入口说明

如果你要阅读新架构，请先从以下文件开始：

- `desktop_app/app.py`
- `desktop_app/ui/shell/main_window.py`
- `desktop_app/core/config/bus.py`
- `desktop_app/core/theme/engine.py`
- `desktop_app/core/shell/registry.py`

## 开发指南 (Development Guide)

### 推荐阅读顺序

1. `AGENTS.md`
2. `docs/planning/PLN-01-page-inventory.md`
3. `docs/planning/PLN-02-information-architecture.md`
4. `docs/planning/PLN-04-design-tokens.md`
5. `desktop_app/app.py`
6. `desktop_app/ui/shell/main_window.py`

### 关键模块说明

#### `desktop_app/app.py`

- 新架构组装根
- 创建 `QApplication`
- 初始化 `ConfigBus`
- 初始化 `ThemeEngine`
- 初始化 `Database`
- 创建 `ServiceRegistry`
- 注册 26 个实际页面与占位路由

#### `desktop_app/core/config/bus.py`

- 实现 `ConfigBus`
- 提供 get / set / subscribe / save / load / snapshot
- 支持 schema、migration、JSON 持久化与信号通知

#### `desktop_app/core/theme/engine.py`

- 实现 `ThemeEngine`
- 负责 light / dark 切换
- 负责 Token 解析与 QApplication 样式应用

#### `desktop_app/core/shell/registry.py`

- 实现 `RouteRegistry`
- 实现 `PageHost`
- 负责页面注册、创建、缓存、激活

#### `desktop_app/services/ai/config_service.py`

- 管理 Provider、模型目录、当前激活模型
- 支持 API Key、Base URL、连接测试
- 支持 OpenAI、Anthropic、Ollama、OpenAI Compatible 等内置 Provider

#### `desktop_app/services/ai/adapters/litellm_adapter.py`

- 实现 LiteLLM 通用 ProviderAdapter
- 统一封装请求构造、错误分类、响应标准化

### 开发建议

- 新页面优先接入 `RouteRegistry`
- 新配置优先走 `ConfigBus`
- 新主题样式优先走 `ThemeEngine + tokens`
- 新 AI Provider 优先实现 `ProviderAdapter`
- 页面实现时优先对照 `stitch_text_document/` 与 `docs/planning/`

## 测试 (Testing)

仓库根目录的 `pyproject.toml` 已配置 pytest：

- `testpaths = ["desktop_app/tests"]`
- `qt_api = "pyside6"`
- marker 包含 `slow`、`widget`、`smoke`

### 测试目录结构

| 目录 | 用途 |
|---|---|
| `desktop_app/tests/fakes/` | Fake Services 与测试替身 |
| `desktop_app/tests/unit/` | 单元测试 |
| `desktop_app/tests/integration/` | 集成测试 |
| `desktop_app/tests/widgets/` | 组件与页面级 PySide6 测试 |
| `desktop_app/tests/smoke/` | 页面加载、导航、主题切换冒烟测试 |

### 运行测试

```powershell
pytest
```

按目录运行：

```powershell
pytest .\desktop_app\tests\unit
pytest .\desktop_app\tests\integration
pytest .\desktop_app\tests\widgets
pytest .\desktop_app\tests\smoke
```

### 测试策略文档

- `docs/planning/PLN-03-tdd-strategy.md`

该文档定义了以下方向：

- 70 / 20 / 8 / 2 测试金字塔
- pytest + pytest-qt 为主
- Fake Services 驱动开发
- SQLite 真实集成测试
- 主题切换、页面加载、导航切换的回归覆盖

## 主题系统 (Theme System)

项目已经有明确的设计令牌文档和运行时主题引擎。

### 设计系统概览

| 项目 | 值 |
|---|---|
| 主品牌色 | `#00F2EA` |
| Light 背景 | `#F5F8F8` |
| Dark 背景 | `#0F2323` |
| 管理域颜色 | `#FF6B6B` |
| 创作域颜色 | `#4ECDC4` |
| 分析域颜色 | `#95E1D3` |
| 自动化域颜色 | `#F38181` |

### 主题实现

- `desktop_app/core/theme/engine.py`
- `desktop_app/core/theme/qss.py`
- `desktop_app/core/theme/tokens.py`
- `docs/planning/PLN-04-design-tokens.md`

### 主题能力说明

- 支持亮色 / 暗色模式
- 通过 `ThemeEngine` 管理当前主题模式
- 通过 `ConfigBus` 存储 `theme.mode`
- 通过 QSS 对 QApplication 应用样式
- 使用语义化 Token，而不是直接在业务代码中硬编码样式

## AI集成 (AI Integration)

### 当前 AI 结构

| 模块 | 路径 | 作用 |
|---|---|---|
| OpenAI MVP 客户端 | `desktop_app/ai/openai_client.py` | 旧版直接调用 OpenAI |
| Provider 配置服务 | `desktop_app/services/ai/config_service.py` | 管理 Provider、模型与当前选择 |
| LiteLLM 适配器 | `desktop_app/services/ai/adapters/litellm_adapter.py` | 统一多 Provider 推理调用 |
| 流式运行时 | `desktop_app/services/ai/streaming.py` | AI 流式能力预留 |
| Agent 角色服务 | `desktop_app/services/ai/agent_service.py` | AI 角色 / 代理相关能力 |

### 已有 Provider Adapter

- OpenAI
- Anthropic
- Ollama
- OpenAI Compatible
- LiteLLM

### 环境变量

| 变量名 | 说明 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API Key，旧版 GUI 与 CLI MVP 会读取 |

### 使用说明

- 没有配置 `OPENAI_API_KEY` 时，旧版客户端会回退为提示文本
- 新架构更推荐通过 Provider 设置页和密钥存储机制管理配置

## 页面清单 (Page Inventory)

当前规划与代码注册共覆盖 **26 个页面**，分布在 9 个业务域中。

| 序号 | route_id | 页面名称 | 业务域 | 设计稿来源 | 备注 |
|---:|---|---|---|---|---|
| 1 | `dashboard_home` | TK-OPS Dashboard / 概览数据看板 | dashboard | `tk_ops/` | 全局经营看板 |
| 2 | `account_management` | 账号管理 | account | `_1/` | 账号状态与详情 |
| 3 | `visual_editor` | 视觉编辑器 | content | `_2/` | 视频编辑工作区 |
| 4 | `visual_lab` | 可视化实验室 | analytics | `_3/` | 数据图表分析 |
| 5 | `competitor_monitoring` | 竞争对手监控 | analytics | `_4/` | 竞品监控 |
| 6 | `profit_analysis` | 利润分析系统 | analytics | `_5/` | 利润与转化分析 |
| 7 | `ai_provider_settings` | AI供应商配置 | system | `_6/` | Provider 配置 |
| 8 | `blue_ocean_analysis` | 蓝海分析 | analytics | `_7/` | 市场机会分析 |
| 9 | `lan_transfer` | 局域网传输 | system | `_8/` | 传输工具 |
| 10 | `task_queue` | 任务队列 | system | `_9/` | 任务执行队列 |
| 11 | `auto_reply_console` | 自动回复控制台 | automation | `_10/` | 自动回复规则 |
| 12 | `viral_title_studio` | 爆款标题 | ai | `_11/` | 标题优化 |
| 13 | `report_generator` | 数据报告生成器 | analytics | `_12/` | 报告构建与导出 |
| 14 | `setup_wizard` | Setup Wizard / 配置向导 | system | `_13/` | 首次运行引导 |
| 15 | `material_factory` | 素材工厂 | content | `_14/` | 素材库与批处理 |
| 16 | `script_extractor` | 脚本提取工具 | ai | `_15/` | 脚本提取 |
| 17 | `data_collection_assistant` | 数据采集助手 | automation | `_16/` | 数据采集 |
| 18 | `download_manager` | 下载器 | system | `_17/` | 下载解析 |
| 19 | `scheduled_publishing` | 定时发布 | automation | `_18/` | 发布日历 |
| 20 | `network_diagnostics` | 网络诊断 | system | `_19/` | 环境检测 |
| 21 | `task_scheduler` | 任务调度 | system | `_21/` | 调度规则 |
| 22 | `engagement_analysis` | 互动分析 | analytics | `_22/` | 情感趋势与互动洞察 |
| 23 | `product_title_master` | 商品标题大师 | ai | `_23/` | 标题与关键词优化 |
| 24 | `creative_workshop` | 创意工坊 | ai | `_24/` | 批量创作配置 |
| 25 | `ai_content_factory` | AI内容工厂 | ai | `ai_1/` | AI 工作流设计 |
| 26 | `ai_copy_generation` | AI文案生成 | ai | `ai_2/` | 文案生成与合规 |
| 27 | `crm_customer_management` | CRM客户关系管理 | crm | `crm/` | 客户关系工作区 |

### 页面域分布

| 业务域 | 页面数 |
|---|---:|
| dashboard | 1 |
| account | 1 |
| operations | 0 个专项设计稿页，Shell 中含占位路由 |
| content | 2 |
| analytics | 6 |
| automation | 3 |
| ai | 6 |
| system | 7 |
| crm | 1 |

## 贡献指南 (Contributing)

欢迎继续完善这个项目。

### 建议贡献方向

- 完善 `operations` 域真实页面
- 完善服务层与仓储层业务逻辑
- 补齐主题与组件规范
- 增加测试覆盖率
- 打通 TikTok Shop API 真实接入
- 增加打包、发布与 CI/CD

### 提交前建议检查

```powershell
pytest
```

同时建议人工确认：

- 主题切换是否正常
- 路由注册是否正确
- Shell 导航是否正常
- 新页面是否和设计稿一致
- 配置项是否接入 `ConfigBus`

### 代码约定建议

- 页面通过 `RouteRegistry` 接入
- 主题通过 `ThemeEngine` 和 Token 管理
- 配置通过 `ConfigBus` 管理
- AI 扩展通过 `ProviderAdapter` 体系扩展

## 许可证 (License)

README 顶部使用 MIT 徽章。若项目准备正式开源，请在仓库根目录补充 `LICENSE` 文件并明确最终许可证文本。

当前可先按 **MIT** 目标许可证管理。

## 附录 (Appendix)

### 规划文档

| 文档 | 说明 |
|---|---|
| `docs/planning/PLN-01-page-inventory.md` | 26 页面盘点 |
| `docs/planning/PLN-02-information-architecture.md` | 全局信息架构 |
| `docs/planning/PLN-03-tdd-strategy.md` | 测试策略 |
| `docs/planning/PLN-04-design-tokens.md` | 设计令牌与主题规范 |

### 当前状态

已完成：

- PySide6 GUI 原型
- CLI MVP
- ConfigBus
- ThemeEngine
- RouteRegistry
- SQLite + SQLAlchemy 数据层骨架
- AI Provider 配置服务
- LiteLLM Adapter
- 26 页面映射与设计稿盘点

待推进：

- TikTok Shop API 真实接入
- 更完整的数据持久化
- 更系统的测试与 CI
- 桌面端打包发布

### 常用命令

```powershell
# 创建虚拟环境
py -3.11 -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r .\desktop_app\requirements.txt

# 运行 GUI 原型
python .\desktop_app\main.py

# 运行 CLI MVP
python .\desktop_app\cli_mvp.py

# 运行测试
pytest
```

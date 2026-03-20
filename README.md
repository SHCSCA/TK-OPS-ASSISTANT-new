# TK-OPS Desktop Prototype

TK-OPS 是一个面向 TikTok Shop 运营场景的 Windows 桌面原型应用。当前仓库的实际实现形态是：

- Python 负责桌面外壳、数据库、服务层和系统能力
- PySide6 + QtWebEngine 承载桌面窗口
- HTML、CSS、JavaScript 负责大部分页面交互
- Python 与前端通过 QWebChannel 双向通信

这份 README 已按当前仓库现状重写，不再描述已被清理的旧架构文件和阶段性原型资产。

## 当前状态

- 桌面入口已经统一到 desktop_app/main.py
- 应用组装逻辑位于 desktop_app/app.py
- 主窗口使用桌面 Web Shell，入口页面为 desktop_app/assets/app_shell.html
- 数据层使用 SQLite + SQLAlchemy + Alembic
- 前端交互集中在 desktop_app/assets/js
- 打包、许可证签发脚本已整理为中文使用方式

## 技术栈

| 分类 | 技术 | 说明 |
| --- | --- | --- |
| 语言 | Python 3.11+ | 当前桌面应用主语言 |
| 桌面框架 | PySide6 6.10 | QApplication、窗口、托盘、WebEngine |
| 前端 | HTML / CSS / JavaScript | 页面结构、交互、路由与组件行为 |
| 桥接 | QWebChannel | JS 调用 Python 服务 |
| 数据库 | SQLite | 本地数据存储 |
| ORM / 迁移 | SQLAlchemy / Alembic | 模型定义与数据库迁移 |
| 网络 | httpx | 服务侧网络调用 |
| AI 接入 | openai | AI 供应商能力接入基础 |
| 测试 | pytest / pytest-qt | 测试依赖已保留 |

## 目录结构

```text
TK-OPS-ASSISTANT-new/
├── README.md
├── requirements.txt
├── alembic.ini
├── build.py
├── build_exe.bat
├── issue_license.bat
├── installer.iss
├── tk_ops.spec
├── tkops.ico
├── docs/
│   ├── PRD.md
│   └── UI-DESIGN-PRD.md
├── desktop_app/
│   ├── main.py
│   ├── app.py
│   ├── logging_config.py
│   ├── assets/
│   │   ├── app_shell.html
│   │   ├── app_shell.js
│   │   ├── css/
│   │   ├── js/
│   │   └── routes/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── migrations/
│   ├── services/
│   │   ├── account_service.py
│   │   ├── ai_service.py
│   │   ├── asset_service.py
│   │   ├── chat_service.py
│   │   ├── license_service.py
│   │   ├── task_service.py
│   │   ├── updater_service.py
│   │   └── usage_tracker.py
│   └── ui/
│       ├── bridge.py
│       └── web_shell.py
└── tools/
        └── issue_license.py
```

## 核心模块说明

### 1. 桌面启动链路

- desktop_app/main.py
    负责设置全局异常钩子并启动应用
- desktop_app/app.py
    负责初始化日志、数据库、启动页和主窗口
- desktop_app/ui/web_shell.py
    负责主窗口、系统托盘、QWebEngineView、QWebChannel 注册

### 2. 前端资源层

- desktop_app/assets/app_shell.html
    主壳页面
- desktop_app/assets/js/routes.js
    前端路由定义
- desktop_app/assets/js/page-loaders.js
    页面加载与具体动作绑定
- desktop_app/assets/js/bindings.js
    共享按钮绑定和通用交互逻辑
- desktop_app/assets/routes/
    当前保留的局部页面片段

### 3. Python 服务层

Bridge 会把下列服务能力暴露给前端：

- 账号与分组
- 设备
- 任务队列
- AI 供应商与聊天能力
- 资产管理
- 许可证校验
- 更新检查
- 使用统计

### 4. 数据库层

- 默认数据库使用 SQLite
- 开发态优先使用 APPDATA 下目录
- 数据库初始化时会自动执行 Alembic 迁移
- 数据库文件默认位置为：

```text
%APPDATA%/TK-OPS-ASSISTANT/tk_ops.db
```

## 本地运行

### 1. 创建虚拟环境

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 启动桌面应用

```powershell
venv\Scripts\python.exe .\desktop_app\main.py
```

如果你直接在根目录运行系统 Python，可能会因为解释器环境不一致而失败，建议始终使用 venv 里的解释器。

## 打包与发布

### 一键打包 EXE

```powershell
.\build_exe.bat --clean
```

脚本特性：

- 中文输出
- 带进度条
- 参数透传给 build.py
- 构建完成后输出 dist\TK-OPS\TK-OPS.exe

常用参数：

- --clean：构建前清理 build 和 dist
- --ico-only：仅生成图标，不执行 EXE 打包

### 许可证签发

```powershell
.\issue_license.bat self
.\issue_license.bat 829D-598A-6587-A85A --days 365 --tier enterprise
```

支持能力：

- 查看本机机器码
- 交互式签发许可证
- 指定有效期与授权等级
- 校验许可证是否合法

## 数据与配置说明

- 打包后的 EXE 不应把数据库写回安装目录
- 数据库存放在用户目录下，避免升级覆盖
- 窗口大小与状态通过 QSettings 持久化
- 系统托盘提供显示主窗口与退出应用入口

## 当前保留文档

清理后仅保留两份产品级文档：

- docs/PRD.md
- docs/UI-DESIGN-PRD.md

它们分别用于描述产品需求和 UI 设计基线。阶段性盘点、映射、原型导出和临时验收文档已从仓库中移除。

## 开发建议

如果要继续扩展这个仓库，建议按下面的顺序推进：

1. 优先补齐 desktop_app/assets/js 与 Bridge 的接口契约
2. 将前端页面动作统一收口到 page-loaders.js 和 bindings.js
3. 为 Bridge 暴露的高频接口补最基本的 pytest 冒烟测试
4. 打包前始终执行一次 build_exe.bat --clean 验证

## 许可证

仓库当前未在 README 中单独声明额外授权条款，若需要开源或商业分发规范，请补充正式 LICENSE 文件。
│       ├── PLN-01-page-inventory.md
│       ├── PLN-02-information-architecture.md
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
- 页面状态统一通过 `BaseViewModel` 管理，不在 Widget 中写业务逻辑
- 数据访问统一通过 `Repository Protocol`，不直接操作 Session
- 服务层方法返回 `Result[T, Error]`，不用异常驱动控制流

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
- 打通 TikTok Shop API 真实接入
- 增加打包、发布与 CI/CD

### 提交前建议检查

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
```

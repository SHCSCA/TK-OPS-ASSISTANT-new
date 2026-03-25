# TK-OPS Desktop Application

TK-OPS 是一个面向 TikTok Shop 运营团队的 Windows 桌面应用。当前版本已经不再停留在纯前端原型阶段，而是以 Python 后端、SQLite 数据库、QWebChannel bridge、桌面 Web Shell 前端的组合方式运行。

当前发布版本：`1.2.1`

## 这个版本更新了什么

### 1.2.0 更新说明

本次更新收口了 4 个 AI 生成页面的硬编码原型内容：

1. **爆款标题页 (viral-title)**
   - 移除了标题示例（"只有 1% 的人知道的理财秘籍"等）、模板成功率（92%/88%/85%）、指标值（8.4/10、88%、92%）和 A/B 方案硬编码
   - 接入 `runtimeSummaryHandlers['viral-title']`，页面加载后根据供应商配置动态更新侧栏摘要
   - 新增 `pageAudits` 审计条目

2. **脚本提取页 (script-extractor)**
   - 移除了示例视频 URL、提取进度（124/300 帧、02:45）、AI 实时摘要和脚本文案示例
   - 接入 `runtimeSummaryHandlers['script-extractor']`，页面加载后根据供应商配置动态更新侧栏摘要
   - 新增 `pageAudits` 审计条目

3. **商品标题页 (product-title)**
   - 移除了示例商品名称、竞品标题、关键词密度和 AI 生成方案
   - 接入 `runtimeSummaryHandlers['product-title']`，页面加载后根据供应商配置动态更新侧栏摘要
   - 新增 `pageAudits` 审计条目

4. **AI 文案页 (ai-copywriter)**
   - 移除了文案示例（"这款划时代的智能助手"等）、合规分（72）、风险词和建议
   - 接入 `runtimeSummaryHandlers['ai-copywriter']`，页面加载后根据供应商配置动态更新侧栏摘要
   - 新增 `pageAudits` 审计条目

所有 4 个页面的 loader 函数均已改造，在加载时通过 `Promise.all` 并行拉取供应商数据并调用对应的 `runtimeSummaryHandlers`。

### 1.2.1 更新说明

- 修复：账号管理卡片操作过多导致按钮文字溢出的问题，卡片区仅保留高频动作并将低频操作移至详情区；按钮支持多行换行以适配窄卡片显示。


### 1.1.0 更新说明

本版本重点完成了“从可点击原型到真实后端驱动”的一大轮收口：

1. 第一层主链路页面已经真实接线
   - 账号管理、分组管理、设备管理、任务队列、AI 供应商、素材中心、系统设置等页面不再依赖主数据硬编码
   - 创建、编辑、删除、启停、筛选、批量动作已尽量接到真实 bridge / service / repository / database 路径

2. 异步按钮不再只做假反馈
   - 原先只是 toast 的部分操作已改为真实 `Task` 创建与回流
   - task-backed actions 已覆盖测试连接、环境检查、分析类动作等典型路径

3. analytics / experiment / workflow / report 已补最小持久化闭环
   - 新增并接入 `analysis_snapshots`
   - 新增并接入 `report_runs`
   - 新增并接入 `workflow_definitions` / `workflow_runs`
   - 新增并接入 `experiment_projects` / `experiment_views`
   - 新增并接入 `activity_logs`

4. analytics 页面开始以真实聚合为主
   - `profit-analysis`、`ecommerce-conversion`、`fan-profile` 已优先改为真实聚合结果驱动
   - 不再伪造利润、ROI、订单额等当前模型不支持的业务指标
   - 无法真实支撑的区域收口为运营过程指标或真实空态

5. analyst 页面与通知中心进一步改成后端驱动
   - 通知中心不再通过前端 `setTimeout` 模拟系统消息
   - 通知列表改为读取真实 `activity_logs` 与 `tasks` 映射结果
   - `traffic-board`、`competitor-monitor`、`blue-ocean`、`interaction-analysis` 已接入新的后端 aggregate surface
   - analyst 工厂模板中的一批静态示例值已被清理，页面默认态改成中性骨架与真实空态

6. 开发测试数据更完整
   - `DevSeedService` 已扩展为页面查看级 seed
   - 可真实写入账号、分组、素材、任务、活动日志、分析快照、报表、工作流、实验项目与实验视图
   - 再次执行 seed 保持幂等，不会无限重复灌数据

7. 自动化测试覆盖继续增强
   - 新增 bridge contract、page audit、CRUD interaction、task-backed action、analytics aggregate、metric truthfulness、experiment/workflow persistence、notification truthfulness、analyst backend-driven、dev seed 等测试
   - 当前 worktree 已验证 `tests/ -v` 全量通过

## 当前架构

- Python 负责桌面外壳、数据库、服务层、bridge 与系统能力
- PySide6 + QtWebEngine 承载桌面窗口
- HTML / CSS / JavaScript 负责页面结构、交互和运行时渲染
- Python 与前端通过 QWebChannel 双向通信
- SQLite + SQLAlchemy + Alembic 负责本地持久化

## 技术栈

| 分类 | 技术 | 说明 |
| --- | --- | --- |
| 语言 | Python 3.11+ | 桌面应用主语言 |
| 桌面框架 | PySide6 6.10 | QApplication、QWebEngine、系统托盘 |
| 前端 | HTML / CSS / JavaScript | 桌面 Web Shell 与页面逻辑 |
| 桥接 | QWebChannel | JS 调用 Python 服务 |
| 数据库 | SQLite | 本地数据文件 |
| ORM / 迁移 | SQLAlchemy 2.x / Alembic | 模型与迁移管理 |
| HTTP | httpx | 服务侧网络调用 |
| AI 接入 | openai | AI provider 基础能力 |
| 测试 | pytest / pytest-qt | 自动化验证 |

## 目录结构

```text
TK-OPS-ASSISTANT-new/
├── README.md
├── requirements.txt
├── alembic.ini
├── build.py
├── build_exe.bat
├── installer.iss
├── file_version_info.txt
├── desktop_app/
│   ├── main.py
│   ├── app.py
│   ├── logging_config.py
│   ├── assets/
│   │   ├── app_shell.html
│   │   ├── css/
│   │   └── js/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── migrations/
│   ├── services/
│   └── ui/
├── docs/
└── tests/
```

## 核心模块

### 桌面启动链路

- `desktop_app/main.py`：应用入口
- `desktop_app/app.py`：应用组装、数据库初始化、主窗口创建
- `desktop_app/ui/web_shell.py`：桌面壳、QWebEngineView、QWebChannel 注册

### 前端运行时

- `desktop_app/assets/app_shell.html`：桌面主壳页面
- `desktop_app/assets/js/routes.js`：路由元数据与页面工厂
- `desktop_app/assets/js/page-loaders.js`：真实数据加载与页面行为绑定
- `desktop_app/assets/js/bindings.js`：共享交互绑定与按钮落点
- `desktop_app/assets/js/data.js`：bridge API 封装、缓存与回流
- `desktop_app/assets/js/ui-notifications.js`：真实通知渲染

### 服务层

- `desktop_app/services/account_service.py`
- `desktop_app/services/task_service.py`
- `desktop_app/services/ai_service.py`
- `desktop_app/services/asset_service.py`
- `desktop_app/services/chat_service.py`
- `desktop_app/services/analytics_service.py`
- `desktop_app/services/report_service.py`
- `desktop_app/services/workflow_service.py`
- `desktop_app/services/activity_service.py`
- `desktop_app/services/dev_seed_service.py`

### 数据层

- 默认数据库位置：`%APPDATA%/TK-OPS-ASSISTANT/tk_ops.db`
- 开发/测试可通过环境变量 `TK_OPS_DATA_DIR` 覆盖数据目录
- 应用启动时会自动执行 Alembic 迁移

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
venv\Scripts\python.exe desktop_app\main.py
```

## 测试

### 运行全量测试

```powershell
venv\Scripts\python.exe -m pytest tests/ -v
```

### 运行重点测试

```powershell
venv\Scripts\python.exe -m pytest tests/test_notification_runtime_truthfulness.py tests/test_analyst_page_backend_driven.py tests/test_dev_seed_service.py -v
```

## 开发测试数据

当前已提供开发 seed，供界面查看和自动化测试使用。

### 方式 1：通过 bridge 调用

- 前端 API：`api.dev.seed()`
- bridge slot：`runDevSeed`

### 方式 2：通过 Python 服务调用

```python
from desktop_app.database.repository import Repository
from desktop_app.services.dev_seed_service import DevSeedService

repo = Repository()
service = DevSeedService(repo)
result = service.seed_development_data()
print(result)
```

seed 特性：

- 幂等
- 写入真实表
- 覆盖 analyst / notification / report / workflow / experiment 页面查看场景

### 仓库内测试数据库样本

仓库现在附带一份可直接用于联调和界面测试的 SQLite 样本库：

- 文件路径：`sample_data/tk_ops_test_seed.db`
- 数据来源：基于本地真实开发库导出的完整一致性快照
- 数据用途：用于页面联调、功能演示、自动化测试前的人工验证
- 数据处理：已清空并重写 `app_settings`，不包含真实 `license_key` 和本机个性化配置

当前样本库包含以下测试数据量：

- `groups=4`
- `devices=4`
- `accounts=9`
- `tasks=14`
- `ai_providers=3`
- `assets=15`
- `analysis_snapshots=6`
- `report_runs=4`
- `workflow_definitions=3`
- `workflow_runs=4`
- `experiment_projects=3`
- `experiment_views=6`
- `activity_logs=12`

### 如何使用仓库样本库

应用默认数据库目录是 `%APPDATA%/TK-OPS-ASSISTANT/`。如果你想在本地直接使用仓库里的样本库进行测试，推荐：

1. 新建一个临时数据目录，例如 `tmp/test-db/`
2. 将 `sample_data/tk_ops_test_seed.db` 复制到该目录，并重命名为 `tk_ops.db`
3. 启动应用前设置环境变量 `TK_OPS_DATA_DIR` 指向这个目录

PowerShell 示例：

```powershell
$env:TK_OPS_DATA_DIR = "$PWD\tmp\test-db"
New-Item -ItemType Directory -Force "$env:TK_OPS_DATA_DIR" | Out-Null
Copy-Item ".\sample_data\tk_ops_test_seed.db" "$env:TK_OPS_DATA_DIR\tk_ops.db" -Force
venv\Scripts\python.exe desktop_app\main.py
```

注意事项：

- `sample_data/tk_ops_test_seed.db` 是仓库测试样本，不是生产数据库
- 如需重新生成最新样本，应从本地开发库重新导出并再次脱敏
- `.gitignore` 已默认忽略其他 `.db` 文件，仅允许提交 `sample_data/*.db`

## 打包

```powershell
.\build_exe.bat --clean
```

输出 EXE：`dist\TK-OPS\TK-OPS.exe`

## 当前边界

以下内容仍不在当前版本真实业务范围内：

1. TikTok Shop 订单、GMV、真实投流消耗、履约流水等未建模业务数据
2. 无法真实支撑的利润/ROI/订单额类指标，不会在当前版本伪造展示
3. 少数系统工具类页面仍有受控降级路径，但不应再保留“能点却无反应”的 silent no-op

## 开发建议

1. 新增功能优先走 TDD
2. 新页面优先补 bridge contract test 与 runtime audit test
3. 页面展示内容优先来自 service / bridge，不要在前端 factory 里硬编码业务主数据
4. 提交前至少运行一次 `venv\Scripts\python.exe -m pytest tests/ -v`

## 许可证

仓库当前未单独附正式 `LICENSE` 文件。如需正式开源或商业分发，请补充明确许可证文本。

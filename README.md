# TK-OPS Desktop

当前发布版本：`1.3.2`

## 项目现状

仓库当前已经切换到新单壳主链路：

- `apps/desktop`：桌面宿主，技术栈为 `Tauri + Vue 3 + TypeScript`
- `apps/py-runtime`：业务 runtime，技术栈为 `Python + FastAPI`
- `desktop_app/`：仅保留为迁移参考和部分运行时复用来源，不再作为默认启动入口

当前主线目标已经从“搭骨架”进入“填业务、补稳定性、收口发布”的阶段。账号管理已完成生产预备版第一阶段。

## 环境准备

推荐 Windows 11 x64，准备以下依赖：

- Python `3.11+`
- Node.js `20+`
- Rust + Cargo
- Visual Studio 2022 Build Tools（含 MSVC C++ 工具链）

首次安装依赖：

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt

cd apps\desktop
npm install
cd ..\..
```

## 如何启动项目

### 默认开发链路

启动新桌面前端和 Python runtime：

```powershell
scripts\dev.ps1
```

常用参数：

```powershell
# 只启动 Python runtime
scripts\dev.ps1 -RuntimeOnly

# 只启动桌面前端（默认连接已有 runtime）
scripts\dev.ps1 -DesktopOnly
```

### 仅检查 runtime

```powershell
scripts\build-runtime.ps1
```

### 构建桌面前端并连跑 runtime 烟测

```powershell
scripts\build-desktop.ps1 -SmokeRuntime
```

### 生成 Alpha 产物

```powershell
scripts\release.ps1
```

### 发布前统一门禁（推荐）

```powershell
# 开发日常快速检查
scripts\preflight-gate.ps1 -Quick

# 发布前完整检查
scripts\preflight-gate.ps1 -Full
```

更多说明见：

- [发布前门禁清单](docs/releases/preflight-checklist.md)
- [发布回滚手册](docs/releases/rollback-playbook.md)
- [v1.3.2 发布记录](docs/releases/2026-04-03-v1.3.2.md)

产物默认输出到：

```text
dist-alpha\TK-OPS-Alpha
```

如需生成 Inno Setup 安装包，先执行 `scripts\release.ps1`，再运行：

```powershell
iscc installer.iss
```

## 验证命令

### Python 测试

```powershell
venv\Scripts\python.exe -m pytest tests -q
```

### Python 编译检查

```powershell
venv\Scripts\python.exe -m compileall apps\py-runtime\src desktop_app
```

### 前端类型检查与构建

```powershell
cd apps\desktop
npm run typecheck
npm run build
```

### Tauri managed runtime 烟测

```powershell
scripts\smoke-tauri-runtime.ps1 -SkipBuild
```

## 当前进度

已完成的主线能力：

- 新单壳桌面链路：`Tauri host + Python sidecar runtime`
- 开发、构建、Alpha 组装和烟测脚本
- `Dashboard / 账号管理 / Provider / 任务队列 / 任务调度 / AI 文案 / Setup Wizard / 设置` 新前端与 runtime 主链路
- 账号管理生产预备版第一阶段：
  - 双状态并排展示
  - 风险状态
  - 批量操作
  - 归档优先
  - 详情摘要与活动摘要

更详细的进度与路线图见：

- [当前进度与路线图](docs/migration/current-status-and-roadmap.md)
- [页面迁移矩阵](docs/migration/page-matrix.md)
- [账号管理设计说明](docs/superpowers/specs/2026-04-02-account-management-production-ready-design.md)

## 目录说明

```text
apps/
├─ desktop/                    # Tauri + Vue 3 + TypeScript 桌面宿主
└─ py-runtime/                 # Python sidecar runtime
desktop_app/                   # reference only，保留迁移参考与部分运行时复用
scripts/
├─ dev.ps1
├─ build-runtime.ps1
├─ build-desktop.ps1
├─ preflight-gate.ps1
├─ smoke-tauri-runtime.ps1
└─ release.ps1
installer.iss                  # 基于 dist-alpha\TK-OPS-Alpha 的安装脚本
```

## 当前约束

- 新需求优先落在 `apps/desktop` 与 `apps/py-runtime`
- `desktop_app/` 不再新增桌面壳功能，只保留迁移参考和运行时复用代码
- 项目文案、交互提示与说明文档优先使用中文

## 许可证

仓库当前未单独附正式 `LICENSE` 文件。如需正式开源或商业分发，请补充明确许可证文本。

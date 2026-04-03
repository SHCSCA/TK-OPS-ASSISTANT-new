# 发布前门禁清单（Preflight Gate）

## 目标

在发版前用统一命令完成关键质量门禁，避免“手工漏跑”。

## 执行命令

### 快速门禁（开发日常）

```powershell
scripts\preflight-gate.ps1 -Quick
```

检查项：
- Runtime + Accounts 关键回归测试
- Python 编译检查
- 前端类型检查

### 完整门禁（发版前）

```powershell
scripts\preflight-gate.ps1 -Full
```

检查项：
- 全量 pytest
- Python 编译检查
- 前端类型检查
- 前端构建
- Tauri managed runtime smoke
- 发布链路脚本契约测试

### 完整门禁 + 产物组装验证

```powershell
scripts\preflight-gate.ps1 -Full -IncludeReleasePack
```

说明：
- 该模式会执行 `scripts\release.ps1 -SkipSmoke`，用于验证组装链路。
- 如果当前机器不具备 Rust/MSVC 环境，请先完成环境准备。

## release 脚本默认行为

- 直接执行 `scripts\release.ps1` 时，会先自动运行 `scripts\preflight-gate.ps1 -Quick`。
- 如需跳过该预检查（仅用于调试），可执行：

```powershell
scripts\release.ps1 -SkipPreflight
```

## 常见参数

- `-SkipSmoke`：在 `-Full` 模式下跳过 smoke（仅用于特定调试）。
- `-IncludeReleasePack`：在 `-Full` 模式下执行 Alpha 产物组装验证。

## 判定标准

- 任一步骤失败，脚本返回非 0 退出码。
- 末尾会输出 Summary 表，包含步骤、状态、耗时和错误信息。

## 发布记录要求

- 每次准备发版时，必须保存一次 `-Full` 执行结果（终端日志或截图）。
- 发版文档中需注明门禁执行时间、分支、提交号和是否包含 `-IncludeReleasePack`。

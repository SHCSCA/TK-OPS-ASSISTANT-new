# 当前进度与路线图

## 一句话判断

新架构的主承重结构已经完成，但页面迁移顺序需要重新收口。当前阶段正式切换为“先全局、再全菜单、后逐页”的稳定迁移模式。

## 当前启动口径

默认开发入口：

```powershell
scripts\dev.ps1
```

常用验证入口：

```powershell
scripts\build-runtime.ps1
scripts\build-desktop.ps1 -SmokeRuntime
scripts\release.ps1
```

说明：

- `apps/desktop` 是唯一继续演进的桌面宿主
- `apps/py-runtime` 是唯一继续演进的业务 runtime
- `desktop_app/` 仅保留迁移参考与运行时复用，不再作为默认入口

## 已完成进度

### 1. 单壳主链路

已完成：

- Tauri 宿主、Python sidecar runtime、前端页面和 runtime API 的主链路打通
- 开发、构建、Alpha 组装、Smoke 验证脚本收口
- 宿主侧基础状态探测、重启入口和受控恢复骨架

### 2. 菜单与页面基线

已进入新链路的页面：

- Dashboard
- 账号管理
- AI Provider
- 任务队列
- 任务调度
- AI 文案生成
- Setup Wizard
- 系统设置

已完成的新基线：

- 新壳左侧菜单与路由骨架已按旧壳补齐到 `44` 个页面
- 已迁移页面仍为 `8` 个，其余页面先进入占位路由，避免再发生漏页
- 迁移矩阵已更新：
  [页面迁移矩阵](c:/Users/wz/Desktop/py/TK-OPS-ASSISTANT-new/docs/migration/page-matrix.md)

### 3. 账号管理生产预备版第一阶段

已落地能力：

- 双状态模型：人工状态 + 系统状态
- 风险状态：`normal / watch / high_risk / frozen`
- 归档优先：默认用归档代替高风险直接删除
- 列表工作台：搜索、筛选、勾选、批量动作
- 详情摘要：最近错误、最近检测、最近活动摘要
- 后端契约：详情、批量操作、归档/取消归档、检测回写
- 审计摘要：基于 `ActivityLog` 记录关键账号动作

对应文档：

- [账号管理设计说明](c:/Users/wz/Desktop/py/TK-OPS-ASSISTANT-new/docs/superpowers/specs/2026-04-02-account-management-production-ready-design.md)
- [账号管理实施计划](c:/Users/wz/Desktop/py/TK-OPS-ASSISTANT-new/docs/superpowers/plans/2026-04-02-account-management-production-ready.md)

## 当前验证状态

最近一轮完成的验证口径：

- `venv\Scripts\python.exe -m pytest tests -q`
- `venv\Scripts\python.exe -m compileall apps\py-runtime\src desktop_app`
- `npm run typecheck`
- `npm run build`
- `scripts\smoke-tauri-runtime.ps1 -SkipBuild`
- `scripts\release.ps1`

这意味着当前仓库已经具备：

- 新架构开发启动能力
- 新架构构建能力
- 受管 runtime 烟测能力
- Alpha 产物组装能力

## 下一阶段规划

### 第一优先：主体框架与全局配置收口

- 统一菜单、路由、标题、详情摘要和占位页口径
- 继续收口全局状态、错误提示、主题变量与宿主信息区
- 让“菜单、路由、迁移矩阵、测试”共用同一套路由真源

### 第二优先：按菜单顺序逐页迁移

- 不再跳着挑页面深挖
- 从 `device-management` 开始，按菜单顺序做整页迁移
- 每页固定顺序：页面结构 -> runtime API -> 交互 -> 样式 -> 测试

### 第三优先：提升宿主与 runtime 稳定性

- 继续增强 sidecar 生命周期与失败恢复
- 让 runtime 故障提示更明确、更面向使用者
- 继续减少 `desktop_app/` 对新链路的隐性依赖

### 第四优先：发布前质量

- 安装后回归
- 升级覆盖验证
- 数据目录兼容验证
- Alpha 到更稳定发布口径的收口

## 当前边界

还需要团队保持一致的约束：

- 新需求优先落在 `apps/desktop` 和 `apps/py-runtime`
- 不再把旧 PySide 壳当默认功能落点
- 不再以“页面能打开”作为完成标准，必须以真实数据链路和异常反馈为准

## 推荐执行顺序

1. 主体框架与全局配置先迁移
2. 建立并冻结完整左侧菜单
3. 按菜单顺序逐页迁移
4. 在逐页迁移过程中同步补稳定性与发布治理

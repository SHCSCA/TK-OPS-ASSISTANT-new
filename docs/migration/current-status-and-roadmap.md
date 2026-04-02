# 当前进度与路线图

## 一句话判断

新架构的主承重结构已经完成，当前阶段已经从“搭骨架”进入“补业务、补稳定性、补发布质量”。

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

### 2. P0 页面迁移

已进入新链路的页面：

- Dashboard
- 账号管理
- AI Provider
- 任务队列
- 任务调度
- AI 文案生成
- Setup Wizard
- 系统设置

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

### 第一优先：继续做深账号管理

下一阶段建议继续补齐这 4 块：

- 导入向导：文件选择、字段映射、预校验、冲突提示、导入结果摘要
- 完整审计页：从“活动摘要”扩到“可查询的账号审计中心”
- 环境绑定深链路：账号与浏览器环境、设备、隔离目录的真实绑定和校验
- 生命周期规则：停用、归档、恢复、删除的边界和权限策略

### 第二优先：提升宿主与 runtime 稳定性

- 继续增强 sidecar 生命周期与失败恢复
- 让 runtime 故障提示更明确、更面向使用者
- 继续减少 `desktop_app/` 对新链路的隐性依赖

### 第三优先：发布前质量

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

1. 账号管理第二阶段：导入向导 + 完整审计页
2. 账号管理第三阶段：环境绑定与生命周期规则
3. sidecar 稳定性补强与发布前验证补齐
4. 继续拆薄旧壳残余依赖

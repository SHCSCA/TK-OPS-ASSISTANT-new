# 设备管理 1:1 全量迁移计划（旧壳基线，含账号联动收口）

## Summary
- 目标：将 `device-management` 从 placeholder 升级为旧壳 `route-device-management-main` 的视觉与交互 1:1 全量迁移（主区 + 右侧详情）。
- 同步目标：迁移完成后执行“账号联动 + 账号右栏样式收口”，不扩展到账号页二次大改。
- 流程：本文件审批后，落 `docs/superpowers/specs/2026-04-06-device-management-1to1-replica-design.md`，再进入实现。

## Key Changes
1. 路由与迁移状态
- `routeManifest` 中 `device-management` 从 `pageKind: placeholder` 切到真实页面类型。
- `migrationStatus` 从 `placeholder` 改为 `implemented`，纳入迁移进度统计。

2. 设备管理页面 1:1 复刻
- 主区结构对齐旧壳：`stat-grid`、`notice-banner`、状态 tabs、`card/list` 视图切换、`device-env-grid`、设备-账号绑定表、覆盖率面板。
- 交互对齐旧壳：默认选中首台、卡片/表格联动详情、筛选与视图同步、批量勾选、批量删除、批量巡检、导出设备报告。
- 动作全量接入：查看详情、编辑设备、删除设备、调整绑定、打开环境、环境日志、巡检/修复。
- 绑定弹层对齐旧壳：同弹层支持“新增绑定账号 + 解除现有绑定”。

3. 右侧详情区设备分支
- `useShellStore` 增加 `deviceDetailState`，固定承载设备基础信息、巡检结论、日志折叠区。
- `DetailPanel` 新增 `device-management` 分支，并把设备动作统一成单一事件分发，主区与右栏共用链路。

4. Runtime 真实接入
- `apps/py-runtime` 新增 `/devices` 路由：
  - `GET /devices`
  - `POST /devices`
  - `PUT /devices/{id}`
  - `DELETE /devices/{id}`
  - `POST /devices/{id}/inspect`
  - `POST /devices/{id}/repair`
  - `POST /devices/{id}/environment/open`
  - `GET /devices/{id}/logs`
- 复用 `AccountService` 设备能力，不引入假动作。
- `apps/desktop` 扩展 `runtimeApi.devices.*` 与对应 `types`。
- 设备绑定关系复用账号更新链路（`updateAccount` 设置 `deviceId`）。

5. 账号联动与右栏收口
- 设备页绑定变更后，触发账号页状态刷新与详情回写。
- 账号右栏样式继续收口：修正字号层级与按钮网格、移除导致溢出的 nowrap、长文本切 stacked 换行，避免顶边框/越界。

## Test Plan
1. 自动化
- 前端契约测试覆盖：
  - `device-management` 不再 placeholder；存在旧壳关键区块与动作入口。
  - `DetailPanel` 存在设备分支与日志折叠渲染。
  - 页面不出现硬编码业务示例数值。
- runtime API 测试覆盖：`/devices` CRUD + inspect/repair/environment/open/logs，及绑定后回写断言。
- 执行：
  - `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
  - `venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "devices or accounts and (proxy_binding or environment or login)" -v`
  - `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
  - `npm run typecheck`
  - `npm run build`

2. 手工验收
- 设备页对照旧壳：布局、信息密度、筛选/切视图、卡片与表格联动、右栏详情与日志展开一致。
- 设备真实动作均可执行并可回写：新增/编辑/删除、巡检/修复、打开环境、绑定/解绑、日志。
- 联动验收：账号页可跳转设备页；设备绑定变更后账号页与右栏状态同步更新。
- 账号右栏验收：文本不越界、长文本可读、按钮布局不挤压边框。

## Assumptions
- 1:1 基线为旧壳 `route-device-management-main` 与 `device-management-main.js / device-environment.js`。
- 不新增设备绑定专用 endpoint，沿用账号更新链路。
- 设备 banner 关闭状态使用现有本地持久化键。
- 本轮账号后续范围固定为“联动 + 右栏样式收口”。

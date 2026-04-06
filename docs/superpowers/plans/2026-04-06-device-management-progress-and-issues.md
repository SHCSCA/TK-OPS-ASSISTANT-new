# 设备管理迁移阶段进度与问题记录（2026-04-06）

## 当前进度
- 已完成并入库文档：
  - `docs/superpowers/plans/2026-04-06-device-management-1to1-replica.md`
  - `docs/superpowers/specs/2026-04-06-device-management-1to1-replica-design.md`
- 后端 Runtime 已完成设备路由接入并在 `app_factory` 注册：
  - `GET /devices`
  - `POST /devices`
  - `PUT /devices/{id}`
  - `DELETE /devices/{id}`
  - `POST /devices/{id}/inspect`
  - `POST /devices/{id}/repair`
  - `POST /devices/{id}/environment/open`
  - `GET /devices/{id}/logs`
- 设备页面迁移已开始：
  - 路由清单 `device-management` 已从 placeholder 切到 implemented
  - 路由组件映射已预留 `DeviceManagementPage`（待页面文件与数据模块落地）

## 当前问题（未收口）
1. `apps/desktop` 前端设备页尚未完整落地：
   - `DeviceManagementPage.vue` / `useDeviceManagementData.ts` 尚未提交
   - `runtimeApi.ts` / `types.ts` 的 `devices.*` 契约尚未补齐
2. 右侧详情区缺设备分支：
   - `useShellStore.ts` 尚未补 `deviceDetailState`
   - `DetailPanel.vue` 尚未新增 `device-management` 渲染分支
3. 账号联动与右栏样式仍有缺口：
   - 设备绑定后触发账号刷新事件链路未收口
   - 账号右栏在部分分辨率下仍有字体层级和长文案换行问题
4. 测试尚未执行完整回归：
   - `pytest` / `npm run typecheck` / `npm run build` 还未跑完本轮变更

## 下一步（已排定）
1. 补齐设备页主区与动作链路（新增/编辑/删除/巡检/修复/打开环境/日志/绑定）。
2. 完成 `deviceDetailState + DetailPanel` 设备分支，统一主区与右栏动作事件源。
3. 处理账号联动与右栏样式溢出，完成账户侧收口。
4. 更新并执行测试，提交验证结果。

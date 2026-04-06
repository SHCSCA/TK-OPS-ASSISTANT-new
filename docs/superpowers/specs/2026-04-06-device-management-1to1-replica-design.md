# 设备管理 1:1 全量迁移设计（旧壳基线）

## Summary
本设计把设备管理页从占位页迁移为真实运行页，完整复刻旧壳核心结构与交互，并接入 py-runtime 设备 API。实现按“前端壳层 / runtime 接口 / 联动回写 / 样式收口”四层推进。

## Architecture & Data Flow
1. 页面入口与路由
- `routeManifest`：`device-management` 改为真实 `pageKind`，`migrationStatus=implemented`。
- `routes.ts`：注册新 `DeviceManagementPage.vue` 组件映射。

2. 数据流
- `DeviceManagementPage` 通过 `useDeviceManagementData` 加载：
  - `runtimeApi.listDevices()`
  - `runtimeApi.listAccounts()`（用于绑定统计与覆盖率）
- 页面计算旧壳视图模型：设备卡片、绑定表、覆盖率、右栏详情。
- 详情更新：页面调用 `shell.setDeviceDetailState(...)`，`DetailPanel` 在 `currentRoute=device-management` 渲染设备详情。

3. 动作流
- 主区与右栏动作统一事件：`tkops:device-detail-action`。
- 动作分发在 `useDeviceManagementData` 内统一处理：
  - `open-environment` -> `runtimeApi.openDeviceEnvironment`
  - `inspect-device` -> `runtimeApi.inspectDevice`
  - `repair-device` -> `runtimeApi.repairDevice`
  - `open-logs` -> `runtimeApi.getDeviceLogs`
  - `edit-device` / `delete-device` -> 对话框 + `update/remove`
  - `adjust-binding` -> 弹层中调用 `runtimeApi.updateAccount(...deviceId...)`

4. 联动回写
- 设备绑定、设备状态动作成功后统一触发：
  - `window.dispatchEvent(new CustomEvent('tkops:accounts-refresh-requested'))`
- 账号模块监听该事件并执行 `refreshAccounts()`，保证账号页与右栏联动一致。

## API / Type Changes
1. py-runtime
- 新增 `apps/py-runtime/src/api/http/devices/routes.py`：
  - `GET /devices`
  - `POST /devices`
  - `PUT /devices/{device_id}`
  - `DELETE /devices/{device_id}`
  - `POST /devices/{device_id}/inspect`
  - `POST /devices/{device_id}/repair`
  - `POST /devices/{device_id}/environment/open`
  - `GET /devices/{device_id}/logs`
- 错误规范：统一 `ok/err` 信封与中文 message；not found 用 404，参数错误用 400。
- `bootstrap/app_factory.py` 注册 `build_devices_router(container)`。

2. desktop runtime contracts
- `types.ts` 新增：
  - `DeviceItem`
  - `DeviceUpsertPayload`
  - `DeviceInspectionResult`
  - `DeviceRepairResult`
  - `DeviceEnvironmentOpenResult`
  - `DeviceLogItem`
- `runtimeApi.ts` 新增 `devices` 分组方法：`list/create/update/remove/inspect/repair/openEnvironment/logs`。

3. shell state
- `useShellStore.ts` 新增 `deviceDetailState`：
  - `kind: 'default' | 'selected'`
  - `deviceId`
  - `title/subtitle/statusLabel/statusTone`
  - `dataPoints[]`
  - `issues[]`
  - `logs[]`
  - `logsCollapsed`
- 增加 `setDeviceDetailState/resetDeviceDetailState`。

## UI & Styling
1. 设备页主区
- 使用旧壳同构块：`device-management-shell`, `device-filter-bar`, `device-env-grid`, `analytics-two-column`, `device-coverage-bar`。
- 视图切换支持 `card/list`，筛选支持 `all/healthy/warning/error/idle`。

2. 右栏设备详情
- `DetailPanel` 新增设备分支模板，按“基础信息 -> 巡检结论 -> 环境日志”渲染。
- 日志默认折叠（超阈值显示“展开全部/收起较早日志”按钮）。

3. 样式迁移与账号右栏收口
- 新增 `apps/desktop/src/styles/device-management.css`（仅设备页作用域）。
- 在 `main.ts` 引入该样式。
- `main.css` 中针对 `detail-panel[data-account-detail-kind]` 修复：
  - strong 文本换行策略
  - stacked 项字体与行高
  - 按钮网格尺寸和间距

## Validation
1. 自动化
- `tests/test_desktop_frontend_routes.py`：设备页组件映射、设备分支存在、关键结构标记存在。
- `tests/test_runtime_api.py`：新增 `/devices` 路由行为断言与异常分支。
- `tests/test_page_runtime_data.py`：校验设备页走 runtime 数据源且无硬编码示例数值。

2. 手工
- 对照旧壳逐块比对视觉与交互。
- 验证设备动作真实生效。
- 验证账号页联动刷新与右栏字体/边界问题消失。

# 账号中心 1:1 迁移计划（旧壳基线，含真实宿主动作接入）

## Summary
- 目标：将 `account` 路由迁移为旧壳 `route-account-main` 的视觉与交互 1:1（主界面严格对齐）。
- 已锁定决策：
1. 主视图采用“严格旧壳主视图”，不保留当前扩展大区块。
2. `进入环境 / Cookie状态 / 重绑并校验` 本轮全部做真实接入，不做假动作。

## Key Changes
1. 账号页结构与交互 1:1
- 重写 `AccountsPage` 为旧壳区块：`notice-banner`、状态 tabs、`card/list` 视图切换、`批量打标签` 入口、`account-grid` 卡片。
- 保留旧壳交互节奏：卡片点击选中、默认选中首项、批量模式显示复选框、状态筛选与视图切换同步。
- 顶部动作对齐旧壳：`导出账号清单`、`批量检测环境`、`新建账号`（以现有真实 API/动作驱动）。

2. 右侧详情区按旧壳承载账号详情
- 在壳层新增 `accountDetailState`（默认态 + 选中账号态 + 建议列表态）。
- `DetailPanel` 在 `currentRoute=account` 时渲染账号详情卡（默认文案、状态、建议项、动作按钮），其他路由保持原逻辑。
- 详情动作与主区动作统一事件源，避免双逻辑漂移。

3. 数据映射与空态（禁止假数据）
- 数据源仅用 runtime/API 与宿主真实返回：
  - 列表：`listAccounts`
  - 详情：`getAccountDetail`
  - 活动摘要：`getAccountActivity`
- 为旧壳字段补齐映射：`tags/notes/cookieContent/cookieUpdatedAt/isolationEnabled/lastLoginAt/lastLoginCheck*` 等。
- 缺字段统一中性空态：`--`、`暂无数据`，不补示例数值。

4. 宿主动作真实接入（本轮新增接口）
- 新增账户运行时接口并接入 `runtimeApi`：
  - `POST /accounts/{id}/environment/open`：启动隔离环境（调用 `AccountService.open_account_environment`）。
  - `POST /accounts/{id}/login/validate`：登录态校验（调用 `AccountService.validate_account_login`）。
  - `GET /accounts/{id}/proxy-binding`：读取当前绑定设备与可选设备快照。
  - `POST /accounts/{id}/proxy-binding`：重绑设备/更新代理并可选 `validateAfterSave`。
- 账号页“重绑并校验”使用同一后端链路：保存绑定后触发登录态校验，结果回写列表与详情。

## Test Plan
1. 自动化
- 前端静态契约测试覆盖：
  - 账号页包含旧壳关键结构标记与交互入口（`js-account-*` 等价行为）。
  - 详情区存在 account 分支与默认详情态。
  - 账号页不出现硬编码业务示例数字。
- 运行时接口测试覆盖：
  - `environment/open`、`login/validate`、`proxy-binding` 读写与失败分支。
- 执行：
  - `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
  - `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
  - `venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "accounts and (environment or login or proxy_binding)" -v`
  - `npm run typecheck`
  - `npm run build`

2. 手工验收
- 主区与旧壳账号页逐块对齐：banner/tabs/视图切换/批量模式/卡片信息密度。
- 选中账号后右侧详情区按旧壳样式与内容更新。
- `进入环境 / Cookie状态 / 重绑并校验` 均可真实执行并回写状态。
- 缺数据场景只出现中性空态，不出现假数据。

## Assumptions
- 本轮 1:1 范围限定在 `account` 路由主区 + 该路由下右侧详情区展示。
- 当前扩展版大区块（导入向导/生命周期大表单等）不在主视图保留；后续如需回补，将走二阶段入口化。
- 不改现有 dashboard/通知中心等已收口页面行为。

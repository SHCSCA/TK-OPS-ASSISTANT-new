# 账号中心 1:1 复刻设计说明（旧壳基线）

## 1. 目标与边界
- 目标：把 Vue `account` 页面落到旧壳 `route-account-main` 的结构、交互节奏和信息密度。
- 边界：仅覆盖 `account` 主区和 `account` 路由下右侧详情区，不扩散到其他路由。
- 本轮不保留扩展区块（导入向导、生命周期大表单等）在主视图展示。

## 2. 结构设计
### 2.1 主区
- 顶部：breadcrumbs + page-header + `导出账号清单 / 批量检测环境`。
- 主体：
  - 隔离提醒 banner（可关闭）。
  - 状态 tabs（all/online/offline/exception）。
  - 视图切换 segmented（card/list）。
  - table-actions（批量打标签、取消多选）。
  - `account-grid` 卡片列表。

### 2.2 右侧详情
- `DetailPanel` 增加 account 分支。
- `accountDetailState` 三态：
  - `default`：未选中账号。
  - `selected`：账号基础详情（环境、Cookie、连接、标签等）。
  - `advice`：风险与处置建议条目。

## 3. 数据与映射
- 输入：`listAccounts`、`getAccountDetail`、`getAccountActivity`。
- 映射字段：
  - 卡片：账号 ID、地区/平台摘要、代理、最近登录、Cookie 状态、登录校验状态、标签。
  - 详情：隔离启用、Cookie 更新时间、连接检测结果、登录校验消息、活动摘要。
- 缺字段：统一 `--` / `暂无数据`。

## 4. 宿主动作接入
### 4.1 py-runtime 路由新增
- `POST /accounts/{id}/environment/open`
- `POST /accounts/{id}/login/validate`
- `GET /accounts/{id}/proxy-binding`
- `POST /accounts/{id}/proxy-binding`

### 4.2 行为约束
- 所有接口返回统一 `ok/err` 信封。
- 错误文案中文化，不暴露 traceback。
- `proxy-binding` 支持：
  - 可选更换设备。
  - 可选更新设备代理/地区。
  - `validateAfterSave=true` 时串联登录态校验。

## 5. 验证
- 静态契约：账号页面关键结构、account 详情分支、无示例假数字。
- 运行时接口：新增 4 个 endpoint 的成功与失败分支。
- 构建与类型：`typecheck` + `build` 必过。

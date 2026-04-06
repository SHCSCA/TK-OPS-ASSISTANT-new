# 概览看板 1:1 复刻设计（旧壳基线）

## 背景

当前 Vue 版 dashboard 已有真实数据链路，但与旧壳 `route-dashboard-main` 在结构与交互上仍有偏差，尤其是快捷入口和右侧详情联动。

## 设计目标

1. dashboard 主区结构与旧壳模板一致。
2. 交互路径一致：活动/系统/快捷入口都能驱动右侧详情。
3. 数据真实性不回退：全部使用 runtime 数据或中性空态。

## 设计方案

### 1. 主区 1:1 结构

- 保持旧壳区块：页头、统计卡、趋势区、活动流、系统状态、快捷入口。
- 关键类语义与旧壳一致，保证样式复用稳定。

### 2. 详情联动模型

- shell store 新增 `dashboardDetailState`：
  - `kind`: `default | activity | system | quick-action`
  - `title`、`subtitle`、`items[]`、`statusLabel/statusTone`
- `DashboardPage` 负责写入该状态。
- `DetailPanel` 在当前路由为 `dashboard` 时优先渲染该状态，否则保持通用详情。

### 3. 快捷入口数据映射

- `处理账号异常`：系统状态异常/关注项 + 最近异常活动。
- `启动内容批量生成`：active provider + 任务状态聚合。
- `网络诊断`：runtime health + host reachability。
- `审核定时发布`：scheduler overview 摘要。

### 4. 空态与容错

- 任一字段缺失：`--` 或 `暂无数据`。
- 不写死演示数字，不写死业务结论。

## 完成标准

- dashboard 页面对齐旧壳模板视觉和交互语义。
- 快捷入口点击仅更新右侧详情卡，不立即跳路由。
- 详情区支持 default/activity/system/quick-action 四种态。
- 自动化检查通过（pytest + typecheck + build）。

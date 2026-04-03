# 页面迁移矩阵

## 当前口径

- 旧壳顶层页面：`44`
- 新壳左侧菜单：`44`
- 已接入真实新链路页面：`8`
- 当前执行顺序：
  1. 主体框架与全局配置先迁移
  2. 左侧菜单与路由骨架一次补齐
  3. 按菜单顺序逐页迁移页面、数据、交互、样式与测试

## 迁移矩阵

| 旧路由键 | 页面名称 | 菜单分区 | 新路径 | 优先级 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| dashboard | 概览看板 | 总览工作台 | `/` | P0 | 已迁移 |
| operations-center | 运营中心 | 运营管理 | `/operations-center` | P1 | 已注册菜单与占位路由 |
| account | 账号管理 | 运营管理 | `/accounts` | P0 | 已迁移 |
| device-management | 设备管理 | 运营管理 | `/device-management` | P0 | 已注册菜单与占位路由 |
| asset-center | 素材中心 | 运营管理 | `/asset-center` | P1 | 已注册菜单与占位路由 |
| order-management | 订单管理 | 运营管理 | `/order-management` | P2 | 已注册菜单与占位路由 |
| service-center | 客服中心 | 运营管理 | `/service-center` | P2 | 已注册菜单与占位路由 |
| refund-processing | 退款处理 | 运营管理 | `/refund-processing` | P2 | 已注册菜单与占位路由 |
| task-queue | 任务队列 | 自动化任务 | `/tasks` | P0 | 已迁移 |
| task-hall | 任务大厅 | 自动化任务 | `/task-hall` | P1 | 已注册菜单与占位路由 |
| task-scheduler | 任务调度 | 自动化任务 | `/task-scheduler` | P0 | 已迁移 |
| scheduled-publish | 定时发布 | 自动化任务 | `/scheduled-publish` | P1 | 已注册菜单与占位路由 |
| data-collector | 数据采集助手 | 自动化任务 | `/data-collector` | P1 | 已注册菜单与占位路由 |
| auto-like | 自动点赞 | 自动化任务 | `/auto-like` | P1 | 已注册菜单与占位路由 |
| auto-comment | 自动评论 | 自动化任务 | `/auto-comment` | P1 | 已注册菜单与占位路由 |
| auto-message | 自动私信 | 自动化任务 | `/auto-message` | P1 | 已注册菜单与占位路由 |
| auto-reply | 自动回复 | 自动化任务 | `/auto-reply` | P1 | 已注册菜单与占位路由 |
| creative-workshop | 创意工坊 | 内容与 AI | `/creative-workshop` | P1 | 已注册菜单与占位路由 |
| visual-lab | 可视化实验室 | 内容与 AI | `/visual-lab` | P2 | 已注册菜单与占位路由 |
| ai-content-factory | AI 内容工厂 | 内容与 AI | `/ai-content-factory` | P1 | 已注册菜单与占位路由 |
| ai-copywriter | AI 文案生成 | 内容与 AI | `/ai-copywriter` | P0 | 已迁移 |
| viral-title | 爆款标题 | 内容与 AI | `/viral-title` | P1 | 已注册菜单与占位路由 |
| script-extractor | 脚本提取 | 内容与 AI | `/script-extractor` | P1 | 已注册菜单与占位路由 |
| product-title | 商品标题 | 内容与 AI | `/product-title` | P1 | 已注册菜单与占位路由 |
| video-editor | 视频编辑 | 内容与 AI | `/video-editor` | P0 | 已注册菜单与占位路由 |
| visual-editor | 可视化编辑 | 内容与 AI | `/visual-editor` | P2 | 已注册菜单与占位路由 |
| ai-provider | AI 提供商 | 内容与 AI | `/providers` | P0 | 已迁移 |
| traffic-board | 流量看板 | 数据分析 | `/traffic-board` | P1 | 已注册菜单与占位路由 |
| profit-analysis | 利润分析 | 数据分析 | `/profit-analysis` | P1 | 已注册菜单与占位路由 |
| competitor-monitor | 竞品监控 | 数据分析 | `/competitor-monitor` | P1 | 已注册菜单与占位路由 |
| blue-ocean | 蓝海机会 | 数据分析 | `/blue-ocean` | P1 | 已注册菜单与占位路由 |
| report-center | 报表中心 | 数据分析 | `/report-center` | P1 | 已注册菜单与占位路由 |
| interaction-analysis | 互动分析 | 数据分析 | `/interaction-analysis` | P2 | 已注册菜单与占位路由 |
| ecommerce-conversion | 电商转化 | 数据分析 | `/ecommerce-conversion` | P2 | 已注册菜单与占位路由 |
| fan-profile | 粉丝画像 | 数据分析 | `/fan-profile` | P2 | 已注册菜单与占位路由 |
| setup-wizard | 初始化向导 | 系统与工具 | `/setup-wizard` | P0 | 已迁移 |
| system-settings | 系统设置 | 系统与工具 | `/settings` | P0 | 已迁移 |
| downloader | 下载器 | 系统与工具 | `/downloader` | P2 | 已注册菜单与占位路由 |
| lan-transfer | 局域网传输 | 系统与工具 | `/lan-transfer` | P2 | 已注册菜单与占位路由 |
| network-diagnostics | 网络诊断 | 系统与工具 | `/network-diagnostics` | P1 | 已注册菜单与占位路由 |
| log-center | 日志中心 | 系统与工具 | `/log-center` | P1 | 已注册菜单与占位路由 |
| version-upgrade | 版本升级 | 系统与工具 | `/version-upgrade` | P1 | 已注册菜单与占位路由 |
| license-issuer | 授权签发 | 系统与工具 | `/license-issuer` | P2 | 已注册菜单与占位路由 |
| permission-management | 权限管理 | 系统与工具 | `/permission-management` | P2 | 已注册菜单与占位路由 |

## 当前结论

- “菜单不全、页面不全”的问题，本轮已先从结构层解决：新壳菜单和路由骨架已对齐旧壳 `44` 个页面。
- “功能不全”的问题还没有结束，下一步不再跳着做，而是严格按上表顺序逐页迁移。
- 下一批优先页：`device-management`、`video-editor`、`traffic-board`、`report-center`。

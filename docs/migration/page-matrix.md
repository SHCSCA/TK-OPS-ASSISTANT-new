# Page Matrix

| Route Key | 页面名称 | 当前数据来源 | 主操作 | 详情面板 | 批量操作 | 迁移优先级 | 当前状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dashboard | Dashboard | Python runtime `/health` + `/dashboard/overview` | 概览刷新 | 是 | 否 | P0 | 已迁移到新链路 |
| account-management | 账号管理 | Python runtime `/accounts` | 列表查询、批量操作、归档、检测 | 是 | 是 | P0 | 已完成生产预备版第一阶段 |
| ai-provider | AI Provider | Python runtime `/providers` | Provider 列表与配置刷新 | 是 | 是 | P0 | 已迁移到新链路 |
| task-queue | 任务队列 | Python runtime `/tasks` | 任务查询与状态操作 | 是 | 是 | P0 | 已迁移到新链路 |
| scheduler | 任务调度 | Python runtime `/scheduler` | 调度总览、新建、启停、删除 | 是 | 否 | P0 | 已迁移到新链路 |
| ai-copywriter | AI 文案生成 | Python runtime `/copywriter/bootstrap` + `/ws/copywriter-stream` | 流式生成文案 | 是 | 否 | P0 | 已迁移到新链路 |
| setup-wizard | Setup Wizard | Python runtime `/license/status` + `/providers` + `/settings` | 初始化检查与配置引导 | 是 | 否 | P0 | 已迁移到新链路 |
| settings | 系统设置 | Python runtime `/settings` | 设置读取与保存 | 是 | 否 | P0 | 已迁移到新链路 |

> 当前 P0 主页面已全部进入新链路。后续重点不再是“有没有页面”，而是“把页面做成可长期迭代的业务工作台”。

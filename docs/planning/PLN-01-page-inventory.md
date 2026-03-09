# PLN-01 · Page Inventory

## Scope Notes

- Source of truth: `stitch_text_document/`
- Counted pages: **26** (`25` HTML-backed/mockup-backed pages + `_6` screenshot recovery page)
- Wave assignments are mapped from the approved 67-task execution plan.
- Sidebar gap analysis treats **exact label match** as the threshold for “has matching mockup”.

## 1) Page Inventory Table

| route_id | display_name_zh | mockup_source | domain_group | sidebar_section | sidebar_icon | has_sub_tabs | ai_features | risk_level | wave_assignment |
|---|---|---|---|---|---|---:|---|---|---|
| `dashboard_home` | TK-OPS Dashboard | `tk_ops/` | dashboard | Main | `dashboard` | false | `AI任务总览`、`AI引擎状态卡` | medium | `Wave 4 · PG-01` |
| `account_management` | 账号管理 | `_1/` | account | Main | `manage_accounts` | true | `—` | medium | `Wave 4 · PG-02` |
| `visual_editor` | 视觉编辑器 | `_2/` | content | 内容创作者专区 | `movie_edit` | true | `智能增强` | high | `Wave 5 · PG-03` |
| `visual_lab` | 可视化实验室 | `_3/` | analytics | 数据分析师专区 | `query_stats` | false | `—` | high | `Wave 4 · PG-04` |
| `competitor_monitoring` | 竞争对手监控 | `_4/` | analytics | 数据分析师专区 | `monitoring` | true | `—` | medium | `Wave 4 · PG-05` |
| `profit_analysis` | 利润分析系统 | `_5/` | analytics | 数据分析师专区 | `analytics` | true | `—` | medium | `Wave 4 · PG-06` |
| `ai_provider_settings` | AI供应商配置 | `_6/` | system | System | `settings` | true | `供应商启停`、`API Key/Base URL/模型配置`、`连接测试`、`自定义Provider` | high | `Wave 5 · PG-07 (recovery)` |
| `blue_ocean_analysis` | 蓝海分析 | `_7/` | analytics | 数据分析师专区 | `explore` | true | `AI策略建议`、`调研报告生成` | high | `Wave 5 · PG-08` |
| `lan_transfer` | 局域网传输 | `_8/` | system | System | `leak_add` | false | `—` | medium | `Wave 4 · PG-09` |
| `task_queue` | 任务队列 | `_9/` | system | System | `account_tree` | true | `—` | medium | `Wave 4 · PG-10` |
| `auto_reply_console` | 自动回复控制台 | `_10/` | automation | 自动化运营专区 | `robot_2` | false | `智能自动回复开关` | high | `Wave 5 · PG-11` |
| `viral_title_studio` | 爆款标题 | `_11/` | ai | 内容创作者专区 | `auto_awesome` | false | `AI智能优化`、`互动率预测`、`A/B方案预估` | medium | `Wave 5 · PG-12` |
| `report_generator` | 数据报告生成器 | `_12/` | analytics | 数据分析师专区 | `description` | false | `—` | high | `Wave 4 · PG-13` |
| `setup_wizard` | Setup Wizard | `_13/` | system | System | `bolt` | true | `AI Provider配置`、`高级推理开关` | medium | `Wave 4 · PG-14` |
| `material_factory` | 素材工厂 | `_14/` | content | 内容创作者专区 | `factory` | true | `—` | high | `Wave 4 · PG-15` |
| `script_extractor` | 脚本提取工具 | `_15/` | ai | 内容创作者专区 | `movie_edit` | true | `ASR转写`、`OCR识别`、`混合分析`、`AI实时摘要`、`AI智能改写` | high | `Wave 5 · PG-16` |
| `data_collection_assistant` | 数据采集助手 | `_16/` | automation | 自动化运营专区 | `analytics` | false | `—` | medium | `Wave 4 · PG-17` |
| `download_manager` | 下载器 | `_17/` | system | System | `download` | false | `—` | medium | `Wave 4 · PG-18` |
| `scheduled_publishing` | 定时发布 | `_18/` | automation | 自动化运营专区 | `schedule` | true | `—` | medium | `Wave 4 · PG-19` |
| `network_diagnostics` | 网络诊断 | `_19/` | system | System | `terminal` | false | `—` | medium | `Wave 4 · PG-20` |
| `task_scheduler` | 任务调度 | `_21/` | system | System | `schedule` | true | `—` | high | `Wave 4 · PG-22` |
| `engagement_analysis` | 互动分析 | `_22/` | analytics | 数据分析师专区 | `bar_chart` | true | `情感分析` | high | `Wave 4 · PG-23` |
| `product_title_master` | 商品标题大师 | `_23/` | ai | 内容创作者专区 | `auto_fix_high` | true | `AI标题优化`、`SEO关键词建议` | medium | `Wave 5 · PG-24` |
| `creative_workshop` | 创意工坊 | `_24/` | ai | 内容创作者专区 | `rocket_launch` | false | `批量AI生成`、`模型选择`、`结果批处理` | high | `Wave 5 · PG-25` |
| `ai_content_factory` | AI内容工厂 | `ai_1/` | ai | 内容创作者专区 | `factory` | false | `AI脚本生成`、`语音合成`、`工作流编排` | high | `Wave 5 · PG-26` |
| `ai_copy_generation` | AI文案生成 | `ai_2/` | ai | 内容创作者专区 | `edit_note` | true | `文案变体生成`、`合规自检`、`风险词替换建议` | high | `Wave 5 · PG-27` |
| `crm_customer_management` | CRM客户关系管理 | `crm/` | crm | 运营经理专区 | `hub` | false | `—` | medium | `Wave 4 · PG-28` |

## 2) Domain Grouping Matrix

| domain_group | Pages | Primary service dependencies |
|---|---|---|
| `dashboard` | `dashboard_home` | `navigation_registry`、`shell_state_service`、`kpi_service`、`alert_service`、`ai_runtime_summary_service` |
| `account` | `account_management` | `account_service`、`group_service`、`device_service`、`cookie_service`、`fingerprint_service` |
| `operations` | `— (sidebar stub domain only in PLN-01)` | `operations_hub_service`、`order_service`、`refund_service`、`customer_service` |
| `content` | `visual_editor`、`material_factory` | `asset_service`、`media_library_service`、`video_project_service`、`editor_state_service`、`batch_media_ops_service` |
| `analytics` | `visual_lab`、`competitor_monitoring`、`profit_analysis`、`blue_ocean_analysis`、`report_generator`、`engagement_analysis` | `analytics_query_service`、`competitor_service`、`profit_service`、`opportunity_scoring_service`、`report_service`、`engagement_service` |
| `automation` | `auto_reply_console`、`data_collection_assistant`、`scheduled_publishing` | `automation_rule_service`、`job_queue_service`、`scheduler_service`、`data_collection_service`、`publish_service` |
| `ai` | `viral_title_studio`、`script_extractor`、`product_title_master`、`creative_workshop`、`ai_content_factory`、`ai_copy_generation` | `provider_registry_service`、`model_catalog_service`、`agent_role_service`、`llm_gateway_service`、`streaming_ai_service`、`compliance_service`、`workflow_service` |
| `system` | `ai_provider_settings`、`lan_transfer`、`task_queue`、`setup_wizard`、`download_manager`、`network_diagnostics`、`task_scheduler` | `settings_service`、`secret_store_service`、`permission_service`、`diagnostics_service`、`transfer_service`、`log_service`、`task_runtime_service` |
| `crm` | `crm_customer_management` | `crm_service`、`customer_timeline_service`、`tagging_service`、`follow_up_service` |

## 3) Route Map

```text
/
├─ Main
│  ├─ /dashboard_home                         (implemented · tk_ops)
│  ├─ /account_management                     (implemented · _1)
│  ├─ /group_management                       (stub page required)
│  └─ /device_management                      (stub page required)
│
├─ 运营经理专区
│  ├─ /operations_center                      (stub hub required)
│  │  └─ /crm_customer_management             (implemented child utility · crm)
│  ├─ /order_management                       (stub page required)
│  ├─ /refund_processing                      (stub page required)
│  └─ /customer_service_center                (stub page required)
│
├─ 内容创作者专区
│  ├─ /material_center                        (stub hub required)
│  │  └─ /material_factory                    (implemented child · _14)
│  ├─ /video_editing                          (stub hub required)
│  │  └─ /visual_editor                       (implemented child · _2)
│  ├─ /script_generation                      (stub hub required)
│  │  ├─ /viral_title_studio                  (implemented child · _11)
│  │  ├─ /script_extractor                    (implemented child · _15)
│  │  ├─ /product_title_master                (implemented child · _23)
│  │  ├─ /creative_workshop                   (implemented child · _24)
│  │  ├─ /ai_content_factory                  (implemented child · ai_1)
│  │  └─ /ai_copy_generation                  (implemented child · ai_2)
│  └─ /task_hall                              (stub page required)
│
├─ 数据分析师专区
│  ├─ /traffic_dashboard                      (stub hub required)
│  │  ├─ /visual_lab                          (implemented child · _3)
│  │  ├─ /competitor_monitoring               (implemented child · _4)
│  │  ├─ /blue_ocean_analysis                 (implemented child · _7)
│  │  └─ /engagement_analysis                 (implemented child · _22)
│  ├─ /ecommerce_conversion                   (stub hub required)
│  │  └─ /profit_analysis                     (implemented child · _5)
│  ├─ /audience_personas                      (stub page required)
│  └─ /report_center                          (stub hub required)
│     └─ /report_generator                    (implemented child · _12)
│
├─ 自动化运营专区
│  ├─ /auto_like                              (stub page required)
│  ├─ /auto_comment                           (stub page required)
│  ├─ /auto_direct_message                    (stub page required)
│  └─ /scheduled_publishing                   (implemented · _18)
│     ├─ /auto_reply_console                  (implemented adjacent tool · _10)
│     └─ /data_collection_assistant           (implemented adjacent tool · _16)
│
└─ System
   ├─ /system_settings                        (stub hub required)
   │  ├─ /setup_wizard                        (implemented child · _13)
   │  └─ /ai_provider_settings                (implemented child · _6 recovery)
   ├─ /permission_management                  (stub page required)
   ├─ /log_center                             (stub hub required)
   │  ├─ /task_queue                          (implemented child · _9)
   │  ├─ /network_diagnostics                 (implemented child · _19)
   │  └─ /task_scheduler                      (implemented child · _21)
   └─ /version_upgrade                        (stub hub required)
      ├─ /lan_transfer                        (implemented child · _8)
      └─ /download_manager                    (implemented child · _17)
```

## 4) Sidebar Navigation Items

| route_id | icon | label_zh | group | group_color | badge_type |
|---|---|---|---|---|---|
| `dashboard_home` | `dashboard` | 概览数据看板 | Main | `default` | `implemented` |
| `account_management` | `manage_accounts` | 账号管理 | Main | `default` | `implemented` |
| `group_management` | `group_work` | 分组管理 | Main | `default` | `stub_required` |
| `device_management` | `devices` | 设备管理 | Main | `default` | `stub_required` |
| `operations_center` | `admin_panel_settings` | 运营中心 | 运营经理专区 | `#FF6B6B` | `stub_hub` |
| `order_management` | `receipt_long` | 订单管理 | 运营经理专区 | `#FF6B6B` | `stub_required` |
| `refund_processing` | `undo` | 退款处理 | 运营经理专区 | `#FF6B6B` | `stub_required` |
| `customer_service_center` | `support_agent` | 客服中心 | 运营经理专区 | `#FF6B6B` | `stub_required` |
| `material_center` | `movie_edit` | 素材中心 | 内容创作者专区 | `#4ECDC4` | `stub_hub` |
| `video_editing` | `content_cut` | 视频剪辑 | 内容创作者专区 | `#4ECDC4` | `stub_hub` |
| `script_generation` | `description` | 脚本生成 | 内容创作者专区 | `#4ECDC4` | `stub_hub` |
| `task_hall` | `assignment` | 任务大厅 | 内容创作者专区 | `#4ECDC4` | `stub_required` |
| `traffic_dashboard` | `bar_chart` | 流量看板 | 数据分析师专区 | `#95E1D3` | `stub_hub` |
| `ecommerce_conversion` | `shopping_bag` | 电商转化 | 数据分析师专区 | `#95E1D3` | `stub_hub` |
| `audience_personas` | `face` | 粉丝画像 | 数据分析师专区 | `#95E1D3` | `stub_required` |
| `report_center` | `pie_chart` | 报表中心 | 数据分析师专区 | `#95E1D3` | `stub_hub` |
| `auto_like` | `thumb_up` | 自动点赞 | 自动化运营专区 | `#F38181` | `stub_required` |
| `auto_comment` | `comment` | 自动评论 | 自动化运营专区 | `#F38181` | `stub_required` |
| `auto_direct_message` | `mail` | 自动私信 | 自动化运营专区 | `#F38181` | `stub_required` |
| `scheduled_publishing` | `schedule` | 定时发布 | 自动化运营专区 | `#F38181` | `implemented` |
| `system_settings` | `settings` | 系统设置 | System | `default` | `stub_hub` |
| `permission_management` | `lock_person` | 权限管理 | System | `default` | `stub_required` |
| `log_center` | `history` | 日志中心 | System | `default` | `stub_hub` |
| `version_upgrade` | `upgrade` | 版本升级 | System | `default` | `stub_hub` |

## 5) Sidebar Items Without Exact Mockup Matches (Stub Pages Required)

Exact-match mockup coverage exists for only **3** master-sidebar items:

- `概览数据看板` → `dashboard_home`
- `账号管理` → `account_management`
- `定时发布` → `scheduled_publishing`

The following **21** sidebar items do **not** have an exact one-to-one mockup page and therefore need stub or hub routes in the shell IA:

| Sidebar item | Recommended route_id | Handling |
|---|---|---|
| 分组管理 | `group_management` | Stub page |
| 设备管理 | `device_management` | Stub page |
| 运营中心 | `operations_center` | Stub hub |
| 订单管理 | `order_management` | Stub page |
| 退款处理 | `refund_processing` | Stub page |
| 客服中心 | `customer_service_center` | Stub page |
| 素材中心 | `material_center` | Stub hub → child `material_factory` |
| 视频剪辑 | `video_editing` | Stub hub → child `visual_editor` |
| 脚本生成 | `script_generation` | Stub hub → multiple AI/script pages |
| 任务大厅 | `task_hall` | Stub page |
| 流量看板 | `traffic_dashboard` | Stub hub |
| 电商转化 | `ecommerce_conversion` | Stub hub |
| 粉丝画像 | `audience_personas` | Stub page |
| 报表中心 | `report_center` | Stub hub |
| 自动点赞 | `auto_like` | Stub page |
| 自动评论 | `auto_comment` | Stub page |
| 自动私信 | `auto_direct_message` | Stub page |
| 系统设置 | `system_settings` | Stub hub |
| 权限管理 | `permission_management` | Stub page |
| 日志中心 | `log_center` | Stub hub |
| 版本升级 | `version_upgrade` | Stub hub |

## 6) Implementation Mapping Notes

- `_6` should be implemented as a **System → AI Provider Settings** recovery page and grouped under `system_settings`.
- `crm/` is best exposed as an **operations child route** under `operations_center`, not as a direct sidebar item.
- The content/AI cluster is intentionally broader than the master sidebar; use `script_generation` as the hub route for `_11`, `_15`, `_23`, `_24`, `ai_1`, and `ai_2`.
- The analytics cluster should use hub routes (`traffic_dashboard`, `ecommerce_conversion`, `report_center`) so every master-sidebar item remains routable even where the mockups are specialized tools rather than exact top-level pages.

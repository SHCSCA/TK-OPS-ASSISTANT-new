# PLN-02 Global Information Architecture

## 0. Source Coverage

Sources reviewed: `tk_ops`, `_1`-`_24` (except `_6` via `screen.png` only), `ai_1`, `ai_2`, `crm`.

26 mockups covered:

| Mockup | Screen | Primary subject | Proposed shell placement |
|---|---|---|---|
| `tk_ops` | 概览数据看板 | Global dashboard shell | `dashboard` |
| `_1` | 账号管理 | Accounts + environment details | `account_management` |
| `_2` | 视觉编辑器 | Timeline/video editing workspace | `video_editor` |
| `_3` | 可视化实验室 | Analyst chart builder | `report_center` |
| `_4` | 竞争对手监控 | Competitive traffic/content analysis | `traffic_dashboard` |
| `_5` | 利润分析系统 | Conversion/profit analytics | `ecommerce_conversion` |
| `_6` | AI供应商配置详细版 | System AI provider settings | `system_settings` |
| `_7` | 蓝海分析 | Market opportunity discovery | `traffic_dashboard` |
| `_8` | 局域网传输 | Asset transfer utility | `asset_center` |
| `_9` | 任务队列 | Queue/task execution | `task_hall` |
| `_10` | 自动回复控制台 | Automation rules console | `customer_service` / `auto_comment` support tool |
| `_11` | 爆款标题 | Title ideation | `script_generation` |
| `_12` | 数据报告生成器 | Report builder | `report_center` |
| `_13` | Setup Wizard | First-run onboarding | Launch flow before shell |
| `_14` | 素材工厂 | Asset library | `asset_center` |
| `_15` | 脚本提取工具 | Script extraction from video | `script_generation` |
| `_16` | 数据采集助手 | Data collection | `traffic_dashboard` / ops tool |
| `_17` | 下载器 | Media download utility | `asset_center` |
| `_18` | 定时发布 | Publishing calendar | `scheduled_publishing` |
| `_19` | Network Diagnostics | Environment/network diagnostics | `system_settings` |
| `_21` | 任务调度 | Scheduler calendar | `task_hall` |
| `_22` | 互动分析 | Engagement analytics | `traffic_dashboard` |
| `_23` | 商品标题大师 | Product title optimizer | `script_generation` |
| `_24` | 批量创作配置/结果 | Batch creative generation | `task_hall` / `script_generation` |
| `ai_1` | AI内容工厂 | Workflow designer | `task_hall` |
| `ai_2` | AI文案生成 | Copy generation + compliance | `script_generation` |
| `crm` | TK-OPS CRM | Customer relationship workspace | `customer_service` |

---

## 1. Shell Zone Layout

### 1.1 Canonical shell

```text
+--------------------------------------------------------------------------------------+
| TITLE BAR                                                                            |
| [Logo] [App/Current Module]   [Global Search................] [Bell] [User Avatar]  |
+--------------------------+------------------------------------------------+----------+
| SIDEBAR                  | CONTENT HOST                                   | DETAIL   |
|                          |                                                | PANEL    |
| Main                     | +--------------------------------------------+ |          |
| - 概览数据看板           | | Breadcrumb / Page title / local toolbar    | | Optional |
| - 账号管理               | +--------------------------------------------+ | right    |
| - 分组管理               | |                                            | | dock /   |
| - 设备管理               | |   QStackedWidget Page Host                 | | drawer   |
|                          | |   - dashboard                              | |          |
| 运营经理专区             | |   - account_management                     | | e.g.     |
| 内容创作者专区           | |   - asset_center                           | | details, |
| 数据分析师专区           | |   - report_center                          | | preview, |
| 自动化运营专区           | |   - ...                                    | | config   |
|                          | |                                            | |          |
| System                   | +--------------------------------------------+ |          |
|                          |                                                |          |
| [Collapse Sidebar]       |                                                |          |
+--------------------------+------------------------------------------------+----------+
| STATUS BAR / JOB STATUS / CONNECTIVITY / LAST SYNC / BUILD / VALIDATION (optional)  |
+--------------------------------------------------------------------------------------+
```

### 1.2 Zone behaviors

- **Title bar**: global search, notifications, user/profile, module title/logo.
- **Sidebar**: collapsible; expanded = group labels + item text, collapsed = icon rail + tooltips.
- **Content host**: central `QStackedWidget` page container; every primary route swaps here.
- **Detail panel**: optional right-side dock/drawer for context-specific properties, previews, logs, or quick actions.
- **Status bar**: optional persistent footer for connectivity, queue state, validation, progress, or environment state.

### 1.3 Detail-panel pages observed

- `_1` 账号管理 — account details
- `_6` AI供应商配置 — provider config
- `_12` 数据报告生成器 — live preview
- `_14` 素材工厂 — asset details
- `_21` 任务调度 — task detail
- `ai_1` AI内容工厂 — node configuration
- `ai_2` AI文案生成 — compliance report
- `crm` — quick customer actions

---

## 2. Complete Sidebar Navigation Tree

```text
Sidebar
├── [Main]
│   ├── 概览数据看板 (dashboard)
│   ├── 账号管理 (account_management)
│   ├── 分组管理 (group_management)
│   └── 设备管理 (device_management)
├── 运营经理专区 (#FF6B6B)
│   ├── 运营中心 (operations_center)
│   ├── 订单管理 (order_management)
│   ├── 退款处理 (refund_processing)
│   └── 客服中心 (customer_service)
├── 内容创作者专区 (#4ECDC4)
│   ├── 素材中心 (asset_center)
│   ├── 视频剪辑 (video_editor)
│   ├── 脚本生成 (script_generation)
│   └── 任务大厅 (task_hall)
├── 数据分析师专区 (#95E1D3)
│   ├── 流量看板 (traffic_dashboard)
│   ├── 电商转化 (ecommerce_conversion)
│   ├── 粉丝画像 (fan_persona)
│   └── 报表中心 (report_center)
├── 自动化运营专区 (#F38181)
│   ├── 自动点赞 (auto_like)
│   ├── 自动评论 (auto_comment)
│   ├── 自动私信 (auto_direct_message)
│   └── 定时发布 (scheduled_publishing)
└── [System]
    ├── 系统设置 (system_settings)
    ├── 权限管理 (permission_management)
    ├── 日志中心 (log_center)
    └── 版本升级 (version_upgrade)
```

### 2.1 Item metadata

| Label | route_id | icon | badge_type | click_action |
|---|---|---|---|---|
| 概览数据看板 | `dashboard` | `dashboard` | none | Open page in content `QStackedWidget` |
| 账号管理 | `account_management` | `manage_accounts` | none | Open page in content `QStackedWidget` |
| 分组管理 | `group_management` | `group_work` | none | Open page in content `QStackedWidget` |
| 设备管理 | `device_management` | `devices` | none | Open page in content `QStackedWidget` |
| 运营中心 | `operations_center` | `admin_panel_settings` | none | Open page in content `QStackedWidget` |
| 订单管理 | `order_management` | `receipt_long` | none | Open page in content `QStackedWidget` |
| 退款处理 | `refund_processing` | `undo` | none | Open page in content `QStackedWidget` |
| 客服中心 | `customer_service` | `support_agent` | none | Open page in content `QStackedWidget` |
| 素材中心 | `asset_center` | `movie_edit` | none | Open page in content `QStackedWidget` |
| 视频剪辑 | `video_editor` | `content_cut` | none | Open page in content `QStackedWidget` |
| 脚本生成 | `script_generation` | `description` | none | Open page in content `QStackedWidget` |
| 任务大厅 | `task_hall` | `assignment` | none | Open page in content `QStackedWidget` |
| 流量看板 | `traffic_dashboard` | `bar_chart` | none | Open page in content `QStackedWidget` |
| 电商转化 | `ecommerce_conversion` | `shopping_bag` | none | Open page in content `QStackedWidget` |
| 粉丝画像 | `fan_persona` | `face` | none | Open page in content `QStackedWidget` |
| 报表中心 | `report_center` | `pie_chart` | none | Open page in content `QStackedWidget` |
| 自动点赞 | `auto_like` | `thumb_up` | none | Open page in content `QStackedWidget` |
| 自动评论 | `auto_comment` | `comment` | none | Open page in content `QStackedWidget` |
| 自动私信 | `auto_direct_message` | `mail` | none | Open page in content `QStackedWidget` |
| 定时发布 | `scheduled_publishing` | `schedule` | none | Open page in content `QStackedWidget` |
| 系统设置 | `system_settings` | `settings` | none | Open page in content `QStackedWidget` |
| 权限管理 | `permission_management` | `lock_person` | none | Open page in content `QStackedWidget` |
| 日志中心 | `log_center` | `history` | none | Open page in content `QStackedWidget` |
| 版本升级 | `version_upgrade` | `upgrade` | none | Open page in content `QStackedWidget` |

### 2.2 Group behavior

- Group headers are section labels, not routes.
- Expanded mode shows color-coded headers.
- Collapsed mode hides labels; items remain as icon buttons with tooltip.
- Active item state in mockup: tinted background + icon/text accent.

---

## 3. Local Navigation Inventory Found Across Mockups

| Mockup | Local navigation / mode switch found |
|---|---|
| `_1` | Tabs: 全部账号 / 在线 / 离线 / 异常 |
| `_2` | Left tool rail: 剪辑 / 字幕 / 特效 / 音乐 / 素材; timeline tabs: 时间轴 / 关键帧 / 调色 |
| `_3` | Top nav: 数据源 / 图表库 / 我的项目 / 文档; time range segmented control: 1H / 1D / 1W / 1M |
| `_4` | Tabs: 视频表现 / 增长趋势 / 内容分析 |
| `_5` | Top module nav: 概览 / 利润分析 / 库存管理 |
| `_6` | Left settings nav: General / AI Configuration / TTS Services / Browser Isolation / Advancod |
| `_7` | Top nav: 机会矩阵 / 竞品监控 / 趋势发现 |
| `_8` | Device list in left pane; no tabs |
| `_9` | Tabs: 全部任务 / 进行中 / 已完成 / 排队中 / 异常 |
| `_10` | Left nav: 主页控制台 / 自动回复规则 / 数据统计 / 全局设置 |
| `_11` | No tabs; horizontal template gallery + tag chips |
| `_12` | Top nav: 仪表盘 / 报告生成器 / 数据源 / 系统设置 |
| `_13` | Setup stepper: Welcome / AI Config / TTS Config / Browser / Complete |
| `_14` | Top nav: 工作台 / 云端存储 / 处理历史 / 团队协作; sidebar sections: 媒体库 / 分类 |
| `_15` | Top nav: 提取任务 / 历史记录 / 模型库; tabs: 脚本文案 / 视频关键帧 / 视觉分析 |
| `_16` | Sidebar nav: 采集任务 / 历史记录 / API设置 / 系统状态 |
| `_17` | Top nav: 提取/历史/设置 actions only; no tabs |
| `_18` | Top nav: 内容管理 / 数据分析 / 定时发布; view switch: 月视图 / 周视图 |
| `_19` | No tabs; test list + accordion logs |
| `_20` | Top nav: 脚本编辑器 / 脚本库 / 话术库 / 数据看板; left category nav |
| `_21` | Segmented top nav: 全部任务 / 数据采集 / 内容发布 / 运维监控; view switch: 周视图 / 月视图; detail tabs: 基础配置 / 调度规则 / 日志 |
| `_22` | Sidebar nav: 仪表盘首页 / 互动深度分析 / 评论内容审计 / 粉丝画像洞察 / 系统设置; tabs: 互动概览 / 情感趋势 / 用户流转 |
| `_23` | Top nav: 标题优化 / 关键词分析 / 行业模板 / 竞品监控; tabs: 关键词密度 / 分类模板 / 竞品对比 / 敏感词过滤 |
| `_24` | Top nav: 控制台 / 创意工坊 / 资产库 / 系统设置 |
| `ai_1` | Top nav: 工作台 / 工作流设计 / 模板库 / 资源管理 |
| `ai_2` | Top nav: 创作中心 / 我的草稿 / 合规记录; tabs: 标题推荐 / 文案脚本 / 热门话题 |
| `crm` | Filter pills: 全部客户 / VIP客户 / 活跃用户 / 非活跃 |

---

## 4. In-Page Tab Structures

### `_1` 账号管理

| tab_id | Label | Content |
|---|---|---|
| `all_accounts` | 全部账号 (24) | Full account card grid |
| `online_accounts` | 在线 (12) | Online-only cards |
| `offline_accounts` | 离线 (8) | Offline-only cards |
| `warning_accounts` | 异常 (4) | Risk/warning accounts |

### `_2` 视觉编辑器

| tab_id | Label | Content |
|---|---|---|
| `timeline` | 时间轴 | Multi-track clip timeline |
| `keyframes` | 关键帧 | Keyframe editing mode |
| `color_grading` | 调色 | Color grading controls |

### `_4` 竞争对手监控

| tab_id | Label | Content |
|---|---|---|
| `video_performance` | 视频表现 | Video KPI table |
| `growth_trends` | 增长趋势 | Trend comparison view |
| `content_analysis` | 内容分析 | Topic/hashtag analysis |

### `_9` 任务队列

| tab_id | Label | Content |
|---|---|---|
| `all_tasks` | 全部任务 (128) | All queue rows |
| `running_tasks` | 进行中 (12) | Running jobs |
| `completed_tasks` | 已完成 (86) | Completed jobs |
| `queued_tasks` | 排队中 (24) | Waiting jobs |
| `failed_tasks` | 异常 (6) | Failed/problem jobs |

### `_15` 脚本提取工具

| tab_id | Label | Content |
|---|---|---|
| `script_text` | 脚本文案 | Extracted text/script table |
| `video_keyframes` | 视频关键帧 | Keyframe-based extraction view |
| `visual_analysis` | 视觉分析 | Visual scene analysis |

### `_21` 任务调度（right detail panel）

| tab_id | Label | Content |
|---|---|---|
| `basic_config` | 基础配置 | URL, concurrency, retries, recent log snippet |
| `schedule_rules` | 调度规则 | Scheduler rule configuration |
| `task_logs` | 日志 | Detailed run logs |

### `_22` 互动分析

| tab_id | Label | Content |
|---|---|---|
| `engagement_overview` | 互动概览 | Heatmap + overview metrics |
| `sentiment_trends` | 情感趋势 | Sentiment trend analysis |
| `user_flow` | 用户流转 | User transition/journey analysis |

### `_23` 商品标题大师

| tab_id | Label | Content |
|---|---|---|
| `keyword_density` | 关键词密度 | Density guidance bars |
| `category_templates` | 分类模板 | Category-specific title patterns |
| `competitor_comparison` | 竞品对比 | TOP competitor title references |
| `sensitive_word_filter` | 敏感词过滤 | Compliance/sensitive-term review |

### `ai_2` AI文案生成

| tab_id | Label | Content |
|---|---|---|
| `title_recommendations` | 标题推荐 | Variant title list |
| `copy_script` | 文案脚本 | Long-form copy output |
| `hot_topics` | 热门话题 | Suggested topical tags/themes |

### Non-tab multi-step / segmented navigation also present

- `_13`: first-run wizard stepper (`welcome` → `ai_config` → `tts_config` → `browser` → `complete`)
- `_18`: calendar view toggle (`month_view`, `week_view`)
- `_21`: main scope segmented control (`all_tasks`, `data_collection`, `content_publishing`, `ops_monitoring`)

---

## 5. Context Menus, Toolbars, and Primary Actions

### 5.1 Explicit right-click menus

- **None explicitly shown in the mockups.**
- Recommend shell supports optional context menus on tables, cards, calendar items, and asset tiles, but no such menu is visually defined in source mockups.

### 5.2 Recurrent toolbar/action patterns by screen

| Mockup | Notable actions |
|---|---|
| `tk_ops` | Quick search, notifications, Launch New Task, chart range select, View History |
| `_1` | 添加账号, 导入 CSV, filters, 立即开启 isolation, edit/delete/login/test/详情/处理异常, 环境配置 |
| `_2` | Undo/Redo, 导出视频, tool rail, zoom, delete track item |
| `_3` | 发布, data source add, chart type selection, reset, save style template |
| `_4` | 添加竞争对手, tab switching, footer links |
| `_5` | 导出 Excel 报表, refresh, settings, search products, pagination |
| `_6` | Reset to Default, save changes, Restart Now, search providers, filter Enabled/Disabled, Configure, Test Connection, Add Custom Provider |
| `_7` | Matrix bubble selection, 生成调研报告 |
| `_8` | 邀请新设备, 选择文件, 选择文件夹, 查看全部, refresh devices |
| `_9` | 新建任务, delete/pause/start, 全选, filters, row actions (pause/cancel/replay/download/view) |
| `_10` | Enable smart auto-reply, add rule, insert image, insert variable, save/reset rule, 查看更多历史 |
| `_11` | AI 智能优化, template selection, add tag, 查看全部 |
| `_12` | 新建报告, 重置, 应用更改, add filters, export PDF/Excel, 保存模板, 定时发送, 立即生成报告 |
| `_13` | Back, Skip for now, Next Step, settings/help |
| `_14` | 上传文件, grid/list toggle, add tag, 立即下载, 共享素材 |
| `_15` | 本地文件, 开始提取, search/fullscreen, edit extracted row, 复制全文, 导出 JSON, AI 智能改写 |
| `_16` | 新建任务, 开始采集, pause/cancel active task, 查看数据, retry failed |
| `_17` | 开始解析, 全部开始, 清除已完成, pause/resume/cancel, change save path |
| `_18` | Month/week switch, calendar prev/next, 上传视频, 保存草稿, 确认发布 |
| `_19` | RUN ALL TESTS, RUN TEST, accordion expand/collapse |
| `_20` | Save as template, 发布脚本, phrase insert, AI 生成卖点 |
| `_21` | 创建任务, today/week/month switch, pause, 立即运行 |
| `_22` | 导出报告, 分享数据 |
| `_23` | 立即优化, tabs, 查看更多, copy generated title, 重新生成一批 |
| `_24` | 立即启动批量生成, 导出全部, 历史记录, card copy/edit/delete |
| `ai_1` | Undo/Redo, zoom in/out, 保存, 运行工作流, upload music, property edits |
| `ai_2` | 立即生成文案, copy variant, export compliance report |
| `crm` | 筛选, 排序, 详情, pagination, 发送私信, 添加备注, 标签管理, 个人摘要 |

### 5.3 Floating / persistent action surfaces

- `_11`: bottom-right chat/help FAB (`chat_bubble`)
- `_14`: bottom floating batch process bar for selected assets
- `tk_ops`: persistent sidebar CTA `Launch New Task`
- `ai_1`: persistent bottom status bar
- `_12`, `_17`, `_19`, `_8`: footer/status surfaces used as operational bars

---

## 6. Navigation Flow Diagram

### 6.1 First launch

```text
App Launch
   |
   v
Setup Wizard (`_13`)
   |- Welcome
   |- AI Config
   |- TTS Config
   |- Browser
   `- Complete
   |
   v
Dashboard (`dashboard` / `tk_ops`)
```

### 6.2 Dashboard to any page

```text
Dashboard
   |
   +--> Sidebar item click
           |
           v
     route_id resolved
           |
           v
     Center QStackedWidget switches page
           |
           +--> optional right detail panel opens if page supports it
           `--> optional status bar updates with page/job state
```

### 6.3 Page to sub-tab navigation

```text
Primary page loaded
   |
   +--> local tab / segmented switch
           |
           +--> swap inner stacked panel
           +--> retain shell route selection
           `--> update toolbar/detail-panel context only
```

### 6.4 Global search to page jump

```text
Global Search (title bar)
   |
   +--> type page / task / customer / asset keyword
           |
           +--> route result selected
           |      |
           |      v
           |   open target shell route
           |
           `--> entity result selected
                  |
                  v
               open parent route + focus row/card/detail panel
```

---

## 7. Shell Component Inventory

| Component | Purpose | Notes from mockups |
|---|---|---|
| `SearchBar` | Global/entity search | Title bar search appears in shell and many pages |
| `NotificationBell` | Alerts/tasks/messages | Often shows unread dot |
| `UserAvatar` | Profile/account entry | Sometimes with name/role block |
| `NavGroup` | Sidebar section wrapper | Color-coded headers for role zones |
| `NavItem` | Primary route entry | Icon + label + active highlight |
| `BreadcrumbBar` | Page context trail | Not explicitly shown; needed for deep tool pages |
| `StatusBar` | Connectivity/job/validation/footer state | Optional, used by several operational mockups |
| `CollapsibleSidebar` | Expand/collapse shell navigation | Required by shell brief |
| `PageHost` | `QStackedWidget` route container | Canonical center pane |
| `DetailPanel` | Context-specific inspector | Reused by account, asset, workflow, CRM, compliance pages |
| `SectionTabs` | Inner page navigation | Used across analytics/editor/reporting pages |
| `QuickActionBar` | Page-level primary actions | e.g. export, create, run, save |
| `WarningBanner` | Risk/compliance/system notices | Seen in `_1`, `_6`, `ai_2` |
| `FloatingActionButton` | Always-available assist action | Seen in `_11`; pattern reusable |
| `BatchActionBar` | Multi-select bulk actions | Seen in `_14` |

---

## 8. IA Notes / Constraints from Mockups

- Only the `tk_ops` shell mockup defines the **global desktop sidebar taxonomy**.
- Other mockups introduce **local navigation**, **mode switches**, and **specialized workspaces**, but do not replace the primary shell tree.
- Right panels are common enough to treat as a reusable shell pattern, not page-specific exceptions.
- Several tools (`_8`, `_17`, `_19`) behave like utility workspaces but can still live inside shell routes rather than separate windows.
- `_13` is a pre-shell onboarding flow; it should not appear as a sidebar route.
- No explicit desktop menubar (`File/Edit/View/...`) is present in the mockups.
- No explicit right-click menu visual is present anywhere in reviewed sources.

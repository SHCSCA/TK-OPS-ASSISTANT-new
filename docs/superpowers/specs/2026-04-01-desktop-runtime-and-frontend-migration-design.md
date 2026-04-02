# TK-OPS 单壳切换与小文件约束实施 Spec（V2）

> 本文档用于替换上一版“旧宿主与新宿主并存过渡”的实施设计。  
> 本版将以下两项要求提升为**不可妥协的硬约束**：
>
> 1. **禁止大文件**：不允许再出现单文件数千行实现，所有模块必须按职责边界合理拆分。  
> 2. **禁止双壳并存运行**：不允许旧 PySide6 壳与新 Tauri 壳在任何环境下并行运行；旧时代代码只允许作为迁移参考，不再进入运行、联调、打包、灰度和发布路径。
> 3. **保证全局性**：所有新开发必须遵循统一架构和规范，确保系统一致性和可维护性。
> 4. **全局采用中文注释**：所有代码必须使用中文注释，确保能清晰理解代码意图和逻辑。
> 5. **全局异常处理以及日志记录**：所有异常必须被捕获并记录，确保系统稳定性和可追踪性。定义统一的日志格式和错误处理机制，便于调试和维护。
> 6. **全局配置总线**：所有配置必须通过统一的配置总线管理，确保配置的一致性和可维护性。
---

## 1. 文档目标

本 spec 的目标不是“尽量平滑兼容旧结构”，而是：

1. 建立 **Tauri + Vue 3 + TypeScript + Python Runtime** 的**唯一未来架构**。
2. 停止旧 PySide6 壳的继续演进，并把它从运行体系中移除。
3. 通过**小文件规则、模块边界规则、CI 规则**，彻底避免新的“大文件 / 巨类 / 巨型页面加载器”继续出现。
4. 在此基础上，完成首批 P0 页面迁移，形成可运行、可演示、可回退的 Windows alpha。

---

## 2. 背景

当前仓库已经不是原型仓库，而是一套可运行的本地桌面系统：

- 旧宿主是 **PySide6 + QtWebEngine**。
- 前端表示层仍由 HTML / CSS / JavaScript 大文件驱动。
- `bridge.py`、`routes.js`、`page-loaders.js` 等承担了过多职责。
- Python 侧已经有数据库模型、迁移、业务服务、seed、sample data 和测试资产。

历史实现带来的主要问题是：

1. **宿主层被绑死在 PySide6 生命周期里**。
2. **桥接层膨胀成 God Object**。
3. **前端页面逻辑被堆进少数大文件**。
4. **如果继续采用“双壳并行过渡”**，最终只会得到：
   - 双入口
   - 双联调路径
   - 双打包路径
   - 双运行心智
   - 下不掉的历史包袱

因此，本版 spec 明确改为：

> **单壳切换、旧壳退场、小文件强约束、按域拆解、以 Tauri + Vue3 + TS + Python Runtime 为唯一演进方向。**

---

## 3. 硬约束

## 3.1 单壳约束（Hard Requirement）

### 规则
1. 自本 spec 生效后，**唯一允许继续开发的桌面宿主是 Tauri**。
2. 旧 `desktop_app/app.py` 不再作为任何默认入口继续演进。
3. 旧 PySide6 壳不再进入：
   - 新功能开发
   - 默认联调链路
   - 打包链路
   - alpha / beta / release 发布链路
4. 旧 `desktop_app` 代码只允许作为：
   - 迁移参考源码
   - 业务逻辑复用来源
   - 截图和行为对照基线

### 明确禁止
以下行为一律禁止：

- 同时运行旧 PySide6 壳与新 Tauri 壳
- 在开发机上以“旧壳做业务联调、新壳做 UI 联调”的方式长期共存
- 在发布包中同时放入两个宿主入口
- 在旧壳中继续新增页面、slot、桥接接口或临时功能
- 为了赶进度继续把新能力接进旧 `bridge.py`

### 实施含义
- 旧壳不是“慢慢淘汰”，而是**从本轮开始退出运行体系**。
- 迁移不是“双壳共存迁移”，而是**单壳替换迁移**。
- 旧代码可以保留在仓库里，但**不能再是运行中的系统**。

---

## 3.2 小文件约束（Hard Requirement）

### 目标
防止新架构重演旧架构问题。  
**任何文件都必须具备清晰职责边界，不允许出现数千行单文件。**

### 默认行数限制

#### 前端（TypeScript / JavaScript）
- `.ts` / `.js`：**300 行警戒，400 行强制拆分**
- `*.types.ts`：**200 行警戒，300 行强制拆分**
- `*.client.ts`：**200 行警戒，300 行强制拆分**
- `*.store.ts`：**220 行警戒，320 行强制拆分**
- `*.constants.ts`：**150 行警戒，220 行强制拆分**

#### Vue
- 单个 `.vue` 文件总长度：**250 行警戒，350 行强制拆分**
- `script setup` 部分：**不超过 180 行**
- 模板中如存在 3 个以上复杂区域，必须拆子组件

#### Python
- `.py`：**350 行警戒，500 行强制拆分**
- 单个 HTTP handler / routes 文件：**200 行警戒，280 行强制拆分**
- 单个 WS handler 文件：**180 行警戒，260 行强制拆分**
- 单个 service 文件：**300 行警戒，420 行强制拆分**
- 单个 adapter 文件：**250 行警戒，350 行强制拆分**

#### Rust
- `.rs`：**250 行警戒，350 行强制拆分**
- command 不允许全部堆在一个文件
- runtime manager、paths、security、commands 分文件实现

### 允许例外的文件
以下文件可申请例外，但必须在文件头写明原因：

- 自动生成代码
- migration snapshot
- fixture data
- 常量字典且无法自然拆分

### 强制拆分原则
任一文件达到强制拆分阈值时，必须按以下顺序拆：

1. **先拆类型**
2. **再拆 API / 客户端**
3. **再拆 ViewModel / service**
4. **最后拆子组件 / 子处理器**

严禁继续用注释分区冒充拆分。

---

## 4. 架构总原则

1. **单壳原则**：只有 Tauri 是运行宿主。
2. **单前端原则**：只有 Vue 3 + TypeScript 是页面表示层。
3. **单 runtime 原则**：只有 Python sidecar runtime 承担业务、数据和 AI 能力。
4. **显式协议原则**：前后端交互必须走明确的 HTTP / WS / command 边界。
5. **小文件原则**：每个文件只承担一类职责。
6. **先主链路原则**：先把第一条业务主链跑通，再扩页面，再优化内部结构。
7. **旧代码只读原则**：旧壳不再生长，旧代码优先提取复用，不再就地增强。

---

## 5. 目标架构

```text
Tauri (唯一宿主)
    ↓
Vue 3 + TypeScript (唯一前端表示层)
    ↓
HTTP / WebSocket (唯一业务通信边界)
    ↓
Python Runtime Sidecar (唯一业务/AI runtime)
    ↓
SQLite / SQLAlchemy
```

---

## 6. 层级职责

## 6.1 Tauri 层
只负责：

- 窗口生命周期
- 文件对话框
- 剪贴板
- 外部链接
- 版本信息
- 应用路径
- Python runtime 启停与守护
- 本地权限边界与 capabilities

**禁止承担：**
- 业务聚合
- 页面数据拼装
- AI 逻辑
- 任务状态机
- 复杂数据转换

---

## 6.2 Vue 层
只负责：

- 页面与组件
- UI 状态
- 页面级 ViewModel
- 路由与布局
- 设计系统
- HTTP / WS 调用接入
- 用户可见错误处理

**禁止承担：**
- 数据库存取
- 系统级文件能力
- 任务执行
- AI provider 管理逻辑本体
- 任意后台轮询大杂烩

---

## 6.3 Python Runtime 层
只负责：

- 业务服务
- 数据访问
- AI 接入
- 任务队列与执行
- 调度
- 聚合查询
- 流式事件
- 设置持久化

**禁止承担：**
- 桌面窗口控制
- 前端模板拼装
- 宿主 UI 生命周期

---

## 7. 新目录结构

```text
tk-ops/
├─ apps/
│  ├─ desktop/
│  │  ├─ src/
│  │  │  ├─ app/
│  │  │  │  ├─ router/
│  │  │  │  ├─ stores/
│  │  │  │  ├─ providers/
│  │  │  │  ├─ guards/
│  │  │  │  └─ boot/
│  │  │  ├─ layouts/
│  │  │  ├─ pages/
│  │  │  ├─ components/
│  │  │  ├─ modules/
│  │  │  ├─ styles/
│  │  │  └─ types/
│  │  └─ src-tauri/
│  │     ├─ src/
│  │     │  ├─ commands/
│  │     │  ├─ runtime/
│  │     │  ├─ state/
│  │     │  ├─ security/
│  │     │  └─ paths/
│  │     ├─ capabilities/
│  │     └─ tauri.conf.json
│  │
│  └─ py-runtime/
│     ├─ src/
│     │  ├─ bootstrap/
│     │  ├─ api/
│     │  │  ├─ http/
│     │  │  ├─ ws/
│     │  │  └─ common/
│     │  ├─ application/
│     │  ├─ infrastructure/
│     │  ├─ legacy_adapter/
│     │  └─ shared/
│     ├─ tests/
│     └─ pyproject.toml
│
├─ packages/
│  ├─ protocol/
│  ├─ design-tokens/
│  └─ ui-kit/
│
├─ docs/
│  ├─ architecture/
│  ├─ migration/
│  └─ release/
│
├─ scripts/
└─ legacy/
   └─ desktop_app_reference/
```

---

## 8. 旧代码处置策略（单壳版）

## 8.1 旧 PySide6 壳的处理方式

### 目标
让旧时代的东西真正过去，但不粗暴删除仍需参考的代码。

### 规则
1. 旧 `desktop_app` 不再作为主运行入口。
2. 旧 `desktop_app` 不再作为开发默认联调入口。
3. 所有 README、脚本、开发文档默认入口切换为新壳。
4. 旧壳源码移动到：
   - `legacy/desktop_app_reference/`
   或
   - 独立归档分支

### 必须执行的切断动作
- 移除旧壳的默认启动脚本
- 移除旧壳的默认打包脚本
- 移除旧壳在主文档中的运行指引
- 在旧壳目录顶部写明：**reference only / do not extend**

### 明确禁止
- 不允许再改旧壳页面
- 不允许再给旧壳新增 slot
- 不允许再以旧壳跑 P0 页面
- 不允许以“先在旧壳验证逻辑”为理由继续把新需求落在旧实现上

---

## 8.2 旧业务代码的复用方式

### 允许复用
允许从旧代码中提取和复用：

- `database/`
- `migrations/`
- `services/`
- `sample_data/`
- 可复用 tests

### 不允许继续增长
禁止继续往以下旧模块堆功能：

- `ui/bridge.py`
- `assets/js/routes.js`
- `assets/js/page-loaders.js`
- `assets/js/bindings.js`
- `ui/web_shell.py`
- `app.py`

### 复用方式
只允许通过以下方式复用：

- `legacy_adapter`
- service adapter
- repository adapter
- protocol remapper

不允许通过以下方式复用：

- 继续走 QWebChannel
- 继续往旧 DOM loader 补逻辑
- 让新前端去兼容旧 loader 心智

---

## 9. 文件与模块拆分规则

## 9.1 页面拆分模板（强制）

每个页面必须按如下结构组织：

```text
dashboard/
├─ DashboardPage.vue
├─ useDashboardViewModel.ts
├─ dashboard.store.ts
├─ dashboard.client.ts
├─ dashboard.types.ts
├─ dashboard.constants.ts
└─ components/
   ├─ DashboardStats.vue
   ├─ DashboardTrend.vue
   ├─ DashboardActivity.vue
   └─ DashboardSystemBoard.vue
```

### 页面拆分规则
- `Page.vue` 只负责页面布局和组合
- `usePageViewModel.ts` 负责交互编排
- `page.store.ts` 负责状态持久与缓存
- `page.client.ts` 负责 API 调用
- `page.types.ts` 负责类型
- 复杂区域必须进 `components/`

### 页面禁止项
- 不允许列表、详情、表单、图表都写在一个 `.vue`
- 不允许在 `.vue` 内写复杂 fetch / ws 逻辑
- 不允许在页面文件里堆大量常量和映射表
- 不允许把多页共用 UI 粘在某一页目录里

---

## 9.2 前端通用模块拆分模板

```text
modules/
├─ api/
│  ├─ httpClient.ts
│  ├─ errorMapper.ts
│  ├─ endpoints/
│  └─ interceptors/
├─ ws/
│  ├─ runtimeSocket.ts
│  ├─ reconnect.ts
│  ├─ eventRouter.ts
│  └─ eventTypes.ts
├─ commands/
│  ├─ app.ts
│  ├─ fileDialog.ts
│  ├─ clipboard.ts
│  └─ runtime.ts
└─ theme/
   ├─ tokens.ts
   ├─ applyTheme.ts
   └─ themeTypes.ts
```

---

## 9.3 Python Runtime 拆分模板

### HTTP 资源域模板
```text
api/http/accounts/
├─ routes.py
├─ handlers.py
├─ schemas.py
├─ mapper.py
└─ service_adapter.py
```

### WS 事件域模板
```text
api/ws/
├─ ai_stream.py
├─ task_stream.py
├─ runtime_status.py
└─ ws_common.py
```

### Application 层模板
```text
application/
├─ accounts/
│  ├─ dto.py
│  ├─ queries.py
│  ├─ commands.py
│  └─ service.py
├─ tasks/
├─ providers/
├─ settings/
└─ dashboard/
```

### Legacy 适配层模板
```text
legacy_adapter/
├─ accounts_adapter.py
├─ tasks_adapter.py
├─ providers_adapter.py
├─ settings_adapter.py
└─ dashboard_adapter.py
```

### Python 禁止项
- 不允许再造新的 `bridge_all_in_one.py`
- 不允许把所有 HTTP 路由写进一个 `routes.py`
- 不允许把所有 ws 事件塞进一个 `socket.py`
- 不允许把所有 service 混进一个 mega service 文件

---

## 9.4 Tauri / Rust 拆分模板

```text
src-tauri/src/
├─ main.rs
├─ commands/
│  ├─ app.rs
│  ├─ file_dialog.rs
│  ├─ clipboard.rs
│  ├─ runtime.rs
│  └─ external.rs
├─ runtime/
│  ├─ manager.rs
│  ├─ spawn.rs
│  ├─ handshake.rs
│  └─ health.rs
├─ security/
│  ├─ capabilities.rs
│  ├─ token.rs
│  └─ csp.rs
├─ paths/
│  ├─ app_paths.rs
│  └─ resource_paths.rs
└─ state/
   ├─ app_state.rs
   └─ runtime_state.rs
```

### Rust 禁止项
- 不允许所有 command 写在 `main.rs`
- 不允许 runtime 生命周期和 command 混写
- 不允许安全边界逻辑散落在多个无名文件中

---

## 10. 协议边界

## 10.1 Tauri Command 只处理桌面短能力

首批 command：

- `get_app_version`
- `open_file_dialog`
- `save_file_dialog`
- `copy_to_clipboard`
- `open_external_url`
- `runtime_health`
- `restart_runtime`
- `get_app_paths`

### 禁止
- 不允许通过 command 直接做复杂业务查询
- 不允许通过 command 代理全部业务 API
- 不允许把 runtime 业务逻辑塞回宿主

---

## 10.2 HTTP 只处理页面初始化和 CRUD

首批 HTTP 资源域：

- `/health`
- `/settings`
- `/accounts`
- `/providers`
- `/tasks`
- `/dashboard/overview`
- `/scheduler`
- `/copywriter/*`

### 原则
- 列表、详情、创建、更新、删除走 HTTP
- 请求与响应必须用明确 schema
- 错误返回走统一 envelope

---

## 10.3 WebSocket 只处理长任务与实时事件

首批 WS 事件：

- `runtime.status`
- `task.progress`
- `task.completed`
- `task.failed`
- `ai.stream.delta`
- `ai.stream.done`
- `ai.stream.error`

### 原则
- 所有长任务和流式能力走 WS
- 不再复用旧的隐式 dataChanged 推送心智
- 前端必须通过 event router 统一消费，不允许每页各自裸连一套 socket

---

## 11. 运行与安全规则

## 11.1 Runtime 握手与鉴权

必须满足：

1. Python runtime 只监听 `127.0.0.1`
2. 启动时使用随机端口
3. Tauri 启动 runtime 时生成 session token
4. HTTP / WS 都必须带 token
5. token 不落长期明文文件

---

## 11.2 数据库运行规则

### 规则
- **只有新 Tauri + Python runtime 进入运行链路**
- 旧 PySide6 壳不再连生产数据库
- 不存在“新旧壳同时访问一份库”的场景

### 迁移期要求
- schema migration 只由新 runtime 负责
- 开发和联调脚本只服务新架构
- 若需旧库对照，使用独立样本库副本，不允许并行跑双壳

---

## 12. P0 页面范围

本轮只允许进入以下页面：

1. Setup Wizard
2. Dashboard
3. 账号管理
4. AI 供应商配置
5. 任务队列
6. 任务调度
7. AI 文案生成
8. 系统设置

### 明确不进入本轮的新前端迁移
- 视觉编辑器
- AI 内容工厂
- 可视化实验室
- 创意工坊
- 视频编辑 / 导出 / 监看相关复杂页面

---

## 13. P0 页面最低交付标准

## 13.1 Dashboard
必须能演示：

- 打开页面加载 overview
- 切换时间范围
- 展示 activity
- 展示 systems 状态
- 错误时有可见提示

---

## 13.2 账号管理
必须能演示：

- 列表加载
- 打开详情抽屉
- 新建 / 编辑基础字段
- Cookie / 校验状态展示
- 删除与错误提示

---

## 13.3 AI 供应商配置
必须能演示：

- 列表
- 新增
- 编辑
- 启用
- 测试连接
- 删除

---

## 13.4 任务队列
必须能演示：

- 列表
- 状态筛选
- 启动 / 删除 / 详情
- WS 实时刷新

---

## 13.5 Setup Wizard
必须能演示：

- 许可证状态
- 供应商引导
- 默认模型设置
- 默认市场 / 工作流设置
- 完成状态保存

---

## 13.6 系统设置
必须能演示：

- 主题切换
- 语言
- 代理
- 超时
- 并发
- 通知设置
- 保存与回显

---

## 13.7 任务调度
必须能演示：

- 调度列表
- 新建调度
- 启停
- 删除
- 最小持久化闭环

---

## 13.8 AI 文案生成
必须能演示：

- 输入 prompt
- 选择 provider / model
- 发起生成
- WS 流式输出
- 复制结果
- 错误反馈

---

## 14. 实施阶段

## Phase A：切断旧壳运行地位
### 目标
把旧壳从“运行系统”降级为“参考源码”。

### 必做项
- 停止旧壳继续接收需求
- README 默认入口切换到新架构
- 打包链路移除旧壳
- 旧壳移动到 `legacy/desktop_app_reference/` 或归档分支
- 标记 `reference only`

### 验收
- 团队不再用旧壳跑新需求
- 不再有双壳并行联调

---

## Phase B：新工程骨架与协议冻结
### 目标
建立新目录和明确协议，避免后续乱写。

### 必做项
- 建立 `apps/desktop`
- 建立 `apps/py-runtime`
- 建立 `packages/protocol`
- 冻结 HTTP / WS / error envelope

### 验收
- 新目录齐备
- 协议文档可供前后端共同开发

---

## Phase C：Python Runtime 第一版
### 目标
形成不依赖 PySide6 的独立 runtime。

### 必做项
- runtime 入口
- settings / container
- legacy adapter
- `/health`
- 首批 HTTP
- 首批 WS

### 验收
- runtime 可单独启动
- `/health` 正常
- WS 可推送事件

---

## Phase D：Tauri 宿主
### 目标
形成唯一桌面壳。

### 必做项
- Tauri 初始化
- runtime manager
- handshake + token
- 首批 commands
- capability 配置

### 验收
- Tauri 启动即拉起 runtime
- command 可用
- runtime 崩溃可见

---

## Phase E：Vue 壳层与基础组件
### 目标
替代旧壳 HTML + 原生 JS 大文件体系。

### 必做项
- AppShell
- Sidebar
- TitleBar
- DetailPanel
- StatusBar
- HTTP / WS 客户端
- 设计 tokens
- 首批基础组件

### 验收
- 新壳可承载页面
- 页面不再依赖旧 loader

---

## Phase F：P0 页面迁移
### 目标
打通第一条业务主链。

### 必做项
- Dashboard
- 账号管理
- AI 供应商配置
- 任务队列
- Setup Wizard
- 系统设置
- 任务调度
- AI 文案生成

### 验收
- 关键页面在新壳下跑通
- AI stream 和 task event 已落地

---

## Phase G：打包与 Alpha
### 目标
形成单壳 Windows alpha。

### 必做项
- runtime 打包
- Tauri installer
- smoke tests
- alpha 说明
- 已知问题清单

### 验收
- 只包含 Tauri + Python runtime
- 不包含旧 PySide6 壳入口
- 可安装、可演示、可回归

---

## 15. CI 与 Code Review 规则

## 15.1 CI 必须检查
1. 文件行数阈值
2. 禁止新增旧壳运行入口
3. 禁止新增对旧 `bridge.py` 的功能性扩展
4. 页面目录结构是否合规
5. routes / handlers / commands 是否超限

---

## 15.2 Code Review 必须拒绝的 PR
以下 PR 必须直接拒绝：

- 往旧 PySide6 壳加功能
- 给旧 `bridge.py` 新增业务 slot
- 新增超过阈值的大文件且未拆分
- 页面逻辑写回单一 mega `.vue`
- 裸 fetch / 裸 WebSocket 散落到页面中
- 宿主层承担业务逻辑
- 以赶进度为由恢复双壳并行运行

---

## 16. 验收口径

本 spec 完成时，必须满足以下口径：

1. **旧 PySide6 壳不再进入运行链路**
2. **新 Tauri 壳成为唯一桌面宿主**
3. **Python runtime 成为唯一业务 runtime**
4. **所有新实现遵守小文件边界规则**
5. **P0 页面主链路在新壳中跑通**
6. **AI 文案生成流式能力与任务队列实时事件能力落地**
7. **生成只包含新壳的 Windows alpha**
8. **旧代码仅作为参考，不再作为可运行系统参与联调**

---

## 17. 一句话结论

本轮不是“保守兼容式迁移”，而是：

**以 Tauri 为唯一宿主，以 Vue3 + TypeScript 为唯一前端，以 Python runtime 为唯一业务底座，在严格小文件约束下完成单壳切换，彻底结束旧 PySide6 壳继续运行和继续演进的可能。**

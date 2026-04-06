# 壳层中文化与品牌收口计划（含真实接入审计）

## 目标

在不打断“旧课程 1:1 迁移”主节奏的前提下，完成以下收口：

- 顶部与启动页品牌图标统一到 `tkops.ico`
- Runtime 展示链路去英文码并全量中文映射
- 通知中心与运行状态弹层在窄屏下可完整可用
- 左下角“当前阶段”由路由迁移矩阵动态驱动
- 已迁移 8 页完成“非假数据”审计与测试收口

## 范围

本轮包含：

1. `logo + 启动页 + runtime + 通知中心 + 运行状态 + 左下角当前阶段框`
2. 已迁移 8 页（dashboard/accounts/providers/tasks/scheduler/copywriter/setup/settings）真实接入审计

本轮不包含：

- 44 路由一次性全量清理
- 通知中心整体视觉重设计
- 品牌文案从 `TK-OPS` 改名为 `TKOPS`

## 文件地图

文档：

- `docs/superpowers/plans/2026-04-03-shell-chinese-brand-runtime-audit.md`
- `docs/superpowers/specs/2026-04-03-shell-chinese-brand-runtime-audit-design.md`

品牌与壳层：

- `apps/desktop/src/layouts/TitleBar.vue`
- `apps/desktop/src/layouts/DetailPanel.vue`
- `apps/desktop/src/layouts/Sidebar.vue`
- `apps/desktop/public/splash.html`
- `apps/desktop/src/styles/main.css`
- `desktop_app/assets/css/shell.css`
- `desktop_app/assets/css/components.css`

Runtime 映射与状态：

- `apps/desktop/src/modules/shell/useShellStore.ts`
- `apps/desktop/src/modules/runtime/runtimePresentation.ts`（新增）
- `apps/desktop/src/pages/shared/MigrationPlaceholderPage.vue`
- `apps/desktop/src/app/router/routeManifest.ts`
- `apps/desktop/src/app/router/migrationProgress.ts`（新增）

真实接入审计（8 页）：

- `apps/desktop/src/modules/dashboard/useDashboardData.ts`
- `apps/desktop/src/modules/accounts/useAccountsData.ts`
- `apps/desktop/src/modules/providers/useProvidersData.ts`
- `apps/desktop/src/modules/tasks/useTasksData.ts`
- `apps/desktop/src/modules/scheduler/useSchedulerData.ts`
- `apps/desktop/src/modules/copywriter/useCopywriterData.ts`
- `apps/desktop/src/modules/setup/useSetupWizardData.ts`
- `apps/desktop/src/modules/settings/useSettingsData.ts`

测试：

- `tests/test_desktop_frontend_routes.py`
- `tests/test_tauri_host_scaffold.py`
- `tests/test_page_runtime_data.py`
- `tests/test_shell_runtime_presentation.py`（新增）

## 分阶段执行

### 阶段 1：品牌与图标收口

- 左上角 logo 从字母块改为图标渲染
- 启动页中间 logo 改为图标
- 保留品牌文字 `TK-OPS`

### 阶段 2：Runtime 中文映射全链路

- 新增统一映射层，输入原始状态码，输出中文文案与语义色调
- 覆盖状态、启动模式、主题映射
- 展示覆盖：底栏 + 顶栏状态弹层 + 右侧详情

### 阶段 3：窄屏弹层可用性

- 通知中心与运行状态弹层修复遮挡、溢出、层级
- 在 `960/860/760` 下确保可读、可滚动、可点击

### 阶段 4：动态阶段框

- 基于 `routeManifest` 动态计算：已迁移/总数、阶段说明、下一优先迁移页
- 左侧栏与占位页共用同一数据来源，清理静态双口径

### 阶段 5：已迁移 8 页真实接入审计

- 确认页面数据来自 runtime API / 宿主状态
- 缺数据统一中性空态，不填假业务数字
- 对发现的硬编码非中性回退进行修复（优先 scheduler 窗口回退）

## 验证方式

自动化：

- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_tauri_host_scaffold.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_shell_runtime_presentation.py -v`
- `npm run typecheck`
- `npm run build`
- `npm run tauri:smoke`

手工：

- 启动页为图标，无 `TK` 字母块
- Runtime 三处展示均中文，无英文状态码裸露
- `960/860/760` 下通知中心和状态弹层可完整操作
- 左下角阶段信息随路由迁移矩阵变化

## 边界与回退点

- 若图标资源在 dev/dist 路径解析冲突，统一落到 `apps/desktop/public/tkops.ico`
- 若窄屏弹层样式调整导致其他层级回归，优先保障点击可用与不遮挡，再做视觉微调
- 若 8 页审计发现超出本轮范围的大面积历史问题，仅记录清单，不做范围外漂移改造

# 概览看板 1:1 复刻实施计划（旧壳基线）

## 目标

以 `desktop_app/assets/app_shell.html` 的 `route-dashboard-main` 为唯一基线，完成概览看板 Vue 版“视觉 + 交互”1:1 复刻，同时保持真实 runtime 数据接入。

## 关键决策

1. 复刻范围：视觉 + 交互全 1:1。
2. 数据口径：真实数据 + 中性空态，不引入假数据。
3. 验收基线：旧壳模板优先。
4. 快捷入口：点击后更新右侧详情卡，不直接跳路由。

## 执行阶段

### 阶段 1：结构与样式对齐

- 对齐 dashboard 的 DOM 结构与关键类语义。
- 保留现有 runtime 数据渲染能力。

### 阶段 2：交互行为对齐

- 范围切换、活动流、系统状态、快捷入口交互按旧壳路径对齐。
- 快捷入口改为详情触发型交互。

### 阶段 3：右侧详情区打通

- 在 shell store 新增 `dashboardDetailState`。
- `DashboardPage` 写入详情态，`DetailPanel` 在 dashboard 路由优先渲染该详情态。

### 阶段 4：数据映射与空态

- 快捷入口详情卡按约定数据源映射。
- 缺失数据统一 `--`/`暂无数据`。

### 阶段 5：测试与验收

- 更新静态契约测试。
- 执行 pytest + typecheck + build。

## 验证命令

- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `npm run typecheck`
- `npm run build`

# 运营中心模块下线计划

## Summary
- 目标：将 `operations-center` 从当前新壳产品面完整移除，不再出现在菜单、路由、页面挂载、右栏详情状态、样式导入、测试断言和迁移文档中。
- 原因：用户已明确该模块当前不需要继续保留；同时它会继续放大菜单噪音、迁移统计和维护成本。
- 流程：本计划确认后，补 `docs/superpowers/specs/2026-04-08-remove-operations-center-design.md`，再进入实现。

## Goals
1. 从新壳左侧菜单、路由清单和页面组件映射中移除 `operations-center`。
2. 删除运营中心前端页面、专属模块、右栏详情状态和页面样式接线，避免遗留死代码。
3. 同步更新测试、迁移矩阵、roadmap 与已有运营中心 plan/spec，确保仓库口径一致。
4. 不扩大到旧壳 `desktop_app/` 的历史参考代码和无关 runtime 服务，保持本轮为新壳产品面收口。

## Scope
### In Scope
- `apps/desktop/src/app/router/routeManifest.ts`
  - 删除 `operations-center` manifest 项。
  - 同步移除 `pageKind: 'operationsCenter'` 的产品面使用。
- `apps/desktop/src/app/router/routes.ts`
  - 删除 `OperationsCenterPage` 导入与页面组件映射。
- `apps/desktop/src/pages/operations/OperationsCenterPage.vue`
  - 删除文件。
- `apps/desktop/src/modules/operations/`
  - 删除 `useOperationsCenterData.ts`
  - 删除 `operationsCenter.helpers.ts`
  - 删除 `operationsCenter.types.ts`
- `apps/desktop/src/layouts/DetailPanel.vue`
  - 删除运营中心专属 detail 分支。
- `apps/desktop/src/modules/shell/useShellStore.ts`
  - 删除 `OperationsDetailState`、默认状态、setter/resetter 与导出项。
- `apps/desktop/src/styles/operations-center.css`
  - 删除文件。
- `apps/desktop/src/main.ts`
  - 删除 `operations-center.css` 导入。
- 测试与文档：
  - `tests/test_desktop_frontend_routes.py`
  - `tests/test_page_runtime_data.py`（如存在运营中心数据断言）
  - `docs/migration/page-matrix.md`
  - `docs/migration/current-status-and-roadmap.md`
  - `docs/UI-DESIGN-PRD.md` 中若有“当前已迁移/当前保留入口”类表述则做最小同步
  - `docs/superpowers/plans/2026-04-08-operations-center-vertical-slice.md`
  - `docs/superpowers/specs/2026-04-08-operations-center-vertical-slice-design.md`

### Out of Scope
- 不删除旧壳 `desktop_app/` 中的 `operations-center` 历史 route、factory、loader、CSS 和模板代码。
- 不删除 Python runtime 中通用 `tasks/accounts/assets/providers` 能力。
- 不顺带重排其他运营域页面的信息架构，只移除 `operations-center` 本身。
- 不在本轮直接做全局字体/壳层缩放重构；样式问题单独分析后再决定是否开新计划。

## Baseline
- 当前新壳入口来源：`apps/desktop/src/app/router/routeManifest.ts`
- 当前新壳路由注册：`apps/desktop/src/app/router/routes.ts`
- 当前页面实现：`apps/desktop/src/pages/operations/OperationsCenterPage.vue`
- 当前数据层：`apps/desktop/src/modules/operations/useOperationsCenterData.ts`
- 当前右栏接线：`apps/desktop/src/layouts/DetailPanel.vue` + `apps/desktop/src/modules/shell/useShellStore.ts`
- 当前样式接线：`apps/desktop/src/main.ts` + `apps/desktop/src/styles/operations-center.css`
- 当前前端断言：`tests/test_desktop_frontend_routes.py` 已要求 `operations-center` 为 implemented 页面并存在 detail state 分支
- 当前文档状态：
  - `docs/migration/page-matrix.md` 把 `operations-center` 标为“已迁移”
  - 已存在迁移计划与设计：
    - `docs/superpowers/plans/2026-04-08-operations-center-vertical-slice.md`
    - `docs/superpowers/specs/2026-04-08-operations-center-vertical-slice-design.md`

## Implementation Phases
### Phase 1: 路由与页面入口下线
- 从 manifest 和 routes 中删除 `operations-center`。
- 删除页面组件、模块文件和样式导入。
- 确保 Sidebar、路由搜索和迁移统计不再暴露该页面。

### Phase 2: 壳层状态与详情分支清理
- 从 `useShellStore.ts` 清理运营中心 detail state。
- 从 `DetailPanel.vue` 删除 `operations-center` 相关渲染与事件分支。
- 确保删除后其余 detail 分支不受影响。

### Phase 3: 测试与文档同步
- 删除或改写运营中心存在性断言。
- 更新迁移矩阵、roadmap 和已存在的运营中心 plan/spec，明确该模块已下线，不再作为迁移目标。

### Phase 4: 验证
- 运行前端路由/页面契约相关 pytest。
- 运行前端 typecheck 与 build，确认没有悬空导入、无效类型或 CSS 引用。

## Validation
### 自动化
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工验收
- 左侧菜单中不再出现“运营中心”。
- 搜索或直接输入路由后不再进入该页面。
- 右侧 DetailPanel 不再保留运营中心专属状态块。
- 文档中不再把它当成当前保留的迁移目标或已迁移页面。

## Risks
1. `tests/test_desktop_frontend_routes.py` 当前把运营中心视为真实 implemented 页面，删除时会牵连 detail panel 和 shell store 断言。
   - 应对：实现阶段同步清理测试，而不是只删页面代码。
2. 迁移文档和既有 plan/spec 已把运营中心写进已迁移列表，若不收口会造成产品范围与代码状态不一致。
   - 应对：本轮把运营中心相关 plan/spec 明确标为已废弃或已下线背景文件。
3. 若仅删页面，不删 shell store/detail 分支，会留下死状态和未来维护噪音。
   - 应对：把壳层状态清理列为硬性范围，不允许跳过。

## Rollback
- 若删除后发现仍有关键入口或测试链依赖，可先恢复 manifest 中的单条占位项，但不恢复页面实现。
- 所有改动集中在新壳产品面，便于局部回滚，不影响旧壳参考代码。

## Exit Criteria
- `operations-center` 不再出现在新壳菜单、路由、页面组件映射、DetailPanel 分支和样式导入中。
- 运营中心相关前端模块文件与测试断言已同步清理。
- 迁移矩阵、roadmap 和已有运营中心 plan/spec 已收口到新的产品范围。
- 前端 typecheck、build 与相关 pytest 通过。
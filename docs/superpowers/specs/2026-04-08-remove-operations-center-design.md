# 运营中心模块下线设计

## Summary
- 本设计落实 `operations-center` 在新壳产品面的完整下线：从菜单、路由、页面挂载、右栏详情状态、样式接线、测试断言和迁移文档中移除。
- 本轮只处理新壳与当前迁移口径，不回滚或删除旧壳 `desktop_app/` 中的历史参考实现。

## Decisions
1. `apps/desktop/src/app/router/routeManifest.ts`
   - 删除 `operations-center` manifest 项。
   - 删除 `RoutePageKind` 中未再使用的 `operationsCenter`。
2. `apps/desktop/src/app/router/routes.ts`
   - 删除 `OperationsCenterPage` 导入。
   - 删除 `pageComponents.operationsCenter`。
3. `apps/desktop/src/pages/operations/OperationsCenterPage.vue`
   - 删除文件。
4. `apps/desktop/src/modules/operations/`
   - 删除 `useOperationsCenterData.ts`。
   - 删除 `operationsCenter.helpers.ts`。
   - 删除 `operationsCenter.types.ts`。
5. `apps/desktop/src/layouts/DetailPanel.vue`
   - 删除 `isOperationsRoute`、`operationsDetailKind` 和运营中心详情渲染分支。
6. `apps/desktop/src/modules/shell/useShellStore.ts`
   - 删除 `OperationsDetailKind`、`OperationsDetailItem`、`OperationsAdviceItem`、`OperationsDetailState`。
   - 删除 `createDefaultOperationsDetailState()`。
   - 删除 `operationsDetailState` ref。
   - 删除 `setOperationsDetailState()` / `resetOperationsDetailState()`。
   - 删除最终 return 中对应暴露项。
7. `apps/desktop/src/styles/operations-center.css`
   - 删除文件。
8. `apps/desktop/src/main.ts`
   - 删除 `./styles/operations-center.css` 导入。

## Documentation Strategy
1. `docs/migration/page-matrix.md`
   - 顶层页面数量维持 `35` 不变，因为这是旧壳保留页面基线，不是新壳当前已挂载页数。
   - 新壳左侧菜单由 `35` 收缩为 `34`。
   - 已接入真实新链路页面由 `15` 收缩为 `14`。
   - 删除迁移矩阵中 `operations-center` 这一行。
   - 更新“下一批优先页”与结论描述，不再把运营中心当成已迁移项。
2. `docs/migration/current-status-and-roadmap.md`
   - 从“已进入新链路的页面”清单中删除运营中心。
   - 将“新壳左侧菜单与路由骨架已收口到当前保留的 35 个页面”改为更准确的“旧壳保留页面 35 个，新壳当前菜单挂载 34 个”。
   - 删除“从 operations-center 开始按菜单顺序迁移”的表述，改为从当前剩余第一优先页继续。
3. `docs/UI-DESIGN-PRD.md`
   - 仅做最小同步：从 Sidebar 导航树中移除“运营中心”，避免当前设计文档继续把它列为现行入口。
4. 既有运营中心迁移文档
   - `docs/superpowers/plans/2026-04-08-operations-center-vertical-slice.md`
   - `docs/superpowers/specs/2026-04-08-operations-center-vertical-slice-design.md`
   - 在文档顶部追加“已下线/不再执行”的标记，保留历史上下文，但明确它们不再是有效实施目标。
5. 关联计划文档
   - `docs/superpowers/plans/2026-04-08-scheduled-publish-vertical-slice.md`
   - 将“已完成的 operations-center、device-management 页面拆分方式”改为不引用运营中心。

## Test Strategy
1. `tests/test_desktop_frontend_routes.py`
   - 删除 `OPERATIONS_PAGE_VUE` 常量。
   - 删除 `test_operations_center_page_and_detail_panel_branch_exist`。
   - 保留其他已迁移页面断言不变。
   - `route_count == 35` 继续保持，因为其断言的是 legacyRouteKey 基线数量，而不是当前已挂载页面数量。
2. `tests/test_page_runtime_data.py`
   - 从 `DESKTOP_APP_MODULES` 中删除 `useOperationsCenterData.ts`。
   - 删除 `test_operations_center_module_uses_runtime_data_and_no_frozen_demo_copy`。
   - 保留其余 runtime 数据断言不变。

## Validation Strategy
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## Notes
- `apps/desktop/dist/**` 为构建产物，不手工编辑；通过最终 `npm run build` 自动刷新。
- `desktop_app/assets/js/routes.js`、`page-loaders.js`、旧壳 CSS 和模板保持不动，继续作为历史参考。
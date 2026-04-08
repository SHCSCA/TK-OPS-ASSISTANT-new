# 暂不需要模块裁剪计划

## Summary
- 目标：从新单壳桌面中移除 9 个当前明确不需要的模块入口，避免继续占用菜单、迁移统计、测试与文档注意力。
- 模块范围：`order-management`、`service-center`、`refund-processing`、`task-hall`、`task-scheduler`、`auto-like`、`auto-comment`、`auto-message`、`auto-reply`。
- 本计划先定义裁剪影响面与执行边界；经你审批后，再补对应 spec，然后进入实现。

## Goals
1. 将上述 9 个模块从新壳左侧菜单、路由清单与迁移统计中移除。
2. 删除这些模块对应的前端页面挂载、无效占位承接和关联前端契约测试。
3. 同步更新迁移矩阵、阶段描述与相关设计/计划文档，确保当前产品口径一致。
4. 对 `task-scheduler` 单独处理，避免把“删除页面模块”和“删除 runtime scheduler 协议”混为一谈。

## Scope
### In Scope
- `apps/desktop/src/app/router/routeManifest.ts`
  - 删除 9 个模块的 manifest 条目。
  - 同步修正总路由数、导航顺序与下一优先项。
- `apps/desktop/src/app/router/routes.ts`
  - 若删除 `task-scheduler`，移除 `SchedulerPage` 导入和 `pageComponents.scheduler` 映射。
- `apps/desktop/src/pages/scheduler/SchedulerPage.vue`
  - 若该页不再被任何入口引用，则一并删除。
- `apps/desktop/src/modules/scheduler/useSchedulerData.ts`
  - 若仅被调度页面使用，则一并删除。
- 与上述模块直接绑定的前端测试、迁移矩阵和计划/spec 文档引用。

### Out of Scope
- 默认不删除 Python runtime 的 scheduler HTTP 接口、类型定义和后端路由注册。
- 默认不删除 legacy 旧壳中的对应 route/page-loader 历史代码。
- 不顺带裁剪其余未点名 placeholder 页面。
- 不借机重排剩余菜单的信息架构，只做最小必要收缩。

## Assumptions
1. “全部删除”当前先按新壳产品面收口处理，即：从当前桌面产品入口、页面、文档、测试口径中消失。
2. `task-scheduler` 的 runtime API 先保留，原因是它已经进入后端契约层，贸然硬删会扩大为跨端协议变更；若你确认要做彻底删除，再单开下一轮计划处理后端与 legacy 清理。

## Module Breakdown
### A 类：纯占位模块，可直接从 manifest 与文档测试中移除
- `order-management`
- `service-center`
- `refund-processing`
- `task-hall`
- `auto-like`
- `auto-comment`
- `auto-message`
- `auto-reply`

### B 类：已实现页面模块，需回收页面挂载与关联前端代码
- `task-scheduler`

## Baseline
- 新壳真实菜单来源：`apps/desktop/src/app/router/routeManifest.ts`
- 新壳路由组装：`apps/desktop/src/app/router/routes.ts`
- 迁移进度统计：`apps/desktop/src/app/router/migrationProgress.ts`
- 调度页面入口：`apps/desktop/src/pages/scheduler/SchedulerPage.vue`
- 调度页面数据层：`apps/desktop/src/modules/scheduler/useSchedulerData.ts`
- 迁移矩阵文档：`docs/migration/page-matrix.md`
- 当前前端契约测试：
  - `tests/test_desktop_frontend_routes.py`
  - `tests/test_scheduler_runtime_contract.py`
  - `tests/test_page_loader_task_ops_split.py`
  - `tests/test_page_runtime_data.py`

## File Map
### 必改文件
- `apps/desktop/src/app/router/routeManifest.ts`
- `apps/desktop/src/app/router/routes.ts`
- `docs/migration/page-matrix.md`
- `tests/test_desktop_frontend_routes.py`

### 条件删除/修改文件
- `apps/desktop/src/pages/scheduler/SchedulerPage.vue`
- `apps/desktop/src/modules/scheduler/useSchedulerData.ts`
- `tests/test_scheduler_runtime_contract.py`
- `tests/test_page_loader_task_ops_split.py`
- `tests/test_page_runtime_data.py`
- `docs/superpowers/plans/2026-04-08-operations-center-vertical-slice.md`
- `docs/superpowers/specs/2026-04-08-operations-center-vertical-slice-design.md`

## Implementation Phases
### Phase 1: 入口裁剪与统计收缩
- 从 `routeManifest.ts` 删除 9 个模块。
- 校正菜单顺序、总路由数与迁移统计基线。
- 保证 Sidebar、placeholder 页面、shell 搜索结果等均自动收敛到新清单。

### Phase 2: 调度页面前端回收
- 从 `routes.ts` 删除 `SchedulerPage` 挂载。
- 删除或回收 `SchedulerPage.vue` 与 `useSchedulerData.ts`。
- 确认没有其他前端模块再引用 scheduler 页面层代码。

### Phase 3: 测试与文档同步
- 更新 manifest 数量断言、菜单存在性断言、迁移矩阵、优先级说明。
- 删除仅为这 9 个模块存在的前端测试断言。
- 修正运营中心 plan/spec 中关于 `order-management` / `service-center` / `refund-processing` 承接位的表述，避免文档继续要求保留已删除模块。

### Phase 4: 验证
- 跑与路由、页面契约、迁移矩阵相关的 pytest。
- 跑前端 `typecheck` 与 `build`，确保删减后没有悬空导入或死引用。

## Validation
### 自动化
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_loader_task_ops_split.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_scheduler_runtime_contract.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工验收
- 左侧菜单中不再出现这 9 个模块。
- 搜索/路由中不再能打开这些页面。
- 迁移统计从旧的 44 页基线收缩到新的有效基线。
- `task-scheduler` 页面代码不再被前端引用。

## Risks
1. `task-scheduler` 已经是 implemented 页面，删它会让“已迁移页数”下降。
   - 应对：显式接受这是产品范围裁剪，不是迁移回退失败。
2. 现有测试与文档大量写死了 44 页基线。
   - 应对：实现时统一更新断言与文档口径，避免只删代码不改基线。
3. `task-scheduler` 的 runtime API 仍会留在前后端代码里。
   - 应对：本轮先接受“后端保留、前端入口删除”的最小安全方案；若需要彻底下线，再开下一轮跨端清理。

## Rollback
- 若删除后发现仍有关键入口依赖 scheduler 页面，可先恢复 `task-scheduler` 单页路由，不恢复其余 8 个纯占位模块。
- 所有裁剪以 manifest 和前端页面层为主，便于局部回滚。

## Exit Criteria
- 9 个指定模块不再出现在新壳菜单、路由和迁移矩阵中。
- `task-scheduler` 前端页面及其数据层不再被引用。
- 相关测试与文档已同步到新的产品范围口径。
- 前端 typecheck、build 和相关 pytest 通过。
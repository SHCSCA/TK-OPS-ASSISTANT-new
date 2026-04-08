# 暂不需要模块裁剪设计

## Summary
- 本设计落实 9 个暂不需要模块的前端下线方案：从新壳菜单、路由、迁移矩阵、页面挂载与直接相关测试中移除。
- 本轮仅处理新壳产品面与文档口径，不继续扩大到 Python runtime scheduler 协议和 legacy 旧壳参考代码。

## Decisions
1. `order-management`、`service-center`、`refund-processing`、`task-hall`、`auto-like`、`auto-comment`、`auto-message`、`auto-reply`
   - 直接从 `routeManifest.ts` 删除。
   - 不保留空占位条目。
2. `task-scheduler`
   - 从 `routeManifest.ts` 与 `routes.ts` 删除前端入口。
   - 删除 `SchedulerPage.vue` 与 `useSchedulerData.ts`。
   - 暂不删除 `runtimeApi` 中的 scheduler 方法和后端 `/scheduler` 路由。
3. 文档与测试
   - 当前产品状态文档统一改为 35 个顶层页面基线。
   - 已迁移页面口径改为 10 个。
   - 删除或改写仅针对已下线模块入口的前端断言。

## File Mapping
### Route and Page Removal
- `apps/desktop/src/app/router/routeManifest.ts`
  - 删除 9 个 manifest 项。
  - 移除 `RoutePageKind` 中未再使用的 `scheduler`。
- `apps/desktop/src/app/router/routes.ts`
  - 删除 `SchedulerPage` 导入。
  - 删除 `pageComponents.scheduler`。
- `apps/desktop/src/pages/scheduler/SchedulerPage.vue`
  - 删除文件。
- `apps/desktop/src/modules/scheduler/useSchedulerData.ts`
  - 删除文件。

### Test Updates
- `tests/test_desktop_frontend_routes.py`
  - 路由总数由 44 改为 35。
  - 移除 `task-scheduler` 路径存在性断言。
- `tests/test_scheduler_runtime_contract.py`
  - 删除文件，避免继续把已下线页面当作前端契约。

### Docs Updates
- `docs/migration/page-matrix.md`
  - 总页面数改为 35。
  - 已迁移页改为 10。
  - 删除 9 个模块对应行。
  - 更新下一批优先页表述。
- `docs/migration/current-status-and-roadmap.md`
  - 更新已接入页面清单与基线数量。
- `docs/superpowers/plans/2026-04-08-operations-center-vertical-slice.md`
  - 删除要求保留 `order-management / service-center / refund-processing` 承接位的描述。
- `docs/superpowers/specs/2026-04-08-operations-center-vertical-slice-design.md`
  - 删除跳转区中已下线模块的设计要求。

## Validation Strategy
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## Notes
- `tests/test_page_loader_task_ops_split.py` 与 `tests/test_page_runtime_data.py` 继续针对 legacy 参考壳代码，不在本轮改动范围内。
- 若后续确认 scheduler runtime 也要彻底下线，应新开跨端清理任务，覆盖 `runtimeApi.ts`、`apps/py-runtime`、相关测试与脚本。
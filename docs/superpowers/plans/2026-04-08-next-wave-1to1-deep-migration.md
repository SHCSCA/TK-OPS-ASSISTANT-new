# 下一批页面 1:1 深度迁移总计划

## Summary
- 目标：把 `data-collector`、`creative-workshop`、`ai-content-factory`、`video-editor` 纳入同一批次迁移计划，统一按旧壳做 1:1 深度迁移与代码转换。
- 原则：后续迁移不再接受“只保留大意”的轻量改写，每个页面都必须完整转移旧壳结构、数据装配、事件关系、文案语义、样式约束和测试锁定。
- 流程：本计划确认后，按菜单顺序逐页补独立 spec，再分阶段实现。

## Global Rules
1. 每个页面必须以旧壳源文件为基线，先冻结 route、loader、factory、template、CSS、数据装配链，再写 spec。
2. 迁移必须覆盖：页面结构、运行时数据、交互动作、右栏/详情关系、样式约束、测试契约。
3. 禁止只做页面壳子；禁止把旧壳多文件关系压缩成单一“新设计”；禁止引入硬编码业务数字冒充真实数据。
4. 任何页面进入 `implemented` 之前，必须完成对应测试、typecheck、build 验证。
5. 当旧壳页面本质上是工厂模式或共享模式时，新壳允许做宿主适配，但不允许改业务语义与区块关系。

## Batch Scope

### 第一页：data-collector
- 目标：1:1 迁移数据采集助手旧壳页面。
- 重点：采集任务列表、数据源、代理/补偿链路、状态视图、主次动作语义。
- 输出：独立 plan/spec/implementation/test。

### 第二页：creative-workshop
- 目标：1:1 迁移创意工坊旧壳页面。
- 重点：创意组合区、脚本/镜头/素材编排区、试验流程与结果视图。
- 输出：独立 plan/spec/implementation/test。

### 第三页：ai-content-factory
- 目标：1:1 迁移 AI 内容工厂旧壳页面。
- 重点：标题/脚本/文案/素材组合产线、任务链与结果状态。
- 输出：独立 plan/spec/implementation/test。

### 第四页：video-editor
- 目标：1:1 迁移视频编辑旧壳页面。
- 重点：时间轴、片段、字幕、导出流程、序列/素材联动。
- 输出：独立 plan/spec/implementation/test。

## File Baseline Strategy

### 每页固定先读
- `desktop_app/assets/js/routes.js`
- 对应 `page-loaders` 或 `factories` 文件
- `desktop_app/assets/app_shell.html`
- `desktop_app/assets/css/components.css`
- 对应页面 CSS 文件

### 新壳固定落点
- `apps/desktop/src/app/router/routeManifest.ts`
- `apps/desktop/src/app/router/routes.ts`
- `apps/desktop/src/pages/*`
- `apps/desktop/src/modules/*`
- `apps/desktop/src/styles/*`
- `apps/desktop/src/layouts/DetailPanel.vue`
- `apps/desktop/src/modules/shell/useShellStore.ts`
- `tests/test_desktop_frontend_routes.py`
- `tests/test_page_runtime_data.py`
- 与页面相关的审计/交互测试

## Execution Order
1. `data-collector`
2. `creative-workshop`
3. `ai-content-factory`
4. `video-editor`

说明：必须按菜单顺序推进，不再跳页，不把后页先行实现成“看起来更容易”的轻量版本。

## Validation Baseline
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- 每页额外补一组页面级测试
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## Risks
1. 后续页面可能继续沿用旧壳工厂化模式，源文件分散。
   - 应对：每页 spec 必须提供旧壳到新壳的逐文件映射表。
2. 新壳当前已经有统一 DetailPanel 和路由壳层，容易与旧壳 detail host 机制不完全一致。
   - 应对：允许宿主适配，但必须保持信息架构和动作语义一致。
3. 如果跳过 plan/spec 直接编码，极易再次出现“半迁移”或“换皮页”。
   - 应对：继续强制 superpowers 工作流，不批准 spec 前不进入实现。

## Exit Criteria
- 下一批页面全部明确进入 1:1 深迁流水线。
- 每一页都有独立 plan/spec，不再使用“占位页补一点交互”的过渡方式。
- 全局迁移文档明确记录：后续迁移统一按旧壳做深度代码转换。
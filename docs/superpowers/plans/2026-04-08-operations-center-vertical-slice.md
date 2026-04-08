# 运营中心旧壳 1:1 全量复刻迁移计划

> 已废弃：2026-04-08 起该模块不再保留在新壳产品范围内，后续实施以 `2026-04-08-remove-operations-center.md` 为准。

## Summary
- 目标：将 `operations-center` 从 placeholder 升级为对旧壳运营中心的 1:1 复刻迁移，完整转移旧壳的页面结构、样式层级、交互约束、事件关系、数据派生和接口调用链路。
- 范围：以旧壳 `makeListManagementRoute({ mode: 'operations' })` 为主基线，不做“只保留大意”的抽象化改写；需要尽可能维持信息密度、区块关系、动作语义和运行时行为一致。
- 流程：本文件审批后，补 `docs/superpowers/specs/2026-04-08-operations-center-vertical-slice-design.md`，再进入实现。

## Goals
1. 把 `operations-center` 从占位页切为真实页面，并纳入迁移进度统计。
2. 1:1 转移旧壳的主区、右侧详情、状态条语义、按钮文案、列表关系与选中态行为。
3. 1:1 转移旧壳依赖的数据装配方式，包括 `tasks/accounts/assets/providers` 的聚合与派生逻辑。
4. 1:1 转移动作链路，包括刷新、创建排期草稿、列表联动、详情更新和路由跳转语义。
5. 样式层面尽量沿用旧壳选择器、栅格关系和视觉约束，避免“新设计替代旧设计”。

## Scope
### In Scope
- `apps/desktop` 新增 `OperationsCenterPage.vue` 与对应 view-model/composable。
- `routeManifest.ts` / `routes.ts` 把 `operations-center` 切为真实 `pageKind` 和 `implemented`。
- 旧壳以下能力的等价迁移：
  - 路由元数据：标题、eyebrow、description、primary/secondary actions、list/detail/sidebar/status 文案语义。
  - 页面结构：`list-management-shell`、metric cards、`workbench-list`、右栏 detail cards、状态摘要区。
  - 数据装配：`_loadListManagementPage`、`_listManagementDraft`、`_listManagementRecords`、相关 metrics/detail 派生。
  - 交互关系：主按钮创建任务草稿、次按钮刷新、列表项选中态与详情联动、跨页跳转入口。
  - 样式约束：旧壳 components/pages-ops 中与 list-management、operations-grid、workbench-list 相关样式块。
- 复用现有 runtime 接口，不得用 mock/stub/演示数字替代旧壳真实派生逻辑。
- 补必要测试：路由存在性、页面关键区块、非 placeholder、真实数据驱动约束、旧壳关键 class/section 锁定。

### Out of Scope
- 不把运营中心改造成新的信息架构或新视觉语言。
- 不随意发明旧壳中不存在的业务指标或动作。
- 不改账号、设备、素材、任务现有底层协议，除非为 1:1 对齐旧壳行为做最小适配。

## Baseline
- PRD 对运营中心定义见 `docs/PRD.md`：定位为运营域 hub 页，核心模块为经营摘要卡、待办列表、异常区、客户热点区、跳转区。
- 旧壳主基线：
  - `desktop_app/assets/js/routes.js` 中 `makeListManagementRoute({ mode: 'operations' })`
  - `desktop_app/assets/js/page-loaders.js` 中 `_loadListManagementPage` / `_bindListManagementActions` / `_listManagementDraft` / `_listManagementRecords` / metrics/detail 渲染链路
  - `desktop_app/assets/js/factories/operations.js` 与 `desktop_app/assets/app_shell.js` 中 `list-management-shell` 模板骨架
  - `desktop_app/assets/css/components.css` 与 `desktop_app/assets/css/pages-ops.css` 中 list-management / operations-grid / workbench-list 等样式块
  - `desktop_app/assets/app_shell.html` 中导航入口与宿主挂载关系
- 新壳迁移顺序依据：`docs/migration/current-status-and-roadmap.md` 明确要求从 `operations-center` 开始按菜单顺序逐页迁移。

## File Map
### 前端页面与状态
- `apps/desktop/src/app/router/routeManifest.ts`
- `apps/desktop/src/app/router/routes.ts`
- `apps/desktop/src/pages/operations/OperationsCenterPage.vue`（新）
- `apps/desktop/src/modules/operations/useOperationsCenterData.ts`（新）
- `apps/desktop/src/styles/main.css` 或独立 `operations-center.css`（spec 中固定最终承载方式）
- `apps/desktop/src/layouts/DetailPanel.vue` / `useShellStore.ts`（若 1:1 复刻要求运营中心占用统一右栏）

### 复用依赖
- `apps/desktop/src/modules/runtime/runtimeApi.ts`
- `apps/desktop/src/modules/runtime/types.ts`
- 已有 `accounts` / `assets` / `tasks` / `providers` 模块与 shell 状态

### 旧壳来源文件（1:1 对照清单）
- `desktop_app/assets/js/routes.js`
- `desktop_app/assets/js/page-loaders.js`
- `desktop_app/assets/js/factories/operations.js`
- `desktop_app/assets/app_shell.js`
- `desktop_app/assets/css/components.css`
- `desktop_app/assets/css/pages-ops.css`
- `desktop_app/assets/app_shell.html`

### 测试
- `tests/test_desktop_frontend_routes.py`
- `tests/test_page_runtime_data.py`
- `tests/test_page_interaction_audit.py`
- 如需新增更细颗粒测试，再在 spec 中定具体文件

## Implementation Phases
### Phase 1: 旧壳源抽取与契约冻结
- 逐块锁定旧壳运营中心的模板、选择器、数据来源、动作链和状态语义。
- 明确哪些 class、section、交互属于必须 1:1 保留，哪些仅允许做宿主适配。

### Phase 2: 页面骨架 1:1 迁移
- 新增 `operations-center` 页面组件和 `pageKind`。
- 把旧壳 `list-management-shell`、header、metrics、`workbench-list`、detail/card/status 区按新壳结构等价迁移。
- 如旧壳右栏依赖 detailHost，则在新壳中明确映射到统一 detail panel 或页面内右栏区域，保持行为一致。

### Phase 3: 数据链与动作链 1:1 迁移
- 复用现有 `runtimeApi`：账户、任务、素材、提供商数据。
- 在 `useOperationsCenterData` 中按旧壳逻辑复刻：记录生成、指标派生、详情摘要、状态条、草稿创建数据。
- 主按钮、刷新按钮、列表选中、跳转入口与旧壳行为保持一致。

### Phase 4: 样式与约束迁移
- 迁移旧壳 list-management / operations-grid / workbench-list 相关样式和响应式约束。
- 只做宿主适配，不主动替换成“更现代”的新布局。

### Phase 5: 验证与回归
- 补前端路由/页面审计测试，锁定旧壳关键结构和类名。
- 执行 pytest、typecheck、build，并对照旧壳做手工验收。

## Validation
### 自动化
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_runtime_data.py -v`
- `venv\Scripts\python.exe -m pytest tests/test_page_interaction_audit.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工验收
- `operations-center` 不再显示 placeholder 文案。
- 页面主区、右栏/详情区、状态条、主次按钮、列表关系与旧壳视觉和语义一致。
- 页面所有摘要和列表都来自旧壳同源的真实聚合结果，而不是写死数字。
- 跨页按钮无死链，能跳转到既有真实页或占位页，且命名语义与旧壳一致。
- 对照旧壳 `operations-center`，信息密度、选中态、布局层次和关键类名不发生结构性漂移。

## Risks
1. 旧壳运营中心是工厂化页面，部分结构分散在 routes/factory/page-loader/CSS 多处。
   - 应对：spec 必须给出逐文件映射表，防止只迁一半。
2. 新壳统一路由/壳层与旧壳 detailHost 机制不完全相同。
   - 应对：允许做最小宿主适配，但不允许改变业务区块关系和动作语义。
3. 现有 runtime 没有专门的运营摘要 endpoint。
   - 应对：先复刻旧壳的前端聚合链，只有旧壳无法等价复刻时才定义最小新增协议。
4. 1:1 要求下容易被“顺手优化”带偏。
   - 应对：spec 中显式标注禁止重设计、禁止改文案、禁止改信息架构。

## Rollback
- 若本轮实现不稳定，可把 `operations-center` 的 `pageKind` 和 `migrationStatus` 回退到 placeholder，并保留新建页面代码不挂路由。
- 所有新能力以新增文件和局部路由切换为主，避免影响已完成的账号、设备、素材和任务页面。

## Exit Criteria
- `operations-center` 进入 implemented 列表。
- 新页面能对照旧壳实现 1:1 的结构、样式关系、动作链和接口调用语义。
- 旧壳关键模板/样式/派生逻辑均有新壳映射，不存在“只迁页面没迁关系”的半迁移状态。
- 自动化检查通过，且没有引入 placeholder 回退或构建告警。
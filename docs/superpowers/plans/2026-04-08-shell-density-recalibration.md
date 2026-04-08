# 全局壳层密度与字号回调计划

## Summary
- 目标：解决当前新壳“整个项目字体以及样式明显偏大”的全局问题，把桌面端的字号、间距、卡片尺寸和壳层宽高回调到更接近旧壳的真实信息密度。
- 核心判断：问题不是单页样式失控，而是三层全局基线叠加导致的整体放大：旧壳设计令牌本身偏大、新壳 `main.css` 再定义一套偏大的标题/统计字号、壳层 `shellScale` 在 full 模式下没有主动收缩。
- 流程：本计划确认后，补 `docs/superpowers/specs/2026-04-08-shell-density-recalibration-design.md`，再进入实现。

## Goals
1. 收缩桌面壳层的全局尺寸基线，包括侧栏、详情栏、标题栏、状态栏、页面 gutter、面板 padding 和卡片间距。
2. 收缩新壳统一字号体系，重点处理 `page-header h1`、`stat-card__value`、正文、辅助文案与导航字体。
3. 调整 `shellScale` 策略，避免宽窗下继续按 1 倍放大，缩短“看起来像浏览器网页而不是桌面工作台”的体感偏差。
4. 保持现有页面结构、旧壳语义类名和运行时数据链路不变，不把本轮演变成新的视觉重设计。
5. 为后续页面迁移建立一套更紧凑的全局基线，避免每个新页面再局部修字号。

## Problem Evidence

### 1. 旧壳设计令牌本身偏大
- `desktop_app/assets/css/variables.css`
  - `--sidebar-width: 292px`
  - `--detail-width: 320px`
  - `--titlebar-height: 72px`
  - `--statusbar-height: 46px`
  - `--page-gutter: 28px`
  - `--page-section-gap: 22px`
  - `--panel-padding: 20px`
  - `--content-max-width: 1480px`

### 2. 新壳又叠加了一套偏大的字号体系
- `apps/desktop/src/styles/main.css`
  - `--shell-font-body: 13px`
  - `--shell-font-subtle: 12px`
  - `--shell-font-h1: 32px`
  - `--shell-font-h1-compact: 20px`
  - `--shell-font-stat: 30px`
  - `--shell-font-stat-compact: 22px`
- 同文件还把 `.resource-header h2` 固定到 `30px`，并把 `page-header h1 / stat-card__value` 再按 `--shell-scale` 放大。

### 3. 壳层缩放策略只会缩小，不会主动回调到更紧凑基线
- `apps/desktop/src/modules/shell/useShellStore.ts`
  - `SHELL_SCALE_BASE_WIDTH = 1440`
  - `SHELL_SCALE_MIN = 0.82`
  - `resolveShellScale(...) = clamp(layoutViewportWidth / 1440, 0.82, 1)`
- 结论：在常见桌面宽度下，full 模式会直接贴到 `1`，没有任何“桌面工作台应比浏览器联调页更紧凑”的主动收缩策略。

### 4. 当前用户体感与截图一致
- 现象包括：
  - 首屏品牌区、主标题和统计数字体感过大。
  - 左侧导航占宽过多，主内容区有效信息密度偏低。
  - 卡片内留白、按钮块和快捷入口显得偏松，和“运营工作台”语义不匹配。

## Scope

### In Scope
- `desktop_app/assets/css/variables.css`
  - 回调全局尺寸令牌。
- `apps/desktop/src/styles/main.css`
  - 回调统一字号、页面标题、统计数字、常用间距与壳层缩放后的文本尺寸。
- `apps/desktop/src/modules/shell/useShellStore.ts`
  - 回调 `shellScale` 的 base/min/max 或计算策略。
- `apps/desktop/src/layouts/AppShell.vue`
  - 如有必要，只做最小变量接线，不改布局结构。
- 与壳层相关的静态契约测试：
  - `tests/test_desktop_frontend_routes.py`
  - 如已有样式基线测试，也纳入更新范围。

### Out of Scope
- 不在本轮逐页重写局部页面 CSS。
- 不修改颜色体系、主题方向、组件信息架构和页面结构。
- 不把本轮扩展成“重做 TK-OPS 视觉系统”。
- 不顺带修改旧壳 `desktop_app/` 的页面模板与业务逻辑。

## Baseline Files
- `desktop_app/assets/css/variables.css`
- `apps/desktop/src/styles/main.css`
- `apps/desktop/src/modules/shell/useShellStore.ts`
- `apps/desktop/src/layouts/AppShell.vue`
- 参考文档：
  - `docs/superpowers/specs/2026-04-03-旧壳字号回归与概览看板增强设计.md`
  - `docs/superpowers/specs/2026-04-02-desktop-shell-and-style-realignment-design.md`

## File Map

### 必改文件
- `desktop_app/assets/css/variables.css`
- `apps/desktop/src/styles/main.css`
- `apps/desktop/src/modules/shell/useShellStore.ts`

### 视实现决定是否需要改动
- `apps/desktop/src/layouts/AppShell.vue`
- `tests/test_desktop_frontend_routes.py`
- 可能存在的前端样式基线测试文件

### 计划产物
- `docs/superpowers/specs/2026-04-08-shell-density-recalibration-design.md`

## Implementation Phases

### Phase 1: 冻结全局尺寸根因与目标区间
- 明确当前全局尺寸控制点：壳层令牌、统一字号、缩放策略。
- 对照旧壳当前视觉和桌面工作台目标，给出一组新的目标区间：
  - sidebar/detail/titlebar/statusbar 宽高
  - page gutter / panel padding / card gap
  - body / subtle / h1 / stat 字号
  - shellScale base/min/max

### Phase 2: 回调全局令牌与统一字号
- 先调整 `variables.css` 中的壳层尺寸令牌。
- 再调整 `main.css` 中统一字号与标题/统计数字的尺寸。
- 要求所有页面自动随全局基线回调，而不是靠页面局部覆盖兜底。

### Phase 3: 收紧壳层缩放策略
- 回调 `resolveShellScale(...)`，让 full 模式默认也带有轻量收缩。
- 保证窄窗仍可读，不因回调导致 960 以下再次挤爆。

### Phase 4: 回归与样式例外检查
- 重点检查：
  - dashboard
  - account
  - device-management
  - asset-center
  - scheduled-publish
  - data-collector
  - creative-workshop
  - ai-content-factory
  - video-editor
- 如果发现个别页面仍显著偏大，只允许做最小例外修正，并记录到 spec，不允许重新铺开大规模局部重写。

### Phase 5: 验证
- 跑前端 typecheck 与 build。
- 更新受影响的静态测试断言。
- 手工按多宽度回归：`1440 / 1280 / 1180 / 960`。

## Validation

### 自动化
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工验收
- 主标题、统计数字和导航字体明显收缩，不再一眼“显大”。
- 左侧导航、顶部栏和右侧详情占宽收紧，主内容有效区域变大。
- 卡片留白与按钮块更贴近桌面工作台而不是网页宣传页。
- 窄窗下没有因为收缩导致新的换行爆炸、按钮拥挤或面板重叠。

## Risks
1. 全局收缩会把部分后来新增页面的局部字体也一起缩小，可能暴露局部层级不平衡。
   - 应对：实现后按已迁移页面逐页快速回归，只做最小例外补丁。
2. `shellScale` 收紧过头会影响 960~1180 宽度下的可读性。
   - 应对：spec 中先给目标区间，再通过多宽度手工回归校准。
3. 旧壳变量和新壳 `main.css` 同时收紧时，容易重复缩小。
   - 应对：先在 spec 中拆清“壳层盒模型”和“字体基线”两条链，避免叠加过量。

## Rollback
- 若全局回调后个别页面出现明显可读性回退，可先回退 `shellScale` 调整，仅保留令牌与字号收紧。
- 所有改动集中在全局样式与壳层状态层，便于局部回滚，不影响 runtime 数据链路。

## Exit Criteria
- 全局字体、留白和壳层尺寸明显回调，用户主观体感不再是“整个项目偏大”。
- 不依赖逐页打补丁，已迁移页面大部分能随全局基线自动受益。
- typecheck、build 与相关静态测试通过。
- plan 获批后，可直接进入 shell-density 的独立设计说明与实现阶段。
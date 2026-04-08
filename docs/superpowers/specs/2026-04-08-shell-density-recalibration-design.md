# 全局壳层密度与字号回调设计

## 1. 目标

- 解决当前新壳“整个项目字体以及样式明显偏大”的全局问题。
- 在不改页面结构、不改数据链路、不重做视觉系统的前提下，把桌面端的字号、间距、壳层宽高和卡片留白回调到更接近旧壳工作台的信息密度。
- 通过全局令牌、统一字号和壳层缩放三条链同时收口，让已迁移页面自动受益，避免逐页打补丁。

## 2. 根因拆解

### 2.1 旧壳令牌偏大

当前 `desktop_app/assets/css/variables.css` 里的壳层盒模型偏大：

- `--sidebar-width: 292px`
- `--detail-width: 320px`
- `--titlebar-height: 72px`
- `--statusbar-height: 46px`
- `--page-gutter: 28px`
- `--page-section-gap: 22px`
- `--panel-padding: 20px`
- `--content-max-width: 1480px`

这些值单看并非错误，但与当前新壳页面的较松排版叠加后，会放大“网页化”和“空”感。

### 2.2 新壳统一字号再次放大

`apps/desktop/src/styles/main.css` 里又定义了一套偏大的统一字号：

- `--shell-font-body: 13px`
- `--shell-font-subtle: 12px`
- `--shell-font-h1: 32px`
- `--shell-font-h1-compact: 20px`
- `--shell-font-stat: 30px`
- `--shell-font-stat-compact: 22px`

而且 `resource-header h2` 固定为 `30px`，主标题和统计数字在大多数页面都偏“宣发感”，不够像桌面工作台。

### 2.3 shellScale 只负责防爆，不负责回调密度

`apps/desktop/src/modules/shell/useShellStore.ts` 当前策略：

- `SHELL_SCALE_BASE_WIDTH = 1440`
- `SHELL_SCALE_MIN = 0.82`
- `resolveShellScale = clamp(width / 1440, 0.82, 1)`

这意味着：

- 窄窗只会被动缩小
- 常见桌面宽度下很快贴到 `1`
- full 模式没有主动收紧

所以用户看到的是“全站默认就偏大”，而不是“只有窄窗时才失真”。

## 3. 设计原则

1. 只回调密度，不改信息架构。
2. 优先改全局令牌和统一字号，不做逐页大修。
3. 壳层缩放从“防溢出”升级为“桌面密度校准”。
4. 已迁移页面如有局部失衡，只允许做最小例外收口。

## 4. 目标值

### 4.1 壳层令牌

修改 `desktop_app/assets/css/variables.css`：

- `--sidebar-width: 292px -> 272px`
- `--detail-width: 320px -> 296px`
- `--titlebar-height: 72px -> 64px`
- `--statusbar-height: 46px -> 40px`
- `--page-gutter: 28px -> 22px`
- `--page-section-gap: 22px -> 18px`
- `--panel-padding: 20px -> 16px`
- `--content-max-width: 1480px -> 1400px`
- `--card-gap: 16px -> 14px`
- `--control-height-md: 40px -> 38px`

### 4.2 统一字号

修改 `apps/desktop/src/styles/main.css`：

- `--shell-font-body: 13px -> 12px`
- `--shell-font-subtle: 12px -> 11px`
- `--shell-font-h1: 32px -> 28px`
- `--shell-font-h1-compact: 20px -> 18px`
- `--shell-font-stat: 30px -> 26px`
- `--shell-font-stat-compact: 22px -> 20px`
- `resource-header h2: 30px -> 26px`

同时把 `.shell-canvas` 中基于 `--shell-scale` 的固定像素同步回调：

- `12 -> 11`
- `13 -> 12`
- `32 -> 28`
- `30 -> 26`
- compact `20 -> 18`
- compact stat `22 -> 20`

### 4.3 壳层缩放策略

修改 `apps/desktop/src/modules/shell/useShellStore.ts`：

- `SHELL_SCALE_BASE_WIDTH: 1440 -> 1500`
- `SHELL_SCALE_MIN: 0.82 -> 0.85`
- 新增 `SHELL_SCALE_MAX = 0.96`
- `resolveShellScale = clamp(width / 1500, 0.85, 0.96)`

这组值的目标是：

- full 模式默认也轻量收缩，不再贴满 1 倍
- 1280 左右宽度快速回落到更紧凑的密度
- 窄窗不低于 0.85，避免因为过度压缩产生新的可读性问题

## 5. 预期效果

### 5.1 壳层

- 左侧栏、详情栏和顶部栏更紧凑
- 主内容区有效宽度变大
- 侧栏不再一眼显得“吃宽”

### 5.2 文本层级

- 页面主标题不再过于夸张
- 统计数字仍保留强调，但不再压倒正文
- 导航、辅助文案和表格文字整体更接近旧壳工作台密度

### 5.3 页面联动收益

以下页面应自动受益，无需大改结构：

- dashboard
- account
- device-management
- asset-center
- scheduled-publish
- data-collector
- creative-workshop
- ai-content-factory
- video-editor

## 6. 文件改动

### 必改文件

- `desktop_app/assets/css/variables.css`
- `apps/desktop/src/styles/main.css`
- `apps/desktop/src/modules/shell/useShellStore.ts`

### 测试

- `tests/test_frontend_style_baseline.py`
  - 增加全局密度令牌与缩放策略的静态回归断言

## 7. 验证策略

### 自动化

- `venv\Scripts\python.exe -m pytest tests/test_frontend_style_baseline.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

### 手工

- 宽度 `1440 / 1280 / 1180 / 960` 回归：
  - 主标题是否明显收缩
  - 统计卡是否仍可读
  - 左侧导航是否更紧凑
  - 页面是否出现新的拥挤和溢出

## 8. 风险控制

1. 若个别页面在回调后显得过紧，优先做最小局部收口，不回退全局基线。
2. 若 `shellScale` 收紧后窄窗反馈变差，可只回调 `SHELL_SCALE_MIN`，不回退字号和令牌。
3. 不新增第二套“dense mode”开关，先把默认密度做对。
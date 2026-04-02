# Desktop Shell 与样式回正执行计划

## 目标

把当前“浏览器开发页 + 新皮肤壳层”纠偏为：

- 默认开发入口回到 `Tauri 桌面壳`
- 浏览器仅保留为辅助调试入口
- 新前端壳层与 Dashboard 首屏回到旧项目视觉语言
- 不再把“联调页”冒充桌面交付态

## 范围

本轮只处理两件核心事情：

1. 开发入口与宿主启动方式
2. 新壳层与 Dashboard 首屏样式回正

不在本轮处理：

- 全量页面的逐页视觉重做
- 旧 `desktop_app` 全部页面模板的逐页 1:1 迁移
- 新旧功能差异的全面收口

## 文件地图

开发入口：

- `scripts/dev.ps1`
- `apps/desktop/package.json`
- `apps/desktop/src-tauri/tauri.conf.json`

桌面壳与样式：

- `apps/desktop/src/main.ts`
- `apps/desktop/src/styles/main.css`
- `apps/desktop/src/layouts/AppShell.vue`
- `apps/desktop/src/layouts/TitleBar.vue`
- `apps/desktop/src/layouts/Sidebar.vue`
- `apps/desktop/src/layouts/PageHost.vue`
- `apps/desktop/src/layouts/DetailPanel.vue`
- `apps/desktop/src/layouts/StatusBar.vue`
- `apps/desktop/src/pages/dashboard/DashboardPage.vue`

旧样式参考：

- `desktop_app/assets/css/variables.css`
- `desktop_app/assets/css/shell.css`
- `desktop_app/assets/css/components.css`
- `desktop_app/assets/app_shell.html`

## 分阶段执行

### 阶段 1：入口回正

- `scripts/dev.ps1` 默认启动 Tauri 桌面宿主
- 保留浏览器调试入口，但明确改成非默认命令
- `tauri.conf.json` 补齐 dev 配置，让宿主真正连到本地 Vite

### 阶段 2：壳层回正

- AppShell 改回旧壳层的布局语义：`title / sidebar / main / detail / status`
- TitleBar、Sidebar、StatusBar、DetailPanel 不再使用当前的简化占位风格
- 主体页面容器类名与结构尽量贴近旧壳 CSS 语义

### 阶段 3：Dashboard 首屏回正

- Dashboard 改成接近旧项目的页面头、统计卡、面板、列表与 detail 语言
- 去掉当前过于简化的“演示页感”
- 保留已接通的新 runtime 数据链路

## 验证方式

按用户要求，本轮只做一轮最终验证：

- `cargo tauri dev` 或等效桌面宿主开发启动验证
- `npm run build`
- `cargo check`
- 关键页面截图/人工确认

中途不做多轮回归测试，只在最后统一验证。

## 边界与回退点

- 若 Tauri 开发链路受 CLI 配置阻塞，优先修入口，不回退到默认浏览器模式
- 若旧 CSS 直接复用冲突过大，优先迁移设计令牌与壳层结构，不强行逐页照搬
- 本轮目标是“方向回正”，不是“一次性完成所有视觉迁移”

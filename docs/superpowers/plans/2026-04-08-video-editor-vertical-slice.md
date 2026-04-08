# 视频编辑垂直切片迁移计划

## Summary
- 目标：将 `video-editor` 从新壳占位路由升级为真实视频编辑页面，并严格按旧壳 `makeVideoEditorRoute()`、`video-editor-main.js`、`video-editor-bindings.js` 的结构与动作做 1:1 深度迁移与代码转换。
- 原则：不能把视频编辑降级成静态示意页，也不能只迁时间线外观；必须同步迁移工程、序列、素材库、时间轴片段、字幕、快照、导出和右栏检查器。
- 范围：本计划覆盖旧壳 route / factory / loader / bindings / state / data / CSS 基线，以及新壳前端、runtime HTTP 契约、DetailPanel、测试与迁移文档闭环。
- 约束：继续遵守单壳路径，`desktop_app/` 只作为行为参考与可复用服务来源，不允许回流为运行入口。

## Legacy Baseline

### 1. Route 基线
- 旧壳入口：`desktop_app/assets/js/routes.js`
- 路由工厂：`desktop_app/assets/js/factories/video-editor.js` 中的 `makeVideoEditorRoute()`。
- 当前新壳状态：`apps/desktop/src/app/router/routeManifest.ts` 里 `video-editor` 仍是 `pageKind: 'placeholder'`。
- 固定语义：
	- 页面名称：`视频编辑`
	- 角色定位：承接创意工作台下发内容后的精剪、字幕校对、时间线检查和终版导出
	- 主动作语义：`发起终版导出`
	- 次动作语义：`切换剪辑序列`
	- 页面目标：围绕当前工程与当前序列完成素材预览、片段裁切、字幕处理、快照恢复和导出闭环

### 2. Factory 基线
- 旧壳入口：`desktop_app/assets/js/factories/video-editor.js`
- 页面不是普通内容工位，而是带节目监视器与时间线的独立编辑器结构。
- 关键结构：
	- `workbench-summary-strip`
	- `content-workbench-shell`
	- `workbench-rail`
	- `workbench-canvas workbench-canvas--video video-editing-studio`
	- `source-browser-shell`
	- `video-preview-shell`
	- `transport-bar`
	- `timeline-board video-timeline-board`
	- `video-inspector-panel`
	- `video-queue-block`
	- `detail-root`
- 关键内容区块：
	- 左侧素材库与素材预览
	- 中部节目监视器、播放条、时间线轨道
	- 右侧检查器、字幕检查、导出队列
	- 详情栏中的当前批次、风险与值班动作

### 3. Loader 基线
- 旧壳入口：`desktop_app/assets/js/page-loaders/video-editor-main.js`
- 页面状态：
	- `selectedProjectId`
	- `selectedSequenceId`
	- `selectedAssetId`
	- `selectedClipId`
	- `selectedSubtitleId`
	- `selectedSnapshotId`
	- `inspectorTab`
	- `playheadMs`
- 真实数据来源：
	- `api.videoProjects.list()` / `api.videoProjects.listVideoProjects()`
	- `api.assets.list()`
	- `api.tasks.list()`
	- `api.videoSequences.list(project.id)`
	- `api.videoClips.list(sequence.id)`
	- `api.videoSubtitles.list(sequence.id)`
	- `api.videoExports.list(project.id)`
	- `api.videoSnapshots.list(project.id)`
- 关键运行逻辑：
	- `runtimeSummaryHandlers['video-editor']`
	- `_renderAssetGrid(...)`
	- `_renderPreview(...)`
	- `_renderTimeline(...)`
	- `_renderOutputs(...)`
	- `handleDataChanged(detail)`
- 结论：新壳不能只展示时间线示意图，必须保留“工程 -> 序列 -> 素材 / 片段 / 字幕 / 导出 / 快照”的真实数据装配。

### 4. 交互与持久化基线
- 旧壳入口：`desktop_app/assets/js/bindings/video-editor-bindings.js`
- 关键动作：
	- `发起终版导出` -> `_runExport('final')`
	- `试看导出` -> `_runExport('preview')`
	- `切换剪辑序列` -> `_switchSequence()`
	- `导入素材` -> 选文件后挂载到当前序列
	- `新增字幕` / `编辑字幕` / `删除字幕`
	- `设入点` / `设出点`
	- `左移片段` / `右移片段` / `删除片段`
	- `保存快照` / `恢复快照`
- 关键行为约束：
	- 动作落真实 `api.video*` 链路，不是 generic toast 或通用 quick task 替代
	- 选中态必须区分素材、时间线片段、字幕三类实体
	- 数据变更通过刷新时间线、输出区和 `handleDataChanged` 回流
- 仓库记忆约束：
	- 当前序列素材库与时间轴片段不能混成同一层语义
	- 删除序列内素材只影响当前序列，不删除全局 `Asset`
	- 导出校验要同时考虑素材库与时间线引用的一致性

### 5. 数据与缓存基线
- 旧壳入口：`desktop_app/assets/js/data.js`
- 已有前端数据封装：
	- `videoProjects`
	- `videoSequences`
	- `videoClips`
	- `videoSubtitles`
	- `videoExports`
	- `videoSnapshots`
- 已有缓存失效链：视频相关写操作会统一失效 `videoProjects:`、`videoSequences:`、`videoClips:`、`videoSubtitles:`、`videoExports:`、`videoSnapshots:` 前缀缓存。
- 结论：新壳 runtime 迁移时必须把这些数据域完整映射到 HTTP API 与前端 store/composable，不能只补单个列表。

### 6. 模型与服务基线
- 旧层已存在可复用模型与服务：
	- `desktop_app/database/models.py`
	- `desktop_app/database/repository.py`
	- `desktop_app/services/video_editing_service.py`
	- `desktop_app/services/video_export_service.py`
	- `desktop_app/ui/bridge.py`
- 已存在的核心实体与方法：
	- `VideoProject`
	- `VideoSequence`
	- `VideoSequenceAsset`
	- `VideoClip`
	- `VideoSubtitle`
	- `VideoExport`
	- `VideoSnapshot`
	- `create_video_project`
	- `list_video_projects`
	- `create_video_sequence`
	- `append_video_clip`
	- `reorder_video_clips`
	- `create_video_subtitle`
	- `createVideoExport` / `runVideoExport`
- 结论：本轮不需要重新发明视频领域模型，应优先复用旧层服务与仓库能力，通过新 runtime HTTP 暴露给 Tauri 前端。

### 7. 样式基线
- 旧壳入口：
	- `desktop_app/assets/css/pages-content.css`
	- `desktop_app/assets/css/interactions.css`
- 关键样式族：
	- `video-editing-studio`
	- `source-browser-*`
	- `video-preview-*`
	- `transport-*`
	- `timeline-*`
	- `video-inspector-*`
	- `video-queue-*`
- 额外约束：节目监视器与素材缩略图区不能复用同一预览容器，新壳要保留独立 `stage/player` 语义，避免本地视频预览再次退化为占位块。

## Runtime Gap Assessment
- 当前新壳 `apps/py-runtime/src/**` 中尚未暴露任何 `videoProjects` / `videoSequences` / `videoClips` / `videoSubtitles` / `videoExports` / `videoSnapshots` 的 HTTP route。
- 当前新壳 `apps/desktop/src/modules/runtime/runtimeApi.ts` 与 `types.ts` 中也没有视频编辑相关 API/type。
- 旧层桥接与仓库能力已经完整存在，因此本轮迁移的真实缺口不在领域模型，而在：
	- runtime HTTP route
	- serializer
	- 前端 runtime API/types
	- 新壳页面与 DetailPanel 接线
- 结论：`video-editor` 的迁移必须同时覆盖前端和 runtime；只做页面壳会再次形成“能看不能剪、能看不能导出”的假迁移。

## New-Shell Scope

### 前端页面与模块
- 新增或修改目标：
	- `apps/desktop/src/pages/content/VideoEditorPage.vue`
	- `apps/desktop/src/modules/content/videoEditor.types.ts`
	- `apps/desktop/src/modules/content/videoEditor.helpers.ts`
	- `apps/desktop/src/modules/content/useVideoEditorData.ts`
	- `apps/desktop/src/styles/video-editor.css`
- 页面必须承载以下新壳语义：
	- 工程与序列切换
	- 素材库网格与当前素材预览
	- 节目监视器 / stage
	- 时间线片段与字幕轨
	- 导出记录与快照记录
	- 错误反馈、空态与可恢复路径

### 壳层接入
- 修改：
	- `apps/desktop/src/app/router/routeManifest.ts`
	- `apps/desktop/src/app/router/routes.ts`
	- `apps/desktop/src/main.ts`
	- `apps/desktop/src/layouts/DetailPanel.vue`
	- `apps/desktop/src/modules/shell/useShellStore.ts`
- 需要新增 `video-editor` 专属 detail state 与 detail action 事件，例如 `tkops:video-editor-detail-action`，承接当前序列、选中片段、字幕风险、导出动作与快照恢复。

### Runtime 契约补齐
- 计划新增或修改：
	- `apps/py-runtime/src/api/http/video_editor/routes.py`
	- `apps/py-runtime/src/bootstrap/app_factory.py`
	- `apps/py-runtime/src/legacy_adapter/serializers.py`
	- `apps/desktop/src/modules/runtime/runtimeApi.ts`
	- `apps/desktop/src/modules/runtime/types.ts`
- 至少补齐以下 HTTP 能力：
	- `listVideoProjects`
	- `createVideoProject`
	- `listVideoSequences`
	- `createVideoSequence`
	- `setActiveVideoSequence`
	- `listVideoClips`
	- `appendAssetsToSequence` 或等价导入素材 / 挂入序列能力
	- `reorderVideoClips`
	- `trimVideoClip` / `updateVideoClip`
	- `deleteVideoClip`
	- `listVideoSubtitles`
	- `createVideoSubtitle`
	- `updateVideoSubtitle`
	- `deleteVideoSubtitle`
	- `createVideoExport`
	- `runVideoExport`
	- `listVideoExports`
	- `createVideoSnapshot`
	- `restoreVideoSnapshot`
	- `listVideoSnapshots`
- 说明：命名最终以 spec 为准，但能力集合不能缩水。

### 测试与文档
- 计划修改：
	- `tests/test_runtime_api.py`
	- `tests/test_desktop_frontend_routes.py`
	- `tests/test_page_runtime_data.py`
	- `tests/test_page_interaction_audit.py`
	- `docs/migration/page-matrix.md`
	- `docs/migration/current-status-and-roadmap.md`
- 如需要独立细测，可增补专门的 `video-editor` runtime / interaction 测试，但不允许跳过现有通用断言体系。

## Phase Plan

### Phase 1: 冻结旧壳结构、选中态与数据映射
- 明确 route、factory、loader、bindings、state、data、CSS 的逐文件映射表。
- 把工程、序列、素材库、片段、字幕、快照、导出映射为新壳 view model。
- 先锁定素材选中态、片段选中态、字幕选中态的边界，避免实现阶段再次混层。

### Phase 2: 补齐 video-editor runtime HTTP 契约
- 复用旧层 repository / service / bridge 语义，新增新壳 runtime route 与 serializer。
- 统一成功 / 失败 JSON 信封与日志记录。
- 确保数据变更后能触发前端刷新与缓存失效，不产生静默漂移。

### Phase 3: 实现新壳 video-editor 页面与壳层细节
- 按旧壳编辑器结构实现页面，不压平成单栏表格或说明卡。
- 保留素材区、节目监视器、时间线、检查器、导出区、快照区的协作关系。
- 接入 DetailPanel 与壳层 action，总线负责“切序列、导出、快照、字幕处理”等关键动作。

### Phase 4: 回归验证与迁移文档收口
- route 从 placeholder 升级为 implemented。
- 补齐 runtime、前端、交互审计和迁移矩阵断言。
- 跑完相关 pytest、typecheck、build，确保该页从占位态变成可用真实页。

## 文件地图
- 旧壳输入：
	- `desktop_app/assets/js/routes.js`
	- `desktop_app/assets/js/factories/video-editor.js`
	- `desktop_app/assets/js/page-loaders/video-editor-main.js`
	- `desktop_app/assets/js/bindings/video-editor-bindings.js`
	- `desktop_app/assets/js/state.js`
	- `desktop_app/assets/js/data.js`
	- `desktop_app/assets/css/pages-content.css`
	- `desktop_app/assets/css/interactions.css`
	- `desktop_app/database/models.py`
	- `desktop_app/database/repository.py`
	- `desktop_app/services/video_editing_service.py`
	- `desktop_app/services/video_export_service.py`
	- `desktop_app/ui/bridge.py`
- 新壳输出：
	- `apps/desktop/src/pages/content/*`
	- `apps/desktop/src/modules/content/*`
	- `apps/desktop/src/modules/runtime/*`
	- `apps/desktop/src/modules/shell/useShellStore.ts`
	- `apps/desktop/src/layouts/DetailPanel.vue`
	- `apps/desktop/src/app/router/*`
	- `apps/desktop/src/styles/*`
	- `apps/py-runtime/src/api/http/**`
	- `apps/py-runtime/src/bootstrap/app_factory.py`
	- `apps/py-runtime/src/legacy_adapter/serializers.py`
	- `tests/*`
	- `docs/migration/*`

## Validation Baseline
- `venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "video" -v`
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py tests/test_page_runtime_data.py tests/test_page_interaction_audit.py -v`
- 如新增专门 video-editor 测试，则把专测加入同一轮验证
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## Boundaries
- 不在本轮同时迁移 `visual-editor`、`visual-lab`、`profit-analysis` 或 `traffic-board`。
- 不引入超出旧壳基线的高级 NLE 特性，如复杂特效、关键帧系统、撤销栈重写。
- 不把视频编辑逻辑偷偷塞回 `desktop_app` 前端壳；新功能默认只落在 `apps/desktop` 与 `apps/py-runtime`。
- 没有真实数据时使用空态，不允许继续保留“混剪序列 #18”一类冻结示例文案作为假数据。

## Rollback Points
1. 若新壳 runtime 在本轮无法稳定暴露视频编辑 HTTP 契约，则停在 spec，不进入页面编码。
2. 若旧层服务与序列素材库语义存在未解歧义，先在 spec 中补清，不直接凭猜测落实现。
3. 若节目监视器与时间线布局在现有壳层内无法承载，则优先扩展壳层状态与样式，不在页面内部复制第二套 detail 体系。

## Risks
1. 旧层视频编辑同时包含素材库、时间线和导出状态，容易在 Vue 页面里重新堆成大文件。
	- 应对：spec 阶段先拆 `types/helpers/composable/page/css/detail state`，避免再次形成巨型组件。
2. 新壳 runtime 目前完全缺失视频编辑 HTTP 契约，范围天然大于 creative-workshop 和 ai-content-factory。
	- 应对：优先复用 `desktop_app` 服务与仓库，避免重写领域逻辑。
3. 素材库与时间线片段语义容易被误合并，导致选中态、删除语义和导出校验失真。
	- 应对：spec 必须单独写明 asset / clip / subtitle 三态与导出校验链。
4. 本地视频预览、导出和快照恢复都依赖文件路径有效性，错误反馈如果不统一，UI 会再次出现静默失败。
	- 应对：runtime 与 composable 统一错误信封、日志与前端提示。

## Exit Criteria
- `video-editor` 拥有独立 plan，不再只是迁移矩阵里的占位条目。
- 已明确该页迁移必须同时覆盖视频工程链路、runtime HTTP、前端编辑器结构、DetailPanel 和测试闭环。
- 已明确旧层可复用资产与新壳缺口，后续 spec 可直接进入文件级设计，不再重复摸底。
- plan 获批后，下一步直接进入 `video-editor` 独立 design spec 编写。
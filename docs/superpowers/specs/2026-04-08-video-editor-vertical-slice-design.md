# 视频编辑垂直切片设计

## 1. 目标

- 将 `video-editor` 从占位路由升级为真实新壳页面。
- 严格复用旧壳 `makeVideoEditorRoute()`、`video-editor-main.js`、`video-editor-bindings.js` 的编辑器语义，不把它降级成静态时间线示意页。
- 同步补齐新壳 runtime 对视频工程、序列、片段、字幕、快照、导出的 HTTP 契约，让“切换剪辑序列”“导入素材”“发起终版导出”等动作走真实数据链路。
- 页面、右栏详情、runtime API、测试、迁移文档同时落地，避免出现“页面已切换但编辑动作仍是空壳”的半迁移状态。

## 2. 旧壳基线映射

### 2.1 Route 基线

- 旧壳入口：`desktop_app/assets/js/routes.js`
- 页面配置：`video-editor: makeVideoEditorRoute()`
- 业务语义：承接上游创意与素材后，在当前工程中进行序列切换、片段裁切、字幕校对、快照恢复和终版导出。
- 核心动作语义：
  - `primaryAction = 发起终版导出`
  - `secondaryAction = 切换剪辑序列`
  - 扩展动作：`试看导出`、`导入素材`、`新增字幕`、`保存快照`

### 2.2 Factory 基线

- 旧壳入口：`desktop_app/assets/js/factories/video-editor.js`
- 页面是独立编辑器布局，而不是普通 content workbench 子页。
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
- 布局职责：
  - 左侧：素材库与当前素材预览
  - 中部：节目监视器、播放头、时间线轨道
  - 右侧：检查器、字幕/导出待办队列
  - 右栏详情：当前批次、重点风险、值班动作

### 2.3 Loader 基线

- 旧壳入口：`desktop_app/assets/js/page-loaders/video-editor-main.js`
- 真实数据来源：
  - `api.videoProjects.list()`
  - `api.assets.list()`
  - `api.tasks.list()`
  - `api.videoSequences.list(project.id)`
  - `api.videoClips.list(sequence.id)`
  - `api.videoSubtitles.list(sequence.id)`
  - `api.videoExports.list(project.id)`
  - `api.videoSnapshots.list(project.id)`
- 页面状态：
  - `selectedProjectId`
  - `selectedSequenceId`
  - `selectedAssetId`
  - `selectedClipId`
  - `selectedSubtitleId`
  - `selectedSnapshotId`
  - `inspectorTab`
  - `playheadMs`
- 关键行为：
  - runtime summary 基于工程、序列、片段、导出状态实时派生
  - 素材点击只切换预览，双击才加入当前序列或时间线
  - 片段、字幕点击分别进入不同选中态
  - `handleDataChanged` 负责时间线、输出区、摘要区的回流刷新

### 2.4 交互与持久化基线

- 旧壳入口：`desktop_app/assets/js/bindings/video-editor-bindings.js`
- 关键动作：
  - `发起终版导出` -> `_runExport('final')`
  - `试看导出` -> `_runExport('preview')`
  - `切换剪辑序列` -> `_switchSequence()`
  - `导入素材` -> 选文件并挂入当前序列
  - `新增字幕` / `编辑字幕` / `删除字幕`
  - `设入点` / `设出点`
  - `左移片段` / `右移片段` / `删除片段`
  - `保存快照` / `恢复快照`
- 交互结论：新壳必须保住 asset / clip / subtitle 三种选中态，并保住导出、快照与字幕操作的真实写链路。

### 2.5 仓库记忆约束

- 当前序列素材库语义：只展示当前序列已导入素材，不等于全局素材中心。
- 删除序列内素材只从当前序列移除，不删除全局 `Asset`。
- `appendAssetsToSequence` 只负责导入当前序列素材库；真正进入时间线的片段语义必须独立处理。
- 选中态必须区分：素材预览、时间线片段编辑、字幕检查器。
- 导出校验不能因为时间线为空就跳过源文件缺失检查。

## 3. Runtime 方案

### 3.1 当前状态判断

- 旧层 `desktop_app` 已具备完整领域能力：
  - `VideoProject`
  - `VideoSequence`
  - `VideoSequenceAsset`
  - `VideoClip`
  - `VideoSubtitle`
  - `VideoExport`
  - `VideoSnapshot`
  - `VideoEditingService`
  - `VideoExportService`
- 当前新壳缺口：
  - `apps/py-runtime/src/api/http/**` 没有 video-editor route
  - `apps/desktop/src/modules/runtime/runtimeApi.ts` 没有视频编辑 API
  - `apps/desktop/src/modules/runtime/types.ts` 没有视频编辑实体类型

### 3.2 新增 HTTP Router

- 新增：`apps/py-runtime/src/api/http/video_editor/routes.py`
- 路由前缀建议：`/video-editor`
- 首轮 endpoint：
  - `GET /video-editor/projects`
  - `POST /video-editor/projects`
  - `GET /video-editor/projects/{project_id}/sequences`
  - `POST /video-editor/sequences`
  - `POST /video-editor/sequences/activate`
  - `GET /video-editor/sequences/{sequence_id}/clips`
  - `POST /video-editor/sequences/{sequence_id}/assets`
  - `POST /video-editor/clips/reorder`
  - `PATCH /video-editor/clips/{clip_id}`
  - `POST /video-editor/clips/trim`
  - `DELETE /video-editor/clips/{clip_id}`
  - `GET /video-editor/sequences/{sequence_id}/subtitles`
  - `POST /video-editor/subtitles`
  - `PATCH /video-editor/subtitles/{subtitle_id}`
  - `DELETE /video-editor/subtitles/{subtitle_id}`
  - `GET /video-editor/projects/{project_id}/exports`
  - `POST /video-editor/exports`
  - `POST /video-editor/exports/{export_id}/run`
  - `GET /video-editor/projects/{project_id}/snapshots`
  - `POST /video-editor/snapshots`
  - `POST /video-editor/snapshots/{snapshot_id}/restore`
- 设计取舍：
  - 路径统一挂到 `video-editor` 前缀，降低前端接线复杂度
  - 不强行暴露 bridge 的所有方法名，HTTP 层可做更清晰的 REST 化整理
  - 能力集合与旧壳保持等价，不缩水

### 3.3 数据来源与胶水层

- 新 router 复用：
  - `desktop_app.database.repository.Repository`
  - `desktop_app.services.video_editing_service.VideoEditingService`
  - `desktop_app.services.video_export_service.VideoExportService`
- 在 `apps/py-runtime/src/legacy_adapter/serializers.py` 新增：
  - `serialize_video_project(...)`
  - `serialize_video_sequence(...)`
  - `serialize_video_sequence_asset(...)`
  - `serialize_video_clip(...)`
  - `serialize_video_subtitle(...)`
  - `serialize_video_export(...)`
  - `serialize_video_snapshot(...)`
- 错误处理：
  - router 捕获异常并返回统一中文错误信息
  - 记录 `log.exception(...)`
  - 不向前端暴露 traceback

### 3.4 app_factory 注册

- 修改：`apps/py-runtime/src/bootstrap/app_factory.py`
- 将 video-editor router 与 `assets`、`tasks`、`providers`、`workflows` 同级注册

### 3.5 新壳 runtimeApi/types 扩展

- 修改：
  - `apps/desktop/src/modules/runtime/types.ts`
  - `apps/desktop/src/modules/runtime/runtimeApi.ts`
- 新增最小类型：
  - `VideoProjectItem`
  - `VideoSequenceItem`
  - `VideoSequenceAssetItem`
  - `VideoClipItem`
  - `VideoSubtitleItem`
  - `VideoExportItem`
  - `VideoSnapshotItem`
  - `VideoProjectCreatePayload`
  - `VideoSequenceCreatePayload`
  - `VideoClipPatchPayload`
  - `VideoClipReorderPayload`
  - `VideoSubtitleCreatePayload`
  - `VideoSubtitlePatchPayload`
  - `VideoExportCreatePayload`
  - `VideoSnapshotCreatePayload`
- 新增方法：
  - `listVideoProjects()`
  - `createVideoProject(payload)`
  - `listVideoSequences(projectId)`
  - `createVideoSequence(payload)`
  - `setActiveVideoSequence(projectId, sequenceId)`
  - `listVideoClips(sequenceId)`
  - `appendAssetsToSequence(sequenceId, payload)`
  - `reorderVideoClips(payload)`
  - `updateVideoClip(clipId, payload)`
  - `trimVideoClip(payload)`
  - `deleteVideoClip(clipId)`
  - `listVideoSubtitles(sequenceId)`
  - `createVideoSubtitle(payload)`
  - `updateVideoSubtitle(subtitleId, payload)`
  - `deleteVideoSubtitle(subtitleId)`
  - `listVideoExports(projectId)`
  - `createVideoExport(payload)`
  - `runVideoExport(exportId)`
  - `listVideoSnapshots(projectId)`
  - `createVideoSnapshot(payload)`
  - `restoreVideoSnapshot(snapshotId)`

## 4. 新壳页面方案

### 4.1 文件布局

- 页面：`apps/desktop/src/pages/content/VideoEditorPage.vue`
- 数据模块：
  - `apps/desktop/src/modules/content/videoEditor.types.ts`
  - `apps/desktop/src/modules/content/videoEditor.helpers.ts`
  - `apps/desktop/src/modules/content/useVideoEditorData.ts`
- 样式：`apps/desktop/src/styles/video-editor.css`

### 4.2 页面结构

页面按旧壳结构拆成 6 段：

1. 头部操作区
   - 切换剪辑序列
   - 发起终版导出
   - 试看导出
   - 刷新
2. summary strip
   - 当前工程
   - 当前序列
   - 导出状态
3. 主编辑器 shell
   - rail tools
   - 素材库面板
   - 节目监视器
   - transport bar
   - 时间线轨道
4. 检查器与待办队列
   - 当前片段/素材/字幕状态
   - 导出队列
   - 字幕校对提醒
5. 页面内输出区
   - 导出记录
   - 快照记录
6. 空态与错误态
   - 无工程
   - 无序列
   - 无素材
   - 无导出

### 4.3 composable 数据面

`useVideoEditorData.ts` 负责：

- 页面初始化并发拉取：
  - `listVideoProjects`
  - `listAssets`
  - `listTasks`
- 在选中工程后拉取：
  - `listVideoSequences(projectId)`
- 在选中序列后拉取：
  - `listVideoClips(sequenceId)`
  - `listVideoSubtitles(sequenceId)`
- 在选中工程后同时拉取：
  - `listVideoExports(projectId)`
  - `listVideoSnapshots(projectId)`
- 维护状态：
  - `selectedProjectId`
  - `selectedSequenceId`
  - `selectedAssetId`
  - `selectedClipId`
  - `selectedSubtitleId`
  - `selectedSnapshotId`
  - `inspectorTab`
  - `playheadMs`
  - `isLoading`
  - `errorMessage`

### 4.4 派生规则

- summary chips：
  - 当前工程：最近工程名，否则显示“尚未创建工程”
  - 当前序列：当前激活序列名，否则显示“尚未创建序列”
  - 导出状态：基于导出列表聚合 `running / failed / completed`
- 素材库卡片：
  - 只显示当前序列素材库或可挂入当前序列的素材
  - 单击切素材预览
  - 双击执行导入/挂载动作
- 时间线轨：
  - 视频轨、字幕轨、音频轨分开渲染
  - 点击片段只切片段选中态
  - 点击字幕只切字幕选中态
- 检查器：
  - `属性`、`字幕`、`导出` 三类 tab
  - 内容由选中实体与导出状态派生

### 4.5 页面动作映射

- `切换剪辑序列`
  - 若仅有一个序列：创建下一个序列并切换
  - 若已有多个序列：在当前序列列表中循环切换
- `导入素材`
  - 首轮继续调用现有素材导入链
  - 导入成功后自动刷新当前序列与时间线
- `新增字幕`
  - 基于当前片段或当前播放头创建字幕
- `编辑字幕`
  - 更新选中字幕文本
- `删除字幕`
  - 删除选中字幕并刷新轨道
- `设入点` / `设出点`
  - 基于选中片段和当前播放头执行 trim
- `左移片段` / `右移片段`
  - 通过 reorder/update 接口调整顺序
- `删除片段`
  - 删除选中片段并刷新时间线
- `保存快照`
  - 创建新快照并刷新快照列表
- `恢复快照`
  - 恢复选中或最近快照后刷新工程视图
- `试看导出`
  - `createVideoExport(preset='preview')` 后 `runVideoExport`
- `发起终版导出`
  - `createVideoExport(preset='final')` 后 `runVideoExport`

### 4.6 空态与错误反馈

- 无工程：展示创建第一个工程的引导卡，不出现伪造示例项目
- 无序列：展示“创建序列”动作
- 无素材：展示“导入素材”动作
- 无片段：提示双击素材加入序列或时间线
- 导出失败：在页面与 DetailPanel 同时显示明确中文原因
- 所有写操作失败都需要 toast 或可见错误条，不允许静默失败

## 5. 壳层详情区

### 5.1 新增状态分支

- 修改：`apps/desktop/src/modules/shell/useShellStore.ts`
- 新增：
  - `VideoEditorDetailKind`
  - `VideoEditorDetailState`
  - `videoEditorDetailState`
  - `setVideoEditorDetailState(...)`
  - `resetVideoEditorDetailState()`

### 5.2 detail state 内容

- `currentProjectName`
- `currentSequenceName`
- `selectedEntityKind`
- `selectedEntityTitle`
- `selectedEntityMeta[]`
- `riskItems[]`
- `queueItems[]`
- `actionState`
  - `canExportFinal`
  - `canPreviewExport`
  - `canSaveSnapshot`
  - `canRestoreSnapshot`
  - `canCreateSubtitle`

### 5.3 DetailPanel 分支

- 修改：`apps/desktop/src/layouts/DetailPanel.vue`
- 当 `currentRouteName === 'video-editor'` 时显示专属分支
- 右栏内容：
  - 当前工程与序列摘要
  - 当前选中素材 / 片段 / 字幕摘要
  - 风险项
  - 导出队列摘要
  - 快捷动作按钮
- detail action 事件：
  - `tkops:video-editor-detail-action`
- 首轮动作：
  - `export-final`
  - `export-preview`
  - `save-snapshot`
  - `restore-snapshot`
  - `create-subtitle`
  - `switch-sequence`

## 6. 前端实现边界

### 6.1 不做的事

- 不在本轮实现高级特效、关键帧、转场库、完整撤销栈
- 不实现浏览器级真实视频剪辑引擎
- 不把 `visual-editor` 一起改造进来

### 6.2 本轮必须有的真实度

- 工程、序列、片段、字幕、快照、导出都来自真实 runtime
- 页面不保留“混剪序列 #18”这类冻结示例文案
- 导出必须至少走真实 export create/run 链路
- 快照恢复必须走真实 runtime 接口，不是只弹 toast

## 7. 测试方案

### 7.1 Runtime 测试

- 修改：`tests/test_runtime_api.py`
- 新增覆盖：
  - video-editor HTTP route 成功返回统一信封
  - 列表类 endpoint 能返回真实结构
  - 写操作 endpoint 能正确透传 payload 并返回新实体

### 7.2 前端结构测试

- 修改：`tests/test_desktop_frontend_routes.py`
- 新增断言：
  - `video-editor` 已从 placeholder 切到真实 pageKind
  - `VideoEditorPage.vue` 已注册
  - `DetailPanel.vue` 拥有 `video-editor` 专属分支

### 7.3 真实数据测试

- 修改：`tests/test_page_runtime_data.py`
- 新增断言：
  - `useVideoEditorData.ts` 使用 `runtimeApi.listVideoProjects` 等真实链路
  - 页面不残留冻结示例文本
  - 导出、快照、字幕操作不只是 toast 假动作

### 7.4 交互审计测试

- 修改：`tests/test_page_interaction_audit.py`
- 新增断言：
  - 页面声明 `data-page-audit="video-editor"`
  - 页面具备 `发起终版导出`、`切换剪辑序列`、`新增字幕`、`保存快照` 等真实动作
  - page audit 注册表包含 `video-editor` 对应数据源与交互语义

### 7.5 验证命令

- `venv\Scripts\python.exe -m pytest tests/test_runtime_api.py -k "video" -v`
- `venv\Scripts\python.exe -m pytest tests/test_desktop_frontend_routes.py tests/test_page_runtime_data.py tests/test_page_interaction_audit.py -v`
- `cd apps/desktop && npm run typecheck`
- `cd apps/desktop && npm run build`

## 8. 文档更新

- 修改：`docs/migration/page-matrix.md`
  - `video-editor` 从“已注册菜单与占位路由”升级为“已迁移”
- 修改：`docs/migration/current-status-and-roadmap.md`
  - 已接入真实新链路页面数量加 1
  - 下一批优先页顺延为 `visual-lab`、`profit-analysis`、`traffic-board`

## 9. 风险与应对

### 9.1 页面复杂度风险

- 风险：素材库、节目监视器、时间线、导出队列天然容易堆成巨型 Vue 文件。
- 应对：实现时严格拆成 `types/helpers/composable/page/css`，必要时再把时间线渲染 helper 独立出来。

### 9.2 语义混层风险

- 风险：把 sequence library asset 与 timeline clip 当成同一实体，导致删除、预览、导出校验全错。
- 应对：spec 明确 `asset / clip / subtitle` 三态，页面和 DetailPanel 统一按三态派生。

### 9.3 runtime 接口过宽风险

- 风险：video-editor 需要的 endpoint 比 ai-content-factory 多，容易一口气铺太广。
- 应对：首轮只补当前页面真正使用的最小集合，命名和结构统一放在 `/video-editor` 前缀下。

### 9.4 文件路径与本地预览风险

- 风险：素材源文件缺失、导出路径不可写、本地视频不可预览会直接影响页面可信度。
- 应对：router 与 composable 必须统一错误反馈，页面空态/失败态要可见可恢复。

## 10. 实施顺序

1. 先补 video-editor runtime route、serializer、runtimeApi/types。
2. 再实现 `useVideoEditorData.ts` 与 view model helpers。
3. 再实现 `VideoEditorPage.vue` 和 `video-editor.css`。
4. 再接 `routeManifest.ts`、`routes.ts`、`main.ts`、`useShellStore.ts`、`DetailPanel.vue`。
5. 最后更新测试与迁移文档，并完成验证。

## 11. Exit Criteria

- `video-editor` 拥有独立 spec，已经明确到 endpoint、前端模块、DetailPanel 与测试粒度。
- 已锁定旧壳基线和新壳缺口，后续实现可直接按文件地图推进。
- spec 获批后，下一步直接进入 `video-editor` 的实现阶段。
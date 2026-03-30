# 视频剪辑模块重建与大文件拆分设计

## 1. 背景

当前仓库中的 `video-editor` 页面仍处于“半真实化壳层”状态：

- 页面结构、模板、loader 与交互绑定存在错位
- 关键操作仍是 toast 或通用任务创建，不是剪辑闭环
- 缺少视频工程、序列、片段、字幕、导出等真实持久化模型
- `page-loaders.js`、`bindings.js`、`factories/content.js` 等文件职责过重，已影响维护与定位问题

同时，`visual-editor` 与 `video-editor` 的职责已经漂移。当前项目需要把“视频剪辑”恢复为真正的核心能力，并顺手拆分与该功能直接相关的大文件，避免继续在根文件中堆叠逻辑。

## 2. 目标

本次改造目标分为两部分，必须同时完成：

1. 将 `video-editor` 做成具备基础剪辑闭环的真实功能页面
2. 对与该功能直接相关的大文件按模块拆分，降低耦合和后续扩展成本

本次完成后的 `video-editor` 至少具备以下能力：

- 素材导入到工程并加入时间线
- 多片段排序与删除
- 片段入点 / 出点裁切
- 字幕新增、编辑、删除
- 音频轨添加、静音、替换、移除
- 工程保存与重新打开恢复
- 导出前基础校验
- 真实导出成片

## 3. 非目标

本次不进入以下高级能力：

- 关键帧编辑
- 调色面板
- 复杂特效
- 高级转场库
- 完整撤销 / 重做栈
- NLE 级自由拖拽交互

这些能力不在本次范围内，但设计需为后续扩展留出边界。

## 4. 总体方案

采用“职责收口 + 最小真实模型 + 渐进式前端拆分”的方案：

- `video-editor` 聚焦真实剪辑工程
- `visual-editor` 收口为封面 / 图文 / 模板编辑器
- 新增视频剪辑持久化模型与服务层
- 导出链路通过 `ffmpeg` 实现，不再伪装成通用任务
- 将 `page-loaders.js`、`bindings.js`、`factories/content.js` 中与视频剪辑相关的部分拆到独立模块

设计原则：

- 优先真实闭环，不再接受“可点击原型”
- 优先小而清晰的模块边界，不再继续扩大根文件
- 优先性能稳定，避免页面进入卡顿、整页重绘、导出阻塞 UI
- 继续遵循现有 `window.api`、Bridge JSON 信封、`dataChanged` 回流契约

## 5. 页面职责边界

### 5.1 `video-editor`

职责：

- 视频工程管理
- 序列切换
- 时间线片段管理
- 字幕编辑
- 音频轨基础管理
- 保存 / 快照 / 恢复
- 导出校验与导出执行

不再承担：

- 封面模板设计
- 图文卡片排版
- 多尺寸静态设计稿导出

### 5.2 `visual-editor`

职责：

- 封面与图文设计
- 模板套用
- 多尺寸导出
- 静态视觉资产组合

不再承担：

- 视频时间线语义
- 片段裁切
- 字幕时间轴
- 成片导出语义

### 5.3 `asset-center`

职责保持为素材库：

- 素材上传、检索、标签、授权、归属
- 供 `video-editor` 与 `visual-editor` 选用

不直接承载剪辑工程语义。

## 6. 数据模型设计

在现有 `assets` 基础上新增最小可用剪辑模型。

### 6.1 新增表

#### `video_projects`

- `id`
- `name`
- `status`
- `canvas_ratio`
- `width`
- `height`
- `cover_asset_id`
- `last_opened_at`
- `created_at`
- `updated_at`

语义：一个视频剪辑工程。

#### `video_sequences`

- `id`
- `project_id`
- `name`
- `duration_ms`
- `sort_order`
- `is_active`
- `created_at`
- `updated_at`

语义：工程下的一个序列。

#### `video_clips`

- `id`
- `sequence_id`
- `asset_id`
- `track_type`，枚举：`video` / `audio`
- `track_index`
- `start_ms`
- `source_in_ms`
- `source_out_ms`
- `duration_ms`
- `sort_order`
- `transform_json`
- `created_at`
- `updated_at`

语义：落在时间线上的真实片段。

#### `video_subtitles`

- `id`
- `sequence_id`
- `start_ms`
- `end_ms`
- `text`
- `style_json`
- `sort_order`
- `created_at`
- `updated_at`

语义：字幕段。

#### `video_exports`

- `id`
- `project_id`
- `sequence_id`
- `status`
- `preset`
- `output_path`
- `ffmpeg_command`
- `error_message`
- `started_at`
- `finished_at`
- `created_at`

语义：一次真实导出行为。

#### `video_snapshots`

- `id`
- `project_id`
- `title`
- `snapshot_json`
- `created_at`

语义：工程快照，用于恢复与回看。

### 6.2 关系

- 一个 `video_project` 有多个 `video_sequence`
- 一个 `video_sequence` 有多个 `video_clip`
- 一个 `video_sequence` 有多个 `video_subtitle`
- 一个 `video_project` 有多个 `video_export`
- 一个 `video_project` 有多个 `video_snapshot`
- `video_clip.asset_id` 关联现有 `assets.id`

### 6.3 建模原则

- 不把剪辑数据塞进 `Task.result_summary` 或通用 JSON 字段里伪装
- 不复制 `assets`，直接复用现有素材表
- 不要求迁移历史页面状态，只要求新模型完整支撑当前功能

## 7. 服务层与 Bridge 设计

### 7.1 新增服务

#### `desktop_app/services/video_editing_service.py`

职责：

- 工程 CRUD
- 序列切换
- 素材加入时间线
- 片段排序 / 删除 / 裁切
- 字幕 CRUD
- 音频轨基础操作
- 快照保存与恢复
- 导出前校验

#### `desktop_app/services/video_export_service.py`

职责：

- FFmpeg / FFprobe 可用性检查
- 素材元信息探测
- 导出命令构建
- 导出执行与状态回写
- 失败原因记录

#### `desktop_app/services/ffmpeg_runtime.py`

职责：

- 查找 `ffmpeg.exe` / `ffprobe.exe`
- 区分开发环境与打包环境路径
- 提供统一可执行路径解析接口

### 7.2 Bridge 新增能力

`desktop_app/ui/bridge.py` 中新增视频编辑槽函数，遵循现有约束：

- `@Slot(..., result=str)`
- `@_safe`
- 返回 `_ok(...)` / `_err(...)`
- 状态变化后触发 `dataChanged`

首批接口建议：

- `listVideoProjects`
- `createVideoProject`
- `getVideoProject`
- `updateVideoProject`
- `listVideoSequences`
- `createVideoSequence`
- `setActiveVideoSequence`
- `appendAssetsToSequence`
- `listVideoClips`
- `updateVideoClip`
- `deleteVideoClip`
- `reorderVideoClips`
- `listVideoSubtitles`
- `createVideoSubtitle`
- `updateVideoSubtitle`
- `deleteVideoSubtitle`
- `listVideoExports`
- `createVideoExport`
- `listVideoSnapshots`
- `createVideoSnapshot`
- `restoreVideoSnapshot`
- `getVideoEditorSummary`

### 7.3 `window.api` 扩展

在 `desktop_app/assets/js/data.js` 新增：

- `api.videoProjects.*`
- `api.videoSequences.*`
- `api.videoClips.*`
- `api.videoSubtitles.*`
- `api.videoExports.*`
- `api.videoSnapshots.*`

继续使用缓存 + `dataChanged` 失效链路。

## 8. 前端结构与文件拆分

### 8.1 前端文件拆分目标

只拆与本次改造直接相关的部分，不做无边界重构。

### 8.2 目标结构

#### 页面 loader

- 保留：`desktop_app/assets/js/page-loaders.js`
  - 只做聚合入口、共享导出、兼容注册
- 新增：`desktop_app/assets/js/page-loaders/editor-shared.js`
  - 时间码、轨道摘要、选择态、通用 editor helper
- 新增：`desktop_app/assets/js/page-loaders/video-editor-main.js`
  - 只负责 `video-editor`
- 新增：`desktop_app/assets/js/page-loaders/visual-editor-main.js`
  - 只负责 `visual-editor`

#### 模板工厂

- 保留：`desktop_app/assets/js/factories/content.js`
  - 只保留聚合和公共结构
- 新增：`desktop_app/assets/js/factories/video-editor.js`
- 新增：`desktop_app/assets/js/factories/visual-editor.js`

#### 交互绑定

- 保留：`desktop_app/assets/js/bindings.js`
  - 全局绑定与聚合入口
- 新增：`desktop_app/assets/js/bindings/video-editor-bindings.js`
- 新增：`desktop_app/assets/js/bindings/visual-editor-bindings.js`

### 8.3 拆分原则

- 根文件继续保留兼容出口，避免一次性破坏脚本链
- 拆分页主逻辑时，同时把对应模板和绑定迁出
- 不再允许 `video-editor` 继续依赖素材中心专用的详情渲染函数

## 9. 页面数据流

`video-editor` 加载顺序：

1. 拉最近项目列表
2. 确定当前项目
3. 拉活动序列
4. 拉序列下的 `clips / subtitles / exports / snapshots`
5. 拉素材列表
6. 组装主页面状态

状态分层：

- 持久状态：来自数据库
- 临时状态：选中片段、播放头、拖拽态、未保存草稿

更新策略：

- 先前端局部更新，保证操作即时反馈
- 再调用后端持久化
- 成功后触发 `dataChanged`
- 当前页收到事件后做最小刷新，而不是整页重绘

## 10. 交互闭环设计

### 10.1 工程与序列

- 首次进入页面时，若无工程，显示空态并支持新建工程
- 工程下必须至少有一个活动序列
- 切换序列必须是后端真实切换，不再只是 toast

### 10.2 素材导入

- 从文件选择器导入：创建 `asset`
- 从素材库加入工程：创建 `video_clip`
- 页面必须明确区分“素材已入库”与“素材已进时间线”

### 10.3 时间线

首期支持：

- 前后移动
- 删除片段
- 修改入点 / 出点
- 视频轨与音频轨基础区分

首期不要求复杂拖拽，但布局与模型要允许后续加入拖拽。

### 10.4 字幕

- 新增、编辑、删除字幕段
- 字幕时间与序列时长保持一致
- 导出前做合法性校验

### 10.5 音频

- 添加到音频轨
- 替换
- 静音
- 删除

不做复杂混音和包络编辑。

### 10.6 保存与快照

- 保存更新工程与序列当前状态
- 支持创建快照
- 重新打开工程时恢复最近状态

### 10.7 导出

- 导出前校验
- 创建真实 `video_export`
- 通过 `ffmpeg` 执行
- 页面可看到导出状态与失败原因

## 11. 导出链路设计

导出不再伪装为通用任务，而是独立媒体链路。

流程：

1. 前端发起导出
2. 后端执行导出前校验
3. 创建 `video_export`
4. 构造 FFmpeg 命令
5. 启动导出进程
6. 状态更新为 `running`
7. 完成后写回 `completed` 或 `failed`
8. 发出 `dataChanged`

首期导出能力：

- 主视频轨顺序拼接
- 音频轨基础混入
- 字幕烧录
- 输出 MP4

若输入素材编码差异过大，可先做规范化转码再进入拼接链路。

## 12. 性能与卡顿优化要求

这是本次改造的硬要求，不是可选项。

### 12.1 页面加载性能

- 页面首屏不执行重量级同步分析
- 不在进入 `video-editor` 时主动做整批素材元信息重算
- 项目、序列、时间线、素材列表分批加载
- 只渲染当前可见列表，避免一次性堆满整个素材库和时间线

### 12.2 交互性能

- 修改片段、字幕、选择态时只做局部 DOM 更新
- 禁止时间线操作后整页 `renderRoute`
- 禁止依赖全页 loader 刷新来驱动每一次编辑

### 12.3 导出性能

- FFmpeg 导出必须在独立进程中执行
- UI 主线程不可等待导出完成
- 导出进度至少要有状态变化反馈，避免用户误判卡死

### 12.4 数据读取性能

- 素材元信息探测与封面读取优先复用缓存
- 进入页面只读取当前项目所需数据
- 历史快照、导出记录等非主视图数据可延后加载

### 12.5 大文件治理

- 拆分后单个页面逻辑文件应尽量控制在可理解范围
- 页面主逻辑、共享 helper、交互绑定、模板工厂分离
- 后续新增功能优先进入对应模块，不回灌根文件

## 13. 错误处理与空态

必须显式处理：

- 素材源文件不存在
- FFmpeg / FFprobe 不可用
- 导出路径不可写
- 片段裁切区间非法
- 字幕时间重叠或越界
- 当前序列为空
- 未保存变更直接导出
- 后端处理异常

UI 必须具备：

- 空态
- 加载态
- 错误态
- 可恢复提示

所有错误提示优先使用中文，不向用户暴露 traceback。

## 14. 数据库迁移策略

- 仅新增视频剪辑相关表
- 不破坏现有 `assets / tasks / reports / workflows / experiments`
- 不要求迁移旧的页面临时状态
- 首次进入 `video-editor` 时可懒创建默认工程

这样可以减少升级风险，并保持数据库升级可控。

## 15. FFmpeg 打包策略

Windows 打包产物中内置：

- `ffmpeg.exe`
- `ffprobe.exe`

打包策略：

- 服务层统一解析二进制路径
- 开发环境优先使用仓库内或打包产物内置版本
- 构建脚本与安装器同步纳入媒体二进制
- 启动前或首次导出前执行可用性检查

## 16. 测试策略

### 16.1 后端

- 模型 / 仓储测试
- Service 行为测试
- 导出校验测试
- FFmpeg 最小导出集成测试

### 16.2 Bridge

- 新增视频编辑接口契约测试
- 参数与 envelope 结构测试

### 16.3 前端

- 页面 loader 测试
- 页面审计测试
- 绑定点测试
- runtime summary 测试
- 错误态 / 空态测试

### 16.4 回归重点

必须覆盖以下已知风险：

- `video-editor` 引用不存在函数的问题
- loader 与模板渲染目标错位
- 素材选中后预览更新错误宿主
- 导出校验失败仍错误启动导出
- 保存后重新打开不能恢复工程

## 17. 落地顺序

推荐顺序：

1. 明确 `video-editor / visual-editor` 路由职责与模板边界
2. 拆分与两个页面相关的大文件逻辑
3. 新增数据库模型、repository、service、bridge、`window.api`
4. 将 `video-editor` 切换为真实工程驱动
5. 接入导出链路与 FFmpeg 打包
6. 补测试、构建验证、版本说明

## 18. 验收标准

满足以下条件才算完成：

- `video-editor` 能完成基础剪辑闭环
- `visual-editor` 职责收口清晰，不再承载时间线剪辑语义
- 新增后端能力全部走真实持久化与真实导出
- `page-loaders.js` 等相关大文件完成与目标功能直接相关的模块拆分
- 页面操作无明显卡顿，导出不阻塞 UI
- 相关测试通过
- 桌面应用能正常启动、打开页面、保存工程、恢复工程并导出成片

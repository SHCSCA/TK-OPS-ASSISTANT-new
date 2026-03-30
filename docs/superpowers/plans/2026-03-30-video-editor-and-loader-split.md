# Video Editor And Loader Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `video-editor` 重建为具备基础剪辑闭环的真实功能页面，并同步完成与该目标直接相关的大文件拆分、`ffmpeg` 导出链路接入和性能收口。

**Architecture:** 先通过测试锁定当前 `video-editor` 的结构错位与拆分契约，再新增视频工程持久化模型、服务层、Bridge 与 `window.api`。在后端能力稳定后，再拆 `factories/content.js`、`bindings.js`、`page-loaders.js` 的编辑器相关逻辑，最后把 `video-editor` 切换到真实工程驱动，并为 `visual-editor` 收口为静态视觉编辑器。导出链路独立于通用任务系统，通过 `ffmpeg` / `ffprobe` 执行，并以独立进程保证 UI 不被阻塞。

**Tech Stack:** Python 3.11+, SQLAlchemy 2.x, Alembic, PySide6/QWebChannel, vanilla JavaScript, Pytest, PowerShell, FFmpeg/FFprobe, PyInstaller

---

## File Map

- `desktop_app/database/models.py`
  - 新增视频工程、序列、片段、字幕、导出、快照实体
- `desktop_app/database/repository.py`
  - 新增视频剪辑数据访问、排序更新、关联查询
- `desktop_app/database/migrations/versions/<revision>_add_video_editor_tables.py`
  - 新增剪辑模块表结构
- `desktop_app/services/video_editing_service.py`
  - 工程/序列/片段/字幕/快照与基础校验
- `desktop_app/services/video_export_service.py`
  - 导出命令构建、导出状态回写、最小媒体校验
- `desktop_app/services/ffmpeg_runtime.py`
  - 统一解析 `ffmpeg.exe` / `ffprobe.exe` 路径
- `desktop_app/ui/bridge.py`
  - 暴露视频编辑相关槽函数
- `desktop_app/assets/js/data.js`
  - 新增 `api.videoProjects.*`、`api.videoSequences.*`、`api.videoClips.*`、`api.videoSubtitles.*`、`api.videoExports.*`、`api.videoSnapshots.*`
- `desktop_app/assets/js/routes.js`
  - 收口 `video-editor` / `visual-editor` 路由职责和静态摘要
- `desktop_app/assets/js/factories/content.js`
  - 只保留聚合入口与公共结构
- `desktop_app/assets/js/factories/video-editor.js`
  - `video-editor` 主模板与结构
- `desktop_app/assets/js/factories/visual-editor.js`
  - `visual-editor` 主模板与结构
- `desktop_app/assets/js/bindings.js`
  - 保留全局入口
- `desktop_app/assets/js/bindings/video-editor-bindings.js`
  - 视频剪辑页交互绑定
- `desktop_app/assets/js/bindings/visual-editor-bindings.js`
  - 视觉编辑页交互绑定
- `desktop_app/assets/js/page-loaders.js`
  - 保留聚合入口与共享导出
- `desktop_app/assets/js/page-loaders/editor-shared.js`
  - 编辑器共享 helper 与性能友好渲染函数
- `desktop_app/assets/js/page-loaders/video-editor-main.js`
  - `video-editor` loader 与局部渲染
- `desktop_app/assets/js/page-loaders/visual-editor-main.js`
  - `visual-editor` loader
- `desktop_app/assets/app_shell.html`
  - 注册新增脚本，保持加载顺序稳定
- `tk_ops.spec`
  - 打包 `ffmpeg` / `ffprobe`
- `build.py`
  - 校验与同步打包媒体二进制
- `tools/ffmpeg/win64/ffmpeg.exe`
  - Windows 打包用 FFmpeg 可执行文件
- `tools/ffmpeg/win64/ffprobe.exe`
  - Windows 打包用 FFprobe 可执行文件
- `tests/test_video_editor_loader_split.py`
  - 页面拆分与模板契约测试
- `tests/test_video_editor_models.py`
  - ORM / repository 层行为测试
- `tests/test_video_editing_service.py`
  - 工程、序列、片段、字幕、快照逻辑测试
- `tests/test_video_export_service.py`
  - 导出校验、命令构建与最小导出测试
- `tests/test_video_editor_bridge_contract.py`
  - Bridge 与 `window.api` 契约测试
- `tests/test_video_editor_runtime.py`
  - `video-editor` 运行时数据与局部更新测试
- `tests/test_video_editor_packaging.py`
  - `ffmpeg` 打包与解析策略测试

---

### Task 1: 锁定 `video-editor` 当前问题与拆分契约

**Files:**
- Create: `tests/test_video_editor_loader_split.py`
- Modify: `tests/test_page_runtime_data.py`
- Modify: `tests/test_crud_interaction_matrix.py`

- [ ] **Step 1: 写 `video-editor` 当前结构错位与拆分契约的失败测试**

在 `tests/test_video_editor_loader_split.py` 中增加以下断言：

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_SHELL = ROOT / "desktop_app" / "assets" / "app_shell.html"
ROUTES = ROOT / "desktop_app" / "assets" / "js" / "routes.js"
PAGE_LOADERS = ROOT / "desktop_app" / "assets" / "js" / "page-loaders.js"


def test_video_editor_route_no_longer_hides_sidebar_and_detail_panel():
    text = ROUTES.read_text(encoding="utf-8")
    assert "'video-editor': makeContentWorkbenchRoute({" in text
    assert "hideWorkbenchSidebar: true" not in text
    assert "hideDetailPanel: true" not in text


def test_video_editor_loader_is_moved_to_dedicated_module():
    html = APP_SHELL.read_text(encoding="utf-8")
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    assert './js/page-loaders/video-editor-main.js' in html
    assert "loaders['video-editor']" not in root


def test_video_editor_no_longer_depends_on_missing_bind_asset_thumbs():
    root = PAGE_LOADERS.read_text(encoding="utf-8")
    assert "_bindAssetThumbs(assets)" not in root
```

- [ ] **Step 2: 运行失败测试确认当前基线确实有问题**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_loader_split.py -v
```

Expected: FAIL，至少在 `hideWorkbenchSidebar`、`hideDetailPanel`、`loaders['video-editor']` 仍在根文件，以及 `_bindAssetThumbs(assets)` 仍存在这些断言上失败。

- [ ] **Step 3: 在现有运行时测试里补 `video-editor` 真实结构预期**

在 `tests/test_page_runtime_data.py` 与 `tests/test_crud_interaction_matrix.py` 中追加以下断言：

```python
def test_video_editor_runtime_uses_project_sequence_clip_language():
    text = aggregate_page_loader_text()
    assert "listVideoProjects" in text
    assert "appendAssetsToSequence" in text
    assert "createVideoExport" in text


def test_video_editor_actions_are_not_plain_toasts():
    text = aggregate_binding_text()
    assert "发起终版导出" in text
    assert "_createQuickTask('终版导出'" not in text
    assert "showToast('已切换到剪辑序列选择模式'" not in text
```

- [ ] **Step 4: 运行扩展后的页面契约测试并记录失败点**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_loader_split.py tests/test_page_runtime_data.py tests/test_crud_interaction_matrix.py -v
```

Expected: FAIL，说明后续改造目标已被测试锁住。

---

### Task 2: 新增视频剪辑 ORM 模型与迁移

**Files:**
- Create: `tests/test_video_editor_models.py`
- Modify: `desktop_app/database/models.py`
- Modify: `desktop_app/database/repository.py`
- Create: `desktop_app/database/migrations/versions/<revision>_add_video_editor_tables.py`

- [ ] **Step 1: 先写模型与关系失败测试**

在 `tests/test_video_editor_models.py` 中新增：

```python
from desktop_app.database.models import Asset
from desktop_app.database.repository import Repository


def test_can_create_video_project_sequence_clip_and_subtitle(tmp_path, repo_factory):
    repo = repo_factory(tmp_path)
    asset = repo.add(Asset(filename="clip.mp4", asset_type="video", file_path="C:/tmp/clip.mp4"))
    project = repo.create_video_project(name="Launch Sequence")
    sequence = repo.create_video_sequence(project.id, name="Main")
    clip = repo.append_video_clip(
        sequence.id,
        asset.id,
        track_type="video",
        track_index=0,
        start_ms=0,
        source_in_ms=0,
        source_out_ms=3000,
    )
    subtitle = repo.create_video_subtitle(sequence.id, start_ms=0, end_ms=1200, text="hello")

    assert project.id is not None
    assert sequence.project_id == project.id
    assert clip.asset_id == asset.id
    assert subtitle.sequence_id == sequence.id


def test_reorder_video_clips_updates_sort_order(tmp_path, repo_factory):
    repo = repo_factory(tmp_path)
    project = repo.create_video_project(name="Sort Test")
    sequence = repo.create_video_sequence(project.id, name="Main")
    first = repo.create_video_clip_placeholder(sequence.id, track_type="video", track_index=0, duration_ms=1000)
    second = repo.create_video_clip_placeholder(sequence.id, track_type="video", track_index=0, duration_ms=1000)

    repo.reorder_video_clips(sequence.id, [second.id, first.id])

    ids = [clip.id for clip in repo.list_video_clips(sequence.id)]
    assert ids == [second.id, first.id]
```

- [ ] **Step 2: 运行模型测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_models.py -v
```

Expected: FAIL，因为模型与 repository helper 尚不存在。

- [ ] **Step 3: 在 `models.py` 中新增视频剪辑实体**

新增以下类：

```python
class VideoProject(Base): ...
class VideoSequence(Base): ...
class VideoClip(Base): ...
class VideoSubtitle(Base): ...
class VideoExport(Base): ...
class VideoSnapshot(Base): ...
```

字段遵循 spec 中定义；关系至少覆盖：

```python
project.sequences
sequence.clips
sequence.subtitles
project.exports
project.snapshots
clip.asset
```

- [ ] **Step 4: 在 `repository.py` 中新增最小 CRUD / 排序 helper**

新增以下方法并保持命名固定：

```python
def create_video_project(self, *, name: str, **fields): ...
def list_video_projects(self): ...
def get_video_project(self, pk: int): ...
def create_video_sequence(self, project_id: int, *, name: str, **fields): ...
def list_video_sequences(self, project_id: int): ...
def set_active_video_sequence(self, project_id: int, sequence_id: int): ...
def append_video_clip(self, sequence_id: int, asset_id: int, **fields): ...
def create_video_clip_placeholder(self, sequence_id: int, *, track_type: str, track_index: int, duration_ms: int): ...
def list_video_clips(self, sequence_id: int): ...
def reorder_video_clips(self, sequence_id: int, ordered_ids: list[int]): ...
def create_video_subtitle(self, sequence_id: int, *, start_ms: int, end_ms: int, text: str, **fields): ...
def list_video_subtitles(self, sequence_id: int): ...
```

- [ ] **Step 5: 生成并应用 Alembic 迁移**

Run:

```powershell
venv\Scripts\python.exe -m alembic revision --autogenerate -m "add video editor tables"
venv\Scripts\python.exe -m alembic upgrade head
```

Expected: 生成包含 6 张新表的迁移，并成功升级。

- [ ] **Step 6: 回跑模型测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_models.py -v
```

Expected: PASS。

---

### Task 3: 实现视频编辑服务层与基础校验

**Files:**
- Create: `tests/test_video_editing_service.py`
- Create: `desktop_app/services/video_editing_service.py`
- Modify: `desktop_app/services/__init__.py`

- [ ] **Step 1: 先写服务层失败测试**

在 `tests/test_video_editing_service.py` 中新增：

```python
from desktop_app.services.video_editing_service import VideoEditingService


def test_append_assets_to_sequence_creates_real_clips(tmp_path, repo_factory):
    repo = repo_factory(tmp_path)
    service = VideoEditingService(repo)
    project = service.create_project("Editor Project")
    sequence = service.create_sequence(project.id, "Main")
    asset = service._repo.add_asset_for_test("clip.mp4", "video", "C:/tmp/clip.mp4")

    created = service.append_assets_to_sequence(sequence.id, [asset.id])

    assert len(created) == 1
    assert created[0].asset_id == asset.id


def test_trim_clip_rejects_invalid_ranges(tmp_path, repo_factory):
    repo = repo_factory(tmp_path)
    service = VideoEditingService(repo)
    clip = service._repo.add_video_clip_for_test(duration_ms=3000)

    try:
        service.update_clip_range(clip.id, source_in_ms=2800, source_out_ms=1200)
    except ValueError as exc:
        assert "裁切区间" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_export_validation_blocks_missing_source_file(tmp_path, repo_factory):
    repo = repo_factory(tmp_path)
    service = VideoEditingService(repo)
    project, sequence = service.create_project_with_sequence("Validation")
    asset = service._repo.add_asset_for_test("missing.mp4", "video", "C:/tmp/missing.mp4")
    service.append_assets_to_sequence(sequence.id, [asset.id])

    result = service.validate_export(project.id, sequence.id)

    assert result["ok"] is False
    assert "素材源文件不存在" in result["errors"][0]
```

- [ ] **Step 2: 运行服务层测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editing_service.py -v
```

Expected: FAIL，因为服务层尚不存在。

- [ ] **Step 3: 实现 `VideoEditingService` 的最小可用接口**

实现并固定以下方法名：

```python
class VideoEditingService:
    def create_project(self, name: str, **fields): ...
    def create_sequence(self, project_id: int, name: str, **fields): ...
    def create_project_with_sequence(self, name: str): ...
    def append_assets_to_sequence(self, sequence_id: int, asset_ids: list[int]): ...
    def update_clip_range(self, clip_id: int, *, source_in_ms: int, source_out_ms: int): ...
    def delete_clip(self, clip_id: int): ...
    def move_clip(self, sequence_id: int, clip_id: int, direction: str): ...
    def create_subtitle(self, sequence_id: int, *, start_ms: int, end_ms: int, text: str, **fields): ...
    def update_subtitle(self, subtitle_id: int, **fields): ...
    def delete_subtitle(self, subtitle_id: int): ...
    def create_snapshot(self, project_id: int, title: str): ...
    def restore_snapshot(self, snapshot_id: int): ...
    def validate_export(self, project_id: int, sequence_id: int) -> dict[str, object]: ...
```

校验规则必须明确：

- `source_in_ms < source_out_ms`
- `source_out_ms` 不得超过素材长度
- 字幕时间不得重叠和越界
- 序列为空时禁止导出
- 源文件不存在时禁止导出

- [ ] **Step 4: 回跑服务层测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editing_service.py tests/test_video_editor_models.py -v
```

Expected: PASS。

---

### Task 4: 接入 FFmpeg 运行时与真实导出链路

**Files:**
- Create: `tests/test_video_export_service.py`
- Create: `tests/test_video_editor_packaging.py`
- Create: `desktop_app/services/ffmpeg_runtime.py`
- Create: `desktop_app/services/video_export_service.py`
- Modify: `desktop_app/services/video_editing_service.py`

- [ ] **Step 1: 先写 FFmpeg 运行时和导出失败测试**

在 `tests/test_video_export_service.py` 中新增：

```python
from desktop_app.services.ffmpeg_runtime import resolve_ffmpeg_binaries
from desktop_app.services.video_export_service import VideoExportService


def test_resolve_ffmpeg_binaries_prefers_bundled_tools(tmp_path, monkeypatch):
    tools = tmp_path / "tools" / "ffmpeg" / "win64"
    tools.mkdir(parents=True)
    (tools / "ffmpeg.exe").write_bytes(b"x")
    (tools / "ffprobe.exe").write_bytes(b"y")

    ffmpeg, ffprobe = resolve_ffmpeg_binaries(root=tmp_path)

    assert ffmpeg.name == "ffmpeg.exe"
    assert ffprobe.name == "ffprobe.exe"


def test_create_export_rejects_invalid_sequence(tmp_path, repo_factory):
    repo = repo_factory(tmp_path)
    service = VideoExportService(repo)

    result = service.validate_and_create_export(project_id=1, sequence_id=1, preset="mp4_1080p")

    assert result["ok"] is False
    assert "序列不存在" in result["error"]
```

再在同文件加入最小导出测试：

```python
def test_minimal_export_writes_output_file(tmp_path, repo_factory, sample_media_factory):
    repo = repo_factory(tmp_path)
    sample = sample_media_factory(tmp_path, duration_ms=1000)
    service = VideoExportService(repo)
    project, sequence = repo.create_video_project_with_sample_clip(sample)

    result = service.validate_and_create_export(project.id, sequence.id, preset="mp4_1080p")
    completed = service.run_export(result["export_id"])

    assert completed.status == "completed"
    assert Path(completed.output_path).exists()
```

- [ ] **Step 2: 运行导出测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_export_service.py -v
```

Expected: FAIL，因为 FFmpeg 运行时与导出服务尚不存在。

- [ ] **Step 3: 实现 `ffmpeg_runtime.py`**

实现以下接口：

```python
def resolve_ffmpeg_binaries(root: Path | None = None) -> tuple[Path, Path]: ...
def ensure_ffmpeg_available(root: Path | None = None) -> dict[str, object]: ...
```

解析顺序固定为：

1. `tools/ffmpeg/win64/ffmpeg.exe`
2. 打包产物目录中的 `tools/ffmpeg/win64/ffmpeg.exe`
3. 如果以上均不存在，则返回明确错误

- [ ] **Step 4: 实现 `VideoExportService`**

接口保持为：

```python
class VideoExportService:
    def validate_and_create_export(self, project_id: int, sequence_id: int, *, preset: str): ...
    def build_export_command(self, export_id: int) -> list[str]: ...
    def run_export(self, export_id: int): ...
```

要求：

- 创建 `video_export` 记录
- 使用独立进程调用 `ffmpeg`
- 状态流转为 `pending -> running -> completed/failed`
- 失败时写回 `error_message`

- [ ] **Step 5: 回跑导出与打包测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_export_service.py tests/test_video_editor_packaging.py -v
```

Expected: PASS。

---

### Task 5: 补齐 Bridge、`window.api` 与浏览器 stub 契约

**Files:**
- Create: `tests/test_video_editor_bridge_contract.py`
- Modify: `desktop_app/ui/bridge.py`
- Modify: `desktop_app/assets/js/data.js`
- Modify: `desktop_app/assets/js/bridge.js`

- [ ] **Step 1: 先写 Bridge 契约失败测试**

在 `tests/test_video_editor_bridge_contract.py` 中新增：

```python
from pathlib import Path


def test_video_editor_bridge_methods_exist():
    text = Path("desktop_app/ui/bridge.py").read_text(encoding="utf-8")
    for name in [
        "listVideoProjects",
        "createVideoProject",
        "listVideoSequences",
        "appendAssetsToSequence",
        "listVideoClips",
        "updateVideoClip",
        "createVideoSubtitle",
        "createVideoExport",
        "listVideoSnapshots",
        "restoreVideoSnapshot",
    ]:
        assert f"def {name}(" in text


def test_data_js_exposes_video_editor_api_groups():
    text = Path("desktop_app/assets/js/data.js").read_text(encoding="utf-8")
    assert "videoProjects:" in text
    assert "videoSequences:" in text
    assert "videoClips:" in text
    assert "videoSubtitles:" in text
    assert "videoExports:" in text
    assert "videoSnapshots:" in text
```

- [ ] **Step 2: 运行 Bridge 契约测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_bridge_contract.py -v
```

Expected: FAIL。

- [ ] **Step 3: 在 `bridge.py`、`data.js`、`bridge.js` 中补齐接口**

Bridge 需新增：

```python
@Slot(result=str) def listVideoProjects(self) -> str: ...
@Slot(str, result=str) def createVideoProject(self, payload: str) -> str: ...
@Slot(int, result=str) def listVideoSequences(self, project_id: int) -> str: ...
@Slot(int, str, result=str) def appendAssetsToSequence(self, sequence_id: int, payload: str) -> str: ...
@Slot(int, result=str) def listVideoClips(self, sequence_id: int) -> str: ...
@Slot(int, str, result=str) def updateVideoClip(self, clip_id: int, payload: str) -> str: ...
@Slot(str, result=str) def createVideoSubtitle(self, payload: str) -> str: ...
@Slot(str, result=str) def createVideoExport(self, payload: str) -> str: ...
```

`data.js` 与 `bridge.js` stub 同步新增同名能力，并在成功后触发 `dataChanged` 缓存失效。

- [ ] **Step 4: 回跑 Bridge 契约测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_bridge_contract.py tests/test_bridge_runtime_contract.py -v
```

Expected: PASS。

---

### Task 6: 拆分模板工厂并收口 `video-editor` / `visual-editor` 路由职责

**Files:**
- Modify: `desktop_app/assets/js/routes.js`
- Modify: `desktop_app/assets/js/factories/content.js`
- Create: `desktop_app/assets/js/factories/video-editor.js`
- Create: `desktop_app/assets/js/factories/visual-editor.js`
- Modify: `desktop_app/assets/app_shell.html`
- Modify: `tests/test_video_editor_loader_split.py`

- [ ] **Step 1: 先写模板拆分失败测试**

在 `tests/test_video_editor_loader_split.py` 中追加：

```python
def test_video_and_visual_editor_factories_are_registered_in_shell():
    html = APP_SHELL.read_text(encoding="utf-8")
    assert './js/factories/video-editor.js' in html
    assert './js/factories/visual-editor.js' in html


def test_content_factory_keeps_only_aggregate_editor_entrypoints():
    text = Path("desktop_app/assets/js/factories/content.js").read_text(encoding="utf-8")
    assert "if (config.workbenchType === 'video-editor')" not in text
    assert "if (config.workbenchType === 'visual-editor')" not in text
```

- [ ] **Step 2: 运行模板拆分测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_loader_split.py::test_video_and_visual_editor_factories_are_registered_in_shell tests/test_video_editor_loader_split.py::test_content_factory_keeps_only_aggregate_editor_entrypoints -v
```

Expected: FAIL。

- [ ] **Step 3: 拆分 `content.js` 并调整路由配置**

实现要求：

- `video-editor` 模板迁入 `factories/video-editor.js`
- `visual-editor` 模板迁入 `factories/visual-editor.js`
- `routes.js` 中移除 `hideWorkbenchSidebar: true`、`hideDetailPanel: true`
- `visual-editor` 文案明确为封面 / 图文 / 模板编辑器

- [ ] **Step 4: 回跑模板拆分测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_loader_split.py -k "factories or hides" -v
```

Expected: PASS。

---

### Task 7: 拆分 `bindings.js` 与 `page-loaders.js` 的编辑器相关逻辑

**Files:**
- Modify: `desktop_app/assets/js/bindings.js`
- Create: `desktop_app/assets/js/bindings/video-editor-bindings.js`
- Create: `desktop_app/assets/js/bindings/visual-editor-bindings.js`
- Modify: `desktop_app/assets/js/page-loaders.js`
- Create: `desktop_app/assets/js/page-loaders/editor-shared.js`
- Create: `desktop_app/assets/js/page-loaders/video-editor-main.js`
- Create: `desktop_app/assets/js/page-loaders/visual-editor-main.js`
- Modify: `desktop_app/assets/app_shell.html`
- Modify: `tests/test_video_editor_loader_split.py`

- [ ] **Step 1: 先写 loader / binding 模块拆分失败测试**

在 `tests/test_video_editor_loader_split.py` 中追加：

```python
def test_shell_registers_editor_loader_and_binding_modules():
    html = APP_SHELL.read_text(encoding="utf-8")
    assert './js/bindings/video-editor-bindings.js' in html
    assert './js/bindings/visual-editor-bindings.js' in html
    assert './js/page-loaders/editor-shared.js' in html
    assert './js/page-loaders/video-editor-main.js' in html
    assert './js/page-loaders/visual-editor-main.js' in html


def test_root_page_loaders_keeps_only_registry_and_shared_exports():
    text = PAGE_LOADERS.read_text(encoding="utf-8")
    assert "window._pageLoaders = loaders;" in text
    assert "window.__pageAudits = pageAudits;" in text
    assert "loaders['video-editor'] = function ()" not in text
    assert "loaders['visual-editor'] = function ()" not in text
```

- [ ] **Step 2: 运行拆分测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_loader_split.py -k "binding or loader" -v
```

Expected: FAIL。

- [ ] **Step 3: 抽离编辑器 loader 与 binding 逻辑**

要求：

- `video-editor` 相关绑定全部迁入 `video-editor-bindings.js`
- `visual-editor` 相关绑定全部迁入 `visual-editor-bindings.js`
- `video-editor` / `visual-editor` loader 迁入对应 `page-loaders/*.js`
- 根 `page-loaders.js` 仅保留聚合入口、共享 helper 导出与 `data:changed` 总线

- [ ] **Step 4: 回跑拆分测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_loader_split.py tests/test_page_loader_account_split.py -v
```

Expected: PASS。

---

### Task 8: 将 `video-editor` 切换为真实工程驱动并收口局部刷新

**Files:**
- Create: `tests/test_video_editor_runtime.py`
- Modify: `desktop_app/assets/js/page-loaders/video-editor-main.js`
- Modify: `desktop_app/assets/js/bindings/video-editor-bindings.js`
- Modify: `desktop_app/assets/js/page-loaders/editor-shared.js`
- Modify: `desktop_app/assets/js/routes.js`

- [ ] **Step 1: 先写运行时测试，锁定真实数据链和局部更新**

在 `tests/test_video_editor_runtime.py` 中新增：

```python
from pathlib import Path


def test_video_editor_loader_reads_project_sequence_clip_export_data():
    text = Path("desktop_app/assets/js/page-loaders/video-editor-main.js").read_text(encoding="utf-8")
    assert "api.videoProjects.list()" in text
    assert "api.videoSequences.list(" in text
    assert "api.videoClips.list(" in text
    assert "api.videoSubtitles.list(" in text
    assert "api.videoExports.list(" in text


def test_video_editor_avoids_full_route_rerender_for_clip_edits():
    text = Path("desktop_app/assets/js/page-loaders/video-editor-main.js").read_text(encoding="utf-8")
    assert "renderRoute('video-editor')" not in text
    assert "loaders['video-editor']();" not in text


def test_video_editor_runtime_summary_is_real_project_based():
    text = Path("desktop_app/assets/js/page-loaders/video-editor-main.js").read_text(encoding="utf-8")
    assert "runtimeSummaryHandlers['video-editor']" in text
```

- [ ] **Step 2: 运行运行时测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_runtime.py -v
```

Expected: FAIL。

- [ ] **Step 3: 实现真实工程驱动 loader**

`video-editor-main.js` 需实现以下最小链路：

```js
api.videoProjects.list()
api.videoProjects.get(projectId)
api.videoSequences.list(projectId)
api.videoClips.list(sequenceId)
api.videoSubtitles.list(sequenceId)
api.videoExports.list(projectId)
api.assets.list()
```

并满足：

- 页面首屏分批加载
- 片段 / 字幕改动后只局部更新 DOM
- 选中素材时更新 `#mainHost` 内预览宿主
- 通过 `runtimeSummaryHandlers['video-editor']` 回写真实摘要

- [ ] **Step 4: 回跑运行时测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_runtime.py tests/test_page_runtime_data.py -v
```

Expected: PASS。

---

### Task 9: 收口 `visual-editor` 为静态视觉编辑器

**Files:**
- Modify: `desktop_app/assets/js/page-loaders/visual-editor-main.js`
- Modify: `desktop_app/assets/js/bindings/visual-editor-bindings.js`
- Modify: `desktop_app/assets/js/routes.js`
- Modify: `tests/test_video_editor_runtime.py`

- [ ] **Step 1: 写 `visual-editor` 职责收口失败测试**

在 `tests/test_video_editor_runtime.py` 中追加：

```python
def test_visual_editor_does_not_use_sequence_clip_export_language():
    text = Path("desktop_app/assets/js/routes.js").read_text(encoding="utf-8")
    assert "视频时间线语义" not in text
    assert "封面、图文卡片和素材拼合" in text
```

- [ ] **Step 2: 运行收口测试确认失败或不稳定**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_runtime.py -k "visual_editor" -v
```

Expected: FAIL 或现有实现不满足新的职责边界。

- [ ] **Step 3: 调整 `visual-editor` loader 与绑定**

要求：

- 只保留封面 / 图文 / 模板 / 多尺寸导出语义
- 不引用 `sequence`、`clip`、`subtitle`、`export job` 数据模型
- 若需要导出，仍走静态设计稿导出链路

- [ ] **Step 4: 回跑 `visual-editor` 收口测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_runtime.py -k "visual_editor" -v
```

Expected: PASS。

---

### Task 10: 接入 FFmpeg 打包与构建校验

**Files:**
- Modify: `tk_ops.spec`
- Modify: `build.py`
- Modify: `installer.iss`
- Create: `tools/ffmpeg/win64/ffmpeg.exe`
- Create: `tools/ffmpeg/win64/ffprobe.exe`
- Modify: `tests/test_video_editor_packaging.py`

- [ ] **Step 1: 先写打包与路径解析失败测试**

在 `tests/test_video_editor_packaging.py` 中新增：

```python
from pathlib import Path


def test_tk_ops_spec_packages_ffmpeg_binaries():
    text = Path("tk_ops.spec").read_text(encoding="utf-8")
    assert "tools/ffmpeg" in text


def test_build_helper_checks_ffmpeg_binaries():
    text = Path("build.py").read_text(encoding="utf-8")
    assert "ffmpeg.exe" in text
    assert "ffprobe.exe" in text
```

- [ ] **Step 2: 运行打包测试确认失败**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_packaging.py -v
```

Expected: FAIL。

- [ ] **Step 3: 修改打包入口**

要求：

- `tk_ops.spec` 将 `tools/ffmpeg/win64` 目录纳入 `datas` 或 `binaries`
- `build.py` 在构建前检查 `ffmpeg.exe` / `ffprobe.exe` 是否存在
- `installer.iss` 保持 `dist\TK-OPS\*` 全量收集，不再单独遗漏媒体二进制

- [ ] **Step 4: 回跑打包测试确认通过**

Run:

```powershell
venv\Scripts\python.exe -m pytest tests/test_video_editor_packaging.py tests/test_version_consistency.py -v
```

Expected: PASS。

---

### Task 11: 全量验证、性能回归与文档同步

**Files:**
- Modify: `README.md`（如需补视频剪辑说明）
- Modify: `docs/superpowers/specs/2026-03-30-video-editor-and-loader-split-design.md`（如执行中有微调）
- Test: `tests/test_video_editor_loader_split.py`
- Test: `tests/test_video_editor_models.py`
- Test: `tests/test_video_editing_service.py`
- Test: `tests/test_video_export_service.py`
- Test: `tests/test_video_editor_bridge_contract.py`
- Test: `tests/test_video_editor_runtime.py`
- Test: `tests/test_video_editor_packaging.py`

- [ ] **Step 1: 运行视频剪辑相关 focused 回归**

Run:

```powershell
venv\Scripts\python.exe -m pytest `
  tests/test_video_editor_loader_split.py `
  tests/test_video_editor_models.py `
  tests/test_video_editing_service.py `
  tests/test_video_export_service.py `
  tests/test_video_editor_bridge_contract.py `
  tests/test_video_editor_runtime.py `
  tests/test_video_editor_packaging.py -v
```

Expected: PASS。

- [ ] **Step 2: 运行主链路前端/Bridge 回归**

Run:

```powershell
venv\Scripts\python.exe -m pytest `
  tests/test_page_runtime_data.py `
  tests/test_bridge_runtime_contract.py `
  tests/test_crud_interaction_matrix.py `
  tests/test_page_interaction_audit.py -v
```

Expected: PASS。

- [ ] **Step 3: 做桌面应用启动与基础导出验证**

Run:

```powershell
venv\Scripts\python.exe desktop_app\main.py
```

人工验证清单：

- `video-editor` 首屏不出现明显卡顿
- 新建工程后可添加素材、修改入点 / 出点、编辑字幕、添加音频
- 保存后重新进入页面可恢复工程
- 导出时 UI 不冻结
- 导出成功后能看到真实输出文件

- [ ] **Step 4: 记录性能检查结果**

至少记录以下观察结果：

- 页面首屏加载时间是否明显小于当前版本
- 素材多时是否仍发生整页闪烁
- 导出进行中是否仍可切换页面
- `data:changed` 是否只触发局部更新而不是重进路由

- [ ] **Step 5: 同步文档与提交**

提交建议拆为 4 组：

```text
feat: add video editor persistence models and services
feat: add ffmpeg export runtime and bridge contracts
refactor: split editor factories bindings and page loaders
test: cover video editor runtime export and packaging
```

---

## Self-Review

### Spec Coverage

- `video-editor` 基础剪辑闭环：Task 2 / 3 / 4 / 8
- `visual-editor` 职责收口：Task 6 / 9
- `page-loaders.js` 等大文件拆分：Task 6 / 7
- `ffmpeg` 接入与打包：Task 4 / 10
- 性能与卡顿优化：Task 8 / 11
- 测试与验收：Task 1 / 2 / 3 / 4 / 5 / 8 / 10 / 11

### Placeholder Scan

- 未使用 `TBD` / `TODO` / “后续补” 等占位语
- 各任务都有明确文件、测试与命令

### Type Consistency

固定命名如下，不得在执行中更改：

- `VideoEditingService`
- `VideoExportService`
- `resolve_ffmpeg_binaries`
- `listVideoProjects`
- `appendAssetsToSequence`
- `createVideoExport`
- `video-editor-main.js`
- `visual-editor-main.js`


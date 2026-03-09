from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnusedCallResult=false, reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false

"""媒体相关 UI 组件。"""

from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Iterable, NamedTuple

from ...core.qt import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, Qt, Signal
from ...core.theme.tokens import STATIC_TOKENS, get_token_value
from ...core.types import ThemeMode


class _BaseLayout:
    """布局占位基类。"""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self._items: list[object] = []

    def setContentsMargins(self, *_args: int) -> None:
        return None

    def setSpacing(self, _value: int) -> None:
        return None

    def addWidget(self, widget: QWidget, *_args: int) -> None:
        self._items.append(widget)

    def addLayout(self, layout: object, *_args: int) -> None:
        self._items.append(layout)

    def addStretch(self, *_args: int) -> None:
        return None


class _FallbackGridLayout(_BaseLayout):
    """网格布局占位实现。"""

    def setHorizontalSpacing(self, _value: int) -> None:
        return None

    def setVerticalSpacing(self, _value: int) -> None:
        return None

    def removeWidget(self, widget: QWidget) -> None:
        if widget in self._items:
            self._items.remove(widget)


class _FallbackSlider(QWidget):
    """滑杆占位实现。"""

    valueChanged: Signal = Signal(int)

    def __init__(self, _orientation: object | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 100
        self._value = 0

    def setRange(self, minimum: int, maximum: int) -> None:
        self._minimum = minimum
        self._maximum = maximum

    def setValue(self, value: int) -> None:
        next_value = max(self._minimum, min(value, self._maximum))
        if next_value == self._value:
            return
        self._value = next_value
        self.valueChanged.emit(self._value)

    def value(self) -> int:
        return self._value


class _FallbackProgressBar(QWidget):
    """进度条占位实现。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 100
        self._value = 0

    def setRange(self, minimum: int, maximum: int) -> None:
        self._minimum = minimum
        self._maximum = maximum

    def setValue(self, value: int) -> None:
        self._value = max(self._minimum, min(value, self._maximum))


class _FallbackFileDialog:
    """文件对话框占位实现。"""

    @staticmethod
    def getOpenFileNames(
        _parent: QWidget | None = None,
        _caption: str = "",
        _directory: str = "",
        _filter_text: str = "",
    ) -> tuple[list[str], str]:
        return [], ""


def _resolve_optional_widget(name: str, fallback: type[object]) -> type[object]:
    """动态解析可选 Qt Widget。"""

    try:
        module = import_module("PySide6.QtWidgets")
    except Exception:
        return fallback
    resolved = getattr(module, name, None)
    if isinstance(resolved, type):
        return resolved
    return fallback


QGridLayout = _resolve_optional_widget("QGridLayout", _FallbackGridLayout)
QSlider = _resolve_optional_widget("QSlider", _FallbackSlider)
QProgressBar = _resolve_optional_widget("QProgressBar", _FallbackProgressBar)
QFileDialog = _resolve_optional_widget("QFileDialog", _FallbackFileDialog)

THUMBNAIL_SIZE = 160


class _Palette(NamedTuple):
    """媒体组件调色板。"""

    surface_primary: str
    surface_secondary: str
    surface_sunken: str
    text_primary: str
    text_secondary: str
    text_tertiary: str
    border_default: str
    border_strong: str
    border_focus: str
    brand_primary: str
    brand_secondary: str
    status_success: str
    status_warning: str
    status_error: str


def _palette(mode: ThemeMode) -> _Palette:
    """读取媒体组件所需 token。"""

    return _Palette(
        get_token_value("surface.primary", mode),
        get_token_value("surface.secondary", mode),
        get_token_value("surface.sunken", mode),
        get_token_value("text.primary", mode),
        get_token_value("text.secondary", mode),
        get_token_value("text.tertiary", mode),
        get_token_value("border.default", mode),
        get_token_value("border.strong", mode),
        get_token_value("border.focus", mode),
        get_token_value("brand.primary", mode),
        get_token_value("brand.secondary", mode),
        get_token_value("status.success", mode),
        get_token_value("status.warning", mode),
        get_token_value("status.error", mode),
    )


def _token_px(name: str) -> int:
    """解析 px token。"""

    raw = STATIC_TOKENS.get(name, "0px")
    text = str(raw).split("/")[0].strip().split()[0]
    return int(float(text[:-2])) if text.endswith("px") else 0


def _safe_call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_like: object, callback: object) -> None:
    """安全连接信号。"""

    method = getattr(signal_like, "connect", None)
    if callable(method):
        method(callback)


def _qt_flag(group_name: str, name: str, default: int = 0) -> object:
    """安全读取 Qt 常量。"""

    group = getattr(Qt, group_name, None)
    value = getattr(group, name, None) if group is not None else None
    if value is not None:
        return value
    direct = getattr(Qt, name, None)
    if direct is not None:
        return direct
    return default


def _format_bytes(size_bytes: int | None) -> str:
    """格式化文件大小。"""

    if size_bytes is None:
        return "未知大小"
    units = ("B", "KB", "MB", "GB")
    value = float(max(size_bytes, 0))
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1
    if index == 0:
        return f"{int(value)} {units[index]}"
    return f"{value:.1f} {units[index]}"


def _file_size(file_path: str) -> int | None:
    """读取文件体积。"""

    try:
        return Path(file_path).stat().st_size
    except OSError:
        return None


def _created_text(file_path: str) -> str:
    """读取文件创建时间。"""

    try:
        created_at = Path(file_path).stat().st_ctime
    except OSError:
        return "未知时间"
    return datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M")


def _is_image(file_path: str) -> bool:
    """判断是否为图片。"""

    return Path(file_path).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def _is_video(file_path: str) -> bool:
    """判断是否为视频。"""

    return Path(file_path).suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def _load_pixmap(file_path: str) -> object | None:
    """尝试加载图片对象。"""

    try:
        module = import_module("PySide6.QtGui")
        pixmap_class = getattr(module, "QPixmap")
        pixmap = pixmap_class(file_path)
    except Exception:
        return None
    is_null = getattr(pixmap, "isNull", None)
    if callable(is_null) and bool(is_null()):
        return None
    return pixmap


def _scaled_pixmap(pixmap: object, width: int, height: int) -> object:
    """按比例缩放 pixmap。"""

    scaled = getattr(pixmap, "scaled", None)
    if callable(scaled):
        return scaled(
            width,
            height,
            _qt_flag("AspectRatioMode", "KeepAspectRatio", 1),
            _qt_flag("TransformationMode", "SmoothTransformation", 0),
        )
    return pixmap


def _media_dimensions(file_path: str) -> str:
    """获取媒体尺寸文本。"""

    pixmap = _load_pixmap(file_path)
    if pixmap is None:
        return "-- × --"
    width_getter = getattr(pixmap, "width", None)
    height_getter = getattr(pixmap, "height", None)
    if callable(width_getter) and callable(height_getter):
        return f"{width_getter()} × {height_getter()}"
    return "-- × --"


def _drop_paths(event: object) -> list[str]:
    """从拖拽事件提取文件路径。"""

    mime_data = _safe_call(event, "mimeData")
    urls = _safe_call(mime_data, "urls")
    if not isinstance(urls, list):
        return []
    paths: list[str] = []
    for url in urls:
        method = getattr(url, "toLocalFile", None)
        if callable(method):
            local_path = method()
            if isinstance(local_path, str) and local_path:
                paths.append(local_path)
    return paths


def _open_file_names(parent: QWidget | None) -> list[str]:
    """安全打开文件选择框并返回文件列表。"""

    method = getattr(QFileDialog, "getOpenFileNames", None)
    if not callable(method):
        return []
    result = method(parent, "选择素材文件", "", "所有文件 (*.*)")
    if not isinstance(result, tuple) or not result:
        return []
    selected = result[0]
    if isinstance(selected, (list, tuple)):
        return [item for item in selected if isinstance(item, str)]
    return []


def _kind_text(file_path: str) -> str:
    """返回文件类型文案。"""

    if _is_image(file_path):
        return "图片"
    if _is_video(file_path):
        return "视频"
    return "文件"


class _SelectionButton(QPushButton):
    """右上角选择按钮。"""

    toggled: Signal = Signal(bool)

    def __init__(self, theme_mode: ThemeMode = ThemeMode.LIGHT, parent: QWidget | None = None) -> None:
        super().__init__("○", parent)
        self._palette = _palette(theme_mode)
        self._checked = False
        _safe_call(self, "setCheckable", True)
        _safe_call(self, "setFixedSize", 28, 28)
        _connect(getattr(self, "clicked", None), self.toggle_checked)
        self._apply_style()

    def is_checked(self) -> bool:
        """返回当前选择状态。"""

        return self._checked

    def set_checked(self, checked: bool) -> None:
        """设置当前选择状态。"""

        self._checked = checked
        _safe_call(self, "setText", "✓" if checked else "○")
        self._apply_style()

    def toggle_checked(self, *_args: object) -> None:
        """切换当前选择状态。"""

        self.set_checked(not self._checked)
        self.toggled.emit(self._checked)

    def _apply_style(self) -> None:
        """刷新按钮样式。"""

        background = self._palette.brand_primary if self._checked else "rgba(15,23,42,0.65)"
        foreground = self._palette.brand_secondary if self._checked else self._palette.surface_secondary
        _safe_call(
            self,
            "setStyleSheet",
            (
                f"background-color: {background};"
                f"color: {foreground};"
                f"border: 1px solid {self._palette.border_focus};"
                f"border-radius: {STATIC_TOKENS['radius.pill']};"
                f"font-size: {STATIC_TOKENS['font.size.sm']};"
                f"font-weight: {STATIC_TOKENS['font.weight.bold']};"
            ),
        )


class _VideoCanvas(QWidget):
    """视频占位绘制区域。"""

    def __init__(self, theme_mode: ThemeMode = ThemeMode.LIGHT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = _palette(theme_mode)
        _safe_call(self, "setMinimumHeight", 280)
        _safe_call(
            self,
            "setStyleSheet",
            (
                f"background-color: {self._palette.brand_secondary};"
                f"border: 1px solid {self._palette.border_default};"
                f"border-radius: {STATIC_TOKENS['radius.lg']};"
            ),
        )

    def paintEvent(self, event: object) -> None:
        """绘制暗色视频占位区。"""

        del event
        try:
            module = import_module("PySide6.QtGui")
            painter_class = getattr(module, "QPainter")
            color_class = getattr(module, "QColor")
        except Exception:
            return
        painter = painter_class(self)
        rect = _safe_call(self, "rect")
        if rect is None:
            return
        render_hint = getattr(painter_class, "Antialiasing", None)
        if render_hint is not None:
            painter.setRenderHint(render_hint, True)
        painter.fillRect(rect, color_class(self._palette.brand_secondary))
        painter.setPen(color_class(self._palette.brand_primary))
        font = painter.font()
        font.setPointSize(42)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, _qt_flag("AlignmentFlag", "AlignCenter", 0), "▶")
        painter.end()


class ThumbnailCard(QFrame):
    """单个图片或视频缩略卡片。"""

    selection_changed: Signal = Signal(str, bool)
    double_clicked: Signal = Signal(str)

    def __init__(
        self,
        file_path: str,
        *,
        duration: str = "",
        status: str = "ready",
        theme_mode: ThemeMode = ThemeMode.LIGHT,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._file_path = file_path
        self._duration = duration
        self._status = status
        self._palette = _palette(theme_mode)
        self._status_label = QLabel("", self)
        self._preview_label = QLabel("", self)
        self._filename_label = QLabel(Path(file_path).name or "未命名素材", self)
        self._meta_label = QLabel("", self)
        self._selection_button = _SelectionButton(theme_mode, self)
        _safe_call(self, "setObjectName", "thumbnailCard")
        self._build_ui()
        self._refresh_content()
        self._apply_style()

    def _build_ui(self) -> None:
        """构建卡片布局。"""

        spacing_md = _token_px("spacing.md")
        spacing_lg = _token_px("spacing.lg")
        root = QVBoxLayout(self)
        root.setContentsMargins(spacing_lg, spacing_lg, spacing_lg, spacing_lg)
        root.setSpacing(spacing_md)

        preview_frame = QFrame(self)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(spacing_md, spacing_md, spacing_md, spacing_md)
        preview_layout.setSpacing(spacing_md)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(spacing_md)
        header_layout.addWidget(self._status_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self._selection_button)
        _safe_call(preview_layout, "addLayout", header_layout)

        _safe_call(self._preview_label, "setMinimumSize", THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        _safe_call(self._preview_label, "setMaximumSize", THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        _safe_call(self._preview_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
        preview_layout.addWidget(self._preview_label)
        root.addWidget(preview_frame)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(spacing_md, 0, spacing_md, spacing_md)
        info_layout.setSpacing(_token_px("spacing.xs"))
        _safe_call(self._filename_label, "setWordWrap", True)
        info_layout.addWidget(self._filename_label)
        info_layout.addWidget(self._meta_label)
        _safe_call(root, "addLayout", info_layout)

        _connect(self._selection_button.toggled, self._on_toggled)

    def _status_text(self) -> tuple[str, str]:
        """返回状态文案与颜色。"""

        if self._status == "processing":
            return "处理中", self._palette.status_warning
        if self._status == "error":
            return "异常", self._palette.status_error
        return "已就绪", self._palette.status_success

    def _refresh_content(self) -> None:
        """刷新卡片预览与信息。"""

        status_text, _ = self._status_text()
        self._status_label.setText(status_text)
        parts = [_format_bytes(_file_size(self._file_path)), _kind_text(self._file_path)]
        if self._duration:
            parts.insert(1, self._duration)
        self._meta_label.setText(" · ".join(parts))

        pixmap = _load_pixmap(self._file_path) if _is_image(self._file_path) else None
        if pixmap is not None:
            _safe_call(self._preview_label, "setPixmap", _scaled_pixmap(pixmap, THUMBNAIL_SIZE, THUMBNAIL_SIZE))
            self._preview_label.setText("")
        else:
            placeholder = "视频缩略图" if _is_video(self._file_path) else "图片缩略图"
            _safe_call(self._preview_label, "clear")
            self._preview_label.setText(placeholder)

    def _apply_style(self) -> None:
        """应用卡片样式。"""

        _, status_color = self._status_text()
        _safe_call(self._status_label, "setProperty", "role", "status")
        _safe_call(self._meta_label, "setProperty", "role", "meta")
        _safe_call(self._preview_label, "setProperty", "role", "preview")
        _safe_call(
            self,
            "setStyleSheet",
            f"""
            QFrame#thumbnailCard {{
                background-color: {self._palette.surface_secondary};
                border: 1px solid {self._palette.border_default};
                border-radius: {STATIC_TOKENS['radius.lg']};
            }}
            QFrame#thumbnailCard:hover {{
                border-color: {self._palette.border_focus};
                background-color: {self._palette.surface_primary};
            }}
            QFrame#thumbnailCard QLabel {{
                color: {self._palette.text_primary};
                font-family: {STATIC_TOKENS['font.family.chinese']};
            }}
            QFrame#thumbnailCard QLabel[role="meta"] {{
                color: {self._palette.text_secondary};
                font-size: {STATIC_TOKENS['font.size.sm']};
            }}
            QFrame#thumbnailCard QLabel[role="status"] {{
                color: {status_color};
                background-color: rgba(0,242,234,0.10);
                border-radius: {STATIC_TOKENS['radius.sm']};
                padding: 2px 8px;
                font-size: {STATIC_TOKENS['font.size.xs']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            QFrame#thumbnailCard QLabel[role="preview"] {{
                background-color: {self._palette.surface_sunken};
                color: {self._palette.text_secondary};
                border: 1px dashed {self._palette.border_strong};
                border-radius: {STATIC_TOKENS['radius.md']};
                font-size: {STATIC_TOKENS['font.size.md']};
            }}
            """
        )

    def file_path(self) -> str:
        """返回素材路径。"""

        return self._file_path

    def is_selected(self) -> bool:
        """返回选中状态。"""

        return self._selection_button.is_checked()

    def set_selected(self, selected: bool) -> None:
        """设置选中状态。"""

        self._selection_button.set_checked(selected)

    def set_status(self, status: str) -> None:
        """更新处理状态。"""

        self._status = status
        self._refresh_content()
        self._apply_style()

    def set_duration(self, duration: str) -> None:
        """更新视频时长。"""

        self._duration = duration
        self._refresh_content()

    def _on_toggled(self, checked: bool) -> None:
        """转发选择变化。"""

        self.selection_changed.emit(self._file_path, checked)

    def mouseDoubleClickEvent(self, event: object) -> None:
        """双击时发出预览信号。"""

        del event
        self.double_clicked.emit(self._file_path)


class ImageGrid(QWidget):
    """图片素材网格。"""

    selection_changed: Signal = Signal(object)
    item_double_clicked: Signal = Signal(str)

    def __init__(
        self,
        image_paths: Iterable[str] | None = None,
        *,
        columns: int = 4,
        theme_mode: ThemeMode = ThemeMode.LIGHT,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._columns = max(1, columns)
        self._theme_mode = theme_mode
        self._cards: list[ThumbnailCard] = []
        self._selected_paths: list[str] = []
        self._grid_widget = QWidget(self)
        self._grid_layout = QGridLayout()
        _safe_call(self, "setObjectName", "imageGrid")
        self._build_ui()
        if image_paths is not None:
            self.set_items(image_paths)

    def _build_ui(self) -> None:
        """构建网格布局。"""

        root = QVBoxLayout(self)
        gap = _token_px("spacing.xl")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(gap)
        _safe_call(self._grid_layout, "setContentsMargins", 0, 0, 0, 0)
        _safe_call(self._grid_layout, "setHorizontalSpacing", gap)
        _safe_call(self._grid_layout, "setVerticalSpacing", gap)
        _safe_call(self._grid_widget, "setLayout", self._grid_layout)
        root.addWidget(self._grid_widget)
        _safe_call(self, "setStyleSheet", "#imageGrid { background-color: transparent; }")

    def clear_items(self) -> None:
        """清空网格项。"""

        for card in self._cards:
            _safe_call(self._grid_layout, "removeWidget", card)
            _safe_call(card, "deleteLater")
        self._cards = []
        self._selected_paths = []
        self.selection_changed.emit([])

    def set_items(self, image_paths: Iterable[str]) -> None:
        """批量设置图片项。"""

        self.clear_items()
        for image_path in image_paths:
            self.add_item(image_path)

    def add_item(self, file_path: str, *, duration: str = "", status: str = "ready") -> None:
        """添加单个素材卡片。"""

        card = ThumbnailCard(file_path, duration=duration, status=status, theme_mode=self._theme_mode, parent=self._grid_widget)
        _connect(card.selection_changed, self._on_card_selection_changed)
        _connect(card.double_clicked, self._on_card_double_clicked)
        row = len(self._cards) // self._columns
        column = len(self._cards) % self._columns
        _safe_call(self._grid_layout, "addWidget", card, row, column)
        self._cards.append(card)

    def selected_paths(self) -> list[str]:
        """返回选中的素材路径。"""

        return list(self._selected_paths)

    def _on_card_selection_changed(self, file_path: str, checked: bool) -> None:
        """处理子卡片选择变化。"""

        if checked and file_path not in self._selected_paths:
            self._selected_paths.append(file_path)
        if not checked and file_path in self._selected_paths:
            self._selected_paths.remove(file_path)
        self.selection_changed.emit(list(self._selected_paths))

    def _on_card_double_clicked(self, file_path: str) -> None:
        """转发双击事件。"""

        self.item_double_clicked.emit(file_path)


class VideoPlayerWidget(QWidget):
    """视频播放器占位组件。"""

    def __init__(self, theme_mode: ThemeMode = ThemeMode.LIGHT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = _palette(theme_mode)
        self._is_playing = False
        self._duration_seconds = 30
        self._position_seconds = 0
        self._syncing_slider = False
        self._canvas = _VideoCanvas(theme_mode, self)
        self._play_button = QPushButton("播放", self)
        self._progress_slider = QSlider()
        _safe_call(self._progress_slider, "setOrientation", _qt_flag("Orientation", "Horizontal", 1))
        self._time_label = QLabel("00:00 / 00:30", self)
        _safe_call(self, "setObjectName", "videoPlayer")
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        """构建播放器界面。"""

        padding = _token_px("spacing.xl")
        root = QVBoxLayout(self)
        root.setContentsMargins(padding, padding, padding, padding)
        root.setSpacing(padding)
        root.addWidget(self._canvas)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(_token_px("spacing.lg"))
        _safe_call(self._progress_slider, "setRange", 0, self._duration_seconds)
        _safe_call(self._progress_slider, "setValue", self._position_seconds)
        controls.addWidget(self._play_button)
        _safe_call(controls, "addWidget", self._progress_slider)
        controls.addWidget(self._time_label)
        _safe_call(root, "addLayout", controls)

        _connect(getattr(self._play_button, "clicked", None), self.toggle_playback)
        _connect(getattr(self._progress_slider, "valueChanged", None), self.set_position)

    def _apply_style(self) -> None:
        """应用播放器样式。"""

        _safe_call(
            self,
            "setStyleSheet",
            f"""
            #videoPlayer {{
                background-color: {self._palette.surface_secondary};
                border: 1px solid {self._palette.border_default};
                border-radius: {STATIC_TOKENS['radius.lg']};
            }}
            #videoPlayer QLabel {{
                color: {self._palette.text_primary};
                font-family: {STATIC_TOKENS['font.family.chinese']};
            }}
            #videoPlayer QPushButton {{
                min-height: {STATIC_TOKENS['button.height.md']};
                padding: {STATIC_TOKENS['button.padding.compact']};
                color: {self._palette.brand_secondary};
                background-color: {self._palette.brand_primary};
                border: none;
                border-radius: {STATIC_TOKENS['radius.md']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            """
        )

    def toggle_playback(self, *_args: object) -> None:
        """切换播放与暂停。"""

        self._is_playing = not self._is_playing
        _safe_call(self._play_button, "setText", "暂停" if self._is_playing else "播放")

    def set_duration(self, seconds: int) -> None:
        """设置总时长。"""

        self._duration_seconds = max(1, seconds)
        _safe_call(self._progress_slider, "setRange", 0, self._duration_seconds)
        self._refresh_time_text()

    def set_position(self, seconds: int) -> None:
        """设置当前进度。"""

        next_value = max(0, min(seconds, self._duration_seconds))
        self._position_seconds = next_value
        if not self._syncing_slider:
            current_value = _safe_call(self._progress_slider, "value")
            if current_value != next_value:
                self._syncing_slider = True
                _safe_call(self._progress_slider, "setValue", next_value)
                self._syncing_slider = False
        self._refresh_time_text()

    def _refresh_time_text(self) -> None:
        """刷新时间显示。"""

        current = f"{self._position_seconds // 60:02d}:{self._position_seconds % 60:02d}"
        total = f"{self._duration_seconds // 60:02d}:{self._duration_seconds % 60:02d}"
        self._time_label.setText(f"{current} / {total}")


class FileUploaderWidget(QFrame):
    """文件选择与上传展示组件。"""

    files_selected: Signal = Signal(object)

    def __init__(self, theme_mode: ThemeMode = ThemeMode.LIGHT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = _palette(theme_mode)
        self._selected_files: list[str] = []
        self._browse_button = QPushButton("选择文件", self)
        self._summary_label = QLabel("尚未选择文件", self)
        self._progress_bar = QProgressBar()
        _safe_call(self, "setObjectName", "fileUploader")
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        """构建上传器结构。"""

        padding = _token_px("spacing.xl")
        root = QVBoxLayout(self)
        root.setContentsMargins(padding, padding, padding, padding)
        root.setSpacing(padding)
        title = QLabel("批量上传素材", self)
        hint = QLabel("支持多选文件，可用于素材工厂、素材中心与视觉编辑器。", self)
        _safe_call(hint, "setWordWrap", True)
        _safe_call(self._summary_label, "setWordWrap", True)
        root.addWidget(title)
        root.addWidget(hint)
        root.addWidget(self._browse_button)
        root.addWidget(self._summary_label)
        _safe_call(self._progress_bar, "setRange", 0, 100)
        _safe_call(self._progress_bar, "setValue", 0)
        _safe_call(root, "addWidget", self._progress_bar)
        _connect(getattr(self._browse_button, "clicked", None), self.open_file_dialog)

    def _apply_style(self) -> None:
        """应用上传器样式。"""

        _safe_call(
            self,
            "setStyleSheet",
            f"""
            #fileUploader {{
                background-color: {self._palette.surface_secondary};
                border: 1px solid {self._palette.border_default};
                border-radius: {STATIC_TOKENS['radius.lg']};
            }}
            #fileUploader QLabel {{
                color: {self._palette.text_primary};
                font-family: {STATIC_TOKENS['font.family.chinese']};
            }}
            #fileUploader QPushButton {{
                min-height: {STATIC_TOKENS['button.height.md']};
                padding: {STATIC_TOKENS['button.padding.compact']};
                color: {self._palette.brand_secondary};
                background-color: {self._palette.brand_primary};
                border: none;
                border-radius: {STATIC_TOKENS['radius.md']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            """
        )

    def open_file_dialog(self, *_args: object) -> None:
        """打开文件选择框。"""

        selected_files = _open_file_names(self)
        if selected_files:
            self.set_selected_files(selected_files)

    def set_selected_files(self, files: Iterable[str]) -> None:
        """设置选中的文件列表。"""

        self._selected_files = list(files)
        self._refresh_summary()
        self.set_upload_progress(0)
        self.files_selected.emit(list(self._selected_files))

    def selected_files(self) -> list[str]:
        """返回当前文件列表。"""

        return list(self._selected_files)

    def set_upload_progress(self, value: int) -> None:
        """设置上传进度。"""

        _safe_call(self._progress_bar, "setValue", max(0, min(100, value)))

    def _refresh_summary(self) -> None:
        """刷新文件信息。"""

        if not self._selected_files:
            self._summary_label.setText("尚未选择文件")
            return
        lines: list[str] = []
        for file_path in self._selected_files:
            path = Path(file_path)
            lines.append(f"{path.name} · {_format_bytes(_file_size(file_path))} · {path.suffix.lower() or '未知类型'}")
        self._summary_label.setText("\n".join(lines))


class DragDropZone(QFrame):
    """支持拖拽文件的落区组件。"""

    files_dropped: Signal = Signal(object)

    def __init__(self, theme_mode: ThemeMode = ThemeMode.LIGHT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = _palette(theme_mode)
        self._drag_active = False
        self._icon_label = QLabel("⬆", self)
        self._title_label = QLabel("拖拽文件到此处", self)
        self._hint_label = QLabel("支持图片、视频与常见素材文件", self)
        _safe_call(self, "setObjectName", "dragDropZone")
        _safe_call(self, "setAcceptDrops", True)
        self._build_ui()
        self._apply_style()

    def _build_ui(self) -> None:
        """构建拖拽区结构。"""

        root = QVBoxLayout(self)
        root.setContentsMargins(_token_px("spacing.3xl"), _token_px("spacing.3xl"), _token_px("spacing.3xl"), _token_px("spacing.3xl"))
        root.setSpacing(_token_px("spacing.lg"))
        root.addStretch(1)
        _safe_call(self._icon_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
        _safe_call(self._title_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
        _safe_call(self._hint_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
        root.addWidget(self._icon_label)
        root.addWidget(self._title_label)
        root.addWidget(self._hint_label)
        root.addStretch(1)
        _safe_call(self, "setMinimumHeight", 240)

    def _apply_style(self) -> None:
        """根据拖拽状态刷新样式。"""

        border_color = self._palette.brand_primary if self._drag_active else self._palette.border_strong
        background = self._palette.surface_primary if self._drag_active else self._palette.surface_secondary
        _safe_call(
            self,
            "setStyleSheet",
            f"""
            #dragDropZone {{
                background-color: {background};
                border: 2px dashed {border_color};
                border-radius: {STATIC_TOKENS['radius.xl']};
            }}
            #dragDropZone QLabel {{
                background: transparent;
                color: {self._palette.text_primary};
                font-family: {STATIC_TOKENS['font.family.chinese']};
            }}
            """
        )

    def dragEnterEvent(self, event: object) -> None:
        """处理拖拽进入。"""

        paths = _drop_paths(event)
        if paths:
            self._drag_active = True
            self._apply_style()
            _safe_call(event, "acceptProposedAction")
            return
        _safe_call(event, "ignore")

    def dragLeaveEvent(self, event: object) -> None:
        """处理拖拽离开。"""

        del event
        self._drag_active = False
        self._apply_style()

    def dropEvent(self, event: object) -> None:
        """处理拖拽释放。"""

        self._drag_active = False
        self._apply_style()
        paths = _drop_paths(event)
        if paths:
            self.files_dropped.emit(paths)
            _safe_call(event, "acceptProposedAction")
            return
        _safe_call(event, "ignore")


class MediaPreview(QDialog):
    """媒体预览弹窗。"""

    def __init__(self, file_path: str | None = None, theme_mode: ThemeMode = ThemeMode.LIGHT, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette = _palette(theme_mode)
        self._current_file_path: str | None = None
        self._preview_label = QLabel("暂无可预览内容", self)
        self._file_name_label = QLabel("文件名：--", self)
        self._dimension_label = QLabel("尺寸：--", self)
        self._size_label = QLabel("大小：--", self)
        self._created_label = QLabel("创建时间：--", self)
        self._close_button = QPushButton("关闭", self)
        _safe_call(self, "setObjectName", "mediaPreview")
        _safe_call(self, "setWindowTitle", "媒体预览")
        self._build_ui()
        self._apply_style()
        if file_path:
            self.set_media(file_path)

    def _build_ui(self) -> None:
        """构建预览弹窗结构。"""

        spacing = _token_px("spacing.2xl")
        root = QHBoxLayout(self)
        root.setContentsMargins(spacing, spacing, spacing, spacing)
        root.setSpacing(spacing)

        preview_layout = QVBoxLayout()
        _safe_call(self._preview_label, "setMinimumSize", 640, 420)
        _safe_call(self._preview_label, "setAlignment", _qt_flag("AlignmentFlag", "AlignCenter", 0))
        preview_layout.addWidget(self._preview_label)

        info_panel = QFrame(self)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(spacing, spacing, spacing, spacing)
        info_layout.setSpacing(_token_px("spacing.lg"))
        info_layout.addWidget(QLabel("素材信息", self))
        info_layout.addWidget(self._file_name_label)
        info_layout.addWidget(self._dimension_label)
        info_layout.addWidget(self._size_label)
        info_layout.addWidget(self._created_label)
        info_layout.addStretch(1)
        info_layout.addWidget(self._close_button)

        _safe_call(root, "addLayout", preview_layout, 1)
        root.addWidget(info_panel)
        _connect(getattr(self._close_button, "clicked", None), self._handle_close)
        _safe_call(self, "resize", 1040, 620)

    def _apply_style(self) -> None:
        """应用预览弹窗样式。"""

        _safe_call(
            self,
            "setStyleSheet",
            f"""
            #mediaPreview {{
                background-color: {self._palette.surface_primary};
            }}
            #mediaPreview QLabel {{
                color: {self._palette.text_primary};
                font-family: {STATIC_TOKENS['font.family.chinese']};
            }}
            #mediaPreview QFrame {{
                background-color: {self._palette.surface_secondary};
                border: 1px solid {self._palette.border_default};
                border-radius: {STATIC_TOKENS['radius.lg']};
            }}
            #mediaPreview QPushButton {{
                min-height: {STATIC_TOKENS['button.height.md']};
                padding: {STATIC_TOKENS['button.padding.compact']};
                color: {self._palette.brand_secondary};
                background-color: {self._palette.brand_primary};
                border: none;
                border-radius: {STATIC_TOKENS['radius.md']};
                font-weight: {STATIC_TOKENS['font.weight.semibold']};
            }}
            """
        )
        _safe_call(
            self._preview_label,
            "setStyleSheet",
            (
                f"background-color: {self._palette.surface_secondary};"
                f"border: 1px solid {self._palette.border_default};"
                f"border-radius: {STATIC_TOKENS['radius.lg']};"
                f"color: {self._palette.text_secondary};"
            )
        )

    def _handle_close(self, *_args: object) -> None:
        """关闭弹窗。"""

        _safe_call(self, "close")

    def set_media(self, file_path: str) -> None:
        """设置预览媒体。"""

        self._current_file_path = file_path
        self._update_info(file_path)
        self._refresh_preview(file_path)

    def _update_info(self, file_path: str) -> None:
        """更新右侧信息栏。"""

        path = Path(file_path)
        self._file_name_label.setText(f"文件名：{path.name}")
        self._dimension_label.setText(f"尺寸：{_media_dimensions(file_path)}")
        self._size_label.setText(f"大小：{_format_bytes(_file_size(file_path))}")
        self._created_label.setText(f"创建时间：{_created_text(file_path)}")

    def _refresh_preview(self, file_path: str) -> None:
        """刷新媒体预览内容。"""

        if _is_image(file_path):
            pixmap = _load_pixmap(file_path)
            if pixmap is not None:
                _safe_call(self._preview_label, "setPixmap", _scaled_pixmap(pixmap, 900, 560))
                self._preview_label.setText("")
                return
        placeholder = "视频预览占位" if _is_video(file_path) else "暂不支持此文件预览"
        _safe_call(self._preview_label, "clear")
        self._preview_label.setText(placeholder)

    def resizeEvent(self, event: object) -> None:
        """尺寸变化时重绘当前预览。"""

        del event
        if self._current_file_path:
            self._refresh_preview(self._current_file_path)


__all__ = [
    "DragDropZone",
    "FileUploaderWidget",
    "ImageGrid",
    "MediaPreview",
    "ThumbnailCard",
    "VideoPlayerWidget",
]

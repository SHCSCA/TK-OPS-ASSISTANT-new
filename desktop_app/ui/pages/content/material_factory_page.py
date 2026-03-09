# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportAssignmentType=false

from __future__ import annotations

"""素材工厂页面。"""

from dataclasses import dataclass
from typing import Final, cast

from ....core.types import RouteId
from ...components import DangerButton, IconButton, ImageGrid, MediaPreview, PageContainer, PrimaryButton, SearchBar, FilterDropdown, SplitPanel, StatusBadge, TagChip
from ...components.tags import BadgeTone
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _format_total_size(total_mb: float) -> str:
    """格式化合计容量。"""

    if total_mb >= 1024:
        return f"{total_mb / 1024:.1f} GB"
    return f"{total_mb:.1f} MB"


def _clear_layout_items(layout: object) -> None:
    """兼容真实 Qt 与占位布局的清空逻辑。"""

    count_method = getattr(layout, "count", None)
    take_at_method = getattr(layout, "takeAt", None)
    if callable(count_method) and callable(take_at_method):
        while True:
            count_value = count_method()
            if not isinstance(count_value, int) or count_value <= 0:
                break
            item = take_at_method(0)
            if item is None:
                break
            widget_method = getattr(item, "widget", None)
            if callable(widget_method):
                widget = widget_method()
                if widget is not None:
                    _call(widget, "setParent", None)
                    _call(widget, "deleteLater")
        return

    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


@dataclass(frozen=True)
class MockMediaItem:
    """页面使用的模拟素材数据。"""

    media_id: str
    file_path: str
    name: str
    media_type: str
    category: str
    size_mb: float
    size_label: str
    resolution: str
    format_label: str
    frame_rate: str
    duration: str
    status: str
    tags: tuple[str, ...]
    accent: str

    @property
    def grid_meta(self) -> str:
        return f"{self.size_label} · {self.resolution}"


SIDEBAR_MIN_WIDTH: Final[int] = 344
PREVIEW_MIN_HEIGHT: Final[int] = 216
BATCH_BAR_MIN_HEIGHT: Final[int] = BUTTON_HEIGHT + SPACING_2XL + SPACING_LG


class MaterialFactoryPage(BasePage):
    """素材工厂，支持搜索、筛选、批量选择与详情预览。"""

    default_route_id: RouteId = RouteId("material_factory")
    default_display_name: str = "素材工厂"
    default_icon_name: str = "factory"

    def setup_ui(self) -> None:
        """构建素材工厂页面。"""

        self._all_media = self._build_mock_media()
        self._selected_media_ids: list[str] = [item.media_id for item in self._all_media[:4]]
        self._active_media_id = self._selected_media_ids[0]
        self._search_text = ""
        self._type_filter = "全部"
        self._view_mode = "grid"
        self._upload_sequence = 1
        self._filtered_media: list[MockMediaItem] = []
        self._grid_media_by_path: dict[str, str] = {}
        self._grid_widget: ImageGrid | None = None
        self._preview_dialog = MediaPreview(parent=self)
        self._updating_grid = False

        _call(self, "setObjectName", "materialFactoryPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._page_container = PageContainer(
            title=self.display_name,
            description="统一管理图片与视频素材，支持筛选、预览与批量处理。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._inventory_badge = StatusBadge(f"{len(self._all_media)} 个素材", tone="brand", parent=self._page_container)
        self._processing_badge = StatusBadge("批量处理就绪", tone="success", parent=self._page_container)
        self._page_container.add_action(self._inventory_badge)
        self._page_container.add_action(self._processing_badge)

        self._page_container.add_widget(self._build_top_toolbar())
        self._page_container.add_widget(self._build_workspace())
        self._page_container.add_widget(self._build_batch_bar())

        self._apply_filters()

    def _build_top_toolbar(self) -> QWidget:
        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "materialFactoryToolbar")
        _call(toolbar, "setProperty", "variant", "card")
        layout = QVBoxLayout(toolbar)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_LG)

        header_copy = QWidget(toolbar)
        header_copy_layout = QVBoxLayout(header_copy)
        header_copy_layout.setContentsMargins(0, 0, 0, 0)
        header_copy_layout.setSpacing(SPACING_XS)
        title_label = QLabel("素材检索与批处理", header_copy)
        _call(title_label, "setObjectName", "materialFactoryToolbarTitle")
        subtitle_label = QLabel("统一搜索、切换视图并快速上传新素材，保持与素材工厂详情区一致的操作节奏。", header_copy)
        _call(subtitle_label, "setObjectName", "materialFactoryToolbarSubtitle")
        _call(subtitle_label, "setWordWrap", True)
        header_copy_layout.addWidget(title_label)
        header_copy_layout.addWidget(subtitle_label)

        header_badges = QWidget(toolbar)
        header_badges_layout = QHBoxLayout(header_badges)
        header_badges_layout.setContentsMargins(0, 0, 0, 0)
        header_badges_layout.setSpacing(SPACING_SM)
        header_badges_layout.addWidget(StatusBadge("素材库已同步", tone="success", parent=header_badges))
        header_badges_layout.addWidget(StatusBadge("支持批量处理", tone="info", parent=header_badges))

        header_row.addWidget(header_copy, 1)
        header_row.addWidget(header_badges)

        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(0, 0, 0, 0)
        controls_row.setSpacing(SPACING_LG)

        self._search_bar = SearchBar("搜索素材、标签或分类...", toolbar)
        self._type_dropdown = FilterDropdown("类型", ("视频", "图片", "封面"), include_all=True, parent=toolbar)
        self._grid_toggle_button = IconButton("▦", "网格视图", toolbar)
        self._list_toggle_button = IconButton("☰", "紧凑视图", toolbar)
        self._upload_button = PrimaryButton("上传素材", toolbar, icon_text="☁")

        controls_row.addWidget(self._search_bar, 1)
        controls_row.addWidget(self._type_dropdown)
        controls_row.addWidget(self._grid_toggle_button)
        controls_row.addWidget(self._list_toggle_button)
        controls_row.addStretch(1)
        controls_row.addWidget(self._upload_button)

        layout.addLayout(header_row)
        layout.addLayout(controls_row)

        _connect(self._search_bar.search_changed, self._handle_search_changed)
        _connect(self._type_dropdown.filter_changed, self._handle_type_filter_changed)
        _connect(getattr(self._grid_toggle_button, "clicked", None), self._handle_grid_view)
        _connect(getattr(self._list_toggle_button, "clicked", None), self._handle_list_view)
        _connect(getattr(self._upload_button, "clicked", None), self._handle_upload_clicked)
        self._refresh_view_toggle_styles()
        return toolbar

    def _build_workspace(self) -> QWidget:
        split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.76, 0.24),
            minimum_sizes=(SPACING_2XL * 24, SIDEBAR_MIN_WIDTH),
            parent=self,
        )
        split.set_first_widget(self._build_library_panel())
        split.set_second_widget(self._build_preview_panel())
        return split

    def _build_library_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        header = QFrame(panel)
        _call(header, "setObjectName", "materialFactoryLibraryHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_LG)

        title_wrap = QWidget(header)
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_XS)
        self._collection_title_label = QLabel("全部项目", title_wrap)
        _call(self._collection_title_label, "setObjectName", "materialFactoryCollectionTitle")
        self._collection_meta_label = QLabel("", title_wrap)
        _call(self._collection_meta_label, "setObjectName", "materialFactoryMutedText")
        title_layout.addWidget(self._collection_title_label)
        title_layout.addWidget(self._collection_meta_label)

        self._selection_hint_badge = StatusBadge("支持批量处理", tone="info", parent=header)

        header_layout.addWidget(title_wrap, 1)
        header_layout.addWidget(self._selection_hint_badge)

        self._grid_shell = QFrame(panel)
        _call(self._grid_shell, "setObjectName", "materialFactoryGridShell")
        self._grid_shell_layout = QVBoxLayout(self._grid_shell)
        self._grid_shell_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        self._grid_shell_layout.setSpacing(SPACING_LG)

        self._empty_state_label = QLabel("当前筛选条件下暂无素材，试试更换关键词或类型。", self._grid_shell)
        _call(self._empty_state_label, "setObjectName", "materialFactoryEmptyState")
        _call(self._empty_state_label, "setWordWrap", True)
        _call(self._empty_state_label, "setVisible", False)
        self._grid_shell_layout.addWidget(self._empty_state_label)

        layout.addWidget(header)
        layout.addWidget(self._grid_shell, 1)
        return panel

    def _build_preview_panel(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "materialFactoryPreviewPanel")
        _call(panel, "setProperty", "variant", "card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(SPACING_MD)
        title_icon = StatusBadge("预览", tone="brand", parent=panel)
        title_label = QLabel("素材详情", panel)
        _call(title_label, "setObjectName", "materialFactorySideTitle")
        title_row.addWidget(title_icon)
        title_row.addWidget(title_label)
        title_row.addStretch(1)

        self._preview_stage = QFrame(panel)
        _call(self._preview_stage, "setObjectName", "materialFactoryPreviewStage")
        _call(self._preview_stage, "setMinimumHeight", PREVIEW_MIN_HEIGHT)
        preview_layout = QVBoxLayout(self._preview_stage)
        preview_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        preview_layout.setSpacing(SPACING_MD)

        preview_top = QHBoxLayout()
        preview_top.setContentsMargins(0, 0, 0, 0)
        preview_top.setSpacing(SPACING_SM)
        self._preview_kind_badge = StatusBadge("视频", tone="info", parent=self._preview_stage)
        self._preview_status_badge = StatusBadge("已就绪", tone="success", parent=self._preview_stage)
        preview_top.addWidget(self._preview_kind_badge)
        preview_top.addWidget(self._preview_status_badge)
        preview_top.addStretch(1)

        self._preview_canvas = QLabel("", self._preview_stage)
        _call(self._preview_canvas, "setObjectName", "materialFactoryPreviewCanvas")
        _call(self._preview_canvas, "setMinimumHeight", PREVIEW_MIN_HEIGHT - (SPACING_XL * 2))
        _call(self._preview_canvas, "setWordWrap", True)

        self._preview_progress = QFrame(self._preview_stage)
        _call(self._preview_progress, "setObjectName", "materialFactoryPreviewProgress")
        _call(self._preview_progress, "setFixedHeight", SPACING_XS)

        preview_layout.addLayout(preview_top)
        preview_layout.addWidget(self._preview_canvas, 1)
        preview_layout.addWidget(self._preview_progress)

        self._detail_name_value = QLabel("--", panel)
        self._detail_name_caption = QLabel("文件名", panel)
        self._detail_format_value = QLabel("--", panel)
        self._detail_format_caption = QLabel("格式", panel)
        self._detail_resolution_value = QLabel("--", panel)
        self._detail_resolution_caption = QLabel("分辨率", panel)
        self._detail_size_value = QLabel("--", panel)
        self._detail_size_caption = QLabel("大小", panel)
        self._detail_fps_value = QLabel("--", panel)
        self._detail_fps_caption = QLabel("帧率", panel)
        self._detail_duration_value = QLabel("--", panel)
        self._detail_duration_caption = QLabel("时长", panel)

        self._tags_title = QLabel("标签", panel)
        _call(self._tags_title, "setObjectName", "materialFactoryMutedCaption")
        self._tags_host = QWidget(panel)
        self._tags_layout = QHBoxLayout(self._tags_host)
        self._tags_layout.setContentsMargins(0, 0, 0, 0)
        self._tags_layout.setSpacing(SPACING_XS)

        self._preview_open_button = PrimaryButton("打开预览", panel, icon_text="▶")
        self._download_button = QPushButton("立即下载", panel)
        _call(self._download_button, "setObjectName", "materialFactorySecondaryAction")
        self._share_button = QPushButton("共享素材", panel)
        _call(self._share_button, "setObjectName", "materialFactorySecondaryAction")

        layout.addLayout(title_row)
        layout.addWidget(self._preview_stage)
        layout.addWidget(self._build_detail_block(self._detail_name_caption, self._detail_name_value))
        layout.addWidget(self._build_detail_grid())
        layout.addWidget(self._tags_title)
        layout.addWidget(self._tags_host)
        layout.addStretch(1)
        layout.addWidget(self._preview_open_button)
        layout.addWidget(self._download_button)
        layout.addWidget(self._share_button)

        _connect(getattr(self._preview_open_button, "clicked", None), self._handle_open_preview)
        _connect(getattr(self._download_button, "clicked", None), self._handle_download_selected)
        _connect(getattr(self._share_button, "clicked", None), self._handle_share_selected)
        return panel

    def _build_detail_grid(self) -> QWidget:
        grid = QWidget(self)
        layout = QVBoxLayout(grid)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        first_row = QHBoxLayout()
        first_row.setContentsMargins(0, 0, 0, 0)
        first_row.setSpacing(SPACING_LG)
        first_row.addWidget(self._build_detail_block(self._detail_format_caption, self._detail_format_value), 1)
        first_row.addWidget(self._build_detail_block(self._detail_resolution_caption, self._detail_resolution_value), 1)

        second_row = QHBoxLayout()
        second_row.setContentsMargins(0, 0, 0, 0)
        second_row.setSpacing(SPACING_LG)
        second_row.addWidget(self._build_detail_block(self._detail_size_caption, self._detail_size_value), 1)
        second_row.addWidget(self._build_detail_block(self._detail_fps_caption, self._detail_fps_value), 1)

        third_row = QHBoxLayout()
        third_row.setContentsMargins(0, 0, 0, 0)
        third_row.setSpacing(SPACING_LG)
        third_row.addWidget(self._build_detail_block(self._detail_duration_caption, self._detail_duration_value), 1)
        third_row.addStretch(1)

        layout.addLayout(first_row)
        layout.addLayout(second_row)
        layout.addLayout(third_row)
        return grid

    def _build_detail_block(self, caption: QLabel, value: QLabel) -> QWidget:
        block = QWidget(self)
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XS)
        _call(caption, "setObjectName", "materialFactoryMutedCaption")
        _call(value, "setObjectName", "materialFactoryValueText")
        layout.addWidget(caption)
        layout.addWidget(value)
        return block

    def _build_batch_bar(self) -> QWidget:
        bar = QFrame(self)
        _call(bar, "setObjectName", "materialFactoryBatchBar")
        _call(bar, "setMinimumHeight", BATCH_BAR_MIN_HEIGHT)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_XL)

        summary_wrap = QWidget(bar)
        summary_layout = QHBoxLayout(summary_wrap)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_MD)

        self._batch_stack_wrap = QWidget(summary_wrap)
        self._batch_stack_layout = QHBoxLayout(self._batch_stack_wrap)
        self._batch_stack_layout.setContentsMargins(0, 0, 0, 0)
        self._batch_stack_layout.setSpacing(SPACING_XS)

        summary_text_wrap = QWidget(summary_wrap)
        summary_text_layout = QVBoxLayout(summary_text_wrap)
        summary_text_layout.setContentsMargins(0, 0, 0, 0)
        summary_text_layout.setSpacing(SPACING_XS)
        self._batch_title_label = QLabel("未选择素材", summary_text_wrap)
        _call(self._batch_title_label, "setObjectName", "materialFactoryBatchTitle")
        self._batch_meta_label = QLabel("选择素材后可执行一键去重、批量改尺寸与统一处理。", summary_text_wrap)
        _call(self._batch_meta_label, "setObjectName", "materialFactoryBatchMeta")
        summary_text_layout.addWidget(self._batch_title_label)
        summary_text_layout.addWidget(self._batch_meta_label)

        summary_layout.addWidget(self._batch_stack_wrap)
        summary_layout.addWidget(summary_text_wrap)

        actions_wrap = QWidget(bar)
        actions_layout = QHBoxLayout(actions_wrap)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACING_MD)

        self._dedupe_button = QPushButton("一键去重", actions_wrap)
        _call(self._dedupe_button, "setObjectName", "materialFactoryBatchAction")
        self._resize_button = QPushButton("批量改尺寸", actions_wrap)
        _call(self._resize_button, "setObjectName", "materialFactoryBatchAction")
        self._process_button = PrimaryButton("开始处理", actions_wrap)
        self._clear_button = DangerButton("清空选择", actions_wrap)
        self._dismiss_button = IconButton("✕", "隐藏批量栏", actions_wrap)

        actions_layout.addWidget(self._dedupe_button)
        actions_layout.addWidget(self._resize_button)
        actions_layout.addWidget(self._process_button)
        actions_layout.addWidget(self._clear_button)
        actions_layout.addWidget(self._dismiss_button)

        layout.addWidget(summary_wrap, 1)
        layout.addWidget(actions_wrap)

        _connect(getattr(self._dedupe_button, "clicked", None), self._handle_dedupe_selected)
        _connect(getattr(self._resize_button, "clicked", None), self._handle_resize_selected)
        _connect(getattr(self._process_button, "clicked", None), self._handle_process_selected)
        _connect(getattr(self._clear_button, "clicked", None), self._handle_clear_selection)
        _connect(getattr(self._dismiss_button, "clicked", None), self._handle_clear_selection)
        return bar

    def _apply_filters(self) -> None:
        normalized_search = self._search_text.strip().lower()
        resolved_type = self._type_filter.strip()

        def matches(item: MockMediaItem) -> bool:
            type_match = resolved_type in {"", "全部"} or item.media_type == resolved_type
            if not type_match:
                return False
            if not normalized_search:
                return True
            haystacks = (item.name, item.category, item.media_type, item.format_label, " ".join(item.tags))
            return any(normalized_search in value.lower() for value in haystacks)

        self._filtered_media = [item for item in self._all_media if matches(item)]

        if not self._filtered_media:
            self._active_media_id = self._selected_media_ids[0] if self._selected_media_ids else ""
        elif not any(item.media_id == self._active_media_id for item in self._filtered_media):
            visible_selected = next((item.media_id for item in self._filtered_media if item.media_id in self._selected_media_ids), None)
            self._active_media_id = visible_selected or self._filtered_media[0].media_id

        self._inventory_badge.setText(f"{len(self._all_media)} 个素材")
        self._collection_meta_label.setText(f"当前显示 {len(self._filtered_media)} / {len(self._all_media)} 个文件")
        self._selection_hint_badge.setText("已选素材" if self._selected_media_ids else "支持批量处理")
        self._selection_hint_badge.set_tone("brand" if self._selected_media_ids else "info")
        self._render_grid()
        self._refresh_preview_panel()
        self._refresh_batch_bar()

    def _render_grid(self) -> None:
        self._updating_grid = True
        _clear_layout_items(self._grid_shell_layout)
        self._grid_media_by_path.clear()

        empty_hint = "当前筛选条件下暂无素材，试试更换关键词、类型，或直接上传新素材补充到当前集合。"
        self._empty_state_label = QLabel(empty_hint, self._grid_shell)
        _call(self._empty_state_label, "setObjectName", "materialFactoryEmptyState")
        _call(self._empty_state_label, "setWordWrap", True)
        _call(self._empty_state_label, "setVisible", not self._filtered_media)
        self._grid_shell_layout.addWidget(self._empty_state_label)

        self._grid_widget = ImageGrid(columns=4 if self._view_mode == "grid" else 2, parent=self._grid_shell)
        _connect(self._grid_widget.selection_changed, self._handle_grid_selection_changed)
        _connect(self._grid_widget.item_double_clicked, self._handle_grid_item_double_clicked)
        _call(self._grid_widget, "setVisible", bool(self._filtered_media))
        self._grid_shell_layout.addWidget(self._grid_widget)

        for item in self._filtered_media:
            self._grid_widget.add_item(
                item.file_path,
                duration=item.duration if item.media_type == "视频" else "",
                status=item.status,
            )
            card = self._grid_widget._cards[-1]
            self._grid_media_by_path[item.file_path] = item.media_id
            self._customize_card(card, item)

        visible_selected_paths = [item.file_path for item in self._filtered_media if item.media_id in self._selected_media_ids]
        self._grid_widget._selected_paths = list(visible_selected_paths)
        self._updating_grid = False
        self._refresh_grid_visuals()

    def _customize_card(self, card: object, item: MockMediaItem) -> None:
        _call(getattr(card, "_filename_label", None), "setText", item.name)
        _call(getattr(card, "_meta_label", None), "setText", item.grid_meta)
        _call(getattr(card, "_preview_label", None), "setText", self._preview_canvas_copy(item))
        _call(getattr(card, "_preview_label", None), "setWordWrap", True)
        _call(getattr(card, "_status_label", None), "setText", item.media_type)
        card.set_selected(item.media_id in self._selected_media_ids)

    def _refresh_grid_visuals(self) -> None:
        if self._grid_widget is None:
            return
        colors = _palette()
        for item, card in zip(self._filtered_media, self._grid_widget._cards):
            is_selected = item.media_id in self._selected_media_ids
            is_active = item.media_id == self._active_media_id
            border_color = _token("brand.primary") if is_selected or is_active else colors.border
            background = _rgba(_token("brand.primary"), 0.08) if is_active else colors.surface
            preview_background = _rgba(item.accent, 0.12)
            preview_border = _rgba(item.accent, 0.36)
            status_background = _rgba(item.accent, 0.18) if item.media_type != "视频" else _rgba(_token("brand.primary"), 0.18)
            _call(
                card,
                "setStyleSheet",
                f"""
                QFrame#thumbnailCard {{
                    background-color: {background};
                    border: 1px solid {border_color};
                    border-radius: {RADIUS_LG}px;
                }}
                QFrame#thumbnailCard:hover {{
                    border-color: {_token('brand.primary')};
                    background-color: {_rgba(_token('brand.primary'), 0.06)};
                }}
                QFrame#thumbnailCard QLabel {{
                    color: {colors.text};
                    background: transparent;
                    font-family: {_static_token('font.family.chinese')};
                }}
                QFrame#thumbnailCard QLabel[role="meta"] {{
                    color: {colors.text_muted};
                    font-size: {_static_token('font.size.sm')};
                }}
                QFrame#thumbnailCard QLabel[role="status"] {{
                    color: {item.accent if item.media_type != '视频' else _token('brand.primary')};
                    background-color: {status_background};
                    border-radius: {RADIUS_MD}px;
                    padding: {SPACING_XS}px {SPACING_MD}px;
                    font-size: {_static_token('font.size.xs')};
                    font-weight: {_static_token('font.weight.bold')};
                }}
                QFrame#thumbnailCard QLabel[role="preview"] {{
                    background-color: {preview_background};
                    color: {colors.text};
                    border: 1px dashed {preview_border};
                    border-radius: {RADIUS_MD}px;
                    font-size: {_static_token('font.size.md')};
                    font-weight: {_static_token('font.weight.semibold')};
                    padding: {SPACING_MD}px;
                }}
                """,
            )
            card.set_selected(is_selected)

    def _refresh_preview_panel(self) -> None:
        current = self._current_active_item()
        if current is None:
            self._detail_name_value.setText("暂无素材")
            self._detail_format_value.setText("--")
            self._detail_resolution_value.setText("--")
            self._detail_size_value.setText("--")
            self._detail_fps_value.setText("--")
            self._detail_duration_value.setText("--")
            self._preview_kind_badge.setText("未选择")
            self._preview_kind_badge.set_tone("neutral")
            self._preview_status_badge.setText("等待选择")
            self._preview_status_badge.set_tone("warning")
            self._preview_canvas.setText("从左侧网格选择素材，右侧将同步详情与预览。")
            self._clear_tags()
            return

        status_text, status_tone = self._status_meta(current.status)
        self._preview_kind_badge.setText(current.media_type)
        self._preview_kind_badge.set_tone("info" if current.media_type == "视频" else "brand")
        self._preview_status_badge.setText(status_text)
        self._preview_status_badge.set_tone(status_tone)
        self._detail_name_value.setText(current.name)
        self._detail_format_value.setText(current.format_label)
        self._detail_resolution_value.setText(current.resolution)
        self._detail_size_value.setText(current.size_label)
        self._detail_fps_value.setText(current.frame_rate)
        self._detail_duration_value.setText(current.duration or "静态素材")
        self._preview_canvas.setText(self._preview_canvas_copy(current))
        self._preview_canvas.setStyleSheet(
            f"""
            QLabel#materialFactoryPreviewCanvas {{
                background-color: {_rgba(current.accent, 0.16)};
                color: {_palette().text};
                border: 1px solid {_rgba(current.accent, 0.34)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_XL}px;
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            """
        )
        self._preview_progress.setStyleSheet(
            f"QFrame#materialFactoryPreviewProgress {{ background-color: {current.accent}; border-radius: {SPACING_XS}px; }}"
        )
        self._sync_preview_dialog(current)
        self._render_tags(current.tags)

    def _refresh_batch_bar(self) -> None:
        selected_items = self._selected_items()
        total_size = sum(item.size_mb for item in selected_items)
        self._batch_title_label.setText(f"已选择 {len(selected_items)} 个素材" if selected_items else "未选择素材")
        if selected_items:
            self._batch_meta_label.setText(f"总计 {_format_total_size(total_size)} · 可执行去重、改尺寸与批量处理")
            self._processing_badge.setText("已进入批处理待命")
            self._processing_badge.set_tone("brand")
        else:
            self._batch_meta_label.setText("选择素材后可执行一键去重、批量改尺寸与统一处理。")
            self._processing_badge.setText("批量处理就绪")
            self._processing_badge.set_tone("success")

        _clear_layout_items(self._batch_stack_layout)
        for item in selected_items[:3]:
            chip = QLabel(item.name[:2], self._batch_stack_wrap)
            _call(chip, "setObjectName", "materialFactoryBatchThumb")
            _call(chip, "setStyleSheet", self._batch_thumb_style(item.accent))
            self._batch_stack_layout.addWidget(chip)
        if len(selected_items) > 3:
            more_chip = QLabel(f"+{len(selected_items) - 3}", self._batch_stack_wrap)
            _call(more_chip, "setObjectName", "materialFactoryBatchThumb")
            _call(more_chip, "setStyleSheet", self._batch_thumb_style(_token("brand.primary")))
            self._batch_stack_layout.addWidget(more_chip)

        enabled = bool(selected_items)
        for button in (self._dedupe_button, self._resize_button, self._process_button, self._clear_button):
            _call(button, "setEnabled", enabled)

    def _sync_preview_dialog(self, item: MockMediaItem) -> None:
        """选择素材时同步完整预览组件状态。"""

        self._preview_dialog.set_media(item.file_path)

    def _render_tags(self, tags: tuple[str, ...]) -> None:
        self._clear_tags()
        for tag in tags:
            self._tags_layout.addWidget(TagChip(tag, tone="neutral", parent=self._tags_host))
        self._tags_layout.addStretch(1)

    def _clear_tags(self) -> None:
        _clear_layout_items(self._tags_layout)

    def _handle_search_changed(self, text: str) -> None:
        self._search_text = text
        self._apply_filters()

    def _handle_type_filter_changed(self, value: str) -> None:
        self._type_filter = value
        self._apply_filters()

    def _handle_grid_view(self) -> None:
        self._view_mode = "grid"
        self._refresh_view_toggle_styles()
        self._apply_filters()

    def _handle_list_view(self) -> None:
        self._view_mode = "list"
        self._refresh_view_toggle_styles()
        self._apply_filters()

    def _handle_grid_selection_changed(self, selected_paths: object) -> None:
        if self._updating_grid or not isinstance(selected_paths, list):
            return
        visible_ids = {item.media_id for item in self._filtered_media}
        retained = [media_id for media_id in self._selected_media_ids if media_id not in visible_ids]
        next_ids = list(retained)
        for path in selected_paths:
            if not isinstance(path, str):
                continue
            media_id = self._grid_media_by_path.get(path)
            if media_id and media_id not in next_ids:
                next_ids.append(media_id)
        self._selected_media_ids = next_ids

        if selected_paths:
            last_path = selected_paths[-1]
            if isinstance(last_path, str):
                self._active_media_id = self._grid_media_by_path.get(last_path, self._active_media_id)
        elif self._filtered_media:
            self._active_media_id = self._filtered_media[0].media_id

        self._refresh_grid_visuals()
        self._refresh_preview_panel()
        self._refresh_batch_bar()

    def _handle_grid_item_double_clicked(self, file_path: str) -> None:
        media_id = self._grid_media_by_path.get(file_path)
        if media_id:
            self._active_media_id = media_id
            if media_id not in self._selected_media_ids:
                self._selected_media_ids.append(media_id)
            self._refresh_grid_visuals()
            self._refresh_preview_panel()
            self._refresh_batch_bar()
        self._handle_open_preview()

    def _handle_upload_clicked(self) -> None:
        template = self._all_media[self._upload_sequence % len(self._all_media)]
        media_type = "图片" if self._upload_sequence % 2 == 0 else "视频"
        uploaded = MockMediaItem(
            media_id=f"upload_{self._upload_sequence}",
            file_path=f"mock_uploads/新上传素材_{self._upload_sequence}.{ 'png' if media_type == '图片' else 'mp4' }",
            name=f"新上传素材_{self._upload_sequence}.{ 'png' if media_type == '图片' else 'mp4' }",
            media_type=media_type,
            category="最近上传",
            size_mb=template.size_mb + float(self._upload_sequence),
            size_label=f"{template.size_mb + float(self._upload_sequence):.1f} MB",
            resolution="1920 × 1080" if media_type == "视频" else "2048 × 2048",
            format_label="MPEG-4" if media_type == "视频" else "PNG",
            frame_rate="30 fps" if media_type == "视频" else "静态",
            duration="00:18" if media_type == "视频" else "",
            status="processing" if media_type == "视频" else "ready",
            tags=("上传", "待整理", "新品"),
            accent=template.accent,
        )
        self._upload_sequence += 1
        self._all_media.insert(0, uploaded)
        self._selected_media_ids = [uploaded.media_id]
        self._active_media_id = uploaded.media_id
        self._processing_badge.setText("刚刚上传")
        self._processing_badge.set_tone("warning")
        self._apply_filters()

    def _handle_open_preview(self) -> None:
        current = self._current_active_item()
        if current is None:
            return
        self._preview_dialog.set_media(current.file_path)
        _call(self._preview_dialog, "show")
        _call(self._preview_dialog, "raise_")
        _call(self._preview_dialog, "activateWindow")

    def _handle_download_selected(self) -> None:
        current = self._current_active_item()
        if current is None:
            return
        self._processing_badge.setText(f"已加入下载：{current.name}")
        self._processing_badge.set_tone("info")

    def _handle_share_selected(self) -> None:
        current = self._current_active_item()
        if current is None:
            return
        self._processing_badge.setText(f"已生成共享链接：{current.name}")
        self._processing_badge.set_tone("brand")

    def _handle_dedupe_selected(self) -> None:
        if not self._selected_media_ids:
            return
        self._processing_badge.setText(f"去重完成 · 处理 {len(self._selected_media_ids)} 个素材")
        self._processing_badge.set_tone("success")

    def _handle_resize_selected(self) -> None:
        if not self._selected_media_ids:
            return
        self._processing_badge.setText(f"改尺寸排队中 · {len(self._selected_media_ids)} 个素材")
        self._processing_badge.set_tone("warning")

    def _handle_process_selected(self) -> None:
        if not self._selected_media_ids:
            return
        self._processing_badge.setText(f"处理任务已启动 · {len(self._selected_media_ids)} 个素材")
        self._processing_badge.set_tone("brand")

    def _handle_clear_selection(self) -> None:
        self._selected_media_ids = []
        if self._filtered_media:
            self._active_media_id = self._filtered_media[0].media_id
        self._apply_filters()

    def _refresh_view_toggle_styles(self) -> None:
        colors = _palette()
        active_background = _rgba(_token("brand.primary"), 0.14)
        active_border = _token("brand.primary")
        inactive_background = colors.surface
        inactive_border = colors.border

        for button, active in (
            (self._grid_toggle_button, self._view_mode == "grid"),
            (self._list_toggle_button, self._view_mode == "list"),
        ):
            _call(
                button,
                "setStyleSheet",
                f"""
                QPushButton#iconButton {{
                    background-color: {active_background if active else inactive_background};
                    color: {colors.text};
                    border: 1px solid {active_border if active else inactive_border};
                    border-radius: {RADIUS_MD}px;
                    min-width: {BUTTON_HEIGHT}px;
                    min-height: {BUTTON_HEIGHT}px;
                    font-size: {_static_token('font.size.lg')};
                    font-weight: {_static_token('font.weight.bold')};
                }}
                QPushButton#iconButton:hover {{
                    border-color: {_token('brand.primary')};
                    background-color: {_rgba(_token('brand.primary'), 0.10)};
                }}
                """,
            )

    def _current_active_item(self) -> MockMediaItem | None:
        return next((item for item in self._all_media if item.media_id == self._active_media_id), None)

    def _selected_items(self) -> list[MockMediaItem]:
        selected_ids = set(self._selected_media_ids)
        return [item for item in self._all_media if item.media_id in selected_ids]

    def _preview_canvas_copy(self, item: MockMediaItem) -> str:
        if item.media_type == "视频":
            return f"▶ {item.name}\n{item.resolution} · {item.duration}"
        return f"▣ {item.name}\n{item.resolution} · {item.category}"

    def _batch_thumb_style(self, accent: str) -> str:
        colors = _palette()
        return (
            f"background-color: {_rgba(accent, 0.18)};"
            f"color: {colors.text};"
            f"border: 1px solid {_rgba(accent, 0.32)};"
            f"border-radius: {RADIUS_MD}px;"
            f"padding: {SPACING_MD}px;"
            f"min-width: {BUTTON_HEIGHT}px;"
            f"min-height: {BUTTON_HEIGHT}px;"
            f"font-size: {_static_token('font.size.sm')};"
            f"font-weight: {_static_token('font.weight.bold')};"
        )

    @staticmethod
    def _status_meta(status: str) -> tuple[str, BadgeTone]:
        mapping: dict[str, tuple[str, BadgeTone]] = {
            "ready": ("已就绪", "success"),
            "processing": ("处理中", "warning"),
            "error": ("异常", "error"),
        }
        return mapping.get(status, ("待处理", "neutral"))

    def _apply_page_styles(self) -> None:
        colors = _palette()
        self.setStyleSheet(
            f"""
            QWidget#materialFactoryPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#materialFactoryPage QLabel {{
                font-family: {_static_token('font.family.chinese')};
                color: {colors.text};
            }}
            QFrame#materialFactoryToolbar,
            QFrame#materialFactoryLibraryHeader,
            QFrame#materialFactoryGridShell,
            QFrame#materialFactoryPreviewPanel {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#materialFactoryCollectionTitle,
            QLabel#materialFactorySideTitle,
            QLabel#materialFactoryToolbarTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#materialFactoryToolbarSubtitle,
            QLabel#materialFactoryMutedText,
            QLabel#materialFactoryBatchMeta {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#materialFactoryMutedCaption {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.xs')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#materialFactoryValueText {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#materialFactoryEmptyState {{
                background-color: {_rgba(_token('brand.primary'), 0.06)};
                color: {colors.text_muted};
                border: 1px dashed {_rgba(_token('brand.primary'), 0.28)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_2XL}px;
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.medium')};
            }}
            QFrame#materialFactoryPreviewStage {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#materialFactoryBatchBar {{
                background-color: {_token('brand.secondary')};
                border: 1px solid {_rgba(_token('text.inverse'), 0.08)};
                border-radius: {RADIUS_LG + RADIUS_MD}px;
            }}
            QLabel#materialFactoryBatchTitle {{
                color: {_token('text.inverse')};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#materialFactoryBatchMeta {{
                color: {_rgba(_token('text.inverse'), 0.72)};
            }}
            QPushButton#materialFactoryBatchAction,
            QPushButton#materialFactorySecondaryAction {{
                background-color: {colors.surface};
                color: {colors.text};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
                min-height: {BUTTON_HEIGHT}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#materialFactoryBatchAction:hover,
            QPushButton#materialFactorySecondaryAction:hover {{
                border-color: {_token('brand.primary')};
                background-color: {_rgba(_token('brand.primary'), 0.08)};
            }}
            QPushButton#materialFactoryBatchAction:disabled,
            QPushButton#materialFactorySecondaryAction:disabled {{
                color: {colors.text_muted};
                background-color: {colors.surface_alt};
                border-color: {colors.border};
            }}
            """
        )

    @staticmethod
    def _build_mock_media() -> list[MockMediaItem]:
        return [
            MockMediaItem(
                media_id="nature_01",
                file_path="mock_library/自然风光_01.mp4",
                name="自然风光_01.mp4",
                media_type="视频",
                category="自然风景",
                size_mb=12.5,
                size_label="12.5 MB",
                resolution="1920 × 1080",
                format_label="MPEG-4",
                frame_rate="30 fps",
                duration="00:15",
                status="ready",
                tags=("风景", "自然", "日出"),
                accent="#00F2EA",
            ),
            MockMediaItem(
                media_id="city_02",
                file_path="mock_library/城市航拍_02.jpg",
                name="城市航拍_02.jpg",
                media_type="图片",
                category="城市建筑",
                size_mb=4.2,
                size_label="4.2 MB",
                resolution="3840 × 2160",
                format_label="JPEG",
                frame_rate="静态",
                duration="",
                status="ready",
                tags=("建筑", "夜景", "航拍"),
                accent="#38BDF8",
            ),
            MockMediaItem(
                media_id="interview_03",
                file_path="mock_library/人物访谈_03.mp4",
                name="人物访谈_03.mp4",
                media_type="视频",
                category="品牌拍摄",
                size_mb=85.1,
                size_label="85.1 MB",
                resolution="1920 × 1080",
                format_label="MPEG-4",
                frame_rate="30 fps",
                duration="02:45",
                status="ready",
                tags=("人物", "采访", "棚拍"),
                accent="#14B8A6",
            ),
            MockMediaItem(
                media_id="product_04",
                file_path="mock_library/产品展示_04.png",
                name="产品展示_04.png",
                media_type="封面",
                category="商品主图",
                size_mb=2.1,
                size_label="2.1 MB",
                resolution="2048 × 2048",
                format_label="PNG",
                frame_rate="静态",
                duration="",
                status="ready",
                tags=("产品", "主图", "极简"),
                accent="#F59E0B",
            ),
            MockMediaItem(
                media_id="promo_05",
                file_path="mock_library/宣传片剪辑.mov",
                name="宣传片剪辑.mov",
                media_type="视频",
                category="品牌拍摄",
                size_mb=45.8,
                size_label="45.8 MB",
                resolution="3840 × 2160",
                format_label="ProRes",
                frame_rate="24 fps",
                duration="00:30",
                status="processing",
                tags=("宣传片", "夜景", "电影感"),
                accent="#8B5CF6",
            ),
            MockMediaItem(
                media_id="workspace_06",
                file_path="mock_library/背景图库_08.webp",
                name="背景图库_08.webp",
                media_type="图片",
                category="办公空间",
                size_mb=1.8,
                size_label="1.8 MB",
                resolution="1800 × 1800",
                format_label="WebP",
                frame_rate="静态",
                duration="",
                status="ready",
                tags=("桌面", "场景", "生活感"),
                accent="#F97316",
            ),
            MockMediaItem(
                media_id="livestream_07",
                file_path="mock_library/短视频素材_07.mp4",
                name="短视频素材_07.mp4",
                media_type="视频",
                category="视频素材",
                size_mb=36.7,
                size_label="36.7 MB",
                resolution="1080 × 1920",
                format_label="MPEG-4",
                frame_rate="30 fps",
                duration="00:42",
                status="ready",
                tags=("短视频", "素材", "高转化"),
                accent="#22C55E",
            ),
            MockMediaItem(
                media_id="detail_08",
                file_path="mock_library/细节特写_08.jpg",
                name="细节特写_08.jpg",
                media_type="图片",
                category="产品细节",
                size_mb=5.4,
                size_label="5.4 MB",
                resolution="3000 × 2000",
                format_label="JPEG",
                frame_rate="静态",
                duration="",
                status="ready",
                tags=("细节", "质感", "特写"),
                accent="#EF4444",
            ),
            MockMediaItem(
                media_id="ugc_09",
                file_path="mock_library/UGC口播_09.mp4",
                name="UGC口播_09.mp4",
                media_type="视频",
                category="达人合作",
                size_mb=28.3,
                size_label="28.3 MB",
                resolution="1080 × 1920",
                format_label="MPEG-4",
                frame_rate="30 fps",
                duration="00:26",
                status="ready",
                tags=("口播", "达人", "种草"),
                accent="#06B6D4",
            ),
            MockMediaItem(
                media_id="cover_10",
                file_path="mock_library/活动封面_10.png",
                name="活动封面_10.png",
                media_type="封面",
                category="活动视觉",
                size_mb=3.6,
                size_label="3.6 MB",
                resolution="1440 × 1920",
                format_label="PNG",
                frame_rate="静态",
                duration="",
                status="ready",
                tags=("封面", "活动", "转化"),
                accent="#A855F7",
            ),
        ]


__all__ = ["MaterialFactoryPage"]

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportAssignmentType=false

from __future__ import annotations

"""素材中心页面。"""

from dataclasses import dataclass
from typing import Final

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    DragDropZone,
    FileUploaderWidget,
    FilterDropdown,
    IconButton,
    ImageGrid,
    KPICard,
    MediaPreview,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TabBar,
    TagChip,
    ThumbnailCard,
    VideoPlayerWidget,
)
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
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


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


def _duration_seconds(text: str) -> int:
    """将 mm:ss 文本转为秒数。"""

    parts = [part.strip() for part in text.split(":") if part.strip()]
    if len(parts) != 2:
        return 15
    minutes = int(parts[0]) if parts[0].isdigit() else 0
    seconds = int(parts[1]) if parts[1].isdigit() else 0
    return max(1, minutes * 60 + seconds)


def _size_matches(size_mb: float, size_filter: str) -> bool:
    """判断素材是否符合体积筛选。"""

    if size_filter == "全部":
        return True
    if size_filter == "0-50 MB":
        return size_mb < 50
    if size_filter == "50-200 MB":
        return 50 <= size_mb < 200
    if size_filter == "200-500 MB":
        return 200 <= size_mb < 500
    if size_filter == ">500 MB":
        return size_mb >= 500
    return True


def _date_matches(created_at: str, date_filter: str) -> bool:
    """判断素材是否符合日期筛选。"""

    if date_filter == "全部":
        return True
    month_text = created_at[:7]
    if date_filter == "近 7 天":
        return created_at >= "2026-03-02"
    if date_filter == "近 30 天":
        return created_at >= "2026-02-08"
    if date_filter == "本月":
        return month_text == "2026-03"
    if date_filter == "上月":
        return month_text == "2026-02"
    return True


@dataclass(frozen=True)
class AssetRecord:
    """素材记录。"""

    asset_id: str
    file_path: str
    name: str
    asset_type: str
    folder: str
    collection: str
    owner: str
    size_mb: float
    size_label: str
    resolution: str
    format_label: str
    duration: str
    created_at: str
    status: str
    tags: tuple[str, ...]
    description: str
    accent: str
    weekly_new: bool


@dataclass(frozen=True)
class FolderGroup:
    """顶部导航分组。"""

    title: str
    subtitle: str


@dataclass(frozen=True)
class UploadTask:
    """上传任务。"""

    file_name: str
    type_label: str
    status: str
    progress: int
    size_label: str


PAGE_MIN_HEIGHT: Final[int] = 760
GRID_COLUMNS: Final[int] = 4
PREVIEW_MIN_WIDTH: Final[int] = 360
WORKSPACE_MIN_WIDTH: Final[int] = 880
TAG_SUGGESTIONS: Final[tuple[str, ...]] = (
    "高点击开场",
    "场景实拍",
    "封面备选",
    "对比卖点",
    "字幕包",
    "品牌视觉",
    "节奏切片",
    "音效氛围",
)
FOLDER_GROUPS: Final[tuple[FolderGroup, ...]] = (
    FolderGroup("全部素材", "统一查看图片、视频、音频与文档"),
    FolderGroup("爆款资产", "优先保留高点击与高完播样本"),
    FolderGroup("模板集合", "可复用片头、字幕、贴纸与封面"),
    FolderGroup("品牌资产", "品牌色、LOGO、标准口播与字体包"),
)
SIZE_FILTERS: Final[tuple[str, ...]] = ("0-50 MB", "50-200 MB", "200-500 MB", ">500 MB")
DATE_FILTERS: Final[tuple[str, ...]] = ("近 7 天", "近 30 天", "本月", "上月")
TYPE_FILTERS: Final[tuple[str, ...]] = ("图片", "视频", "音频", "文档")
TAG_FILTERS: Final[tuple[str, ...]] = (
    "高点击开场",
    "高转化",
    "封面备选",
    "场景实拍",
    "字幕包",
    "品牌视觉",
    "节奏切片",
    "音效氛围",
)

ASSET_LIBRARY: Final[tuple[AssetRecord, ...]] = (
    AssetRecord("mtc-001", "D:/demo/content/material_center/开场秒吸睛航拍.mp4", "开场秒吸睛航拍", "视频", "今日上新", "爆款资产", "内容组 A", 182.4, "182.4 MB", "1080×1920", "MP4", "00:18", "2026-03-08", "已归档", ("高点击开场", "节奏切片", "场景实拍"), "用于三秒强吸引开头，适合首屏钩子镜头。", "#00F2EA", True),
    AssetRecord("mtc-002", "D:/demo/content/material_center/功能细节特写A.mp4", "功能细节特写 A", "视频", "卖点拆解", "爆款资产", "内容组 B", 94.2, "94.2 MB", "1080×1920", "MP4", "00:09", "2026-03-07", "处理中", ("高转化", "对比卖点", "节奏切片"), "适合切入细节与功能演示，常作为第二镜头。", "#22C55E", True),
    AssetRecord("mtc-003", "D:/demo/content/material_center/模特试用竖屏01.mp4", "模特试用竖屏 01", "视频", "场景实拍", "全部素材", "内容组 A", 211.7, "211.7 MB", "1080×1920", "MOV", "00:22", "2026-03-06", "已归档", ("场景实拍", "高转化", "品牌视觉"), "真实使用场景镜头，适合承接卖点后的人物演示。", "#F59E0B", True),
    AssetRecord("mtc-004", "D:/demo/content/material_center/封面主视觉01.jpg", "封面主视觉 01", "图片", "封面仓", "模板集合", "设计组", 8.6, "8.6 MB", "1242×1660", "JPG", "静帧", "2026-03-05", "已归档", ("封面备选", "品牌视觉"), "高对比封面图，适合作为封面 A/B 版本。", "#FB7185", True),
    AssetRecord("mtc-005", "D:/demo/content/material_center/品牌渐变背景包01.png", "品牌渐变背景包 01", "图片", "品牌资产", "品牌资产", "设计组", 5.4, "5.4 MB", "1600×1600", "PNG", "静帧", "2026-03-05", "已归档", ("品牌视觉", "字幕包"), "适合字幕底板、卖点卡片与封面强化区域。", "#6366F1", False),
    AssetRecord("mtc-006", "D:/demo/content/material_center/环境声氛围铺底.wav", "环境声氛围铺底", "音频", "音频库", "全部素材", "后期组", 34.8, "34.8 MB", "48kHz", "WAV", "00:31", "2026-03-03", "已归档", ("音效氛围", "节奏切片"), "适合作为转场段落的底噪氛围，强化现场感。", "#14B8A6", False),
    AssetRecord("mtc-007", "D:/demo/content/material_center/快节奏鼓点循环.mp3", "快节奏鼓点循环", "音频", "音频库", "爆款资产", "后期组", 12.2, "12.2 MB", "44.1kHz", "MP3", "00:15", "2026-03-02", "已归档", ("节奏切片", "音效氛围"), "常用于视频中段提速和卖点切换。", "#E879F9", False),
    AssetRecord("mtc-008", "D:/demo/content/material_center/字幕样式预设A.srt", "字幕样式预设 A", "文档", "字幕模板", "模板集合", "后期组", 0.2, "0.2 MB", "字幕文件", "SRT", "静帧", "2026-02-28", "已归档", ("字幕包", "品牌视觉"), "适配高亮词样式与重点卖点节奏提示。", "#38BDF8", False),
    AssetRecord("mtc-009", "D:/demo/content/material_center/卖点对比拼接版.mp4", "卖点对比拼接版", "视频", "卖点拆解", "模板集合", "内容组 B", 256.8, "256.8 MB", "1080×1920", "MP4", "00:27", "2026-02-26", "已归档", ("对比卖点", "高转化", "节奏切片"), "用于一镜到底式前后对比，强调结果差异。", "#F97316", False),
    AssetRecord("mtc-010", "D:/demo/content/material_center/商品局部细节图03.jpg", "商品局部细节图 03", "图片", "图像细节", "全部素材", "设计组", 6.9, "6.9 MB", "1500×1500", "JPG", "静帧", "2026-02-23", "已归档", ("对比卖点", "封面备选"), "用于放大展示纹理与做工细节。", "#A78BFA", False),
    AssetRecord("mtc-011", "D:/demo/content/material_center/品牌字体授权说明.pdf", "品牌字体授权说明", "文档", "品牌资产", "品牌资产", "品牌组", 1.4, "1.4 MB", "文档", "PDF", "静帧", "2026-02-21", "已归档", ("品牌视觉",), "品牌字体、使用场景与输出要求说明文档。", "#64748B", False),
    AssetRecord("mtc-012", "D:/demo/content/material_center/人物微表情近景02.mp4", "人物微表情近景 02", "视频", "人物演绎", "爆款资产", "内容组 C", 143.9, "143.9 MB", "1080×1920", "MP4", "00:13", "2026-02-18", "已归档", ("场景实拍", "高点击开场"), "适合做情绪转场与停留镜头强化。", "#10B981", False),
    AssetRecord("mtc-013", "D:/demo/content/material_center/包装开箱顶视角.mp4", "包装开箱顶视角", "视频", "开箱素材", "全部素材", "内容组 C", 168.5, "168.5 MB", "1080×1920", "MP4", "00:16", "2026-02-12", "处理中", ("场景实拍", "高转化"), "强调拆箱过程与第一视觉冲击。", "#06B6D4", False),
    AssetRecord("mtc-014", "D:/demo/content/material_center/口播关键词节奏表.xlsx", "口播关键词节奏表", "文档", "脚本模板", "模板集合", "策划组", 0.9, "0.9 MB", "表格", "XLSX", "静帧", "2026-02-10", "已归档", ("字幕包", "节奏切片"), "用于统一口播停顿、重点词与字幕节奏。", "#F43F5E", False),
)


class MaterialCenterPage(BasePage):
    """素材中心，统一管理多类型内容资产。"""

    default_route_id: RouteId = RouteId("material_center")
    default_display_name: str = "素材中心"
    default_icon_name: str = "folder_open"

    def setup_ui(self) -> None:
        """构建素材中心页面。"""

        self._all_assets: list[AssetRecord] = list(ASSET_LIBRARY)
        self._filtered_assets: list[AssetRecord] = []
        self._selected_asset_ids: list[str] = [self._all_assets[0].asset_id, self._all_assets[3].asset_id]
        self._active_asset_id: str = self._all_assets[0].asset_id
        self._view_mode = "grid"
        self._search_text = ""
        self._type_filter = "全部"
        self._tag_filter = "全部"
        self._date_filter = "全部"
        self._size_filter = "全部"
        self._collection_filter = FOLDER_GROUPS[0].title
        self._upload_tasks: list[UploadTask] = [
            UploadTask("新品素材包 A.zip", "文档", "校验完成", 100, "428 MB"),
            UploadTask("封面候选图 3 张", "图片", "上传中", 68, "18 MB"),
            UploadTask("氛围音效 2 条", "音频", "等待入库", 22, "41 MB"),
        ]
        self._suggestion_buttons: list[QPushButton] = []
        self._featured_cards: list[ThumbnailCard] = []
        self._preview_dialog = MediaPreview(parent=self)

        _call(self, "setObjectName", "materialCenterPage")
        _call(self, "setMinimumHeight", PAGE_MIN_HEIGHT)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._apply_page_styles()

        self._page_container = PageContainer(
            title=self.display_name,
            description="管理 TikTok 内容资产、上传任务与多端创作素材，支持筛选、预览与批量处理。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._inventory_badge = StatusBadge("素材仓已同步", tone="success", parent=self._page_container)
        self._selection_badge = StatusBadge("已选 2 项", tone="brand", parent=self._page_container)
        self._ops_badge = StatusBadge("批量操作待命", tone="neutral", parent=self._page_container)
        self._page_container.add_action(self._inventory_badge)
        self._page_container.add_action(self._selection_badge)
        self._page_container.add_action(self._ops_badge)

        self._page_container.add_widget(self._build_kpi_strip())
        self._page_container.add_widget(self._build_collection_navigation())
        self._page_container.add_widget(self._build_filter_bar())
        self._page_container.add_widget(self._build_batch_toolbar())
        self._page_container.add_widget(self._build_workspace())

        self._bind_interactions()
        self._refresh_all_views()

    def _build_kpi_strip(self) -> QWidget:
        strip = QWidget(self)
        _call(strip, "setObjectName", "materialCenterKpiStrip")
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._kpi_total = KPICard("总素材数", "14", trend="up", percentage="+6", caption="较上周新增", parent=strip)
        self._kpi_image = KPICard("图片", "4", trend="flat", percentage="稳定", caption="封面与背景图", parent=strip)
        self._kpi_video = KPICard("视频", "7", trend="up", percentage="+2", caption="主视频与切片", parent=strip)
        self._kpi_audio = KPICard("音频", "2", trend="flat", percentage="稳定", caption="BGM 与氛围音", parent=strip)
        self._kpi_week = KPICard("本周新增", "4", trend="up", percentage="+80%", caption="新近入库素材", parent=strip)

        for card in (
            self._kpi_total,
            self._kpi_image,
            self._kpi_video,
            self._kpi_audio,
            self._kpi_week,
        ):
            layout.addWidget(card, 1)
        return strip

    def _build_collection_navigation(self) -> QWidget:
        section = ContentSection("收藏夹与集合导航", icon="◎", parent=self)
        body_layout = section.content_layout

        self._folder_tab_bar = TabBar(section)
        for group in FOLDER_GROUPS:
            panel = QWidget(self._folder_tab_bar)
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(0, 0, 0, 0)
            panel_layout.setSpacing(SPACING_SM)

            title = QLabel(group.title, panel)
            _call(title, "setObjectName", "materialFolderTitle")
            subtitle = QLabel(group.subtitle, panel)
            _call(subtitle, "setObjectName", "materialFolderSubtitle")
            _call(subtitle, "setWordWrap", True)

            panel_layout.addWidget(title)
            panel_layout.addWidget(subtitle)
            panel_layout.addStretch(1)
            self._folder_tab_bar.add_tab(group.title, panel)

        body_layout.addWidget(self._folder_tab_bar)
        return section

    def _build_filter_bar(self) -> QWidget:
        shell = QFrame(self)
        _call(shell, "setObjectName", "materialCenterFilterShell")
        _call(shell, "setProperty", "variant", "card")
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        intro_row = QHBoxLayout()
        intro_row.setContentsMargins(0, 0, 0, 0)
        intro_row.setSpacing(SPACING_LG)

        intro_copy = QWidget(shell)
        intro_copy_layout = QVBoxLayout(intro_copy)
        intro_copy_layout.setContentsMargins(0, 0, 0, 0)
        intro_copy_layout.setSpacing(SPACING_XS)
        intro_title = QLabel("筛选与标签编排", intro_copy)
        _call(intro_title, "setObjectName", "materialCenterFilterTitle")
        intro_subtitle = QLabel("保持与素材工厂一致的搜索、筛选和标签建议结构，方便快速定位可复用资产。", intro_copy)
        _call(intro_subtitle, "setObjectName", "materialCenterFilterSubtitle")
        _call(intro_subtitle, "setWordWrap", True)
        intro_copy_layout.addWidget(intro_title)
        intro_copy_layout.addWidget(intro_subtitle)

        intro_badges = QWidget(shell)
        intro_badges_layout = QHBoxLayout(intro_badges)
        intro_badges_layout.setContentsMargins(0, 0, 0, 0)
        intro_badges_layout.setSpacing(SPACING_SM)
        intro_badges_layout.addWidget(StatusBadge("支持多维筛选", tone="info", parent=intro_badges))
        intro_badges_layout.addWidget(StatusBadge("标签建议已启用", tone="brand", parent=intro_badges))

        intro_row.addWidget(intro_copy, 1)
        intro_row.addWidget(intro_badges)

        first_row = QHBoxLayout()
        first_row.setContentsMargins(0, 0, 0, 0)
        first_row.setSpacing(SPACING_LG)

        self._search_bar = SearchBar("搜索素材名称、标签、责任人或文件格式...")
        self._type_dropdown = FilterDropdown("类型", TYPE_FILTERS, include_all=True)
        self._tag_dropdown = FilterDropdown("标签", TAG_FILTERS, include_all=True)
        self._date_dropdown = FilterDropdown("日期", DATE_FILTERS, include_all=True)
        self._size_dropdown = FilterDropdown("大小", SIZE_FILTERS, include_all=True)
        self._grid_toggle_button = IconButton("▦", "网格视图")
        self._list_toggle_button = IconButton("☰", "列表视图")

        first_row.addWidget(self._search_bar, 1)
        first_row.addWidget(self._type_dropdown)
        first_row.addWidget(self._tag_dropdown)
        first_row.addWidget(self._date_dropdown)
        first_row.addWidget(self._size_dropdown)
        first_row.addWidget(self._grid_toggle_button)
        first_row.addWidget(self._list_toggle_button)

        second_row = QWidget(shell)
        second_row_layout = QHBoxLayout(second_row)
        second_row_layout.setContentsMargins(0, 0, 0, 0)
        second_row_layout.setSpacing(SPACING_MD)

        suggestion_label = QLabel("标签建议", second_row)
        _call(suggestion_label, "setObjectName", "materialSuggestionLabel")
        second_row_layout.addWidget(suggestion_label)

        self._suggestions_host = QWidget(second_row)
        self._suggestions_layout = QHBoxLayout(self._suggestions_host)
        self._suggestions_layout.setContentsMargins(0, 0, 0, 0)
        self._suggestions_layout.setSpacing(SPACING_SM)
        second_row_layout.addWidget(self._suggestions_host, 1)

        selected_label = QLabel("当前标签", second_row)
        _call(selected_label, "setObjectName", "materialSuggestionLabel")
        second_row_layout.addWidget(selected_label)

        self._active_tags_host = QWidget(second_row)
        self._active_tags_layout = QHBoxLayout(self._active_tags_host)
        self._active_tags_layout.setContentsMargins(0, 0, 0, 0)
        self._active_tags_layout.setSpacing(SPACING_SM)
        second_row_layout.addWidget(self._active_tags_host)

        layout.addLayout(intro_row)
        layout.addLayout(first_row)
        layout.addWidget(second_row)
        return shell

    def _build_batch_toolbar(self) -> QWidget:
        bar = QFrame(self)
        _call(bar, "setObjectName", "materialCenterBatchBar")
        _call(bar, "setProperty", "variant", "card")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        self._batch_summary_label = QLabel("当前已选 2 项，支持批量下载、删除与统一标签。", bar)
        _call(self._batch_summary_label, "setObjectName", "materialBatchSummary")
        self._download_button = SecondaryButton("批量下载", bar)
        self._delete_button = SecondaryButton("批量删除", bar)
        self._tag_button = PrimaryButton("批量标签", bar)
        self._clear_button = IconButton("↺", "清空选择", bar)

        layout.addWidget(self._batch_summary_label, 1)
        layout.addWidget(self._download_button)
        layout.addWidget(self._delete_button)
        layout.addWidget(self._tag_button)
        layout.addWidget(self._clear_button)
        return bar

    def _build_workspace(self) -> QWidget:
        split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.72, 0.28),
            minimum_sizes=(WORKSPACE_MIN_WIDTH, PREVIEW_MIN_WIDTH),
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

        self._featured_section = ContentSection("精选素材速览", icon="★", parent=panel)
        featured_layout = self._featured_section.content_layout
        self._featured_cards_host = QWidget(self._featured_section)
        self._featured_cards_layout = QHBoxLayout(self._featured_cards_host)
        self._featured_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._featured_cards_layout.setSpacing(SPACING_MD)
        featured_layout.addWidget(self._featured_cards_host)

        self._view_stack = QStackedWidget(panel)
        _call(self._view_stack, "setObjectName", "materialViewStack")
        self._grid_view = self._build_grid_view()
        self._list_view = self._build_list_view()
        _call(self._view_stack, "addWidget", self._grid_view)
        _call(self._view_stack, "addWidget", self._list_view)

        layout.addWidget(self._featured_section)
        layout.addWidget(self._view_stack)
        return panel

    def _build_grid_view(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "materialGridPanel")
        _call(panel, "setProperty", "variant", "card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        header = QHBoxLayout()
        header.setSpacing(SPACING_MD)
        self._grid_section_title = QLabel("网格浏览", panel)
        _call(self._grid_section_title, "setObjectName", "materialPanelTitle")
        self._grid_result_badge = StatusBadge("0 项", tone="brand", parent=panel)
        header.addWidget(self._grid_section_title)
        header.addStretch(1)
        header.addWidget(self._grid_result_badge)

        self._image_grid = ImageGrid(columns=GRID_COLUMNS, parent=panel)
        layout.addLayout(header)
        layout.addWidget(self._image_grid)
        return panel

    def _build_list_view(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "materialListPanel")
        _call(panel, "setProperty", "variant", "card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        header = QHBoxLayout()
        header.setSpacing(SPACING_MD)
        self._list_section_title = QLabel("列表浏览", panel)
        _call(self._list_section_title, "setObjectName", "materialPanelTitle")
        self._list_result_badge = StatusBadge("0 条", tone="neutral", parent=panel)
        header.addWidget(self._list_section_title)
        header.addStretch(1)
        header.addWidget(self._list_result_badge)

        self._asset_table = DataTable(
            headers=("素材名称", "类型", "集合", "大小", "时间", "状态", "标签"),
            rows=(),
            page_size=8,
            empty_text="暂无符合筛选条件的素材",
            parent=panel,
        )

        layout.addLayout(header)
        layout.addWidget(self._asset_table)
        return panel

    def _build_preview_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._preview_section = ContentSection("媒体预览", icon="▶", parent=panel)
        preview_layout = self._preview_section.content_layout
        self._preview_status_badge = StatusBadge("已就绪", tone="success", parent=self._preview_section)
        self._preview_name_label = QLabel("--", self._preview_section)
        _call(self._preview_name_label, "setObjectName", "materialPreviewName")
        self._preview_meta_label = QLabel("--", self._preview_section)
        _call(self._preview_meta_label, "setObjectName", "materialPreviewMeta")
        self._preview_description_label = QLabel("--", self._preview_section)
        _call(self._preview_description_label, "setObjectName", "materialPreviewDescription")
        _call(self._preview_description_label, "setWordWrap", True)
        self._preview_player = VideoPlayerWidget(parent=self._preview_section)
        self._preview_open_button = PrimaryButton("打开弹窗预览", self._preview_section)

        preview_layout.addWidget(self._preview_status_badge)
        preview_layout.addWidget(self._preview_name_label)
        preview_layout.addWidget(self._preview_meta_label)
        preview_layout.addWidget(self._preview_description_label)
        preview_layout.addWidget(self._preview_player)
        preview_layout.addWidget(self._preview_open_button)

        self._tags_section = ContentSection("素材标签", icon="#", parent=panel)
        tags_layout = self._tags_section.content_layout
        self._asset_tags_host = QWidget(self._tags_section)
        self._asset_tags_layout = QHBoxLayout(self._asset_tags_host)
        self._asset_tags_layout.setContentsMargins(0, 0, 0, 0)
        self._asset_tags_layout.setSpacing(SPACING_SM)
        self._asset_tags_note = QLabel("选中素材后可快速查看标签结构。", self._tags_section)
        _call(self._asset_tags_note, "setObjectName", "materialPreviewMeta")
        tags_layout.addWidget(self._asset_tags_host)
        tags_layout.addWidget(self._asset_tags_note)

        self._upload_section = ContentSection("上传区", icon="↑", parent=panel)
        upload_layout = self._upload_section.content_layout
        self._drag_drop_zone = DragDropZone(parent=self._upload_section)
        self._file_uploader = FileUploaderWidget(parent=self._upload_section)
        self._upload_table = DataTable(
            headers=("文件", "类型", "状态", "进度", "大小"),
            rows=(),
            page_size=5,
            empty_text="暂无上传任务",
            parent=self._upload_section,
        )
        upload_layout.addWidget(self._drag_drop_zone)
        upload_layout.addWidget(self._file_uploader)
        upload_layout.addWidget(self._upload_table)

        layout.addWidget(self._preview_section)
        layout.addWidget(self._tags_section)
        layout.addWidget(self._upload_section)
        return panel

    def _bind_interactions(self) -> None:
        """绑定页面交互。"""

        _connect(self._search_bar.search_changed, self._handle_search_changed)
        _connect(self._type_dropdown.filter_changed, self._handle_type_changed)
        _connect(self._tag_dropdown.filter_changed, self._handle_tag_changed)
        _connect(self._date_dropdown.filter_changed, self._handle_date_changed)
        _connect(self._size_dropdown.filter_changed, self._handle_size_changed)
        _connect(self._folder_tab_bar.tab_changed, self._handle_folder_changed)
        _connect(getattr(self._grid_toggle_button, "clicked", None), self._handle_grid_view)
        _connect(getattr(self._list_toggle_button, "clicked", None), self._handle_list_view)
        _connect(self._image_grid.selection_changed, self._handle_grid_selection_changed)
        _connect(self._image_grid.item_double_clicked, self._open_media_preview_by_path)
        _connect(self._asset_table.row_selected, self._handle_table_row_selected)
        _connect(self._asset_table.row_double_clicked, self._handle_table_row_double_clicked)
        _connect(getattr(self._preview_open_button, "clicked", None), self._open_media_preview)
        _connect(self._drag_drop_zone.files_dropped, self._handle_files_added)
        _connect(self._file_uploader.files_selected, self._handle_files_added)
        _connect(getattr(self._download_button, "clicked", None), self._handle_batch_download)
        _connect(getattr(self._delete_button, "clicked", None), self._handle_batch_delete)
        _connect(getattr(self._tag_button, "clicked", None), self._handle_batch_tag)
        _connect(getattr(self._clear_button, "clicked", None), self._handle_clear_selection)

    def _refresh_all_views(self) -> None:
        """刷新页面所有视图。"""

        self._apply_filters()
        self._refresh_kpis()
        self._refresh_suggestion_buttons()
        self._refresh_active_tag_chips()
        self._refresh_featured_assets()
        self._refresh_grid_view()
        self._refresh_list_view()
        self._refresh_preview_panel()
        self._refresh_upload_table()
        self._refresh_batch_bar()
        self._refresh_action_badges()
        self._refresh_view_toggle_styles()

    def _apply_filters(self) -> None:
        """根据当前筛选条件重算素材集合。"""

        normalized_query = self._search_text.strip().lower()
        results: list[AssetRecord] = []
        for asset in self._all_assets:
            if self._collection_filter != "全部素材" and asset.collection != self._collection_filter:
                continue
            if self._type_filter != "全部" and asset.asset_type != self._type_filter:
                continue
            if self._tag_filter != "全部" and self._tag_filter not in asset.tags:
                continue
            if not _date_matches(asset.created_at, self._date_filter):
                continue
            if not _size_matches(asset.size_mb, self._size_filter):
                continue
            if normalized_query:
                haystack = " ".join((
                    asset.name,
                    asset.folder,
                    asset.collection,
                    asset.owner,
                    asset.format_label,
                    asset.description,
                    " ".join(asset.tags),
                )).lower()
                if normalized_query not in haystack:
                    continue
            results.append(asset)
        self._filtered_assets = results
        available_ids = {asset.asset_id for asset in self._filtered_assets}
        self._selected_asset_ids = [asset_id for asset_id in self._selected_asset_ids if asset_id in available_ids]
        if self._active_asset_id not in available_ids and self._filtered_assets:
            self._active_asset_id = self._filtered_assets[0].asset_id
        if not self._filtered_assets:
            self._selected_asset_ids = []

    def _refresh_kpis(self) -> None:
        """刷新顶部 KPI。"""

        total = len(self._all_assets)
        image_count = sum(1 for asset in self._all_assets if asset.asset_type == "图片")
        video_count = sum(1 for asset in self._all_assets if asset.asset_type == "视频")
        audio_count = sum(1 for asset in self._all_assets if asset.asset_type == "音频")
        weekly_new = sum(1 for asset in self._all_assets if asset.weekly_new)
        self._kpi_total.set_value(str(total))
        self._kpi_image.set_value(str(image_count))
        self._kpi_video.set_value(str(video_count))
        self._kpi_audio.set_value(str(audio_count))
        self._kpi_week.set_value(str(weekly_new))

    def _refresh_suggestion_buttons(self) -> None:
        """刷新标签建议按钮。"""

        _clear_layout_items(self._suggestions_layout)
        self._suggestion_buttons = []
        for suggestion in TAG_SUGGESTIONS:
            button = QPushButton(suggestion, self._suggestions_host)
            _call(button, "setObjectName", "materialSuggestionButton")
            if suggestion == self._tag_filter:
                _call(button, "setProperty", "active", True)
            _connect(getattr(button, "clicked", None), lambda _checked=False, text=suggestion: self._apply_suggested_tag(text))
            self._suggestions_layout.addWidget(button)
            self._suggestion_buttons.append(button)
        self._suggestions_layout.addStretch(1)

    def _refresh_active_tag_chips(self) -> None:
        """刷新当前标签展示。"""

        _clear_layout_items(self._active_tags_layout)
        active_tags = [self._tag_filter] if self._tag_filter != "全部" else ["全部标签"]
        for tag in active_tags:
            chip = TagChip(tag, tone="brand" if tag != "全部标签" else "neutral", parent=self._active_tags_host)
            self._active_tags_layout.addWidget(chip)

    def _refresh_featured_assets(self) -> None:
        """刷新精选素材卡片。"""

        _clear_layout_items(self._featured_cards_layout)
        self._featured_cards = []
        for asset in self._filtered_assets[:3]:
            card = ThumbnailCard(asset.file_path, duration=asset.duration if asset.asset_type == "视频" else "", status="ready", parent=self._featured_cards_host)
            _connect(card.double_clicked, self._open_media_preview_by_path)
            self._featured_cards_layout.addWidget(card)
            self._featured_cards.append(card)
        self._featured_cards_layout.addStretch(1)

    def _refresh_grid_view(self) -> None:
        """刷新网格视图。"""

        self._image_grid.clear_items()
        self._grid_section_title.setText("网格浏览" if self._filtered_assets else "网格浏览 · 暂无结果")
        for asset in self._filtered_assets:
            duration = asset.duration if asset.asset_type == "视频" or asset.asset_type == "音频" else ""
            status = "processing" if asset.status == "处理中" else "ready"
            self._image_grid.add_item(asset.file_path, duration=duration, status=status)
        self._grid_result_badge.setText(f"{len(self._filtered_assets)} 项")

    def _refresh_list_view(self) -> None:
        """刷新列表视图。"""

        rows = [
            (
                asset.name,
                asset.asset_type,
                asset.collection,
                asset.size_label,
                asset.created_at,
                asset.status,
                " / ".join(asset.tags[:2]),
            )
            for asset in self._filtered_assets
        ]
        self._asset_table.set_rows(rows)
        self._list_result_badge.setText(f"{len(rows)} 条")
        self._list_section_title.setText("列表浏览" if rows else "列表浏览 · 暂无结果")
        if self._filtered_assets:
            active_index = self._index_of_asset(self._active_asset_id, self._filtered_assets)
            if active_index >= 0:
                self._asset_table.select_absolute_row(active_index)

    def _refresh_preview_panel(self) -> None:
        """刷新右侧预览与信息。"""

        active_asset = self._active_asset()
        if active_asset is None:
            self._preview_status_badge.setText("暂无素材")
            self._preview_status_badge.set_tone("neutral")
            self._preview_name_label.setText("暂无符合条件的素材")
            self._preview_meta_label.setText("请调整筛选条件或上传新素材。")
            self._preview_description_label.setText("当前素材库中没有可预览项目。")
            self._preview_player.set_duration(15)
            self._preview_player.set_position(0)
            self._refresh_asset_tags(())
            return

        tone = "warning" if active_asset.status == "处理中" else "success"
        self._preview_status_badge.setText(active_asset.status)
        self._preview_status_badge.set_tone(tone)
        self._preview_name_label.setText(active_asset.name)
        self._preview_meta_label.setText(
            f"{active_asset.asset_type} · {active_asset.resolution} · {active_asset.size_label} · {active_asset.owner}"
        )
        self._preview_description_label.setText(active_asset.description)
        self._preview_player.set_duration(_duration_seconds(active_asset.duration if ":" in active_asset.duration else "00:15"))
        self._preview_player.set_position(0)
        self._refresh_asset_tags(active_asset.tags)

    def _refresh_asset_tags(self, tags: tuple[str, ...]) -> None:
        """刷新素材标签区。"""

        _clear_layout_items(self._asset_tags_layout)
        if not tags:
            chip = TagChip("暂无标签", tone="neutral", parent=self._asset_tags_host)
            self._asset_tags_layout.addWidget(chip)
            self._asset_tags_note.setText("可通过批量标签快速补全资产语义。")
            return
        for tag in tags:
            tone = "brand" if tag in {"高点击开场", "高转化", "品牌视觉"} else "neutral"
            self._asset_tags_layout.addWidget(TagChip(tag, tone=tone, parent=self._asset_tags_host))
        self._asset_tags_note.setText(f"当前素材共 {len(tags)} 个标签，可用于搜索建议与批量归档。")

    def _refresh_upload_table(self) -> None:
        """刷新上传任务列表。"""

        rows = [
            (task.file_name, task.type_label, task.status, f"{task.progress}%", task.size_label)
            for task in self._upload_tasks
        ]
        self._upload_table.set_rows(rows)
        uploader_progress = self._upload_tasks[0].progress if self._upload_tasks else 0
        self._file_uploader.set_upload_progress(uploader_progress)

    def _refresh_batch_bar(self) -> None:
        """刷新批量操作文案。"""

        selected_count = len(self._selected_asset_ids)
        if selected_count == 0:
            self._batch_summary_label.setText("尚未选择素材，可在网格或列表中选中后进行批量处理。")
            return
        selected_names = [asset.name for asset in self._filtered_assets if asset.asset_id in self._selected_asset_ids][:2]
        preview_names = "、".join(selected_names)
        suffix = " 等" if selected_count > 2 else ""
        self._batch_summary_label.setText(f"当前已选 {selected_count} 项：{preview_names}{suffix}")

    def _refresh_action_badges(self) -> None:
        """刷新页头操作状态。"""

        self._inventory_badge.setText(f"已入库 {len(self._all_assets)} 项")
        self._selection_badge.setText(f"已选 {len(self._selected_asset_ids)} 项")
        if self._selected_asset_ids:
            self._selection_badge.set_tone("brand")
        else:
            self._selection_badge.set_tone("neutral")
        processing_count = sum(1 for asset in self._all_assets if asset.status == "处理中")
        if processing_count > 0:
            self._ops_badge.setText(f"{processing_count} 项处理中")
            self._ops_badge.set_tone("warning")
        else:
            self._ops_badge.setText("批量操作待命")
            self._ops_badge.set_tone("success")

    def _refresh_view_toggle_styles(self) -> None:
        """刷新视图切换按钮样式。"""

        active_color = _token("brand.primary")
        inactive_color = _rgba(_token("brand.primary"), 0.08)
        for button, mode in (
            (self._grid_toggle_button, "grid"),
            (self._list_toggle_button, "list"),
        ):
            is_active = self._view_mode == mode
            _call(
                button,
                "setStyleSheet",
                f"background-color: {active_color if is_active else inactive_color};"
                f"border-radius: {RADIUS_MD}px;"
                f"min-height: {BUTTON_HEIGHT}px;",
            )
        _call(self._view_stack, "setCurrentIndex", 0 if self._view_mode == "grid" else 1)

    def _handle_search_changed(self, text: str) -> None:
        """处理搜索变化。"""

        self._search_text = text
        self._refresh_all_views()

    def _handle_type_changed(self, value: str) -> None:
        """处理类型筛选变化。"""

        self._type_filter = value
        self._refresh_all_views()

    def _handle_tag_changed(self, value: str) -> None:
        """处理标签筛选变化。"""

        self._tag_filter = value
        self._refresh_all_views()

    def _handle_date_changed(self, value: str) -> None:
        """处理日期筛选变化。"""

        self._date_filter = value
        self._refresh_all_views()

    def _handle_size_changed(self, value: str) -> None:
        """处理大小筛选变化。"""

        self._size_filter = value
        self._refresh_all_views()

    def _handle_folder_changed(self, index: int) -> None:
        """处理顶部集合切换。"""

        if 0 <= index < len(FOLDER_GROUPS):
            self._collection_filter = FOLDER_GROUPS[index].title
            self._refresh_all_views()

    def _handle_grid_view(self) -> None:
        """切换为网格视图。"""

        self._view_mode = "grid"
        self._refresh_view_toggle_styles()

    def _handle_list_view(self) -> None:
        """切换为列表视图。"""

        self._view_mode = "list"
        self._refresh_view_toggle_styles()

    def _handle_grid_selection_changed(self, file_paths: object) -> None:
        """处理网格选择变化。"""

        if not isinstance(file_paths, list):
            return
        selected_ids: list[str] = []
        for path in file_paths:
            if not isinstance(path, str):
                continue
            asset = self._asset_by_path(path)
            if asset is not None:
                selected_ids.append(asset.asset_id)
        self._selected_asset_ids = selected_ids
        if selected_ids:
            self._active_asset_id = selected_ids[0]
        self._refresh_batch_bar()
        self._refresh_action_badges()
        self._refresh_preview_panel()

    def _handle_table_row_selected(self, row: int) -> None:
        """处理列表行选择。"""

        if not (0 <= row < len(self._filtered_assets)):
            return
        asset = self._filtered_assets[row]
        self._selected_asset_ids = [asset.asset_id]
        self._active_asset_id = asset.asset_id
        self._refresh_batch_bar()
        self._refresh_action_badges()
        self._refresh_preview_panel()

    def _handle_table_row_double_clicked(self, row: int) -> None:
        """处理列表双击。"""

        if not (0 <= row < len(self._filtered_assets)):
            return
        self._open_media_preview_by_path(self._filtered_assets[row].file_path)

    def _handle_files_added(self, files: object) -> None:
        """处理拖拽或选择文件。"""

        if not isinstance(files, list) or not files:
            return
        self._file_uploader.set_selected_files([str(file_path) for file_path in files if isinstance(file_path, str)])
        base_index = len(self._all_assets) + 1
        for offset, file_path in enumerate(files, start=1):
            if not isinstance(file_path, str):
                continue
            suffix = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
            asset_type = "图片" if suffix in {"png", "jpg", "jpeg", "webp"} else "视频" if suffix in {"mp4", "mov", "avi"} else "音频" if suffix in {"mp3", "wav"} else "文档"
            file_name = file_path.replace("\\", "/").split("/")[-1]
            size_value = 18 + offset * 7
            new_asset = AssetRecord(
                f"mtc-auto-{base_index + offset}",
                file_path,
                file_name.rsplit(".", 1)[0],
                asset_type,
                "临时上传",
                self._collection_filter if self._collection_filter != "全部素材" else "全部素材",
                "当前会话",
                float(size_value),
                f"{size_value:.1f} MB",
                "1080×1920" if asset_type == "视频" else "1500×1500" if asset_type == "图片" else "文档",
                suffix.upper() or "文件",
                "00:12" if asset_type in {"视频", "音频"} else "静帧",
                "2026-03-09",
                "处理中",
                ("新上传", "待整理"),
                "来自拖拽或文件选择的新素材，待进一步分类与打标。",
                "#00F2EA",
                True,
            )
            self._all_assets.insert(0, new_asset)
            self._upload_tasks.insert(0, UploadTask(file_name, asset_type, "等待入库", min(100, 18 * offset), f"{size_value:.1f} MB"))
        self._active_asset_id = self._all_assets[0].asset_id
        self._selected_asset_ids = [self._active_asset_id]
        self._refresh_all_views()

    def _handle_batch_download(self) -> None:
        """模拟批量下载。"""

        selected_count = len(self._selected_asset_ids)
        if selected_count == 0:
            self._ops_badge.setText("请先选择素材")
            self._ops_badge.set_tone("warning")
            return
        self._ops_badge.setText(f"已发起 {selected_count} 项下载")
        self._ops_badge.set_tone("success")

    def _handle_batch_delete(self) -> None:
        """模拟批量删除。"""

        if not self._selected_asset_ids:
            self._ops_badge.setText("暂无可删除项")
            self._ops_badge.set_tone("warning")
            return
        deleting_ids = set(self._selected_asset_ids)
        self._all_assets = [asset for asset in self._all_assets if asset.asset_id not in deleting_ids]
        self._selected_asset_ids = []
        if self._all_assets:
            self._active_asset_id = self._all_assets[0].asset_id
        self._ops_badge.setText("已移除所选素材")
        self._ops_badge.set_tone("success")
        self._refresh_all_views()

    def _handle_batch_tag(self) -> None:
        """模拟批量打标签。"""

        if not self._selected_asset_ids:
            self._ops_badge.setText("请先选择素材")
            self._ops_badge.set_tone("warning")
            return
        self._tag_filter = "高转化"
        self._tag_dropdown.set_current_text("高转化")
        self._ops_badge.setText("已应用批量标签：高转化")
        self._ops_badge.set_tone("brand")
        self._refresh_all_views()

    def _handle_clear_selection(self) -> None:
        """清空当前选择。"""

        self._selected_asset_ids = []
        self._refresh_batch_bar()
        self._refresh_action_badges()

    def _apply_suggested_tag(self, tag: str) -> None:
        """应用标签建议。"""

        self._tag_filter = tag
        self._tag_dropdown.set_current_text(tag)
        self._search_bar.setText(tag)
        self._refresh_all_views()

    def _open_media_preview(self) -> None:
        """打开当前素材的弹窗预览。"""

        active_asset = self._active_asset()
        if active_asset is None:
            return
        self._preview_dialog.set_media(active_asset.file_path)
        _call(self._preview_dialog, "show")

    def _open_media_preview_by_path(self, file_path: str) -> None:
        """按路径打开媒体预览。"""

        asset = self._asset_by_path(file_path)
        if asset is not None:
            self._active_asset_id = asset.asset_id
            self._selected_asset_ids = [asset.asset_id]
            self._refresh_preview_panel()
            self._refresh_batch_bar()
            self._refresh_action_badges()
        self._preview_dialog.set_media(file_path)
        _call(self._preview_dialog, "show")

    def _active_asset(self) -> AssetRecord | None:
        """返回当前激活素材。"""

        for asset in self._all_assets:
            if asset.asset_id == self._active_asset_id:
                return asset
        return self._filtered_assets[0] if self._filtered_assets else None

    def _asset_by_path(self, file_path: str) -> AssetRecord | None:
        """按路径查找素材。"""

        for asset in self._all_assets:
            if asset.file_path == file_path:
                return asset
        return None

    def _index_of_asset(self, asset_id: str, assets: list[AssetRecord]) -> int:
        """在列表中定位素材索引。"""

        for index, asset in enumerate(assets):
            if asset.asset_id == asset_id:
                return index
        return -1

    def _apply_page_styles(self) -> None:
        """应用页面样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#materialCenterPage {{
                background: {colors.surface_alt};
            }}
            QFrame#materialCenterFilterShell,
            QFrame#materialCenterBatchBar,
            QFrame#materialGridPanel,
            QFrame#materialListPanel {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#materialCenterKpiStrip > QFrame#kpiCard {{
                min-height: 148px;
            }}
            QLabel#materialFolderTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#materialFolderSubtitle,
            QLabel#materialPreviewMeta,
            QLabel#materialBatchSummary,
            QLabel#materialCenterFilterSubtitle {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#materialPreviewName,
            QLabel#materialPanelTitle,
            QLabel#materialCenterFilterTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#materialPreviewDescription {{
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                line-height: 1.6;
            }}
            QLabel#materialSuggestionLabel {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#materialSuggestionButton {{
                min-height: {BUTTON_HEIGHT - 6}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                border-radius: {RADIUS_MD}px;
                border: 1px solid {_rgba(_token('brand.primary'), 0.22)};
                background-color: {_rgba(_token('brand.primary'), 0.08)};
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.medium')};
            }}
            QPushButton#materialSuggestionButton:hover {{
                background-color: {_rgba(_token('brand.primary'), 0.16)};
                border-color: {_rgba(_token('brand.primary'), 0.34)};
            }}
            QWidget#materialViewStack {{
                background: transparent;
            }}
            QFrame#materialGridPanel,
            QFrame#materialListPanel {{
                min-height: {SPACING_2XL * 12}px;
            }}
            """,
        )

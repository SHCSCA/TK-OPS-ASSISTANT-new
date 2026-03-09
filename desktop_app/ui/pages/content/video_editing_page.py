# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportAssignmentType=false

from __future__ import annotations

"""视频剪辑页面。"""

from dataclasses import dataclass
from typing import Final

from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    DragDropZone,
    FileUploaderWidget,
    FilterDropdown,
    IconButton,
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
    SPACING_XS,
    SPACING_XL,
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
    """将十六进制颜色转换为 rgba。"""

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
    """将时长文本转为秒。"""

    parts = [part.strip() for part in text.split(":") if part.strip()]
    if len(parts) != 2:
        return 15
    minutes = int(parts[0]) if parts[0].isdigit() else 0
    seconds = int(parts[1]) if parts[1].isdigit() else 0
    return max(1, minutes * 60 + seconds)


def _category_matches(category: str, filter_value: str) -> bool:
    """判断素材分类是否匹配筛选项。"""

    return filter_value == "全部" or category == filter_value


@dataclass(frozen=True)
class ClipRecord:
    """素材仓中的视频片段。"""

    clip_id: str
    file_path: str
    name: str
    category: str
    duration: str
    resolution: str
    fps: str
    status: str
    scene: str
    tags: tuple[str, ...]
    accent: str
    effect_name: str
    transition_name: str
    overlay_name: str
    note: str


@dataclass(frozen=True)
class EffectPreset:
    """效果库条目。"""

    name: str
    category: str
    intensity: str
    detail: str
    accent: str


@dataclass(frozen=True)
class AudioTrackRecord:
    """音轨条目。"""

    track_id: str
    name: str
    duration: str
    volume: str
    status: str
    tags: tuple[str, ...]
    accent: str


@dataclass(frozen=True)
class ExportPreset:
    """导出预设。"""

    title: str
    resolution: str
    format_label: str
    quality: str
    bitrate: str
    target: str
    active: bool = False


@dataclass(frozen=True)
class HistoryRow:
    """操作记录。"""

    time_label: str
    action: str
    result: str


PAGE_MIN_HEIGHT: Final[int] = 780
LEFT_PANEL_MIN: Final[int] = 328
CENTER_MIN: Final[int] = 760
RIGHT_PANEL_MIN: Final[int] = 336
TIMELINE_SEGMENT_HEIGHT: Final[int] = 38
CLIP_CATEGORIES: Final[tuple[str, ...]] = ("开场", "卖点", "实拍", "封面", "口播", "字幕")
RESOLUTION_OPTIONS: Final[tuple[str, ...]] = ("1080×1920", "720×1280", "1080×1080", "2160×3840")
FORMAT_OPTIONS: Final[tuple[str, ...]] = ("MP4", "MOV", "WEBM")
QUALITY_OPTIONS: Final[tuple[str, ...]] = ("高质量", "标准", "极速导出")
EFFECT_TABS: Final[tuple[str, ...]] = ("滤镜", "转场", "文字叠层")

CLIP_LIBRARY: Final[tuple[ClipRecord, ...]] = (
    ClipRecord("clip-001", "D:/demo/content/video_editing/开场三秒航拍.mp4", "开场三秒航拍", "开场", "00:08", "1080×1920", "30fps", "已就绪", "街景拉近", ("高点击开场", "品牌视觉"), "#00F2EA", "冷白清透", "闪白切换", "首屏大字标题", "用于首屏钩子与镜头建立。"),
    ClipRecord("clip-002", "D:/demo/content/video_editing/模特拿起产品特写.mp4", "模特拿起产品特写", "卖点", "00:11", "1080×1920", "30fps", "已就绪", "手部特写", ("高转化", "场景实拍"), "#22C55E", "高对比锐化", "快速推进", "卖点角标", "用于放大第一触感与质感细节。"),
    ClipRecord("clip-003", "D:/demo/content/video_editing/实际使用场景01.mp4", "实际使用场景 01", "实拍", "00:15", "1080×1920", "30fps", "已就绪", "桌面布置", ("场景实拍", "节奏切片"), "#F59E0B", "暖调氛围", "平滑溶解", "场景说明卡", "适合衔接功能演示与真实体验。"),
    ClipRecord("clip-004", "D:/demo/content/video_editing/对比镜头前后版.mp4", "对比镜头前后版", "卖点", "00:14", "1080×1920", "60fps", "已就绪", "前后对比", ("对比卖点", "高转化"), "#F97316", "高饱和冲击", "推拉擦除", "对比数据板", "用于突出结果差异与核心提升。"),
    ClipRecord("clip-005", "D:/demo/content/video_editing/封面停留页A.jpg", "封面停留页 A", "封面", "00:03", "1242×1660", "静帧", "已就绪", "封面画面", ("封面备选", "品牌视觉"), "#FB7185", "胶片柔焦", "无", "封面主标题", "适合作为首帧封面与停留画面。"),
    ClipRecord("clip-006", "D:/demo/content/video_editing/人物口播强调句.mp4", "人物口播强调句", "口播", "00:12", "1080×1920", "30fps", "处理中", "人物口播", ("节奏切片", "字幕包"), "#A78BFA", "清晰锐化", "闪白切换", "关键词高亮", "用于强化核心信息与购买理由。"),
    ClipRecord("clip-007", "D:/demo/content/video_editing/细节纹理微距01.mp4", "细节纹理微距 01", "卖点", "00:09", "1080×1920", "60fps", "已就绪", "纹理微距", ("高转化", "对比卖点"), "#14B8A6", "微距增强", "快速推进", "局部说明字", "适合作为第二卖点特写。"),
    ClipRecord("clip-008", "D:/demo/content/video_editing/用户开箱桌拍.mp4", "用户开箱桌拍", "实拍", "00:13", "1080×1920", "30fps", "已就绪", "桌拍开箱", ("场景实拍", "高点击开场"), "#06B6D4", "清爽明亮", "平滑溶解", "开箱说明条", "用于提升真实感与代入感。"),
    ClipRecord("clip-009", "D:/demo/content/video_editing/字幕节奏模版片段.mp4", "字幕节奏模板片段", "字幕", "00:07", "1080×1920", "30fps", "已就绪", "文字节奏", ("字幕包", "品牌视觉"), "#38BDF8", "霓虹高亮", "无", "高频节奏字", "用于快速套用字幕节奏风格。"),
    ClipRecord("clip-010", "D:/demo/content/video_editing/结尾促单收束.mp4", "结尾促单收束", "口播", "00:10", "1080×1920", "30fps", "已就绪", "结尾 CTA", ("高转化", "品牌视觉"), "#10B981", "暖色提亮", "推拉擦除", "结尾行动按钮", "用于结尾收束和行动引导。"),
    ClipRecord("clip-011", "D:/demo/content/video_editing/品牌片头条纹背景.mov", "品牌片头条纹背景", "开场", "00:06", "1080×1920", "30fps", "已就绪", "品牌背景", ("品牌视觉", "封面备选"), "#6366F1", "深色电影感", "闪白切换", "品牌标识条", "适合做系列化片头模板。"),
    ClipRecord("clip-012", "D:/demo/content/video_editing/参数说明停留卡.mp4", "参数说明停留卡", "字幕", "00:05", "1080×1920", "30fps", "已就绪", "信息停留", ("字幕包", "对比卖点"), "#F43F5E", "高对比图文", "平滑溶解", "参数表格卡", "用于功能参数停留与说明。"),
)

FILTER_LIBRARY: Final[tuple[EffectPreset, ...]] = (
    EffectPreset("冷白清透", "滤镜", "72%", "压低黄调，强调轻盈与科技感。", "#00F2EA"),
    EffectPreset("暖调氛围", "滤镜", "48%", "适合生活方式场景与人物镜头。", "#F59E0B"),
    EffectPreset("高对比锐化", "滤镜", "64%", "强化产品边缘与纹理细节。", "#22C55E"),
    EffectPreset("胶片柔焦", "滤镜", "38%", "适合封面停留页与情绪镜头。", "#FB7185"),
    EffectPreset("霓虹高亮", "滤镜", "55%", "用于字幕卡、科技感开场与说明页。", "#38BDF8"),
    EffectPreset("深色电影感", "滤镜", "60%", "拉高高级感，适合品牌片头。", "#6366F1"),
)

TRANSITION_LIBRARY: Final[tuple[EffectPreset, ...]] = (
    EffectPreset("闪白切换", "转场", "0.18s", "适合开场与重点句切入。", "#F43F5E"),
    EffectPreset("平滑溶解", "转场", "0.32s", "适合场景切换与人物过渡。", "#00F2EA"),
    EffectPreset("推拉擦除", "转场", "0.26s", "强调节奏推进和对比冲击。", "#F59E0B"),
    EffectPreset("镜头甩动", "转场", "0.20s", "适合快节奏带动和速度感。", "#A78BFA"),
    EffectPreset("缩放切入", "转场", "0.24s", "卖点放大与细节特写常用。", "#14B8A6"),
)

OVERLAY_LIBRARY: Final[tuple[EffectPreset, ...]] = (
    EffectPreset("首屏大字标题", "文字叠层", "2.0s", "用于首屏钩子，强调强刺激关键词。", "#00F2EA"),
    EffectPreset("卖点角标", "文字叠层", "3.2s", "适合跟随产品细节镜头出现。", "#22C55E"),
    EffectPreset("关键词高亮", "文字叠层", "2.4s", "口播关键词同步跳出。", "#F43F5E"),
    EffectPreset("参数表格卡", "文字叠层", "4.0s", "用于参数、规格、对比说明。", "#38BDF8"),
    EffectPreset("结尾行动按钮", "文字叠层", "2.8s", "在结尾推动下一步动作。", "#F59E0B"),
)

AUDIO_LIBRARY: Final[tuple[AudioTrackRecord, ...]] = (
    AudioTrackRecord("audio-001", "快节奏鼓点循环", "00:15", "82%", "已同步", ("节奏切片", "高点击开场"), "#E879F9"),
    AudioTrackRecord("audio-002", "环境氛围铺底", "00:31", "36%", "已同步", ("音效氛围", "场景实拍"), "#14B8A6"),
    AudioTrackRecord("audio-003", "结尾提示音", "00:03", "64%", "已同步", ("品牌视觉",), "#F97316"),
    AudioTrackRecord("audio-004", "口播降噪轨", "00:12", "100%", "处理中", ("字幕包",), "#38BDF8"),
)

EXPORT_PRESETS: Final[tuple[ExportPreset, ...]] = (
    ExportPreset("信息流竖屏标准", "1080×1920", "MP4", "高质量", "12 Mbps", "信息流发布", True),
    ExportPreset("极速复盘样片", "720×1280", "MP4", "极速导出", "6 Mbps", "内部评审"),
    ExportPreset("品牌归档母版", "2160×3840", "MOV", "高质量", "28 Mbps", "品牌资产库"),
    ExportPreset("封面拆条方版", "1080×1080", "MP4", "标准", "8 Mbps", "封面与二次分发"),
)


class VideoEditingPage(BasePage):
    """视频剪辑工作台，包含素材仓、预览、时间轴与导出配置。"""

    default_route_id: RouteId = RouteId("video_editing")
    default_display_name: str = "视频剪辑"
    default_icon_name: str = "video_settings"

    def setup_ui(self) -> None:
        """构建视频剪辑页面。"""

        self._all_clips: list[ClipRecord] = list(CLIP_LIBRARY)
        self._filtered_clips: list[ClipRecord] = []
        self._audio_tracks: list[AudioTrackRecord] = list(AUDIO_LIBRARY)
        self._selected_clip_id: str = self._all_clips[0].clip_id
        self._search_text = ""
        self._category_filter = "全部"
        self._current_effect_tab = 0
        self._selected_filter = FILTER_LIBRARY[0].name
        self._selected_transition = TRANSITION_LIBRARY[0].name
        self._selected_overlay = OVERLAY_LIBRARY[0].name
        self._resolution = EXPORT_PRESETS[0].resolution
        self._format = EXPORT_PRESETS[0].format_label
        self._quality = EXPORT_PRESETS[0].quality
        self._history_rows: list[HistoryRow] = [
            HistoryRow("10:02", "导入素材包", "已新增 3 个片段"),
            HistoryRow("10:08", "应用滤镜", "冷白清透 已同步到当前片段"),
            HistoryRow("10:15", "保存草稿", "草稿版本 V3 已生成"),
        ]
        self._bin_cards: list[ThumbnailCard] = []
        self._filter_buttons: list[QPushButton] = []
        self._transition_buttons: list[QPushButton] = []
        self._overlay_buttons: list[QPushButton] = []
        self._export_preset_buttons: list[QPushButton] = []
        self._preview_dialog = MediaPreview(parent=self)

        _call(self, "setObjectName", "videoEditingPage")
        _call(self, "setMinimumHeight", PAGE_MIN_HEIGHT)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._page_container = PageContainer(
            title=self.display_name,
            description="为 TikTok 内容制作提供导入、预览、时间轴排布、效果应用与导出配置的一体化工作区。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._editing_badge = StatusBadge("剪辑工作区已就绪", tone="success", parent=self._page_container)
        self._draft_badge = StatusBadge("草稿：V3", tone="brand", parent=self._page_container)
        self._export_badge = StatusBadge("待导出", tone="neutral", parent=self._page_container)
        self._page_container.add_action(self._editing_badge)
        self._page_container.add_action(self._draft_badge)
        self._page_container.add_action(self._export_badge)

        self._page_container.add_widget(self._build_top_toolbar())
        self._page_container.add_widget(self._build_workspace())

        self._bind_interactions()
        self._refresh_all_views()

    def _build_top_toolbar(self) -> QWidget:
        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "videoEditingToolbar")
        _call(toolbar, "setProperty", "variant", "card")
        layout = QVBoxLayout(toolbar)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        intro_row = QHBoxLayout()
        intro_row.setContentsMargins(0, 0, 0, 0)
        intro_row.setSpacing(SPACING_LG)

        intro_copy = QWidget(toolbar)
        intro_copy_layout = QVBoxLayout(intro_copy)
        intro_copy_layout.setContentsMargins(0, 0, 0, 0)
        intro_copy_layout.setSpacing(SPACING_XS)
        intro_title = QLabel("工程工具栏", intro_copy)
        _call(intro_title, "setObjectName", "videoToolbarTitle")
        intro_subtitle = QLabel("统一导入、保存、导出与撤销动作，保持与素材页相同的顶部操作节奏。", intro_copy)
        _call(intro_subtitle, "setObjectName", "videoToolbarSubtitle")
        _call(intro_subtitle, "setWordWrap", True)
        intro_copy_layout.addWidget(intro_title)
        intro_copy_layout.addWidget(intro_subtitle)

        intro_badges = QWidget(toolbar)
        intro_badges_layout = QHBoxLayout(intro_badges)
        intro_badges_layout.setContentsMargins(0, 0, 0, 0)
        intro_badges_layout.setSpacing(SPACING_SM)
        intro_badges_layout.addWidget(StatusBadge("时间轴已同步", tone="success", parent=intro_badges))
        intro_badges_layout.addWidget(StatusBadge("导出预设已加载", tone="brand", parent=intro_badges))

        intro_row.addWidget(intro_copy, 1)
        intro_row.addWidget(intro_badges)

        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(0, 0, 0, 0)
        controls_row.setSpacing(SPACING_LG)

        self._import_button = PrimaryButton("导入素材", toolbar, icon_text="＋")
        self._export_button = PrimaryButton("导出成片", toolbar, icon_text="⇪")
        self._save_button = SecondaryButton("保存草稿", toolbar, icon_text="✓")
        self._undo_button = IconButton("↶", "撤销", toolbar)
        self._redo_button = IconButton("↷", "重做", toolbar)
        self._toolbar_status = QLabel("当前工程：春季爆款主视频 · 竖屏成片 27 秒", toolbar)
        _call(self._toolbar_status, "setObjectName", "videoToolbarStatus")

        controls_row.addWidget(self._import_button)
        controls_row.addWidget(self._export_button)
        controls_row.addWidget(self._save_button)
        controls_row.addWidget(self._undo_button)
        controls_row.addWidget(self._redo_button)
        controls_row.addWidget(self._toolbar_status, 1)

        layout.addLayout(intro_row)
        layout.addLayout(controls_row)
        return toolbar

    def _build_workspace(self) -> QWidget:
        outer_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.78, 0.22),
            minimum_sizes=(LEFT_PANEL_MIN + CENTER_MIN, RIGHT_PANEL_MIN),
            parent=self,
        )
        outer_split.set_first_widget(self._build_main_workspace())
        outer_split.set_second_widget(self._build_inspector_panel())
        return outer_split

    def _build_main_workspace(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        top_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.30, 0.70),
            minimum_sizes=(LEFT_PANEL_MIN, CENTER_MIN),
            parent=panel,
        )
        top_split.set_first_widget(self._build_media_bin_panel())
        top_split.set_second_widget(self._build_preview_center_panel())

        self._timeline_section = self._build_timeline_panel()

        layout.addWidget(top_split)
        layout.addWidget(self._timeline_section)
        return panel

    def _build_media_bin_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._media_bin_section = ContentSection("媒体箱", icon="▣", parent=panel)
        section_layout = self._media_bin_section.content_layout

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(SPACING_MD)
        self._clip_count_badge = StatusBadge("0 个片段", tone="brand", parent=self._media_bin_section)
        self._bin_sync_badge = StatusBadge("自动整理已开启", tone="success", parent=self._media_bin_section)
        header.addWidget(self._clip_count_badge)
        header.addWidget(self._bin_sync_badge)
        header.addStretch(1)

        self._media_search = SearchBar("搜索片段名称、场景或标签...")
        self._category_dropdown = FilterDropdown("片段分类", CLIP_CATEGORIES, include_all=True)
        self._drag_drop_zone = DragDropZone()
        self._file_uploader = FileUploaderWidget()

        cards_shell = QWidget(self._media_bin_section)
        self._clip_cards_layout = QVBoxLayout(cards_shell)
        self._clip_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._clip_cards_layout.setSpacing(SPACING_MD)

        section_layout.addLayout(header)
        section_layout.addWidget(self._media_search)
        section_layout.addWidget(self._category_dropdown)
        section_layout.addWidget(self._drag_drop_zone)
        section_layout.addWidget(self._file_uploader)
        section_layout.addWidget(cards_shell)

        layout.addWidget(self._media_bin_section)
        return panel

    def _build_preview_center_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._preview_section = ContentSection("预览区", icon="▶", parent=panel)
        preview_layout = self._preview_section.content_layout

        top_meta = QWidget(self._preview_section)
        meta_layout = QHBoxLayout(top_meta)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(SPACING_MD)
        self._preview_title = QLabel("--", self._preview_section)
        _call(self._preview_title, "setObjectName", "videoPreviewTitle")
        self._preview_scene = QLabel("--", self._preview_section)
        _call(self._preview_scene, "setObjectName", "videoPreviewMeta")
        self._preview_status_badge = StatusBadge("已就绪", tone="success", parent=self._preview_section)
        meta_layout.addWidget(self._preview_title)
        meta_layout.addWidget(self._preview_scene)
        meta_layout.addStretch(1)
        meta_layout.addWidget(self._preview_status_badge)

        self._preview_player = VideoPlayerWidget(parent=self._preview_section)

        playback_bar = QWidget(self._preview_section)
        playback_layout = QHBoxLayout(playback_bar)
        playback_layout.setContentsMargins(0, 0, 0, 0)
        playback_layout.setSpacing(SPACING_MD)
        self._fit_button = SecondaryButton("自适应画布", playback_bar)
        self._safe_area_button = SecondaryButton("安全框", playback_bar)
        self._marker_button = SecondaryButton("添加标记", playback_bar)
        self._fullscreen_button = PrimaryButton("弹窗预览", playback_bar)
        self._preview_note = QLabel("已同步口播节奏、字幕层与音轨音量。", playback_bar)
        _call(self._preview_note, "setObjectName", "videoPreviewMeta")
        playback_layout.addWidget(self._fit_button)
        playback_layout.addWidget(self._safe_area_button)
        playback_layout.addWidget(self._marker_button)
        playback_layout.addWidget(self._fullscreen_button)
        playback_layout.addWidget(self._preview_note, 1)

        preview_layout.addWidget(top_meta)
        preview_layout.addWidget(self._preview_player)
        preview_layout.addWidget(playback_bar)

        self._effects_section = ContentSection("效果库", icon="✦", parent=panel)
        effects_layout = self._effects_section.content_layout
        self._effects_tab_bar = TabBar(self._effects_section)

        self._filter_tab_widget = QWidget(self._effects_tab_bar)
        self._filter_tab_layout = QVBoxLayout(self._filter_tab_widget)
        self._filter_tab_layout.setContentsMargins(0, 0, 0, 0)
        self._filter_tab_layout.setSpacing(SPACING_MD)

        self._transition_tab_widget = QWidget(self._effects_tab_bar)
        self._transition_tab_layout = QVBoxLayout(self._transition_tab_widget)
        self._transition_tab_layout.setContentsMargins(0, 0, 0, 0)
        self._transition_tab_layout.setSpacing(SPACING_MD)

        self._overlay_tab_widget = QWidget(self._effects_tab_bar)
        self._overlay_tab_layout = QVBoxLayout(self._overlay_tab_widget)
        self._overlay_tab_layout.setContentsMargins(0, 0, 0, 0)
        self._overlay_tab_layout.setSpacing(SPACING_MD)

        self._effects_tab_bar.add_tab(EFFECT_TABS[0], self._filter_tab_widget)
        self._effects_tab_bar.add_tab(EFFECT_TABS[1], self._transition_tab_widget)
        self._effects_tab_bar.add_tab(EFFECT_TABS[2], self._overlay_tab_widget)
        effects_layout.addWidget(self._effects_tab_bar)

        layout.addWidget(self._preview_section)
        layout.addWidget(self._effects_section)
        return panel

    def _build_timeline_panel(self) -> QWidget:
        panel = ContentSection("时间轴与音轨", icon="▬", parent=self)
        layout = panel.content_layout

        controls = QWidget(panel)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(SPACING_MD)
        self._timeline_zoom_badge = StatusBadge("缩放 120%", tone="brand", parent=panel)
        self._timeline_info = QLabel("当前总时长 00:27 · 3 条视频轨 · 2 条音频轨", panel)
        _call(self._timeline_info, "setObjectName", "timelineMeta")
        self._zoom_out_button = IconButton("－", "缩小时间轴", panel)
        self._zoom_in_button = IconButton("＋", "放大时间轴", panel)
        self._snap_button = SecondaryButton("吸附对齐", controls)
        self._ripple_button = SecondaryButton("波纹编辑", controls)
        controls_layout.addWidget(self._timeline_zoom_badge)
        controls_layout.addWidget(self._timeline_info, 1)
        controls_layout.addWidget(self._zoom_out_button)
        controls_layout.addWidget(self._zoom_in_button)
        controls_layout.addWidget(self._snap_button)
        controls_layout.addWidget(self._ripple_button)

        self._timeline_ruler = QWidget(panel)
        self._timeline_ruler_layout = QHBoxLayout(self._timeline_ruler)
        self._timeline_ruler_layout.setContentsMargins(0, 0, 0, 0)
        self._timeline_ruler_layout.setSpacing(SPACING_SM)

        self._timeline_tracks_host = QWidget(panel)
        self._timeline_tracks_layout = QVBoxLayout(self._timeline_tracks_host)
        self._timeline_tracks_layout.setContentsMargins(0, 0, 0, 0)
        self._timeline_tracks_layout.setSpacing(SPACING_MD)

        self._audio_section = QWidget(panel)
        self._audio_section_layout = QVBoxLayout(self._audio_section)
        self._audio_section_layout.setContentsMargins(0, 0, 0, 0)
        self._audio_section_layout.setSpacing(SPACING_SM)

        layout.addWidget(controls)
        layout.addWidget(self._timeline_ruler)
        layout.addWidget(self._timeline_tracks_host)
        layout.addWidget(self._audio_section)
        return panel

    def _build_inspector_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._properties_section = ContentSection("属性检查器", icon="◎", parent=panel)
        props_layout = self._properties_section.content_layout
        self._clip_name_label = QLabel("--", self._properties_section)
        _call(self._clip_name_label, "setObjectName", "inspectorTitle")
        self._clip_meta_label = QLabel("--", self._properties_section)
        _call(self._clip_meta_label, "setObjectName", "inspectorMeta")
        self._clip_note_label = QLabel("--", self._properties_section)
        _call(self._clip_note_label, "setObjectName", "inspectorNote")
        _call(self._clip_note_label, "setWordWrap", True)

        self._selected_tags_host = QWidget(self._properties_section)
        self._selected_tags_layout = QHBoxLayout(self._selected_tags_host)
        self._selected_tags_layout.setContentsMargins(0, 0, 0, 0)
        self._selected_tags_layout.setSpacing(SPACING_SM)

        self._inspector_effect_badge = StatusBadge("滤镜：--", tone="brand", parent=self._properties_section)
        self._inspector_transition_badge = StatusBadge("转场：--", tone="neutral", parent=self._properties_section)
        self._inspector_overlay_badge = StatusBadge("文字：--", tone="info", parent=self._properties_section)

        props_layout.addWidget(self._clip_name_label)
        props_layout.addWidget(self._clip_meta_label)
        props_layout.addWidget(self._clip_note_label)
        props_layout.addWidget(self._selected_tags_host)
        props_layout.addWidget(self._inspector_effect_badge)
        props_layout.addWidget(self._inspector_transition_badge)
        props_layout.addWidget(self._inspector_overlay_badge)

        self._export_section = ContentSection("导出设置", icon="⇪", parent=panel)
        export_layout = self._export_section.content_layout
        self._resolution_dropdown = FilterDropdown("分辨率", RESOLUTION_OPTIONS, include_all=False)
        self._format_dropdown = FilterDropdown("格式", FORMAT_OPTIONS, include_all=False)
        self._quality_dropdown = FilterDropdown("质量", QUALITY_OPTIONS, include_all=False)
        self._export_summary = QLabel("--", self._export_section)
        _call(self._export_summary, "setObjectName", "inspectorNote")
        _call(self._export_summary, "setWordWrap", True)

        self._export_presets_host = QWidget(self._export_section)
        self._export_presets_layout = QVBoxLayout(self._export_presets_host)
        self._export_presets_layout.setContentsMargins(0, 0, 0, 0)
        self._export_presets_layout.setSpacing(SPACING_SM)

        export_layout.addWidget(self._resolution_dropdown)
        export_layout.addWidget(self._format_dropdown)
        export_layout.addWidget(self._quality_dropdown)
        export_layout.addWidget(self._export_summary)
        export_layout.addWidget(self._export_presets_host)

        self._history_section = ContentSection("操作记录", icon="⌛", parent=panel)
        history_layout = self._history_section.content_layout
        self._history_table = DataTable(
            headers=("时间", "操作", "结果"),
            rows=(),
            page_size=6,
            empty_text="暂无操作记录",
            parent=self._history_section,
        )
        history_layout.addWidget(self._history_table)

        layout.addWidget(self._properties_section)
        layout.addWidget(self._export_section)
        layout.addWidget(self._history_section)
        return panel

    def _bind_interactions(self) -> None:
        """绑定页面交互。"""

        _connect(getattr(self._import_button, "clicked", None), self._handle_import_clicked)
        _connect(getattr(self._export_button, "clicked", None), self._handle_export_clicked)
        _connect(getattr(self._save_button, "clicked", None), self._handle_save_clicked)
        _connect(getattr(self._undo_button, "clicked", None), self._handle_undo_clicked)
        _connect(getattr(self._redo_button, "clicked", None), self._handle_redo_clicked)
        _connect(self._media_search.search_changed, self._handle_search_changed)
        _connect(self._category_dropdown.filter_changed, self._handle_category_changed)
        _connect(self._drag_drop_zone.files_dropped, self._handle_files_added)
        _connect(self._file_uploader.files_selected, self._handle_files_added)
        _connect(self._effects_tab_bar.tab_changed, self._handle_effect_tab_changed)
        _connect(self._resolution_dropdown.filter_changed, self._handle_resolution_changed)
        _connect(self._format_dropdown.filter_changed, self._handle_format_changed)
        _connect(self._quality_dropdown.filter_changed, self._handle_quality_changed)
        _connect(getattr(self._fullscreen_button, "clicked", None), self._open_preview_dialog)
        _connect(getattr(self._fit_button, "clicked", None), self._handle_fit_canvas)
        _connect(getattr(self._safe_area_button, "clicked", None), self._handle_safe_area)
        _connect(getattr(self._marker_button, "clicked", None), self._handle_add_marker)
        _connect(getattr(self._zoom_in_button, "clicked", None), self._handle_zoom_in)
        _connect(getattr(self._zoom_out_button, "clicked", None), self._handle_zoom_out)
        _connect(getattr(self._snap_button, "clicked", None), self._handle_snap_toggle)
        _connect(getattr(self._ripple_button, "clicked", None), self._handle_ripple_toggle)

    def _refresh_all_views(self) -> None:
        """刷新页面所有视图。"""

        self._apply_filters()
        self._refresh_badges()
        self._refresh_media_bin()
        self._refresh_preview()
        self._refresh_effect_library()
        self._refresh_timeline()
        self._refresh_inspector()
        self._refresh_export_section()
        self._refresh_history_table()

    def _apply_filters(self) -> None:
        """按搜索和分类过滤片段。"""

        normalized_query = self._search_text.strip().lower()
        results: list[ClipRecord] = []
        for clip in self._all_clips:
            if not _category_matches(clip.category, self._category_filter):
                continue
            if normalized_query:
                haystack = " ".join((clip.name, clip.category, clip.scene, clip.note, " ".join(clip.tags))).lower()
                if normalized_query not in haystack:
                    continue
            results.append(clip)
        self._filtered_clips = results
        valid_ids = {clip.clip_id for clip in self._filtered_clips}
        if self._selected_clip_id not in valid_ids and self._filtered_clips:
            self._selected_clip_id = self._filtered_clips[0].clip_id

    def _refresh_badges(self) -> None:
        """刷新页头状态。"""

        self._clip_count_badge.setText(f"{len(self._filtered_clips)} 个片段")
        active_clip = self._active_clip()
        if active_clip is None:
            self._editing_badge.setText("暂无可编辑片段")
            self._editing_badge.set_tone("warning")
            self._clip_count_badge.set_tone("warning")
        else:
            self._editing_badge.setText(f"当前片段：{active_clip.name}")
            self._editing_badge.set_tone("success")
            self._clip_count_badge.set_tone("brand")

    def _refresh_media_bin(self) -> None:
        """刷新左侧媒体箱。"""

        _clear_layout_items(self._clip_cards_layout)
        self._bin_cards = []
        if not self._filtered_clips:
            empty = QFrame(self._media_bin_section)
            _call(empty, "setObjectName", "videoEditingEmptyState")
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
            empty_layout.setSpacing(SPACING_SM)
            title = QLabel("当前筛选下暂无片段", empty)
            _call(title, "setObjectName", "videoPreviewTitle")
            detail = QLabel("可调整分类、清空搜索条件，或直接导入新素材补充媒体箱。", empty)
            _call(detail, "setObjectName", "videoPreviewMeta")
            _call(detail, "setWordWrap", True)
            empty_layout.addWidget(title)
            empty_layout.addWidget(detail)
            self._clip_cards_layout.addWidget(empty)
            self._clip_cards_layout.addStretch(1)
            return
        for clip in self._filtered_clips:
            wrapper = QFrame(self._media_bin_section)
            _call(wrapper, "setObjectName", "clipBinItem")
            wrapper_layout = QVBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
            wrapper_layout.setSpacing(SPACING_SM)

            card = ThumbnailCard(
                clip.file_path,
                duration=clip.duration,
                status="processing" if clip.status == "处理中" else "ready",
                parent=wrapper,
            )
            card.set_selected(clip.clip_id == self._selected_clip_id)
            _connect(card.selection_changed, lambda file_path, checked, clip_id=clip.clip_id: self._handle_clip_selected(clip_id, checked))
            _connect(card.double_clicked, lambda file_path, clip_id=clip.clip_id: self._handle_clip_open_preview(clip_id))

            info_row = QWidget(wrapper)
            info_layout = QHBoxLayout(info_row)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(SPACING_SM)
            title = QLabel(clip.name, info_row)
            _call(title, "setObjectName", "clipBinTitle")
            badge = StatusBadge(clip.category, tone="brand" if clip.clip_id == self._selected_clip_id else "neutral", parent=info_row)
            info_layout.addWidget(title)
            info_layout.addStretch(1)
            info_layout.addWidget(badge)

            meta = QLabel(f"{clip.duration} · {clip.scene} · {clip.status}", wrapper)
            _call(meta, "setObjectName", "clipBinMeta")

            wrapper_layout.addWidget(card)
            wrapper_layout.addWidget(info_row)
            wrapper_layout.addWidget(meta)
            self._clip_cards_layout.addWidget(wrapper)
            self._bin_cards.append(card)
        self._clip_cards_layout.addStretch(1)

    def _refresh_preview(self) -> None:
        """刷新预览区。"""

        active_clip = self._active_clip()
        if active_clip is None:
            self._preview_title.setText("暂无片段")
            self._preview_scene.setText("请导入新片段或调整筛选条件")
            self._preview_status_badge.setText("等待素材")
            self._preview_status_badge.set_tone("warning")
            self._preview_player.set_duration(15)
            self._preview_player.set_position(0)
            return
        self._preview_title.setText(active_clip.name)
        self._preview_scene.setText(f"{active_clip.scene} · {active_clip.duration} · {active_clip.resolution} · {active_clip.fps}")
        self._preview_status_badge.setText(active_clip.status)
        self._preview_status_badge.set_tone("warning" if active_clip.status == "处理中" else "success")
        self._preview_note.setText(f"当前应用：{self._selected_filter} / {self._selected_transition} / {self._selected_overlay}")
        self._preview_player.set_duration(_duration_seconds(active_clip.duration))
        self._preview_player.set_position(0)

    def _refresh_effect_library(self) -> None:
        """刷新效果库按钮。"""

        self._refresh_effect_buttons(self._filter_tab_layout, FILTER_LIBRARY, self._selected_filter, self._filter_buttons, self._apply_filter)
        self._refresh_effect_buttons(self._transition_tab_layout, TRANSITION_LIBRARY, self._selected_transition, self._transition_buttons, self._apply_transition)
        self._refresh_effect_buttons(self._overlay_tab_layout, OVERLAY_LIBRARY, self._selected_overlay, self._overlay_buttons, self._apply_overlay)

    def _refresh_effect_buttons(
        self,
        layout: QVBoxLayout,
        items: tuple[EffectPreset, ...],
        active_name: str,
        store: list[QPushButton],
        callback: object,
    ) -> None:
        """刷新效果库按钮列表。"""

        _clear_layout_items(layout)
        store.clear()
        for item in items:
            button = QPushButton(f"{item.name} · {item.intensity}\n{item.detail}", self)
            _call(button, "setObjectName", "effectLibraryButton")
            _call(button, "setProperty", "active", item.name == active_name)
            _connect(getattr(button, "clicked", None), lambda _checked=False, value=item.name, apply_callback=callback: apply_callback(value))
            layout.addWidget(button)
            store.append(button)
        layout.addStretch(1)

    def _refresh_timeline(self) -> None:
        """刷新时间轴。"""

        _clear_layout_items(self._timeline_ruler_layout)
        for marker in ("00:00", "00:03", "00:06", "00:09", "00:12", "00:15", "00:18", "00:21", "00:24", "00:27"):
            label = QLabel(marker, self._timeline_ruler)
            _call(label, "setObjectName", "timelineRulerLabel")
            self._timeline_ruler_layout.addWidget(label)
        self._timeline_ruler_layout.addStretch(1)

        _clear_layout_items(self._timeline_tracks_layout)
        active_clip = self._active_clip()
        tracks = (
            ("V1 主轨", self._filtered_clips[:4]),
            ("V2 卖点补充", self._filtered_clips[4:8]),
            ("V3 字幕停留", self._filtered_clips[8:12]),
        )
        for title, clips in tracks:
            row = QWidget(self._timeline_tracks_host)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_MD)

            label = QLabel(title, row)
            _call(label, "setObjectName", "timelineTrackLabel")
            row_layout.addWidget(label)

            segments_host = QWidget(row)
            segments_layout = QHBoxLayout(segments_host)
            segments_layout.setContentsMargins(0, 0, 0, 0)
            segments_layout.setSpacing(SPACING_SM)
            for clip in clips:
                segment = QPushButton(f"{clip.name}\n{clip.duration}", segments_host)
                _call(segment, "setObjectName", "timelineSegment")
                _call(segment, "setProperty", "selected", active_clip is not None and clip.clip_id == active_clip.clip_id)
                _call(segment, "setMinimumHeight", TIMELINE_SEGMENT_HEIGHT)
                _call(segment, "setMinimumWidth", 126 + _duration_seconds(clip.duration) * 4)
                _connect(getattr(segment, "clicked", None), lambda _checked=False, clip_id=clip.clip_id: self._select_clip_directly(clip_id))
                segments_layout.addWidget(segment)
            segments_layout.addStretch(1)
            row_layout.addWidget(segments_host, 1)
            self._timeline_tracks_layout.addWidget(row)

        _clear_layout_items(self._audio_section_layout)
        audio_title = QLabel("音频轨", self._audio_section)
        _call(audio_title, "setObjectName", "timelineTrackLabel")
        self._audio_section_layout.addWidget(audio_title)
        for track in self._audio_tracks:
            row = QWidget(self._audio_section)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_MD)
            label = QLabel(f"{track.name} · {track.duration}", row)
            _call(label, "setObjectName", "clipBinTitle")
            badge = StatusBadge(f"音量 {track.volume}", tone="brand", parent=row)
            chip = TagChip(track.tags[0] if track.tags else "音轨", tone="neutral", parent=row)
            segment = QLabel("▁▂▃▄▅▆▅▄▃▂ ▁▂▃▄▅▆▅▄▃▂", row)
            _call(segment, "setObjectName", "audioWaveLabel")
            row_layout.addWidget(label)
            row_layout.addWidget(chip)
            row_layout.addWidget(segment, 1)
            row_layout.addWidget(badge)
            self._audio_section_layout.addWidget(row)

    def _refresh_inspector(self) -> None:
        """刷新右侧属性检查器。"""

        active_clip = self._active_clip()
        if active_clip is None:
            self._clip_name_label.setText("暂无片段")
            self._clip_meta_label.setText("请选择素材")
            self._clip_note_label.setText("导入新素材后可查看时长、效果、转场与叠层属性。")
            self._refresh_selected_tags(())
            return
        self._clip_name_label.setText(active_clip.name)
        self._clip_meta_label.setText(f"{active_clip.category} · {active_clip.duration} · {active_clip.resolution} · {active_clip.fps}")
        self._clip_note_label.setText(active_clip.note)
        self._refresh_selected_tags(active_clip.tags)
        self._inspector_effect_badge.setText(f"滤镜：{self._selected_filter}")
        self._inspector_transition_badge.setText(f"转场：{self._selected_transition}")
        self._inspector_overlay_badge.setText(f"文字：{self._selected_overlay}")

    def _refresh_selected_tags(self, tags: tuple[str, ...]) -> None:
        """刷新当前片段标签。"""

        _clear_layout_items(self._selected_tags_layout)
        if not tags:
            self._selected_tags_layout.addWidget(TagChip("暂无标签", tone="neutral", parent=self._selected_tags_host))
            return
        for tag in tags:
            tone = "brand" if tag in {"高点击开场", "高转化", "品牌视觉"} else "neutral"
            self._selected_tags_layout.addWidget(TagChip(tag, tone=tone, parent=self._selected_tags_host))

    def _refresh_export_section(self) -> None:
        """刷新导出区。"""

        self._resolution_dropdown.set_current_text(self._resolution)
        self._format_dropdown.set_current_text(self._format)
        self._quality_dropdown.set_current_text(self._quality)
        self._export_summary.setText(f"当前导出：{self._resolution} · {self._format} · {self._quality}，适用于短视频竖屏交付与内部复盘。")

        _clear_layout_items(self._export_presets_layout)
        self._export_preset_buttons.clear()
        for preset in EXPORT_PRESETS:
            button = QPushButton(f"{preset.title}\n{preset.resolution} · {preset.format_label} · {preset.quality} · {preset.target}", self._export_presets_host)
            _call(button, "setObjectName", "exportPresetButton")
            is_active = preset.resolution == self._resolution and preset.format_label == self._format and preset.quality == self._quality
            _call(button, "setProperty", "active", is_active)
            _connect(getattr(button, "clicked", None), lambda _checked=False, preset_item=preset: self._apply_export_preset(preset_item))
            self._export_presets_layout.addWidget(button)
            self._export_preset_buttons.append(button)

    def _refresh_history_table(self) -> None:
        """刷新操作历史。"""

        rows = [(row.time_label, row.action, row.result) for row in self._history_rows]
        self._history_table.set_rows(rows)

    def _handle_import_clicked(self) -> None:
        """模拟导入片段。"""

        index = len(self._all_clips) + 1
        new_clip = ClipRecord(
            f"clip-auto-{index}",
            f"D:/demo/content/video_editing/新增导入片段{index}.mp4",
            f"新增导入片段 {index}",
            "实拍",
            "00:08",
            "1080×1920",
            "30fps",
            "处理中",
            "临时导入",
            ("新导入", "待整理"),
            "#00F2EA",
            self._selected_filter,
            self._selected_transition,
            self._selected_overlay,
            "来自导入按钮的新增片段，待归类与套用效果。",
        )
        self._all_clips.insert(0, new_clip)
        self._selected_clip_id = new_clip.clip_id
        self._history_rows.insert(0, HistoryRow("10:28", "导入素材", f"{new_clip.name} 已进入媒体箱"))
        self._export_badge.setText("工程已更新")
        self._export_badge.set_tone("brand")
        self._refresh_all_views()

    def _handle_export_clicked(self) -> None:
        """模拟导出成片。"""

        self._export_badge.setText(f"导出中：{self._resolution} {self._format}")
        self._export_badge.set_tone("warning")
        self._history_rows.insert(0, HistoryRow("10:30", "导出成片", f"使用 {self._resolution} / {self._format} / {self._quality} 提交导出"))
        self._refresh_history_table()

    def _handle_save_clicked(self) -> None:
        """模拟保存草稿。"""

        self._draft_badge.setText("草稿：V4")
        self._draft_badge.set_tone("success")
        self._history_rows.insert(0, HistoryRow("10:31", "保存草稿", "当前时间轴与效果配置已保存"))
        self._refresh_history_table()

    def _handle_undo_clicked(self) -> None:
        """模拟撤销。"""

        self._history_rows.insert(0, HistoryRow("10:32", "撤销一步", "恢复到上一版效果组合"))
        self._toolbar_status.setText("已撤销最近一次属性修改")
        self._refresh_history_table()

    def _handle_redo_clicked(self) -> None:
        """模拟重做。"""

        self._history_rows.insert(0, HistoryRow("10:33", "重做一步", "重新应用最近一次修改"))
        self._toolbar_status.setText("已重做最近一次属性修改")
        self._refresh_history_table()

    def _handle_search_changed(self, text: str) -> None:
        """处理媒体箱搜索。"""

        self._search_text = text
        self._refresh_all_views()

    def _handle_category_changed(self, value: str) -> None:
        """处理分类筛选。"""

        self._category_filter = value
        self._refresh_all_views()

    def _handle_files_added(self, files: object) -> None:
        """处理拖拽或文件选择。"""

        if not isinstance(files, list) or not files:
            return
        self._file_uploader.set_selected_files([str(item) for item in files if isinstance(item, str)])
        for index, file_path in enumerate(files, start=1):
            if not isinstance(file_path, str):
                continue
            name = file_path.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0]
            clip = ClipRecord(
                f"clip-drop-{len(self._all_clips) + index}",
                file_path,
                name,
                "实拍",
                "00:09",
                "1080×1920",
                "30fps",
                "处理中",
                "拖拽导入",
                ("新导入",),
                "#38BDF8",
                self._selected_filter,
                self._selected_transition,
                self._selected_overlay,
                "来自拖拽导入，建议补充标签与转场节奏。",
            )
            self._all_clips.insert(0, clip)
            self._selected_clip_id = clip.clip_id
        self._history_rows.insert(0, HistoryRow("10:34", "拖拽导入", f"已新增 {len(files)} 个片段"))
        self._refresh_all_views()

    def _handle_effect_tab_changed(self, index: int) -> None:
        """处理效果库标签切换。"""

        self._current_effect_tab = index
        tab_name = EFFECT_TABS[index] if 0 <= index < len(EFFECT_TABS) else "效果库"
        self._toolbar_status.setText(f"当前正在浏览：{tab_name}")

    def _handle_resolution_changed(self, value: str) -> None:
        """处理分辨率变化。"""

        self._resolution = value
        self._refresh_export_section()

    def _handle_format_changed(self, value: str) -> None:
        """处理格式变化。"""

        self._format = value
        self._refresh_export_section()

    def _handle_quality_changed(self, value: str) -> None:
        """处理画质变化。"""

        self._quality = value
        self._refresh_export_section()

    def _handle_clip_selected(self, clip_id: str, checked: bool) -> None:
        """处理片段卡片选择。"""

        if not checked:
            return
        self._selected_clip_id = clip_id
        self._refresh_all_views()

    def _handle_clip_open_preview(self, clip_id: str) -> None:
        """双击片段后打开弹窗预览。"""

        self._selected_clip_id = clip_id
        self._refresh_preview()
        active_clip = self._active_clip()
        if active_clip is None:
            return
        self._preview_dialog.set_media(active_clip.file_path)
        _call(self._preview_dialog, "show")

    def _select_clip_directly(self, clip_id: str) -> None:
        """从时间轴直接切换片段。"""

        self._selected_clip_id = clip_id
        self._refresh_all_views()

    def _apply_filter(self, name: str) -> None:
        """应用滤镜。"""

        self._selected_filter = name
        self._history_rows.insert(0, HistoryRow("10:36", "应用滤镜", f"{name} 已应用到当前片段"))
        self._refresh_all_views()

    def _apply_transition(self, name: str) -> None:
        """应用转场。"""

        self._selected_transition = name
        self._history_rows.insert(0, HistoryRow("10:37", "应用转场", f"{name} 已用于片段切换"))
        self._refresh_all_views()

    def _apply_overlay(self, name: str) -> None:
        """应用文字叠层。"""

        self._selected_overlay = name
        self._history_rows.insert(0, HistoryRow("10:38", "应用叠层", f"{name} 已加入当前片段"))
        self._refresh_all_views()

    def _apply_export_preset(self, preset: ExportPreset) -> None:
        """应用导出预设。"""

        self._resolution = preset.resolution
        self._format = preset.format_label
        self._quality = preset.quality
        self._export_badge.setText(f"已切换到：{preset.title}")
        self._export_badge.set_tone("brand")
        self._refresh_export_section()

    def _open_preview_dialog(self) -> None:
        """打开预览弹窗。"""

        active_clip = self._active_clip()
        if active_clip is None:
            return
        self._preview_dialog.set_media(active_clip.file_path)
        _call(self._preview_dialog, "show")

    def _handle_fit_canvas(self) -> None:
        """模拟适配画布。"""

        self._toolbar_status.setText("预览画布已切换为自适应模式")
        self._history_rows.insert(0, HistoryRow("10:39", "画布适配", "已按竖屏安全区自适应缩放"))
        self._refresh_history_table()

    def _handle_safe_area(self) -> None:
        """模拟安全框开关。"""

        self._toolbar_status.setText("安全框参考已高亮")
        self._history_rows.insert(0, HistoryRow("10:40", "显示安全框", "已高亮顶部标题与底部按钮安全区"))
        self._refresh_history_table()

    def _handle_add_marker(self) -> None:
        """模拟添加时间轴标记。"""

        self._toolbar_status.setText("已在 00:08 添加节奏标记")
        self._history_rows.insert(0, HistoryRow("10:41", "添加标记", "00:08 节点已标为卖点切换"))
        self._refresh_history_table()

    def _handle_zoom_in(self) -> None:
        """放大时间轴。"""

        self._timeline_zoom_badge.setText("缩放 140%")
        self._history_rows.insert(0, HistoryRow("10:42", "时间轴放大", "当前时间轴缩放已提升"))
        self._refresh_history_table()

    def _handle_zoom_out(self) -> None:
        """缩小时间轴。"""

        self._timeline_zoom_badge.setText("缩放 100%")
        self._history_rows.insert(0, HistoryRow("10:43", "时间轴缩小", "当前时间轴缩放已降低"))
        self._refresh_history_table()

    def _handle_snap_toggle(self) -> None:
        """切换吸附对齐。"""

        self._toolbar_status.setText("吸附对齐：已开启")
        self._history_rows.insert(0, HistoryRow("10:44", "吸附对齐", "片段边界将自动对齐节拍点"))
        self._refresh_history_table()

    def _handle_ripple_toggle(self) -> None:
        """切换波纹编辑。"""

        self._toolbar_status.setText("波纹编辑：已开启")
        self._history_rows.insert(0, HistoryRow("10:45", "波纹编辑", "删除空隙时自动收紧后续片段"))
        self._refresh_history_table()

    def _active_clip(self) -> ClipRecord | None:
        """返回当前激活片段。"""

        for clip in self._all_clips:
            if clip.clip_id == self._selected_clip_id:
                return clip
        return self._filtered_clips[0] if self._filtered_clips else None

    def _apply_page_styles(self) -> None:
        """应用页面样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#videoEditingPage {{
                background: {colors.surface_alt};
            }}
            QFrame#videoEditingToolbar,
            QFrame#clipBinItem {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#videoEditingEmptyState {{
                background-color: {_rgba(_token('brand.primary'), 0.06)};
                border: 1px dashed {_rgba(_token('brand.primary'), 0.24)};
                border-radius: {RADIUS_LG}px;
                min-height: {SPACING_2XL * 4}px;
            }}
            QLabel#videoToolbarStatus,
            QLabel#videoToolbarSubtitle,
            QLabel#videoPreviewMeta,
            QLabel#clipBinMeta,
            QLabel#timelineMeta,
            QLabel#inspectorMeta {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#videoPreviewTitle,
            QLabel#videoToolbarTitle,
            QLabel#inspectorTitle,
            QLabel#timelineTrackLabel,
            QLabel#clipBinTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#inspectorNote {{
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.6;
            }}
            QLabel#audioWaveLabel,
            QLabel#timelineRulerLabel {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#effectLibraryButton,
            QPushButton#exportPresetButton {{
                min-height: {BUTTON_HEIGHT + SPACING_MD}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                text-align: left;
                border-radius: {RADIUS_MD}px;
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                background-color: {_rgba(_token('brand.primary'), 0.06)};
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#effectLibraryButton:hover,
            QPushButton#exportPresetButton:hover {{
                background-color: {_rgba(_token('brand.primary'), 0.14)};
                border-color: {_rgba(_token('brand.primary'), 0.28)};
            }}
            QPushButton#timelineSegment {{
                padding: {SPACING_SM}px {SPACING_MD}px;
                text-align: left;
                border-radius: {RADIUS_MD}px;
                border: 1px solid {_rgba(_token('brand.primary'), 0.20)};
                background-color: {_rgba(_token('brand.primary'), 0.08)};
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#timelineSegment:hover {{
                background-color: {_rgba(_token('brand.primary'), 0.16)};
            }}
            """,
        )

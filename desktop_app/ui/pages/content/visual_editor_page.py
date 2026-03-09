# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""视觉编辑器页面。"""

from dataclasses import dataclass
from typing import Final

from ....core.qt import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget, QScrollArea
from ....core.types import RouteId
from ...components import (
    DragDropZone,
    FloatingActionButton,
    IconButton,
    ImageGrid,
    StatusBadge,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SplitPanel,
    TabBar,
    ThemedComboBox,
    TimelineWidget,
    VideoPlayerWidget,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage


SURFACE_BG: Final[str] = "#0f1720"
SURFACE_PANEL: Final[str] = "#14212b"
SURFACE_CARD: Final[str] = "#1a2a35"
SURFACE_ALT: Final[str] = "#213443"
SURFACE_MUTED: Final[str] = "#2a4153"
TEXT_PRIMARY: Final[str] = "#eff6fb"
TEXT_SECONDARY: Final[str] = "#a8c0d0"
TEXT_MUTED: Final[str] = "#7e97a8"
ACCENT: Final[str] = "#00F2EA"
ACCENT_SOFT: Final[str] = "rgba(0, 242, 234, 0.14)"
ACCENT_STRONG: Final[str] = "rgba(0, 242, 234, 0.28)"
BORDER: Final[str] = "rgba(168, 192, 208, 0.18)"
BORDER_STRONG: Final[str] = "rgba(168, 192, 208, 0.34)"
SUCCESS: Final[str] = "#22c55e"
WARNING: Final[str] = "#f59e0b"
ERROR: Final[str] = "#ef4444"
PURPLE: Final[str] = "#8b5cf6"
AMBER: Final[str] = "#fbbf24"
INDIGO: Final[str] = "#6366f1"
ROSE: Final[str] = "#fb7185"
CYAN: Final[str] = "#22d3ee"
EMERALD: Final[str] = "#34d399"


@dataclass(frozen=True)
class ToolItem:
    """工具栏项目。"""

    icon: str
    title: str
    detail: str
    shortcut: str
    active: bool = False


@dataclass(frozen=True)
class MediaAsset:
    """媒体仓素材。"""

    file_path: str
    title: str
    category: str
    duration: str
    ratio: str
    status: str
    tag: str
    note: str


@dataclass(frozen=True)
class TemplateItem:
    """模板卡片。"""

    title: str
    scene: str
    duration: str
    emphasis: str
    detail: str


@dataclass(frozen=True)
class FilterPreset:
    """滤镜预设。"""

    name: str
    tone: str
    intensity: str
    style_hint: str
    active: bool = False


@dataclass(frozen=True)
class LayerItem:
    """图层数据。"""

    name: str
    kind: str
    start: str
    end: str
    blend: str
    opacity: str
    locked: bool
    visible: bool
    selected: bool = False


@dataclass(frozen=True)
class TimelineSegment:
    """时间轴片段。"""

    title: str
    subtitle: str
    start: str
    end: str
    offset: int
    width: int
    color: str
    fill: str
    text_color: str
    selected: bool = False


@dataclass(frozen=True)
class TimelineTrack:
    """时间轴轨道。"""

    icon: str
    title: str
    role: str
    color: str
    segments: tuple[TimelineSegment, ...]


@dataclass(frozen=True)
class MarkerItem:
    """时间轴标记。"""

    time: str
    title: str
    level: str
    detail: str
    color: str
    offset: int


@dataclass(frozen=True)
class PropertyMetric:
    """属性面板滑杆。"""

    label: str
    value: int
    unit: str
    hint: str


@dataclass(frozen=True)
class SettingRow:
    """设置项。"""

    title: str
    value: str
    detail: str
    accent: str


@dataclass(frozen=True)
class ExportPreset:
    """导出预设。"""

    title: str
    format_text: str
    bitrate: str
    target: str
    detail: str
    active: bool = False


TOOL_ITEMS: Final[tuple[ToolItem, ...]] = (
    ToolItem("✂", "剪裁", "画面裁切与智能重构", "C", True),
    ToolItem("⧖", "修剪", "片段头尾精修", "T"),
    ToolItem("字", "文字", "标题、贴纸与口播强调", "Y"),
    ToolItem("◌", "滤镜", "风格滤镜与 LUT 调整", "F"),
    ToolItem("♫", "音频", "配乐、降噪与节奏点", "A"),
    ToolItem("▦", "素材", "媒体仓、模板与字幕包", "M"),
)

MEDIA_ASSETS: Final[tuple[MediaAsset, ...]] = (
    MediaAsset("D:/demo/visual_editor/爆品开场航拍.mp4", "爆品开场航拍", "主视频", "00:18", "16:9", "已同步", "高点击", "用于第一页强吸引开场"),
    MediaAsset("D:/demo/visual_editor/卖点特写1.mp4", "卖点特写 1", "细节镜头", "00:09", "9:16", "已同步", "高转化", "展示材质纹理与细节切面"),
    MediaAsset("D:/demo/visual_editor/卖点特写2.mp4", "卖点特写 2", "细节镜头", "00:07", "9:16", "已同步", "节奏补位", "用于转场后的第二重点镜头"),
    MediaAsset("D:/demo/visual_editor/模特实拍A.mp4", "模特实拍 A", "人物展示", "00:16", "9:16", "处理中", "场景化", "强化真实使用氛围"),
    MediaAsset("D:/demo/visual_editor/场景环境图01.jpg", "场景环境图 01", "静态图", "静帧", "4:5", "已同步", "封面备选", "适合制作封面与结尾停留页"),
    MediaAsset("D:/demo/visual_editor/品牌标识透明.png", "品牌标识透明", "图层素材", "静帧", "1:1", "已同步", "品牌资产", "导出时保留品牌识别"),
    MediaAsset("D:/demo/visual_editor/对比字幕条.psd", "对比字幕条", "字幕模板", "模板", "16:9", "已同步", "卖点强调", "突出使用前后对比"),
    MediaAsset("D:/demo/visual_editor/动效贴纸_闪光.webm", "动效贴纸·闪光", "动效素材", "00:03", "透明", "已同步", "氛围增强", "用于价格与优惠节点"),
)

TEMPLATE_ITEMS: Final[tuple[TemplateItem, ...]] = (
    TemplateItem("强卖点快切模板", "爆款短视频", "00:25", "前三秒高能", "适合大促场景，镜头切换密度高，字幕冲击感强。"),
    TemplateItem("达人口播叠加模板", "口播解说", "00:35", "信息清晰", "左侧人物口播，右侧叠加卖点图层，适合知识型转化。"),
    TemplateItem("新品上架首发模板", "新品冷启", "00:20", "质感开箱", "强调开箱、特写、功能演示三个连续段落。"),
    TemplateItem("短视频素材复用模板", "视频二创", "00:40", "高复用", "自动预留字幕安全区，可快速替换短视频素材片段。"),
    TemplateItem("福利冲刺转化模板", "限时促销", "00:15", "优惠强化", "突出价格锚点、限时券和倒计时气氛。"),
)

FILTER_PRESETS: Final[tuple[FilterPreset, ...]] = (
    FilterPreset("清透电商", "提亮肤色", "72%", "适合白底、浅色场景", True),
    FilterPreset("质感银灰", "中性冷调", "48%", "适合数码、家居和高客单价商品"),
    FilterPreset("暖阳生活", "暖色通透", "63%", "适合生活方式和母婴类内容"),
    FilterPreset("夜景霓虹", "高对比霓虹", "54%", "适合潮流、夜拍与门店探店"),
    FilterPreset("高饱和冲击", "亮度增强", "80%", "适合节日活动与福利信息节点"),
    FilterPreset("轻电影感", "轻胶片", "41%", "适合品牌故事和氛围展示"),
)

LAYER_ITEMS: Final[tuple[LayerItem, ...]] = (
    LayerItem("封面标题 · 春季爆品清单", "文字", "00:00", "00:04", "正常", "100%", False, True, True),
    LayerItem("主视频轨道 · 航拍开场", "视频", "00:00", "00:18", "正常", "100%", False, True),
    LayerItem("卖点特写 · 细节镜头", "视频", "00:18", "00:32", "正常", "96%", False, True),
    LayerItem("价格闪光贴纸", "动效", "00:12", "00:17", "滤色", "88%", False, True),
    LayerItem("底部卖点字幕条", "字幕", "00:05", "00:34", "正常", "100%", True, True),
    LayerItem("背景音乐 · 节奏鼓点", "音频", "00:00", "00:42", "正常", "72%", False, True),
    LayerItem("品牌角标", "图像", "00:00", "00:42", "正常", "82%", False, False),
)

TIMELINE_TRACKS: Final[tuple[TimelineTrack, ...]] = (
    TimelineTrack(
        "▶",
        "视频轨道 1",
        "主剪辑",
        ACCENT,
        (
            TimelineSegment("爆品开场航拍", "主视频 · 画面建立", "00:00", "00:18", 18, 280, ACCENT, "rgba(0, 240, 232, 0.20)", TEXT_PRIMARY, True),
            TimelineSegment("卖点特写 1", "近景 · 材质细节", "00:18", "00:27", 308, 158, CYAN, "rgba(34, 211, 238, 0.18)", TEXT_PRIMARY),
            TimelineSegment("卖点特写 2", "中景 · 功能动作", "00:27", "00:35", 474, 146, EMERALD, "rgba(52, 211, 153, 0.18)", TEXT_PRIMARY),
            TimelineSegment("模特实拍 A", "场景化转化片段", "00:35", "00:42", 628, 128, PURPLE, "rgba(139, 92, 246, 0.18)", TEXT_PRIMARY),
        ),
    ),
    TimelineTrack(
        "字",
        "文字轨道",
        "标题 / 卖点",
        AMBER,
        (
            TimelineSegment("标题开场", "春季爆品清单", "00:00", "00:04", 46, 98, AMBER, "rgba(251, 191, 36, 0.18)", "#fde68a"),
            TimelineSegment("核心卖点一", "耐磨防滑升级", "00:06", "00:16", 188, 166, AMBER, "rgba(251, 191, 36, 0.18)", "#fde68a"),
            TimelineSegment("核心卖点二", "三步快速安装", "00:20", "00:30", 396, 172, AMBER, "rgba(251, 191, 36, 0.18)", "#fde68a"),
            TimelineSegment("福利收口", "限时优惠进行中", "00:33", "00:42", 614, 146, AMBER, "rgba(251, 191, 36, 0.18)", "#fde68a"),
        ),
    ),
    TimelineTrack(
        "◎",
        "动效轨道",
        "贴纸 / 价格提示",
        ROSE,
        (
            TimelineSegment("价格闪光", "优惠点强化", "00:12", "00:17", 286, 100, ROSE, "rgba(251, 113, 133, 0.18)", "#fecdd3"),
            TimelineSegment("到手价强调", "券后立省 60", "00:34", "00:39", 640, 92, ROSE, "rgba(251, 113, 133, 0.18)", "#fecdd3"),
        ),
    ),
    TimelineTrack(
        "♫",
        "音频轨道 1",
        "背景音乐",
        INDIGO,
        (
            TimelineSegment("节奏鼓点 BGM", "主音乐 · 轻电子", "00:00", "00:42", 18, 740, INDIGO, "rgba(99, 102, 241, 0.18)", "#c7d2fe"),
        ),
    ),
)

MARKER_ITEMS: Final[tuple[MarkerItem, ...]] = (
    MarkerItem("00:03", "钩子完成", "高优先", "前三秒完成利益点抛出", SUCCESS, 72),
    MarkerItem("00:12", "价格第一次出现", "关键", "建议同步闪光贴纸与音效", WARNING, 288),
    MarkerItem("00:20", "切入安装演示", "说明", "镜头切换后启用第二套字幕模版", ACCENT, 402),
    MarkerItem("00:34", "优惠收口", "关键", "转为福利口播并拉高音乐情绪", ERROR, 640),
)

PROPERTY_METRICS: Final[tuple[PropertyMetric, ...]] = (
    PropertyMetric("画面缩放", 100, "%", "保持 9:16 主体完整"),
    PropertyMetric("位置偏移", 42, "px", "微调至安全区中央"),
    PropertyMetric("不透明度", 96, "%", "与文字层保持层次差"),
    PropertyMetric("阴影强度", 34, "%", "提升亮场可读性"),
    PropertyMetric("羽化过渡", 18, "%", "适合人物边缘柔化"),
    PropertyMetric("锐化程度", 28, "%", "控制在电商清晰度范围"),
)

SETTING_ROWS: Final[tuple[SettingRow, ...]] = (
    SettingRow("项目比例", "1080 × 1920 · 9:16", "适用于 TikTok Shop 商品短视频主流规格", ACCENT),
    SettingRow("帧率策略", "30fps · 智能补帧关闭", "当前镜头动作稳定，优先保证导出效率", CYAN),
    SettingRow("吸附模式", "片段边缘 + 标记点", "对齐字幕入场与价格节点更高效", EMERALD),
    SettingRow("字幕安全区", "已开启", "避免底部购物组件遮挡核心文案", AMBER),
    SettingRow("自动降噪", "中档", "口播环境噪音保守处理，避免失真", PURPLE),
    SettingRow("AI 节奏建议", "本轮已生成", "建议在 00:12 与 00:34 增强音效和特效密度", ROSE),
)

EXPORT_PRESETS: Final[tuple[ExportPreset, ...]] = (
    ExportPreset("标准发布版", "MP4 · H.264", "12 Mbps", "商品详情页 + 短视频投放", "画质与体积平衡，适合日常批量导出", True),
    ExportPreset("高清素材版", "MOV · ProRes Proxy", "45 Mbps", "用于二次加工与复剪", "保留更多细节，便于后续重剪辑"),
    ExportPreset("短视频素材版", "MP4 · H.265", "10 Mbps", "短视频素材复用", "压缩效率更高，适合快速上传"),
    ExportPreset("封面静帧包", "PNG 序列", "静态", "封面测试与 A/B 实验", "同步导出 3 张封面候选帧"),
)

TIMELINE_EVENTS: Final[tuple[dict[str, str], ...]] = (
    {"timestamp": "09:30:10", "title": "导入主视频素材", "content": "已同步 4 段主视频与 2 张静态素材，系统自动识别镜头节奏。", "type": "success"},
    {"timestamp": "09:31:22", "title": "创建标题图层", "content": "标题使用『春季爆品清单』模板，字号 82，描边 4，动画为快速弹入。", "type": "info"},
    {"timestamp": "09:33:04", "title": "插入价格节点", "content": "在 00:12 和 00:34 添加价格强化动效，建议搭配音效敲击。", "type": "warning"},
    {"timestamp": "09:35:18", "title": "完成色彩统一", "content": "已套用『清透电商』滤镜并将亮度提升 6%，肤色和白底更一致。", "type": "success"},
    {"timestamp": "09:37:56", "title": "检测到遮挡风险", "content": "福利文案距底部购物组件安全线仅 14px，建议上移 24px。", "type": "error"},
)


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _set_word_wrap(widget: object, enabled: bool = True) -> None:
    _call(widget, "setWordWrap", enabled)


def _set_object_name(widget: object, name: str) -> None:
    _call(widget, "setObjectName", name)


def _set_fixed_width(widget: object, width: int) -> None:
    _call(widget, "setFixedWidth", width)


def _set_fixed_height(widget: object, height: int) -> None:
    _call(widget, "setFixedHeight", height)


def _set_minimum_height(widget: object, height: int) -> None:
    _call(widget, "setMinimumHeight", height)


def _set_alignment_center(widget: object) -> None:
    alignment_flag = getattr(getattr(__import__("desktop_app.core.qt", fromlist=["Qt"]), "Qt", object), "AlignmentFlag", None)
    align_center = getattr(alignment_flag, "AlignCenter", 0) if alignment_flag is not None else 0
    _call(widget, "setAlignment", align_center)


def _wrap_scroll(content: QWidget) -> QWidget:
    """用滚动容器包裹内容。"""

    scroll = QScrollArea()
    _call(scroll, "setWidgetResizable", True)
    _call(scroll, "setFrameShape", getattr(getattr(QFrame, "Shape", None), "NoFrame", 0))
    _call(scroll, "setWidget", content)
    _call(
        scroll,
        "setStyleSheet",
        (
            "background: transparent; border: none;"
            f"QScrollArea {{ background-color: transparent; border: none; }}"
            f"QScrollBar:vertical {{ width: 8px; background: {SURFACE_PANEL}; border-radius: 4px; }}"
            f"QScrollBar::handle:vertical {{ background: {ACCENT}; border-radius: 4px; min-height: 28px; }}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, "
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; border: none; }"
        ),
    )
    return scroll


def _frame(parent: QWidget | None = None, *, name: str | None = None, style: str | None = None) -> QFrame:
    frame = QFrame(parent)
    if name:
        _set_object_name(frame, name)
    if style:
        _call(frame, "setStyleSheet", style)
    return frame


def _label(
    text: str,
    parent: QWidget | None = None,
    *,
    name: str | None = None,
    style: str | None = None,
    wrap: bool = False,
) -> QLabel:
    widget = QLabel(text, parent)
    if name:
        _set_object_name(widget, name)
    if wrap:
        _set_word_wrap(widget, True)
    if style:
        _call(widget, "setStyleSheet", style)
    return widget


def _panel_style(background: str = SURFACE_PANEL, border: str = BORDER, radius: int = 16) -> str:
    return (
        f"background-color: {background};"
        f"border: 1px solid {border};"
        f"border-radius: {radius}px;"
        f"color: {TEXT_PRIMARY};"
    )


def _card_style(background: str = SURFACE_CARD, border: str = BORDER, radius: int = 14) -> str:
    return (
        f"background-color: {background};"
        f"border: 1px solid {border};"
        f"border-radius: {radius}px;"
        f"color: {TEXT_PRIMARY};"
    )


class VisualEditorPage(BasePage):
    """内容视觉编辑器页面。"""

    default_route_id = RouteId("visual_editor")
    default_display_name = "视觉编辑器"
    default_icon_name = "movie_edit"

    def setup_ui(self) -> None:
        self._inspector_stack: QStackedWidget | None = None
        self._inspector_buttons: list[QWidget] = []
        self._media_grid: ImageGrid | None = None
        self._timeline_widget: TimelineWidget | None = None

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(self, "setStyleSheet", f"background-color: {SURFACE_BG}; color: {TEXT_PRIMARY};")

        page_container = PageContainer(
            title="",
            description="",
            max_width=1760,
            parent=self,
        )
        page_container.content_layout.setSpacing(18)

        page_container.add_widget(self._build_header_bar())
        page_container.add_widget(self._build_workspace_shell())

        self.layout.addWidget(page_container)

    def _build_header_bar(self) -> QWidget:
        header = _frame(name="visualEditorHeader", style=_panel_style(SURFACE_PANEL, BORDER_STRONG, 20))
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        brand_shell = _frame(header, style="background-color: transparent; border: none;")
        brand_layout = QHBoxLayout(brand_shell)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(12)

        brand_icon = _label(
            "▶",
            brand_shell,
            style=(
                f"background-color: {ACCENT}; color: #052126; border-radius: 10px; "
                "font-size: 22px; font-weight: 700; padding: 8px 12px;"
            ),
        )
        brand_text_shell = _frame(brand_shell, style="background-color: transparent; border: none;")
        brand_text_layout = QVBoxLayout(brand_text_shell)
        brand_text_layout.setContentsMargins(0, 0, 0, 0)
        brand_text_layout.setSpacing(2)
        brand_text_layout.addWidget(_label("视觉编辑器", brand_text_shell, style="font-size: 20px; font-weight: 800; color: #ffffff; background: transparent;"))
        brand_text_layout.addWidget(_label("适用于 TikTok Shop 选品短视频、短视频素材与福利转化视频的快速二创工作台", brand_text_shell, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        brand_layout.addWidget(brand_icon)
        brand_layout.addWidget(brand_text_shell)

        stats_shell = _frame(header, style="background-color: transparent; border: none;")
        stats_layout = QHBoxLayout(stats_shell)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        status_items: tuple[tuple[str, BadgeTone], ...] = (
            ("项目：春季爆品短片", "brand"),
            ("比例：9:16", "info"),
            ("时长：00:42", "neutral"),
            ("状态：草稿已保存", "success"),
        )
        for text, tone in status_items:
            stats_layout.addWidget(StatusBadge(text, tone=tone, parent=stats_shell))

        undo_button = IconButton("↶", "撤销")
        redo_button = IconButton("↷", "重做")
        preview_button = IconButton("▣", "预览窗口设置")
        export_button = PrimaryButton("导出视频", icon_text="⇪")

        action_shell = _frame(header, style="background-color: transparent; border: none;")
        action_layout = QHBoxLayout(action_shell)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        action_layout.addWidget(undo_button)
        action_layout.addWidget(redo_button)
        action_layout.addWidget(preview_button)
        action_layout.addWidget(export_button)

        layout.addWidget(brand_shell)
        layout.addStretch(1)
        layout.addWidget(stats_shell)
        layout.addSpacing(8)
        layout.addWidget(action_shell)
        return header

    def _build_workspace_shell(self) -> QWidget:
        shell = _frame(name="visualEditorWorkspace", style="background-color: transparent; border: none;")
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(16)

        tool_palette = self._build_tool_palette()
        content_split = SplitPanel(orientation="horizontal", split_ratio=(0.23, 0.77), minimum_sizes=(300, 900), parent=shell)
        editor_inspector_split = SplitPanel(orientation="horizontal", split_ratio=(0.73, 0.27), minimum_sizes=(760, 320), parent=shell)
        editor_vertical_split = SplitPanel(orientation="vertical", split_ratio=(0.58, 0.42), minimum_sizes=(380, 320), parent=shell)

        content_split.set_first_widget(self._build_left_library_panel())
        content_split.set_second_widget(editor_inspector_split)

        editor_inspector_split.set_first_widget(editor_vertical_split)
        editor_inspector_split.set_second_widget(self._build_right_inspector())

        editor_vertical_split.set_first_widget(self._build_preview_workspace())
        editor_vertical_split.set_second_widget(self._build_timeline_workspace())

        shell_layout.addWidget(tool_palette)
        shell_layout.addWidget(content_split, 1)
        return shell

    def _build_tool_palette(self) -> QWidget:
        palette = _frame(name="visualEditorTools", style=_panel_style(SURFACE_PANEL, BORDER, 20))
        _set_fixed_width(palette, 98)
        layout = QVBoxLayout(palette)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(10)

        layout.addWidget(_label("工具", palette, style=f"font-size: 12px; color: {TEXT_MUTED}; font-weight: 700; background: transparent;"))
        for tool in TOOL_ITEMS:
            item = _frame(
                palette,
                style=(
                    f"background-color: {ACCENT_SOFT if tool.active else SURFACE_CARD};"
                    f"border: 1px solid {ACCENT_STRONG if tool.active else BORDER};"
                    "border-radius: 16px;"
                ),
            )
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(8, 10, 8, 10)
            item_layout.setSpacing(4)
            icon = _label(
                tool.icon,
                item,
                style=f"font-size: 20px; font-weight: 800; color: {ACCENT if tool.active else TEXT_PRIMARY}; background: transparent;",
            )
            _set_alignment_center(icon)
            title = _label(tool.title, item, style=f"font-size: 11px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent;")
            _set_alignment_center(title)
            shortcut = _label(tool.shortcut, item, style=f"font-size: 10px; color: {TEXT_MUTED}; background: transparent;")
            _set_alignment_center(shortcut)
            item_layout.addWidget(icon)
            item_layout.addWidget(title)
            item_layout.addWidget(shortcut)
            layout.addWidget(item)

        layout.addStretch(1)
        layout.addWidget(
            _label(
                "当前：剪裁",
                palette,
                style=(
                    f"background-color: {SURFACE_CARD}; border: 1px solid {BORDER}; border-radius: 14px; "
                    f"padding: 10px 8px; font-size: 11px; color: {TEXT_SECONDARY}; font-weight: 700;"
                ),
                wrap=True,
            )
        )
        return palette

    def _build_left_library_panel(self) -> QWidget:
        panel = _frame(name="visualEditorLibrary", style=_panel_style(SURFACE_PANEL, BORDER, 20))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        top_row = _frame(panel, style="background-color: transparent; border: none;")
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)
        top_layout.addWidget(_label("媒体仓与素材库", top_row, style="font-size: 16px; font-weight: 800; color: #ffffff; background: transparent;"))
        top_layout.addStretch(1)
        top_layout.addWidget(StatusBadge("已导入 8 项", tone="brand", parent=top_row))
        top_layout.addWidget(IconButton("☰", "切换视图"))
        layout.addWidget(top_row)

        layout.addWidget(
            _label(
                "集中管理主视频、静态素材、字幕模板和滤镜预设；支持拖拽补充素材并快速套用到当前时间轴。",
                panel,
                style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;",
                wrap=True,
            )
        )

        tabs = TabBar(panel)
        tabs.add_tab("媒体仓", self._build_media_bin_tab())
        tabs.add_tab("模板库", self._build_template_library_tab())
        tabs.add_tab("滤镜库", self._build_filter_library_tab())
        layout.addWidget(tabs)
        return panel

    def _build_media_bin_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        search = SearchBar("搜索素材名称、标签或镜头用途")
        category_combo = ThemedComboBox("素材分类", ["全部素材", "主视频", "细节镜头", "图层素材", "字幕模板", "动效素材"])
        sort_combo = ThemedComboBox("排序方式", ["最近导入", "使用频次", "时长优先", "转化标签"])

        combo_row = _frame(tab, style="background-color: transparent; border: none;")
        combo_layout = QHBoxLayout(combo_row)
        combo_layout.setContentsMargins(0, 0, 0, 0)
        combo_layout.setSpacing(10)
        combo_layout.addWidget(category_combo)
        combo_layout.addWidget(sort_combo)

        drop_zone = DragDropZone(parent=tab)
        _set_minimum_height(drop_zone, 180)

        library_hint = _frame(tab, style=_card_style(SURFACE_CARD, BORDER, 16))
        hint_layout = QVBoxLayout(library_hint)
        hint_layout.setContentsMargins(14, 14, 14, 14)
        hint_layout.setSpacing(8)
        hint_layout.addWidget(_label("本次项目建议素材结构", library_hint, style="font-size: 13px; font-weight: 800; color: #ffffff; background: transparent;"))
        for suggestion in (
            "1 个强钩子开场镜头 + 2 个卖点特写 + 1 个场景化转化镜头",
            "字幕模板建议准备主标题、卖点条、福利收口三组",
            "至少保留 1 张封面静帧和 1 个品牌角标透明素材",
        ):
            hint_layout.addWidget(_label(f"• {suggestion}", library_hint, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))

        grid_host = _frame(tab, style=_panel_style(SURFACE_CARD, BORDER, 18))
        grid_layout = QVBoxLayout(grid_host)
        grid_layout.setContentsMargins(12, 12, 12, 12)
        grid_layout.setSpacing(10)
        header_row = _frame(grid_host, style="background-color: transparent; border: none;")
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        header_layout.addWidget(_label("已导入素材", header_row, style="font-size: 14px; font-weight: 800; color: #ffffff; background: transparent;"))
        header_layout.addStretch(1)
        header_layout.addWidget(_label("8 项", header_row, style=f"font-size: 11px; color: {ACCENT}; background: transparent; font-weight: 700;"))
        self._media_grid = ImageGrid(columns=2, parent=grid_host)
        self._populate_media_grid(self._media_grid)
        grid_layout.addWidget(header_row)
        grid_layout.addWidget(self._build_media_asset_summary())
        grid_layout.addWidget(self._media_grid)

        action_row = _frame(tab, style="background-color: transparent; border: none;")
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        add_button = FloatingActionButton("+", "快速新增素材")
        add_note = _label("拖拽至时间轴即可自动创建片段", action_row, style=f"font-size: 12px; color: {TEXT_MUTED}; background: transparent;", wrap=True)
        action_layout.addWidget(add_button)
        action_layout.addWidget(add_note, 1)

        layout.addWidget(search)
        layout.addWidget(combo_row)
        layout.addWidget(drop_zone)
        layout.addWidget(library_hint)
        layout.addWidget(grid_host, 1)
        layout.addWidget(action_row)
        return tab

    def _build_media_asset_summary(self) -> QWidget:
        summary = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(summary)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for asset in MEDIA_ASSETS[:4]:
            row = _frame(summary, style=_card_style(SURFACE_ALT, BORDER, 14))
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 10, 12, 10)
            row_layout.setSpacing(10)
            meta_col = _frame(row, style="background-color: transparent; border: none;")
            meta_layout = QVBoxLayout(meta_col)
            meta_layout.setContentsMargins(0, 0, 0, 0)
            meta_layout.setSpacing(2)
            meta_layout.addWidget(_label(asset.title, meta_col, style="font-size: 12px; font-weight: 700; color: #ffffff; background: transparent;"))
            meta_layout.addWidget(_label(f"{asset.category} · {asset.duration} · {asset.ratio}", meta_col, style=f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;"))
            meta_layout.addWidget(_label(asset.note, meta_col, style=f"font-size: 11px; color: {TEXT_MUTED}; background: transparent;", wrap=True))
            tag = _label(asset.tag, row, style=f"background-color: {ACCENT_SOFT}; color: {ACCENT}; border-radius: 10px; padding: 6px 10px; font-size: 11px; font-weight: 700;")
            status = _label(asset.status, row, style=f"background-color: {SURFACE_BG}; color: {TEXT_SECONDARY}; border-radius: 10px; padding: 6px 10px; font-size: 11px; font-weight: 700;")
            row_layout.addWidget(meta_col, 1)
            row_layout.addWidget(tag)
            row_layout.addWidget(status)
            layout.addWidget(row)
        return summary

    def _populate_media_grid(self, grid: ImageGrid) -> None:
        for asset in MEDIA_ASSETS:
            grid.add_item(asset.file_path, duration=asset.duration if asset.duration != "静帧" else "", status="processing" if asset.status == "处理中" else "ready")

    def _build_template_library_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(_label("推荐模板", tab, style="font-size: 14px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("可直接替换素材并保持原有节奏、字幕安全区和导出规范。", tab, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        for item in TEMPLATE_ITEMS:
            card = _frame(tab, style=_card_style(SURFACE_CARD, BORDER, 16))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 14, 14, 14)
            card_layout.setSpacing(8)
            top_row = _frame(card, style="background-color: transparent; border: none;")
            top_layout = QHBoxLayout(top_row)
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(8)
            top_layout.addWidget(_label(item.title, top_row, style="font-size: 13px; font-weight: 800; color: #ffffff; background: transparent;"))
            top_layout.addStretch(1)
            top_layout.addWidget(_label(item.duration, top_row, style=f"background-color: {SURFACE_ALT}; color: {TEXT_SECONDARY}; border-radius: 10px; padding: 5px 10px; font-size: 11px; font-weight: 700;"))
            card_layout.addWidget(top_row)
            card_layout.addWidget(_label(f"场景：{item.scene} · 强调：{item.emphasis}", card, style=f"font-size: 11px; color: {ACCENT}; background: transparent; font-weight: 700;"))
            card_layout.addWidget(_label(item.detail, card, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
            footer = _frame(card, style="background-color: transparent; border: none;")
            footer_layout = QHBoxLayout(footer)
            footer_layout.setContentsMargins(0, 0, 0, 0)
            footer_layout.setSpacing(8)
            footer_layout.addWidget(IconButton("◎", "预览模板"))
            footer_layout.addWidget(IconButton("⇳", "替换素材"))
            footer_layout.addStretch(1)
            footer_layout.addWidget(PrimaryButton("套用模板"))
            card_layout.addWidget(footer)
            layout.addWidget(card)
        layout.addStretch(1)
        return tab

    def _build_filter_library_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(_label("风格滤镜", tab, style="font-size: 14px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("优先使用适合电商信息展示的清透、高对比和轻电影感风格。", tab, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        for preset in FILTER_PRESETS:
            card = _frame(tab, style=_card_style(ACCENT_SOFT if preset.active else SURFACE_CARD, ACCENT_STRONG if preset.active else BORDER, 16))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 14, 14, 14)
            card_layout.setSpacing(6)
            title_row = _frame(card, style="background-color: transparent; border: none;")
            title_layout = QHBoxLayout(title_row)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(8)
            title_layout.addWidget(_label(preset.name, title_row, style="font-size: 13px; font-weight: 800; color: #ffffff; background: transparent;"))
            title_layout.addStretch(1)
            title_layout.addWidget(_label(preset.intensity, title_row, style=f"background-color: {SURFACE_BG}; color: {ACCENT if preset.active else TEXT_SECONDARY}; border-radius: 10px; padding: 5px 10px; font-size: 11px; font-weight: 700;"))
            card_layout.addWidget(title_row)
            card_layout.addWidget(_label(preset.tone, card, style=f"font-size: 11px; color: {ACCENT}; background: transparent; font-weight: 700;"))
            card_layout.addWidget(_label(preset.style_hint, card, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
            layout.addWidget(card)
        layout.addStretch(1)
        return tab

    def _build_preview_workspace(self) -> QWidget:
        panel = _frame(name="visualEditorPreview", style=_panel_style(SURFACE_PANEL, BORDER, 20))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        layout.addWidget(self._build_preview_header())

        body = _frame(panel, style="background-color: transparent; border: none;")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)
        body_layout.addWidget(self._build_preview_stage(), 4)
        body_layout.addWidget(self._build_storyboard_panel(), 2)

        layout.addWidget(body, 1)
        layout.addWidget(self._build_preview_footer())
        return panel

    def _build_preview_header(self) -> QWidget:
        header = _frame(style="background-color: transparent; border: none;")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        left_col = _frame(header, style="background-color: transparent; border: none;")
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        left_layout.addWidget(_label("视频预览区", left_col, style="font-size: 16px; font-weight: 800; color: #ffffff; background: transparent;"))
        left_layout.addWidget(_label("预览当前画面、字幕安全区、图层叠加效果和导出前构图状态。", left_col, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))

        right_row = _frame(header, style="background-color: transparent; border: none;")
        right_layout = QHBoxLayout(right_row)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.addWidget(StatusBadge("预览 1080p · 30fps", tone="brand", parent=right_row))
        right_layout.addWidget(IconButton("⤢", "全屏预览"))
        right_layout.addWidget(IconButton("⚙", "预览设置"))

        layout.addWidget(left_col, 1)
        layout.addWidget(right_row)
        return header

    def _build_preview_stage(self) -> QWidget:
        stage = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(stage)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        player = VideoPlayerWidget(parent=stage)
        layout.addWidget(player, 1)
        layout.addWidget(self._build_preview_metrics())
        return stage

    def _build_preview_metrics(self) -> QWidget:
        metrics = _frame(style="background-color: transparent; border: none;")
        layout = QHBoxLayout(metrics)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        for title, value, hint in (
            ("当前镜头", "卖点特写 1", "主商品材质细节"),
            ("字幕状态", "第 2 组已激活", "底部安全区自动避让"),
            ("滤镜预设", "清透电商 72%", "亮度 +6 / 对比 +8"),
            ("导出估时", "00:27", "标准发布版"),
        ):
            card = _frame(metrics, style=_card_style(SURFACE_ALT, BORDER, 14))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(2)
            card_layout.addWidget(_label(title, card, style=f"font-size: 11px; color: {TEXT_MUTED}; background: transparent; font-weight: 700;"))
            card_layout.addWidget(_label(value, card, style="font-size: 13px; color: #ffffff; background: transparent; font-weight: 800;"))
            card_layout.addWidget(_label(hint, card, style=f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
            layout.addWidget(card)
        return metrics

    def _build_storyboard_panel(self) -> QWidget:
        panel = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(_label("镜头脚本", panel, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("将当前预览与镜头说明联动，方便运营同学快速检查卖点节奏和信息露出。", panel, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))

        for title, time_text, desc, accent_color in (
            ("开场钩子", "00:00 - 00:04", "第一屏直接出现产品使用前后差异，标题弹入后留白 0.5 秒。", ACCENT),
            ("卖点细节", "00:05 - 00:18", "切入材质细节与防滑纹理，字幕使用高对比黄底条。", AMBER),
            ("安装演示", "00:19 - 00:32", "三步安装过程压缩为快切动作，保持手部动作完整。", CYAN),
            ("优惠收口", "00:33 - 00:42", "字幕上移规避购物组件，配合价格闪光和券后价口播。", ROSE),
        ):
            card = _frame(panel, style=_card_style(SURFACE_ALT, BORDER, 14))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(6)
            top = _frame(card, style="background-color: transparent; border: none;")
            top_layout = QHBoxLayout(top)
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(8)
            top_layout.addWidget(_label(title, top, style="font-size: 13px; font-weight: 800; color: #ffffff; background: transparent;"))
            top_layout.addStretch(1)
            top_layout.addWidget(_label(time_text, top, style=f"background-color: {SURFACE_BG}; color: {accent_color}; border-radius: 10px; padding: 5px 10px; font-size: 11px; font-weight: 700;"))
            card_layout.addWidget(top)
            card_layout.addWidget(_label(desc, card, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
            layout.addWidget(card)

        note = _frame(panel, style=_card_style(ACCENT_SOFT, ACCENT_STRONG, 14))
        note_layout = QVBoxLayout(note)
        note_layout.setContentsMargins(12, 12, 12, 12)
        note_layout.setSpacing(6)
        note_layout.addWidget(_label("AI 提示", note, style=f"font-size: 12px; font-weight: 800; color: {ACCENT}; background: transparent;"))
        note_layout.addWidget(_label("建议将『限时券立减 60』字幕提前 8 帧出现，与价格闪光同时触发，提升福利感知。", note, style=f"font-size: 12px; color: {TEXT_PRIMARY}; background: transparent;", wrap=True))
        layout.addWidget(note)
        layout.addStretch(1)
        return panel

    def _build_preview_footer(self) -> QWidget:
        footer = _frame(style=_card_style(SURFACE_CARD, BORDER, 18))
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        for label_text in ("字幕安全区已启用", "口播转字幕已对齐", "当前导出方案：标准发布版", "时间轴吸附：已开启"):
            layout.addWidget(_label(label_text, footer, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;"))
        layout.addStretch(1)
        layout.addWidget(PrimaryButton("一键导出", icon_text="⇪"))
        return footer

    def _build_timeline_workspace(self) -> QWidget:
        panel = _frame(name="visualEditorTimeline", style=_panel_style(SURFACE_PANEL, BORDER, 20))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        tabs = TabBar(panel)
        tabs.add_tab("多轨时间轴", self._build_multitrack_timeline_tab())
        tabs.add_tab("关键节点", self._build_keyframe_tab())
        tabs.add_tab("调色建议", self._build_color_tab())
        tabs.add_tab("音频节奏", self._build_audio_tab())
        layout.addWidget(_wrap_scroll(tabs))
        return panel

    def _build_multitrack_timeline_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(self._build_timeline_toolbar())
        layout.addWidget(self._build_marker_strip())
        layout.addWidget(self._build_timeline_ruler())
        layout.addWidget(self._build_timeline_tracks_panel(), 1)
        return tab

    def _build_timeline_toolbar(self) -> QWidget:
        toolbar = _frame(style=_card_style(SURFACE_CARD, BORDER, 16))
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        zoom_combo = ThemedComboBox("缩放", ["50%", "75%", "100%", "125%", "150%"])
        snap_combo = ThemedComboBox("吸附", ["关闭", "片段边缘", "片段 + 标记点", "全部元素"])
        speed_combo = ThemedComboBox("预览速度", ["0.5x", "1.0x", "1.25x", "1.5x"])

        layout.addWidget(_label("时间轴编辑", toolbar, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("当前播放头：00:15", toolbar, style=f"font-size: 12px; color: {ACCENT}; background: transparent; font-weight: 700;"))
        layout.addStretch(1)
        layout.addWidget(IconButton("＋", "放大时间轴"))
        layout.addWidget(IconButton("－", "缩小时间轴"))
        layout.addWidget(IconButton("⌦", "删除选中片段"))
        layout.addWidget(zoom_combo)
        layout.addWidget(snap_combo)
        layout.addWidget(speed_combo)
        return toolbar

    def _build_marker_strip(self) -> QWidget:
        strip = _frame(style=_card_style(SURFACE_CARD, BORDER, 16))
        layout = QVBoxLayout(strip)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        layout.addWidget(_label("时间轴标记", strip, style="font-size: 13px; font-weight: 800; color: #ffffff; background: transparent;"))

        line = _frame(strip, style=f"background-color: {SURFACE_ALT}; border: 1px solid {BORDER}; border-radius: 12px;")
        _set_fixed_height(line, 70)
        line_layout = QHBoxLayout(line)
        line_layout.setContentsMargins(12, 10, 12, 10)
        line_layout.setSpacing(12)
        for marker in MARKER_ITEMS:
            item = _frame(line, style=(f"background-color: {SURFACE_BG}; border: 1px solid {marker.color}; border-radius: 12px;"))
            _set_fixed_width(item, 170)
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            item_layout.setSpacing(2)
            item_layout.addWidget(_label(marker.time, item, style=f"font-size: 11px; color: {marker.color}; background: transparent; font-weight: 800;"))
            item_layout.addWidget(_label(marker.title, item, style="font-size: 12px; color: #ffffff; background: transparent; font-weight: 700;"))
            item_layout.addWidget(_label(marker.detail, item, style=f"font-size: 10px; color: {TEXT_MUTED}; background: transparent;", wrap=True))
            line_layout.addWidget(item)
        line_layout.addStretch(1)
        layout.addWidget(line)
        return strip

    def _build_timeline_ruler(self) -> QWidget:
        ruler = _frame(style=_card_style(SURFACE_CARD, BORDER, 16))
        layout = QHBoxLayout(ruler)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(0)
        left_stub = _label("轨道", ruler, style=f"font-size: 12px; color: {TEXT_MUTED}; background: transparent; font-weight: 700;")
        _set_fixed_width(left_stub, 130)
        layout.addWidget(left_stub)

        times = _frame(ruler, style="background-color: transparent; border: none;")
        times_layout = QHBoxLayout(times)
        times_layout.setContentsMargins(0, 0, 0, 0)
        times_layout.setSpacing(0)
        for value in ("00:00", "00:05", "00:10", "00:15", "00:20", "00:25", "00:30", "00:35", "00:40", "00:45"):
            cell = _label(value, times, style=f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent; font-weight: 700;")
            _set_fixed_width(cell, 82)
            layout_cell_wrap = _frame(times, style="background-color: transparent; border: none;")
            cell_layout = QVBoxLayout(layout_cell_wrap)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(0)
            cell_layout.addWidget(cell)
            times_layout.addWidget(layout_cell_wrap)
        layout.addWidget(times, 1)
        return ruler

    def _build_timeline_tracks_panel(self) -> QWidget:
        tracks_panel = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(tracks_panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        for track in TIMELINE_TRACKS:
            layout.addWidget(self._build_track_row(track))
        layout.addWidget(self._build_timeline_overview())
        return tracks_panel

    def _build_track_row(self, track: TimelineTrack) -> QWidget:
        row = _frame(style=_card_style(SURFACE_ALT, BORDER, 16))
        _set_minimum_height(row, 80)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        label_shell = _frame(row, style=(f"background-color: {SURFACE_BG}; border: 1px solid {BORDER}; border-radius: 14px;"))
        _set_fixed_width(label_shell, 130)
        label_layout = QVBoxLayout(label_shell)
        label_layout.setContentsMargins(10, 8, 10, 8)
        label_layout.setSpacing(2)
        label_layout.addWidget(_label(track.icon, label_shell, style=f"font-size: 16px; color: {track.color}; background: transparent; font-weight: 800;"))
        label_layout.addWidget(_label(track.title, label_shell, style="font-size: 12px; color: #ffffff; background: transparent; font-weight: 800;"))
        label_layout.addWidget(_label(track.role, label_shell, style=f"font-size: 10px; color: {TEXT_MUTED}; background: transparent;"))

        clip_row = _frame(row, style=(f"background-color: {SURFACE_BG}; border: 1px solid {BORDER}; border-radius: 14px;"))
        clip_layout = QHBoxLayout(clip_row)
        clip_layout.setContentsMargins(10, 12, 10, 12)
        clip_layout.setSpacing(8)
        for segment in track.segments:
            clip_layout.addSpacing(segment.offset if segment is track.segments[0] else 0)
            clip_layout.addWidget(self._build_track_clip(segment))
        clip_layout.addStretch(1)

        layout.addWidget(label_shell)
        layout.addWidget(clip_row, 1)
        return row

    def _build_track_clip(self, segment: TimelineSegment) -> QWidget:
        clip = _frame(
            style=(
                f"background-color: {segment.fill}; border: 1px solid {segment.color}; border-radius: 12px;"
                f"box-shadow: 0 0 0 1px {ACCENT_STRONG};" if segment.selected else f"background-color: {segment.fill}; border: 1px solid {segment.color}; border-radius: 12px;"
            ),
        )
        _set_fixed_width(clip, segment.width)
        _set_fixed_height(clip, 48)
        layout = QVBoxLayout(clip)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)
        layout.addWidget(_label(segment.title, clip, style=f"font-size: 11px; color: {segment.text_color}; background: transparent; font-weight: 800;"))
        layout.addWidget(_label(segment.subtitle, clip, style=f"font-size: 10px; color: {TEXT_SECONDARY}; background: transparent;"))
        layout.addWidget(_label(f"{segment.start} → {segment.end}", clip, style=f"font-size: 9px; color: {TEXT_MUTED}; background: transparent;"))
        return clip

    def _build_timeline_overview(self) -> QWidget:
        overview = _frame(style=_card_style(SURFACE_ALT, BORDER, 16))
        layout = QHBoxLayout(overview)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        left = _frame(overview, style="background-color: transparent; border: none;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        left_layout.addWidget(_label("时间轴摘要", left, style="font-size: 13px; color: #ffffff; background: transparent; font-weight: 800;"))
        left_layout.addWidget(_label("当前片段总数 11，字幕图层 4，动效图层 2，音乐 1。播放头位于 00:15，已对齐价格节点。", left, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        layout.addWidget(left, 1)
        for chip in ("镜头节奏：稳定", "字幕密度：适中", "转化节点：2 处", "遮挡风险：1 处"):
            layout.addWidget(_label(chip, overview, style=f"background-color: {SURFACE_BG}; color: {TEXT_SECONDARY}; border: 1px solid {BORDER}; border-radius: 10px; padding: 6px 10px; font-size: 11px; font-weight: 700;"))
        return overview

    def _build_keyframe_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(_label("关键节点与操作记录", tab, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("用于回看当前工程的重要编辑动作、AI 建议和风险提醒。", tab, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        self._timeline_widget = TimelineWidget()
        self._timeline_widget.set_events(TIMELINE_EVENTS)
        layout.addWidget(self._timeline_widget)
        return tab

    def _build_color_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(_label("调色建议", tab, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("根据当前镜头混合了白底静物、手部细节和场景化实拍，建议维持统一的冷白电商质感。", tab, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))

        for title, value, detail, accent_color in (
            ("亮度", "+6", "主画面略提亮，强化白底和商品边缘层次。", ACCENT),
            ("对比度", "+8", "保持卖点特写更立体，但避免压暗人物肤色。", CYAN),
            ("高光", "-10", "避免包装反光过曝，提升细节保留。", AMBER),
            ("阴影", "+7", "人物持握画面适当提起阴影区域。", PURPLE),
            ("饱和度", "+5", "控制在信息表达优先的电商风格内。", ROSE),
        ):
            row = _frame(tab, style=_card_style(SURFACE_CARD, BORDER, 16))
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 12, 14, 12)
            row_layout.setSpacing(10)
            row_layout.addWidget(_label(title, row, style="font-size: 13px; color: #ffffff; background: transparent; font-weight: 800;"))
            row_layout.addWidget(_label(value, row, style=f"background-color: {ACCENT_SOFT}; color: {accent_color}; border-radius: 10px; padding: 6px 10px; font-size: 11px; font-weight: 800;"))
            row_layout.addWidget(_label(detail, row, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True), 1)
            layout.addWidget(row)
        layout.addStretch(1)
        return tab

    def _build_audio_tab(self) -> QWidget:
        tab = _frame(style="background-color: transparent; border: none;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(_label("音频节奏与口播提示", tab, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("建议在福利节点使用鼓点击打音效，主音乐整体保持轻电子和稳定律动。", tab, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        for title, meter, detail in (
            ("开场 0-5 秒", "强拍 4 次", "每次镜头切换都应有清晰打点，配合标题弹入。"),
            ("卖点展示 6-18 秒", "中频均衡", "保持口播清晰，背景音乐降低至 68%。"),
            ("安装演示 19-32 秒", "节奏加速", "动作快切段可加入轻微切换音效，增强节奏感。"),
            ("优惠收口 33-42 秒", "高潮抬升", "最后 6 秒提高音乐存在感，同时避免压住券后价口播。"),
        ):
            card = _frame(tab, style=_card_style(SURFACE_CARD, BORDER, 16))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            card_layout.setSpacing(4)
            top_row = _frame(card, style="background-color: transparent; border: none;")
            top_layout = QHBoxLayout(top_row)
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.setSpacing(8)
            top_layout.addWidget(_label(title, top_row, style="font-size: 13px; color: #ffffff; background: transparent; font-weight: 800;"))
            top_layout.addStretch(1)
            top_layout.addWidget(_label(meter, top_row, style=f"background-color: {SURFACE_BG}; color: {INDIGO}; border-radius: 10px; padding: 5px 10px; font-size: 11px; font-weight: 800;"))
            card_layout.addWidget(top_row)
            card_layout.addWidget(_label(detail, card, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
            layout.addWidget(card)
        layout.addStretch(1)
        return tab

    def _build_right_inspector(self) -> QWidget:
        panel = _frame(name="visualEditorInspector", style=_panel_style(SURFACE_PANEL, BORDER, 20))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        layout.addWidget(self._build_layer_panel())
        layout.addWidget(self._build_inspector_switcher())
        layout.addWidget(self._build_inspector_stack(), 1)
        return panel

    def _build_layer_panel(self) -> QWidget:
        panel = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        header = _frame(panel, style="background-color: transparent; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        header_layout.addWidget(_label("图层列表", header, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        header_layout.addStretch(1)
        header_layout.addWidget(IconButton("＋", "新增图层"))
        header_layout.addWidget(IconButton("⇅", "排序图层"))
        layout.addWidget(header)
        for item in LAYER_ITEMS:
            layout.addWidget(self._build_layer_row(item))
        return panel

    def _build_layer_row(self, item: LayerItem) -> QWidget:
        border_color = ACCENT if item.selected else BORDER
        background = ACCENT_SOFT if item.selected else SURFACE_ALT
        row = _frame(style=(f"background-color: {background}; border: 1px solid {border_color}; border-radius: 14px;"))
        layout = QVBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        top = _frame(row, style="background-color: transparent; border: none;")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)
        top_layout.addWidget(_label(item.name, top, style="font-size: 12px; color: #ffffff; background: transparent; font-weight: 800;", wrap=True))
        top_layout.addStretch(1)
        top_layout.addWidget(_label("显" if item.visible else "隐", top, style=f"background-color: {SURFACE_BG}; color: {SUCCESS if item.visible else TEXT_MUTED}; border-radius: 10px; padding: 4px 8px; font-size: 10px; font-weight: 800;"))
        top_layout.addWidget(_label("锁" if item.locked else "可编", top, style=f"background-color: {SURFACE_BG}; color: {WARNING if item.locked else ACCENT}; border-radius: 10px; padding: 4px 8px; font-size: 10px; font-weight: 800;"))
        layout.addWidget(top)
        layout.addWidget(_label(f"{item.kind} · {item.start} → {item.end}", row, style=f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;"))
        layout.addWidget(_label(f"混合模式：{item.blend} · 不透明度：{item.opacity}", row, style=f"font-size: 11px; color: {TEXT_MUTED}; background: transparent;"))
        return row

    def _build_inspector_switcher(self) -> QWidget:
        switcher = _frame(style=_card_style(SURFACE_CARD, BORDER, 16))
        layout = QHBoxLayout(switcher)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        for index, title in enumerate(("属性", "设置", "导出")):
            button = _label(
                title,
                switcher,
                style=(
                    f"background-color: {ACCENT_SOFT if index == 0 else SURFACE_ALT};"
                    f"border: 1px solid {ACCENT_STRONG if index == 0 else BORDER};"
                    f"border-radius: 12px; padding: 8px 12px; color: {ACCENT if index == 0 else TEXT_SECONDARY};"
                    "font-size: 12px; font-weight: 800;"
                ),
            )
            self._inspector_buttons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)
        return switcher

    def _build_inspector_stack(self) -> QWidget:
        self._inspector_stack = QStackedWidget()
        _call(self._inspector_stack, "addWidget", self._build_properties_page())
        _call(self._inspector_stack, "addWidget", self._build_settings_page())
        _call(self._inspector_stack, "addWidget", self._build_export_page())
        _call(self._inspector_stack, "setCurrentIndex", 0)

        stack_shell = _frame(style="background-color: transparent; border: none;")
        shell_layout = QVBoxLayout(stack_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(_wrap_scroll(self._inspector_stack))
        return stack_shell

    def _build_properties_page(self) -> QWidget:
        page = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addWidget(_label("当前选中：卖点特写 1", page, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("用于展示主商品材质细节，建议保持主体居中并强化边缘清晰度。", page, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))

        blend_combo = ThemedComboBox("混合模式", ["正常", "滤色", "叠加", "柔光", "正片叠底"])
        filter_combo = ThemedComboBox("套用滤镜", [preset.name for preset in FILTER_PRESETS])
        canvas_combo = ThemedComboBox("画布对齐", ["居中显示", "顶部安全区", "底部安全区", "智能主体追踪"])
        layout.addWidget(blend_combo)
        layout.addWidget(filter_combo)
        layout.addWidget(canvas_combo)

        for metric in PROPERTY_METRICS:
            layout.addWidget(self._build_slider_row(metric))

        layout.addWidget(self._build_text_overlay_section())
        layout.addWidget(self._build_property_badges())
        layout.addStretch(1)
        return page

    def _build_slider_row(self, metric: PropertyMetric) -> QWidget:
        row = _frame(style=_card_style(SURFACE_ALT, BORDER, 14))
        layout = QVBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        top = _frame(row, style="background-color: transparent; border: none;")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        top_layout.addWidget(_label(metric.label, top, style="font-size: 12px; color: #ffffff; background: transparent; font-weight: 800;"))
        top_layout.addStretch(1)
        top_layout.addWidget(_label(f"{metric.value}{metric.unit}", top, style=f"background-color: {SURFACE_BG}; color: {ACCENT}; border-radius: 10px; padding: 4px 8px; font-size: 11px; font-weight: 800;"))

        bar_shell = _frame(row, style=f"background-color: {SURFACE_BG}; border: 1px solid {BORDER}; border-radius: 999px;")
        _set_fixed_height(bar_shell, 12)
        bar_layout = QHBoxLayout(bar_shell)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)
        fill = _frame(bar_shell, style=f"background-color: {ACCENT}; border-radius: 999px; border: none;")
        _set_fixed_width(fill, max(36, int(metric.value * 1.8)))
        bar_layout.addWidget(fill)
        bar_layout.addStretch(1)

        footer = _frame(row, style="background-color: transparent; border: none;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)
        footer_layout.addWidget(_label("低", footer, style=f"font-size: 10px; color: {TEXT_MUTED}; background: transparent;"))
        footer_layout.addStretch(1)
        footer_layout.addWidget(_label(metric.hint, footer, style=f"font-size: 10px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        footer_layout.addStretch(1)
        footer_layout.addWidget(_label("高", footer, style=f"font-size: 10px; color: {TEXT_MUTED}; background: transparent;"))

        layout.addWidget(top)
        layout.addWidget(bar_shell)
        layout.addWidget(footer)
        return row

    def _build_text_overlay_section(self) -> QWidget:
        section = _frame(style=_card_style(SURFACE_ALT, BORDER, 16))
        layout = QVBoxLayout(section)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(_label("文字叠加建议", section, style="font-size: 13px; color: #ffffff; background: transparent; font-weight: 800;"))
        layout.addWidget(_label("当前段落建议使用『耐磨防滑升级』作为主句，副句控制在 10 字以内以避免遮挡主体。", section, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        for sentence in (
            "主标题：耐磨防滑升级",
            "副标题：一步贴合，安装不费力",
            "福利条：限时券后立省 60 元",
        ):
            layout.addWidget(_label(sentence, section, style=f"background-color: {SURFACE_BG}; color: {TEXT_SECONDARY}; border: 1px solid {BORDER}; border-radius: 10px; padding: 8px 10px; font-size: 11px; font-weight: 700;"))
        return section

    def _build_property_badges(self) -> QWidget:
        section = _frame(style=_card_style(SURFACE_ALT, BORDER, 16))
        layout = QHBoxLayout(section)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        for badge in ("主体检测：已锁定", "肤色保护：已启用", "边缘锐化：中等", "安全区校验：通过"):
            layout.addWidget(_label(badge, section, style=f"background-color: {SURFACE_BG}; color: {TEXT_SECONDARY}; border-radius: 10px; padding: 7px 10px; font-size: 11px; font-weight: 700;"))
        return section

    def _build_settings_page(self) -> QWidget:
        page = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addWidget(_label("项目设置", page, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("统一管理画布规格、对齐策略、字幕安全区和 AI 辅助开关。", page, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        for row in SETTING_ROWS:
            layout.addWidget(self._build_setting_row(row))
        layout.addStretch(1)
        return page

    def _build_setting_row(self, row: SettingRow) -> QWidget:
        card = _frame(style=_card_style(SURFACE_ALT, BORDER, 14))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        top = _frame(card, style="background-color: transparent; border: none;")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        top_layout.addWidget(_label(row.title, top, style="font-size: 12px; color: #ffffff; background: transparent; font-weight: 800;"))
        top_layout.addStretch(1)
        top_layout.addWidget(_label(row.value, top, style=f"background-color: {SURFACE_BG}; color: {row.accent}; border-radius: 10px; padding: 5px 10px; font-size: 11px; font-weight: 800;"))
        layout.addWidget(top)
        layout.addWidget(_label(row.detail, card, style=f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        return card

    def _build_export_page(self) -> QWidget:
        page = _frame(style=_panel_style(SURFACE_CARD, BORDER, 18))
        layout = QVBoxLayout(page)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addWidget(_label("导出设置", page, style="font-size: 15px; font-weight: 800; color: #ffffff; background: transparent;"))
        layout.addWidget(_label("可为当前视频选择适合投放、短视频素材或复剪的导出方案，导出按钮位于顶部与本页底部。", page, style=f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent;", wrap=True))
        for preset in EXPORT_PRESETS:
            layout.addWidget(self._build_export_preset_row(preset))

        summary = _frame(page, style=_card_style(ACCENT_SOFT, ACCENT_STRONG, 16))
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(6)
        summary_layout.addWidget(_label("导出提醒", summary, style=f"font-size: 12px; font-weight: 800; color: {ACCENT}; background: transparent;"))
        summary_layout.addWidget(_label("检测到福利字幕距底部组件安全线较近，建议导出前上移 24px 后再执行批量发布。", summary, style=f"font-size: 12px; color: {TEXT_PRIMARY}; background: transparent;", wrap=True))
        layout.addWidget(summary)
        layout.addWidget(PrimaryButton("导出当前视频", icon_text="⇪"))
        layout.addStretch(1)
        return page

    def _build_export_preset_row(self, preset: ExportPreset) -> QWidget:
        card = _frame(style=_card_style(ACCENT_SOFT if preset.active else SURFACE_ALT, ACCENT_STRONG if preset.active else BORDER, 14))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        top = _frame(card, style="background-color: transparent; border: none;")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        top_layout.addWidget(_label(preset.title, top, style="font-size: 12px; color: #ffffff; background: transparent; font-weight: 800;"))
        top_layout.addStretch(1)
        top_layout.addWidget(_label(preset.target, top, style=f"background-color: {SURFACE_BG}; color: {ACCENT if preset.active else TEXT_SECONDARY}; border-radius: 10px; padding: 5px 10px; font-size: 10px; font-weight: 800;"))
        layout.addWidget(top)
        layout.addWidget(_label(f"{preset.format_text} · 码率 {preset.bitrate}", card, style=f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent;"))
        layout.addWidget(_label(preset.detail, card, style=f"font-size: 11px; color: {TEXT_MUTED}; background: transparent;", wrap=True))
        return card


__all__ = ["VisualEditorPage"]

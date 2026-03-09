# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""脚本提取工具页面。"""

from dataclasses import dataclass
from html import escape
from typing import Literal, Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    ContentSection,
    DragDropZone,
    FilterDropdown,
    IconButton,
    ImageGrid,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatsBadge,
    StatusBadge,
    StreamingOutputWidget,
    TabBar,
    TagChip,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ThemedTextEdit,
    VideoPlayerWidget,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

ACCENT = "#00F2EA"
ACCENT_SOFT = "rgba(0, 242, 234, 0.10)"
ACCENT_STRONG = "rgba(0, 242, 234, 0.18)"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F8FAFC"
SURFACE_SOFT = "#F1F5F9"
BORDER = "#E2E8F0"
TEXT_PRIMARY = "#0F172A"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#64748B"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"
INFO = "#3B82F6"
PURPLE = "#8B5CF6"
ORANGE = "#F97316"


@dataclass(frozen=True)
class ExtractionMetric:
    """提取过程中的概览指标。"""

    title: str
    value: str
    caption: str
    trend: Literal["up", "down", "flat"]
    percentage: str
    sparkline: tuple[float | int, ...]


@dataclass(frozen=True)
class TimelinePhase:
    """视频解析阶段。"""

    name: str
    status: str
    note: str
    tone: str


@dataclass(frozen=True)
class ScriptSegment:
    """脚本片段。"""

    timestamp: str
    speaker: str
    segment_type: str
    confidence: int
    summary: str
    visual_hint: str
    script_text: str
    strategy_tag: str
    tone: str


@dataclass(frozen=True)
class KeyframeItem:
    """关键帧卡片数据。"""

    timestamp: str
    title: str
    description: str
    scene_tag: str
    focus: str
    emotion: str
    path: str


@dataclass(frozen=True)
class VisualInsight:
    """视觉/脚本分析洞察。"""

    title: str
    detail: str
    highlight: str
    icon: str
    tone: str


@dataclass(frozen=True)
class ExportPreset:
    """导出格式。"""

    name: str
    note: str
    tone: str


@dataclass(frozen=True)
class HistoryItem:
    """历史任务。"""

    created_at: str
    title: str
    source: str
    duration: str
    status: str
    output: str
    tone: str


OVERVIEW_METRICS: tuple[ExtractionMetric, ...] = (
    ExtractionMetric(
        title="脚本完整度",
        value="94%",
        caption="旁白、镜头说明与字幕已对齐",
        trend="up",
        percentage="+6.2%",
        sparkline=(61, 66, 72, 80, 86, 90, 94),
    ),
    ExtractionMetric(
        title="关键钩子识别",
        value="7 个",
        caption="前三秒钩子 + 转场卖点 + 收口 CTA",
        trend="up",
        percentage="+2 个",
        sparkline=(1, 2, 3, 4, 5, 6, 7),
    ),
    ExtractionMetric(
        title="口播清晰度",
        value="91%",
        caption="自动去噪后识别准确率提升",
        trend="flat",
        percentage="稳定",
        sparkline=(89, 90, 91, 91, 92, 91, 91),
    ),
    ExtractionMetric(
        title="预计导出耗时",
        value="18 秒",
        caption="含 JSON、逐字稿与镜头拆解",
        trend="down",
        percentage="-12%",
        sparkline=(32, 30, 28, 25, 23, 20, 18),
    ),
)

PIPELINE_PHASES: tuple[TimelinePhase, ...] = (
    TimelinePhase("视频接入", "已完成", "已读取 B 站链接并同步封面、时长与分辨率。", "success"),
    TimelinePhase("音轨分离", "已完成", "背景音乐与人声分离完成，环境噪音已压制。", "success"),
    TimelinePhase("语音转写", "处理中", "当前正在修正口语化停顿，补全连续语义。", "warning"),
    TimelinePhase("关键帧抽取", "处理中", "按剧情节点抽取 12 张高信息量画面。", "brand"),
    TimelinePhase("脚本重构", "待执行", "将口播、字幕和镜头意图融合为脚本段落。", "info"),
    TimelinePhase("导出归档", "待执行", "生成提词版、复盘版与时间轴 JSON。", "neutral"),
)

SCRIPT_SEGMENTS: tuple[ScriptSegment, ...] = (
    ScriptSegment(
        timestamp="00:00:01",
        speaker="达人",
        segment_type="开场钩子",
        confidence=97,
        summary="先抛痛点，直接点明上班族加班后没时间做饭。",
        visual_hint="镜头从厨房台面快速推近，空气炸锅与半成品食材同时入镜。",
        script_text="你是不是每天下班都很累，但又不想吃外卖？今天这个三步空气炸锅晚餐，真的能救命。",
        strategy_tag="前三秒痛点钩子",
        tone="brand",
    ),
    ScriptSegment(
        timestamp="00:00:06",
        speaker="达人",
        segment_type="场景铺垫",
        confidence=95,
        summary="建立典型使用人群，突出通勤党和租房党。",
        visual_hint="桌面摆放一人份食材包，字幕强调“15 分钟搞定”。",
        script_text="尤其是租房党、带饭党，冰箱里囤一点半成品，回家十五分钟就能吃上热的。",
        strategy_tag="人群代入",
        tone="info",
    ),
    ScriptSegment(
        timestamp="00:00:12",
        speaker="达人",
        segment_type="步骤一",
        confidence=93,
        summary="说明第一步准备动作，节奏偏快。",
        visual_hint="俯拍镜头展示鸡翅、土豆和调料倒入大碗。",
        script_text="第一步，把鸡翅和土豆直接拌上现成调料，不需要额外腌很久，三十秒搞定。",
        strategy_tag="低门槛操作",
        tone="success",
    ),
    ScriptSegment(
        timestamp="00:00:18",
        speaker="达人",
        segment_type="步骤二",
        confidence=96,
        summary="引出设备参数，强调复制性。",
        visual_hint="近景给到空气炸锅面板，手指按下 180 度 / 12 分钟。",
        script_text="第二步，空气炸锅一百八十度十二分钟，中途翻一次面，新手照着这个温度做基本不会翻车。",
        strategy_tag="参数明确",
        tone="success",
    ),
    ScriptSegment(
        timestamp="00:00:27",
        speaker="达人",
        segment_type="卖点强化",
        confidence=92,
        summary="强化成品效果，突出外酥里嫩与出片。",
        visual_hint="食物出锅时有特写拉丝和表皮焦脆声效。",
        script_text="出来的状态就是外面酥、里面嫩，而且表面这个颜色，拍视频真的特别出片。",
        strategy_tag="结果预告",
        tone="warning",
    ),
    ScriptSegment(
        timestamp="00:00:34",
        speaker="达人",
        segment_type="步骤三",
        confidence=94,
        summary="补充懒人搭配方案，降低决策成本。",
        visual_hint="切到餐桌摆盘，旁边搭配即食沙拉和饮品。",
        script_text="如果你懒得再配菜，就直接搭一盒沙拉或者玉米杯，这一顿真的比点外卖省太多。",
        strategy_tag="组合方案",
        tone="info",
    ),
    ScriptSegment(
        timestamp="00:00:43",
        speaker="达人",
        segment_type="预算说明",
        confidence=90,
        summary="用价格锚点制造购买动力。",
        visual_hint="画面叠加“单餐不到 12 元”的动效字幕。",
        script_text="整套算下来一顿不到十二块，重点是你不用洗很多锅，也不用等骑手。",
        strategy_tag="价格锚点",
        tone="brand",
    ),
    ScriptSegment(
        timestamp="00:00:51",
        speaker="达人",
        segment_type="情绪收口",
        confidence=93,
        summary="用情绪价值拉高分享意愿。",
        visual_hint="达人端起成品微笑试吃，镜头切半身中景。",
        script_text="那种回到家还能好好吃顿热饭的幸福感，真的会让你觉得今天没白忙。",
        strategy_tag="情绪价值",
        tone="purple",
    ),
    ScriptSegment(
        timestamp="00:00:58",
        speaker="达人",
        segment_type="行动引导",
        confidence=98,
        summary="CTA 清晰，适合短视频素材与短视频挂车。",
        visual_hint="屏幕右下角出现商品卡，达人指向购物车位置。",
        script_text="想要我这套空气炸锅食材清单和调味比例，评论区打“晚餐”，我把完整版发你。",
        strategy_tag="评论区触发",
        tone="orange",
    ),
)

KEYFRAME_ITEMS: tuple[KeyframeItem, ...] = (
    KeyframeItem("00:00:01", "痛点开场", "达人手持空气炸锅半成品食材包，镜头快速推进，注意力集中。", "开场", "痛点表达", "急迫", "demo/frame_01.jpg"),
    KeyframeItem("00:00:05", "人群定向", "字幕出现“租房党 / 通勤党”，画面切到冰箱备餐盒。", "人群", "精准代入", "真实", "demo/frame_02.jpg"),
    KeyframeItem("00:00:12", "备料展示", "俯拍鸡翅、土豆、调味粉倒入容器，步骤清晰。", "步骤", "动作拆解", "清爽", "demo/frame_03.jpg"),
    KeyframeItem("00:00:18", "参数说明", "空气炸锅操作面板特写，温度与时间一目了然。", "参数", "复制门槛低", "专业", "demo/frame_04.jpg"),
    KeyframeItem("00:00:24", "等待转场", "倒计时动画与厨房环境镜头结合，节奏紧凑。", "转场", "节奏推进", "轻快", "demo/frame_05.jpg"),
    KeyframeItem("00:00:27", "成品特写", "高饱和食物特写，表皮酥脆感明显。", "卖点", "食欲刺激", "诱人", "demo/frame_06.jpg"),
    KeyframeItem("00:00:34", "组合搭配", "餐桌摆盘出现沙拉、玉米杯和饮品，强化一餐完成感。", "组合", "省心方案", "温暖", "demo/frame_07.jpg"),
    KeyframeItem("00:00:43", "价格锚点", "大字字幕显示“单餐不到 12 元”，带弹出动效。", "价格", "低成本", "理性", "demo/frame_08.jpg"),
    KeyframeItem("00:00:51", "情绪收口", "达人试吃后微笑点头，镜头停留 1.2 秒。", "情绪", "治愈感", "放松", "demo/frame_09.jpg"),
    KeyframeItem("00:00:58", "行动转化", "购物车提示与评论引导同时出现，收口直接。", "转化", "CTA 清晰", "有力", "demo/frame_10.jpg"),
    KeyframeItem("00:01:02", "补充字幕", "结尾出现“收藏这条，明天回家照着做”的记忆点字幕。", "留存", "收藏引导", "稳定", "demo/frame_11.jpg"),
    KeyframeItem("00:01:06", "封面定格", "画面最终停在成品俯拍，可直接作为封面备选。", "封面", "高点击画面", "满足", "demo/frame_12.jpg"),
)

VISUAL_INSIGHTS: tuple[VisualInsight, ...] = (
    VisualInsight("前三秒留存优势", "首屏使用“下班很累又不想点外卖”的痛点句式，天然适合高频生活场景。", "建议保留当前开场，不要前置自我介绍。", "◎", "brand"),
    VisualInsight("镜头节奏均衡", "全片 11 次镜头切换，平均 5.8 秒一跳，信息密度高但不眩晕。", "适合投放信息流，不建议再加快剪辑。", "◫", "info"),
    VisualInsight("卖点落点明确", "最强转化节点出现在 00:00:27 成品特写，与“特别出片”口播形成双重强化。", "建议该节点增加商品卡停留时长。", "✦", "success"),
    VisualInsight("评论触发机制有效", "结尾 CTA 采用“打关键词领清单”，比直接说私信更容易形成互动。", "适合挂车视频与短视频素材复用。", "☏", "warning"),
)

EXPORT_PRESETS: tuple[ExportPreset, ...] = (
    ExportPreset("逐字稿 JSON", "保留时间戳、说话人、置信度，便于接入自动化工作流。", "brand"),
    ExportPreset("提词器脚本", "合并重复停顿，生成适合复录的顺滑口播稿。", "success"),
    ExportPreset("分镜复盘表", "输出镜头作用、画面元素、卖点密度与 CTA 节点。", "info"),
    ExportPreset("字幕 SRT", "适合投喂剪映或 Premiere 进行二次编辑。", "warning"),
)

HISTORY_ITEMS: tuple[HistoryItem, ...] = (
    HistoryItem("03-08 21:14", "厨房懒人早餐切片", "本地文件 / 1080P", "00:54", "已导出", "逐字稿 + SRT", "success"),
    HistoryItem("03-08 16:32", "防晒喷雾测评口播", "TikTok 链接", "01:12", "复盘中", "JSON + 分镜表", "brand"),
    HistoryItem("03-07 23:09", "母婴辅食收纳教程", "Bilibili 链接", "00:47", "已完成", "提词器脚本", "info"),
    HistoryItem("03-07 14:45", "春季穿搭转场合集", "本地文件 / 4K", "00:38", "等待下载", "关键帧包", "warning"),
)


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """安全连接信号。"""

    method = getattr(signal_object, "connect", None)
    if callable(method):
        method(callback)


def _clear_layout(layout: object) -> None:
    """尽量清空布局中的所有子项。"""

    count_method = getattr(layout, "count", None)
    take_at = getattr(layout, "takeAt", None)
    if callable(count_method) and callable(take_at):
        while True:
            count = count_method()
            if not isinstance(count, int) or count <= 0:
                break
            item = take_at(0)
            widget = item.widget() if item is not None and hasattr(item, "widget") else None
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")
        return
    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


def _tone_badge(tone: str) -> BadgeTone:
    """将自定义 tone 映射到组件支持的 badge tone。"""

    if tone == "brand":
        return "brand"
    if tone == "success":
        return "success"
    if tone == "warning":
        return "warning"
    if tone == "error":
        return "error"
    if tone == "info":
        return "info"
    if tone == "orange":
        return "warning"
    if tone == "purple":
        return "info"
    return "neutral"


def _frame_style(*, accent: bool = False, dashed: bool = False) -> str:
    border_color = ACCENT if accent else BORDER
    border_style = "2px dashed" if dashed else "1px solid"
    background = ACCENT_SOFT if accent else SURFACE
    return f"""
        background-color: {background};
        border: {border_style} {border_color};
        border-radius: 16px;
    """


def _inner_card_style() -> str:
    return f"""
        background-color: {SURFACE_ALT};
        border: 1px solid {BORDER};
        border-radius: 14px;
    """


def _headline_style() -> str:
    return f"color: {TEXT_PRIMARY}; font-size: 24px; font-weight: 700;"


def _card_title_style() -> str:
    return f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 700;"


def _muted_label_style() -> str:
    return f"color: {TEXT_MUTED}; font-size: 12px; line-height: 1.6;"


def _body_label_style() -> str:
    return f"color: {TEXT_SECONDARY}; font-size: 13px; line-height: 1.6;"


def _metric_value_style(color: str = TEXT_PRIMARY) -> str:
    return f"color: {color}; font-size: 22px; font-weight: 700;"


def _capsule_style(background: str, foreground: str, border: str) -> str:
    return (
        f"color: {foreground}; background-color: {background}; border: 1px solid {border}; "
        "border-radius: 999px; padding: 4px 12px; font-size: 12px; font-weight: 600;"
    )


def _tone_colors(tone: str) -> tuple[str, str, str]:
    if tone == "success":
        return (SUCCESS, "rgba(34,197,94,0.12)", "rgba(34,197,94,0.24)")
    if tone == "warning":
        return (WARNING, "rgba(245,158,11,0.12)", "rgba(245,158,11,0.24)")
    if tone == "error":
        return (ERROR, "rgba(239,68,68,0.12)", "rgba(239,68,68,0.24)")
    if tone == "info":
        return (INFO, "rgba(59,130,246,0.12)", "rgba(59,130,246,0.24)")
    if tone == "purple":
        return (PURPLE, "rgba(139,92,246,0.12)", "rgba(139,92,246,0.24)")
    if tone == "orange":
        return (ORANGE, "rgba(249,115,22,0.12)", "rgba(249,115,22,0.24)")
    if tone == "brand":
        return (ACCENT, "rgba(0,242,234,0.10)", "rgba(0,242,234,0.24)")
    return (TEXT_MUTED, SURFACE_SOFT, BORDER)


def _progress_bar_style(percent: int, tone: str = "brand") -> str:
    foreground, _, _ = _tone_colors(tone)
    width = max(0, min(100, percent))
    return f"""
        background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 {foreground},
            stop: {width / 100:.4f} {foreground},
            stop: {width / 100:.4f} {SURFACE_SOFT},
            stop: 1 {SURFACE_SOFT}
        );
        border: 1px solid {BORDER};
        border-radius: 999px;
        min-height: 8px;
        max-height: 8px;
    """


def _script_html(segments: Sequence[ScriptSegment]) -> str:
    blocks: list[str] = []
    for segment in segments:
        foreground, background, border = _tone_colors(segment.tone)
        blocks.append(
            """
            <div style="margin-bottom: 16px; padding: 14px; border-radius: 12px; border: 1px solid {border}; background: {background};">
              <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
                <span style="color:{foreground}; font-weight:700;">[{timestamp}] {segment_type}</span>
                <span style="color:#475569; font-size:12px;">{speaker} · 置信度 {confidence}%</span>
              </div>
              <div style="color:#0F172A; font-size:14px; line-height:1.7; margin-bottom:8px;">{script_text}</div>
              <div style="color:#64748B; font-size:12px; line-height:1.6;">镜头提示：{visual_hint}</div>
            </div>
            """.format(
                border=border,
                background=background,
                foreground=foreground,
                timestamp=escape(segment.timestamp),
                segment_type=escape(segment.segment_type),
                speaker=escape(segment.speaker),
                confidence=segment.confidence,
                script_text=escape(segment.script_text),
                visual_hint=escape(segment.visual_hint),
            )
        )
    return "".join(blocks)


def _history_matches(item: HistoryItem, keyword: str, status: str) -> bool:
    normalized = keyword.strip().lower()
    if normalized:
        haystack = f"{item.title} {item.source} {item.output}".lower()
        if normalized not in haystack:
            return False
    if status and status != "全部" and item.status != status:
        return False
    return True


class ScriptExtractorPage(BasePage):
    """脚本提取工具页面实现。"""

    default_route_id = RouteId("script_extractor")
    default_display_name = "脚本提取工具"
    default_icon_name = "movie_edit"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._url_input: ThemedLineEdit | None = None
        self._analysis_mode_combo: ThemedComboBox | None = None
        self._frame_interval_combo: ThemedComboBox | None = None
        self._scene_focus_combo: ThemedComboBox | None = None
        self._note_editor: ThemedTextEdit | None = None
        self._drop_zone: DragDropZone | None = None
        self._video_player: VideoPlayerWidget | None = None
        self._ai_config_panel: AIConfigPanel | None = None
        self._streaming_output: StreamingOutputWidget | None = None
        self._phase_host: QWidget | None = None
        self._phase_layout: QVBoxLayout | None = None
        self._segment_host: QWidget | None = None
        self._segment_layout: QVBoxLayout | None = None
        self._analysis_host: QWidget | None = None
        self._analysis_layout: QVBoxLayout | None = None
        self._history_host: QWidget | None = None
        self._history_layout: QVBoxLayout | None = None
        self._history_search: SearchBar | None = None
        self._history_filter: FilterDropdown | None = None
        self._history_keyword = ""
        self._history_status = "全部"
        self._keyframe_grid: ImageGrid | None = None
        self._ai_summary_label: QLabel | None = None
        self._ai_config_summary_label: QLabel | None = None
        self._selected_export_label: QLabel | None = None
        self._segment_count_label: QLabel | None = None
        self._history_count_label: QLabel | None = None
        self._task_status_badge: StatusBadge | None = None
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建脚本提取工具页面。"""

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        header_actions = [
            SecondaryButton("导出脚本包", self, icon_text="⇩"),
            PrimaryButton("开始提取", self, icon_text="✦"),
            IconButton("⋯", "更多操作", self),
        ]
        page = PageContainer(
            title="脚本提取工具",
            description="面向 TikTok Shop 运营的脚本解析工作台，支持视频地址接入、关键帧抽取、逐段脚本重构与 AI 智能改写。",
            actions=header_actions,
        )

        scroll = ThemedScrollArea(page)
        scroll.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.content_layout.setSpacing(20)

        scroll.add_widget(self._build_intake_section())
        scroll.add_widget(self._build_overview_section())
        scroll.add_widget(self._build_workspace_section())
        scroll.add_widget(self._build_ai_config_section())
        scroll.add_widget(self._build_history_section())
        scroll.add_widget(self._build_capability_section())
        scroll.add_widget(self._build_footer_section())

        page.add_widget(scroll)
        self.layout.addWidget(page)

        self._seed_demo_values()
        self._bind_events()
        self._render_pipeline_phases()
        self._render_script_segments()
        self._render_visual_insights()
        self._render_history_items()
        self._render_streaming_output()
        self._update_ai_config_summary()

    def _build_intake_section(self) -> QWidget:
        section = ContentSection("提取任务", icon="▶", parent=self)

        shell = QFrame(section)
        shell.setStyleSheet(_frame_style(accent=True))
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(16)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(12)

        left_column = QVBoxLayout()
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setSpacing(12)

        self._url_input = ThemedLineEdit(
            label="视频源地址（链接 / 本地任务名）",
            placeholder="粘贴视频链接（Bilibili、TikTok、YouTube）或填写素材任务名",
            helper_text="当前示例：Bilibili 视频链接，系统已自动抓取时长、分辨率和封面信息。",
        )
        left_column.addWidget(self._url_input)

        config_row = QHBoxLayout()
        config_row.setContentsMargins(0, 0, 0, 0)
        config_row.setSpacing(12)

        self._analysis_mode_combo = ThemedComboBox(
            label="分析模式",
            items=["混合模式（ASR + 视觉）", "仅语音转写", "仅视觉识别", "短视频复盘模式"],
        )
        self._frame_interval_combo = ThemedComboBox(
            label="关键帧间隔",
            items=["自动抽帧", "1 秒 / 帧", "3 秒 / 帧", "5 秒 / 帧"],
        )
        self._scene_focus_combo = ThemedComboBox(
            label="内容重点",
            items=["脚本拆解", "卖点提炼", "分镜复盘", "短视频话术"],
        )
        config_row.addWidget(self._analysis_mode_combo)
        config_row.addWidget(self._frame_interval_combo)
        config_row.addWidget(self._scene_focus_combo)
        left_column.addLayout(config_row)

        self._note_editor = ThemedTextEdit(
            label="任务备注",
            placeholder="例如：保留时间戳、输出提词版脚本，并标记高转化镜头。",
        )
        left_column.addWidget(self._note_editor)

        quick_row = QHBoxLayout()
        quick_row.setContentsMargins(0, 0, 0, 0)
        quick_row.setSpacing(10)
        quick_row.addWidget(TagChip("推荐：食品类短视频", tone="brand", parent=shell))
        quick_row.addWidget(TagChip("预计 30 秒完成", tone="success", parent=shell))
        quick_row.addWidget(TagChip("支持逐字稿导出", tone="info", parent=shell))
        quick_row.addStretch(1)
        left_column.addLayout(quick_row)

        top_row.addLayout(left_column, 2)

        right_panel = QFrame(shell)
        right_panel.setStyleSheet(_inner_card_style())
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        right_title = QLabel("本地上传 / 拖拽导入", right_panel)
        right_title.setStyleSheet(_card_title_style())
        right_layout.addWidget(right_title)

        self._drop_zone = DragDropZone(parent=right_panel)
        right_layout.addWidget(self._drop_zone)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        button_row.addWidget(SecondaryButton("选择本地文件", right_panel, icon_text="⇪"))
        button_row.addWidget(PrimaryButton("创建提取任务", right_panel, icon_text="⚡"))
        right_layout.addLayout(button_row)

        helper = QLabel("支持 MP4 / MOV / MKV。本示例页展示拖拽上传后的预解析状态。", right_panel)
        helper.setStyleSheet(_muted_label_style())
        _call(helper, "setWordWrap", True)
        right_layout.addWidget(helper)

        top_row.addWidget(right_panel, 1)
        shell_layout.addLayout(top_row)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 0, 0, 0)
        footer_row.setSpacing(10)

        self._task_status_badge = StatusBadge("任务准备完成", tone="success", parent=shell)
        footer_row.addWidget(self._task_status_badge)
        footer_row.addWidget(StatusBadge("已识别时长 01:08", tone="info", parent=shell))
        footer_row.addWidget(StatusBadge("分辨率 1080P / 24fps", tone="brand", parent=shell))
        footer_row.addStretch(1)
        footer_row.addWidget(SecondaryButton("复制任务配置", shell, icon_text="⧉"))
        shell_layout.addLayout(footer_row)

        section.content_layout.addWidget(shell)
        return section

    def _build_overview_section(self) -> QWidget:
        section = ContentSection("提取概览", icon="◫", parent=self)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(10)
        badge_row.addWidget(StatusBadge("模型已连接", tone="success", parent=section))
        badge_row.addWidget(StatusBadge("正在处理第 124 / 300 帧", tone="warning", parent=section))
        badge_row.addWidget(StatusBadge("摘要已同步", tone="brand", parent=section))
        badge_row.addStretch(1)
        section.content_layout.addLayout(badge_row)

        kpi_row = QHBoxLayout()
        kpi_row.setContentsMargins(0, 0, 0, 0)
        kpi_row.setSpacing(12)
        for metric in OVERVIEW_METRICS:
            kpi_row.addWidget(
                KPICard(
                    title=metric.title,
                    value=metric.value,
                    trend=metric.trend,
                    percentage=metric.percentage,
                    caption=metric.caption,
                    sparkline_data=metric.sparkline,
                )
            )
        section.content_layout.addLayout(kpi_row)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(12)

        insight = InfoCard(
            title="AI 实时摘要",
            description="当前视频主要围绕“空气炸锅晚餐解决下班做饭难题”展开。最佳信息点集中在 00:00:27 成品特写和 00:00:58 评论区引导，适合拆成“省时晚餐教程 + 商品清单领取”双目标脚本。",
            icon="✦",
            action_text="查看摘要策略",
        )
        bottom_row.addWidget(insight, 2)

        metric_stack = QWidget(section)
        metric_layout = QVBoxLayout(metric_stack)
        metric_layout.setContentsMargins(0, 0, 0, 0)
        metric_layout.setSpacing(10)
        metric_layout.addWidget(StatsBadge("剩余时间", "02:45", "◔", "warning", metric_stack))
        metric_layout.addWidget(StatsBadge("已提取片段", "9 段", "◎", "success", metric_stack))
        metric_layout.addWidget(StatsBadge("关键帧数量", "12 张", "▣", "info", metric_stack))
        bottom_row.addWidget(metric_stack, 1)

        section.content_layout.addLayout(bottom_row)
        return section

    def _build_workspace_section(self) -> QWidget:
        section = ContentSection("提取工作台", icon="⚙", parent=self)

        split = SplitPanel("horizontal", split_ratio=(0.34, 0.66), minimum_sizes=(360, 640), parent=section)
        split.set_widgets(self._build_preview_panel(), self._build_results_panel())
        section.content_layout.addWidget(split)
        return section

    def _build_preview_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        preview_card = QFrame(panel)
        preview_card.setStyleSheet(_frame_style())
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(4)
        title = QLabel("视频预览", preview_card)
        title.setStyleSheet(_card_title_style())
        subtitle = QLabel("当前接入视频：下班 15 分钟空气炸锅晚餐", preview_card)
        subtitle.setStyleSheet(_muted_label_style())
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch(1)
        header.addWidget(TagChip("1080P / 24fps", tone="neutral", parent=preview_card))
        preview_layout.addLayout(header)

        self._video_player = VideoPlayerWidget(parent=preview_card)
        preview_layout.addWidget(self._video_player)

        progress_card = QFrame(preview_card)
        progress_card.setStyleSheet(_inner_card_style())
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(14, 14, 14, 14)
        progress_layout.setSpacing(10)

        progress_top = QHBoxLayout()
        progress_top.setContentsMargins(0, 0, 0, 0)
        progress_top.setSpacing(8)
        label = QLabel("视频分析进度", progress_card)
        label.setStyleSheet(_card_title_style())
        percent = QLabel("45%", progress_card)
        percent.setStyleSheet(_metric_value_style(ACCENT))
        progress_top.addWidget(label)
        progress_top.addStretch(1)
        progress_top.addWidget(percent)
        progress_layout.addLayout(progress_top)

        progress_line = QFrame(progress_card)
        progress_line.setStyleSheet(_progress_bar_style(45, "brand"))
        _call(progress_line, "setMinimumHeight", 8)
        progress_layout.addWidget(progress_line)

        info_grid = QHBoxLayout()
        info_grid.setContentsMargins(0, 0, 0, 0)
        info_grid.setSpacing(10)
        info_grid.addWidget(self._build_small_metric_card("已用时长", "01:12", "已完成音轨分离与粗转写", "info", progress_card))
        info_grid.addWidget(self._build_small_metric_card("预计剩余", "02:45", "将继续进行镜头识别与脚本重构", "warning", progress_card))
        progress_layout.addLayout(info_grid)

        preview_layout.addWidget(progress_card)
        root.addWidget(preview_card)

        phase_section = QFrame(panel)
        phase_section.setStyleSheet(_frame_style())
        phase_layout = QVBoxLayout(phase_section)
        phase_layout.setContentsMargins(16, 16, 16, 16)
        phase_layout.setSpacing(12)

        phase_title = QLabel("分析阶段", phase_section)
        phase_title.setStyleSheet(_card_title_style())
        phase_layout.addWidget(phase_title)

        self._phase_host = QWidget(phase_section)
        self._phase_layout = QVBoxLayout(self._phase_host)
        phase_layout_widget = self._phase_layout
        if phase_layout_widget is not None:
            phase_layout_widget.setContentsMargins(0, 0, 0, 0)
            phase_layout_widget.setSpacing(10)
        phase_layout.addWidget(self._phase_host)

        root.addWidget(phase_section)

        summary_card = QFrame(panel)
        summary_card.setStyleSheet(_frame_style())
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(10)

        summary_title = QLabel("AI 即时判断", summary_card)
        summary_title.setStyleSheet(_card_title_style())
        self._ai_summary_label = QLabel(
            "该视频属于“高频生活场景 + 低门槛教程”结构，最适合提取为：开场痛点、三步教程、价格锚点、评论区互动四段式短视频脚本。",
            summary_card,
        )
        ai_summary_label = self._ai_summary_label
        if ai_summary_label is not None:
            ai_summary_label.setStyleSheet(_body_label_style())
            _call(ai_summary_label, "setWordWrap", True)
        summary_layout.addWidget(summary_title)
        if ai_summary_label is not None:
            summary_layout.addWidget(ai_summary_label)

        tag_row = QHBoxLayout()
        tag_row.setContentsMargins(0, 0, 0, 0)
        tag_row.setSpacing(8)
        tag_row.addWidget(TagChip("高留存开场", tone="brand", parent=summary_card))
        tag_row.addWidget(TagChip("教程型成交", tone="success", parent=summary_card))
        tag_row.addWidget(TagChip("评论触发强", tone="warning", parent=summary_card))
        tag_row.addStretch(1)
        summary_layout.addLayout(tag_row)

        root.addWidget(summary_card)
        root.addStretch(1)
        return panel

    def _build_results_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        tabs_shell = QFrame(panel)
        tabs_shell.setStyleSheet(_frame_style())
        tabs_layout = QVBoxLayout(tabs_shell)
        tabs_layout.setContentsMargins(16, 16, 16, 16)
        tabs_layout.setSpacing(12)

        tab_bar = TabBar(tabs_shell)
        tab_bar.add_tab("脚本文案", self._build_script_tab())
        tab_bar.add_tab("视频关键帧", self._build_keyframe_tab())
        tab_bar.add_tab("视觉分析", self._build_analysis_tab())
        tabs_layout.addWidget(tab_bar)
        root.addWidget(tabs_shell)

        footer_actions = QFrame(panel)
        footer_actions.setStyleSheet(_inner_card_style())
        footer_layout = QHBoxLayout(footer_actions)
        footer_layout.setContentsMargins(16, 16, 16, 16)
        footer_layout.setSpacing(10)

        footer_layout.addWidget(SecondaryButton("复制全文", footer_actions, icon_text="⧉"))
        footer_layout.addWidget(SecondaryButton("导出 JSON", footer_actions, icon_text="{}"))
        footer_layout.addWidget(SecondaryButton("导出 SRT", footer_actions, icon_text="字幕"))
        footer_layout.addStretch(1)
        footer_layout.addWidget(PrimaryButton("AI 智能改写", footer_actions, icon_text="✦"))
        root.addWidget(footer_actions)
        return panel

    def _build_script_tab(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(4)
        title = QLabel("AI 生成脚本文案", panel)
        title.setStyleSheet(_card_title_style())
        subtitle = QLabel("保留时间戳、角色和镜头提示，可直接复制到提词器或文案编辑器。", panel)
        subtitle.setStyleSheet(_muted_label_style())
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        top_row.addLayout(title_col)
        top_row.addStretch(1)

        self._segment_count_label = QLabel("共 9 段可用脚本", panel)
        segment_count_label = self._segment_count_label
        if segment_count_label is not None:
            segment_count_label.setStyleSheet(_capsule_style(ACCENT_SOFT, ACCENT, ACCENT_STRONG))
            top_row.addWidget(segment_count_label)
        root.addLayout(top_row)

        summary = QFrame(panel)
        summary.setStyleSheet(_inner_card_style())
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(14, 14, 14, 14)
        summary_layout.setSpacing(10)
        summary_layout.addWidget(self._build_small_metric_card("高转化段落", "3 段", "痛点、成品特写、评论触发", "brand", summary))
        summary_layout.addWidget(self._build_small_metric_card("平均置信度", "94%", "已自动修正口头禅与停顿词", "success", summary))
        summary_layout.addWidget(self._build_small_metric_card("建议复录长度", "55 秒", "去掉重复语气词后的最佳版本", "info", summary))
        root.addWidget(summary)

        self._streaming_output = StreamingOutputWidget(panel)
        root.addWidget(self._streaming_output)

        script_list = QFrame(panel)
        script_list.setStyleSheet(_frame_style())
        list_layout = QVBoxLayout(script_list)
        list_layout.setContentsMargins(16, 16, 16, 16)
        list_layout.setSpacing(12)
        list_title = QLabel("逐段脚本明细", script_list)
        list_title.setStyleSheet(_card_title_style())
        list_layout.addWidget(list_title)

        self._segment_host = QWidget(script_list)
        self._segment_layout = QVBoxLayout(self._segment_host)
        segment_layout = self._segment_layout
        if segment_layout is not None:
            segment_layout.setContentsMargins(0, 0, 0, 0)
            segment_layout.setSpacing(10)
        list_layout.addWidget(self._segment_host)
        root.addWidget(script_list)
        return panel

    def _build_keyframe_tab(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        title = QLabel("提取关键帧网格", panel)
        title.setStyleSheet(_card_title_style())
        helper = QLabel("已从 300 帧中筛选 12 张高信息密度画面。", panel)
        helper.setStyleSheet(_muted_label_style())
        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(4)
        title_col.addWidget(title)
        title_col.addWidget(helper)
        header.addLayout(title_col)
        header.addStretch(1)
        header.addWidget(TagChip("封面候选 2 张", tone="warning", parent=panel))
        header.addWidget(TagChip("剧情节点 5 个", tone="brand", parent=panel))
        root.addLayout(header)

        self._keyframe_grid = ImageGrid(columns=4, parent=panel)
        root.addWidget(self._keyframe_grid)

        detail_shell = QFrame(panel)
        detail_shell.setStyleSheet(_frame_style())
        detail_layout = QVBoxLayout(detail_shell)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(10)
        detail_title = QLabel("关键帧说明", detail_shell)
        detail_title.setStyleSheet(_card_title_style())
        detail_layout.addWidget(detail_title)

        for keyframe in KEYFRAME_ITEMS[:6]:
            detail_layout.addWidget(self._build_keyframe_detail_card(keyframe, detail_shell))

        root.addWidget(detail_shell)
        return panel

    def _build_analysis_tab(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(10)
        top.addWidget(TagChip("画面语义识别已开启", tone="brand", parent=panel))
        top.addWidget(TagChip("OCR 文本补全 6 处", tone="info", parent=panel))
        top.addWidget(TagChip("CTA 强度高", tone="success", parent=panel))
        top.addStretch(1)
        root.addLayout(top)

        strategy_row = QHBoxLayout()
        strategy_row.setContentsMargins(0, 0, 0, 0)
        strategy_row.setSpacing(12)
        strategy_row.addWidget(self._build_small_metric_card("视觉记忆点", "4 处", "成品特写、参数面板、价格字幕、购物车 CTA", "brand", panel))
        strategy_row.addWidget(self._build_small_metric_card("适合投放场景", "信息流", "教程类商品视频，适配高频消费类目", "success", panel))
        strategy_row.addWidget(self._build_small_metric_card("建议补镜头", "1 处", "可增加“腌制前后对比”提升可信度", "warning", panel))
        root.addLayout(strategy_row)

        self._analysis_host = QWidget(panel)
        self._analysis_layout = QVBoxLayout(self._analysis_host)
        analysis_layout = self._analysis_layout
        if analysis_layout is not None:
            analysis_layout.setContentsMargins(0, 0, 0, 0)
            analysis_layout.setSpacing(10)
        root.addWidget(self._analysis_host)
        return panel

    def _build_ai_config_section(self) -> QWidget:
        section = ContentSection("AI 模型配置与导出预设", icon="✦", parent=self)

        split = SplitPanel("horizontal", split_ratio=(0.42, 0.58), minimum_sizes=(320, 520), parent=section)
        split.set_widgets(self._build_ai_left_panel(), self._build_ai_right_panel())
        section.content_layout.addWidget(split)
        return section

    def _build_ai_left_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._ai_config_panel = AIConfigPanel(panel)
        root.addWidget(self._ai_config_panel)

        config_summary = QFrame(panel)
        config_summary.setStyleSheet(_inner_card_style())
        config_summary_layout = QVBoxLayout(config_summary)
        config_summary_layout.setContentsMargins(16, 16, 16, 16)
        config_summary_layout.setSpacing(8)

        config_summary_title = QLabel("当前模型摘要", config_summary)
        config_summary_title.setStyleSheet(_card_title_style())
        self._ai_config_summary_label = QLabel("等待同步 AI 配置…", config_summary)
        ai_config_summary_label = self._ai_config_summary_label
        if ai_config_summary_label is not None:
            ai_config_summary_label.setStyleSheet(_body_label_style())
            _call(ai_config_summary_label, "setWordWrap", True)

        config_summary_layout.addWidget(config_summary_title)
        if ai_config_summary_label is not None:
            config_summary_layout.addWidget(ai_config_summary_label)
        root.addWidget(config_summary)

        preset_card = QFrame(panel)
        preset_card.setStyleSheet(_frame_style())
        preset_layout = QVBoxLayout(preset_card)
        preset_layout.setContentsMargins(16, 16, 16, 16)
        preset_layout.setSpacing(12)

        preset_title = QLabel("推荐导出格式", preset_card)
        preset_title.setStyleSheet(_card_title_style())
        preset_layout.addWidget(preset_title)

        for preset in EXPORT_PRESETS:
            preset_layout.addWidget(self._build_export_card(preset, preset_card))

        root.addWidget(preset_card)
        return panel

    def _build_ai_right_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        summary = QFrame(panel)
        summary.setStyleSheet(_frame_style())
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(12)

        title = QLabel("模型使用建议", summary)
        title.setStyleSheet(_card_title_style())
        summary_layout.addWidget(title)

        summary_layout.addWidget(
            InfoCard(
                title="当前配置更适合脚本重构",
                description="建议使用 OpenAI / gpt-4o，并将角色设为“脚本创作者”。温度维持 0.6-0.8 区间，可以同时保留结构性和口语化表达。",
                icon="▶",
                action_text="同步到当前任务",
                parent=summary,
            )
        )

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(10)
        badge_row.addWidget(StatsBadge("推荐模型", "gpt-4o", "◎", "brand", summary))
        badge_row.addWidget(StatsBadge("角色", "脚本创作者", "✦", "success", summary))
        badge_row.addWidget(StatsBadge("温度", "0.7", "◔", "info", summary))
        summary_layout.addLayout(badge_row)

        root.addWidget(summary)

        export_status = QFrame(panel)
        export_status.setStyleSheet(_frame_style())
        export_layout = QVBoxLayout(export_status)
        export_layout.setContentsMargins(16, 16, 16, 16)
        export_layout.setSpacing(10)

        export_title = QLabel("当前导出策略", export_status)
        export_title.setStyleSheet(_card_title_style())
        export_layout.addWidget(export_title)

        self._selected_export_label = QLabel(
            "默认将同时导出：逐字稿 JSON、提词器脚本、分镜复盘表。",
            export_status,
        )
        selected_export_label = self._selected_export_label
        if selected_export_label is not None:
            selected_export_label.setStyleSheet(_body_label_style())
            _call(selected_export_label, "setWordWrap", True)
            export_layout.addWidget(selected_export_label)

        checklist = QFrame(export_status)
        checklist.setStyleSheet(_inner_card_style())
        checklist_layout = QVBoxLayout(checklist)
        checklist_layout.setContentsMargins(14, 14, 14, 14)
        checklist_layout.setSpacing(8)
        checklist_layout.addWidget(self._build_check_item("保留原始时间戳", True, checklist))
        checklist_layout.addWidget(self._build_check_item("输出镜头说明", True, checklist))
        checklist_layout.addWidget(self._build_check_item("自动去除语气词", True, checklist))
        checklist_layout.addWidget(self._build_check_item("生成二创复录版", False, checklist))
        export_layout.addWidget(checklist)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(10)
        actions.addWidget(SecondaryButton("复制配置 JSON", export_status, icon_text="⧉"))
        actions.addWidget(PrimaryButton("应用到当前任务", export_status, icon_text="⚡"))
        export_layout.addLayout(actions)

        root.addWidget(export_status)
        root.addStretch(1)
        return panel

    def _build_history_section(self) -> QWidget:
        section = ContentSection("历史提取记录", icon="⌛", parent=self)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)

        self._history_search = SearchBar("搜索任务名称、来源或导出结果...")
        controls.addWidget(self._history_search, 2)

        self._history_filter = FilterDropdown(
            "任务状态",
            ["全部", "已导出", "复盘中", "已完成", "等待下载"],
            include_all=False,
        )
        self._history_filter.set_current_text("全部")
        controls.addWidget(self._history_filter, 1)

        self._history_count_label = QLabel("共 4 条历史记录", section)
        history_count_label = self._history_count_label
        if history_count_label is not None:
            history_count_label.setStyleSheet(_capsule_style(SURFACE_SOFT, TEXT_SECONDARY, BORDER))
            controls.addWidget(history_count_label)
        section.content_layout.addLayout(controls)

        self._history_host = QWidget(section)
        self._history_layout = QVBoxLayout(self._history_host)
        history_layout = self._history_layout
        if history_layout is not None:
            history_layout.setContentsMargins(0, 0, 0, 0)
            history_layout.setSpacing(10)
        section.content_layout.addWidget(self._history_host)
        return section

    def _build_capability_section(self) -> QWidget:
        section = ContentSection("能力亮点", icon="✧", parent=self)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        row.addWidget(
            InfoCard(
                title="ASR 语音增强",
                description="自动过滤背景噪音，增强达人人声，对口语、连读和短视频话术更友好。",
                icon="☏",
                action_text="查看识别策略",
                
            )
        )
        row.addWidget(
            InfoCard(
                title="视觉场景语义",
                description="自动识别镜头场景、画面主体、字幕信息和商品展示逻辑，形成分镜复盘。",
                icon="◫",
                action_text="查看视觉规则",
                
            )
        )
        row.addWidget(
            InfoCard(
                title="OCR 智能补全",
                description="捕捉视频内出现的价格字幕、参数说明、商品标签和封面文案，辅助脚本重构。",
                icon="▣",
                action_text="查看 OCR 输出",
                
            )
        )
        row.addWidget(
            InfoCard(
                title="极速任务调度",
                description="可同时输出逐字稿、分镜表与复录脚本，适合运营批量处理内容素材。",
                icon="⚡",
                action_text="查看批处理方案",
                
            )
        )
        section.content_layout.addLayout(row)
        return section

    def _build_footer_section(self) -> QWidget:
        section = ContentSection("操作建议", icon="◎", parent=self)

        shell = QFrame(section)
        shell.setStyleSheet(_frame_style(accent=True))
        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(6)
        title = QLabel("建议下一步：直接生成二创复录版脚本", shell)
        title.setStyleSheet(_headline_style())
        note = QLabel(
            "当前素材已经具备较完整的时间轴、镜头说明与卖点结构，继续执行“AI 智能改写”可生成更适合短视频复录、达人矩阵分发和短视频素材的话术版本。",
            shell,
        )
        note.setStyleSheet(_body_label_style())
        _call(note, "setWordWrap", True)
        text_col.addWidget(title)
        text_col.addWidget(note)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(10)
        action_row.addWidget(PrimaryButton("生成复录版脚本", shell, icon_text="✦"))
        action_row.addWidget(SecondaryButton("下载脚本包", shell, icon_text="⇩"))
        action_row.addWidget(SecondaryButton("复制逐字稿", shell, icon_text="⧉"))
        action_row.addStretch(1)
        text_col.addLayout(action_row)

        shell_layout.addLayout(text_col, 2)
        shell_layout.addWidget(
            StatsBadge("推荐输出", "复录版 + SRT", "◎", "brand", shell),
        )
        shell_layout.addWidget(
            StatsBadge("适用场景", "投流 / 二创", "◔", "success", shell),
        )

        section.content_layout.addWidget(shell)
        return section

    def _build_small_metric_card(
        self,
        label: str,
        value: str,
        detail: str,
        tone: str,
        parent: QWidget,
    ) -> QWidget:
        foreground, background, border = _tone_colors(tone)
        card = QFrame(parent)
        card.setStyleSheet(
            f"background-color: {background}; border: 1px solid {border}; border-radius: 14px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        top = QLabel(label, card)
        top.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; font-weight: 600;")
        number = QLabel(value, card)
        number.setStyleSheet(_metric_value_style(foreground))
        note = QLabel(detail, card)
        note.setStyleSheet(_muted_label_style())
        _call(note, "setWordWrap", True)

        layout.addWidget(top)
        layout.addWidget(number)
        layout.addWidget(note)
        return card

    def _build_keyframe_detail_card(self, keyframe: KeyframeItem, parent: QWidget) -> QWidget:
        foreground, background, border = _tone_colors("brand")
        card = QFrame(parent)
        card.setStyleSheet(
            f"background-color: {SURFACE_ALT}; border: 1px solid {BORDER}; border-radius: 14px;"
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        stamp = QLabel(keyframe.timestamp, card)
        stamp.setStyleSheet(
            f"color: {foreground}; background-color: {background}; border: 1px solid {border}; border-radius: 999px; padding: 6px 12px; font-weight: 700;"
        )
        layout.addWidget(stamp)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(4)
        title = QLabel(keyframe.title, card)
        title.setStyleSheet(_card_title_style())
        desc = QLabel(keyframe.description, card)
        desc.setStyleSheet(_body_label_style())
        _call(desc, "setWordWrap", True)
        content.addWidget(title)
        content.addWidget(desc)

        tag_row = QHBoxLayout()
        tag_row.setContentsMargins(0, 0, 0, 0)
        tag_row.setSpacing(8)
        tag_row.addWidget(TagChip(keyframe.scene_tag, tone="brand", parent=card))
        tag_row.addWidget(TagChip(keyframe.focus, tone="success", parent=card))
        tag_row.addWidget(TagChip(keyframe.emotion, tone="info", parent=card))
        tag_row.addStretch(1)
        content.addLayout(tag_row)

        layout.addLayout(content, 1)
        layout.addWidget(SecondaryButton("定位此帧", card, icon_text="↗"))
        return card

    def _build_export_card(self, preset: ExportPreset, parent: QWidget) -> QWidget:
        foreground, background, border = _tone_colors(preset.tone)
        card = QFrame(parent)
        card.setStyleSheet(
            f"background-color: {background}; border: 1px solid {border}; border-radius: 14px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        name = QLabel(preset.name, card)
        name.setStyleSheet(f"color: {foreground}; font-size: 14px; font-weight: 700;")
        note = QLabel(preset.note, card)
        note.setStyleSheet(_body_label_style())
        _call(note, "setWordWrap", True)
        layout.addWidget(name)
        layout.addWidget(note)
        return card

    def _build_check_item(self, text: str, checked: bool, parent: QWidget) -> QWidget:
        row = QWidget(parent)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        icon = QLabel("✓" if checked else "○", row)
        icon.setStyleSheet(
            f"color: {SUCCESS if checked else TEXT_MUTED}; font-size: 14px; font-weight: 700;"
        )
        label = QLabel(text, row)
        label.setStyleSheet(_body_label_style())

        layout.addWidget(icon)
        layout.addWidget(label)
        layout.addStretch(1)
        return row

    def _bind_events(self) -> None:
        if self._history_search is not None:
            _connect(self._history_search.search_changed, self._on_history_search_changed)
        if self._history_filter is not None:
            _connect(self._history_filter.filter_changed, self._on_history_filter_changed)
        if self._ai_config_panel is not None:
            _connect(self._ai_config_panel.config_changed, self._update_ai_config_summary)

    def _update_ai_config_summary(self, _config: dict[str, object] | None = None) -> None:
        if self._ai_config_panel is None:
            return
        config = self._ai_config_panel.config()
        provider = str(config.get("provider_label", "AI"))
        model = str(config.get("model", "gpt-4o"))
        role = str(config.get("agent_role", "脚本创作者"))
        temperature = config.get("temperature", 0.7)
        top_p = config.get("top_p", 0.9)
        max_tokens = config.get("max_tokens", 4096)

        if self._ai_config_summary_label is not None:
            self._ai_config_summary_label.setText(
                f"{provider} · {model} · {role} · 温度 {temperature} · Top-p {top_p} · 输出上限 {max_tokens} Token。"
                "当前配置适合逐段脚本重构、口播润色与二创复录。"
            )
        if self._selected_export_label is not None:
            self._selected_export_label.setText(
                "默认将同时导出：逐字稿 JSON、提词器脚本、分镜复盘表。\n"
                f"当前 AI：{provider} · {model} · {role}，便于在 {max_tokens} Token 上限内保留时间戳与镜头说明。"
            )

    def _seed_demo_values(self) -> None:
        if self._url_input is not None:
            self._url_input.setText("https://www.bilibili.com/video/BV1Tk4y1script-demo")
        if self._analysis_mode_combo is not None:
            _call(self._analysis_mode_combo.combo_box, "setCurrentText", "混合模式（ASR + 视觉）")
        if self._frame_interval_combo is not None:
            _call(self._frame_interval_combo.combo_box, "setCurrentText", "自动抽帧")
        if self._scene_focus_combo is not None:
            _call(self._scene_focus_combo.combo_box, "setCurrentText", "脚本拆解")
        if self._note_editor is not None:
            self._note_editor.setPlainText(
                "输出适合复录的脚本版本，保留每段时间戳；重点标记高转化镜头、价格锚点和评论区触发话术。"
            )
        if self._video_player is not None:
            self._video_player.set_duration(68)
            self._video_player.set_position(31)
        if self._ai_config_panel is not None:
            self._ai_config_panel.set_config(
                {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "agent_role": "脚本创作者",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "top_p": 0.92,
                }
            )
        if self._keyframe_grid is not None:
            self._keyframe_grid.clear_items()
            for keyframe in KEYFRAME_ITEMS:
                self._keyframe_grid.add_item(keyframe.path, duration=keyframe.timestamp, status="ready")

    def _render_streaming_output(self) -> None:
        if self._streaming_output is None:
            return
        self._streaming_output.clear()
        self._streaming_output.set_loading(False)
        _call(self._streaming_output, "setWindowTitle", "")
        output_body = getattr(self._streaming_output, "_output", None)
        if output_body is not None:
            html_text = _script_html(SCRIPT_SEGMENTS)
            set_html = getattr(output_body, "setHtml", None)
            if callable(set_html):
                set_html(html_text)
            else:
                plain = "\n\n".join(
                    f"[{segment.timestamp}] {segment.segment_type}\n{segment.script_text}\n镜头提示：{segment.visual_hint}"
                    for segment in SCRIPT_SEGMENTS
                )
                _call(output_body, "setPlainText", plain)
        self._streaming_output.set_token_usage(1684, 932)

    def _render_pipeline_phases(self) -> None:
        if self._phase_layout is None:
            return
        _clear_layout(self._phase_layout)
        for phase in PIPELINE_PHASES:
            self._phase_layout.addWidget(self._build_phase_card(phase))
        self._phase_layout.addStretch(1)

    def _render_script_segments(self) -> None:
        if self._segment_layout is None:
            return
        _clear_layout(self._segment_layout)
        for segment in SCRIPT_SEGMENTS:
            self._segment_layout.addWidget(self._build_segment_card(segment))
        self._segment_layout.addStretch(1)
        if self._segment_count_label is not None:
            self._segment_count_label.setText(f"共 {len(SCRIPT_SEGMENTS)} 段可用脚本")

    def _render_visual_insights(self) -> None:
        if self._analysis_layout is None:
            return
        _clear_layout(self._analysis_layout)
        for insight in VISUAL_INSIGHTS:
            self._analysis_layout.addWidget(self._build_visual_insight_card(insight))
        self._analysis_layout.addStretch(1)

    def _render_history_items(self) -> None:
        if self._history_layout is None:
            return
        _clear_layout(self._history_layout)
        matched = [
            item for item in HISTORY_ITEMS if _history_matches(item, self._history_keyword, self._history_status)
        ]
        for item in matched:
            self._history_layout.addWidget(self._build_history_card(item))
        self._history_layout.addStretch(1)
        if self._history_count_label is not None:
            self._history_count_label.setText(f"共 {len(matched)} 条历史记录")

    def _build_phase_card(self, phase: TimelinePhase) -> QWidget:
        tone = _tone_badge(phase.tone)
        card = QFrame(self)
        card.setStyleSheet(_inner_card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        name = QLabel(phase.name, card)
        name.setStyleSheet(_card_title_style())
        top.addWidget(name)
        top.addStretch(1)
        top.addWidget(TagChip(phase.status, tone=tone, parent=card))
        layout.addLayout(top)

        note = QLabel(phase.note, card)
        note.setStyleSheet(_muted_label_style())
        _call(note, "setWordWrap", True)
        layout.addWidget(note)
        return card

    def _build_segment_card(self, segment: ScriptSegment) -> QWidget:
        foreground, background, border = _tone_colors(segment.tone)
        card = QFrame(self)
        card.setStyleSheet(
            f"background-color: {SURFACE}; border: 1px solid {border}; border-radius: 16px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        stamp = QLabel(segment.timestamp, card)
        stamp.setStyleSheet(
            f"color: {foreground}; background-color: {background}; border: 1px solid {border}; border-radius: 999px; padding: 5px 12px; font-weight: 700;"
        )
        header.addWidget(stamp)
        header.addWidget(TagChip(segment.segment_type, tone=_tone_badge(segment.tone), parent=card))
        header.addWidget(TagChip(segment.strategy_tag, tone="neutral", parent=card))
        header.addStretch(1)
        header.addWidget(QLabel(f"{segment.speaker} · 置信度 {segment.confidence}%", card))
        layout.addLayout(header)

        summary = QLabel(segment.summary, card)
        summary.setStyleSheet(_card_title_style())
        _call(summary, "setWordWrap", True)
        layout.addWidget(summary)

        script = QLabel(segment.script_text, card)
        script.setStyleSheet(_body_label_style())
        _call(script, "setWordWrap", True)
        layout.addWidget(script)

        visual = QLabel(f"镜头提示：{segment.visual_hint}", card)
        visual.setStyleSheet(_muted_label_style())
        _call(visual, "setWordWrap", True)
        layout.addWidget(visual)

        progress_row = QHBoxLayout()
        progress_row.setContentsMargins(0, 0, 0, 0)
        progress_row.setSpacing(10)
        line = QFrame(card)
        line.setStyleSheet(_progress_bar_style(segment.confidence, segment.tone))
        _call(line, "setMinimumHeight", 8)
        progress_row.addWidget(line, 1)
        progress_row.addWidget(SecondaryButton("复制片段", card, icon_text="⧉"))
        layout.addLayout(progress_row)
        return card

    def _build_visual_insight_card(self, insight: VisualInsight) -> QWidget:
        foreground, background, border = _tone_colors(insight.tone)
        card = QFrame(self)
        card.setStyleSheet(
            f"background-color: {SURFACE}; border: 1px solid {border}; border-radius: 16px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        icon = QLabel(insight.icon, card)
        icon.setStyleSheet(
            f"color: {foreground}; background-color: {background}; border: 1px solid {border}; border-radius: 12px; padding: 8px 10px; font-weight: 700;"
        )
        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(4)
        title = QLabel(insight.title, card)
        title.setStyleSheet(_card_title_style())
        detail = QLabel(insight.detail, card)
        detail.setStyleSheet(_body_label_style())
        _call(detail, "setWordWrap", True)
        title_col.addWidget(title)
        title_col.addWidget(detail)
        header.addWidget(icon)
        header.addLayout(title_col, 1)
        layout.addLayout(header)

        highlight = QLabel(f"建议：{insight.highlight}", card)
        highlight.setStyleSheet(_capsule_style(background, foreground, border))
        _call(highlight, "setWordWrap", True)
        layout.addWidget(highlight)
        return card

    def _build_history_card(self, item: HistoryItem) -> QWidget:
        card = QFrame(self)
        card.setStyleSheet(_frame_style())
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(4)
        title = QLabel(item.title, card)
        title.setStyleSheet(_card_title_style())
        meta = QLabel(f"{item.created_at} · {item.source} · 视频时长 {item.duration}", card)
        meta.setStyleSheet(_muted_label_style())
        output = QLabel(f"输出内容：{item.output}", card)
        output.setStyleSheet(_body_label_style())
        left.addWidget(title)
        left.addWidget(meta)
        left.addWidget(output)

        layout.addLayout(left, 1)
        layout.addWidget(TagChip(item.status, tone=_tone_badge(item.tone), parent=card))
        layout.addWidget(SecondaryButton("打开记录", card, icon_text="↗"))
        return card

    def _on_history_search_changed(self, keyword: str) -> None:
        self._history_keyword = keyword
        self._render_history_items()

    def _on_history_filter_changed(self, status: str) -> None:
        self._history_status = status
        self._render_history_items()


__all__ = ["ScriptExtractorPage"]

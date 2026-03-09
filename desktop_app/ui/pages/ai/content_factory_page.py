# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""AI内容工厂页面。"""

from dataclasses import dataclass
from typing import Literal

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    AIStatusIndicator,
    ActionCard,
    ContentSection,
    FilterDropdown,
    FormGroup,
    IconButton,
    InfoCard,
    KPICard,
    LogViewer,
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
    TaskProgressBar,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ThemedTextEdit,
    TimelineWidget,
    ToggleSwitch,
)
from ..base_page import BasePage

ACCENT = "#00F2EA"
ACCENT_SOFT = "rgba(0, 242, 234, 0.10)"
ACCENT_STRONG = "rgba(0, 242, 234, 0.18)"
ACCENT_FAINT = "rgba(0, 242, 234, 0.06)"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"
INFO = "#3B82F6"
TEXT_PRIMARY = "#E6FFFB"
TEXT_MUTED = "#94A3B8"
TEXT_DARK = "#0F172A"
SURFACE = "#0F172A"
SURFACE_ALT = "#111827"
SURFACE_CARD = "#172033"
SURFACE_DEEP = "#0B1220"
SURFACE_LIGHT = "#F8FAFC"
BORDER = "rgba(148, 163, 184, 0.20)"
BORDER_STRONG = "rgba(0, 242, 234, 0.30)"

BadgeTone = Literal["success", "warning", "error", "info", "brand", "neutral"]


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用可能不存在的 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _set_layout(layout: object, margins: tuple[int, int, int, int], spacing: int) -> None:
    """统一设置布局边距与间距。"""

    setter = getattr(layout, "setContentsMargins", None)
    if callable(setter):
        setter(*margins)
    spacing_setter = getattr(layout, "setSpacing", None)
    if callable(spacing_setter):
        spacing_setter(spacing)


def _connect(signal_object: object, callback: object) -> None:
    """安全连接 Qt 信号。"""

    connect_method = getattr(signal_object, "connect", None)
    if callable(connect_method):
        connect_method(callback)


def _clear_layout(layout: object) -> None:
    """移除布局中的全部子项。"""

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
            layout_method = getattr(item, "layout", None)
            if callable(layout_method):
                child_layout = layout_method()
                if child_layout is not None:
                    _clear_layout(child_layout)


def _panel_style(
    object_name: str,
    *,
    background: str = SURFACE_CARD,
    border: str = BORDER,
    radius: int = 18,
    padding: int | None = None,
) -> str:
    """生成基础面板样式。"""

    padding_rule = f"padding: {padding}px;" if padding is not None else ""
    return (
        f"QWidget#{object_name}, QFrame#{object_name} {{"
        f"background-color: {background};"
        f"border: 1px solid {border};"
        f"border-radius: {radius}px;"
        f"{padding_rule}"
        "}"
    )


def _label_style(*, size: int = 13, weight: int = 500, color: str = TEXT_MUTED) -> str:
    """生成统一标签样式。"""

    return f"color: {color}; font-size: {size}px; font-weight: {weight}; background: transparent;"


def _title_style(*, size: int = 18, weight: int = 700, color: str = TEXT_PRIMARY) -> str:
    """生成统一标题样式。"""

    return f"color: {color}; font-size: {size}px; font-weight: {weight}; background: transparent;"


def _button_style(*, primary: bool = False, danger: bool = False) -> str:
    """局部按钮样式。"""

    background = ACCENT if primary else (ERROR if danger else "rgba(15, 23, 42, 0.35)")
    text_color = TEXT_DARK if primary else ("#FFFFFF" if danger else TEXT_PRIMARY)
    border_color = ACCENT if primary else (ERROR if danger else BORDER)
    hover_background = "#28FFF4" if primary else ("rgba(239, 68, 68, 0.90)" if danger else ACCENT_SOFT)
    hover_text = TEXT_DARK if primary else ("#FFFFFF" if danger else ACCENT)
    return f"""
        QPushButton {{
            background-color: {background};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 12px;
            min-height: 40px;
            padding: 8px 18px;
            font-size: 13px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: {hover_background};
            color: {hover_text};
            border-color: {border_color};
        }}
    """


@dataclass(frozen=True)
class FactoryComponentItem:
    """左侧组件库条目。"""

    title: str
    icon: str
    summary: str
    tone: str


@dataclass(frozen=True)
class WorkflowTemplateData:
    """工作流模板数据。"""

    name: str
    scene: str
    cadence: str
    output_count: str
    conversion_hint: str
    description: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class ProjectSnapshot:
    """项目概览数据。"""

    name: str
    status: str
    owner: str
    progress: str
    next_step: str


@dataclass(frozen=True)
class WorkflowNodeData:
    """工作流节点数据。"""

    key: str
    stage: str
    title: str
    description: str
    provider_label: str
    model_label: str
    role_label: str
    prompt_summary: str
    input_hint: str
    output_hint: str
    estimated_duration: str
    status_text: str
    status_tone: BadgeTone
    quality_score: str
    tokens_text: str
    tags: tuple[str, ...]
    accent: str
    highlighted: bool = False


@dataclass(frozen=True)
class WorkflowBranchData:
    """画布中的支线节点数据。"""

    title: str
    detail: str
    owner: str
    tone: str


@dataclass(frozen=True)
class WorkflowHistoryData:
    """工作流时间线数据。"""

    timestamp: str
    title: str
    content: str
    event_type: str


@dataclass(frozen=True)
class BatchRunData:
    """批次运行数据。"""

    batch_id: str
    name: str
    progress: int
    status: str
    throughput: str
    eta: str
    note: str


@dataclass(frozen=True)
class QueueMetricData:
    """批次指标摘要。"""

    label: str
    value: str
    icon: str
    tone: BadgeTone


class AIContentFactoryPage(BasePage):
    """AI内容工厂工作流页面。"""

    default_route_id: RouteId = RouteId("ai_content_factory")
    default_display_name: str = "AI内容工厂"
    default_icon_name: str = "factory"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._component_inventory = self._build_component_inventory()
        self._template_data = self._build_template_data()
        self._project_data = self._build_project_data()
        self._workflow_nodes = self._build_workflow_nodes()
        self._branch_nodes = self._build_branch_nodes()
        self._history_items = self._build_history_items()
        self._batch_runs = self._build_batch_runs()
        self._queue_metrics = self._build_queue_metrics()
        self._selected_template_name = self._template_data[0].name
        self._selected_node_key = "copy_generation"

        self._template_selector: ThemedComboBox | None = None
        self._node_filter: FilterDropdown | None = None
        self._status_indicator: AIStatusIndicator | None = None
        self._selected_node_title: QLabel | None = None
        self._selected_node_summary: QLabel | None = None
        self._selected_node_meta: QLabel | None = None
        self._selected_node_status: StatusBadge | None = None
        self._selected_node_input: ThemedTextEdit | None = None
        self._selected_node_output: ThemedTextEdit | None = None
        self._selected_node_prompt: ThemedTextEdit | None = None
        self._selected_node_temperature: ThemedLineEdit | None = None
        self._selected_node_max_tokens: ThemedLineEdit | None = None
        self._selected_node_scene: ThemedComboBox | None = None
        self._auto_retry_toggle: ToggleSwitch | None = None
        self._human_review_toggle: ToggleSwitch | None = None
        self._history_timeline: TimelineWidget | None = None
        self._log_viewer: LogViewer | None = None
        self._output_preview: StreamingOutputWidget | None = None
        self._execution_progress: TaskProgressBar | None = None
        self._ai_config_panel: AIConfigPanel | None = None
        self._ai_config_summary_label: QLabel | None = None
        self._node_model_matrix_layout: QVBoxLayout | None = None
        self._template_card_layout: QVBoxLayout | None = None
        self._canvas_lane_layout: QHBoxLayout | None = None
        self._batch_list_layout: QVBoxLayout | None = None

        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建 AI 内容工厂完整页面。"""

        _call(self, "setObjectName", "aiContentFactoryPage")
        _set_layout(self.layout, (0, 0, 0, 0), 0)

        page_container = PageContainer(
            title="AI内容工厂",
            description="围绕素材分析、文案生成、标题优化、封面建议与发布编排构建可复用内容流水线。",
            max_width=1760,
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._status_indicator = AIStatusIndicator(page_container)
        self._status_indicator.set_status("就绪")
        page_container.add_action(self._status_indicator)

        snapshot_button = SecondaryButton("保存版本", page_container, icon_text="◎")
        publish_button = PrimaryButton("推送执行队列", page_container, icon_text="▶")
        page_container.add_action(snapshot_button)
        page_container.add_action(publish_button)

        page_container.add_widget(self._build_overview_strip())
        page_container.add_widget(self._build_workspace())

        self._refresh_template_cards()
        self._refresh_canvas_lane()
        self._refresh_node_model_matrix()
        self._refresh_batch_cards()
        self._populate_timeline()
        self._populate_output_preview()
        self._populate_log_viewer()
        self._sync_selected_node_controls()
        self._apply_page_styles()

    def _build_overview_strip(self) -> QWidget:
        """顶部概览指标区。"""

        host = QWidget(self)
        _call(host, "setObjectName", "factoryOverviewStrip")
        layout = QHBoxLayout(host)
        _set_layout(layout, (0, 0, 0, 0), 14)

        template_count = KPICard(
            title="模板覆盖",
            value="12 套",
            trend="up",
            percentage="+3 套",
            caption="本周新增工作流模板",
            sparkline_data=[5, 6, 7, 8, 9, 10, 12],
            parent=host,
        )
        run_efficiency = KPICard(
            title="产能效率",
            value="86%",
            trend="up",
            percentage="+8.4%",
            caption="节点自动化命中率",
            sparkline_data=[58, 62, 66, 72, 77, 82, 86],
            parent=host,
        )
        review_latency = KPICard(
            title="人工复核耗时",
            value="18 分钟",
            trend="down",
            percentage="-6 分钟",
            caption="发布前平均校审时长",
            sparkline_data=[42, 38, 35, 29, 25, 22, 18],
            parent=host,
        )
        strategy_card = InfoCard(
            title="推荐策略",
            description="优先使用“爆款短视频流水线”模板，将素材分析与标题优化节点串联批量运行，可提升封面点击与转化承接。",
            icon="✦",
            action_text="查看模板差异",
            parent=host,
        )

        layout.addWidget(template_count, 1)
        layout.addWidget(run_efficiency, 1)
        layout.addWidget(review_latency, 1)
        layout.addWidget(strategy_card, 2)
        return host

    def _build_workspace(self) -> QWidget:
        """主体工作区。"""

        workspace = QWidget(self)
        _call(workspace, "setObjectName", "factoryWorkspace")
        layout = QHBoxLayout(workspace)
        _set_layout(layout, (0, 0, 0, 0), 18)

        outer_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.27, 0.73),
            minimum_sizes=(340, 960),
            parent=workspace,
        )
        outer_split.set_widgets(self._build_left_sidebar(), self._build_main_stage())
        layout.addWidget(outer_split)
        return workspace

    def _build_left_sidebar(self) -> QWidget:
        """左侧模板、组件和历史区域。"""

        scroll = ThemedScrollArea(self)
        _call(scroll, "setObjectName", "factorySidebarScroll")
        scroll.content_layout.setSpacing(16)

        scroll.add_widget(self._build_template_section())
        scroll.add_widget(self._build_component_library_section())
        scroll.add_widget(self._build_project_section())
        scroll.add_widget(self._build_history_section())
        scroll.content_layout.addStretch(1)
        return scroll

    def _build_template_section(self) -> QWidget:
        """工作流模板选择区。"""

        section = ContentSection("工作流模板", icon="◎", parent=self)

        header_note = QLabel("根据短视频素材、商品混剪、活动预热等场景一键切换节点编排。", section)
        _call(header_note, "setWordWrap", True)
        _call(header_note, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        self._template_selector = ThemedComboBox(
            label="模板选择器",
            items=[template.name for template in self._template_data],
            parent=None,
        )
        _call(self._template_selector.combo_box, "setCurrentText", self._selected_template_name)
        _connect(getattr(self._template_selector.combo_box, "currentTextChanged", None), self._on_template_changed)

        template_search = SearchBar("搜索工作流模板、节点策略或行业场景...", None)
        workflow_mode = FilterDropdown(
            label="工作模式",
            items=["批量量产", "灵感试跑", "达人定制", "活动冲刺"],
            include_all=False,
            parent=None,
        )
        workflow_mode.set_current_text("批量量产")

        cards_host = QWidget(section)
        _call(cards_host, "setObjectName", "factoryTemplateCards")
        self._template_card_layout = QVBoxLayout(cards_host)
        _set_layout(self._template_card_layout, (0, 0, 0, 0), 10)

        section.add_widget(header_note)
        section.add_widget(self._template_selector)
        section.add_widget(template_search)
        section.add_widget(workflow_mode)
        section.add_widget(cards_host)
        return section

    def _build_component_library_section(self) -> QWidget:
        """左侧组件库。"""

        section = ContentSection("组件库", icon="◫", parent=self)
        tip = QLabel("拖拽感通过视觉模拟呈现，可将分析、生成、导出节点快速拼装为链路。", section)
        _call(tip, "setWordWrap", True)
        _call(tip, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        section.add_widget(tip)

        for item in self._component_inventory:
            card = self._build_component_inventory_card(item, section)
            section.add_widget(card)
        return section

    def _build_project_section(self) -> QWidget:
        """左侧项目概览区。"""

        section = ContentSection("我的项目", icon="▣", parent=self)

        project_card = ActionCard(
            title=self._project_data.name,
            description=(
                f"负责人：{self._project_data.owner} · 当前进度 {self._project_data.progress} · 下一步：{self._project_data.next_step}"
            ),
            icon="◎",
            button_text="进入项目排程",
            status_text=self._project_data.status,
            status_tone="brand",
            parent=section,
        )
        section.add_widget(project_card)

        meta_host = QWidget(section)
        meta_layout = QVBoxLayout(meta_host)
        _set_layout(meta_layout, (0, 0, 0, 0), 8)
        for text in (
            "• 今日计划：完成 24 条种草视频文案与 12 套封面建议",
            "• 自动发布窗口：19:30 - 23:00，优先投放美妆与家清类目",
            "• 协同提醒：法务复核已绑定到敏感词检查节点",
        ):
            item = QLabel(text, meta_host)
            _call(item, "setWordWrap", True)
            _call(item, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
            meta_layout.addWidget(item)
        section.add_widget(meta_host)
        return section

    def _build_history_section(self) -> QWidget:
        """左侧工作流历史。"""

        section = ContentSection("工作流历史", icon="⌛", parent=self)

        summary_row = QWidget(section)
        summary_layout = QHBoxLayout(summary_row)
        _set_layout(summary_layout, (0, 0, 0, 0), 8)
        summary_layout.addWidget(StatsBadge(label="今日运行", value="8 次", icon="▶", tone="brand", parent=summary_row))
        summary_layout.addWidget(StatsBadge(label="完成率", value="92%", icon="◎", tone="success", parent=summary_row))
        summary_layout.addWidget(StatsBadge(label="待复核", value="3 条", icon="◌", tone="warning", parent=summary_row))
        section.add_widget(summary_row)

        self._history_timeline = TimelineWidget(None)
        section.add_widget(self._history_timeline)
        return section

    def _build_main_stage(self) -> QWidget:
        """中右主舞台区域。"""

        host = QWidget(self)
        layout = QVBoxLayout(host)
        _set_layout(layout, (0, 0, 0, 0), 18)

        vertical_split = SplitPanel(
            orientation="vertical",
            split_ratio=(0.62, 0.38),
            minimum_sizes=(560, 360),
            parent=host,
        )

        upper_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.67, 0.33),
            minimum_sizes=(760, 360),
            parent=host,
        )
        upper_split.set_widgets(self._build_canvas_stage(), self._build_node_config_panel())

        vertical_split.set_widgets(upper_split, self._build_output_stage())
        layout.addWidget(vertical_split)
        return host

    def _build_canvas_stage(self) -> QWidget:
        """中央工作流画布区域。"""

        stage = QFrame(self)
        _call(stage, "setObjectName", "factoryCanvasStage")
        layout = QVBoxLayout(stage)
        _set_layout(layout, (18, 18, 18, 18), 14)

        layout.addWidget(self._build_canvas_toolbar())

        subhead = QWidget(stage)
        subhead_layout = QHBoxLayout(subhead)
        _set_layout(subhead_layout, (0, 0, 0, 0), 10)
        subhead_layout.addWidget(StatusBadge("工作流设计中", tone="brand", parent=subhead))
        subhead_layout.addWidget(TagChip("目标：单日量产 30 条", tone="brand", parent=subhead))
        subhead_layout.addWidget(TagChip("分发渠道：TikTok Shop", tone="neutral", parent=subhead))
        subhead_layout.addWidget(TagChip("风格：高转化种草", tone="neutral", parent=subhead))
        subhead_layout.addStretch(1)
        subhead_layout.addWidget(StatsBadge(label="预计耗时", value="14 分钟", icon="⌛", tone="info", parent=subhead))
        layout.addWidget(subhead)

        canvas_scroll = ThemedScrollArea(stage)
        _call(canvas_scroll, "setObjectName", "factoryCanvasScroll")
        canvas_scroll.content_layout.setSpacing(16)

        canvas_title = QLabel("工作流画布", stage)
        _call(canvas_title, "setStyleSheet", _title_style(size=18, color=TEXT_PRIMARY))
        canvas_scroll.add_widget(canvas_title)

        canvas_hint = QLabel(
            "当前链路围绕“素材分析 → 卖点提炼 → 文案生成 → 标题优化 → 封面建议 → 发布排程”串联，并保留字幕包装支线。",
            stage,
        )
        _call(canvas_hint, "setWordWrap", True)
        _call(canvas_hint, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        canvas_scroll.add_widget(canvas_hint)

        grid_shell = QFrame(stage)
        _call(grid_shell, "setObjectName", "factoryCanvasGrid")
        grid_layout = QVBoxLayout(grid_shell)
        _set_layout(grid_layout, (20, 20, 20, 20), 18)

        lane_host = QWidget(grid_shell)
        self._canvas_lane_layout = QHBoxLayout(lane_host)
        _set_layout(self._canvas_lane_layout, (0, 0, 0, 0), 10)
        grid_layout.addWidget(lane_host)

        branch_host = self._build_canvas_branch_lane(grid_shell)
        grid_layout.addWidget(branch_host)

        metrics_row = QWidget(grid_shell)
        metrics_layout = QHBoxLayout(metrics_row)
        _set_layout(metrics_layout, (0, 0, 0, 0), 10)
        metrics_layout.addWidget(InfoCard(
            title="节点协作提示",
            description="文案生成节点已与标题优化、封面建议共享卖点摘要，避免信息割裂与重复调用。",
            icon="◫",
            action_text="查看依赖图",
            parent=metrics_row,
        ))
        metrics_layout.addWidget(InfoCard(
            title="质量控制",
            description="输出会在敏感词检查与品牌语气校验后进入人工复核区，再投递到发布排程。",
            icon="◎",
            action_text="打开质检策略",
            parent=metrics_row,
        ))
        grid_layout.addWidget(metrics_row)

        canvas_scroll.add_widget(grid_shell)
        layout.addWidget(canvas_scroll, 1)
        layout.addWidget(self._build_canvas_footer())
        return stage

    def _build_canvas_toolbar(self) -> QWidget:
        """画布工具栏与执行控制。"""

        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "factoryCanvasToolbar")
        layout = QHBoxLayout(toolbar)
        _set_layout(layout, (14, 12, 14, 12), 10)

        left_group = QWidget(toolbar)
        left_layout = QHBoxLayout(left_group)
        _set_layout(left_layout, (0, 0, 0, 0), 8)
        left_layout.addWidget(IconButton("↶", "撤销", left_group))
        left_layout.addWidget(IconButton("↷", "重做", left_group))
        left_layout.addWidget(IconButton("＋", "放大画布", left_group))
        left_layout.addWidget(IconButton("－", "缩小画布", left_group))

        zoom_chip = QLabel("缩放 100%", left_group)
        _call(zoom_chip, "setStyleSheet", _label_style(size=12, weight=700, color=ACCENT))
        left_layout.addWidget(zoom_chip)

        self._node_filter = FilterDropdown(
            label="节点聚焦",
            items=["全部节点", "分析链路", "生成链路", "优化链路", "发布链路"],
            include_all=False,
            parent=None,
        )
        self._node_filter.set_current_text("全部节点")

        right_group = QWidget(toolbar)
        right_layout = QHBoxLayout(right_group)
        _set_layout(right_layout, (0, 0, 0, 0), 8)

        save_button = SecondaryButton("保存草稿", right_group, icon_text="◎")
        pause_button = QPushButton("暂停", right_group)
        stop_button = QPushButton("终止", right_group)
        run_button = PrimaryButton("运行工作流", right_group, icon_text="▶")
        _call(pause_button, "setStyleSheet", _button_style())
        _call(stop_button, "setStyleSheet", _button_style(danger=True))

        right_layout.addWidget(save_button)
        right_layout.addWidget(pause_button)
        right_layout.addWidget(stop_button)
        right_layout.addWidget(run_button)

        layout.addWidget(left_group)
        layout.addWidget(self._node_filter)
        layout.addStretch(1)
        layout.addWidget(right_group)
        return toolbar

    def _build_canvas_branch_lane(self, parent: QWidget) -> QWidget:
        """构建支线路径展示。"""

        host = QWidget(parent)
        layout = QVBoxLayout(host)
        _set_layout(layout, (0, 0, 0, 0), 10)

        title = QLabel("支线处理", host)
        _call(title, "setStyleSheet", _title_style(size=15, color=TEXT_PRIMARY))
        desc = QLabel("主链文案完成后，会触发字幕包装与素材归档支线，保证发布资产同步齐全。", host)
        _call(desc, "setWordWrap", True)
        _call(desc, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        layout.addWidget(title)
        layout.addWidget(desc)

        branch_row = QWidget(host)
        branch_layout = QHBoxLayout(branch_row)
        _set_layout(branch_layout, (0, 0, 0, 0), 10)

        left_spacer = QWidget(branch_row)
        _call(left_spacer, "setMinimumWidth", 310)
        branch_layout.addWidget(left_spacer)
        branch_layout.addWidget(self._build_vertical_connector(branch_row))
        branch_layout.addWidget(self._build_branch_card(self._branch_nodes[0], branch_row))
        branch_layout.addWidget(self._build_horizontal_connector("同步稿件", branch_row))
        branch_layout.addWidget(self._build_branch_card(self._branch_nodes[1], branch_row))
        branch_layout.addStretch(1)

        layout.addWidget(branch_row)
        return host

    def _build_canvas_footer(self) -> QWidget:
        """画布底部状态区。"""

        footer = QFrame(self)
        _call(footer, "setObjectName", "factoryCanvasFooter")
        layout = QHBoxLayout(footer)
        _set_layout(layout, (12, 10, 12, 10), 12)

        left = QWidget(footer)
        left_layout = QHBoxLayout(left)
        _set_layout(left_layout, (0, 0, 0, 0), 8)
        left_layout.addWidget(StatusBadge("系统就绪", tone="success", parent=left))
        left_layout.addWidget(TagChip("GPU 加速：已开启", tone="success", parent=left))
        left_layout.addWidget(TagChip("并发槽位：6 / 8", tone="neutral", parent=left))
        left_layout.addWidget(TagChip("工作流ID：wf_20260309_018", tone="neutral", parent=left))

        right = QWidget(footer)
        right_layout = QHBoxLayout(right)
        _set_layout(right_layout, (0, 0, 0, 0), 8)
        right_layout.addWidget(StatsBadge(label="主链节点", value="6 个", icon="◫", tone="brand", parent=right))
        right_layout.addWidget(StatsBadge(label="支线节点", value="2 个", icon="◎", tone="info", parent=right))
        right_layout.addWidget(StatsBadge(label="预估成本", value="¥ 18.7", icon="¤", tone="warning", parent=right))

        layout.addWidget(left)
        layout.addStretch(1)
        layout.addWidget(right)
        return footer

    def _build_node_config_panel(self) -> QWidget:
        """右侧节点配置面板。"""

        scroll = ThemedScrollArea(self)
        _call(scroll, "setObjectName", "factoryConfigScroll")
        scroll.content_layout.setSpacing(16)

        scroll.add_widget(self._build_execution_control_section())
        scroll.add_widget(self._build_selected_node_section())
        scroll.add_widget(self._build_ai_config_section())
        scroll.add_widget(self._build_model_matrix_section())
        scroll.add_widget(self._build_prompt_strategy_section())
        scroll.add_widget(self._build_parameter_section())
        scroll.content_layout.addStretch(1)
        return scroll

    def _build_execution_control_section(self) -> QWidget:
        """执行控制与运行状态。"""

        section = ContentSection("执行控制", icon="▶", parent=self)

        badge_row = QWidget(section)
        badge_layout = QHBoxLayout(badge_row)
        _set_layout(badge_layout, (0, 0, 0, 0), 8)
        badge_layout.addWidget(StatusBadge("排队就绪", tone="success", parent=badge_row))
        badge_layout.addWidget(TagChip("实时校验开启", tone="success", parent=badge_row))
        badge_layout.addWidget(TagChip("失败自动重试", tone="warning", parent=badge_row))
        badge_layout.addStretch(1)

        controls_row = QWidget(section)
        controls_layout = QHBoxLayout(controls_row)
        _set_layout(controls_layout, (0, 0, 0, 0), 8)
        run_button = PrimaryButton("立即运行", controls_row, icon_text="▶")
        pause_button = QPushButton("暂停队列", controls_row)
        stop_button = QPushButton("终止运行", controls_row)
        _call(pause_button, "setStyleSheet", _button_style())
        _call(stop_button, "setStyleSheet", _button_style(danger=True))
        controls_layout.addWidget(run_button)
        controls_layout.addWidget(pause_button)
        controls_layout.addWidget(stop_button)

        self._execution_progress = TaskProgressBar(72, None)

        notes = QLabel(
            "当前批次正在处理第 18 / 24 条任务，预计 7 分钟后进入人工复核；标题优化节点已完成高转化词替换。",
            section,
        )
        _call(notes, "setWordWrap", True)
        _call(notes, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        section.add_widget(badge_row)
        section.add_widget(controls_row)
        section.add_widget(self._execution_progress)
        section.add_widget(notes)
        return section

    def _build_selected_node_section(self) -> QWidget:
        """当前选中节点摘要。"""

        section = ContentSection("节点配置", icon="◎", parent=self)

        title_row = QWidget(section)
        title_layout = QHBoxLayout(title_row)
        _set_layout(title_layout, (0, 0, 0, 0), 8)
        self._selected_node_title = QLabel("", title_row)
        self._selected_node_status = StatusBadge("", tone="brand", parent=title_row)
        _call(self._selected_node_title, "setStyleSheet", _title_style(size=18, color=TEXT_PRIMARY))
        title_layout.addWidget(self._selected_node_title)
        title_layout.addStretch(1)
        title_layout.addWidget(self._selected_node_status)

        self._selected_node_summary = QLabel("", section)
        _call(self._selected_node_summary, "setWordWrap", True)
        _call(self._selected_node_summary, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        self._selected_node_meta = QLabel("", section)
        _call(self._selected_node_meta, "setWordWrap", True)
        _call(self._selected_node_meta, "setStyleSheet", _label_style(size=12, color=ACCENT))

        self._selected_node_input = ThemedTextEdit(label="输入约束", placeholder="节点输入约束", parent=None)
        self._selected_node_output = ThemedTextEdit(label="输出目标", placeholder="节点输出目标", parent=None)

        section.add_widget(title_row)
        section.add_widget(self._selected_node_summary)
        section.add_widget(self._selected_node_meta)
        section.add_widget(self._selected_node_input)
        section.add_widget(self._selected_node_output)
        return section

    def _build_ai_config_section(self) -> QWidget:
        """选中节点 AI 配置区。"""

        section = ContentSection("AI模型配置", icon="✦", parent=self)
        self._ai_config_panel = AIConfigPanel(None)
        section.add_widget(self._ai_config_panel)

        summary_card = QFrame(section)
        _call(summary_card, "setObjectName", "factoryAiConfigSummary")
        summary_layout = QVBoxLayout(summary_card)
        _set_layout(summary_layout, (14, 14, 14, 14), 6)
        summary_title = QLabel("当前节点模型摘要", summary_card)
        _call(summary_title, "setStyleSheet", _title_style(size=15, color=TEXT_PRIMARY))
        self._ai_config_summary_label = QLabel("等待同步节点 AI 配置…", summary_card)
        _call(self._ai_config_summary_label, "setWordWrap", True)
        _call(self._ai_config_summary_label, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self._ai_config_summary_label)
        section.add_widget(summary_card)

        _connect(self._ai_config_panel.config_changed, self._on_ai_config_changed)
        return section

    def _build_model_matrix_section(self) -> QWidget:
        """各节点模型矩阵。"""

        section = ContentSection("节点模型编排", icon="◫", parent=self)
        intro = QLabel("为每个节点配置独立模型、角色和生成策略，便于在批量模式下优化成本与质量平衡。", section)
        _call(intro, "setWordWrap", True)
        _call(intro, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        matrix_host = QWidget(section)
        self._node_model_matrix_layout = QVBoxLayout(matrix_host)
        _set_layout(self._node_model_matrix_layout, (0, 0, 0, 0), 10)

        section.add_widget(intro)
        section.add_widget(matrix_host)
        return section

    def _build_prompt_strategy_section(self) -> QWidget:
        """提示词策略。"""

        section = ContentSection("提示词策略", icon="⌕", parent=self)
        self._selected_node_prompt = ThemedTextEdit(label="节点提示词摘要", placeholder="提示词策略", parent=None)
        section.add_widget(self._selected_node_prompt)

        chip_row = QWidget(section)
        chip_layout = QHBoxLayout(chip_row)
        _set_layout(chip_layout, (0, 0, 0, 0), 8)
        chip_layout.addWidget(TagChip("保留商品核心卖点", tone="brand", parent=chip_row))
        chip_layout.addWidget(TagChip("优先口语化表达", tone="success", parent=chip_row))
        chip_layout.addWidget(TagChip("避免敏感承诺", tone="warning", parent=chip_row))
        chip_layout.addWidget(TagChip("支持 A/B 两版产出", tone="neutral", parent=chip_row))
        chip_layout.addStretch(1)
        section.add_widget(chip_row)
        return section

    def _build_parameter_section(self) -> QWidget:
        """右侧参数详情。"""

        section = ContentSection("节点参数细化", icon="▤", parent=self)

        self._selected_node_scene = ThemedComboBox(
            label="投放场景",
            items=["新品冷启", "日常冲量", "短视频引流", "节日活动", "达人合作"],
            parent=None,
        )
        self._selected_node_temperature = ThemedLineEdit(
            label="创意温度",
            placeholder="0.7",
            helper_text="越高越发散，越低越稳健。",
            parent=None,
        )
        self._selected_node_max_tokens = ThemedLineEdit(
            label="输出上限",
            placeholder="2048",
            helper_text="建议按节点复杂度控制生成长度。",
            parent=None,
        )

        retry_toggle_widget = QWidget(section)
        retry_toggle_layout = QHBoxLayout(retry_toggle_widget)
        _set_layout(retry_toggle_layout, (0, 0, 0, 0), 10)
        retry_label = QLabel("失败后自动重试", retry_toggle_widget)
        _call(retry_label, "setStyleSheet", _label_style(size=13, color=TEXT_PRIMARY, weight=600))
        self._auto_retry_toggle = ToggleSwitch(True, None)
        retry_toggle_layout.addWidget(retry_label)
        retry_toggle_layout.addStretch(1)
        retry_toggle_layout.addWidget(self._auto_retry_toggle)

        review_toggle_widget = QWidget(section)
        review_toggle_layout = QHBoxLayout(review_toggle_widget)
        _set_layout(review_toggle_layout, (0, 0, 0, 0), 10)
        review_label = QLabel("进入人工复核", review_toggle_widget)
        _call(review_label, "setStyleSheet", _label_style(size=13, color=TEXT_PRIMARY, weight=600))
        self._human_review_toggle = ToggleSwitch(True, None)
        review_toggle_layout.addWidget(review_label)
        review_toggle_layout.addStretch(1)
        review_toggle_layout.addWidget(self._human_review_toggle)

        safe_notes = ThemedTextEdit(
            label="风控与审核备注",
            placeholder="例如：避免使用绝对化词汇，保留价格口径统一。",
            parent=None,
        )
        safe_notes.setPlainText(
            "1. 标题中避免出现夸大功效；\n"
            "2. 口播文案保留品牌指定的功能点顺序；\n"
            "3. 封面建议需同步活动主视觉关键词。"
        )

        scene_group = FormGroup("场景选择", self._selected_node_scene, "决定文案风格与节奏。", parent=section)
        temp_group = FormGroup("创意温度", self._selected_node_temperature, "用于控制表达发散程度。", parent=section)
        token_group = FormGroup("输出上限", self._selected_node_max_tokens, "限制单节点生成成本。", parent=section)

        section.add_widget(scene_group)
        section.add_widget(temp_group)
        section.add_widget(token_group)
        section.add_widget(retry_toggle_widget)
        section.add_widget(review_toggle_widget)
        section.add_widget(safe_notes)
        return section

    def _build_output_stage(self) -> QWidget:
        """底部输出与日志区域。"""

        host = QFrame(self)
        _call(host, "setObjectName", "factoryOutputStage")
        layout = QVBoxLayout(host)
        _set_layout(layout, (18, 18, 18, 18), 14)

        header = QWidget(host)
        header_layout = QHBoxLayout(header)
        _set_layout(header_layout, (0, 0, 0, 0), 10)
        title = QLabel("输出与复盘", header)
        _call(title, "setStyleSheet", _title_style(size=18, color=TEXT_PRIMARY))
        desc = QLabel("预览生成稿、查看批次队列，并跟踪执行日志与复盘记录。", header)
        _call(desc, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        right_summary = QWidget(header)
        right_summary_layout = QHBoxLayout(right_summary)
        _set_layout(right_summary_layout, (0, 0, 0, 0), 8)
        right_summary_layout.addWidget(TagChip("预览版本：V12", tone="brand", parent=right_summary))
        right_summary_layout.addWidget(TagChip("人工复核：待 3 条", tone="warning", parent=right_summary))
        right_summary_layout.addWidget(TagChip("可直接发布：21 条", tone="success", parent=right_summary))

        text_group = QWidget(header)
        text_group_layout = QVBoxLayout(text_group)
        _set_layout(text_group_layout, (0, 0, 0, 0), 2)
        text_group_layout.addWidget(title)
        text_group_layout.addWidget(desc)

        header_layout.addWidget(text_group)
        header_layout.addStretch(1)
        header_layout.addWidget(right_summary)

        tabs = TabBar(host)
        tabs.add_tab("输出预览", self._build_preview_tab())
        tabs.add_tab("批次队列", self._build_batch_tab())
        tabs.add_tab("执行日志", self._build_log_tab())

        layout.addWidget(header)
        layout.addWidget(tabs, 1)
        return host

    def _build_preview_tab(self) -> QWidget:
        """输出预览标签页。"""

        container = QWidget(self)
        layout = QHBoxLayout(container)
        _set_layout(layout, (0, 0, 0, 0), 16)

        split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.66, 0.34),
            minimum_sizes=(640, 320),
            parent=container,
        )

        left = QWidget(container)
        left_layout = QVBoxLayout(left)
        _set_layout(left_layout, (0, 0, 0, 0), 14)
        self._output_preview = StreamingOutputWidget(left)
        left_layout.addWidget(self._output_preview)

        preview_note = QLabel(
            "预览内容会同步展示口播结构、标题建议、卖点排序与封面文案，支持复制到投放或脚本编辑模块继续加工。",
            left,
        )
        _call(preview_note, "setWordWrap", True)
        _call(preview_note, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        left_layout.addWidget(preview_note)

        right = QWidget(container)
        right_layout = QVBoxLayout(right)
        _set_layout(right_layout, (0, 0, 0, 0), 12)

        right_layout.addWidget(ActionCard(
            title="一键投递下一环节",
            description="当输出通过人工复核后，可直接将标题、口播文案与封面建议推送到发布排程。",
            icon="▶",
            button_text="推送到发布排程",
            status_text="待确认",
            status_tone="warning",
            parent=right,
        ))
        right_layout.addWidget(InfoCard(
            title="预览摘要",
            description="当前版本重点强化了‘轻便不漏水’与‘通勤露营双场景适配’两个记忆点，标题优先强调场景代入。",
            icon="◎",
            action_text="查看差异比较",
            parent=right,
        ))

        chips = QWidget(right)
        chips_layout = QVBoxLayout(chips)
        _set_layout(chips_layout, (0, 0, 0, 0), 8)
        chip_title = QLabel("输出标签", chips)
        _call(chip_title, "setStyleSheet", _title_style(size=15, color=TEXT_PRIMARY))
        chips_layout.addWidget(chip_title)

        chip_row_1 = QWidget(chips)
        chip_row_1_layout = QHBoxLayout(chip_row_1)
        _set_layout(chip_row_1_layout, (0, 0, 0, 0), 8)
        chip_row_1_layout.addWidget(TagChip("高转化标题", tone="brand", parent=chip_row_1))
        chip_row_1_layout.addWidget(TagChip("新品预热", tone="info", parent=chip_row_1))
        chip_row_1_layout.addWidget(TagChip("轻快口语化", tone="success", parent=chip_row_1))
        chip_row_1_layout.addStretch(1)

        chip_row_2 = QWidget(chips)
        chip_row_2_layout = QHBoxLayout(chip_row_2)
        _set_layout(chip_row_2_layout, (0, 0, 0, 0), 8)
        chip_row_2_layout.addWidget(TagChip("封面一句话", tone="neutral", parent=chip_row_2))
        chip_row_2_layout.addWidget(TagChip("A/B 双版本", tone="warning", parent=chip_row_2))
        chip_row_2_layout.addWidget(TagChip("可自动配音", tone="neutral", parent=chip_row_2))
        chip_row_2_layout.addStretch(1)

        chips_layout.addWidget(chip_row_1)
        chips_layout.addWidget(chip_row_2)
        right_layout.addWidget(chips)
        right_layout.addStretch(1)

        split.set_widgets(left, right)
        layout.addWidget(split)
        return container

    def _build_batch_tab(self) -> QWidget:
        """批次队列标签页。"""

        host = QWidget(self)
        layout = QHBoxLayout(host)
        _set_layout(layout, (0, 0, 0, 0), 16)

        left = QWidget(host)
        left_layout = QVBoxLayout(left)
        _set_layout(left_layout, (0, 0, 0, 0), 12)

        metric_row = QWidget(left)
        metric_layout = QHBoxLayout(metric_row)
        _set_layout(metric_layout, (0, 0, 0, 0), 8)
        for metric in self._queue_metrics:
            metric_layout.addWidget(StatsBadge(label=metric.label, value=metric.value, icon=metric.icon, tone=metric.tone, parent=metric_row))
        left_layout.addWidget(metric_row)

        batch_list = QFrame(left)
        _call(batch_list, "setObjectName", "factoryBatchList")
        self._batch_list_layout = QVBoxLayout(batch_list)
        _set_layout(self._batch_list_layout, (12, 12, 12, 12), 10)
        left_layout.addWidget(batch_list)

        right = QWidget(host)
        right_layout = QVBoxLayout(right)
        _set_layout(right_layout, (0, 0, 0, 0), 12)
        right_layout.addWidget(InfoCard(
            title="队列策略",
            description="默认按“活动优先级 → 素材完整度 → 类目热度”进行排序。晚高峰时段自动提升标题优化与封面建议节点并发。",
            icon="◫",
            action_text="调整排队规则",
            parent=right,
        ))
        right_layout.addWidget(ActionCard(
            title="空闲时段预跑",
            description="可在凌晨窗口提前生成标题与封面建议，次日只保留人工复核与发布编排。",
            icon="⌛",
            button_text="加入夜间任务",
            status_text="建议开启",
            status_tone="success",
            parent=right,
        ))
        right_layout.addWidget(InfoCard(
            title="质量抽检提醒",
            description="批量运行超过 20 条时，系统会自动抽取 3 条进入复核，确保文案语气和价格口径一致。",
            icon="◎",
            action_text="查看抽检规则",
            parent=right,
        ))
        right_layout.addStretch(1)

        layout.addWidget(left, 2)
        layout.addWidget(right, 1)
        return host

    def _build_log_tab(self) -> QWidget:
        """执行日志标签页。"""

        host = QWidget(self)
        layout = QHBoxLayout(host)
        _set_layout(layout, (0, 0, 0, 0), 16)

        self._log_viewer = LogViewer(None)

        side = QWidget(host)
        side_layout = QVBoxLayout(side)
        _set_layout(side_layout, (0, 0, 0, 0), 12)
        side_layout.addWidget(InfoCard(
            title="日志观察要点",
            description="优先关注模型切换、敏感词校验、人工复核挂起与发布排程回调等关键事件。",
            icon="⌕",
            action_text="导出错误摘要",
            parent=side,
        ))
        side_layout.addWidget(InfoCard(
            title="本轮异常说明",
            description="当前无严重错误。历史中有 1 次封面建议素材缺失，系统已自动切换到补图模板。",
            icon="◎",
            action_text="查看修复详情",
            parent=side,
        ))
        side_layout.addStretch(1)

        layout.addWidget(self._log_viewer, 2)
        layout.addWidget(side, 1)
        return host

    def _build_component_inventory_card(self, item: FactoryComponentItem, parent: QWidget) -> QWidget:
        """组件库卡片。"""

        card = QFrame(parent)
        object_name = f"factoryInventory_{item.title}"
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        _set_layout(layout, (12, 12, 12, 12), 6)

        title_row = QWidget(card)
        title_layout = QHBoxLayout(title_row)
        _set_layout(title_layout, (0, 0, 0, 0), 8)
        icon = QLabel(item.icon, title_row)
        title = QLabel(item.title, title_row)
        tone = StatusBadge(item.tone, tone="brand", parent=title_row)
        _call(icon, "setStyleSheet", _title_style(size=18, color=ACCENT))
        _call(title, "setStyleSheet", _title_style(size=14, color=TEXT_PRIMARY))
        title_layout.addWidget(icon)
        title_layout.addWidget(title)
        title_layout.addStretch(1)
        title_layout.addWidget(tone)

        summary = QLabel(item.summary, card)
        _call(summary, "setWordWrap", True)
        _call(summary, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        layout.addWidget(title_row)
        layout.addWidget(summary)
        _call(
            card,
            "setStyleSheet",
            _panel_style(object_name, background=SURFACE_DEEP, border=BORDER) + f" QLabel {{ background: transparent; }} ",
        )
        return card

    def _build_template_card(self, template: WorkflowTemplateData, parent: QWidget) -> QWidget:
        """模板卡片。"""

        is_active = template.name == self._selected_template_name
        object_name = f"factoryTemplate_{template.name}"
        card = QFrame(parent)
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        _set_layout(layout, (14, 14, 14, 14), 8)

        top = QWidget(card)
        top_layout = QHBoxLayout(top)
        _set_layout(top_layout, (0, 0, 0, 0), 8)
        title = QLabel(template.name, top)
        scene = StatusBadge(template.scene, tone="brand" if is_active else "info", parent=top)
        _call(title, "setStyleSheet", _title_style(size=15, color=TEXT_PRIMARY))
        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(scene)

        desc = QLabel(template.description, card)
        _call(desc, "setWordWrap", True)
        _call(desc, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        meta = QLabel(
            f"节奏：{template.cadence} · 单批输出：{template.output_count} · 提示：{template.conversion_hint}",
            card,
        )
        _call(meta, "setWordWrap", True)
        _call(meta, "setStyleSheet", _label_style(size=12, color=ACCENT if is_active else TEXT_MUTED))

        tag_row = QWidget(card)
        tag_layout = QHBoxLayout(tag_row)
        _set_layout(tag_layout, (0, 0, 0, 0), 6)
        for tag in template.tags:
            tag_layout.addWidget(TagChip(tag, tone="brand" if is_active else "neutral", parent=tag_row))
        tag_layout.addStretch(1)

        layout.addWidget(top)
        layout.addWidget(desc)
        layout.addWidget(meta)
        layout.addWidget(tag_row)
        _call(
            card,
            "setStyleSheet",
            _panel_style(
                object_name,
                background=ACCENT_SOFT if is_active else SURFACE_DEEP,
                border=ACCENT if is_active else BORDER,
                radius=18,
            ) + " QLabel { background: transparent; } ",
        )
        return card

    def _build_node_card(self, node: WorkflowNodeData, parent: QWidget) -> QWidget:
        """主链节点卡片。"""

        object_name = f"factoryNode_{node.key}"
        card = QFrame(parent)
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        _set_layout(layout, (16, 16, 16, 16), 8)
        _call(card, "setMinimumWidth", 240)
        _call(card, "setMaximumWidth", 240)

        stage = QLabel(node.stage, card)
        _call(stage, "setStyleSheet", _label_style(size=11, weight=800, color=node.accent))

        title_row = QWidget(card)
        title_layout = QHBoxLayout(title_row)
        _set_layout(title_layout, (0, 0, 0, 0), 8)
        title = QLabel(node.title, title_row)
        status = StatusBadge(node.status_text, tone=self._node_status_tone(node), parent=title_row)
        _call(title, "setWordWrap", True)
        _call(title, "setStyleSheet", _title_style(size=16, color=TEXT_PRIMARY))
        title_layout.addWidget(title)
        title_layout.addStretch(1)
        title_layout.addWidget(status)

        summary = QLabel(node.description, card)
        _call(summary, "setWordWrap", True)
        _call(summary, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        model = QLabel(f"模型：{node.provider_label} · {node.model_label}", card)
        role = QLabel(f"角色：{node.role_label}", card)
        prompt = QLabel(f"提示词：{node.prompt_summary}", card)
        _call(model, "setWordWrap", True)
        _call(role, "setWordWrap", True)
        _call(prompt, "setWordWrap", True)
        _call(model, "setStyleSheet", _label_style(size=12, color=TEXT_PRIMARY))
        _call(role, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        _call(prompt, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        tag_row = QWidget(card)
        tag_layout = QHBoxLayout(tag_row)
        _set_layout(tag_layout, (0, 0, 0, 0), 6)
        for tag in node.tags:
            tag_layout.addWidget(TagChip(tag, tone="brand" if node.highlighted else "neutral", parent=tag_row))
        tag_layout.addStretch(1)

        io_box = QWidget(card)
        io_layout = QVBoxLayout(io_box)
        _set_layout(io_layout, (0, 0, 0, 0), 4)
        input_label = QLabel(f"输入：{node.input_hint}", io_box)
        output_label = QLabel(f"输出：{node.output_hint}", io_box)
        _call(input_label, "setWordWrap", True)
        _call(output_label, "setWordWrap", True)
        _call(input_label, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        _call(output_label, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        io_layout.addWidget(input_label)
        io_layout.addWidget(output_label)

        metric_row = QWidget(card)
        metric_layout = QHBoxLayout(metric_row)
        _set_layout(metric_layout, (0, 0, 0, 0), 6)
        metric_layout.addWidget(StatsBadge(label="质量", value=node.quality_score, icon="◎", tone="success", parent=metric_row))
        metric_layout.addWidget(StatsBadge(label="Token", value=node.tokens_text, icon="◫", tone="info", parent=metric_row))

        footer = QWidget(card)
        footer_layout = QHBoxLayout(footer)
        _set_layout(footer_layout, (0, 0, 0, 0), 6)
        port_in = QLabel("● 输入", footer)
        duration = QLabel(f"预计：{node.estimated_duration}", footer)
        port_out = QLabel("输出 ●", footer)
        _call(port_in, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        _call(duration, "setStyleSheet", _label_style(size=12, color=node.accent, weight=700))
        _call(port_out, "setStyleSheet", _label_style(size=12, color=node.accent, weight=700))
        footer_layout.addWidget(port_in)
        footer_layout.addStretch(1)
        footer_layout.addWidget(duration)
        footer_layout.addStretch(1)
        footer_layout.addWidget(port_out)

        layout.addWidget(stage)
        layout.addWidget(title_row)
        layout.addWidget(summary)
        layout.addWidget(model)
        layout.addWidget(role)
        layout.addWidget(prompt)
        layout.addWidget(tag_row)
        layout.addWidget(io_box)
        layout.addWidget(metric_row)
        layout.addWidget(footer)

        background = ACCENT_SOFT if node.highlighted else SURFACE_DEEP
        border = node.accent if node.highlighted else BORDER
        _call(
            card,
            "setStyleSheet",
            _panel_style(object_name, background=background, border=border, radius=20)
            + " QLabel { background: transparent; } "
            + (f" QFrame#{object_name} {{ box-shadow: 0 0 0 1px {node.accent}; }} " if node.highlighted else ""),
        )
        return card

    def _build_branch_card(self, branch: WorkflowBranchData, parent: QWidget) -> QWidget:
        """支线节点卡片。"""

        object_name = f"factoryBranch_{branch.title}"
        card = QFrame(parent)
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        _set_layout(layout, (12, 12, 12, 12), 6)
        _call(card, "setMinimumWidth", 210)

        title = QLabel(branch.title, card)
        detail = QLabel(branch.detail, card)
        owner = QLabel(f"执行角色：{branch.owner}", card)
        _call(title, "setStyleSheet", _title_style(size=14, color=TEXT_PRIMARY))
        _call(detail, "setWordWrap", True)
        _call(owner, "setWordWrap", True)
        _call(detail, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        _call(owner, "setStyleSheet", _label_style(size=12, color=branch.tone))

        layout.addWidget(title)
        layout.addWidget(detail)
        layout.addWidget(owner)
        _call(card, "setStyleSheet", _panel_style(object_name, background=SURFACE_DEEP, border=branch.tone, radius=16) + " QLabel { background: transparent; }")
        return card

    def _build_horizontal_connector(self, text: str, parent: QWidget) -> QWidget:
        """主链连接器。"""

        connector = QWidget(parent)
        layout = QVBoxLayout(connector)
        _set_layout(layout, (0, 0, 0, 0), 4)
        label = QLabel(text, connector)
        _call(label, "setStyleSheet", _label_style(size=11, weight=700, color=TEXT_MUTED))
        line = QLabel("────────▶", connector)
        _call(line, "setStyleSheet", _title_style(size=18, color=ACCENT))
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addWidget(line)
        layout.addStretch(1)
        return connector

    def _build_vertical_connector(self, parent: QWidget) -> QWidget:
        """支线垂直连接器。"""

        connector = QWidget(parent)
        layout = QVBoxLayout(connector)
        _set_layout(layout, (0, 0, 0, 0), 2)
        top = QLabel("│", connector)
        mid = QLabel("├─ 支线", connector)
        bottom = QLabel("▼", connector)
        _call(top, "setStyleSheet", _title_style(size=18, color=ACCENT))
        _call(mid, "setStyleSheet", _label_style(size=11, weight=700, color=TEXT_MUTED))
        _call(bottom, "setStyleSheet", _title_style(size=18, color=ACCENT))
        layout.addWidget(top)
        layout.addWidget(mid)
        layout.addWidget(bottom)
        return connector

    def _build_node_model_card(self, node: WorkflowNodeData, parent: QWidget) -> QWidget:
        """右侧节点模型矩阵卡片。"""

        is_selected = node.key == self._selected_node_key
        object_name = f"factoryModelCard_{node.key}"
        card = QFrame(parent)
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        _set_layout(layout, (12, 12, 12, 12), 6)

        top = QWidget(card)
        top_layout = QHBoxLayout(top)
        _set_layout(top_layout, (0, 0, 0, 0), 8)
        title = QLabel(node.title, top)
        badge = StatusBadge(node.status_text, tone=self._node_status_tone(node), parent=top)
        _call(title, "setStyleSheet", _title_style(size=14, color=TEXT_PRIMARY))
        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(badge)

        model = QLabel(f"{node.provider_label} · {node.model_label}", card)
        role = QLabel(f"角色：{node.role_label}", card)
        prompt = QLabel(node.prompt_summary, card)
        _call(model, "setWordWrap", True)
        _call(role, "setWordWrap", True)
        _call(prompt, "setWordWrap", True)
        _call(model, "setStyleSheet", _label_style(size=12, color=ACCENT if is_selected else TEXT_PRIMARY))
        _call(role, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        _call(prompt, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        footer = QLabel(f"耗时 {node.estimated_duration} · 用量 {node.tokens_text}", card)
        _call(footer, "setStyleSheet", _label_style(size=11, weight=700, color=node.accent))

        layout.addWidget(top)
        layout.addWidget(model)
        layout.addWidget(role)
        layout.addWidget(prompt)
        layout.addWidget(footer)

        _call(
            card,
            "setStyleSheet",
            _panel_style(
                object_name,
                background=ACCENT_FAINT if is_selected else SURFACE_DEEP,
                border=node.accent if is_selected else BORDER,
                radius=16,
            ) + " QLabel { background: transparent; } ",
        )
        return card

    def _build_batch_card(self, batch: BatchRunData, parent: QWidget) -> QWidget:
        """批次队列卡片。"""

        object_name = f"factoryBatch_{batch.batch_id}"
        card = QFrame(parent)
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        _set_layout(layout, (14, 14, 14, 14), 8)

        top = QWidget(card)
        top_layout = QHBoxLayout(top)
        _set_layout(top_layout, (0, 0, 0, 0), 8)
        title = QLabel(batch.name, top)
        status = StatusBadge(batch.status, tone=self._status_tone_for_batch(batch.status), parent=top)
        _call(title, "setStyleSheet", _title_style(size=15, color=TEXT_PRIMARY))
        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(status)

        meta = QLabel(
            f"批次编号：{batch.batch_id} · 吞吐：{batch.throughput} · 预计剩余：{batch.eta}",
            card,
        )
        note = QLabel(batch.note, card)
        _call(meta, "setWordWrap", True)
        _call(note, "setWordWrap", True)
        _call(meta, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))
        _call(note, "setStyleSheet", _label_style(size=12, color=TEXT_MUTED))

        progress = TaskProgressBar(batch.progress, None)
        layout.addWidget(top)
        layout.addWidget(meta)
        layout.addWidget(progress)
        layout.addWidget(note)

        _call(card, "setStyleSheet", _panel_style(object_name, background=SURFACE_DEEP, border=BORDER, radius=18) + " QLabel { background: transparent; }")
        return card

    def _refresh_template_cards(self) -> None:
        """刷新左侧模板卡片。"""

        if self._template_card_layout is None:
            return
        _clear_layout(self._template_card_layout)
        for template in self._template_data:
            self._template_card_layout.addWidget(self._build_template_card(template, self))

    def _refresh_canvas_lane(self) -> None:
        """刷新主链画布。"""

        if self._canvas_lane_layout is None:
            return
        _clear_layout(self._canvas_lane_layout)
        for index, node in enumerate(self._workflow_nodes):
            self._canvas_lane_layout.addWidget(self._build_node_card(node, self))
            if index < len(self._workflow_nodes) - 1:
                self._canvas_lane_layout.addWidget(self._build_horizontal_connector("数据流转", self))
        self._canvas_lane_layout.addStretch(1)

    def _refresh_node_model_matrix(self) -> None:
        """刷新右侧模型矩阵。"""

        if self._node_model_matrix_layout is None:
            return
        _clear_layout(self._node_model_matrix_layout)
        for node in self._workflow_nodes:
            self._node_model_matrix_layout.addWidget(self._build_node_model_card(node, self))

    def _refresh_batch_cards(self) -> None:
        """刷新批次卡片。"""

        if self._batch_list_layout is None:
            return
        _clear_layout(self._batch_list_layout)
        title = QLabel("运行批次", self)
        _call(title, "setStyleSheet", _title_style(size=16, color=TEXT_PRIMARY))
        self._batch_list_layout.addWidget(title)
        for batch in self._batch_runs:
            self._batch_list_layout.addWidget(self._build_batch_card(batch, self))
        self._batch_list_layout.addStretch(1)

    def _populate_timeline(self) -> None:
        """填充左侧时间线。"""

        if self._history_timeline is None:
            return
        self._history_timeline.set_events(
            [
                {
                    "timestamp": item.timestamp,
                    "title": item.title,
                    "content": item.content,
                    "type": item.event_type,
                }
                for item in self._history_items
            ]
        )

    def _populate_output_preview(self) -> None:
        """写入示例输出预览。"""

        if self._output_preview is None:
            return
        self._output_preview.clear()
        self._output_preview.append_chunk("【标题建议 A】通勤一天都热着喝，这个随行杯把颜值和保温都拉满！\n\n")
        self._output_preview.append_chunk("【标题建议 B】露营、上班都能带的高颜值保温杯，防漏到包里乱放也安心。\n\n")
        self._output_preview.append_chunk("【15 秒口播结构】\n")
        self._output_preview.append_chunk("1. 开场痛点：早上装的热饮，中午就凉掉？\n")
        self._output_preview.append_chunk("2. 核心卖点：双层真空保温、防漏锁扣、单手开盖、容量刚好。\n")
        self._output_preview.append_chunk("3. 场景代入：通勤包里随手一放不怕漏，露营拍照也很出片。\n")
        self._output_preview.append_chunk("4. 行动召唤：商品卡今天有组合券，想换杯子的可以直接冲。\n\n")
        self._output_preview.append_chunk("【封面一句话】带它出门，热饮真的能撑一整天。")
        self._output_preview.set_token_usage(1864, 962)

    def _populate_log_viewer(self) -> None:
        """填充示例日志。"""

        if self._log_viewer is None:
            return
        self._log_viewer.clear_logs()
        self._log_viewer.append_info("工作流载入完成：爆款短视频流水线，主链节点 6 个，支线节点 2 个。", "2026-03-09 09:20:11")
        self._log_viewer.append_info("素材分析节点完成视觉元素聚类，识别出‘轻便’‘防漏’‘保温’三大主卖点。", "2026-03-09 09:20:49")
        self._log_viewer.append_info("文案生成节点调用主模型完成两版口播脚本与三版标题草案。", "2026-03-09 09:21:28")
        self._log_viewer.append_warning("封面建议节点检测到素材中缺少户外近景，已自动替换为补图模板。", "2026-03-09 09:21:56")
        self._log_viewer.append_info("发布排程节点已匹配晚高峰时段 19:30-23:00，并生成分发优先级。", "2026-03-09 09:22:37")

    def _on_ai_config_changed(self, _config: dict[str, object]) -> None:
        self._update_ai_config_summary()

    def _update_ai_config_summary(self) -> None:
        if self._ai_config_panel is None or self._ai_config_summary_label is None:
            return
        config = self._ai_config_panel.config()
        node = self._selected_node()
        node_name = node.title if node is not None else "当前节点"
        self._ai_config_summary_label.setText(
            f"{node_name}：{config['provider_label']} · {config['model']} · {config['agent_role']} · 温度 {config['temperature']}"
            f" · Top-p {config['top_p']} · 输出上限 {config['max_tokens']} Token。"
            "适合在当前工作流节点中平衡质量、成本与复用效率。"
        )

    def _sync_selected_node_controls(self) -> None:
        """将选中节点数据同步到右侧面板。"""

        node = self._selected_node()
        if node is None:
            return

        if self._selected_node_title is not None:
            self._selected_node_title.setText(node.title)
        if self._selected_node_summary is not None:
            self._selected_node_summary.setText(node.description)
        if self._selected_node_meta is not None:
            self._selected_node_meta.setText(
                f"模型：{node.provider_label} · {node.model_label} · 角色：{node.role_label} · 预计耗时：{node.estimated_duration}"
            )
        if self._selected_node_status is not None:
            self._selected_node_status.setText(node.status_text)
            self._selected_node_status.set_tone(self._node_status_tone(node))
        if self._selected_node_input is not None:
            self._selected_node_input.setPlainText(
                f"- 输入素材：{node.input_hint}\n- 卖点约束：保留防漏、长效保温、通勤露营双场景\n- 风格要求：口语化、有记忆点、适合短视频前 3 秒抓人"
            )
        if self._selected_node_output is not None:
            self._selected_node_output.setPlainText(
                f"- 目标输出：{node.output_hint}\n- 质量标准：转化导向、品牌口径统一、支持短视频口播与短视频文案复用\n- 交付格式：标题 + 脚本 + 卖点摘要"
            )
        if self._selected_node_prompt is not None:
            self._selected_node_prompt.setPlainText(
                f"请以 {node.role_label} 的身份处理当前节点。\n"
                f"核心目标：{node.prompt_summary}\n"
                "请先提炼最强卖点，再用适合 TikTok Shop 的口语化表达输出。\n"
                "避免空泛形容词，优先写出能直接带动画面的细节和使用场景。"
            )
        if self._selected_node_scene is not None:
            _call(self._selected_node_scene.combo_box, "setCurrentText", "短视频引流" if node.key == "title_polish" else "日常冲量")
        if self._selected_node_temperature is not None:
            self._selected_node_temperature.setText("0.8" if node.key == "title_polish" else "0.7")
        if self._selected_node_max_tokens is not None:
            self._selected_node_max_tokens.setText("1536" if node.key == "title_polish" else "2048")
        if self._auto_retry_toggle is not None:
            self._auto_retry_toggle.setChecked(node.key not in {"publish_schedule"})
        if self._human_review_toggle is not None:
            self._human_review_toggle.setChecked(node.key in {"copy_generation", "title_polish", "cover_hook"})
        if self._ai_config_panel is not None:
            self._ai_config_panel.set_config(
                {
                    "provider": self._provider_key(node.provider_label),
                    "model": node.model_label,
                    "agent_role": node.role_label,
                    "temperature": 0.8 if node.key == "title_polish" else 0.7,
                    "max_tokens": 1536 if node.key == "title_polish" else 2048,
                    "top_p": 0.92,
                }
            )
        self._update_ai_config_summary()

    def _on_template_changed(self, template_name: str) -> None:
        """切换模板。"""

        self._selected_template_name = template_name
        self._refresh_template_cards()

    def _select_node(self, node_key: str) -> None:
        """切换选中节点。"""

        self._selected_node_key = node_key
        self._refresh_canvas_lane()
        self._refresh_node_model_matrix()
        self._sync_selected_node_controls()

    def _selected_node(self) -> WorkflowNodeData | None:
        """返回当前选中节点。"""

        for node in self._workflow_nodes:
            if node.key == self._selected_node_key:
                return node
        return self._workflow_nodes[0] if self._workflow_nodes else None

    def _provider_key(self, provider_label: str) -> str:
        """将展示名映射为 provider key。"""

        mapping = {
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "Ollama": "ollama",
            "兼容网关": "openai-compatible",
        }
        return mapping.get(provider_label, "openai-compatible")

    def _status_tone_for_batch(self, status_text: str) -> BadgeTone:
        """批次状态色调。"""

        mapping: dict[str, BadgeTone] = {
            "运行中": "brand",
            "待复核": "warning",
            "已完成": "success",
            "排队中": "info",
        }
        return mapping.get(status_text, "info")

    def _node_status_tone(self, node: WorkflowNodeData) -> BadgeTone:
        """返回节点状态色调。"""

        return node.status_tone

    def _build_component_inventory(self) -> tuple[FactoryComponentItem, ...]:
        """组件库演示数据。"""

        return (
            FactoryComponentItem("输入素材", "⌕", "支持文本、商品链接、短视频素材、达人投稿素材等多源输入。", "基础"),
            FactoryComponentItem("素材分析", "◫", "提取商品卖点、镜头类型、情绪关键词与场景标签，为后续生成节点提供结构化摘要。", "推荐"),
            FactoryComponentItem("文案生成", "✦", "根据卖点摘要生成标题、口播、贴片文案与评论区引导话术。", "热门"),
            FactoryComponentItem("标题优化", "◎", "强化前 3 秒点击诱因，自动规避敏感承诺与违禁词。", "高转化"),
            FactoryComponentItem("封面建议", "▣", "输出封面一句话、画面构图与主视觉关键词，适配短视频与新品预热。", "创意"),
            FactoryComponentItem("发布排程", "▶", "按平台热度窗口、素材成熟度与活动节奏生成分发计划。", "运营"),
        )

    def _build_template_data(self) -> tuple[WorkflowTemplateData, ...]:
        """模板演示数据。"""

        return (
            WorkflowTemplateData(
                name="爆款短视频流水线",
                scene="短视频量产",
                cadence="先分析再生成，保留复核锚点",
                output_count="24 条 / 批",
                conversion_hint="适合日常冲量与短视频引流双场景",
                description="面向 TikTok Shop 的高频内容生产模板，自动串联素材分析、口播生成、标题优化与封面建议。",
                tags=("高转化", "短视频引流", "自动复核"),
            ),
            WorkflowTemplateData(
                name="新品预热快反模板",
                scene="活动冲刺",
                cadence="标题先行，口播精简，发布时间集中晚高峰",
                output_count="12 条 / 批",
                conversion_hint="适合秒杀、节日活动与店播预热",
                description="强调封面一句话与标题冲击力，适合短时间内快速铺量抢占流量窗口。",
                tags=("活动预热", "快反", "标题优先"),
            ),
            WorkflowTemplateData(
                name="达人合作共创链路",
                scene="达人共创",
                cadence="保留达人语气标签，强调个人体验感",
                output_count="8 条 / 批",
                conversion_hint="适合达人口播、测评种草与真实体验分享",
                description="在品牌口径约束下兼容达人个人表达，帮助内容更自然地承接评论和下单。",
                tags=("达人口播", "真实体验", "个性化"),
            ),
        )

    def _build_project_data(self) -> ProjectSnapshot:
        """项目数据。"""

        return ProjectSnapshot(
            name="春季通勤杯爆款计划",
            status="运行中",
            owner="内容中台 · 增长组",
            progress="72%",
            next_step="批次完成后进入人工复核与发布编排",
        )

    def _build_workflow_nodes(self) -> tuple[WorkflowNodeData, ...]:
        """主链节点数据。"""

        return (
            WorkflowNodeData(
                key="asset_ingest",
                stage="阶段 1 / 输入",
                title="输入素材",
                description="接收商品主图、达人种草片段、短视频素材与商品详情页结构化信息。",
                provider_label="兼容网关",
                model_label="glm-4.5-air",
                role_label="通用助手",
                prompt_summary="统一整理输入结构并补全缺失字段",
                input_hint="商品链接、主图、商品卖点、用户评论",
                output_hint="规范化素材包与字段索引",
                estimated_duration="1 分 20 秒",
                status_text="已完成",
                status_tone="success",
                quality_score="98",
                tokens_text="322",
                tags=("结构化", "预处理", "多源输入"),
                accent=INFO,
            ),
            WorkflowNodeData(
                key="asset_analysis",
                stage="阶段 2 / 分析",
                title="素材分析",
                description="识别高频场景、镜头动线与用户评论中的购买触发点，形成卖点优先级。",
                provider_label="OpenAI",
                model_label="gpt-4o",
                role_label="数据分析师",
                prompt_summary="提炼素材中的可视化卖点和情绪关键词",
                input_hint="规范化素材包与用户评论摘要",
                output_hint="卖点树、情绪标签、视觉脚本提示",
                estimated_duration="2 分 10 秒",
                status_text="已完成",
                status_tone="success",
                quality_score="95",
                tokens_text="684",
                tags=("卖点提炼", "评论洞察", "镜头分析"),
                accent=SUCCESS,
            ),
            WorkflowNodeData(
                key="copy_generation",
                stage="阶段 3 / 生成",
                title="文案生成",
                description="根据卖点树生成短视频口播、评论引导和卖货承接话术，兼顾品牌语气与成交驱动。",
                provider_label="OpenAI",
                model_label="gpt-4o",
                role_label="文案专家",
                prompt_summary="输出口语化、高转化、可直接上播的脚本草案",
                input_hint="卖点树、视觉脚本提示、品牌语气约束",
                output_hint="标题草案、口播脚本、评论区引导文案",
                estimated_duration="3 分 40 秒",
                status_text="运行中",
                status_tone="brand",
                quality_score="93",
                tokens_text="1.6K",
                tags=("口播脚本", "转化导向", "品牌语气"),
                accent=ACCENT,
                highlighted=True,
            ),
            WorkflowNodeData(
                key="title_polish",
                stage="阶段 4 / 优化",
                title="标题优化",
                description="压缩信息密度，强化场景代入和点击欲望，确保标题能在前 12 个字内传递核心利益点。",
                provider_label="Anthropic",
                model_label="claude-3-7-sonnet",
                role_label="SEO优化师",
                prompt_summary="压缩标题长度并提升点击诱因",
                input_hint="标题草案、转化关键词、平台热词",
                output_hint="主标题、备选标题、违禁词替换建议",
                estimated_duration="1 分 50 秒",
                status_text="待运行",
                status_tone="info",
                quality_score="91",
                tokens_text="846",
                tags=("热词注入", "长度控制", "风险规避"),
                accent=WARNING,
            ),
            WorkflowNodeData(
                key="cover_hook",
                stage="阶段 5 / 创意",
                title="封面建议",
                description="输出封面一句话、构图重点和主视觉关键词，保证封面与标题语义一致。",
                provider_label="Ollama",
                model_label="qwen2.5:14b",
                role_label="脚本创作者",
                prompt_summary="生成封面主文案并同步视觉锚点",
                input_hint="主标题、卖点树、视觉脚本提示",
                output_hint="封面一句话、构图提示、主视觉词",
                estimated_duration="1 分 10 秒",
                status_text="待运行",
                status_tone="info",
                quality_score="89",
                tokens_text="512",
                tags=("封面一句话", "主视觉", "品牌统一"),
                accent=INFO,
            ),
            WorkflowNodeData(
                key="publish_schedule",
                stage="阶段 6 / 分发",
                title="发布排程",
                description="结合活动节奏、热视频窗口和人工复核结果，生成内容投放顺序与发布时间表。",
                provider_label="兼容网关",
                model_label="deepseek-chat",
                role_label="通用助手",
                prompt_summary="把可发布内容映射到最佳时段和渠道",
                input_hint="最终文案、封面建议、活动时间窗",
                output_hint="发布时间表、优先级、复核提醒",
                estimated_duration="2 分 00 秒",
                status_text="待运行",
                status_tone="info",
                quality_score="94",
                tokens_text="438",
                tags=("自动排程", "活动节奏", "渠道映射"),
                accent=SUCCESS,
            ),
        )

    def _build_branch_nodes(self) -> tuple[WorkflowBranchData, ...]:
        """支线节点数据。"""

        return (
            WorkflowBranchData(
                title="字幕包装",
                detail="为口播脚本补充高亮关键词、节奏点与字幕层级，便于后续剪辑直接套版。",
                owner="脚本创作者",
                tone=ACCENT,
            ),
            WorkflowBranchData(
                title="素材归档",
                detail="把最终稿、封面建议、发布时间表与卖点摘要归档到项目知识库，支持后续复盘。",
                owner="通用助手",
                tone=SUCCESS,
            ),
        )

    def _build_history_items(self) -> tuple[WorkflowHistoryData, ...]:
        """时间线数据。"""

        return (
            WorkflowHistoryData("2026-03-09 09:22", "发布排程已生成草案", "晚高峰 19:30、20:40、22:10 三个窗口优先发布。", "info"),
            WorkflowHistoryData("2026-03-09 09:21", "封面建议已进入待运行", "已读取标题优化的热词策略，等待主标题最终确认。", "warning"),
            WorkflowHistoryData("2026-03-09 09:20", "文案生成完成首轮草案", "输出 3 版标题、2 版口播脚本和 1 组评论区引导。", "success"),
            WorkflowHistoryData("2026-03-09 09:18", "素材分析生成卖点树", "“防漏锁扣”“通勤露营双场景”“高颜值保温”成为主卖点。", "success"),
            WorkflowHistoryData("2026-03-09 09:15", "项目加载完成", "已载入春季通勤杯爆款计划工作流与 24 条待处理任务。", "info"),
        )

    def _build_batch_runs(self) -> tuple[BatchRunData, ...]:
        """批次数据。"""

        return (
            BatchRunData(
                batch_id="batch_260309_01",
                name="春季通勤杯 · 日常冲量批次",
                progress=72,
                status="运行中",
                throughput="4 条 / 分钟",
                eta="7 分钟",
                note="已完成素材分析和文案生成，正在等待标题优化与封面建议并发执行。",
            ),
            BatchRunData(
                batch_id="batch_260309_02",
                name="露营场景分支 · 达人合作批次",
                progress=46,
                status="待复核",
                throughput="2 条 / 分钟",
                eta="11 分钟",
                note="达人口语化标签已生效，需要人工确认价格口径与评论区引导强度。",
            ),
            BatchRunData(
                batch_id="batch_260309_03",
                name="新品预热快反批次",
                progress=100,
                status="已完成",
                throughput="6 条 / 分钟",
                eta="已结束",
                note="已交付 12 条标题与封面组合，准备在晚高峰前投递到发布排程。",
            ),
        )

    def _build_queue_metrics(self) -> tuple[QueueMetricData, ...]:
        """批次指标数据。"""

        return (
            QueueMetricData("队列总量", "3 批", "◫", "brand"),
            QueueMetricData("运行中", "1 批", "▶", "info"),
            QueueMetricData("待复核", "1 批", "◎", "warning"),
            QueueMetricData("已完成", "1 批", "✓", "success"),
        )

    def _apply_page_styles(self) -> None:
        """页面局部样式。"""

        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#aiContentFactoryPage {{
                background-color: {SURFACE_LIGHT};
            }}
            QWidget#factoryWorkspace,
            QWidget#factorySidebarScroll,
            QWidget#factoryConfigScroll {{
                background: transparent;
            }}
            QFrame#factoryCanvasStage,
            QFrame#factoryOutputStage {{
                background-color: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: 22px;
            }}
            QFrame#factoryCanvasToolbar,
            QFrame#factoryCanvasFooter {{
                background-color: {SURFACE_CARD};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
            QFrame#factoryCanvasGrid {{
                background-color: {SURFACE_ALT};
                border: 1px dashed {BORDER_STRONG};
                border-radius: 24px;
            }}
            QFrame#factoryBatchList {{
                background-color: {SURFACE_ALT};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
            """,
        )

    def on_activated(self) -> None:
        """页面激活时刷新关键展示。"""

        self._sync_selected_node_controls()
        self._populate_output_preview()


__all__ = ["AIContentFactoryPage"]

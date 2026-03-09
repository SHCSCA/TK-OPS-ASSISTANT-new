# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnusedImport=false, reportUninitializedInstanceVariable=false, reportImplicitOverride=false, reportPrivateUsage=false

from __future__ import annotations

"""可视化实验室页面。"""

from dataclasses import dataclass
from typing import Final

from ....core.qt import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.theme.tokens import STATIC_TOKENS, get_token_value
from ....core.types import RouteId, ThemeMode
from ...components import ChartWidget, ContentSection, PageContainer, SplitPanel, TabBar, ThemedComboBox, ThemedLineEdit, ToggleSwitch
from ..base_page import BasePage


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 风格方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """安全连接信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _theme_mode() -> ThemeMode:
    """读取当前主题模式。"""

    app = QApplication.instance() if hasattr(QApplication, "instance") else None
    property_reader = getattr(app, "property", None)
    if callable(property_reader):
        for key in ("theme.mode", "theme_mode", "themeMode"):
            value = property_reader(key)
            if value == ThemeMode.DARK or str(value).lower() == ThemeMode.DARK.value:
                return ThemeMode.DARK
    return ThemeMode.LIGHT


def _token(name: str) -> str:
    """解析主题 token。"""

    return get_token_value(name, _theme_mode())


def _px(name: str) -> int:
    """将像素 token 转为整数。"""

    return int(STATIC_TOKENS[name].replace("px", ""))


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class _Palette:
    """页面局部色板。"""

    surface: str
    surface_alt: str
    text: str
    text_muted: str
    text_inverse: str
    border: str
    primary: str
    success: str
    accent_pink: str
    accent_purple: str
    accent_blue: str
    accent_gold: str


def _palette() -> _Palette:
    """生成当前页面使用的主题色板。"""

    return _Palette(
        surface=_token("surface.secondary"),
        surface_alt=_token("surface.sunken"),
        text=_token("text.primary"),
        text_muted=_token("text.secondary"),
        text_inverse=_token("text.inverse"),
        border=_token("border.default"),
        primary=_token("brand.primary"),
        success=_token("status.success"),
        accent_pink=STATIC_TOKENS["chart.series[1]"],
        accent_purple=STATIC_TOKENS["chart.series[2]"],
        accent_blue=STATIC_TOKENS["chart.series[3]"],
        accent_gold=STATIC_TOKENS["chart.series[4]"],
    )


@dataclass(frozen=True)
class _MetricSpec:
    """Y 轴指标映射配置。"""

    multiplier: float
    offset: float
    unit: str
    precision: int


@dataclass(frozen=True)
class _ResolvedSeries:
    """预览用序列数据。"""

    labels: tuple[str, ...]
    values: tuple[float, ...]
    unit: str


@dataclass(frozen=True)
class _VisualLabSource:
    """模拟数据源定义。"""

    name: str
    sync_hint: str
    description: str
    default_title: str
    x_labels: dict[str, tuple[str, ...]]
    x_values: dict[str, tuple[float, ...]]
    pie_labels: dict[str, tuple[str, ...]]
    pie_values: dict[str, tuple[float, ...]]
    metrics: dict[str, _MetricSpec]
    color_modifiers: dict[str, float]

    @property
    def x_options(self) -> tuple[str, ...]:
        """可用的 X 轴字段。"""

        return tuple(self.x_labels.keys())

    @property
    def y_options(self) -> tuple[str, ...]:
        """可用的 Y 轴字段。"""

        return tuple(self.metrics.keys())

    @property
    def color_options(self) -> tuple[str, ...]:
        """可用的颜色字段。"""

        return tuple(self.color_modifiers.keys())

    def resolve_series(self, chart_type: str, x_axis: str, y_axis: str, color_field: str) -> _ResolvedSeries:
        """根据当前配置生成预览序列。"""

        resolved_y = y_axis if y_axis in self.metrics else self.y_options[0]
        spec = self.metrics[resolved_y]
        modifier = self.color_modifiers.get(color_field, 1.0)

        if chart_type == "pie":
            labels = self.pie_labels.get(color_field, next(iter(self.pie_labels.values())))
            base_values = self.pie_values.get(color_field, next(iter(self.pie_values.values())))
            values = tuple(round(spec.offset + value * spec.multiplier * modifier, spec.precision) for value in base_values)
            return _ResolvedSeries(labels=labels, values=values, unit=spec.unit)

        labels = self.x_labels.get(x_axis, next(iter(self.x_labels.values())))
        base_values = self.x_values.get(x_axis, next(iter(self.x_values.values())))
        scatter_factor = 1.0 if chart_type != "scatter" else 0.92
        values = tuple(
            round(spec.offset + value * spec.multiplier * modifier * (scatter_factor + 0.04 * ((index % 3) + 1)), spec.precision)
            for index, value in enumerate(base_values)
        )
        return _ResolvedSeries(labels=labels, values=values, unit=spec.unit)


class _PreviewChartWidget(ChartWidget):
    """为实验室页面补充可更新标题的图表预览部件。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(chart_type="line", title="实时活跃指标走势", parent=parent)

    def set_visual_title(self, title: str) -> None:
        """更新图表标题。"""

        self._title = title
        _call(self, "update")

    def set_visual_chart_type(self, chart_type: str) -> None:
        """设置预览图表类型。"""

        self.set_chart_type("pie" if chart_type == "pie" else "bar" if chart_type == "bar" else "line")


LAYOUT_SIDEBAR_WIDTH: Final[int] = _px("layout.sidebar_width.canonical")
CARD_PADDING: Final[int] = _px("layout.card_padding")
SPACING_SM: Final[int] = _px("spacing.sm")
SPACING_MD: Final[int] = _px("spacing.md")
SPACING_LG: Final[int] = _px("spacing.lg")
SPACING_XL: Final[int] = _px("spacing.xl")
SPACING_2XL: Final[int] = _px("spacing.2xl")
RADIUS_MD: Final[int] = _px("radius.md")
RADIUS_LG: Final[int] = _px("radius.lg")
BUTTON_HEIGHT: Final[int] = _px("button.height.md")
FONT_XS: Final[str] = STATIC_TOKENS["font.size.xs"]
FONT_SM: Final[str] = STATIC_TOKENS["font.size.sm"]
FONT_MD: Final[str] = STATIC_TOKENS["font.size.md"]
FONT_LG: Final[str] = STATIC_TOKENS["font.size.lg"]
FONT_XL: Final[str] = STATIC_TOKENS["font.size.xl"]
FONT_XXL: Final[str] = STATIC_TOKENS["font.size.xxl"]
FONT_DISPLAY: Final[str] = STATIC_TOKENS["font.size.display"]
WEIGHT_MEDIUM: Final[str] = STATIC_TOKENS["font.weight.medium"]
WEIGHT_SEMIBOLD: Final[str] = STATIC_TOKENS["font.weight.semibold"]
WEIGHT_BOLD: Final[str] = STATIC_TOKENS["font.weight.bold"]

CHART_TYPE_LABELS: Final[dict[str, str]] = {
    "line": "折线图",
    "bar": "柱状图",
    "pie": "饼图",
    "scatter": "散点图",
}

CHART_TYPE_ICONS: Final[dict[str, str]] = {
    "line": "↗",
    "bar": "▇",
    "pie": "◔",
    "scatter": "✦",
}


class VisualLabPage(BasePage):
    """匹配设计稿的可视化实验室页面。"""

    default_route_id: RouteId = RouteId("visual_lab")
    default_display_name: str = "可视化实验室"
    default_icon_name: str = "query_stats"

    def setup_ui(self) -> None:
        """构建页面，不调用基类默认占位布局。"""

        self._page_palette = _palette()
        self._sources = self._build_mock_sources()
        self._selected_chart_type = "line"
        self._controls_ready = False

        _call(self, "setObjectName", "visualLabPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._apply_styles()

        self._container = PageContainer()
        self.layout.addWidget(self._container)

        self._container.content_layout.addWidget(self._build_toolbar())
        self._container.content_layout.addWidget(self._build_workspace(), 1)
        self._container.content_layout.addWidget(self._build_bottom_tabs())

        self._populate_source_selector()
        self._refresh_chart_type_buttons()
        self._controls_ready = True
        self._handle_source_changed(self._source_selector.current_text())

    def _build_toolbar(self) -> QWidget:
        """顶部标题与项目条。"""

        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "visualLabToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(CARD_PADDING, SPACING_XL, CARD_PADDING, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        title_wrap = QWidget(toolbar)
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_SM)

        eyebrow = QLabel("VISUAL LAB · 数据画布", title_wrap)
        _call(eyebrow, "setObjectName", "visualLabEyebrow")
        title = QLabel("可视化实验室", title_wrap)
        _call(title, "setObjectName", "visualLabMainTitle")
        subtitle = QLabel("围绕数据源、字段映射与图表属性快速完成实验预览。", title_wrap)
        _call(subtitle, "setObjectName", "visualLabMutedText")
        _call(subtitle, "setWordWrap", True)

        title_layout.addWidget(eyebrow)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self._project_chip = QLabel("项目：未命名实验室-01", toolbar)
        _call(self._project_chip, "setObjectName", "visualLabProjectChip")

        range_wrap = QWidget(toolbar)
        range_layout = QHBoxLayout(range_wrap)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.setSpacing(SPACING_SM)
        self._range_buttons = {}
        for index, label in enumerate(("1H", "1D", "1W", "1M")):
            button = QPushButton(label, range_wrap)
            _call(button, "setObjectName", "visualLabRangeButton")
            _call(button, "setCheckable", True)
            _call(button, "setChecked", index == 0)
            self._range_buttons[label] = button
            range_layout.addWidget(button)

        layout.addWidget(title_wrap, 1)
        layout.addWidget(self._project_chip)
        layout.addWidget(range_wrap)
        return toolbar

    def _build_workspace(self) -> QWidget:
        """三栏工作区。"""

        left_panel = self._build_left_panel()
        center_panel = self._build_center_panel()
        right_panel = self._build_right_panel()

        content_split = SplitPanel(
            split_ratio=(0.68, 0.32),
            minimum_sizes=(LAYOUT_SIDEBAR_WIDTH + LAYOUT_SIDEBAR_WIDTH, LAYOUT_SIDEBAR_WIDTH + SPACING_2XL),
        )
        content_split.set_widgets(center_panel, right_panel)

        root_split = SplitPanel(
            split_ratio=(0.24, 0.76),
            minimum_sizes=(LAYOUT_SIDEBAR_WIDTH, LAYOUT_SIDEBAR_WIDTH + LAYOUT_SIDEBAR_WIDTH),
        )
        root_split.set_widgets(left_panel, content_split)
        return root_split

    def _build_left_panel(self) -> QWidget:
        """左侧选择区。"""

        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        source_section = ContentSection("数据源选择")
        self._source_selector = ThemedComboBox(label="当前数据连接")
        self._source_hint = QLabel("", source_section)
        _call(self._source_hint, "setObjectName", "visualLabMutedText")
        _call(self._source_hint, "setWordWrap", True)
        source_section.add_widget(self._source_selector)
        source_section.add_widget(self._source_hint)

        type_section = ContentSection("图表类型")
        type_grid = QWidget(type_section)
        type_grid_layout = QVBoxLayout(type_grid)
        type_grid_layout.setContentsMargins(0, 0, 0, 0)
        type_grid_layout.setSpacing(SPACING_SM)
        self._chart_type_buttons = {}
        for row_types in (("line", "bar"), ("pie", "scatter")):
            row_wrap = QWidget(type_grid)
            row_layout = QHBoxLayout(row_wrap)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(SPACING_SM)
            for chart_type in row_types:
                button = QPushButton(f"{CHART_TYPE_ICONS[chart_type]}\n{CHART_TYPE_LABELS[chart_type]}", row_wrap)
                _call(button, "setObjectName", "visualLabChartTypeButton")
                _call(button, "setCheckable", True)
                _call(button, "setMinimumHeight", BUTTON_HEIGHT + BUTTON_HEIGHT)
                _connect(getattr(button, "clicked", None), lambda _checked=False, key=chart_type: self._handle_chart_type_changed(key))
                self._chart_type_buttons[chart_type] = button
                row_layout.addWidget(button)
            type_grid_layout.addWidget(row_wrap)
        type_section.add_widget(type_grid)

        mapping_section = ContentSection("字段映射")
        self._x_axis_selector = ThemedComboBox(label="X 轴")
        self._y_axis_selector = ThemedComboBox(label="Y 轴")
        self._color_selector = ThemedComboBox(label="颜色")
        mapping_section.add_widget(self._x_axis_selector)
        mapping_section.add_widget(self._y_axis_selector)
        mapping_section.add_widget(self._color_selector)

        tip_card = QFrame(panel)
        _call(tip_card, "setObjectName", "visualLabTipCard")
        tip_layout = QVBoxLayout(tip_card)
        tip_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        tip_layout.setSpacing(SPACING_SM)
        tip_title = QLabel("提示", tip_card)
        _call(tip_title, "setObjectName", "visualLabSectionTitle")
        tip_text = QLabel("切换字段或图表类型后，中心预览区与底部标签页会实时联动。", tip_card)
        _call(tip_text, "setObjectName", "visualLabMutedText")
        _call(tip_text, "setWordWrap", True)
        tip_layout.addWidget(tip_title)
        tip_layout.addWidget(tip_text)

        layout.addWidget(source_section)
        layout.addWidget(type_section)
        layout.addWidget(mapping_section)
        layout.addStretch(1)
        layout.addWidget(tip_card)

        _connect(getattr(self._source_selector.combo_box, "currentTextChanged", None), self._handle_source_changed)
        _connect(getattr(self._x_axis_selector.combo_box, "currentTextChanged", None), self._refresh_preview)
        _connect(getattr(self._y_axis_selector.combo_box, "currentTextChanged", None), self._refresh_preview)
        _connect(getattr(self._color_selector.combo_box, "currentTextChanged", None), self._refresh_preview)
        return panel

    def _build_center_panel(self) -> QWidget:
        """中心预览区。"""

        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        header = QFrame(panel)
        _call(header, "setObjectName", "visualLabPreviewHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(CARD_PADDING, SPACING_XL, CARD_PADDING, SPACING_XL)
        header_layout.setSpacing(SPACING_XL)

        title_wrap = QWidget(header)
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_SM)
        preview_title = QLabel("实时数据预览", title_wrap)
        _call(preview_title, "setObjectName", "visualLabSectionTitle")
        self._preview_subtitle = QLabel("每 5 秒自动刷新一次模拟数据。", title_wrap)
        _call(self._preview_subtitle, "setObjectName", "visualLabMutedText")
        title_layout.addWidget(preview_title)
        title_layout.addWidget(self._preview_subtitle)

        self._preview_status = QLabel("数据源已连接", header)
        _call(self._preview_status, "setObjectName", "visualLabProjectChip")

        header_layout.addWidget(title_wrap, 1)
        header_layout.addWidget(self._preview_status)

        preview_card = QFrame(panel)
        _call(preview_card, "setObjectName", "visualLabPreviewCard")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        preview_layout.setSpacing(SPACING_XL)

        metric_wrap = QWidget(preview_card)
        metric_layout = QHBoxLayout(metric_wrap)
        metric_layout.setContentsMargins(0, 0, 0, 0)
        metric_layout.setSpacing(SPACING_XL)

        metric_text = QWidget(metric_wrap)
        metric_text_layout = QVBoxLayout(metric_text)
        metric_text_layout.setContentsMargins(0, 0, 0, 0)
        metric_text_layout.setSpacing(SPACING_SM)
        metric_eyebrow = QLabel("活跃指标", metric_text)
        _call(metric_eyebrow, "setObjectName", "visualLabMetricEyebrow")
        self._headline_value = QLabel("--", metric_text)
        _call(self._headline_value, "setObjectName", "visualLabHeadlineValue")
        self._headline_delta = QLabel("--", metric_text)
        _call(self._headline_delta, "setObjectName", "visualLabHeadlineDelta")
        metric_text_layout.addWidget(metric_eyebrow)
        metric_text_layout.addWidget(self._headline_value)
        metric_text_layout.addWidget(self._headline_delta)

        metric_note = QLabel("实验成员：分析师 / 运营 / 视觉工程", metric_wrap)
        _call(metric_note, "setObjectName", "visualLabMutedText")
        metric_layout.addWidget(metric_text, 1)
        metric_layout.addWidget(metric_note)

        self._legend_row = QWidget(preview_card)
        legend_layout = QHBoxLayout(self._legend_row)
        legend_layout.setContentsMargins(0, 0, 0, 0)
        legend_layout.setSpacing(SPACING_SM)
        self._legend_labels = []
        for _ in range(3):
            chip = QLabel("", self._legend_row)
            _call(chip, "setObjectName", "visualLabLegendChip")
            self._legend_labels.append(chip)
            legend_layout.addWidget(chip)
        legend_layout.addStretch(1)

        self._chart_widget = _PreviewChartWidget(preview_card)
        _call(self._chart_widget, "setMinimumHeight", BUTTON_HEIGHT * 8)

        self._chart_footer = QLabel("", preview_card)
        _call(self._chart_footer, "setObjectName", "visualLabMutedText")

        preview_layout.addWidget(metric_wrap)
        preview_layout.addWidget(self._legend_row)
        preview_layout.addWidget(self._chart_widget, 1)
        preview_layout.addWidget(self._chart_footer)

        stats_row = QWidget(panel)
        stats_layout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(SPACING_XL)
        self._stat_titles = []
        self._stat_values = []
        for _ in range(3):
            card = QFrame(stats_row)
            _call(card, "setObjectName", "visualLabStatCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
            card_layout.setSpacing(SPACING_SM)
            title_label = QLabel("", card)
            _call(title_label, "setObjectName", "visualLabMutedText")
            value_label = QLabel("--", card)
            _call(value_label, "setObjectName", "visualLabValueText")
            self._stat_titles.append(title_label)
            self._stat_values.append(value_label)
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            stats_layout.addWidget(card)

        layout.addWidget(header)
        layout.addWidget(preview_card, 1)
        layout.addWidget(stats_row)
        return panel

    def _build_right_panel(self) -> QWidget:
        """右侧属性区。"""

        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        property_section = ContentSection("图表属性")
        self._title_input = ThemedLineEdit(label="图表标题", placeholder="输入图表标题", helper_text="留空时会使用数据源推荐标题。")
        property_section.add_widget(self._title_input)

        self._legend_toggle = ToggleSwitch(checked=True)
        self._grid_toggle = ToggleSwitch(checked=True)
        property_section.add_widget(self._build_toggle_row("显示图例", self._legend_toggle))
        property_section.add_widget(self._build_toggle_row("显示网格", self._grid_toggle))

        summary_section = ContentSection("配置摘要")
        self._summary_label = QLabel("", summary_section)
        _call(self._summary_label, "setObjectName", "visualLabMonoText")
        _call(self._summary_label, "setWordWrap", True)
        summary_section.add_widget(self._summary_label)

        layout.addWidget(property_section)
        layout.addWidget(summary_section)
        layout.addStretch(1)

        _connect(getattr(self._title_input.line_edit, "textChanged", None), self._refresh_preview)
        _connect(self._legend_toggle.toggled, self._refresh_preview)
        _connect(self._grid_toggle.toggled, self._refresh_preview)
        return panel

    def _build_toggle_row(self, text: str, toggle: ToggleSwitch) -> QWidget:
        """构建右侧开关行。"""

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        text_wrap = QWidget(row)
        text_layout = QVBoxLayout(text_wrap)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_SM)
        title = QLabel(text, text_wrap)
        _call(title, "setObjectName", "visualLabSectionTitle")
        hint = QLabel("切换后会立即同步中心预览区。", text_wrap)
        _call(hint, "setObjectName", "visualLabMutedText")
        text_layout.addWidget(title)
        text_layout.addWidget(hint)

        layout.addWidget(text_wrap, 1)
        layout.addWidget(toggle)
        return row

    def _build_bottom_tabs(self) -> TabBar:
        """底部标签页。"""

        self._tab_bar = TabBar(self)
        _call(self._tab_bar, "setObjectName", "visualLabBottomTabs")

        self._data_preview_text = self._build_tab_text()
        self._config_text = self._build_tab_text()
        self._export_text = self._build_tab_text()

        self._tab_bar.add_tab("数据预览", self._build_tab_card("当前样本数据", self._data_preview_text))
        self._tab_bar.add_tab("图表配置", self._build_tab_card("当前配置快照", self._config_text))
        self._tab_bar.add_tab("导出", self._build_tab_card("导出建议", self._export_text))
        return self._tab_bar

    def _build_tab_text(self) -> QLabel:
        """构建标签页文本。"""

        label = QLabel("", self)
        _call(label, "setObjectName", "visualLabMonoText")
        _call(label, "setWordWrap", True)
        return label

    def _build_tab_card(self, title: str, body: QLabel) -> QWidget:
        """用分组卡片包裹标签内容。"""

        section = ContentSection(title)
        section.add_widget(body)
        return section

    def _populate_source_selector(self) -> None:
        """初始化数据源选项。"""

        self._set_combo_items(self._source_selector, tuple(self._sources.keys()))

    def _set_combo_items(self, combo: ThemedComboBox, items: tuple[str, ...], preferred: str | None = None) -> None:
        """统一写入下拉选项。"""

        widget = combo.combo_box
        _call(widget, "clear")
        add_items = getattr(widget, "addItems", None)
        if callable(add_items):
            add_items(list(items))
        else:
            for item in items:
                _call(widget, "addItem", item)
        if not items:
            return
        target = preferred if preferred in items else items[0]
        _call(widget, "setCurrentText", target)

    def _handle_source_changed(self, source_name: str) -> None:
        """切换数据源后刷新字段。"""

        source = self._sources.get(source_name)
        if source is None:
            return

        self._controls_ready = False
        self._set_combo_items(self._x_axis_selector, source.x_options, self._x_axis_selector.current_text())
        self._set_combo_items(self._y_axis_selector, source.y_options, self._y_axis_selector.current_text())
        self._set_combo_items(self._color_selector, source.color_options, self._color_selector.current_text())
        self._source_hint.setText(f"{source.sync_hint}\n{source.description}")
        self._preview_status.setText(source.sync_hint)
        if not self._title_input.text().strip():
            self._title_input.setText(source.default_title)
        self._controls_ready = True
        self._refresh_preview()

    def _handle_chart_type_changed(self, chart_type: str) -> None:
        """切换图表类型按钮状态。"""

        self._selected_chart_type = chart_type
        self._refresh_chart_type_buttons()
        self._refresh_preview()

    def _refresh_chart_type_buttons(self) -> None:
        """同步图表类型按钮视觉状态。"""

        colors = self._page_palette
        for chart_type, button in self._chart_type_buttons.items():
            is_active = chart_type == self._selected_chart_type
            background = colors.primary if is_active else colors.surface_alt
            foreground = colors.text_inverse if is_active else colors.text
            border = colors.primary if is_active else colors.border
            _call(button, "setChecked", is_active)
            _call(
                button,
                "setStyleSheet",
                f"""
                QPushButton#visualLabChartTypeButton {{
                    background-color: {background};
                    color: {foreground};
                    border: 1px solid {border};
                    border-radius: {RADIUS_LG}px;
                    padding: {SPACING_LG}px;
                    font-size: {FONT_SM};
                    font-weight: {WEIGHT_BOLD if is_active else WEIGHT_MEDIUM};
                    text-align: center;
                }}
                QPushButton#visualLabChartTypeButton:hover {{
                    border-color: {colors.primary};
                    background-color: {_rgba(colors.primary[1:] if colors.primary.startswith('#') else '00F2EA', 0.12) if not is_active else colors.primary};
                }}
                """,
            )

    def _refresh_preview(self, *_args: object) -> None:
        """根据当前选择刷新预览、摘要与标签页。"""

        if not self._controls_ready:
            return

        source = self._sources.get(self._source_selector.current_text())
        if source is None:
            return

        x_axis = self._x_axis_selector.current_text() or source.x_options[0]
        y_axis = self._y_axis_selector.current_text() or source.y_options[0]
        color_field = self._color_selector.current_text() or source.color_options[0]
        chart_title = self._title_input.text().strip() or source.default_title
        series = source.resolve_series(self._selected_chart_type, x_axis, y_axis, color_field)

        self._chart_widget.set_visual_title(chart_title)
        self._chart_widget.set_visual_chart_type(self._selected_chart_type)
        self._chart_widget.set_unit(series.unit)
        self._chart_widget.set_data(series.values, series.labels)

        self._preview_subtitle.setText(f"数据源：{source.name} · 图表：{CHART_TYPE_LABELS[self._selected_chart_type]}")
        self._chart_footer.setText(
            f"X轴：{x_axis}  ·  Y轴：{y_axis}  ·  颜色：{color_field}  ·  图例：{'开' if self._legend_toggle.isChecked() else '关'}  ·  网格：{'开' if self._grid_toggle.isChecked() else '关'}"
        )

        self._update_headline(source, series)
        self._update_legend(y_axis, color_field, series)
        self._update_stats(series)
        self._update_summary(source, chart_title, x_axis, y_axis, color_field, series)
        self._update_tabs(source, chart_title, x_axis, y_axis, color_field, series)

    def _update_headline(self, source: _VisualLabSource, series: _ResolvedSeries) -> None:
        """更新主 KPI 头部。"""

        values = list(series.values)
        latest = values[-1] if values else 0.0
        previous = values[-2] if len(values) > 1 else latest
        delta = 0.0 if previous == 0 else ((latest - previous) / previous) * 100.0
        trend = "↑" if delta >= 0 else "↓"
        self._headline_value.setText(self._format_value(latest, series.unit))
        self._headline_delta.setText(f"{trend} {abs(delta):.1f}% · {source.sync_hint}")

    def _update_legend(self, y_axis: str, color_field: str, series: _ResolvedSeries) -> None:
        """更新预览图例信息。"""

        texts = [
            f"指标：{y_axis}",
            f"颜色映射：{color_field}",
            f"范围：{series.labels[0]} → {series.labels[-1]}",
        ]
        for label, text in zip(self._legend_labels, texts):
            label.setText(text)
        _call(self._legend_row, "setVisible", self._legend_toggle.isChecked())

    def _update_stats(self, series: _ResolvedSeries) -> None:
        """更新底部统计卡。"""

        values = list(series.values)
        if not values:
            return
        if self._selected_chart_type == "pie":
            titles = ("总量", "最大分组", "分组数")
            stats = (
                self._format_value(sum(values), series.unit),
                f"{max(values):.1f}{series.unit}",
                f"{len(values)} 组",
            )
        else:
            titles = ("平均值", "峰值", "收官值")
            stats = (
                f"{sum(values) / len(values):.1f}{series.unit}",
                f"{max(values):.1f}{series.unit}",
                f"{values[-1]:.1f}{series.unit}",
            )
        for title_label, value_label, title, value in zip(self._stat_titles, self._stat_values, titles, stats):
            title_label.setText(title)
            value_label.setText(value)

    def _update_summary(
        self,
        source: _VisualLabSource,
        chart_title: str,
        x_axis: str,
        y_axis: str,
        color_field: str,
        series: _ResolvedSeries,
    ) -> None:
        """更新右侧摘要。"""

        self._summary_label.setText(
            "\n".join(
                [
                    f"标题：{chart_title}",
                    f"数据源：{source.name}",
                    f"图表类型：{CHART_TYPE_LABELS[self._selected_chart_type]}",
                    f"字段映射：X={x_axis} / Y={y_axis} / 颜色={color_field}",
                    f"视觉属性：图例={'开启' if self._legend_toggle.isChecked() else '关闭'}，网格={'开启' if self._grid_toggle.isChecked() else '关闭'}",
                    f"样本区间：{series.labels[0]} → {series.labels[-1]}",
                ]
            )
        )

    def _update_tabs(
        self,
        source: _VisualLabSource,
        chart_title: str,
        x_axis: str,
        y_axis: str,
        color_field: str,
        series: _ResolvedSeries,
    ) -> None:
        """更新底部标签页内容。"""

        preview_rows = [f"{label:<8} | {value}" for label, value in zip(series.labels[:6], series.values[:6])]
        self._data_preview_text.setText(
            "\n".join(
                [
                    f"数据源：{source.name}",
                    f"标题：{chart_title}",
                    f"字段：{x_axis} / {y_axis}",
                    "-" * 28,
                    *preview_rows,
                ]
            )
        )
        self._config_text.setText(
            "\n".join(
                [
                    f"图表类型：{CHART_TYPE_LABELS[self._selected_chart_type]}",
                    f"X轴字段：{x_axis}",
                    f"Y轴字段：{y_axis}",
                    f"颜色字段：{color_field}",
                    f"图例：{'开启' if self._legend_toggle.isChecked() else '关闭'}",
                    f"网格：{'开启' if self._grid_toggle.isChecked() else '关闭'}",
                    f"单位：{series.unit or '无'}",
                ]
            )
        )
        export_name = chart_title.replace(" ", "_") or "visual_lab_export"
        export_format = "PNG / SVG" if self._selected_chart_type in {"line", "bar", "scatter"} else "PNG / PDF"
        self._export_text.setText(
            "\n".join(
                [
                    f"建议文件名：{export_name}",
                    f"推荐格式：{export_format}",
                    f"推荐附带数据表：{'是' if self._selected_chart_type != 'pie' else '可选'}",
                    f"导出说明：保留{'图例' if self._legend_toggle.isChecked() else '主图'}，网格{'显示' if self._grid_toggle.isChecked() else '隐藏'}。",
                ]
            )
        )

    def _format_value(self, value: float, unit: str) -> str:
        """格式化预览头部数值。"""

        if unit == "%":
            return f"{value:.2f}{unit}"
        return f"{value:,.1f}{unit}"

    def _build_mock_sources(self) -> dict[str, _VisualLabSource]:
        """构建页面使用的模拟数据源。"""

        return {
            "实时生产库": _VisualLabSource(
                name="实时生产库",
                sync_hint="PostgreSQL · 2 分钟前同步",
                description="适合验证日级走势、渠道转化与品类结构的实时订单视图。",
                default_title="实时活跃指标走势",
                x_labels={
                    "时间周期": ("周一", "周二", "周三", "周四", "周五", "周六", "周日"),
                    "渠道": ("短视频", "短视频", "商城", "搜索"),
                    "商品品类": ("美妆", "个护", "服饰", "家居", "食品"),
                },
                x_values={
                    "时间周期": (34, 41, 46, 43, 58, 63, 60),
                    "渠道": (62, 48, 33, 29),
                    "商品品类": (55, 42, 36, 31, 27),
                },
                pie_labels={
                    "渠道": ("短视频", "短视频", "商城", "搜索"),
                    "地区": ("华东", "华南", "华北", "西南"),
                    "创意类型": ("口播", "剧情", "测评", "混剪"),
                },
                pie_values={
                    "渠道": (42, 31, 18, 15),
                    "地区": (36, 28, 22, 19),
                    "创意类型": (33, 29, 24, 17),
                },
                metrics={
                    "活跃用户": _MetricSpec(4.2, 22.0, "万", 1),
                    "成交额": _MetricSpec(12.6, 120.0, "万元", 1),
                    "转化率": _MetricSpec(0.11, 1.4, "%", 2),
                },
                color_modifiers={"渠道": 1.00, "地区": 0.92, "创意类型": 1.08},
            ),
            "广告投放监测": _VisualLabSource(
                name="广告投放监测",
                sync_hint="广告 API · 8 分钟前同步",
                description="用于观察创意、投放渠道与地区之间的流量分布与转化效率。",
                default_title="投放实验效果预览",
                x_labels={
                    "时间周期": ("09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"),
                    "渠道": ("信息流", "达人合作", "搜索广告", "再营销"),
                    "商品品类": ("新品", "爆品", "利润款", "引流款", "套装"),
                },
                x_values={
                    "时间周期": (22, 26, 31, 37, 42, 49, 56),
                    "渠道": (46, 39, 32, 28),
                    "商品品类": (51, 44, 35, 29, 26),
                },
                pie_labels={
                    "渠道": ("信息流", "达人合作", "搜索广告", "再营销"),
                    "地区": ("华东", "华南", "北方", "海外"),
                    "创意类型": ("高节奏", "场景化", "福利款", "短视频素材"),
                },
                pie_values={
                    "渠道": (39, 33, 24, 18),
                    "地区": (35, 27, 22, 16),
                    "创意类型": (31, 28, 23, 21),
                },
                metrics={
                    "活跃用户": _MetricSpec(3.8, 18.0, "万", 1),
                    "成交额": _MetricSpec(15.8, 96.0, "万元", 1),
                    "转化率": _MetricSpec(0.14, 1.1, "%", 2),
                },
                color_modifiers={"渠道": 1.00, "地区": 0.95, "创意类型": 1.10},
            ),
            "短视频转化快照": _VisualLabSource(
                name="短视频转化快照",
                sync_hint="短视频看板 · 刚刚同步",
                description="适合验证短视频时段表现、品类热点与地区订单占比。",
                default_title="短视频转化实验画布",
                x_labels={
                    "时间周期": ("开播", "预热", "上新", "讲解", "秒杀", "返场", "收官"),
                    "渠道": ("短视频主链路", "短视频引流", "粉丝群", "搜索回流"),
                    "商品品类": ("护肤", "彩妆", "母婴", "家清", "零食"),
                },
                x_values={
                    "时间周期": (19, 23, 31, 44, 53, 47, 38),
                    "渠道": (58, 34, 21, 18),
                    "商品品类": (49, 32, 28, 24, 19),
                },
                pie_labels={
                    "渠道": ("短视频主链路", "短视频引流", "粉丝群", "搜索回流"),
                    "地区": ("华东", "华南", "西南", "华中"),
                    "创意类型": ("讲解", "连麦", "抽奖", "返场"),
                },
                pie_values={
                    "渠道": (45, 26, 18, 13),
                    "地区": (34, 27, 21, 18),
                    "创意类型": (29, 25, 21, 17),
                },
                metrics={
                    "活跃用户": _MetricSpec(4.6, 15.0, "万", 1),
                    "成交额": _MetricSpec(16.2, 88.0, "万元", 1),
                    "转化率": _MetricSpec(0.16, 0.9, "%", 2),
                },
                color_modifiers={"渠道": 1.00, "地区": 0.97, "创意类型": 1.12},
            ),
        }

    def _apply_styles(self) -> None:
        """应用页面级样式。"""

        colors = self._page_palette
        primary_tint = _rgba(colors.primary.lstrip("#") if colors.primary.startswith("#") else "00F2EA", 0.10)
        primary_border = _rgba(colors.primary.lstrip("#") if colors.primary.startswith("#") else "00F2EA", 0.34)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#visualLabPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#visualLabToolbar,
            QFrame#visualLabPreviewHeader,
            QFrame#visualLabPreviewCard {{
                background-color: {colors.surface};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#visualLabStatCard,
            QFrame#visualLabTipCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#visualLabEyebrow {{
                color: {colors.text_muted};
                font-size: {FONT_XS};
                font-weight: {WEIGHT_BOLD};
                background: transparent;
            }}
            QLabel#visualLabMainTitle {{
                color: {colors.text};
                font-size: {FONT_XXL};
                font-weight: {WEIGHT_BOLD};
                background: transparent;
            }}
            QLabel#visualLabSectionTitle {{
                color: {colors.text};
                font-size: {FONT_MD};
                font-weight: {WEIGHT_SEMIBOLD};
                background: transparent;
            }}
            QLabel#visualLabMutedText {{
                color: {colors.text_muted};
                font-size: {FONT_SM};
                background: transparent;
            }}
            QLabel#visualLabProjectChip {{
                background-color: {primary_tint};
                color: {colors.primary};
                border: 1px solid {primary_border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_MD}px {SPACING_XL}px;
                font-size: {FONT_SM};
                font-weight: {WEIGHT_SEMIBOLD};
            }}
            QPushButton#visualLabRangeButton {{
                background-color: {colors.surface};
                color: {colors.text_muted};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {FONT_SM};
                font-weight: {WEIGHT_SEMIBOLD};
            }}
            QPushButton#visualLabRangeButton:hover {{
                border-color: {colors.primary};
                color: {colors.text};
                background-color: {primary_tint};
            }}
            QPushButton#visualLabRangeButton:checked {{
                background-color: {primary_tint};
                color: {colors.text};
                border-color: {colors.primary};
            }}
            QLabel#visualLabMetricEyebrow {{
                color: {colors.primary};
                font-size: {FONT_XS};
                font-weight: {WEIGHT_BOLD};
                background: transparent;
            }}
            QLabel#visualLabHeadlineValue {{
                color: {colors.text};
                font-size: {FONT_DISPLAY};
                font-weight: {WEIGHT_BOLD};
                background: transparent;
            }}
            QLabel#visualLabHeadlineDelta {{
                color: {colors.success};
                font-size: {FONT_SM};
                font-weight: {WEIGHT_SEMIBOLD};
                background: transparent;
            }}
            QLabel#visualLabLegendChip {{
                background-color: {colors.surface_alt};
                color: {colors.text};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                font-size: {FONT_SM};
                font-weight: {WEIGHT_MEDIUM};
            }}
            QLabel#visualLabValueText {{
                color: {colors.text};
                font-size: {FONT_LG};
                font-weight: {WEIGHT_BOLD};
                background: transparent;
            }}
            QLabel#visualLabMonoText {{
                color: {colors.text};
                background: transparent;
                font-family: {STATIC_TOKENS['font.family.mono']};
                font-size: {FONT_SM};
            }}
            """
        )


__all__ = ["VisualLabPage"]

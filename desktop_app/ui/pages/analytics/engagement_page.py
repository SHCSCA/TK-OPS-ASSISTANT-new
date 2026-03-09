# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false

from __future__ import annotations

"""互动分析页面。"""

from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    DistributionChart,
    FilterDropdown,
    FunnelChart,
    HeatmapWidget,
    KPICard,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    SentimentGauge,
    StatusBadge,
    TabBar,
    TagChip,
    ThemedComboBox,
    TrendComparison,
    WordCloudWidget,
)
from ...components.inputs import (
    RADIUS_LG,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    QFrame,
    QHBoxLayout,
    QLabel,
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


HEATMAP_VALUES: tuple[tuple[float, ...], ...] = (
    (18, 12, 10, 8, 6, 9, 16, 24, 38, 52, 61, 58, 49, 42, 39, 45, 54, 66, 79, 92, 108, 114, 93, 62),
    (14, 10, 8, 7, 5, 8, 15, 22, 34, 46, 57, 55, 47, 38, 35, 41, 49, 63, 74, 88, 103, 109, 90, 58),
    (16, 11, 9, 8, 6, 9, 17, 25, 37, 50, 59, 56, 46, 40, 38, 44, 53, 69, 82, 96, 112, 118, 95, 61),
    (17, 12, 10, 8, 7, 11, 18, 27, 39, 54, 65, 60, 52, 44, 42, 47, 58, 72, 86, 99, 117, 123, 101, 67),
    (20, 14, 11, 9, 8, 12, 20, 30, 43, 60, 72, 69, 58, 50, 48, 56, 68, 83, 98, 116, 134, 141, 122, 86),
    (24, 18, 15, 12, 10, 14, 22, 32, 47, 64, 76, 72, 63, 55, 54, 62, 74, 90, 108, 128, 146, 154, 136, 98),
    (19, 15, 13, 10, 9, 13, 19, 29, 44, 58, 68, 66, 57, 51, 49, 57, 69, 84, 101, 119, 139, 147, 129, 91),
)

WORD_CLOUD_ENTRIES: tuple[tuple[str, float], ...] = (
    ("非常好用", 96),
    ("物流给力", 78),
    ("回购多次", 82),
    ("推荐购买", 88),
    ("性价比高", 74),
    ("客服专业", 66),
    ("颜色漂亮", 57),
    ("功能强大", 63),
    ("值得信赖", 52),
    ("视频讲解清楚", 59),
    ("包装一般", 42),
    ("发货太慢", 39),
    ("赠品惊喜", 36),
    ("会继续关注", 48),
)

TREND_LABELS: tuple[str, ...] = ("03-01", "03-02", "03-03", "03-04", "03-05", "03-06", "03-07")
TREND_SERIES: dict[str, dict[str, object]] = {
    "总互动量": {
        "values": (12600.0, 13840.0, 14920.0, 15680.0, 17140.0, 18920.0, 20480.0),
        "unit": "次",
        "hint": "近 7 天点赞、评论、分享与收藏整体持续上扬，周末互动爆发最明显。",
    },
    "互动率": {
        "values": (5.4, 5.8, 6.1, 6.4, 6.9, 7.3, 7.8),
        "unit": "%",
        "hint": "内容完播率提升后，评论与分享同步放大，互动效率保持稳步走高。",
    },
    "正面情感占比": {
        "values": (61.0, 62.4, 63.8, 64.3, 65.1, 66.0, 67.2),
        "unit": "%",
        "hint": "售后回复效率与视频答疑质量改善后，正向反馈占比持续抬升。",
    },
}

SENTIMENT_COMPARE_LABELS: tuple[str, ...] = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
SENTIMENT_DISTRIBUTION: tuple[tuple[str, float], ...] = (
    ("正面情绪", 65),
    ("中性讨论", 20),
    ("负面反馈", 15),
)
POSITIVE_TREND: tuple[float, ...] = (58, 61, 63, 64, 66, 69, 72)
NEGATIVE_TREND: tuple[float, ...] = (19, 18, 17, 16, 15, 14, 13)

FLOW_STAGES: tuple[tuple[str, float], ...] = (
    ("视频曝光", 186000),
    ("有效观看", 82400),
    ("评论互动", 21400),
    ("私信咨询", 6800),
    ("加购跟进", 2480),
)
FLOW_DISTRIBUTION: tuple[tuple[str, float], ...] = (
    ("点赞互动", 46),
    ("评论互动", 29),
    ("分享传播", 15),
    ("收藏回看", 10),
)

HIGHLIGHT_ROWS: tuple[tuple[str, str, str], ...] = (
    ("“这款产品的设计真的惊艳到我了，希望能出更多颜色。”", "正面期待", "1,248"),
    ("“说明书写得有点简略，联网步骤建议再讲细一点。”", "建议反馈", "452"),
    ("“售后响应速度很快，处理问题很专业，体验超预期。”", "高赞好评", "890"),
    ("“短视频演示很完整，看完马上就下单了，节奏也很舒服。”", "成交驱动", "1,036"),
)

SCENE_COPY: dict[str, dict[str, str]] = {
    "短视频": {
        "peak": "短视频互动峰值集中在 20:00 - 22:00，问答型评论显著带动分享与收藏。",
        "flow": "短视频场景下，评论 → 私信咨询的转化衔接最强，适合加重限时福利与口播引导。",
    },
    "视频种草": {
        "peak": "视频种草场景在午休 12:00 - 13:00 与晚间 21:00 后形成双峰，收藏率更突出。",
        "flow": "视频种草更依赖前 3 秒钩子与评论区置顶话术，建议强化首屏利益点。",
    },
    "商品卡": {
        "peak": "商品卡互动更稳定，晚间下单前的收藏与问价行为最密集。",
        "flow": "商品卡用户更关注价格与履约说明，建议补足配送时效与套餐差异说明。",
    },
}


class EngagementPage(BasePage):
    """互动分析主页面。"""

    default_route_id: RouteId = RouteId("engagement_analysis")
    default_display_name: str = "互动分析"
    default_icon_name: str = "bar_chart"

    def setup_ui(self) -> None:
        """构建互动分析页面。"""

        _call(self, "setObjectName", "engagementPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_styles()

        page_container = PageContainer(
            title=self.display_name,
            description="聚焦评论热度、情绪倾向与用户流转节奏，帮助运营团队快速定位高响应内容与风险反馈。",
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._live_badge = StatusBadge("实时演算中", tone="brand", parent=page_container)
        self._export_button = SecondaryButton("导出报告", page_container, icon_text="↓")
        self._share_button = PrimaryButton("分享数据", page_container, icon_text="↗")
        page_container.add_action(self._live_badge)
        page_container.add_action(self._export_button)
        page_container.add_action(self._share_button)

        page_container.add_widget(self._build_filter_toolbar())
        page_container.add_widget(self._build_kpi_row())

        self._tab_bar = TabBar(self)
        self._tab_bar.add_tab("互动概览", self._build_overview_tab())
        self._tab_bar.add_tab("情感趋势", self._build_sentiment_tab())
        self._tab_bar.add_tab("用户流转", self._build_flow_tab())
        page_container.add_widget(self._tab_bar)

        _connect(getattr(self._range_filter, "filter_changed", None), self._refresh_context)
        _connect(getattr(self._scene_filter, "filter_changed", None), self._refresh_context)
        _connect(getattr(self._metric_combo.combo_box, "currentTextChanged", None), self._refresh_context)
        _connect(getattr(self._word_cloud, "word_clicked", None), self._handle_word_clicked)
        self._refresh_context()

    def _build_filter_toolbar(self) -> QWidget:
        """构建顶部筛选工具条。"""

        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "engagementToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        self._range_filter = FilterDropdown("时间范围", ("近7天", "近14天", "近30天"), include_all=False, parent=toolbar)
        self._scene_filter = FilterDropdown("内容场景", ("短视频", "视频种草", "商品卡"), include_all=False, parent=toolbar)
        self._metric_combo = ThemedComboBox("关注指标", ("总互动量", "互动率", "正面情感占比"), parent=toolbar)

        summary_wrap = QWidget(toolbar)
        summary_layout = QVBoxLayout(summary_wrap)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_SM)

        self._toolbar_title = QLabel("互动场景监控正常", summary_wrap)
        _call(self._toolbar_title, "setObjectName", "engagementPanelTitle")
        self._toolbar_hint = QLabel("当前使用演示数据，不会触发真实平台请求。", summary_wrap)
        _call(self._toolbar_hint, "setObjectName", "engagementSubtleText")
        _call(self._toolbar_hint, "setWordWrap", True)

        summary_layout.addWidget(self._toolbar_title)
        summary_layout.addWidget(self._toolbar_hint)

        layout.addWidget(self._range_filter)
        layout.addWidget(self._scene_filter)
        layout.addWidget(self._metric_combo)
        layout.addWidget(summary_wrap, 1)
        return toolbar

    def _build_kpi_row(self) -> QWidget:
        """构建顶部 KPI 区。"""

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._total_card = KPICard(
            "总互动量",
            "20,480",
            trend="up",
            percentage="18.6%",
            caption="较上周期提升",
            sparkline_data=(126, 138, 149, 156, 171, 189, 205),
            parent=row,
        )
        self._rate_card = KPICard(
            "互动率",
            "7.8%",
            trend="up",
            percentage="1.4pct",
            caption="评论与分享同步增长",
            sparkline_data=(5.4, 5.8, 6.1, 6.4, 6.9, 7.3, 7.8),
            parent=row,
        )
        self._sentiment_card = KPICard(
            "正面情感占比",
            "65%",
            trend="up",
            percentage="6.2%",
            caption="售后口碑持续修复",
            sparkline_data=(59, 60, 61, 62, 63, 64, 65),
            parent=row,
        )

        layout.addWidget(self._total_card, 1)
        layout.addWidget(self._rate_card, 1)
        layout.addWidget(self._sentiment_card, 1)
        return row

    def _build_overview_tab(self) -> QWidget:
        """构建互动概览标签页。"""

        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        heatmap_section = ContentSection("互动活跃热力图（24h / 7d）", icon="▦", parent=tab)
        heatmap_meta = QWidget(heatmap_section)
        heatmap_meta_layout = QHBoxLayout(heatmap_meta)
        heatmap_meta_layout.setContentsMargins(0, 0, 0, 0)
        heatmap_meta_layout.setSpacing(SPACING_SM)
        heatmap_meta_layout.addWidget(StatusBadge("晚高峰 20:00-22:00", tone="brand", parent=heatmap_meta))
        heatmap_meta_layout.addWidget(StatusBadge("短视频评论拉动 +18%", tone="success", parent=heatmap_meta))
        heatmap_meta_layout.addStretch(1)
        self._heatmap = HeatmapWidget(heatmap_section, HEATMAP_VALUES)
        self._heatmap_peak_label = QLabel("", heatmap_section)
        _call(self._heatmap_peak_label, "setObjectName", "engagementInsightLabel")
        _call(self._heatmap_peak_label, "setWordWrap", True)
        heatmap_section.add_widget(heatmap_meta)
        heatmap_section.add_widget(self._heatmap)
        heatmap_section.add_widget(self._heatmap_peak_label)

        mid_row = QWidget(tab)
        mid_layout = QHBoxLayout(mid_row)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(SPACING_LG)

        word_section = ContentSection("评论关键词云", icon="☁", parent=mid_row)
        self._word_cloud = WordCloudWidget(word_section, WORD_CLOUD_ENTRIES)
        word_meta = QWidget(word_section)
        word_meta_layout = QHBoxLayout(word_meta)
        word_meta_layout.setContentsMargins(0, 0, 0, 0)
        word_meta_layout.setSpacing(SPACING_SM)
        self._keyword_chip = TagChip("热词：非常好用", tone="brand", parent=word_meta)
        self._keyword_growth_badge = StatusBadge("环比 +12.4%", tone="success", parent=word_meta)
        word_meta_layout.addWidget(self._keyword_chip)
        word_meta_layout.addWidget(self._keyword_growth_badge)
        word_meta_layout.addStretch(1)
        word_section.add_widget(self._word_cloud)
        word_section.add_widget(word_meta)

        sentiment_section = ContentSection("情感倾向分布", icon="◔", parent=mid_row)
        self._sentiment_gauge = SentimentGauge(sentiment_section, 0.64)
        sentiment_meta = QWidget(sentiment_section)
        sentiment_meta_layout = QHBoxLayout(sentiment_meta)
        sentiment_meta_layout.setContentsMargins(0, 0, 0, 0)
        sentiment_meta_layout.setSpacing(SPACING_SM)
        sentiment_meta_layout.addWidget(StatusBadge("正面 65%", tone="success", parent=sentiment_meta))
        sentiment_meta_layout.addWidget(StatusBadge("中性 20%", tone="warning", parent=sentiment_meta))
        sentiment_meta_layout.addWidget(StatusBadge("负面 15%", tone="error", parent=sentiment_meta))
        sentiment_meta_layout.addStretch(1)
        sentiment_section.add_widget(self._sentiment_gauge)
        sentiment_section.add_widget(sentiment_meta)

        mid_layout.addWidget(word_section, 1)
        mid_layout.addWidget(sentiment_section, 1)

        trend_section = ContentSection("互动趋势走势", icon="∿", parent=tab)
        self._trend_chart = ChartWidget(
            chart_type="line",
            title="核心互动指标走势",
            labels=TREND_LABELS,
            data=TREND_SERIES["总互动量"]["values"],
            unit="次",
            parent=trend_section,
        )
        self._trend_hint_label = QLabel("", trend_section)
        _call(self._trend_hint_label, "setObjectName", "engagementInsightLabel")
        _call(self._trend_hint_label, "setWordWrap", True)
        trend_section.add_widget(self._trend_chart)
        trend_section.add_widget(self._trend_hint_label)

        highlight_section = ContentSection("高频互动内容回顾", icon="◎", parent=tab)
        self._highlight_table = DataTable(
            headers=("评论内容摘要", "情感标签", "互动热度"),
            rows=HIGHLIGHT_ROWS,
            page_size=4,
            empty_text="暂无互动评论样本",
            parent=highlight_section,
        )
        self._highlight_hint = QLabel("优先关注高热度正向内容的复用机会，同时跟进“发货慢”“说明不清”等风险反馈。", highlight_section)
        _call(self._highlight_hint, "setObjectName", "engagementSubtleText")
        _call(self._highlight_hint, "setWordWrap", True)
        highlight_section.add_widget(self._highlight_table)
        highlight_section.add_widget(self._highlight_hint)

        layout.addWidget(heatmap_section)
        layout.addWidget(mid_row)
        layout.addWidget(trend_section)
        layout.addWidget(highlight_section)
        return tab

    def _build_sentiment_tab(self) -> QWidget:
        """构建情感趋势标签页。"""

        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        row = QWidget(tab)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_LG)

        comparison_section = ContentSection("正负情绪周趋势对比", icon="∿", parent=row)
        self._sentiment_trend = TrendComparison(
            comparison_section,
            labels=SENTIMENT_COMPARE_LABELS,
            current_values=POSITIVE_TREND,
            compare_values=NEGATIVE_TREND,
            current_name="正向讨论",
            compare_name="负面反馈",
        )
        comparison_section.add_widget(self._sentiment_trend)

        distribution_section = ContentSection("情绪结构拆解", icon="◔", parent=row)
        self._sentiment_distribution = DistributionChart(distribution_section, SENTIMENT_DISTRIBUTION)
        distribution_section.add_widget(self._sentiment_distribution)

        row_layout.addWidget(comparison_section, 3)
        row_layout.addWidget(distribution_section, 2)

        note_section = ContentSection("情绪观察结论", icon="◌", parent=tab)
        note_wrap = QWidget(note_section)
        note_layout = QVBoxLayout(note_wrap)
        note_layout.setContentsMargins(0, 0, 0, 0)
        note_layout.setSpacing(SPACING_MD)

        note_layout.addWidget(TagChip("正面驱动：演示清晰", tone="success", parent=note_wrap))
        note_layout.addWidget(TagChip("中性高频：询价与配送", tone="info", parent=note_wrap))
        note_layout.addWidget(TagChip("风险反馈：发货速度", tone="warning", parent=note_wrap))

        self._sentiment_note_label = QLabel(
            "用户对产品外观、演示细节和客服响应评价更高；少量负面反馈集中在物流时效与说明文档完整度。",
            note_section,
        )
        _call(self._sentiment_note_label, "setObjectName", "engagementInsightLabel")
        _call(self._sentiment_note_label, "setWordWrap", True)
        note_section.add_widget(note_wrap)
        note_section.add_widget(self._sentiment_note_label)

        layout.addWidget(row)
        layout.addWidget(note_section)
        return tab

    def _build_flow_tab(self) -> QWidget:
        """构建用户流转标签页。"""

        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        row = QWidget(tab)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_LG)

        funnel_section = ContentSection("互动到转化流转漏斗", icon="▾", parent=row)
        self._flow_funnel = FunnelChart(funnel_section, FLOW_STAGES)
        funnel_section.add_widget(self._flow_funnel)

        distribution_section = ContentSection("互动动作分布", icon="▥", parent=row)
        self._flow_distribution = DistributionChart(distribution_section, FLOW_DISTRIBUTION)
        distribution_section.add_widget(self._flow_distribution)

        row_layout.addWidget(funnel_section, 3)
        row_layout.addWidget(distribution_section, 2)

        insight_section = ContentSection("流转洞察", icon="◎", parent=tab)
        self._flow_note_label = QLabel("", insight_section)
        _call(self._flow_note_label, "setObjectName", "engagementInsightLabel")
        _call(self._flow_note_label, "setWordWrap", True)
        insight_section.add_widget(self._flow_note_label)

        layout.addWidget(row)
        layout.addWidget(insight_section)
        return tab

    def _refresh_context(self, *_args: object) -> None:
        """根据筛选项刷新趋势说明与场景提示。"""

        range_text = self._range_filter.current_text() or "近7天"
        scene_text = self._scene_filter.current_text() or "短视频"
        metric_text = self._metric_combo.current_text() or "总互动量"
        trend_meta = TREND_SERIES.get(metric_text, TREND_SERIES["总互动量"])
        values = trend_meta["values"]
        unit = str(trend_meta["unit"])
        hint = str(trend_meta["hint"])
        scene_meta = SCENE_COPY.get(scene_text, SCENE_COPY["短视频"])

        self._trend_chart.set_data(values, TREND_LABELS)
        self._trend_chart.set_unit(unit)
        self._trend_hint_label.setText(f"{range_text} · {scene_text} · 当前聚焦“{metric_text}”。{hint}")
        self._heatmap_peak_label.setText(scene_meta["peak"])
        self._flow_note_label.setText(f"{range_text} 内，{scene_meta['flow']}")
        self._toolbar_title.setText(f"{scene_text}互动场景监控正常")
        self._toolbar_hint.setText(f"当前查看 {range_text} 的 {scene_text} 数据，主观察指标为“{metric_text}”。")

    def _handle_word_clicked(self, word: str) -> None:
        """响应词云热词点击。"""

        self._keyword_chip.set_text(f"热词：{word}")
        self._keyword_chip.set_tone("brand")
        self._keyword_growth_badge.setText("已切换关键词焦点")
        self._keyword_growth_badge.set_tone("info")

    def _apply_styles(self) -> None:
        """应用页面样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#engagementPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#engagementToolbar {{
                background-color: {colors.surface};
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#engagementPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#engagementSubtleText {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#engagementInsightLabel {{
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                background-color: {_rgba(_token('brand.primary'), 0.08)};
                border: 1px solid {_rgba(_token('brand.primary'), 0.18)};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_MD}px {SPACING_LG}px;
            }}
            """,
        )


__all__ = ["EngagementPage"]

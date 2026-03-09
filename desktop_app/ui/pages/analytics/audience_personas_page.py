# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""粉丝画像页面。"""

from dataclasses import dataclass
from typing import Final, Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    DistributionChart,
    FilterDropdown,
    HeatmapWidget,
    KPICard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SentimentGauge,
    StatusBadge,
    TabBar,
    TagChip,
    WordCloudWidget,
)
from ...components.inputs import RADIUS_LG, SPACING_LG, SPACING_MD, SPACING_SM, SPACING_XL, SPACING_XS, _call, _connect, _palette, _static_token, _token
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _format_compact(value: int | float) -> str:
    amount = float(value)
    if abs(amount) >= 100000000:
        return f"{amount / 100000000:.2f}亿"
    if abs(amount) >= 10000:
        return f"{amount / 10000:.1f}万"
    return f"{amount:,.0f}"


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


@dataclass(frozen=True)
class FanRecord:
    nickname: str
    region: str
    creator_type: str
    engagement_index: float
    active_days: int
    spend_level: str
    favorite_topic: str
    gender: str
    age_bucket: str


AGE_LABELS: Final[tuple[str, ...]] = ("18-24", "25-30", "31-35", "36-40", "41+", "未标注")
GENDER_LABELS: Final[tuple[str, ...]] = ("女性", "男性", "未标注")
FAN_HEADERS: Final[tuple[str, ...]] = ("昵称", "地区", "创作者类型", "互动指数", "活跃天数", "消费层级", "兴趣主题")
REGION_HEADERS: Final[tuple[str, ...]] = ("地区", "粉丝数", "活跃占比", "互动率", "增长率")
TREND_LABELS: Final[tuple[str, ...]] = ("第1周", "第2周", "第3周", "第4周", "第5周", "第6周", "第7周", "第8周")
TAB_LABELS: Final[tuple[str, ...]] = ("粉丝总览", "兴趣洞察", "核心人群")
SOURCE_OPTIONS: Final[tuple[str, ...]] = ("全部粉丝", "近 30 天新增", "高互动粉丝", "高消费粉丝")
REGION_OPTIONS: Final[tuple[str, ...]] = ("美国", "英国", "加拿大", "德国", "法国", "日本", "韩国", "澳大利亚", "新加坡")

FANS: Final[tuple[FanRecord, ...]] = (
    FanRecord("纽约通勤穿搭控", "美国", "穿搭创作者", 0.92, 26, "高消费", "冬季通勤", "女性", "25-30"),
    FanRecord("伦敦家居疗愈派", "英国", "家居创作者", 0.88, 24, "中高消费", "香氛布置", "女性", "31-35"),
    FanRecord("多伦多装备测评官", "加拿大", "数码创作者", 0.81, 22, "高消费", "耳机数码", "男性", "25-30"),
    FanRecord("柏林简约生活集", "德国", "生活方式博主", 0.77, 19, "中消费", "收纳整理", "女性", "31-35"),
    FanRecord("巴黎妆容收藏夹", "法国", "美妆创作者", 0.85, 23, "高消费", "节日妆容", "女性", "18-24"),
    FanRecord("东京跑步装备党", "日本", "运动创作者", 0.79, 20, "中高消费", "运动装备", "男性", "25-30"),
    FanRecord("首尔极简咖啡角", "韩国", "家居创作者", 0.74, 17, "中消费", "咖啡角布置", "女性", "18-24"),
    FanRecord("悉尼瑜伽晨练派", "澳大利亚", "健身创作者", 0.82, 21, "中高消费", "瑜伽穿搭", "女性", "25-30"),
    FanRecord("新加坡收纳清单控", "新加坡", "效率创作者", 0.71, 15, "中消费", "桌面收纳", "女性", "31-35"),
    FanRecord("芝加哥节日礼物党", "美国", "生活方式博主", 0.84, 18, "中高消费", "礼盒开箱", "男性", "31-35"),
    FanRecord("曼彻斯特复古饰品迷", "英国", "配饰创作者", 0.76, 16, "中消费", "通勤配饰", "女性", "18-24"),
    FanRecord("大阪质感家电控", "日本", "数码创作者", 0.73, 14, "高消费", "小家电", "男性", "36-40"),
)

FOLLOWER_GROWTH: Final[tuple[int, ...]] = (128000, 132400, 136900, 141300, 146800, 152200, 158900, 165600)
FOLLOWER_COMPARE: Final[tuple[int, ...]] = (118000, 121200, 124800, 128200, 131900, 135400, 139100, 143300)
AGE_DISTRIBUTION: Final[tuple[int, int, int, int, int, int]] = (28, 34, 18, 10, 6, 4)
GENDER_DISTRIBUTION: Final[tuple[int, int, int]] = (62, 31, 7)
REGION_TABLE: Final[tuple[tuple[str, int, float, float, float], ...]] = (
    ("美国", 48200, 0.64, 0.087, 0.118),
    ("英国", 26100, 0.59, 0.081, 0.106),
    ("加拿大", 19400, 0.57, 0.079, 0.098),
    ("德国", 16800, 0.53, 0.072, 0.084),
    ("法国", 15100, 0.55, 0.080, 0.091),
    ("日本", 13900, 0.51, 0.075, 0.083),
    ("韩国", 11800, 0.49, 0.069, 0.072),
    ("澳大利亚", 10900, 0.56, 0.077, 0.088),
    ("新加坡", 9200, 0.54, 0.071, 0.079),
)
ACTIVITY_HEATMAP: Final[tuple[tuple[float, ...], ...]] = (
    (8, 10, 12, 11, 9, 7, 5, 4, 5, 6, 7, 8, 10, 13, 16, 20, 24, 28, 31, 33, 30, 24, 18, 12),
    (7, 8, 10, 9, 8, 6, 4, 4, 5, 6, 8, 10, 12, 15, 18, 22, 26, 30, 34, 37, 34, 27, 20, 13),
    (6, 7, 8, 8, 7, 5, 4, 4, 5, 7, 9, 11, 14, 17, 21, 25, 30, 35, 40, 44, 39, 31, 22, 14),
    (7, 8, 9, 8, 7, 5, 4, 4, 5, 7, 10, 13, 16, 19, 23, 27, 33, 39, 44, 48, 43, 34, 25, 16),
    (8, 9, 10, 10, 8, 6, 5, 5, 6, 8, 11, 14, 17, 21, 25, 30, 36, 42, 48, 54, 49, 38, 28, 18),
    (10, 11, 13, 12, 10, 8, 7, 6, 7, 9, 12, 15, 19, 23, 28, 34, 41, 48, 55, 61, 56, 44, 33, 22),
    (11, 12, 15, 14, 12, 10, 8, 7, 8, 10, 13, 17, 21, 26, 31, 37, 44, 52, 59, 66, 60, 47, 35, 24),
)
INTEREST_WORDS: Final[tuple[tuple[str, float], ...]] = (
    ("冬季穿搭", 92), ("收纳整理", 81), ("节日礼物", 74), ("香氛氛围", 68), ("瑜伽运动", 66), ("咖啡角", 61), ("通勤包", 59), ("数码耳机", 57), ("家电测评", 55), ("妆容灵感", 53), ("桌面布置", 49), ("礼盒开箱", 46), ("宠物家居", 42), ("极简生活", 40),
)
TOPIC_PLAYBOOKS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("冬季穿搭", "适合发布场景式合集、通勤模版与多价格带对比。", (18, 20, 24, 28, 33, 37, 42)),
    ("收纳整理", "适合做前后对比、教程拆解与套装清单。", (16, 18, 21, 24, 27, 31, 36)),
    ("节日礼物", "适合做节日节点礼盒推荐与预算区间榜单。", (14, 17, 20, 24, 28, 32, 35)),
    ("香氛氛围", "适合做氛围布置、嗅觉场景联想与礼赠组合。", (12, 15, 18, 22, 25, 29, 33)),
)
SEGMENT_INSIGHTS: Final[tuple[tuple[str, str, str], ...]] = (
    ("18-24 岁", "高互动", "偏好轻决策内容，适合榜单、合集与快节奏剪辑。"),
    ("25-30 岁", "高转化", "偏好功能 + 场景内容，适合对比与教程结构。"),
    ("31-35 岁", "高客单", "偏好质感与实用并重，适合生活方式组合提案。"),
    ("36-40 岁", "高复购", "偏好稳定品牌心智，适合系列化更新。"),
)
CREATOR_ARCHETYPES: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("穿搭创作者", "适合高频更新通勤、节日、预算分层内容。", (18, 21, 25, 29, 34, 39, 43)),
    ("家居创作者", "适合做前后对比、布置模板与空间改造。", (16, 19, 22, 26, 29, 33, 38)),
    ("数码创作者", "适合突出测评、性能对比与真实场景演示。", (14, 16, 19, 23, 27, 31, 35)),
    ("生活方式博主", "适合氛围感合集、节日场景与生活提案。", (15, 17, 20, 24, 28, 32, 36)),
)
CONTENT_SIGNAL_ROWS: Final[tuple[tuple[str, str, str], ...]] = (
    ("高收藏", "清单型内容", "适合做预算、榜单与套组推荐。"),
    ("高评论", "争议型对比", "适合引导互动并提炼 FAQ 选题。"),
    ("高分享", "场景模板", "适合沉淀模板化系列内容。"),
    ("高停留", "教程拆解", "适合分步骤细化并延展系列。"),
)
REGIONAL_STORIES: Final[tuple[tuple[str, str, str, tuple[int, ...]], ...]] = (
    ("美国", "通勤与节日并重", "高峰集中在晚间，适合通勤穿搭与礼盒推荐双线并行。", (22, 25, 29, 33, 38, 42, 46)),
    ("英国", "氛围与家居偏好", "用户更偏好质感布置与香氛类内容，适合柔和叙事节奏。", (18, 20, 23, 27, 30, 34, 37)),
    ("日本", "测评与清单兼顾", "对实用型拆解内容反馈更高，适合功能性标题与步骤说明。", (16, 18, 20, 24, 27, 30, 34)),
    ("澳大利亚", "运动生活方式", "晨间与午后都有活跃波峰，适合运动穿搭与户外收纳选题。", (15, 17, 20, 23, 27, 31, 35)),
)
PURCHASE_LADDERS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("兴趣触达", "通过合集、榜单与种草封面建立初始记忆。", (14, 16, 19, 22, 26, 29, 33)),
    ("深度停留", "用教程、对比与步骤拆解提高停留时长。", (12, 15, 18, 22, 25, 29, 32)),
    ("主页回访", "通过系列化更新与置顶合集推动多次访问。", (10, 12, 15, 18, 22, 26, 30)),
    ("转化触发", "结合优惠口径与组合提案完成最终决策。", (8, 10, 13, 16, 19, 23, 27)),
)
RETENTION_SIGNALS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("7 日留存", "系列化内容更新后留存抬升明显。", (34, 35, 37, 40, 42, 45, 48)),
    ("14 日回访", "主页合集与置顶内容能持续带动回访。", (28, 30, 31, 33, 36, 38, 41)),
    ("30 日深度互动", "高价值粉丝更偏好教程与预算对比内容。", (19, 21, 23, 26, 29, 32, 35)),
)
COMMUNITY_ACTIONS: Final[tuple[tuple[str, str, tuple[int, ...]], ...]] = (
    ("评论区问答", "把高频评论整理成 FAQ 选题池。", (12, 14, 17, 20, 24, 27, 30)),
    ("合拍征集", "引导用户用相同主题参与二次创作。", (10, 12, 15, 18, 21, 25, 29)),
    ("收藏清单", "发布可保存的预算表与商品清单。", (11, 13, 16, 19, 23, 26, 30)),
)


class AudiencePersonasPage(BasePage):
    """粉丝画像页面。"""

    default_route_id: RouteId = RouteId("audience_personas")
    default_display_name: str = "粉丝画像"
    default_icon_name: str = "groups"

    def setup_ui(self) -> None:
        self._current_tab = TAB_LABELS[0]
        self._selected_group = SOURCE_OPTIONS[0]
        self._selected_region = "全部"
        self._keyword = ""
        self._selected_index = 0

        self._search_bar: SearchBar | None = None
        self._group_filter: FilterDropdown | None = None
        self._region_filter: FilterDropdown | None = None
        self._tab_bar: TabBar | None = None
        self._age_chart: DistributionChart | None = None
        self._gender_chart: DistributionChart | None = None
        self._growth_chart: ChartWidget | None = None
        self._activity_heatmap: HeatmapWidget | None = None
        self._interest_cloud: WordCloudWidget | None = None
        self._region_table: DataTable | None = None
        self._fan_table: DataTable | None = None
        self._sentiment_gauge: SentimentGauge | None = None
        self._selection_title: QLabel | None = None
        self._selection_meta: QLabel | None = None
        self._selection_body: QLabel | None = None
        self._selection_badges: list[StatusBadge] = []
        self._selection_metrics: dict[str, QLabel] = {}
        self._playbook_sparklines: list[ChartWidget | None] = []
        self._playbook_value_labels: list[QLabel] = []
        self._segment_body_labels: list[QLabel] = []
        self._archetype_charts: list[ChartWidget] = []
        self._kpi_cards: dict[str, KPICard] = {}

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(self, "setObjectName", "audiencePersonasPage")

        self._page_container = PageContainer(
            title="粉丝画像",
            description="从人口属性、地域、兴趣与活跃时段切入，识别最有价值的 TikTok 核心人群与内容偏好。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._build_header_actions()
        self._page_container.add_widget(self._build_toolbar())
        self._page_container.add_widget(self._build_kpis())
        self._page_container.add_widget(self._build_workspace())
        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_header_actions(self) -> None:
        self._page_container.add_action(TagChip("粉丝增长持续向上", tone="success", parent=self))
        self._page_container.add_action(TagChip("女性占比领先", tone="brand", parent=self))
        self._page_container.add_action(StatusBadge("高互动粉丝占比 31%", tone="info", parent=self))
        self._page_container.add_action(SecondaryButton("刷新样本", parent=self))
        self._page_container.add_action(PrimaryButton("导出画像摘要", parent=self))

    def _build_toolbar(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "audienceToolbar")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        title_row = QWidget(panel)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)
        title_column = QWidget(title_row)
        title_column_layout = QVBoxLayout(title_column)
        title_column_layout.setContentsMargins(0, 0, 0, 0)
        title_column_layout.setSpacing(SPACING_XS)
        title_label = QLabel("画像筛选", title_column)
        _call(title_label, "setObjectName", "audiencePanelTitle")
        helper_label = QLabel("按样本人群、地区与关键词切片粉丝结构，联动兴趣洞察与核心人群模块。", title_column)
        _call(helper_label, "setObjectName", "audienceSubtleText")
        _call(helper_label, "setWordWrap", True)
        title_column_layout.addWidget(title_label)
        title_column_layout.addWidget(helper_label)
        title_layout.addWidget(title_column, 1)
        title_layout.addWidget(StatusBadge("高互动样本已锁定", tone="success", parent=title_row))

        row = QWidget(panel)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_LG)
        self._search_bar = SearchBar("搜索粉丝昵称、兴趣、地区或创作者类型...", row)
        self._group_filter = FilterDropdown("样本人群", SOURCE_OPTIONS, include_all=False, parent=row)
        self._region_filter = FilterDropdown("地区", REGION_OPTIONS, parent=row)
        row_layout.addWidget(self._search_bar, 3)
        row_layout.addWidget(self._group_filter, 1)
        row_layout.addWidget(self._region_filter, 1)

        tags = QWidget(panel)
        tags_layout = QHBoxLayout(tags)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(SPACING_MD)
        tags_layout.addWidget(TagChip("18-30 岁为主力", tone="warning", parent=tags))
        tags_layout.addWidget(TagChip("夜间 20-22 点最活跃", tone="info", parent=tags))
        tags_layout.addWidget(TagChip("家居与穿搭共振明显", tone="brand", parent=tags))
        tags_layout.addStretch(1)
        tags_layout.addWidget(SecondaryButton("重置画像", parent=tags))
        tags_layout.addWidget(PrimaryButton("同步内容策略", parent=tags))

        layout.addWidget(title_row)
        layout.addWidget(row)
        layout.addWidget(tags)
        return panel

    def _build_kpis(self) -> QWidget:
        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        for title in ("总粉丝", "活跃粉丝比", "粉丝增长率", "互动指数"):
            card = KPICard(title=title, value="-", trend="up", percentage="+0.0%", caption="近 8 周变化", sparkline_data=(0, 0, 0, 0, 0, 0, 0), parent=wrapper)
            self._kpi_cards[title] = card
            layout.addWidget(card, 1)
        return wrapper

    def _build_workspace(self) -> QWidget:
        shell = QWidget(self)
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_left_column(), 3)
        layout.addWidget(self._build_right_column(), 2)
        return shell

    def _build_left_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_tabs())
        layout.addWidget(self._build_interest_section())
        layout.addWidget(self._build_fan_table_section())
        layout.addWidget(self._build_playbook_section())
        layout.addWidget(self._build_archetype_section())
        layout.addWidget(self._build_signal_section())
        layout.addWidget(self._build_regional_story_section())
        layout.addWidget(self._build_retention_section())
        layout.addWidget(self._build_community_action_section())
        return column

    def _build_right_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_selection_section())
        layout.addWidget(self._build_region_section())
        layout.addWidget(self._build_activity_section())
        layout.addWidget(self._build_segment_section())
        layout.addWidget(self._build_purchase_ladder_section())
        return column

    def _build_tabs(self) -> QWidget:
        section = ContentSection("人群结构", icon="◎", parent=self)
        self._tab_bar = TabBar(section)
        self._tab_bar.add_tab(TAB_LABELS[0], self._build_overview_tab())
        self._tab_bar.add_tab(TAB_LABELS[1], self._build_interest_tab())
        self._tab_bar.add_tab(TAB_LABELS[2], self._build_core_group_tab())
        section.add_widget(self._tab_bar)
        return section

    def _build_overview_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        left = ContentSection("年龄分布", icon="▥", parent=page)
        self._age_chart = DistributionChart(left, tuple(zip(AGE_LABELS, AGE_DISTRIBUTION)))
        left.add_widget(self._age_chart)
        layout.addWidget(left, 1)
        right = ContentSection("性别占比", icon="◔", parent=page)
        self._gender_chart = DistributionChart(right, tuple(zip(GENDER_LABELS, GENDER_DISTRIBUTION)))
        self._sentiment_gauge = SentimentGauge(right, 0.42)
        right.add_widget(self._gender_chart)
        right.add_widget(self._sentiment_gauge)
        layout.addWidget(right, 1)
        return page

    def _build_interest_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        self._interest_cloud = WordCloudWidget(page, INTEREST_WORDS)
        layout.addWidget(self._interest_cloud)
        return page

    def _build_core_group_tab(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        self._growth_chart = ChartWidget(chart_type="line", title="粉丝增长趋势", labels=TREND_LABELS, data=FOLLOWER_GROWTH, unit="人", parent=page)
        layout.addWidget(self._growth_chart)
        return page

    def _build_interest_section(self) -> QWidget:
        section = ContentSection("兴趣词云", icon="✦", parent=self)
        if self._interest_cloud is None:
            self._interest_cloud = WordCloudWidget(section, INTEREST_WORDS)
        section.add_widget(self._interest_cloud)
        return section

    def _build_fan_table_section(self) -> QWidget:
        section = ContentSection("核心粉丝 / 创作者", icon="▤", parent=self)
        self._fan_table = DataTable(headers=FAN_HEADERS, rows=(), page_size=8, empty_text="暂无粉丝数据", parent=section)
        section.add_widget(self._fan_table)
        return section

    def _build_selection_section(self) -> QWidget:
        section = ContentSection("人群摘要", icon="◌", parent=self)
        card = QFrame(section)
        _call(card, "setObjectName", "audienceDetailCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)
        self._selection_title = QLabel("等待选择粉丝", card)
        self._selection_meta = QLabel("", card)
        self._selection_body = QLabel("点击左侧粉丝行后，此处展示其互动、兴趣与消费偏好。", card)
        _call(self._selection_title, "setObjectName", "audienceSelectionTitle")
        _call(self._selection_meta, "setObjectName", "audienceSubtleText")
        _call(self._selection_body, "setObjectName", "audienceSubtleText")
        _call(self._selection_body, "setWordWrap", True)
        layout.addWidget(self._selection_title)
        layout.addWidget(self._selection_meta)
        layout.addWidget(self._selection_body)
        badges = QWidget(card)
        badges_layout = QHBoxLayout(badges)
        badges_layout.setContentsMargins(0, 0, 0, 0)
        badges_layout.setSpacing(SPACING_SM)
        for text, tone in (("美国", "brand"), ("高消费", "success"), ("冬季穿搭", "warning")):
            badge = StatusBadge(text, tone=tone, parent=badges)
            self._selection_badges.append(badge)
            badges_layout.addWidget(badge)
        badges_layout.addStretch(1)
        layout.addWidget(badges)
        for metric in ("互动指数", "活跃天数", "性别", "年龄段"):
            row = QFrame(card)
            _call(row, "setObjectName", "audienceMetricCard")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            row_layout.setSpacing(SPACING_SM)
            label = QLabel(metric, row)
            value = QLabel("-", row)
            _call(label, "setObjectName", "audienceMetricTitle")
            _call(value, "setObjectName", "audienceMetricValue")
            row_layout.addWidget(label)
            row_layout.addStretch(1)
            row_layout.addWidget(value)
            self._selection_metrics[metric] = value
            layout.addWidget(row)
        section.add_widget(card)
        return section

    def _build_region_section(self) -> QWidget:
        section = ContentSection("地区分布", icon="◫", parent=self)
        self._region_table = DataTable(headers=REGION_HEADERS, rows=(), page_size=8, empty_text="暂无地区数据", parent=section)
        section.add_widget(self._region_table)
        return section

    def _build_activity_section(self) -> QWidget:
        section = ContentSection("活跃时段", icon="⏱", parent=self)
        self._activity_heatmap = HeatmapWidget(section, ACTIVITY_HEATMAP)
        section.add_widget(self._activity_heatmap)
        return section

    def _build_playbook_section(self) -> QWidget:
        section = ContentSection("兴趣运营建议", icon="↗", parent=self)
        for title, summary, values in TOPIC_PLAYBOOKS:
            card = QFrame(section)
            _call(card, "setObjectName", "audiencePlaybookCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            summary_label = QLabel(summary, card)
            value_label = QLabel(f"预计带动互动 {_format_percent(max(values) / 100.0)}", card)
            chart = ChartWidget(chart_type="line", title="互动预估曲线", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(title_label, "setObjectName", "audienceMetricTitle")
            _call(summary_label, "setObjectName", "audienceSubtleText")
            _call(summary_label, "setWordWrap", True)
            _call(value_label, "setObjectName", "audienceMetricValue")
            self._playbook_sparklines.append(chart)
            self._playbook_value_labels.append(value_label)
            layout.addWidget(title_label)
            layout.addWidget(summary_label)
            layout.addWidget(chart)
            layout.addWidget(value_label)
            section.add_widget(card)
        return section

    def _build_segment_section(self) -> QWidget:
        section = ContentSection("核心分层", icon="◎", parent=self)
        for title, flag, summary in SEGMENT_INSIGHTS:
            card = QFrame(section)
            _call(card, "setObjectName", "audienceSegmentCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_XS)
            header = QWidget(card)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(SPACING_SM)
            label = QLabel(title, header)
            badge = StatusBadge(flag, tone="success" if "高" in flag else "info", parent=header)
            _call(label, "setObjectName", "audienceMetricTitle")
            header_layout.addWidget(label)
            header_layout.addStretch(1)
            header_layout.addWidget(badge)
            body = QLabel(summary, card)
            _call(body, "setObjectName", "audienceSubtleText")
            _call(body, "setWordWrap", True)
            self._segment_body_labels.append(body)
            layout.addWidget(header)
            layout.addWidget(body)
            section.add_widget(card)
        return section

    def _build_archetype_section(self) -> QWidget:
        section = ContentSection("创作者原型", icon="◔", parent=self)
        for name, summary, values in CREATOR_ARCHETYPES:
            card = QFrame(section)
            _call(card, "setObjectName", "audienceArchetypeCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            name_label = QLabel(name, card)
            summary_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="内容响应趋势", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(name_label, "setObjectName", "audienceMetricTitle")
            _call(summary_label, "setObjectName", "audienceSubtleText")
            _call(summary_label, "setWordWrap", True)
            self._archetype_charts.append(chart)
            layout.addWidget(name_label)
            layout.addWidget(summary_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_signal_section(self) -> QWidget:
        section = ContentSection("内容信号建议", icon="✓", parent=self)
        for signal, topic, summary in CONTENT_SIGNAL_ROWS:
            row = QFrame(section)
            _call(row, "setObjectName", "audienceSignalCard")
            layout = QHBoxLayout(row)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            layout.addWidget(StatusBadge(signal, tone="info", parent=row))
            topic_label = QLabel(topic, row)
            summary_label = QLabel(summary, row)
            _call(topic_label, "setObjectName", "audienceMetricTitle")
            _call(summary_label, "setObjectName", "audienceSubtleText")
            layout.addWidget(topic_label)
            layout.addStretch(1)
            layout.addWidget(summary_label)
            section.add_widget(row)
        return section

    def _build_regional_story_section(self) -> QWidget:
        section = ContentSection("地区内容叙事", icon="◫", parent=self)
        for region, tag, summary, values in REGIONAL_STORIES:
            card = QFrame(section)
            _call(card, "setObjectName", "audienceRegionStoryCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            header = QWidget(card)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(SPACING_SM)
            title = QLabel(region, header)
            badge = StatusBadge(tag, tone="brand", parent=header)
            _call(title, "setObjectName", "audienceMetricTitle")
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(badge)
            body = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="地区响应曲线", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(body, "setObjectName", "audienceSubtleText")
            _call(body, "setWordWrap", True)
            layout.addWidget(header)
            layout.addWidget(body)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_purchase_ladder_section(self) -> QWidget:
        section = ContentSection("消费心智梯度", icon="↗", parent=self)
        for title, summary, values in PURCHASE_LADDERS:
            card = QFrame(section)
            _call(card, "setObjectName", "audiencePurchaseLadderCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="bar", title="阶段提升潜力", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(title_label, "setObjectName", "audienceMetricTitle")
            _call(body_label, "setObjectName", "audienceSubtleText")
            _call(body_label, "setWordWrap", True)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_retention_section(self) -> QWidget:
        section = ContentSection("留存信号", icon="◎", parent=self)
        for title, summary, values in RETENTION_SIGNALS:
            card = QFrame(section)
            _call(card, "setObjectName", "audienceRetentionCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="line", title="留存变化趋势", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(title_label, "setObjectName", "audienceMetricTitle")
            _call(body_label, "setObjectName", "audienceSubtleText")
            _call(body_label, "setWordWrap", True)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _build_community_action_section(self) -> QWidget:
        section = ContentSection("社群动作建议", icon="✓", parent=self)
        for title, summary, values in COMMUNITY_ACTIONS:
            card = QFrame(section)
            _call(card, "setObjectName", "audienceCommunityCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
            layout.setSpacing(SPACING_SM)
            title_label = QLabel(title, card)
            body_label = QLabel(summary, card)
            chart = ChartWidget(chart_type="bar", title="预估互动提升", labels=("1", "2", "3", "4", "5", "6", "7"), data=values, unit="%", parent=card)
            _call(title_label, "setObjectName", "audienceMetricTitle")
            _call(body_label, "setObjectName", "audienceSubtleText")
            _call(body_label, "setWordWrap", True)
            layout.addWidget(title_label)
            layout.addWidget(body_label)
            layout.addWidget(chart)
            section.add_widget(card)
        return section

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._handle_search)
        if self._group_filter is not None:
            _connect(self._group_filter.filter_changed, self._handle_group)
        if self._region_filter is not None:
            _connect(self._region_filter.filter_changed, self._handle_region)
        if self._tab_bar is not None:
            _connect(self._tab_bar.tab_changed, self._handle_tab)
        if self._fan_table is not None:
            _connect(self._fan_table.row_selected, self._handle_row)
            _connect(self._fan_table.row_double_clicked, self._handle_row)
        if self._interest_cloud is not None:
            _connect(self._interest_cloud.word_clicked, self._handle_word_clicked)

    def _handle_search(self, text: str) -> None:
        self._keyword = text.strip()
        self._selected_index = 0
        self._refresh_all_views()

    def _handle_group(self, text: str) -> None:
        self._selected_group = text
        self._refresh_all_views()

    def _handle_region(self, text: str) -> None:
        self._selected_region = text
        self._selected_index = 0
        self._refresh_all_views()

    def _handle_tab(self, index: int) -> None:
        if 0 <= index < len(TAB_LABELS):
            self._current_tab = TAB_LABELS[index]
            self._refresh_all_views()

    def _handle_row(self, index: int) -> None:
        self._selected_index = index
        self._refresh_selection()

    def _handle_word_clicked(self, text: str) -> None:
        self._keyword = text
        if self._search_bar is not None:
            self._search_bar.setText(text)
        self._refresh_all_views()

    def _filtered_fans(self) -> list[FanRecord]:
        fans: list[FanRecord] = []
        for fan in FANS:
            searchable = " ".join((fan.nickname, fan.region, fan.creator_type, fan.favorite_topic, fan.spend_level))
            if self._keyword and self._keyword.lower() not in searchable.lower():
                continue
            if self._selected_region not in {"", "全部"} and fan.region != self._selected_region:
                continue
            if self._selected_group == "高互动粉丝" and fan.engagement_index < 0.82:
                continue
            if self._selected_group == "高消费粉丝" and "高" not in fan.spend_level:
                continue
            if self._selected_group == "近 30 天新增" and fan.active_days < 18:
                continue
            fans.append(fan)
        return fans

    def _fan_rows(self, fans: Sequence[FanRecord]) -> list[list[object]]:
        return [[fan.nickname, fan.region, fan.creator_type, _format_percent(fan.engagement_index), str(fan.active_days), fan.spend_level, fan.favorite_topic] for fan in fans]

    def _region_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for region, total, active_ratio, engagement, growth in REGION_TABLE:
            if self._selected_region not in {"", "全部"} and region != self._selected_region:
                continue
            rows.append([region, _format_compact(total), _format_percent(active_ratio), _format_percent(engagement), _format_percent(growth)])
        return rows

    def _selected_fan(self) -> FanRecord | None:
        fans = self._filtered_fans()
        if not fans:
            return None
        self._selected_index = max(0, min(self._selected_index, len(fans) - 1))
        return fans[self._selected_index]

    def _refresh_all_views(self) -> None:
        fans = self._filtered_fans()
        total_fans = FOLLOWER_GROWTH[-1]
        active_ratio = _safe_ratio(sum(1 for fan in fans if fan.active_days >= 18), len(fans) or 1)
        growth_rate = _safe_ratio(FOLLOWER_GROWTH[-1] - FOLLOWER_GROWTH[-2], FOLLOWER_GROWTH[-2])
        engagement_index = sum(fan.engagement_index for fan in fans) / max(len(fans), 1)
        payload = {
            "总粉丝": (_format_compact(total_fans), _safe_ratio(FOLLOWER_GROWTH[-1] - FOLLOWER_COMPARE[-1], FOLLOWER_COMPARE[-1]), FOLLOWER_GROWTH[-7:]),
            "活跃粉丝比": (_format_percent(active_ratio), active_ratio - 0.53, tuple(int(fan.engagement_index * 100) for fan in fans[:7] or [0, 0, 0, 0, 0, 0, 0])),
            "粉丝增长率": (_format_percent(growth_rate), growth_rate - 0.031, FOLLOWER_COMPARE[-7:]),
            "互动指数": (_format_percent(engagement_index), engagement_index - 0.74, tuple(int(fan.engagement_index * 100) for fan in fans[:7] or [0, 0, 0, 0, 0, 0, 0])),
        }
        for title, card in self._kpi_cards.items():
            value, delta, spark = payload[title]
            card.set_value(value)
            card.set_trend("up" if delta >= 0 else "down", f"{delta * 100:+.1f}%")
            card.set_sparkline_data(spark)
        if self._fan_table is not None:
            self._fan_table.set_rows(self._fan_rows(fans))
            if fans:
                self._fan_table.select_absolute_row(self._selected_index)
        if self._region_table is not None:
            self._region_table.set_rows(self._region_rows())
        if self._age_chart is not None:
            self._age_chart.set_items(tuple(zip(AGE_LABELS, AGE_DISTRIBUTION)))
        if self._gender_chart is not None:
            self._gender_chart.set_items(tuple(zip(GENDER_LABELS, GENDER_DISTRIBUTION)))
        if self._growth_chart is not None:
            self._growth_chart.set_data(FOLLOWER_GROWTH, TREND_LABELS)
            self._growth_chart.set_unit("人")
        if self._activity_heatmap is not None:
            self._activity_heatmap.set_values(ACTIVITY_HEATMAP)
        if self._interest_cloud is not None:
            self._interest_cloud.set_words(INTEREST_WORDS)
        if self._sentiment_gauge is not None:
            self._sentiment_gauge.set_sentiment(min(max((engagement_index - 0.70) * 3.0, -1.0), 1.0))
        self._refresh_playbook_cards(fans)
        self._refresh_segment_cards(fans)
        self._refresh_archetype_cards(fans)
        self._refresh_selection()

    def _refresh_playbook_cards(self, fans: Sequence[FanRecord]) -> None:
        multiplier = 1.0 + min(len(fans), 12) * 0.01
        for index, (_title, _summary, values) in enumerate(TOPIC_PLAYBOOKS):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._playbook_sparklines):
                chart = self._playbook_sparklines[index]
                if chart is not None:
                    chart.set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                    chart.set_unit("%")
            if index < len(self._playbook_value_labels):
                _call(self._playbook_value_labels[index], "setText", f"预计带动互动 {_format_percent(max(adjusted) / 100.0)}")

    def _refresh_segment_cards(self, fans: Sequence[FanRecord]) -> None:
        active_count = sum(1 for fan in fans if fan.active_days >= 18)
        for index, label in enumerate(self._segment_body_labels):
            if index >= len(SEGMENT_INSIGHTS):
                continue
            title, _flag, summary = SEGMENT_INSIGHTS[index]
            _call(label, "setText", f"{summary} 当前样本中约有 {active_count} 位活跃粉丝可归入 {title} 核心分层。")

    def _refresh_archetype_cards(self, fans: Sequence[FanRecord]) -> None:
        multiplier = 1.0 + min(len(fans), 12) * 0.008
        for index, (_name, _summary, values) in enumerate(CREATOR_ARCHETYPES):
            adjusted = tuple(int(value * multiplier) for value in values)
            if index < len(self._archetype_charts):
                self._archetype_charts[index].set_data(adjusted, ("1", "2", "3", "4", "5", "6", "7"))
                self._archetype_charts[index].set_unit("%")

    def _refresh_selection(self) -> None:
        fan = self._selected_fan()
        if fan is None:
            return
        if self._selection_title is not None:
            _call(self._selection_title, "setText", fan.nickname)
        if self._selection_meta is not None:
            _call(self._selection_meta, "setText", f"{fan.creator_type} · {fan.region} · {fan.favorite_topic}")
        if self._selection_body is not None:
            _call(self._selection_body, "setText", f"该粉丝近 {fan.active_days} 天保持高活跃，偏好 {fan.favorite_topic} 内容，建议推送同题材合集与专题内容。")
        badge_values = ((fan.region, "brand"), (fan.spend_level, "success" if "高" in fan.spend_level else "info"), (fan.favorite_topic, "warning"))
        for badge, (text, tone) in zip(self._selection_badges, badge_values):
            _call(badge, "setText", text)
            badge.set_tone(tone)
        values = {
            "互动指数": _format_percent(fan.engagement_index),
            "活跃天数": str(fan.active_days),
            "性别": fan.gender,
            "年龄段": fan.age_bucket,
        }
        for metric, label in self._selection_metrics.items():
            _call(label, "setText", values[metric])

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#audiencePersonasPage {{ background-color: {colors.surface_alt}; }}
            QFrame#audienceToolbar,
            QFrame#audienceDetailCard,
            QFrame#audienceMetricCard,
            QFrame#audiencePlaybookCard,
            QFrame#audienceSegmentCard,
            QFrame#audienceArchetypeCard,
            QFrame#audienceSignalCard,
            QFrame#audienceRegionStoryCard,
            QFrame#audiencePurchaseLadderCard,
            QFrame#audienceRetentionCard,
            QFrame#audienceCommunityCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#audienceToolbar {{
                border-color: {_rgba(_token('brand.primary'), 0.18)};
            }}
            QLabel#audiencePanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#audienceSelectionTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#audienceSubtleText,
            QLabel#audienceMetricTitle {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#audienceMetricValue {{
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            """,
        )

    def on_activated(self) -> None:
        self._refresh_all_views()

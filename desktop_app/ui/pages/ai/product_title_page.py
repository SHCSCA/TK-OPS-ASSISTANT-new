# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""商品标题大师页面。"""

from dataclasses import dataclass
from typing import Any, cast

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    AIStatusIndicator,
    ContentSection,
    DataTable,
    FilterDropdown,
    IconButton,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    PromptEditor,
    SecondaryButton,
    SplitPanel,
    StatsBadge,
    StatusBadge,
    StreamingOutputWidget,
    TabBar,
    TagChip,
    TagInput,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ThemedTextEdit,
    WordCloudWidget,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

ACCENT = "#00F2EA"
ACCENT_SOFT = "rgba(0, 242, 234, 0.10)"
ACCENT_MEDIUM = "rgba(0, 242, 234, 0.16)"
ACCENT_STRONG = "rgba(0, 242, 234, 0.22)"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"
TEXT_MUTED = "#94A3B8"
SURFACE_ALT = "rgba(15, 23, 42, 0.04)"
SURFACE_DARK = "#0F172A"


@dataclass(frozen=True)
class ScoreBreakdown:
    """标题评分拆解。"""

    label: str
    score: str
    detail: str
    tone: BadgeTone


@dataclass(frozen=True)
class DensityMetric:
    """关键词密度项。"""

    keyword: str
    density: str
    benchmark: str
    progress: int
    insight: str
    tone: BadgeTone


@dataclass(frozen=True)
class CompetitorTitle:
    """竞品标题数据。"""

    rank: str
    shop_name: str
    monthly_sales: str
    ctr: str
    score: str
    title: str
    insight: str
    tone: BadgeTone


@dataclass(frozen=True)
class KeywordSuggestion:
    """关键词建议。"""

    keyword: str
    heat: str
    competition: str
    uplift: str
    scenario: str
    tone: BadgeTone


@dataclass(frozen=True)
class ComplianceRule:
    """合规检查项。"""

    rule_name: str
    result: str
    detail: str
    tone: BadgeTone


@dataclass(frozen=True)
class IndustryTemplate:
    """行业模板卡片。"""

    category: str
    focus: str
    formula: str
    suitable_for: str
    example: str
    tone: BadgeTone


@dataclass(frozen=True)
class BulkTitlePlan:
    """批量标题生成结果。"""

    sku: str
    product_name: str
    recommended_title: str
    title_style: str
    score: str
    keyword_coverage: str
    status: str


@dataclass(frozen=True)
class LengthBenchmark:
    """长度参考区间。"""

    label: str
    range_text: str
    note: str
    tone: BadgeTone


@dataclass(frozen=True)
class GenerationVariant:
    """AI 方案卡片。"""

    label: str
    tag: str
    note: str
    title: str
    score: str
    click_uplift: str
    tone: BadgeTone


SEO_SCORE_BREAKDOWN: tuple[ScoreBreakdown, ...] = (
    ScoreBreakdown("核心词布局", "24/25", "主关键词已覆盖标题前 12 字，搜索抓取位置优秀。", "success"),
    ScoreBreakdown("属性词完整度", "18/20", "已带出材质、季节、版型，但尺码词仍可补强。", "brand"),
    ScoreBreakdown("点击吸引力", "17/20", "卖点清晰，建议增加高转化触发词提升点击意愿。", "warning"),
    ScoreBreakdown("平台合规度", "19/20", "未发现绝对化极限词，合规风险较低。", "success"),
    ScoreBreakdown("字符利用率", "13/15", "当前长度适中，仍有 8 字可用于叠加搜索词。", "brand"),
)

KEYWORD_DENSITY_METRICS: tuple[DensityMetric, ...] = (
    DensityMetric("纯棉短袖T恤男", "2.4%", "2.2% - 2.8%", 76, "核心词命中稳定，建议继续保持前置。", "success"),
    DensityMetric("夏季新款", "1.8%", "1.6% - 2.0%", 64, "季节属性词分布合理，适合继续保留。", "brand"),
    DensityMetric("宽松百搭", "1.2%", "1.2% - 1.6%", 52, "风格词覆盖刚达标，可作为第二梯队词。", "brand"),
    DensityMetric("韩版潮流", "0.5%", "0.9% - 1.3%", 22, "修饰词偏弱，建议加入“潮牌感”“国潮”等替代词。", "warning"),
    DensityMetric("重磅透气", "0.9%", "0.8% - 1.1%", 40, "卖点词可提升面料质感认知。", "success"),
    DensityMetric("2026爆款", "0.2%", "0% - 0.3%", 10, "年份词不宜过高，当前占比安全。", "success"),
)

COMPETITOR_TITLES: tuple[CompetitorTitle, ...] = (
    CompetitorTitle(
        "TOP1",
        "森野男装旗舰店",
        "月销 1.8万+",
        "6.7%",
        "95",
        "2026夏季新款重磅纯棉短袖T恤男宽松百搭潮牌圆领半袖上衣",
        "核心词前置+材质词明确，适合搜索与推荐双场景。",
        "success",
    ),
    CompetitorTitle(
        "TOP2",
        "南潮青年服饰",
        "月销 1.4万+",
        "6.1%",
        "92",
        "男士纯棉短袖T恤夏季宽松韩版潮流百搭半袖打底衫潮牌上衣",
        "风格词密度更高，适合偏年轻用户人群。",
        "brand",
    ),
    CompetitorTitle(
        "TOP3",
        "简色生活男装",
        "月销 9800+",
        "5.8%",
        "90",
        "基础款纯棉短袖T恤男夏季透气宽松大码圆领内搭半袖上衣",
        "基础款+大码词提升了更广泛搜索覆盖。",
        "brand",
    ),
    CompetitorTitle(
        "TOP4",
        "初夏衣橱",
        "月销 8200+",
        "5.4%",
        "88",
        "重磅纯棉T恤男短袖2026夏季新款韩版宽松潮流百搭体恤衫",
        "“重磅”“百搭”提升质感与场景感，但排序稍显拥挤。",
        "warning",
    ),
    CompetitorTitle(
        "TOP5",
        "潮范研究所",
        "月销 7600+",
        "5.2%",
        "86",
        "夏季纯棉圆领短袖T恤男潮牌休闲宽松半袖男装上衣",
        "读感顺畅，但缺少强卖点词，转化略受影响。",
        "warning",
    ),
)

KEYWORD_SUGGESTIONS: tuple[KeywordSuggestion, ...] = (
    KeywordSuggestion("重磅纯棉", "高热", "中", "+12.4%", "强调面料厚实感", "success"),
    KeywordSuggestion("透气不闷", "高热", "低", "+9.8%", "夏季场景直击痛点", "success"),
    KeywordSuggestion("宽松显瘦", "高热", "中", "+8.6%", "适合男装宽版型商品", "brand"),
    KeywordSuggestion("潮牌百搭", "中高", "中高", "+7.9%", "提升年轻群体点击兴趣", "brand"),
    KeywordSuggestion("日常通勤", "中", "低", "+6.2%", "增加穿着场景覆盖", "success"),
    KeywordSuggestion("大码友好", "中高", "低", "+8.1%", "拓宽体型搜索用户", "success"),
    KeywordSuggestion("不易变形", "中", "低", "+5.8%", "强化耐穿与品质感", "brand"),
    KeywordSuggestion("情侣同款", "中", "中", "+6.9%", "适合扩展礼赠需求", "warning"),
    KeywordSuggestion("国潮风", "中高", "高", "+5.4%", "适合短视频内容种草", "warning"),
    KeywordSuggestion("短视频爆款", "中高", "高", "+4.9%", "适合短视频转化场景", "warning"),
)

COMPLIANCE_RULES: tuple[ComplianceRule, ...] = (
    ComplianceRule("极限词检查", "通过", "标题未出现“第一”“最强”“顶级”等平台敏感表达。", "success"),
    ComplianceRule("功效承诺检查", "通过", "未发现夸大承诺和不实效果描述。", "success"),
    ComplianceRule("促销承诺检查", "提示", "如加入“短视频专享最低价”需同步活动凭证。", "warning"),
    ComplianceRule("类目词匹配", "通过", "男装/短袖/T恤/纯棉等类目词高度一致。", "success"),
    ComplianceRule("品牌侵权风险", "低风险", "当前标题未引用外部品牌名，侵权风险较低。", "brand"),
)

INDUSTRY_TEMPLATES: tuple[IndustryTemplate, ...] = (
    IndustryTemplate(
        "服饰内衣",
        "材质 + 季节 + 版型 + 场景",
        "夏季新款 + 材质卖点 + 核心品类 + 风格词 + 场景词",
        "男装、女装、内搭、家居服",
        "夏季新款重磅纯棉短袖T恤男宽松百搭通勤半袖上衣",
        "success",
    ),
    IndustryTemplate(
        "数码家电",
        "功能 + 容量 + 使用场景 + 人群",
        "升级功能 + 核心型号 + 使用收益 + 场景补充",
        "蓝牙耳机、小风扇、充电宝",
        "迷你挂脖小风扇超长续航静音便携学生宿舍通勤随身款",
        "brand",
    ),
    IndustryTemplate(
        "美妆护肤",
        "成分 + 功效 + 肤质 + 场景",
        "明星成分 + 主功效 + 肤质词 + 节点场景",
        "精华、面膜、防晒、底妆",
        "烟酰胺提亮精华水油皮清爽保湿夏季熬夜暗沉护理",
        "brand",
    ),
    IndustryTemplate(
        "食品饮料",
        "口味 + 含量 + 人群 + 场景",
        "风味词 + 规格词 + 功能词 + 消费场景",
        "零食、饮品、冲泡、代餐",
        "低糖黑咖啡速溶提神无蔗糖学生上班族便携装",
        "warning",
    ),
    IndustryTemplate(
        "母婴用品",
        "安全性 + 年龄段 + 场景 + 功能",
        "安心材质 + 年龄词 + 核心用途 + 场景补充",
        "辅食、玩具、用品、童装",
        "婴儿硅胶吸盘碗宝宝辅食训练餐具防摔分格易清洗",
        "success",
    ),
    IndustryTemplate(
        "家居百货",
        "功能 + 收纳/清洁痛点 + 使用空间",
        "空间词 + 功能词 + 高频痛点 + 使用人群",
        "收纳盒、拖把、清洁喷雾、厨具",
        "厨房去油污清洁喷雾免拆洗重油渍一喷即净家用装",
        "brand",
    ),
)

BULK_TITLE_PLANS: tuple[BulkTitlePlan, ...] = (
    BulkTitlePlan(
        "TK-TS-001",
        "重磅纯棉圆领短袖男",
        "夏季新款重磅纯棉短袖T恤男宽松百搭透气圆领半袖上衣",
        "高转化型",
        "94",
        "91%",
        "已生成",
    ),
    BulkTitlePlan(
        "TK-TS-002",
        "冰氧吧速干运动T恤",
        "男士速干运动短袖T恤夏季透气跑步健身宽松训练上衣",
        "搜索放大型",
        "91",
        "88%",
        "已生成",
    ),
    BulkTitlePlan(
        "TK-TS-003",
        "情侣款纯色半袖",
        "情侣同款纯色短袖T恤男女宽松百搭夏季圆领打底半袖",
        "人群拓展型",
        "89",
        "84%",
        "待确认",
    ),
    BulkTitlePlan(
        "TK-TS-004",
        "凉感棉短袖POLO",
        "凉感棉短袖POLO衫男夏季商务休闲翻领透气通勤上衣",
        "场景提效型",
        "90",
        "86%",
        "已生成",
    ),
    BulkTitlePlan(
        "TK-TS-005",
        "简约大码落肩T恤",
        "大码落肩短袖T恤男宽松显瘦纯棉潮流百搭半袖上衣",
        "精准人群型",
        "92",
        "90%",
        "已生成",
    ),
    BulkTitlePlan(
        "TK-TS-006",
        "美式复古印花T恤",
        "美式复古印花短袖T恤男潮牌宽松纯棉夏季百搭上衣",
        "风格强化型",
        "90",
        "87%",
        "待确认",
    ),
)

LENGTH_BENCHMARKS: tuple[LengthBenchmark, ...] = (
    LengthBenchmark("短标题引流", "18 - 24 字", "适合短视频口播同步展示，利于快速扫读。", "brand"),
    LengthBenchmark("推荐标准", "28 - 38 字", "搜索与推荐平衡最好，平台抓取完整度高。", "success"),
    LengthBenchmark("SEO 扩展", "39 - 48 字", "适合叠加品类、属性、场景词，提升长尾覆盖。", "success"),
    LengthBenchmark("风险提示", "49 - 60 字", "超过 48 字要重点校验可读性，避免关键词堆砌。", "warning"),
)

GENERATION_VARIANTS: tuple[GenerationVariant, ...] = (
    GenerationVariant(
        "方案一",
        "高转化型",
        "适合详情页广告与主推款。",
        "夏季新款【100%纯棉】重磅男士短袖T恤 宽松百搭透气圆领半袖上衣",
        "96",
        "+18.2%",
        "success",
    ),
    GenerationVariant(
        "方案二",
        "SEO 加强型",
        "适合搜索权重优先和货架流量承接。",
        "纯棉短袖T恤男夏季新款宽松韩版潮流百搭透气半袖上衣",
        "94",
        "+15.6%",
        "brand",
    ),
    GenerationVariant(
        "方案三",
        "风格放大型",
        "适合短视频内容种草与年轻客群点击。",
        "重磅纯棉短袖T恤男美式潮牌宽松落肩夏季百搭半袖上衣",
        "92",
        "+13.8%",
        "warning",
    ),
)

WORD_CLOUD_ENTRIES: tuple[tuple[str, float], ...] = (
    ("纯棉短袖", 98),
    ("透气不闷", 94),
    ("宽松百搭", 90),
    ("重磅面料", 86),
    ("夏季新款", 82),
    ("男士半袖", 76),
    ("潮牌上衣", 72),
    ("大码友好", 69),
    ("日常通勤", 66),
    ("短视频热卖", 63),
    ("显瘦版型", 58),
    ("圆领基础款", 55),
    ("学生党", 49),
    ("情侣同款", 44),
    ("衣橱必备", 40),
)

PROMPT_TEMPLATE = """你是 TikTok Shop 男装类目资深 SEO 标题优化师，请根据以下信息输出 3 个商品标题方案：
1. 标题必须使用中文，控制在 28-48 字内；
2. 核心词前置：纯棉 / 短袖 / T恤 / 男；
3. 至少加入 2 个卖点词和 1 个场景词；
4. 禁止出现绝对化极限词、虚假承诺词；
5. 输出格式：方案标签 + 标题 + 预计提升点。

商品名称：重磅纯棉男士短袖T恤
目标人群：18-30 岁男装消费用户
卖点：纯棉、宽松、透气、百搭、不易变形
核心场景：通勤、出游、日常穿搭、短视频引流
平台：TikTok Shop"""


def _connect(signal_object: object, callback: object) -> None:
    """安全连接 Qt 风格信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _tone_colors(tone: str) -> tuple[str, str]:
    """返回不同语义色。"""

    mapping = {
        "success": (SUCCESS, "rgba(34, 197, 94, 0.10)"),
        "warning": (WARNING, "rgba(245, 158, 11, 0.12)"),
        "error": (ERROR, "rgba(239, 68, 68, 0.10)"),
        "brand": (ACCENT, ACCENT_SOFT),
        "neutral": (TEXT_MUTED, "rgba(148, 163, 184, 0.12)"),
    }
    return mapping.get(tone, (ACCENT, ACCENT_SOFT))


def _set_word_wrap(label: QLabel) -> None:
    """安全启用换行。"""

    method = getattr(label, "setWordWrap", None)
    if callable(method):
        method(True)


class ProductTitlePage(BasePage):
    """商品标题大师主页面。"""

    default_route_id = RouteId("product_title_master")
    default_display_name = "商品标题大师"
    default_icon_name = "auto_fix_high"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._title_limit = 60
        self._seo_title_editor: ThemedLineEdit | None = None
        self._char_count_label: QLabel | None = None
        self._char_hint_label: QLabel | None = None
        self._title_score_value_label: QLabel | None = None
        self._title_grade_badge: StatusBadge | None = None
        self._keyword_coverage_label: QLabel | None = None
        self._ai_config_panel: AIConfigPanel | None = None
        self._ai_config_summary_label: QLabel | None = None
        self._prompt_editor: PromptEditor | None = None
        self._generation_output: StreamingOutputWidget | None = None
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建商品标题大师页面。"""

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        page_container = PageContainer(
            title="商品标题优化助手",
            description="基于 SEO 关键词密度、竞品标题结构、类目模板与 AI 配置，为 TikTok Shop 商品生成更易点击、更易搜索的中文标题。",
            actions=self._build_header_actions(),
            parent=self,
        )
        self.layout.addWidget(page_container)

        page_container.add_widget(self._build_hero_metrics())
        page_container.add_widget(self._build_top_banner())
        page_container.add_widget(self._build_workspace_tabs())
        page_container.add_widget(self._build_footer_stats())
        self._bind_ai_panel()
        self._update_ai_config_summary()

    def _bind_ai_panel(self) -> None:
        if self._ai_config_panel is not None:
            _connect(self._ai_config_panel.config_changed, self._on_ai_config_changed)

    def _on_ai_config_changed(self, _config: dict[str, object]) -> None:
        self._update_ai_config_summary()

    def _build_header_actions(self) -> list[QWidget]:
        dashboard_button = IconButton("⌕", "查看关键词看板", self)
        settings_button = IconButton("⚙", "配置标题策略", self)
        upgrade_button = PrimaryButton("升级专业版", self)
        return [dashboard_button, settings_button, upgrade_button]

    def _build_hero_metrics(self) -> QWidget:
        host = QWidget(self)
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        metric_cards = (
            KPICard(
                title="当前标题评分",
                value="91",
                trend="up",
                percentage="+8.4%",
                caption="较上周标题平均分提升",
                sparkline_data=[68, 72, 74, 79, 83, 88, 91],
                parent=host,
            ),
            KPICard(
                title="长尾关键词覆盖",
                value="36",
                trend="up",
                percentage="+12.1%",
                caption="已覆盖高意向搜索词",
                sparkline_data=[18, 20, 22, 27, 31, 34, 36],
                parent=host,
            ),
            KPICard(
                title="预计点击提升",
                value="+17.3%",
                trend="up",
                percentage="+3.2%",
                caption="对比原始标题预估表现",
                sparkline_data=[7, 8, 9, 11, 13, 15, 17],
                parent=host,
            ),
        )

        for card in metric_cards:
            layout.addWidget(card, 1)
        return host

    def _build_top_banner(self) -> QWidget:
        banner = QFrame(self)
        banner.setStyleSheet(
            f"""
            QFrame {{
                background-color: {SURFACE_DARK};
                border: 1px solid {ACCENT_STRONG};
                border-radius: 20px;
            }}
            QLabel {{
                background: transparent;
                color: white;
            }}
            QPushButton {{
                min-height: 40px;
            }}
            """
        )

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        text_column = QVBoxLayout()
        text_column.setSpacing(8)

        title = QLabel("AI 标题优化工作台已就绪", banner)
        title.setStyleSheet("font-size: 24px; font-weight: 800;")

        desc = QLabel(
            "已载入男装类目模板、热搜关键词云和 TOP 竞品结构。输入原始标题后，可一键生成高转化型、SEO 加强型、风格放大型方案。",
            banner,
        )
        _set_word_wrap(desc)
        desc.setStyleSheet(f"font-size: 13px; color: rgba(255, 255, 255, 0.72);")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)
        badge_row.addWidget(TagChip("快速生成", tone="brand", parent=banner))
        badge_row.addWidget(TagChip("关键词密度分析", tone="success", parent=banner))
        badge_row.addWidget(TagChip("合规预警", tone="warning", parent=banner))
        badge_row.addWidget(TagChip("竞品标题拆解", tone="brand", parent=banner))
        badge_row.addStretch(1)

        text_column.addWidget(title)
        text_column.addWidget(desc)
        text_column.addLayout(badge_row)

        right_column = QVBoxLayout()
        right_column.setSpacing(10)
        right_column.addWidget(StatsBadge("已节省时长", "124 小时", "◎", "brand", banner))
        right_column.addWidget(StatsBadge("模板总数", "156 套", "◔", "success", banner))
        right_column.addWidget(StatsBadge("平均点击提升", "+34.2%", "▲", "warning", banner))

        layout.addLayout(text_column, 1)
        layout.addLayout(right_column)
        return banner

    def _build_workspace_tabs(self) -> QWidget:
        tabs = TabBar(self)
        tabs.add_tab("标题优化", self._build_optimization_tab())
        tabs.add_tab("关键词密度", self._build_density_tab())
        tabs.add_tab("竞品对比", self._build_competitor_tab())
        tabs.add_tab("批量生成", self._build_bulk_tab())
        return tabs

    def _build_optimization_tab(self) -> QWidget:
        split = SplitPanel(orientation="horizontal", split_ratio=(0.66, 0.34), minimum_sizes=(680, 360), parent=self)
        split.set_widgets(self._build_optimization_main_panel(), self._build_ai_sidebar_panel())
        return split

    def _build_optimization_main_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        host = QWidget(scroll)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._build_title_editor_section())
        layout.addWidget(self._build_score_overview_section())
        layout.addWidget(self._build_generation_section())
        layout.addWidget(self._build_keyword_suggestion_section())
        layout.addWidget(self._build_length_benchmark_section())
        layout.addStretch(1)

        scroll.set_content_widget(host)
        return scroll

    def _build_ai_sidebar_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        host = QWidget(scroll)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._build_ai_status_card())
        layout.addWidget(self._build_ai_config_card())
        layout.addWidget(self._build_prompt_editor_card())
        layout.addWidget(self._build_compliance_section())
        layout.addWidget(self._build_template_section())
        layout.addStretch(1)

        scroll.set_content_widget(host)
        return scroll

    def _build_title_editor_section(self) -> QWidget:
        section = ContentSection("SEO 标题编辑器", "✦", parent=self)

        intro = InfoCard(
            title="先输入原始标题，再叠加核心搜索词",
            description="建议结构：季节词 / 材质词 / 品类词 / 版型词 / 场景词。核心词尽量前置，避免卖点堆叠导致读感割裂。",
            icon="◉",
            action_text="查看优化规则",
            parent=section,
        )
        section.add_widget(intro)

        editor_card = QFrame(section)
        editor_card.setStyleSheet(self._card_style())
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(18, 18, 18, 18)
        editor_layout.setSpacing(14)

        product_name_input = ThemedLineEdit(
            "商品原始名称", "请输入商品原始名称", "便于 AI 理解基础品类和卖点。", cast(Any, editor_card)
        )
        product_name_input.setText("夏季新款纯棉短袖T恤男装韩版潮牌")

        seo_title_editor = ThemedLineEdit(
            "当前 SEO 标题",
            "请输入优化前标题",
            "建议将核心品类词放在前半段，优先覆盖高搜索意图词。",
            cast(Any, editor_card),
        )
        seo_title_editor.setText("夏季新款重磅纯棉短袖T恤男宽松百搭透气圆领半袖上衣")
        self._seo_title_editor = seo_title_editor

        benefit_editor = ThemedTextEdit("卖点拆解", "请输入主要卖点", cast(Any, editor_card))
        benefit_editor.setPlainText(
            "1. 100% 纯棉面料，贴身舒适\n"
            "2. 重磅克重，穿着更有型\n"
            "3. 宽松版型，显瘦且适合通勤/出游\n"
            "4. 面料透气，不易闷热\n"
            "5. 百搭圆领，适合作为主推款和短视频种草"
        )

        tag_input = TagInput("目标关键词池", "输入关键词后按回车", cast(Any, editor_card))
        tag_input.set_tags([
            "纯棉短袖T恤男",
            "夏季新款",
            "宽松百搭",
            "透气半袖",
            "潮牌上衣",
            "重磅纯棉",
        ])

        strategy_row = QWidget(editor_card)
        strategy_layout = QHBoxLayout(strategy_row)
        strategy_layout.setContentsMargins(0, 0, 0, 0)
        strategy_layout.setSpacing(12)

        category_combo = ThemedComboBox(
            "行业模板", ["服饰内衣", "数码家电", "美妆护肤", "食品饮料", "家居百货"], cast(Any, strategy_row)
        )
        scene_combo = ThemedComboBox(
            "优化目标", ["搜索权重优先", "高点击率优先", "短视频转化优先", "人群覆盖优先"], cast(Any, strategy_row)
        )
        style_combo = ThemedComboBox(
            "文案风格", ["高转化型", "SEO 加强型", "风格放大型", "基础稳健型"], cast(Any, strategy_row)
        )
        strategy_layout.addWidget(category_combo, 1)
        strategy_layout.addWidget(scene_combo, 1)
        strategy_layout.addWidget(style_combo, 1)

        indicator_card = self._build_title_indicator_card(editor_card)
        action_row = self._build_editor_action_row(editor_card)

        editor_layout.addWidget(product_name_input)
        editor_layout.addWidget(seo_title_editor)
        editor_layout.addWidget(benefit_editor)
        editor_layout.addWidget(tag_input)
        editor_layout.addWidget(strategy_row)
        editor_layout.addWidget(indicator_card)
        editor_layout.addWidget(action_row)

        section.add_widget(editor_card)

        if self._seo_title_editor is not None:
            _connect(self._seo_title_editor.line_edit.textChanged, self._handle_title_text_changed)
            self._handle_title_text_changed(self._seo_title_editor.text())

        return section

    def _build_title_indicator_card(self, parent: QWidget) -> QWidget:
        card = QFrame(parent)
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {SURFACE_ALT};
                border: 1px solid {ACCENT_SOFT};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
            }}
            """
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        count_column = QVBoxLayout()
        count_column.setSpacing(4)
        count_title = QLabel("字符长度", card)
        count_title.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; font-weight: 600;")
        self._char_count_label = QLabel("0 / 60", card)
        char_count_label = self._char_count_label
        if char_count_label is not None:
            char_count_label.setStyleSheet("font-size: 24px; font-weight: 800;")
        self._char_hint_label = QLabel("推荐控制在 28 - 48 字之间。", card)
        char_hint_label = self._char_hint_label
        if char_hint_label is not None:
            char_hint_label.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        count_column.addWidget(count_title)
        if char_count_label is not None:
            count_column.addWidget(char_count_label)
        if char_hint_label is not None:
            count_column.addWidget(char_hint_label)

        score_column = QVBoxLayout()
        score_column.setSpacing(6)
        score_title = QLabel("标题评分", card)
        score_title.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; font-weight: 600;")
        score_value_row = QHBoxLayout()
        score_value_row.setSpacing(8)
        self._title_score_value_label = QLabel("91", card)
        title_score_value_label = self._title_score_value_label
        if title_score_value_label is not None:
            title_score_value_label.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {ACCENT};")
        self._title_grade_badge = StatusBadge("A级", tone="success", parent=card)
        if title_score_value_label is not None:
            score_value_row.addWidget(title_score_value_label)
        if self._title_grade_badge is not None:
            score_value_row.addWidget(self._title_grade_badge)
        score_value_row.addStretch(1)
        self._keyword_coverage_label = QLabel("核心词覆盖 5/6，搜索抓取位置优秀。", card)
        keyword_coverage_label = self._keyword_coverage_label
        if keyword_coverage_label is not None:
            keyword_coverage_label.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        score_column.addWidget(score_title)
        score_column.addLayout(score_value_row)
        if keyword_coverage_label is not None:
            score_column.addWidget(keyword_coverage_label)

        right_tips = QVBoxLayout()
        right_tips.setSpacing(8)
        right_tips.addWidget(StatsBadge("推荐长度", "28-48 字", "◎", "success", card))
        right_tips.addWidget(StatsBadge("风险提醒", "低风险", "◔", "brand", card))

        layout.addLayout(count_column, 1)
        layout.addLayout(score_column, 1)
        layout.addLayout(right_tips)
        return card

    def _build_editor_action_row(self, parent: QWidget) -> QWidget:
        host = QWidget(parent)
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        optimize_button = PrimaryButton("立即优化标题", host)
        regenerate_button = SecondaryButton("重新生成一批", host)
        compare_button = SecondaryButton("同步竞品对比", host)
        compliance_badge = StatusBadge("合规检测已开启", tone="success", parent=host)

        layout.addWidget(optimize_button)
        layout.addWidget(regenerate_button)
        layout.addWidget(compare_button)
        layout.addStretch(1)
        layout.addWidget(compliance_badge)
        return host

    def _build_score_overview_section(self) -> QWidget:
        section = ContentSection("标题得分拆解", "◎", parent=self)

        score_row = QWidget(section)
        score_layout = QHBoxLayout(score_row)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.setSpacing(12)
        score_layout.addWidget(
            KPICard(
                title="SEO 综合评分",
                value="91 / 100",
                trend="up",
                percentage="+6.9%",
                caption="结构完整度继续提升",
                sparkline_data=[71, 74, 76, 80, 84, 88, 91],
                parent=score_row,
            ),
            1,
        )
        score_layout.addWidget(
            KPICard(
                title="关键词命中率",
                value="83%",
                trend="up",
                percentage="+11.4%",
                caption="目标关键词覆盖更集中",
                sparkline_data=[42, 49, 56, 61, 70, 78, 83],
                parent=score_row,
            ),
            1,
        )
        score_layout.addWidget(
            KPICard(
                title="可读性指数",
                value="A 级",
                trend="flat",
                percentage="稳定",
                caption="标题节奏自然，阅读阻力较低",
                sparkline_data=[85, 84, 83, 84, 85, 85, 85],
                parent=score_row,
            ),
            1,
        )

        breakdown_card = QFrame(section)
        breakdown_card.setStyleSheet(self._card_style())
        breakdown_layout = QVBoxLayout(breakdown_card)
        breakdown_layout.setContentsMargins(18, 18, 18, 18)
        breakdown_layout.setSpacing(12)

        title = QLabel("评分细项", breakdown_card)
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        breakdown_layout.addWidget(title)

        for item in SEO_SCORE_BREAKDOWN:
            breakdown_layout.addWidget(self._build_breakdown_row(item, breakdown_card))

        section.add_widget(score_row)
        section.add_widget(breakdown_card)
        return section

    def _build_breakdown_row(self, item: ScoreBreakdown, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(item.tone)
        row = QFrame(parent)
        row.setStyleSheet(
            f"""
            QFrame {{
                background-color: {tone_bg};
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
            }}
            """
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(4)
        label = QLabel(item.label, row)
        label.setStyleSheet("font-size: 14px; font-weight: 700;")
        detail = QLabel(item.detail, row)
        detail.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(detail)
        left.addWidget(label)
        left.addWidget(detail)

        score = QLabel(item.score, row)
        score.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {tone_color};")

        layout.addLayout(left, 1)
        layout.addWidget(score)
        return row

    def _build_generation_section(self) -> QWidget:
        section = ContentSection("AI 优化标题方案", "⚡", parent=self)

        self._generation_output = StreamingOutputWidget(section)
        self._generation_output.set_loading(False)
        self._generation_output.set_token_usage(862, 496)
        self._generation_output.append_chunk(
            "方案一｜高转化型\n"
            "夏季新款【100%纯棉】重磅男士短袖T恤 宽松百搭透气圆领半袖上衣\n"
            "预计提升点：核心词前置 + 卖点词明确，适合搜索与推荐双场景。\n\n"
        )
        self._generation_output.append_chunk(
            "方案二｜SEO 加强型\n"
            "纯棉短袖T恤男夏季新款宽松韩版潮流百搭透气半袖上衣\n"
            "预计提升点：品类词密度更集中，有利于长尾检索覆盖。\n\n"
        )
        self._generation_output.append_chunk(
            "方案三｜风格放大型\n"
            "重磅纯棉短袖T恤男美式潮牌宽松落肩夏季百搭半袖上衣\n"
            "预计提升点：更适合短视频内容种草和年轻用户点击。"
        )

        variant_host = QWidget(section)
        variant_layout = QVBoxLayout(variant_host)
        variant_layout.setContentsMargins(0, 0, 0, 0)
        variant_layout.setSpacing(12)
        for variant in GENERATION_VARIANTS:
            variant_layout.addWidget(self._build_variant_card(variant, variant_host))

        section.add_widget(self._generation_output)
        section.add_widget(variant_host)
        return section

    def _build_variant_card(self, variant: GenerationVariant, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(variant.tone)
        card = QFrame(parent)
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {SURFACE_DARK};
                border: 1px solid {tone_bg};
                border-radius: 18px;
            }}
            QLabel {{
                background: transparent;
                color: white;
            }}
            QPushButton {{
                min-height: 36px;
                border-radius: 10px;
                padding: 8px 14px;
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.08);
                font-weight: 700;
            }}
            """
        )
        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        text_column = QVBoxLayout()
        text_column.setSpacing(8)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        tag = QLabel(f"{variant.label} · {variant.tag}", card)
        tag.setStyleSheet(
            f"background-color: {tone_bg}; color: {tone_color}; border-radius: 8px; padding: 4px 8px; font-size: 11px; font-weight: 800;"
        )
        note = QLabel(variant.note, card)
        note.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.65);")
        meta_row.addWidget(tag)
        meta_row.addWidget(note)
        meta_row.addStretch(1)

        title = QLabel(variant.title, card)
        title.setStyleSheet("font-size: 17px; font-weight: 700; line-height: 1.5;")
        _set_word_wrap(title)

        stat_row = QHBoxLayout()
        stat_row.setSpacing(12)
        stat_row.addWidget(TagChip(f"评分 {variant.score}", tone=variant.tone, parent=card))
        stat_row.addWidget(TagChip(f"预计点击提升 {variant.click_uplift}", tone="success", parent=card))
        stat_row.addStretch(1)

        text_column.addLayout(meta_row)
        text_column.addWidget(title)
        text_column.addLayout(stat_row)

        action_column = QVBoxLayout()
        action_column.setSpacing(8)
        action_column.addWidget(SecondaryButton("复制标题", card))
        action_column.addWidget(SecondaryButton("设为主标题", card))
        action_column.addStretch(1)

        layout.addLayout(text_column, 1)
        layout.addLayout(action_column)
        return card

    def _build_keyword_suggestion_section(self) -> QWidget:
        section = ContentSection("关键词建议与可视化", "⌕", parent=self)

        content = QFrame(section)
        content.setStyleSheet(self._card_style())
        layout = QVBoxLayout(content)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        top_row = QWidget(content)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(14)

        cloud = WordCloudWidget(top_row, WORD_CLOUD_ENTRIES)
        top_layout.addWidget(cloud, 1)

        suggestion_panel = QFrame(top_row)
        suggestion_panel.setStyleSheet(self._inner_panel_style())
        suggestion_layout = QVBoxLayout(suggestion_panel)
        suggestion_layout.setContentsMargins(14, 14, 14, 14)
        suggestion_layout.setSpacing(10)

        suggestion_title = QLabel("优先补强词", suggestion_panel)
        suggestion_title.setStyleSheet("font-size: 15px; font-weight: 800;")
        suggestion_layout.addWidget(suggestion_title)

        for item in KEYWORD_SUGGESTIONS[:6]:
            suggestion_layout.addWidget(self._build_keyword_suggestion_row(item, suggestion_panel))

        suggestion_layout.addStretch(1)
        top_layout.addWidget(suggestion_panel, 1)

        chip_wrap = QWidget(content)
        chip_layout = QHBoxLayout(chip_wrap)
        chip_layout.setContentsMargins(0, 0, 0, 0)
        chip_layout.setSpacing(8)
        for item in KEYWORD_SUGGESTIONS:
            chip_layout.addWidget(TagChip(item.keyword, tone=item.tone, parent=chip_wrap))
        chip_layout.addStretch(1)

        layout.addWidget(top_row)
        layout.addWidget(chip_wrap)
        section.add_widget(content)
        return section

    def _build_keyword_suggestion_row(self, item: KeywordSuggestion, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(item.tone)
        row = QFrame(parent)
        row.setStyleSheet(
            f"""
            QFrame {{
                background-color: {tone_bg};
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 12px;
            }}
            QLabel {{
                background: transparent;
            }}
            """
        )
        layout = QVBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        keyword = QLabel(item.keyword, row)
        keyword.setStyleSheet("font-size: 13px; font-weight: 800;")
        uplift = QLabel(item.uplift, row)
        uplift.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {tone_color};")
        top.addWidget(keyword)
        top.addStretch(1)
        top.addWidget(uplift)

        desc = QLabel(f"热度：{item.heat} · 竞争度：{item.competition} · 场景：{item.scenario}", row)
        desc.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(desc)

        layout.addLayout(top)
        layout.addWidget(desc)
        return row

    def _build_length_benchmark_section(self) -> QWidget:
        section = ContentSection("标题长度与结构参考", "▣", parent=self)

        host = QFrame(section)
        host.setStyleSheet(self._card_style())
        layout = QVBoxLayout(host)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("字符区间建议", host)
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        layout.addWidget(title)

        for benchmark in LENGTH_BENCHMARKS:
            layout.addWidget(self._build_length_benchmark_row(benchmark, host))

        tip = QLabel(
            "推荐标题结构：季节词 → 材质词 → 核心品类词 → 版型/风格词 → 场景/卖点词。优先保证前 20 字覆盖最强搜索词。",
            host,
        )
        tip.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; line-height: 1.7;")
        _set_word_wrap(tip)
        layout.addWidget(tip)

        section.add_widget(host)
        return section

    def _build_length_benchmark_row(self, benchmark: LengthBenchmark, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(benchmark.tone)
        row = QFrame(parent)
        row.setStyleSheet(
            f"background-color: {tone_bg}; border: 1px solid rgba(255,255,255,0.04); border-radius: 12px;"
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        label = QLabel(benchmark.label, row)
        label.setStyleSheet("font-size: 13px; font-weight: 800;")
        range_text = QLabel(benchmark.range_text, row)
        range_text.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {tone_color};")
        note = QLabel(benchmark.note, row)
        note.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(note)

        layout.addWidget(label)
        layout.addWidget(range_text)
        layout.addWidget(note, 1)
        return row

    def _build_ai_status_card(self) -> QWidget:
        card = QFrame(self)
        card.setStyleSheet(self._card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("优化引擎状态", card)
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        desc = QLabel("当前模型、生成配额和词库状态如下：", card)
        desc.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")

        status = AIStatusIndicator(card)
        status.set_status("就绪")

        badge_row = QWidget(card)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(8)
        badge_layout.addWidget(StatsBadge("词库覆盖", "2,480+", "◎", "brand", badge_row))
        badge_layout.addWidget(StatsBadge("竞品监控", "36 店铺", "◔", "success", badge_row))
        badge_layout.addWidget(StatsBadge("今日分析", "8.9万", "▲", "warning", badge_row))

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(status)
        layout.addWidget(badge_row)
        return card

    def _build_ai_config_card(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._ai_config_panel = AIConfigPanel(host)
        self._ai_config_panel.set_config(
            {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "agent_role": "SEO优化师",
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9,
            }
        )

        summary_card = QFrame(host)
        summary_card.setStyleSheet(self._inner_panel_style())
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(6)

        summary_title = QLabel("当前模型摘要", summary_card)
        summary_title.setStyleSheet("font-size: 13px; font-weight: 800;")
        self._ai_config_summary_label = QLabel("等待同步 AI 配置…", summary_card)
        ai_config_summary_label = self._ai_config_summary_label
        if ai_config_summary_label is not None:
            ai_config_summary_label.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
            _set_word_wrap(ai_config_summary_label)

        summary_layout.addWidget(summary_title)
        if ai_config_summary_label is not None:
            summary_layout.addWidget(ai_config_summary_label)

        tip = InfoCard(
            title="推荐参数",
            description="标题优化建议使用中等温度，确保关键词稳定覆盖；批量生成可切换更快模型降低耗时。",
            icon="◈",
            action_text="应用推荐配置",
            parent=host,
        )

        layout.addWidget(self._ai_config_panel)
        layout.addWidget(summary_card)
        layout.addWidget(tip)
        return host

    def _build_prompt_editor_card(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._prompt_editor = PromptEditor(host)
        self._prompt_editor.set_text(PROMPT_TEMPLATE)
        layout.addWidget(self._prompt_editor)
        return host

    def _build_compliance_section(self) -> QWidget:
        section = ContentSection("标题合规检查", "✓", parent=self)

        card = QFrame(section)
        card.setStyleSheet(self._card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("平台风险扫描结果", card)
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        layout.addWidget(title)

        for rule in COMPLIANCE_RULES:
            layout.addWidget(self._build_compliance_row(rule, card))

        section.add_widget(card)
        return section

    def _build_compliance_row(self, rule: ComplianceRule, parent: QWidget) -> QWidget:
        row = QFrame(parent)
        row.setStyleSheet(self._inner_panel_style())
        layout = QVBoxLayout(row)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        rule_name = QLabel(rule.rule_name, row)
        rule_name.setStyleSheet("font-size: 13px; font-weight: 800;")
        status = StatusBadge(rule.result, tone=rule.tone, parent=row)
        top.addWidget(rule_name)
        top.addStretch(1)
        top.addWidget(status)

        detail = QLabel(rule.detail, row)
        detail.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(detail)

        layout.addLayout(top)
        layout.addWidget(detail)
        return row

    def _update_ai_config_summary(self) -> None:
        if self._ai_config_panel is None or self._ai_config_summary_label is None:
            return
        config = self._ai_config_panel.config()
        self._ai_config_summary_label.setText(
            f"{config['provider_label']} · {config['model']} · {config['agent_role']} · 温度 {config['temperature']}"
            f" · Top-p {config['top_p']} · 输出上限 {config['max_tokens']} Token。"
            "当前配置更适合 SEO 标题精修、关键词扩展与批量标题首稿生成。"
        )

    def on_activated(self) -> None:
        self._update_ai_config_summary()

    def _build_template_section(self) -> QWidget:
        section = ContentSection("行业专属模板", "▤", parent=self)

        host = QFrame(section)
        host.setStyleSheet(self._card_style())
        layout = QVBoxLayout(host)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("类目模板建议", host)
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        desc = QLabel("根据不同类目选择标题结构模板，可提升整体搜索匹配度与点击清晰度。", host)
        desc.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(desc)
        layout.addWidget(title)
        layout.addWidget(desc)

        for template in INDUSTRY_TEMPLATES:
            layout.addWidget(self._build_template_card(template, host))

        section.add_widget(host)
        return section

    def _build_template_card(self, template: IndustryTemplate, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(template.tone)
        card = QFrame(parent)
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {tone_bg};
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 14px;
            }}
            QLabel {{ background: transparent; }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(8)
        category = QLabel(template.category, card)
        category.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {tone_color};")
        suitable = QLabel(template.suitable_for, card)
        suitable.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        top.addWidget(category)
        top.addStretch(1)
        top.addWidget(suitable)

        focus = QLabel(f"优化重点：{template.focus}", card)
        focus.setStyleSheet("font-size: 12px; font-weight: 700;")
        formula = QLabel(f"模板公式：{template.formula}", card)
        formula.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        example = QLabel(f"示例标题：{template.example}", card)
        example.setStyleSheet("font-size: 12px; font-weight: 600;")
        _set_word_wrap(focus)
        _set_word_wrap(formula)
        _set_word_wrap(example)

        layout.addLayout(top)
        layout.addWidget(focus)
        layout.addWidget(formula)
        layout.addWidget(example)
        return card

    def _build_density_tab(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        host = QWidget(scroll)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._build_density_overview_section())
        layout.addWidget(self._build_density_metrics_section())
        layout.addWidget(self._build_density_insights_section())
        layout.addStretch(1)

        scroll.set_content_widget(host)
        return scroll

    def _build_density_overview_section(self) -> QWidget:
        section = ContentSection("关键词密度总览", "▦", parent=self)

        row = QWidget(section)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(
            KPICard(
                title="核心词密度",
                value="2.4%",
                trend="up",
                percentage="推荐区间内",
                caption="“纯棉短袖T恤男”表现稳定",
                sparkline_data=[1.5, 1.8, 1.9, 2.0, 2.2, 2.3, 2.4],
                parent=row,
            ),
            1,
        )
        layout.addWidget(
            KPICard(
                title="属性词完整度",
                value="87%",
                trend="up",
                percentage="+9.3%",
                caption="材质 / 季节 / 版型词齐全",
                sparkline_data=[52, 60, 66, 71, 78, 83, 87],
                parent=row,
            ),
            1,
        )
        layout.addWidget(
            KPICard(
                title="堆砌风险指数",
                value="低",
                trend="flat",
                percentage="稳定",
                caption="当前可读性未受明显影响",
                sparkline_data=[19, 17, 16, 15, 15, 14, 14],
                parent=row,
            ),
            1,
        )

        section.add_widget(row)
        return section

    def _build_density_metrics_section(self) -> QWidget:
        section = ContentSection("关键词密度分析器", "◫", parent=self)

        card = QFrame(section)
        card.setStyleSheet(self._card_style())
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("各类关键词当前分布", card)
        title.setStyleSheet("font-size: 16px; font-weight: 800;")
        layout.addWidget(title)

        for metric in KEYWORD_DENSITY_METRICS:
            layout.addWidget(self._build_density_row(metric, card))

        layout.addWidget(WordCloudWidget(card, WORD_CLOUD_ENTRIES))
        section.add_widget(card)
        return section

    def _build_density_row(self, metric: DensityMetric, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(metric.tone)
        row = QFrame(parent)
        row.setStyleSheet(
            f"QFrame {{ background-color: {tone_bg}; border: 1px solid rgba(255,255,255,0.04); border-radius: 14px; }} QLabel {{ background: transparent; }}"
        )
        layout = QVBoxLayout(row)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)
        keyword = QLabel(metric.keyword, row)
        keyword.setStyleSheet("font-size: 13px; font-weight: 800;")
        density = QLabel(f"{metric.density} · 推荐 {metric.benchmark}", row)
        density.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {tone_color};")
        header.addWidget(keyword)
        header.addStretch(1)
        header.addWidget(density)

        progress_track = QFrame(row)
        progress_track.setStyleSheet("background-color: rgba(148,163,184,0.14); border-radius: 6px;")
        progress_layout = QVBoxLayout(progress_track)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)

        progress_fill = QFrame(progress_track)
        progress_fill.setStyleSheet(
            f"background-color: {tone_color}; border-radius: 6px; min-height: 8px; max-height: 8px; min-width: {max(metric.progress * 3, 8)}px;"
        )
        progress_layout.addWidget(progress_fill)

        insight = QLabel(metric.insight, row)
        insight.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(insight)

        layout.addLayout(header)
        layout.addWidget(progress_track)
        layout.addWidget(insight)
        return row

    def _build_density_insights_section(self) -> QWidget:
        section = ContentSection("密度优化建议", "▲", parent=self)

        host = QFrame(section)
        host.setStyleSheet(self._card_style())
        layout = QVBoxLayout(host)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(
            InfoCard(
                title="建议优先补强“韩版潮流”类风格词",
                description="当前标题偏重材质与基础属性，若希望提升年轻流量点击，可补入“美式”“潮牌”“国潮”“宽版”等风格词，但注意不要牺牲可读性。",
                icon="◌",
                action_text="一键插入推荐词",
                parent=host,
            )
        )
        layout.addWidget(
            InfoCard(
                title="场景词建议增加“通勤/出游/日常”",
                description="场景词可以承接内容种草流量，有利于系统理解适用人群与穿搭场景，提升推荐匹配效率。",
                icon="◈",
                action_text="查看场景词库",
                parent=host,
            )
        )
        section.add_widget(host)
        return section

    def _build_competitor_tab(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        host = QWidget(scroll)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._build_competitor_filter_bar())
        layout.addWidget(self._build_competitor_table_section())
        layout.addWidget(self._build_competitor_cards_section())
        layout.addStretch(1)

        scroll.set_content_widget(host)
        return scroll

    def _build_competitor_filter_bar(self) -> QWidget:
        bar = QFrame(self)
        bar.setStyleSheet(self._card_style())
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        category = FilterDropdown(
            "类目筛选", ["服饰内衣", "男装", "短袖T恤", "休闲上衣"], include_all=False, parent=cast(Any, bar)
        )
        period = FilterDropdown(
            "时间窗口", ["近 7 天", "近 15 天", "近 30 天"], include_all=False, parent=cast(Any, bar)
        )
        style = FilterDropdown(
            "风格偏好", ["高销量型", "高点击型", "SEO 型", "短视频爆发型"], include_all=False, parent=cast(Any, bar)
        )
        refresh = PrimaryButton("刷新竞品样本", bar)

        layout.addWidget(category, 1)
        layout.addWidget(period, 1)
        layout.addWidget(style, 1)
        layout.addWidget(refresh)
        return bar

    def _build_competitor_table_section(self) -> QWidget:
        section = ContentSection("竞品标题对比表", "⇄", parent=self)

        rows = [
            [
                item.rank,
                item.shop_name,
                item.monthly_sales,
                item.ctr,
                item.score,
                item.title,
                item.insight,
            ]
            for item in COMPETITOR_TITLES
        ]
        table = DataTable(
            headers=["排名", "店铺", "月销", "点击率", "评分", "标题", "洞察"],
            rows=rows,
            page_size=10,
            empty_text="暂无竞品标题数据",
            parent=section,
        )
        section.add_widget(table)
        return section

    def _build_competitor_cards_section(self) -> QWidget:
        section = ContentSection("竞品结构拆解", "▧", parent=self)

        host = QWidget(section)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        for item in COMPETITOR_TITLES:
            layout.addWidget(self._build_competitor_card(item, host))

        section.add_widget(host)
        return section

    def _build_competitor_card(self, item: CompetitorTitle, parent: QWidget) -> QWidget:
        tone_color, tone_bg = _tone_colors(item.tone)
        card = QFrame(parent)
        card.setStyleSheet(
            f"QFrame {{ background-color: {tone_bg}; border: 1px solid rgba(255,255,255,0.04); border-radius: 16px; }} QLabel {{ background: transparent; }}"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(8)
        shop = QLabel(f"{item.rank} · {item.shop_name}", card)
        shop.setStyleSheet("font-size: 14px; font-weight: 800;")
        status = StatusBadge(f"评分 {item.score}", tone=item.tone, parent=card)
        top.addWidget(shop)
        top.addStretch(1)
        top.addWidget(status)

        metrics = QLabel(f"{item.monthly_sales} · 点击率 {item.ctr}", card)
        metrics.setStyleSheet(f"font-size: 12px; color: {tone_color}; font-weight: 700;")
        title = QLabel(item.title, card)
        title.setStyleSheet("font-size: 14px; font-weight: 700; line-height: 1.6;")
        _set_word_wrap(title)
        insight = QLabel(item.insight, card)
        insight.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        _set_word_wrap(insight)

        layout.addLayout(top)
        layout.addWidget(metrics)
        layout.addWidget(title)
        layout.addWidget(insight)
        return card

    def _build_bulk_tab(self) -> QWidget:
        split = SplitPanel(orientation="horizontal", split_ratio=(0.48, 0.52), minimum_sizes=(420, 520), parent=self)
        split.set_widgets(self._build_bulk_input_panel(), self._build_bulk_result_panel())
        return split

    def _build_bulk_input_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        host = QWidget(scroll)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        section = ContentSection("批量标题生成", "▥", parent=host)

        card = QFrame(section)
        card.setStyleSheet(self._card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(14)

        batch_input = ThemedTextEdit("批量商品清单", "每行一个商品，或使用 SKU + 商品名 格式", cast(Any, card))
        batch_input.setPlainText(
            "TK-TS-001｜重磅纯棉圆领短袖男\n"
            "TK-TS-002｜冰氧吧速干运动T恤\n"
            "TK-TS-003｜情侣款纯色半袖\n"
            "TK-TS-004｜凉感棉短袖POLO\n"
            "TK-TS-005｜简约大码落肩T恤\n"
            "TK-TS-006｜美式复古印花T恤"
        )

        mode_row = QWidget(card)
        mode_layout = QHBoxLayout(mode_row)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(12)
        mode_layout.addWidget(
            ThemedComboBox("生成策略", ["高转化型", "SEO 加强型", "场景提效型", "风格强化型"], cast(Any, mode_row)),
            1,
        )
        mode_layout.addWidget(
            ThemedComboBox("输出条数", ["每个商品 1 条", "每个商品 3 条", "每个商品 5 条"], cast(Any, mode_row)),
            1,
        )

        button_row = QWidget(card)
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addWidget(PrimaryButton("开始批量生成", button_row))
        button_layout.addWidget(SecondaryButton("导出 Excel", button_row))
        button_layout.addWidget(SecondaryButton("同步到草稿箱", button_row))
        button_layout.addStretch(1)
        button_layout.addWidget(StatusBadge("队列空闲", tone="success", parent=button_row))

        card_layout.addWidget(batch_input)
        card_layout.addWidget(mode_row)
        card_layout.addWidget(button_row)
        section.add_widget(card)

        layout.addWidget(section)
        layout.addWidget(
            InfoCard(
                title="批量生成建议",
                description="建议先生成 1 条主标题，再批量扩展搜索型和风格型标题。高相似标题可按店铺或场景拆分，避免全量标题雷同。",
                icon="◎",
                action_text="查看批量策略",
                parent=host,
            )
        )
        layout.addStretch(1)
        scroll.set_content_widget(host)
        return scroll

    def _build_bulk_result_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        host = QWidget(scroll)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        summary_row = QWidget(host)
        summary_layout = QHBoxLayout(summary_row)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(12)
        summary_layout.addWidget(StatsBadge("已生成", "6 条", "◎", "success", summary_row))
        summary_layout.addWidget(StatsBadge("待确认", "2 条", "◔", "warning", summary_row))
        summary_layout.addWidget(StatsBadge("平均评分", "91", "▲", "brand", summary_row))
        summary_layout.addStretch(1)

        table_rows = [
            [
                item.sku,
                item.product_name,
                item.recommended_title,
                item.title_style,
                item.score,
                item.keyword_coverage,
                item.status,
            ]
            for item in BULK_TITLE_PLANS
        ]
        result_table = DataTable(
            headers=["SKU", "商品名", "推荐标题", "风格", "评分", "关键词覆盖", "状态"],
            rows=table_rows,
            page_size=8,
            empty_text="暂无批量生成结果",
            parent=host,
        )

        insight_section = ContentSection("批量结果建议", "✎", parent=host)
        insight_card = QFrame(insight_section)
        insight_card.setStyleSheet(self._card_style())
        insight_layout = QVBoxLayout(insight_card)
        insight_layout.setContentsMargins(18, 18, 18, 18)
        insight_layout.setSpacing(10)
        insight_layout.addWidget(
            InfoCard(
                title="评分低于 90 的标题建议二次润色",
                description="重点检查是否缺少核心品类词前置、是否缺少场景词、是否存在风格词堆积导致的阅读阻力。",
                icon="◈",
                action_text="筛出低分标题",
                parent=insight_card,
            )
        )
        insight_layout.addWidget(
            InfoCard(
                title="可按渠道拆分标题版本",
                description="搜索流量建议使用 SEO 加强型；内容流量建议使用风格放大型；短视频场景可用高转化型承接即时购买。",
                icon="◎",
                action_text="生成渠道版本",
                parent=insight_card,
            )
        )
        insight_section.add_widget(insight_card)

        layout.addWidget(summary_row)
        layout.addWidget(result_table)
        layout.addWidget(insight_section)
        layout.addStretch(1)
        scroll.set_content_widget(host)
        return scroll

    def _build_footer_stats(self) -> QWidget:
        footer = QFrame(self)
        footer.setStyleSheet(self._card_style())
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        items = (
            ("关键词覆盖", "2,480+", "brand"),
            ("模板总数", "156", "success"),
            ("日均分析量", "8.9万", "brand"),
            ("平均点击提升", "+34.2%", "warning"),
        )
        for label_text, value, tone in items:
            card = QFrame(footer)
            tone_color, tone_bg = _tone_colors(tone)
            card.setStyleSheet(
                f"QFrame {{ background-color: {tone_bg}; border: 1px solid rgba(255,255,255,0.04); border-radius: 14px; }} QLabel {{ background: transparent; }}"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            card_layout.setSpacing(4)
            label = QLabel(label_text, card)
            label.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; font-weight: 700;")
            stat = QLabel(value, card)
            stat.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {tone_color};")
            card_layout.addWidget(label)
            card_layout.addWidget(stat)
            layout.addWidget(card, 1)

        return footer

    def _handle_title_text_changed(self, text: str) -> None:
        title_text = text.strip()
        char_count = len(title_text)
        keyword_hits = sum(
            1 for keyword in ("纯棉", "短袖", "T恤", "男", "宽松", "透气") if keyword in title_text
        )

        length_bonus = 10 if 28 <= char_count <= 48 else 4 if 20 <= char_count <= 60 else 0
        density_bonus = keyword_hits * 4
        readability_bonus = 8 if " " not in title_text and "，，" not in title_text else 4
        score = max(58, min(99, 60 + length_bonus + density_bonus + readability_bonus))

        if score >= 93:
            grade = "S级"
            tone = "success"
            hint = "长度与关键词结构非常理想，可直接进入投放测试。"
        elif score >= 86:
            grade = "A级"
            tone = "success"
            hint = "整体结构良好，建议补强 1-2 个风格词提升点击。"
        elif score >= 78:
            grade = "B级"
            tone = "warning"
            hint = "建议继续压缩冗余描述，避免词序拖慢阅读。"
        else:
            grade = "C级"
            tone = "error"
            hint = "标题信息量不足或结构较散，建议重新组织关键词顺序。"

        if self._char_count_label is not None:
            self._char_count_label.setText(f"{char_count} / {self._title_limit}")
        if self._char_hint_label is not None:
            if char_count > self._title_limit:
                self._char_hint_label.setText("已超出平台建议上限，建议删减冗余修饰词。")
            elif char_count < 24:
                self._char_hint_label.setText("长度偏短，建议补入卖点词或场景词。")
            else:
                self._char_hint_label.setText(hint)
        if self._title_score_value_label is not None:
            self._title_score_value_label.setText(str(score))
        if self._title_grade_badge is not None:
            self._title_grade_badge.setText(grade)
            self._title_grade_badge.set_tone(tone)
        if self._keyword_coverage_label is not None:
            self._keyword_coverage_label.setText(f"核心词覆盖 {keyword_hits}/6，当前标题可读性与搜索兼容度较好。")

    @staticmethod
    def _card_style() -> str:
        return (
            "QFrame {"
            "background-color: palette(base);"
            f"border: 1px solid {ACCENT_SOFT};"
            "border-radius: 18px;"
            "}"
            "QLabel {"
            "background: transparent;"
            "}"
        )

    @staticmethod
    def _inner_panel_style() -> str:
        return (
            "QFrame {"
            f"background-color: {SURFACE_ALT};"
            "border: 1px solid rgba(255, 255, 255, 0.04);"
            "border-radius: 14px;"
            "}"
            "QLabel {"
            "background: transparent;"
            "}"
        )


__all__ = ["ProductTitlePage"]

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""蓝海分析页面。"""

from dataclasses import dataclass
from typing import Final, Sequence

from ....core.qt import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.theme.tokens import STATIC_TOKENS, get_token_value
from ....core.types import RouteId, ThemeMode
from ...components import (
    AIConfigPanel,
    ChartWidget,
    ContentSection,
    FilterDropdown,
    HeatmapWidget,
    KPICard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    StreamingOutputWidget,
    TabBar,
    TagChip,
    ThemedScrollArea,
    TrendComparison,
    WordCloudWidget,
)
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
    """解析当前主题 token。"""

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


def _clear_layout(layout: object) -> None:
    """尽量清空布局内项目。"""

    take_at = getattr(layout, "takeAt", None)
    if not callable(take_at):
        return
    while True:
        item = take_at(0)
        if item is None:
            break
        widget_method = getattr(item, "widget", None)
        child_widget = widget_method() if callable(widget_method) else None
        if child_widget is not None:
            _call(child_widget, "setParent", None)


def _set_frame_panel(widget: QFrame, object_name: str, *, border_color: str | None = None, background: str | None = None) -> None:
    """应用统一面板壳层。"""

    palette = _palette()
    resolved_border = border_color or palette.border
    resolved_background = background or palette.surface
    _call(widget, "setObjectName", object_name)
    _call(
        widget,
        "setStyleSheet",
        f"""
        QFrame#{object_name} {{
            background-color: {resolved_background};
            border: 1px solid {resolved_border};
            border-radius: {RADIUS_XL}px;
        }}
        QLabel {{
            background: transparent;
        }}
        """,
    )


def _set_label_style(widget: QLabel, *, size_token: str, color: str, weight_token: str = "font.weight.medium") -> None:
    """统一设置文本样式。"""

    _call(
        widget,
        "setStyleSheet",
        f"color: {color}; font-size: {STATIC_TOKENS[size_token]}; font-weight: {STATIC_TOKENS[weight_token]}; background: transparent;",
    )


@dataclass(frozen=True)
class _Palette:
    """页面局部色板。"""

    surface: str
    surface_alt: str
    surface_sunken: str
    text: str
    text_muted: str
    text_inverse: str
    border: str
    border_strong: str
    primary: str
    primary_hover: str
    success: str
    warning: str
    danger: str
    info: str
    accent_1: str
    accent_2: str
    accent_3: str
    accent_4: str


def _palette() -> _Palette:
    """生成当前页面使用的色板。"""

    return _Palette(
        surface=_token("surface.secondary"),
        surface_alt=_token("surface.tertiary"),
        surface_sunken=_token("surface.sunken"),
        text=_token("text.primary"),
        text_muted=_token("text.secondary"),
        text_inverse=_token("text.inverse"),
        border=_token("border.default"),
        border_strong=_token("border.strong"),
        primary=_token("brand.primary"),
        primary_hover=_token("brand.primary_hover"),
        success=_token("status.success"),
        warning=_token("status.warning"),
        danger=_token("status.error"),
        info=_token("status.info"),
        accent_1=STATIC_TOKENS["chart.series[1]"],
        accent_2=STATIC_TOKENS["chart.series[2]"],
        accent_3=STATIC_TOKENS["chart.series[3]"],
        accent_4=STATIC_TOKENS["chart.series[4]"],
    )


SPACING_XS: Final[int] = _px("spacing.xs")
SPACING_SM: Final[int] = _px("spacing.sm")
SPACING_MD: Final[int] = _px("spacing.md")
SPACING_LG: Final[int] = _px("spacing.lg")
SPACING_XL: Final[int] = _px("spacing.xl")
SPACING_2XL: Final[int] = _px("spacing.2xl")
SPACING_3XL: Final[int] = _px("spacing.3xl")
SPACING_4XL: Final[int] = _px("spacing.4xl")
RADIUS_MD: Final[int] = _px("radius.md")
RADIUS_LG: Final[int] = _px("radius.lg")
RADIUS_XL: Final[int] = _px("radius.xl")

WEEK_LABELS: Final[tuple[str, ...]] = ("第1周", "第2周", "第3周", "第4周", "第5周", "第6周", "第7周", "第8周")
DEMAND_SCORE_LABELS: Final[tuple[str, ...]] = ("需求搜索", "视频热度", "达人参与", "供给空白", "利润弹性", "复购信号")


@dataclass(frozen=True)
class OpportunityPoint:
    """矩阵中的单个机会点。"""

    key: str
    name: str
    icon: str
    quadrant: str
    region_focus: str
    price_band: str
    scenario: str
    market_size_label: str
    competition_label: str
    opportunity_score: float
    market_gap_index: int
    competitor_count: int
    competitor_delta_text: str
    profit_rate: float
    saturation: int
    aov: int
    demand_growth: int
    conversion_potential: int
    bubble_size: tuple[int, int]
    tone: str
    highlights: tuple[str, ...]
    risks: tuple[str, ...]
    tags: tuple[str, ...]
    ai_summary: str
    ai_bullets: tuple[str, ...]
    report_lines: tuple[str, ...]
    demand_series: tuple[float, ...]
    supply_series: tuple[float, ...]
    gap_series: tuple[float, ...]
    keyword_weights: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class CategorySnapshot:
    """分类分析卡片数据。"""

    category: str
    thesis: str
    opportunity_score: float
    growth_rate: int
    gap_index: int
    competition_index: int
    hero_products: tuple[str, ...]
    recommended_region: str
    price_band: str
    tone: str


@dataclass(frozen=True)
class GapIndicator:
    """市场缺口指标。"""

    title: str
    value: str
    subtitle: str
    detail: str
    tone: str
    trend_text: str
    tags: tuple[str, ...]


HEADER_TAGS: Final[tuple[str, ...]] = ("机会矩阵", "趋势发现", "策略建议")

MATRIX_QUADRANTS: Final[tuple[tuple[str, str, str], ...]] = (
    ("高竞争 × 小规模", "拥挤试错区", "以短期验证和差异功能切入，不宜重库存。"),
    ("高竞争 × 大规模", "红海主战场", "头部竞品集中，需要品牌心智或极致价格。"),
    ("低竞争 × 小规模", "利基培育区", "先用达人场景教育，再扩展核心人群。"),
    ("低竞争 × 大规模", "蓝海机会区", "优先投入选品、内容和达人资源，快速建立先发优势。"),
)

OPPORTUNITY_POINTS: Final[tuple[OpportunityPoint, ...]] = (
    OpportunityPoint(
        key="smart_wear",
        name="智能穿戴设备",
        icon="穿戴",
        quadrant="低竞争 × 大规模",
        region_focus="北美 / 英国",
        price_band="¥899-1499",
        scenario="健身恢复、睡眠监测、远程办公",
        market_size_label="大规模市场",
        competition_label="低竞争",
        opportunity_score=9.4,
        market_gap_index=88,
        competitor_count=12,
        competitor_delta_text="↓ 15%",
        profit_rate=42.8,
        saturation=18,
        aov=1299,
        demand_growth=64,
        conversion_potential=82,
        bubble_size=(124, 124),
        tone="blue",
        highlights=(
            "睡眠质量可视化内容在近 6 周持续拉升互动。",
            "高客单但低同质，适合达人深度种草和对比测评。",
            "北美用户更偏向续航、佩戴舒适度和女性健康场景。",
        ),
        risks=(
            "涉及参数说明与功能承诺时需控制素材合规表达。",
            "售后说明必须突出兼容系统与防水等级。",
        ),
        tags=("高客单", "功能升级", "达人测评", "礼赠场景"),
        ai_summary="智能穿戴赛道处于明显的蓝海区间：需求增速稳定上行，但供给端仍停留在基础手环和低价表盘阶段，具备通过‘续航 + 健康洞察 + 礼品化包装’建立差异的空间。",
        ai_bullets=(
            "优先聚焦女性健康、睡眠恢复、轻运动三类细分场景，内容表达更容易形成高停留。",
            "主推 999-1299 元价格带，既能保证 40% 左右利润，也能和成熟品牌拉开价格心智。",
            "首轮达人合作建议采用‘真实佩戴 7 天复盘’而非单次开箱，突出续航与数据可视化。",
        ),
        report_lines=(
            "市场信号显示，用户对“可量化健康反馈”的接受度明显高于单纯外观升级。",
            "当前头部竞品视频多强调硬件参数，尚未充分教育睡眠、压力与女性健康等高转化场景。",
            "如果以礼赠、通勤健康管理和轻运动习惯养成为核心叙事，有望在北美站建立差异化蓝海心智。",
        ),
        demand_series=(42, 48, 51, 57, 64, 72, 81, 88),
        supply_series=(38, 39, 41, 43, 45, 48, 51, 55),
        gap_series=(6, 9, 10, 14, 19, 24, 30, 33),
        keyword_weights=(
            ("睡眠监测", 94),
            ("长续航", 87),
            ("女性健康", 82),
            ("运动恢复", 78),
            ("商务礼物", 66),
            ("全天佩戴", 62),
            ("精准提醒", 58),
            ("轻量无感", 55),
        ),
    ),
    OpportunityPoint(
        key="portable_power",
        name="便携储能电源",
        icon="储能",
        quadrant="低竞争 × 大规模",
        region_focus="北美 / 德国",
        price_band="¥699-1399",
        scenario="露营、停电应急、车载旅行",
        market_size_label="大规模市场",
        competition_label="低竞争",
        opportunity_score=8.9,
        market_gap_index=81,
        competitor_count=19,
        competitor_delta_text="↓ 9%",
        profit_rate=38.6,
        saturation=26,
        aov=1088,
        demand_growth=58,
        conversion_potential=79,
        bubble_size=(110, 110),
        tone="blue",
        highlights=(
            "露营季前置搜索显著提升，站外内容对站内转化拉动明显。",
            "中小功率产品内容教育成本低，适合生活方式达人种草。",
            "用户更关注“能带走 + 真能用 + 安全感”三要素。",
        ),
        risks=(
            "运输与合规约束高，需优先规划站点与仓配。",
            "素材必须避免极限工况承诺，重点展示真实应用场景。",
        ),
        tags=("露营经济", "应急电源", "高客单", "站外引流"),
        ai_summary="便携储能已经从小众极客用品转向大众露营和居家应急用品，但 TikTok Shop 供给仍集中在参数堆叠，缺乏面向家庭场景的内容包装。",
        ai_bullets=(
            "优先选择 300W-600W 的中功率段，内容更好解释，履约压力也更可控。",
            "素材建议围绕“停电 30 分钟还能做什么”展开，强化家庭安全心智。",
            "投放地区优先北美南部与德国户外消费人群，达人类型选择露营、家居收纳与家庭生活。",
        ),
        report_lines=(
            "用户并不追求复杂技术语言，而是追求一种“可预期的安心感”。",
            "供给端当前没有形成强内容品牌，意味着后入局者仍有通过叙事抢占认知的机会。",
            "建议把“露营娱乐”与“应急供电”双场景打通，扩大购买动机。",
        ),
        demand_series=(35, 39, 45, 52, 56, 63, 71, 79),
        supply_series=(31, 33, 34, 38, 40, 43, 48, 52),
        gap_series=(4, 6, 11, 14, 16, 20, 23, 27),
        keyword_weights=(
            ("露营供电", 88),
            ("停电应急", 82),
            ("静音储能", 71),
            ("户外咖啡", 66),
            ("车载旅行", 61),
            ("家庭备用", 58),
            ("轻便携带", 56),
            ("安全充电", 54),
        ),
    ),
    OpportunityPoint(
        key="pet_dryer",
        name="宠物烘干机",
        icon="宠物",
        quadrant="低竞争 × 大规模",
        region_focus="美国 / 法国",
        price_band="¥499-899",
        scenario="宠物洗护、家用护理、春秋换毛",
        market_size_label="大规模市场",
        competition_label="低竞争",
        opportunity_score=8.6,
        market_gap_index=77,
        competitor_count=15,
        competitor_delta_text="↓ 12%",
        profit_rate=36.4,
        saturation=23,
        aov=688,
        demand_growth=61,
        conversion_potential=74,
        bubble_size=(132, 132),
        tone="blue",
        highlights=(
            "宠物护理内容天然具备停留优势，演示型素材转化链路短。",
            "高毛量犬种和敏感体质猫犬用户对低噪音功能更敏感。",
            "市场教育已完成，但内容表达仍偏硬卖货。",
        ),
        risks=(
            "需要更细的功能分层，避免与传统吹风机概念混淆。",
            "宠物安全表述要强调“低温柔风”和“定时可控”。",
        ),
        tags=("宠物家庭", "演示转化", "低噪音", "洗护场景"),
        ai_summary="宠物烘干机的真实蓝海并不在“烘干”本身，而在“减少宠物焦虑 + 节省主人护理时间”的内容定位上，用户愿意为舒适性买单。",
        ai_bullets=(
            "建议主视觉突出“宠物不抗拒”“主人双手解放”两个卖点，而不是参数堆砌。",
            "价格带建议卡在 599-699 元，便于做首购转化，同时仍保留足够利润。",
            "达人合作优先真实宠物家庭，避免纯测评号降低信任感。",
        ),
        report_lines=(
            "用户更容易被“护理更轻松”的情绪价值打动，而不是单纯烘干速度。",
            "当前同类视频里，低噪音和安心护理仍属于明显供给空白。",
            "如果采用前后对比和宠物情绪反应作为素材结构，转化效率会更高。",
        ),
        demand_series=(28, 34, 41, 46, 53, 59, 67, 73),
        supply_series=(27, 28, 30, 33, 37, 39, 41, 45),
        gap_series=(1, 6, 11, 13, 16, 20, 26, 28),
        keyword_weights=(
            ("低噪音烘干", 90),
            ("宠物洗护", 84),
            ("敏感体质", 72),
            ("换毛季", 68),
            ("主人省时", 61),
            ("安心护理", 57),
            ("柔风速干", 55),
            ("家庭洗护站", 52),
        ),
    ),
    OpportunityPoint(
        key="car_aroma",
        name="车载香氛机",
        icon="车载",
        quadrant="低竞争 × 小规模",
        region_focus="中东 / 东南亚",
        price_band="¥159-299",
        scenario="车内氛围、礼赠、小空间净味",
        market_size_label="中等规模",
        competition_label="低竞争",
        opportunity_score=7.9,
        market_gap_index=69,
        competitor_count=11,
        competitor_delta_text="↓ 6%",
        profit_rate=34.9,
        saturation=29,
        aov=239,
        demand_growth=45,
        conversion_potential=68,
        bubble_size=(96, 96),
        tone="niche",
        highlights=(
            "礼赠与车内氛围内容的视觉表现稳定，适合节日节点放大。",
            "小空间净味和香型高级感是供给端表达弱项。",
            "用户对外观和质感的要求高于技术参数。",
        ),
        risks=(
            "同质化包装较多，必须强化香型差异和车内场景。",
            "需避免“医疗级净化”等高风险话术。",
        ),
        tags=("礼赠属性", "香型心智", "高颜值", "节日场景"),
        ai_summary="车载香氛机更适合作为‘中等规模的内容型利基市场’，核心机会在于香型叙事、包装质感与情绪价值，而不是硬件结构创新。",
        ai_bullets=(
            "优先做情侣礼物、商务座驾和新车除味三个切口。",
            "内容建议结合车内前后对比和香型人格标签，提升记忆点。",
            "适合用低成本试投快速测试香型偏好，再扩量高反馈 SKU。",
        ),
        report_lines=(
            "该赛道天花板不如智能穿戴，但投入产出更适合做轻量试水。",
            "若素材精致度够高，用户愿意为“高级感”而非功能本身付费。",
            "建议优先中东与东南亚站点，礼赠需求和车内装饰需求更强。",
        ),
        demand_series=(20, 23, 26, 28, 31, 36, 39, 43),
        supply_series=(18, 19, 20, 21, 23, 26, 28, 31),
        gap_series=(2, 4, 6, 7, 8, 10, 11, 12),
        keyword_weights=(
            ("车内高级香", 84),
            ("礼盒香氛", 73),
            ("新车除味", 68),
            ("氛围感", 63),
            ("精致座舱", 61),
            ("商务礼赠", 57),
            ("低调香型", 53),
            ("精油扩香", 49),
        ),
    ),
    OpportunityPoint(
        key="camp_filter",
        name="露营净水壶",
        icon="露营",
        quadrant="低竞争 × 小规模",
        region_focus="北美 / 澳新",
        price_band="¥199-359",
        scenario="户外徒步、露营、应急储备",
        market_size_label="中等规模",
        competition_label="低竞争",
        opportunity_score=7.6,
        market_gap_index=65,
        competitor_count=9,
        competitor_delta_text="↓ 4%",
        profit_rate=32.5,
        saturation=24,
        aov=269,
        demand_growth=42,
        conversion_potential=66,
        bubble_size=(90, 90),
        tone="niche",
        highlights=(
            "户外安全感话题在露营社区中稳定活跃。",
            "场景演示天然适合短视频内容，转化链路清晰。",
            "市场尚未形成真正的场景头部品牌。",
        ),
        risks=(
            "教育成本略高，需要配套讲清过滤场景和使用限制。",
            "季节波动明显，适合节奏化投放。",
        ),
        tags=("户外安全", "徒步露营", "季节品", "内容教育"),
        ai_summary="露营净水壶属于典型的内容先行型利基蓝海，适合在露营季用场景故事快速验证，但不建议一次性重仓备货。",
        ai_bullets=(
            "用“户外水源不确定怎么办”作为内容引子，比讲过滤参数更容易打动新手用户。",
            "建议联动露营装备达人，形成组合场景销售。",
            "适合和便携储能形成同主题露营专场，放大整体转化。",
        ),
        report_lines=(
            "小众不代表机会小，关键在于用户决策链条足够短。",
            "该赛道缺的不是商品，而是能够被普通露营用户理解的表达方式。",
            "通过安全感和应急逻辑切入，会比单纯展示滤芯更有效。",
        ),
        demand_series=(18, 20, 22, 25, 28, 31, 35, 38),
        supply_series=(16, 17, 18, 19, 21, 23, 25, 28),
        gap_series=(2, 3, 4, 6, 7, 8, 10, 10),
        keyword_weights=(
            ("露营净水", 82),
            ("户外安全", 71),
            ("应急储备", 63),
            ("徒步装备", 58),
            ("轻量过滤", 54),
            ("野外饮水", 52),
            ("家庭备用", 47),
            ("野营必备", 45),
        ),
    ),
    OpportunityPoint(
        key="nail_lamp",
        name="美甲光疗灯",
        icon="美甲",
        quadrant="高竞争 × 小规模",
        region_focus="东南亚",
        price_band="¥69-129",
        scenario="居家美甲、节日妆造",
        market_size_label="小规模",
        competition_label="高竞争",
        opportunity_score=5.8,
        market_gap_index=36,
        competitor_count=47,
        competitor_delta_text="↑ 12%",
        profit_rate=21.9,
        saturation=61,
        aov=98,
        demand_growth=19,
        conversion_potential=51,
        bubble_size=(76, 76),
        tone="crowded",
        highlights=(
            "内容需求仍在，但价格战严重，利润空间持续压缩。",
            "颜值和便携卖点很难形成真正区隔。",
            "适合作为关联品，不适合作为主力蓝海赛道。",
        ),
        risks=(
            "头部商品同质严重，达人佣金与退货压力偏高。",
            "赛道过度依赖低价冲量。",
        ),
        tags=("低价竞争", "关联销售", "季节节点"),
        ai_summary="美甲光疗灯不属于当前优先布局的蓝海市场，除非绑定耗材或套装逻辑，否则很难建立稳定利润。",
        ai_bullets=(
            "如果必须做，建议转向便携旅行套装或新手入门套组。",
            "不要单独拿光疗灯做放量主品。",
            "适合在节日节点做短促，不适合长期蓝海投入。",
        ),
        report_lines=(
            "该赛道更像成熟品类补充，而不是新的增长引擎。",
            "用户兴趣有，但竞争密度过高。",
            "建议谨慎评估投入，避免资源沉没。",
        ),
        demand_series=(22, 21, 23, 24, 23, 25, 24, 26),
        supply_series=(28, 30, 31, 33, 34, 36, 39, 41),
        gap_series=(-6, -9, -8, -9, -11, -11, -15, -15),
        keyword_weights=(
            ("居家美甲", 70),
            ("新手套装", 61),
            ("便携光疗", 55),
            ("节日美甲", 51),
            ("低价入门", 47),
            ("快干固化", 45),
            ("少女风", 41),
            ("套装搭配", 39),
        ),
    ),
    OpportunityPoint(
        key="phone_case",
        name="个性手机壳",
        icon="数码",
        quadrant="高竞争 × 大规模",
        region_focus="全球泛站点",
        price_band="¥29-79",
        scenario="换新装饰、礼赠、IP 联名",
        market_size_label="大规模市场",
        competition_label="高竞争",
        opportunity_score=4.9,
        market_gap_index=28,
        competitor_count=86,
        competitor_delta_text="↑ 18%",
        profit_rate=18.4,
        saturation=74,
        aov=49,
        demand_growth=12,
        conversion_potential=47,
        bubble_size=(72, 72),
        tone="red",
        highlights=(
            "市场容量大，但同质和价格战极其严重。",
            "除非具备强 IP 或极致供应链，否则难出蓝海机会。",
            "更适合做联名承接，不适合做独立增长赛道。",
        ),
        risks=(
            "售后与型号适配成本高。",
            "竞品密度高，素材生命周期极短。",
        ),
        tags=("红海", "低客单", "型号复杂", "价格战"),
        ai_summary="手机壳属于典型红海主战场，目前不建议作为蓝海分析优先对象。若无独占 IP 或快速上新能力，几乎无法建立长期利润。",
        ai_bullets=(
            "只建议作为礼赠或联名周边承接流量。",
            "避免将其视作核心增长赛道。",
            "如需介入，必须绑定 IP、主题套装或强内容人格。",
        ),
        report_lines=(
            "红海市场并非不能做，而是不适合在有限资源下作为第一优先级。",
            "该品类获客成本与供给密度长期偏高。",
            "建议转向更具利润弹性的功能型周边。",
        ),
        demand_series=(30, 31, 32, 34, 35, 35, 36, 38),
        supply_series=(41, 43, 45, 46, 48, 51, 53, 55),
        gap_series=(-11, -12, -13, -12, -13, -16, -17, -17),
        keyword_weights=(
            ("联名壳", 72),
            ("防摔", 66),
            ("透明壳", 63),
            ("情侣壳", 58),
            ("磁吸", 54),
            ("轻薄", 49),
            ("全包边", 44),
            ("热门机型", 40),
        ),
    ),
    OpportunityPoint(
        key="earbuds",
        name="蓝牙耳机",
        icon="音频",
        quadrant="高竞争 × 大规模",
        region_focus="全球泛站点",
        price_band="¥129-399",
        scenario="通勤、运动、办公",
        market_size_label="大规模市场",
        competition_label="高竞争",
        opportunity_score=5.2,
        market_gap_index=33,
        competitor_count=71,
        competitor_delta_text="↑ 10%",
        profit_rate=20.2,
        saturation=67,
        aov=249,
        demand_growth=17,
        conversion_potential=56,
        bubble_size=(84, 84),
        tone="red",
        highlights=(
            "用户需求始终存在，但头部品牌与白牌夹击明显。",
            "参数型内容已高度内卷，差异化门槛更高。",
            "除非切入专业细分运动或睡眠场景，否则不具备蓝海特征。",
        ),
        risks=(
            "售后敏感，退货率和差评风险更高。",
            "功能承诺和音质表达需谨慎。",
        ),
        tags=("成熟品类", "售后敏感", "高竞争", "参数内卷"),
        ai_summary="蓝牙耳机仍有销量，但不是当前最优蓝海方向。资源更应该优先投入到内容空白更大、利润弹性更高的功能型新品类。",
        ai_bullets=(
            "如果布局，只建议切细分，如助眠耳机或运动骨传导。",
            "普通 TWS 白牌产品很难跑出长期利润。",
            "建议把该类目留给成熟供应链团队而非创新蓝海项目。",
        ),
        report_lines=(
            "该市场更依赖供应链与口碑，而不是纯内容机会。",
            "没有足够品牌背书时，跑量并不等于赚钱。",
            "在当前阶段，优先级应低于智能穿戴和宠物护理。",
        ),
        demand_series=(33, 34, 36, 37, 39, 40, 42, 44),
        supply_series=(39, 40, 42, 44, 46, 48, 51, 54),
        gap_series=(-6, -6, -6, -7, -7, -8, -9, -10),
        keyword_weights=(
            ("降噪耳机", 79),
            ("运动耳机", 68),
            ("通勤听歌", 64),
            ("续航", 59),
            ("低延迟", 56),
            ("骨传导", 52),
            ("助眠模式", 48),
            ("舒适佩戴", 46),
        ),
    ),
)

OPPORTUNITY_LOOKUP: Final[dict[str, OpportunityPoint]] = {point.key: point for point in OPPORTUNITY_POINTS}

CATEGORY_SNAPSHOTS: Final[tuple[CategorySnapshot, ...]] = (
    CategorySnapshot(
        category="健康穿戴",
        thesis="以睡眠监测和女性健康场景切入，市场教育成本低、溢价空间高。",
        opportunity_score=9.4,
        growth_rate=64,
        gap_index=88,
        competition_index=26,
        hero_products=("智能指环", "睡眠追踪手表", "压力监测腕带"),
        recommended_region="北美 / 英国",
        price_band="¥899-1499",
        tone="brand",
    ),
    CategorySnapshot(
        category="户外储能",
        thesis="露营经济与家庭应急并行增长，内容叙事空间大于供给成熟度。",
        opportunity_score=8.9,
        growth_rate=58,
        gap_index=81,
        competition_index=31,
        hero_products=("便携储能", "折叠太阳能板", "露营供电套装"),
        recommended_region="北美 / 德国",
        price_band="¥699-1399",
        tone="success",
    ),
    CategorySnapshot(
        category="宠物护理",
        thesis="“主人省时 + 宠物舒适”是明显内容空白，演示型视频转化效率高。",
        opportunity_score=8.6,
        growth_rate=61,
        gap_index=77,
        competition_index=28,
        hero_products=("宠物烘干机", "宠物修毛吸尘器", "自动梳毛器"),
        recommended_region="美国 / 法国",
        price_band="¥499-899",
        tone="info",
    ),
    CategorySnapshot(
        category="车内氛围",
        thesis="礼赠和香型情绪价值驱动明显，适合作为中腰部利基市场快速试投。",
        opportunity_score=7.9,
        growth_rate=45,
        gap_index=69,
        competition_index=34,
        hero_products=("车载香氛机", "香氛补充液", "氛围礼盒"),
        recommended_region="中东 / 东南亚",
        price_band="¥159-299",
        tone="warning",
    ),
    CategorySnapshot(
        category="露营净水",
        thesis="内容型细分赛道，教育成本可控，适合和露营套装联动。",
        opportunity_score=7.6,
        growth_rate=42,
        gap_index=65,
        competition_index=29,
        hero_products=("净水壶", "滤水杯", "应急饮水套装"),
        recommended_region="北美 / 澳新",
        price_band="¥199-359",
        tone="brand",
    ),
    CategorySnapshot(
        category="成熟红海类目",
        thesis="手机壳、蓝牙耳机等大盘类目仍有销量，但不具备蓝海资源效率优势。",
        opportunity_score=5.1,
        growth_rate=14,
        gap_index=31,
        competition_index=78,
        hero_products=("联名手机壳", "蓝牙耳机", "基础数码配件"),
        recommended_region="全球泛站点",
        price_band="¥29-399",
        tone="error",
    ),
)

GAP_INDICATORS: Final[tuple[GapIndicator, ...]] = (
    GapIndicator(
        title="供给空白率",
        value="31.6%",
        subtitle="高于上周 4.2 个点",
        detail="目标站点中仍有 31.6% 的需求热词缺少稳定头部承接商品。",
        tone="brand",
        trend_text="持续扩大",
        tags=("高优先", "可抢位", "达人测评缺口"),
    ),
    GapIndicator(
        title="高意向价格带",
        value="¥599-1299",
        subtitle="蓝海候选主要集中区间",
        detail="用户愿意为“功能升级 + 场景价值”支付溢价，中高客单接受度明显提升。",
        tone="success",
        trend_text="溢价增强",
        tags=("利润友好", "礼赠接受", "内容解释清晰"),
    ),
    GapIndicator(
        title="达人内容缺口",
        value="47 位",
        subtitle="目标细分缺少持续输出达人",
        detail="多个潜力赛道尚未形成稳定的头部达人内容矩阵，适合优先签约中腰部达人。",
        tone="info",
        trend_text="仍未填补",
        tags=("内容先发", "中腰部达人", "低成本抢占"),
    ),
    GapIndicator(
        title="利润弹性空间",
        value="35%-45%",
        subtitle="建议优先控制的安全利润段",
        detail="蓝海候选中，兼顾放量与复购的利润带集中在 35%-45%，过低会丢失可持续性。",
        tone="warning",
        trend_text="适合放量",
        tags=("可扩量", "可促销", "广告容错"),
    ),
    GapIndicator(
        title="合规风险密度",
        value="中低",
        subtitle="优于传统成熟数码类目",
        detail="功能型新品类只要避开极限功效承诺，整体合规复杂度低于成熟红海赛道。",
        tone="success",
        trend_text="可控",
        tags=("素材友好", "售后可讲清", "适合深度演示"),
    ),
)

HEATMAP_VALUES: Final[tuple[tuple[float, ...], ...]] = (
    (12, 10, 8, 7, 6, 9, 14, 22, 34, 46, 58, 63, 55, 49, 44, 41, 48, 61, 79, 96, 112, 118, 92, 58),
    (10, 9, 7, 6, 5, 8, 13, 20, 30, 42, 55, 60, 53, 47, 41, 39, 45, 58, 73, 91, 106, 112, 88, 54),
    (11, 9, 8, 7, 6, 8, 14, 22, 33, 45, 57, 61, 56, 50, 46, 42, 49, 63, 78, 94, 109, 116, 90, 57),
    (12, 10, 8, 7, 6, 9, 15, 23, 35, 48, 61, 67, 60, 54, 49, 45, 53, 68, 84, 101, 118, 125, 98, 63),
    (14, 11, 9, 8, 7, 10, 17, 26, 39, 54, 68, 74, 66, 59, 54, 51, 60, 76, 92, 110, 128, 136, 111, 72),
    (16, 13, 11, 10, 8, 12, 18, 28, 43, 59, 74, 81, 72, 65, 60, 57, 67, 84, 103, 123, 142, 150, 126, 86),
    (15, 12, 10, 9, 8, 11, 17, 27, 41, 56, 70, 77, 69, 62, 57, 54, 64, 80, 99, 118, 137, 145, 120, 80),
)

DEFAULT_SELECTED_KEY: Final[str] = "smart_wear"


class BlueOceanPage(BasePage):
    """蓝海分析页面。"""

    default_route_id = RouteId("blue_ocean_analysis")
    default_display_name = "蓝海分析"
    default_icon_name = "explore"

    def setup_ui(self) -> None:
        """构建蓝海分析页面。"""

        self._selected_key = DEFAULT_SELECTED_KEY
        self._bubble_buttons: dict[str, QPushButton] = {}
        self._detail_highlight_layout: QVBoxLayout | None = None
        self._detail_risk_layout: QVBoxLayout | None = None
        self._detail_tags_layout: QHBoxLayout | None = None
        self._matrix_summary_label: QLabel | None = None
        self._filter_feedback_label: QLabel | None = None
        self._ai_config_summary_label: QLabel | None = None
        self._selected_name_label: QLabel | None = None
        self._selected_meta_label: QLabel | None = None
        self._selected_summary_label: QLabel | None = None
        self._selected_competitor_value_label: QLabel | None = None
        self._selected_competitor_delta_label: QLabel | None = None
        self._selected_profit_value_label: QLabel | None = None
        self._selected_gap_value_label: QLabel | None = None
        self._selected_growth_value_label: QLabel | None = None
        self._selected_saturation_value_label: QLabel | None = None
        self._selected_aov_value_label: QLabel | None = None
        self._selected_conversion_value_label: QLabel | None = None
        self._saturation_fill: QFrame | None = None
        self._aov_fill: QFrame | None = None
        self._conversion_fill: QFrame | None = None
        self._demand_supply_chart: TrendComparison | None = None
        self._gap_bar_chart: ChartWidget | None = None
        self._growth_line_chart: ChartWidget | None = None
        self._keyword_cloud: WordCloudWidget | None = None
        self._heatmap_widget: HeatmapWidget | None = None
        self._strategy_output: StreamingOutputWidget | None = None
        self._ai_config_panel: AIConfigPanel | None = None
        self._search_bar: SearchBar | None = None
        self._site_filter: FilterDropdown | None = None
        self._price_filter: FilterDropdown | None = None
        self._competition_filter: FilterDropdown | None = None
        self._cycle_filter: FilterDropdown | None = None

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        scroll_area = ThemedScrollArea(self)
        self.layout.addWidget(scroll_area)

        self._page_container = PageContainer(
            title="蓝海分析",
            description="基于市场规模、竞争强度、供给空白与内容趋势，快速锁定适合 TikTok Shop 的潜力蓝海赛道。",
            parent=scroll_area,
        )
        scroll_area.set_content_widget(self._page_container)

        self._build_header_actions()
        self._page_container.add_widget(self._build_toolbar())
        self._page_container.add_widget(self._build_kpi_strip())
        self._page_container.add_widget(self._build_primary_workspace())
        self._page_container.add_widget(self._build_category_analysis_section())
        self._page_container.add_widget(self._build_gap_indicator_section())
        self._page_container.add_widget(self._build_trend_lab_section())
        self._page_container.add_widget(self._build_footer_hint())

        self._apply_page_styles()
        self._bind_interactions()
        self._apply_selection(DEFAULT_SELECTED_KEY)

    def _build_header_actions(self) -> None:
        """构建头部操作区。"""

        palette = _palette()
        for text in HEADER_TAGS:
            tag = TagChip(text, tone="brand", parent=self)
            self._page_container.add_action(tag)
        update_badge = StatusBadge("今日已更新", tone="success", parent=self)
        self._page_container.add_action(update_badge)
        refresh_button = SecondaryButton("刷新样本", parent=self)
        export_button = PrimaryButton("导出策略报告", parent=self)
        self._page_container.add_action(refresh_button)
        self._page_container.add_action(export_button)
        _call(
            refresh_button,
            "setStyleSheet",
            f"""
            QPushButton#secondaryButton {{
                border-color: {palette.border_strong};
            }}
            """,
        )

    def _build_toolbar(self) -> QWidget:
        """构建筛选工具栏。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, "blueOceanToolbar", border_color=_rgba(palette.primary, 0.18))

        root = QVBoxLayout(card)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(SPACING_MD)

        title_label = QLabel("筛选与搜索", card)
        _set_label_style(title_label, size_token="font.size.lg", color=palette.text, weight_token="font.weight.bold")
        helper_label = QLabel("支持按站点、价格带、竞争等级和增长周期定位蓝海机会。", card)
        _set_label_style(helper_label, size_token="font.size.sm", color=palette.text_muted)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)
        title_column.addWidget(title_label)
        title_column.addWidget(helper_label)

        title_row.addLayout(title_column)
        title_row.addStretch(1)

        self._filter_feedback_label = QLabel("当前聚焦：北美高客单、低竞争、近 8 周增长中。", card)
        _set_label_style(self._filter_feedback_label, size_token="font.size.sm", color=palette.primary, weight_token="font.weight.semibold")
        title_row.addWidget(self._filter_feedback_label)

        filters_row = QHBoxLayout()
        filters_row.setContentsMargins(0, 0, 0, 0)
        filters_row.setSpacing(SPACING_LG)

        self._search_bar = SearchBar("搜索类目、场景、热词或策略方向...", card)
        self._site_filter = FilterDropdown("目标站点", ("北美", "英国", "欧洲", "东南亚", "中东"), parent=card)
        self._price_filter = FilterDropdown("价格带", ("¥0-199", "¥199-599", "¥599-1299", "¥1299+"), parent=card)
        self._competition_filter = FilterDropdown("竞争强度", ("低竞争", "中竞争", "高竞争"), parent=card)
        self._cycle_filter = FilterDropdown("增长周期", ("近 4 周", "近 8 周", "近 12 周", "近 24 周"), parent=card)

        filters_row.addWidget(self._search_bar, 3)
        filters_row.addWidget(self._site_filter, 1)
        filters_row.addWidget(self._price_filter, 1)
        filters_row.addWidget(self._competition_filter, 1)
        filters_row.addWidget(self._cycle_filter, 1)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(SPACING_MD)

        focus_tag = TagChip("低竞争优先", tone="success", parent=card)
        content_tag = TagChip("内容供给空白", tone="info", parent=card)
        margin_tag = TagChip("利润率 35%+", tone="warning", parent=card)
        action_row.addWidget(focus_tag)
        action_row.addWidget(content_tag)
        action_row.addWidget(margin_tag)
        action_row.addStretch(1)
        action_row.addWidget(SecondaryButton("重置筛选", card))
        action_row.addWidget(PrimaryButton("生成调研报告", card))

        root.addLayout(title_row)
        root.addLayout(filters_row)
        root.addLayout(action_row)
        return card

    def _build_kpi_strip(self) -> QWidget:
        """构建顶部指标卡片。"""

        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        cards = (
            KPICard(
                title="蓝海候选类目",
                value="8 个",
                trend="up",
                percentage="+2 个",
                caption="较上周新增",
                sparkline_data=(2, 3, 3, 4, 5, 6, 8),
                parent=wrapper,
            ),
            KPICard(
                title="平均缺口指数",
                value="74.3",
                trend="up",
                percentage="+9.8%",
                caption="供给空白扩大",
                sparkline_data=(48, 52, 57, 61, 66, 70, 74),
                parent=wrapper,
            ),
            KPICard(
                title="低竞争赛道占比",
                value="62%",
                trend="up",
                percentage="+6.1%",
                caption="优于上周期",
                sparkline_data=(41, 44, 46, 50, 55, 58, 62),
                parent=wrapper,
            ),
            KPICard(
                title="高意向站点",
                value="北美站",
                trend="flat",
                percentage="稳定",
                caption="转化动能最强",
                sparkline_data=(74, 75, 77, 79, 81, 82, 82),
                parent=wrapper,
            ),
        )

        for card in cards:
            layout.addWidget(card, 1)
        return wrapper

    def _build_primary_workspace(self) -> QWidget:
        """构建主工作区。"""

        split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.62, 0.38),
            minimum_sizes=(620, 400),
            parent=self,
        )
        split.set_widgets(self._build_matrix_panel(), self._build_detail_and_strategy_panel())
        return split

    def _build_matrix_panel(self) -> QWidget:
        """构建机会矩阵区域。"""

        section = ContentSection("机会分布矩阵", icon="◫", parent=self)

        header_card = QFrame(section)
        _set_frame_panel(header_card, "blueOceanMatrixHeader", background=_rgba(_palette().primary, 0.06))
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_LG)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)
        title_label = QLabel("机会分布矩阵", header_card)
        subtitle_label = QLabel("横轴：市场规模｜纵轴：竞争强度｜点击气泡可联动详情与 AI 策略。", header_card)
        _set_label_style(title_label, size_token="font.size.lg", color=_palette().text, weight_token="font.weight.bold")
        _set_label_style(subtitle_label, size_token="font.size.sm", color=_palette().text_muted)
        title_column.addWidget(title_label)
        title_column.addWidget(subtitle_label)
        header_layout.addLayout(title_column)
        header_layout.addStretch(1)

        legend_column = QVBoxLayout()
        legend_column.setContentsMargins(0, 0, 0, 0)
        legend_column.setSpacing(SPACING_SM)
        legend_column.addWidget(StatusBadge("蓝海高潜力", tone="brand", parent=header_card))
        legend_column.addWidget(StatusBadge("利基培育", tone="info", parent=header_card))
        legend_column.addWidget(StatusBadge("成熟红海", tone="warning", parent=header_card))
        header_layout.addLayout(legend_column)

        matrix_shell = QFrame(section)
        _set_frame_panel(matrix_shell, "blueOceanMatrixShell")
        shell_layout = QVBoxLayout(matrix_shell)
        shell_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        shell_layout.setSpacing(SPACING_MD)

        top_hint_row = QHBoxLayout()
        top_hint_row.setContentsMargins(0, 0, 0, 0)
        top_hint_row.setSpacing(SPACING_MD)
        top_hint_row.addWidget(QLabel("高竞争", matrix_shell))
        top_hint_row.addStretch(1)
        top_hint_row.addWidget(StatusBadge("红海主战场", tone="warning", parent=matrix_shell))
        for index in range(top_hint_row.count()):
            item_method = getattr(top_hint_row, "itemAt", None)
            item = item_method(index) if callable(item_method) else None
            widget_method = getattr(item, "widget", None) if item is not None else None
            widget = widget_method() if callable(widget_method) else None
            if isinstance(widget, QLabel):
                _set_label_style(widget, size_token="font.size.sm", color=_palette().text_muted, weight_token="font.weight.semibold")

        quadrants_column = QVBoxLayout()
        quadrants_column.setContentsMargins(0, 0, 0, 0)
        quadrants_column.setSpacing(SPACING_MD)
        quadrants_column.addLayout(self._build_quadrant_row(("nail_lamp", "phone_case"), ("smart_wear", "portable_power")))
        quadrants_column.addLayout(self._build_quadrant_row(("camp_filter", "car_aroma"), ("pet_dryer", "earbuds"), bottom_row=True))

        axis_footer = QHBoxLayout()
        axis_footer.setContentsMargins(0, SPACING_SM, 0, 0)
        axis_footer.setSpacing(SPACING_MD)
        small_scale = QLabel("小规模", matrix_shell)
        medium_scale = QLabel("中等规模", matrix_shell)
        large_scale = QLabel("大规模市场", matrix_shell)
        for label in (small_scale, medium_scale, large_scale):
            _set_label_style(label, size_token="font.size.sm", color=_palette().text_muted, weight_token="font.weight.semibold")
        axis_footer.addWidget(small_scale)
        axis_footer.addStretch(1)
        axis_footer.addWidget(medium_scale)
        axis_footer.addStretch(1)
        axis_footer.addWidget(large_scale)

        summary_card = QFrame(section)
        _set_frame_panel(summary_card, "blueOceanMatrixSummary", background=_rgba(_palette().accent_3, 0.10))
        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        summary_layout.setSpacing(SPACING_LG)
        self._matrix_summary_label = QLabel(
            "当前蓝海高潜力集中在‘智能穿戴、便携储能、宠物护理’三条主线：均具备高客单、低饱和、内容可解释性强的共性。",
            summary_card,
        )
        _call(self._matrix_summary_label, "setWordWrap", True)
        _set_label_style(self._matrix_summary_label, size_token="font.size.md", color=_palette().text, weight_token="font.weight.semibold")
        summary_layout.addWidget(self._matrix_summary_label, 1)
        summary_layout.addWidget(StatusBadge("蓝海密度提升", tone="success", parent=summary_card))

        shell_layout.addLayout(top_hint_row)
        shell_layout.addLayout(quadrants_column)
        shell_layout.addLayout(axis_footer)

        section.add_widget(header_card)
        section.add_widget(matrix_shell)
        section.add_widget(summary_card)
        return section

    def _build_quadrant_row(self, left_keys: tuple[str, str], right_keys: tuple[str, str], *, bottom_row: bool = False) -> QHBoxLayout:
        """构建一行矩阵象限。"""

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACING_MD)

        left_title, left_badge, left_desc = MATRIX_QUADRANTS[2 if bottom_row else 0]
        right_title, right_badge, right_desc = MATRIX_QUADRANTS[3 if bottom_row else 1]
        row.addWidget(self._build_quadrant_card(left_title, left_badge, left_desc, left_keys), 1)
        row.addWidget(self._build_quadrant_card(right_title, right_badge, right_desc, right_keys), 1)
        return row

    def _build_quadrant_card(self, title: str, badge_text: str, description: str, keys: Sequence[str]) -> QWidget:
        """构建单个矩阵象限卡片。"""

        palette = _palette()
        frame = QFrame(self)
        _set_frame_panel(frame, f"quadrant_{title}", background=_rgba(palette.surface_sunken, 0.94))

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_MD)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)
        title_label = QLabel(title, frame)
        desc_label = QLabel(description, frame)
        _call(desc_label, "setWordWrap", True)
        _set_label_style(title_label, size_token="font.size.md", color=palette.text, weight_token="font.weight.bold")
        _set_label_style(desc_label, size_token="font.size.sm", color=palette.text_muted)
        title_column.addWidget(title_label)
        title_column.addWidget(desc_label)
        header_row.addLayout(title_column, 1)

        badge_tone = "brand" if "蓝海" in badge_text else ("warning" if "红海" in badge_text else "info")
        header_row.addWidget(StatusBadge(badge_text, tone=badge_tone, parent=frame))

        bubble_row = QHBoxLayout()
        bubble_row.setContentsMargins(0, SPACING_SM, 0, 0)
        bubble_row.setSpacing(SPACING_MD)
        bubble_row.addStretch(1)
        for key in keys:
            bubble_row.addWidget(self._build_matrix_bubble(OPPORTUNITY_LOOKUP[key]))
            bubble_row.addStretch(1)

        foot_row = QHBoxLayout()
        foot_row.setContentsMargins(0, SPACING_SM, 0, 0)
        foot_row.setSpacing(SPACING_SM)
        for key in keys:
            point = OPPORTUNITY_LOOKUP[key]
            tag_tone = "brand" if point.tone == "blue" else ("warning" if point.tone == "red" else "info")
            foot_row.addWidget(TagChip(f"{point.name} {point.opportunity_score:.1f}", tone=tag_tone, parent=frame))
        foot_row.addStretch(1)

        layout.addLayout(header_row)
        layout.addLayout(bubble_row)
        layout.addLayout(foot_row)
        return frame

    def _build_matrix_bubble(self, point: OpportunityPoint) -> QPushButton:
        """构建矩阵中的气泡按钮。"""

        palette = _palette()
        button = QPushButton(point.name, self)
        self._bubble_buttons[point.key] = button
        width, height = point.bubble_size
        _call(button, "setObjectName", f"matrixBubble_{point.key}")
        _call(button, "setCheckable", True)
        _call(button, "setFixedSize", width, height)
        _call(button, "setToolTip", f"潜力指数 {point.opportunity_score:.1f}｜{point.region_focus}")

        if point.tone == "blue":
            background = _rgba(palette.primary, 0.22)
            border = palette.primary
            hover = _rgba(palette.primary_hover, 0.28)
            text_color = palette.text
        elif point.tone == "red":
            background = _rgba(palette.warning, 0.18)
            border = _rgba(palette.warning, 0.48)
            hover = _rgba(palette.warning, 0.24)
            text_color = palette.text
        else:
            background = _rgba(palette.info, 0.18)
            border = _rgba(palette.info, 0.38)
            hover = _rgba(palette.info, 0.24)
            text_color = palette.text

        _call(
            button,
            "setStyleSheet",
            f"""
            QPushButton#{button.objectName()} {{
                background-color: {background};
                color: {text_color};
                border: 2px solid {border};
                border-radius: {int(min(width, height) / 2)}px;
                padding: {SPACING_SM}px;
                font-size: {STATIC_TOKENS['font.size.sm']};
                font-weight: {STATIC_TOKENS['font.weight.bold']};
            }}
            QPushButton#{button.objectName()}:hover {{
                background-color: {hover};
                border-color: {palette.primary};
            }}
            QPushButton#{button.objectName()}:checked {{
                background-color: {_rgba(palette.primary, 0.32)};
                border-color: {palette.primary_hover};
                color: {palette.text};
            }}
            """,
        )
        _connect(button.clicked, lambda _checked=False, point_key=point.key: self._apply_selection(point_key))
        return button

    def _build_detail_and_strategy_panel(self) -> QWidget:
        """构建右侧详情和策略区。"""

        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_selected_detail_panel())
        layout.addWidget(self._build_ai_strategy_panel())
        return wrapper

    def _build_selected_detail_panel(self) -> QWidget:
        """构建选中项详情卡片。"""

        palette = _palette()
        section = ContentSection("选中项详情", icon="◎", parent=self)

        top_card = QFrame(section)
        _set_frame_panel(top_card, "blueOceanSelectedTop")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        top_layout.setSpacing(SPACING_LG)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_MD)
        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)

        self._selected_name_label = QLabel("智能穿戴设备", top_card)
        self._selected_meta_label = QLabel("北美 / 英国 ｜ ¥899-1499 ｜ 健康管理场景", top_card)
        self._selected_summary_label = QLabel("正在读取蓝海候选项说明。", top_card)
        _call(self._selected_summary_label, "setWordWrap", True)
        _set_label_style(self._selected_name_label, size_token="font.size.xxl", color=palette.primary, weight_token="font.weight.bold")
        _set_label_style(self._selected_meta_label, size_token="font.size.sm", color=palette.text_muted, weight_token="font.weight.semibold")
        _set_label_style(self._selected_summary_label, size_token="font.size.md", color=palette.text)
        title_column.addWidget(self._selected_name_label)
        title_column.addWidget(self._selected_meta_label)
        title_column.addWidget(self._selected_summary_label)
        header_row.addLayout(title_column, 1)
        header_row.addWidget(StatusBadge("蓝海优先", tone="brand", parent=top_card))

        metrics_row = QHBoxLayout()
        metrics_row.setContentsMargins(0, 0, 0, 0)
        metrics_row.setSpacing(SPACING_MD)
        metrics_row.addWidget(self._build_mini_metric_card("竞争对手数量", "12", "↓ 15%", attr_prefix="competitor"), 1)
        metrics_row.addWidget(self._build_mini_metric_card("预估利润率", "42.8%", "高优", attr_prefix="profit"), 1)
        metrics_row.addWidget(self._build_mini_metric_card("市场缺口指数", "88", "持续走高", attr_prefix="gap"), 1)
        metrics_row.addWidget(self._build_mini_metric_card("转化潜力", "82", "内容友好", attr_prefix="growth"), 1)

        progress_column = QVBoxLayout()
        progress_column.setContentsMargins(0, 0, 0, 0)
        progress_column.setSpacing(SPACING_MD)
        progress_column.addWidget(self._build_progress_metric("市场饱和度", "18%", 18, attr_name="saturation_fill", value_attr="selected_saturation_value_label"))
        progress_column.addWidget(self._build_progress_metric("平均客单价", "¥1299", 72, attr_name="aov_fill", value_attr="selected_aov_value_label"))
        progress_column.addWidget(self._build_progress_metric("内容转化弹性", "82", 82, attr_name="conversion_fill", value_attr="selected_conversion_value_label"))

        tags_card = QFrame(section)
        _set_frame_panel(tags_card, "blueOceanSelectedTags", background=_rgba(palette.accent_2, 0.08))
        tags_layout = QVBoxLayout(tags_card)
        tags_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        tags_layout.setSpacing(SPACING_MD)
        tag_title = QLabel("赛道标签", tags_card)
        _set_label_style(tag_title, size_token="font.size.md", color=palette.text, weight_token="font.weight.bold")
        tags_layout.addWidget(tag_title)
        self._detail_tags_layout = QHBoxLayout()
        self._detail_tags_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_tags_layout.setSpacing(SPACING_SM)
        self._detail_tags_layout.addStretch(1)
        tags_layout.addLayout(self._detail_tags_layout)

        highlight_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.5, 0.5),
            minimum_sizes=(220, 220),
            parent=section,
        )
        highlight_split.set_widgets(self._build_detail_list_card("机会要点", "detailHighlights", is_risk=False), self._build_detail_list_card("注意事项", "detailRisks", is_risk=True))

        top_layout.addLayout(header_row)
        top_layout.addLayout(metrics_row)
        top_layout.addLayout(progress_column)

        section.add_widget(top_card)
        section.add_widget(tags_card)
        section.add_widget(highlight_split)
        return section

    def _build_mini_metric_card(self, title: str, value: str, delta: str, *, attr_prefix: str) -> QWidget:
        """构建紧凑指标卡片。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, f"selectedMetric_{attr_prefix}", background=_rgba(palette.surface_sunken, 0.92))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_XS)

        title_label = QLabel(title, card)
        value_label = QLabel(value, card)
        delta_label = QLabel(delta, card)
        _set_label_style(title_label, size_token="font.size.sm", color=palette.text_muted)
        _set_label_style(value_label, size_token="font.size.xl", color=palette.text, weight_token="font.weight.bold")
        _set_label_style(delta_label, size_token="font.size.sm", color=palette.success if "↓" in delta or "高优" in delta or "持续" in delta or "友好" in delta else palette.info, weight_token="font.weight.bold")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(delta_label)

        setattr(self, f"_selected_{attr_prefix}_value_label", value_label)
        setattr(self, f"_selected_{attr_prefix}_delta_label", delta_label)
        return card

    def _build_progress_metric(self, title: str, value: str, percent: int, *, attr_name: str, value_attr: str) -> QWidget:
        """构建进度指标。"""

        palette = _palette()
        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(SPACING_MD)
        title_label = QLabel(title, wrapper)
        value_label = QLabel(value, wrapper)
        _set_label_style(title_label, size_token="font.size.sm", color=palette.text_muted, weight_token="font.weight.semibold")
        _set_label_style(value_label, size_token="font.size.sm", color=palette.text, weight_token="font.weight.bold")
        title_row.addWidget(title_label)
        title_row.addStretch(1)
        title_row.addWidget(value_label)

        track = QFrame(wrapper)
        _call(track, "setObjectName", f"progressTrack_{attr_name}")
        _call(track, "setFixedHeight", 10)
        _call(
            track,
            "setStyleSheet",
            f"QFrame#progressTrack_{attr_name} {{ background-color: {_rgba(palette.surface_sunken, 0.90)}; border: 1px solid {palette.border}; border-radius: {RADIUS_LG}px; }}",
        )

        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(1, 1, 1, 1)
        track_layout.setSpacing(0)
        fill = QFrame(track)
        _call(fill, "setObjectName", f"progressFill_{attr_name}")
        _call(fill, "setStyleSheet", f"QFrame#progressFill_{attr_name} {{ background-color: {palette.primary}; border-radius: {RADIUS_LG}px; }}")
        track_layout.addWidget(fill, percent)
        track_layout.addStretch(max(100 - percent, 1))

        layout.addLayout(title_row)
        layout.addWidget(track)

        setattr(self, f"_{attr_name}", fill)
        setattr(self, f"_{value_attr}", value_label)
        return wrapper

    def _build_detail_list_card(self, title: str, object_name: str, *, is_risk: bool) -> QWidget:
        """构建详情列表卡片。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, object_name, background=_rgba(palette.surface_sunken, 0.92))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(SPACING_MD)
        title_label = QLabel(title, card)
        _set_label_style(title_label, size_token="font.size.md", color=palette.text, weight_token="font.weight.bold")
        title_row.addWidget(title_label)
        title_row.addStretch(1)
        title_row.addWidget(StatusBadge("需要关注" if is_risk else "优先放大", tone="warning" if is_risk else "success", parent=card))

        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(SPACING_SM)
        layout.addLayout(title_row)
        layout.addLayout(list_layout)
        layout.addStretch(1)

        if is_risk:
            self._detail_risk_layout = list_layout
        else:
            self._detail_highlight_layout = list_layout
        return card

    def _build_ai_strategy_panel(self) -> QWidget:
        """构建 AI 策略面板。"""

        palette = _palette()
        section = ContentSection("AI 策略建议", icon="✦", parent=self)

        intro_card = QFrame(section)
        _set_frame_panel(intro_card, "blueOceanAIIntro", background=_rgba(palette.primary, 0.08))
        intro_layout = QHBoxLayout(intro_card)
        intro_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        intro_layout.setSpacing(SPACING_LG)

        intro_column = QVBoxLayout()
        intro_column.setContentsMargins(0, 0, 0, 0)
        intro_column.setSpacing(SPACING_XS)
        intro_title = QLabel("AI 已根据蓝海机会、供给空白和内容热词生成布局建议。", intro_card)
        intro_desc = QLabel("你可以切换模型、角色和采样参数，快速输出不同版本的赛道进入策略。", intro_card)
        _call(intro_desc, "setWordWrap", True)
        _set_label_style(intro_title, size_token="font.size.md", color=palette.text, weight_token="font.weight.bold")
        _set_label_style(intro_desc, size_token="font.size.sm", color=palette.text_muted)
        intro_column.addWidget(intro_title)
        intro_column.addWidget(intro_desc)
        intro_layout.addLayout(intro_column, 1)

        self._ai_config_summary_label = QLabel("当前模型：OpenAI · gpt-4o · 数据分析师 · 温度 0.7", intro_card)
        _set_label_style(self._ai_config_summary_label, size_token="font.size.sm", color=palette.primary, weight_token="font.weight.bold")
        intro_layout.addWidget(self._ai_config_summary_label)

        split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.38, 0.62),
            minimum_sizes=(300, 360),
            parent=section,
        )
        split.set_widgets(self._build_ai_config_column(), self._build_ai_output_column())

        section.add_widget(intro_card)
        section.add_widget(split)
        return section

    def _build_ai_config_column(self) -> QWidget:
        """构建 AI 配置列。"""

        palette = _palette()
        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._ai_config_panel = AIConfigPanel(wrapper)
        self._ai_config_panel.set_config(
            {
                "provider": "openai",
                "model": "gpt-4o",
                "agent_role": "数据分析师",
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9,
            }
        )

        focus_card = QFrame(wrapper)
        _set_frame_panel(focus_card, "blueOceanAIFocus", background=_rgba(palette.accent_1, 0.08))
        focus_layout = QVBoxLayout(focus_card)
        focus_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        focus_layout.setSpacing(SPACING_SM)
        focus_title = QLabel("策略生成偏好", focus_card)
        focus_desc = QLabel("默认输出将优先强调站点优先级、达人切入、内容结构和利润带控制。", focus_card)
        _call(focus_desc, "setWordWrap", True)
        _set_label_style(focus_title, size_token="font.size.md", color=palette.text, weight_token="font.weight.bold")
        _set_label_style(focus_desc, size_token="font.size.sm", color=palette.text_muted)
        focus_layout.addWidget(focus_title)
        focus_layout.addWidget(focus_desc)
        chip_row = QHBoxLayout()
        chip_row.setContentsMargins(0, 0, 0, 0)
        chip_row.setSpacing(SPACING_SM)
        chip_row.addWidget(TagChip("站点优先级", tone="brand", parent=focus_card))
        chip_row.addWidget(TagChip("达人策略", tone="info", parent=focus_card))
        chip_row.addWidget(TagChip("利润控制", tone="warning", parent=focus_card))
        chip_row.addStretch(1)
        focus_layout.addLayout(chip_row)

        layout.addWidget(self._ai_config_panel)
        layout.addWidget(focus_card)
        layout.addStretch(1)
        return wrapper

    def _build_ai_output_column(self) -> QWidget:
        """构建 AI 输出列。"""

        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(SPACING_MD)
        regenerate_button = PrimaryButton("重新生成建议", wrapper)
        report_button = SecondaryButton("同步到调研报告", wrapper)
        action_row.addWidget(regenerate_button)
        action_row.addWidget(report_button)
        action_row.addStretch(1)
        action_row.addWidget(StatusBadge("策略已就绪", tone="success", parent=wrapper))

        self._strategy_output = StreamingOutputWidget(wrapper)
        layout.addLayout(action_row)
        layout.addWidget(self._strategy_output)

        _connect(regenerate_button.clicked, self._refresh_strategy_output)
        _connect(report_button.clicked, self._refresh_strategy_output)
        return wrapper

    def _build_category_analysis_section(self) -> QWidget:
        """构建分类分析区。"""

        section = ContentSection("分类分析卡片", icon="▦", parent=self)
        intro = QLabel(
            "结合市场增速、供给空白和竞争密度，对关键机会赛道进行分层，帮助运营团队快速排定进入优先级。",
            section,
        )
        _call(intro, "setWordWrap", True)
        _set_label_style(intro, size_token="font.size.md", color=_palette().text_muted)
        section.add_widget(intro)

        first_row = QWidget(section)
        first_layout = QHBoxLayout(first_row)
        first_layout.setContentsMargins(0, 0, 0, 0)
        first_layout.setSpacing(SPACING_LG)
        for snapshot in CATEGORY_SNAPSHOTS[:3]:
            first_layout.addWidget(self._build_category_card(snapshot), 1)

        second_row = QWidget(section)
        second_layout = QHBoxLayout(second_row)
        second_layout.setContentsMargins(0, 0, 0, 0)
        second_layout.setSpacing(SPACING_LG)
        for snapshot in CATEGORY_SNAPSHOTS[3:]:
            second_layout.addWidget(self._build_category_card(snapshot), 1)

        section.add_widget(first_row)
        section.add_widget(second_row)
        return section

    def _build_category_card(self, snapshot: CategorySnapshot) -> QWidget:
        """构建分类分析卡片。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, f"categoryCard_{snapshot.category}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_MD)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_MD)
        title_label = QLabel(snapshot.category, card)
        _set_label_style(title_label, size_token="font.size.lg", color=palette.text, weight_token="font.weight.bold")
        badge_map = {
            "brand": "brand",
            "success": "success",
            "info": "info",
            "warning": "warning",
            "error": "error",
        }
        header_row.addWidget(title_label)
        header_row.addStretch(1)
        header_row.addWidget(StatusBadge(f"机会 {snapshot.opportunity_score:.1f}", tone=badge_map.get(snapshot.tone, "brand"), parent=card))

        thesis_label = QLabel(snapshot.thesis, card)
        _call(thesis_label, "setWordWrap", True)
        _set_label_style(thesis_label, size_token="font.size.sm", color=palette.text_muted)

        stat_row = QHBoxLayout()
        stat_row.setContentsMargins(0, 0, 0, 0)
        stat_row.setSpacing(SPACING_SM)
        stat_row.addWidget(TagChip(f"增速 {snapshot.growth_rate}%", tone="success", parent=card))
        stat_row.addWidget(TagChip(f"缺口 {snapshot.gap_index}", tone="brand", parent=card))
        stat_row.addWidget(TagChip(f"竞争 {snapshot.competition_index}", tone="warning" if snapshot.competition_index < 50 else "error", parent=card))
        stat_row.addStretch(1)

        meta_card = QFrame(card)
        _set_frame_panel(meta_card, f"categoryMeta_{snapshot.category}", background=_rgba(palette.surface_sunken, 0.90))
        meta_layout = QVBoxLayout(meta_card)
        meta_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        meta_layout.setSpacing(SPACING_SM)
        region_label = QLabel(f"建议站点：{snapshot.recommended_region}", meta_card)
        price_label = QLabel(f"建议价格带：{snapshot.price_band}", meta_card)
        products_label = QLabel(f"主推形态：{'、'.join(snapshot.hero_products)}", meta_card)
        _call(products_label, "setWordWrap", True)
        for label in (region_label, price_label, products_label):
            _set_label_style(label, size_token="font.size.sm", color=palette.text)
            meta_layout.addWidget(label)

        layout.addLayout(header_row)
        layout.addWidget(thesis_label)
        layout.addLayout(stat_row)
        layout.addWidget(meta_card)
        layout.addStretch(1)
        return card

    def _build_gap_indicator_section(self) -> QWidget:
        """构建市场缺口指标区。"""

        section = ContentSection("市场缺口指标", icon="◌", parent=self)
        intro = QLabel("以下指标用于判断赛道是否值得进入：重点观察供给空白、利润弹性、达人缺口与合规复杂度。", section)
        _call(intro, "setWordWrap", True)
        _set_label_style(intro, size_token="font.size.md", color=_palette().text_muted)
        section.add_widget(intro)

        first_row = QWidget(section)
        first_layout = QHBoxLayout(first_row)
        first_layout.setContentsMargins(0, 0, 0, 0)
        first_layout.setSpacing(SPACING_LG)
        for indicator in GAP_INDICATORS[:3]:
            first_layout.addWidget(self._build_gap_indicator_card(indicator), 1)

        second_row = QWidget(section)
        second_layout = QHBoxLayout(second_row)
        second_layout.setContentsMargins(0, 0, 0, 0)
        second_layout.setSpacing(SPACING_LG)
        for indicator in GAP_INDICATORS[3:]:
            second_layout.addWidget(self._build_gap_indicator_card(indicator), 1)
        second_layout.addStretch(1)

        section.add_widget(first_row)
        section.add_widget(second_row)
        return section

    def _build_gap_indicator_card(self, indicator: GapIndicator) -> QWidget:
        """构建单个缺口指标卡片。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, f"gapCard_{indicator.title}")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_MD)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(SPACING_MD)
        title_label = QLabel(indicator.title, card)
        value_label = QLabel(indicator.value, card)
        _set_label_style(title_label, size_token="font.size.md", color=palette.text, weight_token="font.weight.bold")
        tone_color = {
            "brand": palette.primary,
            "success": palette.success,
            "info": palette.info,
            "warning": palette.warning,
            "error": palette.danger,
        }.get(indicator.tone, palette.primary)
        _set_label_style(value_label, size_token="font.size.xl", color=tone_color, weight_token="font.weight.bold")
        title_row.addWidget(title_label)
        title_row.addStretch(1)
        title_row.addWidget(value_label)

        subtitle = QLabel(indicator.subtitle, card)
        detail = QLabel(indicator.detail, card)
        _call(detail, "setWordWrap", True)
        _set_label_style(subtitle, size_token="font.size.sm", color=tone_color, weight_token="font.weight.semibold")
        _set_label_style(detail, size_token="font.size.sm", color=palette.text_muted)

        tag_row = QHBoxLayout()
        tag_row.setContentsMargins(0, 0, 0, 0)
        tag_row.setSpacing(SPACING_SM)
        tag_row.addWidget(StatusBadge(indicator.trend_text, tone=indicator.tone if indicator.tone in {"success", "warning", "error", "info", "brand"} else "brand", parent=card))
        for tag in indicator.tags:
            tag_row.addWidget(TagChip(tag, tone="neutral", parent=card))
        tag_row.addStretch(1)

        layout.addLayout(title_row)
        layout.addWidget(subtitle)
        layout.addWidget(detail)
        layout.addLayout(tag_row)
        layout.addStretch(1)
        return card

    def _build_trend_lab_section(self) -> QWidget:
        """构建趋势洞察实验室。"""

        section = ContentSection("趋势图表与洞察实验室", icon="◈", parent=self)
        intro = QLabel("通过趋势对比、缺口变化、活跃时段和热词词云，判断蓝海赛道是否具备持续放量能力。", section)
        _call(intro, "setWordWrap", True)
        _set_label_style(intro, size_token="font.size.md", color=_palette().text_muted)
        section.add_widget(intro)

        tab_bar = TabBar(section)
        tab_bar.add_tab("趋势总览", self._build_trend_overview_tab())
        tab_bar.add_tab("活跃时段", self._build_heatmap_tab())
        tab_bar.add_tab("需求热词", self._build_wordcloud_tab())
        section.add_widget(tab_bar)
        return section

    def _build_trend_overview_tab(self) -> QWidget:
        """构建趋势总览标签页。"""

        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        first_row = QWidget(wrapper)
        first_layout = QHBoxLayout(first_row)
        first_layout.setContentsMargins(0, 0, 0, 0)
        first_layout.setSpacing(SPACING_LG)
        self._demand_supply_chart = TrendComparison(
            labels=WEEK_LABELS,
            current_values=OPPORTUNITY_LOOKUP[DEFAULT_SELECTED_KEY].demand_series,
            compare_values=OPPORTUNITY_LOOKUP[DEFAULT_SELECTED_KEY].supply_series,
            current_name="需求热度",
            compare_name="供给热度",
            parent=first_row,
        )
        self._gap_bar_chart = ChartWidget(
            chart_type="bar",
            title="需求-供给缺口走势",
            labels=WEEK_LABELS,
            data=OPPORTUNITY_LOOKUP[DEFAULT_SELECTED_KEY].gap_series,
            unit="点",
            parent=first_row,
        )
        first_layout.addWidget(self._demand_supply_chart, 1)
        first_layout.addWidget(self._gap_bar_chart, 1)

        second_row = QWidget(wrapper)
        second_layout = QHBoxLayout(second_row)
        second_layout.setContentsMargins(0, 0, 0, 0)
        second_layout.setSpacing(SPACING_LG)
        self._growth_line_chart = ChartWidget(
            chart_type="line",
            title="机会维度得分分布",
            labels=DEMAND_SCORE_LABELS,
            data=(86, 90, 74, 88, 81, 67),
            unit="分",
            parent=second_row,
        )
        narrative_card = self._build_trend_narrative_card()
        second_layout.addWidget(self._growth_line_chart, 1)
        second_layout.addWidget(narrative_card, 1)

        layout.addWidget(first_row)
        layout.addWidget(second_row)
        return wrapper

    def _build_trend_narrative_card(self) -> QWidget:
        """构建趋势解读卡片。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, "blueOceanTrendNarrative")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_MD)

        title = QLabel("趋势解读", card)
        _set_label_style(title, size_token="font.size.lg", color=palette.text, weight_token="font.weight.bold")
        desc = QLabel(
            "当前默认类目在近 8 周呈现需求增速快于供给增速的结构性缺口。若连续 3 周保持正向缺口，可作为优先进入窗口。",
            card,
        )
        _call(desc, "setWordWrap", True)
        _set_label_style(desc, size_token="font.size.sm", color=palette.text_muted)

        bullet_layout = QVBoxLayout()
        bullet_layout.setContentsMargins(0, 0, 0, 0)
        bullet_layout.setSpacing(SPACING_SM)
        for text in (
            "需求增速在第 5 周后明显抬升，说明内容教育开始生效。",
            "供给增速保持缓慢上行，头部卖家尚未形成规模压制。",
            "缺口分值扩大的阶段，最适合用中腰部达人快速建认知。",
            "一旦 gap 曲线趋平，应及时转入利润保守模式。",
        ):
            bullet_layout.addWidget(self._create_bullet_label(text, tone="brand"))

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(bullet_layout)
        layout.addStretch(1)
        return card

    def _build_heatmap_tab(self) -> QWidget:
        """构建热力图标签页。"""

        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        intro_card = QFrame(wrapper)
        _set_frame_panel(intro_card, "blueOceanHeatmapIntro", background=_rgba(_palette().accent_4, 0.08))
        intro_layout = QHBoxLayout(intro_card)
        intro_layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        intro_layout.setSpacing(SPACING_LG)
        intro_label = QLabel("蓝海候选类目在晚间 19:00-22:00 的活跃度最强，周五至周日更适合做达人种草或重点内容投放。", intro_card)
        _call(intro_label, "setWordWrap", True)
        _set_label_style(intro_label, size_token="font.size.md", color=_palette().text)
        intro_layout.addWidget(intro_label, 1)
        intro_layout.addWidget(StatusBadge("晚间黄金时段", tone="success", parent=intro_card))

        self._heatmap_widget = HeatmapWidget(wrapper, values=HEATMAP_VALUES)

        layout.addWidget(intro_card)
        layout.addWidget(self._heatmap_widget)
        return wrapper

    def _build_wordcloud_tab(self) -> QWidget:
        """构建词云标签页。"""

        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._keyword_cloud = WordCloudWidget(wrapper, words=OPPORTUNITY_LOOKUP[DEFAULT_SELECTED_KEY].keyword_weights)

        side_card = QFrame(wrapper)
        _set_frame_panel(side_card, "blueOceanWordGuide")
        side_layout = QVBoxLayout(side_card)
        side_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        side_layout.setSpacing(SPACING_MD)
        title = QLabel("热词使用建议", side_card)
        _set_label_style(title, size_token="font.size.lg", color=_palette().text, weight_token="font.weight.bold")
        desc = QLabel("点击词云中的词条可作为素材方向或短视频标题提示。建议优先使用“场景 + 结果 + 情绪价值”的表达结构。", side_card)
        _call(desc, "setWordWrap", True)
        _set_label_style(desc, size_token="font.size.sm", color=_palette().text_muted)
        side_layout.addWidget(title)
        side_layout.addWidget(desc)
        for suggestion in (
            "把“睡眠监测”改写成“7 天睡眠变化看得见”。",
            "把“长续航”改写成“出差一周不用充电”。",
            "把“低噪音烘干”改写成“宠物不再害怕吹风”。",
            "把“停电应急”改写成“家里突然停电也不慌”。",
        ):
            side_layout.addWidget(self._create_bullet_label(suggestion, tone="info"))
        side_layout.addStretch(1)

        layout.addWidget(self._keyword_cloud, 2)
        layout.addWidget(side_card, 1)
        return wrapper

    def _build_footer_hint(self) -> QWidget:
        """构建底部提示。"""

        palette = _palette()
        card = QFrame(self)
        _set_frame_panel(card, "blueOceanFooterHint", background=_rgba(palette.primary, 0.08))
        layout = QHBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)
        summary = QLabel(
            "结论：优先推进智能穿戴、便携储能、宠物护理三条主线；以北美站为主阵地，用中腰部达人和场景型内容建立先发优势。",
            card,
        )
        _call(summary, "setWordWrap", True)
        _set_label_style(summary, size_token="font.size.md", color=palette.text, weight_token="font.weight.semibold")
        layout.addWidget(summary, 1)
        layout.addWidget(StatusBadge("建议本周执行", tone="brand", parent=card))
        return card

    def _bind_interactions(self) -> None:
        """绑定页面交互。"""

        if self._ai_config_panel is not None:
            _connect(self._ai_config_panel.config_changed, self._handle_config_changed)
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._refresh_filter_feedback)
        for dropdown in (self._site_filter, self._price_filter, self._competition_filter, self._cycle_filter):
            if dropdown is not None:
                _connect(dropdown.filter_changed, self._refresh_filter_feedback)
        if self._keyword_cloud is not None:
            _connect(self._keyword_cloud.word_clicked, self._handle_word_clicked)

    def _apply_selection(self, point_key: str) -> None:
        """应用选中的机会点。"""

        point = OPPORTUNITY_LOOKUP.get(point_key)
        if point is None:
            return
        self._selected_key = point_key
        for key, button in self._bubble_buttons.items():
            _call(button, "setChecked", key == point_key)

        if self._selected_name_label is not None:
            self._selected_name_label.setText(point.name)
        if self._selected_meta_label is not None:
            self._selected_meta_label.setText(f"{point.region_focus} ｜ {point.price_band} ｜ {point.scenario}")
        if self._selected_summary_label is not None:
            self._selected_summary_label.setText(point.ai_summary)
        if self._selected_competitor_value_label is not None:
            self._selected_competitor_value_label.setText(str(point.competitor_count))
        if self._selected_competitor_delta_label is not None:
            self._selected_competitor_delta_label.setText(point.competitor_delta_text)
        if self._selected_profit_value_label is not None:
            self._selected_profit_value_label.setText(f"{point.profit_rate:.1f}%")
        if self._selected_gap_value_label is not None:
            self._selected_gap_value_label.setText(str(point.market_gap_index))
        if self._selected_growth_value_label is not None:
            self._selected_growth_value_label.setText(str(point.conversion_potential))
        if self._selected_saturation_value_label is not None:
            self._selected_saturation_value_label.setText(f"{point.saturation}%")
        if self._selected_aov_value_label is not None:
            self._selected_aov_value_label.setText(f"¥{point.aov}")
        if self._selected_conversion_value_label is not None:
            self._selected_conversion_value_label.setText(str(point.conversion_potential))

        self._rebuild_detail_tags(point.tags)
        self._rebuild_detail_lists(point.highlights, point.risks)
        self._refresh_matrix_summary(point)
        self._refresh_trend_widgets(point)
        self._refresh_strategy_output()

    def _rebuild_detail_tags(self, tags: Sequence[str]) -> None:
        """刷新赛道标签。"""

        if self._detail_tags_layout is None:
            return
        _clear_layout(self._detail_tags_layout)
        for tag in tags:
            self._detail_tags_layout.addWidget(TagChip(tag, tone="brand", parent=self))
        self._detail_tags_layout.addStretch(1)

    def _rebuild_detail_lists(self, highlights: Sequence[str], risks: Sequence[str]) -> None:
        """刷新要点与风险列表。"""

        if self._detail_highlight_layout is not None:
            _clear_layout(self._detail_highlight_layout)
            for text in highlights:
                self._detail_highlight_layout.addWidget(self._create_bullet_label(text, tone="brand"))
        if self._detail_risk_layout is not None:
            _clear_layout(self._detail_risk_layout)
            for text in risks:
                self._detail_risk_layout.addWidget(self._create_bullet_label(text, tone="warning"))

    def _refresh_matrix_summary(self, point: OpportunityPoint) -> None:
        """刷新矩阵摘要。"""

        if self._matrix_summary_label is None:
            return
        self._matrix_summary_label.setText(
            f"当前选中「{point.name}」：{point.quadrant}，机会指数 {point.opportunity_score:.1f}，市场缺口 {point.market_gap_index}，建议优先在 {point.region_focus} 测试 {point.price_band} 价格带。"
        )

    def _refresh_trend_widgets(self, point: OpportunityPoint) -> None:
        """刷新趋势可视化组件。"""

        if self._demand_supply_chart is not None:
            self._demand_supply_chart.set_series(
                WEEK_LABELS,
                point.demand_series,
                point.supply_series,
                current_name="需求热度",
                compare_name="供给热度",
            )
        if self._gap_bar_chart is not None:
            self._gap_bar_chart.set_data(point.gap_series, WEEK_LABELS)
            self._gap_bar_chart.set_unit("点")
        if self._growth_line_chart is not None:
            self._growth_line_chart.set_data(
                (
                    float(point.market_gap_index),
                    float(point.demand_growth + 20),
                    float(max(point.competitor_count * 3, 20)),
                    float(point.market_gap_index),
                    float(point.conversion_potential),
                    float(point.profit_rate * 2),
                ),
                DEMAND_SCORE_LABELS,
            )
        if self._keyword_cloud is not None:
            self._keyword_cloud.set_words(point.keyword_weights)
        if self._heatmap_widget is not None:
            self._heatmap_widget.set_values(HEATMAP_VALUES)

    def _handle_config_changed(self, _config: dict[str, object]) -> None:
        """响应 AI 配置变化。"""

        if self._ai_config_panel is None or self._ai_config_summary_label is None:
            return
        config = self._ai_config_panel.config()
        self._ai_config_summary_label.setText(
            f"当前模型：{config['provider_label']} · {config['model']} · {config['agent_role']} · 温度 {config['temperature']:.1f}"
        )
        self._refresh_strategy_output()

    def _refresh_filter_feedback(self, *_args: object) -> None:
        """刷新筛选摘要。"""

        if self._filter_feedback_label is None:
            return
        search_text = self._search_bar.text().strip() if self._search_bar is not None else ""
        site_text = self._site_filter.current_text() if self._site_filter is not None else "全部"
        price_text = self._price_filter.current_text() if self._price_filter is not None else "全部"
        competition_text = self._competition_filter.current_text() if self._competition_filter is not None else "全部"
        cycle_text = self._cycle_filter.current_text() if self._cycle_filter is not None else "全部"
        prefix = f"搜索“{search_text}”｜" if search_text else ""
        self._filter_feedback_label.setText(f"{prefix}{site_text} ｜ {price_text} ｜ {competition_text} ｜ {cycle_text}")

    def _handle_word_clicked(self, text: str) -> None:
        """点击热词后联动搜索框。"""

        if self._search_bar is not None:
            self._search_bar.setText(text)

    def _refresh_strategy_output(self) -> None:
        """重新生成演示策略文本。"""

        if self._strategy_output is None:
            return
        point = OPPORTUNITY_LOOKUP[self._selected_key]
        config = self._ai_config_panel.config() if self._ai_config_panel is not None else {
            "provider_label": "OpenAI",
            "model": "gpt-4o",
            "agent_role": "数据分析师",
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9,
        }
        self._strategy_output.clear()
        self._strategy_output.set_loading(True)
        for chunk in self._compose_strategy_output(point, config):
            self._strategy_output.append_chunk(chunk)
        self._strategy_output.set_loading(False)
        self._strategy_output.set_token_usage(624, 1388)

    def _compose_strategy_output(self, point: OpportunityPoint, config: dict[str, object]) -> tuple[str, ...]:
        """组合 AI 策略输出文本。"""

        provider = str(config.get("provider_label", "OpenAI"))
        model = str(config.get("model", "gpt-4o"))
        role = str(config.get("agent_role", "数据分析师"))
        temperature = float(config.get("temperature", 0.7))
        return (
            f"【AI 策略推荐】\n当前使用 {provider} · {model}，角色设定为“{role}”，温度 {temperature:.1f}。\n\n",
            f"一、蓝海判断\n{point.name} 当前位于“{point.quadrant}”，机会指数 {point.opportunity_score:.1f}，市场缺口指数 {point.market_gap_index}。该类目最强信号来自 {point.region_focus}，建议先围绕 {point.scenario} 建立内容锚点。\n\n",
            "二、站点与价格带建议\n"
            f"优先站点：{point.region_focus}。\n"
            f"建议价格带：{point.price_band}。\n"
            f"当前预估利润率 {point.profit_rate:.1f}%，处于适合快速验证又能保留投放容错的区间。\n\n",
            "三、内容切入建议\n"
            + "\n".join(f"- {bullet}" for bullet in point.ai_bullets)
            + "\n\n",
            "四、执行节奏\n"
            f"第 1 阶段：围绕 {point.tags[0]} 与 {point.tags[1]} 做 5-8 条场景短视频，测试点击率与评论热词。\n"
            f"第 2 阶段：筛选 3-5 位中腰部达人做真实体验内容，重点验证“{point.keyword_weights[0][0]}”“{point.keyword_weights[1][0]}”的转化力。\n"
            "第 3 阶段：若连续两周需求热度高于供给热度 15 点以上，再进入放量与套装策略。\n\n",
            "五、风险提醒\n"
            + "\n".join(f"- {risk}" for risk in point.risks)
            + "\n\n",
            "六、AI 结论\n"
            + "\n".join(f"- {line}" for line in point.report_lines)
            + "\n",
        )

    def _create_bullet_label(self, text: str, *, tone: str) -> QWidget:
        """构建单条 bullet 文案。"""

        palette = _palette()
        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        dot = QLabel("•", wrapper)
        tone_color = {
            "brand": palette.primary,
            "info": palette.info,
            "warning": palette.warning,
            "success": palette.success,
        }.get(tone, palette.primary)
        _set_label_style(dot, size_token="font.size.lg", color=tone_color, weight_token="font.weight.bold")

        label = QLabel(text, wrapper)
        _call(label, "setWordWrap", True)
        _set_label_style(label, size_token="font.size.sm", color=palette.text)

        layout.addWidget(dot)
        layout.addWidget(label, 1)
        return wrapper

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        palette = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget {{
                background: transparent;
            }}
            QLabel#pageContainerTitle {{
                color: {palette.text};
            }}
            QLabel#pageContainerDescription {{
                color: {palette.text_muted};
            }}
            QFrame#blueOceanToolbar,
            QFrame#blueOceanSelectedTop,
            QFrame#blueOceanSelectedTags,
            QFrame#blueOceanAIIntro,
            QFrame#blueOceanTrendNarrative,
            QFrame#blueOceanHeatmapIntro,
            QFrame#blueOceanWordGuide,
            QFrame#blueOceanFooterHint,
            QFrame#blueOceanMatrixHeader,
            QFrame#blueOceanMatrixShell,
            QFrame#blueOceanMatrixSummary {{
                border-radius: {RADIUS_XL}px;
            }}
            """,
        )


__all__ = ["BlueOceanPage"]

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""爆款标题 - 创意灵感中心页面。"""

from dataclasses import dataclass
from typing import Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    ContentSection,
    FilterDropdown,
    FloatingActionButton,
    IconButton,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    PromptEditor,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatsBadge,
    StatusBadge,
    StreamingOutputWidget,
    TabBar,
    TagChip,
    TagInput,
    ThemedLineEdit,
    ThemedScrollArea,
    ThemedTextEdit,
)
from ...components.tags import BadgeTone
from ...components.inputs import SPACING_2XL
from ..base_page import BasePage

ACCENT = "#00F2EA"
ACCENT_SOFT = "rgba(0, 242, 234, 0.10)"
ACCENT_STRONG = "rgba(0, 242, 234, 0.18)"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"
DESKTOP_PAGE_MAX_WIDTH = 1920


@dataclass(frozen=True)
class TitleTemplate:
    """模板卡片演示数据。"""

    category: str
    name: str
    success_rate: str
    usage_count: str
    scene: str
    trait: str
    hook: str
    example_title: str
    prompt_hint: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class TrendingKeyword:
    """趋势关键词数据。"""

    word: str
    heat: str
    uplift: str
    note: str
    tone: str


@dataclass(frozen=True)
class OptimizationSuggestion:
    """标题优化建议数据。"""

    title: str
    summary: str
    expected_uplift: str
    priority: str
    tone: str


@dataclass(frozen=True)
class DensityMetric:
    """关键词密度与命中情况。"""

    keyword: str
    density: int
    target: str
    insight: str
    tone: str


@dataclass(frozen=True)
class ABVariant:
    """A/B 标题方案。"""

    label: str
    title: str
    expected_ctr: str
    delta: str
    audience: str
    winning_reason: str
    tone: str


@dataclass(frozen=True)
class HistoryItem:
    """标题历史记录。"""

    created_at: str
    title: str
    template_name: str
    ctr: str
    status: str
    note: str
    tone: str


@dataclass(frozen=True)
class ComplianceItem:
    """平台合规检查项。"""

    name: str
    result: str
    detail: str
    tone: str


@dataclass(frozen=True)
class LengthBenchmark:
    """字符长度参考。"""

    label: str
    range_text: str
    insight: str
    tone: str


TITLE_TEMPLATES: tuple[TitleTemplate, ...] = (
    TitleTemplate(
        category="悬念钩子",
        name="秘密揭晓型",
        success_rate="92% 成功率",
        usage_count="1.2w 次使用",
        scene="美妆护肤",
        trait="强情绪价值",
        hook="制造未知感，让用户愿意停下来找答案。",
        example_title="懂行的人都在偷偷回购的底妆，原来秘密在这里",
        prompt_hint="围绕“别人不知道、你先知道”的叙事写法展开。",
        keywords=("回购", "秘密", "懂行", "底妆"),
    ),
    TitleTemplate(
        category="悬念钩子",
        name="反常识开头型",
        success_rate="89% 成功率",
        usage_count="9.4k 次使用",
        scene="居家清洁",
        trait="停留时长高",
        hook="用违背直觉的开头打断用户滑动惯性。",
        example_title="不是越贵越好，这款清洁喷雾反而把厨房擦到发亮",
        prompt_hint="开头先否定常识，再给出具体收益。",
        keywords=("不是", "越贵越好", "清洁", "发亮"),
    ),
    TitleTemplate(
        category="悬念钩子",
        name="结果倒置型",
        success_rate="87% 成功率",
        usage_count="7.8k 次使用",
        scene="健身塑形",
        trait="评论互动强",
        hook="先给结果，再补过程，让用户自动追问。",
        example_title="瘦了 6 斤后我才明白，原来早餐顺序真的会影响掉秤",
        prompt_hint="优先写结果数据，再补一个关键认知变化。",
        keywords=("瘦了", "才明白", "早餐", "掉秤"),
    ),
    TitleTemplate(
        category="利益直给",
        name="省钱省时型",
        success_rate="88% 成功率",
        usage_count="8.5k 次使用",
        scene="家电工具",
        trait="高转化率",
        hook="直接交代利益点，适合强购买导向内容。",
        example_title="租房党闭眼冲：10 分钟搞定全屋清洁，电费几乎忽略不计",
        prompt_hint="前半句圈定人群，后半句给出明确收益。",
        keywords=("租房党", "闭眼冲", "10 分钟", "全屋清洁"),
    ),
    TitleTemplate(
        category="利益直给",
        name="解决痛点型",
        success_rate="86% 成功率",
        usage_count="7.1k 次使用",
        scene="母婴用品",
        trait="收藏率高",
        hook="用痛点场景切入，再给快速解决方案。",
        example_title="宝宝半夜总醒？我用这套安睡组合把哄睡时间砍半了",
        prompt_hint="标题要同时出现痛点与结果，减少空泛表达。",
        keywords=("宝宝", "总醒", "安睡", "砍半"),
    ),
    TitleTemplate(
        category="利益直给",
        name="清单承诺型",
        success_rate="84% 成功率",
        usage_count="6.8k 次使用",
        scene="女装穿搭",
        trait="点击稳定",
        hook="以“几件/几步/几套”承诺明确获得感。",
        example_title="通勤女生照着买就够了：3 套不出错早秋显瘦公式",
        prompt_hint="数字 + 场景 + 核心利益，适合清单内容。",
        keywords=("通勤", "照着买", "3 套", "显瘦"),
    ),
    TitleTemplate(
        category="认知偏差",
        name="误区拆解型",
        success_rate="85% 成功率",
        usage_count="6.2k 次使用",
        scene="理财知识",
        trait="评论讨论高",
        hook="指出大众误区，引发“原来我一直做错了”的心理。",
        example_title="别再盲目定投了，90% 新手亏在这个顺序上",
        prompt_hint="先点出错误动作，再压出具体风险比例。",
        keywords=("别再", "盲目", "90%", "新手"),
    ),
    TitleTemplate(
        category="认知偏差",
        name="对立观点型",
        success_rate="83% 成功率",
        usage_count="5.5k 次使用",
        scene="职场成长",
        trait="分享率高",
        hook="用立场对冲激发停留和表达欲。",
        example_title="真正拉开差距的，从来不是加班，而是下班后这 1 小时",
        prompt_hint="用“不是 A，而是 B”制造观点冲突。",
        keywords=("拉开差距", "不是", "而是", "1 小时"),
    ),
    TitleTemplate(
        category="认知偏差",
        name="看似普通型",
        success_rate="82% 成功率",
        usage_count="4.9k 次使用",
        scene="厨房小家电",
        trait="适合种草",
        hook="强调“看起来普通，实际很强”，适合冷启动。",
        example_title="别小看这个煮锅，周末做一顿四菜一汤真的省出半小时",
        prompt_hint="突出产品低预期与高体验的反差。",
        keywords=("别小看", "煮锅", "四菜一汤", "省时间"),
    ),
    TitleTemplate(
        category="场景共鸣",
        name="生活瞬间型",
        success_rate="91% 成功率",
        usage_count="1.0w 次使用",
        scene="家居香氛",
        trait="情绪价值强",
        hook="把产品放进一个具体且可感知的日常时刻里。",
        example_title="下班回家一开门闻到这个味道，疲惫真的会被瞬间关掉",
        prompt_hint="场景要具体到时间、动作、感受。",
        keywords=("下班回家", "一开门", "疲惫", "瞬间"),
    ),
    TitleTemplate(
        category="场景共鸣",
        name="用户代入型",
        success_rate="88% 成功率",
        usage_count="8.2k 次使用",
        scene="旅行收纳",
        trait="完播率高",
        hook="直接点名用户身份，让目标人群立刻对号入座。",
        example_title="行李箱总是乱的人，一定要试试这套旅行分区收纳法",
        prompt_hint="前半句精准点人群，后半句给解决方法。",
        keywords=("行李箱", "总是乱", "一定要试", "分区收纳"),
    ),
    TitleTemplate(
        category="场景共鸣",
        name="节日场景型",
        success_rate="86% 成功率",
        usage_count="7.6k 次使用",
        scene="礼盒食品",
        trait="送礼转化高",
        hook="通过节点时机强化购买冲动和分享心智。",
        example_title="中秋送长辈别再送老三样，这盒坚果礼真的体面又好吃",
        prompt_hint="加入节日、对象与替代方案，更容易成交。",
        keywords=("中秋", "长辈", "别再送", "体面"),
    ),
    TitleTemplate(
        category="数据证明",
        name="实测结论型",
        success_rate="90% 成功率",
        usage_count="9.9k 次使用",
        scene="个护电器",
        trait="信任感强",
        hook="用时间和数据证明结果，降低用户决策风险。",
        example_title="连用 14 天后我只想说，这支电动牙刷真的把黄渍刷淡了",
        prompt_hint="时间锚点 + 结果反馈 + 情绪表达。",
        keywords=("连用 14 天", "只想说", "真的", "黄渍"),
    ),
    TitleTemplate(
        category="数据证明",
        name="对比测试型",
        success_rate="87% 成功率",
        usage_count="7.3k 次使用",
        scene="护发精油",
        trait="信服度高",
        hook="以同条件对比打消夸张感，适合效果型商品。",
        example_title="同样吹头发 5 分钟，为什么用了它之后毛躁感少了这么多？",
        prompt_hint="保留测试条件，突出变化结果。",
        keywords=("同样", "5 分钟", "为什么", "毛躁感"),
    ),
    TitleTemplate(
        category="数据证明",
        name="人群样本型",
        success_rate="84% 成功率",
        usage_count="5.8k 次使用",
        scene="办公数码",
        trait="商务感强",
        hook="用团队/多人反馈提升可信度。",
        example_title="办公室 7 个人试完都改口了，这个支架比我想象中稳太多",
        prompt_hint="多人样本 + 态度反转，更容易建立真实感。",
        keywords=("7 个人", "改口了", "支架", "稳"),
    ),
)

TRENDING_KEYWORDS: tuple[TrendingKeyword, ...] = (
    TrendingKeyword("建议收藏", "热度 98", "+32%", "适合知识、经验、避坑内容", "brand"),
    TrendingKeyword("真的会谢", "热度 93", "+24%", "适合反差、惊喜、效果显著型标题", "warning"),
    TrendingKeyword("别盲买", "热度 90", "+19%", "适合测评、对比、避坑类转化内容", "error"),
    TrendingKeyword("回购无数次", "热度 88", "+21%", "适合复购型商品与口碑种草", "success"),
    TrendingKeyword("被问爆了", "热度 84", "+17%", "适合高颜值、强社交传播商品", "info"),
    TrendingKeyword("租房党闭眼冲", "热度 81", "+25%", "适合工具、家清、小家电场景", "brand"),
    TrendingKeyword("早知道就好了", "热度 79", "+16%", "适合误区纠正与认知升级内容", "warning"),
    TrendingKeyword("原来差别这么大", "热度 76", "+14%", "适合前后对比、实测结论型内容", "info"),
)

OPTIMIZATION_SUGGESTIONS: tuple[OptimizationSuggestion, ...] = (
    OptimizationSuggestion("把利益点前置", "当前标题情绪值足够，但“省时”利益点出现偏后，建议前 10 字直接交代收益。", "预估 CTR +0.8%", "高优先", "brand"),
    OptimizationSuggestion("补充人群标签", "标题已经有痛点表达，可以增加“租房党 / 通勤党 / 宝妈”等身份词提升代入感。", "预估 收藏率 +12%", "高优先", "success"),
    OptimizationSuggestion("加入轻度数字锚点", "数字会增强确定感，建议加入“3 步 / 10 分钟 / 连用 7 天”等实感信息。", "预估 完播率 +9%", "中优先", "info"),
    OptimizationSuggestion("减少口语重复", "当前标题中“真的”“太”出现较多，建议保留 1 个，避免信息密度下降。", "预估 可读性 +15%", "中优先", "warning"),
    OptimizationSuggestion("保留一个悬念尾钩", "若标题已写清利益，可在尾部保留一个“原来关键在这一步”的悬念补强停留。", "预估 停留率 +6%", "中优先", "brand"),
    OptimizationSuggestion("替换弱动词", "“不错、挺好、方便”偏弱，可换成“省一半、稳住、少踩坑”这类更强结果词。", "预估 转化率 +5%", "低优先", "error"),
)

DEFAULT_DENSITY_METRICS: tuple[DensityMetric, ...] = (
    DensityMetric("建议收藏", 28, "20%-35%", "高频热词命中稳定，适合作为首钩或尾钩。", "brand"),
    DensityMetric("租房党", 21, "15%-25%", "人群标签清晰，利于推荐系统识别受众。", "success"),
    DensityMetric("10 分钟", 18, "10%-18%", "时长锚点恰当，能提升确定性。", "info"),
    DensityMetric("全屋清洁", 16, "12%-20%", "核心场景表达明确，建议保留。", "brand"),
    DensityMetric("闭眼冲", 11, "8%-12%", "购买推动力足够，但不宜叠加过多强促词。", "warning"),
)

AB_VARIANTS: tuple[ABVariant, ...] = (
    ABVariant(
        label="A",
        title="租房党闭眼冲：10 分钟搞定全屋清洁，电费几乎忽略不计",
        expected_ctr="4.8%",
        delta="当前最佳",
        audience="租房党 / 上班族 / 懒人家清",
        winning_reason="利益点极清晰，时间锚点与人群标签同时出现。",
        tone="brand",
    ),
    ABVariant(
        label="B",
        title="别再盲买清洁工具了，这台机器才是厨房和客厅的省时答案",
        expected_ctr="4.1%",
        delta="-15%",
        audience="新居用户 / 预算敏感型人群",
        winning_reason="误区感更强，但场景不如 A 具体。",
        tone="warning",
    ),
    ABVariant(
        label="C",
        title="我后悔没早点入：周末打扫终于不用满屋拖来拖去了",
        expected_ctr="3.9%",
        delta="-19%",
        audience="情绪驱动型点击人群",
        winning_reason="情绪价值在线，但利益表达略模糊。",
        tone="info",
    ),
    ABVariant(
        label="D",
        title="同样 30 分钟家务，为什么用了它之后我还能多刷一集剧？",
        expected_ctr="4.3%",
        delta="-10%",
        audience="女性家居 / 效率提升人群",
        winning_reason="悬念感更足，适合内容流量冷启动。",
        tone="success",
    ),
)

HISTORY_ITEMS: tuple[HistoryItem, ...] = (
    HistoryItem("今天 09:40", "通勤女生照着买就够了：3 套不出错早秋显瘦公式", "清单承诺型", "4.2%", "已发布", "收藏率高于账号均值 18%", "success"),
    HistoryItem("今天 08:15", "别再盲目定投了，90% 新手亏在这个顺序上", "误区拆解型", "3.8%", "待测试", "适合理财账号冷启动话题", "warning"),
    HistoryItem("昨天 21:10", "下班回家一开门闻到这个味道，疲惫真的会被瞬间关掉", "生活瞬间型", "5.1%", "已爆发", "评论区情绪共鸣词集中出现", "brand"),
    HistoryItem("昨天 16:30", "宝宝半夜总醒？我用这套安睡组合把哄睡时间砍半了", "解决痛点型", "4.7%", "已发布", "人群标签命中准，适合继续迭代", "success"),
    HistoryItem("周六 19:50", "懂行的人都在偷偷回购的底妆，原来秘密在这里", "秘密揭晓型", "4.5%", "复盘中", "标题停留强，转化仍有上升空间", "info"),
    HistoryItem("周六 13:20", "办公室 7 个人试完都改口了，这个支架比我想象中稳太多", "人群样本型", "3.6%", "已发布", "商务人群反馈偏好明显", "neutral"),
    HistoryItem("周五 11:05", "别小看这个煮锅，周末做一顿四菜一汤真的省出半小时", "看似普通型", "4.0%", "已发布", "适合叠加“租房党”标签再测一轮", "warning"),
    HistoryItem("周四 18:00", "中秋送长辈别再送老三样，这盒坚果礼真的体面又好吃", "节日场景型", "5.4%", "已爆发", "节点标题与礼赠场景高度匹配", "brand"),
)

COMPLIANCE_ITEMS: tuple[ComplianceItem, ...] = (
    ComplianceItem("绝对化表述", "通过", "未检测到“最、第一、永久”等高风险绝对化词。", "success"),
    ComplianceItem("收益承诺", "提醒", "“闭眼冲”具备强引导性，建议搭配具体场景降低夸张感。", "warning"),
    ComplianceItem("医疗功效", "通过", "当前标题未触发疾病治疗、疗效承诺类敏感表述。", "success"),
    ComplianceItem("价格误导", "通过", "未出现“全网最低、只要 9.9”等敏感价格引导。", "success"),
    ComplianceItem("人群歧义", "优化", "若使用“懒人必备”，建议替换为“忙碌上班族更适合”。", "info"),
)

LENGTH_BENCHMARKS: tuple[LengthBenchmark, ...] = (
    LengthBenchmark("平台舒适区", "18-28 字", "最适合 TikTok 快节奏滑动场景，推荐优先控制在此范围。", "brand"),
    LengthBenchmark("强转化区间", "20-32 字", "当需要同时写人群、利益与场景时，长度略长但转化承接更稳。", "success"),
    LengthBenchmark("风险提醒", "超过 36 字", "信息密度过高，首屏识别变慢，建议拆掉一个修饰短语。", "warning"),
)

DEFAULT_PROMPT = """你是 TK-OPS 的标题策划师，请基于以下信息生成 6 个适合 TikTok Shop 的中文爆款标题。

要求：
1. 标题必须口语化、具体、有用户代入感。
2. 优先前置人群标签或核心利益点。
3. 至少 2 个标题使用悬念钩子，至少 2 个标题使用利益直给。
4. 每个标题控制在 18-32 字之间。
5. 避免绝对化承诺、夸大医疗功效、虚假价格引导。
6. 输出时附带“适用模板”“关键词建议”“推荐投放场景”。
"""

DEFAULT_BRIEF = """商品：无线手持清洁机
卖点：轻、续航长、厨房油污和沙发碎屑都能处理
目标人群：租房党、双职工家庭、懒人打扫用户
内容场景：周末做家务、下班回家快速收拾、厨房重油污实测
品牌风格：直接、靠谱、有生活感，不要堆砌空洞形容词
"""

DEFAULT_TITLE = "租房党闭眼冲：10 分钟搞定全屋清洁，电费几乎忽略不计"


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用 Qt 方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """安全连接信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _set_word_wrap(label: QLabel) -> None:
    """安全开启换行。"""

    _call(label, "setWordWrap", True)


def _layout_count(layout: object) -> int:
    """兼容获取布局项数量。"""

    counter = getattr(layout, "count", None)
    if callable(counter):
        value = counter()
        if isinstance(value, int):
            return value
    items = getattr(layout, "_items", [])
    return len(items) if isinstance(items, list) else 0


def _clear_layout(layout: object) -> None:
    """兼容清空布局。"""

    take_at = getattr(layout, "takeAt", None)
    if callable(take_at):
        while _layout_count(layout) > 0:
            item = take_at(0)
            if item is None:
                break
            widget_getter = getattr(item, "widget", None)
            nested_layout_getter = getattr(item, "layout", None)
            widget = widget_getter() if callable(widget_getter) else None
            nested_layout = nested_layout_getter() if callable(nested_layout_getter) else None
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")
            if nested_layout is not None:
                _clear_layout(nested_layout)
        return

    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


def _tone_badge(tone: str) -> BadgeTone:
    """兼容 tone 名称。"""

    if tone == "success":
        return "success"
    if tone == "warning":
        return "warning"
    if tone == "error":
        return "error"
    if tone == "info":
        return "info"
    if tone == "brand":
        return "brand"
    return "neutral"


def _frame_style(*, dashed: bool = False, highlight: bool = False) -> str:
    """统一局部卡片样式。"""

    border = ACCENT if highlight else "palette(midlight)"
    border_style = "dashed" if dashed else "solid"
    background = ACCENT_SOFT if highlight else "palette(base)"
    return f"""
        QFrame {{
            background: {background};
            border: 1px {border_style} {border};
            border-radius: 14px;
        }}
        QLabel {{
            background: transparent;
        }}
        QPushButton {{
            border-radius: 10px;
        }}
    """


def _muted_label_style() -> str:
    """浅色辅助文案。"""

    return "color: palette(mid); background: transparent; font-size: 12px;"


def _title_label_style() -> str:
    """标题文案样式。"""

    return "color: palette(text); background: transparent; font-size: 16px; font-weight: 700;"


def _section_hint_style() -> str:
    """区块描述样式。"""

    return f"color: {ACCENT}; background: transparent; font-size: 12px; font-weight: 700;"


class ViralTitlePage(BasePage):
    """爆款标题 - 创意灵感中心。"""

    default_route_id: RouteId = RouteId("viral_title_studio")
    default_display_name: str = "爆款标题"
    default_icon_name: str = "auto_awesome"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._templates: list[TitleTemplate] = list(TITLE_TEMPLATES)
        self._history_items: list[HistoryItem] = list(HISTORY_ITEMS)
        self._active_scene_filter = "全部"
        self._template_keyword = ""
        self._history_keyword = ""
        self._density_metrics: list[DensityMetric] = list(DEFAULT_DENSITY_METRICS)
        self._template_count_label: QLabel | None = None
        self._template_gallery_host: QWidget | None = None
        self._template_gallery_layout: QVBoxLayout | None = None
        self._history_host: QWidget | None = None
        self._history_layout: QVBoxLayout | None = None
        self._density_host: QWidget | None = None
        self._density_layout: QVBoxLayout | None = None
        self._suggestion_host: QWidget | None = None
        self._suggestion_layout: QVBoxLayout | None = None
        self._compliance_host: QWidget | None = None
        self._compliance_layout: QVBoxLayout | None = None
        self._ab_host: QWidget | None = None
        self._ab_layout: QVBoxLayout | None = None
        self._title_input: ThemedLineEdit | None = None
        self._brief_input: ThemedTextEdit | None = None
        self._keyword_input: TagInput | None = None
        self._prompt_editor: PromptEditor | None = None
        self._config_panel: AIConfigPanel | None = None
        self._streaming_output: StreamingOutputWidget | None = None
        self._char_count_value: QLabel | None = None
        self._length_score_value: QLabel | None = None
        self._emotion_score_value: QLabel | None = None
        self._keyword_score_value: QLabel | None = None
        self._template_hint_label: QLabel | None = None
        self._model_summary_label: QLabel | None = None
        self._history_count_label: QLabel | None = None
        self._selected_template_name = "省钱省时型"
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建爆款标题页面。"""

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        header_actions = [
            PrimaryButton("智能优化", self, icon_text="✦"),
            IconButton("⋯", "更多操作", self),
        ]
        page = PageContainer(
            title="爆款标题",
            description="AI 驱动的标题增长工作台，覆盖模板灵感、生成优化、A/B 对比与历史复盘。",
            actions=header_actions,
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )

        scroll = ThemedScrollArea(page)
        scroll.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.content_layout.setSpacing(SPACING_2XL)

        scroll.add_widget(self._build_overview_section())
        scroll.add_widget(self._build_template_gallery_section())
        scroll.add_widget(self._build_generation_workspace_section())
        scroll.add_widget(self._build_analysis_workspace_section())
        scroll.add_widget(self._build_history_section())
        scroll.add_widget(self._build_footer_actions())

        page.add_widget(scroll)
        self.layout.addWidget(page)

        self._seed_default_values()
        self._bind_events()
        self._render_template_gallery()
        self._render_suggestions()
        self._render_keyword_density()
        self._render_compliance_checks()
        self._render_ab_variants()
        self._render_history_rows()
        self._update_title_metrics()
        self._update_model_summary()
        self._render_generated_output(initial=True)

    def _build_overview_section(self) -> QWidget:
        section = ContentSection("标题增长概览", icon="✦", parent=self)

        top_hint_row = QHBoxLayout()
        top_hint_row.setContentsMargins(0, 0, 0, 0)
        top_hint_row.setSpacing(10)

        status = StatusBadge("模型已就绪", tone="success", parent=section)
        trend = StatusBadge("爆词上升中", tone="brand", parent=section)
        window = StatusBadge("最佳发布时间 19:00-22:00", tone="info", parent=section)

        top_hint_row.addWidget(status)
        top_hint_row.addWidget(trend)
        top_hint_row.addWidget(window)
        top_hint_row.addStretch(1)
        section.content_layout.addLayout(top_hint_row)

        kpi_row = QHBoxLayout()
        kpi_row.setContentsMargins(0, 0, 0, 0)
        kpi_row.setSpacing(12)

        kpi_row.addWidget(
            KPICard(
                title="模板命中率",
                value="92%",
                trend="up",
                percentage="+8.4%",
                caption="近 7 天平均",
                sparkline_data=[67, 72, 75, 79, 84, 88, 92],
                parent=section,
            )
        )
        kpi_row.addWidget(
            KPICard(
                title="预估点击率",
                value="4.8%",
                trend="up",
                percentage="+0.7%",
                caption="优于行业均值",
                sparkline_data=[2.8, 3.0, 3.4, 3.8, 4.1, 4.4, 4.8],
                parent=section,
            )
        )
        kpi_row.addWidget(
            KPICard(
                title="收藏驱动指数",
                value="8.4/10",
                trend="flat",
                percentage="稳定",
                caption="内容获得感高",
                sparkline_data=[8.0, 8.1, 8.2, 8.1, 8.3, 8.4, 8.4],
                parent=section,
            )
        )
        section.content_layout.addLayout(kpi_row)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(12)

        insight_card = InfoCard(
            title="今日策略建议",
            description="优先使用“租房党 / 通勤党 / 宝妈”这类身份词，叠加“10 分钟 / 连用 7 天”等数字锚点，当前账号在“场景 + 利益”结构上的点击优势最明显。",
            icon="◎",
            action_text="查看策略说明",
            parent=section,
        )
        bottom_row.addWidget(insight_card, 2)

        badge_stack = QWidget(section)
        badge_layout = QVBoxLayout(badge_stack)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(10)
        badge_layout.addWidget(StatsBadge("爆词命中", "6/8", "✦", "brand", badge_stack))
        badge_layout.addWidget(StatsBadge("情绪强度", "88%", "▲", "success", badge_stack))
        badge_layout.addWidget(StatsBadge("可读性", "92%", "◎", "info", badge_stack))
        bottom_row.addWidget(badge_stack, 1)

        section.content_layout.addLayout(bottom_row)
        return section

    def _build_template_gallery_section(self) -> QWidget:
        section = ContentSection("热门爆款模板", icon="◈", parent=self)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)

        template_search = SearchBar("搜索模板名称、场景或关键词...", None)
        _connect(template_search.search_changed, self._on_template_search_changed)
        controls.addWidget(template_search, 2)

        scene_filter = FilterDropdown("内容场景", ["全部", "美妆护肤", "家电工具", "母婴用品", "理财知识", "家居香氛", "旅行收纳"], include_all=False, parent=None)
        _connect(scene_filter.filter_changed, self._on_scene_filter_changed)
        scene_filter.set_current_text("全部")
        controls.addWidget(scene_filter, 1)

        self._template_count_label = QLabel("已加载 14 个模板", section)
        template_count_label = self._template_count_label
        if template_count_label is not None:
            template_count_label.setStyleSheet(_section_hint_style())
            controls.addWidget(template_count_label)

        section.content_layout.addLayout(controls)

        keyword_row = QWidget(section)
        keyword_layout = QHBoxLayout(keyword_row)
        keyword_layout.setContentsMargins(0, 0, 0, 0)
        keyword_layout.setSpacing(8)
        for keyword in TRENDING_KEYWORDS[:6]:
            keyword_layout.addWidget(TagChip(f"#{keyword.word}", tone=_tone_badge(keyword.tone), parent=keyword_row))
        keyword_layout.addStretch(1)
        section.content_layout.addWidget(keyword_row)

        self._template_gallery_host = QWidget(section)
        self._template_gallery_layout = QVBoxLayout(self._template_gallery_host)
        template_gallery_layout = self._template_gallery_layout
        if template_gallery_layout is not None:
            template_gallery_layout.setContentsMargins(0, 0, 0, 0)
            template_gallery_layout.setSpacing(14)
        section.content_layout.addWidget(self._template_gallery_host)
        return section

    def _build_generation_workspace_section(self) -> QWidget:
        section = ContentSection("AI 标题生成工作台", icon="⚙", parent=self)

        split = SplitPanel("horizontal", split_ratio=(0.64, 0.36), minimum_sizes=(720, 420), parent=section)
        split.set_widgets(self._build_editor_panel(), self._build_ai_panel())
        section.content_layout.addWidget(split)
        return section

    def _build_analysis_workspace_section(self) -> QWidget:
        host = SplitPanel("horizontal", split_ratio=(0.6, 0.4), minimum_sizes=(760, 540), parent=self)
        host.set_widgets(self._build_strategy_section(), self._build_ab_test_section())
        return host

    def _build_editor_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        summary_frame = QFrame(panel)
        summary_frame.setStyleSheet(_frame_style(highlight=True))
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)

        title = QLabel("当前创作标题", summary_frame)
        title.setStyleSheet(_title_label_style())
        subtitle = QLabel("建议控制在 18-32 字，优先“人群 / 利益 / 场景”三要素。", summary_frame)
        subtitle.setStyleSheet(_muted_label_style())

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(4)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self._template_hint_label = QLabel("当前模板：省钱省时型", summary_frame)
        template_hint_label = self._template_hint_label
        if template_hint_label is not None:
            template_hint_label.setStyleSheet(_section_hint_style())

        header_row.addLayout(title_col)
        header_row.addStretch(1)
        if template_hint_label is not None:
            header_row.addWidget(template_hint_label)
        summary_layout.addLayout(header_row)

        self._title_input = ThemedLineEdit(
            label="主标题",
            placeholder="输入主标题，或从模板、AI 结果中一键带入",
            helper_text="建议前半句优先写核心利益点，尾部保留 1 个轻悬念。",
            parent=None,
        )
        summary_layout.addWidget(self._title_input)

        metric_row = QHBoxLayout()
        metric_row.setContentsMargins(0, 0, 0, 0)
        metric_row.setSpacing(10)
        metric_row.addWidget(self._build_metric_tile("字符计数", "0 / 64", "品牌舒适区 18-28 字", "char_count"))
        metric_row.addWidget(self._build_metric_tile("长度评分", "优", "当前长度适合推荐流", "length_score"))
        metric_row.addWidget(self._build_metric_tile("情绪张力", "高", "悬念与利益表达均衡", "emotion_score"))
        metric_row.addWidget(self._build_metric_tile("关键词浓度", "强", "热点词与人群词匹配", "keyword_score"))
        summary_layout.addLayout(metric_row)

        root.addWidget(summary_frame)

        self._brief_input = ThemedTextEdit(
            label="商品 / 视频简报",
            placeholder="补充商品卖点、视频场景、用户痛点、目标人群和账号风格",
            parent=None,
        )
        root.addWidget(self._brief_input)

        self._keyword_input = TagInput(label="趋势关键词池", placeholder="输入关键词后回车，支持粘贴多个词", parent=None)
        root.addWidget(self._keyword_input)

        quick_keyword_section = QFrame(panel)
        quick_keyword_section.setStyleSheet(_frame_style())
        quick_keyword_layout = QVBoxLayout(quick_keyword_section)
        quick_keyword_layout.setContentsMargins(16, 14, 16, 14)
        quick_keyword_layout.setSpacing(10)

        quick_title = QLabel("可直接插入的热词", quick_keyword_section)
        quick_title.setStyleSheet(_title_label_style())
        quick_keyword_layout.addWidget(quick_title)

        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(8)
        for keyword in TRENDING_KEYWORDS[:4]:
            row1.addWidget(self._build_keyword_action_button(keyword.word))
        row1.addStretch(1)

        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(8)
        for keyword in TRENDING_KEYWORDS[4:8]:
            row2.addWidget(self._build_keyword_action_button(keyword.word))
        row2.addStretch(1)

        quick_keyword_layout.addLayout(row1)
        quick_keyword_layout.addLayout(row2)
        root.addWidget(quick_keyword_section)

        benchmark_section = QFrame(panel)
        benchmark_section.setStyleSheet(_frame_style())
        benchmark_layout = QVBoxLayout(benchmark_section)
        benchmark_layout.setContentsMargins(16, 14, 16, 14)
        benchmark_layout.setSpacing(10)

        benchmark_title = QLabel("字符长度策略", benchmark_section)
        benchmark_title.setStyleSheet(_title_label_style())
        benchmark_layout.addWidget(benchmark_title)
        for benchmark in LENGTH_BENCHMARKS:
            benchmark_layout.addWidget(self._build_length_row(benchmark, benchmark_section))
        root.addWidget(benchmark_section)

        return panel

    def _build_ai_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._config_panel = AIConfigPanel(panel)
        root.addWidget(self._config_panel)

        summary_frame = QFrame(panel)
        summary_frame.setStyleSheet(_frame_style(highlight=True))
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(16, 14, 16, 14)
        summary_layout.setSpacing(8)

        summary_title = QLabel("生成配置摘要", summary_frame)
        summary_title.setStyleSheet(_title_label_style())
        self._model_summary_label = QLabel("OpenAI · gpt-4o · 文案专家 · 温度 0.7", summary_frame)
        model_summary_label = self._model_summary_label
        if model_summary_label is not None:
            model_summary_label.setStyleSheet(_section_hint_style())
        summary_desc = QLabel("建议标题生成使用中高温度；做 A/B 精修时可降低到 0.5-0.6。", summary_frame)
        summary_desc.setStyleSheet(_muted_label_style())
        _set_word_wrap(summary_desc)

        summary_layout.addWidget(summary_title)
        if model_summary_label is not None:
            summary_layout.addWidget(model_summary_label)
        summary_layout.addWidget(summary_desc)
        root.addWidget(summary_frame)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)

        generate_button = PrimaryButton("生成标题", panel, icon_text="✦")
        _connect(generate_button.clicked, self._on_generate_clicked)
        action_row.addWidget(generate_button)

        refresh_button = SecondaryButton("再来一组", panel, icon_text="↻")
        _connect(refresh_button.clicked, self._on_regenerate_clicked)
        action_row.addWidget(refresh_button)

        optimize_button = SecondaryButton("套用最佳方案", panel, icon_text="◎")
        _connect(optimize_button.clicked, self._apply_best_variant)
        action_row.addWidget(optimize_button)
        root.addLayout(action_row)

        self._prompt_editor = PromptEditor(panel)
        root.addWidget(self._prompt_editor)

        self._streaming_output = StreamingOutputWidget(panel)
        root.addWidget(self._streaming_output)
        return panel

    def _build_strategy_section(self) -> QWidget:
        section = ContentSection("优化建议与分析看板", icon="☰", parent=self)

        tabs = TabBar(section)
        tabs.add_tab("优化建议", self._build_suggestion_tab())
        tabs.add_tab("关键词密度", self._build_density_tab())
        tabs.add_tab("平台合规", self._build_compliance_tab())

        section.content_layout.addWidget(tabs)
        return section

    def _build_suggestion_tab(self) -> QWidget:
        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        intro = InfoCard(
            title="当前优化方向",
            description="从账号表现看，你的标题在“场景 + 利益”结构中点击更稳定；若要放大停留，可补一个轻悬念尾钩。",
            icon="▲",
            action_text="同步到标题",
            parent=tab,
        )
        root.addWidget(intro)

        self._suggestion_host = QWidget(tab)
        self._suggestion_layout = QVBoxLayout(self._suggestion_host)
        suggestion_layout = self._suggestion_layout
        if suggestion_layout is not None:
            suggestion_layout.setContentsMargins(0, 0, 0, 0)
            suggestion_layout.setSpacing(10)
        root.addWidget(self._suggestion_host)
        return tab

    def _build_density_tab(self) -> QWidget:
        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        insight = QFrame(tab)
        insight.setStyleSheet(_frame_style())
        insight_layout = QVBoxLayout(insight)
        insight_layout.setContentsMargins(16, 14, 16, 14)
        insight_layout.setSpacing(8)
        density_title = QLabel("关键词密度诊断", insight)
        density_title.setStyleSheet(_title_label_style())
        density_desc = QLabel("系统会根据标题文本、关键词池与热点词趋势，估算关键词密度与推荐阈值。", insight)
        density_desc.setStyleSheet(_muted_label_style())
        _set_word_wrap(density_desc)
        insight_layout.addWidget(density_title)
        insight_layout.addWidget(density_desc)
        root.addWidget(insight)

        self._density_host = QWidget(tab)
        self._density_layout = QVBoxLayout(self._density_host)
        density_layout = self._density_layout
        if density_layout is not None:
            density_layout.setContentsMargins(0, 0, 0, 0)
            density_layout.setSpacing(10)
        root.addWidget(self._density_host)
        return tab

    def _build_compliance_tab(self) -> QWidget:
        tab = QWidget(self)
        root = QVBoxLayout(tab)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QFrame(tab)
        header.setStyleSheet(_frame_style(highlight=True))
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(8)
        head_title = QLabel("标题合规雷达", header)
        head_title.setStyleSheet(_title_label_style())
        head_desc = QLabel("优先规避绝对化承诺、功效夸大、价格误导和易引发投诉的人群标签。", header)
        head_desc.setStyleSheet(_muted_label_style())
        _set_word_wrap(head_desc)
        header_layout.addWidget(head_title)
        header_layout.addWidget(head_desc)
        root.addWidget(header)

        self._compliance_host = QWidget(tab)
        self._compliance_layout = QVBoxLayout(self._compliance_host)
        compliance_layout = self._compliance_layout
        if compliance_layout is not None:
            compliance_layout.setContentsMargins(0, 0, 0, 0)
            compliance_layout.setSpacing(10)
        root.addWidget(self._compliance_host)
        return tab

    def _build_ab_test_section(self) -> QWidget:
        section = ContentSection("A/B 方案对比", icon="⇄", parent=self)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        header_row.addWidget(StatusBadge("当前优选方案 A", tone="brand", parent=section))
        header_row.addWidget(StatusBadge("建议同时测试 D", tone="info", parent=section))
        header_row.addStretch(1)
        header_row.addWidget(SecondaryButton("创建新方案", section, icon_text="＋"))
        section.content_layout.addLayout(header_row)

        self._ab_host = QWidget(section)
        self._ab_layout = QVBoxLayout(self._ab_host)
        ab_layout = self._ab_layout
        if ab_layout is not None:
            ab_layout.setContentsMargins(0, 0, 0, 0)
            ab_layout.setSpacing(10)
        section.content_layout.addWidget(self._ab_host)
        return section

    def _build_history_section(self) -> QWidget:
        section = ContentSection("标题历史", icon="◉", parent=self)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)

        history_search = SearchBar("搜索历史标题、模板或备注...", None)
        _connect(history_search.search_changed, self._on_history_search_changed)
        controls.addWidget(history_search, 2)

        self._history_count_label = QLabel("共 8 条标题记录", section)
        history_count_label = self._history_count_label
        if history_count_label is not None:
            history_count_label.setStyleSheet(_section_hint_style())
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

    def _build_footer_actions(self) -> QWidget:
        footer = QWidget(self)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        footer_tip = QLabel("建议先用模板定结构，再让 AI 生成 6 条标题，最后用 A/B 面板筛选最佳点击方案。", footer)
        footer_tip.setStyleSheet(_muted_label_style())
        _set_word_wrap(footer_tip)

        fab = FloatingActionButton("✚", "新建标题实验", footer)

        layout.addWidget(footer_tip, 1)
        layout.addStretch(1)
        layout.addWidget(fab)
        return footer

    def _build_metric_tile(self, title: str, value: str, note: str, key: str) -> QWidget:
        frame = QFrame(self)
        frame.setStyleSheet(_frame_style())
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        title_label = QLabel(title, frame)
        title_label.setStyleSheet(_muted_label_style())
        value_label = QLabel(value, frame)
        value_label.setStyleSheet(f"color: palette(text); background: transparent; font-size: 18px; font-weight: 800;")
        note_label = QLabel(note, frame)
        note_label.setStyleSheet(_muted_label_style())
        _set_word_wrap(note_label)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(note_label)

        if key == "char_count":
            self._char_count_value = value_label
        elif key == "length_score":
            self._length_score_value = value_label
        elif key == "emotion_score":
            self._emotion_score_value = value_label
        elif key == "keyword_score":
            self._keyword_score_value = value_label
        return frame

    def _build_keyword_action_button(self, keyword: str) -> QPushButton:
        button = QPushButton(keyword, self)
        _call(button, "setStyleSheet", f"""
            QPushButton {{
                background: {ACCENT_SOFT};
                color: {ACCENT};
                border: 1px solid {ACCENT_STRONG};
                border-radius: 16px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: rgba(0, 242, 234, 0.16);
            }}
        """)
        _connect(button.clicked, lambda word=keyword: self._append_keyword(word))
        return button

    def _build_length_row(self, benchmark: LengthBenchmark, parent: QWidget) -> QWidget:
        row = QFrame(parent)
        row.setStyleSheet(_frame_style())
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        badge = StatusBadge(benchmark.label, tone=_tone_badge(benchmark.tone), parent=row)
        range_label = QLabel(benchmark.range_text, row)
        range_label.setStyleSheet("color: palette(text); background: transparent; font-size: 14px; font-weight: 700;")
        insight_label = QLabel(benchmark.insight, row)
        insight_label.setStyleSheet(_muted_label_style())
        _set_word_wrap(insight_label)

        layout.addWidget(badge)
        layout.addWidget(range_label)
        layout.addWidget(insight_label, 1)
        return row

    def _build_category_block(self, category: str, templates: Sequence[TitleTemplate]) -> QWidget:
        block = QWidget(self)
        root = QVBoxLayout(block)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)
        heading = QLabel(category, block)
        heading.setStyleSheet(_title_label_style())
        count = QLabel(f"{len(templates)} 个模板", block)
        count.setStyleSheet(_section_hint_style())
        title_row.addWidget(heading)
        title_row.addWidget(count)
        title_row.addStretch(1)
        root.addLayout(title_row)

        for template in templates:
            root.addWidget(self._build_template_card(template, block))
        return block

    def _build_template_card(self, template: TitleTemplate, parent: QWidget) -> QWidget:
        frame = QFrame(parent)
        frame.setStyleSheet(_frame_style(highlight=template.name == self._selected_template_name))
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        name_label = QLabel(template.name, frame)
        name_label.setStyleSheet(_title_label_style())
        top.addWidget(name_label)
        top.addWidget(StatusBadge(template.success_rate, tone="brand", parent=frame))
        top.addStretch(1)
        top.addWidget(StatusBadge(template.scene, tone="info", parent=frame))
        layout.addLayout(top)

        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(10)
        meta_row.addWidget(StatsBadge("使用量", template.usage_count, "◎", "brand", frame))
        meta_row.addWidget(StatsBadge("特征", template.trait, "▲", "success", frame))
        meta_row.addWidget(StatsBadge("钩子", template.category, "◈", "info", frame))
        meta_row.addStretch(1)
        layout.addLayout(meta_row)

        hook_label = QLabel(template.hook, frame)
        hook_label.setStyleSheet(_muted_label_style())
        _set_word_wrap(hook_label)
        layout.addWidget(hook_label)

        example_frame = QFrame(frame)
        example_frame.setStyleSheet(_frame_style(dashed=True))
        example_layout = QVBoxLayout(example_frame)
        example_layout.setContentsMargins(12, 10, 12, 10)
        example_layout.setSpacing(6)
        example_title = QLabel("示例标题", example_frame)
        example_title.setStyleSheet(_section_hint_style())
        example_text = QLabel(template.example_title, example_frame)
        example_text.setStyleSheet("color: palette(text); background: transparent; font-size: 15px; font-weight: 700;")
        _set_word_wrap(example_text)
        example_hint = QLabel(f"AI 提示：{template.prompt_hint}", example_frame)
        example_hint.setStyleSheet(_muted_label_style())
        _set_word_wrap(example_hint)
        example_layout.addWidget(example_title)
        example_layout.addWidget(example_text)
        example_layout.addWidget(example_hint)
        layout.addWidget(example_frame)

        keyword_row = QWidget(frame)
        keyword_layout = QHBoxLayout(keyword_row)
        keyword_layout.setContentsMargins(0, 0, 0, 0)
        keyword_layout.setSpacing(6)
        for keyword in template.keywords:
            keyword_layout.addWidget(TagChip(keyword, tone="neutral", parent=keyword_row))
        keyword_layout.addStretch(1)
        layout.addWidget(keyword_row)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        apply_button = PrimaryButton("套用模板", frame, icon_text="✦")
        _connect(apply_button.clicked, lambda item=template: self._apply_template(item))
        insert_button = SecondaryButton("带入示例", frame, icon_text="↳")
        _connect(insert_button.clicked, lambda item=template: self._set_title_text(item.example_title))
        action_row.addWidget(apply_button)
        action_row.addWidget(insert_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)
        return frame

    def _build_suggestion_card(self, suggestion: OptimizationSuggestion, parent: QWidget) -> QWidget:
        frame = QFrame(parent)
        frame.setStyleSheet(_frame_style(highlight=suggestion.priority == "高优先"))
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        title = QLabel(suggestion.title, frame)
        title.setStyleSheet(_title_label_style())
        top.addWidget(title)
        top.addWidget(StatusBadge(suggestion.priority, tone=_tone_badge(suggestion.tone), parent=frame))
        top.addStretch(1)
        top.addWidget(StatusBadge(suggestion.expected_uplift, tone="success", parent=frame))
        layout.addLayout(top)

        summary = QLabel(suggestion.summary, frame)
        summary.setStyleSheet(_muted_label_style())
        _set_word_wrap(summary)
        layout.addWidget(summary)
        return frame

    def _build_density_row(self, metric: DensityMetric, parent: QWidget) -> QWidget:
        frame = QFrame(parent)
        frame.setStyleSheet(_frame_style())
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        key_label = QLabel(metric.keyword, frame)
        key_label.setStyleSheet(_title_label_style())
        density_label = QLabel(f"{metric.density}%", frame)
        density_label.setStyleSheet(f"color: {ACCENT}; background: transparent; font-size: 15px; font-weight: 800;")
        top.addWidget(key_label)
        top.addStretch(1)
        top.addWidget(StatusBadge(f"目标 {metric.target}", tone=_tone_badge(metric.tone), parent=frame))
        top.addWidget(density_label)
        layout.addLayout(top)

        bar_track = QFrame(frame)
        _call(bar_track, "setFixedHeight", 10)
        _call(bar_track, "setStyleSheet", "QFrame { background: palette(midlight); border: none; border-radius: 5px; }")
        fill = QFrame(bar_track)
        _call(fill, "setStyleSheet", f"QFrame {{ background: {ACCENT}; border: none; border-radius: 5px; }}")
        _call(fill, "setFixedHeight", 10)
        _call(fill, "setFixedWidth", max(36, metric.density * 5))
        bar_layout = QVBoxLayout(bar_track)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)
        bar_layout.addWidget(fill)
        layout.addWidget(bar_track)

        insight = QLabel(metric.insight, frame)
        insight.setStyleSheet(_muted_label_style())
        _set_word_wrap(insight)
        layout.addWidget(insight)
        return frame

    def _build_compliance_row(self, item: ComplianceItem, parent: QWidget) -> QWidget:
        frame = QFrame(parent)
        frame.setStyleSheet(_frame_style())
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        layout.addWidget(StatusBadge(item.result, tone=_tone_badge(item.tone), parent=frame))

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(4)
        title = QLabel(item.name, frame)
        title.setStyleSheet(_title_label_style())
        detail = QLabel(item.detail, frame)
        detail.setStyleSheet(_muted_label_style())
        _set_word_wrap(detail)
        text_col.addWidget(title)
        text_col.addWidget(detail)

        layout.addLayout(text_col, 1)
        return frame

    def _build_variant_card(self, variant: ABVariant, parent: QWidget) -> QWidget:
        frame = QFrame(parent)
        frame.setStyleSheet(_frame_style(highlight=variant.label == "A"))
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)

        label_badge = StatusBadge(f"方案 {variant.label}", tone=_tone_badge(variant.tone), parent=frame)
        top.addWidget(label_badge)
        top.addStretch(1)
        top.addWidget(StatusBadge(f"预期 CTR {variant.expected_ctr}", tone="brand", parent=frame))
        top.addWidget(StatusBadge(variant.delta, tone="success" if variant.label == "A" else "warning", parent=frame))
        layout.addLayout(top)

        title = QLabel(variant.title, frame)
        title.setStyleSheet("color: palette(text); background: transparent; font-size: 15px; font-weight: 800;")
        _set_word_wrap(title)
        layout.addWidget(title)

        audience = QLabel(f"适配人群：{variant.audience}", frame)
        audience.setStyleSheet(_muted_label_style())
        _set_word_wrap(audience)
        layout.addWidget(audience)

        reason_frame = QFrame(frame)
        reason_frame.setStyleSheet(_frame_style(dashed=True))
        reason_layout = QVBoxLayout(reason_frame)
        reason_layout.setContentsMargins(12, 10, 12, 10)
        reason_layout.setSpacing(4)
        reason_label = QLabel("表现判断", reason_frame)
        reason_label.setStyleSheet(_section_hint_style())
        reason_value = QLabel(variant.winning_reason, reason_frame)
        reason_value.setStyleSheet(_muted_label_style())
        _set_word_wrap(reason_value)
        reason_layout.addWidget(reason_label)
        reason_layout.addWidget(reason_value)
        layout.addWidget(reason_frame)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        use_button = SecondaryButton("设为当前标题", frame, icon_text="↳")
        _connect(use_button.clicked, lambda item=variant: self._set_title_text(item.title))
        actions.addWidget(use_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        return frame

    def _build_history_row(self, item: HistoryItem, parent: QWidget) -> QWidget:
        frame = QFrame(parent)
        frame.setStyleSheet(_frame_style())
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        time_label = QLabel(item.created_at, frame)
        time_label.setStyleSheet(_section_hint_style())
        top.addWidget(time_label)
        top.addWidget(StatusBadge(item.status, tone=_tone_badge(item.tone), parent=frame))
        top.addWidget(StatusBadge(f"CTR {item.ctr}", tone="brand", parent=frame))
        top.addStretch(1)
        top.addWidget(StatusBadge(item.template_name, tone="info", parent=frame))
        layout.addLayout(top)

        title = QLabel(item.title, frame)
        title.setStyleSheet("color: palette(text); background: transparent; font-size: 15px; font-weight: 700;")
        _set_word_wrap(title)
        note = QLabel(item.note, frame)
        note.setStyleSheet(_muted_label_style())
        _set_word_wrap(note)
        layout.addWidget(title)
        layout.addWidget(note)
        return frame

    def _seed_default_values(self) -> None:
        if self._title_input is not None:
            self._title_input.setText(DEFAULT_TITLE)
        if self._brief_input is not None:
            self._brief_input.setPlainText(DEFAULT_BRIEF)
        if self._keyword_input is not None:
            self._keyword_input.set_tags(["建议收藏", "租房党", "10 分钟", "全屋清洁", "闭眼冲"])
        if self._prompt_editor is not None:
            self._prompt_editor.set_text(DEFAULT_PROMPT)
        if self._config_panel is not None:
            self._config_panel.set_config(
                {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "agent_role": "文案专家",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "top_p": 0.9,
                }
            )

    def _bind_events(self) -> None:
        if self._title_input is not None:
            _connect(getattr(self._title_input.line_edit, "textChanged", None), lambda _text: self._on_title_related_changed())
        if self._brief_input is not None:
            _connect(getattr(self._brief_input.text_edit, "textChanged", None), self._update_title_metrics)
        if self._keyword_input is not None:
            _connect(self._keyword_input.tags_changed, lambda _tags: self._on_title_related_changed())
        if self._config_panel is not None:
            _connect(self._config_panel.config_changed, lambda _config: self._update_model_summary())

    def _on_title_related_changed(self) -> None:
        self._update_title_metrics()
        self._render_keyword_density()
        self._render_suggestions()

    def _on_template_search_changed(self, keyword: str) -> None:
        self._template_keyword = keyword.strip()
        self._render_template_gallery()

    def _on_scene_filter_changed(self, value: str) -> None:
        self._active_scene_filter = value.strip() or "全部"
        self._render_template_gallery()

    def _on_history_search_changed(self, keyword: str) -> None:
        self._history_keyword = keyword.strip()
        self._render_history_rows()

    def _append_keyword(self, keyword: str) -> None:
        if self._keyword_input is None:
            return
        self._keyword_input.add_tag(keyword)
        self._update_title_metrics()
        self._render_keyword_density()

    def _apply_template(self, template: TitleTemplate) -> None:
        self._selected_template_name = template.name
        self._set_title_text(template.example_title)
        if self._template_hint_label is not None:
            self._template_hint_label.setText(f"当前模板：{template.name}")
        if self._prompt_editor is not None:
            existing = self._prompt_editor.text().strip()
            template_line = f"\n补充要求：优先采用“{template.name}”结构，突出 {template.scene} 场景，并保留关键词 {', '.join(template.keywords[:3])}。"
            self._prompt_editor.set_text(f"{existing}{template_line}" if template_line not in existing else existing)
        if self._keyword_input is not None:
            for keyword in template.keywords:
                self._keyword_input.add_tag(keyword, emit_signal=False)
            self._keyword_input.tags_changed.emit(self._keyword_input.tags())
        self._render_template_gallery()
        self._render_generated_output(initial=False)

    def _set_title_text(self, text: str) -> None:
        if self._title_input is not None:
            self._title_input.setText(text)

    def _current_title(self) -> str:
        if self._title_input is None:
            return ""
        return self._title_input.text().strip()

    def _current_keywords(self) -> list[str]:
        if self._keyword_input is None:
            return []
        return self._keyword_input.tags()

    def _filtered_templates(self) -> list[TitleTemplate]:
        keyword = self._template_keyword.lower()
        results: list[TitleTemplate] = []
        for template in self._templates:
            if self._active_scene_filter != "全部" and template.scene != self._active_scene_filter:
                continue
            haystack = " ".join(
                [
                    template.category,
                    template.name,
                    template.scene,
                    template.trait,
                    template.hook,
                    template.example_title,
                    template.prompt_hint,
                    *template.keywords,
                ]
            ).lower()
            if keyword and keyword not in haystack:
                continue
            results.append(template)
        return results

    def _render_template_gallery(self) -> None:
        if self._template_gallery_layout is None:
            return
        _clear_layout(self._template_gallery_layout)

        filtered = self._filtered_templates()
        grouped: dict[str, list[TitleTemplate]] = {}
        for template in filtered:
            grouped.setdefault(template.category, []).append(template)

        for category in ("悬念钩子", "利益直给", "认知偏差", "场景共鸣", "数据证明"):
            items = grouped.get(category, [])
            if items:
                self._template_gallery_layout.addWidget(self._build_category_block(category, items))

        if not filtered:
            empty = QFrame(self)
            empty.setStyleSheet(_frame_style(dashed=True))
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(18, 18, 18, 18)
            empty_layout.setSpacing(6)
            empty_title = QLabel("没有找到匹配模板", empty)
            empty_title.setStyleSheet(_title_label_style())
            empty_desc = QLabel("试试更短的关键词，或切换到“全部”场景重新查看。", empty)
            empty_desc.setStyleSheet(_muted_label_style())
            _set_word_wrap(empty_desc)
            empty_layout.addWidget(empty_title)
            empty_layout.addWidget(empty_desc)
            self._template_gallery_layout.addWidget(empty)

        if self._template_count_label is not None:
            self._template_count_label.setText(f"已匹配 {len(filtered)} 个模板")

    def _build_dynamic_density_metrics(self) -> list[DensityMetric]:
        title = self._current_title()
        keywords = self._current_keywords()
        base_words = keywords[:5] if keywords else ["建议收藏", "人群标签", "场景词"]
        metrics: list[DensityMetric] = []
        for index, word in enumerate(base_words):
            hits = title.count(word)
            density = min(38, max(8, len(word) * 2 + hits * 11 + index * 3))
            metrics.append(
                DensityMetric(
                    keyword=word,
                    density=density,
                    target="12%-30%" if index < 2 else "8%-20%",
                    insight=(
                        "标题中已直接命中该词，建议保留并与场景词组合。"
                        if hits
                        else "当前标题未直接出现该词，可考虑替换弱表达提升推荐匹配度。"
                    ),
                    tone="brand" if hits else ("warning" if index == 0 else "info"),
                )
            )
        return metrics or list(DEFAULT_DENSITY_METRICS)

    def _render_keyword_density(self) -> None:
        if self._density_layout is None:
            return
        _clear_layout(self._density_layout)
        self._density_metrics = self._build_dynamic_density_metrics()
        for metric in self._density_metrics:
            self._density_layout.addWidget(self._build_density_row(metric, self))

    def _build_dynamic_suggestions(self) -> list[OptimizationSuggestion]:
        title = self._current_title()
        suggestions = list(OPTIMIZATION_SUGGESTIONS[:4])
        if len(title) < 18:
            suggestions.insert(
                0,
                OptimizationSuggestion(
                    "标题略短，补一个结果词",
                    "当前标题字数偏短，建议补充“省一半 / 少踩坑 / 更稳”这类结果表达，增强获得感。",
                    "预估 CTR +0.5%",
                    "高优先",
                    "warning",
                ),
            )
        elif len(title) > 32:
            suggestions.insert(
                0,
                OptimizationSuggestion(
                    "标题略长，建议减法",
                    "当前标题超过舒适区，建议删除一个修饰短语，把利益点前移。",
                    "预估 可读性 +18%",
                    "高优先",
                    "error",
                ),
            )
        if "建议收藏" not in title:
            suggestions.append(
                OptimizationSuggestion(
                    "可增加收藏钩子",
                    "如果内容偏知识或避坑，尾部加入“建议收藏”会明显提高二次分发和收藏率。",
                    "预估 收藏率 +10%",
                    "中优先",
                    "brand",
                )
            )
        return suggestions[:6]

    def _render_suggestions(self) -> None:
        if self._suggestion_layout is None:
            return
        _clear_layout(self._suggestion_layout)
        for suggestion in self._build_dynamic_suggestions():
            self._suggestion_layout.addWidget(self._build_suggestion_card(suggestion, self))

    def _render_compliance_checks(self) -> None:
        if self._compliance_layout is None:
            return
        _clear_layout(self._compliance_layout)
        for item in COMPLIANCE_ITEMS:
            self._compliance_layout.addWidget(self._build_compliance_row(item, self))

    def _render_ab_variants(self) -> None:
        if self._ab_layout is None:
            return
        _clear_layout(self._ab_layout)
        for variant in AB_VARIANTS:
            self._ab_layout.addWidget(self._build_variant_card(variant, self))

    def _filtered_history_items(self) -> list[HistoryItem]:
        keyword = self._history_keyword.lower()
        if not keyword:
            return list(self._history_items)
        filtered: list[HistoryItem] = []
        for item in self._history_items:
            haystack = f"{item.created_at} {item.title} {item.template_name} {item.status} {item.note}".lower()
            if keyword in haystack:
                filtered.append(item)
        return filtered

    def _render_history_rows(self) -> None:
        if self._history_layout is None:
            return
        _clear_layout(self._history_layout)
        filtered = self._filtered_history_items()
        for item in filtered:
            self._history_layout.addWidget(self._build_history_row(item, self))
        if self._history_count_label is not None:
            self._history_count_label.setText(f"共 {len(filtered)} 条标题记录")

    def _update_title_metrics(self) -> None:
        title = self._current_title()
        length = len(title)
        keyword_hits = 0
        for keyword in self._current_keywords():
            if keyword and keyword in title:
                keyword_hits += 1

        if self._char_count_value is not None:
            self._char_count_value.setText(f"{length} / 64")
        if self._length_score_value is not None:
            if 18 <= length <= 28:
                self._length_score_value.setText("优")
            elif 14 <= length <= 32:
                self._length_score_value.setText("良")
            else:
                self._length_score_value.setText("需优化")
        if self._emotion_score_value is not None:
            emotion_tokens = ("别再", "真的", "原来", "闭眼冲", "后悔", "一定要")
            emotion_score = sum(1 for token in emotion_tokens if token in title)
            self._emotion_score_value.setText("高" if emotion_score >= 2 else ("中" if emotion_score == 1 else "基础"))
        if self._keyword_score_value is not None:
            self._keyword_score_value.setText("强" if keyword_hits >= 2 else ("中" if keyword_hits == 1 else "弱"))

    def _update_model_summary(self) -> None:
        if self._config_panel is None or self._model_summary_label is None:
            return
        config = self._config_panel.config()
        summary = (
            f"{config['provider_label']} · {config['model']} · {config['agent_role']} · "
            f"温度 {config['temperature']} · Top-p {config['top_p']} · 输出上限 {config['max_tokens']} Token"
        )
        self._model_summary_label.setText(summary)

    def _render_generated_output(self, *, initial: bool) -> None:
        if self._streaming_output is None:
            return

        title = self._current_title() or DEFAULT_TITLE
        keywords = "、".join(self._current_keywords()[:5]) or "建议收藏、租房党、10 分钟"
        mode_prefix = "初始化预览" if initial else "基于当前输入生成"
        generated = [
            f"{mode_prefix}：",
            "",
            f"1. {title}",
            "   适用模板：利益直给型",
            f"   关键词建议：{keywords}",
            "   推荐场景：短视频前 3 秒直接亮结果，适合转化投流。",
            "",
            "2. 别再盲买清洁工具了，这台机器才是租房党的省时答案",
            "   适用模板：认知偏差型",
            "   关键词建议：别盲买、租房党、省时、全屋清洁",
            "   推荐场景：测评类内容、避坑类口播、评论区互动引导。",
            "",
            "3. 我后悔没早点入：下班回家 10 分钟，厨房和客厅终于一起干净了",
            "   适用模板：场景共鸣型",
            "   关键词建议：后悔没早点入、下班回家、10 分钟",
            "   推荐场景：生活方式内容、晚间居家收纳场景。",
            "",
            "4. 同样做家务半小时，为什么用了它之后我还能多刷一集剧？",
            "   适用模板：悬念钩子型",
            "   关键词建议：为什么、半小时、多刷一集剧",
            "   推荐场景：对比实测、前后变化、剧情式口播。",
        ]
        self._streaming_output.clear()
        self._streaming_output.set_loading(True)
        self._streaming_output.append_chunk("\n".join(generated))
        self._streaming_output.set_token_usage(864, 612)
        self._streaming_output.set_loading(False)

    def _on_generate_clicked(self) -> None:
        self._render_generated_output(initial=False)

    def _on_regenerate_clicked(self) -> None:
        self._render_generated_output(initial=False)
        if self._streaming_output is not None:
            self._streaming_output.append_chunk(
                "\n\n加生成 2 条补充方案：\n5. 建议收藏：租房党如果只留一台清洁机，我会把这台放在第一位\n6. 原来差别这么大，同样是周末打扫，这台真的把累感降下来了"
            )
            self._streaming_output.set_token_usage(972, 740)

    def _apply_best_variant(self) -> None:
        self._set_title_text(AB_VARIANTS[0].title)
        self._update_title_metrics()
        self._render_generated_output(initial=False)

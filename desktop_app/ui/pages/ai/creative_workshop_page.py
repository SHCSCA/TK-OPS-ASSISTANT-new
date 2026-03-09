# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false, reportPrivateUsage=false

from __future__ import annotations

"""创意工坊页面。"""

from dataclasses import dataclass
from typing import Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    ContentSection,
    DataTable,
    FilterDropdown,
    InfoCard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatsBadge,
    StatusBadge,
    StreamingOutputWidget,
    TagChip,
    TaskProgressBar,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ThemedTextEdit,
    ToggleSwitch,
)
from ...components.tags import BadgeTone
from ...components.inputs import _connect
from ..base_page import BasePage

ACCENT = "#00F2EA"
ACCENT_SOFT = "rgba(0, 242, 234, 0.10)"
ACCENT_STRONG = "rgba(0, 242, 234, 0.20)"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"
INFO = "#38BDF8"
TEXT_STRONG = "#0F172A"
TEXT_MUTED = "#64748B"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F8FAFC"
SURFACE_SOFT = "#F1F5F9"
BORDER = "#E2E8F0"


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用可能不存在的方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _set_word_wrap(label: QLabel, enabled: bool = True) -> None:
    """安全设置文本换行。"""

    _call(label, "setWordWrap", enabled)


def _set_style(widget: object, style: str) -> None:
    """安全设置局部样式。"""

    _call(widget, "setStyleSheet", style)


def _score_tone(score: int) -> BadgeTone:
    """根据质量分数返回色调。"""

    if score >= 90:
        return "success"
    if score >= 80:
        return "brand"
    if score >= 70:
        return "warning"
    return "error"


def _score_color(score: int) -> str:
    """根据质量分数返回主色。"""

    if score >= 90:
        return SUCCESS
    if score >= 80:
        return ACCENT
    if score >= 70:
        return WARNING
    return ERROR


@dataclass(frozen=True)
class BatchTemplate:
    """批量创作模板数据。"""

    category: str
    name: str
    target_scene: str
    target_audience: str
    best_use: str
    output_mode: str
    expected_time: str
    summary: str
    highlights: tuple[str, ...]


@dataclass(frozen=True)
class BatchPreset:
    """批量执行预设。"""

    name: str
    count: str
    variations: str
    length: str
    quality_gate: str
    note: str


@dataclass(frozen=True)
class QueueTask:
    """批次队列任务。"""

    keyword: str
    state: str
    progress: str
    eta: str
    model: str
    note: str
    tone: BadgeTone


@dataclass(frozen=True)
class GenerationResult:
    """单条生成结果。"""

    keyword: str
    title: str
    model: str
    template_name: str
    tone_label: str
    length_label: str
    quality_score: int
    click_forecast: str
    conversion_forecast: str
    uniqueness: str
    created_at: str
    status: str
    hook_summary: str
    content: str
    style_tags: tuple[str, ...]
    quality_dimensions: tuple[tuple[str, int], ...]
    insight_tags: tuple[str, ...]


@dataclass(frozen=True)
class ComparisonRecord:
    """模型对比数据。"""

    variant: str
    model: str
    average_score: str
    hook_power: str
    business_value: str
    click_estimate: str
    cost_efficiency: str
    recommendation: str


@dataclass(frozen=True)
class ArchiveRecord:
    """历史批次记录。"""

    batch_id: str
    batch_name: str
    created_at: str
    generated_count: str
    average_score: str
    winning_model: str
    status: str
    note: str


@dataclass(frozen=True)
class InsightMetric:
    """顶部指标数据。"""

    label: str
    value: str
    detail: str
    icon: str
    tone: BadgeTone


BATCH_TEMPLATES: tuple[BatchTemplate, ...] = (
    BatchTemplate(
        category="商品卖点批量版",
        name="高客单爆款详情口播",
        target_scene="新品上架、达人分发、新品预热",
        target_audience="25-40 岁追求品质与效率的消费人群",
        best_use="适合 299 元以上高客单单品，强调信任感与价值感。",
        output_mode="短口播 + 长图文双版本",
        expected_time="约 6 分钟完成 24 条",
        summary="突出性能证据、适用人群与购买理由，适合做批量素材底稿。",
        highlights=("高转化结构", "价格锚点清晰", "适合卖点拆解", "支持差异化变体"),
    ),
    BatchTemplate(
        category="商品卖点批量版",
        name="功能卖点拆解矩阵",
        target_scene="短视频矩阵号、评论区补充、详情页补文案",
        target_audience="明确需求型消费者与目标词搜索流量",
        best_use="围绕单一功能点快速生成多角度表达，适合量产。",
        output_mode="标题 + 主文案 + CTA",
        expected_time="约 4 分钟完成 32 条",
        summary="从性能、场景、痛点、对比四个维度拆解同一产品。",
        highlights=("便于 A/B 测试", "同品多表达", "结构统一", "利于批量导出"),
    ),
    BatchTemplate(
        category="场景种草版",
        name="生活方式情绪种草",
        target_scene="居家、美妆、穿搭、母婴、收纳",
        target_audience="注重情绪价值与生活方式表达的女性用户",
        best_use="用于打造有代入感的开场和转化钩子。",
        output_mode="场景开头 + 卖点延展",
        expected_time="约 5 分钟完成 18 条",
        summary="以生活场景切入，通过感受驱动用户停留和收藏。",
        highlights=("情绪价值强", "适合收藏", "画面感突出", "适合春夏内容"),
    ),
    BatchTemplate(
        category="场景种草版",
        name="痛点逆转解决方案",
        target_scene="家清、厨房、电器、办公、个护",
        target_audience="有明确痛点且希望快速解决问题的用户",
        best_use="将产品与高频痛点直接绑定，适合转化型素材。",
        output_mode="问题式开头 + 解决式结尾",
        expected_time="约 4 分钟完成 20 条",
        summary="通过“原来一直错了”的认知落差引出商品价值。",
        highlights=("强需求识别", "前 3 秒抓人", "成交意图强", "适合短视频挂车"),
    ),
    BatchTemplate(
        category="达人联动版",
        name="达人试用推荐稿",
        target_scene="达人合作、站外投放、混剪二创",
        target_audience="相信真实体验与口碑背书的种草用户",
        best_use="适合有样品反馈或用户评价沉淀的商品。",
        output_mode="第一人称体验文案",
        expected_time="约 7 分钟完成 16 条",
        summary="强调体验变化、真实反馈和购买前后对比。",
        highlights=("代入感高", "评论氛围好", "适合口播", "可混剪复用"),
    ),
    BatchTemplate(
        category="达人联动版",
        name="短视频催单补量版",
        target_scene="短视频中控、福袋节点、转化低谷补压",
        target_audience="短视频犹豫用户、价格敏感型用户",
        best_use="适合短视频节奏推进和限时权益传达。",
        output_mode="促单短句 + 权益说明",
        expected_time="约 3 分钟完成 40 条",
        summary="突出限时、库存、福利与错过成本，适合高频播报。",
        highlights=("节奏快", "可插播", "促单强", "适合秒杀节点"),
    ),
)


BATCH_PRESETS: tuple[BatchPreset, ...] = (
    BatchPreset(
        name="短视频冲量",
        count="24 条",
        variations="每个关键词 3 版",
        length="120-180 字",
        quality_gate="80 分自动保留",
        note="适合短视频发布前 30 分钟快速铺量。",
    ),
    BatchPreset(
        name="短视频矩阵",
        count="36 条",
        variations="每个关键词 4 版",
        length="180-260 字",
        quality_gate="85 分自动保留",
        note="适合账号矩阵并行发稿。",
    ),
    BatchPreset(
        name="高客单精修",
        count="12 条",
        variations="每个关键词 2 版",
        length="260-380 字",
        quality_gate="90 分自动保留",
        note="适合高客单单品和高转化落地页。",
    ),
    BatchPreset(
        name="上新测试",
        count="18 条",
        variations="每个关键词 3 版",
        length="150-220 字",
        quality_gate="78 分自动保留",
        note="适合新品首轮探索和低成本试错。",
    ),
)


QUEUE_TASKS: tuple[QueueTask, ...] = (
    QueueTask(
        keyword="智能运动手表",
        state="已完成",
        progress="4/4 版本已生成",
        eta="已归档",
        model="gpt-4o",
        note="质量分高于同批均值 6 分，已进入优先导出池。",
        tone="success",
    ),
    QueueTask(
        keyword="降噪耳机",
        state="生成中",
        progress="2/4 版本已生成",
        eta="预计 42 秒",
        model="claude-3-7-sonnet",
        note="当前正在补充对比型卖点与通勤场景版本。",
        tone="brand",
    ),
    QueueTask(
        keyword="人体工学办公椅",
        state="排队中",
        progress="等待模型槽位",
        eta="预计 1 分 18 秒",
        model="gpt-4.1-mini",
        note="将优先生成老板办公室与久坐办公两类版本。",
        tone="warning",
    ),
    QueueTask(
        keyword="便携咖啡机",
        state="评分中",
        progress="去重与质检进行中",
        eta="预计 26 秒",
        model="glm-4.5-air",
        note="已触发重复表达压缩与夸大表述过滤。",
        tone="info",
    ),
    QueueTask(
        keyword="桌面补光灯",
        state="待补写",
        progress="1 条低分待重生成",
        eta="等待人工确认",
        model="deepseek-chat",
        note="原稿过于平铺，建议补强使用场景和结果承诺。",
        tone="error",
    ),
)


INSIGHT_METRICS: tuple[InsightMetric, ...] = (
    InsightMetric("今日批次", "07 个", "含 3 个短视频冲量批次", "批", "brand"),
    InsightMetric("平均质量分", "86.7", "较昨日提升 4.2 分", "质", "success"),
    InsightMetric("高潜结果", "18 条", "点击预估高于 3.8%", "优", "info"),
    InsightMetric("待人工复核", "03 条", "主要集中在夸张表述", "审", "warning"),
)


GENERATION_RESULTS: tuple[GenerationResult, ...] = (
    GenerationResult(
        keyword="智能运动手表",
        title="极限运动也不怕掉链子，这块表把专业感直接戴在手上",
        model="gpt-4o",
        template_name="高客单爆款详情口播",
        tone_label="专业权威",
        length_label="约 310 字",
        quality_score=94,
        click_forecast="4.9%",
        conversion_forecast="8.1%",
        uniqueness="91%",
        created_at="刚刚",
        status="可导出",
        hook_summary="用极限场景先建立可靠感，再把健康监测与材质价值拉满。",
        content="如果你在找一块不只好看、还真的能跟上高强度运动节奏的智能手表，这款会很容易让人一眼记住。它不是只会记步数的普通手表，而是把心率、血氧、睡眠、运动模式和全天候提醒整合进一套非常顺手的体验里。钛金属机身加蓝宝石镜面，日常通勤有质感，户外训练也不容易留下狼狈痕迹。最重要的是，数据反馈不是冷冰冰的数字，而是真的能帮你判断今天该冲还是该缓。对于既要效率、又要专业感的人来说，它不是装饰品，是会一直跟着你做决策的装备。",
        style_tags=("高客单", "科技感", "强信任", "适合卖点拆解"),
        quality_dimensions=(("开头抓力", 95), ("卖点完整", 92), ("转化推动", 94), ("平台适配", 93)),
        insight_tags=("适合高客单短视频", "可拆成 3 条口播", "价格锚点可继续强化"),
    ),
    GenerationResult(
        keyword="降噪耳机",
        title="通勤路上最值的升级，就是终于有人把嘈杂世界按了静音",
        model="claude-3-7-sonnet",
        template_name="生活方式情绪种草",
        tone_label="情绪种草",
        length_label="约 268 字",
        quality_score=90,
        click_forecast="4.4%",
        conversion_forecast="7.2%",
        uniqueness="88%",
        created_at="1 分钟前",
        status="待复选",
        hook_summary="先写通勤噪音痛点，再落到一键降噪和续航，情绪价值较强。",
        content="每天通勤最累的不是路远，而是耳边一直停不下来的杂音。地铁提示音、办公区聊天声、咖啡机的轰鸣，都会让人莫名更烦。这款降噪耳机最让我愿意反复拿出来讲的，不是它参数有多堆，而是戴上的那一秒，世界真的会安静下来。自适应降噪会根据环境变化调整强度，通勤时不压耳，办公时不闷。音乐一开，细节是干净的，人也更容易进入自己的节奏。再加上 40 小时续航和轻量佩戴，日常通勤、加班和短途旅行几乎都不用额外操心。",
        style_tags=("通勤", "情绪共鸣", "收藏向", "女性用户友好"),
        quality_dimensions=(("开头抓力", 92), ("卖点完整", 88), ("转化推动", 86), ("平台适配", 94)),
        insight_tags=("评论区易产生共鸣", "可补充游戏场景版", "适合做画面配文"),
    ),
    GenerationResult(
        keyword="人体工学办公椅",
        title="不是忍着坐满 8 小时，而是终于有人把久坐这件事重新设计了一遍",
        model="gpt-4.1-mini",
        template_name="痛点逆转解决方案",
        tone_label="解决痛点",
        length_label="约 332 字",
        quality_score=88,
        click_forecast="4.1%",
        conversion_forecast="6.9%",
        uniqueness="87%",
        created_at="2 分钟前",
        status="待人工润色",
        hook_summary="强调久坐痛点和体感改善，适合办公椅高意向流量。",
        content="很多人以为上班累是工作的问题，其实更多时候，是椅子一直在偷偷消耗你的状态。坐久了腰酸、肩紧、腿麻，不只是难受，还会直接影响效率。这款人体工学办公椅做得很聪明，头枕、腰托、扶手和坐深都能根据身形微调，不是让你去适应椅子，而是让椅子来适应你。最明显的变化，是下午四五点不会再有那种坐到发空的感觉。透气网布不闷，后仰支撑也稳，开会、剪片、写方案都更容易坐得住。对于每天至少要坐八小时的人来说，它不是可有可无的家具，而是能直接改善体感和专注度的工具。",
        style_tags=("办公场景", "高意向", "痛点明确", "适合老板号"),
        quality_dimensions=(("开头抓力", 86), ("卖点完整", 90), ("转化推动", 87), ("平台适配", 88)),
        insight_tags=("建议补一版老板办公室语气", "可加入久坐数据对比", "适合图文详情页"),
    ),
    GenerationResult(
        keyword="便携咖啡机",
        title="不是咖啡馆去不起，是现在随手一按就能把氛围感带出门",
        model="glm-4.5-air",
        template_name="达人试用推荐稿",
        tone_label="真实体验",
        length_label="约 226 字",
        quality_score=85,
        click_forecast="3.9%",
        conversion_forecast="6.4%",
        uniqueness="84%",
        created_at="4 分钟前",
        status="可复用",
        hook_summary="聚焦出行、露营、办公室三类轻场景，代入感明显。",
        content="以前总觉得喝一杯像样的咖啡，必须得靠咖啡馆或者一大堆设备，现在才发现，原来很多时候只差一个足够轻便又不麻烦的工具。这款便携咖啡机特别适合放在办公室、车里或者周末露营包里，体积不大，但出杯效率很顺。水加好、粉装好，一按就能有稳定的萃取感，不是那种只有噱头、喝起来却空空的便携设备。对爱喝咖啡的人来说，它最打动人的地方是，你不需要迁就场景，随时都能把自己的节奏带上。",
        style_tags=("露营", "办公桌面", "轻生活", "适合达人混剪"),
        quality_dimensions=(("开头抓力", 84), ("卖点完整", 83), ("转化推动", 85), ("平台适配", 88)),
        insight_tags=("适合露营内容号", "可补充清洗方便点", "建议搭配氛围镜头"),
    ),
    GenerationResult(
        keyword="桌面补光灯",
        title="镜头里气色突然变好的秘密，可能只是桌上多了一盏懂你的灯",
        model="deepseek-chat",
        template_name="功能卖点拆解矩阵",
        tone_label="场景种草",
        length_label="约 205 字",
        quality_score=79,
        click_forecast="3.3%",
        conversion_forecast="5.7%",
        uniqueness="80%",
        created_at="6 分钟前",
        status="待重生成",
        hook_summary="氛围感有，但硬卖点不足，需要补参数和使用收益。",
        content="很多人拍视频时总觉得自己的状态比现实差一点，问题往往不是妆没化好，而是光线没站在你这边。这盏桌面补光灯最讨喜的地方，是开了之后整个人会显得更干净、更有精神。它不像强打脸的白光那样把细节全暴露出来，而是能把肤色修得更柔和，桌面拍摄、短视频口播、远程会议都能明显感觉到画面更顺眼。如果你经常出镜，或者希望产品画面看起来更精致，它会是那种用了之后很难再撤掉的桌面设备。",
        style_tags=("出镜优化", "桌面设备", "口播友好", "需补参数"),
        quality_dimensions=(("开头抓力", 81), ("卖点完整", 73), ("转化推动", 78), ("平台适配", 84)),
        insight_tags=("建议补亮度档位", "需强调手机拍摄收益", "适合二次重写"),
    ),
    GenerationResult(
        keyword="家用净饮机",
        title="以前总嫌喝水麻烦，直到我把冷热净饮这件事缩短成了一次伸手",
        model="gpt-4o",
        template_name="高客单爆款详情口播",
        tone_label="品质生活",
        length_label="约 346 字",
        quality_score=92,
        click_forecast="4.7%",
        conversion_forecast="7.8%",
        uniqueness="89%",
        created_at="9 分钟前",
        status="可导出",
        hook_summary="从喝水频次切入，强化省心体验和全家适配价值。",
        content="真正会被长期使用的小家电，不是看起来高级，而是能把原本麻烦的动作直接变顺手。这台家用净饮机让我最满意的地方，就是把净化、即热、冷饮和定量出水整合成了一个很轻松的动作。早上冲咖啡、中午泡茶、晚上接温水，不需要等，也不用反复烧。对于有老人和孩子的家庭来说，温度控制和水质稳定感特别重要，因为它省下来的不只是时间，还有很多本来会被忽略的琐碎成本。再加上机器本身颜值干净、台面占用不夸张，很适合现在越来越讲究效率和整洁感的厨房场景。",
        style_tags=("高客单", "家庭场景", "厨房升级", "适合图文详情页"),
        quality_dimensions=(("开头抓力", 90), ("卖点完整", 94), ("转化推动", 91), ("平台适配", 92)),
        insight_tags=("适合全家需求场景", "可延展母婴温水版", "导购逻辑清晰"),
    ),
)


COMPARISON_RECORDS: tuple[ComparisonRecord, ...] = (
    ComparisonRecord("版本 A", "gpt-4o", "92.8", "强", "高", "4.8%", "中", "适合直接投放短视频口播主版本"),
    ComparisonRecord("版本 B", "claude-3-7-sonnet", "89.6", "中上", "高", "4.4%", "中", "适合做长文案详情页与品牌感表达"),
    ComparisonRecord("版本 C", "gpt-4.1-mini", "86.9", "中", "中上", "4.0%", "高", "适合批量铺量与低成本测试"),
    ComparisonRecord("版本 D", "glm-4.5-air", "84.7", "中", "中", "3.8%", "高", "适合补充场景化版本和尾部关键词"),
    ComparisonRecord("版本 E", "deepseek-chat", "79.8", "中下", "中", "3.3%", "高", "建议仅用于低优先级长尾场景"),
)


ARCHIVE_RECORDS: tuple[ArchiveRecord, ...] = (
    ArchiveRecord("BATCH_20260309_01", "春季上新高客单测试", "今天 09:10", "24 条", "88.4", "gpt-4o", "已完成", "3 条进入优先投放池"),
    ArchiveRecord("BATCH_20260308_07", "短视频催单短句补量", "昨天 20:45", "40 条", "83.6", "gpt-4.1-mini", "已完成", "用于 4 轮短视频插播"),
    ArchiveRecord("BATCH_20260308_04", "办公场景商品矩阵", "昨天 15:22", "30 条", "86.1", "claude-3-7-sonnet", "已完成", "适合老板人群和久坐人群双版本"),
    ArchiveRecord("BATCH_20260307_11", "家居氛围感种草", "03-07 18:30", "18 条", "90.2", "gpt-4o", "已归档", "收藏率预估提升明显"),
    ArchiveRecord("BATCH_20260307_06", "母婴痛点解决方案", "03-07 10:05", "22 条", "87.0", "glm-4.5-air", "已完成", "用于详情页和评论区补充"),
    ArchiveRecord("BATCH_20260306_09", "露营装备达人联动稿", "03-06 16:40", "16 条", "84.9", "claude-3-7-sonnet", "待复盘", "达人反馈需要更轻快语气"),
)


class CreativeWorkshopPage(BasePage):
    """创意工坊 / 批量 AI 生成页面。"""

    default_route_id: RouteId = RouteId("creative_workshop")
    default_display_name: str = "创意工坊"
    default_icon_name: str = "rocket_launch"

    def setup_ui(self) -> None:
        """构建创意工坊页面。"""

        self._ai_config_summary_label: QLabel | None = None
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _set_style(
            self,
            f"""
            QWidget {{
                background: {SURFACE_ALT};
                color: {TEXT_STRONG};
            }}
            QFrame[variant='result-card'] {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
            QFrame[variant='soft-card'] {{
                background: {SURFACE};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
            QLabel[role='headline'] {{
                color: {TEXT_STRONG};
                font-size: 18px;
                font-weight: 700;
            }}
            QLabel[role='muted'] {{
                color: {TEXT_MUTED};
                font-size: 12px;
            }}
            QLabel[role='section-title'] {{
                color: {TEXT_STRONG};
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel[role='result-content'] {{
                color: #334155;
                font-size: 13px;
                line-height: 1.65;
            }}
            QLabel[role='eyebrow'] {{
                color: {ACCENT};
                font-size: 11px;
                font-weight: 700;
            }}
            QLabel[role='score-hero'] {{
                font-size: 30px;
                font-weight: 800;
            }}
            QPushButton[variant='ghost-action'] {{
                background: {SURFACE_SOFT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 8px 12px;
                color: {TEXT_MUTED};
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton[variant='ghost-action']:hover {{
                border-color: {ACCENT};
                color: {ACCENT};
                background: {ACCENT_SOFT};
            }}
            """,
        )

        container = PageContainer(
            title="创意工坊",
            description="批量 AI 生成、质量打分、模型对比与批次归档一体化工作台。",
        )
        self._build_header_actions(container)

        split_panel = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.32, 0.68),
            minimum_sizes=(360, 760),
        )
        split_panel.set_first_widget(self._build_left_panel())
        split_panel.set_second_widget(self._build_right_panel())
        container.add_widget(split_panel)
        self.layout.addWidget(container)

    def _build_header_actions(self, container: PageContainer) -> None:
        """页面头部按钮。"""

        self._save_button = SecondaryButton("保存批次配置")
        self._save_button.set_icon_text("◎")
        self._export_button = SecondaryButton("导出全部结果")
        self._export_button.set_icon_text("⇩")
        self._launch_button = PrimaryButton("启动本批任务")
        self._launch_button.set_icon_text("⚡")
        container.add_action(self._save_button)
        container.add_action(self._export_button)
        container.add_action(self._launch_button)

    def _build_left_panel(self) -> QWidget:
        """左侧配置区域。"""

        scroll = ThemedScrollArea(self)
        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        intro_card = InfoCard(
            title="今日创作目标",
            description="围绕春季上新与高客单品，批量生成适合短视频口播、短视频挂车与详情页补充的多版本文案。",
            icon="✦",
            action_text="查看模板策略",
            parent=content,
        )
        content_layout.addWidget(intro_card)
        content_layout.addWidget(self._build_batch_profile_section(content))
        content_layout.addWidget(self._build_keyword_section(content))
        content_layout.addWidget(self._build_generation_strategy_section(content))
        content_layout.addWidget(self._build_ai_config_section(content))
        content_layout.addWidget(self._build_execution_rules_section(content))
        content_layout.addWidget(self._build_launch_section(content))
        content_layout.addStretch(1)

        scroll.set_content_widget(content)
        return scroll

    def _build_batch_profile_section(self, parent: QWidget) -> QWidget:
        """批次画像与模板配置。"""

        section = ContentSection("批量创作配置", icon="⚙", parent=parent)

        self._batch_name_input = ThemedLineEdit(
            label="批次名称",
            placeholder="例如：春季上新高客单测试",
            helper_text="建议按场景 + 目标 + 时间命名，便于后续归档。",
        )
        self._batch_name_input.setText("春季上新高客单测试")
        section.add_widget(self._batch_name_input)

        self._template_combo = ThemedComboBox(
            label="创作模板",
            items=[template.name for template in BATCH_TEMPLATES],
        )
        _call(self._template_combo.combo_box, "setCurrentText", BATCH_TEMPLATES[0].name)
        section.add_widget(self._template_combo)

        self._scene_dropdown = FilterDropdown(
            label="投放场景",
            items=[
                "短视频卖货",
                "短视频口播",
                "商品详情页",
                "矩阵分发",
                "达人合作",
            ],
            include_all=False,
        )
        self._scene_dropdown.set_current_text("短视频卖货")
        section.add_widget(self._scene_dropdown)

        template_summary = self._build_template_summary_card(BATCH_TEMPLATES[0], section)
        section.add_widget(template_summary)
        return section

    def _build_keyword_section(self, parent: QWidget) -> QWidget:
        """关键词与创作方向。"""

        section = ContentSection("关键词与创作方向", icon="⌕", parent=parent)

        self._keyword_editor = ThemedTextEdit(
            label="产品关键词",
            placeholder="每行输入一个产品关键词",
        )
        self._keyword_editor.setPlainText(
            "智能运动手表\n降噪耳机\n人体工学办公椅\n便携咖啡机\n桌面补光灯\n家用净饮机"
        )
        section.add_widget(self._keyword_editor)

        self._direction_editor = ThemedTextEdit(
            label="创作指令补充",
            placeholder="补充品牌语气、禁用词和希望强调的卖点",
        )
        self._direction_editor.setPlainText(
            "语气更像成熟运营策划，不要夸张承诺；优先写真实使用场景；强调体验提升、价值感和购买理由；避免空泛形容词堆叠。"
        )
        section.add_widget(self._direction_editor)

        keyword_hint = self._build_hint_panel(
            title="关键词输入建议",
            lines=(
                "优先输入具体商品词，减少过泛类目词。",
                "每个词对应 2-4 个变体，更利于比较。",
                "同批次尽量控制在同一场景，方便统一评分。",
            ),
            parent=section,
        )
        section.add_widget(keyword_hint)
        return section

    def _build_generation_strategy_section(self, parent: QWidget) -> QWidget:
        """变体与产能策略。"""

        section = ContentSection("变体与产能设置", icon="◫", parent=parent)

        self._preset_combo = ThemedComboBox(
            label="批次预设",
            items=[preset.name for preset in BATCH_PRESETS],
        )
        _call(self._preset_combo.combo_box, "setCurrentText", BATCH_PRESETS[0].name)
        section.add_widget(self._preset_combo)

        self._count_combo = ThemedComboBox(
            label="批量数量",
            items=["12 条", "18 条", "24 条", "30 条", "36 条", "40 条"],
        )
        _call(self._count_combo.combo_box, "setCurrentText", "24 条")
        section.add_widget(self._count_combo)

        self._variation_combo = ThemedComboBox(
            label="变体数量",
            items=["每个关键词 2 版", "每个关键词 3 版", "每个关键词 4 版", "每个关键词 5 版"],
        )
        _call(self._variation_combo.combo_box, "setCurrentText", "每个关键词 3 版")
        section.add_widget(self._variation_combo)

        self._length_combo = ThemedComboBox(
            label="内容长度",
            items=["120-180 字", "180-260 字", "260-380 字", "380-500 字"],
        )
        _call(self._length_combo.combo_box, "setCurrentText", "180-260 字")
        section.add_widget(self._length_combo)

        self._quality_gate_combo = ThemedComboBox(
            label="质量门槛",
            items=["75 分自动保留", "80 分自动保留", "85 分自动保留", "90 分自动保留"],
        )
        _call(self._quality_gate_combo.combo_box, "setCurrentText", "80 分自动保留")
        section.add_widget(self._quality_gate_combo)

        preset_card = self._build_preset_preview_card(BATCH_PRESETS[0], section)
        section.add_widget(preset_card)
        return section

    def _build_ai_config_section(self, parent: QWidget) -> QWidget:
        """AI 配置区域。"""

        section = ContentSection("模型配置面板", icon="◎", parent=parent)
        self._ai_panel = AIConfigPanel(section)
        self._ai_panel.set_config(
            {
                "provider": "openai",
                "model": "gpt-4o",
                "agent_role": "文案专家",
                "temperature": 0.8,
                "max_tokens": 2048,
                "top_p": 0.9,
            }
        )
        section.add_widget(self._ai_panel)

        summary_card = QFrame(section)
        _call(summary_card, "setProperty", "variant", "soft-card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(14, 14, 14, 14)
        summary_layout.setSpacing(6)
        summary_title = QLabel("当前模型摘要", summary_card)
        _call(summary_title, "setProperty", "role", "section-title")
        self._ai_config_summary_label = QLabel("等待同步 AI 配置…", summary_card)
        _call(self._ai_config_summary_label, "setProperty", "role", "muted")
        _set_word_wrap(self._ai_config_summary_label)
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self._ai_config_summary_label)
        section.add_widget(summary_card)

        model_note = self._build_hint_panel(
            title="当前模型策略",
            lines=(
                "主模型负责高质量初稿，辅模型负责低成本扩写与重生成。",
                "默认开启多模型比稿，保留质量分前 2 的版本。",
                "高客单模板建议温度保持在 0.7-0.9 之间。",
            ),
            parent=section,
        )
        section.add_widget(model_note)
        _connect(self._ai_panel.config_changed, self._update_ai_config_summary)
        self._update_ai_config_summary()
        return section

    def _build_execution_rules_section(self, parent: QWidget) -> QWidget:
        """执行规则与自动化策略。"""

        section = ContentSection("执行规则", icon="▣", parent=parent)
        section.add_widget(self._build_toggle_row("自动质量评分", "生成完成后按开头抓力、卖点完整度、商业性自动打分。", True, section))
        section.add_widget(self._build_toggle_row("自动去重合并", "检测高度相似表达，优先保留转化推动更强的版本。", True, section))
        section.add_widget(self._build_toggle_row("低分自动重写", "低于 78 分的结果自动补写一轮，减少人工回收时间。", True, section))
        section.add_widget(self._build_toggle_row("同步生成对比视图", "每批自动生成模型对比表与最佳版本摘要。", True, section))
        section.add_widget(self._build_toggle_row("自动保存到批次档案", "完成后直接沉淀到历史批次与导出池。", False, section))
        return section

    def _build_launch_section(self, parent: QWidget) -> QWidget:
        """启动任务区。"""

        section = ContentSection("启动任务", icon="⚡", parent=parent)

        status_row = QWidget(section)
        status_layout = QHBoxLayout(status_row)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        status_layout.addWidget(StatusBadge("模板已就绪", tone="success", parent=status_row))
        status_layout.addWidget(StatusBadge("6 个关键词", tone="brand", parent=status_row))
        status_layout.addWidget(StatusBadge("预计 24 条结果", tone="info", parent=status_row))
        status_layout.addWidget(StatusBadge("多模型比稿", tone="warning", parent=status_row))
        status_layout.addStretch(1)
        section.add_widget(status_row)

        summary = self._build_hint_panel(
            title="执行摘要",
            lines=(
                "本批次将输出 6 个关键词 × 每词 3 个变体，共约 18-24 条有效结果。",
                "优先走 gpt-4o 主模型，低分稿件自动分流到轻量模型重写。",
                "完成后自动进入结果评分、导出池和模型对比视图。",
            ),
            parent=section,
        )
        section.add_widget(summary)

        action_row = QWidget(section)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        preview_button = SecondaryButton("预览批次配置", action_row)
        preview_button.set_icon_text("◌")
        run_button = PrimaryButton("立即启动批量生成", action_row)
        run_button.set_icon_text("⚡")
        action_layout.addWidget(preview_button)
        action_layout.addWidget(run_button)
        section.add_widget(action_row)
        return section

    def _build_right_panel(self) -> QWidget:
        """右侧结果区域。"""

        scroll = ThemedScrollArea(self)
        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        content_layout.addWidget(self._build_overview_band(content))
        content_layout.addWidget(self._build_progress_section(content))
        content_layout.addWidget(self._build_live_output_section(content))
        content_layout.addWidget(self._build_results_section(content))
        content_layout.addWidget(self._build_comparison_section(content))
        content_layout.addWidget(self._build_archive_section(content))
        content_layout.addStretch(1)

        scroll.set_content_widget(content)
        return scroll

    def _build_overview_band(self, parent: QWidget) -> QWidget:
        """顶部概览。"""

        wrapper = QFrame(parent)
        _call(wrapper, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QWidget(wrapper)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        header_text = QWidget(header)
        header_text_layout = QVBoxLayout(header_text)
        header_text_layout.setContentsMargins(0, 0, 0, 0)
        header_text_layout.setSpacing(4)

        title = QLabel("任务管理与生成结果", header_text)
        _call(title, "setProperty", "role", "headline")
        subtitle = QLabel("实时查看批次进度、筛选高质量文案并沉淀最佳模型方案。", header_text)
        _call(subtitle, "setProperty", "role", "muted")
        _set_word_wrap(subtitle)
        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)

        header_actions = QWidget(header)
        actions_layout = QHBoxLayout(header_actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)
        actions_layout.addWidget(SecondaryButton("保存到批次档案", header_actions))
        actions_layout.addWidget(SecondaryButton("导出评分前十", header_actions))
        actions_layout.addWidget(PrimaryButton("打开模型对比", header_actions))

        header_layout.addWidget(header_text)
        header_layout.addStretch(1)
        header_layout.addWidget(header_actions)
        layout.addWidget(header)

        metrics_row = QWidget(wrapper)
        metrics_layout = QHBoxLayout(metrics_row)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(12)
        for metric in INSIGHT_METRICS:
            metrics_layout.addWidget(self._build_metric_card(metric, metrics_row))
        layout.addWidget(metrics_row)
        return wrapper

    def _build_progress_section(self, parent: QWidget) -> QWidget:
        """任务进度区。"""

        section = ContentSection("批次进度追踪", icon="↗", parent=parent)

        summary_card = QFrame(section)
        _call(summary_card, "setProperty", "variant", "soft-card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(18, 18, 18, 18)
        summary_layout.setSpacing(12)

        top_row = QWidget(summary_card)
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(10)
        top_row_layout.addWidget(StatusBadge("进行中", tone="brand", parent=top_row))
        top_row_layout.addWidget(StatusBadge("BATCH_20260309_01", tone="info", parent=top_row))
        top_row_layout.addWidget(StatusBadge("已完成 12/24", tone="success", parent=top_row))
        top_row_layout.addStretch(1)
        top_row_layout.addWidget(self._make_ghost_button("暂停批次", top_row))
        top_row_layout.addWidget(self._make_ghost_button("查看日志", top_row))
        summary_layout.addWidget(top_row)

        description = QLabel(
            "当前批次正在并发处理 6 个商品关键词，主模型负责初稿，辅模型正在对低分稿件进行补写与变体扩展。",
            summary_card,
        )
        _call(description, "setProperty", "role", "muted")
        _set_word_wrap(description)
        summary_layout.addWidget(description)

        self._progress_bar = TaskProgressBar(62)
        summary_layout.addWidget(self._progress_bar)

        stat_row = QWidget(summary_card)
        stat_layout = QHBoxLayout(stat_row)
        stat_layout.setContentsMargins(0, 0, 0, 0)
        stat_layout.setSpacing(10)
        stat_layout.addWidget(StatsBadge(label="已评分", value="12 条", icon="质", tone="brand", parent=stat_row))
        stat_layout.addWidget(StatsBadge(label="高分稿", value="8 条", icon="优", tone="success", parent=stat_row))
        stat_layout.addWidget(StatsBadge(label="待重写", value="2 条", icon="修", tone="warning", parent=stat_row))
        stat_layout.addWidget(StatsBadge(label="预计完成", value="4 分钟", icon="时", tone="info", parent=stat_row))
        stat_layout.addStretch(1)
        summary_layout.addWidget(stat_row)
        section.add_widget(summary_card)

        queue_host = QWidget(section)
        queue_layout = QVBoxLayout(queue_host)
        queue_layout.setContentsMargins(0, 0, 0, 0)
        queue_layout.setSpacing(10)
        for task in QUEUE_TASKS:
            queue_layout.addWidget(self._build_queue_card(task, queue_host))
        section.add_widget(queue_host)
        return section

    def _build_live_output_section(self, parent: QWidget) -> QWidget:
        """流式结果预览。"""

        section = ContentSection("流式生成窗口", icon="✦", parent=parent)
        self._streaming_output = StreamingOutputWidget(section)
        self._streaming_output.clear()
        self._streaming_output.set_loading(True)
        self._streaming_output.append_chunk("【当前任务】智能运动手表 · 版本 3\n")
        self._streaming_output.append_chunk("开头先用“极限场景也能稳住状态”建立专业感，")
        self._streaming_output.append_chunk("再补健康监测与材质价值，最后落到“不是装饰品，是决策装备”的购买理由。")
        self._streaming_output.set_token_usage(836, 1242)
        self._streaming_output.set_loading(False)
        section.add_widget(self._streaming_output)
        return section

    def _build_results_section(self, parent: QWidget) -> QWidget:
        """结果卡片区。"""

        section = ContentSection("生成结果卡片", icon="▤", parent=parent)

        toolbar = QWidget(section)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        self._result_search = SearchBar("搜索关键词、标题或标签…")
        self._quality_filter = FilterDropdown("质量筛选", ["全部", "90 分以上", "80-89 分", "79 分以下"], include_all=False)
        self._model_filter = FilterDropdown("模型筛选", ["全部", "gpt-4o", "claude-3-7-sonnet", "gpt-4.1-mini", "glm-4.5-air", "deepseek-chat"], include_all=False)
        self._status_filter = FilterDropdown("状态筛选", ["全部", "可导出", "待复选", "待人工润色", "待重生成"], include_all=False)

        toolbar_layout.addWidget(self._result_search)
        toolbar_layout.addWidget(self._quality_filter)
        toolbar_layout.addWidget(self._model_filter)
        toolbar_layout.addWidget(self._status_filter)
        section.add_widget(toolbar)

        overview_tags = QWidget(section)
        overview_tags_layout = QHBoxLayout(overview_tags)
        overview_tags_layout.setContentsMargins(0, 0, 0, 0)
        overview_tags_layout.setSpacing(8)
        result_overview_tags: tuple[tuple[str, BadgeTone], ...] = (
            ("高分优先导出", "success"),
            ("同词多版本保留", "brand"),
            ("低分自动重写开启", "warning"),
            ("支持批次归档", "info"),
        )
        for chip_text, tone in result_overview_tags:
            overview_tags_layout.addWidget(TagChip(chip_text, tone=tone, parent=overview_tags))
        overview_tags_layout.addStretch(1)
        section.add_widget(overview_tags)

        section.add_widget(self._build_result_grid(section))
        return section

    def _build_result_grid(self, parent: QWidget) -> QWidget:
        """双栏结果卡片栅格。"""

        host = QWidget(parent)
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        left_column = QWidget(host)
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        right_column = QWidget(host)
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        for index, result in enumerate(GENERATION_RESULTS):
            if index % 2 == 0:
                left_layout.addWidget(self._build_result_card(result, left_column))
            else:
                right_layout.addWidget(self._build_result_card(result, right_column))

        left_layout.addStretch(1)
        right_layout.addStretch(1)
        layout.addWidget(left_column)
        layout.addWidget(right_column)
        return host

    def _build_result_card(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """单张结果卡片。"""

        card = QFrame(parent)
        _call(card, "setProperty", "variant", "result-card")
        _set_style(card, f"QFrame {{ border-left: 4px solid {_score_color(result.quality_score)}; }}")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(self._build_result_header(result, card))
        layout.addWidget(self._build_result_score_band(result, card))
        layout.addWidget(self._build_result_body(result, card))
        layout.addWidget(self._build_result_tags(result, card))
        layout.addWidget(self._build_result_quality_dimensions(result, card))
        layout.addWidget(self._build_result_footer(result, card))
        return card

    def _build_result_header(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """结果卡片头部。"""

        header = QWidget(parent)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        text_wrap = QWidget(header)
        text_layout = QVBoxLayout(text_wrap)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        eyebrow = QLabel(f"关键词：{result.keyword}", text_wrap)
        _call(eyebrow, "setProperty", "role", "eyebrow")
        title = QLabel(result.title, text_wrap)
        _call(title, "setProperty", "role", "section-title")
        _set_word_wrap(title)
        summary = QLabel(result.hook_summary, text_wrap)
        _call(summary, "setProperty", "role", "muted")
        _set_word_wrap(summary)
        text_layout.addWidget(eyebrow)
        text_layout.addWidget(title)
        text_layout.addWidget(summary)

        right_wrap = QWidget(header)
        right_layout = QVBoxLayout(right_wrap)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        right_layout.addWidget(StatusBadge(result.status, tone=_score_tone(result.quality_score), parent=right_wrap))
        right_layout.addWidget(StatusBadge(result.created_at, tone="neutral", parent=right_wrap))

        layout.addWidget(text_wrap)
        layout.addStretch(1)
        layout.addWidget(right_wrap)
        return header

    def _build_result_score_band(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """结果评分信息带。"""

        band = QFrame(parent)
        _call(band, "setProperty", "variant", "soft-card")
        layout = QHBoxLayout(band)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        score_wrap = QWidget(band)
        score_layout = QVBoxLayout(score_wrap)
        score_layout.setContentsMargins(0, 0, 0, 0)
        score_layout.setSpacing(2)
        score_label = QLabel(str(result.quality_score), score_wrap)
        _call(score_label, "setProperty", "role", "score-hero")
        _set_style(score_label, f"color: {_score_color(result.quality_score)};")
        score_tip = QLabel("质量总分", score_wrap)
        _call(score_tip, "setProperty", "role", "muted")
        score_layout.addWidget(score_label)
        score_layout.addWidget(score_tip)

        metrics_wrap = QWidget(band)
        metrics_layout = QHBoxLayout(metrics_wrap)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)
        metrics_layout.addWidget(StatsBadge(label="点击预估", value=result.click_forecast, icon="点", tone="info", parent=metrics_wrap))
        metrics_layout.addWidget(StatsBadge(label="转化预估", value=result.conversion_forecast, icon="转", tone="success", parent=metrics_wrap))
        metrics_layout.addWidget(StatsBadge(label="原创度", value=result.uniqueness, icon="新", tone="brand", parent=metrics_wrap))

        detail_wrap = QWidget(band)
        detail_layout = QVBoxLayout(detail_wrap)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(4)
        detail_layout.addWidget(QLabel(f"模型：{result.model}", detail_wrap))
        detail_layout.addWidget(QLabel(f"模板：{result.template_name}", detail_wrap))
        detail_layout.addWidget(QLabel(f"风格：{result.tone_label} · {result.length_label}", detail_wrap))
        _set_style(detail_wrap, f"QLabel {{ color: {TEXT_MUTED}; font-size: 12px; }}")

        layout.addWidget(score_wrap)
        layout.addWidget(metrics_wrap)
        layout.addStretch(1)
        layout.addWidget(detail_wrap)
        return band

    def _build_result_body(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """结果正文。"""

        body = QLabel(result.content, parent)
        _call(body, "setProperty", "role", "result-content")
        _set_word_wrap(body)
        return body

    def _build_result_tags(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """结果标签区。"""

        tags_row = QWidget(parent)
        layout = QHBoxLayout(tags_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for tag in result.style_tags:
            layout.addWidget(TagChip(tag, tone="brand", parent=tags_row))
        layout.addStretch(1)
        return tags_row

    def _build_result_quality_dimensions(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """结果评分维度。"""

        host = QWidget(parent)
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        for label, value in result.quality_dimensions:
            layout.addWidget(self._build_dimension_card(label, value, host))
        return host

    def _build_result_footer(self, result: GenerationResult, parent: QWidget) -> QWidget:
        """结果底部操作与洞察。"""

        wrapper = QWidget(parent)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        insight_row = QWidget(wrapper)
        insight_layout = QHBoxLayout(insight_row)
        insight_layout.setContentsMargins(0, 0, 0, 0)
        insight_layout.setSpacing(8)
        for insight in result.insight_tags:
            insight_layout.addWidget(TagChip(insight, tone="neutral", parent=insight_row))
        insight_layout.addStretch(1)
        layout.addWidget(insight_row)

        action_row = QWidget(wrapper)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        action_layout.addWidget(self._make_ghost_button("复制", action_row))
        action_layout.addWidget(self._make_ghost_button("加入导出池", action_row))
        action_layout.addWidget(self._make_ghost_button("设为对比样本", action_row))
        action_layout.addStretch(1)
        action_layout.addWidget(SecondaryButton("保存此版本", action_row))
        action_layout.addWidget(PrimaryButton("标记为优先投放", action_row))
        layout.addWidget(action_row)
        return wrapper

    def _build_comparison_section(self, parent: QWidget) -> QWidget:
        """模型对比区。"""

        section = ContentSection("模型对比视图", icon="⇄", parent=parent)

        header_note = self._build_hint_panel(
            title="本批对比结论",
            lines=(
                "gpt-4o 在高客单场景下的开头抓力和商业性最稳定。",
                "claude-3-7-sonnet 在长文案叙述与品牌感表达上更完整。",
                "gpt-4.1-mini 成本效率最高，适合补写和大规模铺量。",
            ),
            parent=section,
        )
        section.add_widget(header_note)

        comparison_wrap = QWidget(section)
        comparison_layout = QHBoxLayout(comparison_wrap)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        comparison_layout.setSpacing(12)

        table_host = QFrame(comparison_wrap)
        _call(table_host, "setProperty", "variant", "soft-card")
        table_layout = QVBoxLayout(table_host)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(10)
        table_title = QLabel("模型得分与建议", table_host)
        _call(table_title, "setProperty", "role", "section-title")
        table_layout.addWidget(table_title)

        self._comparison_table = DataTable(
            headers=["方案", "模型", "平均分", "钩子", "商业性", "点击预估", "成本效率", "建议"],
            rows=[
                [
                    record.variant,
                    record.model,
                    record.average_score,
                    record.hook_power,
                    record.business_value,
                    record.click_estimate,
                    record.cost_efficiency,
                    record.recommendation,
                ]
                for record in COMPARISON_RECORDS
            ],
            page_size=5,
            empty_text="暂无模型对比数据",
            parent=table_host,
        )
        table_layout.addWidget(self._comparison_table)

        detail_host = QFrame(comparison_wrap)
        _call(detail_host, "setProperty", "variant", "soft-card")
        detail_layout = QVBoxLayout(detail_host)
        detail_layout.setContentsMargins(14, 14, 14, 14)
        detail_layout.setSpacing(10)

        detail_title = QLabel("最佳版本摘要", detail_host)
        _call(detail_title, "setProperty", "role", "section-title")
        detail_layout.addWidget(detail_title)
        detail_layout.addWidget(StatusBadge("当前胜出：版本 A / gpt-4o", tone="success", parent=detail_host))

        winner_content = StreamingOutputWidget(detail_host)
        winner_content.clear()
        winner_content.append_chunk("【最佳版本结论】\n")
        winner_content.append_chunk("开头把“极限场景稳定性”作为第一钩子，能迅速筛出高意向人群；")
        winner_content.append_chunk("中段补健康监测与材质证明，结尾再落到“辅助决策的装备”这一层，商业解释足够完整。")
        winner_content.set_token_usage(412, 666)
        detail_layout.addWidget(winner_content)

        detail_layout.addWidget(StatsBadge(label="推荐投放", value="短视频主版本", icon="优", tone="success", parent=detail_host))
        detail_layout.addWidget(StatsBadge(label="备选用途", value="详情页补充", icon="备", tone="info", parent=detail_host))
        detail_layout.addWidget(StatsBadge(label="复写建议", value="补价格锚点", icon="修", tone="warning", parent=detail_host))
        detail_layout.addStretch(1)

        comparison_layout.addWidget(table_host)
        comparison_layout.addWidget(detail_host)
        section.add_widget(comparison_wrap)
        return section

    def _build_archive_section(self, parent: QWidget) -> QWidget:
        """历史批次与导出区。"""

        section = ContentSection("批次归档与导出", icon="☰", parent=parent)

        top_row = QWidget(section)
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)
        top_layout.addWidget(StatusBadge("已启用批次沉淀", tone="success", parent=top_row))
        top_layout.addWidget(StatusBadge("支持 Excel / CSV / 素材池", tone="info", parent=top_row))
        top_layout.addStretch(1)
        top_layout.addWidget(SecondaryButton("保存当前批次", top_row))
        top_layout.addWidget(PrimaryButton("导出全部结果", top_row))
        section.add_widget(top_row)

        archive_table = DataTable(
            headers=["批次编号", "批次名称", "创建时间", "生成量", "平均分", "胜出模型", "状态", "备注"],
            rows=[
                [
                    record.batch_id,
                    record.batch_name,
                    record.created_at,
                    record.generated_count,
                    record.average_score,
                    record.winning_model,
                    record.status,
                    record.note,
                ]
                for record in ARCHIVE_RECORDS
            ],
            page_size=6,
            empty_text="暂无历史批次",
            parent=section,
        )
        section.add_widget(archive_table)

        export_panel = QFrame(section)
        _call(export_panel, "setProperty", "variant", "soft-card")
        export_layout = QHBoxLayout(export_panel)
        export_layout.setContentsMargins(16, 16, 16, 16)
        export_layout.setSpacing(12)

        export_text = QWidget(export_panel)
        export_text_layout = QVBoxLayout(export_text)
        export_text_layout.setContentsMargins(0, 0, 0, 0)
        export_text_layout.setSpacing(4)
        export_title = QLabel("导出建议", export_text)
        _call(export_title, "setProperty", "role", "section-title")
        export_desc = QLabel(
            "建议优先导出质量分前 10 的结果，并同步保留低成本模型的备选版本，方便后续做低预算测试与评论区补量。",
            export_text,
        )
        _call(export_desc, "setProperty", "role", "muted")
        _set_word_wrap(export_desc)
        export_text_layout.addWidget(export_title)
        export_text_layout.addWidget(export_desc)

        export_actions = QWidget(export_panel)
        export_actions_layout = QHBoxLayout(export_actions)
        export_actions_layout.setContentsMargins(0, 0, 0, 0)
        export_actions_layout.setSpacing(8)
        export_actions_layout.addWidget(SecondaryButton("导出 Excel", export_actions))
        export_actions_layout.addWidget(SecondaryButton("导出 CSV", export_actions))
        export_actions_layout.addWidget(PrimaryButton("推送至素材池", export_actions))

        export_layout.addWidget(export_text)
        export_layout.addStretch(1)
        export_layout.addWidget(export_actions)
        section.add_widget(export_panel)
        return section

    def _build_template_summary_card(self, template: BatchTemplate, parent: QWidget) -> QWidget:
        """模板摘要卡。"""

        card = QFrame(parent)
        _call(card, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel(template.name, card)
        _call(title, "setProperty", "role", "section-title")
        summary = QLabel(template.summary, card)
        _call(summary, "setProperty", "role", "muted")
        _set_word_wrap(summary)
        layout.addWidget(title)
        layout.addWidget(summary)

        info_row = QWidget(card)
        info_layout = QHBoxLayout(info_row)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        info_layout.addWidget(TagChip(template.category, tone="brand", parent=info_row))
        info_layout.addWidget(TagChip(template.output_mode, tone="info", parent=info_row))
        info_layout.addWidget(TagChip(template.expected_time, tone="success", parent=info_row))
        info_layout.addStretch(1)
        layout.addWidget(info_row)

        note = QLabel(
            f"适用场景：{template.target_scene}\n目标人群：{template.target_audience}\n最佳用途：{template.best_use}",
            card,
        )
        _call(note, "setProperty", "role", "muted")
        _set_word_wrap(note)
        layout.addWidget(note)

        tag_row = QWidget(card)
        tag_layout = QHBoxLayout(tag_row)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(8)
        for item in template.highlights:
            tag_layout.addWidget(TagChip(item, tone="neutral", parent=tag_row))
        tag_layout.addStretch(1)
        layout.addWidget(tag_row)
        return card

    def _build_preset_preview_card(self, preset: BatchPreset, parent: QWidget) -> QWidget:
        """预设摘要卡。"""

        card = QFrame(parent)
        _call(card, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        name = QLabel(f"当前预设：{preset.name}", card)
        _call(name, "setProperty", "role", "section-title")
        layout.addWidget(name)
        layout.addWidget(QLabel(f"批量数量：{preset.count}", card))
        layout.addWidget(QLabel(f"变体配置：{preset.variations}", card))
        layout.addWidget(QLabel(f"长度控制：{preset.length}", card))
        layout.addWidget(QLabel(f"质量门槛：{preset.quality_gate}", card))
        note = QLabel(preset.note, card)
        _call(note, "setProperty", "role", "muted")
        _set_word_wrap(note)
        layout.addWidget(note)
        _set_style(card, f"QLabel {{ color: {TEXT_MUTED}; font-size: 12px; }} QLabel[role='section-title'] {{ color: {TEXT_STRONG}; font-size: 15px; font-weight: 700; }}")
        return card

    def _build_hint_panel(self, title: str, lines: Sequence[str], parent: QWidget) -> QWidget:
        """轻量提示面板。"""

        panel = QFrame(parent)
        _call(panel, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        title_label = QLabel(title, panel)
        _call(title_label, "setProperty", "role", "section-title")
        layout.addWidget(title_label)
        for line in lines:
            item = QLabel(f"• {line}", panel)
            _call(item, "setProperty", "role", "muted")
            _set_word_wrap(item)
            layout.addWidget(item)
        return panel

    def _update_ai_config_summary(self, _config: dict[str, object] | None = None) -> None:
        if getattr(self, "_ai_panel", None) is None or self._ai_config_summary_label is None:
            return
        config = self._ai_panel.config()
        self._ai_config_summary_label.setText(
            f"{config['provider_label']} · {config['model']} · {config['agent_role']} · 温度 {config['temperature']}"
            f" · Top-p {config['top_p']} · 输出上限 {config['max_tokens']} Token。"
            "当前批次默认先走高质量初稿，再把低分稿件分流到轻量模型做重写补量。"
        )

    def _build_toggle_row(self, title: str, description: str, checked: bool, parent: QWidget) -> QWidget:
        """开关行。"""

        row = QFrame(parent)
        _call(row, "setProperty", "variant", "soft-card")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        text_wrap = QWidget(row)
        text_layout = QVBoxLayout(text_wrap)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        title_label = QLabel(title, text_wrap)
        _call(title_label, "setProperty", "role", "section-title")
        desc_label = QLabel(description, text_wrap)
        _call(desc_label, "setProperty", "role", "muted")
        _set_word_wrap(desc_label)
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        toggle = ToggleSwitch(checked=checked)
        layout.addWidget(text_wrap)
        layout.addStretch(1)
        layout.addWidget(toggle)
        return row

    def _build_metric_card(self, metric: InsightMetric, parent: QWidget) -> QWidget:
        """顶部概览指标卡。"""

        card = QFrame(parent)
        _call(card, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        icon_row = QWidget(card)
        icon_layout = QHBoxLayout(icon_row)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(6)
        icon_layout.addWidget(StatusBadge(metric.icon, tone=metric.tone, parent=icon_row))
        icon_layout.addStretch(1)

        label = QLabel(metric.label, card)
        _call(label, "setProperty", "role", "muted")
        value = QLabel(metric.value, card)
        _call(value, "setProperty", "role", "headline")
        detail = QLabel(metric.detail, card)
        _call(detail, "setProperty", "role", "muted")
        _set_word_wrap(detail)

        layout.addWidget(icon_row)
        layout.addWidget(label)
        layout.addWidget(value)
        layout.addWidget(detail)
        return card

    def _build_queue_card(self, task: QueueTask, parent: QWidget) -> QWidget:
        """队列任务卡片。"""

        card = QFrame(parent)
        _call(card, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        top = QWidget(card)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        name = QLabel(task.keyword, top)
        _call(name, "setProperty", "role", "section-title")
        top_layout.addWidget(name)
        top_layout.addStretch(1)
        top_layout.addWidget(StatusBadge(task.state, tone=task.tone, parent=top))
        layout.addWidget(top)

        meta = QLabel(f"进度：{task.progress}    ·    预计：{task.eta}    ·    模型：{task.model}", card)
        _call(meta, "setProperty", "role", "muted")
        _set_word_wrap(meta)
        layout.addWidget(meta)

        note = QLabel(task.note, card)
        _call(note, "setProperty", "role", "muted")
        _set_word_wrap(note)
        layout.addWidget(note)
        return card

    def _build_dimension_card(self, label: str, value: int, parent: QWidget) -> QWidget:
        """单个评分维度卡。"""

        card = QFrame(parent)
        _call(card, "setProperty", "variant", "soft-card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        label_widget = QLabel(label, card)
        _call(label_widget, "setProperty", "role", "muted")
        value_widget = QLabel(f"{value}", card)
        _call(value_widget, "setProperty", "role", "section-title")
        _set_style(value_widget, f"color: {_score_color(value)};")
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        return card

    def _make_ghost_button(self, text: str, parent: QWidget) -> QPushButton:
        """创建轻量幽灵按钮。"""

        button = QPushButton(text, parent)
        _call(button, "setProperty", "variant", "ghost-action")
        return button

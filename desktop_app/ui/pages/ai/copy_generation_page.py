# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportCallIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""AI 文案生成页面。"""

from dataclasses import dataclass

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    AIStatusIndicator,
    ContentSection,
    DataTable,
    FormGroup,
    IconButton,
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
    TagInput,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedScrollArea,
    ThemedTextEdit,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

ACCENT = "#00F2EA"
ACCENT_SOFT = "rgba(0, 242, 234, 0.10)"
ACCENT_MEDIUM = "rgba(0, 242, 234, 0.16)"
ACCENT_STRONG = "rgba(0, 242, 234, 0.24)"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F6FAFA"
SURFACE_SOFT = "#EEF6F6"
SURFACE_MUTED = "#E8F0F0"
BORDER = "#D7E5E5"
BORDER_STRONG = "#B8CCCC"
TEXT = "#102525"
TEXT_MUTED = "#5D7575"
TEXT_FAINT = "#8AA1A1"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"
INFO = "#38BDF8"
DARK_SURFACE = "#0F2323"


def _call(target: object, method_name: str, *args: object) -> object | None:
    """安全调用可能不存在的方法。"""

    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args)
    return None


def _connect(signal_object: object, callback: object) -> None:
    """安全连接信号。"""

    connect = getattr(signal_object, "connect", None)
    if callable(connect):
        connect(callback)


def _badge_tone(value: str) -> BadgeTone:
    """将字符串值转为徽标色调。"""

    if value == "success":
        return "success"
    if value == "warning":
        return "warning"
    if value == "error":
        return "error"
    if value == "info":
        return "info"
    if value == "brand":
        return "brand"
    return "neutral"


def _words_count(text: str) -> int:
    """统计可见字符数。"""

    return len("".join(character for character in text if not character.isspace()))


@dataclass(frozen=True)
class PromptTemplateMeta:
    """提示模板元信息。"""

    name: str
    category: str
    audience: str
    goal: str
    summary: str
    prompt: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class CopyVariant:
    """文案版本卡片数据。"""

    code: str
    title: str
    subtitle: str
    copy_text: str
    scene: str
    conversion_goal: str
    quality_score: str
    compliance_score: str
    estimated_ctr: str
    tone: str
    tags: tuple[str, ...]
    warning_note: str | None = None
    suggested_words: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScoreMetric:
    """质量评分拆解。"""

    label: str
    score: str
    detail: str
    tone: str


@dataclass(frozen=True)
class ComparisonPoint:
    """A/B 对比维度。"""

    dimension: str
    variant_a: str
    variant_b: str
    recommendation: str
    tone: str


@dataclass(frozen=True)
class ComplianceIssue:
    """合规风险项。"""

    phrase: str
    category: str
    level: str
    explanation: str
    alternatives: tuple[str, ...]


@dataclass(frozen=True)
class HistoryEntry:
    """历史记录条目。"""

    created_at: str
    product_name: str
    audience: str
    style: str
    best_variant: str
    quality_score: str
    compliance_score: str
    status: str


PROMPT_TEMPLATES: tuple[PromptTemplateMeta, ...] = (
    PromptTemplateMeta(
        name="短视频爆款冲榜",
        category="高转化模板",
        audience="18-30 岁都市通勤女性",
        goal="提升点击率与进房停留",
        summary="适合 3 秒抓眼球、前半段强利益点、后半段强化限时优惠。",
        prompt=(
            "你是 TikTok Shop 资深文案策划，请围绕 {product_name} 生成 4 版中文卖货文案。"
            "要求：首句直接抓痛点，突出便携、防漏、视觉高级感；面向 {audience}；"
            "语言节奏适合短视频口播字幕；禁止绝对化、医疗化、夸张承诺；输出标题、主文案、CTA。"
        ),
        tags=("短视频", "高点击", "冲榜", "限时优惠"),
    ),
    PromptTemplateMeta(
        name="短视频种草转化",
        category="种草模板",
        audience="精致宝妈 / 家庭收纳人群",
        goal="提升收藏率与评论互动",
        summary="先讲使用场景，再给出情绪价值，最后轻推成交。",
        prompt=(
            "请以 TikTok 短视频种草视角，为 {product_name} 创作 3 版文案。"
            "核心结构：真实场景切入 + 细节感受 + 使用收益 + 行动引导；"
            "语言要自然、可信、像用户真实分享，适度加入口语停顿。"
        ),
        tags=("短视频", "种草", "真实体验", "互动评论"),
    ),
    PromptTemplateMeta(
        name="大促节点抢购提醒",
        category="促销模板",
        audience="价格敏感型新客",
        goal="放大优惠感知与下单紧迫感",
        summary="适合大促期、秒杀、组合套装场景，强调门槛低与限时窗口。",
        prompt=(
            "围绕 {product_name} 生成 5 条大促型中文文案，平台为 {platform}。"
            "要求：突出价格利益、赠品、库存紧张感，但避免虚假倒计时和违规承诺；"
            "适度加入表情符号与行动短句，每条控制在 80-120 字。"
        ),
        tags=("大促", "秒杀", "库存提醒", "优惠机制"),
    ),
    PromptTemplateMeta(
        name="新品首发质感表达",
        category="品牌模板",
        audience="注重审美与品质的白领人群",
        goal="强化品牌感与客单提升",
        summary="适合新品首发、礼赠场景、需要更高质感表达的页面。",
        prompt=(
            "请从品牌升级视角，为 {product_name} 生成 4 版首发文案。"
            "基调为 {tone}，强调设计、材质、送礼体面感、细节工艺；"
            "避免廉价叫卖口吻，整体保持简洁高级，并包含适度的购买引导。"
        ),
        tags=("新品", "品牌调性", "高级感", "礼赠场景"),
    ),
)

COPY_VARIANTS: tuple[CopyVariant, ...] = (
    CopyVariant(
        code="版本 01",
        title="高转化痛点切入",
        subtitle="优先推荐",
        copy_text=(
            "每天通勤都怕咖啡洒包里？这款 380ml 轻量保温杯直接把“防漏 + 高颜值 + 单手开盖”一次配齐。"
            "放进通勤包不占地，早八到午后三点依旧温热在线，拍视频也很出片。现在入手还有杯刷和吸管盖套装，"
            "想要一杯多用、上班出门都顺手的姐妹，真的可以闭眼加入购物车。"
        ),
        scene="通勤场景 / 短视频字幕",
        conversion_goal="提高点击率与下单转化",
        quality_score="92",
        compliance_score="96",
        estimated_ctr="4.8%",
        tone="专业严谨",
        tags=("高点击", "通勤痛点", "防漏卖点", "礼赠套装"),
    ),
    CopyVariant(
        code="版本 02",
        title="情绪价值种草",
        subtitle="收藏率最高",
        copy_text=(
            "最近包里最离不开的小物，就是这只雾感奶油色保温杯。早上装燕麦拿铁，下午装温水，"
            "一整天都觉得自己的节奏被照顾到了。杯盖顺滑、杯口圆润、女生单手也能轻松开合，"
            "拍桌面视频干净又高级。如果你也想给忙碌日常加一点轻松感，这款真的值得先加入心愿单。"
        ),
        scene="短视频种草 / 详情页首屏",
        conversion_goal="拉升收藏与评论互动",
        quality_score="89",
        compliance_score="98",
        estimated_ctr="4.3%",
        tone="亲切随性",
        tags=("高颜值", "情绪价值", "桌面美学", "通勤日常"),
    ),
    CopyVariant(
        code="版本 03",
        title="强刺激利益表达",
        subtitle="建议修改",
        copy_text=(
            "这可能是今年通勤杯里最强的一款：轻、稳、保温久，首批用户都说喝水频率明显上来了。"
            "想要上班不手忙脚乱、外出不担心漏水、拍视频还要显高级感，它几乎一步到位。"
            "现在活动价入手特别划算，适合正在找高颜值实用杯子的你。"
        ),
        scene="短视频口播 / 冷启动拉新",
        conversion_goal="快速抓眼球",
        quality_score="84",
        compliance_score="72",
        estimated_ctr="4.9%",
        tone="专业严谨",
        tags=("冲击力强", "短视频口播", "高对比卖点"),
        warning_note="含绝对化描述词“最强”，建议替换为更稳妥表达。",
        suggested_words=("表现更稳", "体验更顺手", "性能出色"),
    ),
    CopyVariant(
        code="版本 04",
        title="场景化礼赠推荐",
        subtitle="客单价友好",
        copy_text=(
            "如果你最近在挑一份不踩雷的小礼物，可以看看这只高颜值保温杯。配色温柔，拿在手里很轻，"
            "办公室、健身房、露营都用得上；关键是杯盖防漏，日常放包里也更省心。"
            "自用顺手，送朋友也很体面，预算不高但很容易送到心坎上。"
        ),
        scene="礼赠场景 / 商品详情页",
        conversion_goal="提升送礼场景成交",
        quality_score="90",
        compliance_score="97",
        estimated_ctr="4.1%",
        tone="亲切随性",
        tags=("礼赠", "高颜值", "多场景", "送礼体面"),
    ),
)

QUALITY_BREAKDOWN: tuple[ScoreMetric, ...] = (
    ScoreMetric("卖点清晰度", "94", "核心卖点出现频率合理，前 15 字即完成价值表达。", "success"),
    ScoreMetric("平台适配度", "90", "句长控制适合 TikTok 字幕节奏，停顿位清楚。", "brand"),
    ScoreMetric("情绪感染力", "88", "具有轻生活方式感，能兼顾转化与种草氛围。", "info"),
    ScoreMetric("行动引导力", "91", "CTA 明确，且没有过度压迫式催单表达。", "success"),
    ScoreMetric("合规稳健度", "72", "个别版本存在绝对化用语，需替换后再投放。", "warning"),
)

COMPARISON_POINTS: tuple[ComparisonPoint, ...] = (
    ComparisonPoint("开头吸引力", "直接命中通勤漏水痛点，强吸睛", "氛围柔和，更偏生活方式表达", "冷启动优先用 A，种草期搭配 B。", "success"),
    ComparisonPoint("转化力度", "CTA 更明确，适合短视频或挂车卡", "购买引导较软，适合评论区蓄水", "A 更适合冲成交。", "brand"),
    ComparisonPoint("用户信任感", "专业表达更稳，但稍偏销售视角", "更像真实体验分享，信任感更强", "B 更适合账号内容流。", "info"),
    ComparisonPoint("内容风险", "版本 01 风险最低，可直接投放", "版本 02 同样安全，风险更低", "二者都可投，A 优先。", "success"),
    ComparisonPoint("适用素材", "开箱、对比、演示型素材", "Vlog、桌面拍摄、生活记录素材", "根据素材风格切换。", "warning"),
)

COMPLIANCE_ISSUES: tuple[ComplianceIssue, ...] = (
    ComplianceIssue(
        phrase="最强",
        category="绝对化用语",
        level="高风险",
        explanation="广告表达中不宜使用缺乏客观依据的绝对化词汇，容易触发平台审核与法规风险。",
        alternatives=("表现更稳", "体验更顺手", "性能出色", "更受欢迎"),
    ),
    ComplianceIssue(
        phrase="首批用户都说",
        category="用户反馈泛化",
        level="中风险",
        explanation="若未提供真实样本来源，容易被判定为夸大用户评价，建议改为“部分用户反馈”。",
        alternatives=("部分用户反馈", "体验后评价不错", "不少用户表示"),
    ),
    ComplianceIssue(
        phrase="特别划算",
        category="价格引导措辞",
        level="低风险",
        explanation="可保留，但建议结合具体优惠机制呈现，避免空泛价格暗示。",
        alternatives=("到手门槛更友好", "当前活动价更合适", "组合入手更省心"),
    ),
)

COPY_HISTORY: tuple[HistoryEntry, ...] = (
    HistoryEntry("03-09 09:18", "轻量保温杯", "通勤女性", "专业严谨", "版本 01", "92", "96", "已采纳"),
    HistoryEntry("03-08 21:42", "便携榨汁杯", "健身达人", "亲切随性", "版本 02", "88", "94", "已导出"),
    HistoryEntry("03-08 16:05", "无线卷发棒", "美妆白领", "幽默风趣", "版本 03", "83", "71", "待修改"),
    HistoryEntry("03-07 18:37", "香氛洗衣凝珠", "精致宝妈", "专业严谨", "版本 01", "91", "95", "已投放"),
    HistoryEntry("03-07 11:26", "桌面加湿器", "宿舍学生", "亲切随性", "版本 04", "87", "97", "已归档"),
    HistoryEntry("03-06 20:10", "便携充电宝", "旅行人群", "专业严谨", "版本 02", "89", "93", "已导出"),
    HistoryEntry("03-06 13:55", "磁吸手机支架", "车载用户", "幽默风趣", "版本 01", "85", "92", "已采纳"),
)

TOPIC_SUGGESTIONS: tuple[tuple[str, str], ...] = (
    ("#通勤好物", "适合通勤杯、桌面用品、办公室生活类内容，泛流量稳定。"),
    ("#我的包里有什么", "适合多场景展示和开包类内容，利于自然植入产品。"),
    ("#办公室幸福感", "适合强调情绪价值与使用氛围，评论互动率较高。"),
    ("#女生购物分享", "适合生活方式种草内容，适合高颜值产品。"),
    ("#上班族喝水搭子", "适合通勤杯、便携保温用品，标签与人群匹配度高。"),
)


class CopyGenerationPage(BasePage):
    """AI 文案生成主页面。"""

    default_route_id = RouteId("ai_copy_generation")
    default_display_name = "AI文案生成"
    default_icon_name = "edit_note"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._template_cards: list[QFrame] = []
        self._variant_cards: list[QFrame] = []
        self._history_rows: list[HistoryEntry] = list(COPY_HISTORY)
        self._selected_template = PROMPT_TEMPLATES[0]
        self._active_variant = COPY_VARIANTS[0]
        self.ai_config_panel: AIConfigPanel | None = None
        self._ai_config_summary_label: QLabel | None = None
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建 AI 文案生成页面。"""

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(self, "setObjectName", "copyGenerationPage")
        _call(self, "setStyleSheet", self._page_stylesheet())

        self.layout.addWidget(self._build_warning_banner())
        self.layout.addWidget(self._build_header())
        self.layout.addWidget(self._build_main_body(), 1)
        self._update_ai_config_summary()

    def _build_warning_banner(self) -> QWidget:
        banner = QFrame(self)
        _call(banner, "setObjectName", "copyWarningBanner")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)

        icon = QLabel("⚠", banner)
        _call(icon, "setObjectName", "copyWarningIcon")
        text = QLabel("请在发布前完成合规检查，避免使用绝对化、功效承诺与违规引导表述。", banner)
        _call(text, "setObjectName", "copyWarningText")

        layout.addStretch(1)
        layout.addWidget(icon)
        layout.addWidget(text)
        layout.addStretch(1)
        return banner

    def _build_header(self) -> QWidget:
        header = QFrame(self)
        _call(header, "setObjectName", "copyHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(18)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(12)

        logo = QLabel("✦", header)
        _call(logo, "setObjectName", "copyHeaderLogo")
        title = QLabel("AI文案生成", header)
        _call(title, "setObjectName", "copyHeaderTitle")

        brand_row.addWidget(logo)
        brand_row.addWidget(title)

        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(0, 0, 0, 0)
        nav_row.setSpacing(8)
        for index, item in enumerate(("创作中心", "我的草稿", "合规记录")):
            chip = StatusBadge(item, tone="brand" if index == 0 else "neutral", parent=header)
            nav_row.addWidget(chip)

        status = AIStatusIndicator(header)
        status.set_status("就绪")
        user_chip = StatusBadge("个人中心", tone="neutral", parent=header)

        layout.addLayout(brand_row)
        layout.addStretch(1)
        layout.addLayout(nav_row)
        layout.addStretch(1)
        layout.addWidget(status)
        layout.addWidget(user_chip)
        return header

    def _build_main_body(self) -> QWidget:
        container = PageContainer(parent=self)
        container.content_layout.setSpacing(0)

        outer_split = SplitPanel(split_ratio=(0.25, 0.75), minimum_sizes=(300, 760), parent=container)
        inner_split = SplitPanel(split_ratio=(0.67, 0.33), minimum_sizes=(560, 320), parent=outer_split)

        left_panel = self._build_left_panel()
        center_panel = self._build_center_panel()
        right_panel = self._build_right_panel()

        inner_split.set_widgets(center_panel, right_panel)
        outer_split.set_widgets(left_panel, inner_split)
        container.add_widget(outer_split)
        return container

    def _build_left_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        _call(scroll, "setObjectName", "copyLeftPanel")
        scroll.content_layout.setContentsMargins(0, 0, 12, 0)
        scroll.content_layout.setSpacing(16)

        scroll.add_widget(self._build_parameter_section())
        scroll.add_widget(self._build_prompt_template_section())
        scroll.add_widget(self._build_ai_config_section())
        scroll.add_widget(self._build_left_summary_section())
        scroll.content_layout.addStretch(1)
        return scroll

    def _build_parameter_section(self) -> QWidget:
        section = ContentSection("生成参数设置", icon="⚙", parent=self)

        self.product_name_input = ThemedLineEdit(
            label="产品名称",
            placeholder="例如：轻量防漏奶油风保温杯",
            helper_text="建议填写用户可感知的主标题商品名。",
            parent=None,
        )
        self.product_name_input.setText("轻量防漏奶油风保温杯")

        self.product_desc_input = ThemedTextEdit(
            label="产品信息",
            placeholder="请输入产品核心材质、卖点、使用场景和优惠机制",
            parent=None,
        )
        self.product_desc_input.setPlainText(
            "双层不锈钢内胆，约 380ml 容量，单手开盖，密封防漏；适合通勤、办公室、健身与短途出行。"
            "主推雾感奶油色、轻量杯身、好清洗、适合送礼。当前活动送杯刷 + 吸管盖。"
        )

        self.audience_input = TagInput(label="目标人群", placeholder="输入人群特征后按回车", parent=None)
        self.audience_input.set_tags(["25-35 岁通勤女性", "办公室白领", "高颜值杯具偏好", "礼赠需求人群"])

        self.tone_combo = ThemedComboBox(label="写作风格", items=["专业严谨", "亲切随性", "幽默风趣", "高端质感"], parent=None)
        _call(self.tone_combo.combo_box, "setCurrentText", "专业严谨")

        self.platform_combo = ThemedComboBox(label="投放平台", items=["TikTok Shop", "TikTok 短视频", "短视频卖货", "商品详情页"], parent=None)
        _call(self.platform_combo.combo_box, "setCurrentText", "TikTok Shop")

        self.length_combo = ThemedComboBox(label="文案长度", items=["短文案（80-120 字）", "中等（180-260 字）", "长文案（300-450 字）"], parent=None)
        _call(self.length_combo.combo_box, "setCurrentText", "中等（180-260 字）")

        self.selling_points_input = TagInput(label="核心卖点", placeholder="如：防漏 / 高颜值 / 轻量", parent=None)
        self.selling_points_input.set_tags(["单手开盖", "轻量通勤", "雾感奶油色", "密封防漏", "活动赠品"])

        generate_row = QWidget(section)
        row_layout = QHBoxLayout(generate_row)
        row_layout.setContentsMargins(0, 4, 0, 0)
        row_layout.setSpacing(10)

        self.generate_button = PrimaryButton("立即生成文案", generate_row, icon_text="✦")
        self.reset_button = SecondaryButton("重置参数", generate_row, icon_text="↺")
        _connect(self.generate_button.clicked, self._simulate_generation)
        _connect(self.reset_button.clicked, self._reset_to_demo_state)

        row_layout.addWidget(self.generate_button, 1)
        row_layout.addWidget(self.reset_button)

        for widget in (
            self.product_name_input,
            self.product_desc_input,
            self.audience_input,
            self.tone_combo,
            self.platform_combo,
            self.length_combo,
            self.selling_points_input,
            generate_row,
        ):
            section.add_widget(widget)

        return section

    def _build_prompt_template_section(self) -> QWidget:
        section = ContentSection("Prompt 模板选择", icon="🧩", parent=self)
        search_group = FormGroup("模板检索", description="快速筛选短视频、促销等创作模板。", parent=None)
        self.template_search = SearchBar("搜索模板名称、目标或人群...", None)
        search_group.set_field_widget(self.template_search)
        _connect(self.template_search.search_changed, self._filter_template_cards)

        self.template_summary = QLabel(
            "当前模板：短视频爆款冲榜 · 适合短视频字幕、冷启动拉新、突出痛点卖点。",
            section,
        )
        _call(self.template_summary, "setObjectName", "copyTemplateSummary")
        _call(self.template_summary, "setWordWrap", True)

        self.prompt_preview = StreamingOutputWidget(section)
        _call(self.prompt_preview, "setObjectName", "copyPromptPreview")
        self.prompt_preview.clear()
        self.prompt_preview.append_chunk(self._selected_template.prompt)
        self.prompt_preview.set_token_usage(186, 512)

        cards_host = QWidget(section)
        cards_layout = QVBoxLayout(cards_host)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(10)
        self._template_cards.clear()

        for template in PROMPT_TEMPLATES:
            card = self._build_template_card(template)
            self._template_cards.append(card)
            cards_layout.addWidget(card)

        section.add_widget(search_group)
        section.add_widget(self.template_summary)
        section.add_widget(cards_host)
        section.add_widget(self.prompt_preview)
        return section

    def _build_template_card(self, template: PromptTemplateMeta) -> QFrame:
        card = QFrame(self)
        _call(card, "setObjectName", "copyTemplateCard")
        _call(card, "setProperty", "templateName", template.name)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel(template.name, card)
        _call(title, "setObjectName", "copyTemplateCardTitle")
        badge = StatusBadge(template.category, tone="brand" if template is self._selected_template else "neutral", parent=card)
        use_button = SecondaryButton("应用模板", card, icon_text="＋")
        _connect(use_button.clicked, lambda _checked=False, item=template: self._apply_template(item))

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(badge)
        header.addWidget(use_button)

        summary = QLabel(template.summary, card)
        _call(summary, "setWordWrap", True)
        _call(summary, "setObjectName", "copyTemplateCardBody")

        meta = QLabel(f"适用人群：{template.audience} · 目标：{template.goal}", card)
        _call(meta, "setObjectName", "copyTemplateCardMeta")
        _call(meta, "setWordWrap", True)

        tags_row = QWidget(card)
        tags_layout = QHBoxLayout(tags_row)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(6)
        for tag in template.tags:
            tags_layout.addWidget(TagChip(tag, tone="brand" if template is self._selected_template else "neutral", parent=tags_row))
        tags_layout.addStretch(1)

        layout.addLayout(header)
        layout.addWidget(summary)
        layout.addWidget(meta)
        layout.addWidget(tags_row)
        return card

    def _build_ai_config_section(self) -> QWidget:
        section = ContentSection("AI 模型配置", icon="🤖", parent=self)
        self.ai_config_panel = AIConfigPanel(section)
        self.ai_config_panel.set_config(
            {
                "provider": "openai",
                "model": "gpt-4o",
                "agent_role": "文案专家",
                "temperature": 0.8,
                "max_tokens": 2400,
                "top_p": 0.9,
            }
        )

        summary_card = QFrame(section)
        _call(summary_card, "setObjectName", "copyAiConfigSummary")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(6)
        summary_title = QLabel("当前模型摘要", summary_card)
        _call(summary_title, "setObjectName", "copyAiConfigSummaryTitle")
        self._ai_config_summary_label = QLabel("等待同步 AI 配置…", summary_card)
        _call(self._ai_config_summary_label, "setObjectName", "copyAiConfigSummaryText")
        _call(self._ai_config_summary_label, "setWordWrap", True)

        self.ai_config_note = InfoCard(
            title="当前建议",
            description="当前配置偏向高质量生成，适合首版创作；如需批量生产，可切到 gpt-4o-mini 并将温度降至 0.6。",
            icon="◎",
            action_text="复制配置建议",
            parent=section,
        )
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self._ai_config_summary_label)
        _connect(self.ai_config_panel.config_changed, self._on_ai_config_changed)
        section.add_widget(self.ai_config_panel)
        section.add_widget(summary_card)
        section.add_widget(self.ai_config_note)
        return section

    def _on_ai_config_changed(self, _config: dict[str, object]) -> None:
        self._update_ai_config_summary()

    def _update_ai_config_summary(self) -> None:
        if self.ai_config_panel is None or self._ai_config_summary_label is None:
            return
        config = self.ai_config_panel.config()
        self._ai_config_summary_label.setText(
            f"{config['provider_label']} · {config['model']} · {config['agent_role']} · 温度 {config['temperature']}"
            f" · Top-p {config['top_p']} · 输出上限 {config['max_tokens']} Token。"
            "当前配置偏向高质量首稿，适合先做主版本，再衍生评论区和详情页文案。"
        )

    def _build_left_summary_section(self) -> QWidget:
        section = ContentSection("创作输入摘要", icon="📝", parent=self)

        badge_row = QWidget(section)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(8)
        badge_layout.addWidget(StatsBadge(label="模板", value="4 个", icon="◈", tone="brand", parent=badge_row))
        badge_layout.addWidget(StatsBadge(label="卖点", value="5 项", icon="◎", tone="success", parent=badge_row))
        badge_layout.addWidget(StatsBadge(label="人群", value="4 类", icon="◌", tone="info", parent=badge_row))
        badge_layout.addStretch(1)

        summary = QLabel(
            "当前输入聚焦“通勤女性 + 高颜值防漏杯 + 中等长度 + TikTok Shop 转化场景”，"
            "适合先生成 4 个版本后做 A/B 对比，再挑选低风险版本投放。",
            section,
        )
        _call(summary, "setWordWrap", True)
        _call(summary, "setObjectName", "copyAsideSummary")

        section.add_widget(badge_row)
        section.add_widget(summary)
        return section

    def _build_center_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        _call(scroll, "setObjectName", "copyCenterPanel")
        scroll.content_layout.setContentsMargins(0, 0, 12, 0)
        scroll.content_layout.setSpacing(16)

        scroll.add_widget(self._build_center_intro())
        scroll.add_widget(self._build_result_tabs())
        scroll.add_widget(self._build_quality_score_section())
        scroll.add_widget(self._build_variant_comparison_section())
        scroll.add_widget(self._build_history_section())
        scroll.content_layout.addStretch(1)
        return scroll

    def _build_center_intro(self) -> QWidget:
        shell = QFrame(self)
        _call(shell, "setObjectName", "copyCenterHero")
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)
        title = QLabel("创作输出中心", shell)
        _call(title, "setObjectName", "copyCenterHeroTitle")
        hint = StatusBadge("已生成 4 个版本", tone="brand", parent=shell)
        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(hint)

        summary = QLabel(
            "系统已按“通勤女性 + 防漏保温杯 + 专业严谨”生成多版本文案，并同步完成质量评分、风险提示和投放建议。",
            shell,
        )
        _call(summary, "setObjectName", "copyCenterHeroBody")
        _call(summary, "setWordWrap", True)

        stats_row = QWidget(shell)
        stats_layout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        stats_layout.addWidget(KPICard(title="最佳质量分", value="92", trend="up", percentage="+6.2%", caption="较上次生成", parent=stats_row))
        stats_layout.addWidget(KPICard(title="平均合规分", value="90", trend="flat", percentage="稳定", caption="建议直接投放 3 版", parent=stats_row))
        stats_layout.addWidget(KPICard(title="预测 CTR", value="4.8%", trend="up", percentage="+0.7%", caption="版本 01 最优", parent=stats_row))

        action_row = QWidget(shell)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        self.copy_all_button = PrimaryButton("复制最佳版本", action_row, icon_text="⎘")
        self.export_button = SecondaryButton("导出文案包", action_row, icon_text="⇩")
        self.regenerate_button = SecondaryButton("重新生成", action_row, icon_text="✦")
        _connect(self.regenerate_button.clicked, self._simulate_generation)
        _connect(self.copy_all_button.clicked, self._copy_best_variant_to_stream)

        action_layout.addWidget(self.copy_all_button)
        action_layout.addWidget(self.export_button)
        action_layout.addWidget(self.regenerate_button)
        action_layout.addStretch(1)

        layout.addLayout(title_row)
        layout.addWidget(summary)
        layout.addWidget(stats_row)
        layout.addWidget(action_row)
        return shell

    def _build_result_tabs(self) -> QWidget:
        shell = QFrame(self)
        _call(shell, "setObjectName", "copyResultTabsShell")
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.result_tabs = TabBar(shell)
        self.result_tabs.add_tab("标题推荐", self._build_variant_tab())
        self.result_tabs.add_tab("文案脚本", self._build_script_tab())
        self.result_tabs.add_tab("热门话题", self._build_topic_tab())

        layout.addWidget(self.result_tabs)
        return shell

    def _build_variant_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        cards_host = QWidget(host)
        cards_layout = QVBoxLayout(cards_host)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(12)
        self._variant_cards.clear()
        for variant in COPY_VARIANTS:
            card = self._build_variant_card(variant)
            self._variant_cards.append(card)
            cards_layout.addWidget(card)

        empty_state = QFrame(host)
        _call(empty_state, "setObjectName", "copyInspirationState")
        empty_layout = QVBoxLayout(empty_state)
        empty_layout.setContentsMargins(20, 28, 20, 28)
        empty_layout.setSpacing(10)

        icon = QLabel("✧", empty_state)
        _call(icon, "setObjectName", "copyInspirationIcon")
        message = QLabel("点击“立即生成文案”可继续扩展更多创意版本与场景化表达。", empty_state)
        _call(message, "setObjectName", "copyInspirationText")
        _call(message, "setWordWrap", True)

        empty_layout.addWidget(icon, 0)
        empty_layout.addWidget(message, 0)

        layout.addWidget(cards_host)
        layout.addWidget(empty_state)
        return host

    def _build_variant_card(self, variant: CopyVariant) -> QFrame:
        card = QFrame(self)
        _call(card, "setObjectName", "copyVariantCard")
        if variant.warning_note:
            _call(card, "setProperty", "risk", "warning")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        code = StatusBadge(variant.code, tone="brand" if variant is COPY_VARIANTS[0] else "neutral", parent=card)
        subtitle = StatusBadge(variant.subtitle, tone="warning" if variant.warning_note else "success", parent=card)
        copy_button = IconButton(icon_text="⎘", tooltip="复制此版本", parent=card)
        _connect(copy_button.clicked, lambda item=variant: self._set_stream_output(item.copy_text, item.quality_score, item.compliance_score))

        top_row.addWidget(code)
        top_row.addWidget(subtitle)
        top_row.addStretch(1)
        top_row.addWidget(copy_button)

        title = QLabel(variant.title, card)
        _call(title, "setObjectName", "copyVariantTitle")

        body = QLabel(variant.copy_text, card)
        _call(body, "setObjectName", "copyVariantBody")
        _call(body, "setWordWrap", True)

        info_row = QWidget(card)
        info_layout = QHBoxLayout(info_row)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        info_layout.addWidget(StatsBadge("质量分", variant.quality_score, icon="◎", tone="success", parent=info_row))
        info_layout.addWidget(StatsBadge("合规分", variant.compliance_score, icon="◌", tone="warning" if variant.warning_note else "brand", parent=info_row))
        info_layout.addWidget(StatsBadge("预测 CTR", variant.estimated_ctr, icon="↗", tone="info", parent=info_row))
        info_layout.addStretch(1)

        meta = QLabel(f"适用场景：{variant.scene} · 转化目标：{variant.conversion_goal} · 风格：{variant.tone}", card)
        _call(meta, "setObjectName", "copyVariantMeta")
        _call(meta, "setWordWrap", True)

        tags = QWidget(card)
        tags_layout = QHBoxLayout(tags)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(6)
        for tag in variant.tags:
            tags_layout.addWidget(TagChip(tag, tone="brand" if tag in {"高点击", "优先推荐"} else "neutral", parent=tags))
        tags_layout.addStretch(1)

        layout.addLayout(top_row)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addWidget(info_row)
        layout.addWidget(meta)
        layout.addWidget(tags)

        if variant.warning_note:
            warning_box = QFrame(card)
            _call(warning_box, "setObjectName", "copyVariantWarningBox")
            warning_layout = QVBoxLayout(warning_box)
            warning_layout.setContentsMargins(12, 12, 12, 12)
            warning_layout.setSpacing(8)

            warning_text = QLabel(variant.warning_note, warning_box)
            _call(warning_text, "setWordWrap", True)
            _call(warning_text, "setObjectName", "copyVariantWarningText")

            replace_row = QWidget(warning_box)
            replace_layout = QHBoxLayout(replace_row)
            replace_layout.setContentsMargins(0, 0, 0, 0)
            replace_layout.setSpacing(6)
            for word in variant.suggested_words:
                replace_layout.addWidget(TagChip(word, tone="warning", parent=replace_row))
            replace_layout.addStretch(1)

            warning_layout.addWidget(warning_text)
            warning_layout.addWidget(replace_row)
            layout.addWidget(warning_box)

        return card

    def _build_script_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.streaming_output = StreamingOutputWidget(host)
        self.streaming_output.clear()
        self.streaming_output.append_chunk(
            "【开场 3 秒】\n"
            "如果你每天上班都怕咖啡漏包里，那这只通勤杯真的很值得你看完。\n\n"
            "【中段卖点】\n"
            "它是轻量杯身，女生单手拿完全没压力；杯盖密封防漏，通勤包、电脑包都能放心放；"
            "而且雾感奶油色真的很出片，桌面拍摄和开箱视频都很加分。\n\n"
            "【收尾 CTA】\n"
            "现在活动期下单还送杯刷和吸管盖，想把日常喝水这件事变得更轻松一点，可以先点开看看。"
        )
        self.streaming_output.set_token_usage(268, 736)

        script_note = InfoCard(
            title="脚本建议",
            description="推荐将版本 01 作为短视频口播底稿，版本 02 用于评论区置顶文案或视频配文。",
            icon="▶",
            action_text="同步到投放清单",
            parent=host,
        )

        layout.addWidget(self.streaming_output)
        layout.addWidget(script_note)
        return host

    def _build_topic_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        intro = QLabel("结合当前商品人群与素材风格，推荐以下 TikTok 热门话题组合：", host)
        _call(intro, "setObjectName", "copyTopicIntro")
        _call(intro, "setWordWrap", True)
        layout.addWidget(intro)

        for tag, detail in TOPIC_SUGGESTIONS:
            card = QFrame(host)
            _call(card, "setObjectName", "copyTopicCard")
            row = QVBoxLayout(card)
            row.setContentsMargins(14, 14, 14, 14)
            row.setSpacing(6)
            chip = TagChip(tag, tone="brand", parent=card)
            text = QLabel(detail, card)
            _call(text, "setWordWrap", True)
            _call(text, "setObjectName", "copyTopicBody")
            row.addWidget(chip)
            row.addWidget(text)
            layout.addWidget(card)

        layout.addStretch(1)
        return host

    def _build_quality_score_section(self) -> QWidget:
        section = ContentSection("文案质量评分", icon="📊", parent=self)

        header_row = QWidget(section)
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        header_layout.addWidget(StatusBadge("综合得分 91", tone="success", parent=header_row))
        header_layout.addWidget(StatusBadge("推荐直接投放版本 01 / 02 / 04", tone="brand", parent=header_row))
        header_layout.addStretch(1)

        metric_cards = QWidget(section)
        metric_layout = QHBoxLayout(metric_cards)
        metric_layout.setContentsMargins(0, 0, 0, 0)
        metric_layout.setSpacing(10)
        metric_layout.addWidget(KPICard(title="清晰度", value="94", trend="up", percentage="优秀", caption="卖点表达充足", parent=metric_cards))
        metric_layout.addWidget(KPICard(title="感染力", value="88", trend="up", percentage="良好", caption="情绪价值到位", parent=metric_cards))
        metric_layout.addWidget(KPICard(title="合规稳定性", value="90", trend="flat", percentage="可控", caption="仅 1 版需修订", parent=metric_cards))

        breakdown_host = QWidget(section)
        breakdown_layout = QVBoxLayout(breakdown_host)
        breakdown_layout.setContentsMargins(0, 0, 0, 0)
        breakdown_layout.setSpacing(10)
        for metric in QUALITY_BREAKDOWN:
            breakdown_layout.addWidget(self._build_score_metric_card(metric))

        section.add_widget(header_row)
        section.add_widget(metric_cards)
        section.add_widget(breakdown_host)
        return section

    def _build_score_metric_card(self, metric: ScoreMetric) -> QWidget:
        card = QFrame(self)
        _call(card, "setObjectName", "copyScoreMetricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)
        label = QLabel(metric.label, card)
        _call(label, "setObjectName", "copyScoreMetricTitle")
        badge = StatusBadge(metric.score, tone=_badge_tone(metric.tone), parent=card)
        top_row.addWidget(label)
        top_row.addStretch(1)
        top_row.addWidget(badge)

        detail = QLabel(metric.detail, card)
        _call(detail, "setObjectName", "copyScoreMetricBody")
        _call(detail, "setWordWrap", True)

        layout.addLayout(top_row)
        layout.addWidget(detail)
        return card

    def _build_variant_comparison_section(self) -> QWidget:
        section = ContentSection("A/B 版本对比", icon="⚖", parent=self)

        compare_intro = QLabel(
            "系统建议将版本 01 作为成交主版本，版本 02 作为种草承接版本，先用不同素材与封面各跑一轮。",
            section,
        )
        _call(compare_intro, "setWordWrap", True)
        _call(compare_intro, "setObjectName", "copyComparisonIntro")

        showcase = QWidget(section)
        showcase_layout = QHBoxLayout(showcase)
        showcase_layout.setContentsMargins(0, 0, 0, 0)
        showcase_layout.setSpacing(10)
        showcase_layout.addWidget(self._build_comparison_variant_panel("A 版本", COPY_VARIANTS[0], "成交优先", "success"))
        showcase_layout.addWidget(self._build_comparison_variant_panel("B 版本", COPY_VARIANTS[1], "种草优先", "info"))

        points_host = QWidget(section)
        points_layout = QVBoxLayout(points_host)
        points_layout.setContentsMargins(0, 0, 0, 0)
        points_layout.setSpacing(10)
        for point in COMPARISON_POINTS:
            points_layout.addWidget(self._build_comparison_point_card(point))

        action_row = QWidget(section)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)
        action_layout.addWidget(PrimaryButton("选择 A 作为主版本", action_row, icon_text="A"))
        action_layout.addWidget(SecondaryButton("复制 B 做评论区配文", action_row, icon_text="B"))
        action_layout.addStretch(1)

        section.add_widget(compare_intro)
        section.add_widget(showcase)
        section.add_widget(points_host)
        section.add_widget(action_row)
        return section

    def _build_comparison_variant_panel(self, title: str, variant: CopyVariant, label_text: str, tone: str) -> QWidget:
        card = QFrame(self)
        _call(card, "setObjectName", "copyComparisonVariantCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)
        panel_title = QLabel(title, card)
        _call(panel_title, "setObjectName", "copyComparisonVariantTitle")
        badge = StatusBadge(label_text, tone=_badge_tone(tone), parent=card)
        top_row.addWidget(panel_title)
        top_row.addStretch(1)
        top_row.addWidget(badge)

        copy = QLabel(variant.copy_text, card)
        _call(copy, "setWordWrap", True)
        _call(copy, "setObjectName", "copyComparisonVariantBody")

        metric_row = QWidget(card)
        metric_layout = QHBoxLayout(metric_row)
        metric_layout.setContentsMargins(0, 0, 0, 0)
        metric_layout.setSpacing(8)
        metric_layout.addWidget(StatsBadge("质量", variant.quality_score, icon="◎", tone="success", parent=metric_row))
        metric_layout.addWidget(StatsBadge("合规", variant.compliance_score, icon="◌", tone="brand", parent=metric_row))
        metric_layout.addWidget(StatsBadge("CTR", variant.estimated_ctr, icon="↗", tone="info", parent=metric_row))
        metric_layout.addStretch(1)

        layout.addLayout(top_row)
        layout.addWidget(copy)
        layout.addWidget(metric_row)
        return card

    def _build_comparison_point_card(self, point: ComparisonPoint) -> QWidget:
        card = QFrame(self)
        _call(card, "setObjectName", "copyComparisonPointCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)
        title = QLabel(point.dimension, card)
        _call(title, "setObjectName", "copyComparisonPointTitle")
        badge = StatusBadge(point.recommendation, tone=_badge_tone(point.tone), parent=card)
        top_row.addWidget(title)
        top_row.addStretch(1)
        top_row.addWidget(badge)

        a_label = QLabel(f"A：{point.variant_a}", card)
        b_label = QLabel(f"B：{point.variant_b}", card)
        for widget in (a_label, b_label):
            _call(widget, "setWordWrap", True)
            _call(widget, "setObjectName", "copyComparisonPointBody")

        layout.addLayout(top_row)
        layout.addWidget(a_label)
        layout.addWidget(b_label)
        return card

    def _build_history_section(self) -> QWidget:
        section = ContentSection("文案历史记录", icon="🕘", parent=self)
        header_row = QWidget(section)
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        header_layout.addWidget(StatusBadge("近 7 天共生成 28 次", tone="brand", parent=header_row))
        header_layout.addWidget(StatusBadge("已采纳 9 条", tone="success", parent=header_row))
        header_layout.addWidget(StatusBadge("待修订 2 条", tone="warning", parent=header_row))
        header_layout.addStretch(1)

        self.history_table = DataTable(
            headers=["时间", "商品", "人群", "风格", "最佳版本", "质量分", "合规分", "状态"],
            rows=[
                [
                    item.created_at,
                    item.product_name,
                    item.audience,
                    item.style,
                    item.best_variant,
                    item.quality_score,
                    item.compliance_score,
                    item.status,
                ]
                for item in self._history_rows
            ],
            page_size=6,
            empty_text="暂无文案历史记录",
            parent=section,
        )

        section.add_widget(header_row)
        section.add_widget(self.history_table)
        return section

    def _build_right_panel(self) -> QWidget:
        scroll = ThemedScrollArea(self)
        _call(scroll, "setObjectName", "copyRightPanel")
        scroll.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.content_layout.setSpacing(16)

        scroll.add_widget(self._build_compliance_summary_section())
        scroll.add_widget(self._build_compliance_checker_section())
        scroll.add_widget(self._build_rewrite_suggestion_section())
        scroll.add_widget(self._build_report_action_section())
        scroll.content_layout.addStretch(1)
        return scroll

    def _build_compliance_summary_section(self) -> QWidget:
        shell = QFrame(self)
        _call(shell, "setObjectName", "copyComplianceSummary")
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("合规自检报告", shell)
        _call(title, "setObjectName", "copyComplianceTitle")

        score_ring = QFrame(shell)
        _call(score_ring, "setObjectName", "copyRiskRing")
        ring_layout = QVBoxLayout(score_ring)
        ring_layout.setContentsMargins(0, 20, 0, 20)
        ring_layout.setSpacing(4)
        score_value = QLabel("72", score_ring)
        _call(score_value, "setObjectName", "copyRiskRingScore")
        score_label = QLabel("中等风险", score_ring)
        _call(score_label, "setObjectName", "copyRiskRingLabel")
        ring_layout.addWidget(score_value, 0)
        ring_layout.addWidget(score_label, 0)

        metrics = QWidget(shell)
        metrics_layout = QHBoxLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)
        metrics_layout.addWidget(KPICard(title="违规词", value="1", trend="down", percentage="需替换", caption="版本 03", parent=metrics))
        metrics_layout.addWidget(KPICard(title="敏感表达", value="2", trend="flat", percentage="已标记", caption="建议人工复核", parent=metrics))

        layout.addWidget(title)
        layout.addWidget(score_ring)
        layout.addWidget(metrics)
        return shell

    def _build_compliance_checker_section(self) -> QWidget:
        section = ContentSection("风险词检出", icon="🛡", parent=self)

        intro = QLabel(
            "已针对 4 个版本完成广告法与平台表达检查，以下为高优先级风险项。",
            section,
        )
        _call(intro, "setWordWrap", True)
        _call(intro, "setObjectName", "copyComplianceIntro")
        section.add_widget(intro)

        for issue in COMPLIANCE_ISSUES:
            section.add_widget(self._build_issue_card(issue))
        return section

    def _build_issue_card(self, issue: ComplianceIssue) -> QWidget:
        card = QFrame(self)
        _call(card, "setObjectName", "copyIssueCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)
        keyword = TagChip(issue.phrase, tone="error" if issue.level == "高风险" else "warning", parent=card)
        category = StatusBadge(issue.category, tone="warning", parent=card)
        level = StatusBadge(issue.level, tone="error" if issue.level == "高风险" else "warning", parent=card)

        top_row.addWidget(keyword)
        top_row.addWidget(category)
        top_row.addStretch(1)
        top_row.addWidget(level)

        explanation = QLabel(issue.explanation, card)
        _call(explanation, "setWordWrap", True)
        _call(explanation, "setObjectName", "copyIssueBody")

        replacement_row = QWidget(card)
        replacement_layout = QHBoxLayout(replacement_row)
        replacement_layout.setContentsMargins(0, 0, 0, 0)
        replacement_layout.setSpacing(6)
        for alternative in issue.alternatives:
            replacement_layout.addWidget(TagChip(alternative, tone="neutral", parent=replacement_row))
        replacement_layout.addStretch(1)

        layout.addLayout(top_row)
        layout.addWidget(explanation)
        layout.addWidget(replacement_row)
        return card

    def _build_rewrite_suggestion_section(self) -> QWidget:
        section = ContentSection("修改建议与推荐替换", icon="✎", parent=self)

        primary_suggestion = QFrame(section)
        _call(primary_suggestion, "setObjectName", "copySuggestionHero")
        suggestion_layout = QVBoxLayout(primary_suggestion)
        suggestion_layout.setContentsMargins(14, 14, 14, 14)
        suggestion_layout.setSpacing(8)

        heading = QLabel("建议优先修订版本 03", primary_suggestion)
        _call(heading, "setObjectName", "copySuggestionTitle")

        body = QLabel(
            "将“最强”替换为“表现更稳 / 性能出色 / 更受欢迎”等客观表达，同时把“首批用户都说”改为“部分用户反馈”。"
            "修订后预计合规分可从 72 提升至 91。",
            primary_suggestion,
        )
        _call(body, "setWordWrap", True)
        _call(body, "setObjectName", "copySuggestionBody")

        chips = QWidget(primary_suggestion)
        chips_layout = QHBoxLayout(chips)
        chips_layout.setContentsMargins(0, 0, 0, 0)
        chips_layout.setSpacing(6)
        for word in ("表现更稳", "部分用户反馈", "当前活动价更合适", "适合先加入购物车"):
            chips_layout.addWidget(TagChip(word, tone="brand", parent=chips))
        chips_layout.addStretch(1)

        suggestion_layout.addWidget(heading)
        suggestion_layout.addWidget(body)
        suggestion_layout.addWidget(chips)

        legal_note = InfoCard(
            title="补充提示",
            description="在 TikTok 电商投放中，建议尽量使用“更适合 / 更方便 / 更受欢迎”此类相对客观表达，避免极限承诺。",
            icon="ℹ",
            action_text="查看审核规范",
            parent=section,
        )

        section.add_widget(primary_suggestion)
        section.add_widget(legal_note)
        return section

    def _build_report_action_section(self) -> QWidget:
        shell = QFrame(self)
        _call(shell, "setObjectName", "copyReportFooter")
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        export_report = SecondaryButton("导出合规报告", shell, icon_text="⇩")
        apply_safe = PrimaryButton("应用安全替换建议", shell, icon_text="✓")
        layout.addWidget(apply_safe)
        layout.addWidget(export_report)
        return shell

    def _apply_template(self, template: PromptTemplateMeta) -> None:
        self._selected_template = template
        self.template_summary.setText(
            f"当前模板：{template.name} · 面向 {template.audience} · 目标为 {template.goal}。"
        )
        self.prompt_preview.clear()
        self.prompt_preview.append_chunk(template.prompt)
        self.prompt_preview.set_token_usage(196 + len(template.tags) * 8, 520)
        self._refresh_template_card_styles()

    def _refresh_template_card_styles(self) -> None:
        for card, template in zip(self._template_cards, PROMPT_TEMPLATES):
            is_active = template == self._selected_template
            border = ACCENT if is_active else BORDER
            background = ACCENT_SOFT if is_active else SURFACE
            _call(
                card,
                "setStyleSheet",
                (
                    f"QFrame#copyTemplateCard {{"
                    f"background-color: {background};"
                    f"border: 1px solid {border};"
                    "border-radius: 14px;"
                    "}"
                    f"QLabel#copyTemplateCardTitle {{ color: {TEXT}; font-size: 14px; font-weight: 700; }}"
                    f"QLabel#copyTemplateCardBody {{ color: {TEXT_MUTED}; font-size: 12px; line-height: 1.6; }}"
                    f"QLabel#copyTemplateCardMeta {{ color: {TEXT_FAINT}; font-size: 11px; }}"
                ),
            )

    def _filter_template_cards(self, keyword: str) -> None:
        text = keyword.strip().lower()
        for card, template in zip(self._template_cards, PROMPT_TEMPLATES):
            haystack = f"{template.name} {template.category} {template.audience} {template.goal} {' '.join(template.tags)}".lower()
            _call(card, "setVisible", not text or text in haystack)

    def _simulate_generation(self) -> None:
        product_name = self.product_name_input.text() or "轻量防漏奶油风保温杯"
        style = self.tone_combo.current_text() or "专业严谨"
        audience = "、".join(self.audience_input.tags()[:2]) or "通勤女性"

        self._active_variant = COPY_VARIANTS[0]
        self._set_stream_output(
            f"已根据【{product_name}】生成 4 个文案版本。\n"
            f"推荐风格：{style}；核心受众：{audience}。\n\n"
            f"优先版本：{COPY_VARIANTS[0].code}\n"
            f"{COPY_VARIANTS[0].copy_text}",
            COPY_VARIANTS[0].quality_score,
            COPY_VARIANTS[0].compliance_score,
        )

        self._history_rows.insert(
            0,
            HistoryEntry(
                created_at="03-09 10:28",
                product_name=product_name,
                audience=audience,
                style=style,
                best_variant=COPY_VARIANTS[0].code,
                quality_score=COPY_VARIANTS[0].quality_score,
                compliance_score=COPY_VARIANTS[0].compliance_score,
                status="刚生成",
            ),
        )
        self._refresh_history_table()

    def _copy_best_variant_to_stream(self) -> None:
        self._set_stream_output(
            COPY_VARIANTS[0].copy_text,
            COPY_VARIANTS[0].quality_score,
            COPY_VARIANTS[0].compliance_score,
        )

    def _set_stream_output(self, text: str, quality_score: str, compliance_score: str) -> None:
        if not hasattr(self, "streaming_output"):
            return
        self.streaming_output.clear()
        self.streaming_output.append_chunk(text)
        prompt_tokens = 180 + _words_count(text) // 2
        completion_tokens = 420 + int(quality_score) + int(compliance_score)
        self.streaming_output.set_token_usage(prompt_tokens, completion_tokens)

    def _reset_to_demo_state(self) -> None:
        self.product_name_input.setText("轻量防漏奶油风保温杯")
        self.product_desc_input.setPlainText(
            "双层不锈钢内胆，约 380ml 容量，单手开盖，密封防漏；适合通勤、办公室、健身与短途出行。"
            "主推雾感奶油色、轻量杯身、好清洗、适合送礼。当前活动送杯刷 + 吸管盖。"
        )
        self.audience_input.set_tags(["25-35 岁通勤女性", "办公室白领", "高颜值杯具偏好", "礼赠需求人群"])
        self.selling_points_input.set_tags(["单手开盖", "轻量通勤", "雾感奶油色", "密封防漏", "活动赠品"])
        _call(self.tone_combo.combo_box, "setCurrentText", "专业严谨")
        _call(self.platform_combo.combo_box, "setCurrentText", "TikTok Shop")
        _call(self.length_combo.combo_box, "setCurrentText", "中等（180-260 字）")
        self._apply_template(PROMPT_TEMPLATES[0])
        self._copy_best_variant_to_stream()

    def _refresh_history_table(self) -> None:
        if not hasattr(self, "history_table"):
            return
        self.history_table.set_rows(
            [
                [
                    item.created_at,
                    item.product_name,
                    item.audience,
                    item.style,
                    item.best_variant,
                    item.quality_score,
                    item.compliance_score,
                    item.status,
                ]
                for item in self._history_rows[:18]
            ]
        )

    def on_activated(self) -> None:
        self._refresh_template_card_styles()
        self._copy_best_variant_to_stream()

    def _page_stylesheet(self) -> str:
        return f"""
        QWidget#copyGenerationPage {{
            background-color: {SURFACE_ALT};
        }}
        QFrame#copyWarningBanner {{
            background-color: rgba(245, 158, 11, 0.10);
            border-bottom: 1px solid rgba(245, 158, 11, 0.22);
        }}
        QLabel#copyWarningIcon {{
            color: {WARNING};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#copyWarningText {{
            color: #9A6700;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }}
        QFrame#copyHeader {{
            background-color: {SURFACE};
            border-bottom: 1px solid {BORDER};
        }}
        QLabel#copyHeaderLogo {{
            min-width: 34px;
            max-width: 34px;
            min-height: 34px;
            max-height: 34px;
            border-radius: 10px;
            background-color: {ACCENT};
            color: {DARK_SURFACE};
            font-size: 18px;
            font-weight: 800;
        }}
        QLabel#copyHeaderTitle {{
            color: {TEXT};
            font-size: 22px;
            font-weight: 800;
            background: transparent;
        }}
        QWidget#copyLeftPanel,
        QWidget#copyCenterPanel,
        QWidget#copyRightPanel {{
            background: transparent;
        }}
        QLabel#copyTemplateSummary {{
            color: {TEXT_MUTED};
            font-size: 12px;
            line-height: 1.6;
            background: transparent;
        }}
        QWidget#copyPromptPreview QWidget#streamingOutput {{
            border-radius: 14px;
        }}
        QLabel#copyAsideSummary {{
            color: {TEXT_MUTED};
            font-size: 12px;
            line-height: 1.7;
            background: transparent;
        }}
        QFrame#copyCenterHero {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 18px;
        }}
        QLabel#copyCenterHeroTitle {{
            color: {TEXT};
            font-size: 18px;
            font-weight: 800;
            background: transparent;
        }}
        QLabel#copyCenterHeroBody {{
            color: {TEXT_MUTED};
            font-size: 13px;
            line-height: 1.7;
            background: transparent;
        }}
        QFrame#copyResultTabsShell {{
            background: transparent;
            border: none;
        }}
        QFrame#copyVariantCard {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 18px;
        }}
        QFrame#copyVariantCard[risk="warning"] {{
            border: 1px solid rgba(245, 158, 11, 0.45);
            border-left: 4px solid {WARNING};
        }}
        QLabel#copyVariantTitle {{
            color: {TEXT};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#copyVariantBody {{
            color: {TEXT};
            font-size: 14px;
            line-height: 1.85;
            background: transparent;
        }}
        QLabel#copyVariantMeta {{
            color: {TEXT_FAINT};
            font-size: 11px;
            background: transparent;
        }}
        QFrame#copyVariantWarningBox {{
            background-color: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 12px;
        }}
        QLabel#copyVariantWarningText {{
            color: #9A6700;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
        }}
        QFrame#copyInspirationState {{
            background-color: rgba(255,255,255,0.56);
            border: 2px dashed {BORDER_STRONG};
            border-radius: 18px;
        }}
        QLabel#copyInspirationIcon {{
            color: {ACCENT};
            font-size: 28px;
            font-weight: 800;
            background: transparent;
        }}
        QLabel#copyInspirationText {{
            color: {TEXT_MUTED};
            font-size: 13px;
            font-weight: 600;
            background: transparent;
        }}
        QFrame#copyScoreMetricCard,
        QFrame#copyComparisonPointCard,
        QFrame#copyComparisonVariantCard,
        QFrame#copyTopicCard,
        QFrame#copyIssueCard,
        QFrame#copySuggestionHero,
        QFrame#copyComplianceSummary,
        QFrame#copyReportFooter {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 16px;
        }}
        QLabel#copyScoreMetricTitle,
        QLabel#copyComparisonVariantTitle,
        QLabel#copyComparisonPointTitle,
        QLabel#copySuggestionTitle,
        QLabel#copyComplianceTitle {{
            color: {TEXT};
            font-size: 14px;
            font-weight: 700;
            background: transparent;
        }}
        QLabel#copyScoreMetricBody,
        QLabel#copyComparisonVariantBody,
        QLabel#copyComparisonPointBody,
        QLabel#copyTopicBody,
        QLabel#copyIssueBody,
        QLabel#copySuggestionBody,
        QLabel#copyComplianceIntro,
        QLabel#copyTopicIntro {{
            color: {TEXT_MUTED};
            font-size: 12px;
            line-height: 1.75;
            background: transparent;
        }}
        QFrame#copyRiskRing {{
            min-height: 160px;
            border-radius: 80px;
            background-color: rgba(245, 158, 11, 0.10);
            border: 10px solid rgba(245, 158, 11, 0.70);
        }}
        QLabel#copyRiskRingScore {{
            color: {TEXT};
            font-size: 34px;
            font-weight: 800;
            background: transparent;
        }}
        QLabel#copyRiskRingLabel {{
            color: {TEXT_MUTED};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
        }}
        """


__all__ = ["CopyGenerationPage"]

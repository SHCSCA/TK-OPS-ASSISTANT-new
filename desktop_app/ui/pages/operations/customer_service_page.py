# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""客服中心原型页面。"""

from dataclasses import dataclass
from typing import Literal

from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TagChip,
    ThemedComboBox,
)
from ...components.inputs import (
    BUTTON_HEIGHT,
    FilterDropdown,
    RADIUS_LG,
    RADIUS_MD,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QVBoxLayout,
    QWidget,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

TrendDirection = Literal["up", "down", "flat"]


@dataclass(frozen=True)
class ServiceMetric:
    """客服中心 KPI。"""

    title: str
    value: str
    trend: TrendDirection
    percentage: str
    caption: str
    sparkline: tuple[float, ...]


@dataclass(frozen=True)
class ConversationRecord:
    """会话列表记录。"""

    customer_name: str
    preview: str
    status: str
    wait_text: str
    channel: str
    issue_tag: str
    order_count: str
    satisfaction: str
    order_history: tuple[tuple[str, str, str], ...]
    past_issues: tuple[str, ...]
    messages: tuple[tuple[str, str, str], ...]
    recommended_template: str
    assignment_hint: str
    escalation_hint: str


SERVICE_METRICS: tuple[ServiceMetric, ...] = (
    ServiceMetric("在线会话", "86", "up", "+12", "午后咨询量上升明显", (42, 48, 54, 61, 68, 75, 86)),
    ServiceMetric("排队等待", "19", "down", "-4", "高峰排班覆盖改善", (28, 26, 24, 23, 22, 21, 19)),
    ServiceMetric("今日解决", "312", "up", "+18.6%", "售前与售后协同更顺畅", (182, 205, 224, 248, 267, 289, 312)),
    ServiceMetric("满意度", "96.2%", "up", "+1.1%", "模板优化后评价更稳定", (92.8, 93.4, 94.1, 94.7, 95.2, 95.8, 96.2)),
)


CONVERSATIONS: tuple[ConversationRecord, ...] = (
    ConversationRecord(
        "林若溪",
        "粉底液色号我担心选错，能不能再给我建议一下？",
        "处理中",
        "等待 32 秒",
        "店铺私信",
        "售前咨询",
        "近 30 天 3 单",
        "满意度高",
        (("TK250309001", "柔雾持妆粉底液 30ml", "待处理"), ("TK250226088", "洁面慕斯", "已完成"), ("TK250208032", "补水喷雾仪", "已完成")),
        ("曾咨询色号选择", "有复购倾向", "偏好自然妆感"),
        (
            ("客户", "11:28", "粉底液 01 和 02 到底哪个更适合黄一白？"),
            ("客服", "11:29", "可以先告诉我你平时更喜欢自然提亮还是接近肤色的效果哦。"),
            ("客户", "11:30", "想自然一点，不想太白。"),
        ),
        "您好，如果偏黄一白且想更自然，通常更建议 02 自然色；如果您平时底妆容易暗沉，也可以考虑 01 提亮。",
        "建议分配给美妆售前组，结合历史购买记录做推荐。",
        "暂无升级必要，可在 2 轮内完成成交引导。",
    ),
    ConversationRecord(
        "周牧遥",
        "鲨鱼裤尺码到底选 M 还是 L，我怕穿着勒。",
        "待回复",
        "等待 1 分 12 秒",
        "店铺私信",
        "尺码咨询",
        "近 30 天 1 单",
        "新客观察",
        (("TK250309002", "高弹亲肤鲨鱼裤", "待处理"),),
        ("首次下单", "尺码犹豫明显", "高退货风险"),
        (
            ("客户", "11:18", "我腰围 72 臀围 96，M 会不会太紧？"),
            ("客服", "11:19", "正在帮您结合身材数据和面料弹力判断。"),
            ("客户", "11:20", "我不想退换，想一次买对。"),
        ),
        "按您提供的数据，如果更看重包裹感建议 M，若更想要舒适余量可以选 L；如果介于两码之间，我们更建议参考臀围优先。",
        "建议转服饰尺码专席，避免后续退款。",
        "若客户情绪升高，可升级给高级售前。",
    ),
    ConversationRecord(
        "姜晚意",
        "这个清洁喷雾开箱漏液了，你们怎么处理？",
        "高优先",
        "等待 18 秒",
        "售后工单",
        "破损投诉",
        "近 30 天 2 单",
        "需挽回",
        (("TK250309013", "居家多效除菌喷雾 2 瓶装", "退款中"), ("TK250228142", "清洁泡泡", "已完成")),
        ("包装问题投诉", "愿意先看方案", "对时效敏感"),
        (
            ("客户", "10:52", "外箱都湿了，喷头这边有渗漏。"),
            ("客服", "10:53", "非常抱歉影响到您使用体验，我们先帮您登记并确认补偿方案。"),
            ("客户", "10:54", "我要么退款，要么你们赶快给个解决办法。"),
        ),
        "非常抱歉给您带来麻烦，我们可以优先为您处理退款，也可以给您补发一套全新商品，并同步补偿优惠券。",
        "建议分配给售后破损专席，同时同步品控。",
        "若买家情绪继续升级，直接升级到主管席位。",
    ),
    ConversationRecord(
        "何听雪",
        "四件套颜色跟图里不太一样。",
        "处理中",
        "等待 40 秒",
        "店铺私信",
        "色差问题",
        "近 30 天 2 单",
        "中性",
        (("TK250309014", "云感纯棉四件套", "退款处理中"), ("TK250215083", "保温杯礼盒", "已完成")),
        ("对质感满意", "仅对色差犹豫", "可尝试挽回"),
        (
            ("客户", "10:02", "实物颜色感觉更暖一点，没有图里那么奶。"),
            ("客服", "10:03", "理解您的感受，不同光线下会有一定偏差，我先把实拍图发给您参考。"),
            ("客户", "10:04", "你先发我看看。"),
        ),
        "这边先给您补充一组自然光与室内光实拍图，如果仍不符合预期，我们可以为您安排退货退款。",
        "建议保留在家纺售后组跟进。",
        "若买家明确拒绝挽回，再升级到退款审核组。",
    ),
    ConversationRecord(
        "苏月汐",
        "我急着出差，喷雾仪为什么还没发？",
        "待回复",
        "等待 56 秒",
        "店铺私信",
        "发货催促",
        "近 30 天 1 单",
        "风险中",
        (("TK250309015", "便携补水喷雾仪", "退款已同意"),),
        ("急用场景", "对发货时效敏感", "容易转差评"),
        (
            ("客户", "08:31", "你们昨天说今天能发的。"),
            ("客服", "08:32", "很抱歉，目前仓库正在确认加急排单。"),
            ("客户", "08:33", "如果今天发不了我就退款。"),
        ),
        "非常抱歉耽误您的使用安排，如已不满足时效需求，我们可优先为您处理退款，并补发一张补偿券。",
        "建议交给履约售后组，先止损情绪。",
        "若买家提及差评，升级给主管席位处理。",
    ),
    ConversationRecord(
        "程见鹿",
        "礼盒压痕太明显了，我是送人的。",
        "高优先",
        "等待 22 秒",
        "售后工单",
        "礼盒破损",
        "近 30 天 4 单",
        "可挽回",
        (("TK250309018", "保温吸管杯礼盒版", "退款待审核"), ("TK250217044", "礼盒版保温杯", "已完成")),
        ("礼赠场景用户", "对包装要求高", "曾给过好评"),
        (
            ("客户", "11:42", "杯子没事，但礼盒角都瘪了，送人太尴尬。"),
            ("客服", "11:43", "理解您的场景，我们可以优先给您补发礼盒或提供补偿。"),
            ("客户", "11:44", "你们先说怎么补。"),
        ),
        "很抱歉影响您的送礼体验，我们可以优先补发全新礼盒，也可根据您的时间安排提供部分退款补偿。",
        "建议交给礼品售后专席，优先补发礼盒。",
        "若客户强烈要求整单退款，再转退款审核。",
    ),
    ConversationRecord(
        "温景岚",
        "活动说有赠品，我怎么没收到？",
        "处理中",
        "等待 28 秒",
        "店铺私信",
        "赠品争议",
        "近 30 天 5 单",
        "老客需维护",
        (("TK250309022", "洁面慕斯", "退款处理中"), ("TK250301043", "粉底液", "已完成"), ("TK250225061", "补水喷雾仪", "已完成")),
        ("老客", "对活动规则敏感", "容易因为赠品影响复购"),
        (
            ("客户", "10:32", "页面写的旅行装没收到。"),
            ("客服", "10:33", "我先帮您核对活动与发货记录。"),
            ("客户", "10:34", "我主要是觉得承诺了就应该给。"),
        ),
        "非常抱歉给您带来落差，这边先帮您核对活动记录；若确实遗漏赠品，我们会第一时间为您补发或做等值补偿。",
        "建议分给活动客服组优先跟进。",
        "若买家情绪上升，可升级给主管做补偿决策。",
    ),
    ConversationRecord(
        "陆时雨",
        "这个礼盒装我想再加一套送朋友，有优惠吗？",
        "待回复",
        "等待 47 秒",
        "店铺私信",
        "加购咨询",
        "近 30 天 3 单",
        "高价值会员",
        (("TK250309012", "洁面慕斯", "已完成"), ("TK250227089", "礼盒保温杯", "已完成"), ("TK250216077", "粉底液", "已完成")),
        ("复购用户", "偏好礼盒商品", "可做组合包"),
        (
            ("客户", "11:02", "我觉得这个礼盒挺适合送人，第二套能优惠吗？"),
            ("客服", "11:03", "可以的，我帮您看下当前组合优惠。"),
        ),
        "您好，当前加购第二套可享组合满减，同时还能叠加老客专享券，我这边可以直接把链接发给您。",
        "建议交给成交专席，直接推组合购。",
        "暂无升级必要。",
    ),
    ConversationRecord(
        "许知暖",
        "热敷腰带的二档忽冷忽热，我有点担心。",
        "高优先",
        "等待 15 秒",
        "售后工单",
        "质量争议",
        "近 30 天 1 单",
        "待安抚",
        (("TK250309016", "智能暖腹热敷腰带", "退款待审核"),),
        ("功能异常", "高客单售后", "需快速安抚"),
        (
            ("客户", "12:05", "我开到二档会断续，感觉有问题。"),
            ("客服", "12:06", "抱歉影响使用，我这边先帮您登记，并一起确认序列号与使用环境。"),
        ),
        "非常抱歉影响您的使用体验，我们可以优先帮您安排换新或退款，也会同步技术和质检同事核查该批次。",
        "建议转质量售后专席。",
        "若客户表达安全担忧，立即升级到主管。",
    ),
    ConversationRecord(
        "夏知微",
        "支付是不是有问题？订单怎么一直没变化。",
        "处理中",
        "等待 26 秒",
        "店铺私信",
        "支付异常",
        "近 30 天 2 单",
        "中性",
        (("TK250309009", "智能暖腹热敷腰带", "异常订单"), ("TK250223059", "暖腹腰带", "已完成")),
        ("支付回调异常", "二次复购用户", "希望尽快确认"),
        (
            ("客户", "11:23", "我这边已经付款了，为什么还显示异常？"),
            ("客服", "11:24", "我先帮您核对支付回调与订单状态，请稍等。"),
        ),
        "您好，系统正在同步支付状态，我这边会优先帮您核实；若确认支付成功，会第一时间恢复订单并安排优先处理。",
        "建议交给支付异常专席。",
        "若 5 分钟内无法闭环，升级给财务协同。",
    ),
)


QUALITY_TABLE_HEADERS = ["指标", "当前值", "目标值", "说明"]
QUALITY_ROWS = [
    ["首响时长", "38 秒", "≤ 45 秒", "高峰时段已稳定达标"],
    ["一次解决率", "84.6%", ">= 82%", "售前尺码问题改善明显"],
    ["转人工率", "13.2%", "≤ 15%", "复杂售后仍需重点兜底"],
    ["满意度", "96.2%", ">= 95%", "老客维护表现稳定"],
    ["退款挽回率", "28.4%", ">= 25%", "礼盒与赠品类挽回有效"],
    ["高优先工单闭环", "92.1%", ">= 90%", "主管响应更及时"],
]


TEMPLATE_OPTIONS = (
    "售前色号建议",
    "尺码咨询标准回复",
    "破损安抚与补偿",
    "赠品缺失补发说明",
    "发货延迟安抚",
    "质量争议安抚",
)


TEMPLATE_TEXTS: dict[str, str] = {
    "售前色号建议": "您好，结合您描述的肤色与妆感偏好，通常更建议先从自然色入手；如果您更追求提亮效果，也可以考虑亮一档色号。",
    "尺码咨询标准回复": "为了尽量一次买对，建议优先参考臀围与平时穿着习惯；如果介于两码之间，追求包裹感可选小一码，追求舒适余量可选大一码。",
    "破损安抚与补偿": "非常抱歉影响到您的使用体验，我们这边可以优先为您处理退款，也可以为您补发全新商品并同步补偿方案。",
    "赠品缺失补发说明": "抱歉给您造成落差，这边会先帮您核对活动记录；如确认遗漏赠品，我们会第一时间安排补发或做等值补偿。",
    "发货延迟安抚": "非常抱歉耽误了您的安排，这边会立即核对仓库排单；如已不满足您的使用时效，我们也可以优先协助退款并补偿优惠券。",
    "质量争议安抚": "很抱歉影响您的使用体验，我们会第一时间协助您确认具体问题，并同步技术与质检同事给出换新或退款方案。",
}


ASSIGNMENT_OPTIONS = ("当前接待人", "美妆售前组", "服饰尺码专席", "售后破损专席", "质量售后专席", "活动客服组", "支付异常专席")
ESCALATION_OPTIONS = ("无需升级", "升级主管复核", "升级品控协同", "升级仓配协同", "升级财务协同")


class CustomerServiceCenterPage(BasePage):
    """客服中心，包含会话列表、聊天占位区、客户资料与服务质量面板。"""

    default_route_id: RouteId = RouteId("customer_service_center")
    default_display_name: str = "客服中心"
    default_icon_name: str = "support_agent"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._search_text: str = ""
        self._status_filter: str = "全部"
        self._selected_index: int = 0
        self._selected_template: str = TEMPLATE_OPTIONS[0]
        self._metric_cards: list[KPICard] = []
        self._conversation_rows: list[dict[str, QWidget]] = []
        self._message_bubbles: list[QFrame] = []

        self._page_container: PageContainer | None = None
        self._search_bar: SearchBar | None = None
        self._status_dropdown: FilterDropdown | None = None
        self._template_dropdown: ThemedComboBox | None = None
        self._assignment_dropdown: ThemedComboBox | None = None
        self._escalation_dropdown: ThemedComboBox | None = None
        self._summary_badge: StatusBadge | None = None
        self._summary_label: QLabel | None = None
        self._conversation_list_host: QWidget | None = None
        self._conversation_list_layout: QVBoxLayout | None = None
        self._chat_title: QLabel | None = None
        self._chat_status_badge: StatusBadge | None = None
        self._chat_meta_label: QLabel | None = None
        self._chat_messages_host: QWidget | None = None
        self._chat_messages_layout: QVBoxLayout | None = None
        self._template_preview_label: QLabel | None = None
        self._customer_profile_label: QLabel | None = None
        self._order_history_label: QLabel | None = None
        self._past_issues_label: QLabel | None = None
        self._quality_table: DataTable | None = None
        self._feedback_badge: StatusBadge | None = None
        self._feedback_label: QLabel | None = None
        self._assign_button: PrimaryButton | None = None
        self._escalate_button: SecondaryButton | None = None

        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        _call(self, "setObjectName", "customerServiceCenterPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._page_container = PageContainer(
            title=self.display_name,
            description="用于 TikTok Shop 客服团队统一处理售前、售后、挽回与升级协同的三栏式交互工作台。",
            parent=self,
        )

        self._build_action_bar()
        self._build_metric_section()
        self._build_main_split()
        self._build_quality_section()

        self.layout.addWidget(self._page_container)
        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_action_bar(self) -> None:
        if self._page_container is None:
            return
        host = QWidget(self._page_container)
        _call(host, "setObjectName", "customerServiceActionBar")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)
        self._search_bar = SearchBar("搜索客户名、问题关键词或订单号")
        self._status_dropdown = FilterDropdown("会话状态", ["待回复", "处理中", "高优先"], parent=host)
        layout.addWidget(self._search_bar, 1)
        layout.addWidget(self._status_dropdown)
        self._page_container.add_action(host)

    def _build_metric_section(self) -> None:
        if self._page_container is None:
            return
        section = ContentSection("服务概览", icon="◉", parent=self._page_container)

        strip = QWidget(section)
        _call(strip, "setObjectName", "customerServiceSummaryStrip")
        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(0, 0, 0, 0)
        strip_layout.setSpacing(SPACING_MD)
        self._summary_badge = StatusBadge("高优先会话待关注", tone="warning", parent=strip)
        self._summary_label = QLabel("", strip)
        _call(self._summary_label, "setObjectName", "customerServiceSummaryLabel")
        _call(self._summary_label, "setWordWrap", True)
        strip_layout.addWidget(self._summary_badge)
        strip_layout.addWidget(TagChip("支持快捷回复与升级", tone="brand", parent=strip))
        strip_layout.addWidget(self._summary_label, 1)
        section.add_widget(strip)

        row = QWidget(section)
        _call(row, "setObjectName", "customerServiceMetricRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_MD)
        for metric in SERVICE_METRICS:
            card = KPICard(
                title=metric.title,
                value=metric.value,
                trend=metric.trend,
                percentage=metric.percentage,
                caption=metric.caption,
                sparkline_data=metric.sparkline,
            )
            self._metric_cards.append(card)
            row_layout.addWidget(card, 1)
        section.add_widget(row)
        self._page_container.add_widget(section)

    def _build_main_split(self) -> None:
        if self._page_container is None:
            return
        outer_split = SplitPanel(split_ratio=(0.28, 0.72), minimum_sizes=(320, 880), parent=self._page_container)
        outer_split.set_widgets(self._build_conversation_column(), self._build_chat_and_profile_split())
        self._page_container.add_widget(outer_split)

    def _build_conversation_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("会话列表", icon="◌", parent=host)
        section.add_widget(
            InfoCard(
                title="优先级建议",
                description="优先处理高优先与破损 / 质量争议类会话，避免在退款路径中持续放大情绪。",
                icon="⚠",
                action_text="仅看高优先",
                parent=section,
            )
        )

        self._conversation_list_host = QWidget(host)
        _call(self._conversation_list_host, "setObjectName", "customerConversationList")
        self._conversation_list_layout = QVBoxLayout(self._conversation_list_host)
        conversation_list_host = self._conversation_list_host
        if conversation_list_host is not None:
            section.add_widget(conversation_list_host)
        layout.addWidget(section)
        return host

    def _build_chat_and_profile_split(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        inner_split = SplitPanel(split_ratio=(0.58, 0.42), minimum_sizes=(520, 360), parent=host)
        inner_split.set_widgets(self._build_chat_column(), self._build_profile_column())
        layout.addWidget(inner_split)
        return host

    def _build_chat_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("会话窗口", icon="✦", parent=host)
        header_card = QFrame(section)
        _call(header_card, "setObjectName", "customerChatHeaderCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_SM)
        title_row = QHBoxLayout()
        title_row.setSpacing(SPACING_MD)
        self._chat_title = QLabel("", header_card)
        _call(self._chat_title, "setObjectName", "customerChatTitle")
        self._chat_status_badge = StatusBadge("", tone="neutral", parent=header_card)
        title_row.addWidget(self._chat_title, 1)
        title_row.addWidget(self._chat_status_badge)
        header_layout.addLayout(title_row)
        self._chat_meta_label = QLabel("", header_card)
        _call(self._chat_meta_label, "setObjectName", "customerChatMeta")
        _call(self._chat_meta_label, "setWordWrap", True)
        header_layout.addWidget(self._chat_meta_label)
        section.add_widget(header_card)

        self._chat_messages_host = QWidget(host)
        _call(self._chat_messages_host, "setObjectName", "customerChatMessages")
        self._chat_messages_layout = QVBoxLayout(self._chat_messages_host)
        chat_messages_host = self._chat_messages_host
        if chat_messages_host is not None:
            section.add_widget(chat_messages_host)

        template_card = QFrame(section)
        _call(template_card, "setObjectName", "customerTemplateCard")
        template_layout = QVBoxLayout(template_card)
        template_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        template_layout.setSpacing(SPACING_MD)
        template_layout.addWidget(self._create_card_title("快捷回复模板", template_card))
        self._template_dropdown = ThemedComboBox("选择模板", TEMPLATE_OPTIONS, template_card)
        template_layout.addWidget(self._template_dropdown)
        self._template_preview_label = QLabel("", template_card)
        _call(self._template_preview_label, "setObjectName", "customerDetailBody")
        _call(self._template_preview_label, "setWordWrap", True)
        template_layout.addWidget(self._template_preview_label)
        section.add_widget(template_card)

        layout.addWidget(section)
        return host

    def _build_profile_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("客户信息与协同", icon="☍", parent=host)

        profile_card = QFrame(section)
        _call(profile_card, "setObjectName", "customerProfileCard")
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        profile_layout.setSpacing(SPACING_SM)
        profile_layout.addWidget(self._create_card_title("客户画像", profile_card))
        self._customer_profile_label = QLabel("", profile_card)
        _call(self._customer_profile_label, "setObjectName", "customerDetailBody")
        _call(self._customer_profile_label, "setWordWrap", True)
        profile_layout.addWidget(self._customer_profile_label)
        section.add_widget(profile_card)

        order_card = QFrame(section)
        _call(order_card, "setObjectName", "customerProfileCard")
        order_layout = QVBoxLayout(order_card)
        order_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        order_layout.setSpacing(SPACING_SM)
        order_layout.addWidget(self._create_card_title("订单历史", order_card))
        self._order_history_label = QLabel("", order_card)
        _call(self._order_history_label, "setObjectName", "customerDetailBody")
        _call(self._order_history_label, "setWordWrap", True)
        order_layout.addWidget(self._order_history_label)
        section.add_widget(order_card)

        issue_card = QFrame(section)
        _call(issue_card, "setObjectName", "customerProfileCard")
        issue_layout = QVBoxLayout(issue_card)
        issue_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        issue_layout.setSpacing(SPACING_SM)
        issue_layout.addWidget(self._create_card_title("历史问题", issue_card))
        self._past_issues_label = QLabel("", issue_card)
        _call(self._past_issues_label, "setObjectName", "customerDetailBody")
        _call(self._past_issues_label, "setWordWrap", True)
        issue_layout.addWidget(self._past_issues_label)
        section.add_widget(issue_card)

        action_card = QFrame(section)
        _call(action_card, "setObjectName", "customerProfileCard")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        action_layout.setSpacing(SPACING_MD)
        action_layout.addWidget(self._create_card_title("指派与升级", action_card))
        self._assignment_dropdown = ThemedComboBox("工单指派", ASSIGNMENT_OPTIONS, action_card)
        self._escalation_dropdown = ThemedComboBox("升级控制", ESCALATION_OPTIONS, action_card)
        action_layout.addWidget(self._assignment_dropdown)
        action_layout.addWidget(self._escalation_dropdown)
        button_row = QHBoxLayout()
        button_row.setSpacing(SPACING_MD)
        self._assign_button = PrimaryButton("指派当前会话", action_card, icon_text="→")
        self._escalate_button = SecondaryButton("发起升级", action_card, icon_text="⇡")
        button_row.addWidget(self._assign_button)
        button_row.addWidget(self._escalate_button)
        action_layout.addLayout(button_row)
        feedback_row = QHBoxLayout()
        feedback_row.setSpacing(SPACING_MD)
        self._feedback_badge = StatusBadge("等待操作", tone="neutral", parent=action_card)
        self._feedback_label = QLabel("可对当前会话执行指派或升级模拟动作。", action_card)
        _call(self._feedback_label, "setObjectName", "customerDetailBody")
        _call(self._feedback_label, "setWordWrap", True)
        feedback_row.addWidget(self._feedback_badge)
        feedback_row.addWidget(self._feedback_label, 1)
        action_layout.addLayout(feedback_row)
        section.add_widget(action_card)

        layout.addWidget(section)
        return host

    def _build_quality_section(self) -> None:
        if self._page_container is None:
            return
        section = ContentSection("服务质量指标", icon="▣", parent=self._page_container)
        section.add_widget(
            InfoCard(
                title="质量复盘建议",
                description="持续关注高优先工单闭环、一次解决率与退款挽回率，把高频问题沉淀到模板库。",
                icon="◎",
                action_text="输出班次复盘",
                parent=section,
            )
        )
        self._quality_table = DataTable(headers=QUALITY_TABLE_HEADERS, rows=QUALITY_ROWS, page_size=6, parent=section)
        section.add_widget(self._quality_table)
        self._page_container.add_widget(section)

    def _create_card_title(self, text: str, parent: QWidget) -> QLabel:
        label = QLabel(text, parent)
        _call(label, "setObjectName", "customerCardTitle")
        return label

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._on_search_changed)
        if self._status_dropdown is not None:
            _connect(self._status_dropdown.filter_changed, self._on_status_changed)
        if self._template_dropdown is not None:
            _connect(getattr(self._template_dropdown.combo_box, "currentTextChanged", None), self._on_template_changed)
        if self._assign_button is not None:
            _connect(getattr(self._assign_button, "clicked", None), self._assign_current)
        if self._escalate_button is not None:
            _connect(getattr(self._escalate_button, "clicked", None), self._escalate_current)

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#customerServiceCenterPage {{
                background: transparent;
            }}
            QWidget#customerServiceSummaryStrip,
            QWidget#customerServiceActionBar {{
                background-color: rgba(0, 242, 234, 0.05);
                border: 1px solid rgba(0, 242, 234, 0.12);
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px;
            }}
            QLabel#customerServiceSummaryLabel,
            QLabel#customerChatMeta,
            QLabel#customerDetailBody {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.55;
            }}
            QLabel#customerChatTitle,
            QLabel#customerCardTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#customerChatHeaderCard,
            QFrame#customerTemplateCard,
            QFrame#customerProfileCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#customerChatMessages,
            QWidget#customerConversationList {{
                background: transparent;
            }}
            QFrame[conversationActive="true"] {{
                border-color: {_token('brand.primary')};
                background-color: rgba(0, 242, 234, 0.06);
            }}
            QFrame#customerMessageBubble[role="客服"] {{
                background-color: rgba(0, 242, 234, 0.12);
                border: 1px solid rgba(0, 242, 234, 0.22);
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#customerMessageBubble[role="客户"] {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#customerMessageRole {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#customerMessageText {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QFrame#customerConversationRow {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#customerConversationTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#customerConversationMeta,
            QLabel#customerConversationPreview {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#customerConversationInspectButton {{
                background-color: transparent;
                color: {_token('brand.primary')};
                border: 1px solid {_token('brand.primary')};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
            }}
            QPushButton#customerConversationInspectButton:hover {{
                background-color: rgba(0, 242, 234, 0.10);
            }}
            """,
        )

    def _filtered_conversations(self) -> list[ConversationRecord]:
        result: list[ConversationRecord] = []
        for record in CONVERSATIONS:
            if self._status_filter != "全部" and record.status != self._status_filter:
                continue
            if self._search_text:
                haystack = " ".join(
                    (
                        record.customer_name,
                        record.preview,
                        record.issue_tag,
                        record.channel,
                        record.recommended_template,
                    )
                ).lower()
                if self._search_text not in haystack:
                    continue
            result.append(record)
        return result

    def _refresh_all_views(self) -> None:
        conversations = self._filtered_conversations()
        self._refresh_summary(conversations)
        self._refresh_conversation_list(conversations)
        self._refresh_chat_panel(conversations)
        self._refresh_profile_panel(conversations)
        self._refresh_template_preview(conversations)

    def _refresh_summary(self, conversations: list[ConversationRecord]) -> None:
        if self._summary_label is not None:
            _call(self._summary_label, "setText", f"当前筛选命中 {len(conversations)} 个会话，建议优先处理高优先破损 / 质量争议类问题，同时兼顾售前成交机会。")
        if self._summary_badge is not None:
            high_count = sum(1 for item in conversations if item.status == "高优先")
            tone = "warning" if high_count else "success"
            self._summary_badge.set_tone(tone)
            _call(self._summary_badge, "setText", f"高优先 {high_count} 个")

    def _refresh_conversation_list(self, conversations: list[ConversationRecord]) -> None:
        if self._conversation_list_layout is None or self._conversation_list_host is None:
            return
        while getattr(self._conversation_list_layout, "count", lambda: 0)() > 0:
            item = self._conversation_list_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                _call(widget, "deleteLater")
        self._conversation_rows = []
        for index, record in enumerate(conversations):
            row = self._create_conversation_row(index, record, self._conversation_list_host)
            self._conversation_rows.append(row)
            self._conversation_list_layout.addWidget(row["frame"])
        self._conversation_list_layout.addStretch(1)
        if conversations:
            self._selected_index = min(self._selected_index, len(conversations) - 1)
        else:
            self._selected_index = 0
        for index, row in enumerate(self._conversation_rows):
            _call(row["frame"], "setProperty", "conversationActive", "true" if index == self._selected_index else "false")

    def _create_conversation_row(self, index: int, record: ConversationRecord, parent: QWidget) -> dict[str, QWidget]:
        frame = QFrame(parent)
        _call(frame, "setObjectName", "customerConversationRow")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_XS)

        title_row = QHBoxLayout()
        title_row.setSpacing(SPACING_MD)
        title = QLabel(record.customer_name, frame)
        _call(title, "setObjectName", "customerConversationTitle")
        badge = StatusBadge(record.status, tone="neutral", parent=frame)
        badge.set_tone(self._status_tone(record.status))
        title_row.addWidget(title, 1)
        title_row.addWidget(badge)

        preview = QLabel(record.preview, frame)
        _call(preview, "setObjectName", "customerConversationPreview")
        _call(preview, "setWordWrap", True)
        meta = QLabel(f"{record.wait_text}｜{record.channel}｜{record.issue_tag}", frame)
        _call(meta, "setObjectName", "customerConversationMeta")
        button = QPushButton("查看", frame)
        _call(button, "setObjectName", "customerConversationInspectButton")
        _call(button, "setMinimumHeight", BUTTON_HEIGHT)

        layout.addLayout(title_row)
        layout.addWidget(preview)
        layout.addWidget(meta)
        layout.addWidget(button)
        _connect(getattr(button, "clicked", None), lambda current=index: self._select_conversation(current))
        return {"frame": frame, "title": title, "badge": badge, "preview": preview, "meta": meta, "button": button}

    def _refresh_chat_panel(self, conversations: list[ConversationRecord]) -> None:
        if not conversations:
            self._set_empty_chat()
            return
        record = conversations[max(0, min(self._selected_index, len(conversations) - 1))]
        if self._chat_title is not None:
            _call(self._chat_title, "setText", record.customer_name)
        if self._chat_status_badge is not None:
            _call(self._chat_status_badge, "setText", record.status)
            self._chat_status_badge.set_tone(self._status_tone(record.status))
        if self._chat_meta_label is not None:
            _call(self._chat_meta_label, "setText", f"渠道：{record.channel}｜问题标签：{record.issue_tag}｜{record.wait_text}｜{record.order_count}")
        self._render_messages(record.messages)

    def _render_messages(self, messages: tuple[tuple[str, str, str], ...]) -> None:
        if self._chat_messages_layout is None or self._chat_messages_host is None:
            return
        while getattr(self._chat_messages_layout, "count", lambda: 0)() > 0:
            item = self._chat_messages_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                _call(widget, "deleteLater")
        for role, time_text, content in messages:
            bubble = QFrame(self._chat_messages_host)
            _call(bubble, "setObjectName", "customerMessageBubble")
            _call(bubble, "setProperty", "role", role)
            bubble_layout = QVBoxLayout(bubble)
            bubble_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
            bubble_layout.setSpacing(SPACING_XS)
            role_label = QLabel(f"{role}｜{time_text}", bubble)
            _call(role_label, "setObjectName", "customerMessageRole")
            content_label = QLabel(content, bubble)
            _call(content_label, "setObjectName", "customerMessageText")
            _call(content_label, "setWordWrap", True)
            bubble_layout.addWidget(role_label)
            bubble_layout.addWidget(content_label)
            self._chat_messages_layout.addWidget(bubble)
        self._chat_messages_layout.addStretch(1)

    def _refresh_profile_panel(self, conversations: list[ConversationRecord]) -> None:
        if not conversations:
            self._set_empty_profile()
            return
        record = conversations[max(0, min(self._selected_index, len(conversations) - 1))]
        if self._customer_profile_label is not None:
            _call(
                self._customer_profile_label,
                "setText",
                f"客户名称：{record.customer_name}\n会话状态：{record.status}\n问题标签：{record.issue_tag}\n订单概况：{record.order_count}\n满意度：{record.satisfaction}",
            )
        if self._order_history_label is not None:
            lines = [f"• {order_id}｜{product_name}｜{status}" for order_id, product_name, status in record.order_history]
            _call(self._order_history_label, "setText", "\n".join(lines))
        if self._past_issues_label is not None:
            _call(self._past_issues_label, "setText", "\n".join(f"• {item}" for item in record.past_issues))

    def _refresh_template_preview(self, conversations: list[ConversationRecord]) -> None:
        template = TEMPLATE_TEXTS.get(self._selected_template, TEMPLATE_TEXTS[TEMPLATE_OPTIONS[0]])
        if conversations:
            record = conversations[max(0, min(self._selected_index, len(conversations) - 1))]
            template = record.recommended_template if self._selected_template == TEMPLATE_OPTIONS[0] else template
        if self._template_preview_label is not None:
            _call(self._template_preview_label, "setText", template)

    def _set_empty_chat(self) -> None:
        if self._chat_title is not None:
            _call(self._chat_title, "setText", "暂无匹配会话")
        if self._chat_status_badge is not None:
            _call(self._chat_status_badge, "setText", "空状态")
            self._chat_status_badge.set_tone("neutral")
        if self._chat_meta_label is not None:
            _call(self._chat_meta_label, "setText", "请调整筛选条件查看会话内容。")
        self._render_messages((("客服", "--:--", "当前没有匹配的会话记录。"),))

    def _set_empty_profile(self) -> None:
        for widget, text in (
            (self._customer_profile_label, "暂无客户画像。"),
            (self._order_history_label, "暂无订单历史。"),
            (self._past_issues_label, "暂无历史问题。"),
        ):
            if widget is not None:
                _call(widget, "setText", text)

    def _status_tone(self, status: str) -> BadgeTone:
        if status == "待回复":
            return "warning"
        if status == "处理中":
            return "brand"
        if status == "高优先":
            return "error"
        return "neutral"

    def _on_search_changed(self, text: str) -> None:
        self._search_text = text.strip().lower()
        self._selected_index = 0
        self._refresh_all_views()

    def _on_status_changed(self, text: str) -> None:
        self._status_filter = text or "全部"
        self._selected_index = 0
        self._refresh_all_views()

    def _on_template_changed(self, text: str) -> None:
        self._selected_template = text or TEMPLATE_OPTIONS[0]
        self._refresh_template_preview(self._filtered_conversations())

    def _select_conversation(self, index: int) -> None:
        self._selected_index = index
        self._refresh_all_views()

    def _assign_current(self) -> None:
        record = self._current_record()
        if record is None:
            return
        assignment = self._assignment_dropdown.current_text() if self._assignment_dropdown is not None else "当前接待人"
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone("brand")
            _call(self._feedback_badge, "setText", "已指派")
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", f"已将 {record.customer_name} 的会话指派到 {assignment}，建议动作：{record.assignment_hint}")

    def _escalate_current(self) -> None:
        record = self._current_record()
        if record is None:
            return
        escalation = self._escalation_dropdown.current_text() if self._escalation_dropdown is not None else "无需升级"
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone("warning")
            _call(self._feedback_badge, "setText", "已发起升级")
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", f"已对 {record.customer_name} 的会话执行【{escalation}】，升级建议：{record.escalation_hint}")

    def _current_record(self) -> ConversationRecord | None:
        conversations = self._filtered_conversations()
        if not conversations:
            return None
        return conversations[max(0, min(self._selected_index, len(conversations) - 1))]

    def on_activated(self) -> None:
        self._refresh_all_views()

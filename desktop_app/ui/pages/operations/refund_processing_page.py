# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""退款处理原型页面。"""

from dataclasses import dataclass
from typing import Literal

from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    ImageGrid,
    InfoCard,
    KPICard,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TagChip,
    ThemedTextEdit,
    TimelineWidget,
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
DESKTOP_PAGE_MAX_WIDTH = 1880


@dataclass(frozen=True)
class RefundMetric:
    """退款中心 KPI。"""

    title: str
    value: str
    trend: TrendDirection
    percentage: str
    caption: str
    sparkline: tuple[float, ...]


@dataclass(frozen=True)
class RefundHistoryEntry:
    """退款处理历史。"""

    timestamp: str
    title: str
    detail: str
    level: str

    def to_event(self) -> dict[str, str]:
        return {
            "timestamp": self.timestamp,
            "title": self.title,
            "content": self.detail,
            "type": self.level,
        }


@dataclass(frozen=True)
class RefundRecord:
    """退款记录。"""

    refund_id: str
    order_id: str
    buyer_name: str
    reason_category: str
    reason_title: str
    amount_text: str
    amount_value: float
    status: str
    date_text: str
    product_name: str
    order_amount_text: str
    shipping_status: str
    warehouse: str
    reason_detail: str
    evidence_images: tuple[str, ...]
    processing_history: tuple[RefundHistoryEntry, ...]
    note_hint: str
    severity_tag: str
    owner_name: str

    def to_row(self) -> list[str]:
        return [
            self.refund_id,
            self.order_id,
            self.buyer_name,
            self.reason_title,
            self.amount_text,
            self.status,
            self.date_text,
        ]


REFUND_METRICS: tuple[RefundMetric, ...] = (
    RefundMetric("待处理退款", "67", "up", "+8 单", "午后尺码与破损类申请偏多", (32, 38, 40, 45, 52, 58, 67)),
    RefundMetric("今日处理量", "124", "up", "+16.9%", "团队处理效率明显提升", (68, 74, 82, 95, 102, 116, 124)),
    RefundMetric("平均处理时长", "1.8 小时", "down", "-0.4 小时", "标准话术与分级审批见效", (3.4, 3.1, 2.8, 2.5, 2.2, 2.0, 1.8)),
    RefundMetric("退款总额", "¥18,420", "down", "-6.7%", "高客单退款得到控制", (28, 26, 24, 23, 21, 19, 18.4)),
)


REFUND_TABLE_HEADERS = ["退款单号", "订单号", "买家", "退款原因", "金额", "状态", "申请时间"]


REFUND_RECORDS: tuple[RefundRecord, ...] = (
    RefundRecord(
        "RF250309001",
        "TK250309002",
        "周牧遥",
        "尺码问题",
        "尺码不合适",
        "¥199.00",
        199.0,
        "待审核",
        "2026-03-09 11:06",
        "高弹亲肤鲨鱼裤",
        "¥199.00",
        "未发货",
        "华东仓",
        "买家表示之前客服建议 L 码，但担心腰围偏松，希望直接退款后重新下单 M 码。",
        ("mock/refund/size_1.png", "mock/refund/size_2.png", "mock/refund/chat_size.png"),
        (
            RefundHistoryEntry("11:06", "买家提交申请", "备注尺码不合适，要求整单退款。", "warning"),
            RefundHistoryEntry("11:14", "客服初审", "确认订单尚未出库，可直接拦截。", "info"),
        ),
        "建议直接同意退款，并引导买家改拍 M 码链接。",
        "可快速通过",
        "售后一组-初禾",
    ),
    RefundRecord(
        "RF250309002",
        "TK250309005",
        "顾南枝",
        "地址异常",
        "信息填写错误",
        "¥120.00",
        120.0,
        "处理中",
        "2026-03-09 11:18",
        "轻氧羽感防晒乳",
        "¥120.00",
        "面单校验失败",
        "华东仓",
        "地址字段重复导致系统拦截，买家申请退款后重新拍单，正在等待财务释放冻结库存。",
        ("mock/refund/address_1.png", "mock/refund/address_2.png"),
        (
            RefundHistoryEntry("11:18", "买家提交申请", "称地址填错，希望取消。", "warning"),
            RefundHistoryEntry("11:22", "仓库确认", "订单未发货，可直接撤单。", "success"),
            RefundHistoryEntry("11:30", "财务处理中", "等待释放库存与关闭支付流水。", "info"),
        ),
        "优先完成撤单并给出重新拍单指引。",
        "流程清晰",
        "财务协同-秋实",
    ),
    RefundRecord(
        "RF250309003",
        "TK250309013",
        "姜晚意",
        "商品破损",
        "外包装破损漏液",
        "¥114.00",
        114.0,
        "待审核",
        "2026-03-09 10:52",
        "居家多效除菌喷雾 2 瓶装",
        "¥114.00",
        "已签收",
        "华中仓",
        "买家上传开箱图显示瓶口处有轻微渗漏，外箱角落有水渍，担心影响使用。",
        ("mock/refund/leak_1.png", "mock/refund/leak_2.png", "mock/refund/leak_3.png"),
        (
            RefundHistoryEntry("10:52", "买家提交申请", "描述包装渗漏并上传照片。", "warning"),
            RefundHistoryEntry("11:08", "质检待介入", "需要确认是否批次问题。", "info"),
        ),
        "建议同意退款并同步品控抽检同批次商品。",
        "高优先",
        "质检协同-岚岚",
    ),
    RefundRecord(
        "RF250309004",
        "TK250309014",
        "何听雪",
        "体验不符",
        "与描述不一致",
        "¥399.00",
        399.0,
        "处理中",
        "2026-03-09 09:48",
        "云感纯棉四件套",
        "¥399.00",
        "已签收",
        "华北仓",
        "买家反馈实物颜色偏暖，不符合详情页主图预期，希望退货退款。客服已提供补充实拍说明，仍要求退款。",
        ("mock/refund/bedding_1.png", "mock/refund/bedding_2.png"),
        (
            RefundHistoryEntry("09:48", "买家发起售后", "理由为颜色与预期存在偏差。", "warning"),
            RefundHistoryEntry("10:02", "客服沟通", "已发送实拍图和色差说明。", "info"),
            RefundHistoryEntry("10:30", "买家坚持退货", "等待仓库回传退件地址。", "warning"),
        ),
        "如无法挽回，建议走退货退款并记录详情页色彩优化项。",
        "需二次沟通",
        "售后二组-言初",
    ),
    RefundRecord(
        "RF250309005",
        "TK250309015",
        "苏月汐",
        "发货延迟",
        "超时未发货",
        "¥99.00",
        99.0,
        "已同意",
        "2026-03-09 08:26",
        "便携补水喷雾仪",
        "¥99.00",
        "超 24 小时未出库",
        "华南仓",
        "买家需要次日出差使用，因仓库波峰未及时出库，买家申请退款并重新线下购买。",
        ("mock/refund/delay_1.png",),
        (
            RefundHistoryEntry("08:26", "买家提交申请", "说明急用场景。", "warning"),
            RefundHistoryEntry("08:38", "运营确认超时", "超出承诺时效。", "error"),
            RefundHistoryEntry("08:45", "平台同意退款", "已走原路退回。", "success"),
        ),
        "该单已同意，建议复盘仓库波峰时段排班。",
        "已完成审核",
        "履约组-时砚",
    ),
    RefundRecord(
        "RF250309006",
        "TK250309016",
        "许知暖",
        "质量争议",
        "功能异常",
        "¥219.00",
        219.0,
        "待审核",
        "2026-03-09 12:05",
        "智能暖腹热敷腰带",
        "¥219.00",
        "已签收",
        "华中仓",
        "买家反馈第二档加热不稳定，偶发断续，上传了通电视频截图与聊天记录。",
        ("mock/refund/heater_1.png", "mock/refund/heater_2.png", "mock/refund/heater_3.png"),
        (
            RefundHistoryEntry("12:05", "买家提交申请", "说明二档加热异常。", "warning"),
            RefundHistoryEntry("12:14", "客服收集证据", "已让买家补充设备序列号。", "info"),
        ),
        "建议优先补发或退款二选一，并同步质检关注该批次。",
        "高优先",
        "质检协同-木槿",
    ),
    RefundRecord(
        "RF250309007",
        "TK250309017",
        "林若溪",
        "重复下单",
        "拍错规格",
        "¥169.00",
        169.0,
        "已同意",
        "2026-03-09 09:02",
        "柔雾持妆粉底液 30ml",
        "¥169.00",
        "未发货",
        "华东仓",
        "买家误拍两个色号，保留 01 号，申请取消 02 号订单。",
        ("mock/refund/repeat_1.png",),
        (
            RefundHistoryEntry("09:02", "买家提交申请", "表示重复拍单。", "warning"),
            RefundHistoryEntry("09:06", "客服核实", "确认另一单已保留。", "info"),
            RefundHistoryEntry("09:08", "同意退款", "已拦截未发货订单。", "success"),
        ),
        "已完成退款，后续可优化规格选择提示。",
        "已完成审核",
        "售后一组-阿琳",
    ),
    RefundRecord(
        "RF250309008",
        "TK250309018",
        "程见鹿",
        "商品破损",
        "礼盒压痕严重",
        "¥124.00",
        124.0,
        "待审核",
        "2026-03-09 11:42",
        "保温吸管杯礼盒版",
        "¥124.00",
        "已签收",
        "西南仓",
        "礼盒角落明显压瘪，杯体正常，但买家用于送礼，要求整单退款。",
        ("mock/refund/gift_1.png", "mock/refund/gift_2.png"),
        (
            RefundHistoryEntry("11:42", "买家提交申请", "礼盒压痕影响送礼。", "warning"),
            RefundHistoryEntry("11:50", "客服回访", "确认杯体正常但礼盒无法复原。", "info"),
        ),
        "建议优先补发空礼盒或部分退款，尽量保留订单。",
        "有挽回空间",
        "客服挽回-南知",
    ),
    RefundRecord(
        "RF250309009",
        "TK250309019",
        "温景岚",
        "少件漏发",
        "组合装缺少 1 件",
        "¥110.00",
        110.0,
        "处理中",
        "2026-03-09 09:58",
        "婴童柔护湿巾 80 抽 5 包",
        "¥110.00",
        "已签收",
        "华东仓",
        "买家称实收仅 4 包，上传了开箱视频封面，仓库正在核查拣货记录。",
        ("mock/refund/wipes_1.png", "mock/refund/wipes_2.png"),
        (
            RefundHistoryEntry("09:58", "买家提交申请", "声称少发一包。", "warning"),
            RefundHistoryEntry("10:12", "仓库复核", "正在回看称重与打包监控。", "info"),
            RefundHistoryEntry("10:44", "待结果确认", "尚未形成最终责任认定。", "warning"),
        ),
        "建议先安抚并提供补发或差额退款方案。",
        "需仓库协同",
        "仓配售后-闻溪",
    ),
    RefundRecord(
        "RF250309010",
        "TK250309020",
        "宋屿白",
        "不想要了",
        "冲动下单",
        "¥94.00",
        94.0,
        "已拒绝",
        "2026-03-09 08:58",
        "厨房去油清洁泡泡",
        "¥94.00",
        "已发货",
        "华东仓",
        "买家在快递揽收后申请仅退款，理由为临时不需要，但无质量问题。",
        ("mock/refund/no_need_1.png",),
        (
            RefundHistoryEntry("08:58", "买家提交申请", "无质量问题，仅表示不想要。", "warning"),
            RefundHistoryEntry("09:10", "客服判定", "订单已发货且不满足仅退款条件。", "info"),
            RefundHistoryEntry("09:16", "拒绝申请", "建议签收后走退货退款。", "error"),
        ),
        "已拒绝，仅保留沟通记录并提供规范退货路径。",
        "规则拒绝",
        "售后二组-见山",
    ),
    RefundRecord(
        "RF250309011",
        "TK250309021",
        "沈青禾",
        "色差问题",
        "颜色偏差较大",
        "¥439.00",
        439.0,
        "待审核",
        "2026-03-09 12:18",
        "软底轻跑运动鞋",
        "¥439.00",
        "已签收",
        "华中仓",
        "买家认为鞋面蓝色偏灰，与详情页示意不一致，上传自然光与室内光照片。",
        ("mock/refund/shoe_1.png", "mock/refund/shoe_2.png"),
        (
            RefundHistoryEntry("12:18", "买家提交申请", "描述颜色偏差。", "warning"),
            RefundHistoryEntry("12:24", "客服收集图片", "已收集两组对比图。", "info"),
        ),
        "建议判断是否可部分补偿挽留，若失败则按退货退款处理。",
        "高客单需挽留",
        "客服挽回-知遥",
    ),
    RefundRecord(
        "RF250309012",
        "TK250309022",
        "陆时雨",
        "赠品缺失",
        "活动赠品未收到",
        "¥125.00",
        125.0,
        "处理中",
        "2026-03-09 10:32",
        "氨基酸净透洁面慕斯",
        "¥125.00",
        "已签收",
        "华南仓",
        "商品无问题，但买家强调页面承诺赠送旅行装未随单寄出，要求退差价或补发。",
        ("mock/refund/gift_missing_1.png", "mock/refund/gift_missing_2.png"),
        (
            RefundHistoryEntry("10:32", "买家提交申请", "主诉赠品缺失。", "warning"),
            RefundHistoryEntry("10:40", "运营复核活动", "确认该时段活动确有赠品承诺。", "info"),
            RefundHistoryEntry("11:02", "待方案确认", "补发赠品或补偿优惠券待决策。", "warning"),
        ),
        "建议优先补发赠品，避免整单退款。",
        "可挽回",
        "运营协同-予安",
    ),
)


STATUS_OPTIONS = ("全部", "待审核", "已同意", "已拒绝", "处理中")
REASON_OPTIONS = ("全部", "尺码问题", "商品破损", "质量争议", "发货延迟", "不想要了", "少件漏发", "赠品缺失", "色差问题", "地址异常", "重复下单", "体验不符")
AMOUNT_OPTIONS = ("0", "50", "100", "150", "200", "300", "500")


class RefundProcessingPage(BasePage):
    """退款处理页面，提供退款队列、审核详情、证据与趋势分析。"""

    default_route_id: RouteId = RouteId("refund_processing")
    default_display_name: str = "退款处理"
    default_icon_name: str = "assignment_return"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._status_filter: str = "全部"
        self._reason_filter: str = "全部"
        self._min_amount: float = 0.0
        self._search_text: str = ""
        self._selected_index: int = 0
        self._metric_cards: list[KPICard] = []

        self._page_container: PageContainer | None = None
        self._search_bar: SearchBar | None = None
        self._status_filter_widget: FilterDropdown | None = None
        self._reason_filter_widget: FilterDropdown | None = None
        self._amount_filter_widget: FilterDropdown | None = None
        self._refresh_button: PrimaryButton | None = None
        self._summary_badge: StatusBadge | None = None
        self._summary_label: QLabel | None = None
        self._refund_table: DataTable | None = None
        self._detail_title: QLabel | None = None
        self._detail_status_badge: StatusBadge | None = None
        self._order_info_label: QLabel | None = None
        self._reason_info_label: QLabel | None = None
        self._owner_info_label: QLabel | None = None
        self._evidence_grid: ImageGrid | None = None
        self._history_timeline: TimelineWidget | None = None
        self._note_editor: ThemedTextEdit | None = None
        self._approve_button: PrimaryButton | None = None
        self._reject_button: SecondaryButton | None = None
        self._feedback_badge: StatusBadge | None = None
        self._feedback_label: QLabel | None = None
        self._trend_chart: ChartWidget | None = None

        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        _call(self, "setObjectName", "refundProcessingPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._page_container = PageContainer(
            title=self.display_name,
            description="围绕退款审核、证据查看、处理建议与趋势复盘构建的售后决策工作台。",
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )

        self._build_action_bar()
        self._build_metric_section()
        self._build_filter_section()
        self._build_main_split()
        self._build_trend_section()

        self.layout.addWidget(self._page_container)
        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_action_bar(self) -> None:
        if self._page_container is None:
            return
        host = QWidget(self._page_container)
        _call(host, "setObjectName", "refundProcessingActionBar")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self._search_bar = SearchBar("搜索退款单号、订单号、买家或原因")
        _call(self._search_bar, "setMinimumWidth", 260)
        self._refresh_button = PrimaryButton("刷新退款队列", host, icon_text="↻")
        layout.addWidget(self._search_bar, 1)
        layout.addStretch(1)
        layout.addWidget(self._refresh_button)
        self._page_container.add_widget(host)

    def _build_metric_section(self) -> None:
        if self._page_container is None:
            return
        section = ContentSection("退款总览", icon="◉", parent=self._page_container)

        strip = QWidget(section)
        _call(strip, "setObjectName", "refundSummaryStrip")
        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(0, 0, 0, 0)
        strip_layout.setSpacing(SPACING_MD)
        self._summary_badge = StatusBadge("待审核优先", tone="warning", parent=strip)
        self._summary_label = QLabel("", strip)
        _call(self._summary_label, "setObjectName", "refundSummaryLabel")
        _call(self._summary_label, "setWordWrap", True)
        strip_layout.addWidget(self._summary_badge)
        strip_layout.addWidget(TagChip("支持快速审批", tone="brand", parent=strip))
        strip_layout.addWidget(self._summary_label, 1)
        section.add_widget(strip)

        row = QWidget(section)
        _call(row, "setObjectName", "refundMetricRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_MD)
        for metric in REFUND_METRICS:
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

    def _build_filter_section(self) -> None:
        if self._page_container is None:
            return
        section = ContentSection("筛选条件", icon="▣", parent=self._page_container)
        row = QWidget(section)
        _call(row, "setObjectName", "refundFilterRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self._status_filter_widget = FilterDropdown("处理状态", STATUS_OPTIONS[1:], parent=row)
        self._reason_filter_widget = FilterDropdown("原因分类", REASON_OPTIONS[1:], parent=row)
        self._amount_filter_widget = FilterDropdown("最低金额", AMOUNT_OPTIONS, include_all=False, parent=row)
        self._amount_filter_widget.set_current_text("0")

        layout.addWidget(self._status_filter_widget)
        layout.addWidget(self._reason_filter_widget)
        layout.addWidget(self._amount_filter_widget)
        layout.addStretch(1)
        section.add_widget(row)
        self._page_container.add_widget(section)

    def _build_main_split(self) -> None:
        if self._page_container is None:
            return
        split = SplitPanel(split_ratio=(0.55, 0.45), minimum_sizes=(520, 500), parent=self._page_container)
        split.set_widgets(self._build_queue_column(), self._build_detail_column())
        self._page_container.add_widget(split)

    def _build_queue_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("退款队列", icon="◌", parent=host)
        section.add_widget(
            InfoCard(
                title="审核建议",
                description="优先处理高金额、高客单和商品破损类退款，尽量在同一工作班次完成定责与回复。",
                icon="⚠",
                action_text="查看风险分级",
                parent=section,
            )
        )
        self._refund_table = DataTable(headers=REFUND_TABLE_HEADERS, page_size=8, empty_text="当前筛选下暂无退款记录", parent=section)
        section.add_widget(self._refund_table)
        layout.addWidget(section)
        return host

    def _build_detail_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        section = ContentSection("退款详情", icon="✦", parent=host)

        header_card = QFrame(section)
        _call(header_card, "setObjectName", "refundDetailHeaderCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_SM)
        title_row = QHBoxLayout()
        title_row.setSpacing(SPACING_MD)
        self._detail_title = QLabel("", header_card)
        _call(self._detail_title, "setObjectName", "refundDetailTitle")
        self._detail_status_badge = StatusBadge("", tone="neutral", parent=header_card)
        title_row.addWidget(self._detail_title, 1)
        title_row.addWidget(self._detail_status_badge)
        header_layout.addLayout(title_row)
        section.add_widget(header_card)

        order_card = QFrame(section)
        _call(order_card, "setObjectName", "refundDetailInfoCard")
        order_layout = QVBoxLayout(order_card)
        order_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        order_layout.setSpacing(SPACING_SM)
        order_layout.addWidget(self._create_card_title("原订单信息", order_card))
        self._order_info_label = QLabel("", order_card)
        _call(self._order_info_label, "setObjectName", "refundDetailBody")
        _call(self._order_info_label, "setWordWrap", True)
        order_layout.addWidget(self._order_info_label)
        reason_card = QFrame(section)
        _call(reason_card, "setObjectName", "refundDetailInfoCard")
        reason_layout = QVBoxLayout(reason_card)
        reason_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        reason_layout.setSpacing(SPACING_SM)
        reason_layout.addWidget(self._create_card_title("退款原因", reason_card))
        self._reason_info_label = QLabel("", reason_card)
        _call(self._reason_info_label, "setObjectName", "refundDetailBody")
        _call(self._reason_info_label, "setWordWrap", True)
        reason_layout.addWidget(self._reason_info_label)

        info_row = QWidget(section)
        info_row_layout = QHBoxLayout(info_row)
        info_row_layout.setContentsMargins(0, 0, 0, 0)
        info_row_layout.setSpacing(SPACING_XL)
        info_row_layout.addWidget(order_card, 1)
        info_row_layout.addWidget(reason_card, 1)
        section.add_widget(info_row)

        owner_card = QFrame(section)
        _call(owner_card, "setObjectName", "refundDetailInfoCard")
        owner_layout = QVBoxLayout(owner_card)
        owner_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        owner_layout.setSpacing(SPACING_SM)
        owner_layout.addWidget(self._create_card_title("当前处理建议", owner_card))
        self._owner_info_label = QLabel("", owner_card)
        _call(self._owner_info_label, "setObjectName", "refundDetailBody")
        _call(self._owner_info_label, "setWordWrap", True)
        owner_layout.addWidget(self._owner_info_label)
        history_card = QFrame(section)
        _call(history_card, "setObjectName", "refundDetailInfoCard")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        history_layout.setSpacing(SPACING_SM)
        history_layout.addWidget(self._create_card_title("处理历史", history_card))
        self._history_timeline = TimelineWidget(history_card)
        history_layout.addWidget(self._history_timeline)

        support_row = QWidget(section)
        support_row_layout = QHBoxLayout(support_row)
        support_row_layout.setContentsMargins(0, 0, 0, 0)
        support_row_layout.setSpacing(SPACING_XL)
        support_row_layout.addWidget(owner_card, 1)
        support_row_layout.addWidget(history_card, 1)
        section.add_widget(support_row)

        evidence_card = QFrame(section)
        _call(evidence_card, "setObjectName", "refundDetailInfoCard")
        evidence_layout = QVBoxLayout(evidence_card)
        evidence_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        evidence_layout.setSpacing(SPACING_SM)
        evidence_layout.addWidget(self._create_card_title("证据图片", evidence_card))
        self._evidence_grid = ImageGrid(columns=3, parent=evidence_card)
        evidence_layout.addWidget(self._evidence_grid)
        section.add_widget(evidence_card)

        action_card = QFrame(section)
        _call(action_card, "setObjectName", "refundDetailInfoCard")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        action_layout.setSpacing(SPACING_MD)
        action_layout.addWidget(self._create_card_title("快速处理", action_card))
        self._note_editor = ThemedTextEdit("处理备注", "输入同意 / 拒绝说明或补充协同要求", action_card)
        action_layout.addWidget(self._note_editor)

        button_row = QHBoxLayout()
        button_row.setSpacing(SPACING_MD)
        self._approve_button = PrimaryButton("快速同意", action_card, icon_text="✓")
        self._reject_button = SecondaryButton("快速拒绝", action_card, icon_text="✕")
        button_row.addWidget(self._approve_button)
        button_row.addWidget(self._reject_button)
        action_layout.addLayout(button_row)

        feedback_row = QHBoxLayout()
        feedback_row.setSpacing(SPACING_MD)
        self._feedback_badge = StatusBadge("等待处理", tone="neutral", parent=action_card)
        self._feedback_label = QLabel("可在当前详情内快速模拟审批动作，并即时更新建议与历史。", action_card)
        _call(self._feedback_label, "setObjectName", "refundDetailBody")
        _call(self._feedback_label, "setWordWrap", True)
        feedback_row.addWidget(self._feedback_badge)
        feedback_row.addWidget(self._feedback_label, 1)
        action_layout.addLayout(feedback_row)
        section.add_widget(action_card)

        layout.addWidget(section)
        return host

    def _build_trend_section(self) -> None:
        if self._page_container is None:
            return
        section = ContentSection("退款趋势分析", icon="☍", parent=self._page_container)
        section.add_widget(
            InfoCard(
                title="趋势观察",
                description="近 7 日退款峰值集中在尺码问题与破损问题，发货延迟类已明显收敛。",
                icon="◎",
                action_text="查看周报摘要",
                parent=section,
            )
        )
        self._trend_chart = ChartWidget(
            chart_type="bar",
            title="近 7 日退款申请量",
            labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"),
            data=(28, 34, 31, 39, 36, 42, 33),
            unit="单",
            parent=section,
        )
        _call(self._trend_chart, "setMinimumHeight", 280)
        section.add_widget(self._trend_chart)
        self._page_container.add_widget(section)

    def _create_card_title(self, text: str, parent: QWidget) -> QLabel:
        label = QLabel(text, parent)
        _call(label, "setObjectName", "refundCardTitle")
        return label

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._on_search_changed)
        if self._status_filter_widget is not None:
            _connect(self._status_filter_widget.filter_changed, self._on_status_changed)
        if self._reason_filter_widget is not None:
            _connect(self._reason_filter_widget.filter_changed, self._on_reason_changed)
        if self._amount_filter_widget is not None:
            _connect(self._amount_filter_widget.filter_changed, self._on_amount_changed)
        if self._refund_table is not None:
            _connect(self._refund_table.row_selected, self._select_refund)
        if self._refresh_button is not None:
            _connect(getattr(self._refresh_button, "clicked", None), self._refresh_queue)
        if self._approve_button is not None:
            _connect(getattr(self._approve_button, "clicked", None), self._approve_current)
        if self._reject_button is not None:
            _connect(getattr(self._reject_button, "clicked", None), self._reject_current)

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#refundProcessingPage {{
                background: transparent;
            }}
            QWidget#refundSummaryStrip,
            QWidget#refundFilterRow {{
                background-color: rgba(0, 242, 234, 0.05);
                border: 1px solid rgba(0, 242, 234, 0.12);
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px;
            }}
            QLabel#refundSummaryLabel,
            QLabel#refundDetailBody {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.55;
            }}
            QLabel#refundDetailTitle,
            QLabel#refundCardTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#refundDetailHeaderCard,
            QFrame#refundDetailInfoCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )

    def _filtered_records(self) -> list[RefundRecord]:
        result: list[RefundRecord] = []
        for record in REFUND_RECORDS:
            if self._status_filter != "全部" and record.status != self._status_filter:
                continue
            if self._reason_filter != "全部" and record.reason_category != self._reason_filter:
                continue
            if record.amount_value < self._min_amount:
                continue
            if self._search_text:
                haystack = " ".join(
                    (
                        record.refund_id,
                        record.order_id,
                        record.buyer_name,
                        record.reason_title,
                        record.product_name,
                        record.note_hint,
                    )
                ).lower()
                if self._search_text not in haystack:
                    continue
            result.append(record)
        return result

    def _refresh_all_views(self) -> None:
        records = self._filtered_records()
        self._refresh_summary(records)
        self._refresh_table(records)
        self._refresh_detail(records)
        self._refresh_trend(records)

    def _refresh_summary(self, records: list[RefundRecord]) -> None:
        if self._summary_label is not None:
            _call(self._summary_label, "setText", f"当前筛选命中 {len(records)} 笔退款申请，建议优先处理高金额、破损与质量争议类单据。")
        if self._summary_badge is not None:
            tone = "warning" if any(item.status == "待审核" for item in records) else "success"
            self._summary_badge.set_tone(tone)
            _call(self._summary_badge, "setText", f"当前队列 {len(records)} 笔")

    def _refresh_table(self, records: list[RefundRecord]) -> None:
        if self._refund_table is None:
            return
        self._refund_table.set_rows([item.to_row() for item in records])
        if records:
            self._selected_index = min(self._selected_index, len(records) - 1)
            self._refund_table.select_absolute_row(self._selected_index)
        else:
            self._selected_index = 0

    def _refresh_detail(self, records: list[RefundRecord]) -> None:
        if not records:
            self._set_empty_detail()
            return
        record = records[max(0, min(self._selected_index, len(records) - 1))]
        if self._detail_title is not None:
            _call(self._detail_title, "setText", f"{record.refund_id}｜{record.product_name}")
        if self._detail_status_badge is not None:
            _call(self._detail_status_badge, "setText", record.status)
            tone = self._status_tone(record.status)
            self._detail_status_badge.set_tone(tone)
        if self._order_info_label is not None:
            _call(
                self._order_info_label,
                "setText",
                f"订单号：{record.order_id}\n买家：{record.buyer_name}\n原订单金额：{record.order_amount_text}\n物流状态：{record.shipping_status}\n仓库：{record.warehouse}",
            )
        if self._reason_info_label is not None:
            _call(
                self._reason_info_label,
                "setText",
                f"原因分类：{record.reason_category}\n退款原因：{record.reason_title}\n退款金额：{record.amount_text}\n详细说明：{record.reason_detail}",
            )
        if self._owner_info_label is not None:
            _call(
                self._owner_info_label,
                "setText",
                f"处理标签：{record.severity_tag}\n当前负责人：{record.owner_name}\n建议说明：{record.note_hint}",
            )
        if self._evidence_grid is not None:
            self._evidence_grid.set_items(record.evidence_images)
        if self._history_timeline is not None:
            self._history_timeline.set_events([item.to_event() for item in record.processing_history])
        if self._note_editor is not None:
            self._note_editor.setPlainText(record.note_hint)

    def _refresh_trend(self, records: list[RefundRecord]) -> None:
        if self._trend_chart is None:
            return
        count_by_reason: dict[str, int] = {}
        for record in records:
            count_by_reason[record.reason_category] = count_by_reason.get(record.reason_category, 0) + 1
        if not count_by_reason:
            self._trend_chart.set_data([], [])
            return
        labels = list(count_by_reason.keys())[:6]
        values = [count_by_reason[label] for label in labels]
        self._trend_chart.set_data(values, labels)
        self._trend_chart.set_unit("笔")
        setattr(self._trend_chart, "_title", "当前筛选下退款原因分布")
        _call(self._trend_chart, "update")

    def _set_empty_detail(self) -> None:
        if self._detail_title is not None:
            _call(self._detail_title, "setText", "暂无匹配退款单")
        if self._detail_status_badge is not None:
            _call(self._detail_status_badge, "setText", "空状态")
            self._detail_status_badge.set_tone("neutral")
        for widget, text in (
            (self._order_info_label, "暂无原订单信息。"),
            (self._reason_info_label, "暂无退款原因。"),
            (self._owner_info_label, "暂无处理建议。"),
        ):
            if widget is not None:
                _call(widget, "setText", text)
        if self._evidence_grid is not None:
            self._evidence_grid.set_items([])
        if self._history_timeline is not None:
            self._history_timeline.set_events([])
        if self._note_editor is not None:
            self._note_editor.setPlainText("暂无备注")

    def _status_tone(self, status: str) -> BadgeTone:
        if status == "待审核":
            return "warning"
        if status == "已同意":
            return "success"
        if status == "已拒绝":
            return "error"
        if status == "处理中":
            return "brand"
        return "neutral"

    def _on_search_changed(self, text: str) -> None:
        self._search_text = text.strip().lower()
        self._selected_index = 0
        self._refresh_all_views()

    def _on_status_changed(self, text: str) -> None:
        self._status_filter = text or "全部"
        self._selected_index = 0
        self._refresh_all_views()

    def _on_reason_changed(self, text: str) -> None:
        self._reason_filter = text or "全部"
        self._selected_index = 0
        self._refresh_all_views()

    def _on_amount_changed(self, text: str) -> None:
        self._min_amount = float(text or 0)
        self._selected_index = 0
        self._refresh_all_views()

    def _select_refund(self, index: int) -> None:
        self._selected_index = index
        self._refresh_detail(self._filtered_records())

    def _refresh_queue(self) -> None:
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone("brand")
            _call(self._feedback_badge, "setText", "队列已刷新")
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", "已重新拉取退款样本，建议优先审查高金额与高客单退款请求。")
        self._refresh_all_views()

    def _approve_current(self) -> None:
        record = self._current_record()
        if record is None:
            return
        note_text = self._note_editor.toPlainText() if self._note_editor is not None else ""
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone("success")
            _call(self._feedback_badge, "setText", "已模拟同意")
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", f"已同意 {record.refund_id}，备注：{note_text or record.note_hint}")
        if self._history_timeline is not None:
            events = [item.to_event() for item in record.processing_history]
            events.append({"timestamp": "刚刚", "title": "运营同意退款", "content": note_text or record.note_hint, "type": "success"})
            self._history_timeline.set_events(events)

    def _reject_current(self) -> None:
        record = self._current_record()
        if record is None:
            return
        note_text = self._note_editor.toPlainText() if self._note_editor is not None else ""
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone("error")
            _call(self._feedback_badge, "setText", "已模拟拒绝")
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", f"已拒绝 {record.refund_id}，建议回复买家：{note_text or '请走退货退款路径并补充必要证据。'}")
        if self._history_timeline is not None:
            events = [item.to_event() for item in record.processing_history]
            events.append({"timestamp": "刚刚", "title": "运营拒绝申请", "content": note_text or "建议补充证据后再提交。", "type": "error"})
            self._history_timeline.set_events(events)

    def _current_record(self) -> RefundRecord | None:
        records = self._filtered_records()
        if not records:
            return None
        return records[max(0, min(self._selected_index, len(records) - 1))]

    def on_activated(self) -> None:
        self._refresh_all_views()

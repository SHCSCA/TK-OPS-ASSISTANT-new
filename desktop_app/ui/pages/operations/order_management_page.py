# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""订单管理原型页面。"""

from dataclasses import dataclass
from typing import Any, Literal, cast

from ....core.qt import Qt
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
)
from ...components.inputs import (
    BUTTON_HEIGHT,
    DateRangePicker,
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
class OrderMetric:
    """订单管理 KPI。"""

    title: str
    value: str
    trend: TrendDirection
    percentage: str
    caption: str
    sparkline: tuple[float, ...]


@dataclass(frozen=True)
class OrderTimelineEntry:
    """订单处理时间线。"""

    time_text: str
    title: str
    detail: str
    level: str


@dataclass(frozen=True)
class OrderRecord:
    """订单表格记录。"""

    order_id: str
    buyer_name: str
    product_name: str
    category: str
    amount_text: str
    amount_value: float
    status: str
    date_text: str
    channel: str
    region: str
    buyer_phone: str
    buyer_level: str
    address: str
    shipping_text: str
    warehouse: str
    package_count: str
    note: str
    tags: tuple[str, ...]
    items: tuple[tuple[str, str, str], ...]
    timeline: tuple[OrderTimelineEntry, ...]
    action_hint: str

    def to_row(self) -> list[str]:
        return [
            self.order_id,
            self.buyer_name,
            self.product_name,
            self.amount_text,
            self.status,
            self.date_text,
            self.action_hint,
        ]


@dataclass(frozen=True)
class BatchActionRecord:
    """批量操作配置。"""

    title: str
    tone: BadgeTone
    feedback: str


ORDER_TABLE_HEADERS = ["订单号", "买家", "商品", "金额", "状态", "下单时间", "动作建议"]


ORDER_METRICS: tuple[OrderMetric, ...] = (
    OrderMetric("待处理", "186", "up", "+12 单", "午后新增待审单较多", (82, 88, 96, 104, 118, 132, 186)),
    OrderMetric("已发货", "1,248", "up", "+8.5%", "仓配吞吐保持稳定", (880, 930, 1012, 1084, 1140, 1196, 1248)),
    OrderMetric("已完成", "3,964", "up", "+6.1%", "复购客群持续拉动", (3200, 3330, 3492, 3608, 3720, 3856, 3964)),
    OrderMetric("异常订单", "42", "down", "-9 单", "支付超时与地址异常下降", (68, 64, 60, 56, 52, 48, 42)),
)


BATCH_ACTIONS: tuple[BatchActionRecord, ...] = (
    BatchActionRecord("批量发货", "success", "已将当前筛选结果中的待发货订单推送到仓配出库池。"),
    BatchActionRecord("批量标记优先", "brand", "已将高金额与高时效风险订单标记为优先处理。"),
    BatchActionRecord("批量备注", "warning", "已为当前订单批量添加运营备注，方便客服与仓配同步。"),
)


ORDER_RECORDS: tuple[OrderRecord, ...] = (
    OrderRecord(
        "TK250309001",
        "林若溪",
        "柔雾持妆粉底液 30ml",
        "美妆个护",
        "¥169.00",
        169.0,
        "待处理",
        "2026-03-09 09:12",
        "商城推荐",
        "上海",
        "138****1203",
        "高价值会员",
        "上海市浦东新区张江路 88 号 6 栋 1202",
        "待分配快递",
        "华东仓",
        "1 包裹",
        "用户留言需确认色号 02 自然色。",
        ("高客单", "需客服确认"),
        (("粉底液 30ml", "1 件", "¥169.00"),),
        (
            OrderTimelineEntry("09:12", "订单创建", "用户通过商城推荐页下单。", "info"),
            OrderTimelineEntry("09:14", "支付成功", "支付渠道为支付宝。", "success"),
            OrderTimelineEntry("09:18", "待人工确认", "买家留言需确认色号。", "warning"),
        ),
        "优先确认买家留言",
    ),
    OrderRecord(
        "TK250309002",
        "周牧遥",
        "高弹亲肤鲨鱼裤",
        "服饰内衣",
        "¥199.00",
        199.0,
        "待处理",
        "2026-03-09 09:26",
        "短视频挂车",
        "杭州",
        "137****2289",
        "新客",
        "浙江省杭州市余杭区创景路 19 号 2 幢 901",
        "等待尺码核实",
        "华东仓",
        "1 包裹",
        "尺码在 M/L 间摇摆，建议客服回访。",
        ("尺码敏感", "售前咨询未闭环"),
        (("鲨鱼裤 黑色 L", "1 件", "¥199.00"),),
        (
            OrderTimelineEntry("09:26", "订单创建", "来自达人短视频引流。", "info"),
            OrderTimelineEntry("09:28", "支付成功", "用户使用店铺优惠券。", "success"),
            OrderTimelineEntry("09:31", "尺码待确认", "客服尚未完成回访。", "warning"),
        ),
        "先核尺码再发货",
    ),
    OrderRecord(
        "TK250309003",
        "许知暖",
        "云感纯棉四件套",
        "家纺家居",
        "¥399.00",
        399.0,
        "已发货",
        "2026-03-09 08:44",
        "搜索流量",
        "北京",
        "139****5012",
        "老客",
        "北京市朝阳区酒仙桥北路 18 号 4 单元 602",
        "顺丰已揽收，预计明日送达",
        "华北仓",
        "1 包裹",
        "用户要求尽量避开午休派送。",
        ("高客单", "履约平稳"),
        (("四件套 奶油白 1.8m", "1 件", "¥399.00"),),
        (
            OrderTimelineEntry("08:44", "订单创建", "搜索词“纯棉四件套”转化。", "info"),
            OrderTimelineEntry("08:46", "支付成功", "微信支付。", "success"),
            OrderTimelineEntry("10:05", "仓库拣货", "华北仓已完成拣货打包。", "success"),
            OrderTimelineEntry("11:18", "快递揽收", "顺丰已揽收。", "success"),
        ),
        "留意签收评价",
    ),
    OrderRecord(
        "TK250309004",
        "陈闻月",
        "氨基酸净透洁面慕斯",
        "美妆个护",
        "¥125.00",
        125.0,
        "已完成",
        "2026-03-08 21:35",
        "商品卡推荐",
        "广州",
        "136****8711",
        "回购会员",
        "广东省广州市天河区体育东路 100 号 2301",
        "已签收",
        "华南仓",
        "1 包裹",
        "回购客，偏好搭配补水喷雾仪。",
        ("高复购", "可做加购推荐"),
        (("洁面慕斯 150ml", "1 件", "¥125.00"),),
        (
            OrderTimelineEntry("03-08 21:35", "订单创建", "来自商品卡推荐。", "info"),
            OrderTimelineEntry("03-08 21:36", "支付成功", "微信支付。", "success"),
            OrderTimelineEntry("03-09 09:12", "签收完成", "用户已签收。", "success"),
        ),
        "可触发复购关怀",
    ),
    OrderRecord(
        "TK250309005",
        "顾南枝",
        "轻氧羽感防晒乳",
        "美妆个护",
        "¥120.00",
        120.0,
        "异常订单",
        "2026-03-09 10:02",
        "商城推荐",
        "南京",
        "135****6721",
        "新客",
        "江苏省南京市建邺区江东中路 66 号 701",
        "待校验地址",
        "华东仓",
        "1 包裹",
        "楼栋信息重复，快递面单校验失败。",
        ("地址异常", "需人工修正"),
        (("防晒乳 50ml", "1 件", "¥120.00"),),
        (
            OrderTimelineEntry("10:02", "订单创建", "商城推荐流量。", "info"),
            OrderTimelineEntry("10:04", "支付成功", "支付宝支付。", "success"),
            OrderTimelineEntry("10:16", "地址校验失败", "楼栋字段重复。", "error"),
        ),
        "先修正地址",
    ),
    OrderRecord(
        "TK250309006",
        "宋屿白",
        "厨房去油清洁泡泡",
        "家居日用",
        "¥94.00",
        94.0,
        "待处理",
        "2026-03-09 10:18",
        "店铺首页",
        "苏州",
        "134****2201",
        "老客",
        "江苏省苏州市工业园区金鸡湖大道 27 号 1503",
        "待仓库确认赠品",
        "华东仓",
        "1 包裹",
        "赠品库存不足，需判断是否替换。",
        ("赠品确认", "老客关怀"),
        (("清洁泡泡 2 瓶装", "1 件", "¥94.00"),),
        (
            OrderTimelineEntry("10:18", "订单创建", "店铺首页自营流量。", "info"),
            OrderTimelineEntry("10:20", "支付成功", "微信支付。", "success"),
            OrderTimelineEntry("10:36", "赠品待确认", "仓库反馈赠品库存不足。", "warning"),
        ),
        "先定赠品替换方案",
    ),
    OrderRecord(
        "TK250309007",
        "沈青禾",
        "保温吸管杯礼盒版",
        "百货文创",
        "¥124.00",
        124.0,
        "已发货",
        "2026-03-09 07:58",
        "搜索流量",
        "成都",
        "133****9908",
        "新客",
        "四川省成都市武侯区天府大道中段 1366 号 1208",
        "圆通在途，预计 2 天送达",
        "西南仓",
        "1 包裹",
        "礼盒包装需避免挤压。",
        ("礼赠场景", "易出好评"),
        (("吸管杯 礼盒版", "1 件", "¥124.00"),),
        (
            OrderTimelineEntry("07:58", "订单创建", "搜索词“礼盒保温杯”。", "info"),
            OrderTimelineEntry("08:01", "支付成功", "支付宝支付。", "success"),
            OrderTimelineEntry("09:48", "已发货", "西南仓完成出库。", "success"),
        ),
        "关注签收时效",
    ),
    OrderRecord(
        "TK250309008",
        "裴言川",
        "软底轻跑运动鞋",
        "鞋靴箱包",
        "¥439.00",
        439.0,
        "已完成",
        "2026-03-08 16:12",
        "短视频挂车",
        "武汉",
        "132****4010",
        "高价值会员",
        "湖北省武汉市洪山区关山大道 236 号 1605",
        "已签收",
        "华中仓",
        "1 包裹",
        "用户已追加评价，尺码合适。",
        ("高客单", "好评已回流"),
        (("运动鞋 白蓝 42", "1 双", "¥439.00"),),
        (
            OrderTimelineEntry("03-08 16:12", "订单创建", "短视频挂车转化。", "info"),
            OrderTimelineEntry("03-08 16:15", "支付成功", "微信支付。", "success"),
            OrderTimelineEntry("03-09 12:08", "签收完成", "用户好评已同步。", "success"),
        ),
        "可加入好评素材池",
    ),
    OrderRecord(
        "TK250309009",
        "夏知微",
        "智能暖腹热敷腰带",
        "健康护理",
        "¥219.00",
        219.0,
        "异常订单",
        "2026-03-09 11:08",
        "商品卡推荐",
        "郑州",
        "131****7832",
        "新客",
        "河南省郑州市金水区农业路 92 号 1006",
        "支付超时待核销",
        "华中仓",
        "1 包裹",
        "系统支付回调延迟，状态未最终确认。",
        ("支付异常", "需财务核对"),
        (("暖腹腰带 标准版", "1 件", "¥219.00"),),
        (
            OrderTimelineEntry("11:08", "订单创建", "商品卡推荐。", "info"),
            OrderTimelineEntry("11:10", "支付处理中", "第三方回调延迟。", "warning"),
            OrderTimelineEntry("11:24", "异常挂起", "待财务核销支付状态。", "error"),
        ),
        "核对支付回调",
    ),
    OrderRecord(
        "TK250309010",
        "程见鹿",
        "婴童柔护湿巾 80 抽 5 包",
        "母婴用品",
        "¥110.00",
        110.0,
        "已发货",
        "2026-03-09 10:52",
        "店铺首页",
        "合肥",
        "130****2219",
        "回购会员",
        "安徽省合肥市蜀山区望江西路 98 号 2 栋 902",
        "中通在途，预计后日送达",
        "华东仓",
        "1 包裹",
        "老客二次复购，可跟进组合购。",
        ("母婴复购", "可推荐组合购"),
        (("湿巾 80 抽 5 包", "1 件", "¥110.00"),),
        (
            OrderTimelineEntry("10:52", "订单创建", "店铺首页流量。", "info"),
            OrderTimelineEntry("10:53", "支付成功", "微信支付。", "success"),
            OrderTimelineEntry("12:02", "仓库出库", "已完成揽收。", "success"),
        ),
        "签收后推组合购",
    ),
    OrderRecord(
        "TK250309011",
        "陆时雨",
        "便携补水喷雾仪",
        "美妆个护",
        "¥99.00",
        99.0,
        "待处理",
        "2026-03-09 11:32",
        "搜索流量",
        "福州",
        "188****5530",
        "新客",
        "福建省福州市鼓楼区五四路 109 号 803",
        "待拣货",
        "华南仓",
        "1 包裹",
        "用户留言希望加急发货。",
        ("加急", "需优先出库"),
        (("补水喷雾仪 樱粉", "1 件", "¥99.00"),),
        (
            OrderTimelineEntry("11:32", "订单创建", "搜索词“补水喷雾仪”。", "info"),
            OrderTimelineEntry("11:33", "支付成功", "支付宝支付。", "success"),
            OrderTimelineEntry("11:35", "买家留言", "希望今天内出库。", "warning"),
        ),
        "加入加急队列",
    ),
    OrderRecord(
        "TK250309012",
        "温景岚",
        "居家多效除菌喷雾 2 瓶装",
        "家居日用",
        "¥114.00",
        114.0,
        "已完成",
        "2026-03-08 19:26",
        "商城推荐",
        "长沙",
        "189****3101",
        "老客",
        "湖南省长沙市岳麓区梅溪湖路 229 号 1 栋 1501",
        "已签收",
        "华中仓",
        "1 包裹",
        "用户对包装完整度满意。",
        ("老客", "评价正向"),
        (("除菌喷雾 2 瓶装", "1 件", "¥114.00"),),
        (
            OrderTimelineEntry("03-08 19:26", "订单创建", "商城推荐页转化。", "info"),
            OrderTimelineEntry("03-08 19:28", "支付成功", "微信支付。", "success"),
            OrderTimelineEntry("03-09 10:41", "签收完成", "包装完整，用户反馈良好。", "success"),
        ),
        "可邀请晒单",
    ),
)


class OrderManagementPage(BasePage):
    """订单管理页，聚合筛选、批量动作和右侧订单详情。"""

    default_route_id: RouteId = RouteId("order_management")
    default_display_name: str = "订单管理"
    default_icon_name: str = "receipt_long"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._status_filter: str = "全部"
        self._category_filter: str = "全部"
        self._min_amount: float = 0.0
        self._max_amount: float = 999999.0
        self._search_text: str = ""
        self._selected_index: int = 0
        self._metric_cards: list[KPICard] = []
        self._batch_buttons: list[QPushButton] = []

        self._page_container: PageContainer | None = None
        self._search_bar: SearchBar | None = None
        self._date_picker: DateRangePicker | None = None
        self._status_dropdown: FilterDropdown | None = None
        self._category_dropdown: FilterDropdown | None = None
        self._min_amount_dropdown: FilterDropdown | None = None
        self._max_amount_dropdown: FilterDropdown | None = None
        self._export_button: PrimaryButton | None = None
        self._selection_badge: StatusBadge | None = None
        self._summary_label: QLabel | None = None
        self._orders_table: DataTable | None = None
        self._detail_header_title: QLabel | None = None
        self._detail_status_badge: StatusBadge | None = None
        self._detail_meta_label: QLabel | None = None
        self._buyer_info_label: QLabel | None = None
        self._items_info_label: QLabel | None = None
        self._shipping_info_label: QLabel | None = None
        self._timeline_info_label: QLabel | None = None
        self._tag_chips_host: QWidget | None = None
        self._tag_chips_layout: QHBoxLayout | None = None
        self._feedback_badge: StatusBadge | None = None
        self._feedback_label: QLabel | None = None

        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        _call(self, "setObjectName", "orderManagementPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._page_container = PageContainer(
            title=self.display_name,
            description="面向 TikTok Shop 店铺运营的订单工作台，聚合筛选、批量处理、履约跟踪与订单详情面板。",
            parent=self,
        )

        self._build_action_bar()
        self._build_metric_section()
        self._build_filter_section()
        self._build_main_split()

        self.layout.addWidget(self._page_container)
        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_action_bar(self) -> None:
        if self._page_container is None:
            return
        host = QWidget(self._page_container)
        _call(host, "setObjectName", "orderManagementActionBar")
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self._search_bar = SearchBar("搜索订单号、买家、商品或备注")
        _call(self._search_bar, "setMinimumWidth", 300)
        self._export_button = PrimaryButton("导出订单", host, icon_text="⇩")

        layout.addWidget(self._search_bar, 1)
        layout.addWidget(self._export_button)
        self._page_container.add_action(host)

    def _build_metric_section(self) -> None:
        if self._page_container is None:
            return
        section = ContentSection("订单状态概览", icon="◉", parent=self._page_container)

        strip = QWidget(section)
        _call(strip, "setObjectName", "orderManagementSummaryStrip")
        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(0, 0, 0, 0)
        strip_layout.setSpacing(SPACING_MD)
        self._selection_badge = StatusBadge("订单队列已加载", tone="brand", parent=strip)
        strip_layout.addWidget(self._selection_badge)
        strip_layout.addWidget(TagChip("支持批量处理", tone="info", parent=strip))
        self._summary_label = QLabel("", strip)
        _call(self._summary_label, "setObjectName", "orderManagementSummaryLabel")
        _call(self._summary_label, "setWordWrap", True)
        strip_layout.addWidget(self._summary_label, 1)
        section.add_widget(strip)

        row = QWidget(section)
        _call(row, "setObjectName", "orderManagementMetricRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_MD)
        for metric in ORDER_METRICS:
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
        section = ContentSection("筛选与批量操作", icon="▣", parent=self._page_container)

        filter_row = QWidget(section)
        _call(filter_row, "setObjectName", "orderManagementFilterRow")
        filter_layout = QHBoxLayout(filter_row)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(SPACING_MD)

        self._status_dropdown = FilterDropdown("订单状态", ["待处理", "已发货", "已完成", "异常订单"], parent=filter_row)
        self._category_dropdown = FilterDropdown("商品分类", ["美妆个护", "服饰内衣", "家纺家居", "家居日用", "鞋靴箱包", "健康护理", "母婴用品", "百货文创"], parent=filter_row)
        self._date_picker = DateRangePicker("日期范围", filter_row)
        self._min_amount_dropdown = FilterDropdown("最低金额", ["0", "100", "150", "200", "300"], include_all=False, parent=filter_row)
        self._max_amount_dropdown = FilterDropdown("最高金额", ["150", "200", "300", "500", "1000"], include_all=False, parent=filter_row)
        self._min_amount_dropdown.set_current_text("0")
        self._max_amount_dropdown.set_current_text("500")

        for widget in (
            self._status_dropdown,
            self._category_dropdown,
            self._date_picker,
            self._min_amount_dropdown,
            self._max_amount_dropdown,
        ):
            filter_layout.addWidget(widget)
        section.add_widget(filter_row)

        batch_row = QWidget(section)
        _call(batch_row, "setObjectName", "orderManagementBatchRow")
        batch_layout = QHBoxLayout(batch_row)
        batch_layout.setContentsMargins(0, 0, 0, 0)
        batch_layout.setSpacing(SPACING_MD)

        for item in BATCH_ACTIONS:
            button = QPushButton(item.title, batch_row)
            _call(button, "setObjectName", "orderManagementBatchButton")
            _call(button, "setProperty", "tone", item.tone)
            _call(button, "setMinimumHeight", BUTTON_HEIGHT)
            self._batch_buttons.append(button)
            batch_layout.addWidget(button)

        self._feedback_badge = StatusBadge("等待批量动作", tone="neutral", parent=batch_row)
        self._feedback_label = QLabel("当前支持对筛选后的订单模拟执行发货、标记优先与备注同步。", batch_row)
        _call(self._feedback_label, "setObjectName", "orderManagementFeedbackLabel")
        _call(self._feedback_label, "setWordWrap", True)

        batch_layout.addWidget(self._feedback_badge)
        batch_layout.addWidget(self._feedback_label, 1)
        section.add_widget(batch_row)
        self._page_container.add_widget(section)

    def _build_main_split(self) -> None:
        if self._page_container is None:
            return
        split = SplitPanel(split_ratio=(0.62, 0.38), minimum_sizes=(700, 420), parent=self._page_container)
        split.set_widgets(self._build_table_column(), self._build_detail_column())
        self._page_container.add_widget(split)

    def _build_table_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("订单列表", icon="◌", parent=host)
        section.add_widget(
            InfoCard(
                title="列表支持排序与联动详情",
                description="点击任意订单后，右侧将同步展示买家信息、商品明细、物流信息与处理时间线。",
                icon="☍",
                action_text="定位异常订单",
                parent=section,
            )
        )

        self._orders_table = DataTable(headers=ORDER_TABLE_HEADERS, page_size=8, empty_text="当前筛选条件下暂无订单", parent=section)
        section.add_widget(self._orders_table)
        layout.addWidget(section)
        return host

    def _build_detail_column(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("订单详情", icon="✦", parent=host)

        header_card = QFrame(section)
        _call(header_card, "setObjectName", "orderDetailHeaderCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        header_layout.setSpacing(SPACING_SM)

        title_row = QHBoxLayout()
        title_row.setSpacing(SPACING_MD)
        self._detail_header_title = QLabel("", header_card)
        _call(self._detail_header_title, "setObjectName", "orderDetailTitle")
        self._detail_status_badge = StatusBadge("", tone="neutral", parent=header_card)
        title_row.addWidget(self._detail_header_title, 1)
        title_row.addWidget(self._detail_status_badge)
        header_layout.addLayout(title_row)

        self._detail_meta_label = QLabel("", header_card)
        _call(self._detail_meta_label, "setObjectName", "orderDetailMeta")
        _call(self._detail_meta_label, "setWordWrap", True)
        header_layout.addWidget(self._detail_meta_label)

        self._tag_chips_host = QWidget(header_card)
        tag_layout = QHBoxLayout(self._tag_chips_host)
        _call(tag_layout, "setContentsMargins", 0, 0, 0, 0)
        _call(tag_layout, "setSpacing", SPACING_SM)
        self._tag_chips_layout = tag_layout
        header_layout.addWidget(self._tag_chips_host)
        section.add_widget(header_card)

        buyer_card = QFrame(section)
        _call(buyer_card, "setObjectName", "orderDetailInfoCard")
        buyer_layout = QVBoxLayout(buyer_card)
        buyer_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        buyer_layout.setSpacing(SPACING_SM)
        buyer_layout.addWidget(self._create_card_title("买家信息", buyer_card))
        self._buyer_info_label = QLabel("", buyer_card)
        _call(self._buyer_info_label, "setObjectName", "orderDetailBody")
        _call(self._buyer_info_label, "setWordWrap", True)
        buyer_layout.addWidget(self._buyer_info_label)
        section.add_widget(buyer_card)

        items_card = QFrame(section)
        _call(items_card, "setObjectName", "orderDetailInfoCard")
        items_layout = QVBoxLayout(items_card)
        items_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        items_layout.setSpacing(SPACING_SM)
        items_layout.addWidget(self._create_card_title("商品明细", items_card))
        self._items_info_label = QLabel("", items_card)
        _call(self._items_info_label, "setObjectName", "orderDetailBody")
        _call(self._items_info_label, "setWordWrap", True)
        items_layout.addWidget(self._items_info_label)
        section.add_widget(items_card)

        shipping_card = QFrame(section)
        _call(shipping_card, "setObjectName", "orderDetailInfoCard")
        shipping_layout = QVBoxLayout(shipping_card)
        shipping_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        shipping_layout.setSpacing(SPACING_SM)
        shipping_layout.addWidget(self._create_card_title("物流与履约", shipping_card))
        self._shipping_info_label = QLabel("", shipping_card)
        _call(self._shipping_info_label, "setObjectName", "orderDetailBody")
        _call(self._shipping_info_label, "setWordWrap", True)
        shipping_layout.addWidget(self._shipping_info_label)
        section.add_widget(shipping_card)

        timeline_card = QFrame(section)
        _call(timeline_card, "setObjectName", "orderDetailInfoCard")
        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        timeline_layout.setSpacing(SPACING_SM)
        timeline_layout.addWidget(self._create_card_title("处理时间线", timeline_card))
        self._timeline_info_label = QLabel("", timeline_card)
        _call(self._timeline_info_label, "setObjectName", "orderDetailBody")
        _call(self._timeline_info_label, "setWordWrap", True)
        timeline_layout.addWidget(self._timeline_info_label)
        section.add_widget(timeline_card)

        layout.addWidget(section)
        return host

    def _create_card_title(self, text: str, parent: QWidget) -> QLabel:
        label = QLabel(text, parent)
        _call(label, "setObjectName", "orderDetailCardTitle")
        return label

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._on_search_changed)
        if self._status_dropdown is not None:
            _connect(self._status_dropdown.filter_changed, self._on_status_changed)
        if self._category_dropdown is not None:
            _connect(self._category_dropdown.filter_changed, self._on_category_changed)
        if self._min_amount_dropdown is not None:
            _connect(self._min_amount_dropdown.filter_changed, self._on_min_amount_changed)
        if self._max_amount_dropdown is not None:
            _connect(self._max_amount_dropdown.filter_changed, self._on_max_amount_changed)
        if self._orders_table is not None:
            _connect(self._orders_table.row_selected, self._select_order)
        if self._export_button is not None:
            _connect(getattr(self._export_button, "clicked", None), self._export_orders)

        for index, button in enumerate(self._batch_buttons):
            _connect(getattr(button, "clicked", None), lambda current=index: self._run_batch_action(current))

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#orderManagementPage {{
                background: transparent;
            }}
            QWidget#orderManagementSummaryStrip,
            QWidget#orderManagementFilterRow,
            QWidget#orderManagementBatchRow {{
                background-color: rgba(0, 242, 234, 0.05);
                border: 1px solid rgba(0, 242, 234, 0.12);
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px;
            }}
            QLabel#orderManagementSummaryLabel,
            QLabel#orderManagementFeedbackLabel,
            QLabel#orderDetailMeta,
            QLabel#orderDetailBody {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.55;
            }}
            QLabel#orderDetailTitle,
            QLabel#orderDetailCardTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#orderDetailHeaderCard,
            QFrame#orderDetailInfoCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QPushButton#orderManagementBatchButton {{
                background-color: {colors.surface};
                color: {colors.text};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px {SPACING_XL}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#orderManagementBatchButton[tone="success"]:hover {{
                border-color: {_token('status.success')};
                color: {_token('status.success')};
            }}
            QPushButton#orderManagementBatchButton[tone="brand"]:hover {{
                border-color: {_token('brand.primary')};
                color: {_token('brand.primary')};
            }}
            QPushButton#orderManagementBatchButton[tone="warning"]:hover {{
                border-color: {_token('status.warning')};
                color: {_token('status.warning')};
            }}
            """,
        )

    def _filtered_orders(self) -> list[OrderRecord]:
        result: list[OrderRecord] = []
        for record in ORDER_RECORDS:
            if self._status_filter != "全部" and record.status != self._status_filter:
                continue
            if self._category_filter != "全部" and record.category != self._category_filter:
                continue
            if record.amount_value < self._min_amount or record.amount_value > self._max_amount:
                continue
            if self._search_text:
                haystack = " ".join(
                    (
                        record.order_id,
                        record.buyer_name,
                        record.product_name,
                        record.note,
                        record.action_hint,
                        record.region,
                    )
                ).lower()
                if self._search_text not in haystack:
                    continue
            result.append(record)
        return result

    def _refresh_all_views(self) -> None:
        orders = self._filtered_orders()
        self._refresh_summary(orders)
        self._refresh_table(orders)
        self._refresh_detail(orders)

    def _refresh_summary(self, orders: list[OrderRecord]) -> None:
        if self._summary_label is not None:
            _call(self._summary_label, "setText", f"当前筛选命中 {len(orders)} 笔订单，重点建议优先处理异常订单、买家留言与高客单待发货订单。")
        if self._selection_badge is not None:
            _call(self._selection_badge, "setText", f"当前命中 {len(orders)} 笔")
            self._selection_badge.set_tone("brand")

    def _refresh_table(self, orders: list[OrderRecord]) -> None:
        if self._orders_table is None:
            return
        self._orders_table.set_rows([item.to_row() for item in orders])
        if orders:
            self._selected_index = min(self._selected_index, len(orders) - 1)
            self._orders_table.select_absolute_row(self._selected_index)
        else:
            self._selected_index = 0

    def _refresh_detail(self, orders: list[OrderRecord]) -> None:
        if not orders:
            self._set_empty_detail()
            return
        record = orders[max(0, min(self._selected_index, len(orders) - 1))]
        if self._detail_header_title is not None:
            _call(self._detail_header_title, "setText", f"{record.order_id}｜{record.product_name}")
        if self._detail_status_badge is not None:
            _call(self._detail_status_badge, "setText", record.status)
            tone = self._status_tone(record.status)
            self._detail_status_badge.set_tone(tone)
        if self._detail_meta_label is not None:
            _call(
                self._detail_meta_label,
                "setText",
                f"买家：{record.buyer_name}｜渠道：{record.channel}｜区域：{record.region}｜下单时间：{record.date_text}｜金额：{record.amount_text}",
            )
        if self._buyer_info_label is not None:
            _call(
                self._buyer_info_label,
                "setText",
                f"会员等级：{record.buyer_level}\n联系电话：{record.buyer_phone}\n收货地址：{record.address}\n订单备注：{record.note}",
            )
        if self._items_info_label is not None:
            item_lines = [f"• {name}｜{qty}｜{price}" for name, qty, price in record.items]
            _call(self._items_info_label, "setText", "\n".join(item_lines))
        if self._shipping_info_label is not None:
            _call(
                self._shipping_info_label,
                "setText",
                f"仓库：{record.warehouse}\n包裹数：{record.package_count}\n履约状态：{record.shipping_text}\n运营建议：{record.action_hint}",
            )
        if self._timeline_info_label is not None:
            timeline_lines = [f"• {item.time_text}｜{item.title}｜{item.detail}" for item in record.timeline]
            _call(self._timeline_info_label, "setText", "\n".join(timeline_lines))
        self._refresh_tags(record.tags)

    def _refresh_tags(self, tags: tuple[str, ...]) -> None:
        if self._tag_chips_layout is None or self._tag_chips_host is None:
            return
        while getattr(self._tag_chips_layout, "count", lambda: 0)() > 0:
            item = self._tag_chips_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                _call(widget, "deleteLater")
        for index, tag in enumerate(tags):
            tone: BadgeTone = "brand" if index == 0 else "neutral"
            self._tag_chips_layout.addWidget(TagChip(tag, tone=tone, parent=self._tag_chips_host))
        self._tag_chips_layout.addStretch(1)

    def _set_empty_detail(self) -> None:
        if self._detail_header_title is not None:
            _call(self._detail_header_title, "setText", "暂无匹配订单")
        if self._detail_status_badge is not None:
            _call(self._detail_status_badge, "setText", "空状态")
            self._detail_status_badge.set_tone(cast(BadgeTone, "neutral"))
        for widget, text in (
            (self._detail_meta_label, "请调整筛选条件查看订单详情。"),
            (self._buyer_info_label, "暂无买家信息。"),
            (self._items_info_label, "暂无商品明细。"),
            (self._shipping_info_label, "暂无物流信息。"),
            (self._timeline_info_label, "暂无时间线。"),
        ):
            if widget is not None:
                _call(widget, "setText", text)
        self._refresh_tags(())

    def _status_tone(self, status: str) -> BadgeTone:
        if status == "待处理":
            return "warning"
        if status == "已发货":
            return "brand"
        if status == "已完成":
            return "success"
        if status == "异常订单":
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

    def _on_category_changed(self, text: str) -> None:
        self._category_filter = text or "全部"
        self._selected_index = 0
        self._refresh_all_views()

    def _on_min_amount_changed(self, text: str) -> None:
        self._min_amount = float(text or 0)
        if self._max_amount < self._min_amount:
            self._max_amount = self._min_amount
        self._selected_index = 0
        self._refresh_all_views()

    def _on_max_amount_changed(self, text: str) -> None:
        self._max_amount = float(text or 999999)
        if self._max_amount < self._min_amount:
            self._min_amount = self._max_amount
        self._selected_index = 0
        self._refresh_all_views()

    def _select_order(self, index: int) -> None:
        self._selected_index = index
        self._refresh_detail(self._filtered_orders())

    def _run_batch_action(self, index: int) -> None:
        if not (0 <= index < len(BATCH_ACTIONS)):
            return
        action = BATCH_ACTIONS[index]
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone(action.tone)
            _call(self._feedback_badge, "setText", action.title)
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", action.feedback)

    def _export_orders(self) -> None:
        orders = self._filtered_orders()
        if self._feedback_badge is not None:
            self._feedback_badge.set_tone(cast(BadgeTone, "brand"))
            _call(self._feedback_badge, "setText", "导出完成")
        if self._feedback_label is not None:
            _call(self._feedback_label, "setText", f"已模拟导出 {len(orders)} 笔订单，建议按异常优先级与仓库维度做二次复盘。")

    def on_activated(self) -> None:
        self._refresh_all_views()

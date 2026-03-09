# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""运营中心总览原型页面。"""

from dataclasses import dataclass
from typing import Any, Literal, cast

from ....core.qt import Qt
from ....core.types import RouteId
from ...components import (
    ActionCard,
    ChartWidget,
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
    TimelineWidget,
)
from ...components.inputs import (
    BUTTON_HEIGHT,
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
class OperationsMetric:
    """运营中心 KPI 数据。"""

    title: str
    value: str
    trend: TrendDirection
    percentage: str
    caption: str
    sparkline: tuple[float, ...]


@dataclass(frozen=True)
class ProductPerformanceRecord:
    """爆品榜单记录。"""

    rank: str
    product_name: str
    category: str
    order_count: str
    revenue: str
    conversion: str
    stock_status: str
    note: str

    def to_row(self) -> list[str]:
        return [
            self.rank,
            self.product_name,
            self.category,
            self.order_count,
            self.revenue,
            self.conversion,
            self.stock_status,
        ]


@dataclass(frozen=True)
class AlertRecord:
    """运营预警记录。"""

    level: str
    title: str
    source: str
    summary: str
    owner: str
    time_text: str
    suggestion: str


@dataclass(frozen=True)
class QuickActionRecord:
    """常用操作卡片配置。"""

    title: str
    description: str
    icon: str
    button_text: str
    status_text: str
    status_tone: BadgeTone
    action_hint: str


@dataclass(frozen=True)
class FeedEventRecord:
    """实时订单动态。"""

    timestamp: str
    title: str
    content: str
    event_type: str

    def to_event(self) -> dict[str, str]:
        return {
            "timestamp": self.timestamp,
            "title": self.title,
            "content": self.content,
            "type": self.event_type,
        }


@dataclass(frozen=True)
class OperationsSnapshot:
    """某个视角下的完整运营中心快照。"""

    summary: str
    metrics: tuple[OperationsMetric, ...]
    trend_title: str
    trend_unit: str
    trend_labels: tuple[str, ...]
    trend_values: tuple[float, ...]
    top_products: tuple[ProductPerformanceRecord, ...]
    alerts: tuple[AlertRecord, ...]
    feed_events: tuple[FeedEventRecord, ...]


OPERATIONS_TABLE_HEADERS = [
    "排名",
    "商品名称",
    "分类",
    "订单量",
    "销售额",
    "转化率",
    "库存状态",
]


QUICK_ACTIONS: tuple[QuickActionRecord, ...] = (
    QuickActionRecord(
        title="批量催付任务",
        description="对 2 小时内已加购未付款用户自动发送权益提醒，优先覆盖高客单商品。",
        icon="⚑",
        button_text="立即执行",
        status_text="今日已执行 3 次",
        status_tone="success",
        action_hint="已将高意向买家催付名单推送给客服跟进。",
    ),
    QuickActionRecord(
        title="低库存预警处理",
        description="联动仓配数据筛出 48 小时内可能断货的 SKU，生成补货与替代建议。",
        icon="▣",
        button_text="查看清单",
        status_text="6 个 SKU 待处理",
        status_tone="warning",
        action_hint="已打开低库存处理面板，可优先补足常青款颜色尺码。",
    ),
    QuickActionRecord(
        title="客服排班复核",
        description="根据会话峰值和退款咨询波峰调整班次，平衡首响时长与满意度。",
        icon="☍",
        button_text="复核排班",
        status_text="晚高峰建议重排",
        status_tone="brand",
        action_hint="已生成 18:00-22:00 高峰时段增援建议。",
    ),
    QuickActionRecord(
        title="店铺健康巡检",
        description="自动扫描异常退款率、延迟发货、评价波动与客服超时，输出日巡检摘要。",
        icon="✦",
        button_text="生成摘要",
        status_text="待生成",
        status_tone="info",
        action_hint="巡检摘要已刷新，重点异常已同步到预警列表。",
    ),
)


SNAPSHOTS: dict[str, OperationsSnapshot] = {
    "今日总览": OperationsSnapshot(
        summary="今日成交节奏保持稳定，美妆与家清类目拉动明显，售后压力主要集中在晚间尺码咨询与延迟发货说明。",
        metrics=(
            OperationsMetric("今日订单", "2,486", "up", "+12.8%", "较昨日同时段多 282 单", (121, 138, 146, 152, 166, 182, 196)),
            OperationsMetric("总营收", "¥428,760", "up", "+9.4%", "高客单礼盒贡献提升", (68, 72, 84, 93, 96, 108, 114)),
            OperationsMetric("退款率", "2.1%", "down", "-0.4%", "服饰尺码问题有所下降", (3.1, 2.9, 2.8, 2.5, 2.4, 2.2, 2.1)),
            OperationsMetric("客服响应时间", "38 秒", "down", "-12 秒", "高峰排班覆盖更均衡", (70, 65, 58, 52, 49, 43, 38)),
        ),
        trend_title="今日销售额分时走势",
        trend_unit="万元",
        trend_labels=("09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"),
        trend_values=(2.1, 2.6, 3.8, 4.5, 4.2, 4.9, 5.3, 5.9, 6.4),
        top_products=(
            ProductPerformanceRecord("1", "柔雾持妆粉底液 30ml", "美妆个护", "286", "¥42,960", "8.4%", "库存充足", "短视频挂车转化最佳"),
            ProductPerformanceRecord("2", "氨基酸净透洁面慕斯", "美妆个护", "254", "¥31,750", "9.2%", "库存充足", "复购单比例高"),
            ProductPerformanceRecord("3", "轻氧羽感防晒乳", "美妆个护", "226", "¥27,120", "7.9%", "余量 3 天", "需加急补货"),
            ProductPerformanceRecord("4", "居家多效除菌喷雾 2 瓶装", "家居日用", "211", "¥24,054", "6.8%", "库存充足", "直播外自然流量提升"),
            ProductPerformanceRecord("5", "高弹亲肤鲨鱼裤", "服饰内衣", "198", "¥39,402", "5.6%", "尺码紧张", "L 码退款率下降"),
            ProductPerformanceRecord("6", "云感纯棉四件套", "家纺家居", "184", "¥36,248", "4.8%", "库存充足", "高客单拉升营收"),
            ProductPerformanceRecord("7", "婴童柔护湿巾 80 抽 5 包", "母婴用品", "173", "¥19,030", "7.1%", "库存充足", "优惠券带动加购"),
            ProductPerformanceRecord("8", "厨房去油清洁泡泡", "家居日用", "169", "¥15,886", "6.3%", "余量 5 天", "晚间咨询偏多"),
            ProductPerformanceRecord("9", "软底轻跑运动鞋", "鞋靴箱包", "152", "¥33,440", "4.3%", "库存充足", "东北地区出单集中"),
            ProductPerformanceRecord("10", "保温吸管杯礼盒版", "百货文创", "146", "¥18,104", "5.2%", "库存充足", "适合作为组合购引流"),
            ProductPerformanceRecord("11", "便携补水喷雾仪", "美妆个护", "139", "¥13,483", "6.5%", "库存充足", "学生客群转化高"),
            ProductPerformanceRecord("12", "智能暖腹热敷腰带", "健康护理", "128", "¥28,032", "4.0%", "余量 2 天", "需监控断货风险"),
        ),
        alerts=(
            AlertRecord("高", "防晒乳库存告急", "仓配监控", "轻氧羽感防晒乳预计 2.8 天售罄，当前投放持续加量。", "仓储组-阿岳", "09:18", "建议优先补货 800 件，并将替代款加入推荐位。"),
            AlertRecord("中", "鲨鱼裤晚间退款咨询偏高", "售后中心", "尺码相关咨询 1 小时内达到 23 条，集中在 M/L 切换。", "客服组-言初", "10:42", "在详情页补充试穿建议，同时启用客服快捷回复。"),
            AlertRecord("中", "华东仓揽收时效下降", "物流履约", "华东仓 14:00 后出库单平均揽收延迟 1.6 小时。", "物流组-简宁", "14:05", "建议切换部分订单至华中仓分流。"),
            AlertRecord("低", "客服首响表现优秀", "客服质检", "今日平均首响 38 秒，优于周均 51 秒。", "客服组-雨禾", "15:20", "可复盘当前排班规则，沉淀为标准班表。"),
            AlertRecord("中", "暖腹腰带素材点击下滑", "投放看板", "近 3 小时 CTR 较上午下降 12%，素材疲劳迹象明显。", "投放组-沐川", "15:48", "建议切换种草型素材，突出热敷场景。"),
            AlertRecord("高", "厨房清洁泡泡差评风险", "评价监控", "出现 3 条关于包装渗漏的负向评价，可能影响转化。", "品控组-岚岚", "16:06", "尽快抽检近期批次并主动外呼安抚。"),
        ),
        feed_events=(
            FeedEventRecord("09:05", "新订单峰值触发", "柔雾持妆粉底液 10 分钟内新增 32 单，来自首页推荐流量。", "success"),
            FeedEventRecord("09:36", "售后咨询升温", "鲨鱼裤用户集中咨询尺码偏差，客服快捷模板已开启。", "warning"),
            FeedEventRecord("10:12", "物流分仓建议生成", "系统建议将 48 单华东订单转至华中仓，预计缩短 0.8 天。", "info"),
            FeedEventRecord("11:03", "组合购转化提升", "保温吸管杯礼盒版与湿巾组合购转化率升至 6.2%。", "success"),
            FeedEventRecord("12:18", "防晒乳库存预警", "预计 72 小时内库存告急，补货任务已派发。", "warning"),
            FeedEventRecord("13:44", "客服质检通过", "售前团队抽检 20 组会话，话术一致性评分 96 分。", "success"),
            FeedEventRecord("14:27", "异常评价监控", "厨房去油清洁泡泡出现包装问题反馈，已转品控复核。", "error"),
            FeedEventRecord("15:36", "分时销售创新高", "15:00-16:00 累计销售额达 5.9 万，超过近 7 日峰值。", "success"),
        ),
    ),
    "近 7 天": OperationsSnapshot(
        summary="近 7 天订单结构以美妆、家清、家纺为核心，退款率持续收窄，客户体验指标显著优于上周。",
        metrics=(
            OperationsMetric("今日订单", "16,802", "up", "+18.2%", "近 7 天累计订单规模扩张", (12, 13, 14, 15, 15.3, 15.8, 16.8)),
            OperationsMetric("总营收", "¥2,968,440", "up", "+14.6%", "高客单礼盒和家纺占比提升", (30, 34, 38, 41, 43, 46, 49)),
            OperationsMetric("退款率", "2.4%", "down", "-0.6%", "服饰类售后改善明显", (3.2, 3.0, 2.9, 2.8, 2.7, 2.5, 2.4)),
            OperationsMetric("客服响应时间", "45 秒", "down", "-18 秒", "多技能席位配置见效", (69, 64, 61, 56, 53, 49, 45)),
        ),
        trend_title="近 7 天日销售额走势",
        trend_unit="万元",
        trend_labels=("周一", "周二", "周三", "周四", "周五", "周六", "周日"),
        trend_values=(31.6, 34.2, 37.8, 39.5, 42.4, 45.8, 47.6),
        top_products=(
            ProductPerformanceRecord("1", "柔雾持妆粉底液 30ml", "美妆个护", "1,982", "¥298,410", "8.8%", "库存充足", "近 7 天稳居第一"),
            ProductPerformanceRecord("2", "高弹亲肤鲨鱼裤", "服饰内衣", "1,604", "¥318,195", "5.9%", "库存紧张", "尺码结构需优化"),
            ProductPerformanceRecord("3", "云感纯棉四件套", "家纺家居", "1,433", "¥281,658", "4.9%", "库存充足", "高客单持续增长"),
            ProductPerformanceRecord("4", "氨基酸净透洁面慕斯", "美妆个护", "1,392", "¥174,000", "9.4%", "库存充足", "复购转化最好"),
            ProductPerformanceRecord("5", "轻氧羽感防晒乳", "美妆个护", "1,331", "¥159,720", "8.1%", "余量 3 天", "补货中"),
            ProductPerformanceRecord("6", "智能暖腹热敷腰带", "健康护理", "1,012", "¥221,624", "4.4%", "余量 2 天", "素材切换后回升"),
            ProductPerformanceRecord("7", "厨房去油清洁泡泡", "家居日用", "1,005", "¥94,470", "6.8%", "库存充足", "评价需维护"),
            ProductPerformanceRecord("8", "婴童柔护湿巾 80 抽 5 包", "母婴用品", "988", "¥108,680", "7.2%", "库存充足", "复购表现稳定"),
            ProductPerformanceRecord("9", "保温吸管杯礼盒版", "百货文创", "921", "¥114,204", "5.7%", "库存充足", "礼赠场景强"),
            ProductPerformanceRecord("10", "软底轻跑运动鞋", "鞋靴箱包", "884", "¥194,480", "4.1%", "库存充足", "周末放量明显"),
            ProductPerformanceRecord("11", "居家多效除菌喷雾 2 瓶装", "家居日用", "846", "¥96,444", "6.5%", "库存充足", "搜索流量强"),
            ProductPerformanceRecord("12", "便携补水喷雾仪", "美妆个护", "812", "¥78,782", "6.9%", "库存充足", "新客占比高"),
        ),
        alerts=(
            AlertRecord("高", "鲨鱼裤尺码偏差需继续跟进", "退款复盘", "近 7 天 L 码换货申请仍高于均值 13%。", "商品组-予安", "周二", "建议把试穿模特数据上墙，并把问答前置。"),
            AlertRecord("中", "暖腹腰带素材需要轮换", "投放排期", "第二套素材点击下滑，建议加入冬季场景短片。", "投放组-景言", "周三", "新增 3 条场景素材后再观察 ROAS。"),
            AlertRecord("中", "华东仓晚班补货效率不足", "仓配日报", "晚班补货平均完成时间晚于标准 22 分钟。", "仓储组-洛可", "周四", "将高周转 SKU 前置到黄金货位。"),
            AlertRecord("低", "客服满意度持续提升", "服务质检", "近 7 天满意度 96.4%，优于月均 2.3 个点。", "客服组-时雨", "周五", "复制优秀话术到模板库。"),
            AlertRecord("中", "家清类目差评率小幅波动", "评价趋势", "包装相关评论上升，需要同步供应商。", "品控组-念白", "周六", "补拍开箱说明图，减少误解。"),
            AlertRecord("高", "防晒乳补货窗口偏紧", "供应链协同", "如补货延误，将影响下周主推节奏。", "采购组-可心", "周日", "建议追加应急替代 SKU 并平移流量。"),
        ),
        feed_events=(
            FeedEventRecord("周一", "周初活动起量", "粉底液与洁面慕斯同时进入自然流量高峰。", "success"),
            FeedEventRecord("周二", "仓配分流生效", "华中仓承接 162 单，履约时长环比缩短 11%。", "info"),
            FeedEventRecord("周三", "尺码话术优化上线", "鲨鱼裤售前咨询转化率提升 0.9 个点。", "success"),
            FeedEventRecord("周四", "家纺品类高客单放量", "四件套日销突破 40 万，成为利润贡献第一。", "success"),
            FeedEventRecord("周五", "清洁泡泡包装投诉", "品控启动抽检并锁定可疑批次。", "warning"),
            FeedEventRecord("周六", "周末客服高峰稳定", "首响控制在 48 秒以内，未出现大面积排队。", "success"),
            FeedEventRecord("周日", "下周补货计划确认", "防晒乳与暖腹腰带补货单已全部下发。", "info"),
        ),
    ),
    "近 30 天": OperationsSnapshot(
        summary="近 30 天店铺运营进入稳定增长区间，订单结构更均衡，供应链与客服协同效率显著提升。",
        metrics=(
            OperationsMetric("今日订单", "68,940", "up", "+22.4%", "月度订单规模创阶段新高", (41, 44, 48, 52, 58, 63, 69)),
            OperationsMetric("总营收", "¥12,846,500", "up", "+19.8%", "利润主力由美妆延展至家纺", (122, 128, 135, 148, 156, 163, 171)),
            OperationsMetric("退款率", "2.6%", "down", "-0.8%", "售后结构更健康", (3.9, 3.6, 3.4, 3.1, 2.9, 2.8, 2.6)),
            OperationsMetric("客服响应时间", "52 秒", "down", "-24 秒", "月度人效整体优化", (86, 82, 77, 71, 64, 58, 52)),
        ),
        trend_title="近 30 天周度运营趋势",
        trend_unit="万元",
        trend_labels=("第 1 周", "第 2 周", "第 3 周", "第 4 周", "第 5 周"),
        trend_values=(212.0, 235.4, 248.7, 266.9, 289.3),
        top_products=(
            ProductPerformanceRecord("1", "柔雾持妆粉底液 30ml", "美妆个护", "8,982", "¥1,352,910", "8.6%", "库存充足", "持续领跑"),
            ProductPerformanceRecord("2", "云感纯棉四件套", "家纺家居", "7,244", "¥1,425,882", "5.0%", "库存充足", "利润贡献最高"),
            ProductPerformanceRecord("3", "高弹亲肤鲨鱼裤", "服饰内衣", "6,891", "¥1,366,518", "5.5%", "库存紧张", "需常态化尺码优化"),
            ProductPerformanceRecord("4", "氨基酸净透洁面慕斯", "美妆个护", "6,345", "¥793,125", "9.1%", "库存充足", "复购心智强"),
            ProductPerformanceRecord("5", "轻氧羽感防晒乳", "美妆个护", "6,004", "¥720,480", "8.0%", "补货中", "季节性拉动明显"),
            ProductPerformanceRecord("6", "智能暖腹热敷腰带", "健康护理", "4,896", "¥1,072,224", "4.3%", "库存充足", "内容种草有效"),
            ProductPerformanceRecord("7", "软底轻跑运动鞋", "鞋靴箱包", "4,512", "¥992,640", "4.2%", "库存充足", "区域差异大"),
            ProductPerformanceRecord("8", "厨房去油清洁泡泡", "家居日用", "4,383", "¥411,?", "6.4%", "库存充足", "包装优化后评价回暖"),
            ProductPerformanceRecord("9", "保温吸管杯礼盒版", "百货文创", "4,216", "¥522,784", "5.9%", "库存充足", "节日礼赠表现稳"),
            ProductPerformanceRecord("10", "婴童柔护湿巾 80 抽 5 包", "母婴用品", "4,022", "¥442,420", "7.1%", "库存充足", "复购率高"),
            ProductPerformanceRecord("11", "居家多效除菌喷雾 2 瓶装", "家居日用", "3,908", "¥445,512", "6.0%", "库存充足", "站内搜索拉动"),
            ProductPerformanceRecord("12", "便携补水喷雾仪", "美妆个护", "3,766", "¥365,302", "6.7%", "库存充足", "新客蓄水款"),
        ),
        alerts=(
            AlertRecord("中", "月度增长健康但供给要前置", "经营总结", "高增速 SKU 需要提前锁产，避免活动期被动。", "运营组-知遥", "本月", "将高周转款补货周期从 5 天缩到 3 天。"),
            AlertRecord("高", "鲨鱼裤尺码问题需产品化解决", "售后月报", "单靠话术已接近优化上限，需要上新版型。", "商品组-一川", "本月", "优先验证新版腰臀参数并对老款做下架节奏。"),
            AlertRecord("中", "家清包材需要持续监测", "品控协同", "包装优化后负向反馈下降，但仍需观察一周。", "品控组-秋禾", "本月", "保留抽检与主动安抚机制。"),
            AlertRecord("低", "客服首响进入稳定区间", "服务月报", "多技能排班方案有效压平高峰。", "客服组-南枝", "本月", "继续维护模板库与培训机制。"),
            AlertRecord("中", "高客单家纺占比提升", "利润分析", "可适度增加高质感视觉素材，放大溢价感。", "内容组-阿珂", "本月", "家纺详情页建议增加场景化搭配模块。"),
            AlertRecord("高", "主推防晒乳需准备替代策略", "选品排期", "季节窗口短，断货风险会直接影响整体转化。", "供应链-可颂", "本月", "同步预热替代 SKU 并逐步过渡流量。"),
        ),
        feed_events=(
            FeedEventRecord("第 1 周", "经营基线完成", "订单结构完成从单品爆发到多品协同的切换。", "info"),
            FeedEventRecord("第 2 周", "家纺成为利润新核心", "四件套、礼盒类商品带动毛利率提升。", "success"),
            FeedEventRecord("第 3 周", "客服模型优化生效", "首响与满意度同步改善，转人工率下降。", "success"),
            FeedEventRecord("第 4 周", "仓配分流常态化", "多仓策略将平均履约时效拉回到健康区间。", "success"),
            FeedEventRecord("第 5 周", "补货前置成为关键动作", "高增 SKU 通过前置补货规避大促断货。", "warning"),
        ),
    ),
}


class OperationsCenterPage(BasePage):
    """运营中心概览页，聚合经营总览、预警、爆品与实时动态。"""

    default_route_id: RouteId = RouteId("operations_center")
    default_display_name: str = "运营中心"
    default_icon_name: str = "monitoring"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._view_options: tuple[str, ...] = tuple(SNAPSHOTS.keys())
        self._selected_view: str = self._view_options[0]
        self._search_text: str = ""
        self._selected_product_index: int = 0
        self._selected_alert_index: int = 0
        self._refresh_count: int = 0
        self._metric_cards: list[KPICard] = []
        self._quick_action_cards: list[ActionCard] = []
        self._alert_rows: list[dict[str, QWidget]] = []

        self._page_container: PageContainer | None = None
        self._search_bar: SearchBar | None = None
        self._view_combo: ThemedComboBox | None = None
        self._refresh_button: PrimaryButton | None = None
        self._focus_button: SecondaryButton | None = None
        self._summary_label: QLabel | None = None
        self._selection_badge: StatusBadge | None = None
        self._view_chip: TagChip | None = None
        self._trend_chart: ChartWidget | None = None
        self._top_products_table: DataTable | None = None
        self._order_feed: TimelineWidget | None = None
        self._top_product_title: QLabel | None = None
        self._top_product_meta: QLabel | None = None
        self._top_product_hint: QLabel | None = None
        self._alert_detail_title: QLabel | None = None
        self._alert_detail_summary: QLabel | None = None
        self._alert_detail_hint: QLabel | None = None
        self._action_feedback_badge: StatusBadge | None = None
        self._action_feedback_label: QLabel | None = None
        self._overview_card: InfoCard | None = None

        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建运营中心原型。"""

        _call(self, "setObjectName", "operationsCenterPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._page_container = PageContainer(
            title=self.display_name,
            description="围绕订单、营收、履约、客服与售后构建的一体化运营驾驶舱，用于快速识别优先级和处理节奏。",
            parent=self,
        )

        self._build_action_bar()
        self._build_kpi_section()
        self._build_overview_split()
        self._build_bottom_split()

        self.layout.addWidget(self._page_container)
        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_action_bar(self) -> None:
        if self._page_container is None:
            return
        action_host = QWidget(self._page_container)
        _call(action_host, "setObjectName", "operationsCenterActionBar")
        action_layout = QHBoxLayout(action_host)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING_MD)

        self._search_bar = SearchBar("搜索商品、预警或处理建议")
        _call(self._search_bar, "setMinimumWidth", 260)

        self._view_combo = ThemedComboBox("视角", self._view_options, action_host)
        _call(self._view_combo.combo_box, "setCurrentText", self._selected_view)

        self._focus_button = SecondaryButton("聚焦高优先事项", action_host, icon_text="◎")
        self._refresh_button = PrimaryButton("刷新运营节奏", action_host, icon_text="↻")

        action_layout.addWidget(self._search_bar, 1)
        action_layout.addWidget(self._view_combo)
        action_layout.addWidget(self._focus_button)
        action_layout.addWidget(self._refresh_button)
        page_container = cast(PageContainer, self._page_container)
        page_container.add_action(action_host)

    def _build_kpi_section(self) -> None:
        if self._page_container is None:
            return

        section = ContentSection("核心指标速览", icon="◉", parent=self._page_container)

        summary_strip = QWidget(section)
        _call(summary_strip, "setObjectName", "operationsSummaryStrip")
        summary_layout = QHBoxLayout(summary_strip)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_MD)

        self._selection_badge = StatusBadge("运营波动已就绪", tone="brand", parent=summary_strip)
        self._view_chip = TagChip(self._selected_view, tone="info", parent=summary_strip)
        self._summary_label = QLabel("", summary_strip)
        _call(self._summary_label, "setObjectName", "operationsSummaryLabel")
        _call(self._summary_label, "setWordWrap", True)

        summary_layout.addWidget(self._selection_badge)
        summary_layout.addWidget(self._view_chip)
        summary_layout.addWidget(self._summary_label, 1)
        section.add_widget(summary_strip)

        row = QWidget(section)
        _call(row, "setObjectName", "operationsMetricRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACING_MD)

        for metric in SNAPSHOTS[self._selected_view].metrics:
            card = KPICard(
                title=metric.title,
                value=metric.value,
                trend=metric.trend,
                percentage=metric.percentage,
                caption=metric.caption,
                sparkline_data=metric.sparkline,
            )
            _call(card, "setMinimumWidth", 180)
            self._metric_cards.append(card)
            row_layout.addWidget(card, 1)
        section.add_widget(row)
        self._page_container.add_widget(section)

    def _build_overview_split(self) -> None:
        if self._page_container is None:
            return

        split = SplitPanel(split_ratio=(0.58, 0.42), minimum_sizes=(620, 420), parent=self._page_container)
        split.set_widgets(self._build_left_overview_column(), self._build_right_overview_column())
        self._page_container.add_widget(split)

    def _build_left_overview_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        trend_section = ContentSection("成交趋势与节奏判断", icon="◌", parent=column)
        self._overview_card = InfoCard(
            title="今日运营判断",
            description="系统将根据实时订单、退款与会话波动自动输出处理建议，帮助团队把注意力放在最关键的异常上。",
            icon="✦",
            action_text="查看处理重点",
            parent=trend_section,
        )
        trend_section.add_widget(self._overview_card)

        self._trend_chart = ChartWidget(chart_type="line", title="今日销售额分时走势", unit="万元", parent=trend_section)
        _call(self._trend_chart, "setMinimumHeight", 320)
        trend_section.add_widget(self._trend_chart)

        self._action_feedback_badge = StatusBadge("等待操作", tone="neutral", parent=trend_section)
        self._action_feedback_label = QLabel("点击右侧常用操作卡片，可在本页模拟触发运营任务并更新实时动态。", trend_section)
        _call(self._action_feedback_label, "setObjectName", "operationsActionFeedbackLabel")
        _call(self._action_feedback_label, "setWordWrap", True)

        feedback_row = QWidget(trend_section)
        _call(feedback_row, "setObjectName", "operationsFeedbackRow")
        feedback_layout = QHBoxLayout(feedback_row)
        feedback_layout.setContentsMargins(0, 0, 0, 0)
        feedback_layout.setSpacing(SPACING_MD)
        feedback_layout.addWidget(self._action_feedback_badge)
        feedback_layout.addWidget(self._action_feedback_label, 1)
        trend_section.add_widget(feedback_row)

        layout.addWidget(trend_section)
        layout.addWidget(self._build_product_section())
        return column

    def _build_product_section(self) -> QWidget:
        section = ContentSection("爆品榜与运营备注", icon="▣", parent=self)

        table_meta = QWidget(section)
        _call(table_meta, "setObjectName", "operationsTableMeta")
        meta_layout = QHBoxLayout(table_meta)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(SPACING_MD)

        meta_badge = StatusBadge("支持排序与筛选", tone="success", parent=table_meta)
        meta_chip = TagChip("TikTok Shop 运营样本", tone="brand", parent=table_meta)
        self._top_product_hint = QLabel("选中任一商品后，右侧会显示当前运营重点和动作建议。", table_meta)
        _call(self._top_product_hint, "setObjectName", "operationsProductHint")
        _call(self._top_product_hint, "setWordWrap", True)

        meta_layout.addWidget(meta_badge)
        meta_layout.addWidget(meta_chip)
        meta_layout.addWidget(self._top_product_hint, 1)
        section.add_widget(table_meta)

        self._top_products_table = DataTable(headers=OPERATIONS_TABLE_HEADERS, page_size=8, empty_text="暂无商品数据", parent=section)
        section.add_widget(self._top_products_table)

        detail_card = QFrame(section)
        _call(detail_card, "setObjectName", "operationsProductDetailCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        detail_layout.setSpacing(SPACING_SM)

        self._top_product_title = QLabel("", detail_card)
        _call(self._top_product_title, "setObjectName", "operationsProductTitle")
        self._top_product_meta = QLabel("", detail_card)
        _call(self._top_product_meta, "setObjectName", "operationsProductMeta")
        _call(self._top_product_meta, "setWordWrap", True)

        detail_layout.addWidget(self._top_product_title)
        detail_layout.addWidget(self._top_product_meta)
        section.add_widget(detail_card)
        return section

    def _build_right_overview_column(self) -> QWidget:
        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)
        layout.addWidget(self._build_quick_action_section())
        layout.addWidget(self._build_alert_section(), 1)
        return column

    def _build_quick_action_section(self) -> QWidget:
        section = ContentSection("常用操作", icon="✦", parent=self)
        info_row = QWidget(section)
        _call(info_row, "setObjectName", "operationsQuickActionMeta")
        info_layout = QHBoxLayout(info_row)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(SPACING_MD)
        info_layout.addWidget(StatusBadge("点击后会刷新动态", tone="info", parent=info_row))
        info_layout.addWidget(TagChip("偏运营决策视角", tone="neutral", parent=info_row))
        info_layout.addStretch(1)
        section.add_widget(info_row)

        grid_host = QWidget(section)
        _call(grid_host, "setObjectName", "operationsQuickActionGrid")
        grid_layout = QVBoxLayout(grid_host)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(SPACING_MD)

        for item in QUICK_ACTIONS:
            card = ActionCard(
                title=item.title,
                description=item.description,
                icon=item.icon,
                button_text=item.button_text,
                status_text=item.status_text,
                status_tone=item.status_tone,  # type: ignore[arg-type]
                parent=grid_host,
            )
            self._quick_action_cards.append(card)
            grid_layout.addWidget(card)
        section.add_widget(grid_host)
        return section

    def _build_alert_section(self) -> QWidget:
        section = ContentSection("活跃预警 / 通知", icon="⚠", parent=self)

        detail_card = QFrame(section)
        _call(detail_card, "setObjectName", "operationsAlertDetailCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        detail_layout.setSpacing(SPACING_SM)

        self._alert_detail_title = QLabel("", detail_card)
        _call(self._alert_detail_title, "setObjectName", "operationsAlertTitle")
        self._alert_detail_summary = QLabel("", detail_card)
        _call(self._alert_detail_summary, "setObjectName", "operationsAlertSummary")
        _call(self._alert_detail_summary, "setWordWrap", True)
        self._alert_detail_hint = QLabel("", detail_card)
        _call(self._alert_detail_hint, "setObjectName", "operationsAlertHint")
        _call(self._alert_detail_hint, "setWordWrap", True)

        detail_layout.addWidget(self._alert_detail_title)
        detail_layout.addWidget(self._alert_detail_summary)
        detail_layout.addWidget(self._alert_detail_hint)
        section.add_widget(detail_card)

        list_host = QWidget(section)
        _call(list_host, "setObjectName", "operationsAlertList")
        list_layout = QVBoxLayout(list_host)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(SPACING_MD)

        for index in range(6):
            row = self._create_alert_row(index, list_host)
            self._alert_rows.append(row)
            list_layout.addWidget(row["frame"])
        list_layout.addStretch(1)
        section.add_widget(list_host)
        return section

    def _build_bottom_split(self) -> None:
        if self._page_container is None:
            return

        split = SplitPanel(split_ratio=(0.42, 0.58), minimum_sizes=(420, 580), parent=self._page_container)
        split.set_widgets(self._build_notification_section(), self._build_feed_section())
        self._page_container.add_widget(split)

    def _build_notification_section(self) -> QWidget:
        section = ContentSection("运营协同提示", icon="☍", parent=self)
        hint = QLabel(
            "这里聚合来自仓配、客服、品控与投放的处理提示，用来帮助运营经理做优先级排序和跨组协同。",
            section,
        )
        _call(hint, "setObjectName", "operationsCoordinationHint")
        _call(hint, "setWordWrap", True)
        section.add_widget(hint)

        cards_host = QWidget(section)
        _call(cards_host, "setObjectName", "operationsInfoCards")
        cards_layout = QVBoxLayout(cards_host)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(SPACING_MD)

        cards_layout.addWidget(
            InfoCard(
                title="仓配建议",
                description="高周转 SKU 建议提前前移到黄金货位，晚班补货时效预计可再提升 12%。",
                icon="▤",
                action_text="查看仓位调整",
                parent=cards_host,
            )
        )
        cards_layout.addWidget(
            InfoCard(
                title="客服建议",
                description="将鲨鱼裤尺码问答前置到详情页，客服模板继续保留偏瘦提醒与身材示例。",
                icon="◍",
                action_text="打开话术库",
                parent=cards_host,
            )
        )
        cards_layout.addWidget(
            InfoCard(
                title="投放建议",
                description="暖腹腰带 CTR 开始疲劳，建议切换冬季通勤与经期护理双场景素材。",
                icon="◎",
                action_text="生成新排期",
                parent=cards_host,
            )
        )
        section.add_widget(cards_host)
        return section

    def _build_feed_section(self) -> QWidget:
        section = ContentSection("实时订单动态", icon="◌", parent=self)

        top_row = QWidget(section)
        _call(top_row, "setObjectName", "operationsFeedMeta")
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(SPACING_MD)
        top_layout.addWidget(StatusBadge("已接入实时样本流", tone="success", parent=top_row))
        top_layout.addWidget(TagChip("时间线可动态追加", tone="brand", parent=top_row))
        top_layout.addStretch(1)
        section.add_widget(top_row)

        self._order_feed = TimelineWidget()
        section.add_widget(self._order_feed)
        return section

    def _create_alert_row(self, index: int, parent: QWidget) -> dict[str, QWidget]:
        frame = QFrame(parent)
        _call(frame, "setObjectName", f"operationsAlertRow{index}")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_MD)

        badge = StatusBadge("中", tone="warning", parent=frame)

        text_host = QWidget(frame)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)

        title = QLabel("", text_host)
        _call(title, "setObjectName", "operationsAlertRowTitle")
        summary = QLabel("", text_host)
        _call(summary, "setObjectName", "operationsAlertRowSummary")
        _call(summary, "setWordWrap", True)
        meta = QLabel("", text_host)
        _call(meta, "setObjectName", "operationsAlertRowMeta")

        text_layout.addWidget(title)
        text_layout.addWidget(summary)
        text_layout.addWidget(meta)

        button = QPushButton("查看", frame)
        _call(button, "setObjectName", "operationsAlertInspectButton")
        _call(button, "setMinimumHeight", BUTTON_HEIGHT)

        layout.addWidget(badge)
        layout.addWidget(text_host, 1)
        layout.addWidget(button)

        row = {
            "frame": frame,
            "badge": badge,
            "title": title,
            "summary": summary,
            "meta": meta,
            "button": button,
        }
        _connect(getattr(button, "clicked", None), lambda current=index: self._select_alert(current))
        return row

    def _bind_interactions(self) -> None:
        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._on_search_changed)
        if self._view_combo is not None:
            _connect(getattr(self._view_combo.combo_box, "currentTextChanged", None), self._on_view_changed)
        if self._refresh_button is not None:
            _connect(getattr(self._refresh_button, "clicked", None), self._simulate_refresh)
        if self._focus_button is not None:
            _connect(getattr(self._focus_button, "clicked", None), self._focus_high_priority)
        if self._top_products_table is not None:
            _connect(self._top_products_table.row_selected, self._select_product)
        if self._overview_card is not None:
            _connect(getattr(self._overview_card.action_button, "clicked", None), self._focus_high_priority)

        for index, card in enumerate(self._quick_action_cards):
            _connect(getattr(card.primary_button, "clicked", None), lambda _checked=False, current=index: self._run_quick_action(current))

    def _apply_page_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#operationsCenterPage {{
                background: transparent;
            }}
            QWidget#operationsSummaryStrip,
            QWidget#operationsFeedbackRow,
            QWidget#operationsTableMeta,
            QWidget#operationsQuickActionMeta,
            QWidget#operationsFeedMeta {{
                background-color: rgba(0, 242, 234, 0.05);
                border: 1px solid rgba(0, 242, 234, 0.12);
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_SM}px;
            }}
            QLabel#operationsSummaryLabel,
            QLabel#operationsProductHint,
            QLabel#operationsActionFeedbackLabel,
            QLabel#operationsCoordinationHint,
            QLabel#operationsAlertSummary,
            QLabel#operationsAlertHint,
            QLabel#operationsProductMeta,
            QLabel#operationsAlertRowSummary,
            QLabel#operationsAlertRowMeta {{
                color: {colors.text_muted};
                background: transparent;
                font-size: {_static_token('font.size.sm')};
                line-height: 1.55;
            }}
            QLabel#operationsProductTitle,
            QLabel#operationsAlertTitle,
            QLabel#operationsAlertRowTitle {{
                color: {colors.text};
                background: transparent;
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#operationsProductDetailCard,
            QFrame#operationsAlertDetailCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#operationsQuickActionGrid,
            QWidget#operationsInfoCards,
            QWidget#operationsAlertList {{
                background: transparent;
            }}
            QLabel#operationsAlertRowMeta {{
                font-size: {_static_token('font.size.xs')};
            }}
            QPushButton#operationsAlertInspectButton {{
                background-color: transparent;
                color: {_token('brand.primary')};
                border: 1px solid {_token('brand.primary')};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#operationsAlertInspectButton:hover {{
                background-color: rgba(0, 242, 234, 0.12);
            }}
            QFrame[alertLevel="高"] {{
                border: 1px solid rgba(239, 68, 68, 0.26);
                background-color: rgba(239, 68, 68, 0.06);
                border-radius: {RADIUS_LG}px;
            }}
            QFrame[alertLevel="中"] {{
                border: 1px solid rgba(245, 158, 11, 0.24);
                background-color: rgba(245, 158, 11, 0.05);
                border-radius: {RADIUS_LG}px;
            }}
            QFrame[alertLevel="低"] {{
                border: 1px solid rgba(34, 197, 94, 0.22);
                background-color: rgba(34, 197, 94, 0.05);
                border-radius: {RADIUS_LG}px;
            }}
            QFrame[alertActive="true"] {{
                border-color: {_token('brand.primary')};
            }}
            """,
        )

    def _current_snapshot(self) -> OperationsSnapshot:
        return SNAPSHOTS[self._selected_view]

    def _refresh_all_views(self) -> None:
        snapshot = self._current_snapshot()
        self._refresh_summary(snapshot)
        self._refresh_metrics(snapshot)
        self._refresh_chart(snapshot)
        self._refresh_products(snapshot)
        self._refresh_alerts(snapshot)
        self._refresh_feed(snapshot)
        self._refresh_product_detail(snapshot)
        self._refresh_alert_detail(snapshot)

    def _refresh_summary(self, snapshot: OperationsSnapshot) -> None:
        if self._summary_label is not None:
            _call(self._summary_label, "setText", snapshot.summary)
        if self._view_chip is not None:
            self._view_chip.set_text(self._selected_view)
        if self._selection_badge is not None:
            tone = "brand" if self._refresh_count % 2 == 0 else "info"
            self._selection_badge.set_tone(tone)  # type: ignore[arg-type]
            _call(self._selection_badge, "setText", f"已刷新 {self._refresh_count} 次" if self._refresh_count else "运营波动已就绪")
        if self._overview_card is not None:
            self._overview_card.set_description(snapshot.summary)

    def _refresh_metrics(self, snapshot: OperationsSnapshot) -> None:
        for card, metric in zip(self._metric_cards, snapshot.metrics):
            card.set_title(metric.title)
            card.set_value(metric.value)
            card.set_trend(metric.trend, metric.percentage)
            card.set_sparkline_data(metric.sparkline)
            _call(getattr(card, "_caption_label", None), "setText", metric.caption)

    def _refresh_chart(self, snapshot: OperationsSnapshot) -> None:
        if self._trend_chart is None:
            return
        _call(getattr(self._trend_chart, "_title", None), "__class__")
        self._trend_chart.set_unit(snapshot.trend_unit)
        self._trend_chart.set_data(snapshot.trend_values, snapshot.trend_labels)
        setattr(self._trend_chart, "_title", snapshot.trend_title)
        _call(self._trend_chart, "update")

    def _refresh_products(self, snapshot: OperationsSnapshot) -> None:
        if self._top_products_table is None:
            return
        records = self._filtered_products(snapshot.top_products)
        rows = [record.to_row() for record in records]
        self._top_products_table.set_rows(rows)
        if records:
            self._selected_product_index = min(self._selected_product_index, len(records) - 1)
            self._top_products_table.select_absolute_row(self._selected_product_index)
        else:
            self._selected_product_index = 0

    def _refresh_product_detail(self, snapshot: OperationsSnapshot) -> None:
        records = self._filtered_products(snapshot.top_products)
        if not records:
            if self._top_product_title is not None:
                _call(self._top_product_title, "setText", "当前无匹配商品")
            if self._top_product_meta is not None:
                _call(self._top_product_meta, "setText", "请调整搜索条件，查看当前视角下的商品运营备注。")
            return
        index = max(0, min(self._selected_product_index, len(records) - 1))
        record = records[index]
        if self._top_product_title is not None:
            _call(self._top_product_title, "setText", f"{record.rank} · {record.product_name}")
        if self._top_product_meta is not None:
            _call(
                self._top_product_meta,
                "setText",
                f"分类：{record.category}｜订单量：{record.order_count}｜销售额：{record.revenue}｜转化率：{record.conversion}｜库存：{record.stock_status}\n运营备注：{record.note}",
            )

    def _refresh_alerts(self, snapshot: OperationsSnapshot) -> None:
        records = self._filtered_alerts(snapshot.alerts)
        if records:
            self._selected_alert_index = min(self._selected_alert_index, len(records) - 1)
        else:
            self._selected_alert_index = 0

        for index, row in enumerate(self._alert_rows):
            frame = row["frame"]
            if index >= len(records):
                _call(frame, "setVisible", False)
                continue
            record = records[index]
            _call(frame, "setVisible", True)
            _call(frame, "setProperty", "alertLevel", record.level)
            _call(frame, "setProperty", "alertActive", "true" if index == self._selected_alert_index else "false")
            _call(row["badge"], "setText", record.level)
            tone = self._alert_tone(record.level)
            badge = row["badge"]
            if isinstance(badge, StatusBadge):
                badge.set_tone(tone)  # type: ignore[arg-type]
            _call(row["title"], "setText", record.title)
            _call(row["summary"], "setText", record.summary)
            _call(row["meta"], "setText", f"来源：{record.source}｜负责人：{record.owner}｜时间：{record.time_text}")
        self._refresh_alert_detail(snapshot)

    def _refresh_alert_detail(self, snapshot: OperationsSnapshot) -> None:
        records = self._filtered_alerts(snapshot.alerts)
        if not records:
            if self._alert_detail_title is not None:
                _call(self._alert_detail_title, "setText", "暂无预警")
            if self._alert_detail_summary is not None:
                _call(self._alert_detail_summary, "setText", "当前筛选条件下没有命中的预警或通知。")
            if self._alert_detail_hint is not None:
                _call(self._alert_detail_hint, "setText", "可以尝试搜索商品名、负责人或处理建议关键词。")
            return
        index = max(0, min(self._selected_alert_index, len(records) - 1))
        record = records[index]
        if self._alert_detail_title is not None:
            _call(self._alert_detail_title, "setText", f"{record.level} 优先级｜{record.title}")
        if self._alert_detail_summary is not None:
            _call(
                self._alert_detail_summary,
                "setText",
                f"来源：{record.source}｜负责人：{record.owner}｜触发时间：{record.time_text}\n事件说明：{record.summary}",
            )
        if self._alert_detail_hint is not None:
            _call(self._alert_detail_hint, "setText", f"建议动作：{record.suggestion}")

    def _refresh_feed(self, snapshot: OperationsSnapshot) -> None:
        if self._order_feed is None:
            return
        self._order_feed.set_events([item.to_event() for item in snapshot.feed_events])

    def _filtered_products(self, records: tuple[ProductPerformanceRecord, ...]) -> list[ProductPerformanceRecord]:
        query = self._search_text.strip().lower()
        if not query:
            return list(records)
        result: list[ProductPerformanceRecord] = []
        for item in records:
            haystack = " ".join((item.product_name, item.category, item.stock_status, item.note, item.revenue, item.order_count)).lower()
            if query in haystack:
                result.append(item)
        return result

    def _filtered_alerts(self, records: tuple[AlertRecord, ...]) -> list[AlertRecord]:
        query = self._search_text.strip().lower()
        if not query:
            return list(records)
        result: list[AlertRecord] = []
        for item in records:
            haystack = " ".join((item.level, item.title, item.source, item.summary, item.owner, item.suggestion)).lower()
            if query in haystack:
                result.append(item)
        return result

    def _alert_tone(self, level: str) -> BadgeTone:
        mapping: dict[str, BadgeTone] = {"高": "error", "中": "warning", "低": "success", "默认": "neutral"}
        return mapping[level] if level in mapping else mapping["默认"]

    def _on_search_changed(self, text: str) -> None:
        self._search_text = text.strip()
        self._selected_product_index = 0
        self._selected_alert_index = 0
        self._refresh_products(self._current_snapshot())
        self._refresh_alerts(self._current_snapshot())

    def _on_view_changed(self, text: str) -> None:
        if text not in SNAPSHOTS:
            return
        self._selected_view = text
        self._selected_product_index = 0
        self._selected_alert_index = 0
        self._refresh_all_views()

    def _simulate_refresh(self) -> None:
        self._refresh_count += 1
        if self._action_feedback_badge is not None:
            self._action_feedback_badge.set_tone("brand")
            _call(self._action_feedback_badge, "setText", "已刷新")
        if self._action_feedback_label is not None:
            _call(self._action_feedback_label, "setText", f"已重新计算 {self._selected_view} 运营节奏，重点关注库存告急、客服峰值与包装异常。")
        snapshot = self._current_snapshot()
        if self._order_feed is not None:
            events = [item.to_event() for item in snapshot.feed_events]
            events.insert(
                0,
                {
                    "timestamp": f"刷新 {self._refresh_count}",
                    "title": "系统重新评估经营节奏",
                    "content": f"已基于 {self._selected_view} 样本重新生成优先级，当前建议先处理高库存风险与包装投诉。",
                    "type": "info",
                },
            )
            self._order_feed.set_events(events)
        self._refresh_summary(snapshot)

    def _focus_high_priority(self) -> None:
        records = self._filtered_alerts(self._current_snapshot().alerts)
        for index, item in enumerate(records):
            if item.level == "高":
                self._select_alert(index)
                break
        if self._action_feedback_badge is not None:
            self._action_feedback_badge.set_tone("warning")
            _call(self._action_feedback_badge, "setText", "已聚焦高优先")
        if self._action_feedback_label is not None:
            _call(self._action_feedback_label, "setText", "已将视角聚焦到高优先级预警，建议优先安排补货与包装问题复核。")

    def _run_quick_action(self, index: int) -> None:
        if not (0 <= index < len(QUICK_ACTIONS)):
            return
        item = QUICK_ACTIONS[index]
        if self._action_feedback_badge is not None:
            self._action_feedback_badge.set_tone(item.status_tone)
            _call(self._action_feedback_badge, "setText", item.button_text)
        if self._action_feedback_label is not None:
            _call(self._action_feedback_label, "setText", item.action_hint)
        if self._order_feed is not None:
            events = [entry.to_event() for entry in self._current_snapshot().feed_events]
            events.insert(
                0,
                {
                    "timestamp": "刚刚",
                    "title": item.title,
                    "content": item.action_hint,
                    "type": "success" if item.status_tone in {"success", "brand"} else "warning",
                },
            )
            self._order_feed.set_events(events)

    def _select_product(self, index: int) -> None:
        self._selected_product_index = max(0, index)
        self._refresh_product_detail(self._current_snapshot())

    def _select_alert(self, index: int) -> None:
        self._selected_alert_index = max(0, index)
        self._refresh_alerts(self._current_snapshot())

    def on_activated(self) -> None:
        self._refresh_all_views()

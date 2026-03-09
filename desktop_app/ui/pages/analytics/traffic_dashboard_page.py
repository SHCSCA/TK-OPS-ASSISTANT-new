# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false, reportCallIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""流量看板页面。"""

from dataclasses import dataclass
from typing import Final, Sequence

from ....core.qt import QApplication, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    ChartWidget,
    ContentSection,
    DataTable,
    DistributionChart,
    FilterDropdown,
    HeatmapWidget,
    KPICard,
    MiniSparkline,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    StatusBadge,
    TabBar,
    TagChip,
    TrendComparison,
)
from ...components.inputs import (
    RADIUS_LG,
    RADIUS_MD,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _format_int(value: int | float) -> str:
    """格式化整数。"""

    return f"{int(round(float(value))):,}"


def _format_compact(value: int | float) -> str:
    """格式化紧凑数值。"""

    amount = float(value)
    if abs(amount) >= 100000000:
        return f"{amount / 100000000:.2f}亿"
    if abs(amount) >= 10000:
        return f"{amount / 10000:.1f}万"
    return _format_int(amount)


def _format_percent(value: float) -> str:
    """格式化百分比。"""

    return f"{value * 100:.1f}%"


def _safe_ratio(numerator: float, denominator: float) -> float:
    """避免除零。"""

    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _delta_direction(value: float) -> str:
    """将变化映射为趋势方向。"""

    if value > 0.008:
        return "up"
    if value < -0.008:
        return "down"
    return "flat"


def _series_delta(values: Sequence[float]) -> float:
    """返回首尾变化率。"""

    if len(values) < 2:
        return 0.0
    first_value = float(values[0])
    last_value = float(values[-1])
    if abs(first_value) <= 1e-9:
        return 0.0
    return (last_value - first_value) / abs(first_value)


def _theme_mode_text() -> str:
    """读取主题模式文案。"""

    app = QApplication.instance() if hasattr(QApplication, "instance") else None
    reader = getattr(app, "property", None)
    if callable(reader):
        value = reader("theme.mode")
        if str(value).lower() == "dark":
            return "dark"
    return "light"


def _match_keyword(text: str, keyword: str) -> bool:
    """判断关键字是否命中。"""

    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return True
    return normalized_keyword in text.lower()


@dataclass(frozen=True)
class TrafficContentRecord:
    """单条内容流量记录。"""

    title: str
    content_type: str
    traffic_source: str
    region: str
    device: str
    platform: str
    publish_hour: int
    views: int
    new_followers: int
    profile_visits: int
    engagement_rate: float
    ctr: float
    completion_rate: float
    trend_points: tuple[int, ...]


@dataclass(frozen=True)
class TrafficKPIState:
    """页面核心指标。"""

    total_views: int
    new_followers: int
    profile_visits: int
    engagement_rate: float
    views_change: float
    followers_change: float
    visits_change: float
    engagement_change: float
    views_sparkline: tuple[int, ...]
    followers_sparkline: tuple[int, ...]
    visits_sparkline: tuple[int, ...]
    engagement_sparkline: tuple[float, ...]


@dataclass(frozen=True)
class DevicePulse:
    """设备脉冲卡片数据。"""

    name: str
    share: float
    visits: int
    trend: tuple[int, ...]
    summary: str


CONTENT_HEADERS: Final[tuple[str, ...]] = (
    "内容标题",
    "播放量",
    "互动率",
    "点击率",
    "流量来源",
    "地区",
    "设备",
)

REGION_HEADERS: Final[tuple[str, ...]] = ("地区", "播放量", "新增粉丝", "主页访问", "互动率")

PEAK_HEADERS: Final[tuple[str, ...]] = ("时段", "播放量", "互动率", "主页访问", "建议动作")

SOURCE_LABELS: Final[tuple[str, ...]] = ("推荐页", "搜索", "主页", "外部链接")
DEVICE_LABELS: Final[tuple[str, ...]] = ("安卓", "苹果", "平板", "网页")
PLATFORM_LABELS: Final[tuple[str, ...]] = ("移动端应用", "移动网页", "桌面网页", "嵌入跳转")
TAB_LABELS: Final[tuple[str, ...]] = ("总流量", "内容表现", "地域设备")
TREND_LABELS: Final[tuple[str, ...]] = tuple(f"11/{index:02d}" for index in range(1, 31))

TRAFFIC_RECORDS: Final[tuple[TrafficContentRecord, ...]] = (
    TrafficContentRecord("冬季保暖外套穿搭指南", "穿搭短视频", "推荐页", "美国", "苹果", "移动端应用", 20, 542000, 10840, 16320, 0.084, 0.053, 0.468, (15200, 16400, 17800, 18650, 19400, 20500, 21600)), TrafficContentRecord("圣诞礼物清单开箱合集", "开箱短视频", "搜索", "英国", "苹果", "移动端应用", 21, 486000, 9210, 14160, 0.079, 0.047, 0.452, (13400, 14100, 14650, 15880, 16320, 17140, 18620)), TrafficContentRecord("厨房收纳神器 3 步改造", "教程短视频", "推荐页", "加拿大", "安卓", "移动端应用", 19, 438000, 8120, 12740, 0.088, 0.049, 0.487, (12100, 12940, 13420, 13950, 14780, 15210, 16040)), TrafficContentRecord("办公室桌面焕新灵感", "场景短视频", "主页", "德国", "桌面网页", "桌面网页", 14, 392000, 6370, 10980, 0.073, 0.043, 0.416, (10860, 11240, 11980, 12100, 12750, 13140, 13760)),
    TrafficContentRecord("瑜伽裤材质实测对比", "测评短视频", "推荐页", "法国", "苹果", "移动端应用", 18, 371000, 7040, 11620, 0.091, 0.058, 0.493, (10120, 10680, 11240, 11630, 12150, 12680, 13220)), TrafficContentRecord("秋冬家居香氛氛围布置", "氛围短视频", "外部链接", "澳大利亚", "安卓", "移动网页", 16, 348000, 5880, 10210, 0.068, 0.041, 0.402, (9180, 9640, 9860, 10420, 11040, 11460, 11910)), TrafficContentRecord("通勤包容量挑战实录", "实测短视频", "搜索", "美国", "安卓", "移动端应用", 12, 332000, 5590, 9870, 0.077, 0.046, 0.428, (8760, 9020, 9330, 9740, 10040, 10620, 11140)), TrafficContentRecord("节日餐桌布景模板分享", "教程短视频", "主页", "西班牙", "苹果", "移动端应用", 11, 318000, 5380, 9320, 0.074, 0.044, 0.421, (8220, 8610, 8980, 9360, 9740, 10050, 10820)),
    TrafficContentRecord("秋季卫衣版型避坑指南", "穿搭短视频", "推荐页", "意大利", "苹果", "移动端应用", 22, 301000, 5210, 8810, 0.082, 0.051, 0.445, (7860, 8120, 8510, 8860, 9240, 9680, 10260)), TrafficContentRecord("宠物窝冬日保暖升级", "场景短视频", "外部链接", "日本", "安卓", "嵌入跳转", 15, 284000, 4870, 8120, 0.086, 0.055, 0.471, (7440, 7720, 8030, 8420, 8760, 9140, 9650)), TrafficContentRecord("宿舍小家电清单推荐", "榜单短视频", "搜索", "韩国", "苹果", "移动端应用", 17, 266000, 4210, 7740, 0.071, 0.042, 0.399, (6920, 7180, 7460, 7820, 8090, 8460, 8910)), TrafficContentRecord("晨跑耳机佩戴稳定测试", "测评短视频", "推荐页", "美国", "苹果", "移动端应用", 7, 251000, 3980, 7360, 0.089, 0.057, 0.482, (6540, 6880, 7110, 7560, 7920, 8240, 8720)),
    TrafficContentRecord("极简咖啡角布置预算表", "教程短视频", "主页", "新加坡", "网页", "桌面网页", 10, 238000, 3720, 6890, 0.069, 0.039, 0.387, (6180, 6420, 6690, 7020, 7340, 7610, 7980)), TrafficContentRecord("年末派对亮片妆容合集", "妆容短视频", "推荐页", "美国", "苹果", "移动端应用", 23, 229000, 3610, 6520, 0.094, 0.061, 0.506, (6060, 6380, 6630, 7010, 7320, 7660, 8120)),
)

TRAFFIC_SERIES_BY_TAB: Final[dict[str, tuple[int, ...]]] = {
    "总流量": (128000, 131500, 135400, 140200, 146800, 151200, 154900, 160300, 167500, 171800, 175600, 181200, 185100, 188400, 192800, 198300, 202600, 205400, 209800, 214600, 219200, 223400, 229800, 234100, 238600, 243200, 247800, 252600, 258100, 264500),
    "内容表现": (112000, 115600, 118900, 123500, 129400, 133700, 136800, 142200, 146700, 149800, 153900, 159100, 162400, 165300, 168800, 173400, 177600, 181000, 184200, 187900, 191800, 195200, 199400, 202800, 206500, 210300, 214200, 218100, 222900, 226600),
    "地域设备": (98000, 100600, 104200, 107400, 112200, 116000, 119300, 121800, 125600, 129200, 133000, 136200, 139400, 142100, 145700, 149000, 152600, 155400, 158300, 161100, 164900, 168600, 171800, 174400, 178100, 181000, 184300, 188100, 191600, 195200),
}

COMPARE_TRAFFIC_SERIES: Final[dict[str, tuple[int, ...]]] = {
    "总流量": (103000, 107200, 109800, 112400, 116300, 119200, 122400, 126100, 129500, 132000, 135400, 138100, 141500, 144900, 147200, 150600, 153800, 156200, 159100, 162800, 166400, 170200, 173600, 177000, 180100, 183400, 186900, 190200, 193500, 196800),
    "内容表现": (92000, 94100, 96900, 99500, 101800, 104200, 107300, 110100, 113800, 116400, 119600, 123100, 126500, 129800, 132200, 135000, 138600, 141400, 144900, 147100, 149800, 152400, 155700, 158600, 162200, 165400, 168200, 171600, 175100, 178400),
    "地域设备": (81200, 83800, 85600, 88300, 90700, 93600, 96400, 99200, 101900, 104700, 107400, 109800, 112400, 115300, 118000, 120600, 123100, 125700, 128100, 130700, 133100, 135400, 138200, 140900, 143800, 146200, 149000, 151700, 154300, 157100),
}

SOURCE_BREAKDOWN: Final[dict[str, tuple[int, int, int, int]]] = {
    "总流量": (1584000, 648000, 462000, 278000),
    "内容表现": (1321000, 582000, 386000, 214000),
    "地域设备": (1186000, 491000, 354000, 196000),
}

REGION_ROWS: Final[dict[str, tuple[tuple[str, int, int, int, float], ...]]] = {
    "总流量": (("美国", 1284000, 24800, 39000, 0.086), ("英国", 642000, 12140, 18820, 0.078), ("加拿大", 428000, 8320, 12040, 0.082), ("德国", 386000, 6930, 10980, 0.073), ("法国", 342000, 6480, 10040, 0.081), ("澳大利亚", 311000, 6020, 9630, 0.074), ("日本", 276000, 5590, 8420, 0.079), ("韩国", 228000, 4210, 6610, 0.069), ("西班牙", 214000, 3980, 6240, 0.071), ("新加坡", 186000, 3520, 5810, 0.068)),
    "内容表现": (("美国", 1062000, 21420, 33200, 0.089), ("英国", 551000, 10680, 16740, 0.081), ("加拿大", 394000, 7620, 11180, 0.084), ("德国", 348000, 6180, 10020, 0.074), ("法国", 322000, 5960, 9380, 0.085), ("澳大利亚", 274000, 5480, 8720, 0.076), ("日本", 248000, 4920, 7600, 0.082), ("韩国", 196000, 3810, 5900, 0.071), ("西班牙", 182000, 3590, 5520, 0.073), ("新加坡", 161000, 3240, 5110, 0.071)),
    "地域设备": (("美国", 954000, 19120, 28400, 0.079), ("英国", 486000, 9480, 14420, 0.074), ("加拿大", 351000, 6850, 9800, 0.078), ("德国", 316000, 5660, 9120, 0.071), ("法国", 294000, 5280, 8540, 0.076), ("澳大利亚", 262000, 4890, 7940, 0.071), ("日本", 231000, 4430, 7020, 0.075), ("韩国", 186000, 3620, 5560, 0.067), ("西班牙", 168000, 3310, 5020, 0.069), ("新加坡", 149000, 2890, 4680, 0.066)),
}

PEAK_ROWS: Final[dict[str, tuple[tuple[str, int, float, int, str], ...]]] = {
    "总流量": (("07:00-08:00", 182000, 0.069, 4120, "通勤场景封面提亮"), ("09:00-10:00", 226000, 0.074, 5680, "加挂搜索型关键词"), ("12:00-13:00", 298000, 0.081, 7240, "午休场景上新合集"), ("15:00-16:00", 244000, 0.075, 6110, "补投素材测试版本"), ("18:00-19:00", 362000, 0.089, 9630, "集中发布种草内容"), ("20:00-21:00", 428000, 0.094, 11420, "重点推爆款转化素材"), ("21:00-22:00", 403000, 0.091, 10880, "主页置顶同题材合集"), ("23:00-24:00", 256000, 0.078, 6340, "夜间复盘加热视频")),
    "内容表现": (("07:00-08:00", 161000, 0.072, 3760, "轻量开箱短剪先发"), ("09:00-10:00", 208000, 0.078, 5160, "标题加入功能性词"), ("12:00-13:00", 272000, 0.084, 6920, "中段插入福利钩子"), ("15:00-16:00", 229000, 0.079, 5840, "继续扩散高完播视频"), ("18:00-19:00", 331000, 0.092, 8820, "晚高峰推教程内容"), ("20:00-21:00", 392000, 0.096, 10220, "主打高点击封面组合"), ("21:00-22:00", 366000, 0.093, 9640, "同类热视频二次封装"), ("23:00-24:00", 232000, 0.081, 5960, "保留低频投放")),
    "地域设备": (("07:00-08:00", 138000, 0.064, 3250, "同步多地区首条内容"), ("09:00-10:00", 186000, 0.070, 4620, "搜索词覆盖本地语言"), ("12:00-13:00", 234000, 0.076, 5980, "区域标签统一优化"), ("15:00-16:00", 210000, 0.073, 5520, "网页端跳转链路复核"), ("18:00-19:00", 286000, 0.082, 7440, "移动端首屏素材加码"), ("20:00-21:00", 332000, 0.086, 8520, "安卓重点时段提频"), ("21:00-22:00", 315000, 0.084, 8080, "苹果端高互动内容续推"), ("23:00-24:00", 201000, 0.071, 4840, "外链入口优化")),
}

GEO_HEATMAP: Final[dict[str, tuple[tuple[float, ...], ...]]] = {
    "总流量": ((12, 18, 24, 22, 20, 16, 10, 8, 9, 11, 12, 15, 18, 22, 25, 29, 31, 34, 36, 39, 41, 38, 28, 18), (10, 14, 18, 17, 15, 12, 8, 7, 8, 9, 11, 14, 16, 20, 24, 26, 30, 34, 39, 43, 46, 42, 31, 19), (8, 11, 14, 13, 12, 10, 8, 7, 9, 12, 14, 18, 21, 25, 27, 30, 34, 37, 42, 48, 50, 44, 32, 20), (11, 13, 15, 14, 12, 10, 7, 6, 7, 9, 12, 16, 19, 23, 26, 31, 35, 40, 46, 52, 57, 48, 34, 22), (12, 14, 18, 17, 15, 12, 9, 8, 10, 12, 15, 18, 22, 26, 29, 33, 39, 45, 52, 60, 64, 53, 37, 24), (16, 18, 21, 19, 17, 14, 12, 11, 12, 14, 17, 20, 23, 28, 31, 37, 45, 52, 58, 66, 72, 61, 42, 28), (18, 20, 24, 21, 19, 16, 13, 12, 14, 17, 20, 24, 28, 32, 36, 41, 49, 56, 63, 70, 75, 64, 46, 31)),
    "内容表现": ((9, 12, 16, 15, 13, 10, 7, 6, 7, 9, 10, 13, 16, 19, 21, 24, 28, 33, 37, 40, 44, 39, 28, 18), (8, 10, 14, 13, 11, 9, 6, 5, 6, 8, 10, 12, 15, 18, 21, 24, 28, 33, 38, 42, 45, 40, 29, 18), (7, 9, 11, 11, 10, 8, 6, 5, 7, 9, 11, 14, 17, 20, 23, 27, 31, 35, 40, 45, 48, 42, 30, 19), (8, 10, 12, 11, 10, 8, 6, 5, 6, 8, 11, 14, 17, 20, 24, 28, 33, 38, 44, 50, 54, 46, 32, 20), (9, 11, 14, 13, 11, 9, 7, 6, 8, 10, 13, 16, 20, 23, 27, 31, 37, 43, 49, 56, 60, 50, 35, 22), (12, 14, 17, 15, 13, 11, 9, 8, 10, 12, 15, 18, 21, 24, 29, 34, 40, 47, 53, 60, 66, 56, 39, 25), (14, 16, 19, 17, 15, 12, 10, 9, 11, 14, 17, 20, 24, 27, 31, 36, 43, 49, 56, 63, 68, 58, 41, 27)),
    "地域设备": ((6, 8, 11, 10, 9, 8, 6, 5, 6, 8, 9, 11, 14, 16, 18, 21, 25, 28, 31, 34, 36, 32, 24, 15), (5, 7, 9, 9, 8, 7, 5, 4, 5, 7, 9, 11, 13, 16, 18, 21, 24, 28, 32, 35, 37, 33, 24, 15), (5, 6, 8, 8, 7, 6, 5, 4, 6, 8, 10, 12, 15, 17, 20, 23, 26, 30, 34, 37, 39, 35, 25, 16), (6, 7, 9, 8, 7, 6, 5, 4, 5, 7, 9, 12, 14, 17, 20, 23, 28, 31, 36, 40, 43, 37, 27, 17), (7, 8, 10, 10, 9, 7, 6, 5, 7, 9, 11, 14, 16, 20, 22, 26, 31, 36, 41, 45, 48, 40, 28, 18), (9, 10, 12, 11, 10, 8, 7, 6, 8, 10, 12, 15, 18, 21, 25, 29, 35, 40, 45, 50, 55, 46, 31, 20), (10, 11, 14, 13, 11, 9, 8, 7, 9, 11, 14, 17, 20, 23, 27, 31, 37, 42, 47, 53, 57, 48, 33, 21)),
}

DEVICE_PULSES: Final[dict[str, tuple[DevicePulse, ...]]] = {
    "总流量": (DevicePulse("苹果", 0.44, 1482000, (52, 55, 58, 61, 67, 72, 76), "高客单用户访问深度最佳"), DevicePulse("安卓", 0.37, 1246000, (46, 49, 53, 57, 60, 64, 69), "自然流量承接规模最大"), DevicePulse("平板", 0.11, 368000, (18, 19, 20, 21, 23, 24, 26), "长时浏览与收藏偏高"), DevicePulse("网页", 0.08, 274000, (12, 13, 14, 15, 16, 18, 19), "外链与主页回访贡献明显")),
    "内容表现": (DevicePulse("苹果", 0.46, 1314000, (49, 52, 56, 60, 65, 70, 74), "高点击素材集中在苹果端"), DevicePulse("安卓", 0.34, 1016000, (41, 44, 48, 51, 56, 60, 63), "推荐页放量效率更稳定"), DevicePulse("平板", 0.12, 344000, (17, 18, 19, 21, 22, 24, 25), "完播率表现优于整体"), DevicePulse("网页", 0.08, 226000, (11, 12, 13, 14, 16, 17, 18), "主页深度浏览拉升收藏")),
    "地域设备": (DevicePulse("苹果", 0.41, 1121000, (43, 47, 50, 53, 58, 62, 66), "北美与日韩双高峰明显"), DevicePulse("安卓", 0.39, 1068000, (40, 42, 45, 49, 52, 57, 61), "东南亚与欧洲承接稳定"), DevicePulse("平板", 0.10, 286000, (15, 16, 17, 18, 20, 21, 22), "购物清单型内容停留更长"), DevicePulse("网页", 0.10, 271000, (13, 13, 14, 15, 16, 17, 18), "桌面端流量更依赖搜索")),
}

DEVICE_BREAKDOWN: Final[dict[str, tuple[int, int, int, int]]] = {
    "总流量": (44, 37, 11, 8),
    "内容表现": (46, 34, 12, 8),
    "地域设备": (41, 39, 10, 10),
}

PLATFORM_BREAKDOWN: Final[dict[str, tuple[int, int, int, int]]] = {
    "总流量": (63, 17, 12, 8),
    "内容表现": (67, 14, 11, 8),
    "地域设备": (58, 19, 13, 10),
}


class TrafficDashboardPage(BasePage):
    """流量看板主页面。"""

    default_route_id: RouteId = RouteId("traffic_dashboard")
    default_display_name: str = "流量看板"
    default_icon_name: str = "monitoring"

    def setup_ui(self) -> None:
        """构建页面。"""

        self._current_tab = TAB_LABELS[0]
        self._selected_source = "全部"
        self._selected_region = "全部"
        self._selected_device = "全部"
        self._selected_platform = "全部"
        self._search_keyword = ""
        self._selected_record_index = 0
        self._kpi_cards: dict[str, KPICard] = {}
        self._device_sparklines: list[MiniSparkline] = []
        self._device_value_labels: list[QLabel] = []
        self._device_summary_labels: list[QLabel] = []
        self._peak_status_badges: list[StatusBadge] = []

        self._search_bar: SearchBar | None = None
        self._source_filter: FilterDropdown | None = None
        self._region_filter: FilterDropdown | None = None
        self._device_filter: FilterDropdown | None = None
        self._platform_filter: FilterDropdown | None = None
        self._tab_bar: TabBar | None = None
        self._source_chart: ChartWidget | None = None
        self._trend_chart: ChartWidget | None = None
        self._trend_comparison: TrendComparison | None = None
        self._content_table: DataTable | None = None
        self._region_table: DataTable | None = None
        self._peak_table: DataTable | None = None
        self._geo_heatmap: HeatmapWidget | None = None
        self._device_distribution: DistributionChart | None = None
        self._platform_distribution: DistributionChart | None = None
        self._selected_title_label: QLabel | None = None
        self._selected_meta_label: QLabel | None = None
        self._selected_summary_label: QLabel | None = None
        self._selected_views_label: QLabel | None = None
        self._selected_followers_label: QLabel | None = None
        self._selected_visits_label: QLabel | None = None
        self._selected_engagement_label: QLabel | None = None
        self._selected_ctr_label: QLabel | None = None
        self._selected_completion_label: QLabel | None = None
        self._selected_source_badge: StatusBadge | None = None
        self._selected_region_badge: StatusBadge | None = None
        self._selected_device_badge: StatusBadge | None = None
        self._selected_platform_badge: StatusBadge | None = None
        self._selection_hint_label: QLabel | None = None

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(self, "setObjectName", "trafficDashboardPage")

        self._page_container = PageContainer(
            title="流量看板",
            description="围绕推荐、搜索、主页与外链流量，联动内容、地域、设备与峰值时段，快速定位 TikTok 分发机会。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._build_header_actions()
        self._page_container.add_widget(self._build_toolbar())
        self._page_container.add_widget(self._build_kpi_strip())
        self._page_container.add_widget(self._build_workspace())
        self._page_container.add_widget(self._build_footer_hint())

        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_header_actions(self) -> None:
        """构建头部操作区。"""

        self._page_container.add_action(TagChip("近 30 天", tone="brand", parent=self))
        self._page_container.add_action(TagChip("短视频流量", tone="info", parent=self))
        self._page_container.add_action(TagChip("自动刷新开启", tone="success", parent=self))
        self._page_container.add_action(StatusBadge("今日样本 14 条", tone="info", parent=self))
        self._page_container.add_action(SecondaryButton("刷新看板", parent=self))
        self._page_container.add_action(PrimaryButton("导出流量快照", parent=self))

    def _build_toolbar(self) -> QWidget:
        """构建筛选工具栏。"""

        panel = QFrame(self)
        _call(panel, "setObjectName", "trafficToolbar")
        root = QVBoxLayout(panel)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        title_row = QWidget(panel)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)

        title_column = QWidget(title_row)
        title_column_layout = QVBoxLayout(title_column)
        title_column_layout.setContentsMargins(0, 0, 0, 0)
        title_column_layout.setSpacing(SPACING_XS)
        title_label = QLabel("流量筛选", title_column)
        helper_label = QLabel("支持按来源、地区、设备与平台快速切片，并联动下方图表与表格。", title_column)
        _call(title_label, "setObjectName", "trafficSectionTitle")
        _call(helper_label, "setObjectName", "trafficSubtleText")
        title_column_layout.addWidget(title_label)
        title_column_layout.addWidget(helper_label)
        title_layout.addWidget(title_column)
        title_layout.addStretch(1)
        hint_badge = StatusBadge("推荐页贡献最高", tone="success", parent=title_row)
        title_layout.addWidget(hint_badge)

        filter_row = QWidget(panel)
        filter_layout = QHBoxLayout(filter_row)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(SPACING_LG)
        self._search_bar = SearchBar("搜索内容标题、场景、地区或流量线索...", filter_row)
        self._source_filter = FilterDropdown("流量来源", SOURCE_LABELS, parent=filter_row)
        self._region_filter = FilterDropdown("地区", tuple(row[0] for row in REGION_ROWS[TAB_LABELS[0]]), parent=filter_row)
        self._device_filter = FilterDropdown("设备", DEVICE_LABELS, parent=filter_row)
        self._platform_filter = FilterDropdown("平台", PLATFORM_LABELS, parent=filter_row)
        filter_layout.addWidget(self._search_bar, 3)
        filter_layout.addWidget(self._source_filter, 1)
        filter_layout.addWidget(self._region_filter, 1)
        filter_layout.addWidget(self._device_filter, 1)
        filter_layout.addWidget(self._platform_filter, 1)

        tag_row = QWidget(panel)
        tag_layout = QHBoxLayout(tag_row)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(SPACING_MD)
        tag_layout.addWidget(TagChip("搜索增量加速", tone="warning", parent=tag_row))
        tag_layout.addWidget(TagChip("晚高峰 20:00-22:00", tone="brand", parent=tag_row))
        tag_layout.addWidget(TagChip("苹果端点击更高", tone="info", parent=tag_row))
        tag_layout.addStretch(1)
        tag_layout.addWidget(SecondaryButton("重置筛选", parent=tag_row))
        tag_layout.addWidget(PrimaryButton("同步运营节奏", parent=tag_row))

        root.addWidget(title_row)
        root.addWidget(filter_row)
        root.addWidget(tag_row)
        return panel

    def _build_kpi_strip(self) -> QWidget:
        """构建顶部 KPI 卡片。"""

        wrapper = QWidget(self)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        card_specs = (
            ("总播放量", "0", "up", "+0.0%", "近 30 天整体分发", (0, 0, 0, 0, 0, 0, 0)),
            ("新增粉丝", "0", "up", "+0.0%", "内容带粉效率", (0, 0, 0, 0, 0, 0, 0)),
            ("主页访问", "0", "up", "+0.0%", "主页承接强度", (0, 0, 0, 0, 0, 0, 0)),
            ("内容互动率", "0.0%", "up", "+0.0%", "点赞评论分享综合", (0, 0, 0, 0, 0, 0, 0)),
        )
        for title, value, trend, percentage, caption, sparkline in card_specs:
            card = KPICard(title=title, value=value, trend=trend, percentage=percentage, caption=caption, sparkline_data=sparkline, parent=wrapper)
            self._kpi_cards[title] = card
            layout.addWidget(card, 1)
        return wrapper

    def _build_workspace(self) -> QWidget:
        """构建主工作区。"""

        shell = QWidget(self)
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_left_column(), 3)
        layout.addWidget(self._build_right_column(), 2)
        return shell

    def _build_left_column(self) -> QWidget:
        """构建左侧主体列。"""

        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_tabbed_section())
        layout.addWidget(self._build_content_table_section())
        layout.addWidget(self._build_geo_device_section())
        return column

    def _build_right_column(self) -> QWidget:
        """构建右侧洞察列。"""

        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)
        layout.addWidget(self._build_selection_detail_section())
        layout.addWidget(self._build_peak_section())
        layout.addWidget(self._build_device_pulse_section())
        return column

    def _build_tabbed_section(self) -> QWidget:
        """构建标签页区域。"""

        section = ContentSection("流量概览", icon="◎", parent=self)
        self._tab_bar = TabBar(section)
        self._tab_bar.add_tab(TAB_LABELS[0], self._build_overview_tab())
        self._tab_bar.add_tab(TAB_LABELS[1], self._build_performance_tab())
        self._tab_bar.add_tab(TAB_LABELS[2], self._build_geo_tab())
        section.add_widget(self._tab_bar)
        return section

    def _build_overview_tab(self) -> QWidget:
        """构建总流量标签内容。"""

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        charts_row = QWidget(page)
        charts_layout = QHBoxLayout(charts_row)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(SPACING_LG)

        source_section = ContentSection("流量来源拆分", icon="◔", parent=charts_row)
        self._source_chart = ChartWidget(chart_type="pie", title="来源占比", labels=SOURCE_LABELS, data=SOURCE_BREAKDOWN[TAB_LABELS[0]], unit="万", parent=source_section)
        source_section.add_widget(self._source_chart)
        charts_layout.addWidget(source_section, 1)

        trend_section = ContentSection("近 30 天流量走势", icon="∿", parent=charts_row)
        self._trend_chart = ChartWidget(chart_type="line", title="日流量趋势", labels=TREND_LABELS, data=TRAFFIC_SERIES_BY_TAB[TAB_LABELS[0]], unit="", parent=trend_section)
        trend_section.add_widget(self._trend_chart)
        charts_layout.addWidget(trend_section, 2)

        comparison_section = ContentSection("当前周期对比", icon="≈", parent=page)
        self._trend_comparison = TrendComparison(
            comparison_section,
            labels=TREND_LABELS,
            current_values=tuple(float(value) for value in TRAFFIC_SERIES_BY_TAB[TAB_LABELS[0]]),
            compare_values=tuple(float(value) for value in COMPARE_TRAFFIC_SERIES[TAB_LABELS[0]]),
            current_name="本周期",
            compare_name="上一周期",
        )
        comparison_section.add_widget(self._trend_comparison)

        layout.addWidget(charts_row)
        layout.addWidget(comparison_section)
        return page

    def _build_performance_tab(self) -> QWidget:
        """构建内容表现标签内容。"""

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        insight_row = QWidget(page)
        insight_layout = QHBoxLayout(insight_row)
        insight_layout.setContentsMargins(0, 0, 0, 0)
        insight_layout.setSpacing(SPACING_LG)

        left_section = ContentSection("推荐与搜索波动", icon="↗", parent=insight_row)
        left_chart = ChartWidget(chart_type="bar", title="来源贡献变化", labels=SOURCE_LABELS, data=SOURCE_BREAKDOWN[TAB_LABELS[1]], unit="万", parent=left_section)
        left_section.add_widget(left_chart)
        insight_layout.addWidget(left_section, 1)

        right_section = ContentSection("内容拉新趋势", icon="✦", parent=insight_row)
        spark_shell = QWidget(right_section)
        spark_layout = QVBoxLayout(spark_shell)
        spark_layout.setContentsMargins(0, 0, 0, 0)
        spark_layout.setSpacing(SPACING_MD)
        spark_title = QLabel("高潜内容的 7 日增粉曲线", spark_shell)
        _call(spark_title, "setObjectName", "trafficMetricTitle")
        spark_layout.addWidget(spark_title)
        spark_layout.addWidget(MiniSparkline((36, 38, 42, 49, 55, 62, 71), spark_shell))
        spark_layout.addWidget(MiniSparkline((28, 30, 34, 37, 43, 50, 58), spark_shell))
        spark_layout.addWidget(MiniSparkline((19, 22, 25, 29, 33, 38, 46), spark_shell))
        right_section.add_widget(spark_shell)
        insight_layout.addWidget(right_section, 1)

        layout.addWidget(insight_row)
        return page

    def _build_geo_tab(self) -> QWidget:
        """构建地域设备标签内容。"""

        page = QWidget(self)
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        region_section = ContentSection("地区热力", icon="▦", parent=page)
        region_hint = QLabel("热力图按近 7 日全球活跃强度折算，越亮表示该时段跨地区触达越高。", region_section)
        _call(region_hint, "setObjectName", "trafficSubtleText")
        self._geo_heatmap = HeatmapWidget(region_section, GEO_HEATMAP[TAB_LABELS[0]])
        region_section.add_widget(region_hint)
        region_section.add_widget(self._geo_heatmap)
        layout.addWidget(region_section, 2)

        mix_section = ContentSection("设备与平台占比", icon="▥", parent=page)
        self._device_distribution = DistributionChart(mix_section, tuple(zip(DEVICE_LABELS, DEVICE_BREAKDOWN[TAB_LABELS[0]])))
        self._platform_distribution = DistributionChart(mix_section, tuple(zip(PLATFORM_LABELS, PLATFORM_BREAKDOWN[TAB_LABELS[0]])))
        mix_section.add_widget(QLabel("设备结构", mix_section))
        mix_section.add_widget(self._device_distribution)
        mix_section.add_widget(QLabel("平台结构", mix_section))
        mix_section.add_widget(self._platform_distribution)
        layout.addWidget(mix_section, 1)
        return page

    def _build_content_table_section(self) -> QWidget:
        """构建内容表格区域。"""

        section = ContentSection("高表现内容", icon="▤", parent=self)
        helper = QLabel("按筛选条件展示播放与转粉表现最佳内容，点击行可联动右侧详情。", section)
        _call(helper, "setObjectName", "trafficSubtleText")
        self._content_table = DataTable(headers=CONTENT_HEADERS, rows=(), page_size=8, empty_text="暂无内容数据", parent=section)
        section.add_widget(helper)
        section.add_widget(self._content_table)
        return section

    def _build_geo_device_section(self) -> QWidget:
        """构建地域设备区域。"""

        shell = QWidget(self)
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        region_section = ContentSection("地区分布", icon="◫", parent=shell)
        self._region_table = DataTable(headers=REGION_HEADERS, rows=(), page_size=6, empty_text="暂无地区数据", parent=region_section)
        region_section.add_widget(self._region_table)
        layout.addWidget(region_section, 1)

        device_section = ContentSection("设备与平台拆分", icon="◎", parent=shell)
        device_intro = QLabel("结合来源变化查看不同终端的触达与主页承接表现。", device_section)
        _call(device_intro, "setObjectName", "trafficSubtleText")
        device_section.add_widget(device_intro)
        device_section.add_widget(self._build_distribution_panels(device_section))
        layout.addWidget(device_section, 1)
        return shell

    def _build_distribution_panels(self, parent: QWidget) -> QWidget:
        """构建设备分布双栏。"""

        wrapper = QWidget(parent)
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        left = ContentSection("设备占比", icon="▥", parent=wrapper)
        device_chart = DistributionChart(left, tuple(zip(DEVICE_LABELS, DEVICE_BREAKDOWN[TAB_LABELS[0]])))
        left.add_widget(device_chart)
        layout.addWidget(left, 1)

        right = ContentSection("平台拆分", icon="▥", parent=wrapper)
        platform_chart = DistributionChart(right, tuple(zip(PLATFORM_LABELS, PLATFORM_BREAKDOWN[TAB_LABELS[0]])))
        right.add_widget(platform_chart)
        layout.addWidget(right, 1)

        return wrapper

    def _build_selection_detail_section(self) -> QWidget:
        """构建右侧内容详情区域。"""

        section = ContentSection("选中内容详情", icon="✦", parent=self)
        detail_card = QFrame(section)
        _call(detail_card, "setObjectName", "trafficDetailCard")
        root = QVBoxLayout(detail_card)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        self._selected_title_label = QLabel("等待选择内容", detail_card)
        self._selected_meta_label = QLabel("", detail_card)
        self._selected_summary_label = QLabel("点击左侧任意高表现内容后，此处会展示流量来源、互动、设备与平台洞察。", detail_card)
        _call(self._selected_title_label, "setObjectName", "trafficSelectionTitle")
        _call(self._selected_meta_label, "setObjectName", "trafficSubtleText")
        _call(self._selected_summary_label, "setObjectName", "trafficSelectionBody")
        _call(self._selected_summary_label, "setWordWrap", True)
        root.addWidget(self._selected_title_label)
        root.addWidget(self._selected_meta_label)
        root.addWidget(self._selected_summary_label)

        badge_row = QWidget(detail_card)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(SPACING_SM)
        self._selected_source_badge = StatusBadge("来源 -", tone="info", parent=badge_row)
        self._selected_region_badge = StatusBadge("地区 -", tone="brand", parent=badge_row)
        self._selected_device_badge = StatusBadge("设备 -", tone="warning", parent=badge_row)
        self._selected_platform_badge = StatusBadge("平台 -", tone="neutral", parent=badge_row)
        badge_layout.addWidget(self._selected_source_badge)
        badge_layout.addWidget(self._selected_region_badge)
        badge_layout.addWidget(self._selected_device_badge)
        badge_layout.addWidget(self._selected_platform_badge)
        badge_layout.addStretch(1)
        root.addWidget(badge_row)

        stats_wrap = QWidget(detail_card)
        stats_layout = QHBoxLayout(stats_wrap)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(SPACING_MD)
        stats_layout.addWidget(self._build_metric_block("播放量", "trafficMetricViews", "_selected_views_label"), 1)
        stats_layout.addWidget(self._build_metric_block("新增粉丝", "trafficMetricFollowers", "_selected_followers_label"), 1)
        stats_layout.addWidget(self._build_metric_block("主页访问", "trafficMetricVisits", "_selected_visits_label"), 1)
        root.addWidget(stats_wrap)

        stats_wrap_b = QWidget(detail_card)
        stats_layout_b = QHBoxLayout(stats_wrap_b)
        stats_layout_b.setContentsMargins(0, 0, 0, 0)
        stats_layout_b.setSpacing(SPACING_MD)
        stats_layout_b.addWidget(self._build_metric_block("互动率", "trafficMetricEngagement", "_selected_engagement_label"), 1)
        stats_layout_b.addWidget(self._build_metric_block("点击率", "trafficMetricCtr", "_selected_ctr_label"), 1)
        stats_layout_b.addWidget(self._build_metric_block("完播率", "trafficMetricCompletion", "_selected_completion_label"), 1)
        root.addWidget(stats_wrap_b)

        self._selection_hint_label = QLabel("建议：优先复用高点击封面与晚高峰发布时间。", detail_card)
        _call(self._selection_hint_label, "setObjectName", "trafficAccentHint")
        root.addWidget(self._selection_hint_label)

        section.add_widget(detail_card)
        return section

    def _build_metric_block(self, label_text: str, object_name: str, target_attr: str) -> QWidget:
        """构建指标块。"""

        card = QFrame(self)
        _call(card, "setObjectName", object_name)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_XS)
        caption = QLabel(label_text, card)
        value_label = QLabel("-", card)
        _call(caption, "setObjectName", "trafficMetricTitle")
        _call(value_label, "setObjectName", "trafficMetricValue")
        layout.addWidget(caption)
        layout.addWidget(value_label)
        setattr(self, target_attr, value_label)
        return card

    def _build_peak_section(self) -> QWidget:
        """构建峰值时段区域。"""

        section = ContentSection("高峰时段分析", icon="⏱", parent=self)
        hint = QLabel("按近 30 天累计播放汇总高活跃时段，并给出推荐动作。", section)
        _call(hint, "setObjectName", "trafficSubtleText")
        self._peak_table = DataTable(headers=PEAK_HEADERS, rows=(), page_size=8, empty_text="暂无高峰数据", parent=section)
        section.add_widget(hint)
        section.add_widget(self._peak_table)

        badge_row = QWidget(section)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(SPACING_SM)
        for text in ("晚高峰强势", "搜索入口增长", "主页回访稳定"):
            badge = StatusBadge(text, tone="info", parent=badge_row)
            self._peak_status_badges.append(badge)
            badge_layout.addWidget(badge)
        badge_layout.addStretch(1)
        section.add_widget(badge_row)
        return section

    def _build_device_pulse_section(self) -> QWidget:
        """构建设备脉冲区域。"""

        section = ContentSection("设备脉冲", icon="◌", parent=self)
        intro = QLabel("不同设备的流量强度、访问规模与近 7 天波动。", section)
        _call(intro, "setObjectName", "trafficSubtleText")
        section.add_widget(intro)
        for pulse in DEVICE_PULSES[TAB_LABELS[0]]:
            section.add_widget(self._build_device_pulse_card(pulse, section))
        return section

    def _build_device_pulse_card(self, pulse: DevicePulse, parent: QWidget) -> QWidget:
        """构建设备脉冲卡片。"""

        card = QFrame(parent)
        _call(card, "setObjectName", "trafficPulseCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_SM)

        header = QWidget(card)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_SM)
        title_label = QLabel(pulse.name, header)
        title_value = QLabel(f"占比 {_format_percent(pulse.share)}", header)
        _call(title_label, "setObjectName", "trafficMetricTitle")
        _call(title_value, "setObjectName", "trafficSubtleText")
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(title_value)

        visits_label = QLabel(_format_compact(pulse.visits), card)
        summary_label = QLabel(pulse.summary, card)
        _call(visits_label, "setObjectName", "trafficPulseValue")
        _call(summary_label, "setObjectName", "trafficSubtleText")
        _call(summary_label, "setWordWrap", True)

        sparkline = MiniSparkline(pulse.trend, card)
        self._device_sparklines.append(sparkline)
        self._device_value_labels.append(visits_label)
        self._device_summary_labels.append(summary_label)

        layout.addWidget(header)
        layout.addWidget(visits_label)
        layout.addWidget(sparkline)
        layout.addWidget(summary_label)
        return card

    def _build_footer_hint(self) -> QWidget:
        """构建底部提示。"""

        footer = QFrame(self)
        _call(footer, "setObjectName", "trafficFooter")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(SPACING_XL, SPACING_MD, SPACING_XL, SPACING_MD)
        layout.setSpacing(SPACING_MD)
        hint = QLabel("运营建议：优先在 20:00-22:00 投放高点击内容，搜索来源内容标题保持功能词 + 场景词组合。", footer)
        _call(hint, "setObjectName", "trafficSubtleText")
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(StatusBadge(f"主题：{'深色' if _theme_mode_text() == 'dark' else '浅色'}", tone="neutral", parent=footer))
        return footer

    def _bind_interactions(self) -> None:
        """绑定交互。"""

        if self._search_bar is not None:
            _connect(self._search_bar.search_changed, self._handle_search_changed)
        if self._source_filter is not None:
            _connect(self._source_filter.filter_changed, self._handle_source_changed)
        if self._region_filter is not None:
            _connect(self._region_filter.filter_changed, self._handle_region_changed)
        if self._device_filter is not None:
            _connect(self._device_filter.filter_changed, self._handle_device_changed)
        if self._platform_filter is not None:
            _connect(self._platform_filter.filter_changed, self._handle_platform_changed)
        if self._tab_bar is not None:
            _connect(self._tab_bar.tab_changed, self._handle_tab_changed)
        if self._content_table is not None:
            _connect(self._content_table.row_selected, self._handle_row_selected)
            _connect(self._content_table.row_double_clicked, self._handle_row_selected)

    def _handle_search_changed(self, text: str) -> None:
        """处理搜索变化。"""

        self._search_keyword = text.strip()
        self._selected_record_index = 0
        self._refresh_all_views()

    def _handle_source_changed(self, text: str) -> None:
        """处理来源筛选变化。"""

        self._selected_source = text
        self._selected_record_index = 0
        self._refresh_all_views()

    def _handle_region_changed(self, text: str) -> None:
        """处理地区筛选变化。"""

        self._selected_region = text
        self._selected_record_index = 0
        self._refresh_all_views()

    def _handle_device_changed(self, text: str) -> None:
        """处理设备筛选变化。"""

        self._selected_device = text
        self._selected_record_index = 0
        self._refresh_all_views()

    def _handle_platform_changed(self, text: str) -> None:
        """处理平台筛选变化。"""

        self._selected_platform = text
        self._selected_record_index = 0
        self._refresh_all_views()

    def _handle_tab_changed(self, index: int) -> None:
        """处理标签切换。"""

        if 0 <= index < len(TAB_LABELS):
            self._current_tab = TAB_LABELS[index]
            self._selected_record_index = 0
            self._refresh_all_views()

    def _handle_row_selected(self, absolute_row: int) -> None:
        """处理表格行选中。"""

        records = self._filtered_records()
        if not records:
            self._selected_record_index = 0
        else:
            self._selected_record_index = max(0, min(absolute_row, len(records) - 1))
        self._refresh_selection_detail(records)

    def _filtered_records(self) -> list[TrafficContentRecord]:
        """返回筛选后的记录。"""

        records: list[TrafficContentRecord] = []
        for record in TRAFFIC_RECORDS:
            searchable = " ".join((record.title, record.content_type, record.traffic_source, record.region, record.device, record.platform))
            if not _match_keyword(searchable, self._search_keyword):
                continue
            if self._selected_source not in {"", "全部"} and record.traffic_source != self._selected_source:
                continue
            if self._selected_region not in {"", "全部"} and record.region != self._selected_region:
                continue
            if self._selected_device not in {"", "全部"} and record.device != self._selected_device:
                continue
            if self._selected_platform not in {"", "全部"} and record.platform != self._selected_platform:
                continue
            records.append(record)
        return records

    def _build_kpi_state(self, records: Sequence[TrafficContentRecord]) -> TrafficKPIState:
        """聚合 KPI 数据。"""

        total_views = sum(record.views for record in records)
        total_followers = sum(record.new_followers for record in records)
        total_visits = sum(record.profile_visits for record in records)
        engagement_rate = _safe_ratio(sum(record.engagement_rate * record.views for record in records), total_views)

        base_series = TRAFFIC_SERIES_BY_TAB[self._current_tab]
        compare_series = COMPARE_TRAFFIC_SERIES[self._current_tab]
        view_change = _series_delta(base_series)
        followers_change = max(0.0, view_change * 0.72) - 0.012
        visits_change = view_change * 0.88 - 0.008
        engagement_change = _safe_ratio(engagement_rate - 0.074, 0.074)

        return TrafficKPIState(
            total_views=total_views,
            new_followers=total_followers,
            profile_visits=total_visits,
            engagement_rate=engagement_rate,
            views_change=view_change,
            followers_change=followers_change,
            visits_change=visits_change,
            engagement_change=engagement_change,
            views_sparkline=tuple(int(value / 4000) for value in base_series[-7:]),
            followers_sparkline=tuple(int(value / 6000) for value in compare_series[-7:]),
            visits_sparkline=tuple(int(value / 5200) for value in base_series[-7:]),
            engagement_sparkline=tuple(round(engagement_rate * factor, 4) for factor in (0.92, 0.94, 0.97, 1.00, 1.01, 1.03, 1.05)),
        )

    def _content_rows(self, records: Sequence[TrafficContentRecord]) -> list[list[object]]:
        """转换内容表格行。"""

        rows: list[list[object]] = []
        for record in records:
            rows.append(
                [
                    record.title,
                    _format_compact(record.views),
                    _format_percent(record.engagement_rate),
                    _format_percent(record.ctr),
                    record.traffic_source,
                    record.region,
                    record.device,
                ]
            )
        return rows

    def _region_rows(self) -> list[list[object]]:
        """转换地区表格行。"""

        rows: list[list[object]] = []
        for region, views, followers, visits, engagement in REGION_ROWS[self._current_tab]:
            if self._selected_region not in {"", "全部"} and region != self._selected_region:
                continue
            rows.append([region, _format_compact(views), _format_compact(followers), _format_compact(visits), _format_percent(engagement)])
        return rows

    def _peak_rows(self) -> list[list[object]]:
        """转换峰值表格行。"""

        return [[time_range, _format_compact(views), _format_percent(engagement), _format_compact(visits), action] for time_range, views, engagement, visits, action in PEAK_ROWS[self._current_tab]]

    def _selected_record(self, records: Sequence[TrafficContentRecord]) -> TrafficContentRecord | None:
        """返回当前选中记录。"""

        if not records:
            return None
        index = max(0, min(self._selected_record_index, len(records) - 1))
        self._selected_record_index = index
        return records[index]

    def _refresh_all_views(self) -> None:
        """刷新全部视图。"""

        records = self._filtered_records()
        kpi_state = self._build_kpi_state(records)
        self._refresh_kpis(kpi_state)
        self._refresh_source_chart()
        self._refresh_trend_views()
        self._refresh_tables(records)
        self._refresh_geo_and_distribution()
        self._refresh_peak_badges()
        self._refresh_device_pulses()
        self._refresh_selection_detail(records)

    def _refresh_kpis(self, state: TrafficKPIState) -> None:
        """刷新 KPI 卡片。"""

        mapping = {
            "总播放量": (_format_compact(state.total_views), state.views_change, state.views_sparkline, "近 30 天整体分发"),
            "新增粉丝": (_format_compact(state.new_followers), state.followers_change, state.followers_sparkline, "内容带粉效率"),
            "主页访问": (_format_compact(state.profile_visits), state.visits_change, state.visits_sparkline, "主页承接强度"),
            "内容互动率": (_format_percent(state.engagement_rate), state.engagement_change, tuple(int(value * 1000) for value in state.engagement_sparkline), "点赞评论分享综合"),
        }
        for title, card in self._kpi_cards.items():
            value_text, delta_value, sparkline, caption = mapping[title]
            card.set_value(value_text)
            card.set_trend(_delta_direction(delta_value), f"{delta_value * 100:+.1f}%")
            card.set_sparkline_data(sparkline)
            _call(card, "setToolTip", caption)

    def _refresh_source_chart(self) -> None:
        """刷新来源图。"""

        if self._source_chart is None:
            return
        self._source_chart.set_chart_type("pie")
        self._source_chart.set_unit("万")
        self._source_chart.set_data(SOURCE_BREAKDOWN[self._current_tab], SOURCE_LABELS)

    def _refresh_trend_views(self) -> None:
        """刷新趋势图与对比图。"""

        if self._trend_chart is not None:
            self._trend_chart.set_chart_type("line")
            self._trend_chart.set_unit("")
            self._trend_chart.set_data(TRAFFIC_SERIES_BY_TAB[self._current_tab], TREND_LABELS)
        if self._trend_comparison is not None:
            self._trend_comparison.set_series(
                TREND_LABELS,
                tuple(float(value) for value in TRAFFIC_SERIES_BY_TAB[self._current_tab]),
                tuple(float(value) for value in COMPARE_TRAFFIC_SERIES[self._current_tab]),
                current_name="本周期",
                compare_name="上一周期",
            )

    def _refresh_tables(self, records: Sequence[TrafficContentRecord]) -> None:
        """刷新表格。"""

        if self._content_table is not None:
            self._content_table.set_rows(self._content_rows(records))
            if records:
                self._content_table.select_absolute_row(min(self._selected_record_index, len(records) - 1))
        if self._region_table is not None:
            self._region_table.set_rows(self._region_rows())
        if self._peak_table is not None:
            self._peak_table.set_rows(self._peak_rows())

    def _refresh_geo_and_distribution(self) -> None:
        """刷新热力与分布图。"""

        if self._geo_heatmap is not None:
            self._geo_heatmap.set_values(GEO_HEATMAP[self._current_tab])
        if self._device_distribution is not None:
            self._device_distribution.set_items(tuple(zip(DEVICE_LABELS, DEVICE_BREAKDOWN[self._current_tab])))
        if self._platform_distribution is not None:
            self._platform_distribution.set_items(tuple(zip(PLATFORM_LABELS, PLATFORM_BREAKDOWN[self._current_tab])))

    def _refresh_peak_badges(self) -> None:
        """刷新高峰状态徽标。"""

        badge_texts = {
            "总流量": ("推荐页晚高峰冲高", "搜索来源稳步抬升", "主页回访维持高位"),
            "内容表现": ("爆款内容集中在 20 点", "教程内容中午转化更好", "晚间标题点击最佳"),
            "地域设备": ("苹果端晚高峰优势更强", "网页端需加强搜索承接", "欧美地区 18 点后放量"),
        }
        for badge, text in zip(self._peak_status_badges, badge_texts[self._current_tab]):
            _call(badge, "setText", text)
            badge.set_tone("success" if "高" in text or "最佳" in text else "info")

    def _refresh_device_pulses(self) -> None:
        """刷新设备脉冲卡片。"""

        pulses = DEVICE_PULSES[self._current_tab]
        for index, pulse in enumerate(pulses):
            if index < len(self._device_sparklines):
                self._device_sparklines[index].set_values(pulse.trend)
            if index < len(self._device_value_labels):
                _call(self._device_value_labels[index], "setText", _format_compact(pulse.visits))
            if index < len(self._device_summary_labels):
                _call(self._device_summary_labels[index], "setText", pulse.summary)

    def _refresh_selection_detail(self, records: Sequence[TrafficContentRecord]) -> None:
        """刷新右侧详情。"""

        record = self._selected_record(records)
        if record is None:
            if self._selected_title_label is not None:
                _call(self._selected_title_label, "setText", "当前筛选暂无内容")
            if self._selected_meta_label is not None:
                _call(self._selected_meta_label, "setText", "请调整来源、地区、设备或关键词")
            if self._selected_summary_label is not None:
                _call(self._selected_summary_label, "setText", "暂无可用样本，建议先清空筛选后查看近 30 天整体流量。")
            for label in (
                self._selected_views_label,
                self._selected_followers_label,
                self._selected_visits_label,
                self._selected_engagement_label,
                self._selected_ctr_label,
                self._selected_completion_label,
            ):
                if label is not None:
                    _call(label, "setText", "-")
            return

        if self._selected_title_label is not None:
            _call(self._selected_title_label, "setText", record.title)
        if self._selected_meta_label is not None:
            _call(self._selected_meta_label, "setText", f"{record.content_type} · 发布时间 {record.publish_hour:02d}:00 · 7 日趋势持续走高")
        if self._selected_summary_label is not None:
            _call(
                self._selected_summary_label,
                "setText",
                f"该内容主要由{record.traffic_source}驱动，在{record.region}与{record.device}终端表现最突出；建议继续放大 {record.publish_hour:02d}:00 前后相似题材素材。",
            )

        for label, value in (
            (self._selected_views_label, _format_compact(record.views)),
            (self._selected_followers_label, _format_compact(record.new_followers)),
            (self._selected_visits_label, _format_compact(record.profile_visits)),
            (self._selected_engagement_label, _format_percent(record.engagement_rate)),
            (self._selected_ctr_label, _format_percent(record.ctr)),
            (self._selected_completion_label, _format_percent(record.completion_rate)),
        ):
            if label is not None:
                _call(label, "setText", value)

        if self._selected_source_badge is not None:
            _call(self._selected_source_badge, "setText", record.traffic_source)
            self._selected_source_badge.set_tone("success" if record.traffic_source == "推荐页" else "info")
        if self._selected_region_badge is not None:
            _call(self._selected_region_badge, "setText", record.region)
            self._selected_region_badge.set_tone("brand")
        if self._selected_device_badge is not None:
            _call(self._selected_device_badge, "setText", record.device)
            self._selected_device_badge.set_tone("warning")
        if self._selected_platform_badge is not None:
            _call(self._selected_platform_badge, "setText", record.platform)
            self._selected_platform_badge.set_tone("neutral")
        if self._selection_hint_label is not None:
            top_point = max(record.trend_points) if record.trend_points else 0
            _call(self._selection_hint_label, "setText", f"建议：保持 {record.publish_hour:02d}:00 发布时间窗口，复制高峰趋势样本，7 日峰值已达 {top_point:,}。")

    def _apply_page_styles(self) -> None:
        """应用页面样式。"""

        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#trafficDashboardPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#trafficToolbar,
            QFrame#trafficDetailCard,
            QFrame#trafficPulseCard,
            QFrame#trafficFooter,
            QFrame#trafficMetricViews,
            QFrame#trafficMetricFollowers,
            QFrame#trafficMetricVisits,
            QFrame#trafficMetricEngagement,
            QFrame#trafficMetricCtr,
            QFrame#trafficMetricCompletion {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#trafficToolbar {{
                border-color: {_rgba(_token('brand.primary'), 0.18)};
            }}
            QLabel#trafficSectionTitle,
            QLabel#trafficSelectionTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#trafficMetricTitle {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                background: transparent;
            }}
            QLabel#trafficMetricValue,
            QLabel#trafficPulseValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                background: transparent;
            }}
            QLabel#trafficSubtleText,
            QLabel#trafficSelectionBody {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                background: transparent;
            }}
            QLabel#trafficAccentHint {{
                color: {_token('brand.primary')};
                background-color: {_rgba(_token('brand.primary'), 0.08)};
                border: 1px solid {_rgba(_token('brand.primary'), 0.22)};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_MD}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            """,
        )

    def on_activated(self) -> None:
        """页面激活时刷新。"""

        self._refresh_all_views()

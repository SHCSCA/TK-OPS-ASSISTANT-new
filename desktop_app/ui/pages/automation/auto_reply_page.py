# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""自动回复控制台页面。"""

from typing import Any

from ....core.qt import QFrame as CoreQFrame, QHBoxLayout as CoreQHBoxLayout, QLabel as CoreQLabel, QPushButton as CoreQPushButton, QVBoxLayout as CoreQVBoxLayout, QWidget as CoreQWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    IconButton,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SplitPanel,
    StatusBadge,
    TabBar,
    TagInput,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedTextEdit,
    ToggleSwitch,
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
from ...components.operations import LogViewer as RealtimeLogViewer
from ...components.tags import BadgeTone
from ..base_page import BasePage

RULE_TABLE_HEADERS = [
    "规则名称",
    "触发词",
    "适用场景",
    "回复方式",
    "今日触发",
    "成功率",
    "AI 智能回复",
    "状态",
]

STATISTICS_CARDS: list[dict[str, str]] = [
    {
        "title": "今日自动回复量",
        "value": "1,286",
        "delta": "+18.6%",
        "caption": "较昨日多处理 202 条咨询",
        "tone": "brand",
    },
    {
        "title": "平均首响时长",
        "value": "2.4 秒",
        "delta": "-0.8 秒",
        "caption": "夜间咨询响应明显提速",
        "tone": "success",
    },
    {
        "title": "规则命中率",
        "value": "86.2%",
        "delta": "+4.1%",
        "caption": "高频问题已覆盖到价格与物流场景",
        "tone": "info",
    },
    {
        "title": "人工转接占比",
        "value": "13.8%",
        "delta": "-2.3%",
        "caption": "更多简单问题被规则自动消化",
        "tone": "warning",
    },
]

AUTO_REPLY_LOGS: list[dict[str, str]] = [
    {
        "level": "成功",
        "time": "2026-03-09 14:20:45",
        "message": "会话 user_9281 命中规则【价格咨询标准答复】，已发送报价模板并附带限时活动说明。",
    },
    {
        "level": "成功",
        "time": "2026-03-09 14:19:12",
        "message": "新访客 user_1024 触发规则【欢迎语首句】，系统已推送欢迎语与热销款引导。",
    },
    {
        "level": "忽略",
        "time": "2026-03-09 14:15:30",
        "message": "会话 user_7741 命中黑名单词【退款威胁】，已跳过自动回复并标记为优先人工跟进。",
    },
    {
        "level": "预警",
        "time": "2026-03-09 14:12:01",
        "message": "规则【人工客服转接】连续命中 6 次，建议排查高峰时段排班是否充足。",
    },
    {
        "level": "成功",
        "time": "2026-03-09 14:08:26",
        "message": "会话 user_8892 命中规则【物流时效说明】，自动回复预计 48 小时内发货并同步物流节点。",
    },
    {
        "level": "成功",
        "time": "2026-03-09 14:05:49",
        "message": "AI 智能补全已为 user_3520 生成尺码建议，结合历史退货原因自动强调偏小半码。",
    },
    {
        "level": "忽略",
        "time": "2026-03-09 14:03:11",
        "message": "会话 user_6203 在 60 秒内重复发送 4 条相同消息，系统触发去重策略，未再次回复。",
    },
    {
        "level": "成功",
        "time": "2026-03-09 13:58:36",
        "message": "会话 user_1835 命中规则【催付提醒跟进】，订单优惠倒计时消息已成功发送。",
    },
    {
        "level": "预警",
        "time": "2026-03-09 13:55:40",
        "message": "规则【离线兜底回复】当前关闭，13:00-14:00 时段出现 9 条未及时覆盖会话。",
    },
    {
        "level": "成功",
        "time": "2026-03-09 13:52:08",
        "message": "会话 user_5408 命中规则【售后安抚模板】，系统已发送补发登记表单链接。",
    },
]

RECENT_CONVERSATIONS: list[dict[str, str]] = [
    {
        "customer": "用户 user_9281",
        "scene": "价格咨询",
        "status": "已自动回复",
        "summary": "客户询问短视频套餐收费，系统返回基础版 / 专业版 / 企业版三档价格。",
        "rule": "价格咨询标准答复",
    },
    {
        "customer": "用户 user_3520",
        "scene": "尺码建议",
        "status": "AI 智能补全",
        "summary": "客户提供身高体重，AI 根据近 30 天退货尺码原因补充了偏小半码提示。",
        "rule": "尺码推荐智能答复",
    },
    {
        "customer": "用户 user_7741",
        "scene": "敏感投诉",
        "status": "转人工",
        "summary": "客户连续提及退款与差评，系统仅发送安抚开场语后转给高级客服。",
        "rule": "售后情绪安抚",
    },
    {
        "customer": "用户 user_1835",
        "scene": "催付提醒",
        "status": "已成交",
        "summary": "系统在优惠券失效前 12 分钟发送催付提醒，客户当场完成付款。",
        "rule": "催付提醒跟进",
    },
]

DEMO_RULES: list[dict[str, Any]] = [
    {
        "id": "rule-price-standard",
        "name": "价格咨询标准答复",
        "scene": "售前咨询",
        "channel": "店铺私信",
        "match_mode": "包含任意关键词",
        "reply_mode": "模板 + AI 补充",
        "priority": "高优先级",
        "enabled": True,
        "ai_enabled": True,
        "ai_tone": "专业成交型",
        "risk_strategy": "敏感词先审后发",
        "delay": "2.5",
        "daily_limit": "300",
        "quiet_period": "00:30-07:30",
        "success_rate": "93.6%",
        "today_hits": "326",
        "today_success": "305",
        "manual_takeover": "21",
        "conversion": "18.4%",
        "last_trigger": "14:20",
        "owner": "售后客服 A 组",
        "keywords": ["价格", "收费", "多少钱", "套餐", "优惠"],
        "template": """您好，当前店铺的服务方案如下：
1. 基础版：99 元 / 月，适合刚起步的新店；
2. 专业版：199 元 / 月，支持选品建议与话术优化；
3. 企业版：按店铺规模定制，支持专属顾问与数据看板。

如果您告诉我当前经营类目、月销目标或团队规模，我还可以继续帮您推荐更适合的方案。""",
        "condition_logic": "全部满足",
        "conditions": [
            {"field": "咨询来源", "operator": "属于", "value": "短视频 / 商品卡"},
            {"field": "客户标签", "operator": "不包含", "value": "高风险 / 恶意咨询"},
            {"field": "近 10 分钟重复问价次数", "operator": "小于", "value": "3 次"},
        ],
        "notes": [
            "价格类问题命中后优先回复套餐，不直接承诺额外折扣。",
            "如用户已下单但仍追问价格，AI 会改写为老客续费说明。",
            "内容促销时段允许附带“限时优惠”变量。",
        ],
        "examples": [
            "现在做一套短视频代运营多少钱？",
            "你们专业版怎么收费？",
            "新店可以先买基础版吗？",
        ],
    },
    {
        "id": "rule-welcome-first",
        "name": "欢迎语首句",
        "scene": "新访客接待",
        "channel": "店铺私信",
        "match_mode": "首次进入自动触发",
        "reply_mode": "纯模板",
        "priority": "中优先级",
        "enabled": True,
        "ai_enabled": False,
        "ai_tone": "亲和接待型",
        "risk_strategy": "直接发送",
        "delay": "1.2",
        "daily_limit": "999",
        "quiet_period": "无",
        "success_rate": "98.8%",
        "today_hits": "482",
        "today_success": "476",
        "manual_takeover": "6",
        "conversion": "11.2%",
        "last_trigger": "14:19",
        "owner": "接待机器人",
        "keywords": ["首次会话", "进店欢迎", "新访客"],
        "template": """您好，欢迎来到 TK-OPS 运营支持台～
我是您的自动回复助手，您可以直接发送【价格】【物流】【发货】【人工】等关键词，我会先帮您快速处理。

如果您正在看短视频，也可以把商品链接发给我，我会优先帮您定位对应问题。""",
        "condition_logic": "任一满足",
        "conditions": [
            {"field": "是否首次会话", "operator": "等于", "value": "是"},
            {"field": "历史 30 天咨询次数", "operator": "小于", "value": "2 次"},
        ],
        "notes": [
            "欢迎语中优先引导常见关键词，缩短用户试探成本。",
            "凌晨时段自动追加“看到后第一时间回复您”的缓冲语。",
        ],
        "examples": [
            "新用户刚进店还没有发送任何消息",
            "客户发送“你好”或“在吗”",
        ],
    },
    {
        "id": "rule-logistics-timing",
        "name": "物流时效说明",
        "scene": "发货咨询",
        "channel": "商品详情页咨询",
        "match_mode": "包含任意关键词",
        "reply_mode": "模板",
        "priority": "高优先级",
        "enabled": True,
        "ai_enabled": False,
        "ai_tone": "清晰说明型",
        "risk_strategy": "直接发送",
        "delay": "2.0",
        "daily_limit": "260",
        "quiet_period": "无",
        "success_rate": "91.4%",
        "today_hits": "188",
        "today_success": "172",
        "manual_takeover": "16",
        "conversion": "9.4%",
        "last_trigger": "14:08",
        "owner": "物流支持组",
        "keywords": ["多久发货", "什么时候到", "物流", "几天能到", "发什么快递"],
        "template": """您好，常规订单会在 48 小时内安排发出，预售或定制款会按商品页标注时间发货。
发出后系统会同步物流单号，江浙沪通常 1-2 天送达，其它地区大多 3-5 天内送达。

如果您着急使用，可以把收货城市发给我，我再帮您确认是否支持优先发货。""",
        "condition_logic": "全部满足",
        "conditions": [
            {"field": "订单状态", "operator": "不等于", "value": "已签收"},
            {"field": "商品类型", "operator": "不包含", "value": "定制无现货"},
            {"field": "今日同一用户触发次数", "operator": "小于", "value": "4 次"},
        ],
        "notes": [
            "物流延迟超过 72 小时则建议转人工核查。",
            "预售场景优先插入预计发货日期变量。",
        ],
        "examples": [
            "今天拍下能明天发吗？",
            "北京几天到？",
            "是什么快递呀？",
        ],
    },
    {
        "id": "rule-human-transfer",
        "name": "人工客服转接",
        "scene": "复杂问题转人工",
        "channel": "全渠道",
        "match_mode": "精准关键词",
        "reply_mode": "模板",
        "priority": "最高优先级",
        "enabled": True,
        "ai_enabled": False,
        "ai_tone": "安抚过渡型",
        "risk_strategy": "直接发送",
        "delay": "0.8",
        "daily_limit": "999",
        "quiet_period": "无",
        "success_rate": "99.1%",
        "today_hits": "74",
        "today_success": "73",
        "manual_takeover": "73",
        "conversion": "--",
        "last_trigger": "14:12",
        "owner": "客服主管值班池",
        "keywords": ["人工", "客服", "转人工", "投诉", "负责人"],
        "template": """收到，我这边先帮您转接人工客服，请稍等 1-3 分钟。
为了让同事更快处理，您也可以补充一下订单号、商品链接或具体问题，我们会优先查看。""",
        "condition_logic": "任一满足",
        "conditions": [
            {"field": "消息内容", "operator": "包含", "value": "人工 / 投诉 / 负责人"},
            {"field": "情绪分值", "operator": "大于", "value": "0.72"},
            {"field": "近 5 分钟未解决轮次", "operator": "大于", "value": "3 轮"},
        ],
        "notes": [
            "该规则始终高于价格与物流规则。",
            "若对话中包含退款、投诉、平台介入等词，立即抢占回复。",
        ],
        "examples": [
            "我要找人工客服",
            "这个问题机器人解决不了",
            "我要投诉你们处理太慢",
        ],
    },
    {
        "id": "rule-size-ai",
        "name": "尺码推荐智能答复",
        "scene": "尺码咨询",
        "channel": "短视频商品卡",
        "match_mode": "关键词 + AI 语义识别",
        "reply_mode": "AI 智能回复",
        "priority": "高优先级",
        "enabled": True,
        "ai_enabled": True,
        "ai_tone": "顾问推荐型",
        "risk_strategy": "命中尺码词后再生成",
        "delay": "3.0",
        "daily_limit": "220",
        "quiet_period": "无",
        "success_rate": "84.9%",
        "today_hits": "96",
        "today_success": "82",
        "manual_takeover": "14",
        "conversion": "15.7%",
        "last_trigger": "14:05",
        "owner": "商品顾问机器人",
        "keywords": ["尺码", "多大", "身高", "体重", "码数"],
        "template": """我先根据您提供的身高、体重和穿着偏好帮您推荐尺码。
如果您方便的话，请补充一下【身高 / 体重 / 喜欢宽松还是合身】，我会结合近期退换货原因给您更稳妥的建议。""",
        "condition_logic": "全部满足",
        "conditions": [
            {"field": "商品类目", "operator": "属于", "value": "服饰 / 鞋靴"},
            {"field": "用户消息长度", "operator": "大于", "value": "4 字"},
            {"field": "尺码表是否完整", "operator": "等于", "value": "是"},
        ],
        "notes": [
            "AI 会自动引用当前商品的尺码表与近 7 天退货原因。",
            "如客户未提供体重，则只发送补充信息引导，不直接推荐。",
            "当商品库存紧张时，会额外提醒先锁单。",
        ],
        "examples": [
            "165 斤穿多大？",
            "173/68kg 选 L 还是 XL？",
            "鞋码偏大还是偏小？",
        ],
    },
    {
        "id": "rule-payment-reminder",
        "name": "催付提醒跟进",
        "scene": "成交转化",
        "channel": "购物车消息",
        "match_mode": "订单行为触发",
        "reply_mode": "模板 + AI 补充",
        "priority": "中优先级",
        "enabled": True,
        "ai_enabled": True,
        "ai_tone": "限时成交型",
        "risk_strategy": "优惠信息校验后发送",
        "delay": "4.0",
        "daily_limit": "120",
        "quiet_period": "23:30-08:30",
        "success_rate": "79.3%",
        "today_hits": "54",
        "today_success": "43",
        "manual_takeover": "5",
        "conversion": "27.8%",
        "last_trigger": "13:58",
        "owner": "转化运营组",
        "keywords": ["待支付", "优惠快结束", "购物车停留", "催付"],
        "template": """您好，看到您已加入购物车但还没有完成付款～
当前这款商品的优惠还有一段时间就结束，如果您担心尺码、发货或活动规则，我可以马上帮您确认。

回复【下单】我会继续给您发送当前可用优惠信息。""",
        "condition_logic": "全部满足",
        "conditions": [
            {"field": "订单状态", "operator": "等于", "value": "待支付"},
            {"field": "距优惠结束时间", "operator": "小于", "value": "90 分钟"},
            {"field": "近 24 小时催付次数", "operator": "小于", "value": "2 次"},
        ],
        "notes": [
            "催付消息只在用户有真实互动记录时触发。",
            "AI 会根据停留商品自动替换卖点和优惠倒计时。",
        ],
        "examples": [
            "客户加入购物车超过 3 小时未支付",
            "优惠券即将失效且客户已问过物流",
        ],
    },
    {
        "id": "rule-after-sale-soothe",
        "name": "售后情绪安抚",
        "scene": "售后处理",
        "channel": "全渠道",
        "match_mode": "情绪识别 + 关键词",
        "reply_mode": "模板",
        "priority": "最高优先级",
        "enabled": True,
        "ai_enabled": False,
        "ai_tone": "安抚稳态型",
        "risk_strategy": "先安抚后转人工",
        "delay": "1.0",
        "daily_limit": "80",
        "quiet_period": "无",
        "success_rate": "88.0%",
        "today_hits": "31",
        "today_success": "27",
        "manual_takeover": "27",
        "conversion": "--",
        "last_trigger": "13:52",
        "owner": "售后值班组",
        "keywords": ["退款", "差评", "生气", "投诉", "发错货"],
        "template": """非常抱歉给您带来不好的体验，我已经先帮您记录问题。
请您放心，我们会优先安排人工客服尽快处理；如果方便的话，您可以补充订单号、收到的商品照片或问题细节，我们会加速跟进。""",
        "condition_logic": "任一满足",
        "conditions": [
            {"field": "情绪分值", "operator": "大于", "value": "0.75"},
            {"field": "消息内容", "operator": "包含", "value": "退款 / 差评 / 投诉"},
            {"field": "售后工单状态", "operator": "等于", "value": "未创建"},
        ],
        "notes": [
            "不主动给出赔付承诺，只做安抚和信息收集。",
            "命中后自动打标签“高风险售后”。",
        ],
        "examples": [
            "东西发错了还让我等？",
            "我要退款，不然就投诉",
        ],
    },
    {
        "id": "rule-offline-fallback",
        "name": "离线兜底回复",
        "scene": "夜间接待",
        "channel": "全渠道",
        "match_mode": "非工作时段自动触发",
        "reply_mode": "纯模板",
        "priority": "低优先级",
        "enabled": False,
        "ai_enabled": False,
        "ai_tone": "礼貌等待型",
        "risk_strategy": "直接发送",
        "delay": "6.0",
        "daily_limit": "999",
        "quiet_period": "无",
        "success_rate": "72.6%",
        "today_hits": "35",
        "today_success": "24",
        "manual_takeover": "11",
        "conversion": "5.1%",
        "last_trigger": "昨晚 23:48",
        "owner": "夜间守护策略",
        "keywords": ["非工作时间", "离线", "无人值守"],
        "template": """您好，目前值班客服正在处理中，可能无法立即回复您。
您可以先留言商品链接、订单号或问题内容，我们上线后会按顺序第一时间为您处理，感谢理解。""",
        "condition_logic": "全部满足",
        "conditions": [
            {"field": "当前时间", "operator": "属于", "value": "23:00-08:00"},
            {"field": "人工在线状态", "operator": "等于", "value": "离线"},
            {"field": "已启用值班机器人", "operator": "等于", "value": "否"},
        ],
        "notes": [
            "当前处于关闭状态，仅用于夜班缺口兜底。",
            "建议与值班排班联动，避免覆盖真人客服。",
        ],
        "examples": [
            "凌晨咨询但无人在线",
            "售后留资等待次日回访",
        ],
    },
]


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    cleaned = hex_color.strip().lstrip("#")
    if len(cleaned) != 6:
        return hex_color
    red = int(cleaned[0:2], 16)
    green = int(cleaned[2:4], 16)
    blue = int(cleaned[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _clear_layout(layout: object) -> None:
    """清空布局中已有内容。"""

    count_method = getattr(layout, "count", None)
    take_at_method = getattr(layout, "takeAt", None)
    if callable(count_method) and callable(take_at_method):
        while True:
            count_value = count_method()
            if not isinstance(count_value, int) or count_value <= 0:
                break
            item = take_at_method(0)
            if item is None:
                break
            widget_method = getattr(item, "widget", None)
            if callable(widget_method):
                widget = widget_method()
                if widget is not None:
                    _call(widget, "setParent", None)
                    _call(widget, "deleteLater")
            child_layout_method = getattr(item, "layout", None)
            if callable(child_layout_method):
                child_layout = child_layout_method()
                if child_layout is not None:
                    _clear_layout(child_layout)
        return
    raw_items = getattr(layout, "_items", None)
    if isinstance(raw_items, list):
        raw_items.clear()


def _copy_rule(rule: dict[str, Any]) -> dict[str, Any]:
    """深拷贝规则字典，便于本地编辑。"""

    copied: dict[str, Any] = {}
    for key, value in rule.items():
        if isinstance(value, list):
            copied[key] = [item.copy() if isinstance(item, dict) else item for item in value]
            continue
        if isinstance(value, dict):
            copied[key] = value.copy()
            continue
        copied[key] = value
    return copied


def _toggle_text(enabled: bool) -> str:
    """返回开关状态文本。"""

    return "已开启" if enabled else "已关闭"


def _smart_reply_text(enabled: bool) -> str:
    """返回 AI 状态文本。"""

    return "已启用" if enabled else "未启用"


def _badge_tone_from_enabled(enabled: bool) -> BadgeTone:
    """根据启停状态返回徽标色调。"""

    return "success" if enabled else "neutral"


def _rule_table_row(rule: dict[str, Any]) -> list[object]:
    """转换为表格行。"""

    keywords = rule.get("keywords", [])
    preview = " / ".join(str(item) for item in keywords[:3])
    if len(keywords) > 3:
        preview = f"{preview} 等 {len(keywords)} 个"
    return [
        str(rule.get("name", "")),
        preview,
        str(rule.get("scene", "")),
        str(rule.get("reply_mode", "")),
        str(rule.get("today_hits", "0")),
        str(rule.get("success_rate", "--")),
        _smart_reply_text(bool(rule.get("ai_enabled", False))),
        _toggle_text(bool(rule.get("enabled", False))),
    ]


class AutoReplyPage(BasePage):
    """自动回复控制台页面。"""

    default_route_id = RouteId("auto_reply_console")
    default_display_name = "自动回复控制台"
    default_icon_name = "robot_2"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        self._page_enabled = True
        self._rules: list[dict[str, Any]] = [_copy_rule(rule) for rule in DEMO_RULES]
        self._filtered_rules: list[dict[str, Any]] = list(self._rules)
        self._selected_rule_id: str = str(self._rules[0]["id"]) if self._rules else ""
        self._rule_card_widgets: list[dict[str, object]] = []
        self._condition_editors: list[dict[str, object]] = []
        self._editor_widgets: dict[str, object] = {}
        self._metric_value_labels: list[QLabel] = []
        self._metric_delta_labels: list[QLabel] = []
        self._metric_caption_labels: list[QLabel] = []
        self._metric_title_labels: list[QLabel] = []
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建自动回复控制台页面。"""

        colors = _palette()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget {{
                color: {colors.text};
                font-family: {_static_token('font.family.chinese')};
            }}
            QWidget#autoReplyRoot {{
                background-color: {_token('surface.primary')};
            }}
            QFrame#consoleBanner,
            QFrame#ruleSidebarPanel,
            QFrame#editorPanel,
            QFrame#monitorPanel,
            QFrame#miniPanel,
            QFrame#metricCard,
            QFrame#ruleCard,
            QFrame#conditionCard,
            QFrame#conversationCard,
            QFrame#previewPanel,
            QFrame#summaryStrip,
            QFrame#statusPanel,
            QFrame#smartReplyHero {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#sectionTitle {{
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.text};
                background: transparent;
            }}
            QLabel#sectionCaption {{
                font-size: {_static_token('font.size.sm')};
                color: {colors.text_muted};
                background: transparent;
            }}
            QLabel#metricValue {{
                font-size: {_static_token('font.size.xxl')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.text};
                background: transparent;
            }}
            QLabel#metricTitle {{
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
                color: {colors.text_muted};
                background: transparent;
            }}
            QLabel#metricDelta {{
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.primary};
                background: transparent;
            }}
            QLabel#metricCaption {{
                font-size: {_static_token('font.size.xs')};
                color: {colors.text_muted};
                background: transparent;
            }}
            QLabel#panelKicker {{
                font-size: {_static_token('font.size.xs')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.primary};
                background: transparent;
            }}
            QLabel#panelValue {{
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.text};
                background: transparent;
            }}
            QLabel#summaryLabel {{
                font-size: {_static_token('font.size.sm')};
                color: {colors.text_muted};
                background: transparent;
            }}
            QLabel#summaryValue {{
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.text};
                background: transparent;
            }}
            QLabel#conditionText,
            QLabel#exampleText,
            QLabel#noteText,
            QLabel#conversationText,
            QLabel#previewText {{
                font-size: {_static_token('font.size.sm')};
                color: {colors.text};
                background: transparent;
            }}
            QLabel#mutedTiny {{
                font-size: {_static_token('font.size.xs')};
                color: {colors.text_muted};
                background: transparent;
            }}
            QPushButton#ghostChip {{
                background-color: {_rgba(colors.primary, 0.08)};
                color: {colors.primary};
                border: 1px solid {_rgba(colors.primary, 0.20)};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_MD}px;
                min-height: {BUTTON_HEIGHT - SPACING_SM}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#ghostChip:hover {{
                background-color: {_rgba(colors.primary, 0.12)};
            }}
            """,
        )

        root = QWidget(self)
        _call(root, "setObjectName", "autoReplyRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.layout.addWidget(root)

        refresh_button = IconButton("↻", "刷新实时状态", self)
        new_rule_button = PrimaryButton("新增规则", self, icon_text="＋")
        _connect(getattr(refresh_button, "clicked", None), self._refresh_all_views)
        _connect(getattr(new_rule_button, "clicked", None), self._on_create_rule)

        container = PageContainer(
            title="自动回复控制台",
            description="统一管理 TikTok Shop 私信、店铺私信、商品卡等场景下的自动回复规则、AI 补全策略与实时执行日志。",
            actions=[refresh_button, new_rule_button],
            parent=root,
        )
        container.content_layout.setSpacing(SPACING_2XL)
        root_layout.addWidget(container)

        container.add_widget(self._build_console_banner())
        container.add_widget(self._build_statistics_row())
        container.add_widget(self._build_workspace())

        self._populate_log_viewer()
        self._refresh_all_views()

    def _build_console_banner(self) -> QWidget:
        """构建总开关横幅。"""

        colors = _palette()
        banner = QFrame(self)
        _call(banner, "setObjectName", "consoleBanner")
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        left = QWidget(banner)
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(SPACING_XL)

        icon_badge = QLabel("◎", left)
        _call(icon_badge, "setObjectName", "panelValue")
        _call(
            icon_badge,
            "setStyleSheet",
            f"background-color: {_rgba(colors.primary, 0.14)}; color: {colors.primary}; border-radius: {RADIUS_LG}px; min-width: 56px; min-height: 56px; max-width: 56px; max-height: 56px; qproperty-alignment: AlignCenter;",
        )

        text_host = QWidget(left)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)

        title = QLabel("启用智能自动回复", text_host)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel(
            "开启后，系统将根据规则优先级、关键词匹配、场景条件与 AI 策略自动响应客户消息；敏感对话会优先转人工。",
            text_host,
        )
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(SPACING_MD)
        self._system_status_badge = StatusBadge("系统运行中", "success", text_host)
        self._coverage_badge = StatusBadge("规则覆盖 8 个高频场景", "brand", text_host)
        self._risk_badge = StatusBadge("风险会话自动转人工", "warning", text_host)
        badge_row.addWidget(self._system_status_badge)
        badge_row.addWidget(self._coverage_badge)
        badge_row.addWidget(self._risk_badge)
        badge_row.addStretch(1)

        text_layout.addWidget(title)
        text_layout.addWidget(caption)
        text_layout.addLayout(badge_row)

        left_layout.addWidget(icon_badge)
        left_layout.addWidget(text_host, 1)

        right = QWidget(banner)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_SM)

        switch_row = QHBoxLayout()
        switch_row.setContentsMargins(0, 0, 0, 0)
        switch_row.setSpacing(SPACING_MD)
        switch_label = QLabel("总开关", right)
        _call(switch_label, "setObjectName", "summaryLabel")
        self._console_toggle = ToggleSwitch(True)
        _connect(getattr(self._console_toggle, "toggled", None), self._on_console_toggled)
        switch_row.addStretch(1)
        switch_row.addWidget(switch_label)
        switch_row.addWidget(self._console_toggle)

        summary = QLabel("当前规则：6 条开启 / 2 条关闭", right)
        _call(summary, "setObjectName", "summaryValue")
        summary_tip = QLabel("高峰时段建议保留人工客服转接与售后安抚规则。", right)
        _call(summary_tip, "setObjectName", "summaryLabel")
        _call(summary_tip, "setWordWrap", True)
        self._console_summary_label = summary

        right_layout.addLayout(switch_row)
        right_layout.addWidget(summary)
        right_layout.addWidget(summary_tip)

        layout.addWidget(left, 1)
        layout.addWidget(right)
        return banner

    def _build_statistics_row(self) -> QWidget:
        """构建统计卡片行。"""

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        self._metric_value_labels.clear()
        self._metric_delta_labels.clear()
        self._metric_caption_labels.clear()
        self._metric_title_labels.clear()

        for item in STATISTICS_CARDS:
            card = QFrame(row)
            _call(card, "setObjectName", "metricCard")
            _call(card, "setProperty", "tone", item.get("tone", "brand"))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
            card_layout.setSpacing(SPACING_SM)

            title = QLabel(item["title"], card)
            _call(title, "setObjectName", "metricTitle")
            value = QLabel(item["value"], card)
            _call(value, "setObjectName", "metricValue")
            delta = QLabel(item["delta"], card)
            _call(delta, "setObjectName", "metricDelta")
            caption = QLabel(item["caption"], card)
            _call(caption, "setObjectName", "metricCaption")
            _call(caption, "setWordWrap", True)

            card_layout.addWidget(title)
            card_layout.addWidget(value)
            card_layout.addWidget(delta)
            card_layout.addWidget(caption)
            card_layout.addStretch(1)
            layout.addWidget(card, 1)

            self._metric_title_labels.append(title)
            self._metric_value_labels.append(value)
            self._metric_delta_labels.append(delta)
            self._metric_caption_labels.append(caption)

        return row

    def _build_workspace(self) -> QWidget:
        """构建主体三栏工作区。"""

        outer_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.28, 0.72),
            minimum_sizes=(320, 760),
            parent=self,
        )
        right_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.55, 0.45),
            minimum_sizes=(460, 360),
            parent=outer_split,
        )
        outer_split.set_widgets(self._build_rule_sidebar(), right_split)
        right_split.set_widgets(self._build_editor_panel(), self._build_monitor_panel())
        return outer_split

    def _build_rule_sidebar(self) -> QWidget:
        """构建左侧规则列表栏。"""

        panel = QFrame(self)
        _call(panel, "setObjectName", "ruleSidebarPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        header = QWidget(panel)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_SM)
        title = QLabel("回复规则列表", header)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("先在左侧筛选规则，再在中间编辑模板、条件与 AI 策略。", header)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        header_layout.addWidget(title)
        header_layout.addWidget(caption)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(SPACING_MD)
        self._rule_search = SearchBar("搜索规则名、关键词或场景")
        self._scene_filter = ThemedComboBox("场景筛选", ["全部场景", "售前咨询", "新访客接待", "发货咨询", "复杂问题转人工", "尺码咨询", "成交转化", "售后处理", "夜间接待"])
        self._status_filter = ThemedComboBox("启停状态", ["全部状态", "仅看已开启", "仅看已关闭"])
        _connect(getattr(self._rule_search, "search_changed", None), self._apply_filters)
        _connect(getattr(self._scene_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._status_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        action_row.addWidget(self._rule_search, 2)
        action_row.addWidget(self._scene_filter, 1)
        action_row.addWidget(self._status_filter, 1)

        quick_row = QHBoxLayout()
        quick_row.setContentsMargins(0, 0, 0, 0)
        quick_row.setSpacing(SPACING_MD)
        clone_button = PrimaryButton("复制当前规则", panel, icon_text="⎘")
        batch_button = IconButton("⋯", "更多规则操作", panel)
        _connect(getattr(clone_button, "clicked", None), self._on_clone_rule)
        _connect(getattr(batch_button, "clicked", None), self._append_batch_hint_log)
        quick_row.addWidget(clone_button, 1)
        quick_row.addWidget(batch_button)

        self._rule_cards_host = QWidget(panel)
        self._rule_cards_layout = QVBoxLayout(self._rule_cards_host)
        self._rule_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._rule_cards_layout.setSpacing(SPACING_MD)

        bottom_summary = QFrame(panel)
        _call(bottom_summary, "setObjectName", "miniPanel")
        bottom_layout = QVBoxLayout(bottom_summary)
        bottom_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        bottom_layout.setSpacing(SPACING_SM)
        kicker = QLabel("当前班次", bottom_summary)
        _call(kicker, "setObjectName", "panelKicker")
        value = QLabel("企业高级版 · 自动接待中", bottom_summary)
        _call(value, "setObjectName", "panelValue")
        tip = QLabel("价格、物流、欢迎语与售后安抚规则处于主力命中区间。", bottom_summary)
        _call(tip, "setObjectName", "summaryLabel")
        _call(tip, "setWordWrap", True)
        bottom_layout.addWidget(kicker)
        bottom_layout.addWidget(value)
        bottom_layout.addWidget(tip)

        layout.addWidget(header)
        layout.addLayout(action_row)
        layout.addLayout(quick_row)
        layout.addWidget(self._rule_cards_host, 1)
        layout.addWidget(bottom_summary)
        return panel

    def _build_editor_panel(self) -> QWidget:
        """构建中间规则编辑器。"""

        panel = QFrame(self)
        _call(panel, "setObjectName", "editorPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        header = QWidget(panel)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)
        title_host = QWidget(header)
        title_layout = QVBoxLayout(title_host)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_XS)
        title = QLabel("规则编辑器", title_host)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("编辑触发关键词、回复模板、命中条件与 AI 智能回复策略。", title_host)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        title_layout.addWidget(title)
        title_layout.addWidget(caption)

        self._selected_rule_badge = StatusBadge("当前规则：价格咨询标准答复", "brand", header)
        header_layout.addWidget(title_host, 1)
        header_layout.addWidget(self._selected_rule_badge)

        summary_strip = QFrame(panel)
        _call(summary_strip, "setObjectName", "summaryStrip")
        summary_layout = QHBoxLayout(summary_strip)
        summary_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        summary_layout.setSpacing(SPACING_XL)
        self._summary_labels: dict[str, QLabel] = {}
        for label_text, key in (
            ("规则优先级", "priority"),
            ("今日触发", "today_hits"),
            ("转人工", "manual_takeover"),
            ("最新命中", "last_trigger"),
        ):
            block = QWidget(summary_strip)
            block_layout = QVBoxLayout(block)
            block_layout.setContentsMargins(0, 0, 0, 0)
            block_layout.setSpacing(2)
            label = QLabel(label_text, block)
            _call(label, "setObjectName", "summaryLabel")
            value = QLabel("--", block)
            _call(value, "setObjectName", "summaryValue")
            block_layout.addWidget(label)
            block_layout.addWidget(value)
            summary_layout.addWidget(block)
            self._summary_labels[key] = value
        summary_layout.addStretch(1)

        basic_section = ContentSection("规则基础设置", "⚙", parent=panel)
        basic_grid = QWidget(basic_section)
        basic_layout = QHBoxLayout(basic_grid)
        basic_layout.setContentsMargins(0, 0, 0, 0)
        basic_layout.setSpacing(SPACING_XL)

        self._editor_widgets["name"] = ThemedLineEdit("规则名称", "请输入规则名称", "建议使用“场景 + 目的”的命名方式")
        self._editor_widgets["scene"] = ThemedComboBox("适用场景", ["售前咨询", "新访客接待", "发货咨询", "复杂问题转人工", "尺码咨询", "成交转化", "售后处理", "夜间接待"])
        self._editor_widgets["channel"] = ThemedComboBox("触发渠道", ["店铺私信", "店铺私信", "商品详情页咨询", "短视频商品卡", "购物车消息", "全渠道"])
        self._editor_widgets["match_mode"] = ThemedComboBox("匹配方式", ["包含任意关键词", "精准关键词", "关键词 + AI 语义识别", "首次进入自动触发", "订单行为触发", "非工作时段自动触发"])
        basic_layout.addWidget(self._editor_widgets["name"], 2)
        basic_layout.addWidget(self._editor_widgets["scene"], 1)
        basic_layout.addWidget(self._editor_widgets["channel"], 1)
        basic_layout.addWidget(self._editor_widgets["match_mode"], 1)
        basic_section.add_widget(basic_grid)

        trigger_section = ContentSection("触发关键词与回复模板", "✦", parent=panel)
        self._editor_widgets["keywords"] = TagInput("触发关键词", "输入关键词后回车确认，例如：价格、物流、人工")
        self._editor_widgets["template"] = ThemedTextEdit("回复模板", "请输入自动回复内容，支持后续接入变量占位符")
        trigger_section.add_widget(self._editor_widgets["keywords"])
        trigger_section.add_widget(self._editor_widgets["template"])

        shortcut_row = QHBoxLayout()
        shortcut_row.setContentsMargins(0, 0, 0, 0)
        shortcut_row.setSpacing(SPACING_MD)
        for label_text, handler in (
            ("插入订单变量", self._insert_order_variable),
            ("插入活动倒计时", self._insert_campaign_variable),
            ("插入人工转接提示", self._insert_handoff_hint),
        ):
            button = QPushButton(label_text, trigger_section)
            _call(button, "setObjectName", "ghostChip")
            _connect(getattr(button, "clicked", None), handler)
            shortcut_row.addWidget(button)
        shortcut_row.addStretch(1)
        trigger_section.add_widget(self._wrap_layout(shortcut_row, trigger_section))

        conditions_section = ContentSection("命中条件与发送节奏", "⌁", parent=panel)
        condition_header = QWidget(conditions_section)
        condition_header_layout = QHBoxLayout(condition_header)
        condition_header_layout.setContentsMargins(0, 0, 0, 0)
        condition_header_layout.setSpacing(SPACING_MD)
        self._editor_widgets["condition_logic"] = ThemedComboBox("条件关系", ["全部满足", "任一满足"])
        self._editor_widgets["delay"] = ThemedLineEdit("延迟回复（秒）", "如：2.5", "设置轻微延迟可让自动回复更接近真人节奏")
        self._editor_widgets["daily_limit"] = ThemedLineEdit("单日触发上限", "如：300", "超过上限后不再自动发送，避免刷屏")
        self._editor_widgets["quiet_period"] = ThemedLineEdit("静默时段", "如：00:30-07:30", "为空则默认全天可触发")
        condition_header_layout.addWidget(self._editor_widgets["condition_logic"], 1)
        condition_header_layout.addWidget(self._editor_widgets["delay"], 1)
        condition_header_layout.addWidget(self._editor_widgets["daily_limit"], 1)
        condition_header_layout.addWidget(self._editor_widgets["quiet_period"], 1)
        conditions_section.add_widget(condition_header)

        self._conditions_host = QWidget(conditions_section)
        self._conditions_layout = QVBoxLayout(self._conditions_host)
        self._conditions_layout.setContentsMargins(0, 0, 0, 0)
        self._conditions_layout.setSpacing(SPACING_MD)
        conditions_section.add_widget(self._conditions_host)

        condition_action_row = QHBoxLayout()
        condition_action_row.setContentsMargins(0, 0, 0, 0)
        condition_action_row.setSpacing(SPACING_MD)
        add_condition_button = QPushButton("新增条件", conditions_section)
        _call(add_condition_button, "setObjectName", "ghostChip")
        _connect(getattr(add_condition_button, "clicked", None), self._append_empty_condition)
        condition_tip = QLabel("建议至少配置 2-3 条限制条件，降低误触发概率。", conditions_section)
        _call(condition_tip, "setObjectName", "summaryLabel")
        condition_action_row.addWidget(add_condition_button)
        condition_action_row.addWidget(condition_tip)
        condition_action_row.addStretch(1)
        conditions_section.add_widget(self._wrap_layout(condition_action_row, conditions_section))

        ai_section = ContentSection("AI 智能回复增强", "✳", parent=panel)
        hero = QFrame(ai_section)
        _call(hero, "setObjectName", "smartReplyHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        hero_layout.setSpacing(SPACING_XL)

        hero_text_host = QWidget(hero)
        hero_text_layout = QVBoxLayout(hero_text_host)
        hero_text_layout.setContentsMargins(0, 0, 0, 0)
        hero_text_layout.setSpacing(SPACING_XS)
        hero_title = QLabel("启用 AI 智能回复补全", hero_text_host)
        _call(hero_title, "setObjectName", "sectionTitle")
        hero_caption = QLabel(
            "当规则命中但用户表述不完整时，系统将结合商品信息、最近成交文案与会话上下文生成更贴近成交场景的回复。",
            hero_text_host,
        )
        _call(hero_caption, "setObjectName", "sectionCaption")
        _call(hero_caption, "setWordWrap", True)
        hero_text_layout.addWidget(hero_title)
        hero_text_layout.addWidget(hero_caption)

        self._editor_widgets["ai_enabled"] = ToggleSwitch(True)
        _connect(getattr(self._editor_widgets["ai_enabled"], "toggled", None), self._sync_editor_preview)
        hero_layout.addWidget(hero_text_host, 1)
        hero_layout.addWidget(self._editor_widgets["ai_enabled"])
        ai_section.add_widget(hero)

        ai_row = QWidget(ai_section)
        ai_row_layout = QHBoxLayout(ai_row)
        ai_row_layout.setContentsMargins(0, 0, 0, 0)
        ai_row_layout.setSpacing(SPACING_XL)
        self._editor_widgets["ai_tone"] = ThemedComboBox("回复风格", ["专业成交型", "亲和接待型", "清晰说明型", "顾问推荐型", "限时成交型", "安抚稳态型", "礼貌等待型"])
        self._editor_widgets["risk_strategy"] = ThemedComboBox("风控策略", ["直接发送", "敏感词先审后发", "命中尺码词后再生成", "优惠信息校验后发送", "先安抚后转人工"])
        self._editor_widgets["reply_mode"] = ThemedComboBox("回复方式", ["纯模板", "模板 + AI 补充", "AI 智能回复"])
        self._editor_widgets["owner"] = ThemedLineEdit("负责小组", "如：售后客服 A 组", "便于交接排班与责任归属")
        ai_row_layout.addWidget(self._editor_widgets["ai_tone"], 1)
        ai_row_layout.addWidget(self._editor_widgets["risk_strategy"], 1)
        ai_row_layout.addWidget(self._editor_widgets["reply_mode"], 1)
        ai_row_layout.addWidget(self._editor_widgets["owner"], 1)
        ai_section.add_widget(ai_row)

        preview_panel = QFrame(panel)
        _call(preview_panel, "setObjectName", "previewPanel")
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        preview_layout.setSpacing(SPACING_SM)
        preview_title = QLabel("规则预览", preview_panel)
        _call(preview_title, "setObjectName", "sectionTitle")
        self._preview_summary = QLabel("当前规则将用于店铺私信价格咨询场景。", preview_panel)
        _call(self._preview_summary, "setObjectName", "previewText")
        _call(self._preview_summary, "setWordWrap", True)
        self._preview_template_hint = QLabel("模板摘要将在这里更新。", preview_panel)
        _call(self._preview_template_hint, "setObjectName", "summaryLabel")
        _call(self._preview_template_hint, "setWordWrap", True)
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self._preview_summary)
        preview_layout.addWidget(self._preview_template_hint)

        footer = QWidget(panel)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(SPACING_MD)
        reset_button = QPushButton("重置当前编辑", footer)
        _call(reset_button, "setObjectName", "ghostChip")
        save_button = PrimaryButton("保存规则", footer, icon_text="✓")
        _connect(getattr(reset_button, "clicked", None), self._on_reset_editor)
        _connect(getattr(save_button, "clicked", None), self._on_save_rule)
        footer_layout.addStretch(1)
        footer_layout.addWidget(reset_button)
        footer_layout.addWidget(save_button)

        layout.addWidget(header)
        layout.addWidget(summary_strip)
        layout.addWidget(basic_section)
        layout.addWidget(trigger_section)
        layout.addWidget(conditions_section)
        layout.addWidget(ai_section)
        layout.addWidget(preview_panel)
        layout.addWidget(footer)
        layout.addStretch(1)

        self._register_editor_change_listeners()
        return panel

    def _build_monitor_panel(self) -> QWidget:
        """构建右侧监控面板。"""

        panel = QFrame(self)
        _call(panel, "setObjectName", "monitorPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        header = QWidget(panel)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_XS)
        title = QLabel("实时监控与执行面板", header)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("查看规则命中情况、自动回复日志、转人工会话与规则表格总览。", header)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        header_layout.addWidget(title)
        header_layout.addWidget(caption)

        mini_row = QWidget(panel)
        mini_layout = QHBoxLayout(mini_row)
        mini_layout.setContentsMargins(0, 0, 0, 0)
        mini_layout.setSpacing(SPACING_MD)
        self._live_hit_panel = self._build_mini_panel("当前每分钟命中", "12 次", "价格问答仍是主流场景")
        self._manual_panel = self._build_mini_panel("待人工跟进", "9 单", "售后与投诉会话建议优先处理")
        self._ai_panel = self._build_mini_panel("AI 智能补全占比", "31%", "尺码与催付场景表现最佳")
        mini_layout.addWidget(self._live_hit_panel, 1)
        mini_layout.addWidget(self._manual_panel, 1)
        mini_layout.addWidget(self._ai_panel, 1)

        self._monitor_tabs = TabBar(panel)
        self._monitor_tabs.add_tab("实时日志", self._build_log_tab())
        self._monitor_tabs.add_tab("规则总览表", self._build_rule_table_tab())
        self._monitor_tabs.add_tab("最近会话", self._build_conversation_tab())

        layout.addWidget(header)
        layout.addWidget(mini_row)
        layout.addWidget(self._monitor_tabs, 1)
        return panel

    def _build_log_tab(self) -> QWidget:
        """构建日志标签页。"""

        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        status_panel = QFrame(host)
        _call(status_panel, "setObjectName", "statusPanel")
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        status_layout.setSpacing(SPACING_MD)
        self._log_status_badge = StatusBadge("日志 0 条", "brand", status_panel)
        self._log_status_hint = QLabel("最近规则命中、保存与启停操作会实时写入日志。", status_panel)
        _call(self._log_status_hint, "setObjectName", "sectionCaption")
        _call(self._log_status_hint, "setWordWrap", True)
        status_layout.addWidget(self._log_status_badge)
        status_layout.addWidget(self._log_status_hint, 1)

        self._log_viewer = RealtimeLogViewer()
        _call(self._log_viewer, "setMinimumHeight", 320)
        layout.addWidget(status_panel)
        layout.addWidget(self._log_viewer)
        return host

    def _build_rule_table_tab(self) -> QWidget:
        """构建规则总览表标签页。"""

        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        tip = QLabel("表格用于集中查看每条规则的触发词、回复方式、命中数据与 AI 启用状态。", host)
        _call(tip, "setObjectName", "sectionCaption")
        _call(tip, "setWordWrap", True)
        self._rule_table = DataTable(RULE_TABLE_HEADERS, [], page_size=6, empty_text="暂无规则数据", parent=host)
        _connect(getattr(self._rule_table, "row_selected", None), self._on_rule_table_selected)
        layout.addWidget(tip)
        layout.addWidget(self._rule_table, 1)
        return host

    def _build_conversation_tab(self) -> QWidget:
        """构建最近会话标签页。"""

        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)

        self._conversation_cards_host = QWidget(host)
        self._conversation_cards_layout = QVBoxLayout(self._conversation_cards_host)
        self._conversation_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._conversation_cards_layout.setSpacing(SPACING_MD)
        layout.addWidget(self._conversation_cards_host)
        layout.addStretch(1)
        return host

    def _build_mini_panel(self, kicker: str, value: str, caption: str) -> QWidget:
        """构建紧凑监控卡片。"""

        panel = QFrame(self)
        _call(panel, "setObjectName", "miniPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_XS)
        kicker_label = QLabel(kicker, panel)
        _call(kicker_label, "setObjectName", "panelKicker")
        value_label = QLabel(value, panel)
        _call(value_label, "setObjectName", "panelValue")
        caption_label = QLabel(caption, panel)
        _call(caption_label, "setObjectName", "summaryLabel")
        _call(caption_label, "setWordWrap", True)
        layout.addWidget(kicker_label)
        layout.addWidget(value_label)
        layout.addWidget(caption_label)
        panel._value_label = value_label  # type: ignore[attr-defined]
        panel._caption_label = caption_label  # type: ignore[attr-defined]
        return panel

    def _wrap_layout(self, layout: QHBoxLayout, parent: QWidget) -> QWidget:
        """将布局包装为 QWidget。"""

        wrapper = QWidget(parent)
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addLayout(layout)
        return wrapper

    def _register_editor_change_listeners(self) -> None:
        """注册编辑器联动。"""

        name_field = self._editor_widgets.get("name")
        scene_field = self._editor_widgets.get("scene")
        channel_field = self._editor_widgets.get("channel")
        match_mode_field = self._editor_widgets.get("match_mode")
        keyword_field = self._editor_widgets.get("keywords")
        template_field = self._editor_widgets.get("template")
        delay_field = self._editor_widgets.get("delay")
        daily_limit_field = self._editor_widgets.get("daily_limit")
        quiet_period_field = self._editor_widgets.get("quiet_period")
        condition_logic_field = self._editor_widgets.get("condition_logic")
        reply_mode_field = self._editor_widgets.get("reply_mode")
        ai_tone_field = self._editor_widgets.get("ai_tone")
        risk_strategy_field = self._editor_widgets.get("risk_strategy")
        owner_field = self._editor_widgets.get("owner")

        if isinstance(name_field, ThemedLineEdit):
            _connect(getattr(name_field.line_edit, "textChanged", None), self._sync_editor_preview)
        if isinstance(scene_field, ThemedComboBox):
            _connect(getattr(scene_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(channel_field, ThemedComboBox):
            _connect(getattr(channel_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(match_mode_field, ThemedComboBox):
            _connect(getattr(match_mode_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(keyword_field, TagInput):
            _connect(getattr(keyword_field, "tags_changed", None), self._sync_editor_preview)
        if isinstance(template_field, ThemedTextEdit):
            _connect(getattr(template_field.text_edit, "textChanged", None), self._sync_editor_preview)
        if isinstance(delay_field, ThemedLineEdit):
            _connect(getattr(delay_field.line_edit, "textChanged", None), self._sync_editor_preview)
        if isinstance(daily_limit_field, ThemedLineEdit):
            _connect(getattr(daily_limit_field.line_edit, "textChanged", None), self._sync_editor_preview)
        if isinstance(quiet_period_field, ThemedLineEdit):
            _connect(getattr(quiet_period_field.line_edit, "textChanged", None), self._sync_editor_preview)
        if isinstance(condition_logic_field, ThemedComboBox):
            _connect(getattr(condition_logic_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(reply_mode_field, ThemedComboBox):
            _connect(getattr(reply_mode_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(ai_tone_field, ThemedComboBox):
            _connect(getattr(ai_tone_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(risk_strategy_field, ThemedComboBox):
            _connect(getattr(risk_strategy_field.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        if isinstance(owner_field, ThemedLineEdit):
            _connect(getattr(owner_field.line_edit, "textChanged", None), self._sync_editor_preview)

    def _apply_filters(self, *_args: object) -> None:
        """根据搜索和筛选条件过滤规则。"""

        query = self._rule_search.text().strip().lower() if isinstance(self._rule_search, SearchBar) else ""
        scene_text = self._scene_filter.current_text() if isinstance(self._scene_filter, ThemedComboBox) else "全部场景"
        status_text = self._status_filter.current_text() if isinstance(self._status_filter, ThemedComboBox) else "全部状态"

        filtered: list[dict[str, Any]] = []
        for rule in self._rules:
            name_text = str(rule.get("name", "")).lower()
            scene_value = str(rule.get("scene", ""))
            channel_text = str(rule.get("channel", "")).lower()
            keyword_text = " ".join(str(item) for item in rule.get("keywords", [])).lower()
            if query and query not in name_text and query not in keyword_text and query not in channel_text:
                continue
            if scene_text not in ("", "全部场景") and scene_value != scene_text:
                continue
            if status_text == "仅看已开启" and not bool(rule.get("enabled", False)):
                continue
            if status_text == "仅看已关闭" and bool(rule.get("enabled", False)):
                continue
            filtered.append(rule)

        self._filtered_rules = filtered
        if self._selected_rule_id and not any(str(rule.get("id")) == self._selected_rule_id for rule in self._filtered_rules):
            self._selected_rule_id = str(self._filtered_rules[0].get("id", "")) if self._filtered_rules else ""
        self._refresh_rule_cards()
        self._refresh_rule_table()
        self._refresh_sidebar_summary()

    def _refresh_all_views(self, *_args: object) -> None:
        """刷新页面所有视图。"""

        self._apply_filters()
        self._refresh_statistics()
        self._refresh_sidebar_summary()
        self._refresh_monitor_panels()
        self._refresh_recent_conversations()
        self._load_selected_rule_to_editor()
        self._sync_editor_preview()

    def _refresh_statistics(self) -> None:
        """刷新统计卡数值。"""

        enabled_count = sum(1 for rule in self._rules if bool(rule.get("enabled", False)))
        total_hits = sum(int(str(rule.get("today_hits", "0")).replace(",", "")) for rule in self._rules)
        total_success = sum(int(str(rule.get("today_success", "0")).replace(",", "")) for rule in self._rules)
        total_manual = sum(int(str(rule.get("manual_takeover", "0")).replace(",", "")) for rule in self._rules)
        hit_ratio = (total_success / total_hits * 100.0) if total_hits else 0.0
        manual_ratio = (total_manual / total_hits * 100.0) if total_hits else 0.0

        values = [
            f"{total_hits:,}",
            "2.4 秒",
            f"{hit_ratio:.1f}%",
            f"{manual_ratio:.1f}%",
        ]
        deltas = [
            f"+{max(enabled_count * 2, 8)}.6%",
            "-0.8 秒",
            "+4.1%",
            "-2.3%",
        ]
        captions = [
            f"当前共有 {enabled_count} 条规则开启，覆盖高频咨询与售后场景。",
            "欢迎语、物流和价格问答共同拉低首响时长。",
            f"今日共成功执行 {total_success:,} 次，规则表现稳定。",
            f"需人工介入 {total_manual:,} 次，主要集中在售后与投诉场景。",
        ]
        for index, label in enumerate(self._metric_value_labels):
            _call(label, "setText", values[index])
        for index, label in enumerate(self._metric_delta_labels):
            _call(label, "setText", deltas[index])
        for index, label in enumerate(self._metric_caption_labels):
            _call(label, "setText", captions[index])

    def _refresh_sidebar_summary(self) -> None:
        """刷新横幅与侧栏摘要。"""

        enabled_count = sum(1 for rule in self._rules if bool(rule.get("enabled", False)))
        disabled_count = len(self._rules) - enabled_count
        visible_count = len(self._filtered_rules)
        _call(self._console_summary_label, "setText", f"当前规则：{enabled_count} 条开启 / {disabled_count} 条关闭")
        if self._page_enabled:
            self._system_status_badge.setText("系统运行中")
            self._system_status_badge.set_tone("success")
        else:
            self._system_status_badge.setText("系统已暂停")
            self._system_status_badge.set_tone("warning")
        self._coverage_badge.setText(f"筛选后展示 {visible_count} 条规则")

    def _refresh_monitor_panels(self) -> None:
        """刷新右侧顶部监控卡。"""

        live_hits = sum(int(str(rule.get("today_hits", "0")).replace(",", "")) for rule in self._rules if bool(rule.get("enabled", False)))
        ai_hits = sum(int(str(rule.get("today_hits", "0")).replace(",", "")) for rule in self._rules if bool(rule.get("ai_enabled", False)))
        manual_hits = sum(int(str(rule.get("manual_takeover", "0")).replace(",", "")) for rule in self._rules)
        self._set_mini_panel_content(self._live_hit_panel, "当前每分钟命中", f"{max(live_hits // 120, 1)} 次", "高频场景主要由欢迎语、价格与物流答复构成")
        self._set_mini_panel_content(self._manual_panel, "待人工跟进", f"{manual_hits} 单", "售后安抚、人工客服转接规则仍需人工承接")
        ai_ratio = (ai_hits / live_hits * 100.0) if live_hits else 0.0
        self._set_mini_panel_content(self._ai_panel, "AI 智能补全占比", f"{ai_ratio:.0f}%", "尺码推荐与催付跟进是 AI 主要发力场景")

    def _set_mini_panel_content(self, panel: QWidget, kicker: str, value: str, caption: str) -> None:
        """更新紧凑监控卡片文案。"""

        value_label = getattr(panel, "_value_label", None)
        caption_label = getattr(panel, "_caption_label", None)
        layout = getattr(panel, "layout", None)
        if callable(layout):
            existing_layout = layout()
            item_at = getattr(existing_layout, "itemAt", None)
            if callable(item_at):
                first_item = item_at(0)
                widget_method = getattr(first_item, "widget", None) if first_item is not None else None
                first_widget = widget_method() if callable(widget_method) else None
                if first_widget is not None:
                    _call(first_widget, "setText", kicker)
        if value_label is not None:
            _call(value_label, "setText", value)
        if caption_label is not None:
            _call(caption_label, "setText", caption)

    def _refresh_rule_cards(self) -> None:
        """刷新左侧规则卡片。"""

        _clear_layout(self._rule_cards_layout)
        self._rule_card_widgets.clear()

        if not self._filtered_rules:
            empty = QLabel("没有匹配到规则，请尝试调整筛选条件。", self._rule_cards_host)
            _call(empty, "setObjectName", "sectionCaption")
            self._rule_cards_layout.addWidget(empty)
            self._rule_cards_layout.addStretch(1)
            return

        for rule in self._filtered_rules:
            card = self._build_rule_card(rule)
            self._rule_cards_layout.addWidget(card)
        self._rule_cards_layout.addStretch(1)

    def _build_rule_card(self, rule: dict[str, Any]) -> QWidget:
        """构建单条规则卡片。"""

        colors = _palette()
        is_selected = str(rule.get("id", "")) == self._selected_rule_id
        card = QFrame(self._rule_cards_host)
        _call(card, "setObjectName", "ruleCard")
        border_color = colors.primary if is_selected else colors.border
        background = _rgba(colors.primary, 0.06) if is_selected else colors.surface
        _call(
            card,
            "setStyleSheet",
            f"QFrame#ruleCard {{ background-color: {background}; border: 1px solid {border_color}; border-radius: {RADIUS_LG}px; }}",
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_SM)

        row_top = QHBoxLayout()
        row_top.setContentsMargins(0, 0, 0, 0)
        row_top.setSpacing(SPACING_MD)
        name_button = QPushButton(str(rule.get("name", "")), card)
        _call(
            name_button,
            "setStyleSheet",
            f"background: transparent; border: none; text-align: left; color: {colors.text}; font-size: {_static_token('font.size.md')}; font-weight: {_static_token('font.weight.bold')};",
        )
        state_badge = StatusBadge(_toggle_text(bool(rule.get("enabled", False))), _badge_tone_from_enabled(bool(rule.get("enabled", False))), card)
        row_top.addWidget(name_button, 1)
        row_top.addWidget(state_badge)

        scene_label = QLabel(f"场景：{rule.get('scene', '')} · 渠道：{rule.get('channel', '')}", card)
        _call(scene_label, "setObjectName", "summaryLabel")
        keyword_label = QLabel(f"触发词：{' / '.join(str(item) for item in rule.get('keywords', [])[:4])}", card)
        _call(keyword_label, "setObjectName", "summaryValue")
        template_preview = str(rule.get("template", "")).strip().replace("\n", " ")
        preview_label = QLabel(template_preview[:72] + ("…" if len(template_preview) > 72 else ""), card)
        _call(preview_label, "setObjectName", "summaryLabel")
        _call(preview_label, "setWordWrap", True)

        stats_row = QHBoxLayout()
        stats_row.setContentsMargins(0, 0, 0, 0)
        stats_row.setSpacing(SPACING_MD)
        for text in (
            f"今日触发 {rule.get('today_hits', '0')}",
            f"成功率 {rule.get('success_rate', '--')}",
            f"AI {_smart_reply_text(bool(rule.get('ai_enabled', False)))}",
        ):
            chip = QLabel(text, card)
            _call(chip, "setObjectName", "mutedTiny")
            _call(
                chip,
                "setStyleSheet",
                f"background-color: {_rgba(colors.primary, 0.08)}; color: {colors.text_muted}; border: 1px solid {colors.border}; border-radius: {RADIUS_MD}px; padding: {SPACING_XS}px {SPACING_MD}px;",
            )
            stats_row.addWidget(chip)
        stats_row.addStretch(1)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(SPACING_MD)
        select_button = QPushButton("查看并编辑", card)
        _call(select_button, "setObjectName", "ghostChip")
        toggle = ToggleSwitch(bool(rule.get("enabled", False)))
        toggle_label = QLabel("启停", card)
        _call(toggle_label, "setObjectName", "summaryLabel")
        bottom_row.addWidget(select_button)
        bottom_row.addStretch(1)
        bottom_row.addWidget(toggle_label)
        bottom_row.addWidget(toggle)

        _connect(getattr(name_button, "clicked", None), lambda rid=str(rule.get("id", "")): self._select_rule(rid))
        _connect(getattr(select_button, "clicked", None), lambda rid=str(rule.get("id", "")): self._select_rule(rid))
        _connect(getattr(toggle, "toggled", None), lambda checked, rid=str(rule.get("id", "")): self._set_rule_enabled(rid, checked))

        layout.addLayout(row_top)
        layout.addWidget(scene_label)
        layout.addWidget(keyword_label)
        layout.addWidget(preview_label)
        layout.addLayout(stats_row)
        layout.addLayout(bottom_row)

        self._rule_card_widgets.append({"id": str(rule.get("id", "")), "toggle": toggle, "card": card, "badge": state_badge})
        return card

    def _refresh_rule_table(self) -> None:
        """刷新规则总览表。"""

        rows = [_rule_table_row(rule) for rule in self._filtered_rules]
        self._rule_table.set_rows(rows)
        if self._filtered_rules:
            selected_index = 0
            for index, rule in enumerate(self._filtered_rules):
                if str(rule.get("id", "")) == self._selected_rule_id:
                    selected_index = index
                    break
            self._rule_table.select_absolute_row(selected_index)

    def _refresh_recent_conversations(self) -> None:
        """刷新最近会话列表。"""

        _clear_layout(self._conversation_cards_layout)
        for item in RECENT_CONVERSATIONS:
            card = QFrame(self._conversation_cards_host)
            _call(card, "setObjectName", "conversationCard")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
            layout.setSpacing(SPACING_SM)

            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            top_row.setSpacing(SPACING_MD)
            customer = QLabel(item["customer"], card)
            _call(customer, "setObjectName", "sectionTitle")
            badge = StatusBadge(item["status"], "brand", card)
            top_row.addWidget(customer, 1)
            top_row.addWidget(badge)

            scene = QLabel(f"场景：{item['scene']} · 命中规则：{item['rule']}", card)
            _call(scene, "setObjectName", "summaryLabel")
            summary = QLabel(item["summary"], card)
            _call(summary, "setObjectName", "conversationText")
            _call(summary, "setWordWrap", True)

            layout.addLayout(top_row)
            layout.addWidget(scene)
            layout.addWidget(summary)
            self._conversation_cards_layout.addWidget(card)
        self._conversation_cards_layout.addStretch(1)

    def _populate_log_viewer(self) -> None:
        """填充演示日志。"""

        self._log_viewer.clear_logs()
        for item in AUTO_REPLY_LOGS:
            self._log_viewer.append_log(item["level"], item["message"], item["time"])
        if hasattr(self, "_log_status_badge"):
            latest_level = AUTO_REPLY_LOGS[0]["level"] if AUTO_REPLY_LOGS else "无"
            self._log_status_badge.setText(f"日志 {len(AUTO_REPLY_LOGS)} 条 · 最新 {latest_level}")

    def _selected_rule(self) -> dict[str, Any] | None:
        """返回当前选中规则。"""

        for rule in self._rules:
            if str(rule.get("id", "")) == self._selected_rule_id:
                return rule
        return self._rules[0] if self._rules else None

    def _select_rule(self, rule_id: str) -> None:
        """切换当前选中规则。"""

        self._selected_rule_id = rule_id
        self._refresh_rule_cards()
        self._refresh_rule_table()
        self._load_selected_rule_to_editor()
        selected_rule = self._selected_rule()
        selected_name = str(selected_rule.get("name", "")) if selected_rule is not None else ""
        self._append_operation_log(f"已切换到规则【{selected_name}】进行查看。")

    def _load_selected_rule_to_editor(self) -> None:
        """将选中规则加载到编辑区。"""

        rule = self._selected_rule()
        if rule is None:
            return

        name_field = self._editor_widgets.get("name")
        scene_field = self._editor_widgets.get("scene")
        channel_field = self._editor_widgets.get("channel")
        match_mode_field = self._editor_widgets.get("match_mode")
        keyword_field = self._editor_widgets.get("keywords")
        template_field = self._editor_widgets.get("template")
        logic_field = self._editor_widgets.get("condition_logic")
        delay_field = self._editor_widgets.get("delay")
        daily_limit_field = self._editor_widgets.get("daily_limit")
        quiet_period_field = self._editor_widgets.get("quiet_period")
        ai_enabled_field = self._editor_widgets.get("ai_enabled")
        ai_tone_field = self._editor_widgets.get("ai_tone")
        risk_strategy_field = self._editor_widgets.get("risk_strategy")
        reply_mode_field = self._editor_widgets.get("reply_mode")
        owner_field = self._editor_widgets.get("owner")

        if isinstance(name_field, ThemedLineEdit):
            name_field.setText(str(rule.get("name", "")))
        if isinstance(scene_field, ThemedComboBox):
            _call(scene_field.combo_box, "setCurrentText", str(rule.get("scene", "")))
        if isinstance(channel_field, ThemedComboBox):
            _call(channel_field.combo_box, "setCurrentText", str(rule.get("channel", "")))
        if isinstance(match_mode_field, ThemedComboBox):
            _call(match_mode_field.combo_box, "setCurrentText", str(rule.get("match_mode", "")))
        if isinstance(keyword_field, TagInput):
            keyword_field.set_tags([str(item) for item in rule.get("keywords", [])])
        if isinstance(template_field, ThemedTextEdit):
            template_field.setPlainText(str(rule.get("template", "")))
        if isinstance(logic_field, ThemedComboBox):
            _call(logic_field.combo_box, "setCurrentText", str(rule.get("condition_logic", "全部满足")))
        if isinstance(delay_field, ThemedLineEdit):
            delay_field.setText(str(rule.get("delay", "")))
        if isinstance(daily_limit_field, ThemedLineEdit):
            daily_limit_field.setText(str(rule.get("daily_limit", "")))
        if isinstance(quiet_period_field, ThemedLineEdit):
            quiet_period_field.setText(str(rule.get("quiet_period", "")))
        if isinstance(ai_enabled_field, ToggleSwitch):
            ai_enabled_field.setChecked(bool(rule.get("ai_enabled", False)))
        if isinstance(ai_tone_field, ThemedComboBox):
            _call(ai_tone_field.combo_box, "setCurrentText", str(rule.get("ai_tone", "")))
        if isinstance(risk_strategy_field, ThemedComboBox):
            _call(risk_strategy_field.combo_box, "setCurrentText", str(rule.get("risk_strategy", "")))
        if isinstance(reply_mode_field, ThemedComboBox):
            _call(reply_mode_field.combo_box, "setCurrentText", str(rule.get("reply_mode", "")))
        if isinstance(owner_field, ThemedLineEdit):
            owner_field.setText(str(rule.get("owner", "")))

        self._rebuild_conditions(rule)
        self._selected_rule_badge.setText(f"当前规则：{rule.get('name', '')}")
        self._selected_rule_badge.set_tone("brand" if bool(rule.get("enabled", False)) else "neutral")
        for key in ("priority", "today_hits", "manual_takeover", "last_trigger"):
            value_label = self._summary_labels.get(key)
            if value_label is not None:
                _call(value_label, "setText", str(rule.get(key, "--")))
        self._sync_editor_preview()

    def _rebuild_conditions(self, rule: dict[str, Any]) -> None:
        """根据规则重建条件编辑区。"""

        _clear_layout(self._conditions_layout)
        self._condition_editors.clear()
        conditions = rule.get("conditions", [])
        if not isinstance(conditions, list):
            conditions = []
        for condition in conditions:
            if isinstance(condition, dict):
                self._add_condition_editor_row(condition)
        if not self._condition_editors:
            self._add_condition_editor_row({"field": "消息内容", "operator": "包含", "value": "示例条件"})

    def _append_empty_condition(self) -> None:
        """添加空白条件。"""

        self._add_condition_editor_row({"field": "消息内容", "operator": "包含", "value": ""})
        self._sync_editor_preview()

    def _add_condition_editor_row(self, condition: dict[str, Any]) -> None:
        """添加条件编辑行。"""

        row_card = QFrame(self._conditions_host)
        _call(row_card, "setObjectName", "conditionCard")
        row_layout = QHBoxLayout(row_card)
        row_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        row_layout.setSpacing(SPACING_MD)

        field_box = ThemedComboBox("条件字段", ["咨询来源", "客户标签", "近 10 分钟重复问价次数", "是否首次会话", "历史 30 天咨询次数", "订单状态", "商品类型", "情绪分值", "消息内容", "近 5 分钟未解决轮次", "商品类目", "用户消息长度", "尺码表是否完整", "距优惠结束时间", "当前时间", "人工在线状态", "已启用值班机器人", "售后工单状态"])
        operator_box = ThemedComboBox("比较方式", ["等于", "不等于", "包含", "不包含", "属于", "大于", "小于"])
        value_edit = ThemedLineEdit("条件值", "请输入条件值", "例如：短视频 / 商品卡、3 次、23:00-08:00")
        remove_button = QPushButton("移除此条件", row_card)
        _call(remove_button, "setObjectName", "ghostChip")

        _call(field_box.combo_box, "setCurrentText", str(condition.get("field", "消息内容")))
        _call(operator_box.combo_box, "setCurrentText", str(condition.get("operator", "包含")))
        value_edit.setText(str(condition.get("value", "")))

        _connect(getattr(field_box.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        _connect(getattr(operator_box.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        _connect(getattr(value_edit.line_edit, "textChanged", None), self._sync_editor_preview)
        _connect(getattr(remove_button, "clicked", None), lambda: self._remove_condition_editor_row(row_card))

        row_layout.addWidget(field_box, 1)
        row_layout.addWidget(operator_box, 1)
        row_layout.addWidget(value_edit, 2)
        row_layout.addWidget(remove_button)
        self._conditions_layout.addWidget(row_card)
        self._condition_editors.append(
            {
                "card": row_card,
                "field": field_box,
                "operator": operator_box,
                "value": value_edit,
            }
        )

    def _remove_condition_editor_row(self, row_card: QWidget) -> None:
        """移除条件编辑行。"""

        if len(self._condition_editors) <= 1:
            self._append_operation_log("至少保留一条命中条件，已忽略移除操作。")
            return
        self._condition_editors = [item for item in self._condition_editors if item.get("card") is not row_card]
        _call(row_card, "setParent", None)
        _call(row_card, "deleteLater")
        self._sync_editor_preview()

    def _collect_conditions(self) -> list[dict[str, str]]:
        """收集当前条件数据。"""

        collected: list[dict[str, str]] = []
        for item in self._condition_editors:
            field_widget = item.get("field")
            operator_widget = item.get("operator")
            value_widget = item.get("value")
            field_text = field_widget.current_text() if isinstance(field_widget, ThemedComboBox) else ""
            operator_text = operator_widget.current_text() if isinstance(operator_widget, ThemedComboBox) else ""
            value_text = value_widget.text() if isinstance(value_widget, ThemedLineEdit) else ""
            collected.append({"field": field_text, "operator": operator_text, "value": value_text})
        return collected

    def _collect_editor_state(self) -> dict[str, Any]:
        """收集编辑器当前状态。"""

        rule = self._selected_rule()
        current_id = str(rule.get("id", "")) if rule is not None else ""
        return {
            "id": current_id,
            "name": self._read_line_edit("name"),
            "scene": self._read_combo_box("scene"),
            "channel": self._read_combo_box("channel"),
            "match_mode": self._read_combo_box("match_mode"),
            "reply_mode": self._read_combo_box("reply_mode"),
            "priority": str(rule.get("priority", "中优先级")) if rule is not None else "中优先级",
            "enabled": bool(rule.get("enabled", False)) if rule is not None else True,
            "ai_enabled": self._read_toggle("ai_enabled"),
            "ai_tone": self._read_combo_box("ai_tone"),
            "risk_strategy": self._read_combo_box("risk_strategy"),
            "delay": self._read_line_edit("delay"),
            "daily_limit": self._read_line_edit("daily_limit"),
            "quiet_period": self._read_line_edit("quiet_period"),
            "success_rate": str(rule.get("success_rate", "--")) if rule is not None else "--",
            "today_hits": str(rule.get("today_hits", "0")) if rule is not None else "0",
            "today_success": str(rule.get("today_success", "0")) if rule is not None else "0",
            "manual_takeover": str(rule.get("manual_takeover", "0")) if rule is not None else "0",
            "conversion": str(rule.get("conversion", "--")) if rule is not None else "--",
            "last_trigger": str(rule.get("last_trigger", "刚刚")) if rule is not None else "刚刚",
            "owner": self._read_line_edit("owner"),
            "keywords": self._read_tags("keywords"),
            "template": self._read_text_edit("template"),
            "condition_logic": self._read_combo_box("condition_logic"),
            "conditions": self._collect_conditions(),
            "notes": list(rule.get("notes", [])) if rule is not None else [],
            "examples": list(rule.get("examples", [])) if rule is not None else [],
        }

    def _read_line_edit(self, key: str) -> str:
        widget = self._editor_widgets.get(key)
        return widget.text() if isinstance(widget, ThemedLineEdit) else ""

    def _read_combo_box(self, key: str) -> str:
        widget = self._editor_widgets.get(key)
        return widget.current_text() if isinstance(widget, ThemedComboBox) else ""

    def _read_toggle(self, key: str) -> bool:
        widget = self._editor_widgets.get(key)
        return bool(widget.isChecked()) if isinstance(widget, ToggleSwitch) else False

    def _read_tags(self, key: str) -> list[str]:
        widget = self._editor_widgets.get(key)
        return widget.tags() if isinstance(widget, TagInput) else []

    def _read_text_edit(self, key: str) -> str:
        widget = self._editor_widgets.get(key)
        return widget.toPlainText() if isinstance(widget, ThemedTextEdit) else ""

    def _sync_editor_preview(self, *_args: object) -> None:
        """同步规则预览文案。"""

        state = self._collect_editor_state()
        keywords = state.get("keywords", [])
        keyword_preview = "、".join(str(item) for item in keywords[:4]) if isinstance(keywords, list) else ""
        conditions = state.get("conditions", [])
        condition_count = len(conditions) if isinstance(conditions, list) else 0
        template_text = str(state.get("template", "")).strip().replace("\n", " ")
        template_short = template_text[:120] + ("…" if len(template_text) > 120 else "")

        summary = (
            f"规则【{state.get('name', '') or '未命名规则'}】将在【{state.get('scene', '') or '未选择场景'}】场景下，"
            f"通过【{state.get('match_mode', '') or '未设置匹配方式'}】匹配关键词 {keyword_preview or '（暂无）'}，"
            f"命中后以【{state.get('reply_mode', '') or '未设置回复方式'}】发送。"
        )
        follow_up = (
            f"当前共配置 {condition_count} 条条件，延迟 {state.get('delay', '') or '未填'} 秒，"
            f"单日上限 {state.get('daily_limit', '') or '未填'}，静默时段 {state.get('quiet_period', '') or '无'}；"
            f"AI 智能回复 {_smart_reply_text(bool(state.get('ai_enabled', False)))}。"
        )
        _call(self._preview_summary, "setText", summary)
        _call(self._preview_template_hint, "setText", f"模板摘要：{template_short or '请填写自动回复模板内容。'}\n{follow_up}")

    def _on_console_toggled(self, checked: bool) -> None:
        """切换页面总开关。"""

        self._page_enabled = checked
        if checked:
            self._append_operation_log("自动回复总开关已开启，系统恢复规则自动响应。")
        else:
            self._append_operation_log("自动回复总开关已关闭，所有规则停止自动发送，仅保留日志监控。")
        self._refresh_sidebar_summary()

    def _set_rule_enabled(self, rule_id: str, enabled: bool) -> None:
        """更新规则启停状态。"""

        for rule in self._rules:
            if str(rule.get("id", "")) != rule_id:
                continue
            rule["enabled"] = enabled
            self._append_operation_log(f"规则【{rule.get('name', '')}】已{('开启' if enabled else '关闭')}。")
            break
        self._refresh_all_views()

    def _on_save_rule(self) -> None:
        """保存当前编辑规则。"""

        state = self._collect_editor_state()
        for index, rule in enumerate(self._rules):
            if str(rule.get("id", "")) == str(state.get("id", "")):
                merged = _copy_rule(rule)
                merged.update(state)
                self._rules[index] = merged
                self._selected_rule_id = str(merged.get("id", ""))
                break
        self._append_operation_log(f"规则【{state.get('name', '') or '未命名规则'}】已保存，最新模板与条件已生效。")
        self._refresh_all_views()

    def _on_reset_editor(self) -> None:
        """重置编辑区为当前规则原始值。"""

        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已恢复规则【{rule.get('name', '')}】的原始配置。")

    def _on_clone_rule(self) -> None:
        """复制当前规则。"""

        rule = self._selected_rule()
        if rule is None:
            return
        cloned = _copy_rule(rule)
        cloned["id"] = f"{rule.get('id', 'rule')}-copy-{len(self._rules) + 1}"
        cloned["name"] = f"{rule.get('name', '')}（副本）"
        cloned["today_hits"] = "0"
        cloned["today_success"] = "0"
        cloned["manual_takeover"] = "0"
        cloned["last_trigger"] = "尚未触发"
        self._rules.insert(0, cloned)
        self._selected_rule_id = str(cloned.get("id", ""))
        self._append_operation_log(f"已复制规则【{rule.get('name', '')}】，新规则名称为【{cloned.get('name', '')}】。")
        self._refresh_all_views()

    def _on_create_rule(self) -> None:
        """新增演示规则。"""

        new_rule = {
            "id": f"rule-new-{len(self._rules) + 1}",
            "name": "新建自动回复规则",
            "scene": "售前咨询",
            "channel": "店铺私信",
            "match_mode": "包含任意关键词",
            "reply_mode": "纯模板",
            "priority": "中优先级",
            "enabled": True,
            "ai_enabled": False,
            "ai_tone": "亲和接待型",
            "risk_strategy": "直接发送",
            "delay": "2.0",
            "daily_limit": "100",
            "quiet_period": "无",
            "success_rate": "--",
            "today_hits": "0",
            "today_success": "0",
            "manual_takeover": "0",
            "conversion": "--",
            "last_trigger": "尚未触发",
            "owner": "待分配",
            "keywords": ["示例关键词"],
            "template": "您好，这是一条新建的自动回复规则，请根据业务场景继续完善回复内容。",
            "condition_logic": "全部满足",
            "conditions": [{"field": "消息内容", "operator": "包含", "value": "示例关键词"}],
            "notes": ["建议补充至少三条真实触发词与一条风控条件。"],
            "examples": ["客户发送示例关键词后触发。"],
        }
        self._rules.insert(0, new_rule)
        self._selected_rule_id = str(new_rule["id"])
        self._append_operation_log("已创建新的自动回复规则草稿，请完善关键词、模板与条件后保存。")
        self._refresh_all_views()

    def _on_rule_table_selected(self, row_index: int) -> None:
        """表格选中后同步规则。"""

        if not (0 <= row_index < len(self._filtered_rules)):
            return
        self._select_rule(str(self._filtered_rules[row_index].get("id", "")))

    def _append_batch_hint_log(self) -> None:
        """记录批量操作提示。"""

        self._append_operation_log("可继续扩展批量启停、导出规则、按小组复制等高级操作。")

    def _append_operation_log(self, message: str) -> None:
        """向日志面板追加一条操作日志。"""

        self._log_viewer.append_log("操作", message, "2026-03-09 14:30:00")

    def _insert_order_variable(self) -> None:
        """向模板插入订单变量。"""

        widget = self._editor_widgets.get("template")
        if not isinstance(widget, ThemedTextEdit):
            return
        text = widget.toPlainText().rstrip()
        addition = "\n\n可引用变量：{{订单号}}、{{商品名称}}、{{下单时间}}"
        widget.setPlainText(text + addition)
        self._append_operation_log("已向回复模板插入订单相关变量。")

    def _insert_campaign_variable(self) -> None:
        """向模板插入活动倒计时变量。"""

        widget = self._editor_widgets.get("template")
        if not isinstance(widget, ThemedTextEdit):
            return
        text = widget.toPlainText().rstrip()
        addition = "\n\n活动提醒：当前优惠预计在 {{活动结束时间}} 结束，请留意下单时机。"
        widget.setPlainText(text + addition)
        self._append_operation_log("已向回复模板插入活动倒计时变量。")

    def _insert_handoff_hint(self) -> None:
        """向模板插入人工转接说明。"""

        widget = self._editor_widgets.get("template")
        if not isinstance(widget, ThemedTextEdit):
            return
        text = widget.toPlainText().rstrip()
        addition = "\n\n如需进一步处理，请直接回复【人工】，我会优先为您转接客服同事。"
        widget.setPlainText(text + addition)
        self._append_operation_log("已向回复模板插入人工转接提示。")

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""自动私信原型页面。"""

from typing import Any

from ....core.qt import QFrame as CoreQFrame, QHBoxLayout as CoreQHBoxLayout, QLabel as CoreQLabel, QPushButton as CoreQPushButton, QVBoxLayout as CoreQVBoxLayout, QWidget as CoreQWidget
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    IconButton,
    KPICard,
    PageContainer,
    PrimaryButton,
    RuleEditorWidget,
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
    "目标人群",
    "消息序列",
    "每日上限",
    "送达率",
    "回复率",
    "转化率",
    "状态",
]

SEQUENCE_TABLE_HEADERS = ["步骤", "发送时机", "消息摘要", "变量", "自动回复链"]
CONVERSATION_TABLE_HEADERS = ["时间", "对象", "阶段", "状态", "最近消息", "下一动作", "结果"]

STATISTICS_CARDS: list[dict[str, Any]] = [
    {"title": "今日私信量", "value": "624", "trend": "up", "percentage": "+12.9%", "caption": "新关注用户与活跃评论用户带来私信增量", "sparkline": [42, 55, 67, 74, 86, 95, 108]},
    {"title": "送达率", "value": "94.1%", "trend": "up", "percentage": "+1.9%", "caption": "发送节奏与人群过滤让送达更稳定", "sparkline": [88, 89, 90, 91, 92, 93, 94]},
    {"title": "回复率", "value": "18.7%", "trend": "up", "percentage": "+2.4%", "caption": "问答式首条消息显著提升互动概率", "sparkline": [10, 11, 12, 14, 15, 17, 19]},
    {"title": "转化率", "value": "6.8%", "trend": "up", "percentage": "+0.9%", "caption": "多步消息流在第二步转化表现更佳", "sparkline": [3.5, 4.0, 4.8, 5.2, 5.9, 6.2, 6.8]},
]

AUTO_DM_LOGS: list[dict[str, str]] = [
    {"level": "成功", "time": "2026-03-09 15:31:18", "message": "序列【新关注欢迎链】已对 22 位新关注用户发送首条欢迎私信，送达率 100%。"},
    {"level": "预警", "time": "2026-03-09 15:27:42", "message": "账号 @dm_wave_03 在 30 分钟内已发送 18 条私信，系统自动切换到低速模式。"},
    {"level": "成功", "time": "2026-03-09 15:23:07", "message": "序列【高意向评论用户转化】已完成第 2 步跟进，3 位用户点击了商品链接。"},
    {"level": "忽略", "time": "2026-03-09 15:18:56", "message": "对象 @blocked_dm_user 位于私信黑名单中，系统已跳过发送。"},
    {"level": "成功", "time": "2026-03-09 15:14:33", "message": "自动回复链已对 5 条用户回复进行分类，2 条进入人工接手队列。"},
    {"level": "预警", "time": "2026-03-09 15:09:21", "message": "当前私信频率接近平台日限额 72%，建议暂停低意向人群扩量。"},
    {"level": "成功", "time": "2026-03-09 15:04:15", "message": "变量模板 {name}、{product}、{offer} 已被成功替换并发送。"},
    {"level": "忽略", "time": "2026-03-09 14:58:10", "message": "用户 @cold_comment_17 已在近 7 天收到过同序列消息，系统避免重复触达。"},
    {"level": "成功", "time": "2026-03-09 14:51:28", "message": "序列【清单用户定向触达】首轮发送完成，已有 4 人回复关键字【想了解】。"},
    {"level": "预警", "time": "2026-03-09 14:45:03", "message": "检测到一组消息模板包含促销词密度偏高，建议弱化直接成交表述。"},
    {"level": "成功", "time": "2026-03-09 14:37:56", "message": "回复监控识别到 8 条积极回复，已自动接入第 2 步跟进消息。"},
    {"level": "成功", "time": "2026-03-09 14:29:19", "message": "消息序列在活跃评论用户场景中表现稳定，回复率提升到 21%。"},
]

SEQUENCE_STEPS: list[dict[str, str]] = [
    {"step": "第 1 步", "timing": "关注后 5 分钟", "summary": "欢迎语 + 轻问题切入", "variables": "{name} {product}", "chain": "命中积极回复后进入第 2 步"},
    {"step": "第 2 步", "timing": "首条后 8 小时", "summary": "补充使用场景与真实反馈", "variables": "{scene} {benefit}", "chain": "无回复则 48 小时后结束"},
    {"step": "第 3 步", "timing": "点击链接后 6 小时", "summary": "发送轻提醒与答疑入口", "variables": "{offer} {deadline}", "chain": "回复关键字则转人工"},
    {"step": "第 4 步", "timing": "加购后 4 小时", "summary": "发送温和催单信息", "variables": "{product} {offer}", "chain": "未回复则停止触达"},
    {"step": "第 5 步", "timing": "成交后次日", "summary": "发送感谢与使用建议", "variables": "{name} {product}", "chain": "进入老客养护链"},
    {"step": "第 6 步", "timing": "评论后 20 分钟", "summary": "根据评论内容发送个性化问候", "variables": "{comment_topic}", "chain": "命中兴趣标签则推送第 2 步"},
    {"step": "第 7 步", "timing": "活跃互动后 1 天", "summary": "补充产品细节与购买建议", "variables": "{product} {feature}", "chain": "无意向则降级到内容订阅链"},
    {"step": "第 8 步", "timing": "清单导入后 2 小时", "summary": "定向名单欢迎语", "variables": "{name} {segment}", "chain": "人工审核后继续"},
    {"step": "第 9 步", "timing": "停留页面后 3 小时", "summary": "提醒查看收藏内容", "variables": "{product} {scene}", "chain": "点击后进入第 3 步"},
    {"step": "第 10 步", "timing": "连续回复后立即", "summary": "自动答疑链首句", "variables": "{question}", "chain": "复杂问题转人工"},
]

CONVERSATIONS: list[dict[str, str]] = [
    {"time": "15:30", "target": "@newfollow_28", "phase": "第 1 步已送达", "status": "已送达", "message": "欢迎关注，想先了解哪种通勤场景？", "next": "等待用户回复", "result": "送达成功"},
    {"time": "15:22", "target": "@hotcomment_12", "phase": "第 2 步跟进", "status": "已回复", "message": "这个杯子日常通勤和露营都挺适合，你更偏哪种使用场景？", "next": "准备发送产品细节", "result": "高意向"},
    {"time": "15:15", "target": "@wishlist_03", "phase": "第 3 步提醒", "status": "点击链接", "message": "看到你刚刚浏览了随行杯，想了解容量还是材质？", "next": "补充 FAQ", "result": "进入转化链"},
    {"time": "15:07", "target": "@dm_list_08", "phase": "名单触达", "status": "已送达", "message": "你好，这边帮你准备了一份适合办公场景的轻量好物清单。", "next": "24 小时后轻提醒", "result": "等待反馈"},
    {"time": "14:59", "target": "@commentback_06", "phase": "自动回复链", "status": "需人工", "message": "你更关心保温时长还是杯盖防漏？", "next": "转人工答疑", "result": "复杂问题"},
    {"time": "14:53", "target": "@activefan_17", "phase": "第 2 步跟进", "status": "已送达", "message": "你上次提到想找颜值高又适合通勤的杯子，这款会更合适。", "next": "8 小时后再提醒", "result": "中意向"},
    {"time": "14:47", "target": "@dm_wave_test", "phase": "第 1 步已送达", "status": "无回复", "message": "欢迎关注，平时更偏好办公室还是出行场景的杯子？", "next": "48 小时后结束", "result": "观察中"},
    {"time": "14:39", "target": "@cartsave_11", "phase": "加购提醒", "status": "已回复", "message": "看到你刚加入购物车了，想了解材质还是容量细节？", "next": "补充规格对比", "result": "转化中"},
    {"time": "14:33", "target": "@segment_a_02", "phase": "名单触达", "status": "已送达", "message": "你好，这边准备了一份适合露营场景的轻装好物建议。", "next": "等待关键字回复", "result": "送达成功"},
    {"time": "14:26", "target": "@freshreply_05", "phase": "自动回复链", "status": "已回复", "message": "你更在意清洗方便还是保温时长？", "next": "发送对比说明", "result": "积极互动"},
    {"time": "14:20", "target": "@newfollow_17", "phase": "第 1 步已送达", "status": "已送达", "message": "欢迎来到这里，最近在找通勤杯还是露营杯？", "next": "等待回复", "result": "送达成功"},
    {"time": "14:12", "target": "@repeat_skip_09", "phase": "去重拦截", "status": "已跳过", "message": "近 7 天内已命中同序列，未再次发送。", "next": "停止触达", "result": "避免重复"},
]

DEMO_RULES: list[dict[str, Any]] = [
    {"id": "dm-rule-01", "name": "新关注欢迎链", "audience": "新关注用户", "sequence": "3 步欢迎链", "daily_limit": "160", "delivery_rate": "98.7%", "reply_rate": "22.3%", "conversion_rate": "7.4%", "enabled": True, "last_run": "15:30", "account_group": "品牌主号 A 组", "followers": ["近 24 小时新关注"], "commenters": ["高互动评论用户"], "specific_lists": ["欢迎链优先名单"], "message_template": "你好 {name}，欢迎来到这里～如果你最近在看 {product}，我可以先按你的使用场景给你一个更快的建议。", "sequence_steps": ["第 1 步欢迎", "第 2 步场景跟进", "第 3 步轻提醒"], "auto_reply_chain": "积极回复 → 推荐链；复杂问题 → 人工", "compliance": "每账号每小时不超过 12 条", "notes": ["欢迎链首句避免直接成交。", "优先用问题开启对话。"], "conditions": [{"field": "关注时间", "operator": "小于", "value": "24 小时"}, {"field": "是否已私信", "operator": "等于", "value": "否"}], "action": {"type": "执行任务", "value": "发送欢迎私信"}},
    {"id": "dm-rule-02", "name": "高意向评论用户转化", "audience": "活跃评论用户", "sequence": "4 步转化链", "daily_limit": "120", "delivery_rate": "95.2%", "reply_rate": "26.1%", "conversion_rate": "9.3%", "enabled": True, "last_run": "15:23", "account_group": "品牌主号 B 组", "followers": ["近 7 天新关注"], "commenters": ["评论含想了解", "评论含多少钱"], "specific_lists": ["高意向评论名单"], "message_template": "看到你刚刚对 {product} 留了评论，如果你愿意，我可以直接把几个最常被问到的细节发给你。", "sequence_steps": ["第 1 步答疑邀约", "第 2 步产品细节", "第 3 步场景对比", "第 4 步温和提醒"], "auto_reply_chain": "回复价格 → FAQ；回复材质 → 规格说明；复杂问题 → 人工", "compliance": "每日总量不超过 120 条", "notes": ["高意向评论用户更适合答疑型开场。"], "conditions": [{"field": "评论关键词", "operator": "包含", "value": "想了解 / 多少钱"}], "action": {"type": "执行任务", "value": "发送答疑式私信"}},
    {"id": "dm-rule-03", "name": "清单用户定向触达", "audience": "指定名单", "sequence": "2 步名单链", "daily_limit": "80", "delivery_rate": "96.8%", "reply_rate": "17.4%", "conversion_rate": "5.9%", "enabled": True, "last_run": "14:51", "account_group": "达人合作号", "followers": ["无"], "commenters": ["无"], "specific_lists": ["展会名单", "老客推荐名单"], "message_template": "你好 {name}，这边整理了一份更适合 {segment} 人群的轻量选择建议，如果你需要，我可以继续展开。", "sequence_steps": ["第 1 步名单欢迎", "第 2 步建议展开"], "auto_reply_chain": "命中想看 → 继续第 2 步", "compliance": "名单类私信需人工审核来源", "notes": ["导入名单要先做来源校验。"], "conditions": [{"field": "名单来源", "operator": "等于", "value": "已审核"}], "action": {"type": "执行任务", "value": "名单欢迎触达"}},
    {"id": "dm-rule-04", "name": "活跃评论用户问答链", "audience": "活跃评论用户", "sequence": "3 步问答链", "daily_limit": "110", "delivery_rate": "93.4%", "reply_rate": "24.8%", "conversion_rate": "6.2%", "enabled": True, "last_run": "14:37", "account_group": "品牌主号 A 组", "followers": ["近 3 天新关注"], "commenters": ["活跃评论用户"], "specific_lists": ["问答链实验名单"], "message_template": "你刚刚评论提到 {question}，这个问题很多人都会关心，我可以先把最核心的两点发给你。", "sequence_steps": ["第 1 步问题确认", "第 2 步核心回答", "第 3 步推荐延伸"], "auto_reply_chain": "回复使用场景 → 场景建议；回复价格 → FAQ", "compliance": "保持问答型比例高于直接销售型", "notes": ["自动回复链要优先分类问题。"], "conditions": [{"field": "评论情绪", "operator": "等于", "value": "积极 / 中性"}], "action": {"type": "执行任务", "value": "发起问答式私信"}},
    {"id": "dm-rule-05", "name": "新关注低频养护链", "audience": "新关注用户", "sequence": "5 步养护链", "daily_limit": "90", "delivery_rate": "91.9%", "reply_rate": "12.8%", "conversion_rate": "4.1%", "enabled": False, "last_run": "14:20", "account_group": "家居矩阵号", "followers": ["近 48 小时新关注"], "commenters": ["无"], "specific_lists": ["家居养护名单"], "message_template": "你好 {name}，如果你最近在看 {product} 相关内容，我可以先发一份比较适合入门的整理思路给你。", "sequence_steps": ["欢迎", "场景建议", "细节补充", "轻提醒", "结束语"], "auto_reply_chain": "回复有兴趣 → 继续；无回复 → 结束", "compliance": "低频场景仅在白天时段执行", "notes": ["当前暂停，等待养护文案更新。"], "conditions": [{"field": "当前时间", "operator": "属于", "value": "09:00-20:00"}], "action": {"type": "暂停任务", "value": "等待新文案"}},
    {"id": "dm-rule-06", "name": "加购用户提醒链", "audience": "指定名单", "sequence": "3 步提醒链", "daily_limit": "70", "delivery_rate": "95.9%", "reply_rate": "19.6%", "conversion_rate": "8.1%", "enabled": True, "last_run": "14:39", "account_group": "品牌主号 B 组", "followers": ["无"], "commenters": ["无"], "specific_lists": ["加购名单"], "message_template": "看到你刚刚把 {product} 放进了购物车，如果你在纠结容量或材质，我可以直接发一个简版对比给你。", "sequence_steps": ["加购提醒", "规格对比", "温和提醒"], "auto_reply_chain": "回复容量 / 材质 → 对应 FAQ", "compliance": "同一用户 72 小时内不重复提醒", "notes": ["提醒语气要尽量克制。"], "conditions": [{"field": "加购时间", "operator": "小于", "value": "12 小时"}], "action": {"type": "执行任务", "value": "发送加购提醒"}},
    {"id": "dm-rule-07", "name": "露营人群定向链", "audience": "指定名单", "sequence": "4 步场景链", "daily_limit": "60", "delivery_rate": "94.3%", "reply_rate": "16.8%", "conversion_rate": "5.7%", "enabled": True, "last_run": "14:33", "account_group": "达人合作号", "followers": ["无"], "commenters": ["露营关键词评论用户"], "specific_lists": ["露营偏好名单"], "message_template": "如果你最近在看露营相关内容，这个 {product} 在轻量出行场景里的反馈会更适合你。", "sequence_steps": ["场景欢迎", "细节展开", "对比建议", "结束语"], "auto_reply_chain": "回复露营 / 通勤 → 切换对应场景说明", "compliance": "每轮不超过 20 条", "notes": ["细分场景链更适合合作名单。"], "conditions": [{"field": "名单标签", "operator": "包含", "value": "露营"}], "action": {"type": "执行任务", "value": "发送露营场景私信"}},
    {"id": "dm-rule-08", "name": "自动答疑接力链", "audience": "活跃评论用户", "sequence": "实时回复链", "daily_limit": "140", "delivery_rate": "92.6%", "reply_rate": "31.2%", "conversion_rate": "6.9%", "enabled": True, "last_run": "15:14", "account_group": "品牌主号 A 组", "followers": ["近 3 天新关注"], "commenters": ["连续回复用户"], "specific_lists": ["答疑优先名单"], "message_template": "你刚提到 {question}，这个点很多人也会关心，我先把最核心的结论发你。", "sequence_steps": ["问题识别", "快速回答", "延伸建议"], "auto_reply_chain": "复杂问题自动转人工", "compliance": "疑似售后问题禁止继续自动发送", "notes": ["答疑链要严格避开售后敏感问题。"], "conditions": [{"field": "问题类型", "operator": "不等于", "value": "售后投诉"}], "action": {"type": "执行任务", "value": "自动答疑"}},
    {"id": "dm-rule-09", "name": "老客复购提醒链", "audience": "指定名单", "sequence": "2 步复购链", "daily_limit": "50", "delivery_rate": "96.1%", "reply_rate": "15.4%", "conversion_rate": "7.2%", "enabled": False, "last_run": "13:58", "account_group": "品牌主号 B 组", "followers": ["无"], "commenters": ["无"], "specific_lists": ["老客复购名单"], "message_template": "你好 {name}，上次你买的 {product} 如果用得顺手，这次有一个更适合搭配的选择可以给你参考。", "sequence_steps": ["复购问候", "搭配推荐"], "auto_reply_chain": "回复想看 → 继续推荐", "compliance": "复购链需控制在每周 1 次内", "notes": ["当前待机，等活动档期再开启。"], "conditions": [{"field": "上次下单时间", "operator": "大于", "value": "30 天"}], "action": {"type": "暂停任务", "value": "等待活动期"}},
    {"id": "dm-rule-10", "name": "内容浏览停留跟进", "audience": "活跃评论用户", "sequence": "3 步浏览链", "daily_limit": "75", "delivery_rate": "90.8%", "reply_rate": "14.2%", "conversion_rate": "5.1%", "enabled": True, "last_run": "14:59", "account_group": "品牌主号 A 组", "followers": ["近 24 小时新关注"], "commenters": ["内容停留高用户"], "specific_lists": ["浏览链名单"], "message_template": "看到你刚刚停留了 {product} 相关内容，如果你想，我可以把大家最关心的两点直接发给你。", "sequence_steps": ["浏览提醒", "FAQ", "结束语"], "auto_reply_chain": "点击链接 → 第 3 步；无回复 → 结束", "compliance": "停留人群触达频率不宜过高", "notes": ["浏览链适合做轻提醒，不适合强转化。"], "conditions": [{"field": "停留时长", "operator": "大于", "value": "20 秒"}], "action": {"type": "执行任务", "value": "发送浏览跟进"}},
]


def _rgba(hex_color: str, alpha: float) -> str:
    cleaned = hex_color.strip().lstrip("#")
    if len(cleaned) != 6:
        return hex_color
    red = int(cleaned[0:2], 16)
    green = int(cleaned[2:4], 16)
    blue = int(cleaned[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _clear_layout(layout: object) -> None:
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
    return "已开启" if enabled else "已关闭"


def _badge_tone_from_enabled(enabled: bool) -> BadgeTone:
    return "success" if enabled else "neutral"


def _rule_table_row(rule: dict[str, Any]) -> list[object]:
    return [
        str(rule.get("name", "")),
        str(rule.get("audience", "")),
        str(rule.get("sequence", "")),
        str(rule.get("daily_limit", "")),
        str(rule.get("delivery_rate", "--")),
        str(rule.get("reply_rate", "--")),
        str(rule.get("conversion_rate", "--")),
        _toggle_text(bool(rule.get("enabled", False))),
    ]


def _sequence_table_row(item: dict[str, str]) -> list[object]:
    return [item["step"], item["timing"], item["summary"], item["variables"], item["chain"]]


def _conversation_table_row(item: dict[str, str]) -> list[object]:
    return [item["time"], item["target"], item["phase"], item["status"], item["message"], item["next"], item["result"]]


class AutoDirectMessagePage(BasePage):
    """自动私信页面。"""

    default_route_id = RouteId("auto_direct_message")
    default_display_name = "自动私信"
    default_icon_name = "mail"

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
        self._sequence_steps: list[dict[str, str]] = [item.copy() for item in SEQUENCE_STEPS]
        self._conversations: list[dict[str, str]] = [item.copy() for item in CONVERSATIONS]
        self._filtered_conversations: list[dict[str, str]] = list(self._conversations)
        self._selected_rule_id: str = str(self._rules[0]["id"]) if self._rules else ""
        self._kpi_cards: list[KPICard] = []
        self._editor_widgets: dict[str, object] = {}
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        root = QWidget(self)
        _call(root, "setObjectName", "autoDmRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.layout.addWidget(root)

        self._refresh_button = IconButton("↻", "刷新自动私信状态", self)
        self._new_rule_button = PrimaryButton("新增私信规则", self, icon_text="＋")
        container = PageContainer(
            title="自动私信",
            description="围绕目标人群、消息变量、多步序列和合规阈值搭建一套可执行的自动私信原型。",
            actions=[self._refresh_button, self._new_rule_button],
            parent=root,
        )
        container.content_layout.setSpacing(SPACING_2XL)
        root_layout.addWidget(container)

        container.add_widget(self._build_banner())
        container.add_widget(self._build_kpi_row())
        container.add_widget(self._build_workspace())

        self._bind_interactions()
        self._refresh_all_views()

    def _apply_page_styles(self) -> None:
        colors = _palette()
        brand_tint = _rgba(colors.primary, 0.08)
        brand_border = _rgba(colors.primary, 0.20)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget {{
                color: {colors.text};
                font-family: {_static_token('font.family.chinese')};
            }}
            QWidget#autoDmRoot {{
                background-color: {_token('surface.primary')};
            }}
            QFrame#banner,
            QFrame#sidebarPanel,
            QFrame#editorPanel,
            QFrame#monitorPanel,
            QFrame#miniPanel,
            QFrame#ruleCard,
            QFrame#previewPanel,
            QFrame#summaryStrip,
            QFrame#noteCard {{
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
            QLabel#sectionCaption,
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
            QLabel#bodyText {{
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
                background-color: {brand_tint};
                color: {colors.primary};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_MD}px;
                min-height: {BUTTON_HEIGHT - SPACING_SM}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#ghostChip:hover {{
                background-color: {_rgba(colors.primary, 0.14)};
            }}
            QLabel#statusPanelValue {{
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.text};
                background: transparent;
            }}
            """,
        )

    def _build_banner(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "banner")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        left = QWidget(panel)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(SPACING_XS)
        title = QLabel("启用自动私信序列引擎", left)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("系统将根据新关注、活跃评论和指定清单自动触发多步私信流，并实时检查合规阈值。", left)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        badges = QHBoxLayout()
        badges.setContentsMargins(0, 0, 0, 0)
        badges.setSpacing(SPACING_MD)
        self._system_badge = StatusBadge("私信运行中", "success", left)
        self._sequence_badge = StatusBadge("序列链已激活", "brand", left)
        self._compliance_badge = StatusBadge("合规限制开启", "warning", left)
        badges.addWidget(self._system_badge)
        badges.addWidget(self._sequence_badge)
        badges.addWidget(self._compliance_badge)
        badges.addStretch(1)
        left_layout.addWidget(title)
        left_layout.addWidget(caption)
        left_layout.addLayout(badges)

        right = QWidget(panel)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING_SM)
        switch_row = QHBoxLayout()
        switch_row.setContentsMargins(0, 0, 0, 0)
        switch_row.setSpacing(SPACING_MD)
        switch_row.addStretch(1)
        switch_row.addWidget(QLabel("总开关", right))
        self._console_toggle = ToggleSwitch(True)
        switch_row.addWidget(self._console_toggle)
        self._console_summary_label = QLabel("当前启用 8 条私信规则，2 条待机", right)
        _call(self._console_summary_label, "setObjectName", "summaryValue")
        tip = QLabel("私信频率接近限制时，应优先保留高意向人群序列并暂停低转化链。", right)
        _call(tip, "setObjectName", "summaryLabel")
        _call(tip, "setWordWrap", True)
        right_layout.addLayout(switch_row)
        right_layout.addWidget(self._console_summary_label)
        right_layout.addWidget(tip)

        layout.addWidget(left, 1)
        layout.addWidget(right)
        return panel

    def _build_kpi_row(self) -> QWidget:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        self._kpi_cards.clear()
        for item in STATISTICS_CARDS:
            card = KPICard(
                title=str(item["title"]),
                value=str(item["value"]),
                trend=item["trend"],
                percentage=str(item["percentage"]),
                caption=str(item["caption"]),
                sparkline_data=item["sparkline"],
                parent=row,
            )
            layout.addWidget(card, 1)
            self._kpi_cards.append(card)
        return row

    def _build_workspace(self) -> QWidget:
        outer_split = SplitPanel(orientation="horizontal", split_ratio=(0.30, 0.70), minimum_sizes=(320, 760), parent=self)
        right_split = SplitPanel(orientation="horizontal", split_ratio=(0.58, 0.42), minimum_sizes=(520, 360), parent=outer_split)
        outer_split.set_widgets(self._build_sidebar_panel(), right_split)
        right_split.set_widgets(self._build_editor_panel(), self._build_monitor_panel())
        return outer_split

    def _build_sidebar_panel(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "sidebarPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)
        header = QWidget(panel)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_SM)
        title = QLabel("私信规则列表", header)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("按目标人群、状态和搜索关键字筛选私信规则，快速切换要编辑的消息链。", header)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        header_layout.addWidget(title)
        header_layout.addWidget(caption)

        filter_panel = QFrame(panel)
        _call(filter_panel, "setObjectName", "statusPanel")
        filter_layout = QVBoxLayout(filter_panel)
        filter_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        filter_layout.setSpacing(SPACING_SM)
        filter_title = QLabel("规则筛选", filter_panel)
        _call(filter_title, "setObjectName", "sectionTitle")
        filter_hint = QLabel("先按人群、状态和账号池筛选，再去中间区域调整模板变量与序列链。", filter_panel)
        _call(filter_hint, "setObjectName", "sectionCaption")
        _call(filter_hint, "setWordWrap", True)
        filter_layout.addWidget(filter_title)
        filter_layout.addWidget(filter_hint)
        self._rule_search = SearchBar("搜索规则、目标人群、变量或序列")
        self._audience_filter = ThemedComboBox("目标人群", ["全部人群", "新关注用户", "活跃评论用户", "指定名单"])
        self._status_filter = ThemedComboBox("状态筛选", ["全部状态", "仅看已开启", "仅看已关闭"])
        self._account_filter = ThemedComboBox("账号池", ["全部账号池", "品牌主号 A 组", "品牌主号 B 组", "家居矩阵号", "达人合作号"])
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(SPACING_MD)
        self._clone_button = PrimaryButton("复制规则", panel, icon_text="⎘")
        self._tips_button = IconButton("⋯", "私信批量操作提示", panel)
        actions.addWidget(self._clone_button, 1)
        actions.addWidget(self._tips_button)
        self._rule_cards_host = QWidget(panel)
        self._rule_cards_layout = QVBoxLayout(self._rule_cards_host)
        self._rule_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._rule_cards_layout.setSpacing(SPACING_MD)
        self._sidebar_summary = self._build_mini_panel("当前重点", "欢迎链 + 问答链", "新关注欢迎和高意向评论转化仍是私信主力。")
        filter_layout.addWidget(self._rule_search)
        filter_layout.addWidget(self._audience_filter)
        filter_layout.addWidget(self._status_filter)
        filter_layout.addWidget(self._account_filter)
        layout.addWidget(header)
        layout.addWidget(filter_panel)
        layout.addLayout(actions)
        layout.addWidget(self._rule_cards_host, 1)
        layout.addWidget(self._sidebar_summary)
        return panel

    def _build_editor_panel(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "editorPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        header = QWidget(panel)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)
        text_host = QWidget(header)
        text_layout = QVBoxLayout(text_host)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(SPACING_XS)
        title = QLabel("私信配置", text_host)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("设置目标人群、模板变量、序列步骤、自动回复链与合规阈值。", text_host)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        text_layout.addWidget(title)
        text_layout.addWidget(caption)
        self._selected_rule_badge = StatusBadge("当前规则：新关注欢迎链", "brand", header)
        header_layout.addWidget(text_host, 1)
        header_layout.addWidget(self._selected_rule_badge)

        summary = QFrame(panel)
        _call(summary, "setObjectName", "summaryStrip")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        summary_layout.setSpacing(SPACING_XL)
        self._summary_labels: dict[str, QLabel] = {}
        for label_text, key in (("送达率", "delivery_rate"), ("回复率", "reply_rate"), ("转化率", "conversion_rate"), ("最近执行", "last_run")):
            block = QWidget(summary)
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

        basic = ContentSection("目标人群规则", "◎", parent=panel)
        row1 = QWidget(basic)
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(SPACING_XL)
        self._editor_widgets["name"] = ThemedLineEdit("规则名称", "请输入私信规则名称", "建议按人群 + 场景命名")
        self._editor_widgets["audience"] = ThemedComboBox("目标人群", ["新关注用户", "活跃评论用户", "指定名单"])
        self._editor_widgets["account_group"] = ThemedComboBox("账号池", ["品牌主号 A 组", "品牌主号 B 组", "家居矩阵号", "达人合作号"])
        self._editor_widgets["daily_limit"] = ThemedLineEdit("每日上限", "如：160", "超过上限后自动停止发送")
        row1_layout.addWidget(self._editor_widgets["name"], 2)
        row1_layout.addWidget(self._editor_widgets["audience"], 1)
        row1_layout.addWidget(self._editor_widgets["account_group"], 1)
        row1_layout.addWidget(self._editor_widgets["daily_limit"], 1)
        basic.add_widget(row1)
        self._editor_widgets["followers"] = TagInput("新关注人群规则", "输入关注条件标签")
        self._editor_widgets["commenters"] = TagInput("活跃评论人群规则", "输入评论用户规则")
        self._editor_widgets["specific_lists"] = TagInput("指定清单", "输入名单名称或分组")
        basic.add_widget(self._editor_widgets["followers"])
        basic.add_widget(self._editor_widgets["commenters"])
        basic.add_widget(self._editor_widgets["specific_lists"])

        template = ContentSection("消息模板与变量", "✦", parent=panel)
        self._editor_widgets["message_template"] = ThemedTextEdit("首条消息模板", "支持变量：{name} {product} {scene} {offer} 等")
        template.add_widget(self._editor_widgets["message_template"])
        variable_row = QHBoxLayout()
        variable_row.setContentsMargins(0, 0, 0, 0)
        variable_row.setSpacing(SPACING_MD)
        for text, handler in (("插入 {name}", self._insert_name_variable), ("插入 {product}", self._insert_product_variable), ("插入 {offer}", self._insert_offer_variable)):
            button = QPushButton(text, template)
            _call(button, "setObjectName", "ghostChip")
            _connect(getattr(button, "clicked", None), handler)
            variable_row.addWidget(button)
        variable_row.addStretch(1)
        wrapper = QWidget(template)
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addLayout(variable_row)
        template.add_widget(wrapper)

        sequence = ContentSection("序列与自动回复链", "◴", parent=panel)
        row2 = QWidget(sequence)
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(SPACING_XL)
        self._editor_widgets["sequence"] = ThemedLineEdit("消息序列名称", "如：3 步欢迎链", "建议明确步骤数和目标")
        self._editor_widgets["auto_reply_chain"] = ThemedLineEdit("自动回复链", "如：积极回复 → 第 2 步；复杂问题 → 人工", "用于定义响应分流")
        self._editor_widgets["compliance"] = ThemedLineEdit("合规提醒", "如：每账号每小时不超过 12 条", "明确平台限制与内部阈值")
        row2_layout.addWidget(self._editor_widgets["sequence"], 1)
        row2_layout.addWidget(self._editor_widgets["auto_reply_chain"], 1)
        row2_layout.addWidget(self._editor_widgets["compliance"], 1)
        sequence.add_widget(row2)
        self._rule_editor = RuleEditorWidget(panel)
        sequence.add_widget(self._rule_editor)

        preview = QFrame(panel)
        _call(preview, "setObjectName", "previewPanel")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        preview_layout.setSpacing(SPACING_SM)
        preview_title = QLabel("私信预览", preview)
        _call(preview_title, "setObjectName", "sectionTitle")
        self._preview_summary = QLabel("当前规则将为新关注用户发送欢迎式私信。", preview)
        _call(self._preview_summary, "setObjectName", "bodyText")
        _call(self._preview_summary, "setWordWrap", True)
        self._preview_hint = QLabel("变量、序列步骤和自动回复链会同步显示在这里。", preview)
        _call(self._preview_hint, "setObjectName", "summaryLabel")
        _call(self._preview_hint, "setWordWrap", True)
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self._preview_summary)
        preview_layout.addWidget(self._preview_hint)

        footer = QWidget(panel)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(SPACING_MD)
        self._reset_button = QPushButton("恢复当前规则", footer)
        _call(self._reset_button, "setObjectName", "ghostChip")
        self._run_button = PrimaryButton("立即发送一轮", footer, icon_text="▶")
        self._save_button = PrimaryButton("保存规则", footer, icon_text="✓")
        footer_layout.addStretch(1)
        footer_layout.addWidget(self._reset_button)
        footer_layout.addWidget(self._run_button)
        footer_layout.addWidget(self._save_button)

        layout.addWidget(header)
        layout.addWidget(summary)
        layout.addWidget(basic)
        layout.addWidget(template)
        layout.addWidget(sequence)
        layout.addWidget(preview)
        layout.addWidget(footer)
        layout.addStretch(1)
        return panel

    def _build_monitor_panel(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "monitorPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)
        title = QLabel("私信监控", panel)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("同时查看消息序列、会话跟踪、实时日志与合规提醒，确保自动私信不过量也不失真。", panel)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        mini_row = QWidget(panel)
        mini_layout = QHBoxLayout(mini_row)
        mini_layout.setContentsMargins(0, 0, 0, 0)
        mini_layout.setSpacing(SPACING_MD)
        self._delivery_panel = self._build_mini_panel("送达监控", "稳定", "大多数消息链在安全阈值内发送")
        self._reply_panel = self._build_mini_panel("回复进度", "11 条待跟进", "自动回复链已处理首轮反馈")
        self._limit_panel = self._build_mini_panel("合规压力", "72%", "接近日限额，建议控制低意向链")
        mini_layout.addWidget(self._delivery_panel, 1)
        mini_layout.addWidget(self._reply_panel, 1)
        mini_layout.addWidget(self._limit_panel, 1)
        self._monitor_tabs = TabBar(panel)
        self._monitor_tabs.add_tab("序列表", self._build_sequence_tab())
        self._monitor_tabs.add_tab("会话跟踪", self._build_conversation_tab())
        self._monitor_tabs.add_tab("实时日志", self._build_log_tab())
        self._monitor_tabs.add_tab("合规提醒", self._build_alert_tab())
        layout.addWidget(title)
        layout.addWidget(caption)
        layout.addWidget(mini_row)
        layout.addWidget(self._monitor_tabs, 1)
        return panel

    def _build_sequence_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        self._sequence_table = DataTable(SEQUENCE_TABLE_HEADERS, [], page_size=5, empty_text="暂无序列步骤", parent=host)
        self._sequence_status_badge = StatusBadge("序列步骤就绪", "brand", host)
        layout.addWidget(self._sequence_status_badge)
        layout.addWidget(self._sequence_table, 1)
        return host

    def _build_conversation_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        self._conversation_table = DataTable(CONVERSATION_TABLE_HEADERS, [], page_size=6, empty_text="暂无会话跟踪", parent=host)
        self._conversation_status_badge = StatusBadge("会话跟踪就绪", "brand", host)
        layout.addWidget(self._conversation_status_badge)
        layout.addWidget(self._conversation_table, 1)
        return host

    def _build_log_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        status_panel = QFrame(host)
        _call(status_panel, "setObjectName", "statusPanel")
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        status_layout.setSpacing(SPACING_MD)
        self._log_status_badge = StatusBadge("日志 0 条", "brand", host)
        self._log_status_value = QLabel("最新状态 --", status_panel)
        _call(self._log_status_value, "setObjectName", "statusPanelValue")
        self._log_status_hint = QLabel("送达、回复分流与合规拦截都会即时写入私信日志。", status_panel)
        _call(self._log_status_hint, "setObjectName", "sectionCaption")
        _call(self._log_status_hint, "setWordWrap", True)
        status_layout.addWidget(self._log_status_badge)
        status_layout.addWidget(self._log_status_value)
        status_layout.addWidget(self._log_status_hint, 1)
        self._log_viewer = RealtimeLogViewer(host)
        layout.addWidget(status_panel)
        layout.addWidget(self._log_viewer)
        return host

    def _build_alert_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_MD)
        self._alert_cards_host = QWidget(host)
        self._alert_cards_layout = QVBoxLayout(self._alert_cards_host)
        self._alert_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._alert_cards_layout.setSpacing(SPACING_MD)
        layout.addWidget(self._alert_cards_host)
        layout.addStretch(1)
        return host

    def _build_mini_panel(self, kicker: str, value: str, caption: str) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "miniPanel")
        box = QVBoxLayout(panel)
        box.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        box.setSpacing(SPACING_XS)
        kicker_label = QLabel(kicker, panel)
        _call(kicker_label, "setObjectName", "panelKicker")
        value_label = QLabel(value, panel)
        _call(value_label, "setObjectName", "panelValue")
        caption_label = QLabel(caption, panel)
        _call(caption_label, "setObjectName", "summaryLabel")
        _call(caption_label, "setWordWrap", True)
        box.addWidget(kicker_label)
        box.addWidget(value_label)
        box.addWidget(caption_label)
        panel._kicker_label = kicker_label  # type: ignore[attr-defined]
        panel._value_label = value_label  # type: ignore[attr-defined]
        panel._caption_label = caption_label  # type: ignore[attr-defined]
        return panel

    def _bind_interactions(self) -> None:
        _connect(getattr(self._refresh_button, "clicked", None), self._refresh_all_views)
        _connect(getattr(self._new_rule_button, "clicked", None), self._on_create_rule)
        _connect(getattr(self._clone_button, "clicked", None), self._on_clone_rule)
        _connect(getattr(self._tips_button, "clicked", None), self._append_batch_hint_log)
        _connect(getattr(self._console_toggle, "toggled", None), self._on_console_toggled)
        _connect(getattr(self._rule_search, "search_changed", None), self._apply_filters)
        _connect(getattr(self._audience_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._status_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._account_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._conversation_table, "row_selected", None), self._on_conversation_selected)
        _connect(getattr(self._sequence_table, "row_selected", None), self._on_sequence_selected)
        _connect(getattr(self._rule_editor, "rule_changed", None), self._sync_editor_preview)
        _connect(getattr(self._reset_button, "clicked", None), self._on_reset_editor)
        _connect(getattr(self._run_button, "clicked", None), self._on_run_rule)
        _connect(getattr(self._save_button, "clicked", None), self._on_save_rule)
        for key in ("name", "daily_limit", "sequence", "auto_reply_chain", "compliance"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedLineEdit):
                _connect(getattr(widget.line_edit, "textChanged", None), self._sync_editor_preview)
        for key in ("audience", "account_group"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedComboBox):
                _connect(getattr(widget.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        for key in ("followers", "commenters", "specific_lists"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, TagInput):
                _connect(getattr(widget, "tags_changed", None), self._sync_editor_preview)
        message_widget = self._editor_widgets.get("message_template")
        if isinstance(message_widget, ThemedTextEdit):
            _connect(getattr(message_widget.text_edit, "textChanged", None), self._sync_editor_preview)

    def _refresh_all_views(self, *_args: object) -> None:
        self._apply_filters()
        self._populate_log_viewer()
        self._refresh_kpis()
        self._refresh_sidebar_summary()
        self._refresh_monitor_panels()
        self._refresh_sequence_table()
        self._refresh_conversation_table()
        self._refresh_alert_cards()
        self._load_selected_rule_to_editor()
        self._sync_editor_preview()

    def _apply_filters(self, *_args: object) -> None:
        query = self._rule_search.text().strip().lower()
        audience = self._audience_filter.current_text() if isinstance(self._audience_filter, ThemedComboBox) else "全部人群"
        status = self._status_filter.current_text() if isinstance(self._status_filter, ThemedComboBox) else "全部状态"
        account = self._account_filter.current_text() if isinstance(self._account_filter, ThemedComboBox) else "全部账号池"
        filtered: list[dict[str, Any]] = []
        for rule in self._rules:
            haystack = " ".join(
                [
                    str(rule.get("name", "")),
                    str(rule.get("audience", "")),
                    str(rule.get("sequence", "")),
                    str(rule.get("account_group", "")),
                    " ".join(str(item) for item in rule.get("followers", [])),
                    " ".join(str(item) for item in rule.get("commenters", [])),
                    " ".join(str(item) for item in rule.get("specific_lists", [])),
                ]
            ).lower()
            if query and query not in haystack:
                continue
            if audience not in ("", "全部人群") and str(rule.get("audience", "")) != audience:
                continue
            if account not in ("", "全部账号池") and str(rule.get("account_group", "")) != account:
                continue
            if status == "仅看已开启" and not bool(rule.get("enabled", False)):
                continue
            if status == "仅看已关闭" and bool(rule.get("enabled", False)):
                continue
            filtered.append(rule)
        self._filtered_rules = filtered
        if self._selected_rule_id and not any(str(rule.get("id", "")) == self._selected_rule_id for rule in self._filtered_rules):
            self._selected_rule_id = str(self._filtered_rules[0].get("id", "")) if self._filtered_rules else ""
        self._refresh_rule_cards()
        self._refresh_rule_table()

    def _refresh_kpis(self) -> None:
        total_limit = sum(int(str(rule.get("daily_limit", "0")).replace(",", "")) for rule in self._rules)
        enabled_count = sum(1 for rule in self._rules if bool(rule.get("enabled", False)))
        values = ["624", self._average_metric("delivery_rate"), self._average_metric("reply_rate"), self._average_metric("conversion_rate")]
        captions = [
            f"规则总上限 {total_limit} 条，当前主要触达高意向与新关注人群。",
            f"当前启用 {enabled_count} 条序列链，送达稳定。",
            "多步消息流显著提高了私信回复概率。",
            "第二步跟进和加购提醒链贡献了主要转化。",
        ]
        for index, card in enumerate(self._kpi_cards):
            card.set_value(values[index])
            _call(card._caption_label, "setText", captions[index])  # type: ignore[attr-defined]

    def _average_metric(self, key: str) -> str:
        values: list[float] = []
        for rule in self._rules:
            raw = str(rule.get(key, "0")).replace("%", "")
            try:
                values.append(float(raw))
            except ValueError:
                continue
        average = sum(values) / len(values) if values else 0.0
        return f"{average:.1f}%"

    def _refresh_sidebar_summary(self) -> None:
        enabled_count = sum(1 for rule in self._rules if bool(rule.get("enabled", False)))
        disabled_count = len(self._rules) - enabled_count
        _call(self._console_summary_label, "setText", f"当前启用 {enabled_count} 条私信规则，{disabled_count} 条待机")
        if self._page_enabled:
            self._system_badge.setText("私信运行中")
            self._system_badge.set_tone("success")
        else:
            self._system_badge.setText("私信已暂停")
            self._system_badge.set_tone("warning")
        self._set_mini_panel_content(self._sidebar_summary, "当前重点", "欢迎链 + 问答链", f"当前筛选后展示 {len(self._filtered_rules)} 条规则。")

    def _refresh_monitor_panels(self) -> None:
        delivered = sum(1 for item in self._conversations if item.get("status") in ("已送达", "已回复", "点击链接"))
        need_follow = sum(1 for item in self._conversations if item.get("next") not in ("停止触达", "等待回复"))
        self._set_mini_panel_content(self._delivery_panel, "送达监控", f"{delivered} 条正常", "绝大多数会话都已送达或进入反馈阶段")
        self._set_mini_panel_content(self._reply_panel, "回复进度", f"{need_follow} 条待跟进", "自动回复链和人工接手队列都在消化回复")
        self._set_mini_panel_content(self._limit_panel, "合规压力", "72%", "离日限额不远，建议减少低意向名单触达")

    def _set_mini_panel_content(self, panel: QWidget, kicker: str, value: str, caption: str) -> None:
        _call(getattr(panel, "_kicker_label", None), "setText", kicker)
        _call(getattr(panel, "_value_label", None), "setText", value)
        _call(getattr(panel, "_caption_label", None), "setText", caption)

    def _refresh_rule_cards(self) -> None:
        _clear_layout(self._rule_cards_layout)
        if not self._filtered_rules:
            empty = QLabel("没有匹配到私信规则，请尝试调整筛选条件。", self._rule_cards_host)
            _call(empty, "setObjectName", "sectionCaption")
            self._rule_cards_layout.addWidget(empty)
            self._rule_cards_layout.addStretch(1)
            return
        for rule in self._filtered_rules:
            self._rule_cards_layout.addWidget(self._build_rule_card(rule))
        self._rule_cards_layout.addStretch(1)

    def _build_rule_card(self, rule: dict[str, Any]) -> QWidget:
        colors = _palette()
        card = QFrame(self._rule_cards_host)
        _call(card, "setObjectName", "ruleCard")
        selected = str(rule.get("id", "")) == self._selected_rule_id
        _call(card, "setStyleSheet", f"QFrame#ruleCard {{ background-color: {_rgba(colors.primary, 0.06) if selected else colors.surface}; border: 1px solid {colors.primary if selected else colors.border}; border-radius: {RADIUS_LG}px; }}")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_SM)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(SPACING_MD)
        name_button = QPushButton(str(rule.get("name", "")), card)
        _call(name_button, "setStyleSheet", f"background: transparent; border: none; text-align: left; color: {colors.text}; font-size: {_static_token('font.size.md')}; font-weight: {_static_token('font.weight.bold')};")
        badge = StatusBadge(_toggle_text(bool(rule.get("enabled", False))), _badge_tone_from_enabled(bool(rule.get("enabled", False))), card)
        top.addWidget(name_button, 1)
        top.addWidget(badge)
        line1 = QLabel(f"人群：{rule.get('audience', '')} · 账号池：{rule.get('account_group', '')}", card)
        _call(line1, "setObjectName", "summaryLabel")
        line2 = QLabel(f"序列：{rule.get('sequence', '')} · 合规：{rule.get('compliance', '')}", card)
        _call(line2, "setObjectName", "summaryValue")
        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(SPACING_MD)
        for text in (f"送达 {rule.get('delivery_rate', '--')}", f"回复 {rule.get('reply_rate', '--')}", f"转化 {rule.get('conversion_rate', '--')}"):
            chip = QLabel(text, card)
            _call(chip, "setObjectName", "mutedTiny")
            _call(chip, "setStyleSheet", f"background-color: {_rgba(colors.primary, 0.08)}; border: 1px solid {colors.border}; border-radius: {RADIUS_MD}px; padding: {SPACING_XS}px {SPACING_MD}px;")
            chips.addWidget(chip)
        chips.addStretch(1)
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(SPACING_MD)
        select_button = QPushButton("查看并编辑", card)
        _call(select_button, "setObjectName", "ghostChip")
        toggle = ToggleSwitch(bool(rule.get("enabled", False)))
        bottom.addWidget(select_button)
        bottom.addStretch(1)
        bottom.addWidget(QLabel("启停", card))
        bottom.addWidget(toggle)
        _connect(getattr(name_button, "clicked", None), lambda rid=str(rule.get("id", "")): self._select_rule(rid))
        _connect(getattr(select_button, "clicked", None), lambda rid=str(rule.get("id", "")): self._select_rule(rid))
        _connect(getattr(toggle, "toggled", None), lambda checked, rid=str(rule.get("id", "")): self._set_rule_enabled(rid, checked))
        layout.addLayout(top)
        layout.addWidget(line1)
        layout.addWidget(line2)
        layout.addLayout(chips)
        layout.addLayout(bottom)
        return card

    def _refresh_rule_table(self) -> None:
        if not hasattr(self, "_rule_table"):
            self._rule_table = DataTable(RULE_TABLE_HEADERS, [], page_size=5, empty_text="暂无规则数据", parent=self)
        self._rule_table.set_rows([_rule_table_row(rule) for rule in self._filtered_rules])

    def _refresh_sequence_table(self) -> None:
        self._sequence_table.set_rows([_sequence_table_row(item) for item in self._sequence_steps])
        self._sequence_table.select_absolute_row(0)
        self._sequence_status_badge.setText(f"序列步骤：{self._sequence_steps[0]['summary']}")

    def _refresh_conversation_table(self) -> None:
        current_rule = self._selected_rule()
        filtered = []
        audience = str(current_rule.get("audience", "")) if current_rule is not None else ""
        for item in self._conversations:
            if audience == "新关注用户" and item.get("phase") not in ("第 1 步已送达", "第 2 步跟进"):
                continue
            filtered.append(item)
        self._filtered_conversations = filtered or list(self._conversations[:8])
        self._conversation_table.set_rows([_conversation_table_row(item) for item in self._filtered_conversations])
        if self._filtered_conversations:
            self._conversation_table.select_absolute_row(0)
            first = self._filtered_conversations[0]
            self._conversation_status_badge.setText(f"会话跟踪：{first['status']} · {first['target']}")

    def _refresh_alert_cards(self) -> None:
        _clear_layout(self._alert_cards_layout)
        alerts: list[tuple[str, str, BadgeTone]] = [
            ("日限额提醒", "当前私信量已接近日配额 72%，建议优先保留高意向链路。", "warning"),
            ("变量安全提醒", "变量模板应避免出现空值，尤其是 {name} 和 {product} 两类常用字段。", "brand"),
            ("合规表述提醒", "首条消息避免直接促销，优先使用问答或场景建议切入。", "info"),
            ("频率提醒", "同一对象在 72 小时内不宜重复触达同一序列，以降低打扰感。", "warning"),
            ("人工接手提醒", "复杂问题和疑似售后问题应立刻转人工，不继续自动发送。", "neutral"),
        ]
        for title, text, tone in alerts:
            card = QFrame(self._alert_cards_host)
            _call(card, "setObjectName", "noteCard")
            box = QVBoxLayout(card)
            box.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
            box.setSpacing(SPACING_SM)
            top = QHBoxLayout()
            top.setContentsMargins(0, 0, 0, 0)
            top.setSpacing(SPACING_MD)
            heading = QLabel(title, card)
            _call(heading, "setObjectName", "sectionTitle")
            badge = StatusBadge("合规提示", tone, card)
            top.addWidget(heading, 1)
            top.addWidget(badge)
            body = QLabel(text, card)
            _call(body, "setObjectName", "bodyText")
            _call(body, "setWordWrap", True)
            box.addLayout(top)
            box.addWidget(body)
            self._alert_cards_layout.addWidget(card)
        self._alert_cards_layout.addStretch(1)

    def _populate_log_viewer(self) -> None:
        self._log_viewer.clear_logs()
        for item in AUTO_DM_LOGS:
            self._log_viewer.append_log(item["level"], item["message"], item["time"])
        if hasattr(self, "_log_status_badge"):
            latest = AUTO_DM_LOGS[0] if AUTO_DM_LOGS else {"level": "无", "time": "--"}
            self._log_status_badge.setText(f"日志 {len(AUTO_DM_LOGS)} 条")
            _call(self._log_status_value, "setText", f"最新 {latest['level']} · {latest['time']}")

    def _selected_rule(self) -> dict[str, Any] | None:
        for rule in self._rules:
            if str(rule.get("id", "")) == self._selected_rule_id:
                return rule
        return self._rules[0] if self._rules else None

    def _select_rule(self, rule_id: str) -> None:
        self._selected_rule_id = rule_id
        self._refresh_rule_cards()
        self._refresh_conversation_table()
        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已切换到私信规则【{rule.get('name', '')}】。")

    def _load_selected_rule_to_editor(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        self._selected_rule_badge.setText(f"当前规则：{rule.get('name', '')}")
        self._selected_rule_badge.set_tone("brand" if bool(rule.get("enabled", False)) else "neutral")
        for key in ("delivery_rate", "reply_rate", "conversion_rate", "last_run"):
            label = self._summary_labels.get(key)
            if label is not None:
                _call(label, "setText", str(rule.get(key, "--")))
        mapping = {
            "name": rule.get("name", ""),
            "daily_limit": rule.get("daily_limit", ""),
            "sequence": rule.get("sequence", ""),
            "auto_reply_chain": rule.get("auto_reply_chain", ""),
            "compliance": rule.get("compliance", ""),
        }
        for key, value in mapping.items():
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedLineEdit):
                widget.setText(str(value))
        for key in ("audience", "account_group"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedComboBox):
                _call(widget.combo_box, "setCurrentText", str(rule.get(key, "")))
        for key in ("followers", "commenters", "specific_lists"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, TagInput):
                widget.set_tags([str(item) for item in rule.get(key, [])])
        message_widget = self._editor_widgets.get("message_template")
        if isinstance(message_widget, ThemedTextEdit):
            message_widget.setPlainText(str(rule.get("message_template", "")))
        self._rule_editor.set_rule({"logic": "AND", "conditions": rule.get("conditions", []), "action": rule.get("action", {})})

    def _collect_editor_state(self) -> dict[str, Any]:
        rule = self._selected_rule()
        state: dict[str, Any] = {
            "id": str(rule.get("id", "")) if rule is not None else "",
            "name": self._read_line_edit("name"),
            "audience": self._read_combo_box("audience"),
            "account_group": self._read_combo_box("account_group"),
            "daily_limit": self._read_line_edit("daily_limit"),
            "followers": self._read_tags("followers"),
            "commenters": self._read_tags("commenters"),
            "specific_lists": self._read_tags("specific_lists"),
            "message_template": self._read_text_edit("message_template"),
            "sequence": self._read_line_edit("sequence"),
            "auto_reply_chain": self._read_line_edit("auto_reply_chain"),
            "compliance": self._read_line_edit("compliance"),
            "conditions": self._rule_editor.get_rule().get("conditions", []),
            "action": self._rule_editor.get_rule().get("action", {}),
        }
        if rule is not None:
            for key in ("delivery_rate", "reply_rate", "conversion_rate", "last_run", "sequence_steps", "notes"):
                state[key] = rule.get(key, "")
        return state

    def _read_line_edit(self, key: str) -> str:
        widget = self._editor_widgets.get(key)
        return widget.text() if isinstance(widget, ThemedLineEdit) else ""

    def _read_combo_box(self, key: str) -> str:
        widget = self._editor_widgets.get(key)
        return widget.current_text() if isinstance(widget, ThemedComboBox) else ""

    def _read_tags(self, key: str) -> list[str]:
        widget = self._editor_widgets.get(key)
        return widget.tags() if isinstance(widget, TagInput) else []

    def _read_text_edit(self, key: str) -> str:
        widget = self._editor_widgets.get(key)
        return widget.toPlainText() if isinstance(widget, ThemedTextEdit) else ""

    def _sync_editor_preview(self, *_args: object) -> None:
        state = self._collect_editor_state()
        self._preview_summary.setText(
            f"规则【{state.get('name', '') or '未命名规则'}】会面向【{state.get('audience', '') or '未设置人群'}】发送私信，使用账号池【{state.get('account_group', '') or '未设置'}】执行。"
        )
        self._preview_hint.setText(
            f"模板：{(state.get('message_template', '') or '暂无模板')[:120]}\n"
            f"新关注规则：{'、'.join(str(item) for item in state.get('followers', [])[:2]) or '暂无'}\n"
            f"评论用户规则：{'、'.join(str(item) for item in state.get('commenters', [])[:2]) or '暂无'}\n"
            f"指定清单：{'、'.join(str(item) for item in state.get('specific_lists', [])[:2]) or '暂无'}\n"
            f"序列：{state.get('sequence', '') or '未设置'} · 自动回复链：{state.get('auto_reply_chain', '') or '未设置'}\n"
            f"合规限制：{state.get('compliance', '') or '未设置'}"
        )
        if hasattr(self, "_conversation_status_badge"):
            _call(
                self._conversation_status_badge,
                "setText",
                f"会话跟踪：{state.get('audience', '') or '未设置人群'} · {state.get('sequence', '') or '未设置序列'}",
            )

    def _set_rule_enabled(self, rule_id: str, enabled: bool) -> None:
        for rule in self._rules:
            if str(rule.get("id", "")) == rule_id:
                rule["enabled"] = enabled
                self._append_operation_log(f"私信规则【{rule.get('name', '')}】已{('开启' if enabled else '关闭')}。")
                break
        self._refresh_all_views()

    def _on_console_toggled(self, checked: bool) -> None:
        self._page_enabled = checked
        self._append_operation_log("自动私信总开关已开启。" if checked else "自动私信总开关已关闭，仅保留监控。")
        self._refresh_sidebar_summary()

    def _on_save_rule(self) -> None:
        state = self._collect_editor_state()
        for index, rule in enumerate(self._rules):
            if str(rule.get("id", "")) == str(state.get("id", "")):
                merged = _copy_rule(rule)
                merged.update(state)
                self._rules[index] = merged
                self._selected_rule_id = str(merged.get("id", ""))
                break
        self._append_operation_log(f"私信规则【{state.get('name', '') or '未命名规则'}】已保存。")
        self._refresh_all_views()

    def _on_reset_editor(self) -> None:
        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已恢复私信规则【{rule.get('name', '')}】。")

    def _on_clone_rule(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        cloned = _copy_rule(rule)
        cloned["id"] = f"{rule.get('id', 'rule')}-copy-{len(self._rules) + 1}"
        cloned["name"] = f"{rule.get('name', '')}（副本）"
        cloned["last_run"] = "尚未执行"
        self._rules.insert(0, cloned)
        self._selected_rule_id = str(cloned.get("id", ""))
        self._append_operation_log(f"已复制私信规则【{rule.get('name', '')}】。")
        self._refresh_all_views()

    def _on_create_rule(self) -> None:
        new_rule = {
            "id": f"dm-rule-new-{len(self._rules) + 1}",
            "name": "新建私信规则",
            "audience": "新关注用户",
            "sequence": "2 步欢迎链",
            "daily_limit": "60",
            "delivery_rate": "--",
            "reply_rate": "--",
            "conversion_rate": "--",
            "enabled": True,
            "last_run": "尚未执行",
            "account_group": "品牌主号 A 组",
            "followers": ["近 24 小时新关注"],
            "commenters": ["无"],
            "specific_lists": ["示例名单"],
            "message_template": "你好 {name}，如果你最近在看 {product}，我可以先按你的使用场景发一个更快的建议给你。",
            "sequence_steps": ["欢迎", "轻提醒"],
            "auto_reply_chain": "积极回复 → 第 2 步；复杂问题 → 人工",
            "compliance": "每账号每小时不超过 8 条",
            "notes": ["建议先低频试跑。"],
            "conditions": [{"field": "关注时间", "operator": "小于", "value": "24 小时"}],
            "action": {"type": "执行任务", "value": "发送欢迎私信"},
        }
        self._rules.insert(0, new_rule)
        self._selected_rule_id = str(new_rule["id"])
        self._append_operation_log("已创建新的私信规则草稿。")
        self._refresh_all_views()

    def _on_run_rule(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        self._conversations.insert(0, {"time": "15:36", "target": "@manual_dm_01", "phase": "手动触发", "status": "已送达", "message": str(rule.get("message_template", ""))[:42], "next": "等待回复", "result": "预演完成"})
        rule["last_run"] = "15:36"
        self._append_operation_log(f"已手动触发规则【{rule.get('name', '')}】执行一轮私信。")
        self._refresh_all_views()

    def _on_sequence_selected(self, row_index: int) -> None:
        if not (0 <= row_index < len(self._sequence_steps)):
            return
        item = self._sequence_steps[row_index]
        self._sequence_status_badge.setText(f"{item['step']} · {item['summary']}")

    def _on_conversation_selected(self, row_index: int) -> None:
        if not (0 <= row_index < len(self._filtered_conversations)):
            return
        item = self._filtered_conversations[row_index]
        tone: BadgeTone = "success"
        if item["status"] == "需人工":
            tone = "warning"
        elif item["status"] == "已跳过":
            tone = "neutral"
        self._conversation_status_badge.setText(f"{item['status']} · {item['target']}")
        self._conversation_status_badge.set_tone(tone)

    def _insert_name_variable(self) -> None:
        self._append_variable("{name}")

    def _insert_product_variable(self) -> None:
        self._append_variable("{product}")

    def _insert_offer_variable(self) -> None:
        self._append_variable("{offer}")

    def _append_variable(self, variable: str) -> None:
        widget = self._editor_widgets.get("message_template")
        if not isinstance(widget, ThemedTextEdit):
            return
        text = widget.toPlainText().rstrip()
        widget.setPlainText((text + " " + variable).strip())
        self._append_operation_log(f"已插入变量 {variable}。")

    def _append_batch_hint_log(self) -> None:
        self._append_operation_log("可继续扩展批量换模板、批量调整序列步数、批量暂停低转化链。")

    def _append_operation_log(self, message: str) -> None:
        self._log_viewer.append_log("操作", message, "2026-03-09 15:38:00")

    def on_activated(self) -> None:
        self._refresh_all_views()

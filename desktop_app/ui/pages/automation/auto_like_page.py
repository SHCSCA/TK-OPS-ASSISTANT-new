# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""自动点赞原型页面。"""

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
    "账号池",
    "目标范围",
    "内容类型",
    "频率",
    "今日任务",
    "成功率",
    "状态",
]

EXECUTION_TABLE_HEADERS = [
    "执行时间",
    "账号",
    "目标",
    "内容类型",
    "状态",
    "行为节奏",
    "结果说明",
]

STATISTICS_CARDS: list[dict[str, Any]] = [{"title": "今日点赞量", "value": "3,286", "trend": "up", "percentage": "+16.8%", "caption": "热门标签任务在午后集中放量", "sparkline": [210, 256, 278, 301, 332, 368, 402]}, {"title": "成功率", "value": "92.4%", "trend": "up", "percentage": "+3.2%", "caption": "随机延迟策略降低了风控拦截", "sparkline": [84, 85, 87, 88, 89, 91, 92]}, {"title": "活跃账号", "value": "18", "trend": "flat", "percentage": "+0.0%", "caption": "品牌号与矩阵号维持平衡轮转", "sparkline": [17, 17, 18, 18, 18, 18, 18]}, {"title": "今日任务", "value": "42", "trend": "up", "percentage": "+6.1%", "caption": "新增 6 组垂类内容池待执行", "sparkline": [25, 26, 29, 31, 35, 39, 42]}]
ACCOUNT_OPTIONS = ["全部账号池", "品牌主号 A 组", "品牌主号 B 组", "女装矩阵号", "家居矩阵号", "美妆矩阵号", "鞋包矩阵号", "北美测试号", "东南亚测试号", "达人合作号", "新号孵化池"]
CONTENT_TYPE_OPTIONS = ["全部类型", "短视频", "商品卡", "图文", "达人联动内容", "合集页"]
AUTO_LIKE_LOGS: list[dict[str, str]] = [{"level": "成功", "time": "2026-03-09 15:02:18", "message": "任务【春季穿搭标签扩量】已完成本轮 86 次点赞，平均延迟 14.2 秒。"}, {"level": "成功", "time": "2026-03-09 14:58:40", "message": "账号池【家居矩阵号】切换到第二批账号继续执行，未触发频率预警。"}, {"level": "预警", "time": "2026-03-09 14:54:12", "message": "账号 @homefocus_03 在 5 分钟内点赞密度偏高，系统已自动插入 180 秒缓冲。"}, {"level": "成功", "time": "2026-03-09 14:49:56", "message": "任务【竞对热视频跟进】命中 12 条高互动视频，点赞操作全部成功。"}, {"level": "忽略", "time": "2026-03-09 14:42:33", "message": "目标用户 @style_reuse_7 被列入重复互动名单，本轮已自动跳过。"}, {"level": "成功", "time": "2026-03-09 14:36:28", "message": "系统按人性化行为模式完成 24 次点赞，间隔分布落在 9-23 秒之间。"}, {"level": "预警", "time": "2026-03-09 14:31:04", "message": "标签 #minimaldesk 在近 10 分钟新增视频过少，建议切换备用目标池。"}, {"level": "成功", "time": "2026-03-09 14:26:51", "message": "任务【达人合作内容冷启动】已完成首轮点赞预热，预计 20 分钟后复扫。"}, {"level": "忽略", "time": "2026-03-09 14:18:11", "message": "视频 vid_823150 已在昨日执行过点赞，系统已做去重处理。"}, {"level": "成功", "time": "2026-03-09 14:09:43", "message": "账号 @beauty_lab_08 通过轻量节奏执行完成 40 次点赞，成功率 97%。"}, {"level": "成功", "time": "2026-03-09 14:02:05", "message": "任务【北美健身热视频池】已更新内容类型过滤条件，仅保留短视频。"}, {"level": "预警", "time": "2026-03-09 13:55:27", "message": "检测到 2 个账号登录环境相似度偏高，建议下一轮切换设备指纹。"}]
EXECUTION_HISTORY: list[dict[str, str]] = [{"time": "15:00:12", "account": "@brand_wave_01", "target": "#春季穿搭 / @ootd_daily", "content_type": "短视频", "status": "成功", "tempo": "随机 12-20 秒", "result": "完成 32 次点赞，无异常"}, {"time": "14:56:48", "account": "@homefocus_03", "target": "#收纳灵感 / @roomreset", "content_type": "图文", "status": "降速", "tempo": "插入 180 秒缓冲", "result": "节奏过快，系统自动放缓"}, {"time": "14:53:16", "account": "@beauty_lab_08", "target": "#底妆教程 / @glowmakeup", "content_type": "短视频", "status": "成功", "tempo": "随机 9-17 秒", "result": "命中 28 条目标内容"}, {"time": "14:47:39", "account": "@fitnorth_02", "target": "#居家健身 / @trainwithme", "content_type": "短视频", "status": "成功", "tempo": "随机 14-21 秒", "result": "点赞 25 次，账号健康正常"}, {"time": "14:40:26", "account": "@bagshow_05", "target": "@urbanbagclub", "content_type": "商品卡", "status": "跳过", "tempo": "安全去重", "result": "目标内容已执行过"}, {"time": "14:34:18", "account": "@decorplus_02", "target": "#极简书桌 / @deskframe", "content_type": "图文", "status": "成功", "tempo": "随机 11-19 秒", "result": "完成 19 次点赞"}, {"time": "14:28:50", "account": "@brand_wave_03", "target": "#新品开箱 / @trendcatch", "content_type": "达人联动内容", "status": "成功", "tempo": "随机 15-24 秒", "result": "首轮曝光预热完成"}, {"time": "14:22:11", "account": "@shoepulse_11", "target": "#通勤球鞋 / @streetpick", "content_type": "短视频", "status": "成功", "tempo": "随机 13-20 秒", "result": "完成 26 次点赞"}, {"time": "14:16:05", "account": "@brand_wave_06", "target": "#夏日水杯 / @dailycup", "content_type": "商品卡", "status": "成功", "tempo": "随机 10-16 秒", "result": "商品卡点击热视频已覆盖"}, {"time": "14:08:57", "account": "@homefocus_06", "target": "#阳台改造 / @greenhome", "content_type": "短视频", "status": "失败", "tempo": "重试 2 次", "result": "接口超时，待下一轮补跑"}, {"time": "14:01:33", "account": "@beauty_lab_03", "target": "#平价护肤 / @skinfile", "content_type": "短视频", "status": "成功", "tempo": "随机 12-18 秒", "result": "点赞 34 次，互动稳定"}, {"time": "13:55:10", "account": "@fitnorth_07", "target": "#跑步装备 / @runnerpick", "content_type": "合集页", "status": "成功", "tempo": "随机 18-26 秒", "result": "合集内容点赞 14 次"}]

def _like_rule(data: dict[str, Any]) -> dict[str, Any]:
    base = {"enabled": True, "target_users": [], "notes": [], "conditions": [], "action": {"type": "执行任务", "value": "执行点赞"}}
    base.update(data)
    return base

DEMO_RULES: list[dict[str, Any]] = [
    _like_rule({"id": "like-rule-01", "name": "春季穿搭标签扩量", "account_group": "女装矩阵号", "account": "品牌主号 A 组", "content_type": "短视频", "hashtags": ["#春季穿搭", "#今日穿什么", "#通勤搭配", "#显瘦穿搭"], "target_users": ["@ootd_daily", "@style_snap", "@urbancloset"], "target_scope": "标签 + 指定达人", "frequency": "每 12 分钟一轮", "time_window": "09:00-22:30", "daily_limit": "320", "rate_limit": "每账号每小时 42 次", "random_delay": "9-23 秒", "behavior_mode": "高仿真人", "today_tasks": "86", "today_success": "80", "success_rate": "93.0%", "last_run": "15:00", "risk_level": "低风险", "notes": ["优先点赞近 3 小时发布内容。", "评论区争议高的视频自动排除。", "遇到重复作者 30 分钟内不重复互动。"], "conditions": [{"field": "视频发布时间", "operator": "小于", "value": "180 分钟"}, {"field": "点赞量", "operator": "大于", "value": "300"}], "action": {"type": "执行任务", "value": "执行点赞并记录节奏"}}),
    _like_rule({"id": "like-rule-02", "name": "家居收纳热门图文跟进", "account_group": "家居矩阵号", "account": "家居矩阵号", "content_type": "图文", "hashtags": ["#收纳灵感", "#家居布置", "#房间整理"], "target_users": ["@roomreset", "@calmspace_cn"], "target_scope": "标签优先", "frequency": "每 18 分钟一轮", "time_window": "10:00-23:00", "daily_limit": "240", "rate_limit": "每账号每小时 28 次", "random_delay": "11-28 秒", "behavior_mode": "平衡模式", "today_tasks": "54", "today_success": "49", "success_rate": "90.7%", "last_run": "14:56", "risk_level": "中风险", "notes": ["图文页点赞后不立即切换账号。", "遇到同作者连续内容，最多保留 2 条。"], "conditions": [{"field": "内容类型", "operator": "等于", "value": "图文"}, {"field": "收藏量", "operator": "大于", "value": "50"}], "action": {"type": "执行任务", "value": "优先点赞高收藏图文"}}),
    _like_rule({"id": "like-rule-03", "name": "底妆教程热视频预热", "account_group": "美妆矩阵号", "account": "美妆矩阵号", "content_type": "短视频", "hashtags": ["#底妆教程", "#平价底妆", "#化妆技巧"], "target_users": ["@glowmakeup", "@softskinlab", "@beautyminute"], "target_scope": "达人内容池", "frequency": "每 10 分钟一轮", "time_window": "08:30-23:30", "daily_limit": "360", "rate_limit": "每账号每小时 46 次", "random_delay": "8-18 秒", "behavior_mode": "高仿真人", "today_tasks": "73", "today_success": "69", "success_rate": "94.5%", "last_run": "14:53", "risk_level": "低风险", "notes": ["高热视频优先于新发布内容。", "夜间时段自动减少 20% 频次。"], "conditions": [{"field": "播放量", "operator": "大于", "value": "5000"}, {"field": "账号语言", "operator": "等于", "value": "中文"}], "action": {"type": "执行任务", "value": "对高热视频做首轮互动"}}),
    _like_rule({"id": "like-rule-04", "name": "居家健身短视频扩列", "account_group": "北美测试号", "account": "北美测试号", "content_type": "短视频", "hashtags": ["#居家健身", "#fitnessathome", "#quickworkout"], "target_users": ["@trainwithme", "@fitcoachnow"], "target_scope": "北美热视频", "frequency": "每 15 分钟一轮", "time_window": "18:00-08:00", "daily_limit": "180", "rate_limit": "每账号每小时 25 次", "random_delay": "15-30 秒", "behavior_mode": "保守模式", "today_tasks": "31", "today_success": "28", "success_rate": "90.3%", "last_run": "14:47", "risk_level": "中风险", "notes": ["跨时区任务统一用本地晚间时段启动。"], "conditions": [{"field": "地区", "operator": "等于", "value": "北美"}, {"field": "发布时间", "operator": "小于", "value": "240 分钟"}], "action": {"type": "执行任务", "value": "保守节奏执行"}}),
    _like_rule({"id": "like-rule-05", "name": "鞋包通勤内容轻量互动", "account_group": "鞋包矩阵号", "account": "鞋包矩阵号", "content_type": "短视频", "hashtags": ["#通勤球鞋", "#今日包包", "#上班穿搭"], "target_users": ["@streetpick", "@urbanbagclub"], "target_scope": "垂类达人", "frequency": "每 20 分钟一轮", "time_window": "07:30-21:30", "daily_limit": "210", "rate_limit": "每账号每小时 24 次", "random_delay": "16-32 秒", "behavior_mode": "保守模式", "enabled": False, "today_tasks": "16", "today_success": "15", "success_rate": "93.8%", "last_run": "13:58", "risk_level": "低风险", "notes": ["当前关闭，等待素材侧内容上线后再联动。"], "conditions": [{"field": "内容类型", "operator": "等于", "value": "短视频"}, {"field": "作者标签", "operator": "包含", "value": "通勤"}], "action": {"type": "暂停任务", "value": "待上新后恢复"}}),
    _like_rule({"id": "like-rule-06", "name": "极简书桌图文捞热", "account_group": "家居矩阵号", "account": "品牌主号 B 组", "content_type": "图文", "hashtags": ["#极简书桌", "#桌搭分享", "#办公灵感"], "target_users": ["@deskframe", "@workmood"], "target_scope": "标签图文池", "frequency": "每 22 分钟一轮", "time_window": "09:00-23:00", "daily_limit": "160", "rate_limit": "每账号每小时 18 次", "random_delay": "17-36 秒", "behavior_mode": "平衡模式", "today_tasks": "29", "today_success": "27", "success_rate": "93.1%", "last_run": "14:34", "risk_level": "低风险", "notes": ["图文点赞任务优先保留收藏型内容。"], "conditions": [{"field": "收藏量", "operator": "大于", "value": "80"}, {"field": "评论量", "operator": "大于", "value": "10"}], "action": {"type": "执行任务", "value": "图文捞热"}}),
    _like_rule({"id": "like-rule-07", "name": "新品开箱达人联动", "account_group": "达人合作号", "account": "达人合作号", "content_type": "达人联动内容", "hashtags": ["#新品开箱", "#本周上新", "#值得买"], "target_users": ["@trendcatch", "@firstlooklab", "@buyersclub"], "target_scope": "合作达人白名单", "frequency": "每 30 分钟一轮", "time_window": "10:00-20:00", "daily_limit": "120", "rate_limit": "每账号每小时 12 次", "random_delay": "20-40 秒", "behavior_mode": "保守模式", "today_tasks": "18", "today_success": "18", "success_rate": "100.0%", "last_run": "14:28", "risk_level": "低风险", "notes": ["只对白名单达人执行。", "优先在合作视频发布后 20 分钟内启动。"], "conditions": [{"field": "达人类型", "operator": "等于", "value": "白名单"}, {"field": "发布时间", "operator": "小于", "value": "60 分钟"}], "action": {"type": "执行任务", "value": "合作内容预热点赞"}}),
    _like_rule({"id": "like-rule-08", "name": "通勤球鞋热视频复扫", "account_group": "鞋包矩阵号", "account": "鞋包矩阵号", "content_type": "短视频", "hashtags": ["#通勤球鞋", "#球鞋分享", "#穿搭细节"], "target_users": ["@streetpick", "@sneakerroom"], "target_scope": "热视频复扫", "frequency": "每 26 分钟一轮", "time_window": "11:00-23:30", "daily_limit": "170", "rate_limit": "每账号每小时 20 次", "random_delay": "18-34 秒", "behavior_mode": "平衡模式", "today_tasks": "24", "today_success": "22", "success_rate": "91.7%", "last_run": "14:22", "risk_level": "中风险", "notes": ["复扫时避免同一作者连续命中。"], "conditions": [{"field": "播放量", "operator": "大于", "value": "8000"}, {"field": "重复作者命中次数", "operator": "小于", "value": "2"}], "action": {"type": "执行任务", "value": "热视频复扫点赞"}}),
    _like_rule({"id": "like-rule-09", "name": "夏日水杯商品卡点亮", "account_group": "品牌主号 A 组", "account": "品牌主号 A 组", "content_type": "商品卡", "hashtags": ["#夏日水杯", "#随行杯", "#办公室好物"], "target_users": ["@dailycup", "@deskdrink"], "target_scope": "商品卡内容池", "frequency": "每 14 分钟一轮", "time_window": "09:30-22:00", "daily_limit": "260", "rate_limit": "每账号每小时 30 次", "random_delay": "10-18 秒", "behavior_mode": "高仿真人", "today_tasks": "47", "today_success": "43", "success_rate": "91.5%", "last_run": "14:16", "risk_level": "低风险", "notes": ["商品卡任务要避开重复 SKU 页面。"], "conditions": [{"field": "内容类型", "operator": "等于", "value": "商品卡"}, {"field": "SKU 重复度", "operator": "小于", "value": "2"}], "action": {"type": "执行任务", "value": "商品卡首轮互动"}}),
    _like_rule({"id": "like-rule-10", "name": "阳台改造内容冷启动", "account_group": "家居矩阵号", "account": "家居矩阵号", "content_type": "短视频", "hashtags": ["#阳台改造", "#绿植角落", "#小户型灵感"], "target_users": ["@greenhome", "@balconystory"], "target_scope": "新热视频池", "frequency": "每 16 分钟一轮", "time_window": "10:30-21:00", "daily_limit": "190", "rate_limit": "每账号每小时 22 次", "random_delay": "14-26 秒", "behavior_mode": "平衡模式", "today_tasks": "22", "today_success": "18", "success_rate": "81.8%", "last_run": "14:08", "risk_level": "中风险", "notes": ["失败重试仅做 1 次。", "接口波动时改为低频模式。"], "conditions": [{"field": "视频发布时间", "operator": "小于", "value": "90 分钟"}, {"field": "评论量", "operator": "大于", "value": "6"}], "action": {"type": "发送提醒", "value": "失败后提醒运营复核"}}),
    _like_rule({"id": "like-rule-11", "name": "平价护肤内容滚动点赞", "account_group": "美妆矩阵号", "account": "美妆矩阵号", "content_type": "短视频", "hashtags": ["#平价护肤", "#护肤干货", "#护肤分享"], "target_users": ["@skinfile", "@beautyclean"], "target_scope": "标签滚动池", "frequency": "每 12 分钟一轮", "time_window": "08:00-23:00", "daily_limit": "300", "rate_limit": "每账号每小时 36 次", "random_delay": "10-20 秒", "behavior_mode": "高仿真人", "today_tasks": "59", "today_success": "55", "success_rate": "93.2%", "last_run": "14:01", "risk_level": "低风险", "notes": ["高赞护肤笔记优先级更高。"], "conditions": [{"field": "点赞量", "operator": "大于", "value": "500"}, {"field": "作者粉丝量", "operator": "大于", "value": "5000"}], "action": {"type": "执行任务", "value": "滚动点赞保热"}}),
    _like_rule({"id": "like-rule-12", "name": "跑步装备合集页试探", "account_group": "北美测试号", "account": "北美测试号", "content_type": "合集页", "hashtags": ["#跑步装备", "#runnerkit", "#traininggear"], "target_users": ["@runnerpick", "@gearfit"], "target_scope": "合集页试探池", "frequency": "每 40 分钟一轮", "time_window": "19:00-07:00", "daily_limit": "90", "rate_limit": "每账号每小时 10 次", "random_delay": "24-45 秒", "behavior_mode": "保守模式", "enabled": False, "today_tasks": "8", "today_success": "7", "success_rate": "87.5%", "last_run": "13:55", "risk_level": "中风险", "notes": ["合集页数据样本有限，当前暂不放量。"], "conditions": [{"field": "内容类型", "operator": "等于", "value": "合集页"}, {"field": "地区", "operator": "等于", "value": "北美"}], "action": {"type": "暂停任务", "value": "等待更多样本"}}),
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
    """深拷贝规则字典。"""

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
    hashtags = rule.get("hashtags", [])
    preview = " / ".join(str(item) for item in hashtags[:2])
    if len(hashtags) > 2:
        preview = f"{preview} 等 {len(hashtags)} 个"
    return [
        str(rule.get("name", "")),
        str(rule.get("account_group", "")),
        preview,
        str(rule.get("content_type", "")),
        str(rule.get("frequency", "")),
        str(rule.get("today_tasks", "0")),
        str(rule.get("success_rate", "--")),
        _toggle_text(bool(rule.get("enabled", False))),
    ]


def _execution_table_row(item: dict[str, str]) -> list[object]:
    return [
        item["time"],
        item["account"],
        item["target"],
        item["content_type"],
        item["status"],
        item["tempo"],
        item["result"],
    ]


class AutoLikePage(BasePage):
    """自动点赞页面。"""

    default_route_id = RouteId("auto_like")
    default_display_name = "自动点赞"
    default_icon_name = "favorite"

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
        self._execution_records: list[dict[str, str]] = [item.copy() for item in EXECUTION_HISTORY]
        self._filtered_execution_records: list[dict[str, str]] = list(self._execution_records)
        self._selected_rule_id: str = str(self._rules[0]["id"]) if self._rules else ""
        self._selected_execution_index: int = 0
        self._rule_card_widgets: list[dict[str, object]] = []
        self._kpi_cards: list[KPICard] = []
        self._editor_widgets: dict[str, object] = {}
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        """构建自动点赞页面。"""

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        root = QWidget(self)
        _call(root, "setObjectName", "autoLikeRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.layout.addWidget(root)

        self._refresh_button = IconButton("↻", "刷新自动点赞状态", self)
        self._new_rule_button = PrimaryButton("新增点赞规则", self, icon_text="＋")
        container = PageContainer(
            title="自动点赞",
            description="围绕账号池、目标规则、点赞节奏与安全阈值，快速搭建可交互的自动点赞执行原型。",
            actions=[self._refresh_button, self._new_rule_button],
            parent=root,
        )
        container.content_layout.setSpacing(SPACING_2XL)
        root_layout.addWidget(container)

        container.add_widget(self._build_console_banner())
        container.add_widget(self._build_kpi_row())
        container.add_widget(self._build_workspace())

        self._bind_interactions()
        self._refresh_all_views()

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        colors = _palette()
        brand_tint = _rgba(colors.primary, 0.08)
        brand_tint_hover = _rgba(colors.primary, 0.14)
        brand_border = _rgba(colors.primary, 0.20)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget {{
                color: {colors.text};
                font-family: {_static_token('font.family.chinese')};
            }}
            QWidget#autoLikeRoot {{
                background-color: {_token('surface.primary')};
            }}
            QFrame#consoleBanner,
            QFrame#sidebarPanel,
            QFrame#editorPanel,
            QFrame#monitorPanel,
            QFrame#miniPanel,
            QFrame#ruleCard,
            QFrame#previewPanel,
            QFrame#noteCard,
            QFrame#summaryStrip,
            QFrame#statusPanel {{
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
                background-color: {brand_tint_hover};
            }}
            QLabel#statusPanelValue {{
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
                color: {colors.text};
                background: transparent;
            }}
            """,
        )

    def _build_console_banner(self) -> QWidget:
        panel = QFrame(self)
        _call(panel, "setObjectName", "consoleBanner")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(SPACING_2XL, SPACING_XL, SPACING_2XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        left = QWidget(panel)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(SPACING_XS)
        title = QLabel("启用自动点赞执行引擎", left)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("系统会按照账号池轮转、标签目标、内容类型与安全节奏自动完成点赞任务，并在异常时主动降速。", left)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(SPACING_MD)
        self._system_badge = StatusBadge("执行中", "success", left)
        self._coverage_badge = StatusBadge("覆盖 12 套规则", "brand", left)
        self._safety_badge = StatusBadge("安全节奏已启用", "warning", left)
        badge_row.addWidget(self._system_badge)
        badge_row.addWidget(self._coverage_badge)
        badge_row.addWidget(self._safety_badge)
        badge_row.addStretch(1)
        left_layout.addWidget(title)
        left_layout.addWidget(caption)
        left_layout.addLayout(badge_row)

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
        self._console_summary_label = QLabel("当前启用 10 条规则，2 条处于待机状态", right)
        _call(self._console_summary_label, "setObjectName", "summaryValue")
        tip = QLabel("建议在账号环境异常时仅保留低频规则，并开启随机延迟。", right)
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
        outer_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.30, 0.70),
            minimum_sizes=(320, 760),
            parent=self,
        )
        right_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.56, 0.44),
            minimum_sizes=(500, 360),
            parent=outer_split,
        )
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
        title = QLabel("点赞规则列表", header)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("先选择账号池和筛选条件，再针对单条规则调整目标与执行节奏。", header)
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
        filter_hint = QLabel("先按账号池、状态和内容类型收敛规则，再进入中间编辑器调整细节。", filter_panel)
        _call(filter_hint, "setObjectName", "sectionCaption")
        _call(filter_hint, "setWordWrap", True)
        filter_layout.addWidget(filter_title)
        filter_layout.addWidget(filter_hint)

        self._account_filter = ThemedComboBox("账号池", ACCOUNT_OPTIONS)
        self._rule_search = SearchBar("搜索规则、标签或目标账号")
        self._status_filter = ThemedComboBox("状态筛选", ["全部状态", "仅看已开启", "仅看已关闭"])
        self._content_type_filter = ThemedComboBox("内容类型", CONTENT_TYPE_OPTIONS)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(SPACING_MD)
        self._clone_button = PrimaryButton("复制规则", panel, icon_text="⎘")
        self._batch_button = IconButton("⋯", "批量操作提示", panel)
        actions.addWidget(self._clone_button, 1)
        actions.addWidget(self._batch_button)

        self._rule_cards_host = QWidget(panel)
        self._rule_cards_layout = QVBoxLayout(self._rule_cards_host)
        self._rule_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._rule_cards_layout.setSpacing(SPACING_MD)

        self._sidebar_summary = self._build_mini_panel("当前重点", "标签扩量 + 内容复扫", "点赞任务以垂类热视频和商品卡预热为主。")

        layout.addWidget(header)
        filter_layout.addWidget(self._rule_search)
        filter_layout.addWidget(self._account_filter)
        filter_layout.addWidget(self._status_filter)
        filter_layout.addWidget(self._content_type_filter)
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
        title_host = QWidget(header)
        title_layout = QVBoxLayout(title_host)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_XS)
        title = QLabel("执行配置", title_host)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("在中间区域设置目标标签、执行时间窗、日限额与人性化行为参数。", title_host)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        title_layout.addWidget(title)
        title_layout.addWidget(caption)
        self._selected_rule_badge = StatusBadge("当前规则：春季穿搭标签扩量", "brand", header)
        header_layout.addWidget(title_host, 1)
        header_layout.addWidget(self._selected_rule_badge)

        summary = QFrame(panel)
        _call(summary, "setObjectName", "summaryStrip")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        summary_layout.setSpacing(SPACING_XL)
        self._summary_labels: dict[str, QLabel] = {}
        for label_text, key in (("风险等级", "risk_level"), ("今日任务", "today_tasks"), ("成功率", "success_rate"), ("最近执行", "last_run")):
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

        basic_section = ContentSection("账号与目标配置", "◎", parent=panel)
        row1 = QWidget(basic_section)
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(SPACING_XL)
        self._editor_widgets["name"] = ThemedLineEdit("规则名称", "请输入点赞规则名称", "建议按垂类 + 目标池命名")
        self._editor_widgets["account_group"] = ThemedComboBox("账号池", ACCOUNT_OPTIONS[1:])
        self._editor_widgets["content_type"] = ThemedComboBox("内容类型", CONTENT_TYPE_OPTIONS[1:])
        self._editor_widgets["target_scope"] = ThemedComboBox("目标范围", ["标签优先", "达人内容池", "标签 + 指定达人", "商品卡内容池", "合作达人白名单", "新热视频池"])
        row1_layout.addWidget(self._editor_widgets["name"], 2)
        row1_layout.addWidget(self._editor_widgets["account_group"], 1)
        row1_layout.addWidget(self._editor_widgets["content_type"], 1)
        row1_layout.addWidget(self._editor_widgets["target_scope"], 1)
        basic_section.add_widget(row1)

        self._editor_widgets["hashtags"] = TagInput("目标标签", "输入标签后回车确认，例如：#春季穿搭")
        self._editor_widgets["target_users"] = TagInput("目标账号", "输入目标用户后回车确认，例如：@ootd_daily")
        basic_section.add_widget(self._editor_widgets["hashtags"])
        basic_section.add_widget(self._editor_widgets["target_users"])

        schedule_section = ContentSection("时间窗与任务节奏", "◴", parent=panel)
        row2 = QWidget(schedule_section)
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(SPACING_XL)
        self._editor_widgets["frequency"] = ThemedLineEdit("执行频率", "如：每 12 分钟一轮", "高热视频建议更高频，低热度池建议保守")
        self._editor_widgets["time_window"] = ThemedLineEdit("执行时间窗", "如：09:00-22:30", "建议避开账号休眠时段")
        self._editor_widgets["daily_limit"] = ThemedLineEdit("单日上限", "如：320", "超过上限后自动切换待机")
        self._editor_widgets["rate_limit"] = ThemedLineEdit("小时频率限制", "如：每账号每小时 42 次", "用于安全节流")
        row2_layout.addWidget(self._editor_widgets["frequency"], 1)
        row2_layout.addWidget(self._editor_widgets["time_window"], 1)
        row2_layout.addWidget(self._editor_widgets["daily_limit"], 1)
        row2_layout.addWidget(self._editor_widgets["rate_limit"], 1)
        schedule_section.add_widget(row2)

        safety_section = ContentSection("安全设置", "⚑", parent=panel)
        row3 = QWidget(safety_section)
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(SPACING_XL)
        self._editor_widgets["random_delay"] = ThemedLineEdit("随机延迟", "如：9-23 秒", "区间越自然，越接近真人行为")
        self._editor_widgets["behavior_mode"] = ThemedComboBox("行为模式", ["高仿真人", "平衡模式", "保守模式"])
        self._editor_widgets["notes"] = ThemedTextEdit("安全备注", "记录风控观察、去重逻辑或特殊说明")
        row3_layout.addWidget(self._editor_widgets["random_delay"], 1)
        row3_layout.addWidget(self._editor_widgets["behavior_mode"], 1)
        safety_toggle_host = QWidget(row3)
        safety_toggle_layout = QVBoxLayout(safety_toggle_host)
        safety_toggle_layout.setContentsMargins(0, 0, 0, 0)
        safety_toggle_layout.setSpacing(SPACING_SM)
        safety_toggle_label = QLabel("启用人性化行为", safety_toggle_host)
        _call(safety_toggle_label, "setObjectName", "summaryLabel")
        self._editor_widgets["enabled"] = ToggleSwitch(True)
        safety_toggle_layout.addWidget(safety_toggle_label)
        safety_toggle_layout.addWidget(self._editor_widgets["enabled"])
        safety_toggle_layout.addStretch(1)
        row3_layout.addWidget(safety_toggle_host)
        safety_section.add_widget(row3)
        safety_section.add_widget(self._editor_widgets["notes"])

        automation_section = ContentSection("规则编排", "⌁", parent=panel)
        self._rule_editor = RuleEditorWidget(panel)
        automation_section.add_widget(self._rule_editor)

        preview = QFrame(panel)
        _call(preview, "setObjectName", "previewPanel")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        preview_layout.setSpacing(SPACING_SM)
        preview_title = QLabel("执行预览", preview)
        _call(preview_title, "setObjectName", "sectionTitle")
        self._preview_summary = QLabel("当前规则将针对春季穿搭类短视频执行点赞。", preview)
        _call(self._preview_summary, "setObjectName", "bodyText")
        _call(self._preview_summary, "setWordWrap", True)
        self._preview_hint = QLabel("系统会按照账号池轮转和随机延迟执行。", preview)
        _call(self._preview_hint, "setObjectName", "summaryLabel")
        _call(self._preview_hint, "setWordWrap", True)
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self._preview_summary)
        preview_layout.addWidget(self._preview_hint)

        footer = QWidget(panel)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(SPACING_MD)
        self._insert_delay_button = QPushButton("插入安全延迟建议", footer)
        _call(self._insert_delay_button, "setObjectName", "ghostChip")
        self._reset_button = QPushButton("恢复当前规则", footer)
        _call(self._reset_button, "setObjectName", "ghostChip")
        self._run_button = PrimaryButton("立即执行一轮", footer, icon_text="▶")
        self._save_button = PrimaryButton("保存配置", footer, icon_text="✓")
        footer_layout.addWidget(self._insert_delay_button)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self._reset_button)
        footer_layout.addWidget(self._run_button)
        footer_layout.addWidget(self._save_button)

        layout.addWidget(header)
        layout.addWidget(summary)
        layout.addWidget(basic_section)
        layout.addWidget(schedule_section)
        layout.addWidget(safety_section)
        layout.addWidget(automation_section)
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

        header = QWidget(panel)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_XS)
        title = QLabel("执行监控", header)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("同时查看执行历史、实时日志与风控提示，快速判断当前点赞任务是否需要降速。", header)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        header_layout.addWidget(title)
        header_layout.addWidget(caption)

        mini_row = QWidget(panel)
        mini_layout = QHBoxLayout(mini_row)
        mini_layout.setContentsMargins(0, 0, 0, 0)
        mini_layout.setSpacing(SPACING_MD)
        self._live_panel = self._build_mini_panel("当前轮速", "12 次 / 5 分钟", "执行节奏处于安全区间")
        self._risk_panel = self._build_mini_panel("风控提醒", "2 条", "1 个账号已自动插入缓冲")
        self._queue_panel = self._build_mini_panel("待执行池", "146 条内容", "标签池与达人池都在更新")
        mini_layout.addWidget(self._live_panel, 1)
        mini_layout.addWidget(self._risk_panel, 1)
        mini_layout.addWidget(self._queue_panel, 1)

        self._monitor_tabs = TabBar(panel)
        self._monitor_tabs.add_tab("执行记录", self._build_execution_tab())
        self._monitor_tabs.add_tab("实时日志", self._build_log_tab())
        self._monitor_tabs.add_tab("安全提示", self._build_alert_tab())

        layout.addWidget(header)
        layout.addWidget(mini_row)
        layout.addWidget(self._monitor_tabs, 1)
        return panel

    def _build_execution_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        tip = QLabel("执行表格展示每轮点赞动作的账号、目标、节奏与结果。", host)
        _call(tip, "setObjectName", "sectionCaption")
        self._execution_table = DataTable(EXECUTION_TABLE_HEADERS, [], page_size=6, empty_text="暂无执行记录", parent=host)
        self._execution_status_badge = StatusBadge("执行明细就绪", "brand", host)
        layout.addWidget(tip)
        layout.addWidget(self._execution_status_badge)
        layout.addWidget(self._execution_table, 1)
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
        self._log_status_hint = QLabel("异常降速、规则执行与批量操作都会实时落入日志流。", status_panel)
        _call(self._log_status_hint, "setObjectName", "sectionCaption")
        _call(self._log_status_hint, "setWordWrap", True)
        status_layout.addWidget(self._log_status_badge)
        status_layout.addWidget(self._log_status_value)
        status_layout.addWidget(self._log_status_hint, 1)
        self._log_viewer = RealtimeLogViewer(host)
        _call(self._log_viewer, "setMinimumHeight", 320)
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
        panel._value_label = value_label  # type: ignore[attr-defined]
        panel._caption_label = caption_label  # type: ignore[attr-defined]
        panel._kicker_label = kicker_label  # type: ignore[attr-defined]
        return panel

    def _bind_interactions(self) -> None:
        """绑定交互事件。"""

        _connect(getattr(self._refresh_button, "clicked", None), self._refresh_all_views)
        _connect(getattr(self._new_rule_button, "clicked", None), self._on_create_rule)
        _connect(getattr(self._clone_button, "clicked", None), self._on_clone_rule)
        _connect(getattr(self._batch_button, "clicked", None), self._append_batch_hint_log)
        _connect(getattr(self._console_toggle, "toggled", None), self._on_console_toggled)
        _connect(getattr(self._rule_search, "search_changed", None), self._apply_filters)
        _connect(getattr(self._status_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._content_type_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._account_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._execution_table, "row_selected", None), self._on_execution_row_selected)
        _connect(getattr(self._rule_editor, "rule_changed", None), self._sync_editor_preview)
        _connect(getattr(self._insert_delay_button, "clicked", None), self._insert_delay_template)
        _connect(getattr(self._reset_button, "clicked", None), self._on_reset_editor)
        _connect(getattr(self._run_button, "clicked", None), self._on_run_rule)
        _connect(getattr(self._save_button, "clicked", None), self._on_save_rule)

        for key in ("name", "frequency", "time_window", "daily_limit", "rate_limit", "random_delay"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedLineEdit):
                _connect(getattr(widget.line_edit, "textChanged", None), self._sync_editor_preview)
        for key in ("account_group", "content_type", "target_scope", "behavior_mode"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedComboBox):
                _connect(getattr(widget.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        for key in ("hashtags", "target_users"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, TagInput):
                _connect(getattr(widget, "tags_changed", None), self._sync_editor_preview)
        notes_widget = self._editor_widgets.get("notes")
        if isinstance(notes_widget, ThemedTextEdit):
            _connect(getattr(notes_widget.text_edit, "textChanged", None), self._sync_editor_preview)
        enabled_widget = self._editor_widgets.get("enabled")
        if isinstance(enabled_widget, ToggleSwitch):
            _connect(getattr(enabled_widget, "toggled", None), self._sync_editor_preview)

    def _refresh_all_views(self, *_args: object) -> None:
        """刷新页面所有视图。"""

        self._apply_filters()
        self._populate_log_viewer()
        self._refresh_kpis()
        self._refresh_sidebar_summary()
        self._refresh_monitor_panels()
        self._refresh_alert_cards()
        self._load_selected_rule_to_editor()
        self._sync_editor_preview()

    def _apply_filters(self, *_args: object) -> None:
        query = self._rule_search.text().strip().lower()
        status_text = self._status_filter.current_text() if isinstance(self._status_filter, ThemedComboBox) else "全部状态"
        content_type = self._content_type_filter.current_text() if isinstance(self._content_type_filter, ThemedComboBox) else "全部类型"
        account_filter = self._account_filter.current_text() if isinstance(self._account_filter, ThemedComboBox) else "全部账号池"

        filtered: list[dict[str, Any]] = []
        for rule in self._rules:
            haystack = " ".join(
                [
                    str(rule.get("name", "")),
                    str(rule.get("account_group", "")),
                    str(rule.get("target_scope", "")),
                    " ".join(str(item) for item in rule.get("hashtags", [])),
                    " ".join(str(item) for item in rule.get("target_users", [])),
                ]
            ).lower()
            if query and query not in haystack:
                continue
            if status_text == "仅看已开启" and not bool(rule.get("enabled", False)):
                continue
            if status_text == "仅看已关闭" and bool(rule.get("enabled", False)):
                continue
            if content_type not in ("", "全部类型") and str(rule.get("content_type", "")) != content_type:
                continue
            if account_filter not in ("", "全部账号池") and account_filter not in (str(rule.get("account_group", "")), str(rule.get("account", ""))):
                continue
            filtered.append(rule)

        self._filtered_rules = filtered
        if self._selected_rule_id and not any(str(rule.get("id", "")) == self._selected_rule_id for rule in self._filtered_rules):
            self._selected_rule_id = str(self._filtered_rules[0].get("id", "")) if self._filtered_rules else ""
        self._refresh_rule_cards()
        self._refresh_rule_table()
        self._refresh_execution_records()

    def _refresh_kpis(self) -> None:
        enabled_rules = [rule for rule in self._rules if bool(rule.get("enabled", False))]
        total_tasks = sum(int(str(rule.get("today_tasks", "0")).replace(",", "")) for rule in self._rules)
        total_success = sum(int(str(rule.get("today_success", "0")).replace(",", "")) for rule in self._rules)
        success_rate = (total_success / total_tasks * 100.0) if total_tasks else 0.0
        values = [f"{total_success:,}", f"{success_rate:.1f}%", str(len(enabled_rules)), str(len(self._rules))]
        captions = [
            f"今日累计完成 {total_success:,} 次有效点赞，过滤后的重复内容已自动跳过。",
            "安全缓冲与账号轮转共同提升了执行稳定性。",
            f"当前有 {len(enabled_rules)} 个活跃规则参与执行。",
            f"规则总数 {len(self._rules)}，其中高仿真人模式占比较高。",
        ]
        for index, card in enumerate(self._kpi_cards):
            card.set_value(values[index])
            _call(card._caption_label, "setText", captions[index])  # type: ignore[attr-defined]

    def _refresh_sidebar_summary(self) -> None:
        enabled_count = sum(1 for rule in self._rules if bool(rule.get("enabled", False)))
        disabled_count = len(self._rules) - enabled_count
        visible_count = len(self._filtered_rules)
        _call(self._console_summary_label, "setText", f"当前启用 {enabled_count} 条规则，{disabled_count} 条处于待机状态")
        self._coverage_badge.setText(f"筛选后展示 {visible_count} 条规则")
        if self._page_enabled:
            self._system_badge.setText("执行中")
            self._system_badge.set_tone("success")
        else:
            self._system_badge.setText("已暂停")
            self._system_badge.set_tone("warning")
        self._set_mini_panel_content(self._sidebar_summary, "当前重点", "标签扩量 + 内容复扫", f"可见规则 {visible_count} 条，建议优先关注高热视频与商品卡预热。")

    def _refresh_monitor_panels(self) -> None:
        risk_count = sum(1 for item in self._execution_records if item.get("status") in ("失败", "降速"))
        queue_estimate = sum(max(int(str(rule.get("daily_limit", "0")).split()[0].replace(",", "")) // 2, 0) for rule in self._rules[:4])
        self._set_mini_panel_content(self._live_panel, "当前轮速", "12 次 / 5 分钟", "当前执行节奏落在保守安全区间")
        self._set_mini_panel_content(self._risk_panel, "风控提醒", f"{risk_count} 条", "检测到降速与失败记录，建议复核设备环境")
        self._set_mini_panel_content(self._queue_panel, "待执行池", f"{queue_estimate} 条内容", "标签池、达人池与商品卡池都在持续补充")

    def _set_mini_panel_content(self, panel: QWidget, kicker: str, value: str, caption: str) -> None:
        kicker_label = getattr(panel, "_kicker_label", None)
        value_label = getattr(panel, "_value_label", None)
        caption_label = getattr(panel, "_caption_label", None)
        if kicker_label is not None:
            _call(kicker_label, "setText", kicker)
        if value_label is not None:
            _call(value_label, "setText", value)
        if caption_label is not None:
            _call(caption_label, "setText", caption)

    def _refresh_rule_cards(self) -> None:
        _clear_layout(self._rule_cards_layout)
        self._rule_card_widgets.clear()
        if not self._filtered_rules:
            empty = QLabel("没有匹配到点赞规则，请调整筛选条件。", self._rule_cards_host)
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
        is_selected = str(rule.get("id", "")) == self._selected_rule_id
        _call(
            card,
            "setStyleSheet",
            f"QFrame#ruleCard {{ background-color: {_rgba(colors.primary, 0.06) if is_selected else colors.surface}; border: 1px solid {colors.primary if is_selected else colors.border}; border-radius: {RADIUS_LG}px; }}",
        )
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

        line1 = QLabel(f"账号池：{rule.get('account_group', '')} · 类型：{rule.get('content_type', '')}", card)
        _call(line1, "setObjectName", "summaryLabel")
        line2 = QLabel(f"目标：{' / '.join(str(item) for item in rule.get('hashtags', [])[:3])}", card)
        _call(line2, "setObjectName", "summaryValue")
        line3 = QLabel(f"频率：{rule.get('frequency', '')} · 日限额：{rule.get('daily_limit', '')}", card)
        _call(line3, "setObjectName", "summaryLabel")

        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(SPACING_MD)
        for text in (f"成功率 {rule.get('success_rate', '--')}", f"风险 {rule.get('risk_level', '--')}", f"最近 {rule.get('last_run', '--')}"):
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
        toggle_label = QLabel("启停", card)
        _call(toggle_label, "setObjectName", "summaryLabel")
        toggle = ToggleSwitch(bool(rule.get("enabled", False)))
        bottom.addWidget(select_button)
        bottom.addStretch(1)
        bottom.addWidget(toggle_label)
        bottom.addWidget(toggle)

        _connect(getattr(name_button, "clicked", None), lambda rid=str(rule.get("id", "")): self._select_rule(rid))
        _connect(getattr(select_button, "clicked", None), lambda rid=str(rule.get("id", "")): self._select_rule(rid))
        _connect(getattr(toggle, "toggled", None), lambda checked, rid=str(rule.get("id", "")): self._set_rule_enabled(rid, checked))

        layout.addLayout(top)
        layout.addWidget(line1)
        layout.addWidget(line2)
        layout.addWidget(line3)
        layout.addLayout(chips)
        layout.addLayout(bottom)
        self._rule_card_widgets.append({"id": str(rule.get("id", "")), "toggle": toggle, "badge": badge, "card": card})
        return card

    def _refresh_rule_table(self) -> None:
        if not hasattr(self, "_rule_table"):
            self._rule_table = DataTable(RULE_TABLE_HEADERS, [], page_size=5, empty_text="暂无规则数据", parent=self)
        self._rule_table.set_rows([_rule_table_row(rule) for rule in self._filtered_rules])

    def _refresh_execution_records(self) -> None:
        query = self._rule_search.text().strip().lower()
        current_rule = self._selected_rule()
        target_terms = []
        if current_rule is not None:
            target_terms = [str(item).lower() for item in current_rule.get("hashtags", [])[:2]]
        records: list[dict[str, str]] = []
        for item in self._execution_records:
            haystack = " ".join(item.values()).lower()
            if query and query not in haystack:
                continue
            if target_terms and not any(term in haystack for term in target_terms):
                if self._selected_rule_id:
                    continue
            records.append(item)
        self._filtered_execution_records = records or list(self._execution_records[:6])
        self._execution_table.set_rows([_execution_table_row(item) for item in self._filtered_execution_records])
        self._selected_execution_index = 0 if self._filtered_execution_records else -1
        if self._filtered_execution_records:
            self._execution_table.select_absolute_row(0)
            first = self._filtered_execution_records[0]
            self._execution_status_badge.setText(f"当前明细：{first['status']} · {first['account']}")
        else:
            self._execution_status_badge.setText("执行明细为空")

    def _refresh_alert_cards(self) -> None:
        _clear_layout(self._alert_cards_layout)
        alerts: list[tuple[str, str, BadgeTone]] = [
            ("账号轮转提醒", "建议将高频点赞账号每 45 分钟切换一次，避免连续暴露。", "warning"),
            ("重复目标提醒", "本日已有 3 个目标账号被重复命中，建议扩大标签池。", "brand"),
            ("节奏优化提醒", "图文类型的随机延迟建议保持在 15-30 秒，避免节奏过于紧密。", "info"),
            ("环境安全提醒", "北美测试号近 1 小时内有 1 次接口超时，可临时切换为保守模式。", "warning"),
            ("内容库存提醒", "#极简书桌 标签新增内容偏少，建议补充相关备用标签。", "neutral"),
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
            badge = StatusBadge("监控提示", tone, card)
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
        for item in AUTO_LIKE_LOGS:
            self._log_viewer.append_log(item["level"], item["message"], item["time"])
        if hasattr(self, "_log_status_badge"):
            latest = AUTO_LIKE_LOGS[0] if AUTO_LIKE_LOGS else {"level": "无", "time": "--"}
            self._log_status_badge.setText(f"日志 {len(AUTO_LIKE_LOGS)} 条")
            _call(self._log_status_value, "setText", f"最新 {latest['level']} · {latest['time']}")

    def _selected_rule(self) -> dict[str, Any] | None:
        for rule in self._rules:
            if str(rule.get("id", "")) == self._selected_rule_id:
                return rule
        return self._rules[0] if self._rules else None

    def _select_rule(self, rule_id: str) -> None:
        self._selected_rule_id = rule_id
        self._refresh_rule_cards()
        self._refresh_execution_records()
        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已切换到点赞规则【{rule.get('name', '')}】。")

    def _load_selected_rule_to_editor(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        self._selected_rule_badge.setText(f"当前规则：{rule.get('name', '')}")
        self._selected_rule_badge.set_tone("brand" if bool(rule.get("enabled", False)) else "neutral")
        for key in ("risk_level", "today_tasks", "success_rate", "last_run"):
            label = self._summary_labels.get(key)
            if label is not None:
                _call(label, "setText", str(rule.get(key, "--")))

        mapping = {
            "name": rule.get("name", ""),
            "frequency": rule.get("frequency", ""),
            "time_window": rule.get("time_window", ""),
            "daily_limit": rule.get("daily_limit", ""),
            "rate_limit": rule.get("rate_limit", ""),
            "random_delay": rule.get("random_delay", ""),
        }
        for key, value in mapping.items():
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedLineEdit):
                widget.setText(str(value))
        for key in ("account_group", "content_type", "target_scope", "behavior_mode"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedComboBox):
                _call(widget.combo_box, "setCurrentText", str(rule.get(key, "")))
        for key in ("hashtags", "target_users"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, TagInput):
                widget.set_tags([str(item) for item in rule.get(key, [])])
        notes = self._editor_widgets.get("notes")
        if isinstance(notes, ThemedTextEdit):
            notes.setPlainText("\n".join(str(item) for item in rule.get("notes", [])))
        enabled = self._editor_widgets.get("enabled")
        if isinstance(enabled, ToggleSwitch):
            enabled.setChecked(bool(rule.get("enabled", False)))
        self._rule_editor.set_rule({"logic": "AND", "conditions": rule.get("conditions", []), "action": rule.get("action", {})})

    def _collect_editor_state(self) -> dict[str, Any]:
        rule = self._selected_rule()
        current_id = str(rule.get("id", "")) if rule is not None else ""
        state: dict[str, Any] = {
            "id": current_id,
            "name": self._read_line_edit("name"),
            "account_group": self._read_combo_box("account_group"),
            "content_type": self._read_combo_box("content_type"),
            "target_scope": self._read_combo_box("target_scope"),
            "hashtags": self._read_tags("hashtags"),
            "target_users": self._read_tags("target_users"),
            "frequency": self._read_line_edit("frequency"),
            "time_window": self._read_line_edit("time_window"),
            "daily_limit": self._read_line_edit("daily_limit"),
            "rate_limit": self._read_line_edit("rate_limit"),
            "random_delay": self._read_line_edit("random_delay"),
            "behavior_mode": self._read_combo_box("behavior_mode"),
            "enabled": self._read_toggle("enabled"),
            "notes": [line for line in self._read_text_edit("notes").splitlines() if line.strip()],
            "conditions": self._rule_editor.get_rule().get("conditions", []),
            "action": self._rule_editor.get_rule().get("action", {}),
        }
        if rule is not None:
            for key in ("account", "today_tasks", "today_success", "success_rate", "last_run", "risk_level"):
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

    def _read_toggle(self, key: str) -> bool:
        widget = self._editor_widgets.get(key)
        return bool(widget.isChecked()) if isinstance(widget, ToggleSwitch) else False

    def _sync_editor_preview(self, *_args: object) -> None:
        state = self._collect_editor_state()
        hashtags = "、".join(str(item) for item in state.get("hashtags", [])[:4]) or "暂无标签"
        users = "、".join(str(item) for item in state.get("target_users", [])[:3]) or "暂无目标账号"
        conditions = self._rule_editor.get_rule().get("conditions", [])
        self._preview_summary.setText(
            f"规则【{state.get('name', '') or '未命名规则'}】将使用【{state.get('account_group', '') or '未选择账号池'}】执行，"
            f"聚焦【{state.get('content_type', '') or '未设置内容类型'}】内容，目标范围为【{state.get('target_scope', '') or '未设置范围'}】。"
        )
        self._preview_hint.setText(
            f"标签：{hashtags}\n目标账号：{users}\n频率：{state.get('frequency', '') or '未填写'} · 时间窗：{state.get('time_window', '') or '未填写'} · 日上限：{state.get('daily_limit', '') or '未填写'}\n"
            f"随机延迟：{state.get('random_delay', '') or '未填写'} · 行为模式：{state.get('behavior_mode', '') or '未设置'} · 条件数：{len(conditions) if isinstance(conditions, list) else 0} 条"
        )
        if hasattr(self, "_execution_status_badge"):
            _call(
                self._execution_status_badge,
                "setText",
                f"执行明细：{state.get('content_type', '') or '未设置类型'} · {state.get('behavior_mode', '') or '未设置模式'}",
            )

    def _set_rule_enabled(self, rule_id: str, enabled: bool) -> None:
        for rule in self._rules:
            if str(rule.get("id", "")) == rule_id:
                rule["enabled"] = enabled
                self._append_operation_log(f"点赞规则【{rule.get('name', '')}】已{('开启' if enabled else '关闭')}。")
                break
        self._refresh_all_views()

    def _on_console_toggled(self, checked: bool) -> None:
        self._page_enabled = checked
        self._append_operation_log("自动点赞总开关已开启。" if checked else "自动点赞总开关已关闭，当前仅保留监控与日志。")
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
        self._append_operation_log(f"规则【{state.get('name', '') or '未命名规则'}】已保存。")
        self._refresh_all_views()

    def _on_reset_editor(self) -> None:
        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已恢复规则【{rule.get('name', '')}】的原始配置。")

    def _on_clone_rule(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        cloned = _copy_rule(rule)
        cloned["id"] = f"{rule.get('id', 'rule')}-copy-{len(self._rules) + 1}"
        cloned["name"] = f"{rule.get('name', '')}（副本）"
        cloned["today_tasks"] = "0"
        cloned["today_success"] = "0"
        cloned["success_rate"] = "--"
        cloned["last_run"] = "尚未执行"
        self._rules.insert(0, cloned)
        self._selected_rule_id = str(cloned.get("id", ""))
        self._append_operation_log(f"已复制点赞规则【{rule.get('name', '')}】。")
        self._refresh_all_views()

    def _on_create_rule(self) -> None:
        new_rule = {
            "id": f"like-rule-new-{len(self._rules) + 1}",
            "name": "新建点赞规则",
            "account_group": "品牌主号 A 组",
            "account": "品牌主号 A 组",
            "content_type": "短视频",
            "hashtags": ["#示例标签"],
            "target_users": ["@example_target"],
            "target_scope": "标签优先",
            "frequency": "每 20 分钟一轮",
            "time_window": "10:00-20:00",
            "daily_limit": "100",
            "rate_limit": "每账号每小时 12 次",
            "random_delay": "12-24 秒",
            "behavior_mode": "平衡模式",
            "enabled": True,
            "today_tasks": "0",
            "today_success": "0",
            "success_rate": "--",
            "last_run": "尚未执行",
            "risk_level": "低风险",
            "notes": ["建议先用少量内容池做试探。"],
            "conditions": [{"field": "点赞量", "operator": "大于", "value": "100"}],
            "action": {"type": "执行任务", "value": "执行点赞并观察风控"},
        }
        self._rules.insert(0, new_rule)
        self._selected_rule_id = str(new_rule["id"])
        self._append_operation_log("已创建新的自动点赞规则草稿。")
        self._refresh_all_views()

    def _on_run_rule(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        new_record = {
            "time": "15:08:00",
            "account": str(rule.get("account_group", "品牌主号 A 组")),
            "target": " / ".join(str(item) for item in rule.get("hashtags", [])[:2]) or "示例目标",
            "content_type": str(rule.get("content_type", "短视频")),
            "status": "成功",
            "tempo": str(rule.get("random_delay", "12-20 秒")),
            "result": "手动触发完成一轮点赞预演",
        }
        self._execution_records.insert(0, new_record)
        rule["last_run"] = "15:08"
        rule["today_tasks"] = str(int(str(rule.get("today_tasks", "0")).replace(",", "")) + 1)
        self._append_operation_log(f"已手动触发规则【{rule.get('name', '')}】执行一轮。")
        self._refresh_all_views()

    def _on_execution_row_selected(self, row_index: int) -> None:
        if not (0 <= row_index < len(self._filtered_execution_records)):
            return
        self._selected_execution_index = row_index
        item = self._filtered_execution_records[row_index]
        tone: BadgeTone = "success"
        if item["status"] == "失败":
            tone = "error"
        elif item["status"] in ("降速", "跳过"):
            tone = "warning"
        self._execution_status_badge.setText(f"{item['status']} · {item['account']}")
        self._execution_status_badge.set_tone(tone)

    def _insert_delay_template(self) -> None:
        widget = self._editor_widgets.get("notes")
        if not isinstance(widget, ThemedTextEdit):
            return
        current = widget.toPlainText().rstrip()
        addition = "\n建议延迟模版：首轮 12-18 秒，第二轮 20-28 秒，异常时插入 120-180 秒缓冲。"
        widget.setPlainText((current + addition).strip())
        self._append_operation_log("已插入安全延迟建议。")

    def _append_batch_hint_log(self) -> None:
        self._append_operation_log("可继续扩展批量启停、批量换号池、批量调低节奏等高级操作。")

    def _append_operation_log(self, message: str) -> None:
        self._log_viewer.append_log("操作", message, "2026-03-09 15:10:00")

    def on_activated(self) -> None:
        self._refresh_all_views()

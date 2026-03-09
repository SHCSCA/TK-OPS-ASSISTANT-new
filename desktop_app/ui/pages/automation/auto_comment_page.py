# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""自动评论原型页面。"""

from typing import Any

from ....core.qt import QFrame as CoreQFrame, QHBoxLayout as CoreQHBoxLayout, QLabel as CoreQLabel, QPushButton as CoreQPushButton, QVBoxLayout as CoreQVBoxLayout, QWidget as CoreQWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
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
    "目标来源",
    "评论模式",
    "频率",
    "黑名单保护",
    "今日评论",
    "成功率",
    "状态",
]

TEMPLATE_TABLE_HEADERS = ["模板内容", "分类", "使用次数", "最近命中", "状态"]
HISTORY_TABLE_HEADERS = ["时间", "账号", "目标", "评论内容", "情感倾向", "状态", "说明"]

STATISTICS_CARDS: list[dict[str, Any]] = [
    {"title": "今日评论量", "value": "1,946", "trend": "up", "percentage": "+14.2%", "caption": "热门标签池带动评论任务明显增长", "sparkline": [120, 136, 158, 186, 224, 268, 301]},
    {"title": "成功率", "value": "88.9%", "trend": "up", "percentage": "+2.7%", "caption": "模板去重和黑名单过滤降低了失败率", "sparkline": [79, 81, 83, 84, 86, 88, 89]},
    {"title": "回复率", "value": "21.4%", "trend": "up", "percentage": "+1.8%", "caption": "问答型评论更容易激发对方二次互动", "sparkline": [12, 14, 15, 17, 18, 20, 21]},
    {"title": "活跃账号", "value": "14", "trend": "flat", "percentage": "+0.0%", "caption": "评论账号轮转稳定，未额外扩容账号池", "sparkline": [14, 14, 14, 14, 14, 14, 14]},
]

AUTO_COMMENT_LOGS: list[dict[str, str]] = [
    {"level": "成功", "time": "2026-03-09 15:18:12", "message": "规则【竞对粉丝种草切入】已生成 18 条差异化评论，重复率控制在 6% 以内。"},
    {"level": "预警", "time": "2026-03-09 15:14:47", "message": "模板【氛围夸赞型】近 20 分钟使用频次偏高，系统建议切换模板组。"},
    {"level": "成功", "time": "2026-03-09 15:09:31", "message": "AI 评论增强已为 #底妆教程 任务生成问答型评论 9 条，语气统一为轻推荐风。"},
    {"level": "忽略", "time": "2026-03-09 15:03:56", "message": "评论内容命中黑名单词【最便宜】，系统已自动拦截并改写。"},
    {"level": "成功", "time": "2026-03-09 14:58:08", "message": "账号 @commentlab_04 在竞对粉丝池中完成 24 条评论投放，回复率达到 26%。"},
    {"level": "成功", "time": "2026-03-09 14:52:40", "message": "近期发帖人规则已完成一轮复扫，对新发布视频插入轻互动评论。"},
    {"level": "预警", "time": "2026-03-09 14:47:19", "message": "账号 @beautynote_09 连续命中同一作者 3 条内容，系统已加入作者去重限制。"},
    {"level": "成功", "time": "2026-03-09 14:41:03", "message": "模板库已自动提升【提问带购买意向】模板优先级，用于高互动视频评论。"},
    {"level": "忽略", "time": "2026-03-09 14:33:26", "message": "用户 @no_contact_list 被加入评论黑名单，后续任务已自动跳过。"},
    {"level": "成功", "time": "2026-03-09 14:25:12", "message": "规则【近期发帖人热帖切入】首轮评论完成，情感倾向主要为积极。"},
    {"level": "预警", "time": "2026-03-09 14:18:57", "message": "AI 配置温度值偏高，可能导致语气飘逸，建议保持在 0.6-0.8 区间。"},
    {"level": "成功", "time": "2026-03-09 14:11:34", "message": "黑名单词库已更新 5 条营销敏感词，后续评论将自动规避。"},
]

COMMENT_TEMPLATES: list[dict[str, str]] = [
    {"text": "这个思路太实用了，尤其是前半段那个细节，一下就记住了。", "category": "细节夸赞", "usage": "126", "last_hit": "15:12", "status": "启用中"},
    {"text": "这个搭配思路很妙，想问下你更推荐哪一种日常场景去用？", "category": "提问互动", "usage": "98", "last_hit": "14:58", "status": "启用中"},
    {"text": "我也是最近在看这类内容，这条讲得特别清楚，收藏了。", "category": "同感种草", "usage": "84", "last_hit": "14:43", "status": "启用中"},
    {"text": "这种展示方式很容易让人看懂，尤其适合第一次了解的人。", "category": "清晰表达", "usage": "63", "last_hit": "14:36", "status": "启用中"},
    {"text": "这个对比做得很直观，想继续看你下一条延展内容。", "category": "期待追更", "usage": "71", "last_hit": "14:24", "status": "启用中"},
    {"text": "这个氛围真的很舒服，看完会想立刻试一下。", "category": "氛围夸赞", "usage": "117", "last_hit": "15:14", "status": "高频"},
    {"text": "原来还能这样组合，之前完全没想到这个用法。", "category": "惊喜发现", "usage": "52", "last_hit": "14:10", "status": "启用中"},
    {"text": "这条内容节奏拿捏得很好，看到最后完全不想划走。", "category": "内容节奏", "usage": "45", "last_hit": "13:55", "status": "启用中"},
    {"text": "这个角度很有说服力，比单纯展示更容易让人记住。", "category": "观点认可", "usage": "39", "last_hit": "13:48", "status": "启用中"},
    {"text": "想问一下如果是新手，先从哪一步开始会更顺一些？", "category": "新手提问", "usage": "88", "last_hit": "14:51", "status": "启用中"},
    {"text": "这个讲法很自然，不会有那种硬推的感觉。", "category": "自然安利", "usage": "61", "last_hit": "14:08", "status": "启用中"},
    {"text": "先暂停这组模板，等下一波内容方向再重新启用。", "category": "待机模板", "usage": "12", "last_hit": "昨日", "status": "已暂停"},
]

EXECUTION_HISTORY: list[dict[str, str]] = [
    {"time": "15:16", "account": "@commentlab_04", "target": "#底妆教程", "comment": "这个思路真的很适合新手入门，步骤一下就看明白了。", "sentiment": "积极", "status": "成功", "note": "30 分钟内收到 3 条回复"},
    {"time": "15:09", "account": "@beautynote_09", "target": "竞对粉丝 @glowmakeup", "comment": "想问下这种妆感日常通勤会不会也很自然？", "sentiment": "中性", "status": "成功", "note": "提问型评论触发二次互动"},
    {"time": "15:02", "account": "@homecomment_02", "target": "近期发帖人 @roomreset", "comment": "这条内容的空间感展示特别舒服，收藏了。", "sentiment": "积极", "status": "成功", "note": "收藏型语气稳定"},
    {"time": "14:56", "account": "@fitreply_03", "target": "#居家健身", "comment": "这个动作讲得很清楚，新手看了也不容易踩坑。", "sentiment": "积极", "status": "成功", "note": "评论已被作者点赞"},
    {"time": "14:50", "account": "@commentlab_07", "target": "竞对粉丝 @trendcatch", "comment": "这个搭配感太强了，想问下你更常用哪套组合？", "sentiment": "中性", "status": "成功", "note": "互动质量较高"},
    {"time": "14:42", "account": "@homecomment_06", "target": "#阳台改造", "comment": "这个氛围感太舒服了，看完真的想动手改一下角落。", "sentiment": "积极", "status": "成功", "note": "命中氛围夸赞模板"},
    {"time": "14:37", "account": "@beautynote_03", "target": "近期发帖人 @skinfile", "comment": "这种讲法挺自然的，不会有那种很硬的感觉。", "sentiment": "积极", "status": "成功", "note": "作者已回复感谢"},
    {"time": "14:31", "account": "@fitreply_06", "target": "#跑步装备", "comment": "这条评论涉及敏感对比词，已被系统改写后发送。", "sentiment": "中性", "status": "改写", "note": "触发黑名单词保护"},
    {"time": "14:24", "account": "@commentlab_02", "target": "竞对粉丝 @streetpick", "comment": "这个展示逻辑真挺清晰的，一下就能明白重点。", "sentiment": "积极", "status": "成功", "note": "稳定输出"},
    {"time": "14:19", "account": "@homecomment_03", "target": "#极简书桌", "comment": "这个桌面布局太会了，细节收纳真的加分。", "sentiment": "积极", "status": "成功", "note": "内容风格匹配良好"},
    {"time": "14:13", "account": "@commentlab_08", "target": "#新品开箱", "comment": "这个对比点很有记忆点，后面那段讲解也很顺。", "sentiment": "积极", "status": "成功", "note": "无异常"},
    {"time": "14:05", "account": "@beautynote_10", "target": "近期发帖人 @softskinlab", "comment": "原来还能这样拆解，之前真没注意到这个角度。", "sentiment": "积极", "status": "失败", "note": "接口返回超时，待补跑"},
]

DEMO_RULES: list[dict[str, Any]] = [
    {"id": "comment-rule-01", "name": "竞对粉丝种草切入", "source": "竞对粉丝", "comment_mode": "模板 + AI 改写", "frequency": "每 15 分钟一轮", "blacklist": "词库 + 用户双保护", "today_comments": "86", "today_success": "78", "success_rate": "90.7%", "enabled": True, "last_run": "15:16", "reply_rate": "28.4%", "account_group": "美妆矩阵号", "hashtags": ["#底妆教程", "#平价底妆"], "competitors": ["@glowmakeup", "@softskinlab"], "recent_posters": ["@beautyminute", "@skinfile"], "black_words": ["最便宜", "包过", "绝对有效"], "black_users": ["@no_contact_list", "@blocked_sample"], "template": "这个思路讲得挺清楚的，尤其是前半段那个细节，真的很容易让人记住。", "notes": ["优先评论高互动视频。", "提问型语气更适合竞对粉丝场景。"], "conditions": [{"field": "近 2 小时互动量", "operator": "大于", "value": "300"}, {"field": "评论区情绪", "operator": "不等于", "value": "争议高"}], "action": {"type": "执行任务", "value": "输出提问型评论"}},
    {"id": "comment-rule-02", "name": "近期发帖人热帖切入", "source": "近期发帖人", "comment_mode": "纯模板", "frequency": "每 18 分钟一轮", "blacklist": "词库保护", "today_comments": "61", "today_success": "55", "success_rate": "90.2%", "enabled": True, "last_run": "15:02", "reply_rate": "18.8%", "account_group": "家居矩阵号", "hashtags": ["#收纳灵感", "#阳台改造"], "competitors": ["@roomreset"], "recent_posters": ["@greenhome", "@deskframe"], "black_words": ["秒杀", "最低价"], "black_users": ["@spam_case_1"], "template": "这个展示方式特别舒服，关键点一眼就能看懂。", "notes": ["重点评论新发内容。"], "conditions": [{"field": "发布时间", "operator": "小于", "value": "120 分钟"}], "action": {"type": "执行任务", "value": "输出夸赞型评论"}},
    {"id": "comment-rule-03", "name": "标签问答型互动", "source": "标签", "comment_mode": "AI 生成", "frequency": "每 12 分钟一轮", "blacklist": "词库 + 用户双保护", "today_comments": "74", "today_success": "63", "success_rate": "85.1%", "enabled": True, "last_run": "15:09", "reply_rate": "24.6%", "account_group": "品牌主号 A 组", "hashtags": ["#通勤穿搭", "#好物分享"], "competitors": ["@trendcatch"], "recent_posters": ["@urbancloset"], "black_words": ["必买", "稳赚"], "black_users": ["@blocked_demo"], "template": "想问一下这个思路如果放在日常场景里，你最推荐哪一种用法？", "notes": ["问答型内容更适合主账号。"], "conditions": [{"field": "点赞量", "operator": "大于", "value": "500"}], "action": {"type": "执行任务", "value": "AI 生成问答型评论"}},
    {"id": "comment-rule-04", "name": "竞对粉丝轻夸赞", "source": "竞对粉丝", "comment_mode": "纯模板", "frequency": "每 20 分钟一轮", "blacklist": "用户保护", "today_comments": "33", "today_success": "31", "success_rate": "93.9%", "enabled": True, "last_run": "14:50", "reply_rate": "16.2%", "account_group": "鞋包矩阵号", "hashtags": ["#通勤球鞋", "#包包分享"], "competitors": ["@streetpick", "@urbanbagclub"], "recent_posters": ["@bagshow"], "black_words": ["加 V", "私聊"], "black_users": ["@shoe_blocked"], "template": "这个搭配逻辑很顺，看完会想继续刷下一条。", "notes": ["轻夸赞适合避免营销感。"], "conditions": [{"field": "评论量", "operator": "大于", "value": "15"}], "action": {"type": "执行任务", "value": "轻夸赞评论"}},
    {"id": "comment-rule-05", "name": "家居氛围感评论", "source": "标签", "comment_mode": "模板 + AI 改写", "frequency": "每 16 分钟一轮", "blacklist": "词库保护", "today_comments": "42", "today_success": "37", "success_rate": "88.1%", "enabled": True, "last_run": "14:42", "reply_rate": "19.4%", "account_group": "家居矩阵号", "hashtags": ["#极简书桌", "#阳台改造"], "competitors": ["@workmood"], "recent_posters": ["@balconystory"], "black_words": ["立刻买", "冲冲冲"], "black_users": ["@negative_sample"], "template": "这个氛围感真的太舒服了，看完会想立刻整理自己的空间。", "notes": ["氛围型评论要避免过度夸张。"], "conditions": [{"field": "收藏量", "operator": "大于", "value": "60"}], "action": {"type": "执行任务", "value": "氛围感评论"}},
    {"id": "comment-rule-06", "name": "健身干货提问回路", "source": "近期发帖人", "comment_mode": "AI 生成", "frequency": "每 22 分钟一轮", "blacklist": "词库 + 用户双保护", "today_comments": "28", "today_success": "24", "success_rate": "85.7%", "enabled": False, "last_run": "14:31", "reply_rate": "22.0%", "account_group": "北美测试号", "hashtags": ["#居家健身", "#跑步装备"], "competitors": ["@trainwithme"], "recent_posters": ["@runnerpick"], "black_words": ["治愈", "保证瘦"], "black_users": ["@usa_blocked"], "template": "这种拆解方式挺适合新手，想问下最建议先练哪一步？", "notes": ["当前暂停，等待新的英文模板库。"], "conditions": [{"field": "地区", "operator": "等于", "value": "北美"}], "action": {"type": "暂停任务", "value": "等待英文模板补充"}},
    {"id": "comment-rule-07", "name": "新品开箱追更互动", "source": "近期发帖人", "comment_mode": "纯模板", "frequency": "每 24 分钟一轮", "blacklist": "词库保护", "today_comments": "19", "today_success": "18", "success_rate": "94.7%", "enabled": True, "last_run": "14:13", "reply_rate": "17.0%", "account_group": "达人合作号", "hashtags": ["#新品开箱", "#本周上新"], "competitors": ["@firstlooklab"], "recent_posters": ["@buyersclub"], "black_words": ["全网最低"], "black_users": ["@cooperate_blocked"], "template": "这个对比点真的很有记忆点，想继续看你下一条延展内容。", "notes": ["合作内容以追更型评论为主。"], "conditions": [{"field": "发布时间", "operator": "小于", "value": "90 分钟"}], "action": {"type": "执行任务", "value": "追更型评论"}},
    {"id": "comment-rule-08", "name": "平价护肤自然认可", "source": "标签", "comment_mode": "模板 + AI 改写", "frequency": "每 14 分钟一轮", "blacklist": "词库 + 用户双保护", "today_comments": "57", "today_success": "51", "success_rate": "89.5%", "enabled": True, "last_run": "14:37", "reply_rate": "20.1%", "account_group": "美妆矩阵号", "hashtags": ["#平价护肤", "#护肤分享"], "competitors": ["@skinfile"], "recent_posters": ["@beautyclean"], "black_words": ["神药", "必囤"], "black_users": ["@lowtrust_demo"], "template": "这种讲法挺自然的，不会有那种很硬的感觉。", "notes": ["自然认可语气更适合长线种草。"], "conditions": [{"field": "点赞量", "operator": "大于", "value": "400"}], "action": {"type": "执行任务", "value": "自然认可评论"}},
    {"id": "comment-rule-09", "name": "好物分享提问转化", "source": "竞对粉丝", "comment_mode": "AI 生成", "frequency": "每 17 分钟一轮", "blacklist": "词库保护", "today_comments": "36", "today_success": "30", "success_rate": "83.3%", "enabled": True, "last_run": "14:24", "reply_rate": "25.4%", "account_group": "品牌主号 B 组", "hashtags": ["#好物分享", "#办公室好物"], "competitors": ["@dailycup"], "recent_posters": ["@deskdrink"], "black_words": ["包你满意", "绝不后悔"], "black_users": ["@office_blocked"], "template": "想问一下如果是办公室日常使用，你觉得哪个点最打动人？", "notes": ["提问评论优先落在高收藏内容。"], "conditions": [{"field": "收藏量", "operator": "大于", "value": "100"}], "action": {"type": "执行任务", "value": "提问型转化评论"}},
    {"id": "comment-rule-10", "name": "小户型灵感评论池", "source": "近期发帖人", "comment_mode": "纯模板", "frequency": "每 19 分钟一轮", "blacklist": "用户保护", "today_comments": "27", "today_success": "25", "success_rate": "92.6%", "enabled": False, "last_run": "13:59", "reply_rate": "14.1%", "account_group": "家居矩阵号", "hashtags": ["#小户型灵感", "#家居布置"], "competitors": ["@calmspace_cn"], "recent_posters": ["@greenhome"], "black_words": ["便宜到哭"], "black_users": ["@mini_home_blocked"], "template": "这个角度真的很有启发，看完会想把自己的空间重新调整一下。", "notes": ["当前等待新模板补充。"], "conditions": [{"field": "评论量", "operator": "大于", "value": "8"}], "action": {"type": "暂停任务", "value": "模板不足暂缓"}},
    {"id": "comment-rule-11", "name": "鞋包穿搭清晰表达", "source": "标签", "comment_mode": "纯模板", "frequency": "每 21 分钟一轮", "blacklist": "词库保护", "today_comments": "22", "today_success": "20", "success_rate": "90.9%", "enabled": True, "last_run": "13:42", "reply_rate": "15.3%", "account_group": "鞋包矩阵号", "hashtags": ["#今日包包", "#穿搭细节"], "competitors": ["@urbanbagclub"], "recent_posters": ["@bagshow"], "black_words": ["私发链接"], "black_users": ["@bag_ban"], "template": "这个表达方式很清楚，一下就知道重点想传达什么。", "notes": ["适合偏理性内容。"], "conditions": [{"field": "播放量", "operator": "大于", "value": "3000"}], "action": {"type": "执行任务", "value": "清晰表达型评论"}},
    {"id": "comment-rule-12", "name": "运动装备英文试探", "source": "竞对粉丝", "comment_mode": "AI 生成", "frequency": "每 30 分钟一轮", "blacklist": "词库 + 用户双保护", "today_comments": "11", "today_success": "9", "success_rate": "81.8%", "enabled": False, "last_run": "13:18", "reply_rate": "12.0%", "account_group": "北美测试号", "hashtags": ["#runnerkit", "#traininggear"], "competitors": ["@gearfit"], "recent_posters": ["@fitcoachnow"], "black_words": ["free gift", "guaranteed"], "black_users": ["@runnerban"], "template": "这条讲解很清楚，就算是第一次接触这类装备的人也能快速看懂重点。", "notes": ["英文模板库仍在补充中。"], "conditions": [{"field": "地区", "operator": "等于", "value": "北美"}], "action": {"type": "暂停任务", "value": "等待英文模板优化"}},
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
        str(rule.get("source", "")),
        str(rule.get("comment_mode", "")),
        str(rule.get("frequency", "")),
        str(rule.get("blacklist", "")),
        str(rule.get("today_comments", "0")),
        str(rule.get("success_rate", "--")),
        _toggle_text(bool(rule.get("enabled", False))),
    ]


def _template_table_row(item: dict[str, str]) -> list[object]:
    return [item["text"], item["category"], item["usage"], item["last_hit"], item["status"]]


def _history_table_row(item: dict[str, str]) -> list[object]:
    return [item["time"], item["account"], item["target"], item["comment"], item["sentiment"], item["status"], item["note"]]


class AutoCommentPage(BasePage):
    """自动评论页面。"""

    default_route_id = RouteId("auto_comment")
    default_display_name = "自动评论"
    default_icon_name = "chat_bubble"

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
        self._templates: list[dict[str, str]] = [item.copy() for item in COMMENT_TEMPLATES]
        self._filtered_templates: list[dict[str, str]] = list(self._templates)
        self._history: list[dict[str, str]] = [item.copy() for item in EXECUTION_HISTORY]
        self._filtered_history: list[dict[str, str]] = list(self._history)
        self._selected_rule_id: str = str(self._rules[0]["id"]) if self._rules else ""
        self._selected_template_index: int = 0
        self._kpi_cards: list[KPICard] = []
        self._editor_widgets: dict[str, object] = {}
        super().__init__(route_id=route_id, display_name=display_name, icon_name=icon_name, parent=parent)

    def setup_ui(self) -> None:
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        root = QWidget(self)
        _call(root, "setObjectName", "autoCommentRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.layout.addWidget(root)

        self._refresh_button = IconButton("↻", "刷新自动评论状态", self)
        self._new_rule_button = PrimaryButton("新增评论规则", self, icon_text="＋")
        container = PageContainer(
            title="自动评论",
            description="用模板库、AI 生成、黑名单与情感监控组合出更自然的评论互动工作流。",
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
            QWidget#autoCommentRoot {{
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
        title = QLabel("启用评论自动互动引擎", left)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("系统会根据目标来源、模板库、AI 语气配置与黑名单策略自动输出评论，并监控情感反馈。", left)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        badges = QHBoxLayout()
        badges.setContentsMargins(0, 0, 0, 0)
        badges.setSpacing(SPACING_MD)
        self._system_badge = StatusBadge("评论运行中", "success", left)
        self._template_badge = StatusBadge("模板库 12 条", "brand", left)
        self._blacklist_badge = StatusBadge("黑名单保护开启", "warning", left)
        badges.addWidget(self._system_badge)
        badges.addWidget(self._template_badge)
        badges.addWidget(self._blacklist_badge)
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
        self._console_summary_label = QLabel("当前启用 9 条评论规则，3 条待机", right)
        _call(self._console_summary_label, "setObjectName", "summaryValue")
        tip = QLabel("推荐把高频模板与 AI 生成模式错峰使用，降低内容重复感。", right)
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
        title = QLabel("评论规则列表", header)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("按目标来源、规则状态和搜索关键字快速定位要调整的评论策略。", header)
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
        filter_hint = QLabel("先锁定来源、模式和状态，再进入中间区域编辑模板、黑名单与 AI 参数。", filter_panel)
        _call(filter_hint, "setObjectName", "sectionCaption")
        _call(filter_hint, "setWordWrap", True)
        filter_layout.addWidget(filter_title)
        filter_layout.addWidget(filter_hint)
        self._rule_search = SearchBar("搜索规则、标签、竞对或模板")
        self._source_filter = ThemedComboBox("目标来源", ["全部来源", "标签", "竞对粉丝", "近期发帖人"])
        self._status_filter = ThemedComboBox("状态筛选", ["全部状态", "仅看已开启", "仅看已关闭"])
        self._mode_filter = ThemedComboBox("评论模式", ["全部模式", "纯模板", "模板 + AI 改写", "AI 生成"])
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(SPACING_MD)
        self._clone_button = PrimaryButton("复制规则", panel, icon_text="⎘")
        self._tips_button = IconButton("⋯", "评论批量操作提示", panel)
        actions.addWidget(self._clone_button, 1)
        actions.addWidget(self._tips_button)
        self._rule_cards_host = QWidget(panel)
        self._rule_cards_layout = QVBoxLayout(self._rule_cards_host)
        self._rule_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._rule_cards_layout.setSpacing(SPACING_MD)
        self._sidebar_summary = self._build_mini_panel("当前重点", "提问型评论 + 黑名单保护", "评论主力集中在竞对粉丝和近期发帖人场景。")
        filter_layout.addWidget(self._rule_search)
        filter_layout.addWidget(self._source_filter)
        filter_layout.addWidget(self._status_filter)
        filter_layout.addWidget(self._mode_filter)
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
        title = QLabel("评论配置", text_host)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("配置目标规则、模板库、AI 参数与黑名单，生成更自然的自动评论。", text_host)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        text_layout.addWidget(title)
        text_layout.addWidget(caption)
        self._selected_rule_badge = StatusBadge("当前规则：竞对粉丝种草切入", "brand", header)
        header_layout.addWidget(text_host, 1)
        header_layout.addWidget(self._selected_rule_badge)

        summary = QFrame(panel)
        _call(summary, "setObjectName", "summaryStrip")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(SPACING_LG, SPACING_MD, SPACING_LG, SPACING_MD)
        summary_layout.setSpacing(SPACING_XL)
        self._summary_labels: dict[str, QLabel] = {}
        for label_text, key in (("回复率", "reply_rate"), ("今日评论", "today_comments"), ("成功率", "success_rate"), ("最近执行", "last_run")):
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

        basic = ContentSection("目标规则", "◎", parent=panel)
        row1 = QWidget(basic)
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(SPACING_XL)
        self._editor_widgets["name"] = ThemedLineEdit("规则名称", "请输入评论规则名称", "建议按目标来源 + 语气命名")
        self._editor_widgets["source"] = ThemedComboBox("目标来源", ["标签", "竞对粉丝", "近期发帖人"])
        self._editor_widgets["comment_mode"] = ThemedComboBox("评论模式", ["纯模板", "模板 + AI 改写", "AI 生成"])
        self._editor_widgets["account_group"] = ThemedComboBox("账号池", ["品牌主号 A 组", "品牌主号 B 组", "家居矩阵号", "美妆矩阵号", "鞋包矩阵号", "北美测试号", "达人合作号"])
        row1_layout.addWidget(self._editor_widgets["name"], 2)
        row1_layout.addWidget(self._editor_widgets["source"], 1)
        row1_layout.addWidget(self._editor_widgets["comment_mode"], 1)
        row1_layout.addWidget(self._editor_widgets["account_group"], 1)
        basic.add_widget(row1)
        self._editor_widgets["hashtags"] = TagInput("标签规则", "输入目标标签后回车确认")
        self._editor_widgets["competitors"] = TagInput("竞对账号", "输入竞对账号后回车确认")
        self._editor_widgets["recent_posters"] = TagInput("近期发帖人", "输入近期发帖账号后回车确认")
        basic.add_widget(self._editor_widgets["hashtags"])
        basic.add_widget(self._editor_widgets["competitors"])
        basic.add_widget(self._editor_widgets["recent_posters"])

        template = ContentSection("评论模板与黑名单", "✦", parent=panel)
        self._editor_widgets["template"] = ThemedTextEdit("默认评论模板", "填写默认评论模板，用于模板模式或 AI 改写的基础文案")
        template.add_widget(self._editor_widgets["template"])
        row2 = QWidget(template)
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(SPACING_XL)
        self._editor_widgets["black_words"] = TagInput("黑名单词", "输入需要规避的词语")
        self._editor_widgets["black_users"] = TagInput("黑名单用户", "输入需要跳过的用户")
        row2_layout.addWidget(self._editor_widgets["black_words"], 1)
        row2_layout.addWidget(self._editor_widgets["black_users"], 1)
        template.add_widget(row2)

        schedule = ContentSection("节奏与 AI 配置", "◴", parent=panel)
        row3 = QWidget(schedule)
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(SPACING_XL)
        self._editor_widgets["frequency"] = ThemedLineEdit("评论频率", "如：每 15 分钟一轮", "提问型评论建议错峰执行")
        self._editor_widgets["enabled"] = ToggleSwitch(True)
        toggle_host = QWidget(row3)
        toggle_layout = QVBoxLayout(toggle_host)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(SPACING_SM)
        toggle_layout.addWidget(QLabel("启用规则", toggle_host))
        toggle_layout.addWidget(self._editor_widgets["enabled"])
        toggle_layout.addStretch(1)
        row3_layout.addWidget(self._editor_widgets["frequency"], 1)
        row3_layout.addWidget(toggle_host)
        schedule.add_widget(row3)
        self._ai_panel = AIConfigPanel(schedule)
        schedule.add_widget(self._ai_panel)

        logic = ContentSection("评论逻辑编排", "⌁", parent=panel)
        self._rule_editor = RuleEditorWidget(panel)
        logic.add_widget(self._rule_editor)

        preview = QFrame(panel)
        _call(preview, "setObjectName", "previewPanel")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        preview_layout.setSpacing(SPACING_SM)
        preview_title = QLabel("评论预览", preview)
        _call(preview_title, "setObjectName", "sectionTitle")
        self._preview_summary = QLabel("当前规则将优先对竞对粉丝池的高互动内容发起评论。", preview)
        _call(self._preview_summary, "setObjectName", "bodyText")
        _call(self._preview_summary, "setWordWrap", True)
        self._preview_hint = QLabel("预览会根据模板、AI 配置和黑名单动态更新。", preview)
        _call(self._preview_hint, "setObjectName", "summaryLabel")
        _call(self._preview_hint, "setWordWrap", True)
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self._preview_summary)
        preview_layout.addWidget(self._preview_hint)

        footer = QWidget(panel)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(SPACING_MD)
        self._insert_template_button = QPushButton("插入问答型模板", footer)
        _call(self._insert_template_button, "setObjectName", "ghostChip")
        self._reset_button = QPushButton("恢复当前规则", footer)
        _call(self._reset_button, "setObjectName", "ghostChip")
        self._run_button = PrimaryButton("立即评论一轮", footer, icon_text="▶")
        self._save_button = PrimaryButton("保存规则", footer, icon_text="✓")
        footer_layout.addWidget(self._insert_template_button)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self._reset_button)
        footer_layout.addWidget(self._run_button)
        footer_layout.addWidget(self._save_button)

        layout.addWidget(header)
        layout.addWidget(summary)
        layout.addWidget(basic)
        layout.addWidget(template)
        layout.addWidget(schedule)
        layout.addWidget(logic)
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
        title = QLabel("评论监控", panel)
        _call(title, "setObjectName", "sectionTitle")
        caption = QLabel("从模板库、执行历史、实时日志和情感提示四个维度观察评论自动化表现。", panel)
        _call(caption, "setObjectName", "sectionCaption")
        _call(caption, "setWordWrap", True)
        mini_row = QWidget(panel)
        mini_layout = QHBoxLayout(mini_row)
        mini_layout.setContentsMargins(0, 0, 0, 0)
        mini_layout.setSpacing(SPACING_MD)
        self._sentiment_panel = self._build_mini_panel("情感倾向", "积极为主", "多数评论落在自然认可与提问互动风格")
        self._reply_panel = self._build_mini_panel("最近回复", "14 条", "问答型评论更容易收到回应")
        self._blacklist_panel = self._build_mini_panel("黑名单拦截", "7 次", "主要拦截敏感促销词与指定用户")
        mini_layout.addWidget(self._sentiment_panel, 1)
        mini_layout.addWidget(self._reply_panel, 1)
        mini_layout.addWidget(self._blacklist_panel, 1)
        self._monitor_tabs = TabBar(panel)
        self._monitor_tabs.add_tab("模板库", self._build_template_tab())
        self._monitor_tabs.add_tab("执行历史", self._build_history_tab())
        self._monitor_tabs.add_tab("实时日志", self._build_log_tab())
        self._monitor_tabs.add_tab("风控提示", self._build_alert_tab())
        layout.addWidget(title)
        layout.addWidget(caption)
        layout.addWidget(mini_row)
        layout.addWidget(self._monitor_tabs, 1)
        return panel

    def _build_template_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        self._template_search = SearchBar("搜索模板内容或分类")
        self._template_table = DataTable(TEMPLATE_TABLE_HEADERS, [], page_size=5, empty_text="暂无模板", parent=host)
        self._template_preview_badge = StatusBadge("模板预览就绪", "brand", host)
        layout.addWidget(self._template_search)
        layout.addWidget(self._template_preview_badge)
        layout.addWidget(self._template_table, 1)
        return host

    def _build_history_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)
        self._history_table = DataTable(HISTORY_TABLE_HEADERS, [], page_size=6, empty_text="暂无执行历史", parent=host)
        self._history_status_badge = StatusBadge("历史明细就绪", "brand", host)
        layout.addWidget(self._history_status_badge)
        layout.addWidget(self._history_table, 1)
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
        self._log_status_hint = QLabel("模板拦截、AI 改写与批量保存操作都会同步写入评论日志。", status_panel)
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
        _connect(getattr(self._source_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._status_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._mode_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(getattr(self._template_search, "search_changed", None), self._refresh_template_table)
        _connect(getattr(self._template_table, "row_selected", None), self._on_template_selected)
        _connect(getattr(self._history_table, "row_selected", None), self._on_history_selected)
        _connect(getattr(self._insert_template_button, "clicked", None), self._insert_question_template)
        _connect(getattr(self._reset_button, "clicked", None), self._on_reset_editor)
        _connect(getattr(self._run_button, "clicked", None), self._on_run_rule)
        _connect(getattr(self._save_button, "clicked", None), self._on_save_rule)
        _connect(getattr(self._rule_editor, "rule_changed", None), self._sync_editor_preview)
        _connect(getattr(self._ai_panel, "config_changed", None), self._sync_editor_preview)

        for key in ("name", "frequency"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedLineEdit):
                _connect(getattr(widget.line_edit, "textChanged", None), self._sync_editor_preview)
        for key in ("source", "comment_mode", "account_group"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedComboBox):
                _connect(getattr(widget.combo_box, "currentTextChanged", None), self._sync_editor_preview)
        for key in ("hashtags", "competitors", "recent_posters", "black_words", "black_users"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, TagInput):
                _connect(getattr(widget, "tags_changed", None), self._sync_editor_preview)
        template_widget = self._editor_widgets.get("template")
        if isinstance(template_widget, ThemedTextEdit):
            _connect(getattr(template_widget.text_edit, "textChanged", None), self._sync_editor_preview)
        enabled_widget = self._editor_widgets.get("enabled")
        if isinstance(enabled_widget, ToggleSwitch):
            _connect(getattr(enabled_widget, "toggled", None), self._sync_editor_preview)

    def _refresh_all_views(self, *_args: object) -> None:
        self._apply_filters()
        self._populate_log_viewer()
        self._refresh_kpis()
        self._refresh_sidebar_summary()
        self._refresh_monitor_panels()
        self._refresh_template_table()
        self._refresh_history_table()
        self._refresh_alert_cards()
        self._load_selected_rule_to_editor()
        self._sync_editor_preview()

    def _apply_filters(self, *_args: object) -> None:
        query = self._rule_search.text().strip().lower()
        source = self._source_filter.current_text() if isinstance(self._source_filter, ThemedComboBox) else "全部来源"
        status = self._status_filter.current_text() if isinstance(self._status_filter, ThemedComboBox) else "全部状态"
        mode = self._mode_filter.current_text() if isinstance(self._mode_filter, ThemedComboBox) else "全部模式"
        filtered: list[dict[str, Any]] = []
        for rule in self._rules:
            haystack = " ".join(
                [
                    str(rule.get("name", "")),
                    str(rule.get("source", "")),
                    str(rule.get("comment_mode", "")),
                    " ".join(str(item) for item in rule.get("hashtags", [])),
                    " ".join(str(item) for item in rule.get("competitors", [])),
                    " ".join(str(item) for item in rule.get("recent_posters", [])),
                ]
            ).lower()
            if query and query not in haystack:
                continue
            if source not in ("", "全部来源") and str(rule.get("source", "")) != source:
                continue
            if mode not in ("", "全部模式") and str(rule.get("comment_mode", "")) != mode:
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
        total_comments = sum(int(str(rule.get("today_comments", "0")).replace(",", "")) for rule in self._rules)
        total_success = sum(int(str(rule.get("today_success", "0")).replace(",", "")) for rule in self._rules)
        success_rate = (total_success / total_comments * 100.0) if total_comments else 0.0
        reply_values: list[float] = []
        for rule in self._rules:
            raw = str(rule.get("reply_rate", "0")).replace("%", "")
            try:
                reply_values.append(float(raw))
            except ValueError:
                continue
        avg_reply = sum(reply_values) / len(reply_values) if reply_values else 0.0
        values = [f"{total_comments:,}", f"{success_rate:.1f}%", f"{avg_reply:.1f}%", str(sum(1 for rule in self._rules if bool(rule.get('enabled', False))))]
        captions = [
            f"今日共投放 {total_comments:,} 条评论，模板与 AI 混合模式持续工作。",
            f"成功发送 {total_success:,} 条，黑名单保护减少了异常输出。",
            "提问型评论仍是拉动回复率的主要手段。",
            "活跃账号主要集中在美妆、家居和品牌主号场景。",
        ]
        for index, card in enumerate(self._kpi_cards):
            card.set_value(values[index])
            _call(card._caption_label, "setText", captions[index])  # type: ignore[attr-defined]

    def _refresh_sidebar_summary(self) -> None:
        enabled_count = sum(1 for rule in self._rules if bool(rule.get("enabled", False)))
        disabled_count = len(self._rules) - enabled_count
        visible_count = len(self._filtered_rules)
        _call(self._console_summary_label, "setText", f"当前启用 {enabled_count} 条评论规则，{disabled_count} 条待机")
        self._template_badge.setText(f"模板库 {len(self._templates)} 条")
        if self._page_enabled:
            self._system_badge.setText("评论运行中")
            self._system_badge.set_tone("success")
        else:
            self._system_badge.setText("评论已暂停")
            self._system_badge.set_tone("warning")
        self._set_mini_panel_content(self._sidebar_summary, "当前重点", "提问型评论 + 黑名单保护", f"当前筛选后可见 {visible_count} 条规则。")

    def _refresh_monitor_panels(self) -> None:
        positive_count = sum(1 for item in self._history if item.get("sentiment") == "积极")
        reply_like = sum(1 for item in self._history if "回复" in item.get("note", ""))
        blocked = sum(1 for item in AUTO_COMMENT_LOGS if item.get("level") == "忽略")
        self._set_mini_panel_content(self._sentiment_panel, "情感倾向", f"积极 {positive_count} 条", "大多数评论都维持在自然、正向的表达上")
        self._set_mini_panel_content(self._reply_panel, "最近回复", f"{reply_like} 条", "提问型评论对回复率提升更明显")
        self._set_mini_panel_content(self._blacklist_panel, "黑名单拦截", f"{blocked} 次", "敏感词和用户黑名单正在有效工作")

    def _set_mini_panel_content(self, panel: QWidget, kicker: str, value: str, caption: str) -> None:
        _call(getattr(panel, "_kicker_label", None), "setText", kicker)
        _call(getattr(panel, "_value_label", None), "setText", value)
        _call(getattr(panel, "_caption_label", None), "setText", caption)

    def _refresh_rule_cards(self) -> None:
        _clear_layout(self._rule_cards_layout)
        if not self._filtered_rules:
            empty = QLabel("没有匹配到评论规则，请尝试修改筛选条件。", self._rule_cards_host)
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
        line1 = QLabel(f"来源：{rule.get('source', '')} · 模式：{rule.get('comment_mode', '')}", card)
        _call(line1, "setObjectName", "summaryLabel")
        line2 = QLabel(f"标签：{' / '.join(str(item) for item in rule.get('hashtags', [])[:2])}", card)
        _call(line2, "setObjectName", "summaryValue")
        line3 = QLabel(f"频率：{rule.get('frequency', '')} · 回复率：{rule.get('reply_rate', '--')}", card)
        _call(line3, "setObjectName", "summaryLabel")
        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(SPACING_MD)
        for text in (f"今日 {rule.get('today_comments', '0')}", f"成功率 {rule.get('success_rate', '--')}", f"保护 {rule.get('blacklist', '')}"):
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
        layout.addWidget(line3)
        layout.addLayout(chips)
        layout.addLayout(bottom)
        return card

    def _refresh_rule_table(self) -> None:
        if not hasattr(self, "_rule_table"):
            self._rule_table = DataTable(RULE_TABLE_HEADERS, [], page_size=5, empty_text="暂无规则数据", parent=self)
        self._rule_table.set_rows([_rule_table_row(rule) for rule in self._filtered_rules])

    def _refresh_template_table(self, *_args: object) -> None:
        query = self._template_search.text().strip().lower() if hasattr(self, "_template_search") else ""
        filtered = []
        for item in self._templates:
            haystack = " ".join(item.values()).lower()
            if query and query not in haystack:
                continue
            filtered.append(item)
        self._filtered_templates = filtered
        self._template_table.set_rows([_template_table_row(item) for item in self._filtered_templates])
        if self._filtered_templates:
            self._template_table.select_absolute_row(0)
            self._template_preview_badge.setText(f"模板预览：{self._filtered_templates[0]['category']}")
        else:
            self._template_preview_badge.setText("模板预览为空")

    def _refresh_history_table(self) -> None:
        current_rule = self._selected_rule()
        query_terms = [str(item).lower() for item in current_rule.get("hashtags", [])[:1]] if current_rule is not None else []
        filtered = []
        for item in self._history:
            haystack = " ".join(item.values()).lower()
            if query_terms and not any(term in haystack for term in query_terms):
                continue
            filtered.append(item)
        self._filtered_history = filtered or list(self._history[:8])
        self._history_table.set_rows([_history_table_row(item) for item in self._filtered_history])
        if self._filtered_history:
            self._history_table.select_absolute_row(0)
            self._history_status_badge.setText(f"历史明细：{self._filtered_history[0]['status']} · {self._filtered_history[0]['sentiment']}")

    def _refresh_alert_cards(self) -> None:
        _clear_layout(self._alert_cards_layout)
        alerts: list[tuple[str, str, BadgeTone]] = [
            ("模板重复提醒", "高频模板建议每 30 分钟切换一次，以减少评论内容的相似度。", "warning"),
            ("黑名单词提醒", "敏感促销词建议持续扩充，尤其是绝对化承诺与价格刺激词。", "brand"),
            ("情感平衡提醒", "过多夸赞型评论会降低真实性，建议混入提问和同感型语气。", "info"),
            ("AI 生成提醒", "温度保持在 0.6-0.8 可兼顾自然度与稳定性。", "warning"),
            ("作者去重提醒", "同一作者建议 6 小时内最多评论 1 次，避免过度暴露。", "neutral"),
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
        for item in AUTO_COMMENT_LOGS:
            self._log_viewer.append_log(item["level"], item["message"], item["time"])
        if hasattr(self, "_log_status_badge"):
            latest = AUTO_COMMENT_LOGS[0] if AUTO_COMMENT_LOGS else {"level": "无", "time": "--"}
            self._log_status_badge.setText(f"日志 {len(AUTO_COMMENT_LOGS)} 条")
            _call(self._log_status_value, "setText", f"最新 {latest['level']} · {latest['time']}")

    def _selected_rule(self) -> dict[str, Any] | None:
        for rule in self._rules:
            if str(rule.get("id", "")) == self._selected_rule_id:
                return rule
        return self._rules[0] if self._rules else None

    def _select_rule(self, rule_id: str) -> None:
        self._selected_rule_id = rule_id
        self._refresh_rule_cards()
        self._refresh_history_table()
        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已切换到评论规则【{rule.get('name', '')}】。")

    def _load_selected_rule_to_editor(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        self._selected_rule_badge.setText(f"当前规则：{rule.get('name', '')}")
        self._selected_rule_badge.set_tone("brand" if bool(rule.get("enabled", False)) else "neutral")
        for key in ("reply_rate", "today_comments", "success_rate", "last_run"):
            label = self._summary_labels.get(key)
            if label is not None:
                _call(label, "setText", str(rule.get(key, "--")))
        line_mapping = {"name": rule.get("name", ""), "frequency": rule.get("frequency", "")}
        for key, value in line_mapping.items():
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedLineEdit):
                widget.setText(str(value))
        for key in ("source", "comment_mode", "account_group"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, ThemedComboBox):
                _call(widget.combo_box, "setCurrentText", str(rule.get(key, "")))
        for key in ("hashtags", "competitors", "recent_posters", "black_words", "black_users"):
            widget = self._editor_widgets.get(key)
            if isinstance(widget, TagInput):
                widget.set_tags([str(item) for item in rule.get(key, [])])
        template_widget = self._editor_widgets.get("template")
        if isinstance(template_widget, ThemedTextEdit):
            template_widget.setPlainText(str(rule.get("template", "")))
        enabled_widget = self._editor_widgets.get("enabled")
        if isinstance(enabled_widget, ToggleSwitch):
            enabled_widget.setChecked(bool(rule.get("enabled", False)))
        self._rule_editor.set_rule({"logic": "AND", "conditions": rule.get("conditions", []), "action": rule.get("action", {})})
        self._ai_panel.set_config({"provider": "openai", "model": "gpt-4o-mini", "agent_role": "文案专家", "temperature": 0.7, "max_tokens": 1024, "top_p": 0.9})

    def _collect_editor_state(self) -> dict[str, Any]:
        rule = self._selected_rule()
        state: dict[str, Any] = {
            "id": str(rule.get("id", "")) if rule is not None else "",
            "name": self._read_line_edit("name"),
            "source": self._read_combo_box("source"),
            "comment_mode": self._read_combo_box("comment_mode"),
            "account_group": self._read_combo_box("account_group"),
            "hashtags": self._read_tags("hashtags"),
            "competitors": self._read_tags("competitors"),
            "recent_posters": self._read_tags("recent_posters"),
            "black_words": self._read_tags("black_words"),
            "black_users": self._read_tags("black_users"),
            "template": self._read_text_edit("template"),
            "frequency": self._read_line_edit("frequency"),
            "enabled": self._read_toggle("enabled"),
            "conditions": self._rule_editor.get_rule().get("conditions", []),
            "action": self._rule_editor.get_rule().get("action", {}),
            "ai_config": self._ai_panel.config(),
        }
        if rule is not None:
            for key in ("blacklist", "today_comments", "today_success", "success_rate", "last_run", "reply_rate"):
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
        ai_config = state.get("ai_config", {})
        provider = ai_config.get("provider_label", ai_config.get("provider", "未设置")) if isinstance(ai_config, dict) else "未设置"
        model = ai_config.get("model", "未设置") if isinstance(ai_config, dict) else "未设置"
        self._preview_summary.setText(
            f"规则【{state.get('name', '') or '未命名规则'}】会从【{state.get('source', '') or '未设置来源'}】抓取目标，使用【{state.get('comment_mode', '') or '未设置模式'}】输出评论。"
        )
        self._preview_hint.setText(
            f"标签：{'、'.join(str(item) for item in state.get('hashtags', [])[:3]) or '暂无'}\n"
            f"竞对：{'、'.join(str(item) for item in state.get('competitors', [])[:2]) or '暂无'}\n"
            f"近期发帖人：{'、'.join(str(item) for item in state.get('recent_posters', [])[:2]) or '暂无'}\n"
            f"黑名单词：{'、'.join(str(item) for item in state.get('black_words', [])[:3]) or '暂无'}\n"
            f"AI：{provider} / {model} · 频率：{state.get('frequency', '') or '未填写'}"
        )
        if hasattr(self, "_history_status_badge"):
            _call(
                self._history_status_badge,
                "setText",
                f"历史明细：{state.get('comment_mode', '') or '未设置模式'} · {state.get('source', '') or '未设置来源'}",
            )

    def _set_rule_enabled(self, rule_id: str, enabled: bool) -> None:
        for rule in self._rules:
            if str(rule.get("id", "")) == rule_id:
                rule["enabled"] = enabled
                self._append_operation_log(f"评论规则【{rule.get('name', '')}】已{('开启' if enabled else '关闭')}。")
                break
        self._refresh_all_views()

    def _on_console_toggled(self, checked: bool) -> None:
        self._page_enabled = checked
        self._append_operation_log("自动评论总开关已开启。" if checked else "自动评论总开关已关闭，仅保留监控。")
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
        self._append_operation_log(f"评论规则【{state.get('name', '') or '未命名规则'}】已保存。")
        self._refresh_all_views()

    def _on_reset_editor(self) -> None:
        self._load_selected_rule_to_editor()
        rule = self._selected_rule()
        if rule is not None:
            self._append_operation_log(f"已恢复评论规则【{rule.get('name', '')}】。")

    def _on_clone_rule(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        cloned = _copy_rule(rule)
        cloned["id"] = f"{rule.get('id', 'rule')}-copy-{len(self._rules) + 1}"
        cloned["name"] = f"{rule.get('name', '')}（副本）"
        cloned["today_comments"] = "0"
        cloned["today_success"] = "0"
        cloned["success_rate"] = "--"
        cloned["last_run"] = "尚未执行"
        self._rules.insert(0, cloned)
        self._selected_rule_id = str(cloned.get("id", ""))
        self._append_operation_log(f"已复制评论规则【{rule.get('name', '')}】。")
        self._refresh_all_views()

    def _on_create_rule(self) -> None:
        new_rule = {
            "id": f"comment-rule-new-{len(self._rules) + 1}",
            "name": "新建评论规则",
            "source": "标签",
            "comment_mode": "纯模板",
            "frequency": "每 20 分钟一轮",
            "blacklist": "词库保护",
            "today_comments": "0",
            "today_success": "0",
            "success_rate": "--",
            "enabled": True,
            "last_run": "尚未执行",
            "reply_rate": "--",
            "account_group": "品牌主号 A 组",
            "hashtags": ["#示例标签"],
            "competitors": ["@example_competitor"],
            "recent_posters": ["@example_author"],
            "black_words": ["示例敏感词"],
            "black_users": ["@example_blocked"],
            "template": "这个表达方式挺自然的，尤其是前面的细节特别容易让人记住。",
            "notes": ["建议先用模板模式试跑。"],
            "conditions": [{"field": "点赞量", "operator": "大于", "value": "100"}],
            "action": {"type": "执行任务", "value": "输出基础评论"},
        }
        self._rules.insert(0, new_rule)
        self._selected_rule_id = str(new_rule["id"])
        self._append_operation_log("已创建新的评论规则草稿。")
        self._refresh_all_views()

    def _on_run_rule(self) -> None:
        rule = self._selected_rule()
        if rule is None:
            return
        comment_text = self._read_text_edit("template") or str(rule.get("template", ""))
        self._history.insert(0, {"time": "15:22", "account": str(rule.get("account_group", "品牌主号 A 组")), "target": str(rule.get("source", "标签")), "comment": comment_text[:42], "sentiment": "积极", "status": "成功", "note": "手动触发评论预演"})
        rule["last_run"] = "15:22"
        rule["today_comments"] = str(int(str(rule.get("today_comments", "0")).replace(",", "")) + 1)
        self._append_operation_log(f"已手动触发规则【{rule.get('name', '')}】执行一轮评论。")
        self._refresh_all_views()

    def _on_template_selected(self, row_index: int) -> None:
        if not (0 <= row_index < len(self._filtered_templates)):
            return
        self._selected_template_index = row_index
        item = self._filtered_templates[row_index]
        self._template_preview_badge.setText(f"模板预览：{item['category']} · 使用 {item['usage']} 次")

    def _on_history_selected(self, row_index: int) -> None:
        if not (0 <= row_index < len(self._filtered_history)):
            return
        item = self._filtered_history[row_index]
        tone: BadgeTone = "success"
        if item["status"] == "失败":
            tone = "error"
        elif item["status"] == "改写":
            tone = "warning"
        self._history_status_badge.setText(f"{item['status']} · {item['sentiment']} · {item['account']}")
        self._history_status_badge.set_tone(tone)

    def _insert_question_template(self) -> None:
        widget = self._editor_widgets.get("template")
        if not isinstance(widget, ThemedTextEdit):
            return
        widget.setPlainText("这个思路真的挺清楚的，想问下如果是第一次尝试，你更建议先从哪一步开始？")
        self._append_operation_log("已插入问答型模板。")

    def _append_batch_hint_log(self) -> None:
        self._append_operation_log("可继续扩展批量切换模板组、批量更新黑名单、批量调整 AI 语气。")

    def _append_operation_log(self, message: str) -> None:
        self._log_viewer.append_log("操作", message, "2026-03-09 15:24:00")

    def on_activated(self) -> None:
        self._refresh_all_views()

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""脚本生成页面。"""

from dataclasses import dataclass
from typing import Any, Sequence

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
    AIConfigPanel,
    ContentSection,
    DataTable,
    FloatingActionButton,
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
from ...components.layouts import label_text_style, panel_frame_style, rgba_color
from ...components.tags import BadgeTone
from ...components.inputs import (
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_2XL,
    RADIUS_MD,
    RADIUS_LG,
    BUTTON_HEIGHT,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


DESKTOP_PAGE_MAX_WIDTH = 1920


@dataclass(frozen=True)
class ScriptTypeProfile:
    """脚本类型配置。"""

    name: str
    icon: str
    rhythm: str
    hook: str
    structure: str
    recommended_duration: str
    ideal_tone: str
    keywords: tuple[str, ...]
    tips: tuple[str, ...]
    scene: str


@dataclass(frozen=True)
class ScriptTemplate:
    """脚本模板数据。"""

    script_type: str
    title: str
    opening_hook: str
    structure_label: str
    estimated_duration: str
    quality_score: str
    adoption_hint: str
    tone: str
    summary: str
    script_text: str
    selling_points: tuple[str, ...]
    cta: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class HistoryRecord:
    """历史记录。"""

    created_at: str
    product_name: str
    script_type: str
    duration: str
    quality_score: str
    status: str
    author: str
    note: str


@dataclass(frozen=True)
class StrategyNote:
    """策略建议。"""

    title: str
    detail: str
    highlight: str
    tone: str


@dataclass(frozen=True)
class KeywordPulse:
    """热点词趋势。"""

    keyword: str
    heat: str
    direction: str
    tone: str


SCRIPT_TYPES: tuple[ScriptTypeProfile, ...] = (
    ScriptTypeProfile(
        name="种草脚本",
        icon="✦",
        rhythm="情绪代入 + 场景铺垫 + 使用反馈",
        hook="从真实困扰切入，让用户像听朋友分享一样进入内容。",
        structure="开场共鸣 → 痛点拆解 → 卖点示范 → 使用感受 → 轻推 CTA",
        recommended_duration="25-40 秒",
        ideal_tone="真实自然",
        keywords=("被问爆了", "真的会回购", "通勤党", "建议收藏"),
        tips=(
            "前三句必须出现使用场景与用户身份词。",
            "避免上来堆参数，先让人产生代入。",
            "结尾更适合用‘先收藏’而不是强下单。",
        ),
        scene="适合生活方式、家居、个护、服饰类内容。",
    ),
    ScriptTypeProfile(
        name="开箱测评",
        icon="◈",
        rhythm="开箱惊喜 + 核心观察 + 结果结论",
        hook="通过第一眼包装、细节做工和对比体验建立信任感。",
        structure="开箱第一眼 → 细节特写 → 上手测试 → 优缺点总结 → 购买建议",
        recommended_duration="30-45 秒",
        ideal_tone="专业克制",
        keywords=("实测", "别盲买", "细节控", "对比看"),
        tips=(
            "优先展示包装、材质、手感等高感知信息。",
            "测评类脚本一定要有结论句。",
            "可加入‘适合谁 / 不适合谁’提升可信度。",
        ),
        scene="适合数码、家居、收纳、小家电类内容。",
    ),
    ScriptTypeProfile(
        name="教程讲解",
        icon="◎",
        rhythm="结论前置 + 步骤拆解 + 复盘提醒",
        hook="先告诉用户学会后能得到什么，再给具体步骤。",
        structure="结果承诺 → 步骤一 → 步骤二 → 步骤三 → 复盘提示",
        recommended_duration="35-55 秒",
        ideal_tone="清晰直接",
        keywords=("三步学会", "照着做", "新手友好", "少踩坑"),
        tips=(
            "每个步骤只讲一个动作，不要并列太多信息。",
            "加入时长、顺序、参数这类确定性表达。",
            "最后补一条‘最容易出错的位置’会更像真教程。",
        ),
        scene="适合美妆、收纳、厨房、剪辑技巧类内容。",
    ),
    ScriptTypeProfile(
        name="剧情类",
        icon="◆",
        rhythm="冲突引入 + 情节推进 + 结果反转",
        hook="用人物对话或生活矛盾制造停留，再自然带出产品。",
        structure="人物困境 → 冲突升级 → 产品介入 → 反转解决 → 情绪收口",
        recommended_duration="30-50 秒",
        ideal_tone="有戏剧感",
        keywords=("原来关键在这", "差点翻车", "没想到", "反转来了"),
        tips=(
            "台词要短，像真对话，不要像说明书。",
            "产品出场别太早，先让冲突成立。",
            "结尾最好回到人物情绪变化。",
        ),
        scene="适合家庭清洁、母婴、情侣生活、居家用品类内容。",
    ),
    ScriptTypeProfile(
        name="对比评测",
        icon="⇄",
        rhythm="问题提出 + 条件统一 + 结果对照",
        hook="用同场景同条件对比，把差距直观做出来。",
        structure="提出疑问 → 对比标准 → 双边测试 → 结果归纳 → 选择建议",
        recommended_duration="28-42 秒",
        ideal_tone="理性客观",
        keywords=("差别这么大", "同样条件", "一眼看懂", "省钱选法"),
        tips=(
            "必须明确同样条件，否则对比不成立。",
            "不要只说更好，要说好在哪。",
            "最后一句给出场景化选择建议更容易转化。",
        ),
        scene="适合个护、清洁、收纳、办公设备类内容。",
    ),
)


SCRIPT_LIBRARY: tuple[ScriptTemplate, ...] = (
    ScriptTemplate(
        script_type="种草脚本",
        title="下班回家这一下真的会被治愈",
        opening_hook="如果你一回家就只想赶紧把桌面和情绪都收拾干净，这支 {product_name} 真的会让你舒服很多。",
        structure_label="情绪共鸣版",
        estimated_duration="32 秒",
        quality_score="91",
        adoption_hint="适合首发测试收藏率",
        tone="brand",
        summary="从用户日常疲惫感切入，强调使用后的轻松感和生活秩序感。",
        script_text=(
            "【开场】如果你也是下班回家脑子很乱、桌面也很乱的人，这支 {product_name} 我真心想安利给你。\n"
            "【场景】我最喜欢的是它在 {audience} 这种节奏很快的日常里，几乎不需要思考就能直接上手。\n"
            "【卖点】第一，它的核心优势就是 {keywords} 这些高频需求都照顾到了；第二，整个体验不会有多余步骤，节奏很顺。\n"
            "【感受】你会发现自己不是在‘完成一个任务’，而是在把家里和心情一起整理好。\n"
            "【结尾】如果你也想把日常过得更轻一点，这条先收藏，照着试一次就知道值不值。"
        ),
        selling_points=("情绪价值高", "生活感强", "收藏驱动明显"),
        cta="先收藏，晚上回家直接照着拍。",
        tags=("通勤党", "生活方式", "情绪共鸣"),
    ),
    ScriptTemplate(
        script_type="种草脚本",
        title="原来真正拉开体验差距的是这几个细节",
        opening_hook="很多人第一眼看 {product_name} 觉得差不多，但真正用起来，细节差距真的会很明显。",
        structure_label="细节种草版",
        estimated_duration="36 秒",
        quality_score="93",
        adoption_hint="适合叠加特写镜头",
        tone="success",
        summary="突出细节质感和长期体验，适合偏理性但仍想种草的人群。",
        script_text=(
            "【开场】同样是这类产品，为什么有的你会一直用，有的买回来两天就放一边？\n"
            "【细节一】我拿到 {product_name} 第一感受就是顺手，尤其对 {audience} 这种要高频使用的人来说，顺手真的很重要。\n"
            "【细节二】像 {keywords} 这些点，如果没有做好，拍视频好看也没用，真实体验会很快掉分。\n"
            "【总结】它不是那种一眼惊艳，但会越用越顺的类型，所以我更愿意把它归到‘回购型好物’。\n"
            "【CTA】如果你最近正准备入手，建议把这几个细节先记下来再选。"
        ),
        selling_points=("强调细节", "适合理性种草", "利于评论讨论"),
        cta="把这几个细节点收藏下来，选购更稳。",
        tags=("细节控", "理性种草", "回购型"),
    ),
    ScriptTemplate(
        script_type="开箱测评",
        title="别只看外观，真正拉开差距的是上手这一刻",
        opening_hook="今天不吹不黑，我们直接把 {product_name} 拆开看，第一眼、上手、实测，全都给你看清楚。",
        structure_label="拆箱实测版",
        estimated_duration="38 秒",
        quality_score="92",
        adoption_hint="适合高客单测评",
        tone="info",
        summary="用拆箱 + 实测节奏输出明确结论，适合需要信任建立的商品。",
        script_text=(
            "【开箱】先看包装，整体第一印象是干净利落，没有那种一拆开就很廉价的感觉。\n"
            "【细节】我重点看了几个地方：做工、边角、握持感，还有 {keywords} 相关的使用便利度。\n"
            "【上手】拿在手里之后，对 {audience} 这种重视效率的人来说，最明显的感受就是步骤少、反馈快。\n"
            "【结论】如果你只是想拍照好看，它够用；如果你想要长期稳定体验，它也站得住。\n"
            "【CTA】所以这次我的建议很简单：预算够、需求明确，可以入；如果你只图便宜，就先别冲。"
        ),
        selling_points=("信任感强", "结论明确", "适合测评账号"),
        cta="预算和需求都对上，再决定入不入。",
        tags=("开箱", "实测", "结论导向"),
    ),
    ScriptTemplate(
        script_type="开箱测评",
        title="我最在意的三项都过关了",
        opening_hook="拿到 {product_name} 之后，我最先看的不是配色，而是这三项到底能不能打。",
        structure_label="三点评测版",
        estimated_duration="34 秒",
        quality_score="90",
        adoption_hint="适合配字幕条",
        tone="warning",
        summary="用‘三点法’快速完成测评叙事，适合节奏更短的视频。",
        script_text=(
            "【第一点】先说做工，这一类产品最怕看着高级、摸起来松。{product_name} 这点目前是稳的。\n"
            "【第二点】再说上手效率，像 {keywords} 这类核心需求如果不到位，拍视频再高级也没意义。\n"
            "【第三点】最后看适配场景，对 {audience} 这种人群来说，它不是只能在一个场景用，而是能覆盖高频日常。\n"
            "【总结】所以我的结论是：不是样子货，是真正适合拿来长期用的。\n"
            "【CTA】如果你也纠结值不值，先把这三项作为判断标准。"
        ),
        selling_points=("结构清楚", "易做字幕分段", "适合短时长"),
        cta="收藏这三项判断标准，买前先对照。",
        tags=("三点评测", "短时长", "字幕友好"),
    ),
    ScriptTemplate(
        script_type="教程讲解",
        title="照着这个顺序做，新手也不容易翻车",
        opening_hook="如果你总觉得这件事很麻烦，今天我用 {product_name} 给你拆成最简单的三个动作。",
        structure_label="新手教学版",
        estimated_duration="42 秒",
        quality_score="94",
        adoption_hint="适合保存转化",
        tone="brand",
        summary="以结果前置和步骤拆解为主，适合强实用价值内容。",
        script_text=(
            "【结果先说】学会这个顺序之后，你会发现整个过程快很多，而且不容易出错。\n"
            "【步骤一】先确定使用目标，再准备 {product_name} 的关键动作，这一步别急，顺序比速度重要。\n"
            "【步骤二】接着把 {keywords} 相关的部分一次处理掉，避免后面来回返工。\n"
            "【步骤三】最后做检查和收口，这一步很多人会省，但其实最影响成片效果。\n"
            "【复盘】特别是 {audience} 这种新手用户，只要记住‘先准备、再执行、最后检查’，就已经能少踩很多坑。"
        ),
        selling_points=("步骤明确", "适合收藏", "教学口吻自然"),
        cta="这条先留着，真正用的时候直接照着做。",
        tags=("新手友好", "步骤拆解", "保存率高"),
    ),
    ScriptTemplate(
        script_type="教程讲解",
        title="最容易做错的地方我先帮你避开了",
        opening_hook="很多人不是不会做，而是一开始顺序就错了，今天这条就是帮你省掉返工。",
        structure_label="避坑教学版",
        estimated_duration="39 秒",
        quality_score="91",
        adoption_hint="适合系列化内容",
        tone="success",
        summary="以避坑为钩子，强化专业感和确定性。",
        script_text=(
            "【开场】你如果每次做到一半才发现不对，问题大概率不是手慢，而是顺序不对。\n"
            "【避坑一】使用 {product_name} 时，第一步千万不要直接开始，先把需求和场景想清楚。\n"
            "【避坑二】中间处理 {keywords} 这一步最容易偷懒，但它恰好决定最后质感。\n"
            "【避坑三】最后别急着结束，留十秒做一次检查，成片稳定度会高很多。\n"
            "【总结】尤其对 {audience} 这种讲求效率的人来说，这个顺序会让体验好非常多。"
        ),
        selling_points=("避坑表达强", "专业信任感高", "利于做系列"),
        cta="把这条当检查清单留着会很实用。",
        tags=("避坑", "检查清单", "效率提升"),
    ),
    ScriptTemplate(
        script_type="剧情类",
        title="原本以为又要翻车，结果被这一步救回来了",
        opening_hook="昨天我差点因为一个小问题把整段内容重拍，没想到最后是 {product_name} 把节奏救回来了。",
        structure_label="轻反转剧情版",
        estimated_duration="41 秒",
        quality_score="90",
        adoption_hint="适合人物口播出镜",
        tone="warning",
        summary="先立冲突，再让产品自然介入，情绪起伏更明显。",
        script_text=(
            "【冲突】本来拍到一半我已经想放弃了，因为前面的节奏完全不对，画面也有点乱。\n"
            "【升级】尤其是 {keywords} 这几个点没处理好，内容看起来会很碎。\n"
            "【介入】后来我换成 {product_name} 重新走了一遍流程，最明显的感觉就是终于顺下来了。\n"
            "【反转】你会发现很多时候不是你不会拍，而是工具和步骤没有对上。\n"
            "【收口】所以如果你也是 {audience} 这种容易被细节拖住的人，这类产品真的不是可有可无。"
        ),
        selling_points=("情绪波动明显", "适合出镜", "停留更强"),
        cta="如果你也常被流程卡住，先把这条记下来。",
        tags=("轻剧情", "反转", "口播出镜"),
    ),
    ScriptTemplate(
        script_type="剧情类",
        title="本来只是想试一下，结果全程都在感叹",
        opening_hook="我原本真的只是想简单试一下 {product_name}，结果从第一步开始就不停想说一句：原来还能这么省心。",
        structure_label="生活流剧情版",
        estimated_duration="37 秒",
        quality_score="88",
        adoption_hint="适合慢一点的生活化节奏",
        tone="info",
        summary="偏生活流叙事，适合弱推销、强体验型表达。",
        script_text=(
            "【起因】今天原本只是想快点把事情处理完，完全没准备认真拍。\n"
            "【变化】结果一上手我就发现，像 {keywords} 这些细节被处理好之后，整个过程轻松太多。\n"
            "【推进】特别是对 {audience} 这种平时事情很多的人来说，这种‘不用费脑子’的顺畅感会特别明显。\n"
            "【感受】所以这条不是要告诉你它有多夸张，而是它真的把原本麻烦的过程变得很自然。\n"
            "【结尾】如果你喜欢生活感更强的内容，这种拍法很容易让人看完不反感。"
        ),
        selling_points=("生活感浓", "适合低压力转化", "评论氛围友好"),
        cta="生活化内容可以直接套这个节奏。",
        tags=("生活流", "自然转化", "弱推销"),
    ),
    ScriptTemplate(
        script_type="对比评测",
        title="同样条件下，差别真的一眼就能看出来",
        opening_hook="今天我们不聊感觉，直接把两种方案放在同样条件下，看 {product_name} 到底赢在哪。",
        structure_label="同条件对比版",
        estimated_duration="35 秒",
        quality_score="95",
        adoption_hint="适合转化冲刺",
        tone="success",
        summary="对比逻辑清晰，适合需要高说服力的内容场景。",
        script_text=(
            "【设问】很多人都说差不多，但真的放在同样条件下，差距会非常直接。\n"
            "【标准】我们统一看三点：效率、稳定度，还有 {keywords} 这种用户最在意的体验。\n"
            "【结果】第一轮就能看出来，{product_name} 在节奏和反馈上更适合 {audience} 这种高频需求。\n"
            "【解释】不是因为它参数写得更漂亮，而是它在真实使用链路里少了很多卡顿。\n"
            "【建议】如果你重视省时间和稳定体验，选它更稳；如果只是偶尔用，才考虑更低门槛的方案。"
        ),
        selling_points=("说服力强", "高转化", "适合参数党"),
        cta="选购前先看清你更在意哪一种场景。",
        tags=("对比", "理性决策", "转化冲刺"),
    ),
    ScriptTemplate(
        script_type="对比评测",
        title="为什么有的人用着顺，有的人总觉得鸡肋",
        opening_hook="同类产品里最常见的误区，就是只看价格不看使用路径，今天直接对比给你看。",
        structure_label="场景选择版",
        estimated_duration="33 秒",
        quality_score="90",
        adoption_hint="适合预算向内容",
        tone="brand",
        summary="更强调人群与场景差异，适合预算敏感型受众。",
        script_text=(
            "【问题】为什么同样的东西，有的人天天用，有的人两天就闲置？\n"
            "【核心】关键不在贵不贵，而在是不是适合你的真实路径。\n"
            "【对比】像 {keywords} 这些需求，如果你每天都会碰到，那 {product_name} 的价值就会被持续放大。\n"
            "【人群】特别是 {audience} 这种讲究效率的人群，会更明显感受到差别。\n"
            "【结论】所以别只看表面配置，先看自己是不是那个真正会高频使用的人。"
        ),
        selling_points=("预算党友好", "场景化解释强", "易引发评论"),
        cta="先判断自己属于哪类使用者，再决定买哪种。",
        tags=("预算党", "使用路径", "场景选择"),
    ),
)


SCRIPT_HISTORY: tuple[HistoryRecord, ...] = (
    HistoryRecord("今天 10:48", "奶油白随行杯", "种草脚本", "30 秒", "92", "已采用", "内容组 A", "首发视频采用情绪共鸣版，收藏率高。"),
    HistoryRecord("今天 09:20", "磁吸车载支架", "对比评测", "35 秒", "95", "已发布", "内容组 B", "同条件对比表现最好，评论讨论活跃。"),
    HistoryRecord("昨天 20:15", "分区收纳箱", "教程讲解", "42 秒", "93", "待复盘", "内容组 A", "步骤表达清楚，完播稳定。"),
    HistoryRecord("昨天 16:32", "静音电动牙刷", "开箱测评", "38 秒", "91", "已保存", "内容组 C", "细节特写版本更适合做二轮迭代。"),
    HistoryRecord("昨天 11:05", "桌面理线夹", "剧情类", "36 秒", "88", "已采用", "内容组 D", "生活流冲突感弱，建议补一处反转。"),
    HistoryRecord("周六 19:45", "双层便当盒", "种草脚本", "34 秒", "90", "已发布", "内容组 A", "适合上班族人群，午间场景代入强。"),
    HistoryRecord("周六 14:08", "折叠脏衣篮", "教程讲解", "40 秒", "94", "已采用", "内容组 B", "新手向表达清晰，评论区提问少。"),
    HistoryRecord("周五 18:10", "桌面补光灯", "开箱测评", "33 秒", "89", "已保存", "内容组 C", "开箱镜头好，结论句可更强。"),
    HistoryRecord("周五 11:18", "防滑瑜伽垫", "对比评测", "32 秒", "90", "待测试", "内容组 D", "对比结果明确，缺少场景化收口。"),
    HistoryRecord("周四 15:26", "香氛洗衣凝珠", "剧情类", "39 秒", "87", "已发布", "内容组 A", "人物冲突成立，产品露出自然。"),
)


STRATEGY_NOTES: tuple[StrategyNote, ...] = (
    StrategyNote("先写用户，不先写产品", "脚本前两句优先让观众知道‘这条是写给谁的’，再带出产品，推荐流点击更稳。", "身份词前置通常会提升前 3 秒停留。", "brand"),
    StrategyNote("给步骤加确定性", "教程与测评类脚本里加入时长、顺序、温度、数量等具体信息，可信度会明显提升。", "建议至少出现 2 处可量化表达。", "success"),
    StrategyNote("结尾不要只喊下单", "用‘先收藏 / 先对照 / 先记住这一步’代替生硬催单，用户反感更低。", "收藏型 CTA 更适合冷启动内容。", "info"),
    StrategyNote("情绪词只保留一个重音", "‘真的、太、绝了、必须’这类词不要叠加太多，否则信息密度会变差。", "建议每条只保留 1 个强情绪词。", "warning"),
)


KEYWORD_PULSES: tuple[KeywordPulse, ...] = (
    KeywordPulse("建议收藏", "热度 98", "+28%", "brand"),
    KeywordPulse("别盲买", "热度 91", "+19%", "warning"),
    KeywordPulse("同样条件", "热度 86", "+17%", "info"),
    KeywordPulse("通勤党", "热度 82", "+22%", "success"),
    KeywordPulse("原来关键在这", "热度 79", "+14%", "brand"),
    KeywordPulse("新手也能学会", "热度 76", "+16%", "success"),
)


DEFAULT_PRODUCT_INFO = """商品：奶油白随行杯
核心卖点：防漏、轻量、单手开盖、通勤包好收纳
内容场景：早八通勤、午间续杯、会议桌面、下班带走
差异化亮点：磨砂质感、杯口顺滑、颜色出片、容量适中
目标：输出可直接拍短视频的中文脚本，不要空泛形容。"""


DEFAULT_KEYWORDS = ("通勤党", "建议收藏", "防漏", "回购型")


def _tone_badge(tone: str) -> BadgeTone:
    """兼容 tone 名称。"""

    if tone == "success":
        return "success"
    if tone == "warning":
        return "warning"
    if tone == "error":
        return "error"
    if tone == "info":
        return "info"
    if tone == "brand":
        return "brand"
    return "neutral"


def _layout_count(layout: object) -> int:
    """兼容获取布局项数量。"""

    counter = getattr(layout, "count", None)
    if callable(counter):
        value = counter()
        if isinstance(value, int):
            return value
    items = getattr(layout, "_items", [])
    return len(items) if isinstance(items, list) else 0


def _clear_layout(layout: object) -> None:
    """兼容清空布局。"""

    take_at = getattr(layout, "takeAt", None)
    if callable(take_at):
        while _layout_count(layout) > 0:
            item = take_at(0)
            if item is None:
                break
            widget_getter = getattr(item, "widget", None)
            nested_layout_getter = getattr(item, "layout", None)
            widget = widget_getter() if callable(widget_getter) else None
            nested_layout = nested_layout_getter() if callable(nested_layout_getter) else None
            if widget is not None:
                _call(widget, "setParent", None)
                _call(widget, "deleteLater")
            if nested_layout is not None:
                _clear_layout(nested_layout)
        return
    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


class ScriptGenerationPage(BasePage):
    """AI 驱动的脚本生成工作台。"""

    default_route_id = RouteId("script_generation")
    default_display_name = "脚本生成"
    default_icon_name = "description"

    def __init__(self, parent: object | None = None):
        self._records: list[HistoryRecord] = list(SCRIPT_HISTORY)
        self._profiles: list[ScriptTypeProfile] = list(SCRIPT_TYPES)
        self._script_templates: list[ScriptTemplate] = list(SCRIPT_LIBRARY)
        self._generated_scripts: list[ScriptTemplate] = []
        self._filtered_scripts: list[ScriptTemplate] = []
        self._active_type_index = 0
        self._script_keyword = ""
        self._history_keyword = ""
        self._selected_script_title = ""
        self._streaming_output: StreamingOutputWidget | None = None
        self._ai_config_panel: AIConfigPanel | None = None
        self._type_tabs: TabBar | None = None
        self._product_name_input: ThemedLineEdit | None = None
        self._product_info_input: ThemedTextEdit | None = None
        self._audience_input: ThemedLineEdit | None = None
        self._tone_input: ThemedComboBox | None = None
        self._duration_input: ThemedComboBox | None = None
        self._keywords_input: TagInput | None = None
        self._angle_input: ThemedLineEdit | None = None
        self._script_cards_host: QWidget | None = None
        self._script_cards_layout: QVBoxLayout | None = None
        self._history_table: DataTable | None = None
        self._history_count_label: QLabel | None = None
        self._script_count_label: QLabel | None = None
        self._current_type_summary_label: QLabel | None = None
        self._current_type_hint_label: QLabel | None = None
        self._model_summary_label: QLabel | None = None
        self._selected_title_label: QLabel | None = None
        self._selected_cta_label: QLabel | None = None
        self._selected_score_label: QLabel | None = None
        self._selected_hint_label: QLabel | None = None
        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        container = PageContainer(
            title="脚本生成",
            description="面向 TikTok Shop 内容团队的脚本生成实验台，覆盖脚本类型切换、输入编排、AI 生成与历史复盘。",
            actions=[PrimaryButton("生成新脚本", self, icon_text="✦"), IconButton("⋯", "更多操作", self)],
            max_width=DESKTOP_PAGE_MAX_WIDTH,
        )
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(container)

        scroll = ThemedScrollArea(container)
        scroll.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.content_layout.setSpacing(SPACING_2XL)
        container.add_widget(scroll)

        scroll.add_widget(self._build_overview_section())
        scroll.add_widget(self._build_type_section())
        scroll.add_widget(self._build_workspace_section())
        scroll.add_widget(self._build_results_section())
        scroll.add_widget(self._build_footer_section())

        self._apply_page_styles()
        self._bind_interactions()
        self._seed_default_values()
        self._refresh_all_views()

    def _build_overview_section(self) -> QWidget:
        section = ContentSection("脚本增长概览", icon="✦", parent=self)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(8)
        badge_row.addWidget(StatusBadge("模型已就绪", tone="success", parent=section))
        badge_row.addWidget(StatusBadge("适合冷启动内容", tone="brand", parent=section))
        badge_row.addWidget(StatusBadge("建议先测 30-40 秒版本", tone="info", parent=section))
        badge_row.addStretch(1)
        section.content_layout.addLayout(badge_row)

        kpi_row = QHBoxLayout()
        kpi_row.setContentsMargins(0, 0, 0, 0)
        kpi_row.setSpacing(12)
        kpi_row.addWidget(KPICard(title="生成总数", value="1,286", trend="up", percentage="+12.4%", caption="近 30 天累计", sparkline_data=[820, 860, 902, 960, 1040, 1168, 1286], parent=section))
        kpi_row.addWidget(KPICard(title="采用率", value="68%", trend="up", percentage="+5.7%", caption="进入发布流程", sparkline_data=[49, 53, 56, 59, 61, 65, 68], parent=section))
        kpi_row.addWidget(KPICard(title="平均质量分", value="91.3", trend="flat", percentage="稳定", caption="结构与可拍性综合", sparkline_data=[89, 90, 91, 91, 92, 91, 91], parent=section))
        kpi_row.addWidget(KPICard(title="AI 使用量", value="392K", trend="up", percentage="+18%", caption="本周 Token 消耗", sparkline_data=[210, 228, 244, 282, 310, 350, 392], parent=section))
        section.content_layout.addLayout(kpi_row)

        bottom_host = QWidget(section)
        bottom_layout = QVBoxLayout(bottom_host)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(12)

        insight = InfoCard(
            title="今日脚本策略",
            description="当前账号更适合‘身份词 + 具体场景 + 一条结论’的开场。若要提升完播，优先在第 8-12 秒补出可视化结果，而不是继续讲参数。",
            icon="◎",
            action_text="同步到工作区",
            parent=section,
        )
        bottom_layout.addWidget(insight)

        signal_box = QWidget(section)
        signal_layout = QHBoxLayout(signal_box)
        signal_layout.setContentsMargins(0, 0, 0, 0)
        signal_layout.setSpacing(10)
        signal_layout.addWidget(StatsBadge("热点词命中", "4/6", icon="▲", tone="brand", parent=signal_box))
        signal_layout.addWidget(StatsBadge("适拍指数", "高", icon="◎", tone="success", parent=signal_box))
        signal_layout.addWidget(StatsBadge("风险密度", "低", icon="◌", tone="info", parent=signal_box))
        signal_layout.addStretch(1)
        bottom_layout.addWidget(signal_box)

        section.content_layout.addWidget(bottom_host)
        return section

    def _build_type_section(self) -> QWidget:
        section = ContentSection("脚本类型切换", icon="◈", parent=self)

        intro = QFrame(section)
        intro.setStyleSheet(panel_frame_style(variant="highlight"))
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(16, 14, 16, 14)
        intro_layout.setSpacing(8)

        title = QLabel("当前脚本方向", intro)
        title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        self._current_type_summary_label = QLabel("种草脚本 · 适合用真实体验建立信任感。", intro)
        current_type_summary_label = self._current_type_summary_label
        if current_type_summary_label is not None:
            current_type_summary_label.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
        self._current_type_hint_label = QLabel("推荐结构：开场共鸣 → 卖点体验 → 情绪收口 → 收藏 CTA", intro)
        current_type_hint_label = self._current_type_hint_label
        if current_type_hint_label is not None:
            current_type_hint_label.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
            _call(current_type_hint_label, "setWordWrap", True)
        intro_layout.addWidget(title)
        if current_type_summary_label is not None:
            intro_layout.addWidget(current_type_summary_label)
        if current_type_hint_label is not None:
            intro_layout.addWidget(current_type_hint_label)
        section.content_layout.addWidget(intro)

        self._type_tabs = TabBar(section)
        for profile in self._profiles:
            self._type_tabs.add_tab(profile.name, self._build_type_tab(profile))
        section.content_layout.addWidget(self._type_tabs)
        return section

    def _build_type_tab(self, profile: ScriptTypeProfile) -> QWidget:
        host = QWidget(self)
        root = QVBoxLayout(host)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        hero = QFrame(host)
        hero.setStyleSheet(panel_frame_style())
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(16, 16, 16, 16)
        hero_layout.setSpacing(10)

        hero_row = QHBoxLayout()
        hero_row.setContentsMargins(0, 0, 0, 0)
        hero_row.setSpacing(8)
        hero_row.addWidget(StatusBadge(profile.name, tone="brand", parent=hero))
        hero_row.addWidget(StatusBadge(profile.recommended_duration, tone="info", parent=hero))
        hero_row.addWidget(StatusBadge(profile.ideal_tone, tone="success", parent=hero))
        hero_row.addStretch(1)

        hook = QLabel(profile.hook, hero)
        hook.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        _call(hook, "setWordWrap", True)
        structure = QLabel(f"结构建议：{profile.structure}", hero)
        structure.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        _call(structure, "setWordWrap", True)
        scene = QLabel(f"适用场景：{profile.scene}", hero)
        scene.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        _call(scene, "setWordWrap", True)

        hero_layout.addLayout(hero_row)
        hero_layout.addWidget(hook)
        hero_layout.addWidget(structure)
        hero_layout.addWidget(scene)
        root.addWidget(hero)

        keywords_row = QWidget(host)
        keywords_layout = QHBoxLayout(keywords_row)
        keywords_layout.setContentsMargins(0, 0, 0, 0)
        keywords_layout.setSpacing(8)
        for word in profile.keywords:
            keywords_layout.addWidget(TagChip(word, tone="neutral", parent=keywords_row))
        keywords_layout.addStretch(1)
        root.addWidget(keywords_row)

        for tip in profile.tips:
            tip_frame = QFrame(host)
            tip_frame.setStyleSheet(panel_frame_style(variant="dashed"))
            tip_layout = QHBoxLayout(tip_frame)
            tip_layout.setContentsMargins(12, 10, 12, 10)
            tip_layout.setSpacing(10)
            tip_layout.addWidget(StatusBadge("执行提示", tone="warning", parent=tip_frame))
            tip_label = QLabel(tip, tip_frame)
            tip_label.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
            _call(tip_label, "setWordWrap", True)
            tip_layout.addWidget(tip_label, 1)
            root.addWidget(tip_frame)
        return host

    def _build_workspace_section(self) -> QWidget:
        section = ContentSection("脚本生成工作区", icon="⚙", parent=self)
        split = SplitPanel("horizontal", split_ratio=(0.62, 0.38), minimum_sizes=(700, 460), parent=section)
        split.set_widgets(self._build_editor_panel(), self._build_ai_panel())
        section.content_layout.addWidget(split)
        return section

    def _build_results_section(self) -> QWidget:
        host = SplitPanel("horizontal", split_ratio=(0.58, 0.42), minimum_sizes=(720, 560), parent=self)
        host.set_widgets(self._build_generated_section(), self._build_history_section())
        return host

    def _build_editor_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        summary = QFrame(panel)
        summary.setStyleSheet(panel_frame_style(variant="highlight"))
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        title = QLabel("创作输入摘要", summary)
        title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(StatusBadge("可直接生成", tone="success", parent=summary))
        summary_layout.addLayout(header)

        summary_layout.addWidget(StatsBadge("建议时长", "30-40 秒", icon="◷", tone="info", parent=summary))
        summary_layout.addWidget(StatsBadge("当前重心", "场景 + 卖点", icon="◎", tone="brand", parent=summary))
        summary_layout.addWidget(StatsBadge("账号适配", "冷启动友好", icon="▲", tone="success", parent=summary))
        root.addWidget(summary)

        self._product_name_input = ThemedLineEdit(
            label="商品名称",
            placeholder="例如：奶油白随行杯 / 分区收纳箱 / 桌面补光灯",
            helper_text="建议写完整商品名，利于脚本中自然出现。",
            parent=None,
        )
        root.addWidget(self._product_name_input)

        self._product_info_input = ThemedTextEdit(
            label="商品信息",
            placeholder="填写商品卖点、使用场景、材质细节、视频重点与想避开的表达。",
            parent=None,
        )
        root.addWidget(self._product_info_input)

        audience_row = QHBoxLayout()
        audience_row.setContentsMargins(0, 0, 0, 0)
        audience_row.setSpacing(12)
        self._audience_input = ThemedLineEdit(
            label="目标人群",
            placeholder="例如：通勤党、租房党、新手用户",
            helper_text="用户身份词越清晰，开场越容易建立代入。",
            parent=None,
        )
        self._angle_input = ThemedLineEdit(
            label="切入角度",
            placeholder="例如：省时间 / 细节质感 / 对比差异 / 情绪治愈",
            helper_text="决定第一句怎么开口。",
            parent=None,
        )
        audience_row.addWidget(self._audience_input, 1)
        audience_row.addWidget(self._angle_input, 1)
        root.addLayout(audience_row)

        config_row = QHBoxLayout()
        config_row.setContentsMargins(0, 0, 0, 0)
        config_row.setSpacing(12)
        self._tone_input = ThemedComboBox(label="表达语气", items=("真实自然", "专业克制", "轻松亲切", "有戏剧感", "理性客观"), parent=None)
        self._duration_input = ThemedComboBox(label="时长偏好", items=("25-30 秒", "30-40 秒", "40-50 秒", "50-60 秒"), parent=None)
        config_row.addWidget(self._tone_input, 1)
        config_row.addWidget(self._duration_input, 1)
        root.addLayout(config_row)

        self._keywords_input = TagInput(label="关键词池", placeholder="输入关键词后回车，支持多个词", parent=None)
        root.addWidget(self._keywords_input)

        pulse_box = QFrame(panel)
        pulse_box.setStyleSheet(panel_frame_style())
        pulse_layout = QVBoxLayout(pulse_box)
        pulse_layout.setContentsMargins(16, 14, 16, 14)
        pulse_layout.setSpacing(10)
        pulse_title = QLabel("今日可直接带入的热点词", pulse_box)
        pulse_title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        pulse_layout.addWidget(pulse_title)

        pulse_row = QWidget(pulse_box)
        pulse_row_layout = QHBoxLayout(pulse_row)
        pulse_row_layout.setContentsMargins(0, 0, 0, 0)
        pulse_row_layout.setSpacing(8)
        for pulse in KEYWORD_PULSES:
            button = QPushButton(f"{pulse.keyword} {pulse.direction}", pulse_row)
            _call(button, "setStyleSheet", f"""
                QPushButton {{
                    background: {rgba_color(_token('brand.primary'), 0.10)};
                    color: {_token('brand.primary')};
                    border: 1px solid {rgba_color(_token('brand.primary'), 0.18)};
                    border-radius: 16px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background: {rgba_color(_token('brand.primary'), 0.16)};
                }}
            """)
            _connect(button.clicked, lambda word=pulse.keyword: self._append_keyword(word))
            pulse_row_layout.addWidget(button)
        pulse_row_layout.addStretch(1)
        pulse_layout.addWidget(pulse_row)
        root.addWidget(pulse_box)

        tips_box = QFrame(panel)
        tips_box.setStyleSheet(panel_frame_style())
        tips_layout = QVBoxLayout(tips_box)
        tips_layout.setContentsMargins(16, 14, 16, 14)
        tips_layout.setSpacing(10)
        tips_title = QLabel("生成前检查", tips_box)
        tips_title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        tips_layout.addWidget(tips_title)
        for note in STRATEGY_NOTES:
            item = QFrame(tips_box)
            item.setStyleSheet(panel_frame_style(variant="dashed"))
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(12, 10, 12, 10)
            item_layout.setSpacing(4)
            head = QLabel(note.title, item)
            head.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
            body = QLabel(note.detail, item)
            body.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
            _call(body, "setWordWrap", True)
            tail = QLabel(note.highlight, item)
            tail.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm"))
            _call(tail, "setWordWrap", True)
            item_layout.addWidget(head)
            item_layout.addWidget(body)
            item_layout.addWidget(tail)
            tips_layout.addWidget(item)
        root.addWidget(tips_box)
        return panel

    def _build_ai_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self._ai_config_panel = AIConfigPanel(panel)
        root.addWidget(self._ai_config_panel)

        config_summary = QFrame(panel)
        config_summary.setStyleSheet(panel_frame_style(variant="highlight"))
        config_layout = QVBoxLayout(config_summary)
        config_layout.setContentsMargins(16, 14, 16, 14)
        config_layout.setSpacing(8)
        title = QLabel("模型摘要", config_summary)
        title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        self._model_summary_label = QLabel("OpenAI · gpt-4o · 脚本创作者 · 温度 0.7", config_summary)
        model_summary_label = self._model_summary_label
        if model_summary_label is not None:
            model_summary_label.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
        desc = QLabel("当前配置适合生成首版脚本；若要做结构修订，可适度降低温度让表达更稳。", config_summary)
        desc.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        _call(desc, "setWordWrap", True)
        config_layout.addWidget(title)
        if model_summary_label is not None:
            config_layout.addWidget(model_summary_label)
        config_layout.addWidget(desc)
        root.addWidget(config_summary)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        generate_button = PrimaryButton("生成脚本", panel, icon_text="✦")
        refresh_button = SecondaryButton("再来一组", panel, icon_text="↻")
        clear_button = SecondaryButton("清空输出", panel, icon_text="⌫")
        _connect(generate_button.clicked, self._on_generate_clicked)
        _connect(refresh_button.clicked, self._on_regenerate_clicked)
        _connect(clear_button.clicked, self._clear_output)
        action_row.addWidget(generate_button)
        action_row.addWidget(refresh_button)
        action_row.addWidget(clear_button)
        root.addLayout(action_row)

        selected_box = QFrame(panel)
        selected_box.setStyleSheet(panel_frame_style())
        selected_layout = QVBoxLayout(selected_box)
        selected_layout.setContentsMargins(16, 14, 16, 14)
        selected_layout.setSpacing(8)
        selected_head = QLabel("当前推荐脚本", selected_box)
        selected_head.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        self._selected_title_label = QLabel("生成后自动显示最佳脚本标题", selected_box)
        selected_title_label = self._selected_title_label
        if selected_title_label is not None:
            selected_title_label.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
        self._selected_cta_label = QLabel("CTA：先生成内容后查看", selected_box)
        selected_cta_label = self._selected_cta_label
        if selected_cta_label is not None:
            selected_cta_label.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        self._selected_score_label = QLabel("质量分：--", selected_box)
        selected_score_label = self._selected_score_label
        if selected_score_label is not None:
            selected_score_label.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        self._selected_hint_label = QLabel("建议：优先输出真实使用场景与一条结论。", selected_box)
        selected_hint_label = self._selected_hint_label
        if selected_hint_label is not None:
            selected_hint_label.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
            _call(selected_hint_label, "setWordWrap", True)
        if selected_cta_label is not None:
            _call(selected_cta_label, "setWordWrap", True)
        selected_layout.addWidget(selected_head)
        if selected_title_label is not None:
            selected_layout.addWidget(selected_title_label)
        if selected_cta_label is not None:
            selected_layout.addWidget(selected_cta_label)
        if selected_score_label is not None:
            selected_layout.addWidget(selected_score_label)
        if selected_hint_label is not None:
            selected_layout.addWidget(selected_hint_label)
        root.addWidget(selected_box)

        self._streaming_output = StreamingOutputWidget(panel)
        root.addWidget(self._streaming_output)
        return panel

    def _build_generated_section(self) -> QWidget:
        section = ContentSection("已生成脚本", icon="☰", parent=self)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)
        script_search = SearchBar("搜索脚本标题、标签或结构...", None)
        _connect(script_search.search_changed, self._on_script_search_changed)
        controls.addWidget(script_search, 2)
        self._script_count_label = QLabel("共 0 条脚本", section)
        script_count_label = self._script_count_label
        if script_count_label is not None:
            script_count_label.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
            controls.addWidget(script_count_label)
        section.content_layout.addLayout(controls)

        self._script_cards_host = QWidget(section)
        self._script_cards_layout = QVBoxLayout(self._script_cards_host)
        script_cards_layout = self._script_cards_layout
        if script_cards_layout is not None:
            script_cards_layout.setContentsMargins(0, 0, 0, 0)
            script_cards_layout.setSpacing(12)
        section.content_layout.addWidget(self._script_cards_host)
        return section

    def _build_history_section(self) -> QWidget:
        section = ContentSection("历史脚本记录", icon="◉", parent=self)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(12)
        history_search = SearchBar("搜索商品、脚本类型或备注...", None)
        _connect(history_search.search_changed, self._on_history_search_changed)
        controls.addWidget(history_search, 2)
        self._history_count_label = QLabel("共 10 条记录", section)
        history_count_label = self._history_count_label
        if history_count_label is not None:
            history_count_label.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
            controls.addWidget(history_count_label)
        section.content_layout.addLayout(controls)

        self._history_table = DataTable(
            headers=("生成时间", "商品", "脚本类型", "时长", "质量分", "状态", "负责人", "备注"),
            rows=[],
            page_size=6,
            empty_text="暂无脚本历史",
            parent=section,
        )
        section.content_layout.addWidget(self._history_table)
        return section

    def _build_footer_section(self) -> QWidget:
        footer = QWidget(self)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        tip = QLabel("建议先选择脚本类型，再补商品信息与人群词，最后生成 2-4 条脚本做结构筛选。", footer)
        tip.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        _call(tip, "setWordWrap", True)
        fab = FloatingActionButton("✚", "创建新脚本实验", footer)
        layout.addWidget(tip, 1)
        layout.addStretch(1)
        layout.addWidget(fab)
        return footer

    def _bind_interactions(self) -> None:
        if self._type_tabs is not None:
            _connect(self._type_tabs.tab_changed, self._on_type_changed)
        if self._ai_config_panel is not None:
            _connect(self._ai_config_panel.config_changed, self._on_ai_config_changed)
        if self._history_table is not None:
            _connect(self._history_table.row_selected, self._on_history_row_selected)
            _connect(self._history_table.row_double_clicked, self._on_history_row_selected)

    def _seed_default_values(self) -> None:
        if self._product_name_input is not None:
            self._product_name_input.setText("奶油白随行杯")
        if self._product_info_input is not None:
            self._product_info_input.setPlainText(DEFAULT_PRODUCT_INFO)
        if self._audience_input is not None:
            self._audience_input.setText("都市通勤女性 / 早八上班族")
        if self._angle_input is not None:
            self._angle_input.setText("通勤轻松感 + 防漏细节")
        if self._tone_input is not None:
            _call(self._tone_input.combo_box, "setCurrentText", "真实自然")
        if self._duration_input is not None:
            _call(self._duration_input.combo_box, "setCurrentText", "30-40 秒")
        if self._keywords_input is not None:
            self._keywords_input.set_tags(DEFAULT_KEYWORDS)
        if self._ai_config_panel is not None:
            self._ai_config_panel.set_config(
                {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "agent_role": "脚本创作者",
                    "temperature": 0.7,
                    "max_tokens": 2200,
                    "top_p": 0.9,
                }
            )

    def _refresh_all_views(self) -> None:
        self._update_type_summary()
        self._update_model_summary()
        self._generate_scripts(initial=True)
        self._refresh_history_table()

    def _active_profile(self) -> ScriptTypeProfile:
        return self._profiles[self._active_type_index]

    def _current_product_name(self) -> str:
        return self._product_name_input.text().strip() if self._product_name_input is not None else "商品"

    def _current_audience(self) -> str:
        return self._audience_input.text().strip() if self._audience_input is not None else "目标用户"

    def _current_keywords_text(self) -> str:
        if self._keywords_input is None:
            return "核心卖点"
        tags = self._keywords_input.tags()
        return "、".join(tags[:4]) if tags else "核心卖点"

    def _on_type_changed(self, index: int) -> None:
        self._active_type_index = index
        profile = self._active_profile()
        if self._tone_input is not None:
            _call(self._tone_input.combo_box, "setCurrentText", profile.ideal_tone)
        if self._duration_input is not None:
            _call(self._duration_input.combo_box, "setCurrentText", profile.recommended_duration)
        if self._angle_input is not None:
            self._angle_input.setText(profile.rhythm)
        if self._keywords_input is not None:
            self._keywords_input.set_tags(profile.keywords)
        self._update_type_summary()
        self._generate_scripts(initial=True)

    def _on_ai_config_changed(self, _config: dict[str, object]) -> None:
        self._update_model_summary()

    def _on_generate_clicked(self) -> None:
        self._generate_scripts(initial=False)

    def _on_regenerate_clicked(self) -> None:
        self._generate_scripts(initial=False, regenerate=True)

    def _clear_output(self) -> None:
        if self._streaming_output is not None:
            self._streaming_output.clear()

    def _append_keyword(self, keyword: str) -> None:
        if self._keywords_input is not None:
            self._keywords_input.add_tag(keyword)

    def _on_script_search_changed(self, keyword: str) -> None:
        self._script_keyword = keyword.strip().lower()
        self._render_script_cards()

    def _on_history_search_changed(self, keyword: str) -> None:
        self._history_keyword = keyword.strip().lower()
        self._refresh_history_table()

    def _generate_scripts(self, *, initial: bool, regenerate: bool = False) -> None:
        profile = self._active_profile()
        selected = [item for item in self._script_templates if item.script_type == profile.name]
        if regenerate and len(selected) > 1:
            selected = list(reversed(selected))
        self._generated_scripts = [self._resolve_template(item) for item in selected[:2]]
        if not initial:
            self._push_stream_output(self._generated_scripts)
            if self._generated_scripts:
                self._prepend_history(self._generated_scripts[0])
        self._render_script_cards()
        self._update_selected_summary(self._generated_scripts[0] if self._generated_scripts else None)

    def _resolve_template(self, template: ScriptTemplate) -> ScriptTemplate:
        product_name = self._current_product_name()
        audience = self._current_audience()
        keywords_text = self._current_keywords_text()

        def fill(text: str) -> str:
            return (
                text.replace("{product_name}", product_name)
                .replace("{audience}", audience)
                .replace("{keywords}", keywords_text)
            )

        return ScriptTemplate(
            script_type=template.script_type,
            title=fill(template.title),
            opening_hook=fill(template.opening_hook),
            structure_label=template.structure_label,
            estimated_duration=template.estimated_duration,
            quality_score=template.quality_score,
            adoption_hint=template.adoption_hint,
            tone=template.tone,
            summary=fill(template.summary),
            script_text=fill(template.script_text),
            selling_points=template.selling_points,
            cta=fill(template.cta),
            tags=template.tags,
        )

    def _push_stream_output(self, scripts: Sequence[ScriptTemplate]) -> None:
        if self._streaming_output is None:
            return
        self._streaming_output.clear()
        self._streaming_output.set_loading(True)
        intro = f"已根据【{self._active_profile().name}】生成 {len(scripts)} 条脚本方案。\n\n"
        self._streaming_output.append_chunk(intro)
        for index, script in enumerate(scripts, start=1):
            self._streaming_output.append_chunk(
                f"方案 {index}｜{script.title}\n开场钩子：{script.opening_hook}\n结构：{script.structure_label} · {script.estimated_duration}\n\n{script.script_text}\n\nCTA：{script.cta}\n\n"
            )
        prompt_tokens = 980 + len(self._current_keywords_text()) * 6
        completion_tokens = 420 + sum(len(script.script_text) for script in scripts) // 5
        self._streaming_output.set_token_usage(prompt_tokens, completion_tokens)
        self._streaming_output.set_loading(False)

    def _render_script_cards(self) -> None:
        if self._script_cards_layout is None:
            return
        _clear_layout(self._script_cards_layout)
        keyword = self._script_keyword
        filtered = []
        for script in self._generated_scripts:
            haystack = " ".join((script.title, script.summary, script.structure_label, script.cta, " ".join(script.tags))).lower()
            if keyword and keyword not in haystack:
                continue
            filtered.append(script)
        self._filtered_scripts = filtered
        if self._script_count_label is not None:
            self._script_count_label.setText(f"共 {len(filtered)} 条脚本")
        if not filtered:
            empty = QFrame(self)
            empty.setStyleSheet(panel_frame_style(variant="dashed"))
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(18, 18, 18, 18)
            empty_layout.setSpacing(8)
            title = QLabel("当前条件下没有匹配脚本", empty)
            title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
            detail = QLabel("试试切换脚本类型、清空搜索词，或点击“再来一组”重新生成。", empty)
            detail.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
            _call(detail, "setWordWrap", True)
            empty_layout.addWidget(title)
            empty_layout.addWidget(detail)
            self._script_cards_layout.addWidget(empty)
            return
        for script in filtered:
            self._script_cards_layout.addWidget(self._build_script_card(script))

    def _build_script_card(self, script: ScriptTemplate) -> QWidget:
        frame = QFrame(self)
        frame.setStyleSheet(panel_frame_style(variant="highlight" if script.title == self._selected_script_title else "default"))
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        title = QLabel(script.title, frame)
        title.setStyleSheet(label_text_style(size_token="font.size.lg", weight_token="font.weight.bold"))
        top.addWidget(title)
        top.addWidget(StatusBadge(script.estimated_duration, tone="info", parent=frame))
        top.addWidget(StatusBadge(f"质量分 {script.quality_score}", tone=_tone_badge(script.tone), parent=frame))
        top.addStretch(1)
        copy_button = SecondaryButton("复制", frame, icon_text="⎘")
        edit_button = SecondaryButton("编辑", frame, icon_text="✎")
        save_button = PrimaryButton("保存", frame, icon_text="✓")
        _connect(copy_button.clicked, lambda item=script: self._copy_script(item))
        _connect(edit_button.clicked, lambda item=script: self._edit_script(item))
        _connect(save_button.clicked, lambda item=script: self._save_script(item))
        top.addWidget(copy_button)
        top.addWidget(edit_button)
        top.addWidget(save_button)
        layout.addLayout(top)

        summary = QLabel(script.summary, frame)
        summary.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        _call(summary, "setWordWrap", True)
        layout.addWidget(summary)

        hook_box = QFrame(frame)
        hook_box.setStyleSheet(panel_frame_style(variant="dashed"))
        hook_layout = QVBoxLayout(hook_box)
        hook_layout.setContentsMargins(12, 10, 12, 10)
        hook_layout.setSpacing(6)
        hook_title = QLabel("开场钩子", hook_box)
        hook_title.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
        hook_text = QLabel(script.opening_hook, hook_box)
        hook_text.setStyleSheet(label_text_style(tone="muted", size_token="font.size.sm"))
        _call(hook_text, "setWordWrap", True)
        hook_layout.addWidget(hook_title)
        hook_layout.addWidget(hook_text)
        layout.addWidget(hook_box)

        body = QLabel(script.script_text, frame)
        body.setStyleSheet(label_text_style(size_token="font.size.sm", line_height="1.7"))
        _call(body, "setWordWrap", True)
        layout.addWidget(body)

        meta = QWidget(frame)
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)
        meta_layout.addWidget(StatsBadge("结构", script.structure_label, icon="◈", tone="brand", parent=meta))
        meta_layout.addWidget(StatsBadge("采用建议", script.adoption_hint, icon="▲", tone="success", parent=meta))
        meta_layout.addStretch(1)
        layout.addWidget(meta)

        tags_row = QWidget(frame)
        tags_layout = QHBoxLayout(tags_row)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(6)
        for tag in script.tags:
            tags_layout.addWidget(TagChip(tag, tone="neutral", parent=tags_row))
        for point in script.selling_points:
            tags_layout.addWidget(TagChip(point, tone="brand", parent=tags_row))
        tags_layout.addStretch(1)
        layout.addWidget(tags_row)

        cta = QLabel(f"收口 CTA：{script.cta}", frame)
        cta.setStyleSheet(label_text_style(tone="accent", size_token="font.size.sm", weight_token="font.weight.bold"))
        _call(cta, "setWordWrap", True)
        layout.addWidget(cta)
        return frame

    def _copy_script(self, script: ScriptTemplate) -> None:
        self._selected_script_title = script.title
        self._update_selected_summary(script)
        if self._streaming_output is not None:
            self._streaming_output.clear()
            self._streaming_output.append_chunk(f"已复制脚本：{script.title}\n\n{script.script_text}\n\nCTA：{script.cta}")
            self._streaming_output.set_token_usage(120, 260)
        self._render_script_cards()

    def _edit_script(self, script: ScriptTemplate) -> None:
        self._selected_script_title = script.title
        if self._angle_input is not None:
            self._angle_input.setText(script.structure_label)
        if self._product_info_input is not None:
            self._product_info_input.setPlainText(
                f"{self._product_info_input.toPlainText()}\n\n【待编辑脚本】\n标题：{script.title}\n钩子：{script.opening_hook}\nCTA：{script.cta}"
            )
        self._update_selected_summary(script)
        self._render_script_cards()

    def _save_script(self, script: ScriptTemplate) -> None:
        self._selected_script_title = script.title
        self._prepend_history(script, status="已保存")
        self._update_selected_summary(script)
        self._render_script_cards()

    def _prepend_history(self, script: ScriptTemplate, status: str = "已采用") -> None:
        record = HistoryRecord(
            created_at="刚刚",
            product_name=self._current_product_name(),
            script_type=script.script_type,
            duration=script.estimated_duration,
            quality_score=script.quality_score,
            status=status,
            author="当前工作台",
            note=script.title,
        )
        self._records = [record, *self._records[:11]]
        self._refresh_history_table()

    def _refresh_history_table(self) -> None:
        if self._history_table is None:
            return
        keyword = self._history_keyword
        rows: list[tuple[str, ...]] = []
        total = 0
        for item in self._records:
            haystack = " ".join((item.created_at, item.product_name, item.script_type, item.status, item.author, item.note)).lower()
            if keyword and keyword not in haystack:
                continue
            total += 1
            rows.append((item.created_at, item.product_name, item.script_type, item.duration, item.quality_score, item.status, item.author, item.note))
        self._history_table.set_rows(rows)
        if self._history_count_label is not None:
            self._history_count_label.setText(f"共 {total} 条记录")

    def _on_history_row_selected(self, row_index: int) -> None:
        filtered: list[HistoryRecord] = []
        keyword = self._history_keyword
        for item in self._records:
            haystack = " ".join((item.created_at, item.product_name, item.script_type, item.status, item.author, item.note)).lower()
            if keyword and keyword not in haystack:
                continue
            filtered.append(item)
        if not (0 <= row_index < len(filtered)):
            return
        record = filtered[row_index]
        if self._product_name_input is not None:
            self._product_name_input.setText(record.product_name)
        matching = [index for index, profile in enumerate(self._profiles) if profile.name == record.script_type]
        if matching and self._type_tabs is not None:
            self._type_tabs.set_current(matching[0])
        self._generate_scripts(initial=True)
        if self._streaming_output is not None:
            self._streaming_output.clear()
            self._streaming_output.append_chunk(f"已从历史记录载入：{record.product_name} · {record.script_type}\n备注：{record.note}")
            self._streaming_output.set_token_usage(80, 120)

    def _update_type_summary(self) -> None:
        profile = self._active_profile()
        if self._current_type_summary_label is not None:
            self._current_type_summary_label.setText(f"{profile.name} · {profile.scene}")
        if self._current_type_hint_label is not None:
            self._current_type_hint_label.setText(f"推荐结构：{profile.structure}；节奏建议：{profile.rhythm}")

    def _update_model_summary(self) -> None:
        if self._ai_config_panel is None or self._model_summary_label is None:
            return
        config = self._ai_config_panel.config()
        provider = str(config.get("provider_label", "AI"))
        model = str(config.get("model", "gpt-4o"))
        role = str(config.get("agent_role", "脚本创作者"))
        temperature = config.get("temperature", 0.7)
        top_p = config.get("top_p", 0.9)
        max_tokens = config.get("max_tokens", 2048)
        self._model_summary_label.setText(
            f"{provider} · {model} · {role} · 温度 {temperature} · Top-p {top_p} · 输出上限 {max_tokens} Token"
        )

    def _update_selected_summary(self, script: ScriptTemplate | None) -> None:
        if script is None:
            return
        self._selected_script_title = script.title
        if self._selected_title_label is not None:
            self._selected_title_label.setText(script.title)
        if self._selected_cta_label is not None:
            self._selected_cta_label.setText(f"CTA：{script.cta}")
        if self._selected_score_label is not None:
            self._selected_score_label.setText(f"质量分：{script.quality_score} · 结构：{script.structure_label}")
        if self._selected_hint_label is not None:
            self._selected_hint_label.setText(f"采用建议：{script.adoption_hint}；摘要：{script.summary}")

    def _apply_page_styles(self) -> None:
        palette = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#script_generation_root, QWidget {{
                color: {palette.text};
            }}
            QFrame[variant="card"] {{
                border-radius: {RADIUS_LG}px;
            }}
            QLabel {{
                font-family: {_static_token('font.family.chinese')};
            }}
            QPushButton {{
                min-height: {BUTTON_HEIGHT}px;
            }}
            QTableView {{
                border-radius: {RADIUS_MD}px;
            }}
            """,
        )
        _call(self, "setObjectName", "script_generation_root")


__all__ = ["ScriptGenerationPage"]

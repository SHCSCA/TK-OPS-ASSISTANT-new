# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportGeneralTypeIssues=false, reportAssignmentType=false, reportCallIssue=false, reportUnusedImport=false

from __future__ import annotations

"""任务大厅页面。"""

from dataclasses import dataclass, replace
from typing import Any

from ....core.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ....core.types import RouteId
from ...components import (
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
    TabBar,
    TagChip,
    TaskProgressBar,
    ThemedScrollArea,
)
from ...components.tags import BadgeTone
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_MD,
    RADIUS_LG,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_2XL,
    FilterDropdown,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


ACCENT = _token("brand.primary")
ACCENT_SOFT = _rgba(ACCENT, 0.10)
ACCENT_STRONG = _rgba(ACCENT, 0.18)
SUCCESS = _token("status.success")
WARNING = _token("status.warning")
ERROR = _token("status.error")
INFO = _token("status.info")


@dataclass(frozen=True)
class HallTask:
    """任务大厅任务。"""

    task_id: str
    title: str
    task_type: str
    category: str
    urgency: str
    reward: int
    difficulty: str
    deadline: str
    creator: str
    status: str
    progress: int
    estimated_hours: str
    applicants: int
    submitted_assets: int
    brief: str
    deliverables: tuple[str, ...]
    tags: tuple[str, ...]
    fit_people: tuple[str, ...]
    tone: str
    my_task: bool = False


@dataclass(frozen=True)
class HallSignal:
    """大厅趋势提醒。"""

    title: str
    detail: str
    highlight: str
    tone: str


TASKS: tuple[HallTask, ...] = (
    HallTask(
        task_id="TH-201",
        title="奶油白随行杯 3 镜头种草短视频",
        task_type="短视频脚本",
        category="家居好物",
        urgency="高",
        reward=680,
        difficulty="中",
        deadline="今天 18:00",
        creator="内容中台",
        status="待领取",
        progress=0,
        estimated_hours="2.5 小时",
        applicants=6,
        submitted_assets=0,
        brief="围绕通勤女性使用场景产出 30 秒脚本，重点突出防漏、轻量、桌面出片感。",
        deliverables=("30 秒脚本 2 版", "开场钩子 3 条", "镜头提示 1 份"),
        tags=("通勤党", "防漏", "情绪种草"),
        fit_people=("文案型创作者", "生活方式账号", "短视频剪辑"),
        tone="brand",
    ),
    HallTask(
        task_id="TH-202",
        title="分区收纳箱 教程讲解视频",
        task_type="教程视频",
        category="收纳整理",
        urgency="中",
        reward=820,
        difficulty="中",
        deadline="明天 12:00",
        creator="商品运营组",
        status="待领取",
        progress=0,
        estimated_hours="3 小时",
        applicants=4,
        submitted_assets=0,
        brief="需要输出‘三步整理衣柜’教程内容，适合新手收藏转化，要求步骤清晰、镜头简单易拍。",
        deliverables=("脚本 1 版", "字幕提词 1 份", "封面标题 4 条"),
        tags=("教程讲解", "新手友好", "收藏导向"),
        fit_people=("收纳类账号", "教程型创作者", "字幕剪辑"),
        tone="success",
    ),
    HallTask(
        task_id="TH-203",
        title="静音电动牙刷 对比评测内容",
        task_type="对比评测",
        category="个护电器",
        urgency="高",
        reward=960,
        difficulty="高",
        deadline="今天 21:00",
        creator="品牌联动组",
        status="进行中",
        progress=46,
        estimated_hours="4 小时",
        applicants=8,
        submitted_assets=2,
        brief="同条件对比两款牙刷，结论必须清晰，避免夸大功效，重点看刷感、噪音、续航体验。",
        deliverables=("对比口播 1 版", "参数对照表 1 份", "评论区回复模板 5 条"),
        tags=("同条件测试", "理性种草", "高客单"),
        fit_people=("测评型账号", "个护创作者", "表格整理"),
        tone="warning",
        my_task=True,
    ),
    HallTask(
        task_id="TH-204",
        title="桌面补光灯 开箱测评脚本",
        task_type="开箱测评",
        category="办公数码",
        urgency="中",
        reward=740,
        difficulty="中",
        deadline="后天 16:00",
        creator="直播素材组",
        status="待领取",
        progress=0,
        estimated_hours="2 小时",
        applicants=5,
        submitted_assets=0,
        brief="强调桌面拍摄氛围和肤色表现，不做专业摄影参数堆砌，重在上手体验。",
        deliverables=("开箱测评脚本", "镜头分镜 1 份", "标题推荐 3 条"),
        tags=("桌搭", "开箱", "氛围感"),
        fit_people=("数码测评", "桌搭内容", "摄影新手"),
        tone="info",
    ),
    HallTask(
        task_id="TH-205",
        title="香氛洗衣凝珠 生活流剧情短片",
        task_type="剧情短片",
        category="日化清洁",
        urgency="中",
        reward=1080,
        difficulty="高",
        deadline="明天 20:00",
        creator="品牌创意组",
        status="进行中",
        progress=72,
        estimated_hours="5 小时",
        applicants=7,
        submitted_assets=5,
        brief="用‘加班回家情绪差’的生活片段做反转，洗后香味和治愈感是重点，不出现夸张承诺。",
        deliverables=("剧情脚本 1 版", "台词 1 套", "封面文案 2 条"),
        tags=("情绪价值", "生活流", "反转"),
        fit_people=("出镜型创作者", "剧情脚本", "情绪表达"),
        tone="brand",
        my_task=True,
    ),
    HallTask(
        task_id="TH-206",
        title="磁吸车载支架 15 秒转化视频",
        task_type="短视频脚本",
        category="车载用品",
        urgency="高",
        reward=560,
        difficulty="低",
        deadline="今天 23:00",
        creator="转化提效组",
        status="待领取",
        progress=0,
        estimated_hours="1.5 小时",
        applicants=9,
        submitted_assets=0,
        brief="用最短节奏呈现‘装上即稳’的体验，适合强利益点直给，不要铺垫太长。",
        deliverables=("15 秒脚本", "字幕版 1 套"),
        tags=("短时长", "强转化", "车载场景"),
        fit_people=("转化型文案", "快节奏剪辑", "车品内容"),
        tone="error",
    ),
    HallTask(
        task_id="TH-207",
        title="折叠脏衣篮 达人教程合作稿",
        task_type="教程视频",
        category="居家收纳",
        urgency="低",
        reward=880,
        difficulty="中",
        deadline="3 天后 18:00",
        creator="达人合作组",
        status="已完成",
        progress=100,
        estimated_hours="3.5 小时",
        applicants=3,
        submitted_assets=8,
        brief="面向达人合作，需要结构清楚、语气自然，适合‘整理前后差别很大’的展示路线。",
        deliverables=("达人口播脚本", "拍摄提示卡 1 份", "评论区互动词 8 条"),
        tags=("达人合作", "前后对比", "整理感"),
        fit_people=("达人商务", "居家内容", "教程表达"),
        tone="success",
        my_task=True,
    ),
    HallTask(
        task_id="TH-208",
        title="便当盒 午餐场景图文脚本",
        task_type="图文内容",
        category="厨房用品",
        urgency="低",
        reward=420,
        difficulty="低",
        deadline="2 天后 15:00",
        creator="种草组",
        status="待领取",
        progress=0,
        estimated_hours="1 小时",
        applicants=2,
        submitted_assets=0,
        brief="需要轻量图文脚本，重点说容量分区、通勤带饭方便，适合收藏和转发。",
        deliverables=("图文脚本 1 版", "标题 5 条"),
        tags=("带饭党", "图文", "轻种草"),
        fit_people=("图文写手", "厨房内容", "午餐场景"),
        tone="info",
    ),
    HallTask(
        task_id="TH-209",
        title="护发精油 对比评测脚本",
        task_type="对比评测",
        category="美护个护",
        urgency="中",
        reward=990,
        difficulty="高",
        deadline="明天 17:30",
        creator="美护内容组",
        status="待领取",
        progress=0,
        estimated_hours="4 小时",
        applicants=10,
        submitted_assets=0,
        brief="对比使用前后毛躁度和顺滑度，需要给出适合人群建议，不走夸张路线。",
        deliverables=("评测脚本", "镜头标记 1 套", "标题 4 条"),
        tags=("毛躁对比", "实测", "人群建议"),
        fit_people=("美护测评", "出镜讲解", "剪辑对比"),
        tone="warning",
    ),
    HallTask(
        task_id="TH-210",
        title="旅行收纳袋 开箱 + 教程混合稿",
        task_type="混合内容",
        category="旅行收纳",
        urgency="中",
        reward=860,
        difficulty="中",
        deadline="后天 20:30",
        creator="内容策略组",
        status="进行中",
        progress=58,
        estimated_hours="3 小时",
        applicants=6,
        submitted_assets=3,
        brief="前半段开箱建立质感，后半段做分区打包演示，适合节前旅行主题。",
        deliverables=("混合脚本 1 版", "镜头拆解 1 份", "打包顺序清单"),
        tags=("旅行", "开箱", "教程"),
        fit_people=("收纳博主", "节日节点内容", "脚本策划"),
        tone="brand",
        my_task=True,
    ),
)


HALL_SIGNALS: tuple[HallSignal, ...] = (
    HallSignal("高佣任务正在集中在对比评测", "过去 24 小时高于 900 元的任务里，对比评测占比最高，且截止时间更集中。", "优先补充同条件测试与结论句模板。", "brand"),
    HallSignal("教程类任务收藏潜力更高", "教程讲解与整理类内容在冷启动阶段更容易拉起保存数据。", "建议优先领取可拆步骤的实用型任务。", "success"),
    HallSignal("剧情类需求在增长", "品牌组开始偏好生活流反转内容，但对人物台词和节奏要求更高。", "适合有出镜经验的创作者接单。", "warning"),
)


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


def _frame_style(*, highlight: bool = False, dashed: bool = False) -> str:
    """局部卡片样式。"""

    border = ACCENT if highlight else "palette(midlight)"
    border_style = "dashed" if dashed else "solid"
    background = ACCENT_SOFT if highlight else "palette(base)"
    return f"""
        QFrame {{
            background: {background};
            border: 1px {border_style} {border};
            border-radius: 14px;
        }}
        QLabel {{
            background: transparent;
        }}
        QPushButton {{
            border-radius: 10px;
        }}
    """


def _title_label_style() -> str:
    """标题文案样式。"""

    return "color: palette(text); background: transparent; font-size: 16px; font-weight: 700;"


def _muted_label_style() -> str:
    """辅助文案样式。"""

    return "color: palette(mid); background: transparent; font-size: 12px;"


def _section_hint_style() -> str:
    """强调文案样式。"""

    return f"color: {ACCENT}; background: transparent; font-size: 12px; font-weight: 700;"


class TaskHallPage(BasePage):
    """内容创作任务大厅。"""

    default_route_id = RouteId("task_hall")
    default_display_name = "任务大厅"
    default_icon_name = "dashboard_customize"

    def __init__(self, parent: object | None = None):
        self._records: list[HallTask] = list(TASKS)
        self._search_keyword = ""
        self._task_type_filter = "全部"
        self._category_filter = "全部"
        self._urgency_filter = "全部"
        self._reward_filter = "全部"
        self._active_tab_index = 0
        self._selected_task_id = TASKS[0].task_id
        self._task_cards_host: QWidget | None = None
        self._task_cards_layout: QVBoxLayout | None = None
        self._my_task_host: QWidget | None = None
        self._my_task_layout: QVBoxLayout | None = None
        self._my_task_table: DataTable | None = None
        self._hall_tabs: TabBar | None = None
        self._task_type_dropdown: FilterDropdown | None = None
        self._category_dropdown: FilterDropdown | None = None
        self._urgency_dropdown: FilterDropdown | None = None
        self._reward_dropdown: FilterDropdown | None = None
        self._task_count_label: QLabel | None = None
        self._detail_title_label: QLabel | None = None
        self._detail_summary_label: QLabel | None = None
        self._detail_reward_label: QLabel | None = None
        self._detail_deadline_label: QLabel | None = None
        self._detail_creator_label: QLabel | None = None
        self._detail_progress: TaskProgressBar | None = None
        self._detail_metrics_host: QWidget | None = None
        self._detail_metrics_layout: QVBoxLayout | None = None
        self._detail_deliverables_host: QWidget | None = None
        self._detail_deliverables_layout: QVBoxLayout | None = None
        self._detail_tags_host: QWidget | None = None
        self._detail_tags_layout: QHBoxLayout | None = None
        self._task_action_label: QLabel | None = None
        super().__init__(parent=parent)

    def setup_ui(self) -> None:
        container = PageContainer(
            title="任务大厅",
            description="面向内容创作团队的任务协同中心，支持筛选领取、进度追踪与任务详情联动。",
            actions=[PrimaryButton("发布任务", self, icon_text="＋"), IconButton("⋯", "更多操作", self)],
        )
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(container)

        scroll = ThemedScrollArea(container)
        scroll.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll.content_layout.setSpacing(20)
        container.add_widget(scroll)

        scroll.add_widget(self._build_overview_section())
        scroll.add_widget(self._build_signal_section())
        scroll.add_widget(self._build_filters_section())
        scroll.add_widget(self._build_hall_section())
        scroll.add_widget(self._build_footer_section())

        self._apply_page_styles()
        self._bind_interactions()
        self._refresh_all_views()

    def _build_overview_section(self) -> QWidget:
        section = ContentSection("任务大厅概览", icon="✦", parent=self)

        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(8)
        badge_row.addWidget(StatusBadge("协作状态正常", tone="success", parent=section))
        badge_row.addWidget(StatusBadge("高佣任务较多", tone="brand", parent=section))
        badge_row.addWidget(StatusBadge("今晚截止任务 3 个", tone="warning", parent=section))
        badge_row.addStretch(1)
        section.content_layout.addLayout(badge_row)

        kpi_row = QHBoxLayout()
        kpi_row.setContentsMargins(0, 0, 0, 0)
        kpi_row.setSpacing(12)
        kpi_row.addWidget(KPICard(title="待领取任务", value="6", trend="up", percentage="+2", caption="高于昨日", sparkline_data=[2, 3, 4, 4, 5, 5, 6], parent=section))
        kpi_row.addWidget(KPICard(title="进行中", value="3", trend="flat", percentage="稳定", caption="当前协作中", sparkline_data=[2, 3, 3, 3, 4, 3, 3], parent=section))
        kpi_row.addWidget(KPICard(title="已完成", value="1", trend="up", percentage="本周累计 14", caption="可继续复用", sparkline_data=[7, 8, 9, 10, 12, 13, 14], parent=section))
        kpi_row.addWidget(KPICard(title="总佣金", value="¥7,990", trend="up", percentage="+18%", caption="当前任务池", sparkline_data=[4200, 4880, 5360, 5980, 6640, 7210, 7990], parent=section))
        section.content_layout.addLayout(kpi_row)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(12)
        insight = InfoCard(
            title="今日协作建议",
            description="如果团队里有人擅长对比评测与结论型口播，建议优先领取高佣的测试任务；若需要快速补量，教程类任务更适合短时间出稿。",
            icon="◎",
            action_text="查看推荐分配",
            parent=section,
        )
        bottom.addWidget(insight, 2)
        stats_box = QWidget(section)
        stats_layout = QVBoxLayout(stats_box)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        stats_layout.addWidget(StatsBadge("平均响应", "12 分钟", icon="◷", tone="info", parent=stats_box))
        stats_layout.addWidget(StatsBadge("高优先级", "3 个", icon="▲", tone="warning", parent=stats_box))
        stats_layout.addWidget(StatsBadge("可复用率", "71%", icon="◎", tone="success", parent=stats_box))
        bottom.addWidget(stats_box, 1)
        section.content_layout.addLayout(bottom)
        return section

    def _build_signal_section(self) -> QWidget:
        section = ContentSection("任务趋势提示", icon="◈", parent=self)
        for signal in HALL_SIGNALS:
            card = QFrame(section)
            card.setStyleSheet(_frame_style(highlight=signal.tone == "brand"))
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 14, 16, 14)
            layout.setSpacing(6)
            title = QLabel(signal.title, card)
            title.setStyleSheet(_title_label_style())
            detail = QLabel(signal.detail, card)
            detail.setStyleSheet(_muted_label_style())
            _call(detail, "setWordWrap", True)
            highlight = QLabel(signal.highlight, card)
            highlight.setStyleSheet(_section_hint_style())
            _call(highlight, "setWordWrap", True)
            layout.addWidget(title)
            layout.addWidget(detail)
            layout.addWidget(highlight)
            section.content_layout.addWidget(card)
        return section

    def _build_filters_section(self) -> QWidget:
        section = ContentSection("筛选与检索", icon="⌕", parent=self)
        intro = QHBoxLayout()
        intro.setContentsMargins(0, 0, 0, 0)
        intro.setSpacing(12)
        intro_copy = QWidget(section)
        intro_copy_layout = QVBoxLayout(intro_copy)
        intro_copy_layout.setContentsMargins(0, 0, 0, 0)
        intro_copy_layout.setSpacing(4)
        title = QLabel("任务筛选工具栏", intro_copy)
        title.setStyleSheet(_title_label_style())
        subtitle = QLabel("按任务类型、类目、紧急程度和佣金范围快速收缩列表，保持与内容页一致的头部筛选节奏。", intro_copy)
        subtitle.setStyleSheet(_muted_label_style())
        _call(subtitle, "setWordWrap", True)
        intro_copy_layout.addWidget(title)
        intro_copy_layout.addWidget(subtitle)

        intro_badges = QWidget(section)
        intro_badges_layout = QHBoxLayout(intro_badges)
        intro_badges_layout.setContentsMargins(0, 0, 0, 0)
        intro_badges_layout.setSpacing(8)
        intro_badges_layout.addWidget(StatusBadge("支持组合筛选", tone="info", parent=intro_badges))
        intro_badges_layout.addWidget(StatusBadge("详情联动已开启", tone="brand", parent=intro_badges))
        intro.addWidget(intro_copy, 1)
        intro.addWidget(intro_badges)

        tools = QHBoxLayout()
        tools.setContentsMargins(0, 0, 0, 0)
        tools.setSpacing(12)
        search = SearchBar("搜索任务标题、类目、标签或发布方...", None)
        _connect(search.search_changed, self._on_search_changed)
        tools.addWidget(search, 2)
        self._task_type_dropdown = FilterDropdown("任务类型", ["短视频脚本", "教程视频", "开箱测评", "对比评测", "剧情短片", "图文内容", "混合内容"], include_all=True, parent=None)
        self._category_dropdown = FilterDropdown("类目", ["家居好物", "收纳整理", "个护电器", "办公数码", "日化清洁", "车载用品", "居家收纳", "厨房用品", "美护个护", "旅行收纳"], include_all=True, parent=None)
        self._urgency_dropdown = FilterDropdown("紧急程度", ["高", "中", "低"], include_all=True, parent=None)
        self._reward_dropdown = FilterDropdown("佣金范围", ["500 以下", "500-800", "800-1000", "1000 以上"], include_all=True, parent=None)
        tools.addWidget(self._task_type_dropdown)
        tools.addWidget(self._category_dropdown)
        tools.addWidget(self._urgency_dropdown)
        tools.addWidget(self._reward_dropdown)
        section.content_layout.addLayout(intro)
        section.content_layout.addLayout(tools)
        return section

    def _build_hall_section(self) -> QWidget:
        section = ContentSection("任务池与详情", icon="☰", parent=self)
        split = SplitPanel("horizontal", split_ratio=(0.60, 0.40), minimum_sizes=(560, 420), parent=section)
        split.set_widgets(self._build_list_panel(), self._build_detail_panel())
        section.content_layout.addWidget(split)
        return section

    def _build_list_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        head = QFrame(panel)
        head.setStyleSheet(_frame_style(highlight=True))
        head_layout = QHBoxLayout(head)
        head_layout.setContentsMargins(16, 14, 16, 14)
        head_layout.setSpacing(10)
        title = QLabel("任务列表", head)
        title.setStyleSheet(_title_label_style())
        self._task_count_label = QLabel("共 0 条任务", head)
        self._task_count_label.setStyleSheet(_section_hint_style())
        head_layout.addWidget(title)
        head_layout.addStretch(1)
        head_layout.addWidget(self._task_count_label)
        root.addWidget(head)

        self._hall_tabs = TabBar(panel)
        self._hall_tabs.add_tab("全部任务", self._build_all_tasks_tab())
        self._hall_tabs.add_tab("我的任务", self._build_my_tasks_tab())
        root.addWidget(self._hall_tabs)
        return panel

    def _build_all_tasks_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self._task_cards_host = QWidget(host)
        self._task_cards_layout = QVBoxLayout(self._task_cards_host)
        self._task_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._task_cards_layout.setSpacing(12)
        layout.addWidget(self._task_cards_host)
        return host

    def _build_my_tasks_tab(self) -> QWidget:
        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        summary = QFrame(host)
        summary.setStyleSheet(_frame_style())
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(16, 14, 16, 14)
        summary_layout.setSpacing(10)
        summary_layout.addWidget(StatsBadge("我负责", "4 个", icon="◎", tone="brand", parent=summary))
        summary_layout.addWidget(StatsBadge("平均进度", "69%", icon="▲", tone="success", parent=summary))
        summary_layout.addWidget(StatsBadge("待提交", "2 个", icon="◷", tone="warning", parent=summary))
        summary_layout.addStretch(1)
        layout.addWidget(summary)

        self._my_task_host = QWidget(host)
        self._my_task_layout = QVBoxLayout(self._my_task_host)
        self._my_task_layout.setContentsMargins(0, 0, 0, 0)
        self._my_task_layout.setSpacing(12)
        layout.addWidget(self._my_task_host)

        self._my_task_table = DataTable(
            headers=("任务编号", "标题", "状态", "进度", "截止时间", "佣金"),
            rows=[],
            page_size=5,
            empty_text="暂无我的任务",
            parent=host,
        )
        layout.addWidget(self._my_task_table)
        return host

    def _build_detail_panel(self) -> QWidget:
        panel = QWidget(self)
        root = QVBoxLayout(panel)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        top = QFrame(panel)
        top.setStyleSheet(_frame_style(highlight=True))
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(16, 16, 16, 16)
        top_layout.setSpacing(8)
        self._detail_title_label = QLabel("任务标题", top)
        self._detail_title_label.setStyleSheet(_title_label_style())
        self._detail_summary_label = QLabel("任务摘要", top)
        self._detail_summary_label.setStyleSheet(_muted_label_style())
        _call(self._detail_summary_label, "setWordWrap", True)
        self._task_action_label = QLabel("当前可执行操作将在这里显示。", top)
        self._task_action_label.setStyleSheet(_section_hint_style())
        top_layout.addWidget(self._detail_title_label)
        top_layout.addWidget(self._detail_summary_label)
        top_layout.addWidget(self._task_action_label)
        root.addWidget(top)

        badge_row = QWidget(panel)
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(8)
        self._detail_reward_label = QLabel("佣金：--", badge_row)
        self._detail_deadline_label = QLabel("截止：--", badge_row)
        self._detail_creator_label = QLabel("发布方：--", badge_row)
        for label in (self._detail_reward_label, self._detail_deadline_label, self._detail_creator_label):
            label.setStyleSheet(_section_hint_style())
            badge_layout.addWidget(label)
        badge_layout.addStretch(1)
        root.addWidget(badge_row)

        progress_box = QFrame(panel)
        progress_box.setStyleSheet(_frame_style())
        progress_layout = QVBoxLayout(progress_box)
        progress_layout.setContentsMargins(16, 14, 16, 14)
        progress_layout.setSpacing(8)
        progress_title = QLabel("进度追踪", progress_box)
        progress_title.setStyleSheet(_title_label_style())
        self._detail_progress = TaskProgressBar(0, None)
        progress_layout.addWidget(progress_title)
        progress_layout.addWidget(self._detail_progress)
        root.addWidget(progress_box)

        metrics_box = QFrame(panel)
        metrics_box.setStyleSheet(_frame_style())
        metrics_layout = QVBoxLayout(metrics_box)
        metrics_layout.setContentsMargins(16, 14, 16, 14)
        metrics_layout.setSpacing(10)
        metrics_title = QLabel("任务指标", metrics_box)
        metrics_title.setStyleSheet(_title_label_style())
        metrics_layout.addWidget(metrics_title)
        self._detail_metrics_host = QWidget(metrics_box)
        self._detail_metrics_layout = QVBoxLayout(self._detail_metrics_host)
        self._detail_metrics_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_metrics_layout.setSpacing(10)
        metrics_layout.addWidget(self._detail_metrics_host)
        root.addWidget(metrics_box)

        deliverable_box = QFrame(panel)
        deliverable_box.setStyleSheet(_frame_style())
        deliverable_layout = QVBoxLayout(deliverable_box)
        deliverable_layout.setContentsMargins(16, 14, 16, 14)
        deliverable_layout.setSpacing(10)
        deliverable_title = QLabel("交付物要求", deliverable_box)
        deliverable_title.setStyleSheet(_title_label_style())
        deliverable_layout.addWidget(deliverable_title)
        self._detail_deliverables_host = QWidget(deliverable_box)
        self._detail_deliverables_layout = QVBoxLayout(self._detail_deliverables_host)
        self._detail_deliverables_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_deliverables_layout.setSpacing(10)
        deliverable_layout.addWidget(self._detail_deliverables_host)
        root.addWidget(deliverable_box)

        tag_box = QFrame(panel)
        tag_box.setStyleSheet(_frame_style())
        tag_layout = QVBoxLayout(tag_box)
        tag_layout.setContentsMargins(16, 14, 16, 14)
        tag_layout.setSpacing(10)
        tag_title = QLabel("适配标签", tag_box)
        tag_title.setStyleSheet(_title_label_style())
        tag_layout.addWidget(tag_title)
        tag_row = QWidget(tag_box)
        self._detail_tags_layout = QHBoxLayout(tag_row)
        self._detail_tags_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_tags_layout.setSpacing(6)
        tag_layout.addWidget(tag_row)
        root.addWidget(tag_box)

        action_row = QWidget(panel)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        claim_button = PrimaryButton("领取任务", panel, icon_text="✓")
        start_button = SecondaryButton("开始执行", panel, icon_text="▶")
        complete_button = SecondaryButton("标记完成", panel, icon_text="◎")
        _connect(claim_button.clicked, self._claim_selected_task)
        _connect(start_button.clicked, self._start_selected_task)
        _connect(complete_button.clicked, self._complete_selected_task)
        action_layout.addWidget(claim_button)
        action_layout.addWidget(start_button)
        action_layout.addWidget(complete_button)
        action_layout.addStretch(1)
        root.addWidget(action_row)
        return panel

    def _build_footer_section(self) -> QWidget:
        footer = QWidget(self)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        tip = QLabel("先用筛选定位高匹配任务，再在右侧详情确认交付物与截止时间；高佣任务优先保证结论清晰和交付完整。", footer)
        tip.setStyleSheet(_muted_label_style())
        _call(tip, "setWordWrap", True)
        fab = FloatingActionButton("✚", "新建协作任务", footer)
        layout.addWidget(tip, 1)
        layout.addStretch(1)
        layout.addWidget(fab)
        return footer

    def _bind_interactions(self) -> None:
        if self._hall_tabs is not None:
            _connect(self._hall_tabs.tab_changed, self._on_tab_changed)
        if self._task_type_dropdown is not None:
            _connect(self._task_type_dropdown.filter_changed, self._on_task_type_changed)
        if self._category_dropdown is not None:
            _connect(self._category_dropdown.filter_changed, self._on_category_changed)
        if self._urgency_dropdown is not None:
            _connect(self._urgency_dropdown.filter_changed, self._on_urgency_changed)
        if self._reward_dropdown is not None:
            _connect(self._reward_dropdown.filter_changed, self._on_reward_changed)
        if self._my_task_table is not None:
            _connect(self._my_task_table.row_selected, self._on_my_task_table_selected)
            _connect(self._my_task_table.row_double_clicked, self._on_my_task_table_selected)

    def _refresh_all_views(self) -> None:
        self._sync_selected_task()
        self._render_task_cards()
        self._render_my_tasks()
        self._refresh_my_task_table()
        self._refresh_detail_panel()

    def _sync_selected_task(self) -> None:
        """保证当前选中任务在当前上下文中有效。"""

        current_pool = self._my_tasks() if self._active_tab_index == 1 else self._filtered_tasks()
        if not current_pool:
            return
        current_ids = {item.task_id for item in current_pool}
        if self._selected_task_id not in current_ids:
            self._selected_task_id = current_pool[0].task_id

    def _selected_task(self) -> HallTask:
        if not self._records:
            raise ValueError("任务列表为空")
        for item in self._records:
            if item.task_id == self._selected_task_id:
                return item
        return self._records[0]

    def _detail_task(self) -> HallTask | None:
        """返回当前详情面板应展示的任务。"""

        pool = self._my_tasks() if self._active_tab_index == 1 else self._filtered_tasks()
        if not pool:
            return None
        return next((item for item in pool if item.task_id == self._selected_task_id), pool[0])

    def _filtered_tasks(self) -> list[HallTask]:
        results: list[HallTask] = []
        keyword = self._search_keyword
        for item in self._records:
            haystack = " ".join((item.title, item.task_type, item.category, item.creator, item.brief, " ".join(item.tags))).lower()
            if keyword and keyword not in haystack:
                continue
            if self._task_type_filter != "全部" and item.task_type != self._task_type_filter:
                continue
            if self._category_filter != "全部" and item.category != self._category_filter:
                continue
            if self._urgency_filter != "全部" and item.urgency != self._urgency_filter:
                continue
            if self._reward_filter != "全部" and not self._match_reward(item.reward):
                continue
            results.append(item)
        return results

    def _my_tasks(self) -> list[HallTask]:
        return [item for item in self._records if item.my_task]

    def _match_reward(self, reward: int) -> bool:
        if self._reward_filter == "500 以下":
            return reward < 500
        if self._reward_filter == "500-800":
            return 500 <= reward <= 800
        if self._reward_filter == "800-1000":
            return 800 <= reward <= 1000
        if self._reward_filter == "1000 以上":
            return reward > 1000
        return True

    def _on_tab_changed(self, index: int) -> None:
        self._active_tab_index = index
        self._refresh_detail_panel()

    def _on_search_changed(self, keyword: str) -> None:
        self._search_keyword = keyword.strip().lower()
        self._render_task_cards()
        self._refresh_detail_panel()

    def _on_task_type_changed(self, value: str) -> None:
        self._task_type_filter = value
        self._render_task_cards()
        self._refresh_detail_panel()

    def _on_category_changed(self, value: str) -> None:
        self._category_filter = value
        self._render_task_cards()
        self._refresh_detail_panel()

    def _on_urgency_changed(self, value: str) -> None:
        self._urgency_filter = value
        self._render_task_cards()
        self._refresh_detail_panel()

    def _on_reward_changed(self, value: str) -> None:
        self._reward_filter = value
        self._render_task_cards()
        self._refresh_detail_panel()

    def _render_task_cards(self) -> None:
        if self._task_cards_layout is None:
            return
        _clear_layout(self._task_cards_layout)
        tasks = self._filtered_tasks()
        if self._task_count_label is not None:
            self._task_count_label.setText(f"共 {len(tasks)} 条任务")
        if not tasks:
            empty = QFrame(self)
            empty.setStyleSheet(_frame_style(dashed=True))
            layout = QVBoxLayout(empty)
            layout.setContentsMargins(18, 18, 18, 18)
            layout.setSpacing(8)
            title = QLabel("当前没有符合条件的任务", empty)
            title.setStyleSheet(_title_label_style())
            detail = QLabel("试试放宽类目、佣金或紧急程度筛选。", empty)
            detail.setStyleSheet(_muted_label_style())
            _call(detail, "setWordWrap", True)
            layout.addWidget(title)
            layout.addWidget(detail)
            self._task_cards_layout.addWidget(empty)
            self._task_cards_layout.addStretch(1)
            return
        if self._selected_task_id not in {item.task_id for item in tasks}:
            self._selected_task_id = tasks[0].task_id
        for item in tasks:
            self._task_cards_layout.addWidget(self._build_task_card(item))

    def _build_task_card(self, task: HallTask) -> QWidget:
        frame = QFrame(self)
        frame.setStyleSheet(_frame_style(highlight=task.task_id == self._selected_task_id))
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        title = QLabel(task.title, frame)
        title.setStyleSheet(_title_label_style())
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(StatusBadge(task.status, tone=_tone_badge(task.tone), parent=frame))
        layout.addLayout(top)

        meta = QWidget(frame)
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)
        meta_layout.addWidget(StatusBadge(task.task_type, tone="brand", parent=meta))
        meta_layout.addWidget(StatusBadge(task.category, tone="info", parent=meta))
        meta_layout.addWidget(StatusBadge(f"{task.urgency}优先", tone="warning" if task.urgency == "高" else "neutral", parent=meta))
        meta_layout.addStretch(1)
        layout.addWidget(meta)

        brief = QLabel(task.brief, frame)
        brief.setStyleSheet(_muted_label_style())
        _call(brief, "setWordWrap", True)
        layout.addWidget(brief)

        info_row = QWidget(frame)
        info_layout = QHBoxLayout(info_row)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)
        info_layout.addWidget(StatsBadge("佣金", f"¥{task.reward}", icon="¥", tone="success", parent=info_row))
        info_layout.addWidget(StatsBadge("难度", task.difficulty, icon="◈", tone="info", parent=info_row))
        info_layout.addWidget(StatsBadge("截止", task.deadline, icon="◷", tone="warning", parent=info_row))
        info_layout.addStretch(1)
        layout.addWidget(info_row)

        progress_box = QFrame(frame)
        progress_box.setStyleSheet(_frame_style(dashed=True))
        progress_layout = QVBoxLayout(progress_box)
        progress_layout.setContentsMargins(12, 10, 12, 10)
        progress_layout.setSpacing(6)
        progress_layout.addWidget(QLabel("任务进度", progress_box))
        progress_bar = TaskProgressBar(task.progress, None)
        progress_layout.addWidget(progress_bar)
        layout.addWidget(progress_box)

        tags_row = QWidget(frame)
        tags_layout = QHBoxLayout(tags_row)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(6)
        for tag in task.tags:
            tags_layout.addWidget(TagChip(tag, tone="neutral", parent=tags_row))
        tags_layout.addStretch(1)
        layout.addWidget(tags_row)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        select_button = SecondaryButton("查看详情", frame, icon_text="⌕")
        quick_button = PrimaryButton("立即处理" if task.my_task else "领取任务", frame, icon_text="✓")
        _connect(select_button.clicked, lambda item=task: self._select_task(item.task_id))
        _connect(quick_button.clicked, lambda item=task: self._quick_action(item.task_id))
        action_row.addWidget(select_button)
        action_row.addWidget(quick_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)
        return frame

    def _render_my_tasks(self) -> None:
        if self._my_task_layout is None:
            return
        _clear_layout(self._my_task_layout)
        tasks = self._my_tasks()
        if not tasks:
            empty = QFrame(self)
            empty.setStyleSheet(_frame_style(dashed=True))
            layout = QVBoxLayout(empty)
            layout.setContentsMargins(18, 18, 18, 18)
            layout.setSpacing(8)
            title = QLabel("你还没有领取任务", empty)
            title.setStyleSheet(_title_label_style())
            detail = QLabel("可以先在全部任务里领取高匹配任务，再回到这里追踪进度。", empty)
            detail.setStyleSheet(_muted_label_style())
            _call(detail, "setWordWrap", True)
            layout.addWidget(title)
            layout.addWidget(detail)
            self._my_task_layout.addWidget(empty)
            self._my_task_layout.addStretch(1)
            return
        for task in tasks:
            card = QFrame(self)
            card.setStyleSheet(_frame_style(highlight=task.task_id == self._selected_task_id))
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(10)
            head = QHBoxLayout()
            head.setContentsMargins(0, 0, 0, 0)
            head.setSpacing(8)
            title = QLabel(task.title, card)
            title.setStyleSheet(_title_label_style())
            head.addWidget(title)
            head.addStretch(1)
            head.addWidget(StatusBadge(task.status, tone=_tone_badge(task.tone), parent=card))
            layout.addLayout(head)
            detail = QLabel(f"截止：{task.deadline} · 预计耗时：{task.estimated_hours} · 已提交素材：{task.submitted_assets}", card)
            detail.setStyleSheet(_muted_label_style())
            _call(detail, "setWordWrap", True)
            layout.addWidget(detail)
            layout.addWidget(TaskProgressBar(task.progress, None))
            controls = QHBoxLayout()
            controls.setContentsMargins(0, 0, 0, 0)
            controls.setSpacing(8)
            view_button = SecondaryButton("定位详情", card, icon_text="↳")
            step_button = PrimaryButton("推进进度", card, icon_text="▲")
            _connect(view_button.clicked, lambda item=task: self._select_task(item.task_id, switch_to_my=True))
            _connect(step_button.clicked, lambda item=task: self._advance_task(item.task_id))
            controls.addWidget(view_button)
            controls.addWidget(step_button)
            controls.addStretch(1)
            layout.addLayout(controls)
            self._my_task_layout.addWidget(card)

    def _refresh_my_task_table(self) -> None:
        if self._my_task_table is None:
            return
        rows = [(item.task_id, item.title, item.status, f"{item.progress}%", item.deadline, f"¥{item.reward}") for item in self._my_tasks()]
        self._my_task_table.set_rows(rows)

    def _refresh_detail_panel(self) -> None:
        task = self._detail_task()
        if task is None:
            if self._detail_title_label is not None:
                self._detail_title_label.setText("当前没有可查看的任务")
            if self._detail_summary_label is not None:
                self._detail_summary_label.setText("可调整筛选条件，或切换到“我的任务”查看已领取内容。")
            if self._detail_reward_label is not None:
                self._detail_reward_label.setText("佣金：--")
            if self._detail_deadline_label is not None:
                self._detail_deadline_label.setText("截止：--")
            if self._detail_creator_label is not None:
                self._detail_creator_label.setText("发布方：--")
            if self._detail_progress is not None:
                self._detail_progress.set_progress(0)
            if self._task_action_label is not None:
                self._task_action_label.setText("建议动作：放宽筛选范围，优先查看高匹配或临近截止任务。")
            self._render_detail_metrics_empty()
            self._render_detail_deliverables_empty()
            self._render_detail_tags_empty()
            return
        if self._detail_title_label is not None:
            self._detail_title_label.setText(task.title)
        if self._detail_summary_label is not None:
            self._detail_summary_label.setText(task.brief)
        if self._detail_reward_label is not None:
            self._detail_reward_label.setText(f"佣金：¥{task.reward}")
        if self._detail_deadline_label is not None:
            self._detail_deadline_label.setText(f"截止：{task.deadline}")
        if self._detail_creator_label is not None:
            self._detail_creator_label.setText(f"发布方：{task.creator}")
        if self._detail_progress is not None:
            self._detail_progress.set_progress(task.progress)
        if self._task_action_label is not None:
            if task.status == "待领取":
                self._task_action_label.setText("建议动作：先确认交付物与截止时间，再领取任务。")
            elif task.status == "进行中":
                self._task_action_label.setText("建议动作：优先完成核心交付物，再补标题与评论区素材。")
            else:
                self._task_action_label.setText("建议动作：已完成任务可复盘并沉淀模板。")
        self._render_detail_metrics(task)
        self._render_detail_deliverables(task)
        self._render_detail_tags(task)

    def _render_detail_metrics_empty(self) -> None:
        if self._detail_metrics_layout is None:
            return
        _clear_layout(self._detail_metrics_layout)
        empty = QFrame(self)
        empty.setStyleSheet(_frame_style(dashed=True))
        layout = QVBoxLayout(empty)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        title = QLabel("暂无任务指标", empty)
        title.setStyleSheet(_title_label_style())
        detail = QLabel("当列表中存在可选任务时，这里会显示难度、耗时、报名人数与提交数量。", empty)
        detail.setStyleSheet(_muted_label_style())
        _call(detail, "setWordWrap", True)
        layout.addWidget(title)
        layout.addWidget(detail)
        self._detail_metrics_layout.addWidget(empty)

    def _render_detail_deliverables_empty(self) -> None:
        if self._detail_deliverables_layout is None:
            return
        _clear_layout(self._detail_deliverables_layout)
        empty = QFrame(self)
        empty.setStyleSheet(_frame_style(dashed=True))
        layout = QVBoxLayout(empty)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        title = QLabel("暂无交付物要求", empty)
        title.setStyleSheet(_section_hint_style())
        detail = QLabel("选择任务后，这里会列出脚本、标题、封面或评论区等交付项。", empty)
        detail.setStyleSheet(_muted_label_style())
        _call(detail, "setWordWrap", True)
        layout.addWidget(title)
        layout.addWidget(detail)
        self._detail_deliverables_layout.addWidget(empty)

    def _render_detail_tags_empty(self) -> None:
        if self._detail_tags_layout is None:
            return
        _clear_layout(self._detail_tags_layout)
        self._detail_tags_layout.addWidget(TagChip("暂无标签", tone="neutral", parent=self))
        self._detail_tags_layout.addStretch(1)

    def _render_detail_metrics(self, task: HallTask) -> None:
        if self._detail_metrics_layout is None:
            return
        _clear_layout(self._detail_metrics_layout)
        for label, value, tone in (
            ("任务类型", task.task_type, "brand"),
            ("难度等级", task.difficulty, "info"),
            ("预计耗时", task.estimated_hours, "warning"),
            ("报名人数", str(task.applicants), "neutral"),
            ("已交素材", str(task.submitted_assets), "success"),
        ):
            row = QFrame(self)
            row.setStyleSheet(_frame_style(dashed=True))
            layout = QHBoxLayout(row)
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(10)
            layout.addWidget(StatusBadge(label, tone=_tone_badge(tone), parent=row))
            value_label = QLabel(value, row)
            value_label.setStyleSheet(_title_label_style())
            layout.addWidget(value_label)
            layout.addStretch(1)
            self._detail_metrics_layout.addWidget(row)

    def _render_detail_deliverables(self, task: HallTask) -> None:
        if self._detail_deliverables_layout is None:
            return
        _clear_layout(self._detail_deliverables_layout)
        for deliverable in task.deliverables:
            row = QFrame(self)
            row.setStyleSheet(_frame_style(dashed=True))
            layout = QHBoxLayout(row)
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(8)
            layout.addWidget(StatusBadge("交付", tone="brand", parent=row))
            label = QLabel(deliverable, row)
            label.setStyleSheet(_muted_label_style())
            _call(label, "setWordWrap", True)
            layout.addWidget(label, 1)
            self._detail_deliverables_layout.addWidget(row)
        fit = QFrame(self)
        fit.setStyleSheet(_frame_style())
        fit_layout = QVBoxLayout(fit)
        fit_layout.setContentsMargins(12, 10, 12, 10)
        fit_layout.setSpacing(6)
        title = QLabel("更适合谁来做", fit)
        title.setStyleSheet(_section_hint_style())
        fit_layout.addWidget(title)
        for item in task.fit_people:
            label = QLabel(f"• {item}", fit)
            label.setStyleSheet(_muted_label_style())
            fit_layout.addWidget(label)
        self._detail_deliverables_layout.addWidget(fit)

    def _render_detail_tags(self, task: HallTask) -> None:
        if self._detail_tags_layout is None:
            return
        _clear_layout(self._detail_tags_layout)
        for tag in task.tags:
            self._detail_tags_layout.addWidget(TagChip(tag, tone="neutral", parent=self))
        for tag in task.fit_people:
            self._detail_tags_layout.addWidget(TagChip(tag, tone="brand", parent=self))
        self._detail_tags_layout.addStretch(1)

    def _select_task(self, task_id: str, switch_to_my: bool = False) -> None:
        self._selected_task_id = task_id
        if switch_to_my and self._hall_tabs is not None:
            self._hall_tabs.set_current(1)
        self._render_task_cards()
        self._render_my_tasks()
        self._refresh_detail_panel()

    def _quick_action(self, task_id: str) -> None:
        task = next((item for item in self._records if item.task_id == task_id), None)
        if task is None:
            return
        if task.status == "待领取":
            self._claim_task(task_id)
        elif task.status == "进行中":
            self._advance_task(task_id)
        else:
            self._select_task(task_id)

    def _claim_selected_task(self) -> None:
        self._claim_task(self._selected_task_id)

    def _claim_task(self, task_id: str) -> None:
        updated: list[HallTask] = []
        for item in self._records:
            if item.task_id == task_id and item.status == "待领取":
                updated.append(replace(item, status="进行中", progress=12, my_task=True, submitted_assets=1))
            else:
                updated.append(item)
        self._records = updated
        self._selected_task_id = task_id
        self._refresh_all_views()

    def _start_selected_task(self) -> None:
        self._advance_task(self._selected_task_id, step=18)

    def _advance_task(self, task_id: str, step: int = 14) -> None:
        updated: list[HallTask] = []
        for item in self._records:
            if item.task_id == task_id:
                next_progress = min(100, max(item.progress, 12) + step)
                next_status = "已完成" if next_progress >= 100 else "进行中"
                updated.append(replace(item, status=next_status, progress=next_progress, my_task=True, submitted_assets=item.submitted_assets + 1))
            else:
                updated.append(item)
        self._records = updated
        self._selected_task_id = task_id
        self._refresh_all_views()

    def _complete_selected_task(self) -> None:
        updated: list[HallTask] = []
        for item in self._records:
            if item.task_id == self._selected_task_id:
                updated.append(replace(item, status="已完成", progress=100, my_task=True, submitted_assets=max(item.submitted_assets, 8)))
            else:
                updated.append(item)
        self._records = updated
        self._refresh_all_views()

    def _on_my_task_table_selected(self, row_index: int) -> None:
        tasks = self._my_tasks()
        if not (0 <= row_index < len(tasks)):
            return
        self._select_task(tasks[row_index].task_id, switch_to_my=True)

    def _apply_page_styles(self) -> None:
        palette = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#task_hall_root, QWidget {{
                color: {palette.text};
            }}
            QWidget#task_hall_root {{
                background-color: {palette.surface_alt};
            }}
            QLabel {{
                font-family: {_static_token('font.family.chinese')};
            }}
            QPushButton {{
                min-height: {BUTTON_HEIGHT}px;
            }}
            QFrame[variant="card"] {{
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )
        _call(self, "setObjectName", "task_hall_root")


__all__ = ["TaskHallPage"]

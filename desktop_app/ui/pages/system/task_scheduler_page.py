# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""任务调度页面。"""

from dataclasses import dataclass, replace

from ....core.qt import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget
from ....core.types import RouteId
from ...components import (
    CalendarWidget,
    ContentSection,
    DataTable,
    FilterDropdown,
    FloatingActionButton,
    PageContainer,
    PrimaryButton,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TabBar,
    TagChip,
    TaskProgressBar,
    ThemedComboBox,
    ThemedScrollArea,
    TimelineWidget,
)
from ...components.inputs import (
    INPUT_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QPushButton,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

WEEK_DAYS: tuple[tuple[str, str, str], ...] = (
    ("2026-03-09", "周一", "03.09"),
    ("2026-03-10", "周二", "03.10"),
    ("2026-03-11", "周三", "03.11"),
    ("2026-03-12", "周四", "03.12"),
    ("2026-03-13", "周五", "03.13"),
    ("2026-03-14", "周六", "03.14"),
    ("2026-03-15", "周日", "03.15"),
)
CURRENT_DAY_KEY = "2026-03-12"
TABLE_PAGE_SIZE = 8
DAY_COLUMN_MIN_WIDTH = SPACING_2XL * 5
DETAIL_MIN_WIDTH = SPACING_2XL * 12
SLOT_MIN_HEIGHT = SPACING_2XL * 4
TOOLBAR_MIN_HEIGHT = INPUT_HEIGHT + SPACING_XL


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 文本。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _clear_layout(layout: object) -> None:
    """安全清空布局中的所有子项。"""

    count_method = getattr(layout, "count", None)
    take_at_method = getattr(layout, "takeAt", None)
    if not callable(count_method) or not callable(take_at_method):
        return
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


@dataclass(frozen=True)
class SchedulerTask:
    """任务调度页面的演示任务。"""

    task_id: str
    name: str
    category: str
    status: str
    date_key: str
    weekday: str
    date_label: str
    start_time: str
    end_time: str
    schedule_expression: str
    execution_node: str
    progress: int
    next_run: str
    last_run: str
    countdown: str
    target: str
    concurrency: str
    retries: str
    summary: str
    notes: str
    tags: tuple[str, ...]
    result_summary: str
    schedule_group: str
    timeline: tuple[dict[str, str], ...]


class TaskSchedulerPage(BasePage):
    """系统模块下的任务调度页。"""

    default_route_id = RouteId("task_scheduler")
    default_display_name = "任务调度"
    default_icon_name = "schedule"

    def setup_ui(self) -> None:
        """构建任务调度页完整界面。"""

        self._all_tasks = self._build_demo_tasks()
        self._visible_tasks: list[SchedulerTask] = []
        self._selected_task_id: str | None = "TKO-7721-X9"
        self._syncing_table_selection = False
        self._next_task_index = len(self._all_tasks) + 1

        _call(self, "setObjectName", "taskSchedulerPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        page_container = PageContainer(
            title=self.display_name,
            description="按周查看自动化排期、执行状态与调度规则，支持日历与列表双视图联动。",
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._quick_create_button = FloatingActionButton(icon_text="＋", tooltip="快速创建任务", parent=page_container)
        self._create_button = PrimaryButton("创建任务", icon_text="＋", parent=page_container)
        page_container.add_action(self._quick_create_button)
        page_container.add_action(self._create_button)

        self._overview_strip = self._build_overview_strip()
        page_container.add_widget(self._overview_strip)

        self._workspace_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.69, 0.31),
            minimum_sizes=(SPACING_2XL * 18, DETAIL_MIN_WIDTH),
            parent=page_container,
        )
        self._workspace_split.set_widgets(self._build_main_workspace(), self._build_detail_panel())
        page_container.add_widget(self._workspace_split)

        _connect(self._status_filter.filter_changed, self._apply_filters)
        _connect(self._type_filter.filter_changed, self._apply_filters)
        _connect(getattr(self._group_filter.combo_box, "currentTextChanged", None), self._apply_filters)
        _connect(self._view_tabs.tab_changed, self._handle_view_tab_changed)
        _connect(getattr(self._create_button, "clicked", None), lambda *_args: self._handle_create_task())
        _connect(getattr(self._quick_create_button, "clicked", None), lambda *_args: self._handle_create_task())
        _connect(self._task_table.row_selected, self._handle_table_row_selected)
        _connect(self._task_table.row_double_clicked, self._handle_table_row_double_clicked)
        _connect(self._month_calendar.date_selected, self._handle_month_date_selected)
        _connect(getattr(self._primary_action_button, "clicked", None), lambda *_args: self._handle_primary_action())
        _connect(getattr(self._secondary_action_button, "clicked", None), lambda *_args: self._handle_secondary_action())

        self._apply_filters()

    def _build_overview_strip(self) -> QWidget:
        """构建页面顶部状态摘要。"""

        strip = QFrame(self)
        _call(strip, "setObjectName", "taskSchedulerOverviewStrip")
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_SM)

        self._summary_total_badge = StatusBadge("本周任务 0", tone="brand", parent=strip)
        self._summary_running_badge = StatusBadge("运行中 0", tone="info", parent=strip)
        self._summary_warning_badge = StatusBadge("异常 0", tone="error", parent=strip)
        self._summary_focus_badge = StatusBadge("当前未选中任务", tone="neutral", parent=strip)
        self._summary_hint_label = QLabel("可按状态、任务类型与调度分组筛选，左侧双视图会同步更新。", strip)
        _call(self._summary_hint_label, "setObjectName", "taskSchedulerHint")
        _call(self._summary_hint_label, "setWordWrap", True)

        layout.addWidget(self._summary_total_badge)
        layout.addWidget(self._summary_running_badge)
        layout.addWidget(self._summary_warning_badge)
        layout.addWidget(self._summary_focus_badge)
        layout.addStretch(1)
        layout.addWidget(self._summary_hint_label, 1)
        return strip

    def _build_main_workspace(self) -> QWidget:
        """构建左侧主工作区。"""

        workspace = QWidget(self)
        _call(workspace, "setObjectName", "taskSchedulerWorkspace")
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        layout.addWidget(self._build_filter_bar())

        self._view_tabs = TabBar(workspace)
        self._view_stack: QStackedWidget = self._view_tabs.stacked_widget
        self._view_tabs.add_tab("周日历", self._build_calendar_view())
        self._view_tabs.add_tab("任务列表", self._build_list_view())
        layout.addWidget(self._view_tabs, 1)
        return workspace

    def _build_filter_bar(self) -> QWidget:
        """构建筛选栏。"""

        toolbar = QFrame(self)
        _call(toolbar, "setObjectName", "taskSchedulerToolbar")
        _call(toolbar, "setMinimumHeight", TOOLBAR_MIN_HEIGHT)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        self._status_filter = FilterDropdown("任务状态", ("待执行", "运行中", "已完成", "已暂停", "异常"))
        self._type_filter = FilterDropdown("任务类型", ("互动运营", "数据采集", "内容发布", "运维监控"))
        self._group_filter = ThemedComboBox("调度分组", ("全部分组", "高频任务", "夜间任务", "失败重试"))
        self._active_window_badge = StatusBadge("当前视图：周日历", tone="brand")

        layout.addWidget(self._status_filter)
        layout.addWidget(self._type_filter)
        layout.addWidget(self._group_filter)
        layout.addStretch(1)
        layout.addWidget(self._active_window_badge)
        return toolbar

    def _build_calendar_view(self) -> QWidget:
        """构建周视图区域。"""

        view = QWidget(self)
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        section = ContentSection("周调度视图", icon="▦", parent=view)
        section.add_widget(self._build_calendar_header())

        self._week_board = QFrame(section)
        _call(self._week_board, "setObjectName", "taskSchedulerWeekBoard")
        self._week_board_layout = QHBoxLayout(self._week_board)
        self._week_board_layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        self._week_board_layout.setSpacing(SPACING_SM)
        section.add_widget(self._week_board)

        legend = QFrame(section)
        _call(legend, "setObjectName", "taskSchedulerLegend")
        legend_layout = QHBoxLayout(legend)
        legend_layout.setContentsMargins(SPACING_LG, SPACING_SM, SPACING_LG, SPACING_SM)
        legend_layout.setSpacing(SPACING_SM)
        legend_layout.addWidget(StatusBadge("运行中卡片", tone="info", parent=legend))
        legend_layout.addWidget(StatusBadge("异常卡片", tone="error", parent=legend))
        legend_layout.addWidget(StatusBadge("待执行卡片", tone="warning", parent=legend))
        legend_layout.addWidget(StatusBadge("已完成卡片", tone="success", parent=legend))
        legend_layout.addStretch(1)
        section.add_widget(legend)

        layout.addWidget(section)
        return view

    def _build_calendar_header(self) -> QWidget:
        """构建周视图头部信息。"""

        header = QFrame(self)
        _call(header, "setObjectName", "taskSchedulerCalendarHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)

        self._calendar_title_label = QLabel("2026年03月 · 第 11 周", header)
        _call(self._calendar_title_label, "setObjectName", "taskSchedulerCalendarTitle")
        self._calendar_subtitle_label = QLabel("周一至周日共 7 天，重点展示高频调度、失败补偿与夜间任务。", header)
        _call(self._calendar_subtitle_label, "setObjectName", "taskSchedulerCalendarSubtitle")
        _call(self._calendar_subtitle_label, "setWordWrap", True)
        title_column.addWidget(self._calendar_title_label)
        title_column.addWidget(self._calendar_subtitle_label)

        self._week_focus_badge = StatusBadge("当前周：03.09 - 03.15", tone="brand", parent=header)

        layout.addLayout(title_column, 1)
        layout.addWidget(self._week_focus_badge)
        return header

    def _build_list_view(self) -> QWidget:
        """构建列表视图区域。"""

        view = QWidget(self)
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        section = ContentSection("任务列表", icon="≣", parent=view)

        list_summary = QFrame(section)
        _call(list_summary, "setObjectName", "taskSchedulerListSummary")
        list_summary_layout = QHBoxLayout(list_summary)
        list_summary_layout.setContentsMargins(SPACING_LG, SPACING_SM, SPACING_LG, SPACING_SM)
        list_summary_layout.setSpacing(SPACING_SM)
        self._list_result_badge = StatusBadge("筛选结果 0", tone="brand", parent=list_summary)
        self._list_mode_badge = StatusBadge("分组：全部分组", tone="neutral", parent=list_summary)
        self._list_hint_label = QLabel("双击表格行可直接同步右侧详情与周视图焦点。", list_summary)
        _call(self._list_hint_label, "setObjectName", "taskSchedulerListHint")
        list_summary_layout.addWidget(self._list_result_badge)
        list_summary_layout.addWidget(self._list_mode_badge)
        list_summary_layout.addStretch(1)
        list_summary_layout.addWidget(self._list_hint_label)
        section.add_widget(list_summary)

        self._task_table = DataTable(
            headers=("任务名称", "任务类型", "状态", "计划时段", "调度表达式", "执行节点", "最近结果"),
            rows=(),
            page_size=TABLE_PAGE_SIZE,
            empty_text="当前筛选条件下暂无调度任务",
            parent=section,
        )
        section.add_widget(self._task_table)

        layout.addWidget(section)
        return view

    def _build_detail_panel(self) -> QWidget:
        """构建右侧任务详情区。"""

        shell = QWidget(self)
        _call(shell, "setObjectName", "taskSchedulerDetailShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        scroll = ThemedScrollArea(shell)
        shell_layout.addWidget(scroll)

        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACING_XL)
        scroll.set_content_widget(content)

        detail_section = ContentSection("任务详情", icon="◎", parent=content)
        detail_section.add_widget(self._build_detail_hero())
        detail_section.add_widget(self._build_detail_meta_cards())
        detail_section.add_widget(self._build_detail_config())
        detail_section.add_widget(self._build_detail_actions())
        content_layout.addWidget(detail_section)

        calendar_section = ContentSection("月历预览", icon="▣", parent=content)
        self._month_calendar = CalendarWidget()
        calendar_section.add_widget(self._month_calendar)
        content_layout.addWidget(calendar_section)

        timeline_section = ContentSection("执行轨迹", icon="↻", parent=content)
        self._timeline_widget = TimelineWidget()
        timeline_section.add_widget(self._timeline_widget)
        content_layout.addWidget(timeline_section)
        content_layout.addStretch(1)
        return shell

    def _build_detail_hero(self) -> QWidget:
        """构建详情头部卡片。"""

        hero = QFrame(self)
        _call(hero, "setObjectName", "taskSchedulerHeroCard")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(SPACING_SM)
        self._detail_status_badge = StatusBadge("运行中", tone="info", parent=hero)
        self._detail_schedule_badge = StatusBadge("高频任务", tone="brand", parent=hero)
        header_row.addWidget(self._detail_status_badge)
        header_row.addWidget(self._detail_schedule_badge)
        header_row.addStretch(1)

        self._detail_title_label = QLabel("数据采集批处理 #07", hero)
        _call(self._detail_title_label, "setObjectName", "taskSchedulerDetailTitle")
        self._detail_id_label = QLabel("任务编号：TKO-7721-X9", hero)
        _call(self._detail_id_label, "setObjectName", "taskSchedulerDetailMeta")
        self._detail_summary_label = QLabel("从达人池与竞品库抓取增量样本，失败节点自动回补。", hero)
        _call(self._detail_summary_label, "setObjectName", "taskSchedulerDetailSummary")
        _call(self._detail_summary_label, "setWordWrap", True)

        countdown_card = QFrame(hero)
        _call(countdown_card, "setObjectName", "taskSchedulerCountdownCard")
        countdown_layout = QVBoxLayout(countdown_card)
        countdown_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        countdown_layout.setSpacing(SPACING_XS)
        countdown_label = QLabel("距离下次运行", countdown_card)
        _call(countdown_label, "setObjectName", "taskSchedulerCountdownLabel")
        self._detail_countdown_value = QLabel("01:24:45", countdown_card)
        _call(self._detail_countdown_value, "setObjectName", "taskSchedulerCountdownValue")
        countdown_layout.addWidget(countdown_label)
        countdown_layout.addWidget(self._detail_countdown_value)

        self._detail_progress_bar = TaskProgressBar(72)

        self._detail_tag_host = QWidget(hero)
        _call(self._detail_tag_host, "setObjectName", "taskSchedulerTagHost")
        self._detail_tag_layout = QHBoxLayout(self._detail_tag_host)
        self._detail_tag_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_tag_layout.setSpacing(SPACING_SM)

        layout.addLayout(header_row)
        layout.addWidget(self._detail_title_label)
        layout.addWidget(self._detail_id_label)
        layout.addWidget(self._detail_summary_label)
        layout.addWidget(countdown_card)
        layout.addWidget(self._detail_progress_bar)
        layout.addWidget(self._detail_tag_host)
        return hero

    def _build_detail_meta_cards(self) -> QWidget:
        """构建详情元信息卡片。"""

        host = QWidget(self)
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._detail_schedule_card = self._build_value_card("调度表达式", "0 */30 9-23 * * *")
        self._detail_node_card = self._build_value_card("执行节点", "采集节点-A2")
        self._detail_last_run_card = self._build_value_card("最近运行", "2026-03-12 15:31")

        layout.addWidget(self._detail_schedule_card)
        layout.addWidget(self._detail_node_card)
        layout.addWidget(self._detail_last_run_card)
        return host

    def _build_detail_config(self) -> QWidget:
        """构建基础配置区。"""

        card = QFrame(self)
        _call(card, "setObjectName", "taskSchedulerConfigCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_SM)

        title = QLabel("基础配置", card)
        _call(title, "setObjectName", "taskSchedulerConfigTitle")
        self._detail_target_label = self._build_field_label("目标地址")
        self._detail_target_value = self._build_field_value("https://ops.internal/scraper/cluster-a2")
        self._detail_concurrency_label = self._build_field_label("并发数量")
        self._detail_concurrency_value = self._build_field_value("16 并发")
        self._detail_retry_label = self._build_field_label("失败重试")
        self._detail_retry_value = self._build_field_value("失败后 3 次补偿重试")
        self._detail_note_label = self._build_field_label("规则说明")
        self._detail_note_value = self._build_field_value("按优先级队列执行，异常时自动写入巡检日志并通知值班群。")
        _call(self._detail_note_value, "setWordWrap", True)

        layout.addWidget(title)
        layout.addWidget(self._detail_target_label)
        layout.addWidget(self._detail_target_value)
        layout.addWidget(self._detail_concurrency_label)
        layout.addWidget(self._detail_concurrency_value)
        layout.addWidget(self._detail_retry_label)
        layout.addWidget(self._detail_retry_value)
        layout.addWidget(self._detail_note_label)
        layout.addWidget(self._detail_note_value)
        return card

    def _build_detail_actions(self) -> QWidget:
        """构建详情动作区。"""

        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(SPACING_SM)
        self._secondary_action_button = SecondaryButton("暂停任务", parent=panel)
        self._primary_action_button = PrimaryButton("立即执行", parent=panel)
        actions.addWidget(self._secondary_action_button)
        actions.addWidget(self._primary_action_button)

        self._detail_feedback_label = QLabel("支持立即执行、暂停任务与失败补跑。", panel)
        _call(self._detail_feedback_label, "setObjectName", "taskSchedulerFeedback")
        _call(self._detail_feedback_label, "setWordWrap", True)

        layout.addLayout(actions)
        layout.addWidget(self._detail_feedback_label)
        return panel

    def _build_value_card(self, label_text: str, value_text: str) -> QFrame:
        """构建简洁值卡片。"""

        card = QFrame(self)
        _call(card, "setObjectName", "taskSchedulerValueCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
        layout.setSpacing(SPACING_XS)

        label = QLabel(label_text, card)
        _call(label, "setObjectName", "taskSchedulerValueCardLabel")
        value = QLabel(value_text, card)
        _call(value, "setObjectName", "taskSchedulerValueCardValue")
        _call(value, "setWordWrap", True)

        layout.addWidget(label)
        layout.addWidget(value)
        setattr(card, "value_label", value)
        return card

    def _build_field_label(self, text: str) -> QLabel:
        """构建字段标签。"""

        label = QLabel(text, self)
        _call(label, "setObjectName", "taskSchedulerFieldLabel")
        return label

    def _build_field_value(self, text: str) -> QLabel:
        """构建字段值。"""

        label = QLabel(text, self)
        _call(label, "setObjectName", "taskSchedulerFieldValue")
        return label

    def _apply_filters(self, *_args: object) -> None:
        """根据筛选项刷新双视图与详情。"""

        status_value = self._status_filter.current_text()
        type_value = self._type_filter.current_text()
        group_value = self._group_filter.current_text()

        self._visible_tasks = [
            task
            for task in self._all_tasks
            if (status_value in ("", "全部") or task.status == status_value)
            and (type_value in ("", "全部") or task.category == type_value)
            and self._matches_group(task, group_value)
        ]

        visible_ids = {task.task_id for task in self._visible_tasks}
        if self._selected_task_id not in visible_ids:
            self._selected_task_id = self._visible_tasks[0].task_id if self._visible_tasks else None

        self._task_table.set_rows(self._table_rows(self._visible_tasks))
        self._rebuild_week_board()
        self._refresh_overview_strip(group_value)
        self._refresh_list_summary(group_value)
        self._refresh_month_calendar()
        self._refresh_detail_panel()
        self._sync_table_selection()

    def _matches_group(self, task: SchedulerTask, group_value: str) -> bool:
        """判断任务是否符合当前分组筛选。"""

        if group_value in ("", "全部分组"):
            return True
        return task.schedule_group == group_value

    def _table_rows(self, tasks: list[SchedulerTask]) -> list[tuple[str, ...]]:
        """将任务对象转换为表格行。"""

        return [
            (
                task.name,
                task.category,
                task.status,
                f"{task.weekday} {task.start_time}-{task.end_time}",
                task.schedule_expression,
                task.execution_node,
                task.result_summary,
            )
            for task in tasks
        ]

    def _rebuild_week_board(self) -> None:
        """重建周视图任务栏位。"""

        _clear_layout(self._week_board_layout)
        tasks_by_day: dict[str, list[SchedulerTask]] = {date_key: [] for date_key, _day, _label in WEEK_DAYS}
        for task in self._visible_tasks:
            tasks_by_day.setdefault(task.date_key, []).append(task)

        for date_key, weekday, date_label in WEEK_DAYS:
            column = self._build_day_column(date_key, weekday, date_label, tasks_by_day.get(date_key, []))
            self._week_board_layout.addWidget(column, 1)

    def _build_day_column(self, date_key: str, weekday: str, date_label: str, tasks: list[SchedulerTask]) -> QWidget:
        """构建单日列。"""

        colors = _palette()
        is_current_day = date_key == CURRENT_DAY_KEY
        is_weekend = weekday in {"周六", "周日"}
        column = QFrame(self)
        _call(column, "setObjectName", "taskSchedulerDayColumn")
        _call(column, "setMinimumWidth", DAY_COLUMN_MIN_WIDTH)

        background = _rgba(_token("brand.primary"), 0.06) if is_current_day else colors.surface
        border_color = _token("brand.primary") if is_current_day else colors.border
        if is_weekend and not is_current_day:
            background = _rgba(colors.border, 0.12)

        _call(
            column,
            "setStyleSheet",
            f"""
            QFrame#taskSchedulerDayColumn {{
                background-color: {background};
                border: 1px solid {border_color};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#taskSchedulerDayTitle {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#taskSchedulerDayMeta {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#taskSchedulerDayEmpty {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            """,
        )

        layout = QVBoxLayout(column)
        layout.setContentsMargins(SPACING_MD, SPACING_MD, SPACING_MD, SPACING_MD)
        layout.setSpacing(SPACING_SM)

        title = QLabel(f"{weekday}", column)
        _call(title, "setObjectName", "taskSchedulerDayTitle")
        meta = QLabel(f"{date_label} · {len(tasks)} 项", column)
        _call(meta, "setObjectName", "taskSchedulerDayMeta")
        layout.addWidget(title)
        layout.addWidget(meta)

        if not tasks:
            empty = QLabel("暂无排期", column)
            _call(empty, "setObjectName", "taskSchedulerDayEmpty")
            layout.addWidget(empty)
            layout.addStretch(1)
            return column

        for task in tasks:
            layout.addWidget(self._build_task_slot(task))
        layout.addStretch(1)
        return column

    def _build_task_slot(self, task: SchedulerTask) -> QWidget:
        """构建周视图中的任务卡片。"""

        colors = _palette()
        accent = self._task_accent_color(task)
        selected = task.task_id == self._selected_task_id
        background = _rgba(accent, 0.14)
        border_color = _token("brand.primary") if selected else _rgba(accent, 0.34)
        slot = QPushButton(
            f"{task.category}\n{task.name}\n{task.start_time} - {task.end_time}\n{task.status}",
            self,
        )
        _call(slot, "setObjectName", "taskSchedulerSlot")
        _call(slot, "setMinimumHeight", SLOT_MIN_HEIGHT)
        _call(
            slot,
            "setStyleSheet",
            f"""
            QPushButton#taskSchedulerSlot {{
                background-color: {background};
                color: {colors.text};
                border: 1px solid {border_color};
                border-left: {SPACING_XS}px solid {accent};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_SM}px {SPACING_MD}px;
                text-align: left;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#taskSchedulerSlot:hover {{
                border-color: {_token('brand.primary')};
                background-color: {_rgba(accent, 0.20)};
            }}
            """,
        )
        _connect(getattr(slot, "clicked", None), lambda *_args, task_id=task.task_id: self._select_task(task_id))
        return slot

    def _refresh_overview_strip(self, group_value: str) -> None:
        """刷新顶部摘要。"""

        running_count = sum(1 for task in self._visible_tasks if task.status == "运行中")
        warning_count = sum(1 for task in self._visible_tasks if task.status == "异常")
        selected = self._selected_task()

        _call(self._summary_total_badge, "setText", f"本周任务 {len(self._visible_tasks)}")
        _call(self._summary_running_badge, "setText", f"运行中 {running_count}")
        _call(self._summary_warning_badge, "setText", f"异常 {warning_count}")

        if selected is None:
            _call(self._summary_focus_badge, "setText", "当前未选中任务")
            self._summary_focus_badge.set_tone("neutral")
            _call(self._summary_hint_label, "setText", f"当前筛选分组：{group_value}，没有可展示的任务详情。")
            return

        _call(self._summary_focus_badge, "setText", f"焦点任务：{selected.name}")
        self._summary_focus_badge.set_tone(self._status_tone(selected.status))
        _call(
            self._summary_hint_label,
            "setText",
            f"{selected.weekday} {selected.start_time}-{selected.end_time} · {selected.execution_node} · {selected.result_summary}",
        )

    def _refresh_list_summary(self, group_value: str) -> None:
        """刷新列表视图摘要。"""

        _call(self._list_result_badge, "setText", f"筛选结果 {len(self._visible_tasks)}")
        _call(self._list_mode_badge, "setText", f"分组：{group_value}")
        _call(self._active_window_badge, "setText", f"当前视图：{self._current_view_label()}")

    def _refresh_month_calendar(self) -> None:
        """刷新右侧月历事件标记。"""

        events: dict[object, object] = {}
        for task in self._visible_tasks:
            current_count = events.get(task.date_key, 0)
            events[task.date_key] = (current_count if isinstance(current_count, int) else 0) + 1
        self._month_calendar.set_events(events)

    def _refresh_detail_panel(self) -> None:
        """根据当前焦点任务刷新右侧详情。"""

        task = self._selected_task()
        if task is None:
            self._set_empty_detail_state()
            return

        _call(self._detail_status_badge, "setText", task.status)
        self._detail_status_badge.set_tone(self._status_tone(task.status))
        _call(self._detail_schedule_badge, "setText", task.schedule_group)
        self._detail_schedule_badge.set_tone("brand" if task.schedule_group != "失败重试" else "warning")
        _call(self._detail_title_label, "setText", task.name)
        _call(self._detail_id_label, "setText", f"任务编号：{task.task_id}")
        _call(self._detail_summary_label, "setText", task.summary)
        _call(self._detail_countdown_value, "setText", task.countdown)
        self._detail_progress_bar.set_progress(task.progress)
        self._set_value_card_text(self._detail_schedule_card, task.schedule_expression)
        self._set_value_card_text(self._detail_node_card, task.execution_node)
        self._set_value_card_text(self._detail_last_run_card, task.last_run)
        _call(self._detail_target_value, "setText", task.target)
        _call(self._detail_concurrency_value, "setText", task.concurrency)
        _call(self._detail_retry_value, "setText", task.retries)
        _call(self._detail_note_value, "setText", task.notes)
        _call(
            self._detail_feedback_label,
            "setText",
            f"下次计划：{task.next_run} · 当前节点：{task.execution_node} · 最近状态：{task.result_summary}",
        )
        _call(self._primary_action_button, "setEnabled", True)
        _call(self._secondary_action_button, "setEnabled", True)
        self._set_detail_action_labels(task)
        self._rebuild_detail_tags(task.tags)
        self._timeline_widget.set_events(task.timeline)

    def _set_empty_detail_state(self) -> None:
        """当无任务时展示空状态。"""

        _call(self._detail_status_badge, "setText", "无任务")
        self._detail_status_badge.set_tone("neutral")
        _call(self._detail_schedule_badge, "setText", "等待筛选")
        self._detail_schedule_badge.set_tone("neutral")
        _call(self._detail_title_label, "setText", "暂无可展示任务")
        _call(self._detail_id_label, "setText", "任务编号：—")
        _call(self._detail_summary_label, "setText", "请调整筛选条件，或点击“创建任务”添加新的调度任务。")
        _call(self._detail_countdown_value, "setText", "--:--:--")
        self._detail_progress_bar.set_progress(0)
        self._set_value_card_text(self._detail_schedule_card, "—")
        self._set_value_card_text(self._detail_node_card, "—")
        self._set_value_card_text(self._detail_last_run_card, "—")
        _call(self._detail_target_value, "setText", "—")
        _call(self._detail_concurrency_value, "setText", "—")
        _call(self._detail_retry_value, "setText", "—")
        _call(self._detail_note_value, "setText", "暂无规则说明")
        _call(self._detail_feedback_label, "setText", "当前无任务可执行。")
        _call(self._primary_action_button, "setEnabled", False)
        _call(self._secondary_action_button, "setEnabled", False)
        self._rebuild_detail_tags(())
        self._timeline_widget.set_events(())

    def _rebuild_detail_tags(self, tags: tuple[str, ...]) -> None:
        """刷新任务标签。"""

        _clear_layout(self._detail_tag_layout)
        if not tags:
            empty = QLabel("暂无标签", self._detail_tag_host)
            _call(empty, "setObjectName", "taskSchedulerFieldValue")
            self._detail_tag_layout.addWidget(empty)
            self._detail_tag_layout.addStretch(1)
            return

        for tag in tags:
            tone: BadgeTone = "brand" if "高频" in tag or "补偿" in tag else "neutral"
            self._detail_tag_layout.addWidget(TagChip(tag, tone=tone, parent=self._detail_tag_host))
        self._detail_tag_layout.addStretch(1)

    def _set_value_card_text(self, card: QFrame, text: str) -> None:
        """更新值卡片中的内容文本。"""

        value_label = getattr(card, "value_label", None)
        if value_label is not None:
            _call(value_label, "setText", text)

    def _set_detail_action_labels(self, task: SchedulerTask) -> None:
        """根据任务状态调整动作按钮文案。"""

        if task.status == "运行中":
            self._primary_action_button.set_label_text("立即补跑")
            self._secondary_action_button.set_label_text("暂停任务")
            return
        if task.status == "异常":
            self._primary_action_button.set_label_text("失败重试")
            self._secondary_action_button.set_label_text("暂停告警")
            return
        if task.status == "已暂停":
            self._primary_action_button.set_label_text("恢复调度")
            self._secondary_action_button.set_label_text("编辑规则")
            return
        if task.status == "已完成":
            self._primary_action_button.set_label_text("再次执行")
            self._secondary_action_button.set_label_text("查看记录")
            return
        self._primary_action_button.set_label_text("立即执行")
        self._secondary_action_button.set_label_text("暂停任务")

    def _current_view_label(self) -> str:
        """返回当前标签文案。"""

        current_index = getattr(self._view_stack, "currentIndex", lambda: 0)()
        return "任务列表" if current_index == 1 else "周日历"

    def _sync_table_selection(self) -> None:
        """同步表格选中项。"""

        if self._selected_task_id is None:
            return
        row_index = next((index for index, task in enumerate(self._visible_tasks) if task.task_id == self._selected_task_id), -1)
        if row_index < 0:
            return
        self._syncing_table_selection = True
        self._task_table.select_absolute_row(row_index)
        self._syncing_table_selection = False

    def _handle_table_row_selected(self, row_index: int) -> None:
        """处理表格选中变化。"""

        if self._syncing_table_selection or not (0 <= row_index < len(self._visible_tasks)):
            return
        self._select_task(self._visible_tasks[row_index].task_id)

    def _handle_view_tab_changed(self, _index: int) -> None:
        """切换视图时同步顶部摘要。"""

        group_value = self._group_filter.current_text() if self._group_filter is not None else "全部分组"
        self._refresh_list_summary(group_value)

    def _handle_table_row_double_clicked(self, row_index: int) -> None:
        """双击列表项时切回周日历并聚焦任务。"""

        if not (0 <= row_index < len(self._visible_tasks)):
            return
        self._view_tabs.set_current(0)
        self._select_task(self._visible_tasks[row_index].task_id)

    def _handle_month_date_selected(self, date_value: object) -> None:
        """点击月历日期时聚焦当天首个任务。"""

        year_reader = getattr(date_value, "year", None)
        month_reader = getattr(date_value, "month", None)
        day_reader = getattr(date_value, "day", None)
        if not callable(year_reader) or not callable(month_reader) or not callable(day_reader):
            return
        date_key = f"{year_reader():04d}-{month_reader():02d}-{day_reader():02d}"
        matched = next((task for task in self._visible_tasks if task.date_key == date_key), None)
        if matched is None:
            matched = next((task for task in self._all_tasks if task.date_key == date_key), None)
        if matched is None:
            return
        self._view_tabs.set_current(0)
        self._select_task(matched.task_id)

    def _select_task(self, task_id: str) -> None:
        """统一处理任务焦点切换。"""

        self._selected_task_id = task_id
        self._refresh_overview_strip(self._group_filter.current_text())
        self._refresh_detail_panel()
        self._rebuild_week_board()
        self._sync_table_selection()

    def _handle_primary_action(self) -> None:
        """模拟主动作执行。"""

        task = self._selected_task()
        if task is None:
            return

        if task.status == "运行中":
            updated = replace(
                task,
                progress=min(100, max(task.progress, 80)),
                next_run="手动补跑已排队",
                result_summary="已追加一次手动补跑",
            )
        elif task.status == "异常":
            updated = replace(
                task,
                status="运行中",
                progress=max(28, task.progress),
                countdown="00:12:20",
                next_run="立即执行中",
                result_summary="异常补偿已恢复执行",
            )
        elif task.status == "已暂停":
            updated = replace(
                task,
                status="运行中",
                progress=max(18, task.progress),
                countdown="00:18:00",
                next_run="恢复后 18 分钟执行",
                result_summary="任务已恢复调度",
            )
        elif task.status == "已完成":
            updated = replace(
                task,
                status="待执行",
                progress=0,
                countdown="00:06:00",
                next_run="手动触发后 6 分钟启动",
                result_summary="已加入重跑队列",
            )
        else:
            updated = replace(
                task,
                status="运行中",
                progress=max(12, task.progress),
                countdown="00:10:00",
                next_run="立即执行中",
                result_summary="任务已切换为立即执行",
            )

        self._replace_task(updated)
        self._selected_task_id = updated.task_id
        self._detail_feedback_label.setText(f"已对 {updated.name} 执行主操作：{updated.result_summary}")
        self._apply_filters()

    def _handle_secondary_action(self) -> None:
        """模拟次级动作。"""

        task = self._selected_task()
        if task is None:
            return

        if task.status == "运行中":
            updated = replace(task, status="已暂停", next_run="等待人工恢复", result_summary="已手动暂停任务")
        elif task.status == "异常":
            updated = replace(task, status="已暂停", next_run="告警暂停中", result_summary="异常任务已暂停并等待复核")
        elif task.status == "已暂停":
            updated = replace(task, notes="已进入规则编辑队列，等待更新时间窗与重试策略。", result_summary="规则编辑请求已记录")
        else:
            updated = replace(task, notes=f"{task.notes} 已打开历史执行记录。", result_summary="已查看相关记录")

        self._replace_task(updated)
        self._selected_task_id = updated.task_id
        self._detail_feedback_label.setText(f"已对 {updated.name} 执行次级操作：{updated.result_summary}")
        self._apply_filters()

    def _handle_create_task(self) -> None:
        """新增一条演示任务。"""

        new_task = SchedulerTask(
            task_id=f"TKO-NEW-{self._next_task_index:03d}",
            name="自动点赞补量",
            category="互动运营",
            status="待执行",
            date_key="2026-03-13",
            weekday="周五",
            date_label="03.13",
            start_time="20:30",
            end_time="21:00",
            schedule_expression="0 30 20 * * 5",
            execution_node="互动节点-C1",
            progress=0,
            next_run="2026-03-13 20:30",
            last_run="尚未执行",
            countdown="12:08:00",
            target="达人互动池 / 晚高峰补量场景",
            concurrency="8 并发",
            retries="失败后 2 次重试",
            summary="针对重点账号进行晚高峰自动点赞补量，提升互动热度。",
            notes="新建任务默认进入待执行状态，可在夜间窗口前调整频率与目标账号池。",
            tags=("新建任务", "互动运营", "晚高峰"),
            result_summary="刚刚创建，等待进入调度队列",
            schedule_group="夜间任务",
            timeline=(
                {"timestamp": "2026-03-08 16:40:08", "title": "任务创建成功", "content": "已生成默认执行规则与晚高峰时间窗。", "type": "info"},
            ),
        )
        self._next_task_index += 1
        self._all_tasks.insert(0, new_task)
        self._selected_task_id = new_task.task_id
        self._view_tabs.set_current(0)
        self._apply_filters()

    def _replace_task(self, updated: SchedulerTask) -> None:
        """替换任务列表中的指定任务。"""

        self._all_tasks = [updated if task.task_id == updated.task_id else task for task in self._all_tasks]

    def _selected_task(self) -> SchedulerTask | None:
        """返回当前选中的任务。"""

        if self._selected_task_id is None:
            return None
        return next((task for task in self._all_tasks if task.task_id == self._selected_task_id), None)

    @staticmethod
    def _status_tone(status: str) -> BadgeTone:
        """映射状态对应的徽标色。"""

        mapping: dict[str, BadgeTone] = {
            "待执行": "warning",
            "运行中": "info",
            "已完成": "success",
            "已暂停": "neutral",
            "异常": "error",
            "无任务": "neutral",
        }
        return mapping.get(status, "neutral")

    @staticmethod
    def _task_accent_color(task: SchedulerTask) -> str:
        """按任务类型返回卡片强调色。"""

        mapping = {
            "互动运营": _token("status.warning"),
            "数据采集": _token("status.info"),
            "内容发布": _token("status.success"),
            "运维监控": _token("status.error") if task.status == "异常" else _token("brand.primary"),
        }
        return mapping.get(task.category, _token("brand.primary"))

    def _apply_page_styles(self) -> None:
        """应用页面级主题样式。"""

        colors = _palette()
        brand_soft = _rgba(_token("brand.primary"), 0.12)
        brand_border = _rgba(_token("brand.primary"), 0.22)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#taskSchedulerPage {{
                background-color: {colors.surface_alt};
            }}
            QFrame#taskSchedulerToolbar,
            QFrame#taskSchedulerCalendarHeader,
            QFrame#taskSchedulerWeekBoard,
            QFrame#taskSchedulerLegend,
            QFrame#taskSchedulerHeroCard,
            QFrame#taskSchedulerConfigCard,
            QFrame#taskSchedulerValueCard,
            QWidget#taskSchedulerDetailShell {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#taskSchedulerOverviewStrip,
            QFrame#taskSchedulerCalendarHeader,
            QFrame#taskSchedulerListSummary {{
                background-color: {brand_soft};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#taskSchedulerPage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#taskSchedulerHint,
            QLabel#taskSchedulerListHint,
            QLabel#taskSchedulerCalendarSubtitle,
            QLabel#taskSchedulerDetailMeta,
            QLabel#taskSchedulerFeedback,
            QLabel#taskSchedulerFieldLabel,
            QLabel#taskSchedulerValueCardLabel,
            QLabel#taskSchedulerCountdownLabel {{
                background: transparent;
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#taskSchedulerCalendarTitle,
            QLabel#taskSchedulerConfigTitle,
            QLabel#taskSchedulerDetailTitle,
            QLabel#taskSchedulerValueCardValue,
            QLabel#taskSchedulerCountdownValue {{
                background: transparent;
                color: {colors.text};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#taskSchedulerCalendarTitle {{
                font-size: {_static_token('font.size.xl')};
            }}
            QLabel#taskSchedulerConfigTitle,
            QLabel#taskSchedulerValueCardValue {{
                font-size: {_static_token('font.size.md')};
            }}
            QLabel#taskSchedulerDetailTitle {{
                font-size: {_static_token('font.size.xl')};
            }}
            QLabel#taskSchedulerDetailSummary,
            QLabel#taskSchedulerFieldValue {{
                background: transparent;
                color: {colors.text};
                font-size: {_static_token('font.size.sm')};
            }}
            QFrame#taskSchedulerCountdownCard {{
                background-color: {brand_soft};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_MD}px;
            }}
            QLabel#taskSchedulerCountdownValue {{
                color: {_token('brand.primary')};
                font-size: {_static_token('font.size.xxl')};
            }}
            QWidget#taskSchedulerTagHost {{
                background: transparent;
                border: none;
            }}
            """,
        )

    @staticmethod
    def _build_demo_tasks() -> list[SchedulerTask]:
        """构建页面使用的演示数据。"""

        return [
            SchedulerTask(
                task_id="TKO-7612-A1",
                name="自动点赞晨间预热",
                category="互动运营",
                status="已完成",
                date_key="2026-03-09",
                weekday="周一",
                date_label="03.09",
                start_time="09:00",
                end_time="09:30",
                schedule_expression="0 0 9 * * 1-5",
                execution_node="互动节点-A1",
                progress=100,
                next_run="2026-03-10 09:00",
                last_run="2026-03-09 09:31",
                countdown="18:20:00",
                target="重点商品橱窗 / 晨间推荐流",
                concurrency="12 并发",
                retries="成功后不重试",
                summary="晨间时段自动点赞预热，提高商品卡初始互动率。",
                notes="仅对前一晚新上架的商品启用，避免重复互动造成流量浪费。",
                tags=("晨间", "高转化", "自动点赞"),
                result_summary="最近一次完成率 100%，互动回流正常",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-09 09:00:00", "title": "任务启动", "content": "开始扫描晨间重点商品池。", "type": "info"},
                    {"timestamp": "2026-03-09 09:15:12", "title": "互动执行完成", "content": "共完成 86 次点赞与 12 次收藏动作。", "type": "success"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7648-B4",
                name="竞品增量数据采集",
                category="数据采集",
                status="待执行",
                date_key="2026-03-10",
                weekday="周二",
                date_label="03.10",
                start_time="10:30",
                end_time="11:20",
                schedule_expression="0 30 10 * * 2-6",
                execution_node="采集节点-B4",
                progress=0,
                next_run="2026-03-10 10:30",
                last_run="2026-03-09 10:31",
                countdown="04:18:00",
                target="竞品清单 / 价格与销量增量接口",
                concurrency="10 并发",
                retries="失败后 2 次重试",
                summary="定时抓取竞品价格、销量与活动标签，供定价规则引擎回写。",
                notes="若接口返回限流，将自动切换备用代理组并延后 5 分钟重试。",
                tags=("竞品", "增量采集", "价格监控"),
                result_summary="等待开始，尚未进入执行窗口",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-09 10:31:00", "title": "上次任务完成", "content": "已抓取 2411 条竞品记录。", "type": "success"},
                    {"timestamp": "2026-03-10 10:15:00", "title": "预执行检查", "content": "代理池与接口凭证通过健康校验。", "type": "info"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7680-C2",
                name="自动评论回复",
                category="互动运营",
                status="待执行",
                date_key="2026-03-11",
                weekday="周三",
                date_label="03.11",
                start_time="14:00",
                end_time="14:40",
                schedule_expression="0 0 14 * * 1-5",
                execution_node="互动节点-C2",
                progress=0,
                next_run="2026-03-11 14:00",
                last_run="2026-03-10 14:42",
                countdown="27:50:00",
                target="重点短视频评论池 / 高意向提问词",
                concurrency="6 并发",
                retries="失败后 1 次补偿重试",
                summary="对高意向评论进行自动回复，优先处理询价、库存、发货问题。",
                notes="命中敏感词时自动切换人工审核，不直接执行回复。",
                tags=("高意向", "自动回复", "评论池"),
                result_summary="等待下午场任务开始",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-10 14:00:00", "title": "昨日批次启动", "content": "导入待回复评论 126 条。", "type": "info"},
                    {"timestamp": "2026-03-10 14:42:21", "title": "批次完成", "content": "自动回复 98 条，转人工 7 条。", "type": "success"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7702-D5",
                name="店铺环境巡检",
                category="运维监控",
                status="运行中",
                date_key="2026-03-12",
                weekday="周四",
                date_label="03.12",
                start_time="09:30",
                end_time="10:00",
                schedule_expression="0 30 9 * * *",
                execution_node="巡检节点-D5",
                progress=64,
                next_run="2026-03-12 09:30",
                last_run="2026-03-12 09:44",
                countdown="00:11:18",
                target="店铺网络、接口凭证、下载链路、登录态健康检查",
                concurrency="4 并发",
                retries="异常项自动复查 2 次",
                summary="按半小时周期巡检店铺关键链路，异常项直接写入告警中心。",
                notes="当前批次重点检查代理切换、下载目录容量与登录态剩余有效期。",
                tags=("巡检", "半小时", "告警联动"),
                result_summary="当前批次已发现 1 项弱告警，正在复核",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-12 09:30:03", "title": "巡检开始", "content": "载入 18 个系统健康检查项。", "type": "info"},
                    {"timestamp": "2026-03-12 09:37:25", "title": "发现弱告警", "content": "下载目录可用空间低于预警阈值。", "type": "warning"},
                    {"timestamp": "2026-03-12 09:44:10", "title": "自动复核中", "content": "正在验证磁盘清理与缓存回收结果。", "type": "info"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7721-X9",
                name="数据采集批处理 #07",
                category="数据采集",
                status="运行中",
                date_key="2026-03-12",
                weekday="周四",
                date_label="03.12",
                start_time="15:30",
                end_time="16:20",
                schedule_expression="0 */30 9-23 * * *",
                execution_node="采集节点-A2",
                progress=72,
                next_run="2026-03-12 16:30",
                last_run="2026-03-12 15:31",
                countdown="01:24:45",
                target="达人线索池 / 网页采集 / 新热视频评论样本",
                concurrency="16 并发",
                retries="失败后 3 次补偿重试",
                summary="从达人池与竞品内容池抓取增量样本，失败节点自动补偿，适配晚高峰选品分析。",
                notes="当前批次已锁定 2401 个采集节点，输出将直连数据仓库的临时清洗表。",
                tags=("高频轮询", "失败补偿", "达人池", "数据采集"),
                result_summary="正在导出批次结果，预计 16:20 完成",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-12 15:30:01", "title": "任务实例化成功", "content": "已加载 2401 个节点与备用代理组。", "type": "info"},
                    {"timestamp": "2026-03-12 15:31:45", "title": "采集开始", "content": "开始解析热视频评论、达人主页与商品挂链信息。", "type": "info"},
                    {"timestamp": "2026-03-12 15:46:20", "title": "补偿节点生效", "content": "12 个失败节点已切换备用线路重新抓取。", "type": "warning"},
                    {"timestamp": "2026-03-12 15:58:03", "title": "数据清洗通过", "content": "异常空值已剔除，准备进入导出阶段。", "type": "success"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7736-Z2",
                name="数据库冷备份",
                category="运维监控",
                status="异常",
                date_key="2026-03-12",
                weekday="周四",
                date_label="03.12",
                start_time="16:45",
                end_time="17:15",
                schedule_expression="0 45 16 * * 4",
                execution_node="备份节点-Z2",
                progress=38,
                next_run="等待人工确认",
                last_run="2026-03-12 16:52",
                countdown="00:00:00",
                target="订单库 / 内容库 / 任务日志冷备份",
                concurrency="2 并发",
                retries="异常后 1 次自动重试 + 人工确认",
                summary="每周四执行全量冷备份，若目标存储返回延迟则立即告警并暂停写入。",
                notes="本次任务因远端存储握手超时中断，建议先检查备份仓与专线链路。",
                tags=("冷备份", "异常中断", "运维监控"),
                result_summary="远端存储握手超时，等待人工补跑",
                schedule_group="失败重试",
                timeline=(
                    {"timestamp": "2026-03-12 16:45:00", "title": "备份任务启动", "content": "开始执行数据库与日志文件冷备份。", "type": "info"},
                    {"timestamp": "2026-03-12 16:52:16", "title": "连接异常", "content": "远端对象存储握手超时，备份流已中断。", "type": "error"},
                    {"timestamp": "2026-03-12 16:53:04", "title": "告警已触发", "content": "值班群与告警中心已收到异常通知。", "type": "warning"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7755-L8",
                name="午后短视频发布",
                category="内容发布",
                status="待执行",
                date_key="2026-03-13",
                weekday="周五",
                date_label="03.13",
                start_time="11:00",
                end_time="11:20",
                schedule_expression="0 0 11 * * 5",
                execution_node="发布节点-L8",
                progress=0,
                next_run="2026-03-13 11:00",
                last_run="2026-03-06 11:18",
                countdown="19:16:00",
                target="短视频素材池 / 周五午后流量窗口",
                concurrency="3 并发",
                retries="失败后 2 次重发",
                summary="在周五午后流量回升时段自动发布精选短视频，联动商品卡与优惠券。",
                notes="发布前需确认素材已通过审核，若命中风控标签则自动跳过该素材。",
                tags=("短视频", "商品卡", "定时发布"),
                result_summary="等待周五午后窗口开始",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-06 11:00:00", "title": "上周任务启动", "content": "已选择 3 条优先级最高素材。", "type": "info"},
                    {"timestamp": "2026-03-06 11:18:30", "title": "发布完成", "content": "3 条内容发布成功，联动券包已挂载。", "type": "success"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7789-P6",
                name="商品价格波动监控",
                category="数据采集",
                status="已暂停",
                date_key="2026-03-14",
                weekday="周六",
                date_label="03.14",
                start_time="08:30",
                end_time="09:00",
                schedule_expression="0 30 8 * * 6,7",
                execution_node="价格节点-P6",
                progress=46,
                next_run="等待人工恢复",
                last_run="2026-03-14 08:43",
                countdown="--:--:--",
                target="周末竞品价格波动与促销标签识别",
                concurrency="5 并发",
                retries="暂停期间不重试",
                summary="周末采集竞品价格波动，辅助促销策略快速调整。",
                notes="因周末活动口径调整，当前先暂停自动抓取，等待新规则下发。",
                tags=("周末", "价格监控", "人工复核"),
                result_summary="已暂停，等待促销规则更新",
                schedule_group="夜间任务",
                timeline=(
                    {"timestamp": "2026-03-14 08:30:00", "title": "任务启动", "content": "加载周末促销白名单商品。", "type": "info"},
                    {"timestamp": "2026-03-14 08:43:10", "title": "人工暂停", "content": "活动规则变更，任务暂停等待新口径。", "type": "warning"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7814-Q3",
                name="晚间素材水印处理",
                category="内容发布",
                status="待执行",
                date_key="2026-03-14",
                weekday="周六",
                date_label="03.14",
                start_time="21:00",
                end_time="22:10",
                schedule_expression="0 0 21 * * 6",
                execution_node="素材节点-Q3",
                progress=0,
                next_run="2026-03-14 21:00",
                last_run="2026-03-07 21:58",
                countdown="30:52:00",
                target="周末二创素材池 / 批量水印处理与压缩导出",
                concurrency="7 并发",
                retries="失败后 2 次重排队",
                summary="夜间批量清洗待发布素材，自动叠加水印并输出标准发布尺寸。",
                notes="适合在非高峰期执行，避免占用白天导出链路。",
                tags=("夜间任务", "素材处理", "批量导出"),
                result_summary="等待夜间时间窗到达",
                schedule_group="夜间任务",
                timeline=(
                    {"timestamp": "2026-03-07 21:00:00", "title": "上周夜间批次启动", "content": "导入待处理素材 42 条。", "type": "info"},
                    {"timestamp": "2026-03-07 21:58:11", "title": "导出完成", "content": "成功输出 39 条，失败 3 条已回收重试。", "type": "success"},
                ),
            ),
            SchedulerTask(
                task_id="TKO-7842-S7",
                name="周报自动推送",
                category="运维监控",
                status="已完成",
                date_key="2026-03-15",
                weekday="周日",
                date_label="03.15",
                start_time="18:00",
                end_time="18:20",
                schedule_expression="0 0 18 * * 7",
                execution_node="报表节点-S7",
                progress=100,
                next_run="2026-03-22 18:00",
                last_run="2026-03-15 18:18",
                countdown="151:12:00",
                target="运营周报 / 选品、内容、互动与异常汇总",
                concurrency="2 并发",
                retries="发送失败自动补发 1 次",
                summary="每周日自动汇总本周运营数据并推送到管理群与邮件订阅列表。",
                notes="若邮件服务器延迟，将先推送群消息并在稍后补发邮件。",
                tags=("周报", "汇总推送", "管理群"),
                result_summary="周报已发送至 3 个群与 12 个邮箱订阅人",
                schedule_group="高频任务",
                timeline=(
                    {"timestamp": "2026-03-15 18:00:00", "title": "周报生成开始", "content": "已聚合选品、内容、互动与系统异常指标。", "type": "info"},
                    {"timestamp": "2026-03-15 18:18:42", "title": "推送完成", "content": "消息与邮件均发送成功。", "type": "success"},
                ),
            ),
        ]


__all__ = ["TaskSchedulerPage"]

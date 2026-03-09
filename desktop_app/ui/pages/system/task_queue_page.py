# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportArgumentType=false, reportPrivateUsage=false, reportImplicitOverride=false, reportUninitializedInstanceVariable=false, reportUnusedCallResult=false, reportUnknownParameterType=false, reportUnusedImport=false

from __future__ import annotations

"""任务队列页面。"""

from dataclasses import dataclass, replace

from ....core.types import RouteId
from ...components import ContentSection, DataTable, FilterDropdown, PageContainer, PrimaryButton, SearchBar, StatusBadge, TaskProgressBar
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_2XL,
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
from ...components.tags import BadgeTone
from ....core.qt import QHBoxLayout, QLabel, QPushButton, QWidget
from ..base_page import BasePage

TABLE_PAGE_SIZE = 4
TABLE_ROW_HEIGHT = SPACING_2XL * 4
SEARCH_MIN_WIDTH = SPACING_2XL * 14
FILTER_MIN_WIDTH = SPACING_2XL * 8
DESKTOP_PAGE_MAX_WIDTH = 1760


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


@dataclass(frozen=True)
class TaskQueueRecord:
    """任务队列中的单条任务记录。"""

    task_id: str
    task_type: str
    status: str
    progress: int
    created_time: str
    completed_time: str


class TaskQueuePage(BasePage):
    """系统模块下的任务队列页。"""

    default_route_id: RouteId = RouteId("task_queue")
    default_display_name: str = "任务队列"
    default_icon_name: str = "account_tree"

    def setup_ui(self) -> None:
        """构建任务搜索、筛选、表格与分页区域。"""

        self._all_tasks = self._mock_tasks()
        self._visible_tasks: list[TaskQueueRecord] = []
        self._cell_widgets: list[QWidget] = []
        self._selected_task_id: str | None = self._all_tasks[0].task_id if self._all_tasks else None
        self._next_task_index = len(self._all_tasks) + 1
        self._syncing_selection = False

        _call(self, "setObjectName", "taskQueuePage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._new_task_button = PrimaryButton("新建任务", self, icon_text="＋")

        page_container = PageContainer(
            title=self.display_name,
            description="集中查看队列中的批量任务、状态进度与执行动作，适合巡检、重试与快速调度。",
            actions=(self._new_task_button,),
            max_width=DESKTOP_PAGE_MAX_WIDTH,
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._toolbar = self._build_toolbar()
        page_container.add_widget(self._toolbar)

        self._table_section = ContentSection("任务列表", icon="▦", parent=page_container)
        self._summary_bar = self._build_summary_bar()
        self._task_table = DataTable(
            headers=("任务ID", "任务类型", "状态", "进度", "创建时间", "完成时间", "操作"),
            rows=(),
            page_size=TABLE_PAGE_SIZE,
            empty_text="当前筛选条件下暂无任务",
            parent=self._table_section,
        )

        _call(self._task_table.table_view, "setMinimumHeight", TABLE_ROW_HEIGHT * TABLE_PAGE_SIZE)
        vertical_header = getattr(self._task_table.table_view, "verticalHeader", lambda: None)()
        if vertical_header is not None:
            _call(vertical_header, "setDefaultSectionSize", TABLE_ROW_HEIGHT)

        self._table_section.add_widget(self._summary_bar)
        self._table_section.add_widget(self._task_table)
        page_container.add_widget(self._table_section)

        _connect(self._search_bar.search_changed, self._apply_filters)
        _connect(self._status_filter.filter_changed, self._apply_filters)
        _connect(getattr(self._new_task_button, "clicked", None), self._handle_new_task)
        _connect(self._task_table.row_selected, self._handle_row_selected)
        _connect(self._task_table.row_double_clicked, self._handle_row_double_clicked)

        task_model = getattr(self._task_table, "_model", None)
        if task_model is not None:
            _connect(getattr(task_model, "modelReset", None), self._refresh_cell_widgets)
            _connect(getattr(task_model, "layoutChanged", None), self._refresh_cell_widgets)

        self._apply_filters()

    def _build_toolbar(self) -> QWidget:
        """构建顶部搜索与筛选条。"""

        toolbar = QWidget(self)
        _call(toolbar, "setObjectName", "taskQueueToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_XL)

        self._search_bar = SearchBar("搜索任务名称或 ID...")
        self._status_filter = FilterDropdown("状态", ("进行中", "等待中", "已完成", "已暂停", "任务失败"))

        _call(self._search_bar, "setMinimumWidth", SEARCH_MIN_WIDTH)
        _call(self._status_filter, "setMinimumWidth", FILTER_MIN_WIDTH)

        layout.addWidget(self._search_bar, 1)
        layout.addWidget(self._status_filter)
        layout.addStretch(1)
        return toolbar

    def _build_summary_bar(self) -> QWidget:
        """构建表格上方的联动摘要区。"""

        summary = QWidget(self)
        _call(summary, "setObjectName", "taskQueueSummaryBar")
        layout = QHBoxLayout(summary)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_SM)

        self._result_badge = StatusBadge("筛选结果 0/0", tone="brand", parent=summary)
        self._running_badge = StatusBadge("进行中 0", tone="info", parent=summary)
        self._focus_badge = StatusBadge("未选择任务", tone="neutral", parent=summary)
        self._feedback_label = QLabel("支持搜索、筛选、暂停、重试与移除任务。", summary)
        _call(self._feedback_label, "setObjectName", "taskQueueFeedback")
        _call(self._feedback_label, "setWordWrap", True)

        layout.addWidget(self._result_badge)
        layout.addWidget(self._running_badge)
        layout.addWidget(self._focus_badge)
        layout.addStretch(1)
        layout.addWidget(self._feedback_label, 1)
        return summary

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        colors = _palette()
        brand_tint = _rgba(_token("brand.primary"), 0.08)
        brand_border = _rgba(_token("brand.primary"), 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#taskQueuePage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#taskQueueToolbar {{
                background-color: {colors.surface};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#taskQueueSummaryBar {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#taskQueuePage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#taskQueueSummaryBar {{
                padding: {SPACING_SM}px {SPACING_XL}px;
            }}
            QWidget#taskQueueToolbar {{
                padding: {SPACING_SM}px {SPACING_XL}px;
            }}
            QWidget#taskQueuePage QTableView {{
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#taskQueueFeedback {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QWidget#taskQueueStatusCell, QWidget#taskQueueProgressCell, QWidget#taskQueueActionCell {{
                background: transparent;
                border: none;
            }}
            QPushButton#taskQueueActionPrimary {{
                background-color: {brand_tint};
                color: {colors.text};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#taskQueueActionPrimary:hover {{
                border-color: {_token('brand.primary')};
                background-color: {_rgba(_token('brand.primary'), 0.14)};
            }}
            QPushButton#taskQueueActionDanger {{
                background-color: {_rgba(_token('status.error'), 0.10)};
                color: {_token('status.error')};
                border: 1px solid {_rgba(_token('status.error'), 0.18)};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#taskQueueActionDanger:hover {{
                background-color: {_rgba(_token('status.error'), 0.14)};
                border-color: {_token('status.error')};
            }}
            """,
        )

    def _apply_filters(self, *_args: object) -> None:
        """根据搜索词与状态筛选表格数据。"""

        keyword = self._search_bar.text().strip().lower()
        status = self._status_filter.current_text()

        self._visible_tasks = [
            task
            for task in self._all_tasks
            if (not keyword or keyword in f"{task.task_id} {task.task_type} {task.status}".lower())
            and (status in ("", "全部") or task.status == status)
        ]
        self._sync_selection_after_filter()
        self._task_table.set_rows(self._rows_for_tasks(self._visible_tasks))
        self._refresh_summary()
        self._sync_table_selection()
        self._refresh_cell_widgets()

    def _rows_for_tasks(self, tasks: list[TaskQueueRecord]) -> list[tuple[str, ...]]:
        """将任务对象转为 DataTable 行数据。"""

        return [
            (
                task.task_id,
                task.task_type,
                task.status,
                f"{task.progress}%",
                task.created_time,
                task.completed_time,
                self._primary_action_label(task),
            )
            for task in tasks
        ]

    def _refresh_summary(self) -> None:
        """刷新表格上方摘要。"""

        running_count = sum(1 for task in self._visible_tasks if task.status == "进行中")
        selected = self._selected_task()

        _call(self._result_badge, "setText", f"筛选结果 {len(self._visible_tasks)}/{len(self._all_tasks)}")
        _call(self._running_badge, "setText", f"进行中 {running_count}")

        if selected is None:
            _call(self._focus_badge, "setText", "未选择任务")
            self._focus_badge.set_tone("neutral")
            _call(self._feedback_label, "setText", "支持搜索、筛选、暂停、重试与移除任务。")
            return

        _call(self._focus_badge, "setText", f"焦点 {selected.task_id}")
        self._focus_badge.set_tone(self._status_tone(selected.status))
        _call(
            self._feedback_label,
            "setText",
            f"{selected.task_type} · {selected.status} · 进度 {selected.progress}% · 创建于 {selected.created_time}",
        )

    def _sync_selection_after_filter(self) -> None:
        """保证筛选后仍有有效选中项。"""

        visible_ids = {task.task_id for task in self._visible_tasks}
        if self._selected_task_id not in visible_ids:
            self._selected_task_id = self._visible_tasks[0].task_id if self._visible_tasks else None

    def _sync_table_selection(self) -> None:
        """将当前焦点任务同步到表格选中行。"""

        if not self._selected_task_id:
            return
        target_index = next(
            (index for index, task in enumerate(self._visible_tasks) if task.task_id == self._selected_task_id),
            -1,
        )
        if target_index < 0:
            return

        self._syncing_selection = True
        self._task_table.select_absolute_row(target_index)
        self._syncing_selection = False

    def _refresh_cell_widgets(self) -> None:
        """为状态、进度与操作列装配交互控件。"""

        self._clear_cell_widgets()
        table_view = self._task_table.table_view
        set_index_widget = getattr(table_view, "setIndexWidget", None)
        task_model = getattr(self._task_table, "_model", None)
        if not callable(set_index_widget) or task_model is None:
            return

        row_count = task_model.rowCount()
        for page_row in range(row_count):
            absolute_row = task_model.absolute_row(page_row)
            if not (0 <= absolute_row < len(self._visible_tasks)):
                continue
            task = self._visible_tasks[absolute_row]

            status_widget = self._build_status_cell(task)
            progress_widget = self._build_progress_cell(task)
            action_widget = self._build_action_cell(task)

            set_index_widget(task_model.index(page_row, 2), status_widget)
            set_index_widget(task_model.index(page_row, 3), progress_widget)
            set_index_widget(task_model.index(page_row, 6), action_widget)
            self._cell_widgets.extend((status_widget, progress_widget, action_widget))

    def _clear_cell_widgets(self) -> None:
        """释放当前页挂载过的单元格控件。"""

        for widget in self._cell_widgets:
            _call(widget, "setParent", None)
            _call(widget, "deleteLater")
        self._cell_widgets.clear()

    def _build_status_cell(self, task: TaskQueueRecord) -> QWidget:
        """创建状态列单元格。"""

        cell = QWidget(self._task_table)
        _call(cell, "setObjectName", "taskQueueStatusCell")
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        layout.setSpacing(0)

        badge = StatusBadge(task.status, tone=self._status_tone(task.status), parent=cell)
        layout.addStretch(1)
        layout.addWidget(badge)
        layout.addStretch(1)
        return cell

    def _build_progress_cell(self, task: TaskQueueRecord) -> QWidget:
        """创建进度列单元格。"""

        cell = QWidget(self._task_table)
        _call(cell, "setObjectName", "taskQueueProgressCell")
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(SPACING_SM, SPACING_XS, SPACING_SM, SPACING_XS)
        layout.setSpacing(0)

        progress_bar = TaskProgressBar(task.progress)
        _call(progress_bar, "setFixedHeight", TABLE_ROW_HEIGHT - SPACING_MD)
        layout.addWidget(progress_bar)
        return cell

    def _build_action_cell(self, task: TaskQueueRecord) -> QWidget:
        """创建操作列单元格。"""

        cell = QWidget(self._task_table)
        _call(cell, "setObjectName", "taskQueueActionCell")
        layout = QHBoxLayout(cell)
        layout.setContentsMargins(SPACING_SM, SPACING_SM, SPACING_SM, SPACING_SM)
        layout.setSpacing(SPACING_SM)

        primary_button = QPushButton(self._primary_action_label(task), cell)
        _call(primary_button, "setObjectName", "taskQueueActionPrimary")
        remove_button = QPushButton(self._danger_action_label(task), cell)
        _call(remove_button, "setObjectName", "taskQueueActionDanger")

        _connect(getattr(primary_button, "clicked", None), lambda checked=False, task_id=task.task_id: self._handle_primary_action(task_id))
        _connect(getattr(remove_button, "clicked", None), lambda checked=False, task_id=task.task_id: self._handle_remove_action(task_id))

        layout.addWidget(primary_button)
        layout.addWidget(remove_button)
        layout.addStretch(1)
        return cell

    def _handle_row_selected(self, row_index: int) -> None:
        """表格选中行变化时更新焦点任务。"""

        if self._syncing_selection or not (0 <= row_index < len(self._visible_tasks)):
            return
        self._selected_task_id = self._visible_tasks[row_index].task_id
        self._refresh_summary()

    def _handle_row_double_clicked(self, row_index: int) -> None:
        """双击表格行时视为查看任务。"""

        if not (0 <= row_index < len(self._visible_tasks)):
            return
        self._handle_view_task(self._visible_tasks[row_index].task_id)

    def _handle_view_task(self, task_id: str) -> None:
        """聚焦并提示当前任务。"""

        self._selected_task_id = task_id
        self._refresh_summary()
        self._sync_table_selection()

    def _handle_new_task(self) -> None:
        """创建一条新的 mock 队列任务。"""

        new_task = TaskQueueRecord(
            task_id=f"TASK-{self._next_task_index:04d}",
            task_type="批量数据校验",
            status="等待中",
            progress=0,
            created_time="2026-03-08 16:20",
            completed_time="—",
        )
        self._next_task_index += 1
        self._all_tasks.insert(0, new_task)
        self._selected_task_id = new_task.task_id
        _call(self._feedback_label, "setText", f"已创建任务 {new_task.task_id}，当前处于等待队列。")
        self._apply_filters()

    def _handle_primary_action(self, task_id: str) -> None:
        """根据任务当前状态执行主操作。"""

        task = self._task_by_id(task_id)
        if task is None:
            return

        if task.status == "进行中":
            updated = replace(task, status="已暂停", completed_time="—")
            feedback = f"{task.task_id} 已暂停。"
        elif task.status == "任务失败":
            updated = replace(task, status="进行中", progress=max(16, task.progress), completed_time="—")
            feedback = f"{task.task_id} 已重新加入执行。"
        elif task.status in {"等待中", "已暂停"}:
            updated = replace(task, status="进行中", progress=max(10, task.progress), completed_time="—")
            feedback = f"{task.task_id} 已启动执行。"
        else:
            updated = task
            feedback = f"已查看 {task.task_id} 的任务详情。"

        self._replace_task(updated)
        self._selected_task_id = updated.task_id
        _call(self._feedback_label, "setText", feedback)
        self._apply_filters()

    def _handle_remove_action(self, task_id: str) -> None:
        """移除任务。"""

        task = self._task_by_id(task_id)
        if task is None:
            return
        self._all_tasks = [item for item in self._all_tasks if item.task_id != task_id]
        if self._selected_task_id == task_id:
            self._selected_task_id = None
        _call(self._feedback_label, "setText", f"{task.task_id} 已从任务队列中移除。")
        self._apply_filters()

    def _replace_task(self, updated: TaskQueueRecord) -> None:
        """替换列表中的指定任务。"""

        self._all_tasks = [updated if task.task_id == updated.task_id else task for task in self._all_tasks]

    def _task_by_id(self, task_id: str) -> TaskQueueRecord | None:
        """按任务 ID 获取任务。"""

        return next((task for task in self._all_tasks if task.task_id == task_id), None)

    def _selected_task(self) -> TaskQueueRecord | None:
        """返回当前选中的任务。"""

        return self._task_by_id(self._selected_task_id) if self._selected_task_id else None

    @staticmethod
    def _status_tone(status: str) -> BadgeTone:
        """将任务状态映射到徽标语义色。"""

        mapping: dict[str, BadgeTone] = {
            "进行中": "info",
            "等待中": "neutral",
            "已完成": "success",
            "已暂停": "warning",
            "任务失败": "error",
        }
        return mapping.get(status, "neutral")

    @staticmethod
    def _primary_action_label(task: TaskQueueRecord) -> str:
        """返回主操作按钮文案。"""

        if task.status == "进行中":
            return "暂停"
        if task.status == "任务失败":
            return "重试"
        if task.status in {"等待中", "已暂停"}:
            return "启动"
        return "查看"

    @staticmethod
    def _danger_action_label(task: TaskQueueRecord) -> str:
        """返回危险操作按钮文案。"""

        return "移除" if task.status == "已完成" else "取消"

    @staticmethod
    def _mock_tasks() -> list[TaskQueueRecord]:
        """返回页面使用的静态 mock 任务。"""

        return [
            TaskQueueRecord("TASK-3201", "商品同步", "进行中", 68, "2026-03-08 09:10", "—"),
            TaskQueueRecord("TASK-3202", "店铺健康巡检", "任务失败", 42, "2026-03-08 08:45", "—"),
            TaskQueueRecord("TASK-3203", "素材审核分发", "等待中", 0, "2026-03-08 08:30", "—"),
            TaskQueueRecord("TASK-3204", "短视频脚本生成", "已完成", 100, "2026-03-08 07:50", "2026-03-08 08:12"),
            TaskQueueRecord("TASK-3205", "账号环境诊断", "已暂停", 57, "2026-03-08 07:30", "—"),
            TaskQueueRecord("TASK-3206", "评论意图归类", "进行中", 24, "2026-03-08 07:05", "—"),
            TaskQueueRecord("TASK-3207", "达人名单清洗", "已完成", 100, "2026-03-08 06:40", "2026-03-08 07:18"),
            TaskQueueRecord("TASK-3208", "广告素材压缩", "等待中", 0, "2026-03-08 06:10", "—"),
            TaskQueueRecord("TASK-3209", "跨店库存对齐", "进行中", 83, "2026-03-08 05:55", "—"),
        ]


__all__ = ["TaskQueuePage"]

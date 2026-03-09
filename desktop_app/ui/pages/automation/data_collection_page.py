# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportPrivateUsage=false, reportUnusedImport=false, reportUninitializedInstanceVariable=false, reportUnannotatedClassAttribute=false, reportArgumentType=false, reportImplicitOverride=false, reportUnusedCallResult=false

from __future__ import annotations

"""数据采集助手页面。"""

from dataclasses import dataclass, replace

from ....core.types import RouteId
from ...components import (
    ContentSection,
    DataTable,
    PageContainer,
    PrimaryButton,
    SearchBar,
    StatusBadge,
    TabBar,
    TaskProgressBar,
    ThemedComboBox,
    ThemedLineEdit,
)
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_2XL,
    SPACING_LG,
    SPACING_MD,
    SPACING_XL,
    SPACING_XS,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ..base_page import BasePage

SEARCH_MIN_WIDTH = SPACING_2XL * 12
TABLE_PAGE_SIZE = 5
ACTIVE_TASK_LIMIT = 4


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _clear_layout(layout: object) -> None:
    """安全清空布局中的全部子项。"""

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
    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


@dataclass(frozen=True)
class CollectionTask:
    """数据采集任务模型。"""

    task_id: str
    source_url: str
    collection_type: str
    frequency: str
    max_items: int
    collected_items: int
    progress: int
    status: str
    last_update: str


@dataclass(frozen=True)
class ActiveListBinding:
    """活跃任务列表绑定。"""

    layout: QVBoxLayout
    summary_badge: StatusBadge
    statuses: tuple[str, ...]
    empty_text: str


@dataclass(frozen=True)
class ResultsBinding:
    """结果表格绑定。"""

    key: str
    table: DataTable
    summary_badge: StatusBadge
    statuses: tuple[str, ...] | None
    empty_text: str


class DataCollectionPage(BasePage):
    """自动化模块下的数据采集助手。"""

    default_route_id: RouteId = RouteId("data_collection_assistant")
    default_display_name: str = "数据采集助手"
    default_icon_name: str = "analytics"

    def setup_ui(self) -> None:
        """构建数据采集助手页面。"""

        self._tasks = self._mock_tasks()
        self._selected_task_id: str | None = self._tasks[0].task_id if self._tasks else None
        self._next_task_index = len(self._tasks) + 2400
        self._active_bindings: list[ActiveListBinding] = []
        self._results_bindings: list[ResultsBinding] = []
        self._results_rows_by_key: dict[str, list[CollectionTask]] = {}

        _call(self, "setObjectName", "dataCollectionPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._global_search = SearchBar("搜索任务、URL 或采集类型", self)
        _call(self._global_search, "setMinimumWidth", SEARCH_MIN_WIDTH)
        self._api_badge = StatusBadge("Apify API 已连接", tone="success", parent=self)
        self._focus_badge = StatusBadge("未聚焦任务", tone="neutral", parent=self)
        self._new_task_button = PrimaryButton("新建任务", self, icon_text="＋")

        page_container = PageContainer(
            title=self.display_name,
            description="配置并监控采集任务，快速搭建 URL 抓取、频率调度与结果预览工作流。",
            actions=(self._global_search, self._api_badge, self._focus_badge, self._new_task_button),
            parent=self,
        )
        self.layout.addWidget(page_container)

        self._summary_strip = self._build_summary_strip()
        page_container.add_widget(self._summary_strip)

        self._tab_bar = TabBar(page_container)
        self._tab_bar.add_tab("新建任务", self._build_new_task_tab())
        self._tab_bar.add_tab("进行中", self._build_running_tab())
        self._tab_bar.add_tab("已完成", self._build_completed_tab())
        self._tab_bar.add_tab("历史记录", self._build_history_tab())
        page_container.add_widget(self._tab_bar)

        _connect(self._global_search.search_changed, self._refresh_views)
        _connect(getattr(self._create_button, "clicked", None), self._handle_create_task)
        _connect(getattr(self._new_task_button, "clicked", None), self._focus_create_tab)

        self._refresh_views()

    def _focus_create_tab(self) -> None:
        """聚焦到新建任务标签页。"""

        self._tab_bar.set_current(0)
        _call(self._form_state_badge, "setText", "开始新建")
        self._form_state_badge.set_tone("brand")
        _call(self._form_feedback, "setText", "请填写目标 URL、采集类型与条目上限，然后开始采集。")

    def _build_summary_strip(self) -> QWidget:
        """构建顶部概览条。"""

        strip = QWidget(self)
        _call(strip, "setObjectName", "dataCollectionSummaryStrip")
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_MD)

        self._running_badge = StatusBadge("进行中 0", tone="info", parent=strip)
        self._completed_badge = StatusBadge("已完成 0", tone="success", parent=strip)
        self._history_badge = StatusBadge("历史任务 0", tone="brand", parent=strip)
        self._summary_hint = QLabel("顶部搜索会同步过滤进行中任务与结果预览。", strip)
        _call(self._summary_hint, "setObjectName", "dataCollectionSummaryHint")
        _call(self._summary_hint, "setWordWrap", True)

        layout.addWidget(self._running_badge)
        layout.addWidget(self._completed_badge)
        layout.addWidget(self._history_badge)
        layout.addStretch(1)
        layout.addWidget(self._summary_hint, 1)
        return strip

    def _build_new_task_tab(self) -> QWidget:
        """构建新建任务标签页。"""

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        layout.addWidget(self._build_task_form_section(page))
        layout.addWidget(
            self._build_active_tasks_section(
                title="进行中的任务",
                statuses=("进行中", "已暂停"),
                empty_text="暂无进行中的采集任务，先创建一个新任务。",
                parent=page,
            )
        )
        layout.addWidget(
            self._build_results_section(
                key="new_preview",
                title="结果预览",
                statuses=None,
                empty_text="暂无采集记录可预览。",
                parent=page,
            )
        )
        layout.addStretch(1)
        return page

    def _build_running_tab(self) -> QWidget:
        """构建进行中标签页。"""

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        layout.addWidget(
            self._build_active_tasks_section(
                title="活跃采集任务",
                statuses=("进行中", "已暂停"),
                empty_text="当前没有需要监控的活跃采集任务。",
                parent=page,
            )
        )
        layout.addWidget(
            self._build_results_section(
                key="running_preview",
                title="实时结果预览",
                statuses=("进行中", "已暂停"),
                empty_text="没有命中筛选条件的活跃结果。",
                parent=page,
            )
        )
        layout.addStretch(1)
        return page

    def _build_completed_tab(self) -> QWidget:
        """构建已完成标签页。"""

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        layout.addWidget(
            self._build_results_section(
                key="completed_preview",
                title="已完成结果",
                statuses=("已完成",),
                empty_text="还没有已完成的采集任务。",
                parent=page,
            )
        )
        layout.addStretch(1)
        return page

    def _build_history_tab(self) -> QWidget:
        """构建历史记录标签页。"""

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        layout.addWidget(
            self._build_results_section(
                key="history_preview",
                title="历史采集记录",
                statuses=None,
                empty_text="当前没有历史采集记录。",
                parent=page,
            )
        )
        layout.addStretch(1)
        return page

    def _build_task_form_section(self, parent: QWidget) -> ContentSection:
        """构建新建任务表单区。"""

        section = ContentSection("创建新采集任务", icon="◉", parent=parent)

        shell = QWidget(section)
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XL)

        first_row = QHBoxLayout()
        first_row.setSpacing(SPACING_XL)
        second_row = QHBoxLayout()
        second_row.setSpacing(SPACING_XL)

        self._url_input = ThemedLineEdit(
            label="目标 URL",
            placeholder="https://www.tiktok.com/@account 或商品链接",
            helper_text="支持 TikTok 主页、视频、话题与商品详情链接。",
            parent=shell,
        )
        self._type_combo = ThemedComboBox(
            label="采集类型",
            items=("用户主页", "视频内容", "话题标签", "商品详情"),
            parent=shell,
        )
        self._frequency_combo = ThemedComboBox(
            label="采集频率",
            items=("单次采集", "每小时", "每日 09:00", "每周一 08:00"),
            parent=shell,
        )
        self._max_items_input = ThemedLineEdit(
            label="最大条目数",
            placeholder="500",
            helper_text="建议 100-5000 条，避免单次任务过大。",
            parent=shell,
        )
        self._max_items_input.setText("500")

        first_row.addWidget(self._url_input, 2)
        first_row.addWidget(self._type_combo, 1)
        second_row.addWidget(self._frequency_combo, 1)
        second_row.addWidget(self._max_items_input, 1)

        footer = QWidget(shell)
        _call(footer, "setObjectName", "dataCollectionFormFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(SPACING_MD)

        self._form_state_badge = StatusBadge("待创建", tone="brand", parent=footer)
        self._form_feedback = QLabel("创建后任务会立即进入进行中列表。", footer)
        _call(self._form_feedback, "setObjectName", "dataCollectionFormFeedback")
        _call(self._form_feedback, "setWordWrap", True)
        self._create_button = PrimaryButton("开始采集", footer, icon_text="＋")

        footer_layout.addWidget(self._form_state_badge)
        footer_layout.addWidget(self._form_feedback, 1)
        footer_layout.addWidget(self._create_button)

        layout.addLayout(first_row)
        layout.addLayout(second_row)
        layout.addWidget(footer)
        section.add_widget(shell)
        return section

    def _build_active_tasks_section(
        self,
        *,
        title: str,
        statuses: tuple[str, ...],
        empty_text: str,
        parent: QWidget,
    ) -> ContentSection:
        """构建活跃任务区。"""

        section = ContentSection(title, icon="↻", parent=parent)

        summary = QWidget(section)
        _call(summary, "setObjectName", "dataCollectionSectionSummary")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_MD)

        badge = StatusBadge("0 个任务", tone="info", parent=summary)
        hint = QLabel("支持推进、暂停、完成或取消任务。", summary)
        _call(hint, "setObjectName", "dataCollectionSectionHint")
        _call(hint, "setWordWrap", True)

        summary_layout.addWidget(badge)
        summary_layout.addStretch(1)
        summary_layout.addWidget(hint, 1)

        host = QWidget(section)
        _call(host, "setObjectName", "dataCollectionActiveHost")
        host_layout = QVBoxLayout(host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(SPACING_XL)

        self._active_bindings.append(ActiveListBinding(host_layout, badge, statuses, empty_text))
        section.add_widget(summary)
        section.add_widget(host)
        return section

    def _build_results_section(
        self,
        *,
        key: str,
        title: str,
        statuses: tuple[str, ...] | None,
        empty_text: str,
        parent: QWidget,
    ) -> ContentSection:
        """构建结果表格区。"""

        section = ContentSection(title, icon="▦", parent=parent)

        summary = QWidget(section)
        _call(summary, "setObjectName", "dataCollectionSectionSummary")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_MD)

        badge = StatusBadge("0 条记录", tone="brand", parent=summary)
        hint = QLabel("双击结果表可将任务设置为当前聚焦对象。", summary)
        _call(hint, "setObjectName", "dataCollectionSectionHint")
        _call(hint, "setWordWrap", True)

        summary_layout.addWidget(badge)
        summary_layout.addStretch(1)
        summary_layout.addWidget(hint, 1)

        table = DataTable(
            headers=("任务 ID", "类型", "目标", "频率", "数据量", "状态", "最近更新"),
            rows=(),
            page_size=TABLE_PAGE_SIZE,
            empty_text=empty_text,
            parent=section,
        )

        self._results_bindings.append(ResultsBinding(key, table, badge, statuses, empty_text))
        _connect(table.row_selected, lambda row, binding_key=key: self._handle_table_selection(binding_key, row))
        _connect(table.row_double_clicked, lambda row, binding_key=key: self._handle_table_double_click(binding_key, row))

        section.add_widget(summary)
        section.add_widget(table)
        return section

    def _refresh_views(self, *_args: object) -> None:
        """刷新全部绑定视图。"""

        self._refresh_summary_strip()
        self._refresh_active_lists()
        self._refresh_results_tables()

    def _refresh_summary_strip(self) -> None:
        """刷新顶部概览与焦点状态。"""

        running_count = sum(1 for task in self._tasks if task.status in {"进行中", "已暂停"})
        completed_count = sum(1 for task in self._tasks if task.status == "已完成")

        _call(self._running_badge, "setText", f"进行中 {running_count}")
        _call(self._completed_badge, "setText", f"已完成 {completed_count}")
        _call(self._history_badge, "setText", f"历史任务 {len(self._tasks)}")

        selected = self._selected_task()
        if selected is None:
            _call(self._focus_badge, "setText", "未聚焦任务")
            self._focus_badge.set_tone("neutral")
            _call(self._summary_hint, "setText", "顶部搜索会同步过滤进行中任务与结果预览，右上角可快速新建任务。")
            return

        _call(self._focus_badge, "setText", f"焦点 {selected.task_id}")
        self._focus_badge.set_tone(self._status_tone(selected.status))
        _call(
            self._summary_hint,
            "setText",
            f"当前聚焦 {selected.task_id}，状态为 {selected.status}，可在列表或结果预览中继续推进。",
        )

    def _refresh_active_lists(self) -> None:
        """刷新所有活跃任务卡片列表。"""

        for binding in self._active_bindings:
            tasks = self._filtered_tasks(binding.statuses)[:ACTIVE_TASK_LIMIT]
            _call(binding.summary_badge, "setText", f"{len(tasks)} 个任务")
            _clear_layout(binding.layout)

            if not tasks:
                binding.layout.addWidget(self._build_empty_state(binding.empty_text))
                continue

            for task in tasks:
                binding.layout.addWidget(self._build_task_card(task))
            binding.layout.addStretch(1)

    def _refresh_results_tables(self) -> None:
        """刷新全部结果表格。"""

        for binding in self._results_bindings:
            tasks = self._filtered_tasks(binding.statuses)
            self._results_rows_by_key[binding.key] = tasks
            binding.table.set_rows(self._rows_for_tasks(tasks))
            _call(binding.summary_badge, "setText", f"{len(tasks)} 条记录")

    def _build_task_card(self, task: CollectionTask) -> QFrame:
        """创建单个活跃任务卡片。"""

        card = QFrame(self)
        _call(card, "setObjectName", "dataCollectionTaskCard")
        _call(card, "setProperty", "selected", task.task_id == self._selected_task_id)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_LG)

        header = QWidget(card)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)

        title_box = QWidget(header)
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_XS)

        title = QLabel(task.task_id, title_box)
        _call(title, "setObjectName", "dataCollectionTaskTitle")
        subtitle = QLabel(self._display_target(task.source_url), title_box)
        _call(subtitle, "setObjectName", "dataCollectionTaskSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        type_pill = QLabel(task.collection_type, header)
        _call(type_pill, "setObjectName", "dataCollectionTypePill")
        status_badge = StatusBadge(task.status, tone=self._status_tone(task.status), parent=header)

        header_layout.addWidget(title_box, 1)
        header_layout.addWidget(type_pill)
        header_layout.addWidget(status_badge)

        metrics = QWidget(card)
        metrics_layout = QHBoxLayout(metrics)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(SPACING_LG)
        metrics_layout.addWidget(self._build_metric_block("频率", task.frequency, metrics))
        metrics_layout.addWidget(self._build_metric_block("上限", f"{task.max_items} 条", metrics))
        metrics_layout.addWidget(self._build_metric_block("已采集", f"{task.collected_items} 条", metrics))
        metrics_layout.addStretch(1)

        progress_bar = TaskProgressBar(task.progress, card)

        footer = QWidget(card)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(SPACING_MD)

        last_update = QLabel(f"最近更新：{task.last_update}", footer)
        _call(last_update, "setObjectName", "dataCollectionTaskMeta")

        advance_button = QPushButton("推进 15%", footer)
        _call(advance_button, "setObjectName", "dataCollectionGhostButton")
        _connect(getattr(advance_button, "clicked", None), lambda checked=False, task_id=task.task_id: self._advance_task(task_id))

        toggle_button = QPushButton("继续" if task.status == "已暂停" else "暂停", footer)
        _call(toggle_button, "setObjectName", "dataCollectionGhostButton")
        _connect(getattr(toggle_button, "clicked", None), lambda checked=False, task_id=task.task_id: self._toggle_task(task_id))

        finish_button = QPushButton("完成" if task.status != "已完成" else "查看", footer)
        _call(finish_button, "setObjectName", "dataCollectionGhostButton")
        _connect(getattr(finish_button, "clicked", None), lambda checked=False, task_id=task.task_id: self._complete_task(task_id))

        cancel_button = QPushButton("取消", footer)
        _call(cancel_button, "setObjectName", "dataCollectionDangerButton")
        _connect(getattr(cancel_button, "clicked", None), lambda checked=False, task_id=task.task_id: self._cancel_task(task_id))

        footer_layout.addWidget(last_update, 1)
        footer_layout.addWidget(advance_button)
        footer_layout.addWidget(toggle_button)
        footer_layout.addWidget(finish_button)
        footer_layout.addWidget(cancel_button)

        layout.addWidget(header)
        layout.addWidget(metrics)
        layout.addWidget(progress_bar)
        layout.addWidget(footer)
        return card

    def _build_metric_block(self, label: str, value: str, parent: QWidget) -> QWidget:
        """构建卡片中的紧凑指标块。"""

        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_XS)

        title = QLabel(label, widget)
        _call(title, "setObjectName", "dataCollectionMetricLabel")
        content = QLabel(value, widget)
        _call(content, "setObjectName", "dataCollectionMetricValue")

        layout.addWidget(title)
        layout.addWidget(content)
        return widget

    def _build_empty_state(self, text: str) -> QLabel:
        """构建空状态提示。"""

        label = QLabel(text, self)
        _call(label, "setObjectName", "dataCollectionEmptyState")
        _call(label, "setWordWrap", True)
        return label

    def _handle_create_task(self) -> None:
        """创建新的采集任务。"""

        url = self._url_input.text().strip()
        max_items_text = self._max_items_input.text().strip()

        self._url_input.clear_error()
        self._max_items_input.clear_error()

        if not url:
            self._url_input.set_error("请输入有效的目标 URL。")
            _call(self._form_state_badge, "setText", "URL 缺失")
            self._form_state_badge.set_tone("warning")
            _call(self._form_feedback, "setText", "任务创建失败：目标 URL 不能为空。")
            return

        if not max_items_text.isdigit() or int(max_items_text) <= 0:
            self._max_items_input.set_error("最大条目数需要是正整数。")
            _call(self._form_state_badge, "setText", "条目数错误")
            self._form_state_badge.set_tone("warning")
            _call(self._form_feedback, "setText", "任务创建失败：请填写正确的最大条目数。")
            return

        new_task = CollectionTask(
            task_id=f"COL-{self._next_task_index}",
            source_url=url,
            collection_type=self._type_combo.current_text(),
            frequency=self._frequency_combo.current_text(),
            max_items=int(max_items_text),
            collected_items=0,
            progress=0,
            status="进行中",
            last_update="刚刚创建",
        )
        self._next_task_index += 1
        self._tasks.insert(0, new_task)
        self._selected_task_id = new_task.task_id

        self._url_input.setText("")
        self._max_items_input.setText("500")
        _call(self._form_state_badge, "setText", "创建成功")
        self._form_state_badge.set_tone("success")
        _call(self._form_feedback, "setText", f"{new_task.task_id} 已进入进行中列表，可立即监控进度。")
        self._tab_bar.set_current(1)
        self._refresh_views()

    def _advance_task(self, task_id: str) -> None:
        """推进任务进度。"""

        task = self._task_by_id(task_id)
        if task is None or task.status == "已取消":
            return
        if task.status == "已暂停":
            task = replace(task, status="进行中", last_update="从暂停恢复")

        next_progress = min(100, task.progress + 15)
        next_items = min(task.max_items, max(task.collected_items, int(task.max_items * next_progress / 100)))
        next_status = "已完成" if next_progress >= 100 else "进行中"
        next_update = "已完成并写入结果预览" if next_status == "已完成" else "正在抓取新批次数据"
        self._replace_task(
            replace(
                task,
                progress=next_progress,
                collected_items=next_items,
                status=next_status,
                last_update=next_update,
            )
        )
        self._selected_task_id = task_id
        self._refresh_views()

    def _toggle_task(self, task_id: str) -> None:
        """暂停或恢复任务。"""

        task = self._task_by_id(task_id)
        if task is None or task.status in {"已完成", "已取消"}:
            return
        next_status = "已暂停" if task.status == "进行中" else "进行中"
        next_update = "任务已暂停，等待继续" if next_status == "已暂停" else "任务已恢复执行"
        self._replace_task(replace(task, status=next_status, last_update=next_update))
        self._selected_task_id = task_id
        self._refresh_views()

    def _complete_task(self, task_id: str) -> None:
        """直接完成任务。"""

        task = self._task_by_id(task_id)
        if task is None:
            return
        self._replace_task(
            replace(
                task,
                progress=100,
                collected_items=task.max_items,
                status="已完成",
                last_update="手动标记为已完成",
            )
        )
        self._selected_task_id = task_id
        self._refresh_views()

    def _cancel_task(self, task_id: str) -> None:
        """取消任务。"""

        task = self._task_by_id(task_id)
        if task is None:
            return
        self._replace_task(replace(task, status="已取消", last_update="任务已取消"))
        self._selected_task_id = task_id
        self._refresh_views()

    def _handle_table_selection(self, binding_key: str, row_index: int) -> None:
        """处理结果表格选中。"""

        tasks = self._results_rows_by_key.get(binding_key, [])
        if not (0 <= row_index < len(tasks)):
            return
        self._selected_task_id = tasks[row_index].task_id
        self._refresh_views()

    def _handle_table_double_click(self, binding_key: str, row_index: int) -> None:
        """处理结果表格双击。"""

        self._handle_table_selection(binding_key, row_index)
        selected = self._selected_task()
        if selected is None:
            return
        target_tab = 2 if selected.status == "已完成" else 1 if selected.status in {"进行中", "已暂停"} else 3
        self._tab_bar.set_current(target_tab)

    def _filtered_tasks(self, statuses: tuple[str, ...] | None = None) -> list[CollectionTask]:
        """根据顶部搜索与状态过滤任务。"""

        keyword = self._global_search.text().strip().lower()
        tasks = [task for task in self._tasks if statuses is None or task.status in statuses]
        if not keyword:
            return tasks
        return [
            task
            for task in tasks
            if keyword in f"{task.task_id} {task.source_url} {task.collection_type} {task.frequency} {task.status}".lower()
        ]

    def _rows_for_tasks(self, tasks: list[CollectionTask]) -> list[tuple[str, str, str, str, str, str, str]]:
        """将任务转换为表格行。"""

        return [
            (
                task.task_id,
                task.collection_type,
                self._display_target(task.source_url),
                task.frequency,
                f"{task.collected_items}/{task.max_items}",
                task.status,
                task.last_update,
            )
            for task in tasks
        ]

    def _replace_task(self, updated: CollectionTask) -> None:
        """替换任务列表中的指定项。"""

        self._tasks = [updated if task.task_id == updated.task_id else task for task in self._tasks]

    def _task_by_id(self, task_id: str) -> CollectionTask | None:
        """按 ID 获取任务。"""

        return next((task for task in self._tasks if task.task_id == task_id), None)

    def _selected_task(self) -> CollectionTask | None:
        """返回当前聚焦任务。"""

        if self._selected_task_id is None:
            return None
        return self._task_by_id(self._selected_task_id)

    @staticmethod
    def _display_target(url: str) -> str:
        """将目标 URL 格式化为紧凑展示文本。"""

        compact = url.replace("https://", "").replace("http://", "")
        return compact if len(compact) <= 34 else f"{compact[:31]}…"

    @staticmethod
    def _status_tone(status: str) -> str:
        """映射任务状态到徽标色调。"""

        mapping = {
            "进行中": "info",
            "已暂停": "warning",
            "已完成": "success",
            "已取消": "neutral",
        }
        return mapping.get(status, "neutral")

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        colors = _palette()
        brand_tint = _rgba(_token("brand.primary"), 0.10)
        brand_border = _rgba(_token("brand.primary"), 0.22)
        danger_tint = _rgba(_token("status.error"), 0.10)
        danger_border = _rgba(_token("status.error"), 0.22)
        selected_ring = _rgba(_token("brand.primary"), 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#dataCollectionPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#dataCollectionSummaryStrip,
            QWidget#dataCollectionSectionSummary,
            QWidget#dataCollectionFormFooter {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#dataCollectionSummaryHint,
            QLabel#dataCollectionSectionHint,
            QLabel#dataCollectionFormFeedback,
            QLabel#dataCollectionTaskSubtitle,
            QLabel#dataCollectionTaskMeta,
            QLabel#dataCollectionMetricLabel {{
                color: {colors.text_muted};
                background: transparent;
                font-size: {_static_token('font.size.sm')};
            }}
            QFrame#dataCollectionTaskCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#dataCollectionTaskCard[selected="true"] {{
                border: 1px solid {_token('brand.primary')};
                background-color: {selected_ring};
            }}
            QLabel#dataCollectionTaskTitle {{
                color: {colors.text};
                background: transparent;
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#dataCollectionMetricValue {{
                color: {colors.text};
                background: transparent;
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#dataCollectionTypePill {{
                color: {_token('brand.primary')};
                background-color: {brand_tint};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QLabel#dataCollectionEmptyState {{
                color: {colors.text_muted};
                background-color: {colors.surface};
                border: 1px dashed {colors.border};
                border-radius: {RADIUS_LG}px;
                padding: {SPACING_XL}px;
                font-size: {_static_token('font.size.md')};
            }}
            QPushButton#dataCollectionGhostButton {{
                background-color: {brand_tint};
                color: {colors.text};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#dataCollectionGhostButton:hover {{
                background-color: {_rgba(_token('brand.primary'), 0.16)};
                border-color: {_token('brand.primary')};
            }}
            QPushButton#dataCollectionDangerButton {{
                background-color: {danger_tint};
                color: {_token('status.error')};
                border: 1px solid {danger_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_LG}px;
                min-height: {BUTTON_HEIGHT}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QPushButton#dataCollectionDangerButton:hover {{
                background-color: {_rgba(_token('status.error'), 0.16)};
                border-color: {_token('status.error')};
            }}
            """,
        )

    @staticmethod
    def _mock_tasks() -> list[CollectionTask]:
        """返回页面使用的静态 mock 任务。"""

        return [
            CollectionTask(
                task_id="COL-2401",
                source_url="https://www.tiktok.com/@techlab.cn",
                collection_type="用户主页",
                frequency="单次采集",
                max_items=1200,
                collected_items=816,
                progress=68,
                status="进行中",
                last_update="2 分钟前",
            ),
            CollectionTask(
                task_id="COL-2402",
                source_url="https://www.tiktok.com/@beautylab/video/74200001",
                collection_type="视频内容",
                frequency="每小时",
                max_items=300,
                collected_items=96,
                progress=32,
                status="已暂停",
                last_update="等待人工继续",
            ),
            CollectionTask(
                task_id="COL-2403",
                source_url="https://www.tiktok.com/tag/summerfinds",
                collection_type="话题标签",
                frequency="每日 09:00",
                max_items=800,
                collected_items=112,
                progress=14,
                status="进行中",
                last_update="刚抓取第 3 批样本",
            ),
            CollectionTask(
                task_id="COL-2398",
                source_url="https://shop.tiktok.com/view/product/1730021",
                collection_type="商品详情",
                frequency="每周一 08:00",
                max_items=650,
                collected_items=650,
                progress=100,
                status="已完成",
                last_update="今天 11:40 完成",
            ),
            CollectionTask(
                task_id="COL-2394",
                source_url="https://www.tiktok.com/@archived.account",
                collection_type="用户主页",
                frequency="单次采集",
                max_items=5000,
                collected_items=0,
                progress=0,
                status="已取消",
                last_update="昨天 18:20 已取消",
            ),
        ]


__all__ = ["DataCollectionPage"]

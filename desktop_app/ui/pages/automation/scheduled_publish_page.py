# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportCallIssue=false, reportGeneralTypeIssues=false, reportAssignmentType=false

from __future__ import annotations

"""定时发布页面。"""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime, timedelta
from ....core.types import RouteId
from ...components import (
    CalendarWidget,
    ContentSection,
    DataTable,
    FormGroup,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TagInput,
    ThemedComboBox,
    ThemedLineEdit,
    ThemedTextEdit,
)
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
from ...components.operations import QDate
from ...components.tags import BadgeTone
from ..base_page import BasePage

TABLE_PAGE_SIZE = 8
MONTH_PLAN_TARGET = 12
PROGRESS_TRACK_WIDTH = SPACING_2XL * 9
SEARCH_MIN_WIDTH = SPACING_2XL * 12


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _clear_layout(layout: object) -> None:
    """清空布局中的全部子项。"""

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


def _iso_text(date_value: QDate) -> str:
    """将 QDate 序列化为 ISO 日期。"""

    return f"{date_value.year():04d}-{date_value.month():02d}-{date_value.day():02d}"


def _qdate_from_iso(iso_text: str) -> QDate:
    """根据 ISO 日期生成 QDate。"""

    parsed = datetime.strptime(iso_text, "%Y-%m-%d")
    return QDate(parsed.year, parsed.month, parsed.day)


def _compact_title(title: str, limit: int = 18) -> str:
    """压缩标题用于日历和表格展示。"""

    cleaned = title.strip()
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1]}…"


@dataclass(frozen=True)
class ScheduledPost:
    """定时发布任务模型。"""

    post_id: str
    title: str
    description: str
    publish_date: str
    publish_time: str
    category: str
    status: str
    tags: tuple[str, ...]
    asset_name: str
    reminder: str


class ScheduledPublishPage(BasePage):
    """自动化模块下的定时发布页面。"""

    default_route_id: RouteId = RouteId("scheduled_publishing")
    default_display_name: str = "定时发布"
    default_icon_name: str = "schedule"

    def setup_ui(self) -> None:
        """构建定时发布页面。"""

        self._posts = self._build_mock_posts()
        self._visible_posts: list[ScheduledPost] = []
        self._selected_post_id: str | None = self._posts[0].post_id if self._posts else None
        self._selected_asset_name: str = self._posts[0].asset_name if self._posts else "春日旅行 Vlog.mp4"
        self._upload_library = [
            "春日旅行 Vlog.mp4",
            "产品测评 01.mov",
            "新品拆箱实拍.mp4",
            "达人合作短片.mp4",
            "居家收纳教程.mov",
            "节日促销预告.mp4",
        ]
        self._upload_index = 0
        self._next_post_number = 3308
        self._view_mode = "month"

        _call(self, "setObjectName", "scheduledPublishPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._selected_date_badge = StatusBadge("当前日期 --", tone="brand", parent=self)
        self._queue_badge = StatusBadge("即将发布 0", tone="info", parent=self)
        self._view_badge = StatusBadge("月视图", tone="neutral", parent=self)
        self._schedule_search = SearchBar("搜索标题、素材、标签或分区", self)
        _call(self._schedule_search, "setMinimumWidth", SEARCH_MIN_WIDTH)
        self._new_schedule_button = PrimaryButton("新建排期", self, icon_text="＋")

        page_container = PageContainer(
            title=self.display_name,
            description="通过月历排期、任务表单和发布队列统一管理 TikTok 内容自动化发布。",
            actions=(self._schedule_search, self._selected_date_badge, self._queue_badge, self._view_badge, self._new_schedule_button),
            parent=self,
        )
        self.layout.addWidget(page_container)

        workspace = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.66, 0.34),
            minimum_sizes=(SPACING_2XL * 20, SPACING_2XL * 12),
            parent=page_container,
        )
        workspace.set_first_widget(self._build_calendar_column())
        workspace.set_second_widget(self._build_side_column())
        page_container.add_widget(workspace)
        page_container.add_widget(self._build_schedule_table_section())

        _connect(self._calendar.date_selected, self._handle_calendar_date_selected)
        _connect(getattr(self._month_button, "clicked", None), lambda: self._set_view_mode("month"))
        _connect(getattr(self._week_button, "clicked", None), lambda: self._set_view_mode("week"))
        _connect(getattr(self._pick_file_button, "clicked", None), self._handle_pick_asset)
        _connect(getattr(self._save_draft_button, "clicked", None), self._handle_save_draft)
        _connect(getattr(self._confirm_publish_button, "clicked", None), self._handle_confirm_publish)
        _connect(self._schedule_table.row_selected, self._handle_table_row_selected)
        _connect(self._schedule_table.row_double_clicked, self._handle_table_row_selected)
        _connect(self._schedule_search.search_changed, self._refresh_views)
        _connect(getattr(self._new_schedule_button, "clicked", None), self._prepare_new_schedule)

        if self._posts:
            self._load_post_into_form(self._posts[0], sync_calendar=False)
            self._calendar.select_date(_qdate_from_iso(self._posts[0].publish_date))
        else:
            self._sync_form_date_with_calendar(self._calendar.selected_date())
        self._refresh_views()

    def _prepare_new_schedule(self) -> None:
        """切换到新建排期状态。"""

        self._selected_post_id = None
        self._selected_asset_name = ""
        self._title_input.setText("")
        self._description_input.setPlainText("")
        self._sync_form_date_with_calendar(self._calendar.selected_date())
        self._time_input.setText("18:00")
        _call(self._category_combo.combo_box, "setCurrentText", "生活娱乐")
        _call(self._reminder_combo.combo_box, "setCurrentText", "发布前 30 分钟")
        self._tag_input.set_tags(())
        self._upload_title.setText("尚未选择素材")
        self._upload_meta.setText("点击下方按钮模拟上传排期素材。")
        self._upload_badge.setText("待上传")
        self._upload_badge.set_tone("warning")
        self._form_state_badge.setText("新建中")
        self._form_state_badge.set_tone("brand")
        _call(self._form_feedback, "setText", "请先选择素材，再补充标题、时间和标签。")
        self._refresh_views()

    def _build_calendar_column(self) -> QWidget:
        """构建左侧日历与日程概览列。"""

        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)

        section = ContentSection("排期日历", icon="◷", parent=column)

        shell = QWidget(section)
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(SPACING_XL)

        summary = QWidget(shell)
        _call(summary, "setObjectName", "scheduledOverviewStrip")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        summary_layout.setSpacing(SPACING_MD)

        copy_wrap = QWidget(summary)
        copy_layout = QVBoxLayout(copy_wrap)
        copy_layout.setContentsMargins(0, 0, 0, 0)
        copy_layout.setSpacing(SPACING_XS)
        title = QLabel("定时发布", copy_wrap)
        _call(title, "setObjectName", "scheduledSectionTitle")
        subtitle = QLabel("在这里管理您的内容排期和自动化发布流。", copy_wrap)
        _call(subtitle, "setObjectName", "scheduledMutedText")
        _call(subtitle, "setWordWrap", True)
        copy_layout.addWidget(title)
        copy_layout.addWidget(subtitle)

        toggle_wrap = QWidget(summary)
        _call(toggle_wrap, "setObjectName", "scheduledToggleGroup")
        toggle_layout = QHBoxLayout(toggle_wrap)
        toggle_layout.setContentsMargins(SPACING_XS, SPACING_XS, SPACING_XS, SPACING_XS)
        toggle_layout.setSpacing(SPACING_XS)
        self._month_button = QPushButton("月视图", toggle_wrap)
        self._week_button = QPushButton("周视图", toggle_wrap)
        _call(self._month_button, "setObjectName", "scheduledToggleButton")
        _call(self._week_button, "setObjectName", "scheduledToggleButton")
        toggle_layout.addWidget(self._month_button)
        toggle_layout.addWidget(self._week_button)

        summary_layout.addWidget(copy_wrap, 1)
        summary_layout.addWidget(toggle_wrap)

        status_row = QWidget(shell)
        _call(status_row, "setObjectName", "scheduledStatusRow")
        status_layout = QHBoxLayout(status_row)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(SPACING_MD)
        self._day_count_badge = StatusBadge("当天排期 0", tone="brand", parent=status_row)
        self._draft_badge = StatusBadge("草稿 0", tone="neutral", parent=status_row)
        self._status_hint = QLabel("点击日历日期可同步右侧发布日期与下方队列。", status_row)
        _call(self._status_hint, "setObjectName", "scheduledMutedText")
        _call(self._status_hint, "setWordWrap", True)
        status_layout.addWidget(self._day_count_badge)
        status_layout.addWidget(self._draft_badge)
        status_layout.addWidget(self._status_hint, 1)

        self._calendar = CalendarWidget(shell)

        agenda_section = QFrame(shell)
        _call(agenda_section, "setObjectName", "scheduledAgendaSection")
        agenda_layout = QVBoxLayout(agenda_section)
        agenda_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        agenda_layout.setSpacing(SPACING_LG)

        agenda_header = QHBoxLayout()
        agenda_header.setContentsMargins(0, 0, 0, 0)
        agenda_header.setSpacing(SPACING_MD)
        self._agenda_title = QLabel("当天排期", agenda_section)
        _call(self._agenda_title, "setObjectName", "scheduledSubsectionTitle")
        self._agenda_meta_badge = StatusBadge("0 个任务", tone="info", parent=agenda_section)
        agenda_header.addWidget(self._agenda_title)
        agenda_header.addStretch(1)
        agenda_header.addWidget(self._agenda_meta_badge)

        self._agenda_host = QWidget(agenda_section)
        self._agenda_layout = QVBoxLayout(self._agenda_host)
        self._agenda_layout.setContentsMargins(0, 0, 0, 0)
        self._agenda_layout.setSpacing(SPACING_MD)

        agenda_layout.addLayout(agenda_header)
        agenda_layout.addWidget(self._agenda_host)

        shell_layout.addWidget(summary)
        shell_layout.addWidget(status_row)
        shell_layout.addWidget(self._calendar)
        shell_layout.addWidget(agenda_section)

        section.add_widget(shell)
        layout.addWidget(section)
        return column

    def _build_side_column(self) -> QWidget:
        """构建右侧表单与统计列。"""

        column = QWidget(self)
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_2XL)
        layout.addWidget(self._build_form_section())
        layout.addWidget(self._build_stats_card())
        layout.addStretch(1)
        return column

    def _build_form_section(self) -> ContentSection:
        """构建右侧定时发布表单。"""

        section = ContentSection("新建定时任务", icon="＋", parent=self)

        shell = QWidget(section)
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(SPACING_XL)

        self._upload_title = QLabel("尚未选择素材", shell)
        _call(self._upload_title, "setObjectName", "scheduledUploadTitle")
        self._upload_meta = QLabel("点击下方按钮模拟上传排期素材。", shell)
        _call(self._upload_meta, "setObjectName", "scheduledMutedText")
        _call(self._upload_meta, "setWordWrap", True)
        self._upload_badge = StatusBadge("待上传", tone="warning", parent=shell)
        self._pick_file_button = SecondaryButton("点击或拖拽上传", shell, icon_text="☁")

        upload_card = QFrame(shell)
        _call(upload_card, "setObjectName", "scheduledUploadCard")
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(SPACING_2XL, SPACING_2XL, SPACING_2XL, SPACING_2XL)
        upload_layout.setSpacing(SPACING_MD)
        upload_layout.addWidget(self._upload_badge)
        upload_layout.addWidget(self._upload_title)
        upload_layout.addWidget(self._upload_meta)
        upload_layout.addWidget(self._pick_file_button)

        upload_group = FormGroup(
            label="上传视频",
            field_widget=upload_card,
            description="支持 MP4、MOV，模拟上传后会同步更新排期表和月历事件。",
            required=True,
            parent=shell,
        )

        self._title_input = ThemedLineEdit(
            label="视频标题",
            placeholder="输入视频标题",
            helper_text="草稿可留空，确认发布建议填写完整标题。",
            parent=shell,
        )
        self._description_input = ThemedTextEdit(
            label="视频简介",
            placeholder="写点什么来介绍你的视频吧…",
            parent=shell,
        )
        self._date_input = ThemedLineEdit(
            label="发布日期",
            placeholder="YYYY-MM-DD",
            helper_text="默认跟随左侧月历所选日期。",
            parent=shell,
        )
        self._time_input = ThemedLineEdit(
            label="发布时间",
            placeholder="18:00",
            helper_text="使用 24 小时制，例如 19:30。",
            parent=shell,
        )
        self._category_combo = ThemedComboBox(
            label="选择分区",
            items=("生活娱乐", "科技数码", "知识分享", "美食制作", "居家好物", "节日活动"),
            parent=shell,
        )
        self._reminder_combo = ThemedComboBox(
            label="提醒节点",
            items=("发布前 10 分钟", "发布前 30 分钟", "发布前 1 小时", "无需提醒"),
            parent=shell,
        )
        self._tag_input = TagInput(label="发布标签", placeholder="输入标签后按回车", parent=shell)

        schedule_row = QWidget(shell)
        schedule_row_layout = QHBoxLayout(schedule_row)
        schedule_row_layout.setContentsMargins(0, 0, 0, 0)
        schedule_row_layout.setSpacing(SPACING_XL)
        schedule_row_layout.addWidget(self._date_input, 1)
        schedule_row_layout.addWidget(self._time_input, 1)

        options_row = QWidget(shell)
        options_row_layout = QHBoxLayout(options_row)
        options_row_layout.setContentsMargins(0, 0, 0, 0)
        options_row_layout.setSpacing(SPACING_XL)
        options_row_layout.addWidget(self._category_combo, 1)
        options_row_layout.addWidget(self._reminder_combo, 1)

        footer = QWidget(shell)
        _call(footer, "setObjectName", "scheduledFormFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        footer_layout.setSpacing(SPACING_MD)

        feedback_wrap = QWidget(footer)
        feedback_layout = QVBoxLayout(feedback_wrap)
        feedback_layout.setContentsMargins(0, 0, 0, 0)
        feedback_layout.setSpacing(SPACING_XS)
        self._form_state_badge = StatusBadge("编辑中", tone="brand", parent=feedback_wrap)
        self._form_feedback = QLabel("保存草稿或确认发布后，底部排期表与月历事件会即时刷新。", feedback_wrap)
        _call(self._form_feedback, "setObjectName", "scheduledMutedText")
        _call(self._form_feedback, "setWordWrap", True)
        feedback_layout.addWidget(self._form_state_badge)
        feedback_layout.addWidget(self._form_feedback)

        self._save_draft_button = SecondaryButton("保存草稿", footer)
        self._confirm_publish_button = PrimaryButton("确认发布", footer)

        footer_layout.addWidget(feedback_wrap, 1)
        footer_layout.addWidget(self._save_draft_button)
        footer_layout.addWidget(self._confirm_publish_button)

        shell_layout.addWidget(upload_group)
        shell_layout.addWidget(self._title_input)
        shell_layout.addWidget(self._description_input)
        shell_layout.addWidget(schedule_row)
        shell_layout.addWidget(options_row)
        shell_layout.addWidget(self._tag_input)
        shell_layout.addWidget(footer)

        section.add_widget(shell)
        return section

    def _build_stats_card(self) -> QWidget:
        """构建右侧深色统计卡片。"""

        card = QFrame(self)
        _call(card, "setObjectName", "scheduledStatsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_2XL, SPACING_2XL, SPACING_2XL, SPACING_2XL)
        layout.setSpacing(SPACING_MD)

        self._stats_caption = QLabel("本月发布概况", card)
        _call(self._stats_caption, "setObjectName", "scheduledStatsCaption")

        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.setSpacing(SPACING_SM)
        self._stats_value = QLabel("0", card)
        _call(self._stats_value, "setObjectName", "scheduledStatsValue")
        self._stats_unit = QLabel("个已预定视频", card)
        _call(self._stats_unit, "setObjectName", "scheduledStatsUnit")
        value_row.addWidget(self._stats_value)
        value_row.addWidget(self._stats_unit)
        value_row.addStretch(1)

        progress_track = QFrame(card)
        _call(progress_track, "setObjectName", "scheduledProgressTrack")
        _call(progress_track, "setFixedHeight", SPACING_SM)
        _call(progress_track, "setFixedWidth", PROGRESS_TRACK_WIDTH)
        track_layout = QHBoxLayout(progress_track)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(0)
        self._progress_fill = QFrame(progress_track)
        _call(self._progress_fill, "setObjectName", "scheduledProgressFill")
        _call(self._progress_fill, "setFixedHeight", SPACING_SM)
        track_layout.addWidget(self._progress_fill)
        track_layout.addStretch(1)

        self._stats_hint = QLabel("已完成本月计划的 0%", card)
        _call(self._stats_hint, "setObjectName", "scheduledStatsHint")

        layout.addWidget(self._stats_caption)
        layout.addLayout(value_row)
        layout.addWidget(progress_track)
        layout.addWidget(self._stats_hint)
        return card

    def _build_schedule_table_section(self) -> ContentSection:
        """构建底部即将发布表格。"""

        section = ContentSection("即将发布", icon="▦", parent=self)

        summary = QWidget(section)
        _call(summary, "setObjectName", "scheduledOverviewStrip")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        summary_layout.setSpacing(SPACING_MD)
        self._table_summary_badge = StatusBadge("0 条排期", tone="brand", parent=summary)
        self._table_status_badge = StatusBadge("已排期 0", tone="success", parent=summary)
        self._table_hint = QLabel("选中表格行可回填右侧表单并聚焦对应日历日期。", summary)
        _call(self._table_hint, "setObjectName", "scheduledMutedText")
        _call(self._table_hint, "setWordWrap", True)
        summary_layout.addWidget(self._table_summary_badge)
        summary_layout.addWidget(self._table_status_badge)
        summary_layout.addWidget(self._table_hint, 1)

        self._schedule_table = DataTable(
            headers=("任务编号", "视频标题", "发布日期", "发布时间", "分区", "状态", "素材", "标签"),
            rows=(),
            page_size=TABLE_PAGE_SIZE,
            empty_text="暂无即将发布的排期任务。",
            parent=section,
        )
        _call(self._schedule_table.table_view, "setSortingEnabled", False)

        section.add_widget(summary)
        section.add_widget(self._schedule_table)
        return section

    def _handle_calendar_date_selected(self, date_value: QDate) -> None:
        """处理月历选中日期。"""

        self._sync_form_date_with_calendar(date_value)
        self._refresh_views()

    def _handle_pick_asset(self) -> None:
        """模拟选择待发布素材。"""

        self._selected_asset_name = self._upload_library[self._upload_index % len(self._upload_library)]
        self._upload_index += 1
        self._upload_title.setText(self._selected_asset_name)
        self._upload_meta.setText("素材已进入待排期状态，可继续填写标题、文案和发布时间。")
        self._upload_badge.setText("已上传")
        self._upload_badge.set_tone("success")
        self._form_state_badge.setText("素材已就绪")
        self._form_state_badge.set_tone("info")

    def _handle_save_draft(self) -> None:
        """保存草稿。"""

        self._save_form(status="草稿", strict=False)

    def _handle_confirm_publish(self) -> None:
        """确认发布。"""

        self._save_form(status="已排期", strict=True)

    def _handle_table_row_selected(self, row_index: int) -> None:
        """根据表格选择回填表单。"""

        if not (0 <= row_index < len(self._visible_posts)):
            return
        self._load_post_into_form(self._visible_posts[row_index], sync_calendar=True)
        self._refresh_views()

    def _set_view_mode(self, mode: str) -> None:
        """切换视图模式文案。"""

        self._view_mode = "week" if mode == "week" else "month"
        self._view_badge.setText("周视图" if self._view_mode == "week" else "月视图")
        self._view_badge.set_tone("info" if self._view_mode == "week" else "neutral")
        hint_text = "周视图摘要已启用，当前仍保留月历作为主排期面板。" if self._view_mode == "week" else "点击日历日期可同步右侧发布日期与下方队列。"
        _call(self._status_hint, "setText", hint_text)
        self._refresh_toggle_styles()

    def _save_form(self, *, status: str, strict: bool) -> None:
        """保存当前表单。"""

        self._clear_form_errors()
        title = self._title_input.text().strip()
        description = self._description_input.toPlainText().strip()
        publish_date = self._date_input.text().strip()
        publish_time = self._time_input.text().strip()
        parsed_date = self._parse_date(publish_date)
        parsed_time = self._parse_time(publish_time)

        if not title and strict:
            self._title_input.set_error("确认发布前请填写视频标题。")
        if parsed_date is None:
            self._date_input.set_error("发布日期格式应为 YYYY-MM-DD。")
        if parsed_time is None:
            self._time_input.set_error("发布时间格式应为 HH:MM。")
        if strict and not self._selected_asset_name.strip():
            self._upload_badge.setText("素材缺失")
            self._upload_badge.set_tone("warning")

        if strict and (not title or parsed_date is None or parsed_time is None or not self._selected_asset_name.strip()):
            self._form_state_badge.setText("待补全")
            self._form_state_badge.set_tone("warning")
            _call(self._form_feedback, "setText", "请补全标题、发布日期、发布时间和上传素材后再确认发布。")
            return

        resolved_title = title or _compact_title(self._selected_asset_name.replace(".mp4", "").replace(".mov", ""), 10) or "未命名草稿"
        resolved_date = publish_date if parsed_date is not None else _iso_text(self._calendar.selected_date())
        resolved_time = publish_time if parsed_time is not None else "18:00"
        resolved_category = self._category_combo.current_text() or "生活娱乐"
        resolved_reminder = self._reminder_combo.current_text() or "发布前 30 分钟"
        resolved_tags = tuple(self._tag_input.tags())
        resolved_asset = self._selected_asset_name or self._upload_library[0]

        existing = self._post_by_id(self._selected_post_id) if self._selected_post_id else None
        next_post = ScheduledPost(
            post_id=existing.post_id if existing is not None else f"SCH-{self._next_post_number}",
            title=resolved_title,
            description=description,
            publish_date=resolved_date,
            publish_time=resolved_time,
            category=resolved_category,
            status=status,
            tags=resolved_tags,
            asset_name=resolved_asset,
            reminder=resolved_reminder,
        )

        if existing is None:
            self._posts.append(next_post)
            self._next_post_number += 1
        else:
            self._posts = [next_post if item.post_id == next_post.post_id else item for item in self._posts]

        self._load_post_into_form(next_post, sync_calendar=True)
        self._form_state_badge.setText("已保存" if status == "草稿" else "已排期")
        self._form_state_badge.set_tone("neutral" if status == "草稿" else "success")
        action_text = "草稿已保存，可稍后补充发布时间。" if status == "草稿" else f"{next_post.post_id} 已加入发布队列，并同步写入月历。"
        _call(self._form_feedback, "setText", action_text)
        self._refresh_views()

    def _load_post_into_form(self, post: ScheduledPost, *, sync_calendar: bool) -> None:
        """将任务载入右侧表单。"""

        self._selected_post_id = post.post_id
        self._selected_asset_name = post.asset_name
        self._title_input.setText(post.title)
        self._description_input.setPlainText(post.description)
        self._date_input.setText(post.publish_date)
        self._time_input.setText(post.publish_time)
        _call(self._category_combo.combo_box, "setCurrentText", post.category)
        _call(self._reminder_combo.combo_box, "setCurrentText", post.reminder)
        self._tag_input.set_tags(post.tags)
        self._upload_title.setText(post.asset_name)
        self._upload_meta.setText("已载入现有排期，可直接调整文案、时间和标签。")
        self._upload_badge.setText(post.status)
        self._upload_badge.set_tone(self._status_tone(post.status))
        if sync_calendar:
            self._calendar.select_date(_qdate_from_iso(post.publish_date))

    def _refresh_views(self) -> None:
        """刷新全部视图状态。"""

        self._refresh_header_badges()
        self._refresh_toggle_styles()
        self._refresh_calendar_events()
        self._refresh_day_agenda()
        self._refresh_table()
        self._refresh_stats_card()
        self._refresh_draft_badge()

    def _refresh_header_badges(self) -> None:
        """刷新页面顶部状态。"""

        selected_iso = _iso_text(self._calendar.selected_date())
        self._selected_date_badge.setText(f"当前日期 {selected_iso}")
        upcoming_count = sum(1 for item in self._posts if item.status in {"已排期", "待审核"})
        self._queue_badge.setText(f"即将发布 {upcoming_count}")
        self._queue_badge.set_tone("success" if upcoming_count else "neutral")
        query = self._schedule_search.text().strip() if isinstance(self._schedule_search, SearchBar) else ""
        if query:
            _call(self._table_hint, "setText", f"当前按“{query}”过滤排期，选中行可回填右侧表单并同步月历。")
            _call(self._status_hint, "setText", f"当前按“{query}”过滤日程与队列，点击右上角可快速新建排期。")
        else:
            _call(self._table_hint, "setText", "选中表格行可回填右侧表单并聚焦对应日历日期。")
            base_hint = "周视图摘要已启用，当前仍保留月历作为主排期面板。" if self._view_mode == "week" else "点击日历日期可同步右侧发布日期与下方队列。"
            _call(self._status_hint, "setText", base_hint)

    def _refresh_toggle_styles(self) -> None:
        """刷新月/周视图按钮样式。"""

        colors = _palette()
        active_background = colors.surface
        active_color = colors.text
        inactive_background = "transparent"
        inactive_color = colors.text_muted
        active_border = colors.border
        inactive_border = "transparent"

        for button, active in (
            (self._month_button, self._view_mode == "month"),
            (self._week_button, self._view_mode == "week"),
        ):
            _call(
                button,
                "setStyleSheet",
                f"""
                QPushButton#scheduledToggleButton {{
                    background-color: {active_background if active else inactive_background};
                    color: {active_color if active else inactive_color};
                    border: 1px solid {active_border if active else inactive_border};
                    border-radius: {RADIUS_MD}px;
                    min-height: {BUTTON_HEIGHT}px;
                    padding: {SPACING_XS}px {SPACING_XL}px;
                    font-size: {_static_token('font.size.sm')};
                    font-weight: {_static_token('font.weight.bold') if active else _static_token('font.weight.medium')};
                }}
                QPushButton#scheduledToggleButton:hover {{
                    color: {colors.text};
                    border-color: {colors.border};
                }}
                """,
            )

    def _refresh_calendar_events(self) -> None:
        """同步日历事件圆点。"""

        events: dict[str, int] = {}
        for post in self._posts:
            events[post.publish_date] = events.get(post.publish_date, 0) + 1
        self._calendar.set_events(events)

    def _refresh_day_agenda(self) -> None:
        """刷新所选日期的日程列表。"""

        selected_iso = _iso_text(self._calendar.selected_date())
        day_posts = [post for post in self._filtered_posts() if post.publish_date == selected_iso]
        self._day_count_badge.setText(f"当天排期 {len(day_posts)}")
        self._agenda_meta_badge.setText(f"{len(day_posts)} 个任务")
        self._agenda_meta_badge.set_tone("brand" if day_posts else "neutral")
        _call(self._agenda_title, "setText", f"当天排期 · {selected_iso}")

        _clear_layout(self._agenda_layout)
        if not day_posts:
            empty_label = QLabel("当前日期没有排期任务，右侧填写内容后即可创建新任务。", self._agenda_host)
            _call(empty_label, "setObjectName", "scheduledEmptyState")
            _call(empty_label, "setWordWrap", True)
            self._agenda_layout.addWidget(empty_label)
            return

        for post in day_posts:
            item = QFrame(self._agenda_host)
            _call(item, "setObjectName", "scheduledAgendaItem")
            _call(item, "setProperty", "selected", post.post_id == self._selected_post_id)
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(SPACING_LG, SPACING_LG, SPACING_LG, SPACING_LG)
            item_layout.setSpacing(SPACING_MD)

            time_badge = QLabel(post.publish_time, item)
            _call(time_badge, "setObjectName", "scheduledTimePill")

            text_wrap = QWidget(item)
            text_layout = QVBoxLayout(text_wrap)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(SPACING_XS)
            title = QLabel(post.title, text_wrap)
            _call(title, "setObjectName", "scheduledAgendaTitle")
            meta = QLabel(f"{post.category} · {_compact_title(post.asset_name, 20)}", text_wrap)
            _call(meta, "setObjectName", "scheduledMutedText")
            text_layout.addWidget(title)
            text_layout.addWidget(meta)

            status = StatusBadge(post.status, tone=self._status_tone(post.status), parent=item)
            item_layout.addWidget(time_badge)
            item_layout.addWidget(text_wrap, 1)
            item_layout.addWidget(status)
            self._agenda_layout.addWidget(item)

    def _refresh_table(self) -> None:
        """刷新底部排期表。"""

        self._visible_posts = self._filtered_posts()
        rows = [
            (
                post.post_id,
                _compact_title(post.title, 22),
                post.publish_date,
                post.publish_time,
                post.category,
                post.status,
                _compact_title(post.asset_name, 18),
                "、".join(post.tags[:2]) or "--",
            )
            for post in self._visible_posts
        ]
        self._schedule_table.set_rows(rows)
        self._table_summary_badge.setText(f"{len(self._visible_posts)} 条排期")
        scheduled_count = sum(1 for post in self._visible_posts if post.status == "已排期")
        self._table_status_badge.setText(f"已排期 {scheduled_count}")
        self._table_status_badge.set_tone("success" if scheduled_count else "neutral")

    def _filtered_posts(self) -> list[ScheduledPost]:
        """根据顶部搜索过滤排期任务。"""

        query = self._schedule_search.text().strip().lower() if isinstance(self._schedule_search, SearchBar) else ""
        posts = self._sorted_posts()
        if not query:
            return posts
        return [
            post
            for post in posts
            if query
            in " ".join(
                [
                    post.post_id,
                    post.title,
                    post.description,
                    post.publish_date,
                    post.publish_time,
                    post.category,
                    post.status,
                    post.asset_name,
                    " ".join(post.tags),
                ]
            ).lower()
        ]

    def _refresh_stats_card(self) -> None:
        """刷新右侧发布概况卡片。"""

        current_month = self._calendar.selected_date().month()
        current_year = self._calendar.selected_date().year()
        monthly_posts: list[ScheduledPost] = []
        for post in self._posts:
            parsed_date = self._parse_date(post.publish_date)
            if parsed_date is None:
                continue
            if parsed_date.year == current_year and parsed_date.month == current_month and post.status == "已排期":
                monthly_posts.append(post)
        count = len(monthly_posts)
        percentage = min(100, int(round((count / MONTH_PLAN_TARGET) * 100))) if MONTH_PLAN_TARGET else 0
        _call(self._stats_value, "setText", str(count))
        _call(self._stats_hint, "setText", f"已完成本月计划的 {percentage}%")
        fill_width = max(SPACING_2XL, int(PROGRESS_TRACK_WIDTH * (percentage / 100))) if percentage else 0
        _call(self._progress_fill, "setFixedWidth", fill_width)

    def _refresh_draft_badge(self) -> None:
        """刷新草稿状态徽标。"""

        draft_count = sum(1 for post in self._posts if post.status == "草稿")
        self._draft_badge.setText(f"草稿 {draft_count}")
        self._draft_badge.set_tone("warning" if draft_count else "neutral")

    def _sync_form_date_with_calendar(self, date_value: QDate) -> None:
        """将日历选中日期写回表单。"""

        self._date_input.setText(_iso_text(date_value))

    def _clear_form_errors(self) -> None:
        """清除输入错误态。"""

        self._title_input.clear_error()
        self._date_input.clear_error()
        self._time_input.clear_error()

    def _sorted_posts(self) -> list[ScheduledPost]:
        """返回按日期时间排序的任务列表。"""

        return sorted(
            self._posts,
            key=lambda item: f"{item.publish_date} {item.publish_time} {item.post_id}",
        )

    def _post_by_id(self, post_id: str | None) -> ScheduledPost | None:
        """根据任务编号查找任务。"""

        if post_id is None:
            return None
        return next((post for post in self._posts if post.post_id == post_id), None)

    @staticmethod
    def _parse_date(text: str) -> _date | None:
        """解析发布日期。"""

        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _parse_time(text: str) -> str | None:
        """校验发布时间。"""

        try:
            return datetime.strptime(text, "%H:%M").strftime("%H:%M")
        except ValueError:
            return None

    @staticmethod
    def _status_tone(status: str) -> BadgeTone:
        """映射状态到徽标色调。"""

        mapping: dict[str, BadgeTone] = {
            "已排期": "success",
            "草稿": "neutral",
            "待审核": "warning",
            "已发布": "brand",
        }
        return mapping.get(status, "neutral")

    def _apply_page_styles(self) -> None:
        """应用页面级样式。"""

        colors = _palette()
        brand_tint = _rgba(_token("brand.primary"), 0.08)
        brand_border = _rgba(_token("brand.primary"), 0.20)
        inverse_tint = _rgba(_token("text.inverse"), 0.12)
        strong_inverse_text = _rgba(_token("text.inverse"), 0.82)
        self.setStyleSheet(
            f"""
            QWidget#scheduledPublishPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#scheduledOverviewStrip,
            QWidget#scheduledStatusRow,
            QWidget#scheduledFormFooter,
            QFrame#scheduledAgendaSection,
            QFrame#scheduledUploadCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#scheduledToggleGroup {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#scheduledSectionTitle,
            QLabel#scheduledSubsectionTitle,
            QLabel#scheduledUploadTitle {{
                color: {colors.text};
                background: transparent;
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#scheduledMutedText,
            QLabel#scheduledStatsUnit,
            QLabel#scheduledStatsHint {{
                color: {colors.text_muted};
                background: transparent;
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#scheduledStatsHint {{
                color: {strong_inverse_text};
            }}
            QFrame#scheduledAgendaItem {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_MD}px;
            }}
            QFrame#scheduledAgendaItem[selected="true"] {{
                border-color: {_token('brand.primary')};
                background-color: {brand_tint};
            }}
            QLabel#scheduledAgendaTitle {{
                color: {colors.text};
                background: transparent;
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#scheduledTimePill {{
                color: {_token('brand.primary')};
                background-color: {brand_tint};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XS}px {SPACING_MD}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#scheduledEmptyState {{
                background-color: {brand_tint};
                color: {colors.text_muted};
                border: 1px dashed {brand_border};
                border-radius: {RADIUS_MD}px;
                padding: {SPACING_XL}px;
                font-size: {_static_token('font.size.md')};
            }}
            QFrame#scheduledStatsCard {{
                background-color: {colors.text};
                border: 1px solid {brand_border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#scheduledStatsCaption {{
                color: {_rgba(_token('brand.primary'), 0.84)};
                background: transparent;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.medium')};
            }}
            QLabel#scheduledStatsValue {{
                color: {_token('text.inverse')};
                background: transparent;
                font-size: {_static_token('font.size.xxl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#scheduledStatsUnit {{
                color: {_rgba(_token('text.inverse'), 0.70)};
            }}
            QFrame#scheduledProgressTrack {{
                background-color: {inverse_tint};
                border: none;
                border-radius: {SPACING_SM}px;
            }}
            QFrame#scheduledProgressFill {{
                background-color: {_token('brand.primary')};
                border: none;
                border-radius: {SPACING_SM}px;
            }}
            """
        )

    @staticmethod
    def _build_mock_posts() -> list[ScheduledPost]:
        """生成页面初始 mock 数据。"""

        today = _date.today()
        first_day = today.replace(day=1)
        current_month_days = monthrange(first_day.year, first_day.month)[1]

        def month_day(day: int) -> str:
            resolved = min(max(day, 1), current_month_days)
            return first_day.replace(day=resolved).strftime("%Y-%m-%d")

        future_day = (today + timedelta(days=18)).strftime("%Y-%m-%d")
        return [
            ScheduledPost(
                post_id="SCH-3301",
                title="Vlog：春季旅行城市漫游",
                description="记录周末城市漫游路线，强调轻量装备和拍摄节奏。",
                publish_date=month_day(5),
                publish_time="18:00",
                category="生活娱乐",
                status="已排期",
                tags=("Vlog", "旅行", "春日"),
                asset_name="春日旅行 Vlog.mp4",
                reminder="发布前 30 分钟",
            ),
            ScheduledPost(
                post_id="SCH-3302",
                title="产品测评 01：无线吸尘器实测",
                description="突出续航、吸力和收纳细节，适合居家好物账号发布。",
                publish_date=month_day(10),
                publish_time="20:30",
                category="居家好物",
                status="已排期",
                tags=("测评", "好物", "清洁"),
                asset_name="产品测评 01.mov",
                reminder="发布前 1 小时",
            ),
            ScheduledPost(
                post_id="SCH-3303",
                title="新品拆箱：桌面收纳套装",
                description="预留评论区互动问题，导向下一条收纳教程内容。",
                publish_date=month_day(10),
                publish_time="12:00",
                category="知识分享",
                status="草稿",
                tags=("拆箱", "桌面", "收纳"),
                asset_name="新品拆箱实拍.mp4",
                reminder="无需提醒",
            ),
            ScheduledPost(
                post_id="SCH-3304",
                title="达人合作短片：三段式穿搭推荐",
                description="分镜已确认，待补充最终标题和封面文案。",
                publish_date=month_day(14),
                publish_time="19:30",
                category="生活娱乐",
                status="待审核",
                tags=("穿搭", "达人", "联动"),
                asset_name="达人合作短片.mp4",
                reminder="发布前 30 分钟",
            ),
            ScheduledPost(
                post_id="SCH-3305",
                title="居家收纳教程：10 分钟整理玄关",
                description="适合晚间高互动时段，搭配收纳类商品挂车。",
                publish_date=month_day(18),
                publish_time="21:00",
                category="知识分享",
                status="已排期",
                tags=("收纳", "教程", "玄关"),
                asset_name="居家收纳教程.mov",
                reminder="发布前 10 分钟",
            ),
            ScheduledPost(
                post_id="SCH-3306",
                title="节日促销预告：满减活动开场片",
                description="配合活动档期开启，重点突出优惠力度和倒计时。",
                publish_date=month_day(24),
                publish_time="17:30",
                category="节日活动",
                status="已排期",
                tags=("促销", "活动", "预告"),
                asset_name="节日促销预告.mp4",
                reminder="发布前 1 小时",
            ),
            ScheduledPost(
                post_id="SCH-3307",
                title="科技数码周更：新设备上手总结",
                description="跨月预留内容，用于测试未来排期与提醒链路。",
                publish_date=future_day,
                publish_time="11:00",
                category="科技数码",
                status="已排期",
                tags=("数码", "开箱", "周更"),
                asset_name="新设备上手总结.mp4",
                reminder="发布前 30 分钟",
            ),
        ]


__all__ = ["ScheduledPublishPage"]

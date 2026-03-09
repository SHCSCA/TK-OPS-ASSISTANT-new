# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

"""局域网传输页面。"""

from dataclasses import dataclass
from pathlib import Path

from ....core.qt import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ....core.theme.tokens import STATIC_TOKENS
from ....core.types import RouteId
from ...components import (
    ContentSection,
    DeviceCard,
    DragDropZone,
    PageContainer,
    PrimaryButton,
    SearchBar,
    SecondaryButton,
    SplitPanel,
    StatusBadge,
    TaskProgressBar,
    ThemedScrollArea,
)
from ...components.tags import BadgeTone
from ...components.inputs import (
    RADIUS_LG,
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
from ..base_page import BasePage


def _px_token(name: str, fallback: int) -> int:
    """将像素 token 解析为整数。"""

    raw_value = STATIC_TOKENS.get(name, f"{fallback}px")
    digits = "".join(character for character in str(raw_value) if character.isdigit())
    return int(digits) if digits else fallback


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba 字符串。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _format_bytes(size_bytes: int | None) -> str:
    """格式化文件大小。"""

    if size_bytes is None:
        return "未知大小"
    units = ("B", "KB", "MB", "GB")
    value = float(max(size_bytes, 0))
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.1f} {units[unit_index]}"


def _clear_layout(layout: object) -> None:
    """兼容真实 Qt 与占位布局的清空逻辑。"""

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
        return

    items = getattr(layout, "_items", None)
    if isinstance(items, list):
        items.clear()


SPACING_3XL = _px_token("spacing.3xl", 32)
SPACING_4XL = _px_token("spacing.4xl", 48)
RADIUS_XL = _px_token("radius.xl", 16)
SIDEBAR_MIN_WIDTH = _px_token("layout.sidebar_width.canonical", 280)
MAIN_MIN_WIDTH = SPACING_4XL * 10
DROP_ZONE_MIN_HEIGHT = SPACING_4XL * 6
PROGRESS_STEP = SPACING_2XL + SPACING_MD


@dataclass
class DeviceSnapshot:
    """设备展示数据。"""

    device_id: str
    name: str
    ip: str
    status: str
    progress: int
    device_type: str
    note: str
    speed_text: str


@dataclass
class TransferRecord:
    """传输记录数据。"""

    record_id: str
    file_name: str
    peer_name: str
    size_label: str
    direction: str
    status: str
    progress: int
    speed_text: str
    caption: str


class LANTransferPage(BasePage):
    """系统模块下的局域网传输页。"""

    default_route_id: RouteId = RouteId("lan_transfer")
    default_display_name: str = "局域网传输"
    default_icon_name: str = "leak_add"

    def setup_ui(self) -> None:
        """构建局域网传输页面。"""

        self._network_name = "TP-Link_Office_5G"
        self._local_ip = "192.168.1.104"
        self._service_status = "服务运行正常"
        self._activity_text = "当前连接稳定，支持跨端即时发现与断点续传。"
        self._device_query = ""
        self._staged_files: list[str] = []
        self._devices = self._build_demo_devices()
        self._selected_device_id = self._devices[0].device_id if self._devices else ""
        self._records = self._build_demo_records()
        self._tile_refs: dict[str, tuple[StatusBadge, QLabel, QLabel]] = {}

        _call(self, "setObjectName", "lanTransferPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._page_container = PageContainer(
            title=self.display_name,
            description="同一 Wi‑Fi 下快速发送图片、视频、文档与文件夹，实时查看设备发现、传输进度与连接状态。",
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._network_badge = StatusBadge(f"已连接 · {self._network_name}", tone="brand")
        self._local_badge = StatusBadge(f"本机 · {self._local_ip}", tone="info")
        self._service_badge = StatusBadge(self._service_status, tone="success")
        self._page_container.add_action(self._network_badge)
        self._page_container.add_action(self._local_badge)
        self._page_container.add_action(self._service_badge)

        self._main_split = SplitPanel(
            orientation="horizontal",
            split_ratio=(0.31, 0.69),
            minimum_sizes=(SIDEBAR_MIN_WIDTH, MAIN_MIN_WIDTH),
            parent=self._page_container,
        )
        self._main_split.set_first_widget(self._build_device_sidebar())
        self._main_split.set_second_widget(self._build_main_content())
        self._page_container.add_widget(self._main_split)
        self._page_container.add_widget(self._build_connection_section())

        self._render_devices()
        self._render_records()
        self._refresh_selected_device_summary()
        self._refresh_staged_summary()
        self._refresh_connection_tiles()

    def _build_device_sidebar(self) -> QWidget:
        section = ContentSection("在线设备", icon="◎", parent=self)

        header = QWidget(section)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)
        self._device_count_badge = StatusBadge("在线设备 (0)", tone="brand")
        self._refresh_devices_button = SecondaryButton("刷新列表", header, icon_text="↻")
        header_layout.addWidget(self._device_count_badge)
        header_layout.addStretch(1)
        header_layout.addWidget(self._refresh_devices_button)

        self._device_search = SearchBar("搜索设备名称或 IP")
        self._device_scroll = ThemedScrollArea(section)
        self._device_scroll.content_layout.setSpacing(SPACING_LG)

        footer = QFrame(section)
        _call(footer, "setObjectName", "lanTransferHintCard")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        footer_layout.setSpacing(SPACING_MD)
        footer_badge = StatusBadge("同网可见", tone="info")
        footer_copy = QLabel("只有连接到相同 Wi‑Fi 的设备才能互相发现，并建立局域网极速传输通道。", footer)
        _call(footer_copy, "setWordWrap", True)
        self._invite_button = PrimaryButton("邀请新设备", footer, icon_text="＋")
        footer_layout.addWidget(footer_badge)
        footer_layout.addWidget(footer_copy)
        footer_layout.addWidget(self._invite_button)

        section.add_widget(header)
        section.add_widget(self._device_search)
        section.add_widget(self._device_scroll)
        section.add_widget(footer)

        _connect(self._device_search.search_changed, self._handle_device_search)
        _connect(getattr(self._refresh_devices_button, "clicked", None), self._handle_refresh_devices)
        _connect(getattr(self._invite_button, "clicked", None), self._handle_invite_device)
        return section

    def _build_main_content(self) -> QWidget:
        container = QWidget(self)
        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_LG)
        root.addWidget(self._build_transfer_section())
        root.addWidget(self._build_records_section())
        return container

    def _build_transfer_section(self) -> QWidget:
        section = ContentSection("发送文件", icon="⇪", parent=self)

        summary = QWidget(section)
        _call(summary, "setObjectName", "lanTransferTargetPanel")
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(SPACING_XS)
        self._selected_device_title = QLabel("", summary)
        _call(self._selected_device_title, "setObjectName", "lanTransferLead")
        self._selected_device_meta = QLabel("", summary)
        _call(self._selected_device_meta, "setObjectName", "lanTransferMuted")
        _call(self._selected_device_meta, "setWordWrap", True)
        summary_layout.addWidget(self._selected_device_title)
        summary_layout.addWidget(self._selected_device_meta)

        self._drop_zone = DragDropZone()
        _call(self._drop_zone, "setMinimumHeight", DROP_ZONE_MIN_HEIGHT)

        action_row = QWidget(section)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(SPACING_MD)
        self._choose_file_button = PrimaryButton("选择文件", action_row, icon_text="⇪")
        self._choose_folder_button = SecondaryButton("选择文件夹", action_row, icon_text="▣")
        self._start_transfer_button = SecondaryButton("开始发送", action_row, icon_text="➜")
        action_layout.addWidget(self._choose_file_button)
        action_layout.addWidget(self._choose_folder_button)
        action_layout.addWidget(self._start_transfer_button)
        action_layout.addStretch(1)

        feature_row = QWidget(section)
        _call(feature_row, "setObjectName", "lanTransferStatusRow")
        feature_layout = QHBoxLayout(feature_row)
        feature_layout.setContentsMargins(0, 0, 0, 0)
        feature_layout.setSpacing(SPACING_MD)
        feature_layout.addWidget(StatusBadge("端到端加密", tone="brand"))
        feature_layout.addWidget(StatusBadge("极速内网传输", tone="success"))
        feature_layout.addWidget(StatusBadge("单文件最大 2GB", tone="info"))
        feature_layout.addStretch(1)

        staged_card = QFrame(section)
        _call(staged_card, "setObjectName", "lanTransferStageCard")
        staged_layout = QVBoxLayout(staged_card)
        staged_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        staged_layout.setSpacing(SPACING_SM)
        staged_title = QLabel("待发送清单", staged_card)
        _call(staged_title, "setObjectName", "lanTransferSectionTitle")
        self._staged_summary_label = QLabel("", staged_card)
        _call(self._staged_summary_label, "setObjectName", "lanTransferMuted")
        _call(self._staged_summary_label, "setWordWrap", True)
        self._staged_files_label = QLabel("", staged_card)
        _call(self._staged_files_label, "setObjectName", "lanTransferMuted")
        _call(self._staged_files_label, "setWordWrap", True)
        staged_layout.addWidget(staged_title)
        staged_layout.addWidget(self._staged_summary_label)
        staged_layout.addWidget(self._staged_files_label)

        section.add_widget(summary)
        section.add_widget(self._drop_zone)
        section.add_widget(action_row)
        section.add_widget(feature_row)
        section.add_widget(staged_card)

        _connect(self._drop_zone.files_dropped, self._handle_files_dropped)
        _connect(getattr(self._choose_file_button, "clicked", None), self._handle_choose_files)
        _connect(getattr(self._choose_folder_button, "clicked", None), self._handle_choose_folder)
        _connect(getattr(self._start_transfer_button, "clicked", None), self._handle_start_transfer)
        return section

    def _build_records_section(self) -> QWidget:
        section = ContentSection("最近传输", icon="↺", parent=self)

        header = QWidget(section)
        _call(header, "setObjectName", "lanTransferRecordsBar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)
        self._records_badge = StatusBadge("0 条记录", tone="brand")
        self._records_status_label = QLabel("传输队列与最近完成记录会在这里实时更新。", header)
        _call(self._records_status_label, "setObjectName", "lanTransferMuted")
        _call(self._records_status_label, "setWordWrap", True)
        self._advance_button = SecondaryButton("推进进度", header, icon_text="↻")
        header_layout.addWidget(self._records_badge)
        header_layout.addWidget(self._records_status_label, 1)
        header_layout.addWidget(self._advance_button)

        self._records_scroll = ThemedScrollArea(section)
        self._records_scroll.content_layout.setSpacing(SPACING_LG)

        section.add_widget(header)
        section.add_widget(self._records_scroll)

        _connect(getattr(self._advance_button, "clicked", None), self._handle_advance_progress)
        return section

    def _build_connection_section(self) -> QWidget:
        section = ContentSection("连接状态", icon="⌁", parent=self)
        self._connection_summary_label = QLabel("", section)
        _call(self._connection_summary_label, "setObjectName", "lanTransferMuted")
        _call(self._connection_summary_label, "setWordWrap", True)

        tile_row = QWidget(section)
        _call(tile_row, "setObjectName", "lanTransferConnectionPanel")
        tile_layout = QHBoxLayout(tile_row)
        tile_layout.setContentsMargins(0, 0, 0, 0)
        tile_layout.setSpacing(SPACING_LG)
        tile_layout.addWidget(self._create_info_tile("network", "Wi‑Fi", "brand", tile_row), 1)
        tile_layout.addWidget(self._create_info_tile("local", "本机地址", "info", tile_row), 1)
        tile_layout.addWidget(self._create_info_tile("target", "当前目标", "success", tile_row), 1)
        tile_layout.addWidget(self._create_info_tile("service", "服务状态", "warning", tile_row), 1)

        section.add_widget(self._connection_summary_label)
        section.add_widget(tile_row)
        return section

    def _create_info_tile(self, key: str, title: str, tone: BadgeTone, parent: QWidget) -> QWidget:
        tile = QFrame(parent)
        _call(tile, "setObjectName", "lanTransferInfoTile")
        layout = QVBoxLayout(tile)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_SM)

        badge = StatusBadge(title, tone=tone)
        value_label = QLabel("--", tile)
        _call(value_label, "setObjectName", "lanTransferTileValue")
        caption_label = QLabel("--", tile)
        _call(caption_label, "setObjectName", "lanTransferTileCaption")
        _call(caption_label, "setWordWrap", True)
        layout.addWidget(badge)
        layout.addWidget(value_label)
        layout.addWidget(caption_label)

        self._tile_refs[key] = (badge, value_label, caption_label)
        return tile

    def _apply_page_styles(self) -> None:
        colors = _palette()
        primary_soft = _rgba(_token("brand.primary"), 0.08)
        primary_border = _rgba(_token("brand.primary"), 0.18)
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#lanTransferPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#lanTransferPage QLabel {{
                background: transparent;
                font-family: {_static_token('font.family.chinese')};
            }}
            QLabel#lanTransferLead {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#lanTransferMuted,
            QLabel#lanTransferTileCaption {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#lanTransferSectionTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QFrame#lanTransferHintCard,
            QFrame#lanTransferStageCard,
            QFrame#lanTransferInfoTile {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#lanTransferPage QFrame#contentSection,
            QWidget#lanTransferTargetPanel,
            QWidget#lanTransferRecordsBar,
            QWidget#lanTransferConnectionPanel,
            QWidget#lanTransferStatusRow {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#lanTransferTargetPanel {{
                background-color: {primary_soft};
                border-color: {primary_border};
            }}
            QWidget#lanTransferPage QSplitter#splitPanelCore::handle {{
                background-color: {primary_soft};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#lanTransferTileValue {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            """,
        )

    def _handle_device_search(self, text: str) -> None:
        self._device_query = text.strip().lower()
        self._render_devices()

    def _handle_refresh_devices(self) -> None:
        for device in self._devices:
            if device.status == "待机":
                device.status = "在线"
                device.note = "已重新发现 · 9ms 延迟"
                device.speed_text = "峰值 64 MB/s"
            elif device.status == "忙碌":
                device.note = f"同步中 {max(18, device.progress)}% · 当前 {device.speed_text}"
        self._service_status = "设备发现已刷新"
        self._activity_text = "已重新扫描当前局域网，设备可见性与握手状态已同步。"
        self._render_devices()
        self._refresh_connection_tiles()
        self._refresh_header_badges()
        self._render_records()

    def _handle_invite_device(self) -> None:
        self._service_status = "邀请通道已开启"
        self._activity_text = "已生成新的设备加入提示，请在同一 Wi‑Fi 下输入连接码或扫码加入。"
        self._refresh_connection_tiles()
        self._refresh_header_badges()
        self._render_records()

    def _handle_choose_files(self) -> None:
        self._enqueue_demo_records(
            entries=[("达人脚本合集.docx", "1.2 MB"), ("4月投放素材包.zip", "486 MB")],
            source="手动选择",
        )

    def _handle_choose_folder(self) -> None:
        self._enqueue_demo_records(entries=[("春季上新全量文件夹", "1.4 GB")], source="文件夹导入")

    def _handle_start_transfer(self) -> None:
        self._service_status = "传输进行中"
        self._progress_next_record(prefer_selected=True)
        self._refresh_after_transfer_update()

    def _handle_advance_progress(self) -> None:
        self._progress_next_record(prefer_selected=False)
        self._refresh_after_transfer_update()

    def _handle_files_dropped(self, paths: object) -> None:
        if not isinstance(paths, list):
            return

        entries: list[tuple[str, str]] = []
        for raw_path in paths:
            if not isinstance(raw_path, str):
                continue
            file_path = Path(raw_path)
            size_label = self._path_size_label(file_path)
            entries.append((file_path.name or raw_path, size_label))

        if not entries:
            return

        self._enqueue_demo_records(entries=entries, source="拖拽加入")

    def _enqueue_demo_records(self, entries: list[tuple[str, str]], source: str) -> None:
        selected = self._selected_device()
        if selected is None:
            return

        for file_name, size_label in entries:
            self._records.insert(
                0,
                TransferRecord(
                    record_id=f"record_{len(self._records) + 1}",
                    file_name=file_name,
                    peer_name=selected.name,
                    size_label=size_label,
                    direction="发送至",
                    status="queued",
                    progress=12,
                    speed_text=selected.speed_text,
                    caption=f"{source} · 已加入 {selected.name} 的传输队列",
                ),
            )
            self._staged_files.append(file_name)

        self._service_status = "等待发送确认"
        self._activity_text = f"已通过{source}加入 {len(entries)} 个项目，目标设备：{selected.name}。"
        self._refresh_after_transfer_update()

    def _handle_device_action(self, device_id: str, action: str) -> None:
        selected = self._device_by_id(device_id)
        if selected is None:
            return

        self._selected_device_id = device_id
        if action == "connect":
            self._service_status = "直连已建立"
            self._activity_text = f"已切换目标设备为 {selected.name}，当前可用速率 {selected.speed_text}。"
        elif action == "transfer":
            self._service_status = "传输进行中"
            self._activity_text = f"已切换到 {selected.name}，正在推进与该设备相关的传输任务。"
            self._progress_next_record(prefer_selected=True)
        else:
            self._service_status = "连接详情已同步"
            self._activity_text = f"{selected.name} · {selected.ip} · {selected.note} · {selected.speed_text}。"

        self._refresh_after_transfer_update()

    def _progress_next_record(self, prefer_selected: bool) -> None:
        target_record: TransferRecord | None = None
        selected = self._selected_device()

        if prefer_selected and selected is not None:
            for record in self._records:
                if record.peer_name == selected.name and record.status in {"queued", "processing"}:
                    target_record = record
                    break

        if target_record is None:
            for record in self._records:
                if record.status in {"queued", "processing"}:
                    target_record = record
                    break

        if target_record is None:
            self._service_status = "服务运行正常"
            self._activity_text = "当前没有新的进行中任务，局域网传输通道保持待命。"
            return

        next_progress = min(100, target_record.progress + PROGRESS_STEP)
        target_record.progress = next_progress
        target_record.status = "completed" if next_progress >= 100 else "processing"
        target_record.caption = (
            "传输完成 · 已写入目标设备下载目录" if next_progress >= 100 else f"局域网直连中 · 当前速率 {target_record.speed_text}"
        )

        if self._staged_files:
            self._staged_files.pop(0)

        record_device = next((device for device in self._devices if device.name == target_record.peer_name), None)
        if record_device is not None:
            if next_progress >= 100:
                record_device.status = "在线"
                record_device.progress = 0
                record_device.note = "最近一次发送已完成"
            else:
                record_device.status = "忙碌"
                record_device.progress = next_progress
                record_device.note = f"正在传输 {next_progress}% · 当前 {record_device.speed_text}"

        active_count = sum(1 for record in self._records if record.status in {"queued", "processing"})
        self._service_status = "服务运行正常" if active_count == 0 else "传输进行中"
        self._activity_text = (
            f"{target_record.file_name} 已发送完成，最近目标设备：{target_record.peer_name}。"
            if next_progress >= 100
            else f"{target_record.file_name} 正在发送到 {target_record.peer_name}，进度 {next_progress}%。"
        )

    def _refresh_after_transfer_update(self) -> None:
        self._render_devices()
        self._render_records()
        self._refresh_selected_device_summary()
        self._refresh_staged_summary()
        self._refresh_connection_tiles()
        self._refresh_header_badges()

    def _render_devices(self) -> None:
        _clear_layout(self._device_scroll.content_layout)

        visible_devices = self._visible_devices()
        self._device_count_badge.setText(f"在线设备 ({len(visible_devices)})")

        if not visible_devices:
            empty_label = QLabel("没有匹配的设备，试试搜索名称或 IP。", self._device_scroll)
            _call(empty_label, "setObjectName", "lanTransferMuted")
            self._device_scroll.add_widget(empty_label)
            self._device_scroll.content_layout.addStretch(1)
            return

        for device in visible_devices:
            self._device_scroll.add_widget(self._build_device_item(device))

        self._device_scroll.content_layout.addStretch(1)

    def _build_device_item(self, device: DeviceSnapshot) -> QWidget:
        colors = _palette()
        selected = device.device_id == self._selected_device_id
        border_color = _token("brand.primary") if selected else colors.border
        background = _rgba(_token("brand.primary"), 0.08) if selected else colors.surface

        frame = QFrame(self._device_scroll)
        _call(frame, "setObjectName", "lanTransferDeviceItem")
        _call(
            frame,
            "setStyleSheet",
            f"""
            QFrame#lanTransferDeviceItem {{
                background-color: {background};
                border: 1px solid {border_color};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#lanTransferDeviceItem QLabel {{
                background: transparent;
                color: {colors.text};
                font-family: {_static_token('font.family.chinese')};
            }}
            """,
        )

        root = QVBoxLayout(frame)
        root.setContentsMargins(SPACING_XS, SPACING_XS, SPACING_XS, SPACING_XS)
        root.setSpacing(SPACING_SM)

        device_card = DeviceCard(
            name=device.name,
            ip=device.ip,
            status=device.status,
            transfer_progress=device.progress,
        )
        _connect(device_card.action_requested, lambda action, current_id=device.device_id: self._handle_device_action(current_id, action))

        footer = QWidget(frame)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(SPACING_MD, 0, SPACING_MD, SPACING_XS)
        footer_layout.setSpacing(SPACING_SM)
        speed_tone: BadgeTone = "brand" if selected else "neutral"
        type_badge = StatusBadge(device.device_type, tone="info")
        speed_badge = StatusBadge(device.speed_text, tone=speed_tone)
        note_label = QLabel(device.note, footer)
        _call(note_label, "setObjectName", "lanTransferMuted")
        _call(note_label, "setWordWrap", True)
        footer_layout.addWidget(type_badge)
        footer_layout.addWidget(speed_badge)
        footer_layout.addWidget(note_label, 1)
        if selected:
            footer_layout.addWidget(StatusBadge("当前目标", tone="success"))

        root.addWidget(device_card)
        root.addWidget(footer)
        return frame

    def _render_records(self) -> None:
        _clear_layout(self._records_scroll.content_layout)

        active_count = sum(1 for record in self._records if record.status in {"queued", "processing"})
        self._records_badge.setText(f"{len(self._records)} 条记录")
        self._records_status_label.setText(
            "暂无进行中的传输，最近完成记录仍可查看。" if active_count == 0 else f"当前有 {active_count} 项任务正在排队或传输中。"
        )

        if not self._records:
            empty_label = QLabel("暂时没有传输记录。", self._records_scroll)
            _call(empty_label, "setObjectName", "lanTransferMuted")
            self._records_scroll.add_widget(empty_label)
            self._records_scroll.content_layout.addStretch(1)
            return

        for record in self._records[:6]:
            self._records_scroll.add_widget(self._build_record_card(record))

        self._records_scroll.content_layout.addStretch(1)

    def _build_record_card(self, record: TransferRecord) -> QWidget:
        colors = _palette()
        tone_map: dict[str, tuple[str, str, str, BadgeTone]] = {
            "queued": (_token("status.warning"), _rgba(_token("status.warning"), 0.08), "待发送", "warning"),
            "processing": (_token("brand.primary"), _rgba(_token("brand.primary"), 0.08), "传输中", "brand"),
            "completed": (_token("status.success"), _rgba(_token("status.success"), 0.08), "已完成", "success"),
        }
        border_color, background, status_text, status_tone = tone_map.get(
            record.status,
            (colors.border, colors.surface, "待处理", "neutral"),
        )

        card = QFrame(self._records_scroll)
        _call(card, "setObjectName", "lanTransferRecordCard")
        _call(
            card,
            "setStyleSheet",
            f"""
            QFrame#lanTransferRecordCard {{
                background-color: {background};
                border: 1px solid {border_color};
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )

        root = QHBoxLayout(card)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        icon_label = QLabel(self._record_icon_text(record.file_name), card)
        _call(icon_label, "setObjectName", "lanTransferRecordIcon")
        _call(icon_label, "setStyleSheet", self._record_icon_style(record.status))
        _call(icon_label, "setFixedSize", SPACING_4XL + SPACING_MD, SPACING_4XL + SPACING_MD)

        body = QWidget(card)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(SPACING_SM)

        title_row = QWidget(body)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)
        title_label = QLabel(record.file_name, title_row)
        _call(title_label, "setStyleSheet", f"color: {colors.text}; font-size: {_static_token('font.size.md')}; font-weight: {_static_token('font.weight.bold')};")
        _call(title_label, "setWordWrap", True)
        status_badge = StatusBadge(status_text, tone=status_tone)
        title_layout.addWidget(title_label, 1)
        title_layout.addWidget(status_badge)

        meta_label = QLabel(f"{record.direction} {record.peer_name} · {record.size_label}", body)
        _call(meta_label, "setObjectName", "lanTransferMuted")
        progress_bar = TaskProgressBar(record.progress)
        speed_label = QLabel(f"实时速率：{record.speed_text}", body)
        _call(speed_label, "setObjectName", "lanTransferMuted")
        caption_label = QLabel(record.caption, body)
        _call(caption_label, "setObjectName", "lanTransferMuted")
        _call(caption_label, "setWordWrap", True)

        body_layout.addWidget(title_row)
        body_layout.addWidget(meta_label)
        body_layout.addWidget(progress_bar)
        body_layout.addWidget(speed_label)
        body_layout.addWidget(caption_label)

        root.addWidget(icon_label)
        root.addWidget(body, 1)
        return card

    def _refresh_selected_device_summary(self) -> None:
        selected = self._selected_device()
        if selected is None:
            self._selected_device_title.setText("请选择目标设备")
            self._selected_device_meta.setText("从左侧在线设备列表选择接收端，再拖拽文件或点击按钮加入传输队列。")
            return

        self._selected_device_title.setText(f"发送到 {selected.name}")
        self._selected_device_meta.setText(f"{selected.ip} · {selected.note} · {selected.speed_text}")

    def _refresh_staged_summary(self) -> None:
        if not self._staged_files:
            self._staged_summary_label.setText("尚未选择文件，点击按钮或直接拖拽即可加入待发送队列。")
            self._staged_files_label.setText("")
            return

        self._staged_summary_label.setText(f"当前已暂存 {len(self._staged_files)} 个待发送项目，可继续点击“开始发送”推进局域网传输。")
        self._staged_files_label.setText("\n".join(f"• {file_name}" for file_name in self._staged_files[-4:]))

    def _refresh_connection_tiles(self) -> None:
        selected = self._selected_device()
        target_value = selected.name if selected is not None else "未选择设备"
        target_caption = f"{selected.ip} · {selected.speed_text}" if selected is not None else "等待选择目标设备"

        self._update_tile("network", "Wi‑Fi", self._network_name, "当前连接的局域网")
        self._update_tile("local", "本机地址", self._local_ip, "我的设备地址")
        self._update_tile("target", "当前目标", target_value, target_caption)
        self._update_tile("service", "服务状态", self._service_status, self._activity_text)
        self._connection_summary_label.setText(
            f"已连接 {self._network_name} · 本机 {self._local_ip} · 当前目标 {target_value} · {self._service_status}。"
        )

    def _update_tile(self, key: str, title: str, value: str, caption: str) -> None:
        refs = self._tile_refs.get(key)
        if refs is None:
            return
        badge, value_label, caption_label = refs
        badge.setText(title)
        value_label.setText(value)
        caption_label.setText(caption)

    def _refresh_header_badges(self) -> None:
        self._network_badge.setText(f"已连接 · {self._network_name}")
        self._local_badge.setText(f"本机 · {self._local_ip}")
        self._service_badge.setText(self._service_status)
        if self._service_status in {"服务运行正常", "直连已建立"}:
            self._service_badge.set_tone("success")
        elif self._service_status in {"传输进行中", "等待发送确认", "设备发现已刷新"}:
            self._service_badge.set_tone("warning")
        else:
            self._service_badge.set_tone("info")

    def _visible_devices(self) -> list[DeviceSnapshot]:
        if not self._device_query:
            return list(self._devices)
        return [
            device
            for device in self._devices
            if self._device_query in device.name.lower() or self._device_query in device.ip.lower() or self._device_query in device.device_type.lower()
        ]

    def _selected_device(self) -> DeviceSnapshot | None:
        return self._device_by_id(self._selected_device_id)

    def _device_by_id(self, device_id: str) -> DeviceSnapshot | None:
        for device in self._devices:
            if device.device_id == device_id:
                return device
        return None

    def _record_icon_text(self, file_name: str) -> str:
        suffix = Path(file_name).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            return "图"
        if suffix in {".mp4", ".mov", ".avi"}:
            return "影"
        if suffix in {".zip", ".rar", ".7z"}:
            return "包"
        if suffix in {".doc", ".docx", ".txt"}:
            return "文"
        return "档"

    def _record_icon_style(self, status: str) -> str:
        colors = _palette()
        background = {
            "queued": _rgba(_token("status.warning"), 0.18),
            "processing": _rgba(_token("brand.primary"), 0.18),
            "completed": _rgba(_token("status.success"), 0.18),
        }.get(status, colors.surface)
        color = {
            "queued": _token("status.warning"),
            "processing": _token("brand.primary"),
            "completed": _token("status.success"),
        }.get(status, colors.text)
        return (
            f"background-color: {background};"
            f"color: {color};"
            f"border: 1px solid {color};"
            f"border-radius: {RADIUS_XL}px;"
            f"font-size: {_static_token('font.size.lg')};"
            f"font-weight: {_static_token('font.weight.bold')};"
        )

    @staticmethod
    def _path_size_label(path: Path) -> str:
        try:
            return _format_bytes(path.stat().st_size)
        except OSError:
            return "未知大小"

    @staticmethod
    def _build_demo_devices() -> list[DeviceSnapshot]:
        return [
            DeviceSnapshot(
                device_id="iphone_15_pro",
                name="拍摄用 iPhone 15 Pro",
                ip="192.168.1.121",
                status="在线",
                progress=8,
                device_type="手机",
                note="就绪 · 5ms 延迟",
                speed_text="峰值 92 MB/s",
            ),
            DeviceSnapshot(
                device_id="work_station_01",
                name="运营总控台 Work-Station-01",
                ip="192.168.1.088",
                status="忙碌",
                progress=46,
                device_type="工作站",
                note="正在同步 46% · 千兆网卡",
                speed_text="当前 86 MB/s",
            ),
            DeviceSnapshot(
                device_id="ipad_air",
                name="仓播 iPad Air",
                ip="192.168.1.146",
                status="待机",
                progress=0,
                device_type="平板",
                note="最后在线 2 分钟前",
                speed_text="空闲待命",
            ),
            DeviceSnapshot(
                device_id="macbook_pro_14",
                name="摄影棚 MacBook Pro 14",
                ip="192.168.1.109",
                status="在线",
                progress=0,
                device_type="笔记本",
                note="接收就绪 · Thunderbolt 网桥",
                speed_text="峰值 118 MB/s",
            ),
        ]

    @staticmethod
    def _build_demo_records() -> list[TransferRecord]:
        return [
            TransferRecord(
                record_id="record_001",
                file_name="新品脚本合集.zip",
                peer_name="运营总控台 Work-Station-01",
                size_label="348 MB",
                direction="发送至",
                status="processing",
                progress=58,
                speed_text="86 MB/s",
                caption="局域网直连中 · 预计 16 秒后完成",
            ),
            TransferRecord(
                record_id="record_002",
                file_name="2024_Q3_报告.pdf",
                peer_name="拍摄用 iPhone 15 Pro",
                size_label="4.2 MB",
                direction="发送至",
                status="completed",
                progress=100,
                speed_text="18 MB/s",
                caption="发送完成 · 可在移动端立即预览",
            ),
            TransferRecord(
                record_id="record_003",
                file_name="IMG_8842.JPG",
                peer_name="摄影棚 MacBook Pro 14",
                size_label="12.5 MB",
                direction="来自",
                status="completed",
                progress=100,
                speed_text="42 MB/s",
                caption="接收完成 · 已写入下载目录",
            ),
        ]


__all__ = ["LANTransferPage"]

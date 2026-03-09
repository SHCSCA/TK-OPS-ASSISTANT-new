# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportGeneralTypeIssues=false, reportCallIssue=false

from __future__ import annotations

"""网络诊断页面。"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from ....core.types import RouteId
from ...components import ContentSection, IconButton, KPICard, LogViewer, PageContainer, PrimaryButton, SecondaryButton, StatusBadge
from ...components.inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    RADIUS_MD,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    SPACING_XS,
    QLabel,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    Signal,
    _call,
    _connect,
    _palette,
    _static_token,
    _token,
)
from ...components.tags import BadgeTone
from ..base_page import BasePage

try:
    from PySide6.QtWidgets import QFileDialog
except ImportError:  # pragma: no cover - fallback for non-Qt environments
    QFileDialog = None


DiagnosticStatus = Literal["pass", "warning", "fail"]

STATUS_COPY: dict[DiagnosticStatus, tuple[str, BadgeTone]] = {
    "pass": ("通过", "success"),
    "warning": ("告警", "warning"),
    "fail": ("失败", "error"),
}


def _rgba(hex_color: str, alpha: float) -> str:
    """将十六进制颜色转换为 rgba。"""

    color = hex_color.strip().lstrip("#")
    if len(color) != 6:
        return hex_color
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def _now_text() -> str:
    """返回当前时间文本。"""

    return datetime.now().strftime("%H:%M:%S")


@dataclass(frozen=True)
class DiagnosticScenario:
    """单次诊断模拟结果。"""

    status: DiagnosticStatus
    status_text: str
    last_run_text: str
    latency_ms: int
    packet_loss_rate: float
    bandwidth_mbps: int
    detail_title: str
    detail_body: str
    recommendations: tuple[str, ...]
    log_level: str
    output_lines: tuple[str, ...]


@dataclass
class DiagnosticTestState:
    """诊断测试当前状态。"""

    test_id: str
    name: str
    description: str
    accent: str
    scenarios: tuple[DiagnosticScenario, ...]
    current_index: int = 0
    run_count: int = 0

    @property
    def current(self) -> DiagnosticScenario:
        return self.scenarios[self.current_index]


class DiagnosticTestRow(QFrame):
    """诊断测试列表行。"""

    run_requested = Signal(str)

    def __init__(self, state: DiagnosticTestState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = state
        self._status_badge = StatusBadge(parent=self)
        self._last_run_label = QLabel("", self)
        self._run_button = QPushButton("运行测试", self)
        self._title_label = QLabel(state.name, self)
        self._description_label = QLabel(state.description, self)

        _call(self, "setObjectName", "networkDiagnosticsTestRow")
        _call(self._title_label, "setObjectName", "networkDiagnosticsTestTitle")
        _call(self._description_label, "setObjectName", "networkDiagnosticsTestDescription")
        _call(self._last_run_label, "setObjectName", "networkDiagnosticsTestMeta")
        _call(self._run_button, "setObjectName", "networkDiagnosticsTestAction")
        _call(self._description_label, "setWordWrap", True)

        self._build_ui()
        self._apply_styles()
        self.set_state(state)
        _connect(getattr(self._run_button, "clicked", None), lambda: self.run_requested.emit(self._state.test_id))

    def set_state(self, state: DiagnosticTestState) -> None:
        """刷新行展示。"""

        self._state = state
        current = state.current
        status_text, tone = STATUS_COPY[current.status]
        self._status_badge.setText(status_text)
        self._status_badge.set_tone(tone)
        _call(self._last_run_label, "setText", current.last_run_text)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        root.setSpacing(SPACING_LG)

        title_column = QVBoxLayout()
        title_column.setContentsMargins(0, 0, 0, 0)
        title_column.setSpacing(SPACING_XS)
        title_column.addWidget(self._title_label)
        title_column.addWidget(self._description_label)

        status_column = QVBoxLayout()
        status_column.setContentsMargins(0, 0, 0, 0)
        status_column.setSpacing(SPACING_XS)
        status_column.addWidget(self._status_badge)
        status_column.addStretch(1)

        time_column = QVBoxLayout()
        time_column.setContentsMargins(0, 0, 0, 0)
        time_column.setSpacing(SPACING_XS)
        time_column.addWidget(self._last_run_label)
        time_column.addStretch(1)

        action_column = QVBoxLayout()
        action_column.setContentsMargins(0, 0, 0, 0)
        action_column.setSpacing(0)
        action_column.addWidget(self._run_button)
        action_column.addStretch(1)

        root.addLayout(title_column, 6)
        root.addLayout(status_column, 2)
        root.addLayout(time_column, 2)
        root.addLayout(action_column, 1)

    def _apply_styles(self) -> None:
        colors = _palette()
        brand = _token("brand.primary")
        _call(
            self,
            "setStyleSheet",
            f"""
            QFrame#networkDiagnosticsTestRow {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
                border-radius: 0;
            }}
            QFrame#networkDiagnosticsTestRow QLabel {{
                background: transparent;
                font-family: {_static_token('font.family.chinese')};
            }}
            QLabel#networkDiagnosticsTestTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.lg')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#networkDiagnosticsTestDescription,
            QLabel#networkDiagnosticsTestMeta {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QPushButton#networkDiagnosticsTestAction {{
                background-color: transparent;
                color: {brand};
                border: 1px solid transparent;
                border-radius: {RADIUS_MD}px;
                min-height: {BUTTON_HEIGHT}px;
                padding: {SPACING_SM}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QPushButton#networkDiagnosticsTestAction:hover {{
                background-color: {_rgba(brand, 0.10)};
                border-color: {_rgba(brand, 0.18)};
            }}
            """,
        )


class NetworkDiagnosticsPage(BasePage):
    """系统网络诊断页。"""

    default_route_id: RouteId = RouteId("network_diagnostics")
    default_display_name: str = "网络诊断"
    default_icon_name: str = "network_check"

    def setup_ui(self) -> None:
        """构建网络诊断页面。"""

        self._tests = self._build_test_states()
        self._test_rows: dict[str, DiagnosticTestRow] = {}
        self._kpi_cards: dict[str, KPICard] = {}
        self._export_buffer: list[str] = []
        self._active_test_id = "ssl_handshake"

        _call(self, "setObjectName", "networkDiagnosticsPage")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._apply_page_styles()

        self._run_all_button = PrimaryButton("全部测试", self, icon_text="▶")
        self._export_button = SecondaryButton("导出日志", self, icon_text="⇩")
        self._refresh_button = IconButton("↻", "刷新诊断概览", self)

        self._page_container = PageContainer(
            title=self.display_name,
            description="检查网络状态、链路质量与关键服务可用性，快速定位 TikTok Shop 运营链路中的连接异常。",
            actions=(self._run_all_button, self._export_button, self._refresh_button),
            parent=self,
        )
        self.layout.addWidget(self._page_container)

        self._page_container.add_widget(self._build_kpi_strip())
        self._page_container.add_widget(self._build_tests_section())
        self._page_container.add_widget(self._build_analysis_section())

        _connect(getattr(self._run_all_button, "clicked", None), self._run_all_tests)
        _connect(getattr(self._export_button, "clicked", None), self._export_logs)
        _connect(getattr(self._refresh_button, "clicked", None), self._refresh_dashboard)

        self._refresh_test_rows()
        self._refresh_metrics()
        self._refresh_analysis_panel()
        self._seed_initial_logs()

    def _build_kpi_strip(self) -> QWidget:
        container = QWidget(self)
        _call(container, "setObjectName", "networkDiagnosticsKpiStrip")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_LG)

        self._kpi_cards["network"] = KPICard(title="网络状态", value="在线", trend="flat", percentage="稳定", caption="未发现阻断", parent=container)
        self._kpi_cards["latency"] = KPICard(title="延迟", value="24 ms", trend="down", percentage="-8 ms", caption="低于基线", parent=container)
        self._kpi_cards["packet_loss"] = KPICard(title="丢包率", value="0.3%", trend="down", percentage="-0.2%", caption="STUN/TURN 稳定", parent=container)
        self._kpi_cards["bandwidth"] = KPICard(title="带宽", value="820 Mbps", trend="up", percentage="+6%", caption="链路充裕", parent=container)

        self._kpi_cards["network"].set_sparkline_data([96, 97, 96, 98, 98, 99, 99])
        self._kpi_cards["latency"].set_sparkline_data([48, 41, 36, 33, 30, 27, 24])
        self._kpi_cards["packet_loss"].set_sparkline_data([1.1, 0.9, 0.8, 0.6, 0.5, 0.4, 0.3])
        self._kpi_cards["bandwidth"].set_sparkline_data([650, 690, 720, 760, 790, 810, 820])

        for card in self._kpi_cards.values():
            layout.addWidget(card, 1)

        return container

    def _build_tests_section(self) -> QWidget:
        section = ContentSection("活跃诊断测试", icon="≋", parent=self)

        header_bar = QWidget(section)
        _call(header_bar, "setObjectName", "networkDiagnosticsSectionBar")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACING_MD)

        self._summary_badge = StatusBadge("共 4 项测试", tone="brand", parent=header_bar)
        self._health_badge = StatusBadge("诊断进行中", tone="info", parent=header_bar)
        self._summary_label = QLabel("已载入 DNS、延迟、SSL 与丢包四类模拟诊断。", header_bar)
        _call(self._summary_label, "setObjectName", "networkDiagnosticsSummary")
        _call(self._summary_label, "setWordWrap", True)

        header_layout.addWidget(self._summary_badge)
        header_layout.addWidget(self._health_badge)
        header_layout.addWidget(self._summary_label, 1)

        table_card = QFrame(section)
        _call(table_card, "setObjectName", "networkDiagnosticsTestsCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        table_layout.addWidget(self._build_tests_header(table_card))

        for state in self._tests.values():
            row = DiagnosticTestRow(state, table_card)
            _connect(row.run_requested, self._run_single_test)
            table_layout.addWidget(row)
            self._test_rows[state.test_id] = row

        section.add_widget(header_bar)
        section.add_widget(table_card)
        return section

    def _build_tests_header(self, parent: QWidget) -> QWidget:
        header = QWidget(parent)
        _call(header, "setObjectName", "networkDiagnosticsTableHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(SPACING_XL, SPACING_LG, SPACING_XL, SPACING_LG)
        layout.setSpacing(SPACING_LG)

        labels = (
            ("测试项", 6),
            ("状态", 2),
            ("最近运行", 2),
            ("操作", 1),
        )
        for text, stretch in labels:
            label = QLabel(text, header)
            _call(label, "setObjectName", "networkDiagnosticsHeaderLabel")
            layout.addWidget(label, stretch)
        return header

    def _build_analysis_section(self) -> QWidget:
        section = ContentSection("技术分析日志", icon="⌁", parent=self)

        overview = QFrame(section)
        _call(overview, "setObjectName", "networkDiagnosticsDetailCard")
        overview_layout = QVBoxLayout(overview)
        overview_layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        overview_layout.setSpacing(SPACING_LG)

        title_row = QWidget(overview)
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(SPACING_MD)

        self._detail_title_label = QLabel("", title_row)
        _call(self._detail_title_label, "setObjectName", "networkDiagnosticsDetailTitle")
        self._detail_badge = StatusBadge("", tone="error", parent=title_row)

        title_layout.addWidget(self._detail_title_label, 1)
        title_layout.addWidget(self._detail_badge)

        info_grid = QWidget(overview)
        info_layout = QHBoxLayout(info_grid)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(SPACING_LG)

        self._detail_output_card = self._build_detail_panel("详细输出", overview)
        self._detail_recommendations_card = self._build_detail_panel("建议动作", overview)
        self._detail_output_label = self._detail_output_card[1]
        self._detail_recommendations_label = self._detail_recommendations_card[1]
        self._analysis_card = overview

        info_layout.addWidget(self._detail_output_card[0], 1)
        info_layout.addWidget(self._detail_recommendations_card[0], 1)

        self._log_viewer = LogViewer()

        overview_layout.addWidget(title_row)
        overview_layout.addWidget(info_grid)

        section.add_widget(overview)
        section.add_widget(self._log_viewer)
        return section

    def _build_detail_panel(self, title: str, parent: QWidget) -> tuple[QFrame, QLabel]:
        card = QFrame(parent)
        _call(card, "setObjectName", "networkDiagnosticsInfoPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING_XL, SPACING_XL, SPACING_XL, SPACING_XL)
        layout.setSpacing(SPACING_SM)

        title_label = QLabel(title, card)
        _call(title_label, "setObjectName", "networkDiagnosticsInfoPanelTitle")
        value_label = QLabel("", card)
        _call(value_label, "setObjectName", "networkDiagnosticsInfoPanelBody")
        _call(value_label, "setWordWrap", True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    def _apply_page_styles(self) -> None:
        colors = _palette()
        primary = _token("brand.primary")
        warning = _token("status.warning")
        error = _token("status.error")
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#networkDiagnosticsPage {{
                background-color: {colors.surface_alt};
            }}
            QWidget#networkDiagnosticsPage QLabel {{
                font-family: {_static_token('font.family.chinese')};
                background: transparent;
            }}
            QWidget#networkDiagnosticsPage QWidget#networkDiagnosticsSectionBar {{
                background-color: {colors.surface_alt};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QLabel#networkDiagnosticsSummary {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QWidget#networkDiagnosticsPage QFrame#contentSection {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QFrame#networkDiagnosticsTestsCard,
            QFrame#networkDiagnosticsDetailCard,
            QFrame#networkDiagnosticsInfoPanel {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QWidget#networkDiagnosticsTableHeader {{
                background-color: {colors.surface_alt};
                border-top-left-radius: {RADIUS_LG}px;
                border-top-right-radius: {RADIUS_LG}px;
                border-bottom: 1px solid {colors.border};
            }}
            QLabel#networkDiagnosticsHeaderLabel {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#networkDiagnosticsDetailTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.xl')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#networkDiagnosticsInfoPanelTitle {{
                color: {colors.text};
                font-size: {_static_token('font.size.md')};
                font-weight: {_static_token('font.weight.bold')};
            }}
            QLabel#networkDiagnosticsInfoPanelBody {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
                line-height: 1.6;
            }}
            QPushButton#iconButton:hover {{
                border-color: {primary};
            }}
            QWidget#networkDiagnosticsPage StatusBadge[warning='true'] {{
                border-color: {_rgba(warning, 0.22)};
            }}
            """,
        )

    def _build_test_states(self) -> dict[str, DiagnosticTestState]:
        return {
            "dns_resolution": DiagnosticTestState(
                test_id="dns_resolution",
                name="DNS 解析速度",
                description="验证主域名解析链路与边缘节点传播延迟。",
                accent="◎",
                scenarios=(
                    DiagnosticScenario(
                        status="pass",
                        status_text="通过",
                        last_run_text="2 分钟前",
                        latency_ms=22,
                        packet_loss_rate=0.2,
                        bandwidth_mbps=860,
                        detail_title="DNS 解析速度正常 [LOG_104]",
                        detail_body="主域名在多个边缘解析点返回时间稳定，解析缓存命中率良好，未发现传播异常。",
                        recommendations=("维持当前 DNS 策略。", "继续保留智能解析回源。", "下一轮关注 TTL 变更影响。"),
                        log_level="INFO",
                        output_lines=(
                            "# Executing DNS resolution check...",
                            "> Query tk-ops.shop.edge.internal",
                            "> Avg resolve time: 22ms",
                            "> Edge nodes synced: 16/16",
                            "> Result: PASS",
                        ),
                    ),
                    DiagnosticScenario(
                        status="warning",
                        status_text="告警",
                        last_run_text="刚刚",
                        latency_ms=34,
                        packet_loss_rate=0.3,
                        bandwidth_mbps=820,
                        detail_title="DNS 区域传播稍慢 [LOG_105]",
                        detail_body="海外边缘节点缓存刷新略慢于预期，短时间内可能出现首包等待偏高。",
                        recommendations=("检查最近一次域名配置变更。", "确认海外节点缓存刷新窗口。", "评估是否缩短 TTL。"),
                        log_level="WARNING",
                        output_lines=(
                            "# Executing DNS resolution check...",
                            "> Edge cache refresh observed",
                            "> AP-SG node lagging by 12ms",
                            "> Region sync not fully converged",
                            "> Result: WARNING",
                        ),
                    ),
                ),
            ),
            "latency_check": DiagnosticTestState(
                test_id="latency_check",
                name="全球延迟检查",
                description="测量至 US-East-1 与 EU-West-1 的链路时延。",
                accent="≈",
                scenarios=(
                    DiagnosticScenario(
                        status="warning",
                        status_text="告警",
                        last_run_text="5 分钟前",
                        latency_ms=84,
                        packet_loss_rate=0.4,
                        bandwidth_mbps=760,
                        detail_title="跨区延迟偏高 [LOG_991]",
                        detail_body="欧区路由抖动增大，跨区请求在高峰时段出现可见排队，暂未达到完全故障级别。",
                        recommendations=("切换低峰时段批量同步任务。", "检查代理节点出口拥塞。", "优先将实时操作切到低延迟区域。"),
                        log_level="WARNING",
                        output_lines=(
                            "# Executing latency check...",
                            "> US-East-1: 62ms",
                            "> EU-West-1: 106ms",
                            "> Peak jitter: 18ms",
                            "> Result: WARNING",
                        ),
                    ),
                    DiagnosticScenario(
                        status="pass",
                        status_text="通过",
                        last_run_text="刚刚",
                        latency_ms=29,
                        packet_loss_rate=0.2,
                        bandwidth_mbps=840,
                        detail_title="全球延迟恢复正常 [LOG_992]",
                        detail_body="主要区域链路时延已恢复到正常区间，实时同步与接口调用可继续保持当前策略。",
                        recommendations=("继续观察 15 分钟趋势。", "保留当前路由优先级。", "无需额外降级处理。"),
                        log_level="INFO",
                        output_lines=(
                            "# Executing latency check...",
                            "> US-East-1: 24ms",
                            "> EU-West-1: 34ms",
                            "> Peak jitter: 4ms",
                            "> Result: PASS",
                        ),
                    ),
                ),
            ),
            "ssl_handshake": DiagnosticTestState(
                test_id="ssl_handshake",
                name="SSL 握手完整性",
                description="TLS 1.3 证书链、握手时延与加密套件审计。",
                accent="⛨",
                scenarios=(
                    DiagnosticScenario(
                        status="fail",
                        status_text="失败",
                        last_run_text="12 分钟前",
                        latency_ms=46,
                        packet_loss_rate=0.8,
                        bandwidth_mbps=710,
                        detail_title="SSL 握手完整性失败 [ERR_702]",
                        detail_body="网关证书透明度校验失败，且 5000ms 握手超时，当前代理链路上的 SSL 解密行为正在干扰签名验证。",
                        recommendations=("更新本机 CA 证书捆绑包。", "关闭活跃代理节点的 SSL 解密。", "复核 443 出口防火墙策略。"),
                        log_level="ERROR",
                        output_lines=(
                            "# Executing SSL Handshake Audit...",
                            "> Initiating connection to gateway.tk-ops.internal...",
                            "> Detected Cipher Suite: ECDHE-RSA-AES256-GCM-SHA384",
                            "> ERROR: Certificate Transparency check failed.",
                            "> ERROR: Handshake timed out after 5000ms.",
                            "> Connection terminated.",
                        ),
                    ),
                    DiagnosticScenario(
                        status="warning",
                        status_text="告警",
                        last_run_text="刚刚",
                        latency_ms=33,
                        packet_loss_rate=0.4,
                        bandwidth_mbps=780,
                        detail_title="SSL 握手存在潜在阻塞 [WARN_703]",
                        detail_body="证书链校验已恢复，但代理出口上仍存在短时握手等待，建议继续观察出口设备策略。",
                        recommendations=("继续监控代理出口的握手耗时。", "校验中间证书缓存是否完整。", "保留当前降级预案。"),
                        log_level="WARNING",
                        output_lines=(
                            "# Executing SSL Handshake Audit...",
                            "> Re-checking local trust store...",
                            "> Certificate chain restored",
                            "> Handshake latency: 311ms",
                            "> Result: WARNING",
                        ),
                    ),
                    DiagnosticScenario(
                        status="pass",
                        status_text="通过",
                        last_run_text="刚刚",
                        latency_ms=24,
                        packet_loss_rate=0.2,
                        bandwidth_mbps=850,
                        detail_title="SSL 握手链路已恢复 [OK_704]",
                        detail_body="证书链、加密套件与出站防火墙校验全部通过，HTTPS 调用链路恢复稳定。",
                        recommendations=("恢复正常接口调用节奏。", "保留此次修复记录。", "下次巡检继续验证证书自动更新。"),
                        log_level="INFO",
                        output_lines=(
                            "# Executing SSL Handshake Audit...",
                            "> Certificate chain verified",
                            "> TLS1.3 cipher accepted",
                            "> Handshake latency: 119ms",
                            "> Result: PASS",
                        ),
                    ),
                ),
            ),
            "packet_loss": DiagnosticTestState(
                test_id="packet_loss",
                name="丢包检测 (STUN/TURN)",
                description="模拟 WebRTC 连接稳定性与会话保持能力。",
                accent="◌",
                scenarios=(
                    DiagnosticScenario(
                        status="pass",
                        status_text="通过",
                        last_run_text="刚刚",
                        latency_ms=25,
                        packet_loss_rate=0.1,
                        bandwidth_mbps=830,
                        detail_title="丢包检测稳定 [RTC_201]",
                        detail_body="STUN/TURN 中继链路稳定，未发现明显丢包或回声重协商问题。",
                        recommendations=("保持当前中继路由。", "继续记录高峰期包损样本。", "无需切换备用节点。"),
                        log_level="INFO",
                        output_lines=(
                            "# Executing packet loss diagnostics...",
                            "> TURN relay connected",
                            "> Packet retry rate: 0.1%",
                            "> Session renegotiation: none",
                            "> Result: PASS",
                        ),
                    ),
                    DiagnosticScenario(
                        status="warning",
                        status_text="告警",
                        last_run_text="刚刚",
                        latency_ms=37,
                        packet_loss_rate=1.4,
                        bandwidth_mbps=770,
                        detail_title="丢包率短时升高 [RTC_202]",
                        detail_body="TURN 中继在短时高峰出现可恢复包损，视频预览与素材回传可能偶发卡顿。",
                        recommendations=("切换到备用 TURN 节点。", "避免并发大文件上传。", "关注下一轮 5 分钟样本。"),
                        log_level="WARNING",
                        output_lines=(
                            "# Executing packet loss diagnostics...",
                            "> Relay saturation detected",
                            "> Packet retry rate: 1.4%",
                            "> Jitter buffer expanded",
                            "> Result: WARNING",
                        ),
                    ),
                ),
            ),
        }

    def _refresh_test_rows(self) -> None:
        for test_id, row in self._test_rows.items():
            row.set_state(self._tests[test_id])

        total = len(self._tests)
        warning_count = sum(1 for state in self._tests.values() if state.current.status == "warning")
        fail_count = sum(1 for state in self._tests.values() if state.current.status == "fail")

        self._summary_badge.setText(f"共 {total} 项测试")
        if fail_count > 0:
            self._health_badge.setText(f"{fail_count} 项失败")
            self._health_badge.set_tone("error")
        elif warning_count > 0:
            self._health_badge.setText(f"{warning_count} 项告警")
            self._health_badge.set_tone("warning")
        else:
            self._health_badge.setText("全部通过")
            self._health_badge.set_tone("success")

        _call(
            self._summary_label,
            "setText",
            f"最近聚焦：{self._tests[self._active_test_id].name} · 点击单项“运行测试”可切换下一组模拟结果。",
        )

    def _refresh_metrics(self) -> None:
        latency_values = [state.current.latency_ms for state in self._tests.values()]
        packet_loss_values = [state.current.packet_loss_rate for state in self._tests.values()]
        bandwidth_values = [state.current.bandwidth_mbps for state in self._tests.values()]
        fail_count = sum(1 for state in self._tests.values() if state.current.status == "fail")
        warning_count = sum(1 for state in self._tests.values() if state.current.status == "warning")

        average_latency = round(sum(latency_values) / max(1, len(latency_values)))
        average_packet_loss = sum(packet_loss_values) / max(1, len(packet_loss_values))
        average_bandwidth = round(sum(bandwidth_values) / max(1, len(bandwidth_values)))

        network_card = self._kpi_cards["network"]
        if fail_count > 0:
            network_card.set_value("异常")
            network_card.set_trend("down", f"{fail_count} 项失败")
            _call(network_card._caption_label, "setText", "关键链路需要立即处理")
            network_card.set_sparkline_data([93, 91, 89, 90, 88, 86, 82])
        elif warning_count > 0:
            network_card.set_value("告警")
            network_card.set_trend("flat", f"{warning_count} 项告警")
            _call(network_card._caption_label, "setText", "部分链路存在波动")
            network_card.set_sparkline_data([95, 95, 94, 95, 94, 93, 93])
        else:
            network_card.set_value("在线")
            network_card.set_trend("up", "全部通过")
            _call(network_card._caption_label, "setText", "网络保持健康")
            network_card.set_sparkline_data([96, 97, 97, 98, 98, 99, 99])

        latency_card = self._kpi_cards["latency"]
        latency_card.set_value(f"{average_latency} ms")
        latency_card.set_trend("down" if average_latency <= 35 else "up", f"{'-' if average_latency <= 35 else '+'}{abs(average_latency - 32)} ms")
        _call(latency_card._caption_label, "setText", "平均链路往返时延")
        latency_card.set_sparkline_data([average_latency + 16, average_latency + 11, average_latency + 8, average_latency + 5, average_latency + 2, average_latency + 1, average_latency])

        packet_loss_card = self._kpi_cards["packet_loss"]
        packet_loss_card.set_value(f"{average_packet_loss:.1f}%")
        packet_loss_card.set_trend("down" if average_packet_loss <= 0.5 else "up", f"{'-' if average_packet_loss <= 0.5 else '+'}{abs(average_packet_loss - 0.5):.1f}%")
        _call(packet_loss_card._caption_label, "setText", "综合包损估算")
        packet_loss_card.set_sparkline_data([
            round(average_packet_loss + 1.1, 2),
            round(average_packet_loss + 0.8, 2),
            round(average_packet_loss + 0.5, 2),
            round(average_packet_loss + 0.3, 2),
            round(average_packet_loss + 0.2, 2),
            round(average_packet_loss + 0.1, 2),
            round(average_packet_loss, 2),
        ])

        bandwidth_card = self._kpi_cards["bandwidth"]
        bandwidth_card.set_value(f"{average_bandwidth} Mbps")
        bandwidth_card.set_trend("up" if average_bandwidth >= 800 else "flat", f"{average_bandwidth - 760:+d} Mbps")
        _call(bandwidth_card._caption_label, "setText", "可用链路吞吐")
        bandwidth_card.set_sparkline_data([
            max(300, average_bandwidth - 180),
            max(300, average_bandwidth - 130),
            max(300, average_bandwidth - 90),
            max(300, average_bandwidth - 60),
            max(300, average_bandwidth - 30),
            max(300, average_bandwidth - 12),
            average_bandwidth,
        ])

    def _refresh_analysis_panel(self) -> None:
        active_state = self._tests[self._active_test_id]
        scenario = active_state.current
        status_text, tone = STATUS_COPY[scenario.status]
        tone_color = {
            "pass": _token("status.success"),
            "warning": _token("status.warning"),
            "fail": _token("status.error"),
        }[scenario.status]
        self._detail_badge.setText(status_text)
        self._detail_badge.set_tone(tone)
        _call(
            self._analysis_card,
            "setStyleSheet",
            f"""
            QFrame#networkDiagnosticsDetailCard {{
                background-color: {_rgba(tone_color, 0.06)};
                border: 1px solid {_rgba(tone_color, 0.20)};
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )
        _call(self._detail_title_label, "setText", scenario.detail_title)
        _call(self._detail_output_label, "setText", scenario.detail_body)
        _call(self._detail_recommendations_label, "setText", "\n".join(f"• {item}" for item in scenario.recommendations))

    def _seed_initial_logs(self) -> None:
        active_state = self._tests[self._active_test_id]
        self._append_scenario_logs(active_state, prefix="初始化加载")

    def _run_single_test(self, test_id: str) -> None:
        state = self._tests[test_id]
        state.run_count += 1
        state.current_index = (state.current_index + 1) % len(state.scenarios)
        scenario = state.current
        state.scenarios = tuple(state.scenarios)

        dynamic_last_run = f"刚刚 · 第 {state.run_count} 次"
        state.scenarios = tuple(
            DiagnosticScenario(
                status=item.status,
                status_text=item.status_text,
                last_run_text=dynamic_last_run if index == state.current_index else item.last_run_text,
                latency_ms=item.latency_ms,
                packet_loss_rate=item.packet_loss_rate,
                bandwidth_mbps=item.bandwidth_mbps,
                detail_title=item.detail_title,
                detail_body=item.detail_body,
                recommendations=item.recommendations,
                log_level=item.log_level,
                output_lines=item.output_lines,
            )
            if index == state.current_index
            else item
            for index, item in enumerate(state.scenarios)
        )
        self._active_test_id = test_id
        self._refresh_test_rows()
        self._refresh_metrics()
        self._refresh_analysis_panel()
        self._append_scenario_logs(state, prefix=f"单项运行 {state.name}")
        self._append_log("INFO", f"[{_now_text()}] {state.name} 已完成，当前结果：{scenario.status_text}。")

    def _run_all_tests(self) -> None:
        self._append_log("INFO", "开始执行全部网络诊断测试。")
        for test_id in self._tests:
            self._run_single_test(test_id)
        self._append_log("INFO", "全部网络诊断测试执行完成。")

    def _refresh_dashboard(self) -> None:
        self._refresh_test_rows()
        self._refresh_metrics()
        self._refresh_analysis_panel()
        self._append_log("INFO", "已刷新网络诊断概览与技术分析面板。")

    def _append_scenario_logs(self, state: DiagnosticTestState, prefix: str) -> None:
        scenario = state.current
        self._append_log("INFO", f"{prefix} · {state.name}")
        for line in scenario.output_lines:
            self._append_log(scenario.log_level, line)

    def _append_log(self, level: str, message: str) -> None:
        self._log_viewer.append_log(level, message)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._export_buffer.append(f"[{timestamp}] [{level.strip().upper() or 'INFO'}] {message}")

    def _export_logs(self) -> None:
        default_name = f"network_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        export_path = ""
        if QFileDialog is not None:
            file_path, _selected_filter = QFileDialog.getSaveFileName(self, "导出诊断日志", default_name, "Log Files (*.log);;Text Files (*.txt)")
            export_path = file_path
        else:
            export_path = str(Path.cwd() / default_name)

        if not export_path:
            self._append_log("WARNING", "已取消日志导出。")
            return

        Path(export_path).write_text("\n".join(self._export_buffer), encoding="utf-8")
        self._append_log("INFO", f"诊断日志已导出到：{export_path}")


__all__ = ["NetworkDiagnosticsPage"]

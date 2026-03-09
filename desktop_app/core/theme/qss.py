from __future__ import annotations

"""QSS generation helpers backed by semantic design tokens."""

from string import Template
from typing import Final

from ..types import ThemeMode
from .tokens import STATIC_TOKENS, TOKENS, get_token_value

TOKEN_PREFIX: Final[str] = "@"

_QSS_TEMPLATE = Template(
    r'''
/* TK-OPS semantic theme */
QWidget {
    background-color: ${surface_primary};
    color: ${text_primary};
    font-family: ${font_family_primary};
    font-size: ${font_size_md};
    selection-background-color: ${brand_primary};
    selection-color: ${text_inverse};
}

QMainWindow,
QDialog,
QFrame#MainWindow,
QWidget#MainWindow,
QStackedWidget,
QScrollArea,
QScrollArea > QWidget > QWidget {
    background-color: ${surface_primary};
    color: ${text_primary};
}

QFrame[variant="card"],
QWidget[variant="card"],
QGroupBox,
QMenu,
QToolTip,
QStatusBar,
QDockWidget,
QCalendarWidget QWidget,
QListView,
QTreeView,
QTableView,
QTableWidget,
QPlainTextEdit,
QTextEdit,
QTextBrowser {
    background-color: ${surface_secondary};
    color: ${text_primary};
    border: 1px solid ${border_default};
    border-radius: ${radius_lg};
}

QToolTip {
    padding: ${spacing_sm} ${spacing_lg};
    border: 1px solid ${border_strong};
}

QLabel {
    background: transparent;
    color: ${text_primary};
}

QLabel[role="secondary"],
QLabel[muted="true"],
QGroupBox::title {
    color: ${text_secondary};
}

QLabel[role="tertiary"] {
    color: ${text_tertiary};
}

QLabel[status="success"] { color: ${status_success}; }
QLabel[status="warning"] { color: ${status_warning}; }
QLabel[status="error"] { color: ${status_error}; }
QLabel[status="info"] { color: ${status_info}; }

QLabel[role_tag="manager"] {
    color: ${role_manager};
    background-color: rgba(255,107,107,0.12);
    border-radius: ${radius_pill};
    padding: ${spacing_2xs} ${spacing_md};
}

QLabel[role_tag="creator"] {
    color: ${role_creator};
    background-color: rgba(78,205,196,0.12);
    border-radius: ${radius_pill};
    padding: ${spacing_2xs} ${spacing_md};
}

QLabel[role_tag="analyst"] {
    color: ${role_analyst};
    background-color: rgba(149,225,211,0.12);
    border-radius: ${radius_pill};
    padding: ${spacing_2xs} ${spacing_md};
}

QLabel[role_tag="automation"] {
    color: ${role_automation};
    background-color: rgba(243,129,129,0.12);
    border-radius: ${radius_pill};
    padding: ${spacing_2xs} ${spacing_md};
}

QAbstractButton {
    min-height: ${button_height_md};
    border-radius: ${button_radius};
    font-weight: ${font_weight_medium};
    padding: ${spacing_md} ${spacing_xl};
    color: ${text_primary};
}

QPushButton,
QToolButton,
QCommandLinkButton {
    background-color: ${surface_sunken};
    color: ${text_primary};
    border: 1px solid ${border_default};
}

QPushButton:hover,
QToolButton:hover,
QCommandLinkButton:hover {
    background-color: ${surface_tertiary};
    border-color: ${border_strong};
}

QPushButton:pressed,
QToolButton:pressed,
QCommandLinkButton:pressed {
    background-color: ${surface_primary};
}

QPushButton:focus,
QToolButton:focus,
QCommandLinkButton:focus,
QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QDateEdit:focus,
QTimeEdit:focus,
QDateTimeEdit:focus,
QAbstractItemView:focus,
QTabBar::tab:selected {
    border: 1px solid ${brand_primary};
}

QPushButton[variant="primary"],
QToolButton[variant="primary"],
QCommandLinkButton[variant="primary"],
QPushButton#PrimaryButton,
QToolButton#PrimaryButton {
    background-color: ${brand_primary};
    color: ${text_inverse};
    border: 1px solid ${brand_primary};
    padding: ${spacing_lg} ${spacing_2xl};
}

QPushButton[variant="primary"]:hover,
QToolButton[variant="primary"]:hover,
QCommandLinkButton[variant="primary"]:hover,
QPushButton#PrimaryButton:hover,
QToolButton#PrimaryButton:hover {
    background-color: ${brand_primary_hover};
    border-color: ${brand_primary_hover};
}

QPushButton[variant="primary"]:pressed,
QToolButton[variant="primary"]:pressed,
QCommandLinkButton[variant="primary"]:pressed,
QPushButton#PrimaryButton:pressed,
QToolButton#PrimaryButton:pressed {
    background-color: ${brand_primary_pressed};
    border-color: ${brand_primary_pressed};
}

QPushButton[variant="ghost"],
QToolButton[variant="ghost"] {
    background-color: transparent;
    border: 1px solid transparent;
    color: ${text_secondary};
}

QPushButton[variant="ghost"]:hover,
QToolButton[variant="ghost"]:hover {
    background-color: ${surface_tertiary};
    color: ${brand_primary};
}

QPushButton[variant="danger"],
QToolButton[variant="danger"] {
    background-color: ${status_error};
    border: 1px solid ${status_error};
    color: ${surface_secondary};
}

QPushButton[variant="danger"]:hover,
QToolButton[variant="danger"]:hover {
    background-color: rgba(239,68,68,0.90);
}

QPushButton:disabled,
QToolButton:disabled,
QCommandLinkButton:disabled,
QLineEdit:disabled,
QTextEdit:disabled,
QPlainTextEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled,
QDateEdit:disabled,
QTimeEdit:disabled,
QDateTimeEdit:disabled,
QCheckBox:disabled,
QRadioButton:disabled {
    color: ${text_disabled};
    background-color: ${surface_tertiary};
    border-color: ${border_default};
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QDateEdit,
QTimeEdit,
QDateTimeEdit {
    min-height: ${input_height};
    background-color: ${surface_sunken};
    color: ${text_primary};
    border: 1px solid ${border_default};
    border-radius: ${input_radius};
    padding: ${spacing_lg} ${spacing_xl};
    selection-background-color: ${brand_primary};
    selection-color: ${text_inverse};
}

QComboBox::drop-down,
QDateEdit::drop-down,
QTimeEdit::drop-down,
QDateTimeEdit::drop-down {
    width: 28px;
    border: none;
    background: transparent;
}

QComboBox::down-arrow,
QDateEdit::down-arrow,
QTimeEdit::down-arrow,
QDateTimeEdit::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid ${text_secondary};
    margin-right: ${spacing_md};
}

QAbstractSpinBox::up-button,
QAbstractSpinBox::down-button {
    width: 18px;
    border: none;
    background: transparent;
}

QCheckBox,
QRadioButton {
    spacing: ${spacing_md};
    color: ${text_primary};
}

QCheckBox::indicator,
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    background-color: ${surface_sunken};
    border: 1px solid ${border_strong};
}

QCheckBox::indicator {
    border-radius: ${radius_sm};
}

QRadioButton::indicator {
    border-radius: 9px;
}

QCheckBox::indicator:hover,
QRadioButton::indicator:hover {
    border-color: ${brand_primary};
}

QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    background-color: ${brand_primary};
    border-color: ${brand_primary};
}

QCheckBox::indicator:indeterminate {
    background-color: ${brand_primary_hover};
    border-color: ${brand_primary};
}

QGroupBox {
    margin-top: ${spacing_xl};
    padding: ${spacing_2xl};
    padding-top: ${spacing_3xl};
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: ${spacing_xl};
    padding: 0 ${spacing_sm};
    background-color: ${surface_secondary};
}

QTabWidget::pane {
    background-color: ${surface_secondary};
    border: 1px solid ${border_default};
    border-radius: ${radius_lg};
    top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: ${text_secondary};
    padding: ${spacing_lg} ${spacing_2xl};
    margin-right: ${spacing_sm};
    border: 1px solid transparent;
    border-top-left-radius: ${radius_md};
    border-top-right-radius: ${radius_md};
}

QTabBar::tab:hover {
    color: ${text_primary};
    background-color: ${surface_tertiary};
}

QTabBar::tab:selected {
    background-color: ${surface_secondary};
    color: ${brand_primary};
    border-color: ${border_default};
    border-bottom-color: ${surface_secondary};
}

QMenuBar {
    background-color: ${surface_secondary};
    color: ${text_primary};
    border-bottom: 1px solid ${border_default};
}

QMenuBar::item {
    padding: ${spacing_md} ${spacing_xl};
    background: transparent;
}

QMenuBar::item:selected,
QMenu::item:selected {
    background-color: rgba(0,242,234,0.10);
    color: ${brand_primary};
    border-radius: ${radius_md};
}

QMenu {
    padding: ${spacing_sm};
}

QMenu::item {
    padding: ${spacing_md} ${spacing_2xl};
    margin: ${spacing_2xs};
}

QAbstractItemView {
    background-color: ${surface_secondary};
    alternate-background-color: ${surface_tertiary};
    color: ${text_primary};
    border: 1px solid ${border_default};
    border-radius: ${radius_lg};
    gridline-color: ${border_default};
    outline: none;
}

QAbstractItemView::item {
    min-height: ${table_row_height};
    padding: ${spacing_md} ${spacing_xl};
}

QAbstractItemView::item:hover {
    background-color: rgba(0,242,234,0.08);
}

QAbstractItemView::item:selected,
QListWidget::item:selected,
QTreeWidget::item:selected,
QTableWidget::item:selected {
    background-color: rgba(0,242,234,0.12);
    color: ${brand_primary};
}

QHeaderView::section {
    background-color: ${table_header_bg};
    color: ${text_secondary};
    padding: ${spacing_xl};
    border: none;
    border-bottom: 1px solid ${border_default};
    border-right: 1px solid ${border_default};
    font-weight: ${font_weight_semibold};
}

QTreeView::branch:selected,
QListView::item:selected {
    background-color: rgba(0,242,234,0.10);
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background-color: transparent;
    border: none;
    margin: ${spacing_xs};
}

QScrollBar:vertical {
    width: 12px;
}

QScrollBar:horizontal {
    height: 12px;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background-color: ${border_strong};
    border-radius: ${radius_pill};
    min-height: 28px;
    min-width: 28px;
}

QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background-color: ${brand_accent};
}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {
    border: none;
    background: transparent;
}

QProgressBar {
    min-height: 10px;
    background-color: ${surface_sunken};
    color: ${text_secondary};
    border: 1px solid ${border_default};
    border-radius: ${radius_pill};
    text-align: center;
}

QProgressBar::chunk {
    background-color: ${brand_primary};
    border-radius: ${radius_pill};
}

QSlider::groove:horizontal,
QSlider::groove:vertical {
    background-color: ${surface_sunken};
    border-radius: ${radius_pill};
}

QSlider::groove:horizontal { height: 6px; }
QSlider::groove:vertical { width: 6px; }

QSlider::handle:horizontal,
QSlider::handle:vertical {
    background-color: ${brand_primary};
    border: 2px solid ${surface_secondary};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:vertical {
    margin: 0 -6px;
}

QSplitter::handle {
    background-color: ${border_default};
}

QSplitter::handle:hover {
    background-color: ${brand_primary};
}

QStatusBar {
    border-top: 1px solid ${border_default};
    padding: ${spacing_sm} ${spacing_xl};
}

QToolBar {
    background-color: ${surface_secondary};
    border: none;
    border-bottom: 1px solid ${border_default};
    spacing: ${spacing_sm};
    padding: ${spacing_sm};
}

QToolBar QToolButton {
    min-height: ${button_height_sm};
    padding: ${spacing_sm} ${spacing_lg};
}

QTreeWidget,
QListWidget,
QListView[variant="sidebar"],
QTreeView[variant="sidebar"],
QWidget[variant="sidebar"],
QFrame[variant="sidebar"] {
    background-color: ${brand_secondary};
    color: ${text_primary};
    border: none;
}

QListWidget[variant="sidebar"]::item,
QListView[variant="sidebar"]::item,
QTreeView[variant="sidebar"]::item {
    border-radius: ${radius_md};
    margin: ${spacing_2xs} ${spacing_sm};
    padding: ${spacing_lg} ${spacing_xl};
    color: ${text_secondary};
}

QListWidget[variant="sidebar"]::item:hover,
QListView[variant="sidebar"]::item:hover,
QTreeView[variant="sidebar"]::item:hover {
    background-color: rgba(0,242,234,0.08);
    color: ${text_primary};
}

QListWidget[variant="sidebar"]::item:selected,
QListView[variant="sidebar"]::item:selected,
QTreeView[variant="sidebar"]::item:selected {
    background-color: rgba(0,242,234,0.12);
    color: ${brand_primary};
    border-left: 4px solid ${brand_primary};
}

QFrame[variant="panel"],
QWidget[variant="panel"] {
    background-color: ${surface_elevated};
    border: 1px solid ${border_default};
    border-radius: ${radius_xl};
}

QFrame[variant="sunken"],
QWidget[variant="sunken"] {
    background-color: ${surface_sunken};
    border: 1px solid ${border_default};
    border-radius: ${radius_lg};
}

QFrame[variant="tag"],
QLabel[variant="tag"] {
    background-color: ${tag_color_neutral};
    color: ${text_secondary};
    border-radius: ${tag_radius_pill};
    padding: ${spacing_2xs} ${spacing_md};
    font-size: ${tag_font_size};
    font-weight: ${font_weight_semibold};
}

QFrame[variant="tag"][tone="brand"],
QLabel[variant="tag"][tone="brand"] {
    background-color: ${tag_color_brand_bg};
    color: ${tag_color_brand_fg};
}

QFrame[variant="tag"][tone="success"],
QLabel[variant="tag"][tone="success"] {
    background-color: ${tag_color_success_bg};
    color: ${tag_color_success_fg};
}

QFrame[variant="tag"][tone="warning"],
QLabel[variant="tag"][tone="warning"] {
    background-color: ${tag_color_warning_bg};
    color: ${tag_color_warning_fg};
}

QFrame[variant="tag"][tone="error"],
QLabel[variant="tag"][tone="error"] {
    background-color: ${tag_color_error_bg};
    color: ${tag_color_error_fg};
}
'''
)


def _placeholder_name(token_name: str) -> str:
    return token_name.replace(".", "_").replace("[", "_").replace("]", "")


def resolve_tokens(mode: ThemeMode) -> dict[str, str]:
    """Merge themed and static tokens for a theme mode."""

    resolved = {name: token.resolve(mode) for name, token in TOKENS.items()}
    resolved.update(STATIC_TOKENS)
    resolved["table.header_bg"] = get_token_value("table.header_bg.dark", mode) if mode == ThemeMode.DARK else get_token_value("table.header_bg", mode)
    return resolved


def generate_qss(mode: ThemeMode) -> str:
    """Generate the complete TK-OPS stylesheet for a theme mode."""

    resolved_tokens = resolve_tokens(mode)
    substitutions = {_placeholder_name(name): value for name, value in resolved_tokens.items()}
    qss = _QSS_TEMPLATE.substitute(substitutions)
    for token_name, value in resolved_tokens.items():
        qss = qss.replace(f"{TOKEN_PREFIX}{token_name}", value)
    return qss.strip()


class QssBuilder:
    """Simple builder wrapper for compatibility with the shell package."""

    def build(self, mode: ThemeMode) -> str:
        """Generate a stylesheet for the provided theme mode."""

        return generate_qss(mode)


__all__ = ["QssBuilder", "generate_qss", "resolve_tokens"]

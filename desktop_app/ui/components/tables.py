# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false, reportAssignmentType=false, reportGeneralTypeIssues=false

from __future__ import annotations

"""主题化数据表格组件。"""

from math import ceil
from typing import Any, Sequence

from .inputs import (
    BUTTON_HEIGHT,
    RADIUS_LG,
    SPACING_LG,
    SPACING_MD,
    SPACING_SM,
    SPACING_XL,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    _call,
    _connect,
    _palette,
    _static_token,
)

try:
    from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
    from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView

    QT_TABLE_AVAILABLE = True
except ImportError:
    from ...core.qt import Signal

    QT_TABLE_AVAILABLE = False

    class QModelIndex:
        """无 Qt 环境时的最小模型索引。"""

        def __init__(self, row: int = -1, column: int = -1) -> None:
            self._row = row
            self._column = column

        def row(self) -> int:
            return self._row

        def column(self) -> int:
            return self._column

        def isValid(self) -> bool:
            return self._row >= 0 and self._column >= 0

    class QAbstractTableModel:
        """无 Qt 环境时的最小表格模型基类。"""

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

        def beginResetModel(self) -> None:
            return None

        def endResetModel(self) -> None:
            return None

        def createIndex(self, row: int, column: int) -> QModelIndex:
            return QModelIndex(row, column)

    class Qt:
        """无 Qt 环境时的最小常量集合。"""

        class ItemDataRole:
            DisplayRole = 0
            TextAlignmentRole = 1

        class Orientation:
            Horizontal = 1
            Vertical = 2

        class SortOrder:
            AscendingOrder = 0
            DescendingOrder = 1

        class AlignmentFlag:
            AlignCenter = 0
            AlignVCenter = 0

        class SelectionBehavior:
            SelectRows = 0

        class SelectionMode:
            SingleSelection = 0

        NoItemFlags = 0
        ItemIsEnabled = 1
        ItemIsSelectable = 2

    class QAbstractItemView:
        """无 Qt 环境时的最小视图常量。"""

        class SelectionBehavior:
            SelectRows = 0

        class SelectionMode:
            SingleSelection = 0

        class EditTrigger:
            NoEditTriggers = 0

    class QHeaderView:
        """无 Qt 环境时的最小表头对象。"""

        Stretch = 1

        def setStretchLastSection(self, _value: bool) -> None:
            return None

        def setSectionResizeMode(self, _mode: int) -> None:
            return None

        def setDefaultAlignment(self, _alignment: int) -> None:
            return None

        def setHighlightSections(self, _value: bool) -> None:
            return None

    class _SelectionModel:
        """无 Qt 环境时的最小选择模型。"""

        currentRowChanged = Signal(object, object)

    class QTableView(QWidget):
        """无 Qt 环境时的最小表格视图。"""

        doubleClicked = Signal(object)

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self._model: Any = None
            self._selection_model = _SelectionModel()

        def setModel(self, model: Any) -> None:
            self._model = model

        def selectionModel(self) -> _SelectionModel:
            return self._selection_model

        def horizontalHeader(self) -> QHeaderView:
            return QHeaderView()

        def verticalHeader(self) -> QHeaderView:
            return QHeaderView()

        def setSortingEnabled(self, _value: bool) -> None:
            return None

        def setAlternatingRowColors(self, _value: bool) -> None:
            return None

        def setSelectionBehavior(self, _value: int) -> None:
            return None

        def setSelectionMode(self, _value: int) -> None:
            return None

        def setEditTriggers(self, _value: int) -> None:
            return None

        def setShowGrid(self, _value: bool) -> None:
            return None

        def setWordWrap(self, _value: bool) -> None:
            return None

        def setCornerButtonEnabled(self, _value: bool) -> None:
            return None

        def setMinimumHeight(self, _value: int) -> None:
            return None

        def selectRow(self, _row: int) -> None:
            return None

        def scrollTo(self, _index: QModelIndex) -> None:
            return None


def _safe_int(value: str, default: int) -> int:
    """从 token 中读取像素整数。"""

    raw = _static_token(value)
    digits = "".join(character for character in raw if character.isdigit())
    return int(digits) if digits else default


ROW_HEIGHT = _safe_int("table.row_height", 48)


def _emit(signal_like: object) -> None:
    """安全触发 Qt 风格信号。"""

    emit = getattr(signal_like, "emit", None)
    if callable(emit):
        emit()


class _PagedTableModel(QAbstractTableModel):
    """支持分页与排序的轻量表格模型。"""

    def __init__(self, headers: Sequence[str], rows: Sequence[Sequence[object]] | None = None) -> None:
        super().__init__()
        if not QT_TABLE_AVAILABLE:
            self.layoutAboutToBeChanged = Signal()
            self.layoutChanged = Signal()
            self.modelReset = Signal()
        self._headers: list[str] = [str(header) for header in headers]
        self._all_rows: list[list[object]] = [list(row) for row in rows or []]
        self._page_size = 10
        self._page = 1
        self._sort_column = -1
        self._sort_order = getattr(getattr(Qt, "SortOrder", Qt), "AscendingOrder", 0)

    def index(self, row: int, column: int, parent: QModelIndex | None = None) -> QModelIndex:
        """返回模型索引。"""

        _ = parent
        if QT_TABLE_AVAILABLE:
            return self.createIndex(row, column)
        return QModelIndex(row, column)

    def rowCount(self, _parent: QModelIndex | None = None) -> int:
        """返回当前页行数。"""

        return len(self._page_rows())

    def columnCount(self, _parent: QModelIndex | None = None) -> int:
        """返回列数。"""

        return len(self._headers)

    def data(self, index: QModelIndex, role: int = 0) -> object | None:
        """返回单元格展示内容。"""

        if not getattr(index, "isValid", lambda: False)():
            return None
        row = index.row()
        column = index.column()
        current_rows = self._page_rows()
        if not (0 <= row < len(current_rows) and 0 <= column < len(self._headers)):
            return None
        display_role = getattr(getattr(Qt, "ItemDataRole", Qt), "DisplayRole", 0)
        alignment_role = getattr(getattr(Qt, "ItemDataRole", Qt), "TextAlignmentRole", 1)
        if role == display_role:
            return str(current_rows[row][column])
        if role == alignment_role:
            return getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0)
        return None

    def headerData(self, section: int, orientation: object, role: int = 0) -> object | None:
        """返回表头文案。"""

        display_role = getattr(getattr(Qt, "ItemDataRole", Qt), "DisplayRole", 0)
        if role != display_role:
            return None
        horizontal = getattr(getattr(Qt, "Orientation", Qt), "Horizontal", 1)
        if orientation == horizontal and 0 <= section < len(self._headers):
            return self._headers[section]
        page_rows = self._page_rows()
        if 0 <= section < len(page_rows):
            return str((self._page - 1) * self._page_size + section + 1)
        return None

    def flags(self, index: QModelIndex) -> int:
        """返回单元格交互属性。"""

        if not getattr(index, "isValid", lambda: False)():
            return getattr(Qt, "NoItemFlags", 0)
        return getattr(Qt, "ItemIsEnabled", 1) | getattr(Qt, "ItemIsSelectable", 2)

    def sort(self, column: int, order: object = None) -> None:
        """按列排序。"""

        if not (0 <= column < len(self._headers)):
            return
        self._sort_column = column
        self._sort_order = order if order is not None else getattr(getattr(Qt, "SortOrder", Qt), "AscendingOrder", 0)
        reverse = self._sort_order == getattr(getattr(Qt, "SortOrder", Qt), "DescendingOrder", 1)
        if QT_TABLE_AVAILABLE:
            self.beginResetModel()
        else:
            layout_about = getattr(self, "layoutAboutToBeChanged", None)
            _emit(layout_about)
        self._all_rows.sort(key=lambda row: self._sort_key(row, column), reverse=reverse)
        if QT_TABLE_AVAILABLE:
            self.endResetModel()
        else:
            layout_done = getattr(self, "layoutChanged", None)
            _emit(layout_done)

    def set_rows(self, rows: Sequence[Sequence[object]]) -> None:
        """重置数据源。"""

        if QT_TABLE_AVAILABLE:
            self.beginResetModel()
        self._all_rows = [list(row) for row in rows]
        self._page = 1
        if QT_TABLE_AVAILABLE:
            self.endResetModel()
        else:
            _emit(getattr(self, "modelReset", None))

    def set_page_size(self, page_size: int) -> None:
        """设置分页大小。"""

        if QT_TABLE_AVAILABLE:
            self.beginResetModel()
        self._page_size = max(1, page_size)
        self._page = min(self._page, self.page_count())
        if QT_TABLE_AVAILABLE:
            self.endResetModel()
        else:
            _emit(getattr(self, "modelReset", None))

    def set_page(self, page: int) -> None:
        """切换当前页。"""

        next_page = min(max(1, page), self.page_count())
        if next_page == self._page:
            return
        if QT_TABLE_AVAILABLE:
            self.beginResetModel()
        self._page = next_page
        if QT_TABLE_AVAILABLE:
            self.endResetModel()
        else:
            _emit(getattr(self, "modelReset", None))

    def current_page(self) -> int:
        """返回当前页码。"""

        return self._page

    def page_count(self) -> int:
        """返回总页数。"""

        if not self._all_rows:
            return 1
        return max(1, ceil(len(self._all_rows) / self._page_size))

    def total_rows(self) -> int:
        """返回总记录数。"""

        return len(self._all_rows)

    def absolute_row(self, page_row: int) -> int:
        """将页内行号转换为全局行号。"""

        absolute = (self._page - 1) * self._page_size + page_row
        return absolute if 0 <= absolute < len(self._all_rows) else -1

    def _page_rows(self) -> list[list[object]]:
        start = (self._page - 1) * self._page_size
        end = start + self._page_size
        return self._all_rows[start:end]

    @staticmethod
    def _sort_key(row: Sequence[object], column: int) -> tuple[int, object]:
        value = row[column] if column < len(row) else ""
        if isinstance(value, (int, float)):
            return (0, float(value))
        text = str(value).replace("%", "").replace(",", "").strip()
        try:
            return (0, float(text))
        except ValueError:
            return (1, str(value))


class DataTable(QWidget):
    """基于 QTableView 的可排序分页数据表格。"""

    row_selected = Signal(int)
    row_double_clicked = Signal(int)

    def __init__(
        self,
        headers: Sequence[str] | None = None,
        rows: Sequence[Sequence[object]] | None = None,
        *,
        page_size: int = 10,
        empty_text: str = "暂无数据",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        _call(self, "setObjectName", "dataTable")
        self._empty_text = empty_text
        self._headers = list(headers or [])
        self._model = _PagedTableModel(self._headers, rows or [])
        self._suppress_selection_signal = False
        self._model.set_page_size(page_size)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACING_MD)

        self._table = QTableView(self)
        _call(self._table, "setObjectName", "dataTableView")
        _call(self._table, "setModel", self._model)
        _call(self._table, "setSortingEnabled", True)
        _call(self._table, "setAlternatingRowColors", True)
        _call(
            self._table,
            "setSelectionBehavior",
            getattr(getattr(QAbstractItemView, "SelectionBehavior", QAbstractItemView), "SelectRows", 0),
        )
        _call(
            self._table,
            "setSelectionMode",
            getattr(getattr(QAbstractItemView, "SelectionMode", QAbstractItemView), "SingleSelection", 0),
        )
        _call(
            self._table,
            "setEditTriggers",
            getattr(getattr(QAbstractItemView, "EditTrigger", QAbstractItemView), "NoEditTriggers", 0),
        )
        _call(self._table, "setShowGrid", False)
        _call(self._table, "setWordWrap", False)
        _call(self._table, "setCornerButtonEnabled", False)
        _call(self._table, "setMinimumHeight", 320)

        horizontal_header = getattr(self._table, "horizontalHeader", lambda: None)()
        vertical_header = getattr(self._table, "verticalHeader", lambda: None)()
        if horizontal_header is not None:
            _call(horizontal_header, "setStretchLastSection", True)
            _call(horizontal_header, "setSectionResizeMode", getattr(QHeaderView, "Stretch", 1))
            _call(horizontal_header, "setDefaultAlignment", getattr(getattr(Qt, "AlignmentFlag", Qt), "AlignCenter", 0))
            _call(horizontal_header, "setHighlightSections", False)
        if vertical_header is not None:
            _call(vertical_header, "setVisible", False)
            _call(vertical_header, "setDefaultSectionSize", ROW_HEIGHT)

        self._empty_label = QLabel(empty_text, self)
        _call(self._empty_label, "setObjectName", "dataTableEmpty")

        pagination = QHBoxLayout()
        pagination.setSpacing(SPACING_SM)

        self._summary_label = QLabel("", self)
        _call(self._summary_label, "setObjectName", "dataTableSummary")

        self._prev_button = QPushButton("上一页", self)
        self._next_button = QPushButton("下一页", self)
        _call(self._prev_button, "setObjectName", "dataTablePageButton")
        _call(self._next_button, "setObjectName", "dataTablePageButton")
        _call(self._prev_button, "setProperty", "variant", "ghost")
        _call(self._next_button, "setProperty", "variant", "ghost")

        self._page_label = QLabel("", self)
        _call(self._page_label, "setObjectName", "dataTablePageLabel")

        pagination.addWidget(self._summary_label)
        pagination.addStretch(1)
        pagination.addWidget(self._prev_button)
        pagination.addWidget(self._page_label)
        pagination.addWidget(self._next_button)

        root.addWidget(self._table)
        root.addWidget(self._empty_label)
        root.addLayout(pagination)

        selection_model = getattr(self._table, "selectionModel", lambda: None)()
        if selection_model is not None:
            _connect(getattr(selection_model, "currentRowChanged", None), self._on_row_changed)
        _connect(getattr(self._table, "doubleClicked", None), self._on_double_clicked)
        _connect(getattr(self._prev_button, "clicked", None), self.previous_page)
        _connect(getattr(self._next_button, "clicked", None), self.next_page)
        _connect(getattr(self._model, "modelReset", None), self._refresh_state)
        _connect(getattr(self._model, "layoutChanged", None), self._refresh_state)
        self._apply_styles()
        self._refresh_state()

    @property
    def table_view(self) -> QTableView:
        """暴露底层表格视图。"""

        return self._table

    def set_rows(self, rows: Sequence[Sequence[object]]) -> None:
        """设置全部数据。"""

        self._model.set_rows(rows)
        self._refresh_state()

    def set_page_size(self, page_size: int) -> None:
        """设置每页记录数。"""

        self._model.set_page_size(page_size)
        self._refresh_state()

    def sort_by_column(self, column: int, descending: bool = False) -> None:
        """程序化触发排序。"""

        order = getattr(getattr(Qt, "SortOrder", Qt), "DescendingOrder" if descending else "AscendingOrder", 0)
        self._model.sort(column, order)
        self._refresh_state()

    def current_page(self) -> int:
        """返回当前页码。"""

        return self._model.current_page()

    def page_count(self) -> int:
        """返回总页数。"""

        return self._model.page_count()

    def next_page(self) -> None:
        """切换到下一页。"""

        self._model.set_page(self._model.current_page() + 1)
        self._refresh_state()

    def previous_page(self) -> None:
        """切换到上一页。"""

        self._model.set_page(self._model.current_page() - 1)
        self._refresh_state()

    def go_to_page(self, page: int) -> None:
        """跳转到指定页。"""

        self._model.set_page(page)
        self._refresh_state()

    def select_absolute_row(self, row: int) -> None:
        """选中指定全局行。"""

        if row < 0 or row >= self._model.total_rows():
            return
        target_page = row // max(self._model._page_size, 1) + 1
        self.go_to_page(target_page)
        page_row = row % max(self._model._page_size, 1)
        self._suppress_selection_signal = True
        try:
            _call(self._table, "selectRow", page_row)
        finally:
            self._suppress_selection_signal = False

    def _on_row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if self._suppress_selection_signal:
            return
        if not getattr(current, "isValid", lambda: False)():
            return
        absolute = self._model.absolute_row(current.row())
        if absolute >= 0:
            self.row_selected.emit(absolute)

    def _on_double_clicked(self, index: QModelIndex) -> None:
        if not getattr(index, "isValid", lambda: False)():
            return
        absolute = self._model.absolute_row(index.row())
        if absolute >= 0:
            self.row_double_clicked.emit(absolute)

    def _refresh_state(self) -> None:
        total = self._model.total_rows()
        page = self._model.current_page()
        pages = self._model.page_count()
        if total == 0:
            summary_text = self._empty_text
        else:
            start = (page - 1) * self._model._page_size + 1
            end = min(page * self._model._page_size, total)
            summary_text = f"显示第 {start}-{end} 条，共 {total} 条"
        _call(self._summary_label, "setText", summary_text)
        _call(self._page_label, "setText", f"第 {page} / {pages} 页")
        _call(self._empty_label, "setVisible", total == 0)
        _call(self._table, "setVisible", total > 0)
        _call(self._prev_button, "setEnabled", page > 1)
        _call(self._next_button, "setEnabled", page < pages)

    def _apply_styles(self) -> None:
        colors = _palette()
        _call(
            self,
            "setStyleSheet",
            f"""
            QWidget#dataTable {{
                background: transparent;
            }}
            QTableView#dataTableView {{
                background-color: {colors.surface};
                alternate-background-color: {colors.surface_alt};
                color: {colors.text};
                border: 1px solid {colors.border};
                border-radius: {RADIUS_LG}px;
                gridline-color: {colors.border};
                selection-background-color: rgba(0,242,234,0.12);
                selection-color: {_static_token('tag.color.brand.fg')};
                font-size: {_static_token('font.size.sm')};
            }}
            QTableView#dataTableView::item {{
                padding: {SPACING_MD}px {SPACING_XL}px;
                border-bottom: 1px solid {colors.border};
                min-height: {ROW_HEIGHT}px;
            }}
            QHeaderView::section {{
                background-color: {colors.surface_alt};
                color: {colors.text_muted};
                border: none;
                border-bottom: 1px solid {colors.border};
                padding: {SPACING_XL}px {SPACING_LG}px;
                font-size: {_static_token('font.size.sm')};
                font-weight: {_static_token('font.weight.semibold')};
            }}
            QLabel#dataTableSummary, QLabel#dataTablePageLabel {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.sm')};
            }}
            QLabel#dataTableEmpty {{
                color: {colors.text_muted};
                font-size: {_static_token('font.size.md')};
                padding: {SPACING_XL}px;
                background-color: {colors.surface_alt};
                border: 1px dashed {colors.border};
                border-radius: {RADIUS_LG}px;
            }}
            QPushButton#dataTablePageButton {{
                min-height: {BUTTON_HEIGHT}px;
                padding: {SPACING_MD}px {SPACING_LG}px;
                border-radius: {RADIUS_LG}px;
            }}
            """,
        )


__all__ = ["DataTable"]

from __future__ import annotations

"""Base class for route-backed shell pages."""

from ...core.qt import QLabel, QVBoxLayout, QWidget
from ...core.types import RouteId


class BasePage(QWidget):
    """Shared QWidget base class for all shell pages."""

    default_route_id: RouteId = RouteId("base_page")
    default_display_name: str = "Base Page"
    default_icon_name: str = "widgets"

    def __init__(
        self,
        route_id: RouteId | None = None,
        display_name: str | None = None,
        icon_name: str | None = None,
        parent: object | None = None,
    ) -> None:
        super().__init__(parent)
        self._route_id: RouteId = route_id or self.default_route_id
        self._display_name: str = display_name or self.default_display_name
        self._icon_name: str = icon_name or self.default_icon_name
        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.setup_ui()

    @property
    def route_id(self) -> RouteId:
        return self._route_id

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def icon_name(self) -> str:
        return self._icon_name

    def setup_ui(self) -> None:
        """Build the default placeholder page layout."""

        self.layout.addWidget(QLabel(self.display_name))
        self.layout.addWidget(QLabel(f"Route: {self.route_id}"))
        self.layout.addStretch(1)

    def on_activated(self) -> None:
        """Hook invoked when the page becomes the active route."""

        return None

    def on_deactivated(self) -> None:
        """Hook invoked when the page is no longer the active route."""

        return None

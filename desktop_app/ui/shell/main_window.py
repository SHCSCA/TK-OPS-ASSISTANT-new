# pyright: basic, reportAttributeAccessIssue=false

from __future__ import annotations

"""Main application shell for the new TK-OPS architecture."""

from typing import cast

from ...core.qt import QApplication, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
from ...core.types import ThemeMode
from ...core.shell.navigation import NavigationModel
from ...core.shell.registry import PageHost, RouteRegistry
from ...core.types import RouteId

from .sidebar import Sidebar
from .status_bar import StatusBar
from .title_bar import TitleBar


class MainWindow(QMainWindow):
    """Route-driven shell window that hosts the new placeholder pages."""

    def __init__(
        self,
        *,
        route_registry: RouteRegistry,
        navigation_model: NavigationModel,
        theme_engine: object,
        config_bus: object,
        parent: object | None = None,
    ) -> None:
        super().__init__(parent)
        self.route_registry = route_registry
        self.navigation_model = navigation_model
        self.theme_engine = theme_engine
        self.config_bus = config_bus
        self._current_route_id: str | None = None
        self._pages: dict[str, object] = {}

        self.setWindowTitle("TK-OPS Desktop Shell")
        self.resize(1600, 960)
        self.setMinimumSize(1280, 780)

        self._title_bar = TitleBar()
        self._sidebar = Sidebar()
        self._page_host = PageHost()
        self._status_bar = StatusBar()
        self._body: QWidget | None = None
        self._central: QWidget | None = None

        self._setup_ui()
        self._bind_shell_events()
        self._apply_theme_surface()
        self._mount_routes()
        self._sidebar.populate(self.navigation_model)
        self._sidebar.route_requested.connect(self.navigate_to)
        self._activate_initial_route()

    def _setup_ui(self) -> None:
        central = QWidget(self)
        self._central = central
        outer_layout = QVBoxLayout(central)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        body = QWidget(central)
        self._body = body
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self._sidebar)
        body_layout.addWidget(self._page_host, 1)

        outer_layout.addWidget(self._title_bar)
        outer_layout.addWidget(body, 1)
        outer_layout.addWidget(self._status_bar)
        self.setCentralWidget(central)

    def _bind_shell_events(self) -> None:
        theme_toggle = getattr(self._title_bar, "theme_toggle_requested", None)
        connect = getattr(theme_toggle, "connect", None)
        if callable(connect):
            connect(self._on_theme_toggle_requested)

        theme_changed = getattr(self.theme_engine, "theme_changed", None)
        connect_theme = getattr(theme_changed, "connect", None)
        if callable(connect_theme):
            connect_theme(self._on_theme_changed)

    def _on_theme_toggle_requested(self) -> None:
        toggle = getattr(self.theme_engine, "toggle", None)
        if callable(toggle):
            toggle()

    def _on_theme_changed(self, mode_value: str) -> None:
        self._apply_theme_surface(mode_value)

    def _apply_theme_surface(self, mode_value: str | None = None) -> None:
        resolved = ThemeMode.DARK if str(mode_value or getattr(getattr(self.theme_engine, "current_mode", None), "value", "light")).lower() == "dark" else ThemeMode.LIGHT
        palette_mode = resolved.value
        app_instance = QApplication.instance() if hasattr(QApplication, "instance") else None

        if app_instance is not None:
            set_property = getattr(app_instance, "setProperty", None)
            if callable(set_property):
                set_property("theme.mode", palette_mode)
                set_property("theme_mode", palette_mode)
                set_property("themeMode", palette_mode)

        surface = "#071521" if resolved == ThemeMode.DARK else "#F4F7FB"
        body_surface = "#0B1D2A" if resolved == ThemeMode.DARK else "#F7FAFC"
        text = "#EAF4FF" if resolved == ThemeMode.DARK else "#10233F"
        border = "#173245" if resolved == ThemeMode.DARK else "#D9E4EF"
        if self._central is not None:
            set_style = getattr(self._central, "setStyleSheet", None)
            if callable(set_style):
                set_style(f"background-color: {surface}; color: {text};")
        if self._body is not None:
            set_style = getattr(self._body, "setStyleSheet", None)
            if callable(set_style):
                set_style(f"background-color: {body_surface}; border-top: 1px solid {border}; border-bottom: 1px solid {border};")

    def _mount_routes(self) -> None:
        for definition in self.route_registry.definitions():
            page = self._page_host.mount(definition)
            self._pages[str(definition.route_id)] = cast(object, page)

    def _activate_initial_route(self) -> None:
        if not self.navigation_model.sections:
            return
        first_section = self.navigation_model.sections[0]
        if not first_section.items:
            return
        self.navigate_to(str(first_section.items[0].route_id))

    def navigate_to(self, route_id: str) -> None:
        """Switch the shell to the requested page route."""

        if self._current_route_id == route_id:
            return
        previous_page = self._pages.get(self._current_route_id or "")
        previous_deactivate = getattr(previous_page, "on_deactivated", None)
        if callable(previous_deactivate):
            previous_deactivate()

        definition = self.route_registry.get(RouteId(route_id))
        if definition is None:
            raise KeyError(f"Route '{route_id}' is not registered.")
        self._page_host.activate(RouteId(route_id))
        self._sidebar.set_active_route(route_id)
        self._title_bar.set_page_title(definition.display_name)
        self._status_bar.set_message(f"当前页面: {definition.display_name}")

        current_page = self._pages.get(route_id)
        current_activate = getattr(current_page, "on_activated", None)
        if callable(current_activate):
            current_activate()
        self._current_route_id = route_id

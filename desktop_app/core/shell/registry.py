from __future__ import annotations

# pyright: basic

"""Route registry and page-host primitives for the plugin shell."""

from ..qt import QStackedWidget, QWidget
from ..types import DomainGroup, PageFactory, RouteId


class RouteDefinition:
    """Immutable metadata and factory for a routable page."""

    def __init__(
        self,
        route_id: RouteId,
        display_name: str,
        icon_name: str,
        domain_group: DomainGroup,
        page_factory: PageFactory,
        has_sub_tabs: bool = False,
        ai_features: list[str] | None = None,
    ) -> None:
        self.route_id = route_id
        self.display_name = display_name
        self.icon_name = icon_name
        self.domain_group = domain_group
        self.page_factory = page_factory
        self.has_sub_tabs = has_sub_tabs
        self.ai_features = list(ai_features or [])


class RouteRegistry:
    """Central registry mapping route identifiers to page factories."""

    def __init__(self) -> None:
        self._routes: dict[str, RouteDefinition] = {}
        self._page_cache: dict[str, QWidget] = {}

    def register(self, definition: RouteDefinition) -> None:
        """Register a route definition exactly once."""

        route_key = str(definition.route_id)
        if route_key in self._routes:
            raise ValueError(f"Route '{route_key}' is already registered.")
        self._routes[route_key] = definition

    def get(self, route_id: RouteId) -> RouteDefinition | None:
        """Resolve a route definition by identifier."""

        return self._routes.get(str(route_id))

    def all_routes(self) -> list[RouteDefinition]:
        """Return registered routes in insertion order."""

        return list(self._routes.values())

    def definitions(self) -> list[RouteDefinition]:
        """Compatibility alias for existing shell consumers."""

        return self.all_routes()

    def routes_by_domain(self, domain: DomainGroup) -> list[RouteDefinition]:
        """Return all routes for a given domain group."""

        return [definition for definition in self._routes.values() if definition.domain_group == domain]

    def has_route(self, route_id: RouteId) -> bool:
        """Return whether the route is registered."""

        return str(route_id) in self._routes

    def create_page(self, route_id: RouteId) -> QWidget:
        """Create or reuse a page instance by invoking the registered factory lazily."""

        route_key = str(route_id)
        cached_page = self._page_cache.get(route_key)
        if cached_page is not None:
            return cached_page
        definition = self.get(route_id)
        if definition is None:
            raise KeyError(f"Route '{route_key}' is not registered.")
        page = definition.page_factory()
        self._page_cache[route_key] = page
        return page


class PageHost(QStackedWidget):
    """Stacked content host that mounts route pages in the shell center pane."""

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self._indexes: dict[str, int] = {}
        self._pages: dict[str, QWidget] = {}

    def mount(self, definition: RouteDefinition) -> QWidget:
        """Instantiate and mount a page for the supplied route once."""

        route_key = str(definition.route_id)
        existing_page = self._pages.get(route_key)
        if existing_page is not None:
            return existing_page
        page = definition.page_factory()
        index = self.addWidget(page)
        self._indexes[route_key] = index
        self._pages[route_key] = page
        return page

    def activate(self, route_id: RouteId) -> None:
        """Switch the host to the requested mounted route."""

        route_key = str(route_id)
        if route_key not in self._indexes:
            raise KeyError(f"Route '{route_key}' is not mounted in the page host.")
        self.setCurrentIndex(self._indexes[route_key])

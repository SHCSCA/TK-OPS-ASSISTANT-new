from __future__ import annotations

import unittest
from collections.abc import Callable

from ....core.shell.registry import RouteDefinition, RouteRegistry
from ....core.types import DomainGroup, RouteId
from ....ui.pages.base_page import BasePage


ASSERT = unittest.TestCase()


class DummyPage(BasePage):
    default_route_id: RouteId = RouteId("dummy_page")
    default_display_name: str = "Dummy Page"
    default_icon_name: str = "square"


def make_definition(
    route_id: str,
    domain_group: DomainGroup,
    factory: Callable[[], BasePage] | None = None,
) -> RouteDefinition:
    page_factory = factory if callable(factory) else DummyPage
    return RouteDefinition(
        route_id=RouteId(route_id),
        display_name=route_id.replace("_", " ").title(),
        icon_name="square",
        domain_group=domain_group,
        page_factory=page_factory,
    )


def test_register_and_get() -> None:
    registry = RouteRegistry()
    definition = make_definition("dashboard_home", DomainGroup.DASHBOARD)

    registry.register(definition)

    assert registry.get(RouteId("dashboard_home")) is definition


def test_register_duplicate_raises() -> None:
    registry = RouteRegistry()
    definition = make_definition("dashboard_home", DomainGroup.DASHBOARD)
    registry.register(definition)

    with ASSERT.assertRaisesRegex(ValueError, "already registered"):
        registry.register(make_definition("dashboard_home", DomainGroup.DASHBOARD))


def test_get_nonexistent_returns_none() -> None:
    registry = RouteRegistry()

    assert registry.get(RouteId("missing")) is None


def test_all_routes_returns_insertion_order() -> None:
    registry = RouteRegistry()
    first = make_definition("dashboard_home", DomainGroup.DASHBOARD)
    second = make_definition("analytics_home", DomainGroup.ANALYTICS)
    third = make_definition("system_settings", DomainGroup.SYSTEM)
    registry.register(first)
    registry.register(second)
    registry.register(third)

    assert registry.all_routes() == [first, second, third]


def test_routes_by_domain_filters_correctly() -> None:
    registry = RouteRegistry()
    dashboard = make_definition("dashboard_home", DomainGroup.DASHBOARD)
    analytics = make_definition("analytics_home", DomainGroup.ANALYTICS)
    analytics_detail = make_definition("analytics_detail", DomainGroup.ANALYTICS)
    registry.register(dashboard)
    registry.register(analytics)
    registry.register(analytics_detail)

    assert registry.routes_by_domain(DomainGroup.ANALYTICS) == [analytics, analytics_detail]


def test_has_route() -> None:
    registry = RouteRegistry()
    registry.register(make_definition("dashboard_home", DomainGroup.DASHBOARD))

    assert registry.has_route(RouteId("dashboard_home")) is True
    assert registry.has_route(RouteId("missing")) is False


def test_create_page_caches_result() -> None:
    registry = RouteRegistry()
    calls: list[str] = []

    def factory() -> DummyPage:
        calls.append("created")
        return DummyPage()

    registry.register(make_definition("dashboard_home", DomainGroup.DASHBOARD, factory))

    first = registry.create_page(RouteId("dashboard_home"))
    second = registry.create_page(RouteId("dashboard_home"))

    assert first is second
    assert calls == ["created"]


def test_create_page_unknown_route_raises() -> None:
    registry = RouteRegistry()

    with ASSERT.assertRaisesRegex(KeyError, "not registered"):
        _ = registry.create_page(RouteId("missing"))


def test_definitions_alias_matches_all_routes() -> None:
    registry = RouteRegistry()
    definition = make_definition("dashboard_home", DomainGroup.DASHBOARD)
    registry.register(definition)

    assert registry.definitions() == registry.all_routes()


def test_create_page_returns_distinct_instances_per_route() -> None:
    registry = RouteRegistry()
    registry.register(make_definition("dashboard_home", DomainGroup.DASHBOARD))
    registry.register(make_definition("analytics_home", DomainGroup.ANALYTICS))

    dashboard_page = registry.create_page(RouteId("dashboard_home"))
    analytics_page = registry.create_page(RouteId("analytics_home"))

    assert dashboard_page is not analytics_page

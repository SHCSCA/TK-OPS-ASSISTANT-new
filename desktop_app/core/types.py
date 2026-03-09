from __future__ import annotations

# pyright: basic

"""Shared foundational types for the TK-OPS application shell."""

from enum import Enum
from typing import TYPE_CHECKING, Callable, Mapping, NamedTuple, NewType

if TYPE_CHECKING:
    from ..ui.pages.base_page import BasePage

RouteId = NewType("RouteId", str)
ConfigKey = NewType("ConfigKey", str)
EventName = NewType("EventName", str)
CommandName = NewType("CommandName", str)
ThemeTokenName = NewType("ThemeTokenName", str)
JsonDict = "dict[str, object]"
MetadataMap = Mapping[str, object]
PageFactory = Callable[[], "BasePage"]


class ThemeMode(str, Enum):
    """Supported application theme modes."""

    LIGHT = "light"
    DARK = "dark"


class DomainGroup(str, Enum):
    """Canonical domain group identifiers derived from planning docs."""

    DASHBOARD = "dashboard"
    ACCOUNT = "account"
    OPERATIONS = "operations"
    CONTENT = "content"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    AI = "ai"
    SYSTEM = "system"
    CRM = "crm"


class RouteDescriptor(NamedTuple):
    """Immutable metadata describing a routable page."""

    route_id: RouteId
    display_name: str
    icon_name: str
    domain_group: DomainGroup
    is_shell_entry: bool = True


class ServiceDescriptor(NamedTuple):
    """Simple service registration metadata container."""

    name: str
    domain_group: DomainGroup
    tags: tuple[str, ...] = ()

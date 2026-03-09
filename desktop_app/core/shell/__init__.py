from __future__ import annotations

"""Plugin-shell primitives for routing, navigation, and lifecycle."""

from .lifecycle import LifecycleManager, PluginLifecycle
from .navigation import NavGroup, NavItem, NavigationItem, NavigationModel, NavigationSection, build_default_navigation
from .registry import PageHost, RouteDefinition, RouteRegistry

__all__ = [
    "LifecycleManager",
    "NavGroup",
    "NavItem",
    "NavigationItem",
    "NavigationModel",
    "NavigationSection",
    "PageHost",
    "PluginLifecycle",
    "RouteDefinition",
    "RouteRegistry",
    "build_default_navigation",
]

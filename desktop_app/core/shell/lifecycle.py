from __future__ import annotations

"""Plugin lifecycle contracts and manager for shell-managed page modules."""

from typing import Protocol

from ..types import RouteId


class PluginLifecycle(Protocol):
    """Lifecycle hooks for plugin-style page modules."""

    def on_register(self) -> None:
        """Called once after the plugin is registered."""

    def on_activate(self) -> None:
        """Called when the plugin's route becomes active."""

    def on_deactivate(self) -> None:
        """Called when the plugin's route loses focus."""

    def on_dispose(self) -> None:
        """Called during shell shutdown/disposal."""


class LifecycleManager:
    """Manages lifecycle transitions for shell-registered plugins/pages."""

    def __init__(self) -> None:
        self._plugins: dict[str, PluginLifecycle] = {}
        self._active_route: RouteId | None = None

    def register_plugin(self, route_id: RouteId, lifecycle: PluginLifecycle) -> None:
        """Register a plugin lifecycle handler for a route."""

        route_key = str(route_id)
        if route_key in self._plugins:
            raise ValueError(f"Lifecycle for route '{route_key}' is already registered.")
        self._plugins[route_key] = lifecycle
        lifecycle.on_register()

    def activate(self, route_id: RouteId) -> None:
        """Activate a route lifecycle, deactivating the current one first."""

        route_key = str(route_id)
        lifecycle = self._plugins.get(route_key)
        if lifecycle is None:
            raise KeyError(f"Lifecycle for route '{route_key}' is not registered.")
        if self._active_route == route_id:
            return

        if self._active_route is not None:
            self.deactivate(self._active_route)

        lifecycle.on_activate()
        self._active_route = route_id

    def deactivate(self, route_id: RouteId) -> None:
        """Deactivate a route lifecycle if it is registered."""

        route_key = str(route_id)
        lifecycle = self._plugins.get(route_key)
        if lifecycle is None:
            raise KeyError(f"Lifecycle for route '{route_key}' is not registered.")

        lifecycle.on_deactivate()
        if self._active_route == route_id:
            self._active_route = None

    def dispose_all(self) -> None:
        """Dispose all registered plugins and reset manager state."""

        for lifecycle in self._plugins.values():
            lifecycle.on_dispose()
        self._plugins.clear()
        self._active_route = None

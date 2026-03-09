from __future__ import annotations

"""System page placeholder."""

from ....core.types import RouteId
from ..base_page import BasePage


class SystemPage(BasePage):
    """System-management route placeholder."""

    default_route_id: RouteId = RouteId("system_settings")
    default_display_name: str = "系统设置"
    default_icon_name: str = "settings"

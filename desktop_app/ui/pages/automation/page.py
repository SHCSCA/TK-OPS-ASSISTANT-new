from __future__ import annotations

"""Automation page placeholder."""

from ....core.types import RouteId
from ..base_page import BasePage


class AutomationPage(BasePage):
    """Automation route placeholder."""

    default_route_id: RouteId = RouteId("auto_like")
    default_display_name: str = "自动点赞"
    default_icon_name: str = "thumb_up"

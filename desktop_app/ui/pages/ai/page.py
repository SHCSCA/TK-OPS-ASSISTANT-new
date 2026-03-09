from __future__ import annotations

"""AI page placeholder."""

from ....core.types import RouteId
from ..base_page import BasePage


class AIPage(BasePage):
    """AI workflow route placeholder."""

    default_route_id: RouteId = RouteId("script_generation")
    default_display_name: str = "脚本生成"
    default_icon_name: str = "description"

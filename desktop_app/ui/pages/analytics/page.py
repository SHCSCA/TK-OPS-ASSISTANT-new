from __future__ import annotations

"""Analytics page placeholder."""

from ....core.types import RouteId
from ..base_page import BasePage


class AnalyticsPage(BasePage):
    """Analytics route placeholder."""

    default_route_id: RouteId = RouteId("traffic_dashboard")
    default_display_name: str = "流量看板"
    default_icon_name: str = "bar_chart"

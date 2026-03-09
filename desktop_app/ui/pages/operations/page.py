from __future__ import annotations

"""Operations page placeholder."""

from ....core.types import RouteId
from ..base_page import BasePage


class OperationsPage(BasePage):
    """Operations route placeholder."""

    default_route_id: RouteId = RouteId("operations_center")
    default_display_name: str = "运营中心"
    default_icon_name: str = "admin_panel_settings"

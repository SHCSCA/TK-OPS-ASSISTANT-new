from __future__ import annotations

"""Content page placeholder."""

from ....core.types import RouteId
from ..base_page import BasePage


class ContentPage(BasePage):
    """Content-workflow route placeholder."""

    default_route_id: RouteId = RouteId("material_center")
    default_display_name: str = "素材中心"
    default_icon_name: str = "movie_edit"

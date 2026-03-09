# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false

from __future__ import annotations

"""Analytics page package."""

from .blue_ocean_page import BlueOceanPage
from .competitor_page import CompetitorPage
from .engagement_page import EngagementPage
from .page import AnalyticsPage
from .profit_page import ProfitAnalysisPage
from .report_page import ReportGeneratorPage
from .visual_lab_page import VisualLabPage

__all__ = [
    "AnalyticsPage",
    "BlueOceanPage",
    "CompetitorPage",
    "EngagementPage",
    "ProfitAnalysisPage",
    "ReportGeneratorPage",
    "VisualLabPage",
]

from __future__ import annotations

"""Routable application pages for the new shell."""

from .account.page import AccountPage
from .ai.page import AIPage
from .analytics.page import AnalyticsPage
from .automation.page import AutomationPage
from .base_page import BasePage
from .content.page import ContentPage
from .crm.page import CRMPage
from .dashboard.page import DashboardPage
from .operations.page import OperationsPage
from .system.page import SystemPage

__all__ = [
    "AIPage",
    "AccountPage",
    "AnalyticsPage",
    "AutomationPage",
    "BasePage",
    "CRMPage",
    "ContentPage",
    "DashboardPage",
    "OperationsPage",
    "SystemPage",
]

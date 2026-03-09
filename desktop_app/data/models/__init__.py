from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false

"""应用数据层 ORM 模型导出。"""

from .ai_provider import AIModel, AIProvider, AgentRole
from .account import TikTokAccount
from .analytics import AnalyticsSnapshot, CompetitorProfile, Report
from .automation import AutoReplyRule, AutomationTask, CollectionTask
from .asset import Asset
from .base import Base, SoftDeleteMixin, TimestampMixin
from .content import ContentTemplate, Script
from .crm import Customer, CustomerInteraction
from .job import Job, Task
from .log import LogEntry
from .operations import CustomerInquiry, InquiryReply, Order
from .schedule import PublishSchedule
from .settings import AppSetting

__all__ = [
    "AIModel",
    "AIProvider",
    "AgentRole",
    "AnalyticsSnapshot",
    "AppSetting",
    "AutoReplyRule",
    "AutomationTask",
    "Asset",
    "Base",
    "CollectionTask",
    "CompetitorProfile",
    "ContentTemplate",
    "CustomerInquiry",
    "Customer",
    "CustomerInteraction",
    "InquiryReply",
    "Job",
    "LogEntry",
    "Order",
    "PublishSchedule",
    "Report",
    "Script",
    "SoftDeleteMixin",
    "Task",
    "TikTokAccount",
    "TimestampMixin",
]

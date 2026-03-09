from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportUnknownVariableType=false

"""数据仓储层导出。"""

from .ai_repo import AIRepository
from .account_repo import AccountRepository
from .analytics_repo import AnalyticsRepository
from .automation_repo import AutomationRepository
from .asset_repo import AssetRepository
from .base import BaseRepository, RepositoryProtocol
from .content_repo import ContentTemplateRepository, ScriptRepository
from .crm_repo import CRMRepository
from .job_repo import JobRepository
from .log_repo import LogRepository
from .operations_repo import OperationsRepository
from .schedule_repo import ScheduleRepository
from .settings_repo import SettingsRepository

__all__ = [
    "AIRepository",
    "AccountRepository",
    "AnalyticsRepository",
    "AutomationRepository",
    "AssetRepository",
    "BaseRepository",
    "ContentTemplateRepository",
    "CRMRepository",
    "JobRepository",
    "LogRepository",
    "OperationsRepository",
    "RepositoryProtocol",
    "ScheduleRepository",
    "ScriptRepository",
    "SettingsRepository",
]

from __future__ import annotations

"""System page package."""

from .ai_provider_page import AIProviderPage
from .downloader_page import DownloaderPage
from .lan_transfer_page import LANTransferPage
from .network_diagnostics_page import NetworkDiagnosticsPage
from .page import SystemPage
from .setup_wizard_page import SetupWizardPage
from .task_queue_page import TaskQueuePage
from .task_scheduler_page import TaskSchedulerPage

__all__ = [
    "AIProviderPage",
    "DownloaderPage",
    "LANTransferPage",
    "NetworkDiagnosticsPage",
    "SystemPage",
    "SetupWizardPage",
    "TaskQueuePage",
    "TaskSchedulerPage",
]

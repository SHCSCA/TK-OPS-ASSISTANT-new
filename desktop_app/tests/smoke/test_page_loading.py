from __future__ import annotations

# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUntypedFunctionDecorator=false, reportAttributeAccessIssue=false

from collections.abc import Sequence

import pytest

from ...app import TKOpsApp
from ...core.qt import QWidget
from ...core.types import RouteId
from ...ui.pages.account.page import AccountPage
from ...ui.pages.ai.content_factory_page import AIContentFactoryPage
from ...ui.pages.ai.copy_generation_page import CopyGenerationPage
from ...ui.pages.ai.creative_workshop_page import CreativeWorkshopPage
from ...ui.pages.ai.product_title_page import ProductTitlePage
from ...ui.pages.ai.script_generation_page import ScriptGenerationPage
from ...ui.pages.ai.script_extractor_page import ScriptExtractorPage
from ...ui.pages.ai.viral_title_page import ViralTitlePage
from ...ui.pages.analytics.audience_personas_page import AudiencePersonasPage
from ...ui.pages.analytics.blue_ocean_page import BlueOceanPage
from ...ui.pages.analytics.competitor_page import CompetitorPage
from ...ui.pages.analytics.ecommerce_conversion_page import EcommerceConversionPage
from ...ui.pages.analytics.engagement_page import EngagementPage
from ...ui.pages.analytics.profit_page import ProfitAnalysisPage
from ...ui.pages.analytics.report_center_page import ReportCenterPage
from ...ui.pages.analytics.report_page import ReportGeneratorPage
from ...ui.pages.analytics.traffic_dashboard_page import TrafficDashboardPage
from ...ui.pages.analytics.visual_lab_page import VisualLabPage
from ...ui.pages.automation.auto_comment_page import AutoCommentPage
from ...ui.pages.automation.auto_direct_message_page import AutoDirectMessagePage
from ...ui.pages.automation.auto_like_page import AutoLikePage
from ...ui.pages.automation.auto_reply_page import AutoReplyPage
from ...ui.pages.automation.data_collection_page import DataCollectionPage
from ...ui.pages.automation.scheduled_publish_page import ScheduledPublishPage
from ...ui.pages.content.material_center_page import MaterialCenterPage
from ...ui.pages.content.material_factory_page import MaterialFactoryPage
from ...ui.pages.content.task_hall_page import TaskHallPage
from ...ui.pages.content.video_editing_page import VideoEditingPage
from ...ui.pages.content.visual_editor_page import VisualEditorPage
from ...ui.pages.crm.page import CRMPage
from ...ui.pages.dashboard.page import DashboardPage
from ...ui.pages.operations.customer_service_page import CustomerServiceCenterPage
from ...ui.pages.operations.operations_center_page import OperationsCenterPage
from ...ui.pages.operations.order_management_page import OrderManagementPage
from ...ui.pages.operations.refund_processing_page import RefundProcessingPage
from ...ui.pages.system.ai_provider_page import AIProviderPage
from ...ui.pages.system.downloader_page import DownloaderPage
from ...ui.pages.system.lan_transfer_page import LANTransferPage
from ...ui.pages.system.network_diagnostics_page import NetworkDiagnosticsPage
from ...ui.pages.system.log_center_page import LogCenterPage
from ...ui.pages.system.permission_management_page import PermissionManagementPage
from ...ui.pages.system.setup_wizard_page import SetupWizardPage
from ...ui.pages.system.system_settings_page import SystemSettingsPage
from ...ui.pages.system.task_queue_page import TaskQueuePage
from ...ui.pages.system.task_scheduler_page import TaskSchedulerPage
from ...ui.pages.system.version_upgrade_page import VersionUpgradePage

pytestmark = pytest.mark.usefixtures("qapp")

ALL_REGISTERED_ROUTE_IDS: Sequence[str] = (
    "dashboard_home",
    "account_management",
    "group_management",
    "device_management",
    "operations_center",
    "order_management",
    "refund_processing",
    "customer_service_center",
    "crm_customer_management",
    "material_center",
    "material_factory",
    "video_editing",
    "visual_editor",
    "script_generation",
    "task_hall",
    "viral_title_studio",
    "script_extractor",
    "product_title_master",
    "creative_workshop",
    "ai_content_factory",
    "ai_copy_generation",
    "traffic_dashboard",
    "visual_lab",
    "competitor_monitoring",
    "profit_analysis",
    "blue_ocean_analysis",
    "report_generator",
    "engagement_analysis",
    "ecommerce_conversion",
    "audience_personas",
    "report_center",
    "auto_like",
    "auto_comment",
    "auto_direct_message",
    "scheduled_publishing",
    "auto_reply_console",
    "data_collection_assistant",
    "system_settings",
    "ai_provider_settings",
    "lan_transfer",
    "task_queue",
    "setup_wizard",
    "download_manager",
    "network_diagnostics",
    "task_scheduler",
    "permission_management",
    "log_center",
    "version_upgrade",
)


def _assert_widget(page: QWidget) -> None:
    assert isinstance(page, QWidget)


@pytest.fixture(scope="module")
def tkops_app() -> TKOpsApp:
    return TKOpsApp(argv=[])


@pytest.mark.smoke
def test_dashboard_page_instantiates() -> None:
    _assert_widget(DashboardPage())


@pytest.mark.smoke
def test_account_page_instantiates() -> None:
    _assert_widget(AccountPage())


@pytest.mark.smoke
def test_visual_lab_page_instantiates() -> None:
    _assert_widget(VisualLabPage())


@pytest.mark.smoke
def test_competitor_page_instantiates() -> None:
    _assert_widget(CompetitorPage())


@pytest.mark.smoke
def test_profit_analysis_page_instantiates() -> None:
    _assert_widget(ProfitAnalysisPage())


@pytest.mark.smoke
def test_report_generator_page_instantiates() -> None:
    _assert_widget(ReportGeneratorPage())


@pytest.mark.smoke
def test_engagement_page_instantiates() -> None:
    _assert_widget(EngagementPage())


@pytest.mark.smoke
def test_blue_ocean_page_instantiates() -> None:
    _assert_widget(BlueOceanPage())


@pytest.mark.smoke
def test_material_factory_page_instantiates() -> None:
    _assert_widget(MaterialFactoryPage())


@pytest.mark.smoke
def test_visual_editor_page_instantiates() -> None:
    _assert_widget(VisualEditorPage())


@pytest.mark.smoke
def test_data_collection_page_instantiates() -> None:
    _assert_widget(DataCollectionPage())


@pytest.mark.smoke
def test_scheduled_publish_page_instantiates() -> None:
    _assert_widget(ScheduledPublishPage())


@pytest.mark.smoke
def test_auto_reply_page_instantiates() -> None:
    _assert_widget(AutoReplyPage())


@pytest.mark.smoke
def test_lan_transfer_page_instantiates() -> None:
    _assert_widget(LANTransferPage())


@pytest.mark.smoke
def test_task_queue_page_instantiates() -> None:
    _assert_widget(TaskQueuePage())


@pytest.mark.smoke
def test_setup_wizard_page_instantiates() -> None:
    _assert_widget(SetupWizardPage())


@pytest.mark.smoke
def test_downloader_page_instantiates() -> None:
    _assert_widget(DownloaderPage())


@pytest.mark.smoke
def test_network_diagnostics_page_instantiates() -> None:
    _assert_widget(NetworkDiagnosticsPage())


@pytest.mark.smoke
def test_task_scheduler_page_instantiates() -> None:
    _assert_widget(TaskSchedulerPage())


@pytest.mark.smoke
def test_ai_provider_page_instantiates() -> None:
    _assert_widget(AIProviderPage())


@pytest.mark.smoke
def test_viral_title_page_instantiates() -> None:
    _assert_widget(ViralTitlePage())


@pytest.mark.smoke
def test_script_extractor_page_instantiates() -> None:
    _assert_widget(ScriptExtractorPage())


@pytest.mark.smoke
def test_product_title_page_instantiates() -> None:
    _assert_widget(ProductTitlePage())


@pytest.mark.smoke
def test_creative_workshop_page_instantiates() -> None:
    _assert_widget(CreativeWorkshopPage())


@pytest.mark.smoke
def test_ai_content_factory_page_instantiates() -> None:
    _assert_widget(AIContentFactoryPage())


@pytest.mark.smoke
def test_copy_generation_page_instantiates() -> None:
    _assert_widget(CopyGenerationPage())


@pytest.mark.smoke
def test_crm_page_instantiates() -> None:
    _assert_widget(CRMPage())


@pytest.mark.smoke
def test_operations_center_page_instantiates() -> None:
    _assert_widget(OperationsCenterPage())


@pytest.mark.smoke
def test_order_management_page_instantiates() -> None:
    _assert_widget(OrderManagementPage())


@pytest.mark.smoke
def test_refund_processing_page_instantiates() -> None:
    _assert_widget(RefundProcessingPage())


@pytest.mark.smoke
def test_customer_service_center_page_instantiates() -> None:
    _assert_widget(CustomerServiceCenterPage())


@pytest.mark.smoke
def test_traffic_dashboard_page_instantiates() -> None:
    _assert_widget(TrafficDashboardPage())


@pytest.mark.smoke
def test_ecommerce_conversion_page_instantiates() -> None:
    _assert_widget(EcommerceConversionPage())


@pytest.mark.smoke
def test_audience_personas_page_instantiates() -> None:
    _assert_widget(AudiencePersonasPage())


@pytest.mark.smoke
def test_report_center_page_instantiates() -> None:
    _assert_widget(ReportCenterPage())


@pytest.mark.smoke
def test_auto_like_page_instantiates() -> None:
    _assert_widget(AutoLikePage())


@pytest.mark.smoke
def test_auto_comment_page_instantiates() -> None:
    _assert_widget(AutoCommentPage())


@pytest.mark.smoke
def test_auto_direct_message_page_instantiates() -> None:
    _assert_widget(AutoDirectMessagePage())


@pytest.mark.smoke
def test_material_center_page_instantiates() -> None:
    _assert_widget(MaterialCenterPage())


@pytest.mark.smoke
def test_video_editing_page_instantiates() -> None:
    _assert_widget(VideoEditingPage())


@pytest.mark.smoke
def test_task_hall_page_instantiates() -> None:
    _assert_widget(TaskHallPage())


@pytest.mark.smoke
def test_system_settings_page_instantiates() -> None:
    _assert_widget(SystemSettingsPage())


@pytest.mark.smoke
def test_permission_management_page_instantiates() -> None:
    _assert_widget(PermissionManagementPage())


@pytest.mark.smoke
def test_log_center_page_instantiates() -> None:
    _assert_widget(LogCenterPage())


@pytest.mark.smoke
def test_version_upgrade_page_instantiates() -> None:
    _assert_widget(VersionUpgradePage())


@pytest.mark.smoke
def test_script_generation_page_instantiates() -> None:
    _assert_widget(ScriptGenerationPage())


@pytest.mark.smoke
@pytest.mark.parametrize("route_id", ALL_REGISTERED_ROUTE_IDS)
def test_registered_route_factories_instantiate_widgets(tkops_app: TKOpsApp, route_id: str) -> None:
    definition = tkops_app.route_registry.get(RouteId(route_id))

    assert definition is not None
    assert isinstance(tkops_app.route_registry.create_page(RouteId(route_id)), QWidget)

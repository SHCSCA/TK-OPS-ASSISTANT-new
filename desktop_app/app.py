from __future__ import annotations

# pyright: basic, reportAttributeAccessIssue=false

"""Application composition root for the TK-OPS desktop shell."""

from typing import Sequence

from .core.qt import QApplication
from .core.config.bus import ConfigBus
from .core.shell.navigation import build_default_navigation
from .core.shell.registry import RouteDefinition, RouteRegistry
from .core.theme.engine import ThemeEngine
from .data.database import Database
from .services.account.service import AccountService
from .services.ai.agent_service import AgentRoleService
from .services.ai.config_service import AIConfigService
from .services.ai.streaming import StreamingAIRuntime
from .services.analytics.service import AnalyticsService
from .services.automation.service import AutomationService
from .services.content.service import ContentService
from .services.operations.service import OperationsService


class ServiceRegistry:
    """Aggregates service instances owned by the composition root."""

    def __init__(
        self,
        account: AccountService,
        content: ContentService,
        analytics: AnalyticsService,
        automation: AutomationService,
        operations: OperationsService,
        ai_config: AIConfigService,
        ai_roles: AgentRoleService,
        ai_runtime: StreamingAIRuntime,
    ) -> None:
        self.account = account
        self.content = content
        self.analytics = analytics
        self.automation = automation
        self.operations = operations
        self.ai_config = ai_config
        self.ai_roles = ai_roles
        self.ai_runtime = ai_runtime


class TKOpsApp:
    """Composition root that wires the shell placeholder stack."""

    def __init__(self, argv: Sequence[str] | None = None) -> None:
        self._argv = list(argv or [])
        self.qt_app = self._create_qapplication()
        self.config_bus = ConfigBus()
        self.theme_engine = ThemeEngine(config_bus=self.config_bus)
        self.database = Database()
        self.services = self._create_services()
        self.route_registry = RouteRegistry()
        self.navigation_model = build_default_navigation()
        self._register_routes()
        self.main_window = self._create_main_window()

    def _create_qapplication(self):
        """Create or reuse the process-wide QApplication instance."""

        existing = QApplication.instance()
        if existing is not None:
            return existing
        return QApplication(self._argv)

    def _create_services(self) -> ServiceRegistry:
        """Instantiate foundational service stubs."""

        return ServiceRegistry(
            account=AccountService(self.database),
            content=ContentService(),
            analytics=AnalyticsService(self.database),
            automation=AutomationService(),
            operations=OperationsService(self.database),
            ai_config=AIConfigService(),
            ai_roles=AgentRoleService(),
            ai_runtime=StreamingAIRuntime(),
        )

    def _register_routes(self) -> None:
        """Register all hub and child routes with concrete page factories."""

        from .core.types import DomainGroup, RouteId

        # ── Wave 4 concrete page imports ──
        from .ui.pages.account.page import AccountPage
        from .ui.pages.analytics.competitor_page import CompetitorPage
        from .ui.pages.analytics.engagement_page import EngagementPage
        from .ui.pages.analytics.profit_page import ProfitAnalysisPage
        from .ui.pages.analytics.report_page import ReportGeneratorPage
        from .ui.pages.analytics.visual_lab_page import VisualLabPage
        from .ui.pages.automation.data_collection_page import DataCollectionPage
        from .ui.pages.automation.scheduled_publish_page import ScheduledPublishPage
        from .ui.pages.content.material_factory_page import MaterialFactoryPage
        from .ui.pages.crm.page import CRMPage
        from .ui.pages.dashboard.page import DashboardPage
        from .ui.pages.system.downloader_page import DownloaderPage
        from .ui.pages.system.lan_transfer_page import LANTransferPage
        from .ui.pages.system.network_diagnostics_page import NetworkDiagnosticsPage
        from .ui.pages.system.setup_wizard_page import SetupWizardPage
        from .ui.pages.system.task_queue_page import TaskQueuePage
        from .ui.pages.system.task_scheduler_page import TaskSchedulerPage

        # ── Wave 5 concrete page imports ──
        from .ui.pages.ai.content_factory_page import AIContentFactoryPage
        from .ui.pages.ai.copy_generation_page import CopyGenerationPage
        from .ui.pages.ai.creative_workshop_page import CreativeWorkshopPage
        from .ui.pages.ai.script_generation_page import ScriptGenerationPage
        from .ui.pages.ai.product_title_page import ProductTitlePage
        from .ui.pages.ai.script_extractor_page import ScriptExtractorPage
        from .ui.pages.ai.viral_title_page import ViralTitlePage
        from .ui.pages.analytics.audience_personas_page import AudiencePersonasPage
        from .ui.pages.analytics.blue_ocean_page import BlueOceanPage
        from .ui.pages.analytics.ecommerce_conversion_page import EcommerceConversionPage
        from .ui.pages.automation.auto_reply_page import AutoReplyPage
        from .ui.pages.analytics.report_center_page import ReportCenterPage
        from .ui.pages.analytics.traffic_dashboard_page import TrafficDashboardPage
        from .ui.pages.automation.auto_comment_page import AutoCommentPage
        from .ui.pages.automation.auto_direct_message_page import AutoDirectMessagePage
        from .ui.pages.automation.auto_like_page import AutoLikePage
        from .ui.pages.content.material_center_page import MaterialCenterPage
        from .ui.pages.content.task_hall_page import TaskHallPage
        from .ui.pages.content.video_editing_page import VideoEditingPage
        from .ui.pages.operations.customer_service_page import CustomerServiceCenterPage
        from .ui.pages.operations.operations_center_page import OperationsCenterPage
        from .ui.pages.operations.order_management_page import OrderManagementPage
        from .ui.pages.operations.refund_processing_page import RefundProcessingPage
        from .ui.pages.content.visual_editor_page import VisualEditorPage
        from .ui.pages.system.ai_provider_page import AIProviderPage
        from .ui.pages.system.log_center_page import LogCenterPage
        from .ui.pages.system.permission_management_page import PermissionManagementPage
        from .ui.pages.system.system_settings_page import SystemSettingsPage
        from .ui.pages.system.version_upgrade_page import VersionUpgradePage

        specs = [
            # ── Main ──
            ("dashboard_home", "概览数据看板", "dashboard", DomainGroup.DASHBOARD, lambda: DashboardPage()),
            ("account_management", "账号管理", "manage_accounts", DomainGroup.ACCOUNT, lambda: AccountPage()),
            ("group_management", "分组管理", "group_work", DomainGroup.ACCOUNT, lambda: AccountPage(RouteId("group_management"), "分组管理", "group_work")),
            ("device_management", "设备管理", "devices", DomainGroup.ACCOUNT, lambda: AccountPage(RouteId("device_management"), "设备管理", "devices")),
            # ── 运营经理专区 ──
            ("operations_center", "运营中心", "admin_panel_settings", DomainGroup.OPERATIONS, lambda: OperationsCenterPage()),

            ("order_management", "订单管理", "receipt_long", DomainGroup.OPERATIONS, lambda: OrderManagementPage()),
            ("refund_processing", "退款处理", "undo", DomainGroup.OPERATIONS, lambda: RefundProcessingPage()),
            ("customer_service_center", "客服中心", "support_agent", DomainGroup.OPERATIONS, lambda: CustomerServiceCenterPage()),
            ("crm_customer_management", "CRM客户关系管理", "hub", DomainGroup.CRM, lambda: CRMPage()),
            # ── 内容创作者专区 ──
            ("material_center", "素材中心", "movie_edit", DomainGroup.CONTENT, lambda: MaterialCenterPage()),
            ("material_factory", "素材工厂", "factory", DomainGroup.CONTENT, lambda: MaterialFactoryPage()),
            ("video_editing", "视频剪辑", "content_cut", DomainGroup.CONTENT, lambda: VideoEditingPage()),
            ("visual_editor", "视觉编辑器", "movie_edit", DomainGroup.CONTENT, lambda: VisualEditorPage()),
            ("script_generation", "脚本生成", "description", DomainGroup.AI, lambda: ScriptGenerationPage()),
            ("task_hall", "任务大厅", "assignment", DomainGroup.CONTENT, lambda: TaskHallPage()),
            # ── AI 专区 (Wave 5 — concrete pages) ──
            ("viral_title_studio", "爆款标题", "auto_awesome", DomainGroup.AI, lambda: ViralTitlePage()),
            ("script_extractor", "脚本提取工具", "movie_edit", DomainGroup.AI, lambda: ScriptExtractorPage()),

            ("product_title_master", "商品标题大师", "auto_fix_high", DomainGroup.AI, lambda: ProductTitlePage()),
            ("creative_workshop", "创意工坊", "rocket_launch", DomainGroup.AI, lambda: CreativeWorkshopPage()),
            ("ai_content_factory", "AI内容工厂", "factory", DomainGroup.AI, lambda: AIContentFactoryPage()),
            ("ai_copy_generation", "AI文案生成", "edit_note", DomainGroup.AI, lambda: CopyGenerationPage()),
            # ── 数据分析师专区 ──
            ("traffic_dashboard", "流量看板", "bar_chart", DomainGroup.ANALYTICS, lambda: TrafficDashboardPage()),
            ("visual_lab", "可视化实验室", "query_stats", DomainGroup.ANALYTICS, lambda: VisualLabPage()),
            ("competitor_monitoring", "竞争对手监控", "monitoring", DomainGroup.ANALYTICS, lambda: CompetitorPage()),
            ("profit_analysis", "利润分析系统", "analytics", DomainGroup.ANALYTICS, lambda: ProfitAnalysisPage()),
            ("blue_ocean_analysis", "蓝海分析", "explore", DomainGroup.ANALYTICS, lambda: BlueOceanPage()),
            ("report_generator", "数据报告生成器", "description", DomainGroup.ANALYTICS, lambda: ReportGeneratorPage()),
            ("engagement_analysis", "互动分析", "bar_chart", DomainGroup.ANALYTICS, lambda: EngagementPage()),
            ("ecommerce_conversion", "电商转化", "shopping_bag", DomainGroup.ANALYTICS, lambda: EcommerceConversionPage()),
            ("audience_personas", "粉丝画像", "face", DomainGroup.ANALYTICS, lambda: AudiencePersonasPage()),
            ("report_center", "报表中心", "pie_chart", DomainGroup.ANALYTICS, lambda: ReportCenterPage()),
            # ── 自动化运营专区 ──
            ("auto_like", "自动点赞", "thumb_up", DomainGroup.AUTOMATION, lambda: AutoLikePage()),
            ("auto_comment", "自动评论", "comment", DomainGroup.AUTOMATION, lambda: AutoCommentPage()),
            ("auto_direct_message", "自动私信", "mail", DomainGroup.AUTOMATION, lambda: AutoDirectMessagePage()),
            ("scheduled_publishing", "定时发布", "schedule", DomainGroup.AUTOMATION, lambda: ScheduledPublishPage()),
            ("auto_reply_console", "自动回复控制台", "robot_2", DomainGroup.AUTOMATION, lambda: AutoReplyPage()),
            ("data_collection_assistant", "数据采集助手", "analytics", DomainGroup.AUTOMATION, lambda: DataCollectionPage()),
            # ── 系统 ──
            ("system_settings", "系统设置", "settings", DomainGroup.SYSTEM, lambda: SystemSettingsPage()),
            ("ai_provider_settings", "AI供应商配置", "settings", DomainGroup.SYSTEM, lambda: AIProviderPage()),
            ("lan_transfer", "局域网传输", "leak_add", DomainGroup.SYSTEM, lambda: LANTransferPage()),
            ("task_queue", "任务队列", "account_tree", DomainGroup.SYSTEM, lambda: TaskQueuePage()),
            ("setup_wizard", "配置向导", "bolt", DomainGroup.SYSTEM, lambda: SetupWizardPage()),
            ("download_manager", "下载器", "download", DomainGroup.SYSTEM, lambda: DownloaderPage()),
            ("network_diagnostics", "网络诊断", "terminal", DomainGroup.SYSTEM, lambda: NetworkDiagnosticsPage()),
            ("task_scheduler", "任务调度", "schedule", DomainGroup.SYSTEM, lambda: TaskSchedulerPage()),
            ("permission_management", "权限管理", "lock_person", DomainGroup.SYSTEM, lambda: PermissionManagementPage()),
            ("log_center", "日志中心", "history", DomainGroup.SYSTEM, lambda: LogCenterPage()),
            ("version_upgrade", "版本升级", "upgrade", DomainGroup.SYSTEM, lambda: VersionUpgradePage()),
        ]

        for route_id, display_name, icon_name, domain_group, page_factory in specs:
            self.route_registry.register(RouteDefinition(RouteId(route_id), display_name, icon_name, domain_group, page_factory))

    def _create_main_window(self):
        """Instantiate the shell window after core wiring is available."""

        from .ui.shell.main_window import MainWindow

        return MainWindow(route_registry=self.route_registry, navigation_model=self.navigation_model, theme_engine=self.theme_engine, config_bus=self.config_bus)

    def run(self) -> int:
        """Show the shell window and enter the Qt event loop."""

        self.main_window.show()
        return self.qt_app.exec()


def main(argv: Sequence[str] | None = None) -> int:
    """Launch the desktop shell composition root."""

    return TKOpsApp(argv=argv).run()

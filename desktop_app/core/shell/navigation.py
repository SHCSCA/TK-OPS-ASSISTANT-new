from __future__ import annotations

# pyright: basic

"""Hierarchical navigation metadata and observable state for the shell sidebar."""

from ..qt import QObject, Signal
from ..types import RouteId


class NavItem:
    """Single sidebar item that may expose child utility routes."""

    def __init__(
        self,
        route_id: RouteId,
        label: str,
        icon: str,
        badge_text: str = "",
        badge_color: str = "",
        children: list[NavItem] | None = None,
    ) -> None:
        self.route_id = route_id
        self.label = label
        self.icon = icon
        self.badge_text = badge_text
        self.badge_color = badge_color
        self.children = list(children or [])

    @property
    def display_name(self) -> str:
        """Compatibility alias used by shell widgets."""

        return self.label

    @property
    def icon_name(self) -> str:
        """Compatibility alias used by shell widgets."""

        return self.icon


class NavGroup:
    """Sidebar section grouping primary shell items."""

    def __init__(self, title: str, color: str, items: list[NavItem], is_expanded: bool = True) -> None:
        self.title = title
        self.color = color
        self.items = items
        self.is_expanded = is_expanded


NavigationItem = NavItem
NavigationSection = NavGroup


class NavigationModel(QObject):
    """Observable navigation state for sidebar binding."""

    current_changed = Signal(str)

    def __init__(self, groups: list[NavGroup] | None = None, parent: object | None = None) -> None:
        super().__init__(parent)
        self._groups = list(groups or [])
        self._route_map = self._build_route_map(self._groups)
        self._current_route: RouteId | None = None
        self._history: list[RouteId] = []
        self._history_index = -1

    @property
    def groups(self) -> list[NavGroup]:
        """Return navigation groups."""

        return self._groups

    @property
    def sections(self) -> list[NavGroup]:
        """Compatibility alias for shell consumers."""

        return self._groups

    @property
    def current_route(self) -> RouteId | None:
        """Return the current active route."""

        return self._current_route

    def navigate_to(self, route_id: RouteId) -> None:
        """Navigate to a route and append it to history."""

        self._set_current_route(route_id, add_to_history=True)

    def go_back(self) -> None:
        """Navigate back within the local route history."""

        if self._history_index <= 0:
            return
        self._history_index -= 1
        self._set_current_route(self._history[self._history_index], add_to_history=False)

    def history(self) -> list[RouteId]:
        """Return a copy of the route history."""

        return list(self._history)

    def has_route(self, route_id: RouteId) -> bool:
        """Return whether the route exists in the navigation tree."""

        return str(route_id) in self._route_map

    def item_for_route(self, route_id: RouteId) -> NavItem | None:
        """Return the navigation item for a route if present."""

        return self._route_map.get(str(route_id))

    def _set_current_route(self, route_id: RouteId, add_to_history: bool) -> None:
        route_key = str(route_id)
        if route_key not in self._route_map:
            raise ValueError(f"Route '{route_key}' is not present in the navigation model.")
        if self._current_route == route_id:
            return
        if add_to_history:
            if self._history_index < len(self._history) - 1:
                self._history = self._history[: self._history_index + 1]
            self._history.append(route_id)
            self._history_index = len(self._history) - 1
        self._current_route = route_id
        self.current_changed.emit(route_key)

    @staticmethod
    def _build_route_map(groups: list[NavGroup]) -> dict[str, NavItem]:
        route_map: dict[str, NavItem] = {}

        def visit(item: NavItem) -> None:
            route_map[str(item.route_id)] = item
            for child in item.children:
                visit(child)

        for group in groups:
            for item in group.items:
                visit(item)
        return route_map


def build_default_navigation() -> NavigationModel:
    """Build the complete sidebar navigation from PLN-01/PLN-02."""

    return NavigationModel([
        NavGroup("Main", "default", [
            NavItem(RouteId("dashboard_home"), "概览数据看板", "dashboard"),
            NavItem(RouteId("account_management"), "账号管理", "manage_accounts"),
            NavItem(RouteId("group_management"), "分组管理", "group_work"),
            NavItem(RouteId("device_management"), "设备管理", "devices"),
        ]),
        NavGroup("运营经理专区", "#FF6B6B", [
            NavItem(RouteId("operations_center"), "运营中心", "admin_panel_settings", children=[NavItem(RouteId("crm_customer_management"), "CRM客户关系管理", "hub")]),
            NavItem(RouteId("order_management"), "订单管理", "receipt_long"),
            NavItem(RouteId("refund_processing"), "退款处理", "undo"),
            NavItem(RouteId("customer_service_center"), "客服中心", "support_agent"),
        ]),
        NavGroup("内容创作者专区", "#4ECDC4", [
            NavItem(RouteId("material_center"), "素材中心", "movie_edit", children=[NavItem(RouteId("material_factory"), "素材工厂", "factory")]),
            NavItem(RouteId("video_editing"), "视频剪辑", "content_cut", children=[NavItem(RouteId("visual_editor"), "视觉编辑器", "movie_edit")]),
            NavItem(RouteId("script_generation"), "脚本生成", "description", children=[
                NavItem(RouteId("viral_title_studio"), "爆款标题", "auto_awesome"),
                NavItem(RouteId("script_extractor"), "脚本提取工具", "movie_edit"),
                NavItem(RouteId("product_title_master"), "商品标题大师", "auto_fix_high"),
                NavItem(RouteId("creative_workshop"), "创意工坊", "rocket_launch"),
                NavItem(RouteId("ai_content_factory"), "AI内容工厂", "factory"),
                NavItem(RouteId("ai_copy_generation"), "AI文案生成", "edit_note"),
            ]),
            NavItem(RouteId("task_hall"), "任务大厅", "assignment"),
        ]),
        NavGroup("数据分析师专区", "#95E1D3", [
            NavItem(RouteId("traffic_dashboard"), "流量看板", "bar_chart", children=[
                NavItem(RouteId("visual_lab"), "可视化实验室", "query_stats"),
                NavItem(RouteId("competitor_monitoring"), "竞争对手监控", "monitoring"),
                NavItem(RouteId("blue_ocean_analysis"), "蓝海分析", "explore"),
                NavItem(RouteId("engagement_analysis"), "互动分析", "bar_chart"),
            ]),
            NavItem(RouteId("ecommerce_conversion"), "电商转化", "shopping_bag", children=[NavItem(RouteId("profit_analysis"), "利润分析系统", "analytics")]),
            NavItem(RouteId("audience_personas"), "粉丝画像", "face"),
            NavItem(RouteId("report_center"), "报表中心", "pie_chart", children=[NavItem(RouteId("report_generator"), "数据报告生成器", "description")]),
        ]),
        NavGroup("自动化运营专区", "#F38181", [
            NavItem(RouteId("auto_like"), "自动点赞", "thumb_up"),
            NavItem(RouteId("auto_comment"), "自动评论", "comment"),
            NavItem(RouteId("auto_direct_message"), "自动私信", "mail"),
            NavItem(RouteId("scheduled_publishing"), "定时发布", "schedule", children=[
                NavItem(RouteId("auto_reply_console"), "自动回复控制台", "robot_2"),
                NavItem(RouteId("data_collection_assistant"), "数据采集助手", "analytics"),
            ]),
        ]),
        NavGroup("System", "default", [
            NavItem(RouteId("system_settings"), "系统设置", "settings", children=[
                NavItem(RouteId("setup_wizard"), "Setup Wizard", "bolt"),
                NavItem(RouteId("ai_provider_settings"), "AI供应商配置", "settings"),
            ]),
            NavItem(RouteId("permission_management"), "权限管理", "lock_person"),
            NavItem(RouteId("log_center"), "日志中心", "history", children=[
                NavItem(RouteId("task_queue"), "任务队列", "account_tree"),
                NavItem(RouteId("network_diagnostics"), "网络诊断", "terminal"),
                NavItem(RouteId("task_scheduler"), "任务调度", "schedule"),
            ]),
            NavItem(RouteId("version_upgrade"), "版本升级", "upgrade", children=[
                NavItem(RouteId("lan_transfer"), "局域网传输", "leak_add"),
                NavItem(RouteId("download_manager"), "下载器", "download"),
            ]),
        ]),
    ])

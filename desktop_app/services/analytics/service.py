from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false

"""分析服务实现，提供 TikTok Shop 运营分析能力。"""

from dataclasses import dataclass, fields, is_dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, cast
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from desktop_app.data.database import Database
from desktop_app.data.models.account import TikTokAccount
from desktop_app.data.models.analytics import AnalyticsSnapshot, CompetitorProfile as CompetitorProfileModel, Report as ReportModel
from desktop_app.data.models.operations import Order
from desktop_app.data.repositories.analytics_repo import AnalyticsRepository


@dataclass
class DateWindow:
    """统一表示分析查询时间窗口。"""

    start_at: datetime
    end_at: datetime


@dataclass
class TrafficSourceShare:
    """表示单一流量来源贡献。"""

    source: str
    views: int
    unique_visitors: int
    share: float


@dataclass
class KPIDashboard:
    """仪表盘 KPI 汇总。"""

    total_revenue: float
    total_orders: int
    average_order_value: float
    conversion_rate: float
    follower_count: int
    total_views: int
    unique_visitors: int
    ctr: float
    cvr: float
    retention_rate: float
    engagement_rate: float
    gpm: float
    roas: float
    date_range: dict[str, str]


@dataclass
class TrafficData:
    """流量分析数据。"""

    total_views: int
    unique_visitors: int
    impressions: int
    clicks: int
    ctr: float
    gpm: float
    roas: float
    traffic_sources: list[TrafficSourceShare]
    date_range: dict[str, str]


@dataclass
class FunnelStage:
    """转化漏斗阶段指标。"""

    stage: str
    count: int
    conversion_rate: float
    drop_off_rate: float


@dataclass
class ConversionFunnel:
    """转化漏斗分析结果。"""

    stages: list[FunnelStage]
    overall_cvr: float
    date_range: dict[str, str]


@dataclass
class CompetitorProfile:
    """竞品监控列表项。"""

    competitor_id: str
    shop_name: str
    display_name: str
    category: str
    region: str | None
    follower_count: int
    avg_views: int
    avg_price: float
    est_monthly_sales: float
    engagement_rate: float
    ctr: float
    cvr: float
    roas: float
    status: str


@dataclass
class CompetitorAnalysis:
    """竞品对标分析结果。"""

    competitor: CompetitorProfile
    benchmark_shop_name: str
    follower_gap: int
    revenue_gap: float
    price_index: float
    engagement_gap: float
    strengths: list[str]
    risks: list[str]
    opportunities: list[str]


@dataclass
class ProfitBreakdown:
    """利润拆解结果。"""

    product_id: str
    revenue: float
    cogs: float
    shipping_cost: float
    platform_fees: float
    ad_spend: float
    refund_loss: float
    net_profit: float
    gross_margin: float
    net_margin: float
    roas: float
    date_range: dict[str, str]


@dataclass
class AudiencePersona:
    """受众画像摘要。"""

    name: str
    age_range: str
    gender: str
    location: str
    interests: list[str]
    share: float
    pain_points: list[str]


@dataclass
class EngagementMetrics:
    """互动指标汇总。"""

    likes: int
    comments: int
    shares: int
    total_views: int
    average_engagement_rate: float
    retention_rate: float
    date_range: dict[str, str]


@dataclass
class BlueOceanOpportunity:
    """蓝海机会建议。"""

    category: str
    demand_index: float
    competition_index: float
    opportunity_score: float
    rationale: str
    recommended_products: list[str]


@dataclass
class ReportRecord:
    """分析报告记录。"""

    report_id: str
    report_type: str
    title: str
    status: str
    parameters: dict[str, Any]
    payload: dict[str, Any]
    export_format: str | None
    export_path: str | None
    generated_at: str
    summary: str | None


@dataclass
class ReportExportResult:
    """报告导出结果。"""

    report_id: str
    export_format: str
    file_path: str
    exported_at: str


CompetitorMonitor = CompetitorProfile


class AnalyticsService:
    """面向运营分析场景的真实领域服务。"""

    service_name: str = "analytics"

    def __init__(self, database: Database) -> None:
        """注入数据库依赖并初始化仓储。"""

        self._database = database
        self._analytics_repo = AnalyticsRepository(database.create_session)
        self._initialized = False
        self._started_at: datetime | None = None

    def initialize(self) -> None:
        """初始化分析服务并确保分析表结构可用。"""

        self._database.create_all()
        self._started_at = datetime.now(timezone.utc)
        self._initialized = True
        with self._database.session_scope() as session:
            self._analytics_repo.count_competitors(session)

    def shutdown(self) -> None:
        """关闭分析服务状态。"""

        self._initialized = False

    def healthcheck(self) -> dict[str, object]:
        """返回分析服务健康状态。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            return {
                "service": self.service_name,
                "status": "healthy",
                "initialized": self._initialized,
                "database": "ok",
                "started_at": self._started_at.isoformat() if self._started_at is not None else None,
                "competitors": self._analytics_repo.count_competitors(session),
                "reports": self._analytics_repo.count_reports(session),
                "snapshots": self._analytics_repo.count_snapshots(session),
            }

    def get_dashboard_kpis(self) -> KPIDashboard:
        """获取首页仪表盘 KPI 汇总。"""

        self._ensure_initialized()
        window = self._resolve_date_range(None)
        with self._database.session_scope() as session:
            return self._build_dashboard_kpis(session, window)

    def get_dashboard_metrics(self) -> dict[str, object]:
        """兼容旧接口，返回字典形式的仪表盘数据。"""

        return cast(dict[str, object], self._to_jsonable(self.get_dashboard_kpis()))

    def get_traffic_data(self, date_range: object = None) -> TrafficData:
        """获取指定时间窗口的流量分析。"""

        self._ensure_initialized()
        window = self._resolve_date_range(date_range)
        with self._database.session_scope() as session:
            return self._build_traffic_data(session, window)

    def get_conversion_funnel(self, date_range: object = None) -> ConversionFunnel:
        """获取转化漏斗分析。"""

        self._ensure_initialized()
        window = self._resolve_date_range(date_range)
        with self._database.session_scope() as session:
            return self._build_conversion_funnel(session, window)

    def get_competitor_list(self) -> list[CompetitorProfile]:
        """获取竞品监控列表。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            competitors = self._analytics_repo.list_competitors(session, active_only=True)
            if competitors:
                return [self._to_competitor_monitor(item) for item in competitors]
            return self._demo_competitors()

    def add_competitor(self, competitor_data: Mapping[str, object]) -> CompetitorProfile:
        """新增竞品监控对象。"""

        self._ensure_initialized()
        payload = dict(competitor_data)
        shop_name = str(payload.get("shop_name") or payload.get("display_name") or "未命名竞品")
        display_name = str(payload.get("display_name") or shop_name)
        competitor_id = str(payload.get("competitor_id") or self._build_business_id("comp"))
        with self._database.session_scope() as session:
            existing = self._analytics_repo.get_competitor_by_competitor_id(session, competitor_id)
            if existing is not None:
                raise ValueError(f"竞品编号已存在: {competitor_id}")
            competitor = self._analytics_repo.create_competitor(
                session,
                competitor_id=competitor_id,
                shop_name=shop_name,
                display_name=display_name,
                platform_username=self._as_optional_str(payload.get("platform_username")),
                category=str(payload.get("category") or "general"),
                region=self._as_optional_str(payload.get("region")),
                follower_count=self._to_int(payload.get("follower_count"), 0),
                avg_views=self._to_int(payload.get("avg_views"), 0),
                avg_likes=self._to_int(payload.get("avg_likes"), 0),
                avg_price=self._to_float(payload.get("avg_price"), 0.0),
                est_monthly_sales=self._to_float(payload.get("est_monthly_sales"), 0.0),
                engagement_rate=self._to_float(payload.get("engagement_rate"), 0.0),
                ctr=self._to_float(payload.get("ctr"), 0.0),
                cvr=self._to_float(payload.get("cvr"), 0.0),
                roas=self._to_float(payload.get("roas"), 0.0),
                status=str(payload.get("status") or "active"),
                metadata_json=self._normalize_mapping(payload.get("metadata")),
            )
            return self._to_competitor_monitor(competitor)

    def get_competitor_analysis(self, competitor_id: str) -> CompetitorAnalysis:
        """获取指定竞品的对标分析。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            competitor = self._analytics_repo.get_competitor_by_competitor_id(session, competitor_id)
            if competitor is None:
                demo = {item.competitor_id: item for item in self._demo_competitors()}
                selected = demo.get(competitor_id)
                if selected is None:
                    raise ValueError(f"未找到竞品: {competitor_id}")
                return self._build_competitor_analysis_from_monitor(session, selected)
            return self._build_competitor_analysis_from_monitor(session, self._to_competitor_monitor(competitor))

    def get_profit_analysis(self, product_id: str, date_range: object = None) -> ProfitBreakdown:
        """获取商品利润拆解。"""

        self._ensure_initialized()
        window = self._resolve_date_range(date_range)
        with self._database.session_scope() as session:
            return self._build_profit_analysis(session, product_id, window)

    def get_audience_personas(self) -> list[AudiencePersona]:
        """获取受众画像。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            snapshots = self._analytics_repo.list_snapshots(session, snapshot_type="audience", limit=50)
            personas = self._extract_personas_from_snapshots(snapshots)
            if personas:
                return personas
            return self._demo_personas()

    def get_engagement_metrics(self, date_range: object = None) -> EngagementMetrics:
        """获取互动指标分析。"""

        self._ensure_initialized()
        window = self._resolve_date_range(date_range)
        with self._database.session_scope() as session:
            return self._build_engagement_metrics(session, window)

    def get_blue_ocean_opportunities(self) -> list[BlueOceanOpportunity]:
        """获取蓝海机会类目列表。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            return self._build_blue_ocean_opportunities(session)

    def generate_report(self, report_type: str, params: Mapping[str, object] | None = None) -> ReportRecord:
        """生成报告记录并保存计算结果。"""

        self._ensure_initialized()
        normalized_type = report_type.strip().lower()
        parameters = dict(params or {})
        window = self._resolve_date_range(parameters.get("date_range"))
        with self._database.session_scope() as session:
            payload = self._build_report_payload(session, normalized_type, parameters, window)
            report_id = str(parameters.get("report_id") or self._build_business_id("report"))
            title = str(parameters.get("title") or self._default_report_title(normalized_type, window))
            report = self._analytics_repo.create_report(
                session,
                report_id=report_id,
                report_type=normalized_type,
                title=title,
                status="generated",
                parameters_json=self._to_jsonable(parameters),
                payload_json=self._to_jsonable(payload),
                summary=self._build_report_summary(normalized_type, payload),
                generated_at=datetime.now(timezone.utc),
            )
            return self._to_report_record(report)

    def build_report(self, report_id: str) -> dict[str, object]:
        """兼容旧接口，按报告编号读取已生成报告。"""

        self._ensure_initialized()
        with self._database.session_scope() as session:
            report = self._analytics_repo.get_report_by_report_id(session, report_id)
            if report is None:
                raise ValueError(f"未找到报告: {report_id}")
            return cast(dict[str, object], self._to_jsonable(self._to_report_record(report)))

    def export_report(self, report_id: str, format: str) -> ReportExportResult:
        """导出报告并返回占位文件路径。"""

        self._ensure_initialized()
        normalized_format = format.strip().lower() or "json"
        extension = {"xlsx": "xlsx", "csv": "csv", "pdf": "pdf", "json": "json"}.get(normalized_format, "json")
        with self._database.session_scope() as session:
            report = self._analytics_repo.get_report_by_report_id(session, report_id)
            if report is None:
                raise ValueError(f"未找到报告: {report_id}")
            file_path = str(Path("exports") / f"{report.report_type}_{report.report_id}.{extension}")
            updated = self._analytics_repo.update_report(
                session,
                report_id,
                export_format=extension,
                export_path=file_path,
                status="exported",
            )
            if updated is None:
                raise ValueError(f"报告更新失败: {report_id}")
            exported_at = datetime.now(timezone.utc).isoformat()
            return ReportExportResult(
                report_id=report.report_id,
                export_format=extension,
                file_path=file_path,
                exported_at=exported_at,
            )

    def _build_dashboard_kpis(self, session: Session, window: DateWindow) -> KPIDashboard:
        """基于真实数据与占位逻辑构建仪表盘 KPI。"""

        accounts = self._load_accounts(session)
        orders = self._load_orders(session, window)
        live_sessions = self._load_live_sessions(session, window)
        traffic = self._load_snapshots(session, "traffic", window)
        engagement = self._load_snapshots(session, "engagement", window)
        if not accounts and not orders and not live_sessions and not traffic and not engagement:
            return self._demo_dashboard(window)

        total_revenue = round(sum(self._order_revenue(order) for order in orders), 2)
        total_orders = len(orders)
        follower_count = sum(int(getattr(account, "follower_count", 0) or 0) for account in accounts)
        total_views = self._sum_metric(traffic, "views")
        if total_views == 0:
            total_views = sum(int(getattr(item, "viewer_count", 0) or 0) for item in live_sessions)
        total_views = max(total_views, total_orders * 42, follower_count // 3)
        unique_visitors = self._sum_metric(traffic, "unique_visitors")
        if unique_visitors == 0:
            unique_visitors = max(int(total_views * 0.62), total_orders * 5)
        clicks = self._sum_metric(traffic, "clicks")
        if clicks == 0:
            clicks = max(int(total_views * 0.038), total_orders * 6)
        impressions = self._sum_metric(traffic, "impressions")
        if impressions == 0:
            impressions = max(int(total_views * 1.18), clicks * 7)
        ctr = self._safe_ratio(clicks, impressions)
        cvr = self._safe_ratio(total_orders, clicks)
        conversion_rate = self._average_account_metric(accounts, "conversion_rate", fallback=cvr)
        retention_rate = self._metric_average(engagement, "retention_rate", fallback=0.31)
        total_interactions = self._sum_metric(engagement, "likes") + self._sum_metric(engagement, "comments") + self._sum_metric(engagement, "shares")
        if total_interactions == 0:
            total_interactions = sum(
                int(getattr(item, "like_count", 0) or 0) + int(getattr(item, "comment_count", 0) or 0) + int((getattr(item, "comment_count", 0) or 0) * 0.8)
                for item in live_sessions
            )
        engagement_rate = self._safe_ratio(total_interactions, total_views)
        ad_spend = self._sum_metric(traffic, "ad_spend")
        if ad_spend == 0:
            ad_spend = round(max(total_revenue * 0.18, total_orders * 4.6, 1.0), 2)
        average_order_value = round(self._safe_ratio(total_revenue, total_orders), 2)
        gpm = round(self._safe_ratio(total_revenue, max(total_views / 1000, 1e-9)), 2)
        roas = round(self._safe_ratio(total_revenue, ad_spend), 4)
        return KPIDashboard(
            total_revenue=total_revenue,
            total_orders=total_orders,
            average_order_value=average_order_value,
            conversion_rate=round(conversion_rate, 4),
            follower_count=follower_count,
            total_views=total_views,
            unique_visitors=unique_visitors,
            ctr=round(ctr, 4),
            cvr=round(cvr, 4),
            retention_rate=round(retention_rate, 4),
            engagement_rate=round(engagement_rate, 4),
            gpm=gpm,
            roas=roas,
            date_range=self._window_dict(window),
        )

    def _build_traffic_data(self, session: Session, window: DateWindow) -> TrafficData:
        """构建流量分析结果。"""

        traffic = self._load_snapshots(session, "traffic", window)
        orders = self._load_orders(session, window)
        live_sessions = self._load_live_sessions(session, window)
        if not traffic and not orders and not live_sessions:
            return self._demo_traffic(window)

        total_views = self._sum_metric(traffic, "views")
        if total_views == 0:
            total_views = max(sum(int(getattr(item, "viewer_count", 0) or 0) for item in live_sessions), len(orders) * 40)
        unique_visitors = self._sum_metric(traffic, "unique_visitors") or max(int(total_views * 0.61), len(orders) * 4)
        impressions = self._sum_metric(traffic, "impressions") or max(int(total_views * 1.22), 1)
        clicks = self._sum_metric(traffic, "clicks") or max(int(total_views * 0.037), len(orders) * 5)
        ad_spend = self._sum_metric(traffic, "ad_spend") or max(sum(self._order_revenue(item) for item in orders) * 0.16, 1.0)
        revenue = round(sum(self._order_revenue(item) for item in orders), 2)
        ctr = round(self._safe_ratio(clicks, impressions), 4)
        gpm = round(self._safe_ratio(revenue, max(total_views / 1000, 1e-9)), 2)
        roas = round(self._safe_ratio(revenue, ad_spend), 4)
        sources = self._extract_traffic_sources(traffic, total_views, unique_visitors)
        return TrafficData(
            total_views=total_views,
            unique_visitors=unique_visitors,
            impressions=impressions,
            clicks=clicks,
            ctr=ctr,
            gpm=gpm,
            roas=roas,
            traffic_sources=sources,
            date_range=self._window_dict(window),
        )

    def _build_conversion_funnel(self, session: Session, window: DateWindow) -> ConversionFunnel:
        """构建转化漏斗结果。"""

        traffic = self._load_snapshots(session, "traffic", window)
        funnel = self._load_snapshots(session, "funnel", window)
        orders = self._load_orders(session, window)
        if not traffic and not funnel and not orders:
            return self._demo_funnel(window)

        impressions = self._sum_metric(funnel, "impressions") or self._sum_metric(traffic, "impressions")
        clicks = self._sum_metric(funnel, "clicks") or self._sum_metric(traffic, "clicks")
        cart = self._sum_metric(funnel, "cart")
        purchases = self._sum_metric(funnel, "purchase") or len(orders)
        impressions = max(impressions, purchases * 55, 1)
        clicks = max(min(clicks or int(impressions * 0.036), impressions), purchases * 4)
        cart = max(min(cart or int(clicks * 0.23), clicks), purchases)
        purchases = max(min(purchases, cart), 1 if orders else 0)
        stage_values = [
            ("impression", impressions),
            ("click", clicks),
            ("cart", cart),
            ("purchase", purchases),
        ]
        stages: list[FunnelStage] = []
        for index, (name, count) in enumerate(stage_values):
            previous_count = stage_values[index - 1][1] if index > 0 else count
            next_count = stage_values[index + 1][1] if index < len(stage_values) - 1 else count
            stages.append(
                FunnelStage(
                    stage=name,
                    count=count,
                    conversion_rate=round(self._safe_ratio(count, previous_count), 4),
                    drop_off_rate=round(max(0.0, 1 - self._safe_ratio(next_count, count)), 4),
                )
            )
        return ConversionFunnel(
            stages=stages,
            overall_cvr=round(self._safe_ratio(purchases, clicks), 4),
            date_range=self._window_dict(window),
        )

    def _build_competitor_analysis_from_monitor(self, session: Session, competitor: CompetitorProfile) -> CompetitorAnalysis:
        """构建竞品对标分析。"""

        accounts = self._load_accounts(session)
        orders = self._load_orders(session, self._resolve_date_range(None))
        own_followers = sum(int(getattr(item, "follower_count", 0) or 0) for item in accounts)
        own_revenue = round(sum(self._order_revenue(item) for item in orders), 2)
        benchmark_name = getattr(accounts[0], "shop_name", "TK-OPS 自营店") if accounts else "TK-OPS 自营店"
        own_avg_price = round(self._safe_ratio(own_revenue, max(len(orders), 1)), 2) if orders else max(competitor.avg_price * 0.92, 19.9)
        own_engagement = self._average_account_metric(accounts, "conversion_rate", fallback=0.034) + 0.012
        strengths: list[str] = []
        risks: list[str] = []
        opportunities: list[str] = []
        if competitor.follower_count > own_followers:
            strengths.append("粉丝盘更大，冷启动新品触达效率更高")
        else:
            opportunities.append("自营账号粉丝体量已具备追平竞品空间")
        if competitor.engagement_rate >= own_engagement:
            strengths.append("内容互动率更高，说明素材节奏与卖点表达更成熟")
        else:
            opportunities.append("竞品互动率低于我方，可通过短视频素材进一步抢量")
        if competitor.avg_price > own_avg_price * 1.2:
            risks.append("竞品客单价明显偏高，可能对低价带用户吸引不足")
            opportunities.append("可用中价高感知产品切入，放大性价比优势")
        else:
            strengths.append("竞品定价更贴近主流成交区间")
        if competitor.roas < 2.0:
            risks.append("竞品 ROAS 偏低，说明投放放量效率存在波动")
        if not strengths:
            strengths.append("竞品类目成熟，具备稳定的内容与成交闭环")
        if not risks:
            risks.append("竞品当前数据平稳，但需关注促销季对价格带的冲击")
        if not opportunities:
            opportunities.append("可围绕高复购 SKU 与强场景化短视频寻找差异化突破")
        return CompetitorAnalysis(
            competitor=competitor,
            benchmark_shop_name=benchmark_name,
            follower_gap=competitor.follower_count - own_followers,
            revenue_gap=round(competitor.est_monthly_sales - own_revenue, 2),
            price_index=round(self._safe_ratio(competitor.avg_price, own_avg_price), 4),
            engagement_gap=round(competitor.engagement_rate - own_engagement, 4),
            strengths=strengths,
            risks=risks,
            opportunities=opportunities,
        )

    def _build_profit_analysis(self, session: Session, product_id: str, window: DateWindow) -> ProfitBreakdown:
        """构建商品利润分析。"""

        orders = self._load_orders(session, window)
        matching_orders = [item for item in orders if str(self._order_metadata(item).get("product_id") or "") == product_id]
        product_orders = matching_orders or orders
        if not product_orders:
            return self._demo_profit(product_id, window)

        revenue = round(sum(self._order_revenue(item) for item in product_orders), 2)
        order_count = len(product_orders)
        metadata = [self._order_metadata(item) for item in product_orders]
        cogs = round(
            sum(self._to_float(item.get("cogs"), 0.0) for item in metadata) or revenue * 0.37,
            2,
        )
        shipping_cost = round(
            sum(self._to_float(item.get("shipping_cost"), 0.0) for item in metadata) or order_count * 2.8,
            2,
        )
        platform_fees = round(
            sum(self._to_float(item.get("platform_fee"), 0.0) for item in metadata) or revenue * 0.082,
            2,
        )
        ad_spend = round(
            sum(self._to_float(item.get("ad_spend"), 0.0) for item in metadata) or revenue * 0.14,
            2,
        )
        refund_loss = round(sum(self._refund_loss(item) for item in product_orders), 2)
        net_profit = round(revenue - cogs - shipping_cost - platform_fees - ad_spend - refund_loss, 2)
        gross_margin = round(self._safe_ratio(revenue - cogs, revenue), 4)
        net_margin = round(self._safe_ratio(net_profit, revenue), 4)
        roas = round(self._safe_ratio(revenue, ad_spend), 4)
        return ProfitBreakdown(
            product_id=product_id,
            revenue=revenue,
            cogs=cogs,
            shipping_cost=shipping_cost,
            platform_fees=platform_fees,
            ad_spend=ad_spend,
            refund_loss=refund_loss,
            net_profit=net_profit,
            gross_margin=gross_margin,
            net_margin=net_margin,
            roas=roas,
            date_range=self._window_dict(window),
        )

    def _build_engagement_metrics(self, session: Session, window: DateWindow) -> EngagementMetrics:
        """构建互动指标分析结果。"""

        engagement = self._load_snapshots(session, "engagement", window)
        live_sessions = self._load_live_sessions(session, window)
        if not engagement and not live_sessions:
            return self._demo_engagement(window)

        likes = self._sum_metric(engagement, "likes")
        comments = self._sum_metric(engagement, "comments")
        shares = self._sum_metric(engagement, "shares")
        total_views = self._sum_metric(engagement, "views")
        retention_rate = self._metric_average(engagement, "retention_rate", fallback=0.29)
        if likes == 0 and comments == 0 and shares == 0:
            likes = sum(int(getattr(item, "like_count", 0) or 0) for item in live_sessions)
            comments = sum(int(getattr(item, "comment_count", 0) or 0) for item in live_sessions)
            shares = sum(int((getattr(item, "comment_count", 0) or 0) * 0.85) for item in live_sessions)
        if total_views == 0:
            total_views = max(sum(int(getattr(item, "viewer_count", 0) or 0) for item in live_sessions), 1)
        average_engagement_rate = round(self._safe_ratio(likes + comments + shares, total_views), 4)
        return EngagementMetrics(
            likes=likes,
            comments=comments,
            shares=shares,
            total_views=total_views,
            average_engagement_rate=average_engagement_rate,
            retention_rate=round(retention_rate, 4),
            date_range=self._window_dict(window),
        )

    def _build_blue_ocean_opportunities(self, session: Session) -> list[BlueOceanOpportunity]:
        """构建蓝海机会分析。"""

        competitors = self._analytics_repo.list_competitors(session, active_only=True, limit=300)
        snapshots = self._analytics_repo.list_snapshots(session, snapshot_type="opportunity", limit=50)
        if snapshots:
            opportunities: list[BlueOceanOpportunity] = []
            for snapshot in snapshots:
                raw_items = self._normalize_sequence(snapshot.metrics_json.get("opportunities"))
                for item in raw_items:
                    if not isinstance(item, Mapping):
                        continue
                    demand_index = self._to_float(item.get("demand_index"), 0.0)
                    competition_index = self._to_float(item.get("competition_index"), 1.0)
                    score = self._to_float(item.get("opportunity_score"), demand_index / max(competition_index, 1.0))
                    opportunities.append(
                        BlueOceanOpportunity(
                            category=str(item.get("category") or "未分类"),
                            demand_index=round(demand_index, 2),
                            competition_index=round(competition_index, 2),
                            opportunity_score=round(score, 2),
                            rationale=str(item.get("rationale") or "来源于历史机会快照"),
                            recommended_products=[str(value) for value in self._normalize_sequence(item.get("recommended_products"))],
                        )
                    )
            if opportunities:
                return sorted(opportunities, key=lambda item: item.opportunity_score, reverse=True)[:5]
        if not competitors:
            return self._demo_blue_ocean_opportunities()

        category_counts: dict[str, int] = {}
        for competitor in competitors:
            category_counts[competitor.category] = category_counts.get(competitor.category, 0) + 1
        demand_map = {
            "smart_home": (91.0, ["感应夜灯", "桌面迷你加湿器", "抽屉收纳灯条"]),
            "pet_supplies": (88.0, ["宠物饮水机滤芯", "便携外出喂食杯", "宠物除毛滚刷"]),
            "kitchen_gadgets": (84.0, ["多功能切菜器", "冰箱分区收纳盒", "便携榨汁杯"]),
            "office_fitness": (79.0, ["桌下脚踏器", "护腕鼠标垫", "肩颈热敷带"]),
            "beauty_tools": (82.0, ["冷热导入仪", "旅行分装喷雾瓶", "速干化妆刷清洁垫"]),
        }
        opportunities = [
            BlueOceanOpportunity(
                category=category,
                demand_index=demand,
                competition_index=float(category_counts.get(category, 0) + 1),
                opportunity_score=round(demand / float(category_counts.get(category, 0) + 1), 2),
                rationale=f"需求指数高且监控竞品数量仅为 {category_counts.get(category, 0)} 个。",
                recommended_products=products,
            )
            for category, (demand, products) in demand_map.items()
        ]
        return sorted(opportunities, key=lambda item: item.opportunity_score, reverse=True)[:5]

    def _build_report_payload(
        self,
        session: Session,
        report_type: str,
        params: Mapping[str, object],
        window: DateWindow,
    ) -> dict[str, Any]:
        """根据报告类型构建报告内容。"""

        normalized_type = report_type.lower()
        if normalized_type in {"dashboard", "kpi", "summary"}:
            data: Any = self._build_dashboard_kpis(session, window)
        elif normalized_type in {"traffic", "traffic_overview"}:
            data = self._build_traffic_data(session, window)
        elif normalized_type in {"funnel", "conversion_funnel"}:
            data = self._build_conversion_funnel(session, window)
        elif normalized_type in {"competitor", "competitor_analysis"}:
            competitor_id = str(params.get("competitor_id") or "demo-fashion-lab")
            data = self.get_competitor_analysis(competitor_id)
        elif normalized_type in {"profit", "profit_analysis"}:
            product_id = str(params.get("product_id") or "default-product")
            data = self._build_profit_analysis(session, product_id, window)
        elif normalized_type in {"audience", "audience_persona"}:
            personas = self._extract_personas_from_snapshots(self._load_snapshots(session, "audience", None))
            data = personas or self._demo_personas()
        elif normalized_type in {"engagement", "engagement_metrics"}:
            data = self._build_engagement_metrics(session, window)
        elif normalized_type in {"opportunity", "blue_ocean", "blue_ocean_opportunities"}:
            data = self._build_blue_ocean_opportunities(session)
        else:
            raise ValueError(f"不支持的报告类型: {report_type}")
        payload = self._to_jsonable(data)
        return cast(dict[str, Any], payload if isinstance(payload, dict) else {"data": payload})

    def _build_report_summary(self, report_type: str, payload: Mapping[str, object]) -> str:
        """生成报告摘要文本。"""

        normalized_type = report_type.lower()
        if normalized_type in {"dashboard", "kpi", "summary"}:
            revenue = self._to_float(payload.get("total_revenue"), 0.0)
            orders = self._to_int(payload.get("total_orders"), 0)
            return f"本期 GMV {revenue:.2f}，累计订单 {orders} 单。"
        if normalized_type in {"traffic", "traffic_overview"}:
            views = self._to_int(payload.get("total_views"), 0)
            ctr = self._to_float(payload.get("ctr"), 0.0)
            return f"本期累计观看 {views} 次，CTR 为 {ctr:.2%}。"
        if normalized_type in {"profit", "profit_analysis"}:
            net_profit = self._to_float(payload.get("net_profit"), 0.0)
            net_margin = self._to_float(payload.get("net_margin"), 0.0)
            return f"商品净利润 {net_profit:.2f}，净利率 {net_margin:.2%}。"
        return "报告已根据当前分析数据生成。"

    def _default_report_title(self, report_type: str, window: DateWindow) -> str:
        """生成默认报告标题。"""

        return f"{report_type.upper()} 报告 {window.start_at.date().isoformat()} ~ {window.end_at.date().isoformat()}"

    def _load_accounts(self, session: Session) -> list[TikTokAccount]:
        """读取有效账号数据。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(TikTokAccount, "is_deleted"))
        statement = cast(Any, select(TikTokAccount)).where(deleted_column.is_(False))
        return list(session_any.scalars(statement).all())

    def _load_orders(self, session: Session, window: DateWindow | None) -> list[Order]:
        """读取订单数据并按时间窗口过滤。"""

        session_any = cast(Any, session)
        deleted_column = cast(Any, getattr(Order, "is_deleted"))
        statement = cast(Any, select(Order)).where(deleted_column.is_(False))
        rows = list(session_any.scalars(statement).all())
        if window is None:
            return rows
        return [item for item in rows if self._is_in_window(getattr(item, "created_at", None), window, fallback=getattr(item, "updated_at", None))]

    def _load_live_sessions(self, session: Session, window: DateWindow | None) -> list[object]:
        """兼容保留的互动回退入口；当前系统不使用直播指标模型。"""

        _ = session
        _ = window
        return []

    def _load_snapshots(self, session: Session, snapshot_type: str, window: DateWindow | None) -> list[AnalyticsSnapshot]:
        """读取分析快照。"""

        return self._analytics_repo.list_snapshots(
            session,
            snapshot_type=snapshot_type,
            start_at=window.start_at if window is not None else None,
            end_at=window.end_at if window is not None else None,
            limit=500,
        )

    def _extract_traffic_sources(
        self,
        snapshots: list[AnalyticsSnapshot],
        total_views: int,
        unique_visitors: int,
    ) -> list[TrafficSourceShare]:
        """从快照中提取流量来源，没有快照时生成占位分布。"""

        source_totals: dict[str, dict[str, int]] = {}
        for snapshot in snapshots:
            raw_sources = snapshot.metrics_json.get("traffic_sources")
            if not isinstance(raw_sources, Mapping):
                continue
            for key, raw_value in raw_sources.items():
                source_name = str(key)
                bucket = source_totals.setdefault(source_name, {"views": 0, "unique_visitors": 0})
                if isinstance(raw_value, Mapping):
                    bucket["views"] += self._to_int(raw_value.get("views"), 0)
                    bucket["unique_visitors"] += self._to_int(raw_value.get("unique_visitors"), 0)
                else:
                    bucket["views"] += self._to_int(raw_value, 0)
        if not source_totals:
            ratios = {
                "for_you": 0.46,
                "live": 0.19,
                "search": 0.14,
                "affiliate": 0.11,
                "profile": 0.10,
            }
            return [
                TrafficSourceShare(
                    source=source,
                    views=int(total_views * ratio),
                    unique_visitors=int(unique_visitors * max(ratio - 0.02, 0.03)),
                    share=round(ratio, 4),
                )
                for source, ratio in ratios.items()
            ]
        items = [
            TrafficSourceShare(
                source=source,
                views=data["views"],
                unique_visitors=data["unique_visitors"] or int(data["views"] * 0.62),
                share=round(self._safe_ratio(data["views"], total_views), 4),
            )
            for source, data in source_totals.items()
        ]
        return sorted(items, key=lambda item: item.views, reverse=True)

    def _extract_personas_from_snapshots(self, snapshots: list[AnalyticsSnapshot]) -> list[AudiencePersona]:
        """从受众快照中解析画像。"""

        personas: list[AudiencePersona] = []
        for snapshot in snapshots:
            raw_personas = self._normalize_sequence(snapshot.metrics_json.get("personas"))
            for item in raw_personas:
                if not isinstance(item, Mapping):
                    continue
                personas.append(
                    AudiencePersona(
                        name=str(item.get("name") or "未命名人群"),
                        age_range=str(item.get("age_range") or "25-34"),
                        gender=str(item.get("gender") or "female"),
                        location=str(item.get("location") or "一二线城市"),
                        interests=[str(value) for value in self._normalize_sequence(item.get("interests"))],
                        share=round(self._to_float(item.get("share"), 0.0), 4),
                        pain_points=[str(value) for value in self._normalize_sequence(item.get("pain_points"))],
                    )
                )
        return personas[:5]

    def _resolve_date_range(self, raw_date_range: object) -> DateWindow:
        """将外部传入的时间范围统一解析为时间窗口。"""

        default_end = datetime.now(timezone.utc)
        default_start = default_end - timedelta(days=30)
        if raw_date_range is None:
            return DateWindow(start_at=default_start, end_at=default_end)
        if isinstance(raw_date_range, tuple) and len(raw_date_range) == 2:
            start_at = self._coerce_datetime(raw_date_range[0]) or default_start
            end_at = self._coerce_datetime(raw_date_range[1]) or default_end
            return self._normalize_window(start_at, end_at)
        if isinstance(raw_date_range, Mapping):
            mapping = cast(Mapping[str, object], raw_date_range)
            start_at = self._coerce_datetime(
                mapping.get("start") or mapping.get("start_at") or mapping.get("from") or mapping.get("since")
            ) or default_start
            end_at = self._coerce_datetime(mapping.get("end") or mapping.get("end_at") or mapping.get("to") or mapping.get("until")) or default_end
            return self._normalize_window(start_at, end_at)
        parsed = self._coerce_datetime(raw_date_range)
        if parsed is not None:
            return self._normalize_window(parsed, default_end)
        return DateWindow(start_at=default_start, end_at=default_end)

    def _normalize_window(self, start_at: datetime, end_at: datetime) -> DateWindow:
        """规范化时间窗口顺序。"""

        if end_at < start_at:
            start_at, end_at = end_at, start_at
        return DateWindow(start_at=start_at, end_at=end_at)

    def _coerce_datetime(self, value: object) -> datetime | None:
        """将输入值转换为带时区的时间对象。"""

        if isinstance(value, datetime):
            return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
        if isinstance(value, str) and value.strip():
            normalized = value.strip().replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError:
                return None
            return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
        return None

    def _window_dict(self, window: DateWindow) -> dict[str, str]:
        """输出统一的时间窗口字典。"""

        return {"start": window.start_at.isoformat(), "end": window.end_at.isoformat()}

    def _metric_average(self, snapshots: list[AnalyticsSnapshot], key: str, fallback: float) -> float:
        """求指定快照指标均值。"""

        values = [self._to_float(snapshot.metrics_json.get(key), 0.0) for snapshot in snapshots if key in snapshot.metrics_json]
        if not values:
            return fallback
        return sum(values) / len(values)

    def _sum_metric(self, snapshots: list[AnalyticsSnapshot], key: str) -> int:
        """对快照中的整型指标求和。"""

        return sum(self._to_int(snapshot.metrics_json.get(key), 0) for snapshot in snapshots)

    def _average_account_metric(self, accounts: list[TikTokAccount], field_name: str, fallback: float) -> float:
        """求账号字段均值。"""

        if not accounts:
            return fallback
        values = [self._to_float(getattr(account, field_name, 0.0), 0.0) for account in accounts]
        return sum(values) / len(values) if values else fallback

    def _is_in_window(self, value: object, window: DateWindow, *, fallback: object = None) -> bool:
        """判断时间点是否落在窗口内。"""

        actual = self._coerce_datetime(value) or self._coerce_datetime(fallback)
        if actual is None:
            return False
        return window.start_at <= actual <= window.end_at

    def _to_competitor_monitor(self, competitor: CompetitorProfileModel) -> CompetitorProfile:
        """将 ORM 竞品对象转换为 DTO。"""

        return CompetitorProfile(
            competitor_id=competitor.competitor_id,
            shop_name=competitor.shop_name,
            display_name=competitor.display_name,
            category=competitor.category,
            region=competitor.region,
            follower_count=int(competitor.follower_count or 0),
            avg_views=int(competitor.avg_views or 0),
            avg_price=round(float(competitor.avg_price or 0.0), 2),
            est_monthly_sales=round(float(competitor.est_monthly_sales or 0.0), 2),
            engagement_rate=round(float(competitor.engagement_rate or 0.0), 4),
            ctr=round(float(competitor.ctr or 0.0), 4),
            cvr=round(float(competitor.cvr or 0.0), 4),
            roas=round(float(competitor.roas or 0.0), 4),
            status=competitor.status,
        )

    def _to_report_record(self, report: ReportModel) -> ReportRecord:
        """将报告 ORM 对象转换为 DTO。"""

        generated_at = self._coerce_datetime(report.generated_at)
        return ReportRecord(
            report_id=report.report_id,
            report_type=report.report_type,
            title=report.title,
            status=report.status,
            parameters=self._normalize_mapping(report.parameters_json),
            payload=self._normalize_mapping(report.payload_json),
            export_format=report.export_format,
            export_path=report.export_path,
            generated_at=generated_at.isoformat() if generated_at is not None else "",
            summary=report.summary,
        )

    def _order_metadata(self, order: Order) -> dict[str, Any]:
        """安全读取订单元数据。"""

        metadata = getattr(order, "metadata_json", {}) or {}
        return cast(dict[str, Any], metadata if isinstance(metadata, dict) else {})

    def _order_revenue(self, order: Order) -> float:
        """计算订单有效收入。"""

        status = str(getattr(order, "status", "") or "")
        refund_status = str(getattr(order, "refund_status", "") or "")
        amount = float(getattr(order, "total_amount", 0.0) or 0.0)
        if status in {"cancelled", "refunded"}:
            return 0.0
        if refund_status == "approved":
            return amount * 0.2
        return amount

    def _refund_loss(self, order: Order) -> float:
        """估算退款带来的损失。"""

        refund_status = str(getattr(order, "refund_status", "") or "")
        amount = float(getattr(order, "total_amount", 0.0) or 0.0)
        if refund_status == "approved":
            return round(amount * 0.8, 2)
        if refund_status == "requested":
            return round(amount * 0.25, 2)
        return 0.0

    def _normalize_mapping(self, value: object) -> dict[str, Any]:
        """将未知对象转换为字典。"""

        if isinstance(value, Mapping):
            return {str(key): self._to_jsonable(item) for key, item in value.items()}
        return {}

    def _normalize_sequence(self, value: object) -> list[object]:
        """将未知对象转换为列表。"""

        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return []

    def _to_jsonable(self, value: object) -> Any:
        """递归转换为可序列化对象。"""

        if is_dataclass(value) and not isinstance(value, type):
            return {field.name: self._to_jsonable(getattr(value, field.name)) for field in fields(value)}
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Mapping):
            return {str(key): self._to_jsonable(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        if isinstance(value, tuple):
            return [self._to_jsonable(item) for item in value]
        return value

    def _safe_ratio(self, numerator: float | int, denominator: float | int) -> float:
        """安全计算比率。"""

        denominator_value = float(denominator)
        if abs(denominator_value) < 1e-9:
            return 0.0
        return float(numerator) / denominator_value

    def _to_float(self, value: object, default: float) -> float:
        """将值转为浮点数。"""

        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return default
            try:
                return float(text)
            except ValueError:
                return default
        try:
            return float(str(value).strip())
        except (TypeError, ValueError):
            return default

    def _to_int(self, value: object, default: int) -> int:
        """将值转为整数。"""

        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return default
            try:
                return int(float(text))
            except ValueError:
                return default
        try:
            return int(float(str(value).strip()))
        except (TypeError, ValueError):
            return default

    def _as_optional_str(self, value: object) -> str | None:
        """将值转为可选字符串。"""

        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _build_business_id(self, prefix: str) -> str:
        """生成业务侧使用的唯一编号。"""

        return f"{prefix}-{uuid4().hex[:12]}"

    def _ensure_initialized(self) -> None:
        """确保服务已初始化。"""

        if not self._initialized:
            self.initialize()

    def _demo_dashboard(self, window: DateWindow) -> KPIDashboard:
        """返回演示用仪表盘数据。"""

        return KPIDashboard(
            total_revenue=128640.0,
            total_orders=2430,
            average_order_value=52.94,
            conversion_rate=0.041,
            follower_count=85600,
            total_views=1280000,
            unique_visitors=742000,
            ctr=0.0362,
            cvr=0.0568,
            retention_rate=0.338,
            engagement_rate=0.0724,
            gpm=100.5,
            roas=3.41,
            date_range=self._window_dict(window),
        )

    def _demo_traffic(self, window: DateWindow) -> TrafficData:
        """返回演示用流量数据。"""

        return TrafficData(
            total_views=1280000,
            unique_visitors=742000,
            impressions=1660000,
            clicks=60100,
            ctr=0.0362,
            gpm=100.5,
            roas=3.41,
            traffic_sources=[
                TrafficSourceShare(source="for_you", views=588800, unique_visitors=326000, share=0.46),
                TrafficSourceShare(source="live", views=243200, unique_visitors=126000, share=0.19),
                TrafficSourceShare(source="search", views=179200, unique_visitors=98000, share=0.14),
                TrafficSourceShare(source="affiliate", views=140800, unique_visitors=84000, share=0.11),
                TrafficSourceShare(source="profile", views=128000, unique_visitors=72000, share=0.10),
            ],
            date_range=self._window_dict(window),
        )

    def _demo_funnel(self, window: DateWindow) -> ConversionFunnel:
        """返回演示用漏斗数据。"""

        stages = [
            FunnelStage(stage="impression", count=1660000, conversion_rate=1.0, drop_off_rate=0.9638),
            FunnelStage(stage="click", count=60100, conversion_rate=0.0362, drop_off_rate=0.7341),
            FunnelStage(stage="cart", count=15980, conversion_rate=0.2659, drop_off_rate=0.5931),
            FunnelStage(stage="purchase", count=6502, conversion_rate=0.4069, drop_off_rate=0.0),
        ]
        return ConversionFunnel(stages=stages, overall_cvr=0.1082, date_range=self._window_dict(window))

    def _demo_competitors(self) -> list[CompetitorProfile]:
        """返回演示用竞品列表。"""

        return [
            CompetitorProfile(
                competitor_id="demo-fashion-lab",
                shop_name="Fashion Lab",
                display_name="Fashion Lab Official",
                category="fashion_accessories",
                region="US",
                follower_count=124000,
                avg_views=96800,
                avg_price=29.9,
                est_monthly_sales=182500.0,
                engagement_rate=0.084,
                ctr=0.041,
                cvr=0.063,
                roas=3.18,
                status="active",
            ),
            CompetitorProfile(
                competitor_id="demo-home-plus",
                shop_name="Home Plus Studio",
                display_name="Home Plus",
                category="smart_home",
                region="UK",
                follower_count=86300,
                avg_views=74200,
                avg_price=34.5,
                est_monthly_sales=143800.0,
                engagement_rate=0.071,
                ctr=0.037,
                cvr=0.058,
                roas=2.94,
                status="active",
            ),
            CompetitorProfile(
                competitor_id="demo-petwave",
                shop_name="PetWave",
                display_name="PetWave Daily",
                category="pet_supplies",
                region="CA",
                follower_count=59200,
                avg_views=68100,
                avg_price=24.9,
                est_monthly_sales=97800.0,
                engagement_rate=0.089,
                ctr=0.039,
                cvr=0.061,
                roas=3.52,
                status="active",
            ),
        ]

    def _demo_profit(self, product_id: str, window: DateWindow) -> ProfitBreakdown:
        """返回演示用利润分析。"""

        seed = sum(ord(char) for char in product_id) % 17
        revenue = 24800.0 + seed * 430
        cogs = round(revenue * 0.39, 2)
        shipping_cost = round(revenue * 0.067, 2)
        platform_fees = round(revenue * 0.082, 2)
        ad_spend = round(revenue * 0.136, 2)
        refund_loss = round(revenue * 0.031, 2)
        net_profit = round(revenue - cogs - shipping_cost - platform_fees - ad_spend - refund_loss, 2)
        return ProfitBreakdown(
            product_id=product_id,
            revenue=round(revenue, 2),
            cogs=cogs,
            shipping_cost=shipping_cost,
            platform_fees=platform_fees,
            ad_spend=ad_spend,
            refund_loss=refund_loss,
            net_profit=net_profit,
            gross_margin=round(self._safe_ratio(revenue - cogs, revenue), 4),
            net_margin=round(self._safe_ratio(net_profit, revenue), 4),
            roas=round(self._safe_ratio(revenue, ad_spend), 4),
            date_range=self._window_dict(window),
        )

    def _demo_personas(self) -> list[AudiencePersona]:
        """返回演示用受众画像。"""

        return [
            AudiencePersona(
                name="高频囤货白领",
                age_range="25-34",
                gender="female",
                location="一线/新一线城市",
                interests=["居家收纳", "效率工具", "限时秒杀"],
                share=0.38,
                pain_points=["没有时间做复杂对比", "希望快速看到真实场景效果"],
            ),
            AudiencePersona(
                name="价格敏感学生党",
                age_range="18-24",
                gender="all",
                location="大学城与二线城市",
                interests=["平替好物", "开箱测评", "短视频种草"],
                share=0.29,
                pain_points=["预算有限", "担心踩雷与售后体验"],
            ),
            AudiencePersona(
                name="家庭采购决策者",
                age_range="30-44",
                gender="female",
                location="二三线城市",
                interests=["家庭场景升级", "母婴家清", "高性价比套装"],
                share=0.21,
                pain_points=["希望一次购齐", "更关注耐用度与复购价值"],
            ),
        ]

    def _demo_engagement(self, window: DateWindow) -> EngagementMetrics:
        """返回演示用互动数据。"""

        return EngagementMetrics(
            likes=92100,
            comments=14860,
            shares=10340,
            total_views=1280000,
            average_engagement_rate=0.0917,
            retention_rate=0.338,
            date_range=self._window_dict(window),
        )

    def _demo_blue_ocean_opportunities(self) -> list[BlueOceanOpportunity]:
        """返回演示用蓝海机会列表。"""

        return [
            BlueOceanOpportunity(
                category="smart_home",
                demand_index=91.0,
                competition_index=2.0,
                opportunity_score=45.5,
                rationale="智能小家居在 TikTok 场景演示中转化高，但头部竞品密度仍低。",
                recommended_products=["感应夜灯", "抽屉灯条", "桌面迷你加湿器"],
            ),
            BlueOceanOpportunity(
                category="pet_supplies",
                demand_index=88.0,
                competition_index=2.0,
                opportunity_score=44.0,
                rationale="宠物高频消费赛道需求稳定，UGC 内容容易带动复购。",
                recommended_products=["宠物饮水机滤芯", "宠物除毛滚刷", "便携喂食杯"],
            ),
            BlueOceanOpportunity(
                category="office_fitness",
                demand_index=79.0,
                competition_index=2.0,
                opportunity_score=39.5,
                rationale="久坐办公与轻健身结合场景热度上升，内容竞争尚未完全拥挤。",
                recommended_products=["桌下脚踏器", "肩颈热敷带", "便携拉伸带"],
            ),
        ]

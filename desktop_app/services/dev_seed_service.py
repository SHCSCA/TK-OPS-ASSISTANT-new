"""Development-only seed data service."""
from __future__ import annotations

import datetime as _dt
import json
from typing import Any

from sqlalchemy import delete

from desktop_app.database.models import (
    AIProvider,
    Account,
    ActivityLog,
    AnalysisSnapshot,
    Asset,
    Device,
    ExperimentProject,
    ExperimentView,
    Group,
    ReportRun,
    Task,
    WorkflowDefinition,
    WorkflowRun,
)
from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService
from desktop_app.services.activity_service import ActivityService
from desktop_app.services.ai_service import AIService
from desktop_app.services.analytics_service import AnalyticsService
from desktop_app.services.asset_service import AssetService
from desktop_app.services.report_service import ReportService
from desktop_app.services.task_service import TaskService
from desktop_app.services.workflow_service import WorkflowService


class DevSeedService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()
        self._accounts = AccountService(self._repo)
        self._providers = AIService(self._repo)
        self._assets = AssetService(self._repo)
        self._tasks = TaskService(self._repo)
        self._analytics = AnalyticsService(self._repo)
        self._reports = ReportService(self._repo)
        self._workflows = WorkflowService(self._repo)
        self._activity = ActivityService(self._repo)

    def seed_development_data(self) -> dict[str, Any]:
        if self._has_seed_data():
            return {
                "created": 0,
                "counts": self._counts(),
            }

        created = self._seed_minimal_environment()
        return {
            "created": created,
            "counts": self._counts(),
        }

    def reset_business_data_with_realistic_seed(self) -> dict[str, Any]:
        self._clear_business_tables()
        created = self._seed_realistic_environment()
        return {
            "created": created,
            "counts": self._counts(),
        }

    def _seed_minimal_environment(self) -> int:
        created = 0
        group = self._accounts.create_group(
            "Seed / Europe",
            description="Development seed group",
            color="#2dd4bf",
        )
        created += 1

        device = self._accounts.create_device(
            "seed-device-eu-01",
            "Seed / Browser EU-01",
            proxy_ip="198.51.100.11",
            fingerprint_status="normal",
            proxy_status="online",
            status="healthy",
            region="DE",
        )
        created += 1

        account_a = self._accounts.create_account(
            "seed_alpha_us",
            region="US",
            platform="tiktok",
            status="active",
            followers=2800,
            group_id=group.id,
            device_id=device.id,
            notes="Development seed account",
        )
        account_b = self._accounts.create_account(
            "seed_beta_de",
            region="DE",
            platform="tiktok",
            status="warming",
            followers=5200,
            group_id=group.id,
            device_id=device.id,
            notes="Development seed account",
        )
        created += 2

        self._providers.create_provider(
            "Seed Provider",
            provider_type="openai",
            default_model="gpt-4o-mini",
            is_active=True,
        )
        created += 1

        for asset_spec in [
            ("seed-cover.png", "image", "C:/seed/seed-cover.png", 1024, account_a.id, "seed,image"),
            ("seed-hook.mp4", "video", "C:/seed/seed-hook.mp4", 4096, account_b.id, "seed,video"),
            ("seed-copy.txt", "text", "C:/seed/seed-copy.txt", 768, account_a.id, "seed,text"),
        ]:
            self._assets.create_asset(
                asset_spec[0],
                asset_type=asset_spec[1],
                file_path=asset_spec[2],
                file_size=asset_spec[3],
                account_id=asset_spec[4],
                tags=asset_spec[5],
            )
            created += 1

        report_task = self._tasks.create_task(
            "Seed / Weekly Report",
            task_type="report",
            status="completed",
            account_id=account_a.id,
            finished_at=_dt.datetime.now(),
            result_summary="Development seed report task",
        )
        failed_task = self._tasks.create_task(
            "Seed / Risk Review",
            task_type="maintenance",
            status="failed",
            account_id=account_a.id,
            finished_at=_dt.datetime.now(),
            result_summary="Development seed failed task",
        )
        self._tasks.create_task(
            "Seed / Content Publish",
            task_type="publish",
            status="running",
            account_id=account_b.id,
            started_at=_dt.datetime.now(),
            result_summary="Development seed publish task",
        )
        self._tasks.create_task(
            "Seed / Persona Refresh",
            task_type="interact",
            status="pending",
            account_id=account_b.id,
            result_summary="Development seed pending task",
        )
        created += 4

        self._reports.create_report_run(
            "Seed / Operating Report",
            report_type="weekly",
            status="completed",
            task_id=report_task.id,
            filters_json=json.dumps({"window": "7d"}, ensure_ascii=False),
        )
        self._reports.create_report_run(
            "Seed / Exception Digest",
            report_type="exception",
            status="pending",
            task_id=failed_task.id,
            filters_json=json.dumps({"focus": "failed_tasks"}, ensure_ascii=False),
        )
        created += 2

        workflow = self._workflows.create_workflow_definition(
            "Seed / Factory Workflow",
            status="active",
            description="Development seed workflow",
            config_json=json.dumps({"steps": ["input", "generate", "publish"]}, ensure_ascii=False),
        )
        workflow_b = self._workflows.create_workflow_definition(
            "Seed / Review Workflow",
            status="draft",
            description="Development review workflow",
            config_json=json.dumps({"steps": ["collect", "review", "archive"]}, ensure_ascii=False),
        )
        created += 2

        self._workflows.create_workflow_run(
            workflow.id,
            status="running",
            input_json=json.dumps({"source": "seed"}, ensure_ascii=False),
        )
        self._workflows.create_workflow_run(
            workflow_b.id,
            status="completed",
            input_json=json.dumps({"source": "seed-review"}, ensure_ascii=False),
            result_json=json.dumps({"status": "ok"}, ensure_ascii=False),
            finished_at=_dt.datetime.now(),
        )
        created += 2

        project = self._analytics.create_experiment_project(
            "Seed / Visual Experiment",
            goal="Exercise analytics and creative pages",
            status="active",
            config_json=json.dumps({"seed": True}, ensure_ascii=False),
        )
        project_b = self._analytics.create_experiment_project(
            "Seed / Conversion Experiment",
            goal="Exercise conversion and report pages",
            status="draft",
            config_json=json.dumps({"seed": True, "focus": "conversion"}, ensure_ascii=False),
        )
        created += 2

        self._analytics.create_experiment_view(
            project.id,
            "Seed / Trend View",
            layout_json=json.dumps({"chart": "trend"}, ensure_ascii=False),
        )
        self._analytics.create_experiment_view(
            project_b.id,
            "Seed / Funnel View",
            layout_json=json.dumps({"chart": "funnel"}, ensure_ascii=False),
        )
        created += 2

        for page_key, title, payload in [
            ("traffic-board", "Seed / Traffic Snapshot", {"accounts": 2, "tasks": 4}),
            ("competitor-monitor", "Seed / Competitor Snapshot", {"monitored": 2}),
            ("blue-ocean", "Seed / Opportunity Snapshot", {"topics": 4}),
        ]:
            self._analytics.create_analysis_snapshot(
                page_key,
                title,
                summary="Minimal development seed snapshot",
                payload_json=json.dumps(payload, ensure_ascii=False),
            )
            created += 1

        activity_specs = [
            ("seed", "Development seed completed", {"created": True}, "experiment_project", project.id),
            ("report", "Seed / Report queued", {"summary": "Exception digest pending"}, "report_run", None),
            ("workflow", "Seed / Workflow synced", {"message": "Review workflow completed"}, "workflow_run", None),
        ]
        for category, title, payload, related_type, related_id in activity_specs:
            self._activity.create_activity_log(
                category,
                title,
                payload_json=json.dumps(payload, ensure_ascii=False),
                related_entity_type=related_type,
                related_entity_id=related_id,
            )
            created += 1

        return created

    def _seed_realistic_environment(self) -> int:
        created = 0
        now = _dt.datetime.now()

        groups: dict[str, Group] = {}
        for name, description, color in [
            ("North America Growth", "US and CA growth accounts for traffic expansion", "#0ea5e9"),
            ("DACH Conversion", "DE and UK accounts focused on conversion and reporting", "#14b8a6"),
            ("Southeast Asia Labs", "SEA lab accounts for creatives and workflow tests", "#f59e0b"),
            ("Risk Recovery", "Accounts waiting for remediation and replay", "#ef4444"),
        ]:
            groups[name] = self._accounts.create_group(name, description=description, color=color)
            created += 1

        devices: dict[str, Device] = {}
        for spec in [
            {
                "key": "na-01",
                "device_code": "tkops-na-01",
                "name": "Browser Cluster NA-01",
                "proxy_ip": "23.88.14.10",
                "fingerprint_status": "normal",
                "proxy_status": "online",
                "status": "healthy",
                "region": "US",
            },
            {
                "key": "de-02",
                "device_code": "tkops-de-02",
                "name": "Browser Cluster DE-02",
                "proxy_ip": "91.204.17.22",
                "fingerprint_status": "drifted",
                "proxy_status": "lost",
                "status": "warning",
                "region": "DE",
            },
            {
                "key": "sg-03",
                "device_code": "tkops-sg-03",
                "name": "Browser Cluster SG-03",
                "proxy_ip": "103.76.33.18",
                "fingerprint_status": "normal",
                "proxy_status": "online",
                "status": "healthy",
                "region": "SG",
            },
            {
                "key": "uk-04",
                "device_code": "tkops-uk-04",
                "name": "Browser Cluster UK-04",
                "proxy_ip": "185.17.66.42",
                "fingerprint_status": "missing",
                "proxy_status": "offline",
                "status": "error",
                "region": "UK",
            },
        ]:
            devices[spec["key"]] = self._accounts.create_device(
                spec["device_code"],
                spec["name"],
                proxy_ip=spec["proxy_ip"],
                fingerprint_status=spec["fingerprint_status"],
                proxy_status=spec["proxy_status"],
                status=spec["status"],
                region=spec["region"],
            )
            created += 1

        accounts: dict[str, Account] = {}
        for spec in [
            {
                "username": "nova_home_us",
                "region": "US",
                "status": "active",
                "followers": 18600,
                "group": "North America Growth",
                "device": "na-01",
                "notes": "High-volume home storage account with stable publishing cadence.",
            },
            {
                "username": "glow_daily_us",
                "region": "US",
                "status": "warming",
                "followers": 7200,
                "group": "North America Growth",
                "device": "na-01",
                "notes": "Beauty accessories account in warm-up stage.",
            },
            {
                "username": "trend_box_de",
                "region": "DE",
                "status": "active",
                "followers": 13100,
                "group": "DACH Conversion",
                "device": "de-02",
                "notes": "DACH conversion-focused account with strong search traffic.",
            },
            {
                "username": "haus_signal_de",
                "region": "DE",
                "status": "idle",
                "followers": 4400,
                "group": "DACH Conversion",
                "device": "de-02",
                "notes": "Waiting for asset refresh before next campaign.",
            },
            {
                "username": "urban_mix_uk",
                "region": "UK",
                "status": "active",
                "followers": 9700,
                "group": "DACH Conversion",
                "device": "uk-04",
                "notes": "UK storefront with high interaction density.",
            },
            {
                "username": "shop_lab_sg",
                "region": "SG",
                "status": "warming",
                "followers": 5600,
                "group": "Southeast Asia Labs",
                "device": "sg-03",
                "notes": "SEA lab account for new creative themes.",
            },
            {
                "username": "pulse_find_my",
                "region": "MY",
                "status": "active",
                "followers": 8300,
                "group": "Southeast Asia Labs",
                "device": "sg-03",
                "notes": "MY account used for template and automation tests.",
            },
            {
                "username": "recover_ops_us",
                "region": "US",
                "status": "suspended",
                "followers": 3100,
                "group": "Risk Recovery",
                "device": "uk-04",
                "notes": "Suspended account kept for replay and risk review.",
            },
            {
                "username": "retry_lane_uk",
                "region": "UK",
                "status": "idle",
                "followers": 2100,
                "group": "Risk Recovery",
                "device": "uk-04",
                "notes": "Retry lane account with pending remediation workflow.",
            },
        ]:
            accounts[spec["username"]] = self._accounts.create_account(
                spec["username"],
                region=spec["region"],
                platform="tiktok",
                status=spec["status"],
                followers=spec["followers"],
                group_id=groups[spec["group"]].id,
                device_id=devices[spec["device"]].id,
                notes=spec["notes"],
            )
            created += 1

        default_provider_name = self._repo.get_setting("onboarding.default_provider", "OpenAI") or "OpenAI"
        default_model_name = self._repo.get_setting("onboarding.default_model", "gpt-4o-mini") or "gpt-4o-mini"
        for spec in [
            {
                "name": default_provider_name,
                "provider_type": "openai",
                "api_base": "https://api.openai.com/v1",
                "default_model": default_model_name,
                "temperature": 0.4,
                "max_tokens": 4096,
                "is_active": True,
            },
            {
                "name": "Operations Claude Backup",
                "provider_type": "anthropic",
                "api_base": "https://api.anthropic.com",
                "default_model": "claude-3-7-sonnet-latest",
                "temperature": 0.3,
                "max_tokens": 8192,
                "is_active": False,
            },
            {
                "name": "Local Review Runner",
                "provider_type": "local",
                "api_base": "http://127.0.0.1:11434/v1",
                "default_model": "qwen2.5-coder:14b",
                "temperature": 0.2,
                "max_tokens": 2048,
                "is_active": False,
            },
        ]:
            self._providers.create_provider(
                spec["name"],
                provider_type=spec["provider_type"],
                api_base=spec["api_base"],
                default_model=spec["default_model"],
                temperature=spec["temperature"],
                max_tokens=spec["max_tokens"],
                is_active=spec["is_active"],
            )
            created += 1

        asset_specs = [
            ("na-storage-cover-01.png", "image", "C:/seed/assets/na-storage-cover-01.png", 184320, "nova_home_us", "cover,storage,us"),
            ("na-storage-hook-01.mp4", "video", "C:/seed/assets/na-storage-hook-01.mp4", 7340032, "nova_home_us", "hook,video,us"),
            ("na-storage-script-01.txt", "text", "C:/seed/assets/na-storage-script-01.txt", 4096, "nova_home_us", "script,text"),
            ("beauty-angle-02.png", "image", "C:/seed/assets/beauty-angle-02.png", 155648, "glow_daily_us", "beauty,image"),
            ("beauty-offer-02.mp4", "video", "C:/seed/assets/beauty-offer-02.mp4", 6291456, "glow_daily_us", "offer,video"),
            ("de-ranking-board.xlsx", "template", "C:/seed/assets/de-ranking-board.xlsx", 8192, "trend_box_de", "report,template"),
            ("de-funnel-brief.txt", "text", "C:/seed/assets/de-funnel-brief.txt", 2048, "trend_box_de", "conversion,brief"),
            ("de-product-grid.png", "image", "C:/seed/assets/de-product-grid.png", 212992, "haus_signal_de", "grid,image"),
            ("uk-comment-replay.mp3", "audio", "C:/seed/assets/uk-comment-replay.mp3", 3145728, "urban_mix_uk", "audio,replay"),
            ("uk-launch-hook.mp4", "video", "C:/seed/assets/uk-launch-hook.mp4", 8388608, "urban_mix_uk", "launch,video"),
            ("sg-creator-matrix.png", "image", "C:/seed/assets/sg-creator-matrix.png", 172032, "shop_lab_sg", "matrix,lab"),
            ("sg-title-pack.txt", "text", "C:/seed/assets/sg-title-pack.txt", 3072, "shop_lab_sg", "title,copy"),
            ("my-campaign-template.json", "template", "C:/seed/assets/my-campaign-template.json", 5120, "pulse_find_my", "template,workflow"),
            ("risk-replay-sheet.txt", "text", "C:/seed/assets/risk-replay-sheet.txt", 1536, "recover_ops_us", "risk,replay"),
            ("recovery-checklist.png", "image", "C:/seed/assets/recovery-checklist.png", 143360, "retry_lane_uk", "risk,checklist"),
        ]
        for filename, asset_type, file_path, file_size, username, tags in asset_specs:
            self._assets.create_asset(
                filename,
                asset_type=asset_type,
                file_path=file_path,
                file_size=file_size,
                account_id=accounts[username].id,
                tags=tags,
            )
            created += 1

        task_specs = [
            {
                "key": "weekly-report-us",
                "title": "Weekly Report / NA Growth Overview",
                "task_type": "report",
                "priority": "high",
                "status": "completed",
                "account": "nova_home_us",
                "scheduled_at": now - _dt.timedelta(days=2, hours=2),
                "started_at": now - _dt.timedelta(days=2, hours=1, minutes=40),
                "finished_at": now - _dt.timedelta(days=2, hours=1, minutes=22),
                "result_summary": "North America growth report exported successfully.",
            },
            {
                "key": "creative-replay-us",
                "title": "Creative Replay / NA Hook Variants",
                "task_type": "publish",
                "priority": "high",
                "status": "running",
                "account": "nova_home_us",
                "scheduled_at": now - _dt.timedelta(hours=3),
                "started_at": now - _dt.timedelta(hours=2, minutes=35),
                "finished_at": None,
                "result_summary": "Rendering current winning hook versions.",
            },
            {
                "key": "comment-automation-uk",
                "title": "Comment Automation / UK Launch Replies",
                "task_type": "interact",
                "priority": "medium",
                "status": "running",
                "account": "urban_mix_uk",
                "scheduled_at": now - _dt.timedelta(hours=1),
                "started_at": now - _dt.timedelta(minutes=42),
                "finished_at": None,
                "result_summary": "Reply queue at 64% completion.",
            },
            {
                "key": "inventory-risk-de",
                "title": "Inventory Risk Review / DE Conversion",
                "task_type": "maintenance",
                "priority": "urgent",
                "status": "failed",
                "account": "trend_box_de",
                "scheduled_at": now - _dt.timedelta(days=1),
                "started_at": now - _dt.timedelta(days=1, minutes=50),
                "finished_at": now - _dt.timedelta(days=1, minutes=12),
                "result_summary": "Upstream template mismatch blocked risk review.",
            },
            {
                "key": "persona-refresh-sg",
                "title": "Persona Refresh / SG Lab Segment",
                "task_type": "report",
                "priority": "medium",
                "status": "pending",
                "account": "shop_lab_sg",
                "scheduled_at": now + _dt.timedelta(hours=2),
                "started_at": None,
                "finished_at": None,
                "result_summary": "Queued for next analytics window.",
            },
            {
                "key": "asset-sync-my",
                "title": "Asset Sync / MY Template Library",
                "task_type": "scrape",
                "priority": "medium",
                "status": "completed",
                "account": "pulse_find_my",
                "scheduled_at": now - _dt.timedelta(days=3),
                "started_at": now - _dt.timedelta(days=3, minutes=55),
                "finished_at": now - _dt.timedelta(days=3, minutes=9),
                "result_summary": "Template and copy assets synced to local library.",
            },
            {
                "key": "provider-health-check",
                "title": "Provider Health Check / Daily Baseline",
                "task_type": "maintenance",
                "priority": "low",
                "status": "completed",
                "account": None,
                "scheduled_at": now - _dt.timedelta(hours=8),
                "started_at": now - _dt.timedelta(hours=8, minutes=8),
                "finished_at": now - _dt.timedelta(hours=7, minutes=54),
                "result_summary": "Primary provider healthy, backup standby validated.",
            },
            {
                "key": "uk-risk-replay",
                "title": "Risk Replay / UK Recovery Lane",
                "task_type": "maintenance",
                "priority": "urgent",
                "status": "paused",
                "account": "retry_lane_uk",
                "scheduled_at": now - _dt.timedelta(hours=6),
                "started_at": now - _dt.timedelta(hours=5, minutes=35),
                "finished_at": None,
                "result_summary": "Paused pending proxy recovery confirmation.",
            },
            {
                "key": "us-catalog-scan",
                "title": "Catalog Scan / US Storage Products",
                "task_type": "scrape",
                "priority": "medium",
                "status": "completed",
                "account": "glow_daily_us",
                "scheduled_at": now - _dt.timedelta(days=4),
                "started_at": now - _dt.timedelta(days=4, minutes=42),
                "finished_at": now - _dt.timedelta(days=4, minutes=4),
                "result_summary": "24 product candidates scanned and normalized.",
            },
            {
                "key": "de-report-rollup",
                "title": "Report Rollup / DACH Conversion Summary",
                "task_type": "report",
                "priority": "high",
                "status": "completed",
                "account": "trend_box_de",
                "scheduled_at": now - _dt.timedelta(days=1, hours=6),
                "started_at": now - _dt.timedelta(days=1, hours=5, minutes=48),
                "finished_at": now - _dt.timedelta(days=1, hours=5, minutes=18),
                "result_summary": "DACH conversion summary published to report center.",
            },
            {
                "key": "sg-creative-batch",
                "title": "Creative Batch / SEA Theme Comparison",
                "task_type": "publish",
                "priority": "high",
                "status": "running",
                "account": "shop_lab_sg",
                "scheduled_at": now - _dt.timedelta(hours=4),
                "started_at": now - _dt.timedelta(hours=3, minutes=25),
                "finished_at": None,
                "result_summary": "Batch rendering 6 theme variants for review.",
            },
            {
                "key": "my-workflow-handoff",
                "title": "Workflow Handoff / MY Distribution Pack",
                "task_type": "publish",
                "priority": "medium",
                "status": "pending",
                "account": "pulse_find_my",
                "scheduled_at": now + _dt.timedelta(hours=4),
                "started_at": None,
                "finished_at": None,
                "result_summary": "Waiting for workflow approval and asset checklist.",
            },
            {
                "key": "us-risk-audit",
                "title": "Risk Audit / US Suspended Recovery",
                "task_type": "maintenance",
                "priority": "urgent",
                "status": "failed",
                "account": "recover_ops_us",
                "scheduled_at": now - _dt.timedelta(days=2, hours=4),
                "started_at": now - _dt.timedelta(days=2, hours=3, minutes=46),
                "finished_at": now - _dt.timedelta(days=2, hours=3, minutes=10),
                "result_summary": "Account risk replay blocked by missing fingerprint bundle.",
            },
            {
                "key": "daily-notification-sync",
                "title": "Notification Sync / Daily Activity Digest",
                "task_type": "report",
                "priority": "low",
                "status": "completed",
                "account": None,
                "scheduled_at": now - _dt.timedelta(hours=12),
                "started_at": now - _dt.timedelta(hours=11, minutes=55),
                "finished_at": now - _dt.timedelta(hours=11, minutes=46),
                "result_summary": "Activity digest generated for notification center.",
            },
        ]

        tasks: dict[str, Task] = {}
        for spec in task_specs:
            tasks[spec["key"]] = self._tasks.create_task(
                spec["title"],
                task_type=spec["task_type"],
                priority=spec["priority"],
                status=spec["status"],
                account_id=accounts[spec["account"]].id if spec["account"] else None,
                scheduled_at=spec["scheduled_at"],
                started_at=spec["started_at"],
                finished_at=spec["finished_at"],
                result_summary=spec["result_summary"],
            )
            created += 1

        report_specs = [
            {
                "title": "Operating Report / North America Weekly",
                "report_type": "weekly",
                "status": "completed",
                "task_key": "weekly-report-us",
                "filters": {"window": "7d", "region": "US", "group": "North America Growth"},
                "result": {"summary": "Traffic and content output stayed stable with two winning hooks."},
            },
            {
                "title": "Exception Digest / DACH Recovery",
                "report_type": "exception",
                "status": "failed",
                "task_key": "inventory-risk-de",
                "filters": {"window": "24h", "region": "DE", "focus": "failed_tasks"},
                "result": {"summary": "Inventory and template mismatch requires manual review."},
            },
            {
                "title": "Engagement Digest / UK Interaction",
                "report_type": "engagement",
                "status": "running",
                "task_key": "comment-automation-uk",
                "filters": {"window": "3d", "region": "UK", "focus": "comments"},
                "result": {"summary": "Live interaction report is still collecting samples."},
            },
            {
                "title": "SEA Lab Opportunity Report",
                "report_type": "analysis",
                "status": "pending",
                "task_key": "persona-refresh-sg",
                "filters": {"window": "14d", "region": "SG", "focus": "opportunities"},
                "result": {"summary": "Pending next analytics refresh window."},
            },
        ]
        for spec in report_specs:
            self._reports.create_report_run(
                spec["title"],
                report_type=spec["report_type"],
                status=spec["status"],
                task_id=tasks[spec["task_key"]].id,
                filters_json=json.dumps(spec["filters"], ensure_ascii=False),
                result_json=json.dumps(spec["result"], ensure_ascii=False),
            )
            created += 1

        workflow_defs: dict[str, WorkflowDefinition] = {}
        workflow_def_specs = [
            {
                "key": "creative-factory",
                "name": "Creative Factory / Variant Pipeline",
                "status": "active",
                "description": "Pull assets, generate variants, review, and publish winning versions.",
                "config": {"steps": ["collect_assets", "compose_variants", "review", "publish"]},
            },
            {
                "key": "risk-recovery",
                "name": "Risk Recovery / Replay Pipeline",
                "status": "active",
                "description": "Handle suspended accounts, replay remediation, and notify operators.",
                "config": {"steps": ["diagnose", "repair_proxy", "replay", "audit"]},
            },
            {
                "key": "report-assembly",
                "name": "Report Assembly / Ops Digest",
                "status": "draft",
                "description": "Collect metrics, assemble digest, and hand off for distribution.",
                "config": {"steps": ["collect", "aggregate", "draft", "dispatch"]},
            },
        ]
        for spec in workflow_def_specs:
            workflow_defs[spec["key"]] = self._workflows.create_workflow_definition(
                spec["name"],
                status=spec["status"],
                description=spec["description"],
                config_json=json.dumps(spec["config"], ensure_ascii=False),
            )
            created += 1

        workflow_run_specs = [
            {
                "definition": "creative-factory",
                "status": "running",
                "input": {"group": "North America Growth", "variant_count": 6},
                "result": {"note": "Two variants ready for review."},
                "started_at": now - _dt.timedelta(hours=2, minutes=10),
                "finished_at": None,
            },
            {
                "definition": "risk-recovery",
                "status": "failed",
                "input": {"account": "recover_ops_us", "replay_mode": "full"},
                "result": {"error": "Fingerprint package missing."},
                "started_at": now - _dt.timedelta(days=1, hours=1),
                "finished_at": now - _dt.timedelta(days=1, minutes=18),
            },
            {
                "definition": "report-assembly",
                "status": "completed",
                "input": {"report": "Operating Report / North America Weekly"},
                "result": {"export": "ready", "targets": 3},
                "started_at": now - _dt.timedelta(hours=10),
                "finished_at": now - _dt.timedelta(hours=9, minutes=34),
            },
            {
                "definition": "creative-factory",
                "status": "pending",
                "input": {"group": "Southeast Asia Labs", "variant_count": 4},
                "result": {"note": "Waiting for asset sync."},
                "started_at": None,
                "finished_at": None,
            },
        ]
        for spec in workflow_run_specs:
            self._workflows.create_workflow_run(
                workflow_defs[spec["definition"]].id,
                status=spec["status"],
                input_json=json.dumps(spec["input"], ensure_ascii=False),
                result_json=json.dumps(spec["result"], ensure_ascii=False),
                started_at=spec["started_at"],
                finished_at=spec["finished_at"],
            )
            created += 1

        experiment_projects: dict[str, ExperimentProject] = {}
        for spec in [
            {
                "key": "visual-lab",
                "name": "Visual Lab / Hook Retention Study",
                "goal": "Compare retention impact across opening hook structures.",
                "status": "active",
                "config": {"variants": 3, "primary_metric": "retention"},
            },
            {
                "key": "conversion-lab",
                "name": "Conversion Lab / DACH Funnel Repair",
                "goal": "Identify where DACH traffic loses momentum before task completion.",
                "status": "active",
                "config": {"variants": 2, "primary_metric": "completion_rate"},
            },
            {
                "key": "creative-workshop",
                "name": "Creative Workshop / Angle Arbitration",
                "goal": "Store competing creative directions and hand off winners downstream.",
                "status": "draft",
                "config": {"variants": 4, "primary_metric": "operator_score"},
            },
        ]:
            experiment_projects[spec["key"]] = self._analytics.create_experiment_project(
                spec["name"],
                goal=spec["goal"],
                status=spec["status"],
                config_json=json.dumps(spec["config"], ensure_ascii=False),
            )
            created += 1

        for project_key, view_name, layout in [
            ("visual-lab", "Retention Overview", {"chart": "trend", "dimension": "hook"}),
            ("visual-lab", "Winning Variant Grid", {"chart": "grid", "dimension": "variant"}),
            ("conversion-lab", "Funnel Drop-off", {"chart": "funnel", "dimension": "stage"}),
            ("conversion-lab", "Region Conversion Table", {"chart": "table", "dimension": "region"}),
            ("creative-workshop", "Angle Scoreboard", {"chart": "cards", "dimension": "angle"}),
            ("creative-workshop", "Handoff Queue", {"chart": "queue", "dimension": "handoff"}),
        ]:
            self._analytics.create_experiment_view(
                experiment_projects[project_key].id,
                view_name,
                layout_json=json.dumps(layout, ensure_ascii=False),
            )
            created += 1

        snapshot_specs = [
            ("traffic-board", "Traffic Snapshot / Daily Channel Mix", "Traffic status derived from live account, task, and activity data.", {"regions": ["US", "DE", "UK"], "sample_accounts": 9}),
            ("competitor-monitor", "Competitor Snapshot / Account Ranking", "Competitor board refreshed from live account follower distribution.", {"leader": "nova_home_us", "followers": 18600}),
            ("blue-ocean", "Opportunity Snapshot / Topic Surface", "Opportunity map generated from region and asset coverage.", {"topics": 5, "coverage": "mixed"}),
            ("interaction-analysis", "Interaction Snapshot / Sentiment Digest", "Interaction board built from activity logs and task outcomes.", {"positive": 71, "negative": 12}),
            ("report-center", "Report Snapshot / Distribution Status", "Report center state captured after latest digest export.", {"reports": 4, "pending": 1}),
            ("visual-lab", "Experiment Snapshot / Variant Winners", "Visual lab tracks retained winners for downstream handoff.", {"projects": 3, "views": 6}),
        ]
        for page_key, title, summary, payload in snapshot_specs:
            self._analytics.create_analysis_snapshot(
                page_key,
                title,
                summary=summary,
                payload_json=json.dumps(payload, ensure_ascii=False),
                filters_json=json.dumps({"generated_at": now.isoformat(timespec="seconds")}, ensure_ascii=False),
            )
            created += 1

        activity_specs = [
            ("seed", "Realistic business seed rebuilt", {"summary": "Business tables were reset and rebuilt for local operations."}, "seed", None),
            ("task", "Weekly report finished for NA growth", {"summary": "North America weekly report exported successfully."}, "task", tasks["weekly-report-us"].id),
            ("task", "UK interaction task is still running", {"summary": "Reply queue remains active and needs monitoring."}, "task", tasks["comment-automation-uk"].id),
            ("warning", "DACH inventory review failed", {"summary": "Template mismatch blocked the risk review path."}, "task", tasks["inventory-risk-de"].id),
            ("report", "Exception digest needs manual attention", {"summary": "Failed exception report waiting for human review."}, "report_run", None),
            ("workflow", "Creative factory workflow is producing variants", {"summary": "Two winning hooks are ready for review."}, "workflow_run", None),
            ("workflow", "Risk recovery workflow failed on replay", {"summary": "Missing fingerprint bundle requires remediation."}, "workflow_run", None),
            ("experiment", "Visual lab retained the winning hook", {"summary": "Retention overview selected one primary opening variant."}, "experiment_project", experiment_projects["visual-lab"].id),
            ("experiment", "Creative workshop draft is waiting for arbitration", {"summary": "Four creative directions are stored for operator review."}, "experiment_project", experiment_projects["creative-workshop"].id),
            ("task", "Provider health check passed", {"summary": "Primary provider is healthy and backups are available."}, "task", tasks["provider-health-check"].id),
            ("report", "Daily activity digest synced to notifications", {"summary": "Notification center can now render from live activity data."}, "task", tasks["daily-notification-sync"].id),
            ("warning", "US suspended recovery account still blocked", {"summary": "Suspended account requires proxy and fingerprint repair."}, "task", tasks["us-risk-audit"].id),
        ]
        for category, title, payload, related_type, related_id in activity_specs:
            self._activity.create_activity_log(
                category,
                title,
                payload_json=json.dumps(payload, ensure_ascii=False),
                related_entity_type=related_type,
                related_entity_id=related_id,
            )
            created += 1

        return created

    def _clear_business_tables(self) -> None:
        session = self._repo.session
        for model in [
            ActivityLog,
            AnalysisSnapshot,
            ReportRun,
            WorkflowRun,
            ExperimentView,
            Task,
            Asset,
            ExperimentProject,
            WorkflowDefinition,
            Account,
            AIProvider,
            Device,
            Group,
        ]:
            session.execute(delete(model))
        session.commit()
        session.expire_all()

    def _has_seed_data(self) -> bool:
        return any(
            [
                self._repo.count(Group) > 0,
                self._repo.count(Account) > 0,
                self._repo.count(Device) > 0,
                self._repo.count(AIProvider) > 0,
                self._repo.count(Asset) > 0,
                self._repo.count(Task) > 0,
                self._repo.count(ExperimentProject) > 0,
            ]
        )

    def _counts(self) -> dict[str, int]:
        providers = self._repo.count(AIProvider)
        return {
            "groups": self._repo.count(Group),
            "devices": self._repo.count(Device),
            "accounts": self._repo.count(Account),
            "providers": providers,
            "ai_providers": providers,
            "assets": self._repo.count(Asset),
            "tasks": self._repo.count(Task),
            "analysis_snapshots": self._repo.count(AnalysisSnapshot),
            "report_runs": self._repo.count(ReportRun),
            "workflow_definitions": self._repo.count(WorkflowDefinition),
            "workflow_runs": self._repo.count(WorkflowRun),
            "experiment_projects": self._repo.count(ExperimentProject),
            "experiment_views": self._repo.count(ExperimentView),
            "activity_logs": self._repo.count(ActivityLog),
        }

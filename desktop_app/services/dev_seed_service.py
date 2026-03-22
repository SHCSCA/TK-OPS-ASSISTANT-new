"""Development-only seed data service."""
from __future__ import annotations

from typing import Any

from desktop_app.database.models import (
    AIProvider,
    Account,
    Asset,
    ExperimentProject,
    ExperimentView,
    Group,
    Task,
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

        created = 0
        group = self._accounts.create_group("Seed / Europe", description="Development seed group", color="#2dd4bf")
        created += 1

        account_a = self._accounts.create_account(
            "seed_alpha_us",
            region="US",
            platform="tiktok",
            status="active",
            followers=2800,
            group_id=group.id,
            notes="Development seed account",
        )
        account_b = self._accounts.create_account(
            "seed_beta_de",
            region="DE",
            platform="tiktok",
            status="warming",
            followers=5200,
            group_id=group.id,
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

        self._assets.create_asset(
            "seed-cover.png",
            asset_type="image",
            file_path="C:/seed/seed-cover.png",
            file_size=1024,
            account_id=account_a.id,
            tags="seed,image",
        )
        self._assets.create_asset(
            "seed-hook.mp4",
            asset_type="video",
            file_path="C:/seed/seed-hook.mp4",
            file_size=4096,
            account_id=account_b.id,
            tags="seed,video",
        )
        created += 2

        self._assets.create_asset(
            "seed-copy.txt",
            asset_type="text",
            file_path="C:/seed/seed-copy.txt",
            file_size=768,
            account_id=account_a.id,
            tags="seed,text",
        )
        created += 1

        report_task = self._tasks.create_task(
            "Seed / Weekly Report",
            task_type="report",
            status="completed",
            account_id=account_a.id,
            result_summary="Development seed report task",
        )
        self._tasks.create_task(
            "Seed / Content Publish",
            task_type="publish",
            status="running",
            account_id=account_b.id,
            result_summary="Development seed publish task",
        )
        failed_task = self._tasks.create_task(
            "Seed / Risk Review",
            task_type="maintenance",
            status="failed",
            account_id=account_a.id,
            result_summary="Development seed failed task",
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
            filters_json='{"window":"7d"}',
        )
        self._reports.create_report_run(
            "Seed / Exception Digest",
            report_type="exception",
            status="pending",
            task_id=failed_task.id,
            filters_json='{"focus":"failed_tasks"}',
        )
        workflow = self._workflows.create_workflow_definition(
            "Seed / Factory Workflow",
            status="active",
            description="Development seed workflow",
            config_json='{"steps":["input","generate","publish"]}',
        )
        self._workflows.create_workflow_run(
            workflow.id,
            status="running",
            input_json='{"source":"seed"}',
        )
        workflow_b = self._workflows.create_workflow_definition(
            "Seed / Review Workflow",
            status="draft",
            description="Development review workflow",
            config_json='{"steps":["collect","review","archive"]}',
        )
        self._workflows.create_workflow_run(
            workflow_b.id,
            status="completed",
            input_json='{"source":"seed-review"}',
        )
        project = self._analytics.create_experiment_project(
            "Seed / Visual Experiment",
            goal="Exercise analytics and creative pages",
            status="active",
            config_json='{"seed":true}',
        )
        self._analytics.create_experiment_view(
            project.id,
            "Seed / Trend View",
            layout_json='{"chart":"trend"}',
        )
        project_b = self._analytics.create_experiment_project(
            "Seed / Conversion Experiment",
            goal="Exercise conversion and report pages",
            status="draft",
            config_json='{"seed":true,"focus":"conversion"}',
        )
        self._analytics.create_experiment_view(
            project_b.id,
            "Seed / Funnel View",
            layout_json='{"chart":"funnel"}',
        )
        self._analytics.create_analysis_snapshot(
            "traffic-board",
            "Seed / Traffic Snapshot",
            summary="Traffic snapshot for development pages",
            payload_json='{"accounts":2,"tasks":4}',
        )
        self._analytics.create_analysis_snapshot(
            "competitor-monitor",
            "Seed / Competitor Snapshot",
            summary="Competitor snapshot for development pages",
            payload_json='{"monitored":2}',
        )
        self._analytics.create_analysis_snapshot(
            "blue-ocean",
            "Seed / Opportunity Snapshot",
            summary="Blue ocean snapshot for development pages",
            payload_json='{"topics":4}',
        )
        self._activity.create_activity_log(
            "seed",
            "Development seed completed",
            payload_json='{"created":true}',
            related_entity_type="experiment_project",
            related_entity_id=project.id,
        )
        self._activity.create_activity_log(
            "report",
            "Seed / Report queued",
            payload_json='{"summary":"Exception digest pending"}',
            related_entity_type="report_run",
            related_entity_id=2,
        )
        self._activity.create_activity_log(
            "workflow",
            "Seed / Workflow synced",
            payload_json='{"message":"Review workflow completed"}',
            related_entity_type="workflow_run",
            related_entity_id=2,
        )
        created += 14

        return {
            "created": created,
            "counts": self._counts(),
        }

    def _has_seed_data(self) -> bool:
        return any(
            [
                self._repo.count(Account) > 0,
                self._repo.count(AIProvider) > 0,
                self._repo.count(Asset) > 0,
                self._repo.count(Task) > 0,
                self._repo.count(ExperimentProject) > 0,
            ]
        )

    def _counts(self) -> dict[str, int]:
        return {
            "accounts": self._repo.count(Account),
            "groups": self._repo.count(Group),
            "providers": self._repo.count(AIProvider),
            "assets": self._repo.count(Asset),
            "tasks": self._repo.count(Task),
            "experiment_projects": self._repo.count(ExperimentProject),
            "experiment_views": self._repo.count(ExperimentView),
        }

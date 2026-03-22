"""Analytics aggregates plus experiment persistence service."""
from __future__ import annotations

from typing import Any, Sequence

from desktop_app.database.models import (
    AIProvider,
    AnalysisSnapshot,
    Asset,
    Task,
    ExperimentProject,
    ExperimentView,
)
from desktop_app.database.repository import Repository


class AnalyticsService:
    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def get_analytics_summary(self) -> dict[str, Any]:
        accounts = list(self._repo.list_accounts())
        tasks = list(self._repo.list_tasks())
        assets = list(self._repo.list_assets())
        providers = list(self._repo.list_all(AIProvider))
        experiments = list(self._repo.list_experiment_projects())
        views = list(self._repo.list_experiment_views())

        by_region: dict[str, int] = {}
        for account in accounts:
            region = str(account.region or "unknown")
            by_region[region] = by_region.get(region, 0) + 1

        by_asset_type: dict[str, int] = {}
        for asset in assets:
            asset_type = str(asset.asset_type or "unknown")
            by_asset_type[asset_type] = by_asset_type.get(asset_type, 0) + 1

        provider_models = sorted({str(provider.default_model or "").strip() for provider in providers if provider.default_model})
        active_providers = [provider for provider in providers if bool(provider.is_active)]
        completed_tasks = [task for task in tasks if str(task.status or "").lower() == "completed"]
        running_tasks = [task for task in tasks if str(task.status or "").lower() == "running"]
        failed_tasks = [task for task in tasks if str(task.status or "").lower() == "failed"]
        active_accounts = [account for account in accounts if str(account.status or "").lower() in {"active", "warming"}]
        total_followers = sum(int(account.followers or 0) for account in accounts)

        return {
            "accounts": {
                "total": len(accounts),
                "active": len(active_accounts),
                "by_region": by_region,
                "followers_total": total_followers,
            },
            "tasks": {
                "total": len(tasks),
                "completed": len(completed_tasks),
                "running": len(running_tasks),
                "failed": len(failed_tasks),
            },
            "assets": {
                "total": len(assets),
                "by_type": by_asset_type,
            },
            "providers": {
                "total": len(providers),
                "active": len(active_providers),
                "models": provider_models,
            },
            "experiments": {
                "projects": len(experiments),
                "views": len(views),
            },
        }

    def get_conversion_analysis(self) -> dict[str, Any]:
        summary = self.get_analytics_summary()
        accounts_total = int(summary["accounts"]["total"])
        active_accounts = int(summary["accounts"]["active"])
        tasks_total = int(summary["tasks"]["total"])
        completed_tasks = int(summary["tasks"]["completed"])
        assets_total = int(summary["assets"]["total"])

        funnel = [
            {"key": "accounts", "label": "账号样本", "value": accounts_total},
            {"key": "active_accounts", "label": "活跃账号", "value": active_accounts},
            {"key": "tasks", "label": "执行任务", "value": tasks_total},
            {"key": "completed_tasks", "label": "完成任务", "value": completed_tasks},
            {"key": "assets", "label": "素材支撑", "value": assets_total},
        ]
        return {
            "counts": {
                "accounts": accounts_total,
                "active_accounts": active_accounts,
                "tasks": tasks_total,
                "completed_tasks": completed_tasks,
                "assets": assets_total,
            },
            "funnel": funnel,
        }

    def get_persona_analysis(self) -> dict[str, Any]:
        accounts = list(self._repo.list_accounts())
        tasks = list(self._repo.list_tasks())
        assets = list(self._repo.list_assets())

        segments = [
            {
                "key": "high_value",
                "label": "高价值粉丝",
                "count": sum(1 for account in accounts if int(account.followers or 0) >= 3000),
            },
            {
                "key": "active_watch",
                "label": "活跃观察",
                "count": sum(1 for account in accounts if str(account.status or "").lower() in {"active", "warming"}),
            },
            {
                "key": "content_driven",
                "label": "内容驱动",
                "count": max(1, len(assets)),
            },
            {
                "key": "task_backed",
                "label": "任务驱动",
                "count": max(1, len(tasks)),
            },
        ]

        by_region: dict[str, dict[str, Any]] = {}
        for account in accounts:
            region = str(account.region or "unknown")
            if region not in by_region:
                by_region[region] = {"key": region, "label": region, "count": 0, "followers": 0}
            by_region[region]["count"] += 1
            by_region[region]["followers"] += int(account.followers or 0)

        regions = sorted(
            by_region.values(),
            key=lambda item: (-int(item["followers"]), -int(item["count"]), str(item["key"])),
        )

        return {
            "segments": segments,
            "regions": regions,
            "interest_clusters": [
                {"key": "content_reuse", "label": "素材复用", "count": max(1, len(assets))},
                {"key": "task_feedback", "label": "任务反馈", "count": max(1, len(tasks))},
            ],
        }

    def get_traffic_analysis(self) -> dict[str, Any]:
        summary = self.get_analytics_summary()
        activity = list(self._repo.list_activity_logs())
        counts = summary["tasks"]
        account_total = int(summary["accounts"]["total"])
        active_accounts = int(summary["accounts"]["active"])
        task_total = int(counts["total"])
        completed_tasks = int(counts["completed"])
        failed_tasks = int(counts["failed"])
        asset_total = int(summary["assets"]["total"])
        region_map = dict(summary["accounts"].get("by_region", {}))
        region_rows = list(region_map.items())

        return {
            "metrics": {
                "account_sample": account_total,
                "task_completion_rate": self._percent(completed_tasks, task_total),
                "failed_tasks": failed_tasks,
            },
            "sources": [
                {"label": "活跃账号", "value": active_accounts, "meta": f"地区 {len(region_map)} 个 / 持续跟踪"},
                {"label": "执行任务", "value": task_total, "meta": f"完成 {completed_tasks} / 失败 {failed_tasks}"},
                {"label": "活动记录", "value": len(activity), "meta": f"素材 {asset_total} / 最近更新 {min(len(activity), 20)} 条"},
            ],
            "rows": [
                {
                    "label": region or "未标注区域",
                    "delta": f"账号 {count}",
                    "reason": "账号样本已接入" if count >= 1 else "等待样本",
                    "action": "继续观察" if count >= 2 else "补充样本",
                }
                for region, count in region_rows[:4]
            ],
            "trend": [account_total, active_accounts, task_total, completed_tasks, asset_total],
        }

    def get_competitor_analysis(self) -> dict[str, Any]:
        accounts = list(self._repo.list_accounts())
        tasks = list(self._repo.list_tasks())
        ranked_accounts = sorted(accounts, key=lambda item: int(item.followers or 0), reverse=True)
        failed_tasks = sum(1 for task in tasks if str(task.status or "").lower() == "failed")
        region_count = len({str(account.region or "unknown") for account in accounts})
        total_followers = max(1, sum(int(account.followers or 0) for account in ranked_accounts))

        rivals = []
        rows = []
        bars = []
        for index, account in enumerate(ranked_accounts[:4]):
            followers = int(account.followers or 0)
            bars.append(max(20, min(96, round((followers / total_followers) * 100))))
            rivals.append(
                {
                    "name": str(account.username or f"账号 {index + 1}"),
                    "followers": followers,
                    "delta": f"地区 {account.region or 'unknown'}",
                    "tone": "success" if index == 0 else "info",
                }
            )
            rows.append(
                {
                    "title": str(account.username or f"账号 {index + 1}"),
                    "value": followers,
                    "meta": f"{account.region or 'unknown'} / {account.platform or 'tiktok'}",
                    "conclusion": "样本较大，可持续跟踪" if followers >= 3000 else "样本较小，继续观察",
                }
            )

        return {
            "metrics": {
                "monitored_accounts": len(accounts),
                "failed_tasks": failed_tasks,
                "regions": region_count,
            },
            "rivals": rivals,
            "rows": rows,
            "bars": bars,
        }

    def get_blue_ocean_analysis(self) -> dict[str, Any]:
        accounts = list(self._repo.list_accounts())
        assets = list(self._repo.list_assets())
        tasks = list(self._repo.list_tasks())

        region_topics = [f"{account.region} 运营样本" for account in accounts if account.region]
        asset_topics = []
        asset_types = sorted({str(asset.asset_type or "素材") for asset in assets})
        for asset_type in asset_types:
            asset_topics.append(f"{asset_type} 素材主题")
        topic_labels = (region_topics + asset_topics + ["任务反馈主题", "低竞争切口"])[:5]
        failed_tasks = sum(1 for task in tasks if str(task.status or "").lower() == "failed")
        matrix = []
        for index, label in enumerate(topic_labels):
            matrix.append(
                {
                    "label": label,
                    "heat": max(20, min(95, 55 + index * 7 + len(accounts) * 3)),
                    "competition": max(10, min(90, 35 + failed_tasks * 4 + index * 3)),
                    "coverage": max(10, min(90, 18 + len(assets) * 5 - index * 2)),
                }
            )

        lead = matrix[0] if matrix else {"label": "暂无主题", "heat": 0, "competition": 0, "coverage": 0}
        return {
            "metrics": {
                "candidate_topics": len(topic_labels),
                "asset_topics": len(asset_types),
                "failed_tasks": failed_tasks,
            },
            "topics": topic_labels,
            "lead": {
                "title": lead["label"],
                "heat": lead["heat"],
                "competition": lead["competition"],
                "coverage": lead["coverage"],
                "description": "基于账号地区、素材类型和任务反馈自动汇总的候选主题。",
            },
            "matrix": matrix,
        }

    def get_interaction_analysis(self) -> dict[str, Any]:
        accounts = list(self._repo.list_accounts())
        tasks = list(self._repo.list_tasks())
        assets = list(self._repo.list_assets())
        activity = list(self._repo.list_activity_logs())
        followers_total = sum(int(account.followers or 0) for account in accounts)
        failed_tasks = sum(1 for task in tasks if str(task.status or "").lower() == "failed")
        completed_tasks = sum(1 for task in tasks if str(task.status or "").lower() == "completed")
        positive = min(92, max(35, 48 + completed_tasks * 8 + len(activity) * 2))
        negative = min(40, max(4, failed_tasks * 5))
        neutral = max(0, 100 - positive - negative)
        keywords = []
        for account in accounts[:3]:
            if account.region:
                keywords.append(f"{account.region} 用户反馈")
        for asset in assets[:2]:
            if asset.asset_type:
                keywords.append(f"{asset.asset_type} 素材互动")
        keywords.extend(["任务完成反馈", "异常跟进"])

        return {
            "metrics": {
                "followers_total": followers_total,
                "positive_share": positive,
                "risk_items": failed_tasks,
            },
            "sentiment": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
            },
            "keywords": keywords[:7],
            "heatmap": [
                max(1, min(5, 1 + len(accounts))),
                max(1, min(5, 1 + len(assets))),
                max(1, min(5, 1 + len(activity))),
            ],
            "affinity": [
                max(18, min(96, 20 + len(accounts) * 12)),
                max(18, min(96, 18 + len(assets) * 12)),
                max(18, min(96, 16 + completed_tasks * 14)),
                max(18, min(96, 12 + failed_tasks * 10)),
            ],
        }

    @staticmethod
    def _percent(part: int, whole: int) -> int:
        if whole <= 0:
            return 0
        return max(0, min(100, round((part / whole) * 100)))

    def create_analysis_snapshot(self, page_key: str, title: str, **kwargs: Any) -> AnalysisSnapshot:
        return self._repo.add(AnalysisSnapshot(page_key=page_key, title=title, **kwargs))

    def list_analysis_snapshots(self, page_key: str | None = None) -> Sequence[AnalysisSnapshot]:
        return self._repo.list_analysis_snapshots(page_key=page_key)

    def create_experiment_project(self, name: str, **kwargs: Any) -> ExperimentProject:
        return self._repo.add(ExperimentProject(name=name, **kwargs))

    def list_experiment_projects(self) -> Sequence[ExperimentProject]:
        return self._repo.list_experiment_projects()

    def create_experiment_view(
        self, experiment_project_id: int, name: str, **kwargs: Any
    ) -> ExperimentView:
        return self._repo.add(
            ExperimentView(experiment_project_id=experiment_project_id, name=name, **kwargs)
        )

    def list_experiment_views(
        self, experiment_project_id: int | None = None
    ) -> Sequence[ExperimentView]:
        return self._repo.list_experiment_views(experiment_project_id=experiment_project_id)

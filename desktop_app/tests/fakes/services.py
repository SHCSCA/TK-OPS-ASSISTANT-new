from __future__ import annotations

"""Concrete fake service implementations for pytest fixtures."""

from copy import deepcopy

from ...services.ai.config_service import AIModelDescriptor, ProviderSelection
from ...services.ai.provider_adapter import ProviderAdapter


def _clone_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return a typed deep copy for row-like payloads."""

    return deepcopy(rows)


class FakeAccountService:
    """Canned account service for tests."""

    service_name: str = "account"

    def __init__(self) -> None:
        self._accounts: list[dict[str, object]] = [
            {
                "account_id": "acct-001",
                "name": "Demo Shop",
                "status": "active",
                "region": "US",
            }
        ]

    def initialize(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def healthcheck(self) -> dict[str, object]:
        return {"service": self.service_name, "status": "ok"}

    def list_accounts(self) -> list[dict[str, object]]:
        return _clone_rows(self._accounts)

    def get_account_summary(self, account_id: str) -> dict[str, object]:
        for account in self._accounts:
            if account["account_id"] == account_id:
                return {
                    "account_id": account_id,
                    "orders": 0,
                    "revenue": 0.0,
                    "status": account["status"],
                }
        return {"account_id": account_id, "orders": 0, "revenue": 0.0, "status": "unknown"}


class FakeContentService:
    """Canned content service for tests."""

    service_name: str = "content"

    def __init__(self) -> None:
        self._assets: list[dict[str, object]] = [
            {
                "asset_id": "asset-001",
                "title": "Sample Product Clip",
                "status": "ready",
                "channel": "tiktok",
            }
        ]
        self._task_counter: int = 0

    def initialize(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def healthcheck(self) -> dict[str, object]:
        return {"service": self.service_name, "status": "ok"}

    def list_assets(self) -> list[dict[str, object]]:
        return _clone_rows(self._assets)

    def create_content_task(self, payload: dict[str, object]) -> str:
        self._task_counter += 1
        task_id = f"content-task-{self._task_counter:03d}"
        self._assets.append(
            {
                "asset_id": task_id,
                "title": str(payload.get("title", "Generated Content")),
                "status": "queued",
                "channel": str(payload.get("channel", "tiktok")),
            }
        )
        return task_id


class FakeAnalyticsService:
    """Canned analytics service for tests."""

    service_name: str = "analytics"

    def initialize(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def healthcheck(self) -> dict[str, object]:
        return {"service": self.service_name, "status": "ok"}

    def get_dashboard_metrics(self) -> dict[str, object]:
        return {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "ctr": 0.0,
        }

    def build_report(self, report_id: str) -> dict[str, object]:
        return {
            "report_id": report_id,
            "status": "ready",
            "rows": [],
            "summary": self.get_dashboard_metrics(),
        }


class FakeAutomationService:
    """Canned automation service for tests."""

    service_name: str = "automation"

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, object]] = {}
        self._job_counter: int = 0

    def initialize(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def healthcheck(self) -> dict[str, object]:
        return {"service": self.service_name, "status": "ok", "jobs": len(self._jobs)}

    def schedule_job(self, payload: dict[str, object]) -> str:
        self._job_counter += 1
        job_id = f"job-{self._job_counter:03d}"
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": "scheduled",
            "payload": deepcopy(payload),
        }
        return job_id

    def cancel_job(self, job_id: str) -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = "cancelled"


class FakeOperationsService:
    """Canned operations service for tests."""

    service_name: str = "operations"

    def __init__(self) -> None:
        self._work_items: list[dict[str, object]] = [
            {
                "work_item_id": "work-001",
                "title": "Review campaign health",
                "status": "pending",
            }
        ]

    def initialize(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def healthcheck(self) -> dict[str, object]:
        return {"service": self.service_name, "status": "ok"}

    def list_work_items(self) -> list[dict[str, object]]:
        return _clone_rows(self._work_items)

    def update_work_item_status(self, work_item_id: str, status: str) -> None:
        for work_item in self._work_items:
            if work_item["work_item_id"] == work_item_id:
                work_item["status"] = status
                break


class FakeAIConfigService:
    """Canned AI config service for tests."""

    service_name: str = "ai_config"

    def __init__(self, provider_name: str = "mock-provider", model_name: str = "mock-model") -> None:
        self._providers: dict[str, ProviderAdapter] = {}
        self._models: dict[str, list[AIModelDescriptor]] = {
            provider_name: [
                AIModelDescriptor(
                    provider_name=provider_name,
                    model_name=model_name,
                    display_name="Mock Model",
                    supports_streaming=False,
                )
            ]
        }
        self._active_selection: ProviderSelection = ProviderSelection(provider_name=provider_name, model_name=model_name)

    def initialize(self) -> None:
        return None

    def shutdown(self) -> None:
        return None

    def healthcheck(self) -> dict[str, object]:
        return {
            "service": self.service_name,
            "status": "ok",
            "active_provider": self._active_selection.provider_name,
            "active_model": self._active_selection.model_name,
        }

    def register_provider(self, adapter: ProviderAdapter) -> None:
        provider_name = getattr(adapter, "provider_name", adapter.__class__.__name__)
        self._providers[provider_name] = adapter
        _ = self._models.setdefault(
            provider_name,
            [
                AIModelDescriptor(
                    provider_name=provider_name,
                    model_name="default-model",
                    display_name=f"{provider_name} Default Model",
                )
            ],
        )

    def unregister_provider(self, provider_name: str) -> None:
        _ = self._providers.pop(provider_name, None)
        _ = self._models.pop(provider_name, None)
        if self._active_selection.provider_name == provider_name:
            fallback_provider = next(iter(self._models), "mock-provider")
            fallback_model = self._models.get(
                fallback_provider,
                [
                    AIModelDescriptor(
                        provider_name=fallback_provider,
                        model_name="mock-model",
                        display_name="Mock Model",
                        supports_streaming=False,
                    )
                ],
            )[0]
            self._active_selection = ProviderSelection(
                provider_name=fallback_provider,
                model_name=fallback_model.model_name,
            )

    def list_provider_names(self) -> list[str]:
        return sorted(self._models)

    def list_models(self, provider_name: str) -> list[AIModelDescriptor]:
        return list(self._models.get(provider_name, []))

    def get_active_selection(self) -> ProviderSelection:
        return self._active_selection

    def set_active_selection(self, selection: ProviderSelection) -> None:
        provider_models = self._models.setdefault(
            selection.provider_name,
            [
                AIModelDescriptor(
                    provider_name=selection.provider_name,
                    model_name=selection.model_name,
                    display_name=selection.model_name,
                    supports_streaming=False,
                )
            ],
        )
        if not any(model.model_name == selection.model_name for model in provider_models):
            provider_models.append(
                AIModelDescriptor(
                    provider_name=selection.provider_name,
                    model_name=selection.model_name,
                    display_name=selection.model_name,
                    supports_streaming=False,
                )
            )
        self._active_selection = selection


__all__ = [
    "FakeAccountService",
    "FakeContentService",
    "FakeAnalyticsService",
    "FakeAutomationService",
    "FakeOperationsService",
    "FakeAIConfigService",
]

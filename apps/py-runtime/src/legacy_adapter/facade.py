from __future__ import annotations

import datetime as dt
import logging
from typing import Any

from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService
from desktop_app.services.ai_service import AIService
from desktop_app.services.analytics_service import AnalyticsService
from desktop_app.services.chat_service import ChatService, get_preset, list_presets
from desktop_app.services.license_service import LicenseService
from desktop_app.services.task_service import TaskService
from desktop_app.services.usage_tracker import UsageTracker

from legacy_adapter.serializers import serialize_account, serialize_provider, serialize_task

log = logging.getLogger(__name__)


class LegacyRuntimeFacade:
    def get_license_status(self) -> dict[str, Any]:
        status = LicenseService().get_status()
        return {
            "activated": bool(status.get("activated")),
            "machineId": status.get("machine_id", ""),
            "machineIdShort": status.get("machine_id_short", ""),
            "compoundId": status.get("compound_id", ""),
            "tier": status.get("tier"),
            "expiry": status.get("expiry"),
            "daysRemaining": status.get("days_remaining"),
            "isPermanent": bool(status.get("is_permanent")),
            "error": status.get("error"),
        }

    def save_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        repo = Repository()
        try:
            updates = {
                "theme": self._read_payload_value(payload, "theme", default=repo.get_setting("theme", "system")),
                "language": self._read_payload_value(payload, "language", default=repo.get_setting("language", "zh-CN")),
                "network.proxy_url": self._read_payload_value(
                    payload,
                    "proxyUrl",
                    "proxy",
                    default=repo.get_setting("network.proxy_url", ""),
                ),
                "network.timeout_seconds": self._read_payload_value(
                    payload,
                    "timeoutSeconds",
                    "timeout",
                    default=repo.get_setting("network.timeout_seconds", "30"),
                ),
                "network.concurrent_requests": self._read_payload_value(
                    payload,
                    "concurrency",
                    "concurrencyLimit",
                    "concurrentRequests",
                    default=repo.get_setting("network.concurrent_requests", "3"),
                ),
            }
            for key, value in updates.items():
                repo.set_setting(key, value)
            snapshot = self._build_settings_snapshot(repo.get_all_settings())
            snapshot["savedKeys"] = list(updates.keys())
            snapshot["message"] = "设置已保存"
            return snapshot
        finally:
            repo.reset_session()

    def save_setup(self, payload: dict[str, Any]) -> dict[str, Any]:
        repo = Repository()
        try:
            updates = {
                "default_market": self._read_payload_value(
                    payload,
                    "defaultMarket",
                    "market",
                    default=repo.get_setting("default_market", repo.get_setting("primary_market", "")),
                ),
                "default_workflow": self._read_payload_value(
                    payload,
                    "workflow",
                    "defaultWorkflow",
                    default=repo.get_setting("default_workflow", repo.get_setting("workflow", "")),
                ),
                "onboarding.default_model": self._read_payload_value(
                    payload,
                    "model",
                    "defaultModel",
                    default=repo.get_setting("onboarding.default_model", ""),
                ),
                "onboarding.completed": "1" if self._read_payload_flag(payload, "completed", "done", default=True) else "0",
            }
            for key, value in updates.items():
                repo.set_setting(key, value)
            snapshot = self._build_settings_snapshot(repo.get_all_settings())
            snapshot["savedKeys"] = list(updates.keys())
            snapshot["message"] = "初始化向导已完成"
            return snapshot
        finally:
            repo.reset_session()

    def list_accounts(
        self,
        *,
        status: str | None = None,
        query: str | None = None,
        manual_status: str | None = None,
        system_status: str | None = None,
        risk_status: str | None = None,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        repo = Repository()
        try:
            service = AccountService(repo)
            accounts = service.list_accounts(
                status=status,
                query=query,
                manual_status=manual_status,
                system_status=system_status,
                risk_status=risk_status,
                include_archived=include_archived,
            )
            return [serialize_account(account) for account in accounts]
        finally:
            repo.reset_session()

    def list_providers(self) -> list[dict[str, Any]]:
        repo = Repository()
        try:
            service = AIService(repo)
            return [
                serialized
                for serialized in (serialize_provider(provider) for provider in service.list_providers())
                if serialized is not None
            ]
        finally:
            repo.reset_session()

    def create_provider(
        self,
        *,
        name: str,
        provider_type: str = "openai",
        api_base: str = "https://api.openai.com/v1",
        default_model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        is_active: bool = True,
    ) -> dict[str, Any]:
        repo = Repository()
        try:
            service = AIService(repo)
            provider = service.create_provider(
                name.strip(),
                provider_type=provider_type,
                api_base=api_base,
                default_model=default_model,
                temperature=temperature,
                max_tokens=max_tokens,
                is_active=is_active,
            )
            return serialize_provider(provider) or {}
        finally:
            repo.reset_session()

    def update_provider(
        self,
        provider_id: int,
        *,
        name: str,
        provider_type: str,
        api_base: str,
        default_model: str,
        temperature: float,
        max_tokens: int,
        is_active: bool,
    ) -> dict[str, Any] | None:
        repo = Repository()
        try:
            service = AIService(repo)
            provider = service.update_provider(
                provider_id,
                name=name.strip(),
                provider_type=provider_type,
                api_base=api_base,
                default_model=default_model,
                temperature=temperature,
                max_tokens=max_tokens,
                is_active=is_active,
            )
            return serialize_provider(provider)
        finally:
            repo.reset_session()

    def set_active_provider(self, provider_id: int) -> dict[str, Any] | None:
        repo = Repository()
        try:
            service = AIService(repo)
            provider = service.set_active(provider_id)
            return serialize_provider(provider)
        finally:
            repo.reset_session()

    def delete_provider(self, provider_id: int) -> bool:
        repo = Repository()
        try:
            service = AIService(repo)
            return service.delete_provider(provider_id)
        finally:
            repo.reset_session()

    def test_provider(self, provider_id: int) -> dict[str, Any]:
        repo = Repository()
        try:
            service = ChatService(repo)
            return service.test_provider(provider_id)
        finally:
            repo.reset_session()

    def list_tasks(self, *, status: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        repo = Repository()
        try:
            service = TaskService(repo)
            tasks = list(service.list_tasks(status=status))[: max(1, limit)]
            return [serialize_task(task) for task in tasks]
        finally:
            repo.reset_session()

    def get_settings(self) -> dict[str, Any]:
        repo = Repository()
        try:
            return self._build_settings_snapshot(repo.get_all_settings())
        finally:
            repo.reset_session()

    def get_scheduler_overview(self) -> dict[str, Any]:
        repo = Repository()
        try:
            settings = repo.get_all_settings()
            tasks = [serialize_task(task) for task in repo.list_tasks()]
            task_status = repo.count_tasks_by_status()
            scheduled_items = sorted(
                tasks,
                key=lambda item: (
                    item.get("scheduledAt") is None,
                    item.get("scheduledAt") or item.get("createdAt") or "",
                    item.get("id") or 0,
                ),
            )[:8]
            return {
                "generatedAt": dt.datetime.now().isoformat(),
                "summary": {
                    "total": len(tasks),
                    "scheduled": sum(1 for item in tasks if item.get("scheduledAt")),
                    "running": int(task_status.get("running", 0)),
                    "failed": int(task_status.get("failed", 0)),
                },
                "windows": {
                    "quietHours": settings.get("quiet_hours", "23:00-07:00"),
                    "timezone": settings.get("timezone", "Asia/Shanghai"),
                    "defaultWorkflow": (
                        settings.get("default_workflow")
                        or settings.get("workflow")
                        or "内容创作"
                    ),
                },
                "items": scheduled_items,
            }
        finally:
            repo.reset_session()

    def get_dashboard_overview(self) -> dict[str, Any]:
        repo = Repository()
        try:
            analytics = AnalyticsService(repo)
            provider_service = AIService(repo)
            summary = analytics.get_analytics_summary()
            settings = repo.get_all_settings()
            recent_tasks = [serialize_task(task) for task in repo.list_recent_tasks(limit=6)]
            active_provider = serialize_provider(provider_service.get_active_provider())
            regions = [
                {"key": key, "count": value}
                for key, value in sorted(
                    dict(summary["accounts"].get("by_region", {})).items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ]
            account_status = [
                {"key": key, "count": value}
                for key, value in sorted(repo.count_accounts_by_status().items(), key=lambda item: item[0])
            ]
            task_status = [
                {"key": key, "count": value}
                for key, value in sorted(repo.count_tasks_by_status().items(), key=lambda item: item[0])
            ]
            metrics = [
                {
                    "key": "accounts-total",
                    "label": "账号总数",
                    "value": int(summary["accounts"]["total"]),
                    "meta": f"活跃 {int(summary['accounts']['active'])}",
                },
                {
                    "key": "followers-total",
                    "label": "粉丝样本",
                    "value": int(summary["accounts"]["followers_total"]),
                    "meta": f"地区 {len(regions)}",
                },
                {
                    "key": "tasks-total",
                    "label": "任务总数",
                    "value": int(summary["tasks"]["total"]),
                    "meta": f"运行中 {int(summary['tasks']['running'])}",
                },
                {
                    "key": "assets-total",
                    "label": "素材总数",
                    "value": int(summary["assets"]["total"]),
                    "meta": f"AI 提供方 {int(summary['providers']['active'])}",
                },
            ]
            return {
                "generatedAt": dt.datetime.now().isoformat(),
                "metrics": metrics,
                "accountStatus": account_status,
                "taskStatus": task_status,
                "regions": regions,
                "recentTasks": recent_tasks,
                "activeProvider": active_provider,
                "settingsSummary": {
                    "theme": settings.get("theme", "system"),
                    "total": len(settings),
                },
            }
        finally:
            repo.reset_session()

    def get_copywriter_bootstrap(self) -> dict[str, Any]:
        repo = Repository()
        try:
            ai_service = AIService(repo)
            usage = UsageTracker(repo)
            providers = [
                serialized
                for serialized in (serialize_provider(provider) for provider in ai_service.list_providers())
                if serialized is not None
            ]
            return {
                "presets": list_presets(),
                "defaultPreset": "copywriter",
                "activePreset": get_preset("copywriter"),
                "providers": providers,
                "activeProvider": serialize_provider(ai_service.get_active_provider()),
                "usageToday": usage.get_today(),
                "usageStats": usage.get_stats(),
            }
        finally:
            repo.reset_session()

    def stream_copywriter(
        self,
        *,
        prompt: str,
        preset_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        repo = Repository()
        try:
            chat = ChatService(repo)
            usage = UsageTracker(repo)
            messages = [{"role": "user", "content": prompt}]
            for chunk in chat.chat_stream(
                messages=messages,
                model=model,
                preset_key=preset_key or "copywriter",
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                if chunk.done:
                    if chunk.prompt_tokens:
                        usage.record(
                            chunk.provider_name,
                            chunk.model,
                            chunk.prompt_tokens,
                            chunk.completion_tokens,
                        )
                    yield {
                        "type": "ai.stream.done",
                        "payload": {
                            "delta": chunk.delta,
                            "content": chunk.content,
                            "model": chunk.model,
                            "provider": chunk.provider_name,
                            "tokens": {
                                "prompt": chunk.prompt_tokens,
                                "completion": chunk.completion_tokens,
                                "total": chunk.total_tokens,
                            },
                            "elapsedMs": chunk.elapsed_ms,
                        },
                    }
                elif chunk.delta:
                    yield {
                        "type": "ai.stream.delta",
                        "payload": {"delta": chunk.delta},
                    }
        except Exception as exc:
            log.exception("AI 文案流式生成失败")
            yield {
                "type": "ai.stream.error",
                "payload": {"message": str(exc)},
            }
        finally:
            repo.reset_session()

    def _build_settings_snapshot(self, values: dict[str, str]) -> dict[str, Any]:
        items = [
            {"key": key, "value": value}
            for key, value in sorted(values.items(), key=lambda item: item[0])
        ]
        theme = values.get("theme", "system")
        timeout_seconds = self._safe_int(values.get("network.timeout_seconds"), 30)
        concurrency = self._safe_int(values.get("network.concurrent_requests"), 3)
        return {
            "values": values,
            "items": items,
            "theme": theme,
            "total": len(items),
            "preferences": {
                "theme": theme,
                "language": values.get("language", "zh-CN"),
                "proxyUrl": values.get("network.proxy_url", ""),
                "timeoutSeconds": timeout_seconds,
                "concurrency": concurrency,
            },
            "setup": {
                "defaultMarket": values.get("default_market") or values.get("primary_market") or "",
                "defaultWorkflow": values.get("default_workflow") or values.get("workflow") or "",
                "defaultModel": values.get("onboarding.default_model") or "",
                "completed": self._is_truthy(values.get("onboarding.completed")),
            },
        }

    def _read_payload_value(self, payload: dict[str, Any], *keys: str, default: Any = "") -> str:
        for key in keys:
            if key in payload:
                value = payload.get(key)
                return "" if value is None else str(value)
        return "" if default is None else str(default)

    def _read_payload_flag(self, payload: dict[str, Any], *keys: str, default: bool = False) -> bool:
        for key in keys:
            if key in payload:
                return self._is_truthy(payload.get(key))
        return default

    def _safe_int(self, value: Any, default: int) -> int:
        try:
            if value is None or value == "":
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    def _is_truthy(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        return str(value).strip().lower() in {"1", "true", "yes", "on", "completed"}

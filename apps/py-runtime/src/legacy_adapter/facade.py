from __future__ import annotations

import datetime as dt
import json
import logging
from typing import Any

from desktop_app.database.repository import Repository
from desktop_app.services.account_service import AccountService
from desktop_app.services.activity_service import ActivityService
from desktop_app.services.ai_service import AIService
from desktop_app.services.analytics_service import AnalyticsService
from desktop_app.services.chat_service import ChatService, get_preset, list_presets
from desktop_app.services.license_service import LicenseService
from desktop_app.services.task_service import TaskService
from desktop_app.services.updater_service import UpdaterService
from desktop_app.services.usage_tracker import UsageTracker
from desktop_app.version import APP_VERSION

from legacy_adapter.serializers import serialize_account, serialize_provider, serialize_task

log = logging.getLogger(__name__)


class LegacyRuntimeFacade:
    def __init__(self) -> None:
        self._updater = UpdaterService()

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

    def get_dashboard_overview(self, range_key: str = "today") -> dict[str, Any]:
        repo = Repository()
        try:
            analytics = AnalyticsService(repo)
            provider_service = AIService(repo)
            summary = analytics.get_analytics_summary()
            settings = repo.get_all_settings()
            now = dt.datetime.now()
            normalized_range, range_start, range_end, range_label = self._resolve_dashboard_range(range_key, now)
            recent_tasks = [serialize_task(task) for task in repo.list_recent_tasks(limit=6)]
            active_provider = serialize_provider(provider_service.get_active_provider())
            account_status_map = repo.count_accounts_by_status()
            task_status_map = repo.count_tasks_by_status()
            regions = [
                {"key": key, "count": value}
                for key, value in sorted(
                    dict(summary["accounts"].get("by_region", {})).items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ]
            account_status = [
                {"key": key, "count": value}
                for key, value in sorted(account_status_map.items(), key=lambda item: item[0])
            ]
            task_status = [
                {"key": key, "count": value}
                for key, value in sorted(task_status_map.items(), key=lambda item: item[0])
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
                    "meta": f"AI 提供商 {int(summary['providers']['active'])}",
                },
            ]
            trend = [
                {
                    "label": range_label,
                    "created": int(repo.count_tasks_created_between(range_start, range_end)),
                    "completed": int(repo.count_tasks_completed_between(range_start, range_end)),
                    "failed": int(repo.count_tasks_failed_between(range_start, range_end)),
                }
            ]
            activity = [
                self._serialize_dashboard_activity_row(item)
                for item in repo.list_recent_activity_logs(limit=12)
            ]
            systems = self._build_dashboard_systems(
                summary=summary,
                account_status_map=account_status_map,
                task_status_map=task_status_map,
                active_provider=active_provider,
            )
            stats = {
                "accounts": {
                    "total": int(summary["accounts"]["total"]),
                    "active": int(summary["accounts"]["active"]),
                    "byStatus": account_status_map,
                },
                "tasks": {
                    "total": int(summary["tasks"]["total"]),
                    "running": int(summary["tasks"]["running"]),
                    "failed": int(summary["tasks"]["failed"]),
                    "byStatus": task_status_map,
                },
                "providers": int(summary["providers"]["active"]),
            }
            return {
                "generatedAt": now.isoformat(),
                "range": normalized_range,
                "metrics": metrics,
                "accountStatus": account_status,
                "taskStatus": task_status,
                "regions": regions,
                "recentTasks": recent_tasks,
                "trend": trend,
                "activity": activity,
                "systems": systems,
                "stats": stats,
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

    def list_notifications(self, *, limit: int = 20) -> list[dict[str, Any]]:
        repo = Repository()
        try:
            service = ActivityService(repo)
            rows = service.list_notifications(limit=max(1, min(int(limit), 50)))
            return [
                {
                    "id": row.get("id"),
                    "title": row.get("title", ""),
                    "body": row.get("body", ""),
                    "tone": row.get("tone", "info"),
                    "createdAt": row.get("created_at", ""),
                    "source": row.get("source", "activity"),
                    "read": False,
                }
                for row in rows
            ]
        finally:
            repo.reset_session()

    def get_app_version(self) -> dict[str, Any]:
        return {"version": APP_VERSION}

    def check_for_update(self) -> dict[str, Any]:
        info = self._updater.check_update()
        if info is None:
            return {
                "hasUpdate": False,
                "state": "latest",
                "current": APP_VERSION,
                "latest": APP_VERSION,
            }
        state = "available" if info.has_update else "latest"
        return {
            "hasUpdate": info.has_update,
            "state": state,
            "current": APP_VERSION,
            "latest": info.version,
            "tag": info.tag,
            "downloadUrl": info.download_url,
            "htmlUrl": info.html_url,
            "releaseNotes": info.body,
            "assetName": info.asset_name,
            "assetSize": info.asset_size,
        }

    def chat_shell_assistant(
        self,
        *,
        message: str,
        context: dict[str, Any] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        normalized_message = (message or "").strip()
        context_payload = context or {}
        suggestions = self._build_shell_suggestions(normalized_message, context_payload)

        if not normalized_message:
            return {
                "answer": "请先输入你的问题，我会结合当前页面给出建议。",
                "suggestions": suggestions,
                "source": "fallback",
                "contextEcho": context_payload,
            }

        repo = Repository()
        try:
            chat = ChatService(repo)
            usage = UsageTracker(repo)
            system_prompt = self._build_shell_assistant_system_prompt(context_payload)
            history_messages = self._normalize_chat_history(history)
            messages = [
                {"role": "system", "content": system_prompt},
                *history_messages[-8:],
                {"role": "user", "content": normalized_message},
            ]
            result = chat.chat(messages=messages, preset_key="copywriter")
            if result.prompt_tokens:
                usage.record(
                    result.provider_name,
                    result.model,
                    result.prompt_tokens,
                    result.completion_tokens,
                )
            answer = (result.content or "").strip()
            if not answer:
                answer = self._build_shell_assistant_fallback(normalized_message, context_payload)
            return {
                "answer": answer,
                "suggestions": suggestions,
                "source": "model",
                "model": result.model,
                "provider": result.provider_name,
                "elapsedMs": result.elapsed_ms,
                "contextEcho": context_payload,
            }
        except Exception as exc:
            log.warning("shell assistant fallback: %s", exc)
            return {
                "answer": self._build_shell_assistant_fallback(normalized_message, context_payload),
                "suggestions": suggestions,
                "source": "fallback",
                "error": str(exc),
                "contextEcho": context_payload,
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

    def _normalize_chat_history(self, history: list[dict[str, Any]] | None) -> list[dict[str, str]]:
        if not history:
            return []
        normalized: list[dict[str, str]] = []
        for item in history:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "").strip().lower()
            content = str(item.get("content") or "").strip()
            if role not in {"user", "assistant"} or not content:
                continue
            normalized.append({"role": role, "content": content})
        return normalized

    def _build_shell_assistant_system_prompt(self, context: dict[str, Any]) -> str:
        route_name = str(context.get("routeName") or "")
        route_title = str(context.get("routeTitle") or "")
        runtime_status = str(context.get("runtimeStatus") or "")
        shell_summary = str(context.get("routeSummary") or "")
        notifications = str(context.get("notificationSummary") or "")
        return (
            "你是 TK-OPS 桌面壳层 AI 助手。"
            "回答要简洁、可执行、中文优先。"
            "只提供壳层级建议，不要虚构后端数据。"
            f"\n当前页面: {route_name} / {route_title}"
            f"\n页面摘要: {shell_summary}"
            f"\nRuntime: {runtime_status}"
            f"\n通知摘要: {notifications}"
            "\n如果用户问题不明确，先给1-2条最可能可执行建议。"
        )

    def _build_shell_assistant_fallback(self, message: str, context: dict[str, Any]) -> str:
        route_title = str(context.get("routeTitle") or "当前页面")
        if "通知" in message:
            return "你可以先打开通知中心，优先处理未读告警，再回到当前页面继续操作。"
        if "主题" in message or "深色" in message or "浅色" in message:
            return "可以直接使用顶部主题按钮切换明暗主题，切换后会自动持久化到设置。"
        if "右栏" in message or "详情" in message:
            return "你可以先展开右侧详情区查看页面摘要和运行状态，再决定下一步动作。"
        return f"我建议先在“{route_title}”确认当前状态，再使用顶部搜索或快捷动作完成下一步。"

    def _build_shell_suggestions(
        self,
        message: str,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        route_name = str(context.get("routeName") or "")
        base = [
            {"id": "open-notifications", "label": "打开通知中心", "action": "open_notifications"},
            {"id": "toggle-theme", "label": "切换主题", "action": "toggle_theme"},
            {"id": "toggle-detail", "label": "切换右栏", "action": "toggle_detail_panel"},
            {"id": "refresh-page", "label": "刷新当前页", "action": "refresh_current_page"},
        ]
        if route_name:
            base.insert(
                0,
                {
                    "id": "route-focus",
                    "label": "聚焦当前页面",
                    "action": "focus_route",
                    "payload": {"routeName": route_name},
                },
            )

        if "通知" in message:
            return [
                {
                    "id": "open-notifications",
                    "label": "查看未读通知",
                    "action": "open_notifications",
                },
                *[item for item in base if item["id"] != "open-notifications"],
            ][:5]
        if "主题" in message or "深色" in message or "浅色" in message:
            return [
                {"id": "toggle-theme", "label": "立即切换主题", "action": "toggle_theme"},
                *[item for item in base if item["id"] != "toggle-theme"],
            ][:5]
        if "右栏" in message or "详情" in message:
            return [
                {"id": "toggle-detail", "label": "展开/收起右栏", "action": "toggle_detail_panel"},
                *[item for item in base if item["id"] != "toggle-detail"],
            ][:5]
        return base[:5]

    def _resolve_dashboard_range(
        self,
        range_key: str | None,
        now: dt.datetime,
    ) -> tuple[str, dt.datetime, dt.datetime, str]:
        normalized = str(range_key or "today").strip().lower()
        if normalized not in {"today", "7d", "30d"}:
            normalized = "today"
        if normalized == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return normalized, start, now, "今日汇总"
        if normalized == "7d":
            return normalized, now - dt.timedelta(days=7), now, "近7天汇总"
        return normalized, now - dt.timedelta(days=30), now, "近30天汇总"

    def _serialize_dashboard_activity_row(self, item: Any) -> dict[str, str]:
        payload = self._safe_payload_json(getattr(item, "payload_json", None))
        category = str(getattr(item, "category", "") or payload.get("category") or "activity")
        entity = str(getattr(item, "related_entity_type", "") or payload.get("entity") or "activity")
        status = self._derive_dashboard_activity_status(category, payload)
        created_at = self._format_dashboard_time(getattr(item, "created_at", None))
        return {
            "title": str(getattr(item, "title", "") or payload.get("title") or "未命名活动"),
            "entity": entity,
            "category": category,
            "status": status,
            "time": created_at,
        }

    def _safe_payload_json(self, raw: Any) -> dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        if not raw:
            return {}
        try:
            parsed = json.loads(str(raw))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _derive_dashboard_activity_status(self, category: str, payload: dict[str, Any]) -> str:
        payload_status = str(payload.get("status") or "").strip()
        if payload_status:
            return payload_status
        normalized = category.lower()
        if any(token in normalized for token in ("error", "failed", "exception", "risk", "archive")):
            return "异常"
        if any(token in normalized for token in ("warn", "pending", "review", "delay")):
            return "关注"
        return "正常"

    def _build_dashboard_systems(
        self,
        *,
        summary: dict[str, Any],
        account_status_map: dict[str, int],
        task_status_map: dict[str, int],
        active_provider: dict[str, Any] | None,
    ) -> list[dict[str, str]]:
        failed_count = int(task_status_map.get("failed", 0))
        running_count = int(task_status_map.get("running", 0))
        queued_count = int(task_status_map.get("pending", 0))
        provider_active = int(summary["providers"]["active"])
        provider_total = int(summary["providers"]["total"])
        account_total = int(summary["accounts"]["total"])
        account_active = int(summary["accounts"]["active"])

        task_tone = "error" if failed_count > 0 else ("warning" if queued_count > 0 else "success")
        task_status = "异常" if failed_count > 0 else ("排队中" if queued_count > 0 else "正常")

        provider_tone = "success" if provider_active > 0 else "warning"
        provider_status = "已接入" if provider_active > 0 else "未接入"

        account_tone = "warning" if account_total > 0 and account_active == 0 else "success"
        account_status = "正常" if account_active > 0 else ("待检查" if account_total > 0 else "空")

        runtime_status = "在线" if active_provider is not None or provider_total >= 0 else "未知"
        return [
            {
                "key": "runtime",
                "title": "Runtime 状态",
                "status": runtime_status,
                "tone": "success",
                "summary": "dashboard 聚合链路已连接运行时。",
            },
            {
                "key": "tasks",
                "title": "任务执行状态",
                "status": task_status,
                "tone": task_tone,
                "summary": f"运行中 {running_count} / 排队 {queued_count} / 异常 {failed_count}",
            },
            {
                "key": "providers",
                "title": "AI 供应商接入",
                "status": provider_status,
                "tone": provider_tone,
                "summary": f"启用 {provider_active} / 总计 {provider_total}",
            },
            {
                "key": "accounts",
                "title": "账号同步准备",
                "status": account_status,
                "tone": account_tone,
                "summary": f"账号 {account_total} / 活跃 {account_active}",
            },
        ]

    def _format_dashboard_time(self, value: Any) -> str:
        if isinstance(value, dt.datetime):
            return value.isoformat()
        return str(value or "")

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


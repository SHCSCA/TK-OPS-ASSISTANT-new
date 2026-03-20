"""AI usage stats — track token consumption per provider/model/preset."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from desktop_app.database.repository import Repository

log = logging.getLogger(__name__)

_SETTING_KEY = "ai_usage_stats"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class UsageTracker:
    """Accumulates AI usage stats in AppSetting as JSON.

    Schema: {
        "total": {"prompt": N, "completion": N, "requests": N},
        "daily": {"2026-03-19": {"prompt": N, "completion": N, "requests": N}},
        "by_provider": {"OpenAI": {"prompt": N, "completion": N, "requests": N}},
        "by_model": {"gpt-4o-mini": {"prompt": N, "completion": N, "requests": N}},
    }
    """

    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def _load(self) -> dict:
        raw = self._repo.get_setting(_SETTING_KEY, "{}")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _save(self, data: dict) -> None:
        self._repo.set_setting(_SETTING_KEY, json.dumps(data, ensure_ascii=False))

    def record(
        self,
        provider_name: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        data = self._load()
        today = _now_iso()

        # total
        t = data.setdefault("total", {"prompt": 0, "completion": 0, "requests": 0})
        t["prompt"] += prompt_tokens
        t["completion"] += completion_tokens
        t["requests"] += 1

        # daily
        d = data.setdefault("daily", {}).setdefault(today, {"prompt": 0, "completion": 0, "requests": 0})
        d["prompt"] += prompt_tokens
        d["completion"] += completion_tokens
        d["requests"] += 1

        # by provider
        p = data.setdefault("by_provider", {}).setdefault(provider_name, {"prompt": 0, "completion": 0, "requests": 0})
        p["prompt"] += prompt_tokens
        p["completion"] += completion_tokens
        p["requests"] += 1

        # by model
        m = data.setdefault("by_model", {}).setdefault(model, {"prompt": 0, "completion": 0, "requests": 0})
        m["prompt"] += prompt_tokens
        m["completion"] += completion_tokens
        m["requests"] += 1

        self._save(data)

    def get_stats(self) -> dict:
        data = self._load()
        return {
            "total": data.get("total", {"prompt": 0, "completion": 0, "requests": 0}),
            "daily": data.get("daily", {}),
            "by_provider": data.get("by_provider", {}),
            "by_model": data.get("by_model", {}),
        }

    def get_today(self) -> dict:
        data = self._load()
        today = _now_iso()
        return data.get("daily", {}).get(today, {"prompt": 0, "completion": 0, "requests": 0})

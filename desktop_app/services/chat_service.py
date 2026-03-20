"""Unified AI chat service — multi-provider, streaming, fallback chain.

Uses the official openai SDK which supports OpenAI-compatible APIs:
  - OpenAI native
  - Anthropic (via proxy or compatible endpoint)
  - Ollama (local)
  - Any OpenAI-compatible custom API

All providers configured as AIProvider records in DB.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Generator

from openai import OpenAI

from desktop_app.database.models import AIProvider
from desktop_app.database.repository import Repository

log = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str       # system | user | assistant
    content: str


@dataclass
class ChatResult:
    content: str
    model: str
    provider_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    elapsed_ms: int = 0
    finished: bool = True


@dataclass
class StreamChunk:
    """One piece of a streaming response."""
    delta: str          # text fragment
    done: bool = False  # True → last chunk
    # Final chunk carries usage info
    content: str = ""
    model: str = ""
    provider_name: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    elapsed_ms: int = 0


# ── Presets (system prompt templates) ────────────

PRESETS: dict[str, dict] = {
    "default": {
        "name": "通用助手",
        "icon": "🤖",
        "system": "你是 TK-OPS 运营助手，帮助用户处理 TikTok Shop 运营相关问题。回答简洁、专业、有可操作性。",
    },
    "title-generator": {
        "name": "爆款标题大师",
        "icon": "🔥",
        "system": (
            "你是一位 TikTok Shop 爆款标题专家。用户会给你产品信息，你需要：\n"
            "1. 生成 5-8 个吸引点击的标题变体\n"
            "2. 每个标题标注预估点击率(高/中/低)\n"
            "3. 给出标题优化建议\n"
            "保持标题简短有力，善用数字、emoji 和紧迫感词汇。"
        ),
    },
    "copywriter": {
        "name": "AI 文案师",
        "icon": "✍️",
        "system": (
            "你是一位专业的电商文案撰写专家。根据用户提供的产品信息，生成：\n"
            "1. 产品卖点摘要 (3-5 条)\n"
            "2. 短视频文案 (15 秒/30 秒/60 秒版本)\n"
            "3. 详情页描述\n"
            "文案要有感染力，突出用户受益点，符合 TikTok 平台调性。"
        ),
    },
    "script-extractor": {
        "name": "脚本提取器",
        "icon": "📜",
        "system": (
            "你是一位短视频脚本分析师。用户会提供视频文案或描述，你需要：\n"
            "1. 提取脚本结构 (开头hook/主体/结尾CTA)\n"
            "2. 标注时间轴和镜头建议\n"
            "3. 分析可复用的话术模板\n"
            "输出结构化，便于用户直接套用。"
        ),
    },
    "reply-bot": {
        "name": "智能客服",
        "icon": "💬",
        "system": (
            "你是 TikTok Shop 的智能客服助手。根据买家消息：\n"
            "1. 判断意图 (咨询/售后/投诉/催单)\n"
            "2. 生成专业且友好的回复\n"
            "3. 标注是否需要人工介入\n"
            "回复要简短、有温度，避免模板感。"
        ),
    },
    "data-analyst": {
        "name": "数据分析师",
        "icon": "📊",
        "system": (
            "你是一位电商数据分析专家。根据用户提供的运营数据：\n"
            "1. 给出关键指标解读\n"
            "2. 发现数据异常和机会点\n"
            "3. 提出可执行的优化建议\n"
            "用数据说话，结论要具体、可量化。"
        ),
    },
    "content-planner": {
        "name": "内容策划",
        "icon": "📅",
        "system": (
            "你是一位 TikTok 内容策划专家。帮助用户：\n"
            "1. 制定内容日历和发布计划\n"
            "2. 选题方向建议和热点追踪\n"
            "3. 内容矩阵规划 (教程/测评/日常/直播)\n"
            "注重内容节奏和平台算法偏好。"
        ),
    },
    "seo-optimizer": {
        "name": "SEO 优化师",
        "icon": "🔍",
        "system": (
            "你是 TikTok Shop SEO 和标签优化专家。帮助用户：\n"
            "1. 优化商品标题关键词\n"
            "2. 推荐最佳标签组合\n"
            "3. 分析搜索排名改进空间\n"
            "注重长尾关键词和搜索意图匹配。"
        ),
    },
    "competitor-analyst": {
        "name": "竞品分析师",
        "icon": "🕵️",
        "system": (
            "你是一位 TikTok Shop 竞品分析专家。帮助用户：\n"
            "1. 分析竞品的定价、文案、视频策略\n"
            "2. 发现差异化机会\n"
            "3. 给出应对策略建议\n"
            "分析要客观、有数据支撑。"
        ),
    },
}


def list_presets() -> list[dict]:
    """Return all presets as a list of dicts for the frontend."""
    return [
        {"key": k, "name": v["name"], "icon": v["icon"], "system": v["system"]}
        for k, v in PRESETS.items()
    ]


def get_preset(key: str) -> dict | None:
    p = PRESETS.get(key)
    if p is None:
        return None
    return {"key": key, **p}


# ── Client factory ───────────────────────────────

def _build_client(provider: AIProvider) -> OpenAI:
    """Create an OpenAI client configured for the given provider."""
    return OpenAI(
        api_key=provider.api_key_encrypted or "sk-placeholder",
        base_url=provider.api_base,
        timeout=60.0,
    )


# ── Chat service ─────────────────────────────────

class ChatService:
    """Stateless chat completion service with streaming and fallback."""

    def __init__(self, repo: Repository | None = None) -> None:
        self._repo = repo or Repository()

    def _get_providers(self) -> list[AIProvider]:
        """Get providers ordered: active first, then others as fallback."""
        all_p = list(self._repo.list_all(AIProvider))
        active = [p for p in all_p if p.is_active]
        inactive = [p for p in all_p if not p.is_active]
        return active + inactive

    # ── Sync (non-streaming) ─────────────────────

    def chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        preset_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResult:
        """Send a chat completion. Tries providers in fallback order."""
        msgs = self._inject_preset(messages, preset_key)
        providers = self._get_providers()
        if not providers:
            return ChatResult(content="未配置 AI 供应商，请先在「AI 供应商配置」页面添加。",
                              model="", provider_name="", finished=True)

        last_error = ""
        for provider in providers:
            try:
                return self._do_chat(provider, msgs, model, temperature, max_tokens)
            except Exception as exc:
                last_error = f"{provider.name}: {exc}"
                log.warning("Provider %s failed: %s", provider.name, exc)

        return ChatResult(content=f"所有供应商均失败。最后错误: {last_error}",
                          model="", provider_name="", finished=True)

    def _do_chat(
        self,
        provider: AIProvider,
        messages: list[dict],
        model: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> ChatResult:
        client = _build_client(provider)
        t0 = time.monotonic()
        resp = client.chat.completions.create(
            model=model or provider.default_model,
            messages=messages,
            temperature=temperature if temperature is not None else provider.temperature,
            max_tokens=max_tokens or provider.max_tokens,
            stream=False,
        )
        elapsed = int((time.monotonic() - t0) * 1000)
        choice = resp.choices[0] if resp.choices else None
        usage = resp.usage
        return ChatResult(
            content=choice.message.content if choice else "",
            model=resp.model or provider.default_model,
            provider_name=provider.name,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            elapsed_ms=elapsed,
        )

    # ── Streaming ────────────────────────────────

    def chat_stream(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        preset_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Generator[StreamChunk, None, None]:
        """Stream chat completions. Tries providers in fallback order."""
        msgs = self._inject_preset(messages, preset_key)
        providers = self._get_providers()
        if not providers:
            yield StreamChunk(delta="未配置 AI 供应商，请先在「AI 供应商配置」页面添加。", done=True)
            return

        last_error = ""
        for provider in providers:
            try:
                yield from self._do_stream(provider, msgs, model, temperature, max_tokens)
                return
            except Exception as exc:
                last_error = f"{provider.name}: {exc}"
                log.warning("Provider %s stream failed: %s", provider.name, exc)

        yield StreamChunk(delta=f"所有供应商均失败。最后错误: {last_error}", done=True)

    def _do_stream(
        self,
        provider: AIProvider,
        messages: list[dict],
        model: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> Generator[StreamChunk, None, None]:
        client = _build_client(provider)
        t0 = time.monotonic()
        stream = client.chat.completions.create(
            model=model or provider.default_model,
            messages=messages,
            temperature=temperature if temperature is not None else provider.temperature,
            max_tokens=max_tokens or provider.max_tokens,
            stream=True,
            stream_options={"include_usage": True},
        )
        collected = []
        usage_data = {"prompt": 0, "completion": 0, "total": 0}

        for chunk in stream:
            if chunk.usage:
                usage_data["prompt"] = chunk.usage.prompt_tokens or 0
                usage_data["completion"] = chunk.usage.completion_tokens or 0
                usage_data["total"] = chunk.usage.total_tokens or 0

            delta_content = ""
            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    delta_content = delta.content
                    collected.append(delta_content)

                finish = chunk.choices[0].finish_reason
                if finish:
                    elapsed = int((time.monotonic() - t0) * 1000)
                    yield StreamChunk(
                        delta=delta_content,
                        done=True,
                        content="".join(collected),
                        model=chunk.model or provider.default_model,
                        provider_name=provider.name,
                        prompt_tokens=usage_data["prompt"],
                        completion_tokens=usage_data["completion"],
                        total_tokens=usage_data["total"],
                        elapsed_ms=elapsed,
                    )
                    return

            if delta_content:
                yield StreamChunk(delta=delta_content)

        # If we got here without finish_reason, still close out
        elapsed = int((time.monotonic() - t0) * 1000)
        yield StreamChunk(
            delta="",
            done=True,
            content="".join(collected),
            model=provider.default_model,
            provider_name=provider.name,
            prompt_tokens=usage_data["prompt"],
            completion_tokens=usage_data["completion"],
            total_tokens=usage_data["total"],
            elapsed_ms=elapsed,
        )

    # ── Provider health check ────────────────────

    def test_provider(self, provider_id: int) -> dict:
        """Quick connectivity test for a provider."""
        provider = self._repo.get_by_id(AIProvider, provider_id)
        if not provider:
            return {"ok": False, "error": "供应商不存在"}
        try:
            client = _build_client(provider)
            t0 = time.monotonic()
            resp = client.chat.completions.create(
                model=provider.default_model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                stream=False,
            )
            elapsed = int((time.monotonic() - t0) * 1000)
            return {
                "ok": True,
                "model": resp.model,
                "latency_ms": elapsed,
                "provider": provider.name,
            }
        except Exception as exc:
            return {"ok": False, "error": str(exc), "provider": provider.name}

    # ── Helpers ───────────────────────────────────

    @staticmethod
    def _inject_preset(messages: list[dict], preset_key: str | None) -> list[dict]:
        """Prepend system prompt from preset if not already present."""
        if not preset_key:
            return messages
        preset = PRESETS.get(preset_key)
        if not preset:
            return messages
        # Don't duplicate system msg
        if messages and messages[0].get("role") == "system":
            return messages
        return [{"role": "system", "content": preset["system"]}] + messages

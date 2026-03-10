from __future__ import annotations

from typing import Callable, Dict, Mapping, Optional, cast

from ....services.ai import streaming as streaming_module
from ....services.ai.streaming import StreamingAIRuntime

setattr(streaming_module, "Mapping", Mapping)

UsageDict = Dict[str, int]
UsageExtractor = Callable[[Mapping[str, object]], Optional[UsageDict]]

coerce_int = cast(Callable[[object], int], getattr(streaming_module, "_coerce_int"))
empty_usage = cast(Callable[[], UsageDict], getattr(streaming_module, "_empty_usage"))
extract_usage = cast(UsageExtractor, getattr(streaming_module, "_extract_usage"))
normalize_usage = cast(UsageExtractor, getattr(streaming_module, "_normalize_usage"))


def test_streaming_runtime_instantiates() -> None:
    runtime = StreamingAIRuntime()

    assert runtime.service_name == "ai_runtime"
    assert runtime.is_streaming() is False
    assert runtime.get_usage_stats() == empty_usage()


def test_coerce_int_various_inputs() -> None:
    assert coerce_int(True) == 1
    assert coerce_int(False) == 0
    assert coerce_int(7) == 7
    assert coerce_int(-4) == 0
    assert coerce_int(3.9) == 3
    assert coerce_int(" 12 ") == 12
    assert coerce_int("7.8") == 7
    assert coerce_int("invalid") == 0
    assert coerce_int(None) == 0


def test_empty_usage_structure() -> None:
    usage = empty_usage()

    assert usage == {
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
    }


def test_normalize_usage_valid_mapping() -> None:
    usage = normalize_usage({"prompt_tokens": "12", "completion_tokens": 8, "total_tokens": 0})

    assert usage == {
        "total_tokens": 20,
        "prompt_tokens": 12,
        "completion_tokens": 8,
    }


def test_normalize_usage_empty_returns_none() -> None:
    assert normalize_usage({}) is None
    assert normalize_usage({"other": 1}) is None


def test_extract_usage_from_payload() -> None:
    payload = {
        "choices": [{"delta": {"content": "hello"}}],
        "meta": {
            "usage": {
                "prompt_tokens": "5",
                "completion_tokens": 9,
                "total_tokens": 0,
            }
        },
    }

    assert extract_usage(payload) == {
        "total_tokens": 14,
        "prompt_tokens": 5,
        "completion_tokens": 9,
    }


def test_extract_usage_direct_top_level_usage_fields() -> None:
    payload = {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5}

    assert extract_usage(payload) == {
        "total_tokens": 5,
        "prompt_tokens": 2,
        "completion_tokens": 3,
    }

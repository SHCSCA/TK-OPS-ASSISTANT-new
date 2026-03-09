from __future__ import annotations

"""LiteLLM 通用 ProviderAdapter 适配器实现。"""

# pyright: basic, reportMissingImports=false, reportImplicitOverride=false

import os
from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol, cast

from ....core.logger import get_logger
from ....core.security.secret_store import SecretStore
from ..provider_adapter import MessagePayload, ProviderAdapter, ResponsePayload

logger = get_logger(__name__)


class LiteLLMAdapter(ProviderAdapter):
    """通过 LiteLLM 统一封装多提供商推理调用。"""

    provider_name: str
    api_key: str | None
    api_base: str | None
    custom_headers: dict[str, str] | None

    _DEFAULT_SECRET_SERVICE: str = "ai.providers"
    _known_models: tuple[str, ...]
    _requires_api_key: bool
    _requires_api_base: bool
    _litellm_provider: str | None
    _secret_store: SecretStore | None
    _secret_service: str
    _secret_key_name: str
    _default_env_var: str
    _request_timeout: float

    def __init__(
        self,
        provider_name: str,
        api_key: str | None = None,
        api_base: str | None = None,
        custom_headers: Mapping[str, str] | None = None,
        *,
        known_models: Sequence[str] | None = None,
        requires_api_key: bool = True,
        requires_api_base: bool = False,
        litellm_provider: str | None = None,
        secret_store: SecretStore | None = None,
        secret_service: str | None = None,
        secret_key_name: str | None = None,
        default_env_var: str | None = None,
        request_timeout: float = 60.0,
    ) -> None:
        self.provider_name = provider_name
        self.api_key = self._normalize_string(api_key)
        self.api_base = self._normalize_string(api_base)
        self.custom_headers = self._normalize_headers(custom_headers)
        self._known_models = tuple(model.strip() for model in (known_models or ()) if model.strip())
        self._requires_api_key = requires_api_key
        self._requires_api_base = requires_api_base
        self._litellm_provider = self._normalize_string(litellm_provider)
        self._secret_store = secret_store
        self._secret_service = self._normalize_string(secret_service) or self._DEFAULT_SECRET_SERVICE
        self._secret_key_name = self._normalize_string(secret_key_name) or provider_name
        self._default_env_var = self._normalize_string(default_env_var) or self._build_default_env_var(provider_name)
        self._request_timeout = request_timeout

    def list_models(self) -> Sequence[str]:
        """返回当前提供商已知的模型标识列表。"""

        return list(self._known_models)

    def validate_configuration(self, config: Mapping[str, object]) -> bool:
        """校验当前 provider 所需配置是否齐全且格式可用。"""

        provider_name = self._normalize_string(config.get("provider_name"))
        if provider_name is not None and provider_name != self.provider_name:
            return False

        if self._requires_api_base and self._resolve_api_base(config) is None:
            return False

        if self._requires_api_key and self._resolve_api_key(config) is None:
            return False

        model_name = self._normalize_string(config.get("model"))
        if model_name is not None and self._known_models and model_name not in self._known_models:
            return False

        custom_headers = config.get("custom_headers")
        if custom_headers is not None and self._normalize_headers(custom_headers) is None:
            return False

        return True

    def generate(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
    ) -> ResponsePayload:
        """执行非流式推理，并将异常转换为统一错误载荷。"""

        completion = self._import_completion()
        if completion is None:
            return self._error_response(
                model=model,
                error_type="missing_dependency",
                message="LiteLLM 未安装，无法执行模型调用。",
                retryable=False,
            )

        try:
            response: object = completion(
                **self._build_request(model=model, messages=messages, temperature=temperature, stream=False)
            )
            return self._normalize_response_payload(response, model=model)
        except Exception as exc:  # pragma: no cover - 依赖第三方 SDK 的运行时分支
            return self._response_from_exception(exc, model=model)

    def stream(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float = 0.0,
    ) -> Iterable[ResponsePayload]:
        """执行流式推理，并在异常时输出标准化错误分块。"""

        completion = self._import_completion()
        if completion is None:
            yield self._error_response(
                model=model,
                error_type="missing_dependency",
                message="LiteLLM 未安装，无法执行流式模型调用。",
                retryable=False,
                stream=True,
            )
            return

        try:
            response_iterable: object = completion(
                **self._build_request(model=model, messages=messages, temperature=temperature, stream=True)
            )
            for chunk in cast(Iterable[object], response_iterable):
                yield self._normalize_response_payload(chunk, model=model, stream=True)
        except Exception as exc:  # pragma: no cover - 依赖第三方 SDK 的运行时分支
            yield self._response_from_exception(exc, model=model, stream=True)

    def _build_request(
        self,
        *,
        model: str,
        messages: Sequence[MessagePayload],
        temperature: float,
        stream: bool,
    ) -> dict[str, object]:
        """构造传给 LiteLLM completion() 的请求参数。"""

        request: dict[str, object] = {
            "model": model,
            "messages": [dict(message) for message in messages],
            "temperature": temperature,
            "stream": stream,
            "timeout": self._request_timeout,
        }

        resolved_api_key = self._resolve_api_key({})
        resolved_api_base = self._resolve_api_base({})
        if resolved_api_key is not None:
            request["api_key"] = resolved_api_key
        if resolved_api_base is not None:
            request["api_base"] = resolved_api_base
        if self.custom_headers:
            request["custom_headers"] = dict(self.custom_headers)
        if self._litellm_provider is not None:
            request["custom_llm_provider"] = self._litellm_provider

        return request

    def _resolve_api_key(self, config: Mapping[str, object]) -> str | None:
        """按显式参数、配置、密钥存储、环境变量顺序解析 API Key。"""

        explicit_key = self._normalize_string(self.api_key)
        if explicit_key is not None:
            return explicit_key

        config_key = self._normalize_string(config.get("api_key"))
        if config_key is not None:
            return config_key

        secret_key_name = self._normalize_string(config.get("secret_key")) or self._secret_key_name
        secret_service = self._normalize_string(config.get("secret_service")) or self._secret_service
        if self._secret_store is not None:
            try:
                secret_value = self._secret_store.get(secret_service, secret_key_name)
            except Exception as exc:  # pragma: no cover - 底层存储异常仅记录
                logger.warning("读取 %s 的密钥存储失败: %s", self.provider_name, exc)
            else:
                normalized_secret = self._normalize_string(secret_value)
                if normalized_secret is not None:
                    return normalized_secret

        env_value = self._normalize_string(os.environ.get(self._default_env_var))
        if env_value is not None:
            return env_value
        return None

    def _resolve_api_base(self, config: Mapping[str, object]) -> str | None:
        """按实例参数和运行时配置解析 API Base。"""

        explicit_base = self._normalize_string(self.api_base)
        if explicit_base is not None:
            return explicit_base
        return self._normalize_string(config.get("api_base"))

    @staticmethod
    def _normalize_headers(value: object) -> dict[str, str] | None:
        """将 headers 收敛为字符串映射。"""

        if value is None:
            return None
        if not isinstance(value, Mapping):
            return None

        headers: dict[str, str] = {}
        raw_mapping = cast(Mapping[object, object], value)
        for raw_key, raw_item in raw_mapping.items():
            if not isinstance(raw_key, str):
                return None
            if not isinstance(raw_item, str):
                return None
            key = raw_key.strip()
            item = raw_item.strip()
            if not key:
                return None
            headers[key] = item
        return headers

    @staticmethod
    def _normalize_string(value: object) -> str | None:
        """提取非空字符串值。"""

        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    @staticmethod
    def _build_default_env_var(provider_name: str) -> str:
        """为 provider 自动推导默认环境变量名。"""

        normalized = "".join(character if character.isalnum() else "_" for character in provider_name.upper())
        return f"{normalized}_API_KEY"

    def _import_completion(self) -> CompletionCallable | None:
        """延迟导入 LiteLLM completion，缺失时仅记录警告。"""

        try:
            from litellm import completion
        except ImportError:
            logger.warning("LiteLLM 未安装，%s 适配器将返回错误响应。", self.provider_name)
            return None
        return cast(CompletionCallable, completion)

    def _normalize_response_payload(
        self,
        response: object,
        *,
        model: str,
        stream: bool = False,
    ) -> dict[str, object]:
        """将 LiteLLM 响应对象统一转换为字典结构。"""

        payload: dict[str, object]
        if isinstance(response, Mapping):
            payload = dict(cast(Mapping[str, object], response))
        elif hasattr(response, "model_dump"):
            payload = cast(ModelDumpLike, response).model_dump()
        elif hasattr(response, "dict"):
            payload = cast(DictLike, response).dict()
        else:
            payload = {"raw_response": response}

        _ = payload.setdefault("provider", self.provider_name)
        _ = payload.setdefault("model", model)
        _ = payload.setdefault("stream", stream)
        return payload

    def _response_from_exception(
        self,
        exc: Exception,
        *,
        model: str,
        stream: bool = False,
    ) -> dict[str, object]:
        """把运行时异常映射为统一错误响应。"""

        error_type, retryable = self._classify_exception(exc)
        logger.warning("%s 调用失败(%s): %s", self.provider_name, error_type, exc)
        return self._error_response(
            model=model,
            error_type=error_type,
            message=str(exc) or exc.__class__.__name__,
            retryable=retryable,
            stream=stream,
        )

    @staticmethod
    def _classify_exception(exc: Exception) -> tuple[str, bool]:
        """按错误特征归类超时、限流与 API 故障。"""

        class_name = exc.__class__.__name__.lower()
        message = (str(exc) or "").lower()
        signature = f"{class_name} {message}"

        if "rate" in signature and "limit" in signature:
            return "rate_limit", True
        if "timeout" in signature or "timed out" in signature:
            return "timeout", True
        if "auth" in signature or "api key" in signature or "unauthorized" in signature:
            return "authentication_error", False
        if "connection" in signature or "service unavailable" in signature or "api" in signature:
            return "api_error", True
        return "provider_error", False

    def _error_response(
        self,
        *,
        model: str,
        error_type: str,
        message: str,
        retryable: bool,
        stream: bool = False,
    ) -> dict[str, object]:
        """生成统一的错误响应载荷。"""

        return {
            "provider": self.provider_name,
            "model": model,
            "stream": stream,
            "ok": False,
            "choices": [],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "error": {
                "type": error_type,
                "message": message,
                "retryable": retryable,
            },
        }


class CompletionCallable(Protocol):
    """LiteLLM completion 可调用对象协议。"""

    def __call__(self, **kwargs: object) -> object:
        ...


class ModelDumpLike(Protocol):
    """支持 model_dump() 的响应对象协议。"""

    def model_dump(self) -> dict[str, object]:
        ...


class DictLike(Protocol):
    """支持 dict() 的响应对象协议。"""

    def dict(self) -> dict[str, object]:
        ...


__all__ = ["LiteLLMAdapter"]

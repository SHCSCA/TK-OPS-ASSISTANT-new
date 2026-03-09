from __future__ import annotations

# pyright: basic, reportMissingImports=false, reportMissingTypeStubs=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnusedCallResult=false, reportUnnecessaryIsInstance=false

"""AI 提供商、模型与当前选择的配置服务。"""

import importlib
import inspect
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Mapping, cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...core.security.secret_store import SecretStore, create_secret_store
from ...data.database import Database
from ...data.models.ai_provider import AIModel, AIProvider
from ...data.repositories.settings_repo import SettingsRepository
from .adapters.anthropic_adapter import AnthropicAdapter
from .adapters.ollama_adapter import OllamaAdapter
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.openai_compatible_adapter import OpenAICompatibleAdapter
from .provider_adapter import ProviderAdapter


@dataclass(frozen=True)
class AIModelDescriptor:
    """描述可供选择的提供商模型元数据。"""

    provider_name: str
    model_name: str
    display_name: str
    supports_streaming: bool = True


@dataclass(frozen=True)
class ProviderSelection:
    """描述当前运行时使用的提供商与模型选择。"""

    provider_name: str
    model_name: str


class AIConfigService:
    """管理 AI 提供商注册、模型目录、配置持久化与当前激活选择。"""

    service_name: str = "ai_config"

    _SETTINGS_CATEGORY = "ai"
    _ACTIVE_PROVIDER_KEY = "ai.provider.active"
    _ACTIVE_MODEL_KEY = "ai.model.active"
    _SECRET_SERVICE = "ai.providers"
    _DEFAULT_TEST_MESSAGE = [{"role": "user", "content": "ping"}]
    _BUILTIN_SORT_ORDERS = {
        "openai": 10,
        "anthropic": 20,
        "ollama": 30,
        "openai_compatible": 40,
    }
    _BUILTIN_PROVIDER_TYPES = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "ollama": OllamaAdapter,
        "openai_compatible": OpenAICompatibleAdapter,
    }

    def __init__(
        self,
        database: Database | None = None,
        secret_store: SecretStore | None = None,
    ) -> None:
        """初始化服务并接入数据库与安全密钥存储。"""

        self._database = database or Database()
        self._secret_store = secret_store or create_secret_store()
        self._settings_repo = SettingsRepository(self._database.create_session)
        self._providers: dict[str, ProviderAdapter] = {}
        self._provider_models: dict[str, list[AIModelDescriptor]] = {}
        self._active_selection: ProviderSelection | None = None
        self._initialized = False

    def initialize(self) -> None:
        """从数据库恢复提供商状态，并补齐内置默认提供商。"""

        self._database.create_all()
        self._providers.clear()
        self._provider_models.clear()

        for provider_record in self._load_provider_records():
            adapter = self._instantiate_adapter_from_record(provider_record)
            if adapter is None:
                continue
            provider_name = self._normalize_provider_name(provider_record.name)
            self._providers[provider_name] = adapter
            descriptors = self._descriptors_from_record(provider_record)
            if not descriptors:
                descriptors = self._build_model_descriptors(provider_name, adapter.list_models())
            self._provider_models[provider_name] = descriptors

        for adapter in self._build_builtin_adapters():
            if adapter.provider_name not in self._providers:
                self.register_provider(adapter)

        self._reload_models_from_database()
        self._active_selection = self._load_persisted_selection()
        if self._active_selection is None:
            self._active_selection = self._ensure_default_selection(persist=True)
        else:
            self.set_active_selection(self._active_selection)

        self._initialized = True

    def shutdown(self) -> None:
        """释放内存中的注册信息与活动选择。"""

        self._providers.clear()
        self._provider_models.clear()
        self._active_selection = None
        self._initialized = False

    def healthcheck(self) -> dict[str, object]:
        """返回服务当前健康状态摘要。"""

        active_selection = self._active_selection
        return {
            "service": self.service_name,
            "status": "ok",
            "initialized": self._initialized,
            "provider_count": len(self._providers),
            "providers": self.list_provider_names(),
            "active_selection": None
            if active_selection is None
            else {
                "provider_name": active_selection.provider_name,
                "model_name": active_selection.model_name,
            },
        }

    def register_provider(self, adapter: ProviderAdapter) -> None:
        """注册提供商适配器并将其配置与模型写入数据库。"""

        provider_name = self._normalize_provider_name(adapter.provider_name)
        config = self._extract_adapter_config(adapter)
        models = self._build_model_descriptors(provider_name, adapter.list_models())

        self._providers[provider_name] = adapter
        self._provider_models[provider_name] = models
        self._upsert_provider_record(provider_name=provider_name, adapter=adapter, config=config, models=models)

        if self._active_selection is None:
            self._active_selection = self._ensure_default_selection(persist=True)

    def unregister_provider(self, provider_name: str) -> None:
        """注销提供商，并删除其数据库记录。"""

        normalized_name = self._normalize_provider_name(provider_name)
        self._providers.pop(normalized_name, None)
        self._provider_models.pop(normalized_name, None)

        with self._database.session_scope() as session:
            provider_record = session.scalar(select(AIProvider).where(AIProvider.name == normalized_name))
            if provider_record is not None:
                session.delete(provider_record)

        if self._active_selection is not None and self._active_selection.provider_name == normalized_name:
            self._active_selection = self._ensure_default_selection(persist=True)

    def list_provider_names(self) -> list[str]:
        """返回当前已注册的提供商名称列表。"""

        return sorted(self._providers)

    def get_provider(self, provider_name: str) -> ProviderAdapter:
        """按名称返回已注册的提供商适配器实例。"""

        normalized_name = self._normalize_provider_name(provider_name)
        adapter = self._providers.get(normalized_name)
        if adapter is None:
            raise ValueError(f"未注册的 AI 提供商: {provider_name}")
        return adapter

    def list_models(self, provider_name: str) -> list[AIModelDescriptor]:
        """返回指定提供商当前可用的模型列表。"""

        normalized_name = self._normalize_provider_name(provider_name)
        return list(self._provider_models.get(normalized_name, []))

    def get_active_selection(self) -> ProviderSelection:
        """返回当前激活的提供商与模型选择。"""

        if self._active_selection is None:
            selection = self._ensure_default_selection(persist=True)
            if selection is None:
                raise RuntimeError("当前没有可用的 AI 提供商配置。")
            self._active_selection = selection
        return self._active_selection

    def set_active_selection(self, selection: ProviderSelection) -> None:
        """设置并持久化当前激活的提供商与模型选择。"""

        provider_name = self._normalize_provider_name(selection.provider_name)
        model_name = self._normalize_model_name(selection.model_name)
        if provider_name not in self._providers:
            raise ValueError(f"未注册的 AI 提供商: {selection.provider_name}")

        models = self._provider_models.setdefault(provider_name, [])
        if not any(model.model_name == model_name for model in models):
            descriptor = AIModelDescriptor(
                provider_name=provider_name,
                model_name=model_name,
                display_name=model_name,
                supports_streaming=True,
            )
            models.append(descriptor)
            self._upsert_model_record(provider_name=provider_name, model=descriptor)

        self._active_selection = ProviderSelection(provider_name=provider_name, model_name=model_name)
        self._settings_repo.set_value(
            self._ACTIVE_PROVIDER_KEY,
            provider_name,
            category=self._SETTINGS_CATEGORY,
        )
        self._settings_repo.set_value(
            self._ACTIVE_MODEL_KEY,
            model_name,
            category=self._SETTINGS_CATEGORY,
        )
        self._reload_models_from_database()

    def save_provider_config(self, provider_name: str, config: Mapping[str, object]) -> None:
        """保存指定提供商的配置，不包含 API Key。"""

        normalized_name = self._normalize_provider_name(provider_name)
        adapter = self.get_provider(normalized_name)
        sanitized = self._sanitize_provider_config(config, provider_name=normalized_name)
        if not adapter.validate_configuration(sanitized):
            raise ValueError(f"AI 提供商配置校验失败: {normalized_name}")

        with self._database.session_scope() as session:
            statement = cast(Any, select(AIProvider)).where(cast(Any, getattr(AIProvider, "name")) == normalized_name)
            provider_record = session.scalar(statement)
            if provider_record is None:
                raise ValueError(f"未找到提供商记录: {normalized_name}")
            provider_record.base_url = self._optional_string(sanitized.get("api_base"))
            provider_record.config_json = dict(sanitized)
            session.add(provider_record)

    def get_provider_config(self, provider_name: str) -> dict[str, object]:
        """读取指定提供商的持久化配置。"""

        normalized_name = self._normalize_provider_name(provider_name)
        with self._database.session_scope() as session:
            statement = cast(Any, select(AIProvider)).where(cast(Any, getattr(AIProvider, "name")) == normalized_name)
            provider_record = session.scalar(statement)
            if provider_record is None:
                raise ValueError(f"未找到提供商记录: {normalized_name}")

            config = dict(cast(Mapping[str, object], provider_record.config_json or {}))
            config["provider_name"] = normalized_name
            if provider_record.base_url is not None:
                config["api_base"] = provider_record.base_url
            return config

    def set_api_key(self, provider_name: str, api_key: str) -> None:
        """通过安全密钥存储保存提供商 API Key。"""

        normalized_name = self._normalize_provider_name(provider_name)
        normalized_key = self._normalize_non_empty_string(api_key, field_name="api_key")
        _ = self.get_provider(normalized_name)
        self._secret_store.set(self._SECRET_SERVICE, normalized_name, normalized_key)

    def get_api_key(self, provider_name: str) -> str | None:
        """从安全密钥存储读取提供商 API Key。"""

        normalized_name = self._normalize_provider_name(provider_name)
        return self._secret_store.get(self._SECRET_SERVICE, normalized_name)

    def test_provider_connection(self, provider_name: str) -> bool:
        """通过一次最小生成请求验证提供商连接是否可用。"""

        adapter = self.get_provider(provider_name)
        models = self.list_models(adapter.provider_name)
        if not models:
            return False

        response = adapter.generate(
            model=models[0].model_name,
            messages=self._DEFAULT_TEST_MESSAGE,
            temperature=0.0,
        )
        if response.get("ok") is False:
            return False
        if response.get("error") not in (None, {}):
            return False
        return True

    def _load_provider_records(self) -> list[AIProvider]:
        """从数据库加载全部提供商及其模型记录。"""

        with self._database.session_scope() as session:
            session_any = cast(Any, session)
            statement = cast(Any, select(AIProvider))
            statement = statement.options(selectinload(cast(Any, getattr(AIProvider, "models"))))
            statement = statement.order_by(
                cast(Any, getattr(AIProvider, "sort_order")),
                cast(Any, getattr(AIProvider, "name")),
            )
            return list(session_any.scalars(statement).all())

    def _build_builtin_adapters(self) -> list[ProviderAdapter]:
        """构造内置默认提供商适配器实例。"""

        return [
            OpenAIAdapter(secret_store=self._secret_store),
            AnthropicAdapter(secret_store=self._secret_store),
            OllamaAdapter(),
            OpenAICompatibleAdapter(secret_store=self._secret_store),
        ]

    def _instantiate_adapter_from_record(self, provider_record: AIProvider) -> ProviderAdapter | None:
        """根据数据库记录恢复提供商适配器实例。"""

        adapter_class = self._resolve_adapter_class(provider_record)
        if adapter_class is None:
            return None

        config = dict(cast(Mapping[str, object], provider_record.config_json or {}))
        if provider_record.base_url is not None:
            config.setdefault("api_base", provider_record.base_url)

        known_models = [
            model.model_id
            for model in sorted(provider_record.models, key=lambda item: (item.display_name, item.model_id))
            if model.is_enabled
        ]
        api_key = self.get_api_key(provider_record.name)
        return self._instantiate_adapter_class(
            adapter_class,
            provider_name=provider_record.name,
            config=config,
            known_models=known_models,
            api_key=api_key,
        )

    def _resolve_adapter_class(self, provider_record: AIProvider) -> type[object] | None:
        """解析提供商记录对应的适配器类型。"""

        provider_type = self._normalize_provider_name(provider_record.provider_type)
        builtin_class = self._BUILTIN_PROVIDER_TYPES.get(provider_type)
        if builtin_class is not None:
            return cast(type[object], builtin_class)

        provider_name_class = self._BUILTIN_PROVIDER_TYPES.get(provider_record.name)
        if provider_name_class is not None:
            return cast(type[object], provider_name_class)

        if ":" not in provider_type:
            return None
        module_name, _, class_name = provider_type.partition(":")
        try:
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, class_name)
        except (ImportError, AttributeError):
            return None
        if not inspect.isclass(adapter_class):
            return None
        return cast(type[object], adapter_class)

    def _instantiate_adapter_class(
        self,
        adapter_class: type[object],
        *,
        provider_name: str,
        config: Mapping[str, object],
        known_models: list[str],
        api_key: str | None,
    ) -> ProviderAdapter | None:
        """基于构造函数签名安全实例化适配器。"""

        try:
            signature = inspect.signature(adapter_class)
        except (TypeError, ValueError):
            signature = None

        merged_config = dict(config)
        candidate_kwargs: dict[str, object] = dict(merged_config)
        candidate_kwargs.setdefault("provider_name", provider_name)
        candidate_kwargs.setdefault("api_base", self._optional_string(merged_config.get("api_base")))
        candidate_kwargs.setdefault("custom_headers", self._normalize_headers(merged_config.get("custom_headers")))
        if known_models:
            candidate_kwargs.setdefault("known_models", known_models)
        if api_key is not None:
            candidate_kwargs.setdefault("api_key", api_key)
        candidate_kwargs.setdefault("secret_store", self._secret_store)

        if signature is None:
            try:
                adapter = adapter_class(**candidate_kwargs)
            except TypeError:
                return None
        else:
            parameters = signature.parameters
            accepts_kwargs = any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values())
            if accepts_kwargs:
                init_kwargs = candidate_kwargs
            else:
                init_kwargs = {
                    key: value
                    for key, value in candidate_kwargs.items()
                    if key in parameters and value is not None
                }
            try:
                adapter = adapter_class(**init_kwargs)
            except TypeError:
                try:
                    fallback_kwargs = {
                        key: value
                        for key, value in init_kwargs.items()
                        if key in {"provider_name", "secret_store", "api_key", "api_base"}
                    }
                    adapter = adapter_class(**fallback_kwargs)
                except TypeError:
                    try:
                        adapter = adapter_class()
                    except TypeError:
                        return None

        if not isinstance(adapter, ProviderAdapter):
            return None
        return adapter

    def _extract_adapter_config(self, adapter: ProviderAdapter) -> dict[str, object]:
        """从适配器实例提取可持久化的配置。"""

        config: dict[str, object] = {"provider_name": adapter.provider_name}
        api_base = self._optional_string(getattr(adapter, "api_base", None))
        custom_headers = self._normalize_headers(getattr(adapter, "custom_headers", None))
        if api_base is not None:
            config["api_base"] = api_base
        if custom_headers:
            config["custom_headers"] = custom_headers
        if getattr(adapter, "_litellm_provider", None) is not None:
            config["litellm_provider"] = getattr(adapter, "_litellm_provider")
        known_models = [str(model) for model in adapter.list_models() if isinstance(model, str) and model.strip()]
        if known_models:
            config["known_models"] = known_models
        return self._sanitize_provider_config(config, provider_name=adapter.provider_name)

    def _sanitize_provider_config(self, config: Mapping[str, object], *, provider_name: str) -> dict[str, object]:
        """清洗配置数据，确保可安全持久化且不写入密钥。"""

        sanitized: dict[str, object] = {"provider_name": provider_name}

        api_base = self._optional_string(config.get("api_base"))
        if api_base is not None:
            sanitized["api_base"] = api_base

        custom_headers = self._normalize_headers(config.get("custom_headers"))
        if custom_headers:
            sanitized["custom_headers"] = custom_headers

        litellm_provider = self._optional_string(config.get("litellm_provider"))
        if litellm_provider is not None:
            sanitized["litellm_provider"] = litellm_provider

        known_models = config.get("known_models")
        if isinstance(known_models, (list, tuple)):
            normalized_models = [
                str(model).strip()
                for model in known_models
                if isinstance(model, str) and str(model).strip()
            ]
            if normalized_models:
                sanitized["known_models"] = normalized_models

        for key, value in config.items():
            if key in sanitized or key in {"api_key", "secret", "secret_key", "secret_service", "provider_name"}:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                sanitized[key] = value

        return sanitized

    def _upsert_provider_record(
        self,
        *,
        provider_name: str,
        adapter: ProviderAdapter,
        config: Mapping[str, object],
        models: list[AIModelDescriptor],
    ) -> None:
        """创建或更新提供商记录及其模型目录。"""

        with self._database.session_scope() as session:
            statement = cast(Any, select(AIProvider))
            statement = statement.options(selectinload(cast(Any, getattr(AIProvider, "models"))))
            statement = statement.where(cast(Any, getattr(AIProvider, "name")) == provider_name)
            provider_record = session.scalar(statement)
            if provider_record is None:
                provider_record = AIProvider()
                provider_record.name = provider_name

            provider_record.provider_type = self._build_provider_type(adapter)
            provider_record.base_url = self._optional_string(config.get("api_base"))
            provider_record.is_enabled = True
            provider_record.sort_order = self._resolve_sort_order(provider_name)
            provider_record.config_json = dict(config)
            session.add(provider_record)
            session.flush()

            existing_models = {model.model_id: model for model in provider_record.models}
            seen_model_ids = {model.model_name for model in models}

            for descriptor in models:
                model_record = existing_models.get(descriptor.model_name)
                if model_record is None:
                    model_record = AIModel()
                model_record.provider_id = provider_record.id
                model_record.model_id = descriptor.model_name
                model_record.display_name = descriptor.display_name
                model_record.capabilities_json = ["streaming"] if descriptor.supports_streaming else []
                model_record.is_enabled = True
                session.add(model_record)

            for model_id, model_record in existing_models.items():
                if model_id not in seen_model_ids:
                    session.delete(model_record)

    def _upsert_model_record(self, *, provider_name: str, model: AIModelDescriptor) -> None:
        """确保指定模型记录存在于数据库中。"""

        with self._database.session_scope() as session:
            statement = cast(Any, select(AIProvider)).where(cast(Any, getattr(AIProvider, "name")) == provider_name)
            provider_record = session.scalar(statement)
            if provider_record is None:
                raise ValueError(f"未找到提供商记录: {provider_name}")

            statement = cast(Any, select(AIModel)).where(
                cast(Any, getattr(AIModel, "provider_id")) == provider_record.id,
                cast(Any, getattr(AIModel, "model_id")) == model.model_name,
            )
            model_record = session.scalar(statement)
            if model_record is None:
                model_record = AIModel()
                model_record.provider_id = provider_record.id
                model_record.model_id = model.model_name
            model_record.display_name = model.display_name
            model_record.capabilities_json = ["streaming"] if model.supports_streaming else []
            model_record.is_enabled = True
            session.add(model_record)

    def _reload_models_from_database(self) -> None:
        """从数据库刷新内存中的模型索引。"""

        provider_models: dict[str, list[AIModelDescriptor]] = {}
        for provider_record in self._load_provider_records():
            provider_models[provider_record.name] = self._descriptors_from_record(provider_record)
        for provider_name in self._providers:
            provider_models.setdefault(provider_name, self._build_model_descriptors(provider_name, self._providers[provider_name].list_models()))
        self._provider_models = provider_models

    def _descriptors_from_record(self, provider_record: AIProvider) -> list[AIModelDescriptor]:
        """将数据库模型记录转换为内存描述对象。"""

        descriptors = [
            AIModelDescriptor(
                provider_name=provider_record.name,
                model_name=model.model_id,
                display_name=model.display_name,
                supports_streaming="streaming" in list(model.capabilities_json or []),
            )
            for model in sorted(provider_record.models, key=lambda item: (item.display_name, item.model_id))
            if model.is_enabled
        ]
        return descriptors

    def _load_persisted_selection(self) -> ProviderSelection | None:
        """从设置表恢复当前激活选择。"""

        provider_setting = self._settings_repo.get_by_key(self._ACTIVE_PROVIDER_KEY)
        model_setting = self._settings_repo.get_by_key(self._ACTIVE_MODEL_KEY)
        provider_name = self._optional_string(getattr(provider_setting, "value", None))
        model_name = self._optional_string(getattr(model_setting, "value", None))
        if provider_name is None or model_name is None:
            return None
        if provider_name not in self._providers:
            return None
        return ProviderSelection(provider_name=provider_name, model_name=model_name)

    def _ensure_default_selection(self, *, persist: bool) -> ProviderSelection | None:
        """在缺失活动选择时回退到首个可用模型。"""

        for provider_name in self.list_provider_names():
            models = self.list_models(provider_name)
            if not models:
                continue
            selection = ProviderSelection(provider_name=provider_name, model_name=models[0].model_name)
            if persist:
                self.set_active_selection(selection)
            return selection
        return None

    def _build_model_descriptors(self, provider_name: str, model_names: object) -> list[AIModelDescriptor]:
        """把适配器返回的模型标识转换为标准描述对象。"""

        descriptors: list[AIModelDescriptor] = []
        seen_model_names: set[str] = set()
        iterable_model_names: list[object]
        if isinstance(model_names, str):
            iterable_model_names = [model_names]
        elif isinstance(model_names, Iterable):
            iterable_model_names = list(model_names)
        else:
            iterable_model_names = []
        for raw_model_name in iterable_model_names:
            if not isinstance(raw_model_name, str):
                continue
            model_name = raw_model_name.strip()
            if not model_name or model_name in seen_model_names:
                continue
            seen_model_names.add(model_name)
            descriptors.append(
                AIModelDescriptor(
                    provider_name=provider_name,
                    model_name=model_name,
                    display_name=model_name,
                    supports_streaming=True,
                )
            )
        return descriptors

    def _build_provider_type(self, adapter: ProviderAdapter) -> str:
        """生成可用于持久化的适配器类型标识。"""

        adapter_class = adapter.__class__
        builtin_name = self._normalize_provider_name(adapter.provider_name)
        if builtin_name in self._BUILTIN_PROVIDER_TYPES and self._BUILTIN_PROVIDER_TYPES[builtin_name] is adapter_class:
            return builtin_name
        return f"{adapter_class.__module__}:{adapter_class.__qualname__}"

    def _resolve_sort_order(self, provider_name: str) -> int:
        """返回提供商的默认排序权重。"""

        return self._BUILTIN_SORT_ORDERS.get(provider_name, 100)

    @staticmethod
    def _normalize_headers(value: object) -> dict[str, str] | None:
        """把自定义请求头标准化为字符串映射。"""

        if value is None:
            return None
        if not isinstance(value, Mapping):
            return None
        headers: dict[str, str] = {}
        for raw_key, raw_value in cast(Mapping[object, object], value).items():
            if not isinstance(raw_key, str) or not isinstance(raw_value, str):
                return None
            key = raw_key.strip()
            item = raw_value.strip()
            if not key:
                return None
            headers[key] = item
        return headers or None

    @staticmethod
    def _optional_string(value: object) -> str | None:
        """返回去除空白后的可选字符串。"""

        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    def _normalize_provider_name(self, value: str) -> str:
        """校验并标准化提供商名称。"""

        return self._normalize_non_empty_string(value, field_name="provider_name")

    def _normalize_model_name(self, value: str) -> str:
        """校验并标准化模型名称。"""

        return self._normalize_non_empty_string(value, field_name="model_name")

    @staticmethod
    def _normalize_non_empty_string(value: object, *, field_name: str) -> str:
        """校验必填字符串字段。"""

        if not isinstance(value, str):
            raise ValueError(f"{field_name} 必须是非空字符串")
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} 必须是非空字符串")
        return normalized


__all__ = ["AIConfigService", "AIModelDescriptor", "ProviderSelection"]

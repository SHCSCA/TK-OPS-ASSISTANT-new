from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer


class ProviderUpsertPayload(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    provider_type: str = Field(default="openai", alias="providerType")
    api_base: str = Field(default="https://api.openai.com/v1", alias="apiBase", max_length=255)
    default_model: str = Field(default="gpt-4o-mini", alias="defaultModel", max_length=80)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048, alias="maxTokens", ge=1)
    is_active: bool = Field(default=True, alias="isActive")

    model_config = {"populate_by_name": True}


def _not_found(message: str) -> JSONResponse:
    return JSONResponse(status_code=404, content=err("resource.not_found", message))


def build_providers_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(prefix="/providers", tags=["providers"])

    @router.get("", response_model=None)
    def list_providers() -> dict[str, object]:
        providers = container.legacy_facade.list_providers()
        return ok({"items": providers, "total": len(providers)})

    @router.post("", response_model=None)
    def create_provider(payload: ProviderUpsertPayload):
        if not payload.name.strip():
            return JSONResponse(
                status_code=400,
                content=err("validation.invalid_input", "Provider 名称不能为空"),
            )
        provider = container.legacy_facade.create_provider(
            name=payload.name.strip(),
            provider_type=payload.provider_type,
            api_base=payload.api_base,
            default_model=payload.default_model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            is_active=payload.is_active,
        )
        if payload.is_active:
            active_provider = container.legacy_facade.set_active_provider(int(provider["id"]))
            if active_provider is not None:
                provider = active_provider
        return ok(provider)

    @router.put("/{provider_id}", response_model=None)
    def update_provider(provider_id: int, payload: ProviderUpsertPayload):
        if not payload.name.strip():
            return JSONResponse(
                status_code=400,
                content=err("validation.invalid_input", "Provider 名称不能为空"),
            )
        provider = container.legacy_facade.update_provider(
            provider_id,
            name=payload.name.strip(),
            provider_type=payload.provider_type,
            api_base=payload.api_base,
            default_model=payload.default_model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            is_active=payload.is_active,
        )
        if provider is None:
            return _not_found("Provider 不存在，无法更新。")
        if payload.is_active:
            active_provider = container.legacy_facade.set_active_provider(provider_id)
            if active_provider is not None:
                provider = active_provider
        return ok(provider)

    @router.post("/{provider_id}/activate", response_model=None)
    def activate_provider(provider_id: int):
        provider = container.legacy_facade.set_active_provider(provider_id)
        if provider is None:
            return _not_found("Provider 不存在，无法启用。")
        return ok(provider)

    @router.post("/{provider_id}/test", response_model=None)
    def test_provider(provider_id: int):
        result = container.legacy_facade.test_provider(provider_id)
        if not bool(result.get("ok")):
            message = str(result.get("error") or "Provider 测试失败")
            return JSONResponse(
                status_code=400 if result.get("error") else 500,
                content=err("provider.test_failed", message, details=result),
            )
        return ok(result)

    @router.delete("/{provider_id}", response_model=None)
    def delete_provider(provider_id: int):
        deleted = container.legacy_facade.delete_provider(provider_id)
        if not deleted:
            return _not_found("Provider 不存在，无法删除。")
        return ok({"deleted": True, "providerId": provider_id})

    return router

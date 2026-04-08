from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.http.common.envelope import err, ok
from bootstrap.container import RuntimeContainer
from desktop_app.database.repository import Repository
from desktop_app.services.asset_service import AssetService

log = logging.getLogger(__name__)


class AssetCreatePayload(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    asset_type: str = Field(default="image", max_length=20)
    file_path: str = Field(min_length=1, max_length=500)
    tags: str | None = Field(default=None, max_length=500)
    account_id: int | None = Field(default=None)

    model_config = {"populate_by_name": True}


class AssetUpdatePayload(BaseModel):
    filename: str | None = Field(default=None, max_length=255)
    asset_type: str | None = Field(default=None, max_length=20)
    file_path: str | None = Field(default=None, max_length=500)
    tags: str | None = Field(default=None, max_length=500)
    account_id: int | None = Field(default=None)

    model_config = {"populate_by_name": True}


class AssetListQuery(BaseModel):
    asset_type: str | None = Field(default=None)
    query: str | None = Field(default=None)


def _not_found(message: str) -> JSONResponse:
    return JSONResponse(status_code=404, content=err("resource.not_found", message))


def _bad_request(message: str) -> JSONResponse:
    return JSONResponse(status_code=400, content=err("validation.invalid_input", message))


def _serialize_asset(item: object) -> dict[str, Any]:
    return {
        "id": int(getattr(item, "id", 0)),
        "filename": str(getattr(item, "filename", "") or ""),
        "assetType": str(getattr(item, "asset_type", "") or ""),
        "filePath": str(getattr(item, "file_path", "") or ""),
        "fileSize": int(getattr(item, "file_size", 0) or 0),
        "tags": getattr(item, "tags", None),
        "accountId": getattr(item, "account_id", None),
        "createdAt": _format_datetime(getattr(item, "created_at", None)),
        "updatedAt": _format_datetime(getattr(item, "updated_at", None)),
    }


def _format_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def build_assets_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter()

    @router.get("/assets")
    async def list_assets(
        asset_type: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        """List all assets, optionally filtered by type or search query."""
        try:
            service = AssetService()
            items = service.list_assets(asset_type=asset_type)

            # Filter by query if provided (filename or tags contains query)
            if query:
                query_lower = query.lower()
                items = [
                    item for item in items
                    if query_lower in str(item.filename).lower()
                    or (item.tags and query_lower in str(item.tags).lower())
                ]

            return ok({
                "items": [_serialize_asset(item) for item in items],
                "total": len(items),
            })
        except Exception as e:
            log.exception("Failed to list assets")
            return err("asset.list_failed", str(e))

    @router.get("/assets/stats")
    async def get_asset_stats() -> dict[str, Any]:
        """Get asset statistics by type."""
        try:
            service = AssetService()
            counts = service.count_by_type()
            total = sum(counts.values())
            return ok({
                "total": total,
                "byType": counts,
            })
        except Exception as e:
            log.exception("Failed to get asset stats")
            return err("asset.stats_failed", str(e))

    @router.get("/assets/{asset_id}")
    async def get_asset(asset_id: int) -> dict[str, Any]:
        """Get a single asset by ID."""
        try:
            service = AssetService()
            item = service.get_asset(asset_id)
            if item is None:
                return _not_found(f"Asset {asset_id} not found")
            return ok(_serialize_asset(item))
        except Exception as e:
            log.exception("Failed to get asset %s", asset_id)
            return err("asset.get_failed", str(e))

    @router.post("/assets")
    async def create_asset(payload: AssetCreatePayload) -> dict[str, Any]:
        """Create a new asset."""
        try:
            service = AssetService()
            item = service.create_asset(
                filename=payload.filename,
                asset_type=payload.asset_type,
                file_path=payload.file_path,
                tags=payload.tags,
                account_id=payload.account_id,
            )
            return ok(_serialize_asset(item))
        except Exception as e:
            log.exception("Failed to create asset")
            return err("asset.create_failed", str(e))

    @router.put("/assets/{asset_id}")
    async def update_asset(asset_id: int, payload: AssetUpdatePayload) -> dict[str, Any]:
        """Update an existing asset."""
        try:
            service = AssetService()
            update_fields: dict[str, Any] = {}
            if payload.filename is not None:
                update_fields["filename"] = payload.filename
            if payload.asset_type is not None:
                update_fields["asset_type"] = payload.asset_type
            if payload.file_path is not None:
                update_fields["file_path"] = payload.file_path
            if payload.tags is not None:
                update_fields["tags"] = payload.tags
            if payload.account_id is not None:
                update_fields["account_id"] = payload.account_id

            item = service.update_asset(asset_id, **update_fields)
            if item is None:
                return _not_found(f"Asset {asset_id} not found")
            return ok(_serialize_asset(item))
        except Exception as e:
            log.exception("Failed to update asset %s", asset_id)
            return err("asset.update_failed", str(e))

    @router.delete("/assets/{asset_id}")
    async def delete_asset(asset_id: int) -> dict[str, Any]:
        """Delete an asset."""
        try:
            service = AssetService()
            success = service.delete_asset(asset_id)
            if not success:
                return _not_found(f"Asset {asset_id} not found")
            return ok({"deleted": True})
        except Exception as e:
            log.exception("Failed to delete asset %s", asset_id)
            return err("asset.delete_failed", str(e))

    return router

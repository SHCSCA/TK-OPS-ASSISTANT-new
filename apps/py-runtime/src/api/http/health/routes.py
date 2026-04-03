from __future__ import annotations

from fastapi import APIRouter

from api.common.session import PROTOCOL_VERSION, TOKEN_HEADER, TOKEN_QUERY_KEY
from api.http.common.envelope import ok
from bootstrap.container import RuntimeContainer


def build_health_router(container: RuntimeContainer) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/health")
    def health() -> dict[str, object]:
        return ok(
            {
                "status": "ok",
                "version": container.app_version,
                "dbPath": str(container.db_path),
                "dataDir": str(container.runtime_settings.data_dir),
                "host": container.runtime_settings.host,
                "port": container.runtime_settings.port,
                "environment": container.runtime_settings.environment,
                "logLevel": container.runtime_settings.log_level,
                "logFile": str(container.runtime_settings.log_file),
                "protocol": {
                    "version": PROTOCOL_VERSION,
                    "auth": {
                        "header": TOKEN_HEADER,
                        "wsQuery": TOKEN_QUERY_KEY,
                    },
                },
            }
        )

    return router

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.common.session import is_public_http_path
from api.http.assistant.routes import build_assistant_router
from api.http.common.auth import request_has_valid_token, unauthorized_response
from api.http.accounts.routes import build_accounts_router
from api.http.copywriter.routes import build_copywriter_router
from api.http.dashboard.routes import build_dashboard_router
from api.http.health.routes import build_health_router
from api.http.license.routes import build_license_router
from api.http.notifications.routes import build_notifications_router
from api.http.providers.routes import build_providers_router
from api.http.scheduler.routes import build_scheduler_router
from api.http.settings.routes import build_settings_router
from api.http.tasks.routes import build_tasks_router
from api.http.version.routes import build_version_router
from api.ws.copywriter import build_copywriter_stream_router
from api.ws.runtime_status import build_runtime_status_router
from bootstrap.container import RuntimeContainer

log = logging.getLogger(__name__)


def build_app(container: RuntimeContainer) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        container.initialize()
        log.info("Runtime Web 应用启动完成: version=%s", container.app_version)
        yield
        log.info("Runtime Web 应用已关闭")

    app = FastAPI(
        title="TK-OPS Runtime",
        version=container.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:4173",
            "http://localhost:4173",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        is_public_path = is_public_http_path(request.url.path)
        if not is_public_path and not request_has_valid_token(
            request,
            container.runtime_settings,
        ):
            return unauthorized_response()

        if not container.runtime_settings.enable_request_logging or is_public_path:
            return await call_next(request)

        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - started_at) * 1000
            log.exception(
                "HTTP %s %s 执行失败 (%.2f ms)",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        log.info(
            "HTTP %s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    app.include_router(build_health_router(container))
    app.include_router(build_license_router(container))
    app.include_router(build_settings_router(container))
    app.include_router(build_accounts_router(container))
    app.include_router(build_providers_router(container))
    app.include_router(build_tasks_router(container))
    app.include_router(build_scheduler_router(container))
    app.include_router(build_dashboard_router(container))
    app.include_router(build_copywriter_router(container))
    app.include_router(build_notifications_router(container))
    app.include_router(build_version_router(container))
    app.include_router(build_assistant_router(container))
    app.include_router(build_runtime_status_router(container.app_version, container.runtime_settings))
    app.include_router(build_copywriter_stream_router(container))

    return app

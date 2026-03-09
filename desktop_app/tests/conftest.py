# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

from __future__ import annotations

"""Shared pytest fixtures for the TK-OPS desktop application."""

from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest

from ..core.config.bus import ConfigBus
from ..core.qt import QApplication
from ..core.types import ConfigKey
from ..data.database import Database
from ..services.base import ServiceBase
from .fakes.services import (
    FakeAIConfigService,
    FakeAccountService,
    FakeAnalyticsService,
    FakeAutomationService,
    FakeContentService,
    FakeOperationsService,
)


@pytest.fixture(scope="session")
def qapp() -> Iterator[QApplication]:
    """Provide a shared QApplication instance for widget-oriented tests."""

    existing = QApplication.instance()
    if existing is not None:
        yield existing
        return

    app = QApplication([])
    yield app
    app.quit()


@pytest.fixture()
def tmp_config_dir(tmp_path: Path) -> Path:
    """Provide an isolated config directory for one test invocation."""

    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture()
def fake_config(tmp_config_dir: Path) -> ConfigBus:
    """Provide a config bus seeded with deterministic test defaults."""

    config_bus = ConfigBus(path=tmp_config_dir / "config.json")
    config_bus.set(ConfigKey("theme.mode"), "light")
    config_bus.set(ConfigKey("ai.provider.active"), "mock-provider")
    config_bus.set(ConfigKey("ai.model.active"), "mock-model")
    return config_bus


@pytest.fixture()
def fake_db() -> Iterator[Database]:
    """Provide an in-memory database with schema lifecycle per test."""

    database = Database("sqlite:///:memory:")
    database.create_all()
    try:
        yield database
    finally:
        database.drop_all()


@pytest.fixture()
def fake_services(
    fake_config: ConfigBus,
    fake_db: Database,
) -> Iterator[dict[str, object]]:
    """Provide initialized fake domain services backed by canned data."""

    services: dict[str, object] = {
        "account": FakeAccountService(),
        "content": FakeContentService(),
        "analytics": FakeAnalyticsService(),
        "automation": FakeAutomationService(),
        "operations": FakeOperationsService(),
        "ai_config": FakeAIConfigService(
            provider_name=str(fake_config.get(ConfigKey("ai.provider.active"), "mock-provider")),
            model_name=str(fake_config.get(ConfigKey("ai.model.active"), "mock-model")),
        ),
        "config": fake_config,
        "db": fake_db,
    }

    runtime_services: list[ServiceBase] = [
        cast(ServiceBase, services["account"]),
        cast(ServiceBase, services["content"]),
        cast(ServiceBase, services["analytics"]),
        cast(ServiceBase, services["automation"]),
        cast(ServiceBase, services["operations"]),
        cast(ServiceBase, services["ai_config"]),
    ]

    for service in runtime_services:
        service.initialize()

    try:
        yield services
    finally:
        for service in reversed(runtime_services):
            service.shutdown()

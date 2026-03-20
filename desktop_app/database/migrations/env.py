"""Alembic environment -- supports both CLI (alembic upgrade head) and
programmatic usage from desktop_app.database.run_migrations().
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

try:
    from logging.config import fileConfig
except ImportError:
    fileConfig = None  # PyInstaller 可能未收集 logging.config

# Ensure project root is on sys.path for CLI usage
_project_root = str(Path(__file__).resolve().parents[3])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from alembic import context
from sqlalchemy import pool

from desktop_app.database.models import Base

config = context.config

# Only configure logging from alembic.ini if no handlers exist yet (CLI mode).
# When called programmatically, desktop_app.logging_config handles logging.
if fileConfig is not None and config.config_file_name is not None:
    if not logging.getLogger().handlers:
        fileConfig(config.config_file_name)

target_metadata = Base.metadata
log = logging.getLogger("alembic.env")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from desktop_app.database import engine

    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""Database layer – engine creation, session factory, and auto-migration.

DB location: %APPDATA%/TK-OPS-ASSISTANT/tk_ops.db  (survives exe updates)
Fallback for dev: <project>/data/tk_ops.db
"""
from __future__ import annotations

import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from alembic import command as alembic_cmd
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import Session, sessionmaker

from desktop_app.database.models import Base

APP_VERSION = "1.0.0"
log = logging.getLogger(__name__)


def _resolve_data_dir() -> Path:
    """Pick the best data directory: AppData on Windows, project/data in dev."""
    if getattr(sys, "frozen", False):
        # Packaged exe – always use AppData
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / "TK-OPS-ASSISTANT"
    # Dev mode – check if APPDATA is available, otherwise fall back to project/data
    appdata = os.environ.get("APPDATA")
    if appdata:
        p = Path(appdata) / "TK-OPS-ASSISTANT"
        try:
            p.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fall back to a local data directory if APPDATA is not writable
            return Path(__file__).resolve().parents[2] / "data"
        return p
    return Path(__file__).resolve().parents[2] / "data"


DATA_DIR = _resolve_data_dir()
# Allow overriding the database path (useful for tests/CI in isolated environments)
DB_PATH = Path(os.environ.get("TKOPS_DB_PATH")) if os.environ.get("TKOPS_DB_PATH") else DATA_DIR / "tk_ops.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Enable WAL mode for better concurrent read performance
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def _alembic_cfg() -> AlembicConfig:
    """Build an AlembicConfig that works both in dev and frozen (exe) mode."""
    if getattr(sys, "frozen", False):
        ini_path = Path(sys._MEIPASS) / "alembic.ini"
        migrations_dir = Path(sys._MEIPASS) / "desktop_app" / "database" / "migrations"
    else:
        ini_path = Path(__file__).resolve().parents[2] / "alembic.ini"
        migrations_dir = Path(__file__).resolve().parent / "migrations"
    cfg = AlembicConfig(str(ini_path))
    # Override script_location to an absolute path so it works everywhere
    cfg.set_main_option("script_location", str(migrations_dir))
    return cfg


def _run_migrations() -> None:
    """Bring the database schema up to the latest revision.

    For brand-new databases: create_all + stamp head.
    For existing databases: run alembic upgrade head.
    """
    insp = inspect(engine)
    tables = insp.get_table_names()
    cfg = _alembic_cfg()

    if "alembic_version" not in tables:
        # Fresh DB – create tables from models, then stamp at latest revision
        Base.metadata.create_all(engine)
        alembic_cmd.stamp(cfg, "head")
        log.info("Fresh database: tables created and stamped at head")
    else:
        # Existing DB – run pending migrations
        alembic_cmd.upgrade(cfg, "head")
        log.info("Database migrations applied (upgrade to head)")


def init_db() -> None:
    """Create data directory and bring schema to latest revision."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _run_migrations()
    except Exception:
        log.critical("Database migration failed", exc_info=True)
        raise


def get_session() -> Session:
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope with auto-commit / rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Auto-initialize the database when this module is imported (helps tests run reliably
# in fresh environments where migrations may not have run yet).
try:
    init_db()
except Exception:
    # Do not crash import if DB cannot be initialized in some environments
    pass

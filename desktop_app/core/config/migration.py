from __future__ import annotations

# pyright: basic

"""Schema migration primitives for persisted configuration payloads."""

from dataclasses import dataclass


CURRENT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ConfigMigration:
    """Base migration contract from one schema version to the next."""

    from_version: int
    to_version: int

    def migrate(self, data: dict[str, object]) -> dict[str, object]:
        """Transform persisted config data into the target schema version."""

        _ = data
        raise NotImplementedError


MIGRATIONS: list[ConfigMigration] = []


def apply_migrations(data: dict[str, object], current_version: int) -> dict[str, object]:
    """Apply all sequential migrations needed to reach the current schema version."""

    migrated = dict(data)
    version = current_version
    if version >= CURRENT_SCHEMA_VERSION:
        return migrated

    while version < CURRENT_SCHEMA_VERSION:
        next_migration: ConfigMigration | None = None
        for migration in MIGRATIONS:
            if migration.from_version == version:
                next_migration = migration
                break

        if next_migration is None:
            raise ValueError(
                f"No config migration path from schema version {version} to {CURRENT_SCHEMA_VERSION}."
            )

        migrated = next_migration.migrate(migrated)
        version = next_migration.to_version

    return migrated


ConfigMigrationPlan = ConfigMigration


__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "ConfigMigration",
    "ConfigMigrationPlan",
    "MIGRATIONS",
    "apply_migrations",
]

from __future__ import annotations

# pyright: basic

"""Schema definitions and normalization helpers for application config."""

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, cast

from ..types import ConfigKey, ThemeMode


def _copy_default(value: object) -> object:
    """Return an isolated copy for mutable default values."""

    return deepcopy(value)


def serialize_config_value(value: object) -> object:
    """Convert runtime config values into JSON-serializable data."""

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        serialized: dict[str, object] = {}
        for key, item in value.items():
            serialized[str(key)] = serialize_config_value(item)
        return serialized
    if isinstance(value, (list, tuple)):
        return [serialize_config_value(item) for item in value]
    if isinstance(value, set):
        ordered_items: Iterable[object] = sorted(value, key=repr)
        return [serialize_config_value(item) for item in ordered_items]
    return value


def coerce_config_value(value: object, type_hint: type[object]) -> object:
    """Coerce persisted or incoming values into the schema runtime type."""

    if value is None:
        return None

    if issubclass(type_hint, Enum):
        if isinstance(value, type_hint):
            return value
        return type_hint(value)

    if type_hint is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return bool(value)
        raise ValueError(f"Cannot coerce {value!r} to bool.")

    if type_hint is int:
        if isinstance(value, bool):
            raise ValueError("Boolean values are not valid ints for config fields.")
        if not isinstance(value, (int, float, str)):
            raise ValueError(f"Cannot coerce {value!r} to int.")
        return int(cast(int | float | str, value))

    if type_hint is float:
        if isinstance(value, bool):
            raise ValueError("Boolean values are not valid floats for config fields.")
        if not isinstance(value, (int, float, str)):
            raise ValueError(f"Cannot coerce {value!r} to float.")
        return float(cast(int | float | str, value))

    if type_hint is str:
        return str(value)

    if type_hint is dict:
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict, got {type(value).__name__}.")
        return deepcopy(value)

    if type_hint is list:
        if not isinstance(value, list):
            raise ValueError(f"Expected list, got {type(value).__name__}.")
        return deepcopy(value)

    if type_hint is tuple:
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(value)
        raise ValueError(f"Expected tuple-compatible value, got {type(value).__name__}.")

    if not isinstance(value, type_hint):
        raise ValueError(f"Expected {type_hint.__name__}, got {type(value).__name__}.")
    return deepcopy(value)


@dataclass(frozen=True)
class ConfigField:
    """Describes one typed configuration key."""

    key: ConfigKey
    default: object
    type_hint: type[object]
    description: str
    category: str

    def copy_default(self) -> object:
        """Return a safe copy of the field default."""

        return _copy_default(self.default)

    def normalize(self, value: object) -> object:
        """Normalize an incoming value according to this field definition."""

        if value is None:
            return self.copy_default()
        return coerce_config_value(value, self.type_hint)

    def serialize(self, value: object) -> object:
        """Serialize a runtime value for persistence."""

        return serialize_config_value(value)


def _field(
    key: str,
    default: object,
    type_hint: type[object],
    description: str,
    category: str,
) -> ConfigField:
    """Build a config field with a typed key wrapper."""

    return ConfigField(
        key=ConfigKey(key),
        default=default,
        type_hint=type_hint,
        description=description,
        category=category,
    )


SCHEMA: dict[ConfigKey, ConfigField] = {
    ConfigKey("theme.mode"): _field("theme.mode", ThemeMode.LIGHT, ThemeMode, "Active application theme mode.", "theme"),
    ConfigKey("theme.font_scale"): _field("theme.font_scale", 1.0, float, "Global UI font scale multiplier.", "theme"),
    ConfigKey("theme.sidebar_width"): _field("theme.sidebar_width", 280, int, "Canonical expanded sidebar width from design tokens.", "theme"),
    ConfigKey("theme.animations_enabled"): _field("theme.animations_enabled", True, bool, "Whether UI transitions and animations are enabled.", "theme"),
    ConfigKey("app.language"): _field("app.language", "zh-CN", str, "Primary UI language locale.", "general"),
    ConfigKey("app.sidebar_collapsed"): _field("app.sidebar_collapsed", False, bool, "Whether the main navigation sidebar is collapsed.", "general"),
    ConfigKey("app.window.width"): _field("app.window.width", 1440, int, "Last persisted application window width.", "general"),
    ConfigKey("app.window.height"): _field("app.window.height", 900, int, "Last persisted application window height.", "general"),
    ConfigKey("app.window.maximized"): _field("app.window.maximized", False, bool, "Whether the main window was maximized on last exit.", "general"),
    ConfigKey("shell.start_route"): _field("shell.start_route", "dashboard_home", str, "Default shell route shown on startup.", "general"),
    ConfigKey("runtime.offline_mode"): _field("runtime.offline_mode", False, bool, "Disables network-dependent flows for safe offline operation.", "runtime"),
    ConfigKey("runtime.debug_logging"): _field("runtime.debug_logging", False, bool, "Enables verbose runtime logging for troubleshooting.", "runtime"),
    ConfigKey("ai.default_provider"): _field("ai.default_provider", "openai", str, "Default AI provider used by content generation features.", "ai"),
    ConfigKey("ai.default_model"): _field("ai.default_model", "gpt-4o", str, "Default model identifier for AI requests.", "ai"),
    ConfigKey("ai.streaming_enabled"): _field("ai.streaming_enabled", True, bool, "Whether streaming AI responses are enabled by default.", "ai"),
    ConfigKey("ai.temperature"): _field("ai.temperature", 0.7, float, "Default sampling temperature for AI generation.", "ai"),
    ConfigKey("ai.max_tokens"): _field("ai.max_tokens", 2048, int, "Default upper token limit for generated responses.", "ai"),
    ConfigKey("network.proxy"): _field("network.proxy", "", str, "Optional HTTP(S) proxy endpoint.", "network"),
    ConfigKey("network.timeout"): _field("network.timeout", 30, int, "Default outbound network timeout in seconds.", "network"),
    ConfigKey("network.verify_ssl"): _field("network.verify_ssl", True, bool, "Whether TLS certificates are verified for outbound traffic.", "network"),
    ConfigKey("updates.auto_check"): _field("updates.auto_check", True, bool, "Whether the application checks for updates automatically.", "system"),
}


@dataclass
class AppConfigSchema:
    """Schema container with helpers for defaults, validation, and serialization."""

    entries: dict[ConfigKey, ConfigField] = field(default_factory=lambda: dict(SCHEMA))

    def get_field(self, key: ConfigKey) -> ConfigField | None:
        """Return the field definition for a config key if known."""

        return self.entries.get(key)

    def is_known_key(self, key: ConfigKey) -> bool:
        """Return whether the schema knows about the given key."""

        return key in self.entries

    def defaults(self) -> dict[str, object]:
        """Build a fresh dict containing all schema defaults."""

        return {str(key): item.copy_default() for key, item in self.entries.items()}

    def normalize_value(self, key: ConfigKey, value: object) -> object:
        """Normalize a single value according to the schema when possible."""

        item = self.get_field(key)
        if item is None:
            return deepcopy(value)
        return item.normalize(value)

    def normalize_payload(self, values: dict[str, object]) -> dict[str, object]:
        """Merge defaults with a raw payload and normalize known keys."""

        normalized = self.defaults()
        for raw_key, raw_value in values.items():
            normalized[str(ConfigKey(raw_key))] = self.normalize_value(ConfigKey(raw_key), raw_value)
        return normalized

    def serialize_payload(self, values: dict[str, object]) -> dict[str, object]:
        """Serialize a runtime payload into a JSON-safe dict."""

        serialized: dict[str, object] = {}
        for raw_key, raw_value in values.items():
            item = self.get_field(ConfigKey(raw_key))
            serialized[raw_key] = item.serialize(raw_value) if item is not None else serialize_config_value(raw_value)
        return serialized

    def validate(self, values: dict[str, object]) -> None:
        """Validate that provided values can be normalized by the schema."""

        for raw_key, raw_value in values.items():
            self.normalize_value(ConfigKey(raw_key), raw_value)


ConfigEntry = ConfigField


__all__ = [
    "AppConfigSchema",
    "ConfigEntry",
    "ConfigField",
    "SCHEMA",
    "coerce_config_value",
    "serialize_config_value",
]

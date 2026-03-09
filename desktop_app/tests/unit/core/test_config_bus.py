from __future__ import annotations

import json
import threading
import unittest
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import cast

from ....core.config.bus import ConfigBus
from ....core.types import ConfigKey, ThemeMode


ASSERT = unittest.TestCase()


def test_get_returns_default_when_empty(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")

    assert bus.get(ConfigKey("missing.key"), "fallback") == "fallback"


def test_get_known_key_returns_schema_default(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")

    assert bus.get(ConfigKey("app.language")) == "zh-CN"


def test_set_and_get_roundtrip(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")

    bus.set(ConfigKey("app.language"), "en-US")

    assert bus.get(ConfigKey("app.language")) == "en-US"


def test_set_emits_value_changed(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    events: list[tuple[str, object, object]] = []

    def callback(key: str, old_value: object, new_value: object) -> None:
        events.append((key, old_value, new_value))

    bus.subscribe(ConfigKey("app.language"), callback)
    bus.set(ConfigKey("app.language"), "en-US")

    assert events == [("app.language", "zh-CN", "en-US")]


def test_set_same_value_does_not_emit(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    events: list[tuple[str, object, object]] = []

    def callback(key: str, old_value: object, new_value: object) -> None:
        events.append((key, old_value, new_value))

    bus.subscribe(ConfigKey("theme.mode"), callback)
    bus.set(ConfigKey("theme.mode"), ThemeMode.LIGHT)

    assert events == []


def test_subscribe_and_unsubscribe(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    events: list[str] = []

    def callback(_new_value: object) -> None:
        events.append("called")

    key = ConfigKey("app.language")
    bus.subscribe(key, callback)
    bus.unsubscribe(key, callback)
    bus.set(key, "en-US")

    assert events == []


def test_snapshot_is_immutable(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    bus.set(ConfigKey("custom.payload"), {"nested": {"items": [1, 2, 3]}})
    snapshot = bus.snapshot()

    nested = cast(Mapping[str, object], snapshot.values["custom.payload"])
    assert isinstance(snapshot.values, MappingProxyType)
    assert isinstance(nested, MappingProxyType)
    inner = cast(Mapping[str, object], nested["nested"])
    items = cast(tuple[int, ...], inner["items"])
    assert isinstance(items, tuple)
    assert items == (1, 2, 3)

    bus.set(ConfigKey("custom.payload"), {"nested": {"items": [9, 9, 9]}})

    frozen_payload = cast(Mapping[str, object], snapshot.values["custom.payload"])
    frozen_inner = cast(Mapping[str, object], frozen_payload["nested"])
    assert frozen_inner["items"] == (1, 2, 3)


def test_snapshot_contains_current_values(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    bus.set(ConfigKey("app.language"), "en-US")
    bus.set(ConfigKey("theme.mode"), ThemeMode.DARK)

    snapshot = bus.snapshot()

    assert snapshot.get(ConfigKey("app.language")) == "en-US"
    assert snapshot[ConfigKey("theme.mode")] == ThemeMode.DARK
    assert snapshot.schema_version >= 1


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    config_path = tmp_path / "roundtrip.json"
    bus = ConfigBus(path=config_path)
    bus.set(ConfigKey("app.language"), "en-US")
    bus.set(ConfigKey("theme.mode"), ThemeMode.DARK)
    bus.set(ConfigKey("network.timeout"), 45)
    bus.save()

    reloaded = ConfigBus(path=config_path)

    assert reloaded.get(ConfigKey("app.language")) == "en-US"
    assert reloaded.get(ConfigKey("theme.mode")) == ThemeMode.DARK
    assert reloaded.get(ConfigKey("network.timeout")) == 45


def test_load_nonexistent_file_uses_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.json"
    bus = ConfigBus(path=config_path)
    bus.set(ConfigKey("app.language"), "en-US")

    bus.load(config_path)

    assert bus.get(ConfigKey("app.language")) == "zh-CN"
    assert bus.get(ConfigKey("theme.mode")) == ThemeMode.LIGHT


def test_load_corrupted_json_uses_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "corrupted.json"
    _ = config_path.write_text("{not-valid-json", encoding="utf-8")
    bus = ConfigBus(path=config_path)
    bus.set(ConfigKey("app.language"), "en-US")

    bus.load(config_path)

    assert bus.get(ConfigKey("app.language")) == "zh-CN"
    assert bus.get(ConfigKey("theme.mode")) == ThemeMode.LIGHT


def test_reset_to_defaults(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    bus.set(ConfigKey("app.language"), "en-US")
    bus.set(ConfigKey("theme.mode"), ThemeMode.DARK)

    bus.reset_to_defaults()

    assert bus.get(ConfigKey("app.language")) == "zh-CN"
    assert bus.get(ConfigKey("theme.mode")) == ThemeMode.LIGHT


def test_thread_safety_basic(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    key = ConfigKey("app.window.width")
    errors: list[BaseException] = []
    expected_values = {1200, 1280, 1366, 1440, 1600}

    def worker(value: int) -> None:
        try:
            for _ in range(100):
                bus.set(key, value)
                assert bus.get(key) in expected_values
        except BaseException as exc:  # pragma: no cover - assertion capture path
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(value,)) for value in sorted(expected_values)]
    for thread in threads:
        _ = thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert bus.get(key) in expected_values


def test_replace_values_emits_changes(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    events: list[tuple[str, object, object]] = []
    config_path = tmp_config_dir / "replacement.json"

    def callback(key: str, old_value: object, new_value: object) -> None:
        events.append((key, old_value, new_value))

    bus.subscribe(ConfigKey("app.language"), callback)
    _ = config_path.write_text(
        json.dumps({"schema_version": 1, "values": {"app.language": "en-US"}}),
        encoding="utf-8",
    )
    bus.load(config_path)

    assert events == [("app.language", "zh-CN", "en-US")]
    assert bus.get(ConfigKey("app.language")) == "en-US"


def test_config_key_newtype_works(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")
    key = ConfigKey("shell.start_route")

    bus.set(key, "analytics_home")
    snapshot = bus.snapshot()

    assert bus.get(key) == "analytics_home"
    assert snapshot[key] == "analytics_home"
    assert snapshot[str(key)] == "analytics_home"


def test_schema_normalization_on_set(tmp_config_dir: Path) -> None:
    bus = ConfigBus(path=tmp_config_dir / "config.json")

    bus.set(ConfigKey("theme.font_scale"), "1.25")
    bus.set(ConfigKey("theme.animations_enabled"), "false")
    bus.set(ConfigKey("network.timeout"), "45")

    assert bus.get(ConfigKey("theme.font_scale")) == 1.25
    assert isinstance(bus.get(ConfigKey("theme.font_scale")), float)
    assert bus.get(ConfigKey("theme.animations_enabled")) is False
    assert bus.get(ConfigKey("network.timeout")) == 45


def test_load_flat_payload_without_values_wrapper(tmp_path: Path) -> None:
    config_path = tmp_path / "flat.json"
    _ = config_path.write_text(
        json.dumps({"schema_version": 1, "app.language": "en-US", "theme.mode": "dark"}),
        encoding="utf-8",
    )

    bus = ConfigBus(path=config_path)

    assert bus.get(ConfigKey("app.language")) == "en-US"
    assert bus.get(ConfigKey("theme.mode")) == ThemeMode.DARK

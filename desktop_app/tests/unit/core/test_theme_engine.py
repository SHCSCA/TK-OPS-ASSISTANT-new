from __future__ import annotations

from pathlib import Path
from typing import Final
from typing import cast

from ....core.config.bus import ConfigBus
from ....core.qt import Signal
from ....core.theme.engine import ThemeEngine
from ....core.types import ConfigKey, ThemeMode


class StubConfigBus:
    def __init__(self, configured_value: object) -> None:
        self._configured_value: Final[object] = configured_value
        self.theme_mode_changed: Signal = Signal(str)

    def get(self, key: ConfigKey, default: object = None) -> object:
        _ = (key, default)
        return self._configured_value

    def set(self, key: ConfigKey, value: object) -> None:
        _ = (key, value)
        return None


def test_initial_mode_from_config_light_by_default(tmp_config_dir: Path, qapp: object) -> None:
    _ = qapp
    config_bus = ConfigBus(path=tmp_config_dir / "config.json")

    engine = ThemeEngine(config_bus)

    assert engine.current_mode == ThemeMode.LIGHT


def test_set_mode_changes_current_mode(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)

    theme_engine.set_mode(ThemeMode.DARK)

    assert theme_engine.current_mode == ThemeMode.DARK
    assert fake_config.get(ConfigKey("theme.mode")) == ThemeMode.DARK


def test_toggle_switches_between_modes(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)

    theme_engine.toggle()
    assert theme_engine.current_mode == ThemeMode.DARK

    theme_engine.toggle()
    assert theme_engine.current_mode == ThemeMode.LIGHT


def test_set_same_mode_no_op(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)
    events: list[str] = []
    theme_engine.theme_changed.connect(events.append)

    theme_engine.set_mode(ThemeMode.LIGHT)

    assert theme_engine.current_mode == ThemeMode.LIGHT
    assert events == []


def test_theme_changed_signal_emitted(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)
    events: list[str] = []
    theme_engine.theme_changed.connect(events.append)

    theme_engine.set_mode(ThemeMode.DARK)

    assert events == ["dark"]


def test_get_token_returns_string(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)
    token = theme_engine.get_token("brand.primary")

    assert isinstance(token, str)
    assert token


def test_get_color_returns_object(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)
    token = theme_engine.get_token("brand.primary")
    color = theme_engine.get_color("brand.primary")

    assert color is not None
    name_method = getattr(color, "name", None)
    if callable(name_method):
        assert str(name_method()).lower() == token.lower()
    else:
        assert getattr(color, "value") == token


def test_build_stylesheet_returns_nonempty_string(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)
    stylesheet = theme_engine.build_stylesheet()

    assert isinstance(stylesheet, str)
    assert stylesheet.strip()


def test_build_stylesheet_for_mode_light_vs_dark(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    theme_engine = ThemeEngine(fake_config)
    light_stylesheet = theme_engine.build_stylesheet_for_mode(ThemeMode.LIGHT)
    dark_stylesheet = theme_engine.build_stylesheet_for_mode(ThemeMode.DARK)

    assert light_stylesheet != dark_stylesheet
    assert "#F5F8F8" in light_stylesheet
    assert "#0F2323" in dark_stylesheet


def test_coerce_mode_handles_strings_and_enums() -> None:
    assert ThemeEngine(cast(ConfigBus, cast(object, StubConfigBus("DARK")))).current_mode == ThemeMode.DARK
    assert ThemeEngine(cast(ConfigBus, cast(object, StubConfigBus("unknown")))).current_mode == ThemeMode.LIGHT
    assert ThemeEngine(cast(ConfigBus, cast(object, StubConfigBus(ThemeMode.DARK)))).current_mode == ThemeMode.DARK
    assert ThemeEngine(cast(ConfigBus, cast(object, StubConfigBus(None)))).current_mode == ThemeMode.LIGHT


def test_config_signal_updates_engine_mode(fake_config: ConfigBus, qapp: object) -> None:
    _ = qapp
    engine = ThemeEngine(fake_config)

    fake_config.set(ConfigKey("theme.mode"), ThemeMode.DARK)

    assert engine.current_mode == ThemeMode.DARK

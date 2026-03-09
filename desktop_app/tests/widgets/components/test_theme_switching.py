from __future__ import annotations

# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportUntypedFunctionDecorator=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportUnusedCallResult=false

import pytest

from ....core.config.bus import ConfigBus
from ....core.qt import QApplication
from ....core.theme import engine as theme_engine_module
from ....core.theme.engine import ThemeEngine
from ....core.theme.qss import generate_qss
from ....core.theme.tokens import get_token_value
from ....core.types import ConfigKey, ThemeMode


def _install_stylesheet_probe(monkeypatch: pytest.MonkeyPatch, qapp: QApplication) -> list[str]:
    applied_stylesheets: list[str] = []

    def capture_stylesheet(stylesheet: str) -> None:
        applied_stylesheets.append(stylesheet)

    monkeypatch.setattr(theme_engine_module, "_get_qapplication_instance", lambda: qapp)
    monkeypatch.setattr(qapp, "setStyleSheet", capture_stylesheet, raising=False)
    monkeypatch.setattr(qapp, "styleSheet", lambda: applied_stylesheets[-1] if applied_stylesheets else "", raising=False)
    return applied_stylesheets


@pytest.mark.widget
def test_engine_applies_stylesheet_to_qapp(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    applied_stylesheets = _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    assert qapp is QApplication.instance()
    assert applied_stylesheets[-1] == engine.build_stylesheet()


@pytest.mark.widget
def test_toggle_changes_stylesheet(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    before = engine.build_stylesheet()
    engine.toggle()
    assert engine.build_stylesheet() != before


@pytest.mark.widget
def test_light_stylesheet_differs_from_dark(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    light_qss = engine.build_stylesheet_for_mode(ThemeMode.LIGHT)
    dark_qss = engine.build_stylesheet_for_mode(ThemeMode.DARK)
    assert light_qss != dark_qss
    assert light_qss == generate_qss(ThemeMode.LIGHT)
    assert dark_qss == generate_qss(ThemeMode.DARK)


@pytest.mark.widget
def test_set_mode_light_then_dark_roundtrip(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    engine.set_mode(ThemeMode.DARK)
    assert engine.current_mode == ThemeMode.DARK
    engine.set_mode(ThemeMode.LIGHT)
    assert engine.current_mode == ThemeMode.LIGHT
    engine.set_mode(ThemeMode.DARK)
    assert engine.current_mode == ThemeMode.DARK


@pytest.mark.widget
def test_theme_changed_signal_fires_on_switch(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    observed: list[str] = []
    engine.theme_changed.connect(observed.append)
    engine.toggle()
    assert observed == [ThemeMode.DARK.value]


@pytest.mark.widget
def test_get_token_after_switch_returns_new_mode_value(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    light_value = engine.get_token("surface.primary")
    engine.set_mode(ThemeMode.DARK)
    dark_value = engine.get_token("surface.primary")
    assert light_value == get_token_value("surface.primary", ThemeMode.LIGHT)
    assert dark_value == get_token_value("surface.primary", ThemeMode.DARK)
    assert dark_value != light_value


@pytest.mark.widget
def test_config_bus_persists_theme_mode_on_switch(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    engine.set_mode(ThemeMode.DARK)
    persisted = fake_config.get(ConfigKey("theme.mode"), ThemeMode.LIGHT)
    assert persisted == ThemeMode.DARK


@pytest.mark.widget
def test_multiple_rapid_toggles_consistent(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    for _ in range(7):
        engine.toggle()
    assert engine.current_mode == ThemeMode.DARK
    assert engine.build_stylesheet() == engine.build_stylesheet_for_mode(ThemeMode.DARK)


@pytest.mark.widget
def test_external_config_change_updates_engine(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    fake_config.set(ConfigKey("theme.mode"), ThemeMode.DARK)
    assert engine.current_mode == ThemeMode.DARK
    assert engine.get_token("text.primary") == get_token_value("text.primary", ThemeMode.DARK)


@pytest.mark.widget
def test_redundant_set_mode_does_not_emit_signal(
    fake_config: ConfigBus,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_stylesheet_probe(monkeypatch, qapp)
    engine = ThemeEngine(fake_config)
    observed: list[str] = []
    engine.theme_changed.connect(observed.append)
    engine.set_mode(ThemeMode.LIGHT)
    assert observed == []

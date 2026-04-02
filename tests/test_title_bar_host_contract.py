from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TITLE_BAR_VUE = ROOT / "apps" / "desktop" / "src" / "layouts" / "TitleBar.vue"
HOST_COMMANDS_TS = ROOT / "apps" / "desktop" / "src" / "modules" / "host" / "hostCommands.ts"
COMMANDS_RUNTIME_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "commands" / "runtime.rs"


def test_title_bar_uses_host_shell_data_module() -> None:
    text = TITLE_BAR_VUE.read_text(encoding="utf-8")

    assert "loadHostShellInfo" in text
    assert "restartRuntimeFromHost" in text
    assert "hostMeta" in text
    assert "onMounted" in text
    assert "handleRestartRuntime" in text
    assert "重启 Runtime" in text
    assert "currentEyebrow" in text
    assert "searchPlaceholder" in text
    assert "normalizeRuntimeStatus" in text


def test_host_commands_module_reads_tauri_invoke_and_runtime_health() -> None:
    text = HOST_COMMANDS_TS.read_text(encoding="utf-8")

    assert "__TAURI_INTERNALS__" in text
    assert "get_app_version" in text
    assert "get_app_paths" in text
    assert "runtime_health" in text
    assert "restart_runtime" in text
    assert "getRuntimeBaseUrl" in text
    assert "runtimeLaunchMode" in text
    assert "runtimeReachable" in text
    assert "lastError" in text
    assert "lastExitCode" in text
    assert "bootAttempts" in text
    assert "restartRuntimeFromHost" in text


def test_runtime_command_returns_structured_snapshot() -> None:
    text = COMMANDS_RUNTIME_RS.read_text(encoding="utf-8")

    assert "runtime_health_snapshot" in text
    assert "state.restart_runtime()" in text

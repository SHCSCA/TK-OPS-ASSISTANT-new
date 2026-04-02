from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "main.rs"
COMMANDS_RUNTIME_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "commands" / "runtime.rs"
COMMANDS_APP_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "commands" / "app.rs"
RUNTIME_MANAGER_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "runtime" / "manager.rs"
RUNTIME_MOD_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "runtime" / "mod.rs"
RUNTIME_SPAWN_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "runtime" / "spawn.rs"
RUNTIME_HEALTH_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "runtime" / "health.rs"
RUNTIME_HANDSHAKE_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "runtime" / "handshake.rs"
PATHS_MOD_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "paths" / "mod.rs"
APP_PATHS_RS = ROOT / "apps" / "desktop" / "src-tauri" / "src" / "paths" / "app_paths.rs"
BUILD_RS = ROOT / "apps" / "desktop" / "src-tauri" / "build.rs"
DEV_SCRIPT = ROOT / "scripts" / "dev.ps1"
SMOKE_SCRIPT = ROOT / "scripts" / "smoke-tauri-runtime.ps1"
TAURI_CARGO = ROOT / "apps" / "desktop" / "src-tauri" / "Cargo.toml"


def test_tauri_main_registers_runtime_commands() -> None:
    text = MAIN_RS.read_text(encoding="utf-8")

    assert "tauri::Builder::default()" in text
    assert "tauri::generate_handler!" in text
    assert "commands::app::get_app_version" in text
    assert "commands::app::get_app_paths" in text
    assert "commands::runtime::runtime_health" in text
    assert "commands::runtime::restart_runtime" in text


def test_runtime_command_module_is_not_placeholder_only() -> None:
    text = COMMANDS_RUNTIME_RS.read_text(encoding="utf-8")

    assert "runtime-health-placeholder" not in text
    assert "pub fn runtime_health" in text
    assert "pub fn restart_runtime" in text
    assert "tauri::State" in text
    assert "runtime_health_snapshot" in text
    assert "state.restart_runtime()" in text


def test_app_command_module_exposes_runtime_paths() -> None:
    text = COMMANDS_APP_RS.read_text(encoding="utf-8")

    assert "pub fn get_app_paths()" in text
    assert "discover_app_paths_json" in text


def test_runtime_manager_scaffold_exposes_named_state() -> None:
    text = RUNTIME_MANAGER_RS.read_text(encoding="utf-8")

    assert "pub struct RuntimeManagerState" in text
    assert "Mutex<" in text
    assert "pub fn runtime_health_snapshot" in text
    assert "pub fn restart_runtime" in text
    assert "spawn_runtime_process" in text
    assert "probe_runtime_endpoint" in text
    assert "runtime_session_token" in text
    assert "impl Drop for RuntimeManagerState" in text
    assert "last_exit_code" in text
    assert "boot_attempts" in text
    assert "runtime-manager-scaffold" not in text


def test_tauri_build_script_exists() -> None:
    assert BUILD_RS.exists()


def test_dev_script_syncs_runtime_env_for_new_stack() -> None:
    text = DEV_SCRIPT.read_text(encoding="utf-8")

    assert "TKOPS_RUNTIME_HOST" in text
    assert "TKOPS_RUNTIME_PORT" in text
    assert "TKOPS_RUNTIME_TOKEN" in text
    assert "VITE_RUNTIME_URL" in text
    assert "VITE_RUNTIME_TOKEN" in text
    assert "Start-Process -FilePath $python" in text
    assert "-Command" not in text


def test_smoke_script_exists_for_managed_tauri_runtime() -> None:
    text = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "VsDevCmd.bat" in text
    assert "cargo build" in text
    assert "tk_ops_desktop.exe" in text
    assert "runtime.log" in text
    assert "Stop-Process" in text


def test_runtime_modules_are_split_by_responsibility() -> None:
    text = RUNTIME_MOD_RS.read_text(encoding="utf-8")

    assert "pub mod manager;" in text
    assert "pub mod spawn;" in text
    assert "pub mod health;" in text
    assert "pub mod handshake;" in text
    assert RUNTIME_SPAWN_RS.exists()
    assert RUNTIME_HEALTH_RS.exists()
    assert RUNTIME_HANDSHAKE_RS.exists()


def test_runtime_spawn_module_knows_python_entry_and_launch_env() -> None:
    text = RUNTIME_SPAWN_RS.read_text(encoding="utf-8")

    assert "apps/py-runtime/src/main.py" in text
    assert "venv" in text
    assert "CARGO_MANIFEST_DIR" in text
    assert "TKOPS_RUNTIME_HOST" in text
    assert "TKOPS_RUNTIME_PORT" in text
    assert "TKOPS_RUNTIME_TOKEN" in text
    assert "std::process::Command" in text


def test_runtime_spawn_module_supports_alpha_bundle_layout() -> None:
    text = RUNTIME_SPAWN_RS.read_text(encoding="utf-8")

    assert "current_exe" in text
    assert "runtime" in text
    assert "main.py" in text
    assert "python.exe" in text


def test_runtime_spawn_module_reserves_random_port_for_managed_mode() -> None:
    text = RUNTIME_SPAWN_RS.read_text(encoding="utf-8")

    assert "TcpListener" in text
    assert "127.0.0.1:0" in text
    assert "TKOPS_RUNTIME_MANAGED" in text
    assert "runtime_launch_mode() == \"managed\"" in text or "launch_mode == \"managed\"" in text
    assert "\"managed\".to_string()" in text
    assert "\"external\".to_string()" in text


def test_runtime_health_module_probes_local_runtime_endpoint() -> None:
    text = RUNTIME_HEALTH_RS.read_text(encoding="utf-8")

    assert "TcpStream" in text
    assert "probe_runtime_endpoint" in text
    assert "wait_for_runtime_ready" in text
    assert "std::thread::sleep" in text
    assert "127.0.0.1" in text or "localhost" in text


def test_runtime_manager_waits_for_runtime_readiness_after_spawn() -> None:
    text = RUNTIME_MANAGER_RS.read_text(encoding="utf-8")

    assert "wait_for_runtime_ready" in text
    assert "managed-running" in text
    assert "managed-timeout" in text or "managed-starting" in text
    assert "managed-exited" in text or "managed-crashed" in text
    assert "try_wait" in text


def test_runtime_manager_has_bounded_auto_recovery_for_managed_runtime() -> None:
    text = RUNTIME_MANAGER_RS.read_text(encoding="utf-8")

    assert "MAX_BOOT_ATTEMPTS" in text
    assert "RECOVERY_COOLDOWN_MS" in text
    assert "maybe_recover_managed_runtime" in text
    assert "managed-restarting" in text or "managed-recovery-failed" in text
    assert "boot_attempts < MAX_BOOT_ATTEMPTS" in text
    assert "recovery_allowed_at_ms" in text or "last_recovery_at_ms" in text


def test_runtime_manager_avoids_duplicate_managed_spawn_when_child_is_alive() -> None:
    text = RUNTIME_MANAGER_RS.read_text(encoding="utf-8")

    assert "spawn skipped: existing managed runtime process is still alive" in text or "managed-already-running" in text
    assert "existing_child_pid" in text or "child.as_mut()" in text
    assert "probe_runtime_endpoint(&self.launch_plan.endpoint)" in text


def test_tauri_cargo_adds_json_support_for_runtime_snapshots() -> None:
    text = TAURI_CARGO.read_text(encoding="utf-8")

    assert "serde" in text
    assert "serde_json" in text


def test_tauri_path_modules_are_split_from_commands() -> None:
    mod_text = PATHS_MOD_RS.read_text(encoding="utf-8")
    app_paths_text = APP_PATHS_RS.read_text(encoding="utf-8")

    assert "pub mod app_paths;" in mod_text
    assert "pub struct AppPaths" in app_paths_text
    assert "current_dir" in app_paths_text or "current_exe" in app_paths_text
    assert "serde_json::to_string" in app_paths_text

use std::net::TcpListener;
use std::path::{Path, PathBuf};
use std::process::{Child, Stdio};

const DEFAULT_RUNTIME_ENTRY_RELATIVE: &str = "apps/py-runtime/src/main.py";
const BUNDLED_RUNTIME_ENTRY_RELATIVE: &str = "runtime/src/main.py";
const BUNDLED_PYTHON_RELATIVE: &str = "python/python.exe";

#[derive(Clone, Debug)]
pub struct RuntimeLaunchPlan {
    pub endpoint: String,
    pub host: String,
    pub port: u16,
    pub token: String,
    pub python_executable: String,
    pub runtime_entry: String,
    pub launch_mode: String,
}

fn env_text(name: &str, default: &str) -> String {
    std::env::var(name)
        .ok()
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
        .unwrap_or_else(|| default.to_string())
}

fn env_bool(name: &str, default: bool) -> bool {
    std::env::var(name)
        .ok()
        .map(|value| {
            matches!(
                value.trim().to_ascii_lowercase().as_str(),
                "1" | "true" | "yes" | "on"
            )
        })
        .unwrap_or(default)
}

fn manifest_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn repo_root_dir() -> PathBuf {
    manifest_dir()
        .parent()
        .and_then(Path::parent)
        .and_then(Path::parent)
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("."))
}

fn current_exe_dir() -> Option<PathBuf> {
    std::env::current_exe()
        .ok()
        .and_then(|path| path.parent().map(Path::to_path_buf))
}

fn explicit_runtime_entry() -> Option<String> {
    std::env::var("TKOPS_RUNTIME_ENTRY")
        .ok()
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
}

fn runtime_entry_candidates() -> Vec<PathBuf> {
    let mut candidates = Vec::new();

    if let Some(explicit) = explicit_runtime_entry() {
        candidates.push(PathBuf::from(explicit));
    }

    if let Some(current_dir) = current_exe_dir() {
        candidates.push(current_dir.join(BUNDLED_RUNTIME_ENTRY_RELATIVE));
    }

    candidates.push(repo_root_dir().join(DEFAULT_RUNTIME_ENTRY_RELATIVE));
    candidates
}

fn first_existing_path(candidates: &[PathBuf]) -> Option<PathBuf> {
    candidates.iter().find(|candidate| candidate.exists()).cloned()
}

fn runtime_host() -> String {
    env_text("TKOPS_RUNTIME_HOST", "127.0.0.1")
}

fn explicit_runtime_port() -> Option<u16> {
    std::env::var("TKOPS_RUNTIME_PORT")
        .ok()
        .and_then(|value| value.trim().parse::<u16>().ok())
}

fn runtime_launch_mode() -> String {
    if env_bool("TKOPS_RUNTIME_MANAGED", true) {
        return "managed".to_string();
    }
    "external".to_string()
}

fn bundled_python_candidate() -> Option<PathBuf> {
    current_exe_dir()
        .map(|dir| dir.join(BUNDLED_PYTHON_RELATIVE))
        .filter(|path| path.exists())
}

fn venv_python_candidate() -> PathBuf {
    repo_root_dir().join("venv").join("Scripts").join("python.exe")
}

fn python_executable() -> String {
    if let Ok(explicit_python) = std::env::var("TKOPS_RUNTIME_PYTHON") {
        let normalized = explicit_python.trim();
        if !normalized.is_empty() {
            return normalized.to_string();
        }
    }

    if let Some(bundled_python) = bundled_python_candidate() {
        return bundled_python.display().to_string();
    }

    let venv_python = venv_python_candidate();
    if venv_python.exists() {
        return venv_python.display().to_string();
    }

    "python".to_string()
}

fn reserve_local_runtime_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .ok()
        .and_then(|listener| listener.local_addr().ok())
        .map(|address| address.port())
        .unwrap_or(8765)
}

fn runtime_port(launch_mode: &str) -> u16 {
    if let Some(port) = explicit_runtime_port() {
        return port;
    }
    if runtime_launch_mode() == "managed" || launch_mode == "managed" {
        return reserve_local_runtime_port();
    }
    8765
}

fn runtime_entry_path() -> String {
    first_existing_path(&runtime_entry_candidates())
        .unwrap_or_else(|| repo_root_dir().join(DEFAULT_RUNTIME_ENTRY_RELATIVE))
        .display()
        .to_string()
}

pub fn build_runtime_launch_plan(token: String) -> RuntimeLaunchPlan {
    let launch_mode = runtime_launch_mode();
    let host = runtime_host();
    let port = runtime_port(&launch_mode);
    RuntimeLaunchPlan {
        endpoint: format!("http://{host}:{port}"),
        host,
        port,
        token,
        python_executable: python_executable(),
        runtime_entry: runtime_entry_path(),
        launch_mode,
    }
}

pub fn spawn_runtime_process(plan: &RuntimeLaunchPlan) -> Result<Child, String> {
    if plan.launch_mode != "managed" {
        return Err("runtime.launch_mode_not_managed".to_string());
    }

    std::process::Command::new(&plan.python_executable)
        .arg(&plan.runtime_entry)
        .env("TKOPS_RUNTIME_HOST", &plan.host)
        .env("TKOPS_RUNTIME_PORT", plan.port.to_string())
        .env("TKOPS_RUNTIME_TOKEN", &plan.token)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|error| error.to_string())
}

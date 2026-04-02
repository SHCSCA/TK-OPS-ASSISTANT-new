use std::process::{Child, ExitStatus};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

use serde::Serialize;

use crate::runtime::handshake::runtime_session_token;
use crate::runtime::health::{probe_runtime_endpoint, wait_for_runtime_ready};
use crate::runtime::spawn::{build_runtime_launch_plan, spawn_runtime_process, RuntimeLaunchPlan};

const MAX_BOOT_ATTEMPTS: u32 = 3;
const RECOVERY_COOLDOWN_MS: u64 = 2_500;

#[derive(Clone, Debug, Serialize)]
pub struct RuntimeSnapshot {
    pub status: String,
    pub endpoint: String,
    pub launch_mode: String,
    pub reachable: bool,
    pub token_present: bool,
    pub python_executable: String,
    pub runtime_entry: String,
    pub pid: Option<u32>,
    pub last_error: Option<String>,
    pub last_exit_code: Option<i32>,
    pub boot_attempts: u32,
    pub recovery_allowed_at_ms: u64,
}

#[derive(Clone, Debug, Serialize)]
struct RuntimeActionResult {
    action: String,
    status: String,
    snapshot: RuntimeSnapshot,
}

pub struct RuntimeManagerState {
    launch_plan: RuntimeLaunchPlan,
    snapshot: Mutex<RuntimeSnapshot>,
    child: Mutex<Option<Child>>,
}

impl RuntimeManagerState {
    fn now_ms() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|duration| duration.as_millis() as u64)
            .unwrap_or_default()
    }

    fn bootstrap_snapshot(plan: &RuntimeLaunchPlan) -> RuntimeSnapshot {
        let reachable = probe_runtime_endpoint(&plan.endpoint);
        let status = if plan.launch_mode == "managed" {
            "managed-idle"
        } else if reachable {
            "external-reachable"
        } else {
            "external-unreachable"
        };

        RuntimeSnapshot {
            status: status.to_string(),
            endpoint: plan.endpoint.clone(),
            launch_mode: plan.launch_mode.clone(),
            reachable,
            token_present: !plan.token.is_empty(),
            python_executable: plan.python_executable.clone(),
            runtime_entry: plan.runtime_entry.clone(),
            pid: None,
            last_error: None,
            last_exit_code: None,
            boot_attempts: 0,
            recovery_allowed_at_ms: 0,
        }
    }

    fn lock_snapshot(&self) -> std::sync::MutexGuard<'_, RuntimeSnapshot> {
        self.snapshot.lock().expect("runtime snapshot mutex poisoned")
    }

    fn lock_child(&self) -> std::sync::MutexGuard<'_, Option<Child>> {
        self.child.lock().expect("runtime child mutex poisoned")
    }

    fn child_exit_code(status: ExitStatus) -> i32 {
        status.code().unwrap_or(-1)
    }

    fn sync_child_exit_status(&self) -> Option<i32> {
        let mut child = self.lock_child();
        let Some(process) = child.as_mut() else {
            return None;
        };

        match process.try_wait() {
            Ok(Some(status)) => {
                let exit_code = Self::child_exit_code(status);
                *child = None;
                Some(exit_code)
            }
            Ok(None) => None,
            Err(error) => {
                let mut snapshot = self.lock_snapshot();
                snapshot.last_error = Some(format!("runtime.try_wait_failed: {error}"));
                None
            }
        }
    }

    fn managed_exit_status(exit_code: i32) -> String {
        if exit_code == 0 {
            return "managed-exited".to_string();
        }
        "managed-crashed".to_string()
    }

    fn should_attempt_recovery(snapshot: &RuntimeSnapshot) -> bool {
        snapshot.launch_mode == "managed"
            && snapshot.pid.is_none()
            && !snapshot.reachable
            && snapshot.last_exit_code.is_some()
            && snapshot.boot_attempts < MAX_BOOT_ATTEMPTS
            && Self::now_ms() >= snapshot.recovery_allowed_at_ms
            && matches!(
                snapshot.status.as_str(),
                "managed-exited" | "managed-crashed"
            )
    }

    fn maybe_recover_managed_runtime(&self, snapshot: &RuntimeSnapshot) -> Option<RuntimeSnapshot> {
        if !Self::should_attempt_recovery(snapshot) {
            return None;
        }

        {
            let mut locked_snapshot = self.lock_snapshot();
            locked_snapshot.status = "managed-restarting".to_string();
        }

        match self.spawn_managed_runtime() {
            Ok(Some(pid)) => Some(self.finalize_managed_bootstrap(pid)),
            Ok(None) => None,
            Err(error) => {
                let mut locked_snapshot = self.lock_snapshot();
                locked_snapshot.status = "managed-recovery-failed".to_string();
                locked_snapshot.last_error = Some(error);
                Some(locked_snapshot.clone())
            }
        }
    }

    fn refresh_snapshot(&self) -> RuntimeSnapshot {
        let exit_code = self.sync_child_exit_status();
        let pid = self.lock_child().as_ref().map(|child| child.id());
        let reachable = probe_runtime_endpoint(&self.launch_plan.endpoint);
        let mut snapshot = self.lock_snapshot();

        if let Some(code) = exit_code {
            snapshot.last_exit_code = Some(code);
            snapshot.recovery_allowed_at_ms = Self::now_ms() + RECOVERY_COOLDOWN_MS;
            if code != 0 {
                snapshot.last_error = Some(format!("runtime exited with code {code}"));
            }
        }

        snapshot.pid = pid;
        snapshot.reachable = reachable;
        snapshot.status = match (
            snapshot.launch_mode.as_str(),
            pid,
            reachable,
            snapshot.last_exit_code,
            snapshot.boot_attempts,
        ) {
            ("managed", Some(_), true, _, _) => "managed-running".to_string(),
            ("managed", Some(_), false, _, _) => "managed-starting".to_string(),
            ("managed", None, true, _, _) => "managed-runtime-detected".to_string(),
            ("managed", None, false, Some(_), attempts) if attempts >= MAX_BOOT_ATTEMPTS => {
                "managed-recovery-failed".to_string()
            }
            ("managed", None, false, Some(code), _) => Self::managed_exit_status(code),
            ("managed", None, false, None, _) => "managed-idle".to_string(),
            (_, _, true, _, _) => "external-reachable".to_string(),
            _ => "external-unreachable".to_string(),
        };

        let snapshot_clone = snapshot.clone();
        drop(snapshot);

        self.maybe_recover_managed_runtime(&snapshot_clone)
            .unwrap_or(snapshot_clone)
    }

    fn stop_existing_child(&self) {
        let mut child = self.lock_child();
        if let Some(process) = child.as_mut() {
            let _ = process.kill();
            let _ = process.wait();
        }
        *child = None;
    }

    fn spawn_managed_runtime(&self) -> Result<Option<u32>, String> {
        if self.launch_plan.launch_mode != "managed" {
            return Ok(None);
        }

        {
            let mut child = self.lock_child();
            if let Some(process) = child.as_mut() {
                match process.try_wait() {
                    Ok(None) => {
                        let pid = process.id();
                        let mut snapshot = self.lock_snapshot();
                        snapshot.pid = Some(pid);
                        snapshot.status = "managed-already-running".to_string();
                        snapshot.last_error =
                            Some("spawn skipped: existing managed runtime process is still alive".to_string());
                        return Ok(Some(pid));
                    }
                    Ok(Some(_)) => {
                        *child = None;
                    }
                    Err(error) => {
                        let mut snapshot = self.lock_snapshot();
                        snapshot.last_error = Some(format!("runtime.try_wait_failed: {error}"));
                    }
                }
            }
        }

        if probe_runtime_endpoint(&self.launch_plan.endpoint) {
            let mut snapshot = self.lock_snapshot();
            snapshot.status = "managed-already-running".to_string();
            snapshot.reachable = true;
            snapshot.last_error =
                Some("spawn skipped: managed runtime endpoint is already reachable".to_string());
            return Ok(None);
        }

        {
            let mut snapshot = self.lock_snapshot();
            snapshot.boot_attempts += 1;
            snapshot.last_exit_code = None;
            snapshot.recovery_allowed_at_ms = 0;
        }

        let child = spawn_runtime_process(&self.launch_plan)?;
        let pid = child.id();
        *self.lock_child() = Some(child);
        Ok(Some(pid))
    }

    fn finalize_managed_bootstrap(&self, pid: u32) -> RuntimeSnapshot {
        let ready = wait_for_runtime_ready(
            &self.launch_plan.endpoint,
            20,
            std::time::Duration::from_millis(250),
        );
        let mut snapshot = self.lock_snapshot();
        snapshot.pid = Some(pid);
        snapshot.reachable = ready;
        snapshot.status = if ready {
            "managed-running".to_string()
        } else {
            "managed-timeout".to_string()
        };
        snapshot.clone()
    }

    fn set_last_error(&self, error: Option<String>) {
        let mut snapshot = self.lock_snapshot();
        snapshot.last_error = error;
    }

    pub fn runtime_health_snapshot(&self) -> String {
        let snapshot = self.refresh_snapshot();
        serde_json::to_string(&snapshot).unwrap_or_else(|_| {
            "{\"status\":\"runtime-health-serialize-error\"}".to_string()
        })
    }

    pub fn restart_runtime(&self) -> String {
        self.stop_existing_child();
        self.set_last_error(None);

        let action_result = match self.spawn_managed_runtime() {
            Ok(Some(pid)) => RuntimeActionResult {
                action: "restart-runtime".to_string(),
                status: "spawned".to_string(),
                snapshot: self.finalize_managed_bootstrap(pid),
            },
            Ok(None) => RuntimeActionResult {
                action: "restart-runtime".to_string(),
                status: "external-runtime-unchanged".to_string(),
                snapshot: self.refresh_snapshot(),
            },
            Err(error) => {
                self.set_last_error(Some(error.clone()));
                RuntimeActionResult {
                    action: "restart-runtime".to_string(),
                    status: "spawn-failed".to_string(),
                    snapshot: self.refresh_snapshot(),
                }
            }
        };

        serde_json::to_string(&action_result).unwrap_or_else(|_| {
            "{\"action\":\"restart-runtime\",\"status\":\"serialize-error\"}".to_string()
        })
    }
}

impl Default for RuntimeManagerState {
    fn default() -> Self {
        let plan = build_runtime_launch_plan(runtime_session_token());
        let state = Self {
            snapshot: Mutex::new(Self::bootstrap_snapshot(&plan)),
            child: Mutex::new(None),
            launch_plan: plan,
        };

        if state.launch_plan.launch_mode == "managed" {
            match state.spawn_managed_runtime() {
                Ok(Some(pid)) => {
                    let _ = state.finalize_managed_bootstrap(pid);
                }
                Ok(None) => {}
                Err(error) => {
                    state.set_last_error(Some(error));
                }
            }
        }

        state
    }
}

impl Drop for RuntimeManagerState {
    fn drop(&mut self) {
        self.stop_existing_child();
    }
}

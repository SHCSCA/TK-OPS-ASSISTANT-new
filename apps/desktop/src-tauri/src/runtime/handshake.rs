use std::time::{SystemTime, UNIX_EPOCH};

fn env_runtime_token() -> Option<String> {
    std::env::var("TKOPS_RUNTIME_TOKEN")
        .ok()
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty())
}

pub fn runtime_session_token() -> String {
    if let Some(token) = env_runtime_token() {
        return token;
    }

    let entropy = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_nanos())
        .unwrap_or_default();
    format!("tkops-session-{:x}-{:x}", std::process::id(), entropy)
}

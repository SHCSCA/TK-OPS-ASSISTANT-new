use serde::Serialize;

#[derive(Clone, Debug, Serialize)]
pub struct AppPaths {
    pub current_dir: String,
    pub current_exe: String,
}

pub fn discover_app_paths_json() -> String {
    let current_dir = std::env::current_dir()
        .ok()
        .map(|path| path.display().to_string())
        .unwrap_or_default();
    let current_exe = std::env::current_exe()
        .ok()
        .map(|path| path.display().to_string())
        .unwrap_or_default();

    serde_json::to_string(&AppPaths {
        current_dir,
        current_exe,
    })
    .unwrap_or_else(|_| "{\"current_dir\":\"\",\"current_exe\":\"\"}".to_string())
}

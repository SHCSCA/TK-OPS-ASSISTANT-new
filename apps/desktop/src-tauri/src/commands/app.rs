#[tauri::command]
pub fn get_app_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[tauri::command]
pub fn get_app_paths() -> String {
    crate::paths::app_paths::discover_app_paths_json()
}

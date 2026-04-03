use tauri::Manager;

#[tauri::command]
pub fn get_app_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[tauri::command]
pub fn get_app_paths() -> String {
    crate::paths::app_paths::discover_app_paths_json()
}

#[tauri::command]
pub fn app_shell_ready(app: tauri::AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        window.show().map_err(|error| format!("show main window failed: {error}"))?;
        let _ = window.set_focus();
    }
    if let Some(window) = app.get_webview_window("splash") {
        let _ = window.close();
    }
    Ok(())
}

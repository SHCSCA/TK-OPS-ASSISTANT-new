#[tauri::command]
pub fn runtime_health(state: tauri::State<'_, crate::runtime::manager::RuntimeManagerState>) -> String {
    state.runtime_health_snapshot()
}

#[tauri::command]
pub fn restart_runtime(state: tauri::State<'_, crate::runtime::manager::RuntimeManagerState>) -> String {
    state.restart_runtime()
}

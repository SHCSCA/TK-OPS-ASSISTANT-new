mod commands;
mod paths;
mod runtime;

fn main() {
    tauri::Builder::default()
        .manage(runtime::manager::RuntimeManagerState::default())
        .invoke_handler(tauri::generate_handler![
            commands::app::get_app_version,
            commands::app::get_app_paths,
            commands::runtime::runtime_health,
            commands::runtime::restart_runtime,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run TK-OPS desktop host");
}

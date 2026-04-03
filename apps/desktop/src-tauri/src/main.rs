mod commands;
mod paths;
mod runtime;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                std::thread::sleep(std::time::Duration::from_secs(20));
                if let Some(window) = handle.get_webview_window("main") {
                    match window.is_visible() {
                        Ok(false) => {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                        Ok(true) => {}
                        Err(_) => {
                            let _ = window.show();
                        }
                    }
                }
                if let Some(window) = handle.get_webview_window("splash") {
                    let _ = window.close();
                }
            });
            Ok(())
        })
        .manage(runtime::manager::RuntimeManagerState::default())
        .invoke_handler(tauri::generate_handler![
            commands::app::get_app_version,
            commands::app::get_app_paths,
            commands::app::app_shell_ready,
            commands::runtime::runtime_health,
            commands::runtime::restart_runtime,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run TK-OPS desktop host");
}

use tauri::Emitter;

pub mod commands {
    pub mod backup;
    pub mod dispatch;
    pub mod recovery;
    pub mod restore;
}

pub mod python_bridge;

#[cfg(test)]
mod tests;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            use tauri::Manager;
            let window = app.get_webview_window("main").unwrap();
            let window_clone = window.clone();

            window.on_window_event(move |event| match event {
                tauri::WindowEvent::DragDrop(tauri::DragDropEvent::Enter { paths, .. }) => {
                    println!("🔍 [RUST DEBUG] File Hover detected: {:?}", paths);
                }
                tauri::WindowEvent::DragDrop(tauri::DragDropEvent::Drop { paths, .. }) => {
                    println!("✅ [RUST DEBUG] File Dropped: {:?}", paths);
                    window_clone.emit("file-uploaded", &paths).unwrap();
                }
                tauri::WindowEvent::DragDrop(tauri::DragDropEvent::Leave { .. }) => {
                    println!("❌ [RUST DEBUG] File Drop Cancelled/Left");
                }
                _ => {}
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::backup::cmd_backup_start,
            commands::recovery::cmd_export_recovery_svg,
            commands::restore::cmd_restore_backup,
            commands::dispatch::cmd_dispatch,
            commands::dispatch::cmd_restore_from_file
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

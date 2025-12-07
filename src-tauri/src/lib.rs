pub mod commands;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        // .plugin(tauri_plugin_fs::init()) // Commented out to avoid dependency error
        .invoke_handler(tauri::generate_handler![
            // ONLY OMEGA PROTOCOL COMMANDS
            commands::backup::cmd_backup_start,
            commands::recovery::cmd_export_recovery_svg
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

pub mod commands { pub mod recovery_export; }
use commands::recovery_export::*;
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .expect("error while running tauri application");
}
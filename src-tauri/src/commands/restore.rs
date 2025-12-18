//! Restore Command - Wires Frontend to Python via PyO3 Bridge
//!
//! Phase 3 E2E Integration: DropZone/FilePicker → Rust → Python

use crate::python_bridge;
use serde_json::json;
use tauri::command;

/// Restore backup from .cvbak file
///
/// This is the E2E connection point:
/// Frontend (DropZone/FilePicker) → This Command → PyO3 Bridge → Python Dispatcher
#[command]
pub fn cmd_restore_backup(path: String) -> Result<String, String> {
    // Validate file extension
    if !path.to_lowercase().ends_with(".cvbak") {
        return Err("Invalid file format. Expected .cvbak".into());
    }

    println!("🔌 [RUST] cmd_restore_backup called with: {}", path);

    // Create payload for Python Dispatcher
    let payload = json!({
        "path": path
    });

    // Call Python via PyO3 Bridge
    match python_bridge::dispatch_to_python("restore.start", payload) {
        Ok(result) => {
            println!("✅ [RUST] Python returned: {:?}", result);

            // Check Python response status
            if result["status"] == "success" {
                Ok(format!(
                    "Restore initiated: {}",
                    result["message"].as_str().unwrap_or("OK")
                ))
            } else {
                Err(format!(
                    "Python error: {}",
                    result["message"].as_str().unwrap_or("Unknown error")
                ))
            }
        }
        Err(e) => {
            println!("❌ [RUST] Python bridge error: {}", e);
            Err(format!("Bridge error: {}", e))
        }
    }
}

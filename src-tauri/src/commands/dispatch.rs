//! Dispatch Command - Exposes Python bridge to Tauri frontend.
//!
//! MDS v3.14: Rust (Muscle) controls Python (Brain) via PyO3.

use crate::python_bridge;
use serde_json::Value;
use tauri::command;

/// Tauri command to dispatch requests to Python Core.
///
/// # Arguments
/// * `cmd` - Command string (e.g., "backup.start")
/// * `payload` - JSON payload for the command
///
/// # Returns
/// * JSON response from Python Dispatcher
#[command]
pub async fn cmd_dispatch(cmd: String, payload: Value) -> Result<Value, String> {
    // Delegate to Python bridge
    python_bridge::dispatch_to_python(&cmd, payload)
}

/// Tauri command to restore backup from .cvbak file.
///
/// This is the E2E entry point from DropZone drag-drop.
#[command]
pub async fn cmd_restore_from_file(file_path: String) -> Result<Value, String> {
    let payload = serde_json::json!({
        "file_path": file_path
    });

    python_bridge::dispatch_to_python("restore.start", payload)
}

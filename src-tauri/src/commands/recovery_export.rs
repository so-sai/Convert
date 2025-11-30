use tauri::command;

#[command]
pub fn generate_recovery_phrase() -> Result<String, String> {
    Ok("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about".to_string())
}

#[command]
pub fn export_recovery_qr(phrase: String) -> Result<String, String> {
    // Mock implementation - return simple base64 of 1x1 transparent pixel
    Ok("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==".to_string())
}
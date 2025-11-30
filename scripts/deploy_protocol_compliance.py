import os
import shutil
import base64
import sys
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path.cwd()
TAURI_DIR = ROOT / "src-tauri"
RUST_SRC = TAURI_DIR / "src"
RUST_CMD_DIR = RUST_SRC / "commands"
ICONS_DIR = TAURI_DIR / "icons"

def log(msg):
    print(f"✅ {msg}")

def error(msg):
    print(f"❌ {msg}")

def write_file(path, content):
    """Rule #9: Write files using Python I/O, not Shell redirects"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    log(f"Wrote: {path.relative_to(ROOT)}")

def clean_ghosts():
    """Rule #16: The Ghost Protocol - Clean artifacts before building"""
    targets = [
        TAURI_DIR / "target",
        TAURI_DIR / "gen",
        # Không xóa node_modules để tiết kiệm thời gian npm install, 
        # nhưng nếu lỗi lạ thì nên xóa thủ công.
    ]
    for t in targets:
        if t.exists():
            try:
                shutil.rmtree(t)
                log(f"Cleaned ghost: {t.relative_to(ROOT)}")
            except Exception as e:
                error(f"Cannot clean {t}: {e} (Windows Lock?)")

# --- FILE CONTENTS (SSOT) ---

# Cargo.toml: Fix Dependency Hell (qrcode 0.14 <-> image 0.24)
CARGO_TOML = r"""
[package]
name = "convert-vault"
version = "0.1.0"
description = "Omega Vault"
authors = ["Convert Team"]
edition = "2021"

[build-dependencies]
tauri-build = { version = "2.0.1", features = [] }

[dependencies]
tauri = { version = "2.1.0", features = [] }
tauri-plugin-shell = "2.0.1"
tauri-plugin-dialog = "2.0.1"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
# RULE: Explicit version pinning to avoid Trait Bound Errors
qrcode = { version = "0.14", default-features = false, features = ["image"] }
image = "0.24.9"
base64 = "0.22"
"""

# lib.rs: Fix Syntax Error (.expect on Builder)
LIB_RS = r"""
pub mod commands;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            commands::recovery_export::export_recovery_qr
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
"""

MOD_RS = "pub mod recovery_export;"

# recovery_export.rs: Fix Logic Error (Luma<u8> Trait)
RECOVERY_EXPORT_RS = r"""
use tauri::command;
use qrcode::QrCode;
use image::Luma;
use base64::{Engine as _, engine::general_purpose};
use std::io::Cursor;

#[command]
pub fn export_recovery_qr(phrase: String) -> Result<String, String> {
    // 1. Generate Code
    let code = QrCode::new(phrase.as_bytes()).map_err(|e| e.to_string())?;

    // 2. Render Image (Compatible with qrcode 0.14 + image 0.24)
    let image = code.render::<Luma<u8>>()
        .min_dimensions(200, 200)
        .build();

    // 3. Write to Buffer
    let mut cursor = Cursor::new(Vec::new());
    image.write_to(&mut cursor, image::ImageFormat::Png)
        .map_err(|e| e.to_string())?;

    // 4. Base64 Encode
    let base64_str = general_purpose::STANDARD.encode(cursor.get_ref());
    Ok(format!("data:image/png;base64,{}", base64_str))
}
"""

# main.rs: Standard Windows Entry
MAIN_RS = r"""
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
fn main() {
    convert_vault::run();
}
"""

# 1x1 Pixel Transparent PNG (Bypass "failed to fill whole buffer" error)
ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

def main():
    print("🛡️ EXECUTING DEPLOYMENT PROTOCOL (PKSF COMPLIANT)...")
    
    # 1. Clean Environment
    clean_ghosts()

    # 2. Write Configs & Code (Overwrite Strategy)
    write_file(TAURI_DIR / "Cargo.toml", CARGO_TOML)
    write_file(RUST_SRC / "lib.rs", LIB_RS)
    write_file(RUST_SRC / "main.rs", MAIN_RS)
    write_file(RUST_CMD_DIR / "mod.rs", MOD_RS)
    write_file(RUST_CMD_DIR / "recovery_export.rs", RECOVERY_EXPORT_RS)

    # 3. Generate Valid Assets (Avoid File Corruption)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    icon_data = base64.b64decode(ICON_B64)
    for name in ["icon.png", "icon.ico", "32x32.png", "128x128.png", "Square30x30Logo.png", "Square44x44Logo.png"]:
        path = ICONS_DIR / name
        with open(path, "wb") as f:
            f.write(icon_data)
        log(f"Generated Asset: {name}")

    print("\n🚀 PROTOCOL COMPLETE. READY FOR LAUNCH.")
    print("👉 COMMANDS:")
    print("   cd src-tauri")
    print("   npm run tauri dev")

if __name__ == "__main__":
    main()

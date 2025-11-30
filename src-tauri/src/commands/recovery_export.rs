use tauri::command;
use zeroize::{Zeroize, ZeroizeOnDrop};
use bip39::{Mnemonic, MnemonicType, Language};
use qrcode::QrCode;
use image::{ImageBuffer, Luma};
use base64::{Engine as _, engine::general_purpose};
use std::io::Cursor;

#[derive(Zeroize, ZeroizeOnDrop)]
pub struct SensitiveRecoveryData {
    pub phrase: String,
    pub svg_base64: String,
}

#[command]
pub fn generate_recovery_phrase() -> Result<String, String> {
    let mnemonic = Mnemonic::new(MnemonicType::Words12, Language::English);
    Ok(mnemonic.phrase().to_string())
}

#[command]
pub fn export_recovery_image(mut phrase: String) -> Result<String, String> {
    let mut sensitive_bytes = phrase.into_bytes();
    let code = QrCode::new(&sensitive_bytes).map_err(|e| { sensitive_bytes.zeroize(); e.to_string() })?;
    let image_buffer = code.render::<Luma<u8>>().min_dimensions(200, 200).to_image();
    let mut cursor = Cursor::new(Vec::new());
    image_buffer.write_to(&mut cursor, image::ImageFormat::Png).map_err(|e| { sensitive_bytes.zeroize(); e.to_string() })?;
    let base64_string = general_purpose::STANDARD.encode(cursor.get_ref());
    sensitive_bytes.zeroize();
}
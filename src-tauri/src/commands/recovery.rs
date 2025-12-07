use serde::Serialize;

#[derive(Serialize)]
pub struct ExportResp {
    pub data_uri: String,
    pub ttl_seconds: u64,
}

/// BLIND PROTOCOL: Recovery phrase export
///
/// Frontend NEVER receives plaintext mnemonic.
/// Returns SVG as data:image URI with TTL for auto-wipe.
#[tauri::command]
pub fn cmd_export_recovery_svg(auth: String) -> Result<ExportResp, String> {
    // Security validation
    if auth.is_empty() {
        return Err("Authentication required".into());
    }

    // BLIND PROTOCOL: Generate SVG in Rust, never expose mnemonic
    // For Sprint 5, return placeholder. Sprint 6 will use bip39 + qrcode + zeroize

    use base64::{engine::general_purpose, Engine as _};

    // Simple placeholder SVG (no special characters that break Rust strings)
    let svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"300\" height=\"150\"><rect width=\"100%\" height=\"100%\" fill=\"#1a1a2e\"/><text x=\"50%\" y=\"50%\" text-anchor=\"middle\" fill=\"#4ade80\" font-size=\"14\">Recovery Key Placeholder</text></svg>";

    let b64 = general_purpose::STANDARD.encode(svg.as_bytes());

    Ok(ExportResp {
        data_uri: format!("data:image/svg+xml;base64,{}", b64),
        ttl_seconds: 60,
    })
}

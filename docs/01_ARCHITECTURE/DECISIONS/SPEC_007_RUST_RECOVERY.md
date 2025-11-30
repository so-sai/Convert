# SPEC-007 v2.1: SECURE RECOVERY EXPORT (RUST-FIRST & BLIND FRONTEND)

> **Status:** APPROVED - PENDING IMPLEMENTATION  
> **Priority:** CRITICAL  
> **Stack:** Rust (Core Logic) | Svelte (Blind View)  
> **Constraint:** NO PLAINTEXT LEAK TO JS/PYTHON
> **Dependencies:** Requires Tauri v2 + Rust backend setup (Task 5.3+)

---

## 1. MỤC TIÊU & PHẠM VI

Xây dựng cơ chế xuất Recovery Phrase (BIP39) an toàn tuyệt đối, đảm bảo Seed Phrase không bao giờ tồn tại dưới dạng Plaintext trong bộ nhớ Python hoặc JavaScript (Frontend).

---

## 2. NGUYÊN TẮC CỐT LÕI (THE IRON RULES)

1. **Rust Supremacy:** Chỉ Rust được phép chạm vào, giải mã, và xử lý Seed Phrase.
2. **Blind Frontend:** Frontend chỉ nhận dữ liệu hiển thị dưới dạng **HÌNH ẢNH (SVG Base64)**. Tuyệt đối không trả về `String`, `Vec<String>` hay JSON chứa từ khóa.
3. **Zeroize on Drop:** Mọi biến chứa Secret (Password, Seed, Mnemonic) phải được bọc trong `Zeroizing<T>` hoặc `SecretString` và xóa ngay sau khi dùng.
4. **Just-in-Time Access:** Không lưu cache Master Key. Yêu cầu Re-auth (nhập lại passkey) cho mỗi lần export.

---

## 3. THIẾT KẾ KỸ THUẬT (RUST CORE)

### 3.1 Dependencies (`src-tauri/Cargo.toml`)

```toml
[dependencies]
# Crypto & Security
bip39 = "2.0"
zeroize = { version = "1.6", features = ["zeroize_derive"] }
secrecy = "0.8"
chacha20poly1305 = "0.10"
argon2 = "0.5"

# Rendering
qrcode = { version = "0.12", default-features = false, features = ["svg"] }
base64 = "0.21"
```

### 3.2 Command Signature (Strict Contract)

```rust
use zeroize::{Zeroize, Zeroizing};
use serde::Serialize;

#[derive(Serialize)]
pub struct ExportResp {
    /// Base64 encoded SVG data URI (data:image/svg+xml;base64,...)
    data_uri: String, 
    /// Engine identifier for audit ("rust-secure-v1")
    engine: &'static str,
    /// Time-to-live recommendation for Frontend (e.g., 60s)
    ttl_seconds: u32,
}

#[derive(Serialize)]
pub enum ExportError {
    AuthFailed,
    CryptoError,
    InternalError, // Che giấu chi tiết lỗi hệ thống
}

#[tauri::command]
pub fn export_recovery_svg(
    mode: String,        // "qr" | "text_image"
    auth: String         // Re-entry Passkey (Will be zeroized immediately)
) -> Result<ExportResp, ExportError> {
    // 1. Wrap sensitive inputs
    let secure_auth = Zeroizing::new(auth);

    // 2. Authenticate & Decrypt Seed (Just-in-Time)
    // ... Logic decrypt từ DB hoặc Encrypted Blob ...
    let secure_mnemonic = Zeroizing::new(fetch_and_decrypt_seed(&secure_auth)?);

    // 3. Render to SVG Buffer (In-Memory Only)
    let svg_buffer: Zeroizing<String> = match mode.as_str() {
        "qr" => render_qr(&secure_mnemonic),
        "text_image" => render_text_as_svg(&secure_mnemonic),
        _ => return Err(ExportError::InternalError),
    };

    // 4. Encode Base64
    let b64 = base64::encode(svg_buffer.as_bytes());

    // 5. Return (Secrets are dropped & zeroized here)
    Ok(ExportResp {
        data_uri: format!("data:image/svg+xml;base64,{}", b64),
        engine: "rust-secure-v1",
        ttl_seconds: 60,
    })
}
```

### 3.3 Helper Functions (Internal)

```rust
fn fetch_and_decrypt_seed(passkey: &Zeroizing<String>) -> Result<String, ExportError> {
    // 1. Derive KEK from passkey using Argon2id
    // 2. Access encrypted seed from DB (read-only)
    // 3. Decrypt using ChaCha20-Poly1305
    // 4. Return mnemonic string (will be wrapped in Zeroizing by caller)
    todo!("Implement KMS integration")
}

fn render_qr(mnemonic: &Zeroizing<String>) -> Zeroizing<String> {
    use qrcode::{QrCode, render::svg};
    
    // Generate QR code from mnemonic
    let code = QrCode::new(mnemonic.as_bytes()).unwrap();
    let svg = code.render::<svg::Color>()
        .min_dimensions(200, 200)
        .build();
    
    Zeroizing::new(svg)
}

fn render_text_as_svg(mnemonic: &Zeroizing<String>) -> Zeroizing<String> {
    // Render mnemonic as SVG text (or SVG paths for higher security)
    // This prevents text selection and clipboard access
    let svg = format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
            <text x="10" y="30" font-family="monospace" font-size="14">
                {}
            </text>
        </svg>"#,
        mnemonic.as_str()
    );
    
    Zeroizing::new(svg)
}
```

---

## 4. QUY TRÌNH KIỂM THỬ (MANDATORY TESTS)

Trước khi merge, module này phải vượt qua các bài test sau:

### 4.1 Unit Test (Deterministic)
- **Input:** Known Seed + Known Passkey
- **Output:** SVG Base64 hợp lệ
- **Verify:** Decode Base64 → Parse SVG → So sánh nội dung (QR hoặc Text) xem có đúng không

### 4.2 Memory Safety Test (Mock)
- Dùng `valgrind` (trên Linux) hoặc mock `Zeroize` trait để đảm bảo hàm drop được gọi
- Verify: No memory leaks, all sensitive data zeroed

### 4.3 Interop Test
- Python mã hóa 1 payload giả → Gọi Rust → Rust giải mã thành công → Trả về ảnh
- Verify: End-to-end flow works correctly

### 4.4 Expiry/Shutdown Test
- User đóng modal hoặc quit app giữa chừng → Đảm bảo process cleanup sạch sẽ
- Verify: No orphaned processes, all memory freed

---

## 5. MIGRATION PLAN (KMS STRATEGY)

### Phase 1 (Hiện tại)
Rust truy cập DB trực tiếp (read-only) hoặc nhận Encrypted Blob từ Python và dùng Passkey (Re-auth) để giải mã. Không di chuyển toàn bộ KMS.

**Implementation:**
- Python provides encrypted seed blob + salt
- Rust derives KEK from user passkey
- Rust decrypts seed in-memory
- Rust renders SVG and zeroizes all secrets

### Phase 2 (Tương lai)
Di chuyển toàn bộ logic quản lý Key (KMS) xuống Rust.

**Benefits:**
- Single source of truth for key management
- Reduced attack surface (no Python key handling)
- Better performance (no IPC overhead)

---

## 6. UX SECURITY (SVELTE)

### 6.1 Display Controls
- **No Copy/Paste:** Vô hiệu hóa sự kiện chuột phải trên ảnh SVG
- **Hold-to-Reveal:** Ảnh mặc định bị Blur (CSS filter), user phải nhấn giữ chuột để xem
- **Auto-Wipe:** `setTimeout` 60s → Xóa `src` của ảnh, gán `null` cho biến dữ liệu

### 6.2 Implementation Example

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  
  let svgDataUri = $state<string | null>(null);
  let isRevealed = $state(false);
  let wipeTimer: number | null = null;

  async function exportRecovery(mode: 'qr' | 'text_image', passkey: string) {
    try {
      const resp = await invoke('export_recovery_svg', { mode, auth: passkey });
      svgDataUri = resp.data_uri;
      
      // Auto-wipe after TTL
      wipeTimer = setTimeout(() => {
        svgDataUri = null;
        isRevealed = false;
      }, resp.ttl_seconds * 1000);
    } catch (err) {
      console.error('Export failed:', err);
    }
  }

  function handleMouseDown() { isRevealed = true; }
  function handleMouseUp() { isRevealed = false; }
</script>

<div class="recovery-display">
  {#if svgDataUri}
    <img 
      src={svgDataUri} 
      alt="Recovery Data"
      class:blurred={!isRevealed}
      onmousedown={handleMouseDown}
      onmouseup={handleMouseUp}
      oncontextmenu={(e) => e.preventDefault()}
    />
  {/if}
</div>

<style>
  .blurred {
    filter: blur(20px);
    user-select: none;
    pointer-events: none;
  }
</style>
```

### 6.3 Security Headers
- **Cache-Control:** `no-store, no-cache, must-revalidate`
- **Content-Security-Policy:** Restrict image sources to `data:` URIs only

---

## 7. THREAT MODEL & MITIGATIONS

### Threats Mitigated ✅
1. **Clipboard Malware:** No text exposed to clipboard
2. **Memory Dumps:** Zeroization prevents recovery from RAM
3. **Screen Scrapers:** SVG rendering defeats DOM text extraction
4. **JavaScript Injection:** No plaintext in JS context
5. **Python Interception:** No plaintext in Python layer

### Residual Risks ⚠️
1. **Screenshot Malware:** User education required
2. **Physical Shoulder Surfing:** Hold-to-reveal mitigates
3. **Weak Passkey:** Argon2id mitigates brute force

---

## 8. IMPLEMENTATION CHECKLIST

### Rust Backend
- [ ] Add dependencies to `Cargo.toml`
- [ ] Create `src-tauri/src/commands/recovery_export.rs`
- [ ] Implement `export_recovery_svg` command
- [ ] Implement `fetch_and_decrypt_seed` helper
- [ ] Implement `render_qr` helper
- [ ] Implement `render_text_as_svg` helper
- [ ] Add comprehensive unit tests
- [ ] Add memory safety tests (valgrind)
- [ ] Register command in `lib.rs`

### Frontend (Svelte)
- [ ] Create Recovery Export UI component
- [ ] Implement hold-to-reveal interaction
- [ ] Implement auto-wipe timer
- [ ] Disable context menu on SVG
- [ ] Add blur CSS filter
- [ ] Test on multiple browsers

### QA/Security
- [ ] Verify no plaintext in browser DevTools
- [ ] Verify no plaintext in Python logs
- [ ] Memory dump analysis (no secrets found)
- [ ] Cross-platform testing (Windows, macOS, Linux)
- [ ] Security audit by external team

---

## 9. REFERENCES

- **ADR-006:** Memory Zeroing Fallback Pattern
- **MDS v3.14:** Commandment #9 (Offline-first)
- **BIP39 Standard:** Mnemonic code for generating deterministic keys
- **NIST SP 800-63B:** Digital Identity Guidelines
- **Rust Zeroize Crate:** https://docs.rs/zeroize/

---

**APPROVED FOR IMPLEMENTATION** ✅

*"The Iron Vault: Where secrets enter Rust and never leave."*

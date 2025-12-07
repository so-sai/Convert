# SPECIFICATION: FRONTEND SECURITY INTEGRATION (TASK 5.3 - OMEGA EDITION)

> **Ref:** TASK-5.3 | **Status:** DESIGNED (Ready for Code)
> **Stack:** Svelte 5 (Runes) + Tauri v2 (IPC)
> **Philosophy:** Zero-Trust, Event-Driven, Blind-View.

## I. TỔNG QUAN KIẾN TRÚC (THE BRIDGE)

Frontend đóng vai trò là "Người quan sát mù" (Blind Observer). Nó không bao giờ được phép xử lý Logic nghiệp vụ (Backup) hay nắm giữ Bí mật (Recovery Phrase).

### 1. Nguyên tắc "3 KHÔNG"
1.  **KHÔNG Polling:** Không hỏi Server liên tục. Ngồi im và lắng nghe Event (`backup_progress`).
2.  **KHÔNG Plaintext:** Không nhận chuỗi Mnemonic. Chỉ nhận ảnh (`data:image/svg+xml`).
3.  **KHÔNG Xử lý lỗi ngây thơ:** Lỗi hệ thống (File Locked) do Rust tự Retry. Frontend chỉ hiển thị trạng thái cuối cùng.

---

## II. CHI TIẾT KỸ THUẬT (DATA CONTRACTS)

### 1. Tính năng: Secure Backup (Omega Protocol)

**Command:** `cmd_backup_start(target_dir: Option<String>) -> Result<String, String>`
  * **Input:** Đường dẫn thư mục (nếu null, dùng default).
  * **Output:** `TaskID` (để tracking) hoặc Lỗi khởi tạo.

**Event:** `backup_progress` (Global Event)
Payload JSON cấu trúc chặt chẽ để UI render realtime:

```typescript
type BackupPayload = {
  phase: 'idle' | 'init' | 'snapshot' | 'encrypting' | 'finalizing' | 'done' | 'error';
  progress: number;       // 0.0 đến 100.0
  processed_bytes: number;
  total_bytes: number;
  speed: string;          // e.g., "45 MB/s"
  eta: string;            // e.g., "12-15s" (Dạng khoảng, không fix cứng)
  error?: string;         // Chỉ có khi phase == 'error'
};
```

### 2. Tính năng: Recovery Phrase (Blind Protocol)

**Command:** `cmd_export_recovery_svg(auth: String) -> Result<ExportResp, String>`

**Response Struct:**
```typescript
type ExportResp = {
  data_uri: string;   // "data:image/svg+xml;base64,..."
  ttl_seconds: number; // Thời gian sống (ví dụ 60s)
};
```

**UI Requirements:**
1.  **Blur mặc định:** Ảnh SVG phải có CSS `filter: blur(10px)` ngay khi load.
2.  **Hold-to-Reveal:** Nhấn giữ chuột để xem rõ. Thả tay -> Blur lại.
3.  **Auto-Wipe:** Xóa sạch biến `data_uri` sau `ttl_seconds`.

---

## III. IMPLEMENTATION GUIDE (SVELTE 5)

### 1. `lib/stores/backup.svelte.ts` (Global State)
Dùng Svelte 5 Runes để quản lý state backup toàn cục.

```typescript
import { listen } from '@tauri-apps/api/event';

export class BackupState {
    phase = $state('idle');
    progress = $state(0);
    eta = $state('--');
    
    constructor() {
        listen('backup_progress', (event) => {
            const p = event.payload;
            this.phase = p.phase;
            this.progress = p.progress;
            this.eta = p.eta;
        });
    }
}
export const backupStore = new BackupState();
```

### 2. UI Components
*   **`OmegaConsole.svelte`:** Hiển thị thanh tiến trình Backup.
*   **`BlindRecovery.svelte`:** Hiển thị ảnh Recovery Key với hiệu ứng Blur.

---

## IV. KIỂM THỬ (ACCEPTANCE CRITERIA)

1.  **Backup:** Bấm nút -> Thanh % chạy mượt -> Done hiện path.
2.  **Recovery:** Nhập pass -> Ra ảnh mờ -> Giữ chuột xem -> 60s tự mất.
3.  **Safety:** Thử tắt server giữa chừng -> UI báo lỗi, không crash.

---

## V. RUST COMMAND REGISTRATION

**Required in `src-tauri/src/lib.rs`:**
```rust
#[tauri::command]
fn cmd_backup_start(target_dir: Option<String>) -> Result<String, String> {
    // Implementation
}

#[tauri::command]
fn cmd_export_recovery_svg(auth: String) -> Result<ExportResp, String> {
    // Implementation
}

// In main builder:
tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
        cmd_backup_start,
        cmd_export_recovery_svg
    ])
```

---

**NEXT STEP:** Audit Rust code to verify commands are implemented and registered.

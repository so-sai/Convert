# MDS v3.14 Pi — Technical Strategy Mapping (Crystal Edition)

> **Ref:** TASK-5.3 (Hybrid SSOT) | **Audit:** OMEGA_ARCH | **Status:** ACTIVE
> **Last Updated:** 2025-12-27 (December Edition)
> **Python:** 3.14.2 (Free-Threading Experimental)
> **Current Sprint:** 6 - Background Services Core
> **Mục tiêu:** Biến "Trust Framework" thành Code chạy được (Rust Core + Python Brain + Svelte Face).

---

## I. CỐT LÕI CHIẾN LƯỢC (STRATEGIC CORE)

### 1. Định vị (Positioning)
Chúng ta không xây dựng **Utility** (Công cụ chuyển đổi), chúng ta xây dựng **Trust Framework** (Nền tảng niềm tin).
* **Đối thủ:** Convert file xong là hết trách nhiệm.
* **Convert Vault:** Quản lý trọn vẹn **Data Lifecycle Integrity** (Input → Convert → Validate → Seal → Persist → Destroy).

### 2. Ba Trụ Cột SSOT (The 3 Pillars)
1.  **Local-first Compute:** Mọi xử lý diễn ra tại máy client. Không Cloud.
2.  **Zero-Trust Pipeline:** Các module (Watcher, Engine, Vault) không tin nhau, phải xác thực qua chữ ký.
3.  **Hybrid Architecture:**
    * **Python:** The Brain (SSOT, State, Logic).
    * **Rust:** The Muscle (Crypto, Enforcer, IO).
    * **Svelte:** The Face (Ephemeral View, Interaction).

---

## II. MAPPING: 3-LAYER ARCHITECTURE & UI/UX

### LAYER 1: CORE ENGINE (RUST) — "THE MUSCLE"
*Nơi thực thi bất biến, bảo mật tuyệt đối.*

1.  **Convert Engine v2.3:**
    * Pure Rust bindings. Sandbox file ops.
    * **Omega Fix:** Không dùng subprocess. Dùng PyO3 embedding trực tiếp (`maturin build`) để loại bỏ latency 30-40ms.
2.  **Vault Storage Kernel:**
    * Encrypted FS: XChaCha20-Poly1305 (24-byte nonce).
    * **Omega Fix:** `Argon2id` KDF parameters tối ưu hóa.
    * **Commit Flow:** Write → Seal → Hash → Sign → Expose to UI.
3.  **Security Enforcer:**
    * **Memory Hygiene:** Tự động zeroize bộ nhớ khi sleep/hibernate (Windows Power API hooks).
    * **Snapshot Binding:** Gắn output + hash tree + policy version.

### LAYER 2: ORCHESTRATION (PYTHON) — "THE BRAIN"
*Nơi chứa SSOT và điều phối luồng.*

1.  **SSOT Registry (AppState):**
    * Lưu trữ trạng thái duy nhất của ứng dụng.
    * **Schema (Pydantic V2 Strict):**
        ```json
        {
          "version": 1,
          "timestamp": 1733650000,
          "navigation": {
            "active_module": "notes",
            "last_route": "/notes/view/123",
            "ui_depth": 2
          },
          "modules": { ... },
          "panels": {
            "notes": { "split": { "left": 0.33, "right": 0.67 } }
          }
        }
        ```
    * **Invariant:** Frontend coi các trường lạ là opaque (hộp đen), không tự ý sửa schema.

2.  **Task Orchestrator:**
    * Điều phối: FS Watcher → Convert → Vault.
    * **Omega Fix:** Xử lý `PRAGMA wal_autocheckpoint` cho SQLite để tránh file WAL phình to >1GB.
    * **Path Handling:** Sử dụng `pathlib` + fix cho PyInstaller (`sys.frozen`) để chạy đúng trên Windows.

3.  **Audit Log Stream:**
    * Append-only, signed by Rust Keystore.
    * Ghi lại mọi thay đổi trạng thái quan trọng (State Mutation).

### LAYER 3: INTERACTION (SVELTE) — "THE FACE"
*Nơi người dùng cảm nhận giá trị.*

1.  **Lớp 1 — HOME (Shelf & Dock):**
    * **3 Cuốn sách (Books):** Convert / Notes / Workflow. Dựng dọc.
    * **Dock:** Chứa Global Settings, Profile.
    * **Hành vi:** Click sách -> Animation transition -> Gọi `cmd_save_app_state`.

2.  **Lớp 2 — WORKSPACE (Split View):**
    * **Master/Detail:** Cơ chế chia đôi màn hình (Split View).
    * **Persist:** Tự động nhớ vị trí thanh trượt (Split position) vào Python State.
    * **Behavior:** Module cũ thu nhỏ thành card (thumb), module mới mở ra.

3.  **Lớp 3 — COGNITIVE (Interface Layers):**
    * **Sensory:** Drag & Drop, Tactile feedback.
    * **Recovery Viewer:** "X-ray" file để kiểm tra hash integrity.
    * **AI Hooks:** Chỉ hiển thị gợi ý (Suggest), không tự thực thi (Execute) nếu không có xác nhận.

---

## III. IMPLEMENTATION CONTRACTS (QUY TẮC BẤT DI BẤT DỊCH)

1.  **Contract #1: No Secrets in IPC**
    * Frontend **KHÔNG BAO GIỜ** nhận key, mnemonic, password dạng plaintext.
    * Chỉ nhận: Token tạm (Ephemeral), Status, Progress, Hash.
    * **Omega Fix:** Dùng `Zeroizing<SecretBytes>` wrapper ngay tại biên giới PyO3.

2.  **Contract #2: Python is The Boss**
    * Frontend không lưu logic. Frontend chỉ render `AppState` nhận từ Python.
    * Mọi thay đổi (Click, Resize, Config) -> Gửi Command về Python -> Python Validate & Save -> Emit Event update UI.

3.  **Contract #3: Graceful Degradation**
    * Nếu Module chưa sẵn sàng (Workflow) -> Show Toast "Coming Soon" (Non-blocking).
    * Nếu C-Binding lỗi (Memory Zeroing) -> Fallback về Manual Overwrite (ADR-006).

---

## IV. ROADMAP THỰC THI (ACTIONABLE)

1.  **Phase 1: Foundation (DONE)**
    * [x] UI Skeleton (Svelte).
    * [x] Security Protocol (Blind Protocol, ADR-006).

2.  **Phase 2: SSOT Integration (NEXT - PRIORITY)**
    * [ ] **Rust:** Implement `cmd_get_app_state` / `cmd_save_app_state`.
    * [ ] **Python:** Define Pydantic Models cho `AppState`. Implement `Dispatcher`.
    * [ ] **Tauri:** Cấu hình `orjson` thay vì `serde_json` (Performance).

3.  **Phase 3: Features**
    * [ ] HomeShelf Component.
    * [ ] SplitView Logic.
    * [ ] SQLite WAL Tuning.

4.  **Phase 4: Background Services (Sprint 6 - CURRENT)**
    * [x] **Task 6.1:** Watchdog Core - File system monitoring with debouncing (15/15 tests PASSED).
    * [ ] **Task 6.2:** EventBus - Pub/Sub for cross-module communication.
    * [ ] **Task 6.3:** Indexer Queue - SQLite-based job queue.

---

## V. DETAILED PROTOCOLS (PRESERVED)

### 5.1 OMEGA Backup Protocol (The Engine)

| Phase | Action (Rust) | Action (Python) | State |
| :--- | :--- | :--- | :--- |
| **1. INIT** | `cmd_backup_start(target)` | Validate Path, Check Lock | `BUSY` |
| **2. SNAPSHOT** | **Atomic Freeze:** `VACUUM INTO` | Calculate Checksums | `LOCKED` |
| **3. ENCRYPT** | **XChaCha20-Poly1305** Stream | Monitor RAM Usage (<100MB) | `ENCRYPTING` |
| **4. FINALIZE** | Sign Metadata (Ed25519) | Rename `.tmp` -> `.cvbak` | `DONE` |

### 5.2 Recovery Protocol (The Restore)

1.  **Verify:** Check Magic Header (`CVBAK`), Version, Signature.
2.  **Auth:** Prompt User Passphrase -> Derive Key (Argon2id).
3.  **Decrypt:** Stream Decrypt to Temp DB.
4.  **Integrity:** Check SQLite `PRAGMA integrity_check`.
5.  **Swap:** Atomic Swap (Move old DB -> `.bak`, Move Temp DB -> Main).

### 5.3 Cryptographic Parameters (Hardcoded)

| Component | Algorithm | Parameters |
| :--- | :--- | :--- |
| **KDF** | Argon2id | Memory: 64MB, Iterations: 4, Lanes: 4 |
| **Encryption** | XChaCha20-Poly1305 | Nonce: 24 bytes (Random) |
| **Signature** | Ed25519 | Context: `convert_vault_v1` |
| **Hash** | BLAKE3 | Merkle Tree Mode enabled |

---

## APPENDIX A: NAMING CONVENTION

* **Rust (Crate):** `snake_case` (e.g., `cmd_backup_start`)
* **Python (Module):** `snake_case` (e.g., `backup_service.py`)
* **Svelte (Component):** `PascalCase` (e.g., `BackupConsole.svelte`)
* **IPC Events:** `camelCase` (e.g., `backupProgress`)
* **File Extension:** `.cvbak` (Convert Vault Backup)

---

**Authorized by:** ARCH_PRIME
**Compliance:** OMEGA_ARCH (Security Checked)

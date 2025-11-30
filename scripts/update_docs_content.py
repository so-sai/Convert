import os
from pathlib import Path

# --- CONTENT DEFINITIONS ---

# 1. MDS v3.14 (CẬP NHẬT TRẠNG THÁI & CẤU TRÚC)
MDS_CONTENT = """# 📘 MDS v3.14 - THE ETERNAL PYTHON CORE (GRAND UNIFIED)

> **Status:** SPRINT 5 (PHASE 3: FRONTEND INTEGRATION)
> **Engine:** Python 3.14.0 (Free-Threading `cp314t`)
> **Ref:** [Engineering Playbook](../05_OPERATIONS/ENGINEERING_PLAYBOOK.md)

## 1. PROJECT VISION
"Offline-first, event-sourced, cryptographically unbreakable knowledge system."

## 2. ARCHITECTURAL DECISIONS
- **[ADR-002]** Crypto Engine: Libsodium Strategy (XChaCha20-Poly1305).
- **[ADR-003]** Backup Crypto: Omega Standard (Argon2id 128MB/3 Ops).

## 3. TECH STACK (UPDATED)
```yaml
backend:
  language: "Python 3.14 (No-GIL)"
  location: "src/core"
  database: "SQLite STRICT (WAL Mode)"

frontend:
  framework: "Svelte 5 + Tauri v2"
  location: "src-ui"
  bridge: "JSON-RPC via Tauri Commands"
```

## 4. CRYPTOGRAPHIC ARCHITECTURE (THE IRON CORE)

### 4.2 Argon2id Parameters (LOCKED - TASK 5.2 GOLDEN MASTER)

```python
# CẤU HÌNH CỨNG CHO BACKUP (src/core/utils/security.py)
ARGON2_BACKUP_OPSLIMIT    = 3
ARGON2_BACKUP_MEMLIMIT    = 134217728  # 128 MiB (Omega Standard)
ARGON2_BACKUP_PARALLELISM = 4
ARGON2_SALT_BYTES         = 16
```

## 5. SPRINT STATUS (REAL-TIME)

- **Sprint 4 (Security):** ✅ COMPLETED.
- **Sprint 5 (Resilience):**
  - ✅ **Task 5.1: Recovery Phrase (BIP39):** DONE.
  - ✅ **Task 5.2: Secure Backup (Atomic Vacuum):** DONE.
  - 🔄 **Task 5.3: Frontend Integration:** IN PROGRESS (User Stories Ready).

## 6. PHYSICAL DIRECTORY STRUCTURE (CONFIRMED)

```text
E:/DEV/Convert/
├── docs/                       # [KNOWLEDGE BASE]
│   ├── 01_ARCHITECTURE/        # SSOT (DECISIONS, MDS)
│   ├── 04_KNOWLEDGE/           # Lessons Learned
│   └── 05_OPERATIONS/          # Runbooks
├── src/                        # [BACKEND CORE]
│   └── core/                   # Monorepo Root
│       ├── api/                # Tauri Bridge
│       ├── security/           # KMS, Recovery, Backup
│       ├── services/           # Business Logic
│       └── ...
├── src-ui/                     # [FRONTEND - SVELTE 5]
├── tests/                      # [QA SUITE]
├── .gitignore
└── pyproject.toml
```
"""

# 2. SPEC TASK 5.3 (NẠP USER STORIES CỦA SẾP + KỸ THUẬT)
SPEC_5_3_CONTENT = """# SPEC-005: FRONTEND INTEGRATION (BACKUP & RESTORE)

**Parent Task:** Task 5.3 - Resilience UI  
**Status:** READY FOR DEV  
**Ref:** MDS v3.14, ADR-003

## 1. USER STORIES (FROM PRODUCT OWNER)

### Story 1: Smart Toast Notification (The "Gentle Nudge")

**As a** User,  
**I want** to receive a non-intrusive notification when it's time to backup my vault,  
**So that** I can ensure my data is safe without being interrupted.

- **Trigger:** Periodic poll of `get_backup_status`.
- **UI:** Toast at bottom-right.
  - "You've created 10+ notes. Consider backing up."
  - [Backup Now] | [Don't ask again]
- **Behavior:** Auto-dismiss 8s. No Modals.

### Story 2: Magic Restore (Drag & Drop)

**As a** User,  
**I want** to drag a `.cvbak` file onto the application window,  
**So that** I can easily initiate the restore process without navigating complex menus.

- **Detection:** `.cvbak` extension.
- **Feedback:** "Drop Zone" overlay appears.
- **Action:** Triggers Restore Wizard.

### Story 3: Progress Feedback

**As a** User,  
**I want** to see a visual indicator during the Backup and Restore processes.

- **Backup:** Spinner during "Exporting..." (2-3s). Success checkmark.
- **Restore:** Modal steps: "Verifying..." -> "Decrypting..." -> "Restoring...".

---

## 2. TECHNICAL BRIDGE (PYTHON <-> SVELTE)

### 2.1 Backend Commands (src/core/api/routes/backup.py)

Frontend will invoke these via `invoke('command_name', args)`:

1. `backup_create_snapshot(passkey: str, target_path: str) -> Result<bool>`
   - Wraps `src.core.services.backup.create_backup`.
   - Returns success or throws error string.

2. `backup_restore_from_file(backup_path: str, passkey: str) -> Result<bool>`
   - Wraps `src.core.services.backup.restore_backup`.
   - **CRITICAL:** Must handle `WinError 32` (File Locking) gracefully.

3. `backup_get_status() -> BackupStatus`
   - Returns JSON: `{ "last_backup": timestamp, "changes_since_last": int, "should_backup": bool }`

### 2.2 Error Codes (To be displayed in Toasts)

- `ERR_AUTH_FAILED`: Wrong passkey.
- `ERR_IO_LOCKED`: File is busy (Retry logic needed).
- `ERR_INTEGRITY`: Backup file is corrupted/tampered.
"""

# 3. ARCH GRAPH (CẬP NHẬT SƠ ĐỒ MỚI)
GRAPH_CONTENT = """# ARCHITECTURAL GRAPH: The Bridge Pattern

**Date:** 2025-11-29  
**Status:** LIVE

```mermaid
graph TD
    subgraph "FRONTEND (Svelte 5)"
        UI_Dash[Dashboard]
        UI_Toast[Toast Notification]
        UI_Drop[Drop Zone]
    end

    subgraph "BRIDGE (Tauri IPC)"
        CMD_Backup[cmd: backup_create]
        CMD_Restore[cmd: backup_restore]
        CMD_Status[cmd: get_status]
    end

    subgraph "BACKEND (Python src/core)"
        API[src/core/api]
        SVC_Backup[src/core/services/backup.py]
        SEC_KMS[src/core/security/kms.py]
        DB[(SQLite mds_eternal.db)]
    end

    UI_Dash --> CMD_Status
    UI_Drop --> CMD_Restore
    UI_Toast --> CMD_Backup

    CMD_Status --> API
    CMD_Restore --> API
    CMD_Backup --> API

    API --> SVC_Backup
    SVC_Backup --> SEC_KMS
    SVC_Backup --> DB
```
"""

def update_docs():
    base_decisions = Path("docs/01_ARCHITECTURE/DECISIONS")
    
    files = [
        (Path("docs/01_ARCHITECTURE/MDS_v3.14.md"), MDS_CONTENT),
        (base_decisions / "SPEC_TASK_5_3_FRONTEND.md", SPEC_5_3_CONTENT),
        (base_decisions / "ARCH_CORE_GRAPH.md", GRAPH_CONTENT)
    ]
    
    print("=== 🔄 UPDATING DOCUMENTATION ===")
    for path, content in files:
        # Đảm bảo folder tồn tại
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Updated: {path}")

if __name__ == "__main__":
    update_docs()

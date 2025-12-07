# SPEC_TASK_5_3_INTEGRATED — HYBRID SSOT EDITION (MDS v3.14 Pi)

**Ref:** TASK-5.3 (integrated → Model C: Hybrid)  
**Status:** READY FOR IMPLEMENTATION  
**Author:** ARCH_PRIME (per OMEGA_ARCH, PYTHON-FIRST)  
**Goal:** Đồng bộ Frontend (Svelte) ↔ Rust Shell (Tauri) ↔ Python Core (SSOT)

> **Summary:** Python giữ state (SSOT). Rust làm enforcement & crypto. Frontend là ephemeral client.

---

## 0. HIGH-LEVEL SEQUENCE

```
(1) User action → Frontend creates Request (nonce, ephemeral_token)
(2) Frontend → Tauri.invoke("cmd_dispatch", payload)
(3) Rust Shell:
     - Validate envelope signature/nonces
     - Call Python service (PyO3/Sidecar)
     - Crypto primitives only (zeroize)
(4) Python Core (SSOT):
     - Authoritative logic (task dispatch, state, replay window)
     - Emits progress to Rust (callback)
(5) Rust Shell:
     - Emits events to frontend: backup_progress, operation_done
     - No sensitive plaintext crosses IPC
(6) Frontend:
     - Listens to events; renders UI
     - Holds only ephemeral nonce/token
```

---

## 1. INVARIANTS (MUST ENFORCE)

| # | Invariant |
|---|-----------|
| 1 | **SSOT:** Python Core is authoritative for session/task state |
| 2 | **Zero-Trust UI:** Frontend never receives plaintext secrets |
| 3 | **Rust Enforcement:** All crypto in Rust; zeroize immediately |
| 4 | **Replay Protection:** Python maintains replay window |
| 5 | **Ephemeral Tokens:** Short TTL, single-use |
| 6 | **No Business Logic in Rust:** Only validation + crypto + bridge |

---

## 2. DATA CONTRACTS

### Request Envelope
```json
{
  "envelope": {
    "version": "1",
    "service": "backup.start",
    "nonce": "b64url(...)",
    "ephemeral_token": "b64(...)",
    "seq": 12,
    "timestamp": 1700000000
  },
  "payload": { }
}
```

### BackupProgress Event
```ts
type BackupProgress = {
  task_id: string;
  phase: 'idle'|'init'|'snapshot'|'encrypting'|'finalizing'|'done'|'error';
  progress: number;
  speed?: string;
  eta?: string;
  message?: string;
}
```

### ExportResp
```ts
type ExportResp = {
  data_uri: string;
  ttl_seconds: number;
}
```

---

## 3. RUST SHELL COMMANDS

```rust
// src-tauri/src/commands/shell.rs
#[tauri::command]
fn cmd_dispatch(envelope: String) -> Result<String, String>;

#[tauri::command]
fn cmd_request_token(user_id: String) -> Result<String, String>;

#[tauri::command]
fn cmd_cancel_task(task_id: String) -> Result<(), String>;
```

**Rule:** Rust functions MUST NOT compute business metrics.

---

## 4. PYTHON CORE DISPATCHER

```python
# src/core/services/dispatcher.py
def run(service: str, envelope: dict) -> dict:
    """Authoritative dispatcher."""
    # 1. validate envelope
    # 2. check replay window
    # 3. dispatch job
    # 4. return result
```

---

## 5. ERROR CATEGORIES

| Code | Meaning |
|------|---------|
| `bad_envelope` | Malformed request |
| `token_expired` | Token expired |
| `replay_detected` | Nonce reused |
| `auth_failed` | Invalid signature |
| `backend_internal` | Generic error |

---

## 6. ACCEPTANCE CRITERIA

- [ ] Python holds session state (verified by tests)
- [ ] Rust has no business logic (code review)
- [ ] Frontend holds only ephemeral tokens (static scan)
- [ ] RecoveryViewer: blur/press-hold/TTL auto-wipe
- [ ] DropZone: drag-and-drop restore
- [ ] CI passes security tests (replay, expired token)

---

**HASH:** spec-5-3-integrated-hybrid

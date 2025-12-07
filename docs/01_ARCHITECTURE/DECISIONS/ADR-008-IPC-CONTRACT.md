# ADR-008: OMEGA IPC CONTRACT (FULL-STACK SECURITY)

> **Status:** ACCEPTED
> **Type:** Architecture Decision Record
> **Implements:** Hybrid IPC (Command-Init → Event-Stream)
> **Effective:** Sprint 5+

---

## 1. CONTEXT

The Convert Vault requires secure communication between Svelte UI and Rust backend. Two competing patterns exist:
- **Command-only:** Synchronous, simple, but blocks on long operations
- **Event-only:** Asynchronous, but no immediate feedback

## 2. DECISION

**Adopt HYBRID MODEL (Mode 3):**
1. **Commands (`cmd_*`):** Synchronous init, validation, immediate `Result<TaskID>`
2. **Events (`backup_progress`):** Async streaming from Rust to UI

## 3. DATA CONTRACTS

### 3.1 Backup (Omega Protocol)

**Command:**
```rust
#[tauri::command]
async fn cmd_backup_start(
    app: AppHandle, 
    target_dir: Option<String>
) -> Result<String, String>
```

**Event Channel:** `backup_progress` (SINGLE GLOBAL CHANNEL)

**Payload:**
```typescript
interface BackupPayload {
  task_id: string;
  phase: 'init' | 'snapshot' | 'encrypting' | 'finalizing' | 'done' | 'error';
  progress: number;      // 0.0 - 100.0
  speed: string;         // "45 MB/s"
  eta: string;           // "10-15s" (range, not exact)
  msg: string;
  error?: string;
}
```

### 3.2 Recovery (Blind Protocol)

**Command:**
```rust
#[tauri::command]
fn cmd_export_recovery_svg(
    app: AppHandle, 
    auth: String
) -> Result<ExportResp, String>
```

**Response:**
```typescript
interface ExportResp {
  data_uri: string;      // "data:image/svg+xml;base64,..."
  ttl_seconds: number;   // 60
}
```

## 4. RULES (INVARIANTS)

| # | Rule | Rationale |
|---|------|-----------|
| 1 | **`cmd_` Prefix** | All IPC commands must start with `cmd_` |
| 2 | **Blind UI** | Frontend NEVER receives plaintext mnemonics |
| 3 | **Hybrid Flow** | Long tasks spawn thread, return TaskID immediately |
| 4 | **Single Event Channel** | All progress uses `backup_progress` (no dynamic names) |
| 5 | **Panic Safety** | Workers must catch panics and emit error events |

## 5. CONSEQUENCES

**Positive:**
- Zero-Trust UI maintained
- Responsive UX (no blocking)
- Debuggable (single event source)

**Negative:**
- More complex than pure command model
- Requires frontend state management

## 6. VERIFICATION

```bash
# Rust compiles with new commands
cargo check

# Commands registered
grep -r "cmd_backup_start" src-tauri/src/

# Event emitter present
grep -r "emit.*backup_progress" src-tauri/src/
```

---

**Authority:** ARCH_PRIME
**Hash:** adr-008-omega-ipc-contract

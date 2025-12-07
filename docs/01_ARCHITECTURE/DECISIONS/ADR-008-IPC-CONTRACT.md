# HASH: spec-008-ipc-v2
# IMPLEMENTS: Task 5.3 - Convert Protocol & Blind Recovery
# STATUS: IMPLEMENTED (Sprint 5)

# 🔐 SPEC-008: CONVERT PROTOCOL & UI GUIDELINES

> **SSOT Warning:** This document reflects the actual code in `src-tauri` (Rust) and `src-ui` (Svelte).

---

## 1. BRANDING & IDENTITY (THE LAW)

| Term | Usage |
|------|-------|
| **Convert** | Product Name (OFFICIAL) |
| **Convert Protocol** | Feature branding in UI |
| **Backup Protocol** | Technical name for backup system |

**Design Philosophy:** Modern Card UI (Clean, Neutral, Professional).
**Anti-Pattern:** Do NOT use "Hacker Terminal" styles. Use "Apple/Stripe" aesthetic.

---

## 2. IPC COMMANDS (RUST ↔ SVELTE)

### 2.1 Backup Sequence

**Command:** `cmd_backup_start`
```rust
#[tauri::command]
pub async fn cmd_backup_start(
    app: AppHandle,
    target_dir: Option<String>
) -> Result<String, String>  // Returns TaskID
```

**Behavior:** 
- Asynchronous (Fire-and-Forget)
- Returns `task_id` immediately
- Spawns worker thread for backup processing
- Emits `backup_progress` events during operation

### 2.2 Blind Recovery

**Command:** `cmd_export_recovery_svg`
```rust
#[tauri::command]
pub fn cmd_export_recovery_svg(
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

**Security:** SVG is returned as Base64. Frontend must apply CSS `blur` by default.

---

## 3. EVENT STREAM (REALTIME)

**Channel:** `backup_progress` (Static Global Channel)

**Payload Structure:**
```typescript
interface BackupPayload {
    task_id: string;
    phase: 'init' | 'snapshot' | 'encrypting' | 'finalizing' | 'done' | 'error';
    progress: number;    // 0.0 - 100.0
    speed: string;       // "45 MB/s"
    eta: string;         // "10-15s" (range)
    msg: string;         // Human readable status
}
```

**Event Flow:**
1. Frontend calls `cmd_backup_start`
2. Rust returns `TaskID` immediately
3. Frontend listens to `backup_progress` channel
4. Frontend filters events by `task_id`
5. Worker thread emits progress events
6. Worker emits `phase: 'done'` on completion

---

## 4. UI COMPONENT CONTRACT

**File:** `src-ui/src/lib/components/backup/BackupConsole.svelte`

**Requirements:**
- Display **"CONVERT"** as primary header
- Progress Bar: Blue (Active) → Green (Done) → Red (Error)
- Background: Neutral Card on Light App Background
- State via Svelte stores (`backupStore`)

---

## 5. SECURITY CONSTRAINTS

| Constraint | Implementation |
|------------|----------------|
| Zero-Trust | Frontend never sees raw mnemonic (SVG only) |
| Sanitization | All paths validated in Rust |
| Panic Safety | Workers catch panics, emit error events |
| TTL Auto-Wipe | Recovery SVG cleared after `ttl_seconds` |

---

**Authority:** ARCH_PRIME
**Verified:** Sprint 5 Implementation Complete

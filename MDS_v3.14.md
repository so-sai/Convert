# 📘 MDS v3.14 - THE ETERNAL PYTHON CORE (GRAND UNIFIED)

> **Status:** SPRINT 3 COMPLETED
> **Engine:** Python 3.14.0 (Free-Threading `cp314t`)
> **Philosophy:** "Infinite like Pi, Fast like Python, Secure like Rust."
> **Base:** Merged from v3.1-ETERNAL & v4.0-SECURE

## 1. PROJECT VISION & PRINCIPLES

```yaml
mission: "Offline-first, event-sourced, cryptographically unbreakable knowledge system"
principles:
  - offline_first: "Local execution only. Zero cloud dependency."
  - data_sovereignty: "User owns the keys. Data is encrypted at rest."
  - event_sourcing: "Append-only log is the single source of truth."
  - free_threading: "Maximize Python 3.14 No-GIL capabilities."
future_proof: "Language/runtime upgrades handled via automated migration scripts."
```

## 2. TECH STACK & CONSTRAINTS (UPDATED)

```yaml
backend:
  language: "Python 3.14 (Free-Threading Build)"
  concurrency: "PEP 779 (No-GIL) + PEP 734 (Subinterpreters)"
  dependencies:
    - "fastapi==0.121.3"     # Security patched
    - "uvicorn==0.38.0"      # Py3.14 compatible
    - "orjson==3.11.4"       # Pre-compiled binary wheel
    - "aiosqlite==0.21.0"    # Async SQLite
  execution_mode: "python -X gil=0 -m src.core.main"
  database_schema: "SQLite STRICT (INTEGER only, No BIGINT)"

frontend:
  framework: "Svelte 5"
  desktop: "Tauri v2.9.3"
  rendering: "WebGPU"

cryptography:
  key_exchange: "X25519 (Curve25519) - No NIST curves"
  encryption: "XChaCha20-Poly1305 (Sprint 4)"
  integrity: "HMAC-SHA3-256 (Always ON)"
```

## 3. ARCHITECTURE OVERVIEW

- **Streams:** Domain (Immutable), Interaction (Ephemeral), Memory (Rebuildable).
- **Data Flow:** Event -> Canonical JSON -> HMAC -> Encrypt -> BLOB -> DB.
- **Persistence:** SQLite domain_events (Log) + notes (Projection).

## 4. CRYPTOGRAPHIC ARCHITECTURE (THE IRON CORE)

- **Integrity Chain:** prev_event_hash connects all events.
- **HMAC Protection:** Calculated on payload bytes. Verified on read.
- **Passkey Integration (Sprint 4):** Master Key derived from WebAuthn PRF.

## 5. DATABASE SCHEMA (DDL - CORRECTED)

```sql
CREATE TABLE domain_events (
    event_id TEXT PRIMARY KEY,
    stream_type TEXT NOT NULL CHECK(stream_type IN ('domain','interaction','memory')),
    stream_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    stream_sequence INTEGER NOT NULL, -- STRICT: INTEGER only
    global_sequence INTEGER NOT NULL UNIQUE, -- STRICT: INTEGER only
    timestamp INTEGER NOT NULL,
    payload BLOB NOT NULL,
    prev_event_hash BLOB,
    event_hash BLOB NOT NULL,
    enc_algorithm TEXT NOT NULL DEFAULT 'pass-through',
    enc_key_id TEXT,
    enc_nonce BLOB,
    event_hmac TEXT NOT NULL,
    UNIQUE(stream_type, stream_id, stream_sequence)
) STRICT;

CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content BLOB NOT NULL,
    metadata BLOB NOT NULL,
    enc_algorithm TEXT NOT NULL DEFAULT 'pass-through',
    enc_key_id TEXT,
    enc_nonce BLOB,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted_at INTEGER,
    version INTEGER NOT NULL DEFAULT 1
) STRICT;
```

## 6. SPRINT STATUS (REAL-TIME)

```yaml
completed:
  - [Sprint 1] Architecture Foundation
  - [Sprint 2] Core Backend & Database (Fixed BIGINT/Import issues)
  - [Sprint 3] Plugin System & Storage Hardening (ALL TASKS COMPLETED)

current_focus:
  - [Sprint 4] Passkey Auth & Real Encryption (XChaCha20).

next_sprint:
  - [Sprint 5] WASM Sandbox & P2P Sync.
```

## 7. TEAM STRUCTURE & ROLES

- **PM:** Gemini 3.0 Pro (Strategy).
- **SA:** ChatGPT 5.1 (Blueprint).
- **SecA:** Grok 4 (Audit).
- **Dev:** DeepSeek V3.2 (Code).
- **Reviewer:** Claude 4.5 (Quality).

## 8. CRITICAL INVARIANTS (THE 10 COMMANDMENTS)

1.  **Execution:** Always use `python -m <module>` (e.g., `src.core.main`). NEVER call scripts directly.
2.  **Database:** `INTEGER` only. No `BIGINT`.
3.  **Payload:** Always `BLOB`.
4.  **Integrity:** Verify HMAC on Read. Crash on failure.
5.  **Isolation:** Plugins must use defined Protocol (`IPlugin`) & reside in `src/core/plugin`.
6.  **Path:** Use `pathlib` & `encoding='utf-8'`. Single backslash (`/`) normalization only.
7.  **Hygiene:** Monorepo Strictness: Code stays in `src/core`. No `sprint-x` folders.
8.  **Deps:** `requirements.txt` is the Single Source of Truth.
9.  **Platform:** Windows launcher bypass: Use `python -m PyInstaller` instead of `pyinstaller`.
10. **Concurrency:** Thread-safe code for No-GIL environment.

## 9. SPRINT 3 RETROSPECTIVE (LESSONS LEARNED)
Ref: Engineering Playbook (`docs/policies/ENGINEERING_PLAYBOOK.md`)

- **The Windows Protocol:** Direct command calls (like `pytest`, `pyinstaller`) fail on Windows environments with multiple Python versions. **Fix:** Always prefix with `python -m`.
- **The Protocol Check:** Python 3.14 does not allow `issubclass` checks on Protocols with non-method members (data attributes). **Fix:** Use `isinstance` or valid runtime checks.
- **The Overwrite Strategy:** To avoid AI hallucinating line numbers, always overwrite config files (`.spec`, `.txt`) completely using `cat << 'EOF'`.
- **Build Hygiene:** PyInstaller fails if target directories (even empty ones like `config`) do not exist. Always `mkdir` before build.

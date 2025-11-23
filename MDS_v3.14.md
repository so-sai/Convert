# 📘 MDS v3.14 - THE ETERNAL PYTHON CORE (GRAND UNIFIED)

> **Status:** SPRINT 4 ACTIVE
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
    - "cffi>=2.0.0"          # Required for PyNaCl thread safety
    - "pynacl>=1.5.0"        # XChaCha20-Poly1305 (libsodium)
    - "pycryptodome>=3.17.0" # Fallback crypto provider
  execution_mode: "python -X gil=0 -m src.core.main"
  database_schema: "SQLite STRICT (INTEGER only, No BIGINT)"

frontend:
  framework: "Svelte 5"
  desktop: "Tauri v2.9.3"
  rendering: "WebGPU"

cryptography:
  library: "PyNaCl (libsodium) - Ref: ADR-002"
  key_exchange: "X25519 (Curve25519) - No NIST curves"
  encryption: "XChaCha20-Poly1305 (192-bit nonce)"
  integrity: "HMAC-SHA3-256 (Always ON)"
  key_derivation: "HKDF-SHA3-256 (per-stream keys)"
```

## 3. ARCHITECTURE OVERVIEW

- **Streams:** Domain (Immutable), Interaction (Ephemeral), Memory (Rebuildable).
- **Data Flow:** Event -> Canonical JSON -> HMAC -> Encrypt -> BLOB -> DB.
- **Persistence:** SQLite domain_events (Log) + notes (Projection).

## 4. CRYPTOGRAPHIC ARCHITECTURE (THE IRON CORE)

### 4.1 Security Principles
- **Integrity Chain:** prev_event_hash connects all events.
- **HMAC Protection:** Calculated on payload bytes. Verified on read.
- **Passkey Integration (Sprint 4):** Master Key derived via Argon2id KDF.

### 4.2 The Eternal Vault Architecture (Sprint 4 - APPROVED)

**Status:** APPROVED_FOR_MERGE (Hash: SPRINT4-REV5.1-FINAL)  
**Approval Date:** 2025-11-23  
**Security Audit:** SECA_GROK_4.1 + Supreme Judicial Review

**Key Hierarchy:**
```
User Passkey (>=12 chars)
    ↓ Argon2id KDF (OWASP 2025)
KEK (Key Encryption Key, 256-bit)
    ↓ XChaCha20-Poly1305 AEAD
Wrapped DEK (Data Encryption Key, 256-bit)
    ↓ Stored in SQLite (system_keys table)
DEK (Unwrapped in memory)
    ↓ XChaCha20-Poly1305 AEAD
Encrypted Event Payloads
```

**Argon2id Parameters (OWASP 2025 Compliant):**
```python
# CRITICAL: These parameters are LOCKED and IMMUTABLE
ARGON2_OPSLIMIT   = 2                    # iterations (t=2)
ARGON2_MEMLIMIT   = 19456 * 1024         # 19 MiB = 19,922,944 bytes
ARGON2_PARALLELISM = 1                   # p=1 (side-channel resistance)
ARGON2_SALT_BYTES  = 16                  # 128-bit salt
ARGON2_OUTPUT_BYTES = 32                 # 256-bit KEK
```

**Rationale:**
- **Memory (19 MiB):** Prevents DoS attacks (~50 concurrent auth on 1GB RAM)
- **Iterations (t=2):** Balances security and UX (<1 second unlock time)
- **Parallelism (p=1):** Maximizes side-channel attack resistance
- **Performance:** 0.5-1.0s unlock time on desktop, <1s on mobile

**Encryption Primitives:**
```python
# KEK Wrapping (Passkey → KEK → Wrapped DEK)
Algorithm: XChaCha20-Poly1305 AEAD
Nonce: 24 bytes (192-bit, random per operation)
Key: 32 bytes (256-bit KEK from Argon2id)
Output: Ciphertext + 16-byte authentication tag

# Data Encryption (DEK → Encrypted Payload)
Algorithm: XChaCha20-Poly1305 AEAD
Nonce: 24 bytes (192-bit, random per event)
Key: 32 bytes (256-bit DEK)
Additional Data: event_id + stream_id (authenticated but not encrypted)
```

**Database Schema (system_keys table):**
```sql
CREATE TABLE IF NOT EXISTS system_keys (
    id TEXT PRIMARY KEY CHECK (id = 'main'),
    kdf_salt BLOB NOT NULL,              -- 16 bytes (Argon2id salt)
    kdf_ops INTEGER NOT NULL,             -- 2 (iterations)
    kdf_mem INTEGER NOT NULL,             -- 19,922,944 (19 MiB)
    enc_dek BLOB NOT NULL,                -- Wrapped DEK (ciphertext + tag)
    dek_nonce BLOB NOT NULL,              -- 24 bytes (XChaCha20 nonce)
    created_at INTEGER NOT NULL           -- Unix timestamp
) STRICT;
```

**Security Guarantees:**
- ✅ **Local-First:** No cloud dependencies, all keys stored locally
- ✅ **Data Sovereignty:** User controls passkey, vault cannot be accessed without it
- ✅ **Forward Secrecy:** DEK rotation supported (future Sprint 5)
- ✅ **AEAD Protection:** Authenticated encryption prevents tampering
- ✅ **DoS Resistance:** Memory-bound KDF prevents resource exhaustion
- ✅ **OWASP Compliance:** Follows OWASP Password Storage Cheat Sheet 2025

**Passkey Requirements:**
- Minimum length: 12 characters
- Strength validation: Basic complexity check (Phase 1)
- Future enhancement: zxcvbn integration (Sprint 4 Week 1)
- Rate limiting: 3 failed attempts per 5 minutes (Sprint 5)

**Operational Security:**
- **Memory Hygiene:** Best-effort zeroization of sensitive keys
- **Idle Timeout:** DEK cleared from memory after 5 minutes inactivity (Sprint 4 Week 1)
- **Key Rotation:** Passkey change and DEK rotation procedures (Sprint 4 Week 2)
- **Audit Logging:** All vault operations logged for security monitoring


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
  - [Sprint 4] The Cryptographic Vault (IN PROGRESS)
    - ADR-002: PyNaCl (libsodium) selected for XChaCha20-Poly1305
    - EncryptionService with HKDF-SHA3-256 key derivation
    - PyInstaller bundling with libsodium hooks
    - Estimated: 40 dev-hours (5 working days)

next_sprint:
  - [Sprint 5] Passkey Auth & Key Rotation
  - [Sprint 6] WASM Sandbox & P2P Sync
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

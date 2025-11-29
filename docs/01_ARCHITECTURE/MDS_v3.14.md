# 📘 MDS v3.14 - THE ETERNAL PYTHON CORE (GRAND UNIFIED)

> **Status:** SPRINT 5 (RESILIENCE PHASE)  
> **Engine:** Python 3.14.0 (Free-Threading `cp314t`)  
> **Ref:** [Engineering Playbook](../05_OPERATIONS/ENGINEERING_PLAYBOOK.md)

## 1. PROJECT VISION & PRINCIPLES

```yaml
mission: "Offline-first, event-sourced, cryptographically unbreakable knowledge system"
principles:
  - offline_first: "Local execution only. Zero cloud dependency."
  - data_sovereignty: "User owns the keys. Data is encrypted at rest."
  - event_sourcing: "Append-only log is the single source of truth."
```

## 2. ARCHITECTURAL DECISIONS (THE "WHY")

Các quyết định cốt lõi (Đã được bảo tồn):

- **[ADR-002]** Crypto Engine: Libsodium Strategy
- **[ADR-003]** Backup Crypto: XChaCha20-Poly1305
- **[Spec]** Encryption: Sprint 4 Encryption Spec

## 3. TECH STACK & CONSTRAINTS

```yaml
backend:
  language: "Python 3.14 (Free-Threading Build)"
  execution_mode: "python -X gil=0 -m src.core.main"
  database_schema: "SQLite STRICT (INTEGER only, No BIGINT)"

frontend:
  framework: "Svelte 5"
  desktop: "Tauri v2"
  communication: "JSON-RPC over Tauri Commands"

cryptography:
  library: "PyNaCl (libsodium)"
  encryption: "XChaCha20-Poly1305 (192-bit nonce)"
  kdf: "Argon2id (128MB Memory, 3 Ops)"
```

## 4. CRYPTOGRAPHIC ARCHITECTURE (THE IRON CORE)

### 4.1 Key Hierarchy

```
User Passkey (>=12 chars)
    ↓ Argon2id KDF (OWASP 2025)
KEK (Key Encryption Key, 256-bit)
    ↓ XChaCha20-Poly1305 AEAD
Wrapped DEK (Data Encryption Key) -> Stored in SQLite
DEK (Unwrapped in memory)
    ↓ XChaCha20-Poly1305 AEAD
Encrypted Event Payloads
```

### 4.2 Argon2id Parameters (IMMUTABLE)

```python
ARGON2_OPSLIMIT     = 2                   # iterations
ARGON2_MEMLIMIT     = 19 * 1024 * 1024    # 19 MiB
ARGON2_PARALLELISM  = 1                   # p=1
ARGON2_SALT_BYTES   = 16
```

## 5. DATABASE SCHEMA (DDL - STRICT)

```sql
CREATE TABLE domain_events (
    event_id TEXT PRIMARY KEY,
    stream_type TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    stream_sequence INTEGER NOT NULL,
    payload BLOB NOT NULL, -- ENCRYPTED
    event_hmac TEXT NOT NULL,
    UNIQUE(stream_type, stream_id, stream_sequence)
) STRICT;

CREATE TABLE system_keys (
    id INTEGER PRIMARY KEY,
    salt BLOB NOT NULL,
    encrypted_dek BLOB NOT NULL,
    created_at TEXT NOT NULL
) STRICT;
```

## 6. SPRINT STATUS

- **Sprint 4 (Security):** ✅ COMPLETED.
- **Sprint 5 (Resilience):**
  - ✅ Task 5.1: Recovery Phrase (BIP39) - Functional Style.
  - ✅ Task 5.2: Secure Backup (Atomic Vacuum) - Golden Master.
  - ⏳ Task 5.3: Frontend Integration (NEXT).

## 7. CRITICAL INVARIANTS

1. **Execution:** Always use `python -m src.core.main`.
2. **Database:** `INTEGER` only. No `BIGINT`.
3. **Windows Protocol:** Retry Loop for all File I/O.
4. **Toxic Waste:** Secure Wipe all temporary files.

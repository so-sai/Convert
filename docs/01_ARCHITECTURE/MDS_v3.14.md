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

## 2. ARCHITECTURAL DECISIONS

- **[ADR-002]** Crypto Engine: Libsodium Strategy
- **[ADR-003]** Backup Crypto: XChaCha20-Poly1305 (Omega Standard)
- **[Spec]** Encryption: Sprint 5 Encryption Spec

## 3. TECH STACK & CONSTRAINTS

```yaml
backend:
  language: "Python 3.14 (Free-Threading Build)"
  execution_mode: "python -m src.core.main"
  database_schema: "SQLite STRICT (INTEGER only, No BIGINT)"

frontend:
  framework: "Svelte 5"
  desktop: "Tauri v2"
  communication: "JSON-RPC over Tauri Commands"

cryptography:
  library: "PyNaCl (libsodium)"
  encryption: "XChaCha20-Poly1305 (192-bit nonce)"
  kdf: "Argon2id (128MB Memory, 3 Ops, 4 Lanes)"
```

## 4. CRYPTOGRAPHIC ARCHITECTURE (THE IRON CORE)

### 4.1 Key Hierarchy

```
User Passkey (>=12 chars) OR Recovery Phrase (BIP39)
    ↓ Argon2id KDF (Omega Standard)
KEK (Key Encryption Key, 256-bit)
    ↓ XChaCha20-Poly1305 AEAD
Wrapped DEK (Data Encryption Key) -> Stored in SQLite
DEK (Unwrapped in memory)
    ↓ XChaCha20-Poly1305 AEAD
Encrypted Event Payloads
```

### 4.2 Argon2id Parameters (LOCKED – TASK 5.2 GOLDEN MASTER)

```python
# ĐÃ ĐƯỢC CHỐT TRONG src/core/utils/security.py
ARGON2_BACKUP_OPSLIMIT    = 3
ARGON2_BACKUP_MEMLIMIT    = 134217728    # 128 MiB – OWASP 2025 Hardened
ARGON2_BACKUP_PARALLELISM = 4
ARGON2_SALT_BYTES         = 16
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
  - ✅ Task 5.1: Recovery Phrase (BIP39).
  - ✅ Task 5.2: Secure Backup (Atomic Vacuum + Argon2 128MB).
  - ⏳ Task 5.3: Frontend Integration (NEXT).

## 7. CRITICAL INVARIANTS

1. **Execution:** Always use `python -m src.core.main`.
2. **Database:** `INTEGER` only. No `BIGINT`.
3. **Argon2:** MUST match Task 5.2 Golden Master (128MB/3/4).

## 8. PHYSICAL DIRECTORY STRUCTURE (THE BLUEPRINT)

```text
E:/DEV/Convert/
├── .github/                    # CI/CD Workflows
├── assets/                     # Icons, Resources
├── docs/                       # [KNOWLEDGE BASE]
│   ├── 01_ARCHITECTURE/        # SSOT (MDS, ADRs)
│   │   ├── DECISIONS/          # Immutable Decisions
│   │   └── MDS_v3.14.md        # THIS FILE
│   ├── 04_KNOWLEDGE/           # Lessons Learned
│   └── 05_OPERATIONS/          # Runbooks
├── src/                        # [BACKEND CORE]
│   └── core/                   # Monorepo Root
│       ├── main.py
│       ├── api/                # Bridge Layer
│       ├── database/           # Schema & Migrations
│       ├── security/           # KMS & Recovery
│       ├── services/           # Business Logic
│       └── utils/              # Logging & Paths
├── src-ui/                     # [FRONTEND - Svelte 5]
├── tests/                      # [QA]
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

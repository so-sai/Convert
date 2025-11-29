# 📘 MDS v3.14 - THE ETERNAL PYTHON CORE (GRAND UNIFIED)

> **Status:** SPRINT 5 (PHASE 3: FRONTEND INTEGRATION)
> **Engine:** Python 3.14.0 (Free-Threading `cp314t`)
> **Ref:** [Engineering Playbook](../05_OPERATIONS/ENGINEERING_PLAYBOOK.md)

## 1. PROJECT VISION
"Offline-first, event-sourced, cryptographically unbreakable knowledge system."

## 2. ARCHITECTURAL DECISIONS
- **[ADR-002]** Crypto Engine: Libsodium Strategy (XChaCha20-Poly1305).
- **[ADR-003]** Backup Crypto: Omega Standard (Argon2id 128MB/3 Ops).

## 3. TECH STACK (CONFIRMED)
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
  - 🔄 **Task 5.3: Frontend Integration:** IN PROGRESS.

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


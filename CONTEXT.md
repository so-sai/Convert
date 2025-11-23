# Project CONVERT - Context Document

**Last Updated:** 2025-11-23 (Sprint 4 Complete)  
**Version:** 1.0-crypto-trinity-rev2  
**Status:** Production-Ready Security Architecture

---

## Project Identity

**Name:** CONVERT (Cognitive OS for Networked Vault & Encrypted Repository Technology)

**Mission:** Build an offline-first, cryptographically unbreakable knowledge management system that respects user sovereignty and privacy.

**Philosophy:** "Infinite like Pi, Fast like Python, Secure like Rust."

---

## Current State (Sprint 4 Complete)

### Achievements

**Security Architecture (Crypto Trinity Rev 2):**
- ✅ Argon2id KDF (OWASP 2025: 19 MiB, t=2, p=1)
- ✅ XChaCha20-Poly1305 AEAD encryption
- ✅ HMAC-SHA3-256 integrity chain
- ✅ Epoch Secret key management
- ✅ Double-MAC defense-in-depth
- ✅ SQLite STRICT schema with quarantine

**Code Quality:**
- ✅ 100% test suite passing
- ✅ pytest.ini configuration (asyncio_mode=auto)
- ✅ Comprehensive documentation
- ✅ Engineering standards documented

**Compliance:**
- ✅ OWASP Password Storage Cheat Sheet 2025
- ✅ Anti-NSA (side-channel resistant)
- ✅ DoS resistant (memory-bound KDF)
- ✅ Local-first (zero cloud dependencies)

### Technical Debt

**None identified.** Sprint 4 closed with zero outstanding issues.

---

## Architecture Overview

### The Eternal Vault (Key Management)

```
┌─────────────────────────────────────────────────────────┐
│ User Passkey (>=12 chars, user-memorized)              │
└────────────────────┬────────────────────────────────────┘
                     │ Argon2id (19 MiB, t=2, p=1)
                     ↓
┌─────────────────────────────────────────────────────────┐
│ KEK (Key Encryption Key, 256-bit, derived)             │
└────────────────────┬────────────────────────────────────┘
                     │ XChaCha20-Poly1305 AEAD
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Epoch Secret (Root of Trust, 256-bit, random)          │
│ Stored: Encrypted in SQLite (system_keys table)        │
└────────────────────┬────────────────────────────────────┘
                     │ BLAKE2b Key Derivation
                     ↓
┌─────────────────────────────────────────────────────────┐
│ DEK (Data Encryption Key, 256-bit)                     │
│ HMAC_KEY (Integrity Key, 256-bit)                      │
│ Lifetime: In-memory only (zeroized on lock)            │
└────────────────────┬────────────────────────────────────┘
                     │ XChaCha20-Poly1305 + HMAC-SHA3-256
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Encrypted Event Payloads (domain_events table)         │
│ Protection: AEAD tag (Poly1305) + Chain HMAC (SHA3)    │
└─────────────────────────────────────────────────────────┘
```

### Double-MAC Architecture

**Layer 1 (AEAD):** XChaCha20-Poly1305
- Prevents ciphertext tampering
- 16-byte Poly1305 authentication tag
- Constant-time verification

**Layer 2 (Chain):** HMAC-SHA3-256
- Prevents event reordering/deletion
- Calculated on plaintext (before encryption)
- Enables re-encryption without breaking chain

### Database Schema (Rev 2)

```sql
CREATE TABLE domain_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_type TEXT NOT NULL,
    stream_id TEXT NOT NULL,
    payload BLOB NOT NULL,          -- Ciphertext
    enc_nonce BLOB,                 -- 24 bytes (NULL = legacy plaintext)
    event_hmac BLOB NOT NULL,       -- HMAC-SHA3-256 (32 bytes)
    timestamp INTEGER NOT NULL,
    quarantine INTEGER DEFAULT 0,   -- Tamper detection flag
    tamper_reason TEXT              -- Forensic logging
) STRICT;

CREATE TABLE system_keys (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    salt BLOB NOT NULL,             -- 16 bytes (Argon2id salt)
    enc_dek BLOB NOT NULL,          -- Wrapped Epoch Secret
    dek_nonce BLOB NOT NULL,        -- Empty (nonce inside enc_dek)
    ops_limit INTEGER NOT NULL,     -- 2 (Argon2id iterations)
    mem_limit INTEGER NOT NULL,     -- 19922944 (19 MiB)
    created_at INTEGER DEFAULT (unixepoch())
) STRICT;
```

---

## Technology Stack

### Core

- **Language:** Python 3.14 (Free-Threading Build, No-GIL)
- **Concurrency:** PEP 779 (No-GIL) + PEP 734 (Subinterpreters)
- **Database:** SQLite 3.50.2+ (STRICT mode, CVE-2025-6965 protected)

### Dependencies

**Production:**
- PyNaCl 1.5.0 (libsodium 1.0.19+)
- FastAPI 0.121.3
- Uvicorn 0.38.0
- aiosqlite 0.21.0
- orjson 3.11.4

**Development:**
- pytest 8.x
- pytest-asyncio 0.24.x

### Cryptography

- **Encryption:** XChaCha20-Poly1305 (libsodium)
- **KDF:** Argon2id (libsodium)
- **Integrity:** HMAC-SHA3-256 (Python hashlib)
- **Key Derivation:** BLAKE2b (Python hashlib)

---

## Team Structure

| Role | Agent | Responsibility |
|------|-------|----------------|
| **PM** | Gemini 3.0 Pro | Strategy, planning, backlog management |
| **SA** | ChatGPT 5.1 | Architecture, design, technical specs |
| **SecA** | Grok 4.1 | Security audit, threat modeling |
| **Dev** | DeepSeek V3.2 | Implementation, coding |
| **QA** | Claude 4.5 | Judicial review, quality assurance |

---

## Sprint History

### Sprint 1: Architecture Foundation
- Event sourcing design
- Stream types (Domain, Interaction, Memory)
- Initial database schema

### Sprint 2: Core Backend
- FastAPI application
- SQLite integration
- Fixed BIGINT/Import issues

### Sprint 3: Plugin System & Storage Hardening
- Plugin architecture
- Storage adapter
- Transaction safety

### Sprint 4: The Cryptographic Vault ✅
- **Duration:** 2 weeks
- **Status:** COMPLETE (2025-11-23)
- **Deliverables:**
  - Crypto Trinity Rev 2 (Epoch Secret architecture)
  - OWASP-compliant Argon2id (19 MiB, t=2, p=1)
  - Double-MAC integrity (Poly1305 + HMAC-SHA3-256)
  - pytest.ini configuration standard
  - Comprehensive documentation

### Sprint 5: Hardening Fortress (PLANNED)
- **Duration:** 2 weeks
- **Start Date:** 2025-11-23
- **Focus:** Operational security, supply chain defense
- **Tasks:**
  - Kill Switch Protocol
  - Reproducible builds
  - SBOM generation
  - Self-integrity check
  - Fake data injection

---

## Critical Invariants (The 12 Commandments)

1. **Execution:** Always use `python -m <module>`
2. **Database:** INTEGER only (no BIGINT)
3. **Payload:** Always BLOB
4. **Integrity:** Verify HMAC on read, quarantine on failure
5. **Isolation:** Plugins use defined Protocol
6. **Path:** Use pathlib + UTF-8 encoding
7. **Hygiene:** Code stays in `src/core`
8. **Deps:** `requirements.txt` is single source of truth
9. **Platform:** Use `python -m PyInstaller`
10. **Concurrency:** Thread-safe for No-GIL
11. **Encryption (MANDATORY):** All sensitive data encrypted before INSERT
12. **Vault State:** Return VAULT_LOCKED if not unlocked

---

## Security Policies

### Passkey Requirements

- Minimum length: 12 characters
- Strength validation: Basic complexity (Phase 1)
- Future: zxcvbn integration (Sprint 5)
- **NEVER stored:** Only salt + encrypted DEK persisted

### Argon2id Parameters (LOCKED)

```python
# CRITICAL: These parameters are IMMUTABLE
# Any deviation is a SECURITY VIOLATION
ARGON2_OPSLIMIT   = 2                    # iterations (t=2)
ARGON2_MEMLIMIT   = 19 * 1024 * 1024     # 19 MiB (OWASP 2025 MANDATORY)
ARGON2_PARALLELISM = 1                   # p=1 (side-channel resistance)
```

### Memory Hygiene

- Best-effort zeroization via `secure_wipe()`
- Garbage collection: `gc.collect()`
- Sensitive keys cleared in `finally` blocks
- Idle timeout: 5 minutes (Sprint 5)

---

## Testing Standards

### Mandatory Configuration

**File:** `pytest.ini` (root directory)

```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

### Acceptance Criteria

- ✅ Test suite MUST pass with `python -m pytest` (zero arguments)
- ✅ Virtual environment MUST be active
- ✅ All dependencies installed from `requirements.txt`
- ✅ No `@pytest.mark.asyncio` decorators (redundant with config)

---

## Incident Reports

### Task 4.4 Deployment Failure (2025-11-23)

**Root Cause:** Missing `pytest.ini` configuration for asyncio tests.

**Impact:** Correct KMS implementation blocked by environment setup.

**Resolution:**
1. Created `pytest.ini` with mandatory asyncio configuration
2. Updated Engineering Playbook (Section 7: Testing Standard)
3. Established acceptance criteria for test suite

**Prevention:** All future async projects MUST follow Rule #5 (Pytest Configuration Protocol).

---

## Next Steps (Sprint 5)

### Immediate Priorities

1. **Kill Switch Protocol** - Emergency key wipe (<100ms)
2. **Reproducible Builds** - Deterministic binary hashes
3. **SBOM Generation** - Software Bill of Materials
4. **Self-Integrity Check** - Binary tampering detection
5. **Fake Data Injection** - Anti-traffic analysis

### Future Roadmap

- **Sprint 6:** UI Development (Svelte 5 + Tauri v2)
- **Sprint 7:** P2P Sync (WASM Sandbox)
- **Sprint 8:** Key Rotation & Recovery

---

## References

- **[MDS_v3.14.md](MDS_v3.14.md)** - Master Design Spec
- **[SECURITY_POLICY.md](docs/policies/SECURITY_POLICY.md)** - Security standards
- **[ENGINEERING_PLAYBOOK.md](docs/policies/ENGINEERING_PLAYBOOK.md)** - Development standards
- **[ADR-002](docs/decisions/ADR-002-CRYPTO-LIB.md)** - Crypto library selection
- **[SPRINT_5_PLAN.md](docs/planning/SPRINT_5_PLAN.md)** - Hardening roadmap

---

**Document Control:**
- **Created:** 2025-11-23
- **Owner:** BA (Claude 4.5)
- **Last Review:** Sprint 4 Closure
- **Next Review:** Sprint 5 Completion

---

**Convert will never leak. Never break. Never die.**  
**Forever local. Forever yours.** 🛡️⚡

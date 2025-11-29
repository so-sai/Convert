# DATA DICTIONARY

**Project:** Convert Vault  
**Version:** 1.0 (Crypto Trinity Rev 2)  
**Last Updated:** 2025-11-28  
**Ref:** ADR-002, ADR-003, schema.sql

---

## 1. Table: `system_keys`

**Purpose:** Stores encrypted vault master keys and recovery keys for Sprint 4 (Vault) and Sprint 5 (Recovery).

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS system_keys (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    salt BLOB NOT NULL,
    enc_dek BLOB NOT NULL,
    dek_nonce BLOB NOT NULL,
    ops_limit INTEGER NOT NULL,
    mem_limit INTEGER NOT NULL,
    rk_wrapped_dek BLOB,
    recovery_salt BLOB,
    rk_ops_limit INTEGER DEFAULT 2,
    rk_mem_limit INTEGER DEFAULT 67108864,
    rk_nonce BLOB,
    created_at INTEGER DEFAULT (unixepoch())
) STRICT;
```

### Column Definitions

| Column | Type | Nullable | Purpose | Sprint | Default Value |
|:---|:---|:---|:---|:---|:---|
| `id` | INTEGER | NO | Primary key (always 1) | 4 | - |
| `salt` | BLOB | NO | Argon2id salt for passkey KEK (16 bytes) | 4 | - |
| `enc_dek` | BLOB | NO | Wrapped DEK encrypted with passkey KEK | 4 | - |
| `dek_nonce` | BLOB | NO | XChaCha20 nonce for DEK encryption (24 bytes) | 4 | - |
| `ops_limit` | INTEGER | NO | Argon2id iterations for passkey (2) | 4 | - |
| `mem_limit` | INTEGER | NO | Argon2id memory for passkey (19922944 = 19 MiB) | 4 | - |
| `rk_wrapped_dek` | BLOB | YES | Wrapped DEK encrypted with recovery KEK | 5.1 | NULL |
| `recovery_salt` | BLOB | YES | Argon2id salt for recovery KEK (16 bytes) | 5.1 | NULL |
| `rk_ops_limit` | INTEGER | YES | Argon2id iterations for recovery (2) | 5.1 | 2 |
| `rk_mem_limit` | INTEGER | YES | Argon2id memory for recovery (67108864 = 64 MiB) | 5.1 | 67108864 |
| `rk_nonce` | BLOB | YES | XChaCha20 nonce for recovery DEK encryption (24 bytes) | 5.1 | NULL |
| `created_at` | INTEGER | NO | Unix epoch timestamp | 4 | unixepoch() |

### Business Logic

**Dual-Wrap Architecture (Sprint 5.1):**
- The same DEK is wrapped **twice**:
  1. **Passkey Path:** `enc_dek` = Encrypt(DEK, Passkey_KEK)
  2. **Recovery Path:** `rk_wrapped_dek` = Encrypt(DEK, Recovery_KEK)

**Key Derivation:**
- **Passkey KEK:** `Argon2id(user_passkey, salt, ops=2, mem=19MiB)`
- **Recovery KEK:** `Argon2id(recovery_seed, recovery_salt, ops=2, mem=64MiB)`

**Constraints:**
- Only ONE row exists (id=1)
- `salt` and `recovery_salt` MUST be exactly 16 bytes (NaCl requirement)
- `dek_nonce` and `rk_nonce` MUST be exactly 24 bytes (XChaCha20 requirement)

---

## 2. Table: `domain_events`

**Purpose:** Event-sourced log of all domain events with encryption and integrity protection.

### Crypto Columns

| Column | Type | Purpose | Sprint |
|:---|:---|:---|:---|
| `payload` | BLOB | Encrypted event data (Ciphertext \|\| Poly1305 Tag) | 4 |
| `enc_algorithm` | TEXT | Encryption algorithm (default: XChaCha20-Poly1305) | 4 |
| `enc_key_id` | TEXT | Epoch ID for key rotation (default: v1) | 4 |
| `enc_nonce` | BLOB | 24-byte nonce (NULL = legacy plaintext) | 4 |
| `event_hmac` | BLOB | HMAC-SHA3-256 of plaintext payload | 4 |
| `prev_event_hash` | BLOB | SHA3-256 hash of previous event (chain) | 4 |
| `event_hash` | BLOB | SHA3-256 hash of current event | 4 |

### Forensics Columns

| Column | Type | Purpose | Sprint |
|:---|:---|:---|:---|
| `quarantine` | INTEGER | 0=OK, 1=Tampered/Corrupt | 4 |
| `tamper_reason` | TEXT | Reason for quarantine | 4 |

**Business Logic:**
- `enc_nonce = NULL` → Legacy plaintext event (pre-Sprint 4)
- `enc_nonce != NULL` → Encrypted event (Sprint 4+)
- `quarantine = 1` → Event failed integrity check, isolated for forensics

---

## 3. Table: `notes`

**Purpose:** Projection table for note content (encrypted).

### Crypto Columns

| Column | Type | Purpose |
|:---|:---|:---|
| `content` | BLOB | Encrypted note content |
| `metadata` | BLOB | Encrypted note metadata |
| `enc_algorithm` | TEXT | Encryption algorithm (default: pass-through) |
| `enc_key_id` | TEXT | Epoch ID |
| `enc_nonce` | BLOB | 24-byte nonce |

---

## 4. Backup File Format (`.cvbak`)

**Purpose:** Portable encrypted backup (Sprint 5.2).

**Binary Structure:**
```
[MAGIC (8 bytes): "CVBAK002"]
[BACKUP_SALT (16 bytes)]
[STREAM_HEADER (24 bytes)]
[ENCRYPTED_CHUNKS (variable)]
```

**Encryption:**
- **Algorithm:** XChaCha20-Poly1305 (libsodium secretstream)
- **Key Derivation:** `Argon2id(passkey, backup_salt, ops=3, mem=128MiB, p=4)`
- **Compression:** zlib level 6 (before encryption)

---

**Maintained By:** BA (Claude)  
**Date:** 2025-11-28

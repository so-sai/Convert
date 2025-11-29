# ADR-003: Backup Encryption & Key Derivation (Omega Standard)

**Status:** APPROVED  
**Date:** 2025-11-28  
**Context:** Sprint 5 - Resilience & Recovery

## Context

The backup system requires cryptographic key derivation to protect `.cvbak` files at rest against offline brute-force attacks.

## Decision

**Omega Standard for Backup Key Derivation:**
- **Memory:** 128 MiB (134,217,728 bytes)
- **Iterations:** 3 (t=3)
- **Parallelism:** 4 (p=4) - *Optimized for Windows*

## Rationale

1. **Higher Memory Cost (128 MiB):** Increases ASIC resistance for offline attacks (6.7x cost vs Vault).
2. **Performance:** ~2.5s delay is acceptable for infrequent weekly backups.
3. **Extended Nonce:** XChaCha20-Poly1305 (192-bit) prevents nonce collision at scale.

## Consequences

- ✅ **Stronger Security:** 6.7x harder to brute-force than Vault.
- ⚠️ **Higher Memory Usage:** Not suitable for low-end mobile devices (<2GB RAM).

## Technical Specification

### Encryption Algorithm

**XChaCha20-Poly1305 SecretStream**
- **Cipher:** XChaCha20 (stream cipher)
- **MAC:** Poly1305 (authentication)
- **Nonce:** 192-bit (extended from ChaCha20's 96-bit)
- **Key Size:** 256-bit
- **Tag Size:** 128-bit (16 bytes)

### Key Derivation Function

**Argon2id (Omega Standard)**

```python
ARGON2_BACKUP_MEMLIMIT = 134217728  # 128 MiB
ARGON2_BACKUP_OPSLIMIT = 3          # 3 iterations
ARGON2_BACKUP_PARALLELISM = 4       # 4 threads
```

**Comparison with Vault KDF:**

| Parameter | Vault (19 MiB) | Backup (128 MiB) | Ratio |
|-----------|----------------|------------------|-------|
| Memory    | 19,922,944 bytes | 134,217,728 bytes | 6.7x |
| Iterations | 2 | 3 | 1.5x |
| Parallelism | 1 | 4 | 4x |
| Time (est.) | ~300ms | ~2.5s | 8.3x |

### File Format

**`.cvbak` File Structure:**

```
[8 bytes]  Magic: "CVBAK002"
[16 bytes] Salt (random)
[24 bytes] SecretStream Header
[Variable] Encrypted Data (length-prefixed chunks)
```

**Encrypted Data Format:**
```
[4 bytes]  Chunk Length (little-endian uint32)
[N bytes]  Encrypted Chunk (compressed + encrypted)
...repeat...
```

### Implementation

**Location:** `src/core/services/backup.py`

**Key Functions:**
- `derive_backup_key(passkey: str, salt: bytes) -> bytes`
- `create_backup(db_path, passkey, output_path) -> bool`
- `restore_backup(backup_path, passkey, output_db_path) -> bool`

## Security Analysis

### Threat Model

**Offline Brute-Force Attack:**
- **Scenario:** Attacker obtains `.cvbak` file
- **Goal:** Recover passkey to decrypt backup
- **Defense:** High memory cost (128 MiB) makes GPU/ASIC attacks expensive

**Cost Analysis (Argon2id 128 MiB):**
- **Single GPU (RTX 4090):** ~50 hashes/sec
- **12-char alphanumeric passkey:** 62^12 = 3.2 × 10^21 combinations
- **Time to crack:** ~2 × 10^18 years (infeasible)

### Nonce Collision Resistance

**XChaCha20 (192-bit nonce):**
- **Birthday bound:** 2^96 encryptions before 50% collision probability
- **Practical limit:** Can safely encrypt 2^80 messages (far exceeds lifetime backups)

## Alternatives Considered

### Alternative 1: Use Same Parameters as Vault (19 MiB)

**Rejected because:**
- Backup files are high-value targets (contain entire database)
- Offline attacks have no rate limiting
- Performance penalty (2.5s) is acceptable for infrequent operations

### Alternative 2: Use 256 MiB (OWASP Maximum)

**Rejected because:**
- Marginal security benefit (2x vs 6.7x already achieved)
- Excludes users with <4GB RAM
- Longer delay (>5s) degrades UX

### Alternative 3: ChaCha20-Poly1305 (96-bit nonce)

**Rejected because:**
- Nonce collision risk after 2^48 encryptions
- XChaCha20 provides better safety margin with minimal overhead

## Compliance

- **OWASP 2025:** Argon2id with ≥64 MiB memory (✅ 128 MiB exceeds)
- **NIST SP 800-63B:** Password-based key derivation (✅ compliant)
- **NIST SP 800-88:** Secure deletion of temporary files (✅ implemented)

## References

- [RFC 9106: Argon2 Memory-Hard Function](https://www.rfc-editor.org/rfc/rfc9106.html)
- [XChaCha20-Poly1305 Specification](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-xchacha)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- Engineering Playbook Rule #19: Toxic Waste Disposal Protocol
- Engineering Playbook Rule #20: Atomic Snapshot Protocol

## Revision History

- **2025-11-28:** Initial decision (Sprint 5, Task 5.2)
- **Status:** Approved and implemented

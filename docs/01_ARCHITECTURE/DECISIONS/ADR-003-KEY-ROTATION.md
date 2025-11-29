# ADR-003: Key Rotation & Re-encryption Architecture

**Status:** ACCEPTED  
**Date:** 2025-11-23 (Rev 2)  
**Target:** Sprint 5  
**Dependency:** ADR-002  

---

## 1. Context

The Cryptographic Vault MUST support key rotation without breaking the immutable Hash Chain. This is critical for:
- **Passkey changes** (user-initiated)
- **Security incidents** (compromise recovery)
- **Compliance requirements** (periodic rotation policies)

---

## 2. Decision: Three-Tier Rotation Model

| Tier | Trigger | Scope | Implementation |
|:-----|:--------|:------|:---------------|
| **Tier-1** | Change Passkey | KEK Only | Re-wrap the DEK with new KEK. Data untouched. |
| **Tier-2** | Soft Rotation | DEK + Future Writes | Generate New Epoch. Old data stays (Epoch 1). New data uses Epoch 2. |
| **Tier-3** | Hard Rotation | Full Compromise | Batch re-encrypt ALL data. Expensive but thorough. |

---

## 3. Key Hierarchy (Final)

```
User Passkey
    ↓
Argon2id(19MiB, t=2, p=1)
    ↓
KEK (32 bytes)
    ↓
HKDF-SHA3-256 (Salt: EpochID)
    ├──► DEK (Encryption Key, 32 bytes)
    └──► HMAC-Key (Integrity Key, 32 bytes)
```

**Key Insight:** A single `EpochID` derives **both** the DEK and HMAC-Key for that row, ensuring cryptographic binding.

---

## 4. Key Versioning Logic

### 4.1 Epoch ID (`enc_key_id`)
- The `enc_key_id` column in the database represents the **Epoch ID**.
- Format: `v1`, `v2`, `v3`, etc.
- Each Epoch ID derives a unique pair of (DEK, HMAC-Key) via HKDF.

### 4.2 Derivation Process
```python
def derive_epoch_keys(master_key: bytes, epoch_id: str) -> tuple[bytes, bytes]:
    """Derive DEK and HMAC-Key from Master Key and Epoch ID."""
    # Use HKDF with epoch_id as salt
    salt = epoch_id.encode('utf-8')
    
    # Derive 64 bytes total
    okm = hkdf_sha3_256(
        master_key,
        salt=salt,
        info=b"CONVERT_VAULT_EPOCH",
        length=64
    )
    
    dek = okm[:32]        # First 32 bytes for encryption
    hmac_key = okm[32:]   # Last 32 bytes for HMAC
    
    return dek, hmac_key
```

### 4.3 Hash Chain Preservation (CRITICAL)
When rotating keys (Tier-3), the process is:
1. Decrypt old ciphertext → recover plaintext
2. Re-encrypt with new DEK
3. **DO NOT recompute** `event_hash` (it's based on plaintext, must stay constant)
4. Update DB: new ciphertext, new nonce, new `enc_key_id`, **same** `event_hash`

**Test:** Migration script MUST verify hash chain integrity after re-encryption.

---

## 5. Database Readiness

The `domain_events` schema uses `enc_key_id` to track the Key Epoch:

```sql
CREATE TABLE domain_events (
    -- ...
    enc_key_id TEXT DEFAULT 'v1',  -- Epoch ID
    -- ...
);
```

---

## 6. Tier-1 Rotation: Passkey Change

**Scenario:** User wants to change their passkey.

**Procedure:**
1. Validate new passkey strength
2. Unlock vault with old passkey → get DEK
3. Derive new KEK from new passkey (Argon2id)
4. Re-wrap DEK with new KEK
5. Atomic database update to `system_keys` table
6. Zeroize old KEK

**Impact:** Instant. No data re-encryption needed.

---

## 7. Tier-2 Rotation: Soft Rotation

**Scenario:** Periodic security policy requires new DEK.

**Procedure:**
1. Generate new Epoch ID (e.g., `v2`)
2. Derive new (DEK, HMAC-Key) pair from Master Key + `v2`
3. All **new** writes use Epoch `v2`
4. **Old** data remains encrypted with Epoch `v1`
5. Reads check `enc_key_id` and use appropriate keys

**Impact:** Gradual. Old data readable indefinitely.

---

## 8. Tier-3 Rotation: Hard Rotation

**Scenario:** Security incident, full compromise recovery.

**Procedure:**
1. Generate new Epoch ID (e.g., `v3`)
2. Batch process:
   - For each event:
     - Decrypt with old epoch keys
     - Re-encrypt with new epoch keys
     - Preserve `event_hash` (plaintext-based)
     - Update `enc_key_id`, `enc_nonce`, `payload`
3. Verify hash chain integrity
4. Mark old epochs as `deprecated`

**Impact:** Expensive. Requires downtime or read-only mode.

---

## 9. Implementation Roadmap

### Sprint 5 (Planned)
- [ ] Implement HKDF-SHA3-256 key derivation
- [ ] Tier-1 rotation (Passkey change)
- [ ] Tier-2 rotation (Soft rotation)
- [ ] Migration tests (verify hash chain preservation)

### Sprint 6 (Future)
- [ ] Tier-3 rotation (Hard rotation)
- [ ] Automated rotation policies
- [ ] Key rotation audit logging

---

## 10. Security Considerations

### 10.1 Zeroization
All intermediate keys (old DEK, old HMAC-Key) MUST be zeroized after rotation.

### 10.2 Atomicity
Rotation operations MUST be atomic (SQLite transactions).

### 10.3 Rollback Protection
Commit seals (every 256 events) prevent rollback to old epochs.

---

**ADR-003 APPROVED**

**Document Version:** 1.0  
**Last Updated:** 2025-11-23  
**Maintained By:** BA_CLAUDE + SA Team

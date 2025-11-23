# Security Appendix: The 13 Eternal Rules of Convert Vault

**Status:** CANONICAL & IMMUTABLE  
**Date:** 2025-11-23 (Rev 2)  
**Authority:** Security Architect + Supreme Judicial Review  

---

## The 13 Eternal Rules

### Rule #1: 192-bit Random Nonces
**Mandate:** Standard ChaCha20 (96-bit) is **banned forever**.  
**Reason:** Counter-based nonces are operationally risky in offline/distributed systems.  
**Enforcement:** Use XChaCha20-Poly1305 with `nacl.utils.random(24)`.

---

### Rule #2: No Plaintext Fallback
**Mandate:** If `enc_nonce` is present, `TamperDetectedError` MUST be raised on MAC failure.  
**Reason:** Never return raw data ignoring the MAC.  
**Exception:** See Rule #13 (Legacy Handling).

---

### Rule #3: Fail Closed
**Mandate:** Quarantine records on integrity failure. Never skip or ignore.  
**Reason:** Defense-in-depth. Suspicious data must be isolated.  
**Implementation:** Set `quarantine=1`, log `tamper_reason`.

---

### Rule #4: Eternal Hash Chain
**Mandate:** HMAC/Hash is computed on **Plaintext** BEFORE encryption.  
**Reason:** Preserves chain integrity during re-encryption/migration.  
**Implementation:** `event_hash = SHA3-256(prev_hash || plaintext)`.

---

### Rule #5: Key Separation
**Mandate:** Never reuse the same key for AEAD and HMAC.  
**Reason:** Cryptographic hygiene, defense-in-depth.  
**Enforcement:** Use HKDF to derive separate DEK and HMAC-Key.

---

### Rule #6: OWASP Params
**Mandate:** Argon2id MUST use **19 MiB**, t=2, p=1.  
**Reason:** OWASP 2025 compliance, mobile performance optimization.  
**Enforcement:** Hardcoded in `src/core/security/key_derivation.py`.

---

### Rule #7: Doomsday Protocol
**Mandate:** DEK is zeroized from RAM after 5 minutes idle.  
**Reason:** Minimize attack surface for memory dumping.  
**Implementation:** Background timer in `KMS` class.

---

### Rule #8: Kill Switch
**Mandate:** Local-only `/vault/panic` endpoint, WebAuthn protected, destroys KEK/DEK in RAM.  
**Reason:** Emergency response to active compromise.  
**Implementation:** Sprint 5 (Future).

---

### Rule #9: Commit Seals
**Mandate:** Every 256 entries, sign the state to prevent Rollback.  
**Reason:** Rollback attack protection.  
**Implementation:** Sprint 5 (Future).

---

### Rule #10: Reproducible Builds
**Mandate:** PyInstaller builds MUST be verifiable.  
**Reason:** Supply chain security.  
**Enforcement:** Check `sys.frozen` and verify binary hash.

---

### Rule #11: Self-Verification
**Mandate:** App verifies its own binary integrity on startup.  
**Reason:** Detect tampering of the executable.  
**Implementation:** Sprint 6 (Future).

---

### Rule #12: Zero Trust Storage
**Mandate:** The database file is considered public/hostile.  
**Reason:** Defense-in-depth. Assume attacker has full DB access.  
**Enforcement:** All sensitive data encrypted, all integrity protected.

---

### Rule #13: Legacy Handling
**Mandate:**  
- `enc_nonce = NULL` → Legacy Plaintext (Migration mode, ALLOW).  
- `enc_nonce != NULL` → Mandatory Encryption (Decrypt MUST succeed or QUARANTINE).

**Reason:** Resolves conflict between Rule #2 and migration requirements.  
**Implementation:**
```python
if enc_nonce is None:
    # Legacy plaintext data
    return payload  # No decryption
else:
    # Encrypted data - MUST decrypt successfully
    try:
        plaintext = decrypt(payload, enc_nonce, dek)
        return plaintext
    except DecryptionError:
        # CRITICAL: Tamper detected
        quarantine_event(event_id, "Decryption failed")
        raise TamperDetectedError("Integrity violation")
```

---

## Enforcement

**Violation of any rule = Automatic Security Rejection.**

All code reviews, audits, and deployments MUST verify compliance with these 13 rules.

---

**Document Control:**
- **Owner:** Security Architect (SecA)
- **Reviewers:** Supreme Judicial Review (Claude 4.5)
- **Next Review:** Sprint 5 completion
- **Classification:** Internal Use Only

**Signature:** `>>> [NODE: SECA] :: [RULES: ETERNAL] :: [HASH: ETERNAL-RULES-V1.0]`

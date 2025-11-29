# TECH SPEC: SPRINT 4 - ENCRYPTION & KEY MANAGEMENT

**Status:** APPROVED
**Sprint:** 4
**Feature:** Cryptographic Vault & Storage Integration

## 1. OVERVIEW
Implementation of the "Eternal Vault" architecture to secure all sensitive data at rest using XChaCha20-Poly1305 and Argon2id.

## 2. REQUIREMENTS

### 2.1 Safety Mechanism (Backward Compatibility)
- **Requirement:** The `StorageAdapter` MUST support reading legacy (unencrypted) data during the migration phase.
- **Implementation:**
  - When reading data (`get_events`, `get_note`), the system MUST attempt to decrypt.
  - **CRITICAL:** Wrap the decryption logic in a `try-except` block.
  - If decryption fails (e.g., `CryptoError` or invalid UTF-8 after decrypt), assume the data is legacy plaintext and return it as-is (or attempt to parse as JSON if applicable).
  - **Log:** Emit a warning when legacy data is encountered.

### 2.2 Deployment Protocol (Task 4.4)
- **Output Requirement:** The integration code MUST be delivered as a standalone Python script named `update_task_4_4.py`.
- **Behavior:** This script, when run, will:
  1. Backup existing `src/core/adapters/storage.py`.
  2. Rewrite `src/core/adapters/storage.py` with the new `KMS` integrated version.
  3. Rewrite `src/core/main.py` (if needed for startup flow).
  4. Run a verification check.

## 3. SECURITY PARAMETERS (FROZEN)
- **KDF:** Argon2id (19 MiB memory cost).
- **Encryption:** XChaCha20-Poly1305.
- **Nonce:** 192-bit (24 bytes).

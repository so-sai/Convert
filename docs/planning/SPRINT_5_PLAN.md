# SPRINT 5 PLAN: THE FORTRESS

**Status:** DRAFT
**Sprint Goal:** Bê tông hóa hệ thống, chống tấn công Supply Chain và Traffic Analysis.

## 1. OBJECTIVES

1.  **Kill Switch (`/vault/panic`)**: Immediate zeroization of sensitive data in RAM and locking of the DB.
2.  **Supply Chain Defense**: Ensure builds are reproducible and dependencies are verified (SBOM).
3.  **Fake Data Injection**: Generate traffic noise to mask real user activity patterns.

## 2. DETAILED TASKS

### S5.1: Implement Kill Switch
- **Trigger:** Command `/vault/panic` or specific API call.
- **Actions:**
    - **Wipe RAM:** Overwrite DEK, Master Key, and Passkey in memory with zeros.
    - **Lock DB:** Close SQLite connection immediately.
    - **Crash:** Forcefully terminate the process (optional, or return to safe state).
- **Verification:** Memory dump analysis (if possible) or functional test ensuring subsequent reads fail with `VAULT_LOCKED`.

### S5.2: Supply Chain Defense
- **Reproducible Builds:** Ensure `pyinstaller` builds are deterministic.
- **SBOM:** Generate Software Bill of Materials.
- **Verification:** Hash comparison of builds.

### S5.3: Fake Data Injection (Traffic Noise)
- **Mechanism:** Background task that periodically writes "dummy" encrypted events.
- **Stealth:** Dummy events must look indistinguishable from real encrypted events (same size distribution, same timing patterns).
- **Storage:** Dummy events stored in `domain_events` but flagged or identifiable only by the system (e.g., specific metadata or separate stream that is filtered out on read). *Refinement needed: How to distinguish without leaking metadata?* -> Maybe use a specific stream type that is ignored by business logic but looks real to an observer.

## 3. IMPLEMENTATION PLAN

### 3.1 Kill Switch
- Modify `KMS` class to add `panic()` method.
- `panic()` should:
    - `ctypes.memset` key buffers.
    - Set internal state to `LOCKED`.
    - Call `gc.collect()`.

### 3.2 Supply Chain
- Create `scripts/generate_sbom.py`.
- Update `mds-core.spec` to enforce deterministic behavior (if supported).

### 3.3 Fake Data
- Create `src/core/security/noise.py`.
- Implement `NoiseGenerator` class.

## 4. VERIFICATION
- **Unit Tests:** `tests/security/test_panic.py`, `tests/security/test_noise.py`.
- **Manual:** Verify build hashes.

# TEST PLAN: TASK 5.2 - SECURE BACKUP & RESTORE (V2.2)

**Task:** 5.2 - Secure Backup & Restore Strategy  
**Sprint:** Sprint 5 - Resilience & Recovery  
**QA Lead:** Gemini (Antigravity)  
**Status:** READY FOR TESTING  
**Date:** 2025-11-28  
**Spec Version:** V2.2 (Paranoid Edition)

---

## 1. Test Scope

### 1.1 In-Scope
- ✅ Backup Key Derivation (Argon2id 256MB/4ops)
- ✅ Header Encryption (48-byte encrypted header)
- ✅ Streaming Export/Restore Pipeline
- ✅ Secure Wipe (1-pass + Rename + Unlink)
- ✅ Gentle Nudge UX (Event-driven notifications)
- ✅ Drag & Drop Restore
- ✅ Cross-Device Portability

### 1.2 Out-of-Scope
- ❌ Cloud sync (offline-first only)
- ❌ Incremental backups (full snapshot only)
- ❌ Backup scheduling (manual trigger only)

---

## 2. Performance Thresholds (CRITICAL)

| Metric | Threshold | Fail Condition |
|--------|-----------|----------------|
| **Argon2id Memory Usage** | ≤ 128 MiB | > 130 MiB |
| **Backup Time (1GB DB)** | ≤ 3 seconds | > 5 seconds |
| **Restore Time (1GB DB)** | ≤ 4 seconds | > 6 seconds |
| **Temp File Cleanup** | < 100ms | > 500ms |
| **UI Thread Block** | 0ms (async) | Any blocking |

**CRITICAL:** Memory usage MUST NOT exceed 130 MiB to ensure compatibility with 8GB RAM devices.

---

## 3. Test Cases

### 3.1 Cryptographic Security

#### TC-5.2-CRYPTO-001: Backup Key Derivation
**Objective:** Verify Argon2id parameters match spec.

**Steps:**
1. Trigger backup with passkey `TestPass123!`.
2. Monitor memory usage during KDF.
3. Verify parameters: `ops=4`, `mem=256*1024*1024`.

**Expected:**
- ✅ Memory usage ≤ 128 MiB (STRICT).
- ✅ KDF completes in < 2 seconds.

**Fail Condition:**
- ❌ Memory > 130 MiB.
- ❌ KDF takes > 3 seconds.

---

#### TC-5.2-CRYPTO-002: Header Encryption
**Objective:** Verify no plaintext metadata in `.cvbak`.

**Steps:**
1. Create backup.
2. Open `.cvbak` in hex editor.
3. Search for `CVBAK002` magic bytes.

**Expected:**
- ✅ Magic bytes NOT found in plaintext.
- ✅ First 48 bytes are encrypted ciphertext.

**Fail Condition:**
- ❌ `CVBAK002` visible in hex dump.

---

#### TC-5.2-CRYPTO-003: Stream Authentication
**Objective:** Verify tampering detection.

**Steps:**
1. Create backup.
2. Modify byte at offset 0x100 in `.cvbak`.
3. Attempt restore.

**Expected:**
- ✅ Restore fails with `IntegrityError`.
- ✅ Error message: "Stream authentication failed".

**Fail Condition:**
- ❌ Restore succeeds with corrupted file.

---

### 3.2 Forensics & Anti-Forensics

#### TC-5.2-FORENSIC-001: Secure Wipe (1-Pass)
**Objective:** Verify temp file is unrecoverable.

**Steps:**
1. Create backup (generates `temp_{uuid}.db`).
2. Monitor file operations.
3. Verify temp file is:
   - Overwritten with random bytes (1 pass).
   - Renamed to `.trash_{random}`.
   - Unlinked.

**Expected:**
- ✅ Temp file overwritten with `nacl.utils.random()`.
- ✅ File renamed before deletion.
- ✅ File unlinked within 100ms.

**Fail Condition:**
- ❌ Temp file deleted without overwrite.
- ❌ Cleanup takes > 500ms.

---

#### TC-5.2-FORENSIC-002: Memory Hygiene
**Objective:** Verify keys are zeroized.

**Steps:**
1. Create backup.
2. Capture memory dump after backup completes.
3. Search for `backup_key` in memory.

**Expected:**
- ✅ Backup key NOT found in memory dump.

**Fail Condition:**
- ❌ Key material found in memory.

---

### 3.3 UX: Gentle Nudge System

#### TC-5.2-UX-001: Smart Toast Notification (Non-Blocking)
**Objective:** Verify nudge does NOT block UI.

**Steps:**
1. Create 10 notes (trigger Nudge #1).
2. Observe notification behavior.

**Expected:**
- ✅ Toast notification appears (bottom-right).
- ✅ UI remains interactive (can type in editor).
- ✅ Notification auto-dismisses after 10 seconds.

**Fail Condition:**
- ❌ Modal dialog blocks UI.
- ❌ User cannot interact with app during nudge.

---

#### TC-5.2-UX-002: Event-Driven Triggers
**Objective:** Verify nudges are contextual, not time-based.

**Steps:**
1. Create 9 notes → No nudge.
2. Create 10th note → Nudge #1 appears.
3. Dismiss nudge.
4. Wait 2 months (simulated) → No nudge.
5. Edit high-value note (>500 words) → Nudge #2 appears.

**Expected:**
- ✅ Nudges triggered by events, not calendar.

**Fail Condition:**
- ❌ Nudge appears based on time alone.

---

#### TC-5.2-UX-003: Escape Hatch
**Objective:** Verify user can permanently opt-out.

**Steps:**
1. Trigger Nudge #1.
2. Click **[Don't remind me again]**.
3. Confirm opt-out.
4. Create 100 more notes.

**Expected:**
- ✅ No further nudges appear.
- ✅ Opt-out preference persisted in DB.

**Fail Condition:**
- ❌ Nudge appears again after opt-out.

---

### 3.4 Restore Workflow

#### TC-5.2-RESTORE-001: Drag & Drop
**Objective:** Verify drag-and-drop restore.

**Steps:**
1. Create backup → `vault_2025.cvbak`.
2. Drag file onto Dashboard.
3. Verify passkey prompt appears.
4. Enter correct passkey.

**Expected:**
- ✅ Passkey prompt appears AFTER drop.
- ✅ Restore completes successfully.
- ✅ Old DB preserved as `mds.db.backup_{timestamp}`.

**Fail Condition:**
- ❌ No passkey prompt.
- ❌ Old DB overwritten without backup.

---

#### TC-5.2-RESTORE-002: Cross-Device Portability
**Objective:** Verify backup works on different machine.

**Steps:**
1. Create backup on Machine A (Windows 11).
2. Copy `.cvbak` to Machine B (macOS).
3. Restore using same passkey.

**Expected:**
- ✅ Restore succeeds on different OS.
- ✅ All notes intact.
- ✅ DB integrity check passes.

**Fail Condition:**
- ❌ Restore fails on different platform.

---

#### TC-5.2-RESTORE-003: Wrong Passkey
**Objective:** Verify graceful failure.

**Steps:**
1. Create backup with passkey `Correct123!`.
2. Attempt restore with passkey `Wrong456!`.

**Expected:**
- ✅ Restore fails with `AuthenticationError`.
- ✅ Error message: "Invalid passkey".
- ✅ Max 3 retry attempts.

**Fail Condition:**
- ❌ Restore succeeds with wrong passkey.
- ❌ Unlimited retry attempts.

---

### 3.5 Edge Cases

#### TC-5.2-EDGE-001: Insufficient Disk Space
**Objective:** Verify pre-flight check.

**Steps:**
1. Mock disk space to 100 MB.
2. Attempt backup of 200 MB DB.

**Expected:**
- ✅ Backup fails immediately.
- ✅ Error message: "Need 300MB, have 100MB".
- ✅ No partial file created.

**Fail Condition:**
- ❌ Partial backup file created.

---

#### TC-5.2-EDGE-002: Large Database (5GB)
**Objective:** Verify streaming handles large files.

**Steps:**
1. Create 5GB database.
2. Create backup.
3. Monitor memory usage.

**Expected:**
- ✅ Memory usage ≤ 128 MiB (streaming).
- ✅ Backup completes without OOM.

**Fail Condition:**
- ❌ Memory usage > 500 MiB.
- ❌ OOM error.

---

## 4. Acceptance Checklist

### 4.1 Security (MANDATORY)
- [ ] Header fully encrypted (no plaintext magic bytes)
- [ ] Argon2id memory ≤ 128 MiB (STRICT)
- [ ] Tampering detected (stream authentication)
- [ ] Temp files securely wiped (1-pass + rename + unlink)
- [ ] Keys zeroized after use

### 4.2 UX (MANDATORY)
- [ ] Smart toast notifications (non-blocking)
- [ ] Event-driven triggers (not time-based)
- [ ] Escape hatch works (permanent opt-out)
- [ ] Drag & drop restore functional

### 4.3 Portability (MANDATORY)
- [ ] Backup works on Windows/macOS/Linux
- [ ] Same passkey + file = successful restore
- [ ] No dependency on original vault DEK

### 4.4 Performance (MANDATORY)
- [ ] Backup 1GB DB in ≤ 3 seconds
- [ ] Restore 1GB DB in ≤ 4 seconds
- [ ] UI never blocks during backup/restore

### 4.5 Error Handling (MANDATORY)
- [ ] Wrong passkey fails gracefully (max 3 retries)
- [ ] Disk space check prevents partial backups
- [ ] Corrupted file detected before restore
- [ ] Old DB preserved until verification passes

---

## 5. Test Environment

**Hardware:**
- CPU: Intel i5-12400 or equivalent
- RAM: 8 GB (minimum spec)
- Disk: SSD (NVMe preferred)

**Software:**
- OS: Windows 11 24H2 / macOS Sequoia / Ubuntu 24.04
- Python: 3.14.0 (Free-Threading)
- Dependencies: Per `requirements.txt`

**Test Data:**
- Small DB: 10 MB (100 notes)
- Medium DB: 1 GB (10,000 notes)
- Large DB: 5 GB (50,000 notes)

---

## 6. Risk Matrix

| Risk | Severity | Mitigation |
|------|----------|------------|
| Memory > 130 MiB | CRITICAL | Fail build, block merge |
| UI thread blocking | HIGH | Async enforcement |
| Temp file recovery | MEDIUM | Forensic verification |
| Cross-platform failure | HIGH | Multi-OS CI/CD |

---

**Status:** READY FOR EXECUTION  
**Approved By:** QA Lead (Gemini)  
**Date:** 2025-11-28

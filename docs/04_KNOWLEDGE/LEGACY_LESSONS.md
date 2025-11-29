# 🏛️ CONVERT LEGACY LESSONS - The "Why" Behind the Rules

> **Purpose:** Post-mortem analysis of critical failures that shaped our architecture  
> **Warning:** Read this before removing "weird" code (especially `gc.collect()` or retry loops)  
> **Status:** Living document - updated after each major incident

---

## 📖 How to Use This Document

**When to read:**
- Before removing code that seems "unnecessary" or "overcomplicated"
- When debugging similar issues to past incidents
- When onboarding new team members or AI agents
- Before making architectural decisions that might reintroduce old bugs

**Structure:**
Each lesson follows this format:
1. **Symptom** - What the error looked like
2. **Context** - When/where it occurred
3. **Root Cause** - Technical explanation of why it happened
4. **Solution** - The pattern/protocol that fixed it
5. **Artifact** - Where to find the implementation

---

## 🔥 INCIDENT 1: The Windows File Locking Disaster

**Date:** Sprint 5, Task 5.2 (Backup Service Implementation)  
**Severity:** HIGH - Blocked entire test suite on Windows  
**Related Rule:** Engineering Playbook Rule #17 (Windows Persistence Protocol)

### Symptom
```
[WinError 32] The process cannot access the file because 
it is being used by another process
```

Test failures when trying to delete or move database files after backup/restore operations.

### Context
- **Environment:** Windows 11, Python 3.14, aiosqlite
- **Operation:** Backup tests creating/restoring `.db` files
- **Frequency:** Intermittent on small files, consistent on large files (>70KB)

### Root Cause Analysis

**Primary Causes:**
1. **SQLite WAL Mode:** Creates auxiliary files (`.db-shm`, `.db-wal`) that Windows holds longer than the main connection
2. **Python GC Latency:** `async with` context manager doesn't guarantee immediate handle release
3. **Windows File System:** Exclusive locks on open files, no POSIX-style "unlink while open"
4. **Antivirus/Indexing:** Windows Defender scans new files, holding handles

**Technical Deep Dive:**
```python
# This code LOOKS correct but FAILS on Windows:
async with aiosqlite.connect(db_path) as db:
    await db.execute("INSERT INTO notes VALUES ('test')")
    await db.commit()
# Context manager exits here, but...

# Immediately trying to delete fails:
db_path.unlink()  # WinError 32!
```

**Why it fails:**
- `aiosqlite` connection object still exists in local scope
- Python GC hasn't collected it yet (non-deterministic timing)
- Windows holds file handle until GC actually runs
- WAL files (`.db-shm`, `.db-wal`) may have separate handles

### Solution: The Windows Persistence Protocol

**Pattern 1: Explicit Resource Cleanup**
```python
import gc
import asyncio

async def force_close_db():
    """Ensure database handles are released"""
    gc.collect()  # Force garbage collection
    await asyncio.sleep(1.0)  # Give OS time to release handles

# Usage:
async with aiosqlite.connect(db_path) as db:
    await db.execute("PRAGMA journal_mode=DELETE")  # Disable WAL
    await db.commit()

del db  # Explicit deletion of local variable
await force_close_db()  # Now safe to delete file
```

**Pattern 2: Retry with Exponential Backoff**
```python
import time

max_retries = 5
for attempt in range(max_retries):
    try:
        if path.exists():
            path.unlink()
        shutil.move(str(temp_path), str(path))
        break  # Success
    except OSError:
        if attempt == max_retries - 1:
            raise  # Give up after 5 attempts
        time.sleep(0.5 * (attempt + 1))  # Exponential backoff
```

**Pattern 3: Journal Mode Control**
```python
# For tests: Use DELETE mode instead of WAL
async with aiosqlite.connect(db_path) as db:
    await db.execute("PRAGMA journal_mode=DELETE")
    # No .db-shm or .db-wal files created
```

### Artifacts
- **Implementation:** `src/core/services/backup.py` (lines 223-238)
- **Tests:** `tests/security/test_backup.py` (force_close_db helper)
- **Documentation:** Engineering Playbook Rule #17

### Lessons Learned
1. **Windows ≠ Unix:** Never assume POSIX behavior on Windows
2. **Explicit > Implicit:** Don't rely on Python GC for critical resource cleanup
3. **Retry is Resilient:** File operations should always have retry logic
4. **Test on Target Platform:** Linux tests passing doesn't mean Windows works

---

## 🔐 INCIDENT 2: The Libsodium API Hallucination

**Date:** Sprint 4, Task 4.4 (KMS Implementation)  
**Severity:** CRITICAL - Runtime crashes in production crypto code  
**Related Rule:** Engineering Playbook Rule #18 (Libsodium API Protocol)

### Symptom
```python
TypeError: crypto_secretstream_xchacha20poly1305_init_push() 
missing 1 required positional argument: 'key'
```

AI-generated code calling libsodium bindings with incorrect signatures.

### Context
- **Library:** PyNaCl (Python bindings for libsodium)
- **Operation:** SecretStream encryption initialization
- **Source:** AI code generation (multiple models made same mistake)

### Root Cause Analysis

**The Confusion:**
AI models confuse **high-level** PyNaCl API with **low-level** C bindings.

**High-Level API (Python-friendly):**
```python
from nacl.secret import SecretBox

# Automatic state management
box = SecretBox(key)
encrypted = box.encrypt(plaintext)
```

**Low-Level Bindings (C FFI):**
```python
import nacl.bindings

# Manual state allocation required
state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, key)
```

**Why AI hallucinates:**
1. Training data mixes high-level and low-level examples
2. C API documentation shows different signatures than Python bindings
3. Function names are similar but behavior differs

### Solution: The Libsodium API Protocol

**Verified Pattern for Encryption (Push):**
```python
import nacl.bindings
import nacl.utils

# ❌ HALLUCINATED (WRONG)
state, header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(key)

# ✅ CORRECT (VERIFIED)
# Step 1: Allocate state structure
state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()

# Step 2: Initialize with state and key
header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, key)

# Step 3: Encrypt chunks
encrypted = nacl.bindings.crypto_secretstream_xchacha20poly1305_push(
    state, 
    plaintext_chunk,
    tag=nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE
)
```

**Verified Pattern for Decryption (Pull):**
```python
# ❌ HALLUCINATED (WRONG)
state = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_pull(header, key)

# ✅ CORRECT (VERIFIED)
# Step 1: Allocate state structure
state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()

# Step 2: Initialize with state, header, and key
nacl.bindings.crypto_secretstream_xchacha20poly1305_init_pull(state, header, key)

# Step 3: Decrypt chunks
decrypted, tag = nacl.bindings.crypto_secretstream_xchacha20poly1305_pull(state, ciphertext_chunk)
```

### Verification Protocol

**Before committing any libsodium code:**
```bash
# Verify API signature
python -c "
import nacl.bindings
help(nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push)
"

# Expected output:
# init_push(state, key)
#     Initialize a crypto_secretstream_xchacha20poly1305 encryption state
#     
#     :param state: a crypto_secretstream_xchacha20poly1305_state object
#     :param key: must be exactly crypto_secretstream_xchacha20poly1305_KEYBYTES bytes
#     :return: header bytes
```

### Artifacts
- **Implementation:** `src/core/services/backup.py` (lines 117-118, 189-191)
- **Tests:** `tests/security/test_backup.py`
- **Documentation:** Engineering Playbook Rule #18

### Lessons Learned
1. **Never Trust AI-Generated Crypto Code:** Always verify against official docs
2. **Low-Level APIs Need Manual Memory Management:** C bindings require explicit state allocation
3. **Verification is Mandatory:** Use `help()` to check function signatures
4. **Document Correct Patterns:** Create reference implementations for team

---

## ☢️ INCIDENT 3: The Toxic Waste Protocol

**Date:** Sprint 5, Task 5.2 (Backup Service)  
**Severity:** MEDIUM - Security/Privacy risk  
**Related Rule:** Engineering Playbook Rule #19 (Toxic Waste Disposal)

### Symptom
Plaintext temporary database files left on disk after backup operations, recoverable with forensic tools.

### Context
- **Operation:** `VACUUM INTO` creates temporary plaintext database snapshot
- **Risk:** Sensitive user data exposed in temp files
- **Threat:** Physical access, forensic recovery, cloud backup sync

### Root Cause Analysis

**The Problem with `os.unlink()`:**
```python
# Standard deletion
temp_file.unlink()  # Only removes directory entry!
```

**What actually happens:**
1. File system removes directory pointer
2. Data blocks remain on disk until overwritten
3. File recovery tools (PhotoRec, TestDisk) can restore deleted files
4. Metadata (filename, timestamps) persists in filesystem journals

**Threat Model:**
- **Physical Access:** Attacker gains access to user's machine
- **Forensic Recovery:** Deleted files recovered using standard tools
- **Cloud Backup:** Temp files synced to cloud before deletion
- **Malware:** Ransomware scans for recently deleted sensitive files

### Solution: Secure File Wiping

**Pattern: 1-Pass Overwrite + Rename + Delete**
```python
import os
import uuid
from pathlib import Path

def secure_wipe_file(path: Path) -> None:
    """
    Secure file deletion with 1-pass overwrite (SSD-optimized)
    
    Process:
    1. Overwrite file content with random data
    2. Flush to disk (bypass OS cache)
    3. Rename to random UUID (obfuscate metadata)
    4. Delete renamed file
    """
    if not path.exists():
        return
    
    try:
        # Step 1: Overwrite with random data
        file_size = path.stat().st_size
        with open(path, "rb+") as f:
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())  # Force write to disk
        
        # Step 2: Obfuscate filename
        temp_name = path.parent / f"{uuid.uuid4()}.tmp"
        path.rename(temp_name)
        
        # Step 3: Delete
        temp_name.unlink()
        
    except (OSError, IOError):
        # Fallback: Delete without overwrite (best effort)
        try:
            path.unlink()
        except OSError:
            pass
```

**Why 1-Pass is Sufficient:**

**For Modern SSDs:**
- Wear leveling makes multi-pass overwriting ineffective
- Single overwrite is cryptographically sufficient
- Trim/garbage collection handles physical erasure

**Standards Compliance:**
- NIST SP 800-88 Rev. 1: "Clear" method (single overwrite)
- DoD 5220.22-M superseded by NIST guidelines

### Usage Pattern

```python
async def create_backup(db_path, passkey, output_path):
    temp_db_path = temp_dir / f"snapshot_{uuid.uuid4()}.db"
    
    try:
        # Create atomic snapshot (plaintext - TOXIC!)
        await loop.run_in_executor(None, _execute_vacuum_into, db_path, temp_db_path)
        
        # Encrypt snapshot
        encrypt_file(temp_db_path, output_path, passkey)
        
    finally:
        # CRITICAL: Secure wipe plaintext temporary file
        if temp_db_path.exists():
            secure_wipe_file(temp_db_path)  # MANDATORY
```

### Artifacts
- **Implementation:** `src/core/services/backup.py` (lines 69-82, 158)
- **Tests:** Verified in backup test suite
- **Documentation:** Engineering Playbook Rule #19

### Lessons Learned
1. **Temporary = Toxic:** All temp files with sensitive data need secure disposal
2. **Defense in Depth:** Even encrypted backups should wipe temp files
3. **SSD-Aware:** 1-pass is sufficient for modern storage
4. **Always in Finally:** Secure wipe must run even if operation fails

---

## ⚛️ INCIDENT 4: The Atomic Snapshot Protocol

**Date:** Sprint 5, Task 5.2 (Backup Service)  
**Severity:** MEDIUM - Data consistency risk  
**Related Rule:** Engineering Playbook Rule #20 (Atomic Snapshot)

### Problem
Standard SQLite backup methods (`BACKUP API`, manual `COPY`) can create inconsistent snapshots if database is being written to during backup.

### Context
- **Operation:** Creating backup of live database
- **Risk:** Backup contains partial transactions or inconsistent state
- **Requirement:** Point-in-time consistency guarantee

### Solution: VACUUM INTO

**Pattern:**
```python
def _execute_vacuum_into(source_db: Path, target_db: Path) -> None:
    """Execute VACUUM INTO synchronously"""
    source_uri = f"file:{source_db.resolve()}?mode=ro"
    target_path = str(target_db.resolve())
    
    with sqlite3.connect(source_uri, uri=True) as conn:
        conn.execute(f"VACUUM INTO '{target_path}'")
```

**Why VACUUM INTO:**
1. **Atomic:** Creates consistent point-in-time snapshot
2. **Read-Only:** Opens source in read-only mode (no locks)
3. **Compact:** Removes deleted data and optimizes layout
4. **Safe:** No risk of partial writes or corruption

**Async Integration:**
```python
async def create_backup(db_path, passkey, output_path):
    loop = asyncio.get_running_loop()
    
    # Run blocking VACUUM in executor
    await loop.run_in_executor(None, _execute_vacuum_into, db_path, temp_path)
```

### Artifacts
- **Implementation:** `src/core/services/backup.py` (lines 84-91, 110)
- **Documentation:** Engineering Playbook Rule #20

### Lessons Learned
1. **Atomic Over Everything:** Database operations must maintain consistency
2. **Use Built-in Atomicity:** SQLite provides `VACUUM INTO` for this purpose
3. **Executor for Blocking:** Run synchronous DB operations in thread pool

---

## 📊 Summary Table

| Incident | Rule | Severity | Key Lesson |
|----------|------|----------|------------|
| Windows File Locking | #17 | HIGH | Explicit resource cleanup + retry logic |
| Libsodium Hallucination | #18 | CRITICAL | Always verify AI-generated crypto code |
| Toxic Waste | #19 | MEDIUM | Secure wipe all temporary sensitive files |
| Atomic Snapshot | #20 | MEDIUM | Use VACUUM INTO for consistent backups |

---

## 🔮 Future Incidents

*This section will be updated as new critical failures occur and are resolved.*

**Template for new incidents:**
```markdown
## 🔥 INCIDENT X: [Title]

**Date:** [Sprint X, Task X.Y]
**Severity:** [LOW/MEDIUM/HIGH/CRITICAL]
**Related Rule:** [Playbook Rule #X]

### Symptom
[Error message or observable behavior]

### Context
[When/where/how it occurred]

### Root Cause Analysis
[Technical explanation]

### Solution
[Pattern/protocol that fixed it]

### Artifacts
[Where to find implementation]

### Lessons Learned
[Key takeaways]
```

---

*"Those who cannot remember the past are condemned to repeat it." - George Santayana*

*Last Updated: 2025-11-29 (Sprint 5, Task 5.2 completion)*

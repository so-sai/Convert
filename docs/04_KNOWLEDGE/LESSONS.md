# 🧠 CONVERT LESSONS — The "Why" Behind the Rules

> **Navigation:** [MDS](../01_ARCHITECTURE/MDS_v3.14_Pi.md) | [Playbook](../05_OPERATIONS/PLAYBOOK.md) | [Security](../05_OPERATIONS/SECURITY_POLICY.md) | [Lessons](LESSONS.md) | [Dictionary](DATA_DICTIONARY.md)

---

> **Purpose:** Post-mortem analysis + patterns that shaped our architecture
> **Warning:** Read this before removing "weird" code (especially `gc.collect()` or retry loops)
> **Status:** Living document - updated after each major incident
> **Last Updated:** 2025-12-06

---

## 📖 Table of Contents

1. [The 7 Core Lessons](#-the-7-core-lessons)
2. [Incident Reports](#-incident-reports)
3. [Quick Reference Patterns](#-quick-reference-patterns)
4. [Eternal Rules](#-eternal-rules)

---

## 🔥 THE 7 CORE LESSONS

### 1. Windows ≠ Unix

Windows maintains file locks longer than Unix. This causes `[WinError 32]` errors.

```python
# WRONG (Unix mindset)
with open('temp.db', 'w') as f:
    f.write(data)
os.remove('temp.db')  # Fails on Windows!

# RIGHT (Windows-aware)
conn.close()
del conn
gc.collect()
await asyncio.sleep(1)
os.remove('temp.db')  # Works
```

**Rule #17:** All file operations must implement retry with exponential backoff.

---

### 2. Tauri v2 Breaks Expectations

Tauri v2 CLI only searches subfolders for config, never parent folders.

```bash
# WRONG
cd src-ui
npx tauri dev  # Fails: "not a Tauri project"

# RIGHT
cd src-ui
npx tauri dev --config ../src-tauri/tauri.conf.json
```

---

### 3. Filesystem = Truth (Omega Protocol)

When SQLite APIs fail, trust filesystem metadata for progress:

```rust
let total = fs::metadata(&src).len();
let current = fs::metadata(&dst).len();
let progress = (current as f64 / total as f64).min(0.999) * 100.0;
```

---

### 4. Progress is Communication, Not Measurement

- Show ETA as **range**: "12-18s remaining"
- Never show exact numbers that will be wrong
- Heartbeat every 2-5 seconds to show app is alive

---

### 5. Zeroize is a Process

```rust
impl Drop for SecretHolder {
    fn drop(&mut self) {
        self.data.zeroize();
        std::sync::atomic::compiler_fence(Ordering::SeqCst);
    }
}
```

On Windows, use `VirtualLock` to prevent paging.

---

### 6. Monorepo Boundaries are Physical

```
src-tauri/     # Rust only (security)
src/core/      # Python only (business logic)
src-ui/        # Svelte only (UI)
```

If code doesn't fit these directories, architecture needs review.

---

### 7. AI Needs Multiple Witnesses (Tri-Check)

1. **EXECUTION** (DeepSeek): Draft code
2. **CONTEXT CHECK** (Gemini): Verify against codebase
3. **APPROVAL** (Claude): Security review

**Rule #18:** Never implement crypto from single AI without signature verification.

---

## 🔥 INCIDENT REPORTS

### INCIDENT 1: Windows File Locking Disaster

**Sprint:** 5, Task 5.2 | **Severity:** HIGH | **Rule:** #17

**Symptom:**
```
[WinError 32] The process cannot access the file
```

**Root Cause:**
- SQLite WAL files persist locks
- Python GC latency
- Windows exclusive locks

**Solution:**
```python
async def force_close_db():
    gc.collect()
    await asyncio.sleep(1.0)
```

---

### INCIDENT 2: Libsodium API Hallucination

**Sprint:** 4, Task 4.4 | **Severity:** CRITICAL | **Rule:** #18

**Symptom:**
```python
TypeError: missing 1 required positional argument: 'key'
```

**Root Cause:** AI confuses high-level PyNaCl with low-level C bindings.

**Solution:**
```python
# ❌ WRONG (hallucinated)
state, header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(key)

# ✅ RIGHT (verified)
state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, key)
```

**Verification:**
```bash
python -c "import nacl.bindings; help(nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push)"
```

---

### INCIDENT 3: Toxic Waste Protocol

**Sprint:** 5, Task 5.2 | **Severity:** MEDIUM | **Rule:** #19

**Problem:** `os.unlink()` doesn't actually erase data - forensic recovery possible.

**Solution:**
```python
def secure_wipe_file(path: Path) -> None:
    # 1. Overwrite with random
    with open(path, "rb+") as f:
        f.write(os.urandom(path.stat().st_size))
        f.flush()
        os.fsync(f.fileno())
    
    # 2. Rename to random UUID
    temp_name = path.parent / f"{uuid.uuid4()}.tmp"
    path.rename(temp_name)
    
    # 3. Delete
    temp_name.unlink()
```

---

### INCIDENT 4: Atomic Snapshot Protocol

**Sprint:** 5, Task 5.2 | **Severity:** MEDIUM | **Rule:** #20

**Problem:** Copying live SQLite files creates inconsistent backups.

**Solution:**
```python
def _execute_vacuum_into(source_db: Path, target_db: Path):
    source_uri = f"file:{source_db.resolve()}?mode=ro"
    with sqlite3.connect(source_uri, uri=True) as conn:
        conn.execute(f"VACUUM INTO '{target_db}'")
```

---

## 📊 Quick Reference Patterns

### Windows File Operations
```python
max_retries = 5
for attempt in range(max_retries):
    try:
        shutil.move(str(src), str(dst))
        break
    except OSError:
        if attempt == max_retries - 1: raise
        time.sleep(0.5 * (attempt + 1))
```

### Database Cleanup
```python
async with aiosqlite.connect(db_path) as db:
    await db.execute("PRAGMA journal_mode=DELETE")
    await db.commit()
del db
gc.collect()
await asyncio.sleep(1.0)
```

### Backup Progress
```rust
let ema_speed = (instant * 0.3) + (previous * 0.7);
let eta_min = remaining / (mean + 2.0 * std_dev);
let eta_max = remaining / (mean - std_dev).max(0.1);
```

---

## ⚡ ETERNAL RULES

| # | Rule | Mandate |
|---|------|---------|
| 1 | Windows Integrity | NO CLI one-liners for file writing |
| 2 | Async All I/O | Use `run_in_executor` for blocking ops |
| 3 | Salt = 16 bytes | `os.urandom(16)` for Argon2id |
| 4 | Docs = Truth | Code follows Docs, never vice versa |
| 17 | Windows Persistence | Retry + `gc.collect()` always |
| 18 | Libsodium Verify | Check `help()` before commit |
| 19 | Toxic Waste | Secure wipe all temp files |
| 20 | Atomic DB | Use `VACUUM INTO` for backups |
| 21 | Signature Align | Read test files before implementing |

---

## 📊 Incident Summary

| Incident | Rule | Severity | Key Lesson |
|----------|------|----------|------------|
| Windows File Locking | #17 | HIGH | `gc.collect()` + retry |
| Libsodium Hallucination | #18 | CRITICAL | Verify AI crypto code |
| Toxic Waste | #19 | MEDIUM | Secure wipe temp files |
| Atomic Snapshot | #20 | MEDIUM | Use `VACUUM INTO` |

---

*"Those who cannot remember the past are condemned to repeat it." — George Santayana*

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

### INCIDENT 5: Phantom API (sqlite3_backup_pagecount)

**Sprint:** 5, Task 5.1 | **Severity:** HIGH | **Rule:** #3 (Omega Protocol)

**Symptom:**
```
error: linking with `link.exe` failed
undefined reference to `sqlite3_backup_pagecount`
```

**Root Cause:**
- Attempted to use `sqlite3_backup_pagecount` API on Windows
- API exists in documentation but not in Windows SQLite builds
- Wasted 3 days debugging compilation errors

**Solution (Omega Protocol):**
```rust
// ❌ WRONG (Phantom API)
let total_pages = unsafe { sqlite3_backup_pagecount(backup) };

// ✅ RIGHT (Filesystem as Truth)
let total = fs::metadata(&src_path)?.len();
let current = fs::metadata(&dst_path)?.len();
let progress = (current as f64 / total as f64).min(0.999) * 100.0;
```

**Lesson:** When in doubt about C/C++ APIs, use OS filesystem as source of truth.

---

### INCIDENT 6: Lost in Monorepo (Cross-Directory Command)

**Sprint:** 5, Task 5.2 | **Severity:** MEDIUM | **Rule:** #6 (Monorepo Boundaries)

**Symptom:**
```
Error: Couldn't recognize the current folder as a Tauri project
```

**Root Cause:**
- Standing at project root or `src-ui` and running `tauri dev`
- Tauri v2 requires config file in current or child directories
- Monorepo structure confuses CLI path resolution

**Solution:**
```bash
# ❌ WRONG (from root)
cd E:\DEV\Convert
npx tauri dev

# ❌ WRONG (from src-ui without config)
cd src-ui
npx tauri dev

# ✅ RIGHT (Cross-Directory Command)
cd src-ui
npx tauri dev --config ../src-tauri/tauri.conf.json
```

**Lesson:** Stand at Backend (src-tauri) to satisfy config, but borrow tools from Frontend (../src-ui/node_modules/.bin/tauri).

---

### INCIDENT 7: Environmental Hazard (Missing C++ Build Tools)

**Sprint:** 5, Task 5.1 | **Severity:** CRITICAL | **Rule:** New Rule #23

**Symptom:**
```
error: linker `link.exe` not found
note: program not found
```

**Root Cause:**
- Missing Visual Studio C++ Build Tools
- Missing Windows SDK
- Rust cannot link native dependencies

**Solution:**
```powershell
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# Required workloads:
- Desktop development with C++
- Windows 10/11 SDK
```

**Verification:**
```bash
rustc --version
cargo build --release
```

**Lesson:** Windows Rust development requires full C++ toolchain. Document in setup guide.

---

### INCIDENT 8: Concurrency Chaos (Test Thread Conflicts)

**Sprint:** 5, Task 5.2 | **Severity:** MEDIUM | **Rule:** New Rule #24

**Symptom:**
```
[WinError 32] The process cannot access the file because it is being used by another process
```

**Root Cause:**
- `cargo test` runs tests in parallel by default
- Multiple tests accessing same SQLite database simultaneously
- Windows file locking prevents concurrent access

**Solution:**
```bash
# ❌ WRONG (parallel tests)
cargo test

# ✅ RIGHT (sequential tests)
cargo test -- --test-threads=1
```

**Permanent Fix:**
```toml
# .cargo/config.toml
[test]
threads = 1
```

**Lesson:** All Windows tests MUST run sequentially. Add to CI/CD pipeline.

---

### INCIDENT 9: Git Hygiene Disaster (Paste Corruption)

**Sprint:** 5, Task 5.1 | **Severity:** LOW | **Rule:** New Rule #25

**Symptom:**
- `.gitignore` file corrupted with invisible characters
- Committed large database files (>100MB)
- Committed system junk files (`.DS_Store`, `Thumbs.db`)

**Root Cause:**
- Pasting terminal commands into `.gitignore` caused encoding issues
- Loose `.gitignore` patterns missed critical files
- Manual file editing error-prone

**Solution:**
```python
# Use Python script for config files (safer than manual paste)
def update_gitignore(patterns: list[str]):
    gitignore_path = Path(".gitignore")
    existing = gitignore_path.read_text().splitlines()
    new_patterns = [p for p in patterns if p not in existing]
    
    with gitignore_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(new_patterns) + "\n")
```

**Strict `.gitignore`:**
```gitignore
# Database files
*.db
*.db-shm
*.db-wal
*.sqlite
*.sqlite3

# Backup files
*.cvbak
*.bak

# System junk
.DS_Store
Thumbs.db
desktop.ini
```

**Lesson:** Use Python scripts for config file updates. Never paste multi-line content directly into files.

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
| 23 | C++ Toolchain | Windows Rust requires VS Build Tools |
| 24 | Sequential Tests | `cargo test -- --test-threads=1` on Windows |
| 25 | Config Scripts | Use Python for file updates, not paste |

---

## 📊 Incident Summary

| Incident | Rule | Severity | Key Lesson |
|----------|------|----------|------------|
| Windows File Locking | #17 | HIGH | `gc.collect()` + retry |
| Libsodium Hallucination | #18 | CRITICAL | Verify AI crypto code |
| Toxic Waste | #19 | MEDIUM | Secure wipe temp files |
| Atomic Snapshot | #20 | MEDIUM | Use `VACUUM INTO` |
| Phantom API | #3 | HIGH | Filesystem as truth |
| Lost in Monorepo | #6 | MEDIUM | Cross-directory commands |
| Environmental Hazard | #23 | CRITICAL | Install VS Build Tools |
| Concurrency Chaos | #24 | MEDIUM | Sequential tests only |
| Git Hygiene | #25 | LOW | Python scripts for configs |

---

*"Those who cannot remember the past are condemned to repeat it." — George Santayana*

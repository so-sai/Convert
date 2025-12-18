# 🏛️ CONVERT PLAYBOOK — The Engineering Protocol

> **Navigation:** [MDS](../01_ARCHITECTURE/MDS_v3.14_Pi.md) | [Playbook](PLAYBOOK.md) | [Security](SECURITY_POLICY.md) | [Lessons](../04_KNOWLEDGE/LESSONS.md) | [Dictionary](../04_KNOWLEDGE/DATA_DICTIONARY.md)

---

> **Status:** ENFORCED
> **Context:** Windows 11 / Python 3.14 / Rust Tauri v2
> **Last Updated:** 2025-12-06

---

## 1. THE IRON RULES (IMMUTABLE)

| # | Rule | Mandate |
|---|------|---------|
| 1 | Monorepo Law | `src/core` = Python, `src-tauri` = Rust. No `sprint-xx` folders. |
| 2 | Windows Execution | Always `python -m <module>`. Never `pip install` directly. |
| 3 | Anti-Buffer Overflow | No paste >10 lines into terminal. Use Python scripts. |
| 4 | Zero-Trust UI | Frontend is blind. Never send raw secrets to UI. |

---

## 2. CODING STANDARDS

### Rule #17: Windows Persistence
```python
# ALL file operations must have retry logic
max_retries = 5
for attempt in range(max_retries):
    try:
        shutil.move(str(src), str(dst))
        break
    except OSError:
        if attempt == max_retries - 1: raise
        gc.collect()
        time.sleep(0.5 * (attempt + 1))
```

### Rule #18: Libsodium Integrity
Before committing any crypto code:
```bash
python -c "import nacl.bindings; help(nacl.bindings.<function_name>)"
```

### Rule #19: Toxic Waste Disposal
Sensitive temp files must be securely wiped:
```python
secure_wipe_file(temp_path)  # overwrite -> rename -> delete
```

### Rule #20: Atomic Operations
Database backups must use `VACUUM INTO`:
```python
conn.execute(f"VACUUM INTO '{target_path}'")
```

### Rule #21: Signature Alignment
Before implementing, read the test file to ensure:
1. Function names match
2. Arguments match

### Rule #22: Naming Sanctity (Tên Bất Khả Xâm Phạm)
| Term | Status | Usage |
|------|--------|-------|
| **Convert** | ✅ OFFICIAL | Product name. The ONLY acceptable product name. |
| **Convert Protocol** | ⚠️ ALLOWED | Feature branding in UI headers/console logs. |
| **Vault** | ❌ BLACKLISTED | Do NOT use as product name suffix. Use only as technical term (e.g., "vault unlock"). |
| **Omega Protocol** | ❌ BLACKLISTED | Do NOT use as product/feature name. Use "Backup Protocol" instead. |

### Rule #24: Artifact-First Protocol (The "Vibe" Rule)
1. **Planning Mode:** When facing complexity, switch to Planning Mode.
2. **Visualize:** Create an Artifact (Mermaid/Checklist) before coding.
3. **Async Feedback:** Wait for User approval on the Artifact.
4. **Execution:** Only write code after Artifact is approved.

### Rule #25: The Bleeding Edge Protocol (Python/Rust Compatibility)
**Context:** When project uses a Python version newer than PyO3's maximum supported version.
**Anti-Pattern:**
- ❌ NEVER downgrade Python
- ❌ NEVER wait for library updates
**Solution (The ABI Bridge):**
- ✅ Use **Stable ABI (`abi3`)** feature in PyO3
- ✅ Configure Rust to compile with nearest stable version (e.g., `abi3-py312`)
- ✅ Python 3.14+ automatically compatible with 3.12 ABI
**Philosophy:** "Core vững (Rust) thì chấp Interface cũ, nhưng Brain (Python) phải luôn mới nhất."
```toml
pyo3 = { version = "0.22", features = ["auto-initialize", "abi3-py312"] }
```

### Rule #26: Context Preservation (Anti-Blind Overwrite)
**Problem:** Agent overwrites entire file, losing existing functionality
**Anti-Pattern:**
- ❌ Generate new file without reading current state
- ❌ Copy-paste examples that lack full context
- ❌ "Fix logic" by deleting UI components
**Solution:**
- ✅ ALWAYS read full file before editing (use `view_file`)
- ✅ Use targeted patches (change only what's needed)
- ✅ Verify artifact merge includes ALL previous features
**Example (Sprint 5 Mistake):**
```svelte
// ❌ WRONG: Overwrote App.svelte with only DropZone
<DropZone /> <!-- Lost: 3 cards, theme toggle, sidebar -->

// ✅ RIGHT: Preserved all components
<Sidebar />
<ThemeToggle />
<Cards />
<DropZone /> <!-- Added without removing others -->
```

### Rule #27: The Admin Trap (Windows UIPI)
**Problem:** Drag & Drop fails silently when app runs as Administrator
**Root Cause:** Windows User Interface Privilege Isolation (UIPI)
- Explorer runs at Medium Integrity (User level)
- Admin terminal runs at High Integrity
- Windows blocks Medium → High event flow (security feature)
**Detection:**
```bash
whoami /groups | findstr "S-1-16-12288"  # High Mandatory Level = Admin
```
**Solution:**
- ✅ ALWAYS run dev server as normal user (not Admin)
- ✅ Add to setup docs: "Close Admin terminals before `cargo tauri dev`"
- ✅ If drag events don't fire: check integrity level FIRST, not code
**Why it's silent:** Tauri receives no error - OS simply doesn't deliver the event

### Rule #28: Configuration Version Awareness
**Problem:** Using deprecated config from older framework version
**Sprint 5 Examples:**
- Tauri v1: `fileDropEnabled` → Tauri v2: `dragDropEnabled` + capabilities
- Missing `capabilities/default.json` → Events silently blocked
**Solution:**
- ✅ Check framework version in `Cargo.toml` / `package.json`
- ✅ Read migration guide when upgrading major versions
- ✅ Use schema validation: `$schema` in config files
```json
// Tauri v2 requires capabilities system
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "permissions": ["core:window:default", "core:event:allow-listen"]
}
```

---

## 3. THE TRI-CHECK PROTOCOL

All critical features pass through 3 phases:

| Phase | Agent | Focus |
|-------|-------|-------|
| 1. EXECUTION | DeepSeek | Draft code, logic |
| 2. CONTEXT | Gemini | Verify imports, paths |
| 3. APPROVAL | Claude | Security review |

---

---

## 4. VIBE CODING MENTAL MODEL
**"From Micro-management to Orchestration"**

### 1. Artifact as Communication Layer
- **Old (Chat):** Context is lost in the stream.
- **New (Artifact):** Artifact is the Anchor. Sếp and Agent discuss ON the Artifact.

### 2. Async Steering
- **Pain Point:** Watching CLI progress bars.
- **Solution:** Approve the Plan (Artifact) -> Agent executes blindly -> User reviews Result.

### 3. Workflow Orchestration
- Workflows trigger each other (Planning -> TDD -> Implementation -> Review).
- Antigravity is a pipeline, not just a coder.

---

## 5. GIT WORKFLOW (SOLO LEVELING)

### Branch Strategy
```bash
git checkout -b feat/backup-logic
# or
git checkout -b fix/icon-error
```

### Atomic Commits
```bash
# ❌ WRONG
git commit -m "Update code"

# ✅ RIGHT
git commit -m "feat(core): add backup function"
git commit -m "feat(ui): add backup button"
```

### Trinity Test (Before Merge)
```bash
# 1. Python
python -m pytest tests/ -v

# 2. Rust
cd src-tauri && cargo check

# 3. Frontend
cd src-ui && npm run check
```

### Fast Track Merge
```bash
git checkout main
git pull origin main
git merge feat/backup-logic
git push origin main
git branch -d feat/backup-logic
```

---

## 5. VERIFICATION CHECKLIST

### Pre-Commit
- [ ] `python -m py_compile <file>` (syntax check)
- [ ] `python -m pytest` (100% green)
- [ ] `git status` (no junk files)

### Pre-Release
- [ ] All tests pass on Windows
- [ ] File retry logic tested
- [ ] Memory zeroization verified
- [ ] Backup creates `.cvbak` (not `.db`)
- [ ] Progress events fire 80-200ms
- [ ] ETA shows range

---

## 6. DECISION POLICY

Record an ADR when ANY are true:

1. **Architectural Impact** - Affects system design
2. **Dependency Addition** - New library added
3. **Trade-off Made** - Non-trivial decision
4. **Precedent Setting** - Pattern for future

All ADRs must include:
- Rationale (min 20 chars)
- At least 1 alternative considered
- Impact level (low/medium/high)

---

## 7. DIRECTORY STRUCTURE

```
E:/DEV/Convert/
├── docs/                     # Documentation (you are here)
├── scripts/                  # DevOps tools
├── src/core/                 # Python backend
├── src-tauri/                # Rust security core
├── src-ui/                   # Svelte frontend
└── tests/                    # Test suites
```

---

## 8. QUICK COMMANDS

```bash
# Launch Dev
cd src-ui && npx tauri dev --config ../src-tauri/tauri.conf.json

# Run Tests
python -m pytest tests/ -v
cd src-tauri && cargo test -- --test-threads=1

# Build Release
cd src-ui && npx tauri build
```

---

→ See [LESSONS.md](../04_KNOWLEDGE/LESSONS.md) for why these rules exist.
→ See [SECURITY_POLICY.md](SECURITY_POLICY.md) for crypto standards.

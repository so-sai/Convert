# PR CHECKLIST: TASK 5.3 HYBRID SSOT IMPLEMENTATION

**Branch:** `feat/task-5.3-hybrid-ssot`  
**Base:** `main`  
**Ref:** SPEC_TASK_5_3_INTEGRATED.md

---

## 🔴 PHASE 1: PYTHON CORE (SSOT) — Priority HIGH

### 1.1 Create Dispatcher
- [ ] `src/core/services/__init__.py`
- [ ] `src/core/services/dispatcher.py` — `run(service, envelope)`
- [ ] `src/core/services/session.py` — Token & replay management

### 1.2 Create Backup Service
- [ ] `src/core/services/backup.py` — `start_backup()`, progress callback
- [ ] Implement replay window (in-memory dict with TTL)

### 1.3 Tests
- [ ] `tests/test_dispatcher.py`
- [ ] `tests/test_replay_window.py`
- [ ] `tests/test_ephemeral_token.py`

---

## 🟡 PHASE 2: RUST SHELL — Priority MEDIUM

### 2.1 Refactor Commands
- [ ] Create `src-tauri/src/commands/shell.rs`
- [ ] Implement `cmd_dispatch()` — parse envelope, call Python
- [ ] Implement `cmd_request_token()` — forward to Python
- [ ] Remove business logic from `backup.rs` → keep only crypto

### 2.2 PyO3/Sidecar Bridge
- [ ] Choose: PyO3 embed OR subprocess sidecar
- [ ] Implement `python_call(service, payload) -> Result<String>`
- [ ] Add error mapping to canonical categories

### 2.3 Tests
- [ ] `src-tauri/tests/test_shell.rs`
- [ ] `src-tauri/tests/test_bridge.rs`

---

## 🟢 PHASE 3: FRONTEND — Priority LOW (after Phase 1-2)

### 3.1 Envelope Utils
- [ ] `src-ui/src/lib/utils/envelope.ts` — nonce gen, envelope builder
- [ ] `src-ui/src/lib/utils/crypto.ts` — Web Crypto CSPRNG wrapper

### 3.2 Components
- [ ] `RecoveryViewer.svelte` — blur/press-hold/TTL
- [ ] `DropZone.svelte` — drag-and-drop
- [ ] `ToastNotification.svelte` — notification system

### 3.3 Stores
- [ ] Update `backup.ts` — use envelope pattern
- [ ] Create `session.ts` — ephemeral token management

### 3.4 Tests
- [ ] `src-ui/tests/envelope.test.ts`
- [ ] E2E: Playwright test for backup flow

---

## ✅ MERGE CRITERIA

- [ ] All Python tests pass (`python -m pytest tests/ -v`)
- [ ] All Rust tests pass (`cargo test`)
- [ ] Frontend builds without errors (`npm run check`)
- [ ] Security tests pass (replay attack, expired token)
- [ ] Code review: No business logic in Rust
- [ ] SPEC compliance verified

---

## 📋 QUICK START (for developers)

```bash
# 1. Create branch
git checkout -b feat/task-5.3-hybrid-ssot

# 2. Phase 1: Python
mkdir -p src/core/services
# ... implement dispatcher ...
python -m pytest tests/ -v

# 3. Phase 2: Rust
cd src-tauri
# ... refactor commands ...
cargo test

# 4. Phase 3: Frontend
cd src-ui
# ... implement components ...
npm run check

# 5. Submit PR
git push origin feat/task-5.3-hybrid-ssot
```

---

**Owner:** @WORKER  
**Reviewer:** @REVIEWER  
**Deadline:** Sprint 5 closure

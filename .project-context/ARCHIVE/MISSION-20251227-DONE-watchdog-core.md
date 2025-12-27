# STATUS: ✅ DONE
# Completed: 2025-12-27T12:56:00+07:00

# MISSION: SPRINT 6 - TASK 6.1 - WATCHDOG CORE

## 1. CONTEXT
Hệ thống cần File Watcher thông minh để giám sát thư mục dữ liệu, xử lý vấn đề Spam Events và Zombie Threads.

## 2. SCOPE
**Files allowed:**
- `tests/services/test_watchdog.py` (New)
- `src/core/services/watchdog.py` (New)
- `scripts/init_watchdog_tdd.py` (New)

**Forbidden:**
- `src-ui/*`, `src-tauri/*`

## 3. TASKS
- [x] Run `scripts/init_watchdog_tdd.py` to create Test Skeleton.
- [x] Run `pytest` -> CONFIRM FAIL (Red).
- [x] Implement `WatchdogService` (Debounce, ThreadPool).
- [x] Run `pytest` -> CONFIRM PASS (Green).

## 4. ACCEPTANCE
- [x] All tests in `tests/services/test_watchdog.py` passed. (5/5 PASSED)
- [x] Dynamic pathing implemented (temp directory instead of hardcoded paths)

## 5. LESSONS LEARNED
- Git Bash uses Unix commands (`touch`) not Windows CMD (`type nul`)
- Python packages require `__init__.py` files for proper import resolution
- `PYTHONPATH=.` or `pytest.ini` with `pythonpath = .` needed for src imports
- Use `tempfile.mkdtemp()` instead of hardcoded paths for cross-platform compatibility
- `watchdog` library must be installed: `pip install watchdog`

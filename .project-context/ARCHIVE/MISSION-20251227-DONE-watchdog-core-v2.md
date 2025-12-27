# ARCHIVED: Task 6.1 - Watchdog Core
> **Status:** ✅ COMPLETE | **Date:** 2025-12-27 | **Commit:** 57e6d16

## Result: 22/22 TESTS PASSED (Military-Grade)

## Deliverables
| File | Description |
|------|-------------|
| `src/core/services/watchdog.py` | WatchdogService with debounce, UUID, safety valve |
| `tests/services/test_watchdog.py` | 22 tests (15 base + 7 torture) |
| `tests/services/conftest.py` | Test fixtures |
| `docs/03_SPECS/SPEC_TASK_6_1_EVENT_CONTRACT.md` | Frozen Contract 🧊 |

## Features
- [x] Debounce logic (configurable ms)
- [x] POSIX path normalization
- [x] UUID v4 batch tracking
- [x] Safety valve (max 5000 files)
- [x] Thread-safe operations
- [x] Graceful stop (no zombie threads)

## Dependencies Updated (Dec 2025)
- watchdog>=6.0.0
- pydantic>=2.10.0
- ruff>=0.8.0

## Lessons Learned
1. Python 3.14 Free-threading requires careful thread cleanup timing
2. Torture tests (rapid toggle) need 50ms+ sleep for OS context switch
3. Path normalization critical for Windows/POSIX compatibility

**Next:** Task 6.2 - EventBus

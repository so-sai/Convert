# Sprint 6 - Lessons Learned (Dec 2025)

> **Sprint:** Background Services Core | **Date:** 2025-12-27
> **Status:** 2/3 Tasks Complete (Task 6.3 Pending)

---

## 1. Technical Lessons

### 1.1 TDD Works - When Done Right
| Observation | Impact |
|-------------|--------|
| RED phase với 8 tests chạy trong 0.11s | Fast feedback loop |
| GREEN phase hoàn thành trong 1 session | Spec rõ = code nhanh |
| Stress test phát hiện bottleneck thật | Không tin benchmark, tin reality |

**Rule**: Spec → Test → Code → Stress Test → Adjust

---

### 1.2 Queue Sizing - Triết lý 0.1s
```
Publish speed (306K/s) >> Dispatch speed (10K/s)
Small queue (10K) → 89% drops
Large queue (200K) → 0% drops + order preserved
```

**Decision**: Trade memory (~50MB) for reliability (0% drops)

**Comment quan trọng đã thêm vào code:**
> "Queue size is intentionally oversized to absorb burst traffic and preserve instant feedback (<0.1s) for latest events."

---

### 1.3 Single Dispatcher > Multi-Dispatcher (cho file events)
| Multi-Dispatcher | Single Dispatcher |
|------------------|-------------------|
| Faster throughput | Order preserved ✅ |
| Race conditions possible | FIFO guaranteed ✅ |
| Complex debugging | Simple debugging ✅ |

**Lý do**: File events cần thứ tự (Create → Modify → Delete). Đảo thứ tự = BUG logic.

---

### 1.4 Python 3.14 No-GIL
- `ThreadPoolExecutor` hoạt động tốt
- `collections.deque` với `threading.Lock` không bị contention
- Stress test 100K events chạy ổn định

**Cảnh báo**: Rapid thread creation (T20 torture test) có thể gây deadlock. Cần thời gian cleanup giữa cycles.

---

## 2. Process Lessons

### 2.1 Reality Checks Trước Khi Celebrate
| Stage | What happened |
|-------|---------------|
| 8/8 tests passed | "Xong rồi!" |
| Stress test 100K | 89% drops - "Ủa sao?" |
| Queue 200K | 0% drops - "Xong thật!" |

**Rule**: Unit test pass ≠ Production ready. Chạy stress test luôn.

---

### 2.2 Commit Milestones
```
beb48cf - RED phase (8/8 fail)
3e84a73 - GREEN complete (8/8 pass)
2a0b54c - 200K queue fix (0% drops)
```

**Value**: Có thể revert về từng milestone nếu cần.

---

## 3. Architecture Decisions (ADR)

### ADR-007: EventBus Queue Size
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| 10K queue | Low memory | 89% drops | ❌ |
| 200K queue | 0% drops, 20s buffer | ~50MB memory | ✅ |
| Unbounded | Never drops | OOM risk | ❌ |

**Rationale**: Local app có đủ RAM. UX quan trọng hơn RAM.

### ADR-008: Single Dispatcher Architecture
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Multi-dispatcher | Higher throughput | Order loss | ❌ |
| Single dispatcher | Order preserved | 10K/s limit | ✅ |

**Rationale**: Indexer cần events đúng thứ tự. 10K/s >> realistic Watchdog load.

---

## 4. Dependencies Dec 2025

| Package | Version | Notes |
|---------|---------|-------|
| Python | 3.14.2 | Free-threading experimental |
| watchdog | 6.0.0 | File monitoring |
| ruff | 0.14.10 | Fast linter |
| pydantic | 2.10+ | Validation |
| pytest | 8.2+ | Testing |

---

## 5. Next: Task 6.3 Indexer Queue

### Expectations
- Subscribe to EventBus events
- SQLite persistent queue
- Batch processing (100-1000 events)
- Crash recovery

### Watch out for
- SQLite write lock contention
- Memory usage with large batches
- Order preservation from EventBus → SQLite

---

**END OF LESSONS LEARNED**

# CONTRACT: WATCHDOG EVENT STREAM

> **Ref:** SPEC_TASK_6_1_WATCHDOG_CORE | **Status:** 🧊 FROZEN | **Date:** 2025-12-27
> **Scope:** Defines strictly WHAT the Watchdog emits and WHEN.
> **Constraint:** No DB logic, No UI logic, Pure Infrastructure.

---

## 1. DATA STRUCTURE (THE ENVELOPE)

Watchdog **ONLY** emits a standardized `FileBatchEvent` object.

### 1.1 Payload Schema
```json
{
  "event_type": "BATCH_CHANGED",
  "batch_id": "uuid-v4-string",
  "timestamp": 1735281000.500,
  "source_path": "E:/DEV/app-desktop-Convert/content",
  "changes": {
    "created": ["note_01.md", "image_A.png"],
    "modified": ["draft_B.md"],
    "deleted": ["temp_Z.txt"]
  },
  "meta": {
    "debounce_ms": 300,
    "total_items": 4
  }
}
```

### 1.2 Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `batch_id` | UUID v4 | Tracing/Logging. Debug xem batch nào làm crash Worker. |
| `timestamp` | float epoch | Thời điểm emit với millisecond precision |
| `source_path` | string | Đường dẫn POSIX đã normalize |
| `changes` | object | Deduped + Normalized. Last-state-wins. |
| `meta.total_items` | int | Tổng số file trong batch |

---

## 2. TIMING & TRIGGERS (THE FLOODGATE)

### 2.1 Debounce Logic
- **Rule:** "Wait for silence".
- **Behavior:** Timer reset mỗi khi có raw event mới từ OS.
- **Trigger:** `last_raw_event_time + debounce_ms < current_time`

### 2.2 Configurable Parameters
- `debounce_ms`: Default 300ms (có thể tăng lên 1000ms cho máy yếu)
- `max_batch_size`: 5000 files. Vượt ngưỡng → force emit ngay.

---

## 3. ORDERING GUARANTEES

| Type | Guarantee | Note |
|------|-----------|------|
| **Intra-batch** | ❌ Không đảm bảo | Set-based, không phụ thuộc thứ tự |
| **Inter-batch** | ✅ Tuần tự (Sequential) | Batch N emit xong trước Batch N+1 |
| **Thread Safety** | ✅ Background thread | Không block Main Thread |

---

## 4. LIFECYCLE (THE KILL SWITCH)

### 4.1 Stop Protocol
`stop()` phải đảm bảo **idempotency** (gọi nhiều lần không lỗi):

| State | Action | Result |
|-------|--------|--------|
| **Debouncing** | Cancel Timer | Batch bị hủy (Drop) |
| **Emitting** | Wait callback | Batch cuối được gửi an toàn |
| **Idle** | Stop Observer | Clean shutdown |

---

## 5. CONSUMER EXPECTATIONS

- **Idempotency:** Consumer (Indexer) tự xử lý trùng lặp
- **File Existence:** Check `os.path.exists()` trước khi đọc
- **Decoupling:** Watchdog không biết về SQLite/Indexer

---

**END OF CONTRACT** 🧊

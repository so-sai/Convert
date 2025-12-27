# SPEC: INDEXER QUEUE CORE (TASK 6.3) - FINAL

> **Status:** 🧊 FROZEN | **Date:** 2025-12-27
> **Ref:** Task 6.3 | **Sprint:** 6 Background Services

---

## 1. CORE SEMANTICS

### 1.1 Purpose
Batch processing pipeline that bridges EventBus (real-time) to SQLite (persistent).

### 1.2 Delivery Guarantees
- **At-least-once**: Events persisted before acknowledgment
- **Strict FIFO**: Events processed in exact order received
- **Idempotency**: Duplicate events skipped via `processed_events` table
- **Crash-safe**: SQLite WAL mode, pending batches survive restart

### 1.3 Performance Targets
| Metric | Target |
|--------|--------|
| Throughput | 10,000 events/sec |
| Event-to-persist latency | < 0.1s |
| Memory (50K events) | < 50MB |
| Crash recovery time | < 2s |

---

## 2. ARCHITECTURE

```
[EventBus] → [IndexerQueue Buffer] → [SQLite pending_batches]
                    ↓                         ↓
            (100 events OR 500ms)      [processed_events]
                                              ↓
                                    [get_next_batch() → Indexer]
```

### 2.1 Dual-Trigger Flush
```python
DEFAULT_BATCH_SIZE = 100      # Flush at 100 events
FLUSH_TIMEOUT_MS = 500        # OR after 500ms
MAX_BATCH_SIZE = 1000         # Cap for spike absorption
```

---

## 3. API CONTRACT

### 3.1 IndexerQueue Class
```python
class IndexerQueue:
    def __init__(self, db_path: str = "data/indexer_queue.db"): ...
    
    def subscribe_to_eventbus(self, bus: HeavyEventBus) -> str:
        """Subscribe and return subscription_id"""
    
    def get_next_batch(self, timeout: float = 0.1) -> Optional[Batch]:
        """Pull model: returns next pending batch or None"""
    
    def mark_batch_done(self, batch_id: str) -> bool:
        """Mark batch as processed"""
    
    def metrics(self) -> QueueMetrics: ...
    
    def start(self) -> None: ...
    def stop(self, graceful: bool = True) -> None: ...
```

### 3.2 Data Structures
```python
@dataclass
class Batch:
    batch_id: str          # UUID v4
    created_at: float      # Unix timestamp
    events: List[Any]      # Deserialized events
    event_count: int
    status: str            # pending, processing, done

@dataclass
class QueueMetrics:
    buffer_size: int
    pending_batches: int
    events_processed_total: int
    events_duplicate_total: int
    avg_flush_latency_ms: float
```

---

## 4. SQLITE SCHEMA

```sql
CREATE TABLE IF NOT EXISTS pending_batches (
    batch_id TEXT PRIMARY KEY,
    created_at REAL NOT NULL,
    event_count INTEGER NOT NULL,
    events_data BLOB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    CHECK (status IN ('pending', 'processing', 'done'))
);

CREATE TABLE IF NOT EXISTS processed_events (
    event_id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    processed_at REAL NOT NULL
);

CREATE INDEX idx_pending_status ON pending_batches(status, created_at);
CREATE INDEX idx_processed_id ON processed_events(event_id);
```

---

## 5. TEST REQUIREMENTS (10 Cases)

| ID | Test Name | Description |
|----|-----------|-------------|
| T01 | queue_initializes_with_sqlite | DB created with tables |
| T02 | subscribe_to_eventbus | Can connect to EventBus |
| T03 | batch_creation_at_threshold_100 | Flush at 100 events |
| T04 | timeout_flush_500ms | Flush after 500ms |
| T05 | crash_recovery | Pending batches survive restart |
| T06 | idempotency_deduplication | Duplicates skipped |
| T07 | strict_fifo_ordering | Order preserved |
| T08 | performance_10k_under_1s | 10K events < 1s |
| T09 | sqlite_transaction_atomicity | All-or-nothing |
| T10 | graceful_shutdown | Pending events persisted |

---

**END OF SPEC** 🧊

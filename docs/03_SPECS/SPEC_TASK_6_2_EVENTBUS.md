# SPEC: HEAVY EVENTBUS (PYTHON 3.14 NO-GIL) - FINAL

> **Status:** 🧊 FROZEN | **Date:** 2025-12-27
> **Ref:** Task 6.2 | **Changes Applied:** Backpressure, Threading Model, Stress Tests

---

## 1. CORE SEMANTICS

### 1.1 Delivery Guarantees
- **At-least-once**: Cố gắng deliver đến tất cả subscribers
- **Order preservation**: Events từ cùng producer giữ thứ tự
- **Backpressure**: Drop oldest khi queue đầy
- **Failure isolation**: 1 subscriber crash không ảnh hưởng bus

### 1.2 Performance Targets
| Metric | Target |
|--------|--------|
| Publish throughput | 200K events/sec (publish-only) |
| End-to-end latency P99 | <50ms (1 subscriber) |
| Memory growth | <2MB per 10K events |
| Recovery time | <100ms after backpressure |

---

## 2. ARCHITECTURE

```
[Publisher Threads]
        ↓
[Bounded Queue (deque maxlen)]
        ↓
[Dispatcher Thread] → [ThreadPoolExecutor]
        ↓                    ↓
   [Metrics]          [Subscriber Callbacks]
```

### 2.1 Queue Implementation
```python
self._queue = collections.deque(maxlen=max_queue_size)
self._queue_lock = threading.Lock()
self._queue_not_empty = threading.Condition(self._queue_lock)
```

### 2.2 Threading Model
```python
self._executor = ThreadPoolExecutor(
    max_workers=max_workers or (os.cpu_count() * 2),
    thread_name_prefix="EventBusWorker"
)
```

---

## 3. API CONTRACT

### 3.1 HeavyEventBus Class
```python
class HeavyEventBus:
    def __init__(
        self,
        max_queue_size: int = 10000,
        max_workers: Optional[int] = None,
        name: str = "default"
    ): ...
    
    def publish(self, event: FileBatchEvent) -> str:
        """Return event_id (UUID v4)"""
    
    def subscribe(self, callback: Callable, name: str = "") -> str:
        """Return subscription_id"""
    
    def unsubscribe(self, subscription_id: str) -> bool: ...
    
    def metrics(self) -> EventBusMetrics: ...
    
    def start(self) -> None: ...
    
    def stop(self, graceful: bool = True, timeout: float = 5.0) -> None: ...
```

### 3.2 Data Structures
```python
@dataclass
class EventEnvelope:
    event_id: str      # UUID v4
    batch_id: str      # From Watchdog
    timestamp: float   # Unix ms
    event: Any
    source: str = "watchdog"

@dataclass  
class EventBusMetrics:
    events_published: int
    events_processed: int
    events_dropped: int
    queue_size_current: int
    queue_size_max: int
    subscribers_active: int
    avg_processing_time_ms: float
    uptime_seconds: float
```

---

## 4. TEST REQUIREMENTS (8 Cases)

| ID | Test Name | Description |
|----|-----------|-------------|
| T01 | publish_returns_event_id | UUID v4 returned |
| T02 | backpressure_drops_oldest | dropped_count increments |
| T03 | subscriber_isolation | Exception doesn't crash bus |
| T04 | publish_throughput_200k | 200K/sec publish-only |
| T05 | eventual_delivery_100k | 100K processed within 5s |
| T06 | metrics_accuracy | Concurrent updates correct |
| T07 | graceful_shutdown | Wait for pending events |
| T08 | memory_stability | <2MB per 10K events |

---

## 5. ACCEPTANCE CRITERIA

### ✅ MUST HAVE
- 200K publishes/second
- Backpressure drop oldest
- Subscriber isolation
- Graceful shutdown
- Metrics accuracy

### ⚠️ SHOULD HAVE (Post-Sprint)
- Priority queues
- Event replay
- Dynamic worker scaling

---

**END OF SPEC** 🧊

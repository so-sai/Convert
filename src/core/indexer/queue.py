"""
IndexerQueue - Batch Processing & SQLite Synchronization Pipeline
Task 6.3 - Sprint 6 Background Services

SPEC: docs/03_SPECS/SPEC_TASK_6_3_INDEXER_QUEUE.md (FROZEN)

Features:
- Dual-trigger flush: 100 events OR 500ms timeout
- SQLite WAL mode for crash safety
- Idempotency via processed_events table
- Pull model: get_next_batch() for downstream Indexer
- Strict FIFO ordering
"""

import json
import os
import sqlite3
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# Try to import EventBus for type hints
try:
    from src.core.services.eventbus import HeavyEventBus
except ImportError:
    HeavyEventBus = None  # type: ignore


# ===================================================================
# DATA STRUCTURES
# ===================================================================

@dataclass
class Batch:
    """Represents a batch of events ready for processing"""
    batch_id: str
    created_at: float
    events: List[Any]
    event_count: int
    status: str = "pending"  # pending, processing, done
    attempts: int = 0


@dataclass
class QueueMetrics:
    """Real-time metrics for IndexerQueue"""
    timestamp: float = field(default_factory=time.time)
    
    # Buffer stats
    buffer_size: int = 0
    
    # Batch stats
    pending_batches: int = 0
    processing_batches: int = 0
    done_batches: int = 0
    
    # Event stats
    events_received_total: int = 0
    events_processed_total: int = 0
    events_duplicate_total: int = 0
    
    # Performance
    avg_flush_latency_ms: float = 0.0
    
    # System
    uptime_seconds: float = 0.0


# ===================================================================
# INDEXER QUEUE
# ===================================================================

class IndexerQueue:
    """
    High-performance batch processing queue with SQLite persistence.
    
    Features:
    - Dual-trigger flush: batch_size OR timeout
    - WAL mode SQLite for crash safety
    - Idempotency via processed_events table
    - Pull model for downstream consumers
    - Strict FIFO ordering
    """
    
    # Default configuration
    DEFAULT_BATCH_SIZE = 100
    DEFAULT_FLUSH_TIMEOUT_MS = 500
    MAX_BATCH_SIZE = 1000
    
    def __init__(
        self,
        db_path: str = "data/indexer_queue.db",
        batch_size: int = DEFAULT_BATCH_SIZE,
        flush_timeout_ms: int = DEFAULT_FLUSH_TIMEOUT_MS
    ):
        """
        Initialize IndexerQueue.
        
        Args:
            db_path: Path to SQLite database file
            batch_size: Number of events to trigger flush (default: 100)
            flush_timeout_ms: Timeout in ms to trigger flush (default: 500)
        """
        self.db_path = db_path
        self.batch_size = min(batch_size, self.MAX_BATCH_SIZE)
        self.flush_timeout_ms = flush_timeout_ms
        
        # In-memory buffer
        self._buffer: deque = deque()
        self._buffer_lock = threading.Lock()
        
        # Processed event IDs cache (for idempotency check)
        self._processed_ids: set = set()
        self._processed_ids_lock = threading.Lock()
        
        # Metrics
        self._events_received = 0
        self._events_processed = 0
        self._events_duplicate = 0
        self._flush_latencies: List[float] = []
        self._metrics_lock = threading.Lock()
        self._start_time: Optional[float] = None
        
        # Lifecycle
        self._running = False
        self._stop_event = threading.Event()
        self._flush_timer: Optional[threading.Timer] = None
        self._flush_lock = threading.Lock()
        
        # SQLite connection (per-thread for safety)
        self._db_conn: Optional[sqlite3.Connection] = None
        self._db_lock = threading.Lock()
        
        # EventBus subscription
        self._eventbus: Optional[Any] = None
        self._subscription_id: Optional[str] = None
    
    # -------------------------------------------------------------------
    # LIFECYCLE METHODS
    # -------------------------------------------------------------------
    
    def start(self) -> None:
        """Start the queue and initialize SQLite."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._start_time = time.time()
        
        # Initialize SQLite
        self._init_database()
        
        # Load processed event IDs from DB (for crash recovery)
        self._load_processed_ids()
        
        # Start flush timer
        self._reset_flush_timer()
    
    def stop(self, graceful: bool = True) -> None:
        """
        Stop the queue.
        
        Args:
            graceful: If True, flush pending events before stopping
        """
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        # Cancel flush timer
        if self._flush_timer:
            self._flush_timer.cancel()
            self._flush_timer = None
        
        # Graceful: flush any remaining events
        if graceful:
            with self._buffer_lock:
                if len(self._buffer) > 0:
                    self._flush_buffer()
        
        # Unsubscribe from EventBus
        if self._eventbus and self._subscription_id:
            try:
                self._eventbus.unsubscribe(self._subscription_id)
            except:
                pass
        
        # Close SQLite connection
        if self._db_conn:
            self._db_conn.close()
            self._db_conn = None
    
    @property
    def is_running(self) -> bool:
        """Check if queue is currently running."""
        return self._running
    
    # -------------------------------------------------------------------
    # EVENTBUS INTEGRATION
    # -------------------------------------------------------------------
    
    def subscribe_to_eventbus(self, bus: Any) -> str:
        """
        Subscribe to EventBus to receive events.
        
        Args:
            bus: HeavyEventBus instance
            
        Returns:
            subscription_id: UUID string for unsubscribe
        """
        self._eventbus = bus
        self._subscription_id = bus.subscribe(
            callback=self._on_event_received,
            name="IndexerQueue"
        )
        return self._subscription_id
    
    def _on_event_received(self, event: Any) -> None:
        """
        Callback when event is received from EventBus.
        
        Args:
            event: Event data (dict with event_id)
        """
        if not self._running:
            return
        
        # Extract event_id for idempotency
        event_id = None
        if isinstance(event, dict):
            event_id = event.get("event_id")
        
        # Generate event_id if not provided
        if not event_id:
            event_id = str(uuid.uuid4())
        
        # Check for duplicate (in-memory cache is authoritative)
        with self._processed_ids_lock:
            if event_id in self._processed_ids:
                with self._metrics_lock:
                    self._events_duplicate += 1
                return  # Skip duplicate
            
            # Mark as seen IMMEDIATELY (before adding to buffer)
            # This prevents duplicates from entering buffer before flush
            self._processed_ids.add(event_id)
        
        # Add to buffer
        with self._buffer_lock:
            self._buffer.append({
                "event_id": event_id,
                "received_at": time.time(),
                "data": event
            })
            
            with self._metrics_lock:
                self._events_received += 1
            
            # Check if we should flush
            if len(self._buffer) >= self.batch_size:
                self._flush_buffer()
    
    # -------------------------------------------------------------------
    # BUFFER MANAGEMENT
    # -------------------------------------------------------------------
    
    def _reset_flush_timer(self) -> None:
        """Reset the flush timeout timer."""
        if self._flush_timer:
            self._flush_timer.cancel()
        
        if self._running:
            self._flush_timer = threading.Timer(
                self.flush_timeout_ms / 1000.0,
                self._on_flush_timeout
            )
            self._flush_timer.daemon = True
            self._flush_timer.start()
    
    def _on_flush_timeout(self) -> None:
        """Called when flush timeout expires."""
        if not self._running:
            return
        
        with self._flush_lock:
            with self._buffer_lock:
                if len(self._buffer) > 0:
                    self._flush_buffer()
        
        # Reset timer for next interval
        self._reset_flush_timer()
    
    def _flush_buffer(self) -> None:
        """
        Flush current buffer to SQLite as a batch.
        
        MUST be called with _buffer_lock held.
        """
        if len(self._buffer) == 0:
            return
        
        flush_start = time.time()
        
        # Create batch
        batch_id = str(uuid.uuid4())
        events_list = list(self._buffer)
        self._buffer.clear()
        
        # Persist to SQLite (atomic transaction)
        try:
            self._persist_batch(batch_id, events_list)
            
            # Update processed IDs cache
            with self._processed_ids_lock:
                for event in events_list:
                    self._processed_ids.add(event["event_id"])
            
            # Update metrics
            with self._metrics_lock:
                self._events_processed += len(events_list)
                flush_latency = (time.time() - flush_start) * 1000
                self._flush_latencies.append(flush_latency)
                if len(self._flush_latencies) > 100:
                    self._flush_latencies.pop(0)
                    
        except Exception as e:
            # Put events back on error
            for event in reversed(events_list):
                self._buffer.appendleft(event)
            raise e
    
    # -------------------------------------------------------------------
    # SQLITE OPERATIONS
    # -------------------------------------------------------------------
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection (creating if needed)."""
        if self._db_conn is None:
            # Ensure directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            self._db_conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None  # Autocommit for explicit transaction control
            )
            
            # Enable WAL mode for better concurrency
            self._db_conn.execute("PRAGMA journal_mode=WAL")
            self._db_conn.execute("PRAGMA synchronous=NORMAL")
            
        return self._db_conn
    
    def _init_database(self) -> None:
        """Initialize SQLite database with schema."""
        conn = self._get_connection()
        
        with self._db_lock:
            cursor = conn.cursor()
            
            # Create pending_batches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_batches (
                    batch_id TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    event_count INTEGER NOT NULL,
                    events_data BLOB NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    last_attempt REAL,
                    priority INTEGER DEFAULT 0,
                    CHECK (status IN ('pending', 'processing', 'done'))
                )
            """)
            
            # Create processed_events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_events (
                    event_id TEXT PRIMARY KEY,
                    batch_id TEXT NOT NULL,
                    processed_at REAL NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_pending_batches_status 
                ON pending_batches(status, created_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_events_event_id 
                ON processed_events(event_id)
            """)
            
            conn.commit()
    
    def _load_processed_ids(self) -> None:
        """Load processed event IDs from DB for crash recovery."""
        conn = self._get_connection()
        
        with self._db_lock:
            cursor = conn.cursor()
            cursor.execute("SELECT event_id FROM processed_events")
            
            with self._processed_ids_lock:
                for row in cursor.fetchall():
                    self._processed_ids.add(row[0])
    
    def _persist_batch(self, batch_id: str, events: List[Dict]) -> None:
        """
        Persist batch to SQLite in atomic transaction.
        
        Args:
            batch_id: UUID for the batch
            events: List of event dicts
        """
        conn = self._get_connection()
        
        with self._db_lock:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                # Insert batch
                events_data = json.dumps([e["data"] for e in events]).encode("utf-8")
                cursor.execute(
                    """
                    INSERT INTO pending_batches 
                    (batch_id, created_at, event_count, events_data, status)
                    VALUES (?, ?, ?, ?, 'pending')
                    """,
                    (batch_id, time.time(), len(events), events_data)
                )
                
                # Insert processed events (for idempotency)
                processed_at = time.time()
                for event in events:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO processed_events 
                        (event_id, batch_id, processed_at)
                        VALUES (?, ?, ?)
                        """,
                        (event["event_id"], batch_id, processed_at)
                    )
                
                cursor.execute("COMMIT")
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    
    # -------------------------------------------------------------------
    # PULL MODEL INTERFACE
    # -------------------------------------------------------------------
    
    def get_next_batch(self, timeout: float = 0.1) -> Optional[Batch]:
        """
        Get next pending batch for processing.
        
        Pull model: Caller (Indexer) calls this to get work.
        
        Args:
            timeout: Max seconds to wait for batch (default: 0.1s)
            
        Returns:
            Batch object or None if no batch available
        """
        deadline = time.time() + timeout
        
        while time.time() < deadline:
            batch = self._try_get_batch()
            if batch:
                return batch
            time.sleep(0.01)
        
        return None
    
    def _try_get_batch(self) -> Optional[Batch]:
        """Try to get and lock a pending batch."""
        conn = self._get_connection()
        
        with self._db_lock:
            cursor = conn.cursor()
            
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                # Get oldest pending batch
                cursor.execute(
                    """
                    SELECT batch_id, created_at, event_count, events_data, attempts
                    FROM pending_batches
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                    """
                )
                
                row = cursor.fetchone()
                if not row:
                    cursor.execute("ROLLBACK")
                    return None
                
                batch_id, created_at, event_count, events_data, attempts = row
                
                # Mark as processing
                cursor.execute(
                    """
                    UPDATE pending_batches 
                    SET status = 'processing', 
                        attempts = attempts + 1,
                        last_attempt = ?
                    WHERE batch_id = ?
                    """,
                    (time.time(), batch_id)
                )
                
                cursor.execute("COMMIT")
                
                # Parse events
                events = json.loads(events_data.decode("utf-8"))
                
                return Batch(
                    batch_id=batch_id,
                    created_at=created_at,
                    events=events,
                    event_count=event_count,
                    status="processing",
                    attempts=attempts + 1
                )
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    
    def mark_batch_done(self, batch_id: str) -> bool:
        """
        Mark batch as processed.
        
        Args:
            batch_id: Batch ID to mark as done
            
        Returns:
            True if batch was found and updated
        """
        conn = self._get_connection()
        
        with self._db_lock:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE pending_batches 
                SET status = 'done'
                WHERE batch_id = ?
                """,
                (batch_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    # -------------------------------------------------------------------
    # METRICS
    # -------------------------------------------------------------------
    
    def metrics(self) -> QueueMetrics:
        """Get current metrics snapshot."""
        conn = self._get_connection()
        
        with self._metrics_lock:
            uptime = 0.0
            if self._start_time:
                uptime = time.time() - self._start_time
            
            avg_latency = 0.0
            if self._flush_latencies:
                avg_latency = sum(self._flush_latencies) / len(self._flush_latencies)
            
            with self._buffer_lock:
                buffer_size = len(self._buffer)
            
            # Query batch counts from DB
            with self._db_lock:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT COUNT(*) FROM pending_batches WHERE status = 'pending'"
                )
                pending = cursor.fetchone()[0]
                
                cursor.execute(
                    "SELECT COUNT(*) FROM pending_batches WHERE status = 'processing'"
                )
                processing = cursor.fetchone()[0]
                
                cursor.execute(
                    "SELECT COUNT(*) FROM pending_batches WHERE status = 'done'"
                )
                done = cursor.fetchone()[0]
            
            return QueueMetrics(
                timestamp=time.time(),
                buffer_size=buffer_size,
                pending_batches=pending,
                processing_batches=processing,
                done_batches=done,
                events_received_total=self._events_received,
                events_processed_total=self._events_processed,
                events_duplicate_total=self._events_duplicate,
                avg_flush_latency_ms=avg_latency,
                uptime_seconds=uptime
            )

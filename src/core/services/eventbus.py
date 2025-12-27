"""
HeavyEventBus - High-Performance Event Bus for Python 3.14 No-GIL
Task 6.2 - Sprint 6 Background Services

SPEC: docs/03_SPECS/SPEC_TASK_6_2_EVENTBUS.md (FROZEN)

Implementation Status: GREEN PHASE DAY 1
"""

import collections
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class EventEnvelope:
    """Wrapper for events with metadata"""
    event_id: str
    batch_id: str
    timestamp: float
    event: Any
    source: str = "watchdog"
    publish_time: float = field(default_factory=time.time)


@dataclass
class EventBusMetrics:
    """Real-time metrics for EventBus"""
    bus_name: str = "default"
    timestamp: float = field(default_factory=time.time)
    
    # Throughput
    events_published: int = 0
    events_processed: int = 0
    events_dropped: int = 0
    
    # Queue
    queue_size_current: int = 0
    queue_size_max: int = 10000
    
    # Subscribers
    subscribers_active: int = 0
    
    # Performance
    avg_processing_time_ms: float = 0.0
    
    # System
    uptime_seconds: float = 0.0
    worker_threads_active: int = 0


class HeavyEventBus:
    """
    High-performance event bus with backpressure support.
    
    Features:
    - Bounded queue with drop-oldest backpressure
    - ThreadPoolExecutor for subscriber dispatch
    - Thread-safe operations for Python 3.14 No-GIL
    - Graceful shutdown with pending event handling
    """
    
    def __init__(
        self,
        max_queue_size: int = 200000,  # 200K buffer for 20s of peak load
        max_workers: Optional[int] = None,
        name: str = "default"
    ):
        """
        Initialize EventBus.
        
        Args:
            max_queue_size: Maximum events in queue (backpressure threshold)
            max_workers: Worker threads in pool (None = auto)
            name: Bus identifier for logging/metrics
        """
        self.name = name
        self.max_queue_size = max_queue_size
        self.max_workers = max_workers or (os.cpu_count() or 4) * 2
        
        # Queue with backpressure (deque maxlen auto-drops oldest)
        self._queue: collections.deque = collections.deque(maxlen=max_queue_size)
        self._queue_lock = threading.Lock()
        self._queue_not_empty = threading.Condition(self._queue_lock)
        
        # Subscribers: {subscription_id: (callback, name)}
        self._subscribers: Dict[str, tuple] = {}
        self._subscribers_lock = threading.Lock()
        
        # Metrics - thread-safe counters
        self._events_published = 0
        self._events_processed = 0
        self._events_dropped = 0
        self._metrics_lock = threading.Lock()
        self._start_time: Optional[float] = None
        self._processing_times: List[float] = []
        
        # Lifecycle
        self._running = False
        self._stop_event = threading.Event()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._dispatcher_thread: Optional[threading.Thread] = None
    
    def publish(self, event: Any) -> str:
        """
        Publish an event to the bus.
        
        Args:
            event: Event data (typically FileBatchEvent from Watchdog)
            
        Returns:
            event_id: UUID v4 string for tracking
        """
        # Generate UUID v4 for tracking
        event_id = str(uuid.uuid4())
        
        # Extract batch_id from event if available
        batch_id = ""
        if isinstance(event, dict) and "batch_id" in event:
            batch_id = event["batch_id"]
        
        # Create envelope
        envelope = EventEnvelope(
            event_id=event_id,
            batch_id=batch_id,
            timestamp=time.time(),
            event=event
        )
        
        with self._queue_lock:
            # Check if we'll trigger backpressure
            was_full = len(self._queue) >= self.max_queue_size
            
            # Append to queue (deque maxlen auto-drops oldest)
            self._queue.append(envelope)
            
            # Track dropped events for backpressure
            if was_full:
                with self._metrics_lock:
                    self._events_dropped += 1
            
            # Update metrics
            with self._metrics_lock:
                self._events_published += 1
            
            # Signal dispatcher
            self._queue_not_empty.notify()
        
        return event_id
    
    def subscribe(
        self,
        callback: Callable[[Any], None],
        name: str = ""
    ) -> str:
        """
        Subscribe to receive events.
        
        Args:
            callback: Function to call with each event
            name: Optional subscriber name for debugging
            
        Returns:
            subscription_id: Unique ID for unsubscribe
        """
        subscription_id = str(uuid.uuid4())
        
        with self._subscribers_lock:
            self._subscribers[subscription_id] = (callback, name or callback.__name__)
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Remove a subscription.
        
        Args:
            subscription_id: ID returned from subscribe()
            
        Returns:
            True if subscription was found and removed
        """
        with self._subscribers_lock:
            if subscription_id in self._subscribers:
                del self._subscribers[subscription_id]
                return True
            return False
    
    def metrics(self) -> EventBusMetrics:
        """
        Get current metrics snapshot.
        
        Returns:
            EventBusMetrics with current values
        """
        with self._metrics_lock:
            uptime = 0.0
            if self._start_time:
                uptime = time.time() - self._start_time
            
            avg_time = 0.0
            if self._processing_times:
                avg_time = sum(self._processing_times) / len(self._processing_times)
            
            with self._queue_lock:
                queue_size = len(self._queue)
            
            with self._subscribers_lock:
                sub_count = len(self._subscribers)
            
            return EventBusMetrics(
                bus_name=self.name,
                timestamp=time.time(),
                events_published=self._events_published,
                events_processed=self._events_processed,
                events_dropped=self._events_dropped,
                queue_size_current=queue_size,
                queue_size_max=self.max_queue_size,
                subscribers_active=sub_count,
                avg_processing_time_ms=avg_time * 1000,
                uptime_seconds=uptime,
                worker_threads_active=self.max_workers if self._executor else 0
            )
    
    def start(self) -> None:
        """
        Start the event bus dispatcher.
        
        Spawns dispatcher thread and worker pool.
        """
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._start_time = time.time()
        
        # Create thread pool for subscriber callbacks
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix=f"EventBus-{self.name}-Worker"
        )
        
        # Start dispatcher thread
        self._dispatcher_thread = threading.Thread(
            target=self._dispatch_worker,
            name=f"EventBus-{self.name}-Dispatcher",
            daemon=False
        )
        self._dispatcher_thread.start()
    
    def stop(self, graceful: bool = True, timeout: float = 5.0) -> None:
        """
        Stop the event bus.
        
        Args:
            graceful: If True, wait for pending events
            timeout: Max seconds to wait for graceful shutdown
        """
        if not self._running:
            return
        
        if graceful:
            # Wait for queue to drain BEFORE stopping dispatcher
            deadline = time.time() + timeout
            while time.time() < deadline:
                with self._queue_lock:
                    if len(self._queue) == 0:
                        break
                time.sleep(0.01)
            
            # Also wait for executor to finish pending tasks
            time.sleep(0.1)  # Small grace period for in-flight callbacks
        
        self._running = False
        
        # Signal dispatcher to stop
        self._stop_event.set()
        
        # Wake up dispatcher if waiting
        with self._queue_lock:
            self._queue_not_empty.notify_all()
        
        # Stop dispatcher thread
        if self._dispatcher_thread:
            self._dispatcher_thread.join(timeout=1.0)
            self._dispatcher_thread = None
        
        # Shutdown executor
        if self._executor:
            self._executor.shutdown(wait=graceful, cancel_futures=not graceful)
            self._executor = None
    
    @property
    def is_running(self) -> bool:
        """Check if bus is currently running"""
        return self._running
    
    def _dispatch_worker(self) -> None:
        """Background thread that dispatches events to subscribers"""
        while not self._stop_event.is_set():
            envelope: Optional[EventEnvelope] = None
            
            # Wait for event
            with self._queue_not_empty:
                while len(self._queue) == 0 and not self._stop_event.is_set():
                    self._queue_not_empty.wait(timeout=0.1)
                
                if self._stop_event.is_set() and len(self._queue) == 0:
                    break
                
                if len(self._queue) > 0:
                    envelope = self._queue.popleft()
            
            if envelope is None:
                continue
            
            # Dispatch to all subscribers via thread pool
            with self._subscribers_lock:
                subscribers_copy = list(self._subscribers.items())
            
            for sub_id, (callback, name) in subscribers_copy:
                if self._executor:
                    self._executor.submit(
                        self._safe_execute_callback,
                        callback,
                        envelope.event
                    )
    
    def _safe_execute_callback(
        self,
        callback: Callable,
        event: Any
    ) -> None:
        """Execute callback with exception isolation"""
        start_time = time.time()
        
        try:
            callback(event)
        except Exception as e:
            # Log but don't crash bus - isolation pattern
            print(f"[EVENTBUS] Subscriber error: {type(e).__name__}: {e}")
        finally:
            # Track processing time
            processing_time = time.time() - start_time
            
            with self._metrics_lock:
                self._events_processed += 1
                # Keep rolling average (last 100)
                self._processing_times.append(processing_time)
                if len(self._processing_times) > 100:
                    self._processing_times.pop(0)

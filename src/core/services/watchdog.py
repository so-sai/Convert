"""
Watchdog Service - File System Monitor with Debouncing
Sprint 6.1 - Background Services Core

Responsibilities:
1. Observe filesystem events (create/modify/delete)
2. Normalize events (debounce, batch, deduplicate)
3. Emit clean events to Queue
4. Lifecycle-safe (start/stop with no zombie threads)

Does NOT:
- Read file contents
- Parse markdown
- Touch SQLite
- Handle crypto
"""
import threading
import time
import uuid
from pathlib import Path
from typing import Callable, Set, Optional, List, Dict
from dataclasses import dataclass, field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


@dataclass
class FileEvent:
    """Normalized file event with POSIX path"""
    path: str  # Always POSIX format (forward slashes)
    event_type: str  # 'created', 'modified', 'deleted'
    timestamp: float
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class WatchdogService:
    """
    File system watcher with intelligent debouncing and batching.
    
    Thread-safe implementation that prevents event spam and ensures
    graceful shutdown without zombie threads.
    """
    
    def __init__(
        self,
        watch_path: str,
        debounce_ms: int = 1000,
        on_batch_ready: Optional[Callable[[List[FileEvent]], None]] = None,
        max_batch_size: int = 5000
    ):
        """
        Initialize Watchdog service.
        
        Args:
            watch_path: Directory to monitor
            debounce_ms: Milliseconds to wait before emitting batch
            on_batch_ready: Callback function for processed batches
            max_batch_size: Safety valve - force emit if exceeded
        """
        self.watch_path = Path(watch_path).as_posix()  # Normalize to POSIX
        self.debounce_ms = debounce_ms
        self.on_batch_ready = on_batch_ready
        self.max_batch_size = max_batch_size
        
        # Thread-safe event storage
        self._pending_events: Set[str] = set()
        self._event_details: Dict[str, FileEvent] = {}
        self._lock = threading.Lock()
        
        # Debounce timer tracking
        self._last_event_time: float = 0.0
        
        # Lifecycle management
        self._observer: Optional[Observer] = None
        self._flush_thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = threading.Event()
        
    @property
    def is_running(self) -> bool:
        """Check if service is currently running"""
        return self._running
        
    def _on_file_event(self, file_path: str, event_type: str):
        """
        Internal handler for file system events.
        Deduplicates and stores events for batching.
        
        Args:
            file_path: Path to the file (will be normalized to POSIX)
            event_type: Type of event (created/modified/deleted)
        """
        # Normalize path to POSIX format (forward slashes only)
        normalized_path = Path(file_path).as_posix()
        current_time = time.time()
        
        with self._lock:
            # Reset debounce timer on each new event
            self._last_event_time = current_time
            
            # Deduplicate by normalized path
            self._pending_events.add(normalized_path)
            self._event_details[normalized_path] = FileEvent(
                path=normalized_path,
                event_type=event_type,
                timestamp=current_time
            )
            
            # Safety valve: force emit if batch too large
            if len(self._pending_events) >= self.max_batch_size:
                self._flush_batch_unsafe()  # Called inside lock
            
    def _flush_batch_unsafe(self):
        """
        Flush batch without acquiring lock (called from within locked context).
        Used by safety valve.
        """
        if not self._pending_events:
            return
            
        # Collect batch
        batch = [
            self._event_details[path] 
            for path in self._pending_events
        ]
        
        # Clear pending
        self._pending_events.clear()
        self._event_details.clear()
        
        # Emit batch (callback may be slow, but we're in safety valve mode)
        if self.on_batch_ready and batch:
            try:
                self.on_batch_ready(batch)
            except Exception as e:
                print(f"[WATCHDOG] Error in batch callback (safety valve): {e}")
            
    def _flush_batch(self):
        """
        Flush pending events as a batch.
        Called by flush thread after debounce period.
        """
        with self._lock:
            if not self._pending_events:
                return
                
            # Collect batch
            batch = [
                self._event_details[path] 
                for path in self._pending_events
            ]
            
            # Clear pending
            self._pending_events.clear()
            self._event_details.clear()
            
        # Emit batch (outside lock to prevent deadlock)
        if self.on_batch_ready and batch:
            try:
                self.on_batch_ready(batch)
            except Exception as e:
                # Log but don't crash the service
                print(f"[WATCHDOG] Error in batch callback: {e}")
                
    def _flush_loop(self):
        """
        Background thread that periodically flushes batches.
        Runs until stop_event is set.
        """
        while not self._stop_event.is_set():
            # Wait for debounce period or stop signal
            if self._stop_event.wait(timeout=self.debounce_ms / 1000.0):
                break
                
            # Flush any pending events
            self._flush_batch()
            
    def start(self):
        """
        Start watching the file system.
        Spawns observer and flush threads.
        """
        if self._running:
            return
            
        self._running = True
        self._stop_event.clear()
        
        # Start flush thread
        self._flush_thread = threading.Thread(
            target=self._flush_loop,
            daemon=False,  # Explicitly non-daemon for clean shutdown
            name="WatchdogFlushThread"
        )
        self._flush_thread.start()
        
        # Start file system observer
        event_handler = _WatchdogEventHandler(self._on_file_event)
        self._observer = Observer()
        self._observer.schedule(event_handler, self.watch_path, recursive=True)
        self._observer.start()
        
    def stop(self):
        """
        Stop watching and clean up threads.
        Ensures no zombie threads remain.
        """
        if not self._running:
            return
            
        self._running = False
        
        # Signal stop
        self._stop_event.set()
        
        # Stop observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2.0)
            self._observer = None
            
        # Wait for flush thread
        if self._flush_thread:
            self._flush_thread.join(timeout=2.0)
            self._flush_thread = None
            
        # Final flush
        self._flush_batch()


class _WatchdogEventHandler(FileSystemEventHandler):
    """Internal event handler that bridges watchdog to our service"""
    
    def __init__(self, callback: Callable[[str, str], None]):
        super().__init__()
        self.callback = callback
        
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self.callback(event.src_path, "created")
            
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            self.callback(event.src_path, "modified")
            
    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            self.callback(event.src_path, "deleted")

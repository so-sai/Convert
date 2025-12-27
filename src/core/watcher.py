"""
Watchdog System — Real-time File Monitoring with Loop Prevention

This module implements a non-blocking file system watcher for the Convert Protocol.
It detects changes in monitored directories and synchronizes state with SQLite.

Design Principles:
- Observer Pattern with Async Bridge
- Hash-based Loop Prevention (no self-triggering)
- Thread-safe communication via run_coroutine_threadsafe
- SSOT: SQLite tracks asset state

MDS v3.14 Compliance: Rule #6 (Async/Threaded), Rule #26 (Context Preservation)
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from src.core.utils.paths import PathManager


class WatcherHandler(FileSystemEventHandler):
    """
    Handles file system events with hash-based loop prevention.
    
    Maintains an in-memory cache of file hashes to avoid responding to
    changes triggered by the app itself.
    """
    
    def __init__(self, on_event_callback):
        super().__init__()
        self.on_event_callback = on_event_callback
        self._ignore_hashes: Set[str] = set()
        self._last_processed: Dict[str, float] = {}
        self._debounce_seconds = 0.5
    
    def _get_file_hash(self, path: Path) -> Optional[str]:
        """Calculate SHA256 hash of file content."""
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def _should_process(self, event: FileSystemEvent) -> bool:
        """
        Determine if event should be processed.
        
        Returns False if:
        - Event is from a directory
        - File hash matches ignored set (self-write)
        - Event fired too soon after previous (debounce)
        """
        if event.is_directory:
            return False
        
        path = Path(event.src_path)
        now = time.time()
        
        # Debounce: ignore rapid-fire events
        last_time = self._last_processed.get(event.src_path, 0)
        if now - last_time < self._debounce_seconds:
            return False
        
        # Hash check: ignore if we just wrote this file
        file_hash = self._get_file_hash(path)
        if file_hash and file_hash in self._ignore_hashes:
            self._ignore_hashes.discard(file_hash)  # One-time ignore
            return False
        
        self._last_processed[event.src_path] = now
        return True
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if self._should_process(event):
            self.on_event_callback('modified', event.src_path)
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if self._should_process(event):
            self.on_event_callback('created', event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if not event.is_directory:
            self.on_event_callback('deleted', event.src_path)
    
    def add_ignore_hash(self, file_hash: str):
        """Mark a file hash to be ignored on next event (loop prevention)."""
        self._ignore_hashes.add(file_hash)


class AssetWatcher:
    """
    Main watcher class managing the Observer thread and event dispatching.
    
    Usage:
        watcher = AssetWatcher()
        watcher.start()
        # ... app runs ...
        watcher.stop()
    """
    
    def __init__(self, watch_path: Optional[Path] = None):
        self.watch_path = watch_path or (PathManager.get_app_root() / "assets")
        self.observer: Optional[Observer] = None
        self.handler: Optional[WatcherHandler] = None
        self._is_running = False
    
    def _on_file_event(self, event_type: str, file_path: str):
        """
        Callback for file system events.
        
        This is called from the Observer thread. To interact with async code,
        use asyncio.run_coroutine_threadsafe.
        """
        print(f"🔍 [WATCHER] {event_type.upper()}: {Path(file_path).name}")
        
        # TODO: Send event to state manager via async bridge
        # asyncio.run_coroutine_threadsafe(
        #     self._update_asset_db(event_type, file_path),
        #     self._event_loop
        # )
    
    def start(self):
        """Start the file system observer in a background thread."""
        if self._is_running:
            print("⚠️  [WATCHER] Already running")
            return
        
        # Ensure watch directory exists
        if not self.watch_path.exists():
            self.watch_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 [WATCHER] Created directory: {self.watch_path}")
        
        # Initialize handler and observer
        self.handler = WatcherHandler(on_event_callback=self._on_file_event)
        self.observer = Observer()
        self.observer.schedule(
            self.handler,
            str(self.watch_path),
            recursive=True
        )
        
        self.observer.start()
        self._is_running = True
        print(f"🚀 [WATCHER] Monitoring: {self.watch_path}")
    
    def stop(self):
        """Stop the file system observer and join the thread."""
        if not self._is_running:
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2.0)
            self._is_running = False
            print("🛑 [WATCHER] Stopped")
    
    def ignore_next_write(self, file_path: Path):
        """
        Mark the next write to this file to be ignored.
        
        Call this before writing a file to prevent self-triggering.
        """
        if self.handler:
            file_hash = self.handler._get_file_hash(file_path)
            if file_hash:
                self.handler.add_ignore_hash(file_hash)


if __name__ == "__main__":
    # Standalone test mode
    print("=== Watchdog Test Mode ===")
    print("Create/modify files in 'assets/' to trigger events.")
    print("Press Ctrl+C to exit.\n")
    
    watcher = AssetWatcher()
    watcher.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\n✅ Test complete")

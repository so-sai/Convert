"""
IDEMPOTENCY.PY - Event Deduplication & Pipeline Status
Task 6.5 - Sprint 6 Background Services

SPEC: SPEC_TASK_6_5_INTEGRATION.md (FROZEN)

Features:
- PipelineStatus enum for observability
- XXH3-based metadata hashing (fallback: blake2b)
- ProcessingRegistry for in-memory deduplication
- Thread-safe for Python 3.14 No-GIL
"""

import hashlib
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

# Try XXH3 first (optimal for 2025)
try:
    import xxhash
    XXH3_AVAILABLE = True
except ImportError:
    XXH3_AVAILABLE = False


# ===================================================================
# PIPELINE STATUS ENUM (OBSERVABILITY)
# ===================================================================

class PipelineStatus(Enum):
    """
    Pipeline processing status for high-observability.
    
    Replaces boolean returns with detailed status tracking.
    """
    INDEXED = "INDEXED"           # Success: data in FTS5
    DEGRADED = "DEGRADED"         # Partial: metadata only (content failed)
    QUARANTINED = "QUARANTINED"   # Security violation or corrupt
    RETRY = "RETRY"               # Temporary error (file lock, etc.)


# ===================================================================
# EVENT IDEMPOTENCY (METADATA HASHING)
# ===================================================================

class EventIdempotency:
    """
    Fast metadata-based event deduplication.
    
    Uses XXH3 (preferred) or blake2b (fallback) for sub-millisecond hashing.
    Hash key: path + mtime_ns + size (no file content I/O).
    """
    
    @staticmethod
    def generate_key(filepath: str | Path) -> str:
        """
        Generate unique idempotency key from file metadata.
        
        Args:
            filepath: Path to file
            
        Returns:
            Hex digest string (16 chars for XXH3, 32 for blake2b)
            
        Performance:
            - XXH3: ~0.01ms (64-bit hash)
            - blake2b: ~0.05ms (128-bit hash)
        """
        path_str = str(filepath)
        
        try:
            stat = os.stat(filepath)
            # Key components: path + nanosecond mtime + size
            fingerprint = f"{path_str}:{stat.st_mtime_ns}:{stat.st_size}"
            
            # Method 1: XXH3 (preferred for speed)
            if XXH3_AVAILABLE:
                return xxhash.xxh3_64(fingerprint.encode()).hexdigest()
            
            # Method 2: blake2b fallback (digest_size=16 for 32-char hex)
            else:
                return hashlib.blake2b(
                    fingerprint.encode(), 
                    digest_size=16
                ).hexdigest()
                
        except (OSError, FileNotFoundError):
            # Fallback: path-only hash (when file disappears)
            if XXH3_AVAILABLE:
                return xxhash.xxh3_64(path_str.encode()).hexdigest()
            else:
                return hashlib.blake2b(
                    path_str.encode(), 
                    digest_size=16
                ).hexdigest()


# ===================================================================
# PROCESSING RECORD
# ===================================================================

@dataclass
class ProcessingRecord:
    """
    Record of file processing attempt.
    
    Tracks status and retry count for observability.
    """
    event_key: str
    status: str  # 'processing', 'completed', 'failed'
    timestamp: datetime
    retry_count: int = 0


# ===================================================================
# PROCESSING REGISTRY (IN-MEMORY DEDUPLICATION)
# ===================================================================

class ProcessingRegistry:
    """
    In-memory registry for event deduplication.
    
    Thread-safe for Python 3.14 No-GIL.
    Uses RLock for mutation, lock-free for hot path (lookup).
    
    Features:
    - TTL-based expiration (default: 5 minutes)
    - Idempotency window (1 minute for completed events)
    - Retry logic (max 3 attempts)
    """
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize processing registry.
        
        Args:
            ttl_seconds: Time-to-live for records (default: 300s)
        """
        self._registry: Dict[str, ProcessingRecord] = {}
        self._lock = threading.RLock()
        self.ttl = ttl_seconds
        
    def should_process(self, event_key: str) -> bool:
        """
        Check if event should be processed.
        
        Returns False if:
        - Same event is being processed
        - Recently completed (within 1-minute idempotency window)
        
        Args:
            event_key: Event idempotency key
            
        Returns:
            True if event should be processed
        """
        with self._lock:
            self._cleanup_expired()
            
            if event_key not in self._registry:
                return True
                
            record = self._registry[event_key]
            
            # Still processing? Skip
            if record.status == 'processing':
                return False
            
            # Completed recently? Skip (idempotency window)
            if record.status == 'completed':
                time_since = datetime.now() - record.timestamp
                if time_since < timedelta(seconds=60):  # 1-minute window
                    return False
            
            # Failed but retryable? Process again
            if record.status == 'failed' and record.retry_count < 3:
                return True
                
            return False
    
    def mark_processing(self, event_key: str) -> None:
        """Mark event as being processed."""
        with self._lock:
            self._registry[event_key] = ProcessingRecord(
                event_key=event_key,
                status='processing',
                timestamp=datetime.now()
            )
    
    def mark_completed(self, event_key: str) -> None:
        """Mark event as successfully completed."""
        with self._lock:
            if event_key in self._registry:
                self._registry[event_key].status = 'completed'
                self._registry[event_key].timestamp = datetime.now()
    
    def mark_failed(self, event_key: str) -> None:
        """Mark event as failed (increment retry count)."""
        with self._lock:
            if event_key in self._registry:
                record = self._registry[event_key]
                record.status = 'failed'
                record.retry_count += 1
                record.timestamp = datetime.now()
    
    def _cleanup_expired(self) -> None:
        """Remove records older than TTL."""
        cutoff = datetime.now() - timedelta(seconds=self.ttl)
        expired = [
            key for key, record in self._registry.items()
            if record.timestamp < cutoff
        ]
        for key in expired:
            del self._registry[key]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get current registry statistics.
        
        Returns:
            Dict with counts by status
        """
        with self._lock:
            self._cleanup_expired()
            stats = {
                'total': len(self._registry),
                'processing': 0,
                'completed': 0,
                'failed': 0
            }
            for record in self._registry.values():
                if record.status in stats:
                    stats[record.status] += 1
            return stats

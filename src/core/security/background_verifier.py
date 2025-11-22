import asyncio
import threading
import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BackgroundChainVerifier:
    """
    Non-blocking chain verifier for Python 3.14 No-GIL.
    
    Strategy:
        - Verify incrementally (only new events since last check)
        - Run in background thread pool
        - Cache last verified sequence per stream
    """
    
    def __init__(self, storage_adapter, max_workers: int = 2):
        self.adapter = storage_adapter
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="chain-verify"
        )
        self._verification_cache: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    async def verify_stream_async(
        self,
        stream_type: str,
        stream_id: str,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """
        Non-blocking verification.
        
        Returns:
            True if chain is valid, False otherwise
        """
        key = f"{stream_type}:{stream_id}"
        
        # Check cache
        with self._lock:
            last_verified_seq = self._verification_cache.get(key, 0)
        
        # Verify only new events
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self.executor,
                self._verify_incremental,
                stream_type,
                stream_id,
                last_verified_seq,
                progress_callback
            )
            
            # Update cache on success
            if result["valid"]:
                with self._lock:
                    self._verification_cache[key] = result["last_seq"]
            
            return result["valid"]
        
        except Exception as e:
            logger.error(f"Background verification failed: {e}")
            return False
    
    def _verify_incremental(
        self,
        stream_type: str,
        stream_id: str,
        start_seq: int,
        progress_callback: Optional[callable]
    ) -> Dict[str, Any]:
        """
        Synchronous verification (runs in thread pool).
        
        This is CPU-bound (HMAC + SHA3), so it runs in a worker thread
        to avoid blocking the asyncio event loop.
        """
        # This runs in a background thread (Python 3.14 No-GIL)
        # Use synchronous sqlite3 (not aiosqlite)
        
        conn = sqlite3.connect(str(self.adapter.db_path))
        try:
            cursor = conn.execute(
                """
                SELECT event_id, payload, event_hmac, stream_sequence, hmac_key_version
                FROM domain_events
                WHERE stream_type = ? AND stream_id = ? AND stream_sequence > ?
                ORDER BY stream_sequence ASC
                """,
                (stream_type, stream_id, start_seq)
            )
            
            valid = True
            last_seq = start_seq
            total_verified = 0
            
            for row in cursor:
                event_id, payload, stored_hmac, seq, key_ver = row
                
                # Verify HMAC (CPU-intensive)
                # Note: We access self.adapter.hmac_service.verify which is thread-safe (pure python/stdlib)
                if not self.adapter.hmac_service.verify(payload, stored_hmac, stream_id, key_ver):
                    logger.warning(f"HMAC failed: {event_id}")
                    valid = False
                    break
                
                last_seq = seq
                total_verified += 1
                
                # Report progress every 100 events
                if progress_callback and total_verified % 100 == 0:
                    # Callback might need to be thread-safe or scheduled on loop
                    # For simplicity, we assume callback handles threading or is just logging
                    try:
                        progress_callback(total_verified)
                    except Exception:
                        pass
            
            return {
                "valid": valid,
                "last_seq": last_seq,
                "total_verified": total_verified
            }
        finally:
            conn.close()
    
    def shutdown(self):
        """Graceful shutdown of thread pool."""
        self.executor.shutdown(wait=True)

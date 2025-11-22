import asyncio
import logging
import sqlite3
import hashlib
import hmac
from typing import AsyncIterator, Dict, Any, Optional, List
from pathlib import Path

from src.core.storage.database import DatabaseManager
from src.core.crypto.hmac_service import HMACService
from src.core.utils.canonical import canonical_bytes

logger = logging.getLogger(__name__)

class StorageIntegrityError(Exception):
    """Raised when storage integrity verification fails."""
    pass

from src.core.security.background_verifier import BackgroundChainVerifier

class HardenedStorageAdapter:
    def __init__(self, db_path: Path, hmac_service: HMACService):
        self.db_path = db_path
        self._db_manager = DatabaseManager(db_path)
        self.hmac_service = hmac_service
        self.verifier = BackgroundChainVerifier(self)

    async def initialize(self):
        await self._db_manager.connect()

    async def close(self):
        self.verifier.shutdown()
        await self._db_manager.close()

    async def append_event(
        self,
        stream_type: str,
        stream_id: str,
        event_type: str,
        payload: Dict[str, Any],
        timestamp: int
    ) -> str:
        """
        Append an event with cryptographic integrity enforcement.
        """
        payload_bytes = canonical_bytes(payload)
        
        async with self._db_manager.transaction() as conn:
            # 1. Get previous event hash and sequence
            cursor = await conn.execute(
                """
                SELECT stream_sequence, event_hash 
                FROM domain_events 
                WHERE stream_type = ? AND stream_id = ? 
                ORDER BY stream_sequence DESC LIMIT 1
                """,
                (stream_type, stream_id)
            )
            row = await cursor.fetchone()
            
            if row:
                prev_seq, prev_hash = row
                stream_sequence = prev_seq + 1
            else:
                stream_sequence = 1
                prev_hash = None

            # 2. Get global sequence (atomic increment via DB constraint/autoincrement logic or max)
            # For strict ordering, we usually rely on a separate counter or max+1. 
            # Here we'll use max+1 for simplicity in this adapter, though a sequence generator is better for high concurrency.
            cursor = await conn.execute("SELECT MAX(global_sequence) FROM domain_events")
            max_global = (await cursor.fetchone())[0]
            global_sequence = (max_global or 0) + 1

            # 3. Compute Event Hash: SHA3-256(prev_hash || payload_bytes)
            # If prev_hash is None (genesis), use empty bytes or specific genesis marker.
            # We'll use empty bytes for genesis prev_hash in computation.
            prev_hash_bytes = prev_hash if prev_hash else b""
            
            event_hash = hashlib.sha3_256(prev_hash_bytes + payload_bytes).digest()
            
            # 4. Compute HMAC
            event_hmac, key_version = self.hmac_service.sign(payload_bytes, stream_id)
            
            # 5. Insert
            event_id = f"{stream_type}-{stream_id}-{stream_sequence}"
            
            await conn.execute(
                """
                INSERT INTO domain_events (
                    event_id, stream_type, stream_id, event_type, 
                    stream_sequence, global_sequence, timestamp, 
                    payload, prev_event_hash, event_hash, 
                    event_hmac, hmac_key_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id, stream_type, stream_id, event_type,
                    stream_sequence, global_sequence, timestamp,
                    payload_bytes, prev_hash, event_hash,
                    event_hmac, key_version
                )
            )
            
            return event_id

    async def get_events(
        self,
        stream_type: str,
        stream_id: str,
        after_seq: int = 0
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Yield events with on-the-fly HMAC verification.
        """
        # Note: We are NOT using a transaction here for the *entire* iteration 
        # because it might be long-lived. However, for strict consistency, snapshot isolation is good.
        # But aiosqlite cursors fetch eagerly or in batches.
        # For verification safety, we should ideally verify the chain.
        
        # We will verify each event as we yield it.
        
        async with self._db_manager.transaction() as conn:
             cursor = await conn.execute(
                """
                SELECT event_id, stream_sequence, timestamp, payload, 
                       prev_event_hash, event_hash, event_hmac, hmac_key_version
                FROM domain_events 
                WHERE stream_type = ? AND stream_id = ? AND stream_sequence > ?
                ORDER BY stream_sequence ASC
                """,
                (stream_type, stream_id, after_seq)
            )
             
             # We need to track prev_hash to verify chain continuity during iteration
             # But if we start from after_seq > 0, we need the hash of event at after_seq.
             # For simplicity, we verify the hash *of the current event* against its stored prev_hash
             # and its payload. We don't strictly verify the link to the *previous* yielded event 
             # unless we fetch it. 
             # Strict chain verification is done by verify_chain().
             # Here we verify:
             # 1. HMAC matches payload
             # 2. event_hash matches SHA3(prev_hash || payload)
             
             rows = await cursor.fetchall()
             
             for row in rows:
                 (eid, seq, ts, payload, prev_hash, ev_hash, ev_hmac, key_ver) = row
                 
                 # 1. Verify HMAC
                 if not self.hmac_service.verify(payload, ev_hmac, stream_id, key_ver):
                     raise StorageIntegrityError(f"HMAC mismatch for event {eid}")
                 
                 # 2. Verify Event Hash
                 prev_hash_bytes = prev_hash if prev_hash else b""
                 computed_hash = hashlib.sha3_256(prev_hash_bytes + payload).digest()
                 
                 # Constant time comparison for hash
                 if not hmac.compare_digest(computed_hash, ev_hash):
                      raise StorageIntegrityError(f"Event Hash mismatch for event {eid}")
                 
                 yield {
                     "event_id": eid,
                     "stream_sequence": seq,
                     "timestamp": ts,
                     "payload": payload, # Returns bytes (BLOB)
                     "event_hash": ev_hash
                 }

    async def verify_chain_non_blocking(self, stream_type: str, stream_id: str) -> bool:
        """
        Non-blocking chain verification using thread pool executor.
        Delegates to BackgroundChainVerifier.
        """
        return await self.verifier.verify_stream_async(stream_type, stream_id)

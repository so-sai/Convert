# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import aiosqlite
import orjson
import logging
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from ..security.kms import KMS
from ..security.encryption import EncryptionService, TamperDetectedError

logger = logging.getLogger(__name__)

class StorageAdapter:
    def __init__(self, db_path: Path, kms: KMS):
        self.db_path = db_path
        self.kms = kms
        self._init_done = False

    async def _ensure_schema(self):
        if self._init_done: return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            # Matches Schema Rev 2 (ADR-002 Rev 2)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS domain_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stream_type TEXT NOT NULL,
                    stream_id TEXT NOT NULL,
                    payload BLOB NOT NULL,       -- Ciphertext
                    enc_algorithm TEXT DEFAULT 'XChaCha20-Poly1305',
                    enc_key_id TEXT DEFAULT 'v1',
                    enc_nonce BLOB,              -- 24 bytes
                    
                    event_hmac BLOB NOT NULL,    -- HMAC-SHA3-256 (Chain)
                    event_hash BLOB,             -- Current Hash (Simplification)
                    timestamp INTEGER NOT NULL,
                    
                    quarantine INTEGER DEFAULT 0,
                    tamper_reason TEXT
                )
            """)
            await db.commit()
        self._init_done = True

    async def save_event(self, stream_type: str, stream_id: str, payload: Dict) -> int:
        # Check vault is unlocked and get master key
        if not self.kms.is_unlocked or self.kms._master_key is None:
            raise RuntimeError("Vault Locked: Must unlock vault before saving events")
        
        # Derive DEK and HMAC key from master key
        dek, hmac_key = EncryptionService.derive_keys(self.kms._master_key)
        await self._ensure_schema()
        
        json_bytes = orjson.dumps(payload)
        
        # Encrypt + Chain HMAC
        enc_blob, nonce, event_hmac = EncryptionService.encrypt_event(dek, hmac_key, json_bytes)
        
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                """INSERT INTO domain_events 
               (stream_type, stream_id, payload, enc_nonce, event_hmac, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?)""",
                (stream_type, stream_id, enc_blob, nonce, event_hmac, int(time.time()))
            )
            await db.commit()
            return cur.lastrowid

    async def get_events(self, limit: int = 100) -> List[Dict]:
        # Check vault is unlocked and get master key
        if not self.kms.is_unlocked or self.kms._master_key is None:
            raise RuntimeError("Vault Locked: Must unlock vault before reading events")
        
        # Derive DEK and HMAC key from master key
        dek, hmac_key = EncryptionService.derive_keys(self.kms._master_key)
        await self._ensure_schema()
        
        results = []
        async with aiosqlite.connect(self.db_path) as db:
            # SELECT matching the Rev 2 Schema
            query = "SELECT event_id, stream_type, payload, enc_nonce, event_hmac, timestamp FROM domain_events WHERE quarantine=0 ORDER BY timestamp DESC LIMIT ?"
            async with db.execute(query, (limit,)) as cur:
                async for row in cur:
                    eid, stype, payload, nonce, ehmac, ts = row
                    try:
                        if nonce:
                            # Decrypt + Verify Chain
                            plain = EncryptionService.decrypt_event(dek, hmac_key, payload, nonce, ehmac)
                            data = orjson.loads(plain)
                            results.append({"id": eid, "type": stype, "payload": data})
                        else:
                            # Legacy (Rule #13)
                            results.append({"id": eid, "type": stype, "payload": orjson.loads(payload), "_legacy": True})
                    except TamperDetectedError as e:
                        logger.critical(f"QUARANTINE EVENT {eid}: {e}")
                        # In real app: UPDATE domain_events SET quarantine=1...
                        continue
        return results

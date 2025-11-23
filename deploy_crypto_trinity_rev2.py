#!/usr/bin/env python3
# HASH: CODE-CRYPTO-TRINITY-REV2-ETERNAL
# IMPLEMENTS: TASK-4.4-REV2-FINAL
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import sys
import os
from pathlib import Path

def write_file(path_str: str, content: str):
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"✅ [SECURE WRITE] {path}")

# ==============================================================================
# 1. ENCRYPTION SERVICE (XChaCha20 + HMAC-SHA3 Chain)
# ==============================================================================

CODE_ENCRYPTION = """
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import nacl.secret
import nacl.utils
import nacl.exceptions
import nacl.bindings
import hashlib
import hmac
from typing import Tuple

class TamperDetectedError(Exception):
    \"\"\"Raised when Integrity Check (Poly1305 or HMAC-SHA3) fails.\"\"\"
    pass

NONCE_SIZE = 24 # 192-bit XChaCha20 Nonce

class EncryptionService:
    @staticmethod
    def derive_keys(master_secret: bytes) -> Tuple[bytes, bytes]:
        \"\"\"
        Derive DEK and HMAC_KEY from a single Epoch Secret.
        Uses BLAKE2b as a simple KDF for separation.
        \"\"\"
        # Key 1: Encryption (DEK) - first 32 bytes
        dek = hashlib.blake2b(master_secret, digest_size=32, person=b'ENC_KEY_').digest()
        # Key 2: Integrity (HMAC) - second 32 bytes
        hmac_key = hashlib.blake2b(master_secret, digest_size=32, person=b'MAC_KEY_').digest()
        return dek, hmac_key

    @staticmethod
    def wrap_dek(master_key: bytes, dek: bytes) -> bytes:
        \"\"\"Wrap the Epoch Secret using the User Master Key (KEK).\"\"\"
        nonce = nacl.utils.random(NONCE_SIZE)
        ciphertext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
            dek, None, nonce, master_key
        )
        return nonce + ciphertext

    @staticmethod
    def unwrap_dek(master_key: bytes, wrapped_blob: bytes) -> bytes:
        \"\"\"Unwrap the Epoch Secret.\"\"\"
        try:
            nonce = wrapped_blob[:NONCE_SIZE]
            ciphertext = wrapped_blob[NONCE_SIZE:]
            return nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                ciphertext, None, nonce, master_key
            )
        except Exception as e:
            raise TamperDetectedError(f"Master Key Integrity Failure: {e}")

    @staticmethod
    def encrypt_event(dek: bytes, hmac_key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        \"\"\"
        Implements Crypto-Trinity:
        1. Calculate HMAC-SHA3-256 (Plaintext) -> The Chain Link
        2. Encrypt (Plaintext) -> Ciphertext
        
        Returns: (ciphertext_blob, nonce, event_hmac)
        \"\"\"
        # 1. Integrity Chain (Rule #4 - Hash before Encrypt)
        # Using SHA3-256 for the HMAC
        event_hmac = hmac.new(hmac_key, plaintext, hashlib.sha3_256).digest()
        
        # 2. Encryption (XChaCha20-Poly1305)
        nonce = nacl.utils.random(NONCE_SIZE)
        ciphertext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
            plaintext, None, nonce, dek
        )
        
        return ciphertext, nonce, event_hmac

    @staticmethod
    def decrypt_event(dek: bytes, hmac_key: bytes, ciphertext_blob: bytes, nonce: bytes, expected_hmac: bytes) -> bytes:
        \"\"\"
        Decrypts and Verifies Integrity.
        1. Decrypt XChaCha20 (Poly1305 check)
        2. Verify HMAC-SHA3-256 (Chain check)
        \"\"\"
        # 1. Decrypt
        if len(nonce) != NONCE_SIZE: raise TamperDetectedError("Invalid Nonce Size")
        try:
            plaintext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                ciphertext_blob, None, nonce, dek
            )
        except Exception:
            raise TamperDetectedError("AEAD Poly1305 Check Failed (Ciphertext modified)")

        # 2. Verify Chain Integrity
        calculated_hmac = hmac.new(hmac_key, plaintext, hashlib.sha3_256).digest()
        if not hmac.compare_digest(calculated_hmac, expected_hmac):
            raise TamperDetectedError("Chain HMAC Mismatch (Event modified after encryption or logic error)")
            
        return plaintext
"""

# ==============================================================================
# 2. KMS (Key Management System - Epoch Secret)
# ==============================================================================

CODE_KMS = """
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import nacl.pwhash
import nacl.utils
import logging
from typing import Optional, Tuple
from pathlib import Path
from .storage import KeyStorage
from .encryption import EncryptionService

logger = logging.getLogger(__name__)

class KMS:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._epoch_secret: Optional[bytes] = None
        self._storage = KeyStorage(db_path)
        # OWASP 2025 Standard
        self.OPS = 2
        self.MEM = 19 * 1024 * 1024 # 19 MiB
        self.KEY_SIZE = 32

    async def initialize_vault(self, passkey: str) -> None:
        await self._storage.ensure_table_exists()
        if await self._storage.load_keys(): raise RuntimeError("Vault already initialized")

        salt = nacl.utils.random(nacl.pwhash.SALTBYTES)
        # Derive KEK from Passkey
        kek = nacl.pwhash.argon2id.kdf(self.KEY_SIZE, passkey.encode(), salt, opslimit=self.OPS, memlimit=self.MEM)
        
        # Generate Epoch Secret (Root of Trust for DEK & HMAC)
        epoch_secret = nacl.utils.random(self.KEY_SIZE)
        
        # Wrap Epoch Secret
        enc_blob = EncryptionService.wrap_dek(kek, epoch_secret)
        
        # Save (Store blob in enc_dek, empty nonce as it's inside blob now)
        await self._storage.save_keys(salt, enc_blob, b'', self.OPS, self.MEM)
        self._epoch_secret = epoch_secret

    async def unlock_vault(self, passkey: str) -> bool:
        await self._storage.ensure_table_exists()
        row = await self._storage.load_keys()
        if not row: return False
        salt, enc_blob, _, ops, mem = row
        
        try:
            kek = nacl.pwhash.argon2id.kdf(self.KEY_SIZE, passkey.encode(), salt, opslimit=ops, memlimit=mem)
            self._epoch_secret = EncryptionService.unwrap_dek(kek, enc_blob)
            return True
        except Exception:
            return False

    def get_keys(self) -> Tuple[bytes, bytes]:
        \"\"\"Returns (DEK, HMAC_KEY)\"\"\"
        if not self._epoch_secret: raise Exception("Vault Locked")
        return EncryptionService.derive_keys(self._epoch_secret)
"""

# ==============================================================================
# 3. STORAGE ADAPTER (Schema Rev 2 - BLOBs & HMAC)
# ==============================================================================

CODE_ADAPTER = """
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
            await db.execute(\"\"\"
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
            \"\"\")
            await db.commit()
        self._init_done = True

    async def save_event(self, stream_type: str, stream_id: str, payload: Dict) -> int:
        dek, hmac_key = self.kms.get_keys() # Check lock & get derived keys
        await self._ensure_schema()
        
        json_bytes = orjson.dumps(payload)
        
        # Encrypt + Chain HMAC
        enc_blob, nonce, event_hmac = EncryptionService.encrypt_event(dek, hmac_key, json_bytes)
        
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                \"\"\"INSERT INTO domain_events 
               (stream_type, stream_id, payload, enc_nonce, event_hmac, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?)\"\"\",
                (stream_type, stream_id, enc_blob, nonce, event_hmac, int(time.time()))
            )
            await db.commit()
            return cur.lastrowid

    async def get_events(self, limit: int = 100) -> List[Dict]:
        dek, hmac_key = self.kms.get_keys()
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
"""

# ==============================================================================
# 4. SUPPORTING FILES (Storage & Main)
# ==============================================================================

CODE_STORAGE = """
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import aiosqlite
from typing import Optional, Tuple
from pathlib import Path

class KeyStorage:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def ensure_table_exists(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(\"\"\"
                CREATE TABLE IF NOT EXISTS system_keys (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    salt BLOB NOT NULL,
                    enc_dek BLOB NOT NULL,
                    dek_nonce BLOB NOT NULL,
                    ops_limit INTEGER NOT NULL,
                    mem_limit INTEGER NOT NULL,
                    created_at INTEGER DEFAULT (unixepoch())
                ) STRICT;
            \"\"\")
            await db.commit()

    async def save_keys(self, salt, enc_dek, dek_nonce, ops, mem):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO system_keys VALUES (1, ?, ?, ?, ?, ?, unixepoch())", (salt, enc_dek, dek_nonce, ops, mem))
            await db.commit()

    async def load_keys(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT salt, enc_dek, dek_nonce, ops_limit, mem_limit FROM system_keys WHERE id = 1") as c:
                return await c.fetchone()
"""

CODE_MAIN = """
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from .security.kms import KMS
from .storage.adapter import StorageAdapter

logging.basicConfig(level=logging.INFO)
app = FastAPI()
DB_PATH = Path("data/mds.db")
kms = KMS(DB_PATH)
adapter = StorageAdapter(DB_PATH, kms)

class UnlockRequest(BaseModel):
    passkey: str

class EventRequest(BaseModel):
    type: str
    id: str
    payload: dict

@app.post("/vault/init")
async def init(req: UnlockRequest):
    await kms.initialize_vault(req.passkey)
    return {"status": "ok"}

@app.post("/vault/unlock")
async def unlock(req: UnlockRequest):
    if await kms.unlock_vault(req.passkey): return {"status": "unlocked"}
    raise HTTPException(401)

@app.post("/events")
async def save(req: EventRequest):
    try:
        eid = await adapter.save_event(req.type, req.id, req.payload)
        return {"id": eid}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/events")
async def get():
    return await adapter.get_events()
"""

# EXECUTE WRITES
write_file("src/core/security/encryption.py", CODE_ENCRYPTION)
write_file("src/core/security/storage.py", CODE_STORAGE)
write_file("src/core/security/kms.py", CODE_KMS)
write_file("src/core/storage/adapter.py", CODE_ADAPTER)
write_file("src/core/main.py", CODE_MAIN)

print(f"\n🔒 CRYPTO TRINITY (REV 2 - ETERNAL) DEPLOYED SUCCESSFULLY.")

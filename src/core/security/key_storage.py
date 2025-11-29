# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import aiosqlite
import os
from typing import Dict, Any, Optional

class KeyStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_keys (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    salt BLOB NOT NULL,
                    enc_dek BLOB NOT NULL,
                    dek_nonce BLOB NOT NULL,
                    ops_limit INTEGER NOT NULL,
                    mem_limit INTEGER NOT NULL,
                    rk_wrapped_dek BLOB,
                    recovery_salt BLOB,
                    rk_ops_limit INTEGER DEFAULT 2,
                    rk_mem_limit INTEGER DEFAULT 67108864,
                    rk_nonce BLOB,
                    created_at INTEGER DEFAULT (unixepoch())
                ) STRICT;
            """)
            await db.commit()

    async def key_exists(self) -> bool:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM system_keys WHERE id = 1") as cursor:
                return await cursor.fetchone() is not None

    async def save_keys(self, salt: bytes, enc_dek: bytes, dek_nonce: bytes, ops_limit: int, mem_limit: int,
                  rk_wrapped_dek: bytes, recovery_salt: bytes, rk_ops_limit: int, rk_mem_limit: int, rk_nonce: bytes):
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO system_keys (
                    id, salt, enc_dek, dek_nonce, ops_limit, mem_limit,
                    rk_wrapped_dek, recovery_salt, rk_ops_limit, rk_mem_limit, rk_nonce
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (salt, enc_dek, dek_nonce, ops_limit, mem_limit, 
                   rk_wrapped_dek, recovery_salt, rk_ops_limit, rk_mem_limit, rk_nonce))
            await db.commit()

    async def load_keys(self) -> Dict[str, Any]:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM system_keys WHERE id = 1") as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise ValueError("No keys found in database.")
                return dict(row)

    async def load_recovery_keys(self) -> Dict[str, Any]:
        return await self.load_keys()

    async def update_passkey_wrap(self, salt: bytes, enc_dek: bytes, dek_nonce: bytes, ops_limit: int, mem_limit: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE system_keys 
                SET salt = ?, enc_dek = ?, dek_nonce = ?, ops_limit = ?, mem_limit = ?
                WHERE id = 1
            """, (salt, enc_dek, dek_nonce, ops_limit, mem_limit))
            await db.commit()
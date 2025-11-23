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
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_keys (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    salt BLOB NOT NULL,
                    enc_dek BLOB NOT NULL,
                    dek_nonce BLOB NOT NULL,
                    ops_limit INTEGER NOT NULL,
                    mem_limit INTEGER NOT NULL,
                    created_at INTEGER DEFAULT (unixepoch())
                ) STRICT;
            """)
            await db.commit()

    async def save_keys(self, salt, enc_dek, dek_nonce, ops, mem):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO system_keys VALUES (1, ?, ?, ?, ?, ?, unixepoch())", (salt, enc_dek, dek_nonce, ops, mem))
            await db.commit()

    async def load_keys(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT salt, enc_dek, dek_nonce, ops_limit, mem_limit FROM system_keys WHERE id = 1") as c:
                return await c.fetchone()

# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import aiosqlite
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class KeyStorage:
    """
    Manages persistence of encrypted keys with Recovery Phrase support.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def ensure_table_exists(self):
        """Ensure system_keys table exists with recovery columns"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_keys (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    salt BLOB NOT NULL,
                    enc_dek BLOB NOT NULL,
                    rk_wrapped_dek BLOB,
                    dek_nonce BLOB NOT NULL,
                    ops_limit INTEGER NOT NULL,
                    mem_limit INTEGER NOT NULL,
                    recovery_salt BLOB,
                    rk_ops_limit INTEGER DEFAULT 2,
                    rk_mem_limit INTEGER DEFAULT 67108864,
                    created_at INTEGER DEFAULT (unixepoch())
                ) STRICT;
            """)
            await db.commit()

    async def save_keys(
        self, 
        salt: bytes, 
        enc_dek: bytes, 
        rk_wrapped_dek: Optional[bytes] = None,
        dek_nonce: bytes = b'',
        ops: int = 2,
        mem: int = 19922944,
        recovery_salt: Optional[bytes] = None,
        rk_ops: int = 2,
        rk_mem: int = 67108864
    ):
        """Save all keys with optional recovery data"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO system_keys 
                   (id, salt, enc_dek, rk_wrapped_dek, dek_nonce, ops_limit, mem_limit, 
                    recovery_salt, rk_ops_limit, rk_mem_limit) 
                   VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (salt, enc_dek, rk_wrapped_dek, dek_nonce, ops, mem, recovery_salt, rk_ops, rk_mem)
            )
            await db.commit()

    async def load_keys(self) -> Optional[Tuple[bytes, bytes, Optional[bytes], bytes, int, int, Optional[bytes], int, int]]:
        """Load all keys including recovery data"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT salt, enc_dek, rk_wrapped_dek, dek_nonce, ops_limit, mem_limit, 
                       recovery_salt, rk_ops_limit, rk_mem_limit
                FROM system_keys WHERE id = 1
            """) as cursor:
                return await cursor.fetchone()

    async def load_recovery_keys(self) -> Optional[Tuple[bytes, bytes, int, int]]:
        """
        Load only recovery-related keys and parameters.
        
        Returns:
            Tuple of (recovery_salt, rk_wrapped_dek, rk_ops_limit, rk_mem_limit)
            or None if no recovery keys exist
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT recovery_salt, rk_wrapped_dek, rk_ops_limit, rk_mem_limit
                FROM system_keys WHERE id = 1 AND rk_wrapped_dek IS NOT NULL
            """) as cursor:
                return await cursor.fetchone()

    async def update_passkey_wrap(self, new_salt: bytes, new_enc_dek: bytes):
        """
        Update only the passkey-wrapped DEK (used during recovery).
        
        Args:
            new_salt: New salt for passkey KDF
            new_enc_dek: New wrapped DEK with new passkey
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE system_keys 
                   SET salt = ?, enc_dek = ?
                   WHERE id = 1""",
                (new_salt, new_enc_dek)
            )
            await db.commit()

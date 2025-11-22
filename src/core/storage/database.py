import aiosqlite
import logging
from pathlib import Path
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None

    async def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        # Enforce STRICT mode and Foreign Keys
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        
        await self._init_schema()
        logger.info(f"DB Connected: {self.db_path}")

    async def _init_schema(self):
        # STRICT tables with BLOB enforcement
        ddl = """
        CREATE TABLE IF NOT EXISTS domain_events (
            event_id TEXT PRIMARY KEY,
            stream_type TEXT NOT NULL CHECK(stream_type IN ('domain','interaction','memory')),
            stream_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            stream_sequence INTEGER NOT NULL,
            global_sequence INTEGER NOT NULL UNIQUE,
            timestamp INTEGER NOT NULL,
            payload BLOB NOT NULL,
            prev_event_hash BLOB,
            event_hash BLOB NOT NULL,
            enc_algorithm TEXT DEFAULT 'pass-through',
            enc_key_id TEXT, 
            enc_nonce BLOB, 
            event_hmac TEXT NOT NULL,
            hmac_key_version TEXT NOT NULL DEFAULT 'v1',
            UNIQUE(stream_type, stream_id, stream_sequence)
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY, 
            path TEXT UNIQUE, 
            title TEXT, 
            content BLOB NOT NULL,
            metadata BLOB NOT NULL, 
            enc_algorithm TEXT, 
            enc_key_id TEXT, 
            enc_nonce BLOB,
            created_at INTEGER, 
            updated_at INTEGER, 
            deleted_at INTEGER, 
            version INTEGER DEFAULT 1
        ) STRICT;
        """
        await self._conn.executescript(ddl)
        await self._conn.commit()

    @asynccontextmanager
    async def transaction(self):
        """
        Async context manager for database transactions.
        Automatically commits on success, rolls back on exception.
        """
        if not self._conn:
            await self.connect()
            
        try:
            await self._conn.execute("BEGIN IMMEDIATE")
            yield self._conn
            await self._conn.commit()
        except Exception as e:
            logger.error(f"Transaction failed, rolling back: {e}")
            if self._conn:
                await self._conn.rollback()
            raise

    async def close(self): 
        if self._conn: 
            await self._conn.close()
            self._conn = None

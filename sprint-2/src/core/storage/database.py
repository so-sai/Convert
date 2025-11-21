import aiosqlite
from pathlib import Path
import logging

logger = logging.getLogger("CORE.STORAGE")

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None

    async def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self.db_path))
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._init_schema()
        logger.info(f"DB Connected: {self.db_path}")

    async def _init_schema(self):
        ddl = """
        CREATE TABLE IF NOT EXISTS domain_events (
            event_id TEXT PRIMARY KEY,
            stream_type TEXT NOT NULL,
            stream_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            stream_sequence INTEGER NOT NULL,
            global_sequence INTEGER NOT NULL UNIQUE,
            timestamp INTEGER NOT NULL,
            payload BLOB NOT NULL,
            prev_event_hash BLOB,
            event_hash BLOB NOT NULL,
            enc_algorithm TEXT DEFAULT 'pass-through',
            enc_key_id TEXT, enc_nonce BLOB, event_hmac TEXT NOT NULL,
            UNIQUE(stream_type, stream_id, stream_sequence)
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY, path TEXT UNIQUE, title TEXT, content BLOB,
            metadata BLOB, enc_algorithm TEXT, enc_key_id TEXT, enc_nonce BLOB,
            created_at INTEGER, updated_at INTEGER, deleted_at INTEGER, version INTEGER DEFAULT 1
        ) STRICT;
        """
        await self._conn.executescript(ddl)
        await self._conn.commit()

    def get_connection(self): return self._conn
    async def close(self): 
        if self._conn: await self._conn.close()

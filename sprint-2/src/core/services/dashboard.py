import hashlib, logging
from datetime import datetime, timezone
from src.core.config import get_data_path
from src.core.schemas.events import StreamType, SystemHealth, SystemStats, RecentNote
from src.core.storage.database import DatabaseManager
from src.core.crypto.service import StdLibCryptoService
from src.core.storage.adapter import StorageAdapter

logger = logging.getLogger("CORE.SERVICES")

class MDSDashboardService:
    def __init__(self):
        self.db_path = get_data_path() / "mds_eternal.db"
        self._start_time = datetime.now(timezone.utc)
        self.db_manager = None
        self.storage_adapter = None
        
    async def initialize(self):
        self.db_manager = DatabaseManager(self.db_path)
        await self.db_manager.connect()
        master_key = hashlib.sha3_256(b"mds_v3_1_master_key_32_bytes!").digest()
        self.storage_adapter = StorageAdapter(self.db_manager, StdLibCryptoService(master_key))
        await self._create_sample()
        logger.info("Service initialized")

    async def _create_sample(self):
        note = {"note_id": "1", "title": "Hello MDS", "content": "Init", "path": "a.md", "version": 1, "timestamp": 0}
        await self.storage_adapter.append_event(StreamType.DOMAIN, "notes:1", "NoteCreated", note)

    async def get_system_health(self) -> SystemHealth:
        uptime = int((datetime.now(timezone.utc) - self._start_time).total_seconds())
        return SystemHealth(status="connected", backend_version="3.1", uptime_seconds=uptime, last_check=datetime.now(timezone.utc), database_connected=True, chain_integrity=True)

    async def get_system_stats(self) -> SystemStats:
        stats = await self.storage_adapter.get_system_stats()
        return SystemStats(**stats)

    async def get_recent_notes(self, limit: int) -> list[RecentNote]:
        raw = await self.storage_adapter.get_recent_notes(limit)
        return [RecentNote(id=r['note_id'], title=r['title'], updated_at=datetime.now(timezone.utc), excerpt=r['content']) for r in raw]
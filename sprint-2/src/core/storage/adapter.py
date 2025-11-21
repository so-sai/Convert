import logging, orjson, hmac
from datetime import datetime, timezone
from src.core.schemas.events import StreamType
logger = logging.getLogger("CORE.STORAGE")

class StorageAdapter:
    def __init__(self, db_manager, crypto):
        self.db = db_manager
        self.crypto = crypto

    async def append_event(self, stream_type, stream_id, event_type, payload_dict):
        conn = self.db.get_connection()
        canonical = orjson.dumps(payload_dict, option=orjson.OPT_SORT_KEYS)
        enc_payload, algo, kid, nonce = self.crypto.encrypt(canonical)
        
        async with conn.cursor() as cursor:
            await cursor.execute("BEGIN IMMEDIATE")
            # Global Seq
            cursor = await conn.execute("SELECT COALESCE(MAX(global_sequence), 0) + 1 FROM domain_events")
            g_seq = (await cursor.fetchone())[0]
            
            # Stream Seq
            await cursor.execute("SELECT stream_sequence, event_hash FROM domain_events WHERE stream_type=? AND stream_id=? ORDER BY stream_sequence DESC LIMIT 1", (stream_type.value, stream_id))
            row = await cursor.fetchone()
            next_seq, prev_hash = (row[0]+1, row[1]) if row else (1, None)

            # Integrity
            ts = int(datetime.now(timezone.utc).timestamp() * 1_000_000)
            eid = f"{stream_type.value}:{stream_id}:{next_seq}"
            h_input = b"".join([eid.encode(), str(next_seq).encode(), str(ts).encode(), prev_hash or b"", enc_payload])
            e_hash = self.crypto.hash_event(h_input)
            e_hmac = self.crypto.calculate_hmac(stream_id, e_hash)

            await cursor.execute("INSERT INTO domain_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                (eid, stream_type.value, stream_id, event_type, next_seq, g_seq, ts, enc_payload, prev_hash, e_hash, algo, kid, nonce, e_hmac))
            await conn.commit()
            return eid
    
    async def verify_chain_integrity(self, stream_type, stream_id) -> bool:
        if hasattr(stream_type, 'value'): stream_type = stream_type.value
        conn = self.db.get_connection()
        async with conn.execute("SELECT event_id, stream_sequence, timestamp, payload, prev_event_hash, event_hash, event_hmac FROM domain_events WHERE stream_type=? AND stream_id=? ORDER BY stream_sequence", (stream_type, stream_id)) as cursor:
            prev_hash = None
            async for row in cursor:
                if row[4] != prev_hash: return False
                h_input = b"".join([row[0].encode(), str(row[1]).encode(), str(row[2]).encode(), row[4] or b"", row[3]])
                if self.crypto.hash_event(h_input) != row[5]: return False
                if not hmac.compare_digest(self.crypto.calculate_hmac(stream_id, row[5]), row[6]): return False
                prev_hash = row[5]
            return True

    async def get_recent_notes(self, limit=5):
        conn = self.db.get_connection()
        async with conn.execute("SELECT payload FROM domain_events WHERE event_type='NoteCreated' ORDER BY timestamp DESC LIMIT ?", (limit,)) as cursor:
            notes = []
            async for row in cursor:
                try:
                    data = orjson.loads(self.crypto.decrypt(row[0], 'pass-through', None, None))
                    notes.append(data)
                except: pass
            return notes
    
    async def get_system_stats(self):
        return {"total_events": 0, "total_notes": 0, "mds_version": "3.1-ETERNAL", "crypto_integrity": "HMAC-SHA3-256"}
# src/core/storage/migrations/003_add_hmac_key_version.py
import logging

logger = logging.getLogger(__name__)

async def upgrade(conn):
    """Add hmac_key_version column."""
    logger.info("Applying migration: 003_add_hmac_key_version")
    try:
        await conn.execute("""
            ALTER TABLE domain_events 
            ADD COLUMN hmac_key_version TEXT NOT NULL DEFAULT 'v1'
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_hmac_key_version 
            ON domain_events(hmac_key_version)
        """)
        
        # Backfill existing rows (already handled by DEFAULT 'v1', but explicit update is safer if default wasn't applied to old rows in some DBs)
        # SQLite ADD COLUMN with DEFAULT handles existing rows.
        
        logger.info("Migration 003 successful")
    except Exception as e:
        # Ignore if column already exists (idempotency)
        if "duplicate column name" in str(e).lower():
            logger.info("Migration 003: Column already exists, skipping.")
        else:
            raise

async def downgrade(conn):
    """Remove hmac_key_version column."""
    logger.warning("Downgrade not fully supported for SQLite (requires table recreation). Skipping.")
    pass

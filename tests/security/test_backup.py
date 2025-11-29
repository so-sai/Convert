
import pytest
import asyncio
import os
import gc
import aiosqlite
from pathlib import Path
from src.core.services.backup import create_backup, restore_backup

TEST_PASSKEY = "TestPass123!"

@pytest.fixture
def backup_paths(tmp_path):
    db_path = tmp_path / "test_vault.db"
    backup_path = tmp_path / "backup.cvbak"
    return db_path, backup_path

async def force_close_db():
    gc.collect()
    await asyncio.sleep(1.0) # Wait for Windows

@pytest.mark.asyncio
async def test_backup_create_restore_flow(backup_paths):
    db_path, backup_path = backup_paths

    # Explicit Connection Management
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=DELETE")
    await db.execute("CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, content TEXT)")
    await db.execute("INSERT INTO notes (id, content) VALUES ('note1', 'Secret Content')")
    await db.commit()
    await db.close() # <--- EXPLICIT CLOSE
    
    await force_close_db()

    # Backup
    assert await create_backup(db_path, TEST_PASSKEY, backup_path) is True

    # Modify DB
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=DELETE")
    await db.execute("DELETE FROM notes")
    await db.commit()
    await db.close() # <--- EXPLICIT CLOSE
    
    await force_close_db()

    # Restore
    assert await restore_backup(backup_path, TEST_PASSKEY, db_path) is True

    # Verify
    db = await aiosqlite.connect(db_path)
    async with db.execute("SELECT content FROM notes WHERE id='note1'") as cursor:
        row = await cursor.fetchone()
        assert row[0] == 'Secret Content'
    await db.close()

@pytest.mark.asyncio
async def test_torture_overflow_attack(backup_paths):
    db_path, backup_path = backup_paths
    large_payload = "A" * 70000

    # 1. Setup Data
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=DELETE")
    await db.execute("CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, content TEXT)")
    await db.execute("INSERT INTO notes (id, content) VALUES ('large_note', ?)", (large_payload,))
    await db.commit()
    await db.close() # <--- EXPLICIT CLOSE IS KING
    
    await force_close_db()

    # 2. Backup
    assert await create_backup(db_path, TEST_PASSKEY, backup_path) is True

    # 3. Restore (Targeting the same file)
    # On Windows, we sometimes need to help shutil.move by deleting target first
    # BUT restore_backup already does unlink().
    # The issue is unlink() fails if handle is open.
    # force_close_db() above should handle it.
    
    assert await restore_backup(backup_path, TEST_PASSKEY, db_path) is True

    # 4. Verify
    db = await aiosqlite.connect(db_path)
    async with db.execute("SELECT content FROM notes WHERE id='large_note'") as cursor:
        row = await cursor.fetchone()
        assert row[0] == large_payload
    await db.close()

@pytest.mark.asyncio
async def test_wrong_passkey(backup_paths):
    db_path, backup_path = backup_paths
    
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=DELETE")
    await db.execute("CREATE TABLE IF NOT EXISTS notes (id TEXT)")
    await db.close()
    await force_close_db()

    await create_backup(db_path, TEST_PASSKEY, backup_path)
    
    with pytest.raises(Exception):
        await restore_backup(backup_path, "WRONG_PASS", db_path)

@pytest.mark.asyncio
async def test_corrupted_backup(backup_paths):
    db_path, backup_path = backup_paths
    
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=DELETE")
    await db.execute("CREATE TABLE IF NOT EXISTS notes (id TEXT)")
    await db.close()
    await force_close_db()

    await create_backup(db_path, TEST_PASSKEY, backup_path)
    await force_close_db()
    
    with open(backup_path, "r+b") as f:
        f.seek(100)
        f.write(b"TRASH")
        
    with pytest.raises(Exception):
        await restore_backup(backup_path, TEST_PASSKEY, db_path)

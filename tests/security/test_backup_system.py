import pytest
import asyncio
from pathlib import Path
import tempfile
import os

from src.core.services.backup import (
    create_backup,
    restore_backup,
    BackupCryptoError,
    BackupIntegrityError,
    secure_wipe_file
)

TEST_PASSKEY = "SecurePass123!"

@pytest.fixture
def test_db(tmp_path):
    """Create a test database file"""
    db_path = tmp_path / "test.db"
    # Create a dummy database with some content
    with open(db_path, 'wb') as f:
        f.write(b"SQLite format 3\x00" + os.urandom(1000))
    return db_path

@pytest.fixture
def backup_path(tmp_path):
    """Path for backup file"""
    return tmp_path / "test_backup.cvbak"

@pytest.mark.asyncio
async def test_backup_create_and_restore(test_db, backup_path, tmp_path):
    """Test complete backup and restore cycle"""
    # Create backup
    result = await create_backup(test_db, TEST_PASSKEY, backup_path)
    assert result is True
    assert backup_path.exists()
    assert backup_path.stat().st_size > 0
    
    # Restore backup
    restored_db = tmp_path / "restored.db"
    result = await restore_backup(backup_path, TEST_PASSKEY, restored_db)
    assert result is True
    assert restored_db.exists()
    
    # Verify content matches
    with open(test_db, 'rb') as f1, open(restored_db, 'rb') as f2:
        assert f1.read() == f2.read()

@pytest.mark.asyncio
async def test_wrong_passkey_fails(test_db, backup_path, tmp_path):
    """Test that wrong passkey fails restore"""
    # Create backup
    await create_backup(test_db, TEST_PASSKEY, backup_path)
    
    # Try to restore with wrong passkey
    restored_db = tmp_path / "restored.db"
    with pytest.raises(BackupIntegrityError):
        await restore_backup(backup_path, "WrongPassword", restored_db)

@pytest.mark.asyncio
async def test_corrupted_backup_fails(test_db, backup_path, tmp_path):
    """Test that corrupted backup file fails restore"""
    # Create backup
    await create_backup(test_db, TEST_PASSKEY, backup_path)
    
    # Corrupt the backup file
    with open(backup_path, 'r+b') as f:
        f.seek(100)
        f.write(b'\xFF' * 10)
    
    # Try to restore
    restored_db = tmp_path / "restored.db"
    with pytest.raises(BackupIntegrityError):
        await restore_backup(backup_path, TEST_PASSKEY, restored_db)

@pytest.mark.asyncio
async def test_large_file_backup(tmp_path, backup_path):
    """Test backup of larger file (70KB to test chunking)"""
    large_db = tmp_path / "large.db"
    # Create 70KB file
    with open(large_db, 'wb') as f:
        f.write(b"SQLite format 3\x00" + os.urandom(70000))
    
    # Backup and restore
    result = await create_backup(large_db, TEST_PASSKEY, backup_path)
    assert result is True
    
    restored_db = tmp_path / "restored_large.db"
    result = await restore_backup(backup_path, TEST_PASSKEY, restored_db)
    assert result is True
    
    # Verify sizes match
    assert large_db.stat().st_size == restored_db.stat().st_size

def test_secure_wipe(tmp_path):
    """Test secure file wiping"""
    test_file = tmp_path / "sensitive.txt"
    test_file.write_text("Sensitive data")
    
    assert test_file.exists()
    secure_wipe_file(test_file)
    assert not test_file.exists()

@pytest.mark.asyncio
async def test_progress_callback(test_db, backup_path):
    """Test that progress callback is called"""
    progress_updates = []
    
    def callback(percent, message):
        progress_updates.append((percent, message))
    
    await create_backup(test_db, TEST_PASSKEY, backup_path, callback)
    
    # Verify we got progress updates
    assert len(progress_updates) > 0
    assert progress_updates[0][0] == 0  # Started at 0%
    assert progress_updates[-1][0] == 100  # Ended at 100%

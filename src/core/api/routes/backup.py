"""
Backup API Routes - Bridge Layer for Tauri Frontend
Connects frontend commands to src.core.services.backup
"""
import asyncio
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Import the actual backup implementation
from src.core.services.backup import create_backup, restore_backup

# Placeholder for DB path - should come from config
DB_PATH = Path("data/vault.db")


class SecureString(str):
    """Wrapper for sensitive strings (passkeys)"""
    def __repr__(self):
        return "SecureString(***)"


class BackupCreateRequest(BaseModel):
    passkey: str
    output_path: str


class BackupRestoreRequest(BaseModel):
    passkey: str
    backup_path: str


class BackupStatusResponse(BaseModel):
    notes_count: int
    last_backup_ts: Optional[int]
    db_size_bytes: int
    is_safe_mode: bool
    schema_version: int = 1


async def cmd_backup_create_snapshot(passkey: str, output_path: str) -> bool:
    """
    Tauri Command: Create encrypted backup
    """
    try:
        await create_backup(DB_PATH, passkey, Path(output_path))
        return True
    except Exception as e:
        raise RuntimeError(f"Backup creation failed: {e}")


async def cmd_backup_restore_from_file(passkey: str, backup_path: str) -> bool:
    """
    Tauri Command: Restore from encrypted backup
    """
    try:
        await restore_backup(Path(backup_path), passkey, DB_PATH)
        return True
    except Exception as e:
        raise RuntimeError(f"Backup restore failed: {e}")


async def cmd_backup_get_status() -> BackupStatusResponse:
    """
    Tauri Command: Get backup status for UI
    """
    # TODO: Implement actual status check
    # This is a placeholder implementation
    try:
        import nacl.bindings
        is_safe_mode = False
    except ImportError:
        is_safe_mode = True
    
    return BackupStatusResponse(
        notes_count=0,  # TODO: Query from database
        last_backup_ts=None,  # TODO: Get from backup manifest
        db_size_bytes=0,  # TODO: Get actual DB size
        is_safe_mode=is_safe_mode,
        schema_version=1
    )

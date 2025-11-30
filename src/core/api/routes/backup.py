from pathlib import Path
from typing import Dict, Type, Any
import os
import structlog

# Cố gắng import các Exception từ Service Layer
try:
    from src.core.services.backup import (
        BackupCryptoUnavailableError,
        BackupIntegrityError,
        BackupCryptoError,
        BackupError
    )
except ImportError:
    # Fallback dummy classes
    class BackupError(Exception): pass
    class BackupCryptoUnavailableError(BackupError): pass
    class BackupIntegrityError(BackupError): pass
    class BackupCryptoError(BackupError): pass

logger = structlog.get_logger()

# --- CLASS SECURE STRING (FIXED) ---
class SecureString:
    def __init__(self, value: str):
        self._value = value
    
    def get_bytes(self) -> bytes:
        return self._value.encode('utf-8')
    
    # FIX: Trả về mặt nạ khi bị ép kiểu thành string
    def __str__(self):
        return "********"
    
    # FIX: Trả về mặt nạ khi in object trong list/debug
    def __repr__(self):
        return "********"
    
    def __del__(self):
        if hasattr(self, '_value'):
            self._value = '0' * len(self._value)

class BackupCreateRequest:
    def __init__(self, passkey: SecureString, output_path: str):
        self.passkey = passkey
        self.output_path = output_path

class BackupRestoreRequest:
    def __init__(self, passkey: SecureString, backup_path: str):
        self.passkey = passkey
        self.backup_path = backup_path

class BackupStatusResponse:
    def __init__(self, available: bool, provider: str = "", backup_count: int = 0):
        self.available = available
        self.provider = provider
        self.backup_count = backup_count

DB_PATH = Path("mds_eternal.db")

# --- ERROR MAPPING ---
ERROR_MAPPING: Dict[Type[Exception], str] = {
    BackupCryptoUnavailableError: "ERR_AUTH_FAILED",
    BackupIntegrityError: "ERR_AUTH_FAILED",
    BackupCryptoError: "ERR_AUTH_FAILED",
    BackupError: "ERR_IO_LOCKED",
    PermissionError: "ERR_IO_LOCKED",
}

# --- MOCK FUNCTIONS ---
def secure_wipe_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def is_crypto_available() -> bool:
    return True

def get_crypto_provider() -> Any:
    class DefaultProvider:
        name = "SodiumBackend"
    return DefaultProvider()

# Mock logic
def create_backup(passkey: str, output_path: str):
    with open(output_path, 'w') as f:
        f.write("MOCK_BACKUP_DATA")

def restore_backup(passkey: str, backup_path: str, restore_path: str):
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    pass

class BridgeResponse:
    def __init__(self, success: bool, message: str = "", error_code: str = None):
        self.success = success
        self.message = message
        self.error_code = error_code

# --- API IMPLEMENTATION ---
async def cmd_backup_create_snapshot(request: BackupCreateRequest):
    logger.info(f"Creating backup to {request.output_path}")
    try:
        create_backup(request.passkey._value, request.output_path)
        return BridgeResponse(success=True, message="created successfully")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        
        err_type = type(e)
        if err_type in ERROR_MAPPING:
             return BridgeResponse(success=False, error_code=ERROR_MAPPING[err_type])
        
        if "Invalid passkey" in str(e):
             return BridgeResponse(success=False, error_code="ERR_AUTH_FAILED")

        return BridgeResponse(success=False, message=str(e))

async def cmd_backup_restore_from_file(request: BackupRestoreRequest):
    logger.info(f"Restoring from {request.backup_path}")
    try:
        restore_backup(request.passkey._value, request.backup_path, str(DB_PATH))
        return BridgeResponse(success=True, message="restored successfully")
    except Exception as e:
        if "Restore failed" in str(e):
             secure_wipe_file("restored_" + DB_PATH.name)
             return BridgeResponse(success=False, error_code="ERR_UNKNOWN")

        err_type = type(e)
        if err_type in ERROR_MAPPING:
            return BridgeResponse(success=False, error_code=ERROR_MAPPING[err_type])
        
        return BridgeResponse(success=False, message=str(e))

async def cmd_backup_get_status():
    available = is_crypto_available()
    provider = ""
    if available:
        prov = get_crypto_provider()
        if prov:
            provider = prov.name
    
    backup_count = 0
    try:
        if DB_PATH.parent.exists():
            backup_count = len(list(DB_PATH.parent.glob("*.cvbak")))
    except Exception:
        pass

    return BackupStatusResponse(available=available, provider=provider, backup_count=backup_count)

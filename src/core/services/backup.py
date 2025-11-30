# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# MODULE: Backup Service (Functional Style)
# COVERAGE: Database backup/restore with encryption
# ------------------------------------------------------------------------------

import os
import shutil
from pathlib import Path
from typing import Optional, Callable
import asyncio

# Crypto imports
try:
    import nacl.secret
    import nacl.utils
    import nacl.pwhash
    HAS_NACL = True
except ImportError:
    HAS_NACL = False


# ------------------------------------------------------------------------------
# EXCEPTIONS
# ------------------------------------------------------------------------------

class BackupError(Exception):
    """Base exception for backup operations."""
    pass


class BackupCryptoError(BackupError):
    """Raised when cryptographic operation fails."""
    pass


class BackupIntegrityError(BackupError):
    """Raised when backup integrity check fails."""
    pass


class BackupCryptoUnavailableError(BackupCryptoError):
    """Raised when crypto library is unavailable."""
    pass


# ------------------------------------------------------------------------------
# BACKUP CREATION
# ------------------------------------------------------------------------------

async def create_backup(
    db_path: Path | str,
    passkey: str,
    output_path: Path | str,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> bool:
    """
    Create an encrypted backup of the database.
    
    Args:
        db_path: Path to the source database file
        passkey: Encryption passkey
        output_path: Path where backup file will be created
        progress_callback: Optional callback(percent, message) for progress updates
    
    Returns:
        bool: True if backup created successfully
    
    Raises:
        BackupCryptoError: If encryption fails
        BackupError: If backup creation fails
    """
    if not HAS_NACL:
        raise BackupCryptoUnavailableError("nacl library not available")
    
    db_path = Path(db_path)
    output_path = Path(output_path)
    
    try:
        if progress_callback:
            progress_callback(0, "Starting backup...")
        
        # Read source database
        with open(db_path, 'rb') as f:
            plaintext = f.read()
        
        if progress_callback:
            progress_callback(25, "Encrypting...")
        
        # Derive encryption key from passkey
        salt = nacl.utils.random(nacl.pwhash.argon2id.SALTBYTES)
        key = nacl.pwhash.argon2id.kdf(
            size=nacl.secret.SecretBox.KEY_SIZE,
            password=passkey.encode('utf-8'),
            salt=salt,
            opslimit=nacl.pwhash.argon2id.OPSLIMIT_MODERATE,
            memlimit=nacl.pwhash.argon2id.MEMLIMIT_MODERATE
        )
        
        if progress_callback:
            progress_callback(50, "Encrypting data...")
        
        # Encrypt the database content
        box = nacl.secret.SecretBox(key)
        ciphertext = box.encrypt(plaintext)
        
        if progress_callback:
            progress_callback(75, "Writing backup file...")
        
        # Write encrypted backup (salt + ciphertext)
        with open(output_path, 'wb') as f:
            f.write(salt)
            f.write(ciphertext)
        
        if progress_callback:
            progress_callback(100, "Backup complete")
        
        return True
        
    except Exception as e:
        raise BackupError(f"Failed to create backup: {e}")


# ------------------------------------------------------------------------------
# BACKUP RESTORATION
# ------------------------------------------------------------------------------

async def restore_backup(
    backup_path: Path | str,
    passkey: str,
    output_path: Path | str,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> bool:
    """
    Restore a database from an encrypted backup.
    
    Args:
        backup_path: Path to the backup file
        passkey: Decryption passkey
        output_path: Path where database will be restored
        progress_callback: Optional callback(percent, message) for progress updates
    
    Returns:
        bool: True if restore successful
    
    Raises:
        BackupIntegrityError: If decryption fails or backup is corrupted
        BackupError: If restore fails
    """
    if not HAS_NACL:
        raise BackupCryptoUnavailableError("nacl library not available")
    
    backup_path = Path(backup_path)
    output_path = Path(output_path)
    
    try:
        if progress_callback:
            progress_callback(0, "Reading backup...")
        
        # Read encrypted backup
        with open(backup_path, 'rb') as f:
            salt = f.read(nacl.pwhash.argon2id.SALTBYTES)
            ciphertext = f.read()
        
        if progress_callback:
            progress_callback(25, "Deriving key...")
        
        # Derive decryption key from passkey
        key = nacl.pwhash.argon2id.kdf(
            size=nacl.secret.SecretBox.KEY_SIZE,
            password=passkey.encode('utf-8'),
            salt=salt,
            opslimit=nacl.pwhash.argon2id.OPSLIMIT_MODERATE,
            memlimit=nacl.pwhash.argon2id.MEMLIMIT_MODERATE
        )
        
        if progress_callback:
            progress_callback(50, "Decrypting...")
        
        # Decrypt the backup
        box = nacl.secret.SecretBox(key)
        try:
            plaintext = box.decrypt(ciphertext)
        except Exception as e:
            raise BackupIntegrityError(f"Decryption failed - wrong passkey or corrupted backup: {e}")
        
        if progress_callback:
            progress_callback(75, "Writing database...")
        
        # Write restored database
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        if progress_callback:
            progress_callback(100, "Restore complete")
        
        return True
        
    except BackupIntegrityError:
        raise
    except Exception as e:
        raise BackupError(f"Failed to restore backup: {e}")


# ------------------------------------------------------------------------------
# SECURE FILE DELETION
# ------------------------------------------------------------------------------

def secure_wipe_file(path: Path | str) -> None:
    """
    Securely wipe a file by overwriting with random data before deletion.
    
    Args:
        path: Path to the file to wipe
    """
    path = Path(path)
    
    if not path.exists():
        return
    
    try:
        # Get file size
        file_size = path.stat().st_size
        
        # Overwrite with random data (3 passes)
        with open(path, 'r+b') as f:
            for _ in range(3):
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
        
        # Delete the file
        path.unlink()
        
    except Exception as e:
        # If secure wipe fails, at least try to delete
        try:
            path.unlink()
        except:
            pass

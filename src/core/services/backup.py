# HASH: BACKUP_OMEGA_FINAL_V7_ROBUST_RETRY
# IMPLEMENTS: TASK-5.2-VACUUM-ATOMIC
# STATUS: PRODUCTION READY (WINDOWS HARDENED)
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# ------------------------------------------------------------------------------

import asyncio
import zlib
import uuid
import os
import time
import sqlite3
import shutil
import struct
from pathlib import Path
from typing import Optional, Callable

# Import Crypto Library safely
try:
    import nacl.bindings
    import nacl.utils
    HAS_NACL = True
except ImportError:
    HAS_NACL = False

# Import Omega Security Constants
try:
    from ..utils.security import (
        get_crypto_provider, 
        ARGON2_BACKUP_MEMLIMIT, 
        ARGON2_BACKUP_OPSLIMIT, 
        ARGON2_BACKUP_PARALLELISM
    )
except ImportError:
    ARGON2_BACKUP_MEMLIMIT = 134217728
    ARGON2_BACKUP_OPSLIMIT = 3
    ARGON2_BACKUP_PARALLELISM = 4
    def get_crypto_provider(): return None

# --- CUSTOM EXCEPTIONS ---
class BackupCryptoError(Exception): pass
class BackupIntegrityError(BackupCryptoError): pass
class BackupCryptoUnavailableError(BackupCryptoError): pass

# --- CORE LOGIC ---

def derive_backup_key(passkey: str, salt: bytes) -> bytes:
    provider = get_crypto_provider()
    if provider and hasattr(provider, 'derive_key'):
        return provider.derive_key(
            passkey=passkey,
            salt=salt,
            opslimit=ARGON2_BACKUP_OPSLIMIT,
            memlimit=ARGON2_BACKUP_MEMLIMIT,
            parallelism=ARGON2_BACKUP_PARALLELISM
        )
    else:
        if not HAS_NACL: raise BackupCryptoUnavailableError("PyNaCl missing")
        return nacl.bindings.crypto_pwhash_alg_argon2id13(
            nacl.bindings.crypto_secretstream_xchacha20poly1305_KEYBYTES,
            passkey.encode('utf-8'),
            salt,
            ARGON2_BACKUP_OPSLIMIT,
            ARGON2_BACKUP_MEMLIMIT,
            nacl.bindings.crypto_pwhash_alg_argon2id13_ALG_ARGON2ID13
        )

def secure_wipe_file(path: Path) -> None:
    if not path.exists(): return
    try:
        file_size = path.stat().st_size
        with open(path, "rb+") as f:
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())
        temp_name = path.parent / f"{uuid.uuid4()}.tmp"
        path.rename(temp_name)
        temp_name.unlink()
    except (OSError, IOError):
        try: path.unlink()
        except OSError: pass

def _execute_vacuum_into(source_db: Path, target_db: Path) -> None:
    source_uri = f"file:{source_db.resolve()}?mode=ro"
    target_path = str(target_db.resolve())
    try:
        with sqlite3.connect(source_uri, uri=True) as conn:
            conn.execute(f"VACUUM INTO '{target_path}'")
    except sqlite3.Error as e:
        raise BackupCryptoError(f"Database snapshot failed: {str(e)}") from e

async def create_backup(
    db_path: Path, 
    passkey: str, 
    output_path: Path,
    progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
    
    if not HAS_NACL: raise BackupCryptoUnavailableError("PyNaCl missing")
    if not db_path.exists(): raise BackupCryptoError("Database not found")

    temp_dir = output_path.parent / ".backup_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_db_path = temp_dir / f"snapshot_{uuid.uuid4()}.db"
    backup_key = None
    
    try:
        if progress_callback: progress_callback(10, "Creating atomic snapshot...")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _execute_vacuum_into, db_path, temp_db_path)

        if progress_callback: progress_callback(30, "Encrypting snapshot...")

        salt = nacl.utils.random(16)
        backup_key = derive_backup_key(passkey, salt)
        
        state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
        header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, backup_key)

        with open(output_path, 'wb') as f_out:
            f_out.write(b'CVBAK002')
            f_out.write(salt)
            f_out.write(header)

            compressor = zlib.compressobj(level=6)
            with open(temp_db_path, 'rb') as f_in:
                total_size = temp_db_path.stat().st_size
                processed = 0
                while True:
                    chunk = f_in.read(1024 * 1024)
                    is_final = not chunk
                    
                    data = compressor.compress(chunk) if chunk else compressor.flush()

                    if data or is_final:
                        tag = (nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_FINAL if is_final 
                               else nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE)
                        
                        encrypted = nacl.bindings.crypto_secretstream_xchacha20poly1305_push(state, data, tag=tag)
                        f_out.write(struct.pack('<I', len(encrypted)))
                        f_out.write(encrypted)
                    
                    if chunk:
                        processed += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = 30 + (processed / total_size) * 70
                            progress_callback(int(progress), "Encrypting data...")

                    if is_final: break
        
        if progress_callback: progress_callback(100, "Backup completed!")
        return True

    except Exception as e:
        if output_path.exists(): output_path.unlink()
        raise BackupCryptoError(f"Backup failed: {str(e)}") from e
    finally:
        if temp_db_path.exists(): secure_wipe_file(temp_db_path)
        try: shutil.rmtree(temp_dir, ignore_errors=True)
        except: pass
        if backup_key:
            try: nacl.bindings.sodium_memzero(backup_key)
            except: pass

async def restore_backup(
    backup_path: Path,
    passkey: str, 
    output_db_path: Path,
    progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
    
    if not HAS_NACL: raise BackupCryptoUnavailableError("PyNaCl missing")
    if not backup_path.exists(): raise BackupCryptoError("Backup file not found")

    temp_dir = output_db_path.parent / f".restore_temp_{uuid.uuid4()}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_output_path = temp_dir / "restored.db"
    backup_key = None

    try:
        if progress_callback: progress_callback(10, "Validating header...")
        
        with open(backup_path, 'rb') as f_in:
            if f_in.read(8) != b'CVBAK002': raise BackupIntegrityError("Invalid Format")
            salt = f_in.read(16)
            header = f_in.read(24)
            
            backup_key = derive_backup_key(passkey, salt)
            
            state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
            try:
                nacl.bindings.crypto_secretstream_xchacha20poly1305_init_pull(state, header, backup_key)
            except Exception:
                raise BackupCryptoError("Invalid Header/Key")

            decompressor = zlib.decompressobj()
            if progress_callback: progress_callback(30, "Decrypting...")

            with open(temp_output_path, 'wb') as f_out:
                while True:
                    len_bytes = f_in.read(4)
                    if not len_bytes: break
                    
                    chunk_len = struct.unpack('<I', len_bytes)[0]
                    chunk = f_in.read(chunk_len)
                    
                    if len(chunk) != chunk_len: raise BackupIntegrityError("Truncated file")

                    try:
                        decrypted, tag = nacl.bindings.crypto_secretstream_xchacha20poly1305_pull(state, chunk)
                    except Exception:
                        raise BackupIntegrityError("Decryption failed")

                    f_out.write(decompressor.decompress(decrypted))
                    
                    if tag == nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_FINAL:
                        f_out.write(decompressor.flush())
                        break

        with open(temp_output_path, 'rb') as f:
            if not f.read(16).startswith(b'SQLite format 3'):
                raise BackupIntegrityError("Invalid SQLite database restored")

        # --- WINDOWS ROBUST REPLACE ---
        # Retry mechanism for file replacement
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # On Windows, os.replace is atomic but fails if open handles exist
                # Try explicit unlink first if exists
                if output_db_path.exists():
                    try: output_db_path.unlink()
                    except OSError: pass # Ignore if locked, try replace
                
                shutil.move(str(temp_output_path), str(output_db_path))
                break # Success
            except OSError:
                if attempt == max_retries - 1: raise # Give up
                time.sleep(0.5) # Wait for handles to close
        # ------------------------------

        if progress_callback: progress_callback(100, "Restore Success!")
        return True

    except Exception as e:
        raise BackupCryptoError(f"Restore failed: {str(e)}") from e
    finally:
        if temp_output_path.exists(): secure_wipe_file(temp_output_path)
        try: shutil.rmtree(temp_dir, ignore_errors=True)
        except: pass
        if backup_key:
            try: nacl.bindings.sodium_memzero(backup_key)
            except: pass

# API Export
__all__ = ['create_backup', 'restore_backup', 'secure_wipe_file', 'BackupCryptoError', 'BackupIntegrityError']

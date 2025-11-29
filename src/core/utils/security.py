# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import logging
import sys
from typing import Tuple, Optional
from ..security.provider import CryptoProvider

logger = logging.getLogger(__name__)

# OMEGA ARCH CONSTANTS - 128MB SECURITY CORE
ARGON2_BACKUP_MEMLIMIT = 134217728  # 128 MiB - OMEGA STANDARD
ARGON2_BACKUP_OPSLIMIT = 3
ARGON2_BACKUP_PARALLELISM = 4

class SecurityError(Exception):
    """Critical Security Failure."""
    pass

class CryptoUnavailableError(SecurityError):
    """Raised when cryptographic operations are unavailable"""
    pass

class SodiumBackend(CryptoProvider):
    """Primary Backend using PyNaCl (libsodium) - OMEGA IMPLEMENTATION"""
    
    def __init__(self):
        self._available = False
        self._initialize()
    
    def _initialize(self):
        """Lazy import to prevent crashes"""
        try:
            import nacl.bindings
            import nacl.utils
            from argon2 import low_level
            
            self.nacl = nacl
            self._argon2 = low_level
            self._available = True
            logger.info("✅ SodiumBackend initialized successfully")
        except (ImportError, OSError) as e:
            self._available = False
            logger.warning(f"⚠️ SodiumBackend failed: {e}")
    
    def is_available(self) -> bool:
        return self._available
    
    def derive_key(self, passkey: str, salt: bytes, opslimit: int, memlimit: int, parallelism: int) -> bytes:
        if not self.is_available():
            raise CryptoUnavailableError("SodiumBackend not available")
        
        try:
            # Convert memlimit from bytes to KiB for argon2-cffi
            memory_cost_kib = memlimit // 1024
            
            key = self._argon2.hash_secret_raw(
                secret=passkey.encode('utf-8'),
                salt=salt,
                time_cost=opslimit,
                memory_cost=memory_cost_kib,
                parallelism=parallelism,
                hash_len=32,
                type=self._argon2.Type.ID
            )
            return key
        except Exception as e:
            raise CryptoUnavailableError(f"Key derivation failed: {str(e)}") from e
    
    def encrypt_stream_init(self, key: bytes) -> Tuple[any, bytes]:
        if not self.is_available():
            raise CryptoUnavailableError("SodiumBackend not available")
        
        try:
            state = self.nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
            header = self.nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, key)
            return state, header
        except Exception as e:
            raise CryptoUnavailableError(f"Stream init failed: {str(e)}") from e
    
    def encrypt_stream_push(self, state: any, data: bytes, tag: int) -> bytes:
        if not self.is_available():
            raise CryptoUnavailableError("SodiumBackend not available")
        
        try:
            ciphertext = self.nacl.bindings.crypto_secretstream_xchacha20poly1305_push(state, data, tag=tag)
            return ciphertext
        except Exception as e:
            raise CryptoUnavailableError(f"Stream push failed: {str(e)}") from e
    
    def decrypt_stream_init(self, header: bytes, key: bytes) -> any:
        if not self.is_available():
            raise CryptoUnavailableError("SodiumBackend not available")
        
        try:
            state = self.nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
            self.nacl.bindings.crypto_secretstream_xchacha20poly1305_init_pull(state, header, key)
            return state
        except Exception as e:
            raise CryptoUnavailableError(f"Stream decrypt init failed: {str(e)}") from e
    
    def decrypt_stream_pull(self, state: any, ciphertext: bytes) -> Tuple[bytes, int]:
        if not self.is_available():
            raise CryptoUnavailableError("SodiumBackend not available")
        
        try:
            plaintext, tag = self.nacl.bindings.crypto_secretstream_xchacha20poly1305_pull(state, ciphertext)
            return plaintext, tag
        except Exception as e:
            raise CryptoUnavailableError(f"Stream pull failed: {str(e)}") from e
    
    def get_stream_tags(self) -> dict:
        if not self.is_available():
            raise CryptoUnavailableError("SodiumBackend not available")
        
        return {
            'TAG_MESSAGE': self.nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_MESSAGE,
            'TAG_FINAL': self.nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_FINAL,
            'TAG_REKEY': self.nacl.bindings.crypto_secretstream_xchacha20poly1305_TAG_REKEY
        }

class SafeModeBackend(CryptoProvider):
    """Fallback Backend - Prevents crashes but blocks operations"""
    
    def is_available(self) -> bool:
        return False
    
    def derive_key(self, *args, **kwargs) -> bytes:
        raise CryptoUnavailableError(
            "CRITICAL: Argon2 library missing. Cannot derive keys safely. "
            "Please install PyNaCl and argon2-cffi packages."
        )
    
    def encrypt_stream_init(self, *args, **kwargs) -> Tuple[any, bytes]:
        raise CryptoUnavailableError(
            "CRITICAL: PyNaCl library missing. Cannot initialize encryption stream. "
            "Vault operations are disabled. Please install required security packages."
        )
    
    def encrypt_stream_push(self, *args, **kwargs) -> bytes:
        raise CryptoUnavailableError(
            "CRITICAL: PyNaCl library missing. Cannot encrypt stream data. "
            "Vault operations are disabled. Please install required security packages."
        )
    
    def decrypt_stream_init(self, *args, **kwargs) -> any:
        raise CryptoUnavailableError(
            "CRITICAL: PyNaCl library missing. Cannot initialize decryption stream. "
            "Vault operations are disabled. Please install required security packages."
        )
    
    def decrypt_stream_pull(self, *args, **kwargs) -> Tuple[bytes, int]:
        raise CryptoUnavailableError(
            "CRITICAL: PyNaCl library missing. Cannot decrypt stream data. "
            "Vault operations are disabled. Please install required security packages."
        )
    
    def get_stream_tags(self) -> dict:
        raise CryptoUnavailableError(
            "CRITICAL: PyNaCl library missing. Cannot get stream tags. "
            "Vault operations are disabled. Please install required security packages."
        )

# Global provider instance
_PROVIDER_INSTANCE = None

def get_crypto_provider() -> CryptoProvider:
    """Factory method to get active CryptoProvider"""
    global _PROVIDER_INSTANCE
    
    if _PROVIDER_INSTANCE is not None:
        return _PROVIDER_INSTANCE
    
    try:
        _PROVIDER_INSTANCE = SodiumBackend()
        if _PROVIDER_INSTANCE.is_available():
            logger.info("✅ OMEGA CORE: SodiumBackend (128MB) - ONLINE")
            return _PROVIDER_INSTANCE
        else:
            raise CryptoUnavailableError("SodiumBackend not available")
    except (ImportError, OSError, CryptoUnavailableError) as e:
        logger.critical("🚨 OMEGA CORE: Entering Safe Mode - Vault Operations DISABLED")
        _PROVIDER_INSTANCE = SafeModeBackend()
        return _PROVIDER_INSTANCE

def is_crypto_available() -> bool:
    """Check if cryptographic operations are available"""
    provider = get_crypto_provider()
    return provider.is_available()

def get_crypto_status() -> dict:
    """Get detailed crypto provider status"""
    provider = get_crypto_provider()
    return {
        "provider": "SodiumBackend" if provider.is_available() else "SafeModeBackend",
        "available": provider.is_available(),
        "argon2_params": {
            "backup_opslimit": ARGON2_BACKUP_OPSLIMIT,
            "backup_memlimit": ARGON2_BACKUP_MEMLIMIT,
            "backup_parallelism": ARGON2_BACKUP_PARALLELISM
        }
    }

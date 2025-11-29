# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Tuple, Optional

class CryptoProvider(ABC):
    """Abstract Base Class for Cryptographic Operations."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the backend is fully operational."""
        pass
    
    @abstractmethod
    def derive_key(self, passkey: str, salt: bytes, opslimit: int, memlimit: int, parallelism: int) -> bytes:
        """Derive key using Argon2id."""
        pass
    
    @abstractmethod
    def encrypt_stream_init(self, key: bytes) -> Tuple[any, bytes]:
        """Initialize encryption stream. Returns (state, header)."""
        pass
    
    @abstractmethod
    def encrypt_stream_push(self, state: any, data: bytes, tag: int) -> bytes:
        """Encrypt stream chunk."""
        pass
    
    @abstractmethod
    def decrypt_stream_init(self, header: bytes, key: bytes) -> any:
        """Initialize decryption stream. Returns state."""
        pass
    
    @abstractmethod
    def decrypt_stream_pull(self, state: any, ciphertext: bytes) -> Tuple[bytes, int]:
        """Decrypt stream chunk. Returns (plaintext, tag)."""
        pass
    
    @abstractmethod
    def get_stream_tags(self) -> dict:
        """Return stream tag constants."""
        pass

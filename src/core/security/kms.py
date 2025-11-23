from typing import Optional
from src.core.security.key_derivation import KeyDerivation
from src.core.security.encryption import EncryptionService
import nacl.utils

from typing import Optional
from src.core.security.key_derivation import KeyDerivation
from src.core.security.encryption import EncryptionService
from src.core.security.storage import KeyStorage
import nacl.utils

class KMS:
    def __init__(self, db_path: str, provider: str = "pynacl"):
        self.db_path = db_path
        self.provider = provider
        self.storage = KeyStorage(db_path)
        self.master_key: Optional[bytes] = None

    async def initialize_vault(self, passkey: str) -> None:
        salt = nacl.utils.random(16)
        self.master_key = KeyDerivation.derive_master_key(passkey, salt)
        if not self.master_key:
            raise RuntimeError("Failed to derive Master Key")
            
        # Generate and encrypt DEK
        dek = nacl.utils.random(32)
        encrypted_dek = EncryptionService.wrap_dek(self.master_key, dek)
        
        # Store in DB
        self.storage.write(salt, encrypted_dek)

    async def unlock_vault(self, passkey: str) -> None:
        try:
            salt, encrypted_dek = self.storage.read()
        except ValueError as e:
            raise RuntimeError(f"Vault not initialized: {e}")
            
        self.master_key = KeyDerivation.derive_master_key(passkey, salt)
        if not self.master_key:
            raise RuntimeError("Failed to derive Master Key")
            
        # Verify DEK can be decrypted (integrity check)
        try:
            EncryptionService.unwrap_dek(self.master_key, encrypted_dek)
        except Exception:
            self.master_key = None
            raise ValueError("Invalid passkey or corrupted vault")

    def encrypt_dek(self, dek: bytes) -> bytes:
        if not self.master_key:
            raise RuntimeError("KMS not initialized")
        return EncryptionService.wrap_dek(self.master_key, dek)

    def decrypt_dek(self, wrapped_dek: bytes) -> bytes:
        if not self.master_key:
            raise RuntimeError("KMS not initialized")
        return EncryptionService.unwrap_dek(self.master_key, wrapped_dek)
    
    async def close(self):
        self.master_key = None

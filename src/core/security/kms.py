from typing import Optional
from src.core.security.key_derivation import KeyDerivation
from src.core.security.encryption import EncryptionService
import nacl.utils

class KMS:
    def __init__(self, db_path: str, provider: str = "pynacl"):
        self.db_path = db_path
        self.provider = provider
        self.master_key: Optional[bytes] = None

    async def initialize_vault(self, passkey: str) -> None:
        salt = nacl.utils.random(16)
        self.master_key = KeyDerivation.derive_master_key(passkey, salt)
        if not self.master_key:
            raise RuntimeError("Failed to derive Master Key")

    async def unlock_vault(self, passkey: str) -> None:
        await self.initialize_vault(passkey)

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

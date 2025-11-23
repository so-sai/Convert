# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import nacl.pwhash
import nacl.utils
import logging
from typing import Optional, Tuple
from pathlib import Path
from .storage import KeyStorage
from .encryption import EncryptionService

logger = logging.getLogger(__name__)

class KMS:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._epoch_secret: Optional[bytes] = None
        self._storage = KeyStorage(db_path)
        # OWASP 2025 Standard
        self.OPS = 2
        self.MEM = 19 * 1024 * 1024 # 19 MiB
        self.KEY_SIZE = 32

    async def initialize_vault(self, passkey: str) -> None:
        await self._storage.ensure_table_exists()
        if await self._storage.load_keys(): raise RuntimeError("Vault already initialized")

        salt = nacl.utils.random(nacl.pwhash.SALTBYTES)
        # Derive KEK from Passkey
        kek = nacl.pwhash.argon2id.kdf(self.KEY_SIZE, passkey.encode(), salt, opslimit=self.OPS, memlimit=self.MEM)
        
        # Generate Epoch Secret (Root of Trust for DEK & HMAC)
        epoch_secret = nacl.utils.random(self.KEY_SIZE)
        
        # Wrap Epoch Secret
        enc_blob = EncryptionService.wrap_dek(kek, epoch_secret)
        
        # Save (Store blob in enc_dek, empty nonce as it's inside blob now)
        await self._storage.save_keys(salt, enc_blob, b'', self.OPS, self.MEM)
        self._epoch_secret = epoch_secret

    async def unlock_vault(self, passkey: str) -> bool:
        await self._storage.ensure_table_exists()
        row = await self._storage.load_keys()
        if not row: return False
        salt, enc_blob, _, ops, mem = row
        
        try:
            kek = nacl.pwhash.argon2id.kdf(self.KEY_SIZE, passkey.encode(), salt, opslimit=ops, memlimit=mem)
            self._epoch_secret = EncryptionService.unwrap_dek(kek, enc_blob)
            return True
        except Exception:
            return False

    def get_keys(self) -> Tuple[bytes, bytes]:
        """Returns (DEK, HMAC_KEY)"""
        if not self._epoch_secret: raise Exception("Vault Locked")
        return EncryptionService.derive_keys(self._epoch_secret)

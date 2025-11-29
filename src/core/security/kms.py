"""
Key Management System (KMS) - Omega Standard
Status: FIXED (Synchronous API + Correct NaCl Constants)
"""
import os
import json
from typing import Optional
from pathlib import Path
from dataclasses import dataclass, asdict

try:
    from nacl.secret import SecretBox
    from nacl.utils import random
    from nacl.pwhash import argon2id
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

@dataclass
class KeyStore:
    salt: str
    nonce: str
    ciphertext: str
    algo: str = "xchacha20-poly1305"
    kdf: str = "argon2id"

class KMS:
    def __init__(self, storage_path: str = "security/keys.json"):
        if not os.path.isabs(storage_path):
            base = Path.cwd()
            # Xử lý path khi chạy test
            if base.name in ['tests', 'security', 'unit']: 
                base = base.parent if base.name != 'tests' else base.parent
            self.storage_path = base / storage_path
        else:
            self.storage_path = Path(storage_path)
            
        self._master_key: Optional[bytes] = None
        self._is_unlocked: bool = False

    @property
    def is_unlocked(self) -> bool:
        return self._is_unlocked

    @property
    def master_key(self) -> Optional[bytes]:
        return self._master_key

    def initialize(self, passphrase: str) -> bool:
        if not HAS_CRYPTO: raise RuntimeError("Crypto libraries missing.")
        if self.storage_path.exists(): raise FileExistsError("KMS already initialized.")
        
        # FIX: Dùng argon2id.SALTBYTES thay vì nacl.pwhash.SALTBYTES
        salt = random(argon2id.SALTBYTES)
        master_key = random(32) 
        
        kdf_key = argon2id.kdf(
            SecretBox.KEY_SIZE,
            passphrase.encode('utf-8'),
            salt,
            opslimit=argon2id.OPSLIMIT_MODERATE,
            memlimit=argon2id.MEMLIMIT_MODERATE
        )
        
        box = SecretBox(kdf_key)
        nonce = random(SecretBox.NONCE_SIZE)
        encrypted = box.encrypt(master_key, nonce)
        
        ciphertext = encrypted.ciphertext if hasattr(encrypted, 'ciphertext') else encrypted[len(nonce):]
        
        keystore = KeyStore(
            salt=salt.hex(),
            nonce=nonce.hex(),
            ciphertext=ciphertext.hex()
        )
        self._save_keystore(keystore)
        return True

    def unlock(self, passphrase: str) -> bool:
        if not HAS_CRYPTO: return False
        if not self.storage_path.exists(): return False
            
        try:
            keystore = self._load_keystore()
            salt = bytes.fromhex(keystore.salt)
            nonce = bytes.fromhex(keystore.nonce)
            ciphertext = bytes.fromhex(keystore.ciphertext)
            
            kdf_key = argon2id.kdf(
                SecretBox.KEY_SIZE,
                passphrase.encode('utf-8'),
                salt,
                opslimit=argon2id.OPSLIMIT_MODERATE,
                memlimit=argon2id.MEMLIMIT_MODERATE
            )
            
            box = SecretBox(kdf_key)
            self._master_key = box.decrypt(ciphertext, nonce)
            self._is_unlocked = True
            return True
        except Exception:
            self._is_unlocked = False
            return False

    def _save_keystore(self, keystore: KeyStore):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(asdict(keystore), f, indent=4)

    def _load_keystore(self) -> KeyStore:
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        return KeyStore(**data)

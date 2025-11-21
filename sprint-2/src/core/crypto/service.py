import hashlib
import hmac
from abc import ABC, abstractmethod

class ICryptoService(ABC):
    @abstractmethod
    def encrypt(self, data: bytes) -> tuple[bytes, str, str | None, bytes | None]: pass
    @abstractmethod
    def decrypt(self, ct: bytes, algo: str, kid: str | None, nonce: bytes | None) -> bytes: pass
    @abstractmethod
    def calculate_hmac(self, sid: str, data: bytes) -> str: pass
    @abstractmethod
    def hash_event(self, event_data: bytes) -> bytes: pass

class StdLibCryptoService(ICryptoService):
    def __init__(self, master_key: bytes):
        if len(master_key) < 32: raise ValueError("Key too short")
        self.master_key = master_key
    
    def encrypt(self, data: bytes) -> tuple: return data, "pass-through", "mk_sprint2", None
    def decrypt(self, ct: bytes, algo: str, kid: str | None, nonce: bytes | None) -> bytes: return ct
    def _derive_key(self, sid: str) -> bytes: return hmac.new(self.master_key, f"hmac-key:{sid}".encode(), hashlib.sha256).digest()
    def calculate_hmac(self, sid: str, data: bytes) -> str: return hmac.new(self._derive_key(sid), data, hashlib.sha3_256).hexdigest()
    def hash_event(self, event_data: bytes) -> bytes: return hashlib.sha3_256(event_data).digest()
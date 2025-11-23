import nacl.pwhash
import nacl.utils
from typing import Tuple, Union

class KeyDerivation:
    OPS_LIMIT = nacl.pwhash.argon2id.OPSLIMIT_INTERACTIVE
    MEM_LIMIT = 19 * 1024 * 1024  # 19 MiB (OWASP 2025 Compliant)
    KEY_SIZE = 32

    @staticmethod
    def derive_master_key(passkey: Union[str, bytes], salt: bytes) -> bytes:
        if not isinstance(passkey, bytes):
            passkey_bytes = passkey.encode("utf-8")
        else:
            passkey_bytes = passkey
            
        return nacl.pwhash.argon2id.kdf(
            int(KeyDerivation.KEY_SIZE),
            passkey_bytes,
            salt,
            opslimit=KeyDerivation.OPS_LIMIT,
            memlimit=KeyDerivation.MEM_LIMIT
        )

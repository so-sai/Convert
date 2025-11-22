import nacl.secret
import nacl.utils

class EncryptionService:
    @staticmethod
    def wrap_dek(master_key: bytes, dek: bytes) -> bytes:
        nonce = nacl.utils.random(24)
        box = nacl.secret.Aead(master_key)
        return box.encrypt(dek, nonce=nonce)

    @staticmethod
    def unwrap_dek(master_key: bytes, wrapped_blob: bytes) -> bytes:
        try:
            box = nacl.secret.Aead(master_key)
            return box.decrypt(wrapped_blob)
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {str(e)}")

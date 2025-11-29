# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import nacl.secret
import nacl.utils
import nacl.bindings
import hashlib
import hmac
from typing import Dict, Any, Tuple

NONCE_SIZE = 24

class TamperDetectedError(Exception):
    """Raised when data integrity check fails (HMAC mismatch)."""
    pass

class EncryptionService:
    @staticmethod
    def encrypt_dek(dek: bytes, kek: bytes) -> Dict[str, bytes]:
        """Encrypt DEK using KEK with XChaCha20-Poly1305."""
        nonce = nacl.utils.random(NONCE_SIZE)
        ciphertext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
            dek, None, nonce, kek
        )
        return {"ciphertext": ciphertext, "nonce": nonce}

    @staticmethod
    def decrypt_dek(ciphertext: bytes, nonce: bytes, kek: bytes) -> bytes:
        """Decrypt DEK using KEK."""
        return nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
            ciphertext, None, nonce, kek
        )

    @staticmethod
    def derive_keys(master_secret: bytes) -> Tuple[bytes, bytes]:
        """Derive DEK and HMAC key from master secret using BLAKE2b."""
        dek = hashlib.blake2b(master_secret, digest_size=32, person=b"DEK").digest()
        hmac_key = hashlib.blake2b(master_secret, digest_size=32, person=b"HMAC").digest()
        return dek, hmac_key

    @staticmethod
    def encrypt_event(dek: bytes, hmac_key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt event with Double-MAC protection.
        Returns: (ciphertext, nonce, event_hmac)
        """
        # 1. Calculate HMAC on plaintext (Chain Layer)
        event_hmac = hmac.new(hmac_key, plaintext, hashlib.sha3_256).digest()
        
        # 2. Encrypt with XChaCha20-Poly1305 (AEAD Layer)
        nonce = nacl.utils.random(NONCE_SIZE)
        ciphertext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
            plaintext, None, nonce, dek
        )
        
        return ciphertext, nonce, event_hmac

    @staticmethod
    def decrypt_event(dek: bytes, hmac_key: bytes, ciphertext: bytes, nonce: bytes, event_hmac: bytes) -> bytes:
        """
        Decrypt event and verify Double-MAC.
        Raises TamperDetectedError if HMAC verification fails.
        """
        # 1. Decrypt (AEAD Layer verifies Poly1305 tag)
        try:
            plaintext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                ciphertext, None, nonce, dek
            )
        except Exception as e:
            raise TamperDetectedError(f"AEAD decryption failed: {e}")
        
        # 2. Verify Chain HMAC
        expected_hmac = hmac.new(hmac_key, plaintext, hashlib.sha3_256).digest()
        if not hmac.compare_digest(expected_hmac, event_hmac):
            raise TamperDetectedError("Chain HMAC Mismatch - Data tampered")
        
        return plaintext

    @staticmethod
    def wrap_dek(kek: bytes, dek: bytes) -> bytes:
        """Wrap DEK with KEK (nonce embedded in output)."""
        result = EncryptionService.encrypt_dek(dek, kek)
        # Embed nonce in the blob
        return result["nonce"] + result["ciphertext"]

    @staticmethod
    def unwrap_dek(kek: bytes, wrapped: bytes) -> bytes:
        """Unwrap DEK from wrapped blob."""
        nonce = wrapped[:NONCE_SIZE]
        ciphertext = wrapped[NONCE_SIZE:]
        return EncryptionService.decrypt_dek(ciphertext, nonce, kek)
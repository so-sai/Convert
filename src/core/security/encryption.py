# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

import nacl.secret
import nacl.utils
import nacl.exceptions
import nacl.bindings
import hashlib
import hmac
from typing import Tuple

class TamperDetectedError(Exception):
    """Raised when Integrity Check (Poly1305 or HMAC-SHA3) fails."""
    pass

NONCE_SIZE = 24 # 192-bit XChaCha20 Nonce

class EncryptionService:
    @staticmethod
    def derive_keys(master_secret: bytes) -> Tuple[bytes, bytes]:
        """
        Derive DEK and HMAC_KEY from a single Epoch Secret.
        Uses BLAKE2b as a simple KDF for separation.
        """
        # Key 1: Encryption (DEK) - first 32 bytes
        dek = hashlib.blake2b(master_secret, digest_size=32, person=b'ENC_KEY_').digest()
        # Key 2: Integrity (HMAC) - second 32 bytes
        hmac_key = hashlib.blake2b(master_secret, digest_size=32, person=b'MAC_KEY_').digest()
        return dek, hmac_key

    @staticmethod
    def wrap_dek(master_key: bytes, dek: bytes) -> bytes:
        """Wrap the Epoch Secret using the User Master Key (KEK)."""
        nonce = nacl.utils.random(NONCE_SIZE)
        ciphertext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
            dek, None, nonce, master_key
        )
        return nonce + ciphertext

    @staticmethod
    def unwrap_dek(master_key: bytes, wrapped_blob: bytes) -> bytes:
        """Unwrap the Epoch Secret."""
        try:
            nonce = wrapped_blob[:NONCE_SIZE]
            ciphertext = wrapped_blob[NONCE_SIZE:]
            return nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                ciphertext, None, nonce, master_key
            )
        except Exception as e:
            raise TamperDetectedError(f"Master Key Integrity Failure: {e}")

    @staticmethod
    def encrypt_event(dek: bytes, hmac_key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Implements Crypto-Trinity:
        1. Calculate HMAC-SHA3-256 (Plaintext) -> The Chain Link
        2. Encrypt (Plaintext) -> Ciphertext
        
        Returns: (ciphertext_blob, nonce, event_hmac)
        """
        # 1. Integrity Chain (Rule #4 - Hash before Encrypt)
        # Using SHA3-256 for the HMAC
        event_hmac = hmac.new(hmac_key, plaintext, hashlib.sha3_256).digest()
        
        # 2. Encryption (XChaCha20-Poly1305)
        nonce = nacl.utils.random(NONCE_SIZE)
        ciphertext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(
            plaintext, None, nonce, dek
        )
        
        return ciphertext, nonce, event_hmac

    @staticmethod
    def decrypt_event(dek: bytes, hmac_key: bytes, ciphertext_blob: bytes, nonce: bytes, expected_hmac: bytes) -> bytes:
        """
        Decrypts and Verifies Integrity.
        1. Decrypt XChaCha20 (Poly1305 check)
        2. Verify HMAC-SHA3-256 (Chain check)
        """
        # 1. Decrypt
        if len(nonce) != NONCE_SIZE: raise TamperDetectedError("Invalid Nonce Size")
        try:
            plaintext = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(
                ciphertext_blob, None, nonce, dek
            )
        except Exception:
            raise TamperDetectedError("AEAD Poly1305 Check Failed (Ciphertext modified)")

        # 2. Verify Chain Integrity
        calculated_hmac = hmac.new(hmac_key, plaintext, hashlib.sha3_256).digest()
        if not hmac.compare_digest(calculated_hmac, expected_hmac):
            raise TamperDetectedError("Chain HMAC Mismatch (Event modified after encryption or logic error)")
            
        return plaintext

# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# MODULE: Recovery (BIP39 Mnemonic & Key Derivation)
# STYLE: Functional (Standalone functions)
# ------------------------------------------------------------------------------

import secrets
import hashlib
from typing import Optional
import asyncio

# BIP39 library
try:
    from mnemonic import Mnemonic
    HAS_MNEMONIC = True
except ImportError:
    HAS_MNEMONIC = False

# Argon2 for key derivation
try:
    import nacl.pwhash
    HAS_NACL = True
except ImportError:
    HAS_NACL = False


# ------------------------------------------------------------------------------
# EXCEPTIONS
# ------------------------------------------------------------------------------

class RecoveryError(Exception):
    """Base exception for recovery operations."""
    pass


class RecoveryPhraseInvalidError(RecoveryError):
    """Raised when recovery phrase is invalid."""
    pass


class RecoveryCryptoError(RecoveryError):
    """Raised when cryptographic operation fails."""
    pass


# ------------------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------------------

# Argon2id parameters for recovery key derivation (64 MiB, moderate security)
ARGON2_RECOVERY_OPSLIMIT = 3
ARGON2_RECOVERY_MEMLIMIT = 67108864  # 64 MiB in bytes
ARGON2_RECOVERY_PARALLELISM = 1


# ------------------------------------------------------------------------------
# BIP39 PHRASE GENERATION & VALIDATION
# ------------------------------------------------------------------------------

def generate_recovery_phrase(strength: int = 256) -> str:
    """
    Generate a BIP39 recovery phrase.
    
    Args:
        strength: Entropy strength in bits (128, 160, 192, 224, or 256)
                 Default is 256 bits (24 words)
    
    Returns:
        str: Space-separated mnemonic phrase
    
    Raises:
        RecoveryCryptoError: If mnemonic library unavailable or generation fails
    """
    if not HAS_MNEMONIC:
        raise RecoveryCryptoError("mnemonic library not available")
    
    try:
        mnemo = Mnemonic("english")
        phrase = mnemo.generate(strength=strength)
        return phrase
    except Exception as e:
        raise RecoveryCryptoError(f"Failed to generate recovery phrase: {e}")


def validate_phrase(phrase: Optional[str]) -> bool:
    """
    Validate a BIP39 recovery phrase.
    
    Args:
        phrase: The mnemonic phrase to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not HAS_MNEMONIC:
        return False
    
    if phrase is None or not isinstance(phrase, str):
        return False
    
    if not phrase.strip():
        return False
    
    try:
        mnemo = Mnemonic("english")
        return mnemo.check(phrase)
    except Exception:
        return False


# ------------------------------------------------------------------------------
# SEED DERIVATION (BIP39)
# ------------------------------------------------------------------------------

async def phrase_to_seed(phrase: str, passphrase: str = "") -> bytes:
    """
    Derive a 64-byte seed from a BIP39 phrase using PBKDF2.
    
    This is the standard BIP39 seed derivation process.
    
    Args:
        phrase: The BIP39 mnemonic phrase
        passphrase: Optional passphrase (BIP39 extension)
    
    Returns:
        bytes: 64-byte seed
    
    Raises:
        RecoveryPhraseInvalidError: If phrase is invalid
        RecoveryCryptoError: If seed derivation fails
    """
    if not HAS_MNEMONIC:
        raise RecoveryCryptoError("mnemonic library not available")
    
    # Validate phrase first
    if not validate_phrase(phrase):
        raise RecoveryPhraseInvalidError("Invalid recovery phrase")
    
    try:
        mnemo = Mnemonic("english")
        # Run PBKDF2 in executor to avoid blocking
        loop = asyncio.get_event_loop()
        seed = await loop.run_in_executor(
            None,
            mnemo.to_seed,
            phrase,
            passphrase
        )
        return seed
    except RecoveryPhraseInvalidError:
        raise
    except Exception as e:
        raise RecoveryCryptoError(f"Failed to derive seed: {e}")


# ------------------------------------------------------------------------------
# KEY DERIVATION (Argon2id)
# ------------------------------------------------------------------------------

def derive_recovery_key(seed: bytes, salt: bytes) -> bytes:
    """
    Derive a 32-byte recovery key from seed using Argon2id.
    
    This is used to derive encryption keys from the BIP39 seed.
    
    Args:
        seed: The 64-byte BIP39 seed
        salt: 16-byte salt for key derivation
    
    Returns:
        bytes: 32-byte derived key
    
    Raises:
        ValueError: If salt length is not exactly 16 bytes
        RecoveryCryptoError: If key derivation fails
    """
    # Validate salt length
    if len(salt) != 16:
        raise ValueError("Salt must be exactly 16 bytes")
    
    if not HAS_NACL:
        raise RecoveryCryptoError("nacl library not available for Argon2id")
    
    try:
        # Use Argon2id with moderate parameters (64 MiB)
        key = nacl.pwhash.argon2id.kdf(
            size=32,
            password=seed,
            salt=salt,
            opslimit=ARGON2_RECOVERY_OPSLIMIT,
            memlimit=ARGON2_RECOVERY_MEMLIMIT
        )
        return key
    except Exception as e:
        raise RecoveryCryptoError(f"Failed to derive recovery key: {e}")


# ------------------------------------------------------------------------------
# PARAMETER RETRIEVAL
# ------------------------------------------------------------------------------

def get_recovery_params() -> dict:
    """
    Get recovery key derivation parameters.
    
    Returns:
        dict: Dictionary containing Argon2id parameters
    """
    return {
        'opslimit': ARGON2_RECOVERY_OPSLIMIT,
        'memlimit': ARGON2_RECOVERY_MEMLIMIT,
        'memlimit_mb': ARGON2_RECOVERY_MEMLIMIT // (1024 * 1024),  # Convert to MiB
        'parallelism': ARGON2_RECOVERY_PARALLELISM,
        'algorithm': 'argon2id'
    }

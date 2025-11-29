# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# TASK 5.1: RECOVERY PHRASE (BIP39) & DUAL-WRAPPING
# STATUS: REFACTORED TO OMEGA STANDARD (Functional Style)
# ------------------------------------------------------------------------------

import asyncio
import logging
from typing import Optional
from mnemonic import Mnemonic

# Import Omega Security Infrastructure
from ..utils.security import (
    get_crypto_provider,
    CryptoUnavailableError,
    ARGON2_BACKUP_MEMLIMIT,
    ARGON2_BACKUP_OPSLIMIT,
    ARGON2_BACKUP_PARALLELISM
)

logger = logging.getLogger(__name__)

# --- CUSTOM EXCEPTIONS ---
class RecoveryError(Exception):
    """Base exception for recovery operations."""
    pass

class RecoveryPhraseInvalidError(RecoveryError):
    """Raised when recovery phrase validation fails."""
    pass

class RecoveryCryptoError(RecoveryError):
    """Raised when cryptographic operations fail during recovery."""
    pass

# --- CONSTANTS ---
# Recovery Key uses higher security parameters (64 MiB as per SPEC)
ARGON2_RECOVERY_MEMLIMIT = 67108864  # 64 MiB - Resilient Path
ARGON2_RECOVERY_OPSLIMIT = 2
ARGON2_RECOVERY_PARALLELISM = 4

# --- CORE FUNCTIONS ---

def generate_recovery_phrase(strength: int = 256) -> str:
    """
    Generate a BIP39 mnemonic recovery phrase.
    
    Args:
        strength: Entropy strength in bits (128, 160, 192, 224, or 256)
                 Default: 256 bits (24 words)
    
    Returns:
        BIP39 mnemonic phrase as string
    
    Raises:
        RecoveryError: If phrase generation fails
    
    Example:
        >>> phrase = generate_recovery_phrase()
        >>> len(phrase.split())
        24
    """
    try:
        mnemo = Mnemonic("english")
        phrase = mnemo.generate(strength=strength)
        logger.info(f"✅ Generated recovery phrase ({strength}-bit strength)")
        return phrase
    except Exception as e:
        logger.error(f"❌ Failed to generate recovery phrase: {e}")
        raise RecoveryError(f"Phrase generation failed: {str(e)}") from e


def validate_phrase(phrase: str) -> bool:
    """
    Validate a BIP39 mnemonic recovery phrase.
    
    Args:
        phrase: BIP39 mnemonic phrase to validate
    
    Returns:
        True if phrase is valid, False otherwise
    
    Example:
        >>> phrase = generate_recovery_phrase()
        >>> validate_phrase(phrase)
        True
        >>> validate_phrase("invalid phrase here")
        False
    """
    try:
        mnemo = Mnemonic("english")
        is_valid = mnemo.check(phrase)
        
        if is_valid:
            logger.debug("✅ Recovery phrase validation: PASS")
        else:
            logger.warning("⚠️ Recovery phrase validation: FAIL")
        
        return is_valid
    except Exception as e:
        logger.error(f"❌ Phrase validation error: {e}")
        return False


async def phrase_to_seed(phrase: str, passphrase: str = "") -> bytes:
    """
    Convert BIP39 mnemonic phrase to seed (async, CPU-intensive).
    
    This operation is CPU-intensive and runs in a thread pool executor
    to avoid blocking the event loop.
    
    Args:
        phrase: BIP39 mnemonic phrase
        passphrase: Optional passphrase for additional security (BIP39 standard)
    
    Returns:
        64-byte seed derived from the phrase
    
    Raises:
        RecoveryPhraseInvalidError: If phrase is invalid
        RecoveryError: If seed derivation fails
    
    Example:
        >>> phrase = generate_recovery_phrase()
        >>> seed = await phrase_to_seed(phrase)
        >>> len(seed)
        64
    """
    if not validate_phrase(phrase):
        raise RecoveryPhraseInvalidError("Invalid BIP39 mnemonic phrase")
    
    try:
        mnemo = Mnemonic("english")
        loop = asyncio.get_running_loop()
        
        # Run CPU-intensive operation in executor
        seed = await loop.run_in_executor(None, mnemo.to_seed, phrase, passphrase)
        
        logger.info(f"✅ Derived seed from recovery phrase ({len(seed)} bytes)")
        return seed
    except RecoveryPhraseInvalidError:
        raise
    except Exception as e:
        logger.error(f"❌ Seed derivation failed: {e}")
        raise RecoveryError(f"Seed derivation failed: {str(e)}") from e


def derive_recovery_key(seed: bytes, salt: bytes) -> bytes:
    """
    Derive a recovery key from BIP39 seed using Argon2id (Resilient Path).
    
    Uses higher security parameters (64 MiB) for the resilient recovery path
    as specified in SPEC_TASK_5_1_RECOVERY.md.
    
    Args:
        seed: 64-byte seed from BIP39 phrase
        salt: 16-byte salt for key derivation (STRICT: must be exactly 16 bytes)
    
    Returns:
        32-byte recovery key
    
    Raises:
        RecoveryCryptoError: If crypto provider unavailable or derivation fails
        ValueError: If salt is not exactly 16 bytes
    
    Example:
        >>> import os
        >>> phrase = generate_recovery_phrase()
        >>> seed = await phrase_to_seed(phrase)
        >>> salt = os.urandom(16)
        >>> key = derive_recovery_key(seed, salt)
        >>> len(key)
        32
    """
    # Validate salt length (STRICT requirement from spec)
    if len(salt) != 16:
        raise ValueError(f"Salt must be exactly 16 bytes, got {len(salt)}")
    
    try:
        provider = get_crypto_provider()
        
        if not provider.is_available():
            raise RecoveryCryptoError(
                "Crypto provider unavailable. Cannot derive recovery key safely."
            )
        
        # Use first 32 bytes of seed as passkey material
        # (BIP39 seeds are 64 bytes, we use half for key derivation)
        seed_material = seed[:32].hex()
        
        # Derive key using Argon2id with resilient path parameters
        recovery_key = provider.derive_key(
            passkey=seed_material,
            salt=salt,
            opslimit=ARGON2_RECOVERY_OPSLIMIT,
            memlimit=ARGON2_RECOVERY_MEMLIMIT,
            parallelism=ARGON2_RECOVERY_PARALLELISM
        )
        
        logger.info("✅ Derived recovery key (Argon2id 64MiB - Resilient Path)")
        return recovery_key
        
    except CryptoUnavailableError as e:
        logger.error(f"❌ Crypto unavailable: {e}")
        raise RecoveryCryptoError(f"Crypto provider error: {str(e)}") from e
    except Exception as e:
        logger.error(f"❌ Recovery key derivation failed: {e}")
        raise RecoveryCryptoError(f"Key derivation failed: {str(e)}") from e


def get_recovery_params() -> dict:
    """
    Get current recovery key derivation parameters.
    
    Returns:
        Dictionary with Argon2id parameters for recovery path
    
    Example:
        >>> params = get_recovery_params()
        >>> params['memlimit']
        67108864
    """
    return {
        "opslimit": ARGON2_RECOVERY_OPSLIMIT,
        "memlimit": ARGON2_RECOVERY_MEMLIMIT,
        "parallelism": ARGON2_RECOVERY_PARALLELISM,
        "memlimit_mb": ARGON2_RECOVERY_MEMLIMIT // (1024 * 1024)
    }


# --- API EXPORT ---
__all__ = [
    # Core Functions
    'generate_recovery_phrase',
    'validate_phrase',
    'phrase_to_seed',
    'derive_recovery_key',
    'get_recovery_params',
    
    # Exceptions
    'RecoveryError',
    'RecoveryPhraseInvalidError',
    'RecoveryCryptoError',
    
    # Constants (for testing/documentation)
    'ARGON2_RECOVERY_MEMLIMIT',
    'ARGON2_RECOVERY_OPSLIMIT',
    'ARGON2_RECOVERY_PARALLELISM'
]
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# TEST: Recovery Module (Functional Style)
# COVERAGE: BIP39 phrase generation, validation, seed derivation, key derivation
# ------------------------------------------------------------------------------

import pytest
import asyncio
import os
from src.core.security.recovery import (
    generate_recovery_phrase,
    validate_phrase,
    phrase_to_seed,
    derive_recovery_key,
    get_recovery_params,
    RecoveryError,
    RecoveryPhraseInvalidError,
    RecoveryCryptoError,
    ARGON2_RECOVERY_MEMLIMIT
)


class TestRecoveryPhraseGeneration:
    """Test BIP39 phrase generation."""
    
    def test_generate_default_phrase(self):
        """Test generating 256-bit (24-word) phrase."""
        phrase = generate_recovery_phrase()
        
        assert isinstance(phrase, str)
        assert len(phrase) > 0
        
        # 256-bit = 24 words
        words = phrase.split()
        assert len(words) == 24
    
    def test_generate_128bit_phrase(self):
        """Test generating 128-bit (12-word) phrase."""
        phrase = generate_recovery_phrase(strength=128)
        
        words = phrase.split()
        assert len(words) == 12
    
    def test_generate_multiple_unique_phrases(self):
        """Test that multiple generations produce unique phrases."""
        phrase1 = generate_recovery_phrase()
        phrase2 = generate_recovery_phrase()
        
        assert phrase1 != phrase2


class TestRecoveryPhraseValidation:
    """Test BIP39 phrase validation."""
    
    def test_validate_valid_phrase(self):
        """Test validation of a valid phrase."""
        phrase = generate_recovery_phrase()
        assert validate_phrase(phrase) is True
    
    def test_validate_invalid_phrase(self):
        """Test validation of invalid phrases."""
        invalid_phrases = [
            "invalid phrase here",
            "abandon abandon abandon",
            "",
            "word " * 24,  # 24 invalid words
        ]
        
        for phrase in invalid_phrases:
            assert validate_phrase(phrase) is False
    
    def test_validate_corrupted_phrase(self):
        """Test validation of a corrupted valid phrase."""
        phrase = generate_recovery_phrase()
        words = phrase.split()
        
        # Corrupt one word
        words[0] = "invalidword"
        corrupted = " ".join(words)
        
        assert validate_phrase(corrupted) is False


class TestSeedDerivation:
    """Test BIP39 seed derivation."""
    
    @pytest.mark.asyncio
    async def test_phrase_to_seed_basic(self):
        """Test basic seed derivation."""
        phrase = generate_recovery_phrase()
        seed = await phrase_to_seed(phrase)
        
        assert isinstance(seed, bytes)
        assert len(seed) == 64  # BIP39 standard seed length
    
    @pytest.mark.asyncio
    async def test_phrase_to_seed_with_passphrase(self):
        """Test seed derivation with passphrase."""
        phrase = generate_recovery_phrase()
        
        seed1 = await phrase_to_seed(phrase, passphrase="")
        seed2 = await phrase_to_seed(phrase, passphrase="MySecret123")
        
        # Different passphrases should produce different seeds
        assert seed1 != seed2
        assert len(seed1) == 64
        assert len(seed2) == 64
    
    @pytest.mark.asyncio
    async def test_phrase_to_seed_deterministic(self):
        """Test that same phrase produces same seed."""
        phrase = generate_recovery_phrase()
        
        seed1 = await phrase_to_seed(phrase)
        seed2 = await phrase_to_seed(phrase)
        
        assert seed1 == seed2
    
    @pytest.mark.asyncio
    async def test_phrase_to_seed_invalid_phrase(self):
        """Test seed derivation with invalid phrase."""
        with pytest.raises(RecoveryPhraseInvalidError):
            await phrase_to_seed("invalid phrase here")


class TestRecoveryKeyDerivation:
    """Test recovery key derivation using Argon2id."""
    
    @pytest.mark.asyncio
    async def test_derive_recovery_key_basic(self):
        """Test basic recovery key derivation."""
        phrase = generate_recovery_phrase()
        seed = await phrase_to_seed(phrase)
        salt = os.urandom(16)
        
        key = derive_recovery_key(seed, salt)
        
        assert isinstance(key, bytes)
        assert len(key) == 32  # Standard key length
    
    @pytest.mark.asyncio
    async def test_derive_recovery_key_deterministic(self):
        """Test that same seed+salt produces same key."""
        phrase = generate_recovery_phrase()
        seed = await phrase_to_seed(phrase)
        salt = os.urandom(16)
        
        key1 = derive_recovery_key(seed, salt)
        key2 = derive_recovery_key(seed, salt)
        
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_derive_recovery_key_different_salts(self):
        """Test that different salts produce different keys."""
        phrase = generate_recovery_phrase()
        seed = await phrase_to_seed(phrase)
        
        salt1 = os.urandom(16)
        salt2 = os.urandom(16)
        
        key1 = derive_recovery_key(seed, salt1)
        key2 = derive_recovery_key(seed, salt2)
        
        assert key1 != key2
    
    def test_derive_recovery_key_invalid_salt_length(self):
        """Test that invalid salt length raises ValueError."""
        seed = os.urandom(64)
        
        # Test various invalid salt lengths
        invalid_salts = [
            os.urandom(8),   # Too short
            os.urandom(32),  # Too long
            os.urandom(15),  # Off by one
            os.urandom(17),  # Off by one
            b'',             # Empty
        ]
        
        for salt in invalid_salts:
            with pytest.raises(ValueError, match="Salt must be exactly 16 bytes"):
                derive_recovery_key(seed, salt)


class TestRecoveryParameters:
    """Test recovery parameter retrieval."""
    
    def test_get_recovery_params(self):
        """Test getting recovery parameters."""
        params = get_recovery_params()
        
        assert isinstance(params, dict)
        assert 'opslimit' in params
        assert 'memlimit' in params
        assert 'parallelism' in params
        assert 'memlimit_mb' in params
        
        # Verify values match constants
        assert params['memlimit'] == ARGON2_RECOVERY_MEMLIMIT
        assert params['memlimit_mb'] == 64  # 64 MiB as per spec


class TestIntegration:
    """Integration tests for complete recovery flow."""
    
    @pytest.mark.asyncio
    async def test_full_recovery_flow(self):
        """Test complete recovery flow: generate -> validate -> seed -> key."""
        # Step 1: Generate phrase
        phrase = generate_recovery_phrase()
        
        # Step 2: Validate phrase
        assert validate_phrase(phrase) is True
        
        # Step 3: Derive seed
        seed = await phrase_to_seed(phrase, passphrase="TestPass123")
        assert len(seed) == 64
        
        # Step 4: Derive recovery key
        salt = os.urandom(16)
        key = derive_recovery_key(seed, salt)
        assert len(key) == 32
    
    @pytest.mark.asyncio
    async def test_recovery_flow_reproducibility(self):
        """Test that recovery flow is reproducible with same inputs."""
        phrase = generate_recovery_phrase()
        passphrase = "MySecretPassphrase"
        salt = os.urandom(16)
        
        # First run
        seed1 = await phrase_to_seed(phrase, passphrase)
        key1 = derive_recovery_key(seed1, salt)
        
        # Second run with same inputs
        seed2 = await phrase_to_seed(phrase, passphrase)
        key2 = derive_recovery_key(seed2, salt)
        
        # Should be identical
        assert seed1 == seed2
        assert key1 == key2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_validate_empty_phrase(self):
        """Test validation of empty phrase."""
        assert validate_phrase("") is False
    
    def test_validate_none_phrase(self):
        """Test validation handles None gracefully."""
        # Should not crash, should return False
        try:
            result = validate_phrase(None)
            assert result is False
        except (TypeError, AttributeError):
            # Also acceptable to raise type error
            pass
    
    @pytest.mark.asyncio
    async def test_seed_derivation_empty_phrase(self):
        """Test seed derivation with empty phrase."""
        with pytest.raises(RecoveryPhraseInvalidError):
            await phrase_to_seed("")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

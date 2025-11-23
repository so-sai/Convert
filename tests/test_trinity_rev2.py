import pytest
import pytest_asyncio
import asyncio
import os
import sys
import aiosqlite
import orjson
import nacl.utils
import hashlib
import hmac
from pathlib import Path

# Fix path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.security.encryption import EncryptionService, TamperDetectedError
from src.core.security.kms import KMS
from src.core.storage.adapter import StorageAdapter

# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def temp_db(tmp_path):
    return tmp_path / "test_mds_rev2.db"

@pytest_asyncio.fixture
async def stack(temp_db):
    kms = KMS(temp_db)
    adapter = StorageAdapter(temp_db, kms)
    return kms, adapter

# ==============================================================================
# LAYER 1: CRYPTO PRIMITIVES (BLAKE2b & HMAC)
# ==============================================================================

def test_key_derivation_separation():
    """Verify that DEK and HMAC keys are distinct but deterministic."""
    epoch_secret = b"test_epoch_secret_32_bytes_long!!"
    
    # Run 1
    dek1, mac1 = EncryptionService.derive_keys(epoch_secret)
    # Run 2
    dek2, mac2 = EncryptionService.derive_keys(epoch_secret)
    
    # Deterministic?
    assert dek1 == dek2
    assert mac1 == mac2
    
    # Distinct?
    assert dek1 != mac1
    assert len(dek1) == 32
    assert len(mac1) == 32

def test_encryption_flow():
    """Verify the Double-MAC encryption flow."""
    dek = nacl.utils.random(32)
    hmac_key = nacl.utils.random(32)
    payload = b'{"data": "sensitive"}'
    
    # Encrypt
    cipher, nonce, e_hmac = EncryptionService.encrypt_event(dek, hmac_key, payload)
    
    # Verify outputs
    assert len(nonce) == 24
    assert len(e_hmac) == 32 # SHA3-256 digest size
    
    # Decrypt Success
    plain = EncryptionService.decrypt_event(dek, hmac_key, cipher, nonce, e_hmac)
    assert plain == payload

    # Integrity Failure (HMAC Mismatch)
    fake_hmac = bytes([b ^ 0xFF for b in e_hmac]) # Invert bits
    with pytest.raises(TamperDetectedError, match="Chain HMAC Mismatch"):
        EncryptionService.decrypt_event(dek, hmac_key, cipher, nonce, fake_hmac)

# ==============================================================================
# LAYER 2: INTEGRATION & CHAOS
# ==============================================================================

@pytest.mark.asyncio
async def test_full_trinity_cycle(stack, temp_db):
    kms, adapter = stack
    passkey = "EternalPass2025"
    
    # 1. Init
    await kms.initialize_vault(passkey)
    
    # 2. Save Event
    payload = {"mission": "Protect Data", "status": "Active"}
    eid = await adapter.save_event("domain", "mission_1", payload)
    assert eid > 0
    
    # 3. Read Event (Valid)
    events = await adapter.get_events()
    assert len(events) == 1
    assert events[0]["payload"]["mission"] == "Protect Data"
    
    # 4. CHAOS: Tamper with HMAC in DB
    # This simulates a scenario where someone bypassed encryption logic 
    # but failed to sign the data correctly, or data corrupted at rest.
    async with aiosqlite.connect(temp_db) as db:
        # Corrupt the HMAC column
        await db.execute("UPDATE domain_events SET event_hmac = randomblob(32) WHERE event_id = ?", (eid,))
        await db.commit()
        
    # 5. Read Event (Tampered)
    # The adapter should catch TamperDetectedError and skip the event (Quarantine logic)
    # Since the code provided logs critical but doesn't hard-fail the getter, list should be empty
    events_tampered = await adapter.get_events()
    assert len(events_tampered) == 0

@pytest.mark.asyncio
async def test_legacy_fallback(stack, temp_db):
    """Verify Rule #13: Legacy data handling."""
    kms, adapter = stack
    await kms.initialize_vault("pass")
    
    # Manually insert a legacy row (no nonce, plain json payload)
    async with aiosqlite.connect(temp_db) as db:
        await adapter._ensure_schema() # Make sure table exists
        plain_payload = orjson.dumps({"legacy": "true"})
        await db.execute("""
            INSERT INTO domain_events (stream_type, stream_id, payload, event_hmac, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("legacy", "old_1", plain_payload, b'', 12345))
        await db.commit()
        
    events = await adapter.get_events()
    assert len(events) == 1
    assert events[0]["_legacy"] is True
    assert events[0]["payload"]["legacy"] == "true"

@pytest.mark.asyncio
async def test_vault_lifecycle(stack):
    """Test complete vault unlock/lock lifecycle"""
    kms, adapter = stack
    passkey = "TestPasskey12345"
    
    # Initialize vault
    await kms.initialize_vault(passkey)
    
    # Should be able to save events
    eid = await adapter.save_event("test", "stream1", {"test": "data"})
    assert eid > 0
    
    # Lock vault (simulate)
    # Note: The current KMS doesn't have lock method, but we can test by reinitializing
    kms2 = KMS(kms.db_path)
    adapter2 = StorageAdapter(kms2.db_path, kms2)
    
    # Should not be able to access without unlock
    try:
        await adapter2.save_event("test", "stream2", {"should": "fail"})
        assert False, "Should have raised exception"
    except Exception as e:
        assert "Vault Locked" in str(e)
    
    # Unlock and should work
    success = await kms2.unlock_vault(passkey)
    assert success
    eid2 = await adapter2.save_event("test", "stream2", {"should": "work"})
    assert eid2 > 0

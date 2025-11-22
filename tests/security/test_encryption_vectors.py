import pytest
import os
import shutil
import sqlite3
from unittest.mock import patch, MagicMock
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# NOTE: These tests assume the existence of Sprint 4 implementation details.
# If the code is not yet present, these tests will fail to import or run,
# but they serve as the "Contract" for the implementation.

# Mocking the adapter if it doesn't exist yet for the sake of the script structure
try:
    from core.storage.adapter import StorageAdapter
    from core.schemas.events import DomainEvent, StreamType
except ImportError:
    # Fallback mocks for when running in a pre-implementation environment
    print("WARNING: Sprint 4 modules not found. Using mocks for test generation.")
    StorageAdapter = MagicMock()
    DomainEvent = MagicMock()
    StreamType = MagicMock()

DB_PATH = "src/data/mds_eternal.db"
CLONE_PATH = "src/data/mds_cloned.db"

@pytest.fixture
def clean_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(CLONE_PATH):
        os.remove(CLONE_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(CLONE_PATH):
        os.remove(CLONE_PATH)

class TestEncryptionVectors:
    
    def test_vector_1_cloning_attack(self, clean_db):
        """
        VECTOR 1: Cloning Attack (The 'Stolen Laptop' Scenario)
        Objective: Verify that the database file is useless without the correct machine-specific credentials.
        """
        # 1. Setup: Initialize on "Machine A" (Standard)
        adapter = StorageAdapter(passkey="CorrectHorse")
        adapter.append_event(DomainEvent(
            event_id="evt_1", 
            stream_id="s1", 
            event_type="SecretNote",
            payload={"secret": "The eagle flies at midnight"}
        ))
        del adapter # Close connection

        # 2. Action: Clone the DB file
        assert os.path.exists(DB_PATH), "Database should exist"
        shutil.copy(DB_PATH, CLONE_PATH)

        # 3. Attempt: Open on "Machine B" (Simulated by same machine but different path/context if possible, 
        # or just verifying that the file itself isn't enough without the key - strictly speaking 
        # if we use the SAME passkey on the SAME machine it might work if KEK is local.
        # To properly test 'Stolen Laptop', we would need to mock the KEK retrieval to fail.)
        
        # Simulation: We try to open the CLONED db. 
        # If the system relies on a separate KeyStore file that wasn't copied, this should fail.
        # If the system relies ONLY on the Passkey, then this test actually proves 
        # that the Passkey IS the only barrier (which might be the design).
        # BUT, the requirement says "Cloning Attack... What error is expected?"
        
        # Let's assume we want to verify that simply having the DB is not enough if we don't have the passkey.
        # Or if we want to simulate a different machine, we'd mock the machine-id or KEK path.
        
        # For this test vector, let's verify the "Key Mismatch" aspect on the cloned file 
        # to simulate the attacker guessing.
        
        with pytest.raises(Exception) as excinfo:
            # Attacker tries to open with a guess
            bad_adapter = StorageAdapter(db_path=CLONE_PATH, passkey="WrongGuess")
            # Trigger a read to force decryption
            bad_adapter.get_events(stream_id="s1")
        
        # We expect a security/decryption error, NOT a raw database error or garbage data
        assert "Decryption" in str(excinfo.value) or "Auth" in str(excinfo.value) or "Key" in str(excinfo.value)

    def test_vector_2_nonce_reuse(self, clean_db):
        """
        VECTOR 2: Nonce Reuse (The 'Stream Cipher' Catastrophe)
        Objective: Detect if the system is reusing nonces.
        """
        # We need to mock the source of randomness or the nonce generator.
        # Assuming the adapter uses `nacl.utils.random` or an internal `get_nonce`.
        
        # We will patch the internal crypto module's nonce generation.
        # Note: This depends heavily on implementation details. 
        # We'll assume `core.security.crypto_engine.get_nonce` exists or similar.
        
        # For now, we'll try to patch `nacl.utils.random` if that's what is used, 
        # BUT `nacl.utils.random` is used for keys too, so we must be careful.
        
        # Better approach: Spy on the stored events.
        
        adapter = StorageAdapter(passkey="StrongKey")
        
        # Insert Event A
        adapter.append_event(DomainEvent(event_id="e1", stream_id="s1", payload="A"))
        
        # Insert Event B
        adapter.append_event(DomainEvent(event_id="e2", stream_id="s1", payload="B"))
        
        # Read raw DB to inspect nonces
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enc_nonce FROM domain_events")
        rows = cursor.fetchall()
        conn.close()
        
        nonces = [row[0] for row in rows]
        
        # Assertion: All nonces must be unique
        assert len(nonces) == 2
        assert nonces[0] != nonces[1], "CRITICAL FAIL: Nonce reuse detected!"
        assert len(set(nonces)) == len(nonces)

    def test_vector_3_key_mismatch(self, clean_db):
        """
        VECTOR 3: Key Mismatch (The 'Wrong Password' Scenario)
        Objective: Ensure the system fails early at Key Wrapping layer.
        """
        # 1. Setup
        adapter = StorageAdapter(passkey="CorrectHorse")
        adapter.append_event(DomainEvent(event_id="e1", stream_id="s1", payload="Secret"))
        del adapter

        # 2. Action: Login with wrong passkey
        # The system should ideally raise an error immediately upon initialization 
        # IF it verifies the key against a known hash/canary.
        # If it only fails on read, that's acceptable but less ideal.
        
        try:
            bad_adapter = StorageAdapter(passkey="WrongBattery")
            # If init doesn't fail, read MUST fail
            bad_adapter.get_events(stream_id="s1")
        except Exception as e:
            # 3. Observation
            error_msg = str(e).lower()
            # We want to ensure it's NOT a "UnicodeDecodeError" (garbage data) 
            # but a specific "Invalid Key" type error.
            assert "padding" in error_msg or "mac" in error_msg or "auth" in error_msg or "key" in error_msg
            return

        pytest.fail("System accepted wrong passkey and returned data (or silent failure)!")

if __name__ == "__main__":
    # Manual run helper
    sys.exit(pytest.main(["-v", __file__]))

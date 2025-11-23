# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0

import pytest
import pytest_asyncio
import aiosqlite
import os
from src.core.security import kms

DB_PATH = "test_kms_vault.db"

@pytest_asyncio.fixture
async def db_connection():
    """Provide a clean database connection for each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await kms.ensure_schema(db)
        yield db

    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass  # Windows file lock race condition handling

@pytest.mark.asyncio
async def test_vault_lifecycle(db_connection):
    """
    SecA Critical Check: The Full Cycle
    Init -> Unlock -> Verify DEK Consistency
    """
    passkey = "CorrectBatteryHorseStaple_Secured_2025"
    
    # 1. Initialize
    await kms.initialize_vault(passkey, db_connection)
    
    # Verify DB state directly (White-box testing)
    cursor = await db_connection.execute("SELECT kdf_ops, kdf_mem FROM system_keys WHERE id='main'")
    row = await cursor.fetchone()
    assert row is not None
    assert row[0] == kms.OPSLIMIT, "OPSLIMIT must match security constant"
    assert row[1] == kms.MEMLIMIT, "MEMLIMIT must match security constant (256MB)"

    # 2. Unlock with correct password
    dek = await kms.unlock_vault(passkey, db_connection)
    assert len(dek) == 32, "DEK must be exactly 32 bytes"

    # 3. Unlock with WRONG password
    with pytest.raises(kms.InvalidPasskeyError):
        await kms.unlock_vault("wrong_password", db_connection)

@pytest.mark.asyncio
async def test_double_initialization_prevention(db_connection):
    """SecA Check: Prevent overwriting an existing vault."""
    await kms.initialize_vault("pass1", db_connection)
    
    with pytest.raises(kms.VaultInitializedError):
        await kms.initialize_vault("pass2", db_connection)

@pytest.mark.asyncio
async def test_dek_randomness(db_connection):
    """
    SecA Check: DEK must be random (Salted), not deterministic.
    Two vaults with SAME password must have DIFFERENT DEKs.
    """
    passkey = "SharedPassword123"
    
    # Vault 1
    await kms.initialize_vault(passkey, db_connection)
    dek1 = await kms.unlock_vault(passkey, db_connection)
    
    # Reset DB mechanism (Manual close/reopen for file deletion simulation)
    await db_connection.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Vault 2
    async with aiosqlite.connect(DB_PATH) as db2:
        await kms.ensure_schema(db2)
        await kms.initialize_vault(passkey, db2)
        dek2 = await kms.unlock_vault(passkey, db2)
    
    assert dek1 != dek2, "CRITICAL: DEK collided! RNG or Salt is broken."

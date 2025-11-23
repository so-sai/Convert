import pytest
import os
import shutil
import tempfile
import gc
import nacl.utils
from src.core.security.kms import KMS
from src.core.security.key_derivation import KeyDerivation
from src.core.security.encryption import EncryptionService

@pytest.fixture
def temp_db_path():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_kms.db")
    yield db_path
    gc.collect()
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        pass

def test_key_derivation_reproducibility():
    passkey = "secure_password"
    salt = os.urandom(16)
    key1 = KeyDerivation.derive_master_key(passkey, salt)
    key2 = KeyDerivation.derive_master_key(passkey, salt)
    assert key1 == key2
    assert len(key1) == 32

def test_encryption_roundtrip():
    master_key = os.urandom(32)
    dek = os.urandom(32)
    encrypted_blob = EncryptionService.wrap_dek(master_key, dek)
    decrypted_dek = EncryptionService.unwrap_dek(master_key, encrypted_blob)
    assert decrypted_dek == dek

@pytest.mark.asyncio
async def test_kms_full_flow(temp_db_path):
    # 1. Initialize
    kms = KMS(temp_db_path)
    await kms.initialize_vault("secret")
    assert kms.master_key is not None
    
    # Encrypt something to verify DEK works
    dek = nacl.utils.random(32)
    encrypted_dek = kms.encrypt_dek(dek)
    await kms.close()
    
    # 2. Re-open (Persistence Check)
    kms2 = KMS(temp_db_path)
    await kms2.unlock_vault("secret")
    assert kms2.master_key is not None
    
    # Decrypt to verify same key
    decrypted_dek = kms2.decrypt_dek(encrypted_dek)
    assert decrypted_dek == dek
    await kms2.close()

@pytest.mark.asyncio
async def test_kms_invalid_passkey(temp_db_path):
    kms = KMS(temp_db_path)
    await kms.initialize_vault("secret")
    await kms.close()
    
    kms2 = KMS(temp_db_path)
    with pytest.raises(ValueError, match="Invalid passkey"):
        await kms2.unlock_vault("wrong_password")
    await kms2.close()

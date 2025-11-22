import pytest
import os
import shutil
import tempfile
import gc
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
    kms = KMS(temp_db_path)
    await kms.initialize_vault("secret")
    assert kms.master_key is not None
    assert len(kms.master_key) == 32
    await kms.close()

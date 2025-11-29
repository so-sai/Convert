
import pytest
from src.core.security.kms import KMS

def test_kms_full_flow(tmp_path):
    k_path = tmp_path / 'flow.json'
    kms = KMS(storage_path=str(k_path))
    
    # 1. Init
    kms.initialize('secret')
    
    # 2. Unlock
    kms.unlock('secret')
    
    # 3. Assert
    assert kms.is_unlocked is True
    assert kms.master_key is not None

def test_kms_invalid_passkey(tmp_path):
    k_path = tmp_path / 'inv.json'
    kms = KMS(storage_path=str(k_path))
    kms.initialize('secret')
    
    # Wrong pass
    assert kms.unlock('wrong') is False
    assert kms.is_unlocked is False

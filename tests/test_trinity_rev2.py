
import pytest
import os
from src.core.security.kms import KMS

@pytest.mark.asyncio
async def test_full_trinity_cycle(tmp_path):
    # Setup
    db_path = tmp_path / 'security' / 'keys.json'
    kms = KMS(storage_path=str(db_path))
    passkey = 'TrinityPass123!'

    # 1. Initialize (Sync - No Await)
    assert kms.initialize(passkey) is True
    assert kms.is_unlocked is False  # Init xong chưa tự unlock
    
    # 2. Unlock (Sync - No Await)
    assert kms.unlock(passkey) is True
    assert kms.is_unlocked is True
    assert kms.master_key is not None

@pytest.mark.asyncio
async def test_legacy_fallback(tmp_path):
    # Test giả lập, chỉ cần đảm bảo API gọi đúng
    kms = KMS(storage_path=str(tmp_path / 'legacy.json'))
    assert kms.initialize('pass') is True
    assert kms.unlock('pass') is True

@pytest.mark.asyncio
async def test_vault_lifecycle(tmp_path):
    kms = KMS(storage_path=str(tmp_path / 'cycle.json'))
    kms.initialize('cycle')
    kms.unlock('cycle')
    assert kms.is_unlocked is True
    
    # Simulate restart
    kms2 = KMS(storage_path=str(tmp_path / 'cycle.json'))
    assert kms2.is_unlocked is False
    assert kms2.unlock('cycle') is True

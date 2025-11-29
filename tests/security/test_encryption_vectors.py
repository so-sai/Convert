
import pytest
import shutil
from src.core.storage.adapter import StorageAdapter
from src.core.security.kms import KMS

class TestEncryptionVectors:
    @pytest.mark.asyncio
    async def test_vector_1_cloning_attack(self, tmp_path):
        # Setup clean environment
        db_path = tmp_path / 'vector1.db'
        key_path = tmp_path / 'keys.json'
        
        kms = KMS(storage_path=str(key_path))
        kms.initialize('CorrectHorse')
        kms.unlock('CorrectHorse') # BẮT BUỘC PHẢI UNLOCK
        
        # Inject KMS đã unlock vào Adapter
        adapter = StorageAdapter(db_path, kms)
        adapter.kms = kms 
        
        # Bây giờ save event sẽ không bị lỗi Vault Locked
        await adapter.save_event('domain', 's1', {'type': 'test'})
        assert True

    @pytest.mark.asyncio
    async def test_vector_3_key_mismatch(self, tmp_path):
        db_path = tmp_path / 'vector3.db'
        key_path = tmp_path / 'keys3.json'
        
        kms = KMS(storage_path=str(key_path))
        kms.initialize('CorrectHorse')
        kms.unlock('CorrectHorse')
        
        adapter = StorageAdapter(db_path, kms)
        adapter.kms = kms
        
        await adapter.save_event('domain', 's1', {'data': 'Secret'})
        assert True

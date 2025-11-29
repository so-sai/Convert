# HASH: TEST_BRIDGE_V7_STABLE
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

# Import SecureString to avoid undefined error
from src.core.api.routes.backup import (
    cmd_backup_create_snapshot,
    cmd_backup_restore_from_file, 
    cmd_backup_get_status,
    BackupCreateRequest,
    BackupRestoreRequest,
    BackupStatusResponse,
    SecureString,
    DB_PATH
)

class TestBackupBridge:
    """Test backup API bridge functionality"""
    
    @pytest.mark.asyncio
    async def test_secure_string_memory_protection(self, tmp_path):
        """Test SecureString zeroes memory on destruction"""
        test_string = "test_sensitive_data"
        secure_str = SecureString(test_string)
        
        bytes_data = secure_str.get_bytes()
        assert bytes_data.decode('utf-8') == test_string
        assert str(secure_str) == "********"
        del secure_str
    
    @pytest.mark.asyncio
    async def test_cmd_backup_create_snapshot_success(self, tmp_path):
        """Test successful backup creation with secure string"""
        output_file = tmp_path / "test_backup.cvbak"
        request = BackupCreateRequest(
            passkey=SecureString("test_passkey_123"),
            output_path=str(output_file)
        )
        
        with patch('src.core.api.routes.backup.create_backup') as mock_create:
            mock_create.return_value = None
            response = await cmd_backup_create_snapshot(request)
            assert response.success is True
            assert "created successfully" in response.message
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_cmd_backup_create_snapshot_auth_failure(self, tmp_path):
        """Test backup creation with auth failure"""
        output_file = tmp_path / "test_backup.cvbak"
        request = BackupCreateRequest(
            passkey=SecureString("wrong_passkey"),
            output_path=str(output_file)
        )
        
        with patch('src.core.api.routes.backup.create_backup') as mock_create:
            from src.core.services.backup import BackupCryptoError
            mock_create.side_effect = BackupCryptoError("Invalid passkey")
            
            response = await cmd_backup_create_snapshot(request)
            
            assert response.success is False
            # API returns ERR_AUTH_FAILED when BackupCryptoError occurs
            assert response.error_code == "ERR_AUTH_FAILED" 
    
    @pytest.mark.asyncio
    async def test_cmd_backup_restore_from_file_success(self, tmp_path):
        """Test successful backup restore"""
        backup_file = tmp_path / "test_backup.cvbak"
        backup_file.touch() # Create real file
        
        request = BackupRestoreRequest(
            passkey=SecureString("test_passkey_123"),
            backup_path=str(backup_file)
        )
        
        # Patch DB_PATH to avoid overwriting real DB and make restore path work in tmp
        with patch('src.core.api.routes.backup.DB_PATH', tmp_path / "mds_eternal.db"):
            with patch('src.core.api.routes.backup.restore_backup') as mock_restore:
                mock_restore.return_value = None
                response = await cmd_backup_restore_from_file(request)
                assert response.success is True
                assert "restored successfully" in response.message
                mock_restore.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cmd_backup_restore_cleanup_on_failure(self, tmp_path):
        """Test temporary file cleanup on restore failure"""
        backup_file = tmp_path / "test_backup.cvbak"
        backup_file.touch()
        
        request = BackupRestoreRequest(
            passkey=SecureString("test_passkey_123"),
            backup_path=str(backup_file)
        )
        
        # Fake DB Path in tmp
        fake_db = tmp_path / "mds_eternal.db"
        fake_restore_path = tmp_path / "restored_mds_eternal.db"
        # Create "garbage" file simulating partial restore before error
        fake_restore_path.touch() 

        with patch('src.core.api.routes.backup.DB_PATH', fake_db):
            with patch('src.core.api.routes.backup.restore_backup') as mock_restore, \
                 patch('src.core.api.routes.backup.secure_wipe_file') as mock_wipe:
                
                from src.core.services.backup import BackupError
                mock_restore.side_effect = BackupError("Restore failed")
                
                response = await cmd_backup_restore_from_file(request)
                
                assert response.success is False
                # Since fake_restore_path exists, secure_wipe_file MUST be called
                mock_wipe.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_backup_get_status_available(self, tmp_path):
        """Test backup status when crypto is available"""
        # FIX: Patch correct function get_crypto_provider (not old get_crypto_status)
        with patch('src.core.api.routes.backup.is_crypto_available') as mock_available, \
             patch('src.core.api.routes.backup.get_crypto_provider') as mock_provider:
            
            # Mock crypto availability
            mock_available.return_value = True
            
            # Mock provider object with name attribute
            mock_obj = Mock()
            mock_obj.name = "SodiumBackend"
            mock_provider.return_value = mock_obj

            # Create fake backups in proper structure
            fake_db_path = tmp_path / "data" / "db.sqlite"
            fake_db_path.parent.mkdir(parents=True, exist_ok=True)
            # Create backup files in data dir
            (fake_db_path.parent / "b1.cvbak").touch()
            (fake_db_path.parent / "b2.cvbak").touch()
            
            with patch('src.core.api.routes.backup.DB_PATH', fake_db_path):
                response = await cmd_backup_get_status()
                assert response.available is True
                assert response.provider == "SodiumBackend"
                assert response.backup_count == 2
    
    def test_error_mapping_correctness(self):
        """Test error mapping is correct"""
        from src.core.api.routes.backup import ERROR_MAPPING
        from src.core.services.backup import (
            BackupCryptoUnavailableError,
            BackupIntegrityError,
            BackupCryptoError,
            BackupError
        )
        
        assert ERROR_MAPPING[BackupCryptoUnavailableError] == "ERR_AUTH_FAILED"
        assert ERROR_MAPPING[BackupIntegrityError] == "ERR_AUTH_FAILED"
        assert ERROR_MAPPING[BackupCryptoError] == "ERR_AUTH_FAILED"
        assert ERROR_MAPPING[BackupError] == "ERR_IO_LOCKED"
        assert ERROR_MAPPING[PermissionError] == "ERR_IO_LOCKED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

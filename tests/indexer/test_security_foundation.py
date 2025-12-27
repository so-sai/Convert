"""
TEST_SECURITY_FOUNDATION.PY - 5 Kill-Switch Security Tests for IndexerStorage
Task 6.4 - Sprint 6 Background Services

DIRECTIVE: #SECURITY_FOUNDATION_FIRST
Phase: RED (All tests MUST FAIL initially)

Test Categories:
- T19: Path Sanitization (Anti-Traversal)
- T20: Sandbox Timeout Enforcement (10s)
- T21: SQLCipher AES-256 Encryption at Rest
- T22: Resource Quota (512MB Memory Limit)
- T23: Input Validation (MIME Safety)
"""

import asyncio
import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Imports will be available after implementation
try:
    from src.core.indexer.security import PathGuard, InputValidator
except ImportError:
    PathGuard = None
    InputValidator = None

try:
    from src.core.indexer.sandbox import SandboxExecutor, SandboxError
except ImportError:
    SandboxExecutor = None
    SandboxError = Exception

try:
    from src.core.indexer.encrypted_storage import EncryptedIndexerDB
except ImportError:
    EncryptedIndexerDB = None


# ===================================================================
# T19: PATH SANITIZATION (ANTI-TRAVERSAL)
# ===================================================================

class TestPathSanitization(unittest.TestCase):
    """T19: Prevent path traversal attacks"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.temp_dir) / "vault"
        self.vault_root.mkdir(exist_ok=True)
        
        # Create a legitimate file inside vault
        self.safe_file = self.vault_root / "document.txt"
        self.safe_file.write_text("Safe content")
        
        # Create a file outside vault (attack target)
        self.outside_file = Path(self.temp_dir) / "secret.txt"
        self.outside_file.write_text("SECRET DATA")
    
    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    @pytest.mark.security
    def test_T19_01_block_dot_dot_traversal(self):
        """T19.01: Block '../' path traversal attempts"""
        guard = PathGuard(vault_root=self.vault_root)
        
        # Attack: Try to escape vault with ../
        attack_path = "../secret.txt"
        
        with self.assertRaises(ValueError) as ctx:
            guard.validate(attack_path)
        
        self.assertIn("traversal", str(ctx.exception).lower())
        print("\n   ✅ T19.01: '../' traversal blocked")
    
    @pytest.mark.security
    def test_T19_02_block_absolute_path_escape(self):
        """T19.02: Block absolute paths pointing outside vault"""
        guard = PathGuard(vault_root=self.vault_root)
        
        # Attack: Try to access file with absolute path
        attack_path = str(self.outside_file.absolute())
        
        with self.assertRaises(ValueError) as ctx:
            guard.validate(attack_path)
        
        self.assertIn("outside", str(ctx.exception).lower())
        print("\n   ✅ T19.02: Absolute path escape blocked")
    
    @pytest.mark.security
    def test_T19_03_allow_safe_relative_path(self):
        """T19.03: Allow legitimate relative paths inside vault"""
        guard = PathGuard(vault_root=self.vault_root)
        
        # Valid path inside vault
        safe_path = "document.txt"
        
        result = guard.validate(safe_path)
        
        self.assertEqual(result, self.safe_file)
        print("\n   ✅ T19.03: Safe relative path allowed")
    
    @pytest.mark.security
    @pytest.mark.skipif(os.name != 'nt', reason="Windows symlink test")
    def test_T19_04_block_symlink_escape(self):
        """T19.04: Block symlinks pointing outside vault (Windows)"""
        guard = PathGuard(vault_root=self.vault_root)
        
        # Create symlink inside vault pointing outside
        symlink_path = self.vault_root / "evil_link"
        try:
            symlink_path.symlink_to(self.outside_file)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not available")
        
        with self.assertRaises(ValueError) as ctx:
            guard.validate("evil_link")
        
        self.assertIn("symlink", str(ctx.exception).lower())
        print("\n   ✅ T19.04: Symlink escape blocked")


# ===================================================================
# T20: SANDBOX TIMEOUT ENFORCEMENT
# ===================================================================

class TestSandboxTimeout:
    """T20: Enforce timeout on sandboxed processes (pytest-native)"""
    
    @pytest.fixture(autouse=True)
    def setup_temp_dir(self, tmp_path):
        self.temp_dir = tmp_path
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_T20_01_kill_long_running_process(self):
        """T20.01: Kill process that exceeds 10-second timeout"""
        executor = SandboxExecutor(timeout_seconds=2)  # Use 2s for test speed
        
        # Command that runs forever
        if os.name == 'nt':
            infinite_command = ["python", "-c", "import time; time.sleep(100)"]
        else:
            infinite_command = ["python3", "-c", "import time; time.sleep(100)"]
        
        start = time.time()
        
        with pytest.raises(SandboxError) as exc_info:
            await executor.execute(infinite_command)
        
        elapsed = time.time() - start
        
        # Should timeout within 2-3 seconds
        assert elapsed < 5.0, "Timeout should trigger quickly"
        assert "timeout" in str(exc_info.value).lower()
        print(f"\n   ✅ T20.01: Long-running process killed after {elapsed:.1f}s")
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_T20_02_allow_fast_process(self):
        """T20.02: Allow processes that complete within timeout"""
        executor = SandboxExecutor(timeout_seconds=5)
        
        # Quick command
        if os.name == 'nt':
            quick_command = ["python", "-c", "print('Hello')"]
        else:
            quick_command = ["python3", "-c", "print('Hello')"]
        
        result = await executor.execute(quick_command)
        
        assert b"Hello" in result
        print("\n   ✅ T20.02: Fast process completed normally")


# ===================================================================
# T21: SQLCIPHER AES-256 ENCRYPTION AT REST
# ===================================================================

class TestSQLCipherEncryption(unittest.TestCase):
    """T21: Verify database encryption at rest (SQLCipher or PyNaCl fallback)"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "encrypted.db"
        self.test_key = b"test_encryption_key_32_bytes_ok!"  # 32 bytes
    
    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    @pytest.mark.security
    def test_T21_01_create_encrypted_database(self):
        """T21.01: Create encrypted database with key protection"""
        db = EncryptedIndexerDB(
            db_path=self.db_path, 
            key=self.test_key
        )
        
        # Create table and insert data
        conn = db.connect()
        conn.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER, data TEXT)")
        conn.execute("INSERT INTO secrets VALUES (1, 'TOP SECRET')")
        db.commit()
        db.close()
        
        # Verify file exists
        self.assertTrue(self.db_path.exists())
        print("\n   ✅ T21.01: Encrypted database created")
    
    @pytest.mark.security
    def test_T21_02_verify_encryption_active(self):
        """T21.02: Verify encryption is properly configured"""
        # First, create encrypted database
        db = EncryptedIndexerDB(
            db_path=self.db_path,
            key=self.test_key
        )
        conn = db.connect()
        conn.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER, data TEXT)")
        conn.execute("INSERT INTO secrets VALUES (1, 'TOP SECRET')")
        db.commit()
        db.close()
        
        # Verify encryption is active
        db2 = EncryptedIndexerDB(
            db_path=self.db_path,
            key=self.test_key
        )
        
        is_encrypted = db2.verify_encryption()
        self.assertTrue(is_encrypted, "Database should be encrypted")
        
        db2.close()
        print("\n   ✅ T21.02: Encryption verification passed")
    
    @pytest.mark.security
    def test_T21_03_verify_encryption_settings(self):
        """T21.03: Verify correct encryption parameters"""
        db = EncryptedIndexerDB(
            db_path=self.db_path,
            key=self.test_key
        )
        db.connect()
        
        settings = db.get_cipher_settings()
        
        # Verify settings exist
        self.assertIn('provider', settings)
        self.assertIn('kdf_iter', settings)
        self.assertIn('cipher_page_size', settings)
        
        # PBKDF2 with 256K iterations (or equivalent)
        self.assertGreaterEqual(settings['kdf_iter'], 256000)
        
        # Page size 4096
        self.assertEqual(settings['cipher_page_size'], 4096)
        
        db.close()
        print(f"\n   ✅ T21.03: Cipher settings verified (Provider: {settings['provider']}, KDF: {settings['kdf_iter']} iter)")
    
    @pytest.mark.security
    def test_T21_04_wrong_key_rejected(self):
        """T21.04: Wrong key should be rejected"""
        # First, create encrypted database with correct key
        db = EncryptedIndexerDB(
            db_path=self.db_path,
            key=self.test_key
        )
        conn = db.connect()
        conn.execute("CREATE TABLE IF NOT EXISTS secrets (id INTEGER, data TEXT)")
        conn.execute("INSERT INTO secrets VALUES (1, 'TOP SECRET')")
        db.commit()
        db.close()
        
        # Try to open with wrong key
        wrong_key = b"wrong_key_that_should_not_work!!"  # Different 32 bytes
        db2 = EncryptedIndexerDB(
            db_path=self.db_path,
            key=wrong_key
        )
        
        with self.assertRaises(RuntimeError) as ctx:
            db2.connect()
        
        self.assertIn("key", str(ctx.exception).lower())
        print("\n   ✅ T21.04: Wrong key correctly rejected")


# ===================================================================
# T22: RESOURCE QUOTA (MEMORY LIMIT)
# ===================================================================

class TestResourceQuota:
    """T22: Enforce memory limits on sandboxed processes (pytest-native)"""
    
    @pytest.fixture(autouse=True)
    def setup_temp_dir(self, tmp_path):
        self.temp_dir = tmp_path
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_T22_01_kill_memory_hog(self):
        """T22.01: Kill process that exceeds 512MB memory limit"""
        executor = SandboxExecutor(
            timeout_seconds=30,
            memory_limit_mb=50  # Use 50MB for test speed
        )
        
        # Memory bomb: allocate 100MB and TOUCH it to force commit, then wait to be killed
        memory_bomb = """
import time
# Allocate and touch 100MB to force Windows to commit the memory
data = bytearray(100 * 1024 * 1024)
data[0] = 1
data[-1] = 1
# Wait to give monitor time to detect and kill
time.sleep(5)
print('Should not reach here')
"""
        
        if os.name == 'nt':
            command = ["python", "-c", memory_bomb]
        else:
            command = ["python3", "-c", memory_bomb]
        
        with pytest.raises(SandboxError) as exc_info:
            await executor.execute(command)
        
        assert "memory" in str(exc_info.value).lower()
        print("\n   ✅ T22.01: Memory hog process killed")
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_T22_02_allow_normal_memory_usage(self):
        """T22.02: Allow normal memory usage within limit"""
        executor = SandboxExecutor(
            timeout_seconds=10,
            memory_limit_mb=100
        )
        
        # Normal script using ~5MB
        normal_script = """
data = bytearray(5 * 1024 * 1024)  # 5MB
print('OK')
"""
        
        if os.name == 'nt':
            command = ["python", "-c", normal_script]
        else:
            command = ["python3", "-c", normal_script]
        
        result = await executor.execute(command)
        
        assert b"OK" in result
        print("\n   ✅ T22.02: Normal memory usage allowed")


# ===================================================================
# T23: INPUT VALIDATION (MIME SAFETY)
# ===================================================================

class TestInputValidation(unittest.TestCase):
    """T23: Validate file types and MIME signatures"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    @pytest.mark.security
    def test_T23_01_allow_pdf(self):
        """T23.01: Allow PDF files (magic bytes check)"""
        validator = InputValidator()
        
        # Create fake PDF with magic bytes
        pdf_file = self.temp_path / "document.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n%fake content")
        
        result = validator.validate(pdf_file)
        
        self.assertTrue(result.allowed)
        self.assertEqual(result.mime_type, "application/pdf")
        print("\n   ✅ T23.01: PDF files allowed")
    
    @pytest.mark.security
    def test_T23_02_block_executable(self):
        """T23.02: Block executable files (EXE, DLL, etc.)"""
        validator = InputValidator()
        
        # Create fake EXE with magic bytes (MZ header)
        exe_file = self.temp_path / "malware.pdf"  # Disguised as PDF
        exe_file.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00")
        
        with self.assertRaises(ValueError) as ctx:
            validator.validate(exe_file)
        
        self.assertIn("executable", str(ctx.exception).lower())
        print("\n   ✅ T23.02: Executable files blocked")
    
    @pytest.mark.security
    def test_T23_03_allow_docx(self):
        """T23.03: Allow DOCX files (ZIP-based Office)"""
        validator = InputValidator()
        
        # DOCX is a ZIP file with specific structure
        docx_file = self.temp_path / "document.docx"
        # PK signature (ZIP)
        docx_file.write_bytes(b"PK\x03\x04" + b"\x00" * 100)
        
        result = validator.validate(docx_file)
        
        self.assertTrue(result.allowed)
        print("\n   ✅ T23.03: DOCX files allowed")
    
    @pytest.mark.security
    def test_T23_04_block_script_disguised_as_text(self):
        """T23.04: Block scripts disguised as text files"""
        validator = InputValidator()
        
        # Create malicious script with .txt extension
        script_file = self.temp_path / "readme.txt"
        script_file.write_text("#!/bin/bash\nrm -rf /")
        
        # Validator should detect shebang and block
        with self.assertRaises(ValueError) as ctx:
            validator.validate(script_file)
        
        self.assertIn("script", str(ctx.exception).lower())
        print("\n   ✅ T23.04: Disguised scripts blocked")
    
    @pytest.mark.security
    def test_T23_05_allow_images(self):
        """T23.05: Allow image files (PNG, JPG)"""
        validator = InputValidator()
        
        # PNG magic bytes
        png_file = self.temp_path / "image.png"
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        
        result = validator.validate(png_file)
        
        self.assertTrue(result.allowed)
        self.assertEqual(result.mime_type, "image/png")
        print("\n   ✅ T23.05: Image files allowed")


# ===================================================================
# MAIN RUNNER
# ===================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)

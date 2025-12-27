"""
TEST_PIPELINE_INTEGRATION.PY - Integration Tests for Extraction Pipeline
Task 6.5 - Sprint 6 Background Services

T30.01 - T30.04: Golden Path and Failure Scenarios
"""

import unittest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import MagicMock

# Core components
from src.core.indexer.pipeline import ExtractionPipeline
from src.core.indexer.utils.idempotency import PipelineStatus
from src.core.indexer.encrypted_storage import EncryptedIndexerDB

class TestPipelineIntegration(unittest.TestCase):
    """
    Integration tests for the Extraction Pipeline.
    
    Verifies the end-to-end flow from file detection to database storage.
    """
    
    def setUp(self):
        # 1. Setup temporary workspace
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "test_indexer.db"
        
        # 2. Setup mock/real EncryptedIndexerDB
        self.db = EncryptedIndexerDB(self.db_path, key=b"0"*32)
        self.db.connect()
        
        # 3. Create schema (MDS Protocol 2025 Standard)
        self.db.execute("CREATE VIRTUAL TABLE document_content USING fts5(content)")
        self.db.execute("""
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                filename TEXT,
                mime_type TEXT,
                total_chars INTEGER,
                created_at TEXT
            )
        """)
        self.db.commit()
        
        # 4. Initialize Pipeline
        self.pipeline = ExtractionPipeline(self.db)
        
        # Setup sample files
        self.pdf_file = self.test_dir / "sample.pdf"
        self.docx_file = self.test_dir / "sample.docx"
        self.corrupt_file = self.test_dir / "corrupt.pdf"
        
        # Mock extractors to focus on pipeline logic
        self.mock_extractor = MagicMock()
        # Wire up registry to return our mock
        self.pipeline.registry.get_extractor = MagicMock(return_value=self.mock_extractor)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.test_dir)

    def test_T30_01_pdf_golden_path(self):
        """T30.01: PDF drop -> FTS5 storage -> Searchable"""
        # Import the real ExtractionResult class
        from src.core.indexer.extractors.result import ExtractionResult, TextSegment
        
        # Arrange
        self.pdf_file.touch()
        
        # Create REAL ExtractionResult
        mock_result = ExtractionResult(
            segments=[TextSegment(text="This is a secret message in PDF", page=1)],
            metadata={"page_count": 1},
            processing_time_ms=50.0,
            file_size_bytes=2048,
            errors=[],
            truncated=False,
            extractor="pdf_pymupdf",
            version="1.26.2"
        )
        
        self.mock_extractor.extract.return_value = mock_result
        
        # Act
        status = self.pipeline.process_file(self.pdf_file)
        
        # Assert
        self.assertEqual(status, PipelineStatus.INDEXED)
        
        # Verify Metadata Database
        cursor = self.db.execute("SELECT filename, total_chars FROM documents WHERE filename='sample.pdf'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], 31)  # Actual length of "This is a secret message in PDF"
        
        # Verify FTS5 Search
        cursor = self.db.execute("SELECT content FROM document_content WHERE document_content MATCH 'secret'")
        row = cursor.fetchone()
        self.assertIsNotNone(row, "Content should be searchable in FTS5")
        self.assertIn("secret message", row[0])

    def test_T30_03_corrupted_file_quarantine(self):
        """T30.03: Corrupted file -> QUARANTINED status"""
        # Arrange
        self.corrupt_file.touch()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.errors = [MagicMock(recoverable=False, message="File corrupted")]
        self.mock_extractor.extract.return_value = mock_result
        
        # Act
        status = self.pipeline.process_file(self.corrupt_file)
        
        # Assert
        self.assertEqual(status, PipelineStatus.QUARANTINED)
        
        # Verify NOTHING was stored in metadata table
        cursor = self.db.execute("SELECT count(*) FROM documents")
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_T30_04_idempotency_skip(self):
        """T30.04: Duplicate metadata events -> skip processing"""
        # Import the real ExtractionResult class
        from src.core.indexer.extractors.result import ExtractionResult, TextSegment
        
        # Arrange
        self.pdf_file.touch()
        
        # Create REAL ExtractionResult (not Mock) to avoid SQLite binding errors
        mock_result = ExtractionResult(
            segments=[TextSegment(text="Content", page=1)],
            metadata={"test": "data"},
            processing_time_ms=10.0,
            file_size_bytes=1024,
            errors=[],
            truncated=False,
            extractor="pdf_pymupdf",
            version="1.0.0"
        )
        
        self.mock_extractor.extract.return_value = mock_result
        
        # Act
        # First call
        status1 = self.pipeline.process_file(self.pdf_file)
        # Second call (same metadata)
        status2 = self.pipeline.process_file(self.pdf_file)
        
        # Assert
        self.assertEqual(status1, PipelineStatus.INDEXED)
        self.assertEqual(status2, PipelineStatus.INDEXED)
        
        # CRITICAL: Extractor should ONLY be called once
        self.assertEqual(self.mock_extractor.extract.call_count, 1)
        
        # Check stats
        stats = self.pipeline.get_stats()
        self.assertEqual(stats['idempotency']['completed'], 1)

    def test_T30_05_metadata_update_on_change(self):
        """Bonus: If file mtime changes, it should re-index"""
        # Import the real ExtractionResult class
        from src.core.indexer.extractors.result import ExtractionResult, TextSegment
        
        # Arrange
        self.pdf_file.touch()
        
        # Create REAL ExtractionResult for version 1
        mock_result_v1 = ExtractionResult(
            segments=[TextSegment(text="Version 1", page=1)],
            metadata={},
            processing_time_ms=10.0,
            file_size_bytes=512,
            errors=[],
            truncated=False,
            extractor="pdf_pymupdf",
            version="1.0.0"
        )
        
        self.mock_extractor.extract.return_value = mock_result_v1
        
        # Act
        self.pipeline.process_file(self.pdf_file)
        
        # Simulate file modification (Wait a bit and change mtime)
        time.sleep(0.01)
        self.pdf_file.write_text("modified") # Change content/metadata
        
        # Create REAL ExtractionResult for version 2
        mock_result_v2 = ExtractionResult(
            segments=[TextSegment(text="Version 2", page=1)],
            metadata={},
            processing_time_ms=10.0,
            file_size_bytes=1024,
            errors=[],
            truncated=False,
            extractor="pdf_pymupdf",
            version="1.0.0"
        )
        
        self.mock_extractor.extract.return_value = mock_result_v2
        self.pipeline.process_file(self.pdf_file)
        
        # Assert
        # Extractor should be called TWICE because mtime changed
        self.assertEqual(self.mock_extractor.extract.call_count, 2)

    def test_T30_06_docx_golden_path(self):
        """T30.06: DOCX drop -> FTS5 storage -> Searchable"""
        # Import the real ExtractionResult class
        from src.core.indexer.extractors.result import ExtractionResult, TextSegment
        
        # Arrange
        self.docx_file.touch()
        
        # Create REAL ExtractionResult for DOCX
        mock_result = ExtractionResult(
            segments=[TextSegment(text="Hello from DOCX document", page=None, section="paragraph_0")],
            metadata={"paragraph_count": 1},
            processing_time_ms=40.0,
            file_size_bytes=1536,
            errors=[],
            truncated=False,
            extractor="docx_python",
            version="1.0.0-python-fallback"
        )
        
        self.mock_extractor.extract.return_value = mock_result
        
        # Act
        status = self.pipeline.process_file(self.docx_file)
        
        # Assert
        self.assertEqual(status, PipelineStatus.INDEXED)
        
        # Verify FTS5 Search
        cursor = self.db.execute("SELECT content FROM document_content WHERE document_content MATCH 'DOCX'")
        row = cursor.fetchone()
        self.assertIsNotNone(row, "DOCX content should be searchable in FTS5")
        self.assertIn("DOCX", row[0])

    def test_T30_07_degraded_extraction(self):
        """T30.07: Extractor partial failure -> DEGRADED (metadata only)"""
        # Import the real ExtractionResult class
        from src.core.indexer.extractors.result import ExtractionResult, ExtractionError
        
        # Arrange
        self.pdf_file.touch()
        
        # Create REAL ExtractionResult with partial success
        mock_result = ExtractionResult(
            segments=[],  # No content extracted
            metadata={"page_count": 5, "size": 2048},
            processing_time_ms=100.0,
            file_size_bytes=2048,
            errors=[ExtractionError(code="CORRUPTED", message="Page 3 corrupted", recoverable=True)],
            truncated=True,
            extractor="pdf_pymupdf",
            version="1.26.2"
        )
        
        self.mock_extractor.extract.return_value = mock_result
        
        # Act
        status = self.pipeline.process_file(self.pdf_file)
        
        # Assert
        # Should be DEGRADED because we have errors but they're recoverable
        # and we have metadata even though no content
        self.assertEqual(status, PipelineStatus.DEGRADED)

    def test_T30_08_retry_on_permission_error(self):
        """T30.08: File locked/permission denied -> RETRY status"""
        # Import the real ExtractionResult class
        from src.core.indexer.extractors.result import ExtractionResult
        
        # Arrange
        self.pdf_file.touch()
        
        # Simulate permission error during extraction
        self.mock_extractor.extract.side_effect = PermissionError("File is locked by another process")
        
        # Act
        status = self.pipeline.process_file(self.pdf_file)
        
        # Assert
        # Should return RETRY for transient errors
        self.assertEqual(status, PipelineStatus.RETRY)

    def test_T30_09_unsupported_file_type(self):
        """T30.09: Unsupported file type -> DEGRADED (no extractor available)"""
        # Arrange
        txt_file = self.test_dir / "test.txt"
        txt_file.write_text("Plain text content")
        
        # Registry will return None for unsupported MIME types
        self.pipeline.registry.get_extractor = MagicMock(return_value=None)
        
        # Act
        status = self.pipeline.process_file(txt_file)
        
        # Assert
        # Should return DEGRADED when no extractor is available
        self.assertEqual(status, PipelineStatus.DEGRADED)

if __name__ == '__main__':
    unittest.main()

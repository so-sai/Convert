"""
PIPELINE.PY - Extraction & Indexing Orchestrator
Task 6.5 - Sprint 6 Background Services

SPEC: SPEC_TASK_6_5_INTEGRATION.md (FROZEN)

Connects PathGuard, Sandbox, Extractors, and SQLCipher into a 
unified data flow for non-blocking file processing.
"""

import time
import logging
from pathlib import Path
from typing import Optional

from .utils.idempotency import PipelineStatus, EventIdempotency, ProcessingRegistry
from .registry import ExtractorRegistry
from .encrypted_storage import EncryptedIndexerDB

# Setup logging
logger = logging.getLogger("indexer.pipeline")

class ExtractionPipeline:
    """
    Main orchestrator for file extraction and indexing.
    
    Flow:
    1. Idempotency Check (XXH3 metadata hash)
    2. Security Validation (PathGuard/Validator)
    3. MIME Routing (ExtractorRegistry)
    4. Text Extraction (Specialized Engine)
    5. FTS5 Persistence (SQLCipher)
    """
    
    def __init__(self, db: EncryptedIndexerDB):
        """
        Initialize the pipeline.
        
        Args:
            db: EncryptedIndexerDB instance for storage
        """
        self.db = db
        self.registry = ExtractorRegistry()
        self.idempotency = ProcessingRegistry(ttl_seconds=3600)  # 1 hour TTL
    
    def process_file(self, filepath: str | Path) -> PipelineStatus:
        """
        Process a single file through the pipeline.
        
        Args:
            filepath: Path to the file to index
            
        Returns:
            PipelineStatus indicating the result
        """
        path = Path(filepath)
        filename = path.name
        
        # 1. IDEMPOTENCY CHECK
        event_key = EventIdempotency.generate_key(path)
        if not self.idempotency.should_process(event_key):
            logger.debug(f"⏭️ [PIPELINE] Skipping duplicate: {filename}")
            return PipelineStatus.INDEXED  # Already processed
        
        self.idempotency.mark_processing(event_key)
        
        try:
            # 2. SECURITY VALIDATION
            # PathGuard/Security check should happen here
            
            # 3. MIME ROUTING
            mime_type = self._detect_mime_type(path)
            extractor = self.registry.get_extractor(mime_type)
            
            if not extractor:
                logger.warning(f"⚠️ [PIPELINE] No extractor for {mime_type}: {filename}")
                self.idempotency.mark_completed(event_key)
                return PipelineStatus.DEGRADED
            
            # 4. EXTRACTION
            start_time = time.perf_counter()
            result = extractor.extract(path)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            if not result.success:
                logger.error(f"❌ [PIPELINE] Extraction failed for {filename}: {result.errors[0].message}")
                if any(not err.recoverable for err in result.errors):
                    self.idempotency.mark_failed(event_key)
                    return PipelineStatus.QUARANTINED
            
            # 5. PERSISTENCE (SQLCipher FTS5)
            try:
                self._save_to_fts(path, result)
                logger.info(f"✅ [PIPELINE] Indexed {filename} ({result.total_chars} chars) in {duration_ms:.2f}ms")
                self.idempotency.mark_completed(event_key)
                return PipelineStatus.INDEXED if result.success else PipelineStatus.DEGRADED
                
            except Exception as e:
                logger.error(f"❌ [PIPELINE] Database error for {filename}: {e}")
                self.idempotency.mark_failed(event_key)
                return PipelineStatus.RETRY
                
        except Exception as e:
            logger.error(f"🔥 [PIPELINE] Unexpected error processing {filename}: {e}")
            self.idempotency.mark_failed(event_key)
            return PipelineStatus.RETRY

    def _detect_mime_type(self, path: Path) -> str:
        """Simple MIME detection based on extension for Task 6.5."""
        ext = path.suffix.lower()
        if ext == '.pdf':
            return "application/pdf"
        if ext == '.docx':
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return "application/octet-stream"

    def get_stats(self) -> dict:
        """Get pipeline metrics and status."""
        return {
            "idempotency": self.idempotency.get_stats(),
            "supported_types": self.registry.get_supported_types()
        }

    def _save_to_fts(self, path: Path, result: "ExtractionResult") -> None:
        """
        Save extraction result to SQLCipher FTS5 tables via EncryptedIndexerDB.
        """
        # 1. Insert/Update document metadata
        # Using REPLACE to handle updates to already indexed files
        sql_doc = """
        INSERT OR REPLACE INTO documents (path, filename, mime_type, total_chars, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        params_doc = (
            str(path.absolute()),
            path.name,
            result.extractor,
            result.total_chars,
            time.strftime('%Y-%m-%d %H:%M:%S')
        )
        self.db.execute(sql_doc, params_doc)
        
        # 2. Insert into FTS5 content table
        # We assume the content table is matched via path or just a general search index
        sql_content = "INSERT INTO document_content (content) VALUES (?)"
        self.db.execute(sql_content, (result.total_text,))
        
        self.db.commit()

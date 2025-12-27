"""
PDF_EXTRACTOR.PY - PyMuPDF-based PDF Text Extraction
Task 6.4 - Sprint 6 Background Services

Uses PyMuPDF (fitz) 1.26.x for high-performance PDF extraction.
Integrates with security foundation (PathGuard, InputValidator, SandboxExecutor).
"""

import time
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from .result import ExtractionResult, TextSegment, ExtractionError


class PDFExtractor:
    """
    PyMuPDF-based PDF text extractor.
    
    Features:
    - Text extraction with page tracking
    - Metadata extraction (title, author, page count, etc.)
    - Graceful degradation for corrupted PDFs
    - Performance tracking
    
    Security:
    - Should be called through SandboxExecutor for resource limits
    - PathGuard validation before calling
    - InputValidator magic bytes check before calling
    """
    
    VERSION = "1.0.0"
    EXTRACTOR_NAME = "pdf_pymupdf"
    
    def __init__(self):
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError(
                "PyMuPDF not available. Install with: pip install PyMuPDF>=1.26"
            )
    
    def extract(self, file_path: Path) -> ExtractionResult:
        """
        Extract text and metadata from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            ExtractionResult with text segments and metadata
            
        Note:
            This method does NOT perform security checks.
            Caller must validate path and input before calling.
        """
        start_time = time.perf_counter()
        result = ExtractionResult(
            extractor=self.EXTRACTOR_NAME,
            version=self.VERSION
        )
        
        # Get file size
        try:
            result.file_size_bytes = file_path.stat().st_size
        except Exception:
            result.file_size_bytes = 0
        
        # Open PDF
        doc = None
        try:
            doc = fitz.open(str(file_path))
        except fitz.FileNotFoundError:
            result.add_error(
                ExtractionError.FILE_NOT_FOUND,
                f"PDF file not found: {file_path}",
                recoverable=False
            )
            result.processing_time_ms = (time.perf_counter() - start_time) * 1000
            return result
        except fitz.FileDataError as e:
            result.add_error(
                ExtractionError.CORRUPTED,
                f"Corrupted or invalid PDF: {e}",
                recoverable=False
            )
            result.processing_time_ms = (time.perf_counter() - start_time) * 1000
            return result
        except Exception as e:
            result.add_error(
                ExtractionError.INVALID_FORMAT,
                f"Failed to open PDF: {e}",
                recoverable=False
            )
            result.processing_time_ms = (time.perf_counter() - start_time) * 1000
            return result
        
        try:
            # Extract metadata
            result.metadata = self._extract_metadata(doc)
            
            # Check for password protection
            if doc.needs_pass:
                result.add_error(
                    ExtractionError.PASSWORD_PROTECTED,
                    "PDF is password protected",
                    recoverable=False
                )
                return result
            
            # Extract text from each page
            page_count = len(doc)
            for page_num in range(page_count):
                try:
                    page = doc[page_num]
                    text = page.get_text()
                    
                    # Only add non-empty pages
                    if text.strip():
                        result.segments.append(TextSegment(
                            text=text,
                            page=page_num + 1,  # 1-indexed for user display
                            confidence=1.0
                        ))
                except Exception as e:
                    # Partial extraction: log error but continue
                    result.add_error(
                        ExtractionError.CORRUPTED,
                        f"Failed to extract page {page_num + 1}: {e}",
                        recoverable=True
                    )
                    result.truncated = True
            
            # If we got some segments despite errors, mark as partial success
            if len(result.segments) > 0 and len(result.errors) > 0:
                result.truncated = True
                
        except Exception as e:
            result.add_error(
                ExtractionError.CORRUPTED,
                f"Extraction failed: {e}",
                recoverable=len(result.segments) > 0
            )
        finally:
            if doc:
                doc.close()
            result.processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        return result
    
    def _extract_metadata(self, doc: "fitz.Document") -> dict:
        """Extract metadata from PDF document"""
        metadata = {
            "page_count": len(doc),
        }
        
        # Extract standard metadata fields
        try:
            pdf_metadata = doc.metadata
            if pdf_metadata:
                # Map PyMuPDF metadata keys to our standard keys
                key_mapping = {
                    "title": "title",
                    "author": "author",
                    "subject": "subject",
                    "keywords": "keywords",
                    "creator": "creator",
                    "producer": "producer",
                    "creationDate": "creation_date",
                    "modDate": "modification_date",
                }
                
                for pdf_key, our_key in key_mapping.items():
                    value = pdf_metadata.get(pdf_key)
                    if value:
                        metadata[our_key] = value
        except Exception:
            # Metadata extraction is non-critical
            pass
        
        return metadata


def extract_pdf(file_path: Path) -> ExtractionResult:
    """
    Convenience function for PDF extraction.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        ExtractionResult
        
    Note:
        This is a convenience wrapper. For production use,
        call through SandboxExecutor with security checks.
    """
    extractor = PDFExtractor()
    return extractor.extract(file_path)

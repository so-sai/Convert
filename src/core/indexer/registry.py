"""
REGISTRY.PY - Extractor Management and Routing
Task 6.5 - Sprint 6 Background Services

Routes files to the appropriate extractor based on MIME type.
Thread-safe singleton for high-performance extraction.
"""

import threading
from typing import Dict, Optional, Type

from .extractors.pdf_extractor import PDFExtractor
from .extractors.docx_extractor import DOCXExtractor

class ExtractorRegistry:
    """
    Orchestrates the selection of extractors based on file types.
    
    Uses MIME-type mapping to route files to specialized engines.
    Implemented as a thread-safe singleton.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    _mapping = {
        # PDF: Primary Engine (PyMuPDF)
        "application/pdf": PDFExtractor,
        
        # DOCX: Bridge/Fallback Engine (python-docx)
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DOCXExtractor,
    }
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ExtractorRegistry, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize registry with extractor instances."""
        self._extractors = {}
        for mime_type, extractor_class in self._mapping.items():
            try:
                self._extractors[mime_type] = extractor_class()
            except Exception as e:
                print(f"⚠️ [REGISTRY] Failed to initialize {extractor_class.__name__}: {e}")
    
    def get_extractor(self, mime_type: str) -> Optional[object]:
        """
        Get specialized extractor for the given MIME type.
        
        Args:
            mime_type: Standardized MIME type string
            
        Returns:
            Extractor instance or None if unsupported
        """
        return self._extractors.get(mime_type)
    
    def get_supported_types(self) -> list[str]:
        """Get list of supported MIME types."""
        return list(self._extractors.keys())

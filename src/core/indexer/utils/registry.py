"""
REGISTRY.PY - Extractor Registry for MIME-based Routing
Task 6.5 - Sprint 6 Background Services

SPEC: SPEC_TASK_6_5_INTEGRATION.md (FROZEN)

Provides MIME type → Extractor class mapping.
No fallback logic here - that belongs to the pipeline.
"""

from typing import Optional

from ..extractors.pdf_extractor import PDFExtractor
from ..extractors.docx_extractor import DOCXExtractor


class ExtractorRegistry:
    """
    Registry for mapping MIME types to extractor instances.
    
    Design Principles:
    - Routing only, no fallback logic
    - Returns None for unsupported types (caller handles)
    - Stateless (can be shared across threads)
    
    Supported MIME Types:
    - application/pdf → PDFExtractor
    - application/vnd.openxmlformats-officedocument.wordprocessingml.document → DOCXExtractor
    """
    
    # Static mapping of MIME types to extractor classes
    _extractors = {
        "application/pdf": PDFExtractor,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DOCXExtractor,
    }
    
    def get_extractor(self, mime_type: str) -> Optional[object]:
        """
        Get extractor instance for given MIME type.
        
        Args:
            mime_type: MIME type string (e.g., "application/pdf")
            
        Returns:
            Extractor instance or None if unsupported
            
        Note:
            Returns None instead of raising exception.
            Caller (pipeline) decides how to handle unsupported types.
        """
        extractor_class = self._extractors.get(mime_type)
        if extractor_class is None:
            return None
        
        try:
            return extractor_class()
        except Exception:
            # If extractor initialization fails (e.g., missing dependency),
            # return None and let pipeline handle it
            return None
    
    def is_supported(self, mime_type: str) -> bool:
        """
        Check if MIME type is supported.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            True if supported, False otherwise
        """
        return mime_type in self._extractors
    
    def get_supported_types(self) -> list[str]:
        """
        Get list of all supported MIME types.
        
        Returns:
            List of supported MIME type strings
        """
        return list(self._extractors.keys())

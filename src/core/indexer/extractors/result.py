"""
RESULT.PY - Extraction Result Contract v2.0 IRON-CLAD
Task 6.4 - Sprint 6 Background Services

Standardized contract for all extractors (PDF, DOCX, etc.)
Ensures consistent behavior and graceful degradation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TextSegment:
    """
    Single text segment with metadata.
    
    Represents a logical chunk of text (e.g., paragraph, page, section)
    with optional metadata for provenance tracking.
    """
    text: str
    page: Optional[int] = None
    section: Optional[str] = None
    confidence: float = 1.0  # 0.0-1.0, for OCR or uncertain extractions
    
    def __post_init__(self):
        """Validate segment data"""
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class ExtractionError:
    """
    Extraction error details.
    
    Captures errors that occurred during extraction while allowing
    partial results to be returned.
    """
    code: str  # "CORRUPTED", "TIMEOUT", "MEMORY_LIMIT", "PASSWORD_PROTECTED", etc.
    message: str
    recoverable: bool  # True if partial extraction succeeded
    
    # Standard error codes
    CORRUPTED = "CORRUPTED"
    TIMEOUT = "TIMEOUT"
    MEMORY_LIMIT = "MEMORY_LIMIT"
    PASSWORD_PROTECTED = "PASSWORD_PROTECTED"
    INVALID_FORMAT = "INVALID_FORMAT"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"


@dataclass
class ExtractionResult:
    """
    Standardized extraction result (v2.0 IRON-CLAD).
    
    This contract is FROZEN and shared across all extractors.
    Any changes require AMENDMENT protocol per DOC_GOVERNANCE_RULES.md.
    
    Design Principles:
    - Graceful degradation: Partial results + errors, not exceptions
    - Performance tracking: Always measure processing time
    - Provenance: Track extractor and version
    - Metadata: Flexible dict for extractor-specific data
    """
    # Core data
    segments: List[TextSegment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    processing_time_ms: float = 0.0
    file_size_bytes: int = 0
    
    # Error handling
    errors: List[ExtractionError] = field(default_factory=list)
    truncated: bool = False  # True if extraction incomplete
    
    # Provenance
    extractor: str = "unknown"  # "pdf_pymupdf", "docx_rust", etc.
    version: str = "1.0"  # Extractor version
    
    @property
    def success(self) -> bool:
        """True if extraction succeeded without errors"""
        return len(self.errors) == 0
    
    @property
    def partial_success(self) -> bool:
        """True if some content extracted despite errors"""
        return len(self.segments) > 0 and len(self.errors) > 0
    
    @property
    def total_text(self) -> str:
        """Concatenate all segment text"""
        return "\n\n".join(seg.text for seg in self.segments)
    
    @property
    def total_chars(self) -> int:
        """Total character count across all segments"""
        return sum(len(seg.text) for seg in self.segments)
    
    def add_error(self, code: str, message: str, recoverable: bool = False) -> None:
        """Add an error to the result"""
        self.errors.append(ExtractionError(
            code=code,
            message=message,
            recoverable=recoverable
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "segments": [
                {
                    "text": seg.text,
                    "page": seg.page,
                    "section": seg.section,
                    "confidence": seg.confidence
                }
                for seg in self.segments
            ],
            "metadata": self.metadata,
            "processing_time_ms": self.processing_time_ms,
            "file_size_bytes": self.file_size_bytes,
            "errors": [
                {
                    "code": err.code,
                    "message": err.message,
                    "recoverable": err.recoverable
                }
                for err in self.errors
            ],
            "truncated": self.truncated,
            "extractor": self.extractor,
            "version": self.version,
            "success": self.success,
            "partial_success": self.partial_success,
            "total_chars": self.total_chars
        }

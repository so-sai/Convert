"""
SECURITY.PY - Path Sanitization & Input Validation for IndexerStorage
Task 6.4 - Sprint 6 Background Services

T19: PathGuard - Prevent path traversal attacks
T23: InputValidator - MIME type and content validation
"""

import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set


@dataclass
class ValidationResult:
    """Result of input validation"""
    allowed: bool
    mime_type: str
    reason: Optional[str] = None


class PathGuard:
    """
    T19: Path Traversal Prevention
    
    Validates all file paths stay inside vault root.
    Blocks: ../, symlinks escaping, absolute paths outside root.
    """
    
    def __init__(self, vault_root: Path):
        self.vault_root = vault_root.resolve()
    
    def validate(self, path: str) -> Path:
        """
        Validate path is safe and inside vault.
        
        Args:
            path: Relative or absolute path to validate
            
        Returns:
            Resolved Path object pointing to file inside vault
            
        Raises:
            ValueError: If path escapes vault or is unsafe
        """
        # Convert to Path object
        input_path = Path(path)
        
        # Step 1: Check for obvious traversal patterns
        path_str = str(path)
        if '..' in path_str:
            raise ValueError(
                f"Path traversal detected: path contains '..' component"
            )
        
        # Step 2: Resolve the path
        if input_path.is_absolute():
            resolved = input_path.resolve()
        else:
            resolved = (self.vault_root / input_path).resolve()
        
        # Step 3: Verify resolved path is inside vault root
        try:
            resolved.relative_to(self.vault_root)
        except ValueError:
            raise ValueError(
                f"Path escape detected: path resolves outside vault root"
            )
        
        # Step 4: Check symlink doesn't escape (if exists)
        if resolved.exists() and resolved.is_symlink():
            real_target = resolved.resolve()
            try:
                real_target.relative_to(self.vault_root)
            except ValueError:
                raise ValueError(
                    f"Symlink escape detected: symlink target is outside vault root"
                )
        
        return resolved


class InputValidator:
    """
    T23: Input MIME and Content Validation
    
    Validates file types based on magic bytes (not extension).
    Blocks executables, scripts, and suspicious content.
    """
    
    # Magic byte signatures for allowed file types
    MAGIC_SIGNATURES = {
        # PDF: %PDF
        b'%PDF': 'application/pdf',
        # PNG: 89 50 4E 47 0D 0A 1A 0A
        b'\x89PNG\r\n\x1a\n': 'image/png',
        # JPEG: FF D8 FF
        b'\xff\xd8\xff': 'image/jpeg',
        # ZIP-based (DOCX, XLSX, etc): PK
        b'PK\x03\x04': 'application/zip',
        b'PK\x05\x06': 'application/zip',
    }
    
    # Dangerous magic bytes that MUST be blocked
    BLOCKED_SIGNATURES = {
        # Windows Executable: MZ
        b'MZ': 'executable',
        # ELF (Linux executable)
        b'\x7fELF': 'executable',
        # Mach-O (macOS executable)
        b'\xfe\xed\xfa\xce': 'executable',
        b'\xfe\xed\xfa\xcf': 'executable',
        b'\xca\xfe\xba\xbe': 'executable',
    }
    
    # Script shebang patterns
    SCRIPT_PATTERNS = [
        b'#!/',           # Unix shebang
        b'#!\\',          # Windows shebang variant
        b'@echo',         # Windows batch
        b'<?php',         # PHP
        b'<%',            # ASP
    ]
    
    # Allowed MIME types
    ALLOWED_MIMES: Set[str] = {
        'application/pdf',
        'application/zip',  # DOCX, XLSX are ZIP-based
        'text/plain',
        'image/png',
        'image/jpeg',
        'image/tiff',
        # Code files (metadata only, no extraction needed)
        'text/x-python',
        'application/javascript',
        'text/html',
        'text/css',
        'application/json',
    }
    
    def validate(self, path: Path) -> ValidationResult:
        """
        Validate file is allowed type based on magic bytes.
        
        Args:
            path: Path to file to validate
            
        Returns:
            ValidationResult with mime_type and allowed status
            
        Raises:
            ValueError: If file type is blocked (executable, script, etc.)
        """
        if not path.exists():
            raise ValueError(f"File does not exist: {path}")
        
        # Read first 32 bytes for magic detection
        with open(path, 'rb') as f:
            header = f.read(32)
        
        if len(header) == 0:
            return ValidationResult(
                allowed=True,
                mime_type='application/octet-stream',
                reason='Empty file'
            )
        
        # Step 1: Check for BLOCKED signatures (executables)
        for sig, sig_type in self.BLOCKED_SIGNATURES.items():
            if header.startswith(sig):
                raise ValueError(
                    f"Blocked executable detected: file has {sig_type} signature"
                )
        
        # Step 2: Check for script patterns
        for pattern in self.SCRIPT_PATTERNS:
            if header.startswith(pattern):
                raise ValueError(
                    f"Blocked script detected: file contains script shebang or marker"
                )
        
        # Step 3: Detect MIME type from magic bytes
        detected_mime = None
        for sig, mime in self.MAGIC_SIGNATURES.items():
            if header.startswith(sig):
                detected_mime = mime
                break
        
        # Step 4: Handle text files (no magic signature)
        if detected_mime is None:
            # Check if it looks like UTF-8 text
            try:
                header.decode('utf-8')
                detected_mime = 'text/plain'
            except UnicodeDecodeError:
                detected_mime = 'application/octet-stream'
        
        # Step 5: Verify MIME is in allowed list
        if detected_mime not in self.ALLOWED_MIMES:
            return ValidationResult(
                allowed=False,
                mime_type=detected_mime,
                reason=f"MIME type {detected_mime} not in allowed list"
            )
        
        return ValidationResult(
            allowed=True,
            mime_type=detected_mime,
            reason=None
        )

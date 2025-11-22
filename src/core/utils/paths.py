# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
import sys
import urllib.parse
from pathlib import Path

def get_asset_path(relative_path: str) -> Path:
    # Fix: Single backslash replacement for Windows
    normalized = relative_path.replace('\\', '/')
    
    # Security Checks
    if normalized.startswith('//') or '\\\\' in relative_path:
        raise ValueError("Security: UNC paths not allowed")
    if '..' in normalized:
        raise ValueError("Security: Traversal detected")
        
    # Determine Base
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
    else:
        # Dev mode: src/core/utils -> src/core -> src -> ROOT
        base = Path(__file__).parent.parent.parent.parent
        
    return base / normalized

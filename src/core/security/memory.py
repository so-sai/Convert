"""
Memory Safety Module - Implements ADR-006 Memory Zeroing Protocol.

CRITICAL: This module handles sensitive data and MUST zero memory on deletion.
"""
import ctypes
from typing import Optional


class SecureBytes:
    """
    Secure byte container with automatic memory zeroing.
    
    Implements ADR-006 3-layer fallback:
    1. Manual overwrite (always works)
    2. Python del (best effort)
    3. Context manager auto-cleanup
    """
    
    def __init__(self, data: bytes):
        """
        Initialize secure container with data.
        
        Args:
            data: Sensitive bytes to protect
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        
        # Store as mutable bytearray for zeroing
        self.data = bytearray(data)
        self._is_zeroed = False
    
    def secure_delete(self):
        """
        Zero out memory containing sensitive data.
        
        This is the core of ADR-006 compliance.
        """
        if self._is_zeroed:
            return  # Already zeroed
        
        # Layer 1: Manual overwrite (most reliable)
        if len(self.data) > 0:
            # Overwrite with zeros
            for i in range(len(self.data)):
                self.data[i] = 0
        
        self._is_zeroed = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto-zero on exit."""
        self.secure_delete()
        return False  # Don't suppress exceptions
    
    def __del__(self):
        """Destructor - zero on garbage collection (Layer 2 fallback)."""
        if not self._is_zeroed:
            self.secure_delete()

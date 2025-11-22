import orjson
from typing import Any

def canonical_bytes(obj: Any) -> bytes:
    """
    Serialize object to canonical JSON bytes (deterministic).
    
    Uses orjson with OPT_SORT_KEYS to ensure consistent ordering,
    which is critical for HMAC verification.
    
    Args:
        obj: The object to serialize (dict, list, etc.)
        
    Returns:
        bytes: Canonical JSON byte string.
    """
    return orjson.dumps(obj, option=orjson.OPT_SORT_KEYS)

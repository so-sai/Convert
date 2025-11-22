import hmac
import hashlib
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class HMACService:
    def __init__(self, master_keys: dict[str, bytes]):
        """
        Initialize HMAC Service with master keys.
        
        Args:
            master_keys: Dict mapping key_version (e.g., 'v1') to raw bytes.
                         Example: {'v1': b'...', 'v2': b'...'}
        """
        if not master_keys:
            raise ValueError("At least one master key is required")
            
        self.master_keys = master_keys
        # Determine current (latest) version by sorting keys
        self.current_version = sorted(master_keys.keys())[-1]
        logger.info(f"HMACService initialized. Active Key Version: {self.current_version}")

    def _hkdf_expand(self, pseudo_random_key: bytes, info: bytes, length: int = 32) -> bytes:
        """
        HKDF-Expand (RFC 5869) using HMAC-SHA3-256.
        """
        t = b""
        okm = b""
        i = 0
        digest_size = hashlib.sha3_256().digest_size
        
        while len(okm) < length:
            i += 1
            if i > 255:
                raise ValueError("Cannot expand to more than 255 blocks")
            
            msg = t + info + bytes([i])
            t = hmac.new(pseudo_random_key, msg, hashlib.sha3_256).digest()
            okm += t
            
        return okm[:length]

    def _derive_stream_key(self, master_key: bytes, stream_id: str) -> bytes:
        """
        Derive a unique key for a specific stream using HKDF.
        Salt is empty (or could be stream_type if needed).
        Info is stream_id.
        """
        # HKDF-Extract (Salt=None -> 0s)
        # For simplicity and since master_key is high entropy, we can use it directly as PRK 
        # or strictly follow RFC. Let's follow RFC with 0-salt.
        salt = bytes([0] * hashlib.sha3_256().digest_size)
        prk = hmac.new(salt, master_key, hashlib.sha3_256).digest()
        
        # HKDF-Expand
        info = stream_id.encode('utf-8')
        return self._hkdf_expand(prk, info, length=32)

    def sign(self, payload_bytes: bytes, stream_id: str, key_version: str | None = None) -> Tuple[str, str]:
        """
        Sign payload bytes.
        
        Returns:
            (hmac_hex, key_version_used)
        """
        version = key_version or self.current_version
        if version not in self.master_keys:
            raise ValueError(f"Unknown key version: {version}")
            
        master_key = self.master_keys[version]
        stream_key = self._derive_stream_key(master_key, stream_id)
        
        hmac_obj = hmac.new(stream_key, payload_bytes, hashlib.sha3_256)
        return hmac_obj.hexdigest(), version

    def verify(self, payload_bytes: bytes, hmac_hex: str, stream_id: str, key_version: str) -> bool:
        """
        Verify HMAC for a payload.
        """
        if key_version not in self.master_keys:
            logger.warning(f"Verification failed: Unknown key version {key_version}")
            return False
            
        expected_hmac, _ = self.sign(payload_bytes, stream_id, key_version)
        return hmac.compare_digest(expected_hmac, hmac_hex)

    def rotate_key(self, new_master_key: bytes) -> str:
        """
        Add a new master key version.
        
        Returns:
            New key version identifier
        """
        # Generate next version
        # Assuming format "vN"
        try:
            current_num = int(self.current_version[1:])
            new_version = f"v{current_num + 1}"
        except ValueError:
            # Fallback if versioning scheme differs
            new_version = f"v{len(self.master_keys) + 1}"
        
        self.master_keys[new_version] = new_master_key
        self.current_version = new_version
        logger.info(f"HMAC Key Rotated. New Active Version: {self.current_version}")
        
        return new_version

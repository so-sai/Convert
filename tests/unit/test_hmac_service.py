import pytest
import hmac
import hashlib
from src.core.crypto.hmac_service import HMACService

def test_hmac_service_initialization():
    keys = {'v1': b'secret_key'}
    service = HMACService(keys)
    assert service.current_version == 'v1'

def test_hmac_service_sign_verify():
    keys = {'v1': b'secret_key'}
    service = HMACService(keys)
    payload = b'test_payload'
    stream_id = 'stream_1'
    
    # Sign
    hmac_hex, version = service.sign(payload, stream_id)
    assert version == 'v1'
    assert len(hmac_hex) == 64 # SHA3-256 hex digest length
    
    # Verify
    assert service.verify(payload, hmac_hex, stream_id, 'v1') is True
    
    # Verify failure
    assert service.verify(b'tampered', hmac_hex, stream_id, 'v1') is False
    assert service.verify(payload, 'wrong_hmac', stream_id, 'v1') is False

def test_hmac_service_key_rotation():
    keys = {'v1': b'old_key'}
    service = HMACService(keys)
    assert service.current_version == 'v1'
    
    payload = b'data'
    stream_id = 's1'
    
    # Sign with v1
    hmac_v1, ver_v1 = service.sign(payload, stream_id)
    assert ver_v1 == 'v1'
    
    # Rotate key
    new_key = b'new_master_key'
    new_ver = service.rotate_key(new_key)
    assert new_ver == 'v2'
    assert service.current_version == 'v2'
    assert service.master_keys['v2'] == new_key
    
    # Sign with v2 (default)
    hmac_v2, ver_v2 = service.sign(payload, stream_id)
    assert ver_v2 == 'v2'
    
    # Verify v1 signature (should still work)
    assert service.verify(payload, hmac_v1, stream_id, 'v1') is True
    
    # Verify v2 signature
    assert service.verify(payload, hmac_v2, stream_id, 'v2') is True
    
    # Cross verification should fail
    assert service.verify(payload, hmac_v1, stream_id, 'v2') is False

import sys
import nacl.utils
import nacl.bindings
from nacl.secret import SecretBox

def test_crypto():
    print("   [1/3] Testing High-Level API (SecretBox)...")
    try:
        key = nacl.utils.random(SecretBox.KEY_SIZE)
        box = SecretBox(key)
        msg = b"SecurityCheck"
        enc = box.encrypt(msg)
        assert box.decrypt(enc) == msg
        print("         PASS.")
    except Exception as e:
        print(f"         FAIL: {e}")
        sys.exit(1)

    print("   [2/3] Testing Low-Level Bindings (XChaCha20-Poly1305)...")
    try:
        # This verifies the DLL actually exported the symbols we need for Sprint 4
        k = nacl.utils.random(32)
        n = nacl.utils.random(24) # XChaCha Nonce
        c = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_encrypt(b"test", None, n, k)
        p = nacl.bindings.crypto_aead_xchacha20poly1305_ietf_decrypt(c, None, n, k)
        assert p == b"test"
        print("         PASS (Symbol found and working).")
    except Exception as e:
        print(f"         FAIL: {e}")
        sys.exit(1)
    
    print("   [3/3] Library Version Check...")
    try:
        print(f"         Sodium Version: {nacl.bindings.sodium_library_version_major()}")
    except:
        print("         Version check skipped (bindings ok).")

if __name__ == "__main__":
    test_crypto()

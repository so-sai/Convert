import os
from pathlib import Path

def setup():
    print("🚀 Starting Sprint 4 Setup...")
    
    # 1. Create Directories
    dirs = [
        "hooks",
        "src/core/crypto",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ Checked/Created directory: {d}")

    # 2. Create Empty Files
    files = [
        "src/core/crypto/__init__.py",
        "hooks/hook-nacl.py"
    ]
    for f in files:
        path = Path(f)
        if not path.exists():
            path.touch()
            print(f"✅ Created file: {f}")
        else:
            print(f"ℹ️  File already exists: {f}")

    # 3. Update requirements.txt
    req_content = """# MDS v3.14 - Python 3.14 Free-Threading Dependencies
# Sprint 4: The Cryptographic Vault
# Last Updated: 2025-11-22

# ============================================================================
# Core Backend (FastAPI + Async)
# ============================================================================
fastapi==0.121.3        # Security patched, Py3.14 compatible
uvicorn==0.38.0         # ASGI server with Py3.14 support
orjson==3.11.4          # Fast JSON serialization (pre-compiled wheels)
aiosqlite==0.21.0       # Async SQLite wrapper

# ============================================================================
# Cryptography (Sprint 4 - ADR-002)
# ============================================================================
# CRITICAL: Pin cffi>=2.0.0 for Python 3.14 free-threading support
cffi>=2.0.0             # Required for PyNaCl thread safety

# Primary crypto provider (libsodium bindings)
pynacl>=1.5.0,<2.0.0    # XChaCha20-Poly1305, HMAC, key derivation

# Fallback crypto provider (if PyNaCl wheels unavailable)
pycryptodome>=3.17.0,<4.0.0  # XChaCha20 support, self-contained

# ============================================================================
# Development & Testing
# ============================================================================
pytest>=8.0.0           # Testing framework
pytest-asyncio>=0.23.0  # Async test support
pytest-timeout>=2.2.0   # Timeout for long-running tests
pytest-cov>=4.1.0       # Code coverage

# ============================================================================
# Packaging & Deployment
# ============================================================================
pyinstaller>=6.0.0      # Executable bundling
"""
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(req_content)
    print("✅ Updated requirements.txt")

    print("\n✨ Sprint 4 Setup Complete! Ready for 'The Cryptographic Vault'.")

if __name__ == "__main__":
    setup()

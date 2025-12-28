# SQLCipher 4.12.0 Build Documentation

This directory contains comprehensive documentation for building, packaging, and deploying SQLCipher 4.12.0 for Python 3.14 No-GIL on Windows.

## 📚 Quick Links

- **[Complete Documentation Index](./BUILD_GUIDES/README.md)** - Start here
- **[Quick Start Guide](./BUILD_GUIDES/SQLCIPHER_QUICKSTART.md)** - Installation & usage
- **[Build Manifesto](./BUILD_GUIDES/SQLCIPHER_BUILD_MANIFESTO.md)** - Technical deep dive
- **[Packaging Guide](./BUILD_GUIDES/SQLCIPHER_PACKAGING_GUIDE.md)** - Distribution

## 🎯 Achievement

✅ Successfully built SQLCipher 4.12.0 for Python 3.14 No-GIL on Windows x64  
✅ Full AES-256-CBC encryption operational  
✅ FTS5 full-text search enabled  
✅ Production-ready with comprehensive testing

## 🚀 Quick Start

```bash
# Install from wheel
pip install sqlcipher3/dist/sqlcipher3-binary-4.12.0-cp314-cp314-win_amd64.whl

# Verify installation
python sqlcipher3/test_wheel_install.py
```

See [SQLCIPHER_QUICKSTART.md](./BUILD_GUIDES/SQLCIPHER_QUICKSTART.md) for details.

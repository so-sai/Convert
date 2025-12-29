# Convert Desktop - Encrypted Document Management System

**A hybrid Rust/Python/Svelte application for secure document conversion, indexing, and management with military-grade encryption.**

[![Python](https://img.shields.io/badge/Python-3.14%20No--GIL-blue)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/Rust-1.75+-orange)](https://www.rust-lang.org/)
[![SQLCipher](https://img.shields.io/badge/SQLCipher-4.12.0-green)](https://www.zetetic.net/sqlcipher/)
[![License](https://img.shields.io/badge/License-Commercial-red)](./COMMERCIAL.md)

---

## 🎯 Project Vision

Convert is not just a file converter - it's a **Trust Framework** for managing the complete data lifecycle with zero-trust security principles:

- **Local-First**: All processing happens on your machine. No cloud dependencies.
- **Zero-Trust Pipeline**: Every component validates and signs data cryptographically.
- **Hybrid Architecture**: Rust for security-critical operations, Python for orchestration, Svelte for UI.

---

## 🏗️ Architecture Overview

### Three-Layer Design

```
┌─────────────────────────────────────────────────┐
│  LAYER 3: UI (Svelte 5)                        │
│  - Reactive interface                          │
│  - State-driven rendering                      │
└─────────────────────────────────────────────────┘
                    ↕ IPC (Tauri)
┌─────────────────────────────────────────────────┐
│  LAYER 2: Orchestration (Python 3.14 No-GIL)  │
│  - Event-driven pipeline                       │
│  - SQLCipher encrypted storage                 │
│  - Full-text search (FTS5)                     │
└─────────────────────────────────────────────────┘
                    ↕ PyO3 Bindings
┌─────────────────────────────────────────────────┐
│  LAYER 1: Security Core (Rust)                │
│  - XChaCha20-Poly1305 encryption               │
│  - Memory-safe operations                      │
│  - Sandboxed file processing                   │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14+ (No-GIL build recommended)
- Rust 1.75+
- Node.js 18+
- OpenSSL 3.6.0+ (Windows: required for SQLCipher)

### Installation

```bash
# Clone repository
git clone https://github.com/so-sai/Convert.git
cd Convert

# Setup Python environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Running the Application

```bash
# Development mode
npm run tauri dev

# Production build
npm run tauri build
```

---

## 📚 Documentation

### For Developers

- **[Architecture Decisions](./docs/01_ARCHITECTURE/)** - ADRs and design rationale
- **[Technical Specifications](./docs/03_SPECS/)** - Detailed component specs
- **[Master Design Spec](./docs/01_ARCHITECTURE/MDS_v3.14_Pi.md)** - Complete system design

### For Operations

- **[Playbook](./docs/05_OPERATIONS/PLAYBOOK.md)** - Deployment and maintenance
- **[Security Policy](./docs/05_OPERATIONS/SECURITY_POLICY.md)** - Security guidelines

### For SQLCipher Integration

- **[Build Guides](./docs/BUILD_GUIDES/)** - Complete SQLCipher build documentation
- **[Quick Start](./docs/BUILD_GUIDES/SQLCIPHER_QUICKSTART.md)** - Get started in 5 minutes
- **[Build Manifesto](./docs/BUILD_GUIDES/SQLCIPHER_BUILD_MANIFESTO.md)** - Technical deep dive

---

## 🏆 Current Status

**Sprint 6 Complete** ✅ (December 2025)

- ✅ Watchdog file monitoring (22/22 tests)
- ✅ EventBus (8/8 tests, 260K events/sec)
- ✅ Indexer Queue with SQLite persistence (10/10 tests)
- ✅ PDF & DOCX extractors (10/10 tests)
- ✅ Integration pipeline (8/8 tests)
- ✅ SQLCipher 4.12.0 with FTS5 full-text search
- ✅ Repository optimization (285K lines removed)

**Sprint 7 Active** 🚀 (December 2025)

- [ ] Search UI with SvelteKit
- [ ] Real-time FTS5 search interface
- [ ] File preview components

---

## 🔐 Security Features

- **AES-256 Encryption**: SQLCipher with OpenSSL 3.6.0
- **Memory Safety**: Rust core with automatic zeroization
- **Sandboxed Execution**: Isolated file processing
- **Cryptographic Signing**: Ed25519 signatures for data integrity
- **Zero-Knowledge**: No secrets in IPC layer

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/indexer/ -v          # Indexer tests
pytest tests/security/ -v         # Security tests
pytest tests/integration/ -v      # Integration tests

# Run smoke test (verify SQLCipher)
python scripts/smoke_test.py
```

**Test Coverage**: 95%+ across all critical components

---

## 🛠️ Development Tools

Located in `tools/` directory:

- `audit_density.py` - Analyze repository file distribution
- `cleanup.py` - Remove build artifacts safely
- `git_health_check.py` - Verify repository health
- `nuclear_purge.py` - Force remove locked files (Windows)

---

## 📦 Project Structure

```
Convert/
├── src/                    # Python source code
│   ├── core/              # Core business logic
│   │   ├── indexer/       # Document indexing
│   │   ├── security/      # Encryption & key management
│   │   └── services/      # Background services
│   └── plugins/           # Plugin system
├── src-tauri/             # Rust backend (Tauri)
├── src-ui/                # Svelte frontend
├── sqlcipher3/            # SQLCipher Python extension
├── tests/                 # Test suites
├── tools/                 # Development utilities
└── docs/                  # Documentation
```

---

## 🤝 Contributing

This is a commercial project. See [COMMERCIAL.md](./COMMERCIAL.md) for licensing details.

For development guidelines, see [PROJECT_SOP_v1.0.md](./PROJECT_SOP_v1.0.md).

---

## 📄 License

Commercial License - See [COMMERCIAL.md](./COMMERCIAL.md)

---

## 🙏 Acknowledgments

- **SQLCipher** by Zetetic LLC
- **Python 3.14 No-GIL** by Python Software Foundation
- **Tauri** for the excellent Rust/Web framework

---

**Built with ❤️ for secure, local-first document management**
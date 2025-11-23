# Project CONVERT

**Status:** Sprint 4 Complete | Sprint 5 Planning  
**Version:** 1.0-crypto-trinity-rev2  
**License:** PolyForm Noncommercial 1.0.0

---

## Overview

**CONVERT** is an offline-first, cryptographically secure knowledge management system built on event sourcing principles. The system provides military-grade encryption, integrity verification, and key management while maintaining zero cloud dependencies.

**Core Philosophy:**
- **Local-First:** All data stays on your device
- **Data Sovereignty:** You control the encryption keys
- **Cryptographic Integrity:** Every event is authenticated and encrypted
- **Event Sourcing:** Append-only log as single source of truth

---

## Security Architecture (Sprint 4 - Crypto Trinity Rev 2)

### The Eternal Vault

**Status:** APPROVED (Hash: SPRINT4-REV5.1-FINAL)  
**Security Audit:** SECA_GROK_4.1 + Supreme Judicial Review  
**Compliance:** OWASP Password Storage Cheat Sheet 2025

### Key Hierarchy

```
User Passkey (>=12 characters)
    ↓ Argon2id KDF (OWASP 2025: 19 MiB, t=2, p=1)
KEK (Key Encryption Key, 256-bit)
    ↓ XChaCha20-Poly1305 AEAD
Epoch Secret (Root of Trust, 256-bit)
    ↓ BLAKE2b Key Derivation
DEK (Data Encryption Key) + HMAC_KEY
    ↓ XChaCha20-Poly1305 AEAD + HMAC-SHA3-256
Encrypted Event Payloads
```

### Cryptographic Primitives

- **Key Derivation:** Argon2id (19 MiB memory, 2 iterations, p=1)
- **Encryption:** XChaCha20-Poly1305 AEAD (192-bit nonce)
- **Integrity:** HMAC-SHA3-256 (chain) + Poly1305 (AEAD tag)
- **Library:** PyNaCl (libsodium 1.0.19+)

### Security Guarantees

- ✅ **Anti-NSA:** Side-channel resistant (Argon2id, constant-time operations)
- ✅ **DoS Resistant:** Memory-bound KDF prevents resource exhaustion
- ✅ **AEAD Protection:** Authenticated encryption prevents tampering
- ✅ **Double-MAC:** Defense-in-depth integrity verification
- ✅ **OWASP Compliant:** Follows industry best practices (2025 standards)

---

## Tech Stack

**Backend:**
- Python 3.14 (Free-Threading Build, No-GIL)
- FastAPI 0.121.3 + Uvicorn 0.38.0
- SQLite (STRICT mode)
- PyNaCl 1.5.0 (libsodium)

**Frontend:** (Sprint 6)
- Svelte 5
- Tauri v2.9.3
- WebGPU

**Cryptography:**
- XChaCha20-Poly1305 (encryption)
- Argon2id (key derivation)
- HMAC-SHA3-256 (integrity chain)
- BLAKE2b (key separation)

---

## Quick Start

### Prerequisites

- Python 3.14+ (Free-Threading build recommended)
- Virtual environment
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/convert.git
cd convert

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
python -m pip install -r requirements.txt

# Run tests
python -m pytest

# Start server
python -m uvicorn src.core.main:app --reload
```

### First-Time Setup

```bash
# Initialize vault (one-time)
curl -X POST http://localhost:8000/vault/init \
  -H "Content-Type: application/json" \
  -d '{"passkey":"YourSecurePasskey12345"}'

# Unlock vault
curl -X POST http://localhost:8000/vault/unlock \
  -H "Content-Type: application/json" \
  -d '{"passkey":"YourSecurePasskey12345"}'

# Save encrypted event
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{"type":"domain","id":"note-1","payload":{"title":"Test","content":"Secret data"}}'

# Retrieve events
curl http://localhost:8000/events
```

---

## Project Structure

```
convert/
├── src/
│   └── core/
│       ├── security/          # Crypto Trinity
│       │   ├── kms.py         # Key Management System
│       │   ├── encryption.py  # XChaCha20 + HMAC
│       │   └── storage.py     # Key persistence
│       ├── storage/
│       │   └── adapter.py     # Encrypted event storage
│       └── main.py            # FastAPI application
├── tests/
│   ├── security/              # Security test suite
│   └── integration/           # End-to-end tests
├── docs/
│   ├── decisions/             # Architecture Decision Records
│   ├── policies/              # Security & Engineering policies
│   └── planning/              # Sprint plans
├── pytest.ini                 # Test configuration (MANDATORY)
├── requirements.txt           # Python dependencies
└── MDS_v3.14.md              # Master Design Spec
```

---

## Documentation

- **[Master Design Spec](MDS_v3.14.md)** - Complete system architecture
- **[Security Policy](docs/policies/SECURITY_POLICY.md)** - Passkey requirements, crypto standards
- **[Engineering Playbook](docs/policies/ENGINEERING_PLAYBOOK.md)** - Development standards
- **[ADR-002: Crypto Library](docs/decisions/ADR-002-CRYPTO-LIB.md)** - Cryptographic design
- **[Sprint 5 Plan](docs/planning/SPRINT_5_PLAN.md)** - Hardening roadmap

---

## Security Features

### Current (Sprint 4 Complete)

- ✅ Argon2id key derivation (OWASP 2025 compliant)
- ✅ XChaCha20-Poly1305 authenticated encryption
- ✅ HMAC-SHA3-256 integrity chain
- ✅ Epoch Secret architecture (single root of trust)
- ✅ SQLite STRICT schema with quarantine mechanism
- ✅ Memory zeroization (best-effort)
- ✅ Passkey strength validation (12-char minimum)

### Planned (Sprint 5 - Hardening)

- ⏳ Kill Switch Protocol (`/vault/panic` API)
- ⏳ Reproducible builds (deterministic binaries)
- ⏳ SBOM generation (Software Bill of Materials)
- ⏳ Self-integrity check (binary tampering detection)
- ⏳ Fake data injection (anti-traffic analysis)

---

## Testing

```bash
# Run all tests
python -m pytest

# Run security tests only
python -m pytest tests/security/ -v

# Run with coverage
python -m pytest --cov=src/core --cov-report=html

# Collect tests without running
python -m pytest --collect-only
```

**Test Configuration:** See `pytest.ini` for asyncio settings.

---

## Contributing

This project follows strict engineering standards documented in the [Engineering Playbook](docs/policies/ENGINEERING_PLAYBOOK.md).

**Key Requirements:**
- All async projects MUST have `pytest.ini` configuration
- Use `python -m <command>` syntax (never call commands directly)
- Copyright headers required in all source files
- Security tests MUST pass before merging

---

## License

Copyright (c) 2025 Project CONVERT  
Licensed under PolyForm Noncommercial 1.0.0

**Commercial use prohibited.** See LICENSE file for details.

---

## Acknowledgments

**Team:**
- **PM:** Gemini 3.0 Pro (Strategy & Planning)
- **SA:** ChatGPT 5.1 (Architecture & Design)
- **SecA:** Grok 4.1 (Security Audit)
- **Dev:** DeepSeek V3.2 (Implementation)
- **QA:** Claude 4.5 (Judicial Review)

**Security Audits:**
- Sprint 4 Rev 5.1: APPROVED (2025-11-23)
- Argon2id parameters: LOCKED (19 MiB, t=2, p=1)
- Crypto Trinity Rev 2: ETERNAL

---

**Convert will never leak. Never break. Never die.**  
**Forever local. Forever yours.** 🛡️⚡

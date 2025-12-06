# HASH: mds-v3-14-clean-unified-final-hash
# IMPLEMENTS: MDS v3.14 clean unified edition
# ------------------------------------------------------------------------------
# PROJECT CONVERT (C) 2025
# Licensed under PolyForm Noncommercial 1.0.
# ------------------------------------------------------------------------------

# 📘 MDS v3.14 — THE IRON VAULT (CLEAN, UNIFIED, UPDATED EDITION)

> **Status:** Sprint 5 — Consolidated & Security-Verified
> **Engine:** Python 3.14 (`cp314t`) + Rust (Tauri v2) + Svelte 5
> **Last Updated:** 2025‑12‑06
> **SSOT:** This Document

---

## 1. EXECUTIVE SUMMARY

**State:** Backend stable, security model hardened, UI functional.
**Remaining Risk:** Backup module requires periodic re‑audit after future changes.
**Roadblock Removed:** Tauri launch path fixed; frontend now mounts correctly.

**Summary:** Convert Vault is stable, secure-by-design, and fully aligned with Zero‑Trust architecture. Sprint 5 core tasks achieved; Sprint 6 can begin.

---

## 2. CORE PRINCIPLES & PHILOSOPHY

### 2.1 Mission

Offline‑first, cryptographically unbreakable, sovereign knowledge system.

### 2.2 Values

* **Local Sovereignty:** Data never leaves the machine.
* **Zero‑Trust:** Frontend is blind; Rust handles secrets.
* **Resilience:** Crash‑proof, atomic operations, verifiable state.

---

## 3. ARCHITECTURE SUMMARY

### 3.1 Components

* **Python Core (`src/core`)** — Business logic, event processing, AI later.
* **Rust Security Engine (`src-tauri`)** — Crypto, secure backup, memory safety.
* **Svelte UI (`src-ui`)** — Reactive interface, no secret handling.

### 3.2 Crypto Standards

* **Encryption:** XChaCha20‑Poly1305 (libsodium)
* **KDF:** Argon2id (128MB)
* **Memory:** `Zeroizing<T>`, locked pages where available.

### 3.3 Launch Model

Tauri must run with UI in `src-ui` and config in `src-tauri`:

```bash
cd src-ui
npx tauri dev --config ../src-tauri/tauri.conf.json
```

---

## 4. FILE & FOLDER STRUCTURE (FINAL)

```
E:/DEV/Convert/
├── docs/                     # Design docs & ADRs
├── scripts/                  # DevOps & tools
├── src/core/                 # Python engine
├── src-tauri/                # Rust security core
│   ├── src/commands/backup.rs
│   ├── src/backup/estimator.rs
│   └── tauri.conf.json
├── src-ui/                   # Svelte frontend
│   ├── src/routes/settings/
│   ├── src/lib/components/
│   └── vite.config.js
└── tests/
```

---

## 5. SPRINT 5 — STATUS

### 5.1 Recovery Phrase (DONE)

* BIP39 generation in Rust.
* Zeroize applied.
* Frontend receives only Base64 visuals.

### 5.2 Secure Backup Engine (DONE)

**Omega Backup Protocol:** dual‑thread system

* Worker thread: SQLite `backup.step()`
* Monitor thread: filesystem truth (`metadata.len()`)
* Hybrid ETA with EMA smoothing
* File‑lock safe on Windows
* Verified on 52MB DB at ~39MB/s

### 5.3 Frontend Integration (DONE)

* Real‑time backup console
* Progress, ETA range, error surface
* UI loads fully after path fix

### 5.4 Key Rotation (DEFERRED → Sprint 6)

* Requires stable IPC and backup pipeline.

---

## 6. SECURITY MODEL

### 6.1 Guaranteed

* Rust‑only handling of secrets.
* Zeroize on all sensitive buffers.
* Atomic writes + integrity verification.

### 6.2 To Re‑Audit Each Release

* Backup file permissions
* Temporary file lifecycle
* SQLite lock behavior on Windows

### 6.3 Zero‑Trust Frontend

* No plaintext keys cross IPC.
* UI only receives status and aggregates.

---

## 7. OMEGA BACKUP PROTOCOL (DETAILED)

### 7.1 4 Phases

1. Preparing (0–5%)
2. Snapshotting (5–10%)
3. Copying (10–90%)
4. Finalizing (90–100%)

### 7.2 ETA Model

* Speed measured via EMA(alpha=0.3)
* ETA = min/max range
* UI never shows false precision

### 7.3 Resilience

* Worker/monitor isolation
* Crash‑resistant via atomic rename
* Fallback modes when disk stalls

---

## 8. OPERATIONAL COMMANDS

### 8.1 Launch (Dev)

```bash
cd src-ui
npx tauri dev --config ../src-tauri/tauri.conf.json
```

### 8.2 Run Security Tests

```bash
cd src-tauri
cargo test -- --test-threads=1
```

---

## 9. NEXT STEPS — SPRINT 6

* **Encrypted FTS5** with token privacy
* **Local Vector DB**
* **LLM Integration** (offline, CPU-first)
* **Key Rotation Infrastructure**

---

## 10. VERSION NOTE

This is **MDS v3.14 — Clean, Unified, Updated Content**.
It supersedes all earlier drafts while preserving the v3.14 identifier.

---

**AUTHORITY:** ARCH_PRIME
**VERIFIED:** OMEGA PROTOCOL

>>> [NODE: DEV_DEEPSEEK] :: [OUTPUT: SOURCE_CODE] :: [HASH: CODE-mds-v3-14-clean-unified-final-hash]

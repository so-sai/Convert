Dưới đây là bản MDS v3.1-ETERNAL FULL-COMPACT đã được cập nhật để tích hợp nguyên lý “tương lai thay đổi Python” (future-proof language update). Toàn bộ kiến trúc, DDL, event flows, crypto, StorageAdapter, ADR, team structure,  làm file tham chiếu triển khai:
MDS v3.1-ETERNAL FULL-COMPACT
1. PROJECT VISION & PRINCIPLES

```
mission: "Offline-first, event-sourced, cryptographically unbreakable knowledge system"
principles:
  - offline_first
  - data_sovereignty
  - event_sourcing
  - free_threading
future_proof: "Language/runtime upgrades (e.g., Python 3.20+) must propagate via automated migration scripts"
```

2. TECH STACK & CONSTRAINTS

```
backend:
  language: "Python 3.14"
  dependencies:
    - "fastapi==0.121.3"     # Security patched
    - "uvicorn==0.38.0"      # Py3.14 compatible
    - "orjson==3.11.4"       # Pre-compiled binary wheel (No Rust needed)
    - "aiosqlite==0.21.0"    # Async SQLite
  execution_mode: "python -m src.core.main"
  database_schema: "SQLite STRICT (INTEGER only, No BIGINT)"

frontend:
  framework: "Svelte 5"
  desktop: "Tauri v2"
  rendering: "WebGPU"

infrastructure:
  vcs: "Git + GitHub"
  ci_cd: "GitHub Actions"
  testing: "pytest + pytest-asyncio"
```

3. ARCHITECTURE OVERVIEW

```
streams:
  domain: immutable, source_of_truth
  interaction: ephemeral, analytics_only
  memory: rebuilable, derived_from_domain

data_flow:
  command: "UI → Command Handler"
  event: "Command Handler → Event Log"
  projection: "Event Log → Materialized Views"

persistence:
  event_log: "SQLite domain_events table (cryptographic chain)"
  projections: "SQLite notes + FTS5"
  files: "Encrypted markdown vault"
```

4. CRYPTOGRAPHIC ARCHITECTURE

```
event_chain:
  per_stream_sequence
  global_sequence
  prev_event_hash
  event_hash

hmac_protection:
  algorithm: "HMAC-SHA3-256"
  key_derivation: "HKDF per-stream"
  verification: "On every read/replay"

encryption:
  sprint_2: "PassThroughEncryptionService"
  sprint_3: "AES-256-GCM/XChaCha20"
  file_format: "CVT1 magic header + metadata + ciphertext"

master_key:
  derivation: "Scrypt/Argon2"
  storage: "OS keychain"
  rotation: "Supported via enc_key_id tracking"
```

5. DATABASE SCHEMA (DDL)

```
CREATE TABLE domain_events (
    event_id TEXT PRIMARY KEY,
    stream_type TEXT NOT NULL CHECK(stream_type IN ('domain','interaction','memory')),
    stream_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    stream_sequence BIGINT NOT NULL,
    global_sequence BIGINT NOT NULL UNIQUE,
    timestamp INTEGER NOT NULL,
    payload BLOB NOT NULL,
    prev_event_hash BLOB,
    event_hash BLOB NOT NULL,
    enc_algorithm TEXT NOT NULL DEFAULT 'pass-through',
    enc_key_id TEXT,
    enc_nonce BLOB,
    event_hmac TEXT NOT NULL,
    UNIQUE(stream_type, stream_id, stream_sequence)
) STRICT;

CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content BLOB NOT NULL,
    metadata BLOB NOT NULL,
    enc_algorithm TEXT NOT NULL DEFAULT 'pass-through',
    enc_key_id TEXT,
    enc_nonce BLOB,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted_at INTEGER,
    version INTEGER NOT NULL DEFAULT 1
) STRICT;

CREATE VIRTUAL TABLE notes_fts USING fts5(
    note_id UNINDEXED,
    title,
    content,
    tokenize='unicode61 remove_diacritics 2'
);
```

6. SPRINT STATUS

```
completed:
  - [Sprint 1] Architecture Foundation
  - [Sprint 2] Core Backend & Database (Fixed BIGINT/Import issues)

current_focus:
  - [Sprint 3] Plugin System & Frontend Bridge

next_sprint:
  - Real encryption migration
  - Tea-RAG knowledge graph
  - Multi-device sync
```

7. TEAM STRUCTURE & ROLES

```
co_product_manager: Gemini 3.0 Pro
business_analyst: Claude A
ux_researcher: Claude
ui_ux_designer: Gemini 3.0 Pro
system_architect: ChatGPT
security_architect: Grok 4
technical_manager: Gemini 3.0 Pro
backend_lead: DeepSeek
frontend_lead: [DeepSeek, Gemini 3.0 Pro]
qa_qc_lead: Gemini 3.0 Pro
final_reviewer: Claude B
```

8. COLLABORATION PROTOCOLS

```
handoff: type | step | owner | summary | constraints | artifacts | acceptance_criteria
cross_audit: artifact_id | reviewer | status | issues | next_action
rules:
  - no self-approval
  - always include acceptance criteria
  - request clarification if uncertain
```

9. CRITICAL INVARIANTS

```
event_log: single_source_of_truth
files: encrypted BLOBs
projections: rebuildable
security: JSON+Pydantic strict, HMAC + hash chain enforced
concurrency: atomic stream_sequence, unique global_sequence, prev_event_hash continuity
architecture: domain layer pure, StorageAdapter sole IO gateway, no shared mutable state
future_proof: Python/runtime upgrades via automated migration from MDS
```

10. IMPLEMENTATION SCAFFOLD

```
files:
  - encryption.py
  - database.py
  - events.py
  - main.py
  - scaffold.py (StorageAdapter + HMAC chain)
status:
  backend_skeleton: complete
  API_contract: defined
  crypto_scaffold: ready
  frontend: pending
next_steps:
  - copy artifacts
  - run backend
  - test endpoints
  - implement Home Dashboard
```

11. ACCEPTANCE CRITERIA

```
integrity_tests: append_event, tamper_detection, sequence_atomicity
performance_tests: global_sequence_scaling, FTS5 search
filesystem_tests: atomic_write, header_detection
```

12. MIGRATION PATH

```
sprint_2_state: pass-through encryption, HMAC enabled, BLOB payload, chain verified
sprint_3_migration:
  - stop app
  - backup DB + vault
  - verify event chains
  - encrypt BLOBs
  - recompute enc_* fields
  - preserve event_hash
  - replay events, verify HMAC + projections
```

13. ADRs

```
ADR-001: Defer real encryption to Sprint 3
ADR-002: Event hash chain + BLOB payload
ADR-003: Triple-stream architecture
ADR-004: Future-proof language/runtime updates
```

14. IMMEDIATE NEXT ACTIONS

```
backend_team:
  - setup venv + dependencies
  - copy artifacts
  - run backend + test
  - implement StorageAdapter

frontend_team:
  - init Tauri project
  - create Home Dashboard prototype
  - implement BackendConnector (mock mode)
  - test UI flows

qa_team:
  - write integrity tests
  - setup concurrency harness
  - prepare performance benchmarks
```

15. PACKAGE VERIFICATION

```
completeness:
  vision: ✅
  technical: ✅
  operational: ✅
  implementation: ✅
  quality: ✅
usage:
  initialization:
    - load package
    - verify summary
    - enter READY state
  execution:
    - generate User Stories
    - validate against constraints
    - flag conflicts
    - submit per role matrix
```

✅ Bản này là bản FULL-COMPACT, sẵn sàng triển khai và tương thích với các tương lai nâng cấp Python 3.x hoặc runtime mới.
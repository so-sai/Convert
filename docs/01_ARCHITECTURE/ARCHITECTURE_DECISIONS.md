# ARCHITECTURE DECISION LOG (ADL)

**Status:** ACTIVE  
**Last Updated:** 2025-12-27  
**Governance:** See [DOC_GOVERNANCE_RULES.md](../00_GOVERNANCE/DOC_GOVERNANCE_RULES.md)

---

## Purpose

This document records all significant architectural decisions made during the development of Convert Vault. Each entry follows the format:

- **Decision:** What was decided
- **Status:** ACTIVE / SUPERSEDED / DEPRECATED
- **Source:** Reference to the SPEC that defines this decision
- **Summary:** Brief explanation
- **Impact:** What this means for implementation
- **Reference:** Links to related documentation

---

## ADL-001: Hybrid Architecture (Python Brain + Rust Muscle)

**Status:** ACTIVE  
**Source:** MDS_v3.14_Pi.md §I.2  
**Decision Date:** 2025-12 (Sprint 1)

**Summary:** System uses Python for orchestration/state management and Rust for crypto/performance-critical operations.

**Impact:**
- Requires PyO3 bridge for Rust-Python interop
- State management centralized in Python
- Security-critical operations isolated in Rust

**Reference:** [MDS_v3.14_Pi.md](../01_ARCHITECTURE/MDS_v3.14_Pi.md)

---

## ADL-002: XChaCha20-Poly1305 for Encryption

**Status:** ACTIVE  
**Source:** ADR-002-CRYPTO-LIB.md  
**Decision Date:** 2025-12 (Sprint 2)

**Summary:** Use XChaCha20-Poly1305 with 24-byte nonce for all encryption operations.

**Impact:**
- Requires `chacha20poly1305` crate in Rust
- 24-byte nonce generation for each encryption
- Authenticated encryption with associated data (AEAD)

**Reference:** [ADR-002-CRYPTO-LIB.md](../01_ARCHITECTURE/DECISIONS/ADR-002-CRYPTO-LIB.md)

---

## ADL-003: Argon2id for Key Derivation

**Status:** ACTIVE  
**Source:** MDS_v3.14_Pi.md §5.3  
**Decision Date:** 2025-12 (Sprint 2)

**Summary:** Use Argon2id with hardcoded parameters (64MB memory, 4 iterations, 4 lanes).

**Impact:**
- Memory-hard KDF resistant to GPU attacks
- Fixed parameters ensure consistent security level
- ~100-200ms derivation time on modern hardware

**Reference:** [MDS_v3.14_Pi.md](../01_ARCHITECTURE/MDS_v3.14_Pi.md#53-cryptographic-parameters-hardcoded)

---

## ADL-004: SQLite FTS5 for Full-Text Search

**Status:** ACTIVE  
**Source:** SPEC_TASK_6_4_EXTRACTION.md §3  
**Decision Date:** 2025-12 (Sprint 6)

**Summary:** Use SQLite FTS5 extension for indexing and searching extracted document content.

**Impact:**
- Requires SQLite compiled with FTS5 support
- Index stored in encrypted database
- Search latency target: < 100ms for 10K documents

**Reference:** [SPEC_TASK_6_4_EXTRACTION.md](../03_SPECS/SPEC_TASK_6_4_EXTRACTION.md)

---

## ADL-005: Python 3.14 No-GIL Target

**Status:** ACTIVE  
**Source:** MDS_v3.14_Pi.md §I  
**Decision Date:** 2025-12 (Sprint 6)

**Summary:** Target Python 3.14 with experimental free-threading (No-GIL) support.

**Impact:**
- Enables true parallel processing in Python
- Requires careful thread-safety review
- PyO3 bindings must use `abi3-py314` or later

**Reference:** [MDS_v3.14_Pi.md](../01_ARCHITECTURE/MDS_v3.14_Pi.md)

---

## ADL-006: Memory Zeroing Fallback Strategy

**Status:** ACTIVE  
**Source:** ADR-006-MEMZERO-FALLBACK.md  
**Decision Date:** 2025-12 (Sprint 3)

**Summary:** Use C-binding for memory zeroing with graceful fallback to manual overwrite.

**Impact:**
- Primary: Windows API for secure memory zeroing
- Fallback: Manual overwrite if C-binding unavailable
- Non-blocking degradation (security best-effort)

**Reference:** [ADR-006-MEMZERO-FALLBACK.md](../01_ARCHITECTURE/DECISIONS/ADR-006-MEMZERO-FALLBACK.md)

---

## ADL-007: Watchdog with UUID Batch Tracking

**Status:** ACTIVE — IMPLEMENTED (Task 6.1)  
**Source:** Task 6.1 Implementation  
**Decision Date:** 2025-12-27 (Sprint 6)

**Summary:** File system watcher uses UUID-based batch tracking for event correlation.

**Impact:**
- Each watch session gets unique UUID
- Events grouped by batch for atomic processing
- 22/22 tests passing, POSIX path normalization

**Reference:** Task 6.1 completion report

---

## ADL-008: EventBus with 200K Queue Capacity

**Status:** ACTIVE — IMPLEMENTED (Task 6.2)  
**Source:** Task 6.2 Implementation  
**Decision Date:** 2025-12-27 (Sprint 6)

**Summary:** Event bus supports 260K events/sec with 0% drop rate at 200K queue depth.

**Impact:**
- Async event processing with backpressure handling
- Thread-safe publish/subscribe pattern
- 8/8 core tests passing, military-grade stress tested

**Reference:** Task 6.2 completion report

---

## ADL-009: Indexer Queue with SQLite Persistence

**Status:** ACTIVE — IN PROGRESS (Task 6.3)  
**Source:** Task 6.3 Specification  
**Decision Date:** 2025-12-27 (Sprint 6)

**Summary:** Job queue uses SQLite for persistence with SecureLRUCache for idempotency.

**Impact:**
- Persistent queue survives process restarts
- LRU cache prevents unbounded memory growth
- Fallback to SQLite check for idempotency

**Reference:** Task 6.3 implementation

---

## ADL-010: PyMuPDF for PDF Extraction

**Status:** ACTIVE — LOCKED BY SPEC_TASK_6_4_EXTRACTION.md  
**Source:** SPEC_TASK_6_4_EXTRACTION.md §1  
**Decision Date:** 2025-12-27 (Sprint 6)

**Summary:** Use PyMuPDF 1.26.x (C-core) for PDF text extraction.

**Rationale:**
- Mature, battle-tested library
- C-core provides native performance
- Comprehensive metadata extraction support
- Async-compatible via sandbox executor

**Alternatives Considered:**
- pdfplumber: Rejected (slower, Python-only)
- PyPDF2: Rejected (limited metadata support)
- pdf2text: Rejected (CLI dependency)

**Impact:**
- Requires PyMuPDF ≥ 1.26
- Managed via `SandboxExecutor` for security
- Target: > 40 files/sec throughput, < 50ms P95 latency

**Reference:** [SPEC_TASK_6_4_EXTRACTION.md](../03_SPECS/SPEC_TASK_6_4_EXTRACTION.md)

---

## ADL-015: Rust Native DOCX Extraction

**Status:** ACTIVE — LOCKED BY SPEC_TASK_6_4_EXTRACTION.md  
**Source:** SPEC_TASK_6_4_EXTRACTION.md §2  
**Decision Date:** 2025-12-27 (Sprint 6)

**Summary:** Use docx-rs (Rust) via PyO3 bindings for DOCX extraction.

**Rationale:**
1. **Native Performance:** 3-5x faster than python-docx
2. **Memory Safety:** Rust's ownership model prevents memory leaks
3. **No-GIL Compatibility:** Bypasses Python GIL bottleneck
4. **Parallel Processing:** Native Rust concurrency support

**Alternatives Considered:**
- python-docx: Rejected (GIL bottleneck, slower)
- unoconv: Rejected (LibreOffice dependency, heavyweight)
- mammoth: Rejected (HTML conversion overhead)

**Impact:**
- Requires Rust toolchain for building
- PyO3 ≥ 0.23 for Python 3.14 compatibility
- maturin build pipeline for native extension
- Target: > 30 files/sec throughput, < 50ms P95 latency

**ABI Requirements:**
- Python: cp314 (3.14+)
- PyO3: abi3-py314 or later
- Rust: 1.70+ (for PyO3 0.23 compatibility)

**Reference:** [SPEC_TASK_6_4_EXTRACTION.md](../03_SPECS/SPEC_TASK_6_4_EXTRACTION.md)

---

## ADL-016: Sandbox Executor for Extraction Security

**Status:** ACTIVE — LOCKED BY SPEC_TASK_6_4_EXTRACTION.md  
**Source:** SPEC_TASK_6_4_EXTRACTION.md §4  
**Decision Date:** 2025-12-27 (Sprint 6)

**Summary:** All extraction operations run through `SandboxExecutor` with resource limits.

**Impact:**
- PathGuard: File location validation
- InputValidator: Magic bytes verification
- Resource limits: < 512MB memory per process
- Requires psutil ≥ 7.2.0

**Reference:** [SPEC_TASK_6_4_EXTRACTION.md](../03_SPECS/SPEC_TASK_6_4_EXTRACTION.md)

---

## Template for New Entries

```markdown
## ADL-XXX: [Decision Title]

**Status:** ACTIVE / SUPERSEDED / DEPRECATED  
**Source:** [SPEC or ADR reference]  
**Decision Date:** YYYY-MM-DD (Sprint X)

**Summary:** Brief one-line description.

**Rationale:** (Optional) Why this decision was made.

**Alternatives Considered:** (Optional) What else was evaluated.

**Impact:**
- Bullet points of implementation consequences
- Dependencies, requirements, constraints

**Reference:** [Link to source document]
```

---

## Status Legend

- **ACTIVE:** Currently in use, must be followed
- **ACTIVE — LOCKED BY SPEC_X:** Frozen by specific SPEC, requires amendment to change
- **ACTIVE — IMPLEMENTED:** Decision implemented and verified
- **ACTIVE — IN PROGRESS:** Decision approved, implementation ongoing
- **SUPERSEDED:** Replaced by newer decision (link to replacement)
- **DEPRECATED:** No longer recommended, but may exist in legacy code

---

**Governance Note:** This ADL follows the reference-only style per [DOC_GOVERNANCE_RULES.md](../00_GOVERNANCE/DOC_GOVERNANCE_RULES.md). Detailed rationale and context should be in the source SPEC or ADR documents.

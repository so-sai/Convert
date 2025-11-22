# TECH SPEC: REMEDIATION FOR WP-DEEPSEEK-A-001 (Storage Hardening)

**Ref:** SEC-AUDIT-2025-11-22-001  
**Status:** CRITICAL REMEDIATION REQUIRED  
**Author:** BA_CLAUDE v3.14  
**Date:** 2025-11-22  

## EXECUTIVE SUMMARY
SecA has identified **5 CRITICAL** and **3 HIGH** severity issues violating the 10 Commandments. This spec addresses all blocking issues.

## 1. CRITICAL ISSUES (MUST FIX - BLOCKING SPRINT 3)

### CRITICAL-1: PyInstaller Asset Path Error Handling
- **File:** `src/core/utils/paths.py`
- **Requirement:** Handle `sys._MEIPASS` vs `sys.frozen`.
- **Security:** Prevent directory traversal & symlink attacks.

### CRITICAL-2: PyInstaller Specification File Missing
- **File:** `mds-core.spec`
- **Requirement:** Bundle `migrations`, handle hidden imports (`aiosqlite`, `uvicorn`).
- **Constraint:** Must include PolyForm License Header.

### CRITICAL-3: PyInstaller Smoke Test Missing
- **File:** `tests/e2e/test_pyinstaller_smoke.py`
- **Requirement:** Verify executable boots and loads assets in frozen mode.

### CRITICAL-4: SQLite Version Verification (CVE-2025-6965)
- **File:** `scripts/verify_sqlite_version.py`
- **Requirement:** Enforce SQLite >= 3.50.2.

### CRITICAL-5: CI/CD PyInstaller Test Pipeline
- **File:** `.github/workflows/pyinstaller-test.yml`
- **Requirement:** Automated build and size check (<50MB).

## 2. HIGH PRIORITY ISSUES (SHOULD FIX)

### HIGH-1: Transaction Isolation for HMAC
- **Requirement:** Wrap verification in `async with db.transaction()`.

### HIGH-2: Background Chain Verification
- **Requirement:** Use `ThreadPoolExecutor` for non-blocking HMAC checks.

### HIGH-3: HMAC Key Rotation
- **Requirement:** Support `v1`, `v2` keys in `hmac_service.py`.

## 3. DEFINITION OF DONE
- [ ] All Source files must have `PolyForm Noncommercial 1.0.0` Header.
- [ ] Security Audit (Grok) must PASS.
- [ ] Unit Tests (QA) must PASS.
- [ ] Judicial Review (Claude) must APPROVE.

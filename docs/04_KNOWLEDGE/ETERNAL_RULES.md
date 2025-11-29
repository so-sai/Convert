# ETERNAL RULES: THE CONVERT PROTOCOL

> **Status:** IMMUTABLE
> **Context:** Windows 11 / Python 3.14 / Asyncio

## Rule 1: The Windows Integrity Protocol
- **Mandate:** **NO CLI one-liners** (`python -c`) or `cat << EOF` for file writing on Windows.
- **Action:** ALWAYS use full `.py` scripts or IDE editing.
- **Reason:** Prevents `IndentationError` and `UnicodeEncodeError` caused by shell encoding differences.

## Rule 2: The Async Mandate
- **Mandate:** All heavy I/O (Crypto, Backup, Database) **MUST** be Async.
- **Action:** Use `loop.run_in_executor(None, ...)` for CPU-bound tasks (Argon2id, Encryption).
- **Reason:** Blocking the Event Loop kills performance in the GUI (Tauri).

## Rule 3: The Salt Standard
- **Mandate:** Salt **MUST** be exactly **16 bytes** for NaCl/Argon2id.
- **Action:** Use `os.urandom(16)`. Do NOT use 32 bytes.
- **Reason:** `nacl.pwhash.argon2id` throws `ValueError` if salt is not `SALTBYTES` (16).

## Rule 4: The Documentation Supremacy
- **Mandate:** Code follows Docs. Docs is the **Single Source of Truth**.
- **Action:** Update `SPEC` -> Update `IMPL_GUIDE` -> Write Code.
- **Reason:** Prevents "Drift" and "Blind Patching".

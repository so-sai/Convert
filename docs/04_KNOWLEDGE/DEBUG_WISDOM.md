# DEBUG WISDOM: LESSONS FROM THE TRENCHES

> **Status:** LIVING DOCUMENT
> **Purpose:** Quick solutions to recurring errors.

## 1. Syntax & Environment

### Error: `IndentationError: unexpected indent` (in generated files)
- **Cause:** Using `python -c "..."` or `cat` to write Python files on Windows.
- **Fix:** **STOP.** Delete the file. Write a proper `deploy.py` script to generate it.
- **Rule:** See **ETERNAL RULE #1**.

## 2. Cryptography & Security

### Error: `ValueError: salt must be exactly 16 bytes long`
- **Cause:** Passing 32 bytes (from `os.urandom(32)`) to `nacl.pwhash.argon2id`.
- **Fix:** Change to `os.urandom(16)`.
- **Rule:** See **ETERNAL RULE #3**.

### Error: `CryptoError: Decryption failed` (Recovery)
- **Cause:** Using the wrong Nonce. Recovery Key uses a *different* nonce than the Passkey.
- **Fix:** Ensure `rk_nonce` is stored in DB and used for recovery decryption.

## 3. Database & Storage

### Error: `OperationalError: no such column: rk_nonce`
- **Cause:** Code expects a column that hasn't been migrated yet.
- **Fix:**
  1. Check `schema.sql`.
  2. Run a Migration Script (`ALTER TABLE ... ADD COLUMN ...`).
  3. Verify with `PRAGMA table_info(system_keys)`.

# SPECIFICATION: FRONTEND BACKUP INTEGRATION (TASK 5.3)
**Status:** READY FOR CODING
**Bridge Layer:** Python Pydantic <-> Tauri JSON

## 1. DATA CONTRACTS (STRICT SCHEMA)
Frontend expects this exact JSON structure from `backup_get_status()`:
```json
{
  "notes_count": int,          // Total notes in DB
  "last_backup_ts": int|null,  // Unix timestamp or null
  "db_size_bytes": int,        // For disk space check
  "is_safe_mode": bool,        // CRITICAL: True if Libsodium missing
  "schema_version": 1
}
```

## 2. API COMMANDS

1.  `cmd_backup_get_status()` -> Returns JSON above.
2.  `cmd_backup_create(passkey, path)` -> Returns `true` or throws Error.
3.  `cmd_backup_restore(passkey, path)` -> Returns `true` or throws Error.

## 3. UI/UX REQUIREMENTS

### A. The "Smart Toast" (Notification)

  - **Logic:** Show toast IF (`notes_count` > 10 AND `last_backup_ts` is null/old).
  - **Safe Mode:** IF `is_safe_mode` is True -> DO NOT show toast (Silent fail).

### B. The "Backup Dashboard" (Settings)

  - **State: Safe Mode Active**
      - Banner: "⚠️ Backup disabled. Missing crypto libraries."
      - Button: [Backup Now] (Disabled/Greyed out).
  - **State: Normal**
      - Button: [Backup Now] -> Opens Save Dialog.

### C. The "Magic Restore"

  - **Primary:** Drag & Drop `.cvbak` file onto App.
  - **Secondary:** Button [Restore from File...] -> Opens Native File Picker.
  - **Flow:** File Selected -> Valid Header? -> Prompt Passkey -> Show Progress Modal.

## 4. ERROR HANDLING MAPPING

  - Backend `BackupCryptoUnavailableError` -> UI shows "Safe Mode Warning".
  - Backend `WinError 32` -> UI shows "File Busy - Retrying...".
  - Backend `IntegrityError` -> UI shows "❌ File Corrupted".

# SPEC-005: FRONTEND INTEGRATION (BACKUP & RESTORE)

**Parent Task:** Task 5.3 - Resilience UI
**Status:** READY FOR DEV
**Ref:** MDS v3.14, ADR-003

## 1. USER STORIES (FROM PRODUCT OWNER)

### Story 1: Smart Toast Notification (The "Gentle Nudge")

**As a** User,
**I want** to receive a non-intrusive notification when it's time to backup my vault,
**So that** I can ensure my data is safe without being interrupted.

- **Trigger:** Periodic poll of `get_backup_status`.
- **UI:** Toast at bottom-right.
    - "You've created 10+ notes. Consider backing up."
    - [Backup Now] | [Don't ask again]
- **Behavior:** Auto-dismiss 8s. No Modals.

### Story 2: Magic Restore (Drag & Drop)

**As a** User,
**I want** to drag a `.cvbak` file onto the application window,
**So that** I can easily initiate the restore process without navigating complex menus.

- **Detection:** `.cvbak` extension.
- **Feedback:** "Drop Zone" overlay appears.
- **Action:** Triggers Restore Wizard.

### Story 3: Progress Feedback

**As a** User,
**I want** to see a visual indicator during the Backup and Restore processes.

- **Backup:** Spinner during "Exporting..." (2-3s). Success checkmark.
- **Restore:** Modal steps: "Verifying..." -> "Decrypting..." -> "Restoring...".

-----

## 2. TECHNICAL BRIDGE (PYTHON <-> SVELTE)

### 2.1 Backend Commands (src/core/api/routes/backup.py)

Frontend will invoke these via `invoke('command_name', args)`:

1.  `backup_create_snapshot(passkey: str, target_path: str) -> Result<bool>`
2.  `backup_restore_from_file(backup_path: str, passkey: str) -> Result<bool>`
3.  `backup_get_status() -> BackupStatus`

### 2.2 Error Codes

- `ERR_AUTH_FAILED`: Wrong passkey.
- `ERR_IO_LOCKED`: File is busy (Retry logic needed).
- `ERR_INTEGRITY`: Backup file is corrupted/tampered.

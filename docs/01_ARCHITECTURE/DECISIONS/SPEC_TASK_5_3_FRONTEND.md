# TASK 5.2b: FRONTEND USER STORIES (BACKUP & RESTORE)

**Parent Task:** Task 5.2 - Secure Backup & Restore
**Status:** READY FOR DEV
**Tech Stack:** Svelte / Tauri / TypeScript

## Story 1: Smart Toast Notification (The "Gentle Nudge")
**As a** User,
**I want** to receive a non-intrusive notification when it's time to backup my vault,
**So that** I can ensure my data is safe without being interrupted.

### Acceptance Criteria
1.  **Trigger:** The frontend periodically polls (or listens to) `get_backup_status`. If `should_backup` is true, show the toast.
2.  **UI Component:** A "Smart Toast" appears at the bottom-right (or system default location).
    - **Message:** "You've created 10+ notes. Consider backing up."
    - **Button 1:** "Backup Now" (Triggers Backup Flow).
    - **Button 2:** "Don't ask again" (Calls API to disable reminders).
    - **Checkbox:** "Don't ask again" (Alternative to Button 2, for clarity).
3.  **Behavior:**
    - Must NOT block the UI (modal is forbidden).
    - Auto-dismiss after 8 seconds if ignored.
    - "Don't ask again" must persist the preference immediately.

## Story 2: Magic Restore (Drag & Drop)
**As a** User,
**I want** to drag a `.cvbak` file onto the application window,
**So that** I can easily initiate the restore process without navigating complex menus.

### Acceptance Criteria
1.  **Detection:** The app detects when a file with the `.cvbak` extension is being dragged over the window.
2.  **Visual Feedback:** A "Drop Zone" overlay appears (e.g., "Drop to Restore Vault") with a distinct border/background.
3.  **Action:** Dropping the file triggers the **Restore Wizard**.
4.  **Validation:** If a non-`.cvbak` file is dropped, show a subtle error shake or tooltip ("Invalid Backup File").

## Story 3: Progress Feedback
**As a** User,
**I want** to see a visual indicator during the Backup and Restore processes,
**So that** I know the application is working and hasn't frozen (since crypto ops take ~2-3s).

### Acceptance Criteria
1.  **Backup Progress:**
    - Show a spinner or progress bar during the "Exporting..." phase (Avg: 2-3s).
    - Disable the "Backup" button to prevent double-clicks.
    - On success: Show a checkmark animation + "Backup Saved".
2.  **Restore Progress:**
    - Show a modal with steps: "Verifying...", "Decrypting...", "Restoring...".
    - Prevent app interaction during the critical "Atomic Swap" phase.
3.  **Performance:** Animation must remain smooth even if the main thread is busy (use CSS animations).

## Technical Notes for UI Dev
- **API Endpoints (Mock):**
    - `cmd: backup_vault(path)`
    - `cmd: restore_vault(path)`
    - `cmd: get_backup_status()` -> `{ should_backup: bool, reason: str }`
- **Error Handling:** Display friendly error messages for `InsufficientDiskSpace` or `AuthenticationError`.

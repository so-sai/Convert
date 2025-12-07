# SPECIFICATION: UX PHILOSOPHY & WORKFLOWS (TASK 5.2 - IOS 14 EDITION)

> **Ref:** TASK-5.2 | **Status:** DRAFT
> **Philosophy:** iOS 14 "Compact UI" + "Magic" Restore
> **Core Principle:** Non-intrusive Nudges & Drag-and-Drop simplicity.

## 1. THE "SMART NOTIFICATION" SYSTEM (NUDGE UI)

**Goal:** Avoid blocking modals. Respect user focus.

### 1.1 UI Patterns (Prioritized)

**Option A: Smart Toast Banner (Default)**
- **Behavior:** Slides down from top center. Auto-dismisses after 5s.
- **Content:** "📌 Backup Reminder: 10 new notes unprotected. [Fix Now]"
- **Interaction:** Tap to expand/act. Swipe up to dismiss.

**Option B: Dynamic Island (Dock Integration)**
- **Location:** Embedded in the Bookshelf Dock.
- **State:**
    - *Idle:* Pulsing shield icon (🔐).
    - *Active:* Expands on tap to show status.
- **Transition:** Seamless animation from Dock icon to Card.

## 2. RESTORE WORKFLOW ("MAGIC" UX)

**Goal:** No CLI. No "Import" buttons hidden in settings.

### 2.1 Drag-and-Drop Entry
1.  User drags `.cvbak` file onto the main App Window (Bookshelf).
2.  **Visual Feedback:**
    - Entire window dims slightly.
    - A "Drop Zone" glows blue in the center.
    - Icon changes to "Unlock" symbol (🔓).

### 2.2 Restoration Sequence
1.  **Drop:** File released.
2.  **Prompt:** Animated Card appears: "🔐 Unlock your backup" + Passkey Input.
3.  **Process:** Real-time progress bar (0% -> 100%) showing "Found X notes...".
4.  **Success:** Confetti/Celebration animation. "Welcome back! 127 notes restored."

## 3. TRUST & TRANSPARENCY

To combat "Vendor Lock-in" fears (WinRAR effect):

### 3.1 Documentation
- Explicitly link to `.cvbak` technical spec (`convert.dev/cvbak-format`).
- State: "Your data is encrypted with YOUR passkey. Convert cannot open it."

### 3.2 Escape Hatch
- Provide link to Open Source Decryption Tool (CLI) in the "About" or "Export" dialogs.

## 4. UI COMPONENT GUIDELINES
- **Aesthetic:** Apple/Stripe (Clean, Shadows, Rounded Corners).
- **Anti-Pattern:** Hacker Terminal (Black background, green text).
- **Colors:** Neutral Whites/Grays. Blue for Action. Green for Success. Red for Error.

---
**Authority:** ARCH_PRIME

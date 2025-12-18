# SPECIFICATION: UX PHILOSOPHY & WORKFLOWS (TASK 5.2)

> **Ref:** TASK-5.2 | **Status:** 40% IMPLEMENTED  
> **Philosophy:** iOS 14 "Compact UI" + "Magic" Restore  
> **Core Principle:** Non-intrusive Nudges & Drag-and-Drop simplicity  
> **Integration:** See SPEC_TASK_5_3 for combined implementation status

---

## 1. THE "SMART NOTIFICATION" SYSTEM (NUDGE UI) ⏳ PENDING

**Goal:** Avoid blocking modals. Respect user focus.

### 1.1 UI Patterns (Prioritized)

**Option A: Smart Toast Banner (Default)** ✅ IMPLEMENTED
- **Behavior:** Slides down from top center. Auto-dismisses after 3s (configurable).
- **Content:** Supports info/success/error types with icons.
- **Interaction:** Auto-dismiss with visual feedback.
- **Implementation:** `Toast.svelte` (65 lines) + `toast.svelte.ts` store (Runes)
- **Status:** COMPLETE

**Option B: Dynamic Island (Dock Integration)** ⏳ NOT IMPLEMENTED
- **Location:** Embedded in the Bookshelf Dock.
- **State:**
    - *Idle:* Pulsing shield icon (🔐).
    - *Active:* Expands on tap to show status.
- **Transition:** Seamless animation from Dock icon to Card.
- **Priority:** LOW (Future enhancement)

---

## 2. RESTORE WORKFLOW ("MAGIC" UX) ⏳ PENDING

**Goal:** No CLI. No "Import" buttons hidden in settings.

### 2.1 Drag-and-Drop Entry ✅ IMPLEMENTED
1.  User drags `.cvbak` file onto the main App Window.
2.  **Visual Feedback:**
    - Entire window dims with backdrop blur.
    - A "Drop Zone" glows blue in the center with pulsing icon.
    - Dashed border animation.
- **Implementation:** `DropZone.svelte` (166 lines, Tauri Native Events)
- **Status:** COMPLETE

### 2.2 Restoration Sequence ⏳ PARTIAL
1.  **Drop:** File released.
2.  **Prompt:** Animated Card appears: "🔐 Unlock your backup" + Passkey Input.
3.  **Process:** Real-time progress bar (0% -> 100%) showing "Found X notes...". ✅ IMPLEMENTED
4.  **Success:** Confetti/Celebration animation. "Welcome back! 127 notes restored." ⏳ PENDING

**Note:** Progress visualization exists in `BackupConsole.svelte`, can be reused for restore flow.

---

## 3. TRUST & TRANSPARENCY ⏳ PENDING

To combat "Vendor Lock-in" fears (WinRAR effect):

### 3.1 Documentation ⏳ NOT IMPLEMENTED
- Explicitly link to `.cvbak` technical spec (`convert.dev/cvbak-format`).
- State: "Your data is encrypted with YOUR passkey. Convert cannot open it."
- **Priority:** LOW (Trust-building)
- **Estimate:** 30 minutes

### 3.2 Escape Hatch ⏳ NOT IMPLEMENTED
- Provide link to Open Source Decryption Tool (CLI) in the "About" or "Export" dialogs.
- **Priority:** LOW
- **Estimate:** 15 minutes

---

## 4. UI COMPONENT GUIDELINES ✅ IMPLEMENTED

- **Aesthetic:** Apple/Stripe (Clean, Shadows, Rounded Corners). ✅
- **Anti-Pattern:** Hacker Terminal (Black background, green text). ✅ AVOIDED
- **Colors:** Neutral Whites/Grays. Blue for Action. Green for Success. Red for Error. ✅

**Implementation:** See `BackupConsole.svelte` and `app.css` for visual system.

---

## IMPLEMENTATION STATUS SUMMARY

| Feature | Status | Priority | Estimate |
|---------|--------|----------|----------|
| **Smart Toast** | ✅ Done | N/A | N/A |
| **Drag-Drop Restore** | ✅ Done | N/A | N/A |
| **Progress Display** | ✅ Done | N/A | N/A |
| **Trust Messaging** | ⏳ Pending | LOW | 30min |
| **Visual Guidelines** | ✅ Done | N/A | N/A |

**Overall:** 75% Complete (Visual system done, Toast done, DropZone done, Nudge logic pending)

---

**Authority:** ARCH_PRIME  
**Last Updated:** 2025-12-07  
**See Also:** [SPEC_TASK_5_3_FRONTEND.md](SPEC_TASK_5_3_FRONTEND.md) for full implementation details
---

## 5. THE NUDGE SYSTEM & MAGIC RESTORE (DETAILED SPEC)

### 5.1 Design Rationale (The WinRAR Paradox)
- **Problem:** Users ignore generic security warnings.
- **Solution:** 3-Act Escalation (Educator → Realist → Final Offer).
- **Principle:** Triggers must be **Event-Driven** (e.g., 10th note saved), NOT Calendar-Driven.

### 5.2 Trigger Logic
| Nudge | Event | Timing | Psychology |
|-------|-------|--------|------------|
| **#1: Educator** | `note_count == 10` AND `nudge_count == 0` | Immediate | Peak Loss Aversion |
| **#2: Realist** | `word_count > 500` AND `days_since(nudge1) > 60` | After edit | Regret Prevention |
| **#3: Final Offer** | `export_action` OR `batch_delete` AND `days > 90` | Before action | Precautionary Principle |

### 5.3 Message Content (3-Act Escalation)
- **Nudge #1 (Educator):** "✨ Bảo vệ ghi chú... 1 phút thiết lập." (Gentle)
- **Nudge #2 (Realist):** "⚠️ Ghi chú chưa được bảo vệ... Rủi ro mất vĩnh viễn." (Warning)
- **Nudge #3 (Final Offer):** "🔒 Cơ hội cuối... Chúng tôi sẽ không nhắc lại." (Ultimatum)

### 5.4 Magic Restore (Drag-and-Drop) Implementation
- **Component:** `DropZone.svelte` (Overlay).
- **Trigger:** `tauri://file-drop` event.
- **Visuals:**
  - Window dims (Overlay: `bg-black/50` + `backdrop-blur-sm`).
  - Dashed border zone appears in center.
  - Text: "Drop .cvbak to Restore".
- **Z-Index:** Must be `z-50` (Highest), covering all Modals.

### 5.5 State Management Schema
```sql
CREATE TABLE nudge_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nudge_count INTEGER DEFAULT 0,
    last_nudge_shown TEXT,
    permanent_optout BOOLEAN DEFAULT 0
);
```

### 5.6 Progressive Disclosure Flow
1. **Step 1:** Nudge appears → User clicks "Fix Now".
2. **Step 2:** Show **Passkey Setup Modal** ONLY. (Low friction).
3. **Step 3:** Success → Show "Great! Now add Backup".
4. **Step 4:** Show **Backup Path Selection**.

### 5.7 Celebration Animation Specs
- **Type:** Confetti particles (Canvas/SVG).
- **Duration:** 1.5s total.
- **Accessibility:** Respects `prefers-reduced-motion`.
- **Colors:** System Green (#34C759) + White.

---

**Authority:** ARCH_PRIME  
**Last Updated:** 2025-12-07  
**See Also:** [SPEC_TASK_5_3_FRONTEND.md](SPEC_TASK_5_3_FRONTEND.md) for full implementation details


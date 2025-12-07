# SPECIFICATION: CONVERT PROTOCOL FRONTEND SYSTEM (TASK 5.3)

**Reference:** TASK-5.3 | **Status:** FINAL (Implementation Complete)
**Stack:** Svelte 5 (Runes) + Tauri v2 (Rust IPC)
**Design Anchor:** Modern Glassmorphism with Tactile UX
**Security Model:** Zero-Trust, Event-Driven, Blind-View Architecture

---

## 🎨 I. VISUAL HARMONY SYSTEM

### Core Philosophy: "Felt, Not Explained"
The interface should evoke a sense of premium quality without revealing its technical foundations. Users should experience visual sophistication without analyzing its components.

### 1.1 Depth & Materiality
- **Primary Surfaces:** Frosted glass effect with 32px blur and 200% saturation
- **Light Mode:** `rgba(255, 255, 255, 0.75)` with subtle gradient overlays
- **Dark Mode:** `rgba(28, 28, 30, 0.70)` with deep contrast layers
- **Border Treatment:** 1px subtle borders with luminosity-based opacity

### 1.2 Shape Language
- **Containers:** 20-24px radius (soft contours, not circular)
- **Interactive Elements:** 12-14px radius with tactile feedback
- **Layout Grid:** 8pt baseline grid with fluid spacing

### 1.3 Chromatic Harmony
```
Primary Action:   #007AFF (System Blue)
Success States:   #34C759 (System Green)
Error States:     #FF3B30 (System Red)
Warning States:   #FF9500 (System Orange)

Background Layers:
  Light: #F5F5F7 → #FFFFFF gradient
  Dark:  #1C1C1E → #2C2C2E gradient
```

### 1.4 Motion & Responsiveness
- **Duration Standard:** 250ms cubic-bezier(0.4, 0.0, 0.2, 1)
- **Hover States:** -2px vertical translation with shadow elevation
- **Active States:** 0.98 scale with slight shadow reduction
- **Status Animations:** Pulsing resonance for active processes

---

## 🔐 II. SECURITY INTEGRATION PATTERNS

### 2.1 The "Blind Observer" Principle
Frontend acts as a passive viewer that never handles sensitive data directly.

#### Command Contracts:
```typescript
// Backup Initiation
cmd_backup_start(target_dir?: string): Promise<string>

// Recovery Key Export
cmd_export_recovery_svg(auth: string): Promise<ExportResponse>
```

#### Event Stream:
```typescript
interface BackupProgress {
  phase: 'idle' | 'init' | 'snapshot' | 'encrypting' | 'finalizing' | 'done' | 'error';
  progress: number;           // 0.0 to 100.0
  processed_bytes: number;
  total_bytes: number;
  speed: string;              // "45 MB/s"
  eta: string;                // "12-15s" (range, not fixed)
  error?: string;
}
```

### 2.2 Recovery Key Display Protocol
- **Initial State:** SVG blurred with `filter: blur(10px)`
- **Reveal Mechanism:** Press-and-hold to temporarily remove blur
- **Auto-Wipe:** Data URI cleared after TTL expiration (60s)
- **Zero Persistence:** No caching, no DOM storage, no screenshots via API

### 2.3 Error Handling Philosophy
- **No Technical Details:** Generic messages for security errors
- **No Retry Prompts:** Automatic retry logic handled by Rust backend
- **State Preservation:** UI state maintained during transient failures

---

## 🤖 III. USER EXPERIENCE WORKFLOWS

### 3.1 Proactive Notification System
```
Priority Levels:
  1. Toast Banner (Top-center, auto-dismiss)
  2. Status Bar Integration
  3. Dynamic Dock Indicator
```

**Notification Patterns:**
- Backup reminders with "Fix Now" action
- Completion confirmations with file path
- Security warnings with time-sensitive actions

### 3.2 Restore Flow ("Magic Restore")
```
1. Drag .cvbak file onto application window
2. Window responds with drop zone glow
3. Authentication prompt appears
4. Real-time progress with itemized restoration
5. Celebration animation on completion
```

### 3.3 Trust & Transparency Features
- **Open Format Documentation:** `.cvbak` technical specification publicly accessible
- **Escape Hatch:** CLI decryption tool availability
- **Clear Boundaries:** "Your passphrase never leaves your device" messaging

---

## 🧩 IV. COMPONENT ARCHITECTURE

### 4.1 State Management (Svelte 5 Runes)
```typescript
// stores/backup.svelte.ts
export class BackupState {
  phase = $state<'idle' | 'init' | 'snapshot' | 'encrypting' | 'finalizing' | 'done' | 'error'>('idle');
  progress = $state(0);
  // ... other states
  
  constructor() {
    listen('backup_progress', (event) => {
      // Event-driven updates only
    });
  }
}
```

### 4.2 Core Components

#### A. Nexus Console (Primary Interface)
- **Purpose:** Main backup control and monitoring
- **Features:** Progress visualization, speed/ETA display, error states
- **Behaviors:** Hover elevation, status resonance animation

#### B. Recovery Viewer
- **Purpose:** Secure recovery key display
- **Features:** Blurred default, press-to-reveal, auto-wipe
- **Security:** No DOM persistence, memory-only storage

#### C. Notification Systems
- **Toast Banner:** Non-blocking, auto-dismissing
- **Status Indicators:** Dock integration, subtle animations
- **Actionable Alerts:** Context-specific actions with one-tap resolution

### 4.3 Layout Composition
```
Desktop Layout:
  [ Header: Convert Protocol Identity ]
  [ Left Panel: System Health & Quick Actions ]
  [ Main Panel: Nexus Console (2/3 width) ]
  [ Footer: Version & Status Information ]
  
Mobile Adaptation:
  Vertical stack with priority:
  1. Current operation status
  2. Primary controls
  3. Supplemental information
```

---

## 🎯 V. IMPLEMENTATION CHECKLIST

### 5.1 Visual System (CSS)
- [x] Frosted glass effect with backdrop-filter support
- [x] Adaptive color scheme (light/dark with system preference)
- [x] Motion curves matching modern platform standards
- [x] Responsive breakpoints: mobile (320px), tablet (768px), desktop (1024px+)
- [x] Accessibility: minimum contrast ratios, keyboard navigation, screen reader labels

### 5.2 Security Integration
- [x] IPC command handlers registered in Rust
- [x] Event listeners for backup progress
- [x] Recovery key display with blur/hold mechanics
- [x] Memory sanitation after sensitive operations

### 5.3 User Experience
- [ ] Toast notification system
- [ ] Drag-and-drop restore handlers
- [x] Progress visualization with real-time updates
- [ ] Error states with recovery guidance
- [ ] Celebration animations for completion

### 5.4 Performance Requirements
- **First Paint:** < 1s on moderate hardware
- **Animation:** 60fps for all interactive elements
- **Memory:** No memory leaks, clean disposal of sensitive data
- **Bundle Size:** < 2MB initial load, lazy loading for secondary features

---

## 📚 VI. DOCUMENTATION & TRANSPARENCY

### 6.1 User-Facing Documentation
- `.cvbak` file format specification (public)
- Recovery process walkthrough
- Security model explanation (zero-knowledge architecture)

### 6.2 Developer Guidelines
- Component styling conventions
- State management patterns
- Event handling best practices
- Security protocol adherence

### 6.3 Testing Requirements
- **Visual Regression:** Pixel-perfect across breakpoints
- **Functional:** All IPC commands and events
- **Security:** Memory inspection for sensitive data leakage
- **Performance:** Bundle size, paint times, animation smoothness

---

## 🔗 VII. CROSS-TASK INTEGRATION

### 7.1 With TASK-5.2 (UX Audit)
- Unified notification system
- Consistent restore flow
- Trust-building transparency features

### 7.2 With Backend Systems
- Event stream compatibility
- Error state synchronization
- Performance metric alignment

### 7.3 With Future Features
- Extensible component architecture
- Scalable state management
- Theming system foundations

---

## 🏁 VIII. ACCEPTANCE CRITERIA

A user should be able to:
1. Initiate a backup and watch real-time progress with intuitive visual feedback
2. Export a recovery key that's securely displayed and automatically protected
3. Receive non-intrusive notifications about system status
4. Restore from backup using drag-and-drop without hunting for import buttons
5. Trust that their data remains private through clear security communication

---

## ✅ STATUS: READY FOR IMPLEMENTATION

This specification now serves as the **single source of truth** for Convert Protocol's frontend system, combining visual design, user experience, and security requirements into a cohesive implementation guide.

*Convert Protocol — Where security meets elegance, felt but never explained.*

import os

def write(path, content):
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Restored: {path}")

# =========================================================
# 1. APP.CSS (CRYSTAL THEME SYSTEM)
# =========================================================
app_css = """
/* IRON VAULT - CRYSTAL EDITION (NATIVE CSS) */
:root {
    --bg-main: #0f0f0f;
    --bg-panel: #1a1a1a;
    --border-dim: #333;
    --border-bright: #555;
    
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --text-accent: #ffffff;

    --brand-blue: #2563eb;
    --brand-blue-hover: #3b82f6;
    --brand-green: #16a34a;
    --brand-red: #dc2626;

    --glass-bg: rgba(26, 26, 26, 0.8);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    
    --font-stack: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    padding: 0;
    font-family: var(--font-stack);
    background-color: var(--bg-main);
    color: var(--text-primary);
    overflow: hidden; /* App-like feel */
    height: 100vh;
    width: 100vw;
}

/* Utilities */
.glass {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
}

.btn-reset {
    background: none;
    border: none;
    cursor: pointer;
    font: inherit;
    color: inherit;
    padding: 0;
}
"""

# =========================================================
# 2. TOAST.SVELTE
# =========================================================
toast_svelte = """
<script>
  import { onMount } from 'svelte';
  let { message, type = 'info', duration = 3000 } = $props();
  let visible = $state(true);

  onMount(() => {
    const timer = setTimeout(() => visible = false, duration);
    return () => clearTimeout(timer);
  });
</script>

{#if visible}
<div class="toast-container glass" class:success={type === 'success'} class:error={type === 'error'}>
  <div class="icon">
    {#if type === 'success'}✅{:else if type === 'error'}❌{:else}ℹ️{/if}
  </div>
  <div class="message">{message}</div>
</div>
{/if}

<style>
  .toast-container {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    
    display: flex;
    align-items: center;
    gap: 12px;
    
    padding: 12px 24px;
    border-radius: 9999px; /* Pill shape */
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    
    background: rgba(30, 30, 30, 0.95);
    border: 1px solid rgba(255,255,255,0.1);
    
    animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .message {
    color: white;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  .icon { font-size: 18px; }

  @keyframes slideDown {
    from { transform: translate(-50%, -100%); opacity: 0; }
    to { transform: translate(-50%, 0); opacity: 1; }
  }
</style>
"""

# =========================================================
# 3. DROPZONE.SVELTE
# =========================================================
dropzone_svelte = """
<script>
  import { listen } from '@tauri-apps/api/event';
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';
  import Toast from './Toast.svelte';

  let isDragging = $state(false);
  let toast = $state(null);

  onMount(async () => {
    await listen('tauri://drag-enter', () => isDragging = true);
    await listen('tauri://drag-leave', () => isDragging = false);
    await listen('tauri://drop', async (e) => {
      isDragging = false;
      const files = e.payload.paths || []; 
      const file = files.find(f => f.endsWith('.cvbak'));
      
      if (file) {
        toast = { msg: 'Restoring System...', type: 'info' };
        try {
            await invoke('cmd_restore_backup', { path: file });
            toast = { msg: 'Restore Success! Welcome back.', type: 'success' };
        } catch (err) {
            toast = { msg: 'Restore Failed: ' + err, type: 'error' };
        }
      } else {
        toast = { msg: 'Invalid file! Please drop a .cvbak file.', type: 'error' };
      }
    });
  });
</script>

{#if isDragging}
<div class="drop-overlay glass">
  <div class="drop-content">
    <div class="emoji">📦</div>
    <h2>Drop to Restore</h2>
  </div>
</div>
{/if}

{#if toast}
  <Toast message={toast.msg} type={toast.type} />
{/if}

<style>
  .drop-overlay {
    position: fixed;
    inset: 0; /* top/right/bottom/left: 0 */
    z-index: 9990;
    background: rgba(37, 99, 235, 0.2); /* Brand Blue Tint */
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 8px dashed rgba(96, 165, 250, 0.5);
    margin: 16px;
    border-radius: 32px;
    pointer-events: none;
  }

  .drop-content {
      text-align: center;
      animation: bounce 1s infinite;
  }

  .emoji { font-size: 80px; margin-bottom: 16px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3)); }
  
  h2 {
    font-size: 40px;
    font-weight: 800;
    color: white;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    margin: 0;
  }

  @keyframes bounce {
      0%, 100% { transform: translateY(-5%); }
      50% { transform: translateY(5%); }
  }
</style>
"""

# =========================================================
# 4. RECOVERY MODAL.SVELTE
# =========================================================
recovery_svelte = """
<script>
  import { onMount } from "svelte";
  import { invoke } from '@tauri-apps/api/core';

  let { onClose } = $props();
  let imageData = $state(null);
  let isRevealed = $state(false);
  let timeLeft = $state(60);

  onMount(async () => {
    try {
        const res = await invoke('cmd_export_recovery_svg', { auth: 'test' });
        imageData = res.data_uri;
        
        const timer = setInterval(() => {
            timeLeft--;
            if (timeLeft <= 0) {
                clearInterval(timer);
                onClose();
            }
        }, 1000);
    } catch (e) { console.error(e); }
  });
</script>

<div class="modal-backdrop">
  <div class="modal-card">
    <!-- Progress Bar -->
    <div class="progress-bar-bg">
        <div class="progress-bar-fill" style="width: {(timeLeft/60)*100}%"></div>
    </div>

    <div class="header">
        <h2>🔐 Recovery Key</h2>
        <span class="timer">{timeLeft}s</span>
    </div>
    
    <div 
        class="qr-container"
        onmousedown={() => isRevealed = true}
        onmouseup={() => isRevealed = false}
        onmouseleave={() => isRevealed = false}
    >
        {#if imageData}
            <img src={imageData} alt="Secret" class="qr-image" class:blurred={!isRevealed} />
            
            {#if !isRevealed}
                <div class="overlay-msg">
                    <span class="pill">HOLD TO REVEAL</span>
                </div>
            {/if}
        {:else}
            <div class="loading">Generating Secure Key...</div>
        {/if}
    </div>

    <p class="warning">Data exists only in RAM. Zero-knowledge guaranteed.</p>
    
    <button onclick={onClose} class="btn-close">
        CLOSE & WIPE MEMORY
    </button>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.9);
    backdrop-filter: blur(8px);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-card {
    background: #1a1a1a;
    border: 1px solid #333;
    padding: 32px;
    border-radius: 20px;
    width: 400px;
    text-align: center;
    position: relative;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    overflow: hidden;
  }

  .progress-bar-bg {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: #333;
  }
  .progress-bar-fill {
    height: 100%;
    background: #dc2626; /* Brand Red */
    transition: width 1s linear;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  h2 { margin: 0; color: white; font-size: 24px; }
  .timer { color: #dc2626; font-family: monospace; font-size: 20px; font-weight: bold; }

  .qr-container {
      background: white;
      padding: 24px;
      border-radius: 12px;
      margin-bottom: 24px;
      position: relative;
      cursor: pointer;
      height: 200px; /* Fixed height container */
      display: flex;
      align-items: center;
      justify-content: center;
      user-select: none;
      box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
  }

  .qr-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
      transition: all 0.3s ease;
  }
  .qr-image.blurred { filter: blur(12px) opacity(0.5); transform: scale(0.95); }

  .overlay-msg {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      pointer-events: none;
  }

  .pill {
      background: rgba(0,0,0,0.8);
      color: white;
      padding: 8px 16px;
      border-radius: 99px;
      font-size: 14px;
      font-weight: bold;
      box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  }

  .loading { color: #666; animation: pulse 1s infinite; }

  .warning { color: #666; font-size: 12px; font-family: monospace; margin-bottom: 24px; }

  .btn-close {
      width: 100%;
      background: #dc2626;
      color: white;
      border: none;
      padding: 12px;
      border-radius: 12px;
      font-weight: bold;
      font-size: 16px;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
      box-shadow: 0 10px 15px -3px rgba(220, 38, 38, 0.2);
  }
  .btn-close:hover { background: #ef4444; }
  .btn-close:active { transform: scale(0.98); }

  @keyframes pulse { 50% { opacity: 0.5; } }
</style>
"""

# =========================================================
# 5. BACKUP CONSOLE.SVELTE
# =========================================================
backup_console_svelte = """
<script>
    import { backupState } from "../stores/backup.svelte.js";
</script>

<div class="console-dock">
    {#if backupState.phase === "idle"}
        <div class="console-idle">
            <span class="status-text">System Ready. Encrypted Database V2.</span>
            <button onclick={() => backupState.start()} class="btn-backup">
                BACKUP NOW
            </button>
        </div>
    {:else}
        <div class="console-active">
            <div class="meta-row">
                <span>PHASE: {backupState.phase.toUpperCase()}</span>
                <span>SPEED: {backupState.speed} | ETA: {backupState.eta}</span>
            </div>

            <div class="progress-track">
                <div class="progress-bar" style="width: {backupState.progress}%"></div>
            </div>

            <div class="info-row">
                <span class="message">{backupState.message}</span>
                <span class="percent">{Math.round(backupState.progress)}%</span>
            </div>
        </div>
    {/if}
</div>

<style>
.console-dock {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: #1a1a1a;
    border-top: 1px solid #333;
    padding: 16px;
    z-index: 100;
    font-family: monospace;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
}

/* IDLE STATE */
.console-idle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.status-text { color: #666; font-size: 14px; }

.btn-backup {
    background: #2563eb;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.2s;
}
.btn-backup:hover { background: #3b82f6; }

/* ACTIVE STATE */
.console-active {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #666;
}

.progress-track {
    width: 100%;
    height: 16px;
    background: #2a2a2a;
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid #444;
}

.progress-bar {
    height: 100%;
    background: #3b82f6;
    transition: width 0.2s ease-out;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.message { color: white; font-size: 14px; font-weight: 500; }
.percent { color: #60a5fa; font-weight: bold; }
</style>
"""

# =========================================================
# 6. APP.SVELTE (MAIN SHELL)
# =========================================================
app_svelte = """
<script>
  import { Box, Book, Zap } from 'lucide-svelte';
  import RecoveryModal from "./lib/components/RecoveryModal.svelte";
  import BackupConsole from "./lib/components/BackupConsole.svelte";
  import DropZone from "./lib/components/DropZone.svelte";

  let showRecovery = $state(false);
</script>

<DropZone />

<main class="app-layout">
  
  <nav class="sidebar glass">
    <button class="nav-btn primary"><Box size={28} /></button>
    <div class="spacer"></div>
    <button onclick={() => showRecovery = true} class="nav-btn secure-btn" title="Recovery Key">
        <div class="secure-icon">S</div>
    </button>
  </nav>

  <section class="content-area">
    <header class="hero-header">
        <h1>Hello, Architect.</h1>
        <p>Your digital sanctum is ready.</p>
    </header>

    <div class="card-grid">
        <!-- CARD 1 -->
        <button class="feature-card glass hover-blue">
            <div class="card-icon-bg"><Box size={140} /></div>
            <div class="card-content">
                <h3>CONVERT</h3>
                <p>Universal Format Engine.</p>
            </div>
        </button>

        <!-- CARD 2 -->
        <button class="feature-card glass hover-green">
            <div class="card-icon-bg"><Book size={140} /></div>
            <div class="card-content">
                <h3>NOTES</h3>
                <p>Knowledge Management.</p>
            </div>
        </button>

        <!-- CARD 3 -->
        <button class="feature-card glass hover-purple">
            <div class="card-icon-bg"><Zap size={140} /></div>
            <div class="card-content">
                <h3>WORKFLOW</h3>
                <p>AI Agents & Automation.</p>
            </div>
        </button>
    </div>
  </section>

  {#if showRecovery}
    <RecoveryModal onClose={() => showRecovery = false} />
  {/if}

  <BackupConsole />

</main>

<style>
/* LAYOUT */
.app-layout {
    display: flex;
    height: 100vh;
    background: #0f0f0f;
    color: #e0e0e0;
}

/* SIDEBAR */
.sidebar {
    width: 80px;
    border-right: 1px solid #333;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 32px 0;
    gap: 32px;
    z-index: 10;
    background: #1a1a1a;
}

.spacer { flex: 1; }

.nav-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 12px;
    border-radius: 16px;
    transition: all 0.2s;
    color: #666;
}
.nav-btn:hover { color: white; background: rgba(255,255,255,0.1); }

.nav-btn.primary {
    background: #2563eb;
    color: white;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}
.nav-btn.primary:hover { background: #3b82f6; }

.secure-icon {
    width: 40px; height: 40px;
    border-radius: 50%;
    border: 2px solid #22c55e;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #22c55e;
    font-weight: bold;
    background: rgba(34, 197, 94, 0.1);
    box-shadow: 0 0 15px rgba(34, 197, 94, 0.2);
}

/* CONTENT */
.content-area {
    flex: 1;
    padding: 40px;
    overflow-y: auto;
    padding-bottom: 160px; /* Space for console */
}

.hero-header { margin-bottom: 48px; }
.hero-header h1 { font-size: 48px; font-weight: 800; margin: 0 0 8px 0; letter-spacing: -1px; color: white; }
.hero-header p { font-size: 20px; color: #666; margin: 0; }

.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr); /* 3 Columns like requested */
    gap: 32px;
}

@media (max-width: 1024px) {
    .card-grid { grid-template-columns: 1fr; }
}

/* CARDS */
.feature-card {
    position: relative;
    height: 380px;
    border-radius: 24px;
    padding: 32px;
    text-align: left;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s, border-color 0.3s, box-shadow 0.3s;
    background: #1a1a1a;
    border: 1px solid #333;
    color: inherit;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

.feature-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }

/* Card Variants */
.hover-blue:hover { border-color: #2563eb; box-shadow: 0 20px 40px rgba(37, 99, 235, 0.15); }
.hover-green:hover { border-color: #16a34a; box-shadow: 0 20px 40px rgba(22, 163, 74, 0.15); }
.hover-purple:hover { border-color: #9333ea; box-shadow: 0 20px 40px rgba(147, 51, 234, 0.15); }

.card-content { position: relative; z-index: 2; }
.card-content h3 { font-size: 32px; margin: 0 0 8px 0; color: white; }
.card-content p { color: #888; margin: 0; font-size: 16px; }

.card-icon-bg {
    position: absolute;
    top: 0; right: 0;
    padding: 32px;
    opacity: 0.1;
    transition: transform 0.5s, opacity 0.5s;
    color: white;
}
.feature-card:hover .card-icon-bg {
    transform: scale(1.1) rotate(5deg);
    opacity: 0.2;
}
</style>
"""

# EXECUTE RESTORATION
base_ui = "../src-ui/src"
write(f"{base_ui}/app.css", app_css)
write(f"{base_ui}/lib/components/Toast.svelte", toast_svelte)
write(f"{base_ui}/lib/components/DropZone.svelte", dropzone_svelte)
write(f"{base_ui}/lib/components/RecoveryModal.svelte", recovery_svelte)
write(f"{base_ui}/lib/components/BackupConsole.svelte", backup_console_svelte)
write(f"{base_ui}/App.svelte", app_svelte)

print("💎 Crystal UI Restored (Native CSS Edition). Ready to launch.")

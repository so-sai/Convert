import os
from pathlib import Path

# Đảm bảo đường dẫn gốc
try:
    os.chdir("E:/DEV/Convert")
except:
    pass

def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Updated: {path}")

# ==========================================
# 1. LOGIC QUẢN LÝ BACKUP (Store JS thuần)
# ==========================================
backup_store = r"""
import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';

// Svelte 5 Runes (Global State)
export const backupState = $state({
    phase: 'idle',      // idle, init, copying, done, error
    progress: 0,
    speed: '--',
    eta: '--',
    message: '',
    
    async start() {
        try {
            this.phase = 'init';
            this.message = 'Starting...';
            await invoke('cmd_backup_start'); 
        } catch (err) {
            this.phase = 'error';
            this.message = err;
        }
    }
});

listen('backup_progress', (event) => {
    const p = event.payload;
    backupState.phase = p.phase;
    backupState.progress = p.progress;
    backupState.speed = p.speed;
    backupState.eta = p.eta;
    backupState.message = p.message;
});
"""

# ==========================================
# 2. GIAO DIỆN CONSOLE (Thanh chạy %)
# ==========================================
backup_console = r"""
<script>
  import { backupState } from '../stores/backup.svelte.js';
</script>

<div class="fixed bottom-0 left-0 right-0 bg-[#1a1a1a] border-t border-[#333] p-4 shadow-2xl z-50 font-mono">
  
  {#if backupState.phase === 'idle'}
    <div class="flex justify-between items-center">
        <span class="text-gray-400 text-sm">System Ready. Encrypted Database V2.</span>
        <button 
            onclick={() => backupState.start()}
            class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-bold transition flex items-center gap-2 cursor-pointer">
            BACKUP NOW
        </button>
    </div>

  {:else}
    <div class="space-y-2">
        <div class="flex justify-between text-xs text-gray-400">
            <span>PHASE: {backupState.phase.toUpperCase()}</span>
            <span>SPEED: {backupState.speed} | ETA: {backupState.eta}</span>
        </div>
        
        <div class="w-full bg-gray-800 rounded-full h-4 overflow-hidden border border-gray-700">
            <div 
                class="bg-blue-500 h-full transition-all duration-200 ease-out" 
                style="width: {backupState.progress}%">
            </div>
        </div>

        <div class="flex justify-between items-center">
            <span class="text-white text-sm font-medium">{backupState.message}</span>
            <span class="text-blue-400 font-bold">{Math.round(backupState.progress)}%</span>
        </div>
    </div>
  {/if}
</div>
"""

# ==========================================
# 3. COMPONENT: RECOVERY MODAL (Security)
# ==========================================
recovery_modal = r"""
<script>
  import { onMount } from "svelte";
  import { invoke } from '@tauri-apps/api/core';

  let { onClose } = $props();
  let imageData = $state(null);
  let isRevealed = $state(false);

  onMount(async () => {
    // Gọi Rust để lấy ảnh (Giả lập hoặc thật)
    try {
        const res = await invoke('cmd_export_recovery_svg', { auth: 'test' });
        imageData = res.data_uri;
    } catch (e) {
        console.error(e);
    }
  });
</script>

<div class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm font-sans">
  <div class="bg-[#1a1a1a] border border-[#333] p-6 rounded-xl w-96 text-center shadow-2xl">
    <h2 class="text-xl font-bold mb-4 text-white">🔐 The Iron Vault</h2>
    
    <div 
        class="bg-white p-4 rounded-lg mb-4 cursor-pointer relative overflow-hidden group"
        role="button"
        tabindex="0"
        onmousedown={() => isRevealed = true}
        onmouseup={() => isRevealed = false}
        onmouseleave={() => isRevealed = false}
    >
        {#if imageData}
            <img src={imageData} alt="Secret" class="w-full h-48 object-contain transition-all {isRevealed ? 'blur-0' : 'blur-xl opacity-50'}" />
            {#if !isRevealed}
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span class="bg-black/70 text-white px-3 py-1 rounded-full text-sm font-bold">HOLD TO REVEAL</span>
                </div>
            {/if}
        {:else}
            <div class="h-48 flex items-center justify-center text-gray-500 animate-pulse">Generating Secure Key...</div>
        {/if}
    </div>

    <button onclick={onClose} class="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 rounded font-medium transition cursor-pointer">
        Done & Wipe Memory
    </button>
  </div>
</div>
"""

# ==========================================
# 4. MÀN HÌNH CHÍNH (APP.SVELTE)
# ==========================================
app_svelte = r"""
<script>
  import { Box, Book, Brain, Zap } from 'lucide-svelte';
  import RecoveryModal from "./lib/components/RecoveryModal.svelte";
  import BackupConsole from "./lib/components/BackupConsole.svelte";

  let showRecovery = $state(false);
</script>

<main class="flex h-screen w-screen bg-[#0f0f0f] text-gray-200 font-sans overflow-hidden">
  
  <!-- Sidebar -->
  <nav class="w-16 bg-[#1a1a1a] border-r border-[#333] flex flex-col items-center py-6 gap-6 z-10">
    <button class="p-3 rounded-xl bg-blue-600 text-white shadow-lg shadow-blue-900/50">
      <Box size={24} />
    </button>
    <div class="flex-1"></div>
    <button onclick={() => showRecovery = true} class="p-2 text-gray-400 hover:text-white transition cursor-pointer" title="Recovery Key">
        <div class="w-8 h-8 rounded-full border-2 border-green-500 bg-green-900/30 flex items-center justify-center text-xs font-bold text-green-400">S</div>
    </button>
  </nav>

  <!-- Main Content -->
  <section class="flex-1 p-8 overflow-y-auto pb-32">
    <header class="mb-12">
        <h1 class="text-4xl font-bold text-white mb-2">Hello, Architect.</h1>
        <p class="text-gray-400">Your digital sanctum is ready.</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Cards -->
        <button class="group relative h-80 bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 hover:border-blue-500 transition-all hover:-translate-y-2 text-left shadow-xl cursor-pointer">
            <div class="h-full flex flex-col justify-end">
                <h3 class="text-2xl font-bold text-white mb-2">Convert</h3>
                <p class="text-gray-400 text-sm">Universal Format Engine.</p>
            </div>
        </button>

        <button class="group relative h-80 bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 hover:border-green-500 transition-all hover:-translate-y-2 text-left shadow-xl cursor-pointer">
            <div class="h-full flex flex-col justify-end">
                <h3 class="text-2xl font-bold text-white mb-2">Second Brain</h3>
                <p class="text-gray-400 text-sm">Local Knowledge Base.</p>
            </div>
        </button>

        <button class="group relative h-80 bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 hover:border-purple-500 transition-all hover:-translate-y-2 text-left shadow-xl cursor-pointer">
            <div class="h-full flex flex-col justify-end">
                <h3 class="text-2xl font-bold text-white mb-2">Workflow</h3>
                <p class="text-gray-400 text-sm">Automation Pipelines.</p>
            </div>
        </button>
    </div>
  </section>

  {#if showRecovery}
    <RecoveryModal onClose={() => showRecovery = false} />
  {/if}

  <BackupConsole />

</main>
"""

# EXECUTE
print("🚀 DEPLOYING IRON VAULT UI v3...")
write_file("src-ui/src/lib/stores/backup.svelte.js", backup_store)
write_file("src-ui/src/lib/components/BackupConsole.svelte", backup_console)
write_file("src-ui/src/lib/components/RecoveryModal.svelte", recovery_modal)
write_file("src-ui/src/App.svelte", app_svelte)
print("✅ DEPLOYMENT COMPLETE.")

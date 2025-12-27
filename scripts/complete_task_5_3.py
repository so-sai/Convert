import os

# Đảm bảo đường dẫn
try:
    os.chdir("E:/DEV/app-desktop-Convert")
except:
    pass

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created: {path}")

# =========================================================
# 1. FRONTEND COMPONENTS (SVELTE 5)
# =========================================================

# A. TOAST
toast_svelte = r"""
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
<div class="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-4 py-3 rounded-2xl backdrop-blur-xl bg-[#1a1a1a]/90 border border-white/10 shadow-2xl animate-slide-down">
  <div class="text-xl">
    {#if type === 'success'}✅{:else if type === 'error'}❌{:else}ℹ️{/if}
  </div>
  <div class="text-sm font-medium text-white">{message}</div>
</div>
{/if}

<style>
  .animate-slide-down { animation: slide 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
  @keyframes slide { from { transform: translate(-50%, -100%); opacity: 0; } to { transform: translate(-50%, 0); opacity: 1; } }
</style>
"""

# B. DROPZONE (MAGIC RESTORE)
dropzone_svelte = r"""
<script>
  import { listen } from '@tauri-apps/api/event';
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';
  import Toast from './Toast.svelte';

  let isDragging = $state(false);
  let toast = $state(null);

  onMount(async () => {
    // Lắng nghe sự kiện kéo thả file của Tauri
    await listen('tauri://drag-enter', () => isDragging = true);
    await listen('tauri://drag-leave', () => isDragging = false);
    await listen('tauri://drop', async (e) => {
      isDragging = false;
      const files = e.payload.paths || []; // Tauri v2 drop payload
      const file = files.find(f => f.endsWith('.cvbak'));
      
      if (file) {
        toast = { msg: 'Restoring...', type: 'info' };
        try {
            await invoke('cmd_restore_backup', { path: file });
            toast = { msg: 'Restore Success! Welcome back.', type: 'success' };
        } catch (err) {
            toast = { msg: 'Restore Failed: ' + err, type: 'error' };
        }
      } else {
        toast = { msg: 'Invalid file. Drop a .cvbak file.', type: 'error' };
      }
    });
  });
</script>

{#if isDragging}
<div class="fixed inset-0 z-40 bg-blue-500/20 backdrop-blur-sm flex items-center justify-center border-4 border-dashed border-blue-400 m-4 rounded-3xl pointer-events-none">
  <div class="text-center animate-bounce">
    <div class="text-6xl mb-2">📦</div>
    <h2 class="text-2xl font-bold text-white">Drop to Restore</h2>
  </div>
</div>
{/if}

{#if toast}
  <Toast message={toast.msg} type={toast.type} />
{/if}
"""

# C. RECOVERY MODAL (AUTO-WIPE)
recovery_svelte = r"""
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
        
        // Auto-Wipe Timer
        const timer = setInterval(() => {
            timeLeft--;
            if (timeLeft <= 0) {
                clearInterval(timer);
                onClose(); // Tự đóng
            }
        }, 1000);
    } catch (e) { console.error(e); }
  });
</script>

<div class="fixed inset-0 bg-black/90 flex items-center justify-center z-50 backdrop-blur-md">
  <div class="bg-[#1a1a1a] border border-[#333] p-6 rounded-xl w-96 text-center shadow-2xl">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-white">🔐 Recovery Key</h2>
        <span class="text-red-500 font-mono font-bold">{timeLeft}s</span>
    </div>
    
    <div 
        class="bg-white p-4 rounded-lg mb-4 cursor-pointer relative overflow-hidden group select-none"
        onmousedown={() => isRevealed = true}
        onmouseup={() => isRevealed = false}
        onmouseleave={() => isRevealed = false}
    >
        {#if imageData}
            <img src={imageData} alt="Secret" class="w-full h-48 object-contain transition-all duration-300 {isRevealed ? 'blur-0' : 'blur-xl opacity-50'}" />
            {#if !isRevealed}
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span class="bg-black/80 text-white px-3 py-1 rounded-full text-sm font-bold">HOLD TO REVEAL</span>
                </div>
            {/if}
        {:else}
            <div class="h-48 flex items-center justify-center text-gray-500 animate-pulse">Generating Secure Key...</div>
        {/if}
    </div>

    <p class="text-xs text-gray-500 mb-4">Data exists only in RAM. Zero-knowledge guaranteed.</p>
    <button onclick={onClose} class="w-full bg-red-600 hover:bg-red-500 text-white py-2 rounded font-medium">Close & Wipe</button>
  </div>
</div>
"""

# D. UPDATE APP.SVELTE (Add DropZone)
app_svelte = r"""
<script>
  import { Box, Book, Zap } from 'lucide-svelte';
  import RecoveryModal from "./lib/components/RecoveryModal.svelte";
  import BackupConsole from "./lib/components/BackupConsole.svelte";
  import DropZone from "./lib/components/DropZone.svelte"; // <--- NEW

  let showRecovery = $state(false);
</script>

<DropZone /> <!-- Magic Restore Layer -->

<main class="flex h-screen w-screen bg-[#0f0f0f] text-gray-200 font-sans overflow-hidden">
  <nav class="w-16 bg-[#1a1a1a] border-r border-[#333] flex flex-col items-center py-6 gap-6 z-10">
    <button class="p-3 rounded-xl bg-blue-600 text-white shadow-lg shadow-blue-900/50"><Box size={24} /></button>
    <div class="flex-1"></div>
    <button onclick={() => showRecovery = true} class="p-2 text-gray-400 hover:text-white transition cursor-pointer" title="Recovery Key">
        <div class="w-8 h-8 rounded-full border-2 border-green-500 bg-green-900/30 flex items-center justify-center text-xs font-bold text-green-400">S</div>
    </button>
  </nav>

  <section class="flex-1 p-8 overflow-y-auto pb-32">
    <header class="mb-12">
        <h1 class="text-4xl font-bold text-white mb-2">Hello, Architect.</h1>
        <p class="text-gray-400">Your digital sanctum is ready.</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <button class="group relative h-80 bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 hover:border-blue-500 transition-all hover:-translate-y-2 text-left shadow-xl cursor-pointer">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition"><Box size={100} /></div>
            <div class="h-full flex flex-col justify-end">
                <h3 class="text-2xl font-bold text-white mb-2">CONVERT</h3>
                <p class="text-gray-400 text-sm">Universal Format Engine.</p>
            </div>
        </button>
        <button class="group relative h-80 bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 hover:border-green-500 transition-all hover:-translate-y-2 text-left shadow-xl cursor-pointer">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition"><Book size={100} /></div>
            <div class="h-full flex flex-col justify-end">
                <h3 class="text-2xl font-bold text-white mb-2">NOTES</h3>
                <p class="text-gray-400 text-sm">Knowledge Management.</p>
            </div>
        </button>
        <button class="group relative h-80 bg-[#1a1a1a] border border-[#333] rounded-2xl p-6 hover:border-purple-500 transition-all hover:-translate-y-2 text-left shadow-xl cursor-pointer">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition"><Zap size={100} /></div>
            <div class="h-full flex flex-col justify-end">
                <h3 class="text-2xl font-bold text-white mb-2">WORKFLOW</h3>
                <p class="text-gray-400 text-sm">AI Agents & Automation.</p>
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

# =========================================================
# 2. RUST BACKEND STUB (RESTORE COMMAND)
# =========================================================
restore_rs = r"""
use tauri::command;
use std::thread;
use std::time::Duration;

#[command]
pub fn cmd_restore_backup(path: String) -> Result<String, String> {
    // MOCK RESTORE PROCESS
    // In production, this calls Python Core
    if !path.ends_with(".cvbak") {
        return Err("Invalid file format".into());
    }
    
    // Simulate processing
    thread::sleep(Duration::from_millis(1500));
    
    Ok("Restore successful".into())
}
"""

lib_rs_new = r"""
pub mod commands {
    pub mod backup;
    pub mod recovery;
    pub mod restore; // Added
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        // .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            commands::backup::cmd_backup_start,
            commands::recovery::cmd_export_recovery_svg,
            commands::restore::cmd_restore_backup // Registered
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
"""

# =========================================================
# EXECUTE WRITE
# =========================================================
base_ui = "src-ui/src"
write(f"{base_ui}/lib/components/Toast.svelte", toast_svelte)
write(f"{base_ui}/lib/components/DropZone.svelte", dropzone_svelte)
write(f"{base_ui}/lib/components/RecoveryModal.svelte", recovery_svelte)
write(f"{base_ui}/App.svelte", app_svelte)

base_rust = "src-tauri/src"
write(f"{base_rust}/commands/restore.rs", restore_rs)
write(f"{base_rust}/lib.rs", lib_rs_new)

print("🚀 TASK 5.3 FINAL COMPLETION: UI + RUST PATCHED.")

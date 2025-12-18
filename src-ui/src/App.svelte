<script>
  import { onMount } from "svelte";
  import { open } from "@tauri-apps/plugin-dialog";
  import { invoke } from "@tauri-apps/api/core";
  import { listen } from "@tauri-apps/api/event";

  import RecoveryModal from "./lib/components/RecoveryModal.svelte";
  import BackupConsole from "./lib/components/BackupConsole.svelte";
  import DropZone from "./lib/components/DropZone.svelte";
  import Toast from "./lib/components/Toast.svelte";

  import { useToast } from "./lib/stores/toast.svelte.js";
  import { Box, Book, Zap, Moon, Sun, FolderOpen } from "lucide-svelte";

  // State
  let showRecovery = $state(false);
  let isDarkMode = $state(false);
  const toast = useToast();

  // Theme
  function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    updateTheme();
  }

  function updateTheme() {
    const html = document.documentElement;
    if (isDarkMode) {
      html.setAttribute("data-theme", "dark");
    } else {
      html.removeAttribute("data-theme");
    }
  }

  // Fallback: Open file picker
  async function openBackupFile() {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: "Convert Backup", extensions: ["cvbak"] }],
      });

      if (selected) {
        toast.add(`Processing: ${selected}`, "info");

        // CRITICAL FIX: Use 'filePath' (camelCase) to match Tauri v2 convention
        const res = await invoke("cmd_restore_from_file", {
          filePath: selected,
        });
        console.log("✅ Backup loaded:", res);
        toast.add("Backup loaded successfully!", "success");
        showRecovery = true;
      }
    } catch (err) {
      console.error("❌ File picker error:", err);
      toast.add(`Error opening file: ${err}`, "error");
    }
  }

  onMount(async () => {
    // Theme
    const storedTheme = localStorage.getItem("theme");
    isDarkMode = storedTheme
      ? storedTheme === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;
    updateTheme();

    // Welcome
    toast.add("Convert Protocol Ready. Drop .cvbak or use Open File.", "info");

    // Listen for custom "file-uploaded" event from Rust (Manual bridge)
    const unlistenUploaded = await listen("file-uploaded", async (event) => {
      console.log("🚀 [App.svelte] Custom file-uploaded event:", event.payload);
      const paths = event.payload;
      if (paths && paths.length > 0) {
          const filePath = paths[0];
          if (filePath.endsWith(".cvbak")) {
             toast.add(`🚀 Received: ${filePath.split("\\").pop()}`, "info");
             // Trigger restore logic
             try {
                const res = await invoke("cmd_restore_from_file", { filePath: filePath });
                console.log("✅ Restore result:", res);
                toast.add("Backup loaded!", "success");
                showRecovery = true;
             } catch (err) {
                console.error("❌ Restore error:", err);
                toast.add(`Restore failed: ${err}`, "error");
             }
          } else {
             toast.add("Ignored non-.cvbak file", "warning");
          }
      }
    });

    // Direct Tauri event listener as backup (in case DropZone fails)
    try {
      await listen("tauri://file-drop", async (event) => {
        console.log("🔥 [App.svelte] File dropped:", event.payload);
        const filePath = event.payload?.[0];

        if (filePath && filePath.endsWith(".cvbak")) {
          toast.add(`File detected: ${filePath.split("\\").pop()}`, "info");

          try {
            // CRITICAL FIX: Use 'filePath' (camelCase) here too
            const res = await invoke("cmd_restore_from_file", {
              filePath: filePath,
            });
            console.log("✅ Restore result:", res);
            toast.add("Backup loaded!", "success");
            showRecovery = true;
          } catch (err) {
            console.error("❌ Restore error:", err);
            toast.add(`Restore failed: ${err}`, "error");
          }
        } else if (filePath) {
          toast.add("Only .cvbak files are supported", "error");
        }
      });
      console.log("✅ [App.svelte] Direct drop listener registered");
    } catch (err) {
      console.warn("⚠️ Direct drop listener failed:", err);
    }

    // Listen for backup-loaded event from DropZone
    window.addEventListener("backup-loaded", (e) => {
      console.log("📦 Backup loaded event:", e.detail);
      showRecovery = true;
      toast.add("Recovery Interface Activated", "success");
    });
  });
</script>

<!-- DropZone -->
<DropZone />

<!-- Toast Container -->
<div class="toast-container">
  {#each toast.all as item (item.id)}
    <Toast message={item.message} type={item.type} />
  {/each}
</div>

<!-- Main UI -->
<main class="app-layout">
  <button class="theme-btn" onclick={toggleTheme} title="Toggle theme">
    {#if isDarkMode}
      <Sun size={20} />
    {:else}
      <Moon size={20} />
    {/if}
  </button>

  <nav class="sidebar">
    <div class="logo-icon">
      <Box size={24} />
    </div>
    <div class="spacer"></div>
    <button
      class="nav-btn secure"
      onclick={() => (showRecovery = true)}
      title="Recovery"
    >
      S
    </button>
  </nav>

  <section class="content-area">
    <header class="hero-header">
      <div class="badge">SPRINT 5 READY</div>
      <h1>Hello, Architect.</h1>
      <p>
        <span>Drop your <code>.cvbak</code> file anywhere</span>
        <span class="or-separator">or</span>
      </p>
      <button class="open-file-btn" onclick={openBackupFile}>
        <FolderOpen size={18} />
        Open Backup File
      </button>
    </header>

    <div class="card-grid">
      <button class="feature-card blue">
        <div class="card-bg-icon"><Box size={120} /></div>
        <div class="card-body">
          <div class="icon-circle"><Box size={24} /></div>
          <h3>CONVERT</h3>
          <p>Universal Format Engine</p>
        </div>
      </button>

      <button class="feature-card green">
        <div class="card-bg-icon"><Book size={120} /></div>
        <div class="card-body">
          <div class="icon-circle"><Book size={24} /></div>
          <h3>NOTES</h3>
          <p>Secure Knowledge Vault</p>
        </div>
      </button>

      <button class="feature-card purple">
        <div class="card-bg-icon"><Zap size={120} /></div>
        <div class="card-body">
          <div class="icon-circle"><Zap size={24} /></div>
          <h3>WORKFLOW</h3>
          <p>AI Agent Orchestration</p>
        </div>
      </button>
    </div>
  </section>

  {#if showRecovery}
    <RecoveryModal onClose={() => (showRecovery = false)} />
  {/if}

  <BackupConsole />
</main>

<style>
  .app-layout {
    display: flex;
    height: 100vh;
    width: 100vw;
    background: var(--bg-app);
    color: var(--text-main);
    font-family: "Inter", system-ui, sans-serif;
    position: relative;
  }

  .toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    gap: 12px;
    pointer-events: none;
  }

  .sidebar {
    width: 80px;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-glass);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px 0;
    backdrop-filter: blur(20px);
  }

  .logo-icon {
    width: 40px;
    height: 40px;
    background: var(--accent-blue);
    border-radius: 10px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 40px;
  }

  .nav-btn.secure {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 2px solid var(--accent-green);
    color: var(--accent-green);
    background: transparent;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 20px;
  }

  .spacer {
    flex: 1;
  }

  .content-area {
    flex: 1;
    padding: 48px;
    overflow-y: auto;
  }

  .hero-header {
    margin-bottom: 48px;
  }

  .badge {
    display: inline-block;
    padding: 6px 16px;
    background: var(--btn-hover);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent-blue);
    margin-bottom: 16px;
    border: 1px solid var(--border-glass);
  }

  .hero-header h1 {
    font-size: 48px;
    font-weight: 800;
    margin: 0 0 12px 0;
  }

  .hero-header p {
    font-size: 18px;
    color: var(--text-sub);
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .or-separator {
    color: var(--text-sub);
    font-size: 14px;
  }

  code {
    background: var(--bg-card);
    padding: 4px 8px;
    border-radius: 4px;
    font-family: "Monaco", monospace;
    font-size: 16px;
    color: var(--accent-blue);
  }

  .open-file-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: var(--accent-blue);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
    transition: all 0.2s;
  }

  .open-file-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 113, 227, 0.4);
  }

  .card-grid {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
  }

  .feature-card {
    flex: 1;
    min-width: 280px;
    height: 320px;
    border-radius: 24px;
    border: 1px solid var(--border-glass);
    background: var(--bg-card);
    position: relative;
    overflow: hidden;
    cursor: pointer;
    padding: 32px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-card);
  }

  .feature-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-hover);
  }

  .card-bg-icon {
    position: absolute;
    top: -20px;
    right: -20px;
    opacity: 0.05;
    transform: rotate(15deg);
    transition: all 0.5s;
    color: var(--text-main);
  }

  .feature-card:hover .card-bg-icon {
    transform: rotate(0deg) scale(1.1);
    opacity: 0.1;
  }

  .icon-circle {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: var(--bg-app);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    box-shadow: var(--shadow-card);
  }

  .card-body h3 {
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: var(--text-main);
  }

  .card-body p {
    font-size: 14px;
    color: var(--text-sub);
    margin: 0;
  }

  .feature-card.blue {
    color: var(--accent-blue);
  }
  .feature-card.blue .icon-circle {
    color: var(--accent-blue);
  }
  .feature-card.blue:hover {
    border-color: var(--accent-blue);
  }

  .feature-card.green {
    color: var(--accent-green);
  }
  .feature-card.green .icon-circle {
    color: var(--accent-green);
  }
  .feature-card.green:hover {
    border-color: var(--accent-green);
  }

  .feature-card.purple {
    color: var(--accent-purple);
  }
  .feature-card.purple .icon-circle {
    color: var(--accent-purple);
  }
  .feature-card.purple:hover {
    border-color: var(--accent-purple);
  }

  .theme-btn {
    position: absolute;
    top: 24px;
    right: 24px;
    z-index: 100;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 1px solid var(--border-glass);
    background: var(--bg-card);
    color: var(--text-main);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-card);
    transition: transform 0.2s;
  }

  .theme-btn:hover {
    transform: scale(1.1);
  }
</style>

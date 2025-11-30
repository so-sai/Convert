<script>
  import { onMount } from 'svelte';
  
  let status = 'Loading...';
  
  onMount(async () => {
    try {
      if (window.__TAURI__) {
        const { invoke } = await import('@tauri-apps/api/core');
        // Note: We are calling 'export_recovery_qr' which is the command we registered in lib.rs
        // But for initial test, let's just show connection status.
        // If we want to test the command, we need to pass arguments.
        status = '✅ Frontend Ready (Svelte 5 + Tauri v2)';
      } else {
        status = '⚠️ Running in browser mode';
      }
    } catch (error) {
      status = '❌ Error: ' + error;
    }
  });
</script>

<div style="padding: 20px; font-family: sans-serif;">
  <h1>🛡️ Convert Vault</h1>
  <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 10px 0;">
    <p>{status}</p>
  </div>
  <p>Frontend is running with Svelte 5 + Tauri v2</p>
</div>
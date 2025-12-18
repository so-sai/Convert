<script>
    import { onMount, onDestroy } from "svelte";
    import { listen } from "@tauri-apps/api/event";
    import { invoke } from "@tauri-apps/api/core";
    import { useToast } from "../stores/toast.svelte.js";
    import { FileUp, Loader } from "lucide-svelte";

    const toast = useToast();
    let isDragging = $state(false);
    let isProcessing = $state(false);
    let unlistenFunctions = [];

    onMount(async () => {
        try {
            // Listen for Tauri drag-drop events
            const unlistenHover = await listen(
                "tauri://file-drop-hover",
                () => {
                    console.log("📁 File hover detected");
                    isDragging = true;
                },
            );

            const unlistenDrop = await listen(
                "tauri://file-drop",
                async (event) => {
                    console.log("📁 File dropped:", event.payload);
                    isDragging = false;
                    const files = event.payload;

                    if (!files || files.length === 0) {
                        console.log("No files dropped");
                        return;
                    }

                    const path = files[0];
                    if (!path.endsWith(".cvbak")) {
                        toast.add(
                            "❌ Only .cvbak files are supported",
                            "error",
                        );
                        return;
                    }

                    await processFile(path);
                },
            );

            const unlistenCancel = await listen(
                "tauri://file-drop-cancelled",
                () => {
                    console.log("📁 Drag cancelled");
                    isDragging = false;
                },
            );

            unlistenFunctions = [unlistenHover, unlistenDrop, unlistenCancel];
            console.log("✅ DropZone listening for drag-drop events");
        } catch (error) {
            console.error("❌ Failed to setup drag-drop:", error);
            toast.add(
                "⚠️ Drag-drop unavailable. Use Open File button.",
                "error",
            );
        }
    });

    onDestroy(() => {
        unlistenFunctions.forEach((fn) => fn && fn());
    });

    async function processFile(path) {
        isProcessing = true;
        try {
            console.log("🔄 Processing file:", path);
            toast.add(`Processing: ${path.split("\\").pop()}`, "info");

            const result = await invoke("cmd_restore_from_file", {
                filePath: path,
            });

            console.log("✅ Backup processed:", result);

            // Dispatch event to App.svelte
            window.dispatchEvent(
                new CustomEvent("backup-loaded", {
                    detail: result,
                }),
            );

            toast.add("✅ Backup loaded successfully!", "success");
        } catch (error) {
            console.error("❌ Error processing file:", error);
            toast.add(`❌ Failed: ${error}`, "error");
        } finally {
            isProcessing = false;
        }
    }
</script>

{#if isDragging || isProcessing}
    <div class="drop-overlay">
        <div class="drop-content">
            {#if isProcessing}
                <Loader size={64} class="spin" />
                <h2>Processing backup...</h2>
                <p>Please wait</p>
            {:else}
                <FileUp size={64} class="pulse" />
                <h2>Drop to restore</h2>
                <p>Release .cvbak file to load backup</p>
            {/if}
        </div>
    </div>
{/if}

<style>
    .drop-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(10px);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        pointer-events: none;
        animation: fadeIn 0.2s ease;
    }

    .drop-content {
        text-align: center;
        padding: 48px;
        border: 3px dashed rgba(255, 255, 255, 0.3);
        border-radius: 32px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        max-width: 400px;
    }

    h2 {
        font-size: 28px;
        margin: 24px 0 12px 0;
        font-weight: 700;
    }

    p {
        color: rgba(255, 255, 255, 0.7);
        margin: 0;
        font-size: 16px;
    }

    :global(.spin) {
        animation: spin 1s linear infinite;
    }

    :global(.pulse) {
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    @keyframes pulse {
        0%,
        100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.8;
        }
    }
</style>

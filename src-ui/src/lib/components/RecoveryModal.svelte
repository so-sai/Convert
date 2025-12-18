<script>
    import { onMount } from "svelte";
    import { X } from "lucide-svelte";
    import { invoke } from "@tauri-apps/api/core";

    let { onClose } = $props();

    let isBlurred = $state(true);
    let recoveryKey = $state("");
    let timeLeft = $state(60);
    let timer;

    function reveal() {
        isBlurred = false;
    }
    function hide() {
        isBlurred = true;
    }

    onMount(async () => {
        try {
            // Mock key retrieval - in real app invoke rust command
            // const key = await invoke('cmd_get_recovery_key');
            recoveryKey = "MOCK-RECOVERY-KEY-1234-5678-ABCD-EFGH";

            timer = setInterval(() => {
                timeLeft--;
                if (timeLeft <= 0) {
                    clearInterval(timer);
                    onClose();
                }
            }, 1000);
        } catch (e) {
            console.error(e);
        }

        return () => clearInterval(timer);
    });
</script>

<div class="modal-overlay">
    <div class="modal-card">
        <button class="close-btn" onclick={onClose}><X size={20} /></button>

        <div class="header">
            <h3>Recovery Key</h3>
            <p>Blind Protocol Active. Hold to Reveal.</p>
        </div>

        <div
            class="key-container"
            onmousedown={reveal}
            onmouseup={hide}
            onmouseleave={hide}
            role="button"
            tabindex="0"
        >
            <div class="key-content" class:blurred={isBlurred}>
                {recoveryKey}
                <div class="qr-placeholder">
                    <!-- QR Code Placeholder -->
                    <svg width="100" height="100" viewBox="0 0 100 100">
                        <rect width="100" height="100" fill="white" />
                        <rect
                            x="20"
                            y="20"
                            width="60"
                            height="60"
                            fill="black"
                        />
                    </svg>
                </div>
            </div>

            {#if isBlurred}
                <div class="overlay-text">HOLD TO REVEAL</div>
            {/if}
        </div>

        <div class="footer">
            <span class="timer">Auto-wipe in {timeLeft}s</span>
        </div>
    </div>
</div>

<style>
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9995; /* Below DropZone (9999) */
    }

    .modal-card {
        background: var(--bg-card);
        backdrop-filter: blur(24px);
        border: 1px solid var(--border-glass);
        padding: 32px;
        border-radius: 24px;
        width: 360px;
        text-align: center;
        box-shadow: var(--shadow-hover);
        position: relative;
        color: var(--text-main);
    }

    .close-btn {
        position: absolute;
        top: 16px;
        right: 16px;
        background: none;
        border: none;
        color: var(--text-sub);
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        transition: all 0.2s;
    }
    .close-btn:hover {
        background: rgba(125, 125, 125, 0.1);
        color: var(--text-main);
    }

    .header h3 {
        margin: 0 0 8px 0;
        font-size: 1.25rem;
        font-weight: 700;
    }
    .header p {
        margin: 0 0 24px 0;
        color: var(--text-sub);
        font-size: 0.85rem;
    }

    .key-container {
        background: rgba(125, 125, 125, 0.1);
        border-radius: 16px;
        padding: 20px;
        position: relative;
        cursor: pointer;
        overflow: hidden;
        user-select: none;
        border: 1px solid var(--border-glass);
        transition: transform 0.1s;
    }
    .key-container:active {
        transform: scale(0.98);
    }

    .key-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        font-family: monospace;
        font-size: 1.1rem;
        font-weight: 600;
        transition: filter 0.2s;
    }
    .blurred {
        filter: blur(16px);
        opacity: 0.5;
    }

    .overlay-text {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        color: var(--accent-blue);
        letter-spacing: 1px;
        font-size: 0.9rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        pointer-events: none;
    }

    .qr-placeholder {
        background: white;
        padding: 10px;
        border-radius: 8px;
    }

    .footer {
        margin-top: 24px;
    }
    .timer {
        color: #ef4444;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(239, 68, 68, 0.1);
        padding: 6px 12px;
        border-radius: 99px;
    }
</style>

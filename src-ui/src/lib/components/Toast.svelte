<script>
    import { onMount } from "svelte";
    let { message, type = "info", duration = 3000 } = $props();
    let visible = $state(true);

    onMount(() => {
        const timer = setTimeout(() => (visible = false), duration);
        return () => clearTimeout(timer);
    });
</script>

{#if visible}
    <div
        class="toast-container"
        class:success={type === "success"}
        class:error={type === "error"}
    >
        <div class="icon">
            {#if type === "success"}✅{:else if type === "error"}❌{:else}ℹ️{/if}
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
        border-radius: 9999px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        background: rgba(30, 30, 30, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .message {
        color: white;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    .icon {
        font-size: 18px;
    }

    @keyframes slideDown {
        from {
            transform: translate(-50%, -100%);
            opacity: 0;
        }
        to {
            transform: translate(-50%, 0);
            opacity: 1;
        }
    }
</style>

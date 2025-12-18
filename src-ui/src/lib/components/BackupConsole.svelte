<script>
    import { backupState } from "../stores/backup.svelte.js";
</script>

<div class="console-dock">
    {#if backupState.phase === "idle"}
        <div class="console-idle">
            <span class="status-text">System Ready. Encrypted Database V2.</span
            >
            <button onclick={() => backupState.start()} class="btn-backup">
                <span class="btn-icon">⬆</span>
                BACKUP NOW
            </button>
        </div>
    {:else}
        <div class="console-active">
            <div class="meta-row">
                <span class="phase-label"
                    >PHASE: {backupState.phase.toUpperCase()}</span
                >
                <span class="stats"
                    >SPEED: {backupState.speed} | ETA: {backupState.eta}</span
                >
            </div>

            <div class="progress-track">
                <div
                    class="progress-bar"
                    style="width: {backupState.progress}%"
                ></div>
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
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-sidebar);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border-top: 1px solid var(--border-glass);
        padding: 16px 28px;
        z-index: 100;
        font-family: inherit;
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.1);
        transition: background 0.3s ease;
    }

    .console-idle {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }

    .status-text {
        color: var(--text-sub);
        font-size: 13px;
        letter-spacing: 0.3px;
    }

    .btn-backup {
        background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: inherit;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 14px rgba(0, 113, 227, 0.35);
    }
    .btn-backup:hover {
        background: linear-gradient(135deg, #1a8aff 0%, #5ab0f5 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 113, 227, 0.5);
    }
    .btn-backup:active {
        transform: translateY(0) scale(0.98);
    }

    .btn-icon {
        font-size: 16px;
    }

    .console-active {
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .meta-row {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .phase-label {
        color: var(--accent-blue);
        font-weight: 600;
    }
    .stats {
        color: var(--text-sub);
    }

    .progress-track {
        width: 100%;
        height: 8px;
        background: rgba(125, 125, 125, 0.2);
        border-radius: 99px;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #0071e3 0%, #42a5f5 100%);
        border-radius: 99px;
        transition: width 0.3s ease-out;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .message {
        color: var(--text-main);
        font-size: 13px;
        opacity: 0.8;
    }
    .percent {
        color: var(--accent-blue);
        font-weight: 700;
        font-size: 14px;
    }
</style>

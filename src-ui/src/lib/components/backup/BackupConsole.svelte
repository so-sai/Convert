<script>
  import { backupStore } from "../../stores/backup.ts";

  // Use reactive derivations
  $: phase = $backupStore.phase;
  $: progress = $backupStore.progress;
  $: eta = $backupStore.eta || "--";
</script>

<div class="backup-console">
  <div class="backup-console__header">
    <h2 class="backup-console__title">Secure Backup</h2>
    <span class="backup-console__status">{phase}</span>
  </div>

  <div class="backup-console__progress">
    <div class="backup-console__progress-track">
      <div class="backup-console__progress-fill" style="width: {progress}%" />
    </div>
    <div class="backup-console__stats">
      <span>{progress.toFixed(0)}% complete</span>
      <span>ETA: {eta}</span>
    </div>
  </div>

  <!-- Action Button for interaction -->
  <div class="backup-console__actions">
    <button
      on:click={() => backupStore.start()}
      disabled={phase !== "idle" && phase !== "done" && phase !== "error"}
      class="action-btn"
    >
      {phase === "idle"
        ? "Start Backup"
        : phase === "done"
          ? "Done"
          : phase === "error"
            ? "Retry"
            : "Processing..."}
    </button>
  </div>
</div>

<style>
  .backup-console {
    /* === GLASSMORPHISM (Big Sur Vibrancy) === */
    backdrop-filter: blur(20px) saturate(180%);
    background: rgba(255, 255, 255, 0.6);

    /* === SHAPE (Squircle) === */
    border-radius: 20px;

    /* === SHADOW (Soft, Diffused) === */
    box-shadow:
      0 4px 8px rgba(0, 0, 0, 0.06),
      0 12px 24px rgba(0, 0, 0, 0.1),
      0 0 1px rgba(0, 0, 0, 0.12);

    /* === BORDER (Subtle Definition) === */
    border: 1px solid rgba(255, 255, 255, 0.3);

    /* === SPACING === */
    padding: 24px;
    width: 100%;
    max-width: 480px;
    margin: 0 auto;
    box-sizing: border-box;

    /* === ANIMATION === */
    transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .backup-console:hover {
    transform: translateY(-2px);
    box-shadow:
      0 8px 16px rgba(0, 0, 0, 0.08),
      0 20px 40px rgba(0, 0, 0, 0.12),
      0 0 1px rgba(0, 0, 0, 0.15);
  }

  .backup-console__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .backup-console__title {
    font-size: 20px;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }

  .backup-console__status {
    font-size: 13px;
    font-weight: 500;
    color: var(--color-text-secondary);
    text-transform: capitalize;
  }

  .backup-console__progress-track {
    height: 6px;
    background: rgba(0, 0, 0, 0.06);
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 8px;
  }

  .backup-console__progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #007aff, #5ac8fa);
    border-radius: 9999px;
    transition: width 250ms cubic-bezier(0, 0, 0.2, 1);
  }

  .backup-console__stats {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--color-text-secondary);
  }

  .backup-console__actions {
    margin-top: 24px;
  }

  .action-btn {
    width: 100%;
    padding: 12px;
    background: var(--color-action);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .action-btn:hover {
    opacity: 0.9;
  }

  .action-btn:disabled {
    background: var(--color-text-secondary);
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* === DARK MODE === */
  @media (prefers-color-scheme: dark) {
    .backup-console {
      backdrop-filter: blur(20px) saturate(180%);
      background: rgba(28, 28, 30, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.15);
    }

    .backup-console__progress-track {
      background: rgba(255, 255, 255, 0.1);
    }
  }
</style>

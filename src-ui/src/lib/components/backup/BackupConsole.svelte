<script>
  import { backupStore } from "../../stores/backup";

  // Use reactive derivations
  $: phase = $backupStore.phase;
  $: progress = $backupStore.progress;
  $: eta = $backupStore.eta || "--";
</script>

<div class="backup-console glass-panel">
  <div class="backup-console__header">
    <h2 class="backup-console__title">Secure Backup</h2>
    <span class="backup-console__status">{phase}</span>
  </div>

  <div class="backup-console__progress">
    <div class="backup-console__progress-track">
      <div
        class="backup-console__progress-fill"
        style="width: {progress}%"
      ></div>
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
    /* === V3 REFINEMENT: ENHANCED GLASS === */
    backdrop-filter: blur(50px) saturate(180%);
    -webkit-backdrop-filter: blur(50px) saturate(180%);
    background-color: rgba(255, 255, 255, 0.45); /* Increased transparency */

    /* === SHAPE === */
    border-radius: 20px;

    /* === SHADOW & BORDER === */
    box-shadow:
      0 25px 50px -12px rgba(0, 0, 0, 0.05),
      0 0 0 1px rgba(255, 255, 255, 0.3) inset;
    border: 1px solid rgba(255, 255, 255, 0.5);

    /* === SPACING === */
    padding: 40px; /* Increased padding (p-10) */
    width: 100%;
    max-width: 480px;
    margin: 0 auto;
    box-sizing: border-box;

    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .backup-console:hover {
    transform: translateY(-2px);
    box-shadow:
      0 30px 60px -12px rgba(0, 0, 0, 0.08),
      0 0 0 1px rgba(255, 255, 255, 0.4) inset;
  }

  .backup-console__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }

  .backup-console__title {
    font-size: 36px; /* Increased size (text-4xl) */
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.1;
  }

  .backup-console__status {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary);
    text-transform: capitalize;
    background: rgba(0, 0, 0, 0.04);
    padding: 6px 12px;
    border-radius: 20px;
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
    background: linear-gradient(90deg, #0071e3, #34c759);
    border-radius: 9999px;
    transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .backup-console__stats {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--color-text-secondary);
    font-weight: 500;
  }

  .backup-console__actions {
    margin-top: 32px;
  }

  .action-btn {
    width: 100%;
    padding: 14px;
    /* Apple Modern Blue */
    background: linear-gradient(to bottom, #0077ed, #0071e3);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    box-shadow:
      0 4px 14px rgba(0, 113, 227, 0.25),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .action-btn:hover {
    background: #0077ed;
    transform: translateY(-1px);
    box-shadow:
      0 6px 20px rgba(0, 113, 227, 0.35),
      0 0 0 1px rgba(255, 255, 255, 0.15) inset;
  }

  .action-btn:active {
    transform: translateY(0);
    box-shadow:
      0 2px 8px rgba(0, 113, 227, 0.2),
      0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  }

  .action-btn:disabled {
    background: var(--color-text-secondary);
    opacity: 0.5;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }

  /* === DARK MODE === */
  @media (prefers-color-scheme: dark) {
    .backup-console {
      background-color: rgba(20, 20, 20, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .backup-console__status {
      background: rgba(255, 255, 255, 0.1);
    }

    .backup-console__progress-track {
      background: rgba(255, 255, 255, 0.1);
    }
  }
</style>

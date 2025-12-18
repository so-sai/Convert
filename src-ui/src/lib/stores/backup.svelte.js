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

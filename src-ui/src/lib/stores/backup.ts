// Omega Backup Store - Hybrid Command-Event Pattern (ADR-008)
import { writable, get } from 'svelte/store';
import { invoke } from '@tauri-apps/api/core';
import { listen, type UnlistenFn } from '@tauri-apps/api/event';
import type { BackupPayload } from '../types/ipc';

interface BackupState {
    isProcessing: boolean;
    progress: number;
    phase: string;
    speed: string;
    eta: string;
    message: string;
    taskId: string | null;
    error: string | null;
}

const initialState: BackupState = {
    isProcessing: false,
    progress: 0,
    phase: 'idle',
    speed: '',
    eta: '',
    message: '',
    taskId: null,
    error: null
};

function createBackupStore() {
    const { subscribe, set, update } = writable<BackupState>(initialState);
    let unlisten: UnlistenFn | null = null;

    return {
        subscribe,

        // Start backup - Hybrid Flow
        start: async (targetDir?: string) => {
            // Reset state
            set({
                ...initialState,
                isProcessing: true,
                phase: 'init',
                message: 'Starting Omega Engine...'
            });

            try {
                // COMMAND: Get TaskID immediately (no blocking)
                const taskId = await invoke<string>('cmd_backup_start', {
                    targetDir: targetDir || null
                });

                update(s => ({ ...s, taskId }));

                // EVENT: Listen to progress stream
                if (unlisten) unlisten();

                unlisten = await listen<BackupPayload>('backup_progress', (event) => {
                    const payload = event.payload;

                    // Filter: Only process our task
                    if (payload.task_id !== get({ subscribe }).taskId) return;

                    update(s => ({
                        ...s,
                        progress: payload.progress,
                        phase: payload.phase,
                        speed: payload.speed,
                        eta: payload.eta,
                        message: payload.msg,
                        error: payload.phase === 'error' ? payload.msg : null, // msg contains error when phase is 'error'
                        isProcessing: payload.phase !== 'done' && payload.phase !== 'error'
                    }));

                    // Cleanup listener when done
                    if (payload.phase === 'done' || payload.phase === 'error') {
                        if (unlisten) {
                            unlisten();
                            unlisten = null;
                        }
                    }
                });

            } catch (err) {
                set({
                    ...initialState,
                    phase: 'error',
                    error: String(err),
                    message: 'Failed to start backup'
                });
            }
        },

        reset: () => {
            if (unlisten) {
                unlisten();
                unlisten = null;
            }
            set(initialState);
        }
    };
}

export const backupStore = createBackupStore();

// Blind Recovery Store - ADR-008 Compliant
import { writable } from 'svelte/store';
import { invoke } from '@tauri-apps/api/core';
import type { ExportResp } from '../types/ipc';

interface RecoveryState {
    isLoading: boolean;
    dataUri: string | null;
    ttlSeconds: number;
    remainingSeconds: number;
    error: string | null;
}

const initialState: RecoveryState = {
    isLoading: false,
    dataUri: null,
    ttlSeconds: 0,
    remainingSeconds: 0,
    error: null
};

function createRecoveryStore() {
    const { subscribe, set, update } = writable<RecoveryState>(initialState);
    let countdownInterval: ReturnType<typeof setInterval> | null = null;

    return {
        subscribe,

        // Export recovery SVG (Blind Protocol - no plaintext)
        export: async (auth: string) => {
            set({ ...initialState, isLoading: true });

            try {
                // BLIND PROTOCOL: Only receive SVG, never mnemonic
                const response = await invoke<ExportResp>('cmd_export_recovery_svg', { auth });

                set({
                    isLoading: false,
                    dataUri: response.data_uri,
                    ttlSeconds: response.ttl_seconds,
                    remainingSeconds: response.ttl_seconds,
                    error: null
                });

                // Start auto-wipe countdown
                if (countdownInterval) clearInterval(countdownInterval);

                countdownInterval = setInterval(() => {
                    update(s => {
                        const remaining = s.remainingSeconds - 1;
                        if (remaining <= 0) {
                            // AUTO-WIPE: Clear sensitive data
                            if (countdownInterval) clearInterval(countdownInterval);
                            return initialState;
                        }
                        return { ...s, remainingSeconds: remaining };
                    });
                }, 1000);

            } catch (err) {
                set({
                    ...initialState,
                    error: String(err)
                });
            }
        },

        // Manual clear (user finished viewing)
        clear: () => {
            if (countdownInterval) {
                clearInterval(countdownInterval);
                countdownInterval = null;
            }
            set(initialState);
        }
    };
}

export const recoveryStore = createRecoveryStore();

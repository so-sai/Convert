// Toast Store using Svelte 5 Runes
// Manages global toast notifications with auto-dismiss

export interface ToastItem {
    id: string;
    message: string;
    type: 'info' | 'success' | 'error';
}

let toasts = $state<ToastItem[]>([]);

export function useToast() {
    return {
        get all() {
            return toasts;
        },

        add: (message: string, type: 'info' | 'success' | 'error' = 'info', duration = 3000) => {
            const id = crypto.randomUUID();
            toasts.push({ id, message, type });

            // Auto-dismiss after duration
            setTimeout(() => {
                toasts = toasts.filter(t => t.id !== id);
            }, duration);
        },

        dismiss: (id: string) => {
            toasts = toasts.filter(t => t.id !== id);
        },

        clear: () => {
            toasts = [];
        }
    };
}

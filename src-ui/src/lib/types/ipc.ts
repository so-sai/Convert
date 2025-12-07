// IPC Type Contracts for Omega Protocol (ADR-008)

// Backup Progress Event (from Rust worker thread)
export interface BackupPayload {
    task_id: string;
    phase: 'init' | 'snapshot' | 'encrypting' | 'finalizing' | 'done' | 'error';
    progress: number;       // 0.0 - 100.0
    speed: string;          // "45 MB/s"
    eta: string;            // "10-15s" range
    msg: string;            // Error message when phase === 'error'
}

// Recovery SVG Response (Blind Protocol)
export interface ExportResp {
    data_uri: string;       // "data:image/svg+xml;base64,..."
    ttl_seconds: number;    // 60
}

// Command Result Types
export type BackupStartResult = string;  // TaskID
export type RecoveryResult = ExportResp;

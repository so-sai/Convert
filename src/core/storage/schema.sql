-- CONVERT VAULT SCHEMA v1 (Crypto-Trinity Ready)
-- Compatible with ADR-002 and ADR-003 (Rev 2)
-- Last Updated: 2025-11-23

CREATE TABLE IF NOT EXISTS system_keys (
    id TEXT PRIMARY KEY CHECK (id = 'main'),
    kdf_salt BLOB NOT NULL,       -- 16 bytes
    kdf_ops INTEGER NOT NULL,     -- 2
    kdf_mem INTEGER NOT NULL,     -- 19456 * 1024
    enc_dek BLOB NOT NULL,        -- Wrapped DEK (XChaCha20)
    dek_nonce BLOB NOT NULL,      -- 24 bytes
    epoch_status TEXT DEFAULT 'active',
    created_at INTEGER NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS domain_events (
    event_id TEXT PRIMARY KEY,
    stream_type TEXT NOT NULL CHECK(stream_type IN ('domain','interaction','memory')),
    stream_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    stream_sequence INTEGER NOT NULL,
    global_sequence INTEGER NOT NULL UNIQUE,
    timestamp INTEGER NOT NULL,
    
    -- CRYPTO TRINITY COLUMNS
    payload BLOB NOT NULL,        -- [Ciphertext || Poly1305_Tag]
    enc_algorithm TEXT DEFAULT 'XChaCha20-Poly1305',
    enc_key_id TEXT DEFAULT 'v1', -- Epoch ID (Derives DEK & HMAC Key)
    enc_nonce BLOB,               -- 24 bytes (NULL = Legacy Plaintext)
    
    -- INTEGRITY & ROLLBACK PROTECTION
    event_hmac BLOB NOT NULL,     -- HMAC-SHA3-256 of Plaintext (Raw Bytes)
    prev_event_hash BLOB,         -- SHA3-256 of Previous Event
    event_hash BLOB NOT NULL,     -- SHA3-256 Chain
    
    -- FORENSICS
    quarantine INTEGER DEFAULT 0, -- 0=OK, 1=Corrupt/Tampered
    tamper_reason TEXT,
    
    UNIQUE(stream_type, stream_id, stream_sequence)
) STRICT;

CREATE INDEX IF NOT EXISTS idx_events_stream ON domain_events(stream_type, stream_id);
-- Index for fast quarantine lookups
CREATE INDEX IF NOT EXISTS idx_quarantine ON domain_events(quarantine) WHERE quarantine = 1;

CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content BLOB NOT NULL,
    metadata BLOB NOT NULL,
    enc_algorithm TEXT NOT NULL DEFAULT 'pass-through',
    enc_key_id TEXT,
    enc_nonce BLOB,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted_at INTEGER,
    version INTEGER NOT NULL DEFAULT 1
) STRICT;

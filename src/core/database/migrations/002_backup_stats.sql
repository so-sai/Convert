-- ------------------------------------------------------------------------------
-- PROJECT CONVERT (C) 2025
-- Licensed under PolyForm Noncommercial 1.0.
-- ------------------------------------------------------------------------------

-- Migration: 002_backup_stats.sql
-- Creates user_preferences table for backup tracking and smart nudges

CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at INTEGER DEFAULT (unixepoch())
) STRICT;

-- Initialize backup tracking keys
INSERT OR IGNORE INTO user_preferences (key, value) VALUES 
    ('backup.last_ts', NULL),
    ('backup.reminder_count', '0'),
    ('backup.dismissed', '0'),
    ('notes.total_count', '0');

"""
Indexer Module - Task 6.3 + 6.4
Batch processing, SQLite synchronization, and secure storage

Task 6.3: IndexerQueue - Batch processing pipeline
Task 6.4: Security Foundation - Encrypted storage, sandboxed extraction
"""

# Task 6.3 - Queue
from src.core.indexer.queue import IndexerQueue, Batch, QueueMetrics

# Task 6.4 - Security Foundation
from src.core.indexer.security import PathGuard, InputValidator, ValidationResult
from src.core.indexer.sandbox import SandboxExecutor, SandboxError
from src.core.indexer.encrypted_storage import EncryptedIndexerDB

__all__ = [
    # Task 6.3
    "IndexerQueue", 
    "Batch", 
    "QueueMetrics",
    # Task 6.4
    "PathGuard",
    "InputValidator", 
    "ValidationResult",
    "SandboxExecutor",
    "SandboxError",
    "EncryptedIndexerDB",
]

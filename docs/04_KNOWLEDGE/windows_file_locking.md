# Windows File Locking & Persistence Protocol

> **Context:** Windows 11 / Python 3.14
> **Related Rule:** Rule #17 in Engineering Playbook

## The Problem
Windows maintains file locks longer than Unix systems. This causes `[WinError 32] The process cannot access the file because it is being used by another process` errors during tests and production, especially when dealing with SQLite databases and temporary files.

## The Solution: Explicit Resource Management

### 1. Database Connections
Always ensure database handles are released and garbage collected before attempting file operations.

```python
import gc
import asyncio
import aiosqlite

async def force_close_db():
    """Ensure database handles are released"""
    gc.collect()  # Force garbage collection
    await asyncio.sleep(1.0)  # Give OS time to release handles

# Usage pattern
async with aiosqlite.connect(db_path) as db:
    await db.execute("PRAGMA journal_mode=DELETE")  # Disable WAL to avoid -wal file locks
    await db.commit()

del db  # Explicit deletion
await force_close_db()
```

### 2. Retry Logic for File Operations
Implement exponential backoff when performing file operations that might be locked.

```python
import time
import shutil

def resilient_move(source, destination, max_retries=5):
    for attempt in range(max_retries):
        try:
            if destination.exists():
                destination.unlink()
            shutil.move(str(source), str(destination))
            break
        except OSError:
            if attempt == max_retries - 1:
                raise
            time.sleep(0.5 * (attempt + 1))  # Exponential backoff
```

## Best Practices
1.  **Disable WAL Mode** for temporary databases if you plan to move/delete them immediately.
2.  **Explicit `del`** objects that hold file handles.
3.  **`gc.collect()`** is your friend on Windows.
4.  **Async Sleep** allows the OS event loop to process the file handle release.

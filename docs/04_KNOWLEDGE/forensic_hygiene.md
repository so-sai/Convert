# Forensic Hygiene & Toxic Waste Disposal

> **Context:** Security / Privacy
> **Related Rule:** Rule #19 in Engineering Playbook

## The Problem
Standard file deletion (`rm`, `unlink`) only removes the reference to the file, leaving the data intact on the disk until overwritten. For sensitive data (databases, keys, exports), this is a security risk ("Toxic Waste").

## The Solution: Secure Wipe Protocol

### 1. The Protocol
The "Toxic Waste Disposal Protocol" involves three steps:
1.  **Overwrite:** Fill the file content with random data.
2.  **Obfuscate:** Rename the file to a random string (to hide metadata/intent).
3.  **Delete:** Unlink the file.

### 2. Implementation

```python
import os
import uuid
from pathlib import Path

def secure_wipe_file(path: Path) -> None:
    """1-pass overwrite + rename + delete for forensic hygiene"""
    if not path.exists():
        return
    
    try:
        # 1. Overwrite with random data
        file_size = path.stat().st_size
        with open(path, "rb+") as f:
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())
        
        # 2. Obfuscate with random name
        temp_name = path.parent / f"{uuid.uuid4()}.tmp"
        path.rename(temp_name)
        
        # 3. Delete
        temp_name.unlink()
        
    except Exception:
        # Fallback: delete if overwrite fails (better than nothing)
        if path.exists():
            try: path.unlink()
            except: pass
```

## Usage
Use this in `finally` blocks for ANY temporary file containing sensitive data (decrypted DBs, export files, etc.).

```python
try:
    temp_db = create_temp_database()
    process_sensitive_data(temp_db)
finally:
    secure_wipe_file(temp_db)
```

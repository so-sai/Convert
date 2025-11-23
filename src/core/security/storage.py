"""
Key Storage Layer
Ref: TECH_SPEC_SPRINT4_ENCRYPTION.md Section 9
"""

import sqlite3
import datetime
from pathlib import Path
from typing import Tuple, Optional

class KeyStorage:
    """
    Manages persistence of encrypted DEK and Salt in SQLite.
    """
    
    def __init__(self, db_path: str = "db.sqlite"):
        """
        Initialize KeyStorage and ensure schema exists.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create system_keys table if it doesn't exist."""
        # Ensure parent directory exists
        db_path_obj = Path(self.db_path)
        if db_path_obj.parent.name: # Only create parent if it's not empty/current dir
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_keys (
                    id INTEGER PRIMARY KEY,
                    salt BLOB NOT NULL,
                    encrypted_dek BLOB NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def write(self, salt: bytes, encrypted_dek: bytes) -> None:
        """
        Store the salt and encrypted DEK.
        
        Args:
            salt: 16-byte salt
            encrypted_dek: Encrypted DEK blob
        """
        with sqlite3.connect(self.db_path) as conn:
            # We only support one key for now (Single DEK architecture)
            conn.execute("DELETE FROM system_keys")
            
            conn.execute(
                "INSERT INTO system_keys (salt, encrypted_dek, created_at) VALUES (?, ?, ?)",
                (salt, encrypted_dek, datetime.datetime.now(datetime.timezone.utc).isoformat())
            )
            conn.commit()

    def read(self) -> Tuple[bytes, bytes]:
        """
        Retrieve the salt and encrypted DEK.
        
        Returns:
            Tuple[bytes, bytes]: (salt, encrypted_dek)
            
        Raises:
            ValueError: If no key is found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT salt, encrypted_dek FROM system_keys ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            
            if not row:
                raise ValueError("No system keys found in storage.")
                
            return row[0], row[1]

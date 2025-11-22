# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
import sqlite3, sys
MIN_VER = (3, 50, 2)
cur = tuple(map(int, sqlite3.sqlite_version.split('.')))
print(f"SQLite: {sqlite3.sqlite_version}")
sys.exit(0 if cur >= MIN_VER else 1)

# Copyright (c) 2025 Project CONVERT. PolyForm Noncommercial 1.0.0
# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None
a = Analysis(
    ['src/core/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['aiosqlite', 'uvicorn', 'fastapi', 'orjson', 'sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='mds-core', debug=False, strip=False, upx=True, console=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='mds-core')

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import sys
from pathlib import Path

block_cipher = None

# STRATEGY: COMBINED AUTOMATIC + EXPLICIT
nacl_datas, nacl_binaries, nacl_hiddenimports = collect_all('nacl')

a = Analysis(
    ['src/core/main.py'],
    pathex=[],
    binaries=nacl_binaries,
    datas=[
        # QA PATCH: Map config directly to root 'config' folder
        ('src/core/config', 'config'), 
        ('src/core/storage', 'storage'), 
    ] + nacl_datas,
    hiddenimports=[
        # CRITICAL CORE
        'nacl', 'nacl._sodium', 'nacl.bindings', 'nacl.secret', 'nacl.utils', 'nacl.pwhash',
        # ASYNC CORE
        'uvicorn.loops.auto', 'uvicorn.protocols.http.auto', 'uvicorn.lifespan.on',
        'uvicorn.loops.asyncio', 'asyncio', 'concurrent.futures',
        # DATA CORE
        'sqlite3', 'orjson', 'cffi', '_cffi_backend'
    ] + nacl_hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mds-core',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mds-core',
)

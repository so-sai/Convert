"""
Surgical Cleanup - Remove SQLCipher source artifacts from filesystem
Adheres to ARCH_PRIME Constitution: Python-only, no shell commands

This script physically removes source code directories that should not be in the main repository.
Only strategic assets (compiled binaries and wrappers) are preserved.
"""

import shutil
import os
from pathlib import Path

def perform_surgical_cleanup():
    """Remove SQLCipher source artifacts from filesystem"""
    
    print("="*60)
    print("🔪 SURGICAL CLEANUP - SQLCIPHER SOURCE REMOVAL")
    print("="*60)
    
    # Directories to remove (source code, not strategic assets)
    target_folders = [
        "sqlcipher3/src",
        "sqlcipher3/include",
        "sqlcipher3/lib",
        "sqlcipher3/sqlcipher-4.12.0",
        "sqlcipher3/build-scripts",
        "sqlcipher3/tests",
        "sqlcipher3/ext",
    ]
    
    # Files to remove (build artifacts)
    target_files = [
        "sqlcipher3/sqlite3.c",
        "sqlcipher3/sqlite3.h",
        "sqlcipher3/sqlcipher-4.12.0.zip",
        "sqlcipher3/setup.cfg",
        "sqlcipher3/MANIFEST.in",
    ]
    
    base_path = Path.cwd()
    print(f"\n📁 Working directory: {base_path}")
    
    removed_count = 0
    locked_count = 0
    
    # Remove directories
    print("\n🗂️  Removing source directories...")
    for folder in target_folders:
        dir_path = base_path / folder
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                removed_count += 1
                print(f"   ✅ Removed: {folder}")
            except PermissionError:
                locked_count += 1
                print(f"   🔒 Locked: {folder} (close IDE/terminal)")
            except Exception as e:
                print(f"   ❌ Error: {folder} ({e})")
        else:
            print(f"   ℹ️  Not found: {folder}")
    
    # Remove files
    print("\n📄 Removing build artifact files...")
    for file in target_files:
        file_path = base_path / file
        if file_path.exists():
            try:
                file_path.unlink()
                removed_count += 1
                print(f"   ✅ Removed: {file}")
            except PermissionError:
                locked_count += 1
                print(f"   🔒 Locked: {file}")
            except Exception as e:
                print(f"   ❌ Error: {file} ({e})")
    
    # Verify strategic assets remain
    print("\n🛡️  Verifying strategic assets...")
    strategic_assets = [
        "sqlcipher3/sqlcipher3/_sqlite3.pyd",
        "sqlcipher3/sqlcipher3/__init__.py",
        "sqlcipher3/sqlcipher3/dbapi2.py",
        "sqlcipher3/package_sqlcipher.py",
        "sqlcipher3/auto_build_sqlcipher.py",
    ]
    
    all_present = True
    for asset in strategic_assets:
        asset_path = base_path / asset
        if asset_path.exists():
            size = asset_path.stat().st_size
            print(f"   ✅ {asset} ({size:,} bytes)")
        else:
            all_present = False
            print(f"   ❌ MISSING: {asset}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 CLEANUP SUMMARY")
    print("="*60)
    print(f"\n✅ Removed: {removed_count} items")
    
    if locked_count > 0:
        print(f"🔒 Locked: {locked_count} items")
        print("\n   Solutions:")
        print("   1. Close VS Code / PyCharm")
        print("   2. Deactivate venv: deactivate")
        print("   3. Close all terminals in sqlcipher3/")
    
    if all_present:
        print("\n🎉 All strategic assets preserved!")
        print("\n📋 Next steps:")
        print("   1. git rm -rf --cached .")
        print("   2. git add .")
        print("   3. git ls-files | wc -l  (should be ~271)")
    else:
        print("\n⚠️  WARNING: Some strategic assets are missing!")
        print("   Please restore from backup before proceeding")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    perform_surgical_cleanup()

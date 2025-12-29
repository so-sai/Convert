"""
Nuclear Purge - Force remove locked files on Windows
Adheres to ARCH_PRIME Constitution: Python-only file operations

Uses onerror callback to handle:
- Read-only files
- Permission denied errors
- File handles held by other processes

IMPORTANT: Close VS Code and all IDEs before running!
"""

import os
import shutil
import stat
from pathlib import Path

def remove_readonly(func, path, excinfo):
    """
    Error handler for shutil.rmtree.
    If permission denied, change file to writable and retry.
    """
    try:
        # Try to change permission to writable
        os.chmod(path, stat.S_IWRITE)
        func(path)
        print(f"   🔧 Force removed: {path}")
    except Exception as e:
        print(f"   ❌ Still locked: {path} ({e})")

def nuclear_cleanup():
    """Execute nuclear cleanup of all source artifacts"""
    
    print("="*60)
    print("☢️  NUCLEAR PURGE - FORCE REMOVE LOCKED FILES")
    print("="*60)
    print("\n⚠️  PREREQUISITES:")
    print("   1. Close VS Code completely")
    print("   2. Close all terminals in sqlcipher3/")
    print("   3. Deactivate Python venv: deactivate")
    print("\n" + "-"*60)
    
    # Directories to remove (source code, not strategic assets)
    junk_targets = [
        "sqlcipher3/src",
        "sqlcipher3/include", 
        "sqlcipher3/lib",
        "sqlcipher3/sqlcipher-4.12.0",
        "sqlcipher3/build",
        "sqlcipher3/dist",
        "sqlcipher3/tests",
        "sqlcipher3/ext",
        "build",
        "dist",
    ]
    
    # Individual files to remove
    junk_files = [
        "sqlcipher3/sqlite3.c",
        "sqlcipher3/sqlite3.h",
        "sqlcipher3/sqlcipher-4.12.0.zip",
        "sqlcipher3/setup.cfg",
        "sqlcipher3/MANIFEST.in",
    ]
    
    base_dir = Path.cwd()
    print(f"\n📁 Working directory: {base_dir}")
    
    destroyed_count = 0
    failed_count = 0
    
    # Remove directories with force
    print("\n🗂️  Purging directories...")
    for target in junk_targets:
        path = base_dir / target
        if path.exists():
            try:
                # Use onerror callback to handle locked files
                shutil.rmtree(path, onerror=remove_readonly)
                destroyed_count += 1
                print(f"   ✅ DESTROYED: {target}")
            except Exception as e:
                failed_count += 1
                print(f"   ❌ FAILED: {target} ({e})")
        else:
            print(f"   ℹ️  Not found: {target}")
    
    # Remove individual files
    print("\n📄 Purging files...")
    for file in junk_files:
        file_path = base_dir / file
        if file_path.exists():
            try:
                os.chmod(file_path, stat.S_IWRITE)
                file_path.unlink()
                destroyed_count += 1
                print(f"   ✅ DESTROYED: {file}")
            except Exception as e:
                failed_count += 1
                print(f"   ❌ FAILED: {file} ({e})")
    
    # Verify strategic assets
    print("\n🛡️  Verifying strategic assets...")
    strategic_assets = [
        "sqlcipher3/sqlcipher3/_sqlite3.pyd",
        "sqlcipher3/sqlcipher3/__init__.py",
        "sqlcipher3/sqlcipher3/dbapi2.py",
    ]
    
    all_present = True
    for asset in strategic_assets:
        asset_path = base_dir / asset
        if asset_path.exists():
            size = asset_path.stat().st_size
            print(f"   ✅ PRESERVED: {asset} ({size:,} bytes)")
        else:
            all_present = False
            print(f"   ❌ MISSING: {asset}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 NUCLEAR PURGE SUMMARY")
    print("="*60)
    print(f"\n☢️  Destroyed: {destroyed_count} items")
    
    if failed_count > 0:
        print(f"❌ Failed: {failed_count} items")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Restart your computer")
        print("   2. Run this script IMMEDIATELY after boot")
        print("   3. Do NOT open VS Code first")
    else:
        print("\n🎉 ALL TARGETS ELIMINATED!")
    
    if all_present:
        print("\n✅ Strategic assets preserved!")
        print("\n📋 NEXT STEPS:")
        print("   git rm -rf --cached .")
        print("   git add .")
        print("   git ls-files | wc -l  # Target: ~271")
        print("   git commit -m \"feat(cleanup): Task 6.5 Complete - Repository sanitized\"")
        print("   git push origin feat/sprint-6-watchdog --force-with-lease")
    
    print("\n" + "="*60)
    
    return failed_count == 0

if __name__ == "__main__":
    success = nuclear_cleanup()
    exit(0 if success else 1)

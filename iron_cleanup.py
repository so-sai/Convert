import os
import shutil
from pathlib import Path

# DANH SÁCH ĐEN (BLACK LIST) - FILE CẦN XÓA
trash_list = [
    # Docs rác lẻ tẻ
    "docs/04_KNOWLEDGE/windows_file_locking.md",
    "docs/04_KNOWLEDGE/libsodium_api_patterns.md",
    "docs/04_KNOWLEDGE/forensic_hygiene.md",
    "docs/04_KNOWLEDGE/sprint4_walkthrough.md",
    
    # Folder ngữ cảnh thừa
    "docs/00_context",
    
    # Code rác / Backup cũ
    "src/core/security/backup.py.bak_legacy",
    "src/core/security/legacy_kdf_sprint4.py",
    
    # Test rác / Debug
    "tests/debug_crypto.py",
    "tests/debug_trace.py",
    "tests/test_kms_core.py", # Test cũ
    
    # Folder scripts (Chứa các file deploy dùng 1 lần)
    "scripts",
    
    # File rơi rớt ở root
    "deploy_crypto_trinity_rev2.py",
    "setup_sprint4.py",
    "deploy_backup_core.py",
    "deploy_fix_backup_api.py",
    "deploy_fix_return_bool.py",
    "deploy_fix_chunking_logic.py",
    "deploy_fix_test_windows.py",
    "deploy_fix_test_windows_v2.py",
    "deploy_fix_sqlite_mode.py",
    "deploy_fix_backup_retry.py",
    "fix_test_sqlite_mode.py",
    "fix_backup_retry.py",
    "fix_test_timing.py",
    "fix_final_nuclear.py"
]

print("🛡️ STARTING IRON HAND CLEANUP...")

for item in trash_list:
    p = Path(item)
    if p.exists():
        try:
            if p.is_dir():
                shutil.rmtree(p)
                print(f"🔥 Deleted Directory: {item}")
            else:
                p.unlink()
                print(f"🗑️ Deleted File: {item}")
        except Exception as e:
            print(f"⚠️ Failed to delete {item}: {e}")
    else:
        # File đã sạch, tốt
        pass

# KIỂM TRA FILE CỐT LÕI
required_files = [
    "docs/04_KNOWLEDGE/LEGACY_LESSONS.md",
    "docs/05_OPERATIONS/ENGINEERING_PLAYBOOK.md",
    "docs/01_ARCHITECTURE/MDS_v3.14.md"
]

print("\n🔍 VERIFYING CORE FILES...")
for f in required_files:
    if Path(f).exists():
        size = Path(f).stat().st_size
        print(f"✅ OK: {f} ({size} bytes)")
    else:
        print(f"❌ MISSING: {f} (Cần tạo lại hoặc kiểm tra vị trí)")

print("\n✨ CLEANUP COMPLETE. READY FOR HANDOVER.")

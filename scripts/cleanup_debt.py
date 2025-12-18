import shutil
import os
from pathlib import Path

def purge_technical_debt():
    # Define targets relative to project root
    # This script is located in scripts/, so parent is root
    root = Path(__file__).resolve().parent.parent
    redundant_paths = [
        root / "src" / "ui"  # This contains the nested /src and /src-tauri debt
    ]

    print(f"🚀 [CLEANUP] Starting Sprint 6 Sanitization...")
    
    for path in redundant_paths:
        if path.exists() and path.is_dir():
            try:
                shutil.rmtree(path)
                print(f"✅ [REMOVED] Technical Debt: {path}")
            except Exception as e:
                print(f"❌ [ERROR] Failed to remove {path}: {e}")
        else:
            print(f"ℹ️ [SKIP] Path not found or already clean: {path}")

    print("🎯 [STATUS] Project Structure Aligned with MDS v3.14 Pi.")

if __name__ == "__main__":
    purge_technical_debt()

import os
import shutil
from pathlib import Path

def kill_ghost_files():
    print("��� TIÊU DIỆT GHOST FILES...")
    
    root = Path.cwd()
    ghosts = [
        "package.json",           # THỦ PHẠM CHÍNH
        "package-lock.json",
        "node_modules",
        "vite.config.js", 
        "vite.config.ts",
        "tsconfig.json"
    ]
    
    for ghost in ghosts:
        ghost_path = root / ghost
        if ghost_path.exists():
            try:
                if ghost_path.is_dir():
                    shutil.rmtree(ghost_path)
                    print(f"��� ĐÃ XÓA THƯ MỤC MA: {ghost}")
                else:
                    ghost_path.unlink()
                    print(f"��� ĐÃ XÓA FILE MA: {ghost}")
            except Exception as e:
                print(f"⚠️ Không xóa được {ghost}: {e}")
        else:
            print(f"✅ SẠCH: {ghost}")
    
    print("\n��� GHOST FILES ĐÃ BỊ TIÊU DIỆT!")

if __name__ == "__main__":
    kill_ghost_files()

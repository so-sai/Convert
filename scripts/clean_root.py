import os
import shutil
from pathlib import Path

def main():
    root = Path.cwd()
    print(f"🧹 ĐANG QUÉT RÁC TẠI: {root}")
    
    # Danh sách "kẻ phá hoại" cần tiêu diệt ở thư mục gốc
    enemies = [
        "package.json",       # <--- THỦ PHẠM CHÍNH (File rỗng)
        "package-lock.json",
        "node_modules",
        "vite.config.js",
        "vite.config.ts"
    ]
    
    for name in enemies:
        path = root / name
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"   🔥 Đã diệt: {name}")
            except Exception as e:
                print(f"   ⚠️ Không xóa được {name}: {e}")
        else:
            print(f"   ✅ Sạch: Không thấy {name}")

    print("\n👉 Đã dọn xong. Sếp vào lại src-tauri và chạy là lên!")

if __name__ == "__main__":
    main()

import os
import subprocess
import sys

def run_npm_uninstall():
    # Đường dẫn vào thư mục UI
    ui_path = os.path.join("..", "src-ui")
    ui_abs_path = os.path.abspath(ui_path)
    
    print(f"🧹 Đang dọn dẹp thư viện tại: {ui_abs_path}")
    
    # Lệnh gỡ bỏ các gói gây xung đột
    # tailwindcss, postcss, autoprefixer: Bộ 3 gây lỗi
    cmd = "npm uninstall tailwindcss postcss autoprefixer"
    
    try:
        # Chạy lệnh npm uninstall trong thư mục src-ui
        subprocess.run(cmd, cwd=ui_abs_path, shell=True, check=True)
        print("✅ Đã gỡ bỏ thành công Tailwind và PostCSS.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Lỗi khi gỡ npm: {e}")
        print("Đừng lo, script sẽ tiếp tục xóa file cấu hình.")

def remove_config_files():
    ui_path = os.path.join("..", "src-ui")
    
    # Danh sách file rác cần xóa
    files = [
        "postcss.config.js", 
        "postcss.config.cjs",
        "tailwind.config.js", 
        "tailwind.config.ts",
        "tailwind.config.cjs"
    ]
    
    for f in files:
        path = os.path.join(ui_path, f)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🗑️ Đã xóa file thừa: {f}")
            except Exception as e:
                print(f"❌ Không xóa được {f}: {e}")

def fix_app_css():
    # Reset file app.css về sạch sẽ, không còn gọi @tailwind
    css_path = os.path.join("..", "src-ui", "src", "app.css")
    clean_css = """/* MDS v3.14 Pi - Native CSS System */
:root {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f5f7;
}
"""
    try:
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(clean_css)
        print("✨ Đã khôi phục src/app.css sạch sẽ.")
    except Exception as e:
        print(f"❌ Lỗi ghi app.css: {e}")

if __name__ == "__main__":
    print("🚀 Bắt đầu sửa lỗi Dependency...")
    run_npm_uninstall()
    remove_config_files()
    fix_app_css()
    print("\n🏁 HOÀN TẤT! Sếp hãy chạy lại 'cargo tauri dev' ngay.")

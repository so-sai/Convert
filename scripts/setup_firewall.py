import os
from pathlib import Path

# Nội dung .gitignore CHUẨN cho stack: Python + Tauri v2 + Rust + Node
GITIGNORE_CONTENT = r"""
# --- 1. RUST & TAURI GARBAGE (Nặng nhất) ---
/src-tauri/target/
/target/
/src-tauri/gen/
**/.DS_Store
**/*.log

# --- 2. NODE JS GARBAGE ---
node_modules/
/src-tauri/node_modules/
package-lock.json
pnpm-lock.yaml
yarn.lock

# --- 3. PYTHON GARBAGE ---
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.pytest_cache/
.coverage
htmlcov/

# --- 4. OS & IDE GARBAGE ---
.vscode/
.idea/
Thumbs.db
*.swp

# --- 5. SECURITY ---
.env
*.pem
*.key
"""

def main():
    root = Path.cwd()
    gitignore_path = root / ".gitignore"
    
    print(f"🛡️  ACTIVATING FIREWALL AT: {root}")
    
    # Rule #9: Write via Python
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(GITIGNORE_CONTENT.strip())
    
    print("✅ .gitignore has been updated.")
    print("👉 Rác (target, node_modules) sẽ bị chặn.")
    print("👉 Chỉ Source Code (src, icons, Cargo.toml) mới được đi qua.")

if __name__ == "__main__":
    main()

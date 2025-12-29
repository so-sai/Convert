"""
.gitignore Fixer
Updates .gitignore with strict rules to prevent build artifacts from being tracked

Adheres to ARCH_PRIME Constitution:
- No shell commands (cat, echo)
- Preserves strategic assets (_sqlite3.pyd)
- Clear separation of concerns
"""

from pathlib import Path

def fix_gitignore():
    """Apply strict .gitignore rules"""
    
    content = """# ============================================
# ARCH_PRIME CONSTITUTION - GITIGNORE RULES
# ============================================

# --- SYSTEM ARTIFACTS (NEVER COMMIT) ---
**/target/
**/node_modules/
**/__pycache__/
**/.pytest_cache/
**/.mypy_cache/
*.pyc
*.pyo
*.pdb
*.obj
*.exp
*.ilk
build/
dist/
*.egg-info

# --- RUST BUILD ARTIFACTS ---
**/Cargo.lock
**/target/debug/
**/target/release/

# --- PYTHON BUILD ARTIFACTS ---
*.so
*.dll
*.dylib
__pycache__/
*.py[cod]
*$py.class

# --- C/C++ BUILD ARTIFACTS ---
*.o
*.obj
*.lib
*.exp
*.pdb
*.ilk

# --- IDE & EDITOR ---
.vscode/
.idea/
*.swp
*.swo
*~

# --- OS SPECIFIC ---
.DS_Store
Thumbs.db
desktop.ini

# --- LOGS & DATABASES ---
*.log
*.sqlite
*.db

# ============================================
# STRATEGIC ASSETS (FORCE INCLUDE)
# ============================================

# SQLCipher compiled binary (critical asset)
!sqlcipher3/sqlcipher3/_sqlite3.pyd
!sqlcipher3/sqlcipher3/__init__.py
!sqlcipher3/sqlcipher3/dbapi2.py
!sqlcipher3/sqlcipher3/dump.py

# Documentation
!docs/**/*.md

# Configuration
!pyproject.toml
!pytest.ini
!requirements*.txt
"""
    
    gitignore_path = Path(".gitignore")
    
    # Backup existing .gitignore
    if gitignore_path.exists():
        backup_path = Path(".gitignore.backup")
        backup_path.write_text(gitignore_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"📋 Backed up existing .gitignore to {backup_path}")
    
    # Write new .gitignore
    gitignore_path.write_text(content, encoding="utf-8")
    
    print("="*60)
    print("✅ .gitignore UPDATED")
    print("="*60)
    print("\n📝 Applied strict rules:")
    print("   • Block: target/, node_modules/, __pycache__/")
    print("   • Block: *.pyc, *.obj, *.pdb, build/, dist/")
    print("   • Preserve: _sqlite3.pyd (strategic asset)")
    print("\n🎯 Next steps:")
    print("   1. git add .gitignore")
    print("   2. git reset  (clear index)")
    print("   3. git add .  (re-index with new rules)")
    print("   4. git status (verify clean state)")

if __name__ == "__main__":
    fix_gitignore()

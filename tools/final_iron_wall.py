"""
Final Iron Wall - Block all SQLCipher source artifacts from Git
Stealth Protocol: Git won't see locked files anymore

This allows clean Git state even when files are locked by Windows.
"""

from pathlib import Path

def apply_iron_wall():
    """Apply strict .gitignore rules to block all artifacts"""
    
    content = """# ============================================
# IRON WALL - FINAL GITIGNORE CONFIGURATION
# ============================================

# --- SYSTEM ARTIFACTS (BLOCK ALL BUILD OUTPUT) ---
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
*.lib
*.d
build/
dist/
*.egg-info/

# --- SQLCIPHER SOURCE ARTIFACTS (BLOCK LOCKED FILES) ---
sqlcipher3/src/
sqlcipher3/include/
sqlcipher3/lib/
sqlcipher3/build/
sqlcipher3/build-scripts/
sqlcipher3/sqlcipher-4.12.0/
sqlcipher3/tests/
sqlcipher3/ext/
sqlcipher3/sqlite3.c
sqlcipher3/sqlite3.h
sqlcipher3/sqlcipher-4.12.0.zip
sqlcipher3/setup.cfg
sqlcipher3/MANIFEST.in

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

# SQLCipher compiled binary (CRITICAL)
!sqlcipher3/sqlcipher3/
!sqlcipher3/sqlcipher3/_sqlite3.pyd
!sqlcipher3/sqlcipher3/__init__.py
!sqlcipher3/sqlcipher3/dbapi2.py
!sqlcipher3/sqlcipher3/dump.py

# SQLCipher scripts
!sqlcipher3/package_sqlcipher.py
!sqlcipher3/test_wheel_install.py
!sqlcipher3/auto_build_sqlcipher.py

# SQLCipher metadata
!sqlcipher3/.gitignore
!sqlcipher3/LICENSE
!sqlcipher3/README.md
!sqlcipher3/.github/
"""
    
    Path(".gitignore").write_text(content, encoding="utf-8")
    
    print("="*60)
    print("🛡️  IRON WALL APPLIED")
    print("="*60)
    print("\n✅ .gitignore updated with strict artifact blocking")
    print("\n🚫 Git will now IGNORE:")
    print("   • sqlcipher3/src/ (locked C source)")
    print("   • sqlcipher3/include/ (locked headers)")
    print("   • sqlcipher3/lib/ (locked libraries)")
    print("\n✅ Git will KEEP:")
    print("   • sqlcipher3/sqlcipher3/_sqlite3.pyd")
    print("   • sqlcipher3/sqlcipher3/*.py")
    print("   • sqlcipher3/*.py (build scripts)")
    print("\n📋 NEXT STEPS:")
    print("   git rm -rf --cached .")
    print("   git add .")
    print("   git ls-files | wc -l  # Target: ~258")
    print("\n" + "="*60)

if __name__ == "__main__":
    apply_iron_wall()

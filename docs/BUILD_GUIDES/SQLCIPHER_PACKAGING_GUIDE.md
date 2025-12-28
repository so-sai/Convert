# 📦 SQLCIPHER PACKAGING & DISTRIBUTION GUIDE

> **Purpose:** Package the manually-built SQLCipher 4.12.0 binary into a distributable Python wheel  
> **Target:** Easy installation across development and production environments  
> **Status:** Production-Ready

---

## 🎯 1. PACKAGING OBJECTIVES

### Why Package as Wheel?
- ✅ **One-Command Install** - `pip install sqlcipher3-*.whl`
- ✅ **No Rebuild Required** - Pre-compiled binary included
- ✅ **Version Control** - Proper semantic versioning
- ✅ **Team Distribution** - Share across team members easily
- ✅ **CI/CD Ready** - Integrate into automated pipelines

---

## 🛠️ 2. PACKAGING SCRIPT

Create this script in your SQLCipher build directory:

### File: `package_sqlcipher.py`

```python
"""
SQLCipher 4.12.0 Packaging Script
Packages the manually-built _sqlite3.pyd into a distributable wheel
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
PACKAGE_NAME = "sqlcipher3-binary"
VERSION = "4.12.0"
PYTHON_VERSION = "cp314"  # Python 3.14
PLATFORM = "win_amd64"

# Paths
BUILD_DIR = Path("build_wheel")
PACKAGE_DIR = BUILD_DIR / "sqlcipher3"
DIST_DIR = Path("dist")

def clean_build():
    """Remove previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    
    for path in [BUILD_DIR, DIST_DIR, Path("sqlcipher3_binary.egg-info")]:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    
    print("✅ Clean complete")

def create_package_structure():
    """Create proper package directory structure"""
    print("📁 Creating package structure...")
    
    # Create directories
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy the built .pyd file
    pyd_source = Path("sqlcipher3/_sqlite3.pyd")
    if not pyd_source.exists():
        print(f"❌ Error: {pyd_source} not found!")
        print("   Please ensure you've successfully built the .pyd file first.")
        sys.exit(1)
    
    shutil.copy2(pyd_source, PACKAGE_DIR / "_sqlite3.pyd")
    print(f"   ✅ Copied {pyd_source}")
    
    # Copy Python wrapper files
    wrapper_files = [
        "sqlcipher3/__init__.py",
        "sqlcipher3/dbapi2.py",
        "sqlcipher3/dump.py"
    ]
    
    for wrapper in wrapper_files:
        src = Path(wrapper)
        if src.exists():
            shutil.copy2(src, PACKAGE_DIR / src.name)
            print(f"   ✅ Copied {wrapper}")
    
    print("✅ Package structure created")

def create_setup_file():
    """Create setup.py for wheel building"""
    print("📝 Creating setup.py...")
    
    setup_content = f'''
from setuptools import setup, Distribution

class BinaryDistribution(Distribution):
    """Force binary distribution (contains .pyd file)"""
    def has_ext_modules(self):
        return True

setup(
    name="{PACKAGE_NAME}",
    version="{VERSION}",
    description="Pre-compiled SQLCipher 4.12.0 for Python 3.14 No-GIL (Windows x64)",
    long_description="""
# SQLCipher 4.12.0 Binary Distribution

Pre-compiled SQLCipher library with:
- AES-256-CBC encryption
- FTS5 full-text search
- Python 3.14 No-GIL support
- Windows x64 platform

## Installation
```bash
pip install sqlcipher3-binary-{VERSION}-{PYTHON_VERSION}-{PYTHON_VERSION}-{PLATFORM}.whl
```

## Usage
```python
import os
os.add_dll_directory(r"C:\\Program Files\\OpenSSL-Win64\\bin")

from sqlcipher3 import dbapi2 as sqlite

conn = sqlite.connect('encrypted.db')
conn.execute("PRAGMA key = 'your-secret-key'")
# Use like normal SQLite...
```

## Requirements
- OpenSSL 3.x DLLs must be accessible (see documentation)
    """,
    long_description_content_type="text/markdown",
    author="Convert Desktop Team",
    packages=["sqlcipher3"],
    package_dir={{"sqlcipher3": "build_wheel/sqlcipher3"}},
    package_data={{
        "sqlcipher3": ["*.pyd"]
    }},
    include_package_data=True,
    python_requires=">=3.14",
    distclass=BinaryDistribution,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.14",
        "Topic :: Database",
        "Topic :: Security :: Cryptography",
    ],
)
'''
    
    with open(BUILD_DIR / "setup.py", "w", encoding="utf-8") as f:
        f.write(setup_content.strip())
    
    print("✅ setup.py created")

def build_wheel():
    """Build the wheel distribution"""
    print("🔨 Building wheel...")
    
    # Ensure dist directory exists
    DIST_DIR.mkdir(exist_ok=True)
    
    # Build wheel
    result = subprocess.run(
        [sys.executable, "setup.py", "bdist_wheel"],
        cwd=BUILD_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Build failed:")
        print(result.stderr)
        sys.exit(1)
    
    # Move wheel to main dist directory
    wheel_files = list((BUILD_DIR / "dist").glob("*.whl"))
    if wheel_files:
        for wheel in wheel_files:
            dest = DIST_DIR / wheel.name
            shutil.move(str(wheel), str(dest))
            print(f"✅ Created: {dest}")
    else:
        print("❌ No wheel file generated!")
        sys.exit(1)

def print_installation_instructions():
    """Print next steps"""
    print("\n" + "="*60)
    print("🎉 PACKAGING COMPLETE!")
    print("="*60)
    
    wheel_files = list(DIST_DIR.glob("*.whl"))
    if wheel_files:
        wheel_path = wheel_files[0]
        print(f"\n📦 Wheel file: {wheel_path}")
        print(f"\n📋 Installation command:")
        print(f"   pip install {wheel_path}")
        print(f"\n📋 Force reinstall:")
        print(f"   pip install {wheel_path} --force-reinstall")
        print(f"\n📋 Share with team:")
        print(f"   Copy {wheel_path} to shared location")
        print(f"   Team members: pip install <path-to-wheel>")
    
    print("\n⚠️  IMPORTANT: OpenSSL DLLs Required")
    print("   Users must have OpenSSL 3.x installed or DLLs accessible")
    print("   Add to code: os.add_dll_directory(r'C:\\Program Files\\OpenSSL-Win64\\bin')")
    print("\n" + "="*60)

def main():
    """Main packaging workflow"""
    print("="*60)
    print("🛡️  SQLCIPHER 4.12.0 PACKAGING SCRIPT")
    print("="*60 + "\n")
    
    try:
        clean_build()
        create_package_structure()
        create_setup_file()
        build_wheel()
        print_installation_instructions()
        
    except Exception as e:
        print(f"\n❌ Error during packaging: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🚀 3. USAGE INSTRUCTIONS

### Step 1: Navigate to SQLCipher Directory
```cmd
cd e:\DEV\app-desktop-Convert\sqlcipher3
```

### Step 2: Run Packaging Script
```cmd
python package_sqlcipher.py
```

### Step 3: Verify Output
```
✅ Clean complete
✅ Package structure created
✅ setup.py created
✅ Created: dist\sqlcipher3-binary-4.12.0-cp314-cp314-win_amd64.whl
```

### Step 4: Install Wheel
```cmd
pip install dist\sqlcipher3-binary-4.12.0-cp314-cp314-win_amd64.whl
```

---

## 🧪 4. TESTING THE PACKAGED WHEEL

### Quick Test Script: `test_wheel_install.py`

```python
"""
Test the installed SQLCipher wheel
"""
import os
import sys

# Add OpenSSL DLL directory
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")

def test_import():
    """Test basic import"""
    print("🧪 Test 1: Import module...")
    try:
        from sqlcipher3 import dbapi2 as sqlite
        print("   ✅ Import successful")
        return sqlite
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        sys.exit(1)

def test_connection(sqlite):
    """Test database connection"""
    print("🧪 Test 2: Create encrypted database...")
    try:
        conn = sqlite.connect(':memory:')
        conn.execute("PRAGMA key = 'test123'")
        print("   ✅ Connection successful")
        return conn
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        sys.exit(1)

def test_encryption(conn):
    """Test encryption status"""
    print("🧪 Test 3: Verify encryption...")
    try:
        status = conn.execute("PRAGMA cipher_status").fetchone()
        if status[0] == '1':
            print(f"   ✅ Encryption active: {status}")
        else:
            print(f"   ❌ Encryption not active: {status}")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ Encryption check failed: {e}")
        sys.exit(1)

def test_versions(conn):
    """Test version information"""
    print("🧪 Test 4: Check versions...")
    try:
        cipher_ver = conn.execute("PRAGMA cipher_version").fetchone()[0]
        sqlite_ver = conn.execute("SELECT sqlite_version()").fetchone()[0]
        print(f"   ✅ SQLCipher: {cipher_ver}")
        print(f"   ✅ SQLite: {sqlite_ver}")
    except Exception as e:
        print(f"   ❌ Version check failed: {e}")
        sys.exit(1)

def test_fts5(conn):
    """Test FTS5 functionality"""
    print("🧪 Test 5: Test FTS5...")
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE docs USING fts5(title, content)
        """)
        conn.execute("""
            INSERT INTO docs VALUES ('Test', 'Full-text search test')
        """)
        result = conn.execute("""
            SELECT * FROM docs WHERE docs MATCH 'search'
        """).fetchone()
        
        if result:
            print(f"   ✅ FTS5 working: {result}")
        else:
            print("   ❌ FTS5 query returned no results")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ FTS5 test failed: {e}")
        sys.exit(1)

def main():
    print("="*60)
    print("🛡️  SQLCIPHER WHEEL INSTALLATION TEST")
    print("="*60 + "\n")
    
    sqlite = test_import()
    conn = test_connection(sqlite)
    test_encryption(conn)
    test_versions(conn)
    test_fts5(conn)
    
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)

if __name__ == "__main__":
    main()
```

---

## 📤 5. DISTRIBUTION STRATEGIES

### Option A: Local Team Distribution
```cmd
:: Copy wheel to shared network drive
copy dist\*.whl \\shared\python-packages\

:: Team members install from shared location
pip install \\shared\python-packages\sqlcipher3-binary-4.12.0-cp314-cp314-win_amd64.whl
```

### Option B: Private PyPI Server
```cmd
:: Upload to private PyPI (if available)
twine upload --repository-url https://pypi.company.com dist/*.whl

:: Team installs via pip
pip install sqlcipher3-binary --index-url https://pypi.company.com
```

### Option C: Git LFS (Large File Storage)
```cmd
:: Track wheel files with Git LFS
git lfs track "*.whl"
git add .gitattributes
git add dist/*.whl
git commit -m "Add SQLCipher wheel distribution"
git push
```

---

## ⚠️ 6. DEPLOYMENT CONSIDERATIONS

### OpenSSL DLL Requirements

**Development Environment:**
```python
# Add to application startup
import os
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")
```

**Production Deployment (Option 1: Bundle DLLs):**
```
app/
├── app.exe
├── libcrypto-3-x64.dll  ← Copy from OpenSSL
├── libssl-3-x64.dll     ← Copy from OpenSSL
└── ...
```

**Production Deployment (Option 2: Installer):**
```nsis
; NSIS Installer script
Section "OpenSSL DLLs"
    SetOutPath "$INSTDIR"
    File "libcrypto-3-x64.dll"
    File "libssl-3-x64.dll"
SectionEnd
```

---

## 🎯 7. NEXT STEPS

1. ✅ **Package the wheel** - Run `package_sqlcipher.py`
2. ✅ **Test installation** - Run `test_wheel_install.py`
3. ✅ **Distribute to team** - Choose distribution strategy
4. ✅ **Update requirements.txt** - Add wheel reference
5. ✅ **Document in README** - Add installation instructions

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-29  
**Status:** Production-Ready ✅

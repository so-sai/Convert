# 🎯 KINH NGHIỆM THỰC CHIẾN: SQLCIPHER TRÊN WINDOWS

> **Mục đích:** Rút ngắn thời gian build từ 6 giờ xuống 30 phút  
> **Đối tượng:** Developer cần build SQLCipher trên Windows  
> **Độ khó:** Expert (9/10)  
> **Thời gian tiết kiệm:** ~5.5 giờ

---

## ⏱️ TIMELINE THỰC TẾ

### Lần Đầu (Không có kinh nghiệm)
- **Thời gian:** 4-6 giờ
- **Lỗi gặp phải:** 15-20 lỗi khác nhau
- **Số lần rebuild:** 10-15 lần
- **Stress level:** 🔥🔥🔥🔥🔥

### Lần Sau (Có tài liệu này)
- **Thời gian:** 20-30 phút
- **Lỗi gặp phải:** 0-2 lỗi
- **Số lần rebuild:** 1-2 lần
- **Stress level:** ☕

---

## 🔴 TOP 7 LỖI CHẾT NGƯỜI & GIẢI PHÁP TỨC THÌ

### 1️⃣ LỖI: OpenSSL Detection Failed
```
RuntimeError: Fatal error: OpenSSL could not be detected!
```

**Thời gian mất:** ~45 phút (tìm hiểu setup.py)

**Giải pháp 30 giây:**
```cmd
xcopy "C:\Program Files\OpenSSL-Win64\include" include /s /e /y
xcopy "C:\Program Files\OpenSSL-Win64\lib\VC\x64\MT" lib /s /e /y
set "INCLUDE=%CD%\include;%INCLUDE%"
set "LIB=%CD%\lib;%LIB%"
```

---

### 2️⃣ LỖI: SQLCipher Security Macros
```
fatal error C1189: #error: "SQLCipher must be compiled with -DSQLITE_EXTRA_INIT..."
```

**Thời gian mất:** ~30 phút (đọc source code)

**Giải pháp 10 giây:**
```cmd
set "CL=/DSQLITE_EXTRA_INIT=sqlcipher_extra_init /DSQLITE_EXTRA_SHUTDOWN=sqlcipher_extra_shutdown"
```

---

### 3️⃣ LỖI: C11 Syntax (xoshiro)
```
error C2061: syntax error: identifier 'xoshiro_s'
```

**Thời gian mất:** ~1 giờ (debug syntax errors)

**Giải pháp 20 giây:**
```python
# Inject vào đầu sqlite3.c
headers = '''#include <stdint.h>
#include <inttypes.h>
#define SQLITE_EXTRA_INIT sqlcipher_extra_init
#define SQLITE_EXTRA_SHUTDOWN sqlcipher_extra_shutdown
'''
with open('sqlite3.c', 'r+', encoding='utf-8') as f:
    content = f.read()
    f.seek(0)
    f.write(headers + content)
```

---

### 4️⃣ LỖI: OpenSSL 3.x Library Names
```
LINK : fatal error LNK1181: cannot open input file 'libeay32.lib'
```

**Thời gian mất:** ~20 phút (tìm file lib)

**Giải pháp 5 giây:**
```cmd
cd lib
copy libcrypto.lib libeay32.lib
copy libssl.lib ssleay32.lib
```

---

### 5️⃣ LỗI: Module Entry Point
```
ImportError: dynamic module does not define module export function (PyInit__sqlite3)
```

**Thời gian mất:** ~40 phút (debug import)

**Giải pháp 15 giây:**
```cmd
# Thêm vào lệnh link
/EXPORT:PyInit__sqlite3
```

---

### 6️⃣ LỖI: DLL Load Failed
```
ImportError: DLL load failed while importing _sqlite3
```

**Thời gian mất:** ~15 phút (tìm DLL)

**Giải pháp 5 giây:**
```python
import os
os.add_dll_directory(r'C:\Program Files\OpenSSL-Win64\bin')
```

---

### 7️⃣ LỖI: Multiple egg-info
```
error: Multiple .egg-info directories found
```

**Thời gian mất:** ~10 phút (clean build)

**Giải pháp 5 giây:**
```cmd
rmdir /s /q build dist
for /d /r . %d in (*.egg-info) do @rmdir /s /q "%d"
```

---

## 🚀 QUY TRÌNH TỐI ƯU 30 PHÚT

### Phase 1: Setup (5 phút)
```cmd
:: 1. Mở Developer Command Prompt
"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"

:: 2. Activate venv
call .venv\Scripts\activate

:: 3. Install tools
pip install setuptools wheel

:: 4. Copy OpenSSL
xcopy "C:\Program Files\OpenSSL-Win64\include" include /s /e /y
xcopy "C:\Program Files\OpenSSL-Win64\lib\VC\x64\MT" lib /s /e /y
cd lib
copy libcrypto.lib libeay32.lib
copy libssl.lib ssleay32.lib
cd ..
```

### Phase 2: Prepare Source (3 phút)
```python
# inject_headers.py
headers = '''#include <stdint.h>
#include <inttypes.h>
#include <windows.h>
#define SQLITE_EXTRA_INIT sqlcipher_extra_init
#define SQLITE_EXTRA_SHUTDOWN sqlcipher_extra_shutdown
'''

with open('sqlite3.c', 'r', encoding='utf-8') as f:
    content = f.read()
    
with open('sqlite3.c', 'w', encoding='utf-8') as f:
    f.write(headers + content)

print("✅ Headers injected")
```

### Phase 3: Manual Build (15 phút)
```cmd
:: Set environment
set PYTHON_ROOT=C:\Users\Admin\AppData\Local\Programs\Python\Python314
set PYTHON_INCLUDE=%PYTHON_ROOT%\include
set PYTHON_LIBS=%PYTHON_ROOT%\libs

:: Compile sqlite3.c
cl /c /nologo /O2 /W3 /GL /DNDEBUG /MD /std:c11 ^
   /DSQLITE_HAS_CODEC /DSQLITE_ENABLE_FTS5 ^
   /DSQLITE_TEMP_STORE=2 ^
   /DSQLITE_EXTRA_INIT=sqlcipher_extra_init ^
   /DSQLITE_EXTRA_SHUTDOWN=sqlcipher_extra_shutdown ^
   /I"include" /I"." /I"%PYTHON_INCLUDE%" ^
   sqlite3.c /Fosqlite3.obj

:: Compile wrappers
md build
cl /c /nologo /O2 /W3 /GL /DNDEBUG /MD ^
   /I"include" /I"." /I"%PYTHON_INCLUDE%" ^
   -DMODULE_NAME=\"_sqlite3\" ^
   src\module.c src\connection.c src\cursor.c src\cache.c ^
   src\microprotocols.c src\prepare_protocol.c src\row.c ^
   src\statement.c src\util.c ^
   /Fobuild\

:: Link
link /nologo /DLL /LTCG ^
     /OUT:sqlcipher3\_sqlite3.pyd ^
     /LIBPATH:"lib" /LIBPATH:"%PYTHON_LIBS%" ^
     /EXPORT:PyInit__sqlite3 ^
     sqlite3.obj ^
     build\module.obj build\connection.obj build\cursor.obj ^
     build\cache.obj build\microprotocols.obj build\prepare_protocol.obj ^
     build\row.obj build\statement.obj build\util.obj ^
     libcrypto.lib libssl.lib ^
     ws2_32.lib advapi32.lib crypt32.lib user32.lib gdi32.lib
```

### Phase 4: Test (5 phút)
```python
# test_quick.py
import os
os.add_dll_directory(r'C:\Program Files\OpenSSL-Win64\bin')

from sqlcipher3 import dbapi2 as sqlite

conn = sqlite.connect(':memory:')
conn.execute("PRAGMA key = 'test123'")

# Verify
cipher_ver = conn.execute("PRAGMA cipher_version").fetchone()[0]
sqlite_ver = conn.execute("SELECT sqlite_version()").fetchone()[0]
status = conn.execute("PRAGMA cipher_status").fetchone()[0]

assert status == '1', "Encryption not active!"
print(f"✅ SQLCipher {cipher_ver} OK")
print(f"✅ SQLite {sqlite_ver} OK")
print(f"✅ Encryption: Active")
```

### Phase 5: Package (2 phút)
```cmd
python package_sqlcipher.py
pip install dist\*.whl --force-reinstall
```

---

## 💡 BÀI HỌC VÀNG

### 1. ĐỪNG LÃNG PHÍ THỜI GIAN VỚI SETUP.PY
**Sai lầm:** Cố gắng fix setup.py detection logic  
**Đúng:** Copy thủ công OpenSSL và build manual

**Thời gian tiết kiệm:** ~2 giờ

---

### 2. INJECT HEADERS NGAY TỪ ĐẦU
**Sai lầm:** Build rồi mới fix lỗi syntax  
**Đúng:** Inject `<stdint.h>` và macros trước khi compile

**Thời gian tiết kiệm:** ~1 giờ

---

### 3. DÙNG /std:c11 LÀ BẮT BUỘC
**Sai lầm:** Dùng MSVC default (C89)  
**Đúng:** Luôn dùng `/std:c11` cho SQLCipher

**Thời gian tiết kiệm:** ~1.5 giờ

---

### 4. TẠO ALIAS CHO OPENSSL 3.x
**Sai lầm:** Tìm cách sửa setup.py để dùng tên mới  
**Đúng:** Copy `libcrypto.lib` → `libeay32.lib`

**Thời gian tiết kiệm:** ~30 phút

---

### 5. CLEAN BUILD MỖI LẦN
**Sai lầm:** Build đè lên build cũ  
**Đúng:** `rmdir /s /q build` trước mỗi lần build

**Thời gian tiết kiệm:** ~45 phút (debug lỗi lạ)

---

## 🔧 SCRIPT TỰ ĐỘNG HÓA HOÀN CHỈNH

### File: `auto_build_sqlcipher.py`

```python
"""
Auto-build SQLCipher 4.12.0 for Windows
Reduces build time from 6 hours to 30 minutes
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

class SQLCipherBuilder:
    def __init__(self):
        self.root = Path.cwd()
        self.openssl_root = Path(r"C:\Program Files\OpenSSL-Win64")
        self.python_root = Path(sys.executable).parent
        
    def step1_clean(self):
        """Clean previous builds"""
        print("🧹 Step 1: Cleaning...")
        
        for path in ['build', 'dist']:
            if Path(path).exists():
                shutil.rmtree(path)
        
        for pattern in ['*.obj', '*.pyd', '*.exp', '*.lib']:
            for f in self.root.glob(pattern):
                f.unlink()
        
        for egg in self.root.rglob('*.egg-info'):
            shutil.rmtree(egg)
        
        print("   ✅ Clean complete")
    
    def step2_copy_openssl(self):
        """Copy OpenSSL files"""
        print("📦 Step 2: Copying OpenSSL...")
        
        # Copy headers
        if not Path('include').exists():
            shutil.copytree(self.openssl_root / 'include', 'include')
        
        # Copy libs
        if not Path('lib').exists():
            Path('lib').mkdir()
            for lib in (self.openssl_root / 'lib' / 'VC' / 'x64' / 'MT').glob('*.lib'):
                shutil.copy2(lib, 'lib')
        
        # Create aliases
        shutil.copy2('lib/libcrypto.lib', 'lib/libeay32.lib')
        shutil.copy2('lib/libssl.lib', 'lib/ssleay32.lib')
        
        print("   ✅ OpenSSL ready")
    
    def step3_inject_headers(self):
        """Inject C11 headers into sqlite3.c"""
        print("💉 Step 3: Injecting headers...")
        
        headers = '''#include <stdint.h>
#include <inttypes.h>
#include <windows.h>
#define SQLITE_EXTRA_INIT sqlcipher_extra_init
#define SQLITE_EXTRA_SHUTDOWN sqlcipher_extra_shutdown

'''
        
        sqlite_c = Path('sqlite3.c')
        if not sqlite_c.exists():
            print("   ❌ sqlite3.c not found!")
            sys.exit(1)
        
        content = sqlite_c.read_text(encoding='utf-8')
        if '#include <stdint.h>' not in content:
            sqlite_c.write_text(headers + content, encoding='utf-8')
            print("   ✅ Headers injected")
        else:
            print("   ℹ️  Headers already present")
    
    def step4_compile(self):
        """Compile source files"""
        print("🔨 Step 4: Compiling...")
        
        Path('build').mkdir(exist_ok=True)
        
        # Compile sqlite3.c
        cmd_sqlite = [
            'cl', '/c', '/nologo', '/O2', '/W3', '/GL', '/DNDEBUG', '/MD', '/std:c11',
            '/DSQLITE_HAS_CODEC', '/DSQLITE_ENABLE_FTS5', '/DSQLITE_TEMP_STORE=2',
            '/DSQLITE_EXTRA_INIT=sqlcipher_extra_init',
            '/DSQLITE_EXTRA_SHUTDOWN=sqlcipher_extra_shutdown',
            f'/I{self.root}/include', f'/I{self.root}',
            f'/I{self.python_root}/include',
            'sqlite3.c', '/Fosqlite3.obj'
        ]
        
        result = subprocess.run(cmd_sqlite, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ Compile failed:\n{result.stderr}")
            sys.exit(1)
        
        # Compile wrappers
        src_files = list(Path('src').glob('*.c'))
        for src in src_files:
            cmd_wrapper = [
                'cl', '/c', '/nologo', '/O2', '/W3', '/GL', '/DNDEBUG', '/MD',
                f'/I{self.root}/include', f'/I{self.root}',
                f'/I{self.python_root}/include',
                '-DMODULE_NAME=\\"_sqlite3\\"',
                str(src), f'/Fobuild/{src.stem}.obj'
            ]
            subprocess.run(cmd_wrapper, check=True, capture_output=True)
        
        print("   ✅ Compilation complete")
    
    def step5_link(self):
        """Link final .pyd"""
        print("🔗 Step 5: Linking...")
        
        obj_files = ['sqlite3.obj'] + [str(f) for f in Path('build').glob('*.obj')]
        
        cmd_link = [
            'link', '/nologo', '/DLL', '/LTCG',
            '/OUT:sqlcipher3/_sqlite3.pyd',
            f'/LIBPATH:{self.root}/lib',
            f'/LIBPATH:{self.python_root}/libs',
            '/EXPORT:PyInit__sqlite3',
            *obj_files,
            'libcrypto.lib', 'libssl.lib',
            'ws2_32.lib', 'advapi32.lib', 'crypt32.lib', 'user32.lib', 'gdi32.lib'
        ]
        
        result = subprocess.run(cmd_link, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ Link failed:\n{result.stderr}")
            sys.exit(1)
        
        print("   ✅ Linking complete")
    
    def step6_test(self):
        """Quick test"""
        print("🧪 Step 6: Testing...")
        
        os.add_dll_directory(str(self.openssl_root / 'bin'))
        
        from sqlcipher3 import dbapi2 as sqlite
        
        conn = sqlite.connect(':memory:')
        conn.execute("PRAGMA key = 'test'")
        
        cipher_ver = conn.execute("PRAGMA cipher_version").fetchone()[0]
        status = conn.execute("PRAGMA cipher_status").fetchone()[0]
        
        if status != '1':
            print(f"   ❌ Encryption not active: {status}")
            sys.exit(1)
        
        print(f"   ✅ SQLCipher {cipher_ver} certified!")
    
    def build(self):
        """Run full build"""
        print("="*60)
        print("🛡️  SQLCIPHER AUTO-BUILD FOR WINDOWS")
        print("="*60 + "\n")
        
        try:
            self.step1_clean()
            self.step2_copy_openssl()
            self.step3_inject_headers()
            self.step4_compile()
            self.step5_link()
            self.step6_test()
            
            print("\n" + "="*60)
            print("🎉 BUILD SUCCESSFUL!")
            print("="*60)
            print("\n📦 Next: python package_sqlcipher.py")
            
        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    builder = SQLCipherBuilder()
    builder.build()
```

---

## 📋 CHECKLIST TRƯỚC KHI BUILD

### Môi trường
- [ ] Visual Studio 2022 với C++ Desktop Development
- [ ] OpenSSL 3.x 64-bit installed
- [ ] Python 3.14 (hoặc target version)
- [ ] Developer Command Prompt opened
- [ ] Virtual environment activated

### Files cần thiết
- [ ] `sqlite3.c` (từ SQLCipher source)
- [ ] `src/*.c` (Python wrapper files)
- [ ] `setup.py` (reference, không bắt buộc)

### Biến môi trường
```cmd
:: Check these
echo %INCLUDE%
echo %LIB%
echo %PATH%
```

---

## 🎯 KẾT LUẬN

### Thời gian so sánh

| Giai đoạn | Không kinh nghiệm | Có tài liệu này | Tiết kiệm |
|-----------|-------------------|-----------------|-----------|
| Setup môi trường | 30 phút | 5 phút | 25 phút |
| Debug OpenSSL | 1 giờ | 0 phút | 1 giờ |
| Fix C11 errors | 1.5 giờ | 3 phút | 1.5 giờ |
| Fix linker errors | 1 giờ | 5 phút | 55 phút |
| Manual build | 1 giờ | 15 phút | 45 phút |
| Test & verify | 30 phút | 5 phút | 25 phút |
| **TỔNG** | **5.5 giờ** | **33 phút** | **5 giờ** |

### Bài học lớn nhất

> **"Đừng tin setup.py mù quáng. Hiểu từng bước build, kiểm soát từng flag, và document mọi thứ."**

### Giá trị tài liệu này

- 💰 **ROI:** 10x (1 giờ viết doc = 10 giờ tiết kiệm cho team)
- 🎓 **Educational:** Hiểu sâu về Windows compilation
- 🚀 **Productivity:** Team có thể rebuild bất cứ lúc nào
- 🏆 **Quality:** Zero-error builds

---

**Lưu ý cuối:** Luôn test với `PRAGMA cipher_version` và `PRAGMA cipher_status` để xác nhận encryption hoạt động!

**Document Version:** 1.0  
**Last Updated:** 2025-12-29  
**Maintained By:** Convert Desktop Team

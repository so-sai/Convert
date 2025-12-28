# 🎯 QUICK START: SQLCIPHER 4.12.0 DEPLOYMENT

> **For:** Development team members who need to use the pre-built SQLCipher  
> **Time:** 5 minutes  
> **Difficulty:** Easy

---

## 📦 INSTALLATION (Choose One Method)

### Method 1: Install from Wheel (Recommended)

```bash
# Navigate to project directory
cd e:\DEV\app-desktop-Convert\sqlcipher3

# Install the wheel
pip install dist\sqlcipher3-binary-4.12.0-cp314-cp314-win_amd64.whl
```

### Method 2: Install from Source (If wheel not available)

```bash
cd e:\DEV\app-desktop-Convert\sqlcipher3
pip install -e .
```

---

## ✅ VERIFICATION

Run the test script to verify installation:

```bash
cd e:\DEV\app-desktop-Convert\sqlcipher3
python test_wheel_install.py
```

**Expected Output:**
```
🛡️  SQLCIPHER WHEEL INSTALLATION TEST
============================================================

🧪 Test 1: Import module...
   ✅ Import successful
🧪 Test 2: Create encrypted database...
   ✅ Connection successful
🧪 Test 3: Verify encryption...
   ✅ Encryption active: ('1',)
🧪 Test 4: Check versions...
   ✅ SQLCipher: 4.12.0 community
   ✅ SQLite: 3.51.1
🧪 Test 5: Test FTS5...
   ✅ FTS5 working: ('Test', 'Full-text search test')
🧪 Test 6: Test CRUD operations...
   ✅ CRUD operations successful

============================================================
🎉 ALL TESTS PASSED!
   SQLCipher 4.12.0 is fully operational
============================================================
```

---

## 💻 BASIC USAGE

### Example 1: Create Encrypted Database

```python
import os
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")

from sqlcipher3 import dbapi2 as sqlite

# Create encrypted database
conn = sqlite.connect('my_secure_data.db')
conn.execute("PRAGMA key = 'my-secret-password-123'")

# Use like normal SQLite
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute("INSERT INTO users (name) VALUES ('Alice')")
conn.commit()

# Query data
for row in conn.execute("SELECT * FROM users"):
    print(row)

conn.close()
```

### Example 2: Full-Text Search with FTS5

```python
import os
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")

from sqlcipher3 import dbapi2 as sqlite

conn = sqlite.connect('documents.db')
conn.execute("PRAGMA key = 'search-key-456'")

# Create FTS5 table
conn.execute("""
    CREATE VIRTUAL TABLE documents USING fts5(
        title,
        content,
        tags
    )
""")

# Insert documents
conn.execute("""
    INSERT INTO documents VALUES 
    ('Project Plan', 'Q1 2025 roadmap for desktop app', 'planning,2025'),
    ('Meeting Notes', 'Sprint 6 retrospective discussion', 'meeting,sprint6')
""")

# Search
results = conn.execute("""
    SELECT title, content FROM documents 
    WHERE documents MATCH 'sprint6'
""").fetchall()

for title, content in results:
    print(f"{title}: {content}")

conn.close()
```

---

## ⚠️ IMPORTANT NOTES

### 1. OpenSSL DLL Requirement

**Always add this at the start of your script:**
```python
import os
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")
```

**Why?** SQLCipher needs OpenSSL DLLs for encryption. This tells Python where to find them.

### 2. Password Security

```python
# ❌ BAD: Hardcoded password
conn.execute("PRAGMA key = 'password123'")

# ✅ GOOD: Use environment variable
import os
password = os.getenv('DB_PASSWORD')
conn.execute(f"PRAGMA key = '{password}'")

# ✅ BETTER: Use keyring library
import keyring
password = keyring.get_password('myapp', 'database')
conn.execute(f"PRAGMA key = '{password}'")
```

### 3. File Encryption Verification

```python
# Check if database is encrypted
conn = sqlite.connect('test.db')
conn.execute("PRAGMA key = 'mypassword'")

# Verify encryption is active
status = conn.execute("PRAGMA cipher_status").fetchone()
if status[0] == '1':
    print("✅ Database is encrypted")
else:
    print("❌ Database is NOT encrypted!")
```

---

## 🔧 TROUBLESHOOTING

### Problem: `ImportError: DLL load failed`

**Solution:**
```python
# Add OpenSSL DLL directory BEFORE importing
import os
os.add_dll_directory(r"C:\Program Files\OpenSSL-Win64\bin")

# Then import
from sqlcipher3 import dbapi2 as sqlite
```

### Problem: `sqlite3.DatabaseError: file is not a database`

**Cause:** Wrong password or database is corrupted

**Solution:**
```python
# Try with correct password
conn = sqlite.connect('encrypted.db')
conn.execute("PRAGMA key = 'correct-password'")

# Test if it works
try:
    conn.execute("SELECT count(*) FROM sqlite_master")
    print("✅ Password correct!")
except:
    print("❌ Wrong password or corrupted database")
```

### Problem: Wheel installation fails

**Solution:**
```bash
# Ensure you're using Python 3.14
python --version  # Should show 3.14.x

# Force reinstall
pip install dist\*.whl --force-reinstall --no-cache-dir
```

---

## 📚 NEXT STEPS

1. ✅ **Read the Build Manifesto** - `docs/BUILD_GUIDES/SQLCIPHER_BUILD_MANIFESTO.md`
2. ✅ **Check Packaging Guide** - `docs/BUILD_GUIDES/SQLCIPHER_PACKAGING_GUIDE.md`
3. ✅ **Integrate into your app** - Use the examples above
4. ✅ **Test with real data** - Start small, then scale up

---

## 🆘 SUPPORT

**Questions?** Contact the Convert Desktop Team

**Issues?** Check the build manifesto for detailed troubleshooting

**Feature Requests?** Submit to the project backlog

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-29  
**Status:** Production-Ready ✅

"""
Smoke Test - Verify SQLCipher Core Integrity After Cleanup
Quick verification that the binary and wrappers are functional
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.join(os.path.abspath("."), "sqlcipher3"))

# Add OpenSSL DLL directory (required on Windows)
openssl_paths = [
    r"C:\Program Files\OpenSSL-Win64\bin",
    r"C:\OpenSSL-Win64\bin",
]
for path in openssl_paths:
    if os.path.exists(path):
        os.add_dll_directory(path)
        break

def run_smoke_test():

    """Execute smoke test to verify SQLCipher functionality"""
    
    print("="*60)
    print("🧪 SMOKE TEST - SQLCIPHER CORE INTEGRITY")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import
    print("\n1️⃣  Testing Import...")
    try:
        from sqlcipher3 import dbapi2 as sqlite3
        print(f"   ✅ Import OK")
        print(f"   📋 SQLite Version: {sqlite3.sqlite_version}")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ FAILED: {e}")
        print("   → Solution: Copy _sqlite3.pyd from backup")
        tests_failed += 1
        return
    
    # Test 2: Basic Connection
    print("\n2️⃣  Testing In-Memory Connection...")
    try:
        conn = sqlite3.connect(":memory:")
        print("   ✅ Connection OK")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        tests_failed += 1
        return
    
    # Test 3: Encryption (CRITICAL)
    print("\n3️⃣  Testing Encryption (PRAGMA key)...")
    try:
        conn.execute("PRAGMA key = 'test_secret_key_sprint6'")
        print("   ✅ Encryption Key Set")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        tests_failed += 1
    
    # Test 4: Cipher Version
    print("\n4️⃣  Testing Cipher Version...")
    try:
        ver = conn.execute("PRAGMA cipher_version").fetchone()
        if ver and ver[0]:
            print(f"   ✅ Cipher Version: {ver[0]}")
            tests_passed += 1
        else:
            print("   ⚠️  No cipher version (may be standard SQLite)")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        tests_failed += 1
    
    # Test 5: Create Table
    print("\n5️⃣  Testing Table Creation...")
    try:
        conn.execute("CREATE TABLE smoke_test (id INTEGER PRIMARY KEY, mission TEXT)")
        print("   ✅ Table Created")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        tests_failed += 1
    
    # Test 6: Insert Data
    print("\n6️⃣  Testing Data Insert...")
    try:
        conn.execute("INSERT INTO smoke_test VALUES (1, 'Task 6.5 Complete')")
        conn.execute("INSERT INTO smoke_test VALUES (2, 'Sprint 6 Victory')")
        conn.commit()
        print("   ✅ Data Inserted")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        tests_failed += 1
    
    # Test 7: Read Data
    print("\n7️⃣  Testing Data Retrieval...")
    try:
        cursor = conn.execute("SELECT * FROM smoke_test")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   📋 Row: {row}")
        print("   ✅ Data Retrieved")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        tests_failed += 1
    
    # Test 8: FTS5 (Full-Text Search)
    print("\n8️⃣  Testing FTS5 (Full-Text Search)...")
    try:
        conn.execute("CREATE VIRTUAL TABLE fts_test USING fts5(content)")
        conn.execute("INSERT INTO fts_test VALUES ('SQLCipher encryption success')")
        result = conn.execute("SELECT * FROM fts_test WHERE fts_test MATCH 'encryption'").fetchone()
        if result:
            print(f"   ✅ FTS5 Working: {result}")
            tests_passed += 1
        else:
            print("   ⚠️  FTS5 query returned no results")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FTS5 FAILED: {e}")
        tests_failed += 1
    
    # Cleanup
    conn.close()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SMOKE TEST RESULTS")
    print("="*60)
    print(f"\n✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 PHÁO ĐÀI HOẠT ĐỘNG HOÀN HẢO!")
        print("🚀 READY FOR SPRINT 7!")
        print("🍻 CHÚC MỪNG SẾP - TASK 6.5 COMPLETE!")
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        print("   → Restore from E:/SQLCIPHER_VICTORY_PACK/ if needed")
    
    print("\n" + "="*60)
    
    return tests_failed == 0

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)

"""
Repository Density Audit - Analyze file distribution by folder
Adheres to ARCH_PRIME Constitution: Python-only analysis

Provides detailed breakdown of:
- File count per top-level directory
- Identification of bloated directories
- Detection of source code artifacts that should be removed
"""

import subprocess
from collections import Counter, defaultdict
from pathlib import Path

def audit_density():
    """Audit repository file density by directory"""
    
    print("="*60)
    print("🧐 REPOSITORY DENSITY AUDIT")
    print("="*60)
    
    # Get all tracked files
    result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Error: Could not run git ls-files")
        return
    
    files = result.stdout.strip().splitlines()
    total = len(files)
    
    print(f"\n📊 Total tracked files: {total}")
    
    # Count by top-level directory
    top_level = Counter()
    sub_level = defaultdict(Counter)
    
    for f in files:
        parts = f.split('/')
        top = parts[0] if len(parts) > 1 else 'ROOT'
        top_level[top] += 1
        
        # Track second-level for deeper analysis
        if len(parts) > 2:
            sub = f"{parts[0]}/{parts[1]}"
            sub_level[top][sub] += 1
    
    # Display top-level analysis
    print("\n" + "-"*60)
    print("📁 TOP-LEVEL DIRECTORY ANALYSIS")
    print("-"*60)
    
    categories = {
        'GOLD': [],      # Core logic
        'DOCS': [],      # Documentation (expected to be large)
        'TESTS': [],     # Test files
        'SUSPECT': [],   # Potential bloat
        'ROOT': [],      # Root files
    }
    
    for folder, count in top_level.most_common():
        percentage = (count / total) * 100
        
        # Categorize
        if folder == 'docs':
            status = "📚 DOCS"
            categories['DOCS'].append((folder, count))
        elif folder == 'tests':
            status = "🧪 TESTS"
            categories['TESTS'].append((folder, count))
        elif folder in ['src', 'src-tauri', 'src-ui', 'tools', 'scripts']:
            status = "🔥 GOLD"
            categories['GOLD'].append((folder, count))
        elif folder == 'sqlcipher3':
            status = "⚠️ CHECK" if count > 15 else "✅ OK"
            categories['SUSPECT'].append((folder, count))
        elif folder == 'ROOT':
            status = "📄 CONFIG"
            categories['ROOT'].append((folder, count))
        else:
            status = "❓ OTHER"
            categories['SUSPECT'].append((folder, count))
        
        print(f"   {folder:20} {count:4} files ({percentage:5.1f}%) [{status}]")
    
    # SQLCipher deep dive if present
    if 'sqlcipher3' in top_level:
        sqlcipher_files = [f for f in files if f.startswith('sqlcipher3/')]
        print("\n" + "-"*60)
        print("🔍 SQLCIPHER DEEP ANALYSIS")
        print("-"*60)
        
        sqlcipher_subdirs = Counter()
        for f in sqlcipher_files:
            parts = f.split('/')
            if len(parts) > 1:
                subdir = parts[1]
                sqlcipher_subdirs[subdir] += 1
        
        for subdir, count in sqlcipher_subdirs.most_common():
            if subdir in ['src', 'include', 'lib', 'ext', 'tests']:
                status = "❌ RÁC - SHOULD DELETE"
            elif subdir == 'sqlcipher3':
                status = "✅ STRATEGIC"
            else:
                status = "❓ CHECK"
            print(f"   sqlcipher3/{subdir:15} {count:4} files [{status}]")
    
    # Summary
    print("\n" + "="*60)
    print("📋 AUDIT SUMMARY")
    print("="*60)
    
    gold_count = sum(c for _, c in categories['GOLD'])
    docs_count = sum(c for _, c in categories['DOCS'])
    tests_count = sum(c for _, c in categories['TESTS'])
    
    print(f"\n🔥 Core Logic:     {gold_count:4} files")
    print(f"📚 Documentation:  {docs_count:4} files")
    print(f"🧪 Tests:          {tests_count:4} files")
    print(f"📄 Root Config:    {sum(c for _, c in categories['ROOT']):4} files")
    
    # Calculate clean target
    core_files = gold_count + tests_count + 20  # +20 for config
    
    print(f"\n🎯 TARGET ANALYSIS:")
    print(f"   • Code-only target:  ~{core_files} files (without docs)")
    print(f"   • Full project:      ~{core_files + docs_count} files (with docs)")
    print(f"   • Current total:      {total} files")
    
    # Recommendations
    print("\n📝 RECOMMENDATIONS:")
    
    sqlcipher_count = top_level.get('sqlcipher3', 0)
    if sqlcipher_count > 15:
        print(f"   ⚠️  sqlcipher3/ has {sqlcipher_count} files (should be ~10)")
        print("      → Run: python tools/nuclear_purge.py")
    else:
        print(f"   ✅ sqlcipher3/ is clean ({sqlcipher_count} files)")
    
    if docs_count > 100:
        print(f"   📚 docs/ is large ({docs_count} files) - This is NORMAL for well-documented projects")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    audit_density()

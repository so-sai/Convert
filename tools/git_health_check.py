"""
Git Repository Health Check
Analyzes repository cleanliness and identifies remaining artifacts

Adheres to ARCH_PRIME Constitution:
- No shell commands for logic processing
- Python-native subprocess for Git queries
- Clear reporting with actionable insights
"""

import subprocess
from pathlib import Path
from collections import defaultdict

class RepoHealthChecker:
    """Analyzes Git repository health and cleanliness"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.files = []
        self.stats = defaultdict(int)
    
    def check(self):
        """Run comprehensive health check"""
        print("="*60)
        print("🏥 GIT REPOSITORY HEALTH CHECK")
        print("="*60)
        
        self._load_tracked_files()
        self._analyze_distribution()
        self._check_sqlcipher_density()
        self._check_strategic_assets()
        self._print_summary()
    
    def _load_tracked_files(self):
        """Load all Git-tracked files"""
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        self.files = result.stdout.strip().split('\n')
        print(f"\n📊 Total tracked files: {len(self.files)}")
    
    def _analyze_distribution(self):
        """Analyze file distribution by category"""
        print("\n📁 File Distribution:")
        
        categories = {
            'docs': 0,
            'sqlcipher3': 0,
            'src': 0,
            'tests': 0,
            'tools': 0,
            'config': 0,
            'other': 0
        }
        
        for file in self.files:
            if file.startswith('docs/'):
                categories['docs'] += 1
            elif file.startswith('sqlcipher3/'):
                categories['sqlcipher3'] += 1
            elif file.startswith('src/'):
                categories['src'] += 1
            elif file.startswith('tests/'):
                categories['tests'] += 1
            elif file.startswith('tools/'):
                categories['tools'] += 1
            elif any(file.endswith(ext) for ext in ['.toml', '.txt', '.ini', '.yaml', '.json', '.md']):
                categories['config'] += 1
            else:
                categories['other'] += 1
        
        for category, count in sorted(categories.items(), key=lambda x: -x[1]):
            percentage = (count / len(self.files)) * 100
            print(f"   {category:12} {count:4} files ({percentage:5.1f}%)")
        
        self.stats = categories
    
    def _check_sqlcipher_density(self):
        """Check SQLCipher directory for source code artifacts"""
        print("\n🔍 SQLCipher Directory Analysis:")
        
        sqlcipher_files = [f for f in self.files if f.startswith('sqlcipher3/')]
        
        # Categorize SQLCipher files
        source_files = []
        binary_files = []
        python_files = []
        script_files = []
        
        for file in sqlcipher_files:
            if file.endswith(('.c', '.h', '.obj', '.lib', '.d')):
                source_files.append(file)
            elif file.endswith('.pyd'):
                binary_files.append(file)
            elif file.endswith('.py') and not file.endswith(('package_sqlcipher.py', 'test_wheel_install.py', 'auto_build_sqlcipher.py')):
                python_files.append(file)
            elif file.endswith('.py'):
                script_files.append(file)
        
        print(f"   Total: {len(sqlcipher_files)} files")
        print(f"   ├─ Binary assets (.pyd): {len(binary_files)}")
        print(f"   ├─ Python wrappers: {len(python_files)}")
        print(f"   ├─ Build scripts: {len(script_files)}")
        print(f"   └─ ⚠️  Source artifacts (.c/.h/.obj): {len(source_files)}")
        
        if source_files:
            print("\n   🚨 WARNING: Source code artifacts detected!")
            print("   These should NOT be in Git:")
            for file in source_files[:5]:
                print(f"      • {file}")
            if len(source_files) > 5:
                print(f"      ... and {len(source_files) - 5} more")
        
        # Expected clean state
        expected_files = {
            'sqlcipher3/sqlcipher3/_sqlite3.pyd',
            'sqlcipher3/sqlcipher3/__init__.py',
            'sqlcipher3/sqlcipher3/dbapi2.py',
            'sqlcipher3/sqlcipher3/dump.py',
            'sqlcipher3/package_sqlcipher.py',
            'sqlcipher3/test_wheel_install.py',
            'sqlcipher3/auto_build_sqlcipher.py',
        }
        
        actual_strategic = set(f for f in sqlcipher_files if f in expected_files)
        
        print(f"\n   ✅ Strategic assets present: {len(actual_strategic)}/{len(expected_files)}")
        
        if len(sqlcipher_files) > len(expected_files):
            print(f"\n   ⚠️  RECOMMENDATION: Clean up {len(sqlcipher_files) - len(expected_files)} extra files")
            print("   Run: git rm -rf --cached sqlcipher3/src sqlcipher3/include sqlcipher3/lib")
    
    def _check_strategic_assets(self):
        """Verify critical assets are present"""
        print("\n🛡️  Strategic Assets Check:")
        
        critical_assets = {
            'sqlcipher3/sqlcipher3/_sqlite3.pyd': 'SQLCipher binary',
            'docs/BUILD_GUIDES/SQLCIPHER_BUILD_MANIFESTO.md': 'Build documentation',
            'tools/cleanup.py': 'Cleanup utility',
        }
        
        for asset, description in critical_assets.items():
            if asset in self.files:
                # Check file size
                file_path = Path(asset)
                if file_path.exists():
                    size = file_path.stat().st_size
                    if size > 0:
                        print(f"   ✅ {description}: {size:,} bytes")
                    else:
                        print(f"   ⚠️  {description}: Empty file!")
                else:
                    print(f"   ⚠️  {description}: Tracked but missing!")
            else:
                print(f"   ❌ {description}: NOT TRACKED")
    
    def _print_summary(self):
        """Print health summary and recommendations"""
        print("\n" + "="*60)
        print("📋 HEALTH SUMMARY")
        print("="*60)
        
        total = len(self.files)
        sqlcipher_count = self.stats['sqlcipher3']
        
        # Determine health status
        if total < 200:
            status = "🟢 EXCELLENT"
            message = "Repository is extremely clean!"
        elif total < 400:
            status = "🟡 GOOD"
            message = "Repository is reasonably clean"
        elif total < 600:
            status = "🟠 FAIR"
            message = "Repository has some bloat"
        else:
            status = "🔴 NEEDS CLEANUP"
            message = "Repository contains significant artifacts"
        
        print(f"\nStatus: {status}")
        print(f"Message: {message}")
        print(f"\nTotal files: {total}")
        
        # Recommendations
        print("\n📝 RECOMMENDATIONS:")
        
        if sqlcipher_count > 10:
            print("   1. ⚠️  Clean SQLCipher source artifacts:")
            print("      git rm -rf --cached sqlcipher3/src")
            print("      git rm -rf --cached sqlcipher3/include")
            print("      git rm -rf --cached sqlcipher3/lib")
            print("      git add sqlcipher3/sqlcipher3/*.pyd")
            print("      git add sqlcipher3/*.py")
        
        if total > 600:
            print("   2. ⚠️  Review and remove unnecessary documentation")
        
        if sqlcipher_count <= 10 and total < 400:
            print("   ✅ Repository is Sprint 7 ready!")
            print("   ✅ No cleanup needed")
        
        print("\n" + "="*60)

def main():
    """Main entry point"""
    checker = RepoHealthChecker()
    checker.check()

if __name__ == "__main__":
    main()

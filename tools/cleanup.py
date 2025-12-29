"""
Project Cleanup Utility
Removes build artifacts and temporary files safely on Windows

Adheres to ARCH_PRIME Constitution:
- No shell commands (find, rm)
- Uses pathlib for cross-platform safety
- Handles Windows file locks gracefully
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Set, List

class ProjectCleaner:
    """Safe cleanup utility for Windows development environment"""
    
    # Directories to remove
    TARGET_DIRS = {
        "target",           # Rust build artifacts
        "node_modules",     # Node.js dependencies
        "__pycache__",      # Python bytecode cache
        "build",            # Python/C build artifacts
        "dist",             # Distribution packages
        ".pytest_cache",    # Pytest cache
        ".mypy_cache",      # MyPy type checker cache
    }
    
    # File patterns to remove
    TARGET_PATTERNS = {
        "*.pyc",           # Python bytecode
        "*.pyo",           # Optimized bytecode
        "*.obj",           # MSVC object files
        "*.pdb",           # MSVC debug symbols
        "*.exp",           # MSVC export files
        "*.ilk",           # MSVC incremental link files
        "*.egg-info",      # Python egg metadata
    }
    
    def __init__(self, project_root: Path = None):
        """Initialize cleaner with project root"""
        if project_root is None:
            # Auto-detect: go up from tools/ to project root
            self.root = Path(__file__).parent.parent.resolve()
        else:
            self.root = Path(project_root).resolve()
        
        self.removed_count = 0
        self.locked_files: List[Path] = []
        self.errors: List[tuple] = []
    
    def clean(self) -> dict:
        """Execute cleanup and return statistics"""
        print("="*60)
        print("🧹 PROJECT CLEANUP UTILITY")
        print("="*60)
        print(f"\n📁 Project root: {self.root}")
        print(f"🎯 Targets: {', '.join(self.TARGET_DIRS)}")
        print("\n" + "-"*60)
        
        # Clean directories
        self._clean_directories()
        
        # Clean file patterns
        self._clean_file_patterns()
        
        # Print summary
        self._print_summary()
        
        return {
            "removed": self.removed_count,
            "locked": len(self.locked_files),
            "errors": len(self.errors)
        }
    
    def _clean_directories(self):
        """Remove target directories"""
        print("\n🗂️  Scanning for directories...")
        
        for root, dirs, _ in os.walk(self.root, topdown=False):
            for dirname in dirs:
                if dirname in self.TARGET_DIRS:
                    full_path = Path(root) / dirname
                    self._remove_directory(full_path)
    
    def _clean_file_patterns(self):
        """Remove files matching patterns"""
        print("\n📄 Scanning for file patterns...")
        
        for pattern in self.TARGET_PATTERNS:
            for file_path in self.root.rglob(pattern):
                if file_path.is_file():
                    self._remove_file(file_path)
    
    def _remove_directory(self, path: Path):
        """Safely remove a directory"""
        try:
            # Skip if in .venv or .git
            if '.venv' in path.parts or '.git' in path.parts:
                return
            
            shutil.rmtree(path)
            self.removed_count += 1
            print(f"   ✅ Removed: {path.relative_to(self.root)}")
            
        except PermissionError:
            self.locked_files.append(path)
            print(f"   🔒 Locked: {path.relative_to(self.root)}")
            print(f"      → Process holding lock (likely .venv or IDE)")
            
        except Exception as e:
            self.errors.append((path, str(e)))
            print(f"   ❌ Error: {path.relative_to(self.root)}")
            print(f"      → {e}")
    
    def _remove_file(self, path: Path):
        """Safely remove a file"""
        try:
            # Skip if in .venv or .git
            if '.venv' in path.parts or '.git' in path.parts:
                return
            
            path.unlink()
            self.removed_count += 1
            
        except PermissionError:
            self.locked_files.append(path)
            
        except Exception as e:
            self.errors.append((path, str(e)))
    
    def _print_summary(self):
        """Print cleanup summary"""
        print("\n" + "="*60)
        print("📊 CLEANUP SUMMARY")
        print("="*60)
        print(f"\n✅ Removed: {self.removed_count} items")
        
        if self.locked_files:
            print(f"\n🔒 Locked files: {len(self.locked_files)}")
            print("\n   Common causes:")
            print("   • Active Python virtual environment (.venv)")
            print("   • IDE indexing files (VS Code, PyCharm)")
            print("   • Background compiler processes (MSVC)")
            print("\n   Solutions:")
            print("   1. Deactivate venv: deactivate")
            print("   2. Close IDE")
            print("   3. Kill processes: taskkill /F /IM python.exe")
            
            # Show first 5 locked files
            print("\n   First locked files:")
            for path in self.locked_files[:5]:
                print(f"   • {path.relative_to(self.root)}")
            
            if len(self.locked_files) > 5:
                print(f"   ... and {len(self.locked_files) - 5} more")
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for path, error in self.errors[:3]:
                print(f"   • {path.relative_to(self.root)}: {error}")

def main():
    """Main entry point"""
    cleaner = ProjectCleaner()
    stats = cleaner.clean()
    
    # Exit code based on results
    if stats["locked"] > 0:
        print("\n⚠️  Some files are locked. See solutions above.")
        sys.exit(1)
    elif stats["errors"] > 0:
        print("\n⚠️  Some errors occurred during cleanup.")
        sys.exit(1)
    else:
        print("\n🎉 Cleanup completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()

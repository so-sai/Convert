import subprocess
import sys
import tempfile
from pathlib import Path
import pytest
import os

# Skip if PyInstaller not installed or not running in a context where we can build
pytest.importorskip("PyInstaller")

@pytest.fixture(scope="module")
def bundled_executable():
    """Build PyInstaller bundle once for all tests."""
    # Ensure we are at project root
    project_root = Path(__file__).parent.parent.parent
    spec_file = project_root / "mds-core.spec"
    
    if not spec_file.exists():
        pytest.skip("mds-core.spec not found")

    # Build bundle
    print("Building PyInstaller bundle...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec_file)],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes max
    )
    
    if result.returncode != 0:
        pytest.fail(f"PyInstaller build failed:\n{result.stderr}")
    
    # Locate executable
    dist_dir = project_root / "dist"
    if sys.platform == "win32":
        exe_path = dist_dir / "mds-core.exe"
        if not exe_path.exists():
            exe_path = dist_dir / "mds-core" / "mds-core.exe"
    else:
        exe_path = dist_dir / "mds-core"
        if not exe_path.exists():
            exe_path = dist_dir / "mds-core" / "mds-core"
    
    if not exe_path.exists():
        pytest.fail(f"Executable not found at {exe_path} or {dist_dir / 'mds-core'}")
    
    # Make executable on Unix
    if sys.platform != "win32":
        exe_path.chmod(0o755)
    
    return exe_path

def test_executable_exists(bundled_executable):
    """Verify executable was created."""
    assert bundled_executable.exists()
    # Size check (> 5MB to ensure Python is bundled)
    assert bundled_executable.stat().st_size > 5_000_000 

def test_executable_help(bundled_executable):
    """Verify bundled app starts and prints help."""
    result = subprocess.run(
        [str(bundled_executable), "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    # Should exit cleanly (0 or 1 depending on argparse implementation for --help)
    # Usually 0 for --help
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "options" in result.stdout.lower()

def test_sqlite_version_check(bundled_executable):
    """Verify the internal SQLite check runs."""
    # Assuming main.py runs verify_sqlite_version() on startup
    result = subprocess.run(
        [str(bundled_executable)],
        capture_output=True,
        text=True,
        timeout=10
    )
    # It might exit immediately if no args provided or start a server.
    # If it starts a server, it might timeout. 
    # For this smoke test, we just want to see if it boots.
    # If main.py just prints and exits (as currently implemented in Step 91), it returns 0.
    
    assert result.returncode == 0
    assert "SQLite version verified" in result.stderr or "SQLite version verified" in result.stdout

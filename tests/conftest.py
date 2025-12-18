"""
Pytest configuration and shared fixtures.
"""
import sys
from pathlib import Path

# Add src to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import pytest


@pytest.fixture
def mock_dispatcher_envelope():
    """Sample command envelope for dispatcher tests."""
    return {
        "cmd": "backup.start",
        "payload": {
            "target_dir": "C:\\Users\\Test\\Documents"
        }
    }


@pytest.fixture
def secret_data():
    """Sample secret data for memory safety tests."""
    return b"SUPER_SECRET_KEY_12345678901234567890"

import pytest
import time
from unittest.mock import MagicMock, patch
from src.core.enforcer import windows_lock_retry

@pytest.mark.security
def test_windows_lock_retry_success():
    """Test 2.3.2a: Retry logic succeeds eventually."""
    mock_func = MagicMock()
    
    # Create a proper Windows OSError
    lock_error = OSError(13, "Permission denied")
    lock_error.winerror = 32
    
    # Fail twice with WinError 32, then succeed
    mock_func.side_effect = [lock_error, lock_error, "Success"]
    
    with patch("time.sleep") as mock_sleep:
        result = windows_lock_retry(mock_func, max_retries=5)
    
    assert result == "Success"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2

@pytest.mark.security
def test_windows_lock_retry_failure():
    """Test 2.3.2b: Retry logic gives up after max retries."""
    mock_func = MagicMock()
    
    lock_error = OSError(13, "Permission denied")
    lock_error.winerror = 32
    
    mock_func.side_effect = lock_error
    
    with patch("time.sleep"):
        with pytest.raises(OSError) as excinfo:
            windows_lock_retry(mock_func, max_retries=3)
    
    # Verify the raised exception has the correct code
    assert excinfo.value.winerror == 32
    assert mock_func.call_count == 3

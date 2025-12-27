"""
CONFTEST.PY - Test Infrastructure for Watchdog Contract Tests
Sprint 6.1 - Full 15-Test Suite

Chuẩn bị môi trường test TDD Phase RED.
Tất cả đều là Mock/Stub, không phụ thuộc thực tế.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from datetime import datetime


# -------------------------------------------------------------------
# FIXTURES CORE - Dùng cho toàn bộ test Watchdog
# -------------------------------------------------------------------

@pytest.fixture
def mock_time():
    """Mock hệ thống time để kiểm soát debounce timer"""
    with patch('time.time') as mock_t:
        mock_t.return_value = 1000.0
        yield mock_t


@pytest.fixture
def mock_sleep():
    """Mock time.sleep để test không bị block"""
    with patch('time.sleep') as mock_s:
        yield mock_s


@pytest.fixture
def mock_threading():
    """Mock threading để kiểm soát Timer và Thread"""
    with patch('threading.Timer') as MockTimer:
        mock_timer_instance = MagicMock()
        MockTimer.return_value = mock_timer_instance
        
        with patch('threading.Thread') as MockThread:
            mock_thread_instance = MagicMock()
            MockThread.return_value = mock_thread_instance
            
            yield {
                'Timer': MockTimer,
                'Timer_instance': mock_timer_instance,
                'Thread': MockThread,
                'Thread_instance': mock_thread_instance
            }


@pytest.fixture
def mock_uuid():
    """Mock uuid để kiểm soát batch_id"""
    with patch('uuid.uuid4') as mock_u:
        mock_u.return_value = MagicMock(
            __str__=lambda self: '123e4567-e89b-12d3-a456-426614174000'
        )
        yield mock_u


@pytest.fixture
def mock_os_path():
    """Mock os.path để fake filesystem operations"""
    with patch('os.path.exists') as mock_exists:
        with patch('os.path.normpath') as mock_normpath:
            mock_exists.return_value = True
            mock_normpath.side_effect = lambda x: x.replace('\\', '/')
            yield {
                'exists': mock_exists,
                'normpath': mock_normpath
            }


@pytest.fixture
def mock_watchdog_lib():
    """Mock thư viện watchdog.observers (nếu có dùng)"""
    with patch('watchdog.observers.Observer') as MockObserver:
        mock_observer_instance = MagicMock()
        MockObserver.return_value = mock_observer_instance
        
        with patch('watchdog.events.FileSystemEventHandler') as MockEventHandler:
            yield {
                'Observer': MockObserver,
                'Observer_instance': mock_observer_instance,
                'EventHandler': MockEventHandler
            }


@pytest.fixture
def sample_source_path():
    """Đường dẫn nguồn test tiêu chuẩn (POSIX format)"""
    return "C:/Users/Test/Notes"


@pytest.fixture
def sample_debounce_ms():
    """Thời gian debounce mặc định"""
    return 300


@pytest.fixture
def batch_callback():
    """Callback giả lập cho consumer (Queue/Indexer)"""
    return Mock()


@pytest.fixture
def valid_event_schema():
    """Schema chuẩn của FileBatchEvent (theo Contract)"""
    return {
        "event_type": "BATCH_CHANGED",
        "batch_id": "uuid-v4-string",
        "timestamp": 1735281000.500,
        "source_path": "C:/Users/Test/Notes",
        "changes": {
            "created": [],
            "modified": [],
            "deleted": []
        },
        "meta": {
            "debounce_ms": 300,
            "total_items": 0
        }
    }


@pytest.fixture
def file_sequence_events():
    """Chuỗi sự kiện file test cho dedup logic"""
    return [
        {"type": "created", "path": "C:/Users/Test/Notes/note1.md"},
        {"type": "modified", "path": "C:/Users/Test/Notes/note1.md"},
        {"type": "deleted", "path": "C:/Users/Test/Notes/note1.md"},
        {"type": "created", "path": "C:/Users/Test/Notes/note2.md"},
        {"type": "created", "path": "C:/Users/Test/Notes/image.png"}
    ]


# -------------------------------------------------------------------
# FIXTURES ADVANCED - Cho test case phức tạp
# -------------------------------------------------------------------

@pytest.fixture
def high_load_sequence():
    """Tạo 5001 sự kiện liên tiếp để test max_batch_size"""
    events = []
    for i in range(5001):
        events.append({
            "type": "created",
            "path": f"C:/Users/Test/Notes/file_{i:04d}.md"
        })
    return events


# -------------------------------------------------------------------
# TEST CONFIGURATION
# -------------------------------------------------------------------

def pytest_configure(config):
    """Cấu hình pytest cho Watchdog tests"""
    config.addinivalue_line(
        "markers",
        "watchdog_contract: Test thuộc Contract spec"
    )
    config.addinivalue_line(
        "markers", 
        "watchdog_debounce: Test debounce logic"
    )
    config.addinivalue_line(
        "markers",
        "watchdog_lifecycle: Test stop() resilience"
    )
    config.addinivalue_line(
        "markers",
        "watchdog_ordering: Test ordering guarantees"
    )

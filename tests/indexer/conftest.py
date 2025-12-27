"""
CONFTEST.PY - Test Infrastructure for Indexer Queue Tests
Sprint 6.3 - IndexerQueue Core

Fixtures for TDD testing of IndexerQueue.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, MagicMock


# -------------------------------------------------------------------
# FIXTURES CORE - Dùng cho toàn bộ test IndexerQueue
# -------------------------------------------------------------------

@pytest.fixture
def temp_db_path():
    """Tạo temp DB path cho mỗi test"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_indexer_queue.db")
    yield db_path
    # Cleanup
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except:
        pass


@pytest.fixture
def mock_eventbus():
    """Mock EventBus cho integration testing"""
    mock_bus = MagicMock()
    mock_bus.subscribe.return_value = "mock-subscription-id"
    mock_bus.is_running = True
    return mock_bus


@pytest.fixture
def sample_file_event():
    """Sample event từ Watchdog/EventBus"""
    return {
        "event_id": "123e4567-e89b-12d3-a456-426614174000",
        "batch_id": "watchdog-batch-001",
        "timestamp": 1735300000.0,
        "event": {
            "type": "BATCH_CHANGED",
            "changes": {
                "created": ["file1.md", "file2.md"],
                "modified": [],
                "deleted": []
            }
        },
        "source": "watchdog"
    }


@pytest.fixture
def sample_events_batch():
    """Batch 100 events để test threshold"""
    events = []
    for i in range(100):
        events.append({
            "event_id": f"event-{i:05d}",
            "batch_id": f"batch-{i // 10:03d}",
            "timestamp": 1735300000.0 + i,
            "data": f"file_{i}.md"
        })
    return events


@pytest.fixture
def high_volume_events():
    """10K events cho performance testing"""
    events = []
    for i in range(10000):
        events.append({
            "event_id": f"perf-event-{i:06d}",
            "batch_id": f"perf-batch-{i // 100:04d}",
            "timestamp": 1735300000.0 + (i * 0.0001),
            "data": f"perf_file_{i}.md"
        })
    return events


# -------------------------------------------------------------------
# PYTEST CONFIGURATION
# -------------------------------------------------------------------

def pytest_configure(config):
    """Cấu hình pytest cho IndexerQueue tests"""
    config.addinivalue_line(
        "markers",
        "indexer_core: IndexerQueue core functionality tests"
    )
    config.addinivalue_line(
        "markers", 
        "indexer_performance: IndexerQueue performance tests"
    )
    config.addinivalue_line(
        "markers",
        "indexer_resilience: IndexerQueue resilience and recovery tests"
    )

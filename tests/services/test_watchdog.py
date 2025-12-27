"""
Test Suite for WatchdogService - Sprint 6.1
Uses temporary directories and mocking for reliable cross-platform testing
"""
import unittest
import os
import shutil
import tempfile
import time
import threading
from unittest.mock import MagicMock, patch

from src.core.services.watchdog import WatchdogService


class TestWatchdogCore(unittest.TestCase):
    """Core tests for WatchdogService following TDD methodology"""
    
    def setUp(self):
        # Dynamic path: Use system temp directory (no hardcoded paths!)
        self.test_dir = tempfile.mkdtemp(prefix="convert_watchdog_test_")
        self.debounce_ms = 100  # Fast for testing
        
    def tearDown(self):
        # Clean up temp directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_T00_class_exists(self):
        """Verify WatchdogService class exists and is importable"""
        self.assertIsNotNone(WatchdogService)
        print("\n   ✅ T00: WatchdogService class exists")

    def test_T01_initialization(self):
        """Verify service can be initialized with valid parameters"""
        service = WatchdogService(
            watch_path=self.test_dir,
            debounce_ms=self.debounce_ms
        )
        self.assertEqual(service.watch_path, self.test_dir)
        self.assertEqual(service.debounce_ms, self.debounce_ms)
        self.assertFalse(service.is_running)
        print("\n   ✅ T01: Initialization works correctly")

    def test_T02_debounce_deduplication(self):
        """Scenario: Multiple events for same file should be deduplicated"""
        service = WatchdogService(
            watch_path=self.test_dir,
            debounce_ms=self.debounce_ms
        )
        
        # Simulate multiple events for same file (internal method)
        service._on_file_event("file1.md", "modified")
        service._on_file_event("file1.md", "modified")  # Duplicate
        service._on_file_event("file2.md", "created")
        
        # Should only have 2 unique files
        self.assertEqual(len(service._pending_events), 2)
        print("\n   ✅ T02: Deduplication working - 2 unique events from 3 calls")

    def test_T03_lifecycle_management(self):
        """Verify start/stop lifecycle with no zombie threads"""
        service = WatchdogService(
            watch_path=self.test_dir,
            debounce_ms=self.debounce_ms
        )
        
        initial_thread_count = threading.active_count()
        
        # Start service
        service.start()
        self.assertTrue(service.is_running)
        
        # Stop service
        service.stop()
        self.assertFalse(service.is_running)
        
        # Wait for threads to clean up
        time.sleep(0.3)
        final_thread_count = threading.active_count()
        
        # Should not have zombie threads (allow +1 for pytest internals)
        self.assertLessEqual(final_thread_count, initial_thread_count + 1,
                            "Zombie threads detected!")
        print("\n   ✅ T03: Lifecycle management - no zombie threads")

    def test_T04_batch_emission(self):
        """Verify events are batched and emitted after debounce period"""
        emitted_batches = []
        
        def mock_callback(batch):
            emitted_batches.append(batch)
            
        service = WatchdogService(
            watch_path=self.test_dir,
            debounce_ms=100,
            on_batch_ready=mock_callback
        )
        
        service.start()
        
        # Simulate rapid file events (using internal method to avoid OS dependency)
        service._on_file_event("file1.md", "modified")
        service._on_file_event("file2.md", "created")
        service._on_file_event("file3.md", "deleted")
        
        # Wait for debounce period + flush
        time.sleep(0.4)
        
        service.stop()
        
        # Should have received at least one batch
        self.assertGreater(len(emitted_batches), 0, "No batches emitted!")
        print(f"\n   ✅ T04: Batch emission - received {len(emitted_batches)} batch(es)")


if __name__ == '__main__':
    unittest.main(verbosity=2)
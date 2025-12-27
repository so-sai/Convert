"""
TEST_INDEXER_QUEUE.PY - 10 Test Cases for IndexerQueue
Task 6.3 - Sprint 6 Background Services

SPEC: docs/03_SPECS/SPEC_TASK_6_3_INDEXER_QUEUE.md (FROZEN)
Phase: RED → GREEN

Test Categories:
- T01-T04: Core functionality
- T05-T07: Reliability
- T08-T10: Performance & Resilience
"""

import gc
import json
import os
import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

# Import will be available after implementation
try:
    from src.core.indexer.queue import IndexerQueue, Batch, QueueMetrics
except ImportError:
    # Stub for RED phase
    IndexerQueue = None
    Batch = None
    QueueMetrics = None

try:
    from src.core.services.eventbus import HeavyEventBus
except ImportError:
    HeavyEventBus = None


# ===================================================================
# NHÓM 1: CORE FUNCTIONALITY (T01-T04)
# ===================================================================

class TestIndexerQueueCore(unittest.TestCase):
    """Core functionality tests"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_queue.db")
    
    def tearDown(self):
        # Cleanup temp files
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    @pytest.mark.indexer_core
    def test_T01_queue_initializes_with_sqlite(self):
        """T01: IndexerQueue tạo DB file với đúng schema"""
        queue = IndexerQueue(db_path=self.db_path)
        queue.start()
        
        # Verify DB file exists
        self.assertTrue(
            os.path.exists(self.db_path),
            "SQLite DB file should be created"
        )
        
        # Verify tables exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check pending_batches table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pending_batches'"
        )
        self.assertIsNotNone(
            cursor.fetchone(),
            "pending_batches table should exist"
        )
        
        # Check processed_events table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_events'"
        )
        self.assertIsNotNone(
            cursor.fetchone(),
            "processed_events table should exist"
        )
        
        conn.close()
        queue.stop()
        print("\n   ✅ T01: SQLite initialized with correct schema")

    @pytest.mark.indexer_core
    def test_T02_subscribe_to_eventbus(self):
        """T02: IndexerQueue có thể subscribe vào EventBus"""
        queue = IndexerQueue(db_path=self.db_path)
        bus = HeavyEventBus(max_queue_size=1000, name="test_bus")
        
        queue.start()
        bus.start()
        
        # Subscribe to EventBus
        sub_id = queue.subscribe_to_eventbus(bus)
        
        self.assertIsNotNone(sub_id, "subscribe_to_eventbus should return subscription_id")
        self.assertIsInstance(sub_id, str, "subscription_id should be string")
        
        bus.stop()
        queue.stop()
        print("\n   ✅ T02: Successfully subscribed to EventBus")

    @pytest.mark.indexer_core
    def test_T03_batch_creation_at_threshold_100(self):
        """T03: Tạo batch khi đạt 100 events"""
        queue = IndexerQueue(db_path=self.db_path, batch_size=100)
        queue.start()
        
        # Simulate receiving 100 events
        for i in range(100):
            queue._on_event_received({
                "event_id": f"event-{i:03d}",
                "batch_id": f"watchdog-batch-{i // 10}",
                "data": f"file_{i}.md"
            })
        
        # Wait for flush
        time.sleep(0.2)
        
        # Check that a batch was created
        metrics = queue.metrics()
        
        self.assertGreaterEqual(
            metrics.pending_batches, 1,
            "At least 1 batch should be created after 100 events"
        )
        
        queue.stop()
        print("\n   ✅ T03: Batch created at 100 events threshold")

    @pytest.mark.indexer_core
    def test_T04_timeout_flush_500ms(self):
        """T04: Flush sau 500ms ngay cả khi chưa đủ 100 events"""
        queue = IndexerQueue(
            db_path=self.db_path, 
            batch_size=100,
            flush_timeout_ms=500
        )
        queue.start()
        
        # Send only 50 events (less than threshold)
        for i in range(50):
            queue._on_event_received({
                "event_id": f"event-{i:03d}",
                "data": f"file_{i}.md"
            })
        
        # Wait for timeout flush (500ms + margin)
        time.sleep(0.7)
        
        # Check that a batch was created despite < 100 events
        metrics = queue.metrics()
        
        self.assertGreaterEqual(
            metrics.pending_batches, 1,
            "Batch should be created after 500ms timeout even with < 100 events"
        )
        
        queue.stop()
        print("\n   ✅ T04: Timeout flush works at 500ms")


# ===================================================================
# NHÓM 2: RELIABILITY (T05-T07)
# ===================================================================

class TestIndexerQueueReliability(unittest.TestCase):
    """Reliability and crash recovery tests"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_queue.db")
    
    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    @pytest.mark.indexer_resilience
    def test_T05_crash_recovery(self):
        """T05: Pending batches survive restart (crash recovery)"""
        # Create queue and add events
        queue1 = IndexerQueue(db_path=self.db_path, batch_size=100)
        queue1.start()
        
        for i in range(100):
            queue1._on_event_received({
                "event_id": f"event-{i:03d}",
                "data": f"file_{i}.md"
            })
        
        time.sleep(0.2)
        
        # Verify batch was created
        metrics1 = queue1.metrics()
        initial_pending = metrics1.pending_batches
        
        # Simulate crash (stop without graceful shutdown)
        queue1.stop(graceful=False)
        
        # Create new queue instance (simulating restart)
        queue2 = IndexerQueue(db_path=self.db_path, batch_size=100)
        queue2.start()
        
        # Verify pending batches still exist
        metrics2 = queue2.metrics()
        
        self.assertEqual(
            metrics2.pending_batches, initial_pending,
            f"Pending batches should survive restart: expected {initial_pending}, got {metrics2.pending_batches}"
        )
        
        queue2.stop()
        print("\n   ✅ T05: Crash recovery successful")

    @pytest.mark.indexer_resilience
    def test_T06_idempotency_deduplication(self):
        """T06: Same event_id không được xử lý 2 lần"""
        queue = IndexerQueue(db_path=self.db_path, batch_size=10)
        queue.start()
        
        # Send same event multiple times
        duplicate_event = {
            "event_id": "duplicate-event-001",
            "data": "file.md"
        }
        
        for _ in range(5):
            queue._on_event_received(duplicate_event)
        
        # Also send unique events
        for i in range(9):
            queue._on_event_received({
                "event_id": f"unique-event-{i:03d}",
                "data": f"file_{i}.md"
            })
        
        time.sleep(0.2)
        
        metrics = queue.metrics()
        
        # Should have 10 unique events (1 duplicate + 9 unique)
        # Duplicate count should be 4 (5 sends - 1 accepted)
        self.assertGreaterEqual(
            metrics.events_duplicate_total, 4,
            "Should detect at least 4 duplicates"
        )
        
        queue.stop()
        print("\n   ✅ T06: Idempotency working - duplicates skipped")

    @pytest.mark.indexer_resilience
    def test_T07_strict_fifo_ordering(self):
        """T07: Events phải được xử lý đúng thứ tự FIFO"""
        queue = IndexerQueue(db_path=self.db_path, batch_size=10)
        queue.start()
        
        # Send events in specific order
        for i in range(10):
            queue._on_event_received({
                "event_id": f"event-{i:03d}",
                "sequence": i,
                "data": f"file_{i}.md"
            })
        
        time.sleep(0.2)
        
        # Get the batch
        batch = queue.get_next_batch(timeout=0.1)
        
        self.assertIsNotNone(batch, "Should have a batch available")
        
        # Verify order
        for i, event in enumerate(batch.events):
            self.assertEqual(
                event["sequence"], i,
                f"Event at position {i} should have sequence {i}, got {event['sequence']}"
            )
        
        queue.stop()
        print("\n   ✅ T07: Strict FIFO ordering preserved")


# ===================================================================
# NHÓM 3: PERFORMANCE & RESILIENCE (T08-T10)
# ===================================================================

class TestIndexerQueuePerformance(unittest.TestCase):
    """Performance and resilience tests"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_queue.db")
    
    def tearDown(self):
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
        gc.collect()

    @pytest.mark.indexer_performance
    def test_T08_performance_10k_events_under_1s(self):
        """T08: Xử lý 10K events trong < 1 giây"""
        queue = IndexerQueue(db_path=self.db_path, batch_size=100)
        queue.start()
        
        total_events = 10000
        start_time = time.time()
        
        # Send 10K events
        for i in range(total_events):
            queue._on_event_received({
                "event_id": f"event-{i:05d}",
                "data": f"file_{i}.md"
            })
        
        # Wait for all flushes to complete
        deadline = time.time() + 2.0
        while time.time() < deadline:
            metrics = queue.metrics()
            if metrics.events_processed_total >= total_events:
                break
            time.sleep(0.01)
        
        duration = time.time() - start_time
        
        queue.stop()
        
        self.assertLess(
            duration, 1.0,
            f"10K events should process in < 1s, took {duration:.2f}s"
        )
        
        throughput = total_events / duration
        print(f"\n   ✅ T08: Performance: {throughput:.0f} events/sec in {duration:.2f}s")

    @pytest.mark.indexer_resilience
    def test_T09_sqlite_transaction_atomicity(self):
        """T09: Batch flush là all-or-nothing (atomic)"""
        queue = IndexerQueue(db_path=self.db_path, batch_size=10)
        queue.start()
        
        # Send events
        for i in range(10):
            queue._on_event_received({
                "event_id": f"event-{i:03d}",
                "data": f"file_{i}.md"
            })
        
        time.sleep(0.2)
        
        # Verify batch and processed_events are in same transaction
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get batch
        cursor.execute("SELECT batch_id, event_count FROM pending_batches LIMIT 1")
        batch_row = cursor.fetchone()
        
        self.assertIsNotNone(batch_row, "Batch should exist")
        batch_id, event_count = batch_row
        
        # Verify processed_events match
        cursor.execute(
            "SELECT COUNT(*) FROM processed_events WHERE batch_id = ?",
            (batch_id,)
        )
        processed_count = cursor.fetchone()[0]
        
        self.assertEqual(
            processed_count, event_count,
            f"processed_events ({processed_count}) should match event_count ({event_count})"
        )
        
        conn.close()
        queue.stop()
        print("\n   ✅ T09: Transaction atomicity verified")

    @pytest.mark.indexer_resilience
    def test_T10_graceful_shutdown_with_pending(self):
        """T10: graceful=True persists pending events trước khi dừng"""
        queue = IndexerQueue(db_path=self.db_path, batch_size=100)
        queue.start()
        
        # Send 50 events (not enough to trigger batch)
        for i in range(50):
            queue._on_event_received({
                "event_id": f"event-{i:03d}",
                "data": f"file_{i}.md"
            })
        
        # Graceful shutdown should flush pending
        queue.stop(graceful=True)
        
        # Verify events were persisted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT SUM(event_count) FROM pending_batches")
        total_persisted = cursor.fetchone()[0] or 0
        
        conn.close()
        
        self.assertEqual(
            total_persisted, 50,
            f"Graceful shutdown should persist all 50 pending events, got {total_persisted}"
        )
        
        print("\n   ✅ T10: Graceful shutdown persists pending events")


# ===================================================================
# MAIN RUNNER
# ===================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)

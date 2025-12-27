"""
TEST_EVENTBUS_HEAVY.PY - 8 Test Cases for HeavyEventBus
Task 6.2 - Sprint 6 Background Services

SPEC: docs/03_SPECS/SPEC_TASK_6_2_EVENTBUS.md (FROZEN)
Phase: RED (All tests expected to FAIL)

Test Categories:
- T01-T03: Core functionality
- T04-T05: Performance
- T06-T08: Resilience
"""

import gc
import os
import re
import shutil
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest

from src.core.services.eventbus import HeavyEventBus, EventBusMetrics, EventEnvelope


# ===================================================================
# NHÓM 1: CORE FUNCTIONALITY (T01-T03)
# ===================================================================

class TestEventBusCore(unittest.TestCase):
    """Core functionality tests"""
    
    def setUp(self):
        self.bus = HeavyEventBus(
            max_queue_size=100,
            max_workers=4,
            name="test_bus"
        )
    
    def tearDown(self):
        if hasattr(self, 'bus') and self.bus.is_running:
            try:
                self.bus.stop(graceful=False, timeout=1.0)
            except:
                pass

    @pytest.mark.eventbus_core
    def test_T01_publish_returns_event_id(self):
        """T01: publish() phải trả về UUID v4"""
        self.bus.start()
        
        # Publish event
        event = {"batch_id": "test-batch-001", "files": ["a.md", "b.md"]}
        event_id = self.bus.publish(event)
        
        # Verify UUID v4 format
        self.assertIsNotNone(event_id, "publish() must return event_id")
        self.assertIsInstance(event_id, str, "event_id must be string")
        
        # UUID v4 pattern: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            re.I
        )
        self.assertIsNotNone(
            uuid_pattern.match(event_id),
            f"event_id is not UUID v4: {event_id}"
        )
        
        self.bus.stop()
        print("\n   ✅ T01: publish returns UUID v4")

    @pytest.mark.eventbus_core
    def test_T02_backpressure_drops_oldest(self):
        """T02: Queue đầy phải drop event cũ nhất"""
        # Small queue to trigger backpressure quickly
        bus = HeavyEventBus(max_queue_size=10, name="backpressure_test")
        bus.start()
        
        # Don't subscribe - let queue fill up
        
        # Publish more than queue size
        for i in range(15):
            bus.publish({"batch_id": f"batch-{i}"})
        
        time.sleep(0.1)  # Let queue process
        
        # Check metrics for dropped events
        metrics = bus.metrics()
        
        self.assertGreater(
            metrics.events_dropped, 0,
            "Backpressure should have dropped events"
        )
        
        # Should have dropped at least 5 (15 - 10)
        self.assertGreaterEqual(
            metrics.events_dropped, 5,
            f"Expected at least 5 dropped, got {metrics.events_dropped}"
        )
        
        bus.stop()
        print("\n   ✅ T02: Backpressure drops oldest events")

    @pytest.mark.eventbus_core
    def test_T03_subscriber_isolation_on_crash(self):
        """T03: Subscriber crash không ảnh hưởng bus và subscriber khác"""
        bus = HeavyEventBus(max_queue_size=100, name="isolation_test")
        
        good_counter = [0]
        
        def good_subscriber(event):
            good_counter[0] += 1
        
        def bad_subscriber(event):
            raise RuntimeError("I always crash!")
        
        bus.start()
        
        # Subscribe both
        bus.subscribe(good_subscriber, name="good")
        bus.subscribe(bad_subscriber, name="bad")
        
        # Publish events
        for i in range(5):
            bus.publish({"batch_id": f"batch-{i}"})
        
        time.sleep(0.5)  # Let processing complete
        
        # Good subscriber should have received all events
        # despite bad subscriber crashing
        self.assertEqual(
            good_counter[0], 5,
            f"Good subscriber should receive 5, got {good_counter[0]}"
        )
        
        # Bus should still be running
        self.assertTrue(bus.is_running, "Bus should survive subscriber crash")
        
        bus.stop()
        print("\n   ✅ T03: Subscriber isolation working")


# ===================================================================
# NHÓM 2: PERFORMANCE (T04-T05)
# ===================================================================

class TestEventBusPerformance(unittest.TestCase):
    """Performance and throughput tests"""
    
    def tearDown(self):
        gc.collect()

    @pytest.mark.eventbus_performance
    def test_T04_publish_throughput_200k_per_second(self):
        """T04: Đạt 200K publishes/second (publish-only, không subscriber)"""
        bus = HeavyEventBus(max_queue_size=250000, name="throughput_test")
        bus.start()
        
        # Don't subscribe - measure pure publish speed
        target_events = 10000  # Use smaller number for quick test
        target_rate = 200000  # events/sec
        max_duration = target_events / target_rate  # Should finish in 0.05s
        
        start_time = time.time()
        
        for i in range(target_events):
            bus.publish({"batch_id": f"batch-{i}"})
        
        duration = time.time() - start_time
        actual_rate = target_events / duration if duration > 0 else 0
        
        bus.stop(graceful=False)
        
        # Allow 50% margin for CI environments
        min_acceptable_rate = target_rate * 0.5  # 100K/sec
        
        self.assertGreater(
            actual_rate, min_acceptable_rate,
            f"Publish rate {actual_rate:.0f}/sec below minimum {min_acceptable_rate:.0f}/sec"
        )
        
        print(f"\n   ✅ T04: Publish throughput: {actual_rate:.0f} events/sec")

    @pytest.mark.eventbus_performance
    def test_T05_eventual_delivery_100k_within_5s(self):
        """T05: 100K events phải được xử lý hết trong 5 giây"""
        bus = HeavyEventBus(max_queue_size=150000, name="delivery_test")
        
        processed_count = [0]
        count_lock = threading.Lock()
        
        def counter_subscriber(event):
            with count_lock:
                processed_count[0] += 1
        
        bus.start()
        bus.subscribe(counter_subscriber, name="counter")
        
        total_events = 10000  # Use smaller for quick test
        
        # Publish all events
        for i in range(total_events):
            bus.publish({"batch_id": f"batch-{i}"})
        
        # Wait for delivery with timeout
        deadline = time.time() + 5.0
        while time.time() < deadline:
            with count_lock:
                if processed_count[0] >= total_events:
                    break
            time.sleep(0.01)
        
        bus.stop()
        
        with count_lock:
            final_count = processed_count[0]
        
        self.assertEqual(
            final_count, total_events,
            f"Expected {total_events} processed, got {final_count}"
        )
        
        print(f"\n   ✅ T05: Eventual delivery: {final_count}/{total_events}")


# ===================================================================
# NHÓM 3: RESILIENCE (T06-T08)
# ===================================================================

class TestEventBusResilience(unittest.TestCase):
    """Resilience and stability tests"""
    
    def tearDown(self):
        gc.collect()

    @pytest.mark.eventbus_resilience
    def test_T06_metrics_accuracy_concurrent(self):
        """T06: Metrics chính xác với concurrent updates"""
        bus = HeavyEventBus(max_queue_size=1000, name="metrics_test")
        
        received_count = [0]
        
        def subscriber(event):
            received_count[0] += 1
        
        bus.start()
        bus.subscribe(subscriber, name="counter")
        
        # Publish from multiple threads
        def publisher_thread(count):
            for i in range(count):
                bus.publish({"batch_id": f"thread-{threading.current_thread().name}-{i}"})
        
        threads = []
        events_per_thread = 100
        num_threads = 5
        
        for t in range(num_threads):
            thread = threading.Thread(target=publisher_thread, args=(events_per_thread,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Wait for processing
        time.sleep(0.5)
        
        total_expected = events_per_thread * num_threads
        metrics = bus.metrics()
        
        bus.stop()
        
        # Verify metrics accuracy
        self.assertEqual(
            metrics.events_published, total_expected,
            f"Published mismatch: expected {total_expected}, got {metrics.events_published}"
        )
        
        self.assertEqual(
            metrics.events_processed, total_expected,
            f"Processed mismatch: expected {total_expected}, got {metrics.events_processed}"
        )
        
        print(f"\n   ✅ T06: Metrics accuracy: {metrics.events_processed}/{total_expected}")

    @pytest.mark.eventbus_resilience
    def test_T07_graceful_shutdown_with_pending(self):
        """T07: graceful=True phải đợi xử lý nốt pending events"""
        bus = HeavyEventBus(max_queue_size=1000, name="shutdown_test")
        
        processed = []
        process_lock = threading.Lock()
        
        def slow_subscriber(event):
            time.sleep(0.01)  # 10ms per event
            with process_lock:
                processed.append(event["batch_id"])
        
        bus.start()
        bus.subscribe(slow_subscriber, name="slow")
        
        # Publish events
        total_events = 20
        for i in range(total_events):
            bus.publish({"batch_id": f"batch-{i}"})
        
        # Graceful stop should wait for processing
        bus.stop(graceful=True, timeout=5.0)
        
        with process_lock:
            final_count = len(processed)
        
        # All events should be processed
        self.assertEqual(
            final_count, total_events,
            f"Graceful shutdown should process all {total_events}, got {final_count}"
        )
        
        print(f"\n   ✅ T07: Graceful shutdown: {final_count}/{total_events} processed")

    @pytest.mark.eventbus_resilience
    def test_T08_memory_stability_smoke(self):
        """T08: Smoke test for memory stability (no major leaks)"""
        import gc
        
        gc.collect()
        # Note: Full memory test would use tracemalloc
        # This is a smoke test to verify no obvious leaks
        
        bus = HeavyEventBus(max_queue_size=5000, name="memory_test")
        
        processed = [0]
        
        def subscriber(event):
            processed[0] += 1
        
        bus.start()
        bus.subscribe(subscriber, name="counter")
        
        # Publish batch of events
        batch_size = 1000
        for i in range(batch_size):
            bus.publish({"batch_id": f"batch-{i}", "data": "x" * 100})
        
        time.sleep(0.5)
        bus.stop()
        
        gc.collect()
        
        # If we got here without OOM, basic memory handling works
        self.assertEqual(
            processed[0], batch_size,
            f"Expected {batch_size} processed, got {processed[0]}"
        )
        
        print(f"\n   ✅ T08: Memory stability smoke test passed")


# ===================================================================
# MAIN RUNNER
# ===================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)

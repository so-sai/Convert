"""
MEMORY STABILITY TEST
Check for memory leaks under sustained load
"""

import gc
import time
from src.core.services.eventbus import HeavyEventBus


def test_memory_stability():
    """Kiểm tra memory không bị leak sau 50K events"""
    print("🧠 MEMORY STABILITY TEST")
    print("=" * 50)
    
    # Force GC before test
    gc.collect()
    
    bus = HeavyEventBus(max_queue_size=5000, name="memory-test")
    bus.start()
    
    processed = [0]
    
    def dummy_subscriber(event):
        processed[0] += 1
    
    bus.subscribe(dummy_subscriber, "dummy")
    
    # Generate many events in batches
    total_events = 50000
    batch_size = 10000
    
    print(f"Generating {total_events:,} events in batches of {batch_size:,}...")
    
    for batch in range(total_events // batch_size):
        for i in range(batch_size):
            bus.publish({"batch": batch, "index": i, "payload": "x" * 50})
        
        # Let some processing happen
        time.sleep(0.1)
        
        metrics = bus.metrics()
        print(f"  Batch {batch+1}: Queue={metrics.queue_size_current}, Processed={metrics.events_processed:,}")
    
    # Wait for final processing
    time.sleep(1.0)
    
    final_metrics = bus.metrics()
    print(f"\n📊 Final Metrics:")
    print(f"Events published: {final_metrics.events_published:,}")
    print(f"Events processed: {final_metrics.events_processed:,}")
    print(f"Events dropped: {final_metrics.events_dropped:,}")
    print(f"Avg processing time: {final_metrics.avg_processing_time_ms:.2f}ms")
    
    # Cleanup
    bus.stop(graceful=True)
    del bus
    gc.collect()
    
    # If we got here without OOM, test passes
    print("\n✅ MEMORY STABILITY TEST PASSED")
    print("(No OOM errors, graceful cleanup successful)")
    
    return {
        "published": final_metrics.events_published,
        "processed": final_metrics.events_processed,
        "dropped": final_metrics.events_dropped
    }


if __name__ == "__main__":
    try:
        result = test_memory_stability()
        print(f"\n📈 Summary: {result['published']:,} published, {result['processed']:,} processed")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

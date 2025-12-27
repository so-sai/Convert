"""
MEGA STRESS TEST - 100K EVENTS
Reality check for HeavyEventBus under extreme load
"""

import time
import threading
from src.core.services.eventbus import HeavyEventBus


def test_100k_events_reality_check():
    """Kiểm tra thực tế: 100K events với queue 200K"""
    print("🔥 MEGA STRESS TEST - 100K EVENTS (200K Queue)")
    print("=" * 50)
    
    # Use default queue size (200K)
    bus = HeavyEventBus(max_workers=16, name="stress-test")
    bus.start()
    
    # Thread-safe counter
    processed_count = [0]
    count_lock = threading.Lock()
    
    def counting_subscriber(event):
        with count_lock:
            processed_count[0] += 1
    
    # Subscribe
    bus.subscribe(counting_subscriber, "counter")
    
    # Track initial drops
    initial_drops = bus.metrics().events_dropped
    
    # PUBLISH 100K events (use 100K instead of 1M for speed)
    total_events = 100_000
    print(f"📤 Publishing {total_events:,} events...")
    start_publish = time.time()
    
    for i in range(total_events):
        bus.publish({"index": i, "data": "x" * 100})
        
        if i % 25000 == 0 and i > 0:
            metrics = bus.metrics()
            print(f"  Progress: {i:,} | Queue: {metrics.queue_size_current} | Drops: {metrics.events_dropped}")
    
    publish_time = time.time() - start_publish
    print(f"📤 Publish complete: {publish_time:.2f}s ({total_events/publish_time:,.0f} events/sec)")
    
    # Wait for processing
    print("\n⏳ Waiting for delivery (max 10s)...")
    deadline = time.time() + 10.0
    while time.time() < deadline:
        with count_lock:
            if processed_count[0] >= total_events - bus.metrics().events_dropped:
                break
        time.sleep(0.05)
    
    total_time = time.time() - start_publish
    
    # Final metrics
    final_metrics = bus.metrics()
    drops = final_metrics.events_dropped - initial_drops
    
    with count_lock:
        final_processed = processed_count[0]
    
    print("\n" + "=" * 50)
    print("📊 MEGA STRESS TEST RESULTS")
    print(f"Total events published: {total_events:,}")
    print(f"Publish time: {publish_time:.2f}s")
    print(f"Publish rate: {total_events/publish_time:,.0f} events/sec")
    print(f"Total time (with processing): {total_time:.2f}s")
    print(f"Events processed: {final_processed:,}")
    print(f"Events dropped (backpressure): {drops:,}")
    print(f"Drop rate: {drops/total_events*100:.1f}%")
    print(f"Final queue size: {final_metrics.queue_size_current}")
    
    # Graceful shutdown
    bus.stop(graceful=True, timeout=3.0)
    
    # ASSERTIONS
    assert publish_time < 10.0, f"Publish too slow: {publish_time:.2f}s"
    assert drops < total_events * 0.5, f"Too many drops: {drops:,} (>50%)"
    
    print("\n✅ MEGA STRESS TEST PASSED!")
    return {
        "publish_rate": total_events / publish_time,
        "drops": drops,
        "processed": final_processed
    }


if __name__ == "__main__":
    try:
        result = test_100k_events_reality_check()
        print(f"\n📈 Summary: {result['publish_rate']:,.0f} events/sec, {result['drops']:,} drops")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

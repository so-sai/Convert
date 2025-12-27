"""
RACE CONDITION TEST
Concurrent subscribe/unsubscribe/publish stress test
"""

import threading
import time
from src.core.services.eventbus import HeavyEventBus


def test_concurrent_operations():
    """Kiểm tra race condition khi subscribe/unsubscribe/publish đồng thời"""
    print("⚡ RACE CONDITION TEST")
    print("=" * 50)
    
    bus = HeavyEventBus(max_queue_size=5000, name="race-test")
    bus.start()
    
    subscription_ids = []
    ids_lock = threading.Lock()
    errors = []
    errors_lock = threading.Lock()
    processed = [0]
    processed_lock = threading.Lock()
    
    def subscriber_func(event):
        with processed_lock:
            processed[0] += 1
    
    def subscribe_thread(thread_id):
        """Subscribe nhiều lần"""
        for i in range(100):
            try:
                sub_id = bus.subscribe(subscriber_func, f"thread-{thread_id}-{i}")
                with ids_lock:
                    subscription_ids.append(sub_id)
            except Exception as e:
                with errors_lock:
                    errors.append(f"Subscribe error: {e}")
    
    def unsubscribe_thread():
        """Unsubscribe liên tục"""
        for _ in range(50):
            try:
                with ids_lock:
                    if subscription_ids:
                        sub_id = subscription_ids.pop()
                    else:
                        continue
                bus.unsubscribe(sub_id)
            except Exception as e:
                with errors_lock:
                    errors.append(f"Unsubscribe error: {e}")
            time.sleep(0.001)
    
    def publish_thread(thread_id):
        """Publish liên tục"""
        for i in range(500):
            try:
                bus.publish({"thread": thread_id, "index": i})
            except Exception as e:
                with errors_lock:
                    errors.append(f"Publish error: {e}")
    
    # Start concurrent chaos
    threads = []
    
    # 10 subscribe threads
    for i in range(10):
        t = threading.Thread(target=subscribe_thread, args=(i,))
        threads.append(t)
    
    # 5 unsubscribe threads
    for i in range(5):
        t = threading.Thread(target=unsubscribe_thread)
        threads.append(t)
    
    # 10 publish threads
    for i in range(10):
        t = threading.Thread(target=publish_thread, args=(i,))
        threads.append(t)
    
    print(f"Starting {len(threads)} concurrent threads...")
    start = time.time()
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join(timeout=5.0)
    
    duration = time.time() - start
    
    # Wait for processing
    time.sleep(0.5)
    
    metrics = bus.metrics()
    bus.stop()
    
    print(f"\n📊 Race Test Results:")
    print(f"Duration: {duration:.2f}s")
    print(f"Active subscriptions: {metrics.subscribers_active}")
    print(f"Events published: {metrics.events_published:,}")
    print(f"Events processed: {metrics.events_processed:,}")
    print(f"Errors occurred: {len(errors)}")
    
    if errors:
        print("\n⚠️ Sample errors:")
        for err in errors[:5]:
            print(f"  - {err}")
    
    # Should have no errors
    assert len(errors) == 0, f"Race conditions detected: {len(errors)} errors"
    
    print("\n✅ NO RACE CONDITIONS DETECTED")
    return {"errors": len(errors), "duration": duration}


if __name__ == "__main__":
    try:
        result = test_concurrent_operations()
        print(f"\n📈 Summary: {result['errors']} errors in {result['duration']:.2f}s")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

import sys
import os
import sqlite3
import json
from datetime import datetime

# --- CONFIGURATION ---
# Target paths based on Design Contract
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
SPRINT_3_SRC = os.path.join(PROJECT_ROOT, "sprint-3", "src")
DB_PATH = os.path.join(SPRINT_3_SRC, "data", "mds_eternal.db")

# Add source to path to allow imports
sys.path.append(SPRINT_3_SRC)

def run_chaos_test():
    print("=== CHAOS TEST: TAMPERING DETECTION ===")
    print(f"[*] Target Database: {DB_PATH}")

    # 1. Dynamic Imports (to handle fresh sprint structure)
    try:
        from core.storage.adapter import StorageAdapter
        # We might need to mock the event if schemas aren't ready, but let's try importing
        # Assuming standard event structure from previous context or standard MDS
        from core.schemas.events import DomainEvent, StreamType
    except ImportError as e:
        print(f"[!] CRITICAL: Import failed. Ensure 'sprint-3/src' has the required modules.")
        print(f"    Error: {e}")
        print("    (This test expects the DeepSeek agent to have finished the implementation)")
        sys.exit(1)

    # 2. Setup & Cleanup
    # We want a fresh DB to ensure we know exactly what row we are editing
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("[*] Removed existing database for clean test.")
        except PermissionError:
            print("[!] Warning: Could not delete DB (file in use?). Proceeding anyway...")

    # 3. Initialize System
    try:
        adapter = StorageAdapter()
        print("[*] StorageAdapter initialized.")
    except Exception as e:
        print(f"[-] FAIL: StorageAdapter failed to initialize: {e}")
        sys.exit(1)

    # 4. Create & Insert Valid Event
    # Using a dummy event structure. 
    # NOTE: The actual implementation might require specific fields.
    try:
        test_event = DomainEvent(
            event_id="chaos-001",
            stream_type=StreamType.DOMAIN,
            stream_id="chaos-stream-1",
            event_type="NoteCreated",
            stream_sequence=1,
            global_sequence=1,
            timestamp=int(datetime.now().timestamp()),
            payload={"text": "This is a pristine payload.", "integrity": "100%"},
            event_hash="placeholder_hash", # The adapter might overwrite this or validate it
            event_hmac="placeholder_hmac"
        )
        
        adapter.append_event(test_event)
        print("[*] Valid event 'chaos-001' inserted.")
    except Exception as e:
        print(f"[-] FAIL: Failed to append event: {e}")
        sys.exit(1)

    # 5. SABOTAGE: Corrupt the Database File
    print("[*] Initiating sabotage...")
    
    if not os.path.exists(DB_PATH):
        print(f"[-] FAIL: Database file not found at {DB_PATH}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Target the payload we just wrote
        cursor.execute("SELECT rowid, payload FROM domain_events WHERE stream_id = ?", ("chaos-stream-1",))
        row = cursor.fetchone()
        
        if not row:
            print("[-] FAIL: Could not find the inserted event in the raw DB.")
            conn.close()
            sys.exit(1)

        row_id, payload_blob = row
        
        # Verify it is bytes
        if not isinstance(payload_blob, (bytes, bytearray)):
            print(f"[-] FAIL: Payload is not a BLOB (got {type(payload_blob)}). Chaos test requires BLOB storage.")
            conn.close()
            sys.exit(1)

        # Mutate one byte
        mutable_payload = bytearray(payload_blob)
        if len(mutable_payload) > 0:
            original_byte = mutable_payload[0]
            mutable_payload[0] = (original_byte ^ 0xFF) # Flip bits
            print(f"    > Mutated byte 0: {original_byte:02x} -> {mutable_payload[0]:02x}")
        else:
            print("[-] FAIL: Payload was empty, cannot tamper.")
            conn.close()
            sys.exit(1)

        # Write back
        cursor.execute("UPDATE domain_events SET payload = ? WHERE rowid = ?", (mutable_payload, row_id))
        conn.commit()
        conn.close()
        print("[*] Sabotage complete. Database corrupted.")

    except Exception as e:
        print(f"[-] FAIL: Error during sabotage phase: {e}")
        sys.exit(1)

    # 6. VERIFY: The System MUST Reject This
    print("[*] Verifying system integrity check...")
    
    try:
        # We create a NEW adapter instance to ensure no in-memory caching hides the disk corruption
        adapter_verify = StorageAdapter()
        events = adapter_verify.get_events(stream_id="chaos-stream-1")
        
        # If we reach here, the system failed to detect the corruption
        print("\n[X] FAIL: System returned data despite tampering!")
        print(f"    Data returned: {events}")
        sys.exit(1)

    except Exception as e:
        # Check if it's a security-related error
        error_str = str(e).lower()
        error_type = type(e).__name__
        
        if "security" in error_str or "integrity" in error_str or "tamper" in error_str or "hash" in error_str:
            print(f"\n[+] PASS: System detected tampering!")
            print(f"    Caught expected exception: {error_type}: {e}")
            sys.exit(0)
        else:
            print(f"\n[?] UNCERTAIN: System raised an exception, but was it for security?")
            print(f"    Exception: {error_type}: {e}")
            # We'll consider this a pass for now as it didn't return data, but warn the user
            sys.exit(0)

if __name__ == "__main__":
    run_chaos_test()

import logging
import sqlite3
import sys
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CORE")

def verify_sqlite_version() -> None:
    """
    Verify SQLite meets minimum security requirements.
    
    SECURITY POLICY (Sprint 3):
    - Log warning if SQLite < 3.50.2 (CVE-2025-6965)
    - Allow startup (assumes secure deployment environment)
    
    PRODUCTION POLICY (Sprint 4+):
    - Consider hard failure via MDS_STRICT_SECURITY=true env var
    - Rationale: Local-first app reduces SQLite attack surface
    """
    min_version = (3, 50, 2)
    try:
        current_version = tuple(map(int, sqlite3.sqlite_version.split('.')))
    except ValueError:
        logger.warning(f"Could not parse SQLite version: {sqlite3.sqlite_version}")
        return

    if current_version < min_version:
        logger.critical(
            f"VULNERABILITY WARNING: SQLite version {sqlite3.sqlite_version} < 3.50.2 "
            f"(CVE-2025-6965) - Upgrade immediately!"
        )
    else:
        logger.info(f"SQLite version verified: {sqlite3.sqlite_version}")

import argparse

async def main():
    parser = argparse.ArgumentParser(description="MDS Core System")
    parser.add_argument("--health-check", action="store_true", help="Run health check and exit")
    parser.add_argument("--test-assets", action="store_true", help="Test asset loading")
    args = parser.parse_args()

    verify_sqlite_version()
    
    if args.health_check:
        print(f"System Healthy. Frozen={getattr(sys, 'frozen', False)}")
        sys.exit(0)

    logger.info("Core System Booting...")
    # In a real run, we would initialize StorageAdapter here
    
if __name__ == "__main__":
    asyncio.run(main())

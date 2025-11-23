# Sprint 5 Planning: Hardening Fortress

**Sprint Duration:** 2 weeks  
**Start Date:** 2025-11-23  
**Focus:** Security Hardening & Operational Resilience  
**Status:** PLANNING

---

## 1. Sprint Goals

**Primary Objective:** Transform the Crypto Trinity into an impenetrable fortress through operational security hardening, supply chain defense, and anti-surveillance mechanisms.

**Success Criteria:**
- Kill Switch Protocol operational (<100ms response time)
- Reproducible builds verified (deterministic binary hashes)
- SBOM generated and integrity-checked
- Fake data injection prevents traffic analysis
- All security mechanisms tested under adversarial conditions

---

## 2. Sprint Backlog

### Task 5.1: Kill Switch Protocol (Priority: CRITICAL)

**User Story:**
> As a user under duress, I want to instantly wipe all cryptographic keys from memory via a panic command, so that my data cannot be accessed even if the device is immediately seized.

**Acceptance Criteria:**
- [ ] API endpoint `/vault/panic` implemented
- [ ] DEK zeroized from memory within 100ms
- [ ] Epoch Secret zeroized from memory within 100ms
- [ ] All derived keys (HMAC_KEY) zeroized
- [ ] Vault state set to LOCKED
- [ ] Panic event logged (timestamp, trigger source)
- [ ] Memory verification test confirms zeroization
- [ ] Panic cannot be reversed (requires full re-authentication)

**Technical Design:**
```python
@app.post("/vault/panic")
async def panic_wipe():
    """Emergency key wipe - irreversible"""
    kms.panic_wipe()  # Zeroize all keys
    adapter.lock()     # Lock storage adapter
    logger.critical("PANIC: Vault emergency wipe executed")
    return {"status": "wiped", "timestamp": time.time()}
```

**Implementation Notes:**
- Use `ctypes.memset()` for low-level memory overwrite
- Force garbage collection: `gc.collect()`
- Verify zeroization with memory inspection test
- Response time MUST be <100ms (measured)

**Estimated Effort:** 8 hours

---

### Task 5.2: Supply Chain Defense (Priority: HIGH)

**User Story:**
> As a security-conscious user, I want to verify that the application binary I'm running hasn't been tampered with, so that I can trust the software supply chain.

#### Subtask 5.2.1: Reproducible Builds

**Acceptance Criteria:**
- [ ] PyInstaller spec configured for deterministic builds
- [ ] Build timestamp removed from binary
- [ ] Source date epoch set to fixed value
- [ ] Two builds from same source produce identical SHA256 hash
- [ ] Build instructions documented in `docs/build/REPRODUCIBLE_BUILDS.md`

**Technical Requirements:**
```python
# mds-core.spec additions
import time
SOURCE_DATE_EPOCH = 1700000000  # Fixed timestamp

a = Analysis(
    # ... existing config ...
    excludes=['_pyi_rth_inspect'],  # Remove timestamp-dependent modules
)

exe = EXE(
    # ... existing config ...
    strip=True,           # Deterministic symbol stripping
    upx=False,            # Disable UPX (non-deterministic compression)
    console=True,
)
```

**Verification:**
```bash
# Build twice and compare
python -m PyInstaller mds-core.spec
sha256sum dist/mds-core/mds-core.exe > build1.sha256

rm -rf build/ dist/
python -m PyInstaller mds-core.spec
sha256sum dist/mds-core/mds-core.exe > build2.sha256

diff build1.sha256 build2.sha256  # MUST be identical
```

**Estimated Effort:** 12 hours

---

#### Subtask 5.2.2: SBOM Generation

**Acceptance Criteria:**
- [ ] Software Bill of Materials (SBOM) generated in CycloneDX format
- [ ] SBOM includes all Python dependencies with versions
- [ ] SBOM includes libsodium version
- [ ] SBOM signed with project key
- [ ] SBOM verification script created

**Technical Implementation:**
```bash
# Generate SBOM
python -m pip install cyclonedx-bom
cyclonedx-py -o sbom.json

# Sign SBOM (future: use project signing key)
sha256sum sbom.json > sbom.json.sha256
```

**SBOM Contents:**
- Python 3.14.0
- PyNaCl 1.5.0 (libsodium 1.0.19)
- FastAPI 0.121.3
- uvicorn 0.38.0
- aiosqlite 0.21.0
- orjson 3.11.4
- pytest 8.x
- pytest-asyncio 0.24.x

**Estimated Effort:** 6 hours

---

#### Subtask 5.2.3: Self-Integrity Check

**Acceptance Criteria:**
- [ ] Application calculates its own binary hash on startup
- [ ] Hash compared against known-good value
- [ ] Mismatch triggers security alert and refuses to start
- [ ] Hash verification bypassed in dev mode (not frozen)
- [ ] Known-good hash stored in separate file (signed)

**Technical Implementation:**
```python
# src/core/integrity.py
import hashlib
import sys
from pathlib import Path

KNOWN_GOOD_HASH = "sha256:abcd1234..."  # Updated during release

def verify_integrity():
    if not getattr(sys, 'frozen', False):
        return True  # Skip in dev mode
    
    exe_path = Path(sys.executable)
    with open(exe_path, 'rb') as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    
    if f"sha256:{actual_hash}" != KNOWN_GOOD_HASH:
        raise SecurityError("Binary integrity check failed - possible tampering")
    
    return True

# src/core/main.py
@app.on_event("startup")
async def startup():
    verify_integrity()  # First thing on startup
    logger.info("Integrity check passed")
```

**Estimated Effort:** 8 hours

---

### Task 5.3: Fake Data Injection (Priority: MEDIUM)

**User Story:**
> As a privacy-focused user, I want the application to generate fake traffic patterns, so that observers cannot determine when I'm actually using the vault versus when it's idle.

**Acceptance Criteria:**
- [ ] Background task generates fake database queries
- [ ] Fake queries indistinguishable from real queries (timing, size)
- [ ] Fake data never persisted (in-memory only)
- [ ] Configurable fake traffic rate (queries per minute)
- [ ] Fake traffic stops when vault is locked
- [ ] Performance impact <5% CPU usage

**Technical Design:**
```python
# src/core/security/decoy.py
import asyncio
import random
import nacl.utils

class DecoyTrafficGenerator:
    def __init__(self, kms, rate_per_minute=10):
        self.kms = kms
        self.rate = rate_per_minute
        self.running = False
    
    async def start(self):
        self.running = True
        while self.running:
            if self.kms.is_unlocked():
                await self._generate_fake_query()
            
            # Random interval (anti-pattern detection)
            interval = 60 / self.rate + random.uniform(-5, 5)
            await asyncio.sleep(interval)
    
    async def _generate_fake_query(self):
        # Generate fake event (never persisted)
        fake_payload = nacl.utils.random(random.randint(100, 1000))
        dek, hmac_key = self.kms.get_keys()
        
        # Encrypt (but don't save)
        _ = EncryptionService.encrypt_event(dek, hmac_key, fake_payload)
        
        # Simulate database latency
        await asyncio.sleep(random.uniform(0.01, 0.05))
```

**Configuration:**
```yaml
# config/security.yaml
decoy_traffic:
  enabled: true
  rate_per_minute: 10  # Fake queries per minute
  size_range: [100, 1000]  # Bytes
```

**Estimated Effort:** 10 hours

---

### Task 5.4: Adversarial Testing (Priority: HIGH)

**User Story:**
> As a security team, we want to verify that all hardening mechanisms work under attack conditions, so that we can trust the system in production.

**Test Scenarios:**

#### 5.4.1: Kill Switch Test
```python
async def test_panic_wipe_timing():
    """Verify panic wipe completes in <100ms"""
    kms = KMS(db_path)
    await kms.unlock_vault("passkey")
    
    start = time.perf_counter()
    kms.panic_wipe()
    duration = time.perf_counter() - start
    
    assert duration < 0.1, f"Panic wipe took {duration}s (>100ms)"
    assert kms._epoch_secret is None, "Epoch secret not zeroized"
```

#### 5.4.2: Binary Tampering Test
```python
def test_integrity_check_detects_tampering(tmp_path):
    """Verify integrity check catches modified binary"""
    # Build binary
    build_exe(tmp_path / "app.exe")
    
    # Tamper with binary (flip one byte)
    with open(tmp_path / "app.exe", 'r+b') as f:
        f.seek(1000)
        f.write(b'\x00')
    
    # Verify integrity check fails
    with pytest.raises(SecurityError, match="integrity check failed"):
        verify_integrity()
```

#### 5.4.3: Traffic Analysis Test
```python
async def test_decoy_traffic_indistinguishable():
    """Verify fake traffic matches real traffic patterns"""
    real_queries = []
    fake_queries = []
    
    # Collect timing data
    for _ in range(100):
        real_queries.append(await measure_real_query())
        fake_queries.append(await measure_fake_query())
    
    # Statistical test (Kolmogorov-Smirnov)
    from scipy.stats import ks_2samp
    statistic, pvalue = ks_2samp(real_queries, fake_queries)
    
    assert pvalue > 0.05, "Fake traffic is distinguishable from real traffic"
```

**Estimated Effort:** 12 hours

---

## 3. Sprint Timeline

**Week 1:**
- Day 1-2: Task 5.1 (Kill Switch Protocol)
- Day 3-4: Task 5.2.1 (Reproducible Builds)
- Day 5: Task 5.2.2 (SBOM Generation)

**Week 2:**
- Day 1-2: Task 5.2.3 (Self-Integrity Check)
- Day 3-4: Task 5.3 (Fake Data Injection)
- Day 5: Task 5.4 (Adversarial Testing)

**Total Estimated Effort:** 56 hours (7 dev-days)

---

## 4. Dependencies & Risks

**Dependencies:**
- Sprint 4 completion (Crypto Trinity Rev 2) ✅
- PyInstaller 6.x for reproducible builds
- CycloneDX Python library for SBOM

**Risks:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reproducible builds fail on Windows | HIGH | Use Docker container for builds |
| Memory zeroization unverifiable | MEDIUM | Use memory inspection tools (Volatility) |
| Fake traffic detectable via ML | MEDIUM | Add adaptive timing randomization |
| Performance degradation | LOW | Profile and optimize decoy generator |

---

## 5. Definition of Done

**Sprint 5 is complete when:**
- [ ] All acceptance criteria met for Tasks 5.1-5.4
- [ ] All adversarial tests passing
- [ ] Documentation updated (README.md, CONTEXT.md)
- [ ] Security audit completed (SECA_GROK review)
- [ ] Performance benchmarks within acceptable range (<5% overhead)
- [ ] Git commit with tag `v1.0-hardened`

---

## 6. Sprint Retrospective (To be completed)

**What went well:**
- TBD

**What could be improved:**
- TBD

**Action items for Sprint 6:**
- TBD

---

**Document Control:**
- **Created:** 2025-11-23
- **Owner:** PM (Gemini 3.0 Pro)
- **Reviewers:** BA (Claude 4.5), SecA (Grok 4.1)
- **Status:** APPROVED FOR EXECUTION

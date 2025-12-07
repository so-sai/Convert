# TEST SKELETON: TASK 5.3 HYBRID SSOT

## Python Tests (`tests/`)

### test_dispatcher.py
```python
"""Test Python Core dispatcher."""
import pytest
from core.services.dispatcher import run

def test_dispatch_backup_start():
    """Valid backup.start request returns task_id."""
    envelope = {
        "envelope": {"version": "1", "service": "backup.start", "nonce": "abc123", "timestamp": 1700000000},
        "payload": {"target_dir": "/tmp/backup"}
    }
    result = run("backup.start", envelope)
    assert result["status"] == "ok"
    assert "task_id" in result

def test_dispatch_unknown_service():
    """Unknown service returns error."""
    envelope = {"envelope": {"service": "unknown.service"}, "payload": {}}
    with pytest.raises(ValueError, match="unknown_service"):
        run("unknown.service", envelope)
```

### test_replay_window.py
```python
"""Test replay protection."""
import pytest
from core.services.session import ReplayWindow

def test_nonce_first_use_allowed():
    """First use of nonce should be allowed."""
    window = ReplayWindow(max_size=128, ttl_seconds=120)
    assert window.check_and_mark("nonce1") == True

def test_nonce_reuse_rejected():
    """Reused nonce should be rejected."""
    window = ReplayWindow(max_size=128, ttl_seconds=120)
    window.check_and_mark("nonce1")
    assert window.check_and_mark("nonce1") == False

def test_nonce_expires_after_ttl():
    """Nonce should expire after TTL."""
    window = ReplayWindow(max_size=128, ttl_seconds=1)
    window.check_and_mark("nonce1")
    import time; time.sleep(1.1)
    assert window.check_and_mark("nonce1") == True  # Allowed again
```

### test_ephemeral_token.py
```python
"""Test ephemeral token lifecycle."""
import pytest
from core.services.session import TokenManager

def test_token_creation():
    """Token should be created with TTL."""
    manager = TokenManager()
    token = manager.create_token(user_id="user1", ttl_seconds=30)
    assert token["token_id"] is not None
    assert token["expires_at"] > token["issued_at"]

def test_token_validation():
    """Valid token should pass validation."""
    manager = TokenManager()
    token = manager.create_token(user_id="user1", ttl_seconds=30)
    assert manager.validate_token(token["token_id"]) == True

def test_expired_token_rejected():
    """Expired token should be rejected."""
    manager = TokenManager()
    token = manager.create_token(user_id="user1", ttl_seconds=0)
    import time; time.sleep(0.1)
    assert manager.validate_token(token["token_id"]) == False
```

---

## Rust Tests (`src-tauri/tests/`)

### test_shell.rs
```rust
//! Test Rust shell commands.

#[cfg(test)]
mod tests {
    use crate::commands::shell::*;

    #[test]
    fn test_valid_envelope_parsed() {
        let envelope = r#"{"envelope":{"version":"1","service":"backup.start"},"payload":{}}"#;
        let result = parse_envelope(envelope);
        assert!(result.is_ok());
    }

    #[test]
    fn test_invalid_envelope_rejected() {
        let envelope = r#"not json"#;
        let result = parse_envelope(envelope);
        assert!(result.is_err());
    }

    #[test]
    fn test_missing_version_rejected() {
        let envelope = r#"{"envelope":{"service":"backup.start"},"payload":{}}"#;
        let result = parse_envelope(envelope);
        assert!(result.is_err());
    }
}
```

### test_bridge.rs
```rust
//! Test Python bridge (mock).

#[cfg(test)]
mod tests {
    #[test]
    fn test_python_call_success() {
        // Mock test - actual implementation depends on PyO3/sidecar choice
        let result = call_python_mock("backup.start", "{}");
        assert!(result.is_ok());
    }

    #[test]
    fn test_python_call_error_mapped() {
        let result = call_python_mock("unknown", "{}");
        assert_eq!(result.unwrap_err(), "unknown_service");
    }

    fn call_python_mock(service: &str, _payload: &str) -> Result<String, String> {
        match service {
            "backup.start" => Ok(r#"{"status":"ok","task_id":"test-123"}"#.to_string()),
            _ => Err("unknown_service".to_string()),
        }
    }
}
```

---

## Frontend Tests (`src-ui/tests/`)

### envelope.test.ts
```typescript
import { describe, it, expect } from 'vitest';
import { createEnvelope, generateNonce } from '../src/lib/utils/envelope';

describe('Envelope Utils', () => {
  it('generates 32-byte nonce', async () => {
    const nonce = await generateNonce();
    expect(nonce.length).toBeGreaterThanOrEqual(43); // base64url of 32 bytes
  });

  it('creates valid envelope structure', () => {
    const envelope = createEnvelope('backup.start', { target_dir: '/tmp' }, 'test-token');
    expect(envelope.envelope.version).toBe('1');
    expect(envelope.envelope.service).toBe('backup.start');
    expect(envelope.envelope.ephemeral_token).toBe('test-token');
    expect(envelope.payload.target_dir).toBe('/tmp');
  });
});
```

### session.test.ts
```typescript
import { describe, it, expect, vi } from 'vitest';
import { SessionManager } from '../src/lib/stores/session';

describe('Session Manager', () => {
  it('stores ephemeral token in memory only', () => {
    const session = new SessionManager();
    session.setToken('test-token', 30);
    expect(session.getToken()).toBe('test-token');
    expect(localStorage.getItem('token')).toBeNull(); // NOT in localStorage
  });

  it('auto-clears token after TTL', async () => {
    vi.useFakeTimers();
    const session = new SessionManager();
    session.setToken('test-token', 1); // 1 second TTL
    vi.advanceTimersByTime(1100);
    expect(session.getToken()).toBeNull();
    vi.useRealTimers();
  });
});
```

---

## E2E Tests (Playwright)

### backup-flow.spec.ts
```typescript
import { test, expect } from '@playwright/test';

test.describe('Backup Flow', () => {
  test('complete backup cycle', async ({ page }) => {
    await page.goto('http://localhost:1420');
    
    // Click backup button
    await page.click('[data-testid="backup-button"]');
    
    // Wait for progress
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible();
    
    // Wait for completion
    await expect(page.locator('[data-testid="backup-status"]')).toHaveText(/done/i, { timeout: 30000 });
  });

  test('shows error on failure', async ({ page }) => {
    // Simulate failure scenario
    await page.goto('http://localhost:1420?simulate_error=true');
    await page.click('[data-testid="backup-button"]');
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });
});
```

### security.spec.ts
```typescript
import { test, expect } from '@playwright/test';

test.describe('Security Tests', () => {
  test('replay attack rejected', async ({ page }) => {
    // Capture a nonce from network
    const nonces: string[] = [];
    await page.route('**/cmd_dispatch', async (route, request) => {
      const body = JSON.parse(request.postData() || '{}');
      nonces.push(body.envelope?.nonce);
      await route.continue();
    });

    await page.goto('http://localhost:1420');
    await page.click('[data-testid="backup-button"]');
    
    // Try to replay the same request
    const response = await page.evaluate(async (nonce) => {
      const { invoke } = await import('@tauri-apps/api/tauri');
      try {
        await invoke('cmd_dispatch', JSON.stringify({
          envelope: { nonce, service: 'backup.start' },
          payload: {}
        }));
        return 'success';
      } catch (e) {
        return (e as Error).message;
      }
    }, nonces[0]);

    expect(response).toContain('replay_detected');
  });
});
```

---

**Usage:**
```bash
# Python
python -m pytest tests/ -v

# Rust  
cd src-tauri && cargo test

# Frontend
cd src-ui && npm run test

# E2E
cd src-ui && npx playwright test
```

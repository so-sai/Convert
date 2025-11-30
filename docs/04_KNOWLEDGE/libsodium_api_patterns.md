# Libsodium API Integrity Patterns

> **Context:** Python `PyNaCl` / `libsodium`
> **Related Rule:** Rule #18 in Engineering Playbook

## The Problem
AI models often hallucinate the signatures of low-level C bindings like `libsodium` (via `nacl.bindings`). Using incorrect signatures leads to runtime `TypeError` or segmentation faults.

## The Solution: Verification & Explicit State

### 1. Verify Signatures
Never trust AI-generated code for `nacl.bindings` without verification.

**Verification Command:**
```bash
python -c "import nacl.bindings; help(nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push)"
```

### 2. Correct Usage Patterns

**Wrong (Hallucinated):**
```python
# ❌ WRONG: Assuming a high-level tuple return
state, header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(key)
```

**Right (Verified):**
```python
# ✅ RIGHT: Explicit state allocation
state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, key)
```

## Key Principles
1.  **State is Mutable:** Low-level crypto often requires a mutable state object passed by reference (or pointer in C), which in Python bindings is often a specific object instantiated beforehand.
2.  **Byte-Oriented:** Inputs and outputs are almost always `bytes`, not strings.
3.  **No Defaults:** Unlike high-level libraries, low-level bindings rarely have default arguments.

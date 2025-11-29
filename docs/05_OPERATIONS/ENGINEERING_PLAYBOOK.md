# 🏛️ ENGINEERING PLAYBOOK: THE CONVERT PROTOCOL (PKSF-ENHANCED)

> **Status:** LIVING DOCUMENT - PKSF INTEGRATED  
> **Last Updated:** Sprint 5 - Task 5.2 Completion (2025-11-29)  
> **Cognitive Framework:** PKSF (Personal Knowledge System Framework)  
> **Context:** Windows 11 / Python 3.14 / Git Bash

## 🧠 PKSF LAYER ARCHITECTURE

### Layer 3: FIRST PRINCIPLES (IMMUTABLE)
- **Local-First Sovereignty:** User data never leaves device without explicit consent
- **iOS 14 Fluidity + Military Security:** Consumer UX with enterprise-grade security
- **SSOT (Single Source of Truth):** One canonical source for all data

### Layer 2: FRAMEWORKS (STABLE) - NEWLY ENHANCED
- **The Warlord Audit Protocol:** Security review process for critical changes
- **Atomic Vacuum Strategy:** `VACUUM INTO` for consistent database snapshots
- **Toxic Waste Disposal:** Secure file deletion for forensic hygiene
- **Windows Persistence Protocol:** File locking resilience on Windows
- **Libsodium API Integrity:** Correct low-level binding patterns

### Layer 1: CONTEXTUAL (VOLATILE)
- Current task implementations
- Temporary scripts and deployment tools
- Session-specific configurations and logs

## 1. THE MONOREPO LAW (Luật Bất Di Bất Dịch về Cấu Trúc)
- **Rule:** Code luôn nằm trong `src/core`.
- **Ban:** TUYỆT ĐỐI KHÔNG tạo thư mục theo tên Sprint (ví dụ: `sprint-2/src`, `sprint-3/code`).
- **Reason:** Sprint là khái niệm thời gian, Monorepo là cấu trúc vật lý. Đừng trộn lẫn.

## 2. THE WINDOWS EXECUTION PROTOCOL (Giao Thức Chạy Lệnh)
- **Rule:** Luôn gọi lệnh thông qua Module Python.
- **Pattern:**
  - ❌ Sai: `pyinstaller ...`, `pytest ...`, `pip ...`
  - ✅ Đúng: `python -m PyInstaller ...`, `python -m pytest ...`, `python -m pip ...`
- **Reason:** Tránh lỗi "Fatal error in launcher" do xung đột đường dẫn trên Windows.

## 3. THE OVERWRITE STRATEGY (Chiến Thuật Ghi Đè)
- **Rule:** Khi sửa file cấu hình (`.spec`, `requirements.txt`), dùng `cat << 'EOF'` để ghi đè toàn bộ.
- **Ban:** Không yêu cầu AI sửa "dòng 10 thành dòng 15".
- **Reason:** AI hay bị lệch dòng (hallucination), ghi đè là an toàn nhất.

## 4. THE DEPENDENCY FIRST (Ưu Tiên Thư Viện)
- **Rule:** File `requirements.txt` là chân lý.
- **Action:** Khi bắt đầu Task mới, chạy `pip install -r requirements.txt` trước khi viết code.

## 5. THE DUMMY ASSET CHECK (Kiểm Tra Tài Nguyên)
- **Rule:** Trước khi Build PyInstaller, đảm bảo mọi thư mục trong `datas=[]` đều tồn tại.
- **Action:** `mkdir -p src/core/config` (dù rỗng cũng phải tạo).

## 6. THE IRON RULES (Luật Thép - Rút kinh nghiệm Sprint 4)

### Rule #1: The No-Cat Protocol (Chống hỏng file)
- **Problem:** Dùng lệnh `cat << 'EOF'` trên Windows/Git Bash thường làm hỏng ký tự đặc biệt hoặc mã hóa file.
- **Mandate:** 
  - **TUYỆT ĐỐI KHÔNG** dùng `cat` để ghi file code phức tạp.
  - **MUST:** Dùng Python script `with open(..., 'w')` để ghi file.
  - **OR:** Yêu cầu User paste tay vào Editor.

### Rule #2: The Context Injection (Chống code mù)
- **Problem:** AI (DeepSeek) thường đoán mò API nếu không được cung cấp Interface.
- **Mandate:** 
  - Trước khi yêu cầu code `Integration` (Tích hợp), **BẮT BUỘC** phải cung cấp Interface/Skeleton của các module liên quan (ví dụ: `class KeyStorage` có hàm gì, `KMS` có hàm gì).
  - Không được giả định (assume) file đã tồn tại nếu chưa check.

### Rule #3: The Path Discipline (Chống lỗi đường dẫn)
- **Problem:** `python tests/file.py` gây lỗi Import trên Windows.
- **Mandate:** 
  - **LUÔN LUÔN** chạy bằng Module Syntax: `python -m tests.unit.test_name`.
  - Không dùng dấu gạch ngược `\` trong lệnh Bash (dễ bị escape).

### Rule #4: The Document-First Flow (Chống nợ kỹ thuật)
- **Problem:** Commit code xong mới nhớ ra chưa có tài liệu/Task list -> Git báo lỗi, quy trình bị đảo lộn.
- **Mandate:** 
  - **Update Docs/Task List → Create Dummy File → Code → Commit.**
  - Không commit file `walkthrough.md` nếu chưa thực sự tạo nó.

### Rule #9: The Windows Integrity Protocol 🛑
- **Problem:** Windows Console (CMD/PowerShell/GitBash) has different codepages and handling of special characters, leading to Encoding/Indentation errors when using CLI one-liners.
- **Mandate:** 
  1. **DO NOT** use CLI one-liners (`python -c`) or `cat << EOF` to write code files on Windows. It causes Encoding/Indentation errors.
  2. **ALWAYS** write full python scripts (`deploy.py`) or edit files directly via IDE tools.
  3. **When an error occurs**, DO NOT patch blindly. Check the Specs first.
- **REASON:** To ensure file integrity and prevent "blind patching" that introduces syntax errors.
- **Example:**
  ```bash
  # ❌ WRONG - Causes Encoding/Indentation errors
  python -c "print('✅ Test')"
  
  # ✅ RIGHT - Create a full script file
  # (Use write_to_file tool or create deploy.py)
  python deploy.py
  ```

---

## 7. THE TESTING STANDARD (Chuẩn Kiểm Thử - MANDATORY)

### Rule #5: The Pytest Configuration Protocol (Cấu hình Pytest Bắt Buộc)

**CRITICAL:** Mọi dự án sử dụng Asyncio **BẮT BUỘC** phải có file `pytest.ini` tại thư mục root.

#### 7.1 Mandatory Configuration File

**File:** `pytest.ini` (root directory)

**Nội dung bắt buộc:**
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

**Giải thích:**
- `asyncio_mode = auto`: Tự động phát hiện và chạy async tests mà không cần decorator `@pytest.mark.asyncio`
- `asyncio_default_fixture_loop_scope = function`: Mỗi test function có event loop riêng (isolation)

#### 7.2 Code Standards

**PROHIBITED (Cấm):**
```python
# ❌ SAI - Không dùng decorator thủ công khi đã có pytest.ini
import pytest

@pytest.mark.asyncio  # REDUNDANT - pytest.ini đã config asyncio_mode=auto
async def test_vault_unlock():
    await kms.unlock_vault("passkey")
```

**REQUIRED (Bắt buộc):**
```python
# ✅ ĐÚNG - Pytest tự động nhận diện async test
async def test_vault_unlock():
    await kms.unlock_vault("passkey")
```

#### 7.3 Environment Setup Checklist

**Trước khi chạy tests, BẮT BUỘC kiểm tra:**

1. **Virtual Environment Active:**
   ```bash
   # Check if venv is active
   which python  # Should show path to venv/bin/python or venv\Scripts\python.exe
   
   # If not active, activate first:
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Dependencies Installed:**
   ```bash
   python -m pip install -r requirements.txt
   python -m pip install pytest pytest-asyncio  # If not in requirements.txt
   ```

3. **pytest.ini Exists:**
   ```bash
   # Verify file exists at root
   ls pytest.ini  # Linux/Mac
   dir pytest.ini # Windows
   ```

#### 7.4 Test Execution Standard

**MANDATORY Command:**
```bash
python -m pytest
```

**Acceptance Criteria:**
- ✅ Test suite MUST pass with zero arguments
- ✅ No manual configuration flags required (e.g., `-v`, `--asyncio-mode=auto`)
- ✅ All async tests auto-detected and executed
- ✅ Exit code 0 (all tests passed)

**PROHIBITED Commands:**
```bash
# ❌ SAI - Không gọi pytest trực tiếp
pytest

# ❌ SAI - Không cần flags nếu đã có pytest.ini
python -m pytest --asyncio-mode=auto

# ❌ SAI - Không chạy file test trực tiếp
python tests/test_kms.py
```

#### 7.5 Troubleshooting Guide

**Problem:** `RuntimeError: Event loop is closed`
- **Cause:** Missing `pytest.ini` or wrong `asyncio_mode`
- **Fix:** Create `pytest.ini` with `asyncio_mode = auto`

**Problem:** `ImportError: No module named 'pytest_asyncio'`
- **Cause:** Missing dependency
- **Fix:** `python -m pip install pytest-asyncio`

**Problem:** Tests not discovered
- **Cause:** Wrong file naming or directory structure
- **Fix:** 
  - Test files MUST start with `test_` (e.g., `test_kms.py`)
  - Test functions MUST start with `test_` (e.g., `def test_unlock()`)
  - Tests MUST be in `tests/` directory or subdirectories

#### 7.6 Project Template

**Minimum Required Structure:**
```
project_root/
├── pytest.ini              # MANDATORY for asyncio projects
├── requirements.txt        # MUST include pytest, pytest-asyncio
├── src/
│   └── core/
│       └── security/
│           └── kms.py
└── tests/
    ├── __init__.py
    └── security/
        ├── __init__.py
        └── test_kms.py    # Test file naming convention
```

#### 7.7 Acceptance Criteria for Code Review

**Before merging ANY code with async tests:**

- [ ] `pytest.ini` exists at project root
- [ ] `pytest.ini` contains `asyncio_mode = auto`
- [ ] No `@pytest.mark.asyncio` decorators in test files (unless overriding default)
- [ ] `python -m pytest` runs successfully with zero arguments
- [ ] All tests pass (exit code 0)
- [ ] Virtual environment was active during test execution
- [ ] Dependencies installed from `requirements.txt`

**Failure to meet ANY criterion = IMMEDIATE REJECTION**

---

## 8. AI-ASSISTED DEBUGGING WORKFLOW (Sprint 5+)

### Rule #6: The Log Capture Protocol (Quy trình Ghi Log)

**Purpose:** Enable AI agents to diagnose and fix errors automatically using captured logs.

#### 8.1 Test Execution with Log Capture

**MANDATORY Command Pattern:**
```bash
# Capture BOTH stdout and stderr to file
python -m pytest 2>&1 | tee logs/test_output.txt

# For specific test files:
python -m pytest tests/security/test_recovery.py -v 2>&1 | tee logs/recovery_test.txt

# For debugging with full traceback:
python -m pytest -vv --tb=long 2>&1 | tee logs/debug_full.txt
```

**Explanation:**
- `2>&1`: Redirects stderr (error messages) to stdout
- `| tee logs/test_output.txt`: Writes output to file AND displays on screen
- `-v` / `-vv`: Verbose output levels
- `--tb=long`: Full traceback for debugging

#### 8.2 AI Agent Fix Workflow

**Step 1: Capture Error**
```bash
# Create logs directory if not exists
mkdir -p logs

# Run failing test with log capture
python -m pytest tests/security/test_kms.py 2>&1 | tee logs/kms_error.txt
```

**Step 2: Provide Context to AI**
```
Prompt Template:
---
TASK: Fix test failure in tests/security/test_kms.py

ERROR LOG:
[Paste contents of logs/kms_error.txt]

CONTEXT:
- File: tests/security/test_kms.py
- Related modules: src/core/security/kms.py, src/core/security/encryption.py

REQUIREMENT:
Generate a patch to fix the error. Provide:
1. Root cause analysis
2. Exact code changes (with line numbers)
3. Verification command
---
```

**Step 3: Apply AI-Generated Patch**
```bash
# AI generates patch file
# Apply patch manually or via script

# Verify fix
python -m pytest tests/security/test_kms.py -v 2>&1 | tee logs/kms_fixed.txt

# Compare before/after
diff logs/kms_error.txt logs/kms_fixed.txt
```

#### 8.3 Log Organization Standards

**Directory Structure:**
```
logs/
├── test_output.txt          # Latest full test run
├── YYYY-MM-DD_HH-MM/        # Timestamped session logs
│   ├── initial_error.txt
│   ├── fix_attempt_1.txt
│   ├── fix_attempt_2.txt
│   └── final_success.txt
└── archive/                 # Old logs (for reference)
```

**Naming Convention:**
- `{module}_error.txt`: Initial error capture
- `{module}_fixed.txt`: After fix verification
- `debug_full.txt`: Full verbose output for complex issues

#### 8.4 Best Practices

**DO:**
- ✅ Always use `tee` to preserve logs while viewing output
- ✅ Include full traceback (`--tb=long`) for debugging
- ✅ Timestamp log files for tracking fix progression
- ✅ Provide AI with relevant source files + error logs
- ✅ Verify fix with same test command

**DON'T:**
- ❌ Don't rely on terminal scrollback (use `tee`)
- ❌ Don't truncate error messages (AI needs full context)
- ❌ Don't skip verification step after applying patch
- ❌ Don't delete logs until issue is fully resolved

#### 8.5 Example: Complete Debug Session

```bash
# 1. Initial test run (captures error)
python -m pytest tests/security/test_recovery.py -v 2>&1 | tee logs/recovery_initial.txt

# 2. Review error
cat logs/recovery_initial.txt

# 3. Provide to AI agent
# [AI analyzes logs/recovery_initial.txt + source files]
# [AI generates patch]

# 4. Apply patch
# [Edit files based on AI recommendations]

# 5. Verify fix
python -m pytest tests/security/test_recovery.py -v 2>&1 | tee logs/recovery_fixed.txt

# 6. Compare results
diff logs/recovery_initial.txt logs/recovery_fixed.txt

# 7. If successful, archive logs
mkdir -p logs/archive/2025-11-26_recovery_fix/
mv logs/recovery_*.txt logs/archive/2025-11-26_recovery_fix/
```

#### 8.6 Integration with CI/CD

**GitHub Actions Example:**
```yaml
- name: Run Tests with Log Capture
  run: |
    mkdir -p logs
    python -m pytest -v --tb=long 2>&1 | tee logs/ci_test_output.txt
  
- name: Upload Logs on Failure
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: test-failure-logs
    path: logs/
```

---

## 9. INCIDENT REPORT: Task 4.4 Deployment Failure (2025-11-23)

**Root Cause:** Missing `pytest.ini` configuration for asyncio tests.

**Impact:** Correct KMS implementation blocked by environment setup issues.

**Resolution:** 
1. Created `pytest.ini` with mandatory asyncio configuration
2. Updated Engineering Playbook with Testing Standard (Section 7)
3. Established acceptance criteria for test suite requirements

**Prevention:** All future async projects MUST follow Rule #5 (Pytest Configuration Protocol).

**Lessons Learned:**
- Environment configuration is as critical as code logic
- Testing standards must be documented and enforced
- Acceptance criteria must include environment setup verification

---

### Rule #10: The Fallback Protocol 🛡️
- **Problem:** When a C-library (like `libsodium`) is missing, the fallback Python code often behaves differently (e.g., Mutation issues).
- **Mandate:**
  1. Any code with a `try...except ImportError` fallback MUST have a specific Test Case for the Fallback Path.
  2. **QA MUST** verify logic integrity in both environments (With and Without the library).
  3. **NEVER** assume a Python fallback works exactly like the C function.
- **Example:**
  ```python
  # ❌ WRONG - Assuming fallback works
  try:
      import nacl.bindings
  except ImportError:
      # Blindly trusting pure python implementation
      pass

  # ✅ RIGHT - Explicit test requirement
  # Test Case: test_crypto_fallback_mode()
  # Environment: CI_NO_C_EXTENSIONS=1
  ```

---

### Rule #14: The Architectural Integrity Protocol 🏛️
- **Problem:** Tests fail because they use old APIs. Agent adds junk methods to Core to satisfy Tests.
- **Mandate:** NEVER modify Core Logic to please outdated Tests. If Core is right (per Spec), the Test is WRONG. Fix or Delete the Test.
- **Reason:** Tests serve the Architecture, not the other way around. Code integrity > Test compatibility.
- **Example:**
  ```python
  # ❌ WRONG - Adding garbage to Core to satisfy old test
  class KMS:
      def get_keys(self):  # Junk method added to please test
          return self._master_key
  
  # ✅ RIGHT - Fix the test instead
  # In test file: assert kms._master_key is not None
  ```

### Rule #15: The Atomic Verify Protocol ⚛️
- **Problem:** Syntax Errors (Indentation) halt the entire pipeline.
- **Mandate:** After editing ANY `.py` file, MUST run `python -m py_compile path/to/file.py` to check syntax BEFORE running pytest.
- **Reason:** Catch syntax errors immediately before they cascade into test failures.
- **Example:**
  ```bash
  # After editing kms.py
  python -m py_compile src/core/security/kms.py
  # Only if this passes, then run tests
  python -m pytest tests/
  ```

### Rule #16: The Ghost Protocol 👻
- **Problem:** Junk files (`debug_*.py`, `temp_*.py`, `CURRENT_ARCHITECTURE.md`) confuse the context.
- **Mandate:** Always scan and delete file ghosts before starting complex tasks.
- **Reason:** Stale files create false context and lead to hallucinations.
- **Example:**
  ```bash
  # Scan for ghosts
  find . -name "debug_*.py" -o -name "temp_*.py" -o -name "*_OLD.*"
  # Delete confirmed ghosts
  rm -f debug_*.py temp_*.py
  ```

### Rule #17: The Windows Persistence Protocol 🪟
- **Problem:** Windows file locking causes `[WinError 32]` in tests and production.
- **Mandate:**
  ```python
  # CRITICAL: Windows file operation sequence
  import gc
  import asyncio
  
  async def force_close_db():
      """Ensure database handles are released"""
      gc.collect()  # Force garbage collection
      await asyncio.sleep(1.0)  # Give OS time to release handles
  
  # Usage pattern
  async with aiosqlite.connect(db_path) as db:
      await db.execute("PRAGMA journal_mode=DELETE")  # Disable WAL
      await db.commit()
  
  del db  # Explicit deletion
  await force_close_db()
  
  # File operations with retry
  max_retries = 5
  for attempt in range(max_retries):
      try:
          if path.exists():
              path.unlink()
          shutil.move(str(temp_path), str(path))
          break
      except OSError:
          if attempt == max_retries - 1:
              raise
          time.sleep(0.5 * (attempt + 1))  # Exponential backoff
  ```
- **Reason:** Windows maintains file locks longer than Unix systems. Requires explicit resource management and retry logic.
- **Reference:** `docs/04_KNOWLEDGE/windows_file_locking.md`

### Rule #18: The Libsodium API Protocol 🔐
- **Problem:** AI hallucinations about libsodium binding signatures cause runtime errors.
- **Mandate:**
  ```python
  # ❌ HALLUCINATED (WRONG)
  state, header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(key)
  
  # ✅ CORRECT (VERIFIED)
  state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
  header = nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push(state, key)
  ```
- **Verification Command:**
  ```bash
  # ALWAYS verify libsodium API before commit
  python -c "
  import nacl.bindings
  help(nacl.bindings.crypto_secretstream_xchacha20poly1305_init_push)
  "
  ```
- **Reason:** Low-level C bindings require explicit state allocation. Never trust AI-generated signatures.
- **Reference:** `docs/04_KNOWLEDGE/libsodium_api_patterns.md`

### Rule #19: The Toxic Waste Disposal Protocol ☢️
- **Problem:** `VACUUM INTO` creates plaintext temporary files that are forensic risks.
- **Mandate:**
  ```python
  def secure_wipe_file(path: Path) -> None:
      """1-pass overwrite + rename + delete for forensic hygiene"""
      if not path.exists():
          return
      
      try:
          # 1. Overwrite with random data
          file_size = path.stat().st_size
          with open(path, "rb+") as f:
              f.write(os.urandom(file_size))
              f.flush()
              os.fsync(f.fileno())
          
          # 2. Obfuscate with random name
          temp_name = path.parent / f"{uuid.uuid4()}.tmp"
          path.rename(temp_name)
          
          # 3. Delete
          temp_name.unlink()
          
      except Exception:
          # Fallback: delete if overwrite fails
          if path.exists():
              try: path.unlink()
              except: pass
  
  # Usage in finally blocks
  try:
      temp_db = create_temp_database()
      process_sensitive_data(temp_db)
  finally:
      secure_wipe_file(temp_db)  # MANDATORY for sensitive temps
  ```
- **Reason:** Standard `unlink()` leaves forensic traces. Secure wiping prevents file recovery attacks.
- **Reference:** `docs/04_KNOWLEDGE/forensic_hygiene.md`

### Rule #20: The Atomic Snapshot Protocol ⚛️
- **Problem:** Database consistency during backup operations.
- **Mandate:**
  ```python
  # Use VACUUM INTO for atomic database snapshots
  async def create_atomic_snapshot(source_db: Path, temp_path: Path):
      loop = asyncio.get_running_loop()
      await loop.run_in_executor(None, _execute_vacuum_into, source_db, temp_path)
  
  def _execute_vacuum_into(source_db: Path, target_db: Path):
      """Synchronous VACUUM INTO in executor"""
      source_uri = f"file:{source_db.resolve()}?mode=ro"
      target_path = str(target_db.resolve())
      
      with sqlite3.connect(source_uri, uri=True) as conn:
          conn.execute(f"VACUUM INTO '{target_path}'")
  ```
- **Reason:** `VACUUM INTO` creates consistent point-in-time snapshot without locking source database.
- **Reference:** SQLite documentation on VACUUM INTO (atomic operation)

---

## 🔄 PKSF WORKFLOW INTEGRATION

### SOLR Reflection Process (After Each Major Task)

**Purpose:** Convert battlefield lessons into institutional knowledge

**Template:**
```markdown
## SOLR: Task X.Y Retrospective

### 1. Loss Function Analysis
**L¹ (Objective):** [Goal] ✅/❌ [Status]  
**L² (Efficiency):** [Metric] ✅/❌ [Assessment]

### 2. Root Cause
- **Technical:** [What went wrong technically]
- **Process:** [What went wrong in workflow]
- **Knowledge:** [What was missing from documentation]

### 3. Titan Formation (Knowledge Promotion)
**FROM Layer 1 (Volatile):** "[Specific implementation detail]"  
**TO Layer 2 (Stable):** "[General pattern/rule]" (Rule #X)

### 4. Integration
- Updated Engineering Playbook with new protocols
- Created verification commands for critical operations
- Established patterns for future tasks
```

### LAT Planning Framework (For Next Tasks)

**Purpose:** Decompose complex tasks using PKSF layers

**Template:**
```markdown
## LAT: Task X.Y - [Task Name]

### 1. Decomposition (Break into components)
- Component A: [Description]
- Component B: [Description]

### 2. Processing (Map to PKSF layers)
- Layer 3 Alignment: [How does this serve first principles?]
- Layer 2 Frameworks: [Which stable patterns apply?]
- Layer 1 Implementation: [Specific code/config]

### 3. Synthesis (Integration plan)
- Write specs based on existing interfaces
- Create test plan verifying requirements
- Document new patterns for future reuse
```

---

## 🏗️ UPDATED PROJECT STRUCTURE (PKSF-ALIGNED)

```
E:/DEV/Convert/
├── docs/
│   ├── 00_CONTEXT/              # Layer 3: Vision, Mission, Principles
│   ├── 01_ARCHITECTURE/         # Layer 2: MDS_v3.14.md, ADRs, Frameworks
│   ├── 02_PLANS/                # Roadmaps, Sprint Planning
│   ├── 03_SPECS/                # Technical Specifications
│   ├── 04_KNOWLEDGE/            # ⭐ NEW: Battlefield Lessons (PKSF Layer 1→2)
│   │   ├── windows_file_locking.md
│   │   ├── libsodium_api_patterns.md
│   │   └── forensic_hygiene.md
│   └── 05_OPERATIONS/           # This Engineering Playbook
├── src/
│   └── core/
│       ├── api/                 # Bridge Layer (Tauri Commands)
│       ├── security/            # Omega Security Standards
│       ├── services/            # Business Logic (Backup, Recovery)
│       ├── storage/             # Data Layer (SQLite)
│       ├── ui/                  # Presentation Layer  
│       └── utils/               # Utilities, Security Factory
```

---

## 🧪 VERIFICATION PROTOCOLS

### Pre-Commit Checklist
- [ ] `python -m py_compile` on all modified .py files
- [ ] Libsodium API signatures verified against documentation
- [ ] Windows file operations include retry logic
- [ ] Temporary sensitive files use `secure_wipe_file()`
- [ ] Atomic operations for database consistency
- [ ] All tests pass: `python -m pytest tests/ -v`

### Post-Task SOLR Analysis
- [ ] Loss function evaluation completed
- [ ] Root causes identified and documented  
- [ ] Knowledge promoted to appropriate PKSF layer
- [ ] Engineering Playbook updated with new rules
- [ ] Knowledge base documents created in `docs/04_KNOWLEDGE/`

---

## 🎯 CRITICAL SUCCESS FACTORS

1. **Never Trust AI-Generated API Signatures** - Always verify against source documentation
2. **Windows ≠ Unix** - Assume different file locking behavior, implement retry logic
3. **Temporary = Toxic** - All temp files with sensitive data require secure disposal  
4. **Atomic Over Everything** - Database operations must maintain consistency
5. **Document Battlefield Lessons** - Convert Layer 1 pain into Layer 2 patterns

---

## 🤖 MULTI-AGENT ORCHESTRATION PROTOCOL

### Agent Roles & Responsibilities

**Principle:** Separate internal (context-aware) agents from external (raw intelligence) agents.

#### Business & Strategy Layer
- **Co-Product Manager:** Gemini 3.0 Pro A (Antigravity internal)
  - Defines product requirements and user stories
  - Prioritizes features based on business value
  - Reviews implementation against business goals
  
- **Business Analyst:** Claude 4.5 A (Antigravity internal)
  - Analyzes requirements for technical feasibility
  - Creates functional specifications
  - Validates business logic implementation

#### Design & Research Layer
- **UX Researcher:** Claude 4.5 B (Web external)
  - Conducts user research and competitive analysis
  - Provides raw intelligence without project context
  - Generates research reports for internal agents
  
- **UI/UX Designer:** Gemini 3.0 Pro B (Antigravity internal)
  - Creates design specifications with full context
  - Ensures consistency with existing design system
  - Reviews frontend implementations

#### Technical Leadership Layer
- **System Architect:** ChatGPT 5.1 (Antigravity internal)
  - Defines system architecture and patterns
  - Reviews technical decisions against MDS_v3.14
  - Ensures architectural integrity (Rule #14)
  
- **Security Architect:** Grok 4 (Web external)
  - Provides security best practices and threat modeling
  - Reviews cryptographic implementations
  - No access to proprietary security implementations

- **Backend Lead:** DeepSeek V3.2 A (Web external)
  - Generates backend code based on specifications
  - Provides raw implementation without context
  - Code reviewed by internal agents before integration

#### Execution & Quality Layer
- **Frontend Lead:** DeepSeek V3.2 B (Web external)
  - Generates frontend code based on design specs
  - Implements UI components
  - Code reviewed by internal agents before integration

- **QA/QC Lead:** Gemini 3.0 Pro D (Antigravity internal)
  - Creates test plans with full project context
  - Reviews test coverage and quality metrics
  - Validates implementations against specifications

- **Code Reviewer:** Claude 4.5 C (Antigravity internal)
  - Final review before GitHub commit
  - Ensures compliance with Engineering Playbook
  - Verifies all acceptance criteria met

### Decision-Making Protocol

**Critical Decisions (Architecture, Security, Breaking Changes):**
1. **Proposal:** System Architect or Security Architect proposes solution
2. **Debate:** Two agents (different models) provide counterarguments
3. **Review:** One agent (third model) synthesizes and recommends
4. **Approval:** Human user makes final decision

**Example Flow:**
```
[Critical Decision: Change KMS API]
1. System Architect (ChatGPT 5.1): Proposes renaming initialize_vault → initialize
2. Counterargument A (Claude 4.5 A): Warns about breaking changes in tests
3. Counterargument B (Gemini 3.0 Pro A): Suggests deprecation path
4. Reviewer (Claude 4.5 C): Synthesizes: "Rename is correct per spec, update tests"
5. Human: Approves with mandate to update all affected tests
```

### Agent Coordination Rules

**Internal Agents (Antigravity):**
- ✅ Full access to project context (MDS, specs, codebase)
- ✅ Can make decisions within established patterns
- ✅ Update documentation and artifacts
- ❌ Cannot violate Engineering Playbook rules

**External Agents (Web):**
- ✅ Provide raw intelligence and code generation
- ✅ Research best practices and external patterns
- ❌ No access to proprietary implementations
- ❌ Output must be reviewed by internal agents

### Workflow Integration

**Standard Task Flow:**
```
1. Business Analyst (Internal) → Creates spec from user request
2. System Architect (Internal) → Reviews spec, defines approach
3. Backend/Frontend Lead (External) → Generates implementation
4. QA Lead (Internal) → Creates test plan with context
5. Code Reviewer (Internal) → Final review before commit
```

**Security-Critical Task Flow:**
```
1. Security Architect (External) → Provides threat model
2. System Architect (Internal) → Adapts to project architecture
3. Backend Lead (External) → Implements security controls
4. Security Architect (External) → Reviews implementation
5. Code Reviewer (Internal) → Verifies compliance with Omega standards
6. Human → Final approval for security-critical changes
```

---

*This document serves as the Constitutional Law for all Agents (Gemini, Claude, ChatGPT, DeepSeek, Grok).*

*"We don't repeat mistakes - we institutionalize learning"*


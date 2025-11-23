# ENGINEERING PLAYBOOK: THE CONVERT PROTOCOL
> **Status:** LIVING DOCUMENT
> **Last Updated:** Sprint 3 - Batch 1 (Infrastructure)
> **Context:** Windows 11 / Python 3.14 / Git Bash

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
  - **Update Docs/Task List -> Create Dummy File -> Code -> Commit.**
  - Không commit file `walkthrough.md` nếu chưa thực sự tạo nó.

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

## 8. INCIDENT REPORT: Task 4.4 Deployment Failure (2025-11-23)

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

*This document serves as the Constitutional Law for all Agents (Gemini, DeepSeek, Claude).*

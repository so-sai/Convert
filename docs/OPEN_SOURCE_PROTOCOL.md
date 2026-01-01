# 📘 GIAO THỨC ĐÓNG GÓP OPEN SOURCE (OSS PROTOCOL)

> **Đúc kết từ:** Chiến thắng SQLCipher 4.12.0 PR (December 2025)  
> **Mục đích:** Hướng dẫn chuẩn mực cho mọi đóng góp Open Source từ Convert Team  
> **Áp dụng cho:** Python, Rust, JavaScript/TypeScript, C/C++ projects

---

## I. NGUYÊN TẮC VÀNG: "RECIPE VS. CAKE"

Khi đóng góp code (PR), hãy nhớ kỹ sự khác biệt:

| LOẠI | VÍ DỤ | QUY TẮC |
|:-----|:------|:--------|
| **RECIPE (Công thức)** | `setup.py`, `Makefile`, `.rs`, `.js`, `.svelte` | ✅ **COMMIT**. Đây là cái Maintainer cần. |
| **INGREDIENTS (Nguyên liệu)** | `sqlite3.c` (Amalgamation), File ZIP, Ảnh gốc | ⚠️ **HẠN CHẾ**. Chỉ commit nếu Repo gốc yêu cầu. |
| **CAKE (Bánh chín)** | `.pyd`, `.dll`, `.exe`, `build/`, `dist/`, `node_modules/` | 🛑 **CẤM TUYỆT ĐỐI**. Đây là rác. |

### Nguyên tắc áp dụng:
- **SQLCipher Case Study:** File `sqlite3.c` (9.5MB) là **INGREDIENTS**, không phải source code → Không commit
- **Svelte 5 Future:** Chỉ commit `.svelte`, `.ts`, không commit `build/`, `.svelte-kit/`
- **Rust Future:** Chỉ commit `.rs`, `Cargo.toml`, không commit `target/`

---

## II. QUY TRÌNH "PHẪU THUẬT" PR (SURGICAL COMMIT)

Để tránh bị Reject vì "rác", luôn tuân thủ 3 bước trước khi Push:

### 1. Verification (Nghiệm thu Local)

**Checklist:**
- [ ] Build thành công trên máy local
- [ ] Tạo ra sản phẩm hoạt động (`.pyd`, `.exe`, `.wasm`, etc.)
- [ ] Chạy test suite → Tất cả PASS
- [ ] Verify trên môi trường sạch (fresh clone nếu có thể)

**Mẹo:**
- Nếu cần file nguyên liệu (như `amalgamation/`) để build, cứ copy vào máy
- **NHƯNG:** Đừng `git add` chúng vào staging area

**Example:**
```bash
# SQLCipher case
python setup.py build_ext --inplace  # Build local
python test_wheel_install.py         # Verify
# ✅ Thấy SUCCESS → OK để tiếp tục
```

### 2. Isolation (Cách ly)

**Trước khi `git add`, chạy ngay:**

```bash
# Kiểm tra xem có file rác nào đang chờ không
git status

# Bỏ file to/rác ra khỏi staging (nếu lỡ tay)
git reset HEAD amalgamation/
git reset HEAD build/
git reset HEAD dist/

# Cập nhật rào chắn .gitignore
echo "amalgamation/" >> .gitignore
echo "*.pyd" >> .gitignore
echo "*.so" >> .gitignore
echo "*.dll" >> .gitignore
echo "build/" >> .gitignore
echo "dist/" >> .gitignore
echo "*.egg-info/" >> .gitignore
```

**Quy tắc vàng:**
- `.gitignore` phải được cập nhật **TRƯỚC** khi bắt đầu code
- Luôn kiểm tra `git status` trước mỗi commit
- Nếu thấy file > 1MB trong danh sách → **STOP & REVIEW**

### 3. Precision Strike (Commit chính xác)

**TUYỆT ĐỐI KHÔNG dùng `git add .` khi đang làm PR!**

**Cách đúng:**
```bash
# Kiểm tra lần cuối
git status

# Chỉ add file code đã sửa đổi (chỉ đích danh)
git add setup.py
git add .gitignore
git add src/module.py  # Nếu có

# Commit với message rõ ràng
git commit -m "fix(windows): Add missing system libraries for MSVC build"

# Kiểm tra diff trước khi push
git diff HEAD~1

# Push
git push origin feature-branch
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `fix`: Bug fix
- `feat`: New feature
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Updating build tasks, package manager configs, etc.

---

## III. BÀI HỌC XƯƠNG MÁU (LESSONS LEARNED)

### 1. AI Orchestration (Phân vai rõ ràng)

**Cursor/Claude (Brain - Não):**
- ✅ Viết code, thiết kế logic
- ✅ Lên kế hoạch test
- ✅ Review code, phân tích lỗi
- ✅ Tạo documentation

**Terminal/Git Bash (Muscle - Tay):**
- ✅ Chạy lệnh Build nặng
- ✅ Thực thi Git commands
- ✅ Run test suite
- ✅ Deploy/Package

**Nguyên tắc:**
- Không bắt AI chạy lệnh build nặng (sẽ timeout/crash)
- Không để AI tự động commit/push (cần human review)
- AI đề xuất → Human verify → Human execute

### 2. Hardcode là Chân ái (Khi cần thiết)

**Vấn đề:** AI config đường dẫn phức tạp với nhiều if/else → Dễ lỗi

**Giải pháp:** Hardcode đường dẫn rõ ràng khi cần

**Example (SQLCipher):**
```python
# ❌ BAD: Phức tạp, dễ lỗi
if platform.system() == 'Windows':
    if os.path.exists('amalgamation'):
        sources = glob.glob('amalgamation/*.c')
    else:
        sources = ['src/module.c']
else:
    sources = find_sources_recursive()

# ✅ GOOD: Rõ ràng, chắc chắn
sources = [
    'amalgamation/sqlite3.c',  # 9.5MB amalgamation
    'src/module.c',
    'src/connection.c',
    # ... list đầy đủ
]
```

**Khi nào nên hardcode:**
- Đường dẫn file quan trọng (source files)
- Thư viện hệ thống (system libraries)
- Compiler flags cố định

**Khi nào KHÔNG nên:**
- User-specific paths (home directory, etc.)
- Dynamic configuration
- Environment-dependent settings

### 3. Git History là Kho báu

**Lỡ xóa file quan trọng?**

```bash
# Tìm commit cuối cùng có file đó
git log --all --full-history -- path/to/file

# Restore từ commit trước khi xóa
git checkout <commit_hash>~1 -- path/to/file

# Hoặc xem nội dung mà không restore
git show <commit_hash>:path/to/file
```

**Example (SQLCipher case):**
```bash
# File sqlite3.c bị xóa ở commit 6794294
git log --all -- sqlcipher3/sqlite3.c

# Restore từ commit trước đó
git checkout 6794294~1 -- sqlcipher3/sqlite3.c
```

### 4. "Leave it High" - Dừng ở đỉnh cao

**Nguyên tắc:**
- Khi PR đã sạch đẹp → STOP
- Đừng "cải tiến" thêm khi không cần thiết
- Mỗi thay đổi = Thêm rủi ro

**SQLCipher Example:**
- PR đã có 2 files: `setup.py`, `.gitignore` → **PERFECT**
- Không thêm test scripts (giữ local)
- Không restore amalgamation files (không cần)
- **Result:** Clean PR → High chance of merge

### 5. Định luật "Maintainer's Dilemma" (Bài học OpenSSL)

**Tình huống:** Code đóng góp (PR) tốt hơn về mặt kỹ thuật (OpenSSL 3.x, C11, hiệu năng cao), nhưng Maintainer không merge nguyên bản mà chọn giải pháp an toàn hơn (Amalgamation default, vẫn hỗ trợ OpenSSL cũ).

**Phân tích:**

**Góc nhìn Contributor (Chúng ta):** Ưu tiên **"Production-Optimized"**
- Cần hiệu năng cao nhất
- Bảo mật mới nhất (OpenSSL 3.x)
- Chạy tốt nhất trên môi trường hiện đại (Windows 11, Python 3.14)
- Tối ưu cho use case cụ thể

**Góc nhìn Maintainer (Upstream):** Ưu tiên **"Maintenance-Safe"**
- Phải gánh trách nhiệm cho hàng ngàn người dùng
- Hỗ trợ cả môi trường cũ (Windows 7, OpenSSL 1.x)
- Sợ "Breaking Changes" hơn là cần tính năng mới
- Tối ưu cho compatibility rộng nhất

**Hành động chuẩn mực:**

1. **Tôn trọng:** Không ép Upstream phải theo chuẩn cao của mình nếu điều đó làm khó họ trong việc bảo trì.

2. **Giữ lại (Fork/Internal Build):** Tiếp tục sử dụng bản build tối ưu ("hàng may đo") cho dự án của mình để đảm bảo chất lượng Production.

3. **Đóng PR đẹp:** Rút lui với lời cảm ơn và để lại giải pháp như một tài liệu tham khảo (Reference) cho cộng đồng.

4. **Kết quả:** Ta có bản build xịn cho ta, cộng đồng có bản build ổn định cho họ. **Win-Win.**

**SQLCipher Case Study:**
- **Our build:** OpenSSL 3.x + C11 + Windows-specific optimizations → Production-grade
- **Upstream choice:** Amalgamation + OpenSSL 1.x compatibility → Maintenance-safe
- **Outcome:** We maintain our optimized fork, they maintain stable upstream
- **Lesson:** Different goals require different solutions. Both are valid.

---

## IV. MẪU PR CHUẨN (TEMPLATE)

### Title Format:
```
<type>(<scope>): <clear description>
```

**Examples:**
- `fix(windows): Add missing system libraries for MSVC build`
- `feat(build): Add support for OpenSSL 3.x on Windows`
- `docs(readme): Update installation instructions for Windows`

### Description Template:

```markdown
## Summary
Brief explanation of what this PR does (1-2 sentences).

## Problem
Why was this fix/feature needed?

**Before:**
- Build failed on Windows with error X
- Missing library Y caused Z

**After:**
- Build succeeds on Windows
- All tests pass

## Solution
- Added system libraries: `ws2_32`, `advapi32`, `crypt32`, `user32`, `gdi32`
- Updated `setup.py` to detect Windows platform
- Modified `.gitignore` to exclude build artifacts

## Testing
✅ **Environment:** Windows 11 x64, Python 3.14.0a2, MSVC 2022  
✅ **Build:** Static build successful (`.pyd` ~1.8MB)  
✅ **Tests:** All verification tests passed  
✅ **Verification:**
```python
import sqlcipher3.dbapi2 as sqlite
conn = sqlite.connect(':memory:')
conn.execute("PRAGMA key = 'test'")
# ✅ Works perfectly
```

## Breaking Changes
None / List any breaking changes here

## Related Issues
Fixes #123 (if applicable)
```

---

## V. CHECKLIST TRƯỚC KHI SUBMIT PR

### Pre-Commit Checklist:
- [ ] Code builds successfully on local machine
- [ ] All tests pass
- [ ] No build artifacts in staging area (`git status` clean)
- [ ] `.gitignore` updated to exclude new artifacts
- [ ] Only modified source files are staged
- [ ] Commit message follows convention
- [ ] No files > 1MB in commit (unless absolutely necessary)

### Pre-Push Checklist:
- [ ] Reviewed `git diff` one more time
- [ ] Checked "Files Changed" count (should be minimal)
- [ ] PR description is clear and complete
- [ ] No typos in PR title/description
- [ ] Linked related issues (if any)

### Post-Push Checklist:
- [ ] Verified PR on GitHub web interface
- [ ] Checked "Files Changed" tab
- [ ] Ensured CI/CD passes (if applicable)
- [ ] Responded to any automated checks/bots

---

## VI. CASE STUDY: SQLCIPHER 4.12.0 PR

### The Challenge:
- SQLCipher build failed on Windows with Python 3.14 No-GIL
- Missing system libraries
- Amalgamation file confusion

### The Solution:
**Files Changed: 2**
1. `setup.py` - Added Windows-specific libraries and logic
2. `.gitignore` - Excluded build artifacts

**What was NOT committed:**
- ❌ `sqlite3.c` (9.5MB amalgamation file)
- ❌ `build/` directory
- ❌ Test scripts
- ❌ `.pyd` binary

### The Result:
✅ Clean PR  
✅ Professional description  
✅ High chance of merge  
✅ **VICTORY!** 🏆

### Key Takeaways:
1. **Recipe not Cake** - Only commit source code changes
2. **Minimal Changes** - 2 files is better than 20 files
3. **Clear Description** - Maintainer understands immediately
4. **Local Verification** - Tested thoroughly before submitting

---

## VII. CÔNG CỤ HỖ TRỢ

### Git Aliases (Thêm vào `~/.gitconfig`):

```ini
[alias]
    # Kiểm tra nhanh
    st = status --short
    
    # Xem diff trước khi commit
    dc = diff --cached
    
    # Commit với template
    cm = commit -m
    
    # Unstage tất cả
    unstage = reset HEAD --
    
    # Xem lịch sử file
    filelog = log --follow --patch --
    
    # Kiểm tra file size
    ls-large = !git ls-files | xargs ls -lh | awk '{if ($5 > 1000000) print $9, $5}'
```

### Pre-commit Hook (`.git/hooks/pre-commit`):

```bash
#!/bin/bash
# Kiểm tra file lớn trước khi commit

MAX_SIZE=1048576  # 1MB in bytes

for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt $MAX_SIZE ]; then
            echo "❌ ERROR: File $file is larger than 1MB ($size bytes)"
            echo "   Please add to .gitignore or compress it"
            exit 1
        fi
    fi
done

echo "✅ All files are within size limit"
exit 0
```

---

## VIII. TÀI LIỆU THAM KHẢO

### Internal Docs:
- [SQLCIPHER_BUILD_MANIFESTO.md](file:///e:/DEV/app-desktop-Convert/docs/BUILD_GUIDES/SQLCIPHER_BUILD_MANIFESTO.md) - Build process details
- [PROJECT_SOP_v1.0.md](file:///e:/DEV/app-desktop-Convert/PROJECT_SOP_v1.0.md) - Project standards

### External Resources:
- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
- [GitHub PR Best Practices](https://github.com/blog/1943-how-to-write-the-perfect-pull-request)

---

## IX. SPRINT 7 PREVIEW: APPLYING THESE LESSONS

### Svelte 5 Contributions:
- ✅ Only commit `.svelte`, `.ts` files
- ✅ Exclude `.svelte-kit/`, `build/`, `node_modules/`
- ✅ Test locally before PR
- ✅ Keep PRs focused and minimal

### Rust Contributions:
- ✅ Only commit `.rs`, `Cargo.toml` files
- ✅ Exclude `target/`, `Cargo.lock` (for libraries)
- ✅ Run `cargo test` before PR
- ✅ Follow Rust API guidelines

---

**Document Version:** 1.0  
**Created:** 2025-12-31  
**Last Updated:** 2025-12-31  
**Status:** 🏆 **PRODUCTION-READY**  
**Next Review:** Before Sprint 7 (Svelte 5 integration)

---

**🎆 HAPPY NEW YEAR 2026! 🇻🇳**

*This protocol is the legacy of Sprint 6 victory. Use it wisely for all future open source contributions.*

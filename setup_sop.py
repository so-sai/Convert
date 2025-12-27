"""
SOP v1.0 Setup Script for app-desktop-Convert
Tạo cấu trúc .project-context theo chuẩn Isolated Intelligence Protocol
"""
import os
from pathlib import Path

def setup_convert_sop():
    base_dir = Path(".")
    
    # 1. Tạo cấu trúc thư mục não bộ
    context_dir = base_dir / ".project-context"
    archive_dir = context_dir / "ARCHIVE"
    context_dir.mkdir(exist_ok=True)
    archive_dir.mkdir(exist_ok=True)
    print(f"✅ [DIR] Created: {context_dir}")

    # 2. Tạo HIẾN PHÁP (PROJECT_PROMPT.md) - Đã tùy chỉnh cho Convert
    prompt_content = """# SYSTEM CONTEXT: app-desktop-Convert

## 1. IDENTITY (ĐỊNH DANH)
- **Project:** Convert (Local-First Knowledge System).
- **Goal:** 0.1s latency, 10-file conversion, AI on-device.
- **Stack:** 
  - **Brain:** Python 3.14 (No-GIL) + SQLite (WAL Strict) + FastAPI.
  - **Muscle:** Tauri v2 (Rust) - Windowing & System.
  - **Face:** Svelte 5 + Tailwind (Sensory Layer).
- **Owner:** Sếp (Architect) & AI Agents (Implementers).

## 2. BOUNDARIES (BIÊN GIỚI)
- **Phạm vi Code:**
  - `src/core` -> Python Logic (Watchdog, Converters).
  - `src-tauri` -> Rust System (Window, OS).
  - `src-ui` -> Svelte Interface.
- **The Constitution (BẤT BIẾN):**
  - NO Linux-isms (dùng Python scripts thay shell).
  - STRICT Typing (Pydantic v2, SQLite INTEGER).
  - NON-BLOCKING UI (Async/Threaded I/O).

## 3. RULES OF ENGAGEMENT
- **TDD First:** Core modules (Watchdog, Queue) phải có Test trước Code.
- **Protocol:** Đọc `ACTIVE_MISSION.md` -> Viết Test (Red) -> Viết Code (Green) -> Refactor.
- **Stop & Ask:** Thiếu Spec -> Hỏi. Không tự bịa.

## 4. DEFINITION OF DONE
- [ ] Runtime: No errors.
- [ ] Tests: pytest PASSED.
- [ ] Artifacts: Screenshot/Logs confirmed.
"""
    (context_dir / "PROJECT_PROMPT.md").write_text(prompt_content, encoding="utf-8")
    print("✅ [FILE] Created: PROJECT_PROMPT.md (The Constitution)")

    # 3. Tạo LỆNH BÀI SPRINT 6 (ACTIVE_MISSION.md)
    mission_content = """# MISSION: SPRINT 6 - TASK 6.1 - WATCHDOG CORE

## 1. CONTEXT
Hệ thống cần File Watcher thông minh để giám sát thư mục dữ liệu, xử lý vấn đề Spam Events và Zombie Threads.

## 2. SCOPE
**Files allowed:**
- `tests/services/test_watchdog.py` (New)
- `src/core/services/watchdog.py` (New)
- `scripts/init_watchdog_tdd.py` (New)

**Forbidden:**
- `src-ui/*`, `src-tauri/*`

## 3. TASKS
- [ ] Run `scripts/init_watchdog_tdd.py` to create Test Skeleton.
- [ ] Run `pytest` -> CONFIRM FAIL (Red).
- [ ] Implement `WatchdogService` (Debounce, ThreadPool).
- [ ] Run `pytest` -> CONFIRM PASS (Green).

## 4. ACCEPTANCE
- [ ] All tests in `tests/services/test_watchdog.py` passed.
- [ ] Artifact: Screenshot of pytest output showing GREEN.
"""
    (context_dir / "ACTIVE_MISSION.md").write_text(mission_content, encoding="utf-8")
    print("✅ [FILE] Created: ACTIVE_MISSION.md (Sprint 6.1 Mission)")

    # 4. Cập nhật .gitignore (Để mỗi người làm việc độc lập)
    gitignore = base_dir / ".gitignore"
    entry = "\n# SOP v1.0 Context\n.project-context/ACTIVE_MISSION.md\n"
    
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if ".project-context/ACTIVE_MISSION.md" not in content:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write(entry)
            print("✅ [GIT] Updated: .gitignore")
        else:
            print("ℹ️  [GIT] .gitignore already contains SOP entry")
    else:
        with open(gitignore, "w", encoding="utf-8") as f:
            f.write(entry)
        print("✅ [GIT] Created: .gitignore")

    print("\n" + "="*60)
    print("🎯 SOP v1.0 SETUP COMPLETE!")
    print("="*60)
    print("\nCấu trúc đã tạo:")
    print("  .project-context/")
    print("  ├── PROJECT_PROMPT.md    (Hiến pháp)")
    print("  ├── ACTIVE_MISSION.md    (Lệnh bài Sprint 6.1)")
    print("  └── ARCHIVE/             (Kho lưu trữ)")
    print("\nBước tiếp theo:")
    print("  1. Review file .project-context/PROJECT_PROMPT.md")
    print("  2. Review file .project-context/ACTIVE_MISSION.md")
    print("  3. Chạy: git add . && git commit -m 'chore: init SOP v1.0'")
    print("="*60)

if __name__ == "__main__":
    setup_convert_sop()

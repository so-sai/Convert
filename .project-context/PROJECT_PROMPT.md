# SYSTEM CONTEXT: app-desktop-Convert

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

## 5. IMPORT & PATHING RULES (BẮT BUỘC)
- **Import Path:** Mọi import trong code và test phải bắt đầu từ `src.`
  - ✅ Đúng: `from src.core.services.watchdog import WatchdogService`
  - ❌ Sai: `from services.watchdog import Watchdog`
- **PYTHONPATH:** Sử dụng `PYTHONPATH=.` hoặc `pytest.ini` với `pythonpath = .`
- **Path Normalization:** Ép toàn bộ path về `Path(p).as_posix()` cho cross-platform.
- **Package Structure:** Mọi thư mục Python cần có `__init__.py`.

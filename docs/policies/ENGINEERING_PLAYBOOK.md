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

---
*This document serves as the Constitutional Law for all Agents (Gemini, DeepSeek, Claude).*

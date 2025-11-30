# 🏛️ ENGINEERING PLAYBOOK: THE CONVERT PROTOCOL (COMBAT EDITION V2)
> **Status:** ENFORCED | **Context:** Windows 11 / Python 3.14 / Rust Tauri v2

## 1. THE IRON RULES (LUẬT BẤT BIẾN - LAYER 3)
1.  **Monorepo Law:** Code nghiệp vụ -> `src/core`. Code bảo mật Rust -> `src-tauri`. Cấm tạo folder `sprint-xx`.
2.  **Windows Execution:** LUÔN dùng `python -m <module>`. CẤM dùng `pip install` trực tiếp.
3.  **Anti-Buffer Overflow:** 
    *   CẤM paste code > 10 dòng trực tiếp vào Terminal (Git Bash).
    *   BẮT BUỘC dùng Python Script (`open(..., 'w')`) hoặc Notepad để sửa file dài.
4.  **Zero-Trust:** Frontend (Svelte) là "mù" (Blind). Backend không bao giờ gửi Raw Secret ra UI.

## 2. CODING STANDARDS (QUY CHUẨN CODE - LAYER 2)
### Rule #17: Windows Persistence (File I/O)
*   **Mandate:** Mọi thao tác File/DB phải có `try...except [WinError 32]` với `retry` và `gc.collect()`.

### Rule #18: Libsodium Integrity
*   **Mandate:** Không tin tưởng API do AI gợi ý. Phải verify signature trước khi commit.

### Rule #19: Toxic Waste (Dọn rác)
*   **Mandate:** File tạm chứa dữ liệu nhạy cảm phải được `secure_wipe` (ghi đè -> đổi tên -> xóa).

### Rule #20: Atomic Operations
*   **Mandate:** Backup DB bắt buộc dùng `VACUUM INTO`. Cấm copy file `.db` đang mở.

### Rule #21: Signature Alignment (MỚI)
*   **Mandate:** Trước khi Implement, phải đọc file Test (`tests/...`) để:
    1.  Copy đúng tên hàm (Import Name).
    2.  Copy đúng tham số đầu vào (Arguments).
    *   *Bài học xương máu:* `create_backup` thiếu tham số callback, `derive_recovery_key` thiếu hàm.

## 3. THE TRI-CHECK PROTOCOL (QUY TRÌNH PHỐI HỢP AI - MỚI)
Mọi tính năng quan trọng phải đi qua 3 bước:
1.  **EXECUTION (DeepSeek/Web):** Viết code thô, xử lý logic phức tạp, không tốn Token bộ nhớ.
2.  **CONTEXT CHECK (Gemini/Antigravity):** Đối chiếu code vừa viết với Codebase hiện tại (Check import, check path).
3.  **APPROVAL (Claude/GPT-5):** Review lần cuối về Security & Architecture trước khi Commit.

## 4. WORKFLOWS (QUY TRÌNH KIỂM TRA)
### Verification Checklist (Trước khi Commit)
- [ ] `python -m py_compile` (Check Syntax - Tránh lỗi Copy/Paste).
- [ ] `python -m pytest` (Check Logic - Bắt buộc Xanh 100%).
- [ ] Check `git status` để không commit file rác (`.spec`, `fix_*.py`).

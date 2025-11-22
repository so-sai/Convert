# GIT WORKFLOW PROTOCOL: ZERO-TRASH POLICY
> **Context:** MDS Project Convert
> **Enforcement:** STRICT

## GIAI ĐOẠN 0: KHỞI TẠO NỀN TẢNG (BẮT BUỘC)
Mục tiêu: Ngăn chặn file rác (.venv, build, __pycache__) lọt vào Git.

1. **Kiểm tra .gitignore đầu tiên:**
   Trước khi `git add` bất cứ thứ gì, phải chắc chắn `.gitignore` đã chặn các thư mục rác.
   
2. **Cấm kỵ:**
   - ❌ KHÔNG BAO GIỜ chạy `git add .` khi chưa kiểm tra `git status`.
   - ❌ KHÔNG commit thư mục `build/`, `dist/`, `.venv/`.

## GIAI ĐOẠN 1: CHU KỲ PHÁT TRIỂN (ATOMIC COMMITS)
Mục tiêu: Commit nhỏ, rõ ràng.

1. **Quy tắc chọn lọc:**
   - Chỉ add file liên quan: `git add src/core/plugin/loader.py`
   - Không add cả lố.

2. **Chuẩn Commit Message:**
   - `feat(scope): ...` : Tính năng mới
   - `fix(scope): ...` : Sửa lỗi
   - `docs(scope): ...` : Tài liệu
   - `chore(scope): ...` : Cấu hình, dọn dẹp

## GIAI ĐOẠN 2: AN TOÀN KHI PUSH
1. **Rebase trước khi Push:** Giữ lịch sử thẳng hàng.
2. **Test trước khi Push:** Chạy `python -m pytest` (Pass mới được Push).

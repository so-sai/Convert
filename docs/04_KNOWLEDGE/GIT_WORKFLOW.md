OMEGA VAULT: SOLO LEVELING PROTOCOL
Tư duy cốt lõi: "Tôi là hệ thống, hệ thống là tôi. Kỷ luật là sức mạnh."
Mục tiêu: Tốc độ tối đa - Rủi ro tối thiểu.
🏛️ GIAI ĐOẠN 0: THIẾT LẬP CHIẾN HÀO (Foundation)
Nguyên tắc: "Đừng bao giờ để chiến trường bừa bộn."
1. Bùa Hộ Mệnh .gitignore (BẤT KHẢ XÂM PHẠM)
Trước khi code, phải chắc chắn .gitignore đang hoạt động.
Chặn tuyệt đối: node_modules, target, __pycache__, .venv.
Giữ mạng sống: Cargo.lock, package-lock.json (Mất file này là mất sự ổn định).
2. Tạo Nhánh Nhanh (Fast Branching)
Đừng code trên main. Hãy tạo nhánh để có chỗ "đập đi xây lại" thoải mái.
Bash
# Cấu trúc đơn giản: <loại>/<tên-ngắn-gọn>
git checkout -b feat/backup-logic
# hoặc
git checkout -b fix/icon-error
🔨 GIAI ĐOẠN 1: TÁC CHIẾN (Coding & Atomic Commits)
Nguyên tắc: "Chia để trị. Đừng ăn một miếng quá to."
1. Code tập trung (Focus Fire)
Chỉ sửa một thứ tại một thời điểm.
Đang sửa Backend Python? Đừng tiện tay sửa luôn màu nút bấm bên Frontend.
Làm xong logic nào, commit ngay logic đó.
2. Atomic Commits (Quy tắc "Nút Undo")
Commit nhỏ giúp Sếp quay lại quá khứ dễ dàng nếu lỡ tay làm hỏng code.
❌ SAI (Cục to đùng):
Message: "Update code" (Chứa cả sửa lỗi backend, thêm nút frontend, sửa file config).
Hậu quả: Nếu Frontend lỗi, Sếp phải rollback cả Backend đang chạy ngon.
✅ ĐÚNG (Chia nhỏ):
Commit 1: feat(core): Add backup function
Commit 2: feat(ui): Add backup button
Commit 3: config: Update cargo.toml
🛡️ GIAI ĐOẠN 2: CHỐT CHẶN (The Trinity Test & Fast Merge)
Nguyên tắc: "Tin tưởng, nhưng phải kiểm chứng."
1. TRINITY TEST (Bộ 3 Bắt Buộc)
Đây là bước SỐNG CÒN. Vì Sếp solo, không ai kiểm tra giúp Sếp cả. Máy móc phải làm việc đó.
Trước khi nhập code vào main, hãy chạy lần lượt:
Python: pytest (Đảm bảo logic đúng).
Rust: cd src-tauri && cargo check (Đảm bảo không panic).
Frontend: npm run check (Đảm bảo không lỗi cú pháp JS).
👉 Nếu 1 trong 3 đỏ: DỪNG LẠI SỬA NGAY.
2. Fast Track Merge (Bỏ qua PR)
Test xanh rồi thì không cần tạo Pull Request làm màu nữa. Nhập thẳng vào main:
Bash
# 1. Quay về mẫu hạm
git checkout main

# 2. Cập nhật code mới nhất (đề phòng)
git pull origin main

# 3. Hợp nhất nhánh tính năng vào (Sát nhập)
git merge feat/backup-logic

# 4. Đẩy lên mây
git push origin main
🧹 GIAI ĐOẠN 3: DỌN DẸP (Cleanup)
Nguyên tắc: "Rời đi không để lại dấu vết."
Xóa nhánh đã xong:
Bash
git branch -d feat/backup-logic
Gom script rác:
Mọi file .py chạy một lần (như fix_icon.py) dùng xong phải xóa hoặc ném vào thư mục scripts/. Tuyệt đối không để ở thư mục gốc.
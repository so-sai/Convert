# 📘 GIAO THỨC TRÍ TUỆ PHÂN KHOANG (IIP)
**Isolated Intelligence Protocol**

**Phiên bản:** 1.0 (Final Frozen) | **Trạng thái:** Sẵn sàng vận hành  
**Áp dụng:** Hệ sinh thái Claude Code (Brain) + Google Antigravity (Hand) + GitHub.

---

## I. NGUYÊN TẮC CỐT LÕI (CORE PRINCIPLES)

### ✅ Nguyên tắc "Cửa Sổ Độc Lập" (Isolation):
- Mỗi cửa sổ IDE chỉ được mở **DUY NHẤT 1 DỰ ÁN**.
- **Cấm tuyệt đối** mở thư mục cha (Root) chứa nhiều dự án cùng lúc.
- **Mục đích:** Ngăn chặn AI "nhìn trộm" code của dự án khác gây ảo giác (hallucination).

### ✅ Nguyên tắc "Phân Vai Chuyên Biệt" (Specialization):
- **Claude (Kiến trúc sư):** Chỉ dùng để đọc hiểu và viết kế hoạch (.md). Hạn chế viết code.
- **Antigravity/Gemini (Thợ thi công):** Chỉ dùng để thực thi kế hoạch, viết code, chạy test.
- **GitHub (Kho lưu trữ):** Chỉ lưu Lịch sử (Code đã chạy được) và Luật (System Prompt).

### ✅ Nguyên tắc "Không Ghi Nhớ" (Zero-Memory):
- Không dựa vào trí nhớ của con người để biết dự án này làm gì.
- **Tên thư mục và tên file phải tự giải thích nội dung của nó.**

---

## II. QUY TẮC ĐỊNH DANH (NAMING CONVENTION)

Áp dụng bắt buộc để quản lý nhiều dự án.

### 1. Tên Thư mục Dự án

**Công thức:** `[LOẠI]-[VAI TRÒ]-[TÊN NGẮN]`

**LOẠI** (vai trò kiến trúc):
- `app` – Desktop application (Windows/macOS/Linux)
- `web` – Frontend (browser)
- `api` – Backend API
- `svc` – Service nền / worker
- `mob` – Mobile app
- `lib` – Thư viện dùng chung

**VAI TRÒ:** `core`, `client`, `admin`, `auth`, `payment`, `shared`

**TÊN NGẮN:** domain nghiệp vụ (crm, finance, shop…)

**Ví dụ:**
- `app-client-crm`
- `web-admin-crm`
- `api-core-payment`
- `lib-shared-utils`

### 2. Tên File Nhiệm vụ (Mission)

**Công thức:** `MISSION-{YYYYMMDD}-{LOẠI}-{MỤC TIÊU}.md`

- **LOẠI:** `FEAT` (Tính năng), `FIX` (Sửa lỗi), `REFACTOR`.
- **Ví dụ:** `MISSION-20251227-FEAT-login-google.md`

---

## III. CẤU TRÚC HẠ TẦNG (INFRASTRUCTURE)

Cấu trúc thư mục chuẩn cho **MỌI** dự án:

```
[TÊN-DỰ-ÁN-CHUẨN]/
├── .project-context/                  <-- TRUNG TÂM ĐIỀU HÀNH AI
│   ├── PROJECT_PROMPT.md          <-- HIẾN PHÁP (Luật bất biến - Commit Git)
│   ├── ACTIVE_MISSION.md         <-- LỆNH BÀI (Nhiệm vụ đang chạy - .gitignore)
│   └── ARCHIVE/                  <-- LỊCH SỬ (Nhiệm vụ đã xong - Commit Git)
│       └── MISSION-*.md
├── src/
├── package.json
└── .gitignore                    <-- Thêm dòng: .project-context/ACTIVE_MISSION.md
```

---

## IV. CÁC FILE MẪU (TEMPLATES)

### 1. File Hiến Pháp: `PROJECT_PROMPT.md`

Viết 1 lần lúc tạo dự án.

```markdown
# SYSTEM CONTEXT: [LOẠI]-[VAI TRÒ]-[TÊN NGẮN]

## 1. IDENTITY (ĐỊNH DANH)
- **Mục tiêu:** [Mô tả ngắn gọn mục đích của dự án này]
- **Tech Stack:** [Liệt kê ngôn ngữ, framework, DB]
- **Owner:** [Tên bạn]

## 2. BOUNDARIES (BIÊN GIỚI - RẤT QUAN TRỌNG)
- **Phạm vi:** Chỉ chứa logic của [VAI TRÒ].
- **Cấm:** Không được import từ bên ngoài thư mục dự án này.
- **Dependency:** Chỉ dùng các thư viện đã khai báo trong `package.json`.

## 3. RULES OF ENGAGEMENT (LUẬT TƯƠNG TÁC)
- **Stop & Ask:** Nếu Mission không rõ ràng hoặc thiếu file -> DỪNG VÀ HỎI. Không tự suy diễn.
- **Scope Containment:** Chỉ được sửa các file liệt kê trong Mission.
- **Evidence First:** Luôn chạy test và chụp màn hình (Artifact) trước khi báo cáo xong.

## 4. DEFINITION OF DONE
- [ ] Build thành công.
- [ ] Không lỗi Lint.
- [ ] Test case liên quan Pass.
```

### 2. File Lệnh Bài: `ACTIVE_MISSION.md`

Tạo mới hàng ngày cho mỗi task.

```markdown
# MISSION: [LOẠI] - [MỤC TIÊU NGẮN]

## 1. CONTEXT
Vấn đề hiện tại là gì? Tại sao cần làm?

## 2. SCOPE (PHẠM VI CHO PHÉP)
**Files được phép sửa:**
- `src/path/to/file1.ts`
- `src/path/to/file2.ts`

**Files CẤM đụng vào:**
- `src/core/config.ts`

## 3. TASKS (CÁC BƯỚC)
- [ ] Bước 1: ...
- [ ] Bước 2: ...

## 4. ACCEPTANCE (NGHIỆM THU)
- [ ] Unit Test hàm mới pass.
- [ ] Artifact: Ảnh chụp terminal kết quả test.
```

---

## V. QUY TRÌNH VẬN HÀNH (WORKFLOW SOP)

### BƯỚC 1: KHỞI TẠO & THAM MƯU (Brain Phase)

**Công cụ:** VS Code (Claude Code) hoặc Claude Web.

**Hành động:**
1. Mở đúng folder dự án.
2. **Prompt:** "Đọc `PROJECT_PROMPT.md`. Tôi cần làm [X]. Hãy phân tích và tạo file `.project-context/ACTIVE_MISSION.md`. Chỉ viết plan, scope, acceptance criteria. KHÔNG viết code."
3. Review file Mission, nếu ổn thì lưu lại.

### BƯỚC 2: THI CÔNG & GIÁM SÁT (Hand Phase)

**Công cụ:** Google Antigravity.

**Hành động:**
1. Mở đúng folder dự án.
2. **Prompt:** "Thực thi nhiệm vụ trong `.project-context/ACTIVE_MISSION.md`. Tuân thủ Scope. Chạy test và tạo Artifact."
3. Chờ Agent làm việc. Nếu lỗi, comment trực tiếp để Agent sửa.

### BƯỚC 3: ĐÓNG GÓI & LƯU TRỮ (Closing Phase)

**Công cụ:** Terminal / Git.

**Hành động:**
1. Kiểm tra Artifact (ảnh/log).
2. Đổi tên `ACTIVE_MISSION.md` -> `.project-context/ARCHIVE/MISSION-{Date}-{Name}.md`.
3. Thêm dòng `# STATUS: DONE` vào đầu file vừa đổi tên.
4. `git add .` -> `git commit -m "feat: complete mission {name}"` -> `git push`.

---

## VI. CHECKLIST TRIỂN KHAI NGAY

Để biến lý thuyết thành hiện thực, hãy làm ngay các bước sau cho 1 dự án cũ của bạn:

- [ ] Đổi tên 1 thư mục dự án theo chuẩn `[LOẠI]-[VAI TRÒ]-[TÊN]`.
- [ ] Vào từng thư mục, chạy lệnh: `mkdir -p .project-context/ARCHIVE`.
- [ ] Tạo và điền nội dung cho `PROJECT_PROMPT.md` (Copy mẫu ở trên).
- [ ] Thêm `.project-context/ACTIVE_MISSION.md` vào `.gitignore`.
- [ ] Commit đầu tiên: `git commit -m "chore: init PROJECT SOP v1.0"`.

---

**© 2025 | Isolated Intelligence Protocol v1.0 | Final Frozen**

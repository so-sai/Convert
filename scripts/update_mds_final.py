import os
import sys
import logging
from pathlib import Path

# --- CONFIGURATION ---
# Đảm bảo Encoding cho Terminal Windows
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ARCH_PRIME")

# --- CONTENT: MDS v3.14 (SSOT) ---
MDS_CONTENT = r'''# 📘 MDS v3.14 - THE IRON VAULT (CONVERGED EDITION)

> **Status:** SPRINT 5 (EXECUTION PHASE)
> **Engine:** Hybrid (Python 3.14 `cp314t` + Rust Tauri v2)
> **Last Updated:** 2025-11-30
> **Ref:** [Engineering Playbook](../05_OPERATIONS/ENGINEERING_PLAYBOOK.md)

## 1. VISION & PHILOSOPHY
* **Mission:** "Offline-first, event-sourced, cryptographically unbreakable knowledge system."
* **Metaphor:** "The Iron Vault" - Vỏ thép (Rust) bảo vệ Lõi vĩnh cửu (Python/SQLite).
* **Core Values:**
  1. **Local Sovereignty:** Dữ liệu không bao giờ rời khỏi máy.
  2. **Zero-Trust Architecture:** Frontend bị coi là "mù" (Blind), Backend Python không chạm vào Secret.
  3. **Resilience:** Crash-proof, Atomic Writes, Quarantine Bad Data.

## 2. ARCHITECTURAL DECISIONS (ADR)
* **[ADR-001] Hybrid Core:**
  * **Logic & Storage:** Python (Linh hoạt, thư viện phong phú).
  * **High-Security:** Rust (Quản lý bộ nhớ an toàn, Zeroize, Crypto).
  * **UI:** Svelte 5 (Nhẹ, Reactive).
* **[ADR-002] Crypto Standard (Omega):**
  * *Storage:* XChaCha20-Poly1305 (Libsodium).
  * *Key Derivation:* Argon2id (128MB RAM, 3 Ops - Hardened).
* **[SPEC-007] Secure Recovery:**
  * Rust sinh BIP39 -> Render QR/SVG trong RAM -> Base64 -> Frontend.
  * **Tuyệt đối không** gửi chuỗi text 12 từ khóa ra Frontend.

## 3. PHYSICAL DIRECTORY STRUCTURE (CONFIRMED)
```text
E:/DEV/app-desktop-Convert/
├── .github/                    # CI/CD Workflows
├── assets/                     # 🎨 RESOURCES (Restored)
│   ├── icons/                  # App icons (.ico, .png)
│   └── fonts/                  # Offline fonts
├── docs/                       # 🧠 KNOWLEDGE BASE
│   ├── 01_ARCHITECTURE/        # MDS_v3.14.md (SSOT)
│   ├── 02_PLANS/               # Roadmaps
│   ├── 03_SPECS/               # Technical Specs
│   └── 05_OPERATIONS/          # Engineering Playbook
├── scripts/                    # 🛠️ DEVOPS TOOLS
│   ├── clean_ghosts.py         # Dọn dẹp file rác
│   ├── deploy_rust.py          # Script deploy Rust modules
│   └── update_mds_final.py     # 🔄 MDS Updater (This Script)
├── src/
│   └── core/                   # 🐍 PYTHON BACKEND CORE
│       ├── api/                # Tauri Bridge (Routes)
│       ├── security/           # KMS Interface
│       ├── storage/            # SQLite Adapter
│       └── utils/              # Logger, Paths
├── src-tauri/                  # 🦀 RUST SECURITY CORE
│   ├── src/
│   │   ├── commands/           # Modules: recovery_export.rs
│   │   └── lib.rs              # Command Registration
│   ├── Cargo.toml              # Dependencies
│   └── tauri.conf.json         # Security Config
├── src-ui/                     # 🖼️ FRONTEND (Svelte 5)
├── tests/                      # 🧪 QA SUITE
├── .gitignore                  # Git Rule
├── pytest.ini                  # Test Config
└── requirements.txt            # Python Dependencies
```

## 4. ROADMAP (LỘ TRÌNH HỢP NHẤT)

### 🟢 SPRINT 5: RESILIENCE & RECOVERY (Hiện tại)
* ✅ **Task 5.1:** Recovery Phrase (Rust Iron Vault) - DONE.
* ✅ **Task 5.2:** Secure Backup (Python Atomic Vacuum) - DONE.
* ⏳ **Task 5.3:** Frontend Integration (Blind UI for Recovery).
* 📋 **Task 5.4:** Key Rotation (Wrapper Protocol).

### 🟡 SPRINT 6: COGNITION & PIPELINE (Tương lai)
* **Task 6.1:** Streaming Pipeline.
* **Task 6.2:** Encrypted Full-Text Search (FTS5).
* **Task 6.3:** AI Model Integration.

## 5. THE IRON RULES (QUY TẮC BẤT BIẾN)
1. **Zeroize or Die:** Mọi biến chứa Secret trong Rust phải `impl Zeroize` và `Drop`.
2. **No-Cat Protocol:** Không dùng `cat` để ghi file code. Dùng Python Script.
3. **Monorepo Law:** Code nghiệp vụ Python -> `src/core`. Code bảo mật -> `src-tauri`.
4. **Test First:** Không viết code nếu chưa có Test Plan.
5. **Clean Room:** Dọn dẹp file rác trước khi bắt đầu module mới.
'''

def safe_update_mds():
    """
    Hàm cập nhật MDS an toàn, tuân thủ [The Constitution].
    """
    # Định nghĩa đường dẫn tương đối từ vị trí chạy script
    # Giả định script chạy từ root project hoặc folder scripts
    current_path = Path.cwd()
    
    # Tìm root (nếu đang ở trong scripts thì lùi ra 1 cấp)
    if current_path.name == "scripts":
        project_root = current_path.parent
    else:
        project_root = current_path
        
    target_path = project_root / "docs" / "01_ARCHITECTURE" / "MDS_v3.14.md"
    
    try:
        logger.info(f"📍 Project Root detected: {project_root}")
        
        # 1. Đảm bảo thư mục tồn tại
        target_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Verified directory: {target_path.parent}")

        # 2. Ghi file an toàn
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(MDS_CONTENT)
        
        logger.info(f"✅ SUCCESS: MDS updated at {target_path}")
        logger.info("   Status: Sprint 5 Execution Phase")
        logger.info("   System: Hybrid Core (Python + Rust) Lock-in")

    except Exception as e:
        logger.error(f"❌ FAILED to update MDS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    safe_update_mds()

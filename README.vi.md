# Living Codebase Map (LCM)

> **Độ chính xác phẫu thuật, Quản trị ràng buộc ngầm & Bộ nhớ làm việc nguyên tử cho AI Coding Agents.**  
> *Chấm dứt tình trạng AI bị ảo tưởng số dòng, cắt đứt liên kết UI-to-DB và lặp lại các sai lầm ngầm trong quá khứ.*

[English](README.md) | **[Tiếng Việt](README.vi.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![Compatible with](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20Windsurf%20%7C%20Copilot-orange.svg)]()

---

## ✨ 5 Lợi Ích Vượt Trội Cho Lập Trình Viên & AI

| Lợi ích | Giá trị thực tế mang lại |
|---|---|
| 🎯 **Chấm dứt sửa bậy, phá vỡ hệ thống** | AI biết trước chuỗi ảnh hưởng 6 tầng (DOM ➔ JS ➔ API ➔ DB) trong **0.05 giây** trước khi gõ bất kỳ dòng code nào. Không còn tình trạng "chữa chỗ này hỏng chỗ kia". |
| 💸 **Tiết kiệm đến 70% chi phí Token** | AI đọc Mini Map (`PROJECT_MAP.min.md`) siêu nhẹ chỉ 300 token thay vì phải nạp hàng chục nghìn dòng mã nguồn ở mỗi câu hỏi. |
| 🧠 **Bộ nhớ vĩnh cửu - Không bao giờ quên lỗi cũ** | Tự động ghi nhớ các "ràng buộc ngầm" và bài học xương máu (Module 4). Kể cả khi chat bị nén (compaction) hay sang ngày hôm sau, AI vẫn nhớ như in. |
| 💬 **Tương tác trực tiếp trong chat (Zero-Terminal)** | Không cần mở terminal, không cần chạy lệnh python. Chỉ cần gõ `map update`, `map impact`... ngay trong ô chat của Claude, Cursor, Antigravity. |
| 🛡️ **Bảo vệ tự động (Zero-Drift & Git Guard)** | Bản đồ luôn version-control cùng code. Tích hợp sẵn Pre-commit hook & GitHub Actions chặn nguy cơ lệch dòng trước khi tạo PR. |

---

### ⚖️ So Sánh Trước & Sau Khi Sử Dụng

| Tiêu chí | Khi chưa có Living Codebase Map | Khi dùng Living Codebase Map |
|---|---|---|
| **Độ chính xác vị trí** | AI đoán mò số dòng, thường xuyên xóa nhầm code | Nhắm trúng 100% tọa độ `file:line` thực tế |
| **Bẫy nghiệp vụ ngầm** | AI liên tục lặp lại các lỗi cũ đã từng sửa | Ghi nhớ vĩnh viễn trong Module 4, cảnh báo ngay |
| **Tác động đa tầng** | Đổi ID nút bấm UI làm chết API và database ngầm | Báo cáo đầy đủ chuỗi ảnh hưởng trong 0.05s |
| **Thao tác người dùng** | Phải tự nhớ file python, mở terminal gõ lệnh | Tự động hoàn toàn qua ô chat |

---

## 💬 Giao Diện Chat Dùng Ngay (Không Cần Terminal)

Bạn **không cần mở terminal** hay tìm file python. Chỉ cần gõ lệnh trực tiếp trong ô chat IDE, Agent sẽ tự chạy ngầm và báo cáo kết quả:

| Bạn gõ trong ô Chat | Agent tự động thực hiện |
|---|---|
| `map update` hoặc `cập nhật map` | Tự chạy `living_map.py update --auto-commit`, refresh toàn bộ chỉ số dòng, sinh `PROJECT_MAP.min.md`, và báo cáo tóm tắt 3 dòng. |
| `map impact <tên_hàm>` hoặc `ảnh hưởng của <tên>` | Phân tích **Blast Radius 6 tầng** (Code, UI DOM, API, DB, Ràng buộc ngầm, Features) trong 0.05 giây. |
| `map check` hoặc `kiểm tra map` | Kiểm tra Smart Drift MD5 trong 0.02s xem số dòng trong bản đồ có bị lệch so với code thực tế không. |
| `map constraint <nội dung>` hoặc `thêm ràng buộc: <nội dung>` | Ghi nhận ngay bẫy kỹ thuật mới vào Module 4, tự động cấp mã `[C...]` và cập nhật mini map. |
| `map rollback [hash]` | Tra cứu lịch sử commit của map hoặc hoàn nguyên về phiên bản trước. |
| `map init` | Tự động quét cấu trúc dự án và khởi tạo file `PROJECT_MAP.md`. |

---

## 🚀 Hướng Dẫn 5 Phút Khởi Động Nhanh

### Bước 1: Cài đặt vào dự án
Clone thư mục skill vào dự án (ví dụ đặt tại `.agents/skills/` hoặc `tools/`):

```bash
git clone https://github.com/lekhachung1993-hub/living-codebase-map.git .agents/skills/living-codebase-map
```

### Bước 2: Khởi tạo `PROJECT_MAP.md`
Chạy lệnh init tại thư mục gốc của dự án:

```bash
python .agents/skills/living-codebase-map/scripts/living_map.py init
```
*Script sẽ tự phát hiện công nghệ (Go / Python / Node / Rust / C#), nạp các module mẫu và tạo file `PROJECT_MAP.md`.*

### Bước 3: Quét & Đánh chỉ mục vị trí hàm
Chạy quét để cập nhật chính xác số dòng thực tế:

```bash
python .agents/skills/living-codebase-map/scripts/living_map.py update
```

### Bước 4: Hướng dẫn AI Agent của bạn
Thêm đoạn chỉ thị sau vào file cấu hình agent (`.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`, hoặc `AGENTS.md`):

```markdown
<!-- living-codebase-map:start -->
# Giao Thức Living Codebase Map & Lệnh Chat
Trước khi sửa BẤT KỲ dòng code nào:
1. Đọc `PROJECT_MAP.min.md` (hoặc `PROJECT_MAP.md`) để nắm kiến trúc, DOM bindings và các ràng buộc ngầm.
2. Tra cứu Module 4 (Implicit Constraints) để tránh dẫm lại các bẫy kỹ thuật cũ.
3. Xác định đúng tọa độ `file:line` tại Module 1 & 2.

### Lệnh Điều Khiển Trong Chat (Không bắt người dùng chạy script python):
Khi người dùng gõ các từ khóa sau trong ô chat, hãy tự động thực thi:
- `map update` / `cập nhật map`: Chạy `python scripts/living_map.py update --auto-commit` và tóm tắt kết quả.
- `map impact <tên>` / `ảnh hưởng của <tên>`: Chạy `python scripts/living_map.py impact <tên>` và trả về bảng blast radius.
- `map check` / `kiểm tra map`: Chạy `python scripts/living_map.py check` xác minh độ lệch dòng.
- `map constraint <nội dung>`: Tự động nạp constraint mới vào Module 4.
- `map rollback [commit]`: Xem lịch sử hoặc rollback bản đồ.
<!-- living-codebase-map:end -->
```

---

<details>
<summary><h3>🛠️ Chi Tiết Các Lệnh CLI Chạy Bằng Terminal (Click để xem nếu muốn chạy tay)</h3></summary>

### 1. Làm mới số dòng & sinh Mini Map
```bash
python scripts/living_map.py update
```

### 2. Cập nhật và tự động Git Commit Map
```bash
python scripts/living_map.py update --auto-commit
```

### 3. Phân tích ảnh hưởng đa tầng (Blast Radius Analysis)
```bash
python scripts/living_map.py impact <tên_hàm_hoặc_từ_khóa>
```

### 4. Ghi nhận ràng buộc ngầm mới phát hiện
```bash
python scripts/living_map.py add-constraint "Mô tả bẫy nghiệp vụ vừa tìm thấy"
```

### 5. Đăng ký tính năng mới hoàn thành
```bash
python scripts/living_map.py add-feature --id F080 --desc "Xuất Excel" --ui "#btn" --api "GET /api"
```

### 6. Kiểm tra lệch dòng CI/CD (Chặn PR nếu Map bị lệch)
```bash
python scripts/living_map.py check
python scripts/living_map.py check --fix
```

### 7. Cài đặt Git Pre-Commit Hook tự động
```bash
python scripts/living_map.py install-hook --hook pre-commit
```

### 8. Xem lịch sử và hoàn nguyên bản đồ
```bash
python scripts/living_map.py rollback
python scripts/living_map.py rollback --to <COMMIT_HASH>
```
</details>

<details>
<summary><h3>🧩 Ngôn Ngữ & Framework Hỗ Trợ Tự Động (Click để xem chi tiết)</h3></summary>

| Ngôn ngữ | Framework / Kiến trúc hỗ trợ | Ký hiệu trích xuất tự động |
|---|---|---|
| **Go** | net/http, Gin, Fiber, Echo, Chi | Hàm, receiver method, struct, interface |
| **Python** | FastAPI, Django, Flask, PyTorch | `def`, `async def`, `class`, route decorators (`@app.get`, `@router.post`) |
| **TypeScript / JS** | Next.js (App & Pages Router), React, Vue | Route handlers (`GET`, `POST`), Server Actions, `function`, arrow funcs |
| **Node.js Backend** | Express, NestJS, Fastify | `app.get()`, `router.post()`, `@Controller()`, `@Injectable()` |
| **Rust** | Actix-web, Axum, Rocket | `fn`, `async fn`, `pub fn`, `struct`, `impl`, route macros |
| **C# / .NET** | ASP.NET Core MVC & Web API | Controller, action, method, `[HttpGet]`, `[HttpPost]` |
| **Java** | Spring Boot, Jakarta EE | Controller, service, `@GetMapping`, `@PostMapping` |
| **PHP** | Laravel, Symfony | Routes (`Route::get`), classes, methods |
| **HTML / DOM** | HTML5, Vue Templates, JSX | Element ID (`id="..."`), class bindings |

</details>

<details>
<summary><h3>📁 Cấu Trúc Thư Mục Repository</h3></summary>

```
living-codebase-map/
├── .github/workflows/map-lint.yml    # CI/CD GitHub Action
├── SKILL.md                          # Định nghĩa Skill chuẩn Agent (hỗ trợ Chat-Native)
├── README.md                         # Tài liệu tiếng Anh
├── README.vi.md                      # Tài liệu tiếng Việt
├── LICENSE                           # Giấy phép MIT
├── scripts/living_map.py             # Bộ xử lý CLI thuần Python (v2.2)
└── templates/
    ├── PROJECT_MAP.template.md       # Bản mẫu Living Map đầy đủ
    └── PROJECT_MAP.min.template.md   # Bản mẫu Mini Map tiết kiệm token
```

</details>

---

## 📄 Giấy Phép
Phát hành theo giấy phép **MIT License**. Xem chi tiết tại [LICENSE](LICENSE).

# Living Codebase Map (LCM)

> **Độ chính xác phẫu thuật, Quản trị ràng buộc ngầm & Bộ nhớ làm việc nguyên tử cho AI Coding Agents.**  
> *Chấm dứt tình trạng AI bị ảo tưởng số dòng, cắt đứt liên kết UI-to-DB và lặp lại các sai lầm ngầm trong quá khứ.*

[English](README.md) | **[Tiếng Việt](README.vi.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![Compatible with](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20Windsurf%20%7C%20Copilot-orange.svg)]()

---

## 💥 Vấn Đề Thực Tế: Nghịch Lý "Bác Sĩ Mổ Mù"

Các mô hình AI lập trình hiện đại (Claude 3.7 / 4.6, GPT-4o / o3, Gemini 2.5 / 3.0) rất giỏi viết hàm đơn lẻ. Nhưng trong một dự án thực tế đang vận hành, chúng thường mắc kẹt trong **Nghịch lý Bác sĩ mổ mù**:

1. **Ảo tưởng số dòng (Line Hallucination):** Mã nguồn liên tục thay đổi. Agent nhớ vị trí hàm từ các prompt cũ, nhảy vào sửa nhầm dòng và xóa đè code lân cận.
2. **Cắt đứt liên kết đa tầng (Cross-Layer Breakage):** Đổi một `#id` trong HTML làm chết event listener trong JS, làm sai format JSON gửi lên backend API, dẫn đến lỗi database.
3. **Mất trí nhớ về "Ràng buộc ngầm" (Implicit Constraints):** Hệ thống có những quy tắc mà **không có bộ phân tích tĩnh nào tự suy ra được** — ví dụ:
   - *"Không đọc state JS mà phải đọc trực tiếp DOM select vì thao tác chạm mobile không trigger blur."*
   - *"Snapshot hầm đá là bất đồng bộ lúc 0h; không được query đọc ngay sau khi ghi."*
   - *"Bottom bar trên mobile cần padding-bottom 125px để không che khuất nút điều hướng."*
4. **Mất trí nhớ sau nén ngữ cảnh (Context Compaction Amnesia):** Khi đoạn chat quá dài bị tóm tắt/nén lại, Agent quên sạch bối cảnh kiến trúc và lặp lại đúng lỗi đã từng sửa.

---

## 💡 Giải Pháp: Living Codebase Map

**Living Codebase Map (LCM)** trang bị cho AI Agent một chiếc la bàn kiến trúc sống (`PROJECT_MAP.md`) được đồng bộ liên tục bởi công cụ CLI thuần chuẩn (`living_map.py`), hoàn toàn không phụ thuộc thư viện ngoài.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PROJECT_MAP.md                                  │
│                                                                             │
│  MODULE 0: Meta (Stack, Entrypoint, DB, Trạng thái Test)                    │
│  MODULE 1: Chỉ mục vị trí Backend (file:line → hàm/struct)                  │
│  MODULE 2: Chỉ mục vị trí Frontend (file:line → function)                   │
│  MODULE 3: Bản đồ phần tử DOM UI (#id → click → func() → /api)              │
│  MODULE 4: Ràng buộc ngầm (Bài học xương máu: [C1]..[Cn])                   │
│  MODULE 5: Đối soát tính năng đa tầng (UI ➔ JS ➔ API ➔ DB ➔ Constraints)    │
│  MODULE 6: Tiêu chuẩn chất lượng & Kiểm thử                                 │
│  MODULE 7: Mini Map tiết kiệm token (PROJECT_MAP.min.md)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                               ▲               ▲
                   Đọc trước   │               │ Tự đồng bộ &
                   khi sửa code│               │ Commit nguyên tử
                               │               │
┌──────────────────────────────┴───────────────┴──────────────────────────────┐
│                            AI CODING AGENT                                  │
│             (Claude Code / Cursor / Gemini Antigravity / Windsurf)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💬 Giao Diện Chat-Native (Tương Tác Không Cần Mở Terminal)

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

## 🛠️ Danh Mục Lệnh CLI Đầy Đủ

### 1. Làm mới số dòng & sinh Mini Map (Chạy sau khi sửa code)
```bash
python scripts/living_map.py update
```
*Quét lại toàn bộ hàm, class, route, cập nhật lại tọa độ `L<num>` và xuất ra `PROJECT_MAP.min.md`.*

### 2. Cập nhật và tự động Git Commit Map
```bash
python scripts/living_map.py update --auto-commit
```

### 3. Phân tích ảnh hưởng đa tầng (Blast Radius Analysis)
Trước khi sửa bất kỳ hàm nào, chạy trong 0.05s để xem trước toàn bộ hệ thống bị ảnh hưởng:
```bash
python scripts/living_map.py impact <tên_hàm_hoặc_từ_khóa>
```
*Tự gom nhóm: Code liên quan, UI DOM `#id`, API endpoint, Bảng Database, Ràng buộc ngầm `[Cx]` và Features liên quan.*

### 4. Ghi nhận ràng buộc ngầm mới phát hiện
```bash
python scripts/living_map.py add-constraint "Mô tả bẫy nghiệp vụ vừa tìm thấy khi debug"
```
*Tự động cấp mã ID tiếp theo (ví dụ `[C9]`) và chèn vào Module 4.*

### 5. Đăng ký tính năng mới hoàn thành
```bash
python scripts/living_map.py add-feature \
  --id F080 \
  --desc "Xuất dữ liệu kho đá ra Excel" \
  --ui "#btn-export-excel" \
  --js "exportExcel() app_cellar.js" \
  --api "GET /api/cellar/export" \
  --db "cellar_exports" \
  --constraints "C2,C4"
```

### 6. Kiểm tra lệch dòng CI/CD (Chặn PR nếu Map bị lệch)
```bash
python scripts/living_map.py check
```
*Trả về exit code `0` nếu khớp 100%, hoặc exit code `2` kèm bảng sai lệch chi tiết. Dùng cờ `--fix` để tự sửa ngay:*
```bash
python scripts/living_map.py check --fix
```

### 7. Cài đặt Git Pre-Commit Hook tự động
```bash
python scripts/living_map.py install-hook --hook pre-commit
```
*Tự động ngăn commit nếu lập trình viên hoặc AI quên cập nhật bản đồ.*

### 8. Tích hợp GitHub Actions CI/CD
Tệp mẫu workflow đã có sẵn tại [.github/workflows/map-lint.yml](.github/workflows/map-lint.yml). Mọi Pull Request sẽ được kiểm tra tự động:
```yaml
name: Living Codebase Map Lint
on: [push, pull_request]
jobs:
  lint-living-map:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.x' }
      - run: python scripts/living_map.py check
```

### 9. Xem lịch sử và hoàn nguyên bản đồ
```bash
python scripts/living_map.py rollback
python scripts/living_map.py rollback --to <COMMIT_HASH>
```

---

## 🧩 Danh Sách Ngôn Ngữ & Framework Được Hỗ Trợ

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

---

## 📁 Cấu Trúc Thư Mục Repository

```
living-codebase-map/
├── .github/
│   └── workflows/
│       └── map-lint.yml              # CI/CD GitHub Action cho pull requests
├── SKILL.md                          # Định nghĩa Skill chuẩn Agent (hỗ trợ Chat-Native)
├── README.md                         # Tài liệu tiếng Anh
├── README.vi.md                      # Tài liệu tiếng Việt
├── LICENSE                           # Giấy phép MIT
├── .gitignore                        # Cấu hình git ignore chuẩn
├── scripts/
│   └── living_map.py                 # Bộ xử lý CLI thuần Python (v2.2)
└── templates/
    ├── PROJECT_MAP.template.md       # Bản mẫu Living Map đầy đủ
    └── PROJECT_MAP.min.template.md   # Bản mẫu Mini Map tiết kiệm token
```

---

## 📄 Giấy Phép
Phát hành theo giấy phép **MIT License**. Xem chi tiết tại [LICENSE](LICENSE).

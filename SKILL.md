---
name: living-codebase-map
description: >
  Living Codebase Map & Surgical Precision Workflow for AI Coding Agents.
  Maintains PROJECT_MAP.md as living working memory: tracks symbol locations (file:line),
  DOM-to-DB cross-layer mappings, implicit constraints, and enforces risk-gated triage
  with automated git-backed synchronization.
triggers:
  - map
  - lcm
  - map update
  - map check
  - map impact
  - map constraint
  - map rollback
  - quét map
  - cập nhật map
  - kiểm tra map
  - ảnh hưởng của
  - thêm ràng buộc
  - session start
  - before modifying any code
  - implementing new feature
---

# Living Codebase Map: Surgical Precision for AI Agents

> **Philosophy:** AI coding models fail in production codebases not from lack of intelligence, but from **blind surgery** — missing implicit business constraints, hallucinating outdated line numbers, and severing unseen cross-layer connections between UI DOM, API contracts, and database states.
>
> **The Solution:** A living, version-controlled architecture compass (`PROJECT_MAP.md`) paired with a zero-dependency CLI engine (`living_map.py`) that synchronizes symbol locations, enforces atomic git commits, and anchors agent memory across chat compactions.

---

## 💬 CHAT-NATIVE INTERFACE (TƯƠNG TÁC TRỰC TIẾP TRONG Ô CHAT)

Người dùng **KHÔNG CẦN mở terminal hay tìm file python**. Người dùng chỉ cần gõ lệnh trực tiếp trong ô chat, Agent sẽ tự động chạy script ngầm và hiển thị kết quả:

| Lệnh trong ô chat | Hành động tự động của Agent |
|---|---|
| `map update` hoặc `cập nhật map` | Agent tự chạy `living_map.py update --auto-commit`, refresh line numbers, sinh `PROJECT_MAP.min.md` và báo cáo tóm tắt. |
| `map impact <tên>` hoặc `ảnh hưởng của <tên>` | Agent tự chạy `living_map.py impact <tên>`, phân tích blast radius 6 tầng (Code, UI, API, DB, Constraints, Features) và hiển thị ngay. |
| `map check` hoặc `kiểm tra map` | Agent chạy Smart Drift Check (MD5) trong 0.02s và thông báo trạng thái đồng bộ (hoặc tự sửa nếu có `--fix`). |
| `map constraint <nội dung>` hoặc `thêm ràng buộc: <nội dung>` | Agent tự nạp ràng buộc ngầm vào Module 4, cập nhật ID `[Cx]` và sync lại mini map. |
| `map rollback [hash]` | Agent tra cứu lịch sử commit của map và khôi phục về phiên bản mong muốn. |
| `map init` | Agent tự động phát hiện stack công nghệ và khởi tạo `PROJECT_MAP.md` cho dự án mới. |

---

## CORE PROTOCOL: 5-STEP SURGICAL LIFECYCLE


```
  [User Request]
        │
        ▼
┌──────────────────┐
│ STEP 0: WARMUP   │ ──► Read PROJECT_MAP.md before touching any code
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ STEP 1: TRIAGE   │ ──► Classify: GREEN (Low), YELLOW (Medium), RED (Critical)
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ STEP 2: TRACE    │ ──► Map blast radius: UI DOM ➔ JS ➔ API ➔ DB ➔ Constraints
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ STEP 3: SURGERY  │ ──► Karpathy surgical edit at exact file:line target
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ STEP 4: SYNC     │ ──► Run tests & execute `living_map.py update`
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ STEP 5: ATOMIC   │ ──► Git commit code and PROJECT_MAP.md together
└──────────────────┘
```

---

## STEP 0: SESSION WARMUP (TOKEN-SAVING PROTOCOL)

**Mandatory first action of every coding session:**

1. **Read `PROJECT_MAP.min.md` first:**
   - If `PROJECT_MAP.min.md` exists, read it instead of the full map (~300-500 tokens, saving ~70% context).
   - If only `PROJECT_MAP.md` exists, read `PROJECT_MAP.md`.
2. Extract working memory:
   - **Recent Commit & Feature Status** (Header & Module 8)
   - **Implicit Constraints** (Module 4) — *rules that cannot be inferred from code alone*
   - **Feature Cross-Reference** (Module 5) — find related DOM IDs and APIs
3. If `PROJECT_MAP.md` is missing, initialize it immediately:
   ```bash
   python scripts/living_map.py init
   ```
4. Output a brief 3-line session briefing:
   ```markdown
   **LIVING MAP CONTEXT:**
   - Active Commit: [hash] | Last Feature: [name]
   - Key Constraints: [list relevant C-IDs e.g. C1, C4]
   - Target Components: [DOM IDs / Functions involved]
   ```

---

## STEP 1: RISK TRIAGE

Classify every incoming user request into one of three risk categories:

| Level | Blast Radius Criteria | Agent Action |
|---|---|---|
| 🟢 **GREEN (Low)** | CSS, styling, copy, labels, icons. No state changes, no API edits, no DOM ID changes. | Proceed directly. Verify visually. |
| 🟡 **YELLOW (Medium)** | Modifies single function logic, adds API parameter, introduces new UI button or form field. | Trace cross-layer callers. Run targeted unit/integration tests. |
| 🔴 **RED (Critical)** | Touches DB schema, core auth, data mutations, background workers, or payment/ledger logic. | **STOP & WARN:** Present impact analysis to user. Require test pass before commit. |

---

## STEP 2: CROSS-LAYER IMPACT TRACING (FAST CLI)

Before modifying any symbol, query its blast radius in 0.05 seconds via CLI:

```bash
python scripts/living_map.py impact <symbol_or_keyword>
```

This instantly traces the full dependency chain:
```
[UI Trigger: #dom-id] ➔ [Event Handler: func()] ➔ [API Endpoint: /api/...] ➔ [DB Table/Query]
                                  │
                                  ▼
                  [Implicit Constraint Check: C1..Cn]
```

1. **Check UI bindings:** Does changing this element break event listeners attached to `#id` or `.class`?
2. **Check API contracts:** Does the payload match what the backend handler unpacks?
3. **Check Database invariants:** Does this mutate a table with active foreign keys or daily snapshots?
4. **Check Module 4 Constraints:**
   - E.g. *“Mobile viewport requires fixed bottom offset”*
   - E.g. *“Snapshots are asynchronous — do not expect immediate read-after-write”*

---

## STEP 3: KARPATHY SURGICAL SURGERY

1. **Locate exact line:** Use Module 1 & 2 in `PROJECT_MAP.md` (or `living_map.py impact`) to jump directly to `file:line`.
2. **Minimal diff:** Do not reformat adjacent functions. Only edit the exact block required.
3. **Preserve comments & type signatures:** Maintain backwards compatibility.
4. **If a new hidden constraint is uncovered during development:**
   Record it immediately via CLI:
   ```bash
   python scripts/living_map.py add-constraint "New implicit rule or edge case discovered"
   ```

---

## STEP 4: VERIFY & AUTO-SYNC MAP

Once changes are in place and local tests pass:

1. **Refresh symbol line numbers & generate compact map:**
   ```bash
   python scripts/living_map.py update
   ```
2. **Inject new feature (if completing a discrete feature):**
   ```bash
   python scripts/living_map.py add-feature \
     --id F079 \
     --desc "Description of new capability" \
     --ui "#dom-id" \
     --js "functionName() file.js" \
     --api "POST /api/endpoint" \
     --db "table_name" \
     --constraints "C1,C3"
   ```
3. **Smart Drift Check:**
   ```bash
   python scripts/living_map.py check
   ```

---

## STEP 5: ATOMIC GIT CHECKPOINT (CODE & MAP IN LOCKSTEP)

**The Golden Rule:** Code, `PROJECT_MAP.md`, and `PROJECT_MAP.min.md` must **ALWAYS** be committed together.

- **Option A (Automated via CLI):**
  ```bash
  python scripts/living_map.py update --auto-commit
  ```
- **Option B (Standard Git):**
  ```bash
  git add -A
  git commit -m "feat(module): implement feature X (F079) + sync living map"
  ```

---

## KỊCH BẢN XỬ LÝ SỰ CỐ (TROUBLESHOOTING RECIPES)

### Recipe 1: Khi Test bị FAIL (Test Failure Self-Healing)
1. Đọc Terminal Log để xác định chính xác `file:line` phát sinh lỗi.
2. Chạy `python scripts/living_map.py impact <failed_function>` để tra cứu xem dòng đó có dính dáng tới Constraint `[Cx]` nào không.
3. Nếu lỗi do lệch kiểu dữ liệu (Type Mismatch) giữa Frontend và Backend, **tuyệt đối không ép kiểu (type casting) bừa bãi**. Phải sửa đồng bộ cả file gửi (payload) và file nhận (handler).
4. Chạy lại bài test độc lập cho đến khi PASS 100%.

### Recipe 2: Khi Git Hook chặn Commit do lệch dòng (Drift Blocked)
1. Terminal sẽ báo: `[BLOCKED] Git pre-commit aborted: PROJECT_MAP.md is out of sync`.
2. Chạy ngay lệnh tự sửa:
   ```bash
   python scripts/living_map.py check --fix
   ```
3. Stage lại file và commit bình thường:
   ```bash
   git add PROJECT_MAP.md PROJECT_MAP.min.md
   git commit -m "docs: sync living map"
   ```

### Recipe 3: Khi phát hiện ràng buộc ngầm mới khi debug (Constraint Discovery)
1. Ngay khi debug ra một nguyên nhân "quái gở" (ví dụ: *Mobile DOM ưu tiên hơn state*, *Snapshot không realtime*):
2. Nạp ngay vào Module 4 bằng 1 lệnh CLI:
   ```bash
   python scripts/living_map.py add-constraint "Mô tả bẫy nghiệp vụ vừa phát hiện"
   ```
3. Map sẽ tự động cập nhật ID `[C(n+1)]` và sinh lại `PROJECT_MAP.min.md`.

### Recipe 4: Khi chuẩn bị sửa hàm nhạy cảm (Blast Radius Check)
1. Trước khi sửa hàm, chạy:
   ```bash
   python scripts/living_map.py impact <tên_hàm>
   ```
2. Nếu terminal báo `CAUTION: High cross-layer blast radius` $\to$ Cảnh báo user và liệt kê danh sách DOM ID / API bị ảnh hưởng trước khi gõ code.

---

## UNIVERSAL CLI REFERENCE

| Task | Command |
|---|---|
| Initialize map for project | `python scripts/living_map.py init` |
| Refresh line numbers & mini map | `python scripts/living_map.py update` |
| Fast blast radius / impact check | `python scripts/living_map.py impact <symbol>` |
| Fast Smart Drift Check (MD5) | `python scripts/living_map.py check` |
| Auto-repair drifted line numbers | `python scripts/living_map.py check --fix` |
| Force full AST scan check | `python scripts/living_map.py check --full` |
| Install Git Pre-Commit Hook | `python scripts/living_map.py install-hook` |
| Update and auto-commit to Git | `python scripts/living_map.py update --auto-commit` |
| Add newly discovered constraint | `python scripts/living_map.py add-constraint "description"` |
| Register completed feature | `python scripts/living_map.py add-feature --id Fxxx --desc "..."` |
| View commit history of map | `python scripts/living_map.py rollback` |
| Rollback map to commit | `python scripts/living_map.py rollback --to <HASH>` |


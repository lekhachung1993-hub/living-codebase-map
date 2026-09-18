# Living Codebase Map (LCM)

> **Surgical Precision, Implicit Constraints & Atomic Working Memory for AI Coding Agents.**  
> *Stop AI agents from hallucinating line numbers, breaking UI-to-DB connections, and repeating past production mistakes.*

**[English](README.md)** | [Tiếng Việt](README.vi.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![Compatible with](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20Windsurf%20%7C%20Copilot-orange.svg)]()

---

## 💥 The Problem: The "Blind Surgeon" Dilemma

Modern LLM coding agents (Claude 3.7 / 4.6, GPT-4o / o3, Gemini 2.5 / 3.0) are brilliant at writing functions in isolation. But in medium-to-large production codebases, they suffer from **The Blind Surgeon Dilemma**:

1. **Stale Coordinates & Line Hallucination:** Codebases evolve constantly. Agents remember symbol locations from earlier prompts, perform edits at outdated lines, and clobber adjacent code.
2. **Severed Cross-Layer Linkages:** Renaming a DOM `#id` in HTML breaks a listener in frontend JS, which alters payload serialization, breaking a backend API endpoint, which corrupts a database column.
3. **Missing "Implicit Constraints":** Production systems are full of rules that **no static code analyzer can deduce** — e.g.:
   - *"Do not query local state; read active DOM select because mobile users touch without blurring."*
   - *"Daily snapshots are asynchronous; never assume immediate read-after-write."*
   - *"Fixed bottom navigation requires dynamic safe-area-inset padding on mobile."*
4. **Context Amnesia Across Chat Compactions:** When long context windows get compacted or truncated, the agent loses architectural awareness and repeats previously solved bugs.

---

## 💡 The Solution: Living Codebase Map

**Living Codebase Map (LCM)** gives your AI agent a structured, live-synchronized architectural compass (`PROJECT_MAP.md`) maintained by a zero-dependency CLI engine (`living_map.py`).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PROJECT_MAP.md                                  │
│                                                                             │
│  MODULE 0: Meta (Stack, Entrypoint, DB, Test Suite Status)                 │
│  MODULE 1: Code Location Index (Backend file:line → symbol)                 │
│  MODULE 2: Code Location Index (Frontend file:line → function)              │
│  MODULE 3: UI & DOM Element Map (#id → click → func() → /api)               │
│  MODULE 4: Implicit Constraints (Rules learned the hard way: C1..Cn)        │
│  MODULE 5: Feature Cross-Reference (UI ➔ JS ➔ API ➔ DB ➔ Constraints)       │
│  MODULE 6: Quality Gate & Test Invariants                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                               ▲               ▲
                   Read Before │               │ Auto-Sync &
                   Any Surgery │               │ Atomic Commit
                               │               │
┌──────────────────────────────┴───────────────┴──────────────────────────────┐
│                            AI CODING AGENT                                  │
│             (Claude Code / Cursor / Gemini Antigravity / Windsurf)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Highlights

- 🚀 **Zero External Dependencies:** Built with pure Python standard library (`re`, `os`, `sys`, `subprocess`, `argparse`). Runs everywhere instantly without `pip install`.
- 🔍 **Multi-Language AST/Regex Scanner:** Out-of-the-box support for **Go, Python, TypeScript, JavaScript, HTML, Rust, and Vue**.
- 🧠 **Memory of Hidden Rules:** Dedicated Module 4 stores hard-learned domain traps so your agent never repeats the same mistake twice.
- 🎯 **Surgical Karpathy Edits:** Eliminates massive whole-file rewrites. The agent targets the exact `file:line` with minimal blast radius.
- 🔄 **Zero-Drift Git Engine:** Atomic commits ensure `PROJECT_MAP.md` is always versioned in lockstep with the codebase. Built-in 1-command rollback.

---

## 🚀 5-Minute Quickstart

### Step 1: Install into your project
Copy the `living-codebase-map` folder into your project (e.g. under `.agents/skills/` or `tools/`):

```bash
git clone https://github.com/your-username/living-codebase-map.git .agents/skills/living-codebase-map
```

### Step 2: Initialize `PROJECT_MAP.md`
Run the initializer at the root of your project:

```bash
python .agents/skills/living-codebase-map/scripts/living_map.py init
```
*This automatically detects your stack (Go / Python / Node), sets up all modules, and creates `PROJECT_MAP.md`.*

### Step 3: Populate & Index Symbols
Scan your entire codebase to populate exact line numbers:

```bash
python .agents/skills/living-codebase-map/scripts/living_map.py update
```

### Step 4: Tell your AI Agent
Add this directive to your project's agent instruction file (e.g. `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`, or `AGENTS.md`):

```markdown
<!-- living-codebase-map:start -->
# Living Codebase Map Protocol & Chat Interface
Before making ANY code changes:
1. Read `PROJECT_MAP.min.md` (or `PROJECT_MAP.md`) to understand architecture, DOM bindings, and implicit constraints.
2. Check Module 4 (Implicit Constraints) to avoid known production traps.
3. Locate exact code targets via Module 1 & 2 (`file:line`).

### Chat Commands (Never make the user run python scripts):
When the user sends these keywords in chat, execute the corresponding action automatically:
- `map update` / `cập nhật map`: Run `python scripts/living_map.py update --auto-commit` and report summary.
- `map impact <symbol>` / `ảnh hưởng của <symbol>`: Run `python scripts/living_map.py impact <symbol>` and display multi-tier blast radius.
- `map check` / `kiểm tra map`: Run `python scripts/living_map.py check` to verify zero drift.
- `map constraint <text>`: Append new implicit rule to Module 4.
- `map rollback [commit]`: View history or rollback map.
<!-- living-codebase-map:end -->
```

---

## 💬 Chat-Native Interface (Zero-Terminal Experience)

You **do not need to open a terminal** or find the Python script. Just type conversational or shortcut commands directly in your IDE chat (Claude, Cursor, Antigravity, Windsurf, Copilot):

| What you type in Chat | What the AI Agent does automatically |
|---|---|
| `map update` or `cập nhật map` | Runs `living_map.py update --auto-commit`, refreshes all line numbers, generates `PROJECT_MAP.min.md`, and shows a 3-bullet summary. |
| `map impact <symbol>` or `ảnh hưởng của <symbol>` | Runs `living_map.py impact <symbol>`, analyzes 6-layer blast radius (Code, UI, API, DB, Constraints, Features) and returns impact breakdown in 0.05s. |
| `map check` or `kiểm tra map` | Runs Smart Drift MD5 Check in 0.02s to verify if symbol lines drifted. |
| `map constraint <text>` or `thêm ràng buộc: <text>` | Registers a hard-learned implicit rule into Module 4 with automatic `[Cx]` ID assignment. |
| `map rollback [hash]` | Checks map git commit history and rolls back to specified checkpoint. |
| `map init` | Scans workspace and bootstraps `PROJECT_MAP.md` tailored to your stack. |

---

## 🛠️ CLI Command Reference

The CLI tool `living_map.py` provides everything needed to keep your map fresh:

### 1. Refresh Line Numbers (Run after editing code)
```bash
python living_map.py update
```
*Scans all functions, classes, routes, and re-indexes every `L<num>` reference in the map.*

### 2. Auto-Commit Map with Git
```bash
python living_map.py update --auto-commit
```
*Updates line numbers and immediately commits `PROJECT_MAP.md` to git.*

### 3. Fast Blast Radius & Impact Analysis
Before modifying any symbol, trace its 6-tier cross-layer impact in 0.05 seconds:
```bash
python living_map.py impact <symbol_or_keyword>
```
*Instantly scans and groups related Code Definitions, UI DOM `#id` Triggers, API Contracts, Database Tables, Applicable Implicit Constraints (`[Cx]`), and Linked Features.*

### 4. Record a Newly Discovered Constraint
When an agent or developer discovers an unexpected edge case or implicit constraint:
```bash
python living_map.py add-constraint "Mobile bottom bar must maintain 64px padding-bottom to avoid obscuring fixed buttons"
```
*Automatically assigns ID (e.g. `[C8]`) and injects it into Module 4.*

### 5. Register a Completed Feature
Add an end-to-end trace from UI to Database:
```bash
python living_map.py add-feature \
  --id F080 \
  --desc "Export cellar ice grid to Excel" \
  --ui "#btn-export-excel" \
  --js "exportExcel() app_cellar.js" \
  --api "GET /api/cellar/export" \
  --db "cellar_exports" \
  --constraints "C2,C4"
```

### 6. CI/CD Drift Linting (Block PR if Map drifts)
Verify that all symbol locations in `PROJECT_MAP.md` match actual code lines:
```bash
python living_map.py check
```
*Returns exit code `0` if in sync, or exit code `2` with a detailed drift diff table if symbols have moved. Add `--fix` to auto-repair:*
```bash
python living_map.py check --fix
```

### 7. Install Git Pre-Commit Hook (Automatic Guard)
Install a pre-commit or pre-push hook directly into `.git/hooks/` with one command:
```bash
python living_map.py install-hook --hook pre-commit
```
*Prevents developers or AI agents from committing changes if `PROJECT_MAP.md` is out of sync.*

### 8. GitHub Actions CI/CD Integration
Copy [.github/workflows/map-lint.yml](.github/workflows/map-lint.yml) to your repository. Every Pull Request will automatically be checked:
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

### 9. View History & Rollback Map
View previous map commits:
```bash
python living_map.py rollback
```
Restore the map to an exact previous commit:
```bash
python living_map.py rollback --to <COMMIT_HASH>
```

---

## 🧩 Supported Languages & Framework Extractors

Living Codebase Map includes modular AST & Regex extractors for modern multi-tier frameworks:

| Language | Frameworks & Architectures Supported | Extracted Symbols |
|---|---|---|
| **Go** | net/http, Gin, Fiber, Echo, Chi | Functions, receiver methods, structs, interfaces |
| **Python** | FastAPI, Django, Flask, PyTorch | `def`, `async def`, `class`, route decorators (`@app.get`, `@router.post`) |
| **TypeScript / JS** | Next.js (App & Pages Router), React, Vue | Next.js route handlers (`GET`, `POST`), Server Actions, `function`, arrow funcs, classes |
| **Node.js Backend** | Express, NestJS, Fastify | `app.get()`, `router.post()`, `@Controller()`, `@Injectable()`, services |
| **Rust** | Actix-web, Axum, Rocket | `fn`, `async fn`, `pub fn`, `struct`, `impl`, route macros |
| **C# / .NET** | ASP.NET Core MVC & Web API | Controllers, actions, methods, `[HttpGet]`, `[HttpPost]` |
| **Java** | Spring Boot, Jakarta EE | Controllers, services, `@GetMapping`, `@PostMapping` |
| **PHP** | Laravel, Symfony | Routes (`Route::get`), classes, methods |
| **HTML / DOM** | HTML5, Vue Templates, JSX | Element IDs (`id="..."`), class bindings |

---

## 📊 Comparison Matrix

| Capability | Standard Agent (Zero Context) | Vector RAG / Embeddings | Living Codebase Map (LCM) |
|---|---|---|---|
| **Surgical Line Target** | ❌ Hallucinates | ⚠️ Approximate chunks | ✅ Exact `file:line` |
| **Implicit Constraints** | ❌ Forgotten | ❌ Only indexes code | ✅ Explicitly preserved (Module 4) |
| **Cross-Layer Traceability** | ❌ Blind | ⚠️ Semantic similarity | ✅ Deterministic (UI ➔ JS ➔ API ➔ DB) |
| **Context Token Cost** | 🔴 Extreme (reads whole files) | 🟡 Medium (chunk retrieval) | 🟢 Tiny (reads 1 single structured map) |
| **Compaction Resilience** | ❌ Amnesia | ⚠️ Lost working state | ✅ Permanent Git-backed memory |
| **Zero Setup / Deps** | ✅ Yes | ❌ Requires vector DB / API keys | ✅ 100% Pure Python Standard Library |

---

## 📁 Repository Structure

```
living-codebase-map/
├── .github/
│   └── workflows/
│       └── map-lint.yml              # CI/CD GitHub Action for pull requests
├── SKILL.md                          # Standard Agent Skill Definition (Chat-Native)
├── README.md                         # Documentation & Quickstart (English)
├── README.vi.md                      # Documentation & Quickstart (Tiếng Việt)
├── LICENSE                           # MIT License
├── .gitignore                        # Standard Python ignores
├── scripts/
│   └── living_map.py                 # Zero-dependency CLI engine (v2.2)
└── templates/
    ├── PROJECT_MAP.template.md       # Universal Living Map template
    └── PROJECT_MAP.min.template.md   # AI Token-Saver mini map template
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or PRs:
- Adding regex / AST support for additional languages (C#, Swift, Java, Kotlin, PHP, Elixir)
- Framework-specific extractors (Django, FastAPI, Next.js, Gin, Express)
- Enhanced git hooks or CI/CD validation actions

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

# Living Codebase Map (LCM)

> **Surgical Precision, Implicit Constraints & Atomic Working Memory for AI Coding Agents.**  
> *Stop AI agents from hallucinating line numbers, breaking UI-to-DB connections, and repeating past production mistakes.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![Compatible with](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20Windsurf%20%7C%20Copilot-orange.svg)]()

---

## ✨ 5 Breakthrough Benefits for Developers & AI

| Benefit | Real-World Impact |
|---|---|
| 🎯 **Zero Broken Code** | AI analyzes 6-tier cross-layer impact (DOM ➔ JS ➔ API ➔ DB) in **0.05 seconds** before touching code. Eliminates collateral bugs and broken contracts. |
| 💸 **Save up to 70% Token Costs** | AI reads the ultra-lean Mini Map (`PROJECT_MAP.min.md`, ~300 tokens) instead of swallowing thousands of source code lines on every turn. |
| 🧠 **Permanent Working Memory** | Preserves implicit business traps and hard-learned constraints (Module 4). Even across context compactions and new sessions, AI never forgets. |
| 💬 **Chat-Native (Zero Terminal)** | No need to open terminals or run Python commands. Type `map update`, `map impact`... directly inside Claude, Cursor, Antigravity, or Copilot chat. |
| 🛡️ **Zero-Drift Git Guard** | The map versions in lockstep with your codebase. Includes pre-commit hooks and GitHub Actions CI/CD to block drifted PRs automatically. |

---

### ⚖️ Before vs. After Living Codebase Map

| Dimension | Standard AI Agent (Zero Context) | With Living Codebase Map (LCM) |
|---|---|---|
| **Surgical Precision** | Hallucinates lines, overwrites adjacent code | Targets exact 100% verified `file:line` |
| **Hidden Business Traps** | Repeats previously solved production bugs | Permanently anchored in Module 4 constraints |
| **Cross-Layer Awareness** | Renaming UI button silently breaks API & DB | Instant 6-tier blast radius report in 0.05s |
| **Developer Effort** | Remember CLI syntax, juggle terminal windows | Conversational commands directly in IDE chat |

---

## 💬 Chat-Native Interface (Zero-Terminal Experience)

You **do not need to open a terminal** or find the Python script. Just type conversational commands directly in your IDE chat (Claude, Cursor, Antigravity, Windsurf, Copilot):

| What you type in Chat | What the AI Agent does automatically |
|---|---|
| `map update` | Runs `living_map.py update --auto-commit`, refreshes all line numbers, generates `PROJECT_MAP.min.md`, and shows a 3-bullet summary. |
| `map impact <symbol>` | Runs `living_map.py impact <symbol>`, analyzes 6-layer blast radius (Code, UI, API, DB, Constraints, Features) and returns impact breakdown in 0.05s. |
| `map check` | Runs Smart Drift MD5 Check in 0.02s to verify if symbol lines drifted. |
| `map constraint <text>` | Registers a hard-learned implicit rule into Module 4 with automatic `[Cx]` ID assignment. |
| `map rollback [hash]` | Checks map git commit history and rolls back to specified checkpoint. |
| `map init` | Scans workspace and bootstraps `PROJECT_MAP.md` tailored to your stack. |

---

## 🚀 3-Step Quickstart

### Step 1: Install into your project
```bash
git clone https://github.com/lekhachung1993-hub/living-codebase-map.git .agents/skills/living-codebase-map
```

### Step 2: Initialize & Scan
```bash
python .agents/skills/living-codebase-map/scripts/living_map.py init
python .agents/skills/living-codebase-map/scripts/living_map.py update
```

### Step 3: Add to your Agent rules
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
- `map update`: Run `python scripts/living_map.py update --auto-commit` and report summary.
- `map impact <symbol>`: Run `python scripts/living_map.py impact <symbol>` and display multi-tier blast radius.
- `map check`: Run `python scripts/living_map.py check` to verify zero drift.
- `map constraint <text>`: Append new implicit rule to Module 4.
- `map rollback [commit]`: View history or rollback map.
<!-- living-codebase-map:end -->
```

---

<details>
<summary><h3>🛠️ Advanced CLI Command Reference (Click to expand if running manually)</h3></summary>

### 1. Refresh Line Numbers & Mini Map
```bash
python scripts/living_map.py update
```

### 2. Auto-Commit Map with Git
```bash
python scripts/living_map.py update --auto-commit
```

### 3. Fast Blast Radius & Impact Analysis
Trace 6-tier cross-layer impact in 0.05 seconds:
```bash
python scripts/living_map.py impact <symbol_or_keyword>
```

### 4. Record a Newly Discovered Constraint
```bash
python scripts/living_map.py add-constraint "Mobile bottom bar must maintain 64px padding"
```

### 5. Register a Completed Feature
```bash
python scripts/living_map.py add-feature --id F080 --desc "Export Excel" --ui "#btn" --api "GET /api"
```

### 6. CI/CD Drift Linting (Block PR if Map drifts)
```bash
python scripts/living_map.py check
python scripts/living_map.py check --fix
```

### 7. Install Git Pre-Commit Hook
```bash
python scripts/living_map.py install-hook --hook pre-commit
```

### 8. View History & Rollback Map
```bash
python scripts/living_map.py rollback
python scripts/living_map.py rollback --to <COMMIT_HASH>
```

</details>

<details>
<summary><h3>🧩 Supported Languages & Framework Extractors (Click to expand)</h3></summary>

| Language | Frameworks & Architectures Supported | Extracted Symbols |
|---|---|---|
| **Go** | net/http, Gin, Fiber, Echo, Chi | Functions, receiver methods, structs, interfaces |
| **Python** | FastAPI, Django, Flask, PyTorch | `def`, `async def`, `class`, route decorators (`@app.get`, `@router.post`) |
| **TypeScript / JS** | Next.js (App & Pages Router), React, Vue | Next.js route handlers (`GET`, `POST`), Server Actions, `function`, arrow funcs |
| **Node.js Backend** | Express, NestJS, Fastify | `app.get()`, `router.post()`, `@Controller()`, `@Injectable()`, services |
| **Rust** | Actix-web, Axum, Rocket | `fn`, `async fn`, `pub fn`, `struct`, `impl`, route macros |
| **C# / .NET** | ASP.NET Core MVC & Web API | Controllers, actions, methods, `[HttpGet]`, `[HttpPost]` |
| **Java** | Spring Boot, Jakarta EE | Controllers, services, `@GetMapping`, `@PostMapping` |
| **PHP** | Laravel, Symfony | Routes (`Route::get`), classes, methods |
| **HTML / DOM** | HTML5, Vue Templates, JSX | Element IDs (`id="..."`), class bindings |

</details>

<details>
<summary><h3>📁 Repository Structure</h3></summary>

```
living-codebase-map/
├── .github/workflows/map-lint.yml    # CI/CD GitHub Action for pull requests
├── SKILL.md                          # Standard Agent Skill Definition (Chat-Native)
├── README.md                         # Documentation & Quickstart
├── LICENSE                           # MIT License
├── scripts/living_map.py             # Zero-dependency CLI engine (v2.2)
└── templates/
    ├── PROJECT_MAP.template.md       # Universal Living Map template
    └── PROJECT_MAP.min.template.md   # AI Token-Saver mini map template
```

</details>

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or PRs:
- Adding regex / AST support for additional languages (C#, Swift, Java, Kotlin, PHP, Elixir)
- Framework-specific extractors (Django, FastAPI, Next.js, Gin, Express)
- Enhanced git hooks or CI/CD validation actions

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

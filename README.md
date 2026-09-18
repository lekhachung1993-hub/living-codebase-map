# Living Codebase Map (LCM)

> **Surgical Precision, Implicit Constraints & Atomic Working Memory for AI Coding Agents.**  
> *Stop AI agents from hallucinating line numbers, breaking UI-to-DB connections, and repeating past production mistakes.*

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
# Living Codebase Map Protocol
Before making ANY code changes:
1. ALWAYS read `PROJECT_MAP.md` first to understand architecture, DOM bindings, and implicit constraints.
2. Check Module 4 (Implicit Constraints) to avoid known traps.
3. Locate exact code targets via Module 1 & 2 (`file:line`).
4. After completing tests, run: `python .agents/skills/living-codebase-map/scripts/living_map.py update --auto-commit`
<!-- living-codebase-map:end -->
```

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

### 3. Record a Newly Discovered Constraint
When an agent or developer discovers an unexpected edge case or implicit constraint:
```bash
python living_map.py add-constraint "Mobile bottom bar must maintain 64px padding-bottom to avoid obscuring fixed buttons"
```
*Automatically assigns ID (e.g. `[C8]`) and injects it into Module 4.*

### 4. Register a Completed Feature
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

### 5. Check Synchronization Status
Check if any line numbers in the map have drifted without editing:
```bash
python living_map.py check
```

### 6. View History & Rollback Map
View previous map commits:
```bash
python living_map.py rollback
```
Restore the map to an exact previous commit:
```bash
python living_map.py rollback --to <COMMIT_HASH>
```

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
├── SKILL.md                          # Standard Agent Skill Definition
├── README.md                         # Documentation & Quickstart
├── LICENSE                           # MIT License
├── .gitignore                        # Standard Python ignores
├── scripts/
│   └── living_map.py                 # Zero-dependency CLI engine
└── templates/
    └── PROJECT_MAP.template.md       # Universal Living Map template
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

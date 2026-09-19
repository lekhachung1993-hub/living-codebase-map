# Living Codebase Map (LCM)

> **Stable Symbol Identity, Implicit Constraints & Persistent Working Memory for AI Coding Agents.**
> *Treat line numbers as navigation hints—not identity—while preserving cross-layer knowledge and production constraints.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![Compatible with](https://img.shields.io/badge/agents-Claude%20Code%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20Windsurf%20%7C%20Copilot-orange.svg)]()

---

## ✨ 5 Breakthrough Benefits for Developers & AI

| Benefit | Real-World Impact |
|---|---|
| 🎯 **Stable Symbol Index** | `.lcm/index.json` identifies symbols by language, repository path, and qualified name; line ranges remain refreshable navigation metadata. |
| 🕸️ **Evidence-backed Dependency Graph** | `.lcm/graph.json` records dependency edges with confidence and source evidence; ambiguous call targets are not guessed. |
| 🌐 **JavaScript/TypeScript Graph** | Zero-dependency static analysis extracts named calls, test links, Express routes, and Next.js App Router handlers. |
| 📦 **Import-Aware Resolution** | Relative ESM named and namespace imports resolve aliases and duplicate symbol names to the correct JS/TS module. |
| 🐍 **Python Import Resolution** | AST-backed absolute, relative, aliased, module, package, and unique `src/` imports resolve duplicate Python symbols safely. |
| 🐹 **Go Graph Intelligence** | Receiver-qualified methods, local-module import aliases, cross-package calls and handlers, `_test.go` links, `net/http`, and common routers become evidence-backed graph relationships. |
| 🦀 **Rust Graph Intelligence** | Ranged functions, `impl` methods, module-aware `use` aliases and calls, `#[test]`, Axum, Actix, and Rocket routes become evidence-backed relationships. |
| 🔷 **C# Graph Intelligence** | Namespace/class-qualified methods, `using` aliases, calls, xUnit/NUnit/MSTest, ASP.NET controllers, and Minimal APIs become evidence-backed relationships. |
| ☕ **Java Graph Intelligence** | Package/class-qualified methods, calls, JUnit links, Spring mappings, and JAX-RS paths become evidence-backed relationships. |
| ✅ **Deterministic Integrity Check** | `map check` rebuilds and compares the map, symbol index, and graph; missing, stale, malformed, or manually altered artifacts fail CI. |
| 📜 **Structured Constraints** | `.lcm/constraints.json` stores lifecycle, severity, stable-symbol scope, reason, owner, and provenance; active rules become graph edges. |
| 🛡️ **Change Safety Engine** | `map plan` explains risk before editing; `map verify-change` checks the diff against linked tests and constraints afterward. |
| 🧩 **Dynamic Context Compiler** | `map context` selects task-relevant symbols and relationships within a real token budget; `map explain` gives one-symbol orientation. |
| 🕰️ **Git Temporal Memory** | `map why` connects a symbol to its introducing and modifying commits plus active architectural constraints. |
| 🔌 **MCP Capability Parity** | Planning, verification, context compilation, symbol explanation, and temporal history are available as native MCP tools, not only CLI commands. |
| 💸 **Compact Context** | AI can read the Mini Map (`PROJECT_MAP.min.md`) instead of loading broad source context on every turn. Measure savings on your own repository. |
| 🧠 **Permanent Working Memory** | Preserves implicit business traps and hard-learned constraints (Module 4). Even across context compactions and new sessions, AI never forgets. |
| 💬 **Chat-Native (Zero Terminal)** | No need to open terminals or run Python commands. Type `map update`, `map impact`... directly inside Claude, Cursor, Antigravity, or Copilot chat. |
| 🛡️ **Zero-Drift Git Guard** | The map versions in lockstep with your codebase. Includes pre-commit hooks and GitHub Actions CI/CD to block drifted PRs automatically. |

---

### ⚖️ Before vs. After Living Codebase Map

| Dimension | Standard AI Agent (Zero Context) | With Living Codebase Map (LCM) |
|---|---|---|
| **Surgical Precision** | Treats stale line numbers as identity | Resolves a stable Symbol ID, then uses current `file:line` as a cache |
| **Hidden Business Traps** | Repeats previously solved production bugs | Permanently anchored in Module 4 constraints |
| **Cross-Layer Awareness** | Renaming UI button can silently break API & DB | Map-assisted 6-tier blast-radius report |
| **Developer Effort** | Remember CLI syntax, juggle terminal windows | Conversational commands directly in IDE chat |

---

## 💬 Chat-Native Interface (Zero-Terminal Experience)

You **do not need to open a terminal** or find the Python script. Just type conversational commands directly in your IDE chat (Claude, Cursor, Antigravity, Windsurf, Copilot):

| What you type in Chat | What the AI Agent does automatically |
|---|---|
| `map update` | Runs `living_map.py update`, refreshes locations, writes `.lcm/index.json` and `.lcm/graph.json`, generates `PROJECT_MAP.min.md`, and leaves commits under developer control. |
| `map impact <symbol>` | Traverses graph callers/callees and combines them with the documented map layers in concise Lean Mode. |
| `map deep-impact <symbol>` | Runs `living_map.py deep-impact <symbol>`, **Deep Mode** generating an exhaustive 6-layer tree view (`├──`, `└──`) for complex refactoring. |
| `map check` | Deterministically verifies `PROJECT_MAP.md`, `.lcm/index.json`, and `.lcm/graph.json`; `--fix` rebuilds all four generated artifacts. |
| `map plan "<task>"` | Finds likely symbols/files, traverses their blast radius, and reports an explainable GREEN/YELLOW/RED risk score. |
| `map verify-change` | Compares the current Git diff with graph-linked tests and constraints; use `--strict` as a quality gate. |
| `map context "<task>" --budget 500` | Produces a task-specific context packet rather than using one static mini-map for every task. |
| `map explain <symbol>` | Shows the exact Stable Symbol ID, location, incoming callers, outgoing calls, tests, routes, and constraints. |
| `map why <symbol>` | Uses Git pickaxe history to show why a symbol appeared, how it changed, and which active constraints govern it. |
| `map constraint <text>` | Registers a hard-learned implicit rule into Module 4 with automatic `[Cx]` ID assignment. |
| `map add-feature "<prompt>"` | Natural language auto-parsing: extracts feature ID (`Fxxx`), DOM selector, API route, and registers into Module 5. |
| `map rollback [hash]` | Safe Rollback Lock: Inspects map history or restores map checkpoint (**source code is 100% untouched**). |
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
3. Resolve code targets by Symbol ID; use Module 1 & 2 `file:line` values only for navigation.

### Chat Commands (Never make the user run python scripts):
When the user sends these keywords in chat, execute the corresponding action automatically:
- `map update`: Run `python scripts/living_map.py update` and report summary; do not commit unless explicitly requested.
- `map impact <symbol>`: Run `python scripts/living_map.py impact <symbol>` (default Lean mode, <15 lines).
- `map deep-impact <symbol>`: Run `python scripts/living_map.py deep-impact <symbol>` (exhaustive 6-layer tree).
- `map check`: Run `python scripts/living_map.py check` to verify zero drift.
- `map constraint <text>`: Append new implicit rule to Module 4.
- `map rollback [commit]`: View history or rollback map safely (source code untouched).
<!-- living-codebase-map:end -->
```

---

<details>
<summary><h3>🛠️ Advanced CLI Command Reference (Optimized for AI Agents)</h3></summary>

| Command Syntax | Operational Purpose | Token Saving & Safety Mechanism |
|---|---|---|
| `python living_map.py update` | Write `.lcm/index.json` and `.lcm/graph.json`, refresh line coordinates, and generate `.min.md` | Keeps machine identity and dependencies separate from human/LLM projections. |
| `python living_map.py update --auto-commit` | Synchronize map state directly into Git history | Creates atomic memory checkpoint locking code and map. |
| `python living_map.py impact <symbol>` | Quick cross-layer blast radius scan (Lean Mode) | Default: limits output under 15 lines to prevent AI context overflow. |
| `python living_map.py deep-impact <symbol>` | Exhaustive 6-layer architecture dependency tree | Full tree analysis (`├──`, `└──`) for high-stakes refactoring. |
| `python living_map.py add-feature "<prompt>"` | Auto-parse feature from natural language | Extracts ID, UI selector (`#id`, `.class`), API, and cleans description. |
| `python living_map.py add-constraint "<text>"` | Register implicit business traps into Module 4 | Automatically assigns incremental `[Cx]` identifiers. |
| `python living_map.py check` | Rebuild and compare Markdown, symbol index, and graph state | Detects missing files, schema mismatch, stale hashes, malformed edges, and content drift. |
| `python living_map.py install-hook` | Auto-install Git Pre-commit guard | Zero-drift enforcement, blocks commits if map is out of sync. |
| `python living_map.py rollback --to <hash>` | Restore map to previous checkpoint | Safe Lock: Strictly restores `PROJECT_MAP.md`; source code is never touched. |
| `python living_map.py mcp` | Launch as Model Context Protocol (MCP) Server | Runs stdio server exposing 11 native tools to Cursor, Claude, Antigravity, Windsurf. |

</details>

---

## 🔌 Model Context Protocol (MCP) Native Server Integration

Living Codebase Map can run as an official **MCP Stdio Server**, providing 11 Native Tools to AI Agents in **Antigravity IDE, Cursor, Claude Desktop, Windsurf, and Cline**:

### 1. Install MCP SDK (optional, only needed for MCP Server mode):
```bash
pip install 'living-codebase-map[mcp]'
```
*(Note: Core CLI commands remain 100% zero-dependency even without `mcp` installed).*

### 2. Configure in your IDE:

**Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "living-codebase-map": {
      "command": "python",
      "args": ["/absolute/path/to/scripts/living_map.py", "mcp"]
    }
  }
}
```

**Cursor / Antigravity IDE (`Settings -> Features -> MCP -> Add New MCP Server`):**
- **Name:** `living-codebase-map`
- **Type:** `stdio`
- **Command:** `python /absolute/path/to/scripts/living_map.py mcp`

### 3. Native Tools Exposed to Agents:
| Native MCP Tool | Parameters | Operational Capability |
|---|---|---|
| `update_map` | `directory`, `auto_commit` | Scans workspace, writes the stable symbol index and dependency graph, updates location caches, and generates `PROJECT_MAP.min.md`. |
| `check_drift` | `full_ast` | Smart Drift verification using MD5, with optional full symbol scanning. |
| `analyze_code_impact` | `symbol`, `deep_mode` | Dual-mode blast radius: Lean mode (<15 lines) vs Deep 6-layer dependency tree. |
| `plan_change` | `task` | Build a graph-backed pre-flight plan with an explainable risk score. |
| `verify_change` | `base`, `strict` | Compare the Git diff with graph-linked tests and constraints; preserves CLI gate status. |
| `compile_context` | `task`, `budget` | Produce a task-specific context packet within the requested token budget. |
| `explain_symbol` | `symbol` | Resolve one Stable Symbol and show its callers, callees, tests, routes, and constraints. |
| `explain_symbol_history` | `symbol`, `limit` | Retrieve Git-backed changes and active constraints for a symbol. |
| `register_feature` | `prompt`, `auto_commit` | Natural language auto-parsing: extracts `Fxxx`, DOM selector, API route into Module 5. |
| `register_constraint` | `description`, `constraint_id` | Enforces implicit business traps & domain invariants in Module 4. |
| `get_map_summary` | *(none)* | Instant session warmup with lightweight architecture overview in ~300 tokens. |

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

### Dependency graph confidence

The graph extracts Python, JavaScript/TypeScript, Go, Rust, and C# `CALLS`, `TESTED_BY`, and route `HANDLES` relationships with file-and-line evidence. Python uses the standard-library AST and resolves top-level absolute, relative, aliased, module, package, and uniquely matched `src/` imports. JS/TS uses a conservative zero-dependency static pass supporting named functions, block-bodied arrow functions, Express-style routes, and Next.js App Router handlers. Relative ESM named imports, aliases, namespace imports, extensionless modules, directory `index` modules, and NodeNext-style `.js` specifiers are resolved against indexed source files. Go receiver methods use receiver-qualified Stable IDs; same-package and receiver calls remain exact, while `go.mod`-scoped default or explicit import aliases resolve cross-package function calls and route handlers without requiring a Go toolchain. Rust functions receive exact body ranges, methods are qualified by their `impl` type, and `crate`, `self`, `super`, simple `use` aliases, same-module calls, test attributes, Axum routes, plus Actix/Rocket route attributes are linked conservatively. C# symbols include namespace and class identity; regular `using` directives and type aliases disambiguate static calls across files, while direct, `this`, test, controller action, and Minimal API links remain exact.

- `1.0`: exact qualified target in the same file, including `self.method()`.
- `0.9`: the called name has exactly one candidate across the repository.
- unresolved: ambiguous or dynamic calls are omitted rather than reported as facts.

Each edge stores its extractor plus the evidence `path:line`. Calls inside comments and string literals are masked before JS/TS, Go, Rust, and C# analysis. Python wildcard imports, runtime imports, JS/TS package aliases, external or dot-imported Go packages, Rust external crates, glob or nested imports, C# dynamic dispatch and dependency-injected instance calls, anonymous inline handlers, and unbound member calls are deliberately omitted when they cannot be resolved safely. Other languages continue to use the stable symbol index and Markdown impact fallback until dedicated graph extractors are added.

### Structured constraint lifecycle

```bash
python scripts/living_map.py add-constraint "Writes must be idempotent" \
  --severity high \
  --scope py:src/service.py::OrderService.create \
  --reason "Workers retry failed jobs" \
  --owner backend
```

Constraints use `ACTIVE`, `SUSPECT`, `STALE`, or `SUPERSEDED`. Active constraints with missing Symbol IDs fail `map check`; stale constraints may retain deleted scope as historical knowledge. Active and suspect scopes produce `CONSTRAINED_BY` graph edges.

### Safety workflow

```bash
python scripts/living_map.py plan "change order creation API"
# edit code and tests
python scripts/living_map.py verify-change --base HEAD --strict
```

Risk scores explain their inputs: API exposure, constraint severity, graph blast radius, inferred dependencies, and missing linked tests. `verify-change` is advisory by default and becomes a failing quality gate with `--strict`.

### Dynamic context

```bash
python scripts/living_map.py context "fix order validation" --budget 500
python scripts/living_map.py explain create_order
```

The budget is enforced using a conservative character-to-token estimate. Ambiguous `explain` queries fail and list Stable Symbol IDs instead of silently selecting one.

### Temporal memory

```bash
python scripts/living_map.py why create_order --limit 10
```

`why` resolves the symbol first, then searches its tracked file history for commits that added or removed the symbol name. It reports the oldest matching change, recent relevant changes, and linked structured constraints. Ambiguous names require a full Stable Symbol ID.

<details>
<summary><h3>📁 Repository Structure</h3></summary>

```
living-codebase-map/
├── .github/workflows/map-lint.yml    # CI/CD GitHub Action for pull requests
├── SKILL.md                          # Standard Agent Skill Definition (Chat-Native)
├── README.md                         # Documentation & Quickstart
├── LICENSE                           # MIT License
├── scripts/living_map.py             # Zero-dependency core CLI engine (v3)
├── .lcm/index.json                    # Generated machine-readable stable symbol index
├── .lcm/graph.json                    # Generated confidence-scored dependency graph
├── .lcm/constraints.json              # Human-authored structured architectural constraints
├── tests/test_symbol_index.py         # Stable-ID and collision regression tests
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

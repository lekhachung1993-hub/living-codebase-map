---
name: living-codebase-map
description: >
  Living Codebase Map & Surgical Precision Workflow for AI Coding Agents.
  Maintains a stable machine symbol index plus PROJECT_MAP.md working memory; tracks
  Symbol IDs independently from cached file:line locations,
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
  - map init
  - session start
  - before modifying any code
  - implementing new feature
---

# Living Codebase Map: Surgical Precision for AI Agents

> **Philosophy:** AI coding models fail in production codebases not from lack of intelligence, but from **blind surgery** — missing implicit business constraints, hallucinating outdated line numbers, and severing unseen cross-layer connections between UI DOM, API contracts, and database states.
>
> **The Solution:** A stable symbol index, evidence-backed dependency graph, lifecycle-managed constraints (`.lcm/constraints.json`), and living Markdown projection. The CLI refreshes navigation locations without confusing line numbers with identity; commits remain explicit.

---

## 💬 CHAT-NATIVE INTERFACE (ZERO-TERMINAL CHAT COMMANDS)

Users **DO NOT NEED to open a terminal or locate python files**. When a user types any of these commands directly in chat, the AI Agent must autonomously execute the underlying script and return structured results:

| User Chat Command | Agent Autonomous Action |
|---|---|
| `map update` | Run `living_map.py update`, write `.lcm/index.json` and `.lcm/graph.json`, refresh location caches, generate `PROJECT_MAP.min.md`, and report a 3-bullet summary. Never auto-commit unless requested. |
| `map impact <symbol>` | Traverse graph callers/callees, merge documented cross-layer links, and return a concise report with confidence. |
| `map plan "<task>"` | Compile a task-focused file/symbol plan and explainable risk score before editing. |
| `map verify-change` | Compare the Git diff with linked tests and constraints after editing; use strict mode for a gate. |
| `map check` | Deterministically verify Markdown, symbol index, and dependency graph synchronization; rebuild every generated artifact with `--fix`. |
| `map constraint <text>` | Register implicit business rule into Module 4, assign next `[Cx]` ID, and resync mini map. |
| `map rollback [hash]` | Inspect map commit history or safely restore map checkpoint (source code is never touched). |
| `map init` | Autodetect workspace stack and bootstrap a new `PROJECT_MAP.md`. |

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
│ STEP 3: SURGERY  │ ──► Resolve Symbol ID, then navigate to its current file:line
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
   - If `PROJECT_MAP.min.md` exists, read it instead of the full map to reduce repeated context.
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

Run `python scripts/living_map.py plan "<user request>"` when the task is more than a trivial GREEN edit. Use its score reasons as evidence; do not promote or downgrade risk without explaining why.

Classify every incoming user request into one of three risk categories:

| Level | Blast Radius Criteria | Agent Action |
|---|---|---|
| 🟢 **GREEN (Low)** | CSS, styling, copy, labels, icons. No state changes, no API edits, no DOM ID changes. | Proceed directly. Verify visually. |
| 🟡 **YELLOW (Medium)** | Modifies single function logic, adds API parameter, introduces new UI button or form field. | Trace cross-layer callers. Run targeted unit/integration tests. |
| 🔴 **RED (Critical)** | Touches DB schema, core auth, data mutations, background workers, or payment/ledger logic. | **STOP & WARN:** Present impact analysis to user. Require test pass before commit. |

---

## STEP 2: CROSS-LAYER IMPACT TRACING (DUAL-MODE FAST CLI)

Before modifying any symbol, query its documented blast radius via CLI:

- **Daily Standard (Lean Mode, <15 lines):**
  ```bash
  python scripts/living_map.py impact <symbol_or_keyword>
  ```
- **Architectural Surgery (Deep Mode - Exhaustive 6-Layer Dependency Tree):**
  ```bash
  python scripts/living_map.py deep-impact <symbol_or_keyword>
  # Or: python scripts/living_map.py impact <symbol> --deep
  ```

This traces the multi-tier dependency chain:
```

When `.lcm/graph.json` exists, classify edges by confidence:

- `>= 0.95`: confirmed by an exact AST resolution.
- `0.70–0.94`: likely; inspect the stored evidence before relying on it.
- `< 0.70`: uncertain; never present it as confirmed behavior.
- Missing ambiguous targets are unknown, not safe.

Currently generated graph relations are Python AST `CALLS`, `TESTED_BY`, and HTTP route `HANDLES`. Continue using the Markdown cross-layer map as fallback for languages and relationships without a dedicated extractor.

Structured constraints must use stable Symbol IDs in `scope`. Treat `ACTIVE` and `SUSPECT` rules as graph-enforced knowledge. Use `STALE` for historical rules whose symbols no longer exist, and `SUPERSEDED` only with a valid replacement constraint ID.
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

1. **Resolve identity first:** Prefer `.lcm/index.json` Symbol IDs (`language:path::qualified.name`). Use Module 1 & 2 or `impact` only to navigate to the current `file:line`.
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

1. **Refresh the stable symbol index, location caches, and compact map:**
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
3. **Deterministic Integrity Check:**
   ```bash
   python scripts/living_map.py check
   ```
   A passing check requires the current code hash, stable index, graph schema, graph evidence, and freshly rebuilt deterministic content to match.
4. **Change consistency:**
   ```bash
   python scripts/living_map.py verify-change --base HEAD --strict
   ```

---

## STEP 5: ATOMIC GIT CHECKPOINT (CODE & MAP IN LOCKSTEP)

**The Golden Rule:** When a code change affects the map, commit code, `.lcm/index.json`, `.lcm/graph.json`, `.lcm/constraints.json`, `PROJECT_MAP.md`, and `PROJECT_MAP.min.md` together. `map update` itself must not create a commit.

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

## TROUBLESHOOTING RECIPES

### Recipe 1: When Tests Fail (Test Failure Self-Healing)
1. Read the terminal error log to pinpoint the exact `file:line` target.
2. Query `python scripts/living_map.py impact <failed_function>` to inspect linked constraints (`[Cx]`).
3. If the failure stems from a payload/type mismatch between Frontend and Backend, **never apply arbitrary type casting**. Fix both the caller (payload sender) and receiver (API handler) in lockstep.
4. Re-run targeted tests until 100% green.

### Recipe 2: When Git Hook Blocks Commit due to Drift
1. The terminal reports: `[BLOCKED] Git pre-commit aborted: PROJECT_MAP.md is out of sync`.
2. Run the automatic repair command immediately:
   ```bash
   python scripts/living_map.py check --fix
   ```
3. Stage the refreshed map and commit normally:
   ```bash
   git add .lcm/index.json .lcm/graph.json PROJECT_MAP.md PROJECT_MAP.min.md
   git commit -m "docs: sync living map"
   ```

### Recipe 3: When an Implicit Constraint is Discovered During Debugging
1. As soon as you discover an unexpected trap or domain invariant (e.g., *Mobile DOM priority*, *Snapshot async delay*):
2. Register it immediately via CLI:
   ```bash
   python scripts/living_map.py add-constraint "Description of newly discovered invariant"
   ```
3. The map automatically increments the next `[C(n+1)]` ID and regenerates `PROJECT_MAP.min.md`.

### Recipe 4: Before Modifying High-Risk Symbols (Blast Radius Check)
1. Before modifying any function or endpoint, query the lean blast radius:
   ```bash
   python scripts/living_map.py impact <symbol_name>
   ```
2. If the CLI outputs `HIGH BLAST RADIUS` or if performing major refactoring, run the exhaustive 6-layer architecture tree:
   ```bash
   python scripts/living_map.py deep-impact <symbol_name>
   ```
3. Inspect all linked UI DOM IDs, API routes, and DB models before altering code.

---

## UNIVERSAL CLI REFERENCE

| Task | Command |
|---|---|
| Initialize map for project | `python scripts/living_map.py init` |
| Refresh line numbers & mini map | `python scripts/living_map.py update` |
| Fast blast radius / impact check (Lean mode by default) | `python scripts/living_map.py impact <symbol>` |
| Exhaustive 6-layer architecture dependency tree | `python scripts/living_map.py deep-impact <symbol>` |
| Fast Smart Drift Check (MD5) | `python scripts/living_map.py check` |
| Auto-repair drifted line numbers | `python scripts/living_map.py check --fix` |
| Force full AST scan check | `python scripts/living_map.py check --full` |
| Install Git Pre-Commit Hook | `python scripts/living_map.py install-hook` |
| Update and auto-commit to Git | `python scripts/living_map.py update --auto-commit` |
| Add newly discovered constraint | `python scripts/living_map.py add-constraint "description"` |
| View commit history of map | `python scripts/living_map.py rollback` |
| Safe Rollback Lock (source code 100% untouched) | `python scripts/living_map.py rollback --to <HASH>` |
| Run as Model Context Protocol (MCP) Server | `python scripts/living_map.py mcp` |

---

## MODEL CONTEXT PROTOCOL (MCP) INTEGRATION

Living Codebase Map can be connected to any MCP-compliant AI coding assistant (Antigravity IDE, Cursor, Claude Desktop, Windsurf, Cline) via Stdio transport.

### Fast Setup:
1. `pip install mcp`
2. Add to your IDE MCP configuration:
```json
{
  "mcpServers": {
    "living-codebase-map": {
      "command": "python",
      "args": ["scripts/living_map.py", "mcp"]
    }
  }
}
```
Exposes 6 Native Tools: `update_map`, `check_drift`, `analyze_code_impact`, `register_feature`, `register_constraint`, `get_map_summary`.

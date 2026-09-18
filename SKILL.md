---
name: living-codebase-map
description: >
  Living Codebase Map & Surgical Precision Workflow for AI Coding Agents.
  Maintains PROJECT_MAP.md as living working memory: tracks symbol locations (file:line),
  DOM-to-DB cross-layer mappings, implicit constraints, and enforces risk-gated triage
  with automated git-backed synchronization.
triggers:
  - session start
  - before modifying any code
  - implementing new feature
  - debugging cross-layer issue
  - after completing any code change
---

# Living Codebase Map: Surgical Precision for AI Agents

> **Philosophy:** AI coding models fail in production codebases not from lack of intelligence, but from **blind surgery** — missing implicit business constraints, hallucinating outdated line numbers, and severing unseen cross-layer connections between UI DOM, API contracts, and database states.
>
> **The Solution:** A living, version-controlled architecture compass (`PROJECT_MAP.md`) paired with a zero-dependency CLI engine (`living_map.py`) that synchronizes symbol locations, enforces atomic git commits, and anchors agent memory across chat compactions.

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

## STEP 0: SESSION WARMUP (NEVER CODE BLIND)

**Mandatory first action of every coding session:**

1. Read `PROJECT_MAP.md` at the project root.
2. Extract working memory:
   - **Recent Commit & Feature Status** (Header & Module 8)
   - **Implicit Constraints** (Module 4) — *rules that cannot be inferred from code alone*
   - **Feature Cross-Reference** (Module 5) — find related DOM IDs and APIs
   - **Exact `file:line` locations** (Module 1 & 2)
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

## STEP 2: CROSS-LAYER IMPACT TRACING

Before modifying any symbol, trace the entire dependency chain:

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

1. **Locate exact line:** Use Module 1 & 2 in `PROJECT_MAP.md` to jump directly to `file:line`.
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

1. **Refresh symbol line numbers:**
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
3. **Verify synchronization:**
   ```bash
   python scripts/living_map.py check
   ```

---

## STEP 5: ATOMIC GIT CHECKPOINT (CODE & MAP IN LOCKSTEP)

**The Golden Rule:** Code and `PROJECT_MAP.md` must **ALWAYS** be committed together in the exact same commit.

- **Option A (Automated via CLI):**
  ```bash
  python scripts/living_map.py update --auto-commit
  ```
- **Option B (Standard Git):**
  ```bash
  git add -A
  git commit -m "feat(module): implement feature X (F079) + sync living map"
  ```

### Handling Git Rollbacks
If code is reverted or checked out to an earlier commit:
- `git checkout <hash>` automatically brings `PROJECT_MAP.md` back to that exact commit.
- To rollback ONLY the map without touching code:
  ```bash
  python scripts/living_map.py rollback --to <HASH>
  ```

---

## UNIVERSAL CLI REFERENCE

| Task | Command |
|---|---|
| Initialize map for project | `python scripts/living_map.py init` |
| Refresh line numbers | `python scripts/living_map.py update` |
| Update and auto-commit to Git | `python scripts/living_map.py update --auto-commit` |
| Preview changes (no write) | `python scripts/living_map.py update --dry-run` |
| Add newly discovered constraint | `python scripts/living_map.py add-constraint "description"` |
| Register completed feature | `python scripts/living_map.py add-feature --id Fxxx --desc "..."` |
| View commit history of map | `python scripts/living_map.py rollback` |
| Rollback map to commit | `python scripts/living_map.py rollback --to <HASH>` |
| Check if map is in sync | `python scripts/living_map.py check` |

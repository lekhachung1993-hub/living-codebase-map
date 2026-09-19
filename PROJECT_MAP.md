# LIVING PROJECT MAP: living-codebase-map v3.8.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-19 | Commit: fb5feef
>
> **AGENT PROTOCOL:**
> 1. Read MODULE 5 (Feature Cross-Reference) to identify components related to current task.
> 2. Read MODULE 1 (Code Location Index) for exact `file:line` surgery targets.
> 3. Verify MODULE 4 (Implicit Constraints) BEFORE making any code edits.
> 4. Run tests, then update this map using `python scripts/living_map.py update`.

---

## MODULE 0: META & ENVIRONMENT

| Attribute | Specification |
|---|---|
| Tech Stack | Python 3.8+ (Zero-dependency standard library CLI + optional FastMCP/MCPServer) |
| Entry Point | `scripts/living_map.py` (`living-codebase-map` / `living-map`) |
| Primary Storage | `.lcm/index.json`, `.lcm/graph.json`, plus Markdown projections |
| Package Spec | `pyproject.toml`, `manifest.json` (MCPB Bundle), `smithery.yaml` |
| Current Branch | `main` |
| Codebase-MD5 | `29b31553ba93a339281a5df623f3753e` |

---

## MODULE 1: CODE LOCATION INDEX — Core Engine & MCP Server
> Format: `file:line → function()`

### scripts/living_map.py

| Line | Symbol | Description |
|------|--------|-------------|
| L77 | `find_project_root()` | Locates the project root directory reliably |
| L138 | `calculate_codebase_hash()` | MD5 hash computation over all source files |
| L171 | `generate_min_map()` | Generates token-efficient PROJECT_MAP.min.md |
| L267 | `analyze_symbol_impact()` | Cross-layer blast radius analysis |
| L406 | `_git()` | Safe git subprocess runner |
| L421 | `git_get_head_info()` | Fetches current commit hash and date |
| L430 | `git_log_map()` | Reads git commit history of PROJECT_MAP.md |
| L446 | `git_commit_map()` | Commits map updates with atomic git message |
| L471 | `git_rollback_map()` | Reverts PROJECT_MAP.md safely to older commit |
| L517 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L671 | `_strip_javascript_noncode()` | Masks JS/TS comments and literals while preserving evidence coordinates |
| L724 | `_matching_delimiter()` | Resolves balanced JS/TS function and class body ranges |
| L739 | `_javascript_symbol_records()` | Extracts ranged named functions, arrow functions, and classes |
| L872 | `_is_test_path()` | Recognizes Python and JavaScript test path conventions |
| L885 | `_next_route_path()` | Derives Next.js App Router public paths from route modules |
| L1519 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L1558 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L1613 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L1646 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L1678 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L1714 | `cmd_init()` | CLI handler for `living-map init` |
| L1781 | `cmd_update()` | CLI handler for `living-map update` |
| L1852 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L1926 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L2082 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L2086 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L2134 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L2259 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L2322 | `cmd_plan()` | CLI handler for graph-backed change planning |
| L2347 | `cmd_verify_change()` | CLI handler for diff/test/constraint verification |
| L2370 | `cmd_context()` | CLI handler for budgeted task context compilation |
| L2382 | `cmd_explain()` | CLI handler for one-symbol relationship explanation |
| L2411 | `cmd_why()` | CLI handler for Git-backed symbol history |
| L2442 | `cmd_rollback()` | CLI handler for safe map rollback |
| L2469 | `capture_mcp_command()` | Preserves CLI exit status and output for native MCP tools |
| L2480 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L2496 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L2509 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L2525 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L2538 | `plan_change()` | MCP Tool: graph-backed pre-flight plan and risk score |
| L2543 | `verify_change()` | MCP Tool: change/test/constraint consistency gate |
| L2551 | `compile_context()` | MCP Tool: budgeted task context compiler |
| L2559 | `explain_symbol()` | MCP Tool: unambiguous Stable Symbol explanation |
| L2564 | `explain_symbol_history()` | MCP Tool: Git temporal memory and constraints |
| L2572 | `register_feature()` | MCP Tool: feature traceability registration |
| L2596 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L2613 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L2629 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

---

## MODULE 4: ARCHITECTURAL CONSTRAINTS & INVARIANTS
> Read BEFORE modifying code. Zero tolerance for regression.

- [C001] **Zero Dependencies for CLI**: Core CLI commands (`check`, `update`, `impact`, `init`) MUST run with Python standard library only (no external pip requirements).
- [C002] **Graceful MCP Degradation**: MCP server mode degrades gracefully if `mcp` library is missing, printing clear installation instructions.
- [C003] **Safe Rollback**: `rollback` MUST ONLY touch `PROJECT_MAP.md` and `PROJECT_MAP.min.md`. It MUST NEVER revert source code.
- [C004] **UTF-8 Reconfiguration**: `sys.stdout` and `sys.stderr` must be reconfigured to UTF-8 to prevent UnicodeEncodeError on Windows CP1252 consoles.

---

## MODULE 5: FEATURE TRACEABILITY MATRIX

| Feature ID | Description | Source Code | Command / Tool |
|---|---|---|---|
| F001 | Smart Drift Check (MD5) | `scripts/living_map.py:L126` | `living-map check` / `check_drift` |
| F002 | Token-Efficient Compact Map | `scripts/living_map.py:L159` | `living-map update` / `get_map_summary` |
| F003 | Cross-Layer Blast Radius Analysis | `scripts/living_map.py:L255` | `living-map impact` / `analyze_code_impact` |
| F004 | Native Model Context Protocol Server | `scripts/living_map.py:L1292` | `living-map mcp` |
| F005 | Smart Feature Auto-Parsing | `scripts/living_map.py:L1114` | `living-map add-feature` / `register_feature` |
| F006 | Safe Map Rollback Lock | `scripts/living_map.py:L451` | `living-map rollback` |
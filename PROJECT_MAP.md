# LIVING PROJECT MAP: living-codebase-map v3.9.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-19 | Commit: 6a16549
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
| Codebase-MD5 | `fdc565714b8d1e4aa2b4889dbdf840de` |

---

## MODULE 1: CODE LOCATION INDEX — Core Engine & MCP Server
> Format: `file:line → function()`

### scripts/living_map.py

| Line | Symbol | Description |
|------|--------|-------------|
| L78 | `find_project_root()` | Locates the project root directory reliably |
| L139 | `calculate_codebase_hash()` | MD5 hash computation over all source files |
| L172 | `generate_min_map()` | Generates token-efficient PROJECT_MAP.min.md |
| L268 | `analyze_symbol_impact()` | Cross-layer blast radius analysis |
| L407 | `_git()` | Safe git subprocess runner |
| L422 | `git_get_head_info()` | Fetches current commit hash and date |
| L431 | `git_log_map()` | Reads git commit history of PROJECT_MAP.md |
| L447 | `git_commit_map()` | Commits map updates with atomic git message |
| L472 | `git_rollback_map()` | Reverts PROJECT_MAP.md safely to older commit |
| L518 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L672 | `_strip_javascript_noncode()` | Masks JS/TS comments and literals while preserving evidence coordinates |
| L725 | `_matching_delimiter()` | Resolves balanced JS/TS function and class body ranges |
| L740 | `_javascript_symbol_records()` | Extracts ranged named functions, arrow functions, and classes |
| L873 | `_is_test_path()` | Recognizes Python and JavaScript test path conventions |
| L886 | `_next_route_path()` | Derives Next.js App Router public paths from route modules |
| L897 | `_resolve_javascript_module_path()` | Resolves relative ESM specifiers to indexed JS/TS source modules |
| L916 | `_javascript_import_bindings()` | Maps named aliases and namespace imports to exact Stable Symbols |
| L1610 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L1649 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L1704 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L1737 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L1769 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L1805 | `cmd_init()` | CLI handler for `living-map init` |
| L1872 | `cmd_update()` | CLI handler for `living-map update` |
| L1943 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L2017 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L2173 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L2177 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L2225 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L2350 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L2413 | `cmd_plan()` | CLI handler for graph-backed change planning |
| L2438 | `cmd_verify_change()` | CLI handler for diff/test/constraint verification |
| L2461 | `cmd_context()` | CLI handler for budgeted task context compilation |
| L2473 | `cmd_explain()` | CLI handler for one-symbol relationship explanation |
| L2502 | `cmd_why()` | CLI handler for Git-backed symbol history |
| L2533 | `cmd_rollback()` | CLI handler for safe map rollback |
| L2560 | `capture_mcp_command()` | Preserves CLI exit status and output for native MCP tools |
| L2571 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L2587 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L2600 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L2616 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L2629 | `plan_change()` | MCP Tool: graph-backed pre-flight plan and risk score |
| L2634 | `verify_change()` | MCP Tool: change/test/constraint consistency gate |
| L2642 | `compile_context()` | MCP Tool: budgeted task context compiler |
| L2650 | `explain_symbol()` | MCP Tool: unambiguous Stable Symbol explanation |
| L2655 | `explain_symbol_history()` | MCP Tool: Git temporal memory and constraints |
| L2663 | `register_feature()` | MCP Tool: feature traceability registration |
| L2687 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L2704 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L2720 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

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
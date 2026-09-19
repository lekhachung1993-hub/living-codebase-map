# LIVING PROJECT MAP: living-codebase-map v3.5.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-19 | Commit: 8414fed
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
| Codebase-MD5 | `dd5825c2404117d0ee309ca0d0b04c53` |

---

## MODULE 1: CODE LOCATION INDEX — Core Engine & MCP Server
> Format: `file:line → function()`

### scripts/living_map.py

| Line | Symbol | Description |
|------|--------|-------------|
| L68 | `find_project_root()` | Locates the project root directory reliably |
| L126 | `calculate_codebase_hash()` | MD5 hash computation over all source files |
| L159 | `generate_min_map()` | Generates token-efficient PROJECT_MAP.min.md |
| L255 | `analyze_symbol_impact()` | Cross-layer blast radius analysis |
| L394 | `_git()` | Safe git subprocess runner |
| L409 | `git_get_head_info()` | Fetches current commit hash and date |
| L418 | `git_log_map()` | Reads git commit history of PROJECT_MAP.md |
| L434 | `git_commit_map()` | Commits map updates with atomic git message |
| L451 | `git_rollback_map()` | Reverts PROJECT_MAP.md safely to older commit |
| L497 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L592 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L622 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L671 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L704 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L736 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L772 | `cmd_init()` | CLI handler for `living-map init` |
| L839 | `cmd_update()` | CLI handler for `living-map update` |
| L884 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L941 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L1062 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L1066 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L1114 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L1239 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L1265 | `cmd_rollback()` | CLI handler for safe map rollback |
| L1292 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L1308 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L1321 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L1337 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L1350 | `register_feature()` | MCP Tool: feature traceability registration |
| L1374 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L1392 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L1400 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

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
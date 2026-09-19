# LIVING PROJECT MAP: living-codebase-map v3.19.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-20 | Commit: 5888a86
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
| Codebase-MD5 | `35075bd00470432480d6afff7807f47c` |

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
| L524 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L678 | `_strip_javascript_noncode()` | Masks JS/TS comments and literals while preserving evidence coordinates |
| L731 | `_strip_rust_noncode()` | Masks Rust non-code while preserving lifetime and label apostrophes |
| L743 | `_matching_delimiter()` | Resolves balanced JS/TS function and class body ranges |
| L758 | `_javascript_symbol_records()` | Extracts ranged named functions, arrow functions, and classes |
| L807 | `_go_symbol_records()` | Extracts receiver-qualified Go methods, functions, types, and ranges |
| L849 | `_rust_symbol_records()` | Extracts ranged Rust functions, impl-qualified methods, and types |
| L909 | `_csharp_symbol_records()` | Extracts ranged, class-qualified C# methods and types |
| L964 | `_java_symbol_records()` | Extracts ranged, package/class-qualified Java methods and types |
| L901 | `_csharp_namespace_name()` | Reads a single C# namespace for stable symbol qualification |
| L1095 | `_is_test_path()` | Recognizes Python and JavaScript test path conventions |
| L1110 | `_next_route_path()` | Derives Next.js App Router public paths from route modules |
| L1121 | `_resolve_javascript_module_path()` | Resolves relative ESM specifiers to indexed JS/TS source modules |
| L1140 | `_javascript_import_bindings()` | Maps named aliases and namespace imports to exact Stable Symbols |
| L1178 | `_resolve_python_module_path()` | Resolves absolute, relative, package, and unique source-root modules |
| L1202 | `_python_import_bindings()` | Maps Python import aliases and module bindings to exact Stable Symbols |
| L1235 | `_read_go_module_name()` | Reads the local module identity from go.mod without requiring Go |
| L1246 | `_resolve_go_import_dir()` | Resolves local-module Go imports to indexed repository packages |
| L1259 | `_go_import_bindings()` | Maps default and explicit Go aliases to local indexed packages |
| L1300 | `_rust_module_components()` | Derives crate-relative module components from Rust source paths |
| L1315 | `_resolve_rust_module_path()` | Resolves crate, self, and super module paths conservatively |
| L1343 | `_rust_import_bindings()` | Maps simple Rust use aliases to exact local symbols and modules |
| L97 | `evaluate_run()` | Scores one recorded agent run against versioned benchmark ground truth |
| L148 | `render_markdown()` | Produces comparable human-readable benchmark reports |
| L183 | `evaluate_files()` | Validates and compares named baseline and LCM run files |
| L2568 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L2607 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L2662 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L2695 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L2727 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L2763 | `cmd_init()` | CLI handler for `living-map init` |
| L2830 | `cmd_update()` | CLI handler for `living-map update` |
| L2901 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L2975 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L3131 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L3135 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L3183 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L3308 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L3371 | `cmd_plan()` | CLI handler for graph-backed change planning |
| L3396 | `cmd_verify_change()` | CLI handler for diff/test/constraint verification |
| L3419 | `cmd_context()` | CLI handler for budgeted task context compilation |
| L3431 | `cmd_explain()` | CLI handler for one-symbol relationship explanation |
| L3460 | `cmd_why()` | CLI handler for Git-backed symbol history |
| L3491 | `cmd_rollback()` | CLI handler for safe map rollback |
| L3518 | `capture_mcp_command()` | Preserves CLI exit status and output for native MCP tools |
| L3529 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L3545 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L3558 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L3574 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L3587 | `plan_change()` | MCP Tool: graph-backed pre-flight plan and risk score |
| L3592 | `verify_change()` | MCP Tool: change/test/constraint consistency gate |
| L3600 | `compile_context()` | MCP Tool: budgeted task context compiler |
| L3608 | `explain_symbol()` | MCP Tool: unambiguous Stable Symbol explanation |
| L3613 | `explain_symbol_history()` | MCP Tool: Git temporal memory and constraints |
| L3621 | `register_feature()` | MCP Tool: feature traceability registration |
| L3645 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L3662 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L3678 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

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
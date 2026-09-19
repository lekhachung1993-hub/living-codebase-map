# LIVING PROJECT MAP: living-codebase-map v3.19.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-19 | Commit: 751b3f1
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
| Codebase-MD5 | `c0203172cbf3e1bbe2f22cab222e2952` |

---

## MODULE 1: CODE LOCATION INDEX — Core Engine & MCP Server
> Format: `file:line → function()`

### scripts/living_map.py

| Line | Symbol | Description |
|------|--------|-------------|
| L80 | `find_project_root()` | Locates the project root directory reliably |
| L154 | `calculate_codebase_hash()` | MD5 hash computation over all source files |
| L187 | `generate_min_map()` | Generates token-efficient PROJECT_MAP.min.md |
| L283 | `analyze_symbol_impact()` | Cross-layer blast radius analysis |
| L422 | `_git()` | Safe git subprocess runner |
| L437 | `git_get_head_info()` | Fetches current commit hash and date |
| L446 | `git_log_map()` | Reads git commit history of PROJECT_MAP.md |
| L462 | `git_commit_map()` | Commits map updates with atomic git message |
| L487 | `git_rollback_map()` | Reverts PROJECT_MAP.md safely to older commit |
| L539 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L693 | `_strip_javascript_noncode()` | Masks JS/TS comments and literals while preserving evidence coordinates |
| L746 | `_strip_rust_noncode()` | Masks Rust non-code while preserving lifetime and label apostrophes |
| L758 | `_matching_delimiter()` | Resolves balanced JS/TS function and class body ranges |
| L773 | `_javascript_symbol_records()` | Extracts ranged named functions, arrow functions, and classes |
| L822 | `_go_symbol_records()` | Extracts receiver-qualified Go methods, functions, types, and ranges |
| L864 | `_rust_symbol_records()` | Extracts ranged Rust functions, impl-qualified methods, and types |
| L924 | `_csharp_symbol_records()` | Extracts ranged, class-qualified C# methods and types |
| L979 | `_java_symbol_records()` | Extracts ranged, package/class-qualified Java methods and types |
| L916 | `_csharp_namespace_name()` | Reads a single C# namespace for stable symbol qualification |
| L1110 | `_is_test_path()` | Recognizes Python and JavaScript test path conventions |
| L1125 | `_next_route_path()` | Derives Next.js App Router public paths from route modules |
| L1136 | `_resolve_javascript_module_path()` | Resolves relative ESM specifiers to indexed JS/TS source modules |
| L1155 | `_javascript_import_bindings()` | Maps named aliases and namespace imports to exact Stable Symbols |
| L1193 | `_resolve_python_module_path()` | Resolves absolute, relative, package, and unique source-root modules |
| L1217 | `_python_import_bindings()` | Maps Python import aliases and module bindings to exact Stable Symbols |
| L1250 | `_read_go_module_name()` | Reads the local module identity from go.mod without requiring Go |
| L1261 | `_resolve_go_import_dir()` | Resolves local-module Go imports to indexed repository packages |
| L1274 | `_go_import_bindings()` | Maps default and explicit Go aliases to local indexed packages |
| L1315 | `_rust_module_components()` | Derives crate-relative module components from Rust source paths |
| L1330 | `_resolve_rust_module_path()` | Resolves crate, self, and super module paths conservatively |
| L1358 | `_rust_import_bindings()` | Maps simple Rust use aliases to exact local symbols and modules |
| L97 | `evaluate_run()` | Scores one recorded agent run against versioned benchmark ground truth |
| L148 | `render_markdown()` | Produces comparable human-readable benchmark reports |
| L183 | `evaluate_files()` | Validates and compares named baseline and LCM run files |
| L2361 | `load_fitness_config()` | Loads and validates versioned graph-health thresholds |
| L2384 | `write_fitness_config()` | Persists deterministic fitness policy for agents and CI |
| L2392 | `analyze_graph_fitness()` | Measures graph coverage, confidence, hubs, test links, and constraint health |
| L2702 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L2741 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L2796 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L2829 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L2861 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L2897 | `cmd_init()` | CLI handler for `living-map init` |
| L2968 | `cmd_update()` | CLI handler for `living-map update` |
| L3042 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L3512 | `cmd_fitness()` | Reports codebase fitness and optionally enforces thresholds |
| L3116 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L3272 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L3276 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L3324 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L3449 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L3561 | `cmd_plan()` | CLI handler for graph-backed change planning |
| L3586 | `cmd_verify_change()` | CLI handler for diff/test/constraint verification |
| L3609 | `cmd_context()` | CLI handler for budgeted task context compilation |
| L3621 | `cmd_explain()` | CLI handler for one-symbol relationship explanation |
| L3650 | `cmd_why()` | CLI handler for Git-backed symbol history |
| L3681 | `cmd_rollback()` | CLI handler for safe map rollback |
| L3708 | `capture_mcp_command()` | Preserves CLI exit status and output for native MCP tools |
| L3719 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L3735 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L3748 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L3764 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L3777 | `plan_change()` | MCP Tool: graph-backed pre-flight plan and risk score |
| L3790 | `verify_change()` | MCP Tool: change/test/constraint consistency gate |
| L3798 | `compile_context()` | MCP Tool: budgeted task context compiler |
| L3806 | `explain_symbol()` | MCP Tool: unambiguous Stable Symbol explanation |
| L3811 | `explain_symbol_history()` | MCP Tool: Git temporal memory and constraints |
| L3819 | `register_feature()` | MCP Tool: feature traceability registration |
| L3843 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L3860 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L3876 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

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
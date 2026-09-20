# LIVING PROJECT MAP: living-codebase-map v3.30.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-20 | Commit: dfcefca
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
| Codebase-MD5 | `45e5b3fc6484516c1ae89756c0193385` |

---

## MODULE 1: CODE LOCATION INDEX — Core Engine & MCP Server
> Format: `file:line → function()`

### scripts/living_map.py

| Line | Symbol | Description |
|------|--------|-------------|
| L105 | `find_project_root()` | Locates the project root directory reliably |
| L180 | `calculate_codebase_hash()` | MD5 hash computation over all source files |
| L213 | `generate_min_map()` | Generates token-efficient PROJECT_MAP.min.md |
| L316 | `analyze_symbol_impact()` | Cross-layer blast radius analysis |
| L455 | `_git()` | Safe git subprocess runner |
| L470 | `git_get_head_info()` | Fetches current commit hash and date |
| L479 | `git_log_map()` | Reads git commit history of PROJECT_MAP.md |
| L495 | `git_commit_map()` | Commits map updates with atomic git message |
| L520 | `git_rollback_map()` | Reverts PROJECT_MAP.md safely to older commit |
| L572 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L726 | `_strip_javascript_noncode()` | Masks JS/TS comments and literals while preserving evidence coordinates |
| L779 | `_strip_rust_noncode()` | Masks Rust non-code while preserving lifetime and label apostrophes |
| L791 | `_matching_delimiter()` | Resolves balanced JS/TS function and class body ranges |
| L806 | `_javascript_symbol_records()` | Extracts ranged named functions, arrow functions, and classes |
| L855 | `_go_symbol_records()` | Extracts receiver-qualified Go methods, functions, types, and ranges |
| L897 | `_rust_symbol_records()` | Extracts ranged Rust functions, impl-qualified methods, and types |
| L957 | `_csharp_symbol_records()` | Extracts ranged, class-qualified C# methods and types |
| L1012 | `_java_symbol_records()` | Extracts ranged, package/class-qualified Java methods and types |
| L949 | `_csharp_namespace_name()` | Reads a single C# namespace for stable symbol qualification |
| L1173 | `_is_test_path()` | Recognizes Python and JavaScript test path conventions |
| L1188 | `_next_route_path()` | Derives Next.js App Router public paths from route modules |
| L1199 | `_resolve_javascript_module_path()` | Resolves relative ESM specifiers to indexed JS/TS source modules |
| L1218 | `_javascript_import_bindings()` | Maps named aliases and namespace imports to exact Stable Symbols |
| L1256 | `_resolve_python_module_path()` | Resolves absolute, relative, package, and unique source-root modules |
| L1280 | `_python_import_bindings()` | Maps Python import aliases and module bindings to exact Stable Symbols |
| L1313 | `_read_go_module_name()` | Reads the local module identity from go.mod without requiring Go |
| L1324 | `_resolve_go_import_dir()` | Resolves local-module Go imports to indexed repository packages |
| L1337 | `_go_import_bindings()` | Maps default and explicit Go aliases to local indexed packages |
| L1378 | `_rust_module_components()` | Derives crate-relative module components from Rust source paths |
| L1393 | `_resolve_rust_module_path()` | Resolves crate, self, and super module paths conservatively |
| L1421 | `_rust_import_bindings()` | Maps simple Rust use aliases to exact local symbols and modules |
| L97 | `evaluate_run()` | Scores one recorded agent run against versioned benchmark ground truth |
| L148 | `compare_runs()` | Computes benchmark deltas and quality-first regression gates |
| L196 | `render_markdown()` | Produces comparable human-readable benchmark reports |
| L252 | `evaluate_files()` | Validates and compares named baseline and LCM run files |
| L2438 | `load_fitness_config()` | Loads and validates versioned graph-health thresholds |
| L2461 | `write_fitness_config()` | Persists deterministic fitness policy for agents and CI |
| L2490 | `analyze_graph_fitness()` | Measures graph coverage, confidence, hubs, test links, and constraint health |
| L2711 | `parse_unified_diff()` | Extracts changed line ranges from zero-context Git diffs |
| L2752 | `rank_test_gaps()` | Prioritizes untested hubs by graph leverage and exposure |
| L2807 | `analyze_diff_guard()` | Scores changed symbols using graph risk and linked-test evidence |
| L3005 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L3066 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L3121 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L3154 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L3186 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L3222 | `cmd_init()` | CLI handler for `living-map init` |
| L3293 | `cmd_update()` | CLI handler for `living-map update` |
| L3372 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L3855 | `cmd_fitness()` | Reports codebase fitness and optionally enforces thresholds |
| L3904 | `cmd_test_gaps()` | Reports the highest-leverage missing test evidence |
| L3932 | `cmd_guard()` | Enforces risk thresholds on exact Git diff symbols |
| L3455 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L3611 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L3615 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L3663 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L3788 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L3972 | `cmd_plan()` | CLI handler for graph-backed change planning |
| L3997 | `cmd_verify_change()` | CLI handler for diff/test/constraint verification |
| L4020 | `cmd_context()` | CLI handler for budgeted task context compilation |
| L4081 | `cmd_explain()` | CLI handler for one-symbol relationship explanation |
| L4110 | `cmd_why()` | CLI handler for Git-backed symbol history |
| L4141 | `cmd_rollback()` | CLI handler for safe map rollback |
| L4168 | `capture_mcp_command()` | Preserves CLI exit status and output for native MCP tools |
| L4179 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L4195 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L4208 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L4224 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L4237 | `plan_change()` | MCP Tool: graph-backed pre-flight plan and risk score |
| L4268 | `verify_change()` | MCP Tool: change/test/constraint consistency gate |
| L4276 | `compile_context()` | MCP Tool: budgeted task context compiler |
| L4284 | `explain_symbol()` | MCP Tool: unambiguous Stable Symbol explanation |
| L4289 | `explain_symbol_history()` | MCP Tool: Git temporal memory and constraints |
| L4318 | `register_feature()` | MCP Tool: feature traceability registration |
| L4342 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L4359 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L4375 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

### scripts/lcm_core/schema.py

| Line | Symbol | Description |
|------|--------|-------------|
| L9 | `migrate_constraints()` | Migrates versioned constraint knowledge without mutating caller data |

### scripts/lcm_core/evidence.py

| Line | Symbol | Description |
|------|--------|-------------|
| L13 | `make_provenance()` | Creates deterministic knowledge type, source, hash, and freshness metadata |
| L27 | `validate_provenance()` | Validates the evidence contract on structured knowledge |

### scripts/lcm_core/incremental.py

| Line | Symbol | Description |
|------|--------|-------------|
| L34 | `build_incremental_records()` | Reuses unchanged file extraction records through an ignored local cache |

### scripts/lcm_core/semantics.py

| Line | Symbol | Description |
|------|--------|-------------|
| L14 | `validate_markdown_semantics()` | Detects drift across structured, full-map, and compact-map projections |

### scripts/lcm_core/calm_adapter.py

| Line | Symbol | Description |
|------|--------|-------------|
| L26 | `export_calm()` | Projects observed LCM components into an optional CALM 1.2 document |
| L83 | `reconcile_calm()` | Reports declared-versus-observed component and relationship drift |

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
| F007 | Stable Symbol Identity | `scripts/living_map.py:L1022` | `living-map update` |
| F008 | Evidence-Backed Dependency Graph | `scripts/living_map.py:L1388` | `living-map impact` / `analyze_code_impact` |
| F009 | Structured Constraint Lifecycle | `scripts/living_map.py:L2207` | `living-map add-constraint` / `register_constraint` |
| F010 | Graph-Backed Change Planning | `scripts/living_map.py:L3833` | `living-map plan` / `plan_change` |
| F011 | Change Evidence Verification | `scripts/living_map.py:L3858` | `living-map verify-change` / `verify_change` |
| F012 | Hierarchical Context Compiler | `scripts/living_map.py:L2833` | `living-map context` / `compile_context` |
| F013 | Symbol Explanation and History | `scripts/living_map.py:L3893` | `living-map explain` / `living-map why` |
| F014 | Codebase Fitness Gates | `scripts/living_map.py:L2417` | `living-map fitness` / `fitness_report` |
| F015 | Risk-Aware Diff Guard | `scripts/living_map.py:L2734` | `living-map guard` / `guard_change` |
| F016 | Test-Gap Prioritization | `scripts/living_map.py:L2679` | `living-map test-gaps` / `test_gap_hotspots` |
| F017 | Incremental File-Hash Indexing | `scripts/lcm_core/incremental.py` | `living-map update` |
| F018 | Knowledge Evidence and Staleness | `scripts/lcm_core/evidence.py` | generated index and graph artifacts |
| F019 | Optional CALM Projection | `scripts/lcm_core/calm_adapter.py` | `living-map calm-export` / `export_calm_architecture` |
| F020 | Architecture Reconciliation | `scripts/lcm_core/calm_adapter.py` | `living-map calm-reconcile` / `reconcile_calm_architecture` |
| F021 | Benchmark Regression Gates | `scripts/benchmark.py` | `python scripts/benchmark.py` |
# LIVING PROJECT MAP: living-codebase-map v3.34.0
> **Purpose:** Agent's primary working memory and architectural compass. Read this file BEFORE scanning code.
> **Last Updated:** 2026-09-20 | Commit: 098dec9
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
| Codebase-MD5 | `ecb4dad9f11451736ead05d30f72c0e1` |

---

## MODULE 1: CODE LOCATION INDEX — Core Engine & MCP Server
> Format: `file:line → function()`

### scripts/living_map.py

| Line | Symbol | Description |
|------|--------|-------------|
| L137 | `find_project_root()` | Locates the project root directory reliably |
| L214 | `calculate_codebase_hash()` | MD5 hash computation over all source files |
| L247 | `generate_min_map()` | Generates token-efficient PROJECT_MAP.min.md |
| L350 | `analyze_symbol_impact()` | Cross-layer blast radius analysis |
| L489 | `_git()` | Safe git subprocess runner |
| L504 | `git_get_head_info()` | Fetches current commit hash and date |
| L513 | `git_log_map()` | Reads git commit history of PROJECT_MAP.md |
| L529 | `git_commit_map()` | Commits map updates with atomic git message |
| L554 | `git_rollback_map()` | Reverts PROJECT_MAP.md safely to older commit |
| L606 | `scan_file_symbols()` | Regex/AST symbol extractor for multi-language files |
| L760 | `_strip_javascript_noncode()` | Masks JS/TS comments and literals while preserving evidence coordinates |
| L813 | `_strip_rust_noncode()` | Masks Rust non-code while preserving lifetime and label apostrophes |
| L825 | `_matching_delimiter()` | Resolves balanced JS/TS function and class body ranges |
| L840 | `_javascript_symbol_records()` | Extracts ranged named functions, arrow functions, and classes |
| L889 | `_go_symbol_records()` | Extracts receiver-qualified Go methods, functions, types, and ranges |
| L931 | `_rust_symbol_records()` | Extracts ranged Rust functions, impl-qualified methods, and types |
| L991 | `_csharp_symbol_records()` | Extracts ranged, class-qualified C# methods and types |
| L1046 | `_java_symbol_records()` | Extracts ranged, package/class-qualified Java methods and types |
| L983 | `_csharp_namespace_name()` | Reads a single C# namespace for stable symbol qualification |
| L1207 | `_is_test_path()` | Recognizes Python and JavaScript test path conventions |
| L1222 | `_next_route_path()` | Derives Next.js App Router public paths from route modules |
| L1233 | `_resolve_javascript_module_path()` | Resolves relative ESM specifiers to indexed JS/TS source modules |
| L1252 | `_javascript_import_bindings()` | Maps named aliases and namespace imports to exact Stable Symbols |
| L1290 | `_resolve_python_module_path()` | Resolves absolute, relative, package, and unique source-root modules |
| L1314 | `_python_import_bindings()` | Maps Python import aliases and module bindings to exact Stable Symbols |
| L1347 | `_read_go_module_name()` | Reads the local module identity from go.mod without requiring Go |
| L1358 | `_resolve_go_import_dir()` | Resolves local-module Go imports to indexed repository packages |
| L1371 | `_go_import_bindings()` | Maps default and explicit Go aliases to local indexed packages |
| L1412 | `_rust_module_components()` | Derives crate-relative module components from Rust source paths |
| L1427 | `_resolve_rust_module_path()` | Resolves crate, self, and super module paths conservatively |
| L1455 | `_rust_import_bindings()` | Maps simple Rust use aliases to exact local symbols and modules |
| L2498 | `load_fitness_config()` | Loads and validates versioned graph-health thresholds |
| L2521 | `write_fitness_config()` | Persists deterministic fitness policy for agents and CI |
| L2550 | `analyze_graph_fitness()` | Measures graph coverage, confidence, hubs, test links, and constraint health |
| L2672 | `parse_unified_diff()` | Extracts changed line ranges from zero-context Git diffs |
| L2713 | `rank_test_gaps()` | Prioritizes untested hubs by graph leverage and exposure |
| L2768 | `analyze_diff_guard()` | Scores changed symbols using graph risk and linked-test evidence |
| L2902 | `build_symbol_database()` | Full codebase symbol scanner and lookup table builder |
| L2963 | `update_map_line_numbers()` | Synchronizes line numbers in MODULE 1 & 2 tables |
| L3018 | `update_map_header()` | Refreshes date, commit hash, and MD5 in header |
| L3051 | `inject_feature()` | Adds new entry into MODULE 5 Feature Traceability Matrix |
| L3083 | `inject_constraint()` | Appends new operational rule to MODULE 4 |
| L3119 | `cmd_init()` | CLI handler for `living-map init` |
| L3190 | `cmd_update()` | CLI handler for `living-map update` |
| L3296 | `cmd_check()` | CLI handler for CI/CD smart drift check |
| L3783 | `cmd_fitness()` | Reports codebase fitness and optionally enforces thresholds |
| L3832 | `cmd_test_gaps()` | Reports the highest-leverage missing test evidence |
| L3860 | `cmd_guard()` | Enforces risk thresholds on exact Git diff symbols |
| L3383 | `cmd_impact()` | CLI handler for blast radius impact analysis |
| L3539 | `cmd_deep_impact()` | CLI handler for 6-layer architecture dependency tree |
| L3543 | `cmd_install_hook()` | CLI handler for installing Git pre-commit / pre-push hooks |
| L3591 | `cmd_add_feature()` | CLI handler for feature registration (supports NLP auto-parsing) |
| L3716 | `cmd_add_constraint()` | CLI handler for adding constraints to Module 4 |
| L3900 | `cmd_plan()` | CLI handler for graph-backed change planning |
| L3925 | `cmd_verify_change()` | CLI handler for diff/test/constraint verification |
| L3948 | `cmd_context()` | CLI handler for budgeted task context compilation |
| L4112 | `cmd_explain()` | CLI handler for one-symbol relationship explanation |
| L4141 | `cmd_why()` | CLI handler for Git-backed symbol history |
| L4172 | `cmd_rollback()` | CLI handler for safe map rollback |
| L4199 | `capture_mcp_command()` | Preserves CLI exit status and output for native MCP tools |
| L4210 | `build_mcp_server()` | Factory initializing FastMCP or MCPServer instance |
| L4226 | `update_map()` | MCP Tool: updates PROJECT_MAP.md via stdio/SSE |
| L4239 | `check_drift()` | MCP Tool: fast MD5 drift check |
| L4255 | `analyze_code_impact()` | MCP Tool: blast radius impact analysis |
| L4268 | `plan_change()` | MCP Tool: graph-backed pre-flight plan and risk score |
| L4299 | `verify_change()` | MCP Tool: change/test/constraint consistency gate |
| L4307 | `compile_context()` | MCP Tool: budgeted task context compiler |
| L4315 | `explain_symbol()` | MCP Tool: unambiguous Stable Symbol explanation |
| L4320 | `explain_symbol_history()` | MCP Tool: Git temporal memory and constraints |
| L4374 | `register_feature()` | MCP Tool: feature traceability registration |
| L4398 | `register_constraint()` | MCP Tool: implicit constraint registration |
| L4415 | `get_map_summary()` | MCP Tool: returns token-saving minified summary |
| L4431 | `cmd_mcp()` | CLI handler for launching MCP server over Stdio or SSE |

### scripts/lcm_core/schema.py

| Line | Symbol | Description |
|------|--------|-------------|
| L11 | `migrate_constraints()` | Migrates versioned constraint knowledge without mutating caller data |

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

### scripts/lcm_core/engine.py

| Line | Symbol | Description |
|------|--------|-------------|
| L19 | `RepositoryEngine` | Composes pluggable index and graph builders behind a reusable contract |

### scripts/lcm_core/context.py

| Line | Symbol | Description |
|------|--------|-------------|
| L12 | `analyze_graph_impact()` | Traverses evidence relationships around an exact graph node |
| L57 | `build_change_plan()` | Produces an explainable risk-ranked change plan |
| L120 | `compile_task_context()` | Builds hierarchical evidence-aware context within a token budget |

### scripts/lcm_core/observations.py

| Line | Symbol | Description |
|------|--------|-------------|
| L54 | `evaluate_staleness()` | Derives deterministic evidence freshness from symbol and source hashes |
| L70 | `validate_observations()` | Validates operational evidence records and lifecycle state |
| L118 | `apply_observations()` | Projects observed evidence nodes and relationships into the graph |

### scripts/lcm_core/graph_cache.py

| Line | Symbol | Description |
|------|--------|-------------|
| L74 | `build_incremental_graph()` | Safely reuses or partially rebuilds graph evidence with conservative invalidation |

### scripts/proof_campaign.py

| Line | Symbol | Description |
|------|--------|-------------|
| L93 | `evaluate_campaign()` | Aggregates auditable baseline and candidate runs across repositories |

### scripts/benchmark.py

| Line | Symbol | Description |
|------|--------|-------------|
| L97 | `evaluate_run()` | Scores one recorded agent run against versioned benchmark ground truth |
| L148 | `compare_runs()` | Computes benchmark deltas and quality-first regression gates |
| L196 | `render_markdown()` | Produces comparable human-readable benchmark reports |
| L252 | `evaluate_files()` | Validates and compares named baseline and LCM run files |

### scripts/scale_benchmark.py

| Line | Symbol | Description |
|------|--------|-------------|
| L52 | `measure_repository()` | Measures commit-pinned cold and warm engine behavior without executing target code |

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
| F001 | Smart Drift Check (MD5) | `scripts/living_map.py::cmd_check` | `living-map check` / `check_drift` |
| F002 | Token-Efficient Compact Map | `scripts/living_map.py::generate_min_map` | `living-map update` / `get_map_summary` |
| F003 | Cross-Layer Blast Radius Analysis | `scripts/lcm_core/context.py::analyze_graph_impact` | `living-map impact` / `analyze_code_impact` |
| F004 | Native Model Context Protocol Server | `scripts/living_map.py::build_mcp_server` | `living-map mcp` |
| F005 | Smart Feature Auto-Parsing | `scripts/living_map.py::cmd_add_feature` | `living-map add-feature` / `register_feature` |
| F006 | Safe Map Rollback Lock | `scripts/living_map.py::git_rollback_map` | `living-map rollback` |
| F007 | Stable Symbol Identity | `scripts/living_map.py::scan_file_symbol_records` | `living-map update` |
| F008 | Evidence-Backed Dependency Graph | `scripts/living_map.py::build_dependency_graph` | `living-map impact` / `analyze_code_impact` |
| F009 | Structured Constraint Lifecycle | `scripts/living_map.py::validate_constraints` | `living-map add-constraint` / `register_constraint` |
| F010 | Graph-Backed Change Planning | `scripts/lcm_core/context.py::build_change_plan` | `living-map plan` / `plan_change` |
| F011 | Change Evidence Verification | `scripts/living_map.py::verify_changed_files` | `living-map verify-change` / `verify_change` |
| F012 | Hierarchical Context Compiler | `scripts/lcm_core/context.py::compile_task_context` | `living-map context` / `compile_context` |
| F013 | Symbol Explanation and History | `scripts/living_map.py::get_symbol_history` | `living-map explain` / `living-map why` |
| F014 | Codebase Fitness Gates | `scripts/living_map.py::analyze_graph_fitness` | `living-map fitness` / `fitness_report` |
| F015 | Risk-Aware Diff Guard | `scripts/living_map.py::analyze_diff_guard` | `living-map guard` / `guard_change` |
| F016 | Test-Gap Prioritization | `scripts/living_map.py::rank_test_gaps` | `living-map test-gaps` / `test_gap_hotspots` |
| F017 | Incremental File-Hash Indexing | `scripts/lcm_core/incremental.py` | `living-map update` |
| F018 | Knowledge Evidence and Staleness | `scripts/lcm_core/evidence.py` | generated index and graph artifacts |
| F019 | Optional CALM Projection | `scripts/lcm_core/calm_adapter.py` | `living-map calm-export` / `export_calm_architecture` |
| F020 | Architecture Reconciliation | `scripts/lcm_core/calm_adapter.py` | `living-map calm-reconcile` / `reconcile_calm_architecture` |
| F021 | Benchmark Regression Gates | `scripts/benchmark.py` | `python scripts/benchmark.py` |
| F022 | Auditable External Proof Campaigns | `scripts/proof_campaign.py` | `python scripts/proof_campaign.py` |
| F023 | Reusable Repository Engine | `scripts/lcm_core/engine.py` | library contract used by update and scale measurement |
| F024 | Hash-Backed Operational Evidence | `scripts/lcm_core/observations.py` | `living-map observe` / `record_observation` |
| F025 | Evidence Lifecycle Gate | `scripts/lcm_core/observations.py` | `living-map evidence-status` / `evidence_status` |
| F026 | Safe Incremental Graph Rebuild | `scripts/lcm_core/graph_cache.py` | `living-map update` |
| F027 | Commit-Pinned Scale Measurements | `scripts/scale_benchmark.py` | `python scripts/scale_benchmark.py` |
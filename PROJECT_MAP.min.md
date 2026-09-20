# LIVING PROJECT MAP (COMPACT AI WORKING MEMORY)
> **Notice:** This is the token-efficient compact map. Read this first.
> For exact line surgery, query the full map or use: `python living_map.py impact <symbol>`


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
- **scripts/living_map.py:** `find_project_root()`, `calculate_codebase_hash()`, `generate_min_map()`, `analyze_symbol_impact()`, `_git()`, `git_get_head_info()`, `git_log_map()`, `git_commit_map()`, `git_rollback_map()`, `scan_file_symbols()`, `_strip_javascript_noncode()`, `_strip_rust_noncode()`, `_matching_delimiter()`, `_javascript_symbol_records()`, `_go_symbol_records()`, `_rust_symbol_records()`, `_csharp_symbol_records()`, `_java_symbol_records()`, `_csharp_namespace_name()`, `_is_test_path()`, `_next_route_path()`, `_resolve_javascript_module_path()`, `_javascript_import_bindings()`, `_resolve_python_module_path()`, `_python_import_bindings()`, `_read_go_module_name()`, `_resolve_go_import_dir()`, `_go_import_bindings()`, `_rust_module_components()`, `_resolve_rust_module_path()`
- **scripts/lcm_core/schema.py:** `migrate_constraints()`
- **scripts/lcm_core/evidence.py:** `make_provenance()`, `validate_provenance()`
- **scripts/lcm_core/incremental.py:** `build_incremental_records()`
- **scripts/lcm_core/semantics.py:** `validate_markdown_semantics()`
- **scripts/lcm_core/calm_adapter.py:** `export_calm()`, `reconcile_calm()`

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
# Living Codebase Map

Deterministic codebase intelligence and change-safety tooling for AI coding agents.

[![CI](https://github.com/lekhachung1993-hub/living-codebase-map/actions/workflows/ci.yml/badge.svg)](https://github.com/lekhachung1993-hub/living-codebase-map/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg)](https://www.python.org/)
[![Core dependencies](https://img.shields.io/badge/core%20dependencies-0-brightgreen.svg)](#installation)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Living Codebase Map (LCM) turns a repository into a versioned model that coding agents can inspect before a change and verify afterward. It combines stable symbol identities, an evidence-backed dependency graph, structured architectural constraints, focused context retrieval, risk analysis, and CI gates in one local-first tool.

LCM is designed to complement an agent's normal code search and reasoning. It does not replace a compiler, language server, test suite, or human review.

## Why LCM

AI coding agents often start each task with incomplete repository context. File search can find text, but it does not preserve stable symbol identity, explain why a rule exists, or reliably show which callers, tests, routes, and constraints are connected to a proposed change.

LCM adds a deterministic repository layer that can be committed and reviewed with the code:

- **Stable symbol IDs** remain consistent when line numbers move.
- **Evidence-backed graph edges** connect calls, imports, tests, routes, and constraints without guessing ambiguous targets.
- **Change planning and verification** expose likely blast radius before editing and missing evidence afterward.
- **Structured constraints** preserve architectural and operational rules with ownership, severity, scope, and provenance.
- **Focused context packets** give agents task-relevant symbols and relationships within a token budget.
- **Fitness and guard gates** make map quality and change risk enforceable in CI.

## Generated repository model

| Artifact | Purpose |
|---|---|
| `.lcm/index.json` | Stable symbol identities, current locations, language, kind, signature, and content hashes |
| `.lcm/graph.json` | Typed relationships with source evidence and confidence scores |
| `.lcm/constraints.json` | Structured architectural constraints and lifecycle metadata |
| `.lcm/fitness.json` | Versioned thresholds for graph, test-link, and constraint health |
| `PROJECT_MAP.md` | Human-readable architecture, integrations, constraints, and feature registry |
| `PROJECT_MAP.min.md` | Compact generated map for broad agent orientation |

These artifacts are deterministic outputs. Regenerate them with LCM instead of editing generated data manually.

## Installation

LCM's core CLI uses only the Python standard library and supports Python 3.8 or newer.

### Repository-local installation

This layout works well when the map should travel with a project and be discoverable by coding agents:

```bash
git clone https://github.com/lekhachung1993-hub/living-codebase-map.git \
  .agents/skills/living-codebase-map

python .agents/skills/living-codebase-map/scripts/living_map.py init
python .agents/skills/living-codebase-map/scripts/living_map.py update
python .agents/skills/living-codebase-map/scripts/living_map.py check
```

### Editable package installation

```bash
python -m pip install -e .
living-map --help
```

MCP support is optional:

```bash
python -m pip install -e '.[mcp]'
living-map mcp
```

## Recommended workflow

```bash
# Refresh the repository model.
living-map update

# Inspect likely scope and risk before editing.
living-map plan "change authentication token validation"
living-map context "change authentication token validation" --budget 800
living-map impact <symbol-id-or-name>

# Make the code change, then validate its evidence.
living-map verify-change --strict
living-map guard --fail-on high

# Commit regenerated artifacts with the code.
living-map update
living-map check
```

For CI, run the project's tests together with `living-map check`, `living-map fitness --strict`, and the guard policy appropriate for the repository.

## Core capabilities

### Stable symbol index and dependency graph

LCM identifies symbols by language, repository path, and qualified name. Line ranges are refreshable navigation metadata rather than identity.

Graph relationships include source evidence and a confidence score:

- `1.0` — exact module-, package-, namespace-, or type-aware resolution.
- `0.9` — conservative repository-wide resolution when exactly one candidate exists.
- Unresolved or ambiguous targets are omitted rather than guessed.

The graph supports callers, callees, test links, routes, imports, and active constraints. `impact`, `deep-impact`, `explain`, `plan`, and `verify-change` build on the same generated evidence.

### Structured constraints

`living-map add-constraint` records rules in `.lcm/constraints.json` with:

- a stable constraint ID;
- lifecycle state and severity;
- symbol or path scope;
- reason, owner, and provenance;
- optional verification guidance.

Active symbol-scoped rules are projected into the graph so they appear in planning, explanation, guard, and verification output.

### Change-safety analysis

`living-map guard` maps Git diff hunks to symbols and scores risk using graph fan-in, public routes, active constraints, edge confidence, and linked tests. `living-map verify-change` then checks whether the current diff has corresponding test and constraint evidence.

These commands provide explainable signals; they do not claim that a change is semantically correct.

### Fitness and test-gap reporting

`living-map fitness` evaluates the generated model against versioned thresholds. `living-map test-gaps` ranks untested hubs using dependency centrality, API exposure, and constraint severity so teams can prioritize high-value coverage work.

### Focused and temporal context

`living-map context` compiles a task-specific context packet under a token budget. `living-map explain` provides one-symbol orientation, while `living-map why` combines Git history with active constraints to show how a symbol evolved and which rules currently govern it.

### Benchmark and regression gates

The benchmark evaluator compares observed agent runs using task success, retrieval precision and recall, token use, tool calls, duration, and missed dependencies, tests, or constraints. Baseline and delta gates can detect regressions across releases.

Benchmark templates are not product-performance evidence by themselves. Meaningful claims require recorded runs on representative repositories and tasks.

## CLI reference

| Command | Purpose |
|---|---|
| `living-map init` | Bootstrap LCM artifacts for a repository |
| `living-map update` | Regenerate the map, symbol index, graph, and compact map |
| `living-map check` | Rebuild and compare generated artifacts to detect drift |
| `living-map fitness` | Measure model quality against configured thresholds |
| `living-map test-gaps` | Rank high-impact symbols without linked test evidence |
| `living-map guard` | Score the current Git diff and enforce a risk policy |
| `living-map impact` | Show direct graph impact for a symbol |
| `living-map deep-impact` | Traverse a broader dependency tree |
| `living-map install-hook` | Install the repository pre-commit drift check |
| `living-map add-feature` | Register a feature in the human-readable map |
| `living-map add-constraint` | Create or update a structured constraint |
| `living-map plan` | Find likely symbols, blast radius, constraints, tests, and risk before editing |
| `living-map verify-change` | Validate the current diff against graph-linked evidence |
| `living-map context` | Compile task-specific context under a token budget |
| `living-map explain` | Explain a symbol, its relationships, routes, tests, and constraints |
| `living-map why` | Show Git history and active constraints for a symbol |
| `living-map rollback` | Inspect or restore generated-map checkpoints |
| `living-map mcp` | Start the optional MCP server |

Run `living-map <command> --help` for command-specific options.

## MCP integration

The optional MCP server exposes 14 tools so compatible clients can use the same model without parsing terminal output.

| Workflow | MCP tools |
|---|---|
| Model maintenance | `update_map`, `check_drift`, `get_map_summary` |
| Planning and impact | `analyze_code_impact`, `plan_change`, `compile_context` |
| Change verification | `guard_change`, `verify_change` |
| Health and coverage | `fitness_report`, `test_gap_hotspots` |
| Symbol understanding | `explain_symbol`, `explain_symbol_history` |
| Repository knowledge | `register_feature`, `register_constraint` |

Start the server with:

```bash
living-map mcp
```

Configure the MCP client to launch that command from the repository root. The exact configuration format depends on the client.

## Language coverage

LCM uses conservative, zero-core-dependency static analysis. Dedicated graph extractors currently cover:

| Language | Current graph evidence |
|---|---|
| Python | AST-backed imports, aliases, calls, tests, and common route patterns |
| JavaScript / TypeScript | Relative ESM imports, aliases, calls, tests, Express routes, and Next.js App Router handlers |
| Go | `go.mod` package resolution, import aliases, receiver methods, tests, `net/http`, and common routers |
| Rust | `crate` / `self` / `super` modules, `use` aliases, calls, tests, Axum, Actix, and Rocket routes |
| C# | Namespaces, `using` aliases, methods, tests, ASP.NET controllers, and Minimal APIs |
| Java | Packages, class and static imports, calls, JUnit links, Spring mappings, and JAX-RS paths |

PHP, HTML, and Vue files can contribute stable map and symbol information, but they do not yet have the same dedicated import-aware graph coverage as the languages above.

## Known limitations

- Dynamic imports, reflection, generated code, dependency-injection dispatch, runtime monkey-patching, wildcard-heavy resolution, and indirect calls may not produce graph edges.
- LCM performs static repository analysis with the Python standard library; it is not a compiler, type checker, or language server.
- Framework detection is pattern-based and intentionally conservative.
- A linked test is evidence of coverage, not proof that the relevant behavior is asserted.
- Git history features require the repository and relevant commits to be available locally.
- Large polyglot repositories should tune fitness and guard thresholds to their architecture rather than treating the defaults as universal.

## Agent integration

A repository-level instruction can make the workflow explicit for any coding agent:

```md
Before editing code:
1. Run `living-map check` and refresh with `living-map update` if needed.
2. Run `living-map plan "<task>"` and inspect relevant constraints.
3. Use `living-map context "<task>"` or `living-map explain <symbol>` for focused context.

After editing code:
1. Run the relevant project tests.
2. Run `living-map verify-change --strict` and the repository guard policy.
3. Run `living-map update`, then `living-map check`.
4. Commit generated LCM artifacts with the source change.
```

## Repository layout

```text
living-codebase-map/
├── scripts/living_map.py        # CLI entry point and core workflows
├── scripts/mcp_server.py        # Optional MCP server
├── tests/                       # Unit and integration tests
├── benchmarks/                  # Benchmark tasks, schemas, and evaluator
├── .github/workflows/           # CI and release automation
├── SKILL.md                     # Coding-agent skill instructions
├── manifest.json                # Skill metadata
└── pyproject.toml               # Python package metadata
```

## Contributing

Contributions should preserve deterministic output and conservative resolution. Before opening a pull request, run:

```bash
python -m unittest discover -s tests -v
python scripts/living_map.py update
python scripts/living_map.py check
python scripts/living_map.py fitness --strict
git diff --check
```

When adding graph coverage, include fixtures for aliases, duplicate symbol names, unresolved targets, test links, and framework routes where applicable.

## License

[MIT](LICENSE)

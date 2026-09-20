# LCM Product Doctrine

Living Codebase Map is a verified operational-memory and change-safety engine for AI coding agents.

## Independent scope

LCM is code-first, evidence-first, agent-first, local-first, and continuously refreshed. Its core source of truth is repository evidence: symbols, relationships, tests, routes, constraints, Git history, and observed change state.

LCM is not an architecture modeling language, diagram editor, enterprise registry, or governance hub. Features are accepted when they improve knowledge accuracy, freshness, retrieval, change safety, explainability, or measurable agent outcomes.

## Relationship with CALM

CALM is an optional interoperability target and a useful reference for schema evolution, validation, provenance, lifecycle management, and architecture governance. LCM does not use the CALM schema as its internal model and has no mandatory CALM dependency.

The optional adapter supports three operating modes:

1. **Standalone:** LCM runs without CALM.
2. **CALM-aware:** declared architecture may be consumed as `DECLARED` knowledge.
3. **Reconciliation:** declared architecture is compared with code evidence to report components or relationships present on only one side.

Declared architecture is never silently promoted to an observed fact. Interoperability code remains outside the core indexing and graph packages.

## Knowledge contract

LCM distinguishes:

- `FACT`: extracted directly from a deterministic source parser;
- `DERIVED`: produced by a deterministic rule over facts;
- `INFERRED`: proposed by a heuristic or model and not yet verified;
- `DECLARED`: intentionally supplied by a human or external architecture model;
- `OBSERVED`: supported by runtime, test, or operational evidence.

Each knowledge item should carry provenance and a freshness state. Unknown and ambiguous relationships are omitted or marked explicitly; they are never presented as confirmed facts.

Operational observations use content-addressed evidence rather than elapsed time alone. A changed artifact becomes suspect and a missing symbol or artifact becomes stale, keeping lifecycle decisions deterministic and reviewable.

## Roadmap guardrail

Language breadth, UI, hosting, and enterprise features remain secondary to:

1. semantic correctness and dogfooding;
2. modular contracts and migrations;
3. evidence and staleness;
4. incremental performance;
5. hierarchical context quality;
6. benchmarked agent outcomes;
7. optional interoperability.

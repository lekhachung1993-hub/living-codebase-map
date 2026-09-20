"""Core contracts for Living Codebase Map.

The package keeps storage schemas, evidence semantics, incremental indexing,
and optional interoperability adapters independent from the CLI surface.
"""

from .schema import (
    CACHE_SCHEMA_VERSION,
    CONSTRAINT_SCHEMA_VERSION,
    GRAPH_SCHEMA_VERSION,
    INDEX_SCHEMA_VERSION,
    migrate_constraints,
)

__all__ = [
    'CACHE_SCHEMA_VERSION',
    'CONSTRAINT_SCHEMA_VERSION',
    'GRAPH_SCHEMA_VERSION',
    'INDEX_SCHEMA_VERSION',
    'migrate_constraints',
]

"""Versioned LCM artifact schemas and deterministic migrations."""

INDEX_SCHEMA_VERSION = 4
GRAPH_SCHEMA_VERSION = 3
CONSTRAINT_SCHEMA_VERSION = 2
CACHE_SCHEMA_VERSION = 1
GRAPH_CACHE_SCHEMA_VERSION = 1
OBSERVATION_SCHEMA_VERSION = 1


def migrate_constraints(payload):
    """Return a v2 constraint payload without mutating the caller's object."""
    if not isinstance(payload, dict):
        return payload
    version = payload.get('schema_version', 1)
    if version == CONSTRAINT_SCHEMA_VERSION:
        return payload
    if version != 1:
        return payload
    migrated = []
    for raw in payload.get('constraints', []):
        if not isinstance(raw, dict):
            migrated.append(raw)
            continue
        entry = dict(raw)
        entry.setdefault('knowledge_type', 'DECLARED')
        entry.setdefault('staleness', 'FRESH')
        entry.setdefault('verification', [])
        entry.setdefault('source', {
            'kind': 'human',
            'path': '.lcm/constraints.json',
        })
        migrated.append(entry)
    return {
        **payload,
        'schema_version': CONSTRAINT_SCHEMA_VERSION,
        'constraints': migrated,
    }

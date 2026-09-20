"""Evidence and provenance contracts shared by LCM artifacts."""

import hashlib

KNOWLEDGE_TYPES = {'FACT', 'DERIVED', 'INFERRED', 'DECLARED', 'OBSERVED'}
STALENESS_STATES = {'FRESH', 'SUSPECT', 'STALE'}


def digest_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def make_provenance(knowledge_type, extractor, path, source_hash, line=None):
    """Build deterministic provenance; timestamps are deliberately excluded."""
    payload = {
        'knowledge_type': knowledge_type,
        'extractor': extractor,
        'source': {'path': path},
        'source_hash': source_hash,
        'staleness': 'FRESH',
    }
    if line is not None:
        payload['source']['line'] = int(line)
    return payload


def validate_provenance(payload, label='knowledge'):
    issues = []
    if payload.get('knowledge_type') not in KNOWLEDGE_TYPES:
        issues.append(f'{label}: invalid knowledge_type')
    if payload.get('staleness') not in STALENESS_STATES:
        issues.append(f'{label}: invalid staleness')
    source = payload.get('source')
    if not isinstance(source, dict) or not source.get('path'):
        issues.append(f'{label}: source.path is required')
    return issues

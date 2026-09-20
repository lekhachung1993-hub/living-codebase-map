"""Deterministic lifecycle for test, coverage, and runtime observations."""

import hashlib
import json
import os

from .schema import OBSERVATION_SCHEMA_VERSION

OBSERVATION_KINDS = {'test', 'coverage', 'runtime', 'benchmark', 'ci'}
OBSERVATION_RESULTS = {'pass', 'fail', 'present', 'absent', 'unknown'}


def repository_evidence_path(root_dir, source):
    """Resolve a repository-relative evidence path without allowing escape."""
    if not isinstance(source, str) or not source or os.path.isabs(source):
        return None
    root = os.path.realpath(root_dir)
    candidate = os.path.realpath(os.path.join(root, source))
    try:
        return candidate if os.path.commonpath([root, candidate]) == root else None
    except ValueError:
        return None


def file_sha256(path):
    try:
        with open(path, 'rb') as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return None


def observation_id(symbol, kind, source):
    digest = hashlib.sha256(f'{symbol}|{kind}|{source}'.encode('utf-8')).hexdigest()[:12]
    return 'O' + digest.upper()


def load_observations(path):
    if not os.path.exists(path):
        return {'schema_version': OBSERVATION_SCHEMA_VERSION, 'observations': []}
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def write_observations(payload, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    os.replace(temporary, path)


def evaluate_staleness(observation, root_dir, symbol_ids):
    """Derive freshness from stable symbol identity and source content."""
    if observation.get('symbol') not in symbol_ids:
        return 'STALE'
    source = observation.get('source', {}).get('path')
    absolute_source = repository_evidence_path(root_dir, source)
    if not absolute_source:
        return 'STALE'
    current_hash = file_sha256(absolute_source)
    if current_hash is None:
        return 'STALE'
    if current_hash != observation.get('source_hash'):
        return 'SUSPECT'
    return 'FRESH'


def validate_observations(payload, index, root_dir):
    issues = []
    if payload.get('schema_version') != OBSERVATION_SCHEMA_VERSION:
        issues.append(f'observation schema must be {OBSERVATION_SCHEMA_VERSION}')
    records = payload.get('observations')
    if not isinstance(records, list):
        return issues + ['observations must be a list']
    symbol_ids = {symbol['id'] for symbol in index.get('symbols', [])}
    seen = set()
    for position, item in enumerate(records):
        if not isinstance(item, dict):
            issues.append(f'observation {position}: must be an object')
            continue
        oid = item.get('id')
        if not oid:
            issues.append(f'observation {position}: id is required')
        elif oid in seen:
            issues.append(f'duplicate observation id: {oid}')
        seen.add(oid)
        if item.get('kind') not in OBSERVATION_KINDS:
            issues.append(f'{oid or position}: invalid kind')
        if item.get('result') not in OBSERVATION_RESULTS:
            issues.append(f'{oid or position}: invalid result')
        if not item.get('symbol'):
            issues.append(f'{oid or position}: symbol is required')
        source = item.get('source')
        if not isinstance(source, dict) or not source.get('path'):
            issues.append(f'{oid or position}: source.path is required')
        elif repository_evidence_path(root_dir, source['path']) is None:
            issues.append(f'{oid or position}: source.path must stay inside the repository')
        source_hash = item.get('source_hash')
        if not isinstance(source_hash, str) or len(source_hash) != 64:
            issues.append(f'{oid or position}: source_hash must be a SHA-256 digest')
        else:
            try:
                int(source_hash, 16)
            except ValueError:
                issues.append(f'{oid or position}: source_hash must be a SHA-256 digest')
        line = item.get('line')
        if line is not None and (isinstance(line, bool) or not isinstance(line, int) or line < 1):
            issues.append(f'{oid or position}: line must be a positive integer')
        declared = item.get('staleness')
        actual = evaluate_staleness(item, root_dir, symbol_ids)
        if declared not in {None, actual}:
            issues.append(f'{oid or position}: staleness must be {actual}')
    return issues


def apply_observations(graph, payload, root_dir):
    symbol_ids = {
        node['id'] for node in graph.get('nodes', [])
        if node.get('type') == 'symbol'
    }
    nodes = list(graph.get('nodes', []))
    edges = list(graph.get('edges', []))
    for item in payload.get('observations', []):
        staleness = evaluate_staleness(item, root_dir, symbol_ids)
        node_id = f"observation:{item['id']}"
        nodes.append({
            'id': node_id,
            'type': 'observation',
            'name': item['id'],
            'kind': item['kind'],
            'result': item['result'],
            'path': item['source']['path'],
            'source_hash': item['source_hash'],
            'knowledge_type': 'OBSERVED',
            'staleness': staleness,
        })
        if item.get('symbol') in symbol_ids:
            edges.append({
                'source': item['symbol'],
                'target': node_id,
                'relation': 'OBSERVED_BY',
                'confidence': 1.0,
                'evidence': {
                    'path': item['source']['path'],
                    'line': item.get('line', 0),
                    'source': item['kind'],
                },
                'knowledge_type': 'OBSERVED',
                'staleness': staleness,
            })
    return {**graph, 'nodes': nodes, 'edges': edges}


def observation_summary(graph):
    observations = [
        node for node in graph.get('nodes', [])
        if node.get('type') == 'observation'
    ]
    states = {'FRESH': 0, 'SUSPECT': 0, 'STALE': 0}
    results = {}
    for node in observations:
        states[node.get('staleness', 'STALE')] = states.get(node.get('staleness'), 0) + 1
        results[node.get('result', 'unknown')] = results.get(node.get('result', 'unknown'), 0) + 1
    return {'total': len(observations), 'staleness': states, 'results': results}

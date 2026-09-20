"""Safe incremental graph reuse with explicit invalidation rules."""

import hashlib
import json
import os

from .schema import GRAPH_CACHE_SCHEMA_VERSION

GRAPH_BUILDER_VERSION = 2


def _resolution_fingerprint(index):
    records = [
        (
            symbol.get('id'), symbol.get('language'), symbol.get('kind'),
            symbol.get('qualified_name'), symbol.get('receiver'),
            symbol.get('receiver_type'),
        )
        for symbol in index.get('symbols', [])
    ]
    rendered = json.dumps(sorted(records), ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(rendered.encode('utf-8')).hexdigest()


def _environment_hash(root_dir):
    hasher = hashlib.sha256()
    for relative in ('go.mod', 'pyproject.toml', 'package.json', 'Cargo.toml'):
        path = os.path.join(root_dir, relative)
        if not os.path.exists(path):
            continue
        hasher.update(relative.encode('utf-8'))
        try:
            with open(path, 'rb') as handle:
                hasher.update(handle.read())
        except OSError:
            pass
    return hasher.hexdigest()


def _read_cache(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if (
        payload.get('schema_version') != GRAPH_CACHE_SCHEMA_VERSION
        or payload.get('builder_version') != GRAPH_BUILDER_VERSION
    ):
        return None
    return payload


def _write_cache(path, index, graph, root_dir):
    if not path:
        return
    payload = {
        'schema_version': GRAPH_CACHE_SCHEMA_VERSION,
        'builder_version': GRAPH_BUILDER_VERSION,
        'environment_hash': _environment_hash(root_dir),
        'resolution_fingerprint': _resolution_fingerprint(index),
        'graph': graph,
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    os.replace(temporary, path)


def build_incremental_graph(index, root_dir, cache_path, index_stats, builder):
    """Reuse or partially rebuild the graph only when resolution is stable."""
    cached = _read_cache(cache_path)
    changed = set(index_stats.get('changed_paths', []))
    removed = set(index_stats.get('removed_paths', []))
    environment_matches = bool(
        cached and cached.get('environment_hash') == _environment_hash(root_dir)
    )
    resolution_matches = bool(
        cached
        and cached.get('resolution_fingerprint') == _resolution_fingerprint(index)
    )

    if cached and resolution_matches and environment_matches and not changed and not removed:
        graph = cached['graph']
        return graph, {'mode': 'reused', 'files_recomputed': 0}

    if cached and resolution_matches and environment_matches and changed and not removed:
        partial = builder(index, root_dir, source_paths=changed)
        retained_api_nodes = [
            node for node in cached['graph'].get('nodes', [])
            if node.get('type') == 'api' and node.get('path') not in changed
        ]
        symbol_nodes = [node for node in partial.get('nodes', []) if node.get('type') == 'symbol']
        changed_api_nodes = [node for node in partial.get('nodes', []) if node.get('type') == 'api']
        retained_edges = [
            edge for edge in cached['graph'].get('edges', [])
            if edge.get('evidence', {}).get('path') not in changed
        ]
        graph = {
            **partial,
            'nodes': symbol_nodes + retained_api_nodes + changed_api_nodes,
            'edges': retained_edges + partial.get('edges', []),
        }
        graph['nodes'] = sorted(graph['nodes'], key=lambda item: item['id'])
        graph['edges'] = sorted(
            graph['edges'],
            key=lambda item: (
                item['source'], item['target'], item['relation'],
                item.get('evidence', {}).get('path', ''),
                item.get('evidence', {}).get('line', 0),
            ),
        )
        _write_cache(cache_path, index, graph, root_dir)
        return graph, {'mode': 'partial', 'files_recomputed': len(changed)}

    graph = builder(index, root_dir)
    _write_cache(cache_path, index, graph, root_dir)
    reason = (
        'resolution-signature-change'
        if cached and not resolution_matches
        else 'cold-or-environment-change'
    )
    return graph, {
        'mode': 'full',
        'files_recomputed': len(index.get('files', [])),
        'reason': reason,
    }

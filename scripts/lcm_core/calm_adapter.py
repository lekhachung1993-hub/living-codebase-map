"""Optional CALM interoperability profile.

The adapter has no runtime dependency on CALM. It projects verified LCM
components into a small CALM architecture document and reconciles declarations
back against the observed code graph.
"""

import re

CALM_SCHEMA = 'https://calm.finos.org/release/1.2/meta/calm.json'


def _slug(value):
    value = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    return value or 'root'


def _component(path):
    normalized = path.replace('\\', '/')
    parts = [part for part in normalized.split('/') if part]
    if len(parts) <= 1:
        return 'root'
    return parts[0]


def export_calm(index, graph, name='LCM observed architecture'):
    components = sorted({_component(item['path']) for item in index.get('files', [])})
    component_ids = {component: _slug(component) for component in components}
    nodes = [
        {
            'unique-id': component_ids[component],
            'node-type': 'service',
            'name': component,
            'description': f'Observed source component: {component}',
            'metadata': [{'lcm-path': component, 'lcm-knowledge-type': 'DERIVED'}],
        }
        for component in components
    ]
    node_by_symbol = {
        node['id']: _component(node.get('path', ''))
        for node in graph.get('nodes', []) if node.get('type') == 'symbol'
    }
    observed = set()
    for edge in graph.get('edges', []):
        source = node_by_symbol.get(edge.get('source'))
        target = node_by_symbol.get(edge.get('target'))
        if not source or not target or source == target:
            continue
        observed.add((source, target))
    relationships = []
    for source, target in sorted(observed):
        relationships.append({
            'unique-id': f'{component_ids[source]}-to-{component_ids[target]}',
            'description': 'Observed from evidence-backed LCM graph edges.',
            'relationship-type': {
                'connects': {
                    'source': {'node': component_ids[source]},
                    'destination': {'node': component_ids[target]},
                }
            },
            'metadata': [{'lcm-knowledge-type': 'OBSERVED'}],
        })
    return {
        '$schema': CALM_SCHEMA,
        'unique-id': _slug(name),
        'name': name,
        'description': 'Architecture projection generated from deterministic LCM evidence.',
        'nodes': nodes,
        'relationships': relationships,
    }


def _relationship_pair(item):
    relation = item.get('relationship-type', {})
    details = relation.get('connects') or relation.get('interacts') or relation.get('deployed-in')
    if not isinstance(details, dict):
        return None
    source = details.get('source', {}).get('node')
    destination = details.get('destination', {}).get('node')
    return (source, destination) if source and destination else None


def reconcile_calm(declared, observed):
    declared_nodes = {item.get('unique-id') for item in declared.get('nodes', []) if item.get('unique-id')}
    observed_nodes = {item.get('unique-id') for item in observed.get('nodes', []) if item.get('unique-id')}
    declared_edges = {pair for pair in map(_relationship_pair, declared.get('relationships', [])) if pair}
    observed_edges = {pair for pair in map(_relationship_pair, observed.get('relationships', [])) if pair}
    return {
        'declared_not_observed': sorted(declared_nodes - observed_nodes),
        'implemented_not_declared': sorted(observed_nodes - declared_nodes),
        'relationship_drift': [list(pair) for pair in sorted(declared_edges ^ observed_edges)],
        'in_sync': declared_nodes == observed_nodes and declared_edges == observed_edges,
    }

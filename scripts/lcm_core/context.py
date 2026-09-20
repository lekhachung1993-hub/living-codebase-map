"""Pure graph planning and context compilation contracts."""

import re


TRAVERSABLE_RELATIONS = {
    'CALLS', 'TESTED_BY', 'HANDLES', 'TRIGGERS', 'READS', 'WRITES',
    'CONSTRAINED_BY', 'OBSERVED_BY',
}


def analyze_graph_impact(query, graph, max_depth=2):
    """Traverse incoming and outgoing dependency edges from matching nodes."""
    q = query.strip().lower()
    nodes = {node['id']: node for node in graph.get('nodes', [])}
    seeds = [
        node['id'] for node in nodes.values()
        if q == node['id'].lower()
        or q == node.get('qualified_name', '').lower()
        or q == node.get('name', '').lower()
    ]
    if not seeds:
        return {'seeds': [], 'nodes': [], 'edges': []}

    visited = set(seeds)
    frontier = set(seeds)
    selected_edges = []
    for _ in range(max(0, max_depth)):
        next_frontier = set()
        for edge in graph.get('edges', []):
            if edge.get('relation') not in TRAVERSABLE_RELATIONS:
                continue
            if edge['source'] in frontier or edge['target'] in frontier:
                selected_edges.append(edge)
                other = edge['target'] if edge['source'] in frontier else edge['source']
                if other not in visited:
                    visited.add(other)
                    next_frontier.add(other)
        frontier = next_frontier
        if not frontier:
            break

    unique_edges = []
    seen_edges = set()
    for edge in selected_edges:
        key = (edge['source'], edge['target'], edge['relation'])
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(edge)
    return {
        'seeds': seeds,
        'nodes': [nodes[node_id] for node_id in visited if node_id in nodes],
        'edges': unique_edges,
    }


def build_change_plan(task, graph):
    """Compile a task-focused change plan and explainable risk score."""
    tokens = {token for token in re.findall(r'[A-Za-z0-9_/-]{3,}', task.lower())}
    candidates = []
    for node in graph.get('nodes', []):
        haystack = ' '.join(
            str(node.get(key, ''))
            for key in ('id', 'name', 'qualified_name', 'path', 'kind')
        ).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score:
            candidates.append((score, node))
    candidates.sort(key=lambda item: (-item[0], item[1]['id']))
    seeds = [node['id'] for _, node in candidates[:8]]
    selected_nodes = {node['id']: node for _, node in candidates[:8]}
    selected_edges = []
    for seed in seeds:
        impact = analyze_graph_impact(seed, graph, max_depth=2)
        selected_nodes.update({node['id']: node for node in impact['nodes']})
        selected_edges.extend(impact['edges'])

    unique_edges = {(e['source'], e['target'], e['relation']): e for e in selected_edges}
    reasons = []
    risk = 0
    if any(node.get('type') == 'api' for node in selected_nodes.values()):
        risk += 25
        reasons.append(('+25', 'public API or route'))
    constraints = [node for node in selected_nodes.values() if node.get('type') == 'constraint']
    if any(node.get('severity') == 'critical' for node in constraints):
        risk += 25
        reasons.append(('+25', 'critical constraint'))
    elif any(node.get('severity') == 'high' for node in constraints):
        risk += 15
        reasons.append(('+15', 'high constraint'))
    dependent_count = max(0, len(selected_nodes) - len(seeds))
    if dependent_count > 10:
        risk += 20
        reasons.append(('+20', f'{dependent_count} related nodes'))
    elif dependent_count > 3:
        risk += 10
        reasons.append(('+10', f'{dependent_count} related nodes'))
    if any(edge.get('confidence', 1) < 0.95 for edge in unique_edges.values()):
        risk += 10
        reasons.append(('+10', 'inferred dependency'))
    if any(
        node.get('staleness') in {'SUSPECT', 'STALE'}
        for node in selected_nodes.values()
    ):
        risk += 10
        reasons.append(('+10', 'stale or suspect evidence'))
    has_tests = any(edge.get('relation') == 'TESTED_BY' for edge in unique_edges.values())
    if seeds and not has_tests:
        risk += 15
        reasons.append(('+15', 'no linked tests'))
    risk = min(risk, 100)
    level = 'RED' if risk >= 60 else ('YELLOW' if risk >= 30 else 'GREEN')
    return {
        'task': task, 'risk_score': risk, 'risk_level': level,
        'reasons': reasons, 'seeds': seeds,
        'nodes': list(selected_nodes.values()), 'edges': list(unique_edges.values()),
    }


def compile_task_context(task, graph, budget=500):
    """Compile hierarchical, risk-weighted context within an approximate budget."""
    plan = build_change_plan(task, graph)
    node_by_id = {node['id']: node for node in plan['nodes']}
    lines = [
        'LCM TASK CONTEXT',
        f"Task: {task}",
        f"Risk: {plan['risk_level']} ({plan['risk_score']})",
    ]
    if plan['reasons']:
        lines.append('Risk reasons: ' + ', '.join(f"{p} {r}" for p, r in plan['reasons']))
    hierarchy = {}
    for node in plan['nodes']:
        path = node.get('path', '')
        parts = [part for part in path.split('/') if part]
        component = parts[0] if len(parts) > 1 else 'root'
        module = '/'.join(parts[:-1]) if len(parts) > 1 else (
            parts[0] if parts else 'declared-knowledge'
        )
        hierarchy.setdefault(component, set()).add(module)
    if hierarchy:
        lines.append('Architecture scope:')
        for component in sorted(hierarchy):
            lines.append(f"- {component}: {', '.join(sorted(hierarchy[component]))}")
    lines.append('Relevant nodes:')
    type_priority = {'constraint': 0, 'observation': 1, 'api': 2, 'symbol': 3}
    for node in sorted(
        plan['nodes'],
        key=lambda item: (type_priority.get(item.get('type'), 4), item['id']),
    ):
        detail = node.get('path') or node.get('rule') or node.get('result') or ''
        evidence_state = (
            f"{node.get('knowledge_type', 'UNKNOWN')}/"
            f"{node.get('staleness', 'UNKNOWN')}"
        )
        lines.append(
            f"- [{node.get('type', 'node')} {evidence_state}] "
            f"{node['id']} {detail}".rstrip()
        )
    if plan['edges']:
        lines.append('Relationships:')
        for edge in plan['edges']:
            source = node_by_id.get(edge['source'], {}).get('name', edge['source'])
            target = node_by_id.get(edge['target'], {}).get('name', edge['target'])
            evidence = edge.get('evidence', {})
            evidence_ref = evidence.get('path', '?')
            if evidence.get('line'):
                evidence_ref += f":{evidence['line']}"
            lines.append(
                f"- {source} --{edge['relation']}--> {target} "
                f"({edge['confidence']:.2f}, "
                f"{edge.get('knowledge_type', 'UNKNOWN')}, {evidence_ref})"
            )

    max_chars = max(200, int(budget) * 4)
    selected = []
    used = 0
    for line in lines:
        cost = len(line) + 1
        if selected and used + cost > max_chars:
            break
        selected.append(line[:max_chars] if not selected else line)
        used += min(cost, max_chars)
    omitted = len(lines) - len(selected)
    if omitted and used + 40 <= max_chars:
        selected.append(f"... {omitted} context lines omitted by budget")
    text = '\n'.join(selected)
    return {
        'text': text,
        'estimated_tokens': (len(text) + 3) // 4,
        'omitted_lines': omitted,
        'plan': plan,
    }

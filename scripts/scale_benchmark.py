#!/usr/bin/env python3
"""Measure cold, partial, and warm LCM indexing and graph construction."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import tempfile
import tracemalloc

try:
    from . import living_map
    from .lcm_core.engine import RepositoryEngine
except ImportError:
    import living_map
    from lcm_core.engine import RepositoryEngine


SCHEMA_VERSION = 1


def _git(root, arguments):
    result = subprocess.run(
        ['git', '-C', root] + arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ''


def _tool_hash():
    root = os.path.dirname(os.path.abspath(__file__))
    paths = [os.path.join(root, 'living_map.py')]
    core = os.path.join(root, 'lcm_core')
    paths.extend(
        os.path.join(core, name)
        for name in sorted(os.listdir(core))
        if name.endswith('.py')
    )
    hasher = hashlib.sha256()
    for path in paths:
        hasher.update(os.path.basename(path).encode('utf-8'))
        with open(path, 'rb') as handle:
            hasher.update(handle.read())
    return hasher.hexdigest()


def measure_repository(root, repository_url=None, repetitions=2):
    root = os.path.abspath(root)
    if repetitions < 2:
        raise ValueError('repetitions must be at least 2 to measure warm reuse')
    measurements = []
    with tempfile.TemporaryDirectory() as state:
        index_cache = os.path.join(state, 'index-cache.json')
        graph_cache = os.path.join(state, 'graph-cache.json')
        engine = RepositoryEngine(
            living_map.build_symbol_index_incremental,
            living_map.build_dependency_graph,
        )
        for iteration in range(repetitions):
            tracemalloc.start()
            result = engine.build(root, index_cache, graph_cache)
            total_seconds = result.index_seconds + result.graph_seconds
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            measurements.append({
                'iteration': iteration + 1,
                'index_seconds': round(result.index_seconds, 6),
                'graph_seconds': round(result.graph_seconds, 6),
                'total_seconds': round(total_seconds, 6),
                'peak_bytes': peak_bytes,
                'index_stats': result.index_stats,
                'graph_stats': result.graph_stats,
                'files': len(result.index.get('files', [])),
                'symbols': len(result.index.get('symbols', [])),
                'edges': len(result.graph.get('edges', [])),
            })
    cold = measurements[0]
    warm = measurements[-1]
    return {
        'schema_version': SCHEMA_VERSION,
        'repository': repository_url or _git(root, ['config', '--get', 'remote.origin.url']) or os.path.basename(root),
        'repository_commit': _git(root, ['rev-parse', 'HEAD']) or 'unversioned',
        'repository_dirty': bool(_git(root, ['status', '--porcelain'])),
        'tool_source_sha256': _tool_hash(),
        'python': platform.python_version(),
        'platform': platform.platform(),
        'measurements': measurements,
        'summary': {
            'cold_seconds': cold['total_seconds'],
            'warm_seconds': warm['total_seconds'],
            'warm_speedup': round(
                cold['total_seconds'] / warm['total_seconds'], 3
            ) if warm['total_seconds'] else None,
            'warm_graph_mode': warm['graph_stats']['mode'],
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', action='append', required=True, help='Repository path; repeatable')
    parser.add_argument('--repository-url', action='append', help='Public identity matching each repository')
    parser.add_argument('--repetitions', type=int, default=2)
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    urls = args.repository_url or []
    if urls and len(urls) != len(args.repository):
        parser.error('--repository-url count must match --repository count')
    try:
        results = [
            measure_repository(path, urls[index] if urls else None, args.repetitions)
            for index, path in enumerate(args.repository)
        ]
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    payload = {'schema_version': SCHEMA_VERSION, 'repositories': results}
    rendered = json.dumps(payload, indent=2, sort_keys=True) + '\n'
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as handle:
            handle.write(rendered)
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

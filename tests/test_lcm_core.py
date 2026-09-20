import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts import living_map
from scripts.lcm_core.calm_adapter import export_calm, reconcile_calm
from scripts.lcm_core.evidence import make_provenance, validate_provenance
from scripts.lcm_core.graph_cache import build_incremental_graph
from scripts.lcm_core.observations import (
    apply_observations,
    file_sha256,
    load_observations,
    observation_summary,
    repository_evidence_path,
    validate_observations,
    write_observations,
)
from scripts.lcm_core.schema import migrate_constraints
from scripts.lcm_core.semantics import validate_markdown_semantics


class LcmCoreTests(unittest.TestCase):
    def _write(self, root, relative, content):
        path = os.path.join(root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(content)
        return path

    def test_constraint_v1_migration_adds_evidence_contract(self):
        migrated = migrate_constraints({
            'schema_version': 1,
            'constraints': [{
                'id': 'C1', 'rule': 'Keep it safe', 'status': 'ACTIVE',
                'severity': 'high', 'scope': [],
            }],
        })
        self.assertEqual(migrated['schema_version'], 2)
        self.assertEqual(migrated['constraints'][0]['knowledge_type'], 'DECLARED')
        self.assertEqual(migrated['constraints'][0]['staleness'], 'FRESH')

    def test_semantic_lint_detects_projection_drift(self):
        content = (
            '## MODULE 4: ARCHITECTURAL CONSTRAINTS & INVARIANTS\n'
            '- [C001] Keep it safe\n\n'
            '## MODULE 5: FEATURE TRACEABILITY MATRIX\n'
            '| Feature ID | Description |\n|---|---|\n| F001 | Mapping |\n'
        )
        payload = {'schema_version': 2, 'constraints': []}
        issues = validate_markdown_semantics(content, payload, content)
        self.assertIn('Markdown constraints missing structured records: C001', issues)

    def test_semantic_lint_detects_compact_projection_loss(self):
        content = (
            '## MODULE 4: ARCHITECTURAL CONSTRAINTS & INVARIANTS\n'
            '- [C001] Keep it safe\n\n'
            '## MODULE 5: FEATURE TRACEABILITY MATRIX\n'
            '| Feature ID | Description |\n|---|---|\n| F001 | Mapping |\n'
        )
        compact = '## MODULE 4: ARCHITECTURAL CONSTRAINTS & INVARIANTS\n- [C001] Keep it safe\n'
        payload = {'schema_version': 2, 'constraints': [{'id': 'C001'}]}
        issues = validate_markdown_semantics(content, payload, compact)
        self.assertIn('compact map does not preserve all feature records', issues)

    def test_symbol_index_records_deterministic_provenance(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/app.py', 'def run():\n    return True\n')
            index = living_map.build_symbol_index(root)
        symbol = index['symbols'][0]
        self.assertEqual(symbol['knowledge_type'], 'FACT')
        self.assertEqual(symbol['staleness'], 'FRESH')
        self.assertEqual(symbol['source']['path'], 'src/app.py')
        self.assertEqual(validate_provenance(symbol), [])

    def test_incremental_index_reuses_unchanged_files(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return True\n')
            cache = os.path.join(root, '.lcm', 'cache.json')
            first, first_stats = living_map.build_symbol_index_incremental(root, cache)
            second, second_stats = living_map.build_symbol_index_incremental(root, cache)
        self.assertEqual(first, second)
        self.assertEqual(first_stats['scanned'], 1)
        self.assertEqual(second_stats['reused'], 1)

    def test_legacy_line_lookup_is_derived_from_incremental_index(self):
        index = {
            'symbols': [
                {'path': 'src/one.py', 'name': 'run', 'line': 2},
                {'path': 'src/two.py', 'name': 'run', 'line': 8},
                {'path': 'src/two.py', 'name': 'save', 'line': 10},
            ]
        }
        file_map, lookup = living_map.build_symbol_database_from_index(index)
        self.assertEqual(file_map['src/two.py']['save'], 10)
        self.assertNotIn('run', lookup)
        self.assertEqual(lookup['save'], ('src/two.py', 10))

    def test_context_exposes_architecture_scope_and_evidence_state(self):
        graph = {
            'nodes': [{
                'id': 'py:services/payments.py::charge',
                'type': 'symbol',
                'name': 'charge',
                'qualified_name': 'charge',
                'path': 'services/payments.py',
                'knowledge_type': 'FACT',
                'staleness': 'FRESH',
            }],
            'edges': [],
        }
        context = living_map.compile_task_context('change payment charge', graph, budget=200)
        self.assertIn('Architecture scope:', context['text'])
        self.assertIn('- services: services', context['text'])
        self.assertIn('[symbol FACT/FRESH]', context['text'])

    def test_observation_freshness_follows_source_hash(self):
        with tempfile.TemporaryDirectory() as root:
            evidence_path = self._write(root, 'reports/test.json', '{"passed": true}\n')
            symbol_id = 'py:app.py::run'
            index = {'symbols': [{'id': symbol_id}]}
            payload = {
                'schema_version': 1,
                'observations': [{
                    'id': 'O1', 'symbol': symbol_id, 'kind': 'test', 'result': 'pass',
                    'source': {'path': 'reports/test.json'},
                    'source_hash': file_sha256(evidence_path),
                }],
            }
            graph = {'nodes': [{'id': symbol_id, 'type': 'symbol'}], 'edges': []}
            self.assertEqual(validate_observations(payload, index, root), [])
            fresh = apply_observations(graph, payload, root)
            self.assertEqual(observation_summary(fresh)['staleness']['FRESH'], 1)
            self._write(root, 'reports/test.json', '{"passed": false}\n')
            suspect = apply_observations(graph, payload, root)
            self.assertEqual(observation_summary(suspect)['staleness']['SUSPECT'], 1)

    def test_observation_storage_round_trip(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, '.lcm', 'observations.json')
            payload = {'schema_version': 1, 'observations': []}
            write_observations(payload, path)
            self.assertEqual(load_observations(path), payload)

    def test_observation_source_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertIsNone(repository_evidence_path(root, '../outside.json'))
            self.assertEqual(
                repository_evidence_path(root, 'reports/test.json'),
                os.path.join(root, 'reports', 'test.json'),
            )
            payload = {
                'schema_version': 1,
                'observations': [{
                    'id': 'O1', 'symbol': 'py:app.py::run', 'kind': 'test',
                    'result': 'pass', 'source': {'path': '../outside.json'},
                    'source_hash': 'a' * 64,
                }],
            }
            issues = validate_observations(
                payload, {'symbols': [{'id': 'py:app.py::run'}]}, root,
            )
        self.assertTrue(any('must stay inside' in issue for issue in issues))

    def test_update_orchestrates_modular_engine_in_dry_run(self):
        with tempfile.TemporaryDirectory() as root:
            map_path = self._write(
                root, 'PROJECT_MAP.md',
                '# LIVING PROJECT MAP: fixture\nCodebase-MD5: ' + '0' * 32 + '\n',
            )
            constraint_path = self._write(
                root, '.lcm/constraints.json',
                json.dumps({'schema_version': 2, 'constraints': []}),
            )
            observation_path = self._write(
                root, '.lcm/observations.json',
                json.dumps({'schema_version': 1, 'observations': []}),
            )
            self._write(root, 'app.py', 'def run():\n    return True\n')
            replacements = {
                'ROOT': root,
                'MAP_PATH': map_path,
                'MIN_MAP_PATH': os.path.join(root, 'PROJECT_MAP.min.md'),
                'INDEX_PATH': os.path.join(root, '.lcm', 'index.json'),
                'GRAPH_PATH': os.path.join(root, '.lcm', 'graph.json'),
                'CONSTRAINT_PATH': constraint_path,
                'FITNESS_PATH': os.path.join(root, '.lcm', 'fitness.json'),
                'CACHE_PATH': os.path.join(root, '.lcm', 'cache.json'),
                'GRAPH_CACHE_PATH': os.path.join(root, '.lcm', 'graph-cache.json'),
                'OBSERVATION_PATH': observation_path,
            }
            with mock.patch.multiple(living_map, **replacements):
                result = living_map.cmd_update(
                    SimpleNamespace(dry_run=True, auto_commit=False)
                )
        self.assertEqual(result, 0)

    def test_incremental_graph_reuses_and_partially_rebuilds_safely(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return True\n')
            index_cache = os.path.join(root, '.lcm', 'index-cache.json')
            graph_cache = os.path.join(root, '.lcm', 'graph-cache.json')
            first_index, first_stats = living_map.build_symbol_index_incremental(root, index_cache)
            first_graph, graph_stats = build_incremental_graph(
                first_index, root, graph_cache, first_stats, living_map.build_dependency_graph,
            )
            self.assertEqual(graph_stats['mode'], 'full')
            second_index, second_stats = living_map.build_symbol_index_incremental(root, index_cache)
            second_graph, graph_stats = build_incremental_graph(
                second_index, root, graph_cache, second_stats, living_map.build_dependency_graph,
            )
            self.assertEqual(graph_stats['mode'], 'reused')
            self.assertEqual(first_graph, second_graph)
            self._write(root, 'app.py', 'def run():\n    value = 1\n    return value\n')
            third_index, third_stats = living_map.build_symbol_index_incremental(root, index_cache)
            partial_graph, graph_stats = build_incremental_graph(
                third_index, root, graph_cache, third_stats, living_map.build_dependency_graph,
            )
            self.assertEqual(graph_stats['mode'], 'partial')
            self.assertEqual(partial_graph, living_map.build_dependency_graph(third_index, root))
            self._write(root, 'pyproject.toml', '[project]\nname = "changed-environment"\n')
            fourth_index, fourth_stats = living_map.build_symbol_index_incremental(root, index_cache)
            _, graph_stats = build_incremental_graph(
                fourth_index, root, graph_cache, fourth_stats, living_map.build_dependency_graph,
            )
            self.assertEqual(graph_stats['mode'], 'full')
            self.assertEqual(graph_stats['reason'], 'cold-or-environment-change')

    def test_incremental_graph_invalidates_changed_resolution_signature(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return True\n')
            index_cache = os.path.join(root, '.lcm', 'index-cache.json')
            graph_cache = os.path.join(root, '.lcm', 'graph-cache.json')
            index, stats = living_map.build_symbol_index_incremental(root, index_cache)
            build_incremental_graph(
                index, root, graph_cache, stats, living_map.build_dependency_graph,
            )
            changed_index = json.loads(json.dumps(index))
            changed_index['symbols'][0]['kind'] = 'class'
            _, graph_stats = build_incremental_graph(
                changed_index,
                root,
                graph_cache,
                {'changed_paths': [], 'removed_paths': []},
                living_map.build_dependency_graph,
            )
            self.assertEqual(graph_stats['mode'], 'full')
            self.assertEqual(graph_stats['reason'], 'resolution-signature-change')

    def test_calm_projection_and_reconciliation_are_optional(self):
        index = {
            'files': [
                {'path': 'api/app.py'},
                {'path': 'worker/jobs.py'},
            ]
        }
        graph = {
            'nodes': [
                {'id': 'a', 'type': 'symbol', 'path': 'api/app.py'},
                {'id': 'b', 'type': 'symbol', 'path': 'worker/jobs.py'},
            ],
            'edges': [{'source': 'a', 'target': 'b'}],
        }
        observed = export_calm(index, graph, 'Demo')
        self.assertEqual(observed['$schema'], 'https://calm.finos.org/release/1.2/meta/calm.json')
        self.assertEqual({node['unique-id'] for node in observed['nodes']}, {'api', 'worker'})
        self.assertTrue(reconcile_calm(observed, observed)['in_sync'])
        declared = json.loads(json.dumps(observed))
        declared['nodes'].append({'unique-id': 'database', 'node-type': 'database', 'name': 'DB'})
        report = reconcile_calm(declared, observed)
        self.assertEqual(report['declared_not_observed'], ['database'])
        self.assertFalse(report['in_sync'])


if __name__ == '__main__':
    unittest.main()

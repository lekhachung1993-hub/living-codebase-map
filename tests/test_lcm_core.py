import json
import os
import tempfile
import unittest

from scripts import living_map
from scripts.lcm_core.calm_adapter import export_calm, reconcile_calm
from scripts.lcm_core.evidence import make_provenance, validate_provenance
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

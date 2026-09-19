import json
import os
import tempfile
import unittest

from scripts import living_map


class StableSymbolIndexTests(unittest.TestCase):
    def _write(self, root, relative_path, content):
        path = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(content)
        return path

    def test_python_ids_are_qualified_and_line_independent(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root,
                'src/services.py',
                'class UserService:\n    def save(self, user):\n        return user\n',
            )
            first = living_map.scan_file_symbol_records(path, 'src/services.py')

            self._write(
                root,
                'src/services.py',
                '\n\nclass UserService:\n    def save(self, user):\n        return user\n',
            )
            second = living_map.scan_file_symbol_records(path, 'src/services.py')

            first_by_name = {record['qualified_name']: record for record in first}
            second_by_name = {record['qualified_name']: record for record in second}
            symbol = 'UserService.save'
            self.assertEqual(first_by_name[symbol]['id'], second_by_name[symbol]['id'])
            self.assertEqual(first_by_name[symbol]['fingerprint'], second_by_name[symbol]['fingerprint'])
            self.assertNotEqual(first_by_name[symbol]['line'], second_by_name[symbol]['line'])
            self.assertEqual(
                first_by_name[symbol]['id'],
                'py:src/services.py::UserService.save',
            )

    def test_same_method_name_in_two_classes_has_distinct_ids(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root,
                'models.py',
                'class User:\n    def save(self):\n        pass\n\n'
                'class Order:\n    def save(self):\n        pass\n',
            )
            records = living_map.scan_file_symbol_records(path, 'models.py')
            save_ids = {r['id'] for r in records if r['name'] == 'save'}
            self.assertEqual(
                save_ids,
                {'py:models.py::User.save', 'py:models.py::Order.save'},
            )

    def test_ambiguous_bare_symbol_is_not_resolved_arbitrarily(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a/service.py', 'def save():\n    pass\n')
            self._write(root, 'b/service.py', 'def save():\n    pass\n')

            _, lookup = living_map.build_symbol_database(root)

            self.assertNotIn('save', lookup)
            self.assertNotIn(('service.py', 'save'), lookup)
            self.assertEqual(lookup[('a/service.py', 'save')], ('a/service.py', 1))
            self.assertEqual(lookup[('b/service.py', 'save')], ('b/service.py', 1))

    def test_map_uses_full_path_to_resolve_duplicate_symbol(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a/service.py', '\n\ndef save():\n    pass\n')
            self._write(root, 'b/service.py', '\n\n\n\ndef save():\n    pass\n')
            _, lookup = living_map.build_symbol_database(root)
            content = (
                '### a/service.py\n| Line | Symbol | Description |\n'
                '|---|---|---|\n| L1 | `save` | A |\n\n'
                '### b/service.py\n| Line | Symbol | Description |\n'
                '|---|---|---|\n| L1 | `save` | B |'
            )

            updated, count, _ = living_map.update_map_line_numbers(content, lookup)

            self.assertEqual(count, 2)
            self.assertIn('| L3 | `save` | A |', updated)
            self.assertIn('| L5 | `save` | B |', updated)

    def test_index_can_be_persisted_as_schema_v3_json(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return True\n')
            index = living_map.build_symbol_index(root)
            output = os.path.join(root, '.lcm', 'index.json')
            living_map.write_symbol_index(index, output)

            with open(output, 'r', encoding='utf-8') as handle:
                saved = json.load(handle)
            self.assertEqual(saved['schema_version'], 3)
            self.assertEqual(saved['symbols'][0]['id'], 'py:app.py::run')

    def test_graph_extracts_python_calls_with_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'service.py',
                'def validate():\n    return True\n\n'
                'def create():\n    return validate()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)

            self.assertEqual(graph['schema_version'], 1)
            self.assertEqual(len(graph['edges']), 1)
            edge = graph['edges'][0]
            self.assertEqual(edge['source'], 'py:service.py::create')
            self.assertEqual(edge['target'], 'py:service.py::validate')
            self.assertEqual(edge['relation'], 'CALLS')
            self.assertEqual(edge['confidence'], 1.0)
            self.assertEqual(edge['evidence']['path'], 'service.py')
            self.assertEqual(edge['evidence']['line'], 5)

    def test_graph_resolves_self_method_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'service.py',
                'class Service:\n'
                '    def validate(self):\n        return True\n\n'
                '    def create(self):\n        return self.validate()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = graph['edges'][0]
            self.assertEqual(edge['source'], 'py:service.py::Service.create')
            self.assertEqual(edge['target'], 'py:service.py::Service.validate')
            self.assertEqual(edge['confidence'], 1.0)

    def test_graph_creates_api_node_from_python_route_decorator(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'api.py',
                '@router.post("/customers")\n'
                'def create_customer():\n    return True\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            api_node = next(node for node in graph['nodes'] if node['type'] == 'api')
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'HANDLES')
            self.assertEqual(api_node['id'], 'api:POST /customers')
            self.assertEqual(edge['source'], 'api:POST /customers')
            self.assertEqual(edge['target'], 'py:api.py::create_customer')
            self.assertEqual(edge['confidence'], 1.0)

    def test_graph_does_not_guess_ambiguous_call_target(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a.py', 'def save():\n    pass\n')
            self._write(root, 'b.py', 'def save():\n    pass\n')
            self._write(root, 'caller.py', 'def run():\n    save()\n')
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            self.assertEqual(graph['edges'], [])

    def test_graph_impact_traverses_incoming_and_outgoing_edges(self):
        graph = {
            'nodes': [
                {'id': 'py:a.py::first', 'name': 'first', 'qualified_name': 'first'},
                {'id': 'py:a.py::middle', 'name': 'middle', 'qualified_name': 'middle'},
                {'id': 'py:a.py::last', 'name': 'last', 'qualified_name': 'last'},
            ],
            'edges': [
                {'source': 'py:a.py::first', 'target': 'py:a.py::middle', 'relation': 'CALLS'},
                {'source': 'py:a.py::middle', 'target': 'py:a.py::last', 'relation': 'CALLS'},
            ],
        }
        result = living_map.analyze_graph_impact('middle', graph, max_depth=1)
        self.assertEqual(set(result['seeds']), {'py:a.py::middle'})
        self.assertEqual(len(result['edges']), 2)
        self.assertEqual(len(result['nodes']), 3)

    def test_machine_state_is_deterministic(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return True\n')
            first_index = living_map.build_symbol_index(root)
            first_graph = living_map.build_dependency_graph(first_index, root)
            second_index = living_map.build_symbol_index(root)
            second_graph = living_map.build_dependency_graph(second_index, root)
            self.assertEqual(first_index, second_index)
            self.assertEqual(first_graph, second_graph)

    def test_machine_state_validation_detects_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return True\n')
            issues, _, _ = living_map.validate_machine_state(
                root,
                os.path.join(root, '.lcm', 'index.json'),
                os.path.join(root, '.lcm', 'graph.json'),
            )
            self.assertIn('missing .lcm/index.json', issues)
            self.assertIn('missing .lcm/graph.json', issues)

    def test_machine_state_validation_detects_tampered_graph(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'app.py',
                'def helper():\n    return True\n\n'
                'def run():\n    return helper()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            index_path = os.path.join(root, '.lcm', 'index.json')
            graph_path = os.path.join(root, '.lcm', 'graph.json')
            living_map.write_symbol_index(index, index_path)
            graph['edges'][0]['confidence'] = 7
            living_map.write_dependency_graph(graph, graph_path)

            issues, _, _ = living_map.validate_machine_state(root, index_path, graph_path)
            self.assertIn('graph edge 0 has invalid confidence', issues)
            self.assertIn('graph content differs from a fresh deterministic scan', issues)

    def test_constraint_validation_rejects_active_missing_symbol(self):
        index = {'symbols': [{'id': 'py:app.py::run'}]}
        payload = {
            'schema_version': 1,
            'constraints': [{
                'id': 'C1', 'rule': 'Run must be idempotent', 'status': 'ACTIVE',
                'severity': 'high', 'scope': ['py:app.py::missing'],
            }],
        }
        issues = living_map.validate_constraints(payload, index)
        self.assertIn('C1: ACTIVE scope references missing symbols: py:app.py::missing', issues)

    def test_stale_constraint_may_retain_missing_symbol_history(self):
        payload = {
            'schema_version': 1,
            'constraints': [{
                'id': 'C1', 'rule': 'Legacy rule', 'status': 'STALE',
                'severity': 'low', 'scope': ['py:deleted.py::old'],
            }],
        }
        self.assertEqual(living_map.validate_constraints(payload, {'symbols': []}), [])

    def test_constraints_become_graph_nodes_and_edges(self):
        graph = {
            'schema_version': 1,
            'source_hash': 'abc',
            'nodes': [{'id': 'py:app.py::run', 'type': 'symbol'}],
            'edges': [],
        }
        payload = {
            'schema_version': 1,
            'constraints': [{
                'id': 'C7', 'rule': 'Run is idempotent', 'status': 'ACTIVE',
                'severity': 'critical', 'scope': ['py:app.py::run'],
            }],
        }
        result = living_map.apply_constraints_to_graph(graph, payload)
        self.assertEqual(result['nodes'][-1]['id'], 'constraint:C7')
        self.assertEqual(result['edges'][0]['relation'], 'CONSTRAINED_BY')
        self.assertEqual(result['edges'][0]['confidence'], 1.0)

    def test_change_plan_produces_explainable_risk(self):
        graph = {
            'nodes': [
                {'id': 'api:POST /orders', 'type': 'api', 'name': 'POST /orders', 'path': 'api.py'},
                {'id': 'py:service.py::create_order', 'type': 'symbol', 'name': 'create_order', 'qualified_name': 'create_order', 'path': 'service.py'},
                {'id': 'constraint:C1', 'type': 'constraint', 'name': 'C1', 'severity': 'critical'},
            ],
            'edges': [
                {'source': 'api:POST /orders', 'target': 'py:service.py::create_order', 'relation': 'HANDLES', 'confidence': 1.0},
                {'source': 'py:service.py::create_order', 'target': 'constraint:C1', 'relation': 'CONSTRAINED_BY', 'confidence': 1.0},
            ],
        }
        plan = living_map.build_change_plan('change create order API', graph)
        self.assertEqual(plan['risk_level'], 'RED')
        self.assertGreaterEqual(plan['risk_score'], 60)
        self.assertIn(('+25', 'public API or route'), plan['reasons'])
        self.assertIn(('+25', 'critical constraint'), plan['reasons'])

    def test_verify_change_reports_linked_test_not_changed(self):
        graph = {
            'nodes': [
                {'id': 'py:service.py::create', 'type': 'symbol', 'path': 'service.py'},
                {'id': 'py:tests/test_service.py::test_create', 'type': 'symbol', 'path': 'tests/test_service.py'},
            ],
            'edges': [{
                'source': 'py:service.py::create',
                'target': 'py:tests/test_service.py::test_create',
                'relation': 'TESTED_BY', 'confidence': 1.0,
            }],
        }
        report = living_map.verify_changed_files(['service.py'], graph)
        self.assertEqual(report['missing_tests'], ['tests/test_service.py'])

    def test_explain_requires_unambiguous_symbol(self):
        graph = {'nodes': [
            {'id': 'py:a.py::save', 'name': 'save', 'qualified_name': 'save'},
            {'id': 'py:b.py::save', 'name': 'save', 'qualified_name': 'save'},
        ], 'edges': []}
        ambiguous = living_map.explain_graph_symbol('save', graph)
        exact = living_map.explain_graph_symbol('py:a.py::save', graph)
        self.assertIsNone(ambiguous['match'])
        self.assertEqual(len(ambiguous['candidates']), 2)
        self.assertEqual(exact['match']['id'], 'py:a.py::save')

    def test_context_compiler_respects_budget(self):
        graph = {
            'nodes': [
                {'id': 'py:service.py::create_order', 'type': 'symbol', 'name': 'create_order', 'qualified_name': 'create_order', 'path': 'service.py'},
                {'id': 'py:tests/test_service.py::test_create_order', 'type': 'symbol', 'name': 'test_create_order', 'qualified_name': 'test_create_order', 'path': 'tests/test_service.py'},
            ],
            'edges': [{
                'source': 'py:service.py::create_order',
                'target': 'py:tests/test_service.py::test_create_order',
                'relation': 'TESTED_BY', 'confidence': 1.0,
            }],
        }
        result = living_map.compile_task_context('change create order', graph, budget=80)
        self.assertLessEqual(result['estimated_tokens'], 80)
        self.assertIn('Risk:', result['text'])
        self.assertTrue(result['plan']['seeds'])

    def test_parse_symbol_git_history(self):
        raw = (
            'a' * 40 + '\x1faaaaaaa\x1f2026-01-02\x1fFix retry race\x1e'
            + 'b' * 40 + '\x1fbbbbbbb\x1f2025-12-01\x1fAdd worker\x1e'
        )
        entries = living_map.parse_symbol_git_history(raw)
        self.assertEqual(entries[0]['short'], 'aaaaaaa')
        self.assertEqual(entries[0]['subject'], 'Fix retry race')
        self.assertEqual(entries[1]['date'], '2025-12-01')


if __name__ == '__main__':
    unittest.main()

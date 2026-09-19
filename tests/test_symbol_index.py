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


if __name__ == '__main__':
    unittest.main()

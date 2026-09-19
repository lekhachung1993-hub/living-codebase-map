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


if __name__ == '__main__':
    unittest.main()

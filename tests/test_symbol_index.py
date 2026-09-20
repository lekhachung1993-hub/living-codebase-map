import json
import os
import re
import sys
import tempfile
import types
import unittest
from unittest import mock

from scripts import living_map


class StableSymbolIndexTests(unittest.TestCase):
    def _write(self, root, relative_path, content):
        path = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(content)
        return path

    def test_release_versions_stay_in_sync(self):
        root = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(root, 'manifest.json'), 'r', encoding='utf-8') as handle:
            manifest_version = json.load(handle)['version']
        with open(os.path.join(root, 'pyproject.toml'), 'r', encoding='utf-8') as handle:
            pyproject_version = re.search(r'^version = "([^"]+)"', handle.read(), re.MULTILINE).group(1)
        with open(os.path.join(root, 'PROJECT_MAP.md'), 'r', encoding='utf-8') as handle:
            map_version = re.search(r'v(\d+\.\d+\.\d+)', handle.readline()).group(1)
        self.assertEqual({manifest_version, pyproject_version, map_version}, {'3.23.0'})

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

    def test_map_refreshes_documented_function_call_syntax(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'service.py', '\n\ndef save():\n    pass\n')
            _, lookup = living_map.build_symbol_database(root)
            content = (
                '### service.py\n| Line | Symbol | Description |\n'
                '|---|---|---|\n| L1 | `save()` | Save data |'
            )

            updated, count, _ = living_map.update_map_line_numbers(content, lookup)

            self.assertEqual(count, 1)
            self.assertIn('| L3 | `save()` | Save data |', updated)

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

    def test_graph_does_not_resolve_unknown_object_method_by_name_only(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'adapter.py',
                'class Adapter:\n    def send(self):\n        return True\n',
            )
            self._write(
                root,
                'service.py',
                'def run(client):\n    return client.send()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            self.assertEqual(graph['edges'], [])

    def test_python_import_alias_disambiguates_duplicate_names(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a.py', 'def save():\n    return "a"\n')
            self._write(root, 'b.py', 'def save():\n    return "b"\n')
            self._write(
                root,
                'caller.py',
                'from a import save as persist\n\ndef run():\n    return persist()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')

            self.assertEqual(edge['source'], 'py:caller.py::run')
            self.assertEqual(edge['target'], 'py:a.py::save')
            self.assertEqual(edge['confidence'], 1.0)
            self.assertEqual(edge['evidence']['source'], 'python_import')

    def test_python_module_alias_resolves_member_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'services/orders.py', 'def save():\n    return True\n')
            self._write(
                root,
                'caller.py',
                'import services.orders as orders\n\ndef run():\n    return orders.save()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')

            self.assertEqual(edge['target'], 'py:services/orders.py::save')
            self.assertEqual(edge['evidence']['source'], 'python_import')

    def test_python_relative_import_resolves_symbol(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'pkg/service.py', 'def save():\n    return True\n')
            self._write(
                root,
                'pkg/caller.py',
                'from .service import save\n\ndef run():\n    return save()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'py:pkg/service.py::save')

    def test_python_module_resolution_preserves_ambiguity(self):
        known = {'pkg.py', 'pkg/__init__.py'}
        self.assertIsNone(
            living_map._resolve_python_module_path('caller.py', 'pkg', 0, known)
        )

    def test_python_absolute_import_resolves_unique_src_layout(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/pkg/service.py', 'def save():\n    return True\n')
            self._write(
                root,
                'caller.py',
                'from pkg.service import save\n\ndef run():\n    return save()\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'py:src/pkg/service.py::save')

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

    def test_go_receiver_methods_have_qualified_stable_ids(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root,
                'service.go',
                'package service\n\ntype User struct{}\ntype Order struct{}\n\n'
                'func (u *User) Save() {}\nfunc (o *Order) Save() {}\n',
            )
            records = living_map.scan_file_symbol_records(path, 'service.go')
            save_ids = {record['id'] for record in records if record['name'] == 'Save'}
            self.assertEqual(save_ids, {
                'go:service.go::User.Save',
                'go:service.go::Order.Save',
            })

    def test_go_graph_extracts_same_package_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'validate.go', 'package service\n\nfunc Validate() bool { return true }\n')
            self._write(
                root,
                'service.go',
                'package service\n\nfunc Create() bool {\n  return Validate()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'go:service.go::Create')
            self.assertEqual(edge['target'], 'go:validate.go::Validate')
            self.assertEqual(edge['evidence']['source'], 'go_static')

    def test_go_graph_resolves_receiver_method_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'service.go',
                'package service\n\ntype Service struct{}\n\n'
                'func (s *Service) Validate() bool { return true }\n\n'
                'func (s *Service) Create() bool {\n  return s.Validate()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'go:service.go::Service.Create')
            self.assertEqual(edge['target'], 'go:service.go::Service.Validate')

    def test_go_test_call_becomes_tested_by_edge(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'service.go', 'package service\n\nfunc Create() bool { return true }\n')
            self._write(
                root,
                'service_test.go',
                'package service\n\nfunc TestCreate() {\n  Create()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'TESTED_BY')
            self.assertEqual(edge['source'], 'go:service.go::Create')
            self.assertEqual(edge['target'], 'go:service_test.go::TestCreate')

    def test_go_graph_extracts_http_and_framework_routes(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'api.go',
                'package api\n\nfunc ListOrders() {}\nfunc CreateOrder() {}\n\n'
                '// router.DELETE("/orders", CreateOrder)\n'
                'func Routes() {\n'
                '  http.HandleFunc("/health", ListOrders)\n'
                '  router.POST("/orders", CreateOrder)\n'
                '}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            handles = [edge for edge in graph['edges'] if edge['relation'] == 'HANDLES']
            self.assertEqual({edge['source'] for edge in handles}, {
                'api:ANY /health', 'api:POST /orders',
            })
            self.assertTrue(all(edge['evidence']['source'] == 'go_static' for edge in handles))

    def test_go_import_alias_resolves_cross_package_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'go.mod', 'module example.com/shop\n')
            self._write(
                root, 'pkg/orders/orders.go',
                'package orders\n\nfunc Save() bool { return true }\n',
            )
            self._write(
                root, 'cmd/main.go',
                'package main\n\nimport orderSvc "example.com/shop/pkg/orders"\n\n'
                'func Run() bool {\n  return orderSvc.Save()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'go:cmd/main.go::Run')
            self.assertEqual(edge['target'], 'go:pkg/orders/orders.go::Save')
            self.assertEqual(edge['confidence'], 1.0)
            self.assertEqual(edge['evidence']['source'], 'go_import')

    def test_go_grouped_default_import_resolves_route_handler(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'go.mod', 'module example.com/shop\n\ngo 1.22\n')
            self._write(
                root, 'pkg/orders/http.go',
                'package orders\n\nfunc List() {}\n',
            )
            self._write(
                root, 'cmd/main.go',
                'package main\n\nimport (\n  "example.com/shop/pkg/orders"\n  "fmt"\n)\n\n'
                'func Routes() {\n  router.GET("/orders", orders.List)\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'HANDLES')
            self.assertEqual(edge['source'], 'api:GET /orders')
            self.assertEqual(edge['target'], 'go:pkg/orders/http.go::List')
            self.assertEqual(edge['evidence']['source'], 'go_import')

    def test_go_external_import_is_not_resolved(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'go.mod', 'module example.com/shop\n')
            self._write(root, 'local/fmt.go', 'package local\n\nfunc Println() {}\n')
            self._write(
                root, 'main.go',
                'package main\n\nimport "fmt"\n\nfunc Run() { fmt.Println("ok") }\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            self.assertFalse(any(edge['relation'] == 'CALLS' for edge in graph['edges']))

    def test_go_import_resolution_requires_go_mod(self):
        known_dirs = {'pkg/orders'}
        self.assertIsNone(
            living_map._resolve_go_import_dir(
                'example.com/shop/pkg/orders', None, known_dirs,
            )
        )
        self.assertIsNone(
            living_map._resolve_go_import_dir(
                'example.net/other/pkg/orders', 'example.com/shop', known_dirs,
            )
        )

    def test_rust_functions_and_impl_methods_have_ranges_and_stable_ids(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root, 'src/service.rs',
                'pub struct Service;\n\nimpl Service {\n'
                '  pub fn save(&self) -> bool {\n    true\n  }\n}\n',
            )
            records = living_map.scan_file_symbol_records(path, 'src/service.rs')
            method = next(record for record in records if record['name'] == 'save')
            self.assertEqual(method['id'], 'rust:src/service.rs::Service.save')
            self.assertEqual(method['kind'], 'method')
            self.assertEqual((method['line'], method['end_line']), (4, 6))

    def test_rust_graph_extracts_same_module_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/validate.rs', 'pub fn validate() -> bool { true }\n')
            self._write(
                root, 'src/service.rs',
                "pub fn create(_value: &'static str) -> bool {\n  validate()\n}\n",
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'rust:src/service.rs::create')
            self.assertEqual(edge['target'], 'rust:src/validate.rs::validate')
            self.assertEqual(edge['evidence']['source'], 'rust_static')

    def test_rust_test_attribute_becomes_tested_by_edge(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'src/lib.rs',
                'pub fn create() -> bool { true }\n\n'
                '#[test]\nfn test_create() {\n  assert!(create());\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'TESTED_BY')
            self.assertEqual(edge['source'], 'rust:src/lib.rs::create')
            self.assertEqual(edge['target'], 'rust:src/lib.rs::test_create')

    def test_rust_graph_extracts_attribute_and_axum_routes(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'src/api.rs',
                '#[get("/health")]\nasync fn health() {}\n\n'
                'async fn list_orders() {}\n\n'
                'fn router() {\n  Router::new().route("/orders", get(list_orders));\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            handles = [edge for edge in graph['edges'] if edge['relation'] == 'HANDLES']
            self.assertEqual({edge['source'] for edge in handles}, {
                'api:GET /health', 'api:GET /orders',
            })
            self.assertEqual({edge['target'] for edge in handles}, {
                'rust:src/api.rs::health', 'rust:src/api.rs::list_orders',
            })

    def test_rust_use_alias_resolves_cross_module_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/orders.rs', 'pub fn save() -> bool { true }\n')
            self._write(
                root, 'src/main.rs',
                'mod orders;\nuse crate::orders::save as persist;\n\n'
                'fn run() -> bool {\n  persist()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'rust:src/main.rs::run')
            self.assertEqual(edge['target'], 'rust:src/orders.rs::save')
            self.assertEqual(edge['confidence'], 1.0)
            self.assertEqual(edge['evidence']['source'], 'rust_import')

    def test_rust_module_alias_resolves_qualified_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/orders/mod.rs', 'pub fn save() -> bool { true }\n')
            self._write(
                root, 'src/main.rs',
                'mod orders;\nuse crate::orders as order_service;\n\n'
                'fn run() -> bool {\n  order_service::save()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'rust:src/orders/mod.rs::save')
            self.assertEqual(edge['evidence']['source'], 'rust_import')

    def test_rust_crate_qualified_call_resolves_without_use(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/orders.rs', 'pub fn save() -> bool { true }\n')
            self._write(
                root, 'src/main.rs',
                'mod orders;\nfn run() -> bool {\n  crate::orders::save()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'rust:src/orders.rs::save')

    def test_rust_module_resolution_preserves_ambiguity_and_external_paths(self):
        known = {'src/orders.rs', 'src/orders/mod.rs'}
        self.assertIsNone(
            living_map._resolve_rust_module_path('src/main.rs', 'crate::orders', known)
        )
        self.assertIsNone(
            living_map._resolve_rust_module_path('src/main.rs', 'serde::json', known)
        )

    def test_csharp_methods_have_class_qualified_ranges(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root, 'Services/Orders.cs',
                'public class Orders {\n  public bool Save() {\n    return true;\n  }\n}\n',
            )
            records = living_map.scan_file_symbol_records(path, 'Services/Orders.cs')
            method = next(record for record in records if record['name'] == 'Save')
            self.assertEqual(method['id'], 'csharp:Services/Orders.cs::Orders.Save')
            self.assertEqual((method['line'], method['end_line']), (2, 4))

    def test_csharp_graph_resolves_direct_and_this_calls(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'Services/Orders.cs',
                'public class Orders {\n'
                '  private bool Validate() { return true; }\n'
                '  public bool Save() { return this.Validate(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'csharp:Services/Orders.cs::Orders.Save')
            self.assertEqual(edge['target'], 'csharp:Services/Orders.cs::Orders.Validate')
            self.assertEqual(edge['evidence']['source'], 'csharp_static')

    def test_csharp_test_attribute_becomes_tested_by(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'Tests/Helper.cs',
                'public class Helper {\n  public bool Save() { return true; }\n}\n',
            )
            self._write(
                root, 'Tests/HelperTests.cs',
                'public class HelperTests {\n  [Fact]\n'
                '  public void SaveWorks() { Save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'TESTED_BY')
            self.assertEqual(edge['source'], 'csharp:Tests/Helper.cs::Helper.Save')
            self.assertEqual(edge['target'], 'csharp:Tests/HelperTests.cs::HelperTests.SaveWorks')

    def test_csharp_graph_extracts_controller_and_minimal_routes(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'Api/Orders.cs',
                'public class Orders {\n'
                '  [HttpGet("/orders")]\n  public object List() { return null; }\n'
                '  public object Health() { return null; }\n'
                '  public void Routes() { app.MapGet("/health", Health); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            handles = [edge for edge in graph['edges'] if edge['relation'] == 'HANDLES']
            self.assertEqual({edge['source'] for edge in handles}, {
                'api:GET /orders', 'api:GET /health',
            })

    def test_csharp_namespace_becomes_part_of_stable_id(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root, 'Services/Orders.cs',
                'namespace Shop.Services;\n\npublic class Orders {\n'
                '  public bool Save() { return true; }\n}\n',
            )
            records = living_map.scan_file_symbol_records(path, 'Services/Orders.cs')
            ids = {record['id'] for record in records}
            self.assertIn('csharp:Services/Orders.cs::Shop.Services.Orders', ids)
            self.assertIn('csharp:Services/Orders.cs::Shop.Services.Orders.Save', ids)

    def test_csharp_using_namespace_disambiguates_static_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'Sales/Orders.cs',
                'namespace Shop.Sales;\npublic class Orders {\n'
                '  public static bool Save() { return true; }\n}\n',
            )
            self._write(
                root, 'Legacy/Orders.cs',
                'namespace Shop.Legacy;\npublic class Orders {\n'
                '  public static bool Save() { return false; }\n}\n',
            )
            self._write(
                root, 'Api/Runner.cs',
                'using Shop.Sales;\nnamespace Shop.Api;\npublic class Runner {\n'
                '  public bool Run() { return Orders.Save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'csharp:Sales/Orders.cs::Shop.Sales.Orders.Save')

    def test_csharp_type_alias_resolves_static_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'Services/Orders.cs',
                'namespace Shop.Services;\npublic class Orders {\n'
                '  public static bool Save() { return true; }\n}\n',
            )
            self._write(
                root, 'Api/Runner.cs',
                'using OrderService = Shop.Services.Orders;\nnamespace Shop.Api;\n'
                'public class Runner {\n  public bool Run() { return OrderService.Save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'csharp:Services/Orders.cs::Shop.Services.Orders.Save')

    def test_java_methods_have_package_class_qualified_ranges(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root, 'src/Orders.java',
                'package shop.services;\npublic class Orders {\n'
                '  public boolean save() {\n    return true;\n  }\n}\n',
            )
            records = living_map.scan_file_symbol_records(path, 'src/Orders.java')
            method = next(record for record in records if record['name'] == 'save')
            self.assertEqual(method['id'], 'java:src/Orders.java::shop.services.Orders.save')
            self.assertEqual((method['line'], method['end_line']), (3, 5))

    def test_java_graph_resolves_this_method_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'src/Orders.java',
                'package shop;\npublic class Orders {\n'
                '  private boolean validate() { return true; }\n'
                '  public boolean save() { return this.validate(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['source'], 'java:src/Orders.java::shop.Orders.save')
            self.assertEqual(edge['target'], 'java:src/Orders.java::shop.Orders.validate')

    def test_java_junit_call_becomes_tested_by(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/Service.java', 'public class Service {\n  public boolean save() { return true; }\n}\n')
            self._write(
                root, 'src/ServiceTest.java',
                'public class ServiceTest {\n  @Test\n'
                '  public void saveWorks() { save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'TESTED_BY')
            self.assertEqual(edge['source'], 'java:src/Service.java::Service.save')
            self.assertEqual(edge['target'], 'java:src/ServiceTest.java::ServiceTest.saveWorks')

    def test_java_graph_extracts_spring_and_jaxrs_routes(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root, 'src/Orders.java',
                'public class Orders {\n'
                '  @GetMapping("/orders")\n  public Object list() { return null; }\n'
                '  @POST\n  @Path("/orders")\n  public Object create() { return null; }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            handles = [edge for edge in graph['edges'] if edge['relation'] == 'HANDLES']
            self.assertEqual({edge['source'] for edge in handles}, {
                'api:GET /orders', 'api:POST /orders',
            })

    def test_java_import_disambiguates_static_class_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'sales/Orders.java', 'package shop.sales;\npublic class Orders {\n  public static boolean save() { return true; }\n}\n')
            self._write(root, 'legacy/Orders.java', 'package shop.legacy;\npublic class Orders {\n  public static boolean save() { return false; }\n}\n')
            self._write(
                root, 'api/Runner.java',
                'package shop.api;\nimport shop.sales.Orders;\npublic class Runner {\n'
                '  public boolean run() { return Orders.save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'java:sales/Orders.java::shop.sales.Orders.save')
            self.assertEqual(edge['evidence']['source'], 'java_import')

    def test_java_static_import_resolves_bare_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'services/Orders.java', 'package shop.services;\npublic class Orders {\n  public static boolean save() { return true; }\n}\n')
            self._write(
                root, 'api/Runner.java',
                'package shop.api;\nimport static shop.services.Orders.save;\n'
                'public class Runner {\n  public boolean run() { return save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')
            self.assertEqual(edge['target'], 'java:services/Orders.java::shop.services.Orders.save')
            self.assertEqual(edge['evidence']['source'], 'java_import')

    def test_java_wildcard_import_is_not_guessed(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'services/Orders.java', 'package shop.services;\npublic class Orders {\n  public static boolean save() { return true; }\n}\n')
            self._write(
                root, 'api/Runner.java',
                'package shop.api;\nimport static shop.services.Orders.*;\n'
                'public class Runner {\n  public boolean run() { return save(); }\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            self.assertFalse(any(edge['relation'] == 'CALLS' for edge in graph['edges']))

    def test_graph_does_not_guess_ambiguous_call_target(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a.py', 'def save():\n    pass\n')
            self._write(root, 'b.py', 'def save():\n    pass\n')
            self._write(root, 'caller.py', 'def run():\n    save()\n')
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            self.assertEqual(graph['edges'], [])

    def test_javascript_graph_extracts_calls_with_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'service.ts',
                'export function validateOrder(order) {\n'
                '  return Boolean(order)\n'
                '}\n\n'
                'export async function createOrder(order) {\n'
                '  // validateOrder() in a comment is not evidence\n'
                '  const note = "validateOrder()"\n'
                '  return validateOrder(order)\n'
                '}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edges = [edge for edge in graph['edges'] if edge['relation'] == 'CALLS']

            self.assertEqual(len(edges), 1)
            self.assertEqual(edges[0]['source'], 'ts:service.ts::createOrder')
            self.assertEqual(edges[0]['target'], 'ts:service.ts::validateOrder')
            self.assertEqual(edges[0]['confidence'], 1.0)
            self.assertEqual(edges[0]['evidence']['source'], 'javascript_static')
            self.assertEqual(edges[0]['evidence']['line'], 8)

    def test_javascript_graph_does_not_guess_ambiguous_target(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a.ts', 'export function save() { return true }\n')
            self._write(root, 'b.ts', 'export function save() { return true }\n')
            self._write(root, 'caller.ts', 'export function run() { return save() }\n')
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            calls = [edge for edge in graph['edges'] if edge['relation'] == 'CALLS']
            self.assertEqual(calls, [])

    def test_javascript_graph_extracts_block_arrow_call(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'worker.js',
                'const prepare = () => { return true }\n'
                'export const run = async () => {\n  return prepare()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')

            self.assertEqual(edge['source'], 'js:worker.js::run')
            self.assertEqual(edge['target'], 'js:worker.js::prepare')

    def test_javascript_graph_extracts_express_route(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'api.js',
                'function createOrder(req, res) {\n  return res.sendStatus(201)\n}\n'
                '// router.delete("/orders", createOrder)\n'
                'router.post("/orders", createOrder)\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            api_node = next(node for node in graph['nodes'] if node['type'] == 'api')
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'HANDLES')

            self.assertEqual(api_node['id'], 'api:POST /orders')
            self.assertEqual(len([node for node in graph['nodes'] if node['type'] == 'api']), 1)
            self.assertEqual(edge['target'], 'js:api.js::createOrder')
            self.assertEqual(edge['evidence']['source'], 'javascript_static')

    def test_javascript_graph_extracts_next_app_route(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(
                root,
                'app/api/orders/route.ts',
                'export async function GET() {\n  return Response.json([])\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'HANDLES')

            self.assertEqual(edge['source'], 'api:GET /api/orders')
            self.assertEqual(edge['target'], 'ts:app/api/orders/route.ts::GET')

    def test_javascript_spec_call_becomes_tested_by_edge(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'src/service.ts', 'export function createOrder() { return true }\n')
            self._write(
                root,
                'tests/service.spec.ts',
                'function testCreateOrder() {\n  return createOrder()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'TESTED_BY')

            self.assertEqual(edge['source'], 'ts:src/service.ts::createOrder')
            self.assertEqual(edge['target'], 'ts:tests/service.spec.ts::testCreateOrder')
            self.assertEqual(edge['confidence'], 0.9)

    def test_javascript_named_import_alias_disambiguates_duplicate_names(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'a.ts', 'export function save() { return "a" }\n')
            self._write(root, 'b.ts', 'export function save() { return "b" }\n')
            self._write(
                root,
                'caller.ts',
                'import { save as persist } from "./a.js"\n'
                'export function run() {\n  return persist()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')

            self.assertEqual(edge['source'], 'ts:caller.ts::run')
            self.assertEqual(edge['target'], 'ts:a.ts::save')
            self.assertEqual(edge['confidence'], 1.0)

    def test_javascript_namespace_import_resolves_index_module(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'orders/index.ts', 'export function save() { return true }\n')
            self._write(
                root,
                'caller.ts',
                'import * as orders from "./orders"\n'
                'export function run() {\n  return orders.save()\n}\n',
            )
            index = living_map.build_symbol_index(root)
            graph = living_map.build_dependency_graph(index, root)
            edge = next(edge for edge in graph['edges'] if edge['relation'] == 'CALLS')

            self.assertEqual(edge['target'], 'ts:orders/index.ts::save')
            self.assertEqual(edge['evidence']['source'], 'javascript_import')

    def test_javascript_module_resolution_preserves_ambiguity(self):
        known = {'a.js', 'a.ts'}
        self.assertIsNone(
            living_map._resolve_javascript_module_path('caller.ts', './a', known)
        )
        self.assertEqual(
            living_map._resolve_javascript_module_path('caller.ts', './a.js', known),
            'a.js',
        )

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

    def test_mcp_command_adapter_preserves_cli_status_and_output(self):
        def command(args):
            print(f'checked {args.target}')
            return 2

        result = living_map.capture_mcp_command(
            command,
            type('Args', (), {'target': 'checkout'})(),
        )
        self.assertEqual(result, '[ERROR exit=2]\nchecked checkout')

    def test_graph_fitness_measures_coverage_confidence_hubs_and_tests(self):
        graph = {
            'nodes': [
                {'id': 'a', 'type': 'symbol', 'path': 'src/a.py'},
                {'id': 'b', 'type': 'symbol', 'path': 'src/b.py'},
                {'id': 'c', 'type': 'symbol', 'path': 'src/c.py'},
                {'id': 't', 'type': 'symbol', 'path': 'tests/test_c.py'},
            ],
            'edges': [
                {'source': 'a', 'target': 'b', 'relation': 'CALLS', 'confidence': 1.0},
                {'source': 'b', 'target': 'c', 'relation': 'CALLS', 'confidence': 0.8},
                {'source': 'c', 'target': 't', 'relation': 'TESTED_BY', 'confidence': 1.0},
            ],
        }
        config = {
            'schema_version': 1, 'hub_min_incoming': 1,
            'thresholds': {
                'min_edge_coverage': 0.7,
                'min_resolved_edge_ratio': 0.5,
                'max_hub_concentration': 0.5,
                'min_test_link_rate': 0.3,
                'max_constraint_issues': 0,
            },
        }
        report = living_map.analyze_graph_fitness(graph, [], config)
        self.assertTrue(report['passed'])
        self.assertEqual(report['metrics']['edge_coverage'], 0.75)
        self.assertEqual(report['metrics']['resolved_edge_ratio'], 0.5)
        self.assertEqual(report['metrics']['hub_concentration'], 0.5)
        self.assertEqual(report['metrics']['test_link_rate'], 1 / 3)
        self.assertEqual(report['metrics']['untested_hub_count'], 1)

    def test_fitness_config_rejects_incomplete_thresholds(self):
        with tempfile.TemporaryDirectory() as root:
            path = self._write(
                root, 'fitness.json',
                json.dumps({'schema_version': 1, 'hub_min_incoming': 2, 'thresholds': {}}),
            )
            with self.assertRaisesRegex(ValueError, 'must define exactly'):
                living_map.load_fitness_config(path)

    def test_parse_diff_and_guard_score_changed_symbol_only(self):
        diff = (
            'diff --git a/src/service.py b/src/service.py\n'
            '--- a/src/service.py\n+++ b/src/service.py\n'
            '@@ -11 +11,2 @@\n-old\n+new\n+line\n'
        )
        ranges = living_map.parse_unified_diff(diff)
        self.assertEqual(ranges, {'src/service.py': [(11, 12)]})
        nodes = [
            {'id': 'service', 'type': 'symbol', 'path': 'src/service.py', 'line': 10, 'end_line': 20},
            {'id': 'other', 'type': 'symbol', 'path': 'src/service.py', 'line': 30, 'end_line': 40},
            {'id': 'test', 'type': 'symbol', 'path': 'tests/test_service.py', 'line': 1, 'end_line': 8},
        ]
        callers = [
            {'id': f'caller{i}', 'type': 'symbol', 'path': f'src/c{i}.py', 'line': 1, 'end_line': 2}
            for i in range(3)
        ]
        graph = {'nodes': nodes + callers, 'edges': [
            *[
                {'source': f'caller{i}', 'target': 'service', 'relation': 'CALLS', 'confidence': 1.0}
                for i in range(3)
            ],
            {'source': 'service', 'target': 'test', 'relation': 'TESTED_BY', 'confidence': 1.0},
        ]}
        report = living_map.analyze_diff_guard(
            ranges, ['src/service.py'], graph,
        )
        self.assertEqual([item['id'] for item in report['changed_symbols']], ['service'])
        self.assertEqual(report['risk_level'], 'medium')
        self.assertIn('linked tests unchanged', report['changed_symbols'][0]['reasons'])

    def test_test_gap_ranking_prioritizes_untested_hub(self):
        nodes = [
            {'id': 'hub', 'type': 'symbol', 'path': 'src/hub.py', 'line': 1},
            {'id': 'tested', 'type': 'symbol', 'path': 'src/tested.py', 'line': 1},
            {'id': 'test', 'type': 'symbol', 'path': 'tests/test_tested.py', 'line': 1},
            {'id': 'parent', 'type': 'symbol', 'kind': 'function', 'path': 'src/local.py', 'line': 10, 'end_line': 30},
            {'id': 'nested', 'type': 'symbol', 'kind': 'method', 'path': 'src/local.py', 'line': 15, 'end_line': 20},
        ] + [
            {'id': f'caller{i}', 'type': 'symbol', 'path': f'src/c{i}.py', 'line': 1}
            for i in range(3)
        ]
        edges = []
        for index in range(3):
            edges.append({'source': f'caller{index}', 'target': 'hub', 'relation': 'CALLS', 'confidence': 1.0})
            edges.append({'source': f'caller{index}', 'target': 'tested', 'relation': 'CALLS', 'confidence': 1.0})
            edges.append({'source': f'caller{index}', 'target': 'nested', 'relation': 'CALLS', 'confidence': 1.0})
        edges.append({'source': 'tested', 'target': 'test', 'relation': 'TESTED_BY', 'confidence': 1.0})
        gaps = living_map.rank_test_gaps({'nodes': nodes, 'edges': edges}, 3)
        self.assertEqual([item['id'] for item in gaps], ['hub'])
        self.assertEqual(gaps[0]['priority_score'], 30)
        symbol_nodes = {node['id']: node for node in nodes if node.get('type') == 'symbol'}
        self.assertEqual(living_map._nested_local_symbol_ids(symbol_nodes), {'nested'})

    def test_high_fan_in_helpers_have_direct_regression_coverage(self):
        masked = living_map._strip_javascript_noncode(
            'function run() { return "}"; /* ignored */ }'
        )
        opening = masked.index('{')
        self.assertEqual(
            living_map._matching_delimiter(masked, opening, '{', '}'),
            masked.rindex('}'),
        )
        self.assertEqual(
            living_map._symbol_fingerprint('function', 'run', 'function  run()'),
            living_map._symbol_fingerprint('function', 'run', 'function run()'),
        )
        self.assertTrue(living_map._is_test_path('src/service_test.go'))
        self.assertFalse(living_map._is_test_path('src/service.go'))
        with tempfile.TemporaryDirectory() as root:
            self._write(root, 'app.py', 'def run():\n    return 1\n')
            first = living_map.calculate_codebase_hash(root)
            self._write(root, 'ignored/readme.txt', 'not source')
            self.assertEqual(first, living_map.calculate_codebase_hash(root))

    def test_high_leverage_io_helpers_have_direct_regression_coverage(self):
        code, output, error = living_map._git(['rev-parse', '--is-inside-work-tree'])
        self.assertEqual((code, output, error), (0, 'true', ''))
        with mock.patch.object(
            living_map, 'git_get_head_info', return_value=('abc1234', '', ''),
        ):
            updated = living_map.update_map_header(
                '> **Last Updated:** old | Commit: old\nCodebase-MD5: ' + '0' * 32,
                '1' * 32,
            )
        self.assertIn('Commit: abc1234', updated)
        self.assertIn('Codebase-MD5: ' + '1' * 32, updated)
        with tempfile.TemporaryDirectory() as root:
            source = self._write(root, 'PROJECT_MAP.md', '## MODULE 0: META\n| Key | Value |\n')
            compact = os.path.join(root, 'PROJECT_MAP.min.md')
            self.assertEqual(living_map.generate_min_map(source, compact), compact)
            constraint_path = self._write(
                root, '.lcm/constraints.json',
                json.dumps({'schema_version': 1, 'constraints': []}),
            )
            self.assertEqual(living_map.load_constraints(constraint_path)['constraints'], [])

    def test_remaining_hub_helpers_have_direct_regression_coverage(self):
        with mock.patch.object(
            living_map, '_git', return_value=(0, 'abc1234|' + 'a' * 40 + '|2026-09-20 01:02:03', ''),
        ):
            self.assertEqual(
                living_map.git_get_head_info(),
                ('abc1234', 'a' * 40, '2026-09-20'),
            )
        with mock.patch.object(living_map, '_git', side_effect=[
            (0, '', ''), (0, 'committed', ''), (0, 'abc1234', ''),
        ]):
            self.assertTrue(living_map.git_commit_map('test map commit'))
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, '.lcm', 'constraints.json')
            payload = {'schema_version': 1, 'constraints': []}
            living_map.write_constraints(payload, path)
            with open(path, 'r', encoding='utf-8') as handle:
                self.assertEqual(json.load(handle), payload)

    def test_mcp_server_registers_cli_parity_tools(self):
        class FakeFastMCP:
            def __init__(self, name):
                self.name = name
                self.tools = []

            def tool(self):
                def register(function):
                    self.tools.append(function.__name__)
                    return function
                return register

        mcp_module = types.ModuleType('mcp')
        mcp_module.__path__ = []
        server_module = types.ModuleType('mcp.server')
        server_module.__path__ = []
        fastmcp_module = types.ModuleType('mcp.server.fastmcp')
        fastmcp_module.FastMCP = FakeFastMCP
        modules = {
            'mcp': mcp_module,
            'mcp.server': server_module,
            'mcp.server.fastmcp': fastmcp_module,
        }
        with mock.patch.dict(sys.modules, modules):
            server = living_map.build_mcp_server()

        self.assertEqual(set(server.tools), {
            'update_map', 'check_drift', 'analyze_code_impact',
            'plan_change', 'fitness_report', 'test_gap_hotspots', 'guard_change',
            'verify_change', 'compile_context',
            'explain_symbol', 'explain_symbol_history',
            'register_feature', 'register_constraint', 'get_map_summary',
        })


if __name__ == '__main__':
    unittest.main()

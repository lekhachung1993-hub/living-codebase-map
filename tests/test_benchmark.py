import json
import os
import tempfile
import unittest

from scripts import benchmark


class BenchmarkTests(unittest.TestCase):
    def test_evaluate_run_scores_retrieval_and_efficiency(self):
        suite = {'schema_version': 1, 'tasks': [{
            'id': 'T1', 'prompt': 'change context compiler',
            'acceptance_checks': ['tests pass'],
            'expected_files': ['context.py', 'test_context.py'],
            'expected_symbols': ['compile'],
            'expected_dependencies': ['compile->plan'],
            'expected_tests': ['test_context.py'],
            'expected_constraints': ['C1'],
        }]}
        run = {'schema_version': 1, 'metadata': {
            'repository_commit': 'abc', 'model': 'test',
            'configuration': 'lcm', 'timeout_seconds': 60,
        }, 'results': [{
            'task_id': 'T1', 'success': True,
            'files_read': ['context.py', 'extra.py'],
            'symbols_selected': ['compile'],
            'dependencies_found': [],
            'tests_found': ['test_context.py'],
            'constraints_found': ['C1'],
            'tokens': 100, 'tool_calls': 2, 'duration_seconds': 3,
        }]}
        result = benchmark.evaluate_run(suite, run, 'lcm')
        self.assertEqual(result['aggregate']['files_recall'], 0.5)
        self.assertEqual(result['aggregate']['files_precision'], 0.5)
        self.assertEqual(result['aggregate']['dependencies_recall'], 0.0)
        self.assertEqual(result['aggregate']['success_rate'], 1.0)
        self.assertEqual(result['aggregate']['total_tokens'], 100)

    def test_validation_rejects_missing_task_results(self):
        issues = benchmark.validate_run(
            {'schema_version': 1, 'results': []}, {'T1'},
        )
        self.assertIn('missing task results: T1', issues)

    def test_evaluate_files_and_render_report(self):
        suite = {'schema_version': 1, 'name': 'sample', 'tasks': [{
            'id': 'T1', 'prompt': 'task', 'acceptance_checks': ['pass'], 'expected_files': [],
            'expected_symbols': [], 'expected_dependencies': [],
            'expected_tests': [], 'expected_constraints': [],
        }]}
        run = {'schema_version': 1, 'metadata': {
            'repository_commit': 'abc', 'model': 'test',
            'configuration': 'lcm', 'timeout_seconds': 60,
        }, 'results': [{
            'task_id': 'T1', 'success': True, 'tokens': 5,
            'tool_calls': 1, 'duration_seconds': 0.5,
        }]}
        with tempfile.TemporaryDirectory() as root:
            suite_path = os.path.join(root, 'suite.json')
            run_path = os.path.join(root, 'run.json')
            for path, payload in ((suite_path, suite), (run_path, run)):
                with open(path, 'w', encoding='utf-8') as handle:
                    json.dump(payload, handle)
            report = benchmark.evaluate_files(suite_path, [f'lcm={run_path}'])
        rendered = benchmark.render_markdown(report)
        self.assertIn('| lcm | 100.0%', rendered)
        self.assertIn('## Missed ground truth', rendered)


if __name__ == '__main__':
    unittest.main()

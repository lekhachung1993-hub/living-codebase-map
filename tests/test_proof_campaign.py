import json
import os
import tempfile
import unittest

from scripts import proof_campaign, scale_benchmark


class ProofCampaignTests(unittest.TestCase):
    def _write_json(self, root, relative, payload):
        path = os.path.join(root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle)
        return path

    def _run(self, configuration):
        return {
            'schema_version': 1,
            'name': configuration,
            'metadata': {
                'repository_commit': 'a' * 40,
                'repository_url': 'https://example.com/repo',
                'model': 'same-model',
                'configuration': configuration,
                'timeout_seconds': 900,
                'execution_id': configuration + '-001',
                'transcript_sha256': 'b' * 64,
            },
            'results': [{
                'task_id': 'task', 'success': True,
                'files_read': ['app.py'], 'symbols_selected': [],
                'dependencies_found': [], 'tests_found': [],
                'constraints_found': [], 'tokens': 10,
                'tool_calls': 1, 'duration_seconds': 1,
            }],
        }

    def test_campaign_requires_and_aggregates_auditable_runs(self):
        with tempfile.TemporaryDirectory() as root:
            self._write_json(root, 'suite.json', {
                'schema_version': 1,
                'name': 'suite',
                'tasks': [{
                    'id': 'task', 'category': 'test', 'prompt': 'Find app',
                    'acceptance_checks': ['found'], 'expected_files': ['app.py'],
                    'expected_symbols': [], 'expected_dependencies': [],
                    'expected_tests': [], 'expected_constraints': [],
                }],
            })
            self._write_json(root, 'baseline.json', self._run('baseline'))
            self._write_json(root, 'lcm.json', self._run('lcm'))
            manifest = self._write_json(root, 'campaign.json', {
                'schema_version': 1, 'name': 'proof',
                'repositories': [{
                    'name': 'repo', 'suite': 'suite.json',
                    'url': 'https://example.com/repo', 'commit': 'a' * 40,
                    'runs': [
                        {'name': 'baseline', 'path': 'baseline.json', 'role': 'baseline'},
                        {'name': 'lcm', 'path': 'lcm.json', 'role': 'candidate'},
                    ],
                }],
            })
            report = proof_campaign.evaluate_campaign(manifest)
        self.assertTrue(report['passed'])
        self.assertEqual(report['repository_count'], 1)

    def test_campaign_rejects_missing_transcript_digest(self):
        run = self._run('baseline')
        del run['metadata']['transcript_sha256']
        self.assertIn(
            'run metadata is missing transcript_sha256',
            proof_campaign.validate_run_evidence(run),
        )

    def test_campaign_rejects_ambiguous_run_descriptors(self):
        payload = {
            'schema_version': 1,
            'repositories': [{
                'name': 'repo', 'suite': 'suite.json',
                'url': 'https://example.com/repo', 'commit': 'a' * 40,
                'runs': [
                    {'name': 'same', 'path': 'one.json', 'role': 'baseline'},
                    {'name': 'same', 'path': 'two.json', 'role': 'candidate'},
                    {'name': 'extra', 'path': 'three.json', 'role': 'unknown'},
                ],
            }],
        }
        issues = proof_campaign.validate_campaign(payload)
        self.assertTrue(any('duplicate run name' in issue for issue in issues))
        self.assertTrue(any('run role must be' in issue for issue in issues))

    def test_scale_benchmark_records_cold_and_warm_modes(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, 'app.py'), 'w', encoding='utf-8') as handle:
                handle.write('def run():\n    return True\n')
            result = scale_benchmark.measure_repository(root, 'local-fixture', repetitions=2)
        self.assertEqual(result['measurements'][0]['graph_stats']['mode'], 'full')
        self.assertEqual(result['measurements'][1]['graph_stats']['mode'], 'reused')

    def test_scale_git_metadata_helper_reads_repository(self):
        root = os.path.dirname(os.path.dirname(__file__))
        self.assertRegex(scale_benchmark._git(root, ['rev-parse', 'HEAD']), r'^[a-f0-9]{40}$')


if __name__ == '__main__':
    unittest.main()

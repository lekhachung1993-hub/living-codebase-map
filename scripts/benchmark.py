#!/usr/bin/env python3
"""Deterministic benchmark evaluator for Living Codebase Map agent runs."""

import argparse
import json
import os
import statistics
import sys


SCHEMA_VERSION = 1
RETRIEVAL_FIELDS = (
    ('files', 'expected_files', 'files_read'),
    ('symbols', 'expected_symbols', 'symbols_selected'),
    ('dependencies', 'expected_dependencies', 'dependencies_found'),
    ('tests', 'expected_tests', 'tests_found'),
    ('constraints', 'expected_constraints', 'constraints_found'),
)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def validate_suite(suite):
    issues = []
    if suite.get('schema_version') != SCHEMA_VERSION:
        issues.append(f"suite schema_version must be {SCHEMA_VERSION}")
    tasks = suite.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        issues.append('suite tasks must be a non-empty list')
        return issues
    seen = set()
    for index, task in enumerate(tasks):
        task_id = task.get('id')
        if not task_id:
            issues.append(f'task {index} is missing id')
        elif task_id in seen:
            issues.append(f'duplicate task id: {task_id}')
        seen.add(task_id)
        if not task.get('prompt'):
            issues.append(f'{task_id or index}: missing prompt')
        if not isinstance(task.get('acceptance_checks'), list) or not task.get('acceptance_checks'):
            issues.append(f'{task_id or index}: acceptance_checks must be a non-empty list')
        for _, expected_key, _ in RETRIEVAL_FIELDS:
            if not isinstance(task.get(expected_key, []), list):
                issues.append(f'{task_id or index}: {expected_key} must be a list')
    return issues


def validate_run(run, task_ids):
    issues = []
    if run.get('schema_version') != SCHEMA_VERSION:
        issues.append(f"run schema_version must be {SCHEMA_VERSION}")
    metadata = run.get('metadata', {})
    for key in ('repository_commit', 'model', 'configuration', 'timeout_seconds'):
        if not metadata.get(key):
            issues.append(f'run metadata is missing {key}')
    results = run.get('results')
    if not isinstance(results, list):
        return issues + ['run results must be a list']
    seen = set()
    for index, result in enumerate(results):
        task_id = result.get('task_id')
        if task_id not in task_ids:
            issues.append(f'result {index} references unknown task: {task_id}')
        elif task_id in seen:
            issues.append(f'duplicate result task_id: {task_id}')
        seen.add(task_id)
        for key in ('tokens', 'tool_calls', 'duration_seconds'):
            value = result.get(key, 0)
            if not isinstance(value, (int, float)) or value < 0:
                issues.append(f'{task_id or index}: {key} must be non-negative')
    missing = sorted(task_ids - seen)
    if missing:
        issues.append('missing task results: ' + ', '.join(missing))
    return issues


def _retrieval_metrics(expected, actual):
    expected_set = set(expected)
    actual_set = set(actual)
    correct = expected_set & actual_set
    applicable = bool(expected_set)
    recall = len(correct) / len(expected_set) if applicable else None
    precision = len(correct) / len(actual_set) if actual_set and applicable else (0.0 if applicable else None)
    return {
        'applicable': applicable,
        'precision': precision,
        'recall': recall,
        'missed': sorted(expected_set - actual_set),
        'extra': sorted(actual_set - expected_set),
    }


def evaluate_run(suite, run, name=None):
    tasks = {task['id']: task for task in suite['tasks']}
    results = {result['task_id']: result for result in run['results']}
    task_scores = []
    for task_id, task in tasks.items():
        result = results[task_id]
        retrieval = {}
        for label, expected_key, actual_key in RETRIEVAL_FIELDS:
            retrieval[label] = _retrieval_metrics(
                task.get(expected_key, []), result.get(actual_key, []),
            )
        task_scores.append({
            'task_id': task_id,
            'category': task.get('category', 'unspecified'),
            'success': bool(result.get('success')),
            'tokens': result.get('tokens', 0),
            'tool_calls': result.get('tool_calls', 0),
            'duration_seconds': result.get('duration_seconds', 0),
            'retrieval': retrieval,
        })

    def mean(values):
        return statistics.mean(values) if values else 0.0

    aggregate = {
        'task_count': len(task_scores),
        'success_rate': mean([float(item['success']) for item in task_scores]),
        'total_tokens': sum(item['tokens'] for item in task_scores),
        'mean_tokens': mean([item['tokens'] for item in task_scores]),
        'total_tool_calls': sum(item['tool_calls'] for item in task_scores),
        'mean_tool_calls': mean([item['tool_calls'] for item in task_scores]),
        'total_duration_seconds': sum(item['duration_seconds'] for item in task_scores),
    }
    for label, _, _ in RETRIEVAL_FIELDS:
        applicable = [
            item['retrieval'][label] for item in task_scores
            if item['retrieval'][label]['applicable']
        ]
        aggregate[f'{label}_precision'] = mean([item['precision'] for item in applicable]) if applicable else None
        aggregate[f'{label}_recall'] = mean([item['recall'] for item in applicable]) if applicable else None
        aggregate[f'missed_{label}'] = sum(
            len(item['retrieval'][label]['missed']) for item in task_scores
        )
    return {
        'name': name or run.get('name', 'run'),
        'metadata': run.get('metadata', {}),
        'aggregate': aggregate,
        'tasks': task_scores,
    }


def render_markdown(report):
    def percent(value):
        return 'n/a' if value is None else f'{value:.1%}'

    lines = [
        '# LCM Benchmark Report', '',
        f"Suite: `{report['suite']}`  ",
        f"Tasks: {report['task_count']}", '',
        '| Run | Success | File recall | Symbol recall | Dependency recall | Test recall | Constraint recall | Tokens | Tool calls | Seconds |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for run in report['runs']:
        item = run['aggregate']
        lines.append(
            f"| {run['name']} | {item['success_rate']:.1%} | "
            f"{percent(item['files_recall'])} | {percent(item['symbols_recall'])} | "
            f"{percent(item['dependencies_recall'])} | {percent(item['tests_recall'])} | "
            f"{percent(item['constraints_recall'])} | {item['total_tokens']:.0f} | "
            f"{item['total_tool_calls']:.0f} | {item['total_duration_seconds']:.1f} |"
        )
    lines.extend(['', '## Missed ground truth', ''])
    for run in report['runs']:
        misses = []
        for task in run['tasks']:
            for label, metrics in task['retrieval'].items():
                if metrics['missed']:
                    misses.append(
                        f"- `{task['task_id']}` {label}: " + ', '.join(f'`{item}`' for item in metrics['missed'])
                    )
        lines.append(f"### {run['name']}")
        lines.extend(misses or ['- None'])
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def evaluate_files(suite_path, run_specs):
    suite = load_json(suite_path)
    issues = validate_suite(suite)
    if issues:
        raise ValueError('; '.join(issues))
    task_ids = {task['id'] for task in suite['tasks']}
    evaluated = []
    for spec in run_specs:
        if '=' not in spec:
            raise ValueError(f'run must use NAME=PATH: {spec}')
        name, path = spec.split('=', 1)
        run = load_json(path)
        run_issues = validate_run(run, task_ids)
        if run_issues:
            raise ValueError(f'{name}: ' + '; '.join(run_issues))
        evaluated.append(evaluate_run(suite, run, name))
    return {
        'schema_version': SCHEMA_VERSION,
        'suite': suite.get('name', os.path.basename(suite_path)),
        'task_count': len(task_ids),
        'runs': evaluated,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', required=True, help='Benchmark suite JSON')
    parser.add_argument('--run', action='append', required=True, help='Run input as NAME=PATH; repeat to compare')
    parser.add_argument('--json-output', help='Write machine-readable report')
    parser.add_argument('--markdown-output', help='Write human-readable report')
    args = parser.parse_args(argv)
    try:
        report = evaluate_files(args.suite, args.run)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'[BENCHMARK ERROR] {exc}', file=sys.stderr)
        return 2
    rendered = render_markdown(report)
    if args.json_output:
        with open(args.json_output, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write('\n')
    if args.markdown_output:
        with open(args.markdown_output, 'w', encoding='utf-8') as handle:
            handle.write(rendered)
    if not args.json_output and not args.markdown_output:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

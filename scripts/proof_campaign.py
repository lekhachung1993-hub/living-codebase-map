#!/usr/bin/env python3
"""Validate and aggregate reproducible multi-repository LCM proof campaigns."""

import argparse
import hashlib
import json
import os
import re
import sys

try:
    from . import benchmark
except ImportError:
    import benchmark


SCHEMA_VERSION = 1


def load_json(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def validate_run_evidence(run):
    """Require auditable evidence beyond self-reported benchmark metrics."""
    issues = []
    metadata = run.get('metadata', {})
    for key in ('repository_url', 'execution_id', 'transcript_sha256'):
        if not metadata.get(key):
            issues.append(f'run metadata is missing {key}')
    digest = metadata.get('transcript_sha256', '')
    if digest and not re.fullmatch(r'[a-f0-9]{64}', digest):
        issues.append('transcript_sha256 must be a lowercase SHA-256 digest')
    commit = str(metadata.get('repository_commit', ''))
    if commit and not re.fullmatch(r'[a-fA-F0-9]{7,64}', commit):
        issues.append('repository_commit must be a Git commit hash')
    return issues


def transcript_sha256(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_campaign(payload):
    issues = []
    if payload.get('schema_version') != SCHEMA_VERSION:
        issues.append(f'campaign schema_version must be {SCHEMA_VERSION}')
    repositories = payload.get('repositories')
    if not isinstance(repositories, list) or not repositories:
        return issues + ['campaign repositories must be a non-empty list']
    names = set()
    for position, repository in enumerate(repositories):
        name = repository.get('name')
        if not name:
            issues.append(f'repository {position}: name is required')
        elif name in names:
            issues.append(f'duplicate repository name: {name}')
        names.add(name)
        if not repository.get('suite'):
            issues.append(f'{name or position}: suite is required')
        if not repository.get('url'):
            issues.append(f'{name or position}: url is required')
        if not re.fullmatch(r'[a-fA-F0-9]{7,64}', str(repository.get('commit', ''))):
            issues.append(f'{name or position}: commit must be a Git commit hash')
        runs = repository.get('runs')
        if not isinstance(runs, list) or len(runs) < 2:
            issues.append(f'{name or position}: at least two runs are required')
            continue
        baselines = [run for run in runs if run.get('role') == 'baseline']
        candidates = [run for run in runs if run.get('role') == 'candidate']
        if len(baselines) != 1:
            issues.append(f'{name or position}: exactly one baseline run is required')
        if not candidates:
            issues.append(f'{name or position}: at least one candidate run is required')
        run_names = set()
        for run in runs:
            if not run.get('name') or not run.get('path'):
                issues.append(f'{name or position}: every run requires name and path')
            if run.get('role') not in {'baseline', 'candidate'}:
                issues.append(f'{name or position}: run role must be baseline or candidate')
            run_name = run.get('name')
            if run_name in run_names:
                issues.append(f'{name or position}: duplicate run name: {run_name}')
            run_names.add(run_name)
    return issues


def evaluate_campaign(manifest_path, max_token_increase_pct=None):
    campaign = load_json(manifest_path)
    issues = validate_campaign(campaign)
    if issues:
        raise ValueError('; '.join(issues))
    base_dir = os.path.dirname(os.path.abspath(manifest_path))
    reports = []
    evidence_issues = []
    execution_ids = set()
    for repository in campaign['repositories']:
        issue_count = len(evidence_issues)
        suite_path = os.path.join(base_dir, repository['suite'])
        specs = []
        baseline_name = None
        for descriptor in repository['runs']:
            run_path = os.path.join(base_dir, descriptor['path'])
            run = load_json(run_path)
            for issue in validate_run_evidence(run):
                evidence_issues.append(
                    f"{repository['name']}/{descriptor['name']}: {issue}"
                )
            metadata = run.get('metadata', {})
            if metadata.get('repository_url') != repository['url']:
                evidence_issues.append(
                    f"{repository['name']}/{descriptor['name']}: repository_url mismatch"
                )
            if metadata.get('repository_commit') != repository['commit']:
                evidence_issues.append(
                    f"{repository['name']}/{descriptor['name']}: repository_commit mismatch"
                )
            execution_id = metadata.get('execution_id')
            if execution_id in execution_ids:
                evidence_issues.append(f'duplicate execution_id: {execution_id}')
            execution_ids.add(execution_id)
            specs.append(f"{descriptor['name']}={run_path}")
            if descriptor['role'] == 'baseline':
                baseline_name = descriptor['name']
        if len(evidence_issues) > issue_count:
            continue
        report = benchmark.evaluate_files(
            suite_path, specs, baseline_name, max_token_increase_pct,
        )
        report['repository'] = repository['name']
        reports.append(report)
    if evidence_issues:
        raise ValueError('; '.join(evidence_issues))
    comparisons = [
        comparison
        for report in reports
        for comparison in report.get('comparisons', [])
    ]
    return {
        'schema_version': SCHEMA_VERSION,
        'name': campaign.get('name', os.path.basename(manifest_path)),
        'repository_count': len(reports),
        'task_count': sum(report['task_count'] for report in reports),
        'passed': bool(comparisons) and all(item['passed'] for item in comparisons),
        'repositories': reports,
    }


def render_markdown(report):
    lines = [
        '# LCM External Proof Campaign', '',
        f"Campaign: `{report['name']}`  ",
        f"Repositories: {report['repository_count']}  ",
        f"Tasks: {report['task_count']}  ",
        f"Gate: {'PASS' if report['passed'] else 'FAIL'}", '',
    ]
    for repository in report['repositories']:
        lines.append(f"## {repository['repository']}")
        lines.append('')
        lines.append(benchmark.render_markdown(repository))
    return '\n'.join(lines).rstrip() + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', help='Campaign manifest JSON')
    parser.add_argument('--json-output')
    parser.add_argument('--markdown-output')
    parser.add_argument('--gate', action='store_true')
    parser.add_argument('--max-token-increase-pct', type=float)
    parser.add_argument('--sha256', help='Print SHA-256 for a retained raw transcript')
    args = parser.parse_args(argv)
    if args.sha256:
        print(transcript_sha256(args.sha256))
        return 0
    if not args.campaign:
        parser.error('--campaign is required unless --sha256 is used')
    try:
        report = evaluate_campaign(args.campaign, args.max_token_increase_pct)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'[PROOF ERROR] {exc}', file=sys.stderr)
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
    return 3 if args.gate and not report['passed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())

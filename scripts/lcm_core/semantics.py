"""Semantic consistency checks across human and machine projections."""

import re


def markdown_constraint_ids(content):
    return set(re.findall(r'^-\s*\[(C\d+)\]', content, re.MULTILINE))


def markdown_feature_ids(content):
    return set(re.findall(r'^\|\s*(F\d+)\s*\|', content, re.MULTILINE))


def validate_markdown_semantics(content, constraints, compact_content=None):
    """Detect knowledge that exists in only one repository projection."""
    issues = []
    declared = {
        entry.get('id') for entry in constraints.get('constraints', [])
        if isinstance(entry, dict) and entry.get('id')
    }
    documented = markdown_constraint_ids(content)
    missing_structured = sorted(documented - declared)
    missing_markdown = sorted(declared - documented)
    if missing_structured:
        issues.append(
            'Markdown constraints missing structured records: ' + ', '.join(missing_structured)
        )
    if missing_markdown:
        issues.append(
            'structured constraints missing Markdown projection: ' + ', '.join(missing_markdown)
        )

    features = markdown_feature_ids(content)
    if 'FEATURE TRACEABILITY MATRIX' in content and not features:
        issues.append('feature traceability matrix has no feature records')

    if compact_content is not None:
        compact_constraints = markdown_constraint_ids(compact_content)
        compact_features = markdown_feature_ids(compact_content)
        if documented and compact_constraints != documented:
            issues.append('compact map does not preserve all documented constraints')
        if features and compact_features != features:
            issues.append('compact map does not preserve all feature records')
    return issues

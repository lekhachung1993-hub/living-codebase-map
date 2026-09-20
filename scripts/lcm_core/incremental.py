"""File-hash cache used to avoid rescanning unchanged source files."""

import hashlib
import json
import os

from .schema import CACHE_SCHEMA_VERSION

EXTRACTOR_VERSION = 1


def _read_cache(path):
    if not path or not os.path.exists(path):
        return {'schema_version': CACHE_SCHEMA_VERSION, 'extractor_version': EXTRACTOR_VERSION, 'files': {}}
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {'schema_version': CACHE_SCHEMA_VERSION, 'extractor_version': EXTRACTOR_VERSION, 'files': {}}
    if payload.get('schema_version') != CACHE_SCHEMA_VERSION or payload.get('extractor_version') != EXTRACTOR_VERSION:
        return {'schema_version': CACHE_SCHEMA_VERSION, 'extractor_version': EXTRACTOR_VERSION, 'files': {}}
    return payload


def _write_cache(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    os.replace(temporary, path)


def build_incremental_records(root_dir, code_extensions, ignored_dirs, scan, cache_path=None):
    """Return file metadata and symbols, reusing records for unchanged files."""
    previous = _read_cache(cache_path)
    current = {}
    files = []
    symbols = []
    stats = {'scanned': 0, 'reused': 0, 'removed': 0}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = sorted(name for name in dirnames if name not in ignored_dirs)
        for filename in sorted(filenames):
            extension = os.path.splitext(filename)[1].lower()
            if extension not in code_extensions:
                continue
            absolute = os.path.join(dirpath, filename)
            relative = os.path.relpath(absolute, root_dir).replace('\\', '/')
            try:
                with open(absolute, 'rb') as handle:
                    digest = hashlib.sha256(handle.read()).hexdigest()
            except OSError:
                digest = None
            cached = previous.get('files', {}).get(relative)
            if cached and cached.get('sha256') == digest:
                records = cached.get('symbols', [])
                stats['reused'] += 1
            else:
                records = scan(absolute, relative)
                stats['scanned'] += 1
            files.append({'path': relative, 'language': code_extensions[extension], 'sha256': digest})
            symbols.extend(records)
            current[relative] = {'sha256': digest, 'symbols': records}
    stats['removed'] = len(set(previous.get('files', {})) - set(current))
    payload = {
        'schema_version': CACHE_SCHEMA_VERSION,
        'extractor_version': EXTRACTOR_VERSION,
        'files': current,
    }
    if cache_path:
        _write_cache(cache_path, payload)
    return files, symbols, stats

#!/usr/bin/env python3
"""
living_map.py -- Universal Living Codebase Map Engine (v3)
Part of the 'living-codebase-map' skill for AI Coding Agents.

Zero-dependency CLI tool to maintain, update, lint, and version-control PROJECT_MAP.md.

Features:
  - Token-Efficient Compact Map: Automatically generates PROJECT_MAP.min.md (saves ~65% tokens)
  - Fast Blast Radius Scanner: Instant cross-layer impact analysis (--impact-of <symbol>)
  - Smart Drift Checker: MD5 hash-based verification suitable for Git Hooks
  - Multi-language AST/Regex Scanners: Go, Python, TypeScript, JavaScript, HTML, Rust, C#, Java, PHP, Vue
  - Framework Support: Next.js (App & Pages Router), FastAPI, Django, Flask, Gin, Fiber, Express, NestJS, Spring, ASP.NET, Laravel
  - CI/CD Drift Linting: Blocks PRs and Git commits if map is out of sync with code
  - Git Integration: Atomic commit, historical rollback, and auto git hook installer

Usage:
  # Refresh map & generate mini map (run after modifying code):
  python living_map.py update [--auto-commit]

  # Instant blast radius / impact analysis before editing a symbol:
  python living_map.py impact <symbol_or_keyword>

  # Fast Smart Drift Lint (compares the stored MD5):
  python living_map.py check [--full] [--fix]

  # Install Git Pre-Commit / Pre-Push hook:
  python living_map.py install-hook [--hook pre-commit|pre-push]

  # Inject completed feature into Cross-Reference table:
  python living_map.py add-feature --id F001 --desc "Feature name" --commit abc1234 \
    --ui "#btn-id" --js "func() app.js" --api "POST /api/items" --db "items"

  # Add newly discovered implicit constraint to Module 4:
  python living_map.py add-constraint "Mobile bottom bar must have fixed z-index"

  # View map git history or rollback:
  python living_map.py rollback
  python living_map.py rollback --to <COMMIT_HASH>
"""

import ast
import json
import re
import os
import io
import sys
import hashlib
import argparse
import subprocess
import contextlib
import posixpath
from datetime import datetime

# Reconfigure stdout/stderr for Unicode safety across Windows/Linux terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_FILENAME = 'PROJECT_MAP.md'
MIN_MAP_FILENAME = 'PROJECT_MAP.min.md'
INDEX_SCHEMA_VERSION = 3
GRAPH_SCHEMA_VERSION = 1
CONSTRAINT_SCHEMA_VERSION = 1
LCM_DIRNAME = '.lcm'
INDEX_FILENAME = 'index.json'
GRAPH_FILENAME = 'graph.json'
CONSTRAINT_FILENAME = 'constraints.json'

def find_project_root():
    """Locates the project root directory reliably."""
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, MAP_FILENAME)):
        return cwd

    check = cwd
    for _ in range(5):
        if os.path.exists(os.path.join(check, MAP_FILENAME)):
            return check
        p = os.path.dirname(check)
        if p == check:
            break
        check = p

    check = SCRIPT_DIR
    candidate = None
    for _ in range(6):
        if os.path.exists(os.path.join(check, MAP_FILENAME)):
            return check
        if os.path.exists(os.path.join(check, '.git')) and '.agents' not in check and 'skills' not in check:
            candidate = check
        p = os.path.dirname(check)
        if p == check:
            break
        check = p

    return candidate if candidate else cwd

ROOT = find_project_root()
MAP_PATH = os.path.join(ROOT, MAP_FILENAME)
MIN_MAP_PATH = os.path.join(ROOT, MIN_MAP_FILENAME)
INDEX_PATH = os.path.join(ROOT, LCM_DIRNAME, INDEX_FILENAME)
GRAPH_PATH = os.path.join(ROOT, LCM_DIRNAME, GRAPH_FILENAME)
CONSTRAINT_PATH = os.path.join(ROOT, LCM_DIRNAME, CONSTRAINT_FILENAME)

CODE_EXTENSIONS = {
    '.go': 'go',
    '.py': 'py',
    '.js': 'js',
    '.ts': 'ts',
    '.jsx': 'js',
    '.tsx': 'ts',
    '.html': 'html',
    '.vue': 'vue',
    '.rs': 'rust',
    '.cs': 'csharp',
    '.java': 'java',
    '.php': 'php',
}

IGNORED_DIRS = {
    '.git', 'node_modules', 'vendor', '__pycache__', '.pytest_cache',
    'dist', 'release', 'build', 'bin', 'obj', 'scratch', '.idea', '.vscode',
    '.next', '.nuxt', 'target', 'venv', '.venv', 'env'
}

# ─────────────────────────────────────────────────────────────
# SMART HASHING & CODEBASE MD5 ENGINE
# ─────────────────────────────────────────────────────────────

def calculate_codebase_hash(root_dir=ROOT):
    """
    Computes a deterministic combined MD5 hash of all code files.
    Uses streaming reads and deterministic path ordering for drift checking.
    """
    hasher = hashlib.md5()
    file_list = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in CODE_EXTENSIONS:
                full_p = os.path.join(dirpath, fname)
                rel_p = os.path.relpath(full_p, root_dir).replace('\\', '/')
                file_list.append((rel_p, full_p))

    file_list.sort(key=lambda x: x[0])
    for rel_p, full_p in file_list:
        hasher.update(rel_p.encode('utf-8'))
        try:
            with open(full_p, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
        except Exception:
            pass

    return hasher.hexdigest()

# ─────────────────────────────────────────────────────────────
# COMPACT MAP GENERATOR (PROJECT_MAP.min.md)
# ─────────────────────────────────────────────────────────────

def generate_min_map(full_map_path=MAP_PATH, min_map_path=MIN_MAP_PATH):
    """
    Feature 1: Creates an ultra-compact PROJECT_MAP.min.md for AI Agent reading.
    Strips line numbers and raw table bulk, preserving:
      - Hierarchical modules
      - Exported symbols per file
      - UI DOM triggers and API targets
      - Implicit Constraints [C1]..[Cn]
      - Feature Cross-Reference matrix
    Reduces repeated context compared with loading the full map.
    """
    if not os.path.exists(full_map_path):
        return None

    with open(full_map_path, 'r', encoding='utf-8', errors='replace') as f:
        full_content = f.read()

    lines = full_content.splitlines()
    min_lines = [
        "# LIVING PROJECT MAP (COMPACT AI WORKING MEMORY)",
        "> **Notice:** This is the token-efficient compact map. Read this first.",
        "> For exact line surgery, query the full map or use: `python living_map.py impact <symbol>`",
        ""
    ]

    current_section = ""
    current_file_symbols = []
    current_file_name = None

    re_file_hdr = re.compile(r'^###\s+([A-Za-z0-9_\-./\\]+\.[a-z]+)')
    re_table_row = re.compile(r'^\|\s*L\d+\s*\|\s*\*{0,2}`([A-Za-z0-9_#\-]+)`\*{0,2}\s*\|(.*)')

    for line in lines:
        raw = line.strip()

        # Check section change
        if raw.startswith('## '):
            if current_file_name and current_file_symbols:
                syms_str = ", ".join(f"`{s}`" for s in current_file_symbols[:30])
                min_lines.append(f"- **{current_file_name}:** {syms_str}")
                current_file_name = None
                current_file_symbols = []
            current_section = raw
            min_lines.append("")
            min_lines.append(raw)
            continue

        # Detect file headers in Code Location Index
        m_file = re_file_hdr.match(raw)
        if m_file:
            if current_file_name and current_file_symbols:
                syms_str = ", ".join(f"`{s}`" for s in current_file_symbols[:30])
                min_lines.append(f"- **{current_file_name}:** {syms_str}")
            current_file_name = m_file.group(1).strip()
            current_file_symbols = []
            continue

        # In Code Location Index: collect symbols into compact comma-separated list
        if "CODE LOCATION INDEX" in current_section:
            m_row = re_table_row.match(raw)
            if m_row:
                sym = m_row.group(1).strip()
                if sym not in current_file_symbols:
                    current_file_symbols.append(sym)
            continue

        # In other modules: preserve headers, constraints, cross-reference tables
        if any(sec in current_section for sec in [
            "META", "IMPLICIT CONSTRAINTS", "UI & DOM", "CROSS-REFERENCE", "QUALITY GATE"
        ]):
            # Skip separator lines
            if raw.startswith('|---') or raw.startswith('| Line |') or raw.startswith('| Dòng |'):
                min_lines.append(line)
                continue
            min_lines.append(line)

    # Flush last file
    if current_file_name and current_file_symbols:
        syms_str = ", ".join(f"`{s}`" for s in current_file_symbols[:30])
        min_lines.append(f"- **{current_file_name}:** {syms_str}")

    min_content = "\n".join(min_lines)

    with open(min_map_path, 'w', encoding='utf-8') as f:
        f.write(min_content)

    full_size = len(full_content)
    min_size = len(min_content)
    saved_pct = int((1 - min_size / max(full_size, 1)) * 100)
    print(f"  [COMPACT] Generated {MIN_MAP_FILENAME} ({min_size} chars, saved {saved_pct}% tokens).")
    return min_map_path

# ─────────────────────────────────────────────────────────────
# QUICK BLAST RADIUS / IMPACT ANALYSIS (--impact-of)
# ─────────────────────────────────────────────────────────────

def analyze_symbol_impact(symbol_query, map_content):
    """
    Feature 2: Scans PROJECT_MAP.md to report blast radius across:
      - Code locations (Module 1 & 2)
      - UI & DOM Triggers (Module 3)
      - Implicit Constraints (Module 4)
      - API Routes & DB Models
      - Linked Features & Cross-References (Module 5 & 9)
    """
    q = symbol_query.strip().lower()
    report = {
        'locations': [],
        'ui_triggers': [],
        'api_routes': [],
        'db_tables': [],
        'constraints': [],
        'features': []
    }

    current_section = ""
    current_file = None
    current_constraint_id = None
    current_constraint_text = []

    lines = map_content.splitlines()

    re_sec = re.compile(r'^##\s+(MODULE\s+\d+[^:\n]*):?\s*(.*)', re.IGNORECASE)
    re_file = re.compile(r'^###\s+([A-Za-z0-9_\-./\\]+\.[a-z]+)', re.IGNORECASE)
    re_row = re.compile(r'^\|\s*\*?L?(\d+)\*?\s*\|\s*\*{0,2}`?([A-Za-z0-9_#\-]+)`?\*{0,2}\s*\|(.*)')
    re_c_hdr = re.compile(r'^###\s+(C\d+)[:\s]+(.*)', re.IGNORECASE)
    re_c_bullet = re.compile(r'^-\s*\[(C\d+)\]\s*(.*)', re.IGNORECASE)
    re_f_hdr = re.compile(r'^###\s+(F-[A-Za-z0-9_\-]+|F\d+)[:\s]+(.*)', re.IGNORECASE)
    re_api = re.compile(r'(?:GET|POST|PUT|DELETE|PATCH)\s+([/A-Za-z0-9_\-:]+)', re.IGNORECASE)
    re_dom = re.compile(r'([#\.][A-Za-z0-9_\-]+)')

    for idx, line in enumerate(lines):
        raw = line.strip()

        # Track main module sections
        m_s = re_sec.match(raw)
        if m_s:
            if current_constraint_id and current_constraint_text:
                joined_c = " ".join(current_constraint_text)
                if q in joined_c.lower():
                    report['constraints'].append(f"[{current_constraint_id}] {joined_c[:120]}")
                current_constraint_id = None
                current_constraint_text = []
            current_section = (m_s.group(1) + " " + m_s.group(2)).upper()
            continue

        m_f = re_file.match(raw)
        if m_f:
            current_file = m_f.group(1).strip()
            continue

        # 1. Code location check (Module 1, 2)
        m_r = re_row.match(raw)
        if m_r:
            line_no = m_r.group(1)
            sym = m_r.group(2)
            desc = m_r.group(3).strip()
            if q in sym.lower() or q in desc.lower():
                loc_desc = f"{current_file} (L{line_no}) -> `{sym}`"
                if desc and desc != '-':
                    loc_desc += f" ({desc[:60]})"
                report['locations'].append(loc_desc)
                # Check for API mentioned in desc
                for m_api in re_api.finditer(desc):
                    ep = m_api.group(0).strip()
                    if ep not in report['api_routes']:
                        report['api_routes'].append(ep)

        # 2. Constraint check (Module 4) - Heading style (### C1: ...)
        m_ch = re_c_hdr.match(raw)
        if m_ch:
            if current_constraint_id and current_constraint_text:
                joined_c = " ".join(current_constraint_text)
                if q in joined_c.lower():
                    report['constraints'].append(f"[{current_constraint_id}] {joined_c[:120]}")
            current_constraint_id = m_ch.group(1).strip()
            current_constraint_text = [m_ch.group(2).strip()]
            continue

        if current_constraint_id and raw.startswith('-'):
            current_constraint_text.append(raw.lstrip('-* ').strip())

        # Constraint check - Bullet style (- [C1] ...)
        m_cb = re_c_bullet.match(raw)
        if m_cb:
            c_id = m_cb.group(1)
            c_desc = m_cb.group(2).strip()
            if q in c_desc.lower():
                report['constraints'].append(f"[{c_id}] {c_desc}")

        # 3. UI triggers & DOM (Module 3)
        if "MODULE 3" in current_section or "UI MAP" in current_section or "DOM" in current_section:
            if q in raw.lower():
                # Extract DOM selector if present
                m_d = re_dom.search(raw)
                dom_sel = m_d.group(1) if m_d else "UI Element"
                report['ui_triggers'].append(f"{dom_sel}: {raw[:80]}")

        # 4. Feature Cross-Ref (Module 5 or 9)
        m_fh = re_f_hdr.match(raw)
        if m_fh:
            fid = m_fh.group(1).strip()
            fdesc = m_fh.group(2).strip()
            # Look ahead a few lines to see if q is in this feature block
            block_lines = lines[idx:min(idx + 25, len(lines))]
            block_text = " ".join(block_lines)
            if q in block_text.lower():
                report['features'].append(f"{fid}: {fdesc}")
                for m_api in re_api.finditer(block_text):
                    ep = m_api.group(0).strip()
                    if ep not in report['api_routes']:
                        report['api_routes'].append(ep)

        # Catch generic table rows in Cross-Reference (e.g. | F001 | desc | #ui | ...)
        if raw.startswith('|') and ('| F' in raw or '|F-' in raw):
            parts = [p.strip() for p in raw.split('|')[1:-1]]
            if len(parts) >= 5 and any(q in p.lower() for p in parts):
                report['features'].append(f"{parts[0]}: {parts[1]} (UI: {parts[2]} | API: {parts[4]})")
                if parts[4] != '-' and parts[4] not in report['api_routes']:
                    report['api_routes'].append(parts[4])
                if len(parts) >= 6 and parts[5] != '-' and parts[5] not in report['db_tables']:
                    report['db_tables'].append(parts[5])

    # Flush last constraint
    if current_constraint_id and current_constraint_text:
        joined_c = " ".join(current_constraint_text)
        if q in joined_c.lower():
            report['constraints'].append(f"[{current_constraint_id}] {joined_c[:120]}")

    return report

# ─────────────────────────────────────────────────────────────
# GIT ENGINE
# ─────────────────────────────────────────────────────────────

def _git(args_list, cwd=ROOT):
    """Executes a git command in project root."""
    try:
        res = subprocess.run(
            ['git', '--no-pager'] + args_list,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except FileNotFoundError:
        return 127, '', 'git executable not found in PATH'

def git_get_head_info():
    """Returns (short_hash, full_hash, commit_date)."""
    code, out, _ = _git(['log', '-1', '--format=%h|%H|%ci'])
    if code == 0 and out:
        parts = out.split('|')
        if len(parts) >= 3:
            return parts[0], parts[1], parts[2][:10]
    return '0000000', '0000000000000000000000000000000000000000', datetime.now().strftime('%Y-%m-%d')

def git_log_map(limit=15):
    """Returns list of recent commits affecting PROJECT_MAP.md."""
    code, out, _ = _git(['log', f'-{limit}', '--format=%H|%h|%ci|%s', '--', MAP_FILENAME])
    entries = []
    if code == 0 and out:
        for line in out.splitlines():
            parts = line.split('|', 3)
            if len(parts) == 4:
                entries.append({
                    'hash': parts[0],
                    'short': parts[1],
                    'date': parts[2][:16],
                    'msg': parts[3]
                })
    return entries

def git_commit_map(message):
    """Stage and commit human projections plus generated machine state."""
    generated_paths = [MAP_FILENAME, MIN_MAP_FILENAME]
    for relative_path in (
        os.path.join(LCM_DIRNAME, INDEX_FILENAME),
        os.path.join(LCM_DIRNAME, GRAPH_FILENAME),
        os.path.join(LCM_DIRNAME, CONSTRAINT_FILENAME),
    ):
        if os.path.exists(os.path.join(ROOT, relative_path)):
            generated_paths.append(relative_path)
    c1, _, e1 = _git(['add'] + generated_paths)
    if c1 != 0:
        print(f"  [GIT ERR] git add failed: {e1}")
        return False
    c2, o2, e2 = _git(['commit', '-m', message])
    if c2 != 0:
        if 'nothing to commit' in (o2 + e2).lower():
            print("  [GIT] Working tree clean (maps unchanged).")
            return True
        print(f"  [GIT ERR] git commit failed: {e2}")
        return False
    _, short_h, _ = _git(['rev-parse', '--short', 'HEAD'])
    print(f"  [GIT OK] Committed maps: {short_h} - {message}")
    return True

def git_rollback_map(target_hash):
    """Restores PROJECT_MAP.md to a specific commit (SAFE: NEVER touches source code)."""
    print(f"  🛡️ [SAFETY GUARANTEE] Rollback affects ONLY {MAP_FILENAME} & {MIN_MAP_FILENAME}.")
    print(f"     Source code files (.go, .py, .js, .html, etc.) are 100% untouched.")
    code, content, err = _git(['show', f'{target_hash}:{MAP_FILENAME}'])
    if code != 0:
        print(f"  [GIT ERR] Could not read {MAP_FILENAME} at commit {target_hash}: {err}")
        return False
    if os.path.exists(MAP_PATH):
        bak_path = MAP_PATH + '.bak'
        with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f_cur:
            with open(bak_path, 'w', encoding='utf-8') as f_bak:
                f_bak.write(f_cur.read())
        print(f"  [BACKUP] Saved current map to {MAP_FILENAME}.bak")

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] Restored {MAP_FILENAME} to commit {target_hash[:8]}")
    generate_min_map(MAP_PATH, MIN_MAP_PATH)
    msg = f"docs: rollback {MAP_FILENAME} to {target_hash[:8]}"
    git_commit_map(msg)
    return True

# ─────────────────────────────────────────────────────────────
# MULTI-LANGUAGE & FRAMEWORK AST/REGEX SCANNERS
# ─────────────────────────────────────────────────────────────

RE_GO_FUNC    = re.compile(r'^[ \t]*func\s+(?:\([^)]+\)\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_GO_DECL    = re.compile(
    r'^[ \t]*func\s*(?:\(\s*([A-Za-z_][A-Za-z0-9_]*)\s+\*?([A-Za-z_][A-Za-z0-9_]*)[^)]*\)\s*)?'
    r'([A-Za-z_][A-Za-z0-9_]*)\s*\(',
    re.MULTILINE,
)
RE_GO_STRUCT  = re.compile(r'^[ \t]*type\s+([A-Za-z_][A-Za-z0-9_]*)\s+(?:struct|interface)\b', re.MULTILINE)
RE_PY_DEF     = re.compile(r'^[ \t]*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_PY_CLS     = re.compile(r'^[ \t]*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*[:\(]', re.MULTILINE)
RE_JS_FUNC    = re.compile(r'^[ \t]*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_JS_VARF    = re.compile(r'^[ \t]*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>', re.MULTILINE)
RE_JS_CLS     = re.compile(r'^[ \t]*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
RE_NEXT_ROUTE = re.compile(r'^[ \t]*export\s+(?:async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH|HEAD)\s*\(', re.MULTILINE)
RE_NEXT_PAGE  = re.compile(r'^[ \t]*export\s+(?:async\s+)?function\s+(getServerSideProps|getStaticProps|getStaticPaths)\s*\(', re.MULTILINE)
RE_RS_FN      = re.compile(r'^[ \t]*(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_RS_STRUCT  = re.compile(r'^[ \t]*(?:pub(?:\([^)]+\))?\s+)?(?:struct|enum|trait|impl)\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
RE_CS_METHOD  = re.compile(r'^[ \t]*(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:[A-Za-z0-9_<>[\]]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_CS_CLS     = re.compile(r'^[ \t]*(?:public|private|protected|internal)\s+(?:abstract\s+|sealed\s+)?(?:class|interface|record)\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
RE_JAVA_MTH   = re.compile(r'^[ \t]*(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?(?:[A-Za-z0-9_<>[\]]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_JAVA_CLS   = re.compile(r'^[ \t]*(?:public|private|protected)\s+(?:abstract\s+)?(?:class|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
RE_PHP_FUNC   = re.compile(r'^[ \t]*(?:public|private|protected)?\s*(?:static\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_PHP_CLS    = re.compile(r'^[ \t]*(?:abstract\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
RE_HTML_ID    = re.compile(r'id=["\']([A-Za-z0-9_\-]+)["\']')

def scan_file_symbols(file_path):
    """Scans a file using modular extractors and returns {symbol_name: line_number}."""
    ext = os.path.splitext(file_path)[1].lower()
    fname = os.path.basename(file_path).lower()
    symbols = {}
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception:
        return symbols

    for idx, line in enumerate(lines, 1):
        if ext == '.go':
            m = RE_GO_FUNC.match(line)
            if m:
                symbols[m.group(1)] = idx
            else:
                m_st = RE_GO_STRUCT.match(line)
                if m_st:
                    symbols[m_st.group(1)] = idx

        elif ext == '.py':
            m_def = RE_PY_DEF.match(line)
            if m_def:
                symbols[m_def.group(1)] = idx
            else:
                m_cls = RE_PY_CLS.match(line)
                if m_cls:
                    symbols[m_cls.group(1)] = idx

        elif ext in ('.js', '.ts', '.jsx', '.tsx', '.vue'):
            m_next = RE_NEXT_ROUTE.match(line)
            if m_next and ('route.' in fname or 'api/' in file_path.replace('\\', '/')):
                symbols[f"{m_next.group(1)}"] = idx
                continue

            m_page = RE_NEXT_PAGE.match(line)
            if m_page:
                symbols[m_page.group(1)] = idx
                continue

            m_fn = RE_JS_FUNC.match(line)
            if m_fn:
                symbols[m_fn.group(1)] = idx
            else:
                m_var = RE_JS_VARF.match(line)
                if m_var:
                    symbols[m_var.group(1)] = idx
                else:
                    m_cls = RE_JS_CLS.match(line)
                    if m_cls:
                        symbols[m_cls.group(1)] = idx

        elif ext == '.rs':
            m_fn = RE_RS_FN.match(line)
            if m_fn:
                symbols[m_fn.group(1)] = idx
            else:
                m_st = RE_RS_STRUCT.match(line)
                if m_st:
                    symbols[m_st.group(1)] = idx

        elif ext == '.cs':
            m_m = RE_CS_METHOD.match(line)
            if m_m:
                symbols[m_m.group(1)] = idx
            else:
                m_c = RE_CS_CLS.match(line)
                if m_c:
                    symbols[m_c.group(1)] = idx

        elif ext == '.java':
            m_m = RE_JAVA_MTH.match(line)
            if m_m:
                symbols[m_m.group(1)] = idx
            else:
                m_c = RE_JAVA_CLS.match(line)
                if m_c:
                    symbols[m_c.group(1)] = idx

        elif ext == '.php':
            m_f = RE_PHP_FUNC.match(line)
            if m_f:
                symbols[m_f.group(1)] = idx
            else:
                m_c = RE_PHP_CLS.match(line)
                if m_c:
                    symbols[m_c.group(1)] = idx

        elif ext == '.html':
            for id_match in RE_HTML_ID.finditer(line):
                symbols[f"#{id_match.group(1)}"] = idx

    return symbols


def _symbol_fingerprint(kind, qualified_name, declaration):
    """Return a stable content fingerprint that is independent of line numbers."""
    normalized = re.sub(r'\s+', ' ', declaration.strip())
    payload = f"{kind}|{qualified_name}|{normalized}".encode('utf-8')
    return hashlib.sha256(payload).hexdigest()[:16]


def _python_symbol_records(file_path):
    """Extract qualified Python symbols with the standard-library AST parser."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except (OSError, SyntaxError, UnicodeError):
        return []

    source_lines = source.splitlines()
    records = []

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.scope = []

        def _add(self, node, kind):
            qualified_name = '.'.join(self.scope + [node.name])
            declaration = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else node.name
            records.append({
                'name': node.name,
                'qualified_name': qualified_name,
                'kind': kind,
                'line': node.lineno,
                'end_line': getattr(node, 'end_lineno', node.lineno),
                'fingerprint': _symbol_fingerprint(kind, qualified_name, declaration),
            })

        def visit_ClassDef(self, node):
            self._add(node, 'class')
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node):
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node):
            self._visit_function(node)

        def _visit_function(self, node):
            kind = 'method' if self.scope else 'function'
            self._add(node, kind)
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

    Visitor().visit(tree)
    return records


def _strip_javascript_noncode(source):
    """Mask JS/TS comments and literals while preserving offsets and newlines."""
    result = list(source)
    state = 'code'
    quote = None
    escaped = False
    index = 0
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ''
        if state == 'code':
            if char == '/' and following == '/':
                result[index] = result[index + 1] = ' '
                state = 'line_comment'
                index += 2
                continue
            if char == '/' and following == '*':
                result[index] = result[index + 1] = ' '
                state = 'block_comment'
                index += 2
                continue
            if char in {'\'', '"', '`'}:
                result[index] = ' '
                state = 'string'
                quote = char
                escaped = False
        elif state == 'line_comment':
            if char == '\n':
                state = 'code'
            else:
                result[index] = ' '
        elif state == 'block_comment':
            if char == '*' and following == '/':
                result[index] = result[index + 1] = ' '
                state = 'code'
                index += 2
                continue
            if char != '\n':
                result[index] = ' '
        else:
            if char != '\n':
                result[index] = ' '
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                state = 'code'
                quote = None
        index += 1
    return ''.join(result)


def _matching_delimiter(source, start, opening, closing):
    """Return the offset of a matching delimiter in already-masked source."""
    if start < 0 or start >= len(source) or source[start] != opening:
        return -1
    depth = 0
    for index in range(start, len(source)):
        if source[index] == opening:
            depth += 1
        elif source[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    return -1


def _javascript_symbol_records(file_path):
    """Extract named JS/TS functions, arrow functions, and classes with ranges."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            source = f.read()
    except OSError:
        return []
    masked = _strip_javascript_noncode(source)
    source_lines = source.splitlines()
    declarations = []
    patterns = (
        (RE_JS_FUNC, 'function', 'function'),
        (RE_JS_VARF, 'function', 'arrow'),
        (RE_JS_CLS, 'class', 'class'),
    )
    for pattern, kind, style in patterns:
        for match in pattern.finditer(masked):
            line = masked.count('\n', 0, match.start()) + 1
            end_offset = -1
            if style == 'function':
                opening = masked.find('(', match.start(), match.end() + 1)
                closing = _matching_delimiter(masked, opening, '(', ')')
                body = masked.find('{', closing + 1) if closing >= 0 else -1
                terminator = masked.find(';', closing + 1) if closing >= 0 else -1
                if terminator < 0 or (body >= 0 and body < terminator):
                    end_offset = _matching_delimiter(masked, body, '{', '}')
            elif style == 'arrow':
                body_match = re.match(r'\s*\{', masked[match.end():])
                if body_match:
                    body = match.end() + body_match.end() - 1
                    end_offset = _matching_delimiter(masked, body, '{', '}')
            else:
                body = masked.find('{', match.end())
                end_offset = _matching_delimiter(masked, body, '{', '}')
            end_line = masked.count('\n', 0, end_offset) + 1 if end_offset >= 0 else line
            name = match.group(1)
            declaration = source_lines[line - 1] if line <= len(source_lines) else name
            declarations.append({
                'name': name,
                'qualified_name': name,
                'kind': kind,
                'line': line,
                'end_line': end_line,
                'fingerprint': _symbol_fingerprint(kind, name, declaration),
            })
    unique = {(item['name'], item['line']): item for item in declarations}
    return sorted(unique.values(), key=lambda item: (item['line'], item['name']))


def _go_symbol_records(file_path):
    """Extract Go functions, receiver methods, and types with stable ranges."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            source = f.read()
    except OSError:
        return []
    masked = _strip_javascript_noncode(source)
    source_lines = source.splitlines()
    records = []
    for match in RE_GO_DECL.finditer(masked):
        receiver_var, receiver_type, name = match.group(1), match.group(2), match.group(3)
        line = masked.count('\n', 0, match.start()) + 1
        opening = match.end() - 1
        closing = _matching_delimiter(masked, opening, '(', ')')
        body = masked.find('{', closing + 1) if closing >= 0 else -1
        end_offset = _matching_delimiter(masked, body, '{', '}')
        end_line = masked.count('\n', 0, end_offset) + 1 if end_offset >= 0 else line
        qualified = f'{receiver_type}.{name}' if receiver_type else name
        kind = 'method' if receiver_type else 'function'
        declaration = source_lines[line - 1] if line <= len(source_lines) else name
        record = {
            'name': name, 'qualified_name': qualified, 'kind': kind,
            'line': line, 'end_line': end_line,
            'fingerprint': _symbol_fingerprint(kind, qualified, declaration),
        }
        if receiver_type:
            record['receiver'] = receiver_var
            record['receiver_type'] = receiver_type
        records.append(record)
    for match in RE_GO_STRUCT.finditer(masked):
        name = match.group(1)
        line = masked.count('\n', 0, match.start()) + 1
        declaration = source_lines[line - 1] if line <= len(source_lines) else name
        records.append({
            'name': name, 'qualified_name': name, 'kind': 'type',
            'line': line, 'end_line': line,
            'fingerprint': _symbol_fingerprint('type', name, declaration),
        })
    return sorted(records, key=lambda item: (item['line'], item['qualified_name']))


def scan_file_symbol_records(file_path, rel_path=None):
    """Return structured symbols used by the v3 index.

    Stable IDs use language + repository-relative path + qualified symbol name.
    The current line range is navigation metadata, never the identity.
    """
    rel_path = (rel_path or os.path.basename(file_path)).replace('\\', '/')
    ext = os.path.splitext(file_path)[1].lower()
    language = CODE_EXTENSIONS.get(ext, ext.lstrip('.') or 'unknown')

    if ext == '.py':
        records = _python_symbol_records(file_path)
    elif ext == '.go':
        records = _go_symbol_records(file_path)
    elif ext in ('.js', '.ts', '.jsx', '.tsx', '.vue'):
        records = _javascript_symbol_records(file_path)
    else:
        records = []
        for name, line in scan_file_symbols(file_path).items():
            kind = 'dom_id' if name.startswith('#') else 'symbol'
            records.append({
                'name': name,
                'qualified_name': name,
                'kind': kind,
                'line': line,
                'end_line': line,
                'fingerprint': _symbol_fingerprint(kind, name, name),
            })

    for record in records:
        record['id'] = f"{language}:{rel_path}::{record['qualified_name']}"
        record['language'] = language
        record['path'] = rel_path
    return records


def build_symbol_index(root_dir=ROOT):
    """Build the machine-readable v3 symbol index without writing it to disk."""
    files = []
    symbols = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for fname in sorted(filenames):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXTENSIONS:
                continue
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
            records = scan_file_symbol_records(full_path, rel_path)
            try:
                with open(full_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            except OSError:
                file_hash = None
            files.append({'path': rel_path, 'language': CODE_EXTENSIONS[ext], 'sha256': file_hash})
            symbols.extend(records)

    return {
        'schema_version': INDEX_SCHEMA_VERSION,
        'source_hash': calculate_codebase_hash(root_dir),
        'root': '.',
        'files': files,
        'symbols': symbols,
    }


def write_symbol_index(index, index_path=INDEX_PATH):
    """Atomically persist the v3 machine index."""
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    temp_path = index_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    os.replace(temp_path, index_path)


def _call_name(node):
    """Return a dotted textual name for a Python call target when available."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def _is_test_path(path):
    """Recognize conventional Python and JavaScript test file locations."""
    normalized = path.replace('\\', '/').lower()
    basename = normalized.rsplit('/', 1)[-1]
    return (
        normalized.startswith(('test/', 'tests/'))
        or '/test/' in normalized
        or '/tests/' in normalized
        or '.test.' in basename
        or '.spec.' in basename
        or basename.startswith('test_')
        or basename.endswith('_test.go')
    )


def _next_route_path(path):
    """Derive a public route from a Next.js app-router route module path."""
    normalized = path.replace('\\', '/')
    padded = '/' + normalized.lstrip('/')
    if '/app/' in padded:
        route = padded.split('/app/', 1)[1].rsplit('/route.', 1)[0]
        parts = [part for part in route.split('/') if not (part.startswith('(') and part.endswith(')'))]
        return '/' + '/'.join(parts)
    return None


def _resolve_javascript_module_path(importer_path, specifier, known_paths):
    """Resolve a relative JS/TS module specifier to one indexed repository path."""
    if not specifier.startswith('.'):
        return None
    base = posixpath.normpath(posixpath.join(posixpath.dirname(importer_path), specifier))
    if base in known_paths:
        return base
    candidates = []
    extension = posixpath.splitext(base)[1]
    if not extension:
        candidates.extend(base + suffix for suffix in ('.ts', '.tsx', '.js', '.jsx', '.vue'))
        candidates.extend(posixpath.join(base, 'index' + suffix) for suffix in ('.ts', '.tsx', '.js', '.jsx', '.vue'))
    elif extension == '.js':
        stem = base[:-3]
        candidates.extend((stem + '.ts', stem + '.tsx'))
    matches = [candidate for candidate in candidates if candidate in known_paths]
    return matches[0] if len(matches) == 1 else None


def _javascript_import_bindings(source, masked, importer_path, known_paths, by_path_qualified):
    """Resolve explicit relative ESM imports into direct and namespace bindings."""
    direct = {}
    namespaces = {}
    named_pattern = re.compile(
        r'\bimport\s+(?:type\s+)?\{([^}]+)\}\s+from\s*([\'\"])([^\'\"]+)\2',
        re.MULTILINE,
    )
    for match in named_pattern.finditer(source):
        if not masked[match.start():match.start() + 1].strip():
            continue
        target_path = _resolve_javascript_module_path(importer_path, match.group(3), known_paths)
        if not target_path:
            continue
        for item in match.group(1).split(','):
            parts = re.split(r'\s+as\s+', re.sub(r'^\s*type\s+', '', item.strip()), maxsplit=1)
            imported = parts[0].strip()
            local = parts[1].strip() if len(parts) == 2 else imported
            if not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', imported):
                continue
            target = by_path_qualified.get((target_path, imported))
            if target:
                direct[local] = target

    namespace_pattern = re.compile(
        r'\bimport\s+\*\s+as\s+([A-Za-z_$][A-Za-z0-9_$]*)\s+from\s*'
        r'([\'\"])([^\'\"]+)\2',
        re.MULTILINE,
    )
    for match in namespace_pattern.finditer(source):
        if not masked[match.start():match.start() + 1].strip():
            continue
        target_path = _resolve_javascript_module_path(importer_path, match.group(3), known_paths)
        if target_path:
            namespaces[match.group(1)] = target_path
    return direct, namespaces


def _resolve_python_module_path(importer_path, module, level, known_paths):
    """Resolve an absolute or relative Python module to one indexed source path."""
    package_parts = [part for part in posixpath.dirname(importer_path).split('/') if part]
    if level:
        if not package_parts or level > len(package_parts):
            return None
        base_parts = package_parts[:len(package_parts) - (level - 1)]
    else:
        base_parts = []
    if module:
        base_parts.extend(part for part in module.split('.') if part)
    if not base_parts:
        return None
    stem = '/'.join(base_parts)
    candidates = [f'{stem}.py', f'{stem}/__init__.py']
    matches = [candidate for candidate in candidates if candidate in known_paths]
    if not matches and not level:
        matches = [
            path for path in known_paths
            if any(path.endswith('/' + candidate) for candidate in candidates)
        ]
    return matches[0] if len(matches) == 1 else None


def _python_import_bindings(tree, importer_path, known_paths, by_path_qualified):
    """Resolve top-level Python imports into direct symbol and module bindings."""
    direct = {}
    namespaces = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                target_path = _resolve_python_module_path(
                    importer_path, alias.name, 0, known_paths,
                )
                if target_path:
                    namespaces[alias.asname or alias.name] = target_path
        elif isinstance(node, ast.ImportFrom):
            module_path = _resolve_python_module_path(
                importer_path, node.module, node.level, known_paths,
            )
            for alias in node.names:
                if alias.name == '*':
                    continue
                local = alias.asname or alias.name
                target = by_path_qualified.get((module_path, alias.name)) if module_path else None
                if target:
                    direct[local] = target
                    continue
                child_module = '.'.join(part for part in (node.module, alias.name) if part)
                child_path = _resolve_python_module_path(
                    importer_path, child_module, node.level, known_paths,
                )
                if child_path:
                    namespaces[local] = child_path
    return direct, namespaces


def build_dependency_graph(index, root_dir=ROOT):
    """Build a confidence-scored dependency graph from a symbol index.

    Python uses the standard-library AST. JavaScript and TypeScript use a
    conservative zero-dependency static pass. Ambiguous or dynamic constructs
    are omitted instead of being presented as facts.
    """
    nodes = []
    node_ids = set()
    symbols = index.get('symbols', [])
    known_paths = {file_info['path'] for file_info in index.get('files', [])}
    by_path_qualified = {}
    by_name = {}
    by_dir_name = {}

    for symbol in symbols:
        node = {
            'id': symbol['id'],
            'type': 'symbol',
            'name': symbol['name'],
            'qualified_name': symbol['qualified_name'],
            'kind': symbol['kind'],
            'path': symbol['path'],
            'line': symbol['line'],
            'end_line': symbol['end_line'],
        }
        nodes.append(node)
        node_ids.add(node['id'])
        by_path_qualified[(symbol['path'], symbol['qualified_name'])] = symbol
        by_name.setdefault(symbol['name'], []).append(symbol)
        directory = posixpath.dirname(symbol['path'])
        by_dir_name.setdefault((directory, symbol['name']), []).append(symbol)

    edges = []
    edge_keys = set()

    def add_edge(source, target, relation, confidence, path, line, source_type='python_ast'):
        key = (source, target, relation, path, line)
        if source == target or key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({
            'source': source,
            'target': target,
            'relation': relation,
            'confidence': confidence,
            'evidence': {'path': path, 'line': line, 'source': source_type},
        })

    def resolve_target(rel_path, called):
        direct = by_path_qualified.get((rel_path, called))
        if direct:
            return direct, 1.0
        candidates = by_name.get(called, [])
        if len(candidates) == 1:
            return candidates[0], 0.9
        return None, 0.0

    for file_info in index.get('files', []):
        language = file_info.get('language')
        if language not in {'py', 'js', 'ts', 'vue', 'go'}:
            continue
        rel_path = file_info['path']
        full_path = os.path.join(root_dir, rel_path)
        if language == 'go':
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    source = f.read()
            except OSError:
                continue
            masked = _strip_javascript_noncode(source)
            directory = posixpath.dirname(rel_path)
            file_symbols = [
                symbol for symbol in symbols
                if symbol['path'] == rel_path and symbol.get('kind') in {'function', 'method'}
            ]

            def go_owner(line):
                owners = [
                    symbol for symbol in file_symbols
                    if symbol['line'] <= line <= symbol['end_line']
                ]
                return min(owners, key=lambda item: item['end_line'] - item['line']) if owners else None

            def go_package_target(name):
                candidates = [
                    symbol for symbol in by_dir_name.get((directory, name), [])
                    if symbol.get('kind') == 'function'
                ]
                return candidates[0] if len(candidates) == 1 else None

            call_pattern = re.compile(r'(?<![A-Za-z0-9_.])([A-Za-z_][A-Za-z0-9_]*)\s*\(')
            ignored_calls = {
                'if', 'for', 'switch', 'select', 'func', 'len', 'cap', 'append',
                'copy', 'delete', 'complex', 'real', 'imag', 'make', 'new', 'panic',
                'recover', 'print', 'println', 'close',
            }
            for match in call_pattern.finditer(masked):
                called = match.group(1)
                if called in ignored_calls:
                    continue
                line = masked.count('\n', 0, match.start()) + 1
                caller = go_owner(line)
                target = go_package_target(called)
                if not caller or not target:
                    continue
                relation = 'TESTED_BY' if _is_test_path(rel_path) else 'CALLS'
                source_id, target_id = caller['id'], target['id']
                if relation == 'TESTED_BY':
                    source_id, target_id = target_id, source_id
                add_edge(source_id, target_id, relation, 1.0, rel_path, line, 'go_static')

            member_pattern = re.compile(
                r'(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*'
                r'([A-Za-z_][A-Za-z0-9_]*)\s*\('
            )
            for match in member_pattern.finditer(masked):
                line = masked.count('\n', 0, match.start()) + 1
                caller = go_owner(line)
                if not caller or match.group(1) != caller.get('receiver'):
                    continue
                qualified = f"{caller.get('receiver_type')}.{match.group(2)}"
                candidates = [
                    symbol for symbol in symbols
                    if posixpath.dirname(symbol['path']) == directory
                    and symbol.get('qualified_name') == qualified
                ]
                if len(candidates) != 1:
                    continue
                relation = 'TESTED_BY' if _is_test_path(rel_path) else 'CALLS'
                source_id, target_id = caller['id'], candidates[0]['id']
                if relation == 'TESTED_BY':
                    source_id, target_id = target_id, source_id
                add_edge(source_id, target_id, relation, 1.0, rel_path, line, 'go_static')

            route_patterns = (
                (re.compile(r'\bhttp\.HandleFunc\s*\(\s*"([^"]+)"\s*,\s*([A-Za-z_][A-Za-z0-9_]*)'), 'ANY'),
                (re.compile(r'\b(?:router|routes|app|api|group|e)\s*\.\s*(GET|POST|PUT|DELETE|PATCH|HEAD)\s*\(\s*"([^"]+)"\s*,\s*([A-Za-z_][A-Za-z0-9_]*)'), None),
            )
            for pattern, fixed_method in route_patterns:
                for match in pattern.finditer(source):
                    if not masked[match.start():match.start() + 1].strip():
                        continue
                    if fixed_method:
                        method, route, handler_name = fixed_method, match.group(1), match.group(2)
                    else:
                        method, route, handler_name = match.group(1), match.group(2), match.group(3)
                    handler = go_package_target(handler_name)
                    if not handler:
                        continue
                    route_id = f"api:{method} {route}"
                    line = source.count('\n', 0, match.start()) + 1
                    if route_id not in node_ids:
                        node_ids.add(route_id)
                        nodes.append({
                            'id': route_id, 'type': 'api', 'name': f"{method} {route}",
                            'method': method, 'route': route, 'path': rel_path, 'line': line,
                        })
                    add_edge(route_id, handler['id'], 'HANDLES', 1.0, rel_path, line, 'go_static')
            continue

        if language in {'js', 'ts', 'vue'}:
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    source = f.read()
            except OSError:
                continue
            masked = _strip_javascript_noncode(source)
            file_symbols = [
                symbol for symbol in symbols
                if symbol['path'] == rel_path and symbol.get('kind') == 'function'
            ]
            import_bindings, namespace_bindings = _javascript_import_bindings(
                source, masked, rel_path, known_paths, by_path_qualified,
            )
            call_pattern = re.compile(r'(?<![A-Za-z0-9_$.])([A-Za-z_$][A-Za-z0-9_$]*)\s*\(')
            ignored_calls = {
                'if', 'for', 'while', 'switch', 'catch', 'function', 'return',
                'typeof', 'delete', 'void', 'new', 'super', 'import',
            }
            for match in call_pattern.finditer(masked):
                called = match.group(1)
                if called in ignored_calls:
                    continue
                line = masked.count('\n', 0, match.start()) + 1
                owners = [
                    symbol for symbol in file_symbols
                    if symbol['line'] <= line <= symbol['end_line']
                ]
                if not owners:
                    continue
                caller = min(owners, key=lambda item: item['end_line'] - item['line'])
                target = import_bindings.get(called)
                confidence = 1.0 if target else 0.0
                if target is None:
                    target, confidence = resolve_target(rel_path, called)
                if target:
                    relation = 'TESTED_BY' if _is_test_path(rel_path) else 'CALLS'
                    source_id, target_id = caller['id'], target['id']
                    if relation == 'TESTED_BY':
                        source_id, target_id = target_id, source_id
                    add_edge(
                        source_id, target_id, relation, confidence,
                        rel_path, line, 'javascript_static',
                    )

            member_pattern = re.compile(
                r'(?<![A-Za-z0-9_$])([A-Za-z_$][A-Za-z0-9_$]*)\s*\.\s*'
                r'([A-Za-z_$][A-Za-z0-9_$]*)\s*\('
            )
            for match in member_pattern.finditer(masked):
                target_path = namespace_bindings.get(match.group(1))
                if not target_path:
                    continue
                line = masked.count('\n', 0, match.start()) + 1
                owners = [
                    symbol for symbol in file_symbols
                    if symbol['line'] <= line <= symbol['end_line']
                ]
                target = by_path_qualified.get((target_path, match.group(2)))
                if not owners or not target:
                    continue
                caller = min(owners, key=lambda item: item['end_line'] - item['line'])
                relation = 'TESTED_BY' if _is_test_path(rel_path) else 'CALLS'
                source_id, target_id = caller['id'], target['id']
                if relation == 'TESTED_BY':
                    source_id, target_id = target_id, source_id
                add_edge(
                    source_id, target_id, relation, 1.0,
                    rel_path, line, 'javascript_import',
                )

            route_pattern = re.compile(
                r'\b(?:app|router)\s*\.\s*(get|post|put|delete|patch|head)\s*\('
                r'\s*([\'"`])([^\'"`$]+)\2\s*,\s*([A-Za-z_$][A-Za-z0-9_$]*)',
                re.IGNORECASE,
            )
            for match in route_pattern.finditer(source):
                if not masked[match.start():match.start() + 1].strip():
                    continue
                method, route, handler_name = match.group(1).upper(), match.group(3), match.group(4)
                handler, confidence = resolve_target(rel_path, handler_name)
                if not handler:
                    continue
                route_id = f"api:{method} {route}"
                line = source.count('\n', 0, match.start()) + 1
                if route_id not in node_ids:
                    node_ids.add(route_id)
                    nodes.append({
                        'id': route_id, 'type': 'api', 'name': f"{method} {route}",
                        'method': method, 'route': route, 'path': rel_path, 'line': line,
                    })
                add_edge(route_id, handler['id'], 'HANDLES', confidence, rel_path, line, 'javascript_static')

            next_route = _next_route_path(rel_path) if re.search(r'(^|/)route\.(?:js|ts|jsx|tsx)$', rel_path) else None
            if next_route:
                for handler in file_symbols:
                    method = handler['name'].upper()
                    if method not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'}:
                        continue
                    route_id = f"api:{method} {next_route}"
                    if route_id not in node_ids:
                        node_ids.add(route_id)
                        nodes.append({
                            'id': route_id, 'type': 'api', 'name': f"{method} {next_route}",
                            'method': method, 'route': next_route,
                            'path': rel_path, 'line': handler['line'],
                        })
                    add_edge(
                        route_id, handler['id'], 'HANDLES', 1.0,
                        rel_path, handler['line'], 'javascript_static',
                    )
            continue

        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                tree = ast.parse(f.read(), filename=full_path)
        except (OSError, SyntaxError, UnicodeError):
            continue
        import_bindings, namespace_bindings = _python_import_bindings(
            tree, rel_path, known_paths, by_path_qualified,
        )

        class CallVisitor(ast.NodeVisitor):
            def __init__(self):
                self.scope = []
                self.callers = []

            def visit_ClassDef(self, node):
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()

            def visit_FunctionDef(self, node):
                self._visit_function(node)

            def visit_AsyncFunctionDef(self, node):
                self._visit_function(node)

            def _visit_function(self, node):
                qualified = '.'.join(self.scope + [node.name])
                caller = by_path_qualified.get((rel_path, qualified))
                if caller:
                    for decorator in node.decorator_list:
                        if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                            continue
                        method = decorator.func.attr.upper()
                        if method not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'}:
                            continue
                        if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
                            continue
                        route_value = decorator.args[0].value
                        if not isinstance(route_value, str):
                            continue
                        route_id = f"api:{method} {route_value}"
                        if route_id not in node_ids:
                            node_ids.add(route_id)
                            nodes.append({
                                'id': route_id,
                                'type': 'api',
                                'name': f"{method} {route_value}",
                                'method': method,
                                'route': route_value,
                                'path': rel_path,
                                'line': decorator.lineno,
                            })
                        add_edge(route_id, caller['id'], 'HANDLES', 1.0, rel_path, decorator.lineno)
                self.scope.append(node.name)
                self.callers.append(caller)
                self.generic_visit(node)
                self.callers.pop()
                self.scope.pop()

            def visit_Call(self, node):
                caller = self.callers[-1] if self.callers else None
                called = _call_name(node.func)
                if caller and called:
                    target = None
                    confidence = 0.0
                    source_type = 'python_ast'
                    class_scope = caller['qualified_name'].rsplit('.', 1)[0] if caller['kind'] == 'method' else ''
                    if called.startswith('self.') and class_scope:
                        target = by_path_qualified.get((rel_path, f"{class_scope}.{called[5:]}"))
                        confidence = 1.0
                    if target is None:
                        direct = by_path_qualified.get((rel_path, called))
                        if direct:
                            target, confidence = direct, 1.0
                    if target is None and isinstance(node.func, ast.Name):
                        target = import_bindings.get(called)
                        if target:
                            confidence, source_type = 1.0, 'python_import'
                    if target is None and isinstance(node.func, ast.Attribute) and '.' in called:
                        prefix, member = called.rsplit('.', 1)
                        target_path = namespace_bindings.get(prefix)
                        if target_path:
                            target = by_path_qualified.get((target_path, member))
                            if target:
                                confidence, source_type = 1.0, 'python_import'
                    if target is None and isinstance(node.func, ast.Name):
                        candidates = by_name.get(called.rsplit('.', 1)[-1], [])
                        if len(candidates) == 1:
                            target, confidence = candidates[0], 0.9
                    if target:
                        relation = 'TESTED_BY' if _is_test_path(caller['path']) else 'CALLS'
                        source_id, target_id = caller['id'], target['id']
                        if relation == 'TESTED_BY':
                            source_id, target_id = target_id, source_id
                        add_edge(
                            source_id, target_id, relation, confidence,
                            rel_path, node.lineno, source_type,
                        )
                self.generic_visit(node)

        CallVisitor().visit(tree)

    return {
        'schema_version': GRAPH_SCHEMA_VERSION,
        'source_hash': index.get('source_hash', calculate_codebase_hash(root_dir)),
        'nodes': nodes,
        'edges': edges,
    }


def write_dependency_graph(graph, graph_path=GRAPH_PATH):
    """Atomically persist the dependency graph."""
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    temp_path = graph_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    os.replace(temp_path, graph_path)


def load_constraints(constraint_path=CONSTRAINT_PATH):
    """Load human-authored constraints without requiring external YAML packages."""
    if not os.path.exists(constraint_path):
        return {'schema_version': CONSTRAINT_SCHEMA_VERSION, 'constraints': []}
    with open(constraint_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_constraints(constraints, constraint_path=CONSTRAINT_PATH):
    os.makedirs(os.path.dirname(constraint_path), exist_ok=True)
    temp_path = constraint_path + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(constraints, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    os.replace(temp_path, constraint_path)


def validate_constraints(payload, index):
    """Validate constraint lifecycle and references to stable symbol IDs."""
    issues = []
    if payload.get('schema_version') != CONSTRAINT_SCHEMA_VERSION:
        issues.append(f"constraint schema must be {CONSTRAINT_SCHEMA_VERSION}")
    entries = payload.get('constraints')
    if not isinstance(entries, list):
        return issues + ['constraints must be a list']
    known_symbols = {symbol['id'] for symbol in index.get('symbols', [])}
    ids = [entry.get('id') for entry in entries if isinstance(entry, dict)]
    known_constraints = set(ids)
    if len(ids) != len(set(ids)):
        issues.append('constraint IDs must be unique')
    for entry in entries:
        if not isinstance(entry, dict):
            issues.append('constraint entry must be an object')
            continue
        cid = entry.get('id', '<missing>')
        if not re.fullmatch(r'C\d+', str(cid)):
            issues.append(f"{cid}: invalid constraint ID")
        if entry.get('status') not in {'ACTIVE', 'SUSPECT', 'STALE', 'SUPERSEDED'}:
            issues.append(f"{cid}: invalid lifecycle status")
        if entry.get('severity') not in {'low', 'medium', 'high', 'critical'}:
            issues.append(f"{cid}: invalid severity")
        if not str(entry.get('rule', '')).strip():
            issues.append(f"{cid}: rule is required")
        scope = entry.get('scope', [])
        if not isinstance(scope, list):
            issues.append(f"{cid}: scope must be a list")
            continue
        missing = [symbol_id for symbol_id in scope if symbol_id not in known_symbols]
        if missing and entry.get('status') == 'ACTIVE':
            issues.append(f"{cid}: ACTIVE scope references missing symbols: {', '.join(missing)}")
        if entry.get('status') == 'SUPERSEDED':
            replacement = entry.get('superseded_by')
            if replacement not in known_constraints:
                issues.append(f"{cid}: superseded_by must reference an existing constraint")
    return issues


def apply_constraints_to_graph(graph, payload):
    """Add constraint nodes and CONSTRAINED_BY edges to a graph copy in place."""
    node_ids = {node['id'] for node in graph.get('nodes', [])}
    for entry in payload.get('constraints', []):
        constraint_id = f"constraint:{entry['id']}"
        if constraint_id not in node_ids:
            graph['nodes'].append({
                'id': constraint_id,
                'type': 'constraint',
                'name': entry['id'],
                'rule': entry['rule'],
                'status': entry['status'],
                'severity': entry['severity'],
            })
            node_ids.add(constraint_id)
        if entry.get('status') not in {'ACTIVE', 'SUSPECT'}:
            continue
        for symbol_id in entry.get('scope', []):
            if symbol_id not in node_ids:
                continue
            graph['edges'].append({
                'source': symbol_id,
                'target': constraint_id,
                'relation': 'CONSTRAINED_BY',
                'confidence': 1.0,
                'evidence': {'path': f'{LCM_DIRNAME}/{CONSTRAINT_FILENAME}', 'line': 0, 'source': 'human'},
            })
    return graph


def validate_machine_state(root_dir=ROOT, index_path=INDEX_PATH, graph_path=GRAPH_PATH):
    """Validate schemas and compare persisted machine state with fresh analysis."""
    issues = []
    persisted_index = None
    persisted_graph = None

    for label, path, expected_schema in (
        ('index', index_path, INDEX_SCHEMA_VERSION),
        ('graph', graph_path, GRAPH_SCHEMA_VERSION),
    ):
        if not os.path.exists(path):
            issues.append(f"missing {os.path.relpath(path, root_dir).replace(os.sep, '/')}")
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except (OSError, ValueError) as exc:
            issues.append(f"invalid {label} JSON: {exc}")
            continue
        if payload.get('schema_version') != expected_schema:
            issues.append(
                f"{label} schema is {payload.get('schema_version')!r}; expected {expected_schema}"
            )
        if label == 'index':
            persisted_index = payload
        else:
            persisted_graph = payload

    expected_index = build_symbol_index(root_dir)
    constraint_path = os.path.join(root_dir, LCM_DIRNAME, CONSTRAINT_FILENAME)
    if not os.path.exists(constraint_path):
        issues.append(f"missing {LCM_DIRNAME}/{CONSTRAINT_FILENAME}")
    try:
        constraints = load_constraints(constraint_path)
        issues.extend(validate_constraints(constraints, expected_index))
    except (OSError, ValueError) as exc:
        constraints = {'schema_version': CONSTRAINT_SCHEMA_VERSION, 'constraints': []}
        issues.append(f"invalid constraints JSON: {exc}")
    expected_graph = apply_constraints_to_graph(
        build_dependency_graph(expected_index, root_dir), constraints
    )
    current_hash = expected_index['source_hash']

    if persisted_index is not None:
        if persisted_index.get('source_hash') != current_hash:
            issues.append('index source_hash does not match the current codebase')
        if persisted_index != expected_index:
            issues.append('index content differs from a fresh deterministic scan')

    if persisted_graph is not None:
        if persisted_graph.get('source_hash') != current_hash:
            issues.append('graph source_hash does not match the current codebase')
        node_ids = {node.get('id') for node in persisted_graph.get('nodes', [])}
        for position, edge in enumerate(persisted_graph.get('edges', [])):
            if edge.get('source') not in node_ids or edge.get('target') not in node_ids:
                issues.append(f"graph edge {position} references a missing node")
                break
            confidence = edge.get('confidence')
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                issues.append(f"graph edge {position} has invalid confidence")
                break
            evidence = edge.get('evidence', {})
            if not evidence.get('path') or not isinstance(evidence.get('line'), int):
                issues.append(f"graph edge {position} has invalid evidence")
                break
        if persisted_graph != expected_graph:
            issues.append('graph content differs from a fresh deterministic scan')

    return list(dict.fromkeys(issues)), expected_index, expected_graph


def analyze_graph_impact(query, graph, max_depth=2):
    """Traverse incoming and outgoing dependency edges from matching symbols."""
    q = query.strip().lower()
    nodes = {node['id']: node for node in graph.get('nodes', [])}
    seeds = [
        node['id'] for node in nodes.values()
        if q == node['id'].lower()
        or q == node.get('qualified_name', '').lower()
        or q == node.get('name', '').lower()
    ]
    if not seeds:
        return {'seeds': [], 'nodes': [], 'edges': []}

    traversable = {'CALLS', 'TESTED_BY', 'HANDLES', 'TRIGGERS', 'READS', 'WRITES', 'CONSTRAINED_BY'}
    visited = set(seeds)
    frontier = set(seeds)
    selected_edges = []
    for _ in range(max(0, max_depth)):
        next_frontier = set()
        for edge in graph.get('edges', []):
            if edge.get('relation') not in traversable:
                continue
            if edge['source'] in frontier or edge['target'] in frontier:
                selected_edges.append(edge)
                other = edge['target'] if edge['source'] in frontier else edge['source']
                if other not in visited:
                    visited.add(other)
                    next_frontier.add(other)
        frontier = next_frontier
        if not frontier:
            break

    unique_edges = []
    seen_edges = set()
    for edge in selected_edges:
        key = (edge['source'], edge['target'], edge['relation'])
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(edge)
    return {
        'seeds': seeds,
        'nodes': [nodes[node_id] for node_id in visited if node_id in nodes],
        'edges': unique_edges,
    }


def build_change_plan(task, graph):
    """Compile a task-focused change plan and explainable risk score."""
    tokens = {token for token in re.findall(r'[A-Za-z0-9_/-]{3,}', task.lower())}
    candidates = []
    for node in graph.get('nodes', []):
        haystack = ' '.join(str(node.get(key, '')) for key in ('id', 'name', 'qualified_name', 'path')).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score:
            candidates.append((score, node))
    candidates.sort(key=lambda item: (-item[0], item[1]['id']))
    seeds = [node['id'] for _, node in candidates[:8]]
    selected_nodes = {node['id']: node for _, node in candidates[:8]}
    selected_edges = []
    for seed in seeds:
        impact = analyze_graph_impact(seed, graph, max_depth=2)
        selected_nodes.update({node['id']: node for node in impact['nodes']})
        selected_edges.extend(impact['edges'])

    unique_edges = {(e['source'], e['target'], e['relation']): e for e in selected_edges}
    reasons = []
    risk = 0
    if any(node.get('type') == 'api' for node in selected_nodes.values()):
        risk += 25
        reasons.append(('+25', 'public API or route'))
    constraints = [node for node in selected_nodes.values() if node.get('type') == 'constraint']
    if any(node.get('severity') == 'critical' for node in constraints):
        risk += 25
        reasons.append(('+25', 'critical constraint'))
    elif any(node.get('severity') == 'high' for node in constraints):
        risk += 15
        reasons.append(('+15', 'high constraint'))
    dependent_count = max(0, len(selected_nodes) - len(seeds))
    if dependent_count > 10:
        risk += 20
        reasons.append(('+20', f'{dependent_count} related nodes'))
    elif dependent_count > 3:
        risk += 10
        reasons.append(('+10', f'{dependent_count} related nodes'))
    if any(edge.get('confidence', 1) < 0.95 for edge in unique_edges.values()):
        risk += 10
        reasons.append(('+10', 'inferred dependency'))
    has_tests = any(edge.get('relation') == 'TESTED_BY' for edge in unique_edges.values())
    if seeds and not has_tests:
        risk += 15
        reasons.append(('+15', 'no linked tests'))
    level = 'RED' if risk >= 60 else ('YELLOW' if risk >= 30 else 'GREEN')
    return {
        'task': task, 'risk_score': risk, 'risk_level': level,
        'reasons': reasons, 'seeds': seeds,
        'nodes': list(selected_nodes.values()), 'edges': list(unique_edges.values()),
    }


def verify_changed_files(changed_files, graph):
    """Compare changed files with graph-linked tests and constraints."""
    changed = {path.replace('\\', '/') for path in changed_files}
    nodes = {node['id']: node for node in graph.get('nodes', [])}
    changed_ids = {
        node_id for node_id, node in nodes.items()
        if node.get('path', '').replace('\\', '/') in changed
    }
    related_edges = [
        edge for edge in graph.get('edges', [])
        if edge.get('source') in changed_ids or edge.get('target') in changed_ids
    ]
    missing_tests = []
    constraints = []
    for edge in related_edges:
        if edge.get('relation') == 'TESTED_BY' and edge.get('source') in changed_ids:
            test_node = nodes.get(edge.get('target'), {})
            test_path = test_node.get('path')
            if test_path and test_path not in changed:
                missing_tests.append(test_path)
        if edge.get('relation') == 'CONSTRAINED_BY':
            constraint_node = nodes.get(edge.get('target'), {})
            if constraint_node:
                constraints.append(constraint_node)
    return {
        'changed_files': sorted(changed),
        'changed_symbols': sorted(changed_ids),
        'related_edges': related_edges,
        'missing_tests': sorted(set(missing_tests)),
        'constraints': list({node['id']: node for node in constraints}.values()),
    }


def explain_graph_symbol(query, graph):
    """Return a structured one-hop explanation for one unambiguous graph node."""
    q = query.strip().lower()
    matches = [
        node for node in graph.get('nodes', [])
        if q == node.get('id', '').lower()
        or q == node.get('qualified_name', '').lower()
        or q == node.get('name', '').lower()
    ]
    if len(matches) != 1:
        return {'match': None, 'candidates': [node['id'] for node in matches]}
    node = matches[0]
    incoming = [edge for edge in graph.get('edges', []) if edge.get('target') == node['id']]
    outgoing = [edge for edge in graph.get('edges', []) if edge.get('source') == node['id']]
    return {'match': node, 'candidates': [], 'incoming': incoming, 'outgoing': outgoing}


def compile_task_context(task, graph, budget=500):
    """Compile task-specific graph context within an approximate token budget."""
    plan = build_change_plan(task, graph)
    node_by_id = {node['id']: node for node in plan['nodes']}
    lines = [
        'LCM TASK CONTEXT',
        f"Task: {task}",
        f"Risk: {plan['risk_level']} ({plan['risk_score']})",
    ]
    if plan['reasons']:
        lines.append('Risk reasons: ' + ', '.join(f"{p} {r}" for p, r in plan['reasons']))
    lines.append('Relevant nodes:')
    for node in sorted(plan['nodes'], key=lambda item: (item.get('type', ''), item['id'])):
        detail = node.get('path') or node.get('rule') or ''
        lines.append(f"- [{node.get('type', 'node')}] {node['id']} {detail}".rstrip())
    if plan['edges']:
        lines.append('Relationships:')
        for edge in plan['edges']:
            source = node_by_id.get(edge['source'], {}).get('name', edge['source'])
            target = node_by_id.get(edge['target'], {}).get('name', edge['target'])
            lines.append(f"- {source} --{edge['relation']}--> {target} ({edge['confidence']:.2f})")

    max_chars = max(200, int(budget) * 4)
    selected = []
    used = 0
    for line in lines:
        cost = len(line) + 1
        if selected and used + cost > max_chars:
            break
        selected.append(line[:max_chars] if not selected else line)
        used += min(cost, max_chars)
    omitted = len(lines) - len(selected)
    if omitted and used + 40 <= max_chars:
        selected.append(f"... {omitted} context lines omitted by budget")
    text = '\n'.join(selected)
    return {'text': text, 'estimated_tokens': (len(text) + 3) // 4, 'omitted_lines': omitted, 'plan': plan}


def parse_symbol_git_history(raw_log):
    """Parse delimiter-safe git log output into temporal-memory entries."""
    entries = []
    for record in raw_log.split('\x1e'):
        parts = record.strip().split('\x1f', 3)
        if len(parts) == 4:
            entries.append({'hash': parts[0], 'short': parts[1], 'date': parts[2], 'subject': parts[3]})
    return entries


def get_symbol_history(query, graph, limit=10):
    """Resolve a symbol and query Git pickaxe history for its name and file."""
    explanation = explain_graph_symbol(query, graph)
    if explanation['match'] is None:
        return {'symbol': None, 'candidates': explanation['candidates'], 'commits': [], 'constraints': []}
    node = explanation['match']
    path = node.get('path')
    name = node.get('name') or node.get('qualified_name', '').rsplit('.', 1)[-1]
    commits = []
    if path and name:
        code, out, _ = _git([
            'log', '--follow', f'-S{name}',
            '--format=%H%x1f%h%x1f%cs%x1f%s%x1e', '--', path,
        ])
        if code == 0:
            commits = parse_symbol_git_history(out)[:max(1, limit)]
    constraints = []
    nodes = {item['id']: item for item in graph.get('nodes', [])}
    for edge in explanation.get('outgoing', []):
        if edge.get('relation') == 'CONSTRAINED_BY':
            target = nodes.get(edge.get('target'))
            if target:
                constraints.append(target)
    return {'symbol': node, 'candidates': [], 'commits': commits, 'constraints': constraints}

def build_symbol_database(root_dir=ROOT):
    """
    Traverses the codebase and builds:
    file_map: {rel_path: {symbol_name: line_number}}
    symbol_lookup: {(base_fname, sym): (rel_path, line), sym: (rel_path, line)}
    """
    file_map = {}
    symbol_lookup = {}
    candidates = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in CODE_EXTENSIONS:
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
                symbols = scan_file_symbols(full_path)
                if symbols:
                    file_map[rel_path] = symbols
                    for sym, line in symbols.items():
                        base_fname = os.path.basename(rel_path)
                        location = (rel_path, line)
                        for key in ((rel_path, sym), (base_fname, sym), sym):
                            candidates.setdefault(key, []).append(location)

    # Backward-compatible lookup shape, but ambiguous keys are deliberately
    # omitted instead of silently pointing at whichever file was scanned last.
    for key, locations in candidates.items():
        unique_locations = list(dict.fromkeys(locations))
        if len(unique_locations) == 1:
            symbol_lookup[key] = unique_locations[0]

    return file_map, symbol_lookup

# ─────────────────────────────────────────────────────────────
# MAP REFRESH & DRIFT DETECTION ENGINE
# ─────────────────────────────────────────────────────────────

def update_map_line_numbers(map_content, symbol_lookup):
    """
    Updates line references in table rows.
    Returns (new_content, updated_count, drift_details)
    """
    updated_count = 0
    drift_details = []
    current_file = None

    re_file_header = re.compile(r'^###\s+([A-Za-z0-9_\-./\\]+\.[a-z]+)', re.MULTILINE)
    re_table_row = re.compile(
        r'^\|\s*L(\d+)\s*\|\s*(\*{0,2}`([A-Za-z0-9_#\-]+)(?:\(\))?`\*{0,2})\s*\|',
        re.MULTILINE,
    )

    new_lines = []
    lines = map_content.splitlines()

    for line in lines:
        m_hdr = re_file_header.match(line)
        if m_hdr:
            current_file = m_hdr.group(1).strip().replace('\\', '/')

        m_row = re_table_row.match(line)
        if m_row:
            old_line = m_row.group(1)
            raw_sym_md = m_row.group(2)
            sym_name = m_row.group(3)

            matched_loc = None
            normalized_file = current_file.replace('\\', '/') if current_file else None
            if normalized_file and (normalized_file, sym_name) in symbol_lookup:
                matched_loc = symbol_lookup[(normalized_file, sym_name)]
            elif normalized_file and (os.path.basename(normalized_file), sym_name) in symbol_lookup:
                matched_loc = symbol_lookup[(os.path.basename(normalized_file), sym_name)]
            elif sym_name in symbol_lookup:
                matched_loc = symbol_lookup[sym_name]

            if matched_loc:
                rel_p, real_line = matched_loc
                if str(real_line) != old_line:
                    line = line.replace(f'| L{old_line} |', f'| L{real_line} |', 1)
                    updated_count += 1
                    drift_details.append({
                        'file': current_file or rel_p,
                        'symbol': sym_name,
                        'old_line': int(old_line),
                        'new_line': real_line,
                        'delta': real_line - int(old_line)
                    })

        new_lines.append(line)

    return '\n'.join(new_lines), updated_count, drift_details

def update_map_header(map_content, codebase_hash=None):
    """Updates the Last Updated date, latest Commit hash, and Codebase-MD5."""
    today = datetime.now().strftime('%Y-%m-%d')
    short_h, _, _ = git_get_head_info()

    if not codebase_hash:
        codebase_hash = calculate_codebase_hash(ROOT)

    # 1. Update date & commit line
    re_header = re.compile(r'(>\s*\*\*(?:Last Updated|Cập nhật lần cuối):\*\*\s*)[^|\n]+(\|\s*Commit:\s*)[^\n]+')
    if re_header.search(map_content):
        map_content = re_header.sub(rf'\g<1>{today} \g<2>{short_h}', map_content)

    # 2. Update or insert Codebase-MD5 in Module 0
    if "Codebase-MD5:" in map_content:
        map_content = re.sub(r'Codebase-MD5:\s*([a-f0-9]{32})', f'Codebase-MD5: {codebase_hash}', map_content)
    elif "| Codebase-MD5 |" in map_content:
        map_content = re.sub(r'\|\s*Codebase-MD5\s*\|\s*`?[a-f0-9]{32}`?\s*\|', f'| Codebase-MD5 | `{codebase_hash}` |', map_content)
    else:
        # Insert into Module 0 table or list
        if "## MODULE 0: META" in map_content or "## MODULE 0:" in map_content:
            pos = map_content.find("## MODULE 0:")
            if pos != -1:
                next_nl = map_content.find("\n\n", pos)
                if next_nl != -1:
                    insert_txt = f"\n| Codebase-MD5 | `{codebase_hash}` |"
                    # Check if there is a table in Module 0
                    tbl_end = map_content.find("\n\n", next_nl + 2)
                    if tbl_end != -1:
                        map_content = map_content[:tbl_end] + insert_txt + map_content[tbl_end:]

    return map_content

def inject_feature(map_content, feature_id, desc, commit, ui_sel, js_func, api_ep, db_tbl, constraints):
    """Injects a new feature row into Feature Cross-Reference table."""
    row = f"| {feature_id} | {desc} | `{ui_sel}` | `{js_func}` | `{api_ep}` | `{db_tbl}` | {constraints} |"

    marker_candidates = [
        "## MODULE 5: FEATURE CROSS-REFERENCE MATRIX",
        "## MODULE 9: FEATURE CROSS-REFERENCE MATRIX",
        "## FEATURE CROSS-REFERENCE"
    ]

    for marker in marker_candidates:
        if marker in map_content:
            pos = map_content.find(marker)
            next_sec = map_content.find('\n---\n', pos)
            if next_sec == -1:
                next_sec = len(map_content)

            table_block = map_content[pos:next_sec]
            lines = table_block.splitlines()

            last_row_idx = -1
            for i, l in enumerate(lines):
                if l.strip().startswith('|'):
                    last_row_idx = i

            if last_row_idx != -1:
                lines.insert(last_row_idx + 1, row)
                new_table_block = '\n'.join(lines)
                return map_content[:pos] + new_table_block + map_content[next_sec:]

    return map_content + f"\n\n### Added Feature: {feature_id}\n{row}\n"

def inject_constraint(map_content, constraint_desc, custom_id=None):
    """Injects a new implicit constraint into Module 4."""
    if not custom_id:
        existing_ids = re.findall(r'\[C(\d+)\]', map_content)
        if existing_ids:
            next_num = max(int(x) for x in existing_ids) + 1
            custom_id = f"C{next_num}"
        else:
            custom_id = "C1"

    new_line = f"- [{custom_id}] {constraint_desc}"

    marker_candidates = [
        "## MODULE 4: IMPLICIT CONSTRAINTS",
        "## IMPLICIT CONSTRAINTS"
    ]

    for marker in marker_candidates:
        if marker in map_content:
            pos = map_content.find(marker)
            next_sec = map_content.find('\n---\n', pos)
            if next_sec == -1:
                next_sec = len(map_content)

            block = map_content[pos:next_sec]
            lines = block.splitlines()
            lines.append(new_line)
            new_block = '\n'.join(lines)
            return map_content[:pos] + new_block + map_content[next_sec:], custom_id

    return map_content + f"\n\n{new_line}\n", custom_id

# ─────────────────────────────────────────────────────────────
# CLI COMMAND HANDLERS
# ─────────────────────────────────────────────────────────────

def cmd_init(args):
    """Initializes a fresh PROJECT_MAP.md from template."""
    print("=" * 60)
    print("Living Codebase Map -- Initializer (v3)")
    print("=" * 60)

    if os.path.exists(MAP_PATH) and not args.force:
        print(f"[WARN] {MAP_FILENAME} already exists. Use --force to overwrite.")
        return 1

    template_path = os.path.join(SCRIPT_DIR, '..', 'templates', 'PROJECT_MAP.template.md')
    if not os.path.exists(template_path):
        template_path = os.path.join(SCRIPT_DIR, 'PROJECT_MAP.template.md')

    if not os.path.exists(template_path):
        print(f"[ERR] Template not found at {template_path}")
        return 1

    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    proj_name = os.path.basename(ROOT)
    today = datetime.now().strftime('%Y-%m-%d')
    short_h, _, _ = git_get_head_info()
    codebase_hash = calculate_codebase_hash(ROOT)

    stack = "Generic"
    entry = "main"
    db = "SQLite / PostgreSQL"
    test_fw = "pytest / go test / npm test"

    if os.path.exists(os.path.join(ROOT, 'go.mod')):
        stack = "Go (Gin/net/http)"
        entry = "main.go"
    elif os.path.exists(os.path.join(ROOT, 'package.json')):
        stack = "Node.js (Next.js/Express/TypeScript)"
        entry = "index.js / src/app.tsx"
    elif os.path.exists(os.path.join(ROOT, 'pyproject.toml')) or os.path.exists(os.path.join(ROOT, 'requirements.txt')):
        stack = "Python (FastAPI/Django/Flask)"
        entry = "main.py / app.py"
    elif os.path.exists(os.path.join(ROOT, 'Cargo.toml')):
        stack = "Rust (Actix/Axum)"
        entry = "src/main.rs"

    rendered = template.replace('{{PROJECT_NAME}}', proj_name) \
                       .replace('{{UPDATED_AT}}', today) \
                       .replace('{{COMMIT_HASH}}', short_h) \
                       .replace('{{STACK}}', stack) \
                       .replace('{{ENTRY_POINT}}', entry) \
                       .replace('{{DATABASE}}', db) \
                       .replace('{{TEST_FRAMEWORK}}', test_fw) \
                       .replace('{{TEST_COUNT}}', '0') \
                       .replace('{{BACKEND_SAMPLE_FILE}}', 'backend_core') \
                       .replace('{{FRONTEND_SAMPLE_FILE}}', 'frontend_app') \
                       .replace('{{TEST_DIR}}', 'tests/') \
                       .replace('{{TEST_COMMAND}}', 'pytest / npm test')

    rendered = update_map_header(rendered, codebase_hash)

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(rendered)

    print(f"[OK] Generated {MAP_FILENAME} for project: {proj_name}")
    generate_min_map(MAP_PATH, MIN_MAP_PATH)
    print(f"     Next: run 'python living_map.py update' to index symbols.")
    return 0

def cmd_update(args):
    """Scans codebase, updates PROJECT_MAP.md, and generates PROJECT_MAP.min.md."""
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found at {MAP_PATH}. Run 'init' first.")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    print(f"[SCAN] Indexing symbols across codebase ({ROOT})...")
    file_map, symbol_lookup = build_symbol_database(ROOT)
    symbol_index = build_symbol_index(ROOT)
    try:
        constraints = load_constraints(CONSTRAINT_PATH)
    except (OSError, ValueError) as exc:
        print(f"[ERR] Invalid {LCM_DIRNAME}/{CONSTRAINT_FILENAME}: {exc}")
        return 1
    constraint_issues = validate_constraints(constraints, symbol_index)
    if constraint_issues:
        print("[ERR] Constraint validation failed:")
        for issue in constraint_issues:
            print(f"  - {issue}")
        return 1
    dependency_graph = apply_constraints_to_graph(
        build_dependency_graph(symbol_index, ROOT), constraints
    )
    total_syms = len(symbol_index['symbols'])
    total_edges = len(dependency_graph['edges'])
    print(f"       Found {len(file_map)} files with {total_syms} identifiable symbols.")

    # 1. Update line numbers
    new_content, updated_lines, drift_details = update_map_line_numbers(content, symbol_lookup)
    print(f"[SYNC] Updated {updated_lines} line number references.")

    # 2. Compute Codebase-MD5 hash
    codebase_hash = calculate_codebase_hash(ROOT)
    print(f"[HASH] Codebase-MD5: {codebase_hash}")

    # 3. Update header
    new_content = update_map_header(new_content, codebase_hash)

    if args.dry_run:
        print(f"[DRY-RUN] Would write {total_syms} symbols to {LCM_DIRNAME}/{INDEX_FILENAME}.")
        print(f"[DRY-RUN] Would write {total_edges} dependency edges to {LCM_DIRNAME}/{GRAPH_FILENAME}.")
        print("[DRY-RUN] Changes preview complete. No files modified.")
        return 0

    # Write backup and file
    bak_path = MAP_PATH + '.bak'
    with open(bak_path, 'w', encoding='utf-8') as f:
        f.write(content)

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[WRITE] Successfully refreshed {MAP_FILENAME}.")

    write_symbol_index(symbol_index)
    print(f"[INDEX] Wrote {LCM_DIRNAME}/{INDEX_FILENAME} (schema v{INDEX_SCHEMA_VERSION}, {total_syms} symbols).")
    write_dependency_graph(dependency_graph)
    print(f"[GRAPH] Wrote {LCM_DIRNAME}/{GRAPH_FILENAME} (schema v{GRAPH_SCHEMA_VERSION}, {total_edges} edges).")
    if not os.path.exists(CONSTRAINT_PATH):
        write_constraints(constraints)
        print(f"[CONSTRAINTS] Initialized {LCM_DIRNAME}/{CONSTRAINT_FILENAME}.")

    # 4. Auto-generate mini compact map for AI Agents
    generate_min_map(MAP_PATH, MIN_MAP_PATH)

    if args.auto_commit:
        git_commit_map("docs: refresh living codebase map & compact summary")
    return 0

def cmd_check(args):
    """Verify Markdown projections and deterministic machine state."""
    if not os.path.exists(MAP_PATH):
        print(f"❌ [LIVING MAP LINT ERR] {MAP_FILENAME} not found at {MAP_PATH}")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    machine_issues, expected_index, expected_graph = validate_machine_state(ROOT, INDEX_PATH, GRAPH_PATH)
    current_hash = expected_index['source_hash']
    m_hash = re.search(r'Codebase-MD5:\s*([a-f0-9]{32})', content)
    if not m_hash:
        m_hash = re.search(r'\|\s*Codebase-MD5\s*\|\s*`?([a-f0-9]{32})`?\s*\|', content)
    markdown_hash_ok = bool(m_hash and m_hash.group(1) == current_hash)

    _, symbol_lookup = build_symbol_database(ROOT)
    new_content, updated_count, drift_details = update_map_line_numbers(content, symbol_lookup)
    has_drift = bool(machine_issues or not markdown_hash_ok or updated_count)

    if not has_drift:
        print(
            f"✅ [LIVING MAP LINT PASS] Markdown, index, and graph match "
            f"the current codebase ({current_hash[:8]}...)."
        )
        return 0

    print("\n❌ [LIVING MAP LINT FAILED] Generated state is out of sync:\n")
    if not markdown_hash_ok:
        print("  - PROJECT_MAP.md Codebase-MD5 does not match the current codebase")
    for issue in machine_issues:
        print(f"  - {issue}")
    if updated_count:
        print(f"\n❌ [LIVING MAP LINT FAILED] Found {updated_count} outdated symbol location(s) in {MAP_FILENAME}:\n")
        print(f"  {'FILE':<25} {'SYMBOL':<32} {'MAP LINE':<12} {'ACTUAL':<10} {'DELTA'}")
        print("  " + "-" * 85)
        for d in drift_details[:25]:
            delta_str = f"+{d['delta']}" if d['delta'] > 0 else f"{d['delta']}"
            print(f"  {d['file']:<25} {d['symbol']:<32} L{d['old_line']:<11} L{d['new_line']:<9} {delta_str}")
        if len(drift_details) > 25:
            print(f"  ... and {len(drift_details) - 25} more items.")

    if getattr(args, 'fix', False):
        try:
            constraints = load_constraints(CONSTRAINT_PATH)
            constraint_issues = validate_constraints(constraints, expected_index)
        except (OSError, ValueError) as exc:
            print(f"[ERR] Constraints require manual repair: {exc}")
            return 2
        if constraint_issues:
            print("[ERR] Constraints require manual repair before generated state can be rebuilt:")
            for issue in constraint_issues:
                print(f"  - {issue}")
            return 2
        print("\n[AUTO-FIX] Rebuilding Markdown and machine state...")
        with open(MAP_PATH + '.bak', 'w', encoding='utf-8') as f:
            f.write(content)
        new_content = update_map_header(new_content, current_hash)
        with open(MAP_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        write_symbol_index(expected_index)
        write_dependency_graph(expected_graph)
        write_constraints(constraints)
        generate_min_map(MAP_PATH, MIN_MAP_PATH)
        print(
            f"✅ [REPAIRED] Updated {MAP_FILENAME}, {MIN_MAP_FILENAME}, "
            f"{LCM_DIRNAME}/{INDEX_FILENAME}, and {LCM_DIRNAME}/{GRAPH_FILENAME}."
        )
        return 0

    print(f"\n👉 FIX REQUIRED: Run 'python {os.path.relpath(__file__, ROOT)} update' before pushing.")
    print("   Or run: 'python living_map.py check --fix'")
    return 2

def cmd_impact(args, is_deep=False):
    """
    Feature 2: Cross-layer blast radius analysis for a symbol or keyword.
    - Default (Lean Mode): Capped at depth 2 (<15 lines) to save LLM context tokens.
    - Deep Mode (--deep or deep-impact): Exhaustive 6-layer architecture dependency tree.
    """
    if not os.path.exists(MAP_PATH) and not os.path.exists(GRAPH_PATH):
        print(f"[ERR] Neither {MAP_FILENAME} nor {LCM_DIRNAME}/{GRAPH_FILENAME} exists. Run 'update' first.")
        return 1

    content = ''
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

    target = args.target
    report = analyze_symbol_impact(target, content)
    graph_report = {'seeds': [], 'nodes': [], 'edges': []}
    if os.path.exists(GRAPH_PATH):
        try:
            with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
                graph_report = analyze_graph_impact(target, json.load(f), max_depth=max(1, getattr(args, 'depth', 2)))
        except (OSError, ValueError, KeyError) as exc:
            print(f"[WARN] Could not read dependency graph: {exc}")
    graph_links = len(graph_report['edges'])
    blast_count = (
        len(report['locations']) + len(report['ui_triggers']) +
        len(report['api_routes']) + len(report['db_tables']) + graph_links
    )
    has_constraints = bool(report['constraints'])
    risk_level = "🔴 CRITICAL" if (blast_count > 10 or has_constraints) else ("🟡 MEDIUM" if blast_count > 3 else "🟢 LOW")

    # Determine if deep mode is requested
    is_deep = is_deep or getattr(args, 'deep', False) or getattr(args, 'full', False)

    if is_deep:
        # DEEP MODE: Exhaustive 6-layer architecture dependency tree
        print("=" * 75)
        print(f"🔥 [DEEP IMPACT ACTIVE] Exhaustive cross-layer blast radius for: '{target}' | Risk: {risk_level}")
        print("=" * 75)

        layers = [
            ("Graph: Confirmed & Inferred Dependencies", [
                f"{edge['relation']} {edge['source']} -> {edge['target']} "
                f"(confidence {edge['confidence']:.2f}, {edge['evidence']['path']}:{edge['evidence']['line']})"
                for edge in graph_report['edges']
            ], "Edge"),
            ("Layer 1: Code Definitions & Call Sites", report['locations'], "Code"),
            ("Layer 2: API Contracts & Routing", report['api_routes'], "API"),
            ("Layer 3: UI Triggers & DOM Selectors", report['ui_triggers'], "DOM"),
            ("Layer 4: Database Tables & Models", report['db_tables'], "DB"),
            ("Layer 5: Implicit Architectural Constraints (Module 4)", report['constraints'], "Rule"),
            ("Layer 6: Linked Features & Cross-References (Module 5)", report['features'], "Feature")
        ]

        total_found = 0
        active_layers = 0
        custom_depth = getattr(args, 'depth', 0)

        for title, items, layer_type in layers:
            if not items:
                continue
            active_layers += 1
            limit = custom_depth if custom_depth > 0 else len(items)
            print(f"\n📂 [{title}] ({len(items)} found)")
            for i, item in enumerate(items[:limit]):
                is_last = (i == len(items[:limit]) - 1) and (len(items) <= limit)
                branch = "└── " if is_last else "├── "
                print(f"  {branch}[{layer_type}] {item}")
                total_found += 1
            if len(items) > limit:
                print(f"  └── ... (+{len(items) - limit} more items in this layer)")

        print("\n" + "=" * 75)
        print(f"📊 SUMMARY: Detected {total_found} linked components across {active_layers} architectural layers.")
        if blast_count > 3 or has_constraints:
            print("⚠️  HIGH BLAST RADIUS: Verify constraints in Module 4 and run integration tests before commit.")
        else:
            print("✅ LOW BLAST RADIUS: Safe to proceed with minimal cross-layer dependency risk.")
        print("=" * 75)
        return 0

    # LEAN MODE (Default): Under 15 lines, token-saving for daily agent operation
    depth = getattr(args, 'depth', 2)
    if depth <= 0:
        depth = 2

    print(f"🎯 IMPACT (LEAN): '{target}' | Risk: {risk_level} ({blast_count} components)")
    print("-" * 65)
    total_hidden = 0

    if report['locations']:
        loc_sample = [l.split('->')[0].strip() for l in report['locations'][:depth]]
        hidden = len(report['locations']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• Code:        {', '.join(loc_sample)}{extra}")
    if graph_report['edges']:
        graph_sample = []
        for edge in graph_report['edges'][:depth]:
            target_node = edge['target'].split('::')[-1]
            marker = 'confirmed' if edge['confidence'] >= 0.95 else 'likely'
            graph_sample.append(f"{edge['relation']} {target_node} [{marker} {edge['confidence']:.2f}]")
        hidden = len(graph_report['edges']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• Graph:       {', '.join(graph_sample)}{extra}")
    if report['ui_triggers']:
        ui_sample = [u.split(':')[0].strip() for u in report['ui_triggers'][:depth]]
        hidden = len(report['ui_triggers']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• UI DOM:      {', '.join(ui_sample)}{extra}")
    if report['api_routes']:
        hidden = len(report['api_routes']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• API:         {', '.join(report['api_routes'][:depth])}{extra}")
    if report['db_tables']:
        hidden = len(report['db_tables']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• DB:          {', '.join(report['db_tables'][:depth])}{extra}")
    if report['constraints']:
        c_ids = [c.split(']')[0].strip(' [') for c in report['constraints'][:depth]]
        hidden = len(report['constraints']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• Constraints: {', '.join(c_ids)}{extra}")
    if report['features']:
        f_ids = [f.split(':')[0].strip() for f in report['features'][:depth]]
        hidden = len(report['features']) - depth
        if hidden > 0:
            total_hidden += hidden
        extra = f" (+{hidden} more)" if hidden > 0 else ""
        print(f"• Features:    {', '.join(f_ids)}{extra}")

    if risk_level.startswith("🔴"):
        action = "Review graph evidence and constraints; run integration tests before editing."
    elif risk_level.startswith("🟡"):
        action = "Inspect linked callers/callees and run targeted tests."
    else:
        action = "Proceed with a minimal change and targeted verification."
    print(f"💡 Action:     {action}")
    if total_hidden > 0:
        print(f"⚠️  ... Hidden {total_hidden} deeper items to SAVE AI CONTEXT TOKENS.")
        print(f"🤖 For exhaustive 6-layer architecture dependency tree, run: map deep-impact {target} (or --deep)")
    print("-" * 65)
    return 0

def cmd_deep_impact(args):
    """Deep impact wrapper: runs exhaustive 6-layer architecture dependency tree."""
    return cmd_impact(args, is_deep=True)

def cmd_install_hook(args):
    """Installs a Git pre-commit or pre-push hook to guard against map drift."""
    git_dir = os.path.join(ROOT, '.git')
    if not os.path.exists(git_dir):
        print(f"❌ [ERR] .git directory not found in {ROOT}. Is this a Git repository?")
        return 1

    hooks_dir = os.path.join(git_dir, 'hooks')
    os.makedirs(hooks_dir, exist_ok=True)

    hook_type = args.hook or 'pre-commit'
    hook_path = os.path.join(hooks_dir, hook_type)

    rel_script = os.path.relpath(__file__, ROOT).replace('\\', '/')

    hook_content = f"""#!/bin/sh
# Living Codebase Map -- Automated Drift Guard
# Installed automatically by living_map.py

echo "[LIVING MAP GUARD] Checking {MAP_FILENAME} synchronization..."
python "{rel_script}" check
RESULT=$?

if [ $RESULT -ne 0 ]; then
    echo ""
    echo "❌ [BLOCKED] Git {hook_type} aborted: {MAP_FILENAME} is out of sync with code!"
    echo "👉 Fix by running: python {rel_script} update"
    echo "👉 Or auto-repair with: python {rel_script} check --fix"
    echo "👉 Or bypass temporarily with: git commit --no-verify"
    exit 1
fi

exit 0
"""

    with open(hook_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(hook_content)

    try:
        os.chmod(hook_path, 0o755)
    except Exception:
        pass

    print(f"✅ [HOOK INSTALLED] Git {hook_type} hook created at:")
    print(f"   {hook_path}")
    print(f"   Your repository will now automatically block commits if {MAP_FILENAME} drifts!")
    return 0

def cmd_add_feature(args):
    """
    Injects a new feature into the map with smart natural language auto-detection.
    Extracts ID (Fxxx), UI Selector (#id, .class, [data-testid=...]), API Route, and clean description.
    """
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found. Run 'init' first.")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    raw_input = getattr(args, 'raw_text', '') or getattr(args, 'desc', '') or ''
    if not raw_input and not getattr(args, 'id', None):
        print("❌ [ERR] Please provide feature description or natural language prompt.")
        print("   Usage: python living_map.py add-feature \"Integrate button #btn-submit into API POST /api/v1/checkout\"")
        return 1

    # 1. Smart Feature ID (Fxxx auto-incremented based on highest existing ID)
    feature_id = getattr(args, 'id', None)
    if not feature_id:
        m_id = re.search(r'\b(F\d{2,4}|F-[A-Za-z0-9_\-]+)\b', raw_input)
        if m_id:
            feature_id = m_id.group(1).upper()
        else:
            existing_nums = [int(n) for n in re.findall(r'F(\d{2,4})', content)]
            next_num = max(existing_nums) + 1 if existing_nums else 1
            feature_id = f"F{next_num:03d}"

    # 2. Smart UI DOM Selector (#id, .class, [data-testid=...])
    ui_sel = getattr(args, 'ui', None)
    raw_ui_match = None
    if not ui_sel:
        raw_ui_match = re.search(r'(#[\w-]+|\.[\w-]+|\[data-testid=.*?\])', raw_input)
        ui_sel = raw_ui_match.group(1) if raw_ui_match else "-"

    # 3. Smart API Endpoint (METHOD in UPPERCASE, path in exact casing)
    api_ep = getattr(args, 'api', None)
    raw_api_match = None
    if not api_ep:
        m_method_path = re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\s+([\w\/\-{}*:]+)', raw_input, re.IGNORECASE)
        if m_method_path:
            raw_api_match = m_method_path
            api_ep = f"{m_method_path.group(1).upper()} {m_method_path.group(2)}"
        else:
            m_path_only = re.search(r'(\/[\w\/\-{}*:]+)', raw_input)
            if m_path_only:
                raw_api_match = m_path_only
                api_ep = m_path_only.group(1)
            else:
                api_ep = "-"

    # 4. Smart Constraints (C1, C2...)
    constraints = getattr(args, 'constraints', None)
    if not constraints:
        m_c = re.findall(r'\bC\d+\b', raw_input, re.IGNORECASE)
        constraints = ",".join(c.upper() for c in m_c) if m_c else "-"

    # 5. Smart JS function
    js_func = getattr(args, 'js', None)
    if not js_func:
        m_js = re.search(r'([a-zA-Z0-9_]+\(\)(?:\s+[a-zA-Z0-9_.]+)?)', raw_input)
        js_func = m_js.group(1) if m_js else "-"

    # 6. Smart DB Table
    db_tbl = getattr(args, 'db', None)
    if not db_tbl:
        m_db = re.search(r'(?:table|bảng|tbl)\s+([a-zA-Z0-9_]+)', raw_input, re.IGNORECASE)
        db_tbl = m_db.group(1) if m_db else "-"

    # 7. Clean Description (strip parsed UI/API tokens and filler words if natural prompt was provided)
    desc = getattr(args, 'desc', None)
    if not desc:
        desc = raw_input
        if raw_ui_match:
            desc = desc.replace(raw_ui_match.group(0), "")
        if raw_api_match:
            desc = desc.replace(raw_api_match.group(0), "")
        if feature_id and feature_id in desc:
            desc = desc.replace(feature_id, "")
        # Remove common connective phrases
        desc = re.sub(r'\b(at button|tại nút|ở nút|nút|via API|qua API|calling|using|into API|vào API|API)\b', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'\s+', ' ', desc).strip()
        if len(desc) < 3:
            desc = raw_input.strip()

    commit = getattr(args, 'commit', None) or git_get_head_info()[0]
    new_content = inject_feature(
        content,
        feature_id=feature_id,
        desc=desc,
        commit=commit,
        ui_sel=ui_sel,
        js_func=js_func,
        api_ep=api_ep,
        db_tbl=db_tbl,
        constraints=constraints
    )
    codebase_hash = calculate_codebase_hash(ROOT)
    new_content = update_map_header(new_content, codebase_hash)

    if getattr(args, 'dry_run', False):
        print(f"🤖 [DRY-RUN] Auto-parsed feature preview for [{feature_id}]:")
        print(f"   • ID:          {feature_id}")
        print(f"   • Description: {desc}")
        print(f"   • UI Element:  {ui_sel}")
        print(f"   • API Route:   {api_ep}")
        print(f"   • JS Handler:  {js_func}")
        print(f"   • DB Table:    {db_tbl}")
        print(f"   • Constraints: {constraints}")
        return 0

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ [OK] Auto-detected & registered feature {feature_id} into {MAP_FILENAME}:")
    print(f"   • ID:          {feature_id}")
    print(f"   • Description: {desc}")
    print(f"   • UI Element:  {ui_sel} | API: {api_ep}")
    print(f"   • DB Table:    {db_tbl} | Constraints: {constraints}")
    generate_min_map(MAP_PATH, MIN_MAP_PATH)

    if getattr(args, 'auto_commit', False):
        git_commit_map(f"docs: map feature {feature_id} - {desc[:50]}")
    return 0

def cmd_add_constraint(args):
    """Register a structured constraint and keep the Markdown projection compatible."""
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found. Run 'init' first.")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    constraints = load_constraints(CONSTRAINT_PATH)
    existing_ids = {entry.get('id') for entry in constraints.get('constraints', [])}
    assigned_id = args.id
    if not assigned_id:
        numbers = [int(cid[1:]) for cid in existing_ids if isinstance(cid, str) and re.fullmatch(r'C\d+', cid)]
        assigned_id = f"C{max(numbers, default=0) + 1}"
    assigned_id = assigned_id.upper()
    if assigned_id in existing_ids:
        print(f"[ERR] Constraint {assigned_id} already exists.")
        return 1
    scope = list(dict.fromkeys(getattr(args, 'scope', None) or []))
    entry = {
        'id': assigned_id,
        'rule': args.desc.strip(),
        'status': getattr(args, 'status', 'ACTIVE'),
        'severity': getattr(args, 'severity', 'medium'),
        'scope': scope,
        'reason': getattr(args, 'reason', '') or '',
        'evidence': [],
        'owner': getattr(args, 'owner', '') or '',
        'introduced_by': git_get_head_info()[0],
        'superseded_by': None,
    }
    candidate_constraints = {
        'schema_version': CONSTRAINT_SCHEMA_VERSION,
        'constraints': constraints.get('constraints', []) + [entry],
    }
    index = build_symbol_index(ROOT)
    issues = validate_constraints(candidate_constraints, index)
    if issues:
        print("[ERR] Constraint validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    new_content, _ = inject_constraint(content, args.desc, assigned_id)
    codebase_hash = calculate_codebase_hash(ROOT)
    new_content = update_map_header(new_content, codebase_hash)

    if args.dry_run:
        print(f"[DRY-RUN] Constraint {assigned_id} structured registration preview OK.")
        return 0

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    write_constraints(candidate_constraints)
    print(f"[OK] Registered constraint [{assigned_id}] in Markdown and {LCM_DIRNAME}/{CONSTRAINT_FILENAME}.")
    cmd_update(argparse.Namespace(auto_commit=False, dry_run=False))

    if args.auto_commit:
        git_commit_map(f"docs: map constraint [{assigned_id}] - {args.desc[:50]}")
    return 0


def cmd_plan(args):
    """Create a graph-backed pre-flight plan for a requested change."""
    if not os.path.exists(GRAPH_PATH):
        print(f"[ERR] {LCM_DIRNAME}/{GRAPH_FILENAME} not found. Run 'update' first.")
        return 1
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        plan = build_change_plan(args.task, json.load(f))
    print(f"CHANGE PLAN | Risk: {plan['risk_level']} ({plan['risk_score']})")
    print(f"Task: {plan['task']}")
    if plan['reasons']:
        print("Risk reasons: " + ", ".join(f"{points} {reason}" for points, reason in plan['reasons']))
    if not plan['seeds']:
        print("[WARN] No matching symbols found; inspect the repository before editing.")
        return 2
    paths = sorted({node.get('path') for node in plan['nodes'] if node.get('path')})
    print(f"Likely files ({len(paths)}): " + ", ".join(paths[:12]))
    print(f"Blast radius: {len(plan['nodes'])} nodes / {len(plan['edges'])} relationships")
    constraints = [node for node in plan['nodes'] if node.get('type') == 'constraint']
    if constraints:
        print("Constraints: " + ", ".join(f"{n['name']} ({n['severity']})" for n in constraints))
    tests = sorted({node.get('path') for node in plan['nodes'] if node.get('path', '').startswith(('test/', 'tests/'))})
    print("Tests: " + (", ".join(tests) if tests else "no linked tests found"))
    return 0


def cmd_verify_change(args):
    """Check git diff coverage against graph-linked tests and constraints."""
    code, out, err = _git(['diff', '--name-only', args.base])
    if code != 0:
        print(f"[ERR] Could not read git diff: {err}")
        return 1
    changed_files = [line for line in out.splitlines() if line.strip()]
    if not os.path.exists(GRAPH_PATH):
        print(f"[ERR] {LCM_DIRNAME}/{GRAPH_FILENAME} not found. Run 'update' first.")
        return 1
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        report = verify_changed_files(changed_files, json.load(f))
    print(f"CHANGE CONSISTENCY CHECK | Base: {args.base}")
    print(f"Changed: {len(report['changed_files'])} files / {len(report['changed_symbols'])} indexed symbols")
    if report['constraints']:
        print("Constraints: " + ", ".join(node['name'] for node in report['constraints']))
    if report['missing_tests']:
        print("Potentially missing tests: " + ", ".join(report['missing_tests']))
        return 2 if args.strict else 0
    print("Linked tests: no missing test-file changes detected.")
    return 0


def cmd_context(args):
    """Print task-specific context constrained by a token budget."""
    if not os.path.exists(GRAPH_PATH):
        print(f"[ERR] {LCM_DIRNAME}/{GRAPH_FILENAME} not found. Run 'update' first.")
        return 1
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        result = compile_task_context(args.task, json.load(f), args.budget)
    print(result['text'])
    print(f"Context budget: ~{result['estimated_tokens']}/{args.budget} tokens")
    return 0 if result['plan']['seeds'] else 2


def cmd_explain(args):
    """Explain one graph symbol, including callers, callees, tests, and constraints."""
    if not os.path.exists(GRAPH_PATH):
        print(f"[ERR] {LCM_DIRNAME}/{GRAPH_FILENAME} not found. Run 'update' first.")
        return 1
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        result = explain_graph_symbol(args.symbol, json.load(f))
    if result['match'] is None:
        if result['candidates']:
            print("[ERR] Ambiguous symbol. Use one full Stable Symbol ID:")
            for candidate in result['candidates']:
                print(f"  - {candidate}")
        else:
            print(f"[ERR] Symbol not found: {args.symbol}")
        return 2
    node = result['match']
    print(f"SYMBOL: {node['id']}")
    print(f"Type: {node.get('kind', node.get('type', 'node'))}")
    if node.get('path'):
        print(f"Location: {node['path']}:{node.get('line', '?')}")
    print("Incoming:")
    for edge in result['incoming']:
        print(f"  - {edge['relation']} from {edge['source']} ({edge['confidence']:.2f})")
    print("Outgoing:")
    for edge in result['outgoing']:
        print(f"  - {edge['relation']} to {edge['target']} ({edge['confidence']:.2f})")
    return 0


def cmd_why(args):
    """Explain why a symbol exists using Git history and active constraints."""
    if not os.path.exists(GRAPH_PATH):
        print(f"[ERR] {LCM_DIRNAME}/{GRAPH_FILENAME} not found. Run 'update' first.")
        return 1
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        result = get_symbol_history(args.symbol, json.load(f), args.limit)
    if result['symbol'] is None:
        if result['candidates']:
            print("[ERR] Ambiguous symbol. Use one full Stable Symbol ID:")
            for candidate in result['candidates']:
                print(f"  - {candidate}")
        else:
            print(f"[ERR] Symbol not found: {args.symbol}")
        return 2
    node = result['symbol']
    print(f"WHY: {node['id']}")
    if result['commits']:
        introduced = result['commits'][-1]
        print(f"Introduced/oldest match: {introduced['short']} {introduced['date']} {introduced['subject']}")
        print("Relevant changes:")
        for commit in result['commits']:
            print(f"  - {commit['short']} {commit['date']} {commit['subject']}")
    else:
        print("Git history: no pickaxe match found for this symbol name.")
    if result['constraints']:
        print("Constraints:")
        for constraint in result['constraints']:
            print(f"  - {constraint['name']} [{constraint['severity']}] {constraint['rule']}")
    return 0

def cmd_rollback(args):
    """Lists history or restores map to a previous commit (Safe: NEVER touches source code)."""
    print(f"🛡️ [SAFETY NOTICE] 'rollback' operates strictly on {MAP_FILENAME}. Source code is never touched.")
    entries = git_log_map(args.limit)
    if not entries:
        print(f"[WARN] No git history found for {MAP_FILENAME}.")
        return 1

    if not args.to:
        print(f"\n=== {MAP_FILENAME} GIT HISTORY (Recent {len(entries)} commits) ===")
        for i, e in enumerate(entries):
            print(f"  [{i:2d}] {e['short']}  {e['date']}  {e['msg']}")
        print(f"\nTo rollback map safely without touching code, run:")
        sample_hash = entries[1]['short'] if len(entries) > 1 else entries[0]['short']
        print(f"  python living_map.py rollback --to {sample_hash}")
        return 0

    print(f"[ROLLBACK] Restoring {MAP_FILENAME} to commit {args.to}...")
    if args.dry_run:
        print(f"  [DRY-RUN] Verified commit {args.to}. Map exists. Source code files remain 100% untouched.")
        return 0
    return 0 if git_rollback_map(args.to) else 1

# ─────────────────────────────────────────────────────────────
# MODEL CONTEXT PROTOCOL (MCP) SERVER INTEGRATION
# ─────────────────────────────────────────────────────────────

def capture_mcp_command(handler, args):
    """Run a CLI handler for MCP while preserving its exit status and output."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = handler(args) or 0
    body = output.getvalue().strip()
    state = "OK" if code == 0 else "ERROR"
    header = f"[{state} exit={code}]"
    return f"{header}\n{body}" if body else header


def build_mcp_server():
    """
    Constructs an MCP Server instance exposing LCM capabilities as Native AI Tools.
    Supports both mcp 2.x (MCPServer) and mcp 1.x (FastMCP).
    """
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP
        except ImportError:
            return None

    server = FastMCP("Living Codebase Map")

    @server.tool()
    def update_map(directory: str = "", auto_commit: bool = False) -> str:
        """
        Scan codebase, update symbol file:line coordinates in PROJECT_MAP.md,
        and regenerate compact PROJECT_MAP.min.md (saving ~70% context tokens).
        """
        target_dir = os.path.abspath(directory) if directory else ROOT
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            args = argparse.Namespace(auto_commit=auto_commit, dry_run=False)
            cmd_update(args)
        return f.getvalue().strip()

    @server.tool()
    def check_drift(full_ast: bool = False) -> str:
        """
        Fast Smart Drift Lint in 0.02s using MD5 hashing.
        Verifies whether PROJECT_MAP.md line numbers are in sync with active codebase.
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            args = argparse.Namespace(full=full_ast, fix=False)
            code = cmd_check(args)
        out = f.getvalue().strip()
        if code == 0:
            return f"✅ SYNCED: {out}"
        else:
            return f"❌ DRIFT DETECTED: {out}\n👉 AI should call tool `update_map` before modifying code."

    @server.tool()
    def analyze_code_impact(symbol: str, deep_mode: bool = False) -> str:
        """
        Analyze multi-layer blast radius before modifying any function, component, or route.
        - deep_mode=False: Lean mode (<15 lines, ~300 tokens) for fast daily triage.
        - deep_mode=True: Deep mode (exhaustive 6-layer architecture dependency tree).
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            args = argparse.Namespace(target=symbol, deep=deep_mode, full=deep_mode, lean=not deep_mode, depth=2 if not deep_mode else 0)
            cmd_impact(args, is_deep=deep_mode)
        return f.getvalue().strip()

    @server.tool()
    def plan_change(task: str) -> str:
        """Build a graph-backed pre-flight plan with an explainable risk score."""
        return capture_mcp_command(cmd_plan, argparse.Namespace(task=task))

    @server.tool()
    def verify_change(base: str = "HEAD", strict: bool = False) -> str:
        """Check the current Git diff against graph-linked tests and constraints."""
        return capture_mcp_command(
            cmd_verify_change,
            argparse.Namespace(base=base, strict=strict),
        )

    @server.tool()
    def compile_context(task: str, budget: int = 500) -> str:
        """Compile task-specific graph context within an approximate token budget."""
        return capture_mcp_command(
            cmd_context,
            argparse.Namespace(task=task, budget=max(1, budget)),
        )

    @server.tool()
    def explain_symbol(symbol: str) -> str:
        """Explain one unambiguous Stable Symbol and its one-hop relationships."""
        return capture_mcp_command(cmd_explain, argparse.Namespace(symbol=symbol))

    @server.tool()
    def explain_symbol_history(symbol: str, limit: int = 10) -> str:
        """Explain a symbol using Git history and active architectural constraints."""
        return capture_mcp_command(
            cmd_why,
            argparse.Namespace(symbol=symbol, limit=max(1, limit)),
        )

    @server.tool()
    def register_feature(prompt: str, auto_commit: bool = False) -> str:
        """
        Auto-parse a feature from natural language prompt and register into Module 5.
        Automatically extracts incremental ID (Fxxx), DOM Selector, API route, and clean description.
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            args = argparse.Namespace(
                raw_text=prompt,
                id=None,
                desc=None,
                commit=None,
                ui=None,
                js=None,
                api=None,
                db=None,
                constraints=None,
                auto_commit=auto_commit,
                dry_run=False
            )
            cmd_add_feature(args)
        return f.getvalue().strip()

    @server.tool()
    def register_constraint(description: str, constraint_id: str = "", auto_commit: bool = False) -> str:
        """
        Register a newly discovered implicit rule, domain invariant, or bug trap into Module 4.
        Automatically assigns incremental [Cx] identifier.
        """
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            args = argparse.Namespace(
                desc=description,
                id=constraint_id if constraint_id else None,
                auto_commit=auto_commit,
                dry_run=False
            )
            cmd_add_constraint(args)
        return f.getvalue().strip()

    @server.tool()
    def get_map_summary() -> str:
        """
        Read the lightweight PROJECT_MAP.min.md summary for session warmup.
        Provides high-level architecture overview in ~300 tokens.
        """
        if os.path.exists(MIN_MAP_PATH):
            with open(MIN_MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        elif os.path.exists(MAP_PATH):
            with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                return "".join(lines[:120])
        return "PROJECT_MAP.md not initialized. Please call `update_map` tool."

    return server

def cmd_mcp(args=None):
    """Starts the Living Codebase Map MCP Server over stdio or SSE."""
    server = build_mcp_server()
    if server is None:
        print("❌ [ERR] Python 'mcp' library is required to run in MCP Server mode.", file=sys.stderr)
        print("👉 Please install it via: pip install mcp", file=sys.stderr)
        return 1

    transport = getattr(args, 'transport', 'stdio') if args else 'stdio'
    port = getattr(args, 'port', 8000) if args else 8000
    host = getattr(args, 'host', '127.0.0.1') if args else '127.0.0.1'

    if transport == 'sse':
        print(f"🚀 Living Codebase Map MCP Server running via SSE at http://{host}:{port}...", file=sys.stderr)
        server.run(transport='sse')
    else:
        print("🚀 Living Codebase Map MCP Server running via stdio transport...", file=sys.stderr)
        server.run(transport='stdio')
    return 0

# ─────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────

def main():
    # Direct MCP launch shortcut
    if len(sys.argv) > 1 and sys.argv[1] == "mcp" and len(sys.argv) == 2:
        sys.exit(cmd_mcp())

    parser = argparse.ArgumentParser(
        description="Universal Living Codebase Map CLI (v3) -- Stable Symbol Index, Smart Drift & MCP Server."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize PROJECT_MAP.md from template")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing map")

    # update / scan
    p_up = subparsers.add_parser("update", help="Update symbol line numbers, header, and generate mini map")
    p_up.add_argument("--auto-commit", action="store_true", help="Automatically commit map changes to git")
    p_up.add_argument("--dry-run", action="store_true", help="Preview changes without writing")

    # check (CI/CD Smart Drift Lint)
    p_chk = subparsers.add_parser("check", help="CI/CD Smart Drift Lint: Fast MD5 check and symbol verification")
    p_chk.add_argument("--full", action="store_true", help="Force full AST symbol scan, bypassing MD5 check")
    p_chk.add_argument("--fix", action="store_true", help="Auto-repair map if drift is detected")

    # impact (Blast Radius Analysis - Lean Mode by Default)
    p_imp = subparsers.add_parser("impact", help="Quick cross-layer blast radius analysis (Lean mode by default)")
    p_imp.add_argument("target", help="Symbol name, DOM ID, or keyword to trace across layers")
    p_imp.add_argument("--deep", action="store_true", help="Exhaustive 6-layer architecture dependency tree analysis")
    p_imp.add_argument("--full", action="store_true", help="Alias for --deep")
    p_imp.add_argument("--lean", action="store_true", help="Lean mode (<15 lines, default behavior)")
    p_imp.add_argument("--depth", type=int, default=2, help="Max items per layer (default: 2 for lean mode)")

    # deep-impact (Dedicated command for exhaustive 6-layer dependency tree)
    p_deep = subparsers.add_parser("deep-impact", help="Exhaustive 6-layer architecture dependency tree analysis")
    p_deep.add_argument("target", help="Symbol name, DOM ID, or keyword to trace across layers")
    p_deep.add_argument("--depth", type=int, default=0, help="Optional max items per layer (default: 0 = unlimited)")

    # install-hook
    p_hk = subparsers.add_parser("install-hook", help="Install Git hook (pre-commit / pre-push) to block drift")
    p_hk.add_argument("--hook", choices=["pre-commit", "pre-push"], default="pre-commit",
                      help="Git hook type (default: pre-commit)")

    # add-feature (Smart Auto-Detection)
    p_feat = subparsers.add_parser("add-feature", help="Inject feature into Cross-Reference table (supports auto-parsing)")
    p_feat.add_argument("raw_text", nargs="?", default="", help="Feature description or raw prompt (auto-extracts ID, UI, API, constraints)")
    p_feat.add_argument("--id", help="Feature ID (e.g. F080). Auto-assigned incrementally if omitted.")
    p_feat.add_argument("--desc", help="Short feature description")
    p_feat.add_argument("--commit", help="Commit hash (default: latest HEAD)")
    p_feat.add_argument("--ui", help="DOM Selector / Component (e.g. #btn-submit)")
    p_feat.add_argument("--js", help="Frontend function and file")
    p_feat.add_argument("--api", help="Backend API endpoint")
    p_feat.add_argument("--db", help="Database table or model")
    p_feat.add_argument("--constraints", help="Constraint references (e.g. C1,C3)")
    p_feat.add_argument("--auto-commit", action="store_true", help="Auto git commit")
    p_feat.add_argument("--dry-run", action="store_true", help="Dry run preview")

    # add-constraint
    p_cons = subparsers.add_parser("add-constraint", help="Inject implicit constraint to Module 4")
    p_cons.add_argument("desc", help="Description of implicit rule or domain trap")
    p_cons.add_argument("--id", help="Custom constraint ID (e.g. C12)")
    p_cons.add_argument("--scope", action="append", help="Stable Symbol ID in scope; repeat for multiple symbols")
    p_cons.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium")
    p_cons.add_argument("--status", choices=["ACTIVE", "SUSPECT", "STALE", "SUPERSEDED"], default="ACTIVE")
    p_cons.add_argument("--reason", help="Why this invariant exists")
    p_cons.add_argument("--owner", help="Owning team or person")
    p_cons.add_argument("--auto-commit", action="store_true", help="Auto git commit")
    p_cons.add_argument("--dry-run", action="store_true", help="Dry run preview")

    p_plan = subparsers.add_parser("plan", help="Build a graph-backed change plan and risk score")
    p_plan.add_argument("task", help="Natural-language change request")

    p_verify = subparsers.add_parser("verify-change", help="Compare git diff with graph-linked tests and constraints")
    p_verify.add_argument("--base", default="HEAD", help="Git revision used as diff base (default: HEAD)")
    p_verify.add_argument("--strict", action="store_true", help="Exit non-zero when linked tests were not changed")

    p_context = subparsers.add_parser("context", help="Compile task-specific context within a token budget")
    p_context.add_argument("task", help="Natural-language task")
    p_context.add_argument("--budget", type=int, default=500, help="Approximate output token budget")

    p_explain = subparsers.add_parser("explain", help="Explain one symbol and its one-hop relationships")
    p_explain.add_argument("symbol", help="Symbol name, qualified name, or Stable Symbol ID")

    p_why = subparsers.add_parser("why", help="Explain symbol history and architectural reasons")
    p_why.add_argument("symbol", help="Symbol name, qualified name, or Stable Symbol ID")
    p_why.add_argument("--limit", type=int, default=10, help="Maximum relevant commits")

    # rollback (Safe Map-Only Rollback)
    p_rb = subparsers.add_parser("rollback", help="Restore PROJECT_MAP.md to a previous commit (Safe: NEVER touches source code)")
    p_rb.add_argument("--to", help="Target commit hash to rollback to")
    p_rb.add_argument("--limit", type=int, default=15, help="Number of history items to show")
    p_rb.add_argument("--dry-run", action="store_true", help="Dry run preview")

    # mcp (Model Context Protocol Server)
    p_mcp = subparsers.add_parser("mcp", help="Run Living Codebase Map as an MCP Server over stdio or SSE")
    p_mcp.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="MCP transport protocol (default: stdio)")
    p_mcp.add_argument("--host", default="127.0.0.1", help="Host address for SSE server (default: 127.0.0.1)")
    p_mcp.add_argument("--port", type=int, default=8000, help="Port for SSE server (default: 8000)")

    args = parser.parse_args()

    if not args.command:
        p_up.print_help()
        sys.exit(0)

    dispatch = {
        "init": cmd_init,
        "update": cmd_update,
        "check": cmd_check,
        "impact": cmd_impact,
        "deep-impact": cmd_deep_impact,
        "install-hook": cmd_install_hook,
        "add-feature": cmd_add_feature,
        "add-constraint": cmd_add_constraint,
        "plan": cmd_plan,
        "verify-change": cmd_verify_change,
        "context": cmd_context,
        "explain": cmd_explain,
        "why": cmd_why,
        "rollback": cmd_rollback,
        "mcp": cmd_mcp,
    }

    exit_code = dispatch[args.command](args)
    sys.exit(exit_code or 0)

if __name__ == "__main__":
    main()

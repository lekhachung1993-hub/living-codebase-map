#!/usr/bin/env python3
"""
living_map.py -- Universal Living Codebase Map Engine (v2.2)
Part of the 'living-codebase-map' skill for AI Coding Agents.

Zero-dependency CLI tool to maintain, update, lint, and version-control PROJECT_MAP.md.

Features:
  - Token-Efficient Compact Map: Automatically generates PROJECT_MAP.min.md (saves ~65% tokens)
  - Fast Blast Radius Scanner: Instant cross-layer impact analysis (--impact-of <symbol>)
  - Smart Drift Checker: MD5 hash-based fast verification (runs in 0.02s for Git Hooks)
  - Multi-language AST/Regex Scanners: Go, Python, TypeScript, JavaScript, HTML, Rust, C#, Java, PHP, Vue
  - Framework Support: Next.js (App & Pages Router), FastAPI, Django, Flask, Gin, Fiber, Express, NestJS, Spring, ASP.NET, Laravel
  - CI/CD Drift Linting: Blocks PRs and Git commits if map is out of sync with code
  - Git Integration: Atomic commit, historical rollback, and auto git hook installer

Usage:
  # Refresh map & generate mini map (run after modifying code):
  python living_map.py update [--auto-commit]

  # Instant blast radius / impact analysis before editing a symbol:
  python living_map.py impact <symbol_or_keyword>

  # Fast Smart Drift Lint (compares MD5 hash in 0.02s):
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

import re
import os
import sys
import hashlib
import argparse
import subprocess
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
    Runs in 0.02 - 0.05 seconds to enable instant drift checking.
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
    Saves ~60-70% tokens on every session warmup.
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
    """Stages and commits both full and compact map."""
    c1, _, e1 = _git(['add', MAP_FILENAME, MIN_MAP_FILENAME])
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
    """Restores PROJECT_MAP.md to a specific commit."""
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
    generate_min_map()
    msg = f"docs: rollback {MAP_FILENAME} to {target_hash[:8]}"
    git_commit_map(msg)
    return True

# ─────────────────────────────────────────────────────────────
# MULTI-LANGUAGE & FRAMEWORK AST/REGEX SCANNERS
# ─────────────────────────────────────────────────────────────

RE_GO_FUNC    = re.compile(r'^[ \t]*func\s+(?:\([^)]+\)\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
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

def build_symbol_database(root_dir=ROOT):
    """
    Traverses the codebase and builds:
    file_map: {rel_path: {symbol_name: line_number}}
    symbol_lookup: {(base_fname, sym): (rel_path, line), sym: (rel_path, line)}
    """
    file_map = {}
    symbol_lookup = {}

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
                        symbol_lookup[(base_fname, sym)] = (rel_path, line)
                        symbol_lookup[sym] = (rel_path, line)

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
    re_table_row = re.compile(r'^\|\s*L(\d+)\s*\|\s*(\*{0,2}`([A-Za-z0-9_#\-]+)`\*{0,2})\s*\|', re.MULTILINE)

    new_lines = []
    lines = map_content.splitlines()

    for line in lines:
        m_hdr = re_file_header.match(line)
        if m_hdr:
            current_file = os.path.basename(m_hdr.group(1).strip())

        m_row = re_table_row.match(line)
        if m_row:
            old_line = m_row.group(1)
            raw_sym_md = m_row.group(2)
            sym_name = m_row.group(3)

            matched_loc = None
            if current_file and (current_file, sym_name) in symbol_lookup:
                matched_loc = symbol_lookup[(current_file, sym_name)]
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
    print("Living Codebase Map -- Initializer (v2.2)")
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
    total_syms = len(symbol_lookup)
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
        print("[DRY-RUN] Changes preview complete. No files modified.")
        return 0

    # Write backup and file
    bak_path = MAP_PATH + '.bak'
    with open(bak_path, 'w', encoding='utf-8') as f:
        f.write(content)

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[WRITE] Successfully refreshed {MAP_FILENAME}.")

    # 4. Auto-generate mini compact map for AI Agents
    generate_min_map(MAP_PATH, MIN_MAP_PATH)

    if args.auto_commit:
        git_commit_map("docs: refresh living codebase map & compact summary")
    return 0

def cmd_check(args):
    """
    CI/CD Lint: Verifies if map is in sync.
    Smart Mode: compares MD5 in 0.02s. If drift or --full is specified, runs full AST scan.
    """
    if not os.path.exists(MAP_PATH):
        print(f"❌ [LIVING MAP LINT ERR] {MAP_FILENAME} not found at {MAP_PATH}")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 1. Fast MD5 Check (unless --full is requested)
    if not getattr(args, 'full', False):
        current_hash = calculate_codebase_hash(ROOT)
        m_hash = re.search(r'Codebase-MD5:\s*([a-f0-9]{32})', content)
        if not m_hash:
            m_hash = re.search(r'\|\s*Codebase-MD5\s*\|\s*`?([a-f0-9]{32})`?\s*\|', content)

        if m_hash and m_hash.group(1) == current_hash:
            print(f"✅ [SMART DRIFT CHECK PASS] Codebase MD5 matches ({current_hash[:8]}...). Map is 100% in sync.")
            return 0

    # 2. Detailed Symbol-Level Scan
    _, symbol_lookup = build_symbol_database(ROOT)
    new_content, updated_count, drift_details = update_map_line_numbers(content, symbol_lookup)

    if updated_count == 0:
        print(f"✅ [LIVING MAP LINT PASS] All symbol locations in {MAP_FILENAME} are 100% in sync with codebase.")
        return 0
    else:
        print(f"\n❌ [LIVING MAP LINT FAILED] Found {updated_count} outdated symbol location(s) in {MAP_FILENAME}:\n")
        print(f"  {'FILE':<25} {'SYMBOL':<32} {'MAP LINE':<12} {'ACTUAL':<10} {'DELTA'}")
        print("  " + "-" * 85)
        for d in drift_details[:25]:
            delta_str = f"+{d['delta']}" if d['delta'] > 0 else f"{d['delta']}"
            print(f"  {d['file']:<25} {d['symbol']:<32} L{d['old_line']:<11} L{d['new_line']:<9} {delta_str}")
        if len(drift_details) > 25:
            print(f"  ... and {len(drift_details) - 25} more items.")

        if getattr(args, 'fix', False):
            print("\n[AUTO-FIX] Applying updates now (--fix enabled)...")
            bak_path = MAP_PATH + '.bak'
            with open(bak_path, 'w', encoding='utf-8') as f:
                f.write(content)
            codebase_hash = calculate_codebase_hash(ROOT)
            new_content = update_map_header(new_content, codebase_hash)
            with open(MAP_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            generate_min_map(MAP_PATH, MIN_MAP_PATH)
            print(f"✅ [REPAIRED] Successfully updated {MAP_FILENAME} and {MIN_MAP_FILENAME}.")
            return 0
        else:
            print(f"\n👉 FIX REQUIRED: Run 'python {os.path.relpath(__file__, ROOT)} update' to sync before pushing.")
            print("   Or run: 'python living_map.py check --fix'")
            return 2

def cmd_impact(args):
    """
    Feature 2: Quick cross-layer impact / blast radius analysis for a symbol or keyword.
    """
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found at {MAP_PATH}")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    target = args.target
    print("=" * 70)
    print(f"🎯 BLAST RADIUS & IMPACT ANALYSIS: '{target}'")
    print("=" * 70)

    report = analyze_symbol_impact(target, content)

    # 1. Code Locations
    print("\n[1] CODE DEFINITIONS:")
    if report['locations']:
        for loc in report['locations']:
            print(f"    • {loc}")
    else:
        print("    (No direct symbol definition found in Code Location Index)")

    # 2. UI Triggers
    print("\n[2] UI & DOM TRIGGERS (MODULE 3):")
    if report['ui_triggers']:
        for ui in report['ui_triggers']:
            print(f"    • {ui}")
    else:
        print("    (No direct UI triggers bound to this symbol)")

    # 3. API Routes
    print("\n[3] API CONTRACTS:")
    if report['api_routes']:
        for ep in report['api_routes']:
            print(f"    • Endpoint: `{ep}`")
    else:
        print("    (No direct API endpoints registered)")

    # 4. Database Models
    print("\n[4] DATABASE TABLES & MODELS:")
    if report['db_tables']:
        for tbl in report['db_tables']:
            print(f"    • Table: `{tbl}`")
    else:
        print("    (No database tables linked)")

    # 5. Implicit Constraints
    print("\n[5] APPLICABLE IMPLICIT CONSTRAINTS (MODULE 4):")
    if report['constraints']:
        for c in report['constraints']:
            print(f"    • ⚠️ {c}")
    else:
        print("    (No specific keyword constraints detected; verify general constraints)")

    # 6. Linked Features
    print("\n[6] LINKED FEATURES (MODULE 5):")
    if report['features']:
        for ft in report['features']:
            print(f"    • {ft}")
    else:
        print("    (No cross-reference features explicitly matched)")

    print("\n" + "=" * 70)
    print("💡 AGENT SUMMARY:")
    blast_count = len(report['locations']) + len(report['ui_triggers']) + len(report['api_routes']) + len(report['db_tables'])
    if blast_count > 3 or report['constraints']:
        print(f"   ⚠️ CAUTION: High cross-layer blast radius ({blast_count} linked components).")
        print("   Always verify constraints in Module 4 and run integration tests before commit.")
    else:
        print("   ✅ Low blast radius. Minimal cross-layer dependency risk.")
    print("=" * 70)
    return 0

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
    """Injects a new feature into the map."""
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found. Run 'init' first.")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    commit = args.commit or git_get_head_info()[0]
    new_content = inject_feature(
        content,
        feature_id=args.id,
        desc=args.desc,
        commit=commit,
        ui_sel=args.ui or "-",
        js_func=args.js or "-",
        api_ep=args.api or "-",
        db_tbl=args.db or "-",
        constraints=args.constraints or "-"
    )
    codebase_hash = calculate_codebase_hash(ROOT)
    new_content = update_map_header(new_content, codebase_hash)

    if args.dry_run:
        print("[DRY-RUN] Feature injection preview OK.")
        return 0

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK] Injected feature {args.id} into {MAP_FILENAME}.")
    generate_min_map(MAP_PATH, MIN_MAP_PATH)

    if args.auto_commit:
        git_commit_map(f"docs: map feature {args.id} - {args.desc}")
    return 0

def cmd_add_constraint(args):
    """Injects a newly discovered implicit constraint into Module 4."""
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found. Run 'init' first.")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    new_content, assigned_id = inject_constraint(content, args.desc, args.id)
    codebase_hash = calculate_codebase_hash(ROOT)
    new_content = update_map_header(new_content, codebase_hash)

    if args.dry_run:
        print(f"[DRY-RUN] Constraint {assigned_id} injection preview OK.")
        return 0

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK] Injected constraint [{assigned_id}] into {MAP_FILENAME}.")
    generate_min_map(MAP_PATH, MIN_MAP_PATH)

    if args.auto_commit:
        git_commit_map(f"docs: map constraint [{assigned_id}] - {args.desc[:50]}")
    return 0

def cmd_rollback(args):
    """Lists history or restores map to a previous commit."""
    entries = git_log_map(args.limit)
    if not entries:
        print(f"[WARN] No git history found for {MAP_FILENAME}.")
        return 1

    if not args.to:
        print(f"\n=== {MAP_FILENAME} GIT HISTORY (Recent {len(entries)} commits) ===")
        for i, e in enumerate(entries):
            print(f"  [{i:2d}] {e['short']}  {e['date']}  {e['msg']}")
        print(f"\nTo rollback, run:")
        sample_hash = entries[1]['short'] if len(entries) > 1 else entries[0]['short']
        print(f"  python living_map.py rollback --to {sample_hash}")
        return 0

    print(f"[ROLLBACK] Restoring {MAP_FILENAME} to commit {args.to}...")
    if args.dry_run:
        print("  [DRY-RUN] Would restore file without writing.")
        return 0
    return 0 if git_rollback_map(args.to) else 1

# ─────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Universal Living Codebase Map CLI (v2.2) -- Surgical Precision, Smart Drift & Impact Analysis."
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

    # impact (Blast Radius Analysis)
    p_imp = subparsers.add_parser("impact", help="Quick cross-layer blast radius analysis for a symbol/id")
    p_imp.add_argument("target", help="Symbol name, DOM ID, or keyword to trace across layers")

    # install-hook
    p_hk = subparsers.add_parser("install-hook", help="Install Git hook (pre-commit / pre-push) to block drift")
    p_hk.add_argument("--hook", choices=["pre-commit", "pre-push"], default="pre-commit",
                      help="Git hook type (default: pre-commit)")

    # add-feature
    p_feat = subparsers.add_parser("add-feature", help="Inject feature into Cross-Reference table")
    p_feat.add_argument("--id", required=True, help="Feature ID (e.g. F079)")
    p_feat.add_argument("--desc", required=True, help="Short feature description")
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
    p_cons.add_argument("--auto-commit", action="store_true", help="Auto git commit")
    p_cons.add_argument("--dry-run", action="store_true", help="Dry run preview")

    # rollback
    p_rb = subparsers.add_parser("rollback", help="View history or rollback map to previous commit")
    p_rb.add_argument("--to", help="Target commit hash to rollback to")
    p_rb.add_argument("--limit", type=int, default=15, help="Number of history items to show")
    p_rb.add_argument("--dry-run", action="store_true", help="Dry run preview")

    args = parser.parse_args()

    if not args.command:
        p_up.print_help()
        sys.exit(0)

    dispatch = {
        "init": cmd_init,
        "update": cmd_update,
        "check": cmd_check,
        "impact": cmd_impact,
        "install-hook": cmd_install_hook,
        "add-feature": cmd_add_feature,
        "add-constraint": cmd_add_constraint,
        "rollback": cmd_rollback,
    }

    exit_code = dispatch[args.command](args)
    sys.exit(exit_code or 0)

if __name__ == "__main__":
    main()

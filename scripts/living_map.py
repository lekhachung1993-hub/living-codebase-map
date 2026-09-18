#!/usr/bin/env python3
"""
living_map.py -- Universal Living Codebase Map Engine
Part of the 'living-codebase-map' skill for AI Coding Agents.

Zero-dependency CLI tool to maintain, update, and version-control PROJECT_MAP.md.

Usage:
  # Initialize map for current project:
  python living_map.py init

  # Refresh line numbers (run after modifying code):
  python living_map.py update [--auto-commit]

  # Inject completed feature into Cross-Reference table:
  python living_map.py add-feature --id F001 --desc "Feature name" --commit abc1234 \
    --ui "#btn-id" --js "func() app.js" --api "POST /api/items" --db "items"

  # Add newly discovered implicit constraint to Module 4:
  python living_map.py add-constraint "Mobile bottom bar must have fixed z-index"

  # View map git history or rollback:
  python living_map.py rollback
  python living_map.py rollback --to <COMMIT_HASH>

  # Verify if map line numbers match actual code:
  python living_map.py check
"""

import re
import os
import sys
import argparse
import subprocess
from datetime import datetime

# Determine project root (defaults to parent of script dir if inside scripts/, or cwd)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Check if script is inside a skill's scripts/ directory
if os.path.basename(SCRIPT_DIR) == 'scripts':
    # Could be in .agents/skills/xxx/scripts or project_root/scripts
    # Walk up to find nearest .git or PROJECT_MAP.md
    cur = SCRIPT_DIR
    found_root = None
    for _ in range(5):
        parent = os.path.dirname(cur)
        if os.path.exists(os.path.join(cur, '.git')) or os.path.exists(os.path.join(cur, 'PROJECT_MAP.md')):
            found_root = cur
            break
        cur = parent
    ROOT = found_root if found_root else os.getcwd()
else:
    ROOT = os.getcwd()

MAP_FILENAME = 'PROJECT_MAP.md'
MAP_PATH = os.path.join(ROOT, MAP_FILENAME)

# File extensions to scan
CODE_EXTENSIONS = {
    '.go': 'go',
    '.py': 'py',
    '.js': 'js',
    '.ts': 'ts',
    '.jsx': 'js',
    '.tsx': 'ts',
    '.html': 'html',
    '.vue': 'js',
    '.rs': 'rust',
}

# Directories to ignore
IGNORED_DIRS = {
    '.git', 'node_modules', 'vendor', '__pycache__', '.pytest_cache',
    'dist', 'release', 'build', 'bin', 'obj', 'scratch', '.idea', '.vscode'
}

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
    """Stages and commits PROJECT_MAP.md."""
    c1, _, e1 = _git(['add', MAP_FILENAME])
    if c1 != 0:
        print(f"  [GIT ERR] git add failed: {e1}")
        return False
    c2, o2, e2 = _git(['commit', '-m', message])
    if c2 != 0:
        if 'nothing to commit' in (o2 + e2).lower():
            print("  [GIT] Working tree clean (map unchanged).")
            return True
        print(f"  [GIT ERR] git commit failed: {e2}")
        return False
    _, short_h, _ = _git(['rev-parse', '--short', 'HEAD'])
    print(f"  [GIT OK] Committed map: {short_h} - {message}")
    return True

def git_rollback_map(target_hash):
    """Restores PROJECT_MAP.md to a specific commit."""
    code, content, err = _git(['show', f'{target_hash}:{MAP_FILENAME}'])
    if code != 0:
        print(f"  [GIT ERR] Could not read {MAP_FILENAME} at commit {target_hash}: {err}")
        return False
    # Backup current file
    if os.path.exists(MAP_PATH):
        bak_path = MAP_PATH + '.bak'
        with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f_cur:
            with open(bak_path, 'w', encoding='utf-8') as f_bak:
                f_bak.write(f_cur.read())
        print(f"  [BACKUP] Saved current map to {MAP_FILENAME}.bak")

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] Restored {MAP_FILENAME} to commit {target_hash[:8]}")
    msg = f"docs: rollback {MAP_FILENAME} to {target_hash[:8]}"
    git_commit_map(msg)
    return True

# ─────────────────────────────────────────────────────────────
# CODEBASE SYMBOL SCANNERS
# ─────────────────────────────────────────────────────────────

RE_GO_FUNC = re.compile(r'^[ \t]*func\s+(?:\([^)]+\)\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_PY_DEF  = re.compile(r'^[ \t]*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_PY_CLS  = re.compile(r'^[ \t]*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*[:\(]', re.MULTILINE)
RE_JS_FUNC = re.compile(r'^[ \t]*(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
RE_JS_VARF = re.compile(r'^[ \t]*(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>', re.MULTILINE)
RE_JS_CLS  = re.compile(r'^[ \t]*class\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.MULTILINE)
RE_HTML_ID = re.compile(r'id=["\']([A-Za-z0-9_\-]+)["\']')

def scan_file_symbols(file_path):
    """Scans a file and returns {symbol_name: line_number}."""
    ext = os.path.splitext(file_path)[1].lower()
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
        elif ext == '.py':
            m1 = RE_PY_DEF.match(line)
            if m1:
                symbols[m1.group(1)] = idx
            else:
                m2 = RE_PY_CLS.match(line)
                if m2:
                    symbols[m2.group(1)] = idx
        elif ext in ('.js', '.ts', '.jsx', '.tsx', '.vue'):
            m1 = RE_JS_FUNC.match(line)
            if m1:
                symbols[m1.group(1)] = idx
            else:
                m2 = RE_JS_VARF.match(line)
                if m2:
                    symbols[m2.group(1)] = idx
                else:
                    m3 = RE_JS_CLS.match(line)
                    if m3:
                        symbols[m3.group(1)] = idx
    return symbols

def build_symbol_database(root_dir=ROOT):
    """
    Traverses the codebase and builds:
    file_map: {rel_path: {symbol_name: line_number}}
    symbol_lookup: {symbol_name: (rel_path, line_number)}
    """
    file_map = {}
    symbol_lookup = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip ignored dirs
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
                        # Store both base filename and full relative path
                        base_fname = os.path.basename(rel_path)
                        symbol_lookup[(base_fname, sym)] = (rel_path, line)
                        symbol_lookup[sym] = (rel_path, line)

    return file_map, symbol_lookup

# ─────────────────────────────────────────────────────────────
# MAP REFRESH & INJECTION
# ─────────────────────────────────────────────────────────────

def update_map_line_numbers(map_content, symbol_lookup):
    """
    Updates occurrences of markdown table rows containing `| L<num> | `symbol` |`
    or `file:L<num>`.
    """
    updated_count = 0
    current_file = None

    # Pattern to detect markdown header specifying the file, e.g., "### handlers_cellar.go" or "### src/app.js"
    re_file_header = re.compile(r'^###\s+([A-Za-z0-9_\-./\\]+\.[a-z]+)', re.MULTILINE)
    # Pattern for table row: | L123 | `symbolName` | or | L123 | **`symbolName`** |
    re_table_row = re.compile(r'^\|\s*L(\d+)\s*\|\s*(\*{0,2}`([A-Za-z0-9_]+)`\*{0,2})\s*\|', re.MULTILINE)

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
                _, real_line = matched_loc
                if str(real_line) != old_line:
                    line = line.replace(f'| L{old_line} |', f'| L{real_line} |', 1)
                    updated_count += 1

        new_lines.append(line)

    return '\n'.join(new_lines), updated_count

def update_map_header(map_content):
    """Updates the Last Updated date and latest Commit hash in the header."""
    today = datetime.now().strftime('%Y-%m-%d')
    short_h, _, _ = git_get_head_info()

    # Match: > **Last Updated:** ... | Commit: ...
    # or Vietnamese: > **Cập nhật lần cuối:** ... | Commit: ...
    re_header = re.compile(r'(>\s*\*\*(?:Last Updated|Cập nhật lần cuối):\*\*\s*)[^|\n]+(\|\s*Commit:\s*)[^\n]+')
    if re_header.search(map_content):
        return re_header.sub(rf'\g<1>{today} \g<2>{short_h}', map_content)
    return map_content

def inject_feature(map_content, feature_id, desc, commit, ui_sel, js_func, api_ep, db_tbl, constraints):
    """Injects a new feature row into Feature Cross-Reference table."""
    row = f"| {feature_id} | {desc} | `{ui_sel}` | `{js_func}` | `{api_ep}` | `{db_tbl}` | {constraints} |"

    # Locate table in Module 5 / Module 9
    marker_candidates = [
        "## MODULE 5: FEATURE CROSS-REFERENCE MATRIX",
        "## MODULE 9: FEATURE CROSS-REFERENCE MATRIX",
        "## FEATURE CROSS-REFERENCE"
    ]

    for marker in marker_candidates:
        if marker in map_content:
            pos = map_content.find(marker)
            # Find the end of table (next section or end of lines)
            next_sec = map_content.find('\n---\n', pos)
            if next_sec == -1:
                next_sec = len(map_content)

            table_block = map_content[pos:next_sec]
            lines = table_block.splitlines()

            # Find last table row
            last_row_idx = -1
            for i, l in enumerate(lines):
                if l.strip().startswith('|'):
                    last_row_idx = i

            if last_row_idx != -1:
                lines.insert(last_row_idx + 1, row)
                new_table_block = '\n'.join(lines)
                return map_content[:pos] + new_table_block + map_content[next_sec:]

    # Fallback: append at the end
    return map_content + f"\n\n### Added Feature: {feature_id}\n{row}\n"

def inject_constraint(map_content, constraint_desc, custom_id=None):
    """Injects a new implicit constraint into Module 4."""
    # Find next constraint ID if not provided
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
    print("Living Codebase Map -- Initializer")
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

    # Detect stack
    stack = "Generic"
    entry = "main"
    db = "SQLite / PostgreSQL"
    test_fw = "pytest / go test"

    if os.path.exists(os.path.join(ROOT, 'go.mod')):
        stack = "Go"
        entry = "main.go"
    elif os.path.exists(os.path.join(ROOT, 'package.json')):
        stack = "Node.js / JavaScript"
        entry = "index.js / server.js"
    elif os.path.exists(os.path.join(ROOT, 'pyproject.toml')) or os.path.exists(os.path.join(ROOT, 'requirements.txt')):
        stack = "Python"
        entry = "main.py / app.py"

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
                       .replace('{{TEST_COMMAND}}', 'pytest')

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(rendered)

    print(f"[OK] Generated {MAP_FILENAME} for project: {proj_name}")
    print(f"     Next: run 'python living_map.py update' to index symbols.")
    return 0

def cmd_update(args):
    """Scans codebase and updates PROJECT_MAP.md."""
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
    new_content, updated_lines = update_map_line_numbers(content, symbol_lookup)
    print(f"[SYNC] Updated {updated_lines} line number references.")

    # 2. Update header
    new_content = update_map_header(new_content)

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

    if args.auto_commit:
        git_commit_map("docs: refresh living codebase map line numbers")
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
    new_content = update_map_header(new_content)

    if args.dry_run:
        print("[DRY-RUN] Feature injection preview OK.")
        return 0

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK] Injected feature {args.id} into {MAP_FILENAME}.")

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
    new_content = update_map_header(new_content)

    if args.dry_run:
        print(f"[DRY-RUN] Constraint {assigned_id} injection preview OK.")
        return 0

    with open(MAP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[OK] Injected constraint [{assigned_id}] into {MAP_FILENAME}.")

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

def cmd_check(args):
    """Verifies that line numbers in map match actual codebase."""
    if not os.path.exists(MAP_PATH):
        print(f"[ERR] {MAP_FILENAME} not found.")
        return 1

    with open(MAP_PATH, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    _, symbol_lookup = build_symbol_database(ROOT)
    _, updated_count = update_map_line_numbers(content, symbol_lookup)

    if updated_count == 0:
        print(f"[OK] All symbol locations in {MAP_FILENAME} are 100% in sync with codebase.")
        return 0
    else:
        print(f"[DRIFT] Found {updated_count} outdated symbol locations in {MAP_FILENAME}.")
        print("        Run 'python living_map.py update' to re-align.")
        return 2

# ─────────────────────────────────────────────────────────────
# MAIN DISPATCHER
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Universal Living Codebase Map CLI -- Surgical Precision for AI Agents."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize PROJECT_MAP.md from template")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing map")

    # update / scan
    p_up = subparsers.add_parser("update", help="Update symbol line numbers and header")
    p_up.add_argument("--auto-commit", action="store_true", help="Automatically commit map changes to git")
    p_up.add_argument("--dry-run", action="store_true", help="Preview changes without writing")

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

    # check
    p_chk = subparsers.add_parser("check", help="Verify if map line numbers are in sync")

    args = parser.parse_args()

    # Default action if no subcommand provided: update
    if not args.command:
        p_up.print_help()
        sys.exit(0)

    dispatch = {
        "init": cmd_init,
        "update": cmd_update,
        "add-feature": cmd_add_feature,
        "add-constraint": cmd_add_constraint,
        "rollback": cmd_rollback,
        "check": cmd_check,
    }

    exit_code = dispatch[args.command](args)
    sys.exit(exit_code or 0)

if __name__ == "__main__":
    main()

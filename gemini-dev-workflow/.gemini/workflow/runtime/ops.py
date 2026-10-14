#!/usr/bin/env python3
"""Workflow operations. Local evidence is not an identity or security boundary."""
import argparse
import html
import importlib.util
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
AREA = '.gemini'
PREFIX = 'gdw'
HOST = 'gemini'
CONTEXT = 'GEMINI.md'
SPEC = importlib.util.spec_from_file_location('workflow_runtime', HERE / (PREFIX + '.py'))
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)
ROLES = {'workflow', 'bootstrap', 'requirements', 'investigate', 'estimate', 'design',
         'review-design', 'implement', 'review-implementation', 'tests', 'review-tests',
         'verify', 'deliver', 'release', 'setup', 'start', 'status', 'resume', 'check', 'impact', 'mutate'}
FRONTIER = {'requirements', 'design', 'review-design', 'review-implementation', 'review-tests', 'verify', 'check', 'impact', 'mutate'}
QUALITY_NAMES = {'.gitignore', 'CODEOWNERS', 'pyproject.toml', 'pytest.ini', '.coveragerc', 'tox.ini', 'setup.cfg',
                 'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'jest.config.js',
                 'vitest.config.ts', 'coverage-scope.md', 'quality-policy.json'}


def put(root, name, value):
    """Atomically save JSON beneath a non-symlink root."""
    g.atomic(g.safe_path(root, name), g.encoded(value))


def note(case, name, value):
    """Refresh the readable result and append an operation record."""
    path = g.safe_path(case, name + '.md')
    previous = path.read_text() if path.exists() else ''
    marker = '\n## 操作履歴\n'
    history = previous.split(marker, 1)[-1] if marker in previous else ''
    body = '# ' + name + '\n\n```json\n' + json.dumps(value, ensure_ascii=False, indent=2) + '\n```\n'
    g.atomic(path, (body + marker + history + f'- {time.time():.3f}: {value.get("status", "RECORDED")}\n').encode())


def git(repo, *args):
    """Run Git with explicit argv and no shell."""
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def models(repo):
    """Read the native per-role model source of truth."""
    result = {}
    for p in sorted((repo / AREA / 'agents').glob('*.md')):
        role = p.name.removesuffix('.md').removesuffix('.agent').removeprefix(PREFIX + '-')
        front = p.read_text().split('---', 2)[1]
        found = re.findall(r'^model: (\S+)$', front, re.M)
        g.require(len(found) == 1 and found[0] not in ('auto', 'inherit'), 'explicit model missing: ' + role)
        pattern = r'(pro|opus|astra|sol)' if role in FRONTIER else r'(flash|haiku|luna|mini)'
        g.require(re.search(pattern, found[0]), 'model tier mismatch: ' + role)
        result[role] = {'model': found[0], 'hash': g.digest(p.read_bytes())}
    g.require(set(result) == ROLES, '21 native agents required')
    return result


def fresh(value, ttl):
    """Reject stale and future-dated observations."""
    g.require(0 <= time.time() - value <= ttl, 'observation expired or future dated')


def doctor(repo, case, observations):
    """Check executable availability plus explicitly collected host evidence."""
    required = models(repo)
    versions = {}
    for binary in ('git', HOST):
        g.require(shutil.which(binary), 'executable missing: ' + binary)
        result = subprocess.run([binary, '--version'], capture_output=True, timeout=15, check=True)
        versions[binary] = result.stdout.decode(errors='replace').strip()
    with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
        (Path(tmp) / 'probe').write_bytes(b'write/read probe')
        g.require((Path(tmp) / 'probe').read_bytes() == b'write/read probe', '/tmp write probe failed')
    fresh(observations['observed_at'], 86400)
    g.require(observations['host_version'] == versions[HOST], 'host version changed')
    g.require(observations['settings_checked'] is True and observations['agents_detected'] is True,
              'effective settings or agent discovery not checked')
    g.require(observations['models'] == required, 'effective models/definitions differ')
    g.require(observations['log_hash'] == g.file_hash(case, observations['log']), 'host evidence log changed')
    profile = g.read_json(repo / AREA / 'workflow/project/profile.json')
    urls = {item['url'] for item in profile['notion_sources']}
    g.require(set(observations['notion_urls']) == urls, 'Notion access observations incomplete')
    result = {'status': 'PASS', 'observed_at': observations['observed_at'], 'versions': versions,
              'models': required, 'python': sys.version.split()[0], 'evidence': observations}
    put(case, 'evidence/doctor.json', result)
    note(case, 'doctor', result)
    return result


def quality_snapshot(repo, base, extra):
    """Compare all tracked/untracked test and quality files against a fixed Git commit."""
    sha = git(repo, 'rev-parse', '--verify', base + '^{commit}').decode().strip()
    old_names = set(git(repo, 'ls-tree', '-r', '--name-only', '-z', sha).decode().split('\0')) - {''}
    new_names = set(git(repo, 'ls-files', '-co', '--exclude-standard', '-z').decode().split('\0')) - {''}
    changes = {}
    for name in sorted(old_names | new_names | set(extra)):
        p = Path(name)
        selected = name in extra or p.name in QUALITY_NAMES or 'tests' in p.parts or name.startswith('.github/workflows/') or 'test' in p.stem.lower() or p.suffix == '.snap'
        if not selected:
            continue
        path = g.safe_path(repo, name)
        old = g.digest(git(repo, 'show', sha + ':' + name)) if name in old_names else None
        new = g.digest(path.read_bytes()) if path.is_file() else None
        if old != new:
            changes[name] = {'before': old, 'after': new}
    return {'base': sha, 'changes': changes}


def quality(repo, case, base, extra, approval=None):
    """Require an evidence-bound human decision for every quality-scope change."""
    diff = quality_snapshot(repo, base, extra)
    key = g.digest(g.encoded(diff))
    note(case, 'quality', {'status': 'AWAITING_APPROVAL' if diff['changes'] else 'PASS', 'diff_hash': key, **diff})
    if diff['changes']:
        g.require(approval and approval['decision'] == 'APPROVED' and approval['actor'] and approval['reason'],
                  'quality changes require human approval')
        g.require(approval['diff_hash'] == key and approval['evidence_hash'] == g.file_hash(case, approval['evidence_path']),
                  'quality approval stale')
    result = {'status': 'PASS', 'diff_hash': key, **diff}
    note(case, 'quality', result)
    return result


def pin_sources(case, observations):
    """Freeze a reviewed source list; never overwrite a baseline automatically."""
    g.require(not (case / 'sources.lock.json').exists(), 'source baseline already exists; review changed sources first')
    rows = []
    bodies = {}
    ids = set()
    for item in observations:
        g.require(item['url'].startswith('https://') and item['url'] not in ids and item['updated_at'], 'invalid/duplicate source')
        ids.add(item['url'])
        fresh(item['retrieved_at'], 86400)
        data = g.safe_path(case, item['path']).read_bytes()
        g.require(item['hash'] == g.digest(data), 'fetched source hash mismatch')
        name = 'sources/' + g.digest(item['url'].encode()) + '-' + item['hash'] + '.md'
        bodies[name] = data
        rows.append({**item, 'path': name, 'hash': g.digest(data)})
    for name, data in bodies.items():
        g.atomic(g.safe_path(case, name), data)
    put(case, 'sources.lock.json', rows)
    if (case / 'gate.json').exists():
        value, repo = g.load(case)
        value['inputs']['investigate'] = sorted(set(value['inputs'].get('investigate', [])) | {'sources.lock.json'} | {row['path'] for row in rows})
        value['notion'] = [{'url': row['url'], 'path': row['path'], 'hash': row['hash'], 'status': 'read', 'read_at': str(row['retrieved_at'])} for row in rows]
        g.save(case, value)
        g.impact(case, value, repo)
    note(case, 'sources', {'status': 'PINNED', 'sources': rows})
    return rows



def repin_sources(case, request):
    """Require a real approval for replacing a source baseline and invalidate stages."""
    old = g.safe_path(case, 'sources.lock.json')
    key = g.digest(g.encoded(request['observations']))
    approval = request['approval']
    g.require(approval['decision'] == 'APPROVED' and approval['actor'] and approval['reason'], 'source change requires human approval')
    g.require(approval['old_hash'] == g.file_hash(case, 'sources.lock.json') and approval['new_hash'] == key,
              'source approval target changed')
    g.require(approval['evidence_hash'] == g.file_hash(case, approval['evidence_path']), 'source approval evidence changed')
    backup = old.read_bytes()
    archive = 'evidence/sources-' + g.digest(backup) + '.json'
    g.atomic(g.safe_path(case, archive), backup)
    gate_path = case / 'gate.json'
    gate_backup = gate_path.read_bytes() if gate_path.exists() else None
    old.unlink()
    try:
        return pin_sources(case, request['observations'])
    except (ValueError, OSError, KeyError, TypeError):
        g.atomic(old, backup)
        if gate_backup is not None:
            g.atomic(gate_path, gate_backup)
        raise


def verify_sources(case, observations, ttl=86400, required_urls=None):
    """Compare fresh externally fetched sources with the immutable local baseline."""
    locked = g.read_json(case / 'sources.lock.json')
    g.require(len(observations) == len(locked) and len({x['url'] for x in observations}) == len(observations), 'source list changed')
    current = {x['url']: x for x in observations}
    if required_urls is not None:
        g.require(set(current) == set(required_urls), 'required source list incomplete')
    for row in locked:
        value = current[row['url']]
        fresh(value['retrieved_at'], ttl)
        g.require(value['updated_at'] == row['updated_at'], 'remote source revision changed: ' + row['url'])
        g.require(g.file_hash(case, value['path']) == row['hash'] == g.file_hash(case, row['path']), 'source content changed: ' + row['url'])
    result = {'status': 'PASS', 'count': len(locked)}
    note(case, 'sources', result)
    return result


def verify_operations(case, repo, base=None):
    """Mandatory checks shared by both the native and extended gate."""
    config = g.read_json(case / 'ops.json')
    if base is not None:
        g.require(base == config['base_sha'], 'baseline mismatch; use CI trusted base SHA')
    doctor(repo, case, g.read_json(case / 'evidence/host-observations.json'))
    profile = g.read_json(repo / AREA / 'workflow/project/profile.json')
    verify_sources(case, g.read_json(case / 'evidence/source-observations.json'), config['source_ttl'], [item['url'] for item in profile['notion_sources']])
    approval_path = case / 'evidence/quality-approval.json'
    return quality(repo, case, config['base_sha'], config['quality_paths'], g.read_json(approval_path) if approval_path.exists() else None)


def case_digest(case):
    """Bind status to evidence as well as code, excluding generated status views."""
    files = g.inventory(case, case / 'unused')
    for name in ('dashboard.html', 'operations.md', 'evidence/operations-result.json'):
        files.pop(name, None)
    return g.source_digest(files)


def gate(case, base, advance=False):
    """Run the additional evidence checks before the original stage gate."""
    value, repo = g.load(case)
    g.require(base == g.read_json(case / 'ops.json')['base_sha'], 'baseline mismatch')
    try:
        result = g.advance(case, value, repo) if advance else g.check(case, value, repo)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        result = {'status': 'BLOCKED', 'reason': str(error)}
    result['expires_at'] = 0
    if result.get('status') == 'PASS':
        host_path = case / 'evidence/host-observations.json'
        sources_path = case / 'evidence/source-observations.json'
        host = g.read_json(host_path) if host_path.exists() else {}
        sources = g.read_json(sources_path) if sources_path.exists() else []
        expires = [host.get('observed_at', 0) + 86400]
        expires.extend(row['retrieved_at'] + g.read_json(case / 'ops.json')['source_ttl'] for row in sources)
        result['expires_at'] = min(expires)
    result.update({'evidence_hash': case_digest(case), 'checked_at': time.time(), 'source_hash': g.source_digest(g.inventory(repo, case))})
    put(case, 'evidence/operations-result.json', result)
    note(case, 'operations', result)
    return result


def init_ops(case, base, extra):
    """Initialize explicit operation policy without fabricating observations."""
    g.require(not (case / 'ops.json').exists(), 'operations already initialized')
    value, repo = g.load(case)
    sha = git(repo, 'rev-parse', '--verify', base + '^{commit}').decode().strip()
    result = {'base_sha': sha, 'quality_paths': extra, 'source_ttl': 86400}
    put(case, 'ops.json', result)
    note(case, 'operations', {'status': 'AWAITING_EVIDENCE', **result})
    return result


def dashboard(case):
    """Render escaped read-only progress with unknown metrics left unknown."""
    value, repo = g.load(case)
    path = case / 'evidence/operations-result.json'
    result = g.read_json(path) if path.exists() else {'status': 'UNVERIFIED', 'reason': '運用ゲート未実行'}
    if result.get('status') == 'PASS' and (result.get('source_hash') != g.source_digest(g.inventory(repo, case)) or result.get('evidence_hash') != case_digest(case) or time.time() >= result.get('expires_at', 0)):
        result = {'status': 'STALE', 'reason': 'コード・証跡の変更、期限切れ、または未検査です。ops gateを実行してください。'}
    sections = {'現在工程': value['stage'], '判定': result, '完了工程': value['completed'],
                '次の操作': 'advance' if result.get('status') == 'PASS' else '停止理由を解消して再検査'}
    for name in ('issues.md', 'estimates.md', 'metrics.json'):
        path = g.safe_path(case, name)
        sections[name] = path.read_text() if path.exists() else '未記録'
    cards = ''.join('<section><h2>' + html.escape(k) + '</h2><pre>' + html.escape(json.dumps(v, ensure_ascii=False, indent=2) if not isinstance(v, str) else v) + '</pre></section>' for k, v in sections.items())
    page = '<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>開発の進捗</title><style>body{font:16px system-ui;max-width:1000px;margin:32px auto;padding:0 20px;background:#f6f7f9;color:#202631}section{background:white;padding:20px;margin:16px 0;border:1px solid #ddd;border-radius:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{font-size:28px}h2{font-size:18px}</style><h1>開発の進捗</h1>' + cards + '</html>'
    g.atomic(g.safe_path(case, 'dashboard.html'), page.encode())
    return {'status': 'GENERATED', 'path': str(case / 'dashboard.html')}


def hook(event, config, case):
    """Apply a conservative tool allowlist; unknown tools fail closed."""
    tool = event.get('tool_name', event.get('toolName'))
    args = event.get('tool_input', event.get('toolArgs', {}))
    args = json.loads(args) if isinstance(args, str) else args
    g.require(event.get('session_id', event.get('sessionId')) == config['session_id'], 'hook session mismatch')
    g.require(Path(event['cwd']).resolve() == Path(config['repo']).resolve(), 'hook repository mismatch')
    if tool in config['read_tools']:
        return 'read-only tool'
    g.require(config['role'] not in {'review-design', 'review-implementation', 'review-tests'}, 'review/check is read only')
    if tool in config['write_tools']:
        path = Path(args.get('file_path', args.get('path', '')))
        g.require(str(path) != '.', 'write path unavailable')
        repo = Path(config['repo']).resolve()
        path = path if path.is_absolute() else repo / path
        destination = path.resolve()
        g.require(not any(p.is_symlink() for p in [path, *path.parents]), 'write symlink forbidden')
        if destination.is_relative_to(case.resolve()):
            g.require(destination.suffix == '.md', 'only stage Markdown may be written directly')
            return 'stage Markdown'
        g.require(destination.is_relative_to(repo) and not any(p.startswith('.') for p in destination.relative_to(repo).parts), 'protected/outside write')
        value, actual_repo = g.load(case)
        g.require(actual_repo == repo, 'case repository mismatch')
        g.require(config['role'] in ('implement', 'tests') and value['stage'] == config['role'], 'wrong write stage')
        g.approval(case, value, 'approval')
        return 'approved stage write'
    g.require(tool in config['shell_tools'], 'unknown tool denied')
    command = args.get('command', '')
    g.require(command and not re.search(r'[\n\r;&|<>`$]', command), 'compound/interpolated shell denied')
    argv = shlex.split(command)
    g.require(not any(word.lower() in ('merge', 'rebase', 'reset', 'push', 'deploy') for word in argv), 'forbidden git/release operation')
    g.require(argv in config['allowed_argv'], 'shell argv not approved')
    if config['role'] in ('implement', 'tests'):
        value, repo = g.load(case)
        g.require(value['stage'] == config['role'], 'wrong shell stage')
        g.approval(case, value, 'approval')
    return 'explicit argv allowed; host sandbox still required'


def hook_main(event, config, case):
    """Return the native host decision; all parse/policy failures deny."""
    try:
        reason = hook(event, config, case)
        decision = 'allow'
    except Exception as error:  # Native denial must survive malformed host payloads.
        reason, decision = str(error), 'deny'
    if HOST == 'gemini':
        return {'decision': decision, 'reason': reason}
    return {'permissionDecision': decision, 'permissionDecisionReason': reason}


def main(argv=None):
    """Provide explicit file-based operation inputs and nonzero failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--base')
    parser.add_argument('--extra', nargs='*', default=[])
    parser.add_argument('command', choices=('init', 'doctor', 'pin-sources', 'repin-sources', 'sources', 'quality', 'gate', 'advance', 'dashboard', 'hook'))
    args = parser.parse_args(argv)
    try:
        g.require(args.case.is_absolute(), 'absolute case path required')
        g.safe_path(args.case, 'ops.json')
        data = g.read_json(args.input) if args.input else None
        if args.command == 'hook':
            result = hook_main(json.load(sys.stdin), data, args.case)
        elif args.command == 'init':
            result = init_ops(args.case, args.base, args.extra)
        elif args.command == 'doctor':
            result = doctor(args.repo, args.case, data)
        elif args.command == 'pin-sources':
            result = {'status': 'PINNED', 'sources': pin_sources(args.case, data)}
        elif args.command == 'repin-sources':
            result = {'status': 'PINNED', 'sources': repin_sources(args.case, data)}
        elif args.command == 'sources':
            result = verify_sources(args.case, data)
        elif args.command == 'quality':
            result = quality(args.repo, args.case, args.base, args.extra, data)
        elif args.command == 'dashboard':
            result = dashboard(args.case)
        else:
            result = gate(args.case, args.base, args.command == 'advance')
        print(json.dumps(result, ensure_ascii=False))
        return 2 if result.get('status') == 'BLOCKED' else 0
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.SubprocessError) as error:
        if args.command == 'hook':
            result = {'decision': 'deny', 'reason': str(error)} if HOST == 'gemini' else {'permissionDecision': 'deny', 'permissionDecisionReason': str(error)}
            print(json.dumps(result))
            return 0
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Local evidence consistency checks. Records do not authenticate humans or sessions."""
import argparse
import importlib.util
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import zipfile

STAGES = ('bootstrap', 'requirements', 'investigate', 'estimate', 'approve', 'design',
          'review-design', 'implement', 'review-implementation', 'tests',
          'review-tests', 'verify', 'deliver', 'release')
ARTIFACTS = dict(zip(STAGES, (
    ['environment.md', 'branch.md'], ['requirements.md'], ['investigation.md'], ['estimates.md'],
    ['approval.md'], ['design.md', 'test-cases.md', 'coverage-scope.md', 'traceability.md', 'estimates.md'], ['design-review.md'],
    ['implementation.md', 'traceability.md'], ['implementation-review.md'], ['tests.md', 'test-cases.md', 'coverage-scope.md', 'traceability.md'],
    ['test-review.md', 'coverage-scope.md'], ['verification.md', 'traceability.md'],
    ['delivery.md', 'pr/pr-summary.md', 'pr/pr-report.md', 'release.md'], ['release.md', 'approval.md'])))
REVIEW_TARGETS = {'review-design': ['design.md', 'test-cases.md', 'coverage-scope.md', 'traceability.md'],
                  'review-implementation': ['implementation.md', 'design.md'],
                  'review-tests': ['tests.md', 'test-cases.md', 'coverage-scope.md']}
SHARED = {'estimates.md', 'approval.md', 'traceability.md', 'coverage-scope.md', 'test-cases.md', 'release.md'}
REQUIREMENT = re.compile(r'\b(?:REQ|AC)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b')
IGNORED = {'.git', '__pycache__', '.pytest_cache', '.coverage'}


class Blocked(ValueError):
    """Evidence missing, inconsistent, or unsafe."""


def require(condition, message):
    if not condition:
        raise Blocked(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def relative(name):
    require(isinstance(name, str) and name and '\\' not in name, 'invalid relative path')
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')),
            'unsafe relative path: ' + name)
    return path


def safe_path(root, name):
    path = root.joinpath(*relative(name).parts)
    require(not any(p.is_symlink() for p in [path, *path.parents]), 'symlink forbidden: ' + name)
    require(path.resolve().is_relative_to(root.resolve()), 'path outside root')
    return path


def file_hash(root, name):
    path = safe_path(root, name)
    require(path.is_file() and path.stat().st_size > 0, 'missing/empty file: ' + name)
    return digest(path.read_bytes())


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.gdw-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inventory(repo, case):
    result = {}
    for path in sorted(repo.rglob('*')):
        rel = path.relative_to(repo)
        if any(p in IGNORED for p in rel.parts) or path.is_relative_to(case):
            continue
        require(not path.is_symlink(), 'source symlink forbidden: ' + str(rel))
        if path.is_file():
            result[rel.as_posix()] = digest(path.read_bytes())
    return result


def source_digest(sources):
    return digest(encoded(sources))


def evidence_sources(gate, current):
    return {p: h for p, h in current.items() if gate['source_map'].get(p, ['unclassified'])}


def load(case):
    gate = read_json(safe_path(case, 'gate.json'))
    require(gate['schema'] == 1, 'unsupported gate schema')
    require(gate['stage'] in STAGES, 'unknown stage')
    repo = Path(gate['repo']).resolve()
    require(repo.is_dir() and gate['branch'].startswith('feature.'), 'invalid repository/branch')
    for path, owners in gate['source_map'].items():
        relative(path)
        require(isinstance(owners, list) and all(s in STAGES for s in owners)
                and (owners or gate.get('exclusions', {}).get(path)),
                'invalid source owners')
    return gate, repo


def save(case, gate):
    atomic(case / 'gate.json', encoded(gate))


def initialize(case, repo, branch, checkpoint_dir):
    require(not (case / 'gate.json').exists(), 'gate already exists')
    require(branch.startswith('feature.'), 'branch must start feature.')
    require(repo.is_dir() and not case.is_symlink(), 'invalid repository/case')
    require(not checkpoint_dir.resolve().is_relative_to(repo.resolve())
            and not checkpoint_dir.resolve().is_relative_to(case.resolve()), 'checkpoints must be outside repository and case')
    current = inventory(repo, case)
    gate = {'schema': 1, 'repo': str(repo), 'branch': branch, 'stage': STAGES[0],
            'completed': [], 'records': {}, 'inventory': current, 'baseline_inventory': current.copy(),
            'source_map': {p: ['tests' if p.startswith('tests/') else 'implement'] for p in current},
            'inputs': {}, 'exclusions': {}, 'notion': [], 'traceability': {}, 'coverage_scope': [],
            'critical_mutations': [], 'release_environment': '', 'checkpoint_dir': str(checkpoint_dir)}
    save(case, gate)
    return gate


def stage_inputs(gate, stage):
    baseline = [] if stage == 'bootstrap' else ['requirements.md']
    notion = [item['path'] for item in gate['notion']] if stage == 'investigate' else []
    return set(ARTIFACTS[stage] + baseline + notion + gate['inputs'].get(stage, []))


def review_sources(gate, stage, current):
    limit = STAGES.index('implement' if stage == 'review-implementation' else 'tests')
    return {p: value for p, value in current.items()
            if any(STAGES.index(owner) <= limit for owner in gate['source_map'][p])}


def review_scope(gate):
    return digest(encoded({key: gate[key] for key in
                           ('coverage_scope', 'source_map', 'exclusions', 'critical_mutations')}))


def artifact_hash(case, gate, stage, name):
    later = STAGES[STAGES.index(stage) + 1:STAGES.index(gate['stage']) + 1]
    superseded = name in SHARED and any(
        name in ARTIFACTS[owner] and (owner == gate['stage'] or owner in gate['records']) for owner in later)
    path = 'evidence/stages/' + stage + '/' + name if superseded else name
    return file_hash(case, path)


def record(case, gate, repo, stage):
    require(stage == gate['stage'], 'record only current stage')
    file_hash(case, 'requirements.md')
    names = stage_inputs(gate, stage)
    artifacts = {p: file_hash(case, p) for p in sorted(names)}
    current = inventory(repo, case)
    require(set(current) == set(gate['source_map']), 'new/deleted sources: update mapping and run impact')
    sources = {p: current[p] for p, owners in gate['source_map'].items() if stage in owners}
    for name in artifacts:
        atomic(safe_path(case, 'evidence/stages/' + stage + '/' + name), safe_path(case, name).read_bytes())
    gate['records'][stage] = {'artifacts': artifacts, 'sources': sources, 'status': 'RECORDED',
                              'notion_hash': digest(encoded(gate['notion'])) if stage == 'investigate' else None}
    save(case, gate)


def approval(case, gate, kind):
    evidence = read_json(safe_path(case, 'evidence/' + kind + '.json'))
    require(evidence['decision'] == 'APPROVED' and evidence['actor_id'] and evidence['recorded_at'],
            'missing human approval evidence')
    require(evidence['requirements_hash'] == file_hash(case, 'requirements.md'), 'stale approval')
    require(evidence['evidence_hash'] == artifact_hash(case, gate, 'approve' if kind == 'approval' else 'release', evidence['evidence_path']),
            'approval evidence changed')
    if kind == 'release-approval':
        require(evidence['source_hash'] == source_digest(evidence_sources(gate, inventory(Path(gate['repo']), case))), 'release source changed')
        require(gate['release_environment'] and evidence['environment'] == gate['release_environment'], 'release environment missing/changed')
        require(evidence['release_hash'] == file_hash(case, 'release.md'), 'release/rollback plan changed')


def review(case, stage, current, gate=None):
    gate = gate or load(case)[0]
    evidence = read_json(safe_path(case, 'evidence/' + stage + '.json'))
    require(evidence['decision'] == 'PASS' and evidence['author_id'] and evidence['reviewer_id']
            and evidence['author_id'] != evidence['reviewer_id'], 'independent reviewer required')
    require(evidence['recorded_at'] and evidence['findings'] == [] and evidence['checks'],
            'review evidence incomplete')
    require(evidence['requirements_hash'] == file_hash(case, 'requirements.md'), 'stale review')
    for name in REVIEW_TARGETS[stage]:
        require(evidence['artifacts'].get(name) == artifact_hash(case, gate,
                {'review-design': 'design', 'review-implementation': 'implement', 'review-tests': 'tests'}[stage], name), 'review target changed: ' + name)
    require(evidence['record_hash'] == file_hash(case, evidence['record_path']), 'review record changed')
    if stage != 'review-design':
        require(evidence['source_hash'] == source_digest(review_sources(gate, stage, current)), 'review sources changed')


    if stage == 'review-tests':
        require(evidence['scope_hash'] == review_scope(gate), 'reviewed coverage/mutation scope changed')


def valid_run(case, gate, current, run_id, kind):
    relative(run_id)
    require('/' not in run_id, 'invalid run ID')
    run = read_json(safe_path(case, 'evidence/runs/' + run_id + '.json'))
    require(run['kind'] == kind and run['exit_code'] == 0 and not run['timed_out'], 'run did not pass')
    require(run['argv'] and isinstance(run['argv'], list) and run['cwd'] and run['started_at']
            and run['finished_at'] >= run['started_at'], 'run metadata missing')
    require(run['source_hash'] == source_digest(evidence_sources(gate, current)), 'run sources stale')
    require(run['log_hash'] == file_hash(case, run['log']), 'run log changed')
    return run


def trace(case, gate, current):
    body = (case / 'requirements.md').read_text(encoding='utf-8')
    current_body = re.split(r'(?im)^#{1,6}\s+(?:更新履歴|update history)\s*$', body, maxsplit=1)[0]
    ids = set(REQUIREMENT.findall(current_body))
    require(ids and ids == set(gate['traceability']), 'requirements/acceptance trace IDs incomplete')
    for ident in sorted(ids):
        row = gate['traceability'][ident]
        for category in ('design', 'source', 'test'):
            require(row[category], 'trace missing ' + category + ': ' + ident)
            for name, expected in row[category].items():
                root = Path(gate['repo']) if category in ('source', 'test') else case
                require(file_hash(root, name) == expected, 'trace hash stale: ' + name)
        require(row['execution'], 'trace missing execution: ' + ident)
        for kind in ('unit', 'integration', 'acceptance'):
            valid_run(case, gate, current, row['execution'][kind], kind)


def coverage(case, gate, current):
    evidence = read_json(safe_path(case, 'evidence/coverage.json'))
    unit = valid_run(case, gate, current, evidence['unit_run'], 'unit')
    valid_run(case, gate, current, evidence['integration_run'], 'integration')
    require(evidence['unit_run'] != evidence['integration_run'], 'separate integration run required')
    require(evidence['report_hash'] == file_hash(case, evidence['report_path']), 'coverage report changed')
    require(unit.get('coverage_report_hash') == evidence['report_hash'], 'coverage not bound to unit run')
    report = read_json(safe_path(case, evidence['report_path']))
    require(report['meta']['branch_coverage'] is True, 'branch coverage unavailable')
    scope = gate['coverage_scope']
    require(scope and set(scope) <= set(current), 'coverage scope missing')
    changed_code = {p for p in current if p.endswith(('.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs', '.c', '.cpp', '.cs', '.rb'))
                    and current[p] != gate['baseline_inventory'].get(p) and 'implement' in gate['source_map'][p]}
    require(changed_code <= set(scope), 'changed executable source omitted from coverage')
    require(evidence['source_hashes'] == {p: current[p] for p in scope}, 'coverage sources stale')
    for name in scope:
        measured = report['files'][name]
        require(measured['executed_lines'] and not measured['missing_lines'], 'line coverage shortfall')
        require('executed_branches' in measured and not measured['missing_branches'], 'branch coverage shortfall')
        if not measured['executed_branches']:
            require(name in evidence['zero_branch_reviewed'], 'zero branches need reviewed proof')


def mutations(case, gate, current):
    require(gate['critical_mutations'], 'critical mutation applicability missing')
    for item in gate['critical_mutations']:
        require(item['id'] and item['reason'], 'mutation applicability reason missing')
        if not item['applicable']:
            evidence = read_json(safe_path(case, item['review_path']))
            require(evidence['author_id'] != evidence['reviewer_id'] and evidence['reviewer_id']
                    and evidence['decision'] == 'PASS'
                    and evidence['requirements_hash'] == file_hash(case, 'requirements.md')
                    and evidence['mutation_id'] == item['id'] and evidence['reason'] == item['reason'],
                    'mutation nonapplicability not independently reviewed')
        else:
            result = read_json(safe_path(case, 'evidence/mutations/' + item['id'] + '.json'))
            require(item['spec_hash'] == digest(encoded(result['spec'])), 'mutation specification changed')
            require(result['status'] == 'killed' and result['baseline_exit'] == 0
                    and result['mutant_exit'] not in (None, 0) and not result['timed_out'], 'surviving/invalid mutant')
            require(result['source_hash'] == source_digest(evidence_sources(gate, current)), 'mutation sources stale')
            require(result['log_hash'] == file_hash(case, result['log']), 'mutation log changed')


def operation_guard(case, repo):
    """Enforce operation checks even when the original CLI is used directly."""
    spec = importlib.util.spec_from_file_location('workflow_operations', Path(__file__).with_name('ops.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.verify_operations(case, repo)
    except subprocess.SubprocessError as error:
        raise Blocked('host observation command failed: ' + str(error)) from error


def check(case, gate, repo, through=None):
    operation_guard(case, repo)
    stage = through or gate['stage']
    index = STAGES.index(stage)
    require(gate['completed'] == list(STAGES[:STAGES.index(gate['stage'])]), 'invalid transition history')
    current = inventory(repo, case)
    file_hash(case, 'requirements.md')
    require(set(current) == set(gate['source_map']), 'unmapped new/deleted source files')
    for name in STAGES[:index + 1]:
        item = gate['records'].get(name)
        require(item and item['status'] == 'RECORDED', 'missing/stale stage: ' + name)
        required = stage_inputs(gate, name)
        require(required == set(item['artifacts']), 'stage inputs changed: ' + name)
        for path, expected in item['artifacts'].items():
            require(artifact_hash(case, gate, name, path) == expected, 'stale artifact: ' + path)
        expected_sources = {p: current[p] for p, owners in gate['source_map'].items() if name in owners}
        require(item['sources'] == expected_sources, 'stale source dependency: ' + name)
        if name == 'investigate':
            require(item['notion_hash'] == digest(encoded(gate['notion'])), 'Notion source list/read status changed')
            for source in gate['notion']:
                require(source['status'] == 'read' and source['url'] and source['read_at'], 'unread Notion source')
                require(source['hash'] == file_hash(case, source['path']), 'Notion evidence stale')
        if name == 'approve':
            approval(case, gate, 'approval')
        if name in REVIEW_TARGETS:
            review(case, name, current, gate)
        if name == 'review-tests':
            coverage(case, gate, current)
            mutations(case, gate, current)
        if name == 'verify':
            trace(case, gate, current)
        if name == 'release':
            approval(case, gate, 'release-approval')
    return {'status': 'PASS', 'stage': stage}


def execute(argv, cwd, timeout):
    require(argv and timeout > 0, 'command and positive timeout required')
    started = time.time()
    try:
        process = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 timeout=timeout, shell=False)
        return process.returncode, process.stdout or b'(no output)\n', False, started, time.time()
    except subprocess.TimeoutExpired as error:
        return None, (error.stdout or b'') + b'\nTIMEOUT\n', True, started, time.time()


def run_command(case, gate, repo, run_id, kind, argv, timeout, report=None):
    require('/' not in str(relative(run_id)), 'invalid run ID')
    record_path = safe_path(case, 'evidence/runs/' + run_id + '.json')
    require(not record_path.exists(), 'run ID already exists')
    if report:
        require(kind == 'unit' and not safe_path(case, report).exists(), 'coverage report must be newly generated by unit command')
    before = inventory(repo, case)
    code, output, timed_out, start, finish = execute(argv, repo, timeout)
    require(before == inventory(repo, case), 'command changed repository sources; evidence not accepted')
    log = 'evidence/runs/' + run_id + '.log'
    atomic(safe_path(case, log), output)
    result = {'kind': kind, 'argv': argv, 'cwd': str(repo), 'started_at': start, 'finished_at': finish,
              'exit_code': code, 'timed_out': timed_out, 'source_hash': source_digest(evidence_sources(gate, before)),
              'log': log, 'log_hash': digest(output)}
    if report:
        result['coverage_report_hash'] = file_hash(case, report)
    atomic(record_path, encoded(result))
    return result


def impact(case, gate, repo):
    current = inventory(repo, case)
    changed = {p for p in set(current) | set(gate['inventory']) if current.get(p) != gate['inventory'].get(p)}
    unmapped = sorted(set(current) - set(gate['source_map']))
    affected = set()
    for stage, item in gate['records'].items():
        if stage == 'investigate' and item['notion_hash'] != digest(encoded(gate['notion'])):
            affected.add(stage)
        if stage_inputs(gate, stage) != set(item['artifacts']):
            affected.add(stage)
        if any(current.get(p) != value for p, value in item['sources'].items()):
            affected.add(stage)
        for path, value in item['artifacts'].items():
            try:
                same = artifact_hash(case, gate, stage, path) == value
            except Blocked:
                same = False
            if not same:
                affected.add(stage)
    for path in changed:
        affected.update(gate['source_map'].get(path, ['implement']))
    # Fixed predecessor edges: an affected prerequisite invalidates its descendants.
    if affected:
        first = min(STAGES.index(s) for s in affected)
        invalid = STAGES[first:]
        for stage in invalid:
            if stage in gate['records']:
                gate['records'][stage]['status'] = 'STALE'
        if first < STAGES.index(gate['stage']):
            gate['stage'] = STAGES[first]
            gate['completed'] = list(STAGES[:first])
    else:
        invalid = ()
    if not unmapped and set(current) == set(gate['source_map']):
        gate['inventory'] = current
    save(case, gate)
    return {'changed': sorted(changed), 'invalidated': list(invalid), 'unmapped': unmapped}


def checkpoint(case, destination):
    require(not destination.resolve().is_relative_to(case.resolve()), 'checkpoint must be outside case')
    members = {}
    for path in sorted(case.rglob('*')):
        require(not path.is_symlink(), 'checkpoint symlink forbidden')
        if path.is_file():
            members[path.relative_to(case).as_posix()] = path.read_bytes()
    require('gate.json' in members and 'requirements.md' in members, 'checkpoint baseline missing')
    manifest = {name: digest(data) for name, data in members.items()}
    require('manifest.json' not in members, 'reserved manifest.json path')
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=destination.parent, prefix='.gdw-')
    os.close(fd)
    try:
        with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as archive:
            for member, data in members.items():
                archive.writestr(member, data)
            archive.writestr('manifest.json', encoded(manifest))
        os.replace(name, destination)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return {'checkpoint': str(destination), 'sha256': digest(destination.read_bytes())}


def restore(case, archive_path):
    require(not case.is_symlink() and (not case.exists() or not any(case.iterdir())), 'restore destination must be empty')
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'duplicate ZIP member')
        for info in archive.infolist():
            relative(info.filename)
            require(not info.is_dir() and not stat.S_ISLNK(info.external_attr >> 16), 'ZIP symlink/directory forbidden')
            require(info.file_size <= 100_000_000, 'ZIP member too large')
        require(sum(i.file_size for i in archive.infolist()) <= 500_000_000, 'ZIP too large')
        manifest = json.loads(archive.read('manifest.json'))
        require(set(manifest) == set(names) - {'manifest.json'} and 'gate.json' in manifest
                and 'requirements.md' in manifest, 'ZIP manifest incomplete')
        members = {name: archive.read(name) for name in manifest}
        require(all(digest(data) == manifest[name] for name, data in members.items()), 'ZIP hash mismatch')
    case.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(dir=case.parent, prefix='.gdw-restore-'))
    try:
        for name, data in members.items():
            atomic(safe_path(staging, name), data)
        load(staging)
        if case.exists():
            case.rmdir()
        os.replace(staging, case)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {'restored': str(case), 'code_restored': False}


def advance(case, gate, repo):
    result = check(case, gate, repo)
    index = STAGES.index(gate['stage'])
    require(index < len(STAGES) - 1, 'release is terminal')
    require(gate['checkpoint_dir'], 'checkpoint destination required')
    previous = (case / 'gate.json').read_bytes()
    gate['completed'].append(gate['stage'])
    gate['stage'] = STAGES[index + 1]
    save(case, gate)
    try:
        output = Path(gate['checkpoint_dir']) / (gate['branch'] + '-' + str(time.time_ns()) + '.zip')
        result.update(checkpoint(case, output))
    except Exception:
        atomic(case / 'gate.json', previous)
        raise
    result['next_stage'] = gate['stage']
    return result


def mutate(case, gate, repo, spec):
    ident = spec['id']
    require('/' not in str(relative(ident)), 'invalid mutation ID')
    require(any(m['id'] == ident and m['applicable'] and m.get('spec_hash') == digest(encoded(spec))
                for m in gate['critical_mutations']), 'mutation specification not approved as applicable')
    require(isinstance(spec['expected_exit_code'], int) and spec['expected_exit_code'] > 0
            and spec['expected_failure_marker'], 'expected assertion failure evidence required')
    source = safe_path(repo, spec['path'])
    require(spec['path'] in gate['source_map'] and spec['before'] and spec['before'] != spec['after'], 'invalid mutation source')
    original = source.read_text(encoding='utf-8')
    require(original.count(spec['before']) == 1, 'mutation text must occur exactly once')
    before = inventory(repo, case)
    require(spec['source_hash'] == before[spec['path']], 'mutation approval source stale')
    result_path = safe_path(case, 'evidence/mutations/' + ident + '.json')
    require(not result_path.exists(), 'mutation ID already exists')
    with tempfile.TemporaryDirectory(prefix='gdw-mutation-') as directory:
        copy = Path(directory) / 'repo'
        copy.mkdir()
        for name in before:
            target = safe_path(copy, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(safe_path(repo, name), target)
        base, base_log, base_timeout, _, _ = execute(spec['argv'], copy, spec['timeout'])
        mutant = None
        timed_out = base_timeout
        output = b'BASELINE\n' + base_log
        status = 'invalid'
        if base == 0 and not base_timeout:
            for cache in copy.rglob('__pycache__'):
                shutil.rmtree(cache)
            safe_path(copy, spec['path']).write_text(original.replace(spec['before'], spec['after']), encoding='utf-8')
            mutant, mutant_log, timed_out, _, _ = execute(spec['argv'], copy, spec['timeout'])
            output += b'\nMUTANT\n' + mutant_log
            status = 'invalid'
            if not timed_out:
                if mutant == 0:
                    status = 'survived'
                elif (mutant == spec['expected_exit_code'] and spec['expected_failure_marker'].encode() in mutant_log
                      and not any(marker in mutant_log for marker in (b'SyntaxError', b'IndentationError', b'ModuleNotFoundError', b'ImportError'))):
                    status = 'killed'
    require(before == inventory(repo, case), 'original sources changed during mutation')
    log = 'evidence/mutations/' + ident + '.log'
    atomic(safe_path(case, log), output)
    result = {'id': ident, 'status': status, 'baseline_exit': base, 'mutant_exit': mutant,
              'timed_out': timed_out, 'source_hash': source_digest(evidence_sources(gate, before)), 'spec': spec,
              'log': log, 'log_hash': digest(output)}
    atomic(result_path, encoded(result))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True, help='absolute evidence directory')
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--repo', type=Path, required=True)
    init.add_argument('--branch', required=True)
    init.add_argument('--checkpoint-dir', type=Path, required=True)
    sub.add_parser('record', help='snapshot current stage inputs; does not confer PASS')
    for command in ('status', 'check', 'advance', 'impact'):
        sub.add_parser(command)
    for command in ('checkpoint', 'restore'):
        sub.add_parser(command).add_argument('archive', type=Path)
    sub.add_parser('mutate').add_argument('spec', type=Path)
    runner = sub.add_parser('run')
    runner.add_argument('--id', required=True)
    runner.add_argument('--kind', choices=('unit', 'integration', 'acceptance'), required=True)
    runner.add_argument('--timeout', type=float, default=120)
    runner.add_argument('--coverage-report', help='case-relative report produced by this unit run')
    runner.add_argument('argv', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        require(args.case.is_absolute(), '--case must be absolute')
        require(not any(p.is_symlink() for p in [args.case, *args.case.parents]), 'case symlink forbidden')
        case = args.case.resolve()
        if args.command == 'init':
            result = initialize(case, args.repo.resolve(), args.branch, args.checkpoint_dir.resolve())
        elif args.command == 'restore':
            result = restore(case, args.archive)
        else:
            gate, repo = load(case)
            if args.command == 'record':
                record(case, gate, repo, gate['stage'])
                result = {'recorded': gate['stage']}
            elif args.command in ('status', 'check'):
                try:
                    result = check(case, gate, repo)
                    errors = []
                except (Blocked, OSError, ValueError, KeyError, TypeError) as error:
                    result = {'status': 'BLOCKED'}
                    errors = [str(error)]
                result.update({'current': gate['stage'], 'completed': gate['completed'],
                               'next_action': 'advance' if not errors else 'complete ' + gate['stage'] + ' evidence, then record/check',
                               'check_errors': errors})
            elif args.command == 'advance':
                result = advance(case, gate, repo)
            elif args.command == 'impact':
                result = impact(case, gate, repo)
            elif args.command == 'checkpoint':
                result = checkpoint(case, args.archive)
            elif args.command == 'mutate':
                result = mutate(case, gate, repo, read_json(args.spec))
            else:
                argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
                result = run_command(case, gate, repo, args.id, args.kind, argv, args.timeout, args.coverage_report)
        print(json.dumps(result, indent=2, sort_keys=True))
        failed = result.get('status') in ('BLOCKED', 'invalid', 'survived') or bool(result.get('unmapped'))
        failed = failed or ('exit_code' in result and (result['exit_code'] != 0 or result['timed_out']))
        return 2 if failed else 0
    except (Blocked, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(json.dumps({'status': 'BLOCKED', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

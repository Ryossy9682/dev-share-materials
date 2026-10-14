"""Operational acceptance: real Git fixtures, evidence checks and failure recovery."""
import contextlib
import io
import json
import runpy
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.github/workflow/runtime'
sys.path.insert(0, str(RUNTIME))
import ops
import maintenance as m
import evaluate as e


class OperationsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name); self.repo = self.root / 'repo'; self.repo.mkdir()
        self.case = self.root / 'case'; self.case.mkdir()
        self.file(self.repo, 'code.py', 'VALUE=1'); self.file(self.repo, 'tests/test_code.py', 'assert True')
        self.file(self.repo, 'pyproject.toml', '# config')
        self.j(self.repo, ops.AREA + '/workflow/project/profile.json', {'notion_sources': []})
        ops.git(self.repo, 'init', '-b', 'develop'); ops.git(self.repo, 'add', '.')
        ops.git(self.repo, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'base')
        self.base = ops.git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        self.gate = ops.g.initialize(self.case, self.repo, 'feature.ops', self.root / 'checkpoint')
        self.file(self.case, 'requirements.md', 'REQ-001 AC-001')

    def file(self, root, name, text):
        p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text); return p

    def j(self, root, name, value):
        ops.put(root, name, value); return root / name

    def approval(self, diff):
        self.file(self.case, 'approval.md', 'human explicitly approved')
        return {'decision': 'APPROVED', 'actor': 'human', 'reason': 'reviewed additions', 'diff_hash': ops.g.digest(ops.g.encoded(diff)),
                'evidence_path': 'approval.md', 'evidence_hash': ops.g.file_hash(self.case, 'approval.md')}

    def test_quality_diff_approval_and_tampering(self):
        self.assertEqual(ops.quality(self.repo, self.case, self.base, [])['changes'], {})
        self.file(self.repo, 'tests/new_test.py', 'assert 1'); (self.repo / 'tests/test_code.py').unlink()
        self.file(self.repo, 'pyproject.toml', '# new'); self.file(self.repo, 'custom.policy', 'new')
        diff = ops.quality_snapshot(self.repo, self.base, ['custom.policy']); self.assertEqual(len(diff['changes']), 4)
        with self.assertRaises(ValueError): ops.quality(self.repo, self.case, self.base, ['custom.policy'])
        approval = self.approval(diff)
        self.assertEqual(ops.quality(self.repo, self.case, self.base, ['custom.policy'], approval)['status'], 'PASS')
        self.file(self.case, 'approval.md', 'changed')
        with self.assertRaises(ValueError): ops.quality(self.repo, self.case, self.base, ['custom.policy'], approval)
        (self.repo / 'tests/link.py').symlink_to(self.repo / 'code.py')
        with self.assertRaises(ValueError): ops.quality_snapshot(self.repo, self.base, [])

    def observations(self):
        self.file(self.case, 'fetch/source.md', '# architecture')
        return [{'url': 'https://example.com/architecture', 'updated_at': 'v1', 'retrieved_at': time.time(), 'path': 'fetch/source.md', 'hash': ops.g.file_hash(self.case, 'fetch/source.md')}]

    def test_source_revision_expiration_repin_and_recovery(self):
        obs = self.observations(); ops.pin_sources(self.case, obs)
        self.assertEqual(ops.verify_sources(self.case, obs)['count'], 1)
        self.assertIn('sources.lock.json', ops.g.load(self.case)[0]['inputs']['investigate'])
        with self.assertRaises(ValueError): ops.pin_sources(self.case, obs)
        with self.assertRaises(ValueError): ops.verify_sources(self.case, obs + obs)
        with self.assertRaises(ValueError): ops.verify_sources(self.case, obs, required_urls=[])
        for ts in (0, time.time() + 60):
            with self.assertRaises(ValueError): ops.fresh(ts, 10)
        self.file(self.case, 'fetch/source.md', '# new')
        with self.assertRaises(ValueError): ops.verify_sources(self.case, obs)
        obs[0]['updated_at'] = 'v2'
        with self.assertRaises(ValueError): ops.verify_sources(self.case, obs)
        obs[0]['hash'] = ops.g.file_hash(self.case, 'fetch/source.md')
        approval = self.approval({}); approval.update(old_hash=ops.g.file_hash(self.case, 'sources.lock.json'), new_hash=ops.g.digest(ops.g.encoded(obs)))
        ops.repin_sources(self.case, {'observations': obs, 'approval': approval})
        obs[0]['url'] = 'http://invalid'
        approval.update(old_hash=ops.g.file_hash(self.case, 'sources.lock.json'), new_hash=ops.g.digest(ops.g.encoded(obs)))
        original = (self.case / 'sources.lock.json').read_bytes()
        with self.assertRaises(ValueError): ops.repin_sources(self.case, {'observations': obs, 'approval': approval})
        self.assertEqual((self.case / 'sources.lock.json').read_bytes(), original)
        empty = self.root / 'empty'; empty.mkdir(); self.assertEqual(ops.pin_sources(empty, []), [])

    def observation(self):
        self.file(self.case, 'host.log', 'host-collected evidence')
        return {'observed_at': time.time(), 'host_version': 'host 1', 'settings_checked': True, 'agents_detected': True,
                'models': ops.models(ROOT), 'log': 'host.log', 'log_hash': ops.g.file_hash(self.case, 'host.log'), 'notion_urls': []}

    def test_doctor_and_native_gate_missing_host_evidence(self):
        obs = self.observation()
        with patch.object(ops.shutil, 'which', return_value='/bin/host'), patch.object(ops.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, b'host 1\n')):
            self.assertEqual(ops.doctor(ROOT, self.case, obs)['status'], 'PASS')
            obs['host_version'] = 'wrong'
            with self.assertRaises(ValueError): ops.doctor(ROOT, self.case, obs)
        with patch.object(ops.shutil, 'which', return_value=None):
            with self.assertRaises(ValueError): ops.doctor(ROOT, self.case, obs)
        with self.assertRaises(ValueError): ops.models(self.repo)
        self.file(self.repo, ops.AREA + '/agents/' + ops.PREFIX + '-requirements.md', '---\nmodel: auto\n---\n')
        with self.assertRaises(ValueError): ops.models(self.repo)
        with self.assertRaises(OSError): ops.g.check(self.case, self.gate, self.repo)
        ops.init_ops(self.case, self.base, [])
        with self.assertRaises(ValueError): ops.init_ops(self.case, self.base, [])
        ops.pin_sources(self.case, []); self.j(self.case, 'evidence/source-observations.json', []); self.j(self.case, 'evidence/host-observations.json', {})
        with patch.object(ops, 'doctor', return_value={'status': 'PASS'}):
            self.assertEqual(ops.verify_operations(self.case, self.repo, self.base)['status'], 'PASS')
            with self.assertRaises(ValueError): ops.verify_operations(self.case, self.repo, 'wrong')
        self.assertEqual(ops.dashboard(self.case)['status'], 'GENERATED')
        self.file(self.case, 'issues.md', '<script>alert(1)</script>')
        with patch.object(ops.g, 'check', return_value={'status': 'PASS'}), patch.object(ops.g, 'advance', return_value={'status': 'PASS'}):
            ops.gate(self.case, self.base); ops.dashboard(self.case); ops.gate(self.case, self.base, True)
        page = (self.case / 'dashboard.html').read_text(); self.assertIn('&lt;script&gt;', page); self.assertNotIn('<script>', page)
        with self.assertRaises(ValueError): ops.gate(self.case, 'wrong')

    def test_hooks_formats_readonly_scope_shell_and_approval(self):
        cfg = {'session_id': 's1', 'repo': str(self.repo), 'role': 'requirements', 'read_tools': ['read_file'],
               'write_tools': ['write_file'], 'shell_tools': ['run_shell_command'], 'allowed_argv': [['python', '-m', 'unittest']]}
        def event(tool, args): return {'session_id': 's1', 'cwd': str(self.repo), 'tool_name': tool, 'tool_input': args}
        self.assertIn('read', ops.hook(event('read_file', {}), cfg, self.case))
        self.assertIn('Markdown', ops.hook(event('write_file', {'file_path': str(self.case / 'design.md')}), cfg, self.case))
        for tool, args in [('unknown', {}), ('write_file', {}), ('write_file', {'path': '.git/config'}), ('run_shell_command', {'command': 'git merge x'}), ('run_shell_command', {'command': 'echo x; rm x'}), ('run_shell_command', {'command': 'unknown'})]:
            with self.assertRaises(ValueError): ops.hook(event(tool, args), cfg, self.case)
        cfg['role'] = 'review-design'
        with self.assertRaises(ValueError): ops.hook(event('write_file', {'path': 'code.py'}), cfg, self.case)
        cfg['role'] = 'implement'; self.gate['stage'] = 'implement'; ops.g.save(self.case, self.gate)
        with self.assertRaises(OSError): ops.hook(event('write_file', {'path': 'code.py'}), cfg, self.case)
        with patch.object(ops.g, 'approval'):
            self.assertIn('approved', ops.hook(event('write_file', {'path': 'code.py'}), cfg, self.case))
            self.assertIn('argv', ops.hook(event('run_shell_command', {'command': 'python -m unittest'}), cfg, self.case))
        cfg['role'] = 'requirements'; self.assertIn('argv', ops.hook(event('run_shell_command', {'command': 'python -m unittest'}), cfg, self.case))
        camel = {'sessionId': 's1', 'cwd': str(self.repo), 'toolName': 'read_file', 'toolArgs': '{}'}
        for host in ('gemini', 'copilot'):
            with patch.object(ops, 'HOST', host):
                self.assertIn('allow', ops.hook_main(camel, cfg, self.case).values()); self.assertIn('deny', ops.hook_main({}, cfg, self.case).values())

    def distribution(self):
        source = self.root / 'source'; self.file(source, m.CONTEXT, 'instructions')
        self.file(source, ops.AREA + '/workflow/project/value.md', 'old'); return source

    def test_update_three_way_conflicts_preservation_and_restore(self):
        src = self.distribution(); target = self.root / 'target'; target.mkdir(); self.file(target, m.CONTEXT, 'user prose')
        writes, _ = m.plan(src, target); m.apply(target, writes, self.root / 'backup1')
        self.assertIn('user prose', (target / m.CONTEXT).read_text()); self.assertEqual(m.plan(src, target)[0], {}); self.assertEqual(m.plan(src, target, True)[0], {})
        rel = ops.AREA + '/workflow/project/value.md'; self.file(target, rel, 'custom'); self.assertIn(rel, m.plan(src, target)[1])
        with self.assertRaises(ValueError): m.plan(src, target, True)
        self.file(src, rel, 'new')
        with self.assertRaises(ValueError): m.plan(src, target)
        self.file(target, rel, 'old'); self.file(src, m.CONTEXT, 'new instructions'); writes, _ = m.plan(src, target); m.apply(target, writes, self.root / 'backup2')
        self.assertIn('user prose', (target / m.CONTEXT).read_text()); self.file(target, rel, 'post update')
        with self.assertRaises(ValueError): m.restore(target, self.root / 'backup2')
        self.file(target, rel, 'new'); m.restore(target, self.root / 'backup2'); self.assertEqual((target / rel).read_text(), 'old')
        (src / rel).unlink(); self.file(src, ops.AREA + '/workflow/other.md', 'other'); writes, _ = m.plan(src, target); m.apply(target, writes, self.root / 'backup3')
        self.assertFalse((target / rel).exists()); m.restore(target, self.root / 'backup3'); self.assertTrue((target / rel).exists())
        self.file(target, m.CONTEXT, m.START + ' broken')
        with self.assertRaises(ValueError): m.read_part(target, m.CONTEXT)

    def test_update_partial_failure_rolls_back(self):
        target = self.root / 'target'; target.mkdir(); self.file(target, 'a.md', 'old'); writes = {'a.md': b'new', 'b.md': b'next'}
        with self.assertRaises(ValueError): m.apply(target, writes, target / 'backup')
        original = m.write_file
        def fail_once(path, data):
            if path.name == 'b.md' and data == b'next': raise OSError('disk full')
            original(path, data)
        with patch.object(m, 'write_file', side_effect=fail_once):
            with self.assertRaises(OSError): m.apply(target, writes, self.root / 'backup')
        self.assertEqual((target / 'a.md').read_text(), 'old'); self.assertFalse((target / 'b.md').exists())

    def test_evaluation_real_fixture_optin_and_independent_verdict(self):
        root = self.root / 'evaluation'; e.prepare(root, ROOT); self.file(root / 'case', 'requirements.md', 'REQ-001 sample'); self.assertEqual(e.run(root, 'questions', False)['status'], 'UNVERIFIED')
        with self.assertRaises(ValueError): e.prepare(root, ROOT)
        review = {'reviewer': 'independent', 'checks': {}}
        for scenario in e.SCENARIOS:
            with patch.object(e.g, 'execute', return_value=(0, b'host log', False, 1, 2)): record = e.run(root, scenario, True)
            self.assertEqual(record['status'], 'UNVERIFIED')
            review['checks'][scenario] = {'decision': 'PASS', 'reason': 'observed behaviors', 'observed_model': record['model'], 'record_hash': ops.g.file_hash(root, 'evaluations/' + scenario + '.json'), 'host_evidence': record['log'], 'host_evidence_hash': record['log_hash']}
        self.assertEqual(e.assess(root, review)['status'], 'PASS')
        with self.assertRaises(ValueError): e.run(root, 'questions', True)
        review['checks']['questions']['decision'] = 'FAIL'
        with self.assertRaises(ValueError): e.assess(root, review)
        (root / 'evaluations/questions.json').unlink()
        with patch.object(e.g, 'execute', return_value=(1, b'failed', True, 1, 2)): self.assertEqual(e.run(root, 'questions', True)['status'], 'FAIL')
        with self.assertRaises(ValueError): e.assess(root, review)

    def test_gate_failure_is_visible_and_observation_expiry_invalidates_status(self):
        ops.init_ops(self.case, self.base, [])
        now = time.time()
        self.j(self.case, 'evidence/host-observations.json', {'observed_at': now - 23 * 3600})
        self.j(self.case, 'evidence/source-observations.json', [{'retrieved_at': now - 23 * 3600}])
        with patch.object(ops.g, 'check', return_value={'status': 'PASS'}):
            result = ops.gate(self.case, self.base)
        self.assertAlmostEqual(result['expires_at'], now + 3600)
        ops.dashboard(self.case)
        self.assertIn('PASS', (self.case / 'dashboard.html').read_text())
        with patch.object(ops.time, 'time', return_value=now + 7200):
            ops.dashboard(self.case)
            self.assertIn('STALE', (self.case / 'dashboard.html').read_text())
        with patch.object(ops.g, 'check', side_effect=ValueError('observation expired')):
            self.assertEqual(ops.gate(self.case, self.base)['status'], 'BLOCKED')
        ops.dashboard(self.case)
        self.assertIn('observation expired', (self.case / 'dashboard.html').read_text())
        self.file(self.case, 'evidence/source-observations.json', '{broken')
        with patch.object(ops.g, 'check', side_effect=ValueError('invalid JSON')):
            self.assertEqual(ops.gate(self.case, self.base)['status'], 'BLOCKED')
        (self.case / 'evidence/host-observations.json').unlink(); (self.case / 'evidence/source-observations.json').unlink()
        with patch.object(ops.g, 'check', side_effect=ValueError('missing evidence')):
            self.assertEqual(ops.gate(self.case, self.base)['status'], 'BLOCKED')
        with patch.object(ops, 'gate', return_value={'status': 'BLOCKED'}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ops.main(['--case', str(self.case), '--base', self.base, 'gate']), 2)

    def test_host_adapter_variants_and_source_rollback_without_gate(self):
        src = self.root / 'both-hosts'
        for area in ('.github', '.github'):
            self.file(src, area + '/workflow/file.md', 'fixture')
        self.file(src, '.github/copilot-instructions.md', 'fixture'); self.file(src, '.github/copilot-instructions.md', 'fixture')
        for host in ('gemini', 'copilot'):
            root = self.root / ('eval-' + host)
            with patch.object(ops, 'HOST', host), patch.object(ops, 'AREA', '.github' if host == 'gemini' else '.github'):
                e.prepare(root, src)
                with patch.object(ops, 'models', return_value={'requirements': {'model': 'test-model', 'hash': 'test-hash'}}):
                    self.assertEqual(e.run(root, 'questions', False)['status'], 'UNVERIFIED')
        obs = self.observations(); (self.case / 'gate.json').unlink(); ops.pin_sources(self.case, obs)
        approval = self.approval({}); obs[0]['url'] = 'invalid'
        approval.update(old_hash=ops.g.file_hash(self.case, 'sources.lock.json'), new_hash=ops.g.digest(ops.g.encoded(obs)))
        with self.assertRaises(ValueError): ops.repin_sources(self.case, {'observations': obs, 'approval': approval})

    def test_guard_uses_real_checks_and_native_cli_reports_host_failure(self):
        ops.init_ops(self.case, self.base, []); ops.pin_sources(self.case, [])
        self.j(self.case, 'evidence/source-observations.json', []); self.j(self.case, 'evidence/host-observations.json', {})
        with patch.object(ops, 'doctor', return_value={'status': 'PASS'}):
            self.assertEqual(ops.verify_operations(self.case, self.repo)['status'], 'PASS')
        spec = ops.g.importlib.util.spec_from_file_location('real_ops_for_test', RUNTIME / 'ops.py')
        module = ops.g.importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with patch.object(ops.g.importlib.util, 'module_from_spec', return_value=module), patch.object(spec.loader.__class__, 'exec_module'), patch.object(module, 'verify_operations', side_effect=subprocess.TimeoutExpired('host', 15)):
            with self.assertRaisesRegex(ValueError, 'host observation'): ops.g.operation_guard(self.case, self.repo)

    def test_adopt_exact_unmarked_distribution(self):
        src = self.distribution(); self.file(src, 'README.md', 'v0.5.0'); target = self.root / 'adopt-target'; target.mkdir()
        self.file(target, m.CONTEXT, 'instructions')
        self.file(target, ops.AREA + '/workflow/project/value.md', 'old')
        writes, _ = m.plan(src, target, True); m.apply(target, writes, self.root / 'adopt-backup')
        self.assertEqual((target / m.CONTEXT).read_text().count('instructions'), 1)
        self.assertIn(m.START, (target / m.CONTEXT).read_text())

    def test_cli_dispatch_and_failures(self):
        base = ['--case', str(self.case), '--repo', str(self.repo), '--base', self.base]; inp = self.j(self.case, 'input.json', {})
        functions = {'init': 'init_ops', 'doctor': 'doctor', 'pin-sources': 'pin_sources', 'repin-sources': 'repin_sources', 'sources': 'verify_sources', 'quality': 'quality', 'dashboard': 'dashboard', 'gate': 'gate', 'advance': 'gate'}
        for command, function in functions.items():
            with patch.object(ops, function, return_value={'status': 'PASS'}), contextlib.redirect_stdout(io.StringIO()): self.assertEqual(ops.main(base + ['--input', str(inp), command]), 0)
        for host in ('gemini', 'copilot'):
            with patch.object(ops, 'HOST', host), patch('sys.stdin', io.StringIO('{')), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(ops.main(base + ['--input', str(inp), 'hook']), 0); self.assertIn('deny', out.getvalue())
        with patch('sys.stdin', io.StringIO('{}')), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ops.main(base + ['--input', str(inp), 'hook']), 0); self.assertEqual(ops.main(['--case', 'relative', 'gate']), 2)
        src = self.distribution(); target = self.root / 'target'; target.mkdir(); args = ['--target', str(target), '--source', str(src)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(['update'] + args), 2); self.assertEqual(m.main(['install'] + args), 0)
            self.assertEqual(m.main(['install'] + args + ['--apply', '--backup', str(self.root / 'backup')]), 0)
            self.assertEqual(m.main(['adopt'] + args), 0); self.assertEqual(m.main(['update'] + args), 0)
            self.assertEqual(m.main(['restore'] + args + ['--backup', str(self.root / 'backup')]), 0)
            self.assertEqual(m.main(['restore'] + args + ['--apply', '--backup', str(self.root / 'backup')]), 0)
        root = self.root / 'eval-main'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(e.main(['prepare', '--root', str(root), '--source', str(ROOT)]), 0)
            self.assertEqual(e.main(['run', '--root', str(root), '--scenario', 'questions']), 2)
            self.assertEqual(e.main(['assess', '--root', str(root), '--review', str(inp)]), 2)
            with patch.object(e, 'assess', return_value={'status': 'PASS'}): self.assertEqual(e.main(['assess', '--root', str(root), '--review', str(inp)]), 0)
        for name in ('ops', 'maintenance', 'evaluate'):
            with patch.object(sys, 'argv', [name, '--help']), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exc: runpy.run_path(str(RUNTIME / (name + '.py')), run_name='__main__')
            self.assertEqual(exc.exception.code, 0)

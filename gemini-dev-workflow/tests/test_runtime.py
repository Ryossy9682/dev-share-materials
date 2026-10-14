"""Runtime regressions use real files and processes; never approve a bare PASS."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

MODULE = Path(__file__).resolve().parents[1] / '.gemini/workflow/runtime/gdw.py'
spec = importlib.util.spec_from_file_location('gdw_runtime', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        guard = patch.object(g, 'operation_guard')
        guard.start()
        self.addCleanup(guard.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.case = self.root / 'case'
        self.write(self.repo, 'code.py', 'VALUE = 1\n')
        self.write(self.repo, 'tests/test_code.py', 'assert True\n')
        self.gate = g.initialize(self.case, self.repo, 'feature.test', self.root / 'saved')
        self.write(self.case, 'requirements.md', '# REQ-001\nAC-001\n')
        for files in g.ARTIFACTS.values():
            for name in files:
                if name != 'requirements.md':
                    self.write(self.case, name, name + '\n')

    def write(self, root, name, content):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def json(self, name, value):
        return self.write(self.case, name, json.dumps(value))

    def record_to(self, stage):
        for name in g.STAGES[:g.STAGES.index(stage) + 1]:
            self.gate['stage'] = name
            self.gate['completed'] = list(g.STAGES[:g.STAGES.index(name)])
            g.record(self.case, self.gate, self.repo, name)

    def approved(self, kind='approval'):
        self.json('evidence/' + kind + '.json', {
            'decision': 'APPROVED', 'actor_id': 'human-1', 'recorded_at': '2026-01-01',
            'requirements_hash': g.file_hash(self.case, 'requirements.md'),
            'evidence_path': 'approval.md', 'evidence_hash': g.file_hash(self.case, 'approval.md')})

    def reviewed(self, stage):
        value = {'decision': 'PASS', 'author_id': 'author', 'reviewer_id': 'reviewer',
                 'recorded_at': '2026-01-01', 'findings': [], 'checks': ['REQ-001 reviewed'],
                 'requirements_hash': g.file_hash(self.case, 'requirements.md'),
                 'artifacts': {p: g.file_hash(self.case, p) for p in g.REVIEW_TARGETS[stage]},
                 'record_path': g.ARTIFACTS[stage][0], 'record_hash': g.file_hash(self.case, g.ARTIFACTS[stage][0]),
                 'source_hash': g.source_digest(g.review_sources(self.gate, stage, g.inventory(self.repo, self.case))),
                 'scope_hash': g.review_scope(self.gate)}
        self.json('evidence/' + stage + '.json', value)
        return value

    def run_evidence(self, ident='ut', kind='unit', report=None):
        command = 'print("tested")'
        if report:
            path = self.case / report
            data = path.read_text()
            path.unlink()
            command += ';from pathlib import Path;Path(' + repr(str(path)) + ').write_text(' + repr(data) + ')'
        return g.run_command(self.case, self.gate, self.repo, ident, kind,
                             [sys.executable, '-c', command], 10, report)

    def coverage_evidence(self):
        report = {'meta': {'branch_coverage': True}, 'files': {'code.py': {
            'executed_lines': [1], 'missing_lines': [], 'executed_branches': [[1, -1]], 'missing_branches': []}}}
        self.json('evidence/report.json', report)
        self.run_evidence(report='evidence/report.json')
        self.run_evidence('it', 'integration')
        self.gate['coverage_scope'] = ['code.py']
        value = {'unit_run': 'ut', 'integration_run': 'it', 'report_path': 'evidence/report.json',
                 'report_hash': g.file_hash(self.case, 'evidence/report.json'),
                 'source_hashes': {'code.py': g.file_hash(self.repo, 'code.py')}, 'zero_branch_reviewed': []}
        self.json('evidence/coverage.json', value)
        return report, value

    def test_excluded_documents_preserve_execution_evidence(self):
        self.write(self.repo, 'notes.md', 'unrelated note')
        self.gate['source_map']['notes.md'] = []
        self.gate['exclusions']['notes.md'] = 'unrelated documentation reviewed'
        self.run_evidence()
        spec = {'id': 'critical', 'path': 'code.py', 'source_hash': g.file_hash(self.repo, 'code.py'),
                'before': 'VALUE = 1', 'after': 'VALUE = 2',
                'argv': [sys.executable, '-B', '-c', 'import code; assert code.VALUE == 1'],
                'timeout': 10, 'expected_exit_code': 1, 'expected_failure_marker': 'AssertionError'}
        self.gate['critical_mutations'] = [{'id': 'critical', 'applicable': True, 'reason': 'boundary',
                                           'spec_hash': g.digest(g.encoded(spec))}]
        g.mutate(self.case, self.gate, self.repo, spec)
        self.approved('release-approval')
        approval = g.read_json(self.case / 'evidence/release-approval.json')
        self.gate['release_environment'] = 'staging'
        approval.update(source_hash=g.source_digest(g.evidence_sources(self.gate, g.inventory(self.repo, self.case))),
                        environment='staging', release_hash=g.file_hash(self.case, 'release.md'))
        self.json('evidence/release-approval.json', approval)
        self.write(self.repo, 'notes.md', 'changed unrelated note')
        current = g.inventory(self.repo, self.case)
        g.valid_run(self.case, self.gate, current, 'ut', 'unit')
        g.mutations(self.case, self.gate, current)
        g.approval(self.case, self.gate, 'release-approval')
        self.write(self.repo, 'code.py', 'VALUE = 3')
        current = g.inventory(self.repo, self.case)
        with self.assertRaisesRegex(g.Blocked, 'sources stale'):
            g.valid_run(self.case, self.gate, current, 'ut', 'unit')
        with self.assertRaisesRegex(g.Blocked, 'sources stale'):
            g.mutations(self.case, self.gate, current)
        with self.assertRaisesRegex(g.Blocked, 'source changed'):
            g.approval(self.case, self.gate, 'release-approval')

    def test_initialization_preserves_state_and_requires_new_gate(self):
        self.write(self.case, 'state.json', '{"legacy":true}')
        self.assertEqual(g.load(self.case)[0]['stage'], 'bootstrap')
        with self.assertRaises(g.Blocked):
            g.initialize(self.case, self.repo, 'feature.test', self.root / 'saved')
        self.assertEqual((self.case / 'state.json').read_text(), '{"legacy":true}')

    def test_paths_reject_escape_and_symlinks(self):
        for value in ('', '../x', '/x', 'a/../x', 'a//b', 'a\\b', './a'):
            with self.subTest(value=value), self.assertRaises(g.Blocked):
                g.relative(value)
        (self.case / 'link').symlink_to(self.repo)
        with self.assertRaises(g.Blocked):
            g.file_hash(self.case, 'link/code.py')
        with self.assertRaises(g.Blocked):
            g.checkpoint(self.case, self.root / 'zip')
        (self.repo / 'link').symlink_to(self.case)
        with self.assertRaises(g.Blocked):
            g.inventory(self.repo, self.case)

    def test_missing_empty_and_stale_artifacts_and_source(self):
        with self.assertRaises(g.Blocked):
            g.check(self.case, self.gate, self.repo)
        self.record_to('bootstrap')
        self.assertEqual(g.check(self.case, self.gate, self.repo)['status'], 'PASS')
        self.write(self.case, 'branch.md', 'changed')
        with self.assertRaisesRegex(g.Blocked, 'stale artifact'):
            g.check(self.case, self.gate, self.repo)
        self.write(self.case, 'environment.md', '')
        with self.assertRaises(g.Blocked):
            g.record(self.case, self.gate, self.repo, 'bootstrap')
        with self.assertRaises(g.Blocked):
            g.record(self.case, self.gate, self.repo, 'design')

    def test_fixed_order_and_atomic_advance_checkpoint(self):
        self.record_to('bootstrap')
        result = g.advance(self.case, self.gate, self.repo)
        self.assertEqual(result['next_stage'], 'requirements')
        self.assertTrue(Path(result['checkpoint']).is_file())
        self.gate, _ = g.load(self.case)
        self.record_to('requirements')
        previous = (self.case / 'gate.json').read_bytes()
        with patch.object(g, 'checkpoint', side_effect=OSError('storage down')):
            with self.assertRaises(OSError):
                g.advance(self.case, self.gate, self.repo)
        self.assertEqual((self.case / 'gate.json').read_bytes(), previous)
        self.gate['stage'] = 'release'
        with self.assertRaisesRegex(g.Blocked, 'transition history'):
            g.check(self.case, self.gate, self.repo)

    def test_requirements_approval_is_bound_to_actual_hash(self):
        self.record_to('approve')
        with self.assertRaises(FileNotFoundError):
            g.check(self.case, self.gate, self.repo)
        self.approved()
        self.assertEqual(g.check(self.case, self.gate, self.repo)['status'], 'PASS')
        self.write(self.case, 'requirements.md', 'REQ-002\n')
        with self.assertRaisesRegex(g.Blocked, 'stale approval'):
            g.approval(self.case, self.gate, 'approval')

    def test_unread_and_changed_notion_blocks(self):
        self.record_to('investigate')
        self.write(self.case, 'notion.md', 'source')
        source = {'status': 'unread', 'url': 'https://notion.so/x', 'read_at': 'now',
                  'path': 'notion.md', 'hash': g.file_hash(self.case, 'notion.md')}
        self.gate['notion'] = [source]
        g.record(self.case, self.gate, self.repo, 'investigate')
        with self.assertRaisesRegex(g.Blocked, 'unread Notion'):
            g.check(self.case, self.gate, self.repo)
        source['status'] = 'read'
        g.record(self.case, self.gate, self.repo, 'investigate')
        g.check(self.case, self.gate, self.repo)
        self.write(self.case, 'notion.md', 'changed')
        with self.assertRaisesRegex(g.Blocked, 'stale artifact'):
            g.check(self.case, self.gate, self.repo)

    def test_independent_review_rejects_same_author_stale_targets_and_bare_pass(self):
        current = g.inventory(self.repo, self.case)
        value = self.reviewed('review-design')
        g.review(self.case, 'review-design', current)
        value['reviewer_id'] = 'author'
        self.json('evidence/review-design.json', value)
        with self.assertRaisesRegex(g.Blocked, 'independent reviewer'):
            g.review(self.case, 'review-design', current)
        self.reviewed('review-design')
        self.write(self.case, 'design.md', 'changed')
        with self.assertRaisesRegex(g.Blocked, 'review target changed'):
            g.review(self.case, 'review-design', current)
        self.reviewed('review-implementation')
        self.write(self.repo, 'code.py', 'VALUE=2')
        with self.assertRaisesRegex(g.Blocked, 'review sources changed'):
            g.review(self.case, 'review-implementation', g.inventory(self.repo, self.case))
        self.json('evidence/review-design.json', {'decision': 'PASS'})
        with self.assertRaises(KeyError):
            g.review(self.case, 'review-design', current)

    def test_runner_real_exit_log_staleness_timeout_and_no_shell(self):
        result = self.run_evidence()
        self.assertEqual(result['exit_code'], 0)
        current = g.inventory(self.repo, self.case)
        g.valid_run(self.case, self.gate, current, 'ut', 'unit')
        with self.assertRaises(g.Blocked):
            self.run_evidence()
        failed = g.run_command(self.case, self.gate, self.repo, 'failed', 'unit',
                               [sys.executable, '-c', 'raise SystemExit(3)'], 10)
        self.assertEqual(failed['exit_code'], 3)
        with self.assertRaisesRegex(g.Blocked, 'did not pass'):
            g.valid_run(self.case, self.gate, current, 'failed', 'unit')
        timeout = g.run_command(self.case, self.gate, self.repo, 'timeout', 'unit',
                               [sys.executable, '-c', 'import time; time.sleep(2)'], .01)
        self.assertTrue(timeout['timed_out'])
        self.write(self.case, result['log'], 'forged')
        with self.assertRaisesRegex(g.Blocked, 'log changed'):
            g.valid_run(self.case, self.gate, current, 'ut', 'unit')
        code, output, *_ = g.execute([sys.executable, '-c', 'import sys; print(sys.argv[1])', ';touch NO'], self.repo, 10)
        self.assertEqual(code, 0)
        self.assertIn(b';touch NO', output)
        self.assertFalse((self.repo / 'NO').exists())
        with self.assertRaisesRegex(g.Blocked, 'changed repository'):
            g.run_command(self.case, self.gate, self.repo, 'changes', 'unit',
                          [sys.executable, '-c', 'open("new", "w").write("x")'], 10)

    def test_coverage_requires_full_lines_branches_and_independent_it(self):
        report, evidence = self.coverage_evidence()
        current = g.inventory(self.repo, self.case)
        g.coverage(self.case, self.gate, current)
        for missing in ('missing_lines', 'missing_branches'):
            report['files']['code.py'][missing] = [2]
            self.json('evidence/report.json', report)
            evidence['report_hash'] = g.file_hash(self.case, 'evidence/report.json')
            self.json('evidence/coverage.json', evidence)
            run = g.read_json(self.case / 'evidence/runs/ut.json')
            run['coverage_report_hash'] = evidence['report_hash']
            self.json('evidence/runs/ut.json', run)
            with self.assertRaisesRegex(g.Blocked, 'coverage shortfall'):
                g.coverage(self.case, self.gate, current)
            report['files']['code.py'][missing] = []
        evidence['integration_run'] = 'ut'
        self.json('evidence/coverage.json', evidence)
        with self.assertRaises(g.Blocked):
            g.coverage(self.case, self.gate, current)

    def test_traceability_requires_every_id_all_layers_and_real_runs(self):
        for kind in ('unit', 'integration', 'acceptance'):
            self.run_evidence(kind, kind)
        row = {'design': {'design.md': g.file_hash(self.case, 'design.md')},
               'source': {'code.py': g.file_hash(self.repo, 'code.py')},
               'test': {'tests/test_code.py': g.file_hash(self.repo, 'tests/test_code.py')},
               'execution': {k: k for k in ('unit', 'integration', 'acceptance')}}
        self.gate['traceability'] = {'REQ-001': row, 'AC-001': row}
        current = g.inventory(self.repo, self.case)
        self.write(self.case, 'requirements.md', '# REQ-001\nAC-001\n## 更新履歴\nDeprecated REQ-999\n')
        g.trace(self.case, self.gate, current)
        del self.gate['traceability']['AC-001']
        with self.assertRaisesRegex(g.Blocked, 'trace IDs incomplete'):
            g.trace(self.case, self.gate, current)
        self.gate['traceability']['AC-001'] = row
        row['test'] = {}
        with self.assertRaisesRegex(g.Blocked, 'trace missing test'):
            g.trace(self.case, self.gate, current)

    def test_selective_impact_preserves_prior_stages_and_flags_unmapped(self):
        self.record_to('deliver')
        self.write(self.repo, 'tests/test_code.py', 'assert 1 == 1\n')
        result = g.impact(self.case, self.gate, self.repo)
        self.assertEqual(result['invalidated'][0], 'tests')
        self.assertEqual(self.gate['records']['design']['status'], 'RECORDED')
        self.assertEqual(self.gate['stage'], 'tests')
        self.write(self.repo, 'new.py', 'new = True')
        result = g.impact(self.case, self.gate, self.repo)
        self.assertEqual(result['unmapped'], ['new.py'])
        with self.assertRaisesRegex(g.Blocked, 'unmapped'):
            g.check(self.case, self.gate, self.repo)
        self.write(self.case, 'requirements.md', 'REQ-002')
        result = g.impact(self.case, self.gate, self.repo)
        self.assertEqual(result['invalidated'][0], 'requirements')

    def test_checkpoint_restore_roundtrip_and_corruption(self):
        self.record_to('bootstrap')
        archive = self.root / 'backup.zip'
        g.checkpoint(self.case, archive)
        restored = self.root / 'restored'
        g.restore(restored, archive)
        self.assertEqual((restored / 'requirements.md').read_bytes(), (self.case / 'requirements.md').read_bytes())
        self.assertEqual((self.repo / 'code.py').read_text(), 'VALUE = 1\n')
        with self.assertRaises(g.Blocked):
            g.restore(restored, archive)
        with zipfile.ZipFile(archive) as z:
            members = {n: z.read(n) for n in z.namelist()}
        for attack in ('corrupt', 'traversal', 'symlink', 'duplicate'):
            target = self.root / (attack + '.zip')
            with zipfile.ZipFile(target, 'w') as z:
                for name, data in members.items():
                    z.writestr(name, b'corruption' if attack == 'corrupt' and name == 'requirements.md' else data)
                if attack == 'traversal':
                    z.writestr('../escape', 'bad')
                elif attack == 'symlink':
                    info = zipfile.ZipInfo('link')
                    info.external_attr = (0o120777 << 16)
                    z.writestr(info, 'requirements.md')
                elif attack == 'duplicate':
                    with self.assertWarns(UserWarning):
                        z.writestr('requirements.md', 'duplicate')
            with self.subTest(attack=attack), self.assertRaises(g.Blocked):
                g.restore(self.root / ('dest-' + attack), target)
        with self.assertRaises(g.Blocked):
            g.checkpoint(self.case, self.case / 'bad.zip')

    def test_mutation_killed_survivor_invalid_timeout_and_original_untouched(self):
        original = (self.repo / 'code.py').read_bytes()
        for ident, command, expected, timeout in (
                ('killed', 'import code; assert code.VALUE == 1', 'killed', 10),
                ('survivor', 'assert True', 'survived', 10),
                ('baseline-fails', 'assert False', 'invalid', 10),
                ('timeout', 'import time; time.sleep(2)', 'invalid', .01)):
            spec = {'id': ident, 'path': 'code.py', 'source_hash': g.digest(original),
                    'before': 'VALUE = 1', 'after': 'VALUE = 2',
                    'argv': [sys.executable, '-B', '-c', command], 'timeout': timeout,
                    'expected_exit_code': 1, 'expected_failure_marker': 'AssertionError'}
            self.gate['critical_mutations'].append({'id': ident, 'applicable': True, 'reason': 'assertion',
                                                    'spec_hash': g.digest(g.encoded(spec))})
            result = g.mutate(self.case, self.gate, self.repo, spec)
            self.assertEqual(result['status'], expected)
            self.assertEqual((self.repo / 'code.py').read_bytes(), original)
            if expected == 'killed':
                g.mutations(self.case, self.gate, g.inventory(self.repo, self.case))
                approved_hash = self.gate['critical_mutations'][-1]['spec_hash']
                self.gate['critical_mutations'][-1]['spec_hash'] = 'revised-plan'
                with self.assertRaisesRegex(g.Blocked, 'specification changed'):
                    g.mutations(self.case, self.gate, g.inventory(self.repo, self.case))
                self.gate['critical_mutations'][-1]['spec_hash'] = approved_hash
            else:
                with self.assertRaisesRegex(g.Blocked, 'surviving/invalid'):
                    g.mutations(self.case, self.gate, g.inventory(self.repo, self.case))
        with self.assertRaisesRegex(g.Blocked, 'already exists'):
            g.mutate(self.case, self.gate, self.repo, spec)
        spec['before'] = 'absent'
        self.gate['critical_mutations'][-1]['spec_hash'] = g.digest(g.encoded(spec))
        with self.assertRaisesRegex(g.Blocked, 'exactly once'):
            g.mutate(self.case, self.gate, self.repo, spec)

    def test_mutation_nonapplicability_must_be_reviewed(self):
        self.gate['critical_mutations'] = [{'id': 'none', 'reason': 'docs only', 'applicable': False,
                                            'review_path': 'evidence/na.json'}]
        evidence = {'author_id': 'a', 'reviewer_id': 'b', 'decision': 'PASS', 'mutation_id': 'none',
                    'requirements_hash': g.file_hash(self.case, 'requirements.md'), 'reason': 'docs only'}
        self.json('evidence/na.json', evidence)
        current = g.inventory(self.repo, self.case)
        g.mutations(self.case, self.gate, current)
        evidence['reviewer_id'] = 'a'
        self.json('evidence/na.json', evidence)
        with self.assertRaises(g.Blocked):
            g.mutations(self.case, self.gate, current)

    def test_cli_malformed_gate_fails_closed(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(g.main(['--case', str(self.case), 'record']), 0)
            self.assertEqual(g.main(['--case', str(self.case), 'check']), 0)
            self.assertEqual(g.main(['--case', 'relative', 'check']), 2)
            self.write(self.case, 'gate.json', '{broken')
            self.assertEqual(g.main(['--case', str(self.case), 'check']), 2)

    def test_normal_workflow_through_release_with_shared_document_updates(self):
        self.gate['critical_mutations'] = [{'id': 'no-mutation', 'reason': 'docs fixture',
            'applicable': False, 'review_path': 'evidence/na.json'}]
        self.json('evidence/na.json', {'author_id': 'a', 'reviewer_id': 'b', 'decision': 'PASS',
            'requirements_hash': g.file_hash(self.case, 'requirements.md'),
            'mutation_id': 'no-mutation', 'reason': 'docs fixture'})
        self.coverage_evidence()
        self.run_evidence('acceptance', 'acceptance')
        self.gate['release_environment'] = 'staging'
        row = {'design': {'design.md': g.file_hash(self.case, 'design.md')},
               'source': {'code.py': g.file_hash(self.repo, 'code.py')},
               'test': {'tests/test_code.py': g.file_hash(self.repo, 'tests/test_code.py')},
               'execution': {'unit': 'ut', 'integration': 'it', 'acceptance': 'acceptance'}}
        self.gate['traceability'] = {'REQ-001': row, 'AC-001': row}
        for stage in g.STAGES:
            self.assertEqual(self.gate['stage'], stage)
            if stage == 'approve':
                self.approved()
            if stage == 'design':
                self.write(self.case, 'estimates.md', 'design estimate updated')
            if stage == 'implement':
                self.write(self.case, 'traceability.md', 'implementation mapping added')
            if stage == 'tests':
                self.write(self.case, 'traceability.md', 'test mapping added')
                self.write(self.case, 'test-cases.md', 'actual test IDs added')
                self.write(self.case, 'coverage-scope.md', 'measurement evidence added')
            if stage in g.REVIEW_TARGETS:
                self.reviewed(stage)
            if stage == 'release':
                self.write(self.case, 'release.md', 'release environment and rollback finalized')
                self.write(self.case, 'approval.md', 'release approval appended')
                self.approved('release-approval')
                approval = g.read_json(self.case / 'evidence/release-approval.json')
                approval.update(source_hash=g.source_digest(g.inventory(self.repo, self.case)),
                                environment='staging', release_hash=g.file_hash(self.case, 'release.md'))
                self.json('evidence/release-approval.json', approval)
            self.assertEqual(g.impact(self.case, self.gate, self.repo)['invalidated'], [])
            g.record(self.case, self.gate, self.repo, stage)
            self.assertEqual(g.check(self.case, self.gate, self.repo)['status'], 'PASS')
            if stage != 'release':
                g.advance(self.case, self.gate, self.repo)
        with self.assertRaisesRegex(g.Blocked, 'terminal'):
            g.advance(self.case, self.gate, self.repo)
        self.write(self.case, 'design.md', 'changed actual design specification')
        result = g.impact(self.case, self.gate, self.repo)
        self.assertEqual(result['invalidated'][0], 'design')

    def test_mapping_reconciliation_exclusions_and_missing_notion_dependency(self):
        self.record_to('investigate')
        self.write(self.repo, 'unrelated.txt', 'notes')
        self.gate['source_map']['unrelated.txt'] = []
        self.gate['exclusions']['unrelated.txt'] = 'unrelated personal notes, reviewed'
        g.save(self.case, self.gate)
        g.load(self.case)
        result = g.impact(self.case, self.gate, self.repo)
        self.assertEqual(result['invalidated'], [])
        self.write(self.repo, 'unrelated.txt', 'edited notes')
        self.assertEqual(g.impact(self.case, self.gate, self.repo)['invalidated'], [])
        self.gate['notion'] = [{'url': 'https://notion.so/new', 'status': 'unread', 'path': 'new.md'}]
        result = g.impact(self.case, self.gate, self.repo)
        self.assertEqual(result['invalidated'][0], 'investigate')
        self.gate['notion'] = []
        (self.case / 'investigation.md').unlink()
        self.assertEqual(g.impact(self.case, self.gate, self.repo)['invalidated'][0], 'investigate')

    def test_unit_report_must_be_fresh_and_coverage_scope_cannot_omit_changed_code(self):
        self.json('evidence/existing.json', {})
        with self.assertRaisesRegex(g.Blocked, 'newly generated'):
            g.run_command(
                self.case, self.gate, self.repo, 'existing', 'unit', [sys.executable, '-c', 'pass'],
                10, 'evidence/existing.json')
        report, evidence = self.coverage_evidence()
        report['files']['code.py']['executed_branches'] = []
        self.json('evidence/report2.json', report)
        self.run_evidence('zero', report='evidence/report2.json')
        evidence.update(unit_run='zero', report_path='evidence/report2.json',
                        report_hash=g.file_hash(self.case, 'evidence/report2.json'))
        self.json('evidence/coverage.json', evidence)
        with self.assertRaisesRegex(g.Blocked, 'zero branches'):
            g.coverage(self.case, self.gate, g.inventory(self.repo, self.case))
        evidence['zero_branch_reviewed'] = ['code.py']
        self.json('evidence/coverage.json', evidence)
        g.coverage(self.case, self.gate, g.inventory(self.repo, self.case))
        self.gate['baseline_inventory']['tests/test_code.py'] = 'old'
        self.gate['source_map']['tests/test_code.py'] = ['implement']
        with self.assertRaisesRegex(g.Blocked, 'omitted'):
            g.coverage(self.case, self.gate, g.inventory(self.repo, self.case))

    def test_mutation_syntax_error_wrong_failure_and_mutant_timeout_are_invalid(self):
        original = (self.repo / 'code.py').read_bytes()
        for ident, after, command, marker in (
                ('syntax', 'VALUE = ???', 'import code; assert code.VALUE == 1', 'SyntaxError'),
                ('wrong', 'VALUE = 2', 'import code; assert code.VALUE == 1', 'EXPECTED NAMED TEST'),
                ('late', 'VALUE = 2', 'import code,time; time.sleep(2 if code.VALUE == 2 else 0)', 'AssertionError')):
            spec = {'id': ident, 'path': 'code.py', 'source_hash': g.digest(original),
                    'before': 'VALUE = 1', 'after': after,
                    'argv': [sys.executable, '-c', command], 'timeout': .1,
                    'expected_exit_code': 1, 'expected_failure_marker': marker}
            self.gate['critical_mutations'].append({'id': ident, 'applicable': True, 'reason': 'test',
                                                   'spec_hash': g.digest(g.encoded(spec))})
            self.assertEqual(g.mutate(self.case, self.gate, self.repo, spec)['status'], 'invalid')

    def test_cli_commands_report_progress_and_failure_exit_codes(self):
        def cli(*args):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                code = g.main(['--case', str(self.case), *args])
            return code, json.loads(output.getvalue()) if output.getvalue() else {}
        code, status = cli('status')
        self.assertEqual(code, 2)
        self.assertEqual(status['current'], 'bootstrap')
        self.assertTrue(status['check_errors'])
        self.assertEqual(cli('record')[0], 0)
        self.assertEqual(cli('advance')[0], 0)
        self.assertEqual(cli('impact')[0], 0)
        self.assertEqual(cli('checkpoint', str(self.root / 'cli.zip'))[0], 0)
        self.assertEqual(cli('run', '--id', 'cli-fail', '--kind', 'unit', '--', sys.executable,
                             '-c', 'raise SystemExit(4)')[0], 2)
        self.assertEqual(cli('run', '--id', 'cli-pass', '--kind', 'unit', sys.executable,
                             '-c', 'pass')[0], 0)
        old_case = self.case
        self.case = self.root / 'cli-restored'
        self.assertEqual(cli('restore', str(self.root / 'cli.zip'))[0], 0)
        self.case = self.root / 'cli-new'
        self.assertEqual(cli('init', '--repo', str(self.repo), '--branch', 'feature.new',
                             '--checkpoint-dir', str(self.root / 'saved'))[0], 0)
        self.case = old_case
        spec = {'id': 'cli', 'path': 'code.py', 'source_hash': g.file_hash(self.repo, 'code.py'),
                'before': 'VALUE = 1', 'after': 'VALUE = 2', 'timeout': 10,
                'argv': [sys.executable, '-c', 'import code; assert code.VALUE == 1'],
                'expected_exit_code': 1, 'expected_failure_marker': 'AssertionError'}
        self.gate = g.load(self.case)[0]
        self.gate['critical_mutations'] = [{'id': 'cli', 'applicable': True, 'reason': 'test',
                                           'spec_hash': g.digest(g.encoded(spec))}]
        g.save(self.case, self.gate)
        self.json('spec.json', spec)
        self.assertEqual(cli('mutate', str(self.case / 'spec.json'))[0], 0)
        link = self.root / 'linked-case'
        link.symlink_to(self.case)
        self.case = link
        self.assertEqual(cli('status')[0], 2)

    def test_atomic_cleanup_and_failed_restore_leave_no_partial_files(self):
        with patch.object(g.os, 'replace', side_effect=OSError('write failed')):
            with self.assertRaises(OSError):
                g.atomic(self.root / 'atomic.json', b'data')
        self.assertFalse(list(self.root.glob('.gdw-*')))
        self.record_to('bootstrap')
        archive = self.root / 'archive.zip'
        with patch.object(g.os, 'replace', side_effect=OSError('write failed')):
            with self.assertRaises(OSError):
                g.checkpoint(self.case, archive)
        g.checkpoint(self.case, archive)
        destination = self.root / 'empty'
        destination.mkdir()
        g.restore(destination, archive)
        with patch.object(g, 'load', side_effect=g.Blocked('bad metadata')):
            with self.assertRaises(g.Blocked):
                g.restore(self.root / 'bad-restore', archive)
        self.assertFalse((self.root / 'bad-restore').exists())
        self.assertFalse(list(self.root.glob('.gdw-restore-*')))

    def test_inventory_ignores_case_and_cache_and_module_entrypoint(self):
        self.write(self.repo, '__pycache__/cache.pyc', 'cache')
        nested = self.repo / 'case'
        self.write(nested, 'evidence.log', 'evidence')
        self.assertNotIn('case/evidence.log', g.inventory(self.repo, nested))
        self.assertNotIn('__pycache__/cache.pyc', g.inventory(self.repo, nested))
        import runpy
        with patch.object(sys, 'argv', [str(MODULE), '--case', str(self.case), 'status']):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exit_status:
                runpy.run_path(str(MODULE), run_name='__main__')
            self.assertEqual(exit_status.exception.code, 2)


if __name__ == '__main__':
    unittest.main()

"""配布ツールの正常系・競合・非破壊性・検証失敗を確認するUT。"""
import contextlib
import io
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import install, validate


class InstallTests(unittest.TestCase):
    """利用者のファイルを保持する導入契約を検証する。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        (self.source / '.gemini/skills/demo').mkdir(parents=True)
        (self.source / '.gemini/skills/demo/SKILL.md').write_text('demo')
        (self.source / 'GEMINI.md').write_text('context')
        self.target = self.root / 'target'
        self.target.mkdir()

    def apply(self, plan):
        for path, data in plan:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def test_new_install_and_idempotency(self):
        """新規導入を実施し、2回目の変更計画が空になることを確認する。"""
        plan = install.plan_install(self.target, self.source)
        self.assertEqual(len(plan), 2)
        self.assertEqual(list(self.target.iterdir()), [])
        self.apply(plan)
        self.assertIn('context', (self.target / 'GEMINI.md').read_text())
        self.assertEqual(install.plan_install(self.target, self.source), [])

    def test_only_distribution_files_are_copied(self):
        """実行キャッシュや接続設定を配布せずコマンドとランタイムを導入する。"""
        files = {
            '.gemini/settings.json': 'private connection settings',
            '.gemini/workflow/runtime/__pycache__/gdw.pyc': 'cache',
            '.gemini/workflow/runtime/gdw.pyo': 'cache',
            '.gemini/workflow/runtime/gdw.py': 'runtime',
            '.gemini/commands/gdw/start.toml': 'command',
        }
        for name, content in files.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.apply(install.plan_install(self.target, self.source))
        self.assertFalse((self.target / '.gemini/settings.json').exists())
        self.assertFalse((self.target / '.gemini/workflow/runtime/__pycache__').exists())
        self.assertFalse((self.target / '.gemini/workflow/runtime/gdw.pyo').exists())
        self.assertEqual((self.target / '.gemini/workflow/runtime/gdw.py').read_text(), 'runtime')
        self.assertEqual((self.target / '.gemini/commands/gdw/start.toml').read_text(), 'command')

    def test_preserve_existing_context(self):
        """既存指示をバイト列の先頭にそのまま残す。"""
        text = '既存のプロジェクト規約\n'
        (self.target / 'GEMINI.md').write_text(text, encoding='utf-8')
        self.apply(install.plan_install(self.target, self.source))
        self.assertTrue((self.target / 'GEMINI.md').read_text().startswith(text))

    def test_missing_target(self):
        with self.assertRaises(ValueError):
            install.plan_install(self.root / 'absent', self.source)

    def test_conflict_does_not_write(self):
        """既存ファイル競合でGEMINI.mdなどを一切書き換えない。"""
        path = self.target / '.gemini/skills/demo/SKILL.md'
        path.parent.mkdir(parents=True)
        path.write_text('user data')
        with self.assertRaises(ValueError):
            install.plan_install(self.target, self.source)
        self.assertEqual(path.read_text(), 'user data')
        self.assertFalse((self.target / 'GEMINI.md').exists())

    def test_invalid_markers(self):
        for content in (install.START, install.END,
                        install.START + install.END,
                        install.START * 2 + install.END,
                        install.START + install.END * 2):
            with self.subTest(content=content):
                (self.target / 'GEMINI.md').write_text(content)
                with self.assertRaises(ValueError):
                    install.plan_install(self.target, self.source)
                self.assertEqual((self.target / 'GEMINI.md').read_text(), content)

    def test_symlink_context(self):
        (self.target / 'GEMINI.md').symlink_to(self.source / 'GEMINI.md')
        with self.assertRaises(ValueError):
            install.plan_install(self.target, self.source)

    def test_symlink_target_and_ancestor(self):
        """導入先そのものと祖先のリンクを解決前に拒否する。"""
        alias = self.root / 'alias'
        alias.symlink_to(self.target, target_is_directory=True)
        (self.target / 'child').mkdir()
        for path in (alias, alias / 'child'):
            with self.assertRaises(ValueError):
                install.plan_install(path, self.source)
        self.assertFalse((self.target / '.gemini').exists())

    def test_preserve_context_bytes(self):
        """LF・CRLF・末尾改行なしを保持し再実行で変化しない。"""
        for original in (b'keep\n', b'keep\r\n', b'keep'):
            (self.target / 'GEMINI.md').write_bytes(original)
            self.apply(install.plan_install(self.target, self.source))
            saved = (self.target / 'GEMINI.md').read_bytes()
            self.assertTrue(saved.startswith(original))
            self.assertEqual(install.plan_install(self.target, self.source), [])

    def test_all_parent_file_collisions(self):
        """既存の途中階層ファイルをすべて書込前に検出する。"""
        for relative in ('.gemini', '.gemini/skills', '.gemini/skills/demo'):
            with tempfile.TemporaryDirectory() as folder:
                target = Path(folder)
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'user')
                with self.assertRaises(ValueError):
                    install.plan_install(target, self.source)
                self.assertEqual(path.read_bytes(), b'user')
                self.assertFalse((target / 'GEMINI.md').exists())

    def test_symlink_parent(self):
        (self.target / '.gemini').symlink_to(self.source / '.gemini', target_is_directory=True)
        with self.assertRaises(ValueError):
            install.plan_install(self.target, self.source)

    def test_directory_collision(self):
        (self.target / 'GEMINI.md').mkdir()
        with self.assertRaises(ValueError):
            install.plan_install(self.target, self.source)

    def test_parent_file_collision(self):
        (self.target / '.gemini').write_text('existing')
        with self.assertRaises(ValueError):
            install.plan_install(self.target, self.source)

    def test_main_dry_run_apply_and_no_changes(self):
        out = io.StringIO()
        destination = self.target / 'nested/a.txt'
        with contextlib.redirect_stdout(out):
            with patch.object(install, 'plan_install', return_value=[(destination, b'data')]):
                install.main(['--target', str(self.target)])
                self.assertFalse(destination.exists())
                install.main(['--target', str(self.target), '--apply'])
                self.assertEqual(destination.read_bytes(), b'data')
            with patch.object(install, 'plan_install', return_value=[]):
                install.main(['--target', str(self.target)])
        self.assertIn('PLAN ', out.getvalue())
        self.assertIn('WRITE ', out.getvalue())
        self.assertIn('0 file(s)', out.getvalue())

    def test_entrypoint(self):
        with patch('sys.argv', ['install.py', '--target', str(self.target)]):
            with contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(install.ROOT / 'scripts/install.py'), run_name='__main__')
        self.assertFalse((self.target / 'GEMINI.md').exists())


class ValidateTests(unittest.TestCase):
    """静的検査が壊れた成果物を検出し、正常な最小配布を受理することを確認する。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf-8')

    def fixture(self):
        self.put('README.md', '[local](GEMINI.md) [web](https://geminicli.com/) [anchor](#a)')
        self.put('GEMINI.md', 'context')
        self.put('.gemini/workflow/templates/state.json', '{}')
        for i in range(14):
            self.put(f'.gemini/skills/gdw-{i}/SKILL.md', f'---\nname: gdw-{i}\ndescription: "test"\n---\n')

    def test_valid_fixture(self):
        self.fixture()
        self.assertEqual(validate.validate(self.root), [])

    def test_missing_structure(self):
        self.assertEqual(len(validate.validate(self.root)), 4)

    def test_broken_metadata_links_and_json(self):
        self.fixture()
        self.put('.gemini/skills/gdw-0/SKILL.md', 'invalid')
        self.put('bad.md', '[bad](missing.md)')
        self.put('bad.json', '{')
        errors = validate.validate(self.root)
        self.assertEqual(len(errors), 3)
        self.assertTrue(any(x.startswith('frontmatter:') for x in errors))
        self.assertTrue(any(x.startswith('broken link:') for x in errors))
        self.assertTrue(any(x.startswith('invalid JSON:') for x in errors))

    def test_main_pass_and_fail(self):
        for errors, status in (([], 0), (['bad'], 1)):
            with patch.object(validate, 'validate', return_value=errors):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as cm:
                        validate.main()
            self.assertEqual(cm.exception.code, status)

    def test_entrypoint(self):
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                runpy.run_path(str(validate.ROOT / 'scripts/validate.py'), run_name='__main__')
        self.assertEqual(cm.exception.code, 0)

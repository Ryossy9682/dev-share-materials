"""実際のCLI起動から配布物導入・再導入までを確認する結合テスト。"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkflowIntegrationTests(unittest.TestCase):
    def test_install_in_existing_git_project(self):
        """既存Gitプロジェクトに導入し既存指示・Git状態を保持して再実行できる。"""
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'project with spaces'
            target.mkdir()
            subprocess.run(['git', 'init', str(target)], check=True, capture_output=True)
            original = b'# Existing instructions\r\nKeep these bytes.\r\n'
            (target / 'GEMINI.md').write_bytes(original)
            command = [sys.executable, str(ROOT / 'scripts/install.py'), '--target', str(target)]
            subprocess.run(command, check=True, capture_output=True)
            self.assertFalse((target / '.gemini').exists())
            subprocess.run(command + ['--apply'], check=True, capture_output=True)
            self.assertEqual(len(list((target / '.gemini/skills').glob('*/SKILL.md'))), 14)
            self.assertTrue((target / '.git').is_dir())
            # 既存本文・改行を含むバイト列を保持すること。
            self.assertTrue((target / 'GEMINI.md').read_bytes().startswith(original))
            second = subprocess.run(command + ['--apply'], check=True, capture_output=True, text=True)
            self.assertIn('0 file(s)', second.stdout)
            for path in (ROOT / '.gemini').rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc', '.pyo'):
                    self.assertEqual(path.read_bytes(), (target / path.relative_to(ROOT)).read_bytes())

    def test_real_validator(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('PASS', result.stdout)

    def test_conflicting_workflow_file_prevents_all_writes(self):
        """実配布物の後半で競合してもスキルを含め一切書き込まない。"""
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / '.gemini').mkdir()
            conflict = target / '.gemini/workflow'
            conflict.write_bytes(b'existing user file')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/install.py'), '--target', str(target), '--apply'],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(conflict.read_bytes(), b'existing user file')
            self.assertFalse((target / '.gemini/skills').exists())
            self.assertFalse((target / 'GEMINI.md').exists())

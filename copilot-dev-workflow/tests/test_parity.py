"""Pin the port to the reviewed Gemini baseline, independently of AI output."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ParityTests(unittest.TestCase):
    def test_common_specifications_and_operation_bodies_match_baseline(self):
        manifest = json.loads((ROOT / 'docs/creation/evidence/parity.json').read_text())
        for row in manifest['common_files'] + manifest['operation_skills'] + manifest['agent_files']:
            with self.subTest(path=row['target']):
                self.assertEqual(hashlib.sha256((ROOT / row['target']).read_bytes()).hexdigest(),
                                 row['target_sha256'])
        runtime = next(row for row in manifest['common_files'] if row['target'].endswith('/runtime/cdw.py'))
        self.assertEqual(runtime['comparison'], 'platform-substitutions-only')
        self.assertEqual(len(manifest['operation_skills']), 7)
        stages = [r for r in manifest['common_files'] if r['target'].startswith('.github/skills/')]
        self.assertEqual(len(stages), 14)

    def test_copilot_surface_has_no_gemini_runtime_entrypoints(self):
        self.assertFalse((ROOT / '.gemini').exists())
        self.assertFalse((ROOT / 'GEMINI.md').exists())
        for folder in (ROOT / '.github/skills', ROOT / '.github/workflow/references'):
            for path in folder.rglob('*.md'):
                self.assertNotIn('gemini mcp', path.read_text())
                self.assertNotIn('gdw', path.read_text())
                self.assertNotIn('gdw', str(path.relative_to(ROOT)))
        optional = (ROOT / '.github/agents/cdw-review-design.agent.md').read_text()
        self.assertIn('tools: [read, search]', optional)
        self.assertNotIn('kind: local', optional)


if __name__ == '__main__':
    unittest.main()

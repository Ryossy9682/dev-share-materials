from pathlib import Path
import re
import tempfile
import unittest
from scripts import install

ROOT = Path(__file__).resolve().parents[1]
AREA = '.github'
PREFIX = 'cdw'
EXT = '.agent.md'
ROLES = {'workflow','bootstrap','requirements','investigate','estimate','design','review-design','implement','review-implementation','tests','review-tests','verify','deliver','release','setup','start','status','resume','check','impact','mutate'}
FRONTIER = {'requirements','design','review-design','review-implementation','review-tests','verify','check','impact','mutate'}


class ModelRoutingTests(unittest.TestCase):
    def test_every_role_has_explicit_model_in_native_agent(self):
        paths = list((ROOT / AREA / 'agents').glob('*' + EXT))
        self.assertEqual({p.name.removesuffix(EXT).removeprefix(PREFIX + '-') for p in paths}, ROLES)
        for path in paths:
            with self.subTest(agent=path.name):
                body = path.read_text()
                self.assertTrue(body.startswith('---\n'))
                fm = body.split('---', 2)[1]
                model = re.findall(r'^model: (\S+)$', fm, re.M)
                self.assertEqual(len(model), 1)
                self.assertNotIn(model[0], ('auto','inherit'))
                role = path.name.removesuffix(EXT).removeprefix(PREFIX + '-')
                pattern = r'(opus|pro|astra|terra|argon|sol)' if role in FRONTIER else r'(haiku|luna|flash|mini)'
                self.assertRegex(model[0], pattern)
                if AREA == '.github':
                    self.assertIn('modelPolicy: required', fm)
                self.assertIn('model-policy.md', body)
                self.assertIn('自分自身を再委任しない', body)

    def test_reviewers_are_read_only_and_read_requirements(self):
        for role in ('review-design','review-implementation','review-tests'):
            body = (ROOT / AREA / 'agents' / (PREFIX + '-' + role + EXT)).read_text()
            self.assertIn('requirements.md', body)
            expected = 'tools: [read_file, grep_search]' if AREA == '.gemini' else 'tools: [read, search]'
            self.assertIn(expected, body)

    def test_skills_route_to_existing_agent_definitions(self):
        for path in (ROOT / AREA / 'skills').glob('*/SKILL.md'):
            body = path.read_text()
            self.assertIn('model-policy.md', body)
            self.assertIn(f'{AREA}/agents/{path.parent.name}{EXT}', body)
            self.assertTrue((ROOT / AREA / 'agents' / (path.parent.name + EXT)).exists())

    def test_policy_prevents_silent_fallback_and_supports_questions(self):
        policy = (ROOT / AREA / 'workflow/references/model-policy.md').read_text()
        for contract in ('Autoやinheritで代用しない','実モデル不明はBLOCKED','一問だけ','原文で保存','子担当は別工程へ進まず','configure-review','反映後の動作確認はverify','workflow-intake/request.md','ブランチ確定前','転記一致'):
            self.assertIn(contract, policy)

    def test_installer_copies_models_without_copying_user_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for path, data in install.plan_install(target):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            for path in (ROOT / AREA / 'agents').glob('*' + EXT):
                self.assertEqual(path.read_bytes(), (target / path.relative_to(ROOT)).read_bytes())
            self.assertEqual(install.plan_install(target), [])
            self.assertFalse((target / AREA / 'settings.json').exists())

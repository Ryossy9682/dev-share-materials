"""配布物のスキル形式、内部リンク、JSONと必須構成を静的検証する。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    """異常の説明リストを返す。空なら静的構成検査に合格する。"""
    errors = []
    for name in ('README.md', '.github/copilot-instructions.md', '.github/workflow/templates/state.json'):
        if not (root / name).is_file():
            errors.append('missing: ' + name)
    skills = sorted((root / '.github/skills').glob('*/SKILL.md'))
    if len(skills) != 21:
        errors.append('expected 21 skills')
    for path in skills:
        text = path.read_text(encoding='utf-8')
        pattern = r'\A---\nname: ' + re.escape(path.parent.name) + r'\ndescription: "[^\n]+"\n---\n'
        if not re.match(pattern, text):
            errors.append('frontmatter: ' + str(path.relative_to(root)))
    for path in root.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if not re.match(r'https?://|#', link):
                if not (path.parent / link.split('#')[0]).exists():
                    errors.append('broken link: ' + str(path.relative_to(root)) + ': ' + link)
    for path in root.rglob('*.json'):
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except ValueError:
            errors.append('invalid JSON: ' + str(path.relative_to(root)))
    return errors


def main():
    """検証結果を表示し、異常があれば終了コード1を返す。"""
    errors = validate()
    print('\n'.join(errors) if errors else 'PASS: skills, links, JSON, required files')
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()

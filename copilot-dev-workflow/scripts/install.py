"""既存の設定を保持し、Copilotワークフローをプロジェクトへ導入する。"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- copilot-dev-workflow:start -->'
END = '<!-- copilot-dev-workflow:end -->'


def plan_install(target, source=ROOT):
    """差分書込計画を返し、競合・リンクがあれば書込前に停止する。"""
    target = Path(target).absolute()
    if any(p.is_symlink() for p in [target, *target.parents]):
        raise ValueError('導入先ルートにシンボリックリンクがあります。')
    target = target.resolve()
    if not target.is_dir():
        raise ValueError('導入先の既存ディレクトリを指定してください。')
    files = sorted(
        path for area in ('skills', 'workflow', 'agents')
        for path in (source / '.github' / area).rglob('*')
        if path.is_file() and '__pycache__' not in path.parts
        and path.suffix not in ('.pyc', '.pyo'))
    entries = [(p.relative_to(source), p.read_bytes()) for p in files]
    context = (source / '.github/copilot-instructions.md').read_text(encoding='utf-8').strip()
    block = START + '\n' + context + '\n' + END
    destinations = [target / rel for rel, _ in entries] + [target / '.github/copilot-instructions.md']
    for dest in destinations:
        if any(p.is_symlink() for p in [dest, *dest.parents]):
            raise ValueError('導入先にシンボリックリンクがあります: ' + str(dest))
        if dest.exists() and not dest.is_file():
            raise ValueError('ファイルの配置先がディレクトリです: ' + str(dest))
        if any(p.exists() and not p.is_dir() for p in dest.parents):
            raise ValueError('親ディレクトリの位置にファイルがあります: ' + str(dest))
    current = target / '.github/copilot-instructions.md'
    old = current.read_bytes().decode('utf-8') if current.exists() else ''
    if START in old or END in old:
        if old.count(START) != 1 or old.count(END) != 1 or block not in old:
            raise ValueError('既存ワークフローブロックを手動で比較してください。')
        updated = old
    else:
        updated = old + ('\n\n' if old else '') + block + '\n'
    entries.append((Path('.github/copilot-instructions.md'), updated.encode('utf-8')))
    changes = []
    for rel, data in entries:
        dest = target / rel
        if dest.exists():
            if dest.read_bytes() == data:
                continue
            if rel != Path('.github/copilot-instructions.md'):
                raise ValueError('異なる既存ファイルがあります: ' + str(rel))
        changes.append((dest, data))
    return changes


def main(argv=None):
    """引数を解析し、既定では計画表示、--apply指定時だけ書き込む。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    changes = plan_install(args.target)
    for path, data in changes:
        print(('WRITE ' if args.apply else 'PLAN ') + str(path))
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f'{len(changes)} file(s); apply={args.apply}')


if __name__ == '__main__':
    main()

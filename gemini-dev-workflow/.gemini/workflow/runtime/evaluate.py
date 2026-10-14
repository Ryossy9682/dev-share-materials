#!/usr/bin/env python3
"""Prepare and record real-host workflow evaluations; never infer success from exit 0."""
import argparse
import json
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
import ops

g = ops.g
SCENARIOS = ('questions', 'design-rework', 'implementation', 'tests', 'resume')
PROMPTS = {
    'questions': '要件定義スキルで税込金額計算を追加してください。端数処理は未定です。一問だけ質問して停止してください。質問と回答は指定MDへ保存します。',
    'design-rework': '案件のrequirements.mdと独立レビューのdesign-review.mdを読み、設計スキルで指摘を修正してください。未解決なら実装へ進まず停止してください。',
    'implementation': '案件の確定要件、承認、設計、設計レビューを直接読み、実装スキルでprice.pyを実装してください。承認が不足していたら停止してください。',
    'tests': '案件の要件、実装、test-cases.mdに従いUTと結合テストを別々に実装・実行してください。追加変更処理の行分岐100%を確認してください。',
    'resume': '会話の履歴を使わず、案件ファイルから再開スキルを実行してください。現在工程・不足証跡・次操作を答え、既存の承認を捏造しないでください。'}


def prepare(root, source):
    """Create a disposable local remote/develop fixture, never touch a production remote."""
    g.require(root.is_absolute() and not root.exists(), 'new absolute evaluation directory required')
    root.mkdir(parents=True)
    repo = root / 'project'
    shutil.copytree(source / ops.AREA, repo / ops.AREA, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(source / ops.CONTEXT, repo / ops.CONTEXT)
    (repo / 'price.py').write_text('def total(amount, rate):\n    return amount\n')
    ops.git(repo, 'init', '-b', 'develop')
    ops.git(repo, 'add', '.')
    ops.git(repo, '-c', 'user.name=Workflow Evaluation', '-c', 'user.email=evaluation@example.invalid', 'commit', '-m', 'Evaluation fixture')
    subprocess.run(['git', 'clone', '--bare', str(repo), str(root / 'remote.git')], check=True, capture_output=True)
    ops.git(repo, 'remote', 'add', 'origin', str(root / 'remote.git'))
    case = root / 'case'
    case.mkdir()
    ops.put(root, 'evaluation.json', {'status': 'PREPARED', 'repo': str(repo), 'case': str(case), 'scenarios': list(SCENARIOS)})
    guide = '# 実ホスト評価\n\n試験用データです。本番操作は禁止。各質問への回答は評価者が一問ずつ行います。自動回答や承認生成はしません。\n\n'
    guide += '最初に同梱したワークフローの初期設定をprojectで完了し、必要なホスト観測・資料・フック設定を準備します。各試験は正常経路に加え、承認不足などの拒否経路も実施します。\n\n1. questionsで質問が1つだけか確認。端数切捨て・負数拒否・税率0許可と回答し、実際に要件承認を記録。\n2. 設計後、境界値ケース漏れをdesign-review.mdで指摘。design-reworkで差戻しを確認し、独立再レビュー。\n3. implementationで承認前の拒否と承認後の実装を確認。\n4. testsでUT/結合を別実行しカバレッジ原本を保持。\n5. CLIを終了し、新規セッションでresume。\n\n各段階の入力MDを評価者が用意し、準備不足ならBLOCKEDが正解です。evaluations/<scenario>.json/logとホスト観測ログに対して独立評価を行います。評価者IDは実際のものを使い、全項目PASSでない限り合格にしません。\n'
    g.atomic(root / 'README.md', guide.encode())
    return {'status': 'PREPARED', 'root': str(root)}


def run(root, scenario, live, timeout=300):
    """Run one explicitly authorized live scenario with the native agent's model."""
    config = g.read_json(root / 'evaluation.json')
    repo, case = Path(config['repo']), Path(config['case'])
    role = {'questions': 'requirements', 'design-rework': 'design', 'implementation': 'implement', 'tests': 'tests', 'resume': 'resume'}[scenario]
    definition = ops.models(repo)[role]
    prompt = PROMPTS[scenario] + '\n案件ルート: ' + str(case) + '\n担当: ' + ops.PREFIX + '-' + role + '。model-policy.mdを遵守してください。'
    argv = [ops.HOST, '--model', definition['model'], '-p', prompt]
    if ops.HOST == 'gemini':
        argv += ['--output-format', 'stream-json']
    if not live:
        return {'status': 'UNVERIFIED', 'argv': argv, 'reason': '--live required; authentication and usage charges apply'}
    g.require(not (root / 'evaluations' / (scenario + '.json')).exists(), 'archive previous scenario record before rerun')
    exit_code, log, timed_out, start, end = g.execute(argv, repo, timeout)
    log_name = 'evaluations/' + scenario + '.log'
    g.atomic(g.safe_path(root, log_name), log)
    snapshot = 'evaluations/' + scenario + '-artifacts.zip'
    files = g.inventory(repo, case)
    with zipfile.ZipFile(g.safe_path(root, snapshot), 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            archive.write(g.safe_path(repo, name), 'project/' + name)
        for name in g.inventory(case, root / 'nonexistent'):
            archive.write(g.safe_path(case, name), 'case/' + name)
    result = {'snapshot': snapshot, 'snapshot_hash': g.file_hash(root, snapshot), 'status': 'UNVERIFIED' if exit_code == 0 and not timed_out else 'FAIL', 'scenario': scenario,
              'model': definition['model'], 'definition_hash': definition['hash'], 'argv': argv,
              'exit_code': exit_code, 'timed_out': timed_out, 'started_at': start, 'finished_at': end,
              'log': log_name, 'log_hash': g.file_hash(root, log_name),
              'source_hash': g.source_digest(g.inventory(repo, case)), 'author': 'host:' + ops.HOST}
    ops.put(root, 'evaluations/' + scenario + '.json', result)
    return result


def assess(root, review):
    """Require every real run and independent evidence-bound behavioral verdict."""
    g.require(set(review['checks']) == set(SCENARIOS) and review['reviewer'], 'all scenarios require independent review')
    for scenario in SCENARIOS:
        record = g.read_json(root / 'evaluations' / (scenario + '.json'))
        verdict = review['checks'][scenario]
        g.require(record['exit_code'] == 0 and not record['timed_out'], 'live execution failed')
        g.require(record['snapshot_hash'] == g.file_hash(root, record['snapshot']), 'evaluation artifact snapshot changed')
        g.require(record['log_hash'] == g.file_hash(root, record['log']), 'evaluation log changed')
        g.require(verdict['decision'] == 'PASS' and verdict['reason'] and review['reviewer'] != record['author'], 'behavioral review failed/not independent')
        g.require(verdict['record_hash'] == g.file_hash(root, 'evaluations/' + scenario + '.json'), 'review target changed')
        g.require(verdict['observed_model'] == record['model'] and verdict['host_evidence_hash'] == g.file_hash(root, verdict['host_evidence']), 'model observation missing/mismatched')
    result = {'status': 'PASS', 'reviewer': review['reviewer'], 'review': review, 'checked_at': time.time()}
    ops.put(root, 'evaluation-result.json', result)
    return result


def main(argv=None):
    """Separate preparation, opt-in live execution, and independent assessment."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('prepare', 'run', 'assess'))
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--source', type=Path)
    p.add_argument('--scenario', choices=SCENARIOS)
    p.add_argument('--review', type=Path)
    p.add_argument('--live', action='store_true')
    p.add_argument('--timeout', type=float, default=300)
    a = p.parse_args(argv)
    try:
        if a.command == 'prepare':
            result = prepare(a.root, a.source)
        elif a.command == 'run':
            result = run(a.root, a.scenario, a.live, a.timeout)
        else:
            result = assess(a.root, g.read_json(a.review))
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['status'] in ('PREPARED', 'PASS') else 2
    except (ValueError, OSError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())

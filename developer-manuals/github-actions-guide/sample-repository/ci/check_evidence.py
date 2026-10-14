"""Require the successful integration evidence from the same run and commit."""
import json
import os
from pathlib import Path
import sys


def check(path, env):
    matches = list(Path(path).rglob('evidence.json'))
    if len(matches) != 1:
        raise ValueError('Exactly one evidence.json is required')
    evidence = json.loads(matches[0].read_text())
    expected = {'status': 'success', 'sha': env['GITHUB_SHA'],
                'run_id': env['GITHUB_RUN_ID'], 'run_attempt': env['GITHUB_RUN_ATTEMPT']}
    if any(evidence.get(k) != v for k, v in expected.items()):
        raise ValueError('Evidence does not match this successful run and revision')
    return evidence


if __name__ == '__main__':
    check(sys.argv[1], os.environ)
    print('Integration evidence matches this revision')

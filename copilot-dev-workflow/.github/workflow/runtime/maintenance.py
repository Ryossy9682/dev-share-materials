#!/usr/bin/env python3
"""Three-way workflow installation/update with external recovery journal."""
import argparse
import base64
import json
import re
import sys
from pathlib import Path
import ops

g = ops.g
AREA = ops.AREA
CONTEXT = '.github/copilot-instructions.md'
START = '<!-- copilot-dev-workflow:start -->'
END = '<!-- copilot-dev-workflow:end -->'
STATE = AREA + '/workflow-install.json'


def manifest(source):
    """Read managed distribution files without including user settings."""
    entries = {}
    for area in ('skills', 'workflow', 'commands', 'agents'):
        for p in sorted((source / AREA / area).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'):
                g.require(not p.is_symlink(), 'source symlink forbidden')
                entries[p.relative_to(source).as_posix()] = p.read_bytes()
    g.require(entries, 'empty distribution')
    entries[CONTEXT] = (START + '\n' + (source / CONTEXT).read_text().strip() + '\n' + END).encode()
    return entries


def read_part(target, name):
    """Extract only the owned instructions block; leave surrounding prose intact."""
    path = g.safe_path(target, name)
    data = path.read_bytes() if path.exists() else None
    if name == CONTEXT and data is not None:
        text = data.decode()
        if START not in text and END not in text:
            return None
        g.require(text.count(START) == text.count(END) == 1 and text.index(START) < text.index(END), 'ambiguous instruction block')
        return text[text.index(START):text.index(END) + len(END)].encode()
    return data


def encode(data):
    """Serialize bytes, preserving absent files as null."""
    return None if data is None else base64.b64encode(data).decode()


def decode(data):
    """Decode saved bytes using strict Base64 validation."""
    return None if data is None else base64.b64decode(data, validate=True)


def plan(source, target, adopt=False):
    """Compute all conflicts before mutations; preserve local-only edits."""
    incoming = manifest(source)
    state_path = g.safe_path(target, STATE)
    state = g.read_json(state_path) if state_path.exists() else {'files': {}}
    old = {name: decode(data) for name, data in state['files'].items()}
    conflicts, writes, retained = [], {}, []
    for name in sorted(set(old) | set(incoming)):
        current, before, new = read_part(target, name), old.get(name), incoming.get(name)
        if adopt:
            if name == CONTEXT and current is None and g.safe_path(target, name).is_file() and g.safe_path(target, name).read_text().strip() == (source / CONTEXT).read_text().strip():
                writes[name] = new
                current = new
            if current != new:
                conflicts.append(name)
            continue
        if current == new:
            continue
        if current == before:
            writes[name] = new
        elif new == before:
            retained.append(name)
        else:
            conflicts.append(name)
    g.require(not conflicts, 'update conflicts: ' + ', '.join(conflicts))
    for name, data in list(writes.items()):
        if name == CONTEXT:
            path = g.safe_path(target, name)
            current = path.read_text() if path.exists() else ''
            previous = read_part(target, name)
            if adopt and previous is None:
                current = ''
            writes[name] = (current.replace(previous.decode(), data.decode()) if previous else current + '\n\n' + data.decode() + '\n').encode()
    readme = source / 'README.md'
    versions = re.findall(r'v[0-9]+\.[0-9]+\.[0-9]+', readme.read_text() if readme.exists() else '')
    next_state = {'manager_version': '0.6.0', 'distribution_version': versions[-1] if versions else 'unknown', 'distribution_hash': g.digest(g.encoded({k: g.digest(v) for k, v in incoming.items()})),
                  'files': {k: encode(v) for k, v in incoming.items()}}
    writes[STATE] = g.encoded(next_state)
    writes = {name: data for name, data in writes.items() if not g.safe_path(target, name).exists() or g.safe_path(target, name).read_bytes() != data}
    return writes, retained


def write_file(path, data):
    """Apply bytes or remove one known managed file."""
    if data is None:
        path.unlink(missing_ok=True)
    else:
        g.atomic(path, data)


def apply(target, writes, backup):
    """Journal first; retain recovery data if rollback cannot finish."""
    g.require(backup.is_absolute() and not backup.resolve().is_relative_to(target.resolve()) and not backup.exists(), 'new external backup directory required')
    entries = {}
    for name, data in writes.items():
        p = g.safe_path(target, name)
        entries[name] = {'before': encode(p.read_bytes() if p.exists() else None), 'after': encode(data)}
    journal = {'target': str(target.resolve()), 'status': 'PREPARED', 'files': entries}
    ops.put(backup, 'journal.json', journal)
    try:
        for name, data in writes.items():
            write_file(g.safe_path(target, name), data)
    except OSError:
        journal['status'] = 'PARTIAL'
        ops.put(backup, 'journal.json', journal)
        restore(target, backup)
        raise
    journal['status'] = 'APPLIED'
    ops.put(backup, 'journal.json', journal)
    return {'status': 'APPLIED', 'backup': str(backup), 'files': sorted(writes)}


def restore(target, backup):
    """Restore only if every current file still equals before or applied content."""
    journal = g.read_json(g.safe_path(backup, 'journal.json'))
    g.require(journal['target'] == str(target.resolve()), 'backup target mismatch')
    for name, row in journal['files'].items():
        p = g.safe_path(target, name)
        current = encode(p.read_bytes() if p.exists() else None)
        g.require(current in (row['before'], row['after']), 'post-update edit; restore conflict: ' + name)
    for name, row in journal['files'].items():
        write_file(g.safe_path(target, name), decode(row['before']))
    journal['status'] = 'RESTORED'
    ops.put(backup, 'journal.json', journal)
    return {'status': 'RESTORED', 'backup': str(backup)}


def main(argv=None):
    """Dry-run by default for install, adoption, update and restore."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'adopt', 'update', 'restore'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    try:
        g.require(args.target.is_absolute() and args.target.is_dir(), 'existing absolute target required')
        if args.command == 'restore':
            result = restore(args.target, args.backup) if args.apply else {'status': 'PLAN_RESTORE', 'backup': str(args.backup)}
        else:
            if args.command == 'update':
                g.require((args.target / STATE).exists(), 'adopt matching old distribution before update')
            writes, retained = plan(args.source, args.target, args.command == 'adopt')
            result = apply(args.target, writes, args.backup) if args.apply else {'status': 'PLAN', 'files': sorted(writes)}
            result['retained_local_changes'] = retained
        print(json.dumps(result))
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())

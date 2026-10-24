#!/usr/bin/env python3
"""One immutable, separately granted stage; no retry or dependency build."""
import json
import os
from pathlib import Path
import sys
import time
from common import (ROOT, BUNDLE, bindings, execute, finish, install_signal_handlers,
                    load_protocol, save, sha, utc, verify)


def main():
    install_signal_handlers()
    assert len(sys.argv) == 2
    stage = sys.argv[1]
    protocol = load_protocol()
    assert stage in protocol['stages']
    spec = protocol['stage_specs'][stage]
    output = BUNDLE / 'runs' / f'{stage}-001'
    output.mkdir(parents=True, exist_ok=False)
    path = output / 'run.json'
    start = time.monotonic()
    record = {'status': 'running', 'stage': stage, 'started_utc': utc(),
              'bound_seconds': spec['bound_seconds'], 'stages': [],
              'scope': protocol['scope'], 'outputs': {}}
    save(path, record)
    files = {}
    try:
        files = bindings(protocol, stage)
        grant = json.loads((BUNDLE / 'protocol/grants' / f'{stage}.json').read_text())
        for required in spec['requires']:
            previous_path = BUNDLE / 'runs' / f'{required}-001/run.json'
            previous = json.loads(previous_path.read_text())
            assert previous['status'] == 'passed' and previous['inputs_unchanged'] is True
            assert not previous.get('total_bound_exceeded', False)
            expected = protocol['stage_specs'][required]['commands']
            assert len(previous['stages']) == len(expected)
            for actual, command in zip(previous['stages'], expected):
                assert actual['passed'] and actual['command'] == command['command']
                assert actual['exit_code'] == 0 and not actual['timeout']
                assert not actual['cleanup_errors'] and actual['within_bound']
            assert grant['required_receipts'][required] == sha(previous_path)
            extra = {Path(key): digest for key, digest in previous['inputs'].items()}
            extra.update({ROOT / key: digest for key, digest in previous['outputs'].items()})
            extra[previous_path] = sha(previous_path)
            for key, digest in extra.items():
                assert key not in files or files[key] == digest
                files[key] = digest
        verify(files, protocol)
        record['inputs'] = {str(p): digest for p, digest in files.items()}
        save(path, record)
        env = os.environ.copy()
        env.update(RAYON_NUM_THREADS='1', RUST_TEST_THREADS='1', OMP_NUM_THREADS='1',
                   IREGI_PV_PREPARATION_PROFILE='1')
        for item in spec['commands']:
            remaining = spec['bound_seconds'] - (time.monotonic() - start) - spec['postguard_reserve_seconds']
            seconds = min(remaining, item['bound_seconds'])
            env.update(item['environment'])
            step = execute(item['command'], output / item['log'], seconds, env)
            step['name'] = item['name']
            record['stages'].append(step)
            save(path, record)
            assert step['passed'], f"{item['name']} did not pass"
            verify(files, protocol)
        record['status'] = 'passed'
    except BaseException as error:
        record.update(status='failed', error=f'{type(error).__name__}: {error}')
    finally:
        save(path, record)
        try:
            record['outputs'] = {name: sha(ROOT / name) for name in spec['outputs'] if (ROOT / name).is_file()}
            record['missing_outputs'] = [name for name in spec['outputs'] if not (ROOT / name).is_file()]
            if record['missing_outputs']:
                record['status'] = 'failed'
        except BaseException as error:
            record.update(status='failed', output_hash_error=f'{type(error).__name__}: {error}')
        finish(record, path, files, protocol, start)
    print({'stage': stage, 'status': record['status'], 'receipt': str(path)})
    return 0 if record['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())

"""Exact amplitude witness plus complete semantic modules for the combined candidate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import signal
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'collector-nway-build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'passed'
    frozen = root / build['frozen_source_root']
    files = {str((frozen / name).relative_to(root)): value for name, value in build['source_hashes'].items()}
    files.update(build['protected_input_hashes'])
    for path in [Path(__file__), build_path, root / build['test_binary_path'], root / build['exact_binary_path']]:
        files[str(path.relative_to(root))] = sha(path)
    assert all(sha(root / name) == value for name, value in files.items())
    record_path = here / 'collector-nway-checks.json'
    assert not record_path.exists()
    listed = subprocess.run([str(root / build['test_binary_path']), '--list'], capture_output=True, text=True, check=True, timeout=30)
    list_path = here / 'collector-nway-tests-list.txt'
    assert not list_path.exists()
    list_path.write_text(listed.stdout)
    tests = re.findall(r'^(\S+): test$', listed.stdout, re.M)
    assert len(tests) == 174
    runs = []
    for label, binary_key, arguments, limit, mode, expected in [
        ('exact', 'exact_binary_path', [], 30, 'verify', 20),
        ('stability', 'test_binary_path', ['stability::', '--test-threads=1', '--nocapture'], 240, 'nway', 38),
        ('execution', 'test_binary_path', ['execution::', '--test-threads=1', '--nocapture'], 240, 'nway', 35),
    ]:
        command = ['taskset', '-c', '14', str(root / build[binary_key]), *arguments]
        env = os.environ.copy()
        env.update(IREGI_PRIMAL_SUM_MODE=mode, RAYON_NUM_THREADS='1', RUST_TEST_THREADS='1')
        for name in ['IREGI_ALIAS_USE_VERIFY', 'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE']:
            env.pop(name, None)
        log_path = here / ('collector-nway-' + label + '.log')
        out_path = here / 'collector-nway-exact-results.json' if label == 'exact' else log_path
        assert not log_path.exists() and (out_path == log_path or not out_path.exists())
        started = time.monotonic()
        with log_path.open('wb') as log:
            output = out_path.open('wb') if out_path != log_path else log
            try:
                child = subprocess.Popen(command, cwd=root, env=env, stdout=output, stderr=log, start_new_session=True)
                try:
                    code = child.wait(timeout=limit)
                    status = 'passed' if code == 0 else 'failed'
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    code = child.wait()
                    status = 'timeout'
            finally:
                if output != log:
                    output.close()
        row = dict(label=label, command=command, timeout_seconds=limit, mode=mode, status=status,
                   exit_code=code, elapsed_seconds=time.monotonic() - started,
                   log_path=str(log_path.relative_to(root)), log_sha256=sha(log_path))
        if code == 0:
            if label == 'exact':
                result = json.loads(out_path.read_text())
                assert len(result) == len(dict(result)) == expected
                previous = json.loads((here / 'nway-exact-results.json').read_text())
                assert result == previous, 'Every canonical expression/error must also match the retained qualified witness'
                row.update(result_path=str(out_path.relative_to(root)), result_sha256=sha(out_path), checked_cases=expected,
                           retained_exact_result_sha256=sha(here / 'nway-exact-results.json'))
            else:
                log = log_path.read_text()
                summaries = re.findall(r'^test result: ok\. (\d+) passed; 0 failed; 0 ignored; 0 measured; (\d+) filtered out; finished in [0-9.]+s$', log, re.M)
                expected_names = {name for name in tests if name.startswith(label + '::')}
                observed_names = re.findall(r'^test (\S+) \.\.\.', log, re.M)
                assert len(summaries) == 1 and int(summaries[0][0]) == expected == len(expected_names)
                assert int(summaries[0][1]) == 174 - expected
                assert len(observed_names) == expected and set(observed_names) == expected_names
                row['checked_cases'] = expected
        runs.append(row)
        if code:
            break
    changed = {name: [value, sha(root / name)] for name, value in files.items() if sha(root / name) != value}
    record = dict(status='passed' if len(runs) == 3 and all(r['status'] == 'passed' for r in runs) and not changed else 'failed',
                  build_manifest_sha256=sha(build_path), protected_input_hashes=files, changed_inputs=changed,
                  test_listing_sha256=sha(list_path), runs=runs, finished_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Combined collector+n-way candidate:20 exact canonical Atom/error witnesses (verify mode) and complete38 stability+35 execution tests (nway mode); no high-point numeric-array or performance claim.')
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)
    if record['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

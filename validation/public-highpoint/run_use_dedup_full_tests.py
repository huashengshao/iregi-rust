"""Run the complete stability and execution unit modules of the frozen candidate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import signal
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'use-dedup-full-build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'passed'
    binary = root / build['test_binary_path']
    assert sha(binary) == build['test_binary_sha256']
    frozen = root / build['frozen_source_root']
    protected = {str((frozen / name).relative_to(root)): value for name, value in build['frozen_source_hashes'].items()}
    protected.update({str(build_path.relative_to(root)): sha(build_path),
                      str(Path(__file__).relative_to(root)): sha(Path(__file__)),
                      str(binary.relative_to(root)): sha(binary)})
    assert all(sha(root / name) == value for name, value in protected.items())
    result_path = here / 'use-dedup-full-tests-run.json'
    assert not result_path.exists(), 'Preserve prior tests'
    env = os.environ.copy()
    env['RAYON_NUM_THREADS'] = '1'
    env['RUST_TEST_THREADS'] = '1'
    removed = ['IREGI_ALIAS_USE_VERIFY', 'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE', 'IREGI_MASTER_AMPLITUDE_MODE']
    for name in removed:
        env.pop(name, None)
    records = []
    for module in ['stability::', 'execution::']:
        label = module.removesuffix('::')
        log_path = here / ('use-dedup-full-tests-' + label + '.log')
        assert not log_path.exists()
        command = ['taskset', '-c', '14', str(binary), module, '--test-threads=1', '--nocapture']
        started = time.monotonic()
        with log_path.open('wb') as log:
            child = subprocess.Popen(command, env=env, cwd=root, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = child.wait(timeout=240)
                status = 'passed' if code == 0 else 'failed'
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
                status = 'timeout'
        records.append(dict(module=module, status=status, exit_code=code, command=command,
                            timeout_seconds=240, elapsed_seconds=time.monotonic() - started,
                            log_path=str(log_path.relative_to(root)), log_sha256=sha(log_path)))
        if code:
            break
    changed = {name: [value, sha(root / name)] for name, value in protected.items() if sha(root / name) != value}
    record = dict(status='passed' if len(records) == 2 and all(r['status'] == 'passed' for r in records) and not changed else 'failed',
                  finished_utc=datetime.now(timezone.utc).isoformat(), records=records,
                  build_manifest_sha256=sha(build_path), protected_input_hashes=protected,
                  changed_inputs=changed, environment_additions={'RAYON_NUM_THREADS': '1', 'RUST_TEST_THREADS': '1'},
                  environment_removals=removed,
                  scope='Complete stability and execution unit modules on the frozen current-core collector candidate; no public high-point numerical claim.')
    result_path.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)
    if record['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

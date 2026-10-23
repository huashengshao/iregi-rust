"""Replay the immutable original driver in baseline-only mode, bounded at300s."""
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
    build_path = here / 'collector-capture-build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'passed'
    binary = root / build['binary_path']
    assert sha(binary) == build['binary_sha256']
    output = here / 'collector-v1-replay-baseline.json'
    log_path = here / 'collector-v1-replay-baseline.log'
    record_path = here / 'collector-v1-replay-baseline-run.json'
    assert not any(path.exists() for path in [output, log_path, record_path])
    protected = dict(build['protected_input_hashes'])
    for path in [Path(__file__), binary, build_path]:
        protected[str(path.relative_to(root))] = sha(path)
    assert all(sha(root / name) == value for name, value in protected.items())
    env = os.environ.copy()
    env['RAYON_NUM_THREADS'] = '1'
    removed = ['IREGI_CORE_STACK_PROOF_DIR', 'IREGI_ALIAS_USE_VERIFY', 'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE', 'IREGI_PRIMAL_SUM_MODE']
    for name in removed:
        env.pop(name, None)
    command = ['taskset', '-c', '14', str(binary), str(output), 'baseline']
    record = dict(status='started', command=command, variant='baseline', timeout_seconds=300,
                  started_utc=datetime.now(timezone.utc).isoformat(), build_manifest_sha256=sha(build_path),
                  protected_input_hashes=protected, environment_additions={'RAYON_NUM_THREADS': '1'},
                  environment_removals=removed,
                  protocol='Unchanged original binary, original27 cases/order, baseline-only child; no extra controls or rebuild. Diagnostic repeatability replay, not a performance comparison.')
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    started = time.monotonic()
    with log_path.open('wb') as log:
        child = subprocess.Popen(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = child.wait(timeout=300)
            status = 'completed' if code == 0 else 'failed'
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            code = child.wait()
            status = 'timeout'
    changed = {name: [value, sha(root / name)] for name, value in protected.items() if sha(root / name) != value}
    record.update(status=status, exit_code=code, elapsed_seconds=time.monotonic() - started,
                  finished_utc=datetime.now(timezone.utc).isoformat(), changed_inputs=changed,
                  log_sha256=sha(log_path), output_hashes={str(output.relative_to(root)): sha(output)} if output.exists() else {})
    if output.exists():
        record['complete_cases'] = len(json.loads(output.read_text()))
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record.get(key) for key in ['status', 'exit_code', 'elapsed_seconds', 'complete_cases', 'changed_inputs']}), flush=True)
    if status != 'completed' or changed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

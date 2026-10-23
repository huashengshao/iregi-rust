#!/usr/bin/env python3
"""Bounded correctness repeats using the frozen complete current closure."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent / 'thin-lto'
SCRATCH = ROOT / 'target/near-vacuum-adapter-current-thin-lto'
BUILDER = HERE.parent / 'build_thin_lto.py'
spec = importlib.util.spec_from_file_location('private_current_build', BUILDER)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    build_path = HERE / 'build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'private_v3_current_closure_build_passed'
    closure_before = builder.closure_hashes()
    assert closure_before == json.loads((HERE / 'closure-after-build.json').read_text())
    manifest = json.loads((builder.CLOSURE / 'manifest.json').read_text())
    for row in manifest['files'] + manifest['native_files']:
        assert closure_before[str(Path(row['retained']).relative_to(ROOT))] == row['sha256']
    (HERE / 'closure-before-runs.json').write_text(json.dumps(closure_before, indent=2) + '\n')
    input_hashes = build['source_sha256'] | build['output_sha256']
    for path in [Path(__file__), BUILDER, build_path]:
        input_hashes[str(path.relative_to(ROOT))] = sha(path)
    oracle = ROOT / 'validation/near-vacuum-adapter/oracle/output.json'
    input_hashes[str(oracle.relative_to(ROOT))] = sha(oracle)
    assert all(sha(ROOT / path) == digest for path, digest in input_hashes.items())
    cases = [(kind, 'near_vacuum_adapter_validate_v3', [kind])
             for kind in ['f64', 'dd', 'float128', 'float256']]
    cases += [('contract', 'near_vacuum_contract_current', []),
              ('contour', 'five_pinch_compare_current', [str(oracle)])]
    summaries = []
    for name, binary, arguments in cases:
        output = HERE / f'{name}.json'
        log = HERE / f'{name}.log'
        record = HERE / f'{name}-run.json'
        assert not any(path.exists() for path in [output, log, record])
        command = ['taskset', '-c', '18', str(SCRATCH / binary), *arguments, str(output)]
        before = {path: sha(ROOT / path) for path in input_hashes}
        assert before == input_hashes
        started = time.monotonic()
        timed_out = False
        print(json.dumps({'starting': name, 'timeout_seconds': 60}), flush=True)
        with log.open('w') as stream:
            process = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            try:
                code = process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
        elapsed = time.monotonic() - started
        after = {path: sha(ROOT / path) for path in input_hashes}
        run = {'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'command': command, 'cwd': str(ROOT), 'timeout_seconds': 60,
               'timed_out': timed_out, 'exit_code': code, 'diagnostic_wall_seconds': elapsed,
               'sha256_before': before, 'sha256_after': after, 'inputs_unchanged': before == after,
               'output_sha256': sha(output) if output.exists() else None,
               'log_sha256': sha(log),
               'scope': 'Private unchanged v3 prototype with the retained complete 6b24c03 release dependency closure. CPU18 correctness diagnostics only; no performance or production E6 claim.'}
        record.write_text(json.dumps(run, indent=2) + '\n')
        summary = {'case': name, 'exit_code': code, 'timed_out': timed_out,
                   'inputs_unchanged': before == after, 'diagnostic_wall_seconds': elapsed,
                   'record_sha256': sha(record)}
        summaries.append(summary)
        print(json.dumps(summary), flush=True)
        assert before == after
    closure_after = builder.closure_hashes()
    assert closure_before == closure_after
    (HERE / 'closure-after-runs.json').write_text(json.dumps(closure_after, indent=2) + '\n')
    (HERE / 'runs.json').write_text(json.dumps(summaries, indent=2) + '\n')
    assert all(row['exit_code'] == 0 and not row['timed_out'] for row in summaries)

if __name__ == '__main__':
    main()

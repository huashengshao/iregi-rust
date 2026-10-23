#!/usr/bin/env python3
"""Build and run the independent exact oracle using the retained release closure."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCRATCH = ROOT / 'target/near-vacuum-input-enclosure/oracle'
CLOSURE = ROOT / 'target/benchmark/dependency-closures/6b24c03-complete-kinds'
SOURCE = SCRATCH / 'five_pinch_oracle.rs'
BINARY = SCRATCH / 'five_pinch_oracle'
EXPECTED_SOURCE = 'a12d96533f48983bd38f5835c2085dfcb8579707363371385aabc8df33460081'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def hash_closure():
    files = sorted(path for path in CLOSURE.rglob('*') if path.is_file())
    hashes = {str(path.relative_to(ROOT)): sha(path) for path in files}
    manifest = json.loads((CLOSURE / 'manifest.json').read_text())
    for row in manifest['files']:
        retained = Path(row['retained'])
        assert retained.is_relative_to(CLOSURE)
        assert hashes[str(retained.relative_to(ROOT))] == row['sha256']
    completion = json.loads((CLOSURE / 'workspace-completion.json').read_text())
    assert completion['cargo_returncode'] == 0
    assert completion['dependency_closure_manifest_sha256'] == sha(CLOSURE / 'manifest.json')
    assert completion['workspace_manifest_sha256'] == sha(CLOSURE / 'completed-workspace-build.json')
    return hashes


def main():
    assert Path.cwd() == ROOT
    assert sha(SOURCE) == EXPECTED_SOURCE
    assert sha(HERE / 'five_pinch_oracle.rs') == EXPECTED_SOURCE
    assert not BINARY.exists()
    for name in ['build.json', 'build.log', 'run.json', 'run.log', 'output.json']:
        assert not (HERE / name).exists(), f'Never overwrite existing evidence: {name}'

    before = hash_closure()
    write('closure-before.json', before)
    events = json.loads((CLOSURE / 'cargo-library-events.json').read_text())
    selected = {}
    for name in ['symbolica', 'serde_json']:
        matching = [event for event in events
                    if event['target']['name'] == name
                    and event['profile']['opt_level'] == '3'
                    and event['profile']['test'] is False]
        assert len(matching) == 1, (name, len(matching))
        archives = [path for path in matching[0]['filenames'] if path.endswith('.rlib')]
        assert len(archives) == 1
        retained = CLOSURE / 'deps' / Path(archives[0]).name
        assert str(retained.relative_to(ROOT)) in before
        selected[name] = {'cargo_event': matching[0], 'retained_archive': str(retained.relative_to(ROOT)), 'sha256': sha(retained)}
    native = [
        'build/blake3-be485904775d6e47/out',
        'build/gmp-mpfr-sys-575ed8ab5d02dcec/out/lib',
        'build/gmp-mpfr-sys-e9fd89ef30e561a9/out/lib',
        'build/psm-3e52beb8ea08afba/out',
        'build/psm-a698b6f3f5aee778/out',
    ]
    command = ['taskset', '-c', '19', 'rustc', '--edition=2024',
               '-C', 'opt-level=3', '-C', 'lto=thin', '-C', 'embed-bitcode=yes',
               '-C', 'codegen-units=1', '--crate-name', 'five_pinch_nondyadic_oracle',
               str(SOURCE), '-L', f'dependency={CLOSURE}/deps']
    for path in native:
        assert (CLOSURE / path).is_dir()
        command += ['-L', f'native={CLOSURE / path}']
    for name in selected:
        command += ['--extern', f'{name}={ROOT / selected[name]["retained_archive"]}']
    command += ['-o', str(BINARY)]
    environment = {'CARGO_CRATE_NAME': 'five_pinch_nondyadic_oracle',
                   'RAYON_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'}
    start_utc, start = utc(), time.monotonic()
    with (HERE / 'build.log').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=os.environ | environment,
                                stdout=log, stderr=subprocess.STDOUT)
    build = {'schema_version': 1, 'command': command, 'cwd': str(ROOT),
             'environment_overrides': environment, 'started_utc': start_utc,
             'completed_utc': utc(), 'exit_code': result.returncode,
             'diagnostic_build_seconds': time.monotonic() - start,
             'rustc': subprocess.check_output(['rustc', '--version'], text=True).strip(),
             'source_sha256': EXPECTED_SOURCE, 'selected': selected,
             'dependency_closure': str(CLOSURE.relative_to(ROOT)),
             'closure_files_verified': len(before),
             'scope': 'Independent exact Symbolica oracle only. No production reduction or scalar-master code is linked.',
             'build_log_sha256': sha(HERE / 'build.log')}
    write('build.json', build)
    assert result.returncode == 0
    after_build = hash_closure()
    assert before == after_build
    assert sha(SOURCE) == EXPECTED_SOURCE
    write('closure-after-build.json', after_build)
    build |= {'binary_sha256': sha(BINARY),
              'closure_before_sha256': sha(HERE / 'closure-before.json'),
              'closure_after_build_sha256': sha(HERE / 'closure-after-build.json')}
    write('build.json', build)
    print(json.dumps({'status': 'build_passed', 'binary_sha256': sha(BINARY)}), flush=True)

    output = HERE / 'output.json'
    run_command = ['taskset', '-c', '19', 'timeout', '--signal=TERM', '--kill-after=5s', '120s', str(BINARY), str(output)]
    start_utc, start = utc(), time.monotonic()
    with (HERE / 'run.log').open('w') as log:
        result = subprocess.run(run_command, cwd=ROOT, env=os.environ | environment,
                                stdout=log, stderr=subprocess.STDOUT)
    run = {'schema_version': 1, 'command': run_command, 'cwd': str(ROOT),
           'environment_overrides': environment, 'license': 'Inherited privately; contents never recorded.',
           'started_utc': start_utc, 'completed_utc': utc(), 'exit_code': result.returncode,
           'diagnostic_runtime_seconds': time.monotonic() - start,
           'runtime_limit_seconds': 120, 'cpu': 19,
           'binary_sha256': sha(BINARY), 'source_sha256': sha(SOURCE),
           'build_manifest_sha256': sha(HERE / 'build.json'), 'run_log_sha256': sha(HERE / 'run.log'),
           'timing_scope': 'Diagnostic duration only; not a performance benchmark.'}
    if output.exists():
        run['output_sha256'] = sha(output)
    write('run.json', run)
    after_run = hash_closure()
    assert before == after_run
    write('closure-after-run.json', after_run)
    run['closure_after_run_sha256'] = sha(HERE / 'closure-after-run.json')
    write('run.json', run)
    assert result.returncode == 0
    assert sha(SOURCE) == EXPECTED_SOURCE
    assert sha(HERE / 'five_pinch_oracle.rs') == EXPECTED_SOURCE
    report = json.loads(output.read_text())
    assert report['status'] == 'exact_five_pinch_oracle_generated'
    assert report['fixture']['x_exact_rational'] == '2/5'
    assert len(report['boxes']) == 5
    assert all(row['oracle']['remainder_less_than_2_pow_minus_320'] for row in report['boxes'])
    assert report['independent_direct_J5_D4']['remainder_less_than_2_pow_minus_320']
    assert report['five_box_contraction']['independent_enclosures_compatible']
    assert report['mapped_integrand_at_x']['remainder_less_than_2_pow_minus_320']
    print(json.dumps({'status': 'exact_oracle_passed', 'output': str(output.relative_to(ROOT)),
                      'sha256': sha(output), 'run_manifest': str((HERE / 'run.json').relative_to(ROOT)),
                      'closure_files_unchanged': len(before)}), flush=True)


if __name__ == '__main__':
    main()

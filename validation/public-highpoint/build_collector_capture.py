"""Build a matched pure-6b24 baseline and paired collector-only public driver."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    parent_path = here / 'use-dedup-full-build.json'
    parent = json.loads(parent_path.read_text())
    assert parent['status'] == 'passed'
    target = root / 'target/public-highpoint/collector-capture'
    assert not target.exists(), 'Keep paired builds immutable'
    target.mkdir(parents=True)
    original = (root / parent['frozen_source_root']).parent / 'original'
    candidate = (root / parent['frozen_source_root']).parent / 'libiregi_rust.rlib'
    protected = {str((original / name).relative_to(root)): value for name, value in parent['original_source_hashes'].items()}
    protected.update({str((root / parent['frozen_source_root'] / name).relative_to(root)): value
                      for name, value in parent['frozen_source_hashes'].items()})
    driver = here / 'collector_capture.rs'
    frozen_driver = target / 'collector_capture.rs'
    frozen_driver.write_bytes(driver.read_bytes())
    for path in [parent_path, driver, Path(__file__), candidate, frozen_driver]:
        protected[str(path.relative_to(root))] = sha(path)
    assert all(sha(root / name) == value for name, value in protected.items())
    core_command = [part.replace(str(root / parent['frozen_source_root']), str(original))
                    .replace('metadata=public_highpoint_use_dedup_full', 'metadata=public_highpoint_collector_baseline')
                    .replace(str(candidate), str(target / 'libiregi_rust_baseline.rlib'))
                    for part in parent['commands'][0]]
    parent_probe = parent['commands'][1]
    extern = {part.split('=', 1)[0]: part.split('=', 1)[1] for part in parent_probe
              if part.startswith(('iregi_masters=', 'symbolica=', 'serde_json='))}
    command = ['taskset', '-c', '14,15', 'rustc', '--edition=2024', str(frozen_driver), '-C', 'opt-level=2']
    for index, part in enumerate(parent_probe):
        if part == '-L':
            command += ['-L', parent_probe[index + 1]]
    command += ['--extern', 'baseline=' + str(target / 'libiregi_rust_baseline.rlib'),
                '--extern', 'candidate=' + str(candidate)]
    for name, path in extern.items():
        command += ['--extern', name + '=' + path]
    command += ['-o', str(target / 'collector_capture')]
    commands = [core_command, command]
    guards = set()
    for invocation in commands:
        for part in invocation:
            if part.startswith('dependency='):
                guards.update(p for p in Path(part.split('=', 1)[1]).iterdir() if p.suffix in ['.rlib', '.so'])
            if part.startswith(('iregi_masters=', 'symbolica=', 'serde=', 'thiserror=', 'serde_json=', 'candidate=')):
                guards.add(Path(part.split('=', 1)[1]))
    before = {str(path.relative_to(root)): sha(path) for path in sorted(guards)}
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(original / 'crates/iregi-rust'), CARGO_CRATE_NAME='iregi_rust')
    codes = []
    started = time.monotonic()
    for label, invocation in zip(['baseline', 'driver'], commands):
        with (here / ('collector-capture-' + label + '-build.log')).open('w') as log:
            code = subprocess.call(invocation, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        codes.append(code)
        if code:
            break
    changed = {name: [expected, sha(root / name)] for name, expected in {**before, **protected}.items() if sha(root / name) != expected}
    record = dict(status='passed' if codes == [0, 0] and not changed else 'failed',
                  commands=commands, exit_codes=codes, changed_inputs=changed,
                  protected_input_hashes=protected, dependency_hashes=before,
                  parent_build_manifest_sha256=sha(parent_path), elapsed_seconds=time.monotonic() - started,
                  source_revision=parent['source_revision'],
                  binary_path=str((target / 'collector_capture').relative_to(root)),
                  scope='Matched pure6b24 baseline vs collector-only6b24 candidate, with27 complete paired public cases and explicit required-success/guard predicates. Development build; no graph-order or performance claim.')
    if codes == [0, 0]:
        record['binary_sha256'] = sha(target / 'collector_capture')
        record['baseline_archive_sha256'] = sha(target / 'libiregi_rust_baseline.rlib')
        record['candidate_archive_sha256'] = sha(candidate)
    (here / 'collector-capture-build.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ['status', 'exit_codes', 'changed_inputs', 'elapsed_seconds']}), flush=True)
    if record['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

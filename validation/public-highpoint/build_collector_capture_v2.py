"""Compile only the checkpointed v2 driver against the retained matched cores."""
from pathlib import Path
import hashlib
import json
import subprocess
import time


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    parent_path = here / 'collector-capture-build.json'
    parent = json.loads(parent_path.read_text())
    assert parent['status'] == 'passed'
    target = root / 'target/public-highpoint/collector-capture-v2'
    assert not target.exists()
    target.mkdir(parents=True)
    source = here / 'collector_capture_v2.rs'
    frozen = target / 'collector_capture_v2.rs'
    frozen.write_bytes(source.read_bytes())
    command = parent['commands'][1].copy()
    old_source = root / 'target/public-highpoint/collector-capture/collector_capture.rs'
    command = [str(frozen) if part == str(old_source) else part for part in command]
    command[command.index('-o') + 1] = str(target / 'collector_capture_v2')
    protected = dict(parent['protected_input_hashes'])
    for path in [Path(__file__), parent_path, source, frozen]:
        protected[str(path.relative_to(root))] = sha(path)
    guards = set()
    for part in command:
        if part.startswith('dependency='):
            guards.update(p for p in Path(part.split('=', 1)[1]).iterdir() if p.suffix in ['.rlib', '.so'])
        if part.startswith(('baseline=', 'candidate=', 'symbolica=', 'iregi_masters=', 'serde_json=')):
            guards.add(Path(part.split('=', 1)[1]))
    before = {str(path.relative_to(root)): sha(path) for path in sorted(guards)}
    assert all(sha(root / name) == value for name, value in protected.items())
    started = time.monotonic()
    with (here / 'collector-capture-v2-build.log').open('w') as log:
        code = subprocess.call(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
    changed = {name: [value, sha(root / name)] for name, value in {**protected, **before}.items() if sha(root / name) != value}
    record = dict(status='passed' if code == 0 and not changed else 'failed', command=command,
                  exit_code=code, elapsed_seconds=time.monotonic() - started, changed_inputs=changed,
                  protected_input_hashes=protected, dependency_hashes=before,
                  parent_build_manifest_sha256=sha(parent_path), source_revision=parent['source_revision'],
                  binary_path=str((target / 'collector_capture_v2').relative_to(root)),
                  scope='Same retained baseline and collector-only cores; new capture protocol keeps27 prior fixtures and adds2 conditionedf64N4 controls with per-case checkpoints. No runtime or performance qualification.')
    if code == 0:
        record['binary_sha256'] = sha(target / 'collector_capture_v2')
    (here / 'collector-capture-v2-build.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ['status', 'exit_code', 'elapsed_seconds', 'changed_inputs']}), flush=True)
    if record['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

"""Compile the separately prepared collector+n-way snapshot; never alter sources."""
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
    prepared_path = here / 'collector-nway-source.json'
    parent_path = here / 'use-dedup-full-build.json'
    prepared, parent = [json.loads(p.read_text()) for p in [prepared_path, parent_path]]
    assert prepared['status'] == 'source_prepared_only' and parent['status'] == 'passed'
    assert prepared['parent_build_manifest_sha256'] == sha(parent_path)
    frozen = root / prepared['frozen_source_root']
    target = frozen.parent
    assert not (here / 'collector-nway-build.json').exists(), 'Preserve previous builds'
    protected = dict(prepared['protected_input_hashes'])
    protected.update({str(Path(__file__).relative_to(root)): sha(Path(__file__)),
                      str(prepared_path.relative_to(root)): sha(prepared_path)})
    for name, expected in prepared['source_hashes'].items():
        assert sha(frozen / name) == expected
    for name, expected in protected.items():
        assert sha(root / name) == expected
    old_target = (root / parent['frozen_source_root']).parent
    commands = [[part.replace(str(old_target), str(target))
                 .replace('metadata=public_highpoint_use_dedup_full', 'metadata=public_highpoint_collector_nway')
                 for part in command] for command in parent['commands']]
    for command in commands:
        assert command[:2] == ['taskset', '-c']
        command[2] = '15'
    exact_command = [part.replace(str(frozen / 'crates/iregi-rust/examples/highpoint_public.rs'), str(here / 'nway_exact_probe.rs'))
                     for part in commands[1]]
    exact_command[exact_command.index('--crate-name') + 1] = 'nway_exact_probe'
    exact_command[exact_command.index('-o') + 1] = str(target / 'nway_exact_probe')
    commands.append(exact_command)
    guards = set()
    for command in commands:
        for part in command:
            if part.startswith('dependency='):
                directory = Path(part.split('=', 1)[1])
                if directory.exists():
                    guards.update(p for p in directory.iterdir() if p.suffix in ['.rlib', '.so'])
            if part.startswith(('iregi_masters=', 'symbolica=', 'serde=', 'thiserror=', 'serde_json=', 'oneloop=')):
                guards.add(Path(part.split('=', 1)[1]))
    before = {str(p.relative_to(root)): sha(p) for p in sorted(guards)}
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(frozen / 'crates/iregi-rust'), CARGO_CRATE_NAME='iregi_rust')
    codes = []
    started = time.monotonic()
    for label, command in zip(['core', 'probe', 'tests', 'exact'], commands):
        with (here / ('collector-nway-' + label + '-build.log')).open('w') as log:
            code = subprocess.call(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        codes.append(code)
        if code:
            break
    changed = {name: [expected, sha(root / name)] for name, expected in {**before, **protected}.items() if sha(root / name) != expected}
    unchanged = all(sha(frozen / name) == expected for name, expected in prepared['source_hashes'].items())
    record = dict(status='passed' if codes == [0, 0, 0, 0] and not changed and unchanged else 'failed',
                  commands=commands, exit_codes=codes, source_revision=prepared['source_revision'],
                  frozen_source_root=prepared['frozen_source_root'], source_hashes=prepared['source_hashes'],
                  prepared_manifest_sha256=sha(prepared_path), protected_input_hashes=protected,
                  dependency_hashes=before, changed_inputs=changed, sources_unchanged=unchanged,
                  elapsed_seconds=time.monotonic() - started,
                  scope='Compilation of current6b24 collector+n-way source with fine diagnostics. Runtime expression proof, semantic tests and full-array coverage require separate captures.')
    if codes == [0, 0, 0, 0]:
        for label, filename in [('binary', 'highpoint_public'), ('test_binary', 'core_tests'), ('exact_binary', 'nway_exact_probe')]:
            record[label + '_path'] = str((target / filename).relative_to(root))
            record[label + '_sha256'] = sha(target / filename)
    (here / 'collector-nway-build.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ['status', 'exit_codes', 'changed_inputs', 'elapsed_seconds']}), flush=True)
    if record['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

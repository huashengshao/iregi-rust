"""Freeze 6b24c03 with the exact reviewed collector delta and diagnostic timers.

The baseline master/Symbolica/oneloop archives are retained. All Rust link-search
inputs are guarded before/after compilation. No n-way accumulator change,
reference collector, early-stop hook, or guard relaxation is included.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
from use_dedup_full_hooks import apply_phase_hooks


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    target = root / 'target/public-highpoint/use-dedup-full'
    assert not target.exists(), 'Preserve existing frozen builds'
    revision = subprocess.check_output(['git', 'rev-parse', '6b24c03'], text=True).strip()
    original = target / 'original'
    frozen = target / 'source'
    selected = ['crates/iregi-rust/src', 'crates/iregi-rust/examples/highpoint_public.rs',
                'validation/reference/fixtures.json',
                'validation/reference/snapping/reductions.json',
                'validation/pv-high-rank/lightlike-feynman-parameters.json']
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision, '--', *selected], text=True).splitlines()
    originals = {}
    for name in names:
        data = subprocess.check_output(['git', 'show', revision + ':' + name])
        for directory in [original, frozen]:
            p = directory / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        originals[name] = sha(original / name)
    patch = here / 'use-dedup-production.patch'
    assert sha(patch) == '746b05e8a2a9060640d1c0ae4d5f3ec350e91199d817382653efde81139a35a3'
    patch_command = ['git', 'apply', '--directory=' + str(frozen.relative_to(root)), str(patch)]
    subprocess.run(patch_command[:2] + ['--check'] + patch_command[2:], check=True)
    subprocess.run(patch_command, check=True)
    snapshot = frozen / 'crates/iregi-rust'
    apply_phase_hooks(snapshot)
    candidate = (snapshot / 'src/stability.rs').read_text()
    old = (original / 'crates/iregi-rust/src/stability.rs').read_text()
    start = old.index('fn master_amplitude(')
    end = old.index('\nfn ', start + 1)
    assert old[start:end] in candidate, 'Master amplitude implementation must remain unchanged'
    assert 'collect_alias_uses_legacy' not in candidate
    assert 'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE' not in candidate
    sources = {name: sha(frozen / name) for name in names}
    diff = subprocess.run(['diff', '-ru', str(original), str(frozen)], capture_output=True, text=True)
    assert diff.returncode == 1
    (here / 'use-dedup-full-instrumentation.patch').write_text(diff.stdout)
    template_path = here / 'phase-build.json'
    template = json.loads(template_path.read_text())
    parent_snapshot = root / template['frozen_core_source']
    commands = [[part.replace(str(parent_snapshot), str(snapshot))
                 .replace(str(root / 'target/public-highpoint/phase'), str(target))
                 .replace(str(root / 'crates/iregi-rust/examples/highpoint_public.rs'),
                          str(snapshot / 'examples/highpoint_public.rs'))
                 .replace('metadata=public_highpoint_phase', 'metadata=public_highpoint_use_dedup_full')
                 for part in command] for command in template['commands']]
    test_command = commands[0].copy()
    position = test_command.index('--crate-type')
    test_command[position:position + 2] = ['--test']
    test_command = [part.replace('metadata=public_highpoint_use_dedup_full', 'metadata=public_highpoint_use_dedup_full_tests')
                    .replace(str(target / 'libiregi_rust.rlib'), str(target / 'core_tests')) for part in test_command]
    serde_json = next(part for part in commands[1] if part.startswith('serde_json='))
    oneloop = root / 'target/stack-reuse-current-workspace/deps/liboneloop-8562c3cbbf948c0e.rlib'
    test_command += ['--extern', serde_json, '--extern', 'oneloop=' + str(oneloop)]
    commands.append(test_command)
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
    protected = [Path(__file__), here / 'use_dedup_full_hooks.py', patch, template_path,
                 here / 'use-dedup-qualification.json']
    protected_before = {str(p.relative_to(root)): sha(p) for p in protected}
    env = os.environ.copy()
    env.update(CARGO_MANIFEST_DIR=str(snapshot), CARGO_CRATE_NAME='iregi_rust')
    started = time.monotonic()
    codes = []
    for label, command in zip(['core', 'probe', 'tests'], commands):
        with (here / ('use-dedup-full-' + label + '-build.log')).open('w') as log:
            code = subprocess.call(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        codes.append(code)
        if code:
            break
    after = {name: sha(root / name) for name in before}
    changed = {name: [value, after[name]] for name, value in before.items() if value != after[name]}
    for name, value in protected_before.items():
        if sha(root / name) != value:
            changed[name] = [value, sha(root / name)]
    unchanged = all(sha(frozen / name) == value for name, value in sources.items())
    record = dict(status='passed' if codes == [0, 0, 0] and not changed and unchanged else 'failed',
                  commands=commands, exit_codes=codes, source_revision=revision,
                  original_source_hashes=originals, frozen_source_hashes=sources,
                  frozen_source_root=str(frozen.relative_to(root)),
                  frozen_core_source=str(snapshot.relative_to(root)),
                  protected_input_hashes=protected_before, dependency_hashes=before,
                  changed_inputs=changed, sources_unchanged=unchanged,
                  elapsed_seconds=time.monotonic() - started,
                  instrumentation_patch_sha256=sha(here / 'use-dedup-full-instrumentation.patch'),
                  binary_path=str((target / 'highpoint_public').relative_to(root)),
                  test_binary_path=str((target / 'core_tests').relative_to(root)),
                  scope='Frozen 6b24c03 core with only reviewed alias collector delta and stderr phase timers; unchanged master amplitude accumulator and frozen baseline dependencies. Development-profile preparation/numeric diagnostic, not controlled performance qualification.')
    if codes == [0, 0, 0]:
        record.update(binary_sha256=sha(target / 'highpoint_public'), test_binary_sha256=sha(target / 'core_tests'))
    (here / 'use-dedup-full-build.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['status', 'exit_codes', 'changed_inputs', 'elapsed_seconds']}), flush=True)
    if record['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()

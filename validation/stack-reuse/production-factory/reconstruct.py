"""Reconstruct the paired frozen sources from committed checkpoint plus narrow patch.

Run from the project root in a fresh checkout, or supply a new target-only path.
Compile scripts use target/stack-reuse-production by default.
"""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
root = Path.cwd()
evidence = root / 'validation/stack-reuse/production-factory'
base = root / (sys.argv[1] if len(sys.argv) > 1 else 'target/stack-reuse-production')
assert base.is_relative_to(root / 'target'), 'Reconstruction writes under target only'
manifest = json.loads((evidence / 'manifest.json').read_text())
revision = '5c9e3dd'
assert not (base / 'snapshot').exists(), 'Choose a fresh target directory'
for key in manifest['sources']:
    if not key.startswith('snapshot/'):
        continue
    relative = key.removeprefix('snapshot/')
    data = subprocess.check_output(['git', 'show', f'{revision}:{relative}'], cwd=root)
    destination = base / key
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
subprocess.check_call(['git', 'apply', '--directory=' + str((base / 'snapshot').relative_to(root)),
                       str(evidence / 'snapshot-from-5c9e3dd.patch')], cwd=root)
shutil.copytree(base / 'snapshot/crates/iregi-masters', base / 'candidate/crates/iregi-masters')
source = base / 'candidate/crates/iregi-masters/src/lib.rs'
text = source.read_text()
needle = 'context\n        .evaluator(&expressions, &parameters)'
replacement = 'context\n        .evaluator_with_stack_reuse(&expressions, &parameters)'
assert text.count(needle) == 1
source.write_text(text.replace(needle, replacement))
for key, expected in manifest['sources'].items():
    actual = hashlib.sha256((base / key).read_bytes()).hexdigest()
    assert actual == expected, (key, actual, expected)
for name in ['compile.py', 'compile_extra.py', 'run.py', 'run_extra.py', 'factory_probe.rs', 'e6_capture.rs']:
    shutil.copyfile(evidence / name, base / name)
(base / 'snapshot/target').mkdir(exist_ok=True)
print('Reconstructed and SHA256-verified every frozen source and fixture.')

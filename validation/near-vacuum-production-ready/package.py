#!/usr/bin/env python3
"""Package the reviewed cleanup and focused tests without applying the patch."""
import difflib
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
STAGE = ROOT / 'target/near-vacuum-production-ready'
PATHS = ['crates/iregi-masters/src/lib.rs', 'crates/iregi-masters/src/certified.rs',
         'crates/iregi-masters/src/near_vacuum.rs', 'crates/iregi-masters/tests/certified.rs']

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def main():
    proof = json.loads((HERE / 'cleanup-proof.json').read_text())
    assert proof['production_changed'] is False
    for name, evidence in proof['changed_files'].items():
        assert sha(STAGE / 'crates/iregi-masters/src' / name) == evidence['staged_sha256']
    assert sha(ROOT / 'crates/iregi-masters/src/lib.rs') == proof['live_production_lib_sha256']
    typecheck = json.loads((HERE / 'public-api-typecheck.json').read_text())
    assert typecheck['status'] == 'passed' and typecheck['exit_code'] == 0
    assert typecheck['sha256_before'] == typecheck['sha256_after']
    for path, digest in typecheck['sha256_after'].items():
        assert sha(ROOT / path) == digest
    assert (HERE / 'independent-review.md').is_file()
    patch = []
    baseline = {}
    for path in PATHS:
        original = ROOT / path
        staged = STAGE / path
        baseline[path] = sha(original) if original.exists() else None
        patch.extend(difflib.unified_diff(
            original.read_text().splitlines(keepends=True) if original.exists() else [],
            staged.read_text().splitlines(keepends=True),
            fromfile=f'a/{path}' if original.exists() else '/dev/null', tofile=f'b/{path}'))
    patch_path = HERE / 'production.patch'
    patch_path.write_text(''.join(patch))
    result = subprocess.run(['git', 'apply', '--check', str(patch_path)], cwd=ROOT,
                            capture_output=True, text=True)
    (HERE / 'patch-check.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    payload = io.BytesIO()
    with gzip.GzipFile(fileobj=payload, mode='wb', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w') as archive:
            for path in PATHS:
                content = (STAGE / path).read_bytes()
                info = tarfile.TarInfo(path)
                info.size = len(content)
                info.mtime = 0
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(content))
    (HERE / 'proposed-sources.tar.gz').write_bytes(payload.getvalue())
    artifacts = {str(path.relative_to(ROOT)): sha(path) for path in sorted(HERE.iterdir())
                 if path.is_file() and path.name != 'manifest.json'}
    manifest = {
        'status': 'reviewed_unapplied_production_patch_ready', 'production_changed': False,
        'qualified_checkpoint': proof['qualified_checkpoint'],
        'staged_source_sha256': {path: sha(STAGE / path) for path in PATHS},
        'production_baseline_sha256': baseline,
        'patch_check': {'command': ['git', 'apply', '--check', str(patch_path.relative_to(ROOT))],
                        'exit_code': result.returncode, 'applied': False},
        'cleanup': 'Seven stage eprintln sites and their timer removed; module/API documentation and four diagnostic literals updated. Exact whitelist replay proves arithmetic and dispatch unchanged.',
        'focused_public_tests': {'count': 3, 'metadata_typecheck': 'passed', 'executed': False,
            'coverage': ['Mixed odd batch, lane isolation, empty/reverse inputs and independent workspace state',
                         'Explicit accuracy budgets, changed contexts and required versus ordinary policy',
                         'Common-mass third Taylor coefficient at exact vacuum and scale-only jets',
                         'Native degree-five shape with explicit uncertified fallback and no series preparation',
                         'Exact rational certificate distances, independent vacuum identities and zero Laurent poles']},
        'integration_notes': ['One combined public test executable should be built and run after integration; no four-driver relink is required.',
                              'The new public error enum variants affect downstream exhaustive matches.',
                              'The ordinary master evaluator and default E6 path remain unchanged.',
                              'This cleanup does not add input-rounding or quadrature certificates.'],
        'artifacts': artifacts,
    }
    path = HERE / 'manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'manifest': str(path.relative_to(ROOT)), 'sha256': sha(path),
                      'patch': str(patch_path.relative_to(ROOT)), 'applied': False}))

if __name__ == '__main__':
    main()

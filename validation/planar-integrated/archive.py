"""Retain the frozen standalone planar qualification; never run numerics."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess

ROOT = Path.cwd()
RAW = ROOT / 'target/planar-integrated'
DEST = ROOT / 'validation/planar-integrated'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())

build = load(RAW / 'build.json')
assert build['exit_code'] == 0 and build['dependencies_unchanged']
assert build['source_hashes'] == build['source_hashes_after']
assert sha(RAW / 'core-tests') == build['binary_sha256']
for path, digest in build['source_hashes'].items():
    assert sha(RAW / 'source-snapshot' / path) == digest, path
for dep in build['dependencies'].values():
    assert sha(Path(dep['path'])) == dep['sha256']
reports = []
for path in sorted((RAW / 'runs').glob('*.json')):
    report = load(path)
    assert report['status'] != 'running', path
    assert report['binary_sha256'] == build['binary_sha256']
    assert report['build_manifest_sha256'] == sha(RAW / 'build.json')
    reports.append((path, report))
assert len(reports) == 10
for bits in (128, 256):
    report = load(RAW / 'runs' / f'rank7-{bits}.json')
    artifact = RAW / f'precision-{bits}.json'
    assert report['output_artifact_sha256'] == sha(artifact)
assert load(RAW / 'runs/rank7-256.json')['previous_artifact_sha256'] == sha(RAW / 'precision-128.json')
assert load(RAW / 'runs/rank7-256.json')['previous_artifact_unchanged']
assert not DEST.exists(), 'preserve prior evidence bundles'
DEST.mkdir()
for name in ('base.json', 'build.json', 'build.log', 'frozen-dependencies.json',
             'build.py', 'run.py', 'run-initial.py', 'archive.py',
             'original-input-validation.txt', 'precision-128.json', 'precision-256.json'):
    shutil.copy2(RAW / name, DEST / name)
shutil.copytree(RAW / 'source-snapshot', DEST / 'source')
shutil.copytree(RAW / 'runs', DEST / 'runs')

base = '6b24c03'
patch = []
for path in sorted((RAW / 'source-snapshot/crates/iregi-rust/src').rglob('*.rs')):
    relative = str(path.relative_to(RAW / 'source-snapshot'))
    old = subprocess.run(['git', 'show', f'{base}:{relative}'], capture_output=True)
    before = old.stdout.decode() if old.returncode == 0 else ''
    patch.extend(difflib.unified_diff(before.splitlines(True), path.read_text().splitlines(True),
                                   fromfile='a/' + relative if old.returncode == 0 else '/dev/null',
                                   tofile='b/' + relative))
(DEST / 'integrated-candidate-vs-6b24.patch').write_text(''.join(patch))

precision = {}
for bits in (128, 256):
    artifact = load(RAW / f'precision-{bits}.json')
    report = load(RAW / 'runs' / f'rank7-{bits}.json')
    precision[str(bits)] = {k: artifact.get(k) for k in (
        'status', 'working_precision', 'requested_precision', 'components',
        'primary_statuses', 'independent_box_statuses', 'independent_max_normalized_error',
        'independent_tolerance', 'convergence', 'input_rows', 'analytic_rows',
        'reduction_rows', 'master_rows', 'certificate_batches')}
    precision[str(bits)].update(artifact=f'precision-{bits}.json', artifact_sha256=sha(RAW / f'precision-{bits}.json'),
                                run=f'runs/rank7-{bits}.json', elapsed_seconds=report['elapsed_seconds'],
                                stored_complex_slots=len(artifact.get('values', [])),
                                stored_independent_complex_slots=len(artifact.get('independent_box_values', [])))
qualification = {
    'schema_version': 1,
    'kind': 'private-standalone-certified-planar-public-api',
    'status': 'qualified-for-recorded-cases' if all(r['status'] == 'passed' for _, r in reports) else 'contains-failed-qualification',
    'production_promoted': False, 'automatic_workspace_fallback': False,
    'base_revision': '6b24c03', 'base_provenance': 'base.json',
    'binary_sha256': build['binary_sha256'], 'build_manifest_sha256': sha(RAW / 'build.json'),
    'source': 'source/', 'candidate_patch': 'integrated-candidate-vs-6b24.patch',
    'tests': [{'test': p.stem, 'status': r['status'], 'elapsed_seconds': r['elapsed_seconds'],
               'report': 'runs/' + p.name, 'report_sha256': sha(p),
               'log_sha256': sha(p.with_suffix('.log'))} for p, r in reports],
    'rank7_precision': precision,
    'comparison': 'Every complex tensor/Laurent component: error / max(abs(reference), physical_scale^(rank-6)) <=1e-10; rank7 Float128-to-Float256 convergence <=2^-65 with the same dimensional normalization.',
    'fixture': {'propagators': 5, 'rank_maximum': 7, 'moments': 330, 'laurent_slots': ['UV1','IR1','IR2','finite'],
                'shifts': [[0,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,1,1,1]],
                'squared_masses': [4,9,16,25,36], 'mu': 3,
                'convention': 'OneLoop', 'tensor_weights': 'Components',
                'independent_box_weights': ['1/3','-1/6','-1/6','-1/6','1/6']},
    'scope': [
        'Standalone exported CertifiedPlanarReductionPlan/Workspace; N5 unit powers, D=4-2epsilon, Preserve, FromShifts, PV, rank<=7, regular rank-three constant-one chart.',
        'Full requested Taylor determinant-zero certificate and nonzero chart primal; no projection, transverse jets rejected.',
        'Focused ordinary binary64/Float128/Float256, six-component rank-two mixed/second Dual, failed-lane isolation, ordered metadata, empty/odd/reordered batches, counters/profiles and error reuse.',
        'Rank-seven complete ordinary arrays at128 and256 bits and exact represented-value artifacts; requested accuracy53.'
    ],
    'limitations': [
        'No automatic ordinary Workspace fallback or production promotion; no rank-seven Dual qualification in this bundle.',
        'Not a performance comparison:600s run bounds, different snapshots and former180s timeouts cannot establish a speedup.',
        'Lower-rank external spans and homogeneous-only families remain unsupported without a regular constant-one chart.',
        'Rational artifact encoding loses signed-zero signs; evidence is numerical convergence, not bitwise parity.',
        'Rank-seven artifact declares configured metadata/basis and checks returned basis length; focused API tests assert returned metadata exactly, but this rank-seven test does not repeat full metadata equality.',
        'Direct dependency archives are hashed before/after build; transitive dependency search roots are retained in the exact command rather than exhaustively copied into this bundle.'
    ],
    'historical_evidence': ['validation/planar-certified/qualification.json', 'validation/planar-certified-nway/qualification.json'],
    'independent_review': 'batch_execution reviewed validator order, stats/profile error accounting, ordered shape grouping, exact artifact serialization and previous-artifact hash binding; no blocker found.',
    'evidence_manifest': 'files.json'
}
(DEST / 'qualification.json').write_text(json.dumps(qualification, indent=2) + '\n')
(DEST / 'README.md').write_text('''# Standalone certified planar API qualification

This private candidate rebases the certified planar interface onto the production
generalized-PV, allocator and conditioning-context implementation at `6b24c03`.
It exports `CertifiedPlanarReductionPlan` and `CertifiedPlanarWorkspace`, with
full-Taylor rank certificates, regular constant-one chart selection, genuine
instruction-major grouped reductions and unchanged numerical guards.

The ten focused runs and their exact scope are recorded in `qualification.json`.
The rank-seven runs retain every one of the330×4 complex coefficients and the
corresponding five-box identity in exact rational form, including each real and
imaginary component's working precision. The256-bit run binds its128-bit input
artifact by SHA256 and checks dimensionally normalized convergence.

The wrapper now validates each row before certification using the same helper
and exact check order as the ordinary executor. Analytic attempts and actual
child work are counted separately; profiling closes after errors and includes
completed child work. Failed lanes cannot be read as successful zero arrays.

The four-line Symbolica `Atom::add_many` amplitude accumulation change is retained
from the previous independently qualified private candidate. The full patch also
contains opt-in phase diagnostics and tests; it is a review patch, not an automatic
production adoption instruction. Automatic ordinary `Workspace` fallback remains
off. Rank-seven Dual coverage is outside this bundle.

Historical failures and180-second timeouts remain in `validation/planar-certified`.
This is correctness and provenance evidence, not a matched performance experiment.
Rational serialization preserves numerical values but not signed-zero bit patterns.

`source/` includes the complete frozen core and its three include fixtures.
Build and run scripts retain their historical `target/planar-integrated` paths.
Binaries and dependency archives remain hash-bound under `target`; exact commands,
direct archive hashes, all retained source hashes and raw output are committed here.
`files.json` binds all retained files. No production Rust source was changed.
''')
files = {str(p.relative_to(DEST)): {'sha256': sha(p), 'bytes': p.stat().st_size}
         for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST / 'files.json').write_text(json.dumps(files, indent=2) + '\n')
for relative, record in files.items():
    assert sha(DEST / relative) == record['sha256']
print(json.dumps({'qualification': str((DEST / 'qualification.json').relative_to(ROOT)),
                  'qualification_sha256': sha(DEST / 'qualification.json'),
                  'files': len(files), 'bytes': sum(r['bytes'] for r in files.values()),
                  'files_sha256': sha(DEST / 'files.json')}, indent=2))

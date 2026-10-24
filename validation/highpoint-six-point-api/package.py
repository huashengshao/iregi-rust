"""Copy frozen isolated-public-API evidence; no build or numerical execution."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path('/shared/external/iregi/iregi-rust')
HERE = ROOT / 'target/public-highpoint/six-point-integration'
V2 = HERE / 'input-validation-v2'
OUT = ROOT / 'validation/highpoint-six-point-api'
AUDITS = {
    'build-independent-audit.json': (
        'acba53a7d9cbc3dfba950f23fe92485112d5816ff735e71563766dbd25dcad5a',
        'passed_independent_terminal_build_artifact_audit',
        'observed_build_qualified', 'build-001/build.json'),
    'exact-independent-audit.json': (
        '56f5fb7f11b781bb5e51fdf5fed345e9dd3440b0434d5dec090ebddad0c92b50',
        'passed_independent_terminal_selected_test_audit',
        'selected_test_evidence_qualified', 'exact-comparison.json'),
    'ordinary-independent-audit.json': (
        '1c103c24044a99180549ba1a737fcb2fba21e9e0c27b56df0e45d75815402cf2',
        'passed_independent_terminal_ordinary_equivalence_audit',
        'ordinary_retained_fixture_equivalence_qualified', 'ordinary-comparison.json'),
    'public-paired-independent-audit.json': (
        'ed18c0fe016c474dd9efae1d1a1736c0868a05f2761c2224ed4dd89155bd2b81',
        'passed_independent_saved_public_rank3_paired_audit',
        'precision_convergence_qualified', 'comparison-128-256.json'),
    'lifecycle-independent-audit.json': (
        '28e4934238de7224b85b1e4d167bc738b2a3f325712b1942b21bcaffdd5b2e16',
        'passed_independent_saved_public_lifecycle_and_contraction_audit',
        'lifecycle_qualified', 'lifecycle-comparison.json'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    required = list(AUDITS)
    source_manifest = load(V2 / 'source.json')
    expected_inputs = {}
    for name, (expected_sha, status, qualified_flag, subject) in AUDITS.items():
        audit_path = V2 / name
        assert audit_path.is_file(), f'independent audit incomplete: {name}'
        assert sha(audit_path) == expected_sha, f'independent audit changed: {name}'
        audit = load(audit_path)
        assert audit['status'] == status and audit[qualified_flag] is True
        assert audit['findings'] == [] and audit['performance_qualified'] is False
        assert audit['reviewer'] == '/root/highpoint_coverage/evidence_review'
        # Bind each passed review to this current protocol, source inventory,
        # source bytes and its actual terminal comparison/build record.
        current = [V2 / 'protocol.json', V2 / 'source.json', V2 / subject]
        for relative, expected in source_manifest['candidate_files'].items():
            path = V2 / 'core' / relative
            assert sha(path) == expected
            current.append(path)
        for path in current:
            assert audit['input_sha256'][str(path.relative_to(ROOT))] == sha(path)
        for path, digest in audit['input_sha256'].items():
            assert path not in expected_inputs or expected_inputs[path] == digest
            expected_inputs[path] = digest
    # The superseded V1 patch is bound by its independently audited manifest.
    v1_manifest = HERE / 'source.json'
    assert expected_inputs[str(v1_manifest.relative_to(ROOT))] == sha(v1_manifest)
    expected_inputs[str((HERE / 'integration.patch').relative_to(ROOT))] = load(v1_manifest)['patch']['sha256']
    exact = load(V2 / 'exact-comparison.json')
    ordinary = load(V2 / 'ordinary-comparison.json')
    public = load(V2 / 'comparison-128-256.json')
    lifecycle = load(V2 / 'lifecycle-comparison.json')
    assert all(x['passed'] is True for x in (exact, ordinary, public, lifecycle))
    assert load(V2 / 'owned-groups-final-check.json')['all_owned_groups_absent']
    assert not OUT.exists(), 'never overwrite a frozen capsule'
    OUT.mkdir(parents=True)
    origins = {}

    def copy(source, relative):
        destination = OUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        expected = sha(source)
        source_key = str(source.relative_to(ROOT))
        if source_key in expected_inputs:
            assert expected == expected_inputs[source_key], f'audited payload changed: {source_key}'
        # No raw terminal evidence or actual source patch/archive may bypass
        # a reviewed input binding merely because its summary still passes.
        terminal_dirs = {
            'build-001', 'exact-001', 'ordinary-baseline-001',
            'ordinary-candidate-001', 'public-rank3-128-001',
            'public-rank3-256-001', 'lifecycle-001',
        }
        if source.name in {'sources.tar.gz', 'integration.patch'} or any(part in terminal_dirs for part in source.parts):
            assert source_key in expected_inputs, f'unbound critical payload: {source_key}'
        shutil.copyfile(source, destination)
        assert sha(destination) == expected and sha(source) == expected
        origins[str(relative)] = {
            'source': source_key,
            'sha256': expected,
            'bytes': destination.stat().st_size,
        }

    # The first source candidate, its actual source archive, and original
    # proposals/reviews remain visible even though the qualified build is V2.
    for source in sorted(HERE.iterdir()):
        if source.is_file() and source.name != Path(__file__).name:
            copy(source, Path('source-v1') / source.name)
    # Full V2 sources are in sources.tar.gz; executable artifacts stay outside
    # Git and remain bound by the receipts. Preserve every draft and all logs.
    excluded_products = {
        'libbaseline.rlib', 'libcandidate.rlib', 'lifecycle', 'ordinary',
        'six_point', 'tests',
    }
    for source in sorted(V2.rglob('*')):
        relative = source.relative_to(V2)
        if not source.is_file() or 'core' in relative.parts or '__pycache__' in relative.parts:
            continue
        if relative.parts[0] == 'build-001' and source.name in excluded_products:
            continue
        copy(source, Path('qualified-v2') / relative)
    copy(Path(__file__), Path('package.py'))
    (OUT / 'payload-origins.json').write_text(json.dumps(origins, indent=2) + '\n')

    readme = '''# Explicit six-point API: isolated integration qualification

This capsule qualifies the exact V2 source patch in an isolated build. It
does not substitute for the separately recorded production application and
Cargo build. The ordinary API is unchanged on the complete paired fixture
set; the new explicit `SixPointReductionPlan` / `SixPointWorkspace<T>` accepts
N6, ranks 0 through 3, unit powers, dimension shift zero, supplied Cartesian
shifts, Preserve, PV, native IREGI normalization and tensor components.

The public workspace accepts one ordinary component. Generic Rust typing is
broader than the high-point numerical evidence. Numerical Dual inputs,
binary64/DoubleFloat high-point accuracy, arbitrary complex masses, generalized
powers/shifts, broader kinematics, N7, rank7 and performance parity are not
qualified here. Unsupported settings reject explicitly. A failed lane cannot
be counted as numerical agreement or expose partial coefficients.

## Qualified checks

- All 34 selected tests passed. Other tests in the same binary were not run.
- All 12 ordinary baseline/candidate cases match exactly, including full
  values, precision, signs, settings, statuses, flags, diagnostics and counters:
  f64/DoubleFloat/Float128, including the existing ordered Dual settings.
  The 42 successful lanes and 18 matching rejection controls are counted
  separately; the latter establish rejection parity only.
- The retained base N6 rank3 fixture passes all 140 native Laurent slots at
  both Float128 and Float256/request53 against untouched stable original IBP
  with the unchanged dimensionally normalized 1e-10 tolerance. Each precision
  has 105 exactly zero pole slots. The full precision comparison passes 2^-80.
- Eleven rank2 Float128/request53 calls cover singleton/scaled inputs, failed
  neighbors, reorder/chunk/repeat behavior and empty batches. Seventeen
  successful lanes contribute all 1020 moment slots and 68 contraction slots;
  seven rejected lanes and two empty calls remain explicit. Certificate and
  executor counters, flags and resets are checked separately.

The contraction uses the existing Symbolica adapter for
`2 - 3*q0 + q1 + 4*q2*q3`. Its saved-data oracle is the complete rational sum
of captured components and the corresponding untouched original IBP sum.
The scale is `sum_j |c_j| Q^(rank_j - 8)`; no tolerance was enlarged.

## Provenance and reproduction

`qualified-v2/integration.patch` is the tested patch. V2 changed only malformed
input validation relative to the first source candidate. The original source
and unexecuted runner drafts, including the independently found lifecycle
defect and its repair, remain in this capsule. No failed attempt is relabeled
as a pass. `payload-origins.json` maps every copied byte to its original path.

`source-v1/sources.tar.gz` contains 59 candidate plus 44 original baseline
members under `candidate/` and `production-baseline/`. The 59-member
`qualified-v2/sources.tar.gz` contains the actual compiled V2 source and all
seven compile-time fixtures. The production baseline and source archives are
distinct from the initial source manifests. Compiler flags, all native/extern
dependencies, exact commands and output hashes are recorded in the approved
protocol and build/run receipts. No live dependency search fallback was used.
The six executable/archive outputs are retained in the original build folder
and bound by SHA256; they are intentionally not committed in this capsule.

Restore those archives at the target locations declared in the protocol,
restore the recorded dependency closure, and inspect `harness_common.py` before
reproduction. The runners refuse to overwrite prior attempt directories.
An independent reproduction must use newly named attempt directories and new
receipts; it must not change or reuse the approval/terminal records here.
The recorded sequence is build, exact tests/comparison, ordinary baseline,
ordinary candidate/comparison, public128/comparison, public256/comparison, then
lifecycle/comparison. Source the project environment and private Symbolica
license environment without printing it. No license value is stored here.

Every child ran in an owned process group, with cleanup after leader exit or
interruption and a terminal event before hashing. Aggregate caps were 180s
for build/exact/public/lifecycle and 120s for each ordinary capture, with 25s
build or 20s runtime reserves. All 19 owned groups were confirmed absent after
the full window. These durations are diagnostics, not performance benchmarks.

The previous private rank7 discrepancy remains in
`validation/highpoint-thin-n6-rank7-phase`; its failed original-reference gate
is not changed by this restricted rank3 integration checkpoint.
'''
    (OUT / 'README.md').write_text(readme)
    scalar_coverage = {
        key: value for key, value in lifecycle['coverage'].items()
        if not isinstance(value, (list, dict))
    }
    qualification = {
        'schema_version': 1,
        'status': 'isolated_restricted_public_six_point_integration_qualified',
        'isolated_build_qualified': True,
        'production_build_qualified': False,
        'production_application': 'recorded separately by ROOT; this capsule binds the isolated tested source',
        'source_patch_sha256': sha(V2 / 'integration.patch'),
        'protocol_sha256': sha(V2 / 'protocol.json'),
        'selected_exact_tests_passed': 34,
        'ordinary_equivalence': {
            key: ordinary[key] for key in (
                'paired_cases', 'successful_lanes', 'matching_failed_controls',
                'native_complex_taylor_slots', 'comparison',
            )
        },
        'public_rank3': {
            key: public[key] for key in (
                'working_bits', 'native_slots_per_precision',
                'exact_zero_poles_per_precision', 'original_tolerance',
                'convergence_tolerance', 'maximum_original_error',
                'maximum_convergence_error', 'precision_convergence_qualified',
            )
        },
        'public_rank2_lifecycle': scalar_coverage,
        'public_rank2_contraction_qualified': True,
        'public_numeric_dual_qualified': False,
        'highpoint_binary64_doublefloat_qualified': False,
        'arbitrary_complex_mass_qualified': False,
        'generalized_interface_qualified': False,
        'rank7_qualified': False,
        'n7_qualified': False,
        'performance_qualified': False,
        'rigorous_error_enclosure_claim': False,
        'independent_reviews': {
            name: sha(V2 / name) for name in required
        },
        'payloads': {
            str(path.relative_to(OUT)): {'sha256': sha(path), 'bytes': path.stat().st_size}
            for path in sorted(OUT.rglob('*')) if path.is_file()
        },
    }
    (OUT / 'qualification.json').write_text(json.dumps(qualification, indent=2) + '\n')
    print(json.dumps({'path': str(OUT.relative_to(ROOT)),
                      'qualification_sha256': sha(OUT / 'qualification.json'),
                      'payloads': len(qualification['payloads'])}))


if __name__ == '__main__':
    main()

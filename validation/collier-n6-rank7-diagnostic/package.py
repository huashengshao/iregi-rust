"""Package immutable rejected COLI evidence; launches no numerical work."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path('/shared/external/iregi/iregi-rust')
SOURCE = ROOT / 'target/collier-n6-rank7-proposal'
DEST = ROOT / 'validation/collier-n6-rank7-diagnostic'
AUDIT = ROOT / 'target/resume-20261025-review/collier-n6-rank7-independent-saved-review.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}


def main():
    assert Path.cwd().resolve() == ROOT and not DEST.exists()
    assert sha(AUDIT) == 'f1ff043675e49197fb90904d7993e7b1be33bc4dc8553a6e2f6a1bf7ed5843a0'
    review = json.loads(AUDIT.read_text())
    assert review['native_accepted'] is False and review['null_slots'] == 315
    assert review['pole_parameter_probe_failures'] == 3
    assert set(review['full_array_failure_counts'].values()) == {316}
    h = SOURCE / 'finite-v2'
    receipts = {}
    for stage in ['build', 'capture', 'compare']:
        path = h / f'{stage}-001/run.json'
        data = json.loads(path.read_text())
        assert data['status'] == 'passed' and data['inputs_unchanged'] is True
        assert not data['cleanup_errors']
        assert all(step['owned_group_gone'] is True for step in data['steps'])
        receipts[stage] = pin(path)
    comparison = json.loads((h / 'compare-001/comparison.json').read_text())
    assert comparison['collier_lane_accepted'] is False
    assert all(not value['accepted_agreement'] for value in comparison['comparisons'].values())
    DEST.mkdir()
    for source, target in [(h / 'capture-001/stdout.log', 'stdout.log'),
                           (h / 'capture-001/stderr.log', 'stderr.log'),
                           (h / 'compare-001/comparison.json', 'comparison.json'),
                           (AUDIT, 'independent-saved-review.json'),
                           (SOURCE / 'request.txt', 'request.txt'),
                           (Path(__file__), 'package.py')]:
        shutil.copyfile(source, DEST / target)
    files = {str(path.relative_to(ROOT)): path for path in SOURCE.rglob('*')
             if path.is_file() and path.suffix in {'.py', '.json', '.jsonl', '.md', '.log', '.f90', '.patch', '.txt'}}
    for name in ['collier-n6-rank7-independent-source-math-review.json',
                 'collier-n6-rank7-preflight-failure-independent-audit.json',
                 'collier-n6-rank7-independent-saved-review.json', 'audit_coli_n6_rank7_saved.py']:
        path = AUDIT.parent / name
        assert path.is_file()
        files[str(path.relative_to(ROOT))] = path
    for name in ['target/quad-iregi-source-audit/capture-v6-001/request-4.stdout',
                 'target/quad-iregi-source-audit/independent/resume-auditor-v6-full-array-numeric-review.json']:
        path = ROOT / name
        assert path.is_file()
        files[name] = path
    members = {}
    with (DEST / 'evidence.tar.gz').open('xb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for name, path in sorted(files.items()):
                    data = path.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size, info.mode = len(data), 0o644
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ''
                    archive.addfile(info, io.BytesIO(data))
                    members[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    (DEST / 'evidence-members.json').write_text(json.dumps(members, indent=2, sort_keys=True) + '\n')
    qualification = {
        'status': 'native_COLI_accuracy_rejected_diagnostic_only', 'n': 6, 'rank': 7,
        'sample': 'base_first_six_ordered_ec27_propagators_mu3', 'COLLIER_mode': 1,
        'public_tensor_interface': 'TNten_cll', 'source': 'COLLIER1.2.10',
        'requested_moments': 330, 'diagnostic_complex_positions': 1320,
        'diagnostic_null_positions': 315, 'diagnostic_nonnull_positions': 1005,
        'native_error_flag': 0, 'native_accuracy_flag': -2, 'native_accepted': False,
        'accepted_moments': None, 'all_slot_tolerance': '1e-10',
        'each_comparand_failed_positions': 316,
        'each_comparand_failure_partition': {'missing_null_positions': 315, 'finite_numerical_mismatches': 1},
        'comparands': ['TIRust256', 'original_IREGI_IBP', 'original_IREGI_PV_unstable', 'original_IREGI_Hybrid'],
        'additive_independently_admitted_quad_IBP_failed_positions': 316,
        'Laurent_available_pole_residue_failures': 0,
        'pole_parameter_probe_failures': 3,
        'pole_parameter_probe_errors': review['pole_parameter_probe_errors'],
        'pole_probe_interpretation': 'All three native parameter probes contain HUGE sentinels. Zero available Laurent pole-residue failures does not mean pole probes passed.',
        'stage_receipts': receipts, 'independent_saved_audit': pin(AUDIT),
        'retained_preflight_failure': pin(SOURCE / 'finite-v1/build-001/run.json'),
        'native_library_rebuilt': False, 'IREGI_rebuilt': False,
        'numerical_reference_qualified': False, 'performance_qualified': False,
        'earlier_original_double_discrepancy_adjudicated_by_this_COLI_result': False,
        'archive_policy': 'Deterministic source/protocol/request/receipt/log/audit archive. Native executable/compiler/archive/module caches excluded, expected identities retained. No producer runs during packaging.'}
    (DEST / 'qualification.json').write_text(json.dumps(qualification, indent=2, sort_keys=True) + '\n')
    (DEST / 'README.md').write_text('''# Rejected COLI N6/rank7 diagnostic

The one finite COLI-mode1 N6/rank7 CHECK request completed, with fresh driver-only linking, exact first-six ec27 fixture inputs at mu3, all28 Fortran modules protected and all source/artifact guards passing. Both owned compiler/native process groups are gone. The request invokes five public tensor calls including UV/IR parameter probes. No COLLIER or IREGI library was rebuilt.

The numerical lane is rejected: native error flag0 and accuracy flag−2. Its accepted moments remain null. All330×4 diagnostic positions are preserved, including315 null/missing coefficients. At the unchanged dimensionally normalized1e-10 gate, each comparison with TIRust256 and the three original IREGI modes fails316 positions:315 missing values and one finite mismatch. The independent audit also compares the independently admitted stable quad-original IBP array, with316 failures. Original PV remains a native-unstable diagnostic comparand.

All three pole-parameter probes report HUGE sentinels and fail. The separate zero count for available Laurent pole residues does **not** mean those probes pass. These rejected/incomplete diagnostics cannot qualify a rank-seven reference or adjudicate the earlier90-slot original-double discrepancy. No performance claim follows from the supervised correctness durations.

The initial finite-v1 build invocation failed its PATH environment preflight before hashing or compiler entry. Its receipt and launch contract remain unchanged. A separately reviewed finite-v2 namespace restores the exact declared environment before tasksetCPU28 and completes the unchanged60/15/40 link,180/30/120 capture and120/15 saved comparison. There was no native-integral retry or tolerance change.

`stdout.log` preserves raw status and diagnostics; `comparison.json` preserves every missing/mismatching location; `independent-saved-review.json` reconstructs all1320 positions without importing the producer comparator. `evidence.tar.gz` retains exact repository-relative source/protocol/grant/launch/log evidence and the additive quad-reference audit. Binaries and dependency caches are excluded and remain hash references; complete transitive native/compiler/system-link provenance is not inferred. Packaging runs no compiler, reference or numerical comparator.
''')
    payloads = {str(path.relative_to(DEST)): pin(path) for path in sorted(DEST.iterdir()) if path.is_file()}
    (DEST / 'manifest.json').write_text(json.dumps({'status': 'native_rejection_evidence_preserved', 'payloads': payloads, 'manifest_self_excluded': True}, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'capsule': str(DEST.relative_to(ROOT)), 'qualification_sha256': sha(DEST / 'qualification.json'), 'manifest_sha256': sha(DEST / 'manifest.json'), 'archive_members': len(members)}))


if __name__ == '__main__':
    main()

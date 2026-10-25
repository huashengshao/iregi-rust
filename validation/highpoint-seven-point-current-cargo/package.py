#!/usr/bin/env python3
"""Package sealed saved evidence. Never compile, evaluate or rehash dependency GBs."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile

ROOT = Path('/shared/external/iregi/iregi-rust')
BUNDLE = ROOT / 'target/public-seven-point-current-cargo'
DEST = ROOT / 'validation/highpoint-seven-point-current-cargo'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def relative(path):
    return str(path.relative_to(ROOT))


def pin(path):
    return {'path': relative(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def save(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    assert Path.cwd().resolve() == ROOT
    assert len(sys.argv) == 2, 'supply independent partial lifecycle audit path'
    partial = ROOT / sys.argv[1]
    assert partial.is_file()
    audit = read(partial)
    assert str(audit['status']).startswith('passed'), audit['status']
    assert not DEST.exists(), 'durable capsule must be new'
    runs = {name: BUNDLE / 'runs' / (name + '-001') / 'run.json' for name in
            ['build', 'exact', 'capture128', 'capture256', 'capture256-budget', 'lifecycle128-budget']}
    records = {name: read(path) for name, path in runs.items()}
    for name in ['build', 'exact', 'capture128', 'capture256-budget']:
        assert records[name]['status'] == 'passed'
        assert records[name]['inputs_unchanged'] is True
    assert records['capture256']['status'] == records['lifecycle128-budget']['status'] == 'failed'
    assert records['capture256']['inputs_unchanged'] is False
    assert records['lifecycle128-budget']['inputs_unchanged'] is True
    assert not (BUNDLE / 'runs/lifecycle128-001').exists()
    for record in records.values():
        assert record['cleanup_errors'] == []
        assert all(step.get('owned_group_gone') is True for step in record['steps'])
    for name in ['reference128.json', 'reference256-budget-convergence.json']:
        gate = read(BUNDLE / 'saved-gates' / name)
        assert gate['status'] == 'passed' and gate['inputs_unchanged'] is True
    prefix = read(BUNDLE / 'runs/lifecycle128-budget-001/result.json')
    expected = ['empty_before', 'singleton_base', 'odd_mixed', 'reordered', 'chunk_two', 'chunk_invalid']
    assert [call['label'] for call in prefix['calls']] == expected
    assert prefix['status'] == 'reducing' and prefix['active_call'] == 'independent_owned_scratch'

    DEST.mkdir()
    shutil.copyfile(BUNDLE / 'fixture.json', DEST / 'fixture.json')
    shutil.copyfile(BUNDLE / 'current-project-source-snapshot.tar.gz', DEST / 'sources.tar.gz')
    shutil.copyfile(BUNDLE / 'current-project-source-snapshot.json', DEST / 'source-snapshot.json')
    shutil.copyfile(Path(__file__), DEST / 'package.py')
    (DEST / 'captures').mkdir()
    for name in ['capture128', 'capture256', 'capture256-budget', 'lifecycle128-budget']:
        shutil.copyfile(runs[name].parent / 'result.json', DEST / 'captures' / (name + '.json'))

    subjects = {}
    for path in sorted(BUNDLE.rglob('*')):
        if path.is_file() and path.suffix in {'.py', '.json', '.jsonl', '.md', '.log'}:
            subjects[relative(path)] = path
    for path in sorted((ROOT / 'target/resume-20261025-review').glob('n7-current-cargo*')):
        if path.is_file() and path.suffix in {'.py', '.json', '.md', '.log'}:
            subjects[relative(path)] = path
    for pattern in ['audit_n7_current*.py', 'audit_n7_engineering*.py']:
        for path in sorted((ROOT / 'target/resume-20261025-review').glob(pattern)):
            subjects[relative(path)] = path
    subjects[relative(partial)] = partial
    # Preserve the exact original requests/logs supporting the singleton gates.
    for mode in range(3):
        for path in [ROOT / f'target/public-highpoint/thin-n7-rank0-api2/protocol/reference-mode{mode}.txt',
                     ROOT / f'validation/highpoint-thin-n7-rank0-attempt/api2/reference-002/mode{mode}.log']:
            assert path.is_file()
            subjects[relative(path)] = path
    members = {}
    with (DEST / 'evidence.tar.gz').open('xb') as raw:
        with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for name, path in sorted(subjects.items()):
                    data = path.read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size, info.mode = len(data), 0o644
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ''
                    archive.addfile(info, io.BytesIO(data))
                    members[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    save(DEST / 'evidence-members.json', members)

    qualification = {
        'schema_version': 1,
        'status': 'actual_cargo_singleton_agreement_passed_full_lifecycle_incomplete',
        'scope': 'Public restricted N7/rank0, seven unit powers, h0, PV, FromShifts, Preserve, IregiNative raw Components; ordinary Float only at one retained real-mass point.',
        'current_cargo_products': {name: records['build']['outputs'][name] for name in ['default-tests', 'tests', 'driver', 'lifecycle-driver']},
        'build': {'locked_offline': True, 'passed': True, 'source_freeze': pin(BUNDLE / 'source-freeze.json'), 'native_system_link_closure_qualified': False},
        'exact_tests': {'passed': 35, 'selected_original_cases': 29, 'selected_new_constructor_policy_case': 1, 'default_cheap_guards': 5, 'default_full_numerical_capture': False},
        'numerical_features': ['default', 'native-f64-abc'],
        'master_policy': 'Explicit Symbolica on both parent and all child workspaces despite the selective native feature.',
        'precision': {'working_bits': [128, 256], 'requested_bits': 53, 'stable_reference_complex_slots': 16, 'reference_tolerance': '1e-10', 'precision_complex_slots': 4, 'convergence_tolerance': '2^-80', 'componentwise_requested_precision_claimed': False, 'tiny_real_precision_limitation': 'A tiny finite real component reports two represented precision bits; qualification uses the declared full complex norm, not componentwise128/256-bit accuracy.'},
        'partial_lifecycle': {'full_nine_call_passed': False, 'completed_calls': expected, 'successful_rows': 7, 'rejected_rows': 3, 'empty_calls': 1, 'complete_complex_moment_slots': 28, 'complete_unit_contraction_slots': 28, 'unqualified': ['independent_owned_scratch', 'empty_after', 'malformed_call', 'valid_after_malformed'], 'timeout_child_seconds': 650, 'independent_saved_audit': pin(partial)},
        'retained_history': {'original_capture256': {'status': 'failed_child_timeout_no_arrays', 'receipt': pin(runs['capture256']), 'interrupted_postguard_not_rewritten': True}, 'engineering_capture256': {'status': 'passed_separate_named_attempt', 'receipt': pin(runs['capture256-budget'])}, 'original_lifecycle': 'not_started_superseded_budget', 'prospective_lifecycle': {'status': 'failed_child_timeout_partial_arrays', 'receipt': pin(runs['lifecycle128-budget']), 'terminal_source_artifact_guard_passed': True}},
        'source_snapshot': pin(DEST / 'sources.tar.gz'),
        'fixture': pin(DEST / 'fixture.json'),
        'stage_receipts': {name: pin(path) for name, path in runs.items()},
        'saved_gates': {name: pin(BUNDLE / 'saved-gates' / name) for name in ['reference128.json', 'reference256-budget-convergence.json']},
        'independent_audits': {relative(path): pin(path) for path in sorted((ROOT / 'target/resume-20261025-review').glob('n7-current-cargo*.json'))},
        'scope_exclusions': ['full lifecycle', 'rank1..7 N7 numerical results', 'generalized powers/dimension shifts', 'public Dual', 'other numeric types', 'complex masses', 'exceptional domains', 'independent scalar oracle', 'performance parity', 'complete original PLAN acceptance'],
        'performance_qualified': False,
        'whole_goal_complete': False,
        'archive_policy': 'Sorted USTAR/gzip with fixed metadata; source/evidence bytes retained, compiler products and dependency caches excluded. Recorded external hashes require matched closure or a separately qualified rebuild.',
    }
    save(DEST / 'qualification.json', qualification)
    (DEST / 'README.md').write_text('''# Restricted N7 current-Cargo evidence

The actual locked/offline Cargo integration builds and passes35 named tests. Its Float128 and Float256 singleton captures pass all16 complex-slot comparisons with stable original IREGI IBP/Hybrid at the unchanged normalized1e-10 gate and all four precision comparisons at2^-80. Original PV remains unstable. The selected build enables native-f64-abc, while the N7 parent and children explicitly retain Symbolica masters. Default-build evidence consists of five cheap guards, not default numerical captures.

The complete nine-call lifecycle is **incomplete**. The prospective780s stage hit its650s child ceiling during independent_owned_scratch, after six completed calls: empty, singleton, odd mixed, reordered, two-lane chunk and invalid-only chunk. Those retained records cover seven successful rows, three rejected invalid-scale rows, one empty call,28 complex moment slots and28 exact unit-contraction slots. The independent partial audit checks input snapshots, full arrays, permutation, failed/null outputs, master batching and counters. Independent scratch, the later empty call and malformed-call recovery remain unqualified. No complete-nine-call comparator or further lifecycle retry was run.

The original300s Float256 attempt timed out without arrays and its postguard was interrupted. A separate independent fresh terminal guard observed no source/artifact drift; it did not rewrite that failed receipt. A separately named600s engineering256 capture then passed with the same executable, fixture and gates. The original600s lifecycle was never started and remains explicitly superseded. All failed attempts and the pre-main argument-count diagnostic are retained. Stage durations are correctness diagnostics, never performance data.

Scope is N7/rank0, unit powers, zero dimension shift, preserved coordinate shifts, PV and native raw Components at the exact retained real-mass fixture. All21 N5 children remain mandatory; each successful parent row contributes105 scalar-master rows in the batched trace. This does not qualify higher N7 ranks, generalized inputs, public Duals, complex or exceptional cases, an independent scalar oracle, or performance. Working precision does not certify componentwise accuracy: a tiny finite real part has two represented precision bits and is accepted only by the declared full complex norm. The full implementation goal remains unfinished.

`sources.tar.gz` preserves115 project source/configuration files byte-checked against the actual tested source freeze. `evidence.tar.gz` preserves original repository-relative protocols, grants, receipts, strict logs, reference requests and independent audits. `captures/` exposes the complete successful singleton arrays and both failed partial outputs. Source snapshots and historical protocols intentionally retain their original statuses. Archives exclude executables, rlibs, native archives, credentials and caches. Their recorded identities do not prove a complete native/system-link build-input history.

Reproduce source builds with the committed Cargo examples seven_point_public_probe and seven_point_lifecycle and this exact fixture. The examples require the pinned Symbolica environment/license. A new build needs fresh qualification; copying captured hashes onto another executable is invalid. Extracting evidence into a scratch project preserves the original relative paths for saved-only inspection. `package.py` records packaging without any compiler, reducer or reference execution.
''')
    payloads = {relative(path): pin(path) for path in sorted(DEST.rglob('*')) if path.is_file()}
    save(DEST / 'manifest.json', {'status': 'durable_partial_qualification_capsule', 'payloads': payloads, 'manifest_self_excluded': True})
    print(json.dumps({'capsule': relative(DEST), 'qualification_sha256': sha(DEST / 'qualification.json'), 'manifest_sha256': sha(DEST / 'manifest.json'), 'archived_files': len(members)}))


if __name__ == '__main__':
    main()

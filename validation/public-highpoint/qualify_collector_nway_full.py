"""Bind a bounded combined-candidate capture without treating completion as agreement."""
from pathlib import Path
import hashlib
import json
from compare_public import validate


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    stem = 'n6-rank7-collector-nway-128-53'
    paths = {key: here / name for key, name in {
        'build': 'collector-nway-build.json', 'prepared': 'collector-nway-source.json',
        'semantic': 'collector-nway-checks.json', 'capture': 'collector-capture-v4-qualification.json',
        'run': stem + '-run.json', 'result': stem + '.json', 'log': stem + '.log',
        'fixture': 'fixture-conditioned_masses.json', 'previous': 'n6-rank7-pv-current-128-53.json',
        'runner': 'run_collector_nway_full.py', 'patch': 'collector-nway-prepared.patch',
    }.items()}
    build, prepared, semantic, capture, run, result, fixture, previous = [
        json.loads(paths[key].read_text()) for key in ['build', 'prepared', 'semantic', 'capture', 'run', 'result', 'fixture', 'previous']]
    assert build['status'] == semantic['status'] == 'passed'
    assert build['exit_codes'] == [0, 0, 0, 0] and build['changed_inputs'] == semantic['changed_inputs'] == {}
    assert build['sources_unchanged'] is True
    assert build['source_revision'] == prepared['source_revision'] == '6b24c0372022e22606a1ac85f30c7fa579fb41f0'
    assert build['prepared_manifest_sha256'] == sha(paths['prepared'])
    assert prepared['prepared_patch_sha256'] == sha(paths['patch'])
    assert run['status'] in ['completed', 'timeout']
    assert run['timeout_seconds'] == 600 and run['variant'] == 'collector-nway'
    assert run['build_manifest_sha256'] == semantic['build_manifest_sha256'] == sha(paths['build'])
    assert run['semantic_qualification_sha256'] == sha(paths['semantic'])
    assert run['collector_capture_qualification_sha256'] == sha(paths['capture'])
    assert capture['status'] == 'qualified' and capture['paired_cases'] == 29
    assert capture['required_ordinary_successes'] == 26 and capture['known_ordinary_guard_parity_cases'] == 3
    for name, value in capture['artifacts'].items():
        assert sha(root / name) == value, name
    assert [(row['label'], row['status'], row['checked_cases'], row['mode']) for row in semantic['runs']] == [
        ('exact', 'passed', 20, 'verify'), ('stability', 'passed', 38, 'nway'), ('execution', 'passed', 35, 'nway')]
    for row in semantic['runs']:
        assert row['exit_code'] == 0 and sha(root / row['log_path']) == row['log_sha256']
        if row['label'] == 'exact':
            assert sha(root / row['result_path']) == row['result_sha256'] == row['retained_exact_result_sha256']
            assert sha(here / 'nway-exact-results.json') == row['result_sha256']
    assert semantic['test_listing_sha256'] == sha(here / 'collector-nway-tests-list.txt')
    expected_semantic_guards = dict(build['protected_input_hashes'])
    frozen = root / build['frozen_source_root']
    expected_semantic_guards.update({str((frozen / name).relative_to(root)): value for name, value in build['source_hashes'].items()})
    for path in [here / 'run_collector_nway_checks.py', paths['build']]:
        expected_semantic_guards[str(path.relative_to(root))] = sha(path)
    for key in ['test', 'exact']:
        name = build[key + '_binary_path']
        value = build[key + '_binary_sha256']
        assert sha(root / name) == value
        expected_semantic_guards[name] = value
    assert semantic['protected_input_hashes'] == expected_semantic_guards
    for inventory in [build['protected_input_hashes'], semantic['protected_input_hashes']]:
        for name, value in inventory.items():
            assert sha(root / name) == value, name
    for name, value in build['source_hashes'].items():
        assert sha(frozen / name) == value, name
    assert run['frozen_source_files_unchanged'] == len(build['source_hashes'])
    binary = root / build['binary_path']
    assert run['binary_sha256'] == build['binary_sha256'] == sha(binary)
    assert run['fixture_sha256'] == sha(paths['fixture'])
    assert run['result_sha256'] == sha(paths['result']) and run['log_sha256'] == sha(paths['log'])
    assert run['runner_source_sha256'] == sha(paths['runner'])
    assert run['probe_source_sha256'] == sha(frozen / 'crates/iregi-rust/examples/highpoint_public.rs')
    assert run['environment_additions'] == {'IREGI_PV_PREPARATION_PROFILE': '1', 'RAYON_NUM_THREADS': '1',
        'IREGI_PREPARATION_PROFILE': '1', 'IREGI_PRIMAL_SUM_MODE': 'nway'}
    assert run['environment_removals'] == ['IREGI_ALIAS_USE_VERIFY', 'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE', 'IREGI_MASTER_AMPLITUDE_MODE']
    assert run['command'] == ['taskset', '-c', '14', str(binary), str(paths['fixture'].relative_to(root)),
                              '6', '7', 'pv', '128', '53', '1', str(paths['result'].relative_to(root))]
    for key in ['settings', 'input_exact_rational', 'basis', 'rows', 'working_bits', 'requested_bits', 'components']:
        assert result[key] == previous[key], key
    assert result['alias_count'] == 31670 and result['master_count'] == 56
    assert run['last_public_stage'] == result['status']
    entered = result['status'] in ['reducing', 'all_lanes_success', 'lanes_rejected']
    assert run['numerical_reduction_entered'] == entered
    successful = result['status'] == 'all_lanes_success'
    if successful:
        assert run['status'] == 'completed' and run['exit_code'] == 0
        validate(result, fixture)
    else:
        assert run['exit_code'] != 0
        if not entered:
            assert 'lanes' not in result
    log = paths['log'].read_text()
    assert 'diagnostic stop after alias-use reverse pass' not in log and 'HIGHPOINT_PRIMAL VERIFIED' not in log
    phases = [line for line in log.splitlines() if line.startswith(('HIGHPOINT_PHASE', 'HIGHPOINT_PRIMAL'))]
    artifacts = [*paths.values(), Path(__file__), here / 'compare_public.py', here / 'use-dedup-production.patch']
    record = dict(status='bounded_full_path_capture_qualified', outcome=run['status'],
                  last_public_stage=result['status'], exit_code=run['exit_code'],
                  elapsed_seconds=run['elapsed_seconds'], timeout_seconds=run['timeout_seconds'],
                  numerical_reduction_entered=entered, complete_successful_array_captured=successful,
                  numerical_reference_agreement_qualified=False, controlled_performance_qualified=False,
                  phase_ledger=phases,
                  scope='Current6b24 plus reviewed collector deduplication and Symbolica add_many amplitude accumulation; diagnostic counters and explicit nway mode. This binds execution and preserves failures. Any captured array still requires independent reference comparison and higher-precision convergence.',
                  artifacts={str(path.relative_to(root)): sha(path) for path in artifacts})
    (here / 'collector-nway-full-qualification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

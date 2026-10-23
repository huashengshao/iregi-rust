"""Qualify a bounded full-path capture, retaining failures without numeric claims."""
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
    stem = 'n6-rank7-use-dedup-full-128-53'
    build_path = here / 'use-dedup-full-build.json'
    semantic_path = here / 'use-dedup-full-tests-qualification.json'
    run_path = here / (stem + '-run.json')
    result_path = here / (stem + '.json')
    log_path = here / (stem + '.log')
    fixture_path = here / 'fixture-conditioned_masses.json'
    build, semantic, run, result, fixture = [json.loads(p.read_text()) for p in [build_path, semantic_path, run_path, result_path, fixture_path]]
    assert build['status'] == semantic['status'] == 'passed'
    assert build['exit_codes'] == [0, 0, 0] and build['changed_inputs'] == {}
    assert build['sources_unchanged'] is True
    assert build['source_revision'] == '6b24c0372022e22606a1ac85f30c7fa579fb41f0'
    assert run['status'] in ['completed', 'timeout']
    assert run['timeout_seconds'] == 600 and run['variant'] == 'use-dedup-full'
    assert run['build_manifest_sha256'] == semantic['build_manifest_sha256'] == sha(build_path)
    assert run['semantic_qualification_sha256'] == sha(semantic_path)
    assert semantic['exact_complete_module_counts'] == {'stability::': 38, 'execution::': 35}
    for name, value in semantic['artifacts'].items():
        assert sha(root / name) == value, name
    for name, value in build['protected_input_hashes'].items():
        assert sha(root / name) == value, name
    frozen = root / build['frozen_source_root']
    for name, value in build['frozen_source_hashes'].items():
        assert sha(frozen / name) == value, name
    assert run['frozen_source_files_unchanged'] == len(build['frozen_source_hashes']) == 25
    binary = root / build['binary_path']
    assert run['binary_sha256'] == build['binary_sha256'] == sha(binary)
    assert run['fixture_sha256'] == sha(fixture_path)
    assert run['result_sha256'] == sha(result_path) and run['log_sha256'] == sha(log_path)
    assert run['runner_source_sha256'] == sha(here / 'run_use_dedup_full.py')
    assert run['probe_source_sha256'] == sha(frozen / 'crates/iregi-rust/examples/highpoint_public.rs')
    assert build['instrumentation_patch_sha256'] == sha(here / 'use-dedup-full-instrumentation.patch')
    assert run['environment_additions'] == {'IREGI_PV_PREPARATION_PROFILE': '1', 'RAYON_NUM_THREADS': '1', 'IREGI_PREPARATION_PROFILE': '1'}
    assert run['environment_removals'] == ['IREGI_ALIAS_USE_VERIFY', 'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE', 'IREGI_MASTER_AMPLITUDE_MODE']
    assert run['command'] == ['taskset', '-c', '14', str(binary), str(fixture_path.relative_to(root)),
                              '6', '7', 'pv', '128', '53', '1', str(result_path.relative_to(root))]
    previous_path = here / 'n6-rank7-pv-current-128-53.json'
    previous = json.loads(previous_path.read_text())
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
    log = log_path.read_text()
    assert 'HIGHPOINT_USE_DEDUP' not in log and 'diagnostic stop after alias-use reverse pass' not in log
    phases = [line for line in log.splitlines() if line.startswith('HIGHPOINT_PHASE')]
    record = dict(status='bounded_full_path_capture_qualified',
                  outcome=run['status'], last_public_stage=result['status'],
                  exit_code=run['exit_code'], elapsed_seconds=run['elapsed_seconds'],
                  timeout_seconds=run['timeout_seconds'], numerical_reduction_entered=entered,
                  complete_successful_array_captured=successful,
                  numerical_reference_agreement_qualified=False,
                  controlled_performance_qualified=False,
                  phase_ledger=phases,
                  scope='Current 6b24 core plus exact reviewed collector delta and phase hooks, unchanged amplitude accumulator. This record qualifies bounded execution provenance and preserves failures. Independent numerical reference agreement and higher-precision convergence require separate comparisons.',
                  artifacts={str(p.relative_to(root)): sha(p) for p in [build_path, semantic_path, run_path, result_path, log_path, fixture_path, previous_path,
                      here / 'use-dedup-full-instrumentation.patch', here / 'use-dedup-production.patch', here / 'compare_public.py', Path(__file__)]})
    path = here / 'use-dedup-full-capture-qualification.json'
    path.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

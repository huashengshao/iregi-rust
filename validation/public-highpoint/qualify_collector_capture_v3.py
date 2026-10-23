"""Version3: exact current pairs, exact historical inputs/status, normalized historical values."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import math
import compare_collector_history as history


SETTINGS = [(1, 2, 1), (2, 2, 1), (3, 1, 1), (2, 1, 3), (1, 1, 3),
            (3, 1, 3), (4, 2, 1), (4, 1, 3), (5, 1, 1)]
CONTROLS = [(4, 2, 1), (4, 1, 3)]
REMOVED_ENVIRONMENT = ['IREGI_CORE_STACK_PROOF_DIR', 'IREGI_ALIAS_USE_VERIFY',
                       'IREGI_DIAGNOSTIC_STOP_AFTER_REVERSE', 'IREGI_PRIMAL_SUM_MODE']


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def identity(row):
    return (row['domain'], row['propagators'], row['rank'], row['components'], row['fixture'])


def check_rows(baseline, candidate, original, probe):
    assert baseline == candidate, 'Complete paired records differ'
    expected = []
    for domain in ['f64', 'DoubleFloat', 'Float128']:
        expected += [(domain, *setting, 'retained_v1') for setting in SETTINGS]
        if domain == 'f64':
            expected += [(domain, *setting, 'orthogonal_unit_n4') for setting in CONTROLS]
    assert [identity(row) for row in baseline] == expected and len(baseline) == 29
    retained = [row for row in baseline if row['fixture'] == 'retained_v1']
    assert len(original) == len(retained) == 27
    for old, new in zip(original, retained):
        # Original inputs/layout remain exact; every result field is checked below,
        # with the existing numerical tolerance for cross-preparation values.
        for key in ['domain', 'propagators', 'rank', 'components', 'input']:
            assert old[key] == new[key], ('Original capture changed', key, identity(new))
    controls = [row for row in baseline if row['fixture'] == 'orthogonal_unit_n4']
    assert controls == probe, 'Controls differ from the independently checked probe'
    positives = guards = dual_cases = successful_lanes = complex_moments = 0
    guard_records = []
    for row in baseline:
        n, rank, components = row['propagators'], row['rank'], row['components']
        positive = n < 4 or row['domain'] != 'f64' or row['fixture'] == 'orthogonal_unit_n4'
        assert row['requires_ordinary_lane_success'] is positive
        assert row['validation_role'] == ('positive' if positive else 'known_guard_parity')
        result = row['result']
        success = result['lane_successes']
        assert len(success) == 5 and all(type(value) is bool for value in success)
        assert result['ordinary_lane_success'] is success[0]
        assert result['invalid_scale_guard'] is True and success[4] is False
        assert success[0] is positive, ('Required success or retained guard changed', identity(row))
        positives += int(positive)
        guards += int(not positive)
        if row['domain'] == 'f64' and n == 2:
            assert success[3] is False, 'Deliberate binary64 invariant cancellation must stay guarded'
        for key in ['moments', 'repeat', 'contracted']:
            assert len(result[key]) == 5
        assert result['moments'] == result['repeat']
        for lane, accepted in enumerate(success):
            moments, contracted = result['moments'][lane], result['contracted'][lane]
            if not accepted:
                assert moments is None and contracted is None
                continue
            successful_lanes += 1
            assert len(moments) == math.comb(rank + 4, 4) * 4 * components
            assert len(contracted) == 4 * components
            complex_moments += len(moments)
            for value in moments + contracted:
                assert len(value) == 2
                for part in value:
                    assert isinstance(part['rational'], str)
                    Fraction(part['rational'])
                    assert type(part['negative_sign']) is bool and type(part['bits']) is int
            if lane == 0 and components > 1:
                assert components == 3
                for component in [1, 2]:
                    assert any(Fraction(part['rational']) != 0 for index, value in enumerate(moments)
                               if index % components == component for part in value), ('Requested Dual component is zero', component)
                dual_cases += 1
        guard_records.append(dict(domain=row['domain'], propagators=n, rank=rank, components=components,
                                  fixture=row['fixture'], validation_role=row['validation_role'],
                                  ordinary_lane_success=success[0], invalid_scale_lane=4,
                                  additional_guarded_lanes=[i for i, accepted in enumerate(success[:4]) if not accepted],
                                  complete_statuses=result['statuses']))
    assert (positives, guards, dual_cases) == (26, 3, 12)
    return dict(paired_cases=29, compared_lanes=145, required_ordinary_successes=positives,
                ordinary_successes=positives, known_ordinary_guard_parity_cases=guards,
                successful_lanes=successful_lanes, invalid_scale_guards=29,
                nonzero_second_order_dual_cases=dual_cases,
                compared_complex_moment_components=complex_moments, guard_records=guard_records)


def check_guard_inventory(run, build, required):
    expected = dict(build['protected_input_hashes'])
    expected.update(required)
    assert run['protected_input_hashes'] == expected, 'Run guard inventory differs from build plus runner/binary/manifest'
    assert run['environment_additions'] == {'RAYON_NUM_THREADS': '1'}
    assert run['environment_removals'] == REMOVED_ENVIRONMENT


def required_run_guards(root, build_path, build, runner_path):
    return {str(path.relative_to(root)): sha(path) for path in [runner_path, root / build['binary_path'], build_path]}


def check_artifact_inventory(artifacts, required_names):
    assert set(artifacts) == set(required_names), 'Linked artifact inventory is incomplete or unexpected'


def check_child(root, here, build_path, build, variant, cpu):
    stem = here / ('collector-v2-' + variant)
    result_path, run_path = stem.with_suffix('.json'), here / (stem.name + '-run.json')
    progress, log_path = stem.with_suffix('.progress.jsonl'), stem.with_suffix('.log')
    run, rows = [json.loads(path.read_text()) for path in [run_path, result_path]]
    assert run['status'] == 'completed' and run['exit_code'] == 0 and run['changed_inputs'] == {}
    assert run['build_manifest_sha256'] == sha(build_path)
    assert run['selection'] == 'all' and run['variant'] == variant and run['timeout_seconds'] == 300
    assert run['complete_cases'] == run['checkpoint_cases'] == 29
    check_guard_inventory(run, build, required_run_guards(root, build_path, build, here / 'run_collector_capture_v2.py'))
    assert run['command'] == ['taskset', '-c', str(cpu), str(root / build['binary_path']), str(result_path), variant, 'all']
    for name, value in run['protected_input_hashes'].items():
        assert sha(root / name) == value, name
    assert run['output_hashes'] == {str(path.relative_to(root)): sha(path) for path in [result_path, progress]}
    assert [json.loads(line) for line in progress.read_text().splitlines()] == rows
    assert sha(log_path) == run['log_sha256']
    return rows, [result_path, run_path, progress, log_path]


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'collector-capture-v2-build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'passed' and build['exit_code'] == 0 and build['changed_inputs'] == {}
    assert build['source_revision'] == '6b24c0372022e22606a1ac85f30c7fa579fb41f0'
    assert sha(root / build['binary_path']) == build['binary_sha256']
    assert build['parent_build_manifest_sha256'] == sha(here / 'collector-capture-build.json')
    for hashes in [build['protected_input_hashes'], build['dependency_hashes']]:
        for name, value in hashes.items():
            assert sha(root / name) == value, name
    artifacts = [build_path, here / 'collector-capture-build.json', Path(__file__), here / 'collector_capture_v2.rs']
    reports = []
    for variant, cpu in [('baseline', 14), ('candidate', 15)]:
        rows, paths = check_child(root, here, build_path, build, variant, cpu)
        reports.append(rows)
        artifacts += paths
    probe_path = here / 'collector-v2-probe-qualification.json'
    probe_qualification = json.loads(probe_path.read_text())
    assert probe_qualification['status'] == 'qualified' and probe_qualification['complete_paired_cases'] == 2
    probe_artifacts = [build_path, here / 'qualify_collector_v2_probe.py', here / 'compare_public.py',
                       here / 'collector-v2-probe-original.json']
    for variant in ['baseline', 'candidate']:
        probe_artifacts += [here / ('collector-v2-probe-' + variant + suffix)
                            for suffix in ['.json', '-run.json', '.progress.jsonl', '.log']]
    check_artifact_inventory(probe_qualification['artifacts'],
                             [str(path.relative_to(root)) for path in probe_artifacts])
    for name, value in probe_qualification['artifacts'].items():
        assert sha(root / name) == value, name
    probe = json.loads((here / 'collector-v2-probe-baseline.json').read_text())
    original_path = here / 'collector-capture-output.baseline.json'
    original_run_path = here / 'collector-capture-run.json'
    original_run = json.loads(original_run_path.read_text())
    assert original_run['status'] == 'timeout' and original_run['timeout_seconds'] == 300
    original_build_path = here / 'collector-capture-build.json'
    original_build = json.loads(original_build_path.read_text())
    assert original_run['build_manifest_sha256'] == sha(original_build_path)
    assert original_run['changed_inputs'] == original_build['changed_inputs'] == {}
    assert original_build['status'] == 'passed' and original_build['exit_codes'] == [0, 0]
    assert original_build['source_revision'] == build['source_revision']
    check_guard_inventory(original_run, original_build,
                          required_run_guards(root, original_build_path, original_build, here / 'run_collector_capture.py'))
    for name, value in original_run['protected_input_hashes'].items():
        assert sha(root / name) == value, name
    original_log_path = here / 'collector-capture-run.log'
    assert original_run['log_sha256'] == sha(original_log_path)
    assert original_run['command'] == ['taskset', '-c', '14', str(root / original_build['binary_path']),
                                       str(here / 'collector-capture-output.json')]
    assert original_run['output_hashes'][str(original_path.relative_to(root))] == sha(original_path)
    original = json.loads(original_path.read_text())
    counts = check_rows(*reports, original, probe)
    retained = [row for row in reports[0] if row['fixture'] == 'retained_v1']
    historical = history.compare(original, retained)
    replay_path = here / 'collector-v1-replay-baseline.json'
    replay_run_path = here / 'collector-v1-replay-baseline-run.json'
    replay_run = json.loads(replay_run_path.read_text())
    assert json.loads(replay_path.read_text()) == original, 'Original binary replay must be exactly equal'
    assert replay_run['status'] == 'completed' and replay_run['exit_code'] == 0 and replay_run['changed_inputs'] == {}
    assert replay_run['timeout_seconds'] == 300 and replay_run['complete_cases'] == 27
    assert replay_run['build_manifest_sha256'] == sha(original_build_path)
    check_guard_inventory(replay_run, original_build, required_run_guards(root, original_build_path, original_build, here / 'replay_collector_original.py'))
    for name, value in replay_run['protected_input_hashes'].items():
        assert sha(root / name) == value, name
    assert replay_run['command'] == ['taskset', '-c', '14', str(root / original_build['binary_path']), str(replay_path), 'baseline']
    assert replay_run['output_hashes'] == {str(replay_path.relative_to(root)): sha(replay_path)}
    replay_log = here / 'collector-v1-replay-baseline.log'
    assert replay_run['log_sha256'] == sha(replay_log)
    assert len(historical['changed_leaves']) == 29
    assert historical['maximum_raw_difference_exact'] == '1/340282366920938463463374607431768211456'
    artifacts += [replay_path, replay_run_path, replay_log, here / 'replay_collector_original.py',
                  here / 'compare_collector_history.py', here / 'qualify_collector_capture_v2.py',
                  here / 'collector-capture-v2-qualification.log', here / 'collector-v2-historical-differences.json']
    artifacts += [probe_path, original_path, original_run_path, original_log_path,
                  here / 'test_qualify_collector_capture_v2.py', here / 'collector-v2-qualifier-tests.log',
                  here / 'test_compare_collector_history.py', here / 'collector-history-comparator-tests.log',
                  here / 'collector-order-source-audit.json', here / 'collector-order-source-snapshot.json']
    record = dict(status='qualified', **counts, historical_numerical_comparison=historical, unchanged_original_binary_replay_exact=True,
                  protocol='Independent baseline and candidate children, each bounded at300s with durable per-case checkpoints. The original combined300s timeout remains retained.',
                  scope='Exact complete arrays, repeats, contractions, metadata, status, diagnostics, precision and inputs match pure6b24 for29 paired cases.26 ordinary lanes must succeed;3 retained f64N4/N5 ordinary guards are separate parity controls. Original27 inputs/status/layout and2 independently checked conditionedf64N4 controls are preserved. Historical numerical arrays use the unchanged normalized1e-10 tolerance;29 rounding/precision/sign leaves differ, max raw2^-128. Same-protocol current baseline/candidate remain exactly equal. Cross-preparation bitwise reproducibility and the specific cause are not claimed. Dual derivatives are paired snapshots, not independently established here. No N6/N7 full-array or performance claim.',
                  artifacts={str(path.relative_to(root)): sha(path) for path in artifacts})
    (here / 'collector-capture-v3-qualification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

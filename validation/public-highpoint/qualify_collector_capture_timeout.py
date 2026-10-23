"""Preserve the original combined-bound capture failure and baseline controls."""
from pathlib import Path
import hashlib
import json


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'collector-capture-build.json'
    run_path = here / 'collector-capture-run.json'
    baseline_path = here / 'collector-capture-output.baseline.json'
    build, run, baseline = [json.loads(path.read_text()) for path in [build_path, run_path, baseline_path]]
    assert build['status'] == 'passed' and build['exit_codes'] == [0, 0]
    assert run['status'] == 'timeout' and run['exit_code'] == -9 and run['timeout_seconds'] == 300
    assert run['changed_inputs'] == build['changed_inputs'] == {}
    assert run['build_manifest_sha256'] == sha(build_path)
    assert run['output_hashes'] == {str(baseline_path.relative_to(root)): sha(baseline_path)}
    assert not (here / 'collector-capture-output.candidate.json').exists()
    assert not (here / 'collector-capture-output.json').exists()
    assert len(baseline) == 27
    for name, value in run['protected_input_hashes'].items():
        assert sha(root / name) == value
    failures = [dict(domain=row['domain'], propagators=row['propagators'], rank=row['rank'],
                     components=row['components'], statuses=row['result']['statuses'])
                for row in baseline if not row['result']['ordinary_lane_success']]
    assert [(row['domain'], row['propagators'], row['rank'], row['components']) for row in failures] == [
        ('f64', 4, 2, 1), ('f64', 4, 1, 3), ('f64', 5, 1, 1)]
    assert all(row['result']['invalid_scale_guard'] is True for row in baseline)
    log_path = here / 'collector-capture-run.log'
    assert sha(log_path) == run['log_sha256']
    record = dict(status='bounded_failure_capture_qualified', runtime_outcome='timeout',
                  elapsed_seconds=run['elapsed_seconds'], timeout_seconds=300,
                  complete_baseline_cases=27, complete_candidate_cases=0,
                  baseline_ordinary_successes=24, baseline_ordinary_failures=failures,
                  paired_numerical_agreement_qualified=False, performance_qualified=False,
                  scope='The original combined300s bound was reached after a complete27case baseline and during the candidate child. Two required binary64N4 cases also fail the unchanged baseline cancellation guard. No paired agreement or success-only qualification; all raw failures retained.',
                  artifacts={str(path.relative_to(root)): sha(path) for path in [build_path, run_path, baseline_path, log_path, here / 'collector_capture.rs', Path(__file__)]})
    (here / 'collector-capture-timeout-qualification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

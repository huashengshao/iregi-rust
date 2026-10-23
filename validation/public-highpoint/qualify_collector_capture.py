"""Require complete exact paired arrays and successful ordinary lanes, not all-failure agreement."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import math


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'collector-capture-build.json'
    run_path = here / 'collector-capture-run.json'
    build, run = [json.loads(p.read_text()) for p in [build_path, run_path]]
    assert build['status'] == 'passed' and build['exit_codes'] == [0, 0]
    assert build['changed_inputs'] == run['changed_inputs'] == {}
    assert run['status'] == 'completed' and run['exit_code'] == 0
    assert run['build_manifest_sha256'] == sha(build_path)
    assert run['timeout_seconds'] == 300
    assert build['source_revision'] == '6b24c0372022e22606a1ac85f30c7fa579fb41f0'
    for entries in [build['protected_input_hashes'], run['protected_input_hashes']]:
        for name, expected in entries.items():
            assert sha(root / name) == expected, name
    log_path = here / 'collector-capture-run.log'
    assert sha(log_path) == run['log_sha256']
    outputs = [here / ('collector-capture-output' + suffix) for suffix in ['.json', '.baseline.json', '.candidate.json']]
    assert run['command'] == ['taskset', '-c', '14', str(root / build['binary_path']), str(outputs[0])]
    assert all(sha(path) == run['output_hashes'][str(path.relative_to(root))] for path in outputs)
    reports = [json.loads(path.read_text()) for path in outputs]
    assert reports[0] == reports[1] == reports[2]
    cases = reports[0]
    settings = [(1, 2, 1), (2, 2, 1), (3, 1, 1), (2, 1, 3), (1, 1, 3), (3, 1, 3), (4, 2, 1), (4, 1, 3), (5, 1, 1)]
    expected = [(domain, *setting) for domain in ['f64', 'DoubleFloat', 'Float128'] for setting in settings]
    observed = [(row['domain'], row['propagators'], row['rank'], row['components']) for row in cases]
    assert observed == expected and len(cases) == 27
    required_successes = 0
    ordinary_successes = 0
    successful_lanes = 0
    compared_complex_moments = 0
    guard_records = []
    nonzero_dual_cases = 0
    for row in cases:
        n, rank, components = row['propagators'], row['rank'], row['components']
        result = row['result']
        required = n < 5 or row['domain'] == 'Float128'
        assert row['requires_ordinary_lane_success'] == required
        success = result['lane_successes']
        assert len(success) == 5 and all(type(value) is bool for value in success)
        assert result['ordinary_lane_success'] == success[0]
        assert result['invalid_scale_guard'] is True and success[4] is False
        if required:
            assert success[0], (row['domain'], n, rank, components)
            required_successes += 1
        ordinary_successes += int(success[0])
        if row['domain'] == 'f64' and n == 2:
            assert success[3] is False, 'Deliberate binary64 invariant cancellation must stay guarded'
        for key in ['moments', 'repeat', 'contracted']:
            assert len(result[key]) == 5
        assert result['moments'] == result['repeat']
        for lane, accepted in enumerate(success):
            if not accepted:
                assert result['moments'][lane] is None and result['contracted'][lane] is None
                continue
            successful_lanes += 1
            moments = result['moments'][lane]
            assert len(moments) == math.comb(rank + 4, 4) * 4 * components
            assert len(result['contracted'][lane]) == 4 * components
            compared_complex_moments += len(moments)
            for value in moments + result['contracted'][lane]:
                assert len(value) == 2
                for part in value:
                    assert isinstance(part['rational'], str)
                    Fraction(part['rational'])
                    assert type(part['negative_sign']) is bool and type(part['bits']) is int
            if lane == 0 and components > 1:
                assert any(Fraction(part['rational']) != 0 for index, value in enumerate(moments)
                           if index % components != 0 for part in value), 'A requested Dual jet must be exercised'
                nonzero_dual_cases += 1
        guard_records.append(dict(domain=row['domain'], propagators=n, rank=rank, components=components,
                                  ordinary_lane_success=success[0], required_ordinary_success=required,
                                  invalid_scale_lane=4,
                                  additional_guarded_lanes=[i for i, accepted in enumerate(success[:4]) if not accepted],
                                  complete_statuses=result['statuses']))
    assert required_successes == 25 and nonzero_dual_cases == 12
    record = dict(status='qualified', paired_cases=27, compared_lanes=135,
                  required_ordinary_successes=required_successes, ordinary_successes=ordinary_successes,
                  successful_lanes=successful_lanes, invalid_scale_guards=27,
                  nonzero_second_order_dual_cases=nonzero_dual_cases,
                  compared_complex_moment_components=compared_complex_moments,
                  guard_records=guard_records,
                  scope='Exact complete public arrays, repeated calls, contractions, metadata, diagnostics, status and precision match a pure6b24 baseline for27 cases. Every N1..4 ordinary/Dual case and N5Float128 ordinary case requires lane0Success; any N5f64/DD guards remain visible. No graph-instruction-order, independent integral identity, N6/N7 full-array or performance claim.',
                  artifacts={str(path.relative_to(root)): sha(path) for path in [build_path, run_path, log_path, *outputs, here / 'collector_capture.rs', Path(__file__)]})
    (here / 'collector-capture-qualification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

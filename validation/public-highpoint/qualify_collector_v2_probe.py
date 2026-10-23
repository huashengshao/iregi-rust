"""Check conditioned f64 controls against matched cores and untouched original IREGI."""
from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import subprocess
import time
import compare_public as public


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def primal_input(case):
    return [[part['rational'] for part in value] for value in case['input'][:21 * case['components']:case['components']]]


def main():
    root = Path.cwd()
    here = root / 'validation/public-highpoint'
    build_path = here / 'collector-capture-v2-build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'passed'
    artifacts = [build_path, Path(__file__), here / 'compare_public.py']
    reports = []
    for variant in ['baseline', 'candidate']:
        stem = here / ('collector-v2-probe-' + variant)
        result_path = stem.with_suffix('.json')
        run_path = here / (stem.name + '-run.json')
        run, rows = [json.loads(path.read_text()) for path in [run_path, result_path]]
        assert run['status'] == 'completed' and run['exit_code'] == 0 and run['changed_inputs'] == {}
        assert run['build_manifest_sha256'] == sha(build_path)
        assert run['selection'] == 'conditioned-f64' and run['variant'] == variant and run['timeout_seconds'] == 90
        assert run['complete_cases'] == run['checkpoint_cases'] == 2
        for name, value in run['protected_input_hashes'].items():
            assert sha(root / name) == value
        for name, value in run['output_hashes'].items():
            assert sha(root / name) == value
        progress = stem.with_suffix('.progress.jsonl')
        assert [json.loads(line) for line in progress.read_text().splitlines()] == rows
        log_path = stem.with_suffix('.log')
        assert sha(log_path) == run['log_sha256']
        reports.append(rows)
        artifacts += [result_path, run_path, progress, log_path]
    assert reports[0] == reports[1]
    rows = reports[0]
    assert [(row['domain'], row['propagators'], row['rank'], row['components'], row['fixture']) for row in rows] == [
        ('f64', 4, 2, 1, 'orthogonal_unit_n4'), ('f64', 4, 1, 3, 'orthogonal_unit_n4')]
    for row in rows:
        assert row['requires_ordinary_lane_success'] is True and row['validation_role'] == 'positive'
        assert row['result']['lane_successes'] == [True, False, True, False, False]
        assert row['result']['invalid_scale_guard'] is True
        assert row['result']['moments'] == row['result']['repeat']
        expected_basis = '[' + ', '.join('Monomial(' + str(powers) + ')' for powers in public.canonical_basis(row['rank'])) + ']'
        assert row['result']['basis'] == expected_basis
    assert primal_input(rows[0]) == primal_input(rows[1])
    values = primal_input(rows[0])
    assert all(value[1] == '0' for value in values)
    sample = dict(id='orthogonal_unit_n4', mu=values[20][0], propagators=[
        dict(shift=[value[0] for value in values[4*i:4*i+4]], mass_squared=values[16+i], power=1) for i in range(4)])
    assert sample['mu'] == '3'
    assert [p['mass_squared'] for p in sample['propagators']] == [[str(i), '0'] for i in range(1, 5)]
    executable = root / 'target/reference/iregi-reference-original'
    reference_path = here / 'collector-v2-probe-original.json'
    label = 'collector_v2_orthogonal_n4_rank2'
    request = f'EVAL {label} tensor 0 4 2 0 3 0 1e-6\n'
    request += ''.join(' '.join(p['shift'] + p['mass_squared']) + ' 1\n' for p in sample['propagators']) + 'QUIT\n'
    if not reference_path.exists():
        started = time.monotonic()
        child = subprocess.run([str(executable)], input=request, capture_output=True, text=True, timeout=30)
        reference = dict(executable_sha256=sha(executable), command=[str(executable)], request=request,
                         exit_code=child.returncode, elapsed_seconds=time.monotonic() - started,
                         stdout=child.stdout, stderr=child.stderr, reference='untouched original IREGI')
        reference_path.write_text(json.dumps(reference, indent=2) + '\n')
    reference = json.loads(reference_path.read_text())
    assert reference['executable_sha256'] == sha(executable) and reference['request'] == request and reference['exit_code'] == 0
    parsed = [json.loads(line[7:], parse_float=str) for line in reference['stdout'].splitlines() if line.startswith('RESULT ')]
    assert len(parsed) == 1 and parsed[0]['id'] == label and parsed[0]['stable'] is True
    answer = parsed[0]
    assert answer['poles'] == ['uv1', 'ir1', 'ir2', 'finite'] and len(answer['moments']) == 15
    comparisons = []
    with localcontext() as context:
        context.prec = 100
        q = public.scale(sample, 4)
        for row in rows:
            components = row['components']
            values = row['result']['moments'][0]
            assert len(values) == len(public.canonical_basis(row['rank'])) * 4 * components
            maximum = Decimal(0)
            for i, powers in enumerate(public.canonical_basis(row['rank'])):
                normalization = q ** (sum(powers) - 4)
                for slot in range(4):
                    value = [public.decimal_rational(part['rational']) / normalization for part in values[(i*4+slot)*components]]
                    old = [Decimal(str(part)) / normalization for part in answer['moments'][i][slot]]
                    error = public.norm([a-b for a, b in zip(value, old)]) / max(Decimal(1), public.norm(old))
                    maximum = max(maximum, error)
                    assert error <= Decimal('1e-10'), (row['rank'], components, i, slot, error)
                    if slot < 3:
                        assert max(public.norm(value), public.norm(old)) <= Decimal('1e-10')
            if components > 1:
                assert any(Fraction(part['rational']) != 0 for index, value in enumerate(values)
                           if index % components != 0 for part in value)
            comparisons.append(dict(rank=row['rank'], components=components,
                                    compared_primal_complex_slots=len(values) // components,
                                    maximum_normalized_reference_error=str(maximum)))
    artifacts.append(reference_path)
    record = dict(status='qualified', complete_paired_cases=2,
                  successful_ordinary_and_complex_lanes_per_case=2,
                  separately_retained_guard_lanes_per_case=3,
                  original_reference_primal_comparisons=comparisons,
                  scope='Conditionedf64N4 rank2 ordinary and rank1 second-orderDual controls produce complete arrays in lanes0/2 with exact baseline/candidate equality. Lane0 ordinary/primal coefficients also agree with untouched original IREGI at strict normalized1e-10; this does not independently validate Dual derivatives or qualify performance.',
                  artifacts={str(path.relative_to(root)): sha(path) for path in artifacts})
    (here / 'collector-v2-probe-qualification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()

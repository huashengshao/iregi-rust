#!/usr/bin/env python3
"""Independently audit an archived double-precision COLLIER sweep.

Saved JSON/text only: no compiler, binary execution or native Python imports.
The achieved norm is recomputed with Decimal, independently of the runner's
exact-Fraction implementation. The default output is a new target/ report.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path.cwd().resolve()
HERE = Path('validation/benchmark/opening-double-20261026/collier')
REFERENCE = Path('validation/benchmark/opening-rank6-20261026')
LABELS = ('preflight', 'pilot', 'timed', 'postflight')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('target/opening-double-20261026/collier-independent-review.json'))
    parser.add_argument('--inspect-local-build', action='store_true')
    args = parser.parse_args()
    capture = args.capture.resolve()
    errors, files, rows = [], {}, []
    checks = 0

    def check(value, description):
        nonlocal checks
        checks += 1
        if not value:
            errors.append(description)

    def binding(path):
        resolved = path.resolve()
        name = str(resolved.relative_to(ROOT))
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        files[name] = digest
        return {'source': name, 'sha256': digest}

    def read(path):
        binding(path)
        return json.loads(path.read_text())

    def close(actual, expected, message):
        check(type(actual) in (int, float) and math.isfinite(actual)
              and math.isclose(actual, expected, rel_tol=3e-13, abs_tol=1e-28), message)

    def decimal_rational(text):
        value = Fraction(text)
        return Decimal(value.numerator)/Decimal(value.denominator)

    def option_matrix(n, rank):
        modes = (1,) if (n, rank) == (5, 6) else (1, 2)
        return [(mode, ten, permutation) for mode in modes
                for ten in ((6, 7) if n == 6 else (6,))
                for permutation in ((0, 1) if n >= 5 else (0,))]

    def timing(values):
        average = statistics.mean(values)
        deviation = statistics.stdev(values)
        sem = deviation/math.sqrt(len(values))
        return {'mean': average, 'median': statistics.median(values), 'stddev': deviation,
                'standard_error': sem, 'confidence_95_half_width_student_t': 2.228138852*sem,
                'minimum': min(values), 'maximum': max(values)}

    def inspect_array(array, reference, row, context):
        basis = [degree for degree in range(row['rank']+1)
                 for t in range(degree, -1, -1) for x in range(degree-t, -1, -1)
                 for y in range(degree-t-x, -1, -1)]
        check(isinstance(array, list) and len(array) == len(basis), context+' cumulative moment count')
        if not isinstance(array, list) or len(array) != len(basis):
            return dict(complete=False, finite=False, within_three_digits=False)
        maximum_error, maximum_reference, mixed = Decimal(0), Decimal(0), Decimal(0)
        missing, fields = 0, 0
        with localcontext() as ctx:
            ctx.prec = 100
            mu = decimal_rational(row['input']['driver_request']['samples'][0]['mu'])
            for moment, (degree, slots) in enumerate(zip(basis, array)):
                check(isinstance(slots, list) and len(slots) == 4, context+' four Laurent slots')
                if not isinstance(slots, list) or len(slots) != 4:
                    return dict(complete=False, finite=False, within_three_digits=False)
                scale = mu**(degree+4-2*row['n'])
                for slot, value in enumerate(slots):
                    fields += 1
                    expected = [decimal_rational(component['exact_rational'])
                                for component in reference[4*moment+slot]]
                    reference_norm = sum(component*component for component in expected).sqrt()
                    maximum_reference = max(maximum_reference, reference_norm/scale)
                    if value is None:
                        missing += 1
                        continue
                    check(isinstance(value, list) and len(value) == 2
                          and all(type(component) in (int, float) and math.isfinite(component) for component in value),
                          context+' finite complex encoding')
                    if not isinstance(value, list) or len(value) != 2:
                        return dict(complete=False, finite=False, within_three_digits=False)
                    actual = [Decimal.from_float(component) if isinstance(component, float) else Decimal(component)
                              for component in value]
                    magnitude = sum((a-b)*(a-b) for a, b in zip(actual, expected)).sqrt()
                    maximum_error = max(maximum_error, magnitude/scale)
                    mixed = max(mixed, magnitude/max(scale, reference_norm))
            ratio = maximum_error/maximum_reference if maximum_reference else Decimal(0) if not maximum_error else Decimal('Infinity')
            return dict(complete=True, finite=missing == 0, complex_fields=fields,
                        nonfinite_complex_fields=missing, array_relative_error=float(ratio),
                        maximum_coefficient_mixed_normalized_error=float(mixed),
                        within_three_digits=missing == 0 and ratio <= Decimal('1e-3'))

    data = read(capture/'results.json')
    check(data.get('kind') == 'opening-double-collier-public-option-sweep', 'campaign kind')
    check(data.get('numeric_type') == 'binary64' and data.get('working_bits') == 53, 'binary64 campaign')
    check(data.get('status') == 'completed', 'completed capture status')
    check(data.get('sources_unchanged_after') is True and data.get('binary_unchanged_after') is True, 'campaign source guards')
    check(data.get('repeats') == 11 and data.get('target_block_ns') == 30000000, 'fixed timing protocol')
    for path, digest in data['input_sources'].items():
        actual = binding(ROOT/path)
        check(actual['sha256'] == digest, 'source hash '+path)
    binding(ROOT/HERE/'independent_check.py')
    if args.inspect_local_build:
        check(binding(ROOT/data['binary']['path'])['sha256'] == data['binary']['sha256'], 'local binary hash')
    raw_rows = data.get('rows', [])
    check(len(raw_rows) == 12 and len({row['id'] for row in raw_rows}) == 12, 'twelve distinct ordinary rows')
    candidate_count = 0
    for row in raw_rows:
        row_id = row['id']
        ref_path = ROOT/REFERENCE/'cases'/row_id/'result.json'
        ref_data = read(ref_path)
        reference = ref_data['first_output']['lanes'][0]['values']
        check(row['reference_array']['path'] == str(ref_path.relative_to(ROOT)), row_id+' reference path')
        check(row['reference_array']['sha256'] == files[str(ref_path.relative_to(ROOT))], row_id+' reference hash')
        check(ref_data['status'] == 'measured' and ref_data['first_output']['lanes'][0]['status'] == 'Success', row_id+' qualified saved reference')
        candidates = row.get('candidates', [])
        matrix = option_matrix(row['n'], row['rank'])
        actual_matrix = [(c['configuration']['mode'], c['configuration']['direct_tensor_threshold'],
                          c['configuration']['argument_permutation']) for c in candidates]
        check(actual_matrix == matrix, row_id+' exact fixed candidate matrix/order')
        candidate_count += len(candidates)
        reviewed_candidates = []
        cache = {}
        for candidate in candidates:
            option = candidate['configuration']
            name = option['id']
            context = row_id+'/'+name
            directory = capture/row_id/name
            expected_request = '1e-6' if row['n'] >= 5 else '1e-10'
            check(option['requested_accuracy'] == expected_request and option['critical_accuracy'] == '1e-3', context+' accuracy policy')
            check(candidate.get('binary_unchanged_after') is True and candidate.get('reference_array_unchanged_after') is True, context+' source guards')
            all_arrays, array_hashes, response_bindings = [], [], []
            recorded_labels = tuple(candidate.get('captures', {}))
            terminal_failed = candidate['status'] in ('failed', 'timeout')
            check(recorded_labels == LABELS if not terminal_failed else recorded_labels == LABELS[:len(recorded_labels)], context+' phase order/retained partial attempt')
            for label in recorded_labels:
                record = candidate['captures'][label]
                response_path = directory/(label+'.response.json')
                request_path = directory/(label+'.request.txt')
                response = read(response_path)
                response_bindings.append(binding(response_path))
                request_binding = binding(request_path)
                response_bindings.append(request_binding)
                check(record['response_sha256'] == files[str(response_path.relative_to(ROOT))], context+'/'+label+' response hash')
                check(Path(record['response']).parts[-3:] == (row_id, name, label+'.response.json'), context+'/'+label+' captured path suffix')
                header = request_path.read_text().splitlines()[0].split()
                check(len(header) == 14, context+'/'+label+' wire header size')
                check(header[:5] == [('CHECK' if label in ('preflight','postflight') else 'BENCH'), row_id,
                                     str(option['mode']), str(row['n']), str(row['rank'])], context+'/'+label+' wire request identity')
                check(header[10:] == [expected_request, '1e-3', str(option['direct_tensor_threshold']), str(option['argument_permutation'])], context+'/'+label+' wire options')
                check(response.get('id') == row_id and response.get('collier_mode') == option['mode'], context+'/'+label+' response identity')
                check(response.get('argument_permutation') == option['argument_permutation']
                      and response.get('direct_tensor_threshold') == option['direct_tensor_threshold'], context+'/'+label+' response public options')
                close(response.get('requested_accuracy'), float(expected_request), context+'/'+label+' requested accuracy')
                close(response.get('critical_accuracy'), 1e-3, context+'/'+label+' critical accuracy')
                repeats = 11 if label == 'timed' else 1
                check(len(response.get('total_ns', [])) == repeats and len(response.get('blocks', [])) == repeats, context+'/'+label+' block count')
                check(len(response.get('lanes', [])) == 1, context+'/'+label+' singleton lane')
                lane = response['lanes'][0]
                arrays = [lane.get('moments') or lane.get('diagnostic_moments')]
                arrays += [block['lanes'][0]['moments'] for block in response['blocks']]
                phase_comparisons = []
                for array in arrays:
                    array_hash = hashlib.sha256(json.dumps(array, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
                    array_hashes.append(array_hash)
                    if array_hash not in cache:
                        cache[array_hash] = inspect_array(array, reference, row, context+'/'+label)
                    phase_comparisons.append(cache[array_hash])
                    all_arrays.append(cache[array_hash])
                original_comparisons = record['assessment']['arrays']
                check(len(original_comparisons) == len(phase_comparisons), context+'/'+label+' comparison count')
                for actual, advertised in zip(phase_comparisons, original_comparisons):
                    for key in ('complete', 'finite', 'complex_fields', 'nonfinite_complex_fields', 'within_three_digits'):
                        check(actual.get(key) == advertised.get(key), context+'/'+label+' independent '+key)
                    close(advertised.get('array_relative_error'), actual.get('array_relative_error'), context+'/'+label+' independent array norm')
                    close(advertised.get('maximum_coefficient_mixed_normalized_error'), actual.get('maximum_coefficient_mixed_normalized_error'), context+'/'+label+' independent mixed norm')
                if label == 'timed':
                    metrics = timing(response['total_ns'])
                    if 'timing_ns' in candidate and 'timing_us' in candidate:
                        for key, expected in metrics.items():
                            close(candidate['timing_ns'][key], expected, context+' time ns '+key)
                            close(candidate['timing_us'][key], expected/1000, context+' time us '+key)
                    else:
                        # A later postflight failure may leave a valid raw timed
                        # response but no advertised completed-candidate statistics.
                        check(terminal_failed, context+' missing completed timing statistics')
                    check(int(header[7]) == 3 and int(header[8]) == 11 and int(header[9]) == candidate['iterations_per_block'], context+' timed calls')
            for log in ('collier.stdout.log', 'collier.stderr.log'):
                if (directory/log).exists():
                    response_bindings.append(binding(directory/log))
            if not terminal_failed:
                eligible = bool(all_arrays) and all(array['within_three_digits'] for array in all_arrays)
                check(candidate.get('within_three_digits') is eligible, context+' three-digit classification')
                check(candidate.get('native_returncode') == 0, context+' normal process exit')
                maximum_error = max(array['array_relative_error'] for array in all_arrays)
                maximum_mixed = max(array['maximum_coefficient_mixed_normalized_error'] for array in all_arrays)
                missing = max(array['nonfinite_complex_fields'] for array in all_arrays)
                close(candidate['maximum_array_relative_error_over_finite_fields'], maximum_error, context+' maximum relative error')
                close(candidate['maximum_coefficient_mixed_normalized_error_over_finite_fields'], maximum_mixed, context+' maximum mixed error')
                check(candidate['nonfinite_complex_fields'] == missing, context+' nonfinite count')
                check(candidate['array_values_identical_across_all_snapshots'] == (len(set(array_hashes)) == 1), context+' deterministic arrays')
                reviewed_candidates.append({'id': name, 'configuration': option, 'eligible_at_three_digits': eligible,
                    'timing_mean_us': candidate['timing_us']['mean'], 'protocol_valid': candidate.get('protocol_valid', False),
                    'array_relative_error': maximum_error,
                    'maximum_coefficient_mixed_normalized_error': maximum_mixed, 'nonfinite_complex_fields': missing,
                    'source_bindings': response_bindings})
            else:
                reviewed_candidates.append({'id': name, 'configuration': option, 'eligible_at_three_digits': False,
                    'terminal_failure': candidate['status'], 'source_bindings': response_bindings})
        observed = [candidate for candidate in reviewed_candidates
                    if candidate.get('protocol_valid') and 'timing_mean_us' in candidate]
        accurate = [candidate for candidate in observed if candidate['eligible_at_three_digits']]
        selected = min(accurate or observed, key=lambda candidate: candidate['timing_mean_us']) if observed else None
        check(selected is not None and row['selected_candidate'] == selected['id'], row_id+' independent fastest eligible mean selection')
        if selected:
            close(row['timing_us']['mean'], selected['timing_mean_us'], row_id+' selected mean')
            close(row['array_relative_error'], selected['array_relative_error'], row_id+' selected accuracy')
            check(row['nonfinite_complex_fields'] == selected['nonfinite_complex_fields'], row_id+' selected nonfinite')
            check(row['within_three_digits'] == selected['eligible_at_three_digits'], row_id+' selected three-digit status')
        rows.append({'id': row_id, 'n': row['n'], 'rank': row['rank'], 'selected_candidate': selected['id'] if selected else None,
                     'expected_within_three_digits': bool(accurate), 'candidates': reviewed_candidates})
    check(candidate_count == 32, 'all thirty-two predeclared trials retained')
    # Bind every attempt byte, including an unanswered final request, standalone
    # assessment files or a response saved before a later assessment exception.
    # Review/summary outputs live outside these per-row raw capture directories.
    for row in raw_rows:
        for path in sorted((capture/row['id']).rglob('*')):
            if path.is_file():
                binding(path)
    report = {'schema_version': 1, 'status': 'passed' if not errors else 'failed',
              'scope': 'Independent saved-data audit: Decimal whole-array norm, exact binary64 observed values, all cumulative Cartesian/Laurent fields, public option policy, timing statistics, fastest eligible mean selection and captured-file hashes. No native evaluation.',
              'capture': binding(capture/'results.json'), 'checks': checks, 'errors': errors,
              'rows': rows, 'candidate_count': candidate_count, 'files': files}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'status': report['status'], 'checks': checks, 'errors': errors, 'output': str(args.output)}))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fixed public-option binary64 COLLIER timing sweep; run from repository root.

No compilation is performed here. Root supplies a frozen binary and grants the
CPU quiet window. All observations and native warnings are retained. Selection
uses achieved whole-array relative accuracy, never native warning flags alone.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import selectors
import statistics
import time

ROOT = Path.cwd().resolve()
HERE = Path('validation/benchmark/opening-double-20261026/collier')
ORIGINAL = Path('validation/benchmark/opening-rank6-20261026')
KERNEL = Path('validation/benchmark/run.py')
SPEC = importlib.util.spec_from_file_location('opening_double_collier_transport', ROOT / KERNEL)
kernel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kernel)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


class CaptureProcess(kernel.Process):
    """Existing bounded transport, with exact stdout retained as well."""
    def __init__(self, binary, label, directory, timeout):
        super().__init__(binary, label, directory, timeout)
        self.stdout_log = (directory / (label + '.stdout.log')).open('ab')

    def request(self, text):
        if self.process.poll() is not None:
            raise RuntimeError(f'process already exited: {self.process.returncode}')
        deadline = time.monotonic() + self.timeout
        payload = memoryview(text.encode())
        sent = 0
        self.selector.register(self.process.stdin, selectors.EVENT_WRITE)
        try:
            while time.monotonic() < deadline:
                if sent == len(payload):
                    while b'\n' in self.buffer:
                        line, self.buffer = self.buffer.split(b'\n', 1)
                        if line.startswith(b'RESULT '):
                            return json.loads(line[7:])
                events = self.selector.select(max(0.0, deadline-time.monotonic()))
                if not events:
                    break
                for key, _ in events:
                    if key.fileobj is self.process.stdin:
                        try:
                            sent += os.write(self.process.stdin.fileno(), payload[sent:])
                        except BlockingIOError:
                            continue
                        if sent == len(payload):
                            self.selector.unregister(self.process.stdin)
                    else:
                        try:
                            chunk = os.read(self.process.stdout.fileno(), 65536)
                        except BlockingIOError:
                            continue
                        if not chunk:
                            raise RuntimeError(f'process exited without RESULT: {self.process.poll()}')
                        self.stdout_log.write(chunk)
                        self.stdout_log.flush()
                        self.buffer += chunk
            self.process.kill()
            self.process.wait()
            raise TimeoutError('request timeout; observation retained')
        finally:
            try:
                self.selector.unregister(self.process.stdin)
            except KeyError:
                pass

    def close(self):
        super().close()
        self.stdout_log.close()


def represented(value):
    exact = F(value)
    number = float(exact)
    if not math.isfinite(number) or F(number) != exact:
        raise ValueError('fixture value is not exactly representable by binary64')
    return format(number, '.17g')


def candidates(case):
    n, rank = case['driver_request']['n'], case['driver_request']['rank']
    modes = (1,) if (n, rank) == (5, 6) else (1, 2)
    thresholds = (6, 7) if n == 6 else (6,)
    permutations = (0, 1) if n >= 5 else (0,)
    return [{'id': f'mode{mode}-ten{threshold}-perm{permutation}',
             'mode': mode, 'direct_tensor_threshold': threshold,
             'argument_permutation': permutation,
             'requested_accuracy': '1e-6' if n >= 5 else '1e-10',
             'critical_accuracy': '1e-3'}
            for mode in modes for threshold in thresholds for permutation in permutations]


def request(case, option, *, check=False, repeats=1, iterations=1, warmup=0):
    req = case['driver_request']
    if (case['table'] != 'ordinary' or req['dimension_shift'] != 0
            or req['powers'] != [1]*req['n'] or len(req['samples']) != 1):
        raise ValueError('only exact ordinary singleton fixtures admitted')
    sample = req['samples'][0]
    lines = [f'{"CHECK" if check else "BENCH"} {case["id"]} '
             f'{option["mode"]} {req["n"]} {req["rank"]} {represented(sample["mu"])} '
             f'1 {warmup} {repeats} {iterations} {option["requested_accuracy"]} '
             f'{option["critical_accuracy"]} {option["direct_tensor_threshold"]} '
             f'{option["argument_permutation"]}']
    for shift, mass in zip(sample['shifts'], sample['masses_squared']):
        lines.append(' '.join(represented(value) for value in shift)
                     + f' ({represented(mass[0])},{represented(mass[1])})')
    if len(lines) != req['n']+1:
        raise ValueError('propagator count differs')
    return '\n'.join(lines)+'\n'


def degrees(rank):
    return [r for r in range(rank+1) for t in range(r, -1, -1)
            for x in range(r-t, -1, -1) for y in range(r-t-x, -1, -1)]


def decoded_reference(case):
    path = ORIGINAL/'cases'/case['id']/'result.json'
    original_inputs = json.loads((ROOT/ORIGINAL/'inputs.json').read_text())
    original_case = next(item for item in original_inputs['cases'] if item['id'] == case['id'])
    # Precision/requested accuracy may change; mathematical inputs may not.
    for key in ('n', 'rank', 'powers', 'dimension_shift', 'samples'):
        if original_case['driver_request'][key] != case['driver_request'][key]:
            raise ValueError(f'old independently qualified mathematical fixture differs: {key}')
    value = json.loads((ROOT/path).read_text())
    lane = value['first_output']['lanes'][0]
    if value['status'] != 'measured' or lane['status'] != 'Success':
        raise ValueError('saved reference is not successful')
    values = lane['values']
    expected = [[tuple(F(component['exact_rational']) for component in values[4*moment+slot])
                 for slot in range(4)]
                for moment in range(math.comb(case['driver_request']['rank']+4, 4))]
    return expected, path


def inspect_array(moments, expected, case):
    req = case['driver_request']
    if not isinstance(moments, list) or len(moments) != len(expected):
        return {'complete': False, 'finite': False, 'error': 'incomplete cumulative tensor'}
    scale = F(req['samples'][0]['mu'])
    maximum_scaled_error_squared, maximum_scaled_reference_squared, mixed = F(0), F(0), F(0)
    nonfinite, finite, fields, failed_1e6, failed_1e3 = 0, 0, 0, 0, 0
    for degree, actual, reference in zip(degrees(req['rank']), moments, expected):
        if not isinstance(actual, list) or len(actual) != 4:
            return {'complete': False, 'finite': False, 'error': 'missing Laurent slots'}
        scale_squared = scale**(2*(degree+4-2*req['n']))
        for number, answer in zip(actual, reference):
            fields += 1
            reference_squared = sum(value*value for value in answer)
            maximum_scaled_reference_squared = max(maximum_scaled_reference_squared,
                                                   reference_squared/scale_squared)
            if (not isinstance(number, list) or len(number) != 2
                    or any(type(value) not in (int, float) or not math.isfinite(value) for value in number)):
                nonfinite += 1
                continue
            finite += 1
            z = tuple(F(value) for value in number)
            difference_squared = sum((value-answer_component)**2 for value, answer_component in zip(z, answer))
            maximum_scaled_error_squared = max(maximum_scaled_error_squared, difference_squared/scale_squared)
            entry_mixed = difference_squared/max(scale_squared, reference_squared)
            mixed = max(mixed, entry_mixed)
            failed_1e6 += entry_mixed > F(1, 10**12)
            failed_1e3 += entry_mixed > F(1, 10**6)
    relative_squared = (maximum_scaled_error_squared/maximum_scaled_reference_squared
                        if maximum_scaled_reference_squared else
                        F(0) if not maximum_scaled_error_squared else None)
    relative = math.sqrt(float(relative_squared)) if relative_squared is not None else None
    return {'complete': True, 'finite': nonfinite == 0, 'complex_fields': fields,
            'finite_complex_fields': finite, 'nonfinite_complex_fields': nonfinite,
            'array_relative_error': relative,
            'array_relative_error_squared_exact': str(relative_squared) if relative_squared is not None else None,
            'scaled_absolute_error': math.sqrt(float(maximum_scaled_error_squared)),
            'scaled_reference_norm': math.sqrt(float(maximum_scaled_reference_squared)),
            'maximum_coefficient_mixed_normalized_error': math.sqrt(float(mixed)),
            'maximum_coefficient_mixed_squared_exact': str(mixed),
            'failed_mixed_fields_at_1e6': failed_1e6, 'failed_mixed_fields_at_1e3': failed_1e3,
            'within_three_digits': nonfinite == 0 and relative is not None and relative <= 1e-3,
            'within_requested_1e6': nonfinite == 0 and relative is not None and relative <= 1e-6}


def assess(response, case, option, expected, repeats, cache):
    req = case['driver_request']
    errors = []
    iface = {1: 'Aten_cll', 2: 'Bten_cll', 3: 'Cten_cll', 4: 'Dten_cll'}.get(req['n'], 'TNten_cll')
    for key, value in {'id': case['id'], 'collier_mode': option['mode'],
                       'direct_tensor_threshold': option['direct_tensor_threshold'],
                       'argument_permutation': option['argument_permutation'],
                       'requested_accuracy': float(option['requested_accuracy']),
                       'critical_accuracy': float(option['critical_accuracy']),
                       'initialization_topology_capacity': max(req['n'], 2),
                       'initialization_rank_capacity': max(req['rank'], 1, req['n']-max(req['n']-2, 4)),
                       'interface': iface}.items():
        if response.get(key) != value:
            errors.append(f'unexpected {key}: {response.get(key)!r}')
    times = response.get('total_ns')
    if (not isinstance(times, list) or len(times) != repeats
            or any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0 for value in times)):
        errors.append('invalid raw timing blocks')
    if type(response.get('clock_ticks_per_second')) is not int or response['clock_ticks_per_second'] <= 0:
        errors.append('invalid monotonic clock')
    arrays, native = [], []
    lanes = response.get('lanes', [])
    if len(lanes) != 1:
        errors.append('missing singleton result lane')
    else:
        lane = lanes[0]
        arrays.append(lane.get('moments') or lane.get('diagnostic_moments'))
        native.append({key: lane.get(key) for key in ('status', 'last_err_flag', 'last_acc_flag',
                                                     'worst_err_flag', 'worst_acc_flag', 'maximum_rank_error_estimates')})
    blocks = response.get('blocks', [])
    if len(blocks) != repeats:
        errors.append('missing block snapshots')
    for block in blocks:
        block_lanes = block.get('lanes', [])
        if len(block_lanes) != 1:
            errors.append('missing singleton block lane')
            continue
        lane = block_lanes[0]
        arrays.append(lane.get('moments'))
        native.append({key: lane.get(key) for key in ('cumulative_stable', 'last_err_flag', 'last_acc_flag',
                                                     'cumulative_maximum_rank_error_estimates')})
    comparisons = []
    hashes = []
    for array in arrays:
        body = json.dumps(array, separators=(',', ':'), allow_nan=False)
        array_hash = hashlib.sha256(body.encode()).hexdigest()
        hashes.append(array_hash)
        if array_hash not in cache:
            cache[array_hash] = inspect_array(array, expected, case)
        comparisons.append(cache[array_hash])
    complete = not errors and bool(comparisons) and all(value.get('complete') for value in comparisons)
    finite = complete and all(value.get('finite') for value in comparisons)
    within = finite and all(value.get('within_three_digits') for value in comparisons)
    return {'protocol_valid': not errors, 'errors': errors, 'arrays': comparisons,
            'array_hashes': hashes, 'array_values_identical_within_response': len(set(hashes)) == 1,
            'complete': complete, 'finite': finite, 'within_three_digits': within,
            'native_diagnostics': native, 'native_flags_are_not_accuracy_rejection': True,
            'pole_check_errors': response.get('pole_check_errors')}


def describe(values):
    deviation = statistics.stdev(values)
    error = deviation/math.sqrt(len(values))
    return {'raw_block_means': values, 'mean': statistics.mean(values),
            'median': statistics.median(values), 'stddev': deviation, 'standard_error': error,
            'confidence_95_half_width_student_t': 2.228138852*error,
            'minimum': min(values), 'maximum': max(values)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--binary-sha256', required=True)
    parser.add_argument('--inputs', type=Path, default=Path('validation/benchmark/opening-double-20261026/inputs.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cpu', type=int, required=True)
    parser.add_argument('--quiet-note', required=True)
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--cohort-timeout', type=float, default=600)
    args = parser.parse_args()
    if not (ROOT/'Cargo.toml').is_file() or args.cpu not in os.sched_getaffinity(0):
        parser.error('run from repository root using an allowed CPU')
    if (not math.isfinite(args.timeout) or not math.isfinite(args.cohort_timeout)
            or args.timeout <= 0 or args.cohort_timeout <= 0 or not args.quiet_note.strip()):
        parser.error('positive bounded timeouts and explicit quiet-window note required')
    binary, output = args.binary.resolve(), args.output.resolve()
    if digest(binary) != args.binary_sha256:
        parser.error('binary hash differs')
    if not output.is_relative_to(ROOT/'target') or output.exists():
        parser.error('output must be a new target directory')
    output.mkdir(parents=True)
    os.sched_setaffinity(0, {args.cpu})
    source_paths = [args.inputs, KERNEL, HERE/'driver.f90', HERE/'run.py', HERE/'README.md', ORIGINAL/'inputs.json']
    sources = {str(path): digest(ROOT/path) for path in source_paths}
    suite = json.loads((ROOT/args.inputs).read_text())
    cases = [case for case in suite['cases'] if case['table'] == 'ordinary']
    if len(cases) != 12 or sum(len(candidates(case)) for case in cases) != 32:
        raise ValueError('fixed twelve ordinary rows /32 public-option candidates required')
    data = {'schema_version': 1, 'kind': 'opening-double-collier-public-option-sweep', 'status': 'running',
            'started_utc': datetime.now(timezone.utc).isoformat(), 'cpu': args.cpu,
            'quiet_note': args.quiet_note,
            'binary': {'path': str(binary.relative_to(ROOT)), 'sha256': digest(binary)},
            'input_sources': sources, 'numeric_type': 'binary64', 'working_bits': 53, 'sample_lanes': 1,
            'repeats': 11, 'warmup': 3, 'target_block_ns': 30000000, 'maximum_iterations': 1000000,
            'selection': 'Fastest measured mean among predeclared public options with complete finite tensors and whole-array relative error<=1e-3; otherwise fastest observed diagnostic duration with explicit warning. Native flags alone do not reject.',
            'accuracy': 'N5R5/N5R6/N6R6 requested1e-6; other9 requested1e-10; critical1e-3 all. Whole-array relative error E/A with E=max_j|computed-reference|/mu^(degree+4-2N), A=max_j|reference|/same_scale. All cumulative moments and four Laurent slots.',
            'timer_scope': 'Per-root InitEvent, routing/invariants, public tensor call including scalar masters, normalization and Cartesian gathering; excludes initialization/warmup/diagnostic and finite scans/pole probes/block snapshots/I/O. Public argument permutation disables even local cache use; ordinary candidates use local-only memoization.',
            'ratio_campaign': False, 'rows': []}
    save(output/'results.json', data)
    deadline = time.monotonic()+args.cohort_timeout
    for case in cases:
        directory = output/case['id']
        directory.mkdir()
        row = {'id': case['id'], 'n': case['driver_request']['n'], 'rank': case['driver_request']['rank'],
               'status': 'running', 'input': case, 'candidates': [], 'selected_candidate': None}
        data['rows'].append(row)
        expected, reference_path = decoded_reference(case)
        row['reference_array'] = {'path': str(reference_path), 'sha256': digest(ROOT/reference_path)}
        comparison_cache = {}
        for option in candidates(case):
            candidate_directory = directory/option['id']
            candidate_directory.mkdir()
            candidate = {'configuration': option, 'status': 'running', 'captures': {}}
            row['candidates'].append(candidate)
            process = None
            try:
                if time.monotonic() >= deadline:
                    raise TimeoutError('fixed campaign deadline exhausted')
                process = CaptureProcess(binary, 'collier', candidate_directory, min(args.timeout, deadline-time.monotonic()))
                def capture(label, **settings):
                    remaining = deadline-time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError('fixed campaign deadline exhausted')
                    process.timeout = min(args.timeout, remaining)
                    wire = request(case, option, **settings)
                    (candidate_directory/(label+'.request.txt')).write_text(wire)
                    started = time.monotonic()
                    response = process.request(wire)
                    save(candidate_directory/(label+'.response.json'), response)
                    assessment = assess(response, case, option, expected, settings.get('repeats', 1), comparison_cache)
                    save(candidate_directory/(label+'.assessment.json'), assessment)
                    candidate['captures'][label] = {'wall_seconds_including_transport_and_assessment': time.monotonic()-started,
                        'response': str((candidate_directory/(label+'.response.json')).relative_to(ROOT)),
                        'response_sha256': digest(candidate_directory/(label+'.response.json')), 'assessment': assessment}
                    save(output/'results.json', data)
                    return response, assessment
                capture('preflight', check=True)
                pilot, _ = capture('pilot', warmup=3)
                iterations = max(1, min(1000000, math.ceil(30000000/pilot['total_ns'][0])))
                candidate['iterations_per_block'] = iterations
                timed, _ = capture('timed', warmup=3, repeats=11, iterations=iterations)
                capture('postflight', check=True)
                candidate['timing_ns'] = describe(timed['total_ns'])
                candidate['timing_us'] = {key: value/1000 for key, value in candidate['timing_ns'].items()
                                          if key != 'raw_block_means'}
                assessments = [value['assessment'] for value in candidate['captures'].values()]
                candidate['protocol_valid'] = all(value['protocol_valid'] for value in assessments)
                candidate['complete'] = all(value['complete'] for value in assessments)
                candidate['finite'] = all(value['finite'] for value in assessments)
                candidate['within_three_digits'] = all(value['within_three_digits'] for value in assessments)
                arrays = [array for assessment in assessments for array in assessment['arrays']]
                relative = [array['array_relative_error'] for array in arrays if array.get('array_relative_error') is not None]
                mixed = [array['maximum_coefficient_mixed_normalized_error'] for array in arrays
                         if array.get('maximum_coefficient_mixed_normalized_error') is not None]
                candidate['maximum_array_relative_error_over_finite_fields'] = max(relative) if relative else None
                candidate['maximum_coefficient_mixed_normalized_error_over_finite_fields'] = max(mixed) if mixed else None
                candidate['nonfinite_complex_fields'] = max((array.get('nonfinite_complex_fields', 0) for array in arrays), default=0)
                candidate['array_values_identical_across_all_snapshots'] = len({array_hash for assessment in assessments
                                                                               for array_hash in assessment['array_hashes']}) == 1
                candidate['status'] = 'measured' if candidate['within_three_digits'] else 'measured_with_accuracy_warning'
            except Exception as error:
                candidate.update(status='timeout' if isinstance(error, TimeoutError) else 'failed', error=str(error))
            finally:
                if process is not None:
                    process.close()
                    candidate['native_returncode'] = process.process.returncode
                candidate['binary_unchanged_after'] = digest(binary) == args.binary_sha256
                candidate['reference_array_unchanged_after'] = digest(ROOT/reference_path) == row['reference_array']['sha256']
                if (candidate.get('native_returncode') != 0 or not candidate['binary_unchanged_after']
                        or not candidate['reference_array_unchanged_after']):
                    candidate['protocol_valid'] = False
                    candidate['within_three_digits'] = False
                save(output/'results.json', data)
            print(json.dumps({'id': case['id'], 'candidate': option['id'], 'status': candidate['status'],
                              'mean_us': candidate.get('timing_us', {}).get('mean'),
                              'relative_error': candidate.get('maximum_array_relative_error_over_finite_fields'),
                              'nonfinite': candidate.get('nonfinite_complex_fields')}), flush=True)
        observed = [candidate for candidate in row['candidates'] if candidate.get('protocol_valid') and 'timing_us' in candidate]
        accurate = [candidate for candidate in observed if candidate.get('within_three_digits')]
        choice = min(accurate or observed, key=lambda candidate: candidate['timing_us']['mean']) if observed else None
        if choice:
            row['selected_candidate'] = choice['configuration']['id']
            row['selection_pool'] = 'finite_and_at_least_three_digits' if accurate else 'observed_diagnostic_only'
            row['timing_us'] = choice['timing_us']
            row['array_relative_error'] = choice['maximum_array_relative_error_over_finite_fields']
            row['nonfinite_complex_fields'] = choice['nonfinite_complex_fields']
            row['within_three_digits'] = choice['within_three_digits']
            row['status'] = 'measured' if accurate else 'measured_with_accuracy_warning'
        else:
            row['status'] = 'no_timing_observation'
        save(output/'results.json', data)
    data['sources_unchanged_after'] = all(digest(ROOT/path) == expected for path, expected in sources.items())
    data['binary_unchanged_after'] = digest(binary) == args.binary_sha256
    data['completed_utc'] = datetime.now(timezone.utc).isoformat()
    data['status'] = ('completed' if data['sources_unchanged_after'] and data['binary_unchanged_after']
                      and all(row['selected_candidate'] for row in data['rows']) else 'retained_protocol_failure')
    save(output/'results.json', data)
    return 0 if data['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent saved-record audit. Never imports the producer or runs Rust code."""
from __future__ import annotations
import collections
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT / 'target/guard-performance-review/optimized-performance-proposal'
RUN = BASE / 'fresh-captured-runtime'
HERE = Path(__file__).resolve().parent
RESULT = RUN / 'qualification-001/results.json'
RAW = RUN / 'qualification-001/responses.jsonl'
PROTO = RUN / 'protocol.json'
SHAPES = RUN / 'control-shapes.json'
PIN = '2c1f3342e189a20fef3bbf7dd9e0baa372e2b4a2'
ARITY = {'A0': 2, 'B0': 4, 'C0': 7, 'dB0': 4, 'D0': 11}
ORDER = ['finite', 'total_single', 'ir_double', 'uv_single', 'ir_single', 'derivative_discriminant']
checks = 0

def require(value, message):
    global checks
    checks += 1
    if not value:
        raise AssertionError(message)

def same(actual, expected, message):
    require(actual == expected, message)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while data := f.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

def number(value, bits=53, finite=True):
    if not finite:
        return {'finite': False, 'rational': None, 'precision': bits, 'negative_sign': False}
    q = Fraction(value)
    return {'finite': True, 'rational': str(q), 'precision': bits,
            'negative_sign': q < 0 or (isinstance(value, float) and math.copysign(1., value) < 0)}

def z(re=0, im=0, bits=53):
    return [number(re, bits), number(im, bits)]

def real(values, bits=53):
    return [z(x, bits=bits) for x in values]

def represented(value, finite_flag=False):
    require(isinstance(value, dict), 'represented scalar must be object')
    same(set(value), {'precision', 'negative_sign', 'rational'} | ({'finite'} if finite_flag else set()), 'represented scalar fields')
    require(type(value['precision']) is int and value['precision'] > 0, 'positive precision')
    require(type(value['negative_sign']) is bool, 'boolean sign')
    if finite_flag:
        require(type(value['finite']) is bool, 'boolean finite flag')
    if value.get('finite', True):
        require(isinstance(value['rational'], str), 'finite exact rational text')
        q = Fraction(value['rational'])
        same(str(q), value['rational'], 'canonical rational')
        if q:
            same(value['negative_sign'], q < 0, 'nonzero sign matches exact rational')
    else:
        same(value['rational'], None, 'nonfinite input has no successful rational')

def complexes(values, finite_flag=False):
    require(isinstance(values, list), 'complex sequence')
    for value in values:
        require(isinstance(value, list) and len(value) == 2, 'complex real/imag pair')
        for part in value:
            represented(part, finite_flag)

def fixture_specs():
    """Reconstruct the frozen Rust constants, layout, lane order and errors."""
    specs = []
    def add(group, family, label, case, inputs, errors, components=1, shape=None):
        specs.append(dict(group=group, family=family, label=label, case=case,
                          inputs=inputs, errors=errors, components=components, shape=shape))
    good = {'A0': real([2, 1]), 'B0': real([-3, 2, 5, 1]), 'C0': real([-1, -5, -4, 2, 3, 5, 1])}
    zeros = {}
    for family, point in good.items():
        zero = real([0] * (ARITY[family] - 1) + [1]); zeros[family] = zero
        for i, rows in enumerate([0, 1, 5, 3, 0, 1]):
            inp = json.loads(json.dumps(point * rows)); errs = [None] * rows
            if rows > 1:
                inp[2 * ARITY[family] - 1] = z(-1); errs[1] = 'InvalidScale'
            add('selected_families', family, None, f'reuse_step_{i}_rows_{rows}', inp, errs)
        add('selected_families', family, None, 'scaleless', zero * 3, [None] * 3)
        bad = point[:-1] + [z(-1)]
        add('selected_families', family, None, 'all_invalid_then_recover', bad * 3, ['InvalidScale'] * 3)
        add('selected_families', family, None, 'recovery', point, [None])
        bad = json.loads(json.dumps(point)); bad[0][0] = number(0, finite=False)
        add('selected_families', family, None, 'nonfinite_neighbor', point + bad + point,
            [None, 'NonFiniteInput { argument: 0, component: 0 }', None])
        if family == 'A0':
            physical = [z(100, -1.4), z(1)] + point + zero
            rows = 3
        elif family == 'B0':
            physical = real([3, 0, 0, 1]) + [z(3), z(.7, -.03), z(1.4, -.08), z(1)] + real([0, 2, 2, 1]) + real([7, 0, 0, 1]) + zero
            rows = 5
        else:
            physical = real([1, 2, 3, 5, 7, 11, 1]) + real([-1, -2, 30, 2, 3, 5, 1])
            physical += real([1, 2, 3]) + [z(.5, -.1), z(.7, -.1), z(1.4, -.1), z(1)]
            physical += real([-1, -2, 30]) + [z(2, -.1), z(3, -.1), z(5, -.1), z(1)] + zero
            rows = 5
        add('selected_families', family, None, 'physical_complex_mixed_branches', physical, [None] * rows)
        if family == 'B0':
            ci = json.loads(json.dumps(point)); ci[0] = z(-3, 1)
            upper = json.loads(json.dumps(point)); upper[1] = z(2, 1)
            scale = json.loads(json.dumps(point)); scale[3] = z(1, 1)
            add('selected_families', family, None, 'diagnostic_neighbors', point + ci + upper + scale + point,
                [None, 'ComplexInvariant { argument: 0 }', 'UpperHalfPlaneMass { argument: 1 }', 'InvalidScale', None])
    for family, vals in [('dB0', [-3, 2, 5, 1]), ('D0', [-1, -2, -3, -4, -5, -6, 2, 3, 4, 5, 1])]:
        point = real(vals); bad = point[:-1] + [z(-1)]
        for label, inp, errs in [('empty', [], []), ('singleton', point, [None]), ('invalid_neighbor', point + bad + point, [None, 'InvalidScale', None])]:
            add('unchanged_paths', family, 'unselected_family', label, inp, errs)
        if family == 'dB0':
            add('unchanged_paths', family, 'unselected_family', 'scaleless_error', real([0, 0, 0, 1]), ['UndefinedScalelessDerivative'])
    add('unchanged_paths', 'A0', 'primal_only_Dual_shape', 'singleton', real([2, 1]), [None], 1, [[0]])
    for family, point in good.items():
        seeded = [v for i, value in enumerate(point) for v in [value, z(1 if i == 0 else 0)]]
        constant = [v for value in point for v in [value, z(0)]]
        label = f'{family}_seeded_and_constant_Dual'
        for case, inp, errs in [('seeded_three', seeded * 3, [None] * 3), ('constant_kinematics', constant * 3, [None] * 3), ('empty_reuse', [], []), ('seeded_recovery', seeded, [None])]:
            add('unchanged_paths', family, label, case, inp, errs, 2, [[0], [1]])
        if family == 'C0':
            imaginary = json.loads(json.dumps(seeded)); imaginary[1] = z(0, 1)
            width = json.loads(json.dumps(seeded)); width[7] = z(0, 1)
            gram = json.loads(json.dumps(seeded)); gram[2] = z(-4); gram[4] = z(-9)
            add('unchanged_paths', family, label, 'invalid_derivative_neighbors', seeded + imaginary + width + gram + seeded,
                [None, 'UnsupportedDerivativeDomain', 'UnsupportedDerivativeDomain', 'UnsupportedDerivativeDomain', None], 2, [[0], [1]])
    point = [z(Fraction(1) + Fraction(1, 2**80), bits=106), z(1, bits=106)]
    for case, inp, rows in [('three_lanes', point * 3, 3), ('empty_reuse', [], 0), ('singleton_recovery', point, 1)]:
        add('extended_unchanged_paths', 'A0', 'DoubleFloat_beyond53', case, inp, [None] * rows)
    add('extended_unchanged_paths', 'A0', 'Float53_is_not_f64', 'singleton', real([2, 1]), [None])
    for proto in [128, 256]:
        for bits_list in [[128, 256, 64], [256], [], [64, 128, 256]]:
            inp = []
            for bits in bits_list:
                inp += [[number(Fraction(1) + Fraction(1, 2**(bits - 10)), bits), number(0, 128)], [number(1, 128), number(0, 64)]]
            add('extended_unchanged_paths', 'A0', f'Float_mixed_prototype{proto}', f'lane_precisions_{bits_list}', inp, [None] * len(bits_list))
    return specs

def snapshot(snap, spec):
    rows = len(spec['errors']); components = spec['components']
    same(set(snap), {'rows', 'components', 'lanes'}, 'direct snapshot fields')
    same(snap['rows'], rows, 'direct rows'); same(snap['components'], components, 'direct components')
    same(len(snap['lanes']), rows, 'direct lane count')
    count = 0
    for i, lane in enumerate(snap['lanes']):
        same(set(lane), {'error', 'six_outputs'}, 'direct lane fields')
        same(lane['error'], spec['errors'][i], 'independent direct expected lane error')
        if lane['error'] is not None:
            same(lane['six_outputs'], None, 'failed lane outputs null, never zero success')
        else:
            same(len(lane['six_outputs']), 6 * components, 'all six slots and all derivative components')
            complexes(lane['six_outputs']); count += 6 * components
    return count

def core_input(bits, dual, beyond53=False):
    row = [0, 0, 0, 0, 0, 1, 0, 0, 2, 3, 1]
    result = []
    for i, x in enumerate(row):
        if i == 8 and beyond53:
            x = Fraction(18014398509481985, 9007199254740992)
        result.append(z(x, bits=bits))
        if dual:
            result.append(z(1 if i == 8 else 0, bits=bits))
    return result

EXECUTION = {'analytic_rows': 0, 'argument_rows': 1, 'fallback_rows': 0, 'fallback_successes': 0,
             'input_rows': 1, 'master_family_batches': 2, 'master_rows': 3, 'pentagon_box_rows': 0, 'reduction_rows': 1}

def capture_checks(captures, inputs, components):
    same(len(captures), 2, 'B0+A0 master family batches')
    args = [inputs[i:i + components] for i in range(0, len(inputs), components)]
    precision = inputs[0][0]['precision']
    minus_one = [z(-1, bits=precision)] + ([z(0, bits=precision)] if components == 2 else [])
    wanted = [minus_one + args[8] + args[9] + args[10], args[9] + args[10] + args[8] + args[10]]
    total = 0
    for i, cap in enumerate(captures):
        same(cap['backend'], 'SymbolicaBatch', 'observed backend')
        same(cap['family'], ['B0', 'A0'][i], 'observed master family order')
        same(cap['components'], components, 'observed derivative component count')
        same(cap['rows'], [1, 2][i], 'observed master rows')
        same(cap['input'], wanted[i], 'independently reconstructed master inputs')
        complexes(cap['input'], True)
        same(cap['output_order'], ORDER, 'finite/total/IR2/UV/IR/discriminant slots')
        same(cap['errors'], [None] * cap['rows'], 'all core master lanes succeed')
        same(cap['whole_batch_error'], None, 'no hidden batch failure')
        same(cap['valid_lanes'], [0], 'parent lane map')
        same(cap['requests'], [[[0, 0]], [[1, 0], [2, 0]]][i], 'master request node mapping')
        same(len(cap['output']), cap['rows'], 'master output rows')
        for out in cap['output']:
            same(len(out), 6 * components, 'all captured master slots/components')
            complexes(out, True); total += len(out)
    return total

def core_result(result, inputs, components, cache=False):
    same(result['execution'], EXECUTION, 'core exact execution counters')
    same(result['diagnostics'], [[]], 'core exact diagnostics')
    if cache:
        same(result['stable'], True, 'cache stable')
        same(len(result['lanes']), 1, 'cache lane count')
        lane = result['lanes'][0]
        same(lane['status'], 'success', 'cache status')
        same(lane['fallback_used'], False, 'cache no fallback')
        same(lane['analytic_used'], False, 'cache no analytic')
        values = lane['represented']
        if components == 1:
            same(len(lane['moments']), 5, 'five scalar+rank1 moments')
            for i, moment in enumerate(lane['moments']):
                same(len(moment), 4, 'native Laurent tensor slots')
                for j, pair in enumerate(moment):
                    for k, v in enumerate(pair):
                        rep = values[i * 4 + j][k]
                        same(Fraction(v), Fraction(rep['rational']), 'raw tensor f64 equals exact representation')
                        same(math.copysign(1., v) < 0, rep['negative_sign'], 'raw signedzero preserved')
    else:
        same(result['statuses'], '[Success]', 'core status')
        same(result['fallback_used'], [False], 'core no fallback')
        same(result['analytic_used'], [False], 'core no analytic')
        values = result['values']
    same(len(values), 20 * components, 'complete five moments, four Laurent, each component')
    complexes(values, True)
    return 20 * components, capture_checks(result['master_captures'], inputs, components)

def main():
    result = load(RESULT); proto = load(PROTO); shapes = load(SHAPES)
    same(sha(RESULT), '0450b25c2a806c81f4410f567b370612f82401d9a322cb2f87d4115f53770232', 'frozen producer receipt')
    same(sha(PROTO), 'bddd62ae70fbb81200e263ba96ae0185177b090608f7abb0b440e1744bf75b4b', 'frozen protocol')
    same(proto['pinned_source_revision'], PIN, 'pinned source/version context')
    same(sha(RAW), result['raw_sha256'], 'raw saved120event hash')
    same(sha(SHAPES), proto['control_shapes_sha256'], 'shape-only input hash')
    guards = {Path(k): v for k, v in result['input_sha256'].items()}
    for p in [RESULT, RAW, PROTO, SHAPES, Path(__file__).resolve()]:
        guards[p] = sha(p)
    before = {str(k): sha(k) for k in guards}
    for k, expected in guards.items(): same(before[str(k)], expected, 'protected input before ' + str(k))
    events = [json.loads(line) for line in RAW.read_text().splitlines()]
    same(len(events), 120, 'full saved event count')
    requests = {e['serial']: e for e in events if e['event'] == 'request'}
    responses = {e['serial']: e for e in events if e['event'] == 'response'}
    same(set(requests), set(range(1, 61)), 'request serial completeness')
    same(set(responses), set(requests), 'response serial completeness')
    controls = []
    for serial in [33, 34, 35, 36]:
        req = requests[serial]; resp = responses[serial]
        for key in ['serial', 'stage', 'key', 'engine', 'payload']:
            same(resp[key], req[key], 'paired CONTROL envelope ' + key)
        same(req['payload'], 'CONTROLS\n', 'literal control request')
        same(req['engine'], 'baseline' if serial % 2 else 'candidate', 'CONTROL engine sequence')
        same(req['stage'], 'controls' if serial < 35 else 'controls-repeat', 'CONTROL stage sequence')
        controls.append(resp['response'])
    for control in controls[1:]: same(control, controls[0], 'full cross/own CONTROL record exact including precision/sign/errors/counters')
    control = controls[0]
    same(control['status'], 'passed', 'control successful envelope')
    same(control['id'], 'controls', 'control identifier')
    same(control['backend'], 'SymbolicaBatch', 'control backend')
    specs = fixture_specs()
    same(len(specs), 67, 'independent direct fixture inventory')
    specmap = {(s['group'], s['family'], s['label'], s['case']): s for s in specs}
    shape_keys = set()
    for group in ['selected_families', 'unchanged_paths', 'extended_unchanged_paths']:
        for family in shapes[group]:
            for case in family['cases']:
                label = None if group == 'selected_families' else family['label']
                key = (group, family['family'], label, case['label'])
                require(key not in shape_keys, 'unique shape-only fixture key')
                shape_keys.add(key); spec = specmap[key]
                same(case['input_metadata'], spec['inputs'], 'shape-only exact input independently reconstructed')
                same(case['rows'], len(spec['errors']), 'shape-only row count')
                same(case['components'], spec['components'], 'shape-only component count')
                same(case['errors'], spec['errors'], 'shape-only errors independently reconstructed')
    same(shape_keys, set(specmap), 'shape-only complete fixture census')
    found = set(); per_case = []; complex_count = 0; errors = collections.Counter()
    for group in ['selected_families', 'unchanged_paths', 'extended_unchanged_paths']:
        for family in control['masters'][group]:
            for case in family['cases']:
                label = None if group == 'selected_families' else family['label']
                key = (group, family['family'], label, case['label'])
                require(key not in found, 'unique direct fixture key'); found.add(key)
                spec = specmap[key]
                same(case['input_metadata'], spec['inputs'], 'independently reconstructed direct exact input: ' + str(key))
                complexes(case['input_metadata'], True)
                same(len(case['input_metadata']), len(spec['errors']) * ARITY[spec['family']] * spec['components'], 'direct input lane/arg/component layout')
                for field in ['own_repeated_outputs_exact', 'input_unchanged']: same(case[field], True, field)
                same(case['status'], 'passed', 'direct case status')
                same(case['baseline'], case['candidate'], 'within-process direct instances full equality')
                count = snapshot(case['baseline'], spec)
                snapshot(case['candidate'], spec)
                if 'represented_outputs' in case: same(case['represented_outputs'], case['baseline'], 'all represented outputs retained')
                if group == 'selected_families':
                    same(case['family'], family['family'], 'selected family')
                    same(case['baseline_backend'], 'SymbolicaBatch', 'direct baseline backend')
                    same(case['candidate_backend'], 'SymbolicaBatch', 'direct candidate backend')
                    for lane in case['baseline']['lanes']:
                        if lane['error'] is None:
                            for part in lane['six_outputs'][5]: same(Fraction(part['rational']), 0, 'ordinary derivative discriminant zero')
                    if case['label'] == 'scaleless':
                        expected_uv = 1 if family['family'] == 'B0' else 0
                        for lane in case['baseline']['lanes']:
                            wanted = [0, 0, 0, expected_uv, -expected_uv, 0]
                            for i, value in enumerate(lane['six_outputs']):
                                same(Fraction(value[0]['rational']), wanted[i], 'scaleless UV/IR cancellation independent identity')
                                same(Fraction(value[1]['rational']), 0, 'scaleless imaginary zero')
                else:
                    same(family['shape'], spec['shape'], 'direct exact Dual shape')
                    same(family['components'], spec['components'], 'direct components')
                    same(family['backend'], 'SymbolicaBatch', 'unchanged generic backend')
                if group == 'extended_unchanged_paths' and label != 'Float53_is_not_f64':
                    for i, lane in enumerate(case['baseline']['lanes']):
                        out = lane['six_outputs'][3]
                        inp = case['input_metadata'][i * 2]
                        same(out, [{k: v for k, v in p.items() if k != 'finite'} for p in inp], 'A0 UV preserves exact mass and per-component precision')
                complex_count += count
                for error in spec['errors']:
                    if error is not None: errors[error] += 1
                per_case.append({'group': group, 'family': spec['family'], 'label': label, 'case': spec['case'],
                                 'rows': len(spec['errors']), 'components': spec['components'], 'expected_errors': spec['errors'], 'complex_outputs': count})
    same(found, set(specmap), 'all direct fixtures, no omission or extra')
    same(complex_count, 774, 'direct successful allslot complex count')
    same(sum(len(s['errors']) for s in specs), 133, 'direct row count')
    same(sum(errors.values()), 27, 'direct expected errors')
    core_counts = []
    for record, (label, bits, dual, beyond) in zip(control['core'] + control['extended_core'],
        [('f64 Dual N2r1', 53, True, False), ('DoubleFloat N2r1 beyond53', 106, False, True), ('Float256 N2r1 beyond53', 256, False, True)], strict=True):
        inp = core_input(bits, dual, beyond)
        same(record['label'], label, 'frozen core numeric-type fixture')
        same(record['input'], inp, 'independently reconstructed core exact input')
        same(record['components'], 2 if dual else 1, 'core derivative components')
        same(record['input_unchanged'], True, 'core input preservation')
        same(record['own_repeated_outputs_exact'], True, 'core own repeats')
        tc, mc = core_result(record['result'], inp, 2 if dual else 1)
        core_counts.append({'label': label, 'tensor_complex_values': tc, 'master_complex_values': mc})
    for shape, record in zip(shapes['core'] + shapes['extended_core'], control['core'] + control['extended_core'], strict=True):
        same(shape['label'], record['label'], 'core shape-only label')
        same(shape['components'], record['components'], 'core shape-only component count')
        same(shape['input'], record['input'], 'core shape-only input')
        same(shape['complex_output_count'], len(record['result']['values']), 'core shape-only complete output count')
    cache = control['cache_interleaving']; same(cache['same_immutable_plan'], True, 'same immutable cache control plan')
    same(cache['status'], 'passed', 'cache status')
    same(len(cache['expected_current_process_records']), 4, 'four independent reference workspaces')
    cache_counts = []
    for i, (expected, dual) in enumerate(zip(cache['expected_current_process_records'], [False, True, False, True], strict=True)):
        tc, mc = core_result(expected, core_input(53, dual), 2 if dual else 1, cache=True)
        cache_counts.append({'workspace_case': i, 'dual': dual, 'tensor_complex_values': tc, 'master_complex_values': mc})
    same([s['workspace_case'] for s in cache['steps']], [2, 1, 0, 3, 2, 0, 3, 1], 'independent cache interleaving sequence')
    same(shapes['cache_shapes'], [False, True, False, True], 'shape-only workspace contexts')
    same(shapes['cache_indices'], [2, 1, 0, 3, 2, 0, 3, 1], 'shape-only interleaving sequence')
    for step in cache['steps']:
        same(step['backend'], 'SymbolicaBatch', 'cache backend')
        same(step['dual'], [False, True, False, True][step['workspace_case']], 'cache shape/context')
        same(step['result'], cache['expected_current_process_records'][step['workspace_case']], 'full cache record equals own current-process workspace')
    after = {str(k): sha(k) for k in guards}
    same(after, before, 'all input hashes unchanged after saved-data audit')
    report = {
        'status': 'passed', 'scope': 'Independent saved-data-only CONTROL audit of pinned2c1f334 optimized captured whole-call qualification; no algebra/library/integral/timing/compiler execution.',
        'pinned_source_revision': PIN, 'producer_results_sha256': sha(RESULT), 'protocol_sha256': sha(PROTO), 'raw_sha256': sha(RAW),
        'checker_sha256': sha(__file__), 'source_context_role': 'Pinned isolated2c1f334 baseline/candidate and captured fixture overlays; not the concurrently modified working-tree implementation.',
        'producer_admission_imported_or_called': False, 'numerical_or_compiler_or_benchmark_executed': False,
        'independent_original_iregi_comparison_claim': False, 'performance_claim': False, 'production_adoption_qualified': False,
        'control_response_serials': [33, 34, 35, 36], 'full_control_cross_and_own_repeat_equality': True,
        'direct_cases': len(specs), 'direct_rows': 133, 'direct_success_rows': 106, 'direct_expected_error_rows': 27,
        'direct_success_complex_values_all_six_slots_components': complex_count, 'direct_error_census': dict(errors), 'direct_case_inventory': per_case,
        'master_output_order': ORDER, 'core_counts': core_counts, 'cache_workspace_counts': cache_counts, 'cache_interleaving_steps': 8,
        'precision_and_derivative_coverage': {
            'f64': True, 'DoubleFloat_beyond53': 'exact1+2^-80 direct A0 and2+2^-53 core mass',
            'Float53_distinct_type': True, 'Float128_256_prototypes_and64_128_256_lane_precisions': True,
            'dynamic_Dual_shapes_observed': [[[0]], [[0], [1]]],
            'static_Dual_in_this_runtime': False, 'higher_or_mixed_Dual_in_this_runtime': False,
            'caution': 'Static/higher/mixed Dual behavior is outside this saved60-request corpus; earlier local scheduler-test evidence must be bound separately.'},
        'guard_count': len(guards), 'input_sha256_before': before, 'input_sha256_after': after,
        'assertions_passed': checks, 'shape_only_manifest_used_as_convention_not_output_oracle': True,
        'fixtures_reconstructed_independently_from_frozen_Rust_constants': True,
        'source_fixtures_sha256': {str(ROOT / f): sha(ROOT / f) for f in proto['protected_sha256'] if f.endswith(('/probe/master_controls.rs', '/probe/core_probe.rs', '/probe/probe.rs', '/fresh-source/master_controls.rs'))},
    }
    (HERE / 'review.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'assertions_passed', 'direct_cases', 'direct_rows', 'direct_success_rows', 'direct_expected_error_rows', 'direct_success_complex_values_all_six_slots_components', 'guard_count']}))

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (HERE / 'failed-review.json').write_text(json.dumps({'status': 'failed', 'error': repr(error), 'assertions_passed_before_failure': checks, 'checker_sha256': sha(__file__)}, indent=2) + '\n')
        raise

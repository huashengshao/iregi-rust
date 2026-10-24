"""Untimed public-policy admission. Importing this module launches no processes.

Historical values supply fixture identities, shapes and error masks only.
Extended values stay exact Fractions; only ordinary f64 comparisons use floats.
"""
from pathlib import Path
from fractions import Fraction
import importlib.util
import json
import math
import re
import struct

ROOT = Path.cwd()
helper = ROOT / 'validation/benchmark/run.py'
spec = importlib.util.spec_from_file_location('public_policy_qualification_helper', helper)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
POLICIES = {'baseline': 'Symbolica', 'candidate': 'NativeF64Abc'}
ORDER = ['finite', 'total_single', 'ir_double', 'uv_single', 'ir_single', 'derivative_discriminant']
ARITY = {'A0': 2, 'B0': 4, 'C0': 7, 'dB0': 4, 'D0': 11}
CORE_EXECUTION = {'input_rows': 1, 'argument_rows': 1, 'master_family_batches': 2,
                  'master_rows': 3, 'pentagon_box_rows': 0, 'reduction_rows': 1,
                  'fallback_rows': 0, 'fallback_successes': 0, 'analytic_rows': 0}


def exact(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def array(value, length):
    assert type(value) is list and len(value) == length
    return value


def integer(value, expected=None):
    assert type(value) is int and value >= 0
    if expected is not None:
        assert value == expected
    return value


def number(value, domain='f64', finite_field=True, allow_nonfinite=False):
    fields = {'rational', 'precision', 'negative_sign'} | ({'finite'} if finite_field else set())
    assert type(value) is dict and set(value) == fields
    bits = integer(value['precision'])
    assert 0 < bits <= 2 ** 32 - 1 and type(value['negative_sign']) is bool
    if domain in ('f64', 'DoubleFloat'):
        assert bits == {'f64': 53, 'DoubleFloat': 106}[domain]
    else:
        assert domain == 'Float'
    if finite_field:
        assert type(value['finite']) is bool
        if not value['finite']:
            assert allow_nonfinite and value['rational'] is None
            return None
    assert type(value['rational']) is str and re.fullmatch(r'-?\d+(?:/[1-9]\d*)?', value['rational'])
    result = Fraction(value['rational'])
    assert result.denominator & (result.denominator - 1) == 0, 'nonbinary represented rational'
    if result:
        assert (result < 0) == value['negative_sign']
        if domain != 'DoubleFloat':
            # DD is the exact sum of two f64 values, which may have a large gap.
            numerator = abs(result.numerator)
            significant = numerator >> ((numerator & -numerator).bit_length() - 1)
            assert significant.bit_length() <= bits, 'rational exceeds stored mantissa precision'
    if domain == 'f64':
        native = float(result)
        assert math.isfinite(native) and Fraction.from_float(native) == result
    return result


def complex_exact(value, domain='f64', finite_field=True, allow_nonfinite=False):
    return tuple(number(x, domain, finite_field, allow_nonfinite) for x in array(value, 2))


def finite_complex(value):
    parts = complex_exact(value)
    native = [float(x) if x else math.copysign(0., -1. if m['negative_sign'] else 1.)
              for x, m in zip(parts, value)]
    return complex(*native)


def direct_complex(value):
    complex_exact(value, finite_field=False)
    return finite_complex([{**x, 'finite': True} for x in value])


def metadata(value, bits):
    value = Fraction(value)
    return {'finite': True, 'rational': str(value), 'precision': bits, 'negative_sign': value < 0}


def real_metadata(value, bits, imaginary_bits=None):
    return [metadata(value, bits), metadata(0, bits if imaginary_bits is None else imaginary_bits)]


def snapshot(value, rows, components, errors, domain='f64'):
    assert type(value) is dict and set(value) == {'rows', 'components', 'lanes'}
    integer(value['rows'], rows)
    integer(value['components'], components)
    array(errors, rows)
    for lane, error in zip(array(value['lanes'], rows), errors):
        assert set(lane) == {'error', 'six_outputs'} and lane['error'] == error
        assert error is None or type(error) is str
        if error is not None:
            assert lane['six_outputs'] is None
        else:
            for z in array(lane['six_outputs'], 6 * components):
                complex_exact(z, domain, finite_field=False)


def snapshot_like(value, prior, domain='f64'):
    snapshot(value, prior['rows'], prior['components'], [x['error'] for x in prior['lanes']], domain)


def numeric_moments(lane, count):
    represented = array(lane['represented'], 4 * count)
    moments = array(lane['moments'], count)
    numeric = [z for moment in moments for z in array(moment, 4)]
    for z, actual in zip(represented, numeric):
        value = finite_complex(z)
        for lhs, rhs in zip([value.real, value.imag], array(actual, 2)):
            assert type(rhs) in (int, float) and math.isfinite(rhs)
            assert struct.pack('>d', lhs) == struct.pack('>d', rhs), 'native/represented disagreement'


def compare_six(baseline, candidate, point, family):
    squared = max(1., *(abs(z) for z in point))
    unit = {'A0': squared, 'B0': 1., 'C0': 1. / squared}[family]
    assert math.isfinite(squared) and squared > 0 and math.isfinite(unit) and unit > 0
    maximum = 0.
    for coefficient, (x, y) in enumerate(zip(array(baseline, 6), array(candidate, 6))):
        denominator = (1. if coefficient == 5 else unit) + abs(x)
        error = abs(y - x) / denominator
        assert math.isfinite(denominator) and denominator > 0
        assert math.isfinite(error) and error <= 1e-10, (family, coefficient, error)
        if coefficient == 5:
            assert x == y == 0j
        maximum = max(maximum, error)
    return maximum


def master_compare(base, selected, n, rank, batch):
    groups = {(2, 0): [('B0', batch)], (2, 1): [('B0', batch), ('A0', 2 * batch)],
              (3, 0): [('C0', batch)], (3, 1): [('C0', batch), ('B0', 3 * batch)]}[(n, rank)]
    a = array(base['master_captures'], len(groups))
    b = array(selected['master_captures'], len(groups))
    outputs = differences = 0
    worst = 0.
    for x, y, (family, rows) in zip(a, b, groups):
        for field in ['family', 'components', 'rows', 'requests', 'valid_lanes', 'input', 'output_order', 'errors', 'whole_batch_error']:
            assert exact(x[field], y[field]), field
        assert x['family'] == family
        integer(x['rows'], rows); integer(x['components'], 1)
        assert x['backend'] == 'SymbolicaBatch' and y['backend'] == 'RustBatch'
        assert x['whole_batch_error'] is None and exact(x['errors'], [None] * rows)
        assert exact(x['valid_lanes'], list(range(batch))) and x['output_order'] == ORDER
        leaves = {('B0', 2, 0): [0], ('B0', 2, 1): [0], ('A0', 2, 1): [1, 2],
                  ('C0', 3, 0): [0], ('C0', 3, 1): [0], ('B0', 3, 1): [1, 2, 3]}[(family, n, rank)]
        assert exact(x['requests'], [[leaf, lane] for leaf in leaves for lane in range(batch)])
        inputs = [finite_complex(z) for z in array(x['input'], ARITY[family] * rows)]
        for lane, (xa, ya) in enumerate(zip(array(x['output'], rows), array(y['output'], rows))):
            va = [finite_complex(z) for z in array(xa, 6)]
            vb = [finite_complex(z) for z in array(ya, 6)]
            worst = max(worst, compare_six(va, vb, inputs[lane * ARITY[family]:(lane + 1) * ARITY[family]], family))
            outputs += 6
            differences += sum(not exact(aa, bb) for za, zb in zip(xa, ya) for aa, bb in zip(za, zb))
    return {'status': 'passed', 'master_groups': len(groups), 'master_rows': sum(g[1] for g in groups),
            'complex_outputs': outputs, 'max_normalized_error': worst, 'represented_component_differences': differences}


def validate_response(response, case, samples):
    base = response['baseline']; selected = response['candidate']; batch = len(samples)
    assert response['id'] == case['id'] and case['n'] in (2, 3) and case['rank'] in (0, 1) and batch in (1, 32)
    groups, rows_per_lane = {(2, 0): (1, 1), (2, 1): (2, 3), (3, 0): (1, 1), (3, 1): (2, 4)}[(case['n'], case['rank'])]
    expected_execution = {'input_rows': batch, 'argument_rows': batch, 'master_family_batches': groups,
                          'master_rows': rows_per_lane * batch, 'pentagon_box_rows': 0, 'reduction_rows': batch,
                          'fallback_rows': 0, 'fallback_successes': 0, 'analytic_rows': 0}
    for side, value in [('baseline', base), ('candidate', selected)]:
        assert value['requested_master_policy'] == POLICIES[side] and 'private_selected_native' not in value
        assert value['id'] == case['id'] and value['stable'] is True
        integer(value['n'], case['n']); integer(value['rank'], case['rank']); integer(value['batch'], batch)
        integer(value['iterations'], 0)
        array(value['total_ns'], 0); array(value['elapsed_ns'], 0)
        assert all(field not in value for field in ['engine', 'warmup', 'repeats'])
        assert value['capture_enabled'] is True and value['profiling_enabled'] is False
        assert value['own_repeated_outputs_exact'] is True and value['input_unchanged'] is True
        assert type(value['plan_reused']) is bool
        assert value['scope'] == 'untimed public-policy whole-reduction qualification'
        assert exact(value['degrees'], h.degrees(case['rank']))
        for lane in array(value['lanes'], batch):
            assert lane['status'] == 'success' and lane['fallback_used'] is False and lane['analytic_used'] is False
            numeric_moments(lane, len(value['degrees']))
        for count in value['execution'].values():
            integer(count)
        assert exact(value['execution'], expected_execution)
        assert exact(value['diagnostics'], [[] for _ in range(batch)])
    for field in ['degrees', 'diagnostics', 'execution']:
        assert exact(base[field], selected[field]), field
    assert base['execution']['fallback_rows'] == base['execution']['analytic_rows'] == 0
    cross = h.compare(selected, base, case, samples)
    assert cross['status'] == 'passed', cross
    masters = master_compare(base, selected, case['n'], case['rank'], batch)
    assert base['execution']['master_family_batches'] == masters['master_groups'] and base['execution']['master_rows'] == masters['master_rows']
    return {'whole_cross_backend': cross, 'masters': masters}


def canonical(response):
    result = json.loads(json.dumps(response, allow_nan=False))
    for side in POLICIES:
        result[side].pop('plan_reused', None)
    return result


def selected_case(case, prior, family):
    for field in ['label', 'family', 'baseline_backend', 'candidate_backend', 'input_metadata']:
        assert exact(case[field], prior[field]), field
    assert case['family'] == family and case['status'] == 'passed'
    assert case['baseline_backend'] == 'SymbolicaBatch' and case['candidate_backend'] == 'RustBatch'
    assert case['input_unchanged'] is True and case['own_repeated_outputs_exact'] is True
    for side in POLICIES:
        snapshot_like(case[side], prior[side])
    rows = case['baseline']['rows']
    inputs = array(case['input_metadata'], rows * ARITY[family])
    for z in inputs:
        complex_exact(z, allow_nonfinite=True)
    worst = 0.; differences = zeros = successful = 0
    for lane, (a, b) in enumerate(zip(case['baseline']['lanes'], case['candidate']['lanes'])):
        assert a['error'] == b['error']
        if a['error'] is not None:
            continue
        xa, xb = a['six_outputs'], b['six_outputs']
        point = [finite_complex(z) for z in inputs[lane * ARITY[family]:(lane + 1) * ARITY[family]]]
        worst = max(worst, compare_six([direct_complex(z) for z in xa], [direct_complex(z) for z in xb], point, family))
        successful += 1
        for za, zb in zip(xa, xb):
            for x, y in zip(za, zb):
                differences += not exact(x, y)
                zeros += Fraction(x['rational']) == Fraction(y['rational']) == 0 and x['negative_sign'] != y['negative_sign']
    reported = case['maximum_normalized_error']
    assert type(reported) in (int, float) and math.isfinite(reported) and 0 <= reported <= 1e-10
    assert math.isclose(reported, worst, rel_tol=1e-12, abs_tol=1e-30), 'producer maximum differs from six-output recomputation'
    integer(case['represented_component_differences'], differences)
    integer(case['signed_zero_differences'], zeros)
    return {'family': family, 'label': case['label'], 'successful_rows': successful, 'maximum_normalized_error': worst,
            'represented_component_differences': differences, 'signed_zero_differences': zeros}


def unchanged_case(case, rows, components, errors, inputs, domain):
    assert case['status'] == 'passed' and case['input_unchanged'] is True
    assert case['own_repeated_outputs_exact'] is True and case['candidate_exactly_matches_baseline'] is True
    assert exact(case['input_metadata'], inputs)
    for z in inputs:
        complex_exact(z, domain, allow_nonfinite=True)
    for key in ['represented_outputs', 'baseline', 'candidate']:
        snapshot(case[key], rows, components, errors, domain)
    assert exact(case['represented_outputs'], case['baseline']) and exact(case['baseline'], case['candidate'])


def core_captures(captures, components, domain, backend, mass):
    # Fixed spacelike N2r1 fixture: no numerical reconstruction of general inputs.
    for group, family, requests, values, seed in zip(array(captures, 2), ['B0', 'A0'],
            [[[0, 0]], [[1, 0], [2, 0]]], [[-1, mass, 3, 1], [3, 1, mass, 1]], [1, 2]):
        rows = len(requests)
        assert group['family'] == family and group['backend'] == backend
        integer(group['rows'], rows); integer(group['components'], components)
        assert exact(group['requests'], requests) and exact(group['valid_lanes'], [0])
        assert group['output_order'] == ORDER and group['whole_batch_error'] is None
        assert exact(group['errors'], [None] * rows)
        expected = [Fraction(v) for v in values]
        if components == 2:
            expected = [part for i, v in enumerate(expected) for part in [v, Fraction(i == seed)]]
        for actual, expected_re in zip(array(group['input'], 4 * components), expected):
            assert complex_exact(actual, domain) == (expected_re, Fraction(0))
        for row in array(group['output'], rows):
            for z in array(row, 6 * components):
                complex_exact(z, domain)


def core_input(bits, dual=False, mixed=False):
    values = [0, 0, 0, 0, 0, 1, 0, 0, Fraction(18014398509481985, 9007199254740992) if mixed else 2, 3, 1]
    if dual:
        values = [part for i, v in enumerate(values) for part in [v, int(i == 8)]]
    return [real_metadata(x, bits) for x in values]


def whole_unchanged(record, label, domain, bits, dual=False, mixed=False):
    components = 2 if dual else 1
    assert record['label'] == label and record['input_unchanged'] is True and record['own_repeated_outputs_exact'] is True
    integer(record['components'], components)
    assert exact(record['input'], core_input(bits, dual, mixed))
    for z in record['input']:
        complex_exact(z, domain)
    result = record['result']
    assert result['statuses'] == '[Success]' and exact(result['diagnostics'], [[]])
    assert exact(result['fallback_used'], [False]) and exact(result['analytic_used'], [False])
    assert exact(result['execution'], CORE_EXECUTION)
    for z in array(result['values'], 20 * components):
        complex_exact(z, domain)
    core_captures(result['master_captures'], components, domain, 'SymbolicaBatch',
                  Fraction(18014398509481985, 9007199254740992) if mixed else 2)


def extended_masters(groups):
    definitions = [
        ('DoubleFloat_beyond53', 'DoubleFloat', 106, [('three_lanes', [106] * 3), ('empty_reuse', []), ('singleton_recovery', [106])]),
        ('Float53_is_not_f64', 'Float', 53, [('singleton', [53])]),
    ]
    for bits in [128, 256]:
        definitions.append((f'Float_mixed_prototype{bits}', 'Float', bits,
                            [(f'lane_precisions_{p}', p) for p in [[128, 256, 64], [256], [], [64, 128, 256]]]))
    count = successful = 0
    for group, (label, domain, bits, cases) in zip(array(groups, 4), definitions):
        assert group['label'] == label and group['family'] == 'A0' and group['backend'] == 'SymbolicaBatch'
        assert group['status'] == 'passed' and group['shape'] is None
        integer(group['components'], 1)
        for case, (case_label, precisions) in zip(array(group['cases'], len(cases)), cases):
            assert case['label'] == case_label
            inputs = []
            for precision in precisions:
                if domain == 'DoubleFloat':
                    inputs += [real_metadata(1 + Fraction(1, 2 ** 80), 106), real_metadata(1, 106)]
                elif bits == 53:
                    inputs += [real_metadata(2, 53), real_metadata(1, 53)]
                else:
                    inputs += [real_metadata(1 + Fraction(1, 2 ** (precision - 10)), precision, 128), real_metadata(1, 128, 64)]
            unchanged_case(case, len(precisions), 1, [None] * len(precisions), inputs, domain)
            for lane, point in zip(case['baseline']['lanes'], [inputs[i:i + 2] for i in range(0, len(inputs), 2)]):
                expected_uv = [{k: v for k, v in x.items() if k != 'finite'} for x in point[0]]
                assert exact(lane['six_outputs'][3], expected_uv), 'A0 UV mass precision/value/sign changed'
            count += 1; successful += len(precisions)
    assert count == 12 and successful == 19
    return {'groups': 4, 'cases': count, 'successful_rows': successful}


def cache_interleaving(record):
    assert record['status'] == 'passed' and record['same_immutable_plan'] is True
    expected = array(record['expected_current_process_records'], 4)
    for index, value in enumerate(expected):
        dual = index % 2 == 1; components = 2 if dual else 1
        assert value['stable'] is True and exact(value['diagnostics'], [[]]) and exact(value['execution'], CORE_EXECUTION)
        lane = array(value['lanes'], 1)[0]
        assert lane['status'] == 'success' and lane['fallback_used'] is False and lane['analytic_used'] is False
        for z in array(lane['represented'], 20 * components):
            finite_complex(z)
        if dual:
            assert 'moments' not in lane
        else:
            numeric_moments(lane, 5)
        core_captures(value['master_captures'], components, 'f64', 'RustBatch' if index == 2 else 'SymbolicaBatch', 2)
    assert exact(expected[1], expected[3]), 'Dual records differ across policies'
    ordinary_master_comparison = master_compare(expected[0], expected[2], 2, 1, 1)
    sample = {'shifts': [[0., 0., 0., 0.], [0., 1., 0., 0.]], 'masses': [[2., 0.], [3., 0.]], 'mu': 1.}
    ordinary_tensor_comparison = h.compare(expected[2], expected[0], {'n': 2, 'rank': 1}, [sample])
    assert ordinary_tensor_comparison['status'] == 'passed'
    for step, index in zip(array(record['steps'], 8), [2, 1, 0, 3, 2, 0, 3, 1]):
        assert step['requested_master_policy'] == ('Symbolica' if index < 2 else 'NativeF64Abc')
        assert step['dual'] is (index % 2 == 1) and exact(step['result'], expected[index])
    return {'status': 'passed', 'expected_records': 4, 'interleaved_records': 8,
            'ordinary_masters': ordinary_master_comparison, 'ordinary_tensors': ordinary_tensor_comparison}


def validate_controls(response, inventory):
    assert response['id'] == 'controls' and response['status'] == 'passed'
    assert exact(response['requested_master_policies'], POLICIES)
    c = response['controls']; expected = inventory['controls']
    a = array(c['baseline'], 1); b = array(c['candidate'], 1)
    assert exact(a, b)
    prior_whole = array(expected['baseline'], 1)[0]
    for actual in [a[0], b[0]]:
        whole_unchanged(actual, 'f64 Dual N2r1', 'f64', 53, dual=True)
        for field in ['label', 'components', 'input']:
            assert exact(actual[field], prior_whole[field])
        for field in ['statuses', 'diagnostics', 'fallback_used', 'analytic_used', 'execution']:
            assert exact(actual['result'][field], prior_whole['result'][field])
    m = c['masters']; em = expected['masters']
    assert m['status'] == 'passed'
    checks = []
    for group, old, family in zip(array(m['selected_families'], 3), array(em['selected_families'], 3), ['A0', 'B0', 'C0']):
        assert group['family'] == old['family'] == family and group['status'] == 'passed'
        for field in ['layout_and_overflow_errors_checked', 'ordinary_dual_adapter_rejected', 'warm_clone_checked']:
            assert group[field] is True
        for case, prior in zip(array(group['cases'], len(old['cases'])), old['cases']):
            checks.append(selected_case(case, prior, family))
    assert len(checks) == 34
    unchanged_count = 0
    for group, old in zip(array(m['unchanged_paths'], 6), array(em['unchanged_paths'], 6)):
        for field in ['label', 'family', 'components', 'shape']:
            assert exact(group[field], old[field])
        assert group['status'] == 'passed' and group['backend'] == 'SymbolicaBatch'
        integer(group['components'])
        for case, prior in zip(array(group['cases'], len(old['cases'])), old['cases']):
            assert case['label'] == prior['label']
            old_snapshot = prior['represented_outputs']
            unchanged_case(case, old_snapshot['rows'], old_snapshot['components'], [x['error'] for x in old_snapshot['lanes']], prior['input_metadata'], 'f64')
            unchanged_count += 1
    assert unchanged_count == 21
    extended = response['extended_unchanged_controls']
    assert extended['status'] == 'passed'
    assert exact(extended['inventory'], [
        {'label': 'DoubleFloat N2r1 beyond53', 'numeric_type': 'DoubleFloat', 'precision': 106, 'rows': 1, 'components': 1, 'tensor_complex_values': 20},
        {'label': 'Float256 N2r1 beyond53', 'numeric_type': 'Float', 'precision': 256, 'rows': 1, 'components': 1, 'tensor_complex_values': 20},
    ])
    array(extended['baseline'], 2); array(extended['candidate'], 2)
    assert exact(extended['baseline'], extended['candidate'])
    for side in POLICIES:
        for record, label, domain, bits in zip(extended[side], ['DoubleFloat N2r1 beyond53', 'Float256 N2r1 beyond53'], ['DoubleFloat', 'Float'], [106, 256]):
            whole_unchanged(record, label, domain, bits, mixed=True)
    master_extended = extended_masters(m['extended_unchanged_paths'])
    master_inventory = [
        {'label': 'DoubleFloat_beyond53', 'numeric_type': 'DoubleFloat', 'prototype_precision': 106, 'family': 'A0', 'components': 1, 'shape': None, 'case_rows': [3, 0, 1]},
        {'label': 'Float53_is_not_f64', 'numeric_type': 'Float', 'prototype_precision': 53, 'family': 'A0', 'components': 1, 'shape': None, 'case_rows': [1]},
    ]
    for bits in [128, 256]:
        master_inventory.append({'label': f'Float_mixed_prototype{bits}', 'numeric_type': 'Float', 'prototype_precision': bits, 'family': 'A0', 'components': 1,
                                 'shape': None, 'case_real_mass_precisions': [[128, 256, 64], [256], [], [64, 128, 256]], 'case_rows': [3, 1, 0, 3]})
    assert exact(m['extended_inventory'], master_inventory)
    cache = cache_interleaving(response['cache_interleaving'])
    return {'status': 'passed', 'selected_cases': len(checks), 'unchanged_cases': unchanged_count, 'whole_dual_cases': 1,
            'selected_recomputed': checks, 'extended_whole_cases': 2, 'extended_masters': master_extended, 'cache_interleaving': cache}

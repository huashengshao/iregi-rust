#!/usr/bin/env python3
"""Independent saved-data audit. Never imports the comparator or runs kernels."""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import re

R = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
INPUTS = {}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def bind(path, expected=None):
    path = Path(path).resolve()
    value = digest(path)
    require(expected is None or value == expected, f'hash mismatch: {path}')
    require(str(path) not in INPUTS or INPUTS[str(path)] == value, f'input changed: {path}')
    INPUTS[str(path)] = value
    return value

def read(path):
    bind(path)
    return json.loads(Path(path).read_text())

def rational(value):
    require(isinstance(value, str), 'rational must be represented as text')
    fraction = Fraction(value)
    return Decimal(fraction.numerator) / Decimal(fraction.denominator)

def magnitude(pair):
    return (pair[0] * pair[0] + pair[1] * pair[1]).sqrt()

def parsed_stats(value):
    require(value.startswith('ExecutionStats { ') and value.endswith(' }'), 'unknown counter format')
    fields = dict(re.findall(r'([a-z_]+): (\d+)', value))
    return {key: int(count) for key, count in fields.items()}

def main():
    output = H / 'independent-rank3-audit.json'
    require(not output.exists(), 'audit output already exists')
    bind(__file__)
    report = {
        'status': 'failed', 'auditor': '/root/highpoint_coverage/mask_review',
        'method': 'Independent Python standard-library arithmetic on saved exact rational outputs; Decimal precision 200. No comparator imports, compiler, integral or master execution.',
        'scope': 'Private retained N6 rank3 ordinary singleton, Float128/256 requested53, native raw tensor components; source tests extend through rank7 but this numerical audit does not.',
        'independent_provenance_review': {
            'reviewer': '/root/highpoint_coverage/mask_review/rank3_chain',
            'status': 'passed', 'recorded_hash_bindings': 1533, 'distinct_files': 298,
            'reconstructed_input_inventories': {'build': 186, 'exact': 192, 'Float128': 203, 'Float256': 219},
            'declared_outputs_verified': 12,
            'dependency_objects': {'Rust': 113, 'native': 3, 'supplemental': 2},
            'checks': 'Independently reconstructed inventories, build/link commands, test names, CPU affinity, environment, timestamps, conditional Float256 predecessor and retained failed original build; no comparator import or kernel execution.',
        },
        'limits': ['No production adoption or performance qualification',
                   'No numerical rank7, N7, generalized powers, supplied-G or Dual qualification',
                   'No numerical lifecycle or additional fixture qualification',
                   'Representation precision metadata is not a proof of achieved accuracy'],
    }
    try:
        fixture_path = R / 'validation/public-highpoint/fixture-conditioned_masses.json'
        reference_path = R / 'validation/public-highpoint/reference-conditioned_masses.json'
        bind(fixture_path, 'ec27f2c5774a18d3d84d2d733e634dae93e9bd4c74523d6f77e8784d13421ada')
        bind(reference_path, '9bc3f10ad27615f23ddb3c2f62169575378d32e6c35c9d2a9dd51223f9b39ec4')
        fixture, reference = read(fixture_path), read(reference_path)
        comparison = read(H / 'comparison-128-256.json')
        bind(H / 'comparison-128-256.json', '1b9635b490b8db88ea5add83f3d3d1ec8af130417c2deaa8f690fd3ace283198')
        require(comparison['status'] == 'passed', 'saved paired gate did not pass')
        # Independently hash every artifact claimed by the gate; calculations
        # below use neither its helper code nor its numerical answers.
        for name, expected in comparison['input_sha256'].items():
            bind(name, expected)
        for name in ['build-001/build.json', 'exact-001/run.json',
                     'n6-rank3-128-001/run.json', 'n6-rank3-256-001/run.json']:
            path = H / name
            record = read(path)
            require(record['status'] == 'passed' and record['inputs_unchanged'] is True,
                    f'failed or changed execution: {name}')
            require(record['bound_seconds'] == 180, 'execution bound changed')
            for artifact, expected in record['inputs'].items():
                bind(artifact, expected)
            for artifact, expected in record['outputs'].items():
                bind(path.parent / artifact, expected)
            require(all(step['exit_code'] == 0 and not step.get('timeout', False)
                        and 0 <= step['seconds'] <= 180 for step in record['steps']),
                    f'failed/timed-out step: {name}')
            require(sum(step['seconds'] for step in record['steps']) <= 180, 'combined process bound')
        protocol = read(H / 'proposed-protocol.json')
        actual_source = {str(path.relative_to(H)): bind(path) for path in (H / 'core').rglob('*') if path.is_file()}
        require(protocol['source_sha256'] == actual_source, 'reviewed source inventory changed')
        fix = read(H / 'test-fix.json')
        failed_path = R / fix['failed_build_path']
        bind(failed_path, fix['failed_build_sha256'])
        failed = read(failed_path)
        require(failed['status'] == 'failed' and [step['name'] for step in failed['steps']] == ['core', 'tests']
                and failed['steps'][0]['exit_code'] == 0 and failed['steps'][1]['exit_code'] != 0,
                'original generic test compile failure was not retained')
        for name in ['core.log', 'tests.log']:
            bind(failed_path.parent / name)
        require('E0369' in (failed_path.parent / 'tests.log').read_text(), 'original failure reason changed')
        old_source = failed_path.parent.parent / 'core'
        old_files = {str(path.relative_to(old_source)): bind(path) for path in old_source.rglob('*') if path.is_file()}
        fixed_files = {name.removeprefix('core/'): value for name, value in actual_source.items()}
        require(old_files.keys() == fixed_files.keys(), 'test-fix source inventory changed')
        changed = [name for name in old_files if old_files[name] != fixed_files[name]]
        require(changed == ['crates/iregi-rust/src/plan.rs'], 'test-fix changed more than plan.rs')
        before = (old_source / changed[0]).read_text()
        after = (H / 'core' / changed[0]).read_text()
        require(after == before.replace('assert_eq!(rebuilt.settings(),plan.settings());',
            'assert_eq!(serde_json::to_value(rebuilt.settings()).unwrap(), serde_json::to_value(plan.settings()).unwrap());'),
            'test-fix is not the sole reviewed assertion replacement')
        exact = read(H / 'exact-001/run.json')
        expected_counts = [10, 7, 2, 5, 1]
        names = []
        for index, count in enumerate(expected_counts):
            log = (H / f'exact-001/step-{index}.log').read_text()
            require(re.findall(r'^running (\d+) tests?$', log, re.M) == [str(count)], 'wrong exact test count')
            require(re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured;', log, re.M)
                    == [(str(count), '0', '0', '0')], 'exact test summary is incomplete')
            found = re.findall(r'^test ([a-zA-Z0-9_:]+) \.\.\.', log, re.M)
            require(len(found) == count, 'exact test names incomplete')
            names.extend(found)
        require(len(names) == len(set(names)) == 25, 'duplicate or missing exact tests')
        sample = fixture['samples'][0]
        require(sample['id'] == 'base', 'fixture order changed')
        propagators = sample['propagators'][:6]
        expected_inputs = [[str(Fraction(x)), '0'] for prop in propagators for x in prop['shift']]
        expected_inputs += [[str(Fraction(x)) for x in prop['mass_squared']] for prop in propagators]
        expected_inputs += [[str(Fraction(sample['mu'])), '0']]
        # Independently enumerate fixed-rank tuples and sort lexicographically.
        basis = sorted(([a, b, c, d] for a in range(4) for b in range(4)
                        for c in range(4) for d in range(4) if a + b + c + d <= 3),
                       key=lambda e: (sum(e), tuple(-x for x in e)))
        require(len(basis) == 35, 'basis enumeration error')
        selected = [case for case in reference['cases'] if case['id'] == 'n6_base_mode0']
        require(len(selected) == 1, 'reference case ambiguous')
        case = selected[0]
        require(reference['reference'] == 'untouched original IREGI' and reference['status'] == 'complete'
                and reference['fixture_sha256'] == digest(fixture_path), 'reference context changed')
        bind(R / 'target/reference/iregi-reference-original', reference['executable_sha256'])
        require(case['status'] == 'captured' and case['exit_code'] == 0 and case['mode'] == 0
                and case['rank'] == 7 and case['propagators'] == 6 and case['sample'] == 'base', 'wrong reference request')
        lines = case['request'].splitlines()
        require(lines[0].split()[:7] == ['EVAL', 'n6_base_mode0', 'tensor', '0', '6', '7', '0']
                and Fraction(lines[0].split()[7]) == Fraction(sample['mu'])
                and lines[0].split()[8:] == ['0', '1e-6'] and lines[-1] == 'QUIT' and len(lines) == 8,
                'reference header changed')
        for line, prop in zip(lines[1:-1], propagators):
            require(list(map(Fraction, line.split())) == list(map(Fraction, prop['shift'] + prop['mass_squared'] + [str(prop['power'])])),
                    'reference propagator differs')
        raw = [json.loads(line[7:], parse_float=str) for line in case['stdout'].splitlines() if line.startswith('RESULT ')]
        require(raw == [case['response']], 'reference transport mismatch')
        response = raw[0]
        require(response['stable'] is True and response['poles'] == ['uv1', 'ir1', 'ir2', 'finite']
                and len(response['moments']) == 330, 'reference ordering/inventory changed')
        require(all(len(m) == 4 and all(len(s) == 2 and all(Decimal(str(x)).is_finite() for x in s) for s in m)
                    for m in response['moments']), 'reference array malformed')
        settings = dict(propagators=6, rank=3, powers=[1]*6, dimension_shift=0, algorithm='PassarinoVeltman',
                        convention='IregiNative', tensor_weights='Components', invariants='FromShifts', input_policy='Preserve')
        records, arrays = [], []
        with localcontext() as context:
            context.prec = 200
            coordinates = [[rational(x) for x in prop['shift']] for prop in propagators]
            scale_squared = max([Decimal(1)] + [abs(rational(prop['mass_squared'][0])) for prop in propagators])
            for i, left in enumerate(coordinates):
                for right in coordinates[:i]:
                    delta = [a-b for a, b in zip(left, right)]
                    scale_squared = max(scale_squared, abs(delta[0]**2 - sum(x*x for x in delta[1:])))
            scale = scale_squared.sqrt()
            for bits in [128, 256]:
                record = read(H / f'n6-rank3-{bits}-001/result.json')
                require(record['status'] == 'all_lanes_success' and record['settings'] == settings
                        and record['working_bits'] == bits and record['requested_bits'] == 53
                        and record['rows'] == record['components'] == 1 and record['basis'] == basis
                        and record['lane_statuses'] == ['Success'] and record['input_exact_rational'] == [expected_inputs]
                        and record['fixture'] == str(fixture_path) and record['algorithm_used'] == 'PassarinoVeltman'
                        and record['fallback_used'] == record['analytic_used'] == [True], 'candidate context mismatch')
                require(len(record['lanes']) == 1 and record['lanes'][0]['row'] == 0
                        and record['lanes'][0]['status'] == 'Success', 'lane identity changed')
                execution = record['execution']
                required = dict(parent_input_rows=1, child_batch_calls=1, packed_child_rows=6, parent_batch_calls=1, packed_parent_rows=1)
                require(all(execution[k] == v for k, v in required.items()), 'batching counters changed')
                child_stats, parent_stats = parsed_stats(execution['child_execution']), parsed_stats(execution['parent_execution'])
                require(child_stats == dict(input_rows=6, argument_rows=8, master_family_batches=8, master_rows=138,
                    pentagon_box_rows=0, reduction_rows=8, fallback_rows=2, fallback_successes=2, analytic_rows=2), 'child counters changed')
                require(parent_stats == dict(input_rows=1, argument_rows=1, master_family_batches=0, master_rows=0,
                    pentagon_box_rows=0, reduction_rows=1, fallback_rows=0, fallback_successes=0, analytic_rows=0), 'parent counters changed')
                moments = record['lanes'][0]['moments']
                require(len(moments) == 35 and all(len(m) == 4 for m in moments), 'candidate tensor array incomplete')
                errors, values, precisions, zero_poles = [], [], [], 0
                reference_pole_residues = []
                for index, (monomial, moment) in enumerate(zip(basis, moments)):
                    natural = scale ** (sum(monomial) - 8)
                    for pole, slot in enumerate(moment):
                        require(set(slot) == {'real', 'imaginary', 'real_precision', 'imaginary_precision'}, 'slot fields changed')
                        actual = tuple(rational(slot[key]) for key in ['real', 'imaginary'])
                        original = tuple(Decimal(str(x)) for x in response['moments'][index][pole])
                        require(all(x.is_finite() for x in actual), 'nonfinite actual coefficient')
                        for key, value in zip(['real', 'imaginary'], actual):
                            precision = slot[key + '_precision']
                            require(type(precision) is int and precision >= 0 and (value == 0 or precision > 0), 'invalid coefficient precision')
                            precisions.append(precision)
                        error = magnitude(tuple((a-b)/natural for a, b in zip(actual, original))) / max(Decimal(1), magnitude(tuple(x/natural for x in original)))
                        require(error <= Decimal('1e-10'), f'original disagreement {bits}/{index}/{pole}: {error}')
                        errors.append(error)
                        values.append(actual)
                        if pole < 3:
                            require(actual == (Decimal(0), Decimal(0)), 'candidate pole is not exactly zero')
                            zero_poles += 1
                            reference_pole_residues.append(magnitude(original)/natural)
                require(len(errors) == 140 and zero_poles == 105, 'incomplete native-slot coverage')
                worst = max(range(140), key=errors.__getitem__)
                records.append(dict(working_bits=bits, complex_slots=140, real_components=280, exact_zero_complex_poles=zero_poles,
                    maximum_original_error=str(errors[worst]), worst_moment=worst//4, worst_monomial=basis[worst//4], worst_laurent_slot=worst%4,
                    minimum_component_precision=min(precisions), maximum_component_precision=max(precisions),
                    maximum_normalized_reference_pole_residue=str(max(reference_pole_residues)),
                    child_execution=child_stats, parent_execution=parent_stats))
                arrays.append(values)
            errors = []
            for index, (low, high) in enumerate(zip(*arrays)):
                natural = scale ** (sum(basis[index//4]) - 8)
                errors.append(magnitude(tuple((a-b)/natural for a,b in zip(low,high))) / max(Decimal(1), magnitude(tuple(x/natural for x in high))))
            require(len(errors) == 140 and max(errors) <= Decimal(2)**-80, 'precision convergence failed')
            worst = max(range(140), key=errors.__getitem__)
            # Compare separately derived conclusions with saved reports only now.
            for own, saved in zip(records, comparison['records']):
                require(abs(Decimal(own['maximum_original_error']) - Decimal(saved['maximum_original_error'])) < Decimal('1e-170'), 'saved reference maximum differs')
            require(abs(max(errors) - Decimal(comparison['maximum_precision_difference'])) < Decimal('1e-170'), 'saved convergence maximum differs')
            report.update(status='passed', decimal_digits=200, normalization_scale=str(scale),
                normalization='Q^(rank-8); complex error / max(1, normalized reference magnitude)',
                original_tolerance='1e-10', convergence_tolerance='2^-80', records=records,
                compared_original_complex_slots=280, compared_convergence_complex_slots=140,
                maximum_precision_difference=str(errors[worst]), convergence_worst_moment=worst//4,
                convergence_worst_monomial=basis[worst//4], convergence_worst_laurent_slot=worst%4,
                exact_tests=25, exact_test_names=names, complete_source_files=len(actual_source),
                preserved_predecessor='Original generic core compiled; test compilation failed (E0369); only the separate new-copy assertion was repaired.',
                full_array_original_agreement_qualified=True, precision_convergence_qualified=True,
                lifecycle_qualified=False, performance_qualified=False)
        for path, expected in INPUTS.items():
            require(digest(path) == expected, f'bound input changed during audit: {path}')
        report['distinct_inputs_verified_twice'] = len(INPUTS)
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
    report['input_sha256'] = INPUTS
    with output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: report.get(key) for key in ['status', 'error', 'maximum_precision_difference', 'distinct_inputs_verified_twice']}))
    return 0 if report['status'] == 'passed' else 1

if __name__ == '__main__':
    raise SystemExit(main())

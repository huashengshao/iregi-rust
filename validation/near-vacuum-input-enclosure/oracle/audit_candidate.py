#!/usr/bin/env python3
"""Recompute recorded accuracy checks using exact rational numerical arithmetic.

This script does not prepare symbolic expressions, integrate polynomials, or
call the candidate. It audits the independent oracle and candidate JSON files.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--output', type=Path, default=HERE / 'candidate-audit.json')
    args = parser.parse_args()
    oracle_path = HERE / 'output.json'
    candidate_path = args.candidate.resolve()
    candidate = json.loads(candidate_path.read_text())
    oracle = json.loads(oracle_path.read_text())
    checks = []

    def check(condition, label):
        checks.append({'label': label, 'passed': bool(condition)})

    def q(value):
        return Fraction(value)

    def point(value):
        return q(value['real_exact_rational']), q(value['imaginary_exact_rational'])

    def rectangle(value):
        return tuple(q(x) for x in value['real'] + value['imaginary'])

    def contains(bounds, value):
        rl, ru, il, iu = bounds
        return rl <= value[0] <= ru and il <= value[1] <= iu

    def compare(row, reference, label):
        value = point(row['numeric_value'])
        center = point(reference['center'])
        radius = q(reference['absolute_complex_remainder_bound_exact_rational'])
        rl, ru, il, iu = rectangle(row['candidate_rectangle'])
        check(radius >= 0 and rl <= ru and il <= iu, label + ': valid intervals')
        check(point(row['oracle_center']) == center, label + ': independent oracle center')
        check(q(row['oracle_radius']) == radius, label + ': independent oracle radius')
        numeric_error = (abs(value[0] - center[0]) + radius)**2 + (abs(value[1] - center[1]) + radius)**2
        rectangle_error = (max(abs(rl-center[0]), abs(ru-center[0]))+radius)**2 + (max(abs(il-center[1]), abs(iu-center[1]))+radius)**2
        represented_error = max(abs(value[0]-rl), abs(value[0]-ru))**2 + max(abs(value[1]-il), abs(value[1]-iu))**2
        allowed = Fraction(1, 2**(2*candidate['requested_bits'])) * max(Fraction(1), value[0]**2+value[1]**2)
        overlap = max(rl, center[0]-radius) <= min(ru, center[0]+radius) and max(il, center[1]-radius) <= min(iu, center[1]+radius)
        oracle_contained = rl <= center[0]-radius and ru >= center[0]+radius and il <= center[1]-radius and iu >= center[1]+radius
        recomputed = {
            'numeric_error_squared_upper': numeric_error,
            'entire_candidate_rectangle_error_squared_upper': rectangle_error,
            'numeric_to_candidate_rectangle_error_squared_upper': represented_error,
            'allowed_error_squared': allowed,
        }
        for field, expected in recomputed.items():
            check(q(row[field]) == expected, label + ': recomputed ' + field)
        check(row['candidate_and_oracle_rectangles_overlap'] == overlap, label + ': overlap metadata')
        check(row['oracle_rectangle_contained_in_candidate'] == oracle_contained, label + ': containment metadata')
        passed = numeric_error <= allowed and rectangle_error <= allowed and represented_error <= allowed and overlap
        check(row['all_bounds_within_requested_budget'] == passed, label + ': acceptance metadata')
        check(passed, label + ': independent accuracy budget')

    check(candidate['status'] == 'non_dyadic_input_enclosure_passed', 'candidate successful status')
    check(candidate['working_bits'] == 256 and candidate['requested_bits'] == 128, 'precision settings')
    check(oracle['status'] == 'exact_five_pinch_oracle_generated', 'oracle successful status')
    check(oracle['fixture']['x_exact_rational'] == '2/5', 'exact non-dyadic node')
    oracle_input = Path(candidate['oracle_input'])
    if not oracle_input.is_absolute():
        oracle_input = ROOT / oracle_input
    check(oracle_input.resolve() == oracle_path, 'candidate references this independent oracle')
    check(len(candidate['boxes']) == len(oracle['boxes']) == 5, 'five boxes')
    for index, (row, reference) in enumerate(zip(candidate['boxes'], oracle['boxes'])):
        label = f'pinch {index}'
        check(row['pinch'] == reference['pinch'] == index, label + ': ordering')
        check(row['status'] == 'Success' and row['order'] == 2, label + ': N2 success')
        check(Fraction(0) <= q(row['rho']) <= Fraction(1, 4), label + ': convergence radius')
        check(q(row['truncation_radius']) >= 0, label + ': nonnegative truncation')
        compare(row['comparison'], reference['oracle'], label)
    compare(candidate['five_box_contraction_vs_independent_J5_D4'], oracle['independent_direct_J5_D4'], 'five-box contraction')
    compare(candidate['mapped_integrand_vs_independent_oracle'], oracle['mapped_integrand_at_x'], 'mapped integrand')

    exact_mass = point(oracle['fixture']['common_shifted_mass_squared'])
    coefficients = [point(row) for row in oracle['geometry']['C_i_at_t']]
    intended_contour = [point(oracle['fixture']['t']), exact_mass,
                        point(oracle['mapped_integrand_at_x']['dt_dx'])] + coefficients
    check(len(candidate['contour_outputs']) == 5, 'five contour report rows')
    rounded_arguments = 0
    for index, row in enumerate(candidate['contour_outputs']):
        label = f'contour {index}'
        check(row['pinch'] == index, label + ': ordering')
        represented_mass = point(row['represented_mass'])
        bounds = rectangle(row['mass_enclosure'])
        check(point(row['intended_mass']) == exact_mass, label + ': exact intended shifted mass')
        check(represented_mass != exact_mass, label + ': shifted mass actually rounded')
        check(contains(bounds, exact_mass), label + ': exact mass enclosed')
        check(contains(bounds, represented_mass), label + ': represented mass enclosed')
        check(contains(rectangle(row['coefficient_enclosure']), coefficients[index]), label + ': exact Cayley coefficient enclosed')
        components = row['components']
        check(len(components) == 8, label + ': eight serialized contour outputs')
        all_contained = True
        for component_index, component in enumerate(components):
            component_label = label + f': component {component_index}'
            expected_role = ['contour_t', 'shifted_mass_squared', 'dt_dx'][component_index] if component_index < 3 else 'coefficient_update'
            check(component['index'] == component_index and component['role'] == expected_role, component_label + ' role')
            intended = intended_contour[component_index]
            represented = point(component['represented'])
            bounds = rectangle(component['rectangle'])
            check(point(component['intended']) == intended, component_label + ' independent exact input')
            contained = contains(bounds, intended) and contains(bounds, represented)
            all_contained &= contained
            check(contained, component_label + ' intended and represented enclosed')
            check(all(number.denominator & (number.denominator-1) == 0 for number in represented), component_label + ' represented binary rational')
        check(row['all_eight_outputs_contain_exact_oracle_values_and_represented_outputs'] == all_contained, label + ': full contour containment metadata')
        check(components[1]['represented'] == row['represented_mass'] and components[1]['rectangle'] == row['mass_enclosure'], label + ': mass trace matches reused input')
        check(components[3+index]['rectangle'] == row['coefficient_enclosure'], label + ': selected coefficient trace matches contraction input')
        rounded_arguments += 4 * int(represented_mass != exact_mass)
    check(rounded_arguments == candidate['rounded_shifted_mass_components'] == 20, 'all twenty complex mass arguments rounded')

    controls = candidate['rejection_controls']
    check(len(controls) == 4, 'four rejection controls')
    for index, row in enumerate(controls):
        check(row['lane'] == index + 5, f'control {index}: lane')
        check(row['values_hidden'] is True, f'control {index}: value hidden')
        if index == 0:
            check(row['status'] == 'UncertifiedComponent(0)', 'wide input uncertainty rejected by budget')
        else:
            check(row['status'].startswith('InvalidInput('), f'control {index}: invalid enclosure rejected')
        expected_argument = 0 if index == 3 else 6
        check(row['affected_argument'] == expected_argument, f'control {index}: affected argument')
        represented = point(row['represented_input'])
        bounds = rectangle(row['input_rectangle'])
        width = Fraction(1, 2**80)
        original_mass_bounds = rectangle(candidate['contour_outputs'][0]['mass_enclosure'])
        original_mass_value = point(candidate['contour_outputs'][0]['represented_mass'])
        if index < 3:
            check(represented == original_mass_value, f'control {index}: unchanged nominal mass')
        if index == 0:
            rl, ru, il, iu = original_mass_bounds
            check(bounds == (rl-width, ru+width, il, iu), 'budget control: exact enlarged uncertainty')
            check(contains(bounds, represented) and contains(bounds, exact_mass), 'budget control: intended and nominal input retained')
        elif index == 1:
            rl, ru, il, iu = original_mass_bounds
            check(bounds == (rl, ru, il, Fraction(1)), 'branch control: exact upper-half-plane crossing')
            check(bounds[3] > 0 and contains(bounds, represented), 'branch control: unsafe interval with valid nominal point')
        elif index == 2:
            rl, ru, il, iu = original_mass_bounds
            excluded = represented[0] + width
            check(bounds == (excluded, excluded, il, iu), 'containment control: exact excluded nominal input')
            check(not contains(bounds, represented), 'containment control: nominal point outside interval')
        else:
            original = point(oracle['boxes'][0]['inputs'][0])
            check(represented == original, 'invariant control: unchanged exact nominal invariant')
            check(bounds == (original[0], original[0], -width, width), 'invariant control: exact imaginary uncertainty')
            check(represented[1] == 0 and bounds[2] < 0 < bounds[3], 'invariant control: real point with nonreal interval')
    jet = candidate['exact_vacuum_jet_uncertainty_control']
    check(jet['shape'] == [[0], [1], [2], [3]], 'jet shape through degree three')
    check(jet['input_rows'] == 2, 'two jet control lanes')
    check(jet['exact_point_status'] == 'Success', 'exact vacuum jet lane succeeds')
    check(jet['uncertain_status'].startswith('UncertifiedComponent('), 'uncertain jet lane rejected')
    check(jet['uncertain_values_hidden'] is True and jet['rho_exactly_zero'] is True, 'uncertain jets hidden at zero primal rho')
    check(q(jet['uncertain_rho']) == 0, 'actual serialized uncertain primal rho is zero')
    check(q(jet['independent_common_mass_third_coefficient']) == Fraction(-2, 3), 'independent degree-three coefficient')
    check(q(jet['uncertain_third_component_truncation']) >= Fraction(2, 3), 'zero-primal degree-three uncertainty tail covers 2/3')
    for name in ['reversed_independent_workspace_identical', 'empty_batch_passed', 'incorrect_rectangle_length_rejected']:
        check(candidate[name] is True, name)
    for label, execution, expected_rows, expected_active in [
        ('primary series', candidate['series_execution'], 9, 6),
        ('jet series', jet['execution'], 2, 2),
    ]:
        check(execution['input_rows'] == expected_rows, label + ': row count')
        check(execution['active_rows'] == expected_active, label + ': active row count')
        for field in ['numeric_batch_calls', 'enclosure_batch_calls', 'tail_batch_calls']:
            check(execution[field] == 1, label + ': ' + field)
    contour_execution = candidate['contour_execution']
    check(contour_execution == {'rows': 5, 'numeric_batch_calls': 1, 'enclosure_batch_calls': 1, 'output_components_per_row': 8}, 'contour batch counters')

    result = {'schema_version': 1, 'status': 'passed' if all(row['passed'] for row in checks) else 'failed',
              'checks': len(checks), 'failures': [row for row in checks if not row['passed']],
              'details': checks,
              'input_hashes': {str(candidate_path.relative_to(ROOT)): sha(candidate_path),
                               str(oracle_path.relative_to(ROOT)): sha(oracle_path),
                               str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__))},
              'scope': 'Exact rational recomputation of recorded numerical distance bounds and input/control checks. No symbolic algebra or candidate evaluation.',
              'limits': 'All forty contour outputs and four faulty input rectangles are audited from exact recorded numbers. Hidden-value, lane-reversal and execution-counter claims remain source/runtime assertions rather than independently recoverable full execution traces.'}
    assert not args.output.exists(), 'Never overwrite an audit result'
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'failures': len(result['failures']),
                      'output': str(args.output), 'sha256': sha(args.output)}))
    raise SystemExit(0 if result['status'] == 'passed' else 1)


if __name__ == '__main__':
    main()

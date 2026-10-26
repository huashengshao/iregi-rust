#!/usr/bin/env python3
"""Join a frozen COLLIER double campaign and its saved-data independent review.

No numerical integrals are evaluated. Every option remains represented. Native
warning flags are preserved without labelling accurate finite timings rejected.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path.cwd().resolve()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path):
    resolved = path.resolve()
    return {'source': str(resolved.relative_to(ROOT)), 'sha256': digest(resolved)}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qualification', type=Path)
    args = parser.parse_args()
    capture = json.loads((args.capture/'results.json').read_text())
    review = json.loads(args.review.read_text())
    assert review['status'] == 'passed' and not review['errors']
    assert review['capture'] == binding(args.capture/'results.json')
    assert len(capture['rows']) == 12 and review['candidate_count'] == 32
    audits = {row['id']: row for row in review['rows']}
    rows = []
    for raw in capture['rows']:
        row_id = raw['id']
        audit = audits[row_id]
        assert raw['selected_candidate'] == audit['selected_candidate']
        selected = next(candidate for candidate in raw['candidates']
                        if candidate['configuration']['id'] == raw['selected_candidate'])
        option = selected['configuration']
        assert selected['within_three_digits'] is audit['expected_within_three_digits']
        observed = []
        for candidate in raw['candidates']:
            candidate_id = candidate['configuration']['id']
            directory = args.capture/row_id/candidate_id
            timed_path = directory/'timed.response.json'
            timed = json.loads(timed_path.read_text()) if timed_path.exists() else None
            diagnostics = timed['lanes'][0] if timed else {}
            observed.append({'id': candidate_id, 'configuration': candidate['configuration'],
                             'status': candidate['status'], 'selected': candidate_id == raw['selected_candidate'],
                             'timing_us': candidate.get('timing_us'),
                             'array_relative_error': candidate.get('maximum_array_relative_error_over_finite_fields'),
                             'maximum_coefficient_mixed_normalized_error': candidate.get('maximum_coefficient_mixed_normalized_error_over_finite_fields'),
                             'nonfinite_complex_fields': candidate.get('nonfinite_complex_fields'),
                             'within_three_digits': candidate.get('within_three_digits', False),
                             'native_returncode': candidate.get('native_returncode'),
                             'last_err_flag': diagnostics.get('last_err_flag'),
                             'last_acc_flag': diagnostics.get('last_acc_flag'),
                             'worst_err_flag': diagnostics.get('worst_err_flag'),
                             'worst_acc_flag': diagnostics.get('worst_acc_flag'),
                             'maximum_rank_error_estimates': diagnostics.get('maximum_rank_error_estimates'),
                             'timed_response': binding(timed_path) if timed else None,
                             'captures': [{key: value for key, value in record.items() if key != 'assessment'}
                                          for record in candidate.get('captures', {}).values()]})
        selected_observation = next(item for item in observed if item['selected'])
        warning = None
        if not selected['within_three_digits']:
            nonfinite = selected.get('nonfinite_complex_fields', 0)
            warning = f'{nonfinite} nonfinite fields' if nonfinite else 'measured relative error exceeds 1e-3'
        rows.append({'id': row_id, 'n': raw['n'], 'rank': raw['rank'],
                     'numeric_type': 'binary64', 'working_bits': 53, 'batch_size': 1,
                     'status': raw['status'], 'timing_qualified': selected['within_three_digits'],
                     'timing_role': 'optimistic observed absolute warm reduction time; accuracy shown separately',
                     'accuracy_warning': warning, 'failure_label': warning,
                     'timing_us': selected['timing_us'], 'array_relative_error': raw['array_relative_error'],
                     'maximum_coefficient_mixed_normalized_error': selected['maximum_coefficient_mixed_normalized_error_over_finite_fields'],
                     'nonfinite_complex_fields': raw['nonfinite_complex_fields'],
                     'distinct_complex_fields': 4*math.comb(raw['rank']+4, 4),
                     'requested_accuracy': option['requested_accuracy'], 'critical_accuracy': option['critical_accuracy'],
                     'selected_candidate': option['id'], 'mode': 'COLI' if option['mode'] == 1 else 'DD',
                     'mode_number': option['mode'], 'direct_tensor_threshold': option['direct_tensor_threshold'],
                     'argument_permutation': bool(option['argument_permutation']),
                     'native_diagnostics': {key: selected_observation[key] for key in ('last_err_flag', 'last_acc_flag',
                        'worst_err_flag', 'worst_acc_flag', 'maximum_rank_error_estimates')},
                     'repeats': 11, 'iterations_per_block': selected['iterations_per_block'],
                     'within_three_digits': selected['within_three_digits'],
                     'within_requested_accuracy': (selected['finite'] and raw['array_relative_error'] is not None
                                                   and raw['array_relative_error'] <= float(option['requested_accuracy'])),
                     'timed_response': selected_observation['timed_response'], 'all_candidate_attempts': observed,
                     'reference_array': raw['reference_array']})
    summary = {'schema_version': 1, 'measurement_date': capture['completed_utc'][:10],
               'purpose': 'Binary64 optimistic COLLIER column for the opening ordinary examples',
               'numeric_type': 'binary64', 'working_bits': 53, 'cpu': capture['cpu'],
               'input_family': 'Unchanged exact massive E-prefix input geometry; cumulative Cartesian moments and all native Laurent slots',
               'capture': binding(args.capture/'results.json'), 'independent_review': binding(args.review),
               'rows': rows, 'measured_rows': len(rows),
               'rows_with_at_least_three_digits': sum(row['within_three_digits'] for row in rows),
               'rows_with_accuracy_warning': sum(not row['within_three_digits'] for row in rows),
               'predeclared_candidates': sum(len(row['all_candidate_attempts']) for row in rows),
               'candidates_with_completed_timings': sum(item['timing_us'] is not None for row in rows for item in row['all_candidate_attempts']),
               'candidates_with_terminal_failure': sum(item['status'] in ('failed', 'timeout') for row in rows for item in row['all_candidate_attempts']),
               'selection': capture['selection'], 'accuracy': capture['accuracy'], 'timer_scope': capture['timer_scope'],
               'ratio_campaign': False,
               'protocol': 'All 32 predeclared public-option candidates attempted. One warm pilot chooses a fixed count targeting30ms, cap1e6; three warmups and11 timed blocks. Fastest mean within three digits selected; otherwise fastest diagnostic time remains visible. Means and descriptive SEM are observations, not a controlled-host confidence gate.',
               'classification': 'Timing-first. Native warnings alone do not mark a row rejected. Explicit accuracy warning only when achieved whole-array relative error>1e-3 or a requested complex field is nonfinite.',
               'no_precision_promotion': True}
    save(args.output, summary)
    if args.qualification:
        qualification = {'schema_version': 1, 'status': 'saved_data_audit_passed',
                         'capture': summary['capture'], 'independent_review': summary['independent_review'],
                         'summary': binding(args.output), 'measured_rows': len(rows),
                         'predeclared_candidates': summary['predeclared_candidates'],
                         'rows_with_at_least_three_digits': summary['rows_with_at_least_three_digits'],
                         'rows_with_accuracy_warning': summary['rows_with_accuracy_warning'],
                         'selected_options': [{'id': row['id'], 'configuration': row['selected_candidate'],
                            'array_relative_error': row['array_relative_error'], 'within_three_digits': row['within_three_digits'],
                            'nonfinite_complex_fields': row['nonfinite_complex_fields']} for row in rows],
                         'classification': summary['classification'], 'no_performance_parity_claim': True}
        save(args.qualification, qualification)
    print(json.dumps({'output': str(args.output), 'measured_rows': len(rows),
                      'within_three_digits': summary['rows_with_at_least_three_digits'],
                      'accuracy_warnings': summary['rows_with_accuracy_warning']}))


if __name__ == '__main__':
    main()

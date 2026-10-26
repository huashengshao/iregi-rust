#!/usr/bin/env python3
"""Assemble the opening-table view from independently retained tool summaries."""
import hashlib
import json
from pathlib import Path

HERE = Path('validation/benchmark/opening-double-20261026')


def load(path):
    return json.loads(path.read_text())


def binding(path):
    return {'source': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source = HERE / 'tirust-summary.json'
    reference = HERE / 'collier/summary.json'
    result = load(source)
    collier = load(reference)
    supplement_path = HERE / 'supplemental/supplemental-summary.json'
    supplement_review_path = HERE / 'supplemental/independent-review.json'
    supplement = load(supplement_path)
    supplement_review = load(supplement_review_path)
    assert str(supplement_review['status']).startswith('passed')
    initial_review = load(HERE / 'independent-review.json')
    assert initial_review['passed'] and initial_review['terminal_attempts'] == 38
    rows = {row['id']: row for row in collier['rows']}
    assert len(rows) == 12 and len(result['rows']) == 18
    for row in result['rows']:
        assert row['numeric_type'] == 'f64' and row['working_bits'] == 53
        added = [dict(attempt, id=attempt['candidate_id']) for attempt in supplement['attempts']
                 if attempt['case_id'] == row['id']]
        if added:
            row['attempts'].extend(added)
            timed = [a for a in row['attempts'] if a.get('timing_captured')]
            eligible = [a for a in timed if a.get('eligible_optimistic_result')]
            finite = [a for a in timed if a.get('successful_finite_full_array')
                      and a.get('accuracy', {}).get('measured')]
            chosen = min(eligible or finite or timed,
                         key=lambda a: a['timing']['outer_total_us']['mean'])
            for key in ('timing', 'accuracy', 'engine', 'plan_engine', 'plan_ns', 'workspace_ns',
                        'first_call_ns', 'repeats', 'calls_per_repeat', 'total_timed_calls',
                        'result_source', 'supervision_source', 'successful_finite_full_array', 'timing_captured'):
                row[key] = chosen[key]
            row.update(status=chosen['status'], selected_candidate=chosen['id'],
                       timing_qualified=bool(eligible), algorithm=chosen['request']['algorithm'],
                       master_policy=chosen['request']['master_policy'],
                       postconstruction_profiling=chosen['request']['postconstruction_profiling'],
                       denominator_permutation=chosen.get('permutation'),
                       selection_warning=None if eligible else 'All measured paths refused or failed the three-digit/full-array boundary; diagnostic timing only')
        row['requested_relative_accuracy'] = 2 ** (19 - row['requested_bits'])
        if row['table'] != 'ordinary':
            assert row['id'] not in rows
            continue
        saved = rows.pop(row['id'])
        assert saved['working_bits'] == 53 and saved['numeric_type'] == 'binary64'
        assert saved['n'] == row['n'] and saved['rank'] == row['rank']
        row['collier'] = dict(saved)
        row['collier']['accuracy'] = {
            'measured': saved['array_relative_error'] is not None,
            'relative_error': saved['array_relative_error'],
            'nonfinite_complex_fields': saved['nonfinite_complex_fields'],
        }
    assert not rows
    result.update(
        tirust_summary=binding(source), collier_summary=binding(reference),
        supplemental_summary=binding(supplement_path), supplemental_review=binding(supplement_review_path),
        initial_candidates=38, supplemental_candidates=4,
        measured_rows=sum(bool(r.get('timing_captured')) for r in result['rows']),
        three_digit_rows=sum(bool(r['timing_qualified']) for r in result['rows']),
        supplemental_selection_notice=supplement['selection_notice'],
        purpose='Optimistic binary64 opening tables; measured accuracy is annotated separately',
        no_precision_promotion=True,
        collier_strategy_precision_note='DD denotes the Denner-Dittmaier algorithm, not double-double precision; every COLLIER candidate is binary64',
    )
    (HERE / 'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    qualification = {
        'schema_version': 1, 'status': 'passed_joined_saved_data_selection_and_precision_review',
        'summary': binding(HERE / 'summary.json'), 'initial_review': binding(HERE / 'independent-review.json'),
        'supplemental_review': binding(supplement_review_path),
        'collier_review': binding(HERE / 'collier/independent-review.json'),
        'all_tirust_working_types': 'f64/53 significant bits',
        'initial_candidates': 38, 'post_hoc_public_permutation_PV_candidates': 4,
        'tirust_rows': len(result['rows']), 'tirust_three_digit_rows': result['three_digit_rows'],
        'collier_rows': 12, 'collier_three_digit_rows': collier['rows_with_at_least_three_digits'],
        'selection': 'Fastest observed mean over all independently audited available configurations, preferring complete finite tensors within three relative digits; preserve diagnostic durations if none',
        'post_hoc_reason': supplement['post_hoc_reason'], 'new_comparative_speed_gate': False,
        'selected_rows': [{'id': r['id'], 'candidate': r['selected_candidate'],
                           'eligible': r['timing_qualified'], 'accuracy': r['accuracy'],
                           'result_source': r['result_source']} for r in result['rows']],
    }
    (HERE / 'joined-qualification.json').write_text(json.dumps(qualification, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'assembled_rows': len(result['rows']), 'collier_rows': 12}))


if __name__ == '__main__':
    main()

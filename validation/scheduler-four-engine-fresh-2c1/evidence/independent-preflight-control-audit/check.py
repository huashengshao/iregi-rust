#!/usr/bin/env python3
"""Supplemental independent saved-only audit; no producer imports or numerical execution."""
import collections
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('/shared/external/iregi/iregi-rust')
BASE = ROOT / 'target/guard-performance-review/optimized-performance-proposal'
HERE = Path(__file__).resolve().parent
OLD = BASE / 'independent-captured-control-audit'
RUN = BASE / 'fresh-four-engine-proposal/preflight-fresh2c1-001'
PROTOCOL = BASE / 'fresh-four-engine-proposal/preflight-fresh2c1-001-protocol.json'
RECEIPT = RUN / 'receipt.json'
RAW = RUN / 'raw.jsonl'
PRIOR_RAW = BASE / 'fresh-captured-runtime/qualification-001/responses.jsonl'
EXPECTED = {
    RECEIPT: '10a8ca2bd11c881c353fb5cfda2944333c0f4adcf1cc2c09b4ac01700ac9be39',
    RAW: '5cfbf85862b86367fe54295c0668db95c15bd9758c402362ba5ba7d5d07229d3',
    PROTOCOL: '5eaeb1bf6a5085226333f65c9836c6cf897488d31efa108f9507c257ee070886',
    OLD / 'check.py': 'd9244a7d6dfe0454e3540ba33197cb237696334a75ca19abfb583ba81e57a9a9',
    OLD / 'review.json': 'cd1f2eca7310e1fd117f0d7c93c9b791974e7fe7e614c387a17fe95e42329533',
    PRIOR_RAW: '750310b9290ae9e9aa6f396dfae5837187dbf9f451bdc1fce950f5d2a288b21e',
}

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while data := f.read(1024 * 1024): h.update(data)
    return h.hexdigest()

for path, digest in EXPECTED.items():
    if sha(path) != digest: raise AssertionError('Frozen input hash differs: ' + str(path))

# Reuse only our independently authored, hash-pinned numeric/fixture primitives.
# Loading this source does not call its main or write its sealed report.
spec = importlib.util.spec_from_file_location('independent_control_primitives', OLD / 'check.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
same = audit.same
require = audit.require

receipt = audit.load(RECEIPT); protocol = audit.load(PROTOCOL)
same(receipt['status'], 'completed-preflight', 'completed saved preflight receipt')
same(receipt['mode'], 'preflight', 'preflight mode')
same(receipt['pinned_source_revision'], audit.PIN, 'receipt pinned source context')
same(protocol['pinned_source_revision'], audit.PIN, 'protocol pinned source context')
same(receipt['raw_sha256'], EXPECTED[RAW], 'receipt raw binding')
same(receipt['protocol_sha256'], EXPECTED[PROTOCOL], 'receipt protocol binding')
same(receipt['guard_before'], True, 'producer preguard completed')
same(receipt['guard_after'], True, 'producer postguard completed')
same(receipt['global_lifecycle_clean'], True, 'producer terminal cleanup receipt')
same(receipt['cleanup_errors'], [], 'producer clean terminal receipt')
same(len(receipt['process_terminals']), 6, 'six terminal records')
for terminal in receipt['process_terminals']:
    same(terminal['returncode'], 0, 'successful terminal returncode')
    same(terminal['owned_group_gone'], True, 'terminal owned group absent per receipt')

guards = {Path(k): v for k, v in receipt['input_sha256'].items()}
guards.update(EXPECTED); guards[Path(__file__).resolve()] = sha(__file__)
before = {str(k): sha(k) for k in guards}
for path, expected in guards.items(): same(before[str(path)], expected, 'protected input before ' + str(path))

events = [json.loads(line) for line in RAW.read_text().splitlines()]
same(len(events), 336, 'saved preflight raw event count')
requests = {e['serial']: e for e in events if e['event'] == 'request'}
responses = {e['serial']: e for e in events if e['event'] == 'response'}
same(set(requests), set(range(1, 169)), '168 complete preflight requests')
same(set(responses), set(requests), '168 complete paired preflight responses')
prior = [json.loads(line) for line in PRIOR_RAW.read_text().splitlines()]
canonical = next(e['response'] for e in prior if e['event'] == 'response' and e['serial'] == 33)
same(audit.load(OLD / 'review.json')['status'], 'passed', 'independently audited prior exact CONTROL body')

def control_results(control):
    return ([e['result'] for e in control['core']] +
            [e['result'] for e in control['extended_core']] +
            control['cache_interleaving']['expected_current_process_records'] +
            [e['result'] for e in control['cache_interleaving']['steps']])

uncaptured_canonical = copy.deepcopy(canonical)
same(len(control_results(uncaptured_canonical)), 15, 'exact capture-bearing record path inventory')
for record in control_results(uncaptured_canonical):
    same(len(record['master_captures']), 2, 'captured reference contains B0+A0 families')
    record['master_captures'] = []

fixtures = audit.fixture_specs()
specmap = {(s['group'], s['family'], s['label'], s['case']): s for s in fixtures}
roles = ['baseline-captured', 'candidate-captured', 'baselineTIRust', 'candidateTIRust']
inventory = []; first = {}
for serial in [65, 66, 67, 68, 165, 166, 167, 168]:
    req = requests[serial]; response = responses[serial]
    role = roles[(serial - 65) % 100]
    for key in ['serial', 'stage', 'kind', 'engine', 'payload']:
        same(response[key], req[key], 'CONTROL paired envelope ' + key)
    same(req['payload'], 'CONTROLS\n', 'literal CONTROL payload')
    same(req['engine'], role, 'four-role sequence')
    same(req['kind'], 'controls', 'control event kind')
    same(req['stage'], 'controls-before' if serial < 100 else 'controls-after', 'CONTROL stage')
    control = response['response']; captured = role.endswith('-captured')
    same(control, canonical if captured else uncaptured_canonical,
         'complete control equality except exact fifteen capture-array projections')
    if serial < 100: first[role] = control
    else: same(control, first[role], 'own full before/after control record exact')
    found = set(); rows = successes = errors = complex_count = 0
    for group in ['selected_families', 'unchanged_paths', 'extended_unchanged_paths']:
        for family in control['masters'][group]:
            for case in family['cases']:
                label = None if group == 'selected_families' else family['label']
                key = (group, family['family'], label, case['label'])
                require(key not in found, 'unique actual direct case'); found.add(key)
                fs = specmap[key]
                same(case['input_metadata'], fs['inputs'], 'independently reconstructed actual direct input')
                audit.complexes(case['input_metadata'], True)
                same(case['baseline'], case['candidate'], 'within-role direct complete equality')
                count = audit.snapshot(case['baseline'], fs)
                audit.snapshot(case['candidate'], fs)
                if 'represented_outputs' in case: same(case['represented_outputs'], case['baseline'], 'retained represented values')
                for field in ['input_unchanged', 'own_repeated_outputs_exact']: same(case[field], True, field)
                rows += len(fs['errors']); errors += sum(e is not None for e in fs['errors'])
                successes += sum(e is None for e in fs['errors']); complex_count += count
    same(found, set(specmap), 'all67independent actual direct fixture shapes')
    same((len(found), rows, successes, errors, complex_count), (67, 133, 106, 27, 774), 'complete direct inventory each role/control stage')
    for record in control_results(control):
        same(len(record['master_captures']), 2 if captured else 0, 'capture mode explicit at exact record path')
    inventory.append({'serial': serial, 'role': role, 'captured': captured, 'stage': req['stage'],
                      'direct_cases': len(found), 'direct_rows': rows, 'direct_success_rows': successes,
                      'direct_expected_null_error_rows': errors, 'direct_sixslot_complex_values': complex_count,
                      'core_tensor_complex_values': 80, 'core_captured_master_complex_values': 72 if captured else 0,
                      'cache_reference_contexts': 4, 'cache_interleaving_steps': 8,
                      'complete_exact_control_body_qualified': True})

after = {str(k): sha(k) for k in guards}
same(after, before, 'all protected input hashes unchanged after audit')
report = {
    'status': 'passed',
    'scope': 'Independent saved CONTROL-only audit of actual completed six-process preflight. Checks eight controls across four TIRust roles, before/after, with exact capture-only projection. Other raw responses are paired/count-bound but not numerically audited here.',
    'pinned_source_revision': audit.PIN,
    'source_context_role': 'Pinned isolated2c1f334 optimized captured and capture-free builds, not concurrently modified production tree.',
    'checker_sha256': sha(__file__), 'independent_primitives_sha256': EXPECTED[OLD / 'check.py'],
    'prior_independent_review_sha256': EXPECTED[OLD / 'review.json'],
    'receipt_sha256': EXPECTED[RECEIPT], 'protocol_sha256': EXPECTED[PROTOCOL], 'raw_sha256': EXPECTED[RAW],
    'saved_raw_events': 336, 'saved_raw_request_response_pairs': 168,
    'control_responses': 8, 'control_inventory': inventory,
    'per_control_inventory': {'direct_cases': 67, 'direct_rows': 133, 'direct_success_rows': 106, 'direct_expected_null_error_rows': 27, 'direct_all_sixslot_complex_values': 774,
                              'core_tensor_complex_values': 80, 'core_master_complex_values_captured_only': 72, 'cache_reference_contexts': 4, 'cache_interleaving_steps': 8},
    'all_controls_equal_same_canonical_after_exact_capture_projection': True,
    'exact_projection_scope': 'Only master_captures arrays at15frozen core/extended/cache reference/cache step result paths become empty; all other keys and values remain exact.',
    'static_higher_or_mixed_Dual_in_this_runtime': False,
    'dynamic_Dual_shapes_observed': [[[0]], [[0], [1]]],
    'Float_DoubleFloat_and_beyond53_exact_inputs_qualified': True,
    'producer_validator_imported_or_called': False,
    'compiler_numerical_library_executable_integral_or_bootstrap_launched': False,
    'timing_or_performance_claim': False,
    'independent_original_IREGI_comparison_claim': False,
    'production_adoption_qualified': False,
    'guard_count': len(guards), 'input_sha256_before': before, 'input_sha256_after': after,
    'assertions_passed': audit.checks,
}
(HERE / 'review.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps({key: report[key] for key in ['status', 'assertions_passed', 'guard_count', 'control_responses', 'saved_raw_events']}))
